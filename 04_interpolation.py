import marimo

__generated_with = "0.18.4"
app = marimo.App(width="columns")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    import tobler
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constants
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filepaths
    """)
    return


@app.cell
def _():
    RESULTS_FP = "./outputs/"
    return


if __name__ == "__main__":
    app.run()
