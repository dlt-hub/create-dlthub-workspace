import marimo

__generated_with = "0.19.2"
app = marimo.App(width="full")

with app.setup:
    import dlt
    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
        # Transform Brewery Data

        This example starts from public brewery records and creates a cleaner,
        analytics-friendly view of the data.
        """
    )
    return


@app.cell
def _():
    from starter_pipeline import brewery_rest_api_source

    pipeline = dlt.pipeline(
        pipeline_name="starter_pipeline",
        destination="warehouse",
        dataset_name="brewery_data",
    )
    load_info = pipeline.run(brewery_rest_api_source())
    load_info
    return (pipeline,)


@app.cell
def _(pipeline):
    dataset = pipeline.dataset()
    dataset.tables
    return (dataset,)


@app.cell
def _(dataset):
    breweries = dataset.breweries.df()
    breweries.head(10)
    return (breweries,)


@app.cell
def _(breweries):
    clean_breweries = breweries[
        [
            "id",
            "name",
            "brewery_type",
            "city",
            "state_province",
            "country",
            "latitude",
            "longitude",
            "website_url",
        ]
    ].copy()
    clean_breweries["has_coordinates"] = (
        clean_breweries["latitude"].notna() & clean_breweries["longitude"].notna()
    )
    clean_breweries.head(10)
    return (clean_breweries,)


@app.cell
def _(clean_breweries):
    summary_by_type = (
        clean_breweries.groupby("brewery_type", dropna=False)
        .agg(
            breweries=("id", "count"),
            with_coordinates=("has_coordinates", "sum"),
        )
        .reset_index()
        .sort_values("breweries", ascending=False)
    )
    summary_by_type
    return (summary_by_type,)


if __name__ == "__main__":
    app.run()
