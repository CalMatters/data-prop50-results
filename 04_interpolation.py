import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    from glob import glob

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    from shapely.geometry import Point
    import tobler
    return Point, glob, gpd, mo, pd, tobler


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell
def _():
    # counties where the audit found a mismatch of 2 or fewer precincts
    # an exception was made for OC due to many unpopulated precincts
    # existing in the GIS file and not in the results
    ADDTNL_COUNTIES_PASSING_AUIDIT = [
        "Los Angeles",
        "Inyo",
        "Marin",
        "Merced",
        "Orange",
        "Shasta",
        "Tulare",
    ]
    return (ADDTNL_COUNTIES_PASSING_AUIDIT,)


@app.cell
def _():
    CVAP_EST_COLUMN_SUFFIX = "_est"
    CVAP_COLUMN_KEYWORD = "CVAP"
    return CVAP_COLUMN_KEYWORD, CVAP_EST_COLUMN_SUFFIX


@app.cell
def _():
    MERGE_KEYS = ["precinct_id", "county"]
    return (MERGE_KEYS,)


@app.cell
def _():
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )
    return (PROJECTED_CRS,)


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


@app.cell
def _():
    AUDIT_SUMMARY_FILE_PREFIX = "./debug/audit_summary_*"
    return (AUDIT_SUMMARY_FILE_PREFIX,)


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


@app.function
def validate_and_reproject_geometries(source_gdf, target_gdf, projected_crs):
    """
    Validate geometries using buffer(0) for invalid ones and reproject to target CRS.

    Parameters
    ----------
    source_gdf : gpd.GeoDataFrame
        Source GeoDataFrame (e.g., CVAP tracts or blocks)
    target_gdf : gpd.GeoDataFrame
        Target GeoDataFrame (e.g., precincts)
    projected_crs : str
        Target CRS to reproject to (e.g., "EPSG:3310")

    Returns
    -------
    tuple
        (validated_source_gdf, validated_target_gdf) both in projected_crs
    """
    # Validate and fix source geometries
    _temp_source_invalid = ~source_gdf.geometry.is_valid
    _temp_source_valid = source_gdf.copy()
    if _temp_source_invalid.any():
        _temp_source_valid.loc[_temp_source_invalid, "geometry"] = (
            _temp_source_valid.loc[_temp_source_invalid, "geometry"].buffer(0)
        )

    # Validate and fix target geometries
    _temp_target_invalid = ~target_gdf.geometry.is_valid
    _temp_target_valid = target_gdf.copy()
    if _temp_target_invalid.any():
        _temp_target_valid.loc[_temp_target_invalid, "geometry"] = (
            _temp_target_valid.loc[_temp_target_invalid, "geometry"].buffer(0)
        )

    # Reproject both to target CRS
    _temp_source_proj = _temp_source_valid.to_crs(projected_crs)
    _temp_target_proj = _temp_target_valid.to_crs(projected_crs)

    return _temp_source_proj, _temp_target_proj


@app.cell
def _(tobler):
    def interpolate_and_calculate_percentages(
        source_gdf,
        target_gdf,
        extensive_variables,
        subgroup_columns,
        merge_keys,
        join_pct_columns_func,
    ):
        """
        Perform area-weighted interpolation and calculate percentages.

        Parameters
        ----------
        source_gdf : gpd.GeoDataFrame
            Source GeoDataFrame (e.g., CVAP tracts or blocks) in projected CRS
        target_gdf : gpd.GeoDataFrame
            Target GeoDataFrame (e.g., precincts) in projected CRS, indexed by merge_keys
        extensive_variables : list[str]
            List of extensive variable column names to interpolate
        subgroup_columns : list[str]
            List of subgroup columns to sum for total calculation
        merge_keys : list[str]
            List of column names used as index in target_gdf
        join_pct_columns_func : callable
            Function to add percentage columns

        Returns
        -------
        pd.DataFrame
            DataFrame with interpolated estimates and percentage columns
        """
        # Perform area-weighted interpolation
        _temp_interpolated = tobler.area_weighted.area_interpolate(
            source_gdf,
            target_gdf,
            extensive_variables=extensive_variables,
        )

        # Round extensive variables
        _temp_interpolated = _temp_interpolated[extensive_variables].apply(round)

        # Calculate interpolated total from subgroups
        _temp_interpolated["_interpolated_total_est"] = _temp_interpolated[
            subgroup_columns
        ].sum(axis=1)

        # Add percentage columns
        _temp_interpolated = join_pct_columns_func(
            df=_temp_interpolated,
            numerator_columns=subgroup_columns,
            denominator_column="_interpolated_total_est",
        )

        return _temp_interpolated
    return (interpolate_and_calculate_percentages,)


