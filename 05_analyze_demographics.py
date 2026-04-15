import marimo

__generated_with = "0.23.0"
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
    # Demographics and precinct-level vote patterns (Prop 50 and 2024 presidential)

    This notebook explores how [Census CVAP](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) race and ethnicity shares line up with precinct results. It reads merged GeoPackages produced upstream (notably `04_interpolation.py`): **Prop 50** and **2024 presidential** vote totals joined to block- or tract-level CVAP estimates (`outputs/precincts_results_cvap_blocks.gpkg`, `outputs/precincts_results_cvap_tracts.gpkg`, and `outputs/precincts_2024_results_cvap_blocks.gpkg`).

    You can compare **block- vs tract-based** demographics, tune a **threshold** for calling a precinct “majority” one racial/ethnic group (otherwise labeled multiracial plurality), and review **statewide**, **county**, and **multi-county** aggregates. The notebook measures **vote shift** in two ways (toggle below): **one-party** (Prop 50 Yes % minus 2024 Democratic presidential %) and **net** (Prop 50 Yes−No margin minus 2024 Dem−Rep margin). It also flags **partisan flip** patterns where 2024 and Prop 50 majorities disagree—treated as exploratory given interpolation from 2024 votes onto 2025 precinct geography.
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
    # Same percent scale as the majority-threshold slider (0–100).
    ROBUSTNESS_MAJORITY_THRESHOLDS = (50, 60, 70, 75, 80, 85, 90)
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
    return ROBUSTNESS_MAJORITY_THRESHOLDS, threshold_slider


@app.cell
def _():
    SHIFT_MODE_ONE_PARTY = "one_party"
    SHIFT_MODE_NET = "net"
    # Radio labels (mo.ui.radio: dict keys are shown; values become .value).
    SHIFT_MODE_OPTION_LABEL_ONE_PARTY = "One-party shift (Yes % - Dem %)"
    SHIFT_MODE_OPTION_LABEL_NET = "Net shift ((Yes − No) − (Dem − Rep))"
    SHIFT_MODE_LABELS = {
        SHIFT_MODE_OPTION_LABEL_ONE_PARTY: SHIFT_MODE_ONE_PARTY,
        SHIFT_MODE_OPTION_LABEL_NET: SHIFT_MODE_NET,
    }
    SHIFT_MODE_TABLE_CAPTION = {
        SHIFT_MODE_ONE_PARTY: SHIFT_MODE_OPTION_LABEL_ONE_PARTY,
        SHIFT_MODE_NET: SHIFT_MODE_OPTION_LABEL_NET,
    }
    SHIFT_MODE_ROBUSTNESS_MD = {
        SHIFT_MODE_ONE_PARTY: "One-party shift",
        SHIFT_MODE_NET: "Net shift",
    }


    def arrow_axis_column_names(mode):
        """Arrow plot x-axis columns in memo-style tables (one-party vs net layout)."""
        if mode == SHIFT_MODE_NET:
            return (
                "Pres margin (Dem − Rep) (pts)",
                "Prop 50 margin (Yes − No) (pts)",
            )
        return ("HARRIS - pct", "YES on Prop. 50 - pct")


    shift_mode = mo.ui.radio(
        options=SHIFT_MODE_LABELS,
        value=SHIFT_MODE_OPTION_LABEL_ONE_PARTY,
        label="### Vote shift definition",
    )
    shift_mode
    return (
        SHIFT_MODE_NET,
        SHIFT_MODE_ROBUSTNESS_MD,
        SHIFT_MODE_TABLE_CAPTION,
        arrow_axis_column_names,
        shift_mode,
    )


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
def calculate_pct(numerator, denominator, precision=1):
    return round((numerator / denominator) * 100, precision)


@app.function
def vote_shift_one_party(prop50_yes_pct, pres_dem_pct):
    """Prop 50 Yes % minus 2024 Democratic presidential % (one-party shift)."""
    if any(pd.isna(pct) for pct in (prop50_yes_pct, pres_dem_pct)):
        return None
    return round(float(prop50_yes_pct) - float(pres_dem_pct), 1)


