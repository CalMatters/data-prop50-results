import marimo

__generated_with = "0.18.2"
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
    import pandas as pd
    import pdfplumber
    return mo, pd, pdfplumber


@app.cell
def _(butte, contra_costa, imperial, pd):
    combined = pd.concat([butte, contra_costa, imperial]).reset_index(drop=True)
    combined.to_csv("outputs/results.csv", index=False)
    combined.head()
    return


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
        csv.rename(
            columns={
                "Precinct": "precinct_id",
                "Total Votes": "no_votes",
                "Total Votes.1": "yes_votes",
            },
            inplace=True,
        )
        csv["county"] = "Butte"
        csv["turnout"] = round((csv["Total"] / csv["Registered Voters"]) * 100, 1)
        csv.drop(
            columns=[
                "Live",
                "Vote By Mail",
                "Registered Voters",
                "Provisional",
                "Live.1",
                "Vote By Mail.1",
                "Provisional.1",
                "Total",
            ],
            inplace=True,
        )
        return csv


    butte = butte_df()
    butte.head()
    return (butte,)


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
        csv.drop(
            columns=[
                "Times Cast",
                "Unnamed: 3",
                "Precinct.1",
                "Unnamed: 6",
                "Unnamed: 8",
                "Unnamed: 10",
                "Unnamed: 11",
                "Unnamed: 12",
            ],
            inplace=True,
        )

        # there are four rows per precinct so let's drop two of them
        # "In-person" and "Vote By Mail"
        csv.drop(csv[csv["Precinct"] == "In-Person"].index, inplace=True)
        csv.drop(csv[csv["Precinct"] == "Vote By Mail"].index, inplace=True)

        # get rid of the first two rows
        csv.drop([0, 1], inplace=True)

        # backfill the values from the rows where "Precinct" is "Total" to the rows
        # that have proper precinct IDs
        csv.bfill(limit=1, inplace=True)

        # and now get rid of that extra row for Total
        csv.drop(csv[csv["Precinct"] == "Total"].index, inplace=True)
        csv.rename(
            columns={
                "Precinct": "precinct_id",
                "Yes\n ": "yes_votes",
                "No\n ": "no_votes",
            },
            inplace=True,
        )

        # replaced masked values with 0 for turnout calculations
        csv.replace("****", 0, inplace=True)

        # and then add in a calculated turnout column
        csv["turnout"] = round(
            (csv["Total Votes"] / csv["Registered \nVoters"]) * 100, 1
        )

        # make the index a column so we can drop it
        csv.reset_index(inplace=True)

        # get rid of remaining columns
        csv.drop(
            columns=["index", "Registered \nVoters", "Total Votes"], inplace=True
        )

        return csv


    contra_costa = contra_costa_df()
    contra_costa.head(20)
    return (contra_costa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## El Dorado
    """)
    return


@app.cell
def _(pd, pdfplumber):
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
    el_dorado.columns = ["precinct_id", "yes_votes", "Yes_Blank", "no_votes", "No_Blank", "total_votes"]

    # drop some empty columns that were part of the spreadsheet structure
    el_dorado.drop(columns=["Yes_Blank", "No_Blank"], inplace=True)

    # get rid of four values associated with each precinct
    el_dorado = el_dorado[el_dorado['precinct_id'] != 'Mail'].copy()
    el_dorado = el_dorado[el_dorado['precinct_id'] != 'Vote Center'].copy()
    el_dorado = el_dorado[el_dorado['precinct_id'] != 'Election Day'].copy()
    el_dorado = el_dorado[el_dorado['precinct_id'] != 'Provisional'].copy()

    # some values are white space so replace that with None
    el_dorado = el_dorado.replace(r'^\s*$', None, regex=True)

    # backfill missing values
    el_dorado = el_dorado.bfill(limit = 1)

    # and then drop the "Total" value rows that were used to backfill
    el_dorado = el_dorado[el_dorado['precinct_id'] != 'Total'].copy()

    # don't forget to add the county
    el_dorado['county'] = 'El Dorado'

    # and get rid of the index column
    el_dorado = el_dorado.reset_index()
    el_dorado = el_dorado.drop(columns=['index'])

    el_dorado.head()
    return


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

        return prop_50_altered


    imperial = imperial_df()

    imperial.head()
    return (imperial,)


if __name__ == "__main__":
    app.run()
