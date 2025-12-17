import marimo

__generated_with = "0.18.4"
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
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pdfplumber
    return mo, np, pd, pdfplumber


@app.cell
def _(
    alameda,
    butte,
    calaveras,
    colusa,
    contra_costa,
    el_dorado,
    glenn,
    imperial,
    pd,
    santa_barbara,
    shasta,
    siskiyou,
    solano,
    sonoma,
    sutter,
    trinity,
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
            imperial,
            santa_barbara,
            shasta,
            siskiyou,
            solano,
            sonoma,
            sutter,
            trinity,
        ]
    ).reset_index(drop=True)
    combined.to_csv("outputs/results.csv", index=False)
    combined.head(None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Alameda
    """)
    return


@app.cell
def _(pd):
    alameda = pd.read_excel(
        "inputs/counties/alameda/Statement of Vote - Statewide Special Election.xlsx",
        sheet_name="Sheet2",
        skiprows=5,
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
    alameda['turnout'] = alameda['turnout'].str.replace('%', '')

    # get rid of the index column
    alameda = alameda.reset_index().drop(columns=["index"])

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
def _(pd):
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
        csv = csv.replace("****", 0)

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

        # get rid of four values associated with each precinct
        glenn = glenn[glenn["precinct_id"] != "Electionwide"].copy()
        glenn = glenn[glenn["precinct_id"] != "Vote by Mail"].copy()
        glenn = glenn[glenn["precinct_id"] != "Election Day"].copy()
        # glenn = glenn[glenn['precinct_id'] != 'Provisional'].copy()

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

    # show all of the data
    santa_barbara.head(None)
    return (santa_barbara,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shasta
    """)
    return


@app.cell
def _(pd):
    shasta = pd.read_excel(
        "inputs/counties/shasta/detail.xlsx", sheet_name="2", skiprows=2
    )
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
    shasta = shasta.reset_index().drop(
        columns=[
            "index",
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
    sonoma = pd.read_excel(
        "inputs/counties/sonoma/detail 2.xlsx", sheet_name="3", skiprows=2
    )
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
    sonoma = sonoma.reset_index().drop(
        columns=[
            "index",
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
    ## Sutter
    """)
    return


@app.cell
def _(pd):
    sutter = pd.read_excel(
        "inputs/counties/sutter/Statement Of Votes Cast - Countywide.xlsx",
        sheet_name="Sheet2",
        skiprows=5,
    )
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
    sutter = sutter.reset_index().drop(columns=["index", "Registered Voters"])
    sutter.head(None)
    return (sutter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Trinity
    """)
    return


@app.cell
def _(pd):
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


    def trinity_extract_df(df):
        precinct_id = df.iloc[0, 0]
        yes_votes = df.iloc[6, 20]
        no_votes = df.iloc[7, 20]
        turnout = df.iloc[0, 13].split(" = ")[1].replace("%", "")
        return {
            "precinct_id": precinct_id,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "total_votes": yes_votes + no_votes,
            "turnout": turnout,
        }


    for sheet in trinity_sheets:
        trinity_sheet_df = pd.read_excel(
            "inputs/counties/trinity/Final Precinct Results-12-2-2025 08-46-33 AM.xlsx",
            sheet_name=sheet,
            skiprows=23,
        )
        trinity_extracted = trinity_extract_df(trinity_sheet_df)
        trinity.append(trinity_extracted)

    trinity = pd.DataFrame(trinity)
    trinity["county"] = "Trinity"
    trinity.head(None)
    return (trinity,)


if __name__ == "__main__":
    app.run()
