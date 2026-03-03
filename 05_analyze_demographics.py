import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")

with app.setup:
    import json
    import pathlib

    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.linear_model import LinearRegression
    import pandas as pd


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Analyze demographics
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    DEFAULT_MAJORITY_THRESHOLD = 50
    threshold_slider = mo.ui.slider(
        start=0,
        stop=100,
        step=1,
        value=DEFAULT_MAJORITY_THRESHOLD,
        debounce=True,
        include_input=True,
        label="### Threshold for racial group categorization",
    )
    threshold_slider
    return (threshold_slider,)


@app.cell
def _(threshold_slider):
    VOTE_STANDARD = ("yes_votes", "no_votes", "total_votes")
    DEMOGRAPHIC_STANDARD = (
        "asian_pct",
        "black_or_african_american_pct",
        "hispanic_or_latino_pct",
        "white_pct",
    )
    filter_threshold = threshold_slider.value
    return VOTE_STANDARD, filter_threshold


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
    # Maps schema type -> {source_column_name: standard_name}
    # Blocks GPKG: CVAP_BLK23_pct, CVAP_HSP23_pct, CVAP_WHT23_pct, _cvap_api23_pct (from 02b_census)
    # Tracts GPKG: asian_alone_cvap_est_pct, black_or_african_american_alone_cvap_est_pct, ... (from 02_census)
    DEMOGRAPHIC_SOURCE_TO_STANDARD = {
        "blocks": {
            "_cvap_api24_pct": "asian_pct",  # Asian+PI from 02b_census
            "CVAP_BLK24_pct": "black_or_african_american_pct",
            "CVAP_HSP24_pct": "hispanic_or_latino_pct",
            "CVAP_WHT24_pct": "white_pct",
        },
        "tracts": {
            "asian_alone_cvap_est_pct": "asian_pct",
            "black_or_african_american_alone_cvap_est_pct": "black_or_african_american_pct",
            "hispanic_or_latino_cvap_est_pct": "hispanic_or_latino_pct",
            "white_alone_cvap_est_pct": "white_pct",
        },
    }
    return (DEMOGRAPHIC_SOURCE_TO_STANDARD,)


@app.cell
def _():
    VOTE_DISPLAY_PROP50 = {"yes": "Yes %", "no": "No %"}
    # mapping yes / no to Dem / Rep to correspond with the partisan gerrymander
    VOTE_DISPLAY_2024 = {"yes": "Democrat %", "no": "Republican %"}

    DATASET_CONFIG = [
        {
            "id": "blocks",
            "filepath": "./outputs/precincts_results_cvap_blocks.gpkg",
            "display_name": "Prop 50 (Blocks)",
            "demographic_schema": "blocks",
            "vote_source_to_standard": {
                "yes_votes": "yes_votes",
                "no_votes": "no_votes",
            },
            "vote_display_labels": VOTE_DISPLAY_PROP50,
        },
        {
            "id": "blocks_2024",
            "filepath": "./outputs/precincts_2024_results_cvap_blocks.gpkg",
            "display_name": "2024 Presidential (Blocks)",
            "demographic_schema": "blocks",
            "vote_source_to_standard": {
                "dem_votes": "yes_votes",
                "rep_votes": "no_votes",
            },
            "vote_display_labels": VOTE_DISPLAY_2024,
        },
        {
            "id": "tracts",
            "filepath": "./outputs/precincts_results_cvap_tracts.gpkg",
            "display_name": "Prop 50 (Tracts)",
            "demographic_schema": "tracts",
            "vote_source_to_standard": {
                "yes_votes": "yes_votes",
                "no_votes": "no_votes",
            },
            "vote_display_labels": VOTE_DISPLAY_PROP50,
        },
    ]

    display_options = [
        config_option["display_name"] for config_option in DATASET_CONFIG
    ]
    return DATASET_CONFIG, display_options


@app.cell
def _(DATASET_CONFIG, config_data_options_multiselect):
    dataset_config = [
        config_entry
        for config_entry in DATASET_CONFIG
        if config_entry["display_name"] in config_data_options_multiselect.value
    ]
    return (dataset_config,)


