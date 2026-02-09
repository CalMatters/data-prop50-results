import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analyze demographics
    """)
    return


@app.cell
def _():
    import pathlib

    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.linear_model import LinearRegression
    import pandas as pd
    return LinearRegression, gpd, mo, np, pathlib, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _(precinct_results_blocks):
    TOTAL_YES_VOTES = 7453339
    TOTAL_NO_VOTES = 4116998
    total_votes = TOTAL_YES_VOTES + TOTAL_NO_VOTES

    print(
        f"Out of a total of {total_votes:,} votes cast, there were {TOTAL_YES_VOTES:,} 'Yes' votes and {TOTAL_NO_VOTES:,} 'No' votes on Prop 50.\n"
    )

    analysis_total_votes = precinct_results_blocks["total_votes"].sum()
    analysis_total_votes_pct = analysis_total_votes / total_votes

    print(
        f"Our analysis has processed data representing {analysis_total_votes_pct:.1%} of votes cast"
    )

    analysis_yes_votes = precinct_results_blocks["yes_votes"].sum()
    analysis_no_votes = precinct_results_blocks["no_votes"].sum()

    analysis_yes_proportion = analysis_yes_votes / TOTAL_YES_VOTES
    analysis_no_proportion = analysis_no_votes / TOTAL_NO_VOTES

    print(f"YES VOTES: {analysis_yes_proportion:.1%}")
    print(f"NO VOTES: {analysis_no_proportion:.1%}")
    return


@app.cell
def _():
    VOTE_COUNT_COLUMNS = ["yes_votes", "no_votes", "total_votes"]
    return (VOTE_COUNT_COLUMNS,)


@app.cell
def _():
    # Analysis groups: 4 single-race + multiracial (collapses "Multiracial (X plurality)" variants)
    ANALYSIS_GROUPS = [
        "asian",
        "black_or_african_american",
        "hispanic_or_latino",
        "white",
        "multiracial",
    ]
    GROUP_DISPLAY_LABELS = {
        "asian": "Asian",
        "black_or_african_american": "Black Or African American",
        "hispanic_or_latino": "Hispanic Or Latino",
        "white": "White",
        "multiracial": "Multiracial",
    }
    return ANALYSIS_GROUPS, GROUP_DISPLAY_LABELS


@app.cell
def _():
    # Dictionary mapping standardized group labels to their equivalents in each dataset
    STANDARDIZED_GROUP_LABELS = {
        "asian": {"tracts": "asian_alone_cvap_est", "blocks": "_cvap_api23"},
        "black_or_african_american": {
            "tracts": "black_or_african_american_alone_cvap_est",
            "blocks": "CVAP_BLK23",
        },
        "hispanic_or_latino": {
            "tracts": "hispanic_or_latino_cvap_est",
            "blocks": "CVAP_HSP23",
        },
        "white": {"tracts": "white_alone_cvap_est", "blocks": "CVAP_WHT23"},
    }
    return (STANDARDIZED_GROUP_LABELS,)


@app.cell
def _(STANDARDIZED_GROUP_LABELS):
    # Create percentage version of the mapping
    standardized_group_labels_pct = {
        key: {
            "tracts": value["tracts"].replace("_est", "_est_pct"),
            "blocks": value["blocks"] + "_pct",
        }
        for key, value in STANDARDIZED_GROUP_LABELS.items()
    }
    return (standardized_group_labels_pct,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filepaths
    """)
    return


@app.cell
def _():
    PRECINCT_RESULTS_TRACTS_FP = "./outputs/precincts_results_cvap_tracts.gpkg"
    PRECINCT_RESULTS_BLOCKS_FP = "./outputs/precincts_results_cvap_blocks.gpkg"
    return PRECINCT_RESULTS_BLOCKS_FP, PRECINCT_RESULTS_TRACTS_FP


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _(gpd):
    def read_gis_data(fp, name="", **read_file_kwargs):
        gdf = gpd.read_file(fp, **read_file_kwargs)
        print(f"{name.upper()} COLUMNS: {list(gdf)}\n")
        return gdf
    return (read_gis_data,)


