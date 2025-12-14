from __future__ import annotations

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from textual.widgets import Static

from football.engine.game_state import GameState

TEAM_PALETTE: dict[str, tuple[str, str]] = {
    # code: (fg, bg)
    "BAL": ("gold1", "purple4"),
    "SFO": ("red3", "grey85"),
    "S-F": ("red3", "grey85"),
    "NYG": ("blue3", "white"),
    "DAL": ("dodger_blue2", "white"),
    "G-B": ("green3", "gold1"),
    "K-C": ("red1", "gold1"),
}

FIELD_ART = """┌─────────┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬─────────┐
│ ▉ ▉ ▉ ▉ │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │  ◂1│0   │  ◂2│0   │  ◂3│0   │  ◂4│0   │  ◂5│0▸  │   4│0▸  │   3│0▸  │   2│0▸  │   1│0▸  │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │    │    │    │    │    │    │    │    │    │   NFL   │    │    │    │    │    │    │    │    │    │  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│||||│  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │  ◂1│0   │  ◂2│0   │  ◂3│0   │  ◂4│0   │  ◂5│0▸  │   4│0▸  │   3│0▸  │   2│0▸  │   1│0▸  │    │ ▉ ▉ ▉ ▉ │
│  ▉ ▉ ▉  │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │  ▉ ▉ ▉  │
│ ▉ ▉ ▉ ▉ │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │ ▉ ▉ ▉ ▉ │
└─────────┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴─────────┘"""


def _team_fg_bg(code: str) -> tuple[str, str]:
    code = (code or "").upper()
    return TEAM_PALETTE.get(code, ("white", "grey35"))


def _apply_midfield_logo(field_art: str, team_code: str) -> Text:
    """Return a Rich Text version of the field with a styled midfield logo.

    Looks for 'NFL' in the middle of the field and replaces JUST those 3 chars
    with a bold 3-letter team code (e.g. BAL), colored with fg/bg team colors.
    """
    lines = field_art.splitlines()
    rows: list[Text] = []

    team_code = (team_code or "").upper()[:3]
    fg, bg = _team_fg_bg(team_code)
    logo_style = f"bold {fg} on {bg}"

    for line in lines:
        if "NFL" in line:
            idx = line.index("NFL")
            before = line[:idx]
            after = line[idx+3:]

            # The field already has spaces around 'NFL', so we only swap the 3 letters.
            row = Text.assemble(
                before,
                (team_code, logo_style),
                after,
                no_wrap=True,
            )
        else:
            row = Text(line, no_wrap=True)

        rows.append(row)

    field_text = Text("\n").join(rows)
    field_text.no_wrap = True
    return field_text


class FieldView(Static):
    """Center widget showing the ASCII art field plus dynamic strips."""

    def __init__(self, *, state: GameState, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = state

    def set_state(self, state: GameState) -> None:
        self._state = state
        self.refresh()

    # --- helpers ---

    def _yard_descriptor_offense(self, yard_line: int) -> str:
        """Return 'OWN 35' or 'THEIR 35' from the offense perspective."""
        if yard_line <= 50:
            return f"OWN {yard_line}"
        else:
            return f"THEIR {100 - yard_line}"

    def _first_down_yard(self, s: GameState) -> int:
        """Compute first-down yard based on possession direction."""
        direction = 1 if s.possession == "HOME" else -1
        target = s.yard_line + direction * s.distance
        return max(0, min(100, target))

    def _top_strip(self, s: GameState) -> Text:
        """
        Calibrated strip:
        - Yellow triangle at OWN 25
        - Red triangle at OWN 35

        The ASCII field has an 11-character endzone before yard 0,
        so every yard marker must add +11.
        """

        lines = FIELD_ART.splitlines()
        first_line = lines[0]
        field_width = len(first_line)

        # CONSTANT — the left endzone size
        ENDZONE_OFFSET = 11  # yard 0 begins at column 11

        # Yard positions
        yellow_yard = 25
        red_yard = 35

        yellow_col = ENDZONE_OFFSET + yellow_yard
        red_col = ENDZONE_OFFSET + red_yard

        strip = Text(justify="left", no_wrap=True)

        for col in range(field_width):
            if col == yellow_col:
                strip.append("▼", style="bright_yellow")
            elif col == red_col:
                strip.append("▼", style="red3")
            else:
                strip.append(" ")

        return strip

    def _bottom_strip(self, s: GameState) -> Text:
        """
        Bottom strip aligned to the same yard column as the yellow arrow.

        For now:
        - Yellow arrow is at OWN 25 on the top strip.
        - We place 'OWN 25 ───▶' starting at that same column.
        """

        lines = FIELD_ART.splitlines()
        first_line = lines[0]
        field_width = len(first_line)

        ENDZONE_OFFSET = 11  # yard 0 begins at this column
        yellow_yard = 25  # matches the top-strip yellow marker

        # Column where the yellow arrow sits
        start_col = ENDZONE_OFFSET + yellow_yard

        # The label we want to render there
        label_text = "OWN 25 ───▶"
        label_len = len(label_text)

        # Compute spaces on left and right so the whole line matches field width
        left_spaces_count = max(0, start_col)
        right_spaces_count = max(0, field_width - left_spaces_count - label_len)

        strip = Text(justify="left", no_wrap=True)

        # Left padding
        strip.append(" " * left_spaces_count)

        # Label: bold text + green arrow
        # (we split so we can color the arrow)
        strip.append("OWN 25", style="bold")
        strip.append(" ───▶", style="bright_green")

        # Right padding
        strip.append(" " * right_spaces_count)

        return strip

    # --- rendering ---

    def render(self) -> Panel:
        s = self._state

        home_code = getattr(s, "home_abbr", "BAL")
        field_text = _apply_midfield_logo(FIELD_ART, home_code)
        top_strip = self._top_strip(s)
        bottom_strip = self._bottom_strip(s)

        layout = Table.grid(expand=True, pad_edge=False)
        layout.add_column(justify="center")
        layout.add_row(top_strip)
        layout.add_row(field_text)
        layout.add_row(bottom_strip)

        return Panel(
            layout,
            title="Field",
            border_style="green",
            padding=(0, 0),
        )
