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
