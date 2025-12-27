from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import events
from textual.widgets import Static
from textual.message import Message
from football.engine.play_call import PassDepth, PersonnelGroup, OffensePlayType, PlayDirection, TargetType
from football.playbooks.offense_cards_default import OFFENSIVE_CARDS


class OffensePlaySelected(Message):
    """Sent when user selects a play from the Offense playbook tab."""

    def __init__(
        self,
        personnel: PersonnelGroup,
        play_type: OffensePlayType,
        direction: PlayDirection | None = None,
        target: TargetType | None = None,
        depth: PassDepth | None = None,
    ) -> None:
        super().__init__()
        self.personnel = personnel
        self.play_type = play_type
        self.direction = direction
        self.target = target
        self.depth = depth


class FocusCol(Enum):
    PERSONNEL = auto()
    PLAY = auto()


def _fmt_enum_name(name: str) -> str:
    return name.replace("_", " ").title()


def _core_family_for_play_name(play_name: str) -> str:
    n = play_name.upper()

    if n in ("SPIKE",):
        return "SPIKE"
    if n in ("KNEEL", "QB_KNEEL"):
        return "KNEEL"
    if "SCREEN" in n:
        return "SCREEN_PASS"
    if "PLAY_ACTION" in n or n in ("BOOTLEG", "ROLL_OUT"):
        return "PLAY_ACTION"

    if any(k in n for k in ("INSIDE", "POWER", "COUNTER", "TRAP", "ISO", "DRAW", "DELAY")):
        return "INSIDE_RUN"
    if any(k in n for k in ("OUTSIDE", "SWEEP", "TOSS", "JET", "REVERSE")):
        return "OUTSIDE_RUN"
    if any(k in n for k in ("OPTION", "KEEPER", "QB_")):
        return "OPTION_RUN"

    if any(k in n for k in ("QUICK", "HITCH", "SLANT", "BUBBLE", "SMOKE")):
        return "QUICK_PASS"
    if any(k in n for k in ("MESH", "OUT", "CROSS", "SEAM")):
        return "SHORT_PASS"
    if any(k in n for k in ("DIG", "COMEBACK", "DEEP_OUT", "CROSSERS")):
        return "INTERMEDIATE_PASS"
    if any(k in n for k in ("GO", "POST", "CORNER", "FADE", "DEEP")):
        return "DEEP_PASS"

    return "SHORT_PASS"


def _p_code(n: int) -> str:
    return f"P{n:02d}"


@dataclass(frozen=True, slots=True)
class PersonnelRow:
    code: str
    group: PersonnelGroup | None  # None if not implemented in OFFENSIVE_CARDS yet
    enabled: bool


