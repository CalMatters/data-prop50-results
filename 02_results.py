import marimo

__generated_with = "0.19.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # California counties' results workflow

    This notebook cleans Prop. 50 precinct results data from all counties in the state. We want each precinct to have the following attributes/columns:

    * `county` - The county containing the precinct
    * `precinct_id` - Unique ID for the precinct
    * `yes_votes` - the number of votes for "Yes" on Prop. 50 in the precinct
    * `no_votes` - the number of votes for "No" on Prop. 50 in the precinct
    * `turnout` - the percent of the voters who cast a ballot in the precinct, included if included by the county; range is 0 to 100
    """)
    return


@app.cell
def _():
    import json
    from pathlib import Path
    import re

    from esridump.dumper import EsriDumper
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pdfplumber
    return EsriDumper, Path, json, mo, np, pd, pdfplumber, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    VOTE_COUNT_COLUMNS = ["yes_votes", "no_votes", "total_votes"]
    return (VOTE_COUNT_COLUMNS,)


@app.cell
def _():
    REGISTERED_VOTERS_COLUMN_NAME = "registered_voters"
    TURNOUT_COLUMN_NAME = "turnout"
    return REGISTERED_VOTERS_COLUMN_NAME, TURNOUT_COLUMN_NAME


@app.cell
def _(REGISTERED_VOTERS_COLUMN_NAME, TURNOUT_COLUMN_NAME, VOTE_COUNT_COLUMNS):
    NUMERIC_COLUMNS = [
        REGISTERED_VOTERS_COLUMN_NAME,
        TURNOUT_COLUMN_NAME,
    ] + VOTE_COUNT_COLUMNS
    return (NUMERIC_COLUMNS,)


@app.cell
def _():
    STANDARDIZED_COLUMNS = [
        "precinct_id",
        "turnout",
        "yes_votes",
        "no_votes",
        "total_votes",
        "county",
        "registered_voters",
    ]
    return (STANDARDIZED_COLUMNS,)


@app.cell
def _():
    OUTPUT_FP = "outputs/results.csv"
    return (OUTPUT_FP,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper Functions
    """)
    return


@app.cell
def _(pd):
    def _clean_numeric_string(series_pd: pd.Series) -> pd.Series:
        # Remove comma separators and percent signs
        return (
            series_pd.astype(str)
            .str.replace(",", "")
            .str.replace("%", "")
            .str.strip()
        )


    def to_numeric_with_warning(series: pd.Series, **kwargs) -> pd.Series:
        """
        Convert a pandas Series to numeric, with warning for values coerced to NaN.

        Parameters
        ----------
        series : pd.Series
            The input series to convert
        **kwargs :
            Additional arguments to pass to pd.to_numeric

        Returns
        -------
        pd.Series
            Series with numeric values, NaN for invalid inputs

        Notes
        -----
        This function wraps pd.to_numeric and warns about values that couldn't be
        converted to numeric format. Preprocessing removes comma separators to avoid mistaken coercions.
        """
        # Get original non-null values
        original_values = series.copy()

        # Remove comma separators and convert to numeric with coercion
        numeric_series = pd.to_numeric(
            _clean_numeric_string(original_values),
            errors="coerce",
            **kwargs,
        )

        # Find values that were converted to NaN but weren't NaN originally
        null_mask = numeric_series.isna() & original_values.notna()

        # If any values were coerced, print a warning with the list
        if null_mask.any():
            bad_values = original_values[null_mask].unique()
            print(
                f"Warning: {len(bad_values)} values in {series.name} could not be converted to numeric and were set to NaN: {bad_values}"
            )

        return numeric_series
    return (to_numeric_with_warning,)


@app.cell
def _(
    NUMERIC_COLUMNS,
    REGISTERED_VOTERS_COLUMN_NAME,
    STANDARDIZED_COLUMNS,
    calculate_total_votes,
    calculate_turnout,
    pd,
    to_numeric_with_warning,
):
    def standardize_results_df(
        results_df: pd.DataFrame,
        county: str,
        rename_column_map=None,
        keep_columns=None,
    ) -> pd.DataFrame:
        """
        Standardize the structure of a results DataFrame by renaming columns and keeping specified columns.

        This function takes a DataFrame containing election results and standardizes it by:
        1. Renaming columns according to the provided mapping
        2. Keeping only columns specified in keep_columns, or using the global STANDARDIZED_COLUMNS if not specified
        3. Returning a copy of the DataFrame with only the desired columns

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame to be standardized
        rename_columns : dict, optional
            A dictionary mapping existing column names to new column names, by default None
        keep_columns : list, optional
            A list of column names to keep in the final DataFrame. If not provided,
            uses the global STANDARDIZED_COLUMNS constant, by default None

        Returns
        -------
        pd.DataFrame
            A new DataFrame with standardized column names and only the specified columns
        """
        results_df["county"] = county

        if rename_column_map:
            results_df = results_df.rename(columns=rename_column_map)

        for numeric_column in NUMERIC_COLUMNS:
            if numeric_column in list(results_df):
                results_df[numeric_column] = to_numeric_with_warning(
                    results_df[numeric_column]
                )

        if "total_votes" not in list(results_df):
            results_df["total_votes"] = calculate_total_votes(results_df)

        if REGISTERED_VOTERS_COLUMN_NAME in list(
            results_df
        ) and "turnout" not in list(results_df):
            results_df["turnout"] = calculate_turnout(
                results_df["total_votes"],
                results_df[REGISTERED_VOTERS_COLUMN_NAME],
            )

        if not keep_columns:
            keep_columns = STANDARDIZED_COLUMNS
        keep_columns = [
            column for column in results_df.columns if column in keep_columns
        ]

        return results_df[keep_columns].copy()
    return (standardize_results_df,)


@app.cell
def _(np, pd, re):
    REDACTED_PLACEHOLDER_REGEX = re.compile(r"\*+")


    def clean_redacted_precincts(
        _series: pd.Series,
        placeholder_regex=REDACTED_PLACEHOLDER_REGEX,
    ) -> pd.Series:
        _series = _series.replace(placeholder_regex, np.nan)
        return _series.astype("Int64")
    return (clean_redacted_precincts,)


@app.cell
def _(pd):
    def calculate_total_votes(df_clean: pd.DataFrame) -> pd.Series:
        return df_clean["yes_votes"] + df_clean["no_votes"]
    return (calculate_total_votes,)


