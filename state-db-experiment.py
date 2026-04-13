import marimo

__generated_with = "0.23.0"
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
    from pathlib import Path

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import requests

    return Path, gpd, mo, pd, requests, time


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
def _(
    INDEX_COLUMNS,
    county_fips_to_name,
    download_and_read_county_data,
    gpd,
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
            if len(county_merged_df) != len(precincts_gdf):
                print(
                    f"Row count mismatch for county '{county}': merged frame has {len(county_merged_df)} rows, GIS frame has {len(precincts_gdf)} rows."
                )

            precincts_gdf = precincts_gdf.merge(
                county_merged_df, on=INDEX_COLUMNS, how="outer", validate="1:1"
            )
            merged_frames.append(precincts_gdf)
        except Exception as error:
            skipped_counties.append(
                {"county": county, "county_fips": county_fips, "error": str(error)}
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
    merged_df = merged_df.to_crs(PROJECTED_CRS)
    merged_df
    return (merged_df,)


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
def _(merged_df, results_2025):
    maj_latino_turnout = merged_df[
        results_2025["_is_maj_latino_turnout"].notnull()
        & results_2025["_is_maj_latino_turnout"]
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
def _(merged_df, results_2024):
    _maj_latino_results_2024 = results_2024[
        results_2024["_is_maj_latino_turnout"].notnull()
        & results_2024["_is_maj_latino_turnout"]
        & (results_2024["county"].isin(merged_df["county"].unique()))
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Merge and export

    - Merge counties that statewide db doesn't have but we do and export
    """)
    return


@app.cell
def _(gpd, merged_df, pd):
    results_gdf = gpd.read_file("./outputs/precinct_results.gpkg")
    missing_county_names = set(results_gdf["county"]) - set(merged_df["county"])
    print(
        f"Counties in results_gdf but not in merged_df: {sorted(missing_county_names)}"
    )
    missing_county_results_gdf = results_gdf[
        results_gdf["county"].isin(missing_county_names)
    ]
    export_gdf = pd.concat(
        [merged_df, missing_county_results_gdf], ignore_index=True
    )
    # export_gdf.to_file("./outputs/precinct_results_latest.gpkg", driver="GPKG")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