@app.function
def caclulate_pct(numerator, denominator, precision=1):
    return round((numerator / denominator) * 100, precision)


@app.cell
def _(np):
    def calculate_yes_pct(precincts_df):
        df = precincts_df.copy()
        # Handle cases where one column is null and the other is not
        yes_null = df["yes_votes"].isna()
        no_null = df["no_votes"].isna()

        # Replace null with zero when a yes or no vote tally is null
        # but the opposing vote tally is not null (using XOR)
        yes_no_null_xor_mask = yes_null ^ no_null
        df.loc[yes_no_null_xor_mask, ["yes_votes", "no_votes"]] = df.loc[
            yes_no_null_xor_mask, ["yes_votes", "no_votes"]
        ].fillna(0)

        # Only recalculate total_votes for entries that match the xor mask, otherwise use the original total_votes column
        total_votes = df["total_votes"].copy()
        total_votes.loc[yes_no_null_xor_mask] = (
            df.loc[yes_no_null_xor_mask, "yes_votes"]
            + df.loc[yes_no_null_xor_mask, "no_votes"]
        )

        # Initialize yes_pct as null (NaN) where both yes_votes and no_votes are null
        both_null = yes_null & no_null
        df["yes_pct"] = np.nan

        # Calculate yes_pct and no_pct only where total votes are > 0
        valid_total_mask = total_votes > 0
        df.loc[valid_total_mask, "yes_pct"] = caclulate_pct(
            df.loc[valid_total_mask, "yes_votes"], total_votes[valid_total_mask]
        )
        df["no_pct"] = np.nan
        df.loc[valid_total_mask, "no_pct"] = caclulate_pct(
            df.loc[valid_total_mask, "no_votes"], total_votes[valid_total_mask]
        )

        return df
    return (calculate_yes_pct,)


@app.cell
def _(np, pd):
    def get_majority_racial_group(
        row, group_labels_pct, dataset_type, threshold=50
    ):
        """Determine the majority racial group for a single precinct and return both group and percentage.
        If no group exceeds the threshold, return 'Multiracial' with the plurality group and its percentage."""
        # Extract percentages for each racial group, using .get() to handle missing keys gracefully
        group_percentages = {
            group: row.get(group_labels_pct[group][dataset_type])
            for group in group_labels_pct
        }

        valid_percentages = {
            k: v for k, v in group_percentages.items() if pd.notna(v)
        }
        if not valid_percentages:
            return np.nan, np.nan

        plurality_group = max(valid_percentages, key=valid_percentages.get)
        max_percentage = valid_percentages[plurality_group]
        plurality_group_label = plurality_group.replace("_", " ").title()

        # Return majority group if it exceeds threshold, else multiracial label
        if max_percentage > threshold:
            return plurality_group_label, max_percentage
        return f"Multiracial ({plurality_group_label} plurality)", max_percentage
    return (get_majority_racial_group,)


@app.cell
def _(get_majority_racial_group, np, pd):
    def prepare_precinct_results_df(df, vote_count_columns):
        """Replace redacted values with NaN and convert vote columns to numeric."""
        df = df.replace("-1", np.nan).replace(-1, np.nan)
        df[vote_count_columns] = df[vote_count_columns].apply(pd.to_numeric)
        return df


    def add_majority_racial_group(df, group_labels_pct, dataset_type):
        """Add majority_racial_group and majority_racial_group_pct columns."""
        df = df.copy()
        df[["majority_racial_group", "majority_racial_group_pct"]] = df.apply(
            lambda row: pd.Series(
                get_majority_racial_group(row, group_labels_pct, dataset_type)
            ),
            axis=1,
        )
        return df
    return add_majority_racial_group, prepare_precinct_results_df


