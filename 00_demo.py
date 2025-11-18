import marimo

__generated_with = "0.17.8"
app = marimo.App(width="columns")


@app.cell
def _():
    import zipfile

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import tobler
    return gpd, mo, pd, tobler, zipfile


@app.cell
def _():
    HEADER_ROWS_N = 6
    return


@app.cell
def _():
    BG_GIS_FILE = "./inputs/census/tl_2020_06_bg.zip"
    return (BG_GIS_FILE,)


@app.cell
def _():
    PRECINCT_GIS_FP = "./inputs/shasta/Consolidated_Precincts.zip"
    PRECINCT_RESULTS_FP = "./inputs/shasta/detail.xlsx"
    PROP_50_RESULTS_SHEET = 2

    CENSUS_CVAP_ZIPPED_DATA = "./inputs/census/CVAP_2019-2023_ACS_csv_files.zip"
    return (
        CENSUS_CVAP_ZIPPED_DATA,
        PRECINCT_GIS_FP,
        PRECINCT_RESULTS_FP,
        PROP_50_RESULTS_SHEET,
    )


@app.cell
def _():
    RESULT_COL_RENAMES = [
        "precinct",
        "registered_voters",
        "vote_by_mail_yes",
        "election_day_yes",
        "total_votes_yes",
        "vote_by_mail_no",
        "election_day_no",
        "total_votes_no",
        "total_no_votes",
    ]
    return (RESULT_COL_RENAMES,)


@app.cell
def _():
    FIPS_LEN = 12
    SHASTA_FIPS = "06089"
    return FIPS_LEN, SHASTA_FIPS


@app.cell
def _(pd, zipfile):
    def list_files_in_zip(zip_path: str) -> list:
        """Returns a list of file names inside the given zipfile."""
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            return zip_ref.namelist()


    def read_csv_from_zip(
        zip_path: str, csv_filename: str, **read_csv_kwargs
    ) -> pd.DataFrame:
        """Reads a CSV file from a zipfile and returns it as a pandas DataFrame.

        Additional keyword arguments are passed to pd.read_csv.
        """
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            with zip_ref.open(csv_filename) as file:
                return pd.read_csv(file, **read_csv_kwargs)
    return list_files_in_zip, read_csv_from_zip


@app.cell
def _(PRECINCT_GIS_FP, PRECINCT_RESULTS_FP, PROP_50_RESULTS_SHEET, gpd, pd):
    DF_RESULTS = pd.read_excel(
        PRECINCT_RESULTS_FP,
        sheet_name=PROP_50_RESULTS_SHEET,
        skiprows=1,
        header=[0, 1],
    )
    GDF_PRECINCTS = gpd.read_file(PRECINCT_GIS_FP)
    return DF_RESULTS, GDF_PRECINCTS


@app.cell
def _(DF_RESULTS, RESULT_COL_RENAMES):
    df_results = DF_RESULTS.copy()
    df_results.columns = RESULT_COL_RENAMES
    df_results = df_results[~df_results["precinct"].str.contains("Total")].copy()
    return (df_results,)


@app.cell
def _(GDF_PRECINCTS, df_results):
    gdf_precinct_results = GDF_PRECINCTS.merge(
        df_results, left_on="CONS_PCTNU", right_on="precinct", validate="1:1"
    )
    return (gdf_precinct_results,)


@app.cell
def _(
    CENSUS_CVAP_ZIPPED_DATA,
    FIPS_LEN,
    SHASTA_FIPS,
    list_files_in_zip,
    read_csv_from_zip,
):
    bg_filename = list_files_in_zip(CENSUS_CVAP_ZIPPED_DATA)[0]
    DF_CVAP_BG = read_csv_from_zip(
        CENSUS_CVAP_ZIPPED_DATA, bg_filename, encoding="latin1"
    )
    DF_CVAP_BG.loc[:, "geoid"] = DF_CVAP_BG["geoid"].str.slice(-1 * FIPS_LEN)
    df_shasta_cvap_bg = DF_CVAP_BG[
        DF_CVAP_BG["geoid"].str.startswith(SHASTA_FIPS)
    ].copy()
    del DF_CVAP_BG
    df_shasta_cvap_bg
    return (df_shasta_cvap_bg,)


