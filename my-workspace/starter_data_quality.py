"""Data quality checks for the starter brewery dataset."""

import dlt
from dlt.hub import run
from dlt.hub.run import trigger

import dlthub.data_quality as dq


named_brewery_checks = [
    ("id__is_not_null", dq.checks.is_not_null("id")),
    ("name__is_not_null", dq.checks.is_not_null("name")),
    ("brewery_type__is_not_null", dq.checks.is_not_null("brewery_type")),
    ("city__is_not_null", dq.checks.is_not_null("city")),
    ("country__is_not_null", dq.checks.is_not_null("country")),
    ("brewery_type__is_in", dq.checks.is_in(
        "brewery_type",
        [
            "micro",
            "nano",
            "regional",
            "brewpub",
            "large",
            "planning",
            "bar",
            "contract",
            "proprietor",
            "closed",
            "taproom",
            "beergarden",
        ],
    )),
]

brewery_checks = [check for _, check in named_brewery_checks]


@run.job(
    trigger=trigger.schedule("0 * * * *"),
    expose={"display_name": "Starter data quality"},
)
def run_dq_checks():
    """Run starter data quality checks. Fails if any check has failures."""
    pipeline = dlt.pipeline(
        pipeline_name="starter_pipeline",
        destination="warehouse",
        dataset_name="brewery_data",
    )

    dataset = pipeline.dataset()
    suite = dq.CheckSuite(dataset, checks={"breweries": brewery_checks})

    all_passed = True
    for check_name, _check in named_brewery_checks:
        failures = suite.get_failures("breweries", check_name).arrow()
        if len(failures) > 0:
            print(f"FAIL: breweries.{check_name} -- {len(failures)} failures")
            all_passed = False
        else:
            print(f"PASS: breweries.{check_name}")

    if not all_passed:
        raise RuntimeError("Data quality checks failed -- see output above for details")
    print("All data quality checks passed")


if __name__ == "__main__":
    run_dq_checks()
