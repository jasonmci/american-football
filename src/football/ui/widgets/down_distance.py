from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from football.engine.game_state import GameState


def _down_text(down: int) -> str:
    if down == 1:
        return "1st"
    if down == 2:
        return "2nd"
    if down == 3:
        return "3rd"
    return "4th"


def _yard_descriptor(yard_line: int) -> str:
    """Return string like 'OWN 20' or 'OPP 35'."""
    if yard_line <= 50:
        return f"OWN {yard_line}"
    else:
        return f"OPP {100 - yard_line}"


class DownDistance(Static):
    """Panel showing down, distance, yard line, and possession."""

    def __init__(self, *, state: GameState, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = state

    def set_state(self, state: GameState) -> None:
        self._state = state
        self.refresh()

    def render(self) -> Panel:
        s = self._state

        table = Table.grid(pad_edge=False)
        table.add_column(justify="left")
        table.add_column(justify="right")

        # Possession
        table.add_row(
            Text("Possession", style="dim"),
            Text(s.possession, style="bold"),
        )

        # Down & distance
        table.add_row(
            Text("Down & Dist", style="dim"),
            Text(f"{_down_text(s.down)} & {s.distance}", style="bold yellow"),
        )

        # Spot
        table.add_row(
            Text("Ball On", style="dim"),
            Text(_yard_descriptor(s.yard_line), style="bold cyan"),
        )

        # Optional: you could add drive number, play count, etc later.

        return Panel(
            table,
            title="Situation",
            border_style="bright_blue",
            padding=(1, 1),
        )