@app.cell
def _(pd):
    def calculate_turnout(
        votes_cast: pd.Series, registered_voter_count: pd.Series
    ) -> pd.Series:
        registered_voter_count = registered_voter_count.replace(0, 1)
        return round((votes_cast / registered_voter_count) * 100, 1)
    return (calculate_turnout,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Combine and export
    """)
    return


@app.cell
def _(
    alameda,
    butte,
    calaveras,
    colusa,
    contra_costa,
    el_dorado,
    fresno,
    glenn,
    imperial,
    inyo,
    kern,
    kings,
    lake,
    los_angeles,
    madera,
    marin,
    merced,
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
    santa_clara,
    shasta,
    sierra,
    siskiyou,
    solano,
    sonoma,
    stanislaus,
    sutter,
    trinity,
    tulare,
    tuolumne,
    ventura,
    yolo,
    yuba,
):
    COUNTIES_TO_COMBINE = [
        alameda,
        butte,
        calaveras,
        colusa,
        contra_costa,
        el_dorado,
        glenn,
        fresno,
        imperial,
        inyo,
        kern,
        kings,
        lake,
        los_angeles,
        madera,
        marin,
        merced,
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
        santa_clara,
        shasta,
        sierra,
        siskiyou,
        solano,
        sonoma,
        stanislaus,
        sutter,
        trinity,
        tulare,
        tuolumne,
        ventura,
        yolo,
        yuba,
    ]
    return (COUNTIES_TO_COMBINE,)


@app.cell
def _(COUNTIES_TO_COMBINE, OUTPUT_FP, pd):
    combined = pd.concat(COUNTIES_TO_COMBINE).reset_index(drop=True)
    combined.to_csv(OUTPUT_FP, index=False)
    combined
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(
    VOTE_COUNT_COLUMNS,
    clean_redacted_precincts,
    pd,
    standardize_results_df,
):
    _COUNTY = "Alameda"
    _DATA_FP = "inputs/counties/alameda/Statement of Vote - Statewide Special Election.xlsx"
    ALAMEDA_PRECINCT_ID_PATTERN = r"\d{6}"
    ALAMEDA_SKIP_HEADER_ROWS = 5
    _PRECINCT_EXCLUDE_VALUES = ["Vote by Mail", "Election Day"]

    alameda = pd.read_excel(
        _DATA_FP,
        sheet_name=1,
        skiprows=ALAMEDA_SKIP_HEADER_ROWS,
    )

    # get rid of extra values associated with each precinct
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        alameda = alameda[alameda["Unnamed: 1"] != _exclude_val].copy()

    alameda = standardize_results_df(
        results_df=alameda,
        county=_COUNTY,
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Total Votes": "total_votes",
        },
    )

    # remove rows where the precinct ID is not a six digit number
    alameda = alameda[
        alameda["precinct_id"].str.match(ALAMEDA_PRECINCT_ID_PATTERN, na=False)
    ].copy()

    alameda[VOTE_COUNT_COLUMNS] = alameda[VOTE_COUNT_COLUMNS].apply(
        clean_redacted_precincts
    )

    # get rid of the index column
    alameda = alameda.reset_index(drop=True)

    alameda.head()
    return (alameda,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Butte
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Butte"
    _DATA_FP = "inputs/counties/butte/detail.xlsx"
    _PRECINCT_ID_PATTERN = r"\d{4}"


    def butte_df():
        results_df = pd.read_excel(_DATA_FP, sheet_name="2", skiprows=2)
        results_df = standardize_results_df(
            results_df=results_df,
            county=_COUNTY,
            rename_column_map={
                "Precinct": "precinct_id",
                "Total Votes": "no_votes",
                "Total Votes.1": "yes_votes",
                "Total": "total_votes",
                "Registered Voters": "registered_voters",
            },
        )
        # remove rows where the precinct_id is not a four digit number
        results_df = results_df[
            results_df["precinct_id"].str.match(_PRECINCT_ID_PATTERN)
        ].copy()
        return results_df


    butte = butte_df()
    butte.head()
    return (butte,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calaveras
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Calaveras"
    _PRECINCT_ID_CROP = (0, 135, 60, 160)
    _YES_VOTES_CROP = (532, 200, 556, 215)
    _NO_VOTES_CROP = (532, 220, 556, 235)
    _REGISTERED_VOTERS_CROP = (445, 140, 470, 155)
    _PDF_FP = "inputs/counties/calaveras/Official Precinct Report-12-1-2025 01-27-49 PM.pdf"

    rows = []
    with pdfplumber.open(_PDF_FP) as pdf:
        for page in pdf.pages:
            row = {}
            row["precinct_id"] = page.crop(_PRECINCT_ID_CROP).extract_text()
            row["yes_votes"] = int(
                page.crop(_YES_VOTES_CROP).extract_text().replace(",", "")
            )
            row["no_votes"] = int(
                page.crop(_NO_VOTES_CROP).extract_text().replace(",", "")
            )
            row["registered_voters"] = int(
                page.crop(_REGISTERED_VOTERS_CROP)
                .extract_text()
                .replace(",", "")
                .replace("of", "")
                .strip()
            )
            rows.append(row)

    calaveras = pd.DataFrame(rows)
    calaveras = standardize_results_df(
        results_df=calaveras,
        county=_COUNTY,
        rename_column_map=None,
    )
    calaveras.head()
    return (calaveras,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Colusa
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Colusa"
    _PDF_FP = "inputs/counties/colusa/precinct SOV.pdf"
    _PDF_PAGE_RANGE = (4, 5)  # (start, end) non-inclusive
    _CROP_BOX = (396, 50, 792, 612)
    # Exclude rows with these precinct_id values: totals and additional per-precinct breakdowns
    _PRECINCT_ID_EXCLUDE_VALUES = [
        "Electionwide - Total",
        "Electionwide",
        "Vote by Mail",
        "Election Day",
        "California - Total",
    ]
    _COLUMN_NAMES = [
        "precinct_id",
        "yes_votes",
        "Yes_Blank",
        "no_votes",
        "No_Blank",
    ]


    def colusa_df():
        colusa = None
        with pdfplumber.open(_PDF_FP) as pdf:
            extracted_pages = []
            prop_50_pages = pdf.pages[_PDF_PAGE_RANGE[0] : _PDF_PAGE_RANGE[1]]

            for page in prop_50_pages:
                cropped = page.crop(_CROP_BOX)
                table = cropped.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            colusa = pd.concat(extracted_pages)

        # rename columns
        colusa.columns = _COLUMN_NAMES

        for _exclude_val in _PRECINCT_ID_EXCLUDE_VALUES:
            colusa = colusa[colusa["precinct_id"] != _exclude_val].copy()

        # some values are white space so replace that with None
        colusa = colusa.replace(r"^\s*$", None, regex=True)

        # backfill missing values
        colusa = colusa.bfill(limit=1)

        # and then drop the "Total" value rows that were used to backfill
        colusa = colusa[colusa["precinct_id"] != "Total"].copy()

        return colusa


    colusa = colusa_df()
    colusa = standardize_results_df(
        results_df=colusa,
        county=_COUNTY,
    )
    colusa = colusa.reset_index(drop=True)
    colusa.head()
    return (colusa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Contra Costa
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Contra Costa"
    _DATA_FP = (
        "inputs/counties/contra_costa/StatementOfVotesCastRPT_ByPrecinct.xlsx"
    )
    _RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 3
    # Remove rows corresponding to non-precinct records, including by voting method and extra cumalative/county rows.
    _PRECINCT_EXCLUDE_VALUES = [
        # there are four rows per precinct so let's drop two of them: In-Person and Vote By Mail
        "In-Person",
        "Vote By Mail",
        # drop extraneous Cumulative records and county-wide summaries
        "Cumulative",
        "County",
        "Contra Costa County",
        "Cumulative - Total",
        "County - Total",
        "Contra Costa County - Total",
    ]

    contra_costa = pd.read_excel(
        _DATA_FP,
        sheet_name=_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        contra_costa = contra_costa[
            contra_costa["Precinct"] != _exclude_val
        ].copy()

    # backfill the values from the rows where "Precinct" is "Total" to the rows
    # that have proper precinct IDs
    contra_costa = contra_costa.bfill(limit=1)

    # and now get rid of the total per precinct row
    contra_costa = contra_costa[contra_costa["Precinct"] != "Total"]

    # use the standardize_results_df function to calculate turnout and finalize columns
    contra_costa = standardize_results_df(
        results_df=contra_costa,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    # get rid of remaining index column
    contra_costa = contra_costa.reset_index(drop=True)
    contra_costa
    return (contra_costa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## El Dorado
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "El Dorado"
    _PDF_FP = "inputs/counties/el_dorado/SOS - EDC - StatementOfVotestCastRPT-Precinct.pdf"
    _PDF_PAGE_RANGE = (26, 47)
    _CROP_BOX = (396, 50, 792, 612)
    _COLUMN_NAMES = [
        "precinct_id",
        "yes_votes",
        "Yes_Blank",
        "no_votes",
        "No_Blank",
        "total_votes",
    ]
    _PRECINCT_ID_EXCLUDE_VALUES = [
        "Mail",
        "Vote Center",
        "Election Day",
        "Provisional",
        "Electionwide - Total",
        "Cumulative",
    ]


    def el_dorado_df():
        el_dorado = None
        with pdfplumber.open(
            _PDF_FP,
        ) as pdf:
            extracted_pages = []
            prop_50_pages = pdf.pages[_PDF_PAGE_RANGE[0] : _PDF_PAGE_RANGE[1]]

            for page in prop_50_pages:
                cropped = page.crop(_CROP_BOX)
                table = cropped.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            el_dorado = pd.concat(extracted_pages)

        # rename columns
        el_dorado.columns = _COLUMN_NAMES

        # get rid of total count rows
        for _exclude_val in _PRECINCT_ID_EXCLUDE_VALUES:
            el_dorado = el_dorado[el_dorado["precinct_id"] != _exclude_val].copy()

        # some values are white space so replace that with None
        el_dorado = el_dorado.replace(r"^\s*$", None, regex=True)

        # backfill missing values
        el_dorado = el_dorado.bfill(limit=1)

        # and then drop the "Total" value rows that were used to backfill
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Total"].copy()

        return el_dorado


    el_dorado = el_dorado_df()
    el_dorado = standardize_results_df(
        results_df=el_dorado,
        county=_COUNTY,
    )
    el_dorado = el_dorado.reset_index(drop=True)
    el_dorado.head()
    return (el_dorado,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fresno
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Fresno"
    _DATA_FP = "inputs/counties/fresno/statementofvotescastrpt-with-privacy.xlsx"
    _PROP50_RESULTS_SHEET = "Sheet3"
    _SKIP_HEADER_ROWS = 5
    _PRECINCT_EXCLUDE_VALUES = [
        "Vote Center",
        "Vote by Mail",
        "County - Total",
        "Electionwide - Total",
    ]

    fresno = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    # Remove extra row containing repeated or extraneous data
    is_extra_row = fresno["Electionwide"].isin(_PRECINCT_EXCLUDE_VALUES) | fresno[
        "Electionwide"
    ].str.contains("Cumulative", na=False)
    fresno = fresno[~is_extra_row].copy()
    # and then backfill so that the total values are associated
    # with the rows with valid precinct ids
    fresno = fresno.bfill()

    # and then get rid of the "Total" rows
    fresno = fresno[fresno["Electionwide"] != "Total"].copy()

    fresno = standardize_results_df(
        results_df=fresno,
        county=_COUNTY,
        # contents of unnamed columns is very clear in the source
        # spreadsheet and are unnamed because there are multiple
        # header rows. open source spreadsheet to verify
        rename_column_map={
            "Electionwide": "precinct_id",
            "Unnamed: 7": "yes_votes",
            "Unnamed: 9": "no_votes",
            "Unnamed: 2": "registered_voters",
        },
    )

    # reset and drop index column
    fresno = fresno.reset_index(drop=True)

    fresno.head()
    return (fresno,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Glenn
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Glenn"
    _PDF_FP = "inputs/counties/glenn/Statement of Votes 2025.pdf"
    _PDF_PAGE_RANGE = (13, 41)
    _PDF_PAGE_STEP = 2
    _CROP_BOX = (396, 50, 792, 612)
    _COLUMN_NAMES = [
        "precinct_id",
        "yes_votes",
        "Yes_Blank",
        "no_votes",
        "No_Blank",
        "total_votes",
    ]
    _PRECINCT_ID_EXCLUDE_VALUES = [
        "Electionwide - Total",
        "Electionwide",
        "Vote by Mail",
        "Election Day",
    ]


    def glenn_df():
        glenn = None
        with pdfplumber.open(_PDF_FP) as pdf:
            extracted_pages = []
            prop_50_pages = pdf.pages[_PDF_PAGE_RANGE[0] : _PDF_PAGE_RANGE[1]][
                ::_PDF_PAGE_STEP
            ]

            for page in prop_50_pages:
                cropped = page.crop(_CROP_BOX)
                table = cropped.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            glenn = pd.concat(extracted_pages)

        # rename columns
        glenn.columns = _COLUMN_NAMES

        # get rid of total rows and values associated with each precinct
        for _exclude_val in _PRECINCT_ID_EXCLUDE_VALUES:
            glenn = glenn[glenn["precinct_id"] != _exclude_val].copy()

        # some values are white space so replace that with None
        glenn = glenn.replace(r"^\s*$", None, regex=True)

        # backfill missing values
        glenn = glenn.bfill(limit=1)

        # and then drop the "Total" value rows that were used to backfill
        glenn = glenn[glenn["precinct_id"] != "Total"].copy()

        return glenn


    glenn = glenn_df()
    glenn = standardize_results_df(
        results_df=glenn,
        county=_COUNTY,
    )
    glenn = glenn.reset_index(drop=True)
    glenn.head()
    return (glenn,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imperial
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Imperial"
    _DATA_FP = "inputs/counties/imperial/Precincts_4.csv"
    _SKIP_HEADER_ROWS = 2


    def imperial_df():
        csv = pd.read_csv(_DATA_FP, skiprows=_SKIP_HEADER_ROWS)
        prop_50 = csv[csv["Contest Name"] == "PROPOSITION 50"]

        pt = prop_50.pivot_table(
            index="Precinct",
            columns="Candidate Name",
            values="Votes",
            aggfunc="sum",
        )

        turnout = prop_50.groupby("Precinct")["Voter Turnout"].max()

        prop_50_altered = pt.merge(turnout, on="Precinct")
        prop_50_altered = prop_50_altered.reset_index()
        prop_50_altered = standardize_results_df(
            results_df=prop_50_altered,
            county=_COUNTY,
            rename_column_map={
                "Precinct": "precinct_id",
                "Voter Turnout": "turnout",
                "YES": "yes_votes",
                "NO": "no_votes",
            },
        )

        prop_50_altered["precinct_id"] = (
            prop_50_altered["precinct_id"].str.replace("MB", "").str.strip()
        )

        return prop_50_altered


    imperial = imperial_df()

    imperial.head()
    return (imperial,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inyo
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Inyo"
    _DATA_FP = "inputs/counties/inyo/SOVC-Redacted (by precincts).xlsx"
    _SKIP_HEADER_ROWS = 5
    _PRECINCT_EXCLUDE_VALUES = [
        "Electionwide - Total",
        "Cumulative",
        "Cumulative - Total",
        "County - Total",
    ]

    inyo = pd.read_excel(
        _DATA_FP,
        sheet_name=1,
        skiprows=_SKIP_HEADER_ROWS,
    )

    # get rid of some extra rows
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        inyo = inyo[inyo["Electionwide"] != _exclude_val].copy()

    inyo = standardize_results_df(
        results_df=inyo,
        county=_COUNTY,
        rename_column_map={  # multi-header columns produced unnameed columns; correct names determined manually
            "Electionwide": "precinct_id",
            "Unnamed: 6": "yes_votes",
            "Unnamed: 8": "no_votes",
            "Unnamed: 10": "total_votes",
            "Unnamed: 2": "registered_voters",  # registered voters column
        },
    )

    # reset and drop index column
    inyo = inyo.reset_index(drop=True)

    inyo.head()
    return (inyo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kern
    """)
    return