@app.function
def vote_shift_net(prop50_yes_pct, prop50_no_pct, pres_dem_pct, pres_rep_pct):
    """(Prop 50 Yes − No) minus (2024 Dem − Rep) margin difference."""
    if any(
        pd.isna(pct)
        for pct in (
            prop50_yes_pct,
            prop50_no_pct,
            pres_dem_pct,
            pres_rep_pct,
        )
    ):
        return None
    margin_prop50 = float(prop50_yes_pct) - float(prop50_no_pct)
    margin_pres = float(pres_dem_pct) - float(pres_rep_pct)
    return round(margin_prop50 - margin_pres, 1)


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
    df.loc[valid_total_mask, "yes_pct"] = calculate_pct(
        df.loc[valid_total_mask, "yes_votes"], total_votes[valid_total_mask]
    )
    df["no_pct"] = np.nan
    df.loc[valid_total_mask, "no_pct"] = calculate_pct(
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
def _(filter_threshold, get_majority_racial_group):
    def prepare_precinct_results_df(df, vote_count_columns):
        """Replace redacted values with NaN and convert vote columns to numeric."""
        df = df.replace("-1", np.nan).replace(-1, np.nan)
        df[vote_count_columns] = df[vote_count_columns].apply(pd.to_numeric)
        return df


    def assign_majority_racial_group(df, threshold):
        """Recompute majority_racial_group and majority_racial_group_pct at threshold (percent scale)."""
        df = df.copy()
        df[["majority_racial_group", "majority_racial_group_pct"]] = df.apply(
            lambda row: pd.Series(
                get_majority_racial_group(row, threshold=threshold)
            ),
            axis=1,
        )
        return df


    def add_majority_racial_group(df):
        """Add majority columns using the interactive slider threshold."""
        return assign_majority_racial_group(df, filter_threshold)

    return (
        add_majority_racial_group,
        assign_majority_racial_group,
        prepare_precinct_results_df,
    )


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
def _(DATASET_CONFIG, read_gis_data):
    # Read all GIS datasets once; this cell does not depend on the multiselect
    # or threshold slider, so it only re-runs when config or read_gis_data changes.
    raw_gis_data_by_id = {
        _cfg["id"]: read_gis_data(_cfg["filepath"], _cfg["id"])
        for _cfg in DATASET_CONFIG
    }
    return (raw_gis_data_by_id,)


@app.cell
def _(
    VOTE_STANDARD,
    add_majority_racial_group,
    dataset_config,
    prepare_precinct_results_df,
    raw_gis_data_by_id,
    standardize_demographic_columns,
    standardize_vote_columns,
):
    precinct_results = {}
    for _cfg in dataset_config:
        df = raw_gis_data_by_id[_cfg["id"]].copy()
        df = standardize_vote_columns(df, _cfg["vote_source_to_standard"])
        df = standardize_demographic_columns(df, _cfg["demographic_schema"])
        df = prepare_precinct_results_df(df, list(VOTE_STANDARD))
        df = calculate_yes_pct(df)
        df = add_majority_racial_group(df)
        precinct_results[_cfg["id"]] = df

    # Validate null yes_pct count on tracts dataset
    _df_validate = precinct_results["blocks"]
    null_votes = (
        _df_validate["yes_votes"].isnull() & _df_validate["no_votes"].isnull()
    )
    _total_votes = _df_validate["yes_votes"] + _df_validate["no_votes"]
    has_zero_total_votes = _total_votes == 0
    expected_null_yes_pct_count = (null_votes | has_zero_total_votes).sum()
    observed_null_yes_pct_count = _df_validate["yes_pct"].isna().sum()
    assert expected_null_yes_pct_count - 1 == observed_null_yes_pct_count, (
        f"Expected {expected_null_yes_pct_count} null values in 'yes_pct', "
        f"but found {observed_null_yes_pct_count}."
    )

    # Calculate vote shift from Harris to YES on Prop. 50
    precinct_2025_results = precinct_results["blocks"]
    precinct_2025_results["dem_pct_2024"] = calculate_pct(
        precinct_2025_results["dem_votes"],
        precinct_2025_results["total_votes_2024"],
    )
    precinct_2025_results["rep_pct_2024"] = calculate_pct(
        precinct_2025_results["rep_votes"],
        precinct_2025_results["total_votes_2024"],
    )
    # Same formulas as vote_shift_one_party / vote_shift_net (vectorized; NaNs propagate).
    precinct_2025_results["vote_shift"] = (
        precinct_2025_results["yes_pct"] - precinct_2025_results["dem_pct_2024"]
    ).round(1)
    precinct_2025_results["vote_shift_net"] = (
        (precinct_2025_results["yes_pct"] - precinct_2025_results["no_pct"])
        - (
            precinct_2025_results["dem_pct_2024"]
            - precinct_2025_results["rep_pct_2024"]
        )
    ).round(1)

    # Identify partisan flip
    is_trump_win = (
        precinct_2025_results["rep_pct_2024"]
        > precinct_2025_results["dem_pct_2024"]
    )
    is_harris_win = (
        precinct_2025_results["rep_pct_2024"]
        < precinct_2025_results["dem_pct_2024"]
    )

    is_prop50_win = (
        precinct_2025_results["yes_pct"] > precinct_2025_results["no_pct"]
    )
    is_prop50_loss = (
        precinct_2025_results["yes_pct"] < precinct_2025_results["no_pct"]
    )

    precinct_2025_results.loc[is_trump_win & is_prop50_win, "flipped"] = "D"
    precinct_2025_results.loc[is_harris_win & is_prop50_loss, "flipped"] = "R"

    # Debug: county distribution of precincts with null yes_pct (validation opportunity)
    mo.vstack(
        [
            mo.md("## County distribution of precincts with null yes_pct"),
            precinct_results["blocks"]
            .loc[precinct_results["blocks"]["yes_pct"].isna(), "county"]
            .value_counts(),
        ]
    )
    return (
        is_harris_win,
        is_prop50_loss,
        is_prop50_win,
        is_trump_win,
        precinct_2025_results,
        precinct_results,
    )


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

    county_count = precinct_results["blocks"]["county"].nunique()
    print(
        f"Our analysis has processed data in {county_count} counties representing {analysis_total_votes_pct:.1%} of votes cast"
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
    # Majority group precincts

    - Groupby the results by the majority racial demographic group in each precinct

    For example, the first row in each output dataframe represent the aggregate result data for all of the Asian-majority precincts available in our analysis.
    """)
    return


@app.cell
def _(filter_threshold):
    def _calculate_vote_stats(yes_votes, no_votes, total_votes=None):
        if total_votes is None:
            total_votes = yes_votes + no_votes
        yes_pct = calculate_pct(yes_votes, total_votes)
        no_pct = calculate_pct(no_votes, total_votes)
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
    # Running Statewide majority-group

    We only have a subset of counties but it includes the vast majority of votes cast.
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
    ## Vote shift
    """)
    return


@app.cell
def _(SHIFT_MODE_NET, filter_threshold):
    PROP50_DATASET_ID = "blocks"
    PRES2024_DATASET_ID = "blocks_2024"
    YES_PCT_SUFFIX = f"_{filter_threshold}_yes_pct"
    NO_PCT_SUFFIX = f"_{filter_threshold}_no_pct"


    def compute_vote_shift(prop50_series, pres2024_series, group_id, mode):
        """One-party or net shift for one racial group; None if required keys or pcts missing."""
        yes_key = f"{group_id}{YES_PCT_SUFFIX}"
        no_key = f"{group_id}{NO_PCT_SUFFIX}"
        if (
            yes_key not in prop50_series.index
            or yes_key not in pres2024_series.index
        ):
            return None
        if mode == SHIFT_MODE_NET:
            if (
                no_key not in prop50_series.index
                or no_key not in pres2024_series.index
            ):
                return None
            return vote_shift_net(
                prop50_series[yes_key],
                prop50_series[no_key],
                pres2024_series[yes_key],
                pres2024_series[no_key],
            )
        return vote_shift_one_party(
            prop50_series[yes_key],
            pres2024_series[yes_key],
        )

    return PRES2024_DATASET_ID, PROP50_DATASET_ID, compute_vote_shift


@app.cell
def _(SHIFT_MODE_NET, analyze_by_group):
    def robustness_shift_and_precinct_count(
        prop50_precincts,
        pres2024_precincts,
        group_id,
        majority_threshold_percent,
        shift_mode_value,
    ):
        """
        State-level vote shift and Prop 50 precinct count for one analysis group,
        using already-relabeled precinct frames.
        """
        prop50_state = analyze_by_group(
            prop50_precincts,
            group_id,
            threshold=majority_threshold_percent,
            by_county=False,
        )
        pres2024_state = analyze_by_group(
            pres2024_precincts,
            group_id,
            threshold=majority_threshold_percent,
            by_county=False,
        )
        if shift_mode_value == SHIFT_MODE_NET:
            shift = vote_shift_net(
                prop50_state["yes_split_pct"],
                prop50_state["no_split_pct"],
                pres2024_state["yes_split_pct"],
                pres2024_state["no_split_pct"],
            )
        else:
            shift = vote_shift_one_party(
                prop50_state["yes_split_pct"],
                pres2024_state["yes_split_pct"],
            )
        precinct_count = int(prop50_state["num_precincts"])
        return shift, precinct_count

    return (robustness_shift_and_precinct_count,)


@app.cell
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    ROBUSTNESS_MAJORITY_THRESHOLDS,
    assign_majority_racial_group,
    precinct_results,
    robustness_shift_and_precinct_count,
    shift_mode,
):
    def build_robustness_vote_shift_and_precinct_tables(
        precinct_results_map,
        prop50_dataset_id,
        pres2024_dataset_id,
        majority_threshold_percents,
        shift_mode_value,
    ):
        """
        Build two aligned tables (groups × thresholds): vote shift and precinct counts.

        For each threshold, precincts are relabeled once per dataset; then each group
        gets one shift and one count (count from the Prop 50 frame).
        """

        def empty_group_rows():
            return [
                {"group": GROUP_DISPLAY_LABELS[group_id]}
                for group_id in ANALYSIS_GROUPS
            ]

        vote_shift_rows = empty_group_rows()
        precinct_count_rows = empty_group_rows()

        for majority_threshold_percent in majority_threshold_percents:
            column_header = f"{majority_threshold_percent}%"
            prop50_precincts = assign_majority_racial_group(
                precinct_results_map[prop50_dataset_id],
                majority_threshold_percent,
            )
            pres2024_precincts = assign_majority_racial_group(
                precinct_results_map[pres2024_dataset_id],
                majority_threshold_percent,
            )
            for group_id, vote_row, count_row in zip(
                ANALYSIS_GROUPS,
                vote_shift_rows,
                precinct_count_rows,
                strict=True,
            ):
                shift, precinct_count = robustness_shift_and_precinct_count(
                    prop50_precincts,
                    pres2024_precincts,
                    group_id,
                    majority_threshold_percent,
                    shift_mode_value,
                )
                vote_row[column_header] = shift
                count_row[column_header] = precinct_count

        return (
            pd.DataFrame(vote_shift_rows),
            pd.DataFrame(precinct_count_rows),
        )


    vote_shift_robustness_table, precinct_count_robustness_table = (
        build_robustness_vote_shift_and_precinct_tables(
            precinct_results,
            PROP50_DATASET_ID,
            PRES2024_DATASET_ID,
            ROBUSTNESS_MAJORITY_THRESHOLDS,
            shift_mode.value,
        )
    )
    return precinct_count_robustness_table, vote_shift_robustness_table


