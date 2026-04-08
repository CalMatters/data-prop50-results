import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import geopandas as gpd
    import marimo as mo
    import pandas as pd
    import requests

    return Path, gpd, mo, pd, requests


@app.cell
def _(Path):
    COUNTIES_FP = Path("./inputs/census/tl_2020_us_county.zip")
    COUNTY_ELECTION_DATA_DIR = Path("./inputs/counties/")
    CA_FIPS = "06"
    return CA_FIPS, COUNTIES_FP, COUNTY_ELECTION_DATA_DIR


@app.cell
def _():
    USER_AGENT = {"User-Agent": "Mozilla/5.0"}
    return (USER_AGENT,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read data
    """)
    return


@app.cell
def _(Path, USER_AGENT, requests):
    # URL is consistent with the filename prefix representing county
    def get_results_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/c{county_fips}_s25_sov_data_by_s25_srprec.csv"


    def get_voters_url(county_fips: str):
        return f"https://statewidedatabase.org/pub/data/S25/c{county_fips}/c{county_fips}_s25_voters_by_s25_srprec.csv"


    def snake_case(_in: str):
        return _in.replace(" ", "_").lower()


    def download_file(url: str, save_path: Path):
        response = requests.get(url, headers=USER_AGENT)
        response.raise_for_status()
        save_path.write_bytes(response.content)

    return download_file, get_results_url, get_voters_url, snake_case


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
    county_selection_dropdown = mo.ui.dropdown(
        ca_counties_dict.keys(), value="Alameda"
    )
    county_selection_dropdown
    return (county_selection_dropdown,)


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
    COUNTY_ELECTION_DATA_DIR,
    Path,
    download_file,
    get_results_url,
    get_voters_url,
    pd,
    selected_county,
    selected_county_fips,
    snake_case,
):
    data_meta_dict = {
        "results": {
            "url": get_results_url(selected_county_fips),
            "fp": (
                COUNTY_ELECTION_DATA_DIR
                / snake_case(selected_county)
                / Path(get_results_url(selected_county_fips)).name
            ),
        },
        "voters": {
            "url": get_voters_url(selected_county_fips),
            "fp": (
                COUNTY_ELECTION_DATA_DIR
                / snake_case(selected_county)
                / Path(get_voters_url(selected_county_fips)).name
            ),
        },
    }

    for key, meta in data_meta_dict.items():
        if not meta["fp"].exists():
            download_file(str(meta["url"]), meta["fp"])

        data_meta_dict[key]["raw_df"] = pd.read_csv(
            meta["fp"], dtype={"srprec": str}
        )
    return (data_meta_dict,)


@app.cell
def _(LATINO_VOTER_COLUMNS, VOTERS_COLUMNS, data_meta_dict):
    _df = data_meta_dict["voters"]["raw_df"][VOTERS_COLUMNS].copy()
    _df["_latino_voters"] = _df[LATINO_VOTER_COLUMNS].sum(axis=1)
    _df["_is_maj_latino"] = (_df["_latino_voters"] / _df["totreg_r"]) > 0.50
    data_meta_dict["voters"]["trans_df"] = _df
    data_meta_dict["voters"]["trans_df"]
    return


@app.cell
def _():
    LATINO_VOTER_COLUMNS = [
        "hispdem",
        "hisprep",
        "hispdcl",
        "hispoth",
    ]

    VOTERS_COLUMNS = [
        "srprec",
        "election",
        "type",
        "totreg_r",
        *LATINO_VOTER_COLUMNS,
    ]
    return LATINO_VOTER_COLUMNS, VOTERS_COLUMNS


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
