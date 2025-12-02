import marimo

__generated_with = "0.18.0"
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
    COMBINED_OUTPUT_PATH = "outputs/precincts.gpkg"
    COMBINED_OUTPUT_DRIVER = "GPKG"
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
    marin,
    monterey,
    napa,
    orange,
    pd,
    sacramento,
    san_benito,
    san_bernardino,
    san_diego,
    san_francisco,
    san_mateo,
    santa_cruz,
    shasta,
    siskiyou,
    solano,
    sonoma,
    sutter,
    tuolumne,
    ventura,
    yolo,
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
            los_angeles,
            marin,
            monterey,
            napa,
            orange,
            sacramento,
            san_benito,
            san_bernardino,
            san_diego,
            san_francisco,
            san_mateo,
            santa_cruz,
            shasta,
            siskiyou,
            solano,
            sonoma,
            sutter,
            tuolumne,
            ventura,
            yolo,
            yuba,
        ]
    )
    combined.head()
    return (combined,)


@app.cell
def _(COMBINED_OUTPUT_DRIVER, COMBINED_OUTPUT_PATH, combined):
    combined.to_file(COMBINED_OUTPUT_PATH, driver=COMBINED_OUTPUT_DRIVER)
    return


@app.function
def alter_gdf(gdf, county, rename={}, drop=[]):
    gdf["county"] = county
    gdf.rename(
        columns=rename,
        inplace=True,
    )
    gdf.drop(
        labels=drop,
        axis="columns",
        inplace=True,
        errors="ignore",
    )
    return gdf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    alameda = gpd.read_file(
        "inputs/counties/alameda/Consolidated_Precincts_-_November_4%2C_2025_Statewide_Special_Election.geojson"
    ).to_crs(PROJECTED_CRS)

    alameda = alter_gdf(
        alameda,
        "Alameda",
        {"Precinct_ID": "precinct_id"},
        [
            "Election_Name",
            "Precinct_ID",
            "OBJECTID",
            "Shape__Area",
            "Shape__Length",
        ],
    )
    alameda["precinct_name"] = None

    alameda.head()
    return (alameda,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Butte
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    butte = gpd.read_file("inputs/counties/butte/Butte Precincts 2025.kmz").to_crs(
        PROJECTED_CRS
    )

    butte = alter_gdf(
        butte,
        "Butte",
        {"id": "precinct_id", "Name": "precinct_name"},
        [
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
    colusa = gpd.read_file(
        "inputs/counties/colusa/Voting Precincts - 2020.shp"
    ).to_crs(PROJECTED_CRS)

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
        "inputs/counties/humboldt/precincts17sp_202507111714287445.zip"
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
    imperial = gpd.read_file(
        "inputs/counties/imperial/Voting_Precincts.shp"
    ).to_crs(PROJECTED_CRS)

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
    inyo = gpd.read_file("inputs/counties/inyo/consolidated.zip").to_crs(
        PROJECTED_CRS
    )

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
        "inputs/counties/los angeles/Registrar_Recorder_Election_Precincts_.shp"
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
    marin = gpd.read_file("inputs/counties/marin/Marin.shp").to_crs(PROJECTED_CRS)

    marin["county"] = "Marin"
    marin["precinct_name"] = None
    marin.rename(columns={"Precinct": "precinct_id"}, inplace=True)

    marin.head()
    return (marin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Monterey
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    monterey = gpd.read_file(
        "inputs/counties/monterey/2024-11-05 Precincts.zip"
    ).to_crs(PROJECTED_CRS)

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
    napa = gpd.read_file("inputs/counties/napa/Precincts.zip").to_crs(
        PROJECTED_CRS
    )

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
    orange = gpd.read_file("inputs/counties/orange/OC_Precinct_2024GE.zip").to_crs(
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
        "inputs/counties/sacramento/Voter_Registration_Precincts.shp"
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
        "inputs/counties/san benito/San_Benito_Base_Precincts_2025.zip"
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
    ## San Bernardino
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_bernardino = gpd.read_file(
        "inputs/counties/san bernardino/ROV_Precincts.zip"
    ).to_crs(PROJECTED_CRS)

    san_bernardino["county"] = "San Bernardino"
    san_bernardino.rename(
        columns={"PRECINCTID": "precinct_id", "ABRV_NAME": "precinct_name"},
        inplace=True,
    )
    san_bernardino.drop(
        columns=[
            "OBJECTID",
            "PRECINCT",
            "PRECINCT_N",
            "POLLID",
            "PORTION",
            "PRCNCT_PRT",
            "Shape__Are",
            "Shape__Len",
        ],
        inplace=True,
        errors="ignore",
    )

    san_bernardino.head()
    return (san_bernardino,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Diego
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_diego = gpd.read_file(
        "inputs/counties/san diego/Election_Precinct_2025_11_04.json"
    ).to_crs(PROJECTED_CRS)

    san_diego["county"] = "San Diego"
    san_diego.rename(
        columns={"consnum": "precinct_id", "consname": "precinct_name"},
        inplace=True,
    )
    san_diego.drop(
        columns=[
            "eid",
            "bt",
            "rv_totals",
            "pvbm",
            "count",
            "net_rvs",
            "SHAPE__Length",
            "objectid",
            "SHAPE__Area",
        ],
        inplace=True,
        errors="ignore",
    )

    san_diego.head()
    return (san_diego,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Francisco
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_francisco = gpd.read_file(
        "inputs/counties/san francisco/Election Precincts - Current, Defined 2022_20251120.zip"
    ).to_crs(PROJECTED_CRS)

    san_francisco = alter_gdf(
        san_francisco,
        "San Francisco",
        {"neigh22": "precinct_name", "prec_2022": "precinct_id"},
        [
            "supe22",
            "assemb22",
            "cong22",
            "bart22",
            "boe22",
            "sen22",
            "histnhood",
            "shape_leng",
            "shape_area",
        ],
    )

    san_francisco.head()
    return (san_francisco,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Mateo
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_mateo = gpd.read_file(
        "inputs/counties/san mateo/ELECTION_PRECINCTS.shp"
    ).to_crs(PROJECTED_CRS)

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
        "inputs/counties/santa cruz/Precincts_5962167425846516299.zip"
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
    shasta = gpd.read_file(
        "inputs/counties/shasta/Consolidated_Precincts.shp"
    ).to_crs(PROJECTED_CRS)

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
    siskiyou = gpd.read_file(
        "inputs/counties/siskiyou/Election_Precincts.zip"
    ).to_crs(PROJECTED_CRS)

    siskiyou = alter_gdf(
        siskiyou,
        "Siskiyou",
        {"PRCNCT_11": "precinct_id", "NAME_11": "precinct_name"},
        ["OBJECTID", "DIST_11", "NAME_NUM", "Shape__Are", "Shape__Len"],
    )

    siskiyou.head()
    return (siskiyou,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Solano
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    solano = gpd.read_file("inputs/counties/solano/Current_Precincts.json").to_crs(
        PROJECTED_CRS
    )

    solano = alter_gdf(
        solano,
        "Solano",
        {"precinct": "precinct_id", "pctname": "precinct_name"},
        [
            "objectid",
            "objectid_1",
            "consol",
            "pct",
            "shape_length",
            "precinct_g",
            "Shape__Area",
            "Shape__Length",
            "shape_leng",
        ],
    )

    solano.head()
    return (solano,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sonoma
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sonoma = gpd.read_file(
        "inputs/counties/sonoma/ROVPublic_Precincts.json"
    ).to_crs(PROJECTED_CRS)

    sonoma = alter_gdf(
        sonoma,
        "Sonoma",
        {"OBJECTID": "precinct_id"},
        ["SubPrecinct", "Shape__Area", "Shape__Length"],
    )
    sonoma["precinct_name"] = None

    sonoma.head()
    return (sonoma,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sutter
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sutter = gpd.read_file(
        "inputs/counties/sutter/Elections_Precincts.zip"
    ).to_crs(PROJECTED_CRS)

    sutter = alter_gdf(
        sutter,
        "Sutter",
        {"NAME": "precinct_name", "PRECINCTID": "precinct_id"},
        [
            "OBJECTID",
            "GlobalID",
            "Precinct_1",
            "MapLabel",
            "Shape__Are",
            "Shape__Len",
        ],
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
        "inputs/counties/tuolumne/TC_VotingPrecincts_Sept2022/TuolumneCounty_VotingPrecincts_consolidationNov2022.shp"
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
    ventura = gpd.read_file(
        "inputs/counties/ventura/Election_Precinct.zip"
    ).to_crs(PROJECTED_CRS)

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
    ## Yolo (consolidated)
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    yolo = gpd.read_file(
        "inputs/counties/yolo/Precincts_Consolidated_Open_Data.zip"
    ).to_crs(PROJECTED_CRS)

    yolo = alter_gdf(
        yolo,
        "Yolo",
        {"PRECINCTID": "precinct_id"},
        [
            "OBJECTID",
            "Precinct_N",
            "BOS_Dist",
            "BallotType",
            "PollVoters",
            "Registered",
            "City",
            "Shape__Are",
            "Shape__Len",
        ],
    )

    yolo.head()
    return (yolo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Yuba
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    yuba = gpd.read_file(
        "inputs/counties/yuba/YubaCountyCA_2024_03_21_001/VotingPrecincts.shp"
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
