import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Prop. 50 Election
    """)
    return


@app.cell
def _():
    import time
    from datetime import datetime
    from pathlib import Path

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import requests

    return Path, datetime, gpd, mo, pd, requests, time


@app.cell
def _(Path):
    COUNTIES_FP = Path("./inputs/census/tl_2020_us_county.zip")
    ELECTION_DATA_DIR = Path("./inputs/statewide_db/S25")
    CA_FIPS = "06"
    return CA_FIPS, COUNTIES_FP, ELECTION_DATA_DIR


@app.cell
def _():
    PROJECTED_CRS = (
        "EPSG:3310"  # NAD83 / California Albers (good for area calculations in CA)
    )
    return (PROJECTED_CRS,)


@app.cell
def _():
    USER_AGENT = {"User-Agent": "Mozilla/5.0"}
    return (USER_AGENT,)


@app.cell
def _():
    INDEX_COLUMNS = ["county", "srprec"]
    return (INDEX_COLUMNS,)


@app.cell
def _():
    COUNTY_AGG_RESULTS_ID = "CNTYTOT"
    return (COUNTY_AGG_RESULTS_ID,)


@app.cell
def _():
    COLUMNS_DICT = {
        "county": "county",  # The county containing the precinct
        "srprec": "precinct_id",  # Unique ID for the precinct
        "PR_50_Y": "yes_votes",  # the number of votes for "Yes" on Prop. 50 in the precinct
        "PR_50_N": "no_votes",  # the number of votes for "No" on Prop. 50 in the precinct
        "no_pct": "no_pct",
        "yes_pct": "yes_pct",
        "TOTVOTE": "total_votes",
        "TOTREG": "registered_voters",
        "turnout": "turnout",  # the percent of the voters who cast a ballot in the precinct
        "election": "election",
        "_latino_voters": "_latino_voters",
        "_asian_voters": "_asian_voters",
        "_is_maj_latino_turnout": "_is_maj_latino_turnout",
        "_is_maj_asian_turnout": "_is_maj_asian_turnout",
        "geometry": "geometry",
    }
    return (COLUMNS_DICT,)


@app.cell
def _(INDEX_COLUMNS):
    ASIAN_VOTER_COLUMNS = [
        "kordem",
        "korrep",
        "kordcl",
        "koroth",
        "jpndem",
        "jpnrep",
        "jpndcl",
        "jpnoth",
        "chidem",
        "chirep",
        "chidcl",
        "chioth",
        "inddem",
        "indrep",
        "inddcl",
        "indoth",
        "vietdem",
        "vietrep",
        "vietdcl",
        "vietoth",
        "fildem",
        "filrep",
        "fildcl",
        "filoth",
    ]

    LATINO_VOTER_COLUMNS = [
        "hispdem",
        "hisprep",
        "hispdcl",
        "hispoth",
    ]

    VOTERS_COLUMNS = [
        *INDEX_COLUMNS,
        "election",
        "type",
        "totreg_r",
        *LATINO_VOTER_COLUMNS,
        *ASIAN_VOTER_COLUMNS,
    ]
    return ASIAN_VOTER_COLUMNS, LATINO_VOTER_COLUMNS, VOTERS_COLUMNS


@app.cell
def _(INDEX_COLUMNS):
    RESULTS_COLUMNS = [
        *INDEX_COLUMNS,
        "TOTREG",
        "TOTVOTE",
        "PR_50_N",
        "PR_50_Y",
    ]
    return (RESULTS_COLUMNS,)


@app.cell
def _():
    DUPE_CHECK_COLUMNS = [
        "county",
        "precinct_id",
        "yes_votes",
        "no_votes",
        "total_votes",
    ]
    return (DUPE_CHECK_COLUMNS,)


@app.cell
def _(mo):
    MAJORITY_THRESHOLD_SLIDER = mo.ui.slider(
        start=0.0,
        stop=1.0,
        step=0.001,
        value=0.500,
        debounce=False,
        show_value=True,
        label="Group categorization threshold",
        include_input=True,
    )
    return (MAJORITY_THRESHOLD_SLIDER,)


@app.cell
def _(MAJORITY_THRESHOLD_SLIDER):
    majority_threshold = MAJORITY_THRESHOLD_SLIDER.value
    return (majority_threshold,)


@app.cell
def _():
    ROBUSTNESS_MAJORITY_THRESHOLDS = (50, 60, 70, 75, 80, 85, 90)
    return (ROBUSTNESS_MAJORITY_THRESHOLDS,)


@app.cell
def _(Path, USER_AGENT, requests, time):
    # URL is consistent with the filename prefix representing county
    def get_results_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/c{county_fips}_s25_sov_data_by_s25_srprec.csv"


    def get_voters_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/c{county_fips}_s25_voters_by_s25_srprec.csv"


    def get_gis_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/srprec_{county_fips}_s25_v01.gpkg.zip"


    def snake_case(_in: str):
        return _in.replace(" ", "_").lower()


    def download_file(url: str, save_path: Path):
        response = requests.get(url, headers=USER_AGENT)
        response.raise_for_status()
        time.sleep(1)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(response.content)
        print(f"Saved {url} to {save_path}")
        return response.ok

    return (
        download_file,
        get_gis_url,
        get_results_url,
        get_voters_url,
        snake_case,
    )


@app.function
def calculate_pct(numerator, denominator, rounding_place=1):
    return round((numerator / denominator) * 100, rounding_place)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read and prepare data

    Read California county names and fips from Census to build data download urls
    """)
    return


