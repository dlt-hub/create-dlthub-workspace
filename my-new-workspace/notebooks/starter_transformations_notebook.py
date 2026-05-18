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
        # Transformations

        Cleaned and aggregated tables built from the raw brewery data by the
        `starter_transform` pipeline.
        """
    )
    return


@app.cell
def _():
    transform_pipe = dlt.pipeline(
        pipeline_name="starter_transform",
        destination="warehouse",
        dataset_name="brewery_transforms",
    )
    dataset = transform_pipe.dataset()
    return (dataset,)


@app.cell(hide_code=True)
def _():
    mo.md(r"## Clean brewery records")
    return


@app.cell
def _(dataset):
    dataset.breweries_clean.df().head(10)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"## Breweries by state")
    return


@app.cell
def _(dataset):
    by_state = (
        dataset.breweries_by_state.df()
        .sort_values("brewery_count", ascending=False)
        .head(15)
    )
    by_state
    return (by_state,)


@app.cell
def _(by_state):
    chart = (
        alt.Chart(by_state, title="Top States by Brewery Count")
        .mark_bar()
        .encode(
            x=alt.X("brewery_count:Q", title="Breweries"),
            y=alt.Y("state_province:N", sort="-x", title="State / Province"),
            tooltip=[
                "state_province:N",
                "brewery_count:Q",
                "with_coordinates:Q",
            ],
        )
        .properties(width=700, height=400)
    )
    chart
    return


if __name__ == "__main__":
    app.run()
