import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CVAP by Block

    This notebook outputs a GIS data file with Citizen Voter Age Population by block. The source data for CVAP by block is the [Redistricting Hub](https://redistrictingdatahub.org/dataset/california-cvap-data-disaggregated-to-the-2020-block-level-2023/).
    """)
    return


@app.cell
def _():
    from pathlib import Path
    import urllib.request

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    return Path, gpd, mo, pd, urllib


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    READ_DTYPE = {"GEOID20": str}
    CVAP_COLUMN_PREFIX = "CVAP"

    GIS_REQUIRED_COLUMNS = ["GEOID20", "geometry"]
    return CVAP_COLUMN_PREFIX, GIS_REQUIRED_COLUMNS, READ_DTYPE


@app.cell
def _():
    COLUMNS_TO_RETAIN_AS_IS = [
        "CVAP_TOT23",  # Total Citizen Voting Age Population 2023
        "CVAP_WHT23",  # White Citizen Voting Age Population 2023
        "CVAP_BLK23",  # Black or African American Citizen Voting Age Population 2023
        "CVAP_2OM23",  # Two or More Races Citizen Voting Age Population 2023
    ]
    NEW_COMPOSITE_COLUMNS = [
        "_cvap_api23",  # Asian and Pacific Islander Citizen Voting Age Population 2023
        "_cvap_amw23",  # American Indian and Alaska Native (Non-Hispanic) Citizen Voting Age Population 2023
    ]
    return COLUMNS_TO_RETAIN_AS_IS, NEW_COMPOSITE_COLUMNS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filepaths
    """)
    return


@app.cell
def _():
    RDH_CVAP_DATA_FP = "./inputs/rdh/ca_cvap_2023_2020_b.csv"
    return (RDH_CVAP_DATA_FP,)


@app.cell
def _():
    CA_CENSUS_BLOCKS_FILE_PATH = "./inputs/census/tl_2020_06_tabblock20.zip"
    return (CA_CENSUS_BLOCKS_FILE_PATH,)


@app.cell
def _():
    CA_CENSUS_BLOCKS_URL_PATH = "https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_06_tabblock20.zip"
    return


@app.cell
def _():
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )
    OUTPUT_PATH = "./outputs/cvap_blocks.gpkg"
    DRIVER_FORMAT = "GPKG"
    return DRIVER_FORMAT, OUTPUT_PATH, PROJECTED_CRS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(CVAP_COLUMN_PREFIX, RDH_CVAP_DATA_FP, READ_DTYPE, pd):
    RH_VAP_DF = pd.read_csv(
        RDH_CVAP_DATA_FP, dtype=READ_DTYPE, index_col="GEOID20"
    )

    cvap_columns = [
        column
        for column in list(RH_VAP_DF)
        if column.startswith(CVAP_COLUMN_PREFIX)
    ]
    rh_cvap_df = RH_VAP_DF[cvap_columns].copy()
    rh_cvap_df
    return (rh_cvap_df,)