@app.function
def merge_interpolated_results(
    precincts_gdf, interpolated_estimates, merge_keys
):
    """
    Merge interpolated estimates back to precincts GeoDataFrame.

    Parameters
    ----------
    precincts_gdf : gpd.GeoDataFrame
        Original precincts GeoDataFrame
    interpolated_estimates : pd.DataFrame
        Interpolated estimates DataFrame with index matching merge_keys
    merge_keys : list[str]
        List of column names to merge on

    Returns
    -------
    gpd.GeoDataFrame
        Merged GeoDataFrame with interpolated estimates
    """
    _temp_merged = precincts_gdf.merge(
        interpolated_estimates,
        left_on=merge_keys,
        right_index=True,
        validate="1:1",
    )
    return _temp_merged


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


@app.cell
def _(ADDTNL_COUNTIES_PASSING_AUIDIT, AUDIT_SUMMARY_FILE_PREFIX, glob, pd):
    audits_fps = sorted(glob(AUDIT_SUMMARY_FILE_PREFIX), reverse=True)
    latest_audit_summary_fp = audits_fps[0] if audits_fps else ""

    if latest_audit_summary_fp:
        audit_summary_df = pd.read_csv(latest_audit_summary_fp, index_col=0)

        counties_without_failed_matches = audit_summary_df[
            (audit_summary_df["missing_in_gis"] == 0)
            & (audit_summary_df["missing_in_results"] == 0)
        ].index.tolist()

    counties_passing_audit = (
        ADDTNL_COUNTIES_PASSING_AUIDIT + counties_without_failed_matches
    )
    counties_passing_audit
    counties_passing_audit
    return (counties_passing_audit,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Filter

    I am filtering for counties where the results have passed a data audit in notebook `03`.
    """)
    return


@app.cell
def _(counties_passing_audit, precinct_results_gdf):
    has_county_passed_audit = precinct_results_gdf["county"].isin(
        counties_passing_audit
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
    MERGE_KEYS,
    PROJECTED_CRS,
    audited_precinct_results_gdf,
    cvap_gdf,
    interpolate_and_calculate_percentages,
    join_pct_columns,
    tracts_extensive_variables_to_interpolate,
    tracts_subgroup_est_columns,
):
    # Validate geometries and reproject to target CRS
    _temp_cvap_proj, _temp_precincts_proj = validate_and_reproject_geometries(
        cvap_gdf, audited_precinct_results_gdf, PROJECTED_CRS
    )

    # Set index for target GeoDataFrame
    _temp_target_gdf = _temp_precincts_proj.set_index(MERGE_KEYS)

    # Perform interpolation and calculate percentages
    cvap_precinct_estimates = interpolate_and_calculate_percentages(
        source_gdf=_temp_cvap_proj,
        target_gdf=_temp_target_gdf,
        extensive_variables=tracts_extensive_variables_to_interpolate,
        subgroup_columns=tracts_subgroup_est_columns,
        merge_keys=MERGE_KEYS,
        join_pct_columns_func=join_pct_columns,
    )
    return (cvap_precinct_estimates,)


@app.cell
def _(MERGE_KEYS, audited_precinct_results_gdf, cvap_precinct_estimates):
    precincts_results_cvap_merged = merge_interpolated_results(
        audited_precinct_results_gdf, cvap_precinct_estimates, MERGE_KEYS
    )
    precincts_results_cvap_merged.plot()
    return (precincts_results_cvap_merged,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CVAP by block
    """)
    return


