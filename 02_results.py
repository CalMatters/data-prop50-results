import marimo

__generated_with = "0.19.4"
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
    import re

    from esridump.dumper import EsriDumper
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pdfplumber
    return json, re, EsriDumper, mo, np, pd, pdfplumber


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
    combined = pd.concat(
        [
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
    ).reset_index(drop=True)
    combined.to_csv("outputs/results.csv", index=False)
    combined.head(None)
    return


@app.cell
def _():
    VOTE_COUNT_COLUMNS = ["yes_votes", "no_votes", "total_votes"]
    return (VOTE_COUNT_COLUMNS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(VOTE_COUNT_COLUMNS, clean_redacted_precincts, pd):
    ALAMEDA_PRECINCT_ID_PATTERN = r"\d{6}"
    ALAMEDA_HEADER_ROWS_N = 5
    alameda = pd.read_excel(
        "inputs/counties/alameda/Statement of Vote - Statewide Special Election.xlsx",
        sheet_name=1,
        skiprows=ALAMEDA_HEADER_ROWS_N,
    )

    # get rid of extra values associated with each precinct
    alameda = alameda[alameda["Unnamed: 1"] != "Vote by Mail"].copy()
    alameda = alameda[alameda["Unnamed: 1"] != "Election Day"].copy()

    # rename columns
    alameda = alameda.rename(
        columns={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # drop unncessary columns
    alameda = alameda.drop(
        columns=[
            "Unnamed: 1",
            "Registered Voters",
            "Voters Cast",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 8",
            "Unnamed: 10",
            "Over Votes",
            "Under Votes",
        ]
    )

    # remove the "%" from turnout column
    alameda["turnout"] = alameda["turnout"].str.replace("%", "")

    # remove rows where the precinct ID is not a six digit number
    alameda = alameda[
        alameda["precinct_id"].str.match(ALAMEDA_PRECINCT_ID_PATTERN, na=False)
    ].copy()

    alameda[VOTE_COUNT_COLUMNS] = alameda[VOTE_COUNT_COLUMNS].apply(
        clean_redacted_precincts
    )

    # get rid of the index column
    alameda = alameda.reset_index(drop=True)
    alameda["county"] = "Alameda"

    alameda.head(None)
    return (alameda,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Butte
    """)
    return


@app.cell
def _(pd):
    _PRECINCT_ID_PATTERN = r"\d{4}"


    def butte_df():
        csv = pd.read_excel(
            "inputs/counties/butte/detail.xlsx", sheet_name="2", skiprows=2
        )
        csv = csv.rename(
            columns={
                "Precinct": "precinct_id",
                "Total Votes": "no_votes",
                "Total Votes.1": "yes_votes",
                "Total": "total_votes",
            }
        )
        csv["county"] = "Butte"
        csv["turnout"] = round(
            (csv["total_votes"] / csv["Registered Voters"]) * 100, 1
        )
        csv = csv.drop(
            columns=[
                "Live",
                "Vote By Mail",
                "Registered Voters",
                "Provisional",
                "Live.1",
                "Vote By Mail.1",
                "Provisional.1",
            ],
        )
        # remove rows where the precinct_id is not a four digit number
        csv = csv[csv["precinct_id"].str.match(_PRECINCT_ID_PATTERN)].copy()
        return csv


    butte = butte_df()
    butte.head(None)
    return (butte,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calaveras
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def calaveras_df():
        all = []
        with pdfplumber.open(
            "inputs/counties/calaveras/Official Precinct Report-12-1-2025 01-27-49 PM.pdf"
        ) as pdf:
            for page in pdf.pages:
                d = {}
                d["precinct_id"] = page.crop((0, 135, 60, 160)).extract_text()
                d["yes_votes"] = int(
                    page.crop((532, 200, 556, 215)).extract_text().replace(",", "")
                )
                d["no_votes"] = int(
                    page.crop((532, 220, 556, 235)).extract_text().replace(",", "")
                )
                d["registered_voters"] = int(
                    page.crop((445, 140, 470, 155))
                    .extract_text()
                    .replace(",", "")
                    .replace("of", "")
                    .strip()
                )
                all.append(d)
        df = pd.DataFrame(all)
        df["total_votes"] = df["yes_votes"] + df["no_votes"]
        df["county"] = "Calaveras"
        return df


    calaveras = calaveras_df()
    calaveras.head(None)
    return (calaveras,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Colusa
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def colusa_df():
        colusa = None
        with pdfplumber.open("inputs/counties/colusa/precinct SOV.pdf") as pdf:
            extracted_pages = []
            prop_50_pages = pdf.pages[4:5]

            for page in prop_50_pages:
                cropped = page.crop((396, 50, 792, 612))
                table = cropped.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            colusa = pd.concat(extracted_pages)

        # rename columns
        colusa.columns = [
            "precinct_id",
            "yes_votes",
            "Yes_Blank",
            "no_votes",
            "No_Blank",
        ]

        # drop some empty columns that were part of the spreadsheet structure
        colusa.drop(columns=["Yes_Blank", "No_Blank"], inplace=True)

        # get rid of total rows
        colusa = colusa[colusa["precinct_id"] != "Electionwide - Total"].copy()

        # get rid of four values associated with each precinct
        colusa = colusa[colusa["precinct_id"] != "Electionwide"].copy()
        colusa = colusa[colusa["precinct_id"] != "Vote by Mail"].copy()
        colusa = colusa[colusa["precinct_id"] != "Election Day"].copy()

        # get rid of the total value row
        colusa = colusa[colusa["precinct_id"] != "California - Total"].copy()

        # some values are white space so replace that with None
        colusa = colusa.replace(r"^\s*$", None, regex=True)

        # backfill missing values
        colusa = colusa.bfill(limit=1)

        # and then drop the "Total" value rows that were used to backfill
        colusa = colusa[colusa["precinct_id"] != "Total"].copy()

        # don't forget to add the county
        colusa["county"] = "Colusa"

        # make sure vote columns are numbers
        colusa = colusa.astype({"yes_votes": int, "no_votes": int})

        # add total_votes column
        colusa["total_votes"] = colusa["yes_votes"] + colusa["no_votes"]

        # and get rid of the index column
        colusa = colusa.reset_index()
        colusa = colusa.drop(columns=["index"])

        return colusa


    colusa = colusa_df()
    colusa.head(None)
    return (colusa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Contra Costa
    """)
    return


@app.cell
def _(np, pd):
    def contra_costa_df():
        csv = pd.read_excel(
            "inputs/counties/contra_costa/StatementOfVotesCastRPT_ByPrecinct.xlsx",
            sheet_name="Sheet2",
            skiprows=3,
        )

        # add the county
        csv["county"] = "Contra Costa"

        # drop some columns we don't need
        csv = csv.drop(
            columns=[
                "Times Cast",
                "Unnamed: 3",
                "Precinct.1",
                "Unnamed: 6",
                "Unnamed: 8",
                "Unnamed: 10",
                "Unnamed: 11",
                "Unnamed: 12",
            ]
        )

        # there are four rows per precinct so let's drop two of them
        # "In-person" and "Vote By Mail"
        csv = csv[csv["Precinct"] != "In-Person"]
        csv = csv[csv["Precinct"] != "Vote By Mail"]

        # drop extraneous Cumalative records
        csv = csv[csv["Precinct"] != "Cumulative"].copy()

        # get rid of the first two rows
        csv = csv.drop([0, 1])

        # backfill the values from the rows where "Precinct" is "Total" to the rows
        # that have proper precinct IDs
        csv = csv.bfill(limit=1)

        # and now get rid of the total per precinct row
        csv = csv[csv["Precinct"] != "Total"]

        # remove county total rows
        csv = csv[csv["Precinct"] != "Contra Costa County - Total"]
        csv = csv[csv["Precinct"] != "Cumulative"]
        csv = csv[csv["Precinct"] != "Cumulative - Total"]
        csv = csv[csv["Precinct"] != "County - Total"]

        csv = csv.rename(
            columns={
                "Precinct": "precinct_id",
                "Yes\n ": "yes_votes",
                "No\n ": "no_votes",
                "Total Votes": "total_votes",
            }
        )

        # replaced masked values with 0 for turnout calculations
        csv.replace("****", np.nan, inplace=True)
        csv[["yes_votes", "no_votes", "total_votes"]] = csv[
            ["yes_votes", "no_votes", "total_votes"]
        ].astype(float)

        # and then add in a calculated turnout column
        csv["turnout"] = round(
            (csv["total_votes"] / csv["Registered \nVoters"]) * 100, 1
        )

        # make the index a column so we can drop it
        csv = csv.reset_index()

        # get rid of remaining columns
        csv = csv.drop(columns=["index", "Registered \nVoters"])

        return csv


    contra_costa = contra_costa_df()
    contra_costa.head(None)
    return (contra_costa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## El Dorado
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def el_dorado_df():
        el_dorado = None
        with pdfplumber.open(
            "inputs/counties/el_dorado/SOS - EDC - StatementOfVotestCastRPT-Precinct.pdf"
        ) as pdf:
            extracted_pages = []
            prop_50_pages = pdf.pages[26:47]

            for page in prop_50_pages:
                cropped = page.crop((396, 50, 792, 612))
                table = cropped.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            el_dorado = pd.concat(extracted_pages)

        # rename columns
        el_dorado.columns = [
            "precinct_id",
            "yes_votes",
            "Yes_Blank",
            "no_votes",
            "No_Blank",
            "total_votes",
        ]

        # drop some empty columns that were part of the spreadsheet structure
        el_dorado.drop(columns=["Yes_Blank", "No_Blank"], inplace=True)

        # get rid of total count rows
        el_dorado = el_dorado[
            el_dorado["precinct_id"] != "Electionwide - Total"
        ].copy()
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Cumulative"].copy()

        # get rid of four values associated with each precinct
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Mail"].copy()
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Vote Center"].copy()
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Election Day"].copy()
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Provisional"].copy()

        # some values are white space so replace that with None
        el_dorado = el_dorado.replace(r"^\s*$", None, regex=True)

        # backfill missing values
        el_dorado = el_dorado.bfill(limit=1)

        # and then drop the "Total" value rows that were used to backfill
        el_dorado = el_dorado[el_dorado["precinct_id"] != "Total"].copy()

        # don't forget to add the county
        el_dorado["county"] = "El Dorado"

        # and get rid of the index column
        el_dorado = el_dorado.reset_index()
        el_dorado = el_dorado.drop(columns=["index"])
        return el_dorado


    el_dorado = el_dorado_df()
    el_dorado.head(None)
    return (el_dorado,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fresno
    """)
    return


@app.cell
def _(np, pd):
    FRESNO_PROP50_RESULTS_SHEET = "Sheet3"
    FRESNO_HEADER_ROWS_N = 5
    fresno = pd.read_excel(
        "inputs/counties/fresno/statementofvotescastrpt-with-privacy.xlsx",
        sheet_name=FRESNO_PROP50_RESULTS_SHEET,
        skiprows=FRESNO_HEADER_ROWS_N,
    )

    # Remove extra row containing repeated or extraneous data
    # Remove extra row containing repeated or extraneous data
    EXTRANEOUS_ROW_IDENTIFIERS = [
        "Vote Center",
        "Vote by Mail",
        "County - Total",
        "Electionwide - Total",
    ]
    is_extra_row = fresno["Electionwide"].isin(
        EXTRANEOUS_ROW_IDENTIFIERS
    ) | fresno["Electionwide"].str.contains("Cumulative", na=False)
    fresno = fresno[~is_extra_row].copy()
    # and then backfill so that the total values are associated
    # with the rows with valid precinct ids
    fresno = fresno.bfill()

    # and then get rid of the "Total" rows
    fresno = fresno[fresno["Electionwide"] != "Total"].copy()

    # contents of unnamed columns is very clear in the source
    # spreadsheet and are unnamed because there are multiple
    # header rows. open source spreadsheet to verify
    fresno = fresno.rename(
        columns={
            "Electionwide": "precinct_id",
            "Unnamed: 7": "yes_votes",
            "Unnamed: 9": "no_votes",
        }
    )

    # and then drop everything else
    fresno = fresno.drop(
        columns=[
            "Unnamed: 1",
            "Unnamed: 2",  # registered voter columns
            "Unnamed: 3",
            "Unnamed: 4",
            "Unnamed: 5",
            "Electionwide.1",
            "Unnamed: 8",
            "Unnamed: 10",
            "Unnamed: 11",
            "Unnamed: 12",
            "Unnamed: 13",
        ]
    )

    # add county column
    fresno["county"] = "Fresno"

    # replace privacy protecting string values with NaN
    fresno["yes_votes"] = fresno["yes_votes"].replace("****", np.nan)
    fresno["no_votes"] = fresno["no_votes"].replace("****", np.nan)
    fresno["total_votes"] = fresno["yes_votes"] + fresno["no_votes"]

    # reset and drop index column
    fresno = fresno.reset_index(drop=True)

    fresno.head(None)
    return (fresno,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Glenn
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def glenn_df():
        glenn = None
        with pdfplumber.open(
            "inputs/counties/glenn/Statement of Votes 2025.pdf"
        ) as pdf:
            extracted_pages = []
            prop_50_pages = pdf.pages[13:41][::2]

            for page in prop_50_pages:
                cropped = page.crop((396, 50, 792, 612))
                table = cropped.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            glenn = pd.concat(extracted_pages)

        # rename columns
        glenn.columns = [
            "precinct_id",
            "yes_votes",
            "Yes_Blank",
            "no_votes",
            "No_Blank",
            "total_votes",
        ]

        # drop some empty columns that were part of the spreadsheet structure
        glenn.drop(columns=["Yes_Blank", "No_Blank"], inplace=True)

        # get rid of total rows
        glenn = glenn[glenn["precinct_id"] != "Electionwide - Total"].copy()

        # get rid of values associated with each precinct
        glenn = glenn[glenn["precinct_id"] != "Electionwide"].copy()
        glenn = glenn[glenn["precinct_id"] != "Vote by Mail"].copy()
        glenn = glenn[glenn["precinct_id"] != "Election Day"].copy()

        # some values are white space so replace that with None
        glenn = glenn.replace(r"^\s*$", None, regex=True)

        # backfill missing values
        glenn = glenn.bfill(limit=1)

        # and then drop the "Total" value rows that were used to backfill
        glenn = glenn[glenn["precinct_id"] != "Total"].copy()

        # don't forget to add the county
        glenn["county"] = "Glenn"

        # and get rid of the index column
        glenn = glenn.reset_index()
        glenn = glenn.drop(columns=["index"])
        return glenn


    glenn = glenn_df()
    glenn.head(None)
    return (glenn,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imperial
    """)
    return


@app.cell
def _(pd):
    def imperial_df():
        csv = pd.read_csv("inputs/counties/imperial/Precincts_4.csv", skiprows=2)
        prop_50 = csv[csv["Contest Name"] == "PROPOSITION 50"]

        pt = prop_50.pivot_table(
            index="Precinct",
            columns="Candidate Name",
            values="Votes",
            aggfunc="sum",
        )

        turnout = prop_50.groupby("Precinct")["Voter Turnout"].max()

        prop_50_altered = pt.merge(turnout, on="Precinct")
        prop_50_altered = prop_50_altered.reset_index().rename(
            columns={
                "Precinct": "precinct_id",
                "Voter Turnout": "turnout",
                "YES": "yes_votes",
                "NO": "no_votes",
            }
        )

        prop_50_altered["precinct_id"] = prop_50_altered[
            "precinct_id"
        ].str.replace("MB", "")
        prop_50_altered["turnout"] = prop_50_altered["turnout"].str.replace(
            "%", ""
        )

        prop_50_altered["county"] = "Imperial"
        prop_50_altered["total_votes"] = (
            prop_50_altered["yes_votes"] + prop_50_altered["no_votes"]
        )

        return prop_50_altered


    imperial = imperial_df()

    imperial.head(None)
    return (imperial,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inyo
    """)
    return


@app.cell
def _(np, pd):
    INYO_HEADERS_N = 5
    inyo = pd.read_excel(
        "inputs/counties/inyo/SOVC-Redacted (by precincts).xlsx",
        sheet_name=1,
        skiprows=INYO_HEADERS_N,
    )

    # get rid of some extra rows
    inyo = inyo[inyo["Electionwide"] != "Electionwide - Total"].copy()
    inyo = inyo[inyo["Electionwide"] != "Cumulative"].copy()
    inyo = inyo[inyo["Electionwide"] != "Cumulative - Total"].copy()
    inyo = inyo[inyo["Electionwide"] != "County - Total"].copy()

    # add a county column
    inyo["county"] = "Inyo"

    # rename some columns so that it's easier to work with
    # contents of unnamed columns is very clear in the
    # source spreadsheet and are unnamed because there
    # are multiple header rows
    inyo = inyo.rename(
        columns={
            "Electionwide": "precinct_id",
            "Unnamed: 6": "yes_votes",
            "Unnamed: 8": "no_votes",
            "Unnamed: 10": "total_votes",
        }
    )

    # and then drop other columns we aren't using
    inyo = inyo.drop(
        columns=[
            "Unnamed: 1",
            "Unnamed: 2",  # registered voters column
            "Unnamed: 3",
            "Unnamed: 4",
            "Electionwide.1",
            "Unnamed: 7",
            "Unnamed: 9",
            "Unnamed: 11",
        ]
    )

    # replace privacy masking "***" values with np.nan
    inyo["yes_votes"] = inyo["yes_votes"].replace("****", np.nan)
    inyo["no_votes"] = inyo["no_votes"].replace("****", np.nan)
    inyo["total_votes"] = inyo["total_votes"].replace("****", np.nan)

    # reset and drop index column
    inyo = inyo.reset_index(drop=True)

    inyo.head(None)
    return (inyo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kern
    """)
    return


@app.cell
def _(np, pd):
    # read the excel file using the "Sheet2" sheet, skip TK rows at the top and TK rows at the bottom
    KERN_HEADER_N = 3
    KERN_CUMULATIVE_FOOTER_N = 3
    kern = pd.read_excel(
        "inputs/counties/kern/StatementOfVotesCastRPT.xlsx",
        sheet_name=1,
        skiprows=KERN_HEADER_N,
        skipfooter=KERN_CUMULATIVE_FOOTER_N,
    )

    _KERN_PRECINCT_VALUES_TO_REMOVE = [
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

    # get rid of the first two rows that are presentational
    for value in _KERN_PRECINCT_VALUES_TO_REMOVE:
        kern = kern[kern["Precinct"] != value].copy()

    # drop columns we don't care about at all
    kern = kern.drop(
        columns=[
            "Times Cast",
            "Unnamed: 3",
            "Overvotes",
            "Precinct.1",
            "Unnamed: 7",
            "Unnamed: 9",
            "Unnamed: 11",
            "Unresolved\nWrite-In",
        ]
    )

    # replace masked values with np.nan so that we can do math calculations
    kern["Yes\n "] = kern["Yes\n "].replace("****", np.nan)
    kern["No\n "] = kern["No\n "].replace("****", np.nan)
    kern["Total Votes"] = kern["Total Votes"].replace("****", np.nan)

    # calculate turnout
    kern["turnout"] = (kern["Total Votes"] / kern["Registered \nVoters"]) * 100

    # now that turnout is calculated we can drop registered voters
    kern = kern.drop(columns=["Registered \nVoters"])

    # rename the columns to match our scheme
    kern = kern.rename(
        columns={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # add a county column
    kern["county"] = "Kern"

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
def _(pd, pdfplumber):
    _PROP50_PAGE_RANGE = (9, 12)


    def extract_kings_pdf():
        kings = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open("inputs/counties/kings/NOV 2025 SOV BOOK.pdf") as pdf:
            extracted_pages = []
            # just a few pages from the document are related to Prop 50
            prop_50_pages = pdf.pages[
                _PROP50_PAGE_RANGE[0] : _PROP50_PAGE_RANGE[1]
            ]

            for page in prop_50_pages:
                table = page.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            kings = pd.concat(extracted_pages)
        return kings


    # create a dataframe from the pdf
    kings = extract_kings_pdf()

    # there are rows for different types of voting
    # but we just want the "Total"
    kings = kings[kings[1] == "Total"].copy()

    # the precinct IDs all start with "1" so
    # filter rows to just those
    _PRECINCT_ID_PATTERN = r"1\{3}"
    kings = kings[kings[0].str.match(_PRECINCT_ID_PATTERN)].copy()

    # now that all the data has been extracted we need to rename
    # the columns in the dataframe. the mapping can be verified
    # by looking at the source PDF document
    _RENAME_COL_MAP = {
        0: "precinct_id",
        4: "turnout",
        5: "yes_votes",
        6: "no_votes",
    }
    kings = kings.rename(columns=_RENAME_COL_MAP)

    # we can drop columns we don't care about
    _DROP_COLUMNS = [
        1,  # Registered voters
        2,  # Ballots cast
        3,
        7,
        8,  # Misc.
    ]
    kings = kings.drop(columns=_DROP_COLUMNS)

    # add a county column
    kings["county"] = "Kings"

    # force yes_votes and no_votes to be numbers
    kings["yes_votes"] = pd.to_numeric(kings["yes_votes"], errors="coerce")
    kings["no_votes"] = pd.to_numeric(kings["no_votes"], errors="coerce")

    # and add a total_votes
    kings["total_votes"] = kings["yes_votes"] + kings["no_votes"]

    # remove " %" from the turnout column
    kings["turnout"] = kings["turnout"].str.replace(" %", "")

    # and remove the index
    kings = kings.reset_index(drop=True)

    kings.head(None)
    return (kings,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lake
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def extract_lake_pdf():
        lake = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            "inputs/counties/lake/Statement of Votes12022025.pdf"
        ) as pdf:
            # just a few pages from the document are related to Prop 50
            prop_50_page = pdf.pages[0]
            table = prop_50_page.extract_table()
            lake = pd.DataFrame(table[1:])

        return lake


    # create a dataframe from the pdf
    lake = extract_lake_pdf()

    # remove some extra rows at the end of the dataframe
    lake = lake[lake[0] != "Vote by Mail Totals"].copy()
    lake = lake[lake[0] != "Election Day Voting Totals"].copy()
    lake = lake[lake[0] != "Grand Totals"].copy()

    # now that all the data has been extracted we need to rename
    # the columns in the dataframe. the mapping can be verified
    # by looking at the source PDF document
    lake = lake.rename(
        columns={0: "precinct_id", 3: "turnout", 4: "yes_votes", 5: "no_votes"}
    )

    # we can drop columns we don't care about
    # column with an index of 1 is "Registration"
    # column with an index of 2 is "Ballots Cast"
    lake = lake.drop(columns=[1, 2])

    # # add a county column
    lake["county"] = "Lake"

    # force yes_votes and no_votes to be numbers
    lake["yes_votes"] = pd.to_numeric(lake["yes_votes"], errors="coerce")
    lake["no_votes"] = pd.to_numeric(lake["no_votes"], errors="coerce")

    # and add a total_votes
    lake["total_votes"] = lake["yes_votes"] + lake["no_votes"]

    # and remove the index
    lake = lake.reset_index(drop=True)

    lake.head(None)
    return (lake,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Los Angeles
    """)
    return


@app.cell
def _(np, pd):
    LOS_ANGELES_HEADER_N = 2
    los_angeles = pd.read_excel(
        "inputs/counties/los_angeles/4337_final_svc_excel/STATE_MEASURE_50_11-04-25_by_Precinct_4337-bmc9985.xls",
        skiprows=LOS_ANGELES_HEADER_N,
    )

    # remove rows for individual voting methods
    los_angeles = los_angeles[los_angeles["TYPE"] == "TOTAL"].copy()

    # rename columns to match our scheme
    los_angeles = los_angeles.rename(
        columns={"PRECINCT": "precinct_id", "YES": "yes_votes", "NO": "no_votes"}
    )

    # calculate total votes
    los_angeles["total_votes"] = los_angeles["yes_votes"] + los_angeles["no_votes"]

    # because there are precincts with 0 registered voters
    # and we can't divide by zero first we have to replace
    # all of the 0s with np.nan
    los_angeles["REGISTRATION"] = los_angeles["REGISTRATION"].replace(0, np.nan)
    # and then calculate turnout
    los_angeles["turnout"] = (
        los_angeles["total_votes"] / los_angeles["REGISTRATION"]
    ) * 100

    # drop some columns we know we won't need
    los_angeles = los_angeles.drop(
        columns=[
            "LOCATION",
            "SERIAL",
            "REGISTRATION",
            "BALLOT GROUP",
            "VOTE BY MAIL ONLY",
            "TYPE",
            "BALLOTS CAST",
            "Unnamed: 10",
        ]
    )

    # add a county column
    los_angeles["county"] = "Los Angeles"

    # drop the index
    los_angeles = los_angeles.reset_index(drop=True)

    los_angeles.head(None)
    return (los_angeles,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Madera
    """)
    return


@app.cell
def _(np, pd):
    MADERA_PRECINCT_RESULTS_SHEET = "SOV by Precinct"
    MADERA_HEADER_N = 7
    PRECINCT_ID_FORMAT = r"^\d{4}$"
    madera = pd.read_excel(
        "inputs/counties/madera/Statement-of-Votes-CastXLSX-November-4-2025-1.xlsx",
        sheet_name=MADERA_PRECINCT_RESULTS_SHEET,
        skiprows=MADERA_HEADER_N,
    )

    # remove extra rows
    madera = madera[madera["Unnamed: 1"] != "Vote Center"].copy()
    madera = madera[madera["Unnamed: 1"] != "Vote by Mail"].copy()

    # rename columns we care about
    madera = madera.rename(
        columns={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "Yes": "yes_votes",
            "No": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # drop columns
    madera = madera.drop(
        columns=[
            "Unnamed: 1",
            "Registered Voters",
            "Voters Cast",
            "Unnamed: 5",
            "Unnamed: 8",
            "Over Votes",
            "Under Votes",
        ]
    )

    # remove % from turnout column
    madera["turnout"] = madera["turnout"].str.replace("%", "")

    # replace privacy masking *** with np.nan
    madera["yes_votes"] = madera["yes_votes"].replace("***", np.nan)
    madera["no_votes"] = madera["no_votes"].replace("***", np.nan)
    madera["total_votes"] = madera["total_votes"].replace("***", np.nan)

    madera = madera[
        madera["precinct_id"]
        .astype(str)
        .str.strip()
        .str.match(PRECINCT_ID_FORMAT, na=True)
    ]

    # reset and drop index column
    madera = madera.reset_index(drop=True)

    # add county column
    madera["county"] = "Madera"

    madera.head(None)
    return (madera,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Marin
    """)
    return


@app.cell
def _(np, pd):
    marin = pd.read_excel(
        "inputs/counties/marin/11-25_SOVC.Final_.xlsx",
        sheet_name="Sheet4",
        skiprows=3,
    )

    # get rid of some extra rows
    marin = marin[marin["Precinct"] != "Countywide"].copy()
    marin = marin[marin["Precinct"] != "Countywide - Total"].copy()
    marin = marin[marin["Precinct"] != "Cumulative"].copy()
    marin = marin[marin["Precinct"] != "Cumulative - Total"].copy()
    marin = marin[marin["Precinct"] != "Electionwide"].copy()
    marin = marin[marin["Precinct"] != "Electionwide - Total"].copy()

    # add county column
    marin["county"] = "Marin"

    # rename some columns
    marin = marin.rename(
        columns={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
        }
    )

    # Convert 'Total Votes' and 'Registered \nVoters' columns to numeric, coercing any non-numeric values to NaN
    marin["Total Votes"] = pd.to_numeric(marin["Total Votes"], errors="coerce")
    marin["Registered \nVoters"] = pd.to_numeric(
        marin["Registered \nVoters"], errors="coerce"
    )

    # Calculate turnout, replacing division by zero with 0
    marin["turnout"] = marin["Total Votes"] / marin["Registered \nVoters"].replace(
        0, 1
    )
    marin["turnout"] = marin["turnout"].fillna(
        0
    )  # Handle cases where Registered Voters is NaN or null

    # replace masked values with nan
    marin = marin.replace('****', np.nan)


    # drop the remaining columns we don't care about, including the index
    marin = marin.reset_index(drop=True).drop(
        columns=[
            "Times Cast",
            "Registered \nVoters",
            "Unnamed: 3",
            "Precinct.1",
            "Unnamed: 6",
            "Unnamed: 8",
            "Total Votes",
            "Unresolved\nWrite-In",
            "Unnamed: 11",
        ]
    )

    marin.head(None)
    return (marin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Merced
    """)
    return


@app.cell
def _(pd):
    MERCED_PROP50_RESULTS_SHEET = "2"
    MERCED_HEADER_N = 2
    merced = pd.read_excel(
        "inputs/counties/merced/detail.xlsx",
        sheet_name=MERCED_PROP50_RESULTS_SHEET,
        skiprows=MERCED_HEADER_N,
    )

    # add turnout and county columns
    merced["turnout"] = (merced["Total"] / merced["Registered Voters"]) * 100
    merced["county"] = "Merced"

    # drop the columns we don't need
    merced = merced.drop(
        columns=[
            "Registered Voters",
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

    # now rename the columns, the first "Total Votes" is for Yes according to the source spreadsheet
    merced = merced.rename(
        columns={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
            "Total": "total_votes",
        }
    )

    merced.head(None)
    return (merced,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Monterey
    """)
    return


@app.cell
def _(np, pd):
    MONTEREY_PROP50_RESULTS_SHEET = "PrecinctCanvass"
    MONTEREY_HEADER_N = 5
    monterey = pd.read_excel(
        "inputs/counties/monterey/SOV_2025-11-04_ByPrecinct.xlsx",
        sheet_name=MONTEREY_PROP50_RESULTS_SHEET,
        skiprows=MONTEREY_HEADER_N,
    )

    # add county columns
    monterey["county"] = "Monterey"

    # drop all the rows that are individual voting methods

    monterey = monterey[monterey["Unnamed: 1"] == "Total"].copy()

    # drop the columns we don't need
    monterey = monterey.drop(
        columns=[
            "Unnamed: 1",
            "Registered Voters",
            "Voters Cast",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 8",
            "Unnamed: 10",
        ]
    )

    # now rename the columns
    monterey = monterey.rename(
        columns={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # replace masked values (***) with np.nan
    monterey["yes_votes"] = monterey["yes_votes"].replace("***", np.nan)
    monterey["no_votes"] = monterey["no_votes"].replace("***", np.nan)
    monterey["total_votes"] = monterey["total_votes"].replace("***", np.nan)

    # force yes_votes, no_votes, total_votes to be numbers
    monterey["yes_votes"] = pd.to_numeric(
        monterey["yes_votes"].str.replace(",", ""), errors="coerce"
    )
    monterey["no_votes"] = pd.to_numeric(
        monterey["no_votes"].str.replace(",", ""), errors="coerce"
    )
    monterey["total_votes"] = pd.to_numeric(
        monterey["total_votes"].str.replace(",", ""), errors="coerce"
    )

    # remove the "%" from the turnout column values
    monterey["turnout"] = monterey["turnout"].str.replace("%", "")

    # remove the index
    monterey = monterey.reset_index(drop=True)

    monterey.head(None)
    return (monterey,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Napa
    """)
    return


@app.cell
def _(pd, pdfplumber):
    _PROP50_END_PAGE = 6


    _PROP50_END_PAGE = 6


    def extract_napa_pdf():
        napa = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            "inputs/counties/napa/Statement of Votes Cast_202512031558433636.pdf"
        ) as pdf:
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

    # now that all the data has been extracted we need to rename
    # the columns in the dataframe. the mapping can be verified
    # by looking at the source PDF document
    napa = napa.rename(
        columns={
            0: "precinct_id",
            3: "turnout",
            4: "total_votes",
            5: "yes_votes",
            6: "no_votes",
        }
    )

    # we can drop columns we don't care about
    # column with an index of 1 is "Registered Voters"
    # column with an index of 2 is "Times Cast"
    napa = napa.drop(columns=[1, 2])

    # add a county column
    napa["county"] = "Napa"

    # force yes_votes, no_votes, total_votes to be numbers
    napa["yes_votes"] = pd.to_numeric(
        napa["yes_votes"].str.replace(",", ""), errors="coerce"
    )
    napa["no_votes"] = pd.to_numeric(
        napa["no_votes"].str.replace(",", ""), errors="coerce"
    )
    napa["total_votes"] = pd.to_numeric(
        napa["total_votes"].str.replace(",", ""), errors="coerce"
    )

    # remove the "%" from the turnout column
    napa["turnout"] = napa["turnout"].str.replace("%", "")

    # and remove the index
    napa = napa.reset_index(drop=True)

    napa.head(None)
    return (napa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orange

    Orange has a precinct with ID `99999`. The precinct's record says it has 976 registered voters with 430 votes cast. It has null value for turnout. It may be worth it to reach out to county to ask which voters are registered to this precinct. My guess is these are Americans voting from abroad.

    Orange results data has two different precinct identifiers. I determined which one to use by cross referencing with the counties precinct GIS file.
    """)
    return


@app.cell
def _(calculate_total_votes, pd):
    _DATA_FP = "./inputs/counties/orange/media.zip"
    _TAB_SEP = "\t"
    _DTYPE_MAP = {".Precinct": str, "Precinct ID": str}
    _COLUMN_NAMES = ["precinct_id", "no_votes", "yes_votes", "turnout", "to_drop"]

    orange = pd.read_csv(_DATA_FP, sep=_TAB_SEP, dtype=_DTYPE_MAP)
    orange = orange.pivot_table(
        values=["Total Votes", "Turnout Percentage"],
        index=[".Precinct"],
        columns=["Choice Name1"],
        dropna=False,
    ).reset_index()

    # Precinct 99999 should be the only precinct without turnout set
    # this precinct does not exist in geography file, so it will likely be dropped
    # assertion included b/c we pivot on the turnout records from the source data
    assert (
        orange[("Turnout Percentage", "No")]
        != orange[("Turnout Percentage", "Yes")]
    ).sum() == 1

    orange.columns = _COLUMN_NAMES
    orange = orange[orange.columns[:-1]].copy()

    orange["total_votes"] = calculate_total_votes(orange)
    orange["county"] = "Orange"


    orange
    return (orange,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sacramento
    """)
    return


@app.cell
def _(pd):
    SACRAMENTO_PROP50_RESULTS_SHEET = "Precinct Results"
    _READ_DTYPE = {"Precinct": str}
    sacramento = pd.read_excel(
        "inputs/counties/sacramento/Results_bd6edf40-d97c-4b13-adc8-792cb842323e.xlsx",
        sheet_name=SACRAMENTO_PROP50_RESULTS_SHEET,
        dtype=_READ_DTYPE,
    )

    # only use the rows with Yes and No results
    sacramento = sacramento[sacramento["Ballot Name"] != "Ballots Cast"].copy()
    sacramento = sacramento[sacramento["Ballot Name"] != "Over Votes"].copy()
    sacramento = sacramento[sacramento["Ballot Name"] != "Under Votes"].copy()

    # make a pivot table to group yes and no votes per precinct together
    sacramento = sacramento.pivot_table(
        index="Precinct",
        columns="Ballot Name",
        values="Total",
        aggfunc="sum",
    )

    # reset the index so the precinct ID is in a regular data column
    sacramento = sacramento.reset_index()

    # add a county column
    sacramento["county"] = "Sacramento"

    # rename the other columns to match our scheme
    sacramento = sacramento.rename(
        columns={"Precinct": "precinct_id", "No": "no_votes", "Yes": "yes_votes"}
    )

    # remove leading 00 from precinct_id
    sacramento["precinct_id"] = sacramento["precinct_id"].str.lstrip("0")

    # add total_votes column
    sacramento["total_votes"] = sacramento["no_votes"] + sacramento["yes_votes"]

    sacramento.head(None)
    return (sacramento,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Benito
    """)
    return


@app.cell
def _(pd):
    SAN_BENITO_PROP50_RESULTS_SHEET = "Proposition 50"
    SAN_BENITO_HEADER_N = 2
    SAN_BENITO_CUMULATIVE_FOOTER_N = 3
    _PRECINCT_PATTERN = r"[a-zA-Z]\d{5}"

    san_benito = pd.read_excel(
        "inputs/counties/san_benito/November 4, 2025 Special Election Statement of Vote - By Precinct.xlsx",
        sheet_name=SAN_BENITO_PROP50_RESULTS_SHEET,
        skiprows=SAN_BENITO_HEADER_N,
        skipfooter=SAN_BENITO_CUMULATIVE_FOOTER_N,
    )

    # remove two rows at the top that are countywide data
    san_benito = san_benito[san_benito["Precinct"] != "Countywide"].copy()
    san_benito = san_benito[san_benito["Precinct"] != "Electionwide"].copy()

    # there are multiple lines per precinct, remove those for vote centers and vote by mail
    san_benito = san_benito[san_benito["Precinct"] != "Vote Centers"].copy()
    san_benito = san_benito[san_benito["Precinct"] != "Vote by Mail"].copy()

    # backfill the data so that the vote counts are in the same rows as the precinct IDs
    san_benito = san_benito.bfill()

    # and then we can drop the total rows
    san_benito = san_benito[san_benito["Precinct"] != "Total"].copy()

    # calculate turnout
    san_benito["turnout"] = (
        san_benito["Total Votes"] / san_benito["Registered \nVoters"]
    ) * 100

    # drop columns we don't care about
    san_benito = san_benito.drop(
        columns=["Times Cast", "Registered \nVoters", "Unnamed: 3"]
    )
    # and rename the ones we do want to keep
    san_benito = san_benito.rename(
        columns={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    san_benito = san_benito[
        san_benito["precinct_id"].str.match(_PRECINCT_PATTERN)
    ].reset_index(drop=True)

    # finally add a county column
    san_benito["county"] = "San Benito"

    san_benito.head(None)
    return (san_benito,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Bernardino
    """)
    return


@app.cell
def _(np, pd):
    SAN_BERNARDINO_PROP50_RESULTS_SHEET = "Sheet2"
    SAN_BERNARDINO_HEADER_N = 3
    SAN_BERNARDINO_CUMULATIVE_FOOTER_N = 8
    _PRECINT_ID_START_INDEX = -7 # trailing N digits represent matching ID in results
    san_bernardino = pd.read_excel(
        "inputs/counties/san_bernardino/Report_SOVbyPrecinct.xlsx",
        sheet_name=SAN_BERNARDINO_PROP50_RESULTS_SHEET,
        skiprows=SAN_BERNARDINO_HEADER_N,
        skipfooter=SAN_BERNARDINO_CUMULATIVE_FOOTER_N,
    )

    # remove some rows that are in the source spreadsheet for formatting
    san_bernardino = san_bernardino[
        san_bernardino["Precinct"] != "Electionwide"
    ].copy()

    # and also get rid of rows that break down the voting method by precinct
    san_bernardino = san_bernardino[
        san_bernardino["Precinct"] != "Mail Ballot"
    ].copy()
    san_bernardino = san_bernardino[
        san_bernardino["Precinct"] != "Polling Place"
    ].copy()

    # backfill the data so that precincts and vote counts are on the same row
    san_bernardino = san_bernardino.bfill()

    # and then get rid of the total rows so we're left with just precincts
    san_bernardino = san_bernardino[san_bernardino["Precinct"] != "Total"].copy()

    # replace masked values with np.nan so we can calculate turnout
    san_bernardino["YES\n "] = san_bernardino["YES\n "].replace("****", np.nan)
    san_bernardino["NO\n "] = san_bernardino["NO\n "].replace("****", np.nan)
    san_bernardino["Total Votes"] = san_bernardino["Total Votes"].replace(
        "****", np.nan
    )
    san_bernardino["turnout"] = (
        san_bernardino["Total Votes"] / san_bernardino["Registered \nVoters"]
    ) * 100

    # drop some columns we don't care about
    san_bernardino = san_bernardino.drop(
        columns=[
            "Registered \nVoters",
            "Times Cast",
            "Unnamed: 3",
            "Precinct.1",
            "Unnamed: 6",
            "Unnamed: 8",
            "Unnamed: 10",
            "Unnamed: 11",
            "Unnamed: 12",
        ]
    )

    # rename columns
    san_bernardino = san_bernardino.rename(
        columns={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # adjust the precinct id to better match the geography
    san_bernardino["precinct_id"] = san_bernardino["precinct_id"].str[
        _PRECINT_ID_START_INDEX:
    ]

    # add county column
    san_bernardino["county"] = "San Bernardino"

    # and remove index
    san_bernardino = san_bernardino.reset_index(drop=True)

    san_bernardino.head(None)
    return (san_bernardino,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Diego
    """)
    return


@app.cell
def _(np, pd):
    SAN_DIEGO_PROP50_RESULTS_SHEET = "Sheet2"
    SAN_DIEGO_HEADER_N = 6
    SAN_DIEGO_CUMULATIVE_FOOTER_N = 5

    san_diego = pd.read_excel(
        "inputs/counties/san_diego/Statement of Votes Cast 202511.xls",
        sheet_name=SAN_DIEGO_PROP50_RESULTS_SHEET,
        skiprows=SAN_DIEGO_HEADER_N,
        skipfooter=SAN_DIEGO_CUMULATIVE_FOOTER_N,
    )

    # replace masked values with np.nan so we can calculate turnout
    san_diego["YES"] = san_diego["YES"].replace("***", np.nan)
    san_diego["NO"] = san_diego["NO"].replace("***", np.nan)
    san_diego["Total Votes"] = san_diego["Total Votes"].replace("***", np.nan)

    # replace "%" in turnout values
    san_diego["Turnout (%)"] = san_diego["Turnout (%)"].str.replace("%", "")

    # drop some columns we don't care about
    san_diego = san_diego.drop(
        columns=[
            "Unnamed: 1",
            "Registered Voters",
            "Voters Cast",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 8",
            "Unnamed: 10",
        ]
    )

    # rename columns
    san_diego = san_diego.rename(
        columns={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",
            "YES": "yes_votes",
            "NO": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # alter the precinct ID format to match with the geography
    san_diego['precinct_id'] = san_diego['precinct_id'].str.split('-', expand=True)[1]

    san_diego_vote_by_mail_precinct_regex = r"^999"

    # remove vote-by-mail (VBM) result rows since those won't match geography
    san_diego = san_diego[
        ~san_diego["precinct_id"].str.match(san_diego_vote_by_mail_precinct_regex)
    ].copy()

    # add county column
    san_diego["county"] = "San Diego"

    san_diego.head(None)
    return (san_diego,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Francisco
    """)
    return


@app.cell
def _(pd):
    SAN_FRANCISCO_PROP50_RESULTS_SHEET = "Sheet2"
    SAN_FRANCISCO_HEADER_N = 3
    SAN_FRANCISCO_CUMULATIVE_FOOTER_N = 8

    san_francisco = pd.read_excel(
        "inputs/counties/san_francisco/sov.xlsx",
        sheet_name=SAN_FRANCISCO_PROP50_RESULTS_SHEET,
        skiprows=SAN_FRANCISCO_HEADER_N,
        skipfooter=SAN_FRANCISCO_CUMULATIVE_FOOTER_N,
    )

    # remove some extra rows
    san_francisco = san_francisco[
        san_francisco["Precinct"] != "Electionwide"
    ].copy()

    # there are multiple rows per precinct, one per voting method
    # remove them except for the total votes values
    san_francisco = san_francisco[
        san_francisco["Precinct"] != "Election Day"
    ].copy()
    san_francisco = san_francisco[
        san_francisco["Precinct"] != "Vote by Mail"
    ].copy()

    # backfill the data so that the vote totals are on the same
    # rows as the precinct ids
    san_francisco = san_francisco.bfill()

    # and then get rid of the "Total" rows so we're just left with precinct data
    san_francisco = san_francisco[san_francisco["Precinct"] != "Total"].copy()

    # calculate turnout per precinct
    san_francisco["turnout"] = (
        san_francisco["Total Votes"] / san_francisco["Registered \nVoters"]
    ) * 100

    # drop the columns we don't want
    san_francisco = san_francisco.drop(
        columns=[
            "Registered \nVoters",
            "Undervotes",
            "Unnamed: 3",
            "Overvotes",
            "Precinct.1",
            "Unnamed: 7",
            "Unnamed: 9",
            "Unnamed: 11",
        ]
    )

    # rename columns to match our schema
    san_francisco = san_francisco.rename(
        columns={
            "Precinct": "precinct_id",
            "Yes\n ": "yes_votes",
            "No\n ": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # add a county column
    san_francisco["county"] = "San Francisco"

    # get rid of the index
    san_francisco = san_francisco.reset_index(drop=True)

    san_francisco.head(None)
    return (san_francisco,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Joaquin
    """)
    return


@app.cell
def _(pd, pdfplumber):
    _PROP50_PAGE_RANGE = (5, 10)


    def extract_san_joaquin_pdf():
        san_joaquin = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            "inputs/counties/san_joaquin/November-4-2025-Statewide-Special-Election-Statement-of-the-Vote.pdf"
        ) as pdf:
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


    san_joaquin = extract_san_joaquin_pdf()

    # now that all the data has been extracted we need to rename
    # the columns in the dataframe. the mapping can be verified
    # by looking at the source PDF document
    san_joaquin = san_joaquin.rename(
        columns={0: "precinct_id", 3: "turnout", 4: "yes_votes", 5: "no_votes"}
    )

    # we can drop columns we don't care about
    # column with an index of 1 is "Registered Voters"
    # column with an index of 2 is "Ballots Cast"
    san_joaquin = san_joaquin.drop(columns=[1, 2])

    # add a county column
    san_joaquin["county"] = "San Joaquin"

    # force yes_votes and no_votes to be numbers
    san_joaquin["yes_votes"] = pd.to_numeric(
        san_joaquin["yes_votes"].str.replace(",", ""), errors="coerce"
    )
    san_joaquin["no_votes"] = pd.to_numeric(
        san_joaquin["no_votes"].str.replace(",", ""), errors="coerce"
    )

    # and add a total_votes
    san_joaquin["total_votes"] = san_joaquin["yes_votes"] + san_joaquin["no_votes"]

    _PRECINCT_ID_PATTERN = r"\d{7}"
    san_joaquin = san_joaquin[
        san_joaquin["precinct_id"].str.match(_PRECINCT_ID_PATTERN)
    ].reset_index(drop=True)

    san_joaquin.head(None)
    return (san_joaquin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Luis Obispo
    """)
    return


@app.cell
def _(np, pd):
    SLO_HEADER_N = 3
    SLO_CUMULATIVE_FOOTER_N = 8
    san_luis_obispo = pd.read_excel(
        "inputs/counties/san_luis_obispo/2025-special-official-sovc-split-by-precinct-excel.xlsx",
        sheet_name=1,
        skiprows=SLO_HEADER_N,
        skipfooter=SLO_CUMULATIVE_FOOTER_N,
    )

    # get rid of the first three rows that are county wide results or headers
    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "Countywide"
    ].copy()
    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "Electionwide"
    ].copy()
    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "County"
    ].copy()

    # each precinct has results for polling, vote by mail, and total - we just want the total row
    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "Polling"
    ].copy()
    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "Vote by Mail"
    ].copy()

    # then backfill each precinct results so that the "Total" values are on the same
    # row as the precinct ID
    san_luis_obispo = san_luis_obispo.bfill()

    # and then get rid of the "Total" rows
    san_luis_obispo = san_luis_obispo[
        san_luis_obispo["Precinct"] != "Total"
    ].copy()

    # replace masked values with np.nan
    san_luis_obispo["YES\n "] = san_luis_obispo["YES\n "].replace("****", np.nan)
    san_luis_obispo["NO\n "] = san_luis_obispo["NO\n "].replace("****", np.nan)
    san_luis_obispo["Total Votes"] = san_luis_obispo["Total Votes"].replace(
        "****", np.nan
    )

    # add "county" and "turnout columns"
    san_luis_obispo["county"] = "San Luis Obispo"
    san_luis_obispo["turnout"] = (
        san_luis_obispo["Total Votes"] / san_luis_obispo["Registered \nVoters"]
    ) * 100

    # and then drop the columns we don't want to keep
    san_luis_obispo = san_luis_obispo.drop(
        columns=[
            "Times Cast",
            "Registered \nVoters",
            "Unnamed: 3",
            "Undervotes",
            "Overvotes",
            "Precinct.1",
            "Unnamed: 8",
            "Unnamed: 10",
            "Unnamed: 11",
        ]
    )

    # and rename the ones we do want to keep
    san_luis_obispo = san_luis_obispo.rename(
        columns={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # reset the index
    san_luis_obispo = san_luis_obispo.reset_index(drop=True)

    san_luis_obispo.head(None)
    return (san_luis_obispo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## San Mateo
    """)
    return


@app.cell
def _(pd):
    # read in the file, skip the first two rows, and make sure the "Precinct" column is a string
    SAN_MATEO_HEADER_N = 2
    san_mateo_csv = pd.read_csv(
        "inputs/counties/san_mateo/Precincts_18.csv",
        skiprows=SAN_MATEO_HEADER_N,
        dtype={"Precinct": str},
    )

    # since the YES and NO values are on two separate rows per precinct
    # we want to make a pivot table and get them together
    san_mateo = san_mateo_csv.pivot_table(
        index="Precinct", columns="Candidate Name", values="Votes", aggfunc="sum"
    )

    # join the pivot table and the csv data together so we can get some more
    # data from the source file csv such as turnout
    san_mateo = san_mateo.join(san_mateo_csv.set_index("Precinct"), on="Precinct")

    # rename the columns we care about
    san_mateo = san_mateo.reset_index().rename(
        columns={
            "Precinct": "precinct_id",
            "NO": "no_votes",
            "YES": "yes_votes",
            "Voter Turnout": "turnout",
        }
    )

    # and drop the rest
    san_mateo = san_mateo.drop(columns=["Contest Name", "Candidate Name", "Votes"])

    # the join created duplicate rows so we want to get rid of those too
    san_mateo = san_mateo.drop_duplicates()

    # let's add columns: county and total_votes
    san_mateo["county"] = "San Mateo"
    san_mateo["total_votes"] = san_mateo["no_votes"] + san_mateo["yes_votes"]

    # and get rid of the % in turnout
    san_mateo["turnout"] = san_mateo["turnout"].str.replace("%", "")

    # and finally get rid of the index
    san_mateo = san_mateo.reset_index(drop=True)

    san_mateo.head(None)
    return (san_mateo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Barbara
    """)
    return


@app.cell
def _(np, pd):
    santa_barbara = pd.read_excel(
        "inputs/counties/santa_barbara/sov-pct.xlsx",
        sheet_name="Sheet2",
        skiprows=5,
    )

    # get rid of some extra rows
    santa_barbara = santa_barbara[santa_barbara["Electionwide"] != "Poll"].copy()
    santa_barbara = santa_barbara[santa_barbara["Electionwide"] != "Mail"].copy()
    santa_barbara = santa_barbara[
        santa_barbara["Electionwide"] != "Cumulative"
    ].copy()
    santa_barbara = santa_barbara[
        santa_barbara["Electionwide"] != "Cumulative - Total"
    ].copy()
    santa_barbara = santa_barbara[
        santa_barbara["Electionwide"] != "Electionwide - Total"
    ].copy()

    # use the total row to backfill the data
    santa_barbara = santa_barbara.bfill()

    # and then get rid of the total row
    santa_barbara = santa_barbara[santa_barbara["Electionwide"] != "Total"].copy()

    # drop some columns we don't care about
    santa_barbara = santa_barbara.drop(
        columns=[
            "Unnamed: 1",
            "Unnamed: 2",  # registered voters per precinct
            "Unnamed: 3",
            "Electionwide.1",
            "Unnamed: 6",
            "Unnamed: 8",
            "Unnamed: 9",
            "Unnamed: 10",
            "Unnamed: 11",
        ]
    )

    # rename columns to be human-readable
    santa_barbara.columns = [
        "precinct_id",
        "yes_votes",
        "no_votes",
    ]

    # get rid of index
    santa_barbara = santa_barbara.reset_index().drop(columns=["index"])

    santa_barbara["yes_votes"] = santa_barbara["yes_votes"].replace("****", np.nan)
    santa_barbara["no_votes"] = santa_barbara["no_votes"].replace("****", np.nan)
    santa_barbara["county"] = "Santa Barbara"
    # show all of the data
    santa_barbara.head(None)
    return (santa_barbara,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Santa Clara
    """)
    return


@app.cell
def _(pd):
    SANTA_CLARA_PROP50_RESULTS_SHEET = "3"
    SANTA_CLARA_HEADER_N = 2
    santa_clara = pd.read_excel(
        "inputs/counties/santa_clara/detail.xlsx",
        sheet_name=SANTA_CLARA_PROP50_RESULTS_SHEET,
        skiprows=SANTA_CLARA_HEADER_N,
    )

    # rename the columns we care about
    # "Total Votes" is for "Yes" and "Total Votes.1" is for "No"
    # which you can verify with the grouped multi-index header in the source spreadsheet
    santa_clara = santa_clara.rename(
        columns={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
            "Total": "total_votes",
        }
    )

    # calculate turnout, it's more than 100% in some precincts and jeremia called
    # to ask them to explain and they're going to call him back
    santa_clara["turnout"] = (
        santa_clara["total_votes"] / santa_clara["Registered Voters"]
    ) * 100

    # and then drop columns we don't need
    santa_clara = santa_clara.drop(
        columns=[
            "Registered Voters",
            "Election Day",
            "Vote By Mail",
            "Election Day.1",
            "Vote By Mail.1",
        ]
    )

    # and add a county column
    santa_clara["county"] = "Santa Clara"

    santa_clara.head(None)
    return (santa_clara,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shasta
    """)
    return


@app.cell
def _(pd):
    SHASTA_PROP50_SHEET = "2"
    SHASTA_HEADER_N = 2
    shasta = pd.read_excel(
        "inputs/counties/shasta/detail.xlsx",
        sheet_name=SHASTA_PROP50_SHEET,
        skiprows=SHASTA_HEADER_N,
    )
    # column renaming determined by looking at the source
    # spreadsheet, which has multiple header rows
    shasta = shasta.rename(
        columns={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
        }
    )
    shasta = shasta[shasta["precinct_id"] != "Total:"].copy()
    shasta["county"] = "Shasta"
    shasta["turnout"] = (shasta["Total"] / shasta["Registered Voters"]) * 100
    shasta = shasta.reset_index(drop=True).drop(
        columns=[
            "Registered Voters",
            "Election Day",
            "Vote by  Mail",
            "Election Day.1",
            "Vote by  Mail.1",
            "Total",
        ]
    )
    shasta.head(None)
    return (shasta,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sierra
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def extract_sierra_pdf():
        sierra = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            "inputs/counties/sierra/Statement of Vote.pdf"
        ) as pdf:
            # only the first page has vote counts from Prop 50
            # just a few pages from the document are related to Prop 50
            table = pdf.pages[0].extract_table()
            # last entry is the aggregate results which is dropped
            sierra = pd.DataFrame(table[1:])[:-1]

        return sierra


    sierra = extract_sierra_pdf()

    # now that all the data has been extracted we need to rename
    # the columns in the dataframe. the mapping can be verified
    # by looking at the source PDF document
    sierra = sierra.rename(
        columns={0: "precinct_id", 1: "yes_votes", 2: "no_votes", 11: "turnout"}
    )

    # drop columns that are not needed for Prop 50 results
    _DROP_COLUMNS = [
        3,  # Cast Votes
        4,  # Undervotes
        5,  # Overvotes
        6,  # Rejected write in votes
        7,  # Unresolved write in votes
        8,  # Vote-By-Mail Ballots Cast
        9,  # Total Ballots Cast
        10,  # Registered Voters
    ]
    sierra = sierra.drop(columns=_DROP_COLUMNS)

    # add a county column
    sierra["county"] = "Sierra"

    # force yes_votes and no_votes to be numbers
    sierra["yes_votes"] = pd.to_numeric(
        sierra["yes_votes"].str.replace(",", ""), errors="coerce"
    )
    sierra["no_votes"] = pd.to_numeric(
        sierra["no_votes"].str.replace(",", ""), errors="coerce"
    )

    # calculate total votes
    sierra["total_votes"] = sierra["yes_votes"] + sierra["no_votes"]

    # remove the "%" from the turnout column
    sierra["turnout"] = sierra["turnout"].str.replace("%", "")

    sierra.head(None)
    return (sierra,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Siskiyou
    """)
    return


@app.cell
def _(pd):
    def siskiyou_df():
        siskiyou = pd.read_excel(
            "inputs/counties/siskiyou/statementofvotescastrpt.xlsx",
            sheet_name="Sheet2",
            skiprows=3,
            skipfooter=5,
        )
        siskiyou = siskiyou.drop(
            columns=[
                "Times Cast",
                "Unnamed: 3",
                "Precinct.1",
                "Unnamed: 6",
                "Unnamed: 8",
                "Unresolved\nWrite-In",
                "Unnamed: 11",
            ]
        ).rename(
            columns={
                "Precinct": "precinct_id",
                "YES\n ": "yes_votes",
                "NO\n ": "no_votes",
                "Total Votes": "total_votes",
            }
        )
        siskiyou = siskiyou[siskiyou["precinct_id"] != "County"].copy()
        siskiyou = siskiyou[siskiyou["precinct_id"] != "Electionwide"].copy()
        siskiyou["turnout"] = (
            siskiyou["total_votes"] / siskiyou["Registered \nVoters"]
        ) * 100
        siskiyou = siskiyou.reset_index().drop(
            columns=["index", "Registered \nVoters"]
        )
        siskiyou["county"] = "Siskiyou"
        return siskiyou


    siskiyou = siskiyou_df()
    siskiyou.head(None)
    return (siskiyou,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Solano
    """)
    return


@app.cell
def _(pd):
    def solano_df():
        # read in the source file
        solano_csv = pd.read_csv(
            "inputs/counties/solano/Precincts_19.csv", skiprows=2
        )
        # create a pivot table so we get closer to our desired structure
        solano = solano_csv.pivot_table(
            index="Precinct",
            columns="Candidate Name",
            values="Votes",
            aggfunc="sum",
        )
        # join the pivot table and the csv together so we can get some more
        # data from the source file csv such as turnout
        solano = solano.join(solano_csv.set_index("Precinct"), on="Precinct")
        # rename the columns
        solano = (
            solano.reset_index()
            .rename(
                columns={
                    "Precinct": "precinct_id",
                    "NO": "no_votes",
                    "YES": "yes_votes",
                    "Voter Turnout": "turnout",
                }
            )
            # get rid of some columns so we can get rid of duplicates
            .drop(columns=["Contest Name", "Candidate Name", "Votes"])
            # drop duplicates
            .drop_duplicates()
            # reset and get rid of the index column
            .reset_index()
            .drop(columns=["index"])
        )
        # add county column
        solano["county"] = "Solano"
        # add total_votes column
        solano["total_votes"] = solano["no_votes"] + solano["yes_votes"]
        # remove "%" from turnout column values
        solano["turnout"] = solano["turnout"].str.replace("%", "")

        return solano


    solano = solano_df()
    solano.head(None)
    return (solano,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sonoma
    """)
    return


@app.cell
def _(pd):
    SONOMA_PROP50_RESULTS_SHEET = "3"
    SONOMA_HEADER_ROWS_N = 2

    sonoma = pd.read_excel(
        "inputs/counties/sonoma/detail 2.xlsx",
        sheet_name=SONOMA_PROP50_RESULTS_SHEET,
        skiprows=SONOMA_HEADER_ROWS_N,
    )

    # look at source spreadsheet to understand column name mapping
    # there are multiple header rows in the spreadsheet but the values
    # are obvious if you look open the document
    sonoma = sonoma.rename(
        columns={
            "Precinct": "precinct_id",
            "Total Votes": "yes_votes",
            "Total Votes.1": "no_votes",
        }
    )
    sonoma = sonoma[sonoma["precinct_id"] != "Total:"].copy()
    sonoma["county"] = "Sonoma"
    sonoma["turnout"] = (sonoma["Total"] / sonoma["Registered Voters"]) * 100
    sonoma = sonoma.reset_index(drop=True).drop(
        columns=[
            "Registered Voters",
            "Election Day",
            "Vote By Mail",
            "Election Day.1",
            "Vote By Mail.1",
            "Total",
        ]
    )
    sonoma.head(None)
    return (sonoma,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Stanislaus
    """)
    return


@app.cell
def _(pd, pdfplumber):
    _PROP5_PAGE_RANGE = (6, 8)


    def extract_stanislaus_pdf():
        stanislaus = None
        # extract the tables from the Prop 50 results pages in the PDF document
        with pdfplumber.open(
            "inputs/counties/stanislaus/11-04-2025-sov.pdf"
        ) as pdf:
            extracted_pages = []
            # just a few pages from the document are related to Prop 50
            prop_50_pages = pdf.pages[_PROP5_PAGE_RANGE[0] : _PROP5_PAGE_RANGE[1]]

            for page in prop_50_pages:
                table = page.extract_table()
                df = pd.DataFrame(table[1:])
                extracted_pages.append(df)

            stanislaus = pd.concat(extracted_pages)
        return stanislaus


    stanislaus = extract_stanislaus_pdf()

    # now that all the data has been extracted we need to rename
    # the columns in the dataframe. the mapping can be verified
    # by looking at the source PDF document
    stanislaus = stanislaus.rename(
        columns={0: "precinct_id", 3: "turnout", 4: "yes_votes", 5: "no_votes"}
    )

    # we can drop columns we don't care about
    # column with an index of 1 is "Registered Voters"
    # column with an index of 2 is "Ballots Cast"
    stanislaus = stanislaus.drop(columns=[1, 2])

    # add a county column
    stanislaus["county"] = "Stanislaus"

    # force yes_votes and no_votes to be numbers
    stanislaus["yes_votes"] = pd.to_numeric(
        stanislaus["yes_votes"], errors="coerce"
    )
    stanislaus["no_votes"] = pd.to_numeric(stanislaus["no_votes"], errors="coerce")

    # and add a total_votes
    stanislaus["total_votes"] = stanislaus["yes_votes"] + stanislaus["no_votes"]

    _PRECINCT_ID_PATTERN = r"\d{6}"
    stanislaus = stanislaus[
        stanislaus["precinct_id"].str.match(_PRECINCT_ID_PATTERN)
    ].reset_index(drop=True)

    stanislaus.head(None)
    return (stanislaus,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sutter
    """)
    return


@app.cell
def _(pd):
    sutter_prop_50_sheet_name = "Sheet2"
    sutter = pd.read_excel(
        "inputs/counties/sutter/Statement Of Votes Cast - Countywide.xlsx",
        sheet_name=sutter_prop_50_sheet_name,
        skiprows=5,
    )

    sutter = sutter[sutter["Electionwide"] != "County - Total"].copy()
    sutter = sutter[sutter["Electionwide"] != "Cumulative"].copy()
    sutter = sutter[sutter["Electionwide"] != "Cumulative - Total"].copy()
    sutter = sutter[sutter["Electionwide"] != "Electionwide - Total"].copy()
    sutter = sutter[sutter["Electionwide"] != "VBM"].copy()
    sutter = sutter[sutter["Electionwide"] != "Polls"].copy()
    sutter = sutter[sutter["Electionwide"] != "Early Voting"].copy()
    sutter = sutter.bfill()
    sutter = sutter[sutter["Electionwide"] != "Total"].copy()
    sutter = sutter.drop(
        columns=[
            "Unnamed: 1",
            "Unnamed: 3",
            "Unnamed: 4",
            "Unnamed: 5",
            "Electionwide.1",
            "Unnamed: 8",
            "Unnamed: 10",
            "Unnamed: 11",
        ]
    )
    sutter.columns = [
        "precinct_id",
        "Registered Voters",
        "yes_votes",
        "no_votes",
        "total_votes",
    ]
    sutter["turnout"] = (sutter["total_votes"] / sutter["Registered Voters"]) * 100
    sutter = sutter.reset_index(drop=True).drop(columns=["Registered Voters"])
    sutter["county"] = "Sutter"
    sutter
    return (sutter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tulare
    """)
    return


@app.cell
def _(
    calculate_turnout,
    clean_redacted_precincts,
    pd,
    rename_and_filter_columns,
):
    def tulare_df(fp, column_renames=dict()) -> pd.DataFrame:
        COUNTY_NAME = "Tulare"
        RESULTS_HEADER = 3
        VALUE_COLUMNS = ["YES\n ", "NO\n ", "Total Votes"]

        df = pd.read_excel(fp, sheet_name=1, skiprows=RESULTS_HEADER)

        def dedupe_data(df) -> pd.DataFrame:
            """Source data includes multiple entries for each precincts grouped
            by CD, SD, etc.. I filter for numeric strings to drop headers and
            then retain only the first value from the election wide data group"""
            is_precinct_id = df["Precinct"].str.isnumeric()
            df_headers_dropped = df[
                is_precinct_id
            ].copy()  # drop inline header rows
            expected_precinct_count = df_headers_dropped["Precinct"].nunique()
            df_deduped = df_headers_dropped.drop_duplicates(
                "Precinct", keep="first"
            )  # precinct data repeated and grouped by CD, SD, etc.
            assert df_deduped["Precinct"].nunique() == expected_precinct_count
            return df_deduped

        df = dedupe_data(df)
        df = df.dropna(axis=1, how="all", ignore_index=True)

        df[VALUE_COLUMNS] = df[VALUE_COLUMNS].apply(clean_redacted_precincts)

        df["turnout"] = calculate_turnout(
            df["Total Votes"], df["Registered \nVoters"]
        )

        if column_renames:
            df = rename_and_filter_columns(df, column_renames)

        df["county"] = COUNTY_NAME

        return df


    TULARE_FP = (
        "./inputs/counties/tulare/results/StatementOfVotesCastRPT_By_Precinct.xlsx"
    )
    tulare = tulare_df(
        TULARE_FP,
        {
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
            "turnout": "turnout",
        },
    )
    tulare
    return (tulare,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Trinity
    """)
    return


@app.cell
def _(pd):
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
        TRINITY_HEADER_ROWS_N = 23
        trinity = []
        trinity_sheets = [
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
        for sheet in trinity_sheets:
            trinity_sheet_df = pd.read_excel(
                "inputs/counties/trinity/Final Precinct Results-12-2-2025 08-46-33 AM.xlsx",
                sheet_name=sheet,
                skiprows=TRINITY_HEADER_ROWS_N,
            )
            trinity_extracted = trinity_extract_df(trinity_sheet_df)
            trinity.append(trinity_extracted)

        trinity = pd.DataFrame(trinity)
        trinity["county"] = "Trinity"
        return trinity


    trinity = trinity_df()
    trinity.head(None)
    return (trinity,)


@app.cell
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _(pd, re):
    REDACTED_PLACEHOLDER_REGEX = re.compile(r"\*+")


    def clean_redacted_precincts(
        _series: pd.Series,
        placeholder_regex=REDACTED_PLACEHOLDER_REGEX,
    ) -> pd.Series:
        _series = _series.replace(placeholder_regex, pd.NA)
        return _series.astype("Int64")
    return (clean_redacted_precincts,)


@app.cell
def _(pd):
    def rename_and_filter_columns(df: pd.DataFrame, rename_dict: dict):
        return df.rename(columns=rename_dict)[list(rename_dict.values())].copy()
    return (rename_and_filter_columns,)


@app.cell
def _(pd):
    def calculate_turnout(
        votes_cast: pd.Series, registered_voter_count: pd.Series
    ) -> pd.Series:
        registered_voter_count = registered_voter_count.replace(0, 1)
        return round((votes_cast / registered_voter_count) * 100, 1)
    return (calculate_turnout,)


@app.cell
def _(pd):
    def calculate_total_votes(df_clean: pd.DataFrame) -> pd.Series:
        return df_clean["yes_votes"] + df_clean["no_votes"]
    return (calculate_total_votes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tuolumne
    """)
    return


@app.cell
def _(pd):
    # read in excel file using the sheet titled "Sheet2" and skip 3 rows at the top and five at the end
    TUOLUMNE_HEADER_N = 3
    TUOLUMNE_CUMULATIVE_FOOTER_N = 5
    tuolumne = pd.read_excel(
        "inputs/counties/tuolumne/StatementOfVotesCastRPT.xlsx",
        sheet_name=1,
        skiprows=TUOLUMNE_HEADER_N,
        skipfooter=TUOLUMNE_CUMULATIVE_FOOTER_N,
    )

    # the first two rows aren't useful to us so we want to drop those too
    tuolumne = tuolumne[tuolumne["Precinct"] != "County"].copy()
    tuolumne = tuolumne[tuolumne["Precinct"] != "Electionwide"].copy()

    # let's add a turnout column before we drop all the columns we don't care about
    tuolumne["turnout"] = (
        tuolumne["Total Votes"] / tuolumne["Registered \nVoters"]
    ) * 100

    # and now drop 'em
    tuolumne = tuolumne.drop(
        columns=[
            "Times Cast",
            "Registered \nVoters",
            "Unnamed: 3",
            "Undervotes",
            "Overvotes",
            "Precinct.1",
            "Unnamed: 8",
            "Unnamed: 10",
            "Unnamed: 11",
        ]
    )

    # let's rename the columns and add a county column
    tuolumne = tuolumne.rename(
        columns={
            "Precinct": "precinct_id",
            "YES\n ": "yes_votes",
            "NO\n ": "no_votes",
            "Total Votes": "total_votes",
        }
    )
    tuolumne["county"] = "Tuolumne"

    # and get rid of the index
    tuolumne = tuolumne.reset_index(drop=True)

    tuolumne.head(None)
    return (tuolumne,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ventura
    """)
    return


@app.cell
def _(np, pd):
    VENTURA_FILENAME = "inputs/counties/ventura/2025.11.04-Statement-of-Votes-Precinct-Canvass.xlsx"
    _PRECINCT_ID_PATTERN = r"\d{7}"

    # read in the source file
    VENTURA_HEADER_N = 6
    ventura = pd.read_excel(
        VENTURA_FILENAME, sheet_name=1, skiprows=VENTURA_HEADER_N
    )

    # rename some columns
    ventura = ventura.rename(
        columns={
            "Unnamed: 0": "precinct_id",
            "Turnout (%)": "turnout",  # some values in this column are >100%; emailed to ask why
            "Yes": "yes_votes",
            "No": "no_votes",
            "Total Votes": "total_votes",
        }
    )

    # and then drop some columns we don't want to care about
    ventura = ventura.drop(
        columns=[
            "Unnamed: 1",
            "Registered Voters",
            "Voters Cast",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 8",
            "Unnamed: 10",
        ]
    )

    # remove the % from the turnout column
    ventura["turnout"] = ventura["turnout"].str.replace("%", "")

    # replace masked values with np.nan
    ventura["yes_votes"] = ventura["yes_votes"].replace("***", np.nan)
    ventura["no_votes"] = ventura["no_votes"].replace("***", np.nan)
    ventura["total_votes"] = ventura["total_votes"].replace("***", np.nan)

    ventura = ventura[
        ventura["precinct_id"].str.match(_PRECINCT_ID_PATTERN, na=False)
    ].reset_index(drop=True)

    # add county column
    ventura["county"] = "Ventura"

    ventura.head(None)
    return (ventura,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Yolo
    """)
    return


@app.cell
def _(EsriDumper, pd):
    YOLO_COUNTY_PRECINCT_RESULTS_FEATURE_SERVER = "https://services2.arcgis.com/RETsakmE0SJfZXCd/ArcGIS/rest/services/Election_Results_Nov_2025/FeatureServer/0"
    yolo_features = EsriDumper(YOLO_COUNTY_PRECINCT_RESULTS_FEATURE_SERVER)

    yolo = []
    # Iterate over each feature and collect the data we want
    for feature in yolo_features:
        d = {
            "county": "Yolo",
            "precinct_id": feature["properties"]["PRECINCTID"],
            "no_votes": feature["properties"]["TOTALVOTES_1"],
            "yes_votes": feature["properties"]["TOTALVOTES_2"],
        }

        d["total_votes"] = d["no_votes"] + d["yes_votes"]

        if feature["properties"]["RegisteredVoters"] == 0:
            d["turnout"] = 0
        else:
            d["turnout"] = (
                d["total_votes"] / (feature["properties"]["RegisteredVoters"] or 0)
            ) * 100

        yolo.append(d)

    yolo = pd.DataFrame(yolo)

    yolo
    return (yolo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Yuba
    """)
    return


@app.cell
def _(pd):
    YUBA_FILENAME = "inputs/counties/yuba/11_25_SOV.xlsx"

    # read in the source file
    yuba_xlsx = pd.read_excel(YUBA_FILENAME, skiprows=6, skipfooter=3).set_index(
        "Unnamed: 0"
    )

    # create a pivot table to add together the different voting methods in each precinct
    yuba_pt = yuba_xlsx.pivot_table(
        index="Unnamed: 0",
        values=["Yes", "No"],
        aggfunc="sum",
    )

    # drop a bunch of columns from the source spreadsheet that aren't needed anymore
    yuba_xlsx = yuba_xlsx.drop(
        columns=[
            "Unnamed: 1",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 9",
            "Voters Cast",
            "Turnout (%)",
            "Yes",
            "No",
        ]
    )

    # join the pivot table and the csv together so we can get registered voters per precinct
    yuba = yuba_pt.join(yuba_xlsx, on="Unnamed: 0")

    # then rename some columns so that they're easier to work with
    yuba = yuba.reset_index().rename(
        columns={"Unnamed: 0": "precinct_id", "No": "no_votes", "Yes": "yes_votes"}
    )

    # get rid of duplicates
    yuba = yuba.drop_duplicates()

    # calculate total votes
    yuba["total_votes"] = yuba["no_votes"] + yuba["yes_votes"]

    # and then turnout
    yuba["turnout"] = (yuba["total_votes"] / yuba["Registered Voters"]) * 100

    # now that we're done with it drop the "Registered Voters" column
    yuba = yuba.drop(columns=["Registered Voters"])

    # note the county
    yuba["county"] = "Yuba"

    # and then clean up the index
    yuba = yuba.reset_index(drop=True)

    yuba.head(None)
    return (yuba,)


if __name__ == "__main__":
    app.run()
