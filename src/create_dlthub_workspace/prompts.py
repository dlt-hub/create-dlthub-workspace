"""Interactive prompts. Called only from the planning phase."""

from __future__ import annotations

import beaupy

from .config import AGENTS, DEFAULT_AGENT, DEFAULT_SCAFFOLD, SCAFFOLDS
from .display import console

CURSOR = "❯"
CURSOR_STYLE = "#59C1D5"
TICK_CHAR = "●"


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