@app.cell
def _(LinearRegression, np, plt):
    def plot_lnr_yes_pct_vs_cvap(
        df, cvap_column, yes_pct_column, group_label="White", title_suffix=""
    ):
        # Handle NaN values by dropping them for plotting
        plot_data = df.dropna(subset=[cvap_column, yes_pct_column])

        fig, ax = plt.subplots(figsize=(8, 6))

        # Reshape data for sklearn
        X = plot_data[cvap_column].values.reshape(-1, 1)
        y = plot_data[yes_pct_column].values

        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)

        # Predict for line plot
        X_range = np.linspace(0, 100, 100).reshape(-1, 1)
        y_pred = model.predict(X_range)

        # Scatter plot
        ax.scatter(
            plot_data[cvap_column],
            plot_data[yes_pct_column],
            alpha=0.6,
            s=5,
            edgecolor="none",
            label="Precincts",
        )

        # Regression line
        ax.plot(
            X_range[:, 0],
            y_pred,
            color="red",
            linewidth=1,
            label=f"Linear fit: y = {model.coef_[0]:.2f}x + {model.intercept_:.2f}",
        )

        ax.set_xlabel(f"Percent {group_label} Voters")
        ax.set_ylabel("Yes Vote Percentage")
        ax.set_title(
            f"Yes Vote Percentage vs. Percent {group_label} Voters {title_suffix}"
        )
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Set axis limits to ensure full visibility
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        # Use plt.gca() as the last expression
        return plt.gca()
    return (plot_lnr_yes_pct_vs_cvap,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read and prepare data
    """)
    return


@app.cell
def _(
    PRECINCT_RESULTS_BLOCKS_FP,
    PRECINCT_RESULTS_TRACTS_FP,
    VOTE_COUNT_COLUMNS,
    add_majority_racial_group,
    calculate_yes_pct,
    prepare_precinct_results_df,
    read_gis_data,
    standardized_group_labels_pct,
):
    def _load_and_prepare(fp, name):
        df = read_gis_data(fp, name)
        df = prepare_precinct_results_df(df, VOTE_COUNT_COLUMNS)
        return calculate_yes_pct(df)


    precinct_results_blocks = _load_and_prepare(
        PRECINCT_RESULTS_BLOCKS_FP, "blocks"
    )
    precinct_results_tracts = _load_and_prepare(
        PRECINCT_RESULTS_TRACTS_FP, "tracts"
    )

    # Validate null yes_pct count: expected when both votes null or total votes = 0
    null_votes = (
        precinct_results_tracts["yes_votes"].isnull()
        & precinct_results_tracts["no_votes"].isnull()
    )
    total_votes = (
        precinct_results_tracts["yes_votes"] + precinct_results_tracts["no_votes"]
    )
    has_zero_total_votes = total_votes == 0
    expected_null_yes_pct_count = (null_votes | has_zero_total_votes).sum()
    observed_null_yes_pct_count = precinct_results_tracts["yes_pct"].isna().sum()

    assert expected_null_yes_pct_count == observed_null_yes_pct_count, (
        f"Expected {expected_null_yes_pct_count} null values in 'yes_pct' for blocks, "
        f"but found {observed_null_yes_pct_count}."
    )

    precinct_results_blocks = add_majority_racial_group(
        precinct_results_blocks, standardized_group_labels_pct, "blocks"
    )
    precinct_results_tracts = add_majority_racial_group(
        precinct_results_tracts, standardized_group_labels_pct, "tracts"
    )

    # Debug: county distribution of precincts with null yes_pct (validation opportunity)
    precinct_results_blocks.loc[
        precinct_results_blocks["yes_pct"].isna(), "county"
    ].value_counts()
    return precinct_results_blocks, precinct_results_tracts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Majority group precincts

    - Groupby the results by the majority racial demographic group in each precinct

    For example, the first row in each output dataframe represent the aggregate result data for all of the Asian-majority precincts available in our analysis.
    """)
    return


