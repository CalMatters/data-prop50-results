import marimo

__generated_with = "0.18.0"
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
    return mo, pd


@app.cell
def _(imperial, pd):
    combined = pd.concat([imperial])
    combined.to_csv("outputs/results.csv", index=False)
    combined.head()
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

        return prop_50_altered


    imperial = imperial_df()

    imperial.head()
    return (imperial,)


if __name__ == "__main__":
    app.run()
