import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    import pandas as pd

    return gpd, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read and prepare data
    """)
    return


@app.cell
def _():
    DATASET_CONFIG = [
        {
            "id": "Prop. 50",
            "filepath": "./outputs/precincts_results_cvap_blocks.gpkg",
            "demographic_schema": "blocks",
            "vote_source_to_standard": {
                "yes_votes": "yes_votes",
                "no_votes": "no_votes",
            },
        },
        {
            "id": "Presidential",
            "filepath": "./outputs/precincts_2024_results_cvap_blocks.gpkg",
            "demographic_schema": "blocks",
            "vote_source_to_standard": {
                "dem_votes": "yes_votes",
                "rep_votes": "no_votes",
            },
        },
    ]
    return (DATASET_CONFIG,)


@app.function
def calculate_net_shift(_df_prop50, _df_pres24):
    yes_votes = _df_prop50["yes_votes"].sum()
    no_votes = _df_prop50["no_votes"].sum()
    total_votes_25 = _df_prop50["total_votes"].sum()
    yes_pct = yes_votes / total_votes_25
    no_pct = no_votes / total_votes_25

    dem_votes = _df_pres24["dem_votes"].sum()
    rep_votes = _df_pres24["rep_votes"].sum()
    total_votes_24 = _df_pres24["total_votes"].sum()
    dem_pct = dem_votes / total_votes_24
    rep_pct = rep_votes / total_votes_24

    net_shift = (yes_pct - no_pct) - (dem_pct - rep_pct)
    return round(net_shift, 3)


@app.cell
def _():
    [
        "_latino_voters",
        "_asian_voters",
    ]

    [
        "CVAP_TOT24",
        "CVAP_HSP24",
        "CVAP_WHT24",
        "CVAP_BLK24",
        "CVAP_2OM24",
        "_cvap_api24",
        "_cvap_amw24",
    ]

    DEMOGRAPHIC_PCT_COLUMNS = [
        "CVAP_HSP24_pct",
        "CVAP_WHT24_pct",
        "CVAP_BLK24_pct",
        "CVAP_2OM24_pct",
        "_cvap_api24_pct",
        "_cvap_amw24_pct",
    ]
    return


@app.cell
def _(DATASET_CONFIG, gpd):
    df_prop50 = gpd.read_file(DATASET_CONFIG[0]["filepath"])
    counties_prop50 = list(df_prop50["county"].unique())

    df_pres24 = gpd.read_file(DATASET_CONFIG[1]["filepath"])
    df_pres24 = df_pres24[df_pres24["county"].isin(counties_prop50)]
    return df_pres24, df_prop50


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Fact-check
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Main bar
    """)
    return


@app.cell(hide_code=True)
def _(county_count, mo, net_shift_voter_of_color_precincts):
    mo.md(rf"""
    Source text:

    > The analysis of voting results from 57 of California’s 58 counties found that Proposition 50, Gov. Gavin Newsom’s plan to gerrymander the state’s congressional districts in Democrats’ favor, vastly outperformed Kamala Harris’s 2024 presidential campaign in precincts where the majority of voters are nonwhite.

    Fact-checked text:
    > The analysis of voting results from {county_count} of California’s 58 counties found that Proposition 50, Gov. Gavin Newsom’s plan to gerrymander the state’s congressional districts in Democrats’ favor, outperformed Kamala Harris’s 2024 presidential campaign in precincts where the majority of voters are nonwhite by {net_shift_voter_of_color_precincts:+0.00%} percentage points.
    """)
    return


@app.cell
def _(df_prop50):
    county_count = df_prop50["county"].nunique()
    return (county_count,)


@app.cell
def _(df_pres24, df_prop50):
    def is_maj_non_white(_df):
        return round(100 - _df["CVAP_WHT24_pct"], 1) > 50


    net_shift_voter_of_color_precincts = calculate_net_shift(
        df_prop50[is_maj_non_white(df_prop50)],
        df_pres24[is_maj_non_white(df_pres24)],
    )
    return (net_shift_voter_of_color_precincts,)