@app.cell
def _(display_options):
    config_data_options_multiselect = mo.ui.multiselect(
        options=display_options, value=display_options
    )
    return (config_data_options_multiselect,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _(DEMOGRAPHIC_SOURCE_TO_STANDARD):
    def read_gis_data(fp, name="", **read_file_kwargs):
        gdf = gpd.read_file(fp, **read_file_kwargs)
        print(f"{name.upper()} COLUMNS: {list(gdf)}\n")
        return gdf


    def standardize_vote_columns(df, vote_source_to_standard):
        """Rename source vote columns to standard yes_votes/no_votes. Adds total_votes if missing."""
        rename_map = {
            k: v for k, v in vote_source_to_standard.items() if k in df.columns
        }
        df = df.rename(columns=rename_map)
        if "total_votes" not in df.columns:
            df["total_votes"] = df["yes_votes"] + df["no_votes"]
        return df


    def standardize_demographic_columns(df, demographic_schema):
        """Rename source demographic pct columns to standard names."""
        mapping = DEMOGRAPHIC_SOURCE_TO_STANDARD[demographic_schema]
        rename_map = {k: v for k, v in mapping.items() if k in df.columns}
        return df.rename(columns=rename_map)

    return (
        read_gis_data,
        standardize_demographic_columns,
        standardize_vote_columns,
    )


@app.function
def caclulate_pct(numerator, denominator, precision=1):
    return round((numerator / denominator) * 100, precision)


@app.function
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


@app.cell
def _(ANALYSIS_GROUPS, filter_threshold):
    def get_majority_racial_group(row, threshold=filter_threshold):
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
def _(get_majority_racial_group):
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
def _():
    mo.md(r"""
    # Read and prepare data
    """)
    return


@app.cell
def _(config_data_options_multiselect):
    mo.vstack(
        [
            mo.md("## Select datasets"),
            config_data_options_multiselect,
            mo.md(f"**Datasets: {config_data_options_multiselect.value}**"),
        ]
    )
    return


@app.cell
def _(
    VOTE_STANDARD,
    add_majority_racial_group,
    dataset_config,
    prepare_precinct_results_df,
    read_gis_data,
    standardize_demographic_columns,
    standardize_vote_columns,
):
    precinct_results = {}
    for _cfg in dataset_config:
        df = read_gis_data(_cfg["filepath"], _cfg["id"])
        df = standardize_vote_columns(df, _cfg["vote_source_to_standard"])
        df = standardize_demographic_columns(df, _cfg["demographic_schema"])
        df = prepare_precinct_results_df(df, list(VOTE_STANDARD))
        df = calculate_yes_pct(df)
        df = add_majority_racial_group(df)
        precinct_results[_cfg["id"]] = df

    # Validate null yes_pct count on tracts dataset
    _df_validate = precinct_results["tracts"]
    null_votes = (
        _df_validate["yes_votes"].isnull() & _df_validate["no_votes"].isnull()
    )
    _total_votes = _df_validate["yes_votes"] + _df_validate["no_votes"]
    has_zero_total_votes = _total_votes == 0
    expected_null_yes_pct_count = (null_votes | has_zero_total_votes).sum()
    observed_null_yes_pct_count = _df_validate["yes_pct"].isna().sum()
    assert expected_null_yes_pct_count == observed_null_yes_pct_count, (
        f"Expected {expected_null_yes_pct_count} null values in 'yes_pct', "
        f"but found {observed_null_yes_pct_count}."
    )

    # Calculate vote shift from Harris to YES on Prop. 50
    precinct_2025_results = precinct_results["blocks"]
    precinct_2025_results["dem_pct_2024"] = caclulate_pct(
        precinct_2025_results["dem_votes"],
        precinct_2025_results["total_votes_2024"],
    )
    precinct_2025_results["rep_pct_2024"] = caclulate_pct(
        precinct_2025_results["dem_votes"],
        precinct_2025_results["total_votes_2024"],
    )
    precinct_2025_results["vote_shift"] = round(
        precinct_2025_results["yes_pct"] - precinct_2025_results["dem_pct_2024"], 1
    )

    # Debug: county distribution of precincts with null yes_pct (validation opportunity)
    mo.vstack(
        [
            mo.md("## County distribution of precincts with null yes_pct"),
            precinct_results["blocks"]
            .loc[precinct_results["blocks"]["yes_pct"].isna(), "county"]
            .value_counts(),
        ]
    )
    return (precinct_results,)


@app.cell
def _(precinct_results):
    TOTAL_YES_VOTES = 7453339
    TOTAL_NO_VOTES = 4116998
    total_votes_from_sov = TOTAL_YES_VOTES + TOTAL_NO_VOTES

    print(
        f"Out of a total of {total_votes_from_sov:,} votes cast, there were {TOTAL_YES_VOTES:,} 'Yes' votes and {TOTAL_NO_VOTES:,} 'No' votes on Prop 50.\n"
    )

    analysis_total_votes = precinct_results["blocks"]["total_votes"].sum()
    analysis_total_votes_pct = analysis_total_votes / total_votes_from_sov

    print(
        f"Our analysis has processed data representing {analysis_total_votes_pct:.1%} of votes cast"
    )

    analysis_yes_votes = precinct_results["blocks"]["yes_votes"].sum()
    analysis_no_votes = precinct_results["blocks"]["no_votes"].sum()

    analysis_yes_proportion = analysis_yes_votes / TOTAL_YES_VOTES
    analysis_no_proportion = analysis_no_votes / TOTAL_NO_VOTES

    print(f"YES VOTES: {analysis_yes_proportion:.1%}")
    print(f"NO VOTES: {analysis_no_proportion:.1%}")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Analysis
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Majority group precincts

    - Groupby the results by the majority racial demographic group in each precinct

    For example, the first row in each output dataframe represent the aggregate result data for all of the Asian-majority precincts available in our analysis.
    """)
    return


@app.cell
def _(filter_threshold):
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


    def analyze_by_group_state(df, group_key, threshold=filter_threshold):
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


    def analyze_by_group_county(df, group_key, threshold=filter_threshold):
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


    def analyze_by_group(
        df, group_key, threshold=filter_threshold, by_county=False
    ):
        """Analyze vote stats for a demographic group. Returns dict (state) or DataFrame (county)."""
        if by_county:
            return analyze_by_group_county(df, group_key, threshold)
        return analyze_by_group_state(df, group_key, threshold)

    return (analyze_by_group,)


@app.cell
def _(ANALYSIS_GROUPS, GROUP_DISPLAY_LABELS, analyze_by_group):
    def build_majority_analysis_df(precinct_df, cfg):
        """Build majority-analysis table (group rows, yes/no columns) from any precinct-level DataFrame."""
        _df = pd.DataFrame(
            {
                g: analyze_by_group(precinct_df, g, by_county=False)
                for g in ANALYSIS_GROUPS
            }
        ).T
        _df.index = [GROUP_DISPLAY_LABELS[g] for g in ANALYSIS_GROUPS]
        _df = _df.rename(
            columns={
                "yes_split_pct": cfg["vote_display_labels"]["yes"],
                "no_split_pct": cfg["vote_display_labels"]["no"],
            }
        )
        return _df

    return (build_majority_analysis_df,)


@app.cell
def _(build_majority_analysis_df, dataset_config, precinct_results):
    majority_analysis = {
        _cfg["id"]: build_majority_analysis_df(precinct_results[_cfg["id"]], _cfg)
        for _cfg in dataset_config
    }
    return (majority_analysis,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Aggregate
    """)
    return


