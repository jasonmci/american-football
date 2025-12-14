from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from football.engine.game_state import GameState


class CurrentDrive(Static):
    """Panel showing information about the current offensive drive."""

    def __init__(self, *, state: GameState | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = state

    def set_state(self, state: GameState) -> None:
        self._state = state
        self.refresh()

    def render(self) -> Panel:
        # For now this is hard-coded demo data.
        # Later we can derive these from self._state / a Drive model.
        total_plays = 8
        runs = 5
        passes = 3
        yards = 42
        time_elapsed = "3:24"

        table = Table.grid(pad_edge=False)
        table.add_column(justify="left")
        table.add_column(justify="right")

        table.add_row(Text("Total Plays", style="dim"), Text(str(total_plays), style="bold"))
        table.add_row(Text("Runs", style="dim"), Text(str(runs), style="bold"))
        table.add_row(Text("Passes", style="dim"), Text(str(passes), style="bold"))
        table.add_row(Text("Total Yards", style="dim"), Text(f"{yards}", style="bold cyan"))
        table.add_row(Text("Time Elapsed", style="dim"), Text(time_elapsed, style="bold yellow"))

        return Panel(
            table,
            title="Current Drive",
            border_style="bright_magenta",
            padding=(1, 1),
        )
