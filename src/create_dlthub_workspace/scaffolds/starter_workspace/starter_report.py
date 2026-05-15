import marimo

__generated_with = "0.19.2"
app = marimo.App(width="full")

with app.setup:
    import altair as alt
    import dlt
    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
        # Brewery Starter Report

        A small report over the public brewery dataset loaded by
        `starter_pipeline.py`.
        """
    )
    return


@app.cell
def _():
    pipeline = dlt.pipeline(
        pipeline_name="starter_pipeline",
        destination="warehouse",
        dataset_name="brewery_data",
    )
    breweries = pipeline.dataset().breweries.df()
    return (breweries,)


@app.cell
def _(breweries):
    total = len(breweries)
    states = breweries["state_province"].nunique()
    types = breweries["brewery_type"].nunique()

    mo.hstack(
        [
            mo.stat(value=total, label="Breweries"),
            mo.stat(value=states, label="States / Provinces"),
            mo.stat(value=types, label="Brewery Types"),
        ],
        justify="center",
    )
    return


@app.cell
def _(breweries):
    by_type = (
        breweries.groupby("brewery_type", dropna=False)
        .size()
        .reset_index(name="breweries")
        .sort_values("breweries", ascending=False)
    )
    return (by_type,)


@app.cell
def _(alt, by_type):
    chart = (
        alt.Chart(by_type, title="Breweries by Type")
        .mark_bar()
        .encode(
            x=alt.X("breweries:Q", title="Breweries"),
            y=alt.Y("brewery_type:N", sort="-x", title="Type"),
            tooltip=["brewery_type:N", "breweries:Q"],
        )
        .properties(width=700, height=320)
    )
    chart
    return


@app.cell
def _(breweries):
    top_states = (
        breweries.groupby("state_province", dropna=False)
        .size()
        .reset_index(name="breweries")
        .sort_values("breweries", ascending=False)
        .head(15)
    )
    top_states
    return


if __name__ == "__main__":
    app.run()
