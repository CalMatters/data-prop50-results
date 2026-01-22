import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    return gpd, mo, pd, plt


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

    # Create percentage version of the mapping
    STANDARDIZED_GROUP_LABELS_PCT = {
        key: {
            "tracts": value["tracts"].replace("_est", "_est_pct"),
            "blocks": value["blocks"] + "_pct",
        }
        for key, value in STANDARDIZED_GROUP_LABELS.items()
    }
    return (STANDARDIZED_GROUP_LABELS_PCT,)


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
    ## Helper functions
    """)
    return


@app.cell
def _(gpd):
    def read_gis_data(fp, name="", **read_file_kwargs):
        gdf = gpd.read_file(fp, **read_file_kwargs)
        print(f"{name.upper()} COLUMNS: {list(gdf)}")
        return gdf
    return (read_gis_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(
    PRECINCT_RESULTS_BLOCKS_FP,
    PRECINCT_RESULTS_TRACTS_FP,
    VOTE_COUNT_COLUMNS,
    pd,
    read_gis_data,
):
    precinct_results_tracts = read_gis_data(PRECINCT_RESULTS_TRACTS_FP, "tracts")
    precinct_results_tracts = precinct_results_tracts.replace("-1", pd.NA)

    precinct_results_blocks = read_gis_data(PRECINCT_RESULTS_BLOCKS_FP, "blocks")
    precinct_results_blocks = precinct_results_blocks.replace("-1", pd.NA)

    for column in VOTE_COUNT_COLUMNS:
        precinct_results_blocks[column] = pd.to_numeric(
            precinct_results_blocks[column]
        )
        precinct_results_tracts[column] = pd.to_numeric(
            precinct_results_tracts[column]
        )
    return precinct_results_blocks, precinct_results_tracts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Prepare data
    """)
    return


@app.function
def caclulate_pct(numerator, denominator):
    return round((numerator / denominator) * 100, 1)


@app.cell
def _(pd):
    def calculate_yes_pct(precincts_df):
        df = precincts_df.copy()
        # Handle cases where one column is null and the other is not
        yes_null = df["yes_votes"].isna()
        no_null = df["no_votes"].isna()

        # If yes_votes is null and no_votes is not null, set yes_votes to 0
        df.loc[yes_null & ~no_null, "yes_votes"] = 0
        # If no_votes is null and yes_votes is not null, set no_votes to 0
        df.loc[no_null & ~yes_null, "no_votes"] = 0

        # Set total_votes after filling nulls
        total_votes = df["yes_votes"] + df["no_votes"]

        # Initialize yes_pct as null (NaN) where both yes_votes and no_votes are null
        both_null = yes_null & no_null
        df["yes_pct"] = pd.NA

        # Calculate yes_pct only where total votes are > 0
        valid_total_mask = total_votes > 0
        df.loc[valid_total_mask, "yes_pct"] = caclulate_pct(
            df.loc[valid_total_mask, "yes_votes"], total_votes[valid_total_mask]
        )

        return df
    return (calculate_yes_pct,)


