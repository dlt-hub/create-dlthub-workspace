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
    """Initialize one AI workbench inside the workspace.

    `--overwrite` is required so the second+ agent init in the same workspace
    actually writes per-agent files. Without it, dlthub detects the shared
    'init' toolkit and silently no-ops (exit 0, nothing on disk).
    """
    run_uv_command(
        uv_executable,
        project_dir,
        ["run", "dlthub", "ai", "init", "--agent", agent, "--overwrite"],
        verbose=verbose,
    )


def install_toolkit(
    uv_executable: str,
    project_dir: Path,
    toolkit: str,
    *,
    verbose: bool = False,
) -> None:
    """Install one dlt AI toolkit.

    Omits `--agent` so dlthub auto-detects every initialized agent in the
    workspace and installs the toolkit for all of them in a single call.
    """
    run_uv_command(
        uv_executable,
        project_dir,
        ["run", "dlthub", "ai", "toolkit", "install", toolkit],
        verbose=verbose,
    )
