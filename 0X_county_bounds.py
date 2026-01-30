import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    return (gpd,)


@app.cell
def _():
    CA_GEO_ID = "06"
    INPUT_FP = "./inputs/census/tl_2020_us_county.zip"
    OUTPUT_FP = "./outputs/county_bounds.geojson"
    OUTPUT_DRIVER = "GeoJSON"
    return CA_GEO_ID, INPUT_FP, OUTPUT_DRIVER, OUTPUT_FP


@app.cell
def _():
    COLUMNS = [
        "GEOID",
        "NAME",
        "geometry",
    ]
    return (COLUMNS,)


@app.cell
def _(CA_GEO_ID, COLUMNS, INPUT_FP, OUTPUT_DRIVER, OUTPUT_FP, gpd):
    GDF = gpd.read_file(INPUT_FP)
    is_ca_county = GDF["GEOID"].str.startswith(CA_GEO_ID)
    gdf_ca_counties = GDF[is_ca_county].copy()
    gdf_ca_counties = gdf_ca_counties[COLUMNS].copy()
    gdf_ca_counties = gdf_ca_counties.reset_index(drop=True)
    gdf_ca_counties.to_file(OUTPUT_FP, driver=OUTPUT_DRIVER)
    gdf_ca_counties
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
