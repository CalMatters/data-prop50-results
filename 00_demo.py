import marimo

__generated_with = "0.17.8"
app = marimo.App(width="columns")


@app.cell
def _():
    import zipfile

    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    return gpd, mo, pd, zipfile


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
def _(BG_GIS_FILE, SHASTA_FIPS, gpd):
    GDF_BG = gpd.read_file(BG_GIS_FILE)
    gdf_shasta_bg = GDF_BG[GDF_BG["GEOID"].str.startswith(SHASTA_FIPS)].copy()
    del GDF_BG
    return (gdf_shasta_bg,)


@app.cell
def _(df_shasta_cvap_bg, gdf_shasta_bg):
    df_shasta_cvap_total_bg = df_shasta_cvap_bg[
        df_shasta_cvap_bg["lntitle"] == "Total"
    ].copy()
    gdf_shasta_bg.merge(
        df_shasta_cvap_total_bg, left_on="GEOID", right_on="geoid", validate="1:1"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    # MERGE
    """)
    return


@app.cell
def _(gdf_shasta_bg):
    gdf_shasta_bg.plot()
    return


@app.cell
def _(gdf_precinct_results):
    gdf_precinct_results.plot()
    return


@app.cell
def _():
    # TODO: I want merge the demographic figures from @data://gdf_shasta_bg to @data://gdf_precinct_results . @data://gdf_precinct_results has the final geographies I need. If I remember correctly, I will need to run an operation on @data://gdf_shasta_bg that tell me the land area % that each precinct has for each bg (block group). Then I can use that land area percentage to recalculate the demographic figures and group by precinct number to sum the totals for each precinct. I plan on using Tobler: https://github.com/pysal/tobler
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