@app.cell
def _(pd):
    # Shared helper to calculate vote statistics from yes/no vote counts
    def _calculate_vote_stats(yes_votes, no_votes):
        total_votes = yes_votes + no_votes
        yes_pct = caclulate_pct(yes_votes, total_votes)
        no_pct = caclulate_pct(no_votes, total_votes)
        return total_votes, yes_pct, no_pct


    def analyze_by_group(
        df, group_key, dataset_type, threshold=50, by_county=False
    ):
        """Analyze vote stats for a demographic group. Returns dict (state-level) or DataFrame (county-level)."""
        if group_key == "multiracial":
            mask = df["majority_racial_group"].str.startswith(
                "Multiracial", na=False
            )
        else:
            formatted_label = group_key.replace("_", " ").title()
            mask = df["majority_racial_group"] == formatted_label

        majority_precincts = df[mask]

        if by_county:
            if majority_precincts.empty:
                return pd.DataFrame(
                    {
                        "county": [],
                        f"{group_key}_{threshold}_precinct_count": [],
                        f"{group_key}_{threshold}_yes_pct": [],
                        f"{group_key}_{threshold}_no_pct": [],
                    },
                ).set_index("county")

            grouped = majority_precincts.groupby("county")
            precinct_counts = grouped.size()
            yes_votes = grouped["yes_votes"].sum()
            no_votes = grouped["no_votes"].sum()
            total_votes, yes_pct, no_pct = _calculate_vote_stats(
                yes_votes, no_votes
            )

            return pd.DataFrame(
                {
                    "county": precinct_counts.index,
                    f"{group_key}_{threshold}_precinct_count": precinct_counts.values,
                    f"{group_key}_{threshold}_yes_pct": yes_pct.values,
                    f"{group_key}_{threshold}_no_pct": no_pct.values,
                    f"{group_key}_{threshold}_total_votes": total_votes.values,
                },
            ).set_index("county")
        else:
            total_yes_votes = majority_precincts["yes_votes"].sum()
            total_no_votes = majority_precincts["no_votes"].sum()
            total_votes, yes_split_pct, no_split_pct = _calculate_vote_stats(
                total_yes_votes, total_no_votes
            )
            return {
                "group": group_key,
                "dataset_type": dataset_type,
                "threshold": threshold,
                "num_precincts": len(majority_precincts),
                "total_votes": total_votes,
                "yes_votes": total_yes_votes,
                "no_votes": total_no_votes,
                "yes_split_pct": yes_split_pct,
                "no_split_pct": no_split_pct,
            }
    return (analyze_by_group,)


@app.cell
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    analyze_by_group,
    pd,
    precinct_results_blocks,
    precinct_results_tracts,
):
    # State-level analysis
    majority_analysis_results_blocks = {
        group: analyze_by_group(
            precinct_results_blocks, group, dataset_type="blocks", by_county=False
        )
        for group in ANALYSIS_GROUPS
    }
    majority_analysis_results_tracts = {
        group: analyze_by_group(
            precinct_results_tracts, group, dataset_type="tracts", by_county=False
        )
        for group in ANALYSIS_GROUPS
    }

    majority_analysis_blocks_df = pd.DataFrame(majority_analysis_results_blocks).T
    majority_analysis_tracts_df = pd.DataFrame(majority_analysis_results_tracts).T
    majority_analysis_blocks_df.index = [
        GROUP_DISPLAY_LABELS[g] for g in ANALYSIS_GROUPS
    ]
    majority_analysis_tracts_df.index = [
        GROUP_DISPLAY_LABELS[g] for g in ANALYSIS_GROUPS
    ]
    return majority_analysis_blocks_df, majority_analysis_tracts_df