@app.cell
def _(gpd):
    RESULTS_2024 = gpd.read_file("./outputs/precinct_results_2024.gpkg")
    return (RESULTS_2024,)


@app.cell
def _(CA_FIPS, COUNTIES_FP, gpd):
    counties_gdf = gpd.read_file(COUNTIES_FP)
    is_ca_county = counties_gdf["GEOID"].str.startswith(CA_FIPS)
    ca_counties_gdf = counties_gdf[is_ca_county].copy()
    del counties_gdf
    ca_counties_gdf = ca_counties_gdf.sort_values("NAME")
    county_name_to_fips = dict(
        zip(ca_counties_gdf["NAME"], ca_counties_gdf["COUNTYFP"])
    )
    county_fips_to_name = {
        fips: name for name, fips in county_name_to_fips.items()
    }
    del ca_counties_gdf
    return county_fips_to_name, county_name_to_fips


@app.cell
def _(county_name_to_fips, mo):
    data_scope_dropdown = mo.ui.dropdown(
        options=["county", "statewide"], value="statewide", label="## Data scope:"
    )
    county_selection_dropdown = mo.ui.dropdown(
        county_name_to_fips.keys(), value="Alameda", label="County:"
    )
    return county_selection_dropdown, data_scope_dropdown


@app.cell
def _(county_selection_dropdown, data_scope_dropdown, mo):
    dropdowns = (
        [data_scope_dropdown, county_selection_dropdown]
        if data_scope_dropdown.value == "county"
        else [data_scope_dropdown]
    )
    mo.vstack(dropdowns)
    return


@app.cell
def _(county_name_to_fips, county_selection_dropdown, data_scope_dropdown):
    selected_counties = (
        list(county_name_to_fips.items())
        if data_scope_dropdown.value == "statewide"
        else [
            (
                county_selection_dropdown.value,
                county_name_to_fips[county_selection_dropdown.value],
            )
        ]
    )
    return (selected_counties,)


@app.cell
def _(
    ELECTION_DATA_DIR,
    Path,
    get_gis_url,
    get_results_url,
    get_voters_url,
    snake_case,
):
    def build_county_meta(county: str, county_fips: str):
        results_url = get_results_url(county_fips)
        voters_url = get_voters_url(county_fips)
        gis_url = get_gis_url(county_fips)
        county_dir = ELECTION_DATA_DIR / snake_case(county)
        return {
            "results": {
                "url": results_url,
                "fp": county_dir / Path(results_url).name,
            },
            "voters": {
                "url": voters_url,
                "fp": county_dir / Path(voters_url).name,
            },
            "gis": {
                "url": gis_url,
                "fp": county_dir / Path(gis_url).name,
            },
        }

    return (build_county_meta,)


