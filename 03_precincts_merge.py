import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    from datetime import datetime
    import os
    from pathlib import Path

    import marimo as mo
    import geopandas as gpd
    import pandas as pd
    return Path, datetime, gpd, mo, os, pd


@app.cell
def _(
    MERGE_COLUMNS,
    check_and_export_duplicates,
    pd,
    precincts_gdf,
    results_df,
):
    precincts_county_set = set(precincts_gdf["county"])
    results_county_set = set(results_df["county"])

    county_intersect = precincts_county_set & results_county_set
    print(
        f"Counties present in both precincts and results data: {sorted(county_intersect)}"
    )

    precincts_filtered_gdf = precincts_gdf[
        precincts_gdf["county"].isin(county_intersect)
    ]
    try:
        precincts_results_merge = precincts_filtered_gdf.merge(
            results_df, on=MERGE_COLUMNS, how="outer", validate="1:1"
        )
    except pd.errors.MergeError as e:
        print("One-to-one merge failed. Checking for duplicate keys...")

        # Check for duplicates in both DataFrames
        has_precincts_dups = check_and_export_duplicates(
            precincts_filtered_gdf,
            "precincts",
            MERGE_COLUMNS,
        )
        has_results_dups = check_and_export_duplicates(
            results_df,
            "results",
            MERGE_COLUMNS,
        )

        # Proceed with merge without validation for now, to allow inspection
        precincts_results_merge = precincts_filtered_gdf.merge(
            results_df, on=MERGE_COLUMNS, how="outer", validate=None
        )
        print(
            "Merge completed with duplicates present. Inspect the result to resolve key conflicts."
        )

    precincts_results_merge
    return (precincts_results_merge,)


@app.cell
def _(
    DEBUG_DIR,
    export_if_not_empty,
    get_current_timestamp,
    pd,
    precincts_results_merge,
):
    def audit_merged_precinct_data(merged_gdf, debug_dir=DEBUG_DIR):
        """
        Audit an outer-merged precincts-results GeoDataFrame.
        Identifies missing entries by county and exports mismatches for inspection.
        """

        # Reusable function to count entries by county given a condition
        def count_by_county(condition):
            return merged_gdf.loc[condition, "county"].value_counts()

        timestamp = get_current_timestamp()

        # Identify missing entries (from either left or right)
        is_left_missing = merged_gdf["geometry"].isna()
        is_right_missing = merged_gdf["total_votes"].isna()

        left_only = merged_gdf[is_left_missing]  # in results, not in precincts GIS
        right_only = merged_gdf[is_right_missing]  # in GIS, not in results

        # Get counts for all relevant categories
        gis_missing_counts = count_by_county(
            is_left_missing
        )  # number of result records without a geography match in each county
        results_missing_counts = count_by_county(
            is_right_missing
        )  # number of precinct geographies without corresponding results in each county
        gis_valid_counts = count_by_county(merged_gdf["geometry"].notna())
        results_valid_counts = count_by_county(merged_gdf["total_votes"].notna())

        # Build audit summary using all counties present
        all_counties = sorted(merged_gdf["county"].unique())
        audit_summary = {
            county: {
                "gis_entries": gis_valid_counts.get(county, 0),
                "results_entries": results_valid_counts.get(county, 0),
                "missing_in_gis": gis_missing_counts.get(county, 0),
                "missing_in_results": results_missing_counts.get(county, 0),
            }
            for county in all_counties
        }

        # Convert to DataFrame
        audit_df = pd.DataFrame.from_dict(audit_summary, orient="index")

        # Export for inspection
        export_if_not_empty(left_only, "missing_in_gis")
        export_if_not_empty(right_only, "missing_in_results")
        audit_filepath = f"{debug_dir}/audit_summary_{timestamp}.csv"
        audit_df.to_csv(audit_filepath, index=True)

        print(
            f"Audit complete. {len(left_only)} entries missing in GIS, {len(right_only)} missing in results. See exported audit debug data in `debug/` directory."
        )
        return audit_df


    # Run audit
    audit_results = audit_merged_precinct_data(precincts_results_merge, DEBUG_DIR)
    audit_results
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Explore
    """)
    return


@app.cell
def _(mo, results_df):
    county_dropdown = mo.ui.dropdown(list(results_df["county"].unique()))
    county_dropdown
    return (county_dropdown,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Merged data
    """)
    return