@app.cell
def _(
    CVAP_COLUMN_KEYWORD,
    MERGE_KEYS,
    PROJECTED_CRS,
    audited_precinct_results_gdf,
    cvap_block_gdf,
    interpolate_and_calculate_percentages,
    join_pct_columns,
):
    # Identify block extensive variables
    block_extensive_vars = [
        column
        for column in list(cvap_block_gdf)
        if CVAP_COLUMN_KEYWORD in column.upper()
    ]
    block_subgroup_est_columns = [
        column for column in block_extensive_vars if "TOT" not in column
    ]

    # Validate geometries and reproject to target CRS
    _temp_cvap_block_proj, _temp_precincts_proj = (
        validate_and_reproject_geometries(
            cvap_block_gdf, audited_precinct_results_gdf, PROJECTED_CRS
        )
    )

    # Set index for target GeoDataFrame
    _temp_target_gdf = _temp_precincts_proj.set_index(MERGE_KEYS)

    # Perform interpolation and calculate percentages
    cvap_block_precinct_estimates = interpolate_and_calculate_percentages(
        source_gdf=_temp_cvap_block_proj,
        target_gdf=_temp_target_gdf,
        extensive_variables=block_extensive_vars,
        subgroup_columns=block_subgroup_est_columns,
        merge_keys=MERGE_KEYS,
        join_pct_columns_func=join_pct_columns,
    )
    return block_subgroup_est_columns, cvap_block_precinct_estimates


@app.cell
def _(MERGE_KEYS, audited_precinct_results_gdf, cvap_block_precinct_estimates):
    precincts_results_cvap_block_merged = merge_interpolated_results(
        audited_precinct_results_gdf, cvap_block_precinct_estimates, MERGE_KEYS
    )
    precincts_results_cvap_block_merged.plot()
    return (precincts_results_cvap_block_merged,)


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Export
    """)
    return


@app.cell
def _(precincts_results_cvap_block_merged, precincts_results_cvap_merged):
    precincts_results_cvap_merged.to_file(
        "./outputs/precincts_results_cvap_tracts.gpkg", driver="GPKG"
    )
    precincts_results_cvap_block_merged.to_file(
        "./outputs/precincts_results_cvap_blocks.gpkg", driver="GPKG"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Appendix: Debug and Validation Tools

    The following cells contain diagnostic tools for debugging geometry validation and CRS issues.
    These tools were used to identify and fix the topology errors encountered during interpolation.
    They are preserved here for future reference and troubleshooting.

    **Key diagnostic features:**
    - Geometry validation checks (identifies invalid geometries)
    - Automatic geometry repair using `buffer(0)` method
    - CRS verification and reprojection
    - Coordinate bounds checking
    - Problematic geometry location identification
    """)
    return


@app.cell
def _(PROJECTED_CRS, Point, audited_precinct_results_gdf, cvap_gdf):
    # Check CRS of both GeoDataFrames
    print(f"CVAP GDF CRS: {cvap_gdf.crs}")
    print(f"Precincts GDF CRS: {audited_precinct_results_gdf.crs}")

    # Check for invalid geometries
    _temp_cvap_invalid = ~cvap_gdf.geometry.is_valid
    _temp_precincts_invalid = ~audited_precinct_results_gdf.geometry.is_valid

    print(f"\nInvalid geometries in CVAP: {_temp_cvap_invalid.sum()}")
    print(f"Invalid geometries in Precincts: {_temp_precincts_invalid.sum()}")

    if _temp_cvap_invalid.any():
        print("\nCVAP invalid geometries:")
        _temp_invalid_cols = ["geoid"] if "geoid" in cvap_gdf.columns else []
        print(cvap_gdf[_temp_cvap_invalid][_temp_invalid_cols])

    if _temp_precincts_invalid.any():
        print("\nPrecincts invalid geometries:")
        print(
            audited_precinct_results_gdf[_temp_precincts_invalid][
                ["county", "precinct_id"]
            ]
        )

    # Make geometries valid if needed
    _temp_cvap_gdf_valid = cvap_gdf.copy()
    if _temp_cvap_invalid.any():
        print("\nMaking CVAP geometries valid...")
        _temp_cvap_gdf_valid.loc[_temp_cvap_invalid, "geometry"] = (
            _temp_cvap_gdf_valid.loc[_temp_cvap_invalid, "geometry"].buffer(0)
        )

    _temp_precincts_gdf_valid = audited_precinct_results_gdf.copy()
    if _temp_precincts_invalid.any():
        print("\nMaking precinct geometries valid...")
        _temp_precincts_gdf_valid.loc[_temp_precincts_invalid, "geometry"] = (
            _temp_precincts_gdf_valid.loc[
                _temp_precincts_invalid, "geometry"
            ].buffer(0)
        )

    # Ensure both are in the same CRS
    cvap_gdf_ai_validated = _temp_cvap_gdf_valid.to_crs(PROJECTED_CRS)
    precincts_gdf_ai_validated = _temp_precincts_gdf_valid.to_crs(PROJECTED_CRS)

    # Check bounds to see if coordinates make sense
    print(f"\nCVAP bounds: {cvap_gdf_ai_validated.total_bounds}")
    print(f"Precincts bounds: {precincts_gdf_ai_validated.total_bounds}")

    # Look for geometries near the problematic coordinates
    _temp_problem_x, _temp_problem_y = -200152.7632203573, -1406.7365180175839
    print(
        f"\nSearching for geometries near problematic coordinates: ({_temp_problem_x}, {_temp_problem_y})"
    )

    # Create a small buffer around the problem point
    _temp_problem_point = Point(_temp_problem_x, _temp_problem_y)
    _temp_buffer_distance = 1000  # 1km buffer

    # Check if any geometries intersect with this area
    _temp_cvap_near_problem = cvap_gdf_ai_validated[
        cvap_gdf_ai_validated.geometry.intersects(
            _temp_problem_point.buffer(_temp_buffer_distance)
        )
    ]
    _temp_precincts_near_problem = precincts_gdf_ai_validated[
        precincts_gdf_ai_validated.geometry.intersects(
            _temp_problem_point.buffer(_temp_buffer_distance)
        )
    ]

    print(f"CVAP geometries near problem: {len(_temp_cvap_near_problem)}")
    print(f"Precinct geometries near problem: {len(_temp_precincts_near_problem)}")

    if len(_temp_cvap_near_problem) > 0:
        print("\nCVAP geometries near problem:")
        _temp_invalid_cols = (
            ["geoid"] if "geoid" in _temp_cvap_near_problem.columns else []
        )
        print(_temp_cvap_near_problem[_temp_invalid_cols])

    if len(_temp_precincts_near_problem) > 0:
        print("\nPrecinct geometries near problem:")
        print(_temp_precincts_near_problem[["county", "precinct_id"]])
    return cvap_gdf_ai_validated, precincts_gdf_ai_validated


