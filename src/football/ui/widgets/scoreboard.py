from __future__ import annotations
from typing import Optional

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from football.engine.game_state import GameState


class Scoreboard(Static):
    """Top-center scoreboard showing score by quarter and total with possession + timeouts."""

    def __init__(self, *, state: Optional[GameState] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = state

    def set_state(self, state: GameState) -> None:
        self._state = state
        self.refresh()

    # helper to render "🏈 HOME ●●●"
    def _team_cell(self, name: str, has_ball: bool, timeouts: int) -> Text:
        text = Text()

        # possession icon
        if has_ball:
            text.append("🏈 ", style="yellow")
        else:
            text.append("   ")

        # team name
        text.append(name, style="bold")

        # timeouts: 3 dots, green for remaining, dim for spent
        text.append("  ")
        for i in range(3):
            if i < timeouts:
                text.append("● ", style="green")
            else:
                text.append("● ", style="dim")

        return text

    def render(self) -> Panel:
        s = self._state

        # --- Header: Quarter + Clock ---
        clock_min = s.time_remaining // 60
        clock_sec = s.time_remaining % 60
        clock_str = f"{clock_min:02d}:{clock_sec:02d}"

        header = Text(justify="center")
        header.append(f"Q{s.quarter}  ", style="bold cyan")
        header.append(clock_str, style="bold yellow")

        # --- Create the box score table ---
        # No TEAM header, clean layout
        table = Table(
            expand=True,
            show_header=True,
            show_lines=False,
            box=None,  # no heavy borders
            pad_edge=False,
        )

        # Quarter headings only
        table.add_column("", justify="left")  # (team cell with possession + timeouts)
        table.add_column("Q1", justify="center")
        table.add_column("Q2", justify="center")
        table.add_column("Q3", justify="center")
        table.add_column("Q4", justify="center")
        table.add_column("OT", justify="center")
        table.add_column("TOT", justify="center", style="bold")

        s = self._state

        aq = list(s.scores.away)
        hq = list(s.scores.home)

        # Make sure we have at least 4 quarters (Q1–Q4); fill missing with 0
        while len(hq) < 5:
            hq.append(0)
        while len(aq) < 5:
            aq.append(0)

        # If you only show 4 quarters, ignore OT here:
        hq4 = hq[:5]
        aq4 = aq[:5]

        home_total = s.home_score_total()
        away_total = s.away_score_total()

        away_label = s.away_abbr  # "DAL"
        home_label = s.home_abbr  # "BAL"

        # Prepare team cells
        away_cell = self._team_cell(
            away_label,
            has_ball=(s.possession == "AWAY"),
            timeouts=s.away_timeouts,
        )
        home_cell = self._team_cell(
            home_label,
            has_ball=(s.possession == "HOME"),
            timeouts=s.home_timeouts,
        )

        # --- Add rows: AWAY first, HOME second ---
        table.add_row(
            away_label,
            str(aq4[0]), str(aq4[1]), str(aq4[2]), str(aq4[3]), str(aq4[4]),
            str(s.away_score_total()),
        )

        table.add_row(
            home_label,
            str(hq4[0]), str(hq4[1]), str(hq4[2]), str(hq4[3]), str(hq4[4]),
            str(s.home_score_total()),
        )

        # --- Soft separator between column headings and team rows ---
        # This goes *inside* the main layout, not inside the table.
        separator = Text("─" * 40, style="dim", justify="center")

        # --- Stack the scoreboard: header, table headings, separator, table rows ---
        layout = Table.grid(expand=True, pad_edge=False)
        layout.add_row(header)
        layout.add_row(separator)
        layout.add_row(table)

        return Panel(
            layout,
            title="Scoreboard",
            border_style="bright_green",
            padding=(1, 2),
        )
