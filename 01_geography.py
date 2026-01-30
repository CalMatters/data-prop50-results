import marimo

__generated_with = "0.19.5"
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
    santa_clara,
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
            santa_clara,
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
def alter_df(df, county, rename=None, drop=None):
    """
    Alter the dataframe, in place, by renaming and dropping columns
    """
    df["county"] = county
    if rename:
        df = df.rename(
            columns=rename,
        )
    if drop:
        df = df.drop(
            labels=drop,
            axis="columns",
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
    _GIS_FP = "inputs/counties/alameda/precincts/Consolidated_Precincts_-_November_4%2C_2025_Statewide_Special_Election.geojson"
    alameda = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    # use alter_df to clean, renaming some columns and dropping others
    alameda = alter_df(
        df=alameda,
        county="Alameda",
        rename={"Precinct_ID": "precinct_id"},
        drop=[
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
    _GIS_FP = (
        "inputs/counties/amador/precincts/VotingDistricts_2021_Updated3-18-22.zip"
    )
    amador = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    # the spatial data is more granular than the results so we should combine
    # features based on the value in the "CP" column
    # spatial data is likely voting precincts, and the results data is reported using Consolidated Precincts.
    # We are (safely) assuming "CP" is consolidated precincts and dissolving the data appropriately
    amador = amador.dissolve(by="CP").reset_index()
    amador = alter_df(
        df=amador,
        county="Amador",
        rename={"CP": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/butte/precincts/Butte Precincts 2025.kmz"
    butte = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    butte = alter_df(
        df=butte,
        county="Butte",
        rename={"Name": "precinct_name", "id": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/colusa/precincts/Voting Precincts - 2020.shp"
    colusa = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    colusa = alter_df(
        df=colusa,
        county="Colusa",
        rename={"PRECINCTNU": "precinct_id", "PRECINCT": "precinct_name"},
        drop=["DISTRICT"],
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
    _GIS_FP = "inputs/counties/contra_costa/precincts/PrecinctSet_PDMJ017.json"
    _ZERO_REGISTRATION_FLAG = 1
    contra_costa = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    has_voters = contra_costa["iZeroRegistrationPct"] != _ZERO_REGISTRATION_FLAG
    contra_costa = contra_costa[has_voters].copy()

    contra_costa = alter_df(
        df=contra_costa,
        county="Contra Costa",
        rename={"sPrecinctID": "precinct_id", "szPrecinctName": "precinct_name"},
        drop=[
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

    _CROSSWALK_PDF_PATH = (
        "inputs/counties/fresno/ewmr008_votabsregpctxref-2025.pdf"
    )

    with pdfplumber.open(_CROSSWALK_PDF_PATH) as fresno_crosswalk_pdf:
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
    _GIS_FP = "inputs/counties/fresno/precincts/ELECTIONS_PRECINCT_VW.zip"
    fresno = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

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
    if len(unmatched) != 0:
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
        df=fresno,
        county="Fresno",
        rename={"results_precinct": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/glenn/precincts/Precincts_9_3_2.json"
    glenn = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    glenn = alter_df(
        df=glenn,
        county="Glenn",
        rename={"PREC": "precinct_id"},
        drop=[
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
    _GIS_FP = (
        "inputs/counties/humboldt/precincts/precincts17sp_202507111714287445.zip"
    )
    humboldt = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    humboldt = alter_df(
        df=humboldt,
        county="Humboldt",
        rename={"PRECINCT": "precinct_name", "Prcnct_Num": "precinct_id"},
        drop=["DISTRICT", "ACRES", "POP2010", "Shape_Leng", "Shape_Area"],
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
    _GIS_FP = "inputs/counties/imperial/precincts/Voting_Precincts.shp"
    imperial = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    imperial = alter_df(
        df=imperial,
        county="Imperial",
        rename={"precinctid": "precinct_id", "name": "precinct_name"},
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
    _GIS_FP = "inputs/counties/inyo/precincts/consolidated.zip"
    inyo = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    inyo = alter_df(
        df=inyo,
        county="Inyo",
        rename={"cons_prec": "precinct_id"},
        drop=["OBJECTID", "GlobalID", "Shape__Are", "Shape__Len"],
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
def _(pd):
    def process_kern_crosswalk_section(
        file_path,
        usecols,
        skiprows,
        truncate_after,
        columns_to_drop,
        rename_mapping,
    ):
        """
        Process a single section of the Kern county crosswalk Excel file.

        Parameters:
            file_path: Path to the Excel file
            usecols: Column range to read (e.g., "B:Q")
            skiprows: Number of header rows to skip
            truncate_after: Row index to truncate after
            columns_to_drop: List of column names to drop
            rename_mapping: Dictionary mapping old column names to new ones
            pd: pandas module

        Returns:
            Processed DataFrame with voting_precinct, regular_precinct, and registration columns
        """
        df = (
            pd.read_excel(
                file_path,
                usecols=usecols,
                skiprows=skiprows,
            )
            .truncate(after=truncate_after)
            .drop(columns=columns_to_drop)
        )

        df = df.rename(columns=rename_mapping)
        df["voting_precinct"] = df["voting_precinct"].ffill()
        df_has_voters = df["registration"].notnull()
        df = df[df_has_voters].copy()

        df["voting_precinct"] = df["voting_precinct"].str.split(" ", expand=True)[
            0
        ]
        df = df.reset_index(drop=True)

        return df
    return (process_kern_crosswalk_section,)


@app.cell
def _(pd, process_kern_crosswalk_section):
    # Constants for crosswalk file processing
    _CROSSWALK_EXCEL_PATH = (
        "inputs/counties/kern/precincts/2025 Statewide Special Election.xls"
    )
    _CROSSWALK_SKIPROWS = 6  # skip the header rows

    # Configuration for left and right sections
    _CROSSWALK_SECTIONS = {
        "left": {
            "usecols": "B:Q",  # left half of the data
            "truncate_after": 5690,  # rows after are relevant to cities in the county
            "columns_to_drop": [
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
            ],
            "rename_mapping": {
                "\nVoting Precinct": "voting_precinct",
                "\nRegular Precinct": "regular_precinct",
                "\nRegistration": "registration",
            },
        },
        "right": {
            "usecols": "U:AC",  # right half of the data
            "truncate_after": 5655,  # rows after are relevant to cities in the county
            "columns_to_drop": [
                "Unnamed: 21",
                "Mail\nBallot",
                "Unnamed: 24",
                "Unnamed: 25",
                "Unnamed: 26",
                "Ballot \nType.1",
            ],
            "rename_mapping": {
                "\nVoting Precinct.1": "voting_precinct",
                "\nRegular Precinct.1": "regular_precinct",
                "\nRegistration.1": "registration",
            },
        },
    }

    # the crosswalk file is two columns smashed together
    # so we read them into two different data frames to start
    kern_sections = [
        process_kern_crosswalk_section(
            file_path=_CROSSWALK_EXCEL_PATH,
            skiprows=_CROSSWALK_SKIPROWS,
            **section_config,
        )
        for section_config in _CROSSWALK_SECTIONS.values()
    ]

    # combine both dataframes to get a single crosswalk dataframe
    kern_crosswalk = pd.concat(kern_sections).reset_index(drop=True)

    # replace multiple spaces with one in preparation for the merge
    kern_crosswalk["regular_precinct"] = kern_crosswalk[
        "regular_precinct"
    ].str.replace("  ", " ")
    return (kern_crosswalk,)


@app.cell
def _(PROJECTED_CRS, gpd, kern_crosswalk, pd):
    # Constants for shapefile processing
    _GIS_PATH = "inputs/counties/kern/precincts/remediainquiryelectionprecinctgeographicfiles/2025 Precincts.shp"
    _DROP_COLUMNS = [
        "OBJECTID_1",
        "OBJECTID",
        "Shape_Leng",
        "Shape_Le_1",
        "Latitude",
        "Longitude",
        "PrecintID",
        "regular_precinct",
    ]

    # read in the shapefile
    kern = gpd.read_file(_GIS_PATH).to_crs(PROJECTED_CRS)

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
        df=kern,
        county="Kern",
        rename={"voting_precinct": "precinct_id", "Layer": "precinct_name"},
        drop=_DROP_COLUMNS,
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
    _GIS_FP = "inputs/counties/lake/precincts/precincts.zip"
    lake = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

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
    _GIS_FP = "inputs/counties/los_angeles/precincts/Registrar_Recorder_Election_Precincts_.shp"
    los_angeles = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    los_angeles = alter_df(
        df=los_angeles,
        county="Los Angeles",
        rename={"Precinct": "precinct_id"},
        drop=[
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
    _GIS_FP = (
        "inputs/counties/madera/precincts/VotingPrecincts_2025SpecialElection.zip"
    )
    madera = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    madera = alter_df(
        df=madera,
        county="Madera",
        rename={"VotingPrec": "precinct_id"},
        drop=["CreatedBy", "CreatedDat", "ModifyBy", "ModifyDate"],
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
    _GIS_FP = "inputs/counties/marin/precincts/CONSOLIDATED_PRECINCT.zip"
    _MARIN_PRECINCT_PREFIX = "C"
    marin = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    marin = alter_df(
        df=marin,
        county="Marin",
        rename={"Consolidat": "precinct_id"},
        drop=[
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

    marin["precinct_id"] = marin["precinct_id"].str.replace(
        _MARIN_PRECINCT_PREFIX, ""
    )

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
    _GIS_FP = "inputs/counties/mariposa/precincts/Voting_Precincts_2021_public_view_-5183800690768860583.zip"
    mariposa = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    mariposa = alter_df(
        df=mariposa,
        county="Mariposa",
        rename={"Name": "precinct_name", "PrecinctID": "precinct_id"},
        drop=["District", "Supervisor", "YEAR_CREAT"],
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
    _GIS_FP = "inputs/counties/mendocino/precincts/voterprecincts.zip"
    mendocino = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    mendocino = alter_df(
        df=mendocino,
        county="Mendocino",
        rename={"NUMBER": "precinct_id", "VOTE_DIST": "precinct_name"},
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
    _GIS_FP = "inputs/counties/merced/Merced County Pct Shapefile/MercedCountyPrecincts.shp"
    merced = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    merced = alter_df(
        df=merced,
        county="Merced",
        rename={"REF_NUM_28": "precinct_id", "PCT_NAME_1": "precinct_name"},
        drop=["Ballot_Lin", "Shape_Leng", "Shape_Area"],
    )

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
    _GIS_FP = "inputs/counties/modoc/precincts/Modoc_Voter_Precincts_2024.json"
    modoc = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    modoc = alter_df(
        df=modoc,
        county="Modoc",
        rename={"Name": "precinct_name", "Precinct_ID": "precinct_id"},
        drop=["OBJECTID", "Id", "Disclaimer", "Shape__Area", "Shape__Length"],
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
    _GIS_FP = "inputs/counties/mono/precincts/Voting_Precincts.zip"
    mono = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    mono = alter_df(
        df=mono,
        county="Mono",
        rename={"VotingPrct": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/monterey/precincts/2024-11-05 Precincts.zip"
    monterey = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    monterey = alter_df(
        df=monterey,
        county="Monterey",
        rename={"precinct": "precinct_id", "precinct_n": "precinct_name"},
        drop=["Shape_Leng", "Shape_Area"],
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
    _GIS_FP = "inputs/counties/napa/precincts/Precincts.zip"
    napa = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    napa = alter_df(
        df=napa,
        county="Napa",
        rename={"precinct": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/nevada/precincts/Voter Precincts.json"
    nevada = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    nevada = alter_df(
        df=nevada,
        county="Nevada",
        rename={"PRECINCT": "precinct_id", "PREC_NAME": "precinct_name"},
        drop=["GlobalID", "Shape__Area", "Shape__Length", "EditDate", "CONS_PREC"],
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
    _GIS_FP = "inputs/counties/orange/precincts/2025_Statewide_Special_Election_Precincts.zip"
    orange = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    orange = alter_df(
        df=orange,
        county="Orange",
        rename={"Precinct": "precinct_id"},
        drop=["Shape_Leng", "Shape_Area"],
    )

    orange
    return (orange,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Placer
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    _GIS_FP = "inputs/counties/placer/precincts/PlacerCo_VotingPrecincts_2025Spec/PlacerCo_VotingPrecincts_2025Spec.shp"
    placer = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    placer = alter_df(
        df=placer,
        county="Placer",
        rename={"VOTINGPREC": "precinct_id"},
        drop=["SHAPE_Leng", "SHAPE_Area"],
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
    _GIS_FP = "inputs/counties/riverside/precincts/riversidecaenr_9.json"
    riverside = gpd.read_file(_GIS_FP, dtype={"sVotingPre": str}).to_crs(
        PROJECTED_CRS
    )

    riverside = alter_df(
        df=riverside,
        county="Riverside",
        rename={"sVotingPre": "precinct_id"},
        drop=[
            "SUM_lTotal",
            "SUM_lTot_1",
            "VPMapping",
            "PRIMARY_NE",
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

    # change the precinct_id to match the format in the results file
    riverside["precinct_id"] = (
        riverside["precinct_id"].astype(str).str.replace(".0", "")
    )

    riverside
    return (riverside,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sacramento
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    _GIS_FP = "inputs/counties/sacramento/precincts/ConsolidatedPrecincts_-8549929174186228288.zip"
    sacramento = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    sacramento = alter_df(
        df=sacramento, county="Sacramento", rename={"VPrecinct": "precinct_id"}
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
    _GIS_FP = "inputs/counties/san_benito/precincts/Consolidated_Precincts_November_2025.zip"
    san_benito = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    san_benito = alter_df(
        df=san_benito,
        county="San Benito",
        rename={"PrecinctID": "precinct_id", "Name": "precinct_name"},
        drop=[
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

    san_benito
    return (san_benito,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Bernardino
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    _GIS_FP = "inputs/counties/san_bernardino/precincts/ROV_Precincts.zip"
    san_bernardino = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    san_bernardino = alter_df(
        df=san_bernardino,
        county="San Bernardino",
        rename={"ABRV_NAME": "precinct_id"},
        drop=[
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
    _GIS_FP = (
        "inputs/counties/san_diego/precincts/Election_Precinct_2025_11_04.json"
    )
    san_diego = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    san_diego = alter_df(
        df=san_diego,
        county="San Diego",
        rename={"consnum": "precinct_id", "consname": "precinct_name"},
        drop=[
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
    _GIS_FP = "inputs/counties/san_francisco/precincts/Election Precincts - Current, Defined 2022_20251120.zip"
    san_francisco = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    san_francisco = alter_df(
        df=san_francisco,
        county="San Francisco",
        rename={"neigh22": "precinct_name", "prec_2022": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/san_joaquin/precincts/Precincts_2025.json"
    san_joaquin = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    san_joaquin = alter_df(
        df=san_joaquin,
        county="San Joaquin",
        rename={"PRECINCT": "precinct_id"},
        drop=[
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

    san_joaquin
    return (san_joaquin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Luis Obispo
    """)
    return


@app.cell
def _(pd):
    _CROSSWALK_FP = (
        "inputs/counties/san_luis_obispo/precincts/EWMJ015_RegPctVotPctXref.txt"
    )

    # read in crosswalk from text file, make sure PRECINCTID column is a string
    # and not a float
    san_luis_obispo_crosswalk = pd.read_csv(
        _CROSSWALK_FP, sep="\t", dtype={"PRECINCTID": str}
    )

    # the value that links to election results is part of the "VOTINGPRECINCT"
    # column, extract it into its own column
    san_luis_obispo_crosswalk["voting_precinct"] = san_luis_obispo_crosswalk[
        "VOTINGPRECINCT"
    ].str.split(" ", expand=True)[0]

    # create a new value "registration_precinct" is that is the
    # potential combination of two other values. When
    # "PRECINCTPORTION" is nan then the value of the new column
    # is simply "PRECINCTID"
    # otherwise it is "%s.%s" % ("PRECINCTID", "PRECINCTPORTION")
    san_luis_obispo_crosswalk["registration_precinct"] = san_luis_obispo_crosswalk[
        "PRECINCTID"
    ].where(
        san_luis_obispo_crosswalk["PRECINCTPORTION"].isna(),
        san_luis_obispo_crosswalk["PRECINCTID"]
        + "."
        + san_luis_obispo_crosswalk["PRECINCTPORTION"],
    )

    # and drop the crosswalk columns we don't need
    san_luis_obispo_crosswalk = san_luis_obispo_crosswalk.drop(
        columns=[
            "ELECTIONABBR",
            "PRECINCTID",
            "PRECINCTPORTION",
            "VOTINGPRECINCT",
            "MAILBALLOT",
            "ABSENTEEPRECINCT",
            "BALLOTTYPE",
        ]
    )

    san_luis_obispo_crosswalk
    return (san_luis_obispo_crosswalk,)


@app.cell
def _(PROJECTED_CRS, gpd, san_luis_obispo_crosswalk):
    _GIS_FP = (
        "inputs/counties/san_luis_obispo/precincts/Voter_Precincts_-_2023.zip"
    )
    san_luis_obispo = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    # merge the crosswalk with the geo dataframe
    pre_merge_len = len(san_luis_obispo)
    san_luis_obispo = san_luis_obispo.merge(
        san_luis_obispo_crosswalk,
        left_on="PrecinctFu",
        right_on="registration_precinct",
        how="outer",
        validate="m:1",
    )
    post_merge_len = len(san_luis_obispo)
    assert pre_merge_len == post_merge_len

    # dissolve the features based on "voting_precinct_id"
    san_luis_obispo = san_luis_obispo.dissolve("voting_precinct").reset_index()

    # alter the geo data frame
    san_luis_obispo = alter_df(
        df=san_luis_obispo,
        county="San Luis Obispo",
        rename={"voting_precinct": "precinct_id"},
        drop=[
            "OBJECTID",
            "ShapeSTAre",
            "ShapeSTLen",
            "PrecinctFu",
            "PrecinctID",
            "PrecinctPo",
            "ShapeSTAre",
            "ShapeSTLen",
            "PRECINCTID",
            "registration_precinct",
        ],
    )

    san_luis_obispo
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

    _SM_CROSSWALK_PDF_PATH = (
        "inputs/counties/san_mateo/50_PrecinctConsolidations Nov2025.pdf"
    )
    _FIRST_TABLE_INDEX = 0
    _VOTING_PRECINCT_HEADER = "Voting\nPrecinct"

    with pdfplumber.open(_SM_CROSSWALK_PDF_PATH) as _sm_pdf:
        for _sm_page in _sm_pdf.pages:
            _sm_table = _sm_page.extract_tables()
            for _sm_table_row in _sm_table[_FIRST_TABLE_INDEX]:
                if _sm_table_row[_FIRST_TABLE_INDEX] != _VOTING_PRECINCT_HEADER:
                    _sm_precinct_id = _sm_table_row[_FIRST_TABLE_INDEX]
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

    _GIS_FP = "inputs/counties/san_mateo/precincts/ELECTION_PRECINCTS.shp"
    san_mateo = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

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
        df=san_mateo,
        county="San Mateo",
        rename={"consolidated_precinct": "precinct_id"},
        drop=["OBJECTID", "PrecinctID", "regular_precinct"],
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
    _GIS_FP = "inputs/counties/santa_barbara/precincts/PrecinctsAug2025.json"
    santa_barbara = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    santa_barbara = alter_df(
        df=santa_barbara,
        county="Santa Barbara",
        rename={"PRECINCTID": "precinct_id", "ABRV_NAME": "precinct_name"},
        drop=[
            "PRECINCT_N",
            "PRCNCT_PRT",
            "OBJECTID",
            "Shape__Area",
            "Shape__Length",
        ],
    )

    santa_barbara.head()

    santa_barbara.plot()
    return (santa_barbara,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Santa Clara
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    _GIS_FP = "inputs/counties/santa_clara/Precinct Data Nov 2025 Election - Kimelman (CalMatters) 01292026.zip"

    santa_clara = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    santa_clara = alter_df(
        df=santa_clara,
        county="Santa Clara",
        rename={"VPCT": "precinct_id"},
        drop=["Shape_Leng", "Shape_Area"],
    )

    santa_clara
    return (santa_clara,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Cruz
    """)
    return


@app.cell
def _(PROJECTED_CRS, gpd):
    _GIS_FP = (
        "inputs/counties/santa_cruz/precincts/Precincts_5962167425846516299.zip"
    )
    santa_cruz = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    santa_cruz = alter_df(
        df=santa_cruz,
        county="Santa Cruz",
        rename={"Precinct": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/shasta/precincts/Consolidated_Precincts.shp"
    shasta = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    shasta = alter_df(
        df=shasta,
        county="Shasta",
        rename={"CONS_PCTNU": "precinct_id", "PP_Name": "precinct_name"},
        drop=[
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
    _GIS_FP = "inputs/counties/sierra/precincts/Sierra_County_2021_Voter_Jurisdiction_Data.zip"
    _GIS_LAYER = "Sierra_County_Voter_Precincts_2021"
    sierra = gpd.read_file(_GIS_FP, layer=_GIS_LAYER).to_crs(PROJECTED_CRS)

    sierra = alter_df(
        df=sierra,
        county="Sierra",
        rename={"PRECINCT": "precinct_id", "NAME": "precinct_name"},
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
    _GIS_FP = "inputs/counties/siskiyou/precincts/Election_Precincts.zip"
    siskiyou = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    siskiyou = alter_df(
        df=siskiyou,
        county="Siskiyou",
        rename={"PRCNCT_11": "precinct_id", "NAME_11": "precinct_name"},
        drop=["OBJECTID", "DIST_11", "NAME_NUM", "Shape__Are", "Shape__Len"],
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
    _GIS_FP = "inputs/counties/solano/precincts/Current_Precincts.json"
    solano = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    solano = alter_df(
        df=solano,
        county="Solano",
        rename={"precinct": "precinct_id", "pctname": "precinct_name"},
        drop=[
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
    _GIS_FP = "inputs/counties/sonoma/precincts/ROVPublic_Precincts.json"
    sonoma = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    sonoma = alter_df(
        df=sonoma,
        county="Sonoma",
        rename={"OBJECTID": "precinct_id"},
        drop=["SubPrecinct", "Shape__Area", "Shape__Length"],
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
    _GIS_FP = "inputs/counties/sutter/precincts/Elections_Precincts.zip"
    sutter = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    sutter = alter_df(
        df=sutter,
        county="Sutter",
        rename={"NAME": "precinct_name", "PRECINCTID": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/tehama/precincts/tehama-precincts.json"
    tehama = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    tehama = alter_df(
        df=tehama,
        county="Tehama",
        rename={"PRECINCTID": "precinct_id", "NAME": "precinct_name"},
        drop=["OBJECTID"],
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
        _PRECINCT_ID_DIGIT_COUNT = 7
        _REGISTRATION_PRECINCT_PREFIX = "1 "
        last_seen_id = None

        def _extract_precinct_from_page_line(line, last_seen_id):
            row = {
                "registration_precinct": None,
                "results_precinct": None,
            }

            # the lines with voting precincts (which are like sections)
            # start with a seven digit number
            if re.match(rf"^\d{{{_PRECINCT_ID_DIGIT_COUNT}}}", line):
                last_seen_id = line.split(" -")[0]
                row["results_precinct"] = last_seen_id
            else:
                row["results_precinct"] = last_seen_id

            # if the row starts with a "1 " then it contains the
            # registration precinct
            if re.match(rf"^{_REGISTRATION_PRECINCT_PREFIX}", line):
                line_split = line.split(" ")
                regular_precinct = line_split[REGISTRATION_PRECINCT_INDEX].strip()
                if re.match(
                    rf"^\d{{{_PRECINCT_ID_DIGIT_COUNT}}}$", regular_precinct
                ):
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
    _TULARE_CROSSWALK_PDF_PATH = "inputs/counties/tulare/tularecounty_2025novspec_votabsregpctxrefdetail.pdf"
    _GIS_FP = "inputs/counties/tulare/precincts/tulare-precincts.json"

    # create a variable to store all of the extracted rows
    tulare_crosswalk = []

    with pdfplumber.open(_TULARE_CROSSWALK_PDF_PATH) as tulare_crosswalk_pdf:
        for page in tulare_crosswalk_pdf.pages:
            # extract the text from each page
            page_extracted = extract_tulare_crosswalk_pdf_page(page)

            # and add the results to our list
            tulare_crosswalk.extend(page_extracted)

    # turn the resulting list into a dataframe
    tulare_crosswalk = pd.DataFrame(tulare_crosswalk)

    tulare = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

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
        df=tulare,
        county="Tulare",
        rename={"results_precinct": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/tuolumne/precincts/TC_VotingPrecincts_Sept2022/TuolumneCounty_VotingPrecincts_consolidationNov2022.shp"
    tuolumne = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    tuolumne = alter_df(
        df=tuolumne,
        county="Tuolumne",
        rename={"PREC_NO": "precinct_id", "PRECINCT": "precinct_name"},
        drop=["HomePrecin", "PropConsol"],
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
    _GIS_FP = "inputs/counties/ventura/precincts/Election_Precinct.zip"
    ventura = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    ventura = alter_df(
        df=ventura,
        county="Ventura",
        rename={"electid": "precinct_id", "number_": "precinct_name"},
        drop=[
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
    _GIS_FP = "inputs/counties/yolo/precincts/PrecinctsConsolidated_20250904.zip"
    yolo = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    yolo = alter_df(
        df=yolo,
        county="Yolo",
        rename={"PRECINCTID": "precinct_id"},
        drop=[
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
    _GIS_FP = "inputs/counties/yuba/precincts/YubaCountyCA_2024_03_21_001/VotingPrecincts.shp"
    yuba = gpd.read_file(_GIS_FP).to_crs(PROJECTED_CRS)

    yuba = alter_df(
        df=yuba,
        county="Yuba",
        rename={"precinctid": "precinct_id", "name": "precinct_name"},
        drop=[
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