@app.cell
def _(
    MERGE_KEYS,
    cvap_gdf_ai_validated,
    join_pct_columns,
    precincts_gdf_ai_validated,
    tobler,
    tracts_extensive_variables_to_interpolate,
    tracts_subgroup_est_columns,
):
    # Use the validated and reprojected geometries
    _temp_target_gdf = precincts_gdf_ai_validated.set_index(MERGE_KEYS)

    cvap_precinct_estimates_ai = tobler.area_weighted.area_interpolate(
        cvap_gdf_ai_validated,
        _temp_target_gdf,
        extensive_variables=tracts_extensive_variables_to_interpolate,
    )
    cvap_precinct_estimates_ai = cvap_precinct_estimates_ai[
        tracts_extensive_variables_to_interpolate
    ].apply(round)

    cvap_precinct_estimates_ai["_interpolated_total_est"] = (
        cvap_precinct_estimates_ai[tracts_subgroup_est_columns].sum(axis=1)
    )

    cvap_precinct_estimates_ai = join_pct_columns(
        df=cvap_precinct_estimates_ai,
        numerator_columns=tracts_subgroup_est_columns,
        denominator_column="_interpolated_total_est",
    )
    return


@app.cell
def _(
    CVAP_COLUMN_KEYWORD,
    MERGE_KEYS,
    PROJECTED_CRS,
    cvap_block_gdf,
    join_pct_columns,
    precincts_gdf_ai_validated,
    tobler,
):
    # Validate and reproject block geometries
    _temp_cvap_block_invalid = ~cvap_block_gdf.geometry.is_valid
    if _temp_cvap_block_invalid.any():
        print(
            f"Making {_temp_cvap_block_invalid.sum()} invalid block geometries valid..."
        )
        cvap_block_gdf.loc[_temp_cvap_block_invalid, "geometry"] = (
            cvap_block_gdf.loc[_temp_cvap_block_invalid, "geometry"].buffer(0)
        )

    _temp_cvap_block_gdf_proj = cvap_block_gdf.to_crs(PROJECTED_CRS)

    _temp_block_extensive_vars = [
        column
        for column in list(_temp_cvap_block_gdf_proj)
        if CVAP_COLUMN_KEYWORD in column.upper()
    ]
    _temp_block_subgroup_est_columns = [
        column for column in _temp_block_extensive_vars if "TOT" not in column
    ]

    # Use the validated and reprojected geometries
    _temp_target_gdf = precincts_gdf_ai_validated.set_index(MERGE_KEYS)

    cvap_block_precinct_estimates_ai = tobler.area_weighted.area_interpolate(
        _temp_cvap_block_gdf_proj,
        _temp_target_gdf,
        extensive_variables=_temp_block_extensive_vars,
    )

    cvap_block_precinct_estimates_ai = cvap_block_precinct_estimates_ai[
        _temp_block_extensive_vars
    ].apply(round)
    cvap_block_precinct_estimates_ai["_interpolated_total_est"] = (
        cvap_block_precinct_estimates_ai[_temp_block_subgroup_est_columns].sum(
            axis=1
        )
    )
    cvap_block_precinct_estimates_ai = join_pct_columns(
        cvap_block_precinct_estimates_ai,
        _temp_block_extensive_vars,
        "_interpolated_total_est",
    )
    return (cvap_block_precinct_estimates_ai,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Merge using the validated geometries
    """)
    return


@app.cell
def _(
    MERGE_KEYS,
    audited_precinct_results_gdf,
    cvap_block_precinct_estimates_ai,
):
    # Merge using the validated geometries
    precincts_results_cvap_block_merged_ai = audited_precinct_results_gdf.merge(
        cvap_block_precinct_estimates_ai,
        left_on=MERGE_KEYS,
        right_index=True,
        validate="1:1",
    )
    precincts_results_cvap_block_merged_ai.plot()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calculate proportion of CVAP population in interpolation
    """)
    return


