import marimo

__generated_with = "0.19.4"
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
    import re

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import pdfplumber
    return gpd, mo, pd, pdfplumber, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Merge and export
    """)
    return


@app.cell
def _(combined_reordered):
    # show the counties that are included in the workflow
    combined_reordered.plot()
    return


@app.cell
def _(
    COMBINED_OUTPUT_DRIVER,
    COMBINED_OUTPUT_PATH,
    alameda,
    amador,
    butte,
    colusa,
    contra_costa,
    fresno,
    glenn,
    humboldt,
    imperial,
    inyo,
    kern,
    lake,
    los_angeles,
    madera,
    marin,
    mariposa,
    mendocino,
    merced,
    modoc,
    mono,
    monterey,
    napa,
    nevada,
    orange,
    pd,
    placer,
    riverside,
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
    sierra,
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
            amador,
            butte,
            colusa,
            contra_costa,
            fresno,
            glenn,
            humboldt,
            imperial,
            inyo,
            kern,
            lake,
            los_angeles,
            madera,
            marin,
            mariposa,
            mendocino,
            merced,
            modoc,
            mono,
            monterey,
            napa,
            nevada,
            orange,
            placer,
            riverside,
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
            sierra,
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

    dupes = check_duplicates(combined_reordered)

    # save the reordered results to a file at COMBINED_OUTPUT_PATH
    combined_reordered.to_file(COMBINED_OUTPUT_PATH, driver=COMBINED_OUTPUT_DRIVER)
    print(f"Saved combined precincts to {COMBINED_OUTPUT_PATH}")
    return (combined_reordered,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.function
def check_duplicates(df, columns_to_check=["county", "precinct_id"]):
    """
    Check for duplicate entries in the DataFrame based on specified columns.
    If duplicates are found, print a descriptive message listing the counties with duplicate IDs.
    Returns the duplicate rows sorted by the specified columns if possible; otherwise, returns unsorted duplicates.
    Parameters:
        df (pd.DataFrame): The input DataFrame to check for duplicates.
        columns_to_check (list): List of column names to identify duplicates. Defaults to ["county", "precinct_id"].

    Returns:
        pd.DataFrame or bool: DataFrame of duplicate rows if found (sorted if possible), otherwise None.
    """
    # Identify duplicate rows based on "county" and "precinct_id"
    duplicates = df[df.duplicated(subset=columns_to_check, keep=False)]

    if not duplicates.empty:
        # Get the list of counties that have duplicate precinct IDs
        duplicate_counties = duplicates["county"].unique().tolist()
        print(
            f"Duplicate precinct IDs found in the following counties: {', '.join(sorted(duplicate_counties))}"
        )
        # Attempt to sort by precinct_id, but handle unsortable cases (e.g., mixed str/float)
        try:
            return duplicates.sort_values(columns_to_check)
        except TypeError:
            print(
                "Sorting by (county, precinct_id) threw a type error, returning unsorted dupe data"
            )
            return duplicates  # Return unsorted if sorting fails
    else:
        return None


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
    # Extract and transform by county

    Each county's indepedent election adminstrator produces an election precincts map that needs to read in and transformed into our standardized format
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    # read in the source file with geopandas and reproject to PROJECTED_CRS
    alameda = gpd.read_file(
        "inputs/counties/alameda/precincts/Consolidated_Precincts_-_November_4%2C_2025_Statewide_Special_Election.geojson"
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
    ## Amador
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    amador = gpd.read_file(
        "inputs/counties/amador/precincts/VotingDistricts_2021_Updated3-18-22.zip"
    ).to_crs(PROJECTED_CRS)

    # the spatial data is more granular than the results so we should combine
    # features based on the value in the "CP" column
    # spatial data is likely voting precincts, and the results data is reported using Consolidated Precincts.
    # We are (safely) assuming "CP" is consolidated precincts and dissolving the data appropriately
    amador = amador.dissolve(by="CP").reset_index()
    amador = alter_df(
        amador,
        "Amador",
        {"CP": "precinct_id"},
        [
            "PRECINCT",
            "LOCATION",
            "SUPDIST",
            "POLLPLACE",
            "POLLADDR",
            "POLLCITY",
            "POLLSTATE",
            "POLLZIP",
            "SHAPE_Leng",
            "SHAPE_Area",
        ],
    )

    amador.head()
    return (amador,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Butte
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    butte = gpd.read_file(
        "inputs/counties/butte/precincts/Butte Precincts 2025.kmz"
    ).to_crs(PROJECTED_CRS)

    butte = alter_df(
        butte,
        "Butte",
        {"Name": "precinct_name", "id": "precinct_id"},
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
        "inputs/counties/colusa/precincts/Voting Precincts - 2020.shp"
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

    Precincts with zero registered voters are filtered out, because these precincts are not included in the official results data. [Read more issue #47](https://github.com/CalMatters/data-prop50-results/issues/47)
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    contra_costa = gpd.read_file(
        "inputs/counties/contra_costa/precincts/PrecinctSet_PDMJ017.json"
    ).to_crs(PROJECTED_CRS)

    has_voters = contra_costa["iZeroRegistrationPct"] != 1
    contra_costa = contra_costa[has_voters].copy()

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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Extract crosswalk data to convert the geographic file to match the expected precinct in the results data
    """)
    return