@app.cell(hide_code=True)
def _(
    SHIFT_MODE_ROBUSTNESS_MD,
    precinct_count_robustness_table,
    shift_mode,
    vote_shift_robustness_table,
):
    _robustness_shift_phrase = SHIFT_MODE_ROBUSTNESS_MD[shift_mode.value]
    vote_shift_robustness_ui = mo.vstack(
        [
            mo.md(
                f"""
    **Robustness: vote shift by categorization threshold**

    Each column uses a fixed categorization rule (same scale as the threshold slider). The
    slider still controls categorization everywhere else in this notebook; this table
    only sweeps that rule to show how {_robustness_shift_phrase} moves with
    higher or lower categorization threshold.
    """
            ),
            vote_shift_robustness_table,
            mo.md(
                r"""
    **Precinct counts (same grouping)**

    How many precincts fall in each racial analysis group under each cutoff, after the same
    relabeling as above. Counts follow the Prop 50 precinct table (numerator of the shift).
    """
            ),
            precinct_count_robustness_table,
        ]
    )
    vote_shift_robustness_ui
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # County-level breakdowns
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Population data
    """)
    return


@app.cell
def _(precinct_results):
    POP_TOTAL_COLUMNS = [
        "CVAP_TOT24",
        "CVAP_HSP24",
        "CVAP_WHT24",
        "CVAP_BLK24",
        "CVAP_2OM24",
        "_cvap_api24",
        "_cvap_amw24",
    ]
    precinct_results["blocks"].groupby("county")[POP_TOTAL_COLUMNS].sum()
    return


@app.cell
def _(precinct_results):
    def get_group_precinct_counts_by_county(df_precincts):
        df = df_precincts.copy()
        df["majority_racial_group"] = (
            df["majority_racial_group"].str.split("(").str[0]
        )
        return df.pivot_table(
            index="county",
            columns="majority_racial_group",
            aggfunc="size",
            fill_value=0,
        )


    get_group_precinct_counts_by_county(precinct_results["blocks"])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Results
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
        df["total_votes_pct"] = calculate_pct(
            df["total_votes"], df["total_votes"].sum()
        )
        return df


    mo.vstack(
        [
            county_dropdown,
            *[
                mo.vstack(
                    [
                        mo.md(f"**{_cfg['display_name']}**"),
                        _transform_county_series_to_dataframe(
                            county_level_demo_analysis[_cfg["id"]].loc[
                                county_dropdown.value
                            ],
                            _cfg["vote_display_labels"],
                            threshold=filter_threshold,
                        ),
                    ]
                )
                for _cfg in DATASET_CONFIG
                if county_dropdown.value
                in county_level_demo_analysis[_cfg["id"]].index
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
    SHIFT_MODE_NET,
    arrow_axis_column_names,
    compute_vote_shift,
    county_dropdown,
    county_level_demo_analysis,
    filter_threshold,
    shift_mode,
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
        _memo_shift_mode = shift_mode.value

        def _memo_row(group_id):
            yes_key = f"{group_id}{yes_suffix}"
            no_key = f"{group_id}{no_suffix}"

            swing = compute_vote_shift(
                prop50_row, pres2024_row, group_id, _memo_shift_mode
            )
            row = {
                "Racial group": GROUP_DISPLAY_LABELS[group_id],
                "Swing from Harris to Prop 50": (
                    swing if swing is not None else ""
                ),
                "YES on Prop. 50 - pct": prop50_row[yes_key],
                "HARRIS - pct": pres2024_row[yes_key],
                "NO on Prop. 50 - pct": prop50_row[no_key],
                "TRUMP - pct": pres2024_row[no_key],
            }
            if _memo_shift_mode == SHIFT_MODE_NET:
                pres_margin_col, prop_margin_col = arrow_axis_column_names(
                    _memo_shift_mode
                )
                row[pres_margin_col] = float(pres2024_row[yes_key]) - float(
                    pres2024_row[no_key]
                )
                row[prop_margin_col] = float(prop50_row[yes_key]) - float(
                    prop50_row[no_key]
                )
            return row

        rows = [
            row
            for group_id in ANALYSIS_GROUPS
            if (row := _memo_row(group_id)) is not None
        ]
        return pd.DataFrame(rows) if rows else None


    memo_table = _build_county_memo_table(county_dropdown.value)
    mo.vstack(
        [
            mo.md(
                f"**{county_dropdown.value} County memo** — Prop 50 vs 2024 Presidential (Harris/Trump) by racial group"
            ),
            memo_table
            if memo_table is not None
            else mo.md(
                "_Select both «Prop 50 (Blocks)» and «2024 Presidential (Blocks)» above to show this table._"
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Vote shift
    """)
    return