@app.cell
def _(
    block_subgroup_est_columns,
    cvap_block_gdf,
    cvap_gdf,
    precincts_results_cvap_block_merged,
    precincts_results_cvap_merged,
    tracts_subgroup_est_columns,
):
    def _calculate_and_print_ratio(state_gdf, merged_gdf, columns, level_name):
        """
        Calculate and print the proportion of total CVAP interpolated to precincts.

        Parameters
        ----------
        state_gdf : gpd.GeoDataFrame
            Original state-level GeoDataFrame with source totals
        merged_gdf : gpd.GeoDataFrame
            Merged GeoDataFrame with interpolated precinct data
        columns : list[str]
            List of subgroup columns to aggregate
        level_name : str
            Description of the geographic level (e.g., "tract level", "block level")
        """
        state_total = state_gdf[columns].sum().sum()
        interpolated_total = merged_gdf[columns].sum().sum()

        ratio = interpolated_total / state_total

        print(
            f"Proportion of total CVAP interpolated to precincts ({level_name}): {ratio:.1%}"
        )


    _calculate_and_print_ratio(
        cvap_gdf,
        precincts_results_cvap_merged,
        tracts_subgroup_est_columns,
        "tract level",
    )

    _calculate_and_print_ratio(
        cvap_block_gdf,
        precincts_results_cvap_block_merged,
        block_subgroup_est_columns,
        "block level",
    )
    return


@app.cell
def _(
    block_subgroup_est_columns,
    cvap_block_gdf,
    cvap_gdf,
    pd,
    precincts_results_cvap_block_merged,
    precincts_results_cvap_merged,
    tracts_subgroup_est_columns,
):
    def _create_interpolation_summary(state_gdf, merged_gdf, subgroup_columns):
        """
        Calculate summary statistics comparing state totals vs interpolated totals.

        Parameters
        ----------
        state_gdf : GeoDataFrame
            Original state-level GeoDataFrame with source data
        merged_gdf : GeoDataFrame
            Merged GeoDataFrame with interpolated data
        subgroup_columns : list
            List of column names to aggregate

        Returns
        -------
        DataFrame
            Summary with state_total, interpolated_total, and interpolated_pct
        """
        state_sums = state_gdf[subgroup_columns].sum()
        interpolated_sums = merged_gdf[subgroup_columns].sum()

        summary_df = pd.DataFrame(
            {
                "state_total": state_sums,
                "interpolated_total": interpolated_sums,
            }
        )
        summary_df["interpolated_pct"] = round(
            (summary_df["interpolated_total"] / summary_df["state_total"]) * 100, 1
        )
        summary_df.index.name = "subgroup"

        return summary_df


    # Calculate totals for each subgroup column at the tract level
    _tract_summary_df = _create_interpolation_summary(
        cvap_gdf,
        precincts_results_cvap_merged,
        tracts_subgroup_est_columns,
    )

    # Calculate totals for each subgroup column at the block level
    _block_summary_df = _create_interpolation_summary(
        cvap_block_gdf,
        precincts_results_cvap_block_merged,
        block_subgroup_est_columns,
    )

    _tract_summary_df, _block_summary_df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