@app.cell
def _(dataset_config):
    def majority_analysis_display(analysis_dict):
        return mo.vstack(
            [
                mo.vstack(
                    [
                        mo.md(f"{_cfg['display_name']}"),
                        analysis_dict[_cfg["id"]],
                    ]
                )
                for _cfg in dataset_config
            ]
        )

    return (majority_analysis_display,)


@app.cell
def _(majority_analysis, majority_analysis_display):
    majority_analysis_display(majority_analysis)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### County
    """)
    return


@app.cell
def _(county_level_demo_analysis):
    counties = sorted(list(county_level_demo_analysis["blocks"].index))
    county_dropdown = mo.ui.dropdown(counties, value=counties[0], searchable=True)
    return counties, county_dropdown


@app.cell
def _(
    ANALYSIS_GROUPS,
    analyze_by_group,
    dataset_config,
    filter_threshold,
    precinct_results,
):
    county_level_demo_analysis = {}
    for _cfg in dataset_config:
        _df = pd.concat(
            [
                analyze_by_group(
                    precinct_results[_cfg["id"]],
                    group,
                    threshold=filter_threshold,
                    by_county=True,
                )
                for group in ANALYSIS_GROUPS
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
def _(
    DATASET_CONFIG,
    GROUP_DISPLAY_LABELS,
    county_dropdown,
    county_level_demo_analysis,
    filter_threshold,
):
    def _transform_county_series_to_dataframe(
        series, vote_display_labels, threshold=filter_threshold
    ):
        yes_pct_suffix = f"_{threshold}_yes_pct"
        yes_pct_cols = [
            col for col in series.index if col.endswith(yes_pct_suffix)
        ]

        data = []
        for pct_col in yes_pct_cols:
            group_key = pct_col.removesuffix(yes_pct_suffix)
            group_threshold_prefix = f"{group_key}_{threshold}"
            precinct_col = f"{group_threshold_prefix}_precinct_count"
            no_pct_col = f"{group_threshold_prefix}_no_pct"

            data.append(
                {
                    "precinct_count": series[precinct_col],
                    "total_votes": series[f"{group_key}_{threshold}_total_votes"],
                    vote_display_labels["yes"]: series[pct_col],
                    vote_display_labels["no"]: series[no_pct_col],
                }
            )

        display_labels = [
            GROUP_DISPLAY_LABELS[col.removesuffix(yes_pct_suffix)]
            for col in yes_pct_cols
        ]
        df = pd.DataFrame(data, index=display_labels)
        df["total_votes_pct"] = caclulate_pct(
            df["total_votes"], df["total_votes"].sum()
        )
        return df


    _county = county_dropdown.value
    mo.vstack(
        [
            county_dropdown,
            *[
                mo.vstack(
                    [
                        mo.md(f"**{_cfg['display_name']}**"),
                        _transform_county_series_to_dataframe(
                            county_level_demo_analysis[_cfg["id"]].loc[_county],
                            _cfg["vote_display_labels"],
                            threshold=filter_threshold,
                        ),
                    ]
                )
                for _cfg in DATASET_CONFIG
                if _county in county_level_demo_analysis[_cfg["id"]].index
            ],
        ]
    )
    return


@app.cell
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    compute_vote_shift,
    county_dropdown,
    county_level_demo_analysis,
    filter_threshold,
):
    def _build_county_memo_table(county):
        """One table per county: Racial group, Swing, YES %, HARRIS %, NO %, TRUMP %."""
        prop50_df = county_level_demo_analysis.get(PROP50_DATASET_ID)
        pres2024_df = county_level_demo_analysis.get(PRES2024_DATASET_ID)
        if (
            prop50_df is None
            or pres2024_df is None
            or county not in prop50_df.index
            or county not in pres2024_df.index
        ):
            return None
        prop50_row = prop50_df.loc[county]
        pres2024_row = pres2024_df.loc[county]
        yes_suffix = f"_{filter_threshold}_yes_pct"
        no_suffix = f"_{filter_threshold}_no_pct"

        def _memo_row(group_id):
            yes_key = f"{group_id}{yes_suffix}"
            no_key = f"{group_id}{no_suffix}"
            if (
                yes_key not in prop50_row.index
                or yes_key not in pres2024_row.index
            ):
                return None
            swing = compute_vote_shift(prop50_row, pres2024_row, group_id)
            return {
                "Racial group": GROUP_DISPLAY_LABELS[group_id],
                "Swing from Harris to Prop 50": (
                    swing if swing is not None else ""
                ),
                "YES on Prop. 50 - pct": prop50_row[yes_key],
                "HARRIS - pct": pres2024_row[yes_key],
                "NO on Prop. 50 - pct": prop50_row[no_key],
                "TRUMP - pct": pres2024_row[no_key],
            }

        rows = [
            row
            for group_id in ANALYSIS_GROUPS
            if (row := _memo_row(group_id)) is not None
        ]
        return pd.DataFrame(rows) if rows else None


    _county = county_dropdown.value
    _memo_table = _build_county_memo_table(_county)
    mo.vstack(
        [
            mo.md(
                f"**{_county} County memo** — Prop 50 vs 2024 Presidential (Harris/Trump) by racial group"
            ),
            _memo_table
            if _memo_table is not None
            else mo.md(
                "_Select both «Prop 50 (Blocks)» and «2024 Presidential (Blocks)» above to show this table._"
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Vote shift
    """)
    return


