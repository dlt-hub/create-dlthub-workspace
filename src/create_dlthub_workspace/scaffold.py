"""Copy a bundled scaffold into a new workspace directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from .errors import ScaffoldError

SCAFFOLDS_DIR = Path(__file__).parent / "scaffolds"


def validate_scaffold_target(project_dir: Path, *, scaffold: str) -> None:
    """Check that the scaffold exists and the target directory is writable. No writes."""
    source = SCAFFOLDS_DIR / scaffold
    if not source.is_dir():
        available = ", ".join(sorted(p.name for p in SCAFFOLDS_DIR.iterdir() if p.is_dir()))
        raise ScaffoldError(
            f"Unknown scaffold {scaffold!r}. Available: {available or '(none)'}"
        )

    if project_dir.exists() and any(project_dir.iterdir()):
        raise ScaffoldError(
            f"Target directory already exists and is not empty: {project_dir}"
        )


def copy_scaffold(project_dir: Path, *, scaffold: str) -> None:
    """Copy the bundled scaffold ``scaffold`` into ``project_dir``."""
    validate_scaffold_target(project_dir, scaffold=scaffold)
    source = SCAFFOLDS_DIR / scaffold
    project_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, project_dir, ignore=_ignore_runtime, dirs_exist_ok=True)


def _ignore_runtime(src: str, names: list[str]) -> set[str]:
    """Skip dev-time artifacts that may sit alongside the scaffold sources."""
    skip: set[str] = set()
    src_basename = Path(src).name

    for name in names:
        if name in {"__pycache__", ".venv", ".pytest_cache", ".ruff_cache", ".mypy_cache"}:
            skip.add(name)
        elif name.endswith(".pyc"):
            skip.add(name)
        elif src_basename == ".dlt" and name in {"data", "state", ".var"}:
            skip.add(name)

    return skip