@app.cell
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    SHIFT_MODE_TABLE_CAPTION,
    compute_vote_shift,
    county_level_demo_analysis,
    shift_mode,
):
    prop50_by_county = county_level_demo_analysis[PROP50_DATASET_ID]
    pres2024_by_county = county_level_demo_analysis[PRES2024_DATASET_ID]
    _table_shift_mode = shift_mode.value


    def vote_shift_row_for_county(county):
        row = {"county": county}
        for group_id in ANALYSIS_GROUPS:
            value = compute_vote_shift(
                prop50_by_county.loc[county],
                pres2024_by_county.loc[county],
                group_id,
                _table_shift_mode,
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
            mo.md(
                f"**Vote shift ({SHIFT_MODE_TABLE_CAPTION[_table_shift_mode]}) by county (statewide)**"
            ),
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
    SHIFT_MODE_TABLE_CAPTION,
    compute_vote_shift,
    county_dropdown,
    county_level_demo_analysis,
    shift_mode,
):
    _selected_county = county_dropdown.value
    _county_table_shift_mode = shift_mode.value
    prop50_row = county_level_demo_analysis[PROP50_DATASET_ID].loc[
        _selected_county
    ]
    pres2024_row = county_level_demo_analysis[PRES2024_DATASET_ID].loc[
        _selected_county
    ]

    vote_shift_rows = []
    for group_id in ANALYSIS_GROUPS:
        value = compute_vote_shift(
            prop50_row, pres2024_row, group_id, _county_table_shift_mode
        )
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
            mo.md(
                f"**Vote shift ({SHIFT_MODE_TABLE_CAPTION[_county_table_shift_mode]}) for {_selected_county}**"
            ),
            vote_shift_table,
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## County multiselect
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
def _(
    is_harris_win,
    is_prop50_loss,
    is_prop50_win,
    is_trump_win,
    precinct_2025_results,
):
    mo.md(rf"""
    ## Partisan flip

    **There are {(is_trump_win & is_prop50_win).sum():,} precincts in the {precinct_2025_results["county"].nunique()} counties where Prop. 50 won and Trump won.** There were {(is_harris_win & is_prop50_loss).sum():,} precincts where Harris won but Prop. 50 lost.

    These findings should be used only for exploratory purposes. The 2024 results are interpolated to 2025 precincts. This introduces issues such as the faulty assumption of uniform population distribution and the modifiable areal unit problem. These limitations require extra scrutiny of any findings we want to publish about partisan flips at the precinct-level.
    """)
    return


