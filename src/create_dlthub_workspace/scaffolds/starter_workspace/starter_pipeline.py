"""Open Brewery DB ingestion pipeline.

Loads public brewery records from a no-auth REST API into the configured
warehouse. Dev runs on a local DuckDB file; prod uses MotherDuck (see
.dlt/prod.secrets.toml for the token).
"""

import dlt
from dlt.hub import run
from dlt.hub.run import trigger
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def brewery_rest_api_source(
    country: str = "united_states",
    per_page: int = 50,
):
    """Define dlt resources for the Open Brewery DB API."""
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.openbrewerydb.org/v1",
            "headers": {"User-Agent": "dlthub-starter-workspace"},
            "paginator": {
                "type": "page_number",
                "base_page": 1,
                "page_param": "page",
                "total_path": None,
                "stop_after_empty_page": True,
            },
        },
        "resource_defaults": {
            "endpoint": {
                "params": {
                    "per_page": per_page,
                }
            },
            "write_disposition": "replace",
        },
        "resources": [
            {
                "name": "breweries",
                "endpoint": {
                    "path": "/breweries",
                    "params": {"by_country": country},
                },
            },
        ],
    }

    yield from rest_api_resources(config)


starter_pipe = dlt.pipeline(
    pipeline_name="starter_pipeline",
    destination="warehouse",
    dataset_name="brewery_data",
    progress="log",
)


@run.pipeline(
    starter_pipe,
    expose={"tags": ["ingest"], "display_name": "Brewery data ingest"},
)
def load_breweries():
    """Load public brewery records into the configured warehouse."""
    # Cap to a handful of pages so starter runs finish quickly.
    load_info = starter_pipe.run(brewery_rest_api_source().add_limit(10))
    print(load_info)


if __name__ == "__main__":
    load_breweries()
