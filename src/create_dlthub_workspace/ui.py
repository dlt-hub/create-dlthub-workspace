"""Rich-powered terminal UI for create-dlthub-workspace."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import beaupy
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .config import AGENTS, DEFAULT_AGENT, DEFAULT_SCAFFOLD, SCAFFOLDS, TIPS, VERSION

CURSOR = "❯"
CURSOR_STYLE = "#59C1D5"
TICK_CHAR = "●"

console = Console()


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


def choose_scaffold(default: str = DEFAULT_SCAFFOLD) -> str:
    """Arrow-key select for the bundled scaffold."""
    keys = [key for key, _, _ in SCAFFOLDS]
    options = [
        f"[bold]{label}[/bold]   [dim]{description}[/dim]"
        for _, label, description in SCAFFOLDS
    ]
    default_index = keys.index(default) if default in keys else 0

    console.print(
        "\n[bold]Choose a scaffold[/bold] [dim](↑/↓ to move, enter to confirm)[/dim]"
    )
    index = beaupy.select(
        options,
        cursor=CURSOR,
        cursor_style=CURSOR_STYLE,
        cursor_index=default_index,
        return_index=True,
    )
    return keys[index]


def choose_agents(default: str = DEFAULT_AGENT) -> list[str]:
    """Arrow-key multi-select for AI workbenches."""
    agents = list(AGENTS)
    default_index = agents.index(default) if default in agents else 0

    console.print(
        "\n[bold]Choose AI workbench(es)[/bold] "
        "[dim](space to toggle, enter to confirm)[/dim]"
    )
    return beaupy.select_multiple(
        agents,
        cursor_style=CURSOR_STYLE,
        tick_character=TICK_CHAR,
        tick_style=CURSOR_STYLE,
        ticked_indices=[default_index],
    )


def confirm(message: str, *, default: bool = True) -> bool:
    """Arrow-key Yes/No confirmation."""
    console.print(f"\n[bold]{message}[/bold]")
    choice = beaupy.select(
        ["Yes", "No"],
        cursor=CURSOR,
        cursor_style=CURSOR_STYLE,
        cursor_index=0 if default else 1,
    )
    return choice == "Yes"


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

