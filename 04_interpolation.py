import marimo

__generated_with = "0.19.2"
app = marimo.App(width="columns")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    import tobler
    return gpd, mo, tobler


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
    cvap_gdf,
    extensive_variables_to_interpolate,
    tobler,
):
    cvap_precinct_estimates = tobler.area_weighted.area_interpolate(
        cvap_gdf,
        audited_precinct_results_gdf,
        extensive_variables=extensive_variables_to_interpolate,
    )
    cvap_precinct_estimates = cvap_precinct_estimates[
        extensive_variables_to_interpolate
    ].apply(round)
    return


@app.cell
def _(cvap_gdf, subgroup_est_columns):
    cvap_gdf["interpolated_total_est"] = cvap_gdf[subgroup_est_columns].sum(axis=1)
    cvap_gdf
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
