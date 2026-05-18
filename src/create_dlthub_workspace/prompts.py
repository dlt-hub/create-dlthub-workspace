"""Interactive prompts. Called only from the planning phase."""

from __future__ import annotations

from typing import cast

import beaupy

from .config import AGENTS, DEFAULT_AGENT, DEFAULT_SCAFFOLD, SCAFFOLDS
from .display import console

CURSOR = "❯"
CURSOR_STYLE = "#59C1D5"
TICK_CHAR = "●"


def _echo_selection(value: str) -> None:
    """Persist the user's choice after beaupy clears its widget."""
    console.print(f"  [{CURSOR_STYLE}]{TICK_CHAR}[/{CURSOR_STYLE}] [bold]{value}[/bold]")


def choose_scaffold(default: str = DEFAULT_SCAFFOLD) -> str:
    """Arrow-key select for the bundled scaffold."""
    keys = [key for key, _, _ in SCAFFOLDS]
    labels = [label for _, label, _ in SCAFFOLDS]
    options = [f"[bold]{label}[/bold]   [dim]{description}[/dim]" for _, label, description in SCAFFOLDS]
    default_index = keys.index(default) if default in keys else 0

    console.print("\n[bold]Choose a scaffold[/bold] [dim](↑/↓ to move, enter to confirm)[/dim]")
    # beaupy ships no type stubs, so mypy sees the result as Any; cast narrows it
    # to the concrete branch we're using (return_index=True yields an int).
    index = cast(
        int,
        beaupy.select(
            options,
            cursor=CURSOR,
            cursor_style=CURSOR_STYLE,
            cursor_index=default_index,
            return_index=True,
        ),
    )
    _echo_selection(labels[index])
    return keys[index]


def choose_agents(default: str = DEFAULT_AGENT) -> list[str]:
    """Arrow-key multi-select for AI workbenches."""
    agents = list(AGENTS)
    default_index = agents.index(default) if default in agents else 0

    console.print("\n[bold]Choose AI workbench(es)[/bold] [dim](space to toggle, enter to confirm)[/dim]")
    selected = cast(
        list[str],
        beaupy.select_multiple(
            agents,
            cursor_style=CURSOR_STYLE,
            tick_character=TICK_CHAR,
            tick_style=CURSOR_STYLE,
            ticked_indices=[default_index],
        ),
    )
    _echo_selection(", ".join(selected) if selected else "(none)")
    return selected


def confirm(message: str, *, default: bool = True) -> bool:
    """Arrow-key Yes/No confirmation."""
    console.print(f"\n[bold]{message}[/bold]")
    choice = cast(
        str,
        beaupy.select(
            ["Yes", "No"],
            cursor=CURSOR,
            cursor_style=CURSOR_STYLE,
            cursor_index=0 if default else 1,
        ),
    )
    _echo_selection(choice)
    return choice == "Yes"