@app.cell
def _(df_shasta_cvap_bg, pd):
    def pivot_cvap_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform CVAP data from long to wide format, with each demographic group as a column.

        Parameters
        ----------
        df : pd.DataFrame
            Input CVAP dataframe with columns including 'geoid', 'lntitle', 'cvap_est', 'cvap_moe'

        Returns
        -------
        pd.DataFrame
            Transformed dataframe with demographic groups as separate columns for est and moe
        """
        # Create copy to avoid modifying original
        df_copy = df.copy()

        # Clean up lntitle values for use as column names
        df_copy["lntitle_clean"] = (
            df_copy["lntitle"].str.replace(r"[^\w\s]", "").str.strip()
        )
        df_copy["lntitle_clean"] = (
            df_copy["lntitle_clean"].str.replace(" ", "_").str.lower()
        )

        # Create column names for estimate and margin of error
        df_copy["est_col"] = df_copy["lntitle_clean"] + "_cvap_est"
        df_copy["moe_col"] = df_copy["lntitle_clean"] + "_cvap_moe"

        # Create dictionaries mapping geoid to value for each column
        est_dict = df_copy.set_index(["geoid", "est_col"])["cvap_est"].to_dict()
        moe_dict = df_copy.set_index(["geoid", "moe_col"])["cvap_moe"].to_dict()

        # Get unique geoids and initialize result dataframe
        geoids = df_copy["geoid"].unique()
        result = pd.DataFrame({"geoid": geoids})

        # Pivot both est and moe values
        est_pivot = df_copy.pivot(
            index="geoid", columns="est_col", values="cvap_est"
        )
        moe_pivot = df_copy.pivot(
            index="geoid", columns="moe_col", values="cvap_moe"
        )

        # Join est and moe columns to result
        result = result.join(est_pivot, on="geoid")
        result = result.join(moe_pivot, on="geoid")

        return result


    def transform_cvap_format(df: pd.DataFrame) -> pd.DataFrame:
        """
        Main function to transform CVAP data into clean, human-readable format.

        Parameters
        ----------
        df : pd.DataFrame
            Input CVAP dataframe in standard format

        Returns
        -------
        pd.DataFrame
            Cleanly formatted dataframe with demographic groups as columns
        """
        # Validate required columns
        required_cols = {"geoid", "lntitle", "cvap_est", "cvap_moe"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")

        # Transform the data
        result_df = pivot_cvap_data(df)

        return result_df


    # Apply transformation to the Shasta CVAP data
    df_shasta_cvap_bg_wide = transform_cvap_format(df_shasta_cvap_bg)
    df_shasta_cvap_bg_wide
    return (df_shasta_cvap_bg_wide,)


@app.cell
def _(df_shasta_cvap_bg_wide, pd):
    def filter_moe_from_wide_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a wide-format CVAP dataframe and returns a copy with only the estimate columns (removes MOE columns).

        Parameters
        ----------
        df : pd.DataFrame
            Input wide-format dataframe with both _cvap_est and _cvap_moe columns

        Returns
        -------
        pd.DataFrame
            DataFrame with only the estimate columns and 'geoid'
        """
        # Select columns that end with '_cvap_est' or are the geoid column
        est_columns = [
            col
            for col in df.columns
            if col.endswith("_cvap_est") or col == "geoid"
        ]
        df_estimates = df[est_columns].copy()

        return df_estimates


    # Apply function to df_shasta_cvap_bg_wide
    df_shasta_cvap_bg_estimates = filter_moe_from_wide_df(df_shasta_cvap_bg_wide)
    df_shasta_cvap_bg_estimates
    return (df_shasta_cvap_bg_estimates,)


@app.cell
def _(BG_GIS_FILE, SHASTA_FIPS, gpd):
    GDF_BG = gpd.read_file(BG_GIS_FILE)
    gdf_shasta_bg = GDF_BG[GDF_BG["GEOID"].str.startswith(SHASTA_FIPS)].copy()
    del GDF_BG
    return (gdf_shasta_bg,)


@app.cell
def _(df_shasta_cvap_bg, df_shasta_cvap_bg_estimates, gdf_shasta_bg):
    df_shasta_cvap_total_bg = df_shasta_cvap_bg[
        df_shasta_cvap_bg["lntitle"] == "Total"
    ].copy()
    gdf_shasta_cvap_bg = gdf_shasta_bg.merge(
        df_shasta_cvap_bg_estimates,
        left_on="GEOID",
        right_on="geoid",
        validate="1:1",
    )
    return (gdf_shasta_cvap_bg,)


@app.cell
def _(mo):
    mo.md(r"""
    # MERGE
    """)
    return


@app.cell
def _(gdf_shasta_cvap_bg):
    gdf_shasta_cvap_bg.plot()
    return


@app.cell
def _(gdf_precinct_results):
    gdf_precinct_results
    return


@app.cell
def _():
    # TODO: I want merge the demographic figures from @data://gdf_shasta_bg to @data://gdf_precinct_results . @data://gdf_precinct_results has the final geographies I need. If I remember correctly, I will need to run an operation on @data://gdf_shasta_bg that tell me the land area % that each precinct has for each bg (block group). Then I can use that land area percentage to recalculate the demographic figures and group by precinct number to sum the totals for each precinct. I plan on using Tobler: https://github.com/pysal/tobler
    return