@app.cell
def _(precinct_2025_results):
    flipped_precincts = precinct_2025_results[
        precinct_2025_results["flipped"].notnull()
    ]
    flipped_precincts
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Arrow plot
    """)
    return


@app.cell(hide_code=True)
def _():
    FIG_SIZE = (8.5, 2.8)
    ARROW_COLOR = "#0077a3"
    # CalMatters "red_500" token for decreasing states.
    DECREASE_COLOR = "#D35F4F"
    ARROW_WIDTH_DEFAULT = 3
    FONT_SIZE = 9
    TITLE_PADDING = 12
    SWING_LABEL_DX = 0.6
    SWING_LABEL_DY = 0.03
    X_AXIS_ROUNDING_STEP = 5
    XTICK_STEP = 10
    X_GRID_ALPHA = 0.35
    Y_GRID_ALPHA = 0.15
    HEADER_Y_OFFSET = 0.75
    Y_MIN_PADDING = -0.6
    Y_MAX_PADDING = 1.1
    HEADER_TICK_COLOR = "gray"
    HEADER_TICK_ALPHA = 0.6
    HEADER_TICK_LW = 1.0
    HEADER_TICK_DY_TOP = 0.08
    HEADER_TICK_DY_BOTTOM = 0.35

    HARRIS_TICK_LABEL = "Harris"
    PROP_50_TICK_LABEL = "Prop. 50"

    arrow_plot_mode_dropdown = mo.ui.dropdown(
        options=["County", "Statewide"],
        value="County",
        label="Arrow plot view:",
    )
    arrow_width_slider = mo.ui.slider(
        0, 10, 0.5, ARROW_WIDTH_DEFAULT, show_value=True, label="Arrow width:"
    )
    return (
        ARROW_COLOR,
        DECREASE_COLOR,
        FIG_SIZE,
        FONT_SIZE,
        HARRIS_TICK_LABEL,
        HEADER_TICK_ALPHA,
        HEADER_TICK_COLOR,
        HEADER_TICK_DY_BOTTOM,
        HEADER_TICK_DY_TOP,
        HEADER_TICK_LW,
        HEADER_Y_OFFSET,
        PROP_50_TICK_LABEL,
        SWING_LABEL_DX,
        SWING_LABEL_DY,
        TITLE_PADDING,
        XTICK_STEP,
        X_AXIS_ROUNDING_STEP,
        X_GRID_ALPHA,
        Y_GRID_ALPHA,
        Y_MAX_PADDING,
        Y_MIN_PADDING,
        arrow_plot_mode_dropdown,
        arrow_width_slider,
    )


@app.cell(hide_code=True)
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    SHIFT_MODE_NET,
    arrow_axis_column_names,
    compute_vote_shift,
    county_level_demo_analysis,
    filter_threshold,
    shift_mode,
):
    def _build_arrow_table_from_rows(
        prop50_row, pres2024_row, yes_suffix, no_suffix, mode
    ):
        def _arrow_row(group_id):
            yes_key = f"{group_id}{yes_suffix}"
            no_key = f"{group_id}{no_suffix}"

            swing = compute_vote_shift(prop50_row, pres2024_row, group_id, mode)
            row = {
                "Racial group": GROUP_DISPLAY_LABELS[group_id],
                "Swing from Harris to Prop 50": (
                    swing if swing is not None else ""
                ),
                "YES on Prop. 50 - pct": prop50_row[yes_key],
                "HARRIS - pct": pres2024_row[yes_key],
                "NO on Prop. 50 - pct": prop50_row[no_key],
                "TRUMP - pct": pres2024_row[no_key],
            }
            if mode == SHIFT_MODE_NET:
                pres_margin_col, prop_margin_col = arrow_axis_column_names(mode)
                row[pres_margin_col] = float(pres2024_row[yes_key]) - float(
                    pres2024_row[no_key]
                )
                row[prop_margin_col] = float(prop50_row[yes_key]) - float(
                    prop50_row[no_key]
                )
            return row

        rows = [
            row
            for group_id in ANALYSIS_GROUPS
            if (row := _arrow_row(group_id)) is not None
        ]
        return pd.DataFrame(rows) if rows else None


    def build_county_arrow_table(county):
        prop50_df = county_level_demo_analysis.get(PROP50_DATASET_ID)
        pres2024_df = county_level_demo_analysis.get(PRES2024_DATASET_ID)

        yes_suffix = f"_{filter_threshold}_yes_pct"
        no_suffix = f"_{filter_threshold}_no_pct"
        return _build_arrow_table_from_rows(
            prop50_df.loc[county],
            pres2024_df.loc[county],
            yes_suffix,
            no_suffix,
            shift_mode.value,
        )

    return (build_county_arrow_table,)


@app.cell(hide_code=True)
def _(
    ANALYSIS_GROUPS,
    GROUP_DISPLAY_LABELS,
    PRES2024_DATASET_ID,
    PROP50_DATASET_ID,
    SHIFT_MODE_NET,
    arrow_axis_column_names,
    majority_analysis,
    shift_mode,
):
    def build_statewide_arrow_table():
        prop50_statewide = majority_analysis.get(PROP50_DATASET_ID)
        pres2024_statewide = majority_analysis.get(PRES2024_DATASET_ID)
        mode = shift_mode.value

        rows = []
        for group_id in ANALYSIS_GROUPS:
            label = GROUP_DISPLAY_LABELS[group_id]
            prop50_row = prop50_statewide.loc[label]
            pres2024_row = pres2024_statewide.loc[label]

            if mode == SHIFT_MODE_NET:
                swing = vote_shift_net(
                    prop50_row["Yes %"],
                    prop50_row["No %"],
                    pres2024_row["Democrat %"],
                    pres2024_row["Republican %"],
                )
            else:
                swing = vote_shift_one_party(
                    prop50_row["Yes %"],
                    pres2024_row["Democrat %"],
                )

            row = {
                "Racial group": label,
                "Swing from Harris to Prop 50": (
                    swing if swing is not None else ""
                ),
                "YES on Prop. 50 - pct": prop50_row["Yes %"],
                "HARRIS - pct": pres2024_row["Democrat %"],
                "NO on Prop. 50 - pct": prop50_row["No %"],
                "TRUMP - pct": pres2024_row["Republican %"],
            }
            if mode == SHIFT_MODE_NET:
                pres_margin_col, prop_margin_col = arrow_axis_column_names(mode)
                row[pres_margin_col] = float(pres2024_row["Democrat %"]) - float(
                    pres2024_row["Republican %"]
                )
                row[prop_margin_col] = float(prop50_row["Yes %"]) - float(
                    prop50_row["No %"]
                )
            rows.append(row)
        return pd.DataFrame(rows) if rows else None

    return (build_statewide_arrow_table,)


@app.cell(hide_code=True)
def _(
    SHIFT_MODE_TABLE_CAPTION,
    arrow_plot_mode_dropdown,
    build_county_arrow_table,
    build_statewide_arrow_table,
    county_dropdown,
    shift_mode,
):
    _shift_caption = SHIFT_MODE_TABLE_CAPTION[shift_mode.value]
    if arrow_plot_mode_dropdown.value == "Statewide":
        arrow_plot_title = (
            f"Vote shift ({_shift_caption}): statewide by racial group"
        )
        arrow_plot_table = build_statewide_arrow_table()
    else:
        arrow_plot_title = (
            f"{county_dropdown.value} County — vote shift ({_shift_caption})"
        )
        arrow_plot_table = build_county_arrow_table(county_dropdown.value)
    return arrow_plot_table, arrow_plot_title


@app.cell
def _(arrow_plot_table):
    arrow_plot_table
    return


@app.cell(hide_code=True)
def _(
    ARROW_COLOR,
    DECREASE_COLOR,
    FIG_SIZE,
    FONT_SIZE,
    HARRIS_TICK_LABEL,
    HEADER_TICK_ALPHA,
    HEADER_TICK_COLOR,
    HEADER_TICK_DY_BOTTOM,
    HEADER_TICK_DY_TOP,
    HEADER_TICK_LW,
    HEADER_Y_OFFSET,
    PROP_50_TICK_LABEL,
    SHIFT_MODE_NET,
    SWING_LABEL_DX,
    SWING_LABEL_DY,
    TITLE_PADDING,
    XTICK_STEP,
    X_AXIS_ROUNDING_STEP,
    X_GRID_ALPHA,
    Y_GRID_ALPHA,
    Y_MAX_PADDING,
    Y_MIN_PADDING,
    arrow_axis_column_names,
    arrow_plot_mode_dropdown,
    arrow_plot_table,
    arrow_plot_title,
    arrow_width_slider,
    county_dropdown,
    shift_mode,
):
    """Arrow plot comparing Harris vs. Prop 50 support by racial group."""

    _mode = shift_mode.value
    _harris_col, _prop50_col = arrow_axis_column_names(_mode)
    _harris_header = (
        "2024 pres. margin" if _mode == SHIFT_MODE_NET else HARRIS_TICK_LABEL
    )
    _prop50_header = (
        "Prop 50 margin" if _mode == SHIFT_MODE_NET else PROP_50_TICK_LABEL
    )

    _df = arrow_plot_table[
        arrow_plot_table["Swing from Harris to Prop 50"].notnull()
    ].copy()
    _df["Swing from Harris to Prop 50"] = _df[
        "Swing from Harris to Prop 50"
    ].astype(float)
    _df = _df.sort_values(_prop50_col, ascending=False)

    _y_positions = list(range(len(_df)))[::-1]

    # Dynamically scale x-axis to the observed Harris/Prop. 50 values.
    _observed_min = (
        min(
            float(_df[_harris_col].min()),
            float(_df[_prop50_col].min()),
        )
        - SWING_LABEL_DX
    )
    _observed_max = (
        max(
            float(_df[_harris_col].max()),
            float(_df[_prop50_col].max()),
        )
        + SWING_LABEL_DX
    )

    # Round down/up to the nearest multiple of 5 for clean tick marks.
    _x_min = int(
        X_AXIS_ROUNDING_STEP * np.floor(_observed_min / X_AXIS_ROUNDING_STEP)
    )
    _x_max = int(
        X_AXIS_ROUNDING_STEP * np.ceil(_observed_max / X_AXIS_ROUNDING_STEP)
    )
    if _x_min == _x_max:
        _x_min -= X_AXIS_ROUNDING_STEP
        _x_max += X_AXIS_ROUNDING_STEP

    _fig, _ax = plt.subplots(figsize=FIG_SIZE)

    # plot arrows
    for _y, (_, _row) in zip(_y_positions, _df.iterrows()):
        _harris = _row[_harris_col]
        _prop50 = _row[_prop50_col]
        _swing = _row["Swing from Harris to Prop 50"]

        _is_decrease = _swing < 0
        _arrow_color = DECREASE_COLOR if _is_decrease else ARROW_COLOR
        _label_x = (
            _prop50 - SWING_LABEL_DX if _is_decrease else _prop50 + SWING_LABEL_DX
        )
        _label_ha = "right" if _is_decrease else "left"

        # Draw arrow from Harris to Prop 50 for each racial group.
        _ax.annotate(
            "",
            xy=(_prop50, _y),
            xytext=(_harris, _y),
            arrowprops=dict(
                arrowstyle="->",
                color=_arrow_color,
                lw=arrow_width_slider.value,
            ),
        )

        # Label the swing at the arrow tip, e.g. +7.4
        _sign = "+" if _swing >= 0 else ""
        _ax.text(
            _label_x,
            _y + SWING_LABEL_DY,
            f"{_sign}{_swing:.1f}",
            va="center",
            ha=_label_ha,
            fontsize=FONT_SIZE,
            color=_arrow_color,
        )

    _ax.set_yticks(_y_positions)
    _ax.set_yticklabels(_df["Racial group"])
    _ax.tick_params(axis="y", which="both", length=0)

    _ax.set_xlim(_x_min, _x_max)
    _ax.set_title(
        arrow_plot_title,
        pad=TITLE_PADDING,
    )
    _ax.set_axisbelow(True)

    # Vertical gridlines on x-axis, slightly more visible.
    _xticks_with_max = np.arange(_x_min, _x_max + 1, XTICK_STEP)
    # Ensure the axis upper bound is always labeled, even if the step misses it.
    if len(_xticks_with_max) == 0 or not np.isclose(_xticks_with_max[-1], _x_max):
        _xticks_with_max = np.append(_xticks_with_max, _x_max)
    _ax.set_xticks(_xticks_with_max)
    _ax.grid(axis="x", alpha=X_GRID_ALPHA, color="gray")

    # Horizontal gridlines
    _ax.grid(axis="y", alpha=Y_GRID_ALPHA, color="gray")

    # Align labels to the start/end of the top arrow (first row after sorting)
    _top_row = _df.iloc[0]
    _harris_point = float(_top_row[_harris_col])
    _prop50_point = float(_top_row[_prop50_col])
    _label_y = max(_y_positions) + HEADER_Y_OFFSET
    # add padding to the y-axis for the annotation labels
    _ax.set_ylim(Y_MIN_PADDING, max(_y_positions) + Y_MAX_PADDING)
    _ax.text(
        _harris_point,
        _label_y,
        _harris_header,
        ha="right",
        va="bottom",
        fontsize=FONT_SIZE,
        color="gray",
    )
    _ax.text(
        _prop50_point,
        _label_y,
        _prop50_header,
        ha="left",
        va="bottom",
        fontsize=FONT_SIZE,
        color="gray",
    )

    # Add small tick marks under the top labels for clarity.
    _tick_top = _label_y - HEADER_TICK_DY_TOP
    _tick_bottom = _label_y - HEADER_TICK_DY_BOTTOM
    _ax.vlines(
        [_harris_point, _prop50_point],
        _tick_bottom,
        _tick_top,
        colors=HEADER_TICK_COLOR,
        alpha=HEADER_TICK_ALPHA,
        linewidth=HEADER_TICK_LW,
    )

    # Style tweaks to better match the reference.
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.spines["left"].set_visible(False)
    _ax.spines["bottom"].set_visible(False)

    _fig.tight_layout()
    _arrow_plot_output = _fig

    _county_dropdown = (
        county_dropdown if arrow_plot_mode_dropdown.value == "County" else "\n"
    )
    mo.vstack(
        [
            arrow_plot_mode_dropdown,
            _county_dropdown,
            arrow_width_slider,
            _arrow_plot_output,
        ]
    )
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
        "vote_shift_net",
        "flipped",
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
        "vote_shift_net",
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
        "vote_shift_net",
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


if __name__ == "__main__":
    app.run()