@app.cell
def _(
    ANALYSIS_GROUPS,
    analyze_by_group,
    pd,
    precinct_results_blocks,
    precinct_results_tracts,
):
    # County-level analysis
    county_level_demo_analysis_blocks, county_level_demo_analysis_tracts = (
        pd.concat(
            [
                analyze_by_group(_dataset, g, dataset_type=_type, by_county=True)
                for g in ANALYSIS_GROUPS
            ],
            axis=1,
        )
        for _type, _dataset in [
            ("blocks", precinct_results_blocks),
            ("tracts", precinct_results_tracts),
        ]
    )

    precinct_count_cols_blocks = [
        col
        for col in county_level_demo_analysis_blocks.columns
        if col.endswith("_precinct_count")
    ]
    precinct_count_cols_tracts = [
        col
        for col in county_level_demo_analysis_tracts.columns
        if col.endswith("_precinct_count")
    ]

    county_level_demo_analysis_blocks[precinct_count_cols_blocks] = (
        county_level_demo_analysis_blocks[precinct_count_cols_blocks].fillna(0)
    )
    county_level_demo_analysis_tracts[precinct_count_cols_tracts] = (
        county_level_demo_analysis_tracts[precinct_count_cols_tracts].fillna(0)
    )
    return county_level_demo_analysis_blocks, county_level_demo_analysis_tracts


@app.cell
def _(county_level_demo_analysis_blocks, mo):
    counties = list(county_level_demo_analysis_blocks.index)
    county_dropdown = mo.ui.dropdown(counties, value=counties[0], searchable=True)
    return (county_dropdown,)


@app.cell
def _(
    GROUP_DISPLAY_LABELS,
    county_dropdown,
    county_level_demo_analysis_blocks,
    county_level_demo_analysis_tracts,
    pd,
):
    def _transform_county_series_to_dataframe(series):
        # Extract columns that end with "_yes_pct" to identify demographic groups
        yes_pct_cols = [col for col in series.index if col.endswith("_yes_pct")]

        data = []
        for pct_col in yes_pct_cols:
            group_key = pct_col.split("_50_yes_pct")[0]
            precinct_col = pct_col.replace("_yes_pct", "_precinct_count")
            no_pct_col = pct_col.replace("_yes_pct", "_no_pct")

            data.append(
                {
                    "precinct_count": series[precinct_col],
                    "total_votes": series[f"{group_key}_50_total_votes"],
                    "yes_pct": series[pct_col],
                    "no_pct": series[no_pct_col],
                }
            )

        display_labels = [
            GROUP_DISPLAY_LABELS[col.split("_50_yes_pct")[0]]
            for col in yes_pct_cols
        ]
        df = pd.DataFrame(data, index=display_labels)
        df["total_votes_pct"] = caclulate_pct(
            df["total_votes"], df["total_votes"].sum()
        )
        return df


    {
        "County": county_dropdown,
        "BLOCKS": _transform_county_series_to_dataframe(
            county_level_demo_analysis_blocks.loc[county_dropdown.value]
        ),
        "TRACTS": _transform_county_series_to_dataframe(
            county_level_demo_analysis_tracts.loc[county_dropdown.value]
        ),
    }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demographic scatterplot and linear regression

    Linear regression is plotted for exploratory purposes. We would need to [validate the assumptions required](https://online.stat.psu.edu/stat200/lesson/12/12.3/12.3.2) to use linear regression in our final analysis. The results by majority group is currently the preferred analysis tool.
    """)
    return


@app.cell
def _(mo, standardized_group_labels_pct):
    demo_group_dropdown = mo.ui.dropdown(
        options=standardized_group_labels_pct.keys(), value="white"
    )
    demo_group_dropdown
    return (demo_group_dropdown,)


@app.cell
def _(
    demo_group_dropdown,
    plot_lnr_yes_pct_vs_cvap,
    precinct_results_blocks,
    standardized_group_labels_pct,
):
    plot_lnr_yes_pct_vs_cvap(
        precinct_results_blocks,
        standardized_group_labels_pct[demo_group_dropdown.value]["blocks"],
        "yes_pct",
        demo_group_dropdown.value.title().replace("_", " "),
        "(Blocks)",
    )
    return


@app.cell
def _(
    demo_group_dropdown,
    plot_lnr_yes_pct_vs_cvap,
    precinct_results_tracts,
    standardized_group_labels_pct,
):
    plot_lnr_yes_pct_vs_cvap(
        precinct_results_tracts,
        standardized_group_labels_pct[demo_group_dropdown.value]["tracts"],
        "yes_pct",
        demo_group_dropdown.value.title().replace("_", " "),
        "(Tracts)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demographic correlation coefficient

    [User's guide to correlation coefficients](https://pmc.ncbi.nlm.nih.gov/articles/PMC6107969/#sec2)

    Correlation coefficient is a fine exploratory tool, but our data likely does not meet the requirements for this test.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Blocks
    """)
    return