@app.cell
def _(filter_threshold):
    PROP50_DATASET_ID = "blocks"
    PRES2024_DATASET_ID = "blocks_2024"
    YES_PCT_SUFFIX = f"_{filter_threshold}_yes_pct"


    def compute_vote_shift(prop50_series, pres2024_series, group_id):
        """Vote shift (Yes % − Democrat %) for one group; returns None if key missing."""
        key = f"{group_id}{YES_PCT_SUFFIX}"
        if key not in prop50_series.index or key not in pres2024_series.index:
            return None
        return round(float(prop50_series[key] - pres2024_series[key]), 1)

    return PRES2024_DATASET_ID, PROP50_DATASET_ID, compute_vote_shift


@app.cell
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    compute_vote_shift,
    county_level_demo_analysis,
):
    prop50_by_county = county_level_demo_analysis[PROP50_DATASET_ID]
    pres2024_by_county = county_level_demo_analysis[PRES2024_DATASET_ID]


    def vote_shift_row_for_county(county):
        row = {"county": county}
        for group_id in ANALYSIS_GROUPS:
            value = compute_vote_shift(
                prop50_by_county.loc[county],
                pres2024_by_county.loc[county],
                group_id,
            )
            if value is not None:
                row[GROUP_DISPLAY_LABELS[group_id]] = value
        return row


    vote_shift_by_county = pd.DataFrame(
        [vote_shift_row_for_county(county) for county in prop50_by_county.index]
    )
    column_order = ["county"] + [GROUP_DISPLAY_LABELS[g] for g in ANALYSIS_GROUPS]
    vote_shift_by_county = vote_shift_by_county[
        [c for c in column_order if c in vote_shift_by_county.columns]
    ]

    mo.vstack(
        [
            mo.md("**Vote shift (Yes % − Democrat %) by county (statewide)**"),
            vote_shift_by_county,
        ]
    )
    return


