"""Rich-powered terminal UI for create-dlthub-workspace."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from .config import AGENTS, DEFAULT_AGENT, TIPS, VERSION

console = Console()

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


def choose_agent(default: str = DEFAULT_AGENT) -> str:
    """Ask the user which AI workbench to initialize."""
    return Prompt.ask(
        "Choose your AI workbench",
        choices=list(AGENTS),
        default=default,
    )


def confirm(message: str, *, default: bool = True) -> bool:
    """Ask for yes/no confirmation."""
    return Confirm.ask(message, default=default)


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

