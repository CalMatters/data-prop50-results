import marimo

__generated_with = "0.18.1"
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
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(Path, RESULTS_CSV_FP, pd):
    if Path(RESULTS_CSV_FP).exists():
        results_df = pd.read_csv(RESULTS_CSV_FP, dtype={"precinct_id": str})
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


@app.cell
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    MERGE_COLUMNS = ["county", "precinct_id"]
    return (MERGE_COLUMNS,)


@app.cell
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


@app.cell
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _(DEBUG_DIR, datetime):
    def check_and_export_duplicates(
        df, df_name, merge_columns, debug_dir=DEBUG_DIR
    ):
        """Check for duplicates in a DataFrame and export them if found."""
        dup = df.duplicated(subset=merge_columns, keep=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if dup.any():
            duplicates_df = df[dup].sort_values(by=merge_columns)
            filename = f"{debug_dir}/duplicates_{df_name}_{timestamp}.csv"
            duplicates_df.to_csv(filename, index=False)
            print(
                f"Found {dup.sum()} duplicate(s) in {df_name} on {merge_columns}. Exported to {filename}"
            )
        return dup.any()
    return (check_and_export_duplicates,)


if __name__ == "__main__":
    app.run()
