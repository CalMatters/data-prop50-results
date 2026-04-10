import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Census ETL

    This notebook produces three GIS outputs from census and CVAP sources:

    1. **County bounds** – California county boundaries from the 2020 Census, reprojected to NAD83/California Albers and written to `outputs/county_bounds.geojson`.
    2. **CVAP by tract** – [Citizen Voting Age Population](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) (CVAP) by census tract: reads CVAP data, transforms to wide format, merges with tract geography, and exports to `outputs/cvap_tracts.gpkg`.
    3. **CVAP by block** – CVAP by block from the [Redistricting Hub](https://redistrictingdatahub.org/dataset/california-cvap-data-disaggregated-to-the-2020-block-level-2024/), joined to block geography and exported to `outputs/cvap_blocks.gpkg`.

    All three outputs use the same CRS: EPSG:3310 (NAD83 / California Albers).
    """)
    return


@app.cell
def _():
    import zipfile
    from pathlib import Path
    import urllib.request

    import geopandas as gpd
    import marimo as mo
    import pandas as pd

    return Path, gpd, mo, pd, urllib, zipfile


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Shared constants
    """)
    return


@app.cell
def _():
    CA_FIPS = "06"
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )
    return CA_FIPS, PROJECTED_CRS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # County bounds
    """)
    return


@app.cell
def _():
    COUNTY_BOUNDS_INPUT_FP = "./inputs/census/tl_2020_us_county.zip"
    COUNTY_BOUNDS_OUTPUT_FP = "./outputs/county_bounds.geojson"
    COUNTY_BOUNDS_OUTPUT_DRIVER = "GeoJSON"
    COUNTY_BOUNDS_COLUMNS = [
        "GEOID",
        "NAME",
        "geometry",
    ]
    return (
        COUNTY_BOUNDS_COLUMNS,
        COUNTY_BOUNDS_INPUT_FP,
        COUNTY_BOUNDS_OUTPUT_DRIVER,
        COUNTY_BOUNDS_OUTPUT_FP,
    )


@app.cell
def _(
    CA_FIPS,
    COUNTY_BOUNDS_COLUMNS,
    COUNTY_BOUNDS_INPUT_FP,
    COUNTY_BOUNDS_OUTPUT_DRIVER,
    COUNTY_BOUNDS_OUTPUT_FP,
    PROJECTED_CRS,
    gpd,
):
    _gdf_counties = gpd.read_file(COUNTY_BOUNDS_INPUT_FP)
    _is_ca = _gdf_counties["GEOID"].str.startswith(CA_FIPS)
    gdf_ca_counties = _gdf_counties.loc[_is_ca, COUNTY_BOUNDS_COLUMNS].copy()
    gdf_ca_counties = gdf_ca_counties.reset_index(drop=True)

    gdf_ca_counties.to_crs(PROJECTED_CRS).to_file(
        COUNTY_BOUNDS_OUTPUT_FP, driver=COUNTY_BOUNDS_OUTPUT_DRIVER
    )
    print(f"Exported county bounds to {COUNTY_BOUNDS_OUTPUT_FP}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CVAP by tract
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constants and filepaths
    """)
    return


