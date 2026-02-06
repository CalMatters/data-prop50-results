import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Statewide Precinct Results for 2024 Presidential Election

    Data source: [Statewide Database](https://statewidedatabase.org/d20/g24.html) (official redistricting database for the state of California)

    Data uses the SR Consolidated Precincts geographic unit for the results and mapping. We ran into issues trying to use SV such as the aggregation of votes for presidential candidates exceeding the total votes cast statewide according to the Secretary of State SOV results. We expect there was double counting due across consolidated precinct subunits.

    The vote aggregation for the SR data was closer to the SOS total. SR's aggregation was lower than the reported SOS total. This is likely explained by precincts with few voters that require redaction for privacy.
    """)
    return


@app.cell
def _():
    from pathlib import Path
    import urllib

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
    INDEX_COLUMNS = [
        "SRPREC_KEY",
        "SRPREC",
        "FIPS",
    ]
    MAJOR_PARTY_CAND_COLUMNS = [
        "PRSDEM01",  # Harris
        "PRSREP01",  # Trump
    ]
    PRES_RACE_CAND_COLUMNS = [
        "PRSAIP01",
        "PRSGRN01",
        "PRSLIB01",
        "PRSPAF01",
        *MAJOR_PARTY_CAND_COLUMNS,
    ]
    TOTAL_REGISTRATION_COLUMN = "TOTREG"
    return (
        INDEX_COLUMNS,
        MAJOR_PARTY_CAND_COLUMNS,
        PRES_RACE_CAND_COLUMNS,
        TOTAL_REGISTRATION_COLUMN,
    )


@app.cell
def _():
    CA_STATE_FIPS_ID = "06"
    return (CA_STATE_FIPS_ID,)


@app.cell
def _():
    PROJECTED_CRS = "EPSG:3310"  # NAD83 / California Albers (good for area calculations    in CA)
    return (PROJECTED_CRS,)


@app.cell
def _():
    TOTAL_SOV_VOTES = 15865475
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filepaths
    """)
    return


@app.cell
def _():
    COUNTY_FP = "./inputs/census/tl_2020_us_county.zip"
    return (COUNTY_FP,)


@app.cell
def _():
    RESULTS_DATA_SRPREC_FP = (
        "./inputs/statewide_db/state_g24_sov_data_by_g24_srprec.zip"
    )

    PRECINCTS_2024_FP = "./inputs/statewide_db/srprec_state_g24_v01_shp.zip"
    PRECINCTS_2024_URL_PATH = "https://statewidedatabase.org/pub/data/G24/state/srprec_state_g24_v01_shp.zip"
    return PRECINCTS_2024_FP, PRECINCTS_2024_URL_PATH, RESULTS_DATA_SRPREC_FP


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export
    """)
    return


@app.cell
def _():
    EXPORT_FP = "./outputs/precinct_results_2024.gpkg"
    EXPORT_DRIVER = "GPKG"
    EXPORT_COLUMNS = [
        "SRPREC_KEY",
        "county",
        "TOTREG",
        "PRSDEM01",
        "PRSREP01",
        "total_votes",
        "geometry",
    ]
    EXPORT_COLUMN_RENAMES = {
        "SRPREC_KEY": "precinct_id",
        "TOTREG": "registered_voters",
        "PRSDEM01": "dem_votes",
        "PRSREP01": "rep_votes",
    }
    return EXPORT_COLUMNS, EXPORT_COLUMN_RENAMES, EXPORT_DRIVER, EXPORT_FP


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read and prepare data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    County data used to map the FIPS records in the Statewide DB data to its county name.
    """)
    return


@app.cell
def _(CA_STATE_FIPS_ID, COUNTY_FP, gpd):
    _gdf_counties = gpd.read_file(COUNTY_FP)
    is_ca_county = _gdf_counties["STATEFP"] == CA_STATE_FIPS_ID
    _gdf_ca_counties = _gdf_counties[is_ca_county].copy()
    geo_id_county_map = {
        geo_id: name
        for geo_id, name in zip(
            _gdf_ca_counties["GEOID"], _gdf_ca_counties["NAME"]
        )
    }
    return (geo_id_county_map,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Precinct geographies

    I drop geographic records without a precint identifier. These are are along the coastline.
    """)
    return


@app.cell
def _(PRECINCTS_2024_FP, PRECINCTS_2024_URL_PATH, Path, urllib):
    # Create directory if it doesn't exist
    precincts_path = Path(PRECINCTS_2024_FP)
    precincts_path.parent.mkdir(parents=True, exist_ok=True)

    # Download file if it doesn't exist
    if not precincts_path.exists():
        urllib.request.urlretrieve(PRECINCTS_2024_URL_PATH, precincts_path)
    return (precincts_path,)


@app.cell
def _(PROJECTED_CRS, geo_id_county_map, gpd, precincts_path):
    gdf_precincts = gpd.read_file(precincts_path).to_crs(PROJECTED_CRS)
    len(gdf_precincts)


    gdf_precincts["county"] = gdf_precincts["FIPS_CODE"].map(geo_id_county_map)
    gdf_precincts = gdf_precincts[
        [
            "SRPREC_KEY",
            "county",
            "geometry",
        ]
    ].copy()

    # drop coastline
    gdf_precincts[gdf_precincts["SRPREC_KEY"].isna()].plot()
    gdf_precincts = gdf_precincts[~gdf_precincts["SRPREC_KEY"].isnull()].copy()
    return (gdf_precincts,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Election results
    """)
    return


