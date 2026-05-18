"""Project-wide constants for the create-dlthub-workspace CLI."""

from __future__ import annotations

from dataclasses import dataclass

VERSION = "0.1.0"

SCAFFOLDS = (
    (
        "starter_workspace",
        "Starter",
        "Ingestion, transformations, data quality, and notebooks.",
    ),
    (
        "minimal_workspace",
        "Minimal",
        "Bare workspace with a single placeholder pipeline.",
    ),
)

AGENTS = ("claude", "cursor", "codex")

TOOLKITS = (
    "data-exploration",
    "dlthub-runtime",
    "rest-api-pipeline",
    "transformations",
)

# Pinned commit of dlt-hub/dlthub-ai-workbench that `make generate-ai` fetches.
# Setting a SHA keeps generation reproducible across machines and over time:
# CI's `check-ai` step compares the committed scaffold against whatever this
# ref produces, so any drift becomes a deliberate two-line PR (bump SHA +
# commit regenerated scaffold).
#
# To bump: pick a new SHA (the workbench repo has no tags today), update the
# constant below, run `make generate-ai`, commit the resulting scaffold diff
# alongside this change.
WORKBENCH_REF: str | None = "2e2a3695b6fb039d2a4638a0f7e23751fe33b16d"


@dataclass(frozen=True)
class RecommendedPath:
    """The path we recommend new users follow. Also the path `--yes` runs."""

    scaffold: str
    install_uv: bool
    run_uv_sync: bool
    agents: tuple[str, ...]


RECOMMENDED = RecommendedPath(
    scaffold="starter_workspace",
    install_uv=True,
    run_uv_sync=True,
    agents=AGENTS,
)
