"""Minimal dlt pipeline.

Loads a tiny in-memory dataset into a local warehouse. Replace this with
your own source.
"""

import dlt
from dlt.hub import run


pipe = dlt.pipeline(
    pipeline_name="minimal_pipeline",
    destination="warehouse",
    dataset_name="my_data",
)


@run.pipeline(pipe, expose={"display_name": "Minimal pipeline"})
def load_data():
    """Load a placeholder dataset. Swap the list for a real dlt source."""
    load_info = pipe.run(
        [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}],
        table_name="example",
    )
    print(load_info)


if __name__ == "__main__":
    load_data()
