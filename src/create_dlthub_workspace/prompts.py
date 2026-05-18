"""Interactive prompts. Called only from the planning phase."""

from __future__ import annotations

from typing import cast

import beaupy

from .config import AGENTS, RECOMMENDED, SCAFFOLDS
from .display import console

CURSOR = "❯"
CURSOR_STYLE = "#59C1D5"
TICK_CHAR = "●"
RECOMMENDED_SUFFIX = " [dim](recommended)[/dim]"


def _echo_selection(value: str) -> None:
    """Persist the user's choice after beaupy clears its widget."""
    console.print(f"  [{CURSOR_STYLE}]{TICK_CHAR}[/{CURSOR_STYLE}] [bold]{value}[/bold]")


def choose_scaffold(default: str = RECOMMENDED.scaffold) -> str:
    """Arrow-key select for the bundled scaffold."""
    keys = [key for key, _, _ in SCAFFOLDS]
    labels = [label for _, label, _ in SCAFFOLDS]
    options = [
        f"[bold]{label}[/bold]{RECOMMENDED_SUFFIX if key == RECOMMENDED.scaffold else ''}   [dim]{description}[/dim]"
        for key, label, description in SCAFFOLDS
    ]
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


def choose_agents(default: str = RECOMMENDED.agent) -> list[str]:
    """Arrow-key multi-select for AI workbenches."""
    agents = list(AGENTS)
    options = [f"{agent}{RECOMMENDED_SUFFIX if agent == RECOMMENDED.agent else ''}" for agent in agents]
    default_index = agents.index(default) if default in agents else 0

    console.print("\n[bold]Choose AI workbench(es)[/bold] [dim](space to toggle, enter to confirm)[/dim]")
    selected_options = cast(
        list[str],
        beaupy.select_multiple(
            options,
            cursor_style=CURSOR_STYLE,
            tick_character=TICK_CHAR,
            tick_style=CURSOR_STYLE,
            ticked_indices=[default_index],
        ),
    )
    selected = [agents[i] for i, option in enumerate(options) if option in selected_options]
    _echo_selection(", ".join(selected) if selected else "(none)")
    return selected


def confirm(message: str, *, default: bool = True, recommended: bool | None = None) -> bool:
    """Arrow-key Yes/No confirmation.

    Pass ``recommended=True`` (or ``False``) to badge the recommended choice.
    """
    console.print(f"\n[bold]{message}[/bold]")
    yes_label = "Yes" + (RECOMMENDED_SUFFIX if recommended is True else "")
    no_label = "No" + (RECOMMENDED_SUFFIX if recommended is False else "")
    choice = cast(
        str,
        beaupy.select(
            [yes_label, no_label],
            cursor=CURSOR,
            cursor_style=CURSOR_STYLE,
            cursor_index=0 if default else 1,
        ),
    )
    result = choice == yes_label
    _echo_selection("Yes" if result else "No")
    return result
