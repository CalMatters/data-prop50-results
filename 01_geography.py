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
    * `precinct_name` - The human-readable name provided by the county or is otherwise an empty string
    """)
    return


@app.cell
def _():
    # NAD83 / California Albers (good for area calculations in CA)
    PROJECTED_CRS = "EPSG:3310"

    # the path for the output file
    COMBINED_OUTPUT_PATH = "outputs/precincts.geojson"

    # the driver to match the file type of COMBINED_OUTPUT_PATH, passed to df.to_file function
    COMBINED_OUTPUT_DRIVER = "GeoJSON"
    return COMBINED_OUTPUT_DRIVER, COMBINED_OUTPUT_PATH, PROJECTED_CRS


@app.cell
def _(combined_reordered):
    # show the counties that are included in the workflow
    combined_reordered.plot()
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    return gpd, mo, pd


@app.cell
def _(
    COMBINED_OUTPUT_DRIVER,
    COMBINED_OUTPUT_PATH,
    alameda,
    butte,
    colusa,
    contra_costa,
    fresno,
    glenn,
    humboldt,
    imperial,
    inyo,
    lake,
    los_angeles,
    marin,
    mariposa,
    mendocino,
    monterey,
    napa,
    orange,
    pd,
    sacramento,
    san_benito,
    san_bernardino,
    san_diego,
    san_francisco,
    san_joaquin,
    san_luis_obispo,
    san_mateo,
    santa_barbara,
    santa_cruz,
    shasta,
    siskiyou,
    solano,
    sonoma,
    sutter,
    tehama,
    tulare,
    tuolumne,
    ventura,
    yolo,
    yuba,
):
    # create a new data frame from the data frames for each county
    combined = pd.concat(
        [
            alameda,
            butte,
            colusa,
            contra_costa,
            fresno,
            glenn,
            humboldt,
            imperial,
            inyo,
            lake,
            los_angeles,
            marin,
            mariposa,
            mendocino,
            monterey,
            napa,
            orange,
            sacramento,
            san_benito,
            san_bernardino,
            san_diego,
            san_francisco,
            san_joaquin,
            san_luis_obispo,
            san_mateo,
            santa_barbara,
            santa_cruz,
            shasta,
            siskiyou,
            solano,
            sonoma,
            sutter,
            tehama,
            tulare,
            tuolumne,
            ventura,
            yolo,
            yuba,
        ]
    )

    # make sure any mising "precinct_name" values are empty strings
    combined.fillna(value={"precinct_name": ""}, inplace=True)

    # reorder the columns to make it more readable
    combined_reordered = combined[
        ["county", "precinct_id", "precinct_name", "geometry"]
    ]

    # save the reordered results to a file at COMBINED_OUTPUT_PATH
    combined_reordered.to_file(COMBINED_OUTPUT_PATH, driver=COMBINED_OUTPUT_DRIVER)

    # show the data on the screen
    print(combined_reordered)
    return (combined_reordered,)


@app.function
def alter_df(df, county, rename={}, drop=[]):
    """
    Alter the dataframe, in place, by renaming and dropping columns
    """
    df["county"] = county
    df.rename(
        columns=rename,
        inplace=True,
    )
    df.drop(
        labels=drop,
        axis="columns",
        inplace=True,
        errors="ignore",
    )
    return df


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    # this pattern is used for all counties

    # read in the source file with geopandas and reproject to PROJECTED_CRS
    alameda = gpd.read_file(
        "inputs/counties/alameda/Consolidated_Precincts_-_November_4%2C_2025_Statewide_Special_Election.geojson"
    ).to_crs(PROJECTED_CRS)

    # use alter_df to clean, renaming some columns and dropping others
    alameda = alter_df(
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

    # look at the first five rows
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

    butte = alter_df(
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

    colusa = alter_df(
        colusa,
        "Colusa",
        {"PRECINCTNU": "precinct_id", "PRECINCT": "precinct_name"},
        ["DISTRICT"],
    )

    colusa.head()
    return (colusa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Contra Costa
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    contra_costa = gpd.read_file(
        "inputs/counties/contra costa/PrecinctSet_PDMJ017.json"
    ).to_crs(PROJECTED_CRS)

    contra_costa = alter_df(
        contra_costa,
        "Contra Costa",
        {"sPrecinctID": "precinct_id", "szPrecinctName": "precinct_name"},
        [
            "OBJECTID",
            "sPrecinctPortion",
            "sMapNumber",
            "szRemarks",
            "szCityName",
            "iZeroRegistrationPct",
            "iLanguageTargetedPct",
            "geomPrecinct",
            "szPrecinctSetDesc",
            "created_user",
            "created_date",
            "last_edited_user",
            "last_edited_date",
            "GlobalID",
            "Shape__Area",
            "Shape__Length",
        ],
    )

    contra_costa.head()
    return (contra_costa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fresno
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    fresno = gpd.read_file(
        "inputs/counties/fresno/ELECTIONS_NOV2024_VOTING_PRECINCTS_VW.zip"
    ).to_crs(PROJECTED_CRS)

    fresno = alter_df(
        fresno,
        "Fresno",
        {"VP": "precinct_id"},
        [
            "OBJECTID_1",
            "SUM_Poll_C",
            "SUM_lTotal",
            "SUM_lSpeci",
            "Shape_Leng",
            "Shape__Are",
            "Shape__Len",
        ],
    )

    fresno.head()
    return (fresno,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Glenn
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    glenn = (
        gpd.read_file("inputs/counties/glenn/Precincts_9_3_2.json")
        .to_crs(PROJECTED_CRS)
        .to_crs(PROJECTED_CRS)
    )

    glenn = alter_df(
        glenn,
        "Glenn",
        {"PREC": "precinct_id"},
        [
            "OBJECTID",
            "P00C58RB_I",
            "COUNTY",
            "SUP",
            "Consolidat",
            "Shape_Leng",
            "Shape_Le_1",
            "Shape__Area",
            "Shape__Length",
        ],
    )

    glenn.head()
    return (glenn,)


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

    humboldt = alter_df(
        humboldt,
        "Humboldt",
        {"PRECINCT": "precinct_name", "Prcnct_Num": "precinct_id"},
        ["DISTRICT", "ACRES", "POP2010", "Shape_Leng", "Shape_Area"],
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

    imperial = alter_df(
        imperial,
        "Imperial",
        {"precinctid": "precinct_id", "name": "precinct_name"},
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

    inyo = alter_df(
        inyo,
        "Inyo",
        {"cons_prec": "precinct_id"},
        ["OBJECTID", "GlobalID", "Shape__Are", "Shape__Len"],
    )

    inyo.head()
    return (inyo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lake
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    lake = gpd.read_file("inputs/counties/lake/precincts.zip").to_crs(
        PROJECTED_CRS
    )

    lake = alter_df(
        lake,
        "Lake",
        rename={"PRECINCT": "precinct_id"},
        drop=["NUMBER", "Shape_Leng", "Shape_Area"],
    )

    lake.head()
    return (lake,)


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

    los_angeles = alter_df(
        los_angeles,
        "Los Angeles",
        {"Precinct": "precinct_id"},
        [
            "OBJECTID",
            "VoteByMail",
            "BallotGrou",
            "SerialNumb",
            "VBMVoters",
            "PollVoters",
            "Shape__Are",
            "Shape__Len",
        ],
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

    marin = alter_df(marin, "Marin", {"Precinct": "precinct_id"})

    marin.head()
    return (marin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mariposa
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    mariposa = gpd.read_file(
        "inputs/counties/mariposa/Voting_Precincts_2021_public_view_-5183800690768860583.zip"
    ).to_crs(PROJECTED_CRS)

    mariposa = alter_df(
        mariposa,
        "Mariposa",
        {"Name": "precinct_name", "PrecinctID": "precinct_id"},
        ["District", "Supervisor", "YEAR_CREAT"],
    )

    mariposa.head()
    return (mariposa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mendocino
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    mendocino = gpd.read_file(
        "inputs/counties/mendocino/voterprecincts.zip"
    ).to_crs(PROJECTED_CRS)

    mendocino = alter_df(
        mendocino,
        "Mendocino",
        {"NUMBER": "precinct_id", "VOTE_DIST": "precinct_name"},
    )

    mendocino.head()
    return (mendocino,)


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

    monterey = alter_df(
        monterey,
        "Monterey",
        {"precinct": "precinct_id", "precinct_n": "precinct_name"},
        ["Shape_Leng", "Shape_Area"],
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

    napa = alter_df(
        napa,
        "Napa",
        {"precinct": "precinct_id"},
        [
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

    orange = alter_df(
        orange, "Orange", {"Precinct": "precinct_id"}, ["Shape_Leng", "Shape_Area"]
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

    sacramento = alter_df(
        sacramento,
        "Sacramento",
        {"PrecinctNo": "precinct_id", "Community": "precinct_name"},
        [
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

    san_benito = alter_df(
        san_benito,
        "San Benito",
        {"PrecinctID": "precinct_id", "Name": "precinct_name"},
        [
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

    san_bernardino = alter_df(
        san_bernardino,
        "San Bernardino",
        {"PRECINCTID": "precinct_id", "ABRV_NAME": "precinct_name"},
        [
            "OBJECTID",
            "PRECINCT",
            "PRECINCT_N",
            "POLLID",
            "PORTION",
            "PRCNCT_PRT",
            "Shape__Are",
            "Shape__Len",
        ],
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

    san_diego = alter_df(
        san_diego,
        "San Diego",
        {"consnum": "precinct_id", "consname": "precinct_name"},
        [
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

    san_francisco = alter_df(
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
    ## San Joaquin
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_joaquin = gpd.read_file(
        "inputs/counties/san joaquin/Precincts_2025.json"
    ).to_crs(PROJECTED_CRS)

    san_joaquin = alter_df(
        san_joaquin,
        "San Joaquin",
        {"PRECINCT": "precinct_id"},
        [
            "OBJECTID_1",
            "OBJECTID",
            "PERIMETER",
            "Sub_ID_00",
            "GlobalID",
            "Shape__Area",
            "Area",
            "Shape__Length",
        ],
    )

    san_joaquin.head(200)
    return (san_joaquin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Luis Obispo
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_luis_obispo = gpd.read_file(
        "inputs/counties/san luis obispo/Voter_Precincts_-_2023.zip"
    ).to_crs(PROJECTED_CRS)

    san_luis_obispo = alter_df(
        san_luis_obispo,
        "San Luis Obispo",
        {"PrecinctID": "precinct_id", "PrecinctFu": "precinct_name"},
        ["OBJECTID", "PrecinctPo", "ShapeSTAre", "ShapeSTLen"],
    )

    san_luis_obispo.head()
    return (san_luis_obispo,)


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


    san_mateo = alter_df(
        san_mateo, "San Mateo", {"PrecinctID": "precinct_id"}, ["OBJECTID"]
    )

    san_mateo.head()
    return (san_mateo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Barbara
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    santa_barbara = gpd.read_file(
        "inputs/counties/santa barbara/PrecinctsAug2025.json"
    ).to_crs(PROJECTED_CRS)

    santa_barbara = alter_df(
        santa_barbara,
        "Santa Barbara",
        {"PRECINCTID": "precinct_id", "ABRV_NAME": "precinct_name"},
        ["PRECINCT_N", "PRCNCT_PRT", "OBJECTID", "Shape__Area", "Shape__Length"],
    )

    santa_barbara.head()
    return (santa_barbara,)


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

    santa_cruz = alter_df(
        santa_cruz,
        "Santa Cruz",
        {"Precinct": "precinct_id"},
        [
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

    shasta = alter_df(
        shasta,
        "Shasta",
        {"CONS_PCTNU": "precinct_id", "PP_Name": "precinct_name"},
        [
            "OBJECTID",
            "CONS_PCTNA",
            "Mail_Only",
            "PP_ID",
            "PP_Address",
            "PP_Room",
            "Shape__Are",
            "Shape__Len",
        ],
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

    siskiyou = alter_df(
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

    solano = alter_df(
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

    sonoma = alter_df(
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

    sutter = alter_df(
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
    ## Tehama
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    tehama = gpd.read_file("inputs/counties/tehama/tehama-precincts.json").to_crs(
        PROJECTED_CRS
    )

    tehama = alter_df(
        tehama,
        "Tehema",
        {"PRECINCTID": "precinct_id", "NAME": "precinct_name"},
        ["OBJECTID"],
    )

    tehama.head()
    return (tehama,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Tulare
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    tulare = gpd.read_file("inputs/counties/tulare/tulare-precincts.json").to_crs(
        PROJECTED_CRS
    )

    tulare = alter_df(
        tulare,
        "Tulare",
        {"VotingPctID": "precinct_id"},
        [
            "OBJECTID_12",
            "OBJECTID_1",
            "OBJECTID_2",
            "OBJECTID",
            "C",
            "WARD",
            "SECTION",
            "TRA",
            "PrecNum",
            "BOS",
            "Shape_Leng",
            "Change",
            "changedPRE",
            "match",
            "Shape_Le_1",
            "Pollsite",
            "PollingSiteID",
            "BallotTypeList",
            "PrecNum1",
            "Precincts_UPDATE_LOCAL_VotingPc",
            "Shape__Area",
            "Shape__Length",
        ],
    )

    tulare.head()
    return (tulare,)


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

    tuolumne = alter_df(
        tuolumne,
        "Tuolumne",
        {"PREC_NO": "precinct_id", "PRECINCT": "precinct_name"},
        ["HomePrecin", "PropConsol"],
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

    ventura = alter_df(
        ventura,
        "Ventura",
        {"number_": "precinct_id"},
        [
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

    yolo = alter_df(
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

    yuba = alter_df(
        yuba,
        "Yuba",
        {"precinctid": "precinct_id", "name": "precinct_name"},
        [
            "facilityid",
            "pollingid",
            "GlobalID",
            "created_da",
            "last_edite",
            "precinctty",
        ],
    )

    yuba.head()
    return (yuba,)


if __name__ == "__main__":
    app.run()