@app.cell
def _():
    DROP_NH_EST = "not_hispanic_or_latino_cvap_est"
    TRACT_FIPS_LEN = 11
    BLOCK_GROUP_FIPS_LEN = 12
    EST_CVAP_SUFFIX = "_est"
    TOTAL_POP_KEYWORD = "total"

    TRACTS_GIS_FP = "./inputs/census/tl_2020_06_tract.zip"
    BLOCK_GROUPS_GIS_FP = "./inputs/census/tl_2020_06_bg.zip"
    CVAP_ZIPPED_DATA_FP = "./inputs/census/CVAP_2020-2024_ACS_csv_files.zip"
    CVAP_TRACT_DATA_FP = "Tract.csv"
    CVAP_BLOCK_GROUP_DATA_FP = "BlockGr.csv"
    CVAP_TRACT_OUTPUT_FP = "./outputs/cvap_tracts.gpkg"
    CVAP_TRACT_OUTPUT_DRIVER = "GPKG"
    return (
        BLOCK_GROUPS_GIS_FP,
        BLOCK_GROUP_FIPS_LEN,
        CVAP_BLOCK_GROUP_DATA_FP,
        CVAP_TRACT_DATA_FP,
        CVAP_TRACT_OUTPUT_DRIVER,
        CVAP_TRACT_OUTPUT_FP,
        CVAP_ZIPPED_DATA_FP,
        DROP_NH_EST,
        EST_CVAP_SUFFIX,
        TOTAL_POP_KEYWORD,
        TRACTS_GIS_FP,
        TRACT_FIPS_LEN,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Helper functions
    """)
    return


@app.cell
def _(pd, zipfile):
    def list_files_in_zip(zip_path: str) -> list:
        """Returns a list of file names inside the given zipfile."""
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            return zip_ref.namelist()


    def read_csv_from_zip(
        zip_path: str, csv_filename: str, **read_csv_kwargs
    ) -> pd.DataFrame:
        """Reads a CSV file from a zipfile and returns it as a pandas DataFrame.

        Additional keyword arguments are passed to pd.read_csv.
        """
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            with zip_ref.open(csv_filename) as file:
                return pd.read_csv(file, **read_csv_kwargs)

    return list_files_in_zip, read_csv_from_zip


@app.cell
def _(pd):
    def pivot_cvap_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform CVAP data from long to wide format, with each demographic group as a column.
        """
        df_copy = df.copy()
        df_copy["lntitle_clean"] = (
            df_copy["lntitle"].str.replace(r"[^\w\s]", "").str.strip()
        )
        df_copy["lntitle_clean"] = (
            df_copy["lntitle_clean"].str.replace(" ", "_").str.lower()
        )
        df_copy["est_col"] = df_copy["lntitle_clean"] + "_cvap_est"
        df_copy["moe_col"] = df_copy["lntitle_clean"] + "_cvap_moe"

        geoids = df_copy["geoid"].unique()
        result = pd.DataFrame({"geoid": geoids})
        est_pivot = df_copy.pivot(
            index="geoid", columns="est_col", values="cvap_est"
        )
        moe_pivot = df_copy.pivot(
            index="geoid", columns="moe_col", values="cvap_moe"
        )
        result = result.join(est_pivot, on="geoid")
        result = result.join(moe_pivot, on="geoid")

        return result


    def transform_cvap_format(df: pd.DataFrame) -> pd.DataFrame:
        """Transform CVAP data into clean, wide format."""
        required_cols = {"geoid", "lntitle", "cvap_est", "cvap_moe"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")
        return pivot_cvap_data(df)

    return (transform_cvap_format,)


@app.cell
def _(pd):
    def filter_moe_from_wide_df(df: pd.DataFrame) -> pd.DataFrame:
        """Return a copy with only the estimate columns (removes MOE columns)."""
        est_columns = [
            col
            for col in df.columns
            if col.endswith("_cvap_est") or col == "geoid"
        ]
        return df[est_columns].copy()

    return (filter_moe_from_wide_df,)


@app.cell
def _(CA_FIPS, pd):
    def is_ca_geoid(geoid_series: pd.Series) -> pd.Series:
        return geoid_series.str.startswith(CA_FIPS)


    def extract_tract_geoid(
        geoid_series: pd.Series, tract_fips_len: int
    ) -> pd.Series:
        return geoid_series.str.slice(-1 * tract_fips_len)


    def filter_california_data(
        df: pd.DataFrame, geoid_column: str = "geoid"
    ) -> pd.DataFrame:
        return df[is_ca_geoid(df[geoid_column])].copy()


    def standardize_geoid_column(
        df: pd.DataFrame,
        source_column: str = "GEOID",
        target_column: str = "geoid",
    ) -> pd.DataFrame:
        return df.rename(columns={source_column: target_column})

    return (
        extract_tract_geoid,
        filter_california_data,
        standardize_geoid_column,
    )


@app.cell
def _(CVAP_ZIPPED_DATA_FP, list_files_in_zip):
    list_files_in_zip(CVAP_ZIPPED_DATA_FP)
    return


@app.cell
def _(
    BLOCK_GROUP_FIPS_LEN,
    CVAP_BLOCK_GROUP_DATA_FP,
    CVAP_TRACT_DATA_FP,
    CVAP_ZIPPED_DATA_FP,
    DROP_NH_EST,
    TRACT_FIPS_LEN,
    extract_tract_geoid,
    filter_california_data,
    filter_moe_from_wide_df,
    read_csv_from_zip,
    transform_cvap_format,
):
    _df_cvap = read_csv_from_zip(
        CVAP_ZIPPED_DATA_FP, CVAP_TRACT_DATA_FP, encoding="latin1"
    )
    _df_cvap["geoid"] = extract_tract_geoid(_df_cvap["geoid"], TRACT_FIPS_LEN)
    df_ca_cvap_by_tract = filter_california_data(_df_cvap)
    df_ca_cvap_by_tract = transform_cvap_format(df_ca_cvap_by_tract)
    df_ca_cvap_est_by_tract = filter_moe_from_wide_df(df_ca_cvap_by_tract)
    df_ca_cvap_est_by_tract = df_ca_cvap_est_by_tract.drop(
        DROP_NH_EST, axis=1
    ).reset_index(drop=True)

    _df_cvap_bg = read_csv_from_zip(
        CVAP_ZIPPED_DATA_FP, CVAP_BLOCK_GROUP_DATA_FP, encoding="latin1"
    )
    _df_cvap_bg["geoid"] = extract_tract_geoid(
        _df_cvap_bg["geoid"], BLOCK_GROUP_FIPS_LEN
    )
    df_ca_cvap_by_block_group = filter_california_data(_df_cvap_bg)
    df_ca_cvap_by_block_group = transform_cvap_format(df_ca_cvap_by_block_group)
    df_ca_cvap_est_by_block_group = filter_moe_from_wide_df(
        df_ca_cvap_by_block_group
    )
    df_ca_cvap_est_by_block_group = df_ca_cvap_est_by_block_group.drop(
        DROP_NH_EST, axis=1
    ).reset_index(drop=True)
    return df_ca_cvap_est_by_block_group, df_ca_cvap_est_by_tract


@app.cell
def _(TRACTS_GIS_FP, filter_california_data, gpd, standardize_geoid_column):
    _gdf_tracts = gpd.read_file(TRACTS_GIS_FP)
    gdf_ca_tracts = filter_california_data(_gdf_tracts, geoid_column="GEOID")[
        ["GEOID", "geometry"]
    ].copy()
    gdf_ca_tracts = standardize_geoid_column(gdf_ca_tracts)

    gdf_ca_tracts.plot()
    return (gdf_ca_tracts,)


@app.cell
def _(
    BLOCK_GROUPS_GIS_FP,
    filter_california_data,
    gpd,
    standardize_geoid_column,
):
    _gdf_block_groups = gpd.read_file(BLOCK_GROUPS_GIS_FP)
    gdf_ca_block_groups = filter_california_data(
        _gdf_block_groups, geoid_column="GEOID"
    )[["GEOID", "geometry"]].copy()
    gdf_ca_block_groups = standardize_geoid_column(gdf_ca_block_groups)

    gdf_ca_block_groups.plot()
    return (gdf_ca_block_groups,)


@app.cell
def _(df_ca_cvap_est_by_tract, gdf_ca_tracts):
    expected_tract_num = len(gdf_ca_tracts)
    gdf_ca_cvap_tracts = gdf_ca_tracts.merge(
        df_ca_cvap_est_by_tract, validate="1:1", how="outer"
    )

    assert not gdf_ca_cvap_tracts["total_cvap_est"].isnull().any(), (
        "Unexpected null value post-merge"
    )
    assert len(gdf_ca_cvap_tracts) == expected_tract_num, (
        "Tract count changed after merge"
    )

    gdf_ca_cvap_tracts
    return (gdf_ca_cvap_tracts,)


@app.cell
def _(df_ca_cvap_est_by_block_group, gdf_ca_block_groups):
    expected_block_group_num = len(gdf_ca_block_groups)
    gdf_ca_cvap_block_groups = gdf_ca_block_groups.merge(
        df_ca_cvap_est_by_block_group, validate="1:1", how="outer"
    )

    assert not gdf_ca_cvap_block_groups["total_cvap_est"].isnull().any(), (
        "Unexpected null value post-merge"
    )
    assert len(gdf_ca_cvap_block_groups) == expected_block_group_num, (
        "Block group count changed after merge"
    )

    gdf_ca_cvap_block_groups
    return (gdf_ca_cvap_block_groups,)


@app.cell
def _(
    CVAP_TRACT_OUTPUT_DRIVER,
    CVAP_TRACT_OUTPUT_FP,
    PROJECTED_CRS,
    gdf_ca_cvap_tracts,
):
    gdf_ca_cvap_tracts.to_crs(PROJECTED_CRS).to_file(
        CVAP_TRACT_OUTPUT_FP, driver=CVAP_TRACT_OUTPUT_DRIVER
    )
    print(f"Exported CVAP data by tract to {CVAP_TRACT_OUTPUT_FP}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore tract data
    """)
    return


@app.cell
def _(EST_CVAP_SUFFIX, TOTAL_POP_KEYWORD):
    def get_subgroup_columns(df):
        return [
            column
            for column in list(df)
            if column.endswith(EST_CVAP_SUFFIX) and TOTAL_POP_KEYWORD not in column
        ]

    return (get_subgroup_columns,)


@app.function
def calculate_comparison_counts(df, agg_col, est_col):
    discrepancy_count = (df[agg_col] != df[est_col]).sum()
    exceed_count = (df[agg_col] > df[est_col]).sum()
    equal_count = (df[agg_col] == df[est_col]).sum()

    return discrepancy_count, exceed_count, equal_count


@app.function
def summarize_subgroup_total_validation(df, subgroup_columns, geography_name):
    _explore = df.copy()
    _explore["subgroup_agg_total"] = _explore[subgroup_columns].sum(axis=1)
    discrepancy_count, exceed_count, equal_count = calculate_comparison_counts(
        _explore, "subgroup_agg_total", "total_cvap_est"
    )
    total_geographies = len(_explore)

    print(
        f"Subgroup aggregated total does not match the total CVAP estimate in {discrepancy_count} out of {total_geographies} {geography_name}s."
    )
    print(
        f"Subgroup aggregated total exceeds the total CVAP estimate in {exceed_count} {geography_name}s."
    )
    print(
        f"Subgroup aggregated total is equal to the total CVAP estimate in {equal_count} {geography_name}s."
    )

    exceeding_geographies = _explore[
        _explore["subgroup_agg_total"] > _explore["total_cvap_est"]
    ]
    if not exceeding_geographies.empty:
        max_excess_idx = (
            exceeding_geographies["subgroup_agg_total"]
            - exceeding_geographies["total_cvap_est"]
        ).idxmax()
        max_excess_row = exceeding_geographies.loc[max_excess_idx]
        excess_value = (
            max_excess_row["subgroup_agg_total"]
            - max_excess_row["total_cvap_est"]
        )
        print(
            f"The largest excess is {excess_value:,} in {geography_name} {max_excess_row['geoid']}, "
            f"with subgroup aggregate total {max_excess_row['subgroup_agg_total']:,} "
            f"vs. estimated total {max_excess_row['total_cvap_est']:,}."
        )

    return


@app.cell
def _(gdf_ca_cvap_tracts, get_subgroup_columns):
    subgroup_columns = [
        column for column in get_subgroup_columns(gdf_ca_cvap_tracts)
    ]
    return (subgroup_columns,)


@app.cell
def _(gdf_ca_cvap_tracts, subgroup_columns):
    summarize_subgroup_total_validation(
        gdf_ca_cvap_tracts, subgroup_columns, "tract"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore block group data
    """)
    return


@app.cell
def _(gdf_ca_cvap_block_groups, get_subgroup_columns):
    block_group_subgroup_columns = get_subgroup_columns(gdf_ca_cvap_block_groups)
    return (block_group_subgroup_columns,)


@app.cell
def _(block_group_subgroup_columns, gdf_ca_cvap_block_groups):
    summarize_subgroup_total_validation(
        gdf_ca_cvap_block_groups, block_group_subgroup_columns, "block group"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For any analysis calculating proportions, use an aggregated total so the proportions sum to one.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CVAP by block
    """)
    return


@app.cell
def _():
    READ_DTYPE = {"GEOID20": str}
    CVAP_COLUMN_PREFIX = "CVAP"
    GIS_REQUIRED_COLUMNS = ["GEOID20", "geometry"]
    # RDH 2024 CVAP block-level estimates (ACS 2020–2024). Retain OMB-aligned categories as-is.
    COLUMNS_TO_RETAIN_AS_IS = [
        "CVAP_TOT24",  # CVAP estimate for total
        "CVAP_HSP24",  # Hispanic or Latino
        "CVAP_WHT24",  # White alone
        "CVAP_BLK24",  # Black or African American alone or in combination
        "CVAP_2OM24",  # Remainder of two or more race responses
    ]
    # Composite columns we derive to and avoid double-counting.
    NEW_COMPOSITE_COLUMNS = [
        "_cvap_api24",  # Asian and Pacific Islander: CVAP_ASN24 + CVAP_NHP24
        "_cvap_amw24",  # American Indian / Alaska Native (non-Hispanic): CVAP_AIA24 - CVAP_AIB24 to avoid double count with Black
    ]

    RDH_CVAP_DATA_FP = (
        "./inputs/rdh/ca_cvap_2024_2020_b_csv/ca_cvap_2024_2020_b.csv"
    )
    CA_CENSUS_BLOCKS_FILE_PATH = "./inputs/census/tl_2020_06_tabblock20.zip"
    CA_CENSUS_BLOCKS_URL = "https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_06_tabblock20.zip"
    CVAP_BLOCKS_OUTPUT_FP = "./outputs/cvap_blocks.gpkg"
    CVAP_BLOCKS_DRIVER = "GPKG"
    return (
        CA_CENSUS_BLOCKS_FILE_PATH,
        CA_CENSUS_BLOCKS_URL,
        COLUMNS_TO_RETAIN_AS_IS,
        CVAP_BLOCKS_DRIVER,
        CVAP_BLOCKS_OUTPUT_FP,
        CVAP_COLUMN_PREFIX,
        GIS_REQUIRED_COLUMNS,
        NEW_COMPOSITE_COLUMNS,
        RDH_CVAP_DATA_FP,
        READ_DTYPE,
    )


@app.cell
def _(CVAP_COLUMN_PREFIX, RDH_CVAP_DATA_FP, READ_DTYPE, pd):
    _rh_df = pd.read_csv(RDH_CVAP_DATA_FP, dtype=READ_DTYPE, index_col="GEOID20")
    cvap_columns = [c for c in _rh_df.columns if c.startswith(CVAP_COLUMN_PREFIX)]
    rh_cvap_df = _rh_df[cvap_columns].copy()

    rh_cvap_df
    return (rh_cvap_df,)


@app.cell
def _(
    CA_CENSUS_BLOCKS_FILE_PATH,
    CA_CENSUS_BLOCKS_URL,
    GIS_REQUIRED_COLUMNS,
    Path,
    gpd,
    urllib,
):
    census_blocks_path = Path(CA_CENSUS_BLOCKS_FILE_PATH)
    if not census_blocks_path.exists():
        urllib.request.urlretrieve(CA_CENSUS_BLOCKS_URL, census_blocks_path)

    _blocks_gdf = gpd.read_file(census_blocks_path)
    ca_block_gdf = _blocks_gdf[GIS_REQUIRED_COLUMNS].copy()

    ca_block_gdf.head()
    return (ca_block_gdf,)


@app.cell
def _(COLUMNS_TO_RETAIN_AS_IS, NEW_COMPOSITE_COLUMNS, rh_cvap_df):
    transformed_rh_cvap_df = rh_cvap_df.copy()

    # AAPI column produced by adding asian and native hawaiin, pacific islander
    transformed_rh_cvap_df["_cvap_api24"] = (
        transformed_rh_cvap_df["CVAP_ASN24"] + transformed_rh_cvap_df["CVAP_NHP24"]
    )

    # (american indian - american indian and black) to avoid double counting in the black
    # CVAP columns
    transformed_rh_cvap_df["_cvap_amw24"] = (
        transformed_rh_cvap_df["CVAP_AIA24"] - transformed_rh_cvap_df["CVAP_AIB24"]
    )

    transformed_rh_cvap_df = transformed_rh_cvap_df[
        COLUMNS_TO_RETAIN_AS_IS + NEW_COMPOSITE_COLUMNS
    ].copy()

    transformed_rh_cvap_df
    return (transformed_rh_cvap_df,)


@app.cell
def _(ca_block_gdf, transformed_rh_cvap_df):
    assert len(transformed_rh_cvap_df) == len(ca_block_gdf)
    ca_block_cvap_gdf = ca_block_gdf.merge(
        transformed_rh_cvap_df, left_on="GEOID20", right_index=True, validate="1:1"
    )
    ca_block_cvap_gdf
    return (ca_block_cvap_gdf,)


@app.cell
def _(
    CVAP_BLOCKS_DRIVER,
    CVAP_BLOCKS_OUTPUT_FP,
    PROJECTED_CRS,
    ca_block_cvap_gdf,
):
    ca_block_cvap_gdf.to_crs(PROJECTED_CRS).to_file(
        CVAP_BLOCKS_OUTPUT_FP, driver=CVAP_BLOCKS_DRIVER
    )
    print(f"Exported CVAP data by block to {CVAP_BLOCKS_OUTPUT_FP}")
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
    ## CVAP by block – data fields

    - CVAP_TOT24 CVAP Estimate for Total
    - CVAP_NHS24 CVAP Estimate for Not Hispanic or Latino
    - CVAP_AMI24 CVAP Estimate for American Indian or Alaska Native Alone
    - CVAP_ASI24 CVAP Estimate for Asian Alone
    - CVAP_BLA24 CVAP Estimate for Black or African American Alone
    - CVAP_NHP24 CVAP Estimate for Native Hawaiian or Other Pacific Islander Alone
    - CVAP_WHT24 CVAP Estimate for White Alone
    - CVAP_AIW24 CVAP Estimate for American Indian or Alaska Native and White
    - CVAP_ASW24 CVAP Estimate for Asian and White
    - CVAP_BLW24 CVAP Estimate for Black or African American and White
    - CVAP_AIB24 CVAP Estimate for American Indian or Alaska Native and Black or African American
    - CVAP_2OM24 CVAP Estimate for Remainder of Two or More Race Responses
    - CVAP_HSP24 CVAP Estimate for Hispanic or Latino
    - CVAP_AIA24 CVAP Estimate for American Indian or Alaska Native Alone or In Combination
    - CVAP_ASN24 CVAP Estimate for Asian Alone or In Combination
    - CVAP_BLK24 CVAP Estimate for Black or African American Alone or In Combination
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CVAP field corresponding PL field(s)

    - CVAP_TOT24 = P0040001
    - CVAP_NHS24 = P0040003
    - CVAP_AMI24 = P0040007
    - CVAP_ASI24 = P0040008
    - CVAP_BLA24 = P0040006
    - CVAP_NHP24 = P0040009
    - CVAP_WHT24 = P0040005
    - CVAP_AIW24 = P0040014
    - CVAP_ASW24 = P0040015
    - CVAP_BLW24 = P0040013
    - CVAP_AIB24 = P0040018
    - CVAP_2OM24 = P0040011 - P0040018 - P0040014 - P0040013 - P0040015
    - CVAP_HSP24 = P0040002
    - CVAP_AIA24 = P0040007 + P0040018 + P0040014
    - CVAP_ASN24 = P0040008 + P0040015
    - CVAP_BLK24 = P0040006 + P0040013 + P0040018
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Horizontal validation
    """)
    return


@app.cell
def _():
    BLOCK_COL_TO_BG_COLUMNS = {
        "CVAP_TOT24": ["total_cvap_est"],
        "CVAP_HSP24": ["hispanic_or_latino_cvap_est"],
        "CVAP_WHT24": ["white_alone_cvap_est"],
        "CVAP_BLK24": [
            "black_or_african_american_alone_cvap_est",
            "american_indian_or_alaska_native_and_black_or_african_american_cvap_est",
            "black_or_african_american_and_white_cvap_est",
        ],
        "CVAP_2OM24": [
            "remainder_of_two_or_more_race_responses_cvap_est",
        ],
        "_cvap_api24": [
            "asian_alone_cvap_est",
            "asian_and_white_cvap_est",
            "native_hawaiian_or_other_pacific_islander_alone_cvap_est",
        ],
        "_cvap_amw24": [
            "american_indian_or_alaska_native_alone_cvap_est",
            "american_indian_or_alaska_native_and_white_cvap_est",
        ],
    }
    return (BLOCK_COL_TO_BG_COLUMNS,)


@app.cell
def _(
    BLOCK_COL_TO_BG_COLUMNS,
    BLOCK_GROUP_FIPS_LEN,
    ca_block_cvap_gdf,
    gdf_ca_cvap_block_groups,
    mo,
    pd,
):
    _block_cols = list(BLOCK_COL_TO_BG_COLUMNS)
    _blocks = ca_block_cvap_gdf.assign(
        geoid=ca_block_cvap_gdf["GEOID20"].str[:BLOCK_GROUP_FIPS_LEN]
    )
    _from_blocks = _blocks.groupby("geoid", as_index=False)[_block_cols].sum()

    _bg = gdf_ca_cvap_block_groups[
        ["geoid"]
        + sorted({c for cols in BLOCK_COL_TO_BG_COLUMNS.values() for c in cols})
    ].copy()

    _merged = _from_blocks.merge(_bg, on="geoid", how="inner", validate="1:1")
    _n_bg = len(gdf_ca_cvap_block_groups)
    _n_merged = int(_merged.shape[0])

    _rows = []
    for _block_col, _bg_cols in BLOCK_COL_TO_BG_COLUMNS.items():
        _agg_from_bg = _merged[_bg_cols].sum(axis=1)
        _diff = _merged[_block_col] - _agg_from_bg
        _n_mismatch = int((_diff != 0).sum())
        _max_abs = int(_diff.abs().max())
        _worst = (
            str(_merged.loc[_diff.abs().idxmax(), "geoid"]) if _n_mismatch else "—"
        )
        _expected_sum = int(_agg_from_bg.sum())
        _observed_sum = int(_merged[_block_col].sum())
        _rows.append(
            {
                "block_column": _block_col,
                "bg_columns": ", ".join(_bg_cols),
                "expected_sum": _expected_sum,
                "observed_sum": _observed_sum,
                "sum_diff": _observed_sum - _expected_sum,
                "mismatched_bg_count": _n_mismatch,
                "max_abs_diff": _max_abs,
                "worst_geoid": _worst,
            }
        )

    horizontal_validation_summary_df = pd.DataFrame(_rows)


    header = f"Block→block-group validation: {_n_merged:,} block groups overlap on geoid<br>(CVAP BG table has {_n_bg:,} California block groups)."
    if _n_merged != _n_bg:
        header += "<br>Note: merged row count ≠ CVAP BG row count (tabblock coverage / GEOID12)."

    mo.vstack([header, horizontal_validation_summary_df])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