@app.cell
def _(
    CA_CENSUS_BLOCKS_FILE_PATH,
    CA_CENSUS_BLOCKS_URL,
    GIS_REQUIRED_COLUMNS,
    Path,
    gpd,
    urllib,
):
    census_blocks_path = Path(CA_CENSUS_BLOCKS_FILE_PATH)

    if not census_blocks_path.exists():
        urllib.request.urlretrieve(CA_CENSUS_BLOCKS_URL, census_blocks_path)

    CA_BLOCKS_GDF = gpd.read_file(census_blocks_path)
    ca_block_gdf = CA_BLOCKS_GDF[GIS_REQUIRED_COLUMNS].copy()
    del CA_BLOCKS_GDF

    ca_block_gdf.head()
    return (ca_block_gdf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Transform data
    """)
    return


@app.cell
def _(COLUMNS_TO_RETAIN_AS_IS, NEW_COMPOSITE_COLUMNS, rh_cvap_df):
    transformed_rh_cvap_df = rh_cvap_df.copy()

    # Calculate Asian and Pacific Islander CVAP as sum of Asian (CVAP_ASN23) and Native Hawaiian/Other Pacific Islander (CVAP_NHP23)
    transformed_rh_cvap_df["_cvap_api23"] = (
        transformed_rh_cvap_df["CVAP_ASN23"] + transformed_rh_cvap_df["CVAP_NHP23"]
    )

    # Calculate American Indian and Alaska Native (AIAN) as Total AIAN (CVAP_AMI23) minus AIAN and and Black (CVAP_AIB23)
    # This is necessary to avoid a double count b/c CVAP_BLK23 includes CVAP_AIB23
    transformed_rh_cvap_df["_cvap_amw23"] = (
        transformed_rh_cvap_df["CVAP_AIA23"] - transformed_rh_cvap_df["CVAP_AIB23"]
    )

    transformed_rh_cvap_df = transformed_rh_cvap_df[
        COLUMNS_TO_RETAIN_AS_IS + NEW_COMPOSITE_COLUMNS
    ].copy()
    transformed_rh_cvap_df
    return (transformed_rh_cvap_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Join CVAP demographics and GIS file
    """)
    return


@app.cell
def _(
    DRIVER_FORMAT,
    OUTPUT_PATH,
    PROJECTED_CRS,
    ca_block_gdf,
    transformed_rh_cvap_df,
):
    assert len(transformed_rh_cvap_df) == len(ca_block_gdf)
    ca_block_cvap_gdf = ca_block_gdf.merge(
        transformed_rh_cvap_df, left_on="GEOID20", right_index=True, validate="1:1"
    )

    ca_block_cvap_gdf.to_crs(PROJECTED_CRS).to_file(
        OUTPUT_PATH, driver=DRIVER_FORMAT
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Appendix
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data fields

    CVAP_TOT23 CVAP Estimate for Total
    CVAP_NHS23 CVAP Estimate for Not Hispanic or Latino
    CVAP_AMI23 CVAP Estimate for American Indian or Alaska Native Alone
    CVAP_ASI23 CVAP Estimate for Asian Alone
    CVAP_BLA23 CVAP Estimate for Black or African American Alone
    CVAP_NHP23 CVAP Estimate for Native Hawaiian or Other Pacific Islander Alone
    CVAP_WHT23 CVAP Estimate for White Alone
    CVAP_AIW23 CVAP Estimate for American Indian or Alaska Native and White
    CVAP_ASW23 CVAP Estimate for Asian and White
    CVAP_BLW23 CVAP Estimate for Black or African American and White
    CVAP_AIB23 CVAP Estimate for American Indian or Alaska Native and Black or African American
    CVAP_2OM23 CVAP Estimate for Remainder of Two or More Race Responses
    CVAP_HSP23 CVAP Estimate for Hispanic or Latino
    CVAP_AIA23 CVAP Estimate for American Indian or Alaska Native Alone or In Combination
    CVAP_ASN23 CVAP Estimate for Asian Alone or In Combination
    CVAP_BLK23 CVAP Estimate for Black or African American Alone or In Combination
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CVAP Field Corresponding PL Field(s)

    CVAP_TOT23 P0040001
    CVAP_NHS23 P0040003
    CVAP_AMI23 P0040007
    CVAP_ASI23 P0040008
    CVAP_BLA23 P0040006
    CVAP_NHP23 P0040009
    CVAP_WHT23 P0040005
    CVAP_AIW23 P0040014
    CVAP_ASW23 P0040015
    CVAP_BLW23 P0040013
    CVAP_AIB23 P0040018
    CVAP_2OM23 P0040011 - P0040018 - P0040014 - P0040013 - P0040015
    CVAP_HSP23 P0040002
    CVAP_AIA23 P0040007 + P0040018 + P0040014
    CVAP_ASN23 P0040008 + P0040015
    CVAP_BLK23 P0040006 + P0040013 + P0040018
    """)
    return


@app.cell(hide_code=True)
def _():
    return


if __name__ == "__main__":
    app.run()