@app.cell
def _():
    def _strip_lang_signifier_from_registration_precinct_id(precinct_id):
        # some precincts have a suffix such as "_H" or "_L"
        # which signify the major language in that precinct
        # we can remove that to complete our merge
        suffixes_to_remove = [
            "_C",
            "_H",
            "_L",
            "_P",
            "_T",
            "_V",
            "_KH",
            "_KO",
            "KO",
        ]
        for suffix in suffixes_to_remove:
            precinct_id = precinct_id.replace(suffix, "")
        return precinct_id


    def extract_fresno_crosswalk_pdf_page(
        page, last_seen_results_precinct_id=None
    ):
        """
        Extracts the crosswalk from PDF pages the crosswalk connects "Regular Precincts" which are used for voter registration (and therefore called registration_precincts in this code) to "Voting Precincts" which are used for results (and therefore called results_precincts in this code)
         Parameters:
             page (pdfplumber.Page): The PDF page to extract

         Returns:
             list: A list of objects, each with "registration_precinct" and "results_precinct"
             str|none: latest value for last_seen_results_precinct_id
        """

        # the shapefile from the county only has "Regular Precincts"
        # but the results file only has "Voting Precincts"

        # create a list to store the page's data in
        page_rows = []

        # get all of the text from the page and split it into lines
        page_text = page.extract_text()
        page_lines = page_text.splitlines()

        # define constants for line split counts
        REGULAR_LINE_SPLIT_COUNT = 4
        LINE_WITH_RESULTS_ID_SPLIT_COUNT = 7

        # define constants for index positions
        REGISTRATION_PRECINCT_INDEX_REGULAR = 2
        REGISTRATION_PRECINCT_INDEX_WITH_RESULTS = 5
        RESULTS_PRECINCT_ID_INDEX = 0

        def _extract_precinct_from_page_line(line, last_seen_id):
            line_split = line.split(" ")
            line_split_count = len(line_split)
            row = None
            # regular data lines have 4 elements after the split
            if line_split_count == REGULAR_LINE_SPLIT_COUNT:
                row = {
                    "registration_precinct": _strip_lang_signifier_from_registration_precinct_id(
                        line_split[REGISTRATION_PRECINCT_INDEX_REGULAR]
                    ),
                    "results_precinct": last_seen_id,
                }
                return row, last_seen_id
            # if the data has 7 elements after the split that means it has
            # the results precinct id
            elif line_split_count == LINE_WITH_RESULTS_ID_SPLIT_COUNT:
                new_last_seen_id = "%s" % line_split[RESULTS_PRECINCT_ID_INDEX]
                row = {
                    "registration_precinct": _strip_lang_signifier_from_registration_precinct_id(
                        line_split[REGISTRATION_PRECINCT_INDEX_WITH_RESULTS]
                    ),
                    "results_precinct": new_last_seen_id,
                }
                return row, new_last_seen_id
            return None, last_seen_id

        # go through each line and split it on white space
        for line in page_lines:
            row, last_seen_results_precinct_id = _extract_precinct_from_page_line(
                line, last_seen_results_precinct_id
            )
            if row is not None:
                page_rows.append(row)

        return page_rows, last_seen_results_precinct_id
    return (extract_fresno_crosswalk_pdf_page,)


