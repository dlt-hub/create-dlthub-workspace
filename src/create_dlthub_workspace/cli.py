"""Command-line entrypoint for create-dlthub-workspace."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import AGENTS, DEFAULT_AGENT, DEFAULT_TEMPLATE_DIR, DEFAULT_TEMPLATE_REF, TOOLKITS
from .dlt_ai import initialize_agent, install_toolkit
from .errors import WorkspaceError
from .project_metadata import apply_workspace_name
from .scaffold import download_scaffold
from .ui import choose_agent, confirm, console, print_banner, print_next_steps, step
from .uv import ensure_uv, run_uv_sync


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="create-dlthub-workspace",
        description="Scaffold a new dltHub workspace.",
    )
    parser.add_argument("project_dir", help="Directory to create for the new workspace.")
    parser.add_argument(
        "--agent",
        choices=AGENTS,
        help=f"AI workbench to initialize. Defaults to {DEFAULT_AGENT!r} in non-interactive mode.",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Accept defaults and approve required setup prompts.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Stream output from underlying subprocesses (uv, dlthub).",
    )
    parser.add_argument(
        "--template-ref",
        default=DEFAULT_TEMPLATE_REF,
        help="Starter-pack GitHub branch, tag, or commit to download.",
    )
    parser.add_argument(
        "--skip-uv-sync",
        action="store_true",
        help="Create the workspace without running `uv sync`.",
    )
    parser.add_argument(
        "--template-dir",
        default=DEFAULT_TEMPLATE_DIR,
        help=argparse.SUPPRESS,
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
    project_dir = Path(args.project_dir).expanduser().resolve()
    verbose = args.verbose

    print_banner()
    console.print()

    agent = args.agent or (DEFAULT_AGENT if args.yes else choose_agent())
    uv_executable = ensure_uv(
        assume_yes=args.yes,
        confirm_install=confirm,
        verbose=verbose,
    )

    with step(f"Creating workspace at {project_dir}", verbose=verbose):
        download_scaffold(
            project_dir,
            template_ref=args.template_ref,
            template_dir=args.template_dir,
        )
        package_name = apply_workspace_name(project_dir, project_dir.name)

    console.print(f"[green]Created[/green] {project_dir}")
    console.print(f"[dim]Project package name:[/dim] {package_name}")

    if args.skip_uv_sync:
        console.print(
            f"[yellow]Skipped[/yellow] dependency sync. Run `cd {project_dir} && uv sync` later."
        )
    else:
        with step("Installing dependencies", verbose=verbose):
            run_uv_sync(uv_executable, project_dir, verbose=verbose)
        console.print("[green]Installed[/green] dependencies")

    with step(f"Initializing {agent}", verbose=verbose):
        initialize_agent(uv_executable, project_dir, agent, verbose=verbose)
    console.print(f"[green]Initialized[/green] {agent}")

    console.print("\n[bold]Installing dltHub AI toolkits[/bold]")
    for toolkit in TOOLKITS:
        with step(f"  Installing {toolkit}", verbose=verbose):
            install_toolkit(uv_executable, project_dir, toolkit, verbose=verbose)
        console.print(f"  [green]Installed[/green] {toolkit}")

    console.print()
    print_next_steps(project_dir)


if __name__ == "__main__":
    sys.exit(main())