@app.cell
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    compute_vote_shift,
    county_dropdown,
    county_level_demo_analysis,
):
    _selected_county = county_dropdown.value
    prop50_row = county_level_demo_analysis[PROP50_DATASET_ID].loc[
        _selected_county
    ]
    pres2024_row = county_level_demo_analysis[PRES2024_DATASET_ID].loc[
        _selected_county
    ]

    vote_shift_rows = []
    for group_id in ANALYSIS_GROUPS:
        value = compute_vote_shift(prop50_row, pres2024_row, group_id)
        if value is not None:
            vote_shift_rows.append(
                {
                    "group": GROUP_DISPLAY_LABELS[group_id],
                    "vote_shift": value,
                }
            )
    vote_shift_table = pd.DataFrame(vote_shift_rows)

    mo.vstack(
        [
            county_dropdown,
            mo.md(f"**Vote shift (Yes % − Democrat %) for {_selected_county}**"),
            vote_shift_table,
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### County multiselect
    """)
    return


@app.cell
def _(counties):
    county_multiselect = mo.ui.multiselect(counties, full_width=True)
    county_multiselect
    return (county_multiselect,)


@app.cell
def _(
    build_majority_analysis_df,
    county_multiselect,
    dataset_config,
    majority_analysis_display,
    precinct_results,
):
    def _county_subset_majority_display(selected_counties):
        if not selected_counties:
            return mo.md(
                "Select one or more counties to see aggregated majority analysis."
            )
        _subset = {
            _cfg["id"]: build_majority_analysis_df(
                precinct_results[_cfg["id"]].loc[
                    precinct_results[_cfg["id"]]["county"].isin(selected_counties)
                ],
                _cfg,
            )
            for _cfg in dataset_config
        }
        return mo.vstack(
            [
                mo.md(f"**Selected counties:** {', '.join(selected_counties)}"),
                majority_analysis_display(_subset),
            ]
        )


    _county_subset_majority_display(county_multiselect.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Demographic scatterplot and linear regression

    Linear regression is plotted for exploratory purposes. We would need to [validate the assumptions required](https://online.stat.psu.edu/stat200/lesson/12/12.3/12.3.2) to use linear regression in our final analysis. The results by majority group is currently the preferred analysis tool.
    """)
    return


@app.function
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


@app.cell
def _(ANALYSIS_GROUPS):
    demo_group_dropdown = mo.ui.dropdown(
        options=[g for g in ANALYSIS_GROUPS if g != "multiracial"],
        value="white",
    )
    return (demo_group_dropdown,)


@app.cell
def _(DATASET_CONFIG, demo_group_dropdown, precinct_results):
    _group = demo_group_dropdown.value
    _cvap_col = f"{_group}_pct"
    _group_label = _group.replace("_", " ").title()
    mo.vstack(
        [
            demo_group_dropdown,
            *[
                mo.vstack(
                    [
                        mo.md(f"**{_cfg['display_name']}**"),
                        plot_lnr_yes_pct_vs_cvap(
                            precinct_results[_cfg["id"]],
                            _cvap_col,
                            "yes_pct",
                            _group_label,
                            f"({_cfg['display_name']})",
                            y_label=f"{_cfg['vote_display_labels']['yes'].removesuffix(' %')} Vote Percentage",
                        ),
                    ]
                )
                for _cfg in DATASET_CONFIG
            ],
        ]
    )
    return


@app.cell(hide_code=True)
def _():
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
    mo.vstack(
        [
            demo_group_dropdown,
            *[
                mo.vstack(
                    [
                        mo.md(f"**{_cfg['display_name']}**"),
                        precinct_results[_cfg["id"]][[_cvap_col, "yes_pct"]]
                        .dropna()
                        .corr(method="pearson"),
                    ]
                )
                for _cfg in DATASET_CONFIG
            ],
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Hypothesis testing

    For both of the following hypothesis, we are looking at how specific demographic groups voted. I first output how precincts where the majority of voting-age citizens belong to that racial demographic group, then I output a scatter plot with a linear regression plotted.

    The linear regression is an exploration tool, not a thorough analysis of the relation between racial demographics and support for Prop 50.
    """)
    return


@app.cell(hide_code=True)
def _():
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
def _():
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
def _():
    mo.md(r"""
    # Appendix
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Export GIS file
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Export source data for analysis
    """)
    return


@app.cell
def _(dataset_config, precinct_results):
    EXPORT_DATA_CONFIG_KEYS = [
        "blocks",
        "blocks_2024",
    ]
    EXPORT_DRIVER = "GPKG"

    for _cfg in dataset_config:
        if _cfg["id"] in EXPORT_DATA_CONFIG_KEYS:
            _path = pathlib.Path(
                f"./outputs/precinct_results_plus_demographics_{_cfg['id']}.gpkg"
            )
            if _path.exists():
                _path.unlink()
            precinct_results[_cfg["id"]].to_file(str(_path), driver=EXPORT_DRIVER)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Export map data

    This is an intermediate file used to generate the pmtiles file for the visual.
    """)
    return


@app.cell
def _(precinct_results):
    MAP_EXPORT_CONFIG_KEY = "blocks"
    MAP_EXPORT_DRIVER = "GeoJSON"
    MAP_EXPORT_COLUMNS = [
        "county",
        "precinct_id",
        "yes_votes",
        "no_votes",
        "total_votes",
        "yes_pct",
        "no_pct",
        "dem_votes",
        "rep_votes",
        "total_votes_2024",
        "vote_shift",
        "majority_racial_group",
        "majority_racial_group_pct",
        "geometry",
    ]
    MAP_PATH = f"./outputs/precinct_results_plus_demographics_blocks.geojson"

    _path = pathlib.Path(MAP_PATH)
    _cols = [
        c
        for c in MAP_EXPORT_COLUMNS
        if c in precinct_results[MAP_EXPORT_CONFIG_KEY].columns
    ]

    if _path.exists():
        _path.unlink()
    precinct_results[MAP_EXPORT_CONFIG_KEY].to_file(
        str(_path), driver=MAP_EXPORT_DRIVER
    )
    return (MAP_EXPORT_CONFIG_KEY,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Export partner data

    This file is used to produce a [Google Sheet](https://docs.google.com/spreadsheets/d/1W5_vdO3vjfrGStJVJ0M2XNHmK1-rfDVTet2GnRt-4cw/edit?gid=0#gid=0) sharing the analysis data with partners.
    """)
    return


@app.cell
def _(MAP_EXPORT_CONFIG_KEY, precinct_results):
    _PARTNER_EXPORT_PATH = "./outputs/partner_export.csv"
    _PCT_COLUMNS = [
        "yes_pct",
        "no_pct",
        "dem_pct_24",
        "rep_pct_24",
        "vote_shift",
        "turnout",
        "largest_racial_group_pct",
    ]

    _COLUMN_RENAMES = {
        "total_votes": "total_votes_25",
        "dem_votes": "dem_votes_24",
        "rep_votes": "rep_votes_24",
        "total_votes_2024": "total_votes_24",
        "majority_racial_group_pct": "largest_racial_group_pct",
        "dem_pct_2024": "dem_pct_24",
        "rep_pct_2024": "rep_pct_24",
    }

    _EXPORT_COLUMNS = [
        "county",
        "precinct_id",
        "total_votes_25",
        "yes_votes",
        "no_votes",
        "yes_pct",
        "no_pct",
        "registered_voters",
        "turnout",
        "total_votes_24",
        "dem_votes_24",
        "rep_votes_24",
        "dem_pct_24",
        "rep_pct_24",
        "vote_shift",
        "majority_racial_group",
        "plurality_racial_group",
        "largest_racial_group_pct",
    ]

    precinct_results_export = (
        precinct_results[MAP_EXPORT_CONFIG_KEY]
        .rename(columns=_COLUMN_RENAMES)
        .copy()
    )

    # Split the combined majority_racial_group string into separate majority and plurality columns
    precinct_results_export[
        ["majority_racial_group", "plurality_racial_group"]
    ] = (
        precinct_results_export["majority_racial_group"]
        .str.strip(")")
        .str.split("(", expand=True)
    )

    # Clean up whitespace and remove the "plurality" suffix from the plurality column
    precinct_results_export["majority_racial_group"] = precinct_results_export[
        "majority_racial_group"
    ].str.strip()
    precinct_results_export["plurality_racial_group"] = (
        precinct_results_export["plurality_racial_group"]
        .str.removesuffix("plurality")
        .str.strip()
    )

    # divide by 100 for Google Sheet formatting
    precinct_results_export[_PCT_COLUMNS] = (
        precinct_results_export[_PCT_COLUMNS] / 100
    )

    precinct_results_export = precinct_results_export[_EXPORT_COLUMNS]

    precinct_results_export.to_csv(_PARTNER_EXPORT_PATH, index=False)
    del precinct_results_export
    return


@app.cell
def _(MAP_EXPORT_CONFIG_KEY, precinct_results):
    _precincts_df = precinct_results[MAP_EXPORT_CONFIG_KEY][
        ["county", "precinct_id"]
    ]
    county_precinct_dict = (
        _precincts_df.groupby("county")["precinct_id"].apply(list).to_dict()
    )

    _output_path = pathlib.Path("./outputs/county_precincts.json")
    with _output_path.open("w") as f:
        json.dump(county_precinct_dict, f)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
