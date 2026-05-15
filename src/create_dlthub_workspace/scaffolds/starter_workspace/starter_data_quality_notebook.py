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
        # Data Quality for Brewery Data

        This example validates required brewery fields and checks that brewery
        types are within the expected values from Open Brewery DB.
        """
    )
    return


@app.cell
def _():
    import dlthub.data_quality as dq
    from starter_data_quality import brewery_checks, named_brewery_checks
    from starter_pipeline import brewery_rest_api_source

    return brewery_checks, brewery_rest_api_source, dq, named_brewery_checks


@app.cell
def _(brewery_rest_api_source):
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
    pipeline.dataset().breweries.head(10).df()
    return


@app.cell
def _(brewery_checks, dq, named_brewery_checks, pipeline):
    suite = dq.CheckSuite(
        pipeline.dataset(),
        checks={"breweries": brewery_checks},
    )

    results = []
    for check_name, _check in named_brewery_checks:
        failures = suite.get_failures("breweries", check_name).df()
        results.append(
            {
                "check": check_name,
                "failures": len(failures),
                "status": "pass" if len(failures) == 0 else "fail",
            }
        )
    results
    return


if __name__ == "__main__":
    app.run()
