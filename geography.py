import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # California counties' precinct workflow

    This notebook standardizes the geographic precinct files from each county. It re-projects everything into NAD83/California Albers, and ensures that each feature has the following attributes:

    * `county`
    * `precinct_id` - The precinct ID

    If the county precincts also have a human-readable name that is included as `precinct_name` which is otherwise `None`.
    """)
    return


@app.cell
def _():
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )
    COMBINED_OUTPUT_PATH = "outputs/precincts.geojson"
    COMBINED_OUTPUT_DRIVER = "GeoJSON"
    return COMBINED_OUTPUT_DRIVER, COMBINED_OUTPUT_PATH, PROJECTED_CRS


@app.cell
def _(combined):
    combined.plot()
    return


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    return gpd, mo, pd


@app.cell
def _(
    alameda,
    butte,
    colusa,
    humboldt,
    imperial,
    inyo,
    los_angeles,
    monterey,
    napa,
    orange,
    pd,
    sacramento,
    san_benito,
    san_mateo,
    santa_cruz,
    shasta,
    siskiyou,
    sutter,
    tuolumne,
    ventura,
    yuba,
):
    combined = pd.concat(
        [
            alameda,
            butte,
            colusa,
            humboldt,
            imperial,
            inyo,
            monterey,
            napa,
            los_angeles,
            orange,
            sacramento,
            san_benito,
            san_mateo,
            santa_cruz,
            shasta,
            siskiyou,
            sutter,
            tuolumne,
            ventura,
            yuba,
        ]
    )
    combined.head()
    return (combined,)


@app.cell
def _(COMBINED_OUTPUT_DRIVER, COMBINED_OUTPUT_PATH, combined):
    combined.to_file(COMBINED_OUTPUT_PATH, driver=COMBINED_OUTPUT_DRIVER)
    return


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
    alameda["precinct_id"] = alameda["Precinct_ID"]
    alameda["precinct_name"] = None

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

    butte["county"] = "Butte"
    butte.rename(
        columns={"id": "precinct_id", "Name": "precinct_name"}, inplace=True
    )
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

    butte.head()
    return (butte,)


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

    colusa["county"] = "Colusa"
    colusa.rename(
        columns={"PRECINCTNU": "precinct_id", "PRECINCT": "precinct_name"},
        inplace=True,
    )
    colusa.drop(labels=["DISTRICT"], axis="columns", inplace=True, errors="ignore")

    colusa.head()
    return (colusa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Humbodlt
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    humboldt = gpd.read_file(
        "inputs/humboldt/precincts17sp_202507111714287445.zip"
    ).to_crs(PROJECTED_CRS)

    humboldt["county"] = "Humboldt"
    humboldt.rename(
        columns={"PRECINCT": "precinct_name", "Prcnct_Num": "precinct_id"},
        inplace=True,
    )
    humboldt.drop(
        columns=["DISTRICT", "ACRES", "POP2010", "Shape_Leng", "Shape_Area"],
        inplace=True,
        errors="ignore",
    )

    humboldt.head()
    return (humboldt,)


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

    imperial.rename(
        columns={"precinctid": "precinct_id", "name": "precinct_name"},
        inplace=True,
    )

    imperial.head()
    return (imperial,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inyo (consolidated)
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    inyo = gpd.read_file("inputs/inyo/consolidated.zip").to_crs(PROJECTED_CRS)

    inyo["county"] = "Inyo"
    inyo.rename(columns={"cons_prec": "precinct_id"}, inplace=True)
    inyo.drop(
        columns=["OBJECTID", "GlobalID", "Shape__Are", "Shape__Len"],
        inplace=True,
        errors="ignore",
    )

    inyo.head()
    return (inyo,)


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

    los_angeles["county"] = "Los Angeles"
    los_angeles["precinct_name"] = None
    los_angeles.rename(columns={"Precinct": "precinct_id"}, inplace=True)
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

    los_angeles.head()
    return (los_angeles,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Marin
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    marin = gpd.read_file("inputs/marin/Marin.shp").to_crs(PROJECTED_CRS)

    marin["county"] = "Marin"
    marin["precinct_name"] = None
    marin.rename(columns={"Precinct": "precinct_id"}, inplace=True)

    marin.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Monterey
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    monterey = gpd.read_file("inputs/monterey/2024-11-05 Precincts.zip").to_crs(
        PROJECTED_CRS
    )

    monterey["county"] = "Monterey"
    monterey.rename(
        columns={"precinct": "precinct_id", "precinct_n": "precinct_name"},
        inplace=True,
    )
    monterey.drop(
        columns=["Shape_Leng", "Shape_Area"], inplace=True, errors="ignore"
    )

    monterey.head()
    return (monterey,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Napa
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    napa = gpd.read_file("inputs/napa/Precincts.zip").to_crs(PROJECTED_CRS)

    napa["county"] = "Napa"
    napa["precinct_name"] = None
    napa.rename(columns={"precinct": "precinct_id"}, inplace=True)
    napa.drop(
        columns=[
            "objectid",
            "pdflink",
            "supervisor",
            "municipali",
            "school_dis",
            "park_ward",
            "nvc_truste",
            "boe_truste",
            "nvusd_area",
            "napacityco",
            "sfid",
            "globalid",
            "Shape__Are",
            "Shape__Len",
        ],
        inplace=True,
        errors="ignore",
    )

    napa.head()
    return (napa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orange
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    orange = gpd.read_file("inputs/orange/OC_Precinct_2024GE.zip").to_crs(
        PROJECTED_CRS
    )

    orange["county"] = "Orange"
    orange["precinct_name"] = None
    orange.rename(columns={"Precinct": "precinct_id"}, inplace=True)
    orange.drop(
        columns=["Shape_Leng", "Shape_Area"], inplace=True, errors="ignore"
    )

    orange.head()
    return (orange,)


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

    sacramento["county"] = "Sacramento"
    sacramento.rename(
        columns={"PrecinctNo": "precinct_id", "Community": "precinct_name"},
        inplace=True,
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

    sacramento.head()
    return (sacramento,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Benito
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_benito = gpd.read_file(
        "inputs/san benito/San_Benito_Base_Precincts_2025.zip"
    ).to_crs(PROJECTED_CRS)

    san_benito["county"] = "San Benito"
    san_benito.rename(
        columns={"PrecinctID": "precinct_id", "Name": "precinct_name"},
        inplace=True,
    )
    san_benito.drop(
        columns=[
            "FID",
            "OBJECTID",
            "Id",
            "Sub_PID",
            "Consolidat",
            "Shape__Are",
            "Shape__Len",
            "Precinct",
            "Shape__A_1",
            "Shape__L_1",
        ],
        inplace=True,
        errors="ignore",
    )

    san_benito.head()
    return (san_benito,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Mateo
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_mateo = gpd.read_file("inputs/san mateo/ELECTION_PRECINCTS.shp").to_crs(
        PROJECTED_CRS
    )

    san_mateo["county"] = "San Mateo"
    san_mateo.rename(columns={"PrecinctID": "precinct_id"}, inplace=True)
    san_mateo.drop(columns=["OBJECTID"], inplace=True, errors="ignore")

    san_mateo.head()
    return (san_mateo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Cruz
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    santa_cruz = gpd.read_file(
        "inputs/santa cruz/Precincts_5962167425846516299.zip"
    ).to_crs(PROJECTED_CRS)

    santa_cruz["county"] = "Santa Cruz"
    santa_cruz["precinct_name"] = None
    santa_cruz.rename(columns={"Precinct": "precinct_id"}, inplace=True)
    santa_cruz.drop(
        columns=[
            "XCOORD",
            "YCOORD",
            "CITYLIMITS",
            "SUPDIST",
            "CSA09BSCHX",
            "CSA09CREFD",
            "CSA38SHRF",
            "CSA53VC",
            "FIREDIST",
            "MIDPENINOS",
            "PORTDIST",
            "PVWMA",
            "RECDIST",
            "RESCONDIST",
            "SCHOOLPRI",
            "SCHOOLSEC",
            "WATERDIST",
            "STASSMBLY",
            "STATESEN",
            "BOETRUST",
            "CABCOTRUST",
            "PVTRUST",
            "SCCTRUST",
            "SLVTRUST",
            "USCONGRESS",
            "PVHCD",
            "WVTRUST",
            "WATCC",
            "SUETRUST",
            "SCCC",
            "ASJUSD",
        ],
        inplace=True,
        errors="ignore",
    )

    santa_cruz.head()
    return (santa_cruz,)


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

    shasta["county"] = "Shasta"
    shasta.rename(
        columns={"CONS_PCTNU": "precinct_id", "PP_Name": "precinct_name"},
        inplace=True,
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
    shasta.head()
    return (shasta,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Siskiyou
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    siskiyou = gpd.read_file("inputs/siskiyou/Election_Precincts.zip").to_crs(
        PROJECTED_CRS
    )

    siskiyou["county"] = "Siskiyou"
    siskiyou.rename(
        columns={"PRCNCT_11": "precinct_id", "NAME_11": "precinct_name"},
        inplace=True,
    )
    siskiyou.drop(
        labels=["OBJECTID", "DIST_11", "NAME_NUM", "Shape__Are", "Shape__Len"],
        axis="columns",
        inplace=True,
        errors="ignore",
    )

    siskiyou.head()
    return (siskiyou,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sutter
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sutter = gpd.read_file("inputs/sutter/Elections_Precincts.zip").to_crs(
        PROJECTED_CRS
    )

    sutter["county"] = "Sutter"
    sutter.rename(
        columns={"NAME": "precinct_name", "PRECINCTID": "precinct_id"},
        inplace=True,
    )
    sutter.drop(
        columns=[
            "OBJECTID",
            "GlobalID",
            "Precinct_1",
            "MapLabel",
            "Shape__Are",
            "Shape__Len",
        ],
        inplace=True,
        errors="ignore",
    )

    sutter.head()
    return (sutter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tuolumne
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    tuolumne = gpd.read_file(
        "inputs/tuolumne/TC_VotingPrecincts_Sept2022/TuolumneCounty_VotingPrecincts_consolidationNov2022.shp"
    ).to_crs(PROJECTED_CRS)

    tuolumne["county"] = "Tuolumne"
    tuolumne.rename(
        columns={"PREC_NO": "precinct_id", "PRECINCT": "precicnt_name"},
        inplace=True,
    )
    tuolumne.drop(
        columns=["HomePrecin", "PropConsol"], inplace=True, errors="ignore"
    )

    tuolumne.head()
    return (tuolumne,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ventura
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    ventura = gpd.read_file("inputs/ventura/Election_Precinct.zip").to_crs(
        PROJECTED_CRS
    )

    ventura["county"] = "Ventura"
    ventura["precinct_name"] = None
    ventura.rename(columns={"number_": "precinct_id"}, inplace=True)
    ventura.drop(
        columns=[
            "objectid",
            "gr_cr_date",
            "gr_co_date",
            "acres",
            "created_da",
            "last_edite",
            "oldprecinc",
            "globalid",
            "electid",
            "shape_Leng",
            "shape_Area",
        ],
        inplace=True,
        errors="ignore",
    )

    ventura.head()
    return (ventura,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Yuba
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    yuba = gpd.read_file(
        "inputs/yuba/YubaCountyCA_2024_03_21_001/VotingPrecincts.shp"
    ).to_crs(PROJECTED_CRS)

    yuba["county"] = "Yuba"
    yuba.rename(
        columns={"precinctid": "precinct_id", "name": "precinct_name"},
        inplace=True,
    )
    yuba.drop(
        columns=[
            "facilityid",
            "pollingid",
            "GlobalID",
            "created_da",
            "last_edite",
            "precinctty",
        ],
        inplace=True,
        errors="ignore",
    )

    yuba.head()
    return (yuba,)


if __name__ == "__main__":
    app.run()
