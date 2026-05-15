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
        # Data Quality

        Results of the starter data quality checks over the brewery dataset.
        """
    )
    return


@app.cell
def _():
    import pandas as pd

    import dlthub.data_quality as dq
    from starter_data_quality import brewery_checks, named_brewery_checks

    pipeline = dlt.pipeline(
        pipeline_name="starter_pipeline",
        destination="warehouse",
        dataset_name="brewery_data",
    )
    suite = dq.CheckSuite(pipeline.dataset(), checks={"breweries": brewery_checks})

    results = pd.DataFrame(
        [
            {
                "check": name,
                "failures": len(suite.get_failures("breweries", name).df()),
            }
            for name, _ in named_brewery_checks
        ]
    )
    results["status"] = results["failures"].apply(
        lambda n: "pass" if n == 0 else "fail"
    )
    return (results,)


@app.cell
def _(results):
    chart = (
        alt.Chart(results, title="Failures by Check")
        .mark_bar()
        .encode(
            x=alt.X("failures:Q", title="Failures"),
            y=alt.Y("check:N", sort="-x", title="Check"),
            color=alt.Color(
                "status:N",
                scale=alt.Scale(
                    domain=["pass", "fail"], range=["#10b981", "#ef4444"]
                ),
            ),
            tooltip=["check:N", "failures:Q", "status:N"],
        )
        .properties(width=700, height=320)
    )
    chart
    return


@app.cell
def _(results):
    results
    return


if __name__ == "__main__":
    app.run()
