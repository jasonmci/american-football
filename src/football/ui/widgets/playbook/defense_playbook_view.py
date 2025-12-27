from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import events
from textual.message import Message
from textual.widgets import Static

from football.engine.play_call import DefenseFront, DefensePlayFlavor, CoverageShell
from football.playbooks.defense_cards_default import DEFENSIVE_CARDS


class FocusCol(Enum):
    PACKAGE = auto()
    CALL = auto()


ACTIVE_MARK = "▶ "
INACTIVE_MARK = "▸ "
ACTIVE_STYLE = "reverse bold yellow"
INACTIVE_STYLE = "reverse yellow"
DISABLED_STYLE = "dim"


@dataclass(frozen=True, slots=True)
class FrontRow:
    front: DefenseFront
    enabled: bool


class DefensePlaySelected(Message):
    """Sent when user selects a defensive call from the Defense playbook tab."""

    def __init__(self, front: DefenseFront, flavor: DefensePlayFlavor, coverage: CoverageShell) -> None:
        super().__init__()
        self.front = front
        self.flavor = flavor
        self.coverage = coverage


def _fmt_enum(e) -> str:
    return e.name.replace("_", " ").title()


class DefensePlaybookView(Static):
    can_focus = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.focus_col: FocusCol = FocusCol.PACKAGE

        fronts = list(DefenseFront)
        self.front_rows = [FrontRow(front=f, enabled=True) for f in fronts]

        # Default package: NICKEL if exists, else FOUR_THREE, else first
        self.front_index = 0
        preferred = [DefenseFront.NICKEL, DefenseFront.FOUR_THREE, DefenseFront.THREE_FOUR]
        for p in preferred:
            for i, r in enumerate(self.front_rows):
                if r.front == p:
                    self.front_index = i
                    break

        self.call_index = 0

    def _selected_front(self) -> DefenseFront:
        return self.front_rows[self.front_index].front

    def _calls_for_selected(self):
        card = DEFENSIVE_CARDS.get(self._selected_front())
        if not card:
            return []
        return list(card.calls)

    def on_key(self, event: events.Key) -> None:
        k = event.key

        if k == "tab":
            self.focus_col = FocusCol.CALL if self.focus_col == FocusCol.PACKAGE else FocusCol.PACKAGE
            self.refresh()
            event.stop()
            return

        if k in ("up", "k"):
            if self.focus_col == FocusCol.PACKAGE:
                self.front_index = max(0, self.front_index - 1)
                self.call_index = 0
            else:
                self.call_index = max(0, self.call_index - 1)
            self.refresh()
            event.stop()
            return

        if k in ("down", "j"):
            if self.focus_col == FocusCol.PACKAGE:
                self.front_index = min(len(self.front_rows) - 1, self.front_index + 1)
                self.call_index = 0
            else:
                calls = self._calls_for_selected()
                if calls:
                    self.call_index = min(len(calls) - 1, self.call_index + 1)
            self.refresh()
            event.stop()
            return

        if k == "enter":
            if self.focus_col == FocusCol.PACKAGE:
                self.call_index = 0
                self.focus_col = FocusCol.CALL
                self.refresh()
                event.stop()
                return

            if self.focus_col == FocusCol.CALL:
                calls = self._calls_for_selected()
                if not calls:
                    event.stop()
                    return
                c = calls[self.call_index]
                self.post_message(DefensePlaySelected(front=c.front, flavor=c.flavor, coverage=c.coverage))
                event.stop()
                return

    def render(self) -> Panel:
        border = "bright_yellow" if self.has_focus else "magenta"

        help_text = Text(
            "↑/↓ or j/k: move • Tab: switch column • Enter: select package → call",
            style="dim",
        )

        # LEFT: packages/fronts
        left = Table(expand=False, show_header=True, header_style="bold")
        left.add_column("Package", no_wrap=True)

        for i, row in enumerate(self.front_rows):
            is_cursor = i == self.front_index
            mark = INACTIVE_MARK
            style = ""

            if is_cursor:
                mark = ACTIVE_MARK if self.focus_col == FocusCol.PACKAGE else INACTIVE_MARK
                style = ACTIVE_STYLE if self.focus_col == FocusCol.PACKAGE else INACTIVE_STYLE

            left.add_row(Text(f"{mark}{_fmt_enum(row.front)}", style=style))

        # RIGHT: calls
        calls = self._calls_for_selected()
        card = DEFENSIVE_CARDS.get(self._selected_front())

        right = Table(expand=True, show_header=True, header_style="bold")
        right.add_column("Call", ratio=3)
        right.add_column("Coverage", ratio=2, no_wrap=True)
        right.add_column("Notes", ratio=4)

        if not card:
            right.add_row(Text("No card found for this package.", style="dim"), Text(""), Text(""))
        else:
            for idx, opt in enumerate(calls):
                is_cursor = idx == self.call_index
                mark = INACTIVE_MARK
                row_style = ""

                if is_cursor:
                    mark = ACTIVE_MARK if self.focus_col == FocusCol.CALL else INACTIVE_MARK
                    row_style = ACTIVE_STYLE if self.focus_col == FocusCol.CALL else INACTIVE_STYLE

                notes = ", ".join(opt.tags) if opt.tags else "—"
                right.add_row(
                    Text(f"{mark}{opt.label} ({_fmt_enum(opt.flavor)})", style=row_style),
                    Text(_fmt_enum(opt.coverage), style=row_style),
                    Text(notes, style=row_style or "dim"),
                )

        main = Table.grid(expand=True)
        main.add_column(ratio=1)
        main.add_column(ratio=5)
        main.add_row(left, right)

        wrapper = Table.grid(expand=True)
        wrapper.add_row(help_text)
        wrapper.add_row(main)

        title = f"Defensive Playbook — {_fmt_enum(self._selected_front())}"
        return Panel(wrapper, title=title, border_style=border, padding=(1, 2))
