import marimo

__generated_with = "0.19.2"
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
    return (CVAP_EST_COLUMN_SUFFIX,)


@app.cell
def _():
    TENTHS_PLACE_ROUNDING = 1
    return (TENTHS_PLACE_ROUNDING,)


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
def _(TENTHS_PLACE_ROUNDING):
    def calculate_percentage(numerator, denominator, digits=TENTHS_PLACE_ROUNDING):
        return round((numerator / denominator) * 100, digits)
    return (calculate_percentage,)


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
    return


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


@app.cell
def _(CVAP_EST_COLUMN_SUFFIX, cvap_gdf):
    extensive_variables_to_interpolate = [
        column
        for column in list(cvap_gdf)
        if column.endswith(CVAP_EST_COLUMN_SUFFIX)
    ]

    subgroup_est_columns = [
        column
        for column in extensive_variables_to_interpolate
        if "total" not in column
    ]
    return extensive_variables_to_interpolate, subgroup_est_columns


@app.cell
def _(
    audited_precinct_results_gdf,
    calculate_percentage,
    cvap_gdf,
    extensive_variables_to_interpolate,
    pd,
    subgroup_est_columns,
    tobler,
):
    cvap_precinct_estimates = tobler.area_weighted.area_interpolate(
        cvap_gdf,
        audited_precinct_results_gdf.set_index("precinct_id"),
        extensive_variables=extensive_variables_to_interpolate,
    )
    cvap_precinct_estimates = cvap_precinct_estimates[
        extensive_variables_to_interpolate
    ].apply(round)

    cvap_precinct_estimates["interpolated_total_est"] = cvap_precinct_estimates[
        subgroup_est_columns
    ].sum(axis=1)
    pct_columns = {
        f"{column_name}_pct": calculate_percentage(
            cvap_precinct_estimates[column_name],
            cvap_precinct_estimates["interpolated_total_est"],
        )
        for column_name in subgroup_est_columns
    }
    cvap_precinct_estimates = pd.concat(
        [cvap_precinct_estimates, pd.DataFrame(pct_columns)], axis=1
    )

    pct_column_names = [
        column
        for column in list(cvap_precinct_estimates)
        if column.endswith("pct")
    ]
    cvap_precinct_estimates[pct_column_names]
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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