@app.cell
def _(extract_fresno_crosswalk_pdf_page, pd, pdfplumber):
    last_seen_results_precinct_id = None
    # create a variable to store all of the extracted row
    fresno_page_rows = []

    # Define bounding box coordinates for left and right sections
    _LEFT_CROP_BOUNDS = [15, 30, 388, 580]
    _RIGHT_CROP_BOUNDS = [390, 30, 760, 580]

    _crosswalk_pdf_path = (
        "inputs/counties/fresno/ewmr008_votabsregpctxref-2025.pdf"
    )

    with pdfplumber.open(_crosswalk_pdf_path) as fresno_crosswalk_pdf:
        for fresno_crosswalk_page in fresno_crosswalk_pdf.pages:
            # the source pdf has a table that is split into two halves

            # crop the page into two sections
            left_page = fresno_crosswalk_page.crop(bbox=_LEFT_CROP_BOUNDS)
            right_page = fresno_crosswalk_page.crop(bbox=_RIGHT_CROP_BOUNDS)

            # extract the text from each section
            left_page_extracted, last_seen_results_precinct_id = (
                extract_fresno_crosswalk_pdf_page(
                    left_page, last_seen_results_precinct_id
                )
            )
            right_page_extracted, last_seen_results_precinct_id = (
                extract_fresno_crosswalk_pdf_page(
                    right_page, last_seen_results_precinct_id
                )
            )

            # and add the results of both to our list for all pages
            fresno_page_rows.extend(left_page_extracted)
            fresno_page_rows.extend(right_page_extracted)

    # turn the resulting list into a dataframe
    fresno_page_rows = pd.DataFrame(fresno_page_rows)
    return (fresno_page_rows,)


