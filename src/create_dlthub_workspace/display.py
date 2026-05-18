"""Rich-powered output: banner, spinners, next-steps panel."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .config import VERSION

console = Console()

NEXT_STEPS: dict[str, tuple[tuple[str, str | None], ...]] = {
    "starter_workspace": (
        (
            "Run the ingestion pipeline in dltHub (transformations auto-trigger; you'll be prompted to connect/login):",
            "uv run dlthub run load_breweries",
        ),
        ("Open the dltHub dashboard:", "uv run dlthub show"),
    ),
    "minimal_workspace": (
        (
            "Run the placeholder pipeline in dltHub (you'll be prompted to connect/login):",
            "uv run dlthub run load_data",
        ),
        ("Open the dltHub dashboard:", "uv run dlthub show"),
        ("Edit pipeline.py to swap the placeholder for a real source, then re-run.", None),
    ),
}


@contextmanager
def step(description: str, *, verbose: bool = False) -> Iterator[None]:
    """Show a spinner during a subprocess step, or a plain header in verbose mode."""
    if verbose:
        console.print(f"[bold]{description}[/bold]")
        yield
        return
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(description, total=None)
        yield


ROWS = [
    [
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
    ],
    [
        ("    ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("      ", ""),
        ("█", "bold #C6D300"),
    ],
    [
        ("    ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("      ", ""),
        ("█", "bold #C6D300"),
    ],
    [
        ("  ", ""),
        ("███", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("██", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("███", "bold #C6D300"),
    ],
    [
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("████", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
    ],
    [
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
    ],
    [
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
    ],
    [
        ("  ", ""),
        ("███", "bold #59C1D5"),
        (" ", ""),
        ("█", "bold #59C1D5"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        (" ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("█", "bold #C6D300"),
        ("  ", ""),
        ("███", "bold #C6D300"),
        (" ", ""),
        ("███", "bold #C6D300"),
    ],
]


def _build_logo() -> Text:
    logo = Text()
    for row in ROWS:
        for text, style in row:
            logo.append(text, style=style)
        logo.append("\n")
    logo.append("\n  Scaffold a dltHub workspace", style="dim")
    return logo


def print_banner() -> None:
    console.print(
        Panel(
            _build_logo(),
            title=f"create-dlthub-workspace v{VERSION}",
            title_align="left",
            border_style="#59C1D5",
            padding=(1, 2),
        )
    )


def print_next_steps(project_dir: Path, *, scaffold: str) -> None:
    """Post-setup tips panel. Steps are tailored to the chosen scaffold."""
    steps = NEXT_STEPS[scaffold]

    body = Text()
    body.append("  cd ", style="dim")
    body.append(str(project_dir), style="bold #59C1D5")
    body.append("\n\n")
    body.append("What to try next\n\n", style="bold #C6D300")
    for index, (label, command) in enumerate(steps, start=1):
        body.append(f"  {index}. {label}\n", style="dim")
        if command is not None:
            body.append(f"     {command}\n", style="bold #59C1D5")
        body.append("\n")
    body.append("  Docs: ", style="dim")
    body.append(
        "github.com/dlt-hub/dlthub-ai-workbench",
        style="underline #59C1D5 link https://github.com/dlt-hub/dlthub-ai-workbench/blob/master/README.md",
    )

    console.print(
        Panel(
            body,
            title="You're all set",
            title_align="left",
            border_style="#C6D300",
            padding=(1, 2),
        )
    )


def print_resume_steps(project_dir: Path, *, uv_installed: bool) -> None:
    """Remaining setup commands. Used when execution stops before AI work."""
    steps: list[tuple[str, str]] = []
    if not uv_installed:
        steps.append(("Install uv:", "curl -LsSf https://astral.sh/uv/install.sh | sh"))
    steps.append(("Install workspace dependencies:", "uv sync"))
    steps.append(("Initialize an AI workbench:", "uv run dlthub ai init --agent claude"))

    body = Text()
    body.append("  cd ", style="dim")
    body.append(str(project_dir), style="bold #59C1D5")
    body.append("\n\n")
    body.append("Finish setup\n\n", style="bold #C6D300")
    for index, (label, command) in enumerate(steps, start=1):
        body.append(f"  {index}. {label}\n", style="dim")
        body.append(f"     {command}\n\n", style="bold #59C1D5")
    body.append("  Docs: ", style="dim")
    body.append(
        "github.com/dlt-hub/dlthub-ai-workbench",
        style="underline #59C1D5 link https://github.com/dlt-hub/dlthub-ai-workbench/blob/master/README.md",
    )

    console.print(
        Panel(
            body,
            title="Almost there",
            title_align="left",
            border_style="#C6D300",
            padding=(1, 2),
        )
    )