@app.cell
def _(
    INDEX_COLUMNS,
    MAJOR_PARTY_CAND_COLUMNS,
    PRES_RACE_CAND_COLUMNS,
    RESULTS_DATA_SRPREC_FP,
    TOTAL_REGISTRATION_COLUMN,
    geo_id_county_map,
    pd,
):
    def read_results_data(fp, index_columns):
        _read_dtype = {col: str for col in index_columns}
        df = pd.read_csv(fp, dtype=_read_dtype)
        df = df[
            [
                *index_columns,
                *PRES_RACE_CAND_COLUMNS,
                TOTAL_REGISTRATION_COLUMN,
            ]
        ].copy()

        assert not df[PRES_RACE_CAND_COLUMNS].isnull().any().any(), (
            f"Found null values in vote tally column; coercion of redacted values will lead to ambigious mapping between redacted and values originally set to null"
        )
        df[PRES_RACE_CAND_COLUMNS] = df[PRES_RACE_CAND_COLUMNS].apply(
            pd.to_numeric, errors="coerce"
        )

        df["total_votes"] = df[PRES_RACE_CAND_COLUMNS].astype(float).sum(axis=1)
        df = df[
            [
                *index_columns,
                TOTAL_REGISTRATION_COLUMN,
                *MAJOR_PARTY_CAND_COLUMNS,
                "total_votes",
            ]
        ].copy()
        return df


    df_results = read_results_data(RESULTS_DATA_SRPREC_FP, INDEX_COLUMNS)
    df_results["county"] = df_results["FIPS"].map(geo_id_county_map)
    df_results
    return (df_results,)


@app.cell(hide_code=True)
def _(df_results_no_match, mo):
    mo.md(rf"""
    # Merge and export

    All of the precincts in the GIS data are retained on the merge. There are {len(df_results_no_match):,} precincts in the results dataset without a match in the GIS data. These precincts represent {df_results_no_match["TOTREG"].sum():,} registered voters and {df_results_no_match["total_votes"].sum():,} total votes across {list(df_results_no_match["county"].unique())} counties. 

    This represents a marginal number of votes. {df_results_no_match["TOTREG"].value_counts().loc[0] / len(df_results_no_match):.0%} of these precincts record zero registered voters.
    """)
    return


@app.cell
def _(
    EXPORT_COLUMNS,
    EXPORT_COLUMN_RENAMES,
    EXPORT_DRIVER,
    EXPORT_FP,
    df_results,
    gdf_precincts,
):
    gdf_precinct_results = gdf_precincts.merge(
        df_results,
        on=["SRPREC_KEY", "county"],
        how="outer",
        validate="1:1",
        indicator=True,
    )

    is_results_only_record = gdf_precinct_results["_merge"] == "right_only"
    df_results_no_match = gdf_precinct_results[is_results_only_record]

    gdf_precinct_results = gdf_precinct_results[
        gdf_precinct_results["_merge"] == "both"
    ].copy()

    _gdf_export = gdf_precinct_results[EXPORT_COLUMNS].copy()
    _gdf_export = _gdf_export.rename(columns=EXPORT_COLUMN_RENAMES)
    _gdf_export.to_file(EXPORT_FP, EXPORT_DRIVER)
    return (df_results_no_match,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Appendix
    """)
    return


@app.cell
def _(mo, perfect_match_pct):
    mo.md(rf"""
    Our analysis relies on the interpolation of block demographics to precincts. I am taking a peek at the Statewide Database mapping of these geographies to get a sense of how often a block's population needs to be split on interpolation vs 100% allocated as a subset of a precinct.

    {perfect_match_pct:.1%} of blocks are wholly allocated to a single precinct.
    """)
    return


@app.cell
def _(pd):
    df_prec_blk_mapping = pd.read_csv(
        "./inputs/statewide_db/state_g24_sr_blk_map.csv"
    )
    prec_blk_mapping_summary_stats = df_prec_blk_mapping["PCTBLK"].describe()

    perfect_match_pct = (df_prec_blk_mapping["PCTBLK"] == 100).sum() / len(
        df_prec_blk_mapping
    )

    prec_blk_mapping_summary_stats
    return (perfect_match_pct,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
