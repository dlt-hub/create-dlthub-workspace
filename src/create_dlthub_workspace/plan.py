"""Resolved answers to every question the CLI asks the user.

A `WorkspacePlan` is built once during the planning phase and then frozen.
Execution reads from it and must not prompt the user again.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_AGENT, DEFAULT_SCAFFOLD
from .errors import UvError, WorkspaceError
from .scaffold import validate_scaffold_target
from .prompts import choose_agents, choose_scaffold, confirm
from .uv import find_uv


@dataclass(frozen=True)
class WorkspacePlan:
    project_dir: Path
    scaffold: str
    agents: tuple[str, ...]
    uv_executable: str | None
    install_uv: bool
    skip_uv_sync: bool
    verbose: bool


def build_plan(args: argparse.Namespace) -> WorkspacePlan:
    """Gather every answer needed to scaffold the workspace. No filesystem writes."""
    project_dir = Path(args.project_dir).expanduser().resolve()

    scaffold = args.scaffold or (DEFAULT_SCAFFOLD if args.yes else choose_scaffold())
    agents = tuple(args.agent or ([DEFAULT_AGENT] if args.yes else choose_agents()))
    if not agents:
        raise WorkspaceError("At least one AI workbench must be selected.")

    validate_scaffold_target(project_dir, scaffold=scaffold)

    uv_executable = find_uv()
    install_uv = False
    if uv_executable is None:
        if args.yes or confirm("uv is required but was not found. Install uv now?"):
            install_uv = True
        else:
            raise UvError("uv is required. Install uv and run this command again.")

    return WorkspacePlan(
        project_dir=project_dir,
        scaffold=scaffold,
        agents=agents,
        uv_executable=uv_executable,
        install_uv=install_uv,
        skip_uv_sync=args.skip_uv_sync,
        verbose=args.verbose,
    )
