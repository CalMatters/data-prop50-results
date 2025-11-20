import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This notebook standardizes the geographic precinct files from each county. It re-projects everything into NAD83/California Albers, and ensures that each feature has the following attributes:

    * `county`
    * `p_id` - The precinct ID

    If the county precincts also have a human-readable name that is included as `precinct_name` which is otherwise `None`.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    return gpd, mo, pd


@app.cell
def _():
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )
    return (PROJECTED_CRS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    alameda = gpd.read_file(
        "inputs/alameda/Consolidated_Precincts_-_November_4%2C_2025_Statewide_Special_Election.geojson"
    ).to_crs(PROJECTED_CRS)
    return (alameda,)


@app.cell
def _(alameda):
    alameda["county"] = "Alameda"
    alameda["p_id"] = alameda["Precinct_ID"]
    alameda["p_name"] = None
    return


@app.cell
def _(alameda):
    alameda.drop(
        labels=[
            "Election_Name",
            "Precinct_ID",
            "OBJECTID",
            "Shape__Area",
            "Shape__Length",
        ],
        axis="columns",
        inplace=True,
    )
    return


@app.cell
def _(alameda):
    alameda.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Butte
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    butte = gpd.read_file("inputs/butte/Butte Precincts 2025.kmz").to_crs(
        PROJECTED_CRS
    )
    return (butte,)


@app.cell
def _(butte):
    butte["county"] = "Butte"
    butte.rename(columns={"id": "p_id", "Name": "p_name"}, inplace=True)
    butte.drop(
        labels=[
            "id",
            "Name",
            "description",
            "timestamp",
            "begin",
            "end",
            "altitudeMode",
            "tessellate",
            "extrude",
            "visibility",
            "drawOrder",
            "icon",
        ],
        axis="columns",
        inplace=True,
        errors="ignore",
    )
    return


@app.cell
def _(butte):
    butte.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Colusa
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    colusa = gpd.read_file("inputs/colusa/Voting Precincts - 2020.shp").to_crs(
        PROJECTED_CRS
    )
    return (colusa,)


@app.cell
def _(colusa):
    colusa["county"] = "Colusa"
    colusa.rename(
        columns={"PRECINCTNU": "p_id", "PRECINCT": "p_name"}, inplace=True
    )
    colusa.drop(labels=["DISTRICT"], axis="columns", inplace=True, errors="ignore")
    return


@app.cell
def _(colusa):
    colusa.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imperial
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    imperial = gpd.read_file("inputs/imperial/Voting_Precincts.shp").to_crs(
        PROJECTED_CRS
    )
    return (imperial,)


@app.cell
def _(imperial):
    imperial.rename(columns={"precinctid": "p_id", "name": "p_name"}, inplace=True)
    return


@app.cell
def _(imperial):
    imperial.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Los Angeles
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    los_angeles = gpd.read_file(
        "inputs/los angeles/Registrar_Recorder_Election_Precincts_.shp"
    ).to_crs(PROJECTED_CRS)
    return (los_angeles,)


@app.cell
def _(los_angeles):
    los_angeles["county"] = "Los Angeles"
    los_angeles["p_name"] = None
    los_angeles.rename(columns={"Precinct": "p_id"}, inplace=True)
    los_angeles.drop(
        columns=[
            "OBJECTID",
            "VoteByMail",
            "BallotGrou",
            "SerialNumb",
            "VBMVoters",
            "PollVoters",
            "Shape__Are",
            "Shape__Len",
        ],
        inplace=True,
        errors="ignore",
    )
    return


@app.cell
def _(los_angeles):
    los_angeles.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Marin
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    marin = gpd.read_file("inputs/marin/Marin.shp").to_crs(PROJECTED_CRS)
    return (marin,)


@app.cell
def _(marin):
    marin["county"] = "Marin"
    marin.rename(columns={"Precinct": "p_id"}, inplace=True)
    marin["p_name"] = None
    return


@app.cell
def _(marin):
    marin.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sacramento
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sacramento = gpd.read_file(
        "inputs/sacramento/Voter_Registration_Precincts.shp"
    ).to_crs(PROJECTED_CRS)
    return (sacramento,)


@app.cell
def _(sacramento):
    sacramento["county"] = "Sacramento"
    sacramento.rename(
        columns={"PrecinctNo": "p_id", "Community": "p_name"}, inplace=True
    )
    sacramento.drop(
        labels=[
            "SqMi",
            "Congress",
            "Senate",
            "Assembly",
            "Supervisor",
            "City",
            "BoardofEd",
            "ComCollege",
            "UnifSchool",
            "FacilityID",
            "HighSchool",
            "ElemSchool",
            "CSD",
            "ResConserv",
            "Fire",
            "Irrigation",
            "Utility",
            "Flood",
            "Water",
            "RecAndPark",
            "TractNo",
        ],
        axis="columns",
        inplace=True,
        errors="ignore",
    )
    return


@app.cell
def _(sacramento):
    sacramento.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shasta
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    shasta = gpd.read_file("inputs/shasta/Consolidated_Precincts.shp").to_crs(
        PROJECTED_CRS
    )
    return (shasta,)


@app.cell
def _(shasta):
    shasta["county"] = "Shasta"
    shasta.rename(
        columns={"CONS_PCTNU": "p_id", "PP_Name": "p_name"}, inplace=True
    )
    shasta.drop(
        labels=[
            "OBJECTID",
            "CONS_PCTNA",
            "Mail_Only",
            "PP_ID",
            "PP_Address",
            "PP_Room",
            "Shape__Are",
            "Shape__Len",
        ],
        axis="columns",
        inplace=True,
        errors="ignore",
    )
    return


@app.cell
def _(shasta):
    shasta.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Combined
    """)
    return


@app.cell
def _(
    alameda,
    butte,
    colusa,
    imperial,
    los_angeles,
    marin,
    pd,
    sacramento,
    shasta,
):
    combined = pd.concat(
        [alameda, butte, colusa, imperial, los_angeles, marin, sacramento, shasta]
    )
    return (combined,)


@app.cell
def _(combined):
    combined.plot()
    return


@app.cell
def _(combined):
    combined.to_file("outputs/precincts.fgb", driver="FlatGeoBuf")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
