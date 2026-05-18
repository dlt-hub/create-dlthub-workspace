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
        # Pipeline Runs

        Recent loads of the brewery pipeline into the local warehouse.
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
    loads = pipeline.dataset()._dlt_loads.df().sort_values("inserted_at", ascending=False)
    return (loads,)


@app.cell
def _(loads):
    successful = int((loads["status"] == 0).sum())
    mo.hstack(
        [
            mo.stat(value=len(loads), label="Total Loads"),
            mo.stat(value=successful, label="Successful"),
            mo.stat(
                value=str(loads["inserted_at"].max()) if len(loads) else "—",
                label="Latest Load",
            ),
        ],
        justify="center",
    )
    return


@app.cell
def _(loads):
    chart_data = loads.assign(success=lambda d: d["status"] == 0)
    chart = (
        alt.Chart(chart_data, title="Loads Over Time")
        .mark_circle(size=120)
        .encode(
            x=alt.X("inserted_at:T", title="Inserted At"),
            y=alt.Y("schema_name:N", title="Schema"),
            color=alt.Color(
                "success:N",
                scale=alt.Scale(domain=[True, False], range=["#10b981", "#ef4444"]),
                title="Successful",
            ),
            tooltip=["load_id:N", "inserted_at:T", "status:Q", "schema_name:N"],
        )
        .properties(width=700, height=200)
    )
    chart
    return


@app.cell
def _(loads):
    loads[["load_id", "schema_name", "status", "inserted_at"]].head(10)
    return


if __name__ == "__main__":
    app.run()
