"""dlt AI setup commands."""

from __future__ import annotations

from pathlib import Path

from .uv import run_uv_command


def initialize_agent(
    uv_executable: str,
    project_dir: Path,
    agent: str,
    *,
    verbose: bool = False,
) -> None:
    """Initialize one AI workbench inside the workspace."""
    run_uv_command(
        uv_executable,
        project_dir,
        ["run", "dlthub", "ai", "init", "--agent", agent],
        verbose=verbose,
    )


def install_toolkit(
    uv_executable: str,
    project_dir: Path,
    toolkit: str,
    *,
    verbose: bool = False,
) -> None:
    """Install one dlt AI toolkit."""
    run_uv_command(
        uv_executable,
        project_dir,
        ["run", "dlthub", "ai", "toolkit", "install", toolkit],
        verbose=verbose,
    )
