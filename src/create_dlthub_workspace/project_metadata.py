"""Helpers for customizing generated workspace metadata."""

from __future__ import annotations

import re
from pathlib import Path

from .errors import ScaffoldError

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10.
    import tomli as tomllib


def apply_workspace_name(project_dir: Path, workspace_name: str) -> str:
    """Set the generated project's package name and return the normalized value."""
    package_name = normalize_project_name(workspace_name)
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        return package_name

    content = pyproject.read_text(encoding="utf-8")
    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise ScaffoldError(f"Could not parse generated pyproject.toml: {exc}") from exc

    if "project" not in data:
        return package_name

    pyproject.write_text(_replace_project_name(content, package_name), encoding="utf-8")
    return package_name


def normalize_project_name(name: str) -> str:
    """Normalize a directory name into a valid Python distribution name."""
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return normalized or "dlthub-workspace"


def _replace_project_name(content: str, package_name: str) -> str:
    lines = content.splitlines(keepends=True)
    in_project = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if in_project and stripped.startswith("["):
            break
        if in_project and re.match(r"^name\s*=", stripped):
            newline = "\n" if line.endswith("\n") else ""
            lines[index] = f'name = "{package_name}"{newline}'
            return "".join(lines)

    insert_at = next(
        (index + 1 for index, line in enumerate(lines) if line.strip() == "[project]"),
        None,
    )
    if insert_at is None:
        return content

    lines.insert(insert_at, f'name = "{package_name}"\n')
    return "".join(lines)