class OffensePlaybookView(Static):
    can_focus = True

    DEFAULT_CSS = """
    OffensePlaybookView {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.focus_col: FocusCol = FocusCol.PERSONNEL

        # Build from enum: only real personnel packages exist here
        self.personnel_rows: list[PersonnelRow] = []

        # Ensure stable order (P00, P01, ... P11, P12, ...), assuming enum names like "P11"
        groups = sorted(
            list(PersonnelGroup),
            key=lambda g: int(g.name[1:]) if g.name.startswith("P") and g.name[1:].isdigit() else 999,
        )

        for g in groups:
            code = g.name  # e.g. "P11"
            enabled = g in OFFENSIVE_CARDS  # has a card right now
            self.personnel_rows.append(PersonnelRow(code=code, group=g, enabled=enabled))

        # Default selection = P11 if it exists, otherwise first enabled, otherwise first row
        self.personnel_index = 0
        for i, row in enumerate(self.personnel_rows):
            if row.group is not None and row.group.name == "P11":
                self.personnel_index = i
                break
        else:
            for i, row in enumerate(self.personnel_rows):
                if row.enabled:
                    self.personnel_index = i
                    break

        self.play_index = 0

    def on_mount(self) -> None:
        self.styles.height = "1fr"
        self.styles.width = "1fr"
        self.refresh()

    # --------- helpers ---------

    def _selected_personnel_row(self) -> PersonnelRow:
        return self.personnel_rows[self.personnel_index]

    def _selected_personnel_group(self) -> PersonnelGroup | None:
        row = self._selected_personnel_row()
        return row.group if row.enabled else None

    def _plays_for_selected(self):
        group = self._selected_personnel_group()
        if group is None:
            return []
        card = OFFENSIVE_CARDS.get(group)
        if card is None:
            return []
        return list(card.plays)

    # --------- input ---------

    def on_key(self, event: events.Key) -> None:
        k = event.key

        if k == "tab":
            self.focus_col = FocusCol.PLAY if self.focus_col == FocusCol.PERSONNEL else FocusCol.PERSONNEL
            self.refresh()
            event.stop()
            return

        if k in ("up", "k"):
            if self.focus_col == FocusCol.PERSONNEL:
                self.personnel_index = max(0, self.personnel_index - 1)
                self.play_index = 0
            else:
                self.play_index = max(0, self.play_index - 1)
            self.refresh()
            event.stop()
            return

        if k in ("down", "j"):
            if self.focus_col == FocusCol.PERSONNEL:
                self.personnel_index = min(len(self.personnel_rows) - 1, self.personnel_index + 1)
                self.play_index = 0
            else:
                plays = self._plays_for_selected()
                if plays:
                    self.play_index = min(len(plays) - 1, self.play_index + 1)
            self.refresh()
            event.stop()
            return

        if k == "enter":
            if self.focus_col == FocusCol.PERSONNEL:
                # Lock personnel, jump to play selection
                self.play_index = 0
                self.focus_col = FocusCol.PLAY
                self.refresh()
                event.stop()
                return

            if self.focus_col == FocusCol.PLAY:
                group = self._selected_personnel_group()
                if group is None:
                    event.stop()
                    return

                plays = self._plays_for_selected()
                if not plays:
                    event.stop()
                    return

                opt = plays[self.play_index]

                self.post_message(
                    OffensePlaySelected(
                        personnel=group,
                        play_type=opt.play_type,
                        direction=getattr(opt, "default_direction", None),
                        target=getattr(opt, "default_target", None),
                        depth=getattr(opt, "default_depth", None),
                    )
                )
                event.stop()
                return

        # Quick jump: type 11/12/21 etc later. For now, support digits as fast jump:
        # Pressing "1" twice quickly would be nicer; keep simple for now.
        if self.focus_col == FocusCol.PERSONNEL and k.isdigit():
            # jump to P0x / Px? We'll make a proper 2-digit buffer later.
            target = int(k)
            if 0 <= target <= 32:
                self.personnel_index = target
                self.play_index = 0
                self.refresh()
                event.stop()
                return

    # --------- render ---------

    def render(self) -> Panel:
        DISABLED_STYLE = "dim"
        ACTIVE_MARK = "▶ "
        INACTIVE_MARK = "  "
        ACTIVE_STYLE = "reverse bold yellow"
        INACTIVE_STYLE = "reverse white on grey23"

        border = "bright_yellow" if self.focus_col == FocusCol.PLAY else "yellow"

        help_text = Text(
            "Tab: switch focus (Personnel/Play) • ↑/↓ or j/k: move • " "Disabled personnel are dim (no card yet)",
            style="dim",
        )

        # LEFT: personnel-only column
        left = Table(expand=False, show_header=True, header_style="bold")
        left.add_column("Personnel", no_wrap=True)

        for i, row in enumerate(self.personnel_rows):
            is_cursor = (i == self.personnel_index)
            enabled = row.enabled

            mark = INACTIVE_MARK
            style = ""

            if not enabled:
                style = DISABLED_STYLE

            if is_cursor:
                mark = ACTIVE_MARK if self.focus_col == FocusCol.PERSONNEL else INACTIVE_MARK
                style = ACTIVE_STYLE if self.focus_col == FocusCol.PERSONNEL else INACTIVE_STYLE

            left.add_row(Text(f"{mark}{row.code}", style=style))

        # RIGHT: plays for selected personnel
        plays = self._plays_for_selected()
        group = self._selected_personnel_group()

        right = Table(expand=True, show_header=True, header_style="bold")
        right.add_column("Play", ratio=3)
        right.add_column("Type", ratio=2, no_wrap=True)
        right.add_column("Notes", ratio=4)

        if group is None:
            right.add_row(
                Text("No playcalling card for this personnel yet.", style="dim"),
                Text(""),
                Text("Add a card in football/playbooks/offense_cards_default.py", style="dim"),
            )
        else:
            for idx, opt in enumerate(plays):
                play_type = opt.play_type
                key = getattr(play_type, "name", str(play_type))
                label = getattr(opt, "label", _fmt_enum_name(key))
                core = _core_family_for_play_name(key)
                notes = ", ".join(getattr(opt, "tags", ()))

                is_cursor = (idx == self.play_index)

                mark = INACTIVE_MARK
                row_style = ""

                if is_cursor:
                    mark = ACTIVE_MARK if self.focus_col == FocusCol.PLAY else INACTIVE_MARK
                    row_style = ACTIVE_STYLE if self.focus_col == FocusCol.PLAY else INACTIVE_STYLE

                right.add_row(
                    Text(f"{mark}{label}", style=row_style),
                    Text(core, style=row_style),
                    Text(notes if notes else "—", style=row_style or "dim"),
                )

        # Put left and right side-by-side
        main = Table.grid(expand=True)
        main.add_column(ratio=1)
        main.add_column(ratio=5)

        main.add_row(left, right)

        wrapper = Table.grid(expand=True)
        wrapper.add_row(help_text)
        wrapper.add_row(main)

        selected_code = self._selected_personnel_row().code
        title = f"Offensive Playbook — {selected_code}"

        return Panel(wrapper, title=title, border_style=border, padding=(1, 2))
