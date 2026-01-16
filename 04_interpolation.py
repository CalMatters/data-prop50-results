import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import tobler
    return gpd, mo, pd, tobler


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    COUNTIES_PASSING_AUIDIT = ["Los Angeles"]
    return (COUNTIES_PASSING_AUIDIT,)


@app.cell
def _():
    CVAP_EST_COLUMN_SUFFIX = "_est"
    CVAP_COLUMN_KEYWORD = "CVAP"
    return CVAP_COLUMN_KEYWORD, CVAP_EST_COLUMN_SUFFIX


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filepaths
    """)
    return


@app.cell
def _():
    RESULTS_FP = "./outputs/precinct_results.gpkg"
    return (RESULTS_FP,)


@app.cell
def _():
    CVAP_FP = "./outputs/cvap_tracts.gpkg"
    return (CVAP_FP,)


@app.cell
def _():
    CVAP_BLOCKS_FP = "./outputs/cvap_blocks.gpkg"
    return (CVAP_BLOCKS_FP,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper functions
    """)
    return


@app.cell
def _():
    TENTHS_PLACE_ROUNDING = 1


    def calculate_percentage(numerator, denominator, digits=TENTHS_PLACE_ROUNDING):
        return round((numerator / denominator) * 100, digits)
    return (calculate_percentage,)


@app.function
def get_percentage_columns(df, suffix="pct"):
    """
    Select and display only the columns ending with the specified suffix from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing the data
    suffix : str, optional
        Suffix to filter column names by (default is "pct")

    Returns
    -------
    pd.DataFrame
        DataFrame containing only the columns that end with the specified suffix
    """
    pct_column_names = [
        column for column in list(df) if column.endswith(suffix)
    ]
    return df[pct_column_names]