@app.cell
def _():
    KERN_PRECINCT_VALUES_TO_REMOVE = [
        "12th Senatorial District",
        "12th Senatorial District - Total",
        "16th Senatorial District",
        "16th Senatorial District - Total",
        "1st Supervisorial District",
        "1st Supervisorial District - Total",
        "2nd Supervisorial District",
        "2nd Supervisorial District - Total",
        "32nd Assembly District",
        "32nd Assembly District - Total",
        "34th Assembly District",
        "34th Assembly District - Total",
        "35th Assembly District",
        "35th Assembly District - Total",
        "3rd Supervisorial District",
        "3rd Supervisorial District - Total",
        "4th Supervisorial District",
        "4th Supervisorial District - Total",
        "5th Supervisorial District",
        "5th Supervisorial District - Total",
        "Board Of Equalization",
        "Board Of Equalization - Total",
        "Board of Equalization (State)",
        "Board of Equalization (State) - Total",
        "CALIFORNIA",
        "CALIFORNIA - Total",
        "Cities",
        "Cities - Total",
        "City of Arvin",
        "City of Arvin - Total",
        "City of Bakersfield",
        "City of Bakersfield - Total",
        "City of California City",
        "City of California City - Total",
        "City of Delano",
        "City of Delano - Total",
        "City of Maricopa",
        "City of Maricopa - Total",
        "City of McFarland",
        "City of McFarland - Total",
        "City of Ridgecrest",
        "City of Ridgecrest - Total",
        "City of Shafter",
        "City of Shafter - Total",
        "City of Taft",
        "City of Taft - Total",
        "City of Tehachapi",
        "City of Tehachapi - Total",
        "City of Wasco",
        "City of Wasco - Total",
        "County",
        "County - Total",
        "County Supervisor",
        "County Supervisor - Total",
        "Countywide",
        "Countywide - Total",
        "Cumulative",
        "Cumulative - Total",
        "Electionwide",
        "Electionwide - Total",
        "Kern County",
        "Kern County - Total",
        "Member of the State Assembly",
        "Member of the State Assembly - Total",
        "STATE",
        "STATE - Total",
        "State Senator",
        "State Senator - Total",
        "Unincorporated",
        "Unincorporated - Total",
        "Unincorporated Area",
        "Unincorporated Area - Total",
    ]
    return (KERN_PRECINCT_VALUES_TO_REMOVE,)