@app.cell
def _(demo_group_dropdown):
    demo_group_dropdown
    return


@app.cell
def _(
    demo_group_dropdown,
    precinct_results_blocks,
    standardized_group_labels_pct,
):
    precinct_results_blocks[
        [
            standardized_group_labels_pct[demo_group_dropdown.value]["blocks"],
            "yes_pct",
        ]
    ].dropna().corr(method="pearson")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tracts
    """)
    return


@app.cell
def _(
    demo_group_dropdown,
    precinct_results_tracts,
    standardized_group_labels_pct,
):
    precinct_results_tracts[
        [
            standardized_group_labels_pct[demo_group_dropdown.value]["tracts"],
            "yes_pct",
        ]
    ].dropna().corr(method="pearson")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hypothesis testing

    For both of the following hypothesis, we are looking at how specific demographic groups voted. I first output how precincts where the majority of voting-age citizens belong to that racial demographic group, then I output a scatter plot with a linear regression plotted.

    The linear regression is an exploration tool, not a thorough analysis of the relation between racial demographics and support for Prop 50.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Hypothesis #1:

    > The more Hispanic or Latino voters (%) there are in a precinct, the higher the vote share for "Yes" on Prop. 50
    """)
    return


@app.cell
def _(majority_analysis_blocks_df, majority_analysis_tracts_df):
    # what were the results in majority hispanic or latino precincts?
    (
        majority_analysis_blocks_df.loc["Hispanic Or Latino"],
        majority_analysis_tracts_df.loc["Hispanic Or Latino"],
    )
    return


@app.cell
def _(
    plot_lnr_yes_pct_vs_cvap,
    precinct_results_blocks,
    standardized_group_labels_pct,
):
    plot_lnr_yes_pct_vs_cvap(
        precinct_results_blocks,
        standardized_group_labels_pct["hispanic_or_latino"]["blocks"],
        "yes_pct",
        "Hispanic or Latino",
        "(Blocks)",
    )
    return


@app.cell
def _(
    plot_lnr_yes_pct_vs_cvap,
    precinct_results_tracts,
    standardized_group_labels_pct,
):
    plot_lnr_yes_pct_vs_cvap(
        precinct_results_tracts,
        standardized_group_labels_pct["hispanic_or_latino"]["tracts"],
        "yes_pct",
        "Hispanic or Latino",
        "(Tracts)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Hypothesis #2:

    > If there are more white voters in a precinct, then there will be a higher vote share for "No" on Prop. 50
    """)
    return


@app.cell
def _(majority_analysis_blocks_df, majority_analysis_tracts_df):
    # what were the results in majority white precincts?
    (
        majority_analysis_blocks_df.loc["White"],
        majority_analysis_tracts_df.loc["White"],
    )
    return


@app.cell
def _(
    plot_lnr_yes_pct_vs_cvap,
    precinct_results_blocks,
    standardized_group_labels_pct,
):
    plot_lnr_yes_pct_vs_cvap(
        precinct_results_blocks,
        standardized_group_labels_pct["white"]["blocks"],
        "yes_pct",
        "White",
        "(Blocks)",
    )
    return


@app.cell
def _(
    plot_lnr_yes_pct_vs_cvap,
    precinct_results_tracts,
    standardized_group_labels_pct,
):
    plot_lnr_yes_pct_vs_cvap(
        precinct_results_tracts,
        standardized_group_labels_pct["white"]["tracts"],
        "yes_pct",
        "White",
        "(Tracts)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Appendix
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export GIS file
    """)
    return


