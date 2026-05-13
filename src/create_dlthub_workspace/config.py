"""Project-wide constants for the create-dlthub-workspace CLI."""

VERSION = "0.1.0"

REPO_URL = "https://github.com/dlt-hub/runtime-starter-pack"
DEFAULT_TEMPLATE_REF = "main"
DEFAULT_TEMPLATE_DIR = "github_ingest_workspace"

AGENTS = ("claude", "cursor", "codex")
DEFAULT_AGENT = "claude"

TOOLKITS = (
    "data-exploration",
    "dlthub-runtime",
    "rest-api-pipeline",
    "transformations",
)

TIPS = (
    ("/init-workspace", "set up a fresh Python environment"),
    ("/find-source", "load data from a REST API"),
    ("/explore-data", "query and explore loaded tables"),
    ("/setup-runtime", "deploy your pipeline to dltHub"),
)


def tarball_url(template_ref: str = DEFAULT_TEMPLATE_REF) -> str:
    """Return the GitHub tarball URL for a starter-pack ref."""
    return f"{REPO_URL}/archive/{template_ref}.tar.gz"
