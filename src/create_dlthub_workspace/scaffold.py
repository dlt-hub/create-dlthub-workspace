"""Copy a bundled scaffold into a new workspace directory."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from .errors import ScaffoldError

SCAFFOLDS_DIR = Path(__file__).parent / "scaffolds"

# Top-level entries (relative to the scaffold root) that belong to each agent.
# Used by copy_scaffold to drop entries for agents the user did not select.
# `.agents/` is intentionally not listed here — codex reads it as its skill
# source AND it holds the shared toolkit pool that all agents reference.
AGENT_FILES: dict[str, tuple[str, ...]] = {
    "claude": (".claude", ".claudeignore", ".mcp.json"),
    "cursor": (".cursor", ".cursorignore"),
    "codex": (".codex", ".codexignore", "AGENTS.md"),
}

# The vendored `.dlt/.toolkits` manifest stores an `installed_at` ISO timestamp
# per toolkit. We commit it with this sentinel so `check-ai` diffs stay clean
# across machines; copy_scaffold replaces it with the real install time when
# the user actually creates a workspace.
TOOLKITS_MANIFEST = Path(".dlt") / ".toolkits"
INSTALL_TIME_SENTINEL = "1970-01-01T00:00:00+00:00"


def validate_target_dir(project_dir: Path) -> None:
    """Refuse to write into a non-empty existing directory. No filesystem writes."""
    if project_dir.exists() and any(project_dir.iterdir()):
        raise ScaffoldError(f"Target directory already exists and is not empty: {project_dir}")


def validate_scaffold_name(scaffold: str) -> None:
    """Refuse to copy from a scaffold that isn't bundled. No filesystem writes."""
    source = SCAFFOLDS_DIR / scaffold
    if not source.is_dir():
        available = ", ".join(sorted(p.name for p in SCAFFOLDS_DIR.iterdir() if p.is_dir()))
        raise ScaffoldError(f"Unknown scaffold {scaffold!r}. Available: {available or '(none)'}")


def validate_scaffold_target(project_dir: Path, *, scaffold: str) -> None:
    """Combined target-dir + scaffold-name validation. No filesystem writes."""
    validate_scaffold_name(scaffold)
    validate_target_dir(project_dir)


def copy_scaffold(project_dir: Path, *, scaffold: str, agents: tuple[str, ...] = ()) -> None:
    """Copy the bundled scaffold into ``project_dir``.

    If ``agents`` is non-empty, top-level entries belonging to agents NOT in
    the selection are removed after the copy. Pass ``()`` to keep everything
    that's bundled (useful for tests that just want to verify the layout).
    """
    validate_scaffold_target(project_dir, scaffold=scaffold)
    source = SCAFFOLDS_DIR / scaffold
    project_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, project_dir, ignore=_ignore_runtime, dirs_exist_ok=True)

    if agents:
        _drop_unselected_agent_entries(project_dir, agents)

    _stamp_install_time(project_dir)


def _drop_unselected_agent_entries(project_dir: Path, agents: tuple[str, ...]) -> None:
    """Remove top-level entries for agents not in the selection.

    NB: passes through AGENT_FILES.items(), so an agents tuple containing
    names that aren't in AGENT_FILES (typos, unknown agents) match nothing
    and every entry gets removed. Argparse normally guards this via
    `choices=AGENTS`, but programmatic callers should pass validated values.
    """
    for agent, entries in AGENT_FILES.items():
        if agent in agents:
            continue
        for entry in entries:
            target = project_dir / entry
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()


def _stamp_install_time(project_dir: Path) -> None:
    """Replace the sentinel `installed_at` in the toolkits manifest with now."""
    manifest = project_dir / TOOLKITS_MANIFEST
    if not manifest.exists():
        return
    content = manifest.read_text(encoding="utf-8")
    if INSTALL_TIME_SENTINEL not in content:
        return
    now_iso = datetime.now(timezone.utc).isoformat()
    manifest.write_text(content.replace(INSTALL_TIME_SENTINEL, now_iso), encoding="utf-8")


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
