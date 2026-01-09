import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    return gpd, pd


@app.cell
def _():
    CD_GIS_FP = (
        "./inputs/wedrawthelines/CD_Final shapefile/CD_Final 2021-12-20.shp"
    )
    CD_PARTY_FP = 'inputs/california-cd-rep-party-affiliation-nov-2025.csv'
    PRECINCTS_GIS_FP = "./outputs/precincts.gpkg"
    return CD_GIS_FP, CD_PARTY_FP, PRECINCTS_GIS_FP


@app.cell
def _(CD_PARTY_FP, pd):
    # get the partisan affilation of each district's representative in November 2025
    cd_party = pd.read_csv(CD_PARTY_FP, dtype={'district': str})
    return (cd_party,)


@app.cell
def _(CD_GIS_FP, gpd):
    # read in congressional district boundaries
    cd_gdf = gpd.read_file(CD_GIS_FP).to_crs("EPSG:3310")
    return (cd_gdf,)


@app.cell
def _(PRECINCTS_GIS_FP, gpd):
    # read in statewide precincts boundaries
    precincts_gdf = gpd.read_file(PRECINCTS_GIS_FP)
    return (precincts_gdf,)


@app.cell
def _(cd_gdf, precincts_gdf):
    # spatial join the two to determine the congressional district that each precinct is in
    precincts_joined_cd_gdf = precincts_gdf.sjoin(cd_gdf)
    return (precincts_joined_cd_gdf,)


@app.cell
def _(cd_party, precincts_joined_cd_gdf):
    # drop most of the columns that come from cd_gdf
    precincts_with_district_gdf = precincts_joined_cd_gdf[
        ["county", "precinct_id", "precinct_name", "geometry", "DISTRICT"]
    ]

    # and then rename for consistent casing
    precincts_with_district_gdf = precincts_with_district_gdf.rename(columns={"DISTRICT": "district"})

    # and join with party affiliation of rep in office in November 2025
    precincts_with_district_party_gdf = precincts_with_district_gdf.merge(cd_party, on='district')

    precincts_with_district_party_gdf
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