@app.cell
def _(PROJECTED_CRS, fresno_page_rows, gpd):
    # use fresno registration precicnts
    fresno = gpd.read_file(
        "inputs/counties/fresno/precincts/ELECTIONS_PRECINCT_VW.zip"
    ).to_crs(PROJECTED_CRS)

    # create a column to merge on
    fresno["registration_precinct"] = fresno["EIMS_PRCT"]

    # merge precincts with crosswalk data
    fresno_merged = fresno.merge(
        fresno_page_rows,
        on="registration_precinct",
        validate="m:1",
        how="left",
        indicator=True,
    )

    # check for records that did not match
    unmatched = fresno_merged[fresno_merged["_merge"] == "left_only"]
    if len(unmatched) > 0:
        print(
            f"Warning: {len(unmatched)} precincts did not match in the crosswalk data."
        )
        # display a few examples
        debug_output_path = "debug/fresno_unmatched_precincts.csv"
        unmatched[["registration_precinct", "_merge"]].to_csv(
            debug_output_path, index=False
        )
        print(f"Unmatched precincts exported to {debug_output_path}")

    # drop the indicator column used for debugging
    fresno_merged = fresno_merged.drop(columns=["_merge"])

    # proceed with the merged data
    fresno = fresno_merged

    # dissolve on the results_precinct column
    fresno = fresno.dissolve("results_precinct")

    # reset the index so we can use the column
    fresno = fresno.reset_index()

    # rename and drop columns
    fresno = alter_df(
        fresno,
        "Fresno",
        {"results_precinct": "precinct_id"},
        [
            "OBJECTID",
            "AREA_",
            "PERIMETER",
            "PRCT_",
            "PRCT_ID",
            "NO_PRCT",
            "EIMS_PRCT",
            "NO_PRCT_RT",
            "NO_PRCT_SU",
            "Shape__Are",
            "Shape__Len",
            "registration_precinct",
        ],
    )

    fresno
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
        gpd.read_file("inputs/counties/glenn/precincts/Precincts_9_3_2.json")
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
        "inputs/counties/humboldt/precincts/precincts17sp_202507111714287445.zip"
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
        "inputs/counties/imperial/precincts/Voting_Precincts.shp"
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
    inyo = gpd.read_file("inputs/counties/inyo/precincts/consolidated.zip").to_crs(
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
    ## Kern
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd, pd):
    # the kern county crosswalk file is two columns smashed together
    # so we read them into two different data frames to start
    kern_1 = (
        pd.read_excel(
            "inputs/counties/kern/precincts/2025 Statewide Special Election.xls",
            usecols="B:Q",  # these columns are the first half of the data
            skiprows=6,  # skip the header rows
        )
        .truncate(
            after=5690  # the rows after are relevant to cities in the county
        )
        .drop(
            columns=[  # drop columns we don't need
                "Mail\nBallot ",
                "Unnamed: 2",
                "Unnamed: 3",
                "Unnamed: 4",
                "Unnamed: 5",
                "Unnamed: 6",
                "Unnamed: 8",
                "Unnamed: 9",
                "Unnamed: 11",
                "Unnamed: 12",
                "Unnamed: 13",
                "Unnamed: 15",
                "Ballot \nType",
            ]
        )
    )
    kern_1 = kern_1.rename(
        columns={
            "\nVoting Precinct": "voting_precinct",
            "\nRegular Precinct": "regular_precinct",
            "\nRegistration": "registration",
        }
    )
    kern_1["voting_precinct"] = kern_1["voting_precinct"].ffill()
    kern_1_has_voters = kern_1["registration"].notnull()
    kern_1 = kern_1[kern_1_has_voters].copy()

    kern_1["voting_precinct"] = kern_1["voting_precinct"].str.split(
        " ", expand=True
    )[0]
    kern_1 = kern_1.reset_index(drop=True)

    kern_2 = (
        pd.read_excel(
            "inputs/counties/kern/precincts/2025 Statewide Special Election.xls",
            usecols="U:AC",
            skiprows=6,
        )
        .truncate(
            after=5655  # the rows after are relevant to cities in the county
        )
        .drop(
            columns=[
                "Unnamed: 21",
                "Mail\nBallot",
                "Unnamed: 24",
                "Unnamed: 25",
                "Unnamed: 26",
                "Ballot \nType.1",
            ]
        )
    )
    kern_2 = kern_2.rename(
        columns={
            "\nVoting Precinct.1": "voting_precinct",
            "\nRegular Precinct.1": "regular_precinct",
            "\nRegistration.1": "registration",
        }
    )

    kern_2["voting_precinct"] = kern_2["voting_precinct"].ffill()
    kern_2_has_voters = kern_2["registration"].notnull()
    kern_2 = kern_2[kern_2_has_voters].copy()

    kern_2["voting_precinct"] = kern_2["voting_precinct"].str.split(
        " ", expand=True
    )[0]
    kern_2 = kern_2.reset_index(drop=True)

    # and then combine both dataframes to get a single crosswalk dataframe
    kern_crosswalk = pd.concat([kern_1, kern_2]).reset_index(drop=True)

    # replace multiple spaces with one in preparation for the merge
    kern_crosswalk["regular_precinct"] = kern_crosswalk[
        "regular_precinct"
    ].str.replace("  ", " ")

    # read in the shapefile
    kern = gpd.read_file(
        "inputs/counties/kern/precincts/remediainquiryelectionprecinctgeographicfiles/2025 Precincts.shp"
    ).to_crs(PROJECTED_CRS)

    # create a key for merging with the crosswalk
    kern["regular_precinct"] = (
        kern["PrecintID"].astype(str) + " " + kern["Layer"].astype(str)
    )
    # which includes replacing multiple spaces with a single space
    kern["regular_precinct"] = kern["regular_precinct"].str.replace(" +", "")

    # merge the two together
    kern = pd.merge(
        kern, kern_crosswalk, on="regular_precinct", how="inner", validate="m:1"
    )

    # consolidate registration precincts into voting precincts and add data attributes together
    # (we only care about registration)
    kern = kern.dissolve(by="voting_precinct", aggfunc="sum").reset_index()

    # cleanup column names to match our schema

    kern = alter_df(
        kern,
        "Kern",
        {"voting_precinct": "precinct_id", "Layer": "precinct_name"},
        [
            "OBJECTID_1",
            "OBJECTID",
            "Shape_Leng",
            "Shape_Le_1",
            "Latitude",
            "Longitude",
            "PrecintID",
            "regular_precinct",
        ],
    )

    kern
    return (kern,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lake
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    lake = gpd.read_file("inputs/counties/lake/precincts/precincts.zip").to_crs(
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
        "inputs/counties/los_angeles/precincts/Registrar_Recorder_Election_Precincts_.shp"
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
    ## Madera
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    madera = gpd.read_file(
        "inputs/counties/madera/precincts/VotingPrecincts_2025SpecialElection.zip"
    ).to_crs(PROJECTED_CRS)

    madera = alter_df(
        madera,
        "Madera",
        {"VotingPrec": "precinct_id"},
        ["CreatedBy", "CreatedDat", "ModifyBy", "ModifyDate"],
    )

    madera.head()
    return (madera,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Marin
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    marin = gpd.read_file(
        "inputs/counties/marin/precincts/CONSOLIDATED_PRECINCT.zip"
    ).to_crs(PROJECTED_CRS)

    marin = alter_df(
        marin,
        "Marin",
        {"Consolidat": "precinct_id"},
        [
            "ElectionDa",
            "SubPrecinc",
            "SubPreci_1",
            "ElectionTi",
            "GlobalID",
            "OBJECTID",
            "Shape__Are",
            "Shape__Len",
        ],
    )

    marin["precinct_id"] = marin["precinct_id"].str.replace("C", "")

    marin
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
        "inputs/counties/mariposa/precincts/Voting_Precincts_2021_public_view_-5183800690768860583.zip"
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
        "inputs/counties/mendocino/precincts/voterprecincts.zip"
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
    ## Merced
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    merced = gpd.read_file(
        "inputs/counties/merced/Merced County Pct Shapefile/MercedCountyPrecincts.shp"
    ).to_crs(PROJECTED_CRS)

    merced = alter_df(
        merced,
        "Merced",
        {"REF_NUM_28": "precinct_id", "PCT_NAME_1": "precinct_name"},
        ["Ballot_Lin", "Shape_Leng", "Shape_Area"],
    )

    merced["county"] = "Merced"

    merced.head(None)
    return (merced,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Modoc
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    modoc = gpd.read_file(
        "inputs/counties/modoc/precincts/Modoc_Voter_Precincts_2024.json"
    ).to_crs(PROJECTED_CRS)

    modoc = alter_df(
        modoc,
        "Modoc",
        {"Name": "precinct_name", "Precinct_ID": "precinct_id"},
        ["OBJECTID", "Id", "Disclaimer", "Shape__Area", "Shape__Length"],
    )

    modoc.head()
    return (modoc,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mono
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    mono = gpd.read_file(
        "inputs/counties/mono/precincts/Voting_Precincts.zip"
    ).to_crs(PROJECTED_CRS)

    mono = alter_df(
        mono,
        "Mono",
        {"VotingPrct": "precinct_id"},
        [
            "OBJECTID",
            "SupDist",
            "Supervisor",
            "PollingPla",
            "PollingAdd",
            "PollingCom",
            "PollingZip",
            "last_edite",
            "Number",
            "ShapeSTAre",
            "ShapeSTLen",
        ],
    )

    mono.head()
    return (mono,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Monterey
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    monterey = gpd.read_file(
        "inputs/counties/monterey/precincts/2024-11-05 Precincts.zip"
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
    napa = gpd.read_file("inputs/counties/napa/precincts/Precincts.zip").to_crs(
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
    ## Nevada
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    nevada = gpd.read_file(
        "inputs/counties/nevada/precincts/Voter Precincts.json"
    ).to_crs(PROJECTED_CRS)

    nevada = alter_df(
        nevada,
        "Nevada",
        {"PRECINCT": "precinct_id", "PREC_NAME": "precinct_name"},
        ["GlobalID", "Shape__Area", "Shape__Length", "EditDate", "CONS_PREC"],
    )

    nevada.head()
    return (nevada,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orange
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    orange = gpd.read_file(
        "inputs/counties/orange/precincts/OC_Precinct_2024GE.zip"
    ).to_crs(PROJECTED_CRS)

    orange = alter_df(
        orange, "Orange", {"Precinct": "precinct_id"}, ["Shape_Leng", "Shape_Area"]
    )

    orange.head()
    return (orange,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Placer
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    placer = gpd.read_file(
        "inputs/counties/placer/precincts/PlacerCo_VotingPrecincts_2025Spec/PlacerCo_VotingPrecincts_2025Spec.shp"
    ).to_crs(PROJECTED_CRS)

    placer = alter_df(
        placer,
        "Placer",
        {"VOTINGPREC": "precinct_id"},
        ["SHAPE_Leng", "SHAPE_Area"],
    )

    placer.head()
    return (placer,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Riverside
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    riverside = gpd.read_file(
        "inputs/counties/riverside/precincts/Final Voting Precincts.zip"
    ).to_crs(PROJECTED_CRS)

    riverside = alter_df(
        riverside,
        "Riverside",
        {"PRIMARY_NE": "precinct_id"},
        [
            "SUM_lTotal",
            "sVotingPre",
            "SUM_lTot_1",
            "VPMapping",
            "sVotingP_1",
            "iMailBallo",
            "Shape_Leng",
            "Shape_Area",
            "iBalType",
            "iMailBal_1",
            "Shape_Le_1",
            "Shape_Ar_1",
        ],
    )

    riverside.head()
    return (riverside,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sacramento
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sacramento = gpd.read_file(
        "inputs/counties/sacramento/precincts/ConsolidatedPrecincts_-8549929174186228288.zip"
    ).to_crs(PROJECTED_CRS)

    sacramento = alter_df(sacramento, "Sacramento", {"VPrecinct": "precinct_id"})

    sacramento.head()
    return (sacramento,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Benito

    A dissolve operation is executed to join all the records with `precinct_id` `0`. These are associated with unpopulated areas such as water treatment plant, farmland, parks, open fields. [Read more issue #32](https://github.com/CalMatters/data-prop50-results/issues/32)
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    san_benito = gpd.read_file(
        "inputs/counties/san_benito/precincts/San_Benito_Base_Precincts_2025.zip"
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

    assert len(check_duplicates(san_benito)) > 0, (
        "Expected duplicates but found none"
    )
    unpopulated_precinct_count = (san_benito["precinct_id"] == "0").sum()
    _predissolve_precinct_count = len(san_benito)
    san_benito = san_benito.dissolve("precinct_id", as_index=False)
    expected_count = _predissolve_precinct_count - (unpopulated_precinct_count - 1)
    actual_count = len(san_benito)
    assert actual_count == expected_count, (
        f"San Benito dissolve assertion failed: expected {expected_count} precincts after dissolve, but got {actual_count}."
    )
    assert check_duplicates(san_benito) is None, (
        "Expected no duplicate entires after dissolve operations but duplicate check returned True"
    )
    print("San Benito duplicate resolved using dissolve operation")

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
        "inputs/counties/san_bernardino/precincts/ROV_Precincts.zip"
    ).to_crs(PROJECTED_CRS)

    san_bernardino = alter_df(
        san_bernardino,
        "San Bernardino",
        {"ABRV_NAME": "precinct_id"},
        [
            "OBJECTID",
            "PRECINCT",
            "PRECINCTID",
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
        "inputs/counties/san_diego/precincts/Election_Precinct_2025_11_04.json"
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
        "inputs/counties/san_francisco/precincts/Election Precincts - Current, Defined 2022_20251120.zip"
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
        "inputs/counties/san_joaquin/precincts/Precincts_2025.json"
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
        "inputs/counties/san_luis_obispo/precincts/Voter_Precincts_-_2023.zip"
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
def _(PROJECTED_CRS, gpd, pd, pdfplumber):
    san_mateo_crosswalk_rows = []

    _sm_crosswalk_pdf_path = (
        "inputs/counties/san_mateo/50_PrecinctConsolidations Nov2025.pdf"
    )

    with pdfplumber.open(_sm_crosswalk_pdf_path) as _sm_pdf:
        for _sm_page in _sm_pdf.pages:
            _sm_table = _sm_page.extract_tables()
            for _sm_table_row in _sm_table[0]:
                if _sm_table_row[0] != "Voting\nPrecinct":
                    _sm_precinct_id = _sm_table_row[0]
                    for _sm_cell in _sm_table_row[1:]:
                        san_mateo_crosswalk_rows.append(
                            {
                                "consolidated_precinct": _sm_precinct_id,
                                "regular_precinct": _sm_cell
                                if _sm_cell != ""
                                else _sm_precinct_id,
                            }
                        )

    san_mateo_crosswalk_rows = pd.DataFrame(
        san_mateo_crosswalk_rows
    ).drop_duplicates()

    san_mateo = gpd.read_file(
        "inputs/counties/san_mateo/precincts/ELECTION_PRECINCTS.shp"
    ).to_crs(PROJECTED_CRS)

    san_mateo_with_crosswalk = pd.merge(
        san_mateo,
        san_mateo_crosswalk_rows,
        left_on="PrecinctID",
        right_on="regular_precinct",
    )

    san_mateo = san_mateo_with_crosswalk.dissolve(
        "consolidated_precinct"
    ).reset_index()

    san_mateo = alter_df(
        san_mateo,
        "San Mateo",
        {"consolidated_precinct": "precinct_id"},
        ["OBJECTID", "PrecinctID", "regular_precinct"],
    )

    san_mateo
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
        "inputs/counties/santa_barbara/precincts/PrecinctsAug2025.json"
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
        "inputs/counties/santa_cruz/precincts/Precincts_5962167425846516299.zip"
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
        "inputs/counties/shasta/precincts/Consolidated_Precincts.shp"
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
    ## Sierra
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sierra = gpd.read_file(
        "inputs/counties/sierra/precincts/Sierra_County_2021_Voter_Jurisdiction_Data.zip",
        layer="Sierra_County_Voter_Precincts_2021",
    ).to_crs(PROJECTED_CRS)

    sierra = alter_df(
        sierra, "Sierra", {"PRECINCT": "precinct_id", "NAME": "precinct_name"}
    )

    sierra.head()
    return (sierra,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Siskiyou
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    siskiyou = gpd.read_file(
        "inputs/counties/siskiyou/precincts/Election_Precincts.zip"
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
    solano = gpd.read_file(
        "inputs/counties/solano/precincts/Current_Precincts.json"
    ).to_crs(PROJECTED_CRS)

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
        "inputs/counties/sonoma/precincts/ROVPublic_Precincts.json"
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

    Sutter requires a dissolve operation to resolve an issue with a data artifact. [Read more issue #35](https://github.com/CalMatters/data-prop50-results/issues/35)
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    sutter = gpd.read_file(
        "inputs/counties/sutter/precincts/Elections_Precincts.zip"
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

    assert len(check_duplicates(sutter)) > 1, "Expected duplicates but found none"
    _predissolve_precinct_count = len(sutter)
    sutter = sutter.dissolve(by="precinct_id", as_index=False)
    assert (_predissolve_precinct_count - 1) == len(sutter), (
        f"Expected {_predissolve_precinct_count - 1} precincts after dissolve, but got {len(sutter)}"
    )
    assert check_duplicates(sutter) is None, (
        "Expected no duplicate entires after dissolve operations but duplicate check returned True"
    )
    print("Sutter duplicate resolved using dissolve operation")


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
    tehama = gpd.read_file(
        "inputs/counties/tehama/precincts/tehama-precincts.json"
    ).to_crs(PROJECTED_CRS)

    tehama = alter_df(
        tehama,
        "Tehema",
        {"PRECINCTID": "precinct_id", "NAME": "precinct_name"},
        ["OBJECTID"],
    )

    tehama.head()
    return (tehama,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tulare
    """)
    return


@app.cell
def _(re):
    def extract_tulare_crosswalk_pdf_page(
        page, last_seen_results_precinct_id=None
    ):
        """
        Extracts the crosswalk from PDF pages the crosswalk connects "Regular Precincts" which are used for voter registration (and therefore called registration_precincts in this code) to "Voting Precincts" which are used for results (and therefore called results_precincts in this code)
         Parameters:
             page (pdfplumber.Page): The PDF page to extract

         Returns:
             list: A list of objects, each with "registration_precinct" and "results_precinct"
        """
        # create a list to store the page's data in
        page_rows = []

        # get all of the text from the page and split it into lines
        page_text = page.extract_text()
        page_lines = page_text.splitlines()

        # define constants for index positions
        REGISTRATION_PRECINCT_INDEX = 2
        last_seen_id = None

        def _extract_precinct_from_page_line(line, last_seen_id):
            row = {
                "registration_precinct": None,
                "results_precinct": None,
            }

            # the lines with voting precincts (which are like sections)
            # start with a seven digit number
            if re.match(r"^\d{7}", line):
                last_seen_id = line.split(" -")[0]
                row["results_precinct"] = last_seen_id
            else:
                row["results_precinct"] = last_seen_id

            # if the row starts with a "1 " then it contains the
            # registration precinct
            if re.match(r"^1 ", line):
                line_split = line.split(" ")
                regular_precinct = line_split[REGISTRATION_PRECINCT_INDEX].strip()
                if re.match(r"^\d{7}$", regular_precinct):
                    row["registration_precinct"] = regular_precinct
                else:
                    breakpoint()
            else:
                return None, last_seen_id

            return row, last_seen_id

        # go through each line and split it on white space
        for line in page_lines:
            row, last_seen_id = _extract_precinct_from_page_line(
                line, last_seen_id
            )
            if row is not None:
                page_rows.append(row)

        return page_rows
    return (extract_tulare_crosswalk_pdf_page,)


@app.cell
def _(PROJECTED_CRS, extract_tulare_crosswalk_pdf_page, gpd, pd, pdfplumber):
    TULARE_CROSSWALK_PDF_PATH = "inputs/counties/tulare/tularecounty_2025novspec_votabsregpctxrefdetail.pdf"
    TULARE_PRECINCT_PATH = "inputs/counties/tulare/precincts/tulare-precincts.json"

    # create a variable to store all of the extracted rows
    tulare_crosswalk = []

    with pdfplumber.open(TULARE_CROSSWALK_PDF_PATH) as tulare_crosswalk_pdf:
        for page in tulare_crosswalk_pdf.pages:
            # extract the text from each page
            page_extracted = extract_tulare_crosswalk_pdf_page(page)

            # and add the results to our list
            tulare_crosswalk.extend(page_extracted)

    # turn the resulting list into a dataframe
    tulare_crosswalk = pd.DataFrame(tulare_crosswalk)

    tulare = gpd.read_file(TULARE_PRECINCT_PATH).to_crs(PROJECTED_CRS)

    # make sure the column we'll join on is a string
    tulare["PrecNum1"] = tulare["PrecNum1"].astype(str)

    # merge the shapefile and the crosswalk file data
    tulare = pd.merge(
        tulare,
        tulare_crosswalk,
        left_on="PrecNum1",
        right_on="registration_precinct",
        how="inner",
    )

    # and change the resulting dataframe to match our schema
    tulare = alter_df(
        tulare,
        "Tulare",
        {"results_precinct": "precinct_id"},
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
            "PrecNum1",
            "BOS",
            "Shape_Leng",
            "Change",
            "changedPRE",
            "match",
            "Shape_Le_1",
            "Pollsite",
            "PollingSiteID",
            "BallotTypeList",
            "VotingPctID",
            "Precincts_UPDATE_LOCAL_VotingPc",
            "Shape__Area",
            "Shape__Length",
            "registration_precinct",
        ],
    ).reset_index(drop=True)

    # only use features with valid geometry
    tulare = tulare[tulare.geometry.is_valid]

    # dissolve all precincts with the same precinct_id
    tulare = tulare.dissolve("precinct_id").reset_index()

    tulare
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
        "inputs/counties/tuolumne/precincts/TC_VotingPrecincts_Sept2022/TuolumneCounty_VotingPrecincts_consolidationNov2022.shp"
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
        "inputs/counties/ventura/precincts/Election_Precinct.zip"
    ).to_crs(PROJECTED_CRS)

    ventura = alter_df(
        ventura,
        "Ventura",
        {"electid": "precinct_id", "number_": "precinct_name"},
        [
            "objectid",
            "gr_cr_date",
            "gr_co_date",
            "acres",
            "created_da",
            "last_edite",
            "oldprecinc",
            "globalid",
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
        "inputs/counties/yolo/precincts/PrecinctsConsolidated_20250904.zip"
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

    yolo
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
        "inputs/counties/yuba/precincts/YubaCountyCA_2024_03_21_001/VotingPrecincts.shp"
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