@app.cell
def _(calculate_yes_pct, precinct_results_blocks, precinct_results_tracts):
    precinct_results_blocks_new = calculate_yes_pct(precinct_results_blocks)
    precinct_results_tracts_new = calculate_yes_pct(precinct_results_tracts)
    precinct_results_blocks_new[precinct_results_blocks_new["yes_pct"].isna()]
    return precinct_results_blocks_new, precinct_results_tracts_new


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hypothesis #1:

    > If there are more white voters in a precinct, then there will be a higher vote share for "No" on Prop. 50
    """)
    return


@app.cell
def _(plt):
    def plot_yes_pct_vs_cvap(
        df, cvap_column, yes_pct_column, group_label="White", title_suffix=""
    ):
        # Handle NaN values by dropping them for plotting
        plot_data = df.dropna(subset=[cvap_column, yes_pct_column])

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.scatter(
            plot_data[cvap_column],
            plot_data[yes_pct_column],
            alpha=0.6,
            s=50,
            edgecolor="none",
        )

        ax.set_xlabel(f"Percent {group_label} CVAP")
        ax.set_ylabel("Yes Vote Percentage")
        ax.set_title(
            f"Yes Vote Percentage vs. Percent {group_label} CVAP {title_suffix}"
        )
        ax.grid(True, alpha=0.3)

        # Set axis limits to ensure full visibility
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        # Use plt.gca() as the last expression
        return plt.gca()
    return (plot_yes_pct_vs_cvap,)


@app.cell
def _(
    STANDARDIZED_GROUP_LABELS_PCT,
    demo_group_dropdown,
    plot_yes_pct_vs_cvap,
    precinct_results_blocks_new,
):
    # Example usage:
    plot_yes_pct_vs_cvap(
        precinct_results_blocks_new,
        STANDARDIZED_GROUP_LABELS_PCT[demo_group_dropdown.value]["blocks"],
        "yes_pct",
        "White",
        "(Blocks)",
    )
    return


@app.cell
def _(plot_yes_pct_vs_cvap, precinct_results_tracts_new):
    # Example usage:
    plot_yes_pct_vs_cvap(
        precinct_results_tracts_new,
        "white_alone_cvap_est_pct",
        "yes_pct",
        "White",
        "(Tracts)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demographic scatterplot

    Convert the historgram to an explore panel
    """)
    return


@app.cell
def _(STANDARDIZED_GROUP_LABELS_PCT, mo):
    demo_group_dropdown = mo.ui.dropdown(
        options=STANDARDIZED_GROUP_LABELS_PCT.keys(), value="white"
    )
    demo_group_dropdown
    return (demo_group_dropdown,)


@app.cell
def _(
    STANDARDIZED_GROUP_LABELS_PCT,
    demo_group_dropdown,
    plot_yes_pct_vs_cvap,
    precinct_results_blocks_new,
):
    # Example usage:
    plot_yes_pct_vs_cvap(
        precinct_results_blocks_new,
        STANDARDIZED_GROUP_LABELS_PCT[demo_group_dropdown.value]["blocks"],
        "yes_pct",
        demo_group_dropdown.value.title(),
        "(Blocks)",
    )
    return


@app.cell
def _(
    STANDARDIZED_GROUP_LABELS_PCT,
    demo_group_dropdown,
    plot_yes_pct_vs_cvap,
    precinct_results_tracts_new,
):
    # Example usage:
    plot_yes_pct_vs_cvap(
        precinct_results_tracts_new,
        STANDARDIZED_GROUP_LABELS_PCT[demo_group_dropdown.value]["tracts"],
        "yes_pct",
        demo_group_dropdown.value.title(),
        "(Tracts)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demographic correlation coefficient

    [User's guide to correlation coefficients](https://pmc.ncbi.nlm.nih.gov/articles/PMC6107969/#sec2)
    """)
    return


@app.cell
def _(
    STANDARDIZED_GROUP_LABELS_PCT,
    demo_group_dropdown,
    precinct_results_blocks_new,
):
    precinct_results_blocks_new[
        [
            STANDARDIZED_GROUP_LABELS_PCT[demo_group_dropdown.value]["blocks"],
            "yes_pct",
        ]
    ].dropna().corr(method="pearson")
    return


@app.cell
def _(
    STANDARDIZED_GROUP_LABELS_PCT,
    demo_group_dropdown,
    precinct_results_tracts_new,
):
    precinct_results_tracts_new[
        [
            STANDARDIZED_GROUP_LABELS_PCT[demo_group_dropdown.value]["tracts"],
            "yes_pct",
        ]
    ].dropna().corr(method="pearson")
    return


@app.cell(disabled=True)
def _(precinct_results_blocks_new):
    # output too large to use this
    import altair as alt

    # Create a scatter plot with Altair
    chart = (
        alt.Chart(precinct_results_blocks_new)
        .mark_point(opacity=0.6)
        .encode(
            x=alt.X("CVAP_WHT23_pct:Q", title="Percent White CVAP"),
            y=alt.Y("yes_pct:Q", title="Yes Vote Percentage"),
            tooltip=["CVAP_WHT23_pct", "yes_pct"],
        )
        .interactive()
    )

    chart
    return


if __name__ == "__main__":
    app.run()