@app.cell
def _(build_county_meta, download_file, pd):
    def download_and_read_county_data(county: str, county_fips: str):
        county_meta = build_county_meta(county, county_fips)
        county_raw = {}
        for key, meta in county_meta.items():
            if not meta["fp"].exists():
                download_file(str(meta["url"]), meta["fp"])
            if key == "gis":
                county_raw[key] = meta["fp"]
                continue

            county_df = pd.read_csv(
                meta["fp"], dtype={"srprec": str, "county": str}
            )
            county_df["county"] = county
            county_raw[key] = county_df
        return county_raw

    return (download_and_read_county_data,)


@app.cell
def _(
    ASIAN_VOTER_COLUMNS,
    COUNTY_AGG_RESULTS_ID,
    LATINO_VOTER_COLUMNS,
    RESULTS_COLUMNS,
    VOTERS_COLUMNS,
    pd,
):
    def transform_voters(voters_raw_df):
        _df = voters_raw_df[VOTERS_COLUMNS].copy()
        _df["_latino_voters"] = _df[LATINO_VOTER_COLUMNS].sum(axis=1)
        _df["_asian_voters"] = _df[ASIAN_VOTER_COLUMNS].sum(axis=1)
        return _df


    def transform_results(results_raw_df):
        _df = results_raw_df[RESULTS_COLUMNS].copy()
        _df = _df[_df["srprec"] != COUNTY_AGG_RESULTS_ID].copy()
        _df["PR_50_Y"] = pd.to_numeric(_df["PR_50_Y"], errors="coerce")
        _df["PR_50_N"] = pd.to_numeric(_df["PR_50_N"], errors="coerce")
        _df["yes_pct"] = calculate_pct(_df["PR_50_Y"], _df["TOTVOTE"])
        _df["no_pct"] = calculate_pct(_df["PR_50_N"], _df["TOTVOTE"])
        return _df

    return transform_results, transform_voters


@app.cell
def _(Path, datetime):
    DEBUG_DIR = Path("debug")
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)


    def get_current_timestamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    return DEBUG_DIR, get_current_timestamp


@app.cell
def _(DEBUG_DIR, get_current_timestamp, pd):
    def audit_merged_precinct_data(
        merged_gdf, debug_dir=DEBUG_DIR, *, results_entry_column="TOTVOTE"
    ):
        """Audit an outer-merged precincts-results GeoDataFrame (same summary as 03_precincts_merge)."""

        def count_by_county(mask):
            return merged_gdf.loc[mask, "county"].value_counts()

        stamp = get_current_timestamp()
        missing_geometry = merged_gdf["geometry"].isna()
        missing_results = merged_gdf[results_entry_column].isna()
        rows_missing_gis = merged_gdf[missing_geometry]
        rows_missing_results = merged_gdf[missing_results]

        gis_entries = count_by_county(merged_gdf["geometry"].notna())
        results_entries = count_by_county(merged_gdf[results_entry_column].notna())
        missing_gis_by_county = count_by_county(missing_geometry)
        missing_results_by_county = count_by_county(missing_results)

        all_counties = sorted(list(merged_gdf["county"].unique()))
        audit_summary = {
            county: {
                "gis_entries": gis_entries.get(county, 0),
                "results_entries": results_entries.get(county, 0),
                "missing_in_gis": missing_gis_by_county.get(county, 0),
                "missing_in_results": missing_results_by_county.get(county, 0),
            }
            for county in all_counties
        }

        audit_df = pd.DataFrame.from_dict(audit_summary, orient="index")
        for rows, name in (
            (rows_missing_gis, "missing_in_gis"),
            (rows_missing_results, "missing_in_results"),
        ):
            if not rows.empty:
                rows.to_csv(debug_dir / f"{name}_{stamp}.csv", index=False)

        audit_df.to_csv(debug_dir / f"audit_summary_{stamp}.csv", index=True)
        print(
            f"Audit complete. {len(rows_missing_gis)} entries missing in GIS, "
            f"{len(rows_missing_results)} missing in results. "
            f"See exported audit debug data in {debug_dir}/"
        )
        return audit_df

    return (audit_merged_precinct_data,)


