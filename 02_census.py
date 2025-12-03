import marimo

__generated_with = "0.18.1"
app = marimo.App(width="columns")


@app.cell
def _(mo):
    mo.md(r"""
    # CVAP by Tract

    This notebook produces a GIS file containing the [Citizen Voting Age Population](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) (CVAP) data by census tract. It reads in the CVAP dataset and transforms it into wide format, creating a `geoid`-indexed DataFrame with columns of the form `RACIAL_DEMOGRAPHIC_GROUP_cvap_est`, where each `_est` column represents the estimated number of voting-age citizens in a specific demographic group for each tract.


    Next, the notebook loads a GIS file for 2020 U.S. Census Tracts, filters it to California tracts, and merges the CVAP estimates onto the geospatial data. The resulting merged GeoDataFrame is validated to ensure no tracts are missing or duplicated, then exported to the `outputs` directory in GeoPackage format.
    """)
    return


@app.cell
def _():
    import zipfile

    import marimo as mo
    import geopandas as gpd
    import pandas as pd
    return gpd, mo, pd, zipfile


@app.cell
def _(OUTPUT_DRIVER, OUTPUT_FP, gdf_ca_cvap_tracts):
    gdf_ca_cvap_tracts.to_file(OUTPUT_FP, driver=OUTPUT_DRIVER)
    return


@app.cell
def _(df_ca_cvap_est_by_tract, gdf_ca_tracts):
    expected_tract_num = len(gdf_ca_tracts)
    gdf_ca_cvap_tracts = gdf_ca_tracts.merge(
        df_ca_cvap_est_by_tract, validate="1:1", how="outer"
    )
    observed_post_merge_tract_num = len(gdf_ca_cvap_tracts)

    assert gdf_ca_cvap_tracts["total_cvap_est"].isnull().sum() == 0, (
        "Unexpected null value post-merge, each row should contain a non-null value for total cvap estimate"
    )
    assert observed_post_merge_tract_num == expected_tract_num, (
        f"Number of tracts after merge ({observed_post_merge_tract_num}) does not match expected number ({expected_tract_num}). "
        "This suggests that some tracts were either duplicated or dropped during the merge operation."
    )

    gdf_ca_cvap_tracts
    return (gdf_ca_cvap_tracts,)


@app.cell
def _(TRACTS_GIS_FP, gpd, is_ca_geoid):
    GDF_TRACTS = gpd.read_file(TRACTS_GIS_FP)
    gdf_ca_tracts = GDF_TRACTS[is_ca_geoid(GDF_TRACTS["GEOID"])][
        ["GEOID", "geometry"]
    ].copy()
    gdf_ca_tracts = gdf_ca_tracts.rename(columns={"GEOID": "geoid"})
    del GDF_TRACTS
    gdf_ca_tracts.plot()
    return (gdf_ca_tracts,)


@app.cell
def _(
    CVAP_TRACT_DATA_FP,
    CVAP_ZIPPED_DATA_FP,
    TRACT_FIPS_LEN,
    filter_moe_from_wide_df,
    is_ca_geoid,
    read_csv_from_zip,
    transform_cvap_format,
):
    DF_CVAP_BY_TRACT = read_csv_from_zip(
        CVAP_ZIPPED_DATA_FP, CVAP_TRACT_DATA_FP, encoding="latin1"
    )
    DF_CVAP_BY_TRACT["geoid"] = DF_CVAP_BY_TRACT["geoid"].str.slice(
        -1 * TRACT_FIPS_LEN
    )

    df_ca_cvap_by_tract = DF_CVAP_BY_TRACT[
        is_ca_geoid(DF_CVAP_BY_TRACT["geoid"])
    ].copy()
    del DF_CVAP_BY_TRACT

    df_ca_cvap_by_tract = transform_cvap_format(df_ca_cvap_by_tract)
    df_ca_cvap_est_by_tract = filter_moe_from_wide_df(df_ca_cvap_by_tract)
    return (df_ca_cvap_est_by_tract,)


@app.cell
def _(CVAP_ZIPPED_DATA_FP, list_files_in_zip):
    list_files_in_zip(CVAP_ZIPPED_DATA_FP)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Filepaths
    """)
    return


@app.cell
def _():
    TRACTS_GIS_FP = "./inputs/census/tl_2020_06_tract.zip"
    return (TRACTS_GIS_FP,)


@app.cell
def _():
    CVAP_ZIPPED_DATA_FP = "./inputs/census/CVAP_2019-2023_ACS_csv_files.zip"
    CVAP_TRACT_DATA_FP = "Tract.csv"
    return CVAP_TRACT_DATA_FP, CVAP_ZIPPED_DATA_FP


@app.cell
def _():
    OUTPUT_FP = "./outputs/cvap_tracts.gpkg"
    OUTPUT_DRIVER = "GPKG"
    return OUTPUT_DRIVER, OUTPUT_FP


@app.cell
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    TRACT_FIPS_LEN = 11
    return (TRACT_FIPS_LEN,)


@app.cell
def _():
    CA_FIPS = "06"
    return (CA_FIPS,)


@app.cell
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


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
def _(pd):
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
    return (transform_cvap_format,)


@app.cell
def _(pd):
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
    return (filter_moe_from_wide_df,)


@app.cell
def _(CA_FIPS, pd):
    def is_ca_geoid(geoid_series: pd.Series) -> pd.Series:
        """
        Check if each GEOID in the series corresponds to California.

        California FIPS code is '06', and this function checks whether each
        GEOID string in the input series starts with this prefix.

        Parameters
        ----------
        geoid_series : pd.Series
            A pandas Series containing GEOID strings.

        Returns
        -------
        pd.Series
            A boolean Series indicating whether each GEOID starts with '06'.
        """
        return geoid_series.str.startswith(CA_FIPS)
    return (is_ca_geoid,)


if __name__ == "__main__":
    app.run()
