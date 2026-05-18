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

# Pin for the dlt-hub/dlthub-ai-workbench repo used by `make generate-ai`.
# - None  -> use the upstream default branch (today: master). Fine for dev.
# - "<sha>" or "<branch>" -> pass through to `dlthub ai init --branch ...`.
# Set this to a commit SHA before cutting a release so the bundled output
# is reproducible. The workbench repo has no tags today, so SHA is the
# only stable handle.
WORKBENCH_REF: str | None = None


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