@app.cell(hide_code=True)
def _(mo, net_shift_maj_latino_voters):
    mo.md(rf"""
    Static text:

    > The trend was most striking in precincts where the majority of ballots were cast by Latino voters. “Yes” on Prop. 50 gained about 30 percentage points compared to Harris’s performance against Trump a year earlier, according to CalMatters’ analysis.

    Dynamic text:

    > The trend was most striking in precincts where the majority of ballots were cast by Latino voters. “Yes” on Prop. 50 gained about {net_shift_maj_latino_voters:+00.000%} percentage points compared to Harris’s performance against Trump a year earlier, according to CalMatters’ analysis.
    """)
    return


@app.cell
def _(df_pres24, df_prop50):
    COUNTIES_NOT_AVAILABLE_ON_SWDB = ["Shasta", "Tulare"]


    def exclude_non_swdb_data(_df):
        return ~_df["county"].isin(COUNTIES_NOT_AVAILABLE_ON_SWDB)


    def is_maj_votes_cast_by_latino_voters(_df):
        return (_df["_latino_voters"] / _df["total_votes"]) > 0.50


    net_shift_maj_latino_voters = calculate_net_shift(
        df_prop50[
            is_maj_votes_cast_by_latino_voters(df_prop50)
            & exclude_non_swdb_data(df_prop50)
        ],
        df_pres24[
            is_maj_votes_cast_by_latino_voters(df_pres24)
            & exclude_non_swdb_data(df_pres24)
        ],
    )
    return (net_shift_maj_latino_voters,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Show Your Work
    """)
    return


@app.cell(hide_code=True)
def _(county_count, mo, pct_total_vote):
    mo.md(rf"""
    Static text:
    > CalMatters analyzed precinct-level results from the 2025 election in 57 of 58 California counties, representing over 99% of the statewide vote.

    Dynamic text: 
    > CalMatters analyzed precinct-level results from the 2025 election in {county_count} of 58 California counties, representing over {pct_total_vote:0.1%} of the statewide vote.
    """)
    return


@app.cell
def _(df_prop50):
    # pulled from https://elections.cdn.sos.ca.gov/sov/2025-special/sov/complete-sov.pdf
    SOV_TOTAL_VOTERS = 11_584_393

    total_votes = df_prop50["total_votes"].sum()
    pct_total_vote = total_votes / SOV_TOTAL_VOTERS
    return (pct_total_vote,)


@app.cell(hide_code=True)
def _(mo, net_shift_voter_of_color_precincts):
    mo.md(rf"""
    Static text:
    > Our analysis shows that Proposition 50, Gov. Gavin Newsom’s plan to gerrymander congressional districts in Democrats’ favor in response to a Republican gerrymander in Texas, outperformed the 2024 Kamala Harris campaign among voters of color.

    Dynamic text:
    > Our analysis shows that Proposition 50, Gov. Gavin Newsom’s plan to gerrymander congressional districts in Democrats’ favor in response to a Republican gerrymander in Texas, outperformed the 2024 Kamala Harris campaign among voters of color by {net_shift_voter_of_color_precincts:+0.1%} percentage points.
    """)
    return


@app.cell(hide_code=True)
def _(mo, net_shift_in_maj_latino_precincts, net_shift_maj_latino_voters):
    mo.md(rf"""
    Static text:

    > In these counties, we observed the largest change in majority-Latino precincts. In precincts where Latinos are the majority of the citizen voting-age population, there was a 25 percentage-point net shift to the Prop. 50 redistricting measure. In precincts where the majority of votes cast were by Latino voters, there was a net shift of 29 percentage points.

    Dynamic text:

    > In these counties, we observed the largest change in majority-Latino precincts. In precincts where Latinos are the majority of the citizen voting-age population, there was a {net_shift_in_maj_latino_precincts:.1%} percentage-point net shift to the Prop. 50 redistricting measure. In precincts where the majority of votes cast were by Latino voters, there was a net shift of {net_shift_maj_latino_voters:.1%} percentage points.
    """)
    return


@app.cell
def _(df_pres24, df_prop50):
    def meets_group_threshold(_df, group, threshold):
        return _df[group] > threshold


    net_shift_in_maj_latino_precincts = calculate_net_shift(
        df_prop50[meets_group_threshold(df_prop50, "CVAP_HSP24_pct", 50)],
        df_pres24[meets_group_threshold(df_pres24, "CVAP_HSP24_pct", 50)],
    )
    return meets_group_threshold, net_shift_in_maj_latino_precincts


@app.cell(hide_code=True)
def _(mo, pct_dem_maj_latino_precincts, pct_yes_maj_latino_precincts):
    mo.md(rf"""
    Static text: 
    > The largest difference was observed in majority-Latino precincts, where the measure won 73% of the vote statewide, compared to Harris's 59% in 2024.

    Dynamic text: 
    > The largest difference was observed in majority-Latino precincts, where the measure won {pct_yes_maj_latino_precincts:.00%} of the vote statewide, compared to Harris's {pct_dem_maj_latino_precincts:.00%} in 2024. 
    """)
    return


@app.cell
def _(df_pres24, df_prop50, meets_group_threshold):
    df_prop50_maj_latino_precincts = df_prop50[
        meets_group_threshold(df_prop50, "CVAP_HSP24_pct", 50)
    ]
    df_pres24_maj_latino_precincts = df_pres24[
        meets_group_threshold(df_pres24, "CVAP_HSP24_pct", 50)
    ]

    pct_yes_maj_latino_precincts = (
        df_prop50_maj_latino_precincts["yes_votes"].sum()
        / df_prop50_maj_latino_precincts["total_votes"].sum()
    )
    pct_dem_maj_latino_precincts = (
        df_pres24_maj_latino_precincts["dem_votes"].sum()
        / df_pres24_maj_latino_precincts["total_votes"].sum()
    )
    return (
        df_pres24_maj_latino_precincts,
        df_prop50_maj_latino_precincts,
        pct_dem_maj_latino_precincts,
        pct_yes_maj_latino_precincts,
    )


@app.cell(hide_code=True)
def _(
    mo,
    net_shift_socal_maj_latino_precincts,
    pct_dem_socal_maj_latino_precincts,
    pct_yes_socal_maj_latino_precincts,
):
    mo.md(rf"""
    Static text:
    > Majority-Latino precincts in Southern California reported the largest shift in vote percentage: Los Angeles, Orange, Riverside, and San Bernardino counties shifted a net 27.5 percentage points, voting 60.6% for Harris and 75.9% for Prop. 50. 

    Dynamic Text:
    > Majority-Latino precincts in Southern California reported the largest shift in vote percentage: Los Angeles, Orange, Riverside, and San Bernardino counties shifted a net {net_shift_socal_maj_latino_precincts:0.1%} percentage points, voting {pct_dem_socal_maj_latino_precincts:0.1%} for Harris and {pct_yes_socal_maj_latino_precincts:0.1%} for Prop. 50. 
    """)
    return


@app.cell
def _(df_pres24_maj_latino_precincts, df_prop50_maj_latino_precincts):
    SOCAL_COUNTIES = ["Los Angeles", "Orange", "Riverside", "San Bernardino"]


    def calculate_yes_pct(_df_prop50):
        return _df_prop50["yes_votes"].sum() / _df_prop50["total_votes"].sum()


    def calculate_dem_pct(_df_pres24):
        return _df_pres24["dem_votes"].sum() / _df_pres24["total_votes"].sum()


    df_prop50_maj_latino_socal_precincts = df_prop50_maj_latino_precincts[
        df_prop50_maj_latino_precincts["county"].isin(SOCAL_COUNTIES)
    ]
    df_pres24_maj_latino_socal_precincts = df_pres24_maj_latino_precincts[
        df_pres24_maj_latino_precincts["county"].isin(SOCAL_COUNTIES)
    ]

    pct_yes_socal_maj_latino_precincts = calculate_yes_pct(
        df_prop50_maj_latino_socal_precincts
    )
    pct_dem_socal_maj_latino_precincts = calculate_dem_pct(
        df_pres24_maj_latino_socal_precincts
    )
    net_shift_socal_maj_latino_precincts = calculate_net_shift(
        df_prop50_maj_latino_socal_precincts,
        df_pres24_maj_latino_socal_precincts,
    )
    return (
        calculate_dem_pct,
        calculate_yes_pct,
        net_shift_socal_maj_latino_precincts,
        pct_dem_socal_maj_latino_precincts,
        pct_yes_socal_maj_latino_precincts,
    )


@app.cell(hide_code=True)
def _(mo, net_shift_central_valley_maj_latino_precincts):
    mo.md(rf"""
    Static text:
    > This finding was not isolated to counties with large urban centers. Kern and Stanislaus counties, both in the Central Valley, reported a 24.5 percentage-point net shift in majority-Latino precincts.

    Dynamic text:
    > This finding was not isolated to counties with large urban centers. Kern and Stanislaus counties, both in the Central Valley, reported a {net_shift_central_valley_maj_latino_precincts:0.1%} percentage-point net shift in majority-Latino precincts.
    """)
    return


@app.cell
def _(df_pres24_maj_latino_precincts, df_prop50_maj_latino_precincts):
    CENTRAL_VALLEY_COUNTIES = ["Kern", "Stanislaus"]

    df_prop50_maj_latino_central_valley_precincts = df_prop50_maj_latino_precincts[
        df_prop50_maj_latino_precincts["county"].isin(CENTRAL_VALLEY_COUNTIES)
    ]
    df_pres24_maj_latino_central_valley_precincts = df_pres24_maj_latino_precincts[
        df_pres24_maj_latino_precincts["county"].isin(CENTRAL_VALLEY_COUNTIES)
    ]

    net_shift_central_valley_maj_latino_precincts = calculate_net_shift(
        df_prop50_maj_latino_central_valley_precincts,
        df_pres24_maj_latino_central_valley_precincts,
    )
    return (net_shift_central_valley_maj_latino_precincts,)


@app.cell(hide_code=True)
def _(mo, pct_dem_maj_black_precincts, pct_yes_maj_black_precincts):
    mo.md(rf"""
    Static text: 
    > Black-majority precincts, which are located largely in Los Angeles and Alameda counties, had the strongest support for both Harris in 2024 and Prop. 50 in 2025. Harris won with 85% of the vote; Prop. 50 won over 92%.

    Dynamic text:
    > Black-majority precincts, which are located largely in Los Angeles and Alameda counties, had the strongest support for both Harris in 2024 and Prop. 50 in 2025. Harris won with {pct_dem_maj_black_precincts:0.1%} of the vote; Prop. 50 won {pct_yes_maj_black_precincts:0.1%}. 
    """)
    return


@app.cell
def _(
    calculate_dem_pct,
    calculate_yes_pct,
    df_pres24,
    df_prop50,
    meets_group_threshold,
):
    COUNTIES_WITH_MAJ_PRECINCTS = ["Alameda", "Los Angeles"]

    df_prop50_maj_black_precincts = df_prop50[
        meets_group_threshold(df_prop50, "CVAP_BLK24_pct", 50)
    ]
    df_pres24_maj_black_precincts = df_pres24[
        meets_group_threshold(df_pres24, "CVAP_BLK24_pct", 50)
    ]

    pct_yes_maj_black_precincts = calculate_yes_pct(df_prop50_maj_black_precincts)
    pct_dem_maj_black_precincts = calculate_dem_pct(df_pres24_maj_black_precincts)
    return pct_dem_maj_black_precincts, pct_yes_maj_black_precincts


@app.cell(hide_code=True)
def _(
    mo,
    net_shift_maj_asian_precincts,
    pct_dem_maj_asian_precincts,
    pct_yes_maj_asian_precincts,
):
    mo.md(rf"""
    Static text:
    > Kamala Harris won 60% of the vote statewide in Asian-majority precincts in 2024. The following year, Prop. 50 received 67% of the vote in Asian-majority precincts, a net shift of 10.3 percentage points.

    Dynamic text:
    > Kamala Harris won {pct_dem_maj_asian_precincts:0.1%} of the vote statewide in Asian-majority precincts in 2024. The following year, Prop. 50 received {pct_yes_maj_asian_precincts:0.1%} of the vote in Asian-majority precincts, a net shift of {net_shift_maj_asian_precincts:0.1%} percentage points.
    """)
    return


@app.cell
def _(
    calculate_dem_pct,
    calculate_yes_pct,
    df_pres24,
    df_prop50,
    meets_group_threshold,
):
    df_prop50_maj_asian_precincts = df_prop50[
        meets_group_threshold(df_prop50, "_cvap_api24_pct", 50)
    ]
    df_pres24_maj_asian_precincts = df_pres24[
        meets_group_threshold(df_pres24, "_cvap_api24_pct", 50)
    ]

    pct_yes_maj_asian_precincts = calculate_yes_pct(df_prop50_maj_asian_precincts)
    pct_dem_maj_asian_precincts = calculate_dem_pct(df_pres24_maj_asian_precincts)
    net_shift_maj_asian_precincts = calculate_net_shift(
        df_prop50_maj_asian_precincts,
        df_pres24_maj_asian_precincts,
    )
    return (
        net_shift_maj_asian_precincts,
        pct_dem_maj_asian_precincts,
        pct_yes_maj_asian_precincts,
    )


@app.cell(hide_code=True)
def _(api_cvap_la_orange, mo, net_shift_maj_asian_la_orange_precincts):
    mo.md(rf"""
    Static text:
    > Los Angeles and Orange County have a combined population of over 1.5 million voting-age Asian-American citizens. Analyzing results from the majority-Asian precincts in these two Southern California counties shows a 13.1 percentage-point net shift.

    Dynamic text:
    > Los Angeles and Orange County have a combined CVAP estimate of {api_cvap_la_orange:,.0f} voting-age Asian and Pacific Islander citizens (interpolated from Census block CVAP onto 2025 precincts). Analyzing results from the majority-Asian precincts in these two Southern California counties shows a {net_shift_maj_asian_la_orange_precincts:0.1%} percentage-point net shift.
    """)
    return


@app.cell
def _(df_pres24, df_prop50, meets_group_threshold):
    LA_ORANGE_COUNTIES = ["Los Angeles", "Orange"]

    df_prop50_la_orange = df_prop50[df_prop50["county"].isin(LA_ORANGE_COUNTIES)]
    api_cvap_la_orange = df_prop50_la_orange["_cvap_api24"].sum()

    df_prop50_maj_asian_la_orange_precincts = df_prop50[
        df_prop50["county"].isin(LA_ORANGE_COUNTIES)
        & meets_group_threshold(df_prop50, "_cvap_api24_pct", 50)
    ]
    df_pres24_maj_asian_la_orange_precincts = df_pres24[
        df_pres24["county"].isin(LA_ORANGE_COUNTIES)
        & meets_group_threshold(df_pres24, "_cvap_api24_pct", 50)
    ]
    net_shift_maj_asian_la_orange_precincts = calculate_net_shift(
        df_prop50_maj_asian_la_orange_precincts,
        df_pres24_maj_asian_la_orange_precincts,
    )
    return api_cvap_la_orange, net_shift_maj_asian_la_orange_precincts


@app.cell(hide_code=True)
def _(
    mo,
    net_shift_maj_white_precincts,
    pct_dem_maj_white_precincts,
    pct_yes_maj_white_precincts,
):
    mo.md(rf"""
    Static text:
    > Majority-white precincts were the only grouping we observed where the statewide net shift between the 2024 Presidential contest and Prop. 50 was below 10 percentage points. The net shift was 1.6 percentage points: Harris won 56.3% in 2024; Prop. 50 won 58.6%.

    Dynamic text:
    > Majority-white precincts were the only grouping we observed where the statewide net shift between the 2024 Presidential contest and Prop. 50 was below 10 percentage points. The net shift was {net_shift_maj_white_precincts:0.1%} percentage points: Harris won {pct_dem_maj_white_precincts:0.1%} in 2024; Prop. 50 won {pct_yes_maj_white_precincts:0.1%}.
    """)
    return


@app.cell
def _(
    calculate_dem_pct,
    calculate_yes_pct,
    df_pres24,
    df_prop50,
    meets_group_threshold,
):
    df_prop50_maj_white_precincts = df_prop50[
        meets_group_threshold(df_prop50, "CVAP_WHT24_pct", 50)
    ]
    df_pres24_maj_white_precincts = df_pres24[
        meets_group_threshold(df_pres24, "CVAP_WHT24_pct", 50)
    ]
    pct_yes_maj_white_precincts = calculate_yes_pct(df_prop50_maj_white_precincts)
    pct_dem_maj_white_precincts = calculate_dem_pct(df_pres24_maj_white_precincts)
    net_shift_maj_white_precincts = calculate_net_shift(
        df_prop50_maj_white_precincts,
        df_pres24_maj_white_precincts,
    )
    return (
        net_shift_maj_white_precincts,
        pct_dem_maj_white_precincts,
        pct_yes_maj_white_precincts,
    )


@app.cell(hide_code=True)
def _(
    mo,
    net_shift_no_majority_racial_precincts,
    pct_dem_no_majority_racial_precincts,
    pct_yes_no_majority_racial_precincts,
):
    mo.md(rf"""
    Static text:
    > Our analysis of precincts where no racial group comprises a majority found that the difference in support between Harris in 2024 and Prop. 50 roughly matched the shift in majority-Asian and Black precincts statewide: Harris won 60.7% of the vote in 2024 while Prop. 50 won 68.3%.

    Dynamic text:
    > Our analysis of precincts where no single racial or ethnic group exceeds 50% of interpolated CVAP found that the difference in support between Harris in 2024 and Prop. 50 roughly matched the shift in majority-Asian and Black precincts statewide: Harris won {pct_dem_no_majority_racial_precincts:0.1%} of the vote in 2024 while Prop. 50 won {pct_yes_no_majority_racial_precincts:0.1%}, net shift of {net_shift_no_majority_racial_precincts:0.1%}.
    """)
    return


@app.cell
def _(calculate_dem_pct, calculate_yes_pct, df_pres24, df_prop50):
    FOUR_WAY_MAJORITY_PCT_COLUMNS = [
        "_cvap_api24_pct",
        "CVAP_HSP24_pct",
        "CVAP_BLK24_pct",
        "CVAP_WHT24_pct",
    ]


    def is_no_racial_ethnic_majority(_df):
        return _df[FOUR_WAY_MAJORITY_PCT_COLUMNS].max(axis=1) <= 50


    df_prop50_no_majority = df_prop50[is_no_racial_ethnic_majority(df_prop50)]
    df_pres24_no_majority = df_pres24[is_no_racial_ethnic_majority(df_pres24)]
    pct_yes_no_majority_racial_precincts = calculate_yes_pct(df_prop50_no_majority)
    pct_dem_no_majority_racial_precincts = calculate_dem_pct(df_pres24_no_majority)
    net_shift_no_majority_racial_precincts = calculate_net_shift(
        df_prop50_no_majority,
        df_pres24_no_majority,
    )
    return (
        net_shift_no_majority_racial_precincts,
        pct_dem_no_majority_racial_precincts,
        pct_yes_no_majority_racial_precincts,
    )


@app.cell(hide_code=True)
def _(mo, pct_fully_allocated_to_single_precinct):
    mo.md(rf"""
    Static text:
    > Using this methodology, the Statewide Database has determined that 80% of census blocks place all their respective registered voters in the same precinct rather than splitting them across multiple precincts.

    Dynamic text:
    > Using this methodology, the Statewide Database has determined that {pct_fully_allocated_to_single_precinct:0.1%} of census blocks place all their respective registered voters in the same precinct rather than splitting them across multiple precincts.
    """)
    return


@app.cell
def _(pd):
    df_precinct_block_map = pd.read_csv(
        "./inputs/statewide_db/state_g24_sr_blk_map.csv", usecols=["PCTBLK"]
    )
    pct_fully_allocated_to_single_precinct = (
        df_precinct_block_map["PCTBLK"] >= 100
    ).sum() / len(df_precinct_block_map)
    return (pct_fully_allocated_to_single_precinct,)


@app.cell(hide_code=True)
def _(
    min_net_shift_voc_across_majority_thresholds,
    mo,
    net_shift_latino_cvap_gt_90,
    net_shift_white_cvap_gt_90,
):
    mo.md(rf"""
    Static text:
    > We reran our analysis with increasingly high thresholds up to 100% and observed that the net shift towards Prop. 50 remained above +5 percentage points in voter-of-color precincts and reached as high as +36.6 percentage points for precincts where Latino eligible voters are over 90% of the eligible voters. It decreased in majority-white precincts, reaching as low as -7.4 percentage points in precincts where white eligible voters accounted for over 90% of eligible voters.

    Dynamic text:

    > We reran our analysis with increasingly high majority cutoffs from 50% through 100% on the four-way CVAP plurality classification. The net shift towards Prop. 50 stayed at or above {min_net_shift_voc_across_majority_thresholds:0.1%} percentage points in voter-of-color precincts at every cutoff, reached as high as {net_shift_latino_cvap_gt_90:0.1%} percentage points where Latino CVAP share exceeds 90%, and was as low as {net_shift_white_cvap_gt_90:+0.1%} percentage points where white CVAP share exceeds 90%.
    """)
    return


@app.cell
def _(df_pres24, df_prop50, meets_group_threshold):
    MAJORITY_PLURALITY_COLUMNS = [
        "_cvap_api24_pct",
        "CVAP_HSP24_pct",
        "CVAP_BLK24_pct",
        "CVAP_WHT24_pct",
    ]
    COL_TO_GROUP = {
        "_cvap_api24_pct": "asian",
        "CVAP_HSP24_pct": "latino",
        "CVAP_BLK24_pct": "black",
        "CVAP_WHT24_pct": "white",
    }


    def majority_labels_at_threshold(df, threshold):
        sub = df[MAJORITY_PLURALITY_COLUMNS]
        # Avoid pandas FutureWarning: idxmax on all-NA rows (some precincts lack CVAP shares).
        all_na = sub.isna().all(axis=1)
        plurality_col = (
            sub.loc[~all_na].idxmax(axis=1, skipna=True).reindex(sub.index)
        )
        plurality = plurality_col.map(COL_TO_GROUP)
        max_pct = sub.max(axis=1, skipna=True)
        is_majority = max_pct.notna() & (max_pct > threshold)
        return plurality.where(is_majority, "multiracial")


    min_net_shift_voc_across_majority_thresholds = 1.0
    for thr in range(50, 101):
        mp = majority_labels_at_threshold(df_prop50, thr)
        mr = majority_labels_at_threshold(df_pres24, thr)
        ns = calculate_net_shift(
            df_prop50[mp != "white"],
            df_pres24[mr != "white"],
        )
        min_net_shift_voc_across_majority_thresholds = min(
            min_net_shift_voc_across_majority_thresholds,
            ns,
        )

    net_shift_latino_cvap_gt_90 = calculate_net_shift(
        df_prop50[meets_group_threshold(df_prop50, "CVAP_HSP24_pct", 90)],
        df_pres24[meets_group_threshold(df_pres24, "CVAP_HSP24_pct", 90)],
    )
    net_shift_white_cvap_gt_90 = calculate_net_shift(
        df_prop50[meets_group_threshold(df_prop50, "CVAP_WHT24_pct", 90)],
        df_pres24[meets_group_threshold(df_pres24, "CVAP_WHT24_pct", 90)],
    )
    return (
        min_net_shift_voc_across_majority_thresholds,
        net_shift_latino_cvap_gt_90,
        net_shift_white_cvap_gt_90,
    )


@app.cell(hide_code=True)
def _(mo, net_shift_maj_latino_voters):
    mo.md(rf"""
    Static text:
    > We reran a version of our analysis incorporating voter file data from the Statewide Database. We categorized precincts according to whether the majority of the voters are Latino and calculated the net shift.

    Dynamic text:
    > We reran a version of our analysis incorporating voter file data from the Statewide Database. We categorized precincts according to whether the majority of the voters are Latino (excluding counties without SWDB surname estimates) and calculated a net shift of {net_shift_maj_latino_voters:0.1%} percentage points (same Latino-turnout-majority construction as earlier in this notebook).
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