@app.cell
def _(
    DEBUG_DIR,
    INDEX_COLUMNS,
    audit_merged_precinct_data,
    county_fips_to_name,
    download_and_read_county_data,
    gpd,
    pd,
    selected_counties,
    transform_results,
    transform_voters,
):
    merged_frames = []
    skipped_counties = []
    for county, county_fips in selected_counties:
        try:
            county_raw = download_and_read_county_data(county, county_fips)
            transformed_results = transform_results(county_raw["results"])
            transformed_voters = transform_voters(county_raw["voters"])
            county_merged_df = transformed_results.merge(
                transformed_voters, on=INDEX_COLUMNS, how="left", validate="1:1"
            )

            precincts_gdf = gpd.read_file(county_raw["gis"])
            precincts_gdf["county"] = precincts_gdf["COUNTY"].map(
                county_fips_to_name
            )
            precincts_gdf = precincts_gdf.merge(
                county_merged_df, on=INDEX_COLUMNS, how="outer", validate="1:1"
            )

            merged_frames.append(precincts_gdf)

        except Exception as error:
            skipped_counties.append(
                {"county": county, "county_fips": county_fips, "error": str(error)}
            )

    if merged_frames:
        combined_for_audit = pd.concat(merged_frames, ignore_index=True)
        combined_for_audit = combined_for_audit[
            combined_for_audit["county"].notnull()
        ]
        audit_summary_df = audit_merged_precinct_data(
            combined_for_audit, DEBUG_DIR
        )
    return merged_frames, skipped_counties


@app.cell
def _(
    COLUMNS_DICT,
    INDEX_COLUMNS,
    PROJECTED_CRS,
    RESULTS_COLUMNS,
    VOTERS_COLUMNS,
    merged_frames,
    pd,
):
    expected_columns = list(
        dict.fromkeys(
            RESULTS_COLUMNS
            + ["yes_pct", "no_pct"]
            + VOTERS_COLUMNS[len(INDEX_COLUMNS) :]
            + ["_latino_voters", "_is_maj_latino"]
        )
    )
    merged_df = (
        pd.concat(merged_frames, ignore_index=True)
        if merged_frames
        else pd.DataFrame(columns=expected_columns)
    )
    merged_df = merged_df.rename(columns=COLUMNS_DICT)
    merged_df["turnout"] = calculate_pct(
        merged_df["total_votes"], merged_df["registered_voters"]
    )
    merged_df = merged_df[
        [col for col in COLUMNS_DICT.values() if col in list(merged_df)]
    ].copy()
    merged_df = merged_df[merged_df["county"].notnull()]
    merged_df = merged_df.to_crs(PROJECTED_CRS)
    return (merged_df,)


