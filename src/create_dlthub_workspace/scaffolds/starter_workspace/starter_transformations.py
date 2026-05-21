"""Brewery starter transformations.

Reads raw brewery data and computes cleaned and aggregated tables using Ibis.
Triggered automatically after ingestion succeeds.
"""

import typing

import dlt
from dlt.hub import run
from ibis import ir

from starter_pipeline import load_breweries


@dlt.hub.transformation(write_disposition="replace")
def breweries_clean(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
    """Select a clean column set with a derived has_coordinates flag."""
    breweries = dataset.table("breweries").to_ibis()
    yield breweries.select(
        "id",
        "name",
        "brewery_type",
        "city",
        "state_province",
        "country",
        "latitude",
        "longitude",
    ).mutate(has_coordinates=breweries.latitude.notnull() & breweries.longitude.notnull())


@dlt.hub.transformation(write_disposition="replace")
def breweries_by_state(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
    """Count breweries per state/province with coordinate availability."""
    breweries = dataset.table("breweries").to_ibis()
    yield breweries.group_by("state_province").aggregate(
        brewery_count=breweries.id.count(),
        with_coordinates=(breweries.latitude.notnull() & breweries.longitude.notnull()).sum(),
    )


@dlt.source
def brewery_metrics(raw_dataset: dlt.Dataset) -> list:
    """Combine brewery transformations into a single source."""
    return [
        breweries_clean(raw_dataset),
        breweries_by_state(raw_dataset),
    ]


starter_transform_pipe = dlt.pipeline(
    pipeline_name="starter_transform",
    destination="warehouse",
    dataset_name="brewery_transforms",
)


@run.pipeline(
    starter_transform_pipe,
    trigger=load_breweries.success,
    expose={"display_name": "Brewery transformations"},
)
def transform_breweries():
    """Transform raw brewery data into clean tables and metrics."""
    source_pipe = dlt.attach(pipeline_name="starter_pipeline")
    load_info = starter_transform_pipe.run(brewery_metrics(source_pipe.dataset()))
    print(load_info)


if __name__ == "__main__":
    transform_breweries()