@app.cell
def _(interpolated_gdf):
    interpolated_gdf
    return


@app.cell
def _(gdf_precinct_results, gdf_shasta_cvap_bg, tobler):
    # Define projected CRS for accurate area-based interpolation
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )

    # Prepare source: block group CVAP geodataframe
    source_gdf = gdf_shasta_cvap_bg.to_crs(PROJECTED_CRS)

    # Prepare target: precinct geometries (ensure we preserve all)
    target_gdf = gdf_precinct_results[["precinct", "geometry"]].to_crs(
        PROJECTED_CRS
    )
    target_gdf = target_gdf.set_index(
        "precinct"
    )  # Set as index so tobler preserves it

    # Identify ALL CVAP estimate columns (extensive variables — all population counts)
    extensive_vars = [
        col for col in source_gdf.columns if col.endswith("_cvap_est")
    ]

    # Confirm we're including total_cvap_est
    assert "total_cvap_est" in extensive_vars, (
        "total_cvap_est missing from source data"
    )

    print(
        f"Interpolating {len(extensive_vars)} CVAP variables to {len(target_gdf)} precincts:"
    )
    print("\n".join([f"  - {var}" for var in extensive_vars[:10]]))
    if len(extensive_vars) > 10:
        print(f"  ... and {len(extensive_vars) - 10} more")

    # Perform area-weighted interpolation
    interpolated_gdf = tobler.area_weighted.area_interpolate(
        source_df=source_gdf,
        target_df=target_gdf,
        extensive_variables=extensive_vars,
        intensive_variables=[],  # none yet (e.g., %s or densities — we'll derive those)
        allocate_total=True,  # distribute full source value across targets
        n_jobs=1,  # parallel jobs; use -1 for all cores, but may not help small data
    )

    # Convert back to original CRS
    interpolated_gdf = interpolated_gdf.to_crs(gdf_precinct_results.crs)

    # Merge interpolated CVAP data into original precinct results
    gdf_precinct_cvap = gdf_precinct_results[
        [
            "precinct",
            "registered_voters",
            "total_votes_yes",
            "total_votes_no",
            "geometry",
        ]
    ].merge(
        interpolated_gdf.drop(
            columns="geometry"
        ),  # keep only the interpolated data
        on="precinct",
        how="left",
        suffixes=("", "_interpolated"),
        validate="1:1",
    )

    # Fill any failed interpolation with 0 (should be rare)
    for col in extensive_vars:
        gdf_precinct_cvap[col] = (
            gdf_precinct_cvap[col].round().fillna(0).astype(int)
        )

    # Optional: compute diagnostic field — is total_cvap_est close to sum of others?
    # This helps assess potential overlap or estimation differences

    component_sum_cols = [col for col in extensive_vars if col != "total_cvap_est"]
    gdf_precinct_cvap["_sum_of_cvap_components"] = gdf_precinct_cvap[
        component_sum_cols
    ].sum(axis=1)
    gdf_precinct_cvap["_cvap_residual"] = (
        gdf_precinct_cvap["total_cvap_est"]
        - gdf_precinct_cvap["_sum_of_cvap_components"]
    )

    # Show diagnostics
    print("\n🔍 Diagnostic: total_cvap_est vs sum of components (per precinct)")
    print(
        gdf_precinct_cvap[
            [
                "precinct",
                "total_cvap_est",
                "_sum_of_cvap_components",
                "_cvap_residual",
            ]
        ]
        .round()
        .head(10)
    )
    return gdf_precinct_cvap, interpolated_gdf


@app.cell
def _(gdf_precinct_cvap):
    gdf_precinct_cvap.to_file("./outputs/shasta_merge.gpkg", driver="GPKG")
    return


@app.cell
def _(df_shasta_cvap_bg_wide):
    # Calculate residuals between total_cvap_est and sum of all other est columns
    est_columns = [
        col
        for col in df_shasta_cvap_bg_wide.columns
        if col.endswith("_cvap_est") and col != "total_cvap_est"
    ]
    df_shasta_cvap_bg_wide["_sum_of_components"] = df_shasta_cvap_bg_wide[
        est_columns
    ].sum(axis=1)
    df_shasta_cvap_bg_wide["_residual"] = (
        df_shasta_cvap_bg_wide["total_cvap_est"]
        - df_shasta_cvap_bg_wide["_sum_of_components"]
    )

    # Compute summary statistics of residuals
    residual_summary = df_shasta_cvap_bg_wide["_residual"].describe()

    # Display residual summary and example rows
    print("Residuals between total_cvap_est and sum of demographic components:")
    print(residual_summary)
    print("\nSample of residuals:")
    print(
        df_shasta_cvap_bg_wide[
            ["geoid", "total_cvap_est", "_sum_of_components", "_residual"]
        ].head()
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