@app.function
def turnout_majority_group_metrics(
    prop50_merged_gdf,
    presidential_2024_gdf,
    group_key,
    threshold_fraction,
    counties_in_scope,
):
    group_voter_count_column = (
        "_latino_voters" if group_key == "latino" else "_asian_voters"
    )
    presidential_2024_in_scope = presidential_2024_gdf[
        presidential_2024_gdf["county"].isin(counties_in_scope)
    ]

    is_majority_on_prop50_frame = (
        prop50_merged_gdf[group_voter_count_column]
        / prop50_merged_gdf["total_votes"]
    ) > threshold_fraction
    is_majority_on_prop50_frame = is_majority_on_prop50_frame.fillna(False)
    prop50_majority_precincts = prop50_merged_gdf.loc[
        is_majority_on_prop50_frame
    ]

    is_majority_on_presidential_2024_frame = (
        presidential_2024_in_scope[group_voter_count_column]
        / presidential_2024_in_scope["total_votes"]
    ) > threshold_fraction
    is_majority_on_presidential_2024_frame = (
        is_majority_on_presidential_2024_frame.fillna(False)
    )
    presidential_2024_majority_precincts = presidential_2024_in_scope.loc[
        is_majority_on_presidential_2024_frame
    ]

    precinct_count_prop50 = len(prop50_majority_precincts)
    precinct_count_presidential_2024 = len(
        presidential_2024_majority_precincts
    )
    total_votes_prop50 = prop50_majority_precincts["total_votes"].sum()
    total_votes_presidential_2024 = presidential_2024_majority_precincts[
        "total_votes"
    ].sum()
    if (
        precinct_count_prop50 == 0
        or precinct_count_presidential_2024 == 0
        or total_votes_prop50 == 0
        or total_votes_presidential_2024 == 0
    ):
        return (
            None,
            precinct_count_prop50,
            precinct_count_presidential_2024,
            None,
            None,
        )

    prop50_yes_pct = calculate_pct(
        prop50_majority_precincts["yes_votes"].sum(), total_votes_prop50
    )
    prop50_no_pct = calculate_pct(
        prop50_majority_precincts["no_votes"].sum(), total_votes_prop50
    )
    presidential_2024_dem_pct = calculate_pct(
        presidential_2024_majority_precincts["dem_votes"].sum(),
        total_votes_presidential_2024,
    )
    presidential_2024_rep_pct = calculate_pct(
        presidential_2024_majority_precincts["rep_votes"].sum(),
        total_votes_presidential_2024,
    )
    prop50_yes_minus_no_margin_pct = round(prop50_yes_pct - prop50_no_pct, 1)
    presidential_2024_dem_minus_rep_margin_pct = round(
        presidential_2024_dem_pct - presidential_2024_rep_pct, 1
    )
    net_democratic_shift = round(
        (prop50_yes_pct - prop50_no_pct)
        - (presidential_2024_dem_pct - presidential_2024_rep_pct),
        1,
    )
    return (
        net_democratic_shift,
        precinct_count_prop50,
        precinct_count_presidential_2024,
        prop50_yes_minus_no_margin_pct,
        presidential_2024_dem_minus_rep_margin_pct,
    )


@app.cell
def _(RESULTS_2024, ROBUSTNESS_MAJORITY_THRESHOLDS, merged_df, pd):
    counties_present_in_prop50_merge = merged_df["county"].unique()
    turnout_group_specs = (
        ("Latino majority (turnout)", "latino"),
        ("Asian majority (turnout)", "asian"),
    )
    vote_shift_table_rows = []
    prop50_yes_minus_no_table_rows = []
    presidential_2024_dem_minus_rep_table_rows = []
    precinct_count_prop50_table_rows = []
    precinct_count_presidential_2024_table_rows = []
    for group_display_label, group_key in turnout_group_specs:
        vote_shift_row = {"group": group_display_label}
        prop50_yes_minus_no_row = {"group": group_display_label}
        presidential_2024_dem_minus_rep_row = {"group": group_display_label}
        precinct_count_prop50_row = {"group": group_display_label}
        precinct_count_presidential_2024_row = {"group": group_display_label}
        for majority_threshold_percent in ROBUSTNESS_MAJORITY_THRESHOLDS:
            threshold_column_label = f"{majority_threshold_percent}%"
            threshold_as_fraction = majority_threshold_percent / 100.0
            (
                net_shift_at_threshold,
                precinct_count_prop50,
                precinct_count_presidential_2024,
                prop50_yes_minus_no_at_threshold,
                presidential_2024_dem_minus_rep_at_threshold,
            ) = turnout_majority_group_metrics(
                merged_df,
                RESULTS_2024,
                group_key,
                threshold_as_fraction,
                counties_present_in_prop50_merge,
            )
            vote_shift_row[threshold_column_label] = net_shift_at_threshold
            prop50_yes_minus_no_row[threshold_column_label] = (
                prop50_yes_minus_no_at_threshold
            )
            presidential_2024_dem_minus_rep_row[threshold_column_label] = (
                presidential_2024_dem_minus_rep_at_threshold
            )
            precinct_count_prop50_row[threshold_column_label] = (
                precinct_count_prop50
            )
            precinct_count_presidential_2024_row[threshold_column_label] = (
                precinct_count_presidential_2024
            )
        vote_shift_table_rows.append(vote_shift_row)
        prop50_yes_minus_no_table_rows.append(prop50_yes_minus_no_row)
        presidential_2024_dem_minus_rep_table_rows.append(
            presidential_2024_dem_minus_rep_row
        )
        precinct_count_prop50_table_rows.append(precinct_count_prop50_row)
        precinct_count_presidential_2024_table_rows.append(
            precinct_count_presidential_2024_row
        )
    turnout_robustness_shift_table = pd.DataFrame(vote_shift_table_rows)
    turnout_robustness_prop50_yes_minus_no_table = pd.DataFrame(
        prop50_yes_minus_no_table_rows
    )
    turnout_robustness_presidential_2024_dem_minus_rep_table = pd.DataFrame(
        presidential_2024_dem_minus_rep_table_rows
    )
    turnout_robustness_precincts_2025_table = pd.DataFrame(
        precinct_count_prop50_table_rows
    )
    turnout_robustness_precincts_2024_table = pd.DataFrame(
        precinct_count_presidential_2024_table_rows
    )
    return (
        turnout_robustness_precincts_2024_table,
        turnout_robustness_precincts_2025_table,
        turnout_robustness_presidential_2024_dem_minus_rep_table,
        turnout_robustness_prop50_yes_minus_no_table,
        turnout_robustness_shift_table,
    )