@app.cell
def _(KERN_PRECINCT_VALUES_TO_REMOVE, pd, standardize_results_df):
    _COUNTY = "Kern"
    _DATA_FP = "inputs/counties/kern/StatementOfVotesCastRPT.xlsx"
    # read the excel file using the "Sheet2" sheet, skip TK rows at the top and TK rows at the bottom
    _SKIP_HEADER_ROWS = 3
    _SKIP_FOOTER_ROWS = 3
    kern = pd.read_excel(
        _DATA_FP,
        sheet_name=1,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )

    # get rid of the first two rows that are presentational
    for value in KERN_PRECINCT_VALUES_TO_REMOVE:
        kern = kern[kern["Precinct"] != value].copy()

    kern = standardize_results_df(
        results_df=kern,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    # finally, drop the index and duplicates
    kern = kern.reset_index(drop=True).drop_duplicates()
    kern
    return (kern,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kings
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Kings"
    _PDF_FP = "inputs/counties/kings/NOV 2025 SOV BOOK.pdf"
    _PROP50_PAGE_RANGE = (9, 12)
    # Precinct IDs are 4 digits starting with 1 (e.g., 1001, 1002)
    _PRECINCT_ID_PATTERN = r"1\d{3}"


    def extract_kings_pdf():
        kings = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(_PDF_FP) as pdf:
            # just a few pages from the document are related to Prop 50
            prop_50_pages = pdf.pages[
                _PROP50_PAGE_RANGE[0] : _PROP50_PAGE_RANGE[1]
            ]
            extracted_pages = [
                pd.DataFrame(page.extract_table()[1:]) for page in prop_50_pages
            ]
            kings = pd.concat(extracted_pages)
        return kings


    # create a dataframe from the pdf
    kings = extract_kings_pdf()

    # there are rows for different types of voting
    # but we just want the "Total"
    kings = kings[kings[1] == "Total"].copy()

    # the precinct IDs all start with "1"
    kings = kings[kings[0].str.match(_PRECINCT_ID_PATTERN)].copy()

    kings = standardize_results_df(
        results_df=kings,
        county=_COUNTY,
        # mapping manually verified from the source PDF document
        rename_column_map={
            0: "precinct_id",
            2: "registered_voters",
            # 3: "total_votes" # uses votes cast
            4: "turnout",
            5: "yes_votes",
            6: "no_votes",
        },
    )

    kings = kings.reset_index(drop=True)
    kings.head()
    return (kings,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lake
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Lake"
    _PDF_FP = "inputs/counties/lake/Statement of Votes12022025.pdf"
    _PRECINCT_EXCLUDE_VALUES = [
        "Vote by Mail Totals",
        "Election Day Voting Totals",
        "Grand Totals",
    ]


    def extract_lake_pdf():
        lake = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(_PDF_FP) as pdf:
            # just a few pages from the document are related to Prop 50
            prop_50_page = pdf.pages[0]
            table = prop_50_page.extract_table()
            lake = pd.DataFrame(table[1:])

        return lake


    # create a dataframe from the pdf
    lake = extract_lake_pdf()

    # remove some extra rows at the end of the dataframe
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        lake = lake[lake[0] != _exclude_val].copy()

    lake = standardize_results_df(
        results_df=lake,
        county=_COUNTY,
        # column with an index of 2 is "Ballots Cast"
        rename_column_map={
            0: "precinct_id",
            1: "registration",
            3: "turnout",
            4: "yes_votes",
            5: "no_votes",
        },
    )

    # and remove the index
    lake = lake.reset_index(drop=True)

    lake
    return (lake,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Los Angeles
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _DATA_FP = "inputs/counties/los_angeles/4337_final_svc_excel/STATE_MEASURE_50_11-04-25_by_Precinct_4337-bmc9985.xls"
    _COUNTY = "Los Angeles"
    _SKIP_HEADER_ROWS = 2

    los_angeles = pd.read_excel(
        _DATA_FP,
        skiprows=_SKIP_HEADER_ROWS,
    )

    # remove rows for individual voting methods
    los_angeles = los_angeles[los_angeles["TYPE"] == "TOTAL"].copy()

    los_angeles = standardize_results_df(
        results_df=los_angeles,
        county=_COUNTY,
        # "BALLOTS CAST" is dropped
        rename_column_map={
            "PRECINCT": "precinct_id",
            "YES": "yes_votes",
            "NO": "no_votes",
            "REGISTRATION": "registered_voters",
        },
    )

    # drop the index
    los_angeles = los_angeles.reset_index(drop=True)

    los_angeles.head()
    return (los_angeles,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Madera
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Madera"
    _DATA_FP = (
        "inputs/counties/madera/Statement-of-Votes-CastXLSX-November-4-2025-1.xlsx"
    )
    _PRECINCT_RESULTS_SHEET = "SOV by Precinct"
    _SKIP_HEADER_ROWS = 7
    _PRECINCT_ID_PATTERN = r"^\d{4}$"
    _PRECINCT_EXCLUDE_VALUES = ["Vote Center", "Vote by Mail"]

    madera = pd.read_excel(
        _DATA_FP,
        sheet_name=_PRECINCT_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
        dtype={"Unnamed: 0": str},
    )

    # remove extra rows
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        madera = madera[madera["Unnamed: 1"] != _exclude_val].copy()

    madera = standardize_results_df(
        results_df=madera,
        county=_COUNTY,
        # "Voters Cast" is dropped
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "Yes": "yes_votes",
            "No": "no_votes",
            "Total Votes": "total_votes",
        },
    )

    madera = madera[
        madera["precinct_id"].str.strip().str.match(_PRECINCT_ID_PATTERN, na=False)
    ]

    # reset and drop index column
    madera = madera.reset_index(drop=True)

    madera
    return (madera,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Marin
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Marin"
    _DATA_FP = "inputs/counties/marin/11-25_SOVC.Final_.xlsx"
    _PRECINCT_EXCLUDE_VALUES = [
        "Countywide",
        "Countywide - Total",
        "Cumulative",
        "Cumulative - Total",
        "Electionwide",
        "Electionwide - Total",
    ]

    marin = pd.read_excel(
        _DATA_FP,
        sheet_name="Sheet4",
        skiprows=3,
    )

    # get rid of some extra rows
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        marin = marin[marin["Precinct"] != _exclude_val].copy()

    marin = standardize_results_df(
        results_df=marin,
        county=_COUNTY,
        # "Voters Cast" is dropped
        rename_column_map={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    # drop the remaining columns we don't care about, including the index
    marin = marin.reset_index(drop=True)

    marin.head()
    return (marin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Merced
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Merced"
    _DATA_FP = "inputs/counties/merced/detail.xlsx"
    _PROP50_RESULTS_SHEET = "2"
    _SKIP_HEADER_ROWS = 2
    merced = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    # drop the columns we don't need
    merced = merced.drop(
        columns=[
            "Election Day",
            "Early Voting",
            "Vote by Mail",
            "Conditional/Provisional",
            "Election Day.1",
            "Early Voting.1",
            "Vote by Mail.1",
            "Conditional/Provisional.1",
        ]
    )

    merced = standardize_results_df(
        results_df=merced,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
            "Total": "total_votes",
            "Registered Voters": "registered_voters",
        },
    )
    merced.head()
    return (merced,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Monterey
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Monterey"
    _DATA_FP = "inputs/counties/monterey/SOV_2025-11-04_ByPrecinct.xlsx"
    _PROP50_RESULTS_SHEET = "PrecinctCanvass"
    _SKIP_HEADER_ROWS = 5
    monterey = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    monterey = monterey[monterey["Unnamed: 1"] == "Total"].copy()

    monterey = standardize_results_df(
        results_df=monterey,
        county=_COUNTY,
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Total Votes": "total_votes",
            "Registered Voters": "registered_voters",
        },
    )

    monterey = monterey.reset_index(drop=True)
    monterey.head()
    return (monterey,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Napa
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Napa"
    _PDF_FP = "inputs/counties/napa/Statement of Votes Cast_202512031558433636.pdf"
    _PROP50_END_PAGE = 6


    def extract_napa_pdf():
        napa = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(_PDF_FP) as pdf:
            extracted_pages = []
            # just a few pages from the document are related to Prop 50
            prop_50_pages = pdf.pages[:_PROP50_END_PAGE]

            for page in prop_50_pages:
                table = page.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            napa = pd.concat(extracted_pages)
        return napa


    napa = extract_napa_pdf()

    napa = standardize_results_df(
        results_df=napa,
        county=_COUNTY,
        rename_column_map={
            0: "precinct_id",
            1: "registered_voters",
            # 2 is Times Cast
            3: "turnout",
            4: "total_votes",
            5: "yes_votes",
            6: "no_votes",
        },
    )

    napa = napa.reset_index(drop=True)
    napa.head()
    return (napa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orange

    Orange has a precinct with ID `99999` which is used to report results in precincts that have fewer than 10 voters. The precinct's record says it has 976 registered voters with 430 votes cast but it doesn't have a corresponding geographic feature so we drop it.

    Orange results data has two different precinct identifiers. I determined which one to use by cross referencing with the counties precinct GIS file.
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Orange"
    _DATA_FP = "inputs/counties/orange/media.zip"
    _TAB_SEP = "\t"
    _DTYPE_MAP = {".Precinct": str, "Precinct ID": str}
    _COLUMN_NAMES = [
        "precinct_id",
        "total_votes",
        "total_votes_dupe",
        "registered_voters",
        "registered_voters_dupe",
        "no_votes",
        "yes_votes",
        "turnout",
        "turnout_dupe",
    ]
    _AGGREGATE_PRECINCT_ID = "99999"

    orange = pd.read_csv(_DATA_FP, sep=_TAB_SEP, dtype=_DTYPE_MAP)
    orange_pivot = orange.pivot_table(
        values=[
            "Total Votes",
            "Turnout Percentage",
            "Registered Voters",
            "Ballots Cast",
        ],
        index=[".Precinct"],
        columns=["Choice Name1"],
        dropna=False,
    ).reset_index()

    # verify these values are equal before dropping one
    assert (
        orange_pivot[("Registered Voters", "No")]
        != orange_pivot[("Registered Voters", "Yes")]
    ).any() == False
    assert (
        orange_pivot[("Ballots Cast", "No")]
        != orange_pivot[("Ballots Cast", "Yes")]
    ).any() == False

    # set instead of renaming b/c of multi-level columns
    orange_pivot.columns = _COLUMN_NAMES

    # remove precinct 99999 which is used to report votes for
    # all precincts that have fewer than 10 voters
    orange_pivot = orange_pivot[
        orange_pivot["precinct_id"] != _AGGREGATE_PRECINCT_ID
    ].copy()

    orange_pivot = standardize_results_df(
        results_df=orange_pivot,
        county=_COUNTY,
    )

    orange = orange_pivot.copy()
    orange.head()
    return (orange,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Riverside
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Riverside"
    _DATA_FP = "inputs/counties/riverside/SOV_County_District Canvass_20251202134500057.xlsx"
    _PROP50_RESULTS_SHEET = "District Canvass"
    _SKIP_HEADER_ROWS = 7
    _TRUNCATE_AFTER = 920

    riverside = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    ).truncate(after=_TRUNCATE_AFTER)

    riverside = standardize_results_df(
        results_df=riverside,
        county=_COUNTY,
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Registered Voters": "registered_voters",
            # "Voters Cast": "total_votes", # vote cast may exceed exceed total votes
        },
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
def _(pd, standardize_results_df):
    _COUNTY = "Sacramento"
    _DATA_FP = "inputs/counties/sacramento/Results_bd6edf40-d97c-4b13-adc8-792cb842323e.xlsx"
    _PROP50_RESULTS_SHEET = "Precinct Results"
    _DTYPE = {"Precinct": str}
    _BALLOT_NAME_EXCLUDE_VALUES = ["Ballots Cast", "Over Votes", "Under Votes"]

    sacramento = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        dtype=_DTYPE,
    )

    # only use the rows with Yes and No results
    for _exclude_val in _BALLOT_NAME_EXCLUDE_VALUES:
        sacramento = sacramento[sacramento["Ballot Name"] != _exclude_val].copy()

    # make a pivot table to group yes and no votes per precinct together
    sacramento = sacramento.pivot_table(
        index="Precinct",
        columns="Ballot Name",
        values="Total",
        aggfunc="sum",
    )

    sacramento = sacramento.reset_index()

    sacramento = standardize_results_df(
        results_df=sacramento,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "No": "no_votes",
            "Yes": "yes_votes",
        },
    )
    sacramento["precinct_id"] = sacramento["precinct_id"].str.lstrip("0")
    sacramento.head()
    return (sacramento,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Benito
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "San Benito"
    _DATA_FP = "inputs/counties/san_benito/November 4, 2025 Special Election Statement of Vote - By Precinct.xlsx"
    _PROP50_RESULTS_SHEET = "Proposition 50"
    _SKIP_HEADER_ROWS = 2
    _SKIP_FOOTER_ROWS = 3
    _PRECINCT_ID_PATTERN = r"[a-zA-Z]\d{5}"
    _PRECINCT_EXCLUDE_VALUES = [
        "Countywide",
        "Electionwide",
        "Vote Centers",
        "Vote by Mail",
    ]

    san_benito = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )

    # remove countywide data and multiple lines per precinct (vote centers, vote by mail)
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        san_benito = san_benito[san_benito["Precinct"] != _exclude_val].copy()

    # backfill the data so that the vote counts are in the same rows as the precinct IDs
    san_benito = san_benito.bfill()
    san_benito = san_benito[san_benito["Precinct"] != "Total"].copy()

    san_benito = standardize_results_df(
        results_df=san_benito,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )
    san_benito = san_benito[
        san_benito["precinct_id"].str.match(_PRECINCT_ID_PATTERN)
    ].reset_index(drop=True)

    # standardize the case of the precinct_id column
    san_benito["precinct_id"] = san_benito["precinct_id"].str.upper()

    # remove duplicates
    san_benito = san_benito.drop_duplicates()

    san_benito.head()
    return (san_benito,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Bernardino
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "San Bernardino"
    _DATA_FP = "inputs/counties/san_bernardino/Report_SOVbyPrecinct.xlsx"
    _PROP50_RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 3
    _SKIP_FOOTER_ROWS = 8
    _PRECINT_ID_START_INDEX = (
        -7
    )  # trailing N digits represent matching ID in results
    _PRECINCT_EXCLUDE_VALUES = [
        "Electionwide",
        "Mail Ballot",
        "Polling Place",
        "Total",
    ]

    san_bernardino = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )

    # remove rows for formatting and voting method breakdown
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        san_bernardino = san_bernardino[
            san_bernardino["Precinct"] != _exclude_val
        ].copy()

    # backfill the data so that precincts and vote counts are on the same row
    san_bernardino = san_bernardino.bfill()

    san_bernardino = standardize_results_df(
        results_df=san_bernardino,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    san_bernardino["precinct_id"] = san_bernardino["precinct_id"].str[
        _PRECINT_ID_START_INDEX:
    ]

    san_bernardino = san_bernardino.reset_index(drop=True)
    san_bernardino.head()
    return (san_bernardino,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Diego
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "San Diego"
    _DATA_FP = "inputs/counties/san_diego/Statement of Votes Cast 202511.xls"
    _PROP50_RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 6
    _SKIP_FOOTER_ROWS = 5
    _VBM_PRECINCT_REGEX = r"^999"

    san_diego = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )

    san_diego = standardize_results_df(
        results_df=san_diego,
        county=_COUNTY,
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Total Votes": "total_votes",
            "Registered Voters": "registered_voters",
        },
    )

    san_diego["precinct_id"] = san_diego["precinct_id"].str.split(
        "-", expand=True
    )[1]

    san_diego = san_diego[
        ~san_diego["precinct_id"].str.match(_VBM_PRECINCT_REGEX)
    ].copy()
    san_diego.head()
    return (san_diego,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Francisco
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "San Francisco"
    _DATA_FP = "inputs/counties/san_francisco/sov.xlsx"
    _PROP50_RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 3
    _SKIP_FOOTER_ROWS = 8
    _PRECINCT_EXCLUDE_VALUES = ["Electionwide", "Election Day", "Vote by Mail"]

    san_francisco = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )

    # remove some extra rows and multiple rows per precinct (voting method breakdown)
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        san_francisco = san_francisco[
            san_francisco["Precinct"] != _exclude_val
        ].copy()

    # backfill the data so that the vote totals are on the same
    # rows as the precinct ids
    san_francisco = san_francisco.bfill()
    san_francisco = san_francisco[san_francisco["Precinct"] != "Total"].copy()

    san_francisco = standardize_results_df(
        results_df=san_francisco,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    # remove "PCT" and "MB" from precinct_id to match geographies
    san_francisco['precinct_id'] = san_francisco['precinct_id'].str.split(' ', expand=True)[1]

    san_francisco = san_francisco.reset_index(drop=True)
    san_francisco.head()
    return (san_francisco,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Joaquin
    """)
    return


@app.cell
def _(pd, pdfplumber):
    _PDF_FP = "inputs/counties/san_joaquin/November-4-2025-Statewide-Special-Election-Statement-of-the-Vote.pdf"
    _PROP50_PAGE_RANGE = (5, 10)


    def extract_san_joaquin_pdf():
        san_joaquin = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(_PDF_FP) as pdf:
            extracted_pages = []
            # just a few pages from the document are related to Prop 50
            prop_50_pages = pdf.pages[
                _PROP50_PAGE_RANGE[0] : _PROP50_PAGE_RANGE[1]
            ]

            for page in prop_50_pages:
                table = page.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            san_joaquin = pd.concat(extracted_pages)
        return san_joaquin
    return (extract_san_joaquin_pdf,)


@app.cell
def _(extract_san_joaquin_pdf, standardize_results_df):
    _COUNTY = "San Joaquin"
    _PRECINCT_ID_PATTERN = r"\d{7}"

    san_joaquin = extract_san_joaquin_pdf()

    san_joaquin = standardize_results_df(
        results_df=san_joaquin,
        county=_COUNTY,
        rename_column_map={
            0: "precinct_id",
            1: "registered_voters",
            2: "total_votes",
            3: "turnout",
            4: "yes_votes",
            5: "no_votes",
        },
    )

    san_joaquin = san_joaquin[
        san_joaquin["precinct_id"].str.match(_PRECINCT_ID_PATTERN)
    ].reset_index(drop=True)
    san_joaquin.head()
    return (san_joaquin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Luis Obispo
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "San Luis Obispo"
    _DATA_FP = "inputs/counties/san_luis_obispo/2025-special-official-sovc-split-by-precinct-excel.xlsx"
    _SKIP_HEADER_ROWS = 3
    _SKIP_FOOTER_ROWS = 8
    # List of "Precinct" values representing countywide totals, headers, or row types we want to exclude
    _PRECINCT_EXCLUDE_VALUES = [
        "Countywide",
        "Electionwide",
        "County",
        "Polling",
        "Vote by Mail",
    ]

    san_luis_obispo = pd.read_excel(
        _DATA_FP,
        sheet_name=1,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )

    # Remove rows where "Precinct" column matches any value in the exclusion list above
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        san_luis_obispo = san_luis_obispo[
            san_luis_obispo["Precinct"] != _exclude_val
        ].copy()

    # then backfill each precinct results so that the "Total" values are on the same
    # row as the precinct ID
    san_luis_obispo = san_luis_obispo.bfill()

    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "Total"
    ].copy()

    san_luis_obispo = standardize_results_df(
        results_df=san_luis_obispo,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            # data also has a Times Cast column which records all ballots cast including blank votes
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    san_luis_obispo = san_luis_obispo.reset_index(drop=True)
    san_luis_obispo.head()
    return (san_luis_obispo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Mateo
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "San Mateo"
    _DATA_FP = "inputs/counties/san_mateo/Precincts_18.csv"
    _SKIP_HEADER_ROWS = 2
    _DTYPE = {"Precinct": str}

    san_mateo_csv = pd.read_csv(
        _DATA_FP,
        skiprows=_SKIP_HEADER_ROWS,
        dtype=_DTYPE,
    )

    # since the YES and NO values are on two separate rows per precinct
    # we want to make a pivot table and get them together
    san_mateo = san_mateo_csv.pivot_table(
        index="Precinct", columns="Candidate Name", values="Votes", aggfunc="sum"
    )

    # join the pivot table and the csv data together so we can get some more
    # data from the source file csv such as turnout
    san_mateo = san_mateo.join(san_mateo_csv.set_index("Precinct"), on="Precinct")
    san_mateo = san_mateo.reset_index()

    san_mateo = standardize_results_df(
        results_df=san_mateo,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "NO": "no_votes",
            "YES": "yes_votes",
            "Voter Turnout": "turnout",
        },
    )

    # drop dupes produced in the join operations
    san_mateo = san_mateo.drop_duplicates()

    san_mateo = san_mateo.reset_index(drop=True)
    san_mateo.head()
    return (san_mateo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Barbara
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Santa Barbara"
    _DATA_FP = "inputs/counties/santa_barbara/sov-pct.xlsx"
    _PROP50_RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 3
    # Remove rows where "Electionwide" column is any of the specified values to drop
    _PRECINCT_EXCLUDE_VALUES = [
        "Poll",
        "Mail",
        "Cumulative",
        "Cumulative - Total",
        "Electionwide - Total",
        "Electionwide",
    ]

    santa_barbara = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        santa_barbara = santa_barbara[
            santa_barbara["Precinct"] != _exclude_val
        ].copy()

    # use the total row to backfill the data
    santa_barbara = santa_barbara.bfill()
    santa_barbara = santa_barbara[santa_barbara["Precinct"] != "Total"].copy()

    santa_barbara = standardize_results_df(
        results_df=santa_barbara,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    santa_barbara = santa_barbara.reset_index(drop=True)
    santa_barbara.head()
    return (santa_barbara,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Clara
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Santa Clara"
    _DATA_FP = "inputs/counties/santa_clara/detail.xlsx"
    _PROP50_RESULTS_SHEET = "3"
    _SKIP_HEADER_ROWS = 2

    santa_clara = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    santa_clara = standardize_results_df(
        results_df=santa_clara,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
            "Total": "total_votes",
            "Registered Voters": "registered_voters",
        },
    )

    # remove an extra aggregate row of data
    santa_clara = santa_clara[santa_clara["precinct_id"] != "Total:"].copy()

    # remove leading zeros in precinct_id
    santa_clara["precinct_id"] = santa_clara["precinct_id"].str.lstrip("0")

    santa_clara.head()
    return (santa_clara,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shasta
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Shasta"
    _DATA_FP = "inputs/counties/shasta/detail.xlsx"
    _PROP50_RESULTS_SHEET = "2"
    _SKIP_HEADER_ROWS = 2

    shasta = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )
    shasta = shasta[shasta["Precinct"] != "Total:"].copy()

    shasta = standardize_results_df(
        results_df=shasta,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
            "Registered Voters": "registered_voters",
        },
    )

    shasta = shasta.reset_index(drop=True)
    shasta.head()
    return (shasta,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sierra
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Sierra"
    _PDF_FP = "inputs/counties/sierra/Statement of Vote.pdf"


    def extract_sierra_pdf():
        sierra = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            _PDF_FP,
        ) as pdf:
            # only the first page has vote counts from Prop 50
            # just a few pages from the document are related to Prop 50
            table = pdf.pages[0].extract_table()
            # last entry is the aggregate results which is dropped
            sierra = pd.DataFrame(table[1:])[:-1]

        return sierra


    sierra = extract_sierra_pdf()

    sierra = standardize_results_df(
        results_df=sierra,
        county=_COUNTY,
        rename_column_map={
            0: "precinct_id",
            1: "yes_votes",
            2: "no_votes",
            10: "registered_voters",
            11: "turnout",
        },
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
def _(pd, standardize_results_df):
    _COUNTY = "Siskiyou"
    _DATA_FP = "inputs/counties/siskiyou/statementofvotescastrpt.xlsx"
    _PROP50_RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 3
    _SKIP_FOOTER_ROWS = 5
    _PRECINCT_EXCLUDE_VALUES = ["County", "Electionwide"]

    siskiyou = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        siskiyou = siskiyou[siskiyou["Precinct"] != _exclude_val].copy()

    siskiyou = standardize_results_df(
        results_df=siskiyou,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    ).reset_index(drop=True)

    siskiyou.head()
    return (siskiyou,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Solano
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Solano"
    _DATA_FP = "inputs/counties/solano/Precincts_19.csv"
    _SKIP_HEADER_ROWS = 2

    # read in the source file
    solano_csv = pd.read_csv(_DATA_FP, skiprows=_SKIP_HEADER_ROWS)

    # create a pivot table so we get closer to our desired structure
    solano = solano_csv.pivot_table(
        index="Precinct",
        columns="Candidate Name",
        values="Votes",
        aggfunc="sum",
    )

    # join the pivot table and the csv together so voter turnout
    _voter_turnout_series = solano_csv.set_index("Precinct")["Voter Turnout"]
    solano = solano.join(_voter_turnout_series, on="Precinct")
    solano = solano.reset_index()
    solano = solano.drop_duplicates()

    solano = standardize_results_df(
        results_df=solano,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "NO": "no_votes",
            "YES": "yes_votes",
            "Voter Turnout": "turnout",
        },
    )
    solano = solano.reset_index(drop=True)

    solano.head()
    return (solano,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sonoma
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Sonoma"
    _DATA_FP = "inputs/counties/sonoma/detail 2.xlsx"
    _PROP50_RESULTS_SHEET = "3"
    _SKIP_HEADER_ROWS = 2

    sonoma = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    sonoma = sonoma[sonoma["Precinct"] != "Total:"].copy()

    sonoma = standardize_results_df(
        results_df=sonoma,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            # determined by manual check column mapping for yes / no
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
            "Registered Voters": "registered_voters",
        },
    )

    sonoma = sonoma.reset_index(drop=True)
    sonoma.head()
    return (sonoma,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Stanislaus
    """)
    return


@app.cell
def _(pd, pdfplumber, standardize_results_df):
    _COUNTY = "Stanislaus"
    _PDF_FP = "inputs/counties/stanislaus/11-04-2025-sov.pdf"
    _PROP50_PAGE_RANGE = (6, 8)
    _PRECINCT_ID_PATTERN = r"\d{6}"


    def extract_stanislaus_pdf():
        stanislaus = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            _PDF_FP,
        ) as pdf:
            prop_50_pages = pdf.pages[
                _PROP50_PAGE_RANGE[0] : _PROP50_PAGE_RANGE[1]
            ]
            extracted_pages = [
                pd.DataFrame(page.extract_table()[1:]) for page in prop_50_pages
            ]
            stanislaus = pd.concat(extracted_pages)
        return stanislaus


    stanislaus = extract_stanislaus_pdf()

    stanislaus = standardize_results_df(
        results_df=stanislaus,
        county=_COUNTY,
        rename_column_map={
            0: "precinct_id",
            1: "registered_voters",
            # 2 is ballots cast
            3: "turnout",
            4: "yes_votes",
            5: "no_votes",
        },
    )

    stanislaus = stanislaus[
        stanislaus["precinct_id"].str.match(_PRECINCT_ID_PATTERN)
    ].reset_index(drop=True)
    stanislaus.head()
    return (stanislaus,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sutter
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Sutter"
    _DATA_FP = "inputs/counties/sutter/Statement Of Votes Cast - Countywide.xlsx"
    _PROP50_RESULTS_SHEET = "Sheet2"
    _SKIP_HEADER_ROWS = 3
    # Remove rows where "Electionwide" column matches any in the exclusion list
    _PRECINCT_EXCLUDE_VALUES = [
        "County",
        "Electionwide",
        "County - Total",
        "Cumulative",
        "Cumulative - Total",
        "Electionwide - Total",
        "VBM",
        "Polls",
        "Early Voting",
    ]

    sutter = pd.read_excel(
        _DATA_FP,
        sheet_name=_PROP50_RESULTS_SHEET,
        skiprows=_SKIP_HEADER_ROWS,
    )

    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        sutter = sutter[sutter["Precinct"] != _exclude_val].copy()

    sutter = sutter.bfill()
    sutter = sutter[sutter["Precinct"] != "Total"].copy()

    sutter = standardize_results_df(
        results_df=sutter,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "Registered \nVoters": "registered_voters",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
        },
    )

    sutter = sutter.reset_index(drop=True)
    sutter.head()
    return (sutter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tulare
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Tulare"
    _DATA_FP = (
        "inputs/counties/tulare/results/StatementOfVotesCastRPT_By_Precinct.xlsx"
    )
    _SKIP_HEADER_ROWS = 3

    tulare = pd.read_excel(_DATA_FP, sheet_name=1, skiprows=_SKIP_HEADER_ROWS)

    # Dedupe: filter only numeric "Precinct" entries, retain first instance of each
    is_precinct_id = tulare["Precinct"].str.isnumeric()
    tulare_headers_dropped = tulare[is_precinct_id].copy()
    expected_precinct_count = tulare_headers_dropped["Precinct"].nunique()
    tulare_deduped = tulare_headers_dropped.drop_duplicates(
        "Precinct", keep="first"
    )
    assert tulare_deduped["Precinct"].nunique() == expected_precinct_count

    tulare = tulare_deduped.dropna(axis=1, how="all", ignore_index=True).copy()

    tulare = standardize_results_df(
        results_df=tulare,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )

    tulare
    return (tulare,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Trinity

    Trinity organizes the precinct results per sheet, so this requires custom processing workflow.
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Trinity"
    _DATA_FP = (
        "inputs/counties/trinity/Final Precinct Results-12-2-2025 08-46-33 AM.xlsx"
    )
    _SKIP_HEADER_ROWS = 23
    _PRECINCT_SHEETS = [
        "Sheet2",
        "Sheet3",
        "Sheet4",
        "Sheet5",
        "Sheet6",
        "Sheet7",
        "Sheet8",
        "Sheet9",
        "Sheet10",
    ]


    def trinity_extract_df(df):
        PRECINCT_ID_CELL = (0, 0)
        YES_VOTES_CELL = (6, 20)
        NO_VOTES_CELL = (7, 20)
        TURNOUT_CELL = (0, 13)

        precinct_id = df.iloc[PRECINCT_ID_CELL]
        yes_votes = df.iloc[YES_VOTES_CELL]
        no_votes = df.iloc[NO_VOTES_CELL]
        turnout_str = df.iloc[TURNOUT_CELL]
        turnout = (
            turnout_str.split(" = ")[1].replace("%", "")
            if isinstance(turnout_str, str) and " = " in turnout_str
            else turnout_str
        )
        return {
            "precinct_id": precinct_id,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "total_votes": yes_votes + no_votes,
            "turnout": turnout,
        }


    def trinity_df():
        trinity = []
        for sheet in _PRECINCT_SHEETS:
            trinity_sheet_df = pd.read_excel(
                _DATA_FP,
                sheet_name=sheet,
                skiprows=_SKIP_HEADER_ROWS,
            )
            trinity_extracted = trinity_extract_df(trinity_sheet_df)
            trinity.append(trinity_extracted)

        trinity = pd.DataFrame(trinity)
        trinity = standardize_results_df(
            results_df=trinity,
            county=_COUNTY,
        )
        return trinity


    trinity = trinity_df()
    trinity.head()
    return (trinity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tuolumne
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Tuolumne"
    # read in excel file using the sheet titled "Sheet2" and skip 3 rows at the top and five at the end
    _DATA_FP = "inputs/counties/tuolumne/StatementOfVotesCastRPT.xlsx"
    _SKIP_HEADER_ROWS = 3
    _SKIP_FOOTER_ROWS = 5
    _PRECINCT_EXCLUDE_VALUES = ["County", "Electionwide"]

    tuolumne = pd.read_excel(
        _DATA_FP,
        sheet_name=1,
        skiprows=_SKIP_HEADER_ROWS,
        skipfooter=_SKIP_FOOTER_ROWS,
    )
    for _exclude_val in _PRECINCT_EXCLUDE_VALUES:
        tuolumne = tuolumne[tuolumne["Precinct"] != _exclude_val].copy()

    tuolumne = standardize_results_df(
        results_df=tuolumne,
        county=_COUNTY,
        rename_column_map={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
            "Registered \nVoters": "registered_voters",
        },
    )
    tuolumne = tuolumne.reset_index(drop=True)
    tuolumne.head()
    return (tuolumne,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ventura
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Ventura"
    _DATA_FP = "inputs/counties/ventura/2025.11.04-Statement-of-Votes-Precinct-Canvass.xlsx"
    _SKIP_HEADER_ROWS = 6
    _PRECINCT_ID_PATTERN = r"\d{7}"

    ventura = pd.read_excel(_DATA_FP, sheet_name=1, skiprows=_SKIP_HEADER_ROWS)

    ventura = standardize_results_df(
        results_df=ventura,
        county=_COUNTY,
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "Yes": "yes_votes",
            "No": "no_votes",
            "Total Votes": "total_votes",
            "Registered Voters": "registered_voters",
        },
    )

    ventura = ventura[
        ventura["precinct_id"].str.match(_PRECINCT_ID_PATTERN, na=False)
    ].reset_index(drop=True)

    ventura.head()
    return (ventura,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Yolo
    """)
    return


@app.cell
def _(EsriDumper, Path, json, pd, standardize_results_df):
    _COUNTY = "Yolo"
    _FEATURE_SERVER_URL = "https://services2.arcgis.com/RETsakmE0SJfZXCd/ArcGIS/rest/services/Election_Results_Nov_2025/FeatureServer/0"
    _CACHE_FP = Path("inputs/counties/yolo/yolo_precinct_results.json")

    if _CACHE_FP.exists():
        with open(_CACHE_FP, "r") as f:
            yolo_features = json.load(f)
    else:
        yolo_features = list(EsriDumper(_FEATURE_SERVER_URL))
        _CACHE_FP.parent.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_FP, "w") as f:
            json.dump(yolo_features, f)

    yolo = [
        {
            "precinct_id": feature["properties"]["PRECINCTID"],
            "no_votes": feature["properties"]["TOTALVOTES_1"],
            "yes_votes": feature["properties"]["TOTALVOTES_2"],
            "registered_voters": feature["properties"]["RegisteredVoters"],
        }
        for feature in yolo_features
    ]

    yolo = pd.DataFrame(yolo)
    yolo = standardize_results_df(
        results_df=yolo,
        county=_COUNTY,
    )
    yolo = yolo.reset_index(drop=True)
    yolo.head()
    return (yolo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Yuba
    """)
    return


@app.cell
def _(pd, standardize_results_df):
    _COUNTY = "Yuba"
    _DATA_FP = "inputs/counties/yuba/11_25_SOV.xlsx"
    _SKIP_HEADER_ROWS = 6
    _SKIP_FOOTER_ROWS = 3
    yuba_xlsx = pd.read_excel(
        _DATA_FP, skiprows=_SKIP_HEADER_ROWS, skipfooter=_SKIP_FOOTER_ROWS
    )

    # create a pivot table to add together the different voting methods in each precinct
    yuba_pt = yuba_xlsx.pivot_table(
        index="Unnamed: 0",
        values=["Yes", "No"],
        aggfunc="sum",
    ).reset_index()

    # join the pivot table and the csv together so we can get registered voters per precinct
    yuba = yuba_pt.merge(
        yuba_xlsx[["Unnamed: 0", "Registered Voters"]],
        on="Unnamed: 0",
        validate="1:m",
    )
    yuba = yuba.drop_duplicates()

    yuba = standardize_results_df(
        results_df=yuba,
        county=_COUNTY,
        rename_column_map={
            "Unnamed: 0": "precinct_id",
            "No": "no_votes",
            "Yes": "yes_votes",
            "Registered Voters": "registered_voters",
        },
    )

    yuba = yuba.reset_index(drop=True)
    yuba.head()
    return (yuba,)


if __name__ == "__main__":
    app.run()
