"""dlt AI setup commands."""

from __future__ import annotations

from pathlib import Path

from .config import TOOLKITS
from .uv import run_uv_command


def initialize_agent(uv_executable: str, project_dir: Path, agent: str) -> None:
    """Initialize one AI workbench inside the workspace."""
    run_uv_command(
        uv_executable,
        project_dir,
        ["run", "dlt", "ai", "init", "--agent", agent],
    )


def install_all_toolkits(uv_executable: str, project_dir: Path) -> None:
    """Install every supported dlt AI toolkit."""
    for toolkit in TOOLKITS:
        install_toolkit(uv_executable, project_dir, toolkit)


def install_toolkit(uv_executable: str, project_dir: Path, toolkit: str) -> None:
    """Install one dlt AI toolkit."""
    run_uv_command(
        uv_executable,
        project_dir,
        ["run", "dlt", "ai", "toolkit", toolkit, "install"],
    )
