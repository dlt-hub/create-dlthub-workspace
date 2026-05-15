"""Open Brewery DB ingestion pipeline.

Loads public brewery records from a no-auth REST API into a local warehouse.
The example is intentionally small so a new workspace can run without secrets,
API keys, or signups.
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


@run.pipeline(
    "starter_pipeline",
    trigger=trigger.every("5m"),
    expose={"tags": ["ingest"], "display_name": "Brewery data ingest"},
)
def load_breweries():
    """Load public brewery records into the local warehouse."""
    pipeline = dlt.pipeline(
        pipeline_name="starter_pipeline",
        destination="warehouse",
        dataset_name="brewery_data",
        progress="log",
    )
    load_info = pipeline.run(brewery_rest_api_source().add_limit(2))
    print(load_info)


if __name__ == "__main__":
    load_breweries()