@app.cell
def _(merged_df):
    merged_df[merged_df["county"].isna()].to_file("test.geojson")
    return


@app.cell
def _(RESULTS_2024, majority_threshold, merged_df):
    def categorize_turnout_group(
        df_results, categorize_threshold=majority_threshold
    ):
        _df = df_results.copy()
        _df["_is_maj_latino_turnout"] = (
            _df["_latino_voters"] / _df["total_votes"]
        ) > categorize_threshold
        _df["_is_maj_asian_turnout"] = (
            _df["_asian_voters"] / _df["total_votes"]
        ) > categorize_threshold
        _df["_is_maj_latino_turnout"] = _df["_is_maj_latino_turnout"].fillna(False)
        _df["_is_maj_asian_turnout"] = _df["_is_maj_asian_turnout"].fillna(False)
        return _df


    results_2024 = categorize_turnout_group(RESULTS_2024)
    results_2025 = categorize_turnout_group(merged_df)
    return results_2024, results_2025


@app.cell
def _(merged_df, mo, selected_counties, skipped_counties):
    total_counties = len(selected_counties)
    processed_counties = total_counties - len(skipped_counties)
    status_lines = [
        f"Processed counties: {processed_counties}/{total_counties}",
        f"Merged precinct rows: {len(merged_df):,}",
    ]
    if skipped_counties:
        skipped_names = ", ".join([item["county"] for item in skipped_counties])
        status_lines.append(f"Skipped counties: {skipped_names}")
    mo.md("<br>".join(status_lines))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Calculate net shift
    """)
    return


@app.cell
def _(MAJORITY_THRESHOLD_SLIDER):
    MAJORITY_THRESHOLD_SLIDER
    return


@app.cell
def _():
    LA_COUNTY = "Los Angeles"
    return (LA_COUNTY,)


@app.cell
def _(LA_COUNTY, merged_df, results_2025):
    maj_latino_turnout = merged_df[
        results_2025["_is_maj_latino_turnout"].notnull()
        & results_2025["_is_maj_latino_turnout"]
        & (results_2025["county"] == LA_COUNTY)
    ]
    latino_precincts_2025 = len(maj_latino_turnout)
    yes_pct = calculate_pct(
        maj_latino_turnout["yes_votes"].sum(),
        maj_latino_turnout["total_votes"].sum(),
    )
    no_pct = calculate_pct(
        maj_latino_turnout["no_votes"].sum(),
        maj_latino_turnout["total_votes"].sum(),
    )
    return latino_precincts_2025, no_pct, yes_pct


@app.cell
def _(LA_COUNTY, merged_df, results_2024):
    _maj_latino_results_2024 = results_2024[
        results_2024["_is_maj_latino_turnout"].notnull()
        & results_2024["_is_maj_latino_turnout"]
        & (results_2024["county"].isin(merged_df["county"].unique()))
        & (results_2024["county"] == LA_COUNTY)
    ]
    latino_precincts_2024 = len(_maj_latino_results_2024)
    dem_pct = calculate_pct(
        _maj_latino_results_2024["dem_votes"].sum(),
        _maj_latino_results_2024["total_votes"].sum(),
    )
    rep_pct = calculate_pct(
        _maj_latino_results_2024["rep_votes"].sum(),
        _maj_latino_results_2024["total_votes"].sum(),
    )
    return dem_pct, latino_precincts_2024, rep_pct


@app.cell
def _(
    dem_pct,
    latino_precincts_2024,
    latino_precincts_2025,
    mo,
    no_pct,
    rep_pct,
    yes_pct,
):
    net_shift = round((yes_pct - no_pct) - (dem_pct - rep_pct), 1)
    mo.md(
        f"NET DEMOCRACTIC SHIFT: {net_shift:+} ({latino_precincts_2024:,} in 2024, {latino_precincts_2025:,} in 2025)"
    )
    return


@app.cell
def _(
    mo,
    turnout_robustness_precincts_2024_table,
    turnout_robustness_precincts_2025_table,
    turnout_robustness_presidential_2024_dem_minus_rep_table,
    turnout_robustness_prop50_yes_minus_no_table,
    turnout_robustness_shift_table,
):
    mo.vstack(
        [
            mo.md(
                r"""
    **Robustness: fixed categorization cutoffs (50%–90%)**

    Each column applies the same turnout-majority rule **separately** to the 2025 Prop 50 merge and to the 2024 presidential file, then compares two **state-level** margins. The qualifying precinct *sets* (and their vote weights) are not paired row-by-row, so net shift can move non-monotonically across cutoffs—especially for small groups (e.g. Asian at high thresholds) where either aggregate can swing when a few precincts enter or leave the filter.

    The **slider** still drives the `NET DEMOCRACTIC SHIFT` line above; these tables do not. Set the slider to one of these cutoffs (e.g. 50%) to compare that column to the line for Latino.
    """
            ),
            mo.md(
                "**Net democratic shift** (Prop 50 yes−no margin minus 2024 Dem−Rep margin)"
            ),
            turnout_robustness_shift_table,
            mo.md(
                "**Margins that compose net shift** (same cutoff on each side; each value is aggregated only over precincts that pass that cutoff in *that* file)"
            ),
            mo.md("*Prop 50 (2025 merge): yes % − no %*"),
            turnout_robustness_prop50_yes_minus_no_table,
            mo.md("*Presidential 2024: Dem % − Rep %*"),
            turnout_robustness_presidential_2024_dem_minus_rep_table,
            mo.md("**Precinct counts (Prop 50 / 2025 merge)**"),
            turnout_robustness_precincts_2025_table,
            mo.md(
                "**Precinct counts (Presidential 2024, counties present in 2025 merge)**"
            ),
            turnout_robustness_precincts_2024_table,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Merge and export

    - Merge counties that statewide db doesn't have but we do and export
    """)
    return


@app.cell
def _(export_gdf):
    export_gdf["county"].nunique()
    return


@app.cell
def _(DUPE_CHECK_COLUMNS, gpd, merged_df, pd):
    results_gdf = gpd.read_file("./outputs/precinct_results.gpkg")
    missing_county_names = set(results_gdf["county"]) - set(merged_df["county"])
    print(
        f"Counties in results_gdf but not in merged_df: {sorted(missing_county_names)}"
    )
    missing_county_results_gdf = results_gdf[
        results_gdf["county"].isin(missing_county_names)
    ]
    missing_county_results_gdf = missing_county_results_gdf.drop_duplicates(
        subset=DUPE_CHECK_COLUMNS
    )


    export_gdf = pd.concat(
        [merged_df, missing_county_results_gdf], ignore_index=True
    )
    export_gdf.to_file("./outputs/precinct_results_latest.gpkg", driver="GPKG")
    return (export_gdf,)


@app.cell
def _(export_gdf):
    TOTAL_VOTES_CAST = 11_584_393
    TOTAL_YES_VOTES = 7_453_339
    TOTAL_NO_VOTES = 4_116_998
    total_votes_observed = export_gdf["total_votes"].sum()
    total_votes_observed / TOTAL_VOTES_CAST
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
