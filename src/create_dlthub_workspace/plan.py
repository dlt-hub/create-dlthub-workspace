"""Resolved answers to every question the CLI asks the user.

A `WorkspacePlan` is built once during the planning phase and then frozen.
Execution reads from it and must not prompt the user again.

Auto-detection (uv presence, target-dir validity, scaffold availability) runs
in `build_plan` BEFORE the related prompt fires.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .config import RECOMMENDED
from .errors import WorkspaceError
from .prompts import choose_agents, choose_scaffold, confirm
from .scaffold import validate_scaffold_target
from .uv import find_uv


class WorkspaceStage(Enum):
    """How far the execution phase should run before stopping."""

    SCAFFOLD_ONLY = "scaffold_only"
    THROUGH_UV_INSTALL = "through_uv_install"
    FULL = "full"


@dataclass(frozen=True)
class WorkspacePlan:
    project_dir: Path
    scaffold: str
    stage: WorkspaceStage
    agents: tuple[str, ...]
    uv_executable: str | None
    install_uv: bool
    verbose: bool


def build_plan(args: argparse.Namespace) -> WorkspacePlan:
    """Gather every answer needed to scaffold the workspace. No filesystem writes."""
    project_dir = Path(args.project_dir).expanduser().resolve()

    scaffold = args.scaffold or (RECOMMENDED.scaffold if args.yes else choose_scaffold())
    validate_scaffold_target(project_dir, scaffold=scaffold)

    uv_executable = find_uv()
    install_uv = False
    stage = WorkspaceStage.FULL

    if uv_executable is None:
        if args.yes or confirm(
            "uv is required but was not found. Install uv now?",
            recommended=RECOMMENDED.install_uv,
        ):
            install_uv = True
        else:
            stage = WorkspaceStage.SCAFFOLD_ONLY

    if stage != WorkspaceStage.SCAFFOLD_ONLY:
        if args.skip_uv_sync or (
            not args.yes
            and not confirm(
                "Install workspace dependencies with `uv sync`?",
                recommended=RECOMMENDED.run_uv_sync,
            )
        ):
            stage = WorkspaceStage.THROUGH_UV_INSTALL

    if stage == WorkspaceStage.FULL:
        agents = tuple(args.agent or ([RECOMMENDED.agent] if args.yes else choose_agents()))
        if not agents:
            raise WorkspaceError("At least one AI workbench must be selected.")
    else:
        agents = ()

    return WorkspacePlan(
        project_dir=project_dir,
        scaffold=scaffold,
        stage=stage,
        agents=agents,
        uv_executable=uv_executable,
        install_uv=install_uv,
        verbose=args.verbose,
    )
