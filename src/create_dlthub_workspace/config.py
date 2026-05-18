"""Project-wide constants for the create-dlthub-workspace CLI."""

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
DEFAULT_SCAFFOLD = SCAFFOLDS[0][0]

AGENTS = ("claude", "cursor", "codex")
DEFAULT_AGENT = "claude"

TOOLKITS = (
    "data-exploration",
    "dlthub-runtime",
    "rest-api-pipeline",
    "transformations",
)
