import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


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
    USER_AGENT = {"User-Agent": "Mozilla/5.0"}
    return (USER_AGENT,)


@app.cell
def _():
    INDEX_COLUMNS = ["county", "srprec"]
    return (INDEX_COLUMNS,)


@app.cell
def _(INDEX_COLUMNS):
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
    ]
    return LATINO_VOTER_COLUMNS, VOTERS_COLUMNS


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
def _(Path, USER_AGENT, requests, time):
    # URL is consistent with the filename prefix representing county
    def get_results_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/c{county_fips}_s25_sov_data_by_s25_srprec.csv"


    def get_voters_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/c{county_fips}_s25_voters_by_s25_srprec.csv"


    def snake_case(_in: str):
        return _in.replace(" ", "_").lower()


    def download_file(url: str, save_path: Path):
        response = requests.get(url, headers=USER_AGENT)
        time.sleep(1)
        if response.ok:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(response.content)
            print(f"Saved {url} to {save_path}")
        else:
            print(f"Failed to located {url}; no file saved")
        return response.ok

    return download_file, get_results_url, get_voters_url, snake_case


@app.function
def calculate_pct(numerator, denominator, rounding_place=1):
    return round((numerator / denominator) * 100, rounding_place)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(CA_FIPS, COUNTIES_FP, gpd):
    counties_gdf = gpd.read_file(COUNTIES_FP)
    is_ca_county = counties_gdf["GEOID"].str.startswith(CA_FIPS)
    ca_counties_gdf = counties_gdf[is_ca_county].copy()
    del counties_gdf
    ca_counties_gdf = ca_counties_gdf.sort_values("NAME")
    ca_counties_dict = dict(
        zip(ca_counties_gdf["NAME"], ca_counties_gdf["COUNTYFP"])
    )
    del ca_counties_gdf
    return (ca_counties_dict,)


@app.cell
def _(ca_counties_dict, mo):
    data_scope_dropdown = mo.ui.dropdown(
        options=["county", "statewide"], value="county", label="## Data scope:"
    )
    county_selection_dropdown = mo.ui.dropdown(
        ca_counties_dict.keys(), value="Alameda", label="County:"
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
def _(ca_counties_dict, county_selection_dropdown):
    selected_county = county_selection_dropdown.value
    selected_county_fips = (
        ca_counties_dict[county_selection_dropdown.value]
        if county_selection_dropdown.value
        else ""
    )
    return selected_county, selected_county_fips


@app.cell
def _(
    ELECTION_DATA_DIR,
    Path,
    get_results_url,
    get_voters_url,
    selected_county,
    selected_county_fips,
    snake_case,
):
    data_meta_dict = {
        "results": {
            "url": get_results_url(selected_county_fips),
            "fp": (
                ELECTION_DATA_DIR
                / snake_case(selected_county)
                / Path(get_results_url(selected_county_fips)).name
            ),
        },
        "voters": {
            "url": get_voters_url(selected_county_fips),
            "fp": (
                ELECTION_DATA_DIR
                / snake_case(selected_county)
                / Path(get_voters_url(selected_county_fips)).name
            ),
        },
    }
    return (data_meta_dict,)


@app.cell
def _(data_meta_dict, download_file, pd, selected_county):
    for key, meta in data_meta_dict.items():
        if not meta["fp"].exists():
            download_file(str(meta["url"]), meta["fp"])

        if meta["fp"].exists():
            data_meta_dict[key]["raw_df"] = pd.read_csv(
                meta["fp"], dtype={"srprec": str, "county": str}
            )
            data_meta_dict[key]["raw_df"]["county"] = selected_county
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Prepare data
    """)
    return


@app.cell
def _(LATINO_VOTER_COLUMNS, VOTERS_COLUMNS, data_meta_dict):
    _df = data_meta_dict["voters"]["raw_df"][VOTERS_COLUMNS].copy()
    _df["_latino_voters"] = _df[LATINO_VOTER_COLUMNS].sum(axis=1)
    _df["_is_maj_latino"] = (_df["_latino_voters"] / _df["totreg_r"]) > 0.50
    data_meta_dict["voters"]["trans_df"] = _df
    data_meta_dict["voters"]["trans_df"]
    return


@app.cell
def _(RESULTS_COLUMNS, data_meta_dict, pd):
    _df = data_meta_dict["results"]["raw_df"][RESULTS_COLUMNS].copy()
    _df["PR_50_Y"] = pd.to_numeric(_df["PR_50_Y"], errors="coerce")
    _df["PR_50_N"] = pd.to_numeric(_df["PR_50_N"], errors="coerce")
    _df["yes_pct"] = calculate_pct(_df["PR_50_Y"], _df["TOTVOTE"])
    _df["no_pct"] = calculate_pct(_df["PR_50_N"], _df["TOTVOTE"])
    data_meta_dict["results"]["trans_df"] = _df
    data_meta_dict["results"]["trans_df"]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Merge data
    """)
    return


@app.cell
def _(INDEX_COLUMNS, data_meta_dict):
    _results = data_meta_dict["results"]["trans_df"]
    _voters = data_meta_dict["voters"]["trans_df"]
    _results.merge(_voters, on=INDEX_COLUMNS, how="left", validate="1:1")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
