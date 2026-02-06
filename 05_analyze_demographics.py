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
    # Maps schema type -> {standard_name: source_column_name}
    DEMOGRAPHIC_COLUMN_MAPPING = {
        "blocks": {
            "asian_pct": "_cvap_api23_pct",  # Asian+PI from 02b_census
            "black_or_african_american_pct": "CVAP_BLK23_pct",
            "hispanic_or_latino_pct": "CVAP_HSP23_pct",
            "white_pct": "CVAP_WHT23_pct",
        },
        "tracts": {
            "asian_pct": "asian_alone_cvap_est_pct",
            "black_or_african_american_pct": "black_or_african_american_alone_cvap_est_pct",
            "hispanic_or_latino_pct": "hispanic_or_latino_cvap_est_pct",
            "white_pct": "white_alone_cvap_est_pct",
        },
    }
    return (DEMOGRAPHIC_COLUMN_MAPPING,)


@app.cell
def _():
    VOTE_DISPLAY_PROP50 = {"yes": "Yes %", "no": "No %"}
    VOTE_DISPLAY_2024 = {"yes": "Democrat %", "no": "Republican %"}

    DATASET_CONFIG = [
        {
            "id": "blocks",
            "filepath": "./outputs/precincts_results_cvap_blocks.gpkg",
            "display_name": "Blocks (Prop 50)",
            "group_labels_key": "blocks",
            "vote_column_mapping": {
                "yes_votes": "yes_votes",
                "no_votes": "no_votes",
            },
            "vote_display_labels": VOTE_DISPLAY_PROP50,
        },
        {
            "id": "blocks_2024",
            "filepath": "./outputs/precincts_2024_results_cvap_blocks.gpkg",
            "display_name": "Blocks (2024 Presidential)",
            "group_labels_key": "blocks",
            "vote_column_mapping": {
                "yes_votes": "dem_votes",
                "no_votes": "rep_votes",
            },
            "vote_display_labels": VOTE_DISPLAY_2024,
        },
        {
            "id": "tracts",
            "filepath": "./outputs/precincts_results_cvap_tracts.gpkg",
            "display_name": "Tracts (Prop 50)",
            "group_labels_key": "tracts",
            "vote_column_mapping": {
                "yes_votes": "yes_votes",
                "no_votes": "no_votes",
            },
            "vote_display_labels": VOTE_DISPLAY_PROP50,
        },
    ]
    return (DATASET_CONFIG,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filepaths
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _(DEMOGRAPHIC_COLUMN_MAPPING, gpd):
    def read_gis_data(fp, name="", **read_file_kwargs):
        gdf = gpd.read_file(fp, **read_file_kwargs)
        print(f"{name.upper()} COLUMNS: {list(gdf)}\n")
        return gdf


    def standardize_vote_columns(df, vote_column_mapping):
        """Rename source vote columns to standard yes_votes/no_votes. Adds total_votes if missing."""
        rename_map = {v: k for k, v in vote_column_mapping.items()}
        df = df.rename(columns=rename_map)
        if "total_votes" not in df.columns:
            df["total_votes"] = df["yes_votes"] + df["no_votes"]
        return df


    def standardize_demographic_columns(df, group_labels_key):
        """Rename source demographic pct columns to standard names."""
        mapping = DEMOGRAPHIC_COLUMN_MAPPING[group_labels_key]
        rename_map = {v: k for k, v in mapping.items() if v in df.columns}
        return df.rename(columns=rename_map)
    return (
        read_gis_data,
        standardize_demographic_columns,
        standardize_vote_columns,
    )


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
def _(ANALYSIS_GROUPS, np, pd):
    def get_majority_racial_group(row, threshold=50):
        """Determine the majority racial group for a single precinct and return both group and percentage.
        If no group exceeds the threshold, return 'Multiracial' with the plurality group and its percentage."""
        demographic_groups = [g for g in ANALYSIS_GROUPS if g != "multiracial"]
        group_percentages = {
            group: row.get(f"{group}_pct") for group in demographic_groups
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


    def add_majority_racial_group(df):
        """Add majority_racial_group and majority_racial_group_pct columns."""
        df = df.copy()
        df[["majority_racial_group", "majority_racial_group_pct"]] = df.apply(
            lambda row: pd.Series(get_majority_racial_group(row)),
            axis=1,
        )
        return df
    return add_majority_racial_group, prepare_precinct_results_df


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read and prepare data
    """)
    return


@app.cell
def _(
    DATASET_CONFIG,
    VOTE_COUNT_COLUMNS,
    add_majority_racial_group,
    calculate_yes_pct,
    prepare_precinct_results_df,
    read_gis_data,
    standardize_demographic_columns,
    standardize_vote_columns,
):
    precinct_results = {}
    for _cfg in DATASET_CONFIG:
        df = read_gis_data(_cfg["filepath"], _cfg["id"])
        df = standardize_vote_columns(df, _cfg["vote_column_mapping"])
        df = standardize_demographic_columns(df, _cfg["group_labels_key"])
        df = prepare_precinct_results_df(df, VOTE_COUNT_COLUMNS)
        df = calculate_yes_pct(df)
        df = add_majority_racial_group(df)
        precinct_results[_cfg["id"]] = df

    # Validate null yes_pct count on tracts dataset
    _df_validate = precinct_results["tracts"]
    null_votes = (
        _df_validate["yes_votes"].isnull() & _df_validate["no_votes"].isnull()
    )
    total_votes = _df_validate["yes_votes"] + _df_validate["no_votes"]
    has_zero_total_votes = total_votes == 0
    expected_null_yes_pct_count = (null_votes | has_zero_total_votes).sum()
    observed_null_yes_pct_count = _df_validate["yes_pct"].isna().sum()
    assert expected_null_yes_pct_count == observed_null_yes_pct_count, (
        f"Expected {expected_null_yes_pct_count} null values in 'yes_pct', "
        f"but found {observed_null_yes_pct_count}."
    )

    # Debug: county distribution of precincts with null yes_pct (validation opportunity)
    precinct_results["blocks"].loc[
        precinct_results["blocks"]["yes_pct"].isna(), "county"
    ].value_counts()
    return (precinct_results,)


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
    def _calculate_vote_stats(yes_votes, no_votes, total_votes=None):
        if total_votes is None:
            total_votes = yes_votes + no_votes
        yes_pct = caclulate_pct(yes_votes, total_votes)
        no_pct = caclulate_pct(no_votes, total_votes)
        return total_votes, yes_pct, no_pct


    def _get_majority_precincts(df, group_key):
        """Filter df to precincts where majority_racial_group matches group_key."""
        if group_key == "multiracial":
            mask = df["majority_racial_group"].str.startswith(
                "Multiracial", na=False
            )
        else:
            formatted_label = group_key.replace("_", " ").title()
            mask = df["majority_racial_group"] == formatted_label
        return df[mask]


    def analyze_by_group_state(df, group_key, threshold=50):
        """Analyze vote stats for a demographic group at state level. Returns dict."""
        majority_precincts = _get_majority_precincts(df, group_key)
        total_yes_votes = majority_precincts["yes_votes"].sum()
        total_no_votes = majority_precincts["no_votes"].sum()
        total_votes_grouped = majority_precincts["total_votes"].sum()
        total_votes, yes_split_pct, no_split_pct = _calculate_vote_stats(
            total_yes_votes, total_no_votes, total_votes_grouped
        )
        return {
            "group": group_key,
            "threshold": threshold,
            "num_precincts": len(majority_precincts),
            "total_votes": total_votes,
            "yes_votes": total_yes_votes,
            "no_votes": total_no_votes,
            "yes_split_pct": yes_split_pct,
            "no_split_pct": no_split_pct,
        }


    def analyze_by_group_county(df, group_key, threshold=50):
        """Analyze vote stats for a demographic group by county. Returns DataFrame."""
        majority_precincts = _get_majority_precincts(df, group_key)
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
        total_votes_grouped = grouped["total_votes"].sum()
        total_votes, yes_pct, no_pct = _calculate_vote_stats(
            yes_votes, no_votes, total_votes_grouped
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


    def analyze_by_group(df, group_key, threshold=50, by_county=False):
        """Analyze vote stats for a demographic group. Returns dict (state) or DataFrame (county)."""
        if by_county:
            return analyze_by_group_county(df, group_key, threshold)
        return analyze_by_group_state(df, group_key, threshold)
    return (analyze_by_group,)


@app.cell
def _(
    ANALYSIS_GROUPS,
    DATASET_CONFIG,
    GROUP_DISPLAY_LABELS,
    analyze_by_group,
    pd,
    precinct_results,
):
    majority_analysis = {}
    for _cfg in DATASET_CONFIG:
        _df = pd.DataFrame(
            {
                g: analyze_by_group(
                    precinct_results[_cfg["id"]], g, by_county=False
                )
                for g in ANALYSIS_GROUPS
            }
        ).T
        _df.index = [GROUP_DISPLAY_LABELS[g] for g in ANALYSIS_GROUPS]
        _df = _df.rename(
            columns={
                "yes_split_pct": _cfg["vote_display_labels"]["yes"],
                "no_split_pct": _cfg["vote_display_labels"]["no"],
            }
        )
        majority_analysis[_cfg["id"]] = _df
    return (majority_analysis,)


@app.cell
def _(DATASET_CONFIG, majority_analysis, mo):
    mo.vstack(
        [
            mo.vstack(
                [
                    mo.md(f"### {_cfg['display_name']}"),
                    majority_analysis[_cfg["id"]],
                ]
            )
            for _cfg in DATASET_CONFIG
        ]
    )
    return


@app.cell
def _(ANALYSIS_GROUPS, DATASET_CONFIG, analyze_by_group, pd, precinct_results):
    county_level_demo_analysis = {}
    for _cfg in DATASET_CONFIG:
        _df = pd.concat(
            [
                analyze_by_group(precinct_results[_cfg["id"]], g, by_county=True)
                for g in ANALYSIS_GROUPS
            ],
            axis=1,
        )
        precinct_count_cols = [
            col for col in _df.columns if col.endswith("_precinct_count")
        ]
        _df[precinct_count_cols] = _df[precinct_count_cols].fillna(0)
        county_level_demo_analysis[_cfg["id"]] = _df
    return (county_level_demo_analysis,)


@app.cell
def _(county_level_demo_analysis, mo):
    counties = list(county_level_demo_analysis["blocks"].index)
    county_dropdown = mo.ui.dropdown(counties, value=counties[0], searchable=True)
    return (county_dropdown,)


@app.cell
def _(
    DATASET_CONFIG,
    GROUP_DISPLAY_LABELS,
    county_dropdown,
    county_level_demo_analysis,
    pd,
):
    def _transform_county_series_to_dataframe(series, vote_display_labels):
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
                    vote_display_labels["yes"]: series[pct_col],
                    vote_display_labels["no"]: series[no_pct_col],
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


    _county = county_dropdown.value
    {
        "County": county_dropdown,
        **{
            _cfg["display_name"]: _transform_county_series_to_dataframe(
                county_level_demo_analysis[_cfg["id"]].loc[_county],
                _cfg["vote_display_labels"],
            )
            for _cfg in DATASET_CONFIG
            if _county in county_level_demo_analysis[_cfg["id"]].index
        },
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
def _(LinearRegression, np, plt):
    def plot_lnr_yes_pct_vs_cvap(
        df,
        cvap_column,
        yes_pct_column,
        group_label="White",
        title_suffix="",
        y_label="Yes Vote Percentage",
    ):
        plot_data = df.dropna(subset=[cvap_column, yes_pct_column])

        fig, ax = plt.subplots(figsize=(8, 6))

        X = plot_data[cvap_column].values.reshape(-1, 1)
        y = plot_data[yes_pct_column].values

        model = LinearRegression()
        model.fit(X, y)

        X_range = np.linspace(0, 100, 100).reshape(-1, 1)
        y_pred = model.predict(X_range)

        ax.scatter(
            plot_data[cvap_column],
            plot_data[yes_pct_column],
            alpha=0.6,
            s=5,
            edgecolor="none",
            label="Precincts",
        )

        ax.plot(
            X_range[:, 0],
            y_pred,
            color="red",
            linewidth=1,
            label=f"Linear fit: y = {model.coef_[0]:.2f}x + {model.intercept_:.2f}",
        )

        ax.set_xlabel(f"Percent {group_label} Voters")
        ax.set_ylabel(y_label)
        ax.set_title(f"{y_label} vs. Percent {group_label} Voters {title_suffix}")
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        return plt.gca()
    return (plot_lnr_yes_pct_vs_cvap,)


@app.cell
def _(ANALYSIS_GROUPS, mo):
    demo_group_dropdown = mo.ui.dropdown(
        options=[g for g in ANALYSIS_GROUPS if g != "multiracial"],
        value="white",
    )
    return (demo_group_dropdown,)


@app.cell
def _(
    DATASET_CONFIG,
    demo_group_dropdown,
    plot_lnr_yes_pct_vs_cvap,
    precinct_results,
):
    _group = demo_group_dropdown.value
    _cvap_col = f"{_group}_pct"
    _group_label = _group.replace("_", " ").title()
    (
        demo_group_dropdown,
        *[
            plot_lnr_yes_pct_vs_cvap(
                precinct_results[_cfg["id"]],
                _cvap_col,
                "yes_pct",
                _group_label,
                f"({_cfg['display_name']})",
                y_label=f"{_cfg['vote_display_labels']['yes'].replace(' %', '')} Vote Percentage",
            )
            for _cfg in DATASET_CONFIG
        ],
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


@app.cell
def _(DATASET_CONFIG, demo_group_dropdown, precinct_results):
    _group = demo_group_dropdown.value
    _cvap_col = f"{_group}_pct"
    (
        demo_group_dropdown,
        {
            _cfg["display_name"]: precinct_results[_cfg["id"]][
                [_cvap_col, "yes_pct"]
            ]
            .dropna()
            .corr(method="pearson")
            for _cfg in DATASET_CONFIG
        },
    )
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
def _():
    # what were the results in majority hispanic or latino precincts?
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Hypothesis #2:

    > If there are more white voters in a precinct, then there will be a higher vote share for "No" on Prop. 50
    """)
    return


@app.cell
def _():
    # what were the results in majority white precincts?
    return


@app.cell
def _():
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
    MAP_EXPORT_DRIVER = "geojson"
    return (MAP_EXPORT_DRIVER,)


@app.cell
def _(
    DATASET_CONFIG,
    MAP_EXPORT_COLUMNS,
    MAP_EXPORT_DRIVER,
    pathlib,
    precinct_results,
):
    for _cfg in DATASET_CONFIG:
        _path = pathlib.Path(
            f"./outputs/precinct_results_plus_demographics_{_cfg['id']}.geojson"
        )
        if _path.exists():
            _path.unlink()
        _cols = [
            c
            for c in MAP_EXPORT_COLUMNS
            if c in precinct_results[_cfg["id"]].columns
        ]
        precinct_results[_cfg["id"]][_cols].to_file(
            str(_path), driver=MAP_EXPORT_DRIVER
        )
    return


if __name__ == "__main__":
    app.run()
