"""Command-line entrypoint for create-dlthub-workspace."""

from __future__ import annotations

import argparse
import sys

from .config import AGENTS, RECOMMENDED, SCAFFOLDS
from .display import console, print_banner, print_next_steps, print_resume_steps, step
from .errors import WorkspaceError
from .plan import WorkspacePlan, WorkspaceStage, build_plan
from .project_metadata import apply_workspace_name
from .scaffold import copy_scaffold
from .uv import execute_uv_install, run_uv_sync


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="create-dlthub-workspace",
        description="Scaffold a new dltHub workspace.",
    )
    parser.add_argument("project_dir", help="Directory to create for the new workspace.")
    parser.add_argument(
        "--scaffold",
        choices=[key for key, _, _ in SCAFFOLDS],
        help=f"Bundled scaffold to use. Defaults to the recommended {RECOMMENDED.scaffold!r} in non-interactive mode.",
    )
    parser.add_argument(
        "--agent",
        action="append",
        choices=AGENTS,
        help=(
            "AI workbench to initialize. Pass multiple times to initialize several. "
            "Defaults to all available workbenches in non-interactive mode."
        ),
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Run the recommended path (starter scaffold, install uv, uv sync, all AI workbenches).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Stream output from underlying subprocesses (uv, dlthub).",
    )
    parser.add_argument(
        "--skip-uv-sync",
        action="store_true",
        help="Stop after installing uv. Skips `uv sync` and all downstream AI setup.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        run(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        return 130
    except WorkspaceError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        return 1
    return 0


def run(args: argparse.Namespace) -> None:
    print_banner()
    console.print()

    plan = build_plan(args)
    execute_plan(plan)


def execute_plan(plan: WorkspacePlan) -> None:
    verbose = plan.verbose

    with step(f"Creating workspace at {plan.project_dir}", verbose=verbose):
        copy_scaffold(plan.project_dir, scaffold=plan.scaffold, agents=plan.agents)
        package_name = apply_workspace_name(plan.project_dir, plan.project_dir.name)
    console.print(f"[green]Created[/green] {plan.project_dir}")
    console.print(f"[dim]Project package name:[/dim] {package_name}")

    if plan.stage is WorkspaceStage.SCAFFOLD_ONLY:
        console.print("\n[yellow]Skipped[/yellow] uv install and dependency sync.\n")
        print_resume_steps(plan.project_dir, uv_installed=False)
        return

    if plan.install_uv:
        uv_executable = execute_uv_install(verbose=verbose)
    else:
        assert plan.uv_executable is not None
        uv_executable = plan.uv_executable

    if plan.stage is WorkspaceStage.THROUGH_UV_INSTALL:
        console.print("\n[yellow]Skipped[/yellow] dependency sync.\n")
        print_resume_steps(plan.project_dir, uv_installed=True)
        return

    with step("Installing dependencies", verbose=verbose):
        run_uv_sync(uv_executable, plan.project_dir, verbose=verbose)
    console.print("[green]Installed[/green] dependencies into .venv")

    console.print()
    print_next_steps(plan.project_dir, scaffold=plan.scaffold)


if __name__ == "__main__":
    sys.exit(main())
