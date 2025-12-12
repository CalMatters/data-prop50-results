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
    import pandas as pd
    import pdfplumber
    return mo, pd, pdfplumber


@app.cell
def _(
    butte,
    calaveras,
    colusa,
    contra_costa,
    el_dorado,
    glenn,
    imperial,
    pd,
    sutter,
    tulare,
):
    combined = pd.concat(
        [
            butte,
            calaveras,
            colusa,
            contra_costa,
            el_dorado,
            glenn,
            imperial,
            sutter,
            tulare,
        ]
    ).reset_index(drop=True)
    combined.to_csv("outputs/results.csv", index=False)
    combined.head(None)
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
    ## Sutter
    """)
    return


@app.cell
def _(pd, pdfplumber):
    def sutter_df():
        sutter = None
        with pdfplumber.open(
            "inputs/counties/sutter/Statement Of Votes Cast  Countywide.pdf"
        ) as pdf:
            extracted = None
            prop_50_page = pdf.pages[2]
            cropped = prop_50_page.crop((396, 50, 792, 612))
            table = cropped.extract_table()
            sutter = pd.DataFrame(table)

        # # rename columns
        sutter.columns = [
            "precinct_id",
            "yes_votes",
            "Yes_%",
            "no_votes",
            "No_%",
            "total_votes",
        ]

        # # drop some empty columns that were part of the spreadsheet structure
        sutter.drop(columns=["Yes_%", "No_%"], inplace=True)

        # get rid of total rows
        sutter = sutter[sutter["precinct_id"] != "Precinct"].copy()
        sutter = sutter[sutter["precinct_id"] != "County"].copy()
        sutter = sutter[sutter["precinct_id"] != "Electionwide"].copy()
        sutter = sutter[sutter["precinct_id"] != "Electionwide - Total"].copy()
        sutter = sutter[sutter["precinct_id"] != "Cumulative"].copy()
        sutter = sutter[sutter["precinct_id"] != "Cumulative - Total"].copy()
        sutter = sutter[sutter["precinct_id"] != "County - Total"].copy()

        # don't forget to add the county
        sutter["county"] = "Sutter"

        # and get rid of the index column
        sutter = sutter.reset_index()
        sutter = sutter.drop(columns=["index"])
        return sutter


    sutter = sutter_df()
    sutter.head(None)
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
    pd,
    rename_and_filter_columns,
    zero_out_insufficient_turnout_precincts,
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

        df[VALUE_COLUMNS] = df[VALUE_COLUMNS].apply(
            zero_out_insufficient_turnout_precincts
        )

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


@app.cell
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


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
    INSUFFICIENT_TURNOUT_PLACEHOLDER = "****"


    def zero_out_insufficient_turnout_precincts(
        _series: pd.Series, placeholder_value=INSUFFICIENT_TURNOUT_PLACEHOLDER
    ) -> pd.Series:
        _series = _series.replace({placeholder_value: "0"})
        return _series.astype(int)
    return (zero_out_insufficient_turnout_precincts,)


if __name__ == "__main__":
    app.run()