@app.cell
def _(calculate_percentage, pd):
    def join_pct_columns(
        df: pd.DataFrame, numerator_columns: list[str], denominator_column: str
    ) -> pd.DataFrame:
        """
        Calculate percentage columns based on numerator columns and a denominator column.

        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe containing the data
        numerator_columns : list of str
            List of column names to use as numerators for percentage calculation
        denominator_column : str
            Column name to use as denominator for percentage calculation

        Returns
        -------
        pd.DataFrame
            DataFrame with additional percentage columns appended
        """
        df_copy = df.copy()

        # Create percentage columns using dictionary comprehension
        pct_columns = {
            f"{col}_pct": calculate_percentage(
                df_copy[col], df_copy[denominator_column]
            )
            for col in numerator_columns
        }

        # Concatenate the new percentage columns to the original dataframe
        df_copy = pd.concat(
            [df_copy, pd.DataFrame(pct_columns, index=df_copy.index)], axis=1
        )

        return df_copy
    return (join_pct_columns,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(gpd):
    def read_gis_data(fp, **read_file_kwargs):
        gdf = gpd.read_file(fp, **read_file_kwargs)
        print(f"COLUMNS: {list(gdf)}")
        return gdf
    return (read_gis_data,)


@app.cell
def _(RESULTS_FP, read_gis_data):
    precinct_results_gdf = read_gis_data(RESULTS_FP)
    precinct_results_gdf.head()
    return (precinct_results_gdf,)


@app.cell
def _(CVAP_FP, read_gis_data):
    cvap_gdf = read_gis_data(CVAP_FP)
    cvap_gdf.head()
    return (cvap_gdf,)


@app.cell
def _(CVAP_BLOCKS_FP, read_gis_data):
    cvap_block_gdf = read_gis_data(CVAP_BLOCKS_FP)
    cvap_block_gdf.head()
    return (cvap_block_gdf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Filter

    I am filtering for counties where the results have passed a data audit in notebook `03`.
    """)
    return


@app.cell
def _(COUNTIES_PASSING_AUIDIT, precinct_results_gdf):
    has_county_passed_audit = precinct_results_gdf["county"].isin(
        COUNTIES_PASSING_AUIDIT
    )
    audited_precinct_results_gdf = precinct_results_gdf[has_county_passed_audit]
    audited_precinct_results_gdf
    return (audited_precinct_results_gdf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Interpolate

    [Tobler example Jupyter notebook interpolating tracts to voting precincts](https://pysal.org/tobler/notebooks/02_areal_interpolation_example.html).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CVAP by tract
    """)
    return


@app.cell
def _(CVAP_EST_COLUMN_SUFFIX, cvap_gdf):
    tracts_extensive_variables_to_interpolate = [
        column
        for column in list(cvap_gdf)
        if column.endswith(CVAP_EST_COLUMN_SUFFIX)
    ]

    tracts_subgroup_est_columns = [
        column
        for column in tracts_extensive_variables_to_interpolate
        if "total" not in column
    ]
    return (
        tracts_extensive_variables_to_interpolate,
        tracts_subgroup_est_columns,
    )


@app.cell
def _(cvap_precinct_estimates):
    # Display percentage columns
    get_percentage_columns(cvap_precinct_estimates)
    return


@app.cell
def _(
    audited_precinct_results_gdf,
    cvap_gdf,
    join_pct_columns,
    tobler,
    tracts_extensive_variables_to_interpolate,
    tracts_subgroup_est_columns,
):
    cvap_precinct_estimates = tobler.area_weighted.area_interpolate(
        cvap_gdf,
        audited_precinct_results_gdf.set_index("precinct_id"),
        extensive_variables=tracts_extensive_variables_to_interpolate,
    )
    cvap_precinct_estimates = cvap_precinct_estimates[
        tracts_extensive_variables_to_interpolate
    ].apply(round)

    cvap_precinct_estimates["_interpolated_total_est"] = cvap_precinct_estimates[
        tracts_subgroup_est_columns
    ].sum(axis=1)

    cvap_precinct_estimates = join_pct_columns(
        df=cvap_precinct_estimates,
        numerator_columns=tracts_subgroup_est_columns,
        denominator_column="_interpolated_total_est",
    )
    return (cvap_precinct_estimates,)


@app.cell
def _(audited_precinct_results_gdf, cvap_precinct_estimates):
    precincts_results_cvap_merged = audited_precinct_results_gdf.merge(
        cvap_precinct_estimates,
        left_on="precinct_id",
        right_index=True,
        validate="1:1",
    )
    precincts_results_cvap_merged.plot()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CVAP by block
    """)
    return


@app.cell
def _(
    CVAP_COLUMN_KEYWORD,
    audited_precinct_results_gdf,
    cvap_block_gdf,
    join_pct_columns,
    tobler,
):
    block_extensive_vars = [
        column
        for column in list(cvap_block_gdf)
        if CVAP_COLUMN_KEYWORD in column.upper()
    ]
    block_subgroup_est_columns = [
        column for column in block_extensive_vars if "TOT" not in column
    ]

    cvap_block_precinct_estimates = tobler.area_weighted.area_interpolate(
        cvap_block_gdf,
        audited_precinct_results_gdf.set_index("precinct_id"),
        extensive_variables=block_extensive_vars,
    )

    cvap_block_precinct_estimates = cvap_block_precinct_estimates[
        block_extensive_vars
    ].apply(round)
    cvap_block_precinct_estimates["_interpolated_total_est"] = (
        cvap_block_precinct_estimates[block_subgroup_est_columns].sum(axis=1)
    )
    cvap_block_precinct_estimates = join_pct_columns(
        cvap_block_precinct_estimates,
        block_extensive_vars,
        "_interpolated_total_est",
    )

    precincts_results_cvap_block_merged = audited_precinct_results_gdf.merge(
        cvap_block_precinct_estimates,
        left_on="precinct_id",
        right_index=True,
        validate="1:1",
    )
    precincts_results_cvap_block_merged.plot()
    return block_subgroup_est_columns, cvap_block_precinct_estimates


@app.cell(hide_code=True)
def _(block_subgroup_est_columns, mo, tracts_subgroup_est_columns):
    mo.md(rf"""
    # Explore interpolation results

    1. What is the difference between the interpolated source total and the sum of each subgroup's interpolated total

    This exploration assumes that the subgroup column sum should be close to the interpolated sum: 

    TRACTS: {f"SUM({list(tracts_subgroup_est_columns)} = interpolated sum)"}

    BLOCKS: {f"SUM({list(block_subgroup_est_columns)} = interpolated sum)"}
    """)
    return


@app.cell
def _(calculate_percentage, pd):
    def evaluate_interpolation_accuracy(
        df: pd.DataFrame,
        subgroup_columns: list[str],
        total_column: str,
        description: str = "",
    ) -> pd.DataFrame:
        """
        Evaluate the accuracy of areal interpolation by comparing the sum of subgroup estimates
        to the interpolated total.

        This function helps assess how well the interpolation preserved the original data constraints,
        where the sum of subgroup estimates should approximately equal the interpolated total.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the interpolated data
        subgroup_columns : list of str
            List of column names representing subgroups that should sum to the total
        total_column : str
            Column name representing the interpolated total to compare against
        description : str, optional
            Optional description of the data source (e.g., "Tracts", "Blocks") for reporting

        Returns
        -------
        pd.DataFrame
            Summary DataFrame with:
            - subgroup_sum: sum of all subgroup columns
            - total_column: the provided total column value
            - difference: difference between subgroup sum and total
            - percent_difference: percent difference relative to the total
        """
        # Calculate sum of subgroups
        subgroup_sum_col = "_subgroup_sum"
        df[subgroup_sum_col] = df[subgroup_columns].sum(axis=1)

        # Calculate differences
        difference = df[subgroup_sum_col] - df[total_column]
        percent_difference = calculate_percentage(difference, df[total_column])

        # Create summary
        summary = pd.DataFrame(
            {
                "source": description,
                "subgroup_sum": df[subgroup_sum_col],
                "interpolated_source_total": df[total_column],
                "difference": difference,
                "percent_difference": percent_difference,
            }
        )

        return summary.round({"difference": 2, "percent_difference": 2})
    return (evaluate_interpolation_accuracy,)


@app.cell
def _(tract_interpolation_summary):
    tract_interpolation_summary
    return


@app.cell
def _(tract_interpolation_summary):
    tract_interpolation_summary
    return


@app.cell
def _(
    block_subgroup_est_columns,
    cvap_block_precinct_estimates,
    cvap_precinct_estimates,
    evaluate_interpolation_accuracy,
    tracts_subgroup_est_columns,
):
    # Evaluate interpolation accuracy for tracts
    tract_interpolation_summary = evaluate_interpolation_accuracy(
        df=cvap_precinct_estimates,
        subgroup_columns=tracts_subgroup_est_columns,
        total_column="total_cvap_est",
        description="Tracts",
    )

    # Evaluate interpolation accuracy for blocks
    block_interpolation_summary = evaluate_interpolation_accuracy(
        df=cvap_block_precinct_estimates,
        subgroup_columns=block_subgroup_est_columns,
        total_column="CVAP_TOT23",
        description="Blocks",
    )

    block_interpolation_summary_described = block_interpolation_summary.describe()
    # Display summaries
    tract_interpolation_summary.describe(), block_interpolation_summary.describe()
    return block_interpolation_summary, tract_interpolation_summary


@app.cell
def _(block_interpolation_summary, tract_interpolation_summary):
    print(
        f"Tract interpolation - subgroup sum: {sum(tract_interpolation_summary['subgroup_sum']):,}, interpolated total: {sum(tract_interpolation_summary['interpolated_source_total']):,}"
    )
    print(
        f"Block interpolation - subgroup sum: {sum(block_interpolation_summary['subgroup_sum']):,}, interpolated total: {sum(block_interpolation_summary['interpolated_source_total']):,}"
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