@app.cell
def _():
    MAP_EXPORT_COLUMNS = [
        "county",
        "precinct_id",
        "yes_votes",
        "no_votes",
        "total_votes",
        "yes_pct",
        "no_pct",
        "majority_racial_group",
        "majority_racial_group_pct",
        "geometry",
    ]
    return (MAP_EXPORT_COLUMNS,)


@app.cell
def _():
    MAP_EXPORT_PATH = "./outputs/precinct_results_plus_demographics.geojson"
    MAP_EXPORT_DRIVER = "geojson"
    return MAP_EXPORT_DRIVER, MAP_EXPORT_PATH


@app.cell
def _(
    MAP_EXPORT_COLUMNS,
    np,
    pd,
    precinct_results_blocks,
    precinct_results_tracts,
    standardized_group_labels_pct,
):
    def get_majority_racial_group(
        row, group_labels_pct, dataset_type, threshold=50
    ):
        """Determine the majority racial group for a single precinct and return both group and percentage.
        If no group exceeds the threshold, return 'Multiracial' with the plurality group and its percentage."""
        # Extract percentages for each racial group, using .get() to handle missing keys gracefully
        group_percentages = {
            group: row.get(group_labels_pct[group][dataset_type])
            for group in group_labels_pct
        }

        valid_percentages = {
            k: v for k, v in group_percentages.items() if pd.notna(v)
        }
        if not valid_percentages:
            return np.nan, np.nan

        plurality_group = max(valid_percentages, key=valid_percentages.get)
        max_percentage = valid_percentages[plurality_group]
        plurality_group_label = plurality_group.replace("_", " ").title()

        # Return majority group if it exceeds threshold, else multiracial label
        if max_percentage > threshold:
            return plurality_group_label, max_percentage
        return f"Multiracial ({plurality_group_label} plurality)", max_percentage


    # Apply to create majority_racial_group and majority_racial_group_pct columns for blocks data
    precinct_results_blocks[
        ["majority_racial_group", "majority_racial_group_pct"]
    ] = precinct_results_blocks.apply(
        lambda row: pd.Series(
            get_majority_racial_group(row, standardized_group_labels_pct, "blocks")
        ),
        axis=1,
    )

    # Apply to create majority_racial_group and majority_racial_group_pct columns for tracts data
    precinct_results_tracts[
        ["majority_racial_group", "majority_racial_group_pct"]
    ] = precinct_results_tracts.apply(
        lambda row: pd.Series(
            get_majority_racial_group(row, standardized_group_labels_pct, "tracts")
        ),
        axis=1,
    )

    precinct_results_blocks[MAP_EXPORT_COLUMNS]
    return


@app.cell
def _(
    MAP_EXPORT_COLUMNS,
    MAP_EXPORT_DRIVER,
    MAP_EXPORT_PATH,
    pathlib,
    precinct_results_blocks,
):
    # Check if the file exists and delete it before writing
    path = pathlib.Path(MAP_EXPORT_PATH)
    if path.exists():
        path.unlink()

    precinct_results_blocks[MAP_EXPORT_COLUMNS].to_file(
        MAP_EXPORT_PATH, driver=MAP_EXPORT_DRIVER
    )
    return


if __name__ == "__main__":
    app.run()