@app.cell
def _(county_dropdown, precincts_results_merge):
    precincts_results_merge[
        (precincts_results_merge["county"] == county_dropdown.value)
    ]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Results without a geographic match
    """)
    return


@app.cell
def _(county_dropdown, precincts_results_merge):
    precincts_results_merge[
        (precincts_results_merge["county"] == county_dropdown.value)
        & (precincts_results_merge["geometry"].isnull())
    ]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Geographic data without a results match
    """)
    return


@app.cell
def _(county_dropdown, precincts_results_merge):
    precincts_results_merge[
        (precincts_results_merge["county"] == county_dropdown.value)
        & (precincts_results_merge["yes_votes"].isnull())
    ]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(Path, RESULTS_CSV_FP, pd):
    if Path(RESULTS_CSV_FP).exists():
        results_df = pd.read_csv(RESULTS_CSV_FP, dtype={"precinct_id": str})
        results_df[["yes_votes", "no_votes", "total_votes"]] = results_df[
            ["yes_votes", "no_votes", "total_votes"]
        ].fillna(-1)
        result_county_count = results_df["county"].nunique()
        print(
            f"Read in {RESULTS_CSV_FP}. Precincts for {result_county_count} counties present"
        )
    else:
        raise FileNotFoundError(
            f"The file {RESULTS_CSV_FP} does not exist. Please run 'uv run 02_results.py' to create it."
        )
    return (results_df,)


@app.cell
def _(PRECINCTS_GIS_FP, Path, gpd):
    if Path(PRECINCTS_GIS_FP).exists():
        precincts_gdf = gpd.read_file(PRECINCTS_GIS_FP)
        precinct_county_count = precincts_gdf["county"].nunique()
        print(
            f"Read in {PRECINCTS_GIS_FP}. Precincts for {precinct_county_count} counties present"
        )
    else:
        raise FileNotFoundError(
            f"The file {PRECINCTS_GIS_FP} does not exist. Please run 'just generate-precincts-file' to create it."
        )
    return (precincts_gdf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    MERGE_COLUMNS = ["county", "precinct_id"]
    return (MERGE_COLUMNS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## File paths
    """)
    return


@app.cell
def _():
    PRECINCTS_GIS_FP = "./outputs/precincts.gpkg"
    return (PRECINCTS_GIS_FP,)


@app.cell
def _():
    RESULTS_CSV_FP = "./outputs/results.csv"
    return (RESULTS_CSV_FP,)


@app.cell
def _(os):
    DEBUG_DIR = "./debug"
    os.makedirs(DEBUG_DIR, exist_ok=True)
    return (DEBUG_DIR,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _(DEBUG_DIR, get_current_timestamp):
    def check_and_export_duplicates(
        df, df_name, merge_columns, debug_dir=DEBUG_DIR
    ):
        """Check for duplicates in a DataFrame and export them if found."""
        dup = df.duplicated(subset=merge_columns, keep=False)
        timestamp = get_current_timestamp()
        if dup.any():
            duplicates_df = df[dup].sort_values(by=merge_columns)
            filename = f"{debug_dir}/duplicates_{df_name}_{timestamp}.csv"
            duplicates_df.to_csv(filename, index=False)
            print(
                f"Found {dup.sum()} duplicate(s) in {df_name} on {merge_columns}. Exported to {filename}"
            )
        return dup.any()
    return (check_and_export_duplicates,)


@app.cell
def _(datetime):
    def get_current_timestamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    return (get_current_timestamp,)


@app.cell
def _(DEBUG_DIR, get_current_timestamp):
    # Helper to export DataFrame if not empty
    def export_if_not_empty(df, filename_suffix, debug_dir=DEBUG_DIR):
        timestamp = get_current_timestamp()
        filepath = f"{debug_dir}/{filename_suffix}_{timestamp}.csv"
        if len(df) > 0:
            df.to_csv(filepath, index=False)
            return filepath
        return None
    return (export_if_not_empty,)


if __name__ == "__main__":
    app.run()
