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

TIPS = (
    ("/init-workspace", "set up a fresh Python environment"),
    ("/find-source", "load data from a REST API"),
    ("/explore-data", "query and explore loaded tables"),
    ("/setup-runtime", "deploy your pipeline to dltHub"),
)


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
    [("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", "")],
    [("    ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), ("      ", ""), ("█", "bold #C6D300")],
    [("    ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), ("      ", ""), ("█", "bold #C6D300")],
    [("  ", ""), ("███", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), (" ", ""), ("██", "bold #59C1D5"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("███", "bold #C6D300")],
    [(" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("████", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300")],
    [(" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300")],
    [(" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300")],
    [("  ", ""), ("███", "bold #59C1D5"), (" ", ""), ("█", "bold #59C1D5"), ("  ", ""), ("█", "bold #C6D300"), (" ", ""), ("█", "bold #C6D300"), ("  ", ""), ("█", "bold #C6D300"), ("  ", ""), ("███", "bold #C6D300"), (" ", ""), ("███", "bold #C6D300")],
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


def print_next_steps(project_dir: Path) -> None:
    body = Text()
    body.append("  cd ", style="dim")
    body.append(str(project_dir), style="bold #59C1D5")
    body.append("\n\n")
    body.append("Tips for getting started\n\n", style="bold #C6D300")
    for cmd, desc in TIPS:
        body.append("  Run ", style="dim")
        body.append(cmd, style="bold #59C1D5")
        body.append(f"  {desc}\n", style="dim")
    body.append("\n  Docs: ", style="dim")
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
