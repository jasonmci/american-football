from __future__ import annotations

from typing import Literal, Optional, TypeVar

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widget import Widget
from textual import events

from football.engine.game_state import GameState, Side
from football.engine.play_call import (
    PersonnelGroup,
    OffensePlayType,
    OffensivePlayCall,
    PlayDirection,
    PassDepth,
    TargetType,
    DefenseFront,
    DefensePlayFlavor,
    CoverageShell,
    DefensivePlayCall,
)

T = TypeVar("T")


def _cycle(values: list[T], current: T, step: int = 1) -> T:
    if not values:
        raise ValueError("No values to cycle.")
    i = values.index(current) if current in values else 0
    return values[(i + step) % len(values)]


def _fmt_enum(e) -> str:
    return e.name.replace("_", " ").title()


class PlaycallPanel(Widget):
    can_focus = True

    def __init__(self, team_side: Side, **kwargs) -> None:
        super().__init__(**kwargs)
        self.team_side = team_side
        self.mode: Literal["OFFENSE", "DEFENSE"] = "OFFENSE"

        # OFFENSE defaults
        self.off_personnel: PersonnelGroup = PersonnelGroup.P11
        self.off_play_type: OffensePlayType = OffensePlayType.INSIDE_ZONE
        self.off_direction: Optional[PlayDirection] = PlayDirection.MIDDLE
        self.off_pass_depth: Optional[PassDepth] = None
        self.off_primary_target: Optional[TargetType] = None

        # DEFENSE defaults
        self.def_front: DefenseFront = DefenseFront.FOUR_THREE
        self.def_flavor: DefensePlayFlavor = DefensePlayFlavor.BASE
        self.def_coverage: CoverageShell = CoverageShell.COVER_2

    # ---------- Build engine calls ----------

    def set_offense(self) -> None:
        self.mode = "OFFENSE"
        self.refresh()

    def set_defense(self) -> None:
        self.mode = "DEFENSE"
        self.refresh()

    def toggle_mode(self) -> None:
        self.mode = "DEFENSE" if self.mode == "OFFENSE" else "OFFENSE"
        self.refresh()

    def apply_offense_selection(
        self,
        *,
        personnel=None,
        play_type=None,
        direction=None,
        primary_target=None,
        pass_depth=None,
    ) -> None:
        """Optionally set current offense selections (used by app sync)."""
        if personnel is not None:
            self.off_personnel = personnel
        if play_type is not None:
            self.off_play_type = play_type
        if direction is not None:
            self.off_direction = direction
        if primary_target is not None:
            self.off_primary_target = primary_target
        if pass_depth is not None:
            self.off_pass_depth = pass_depth
        self.refresh()

    def get_offensive_play_call(self, state: GameState) -> OffensivePlayCall:
        # (Optional) infer pass depth for some pass types if unset
        pass_depth = self.off_pass_depth
        if pass_depth is None:
            name = self.off_play_type.name
            if "QUICK" in name or "SCREEN" in name:
                pass_depth = PassDepth.QUICK
            elif name in ("DIG", "COMEBACK", "DEEP_OUT", "CROSSERS", "MESH", "SEAM"):
                pass_depth = PassDepth.INTERMEDIATE
            elif name in ("GO", "POST", "CORNER", "FADE", "DEEP_CROSS") or "SHOT" in name:
                pass_depth = PassDepth.DEEP
            elif "PLAY_ACTION" in name:
                pass_depth = PassDepth.INTERMEDIATE

        return OffensivePlayCall(
            side=self.team_side,
            personnel=self.off_personnel,
            play_type=self.off_play_type,
            direction=self.off_direction,
            pass_depth=pass_depth,
            primary_target=self.off_primary_target,
        )

    def get_defensive_play_call(self, state: GameState) -> DefensivePlayCall:
        return DefensivePlayCall(
            side=self.team_side,
            front=self.def_front,
            flavor=self.def_flavor,
            coverage=self.def_coverage,
        )

    def apply_offense_playbook_selection(
        self,
        personnel: PersonnelGroup,
        play_type: OffensePlayType,
        direction: PlayDirection | None = None,
        target: TargetType | None = None,
        depth: PassDepth | None = None,
    ) -> None:
        """Apply a play chosen from the Offense playbook tab."""
        self.off_personnel = personnel
        self.off_play_type = play_type

        if direction is not None:
            self.off_direction = direction
        if target is not None:
            self.off_primary_target = target
        if depth is not None:
            self.off_pass_depth = depth

        self.refresh()

    def apply_defense_playbook_selection(
        self,
        front: DefenseFront,
        flavor: DefensePlayFlavor,
        coverage: CoverageShell,
    ) -> None:
        self.def_front = front
        self.def_flavor = flavor
        self.def_coverage = coverage
        self.refresh()

    # ---------- Input handling ----------

    def on_key(self, event: events.Key) -> None:
        key = event.key

        if key == "tab":
            self.mode = "DEFENSE" if self.mode == "OFFENSE" else "OFFENSE"
            self.refresh()
            event.stop()
            return

        if key == "p":
            self.off_personnel = _cycle(list(PersonnelGroup), self.off_personnel)
            self.refresh()
            event.stop()
            return

        if key == "t":
            self.off_play_type = _cycle(list(OffensePlayType), self.off_play_type)
            # wipe target/depth if switching between run/pass concepts
            self.off_primary_target = None
            self.off_pass_depth = None
            self.refresh()
            event.stop()
            return

        if key == "r":
            self.def_front = _cycle(list(DefenseFront), self.def_front)
            self.refresh()
            event.stop()
            return

        if key == "f":
            self.def_flavor = _cycle(list(DefensePlayFlavor), self.def_flavor)
            self.refresh()
            event.stop()
            return

        if key == "c":
            self.def_coverage = _cycle(list(CoverageShell), self.def_coverage)
            self.refresh()
            event.stop()
            return

        if key in ("1", "2", "3"):
            self.off_direction = {
                "1": PlayDirection.LEFT,
                "2": PlayDirection.MIDDLE,
                "3": PlayDirection.RIGHT,
            }[key]
            self.refresh()
            event.stop()
            return

        if key == "g":
            targets = [
                TargetType.RB1,
                TargetType.RB2,
                TargetType.WR1,
                TargetType.WR2,
                TargetType.WR3,
                TargetType.WR4,
                TargetType.TE1,
                TargetType.TE2,
                TargetType.QB,
            ]
            cur = self.off_primary_target or targets[0]
            self.off_primary_target = _cycle(targets, cur)
            self.refresh()
            event.stop()
            return

    # ---------- Render ----------

    def render(self) -> Panel:
        title = f"{self.team_side.value} ({self.mode})"

        border = "bright_magenta" if self.has_focus else "magenta"

        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="left", ratio=2)

        if self.mode == "OFFENSE":
            table.add_row("Personnel", Text(self.off_personnel.value, style="bold"))
            table.add_row("Play", Text(_fmt_enum(self.off_play_type), style="bold"))
            table.add_row("Direction", Text(_fmt_enum(self.off_direction) if self.off_direction else "—"))
            table.add_row("Target", Text(_fmt_enum(self.off_primary_target) if self.off_primary_target else "—"))
            table.add_row("Depth", Text(_fmt_enum(self.off_pass_depth) if self.off_pass_depth else "auto", style="dim"))

            hints = Text("P=Personnel  T=Play  1/2/3=Dir  G=Target", style="dim")

        else:  # DEFENSE
            table.add_row("Front", Text(_fmt_enum(self.def_front), style="bold"))
            table.add_row("Flavor", Text(_fmt_enum(self.def_flavor), style="bold"))
            table.add_row("Coverage", Text(_fmt_enum(self.def_coverage), style="bold"))

            hints = Text("R=Front  F=Flavor  C=Coverage", style="dim")

        body = Table.grid(expand=True)
        body.add_row(table)
        body.add_row(hints)

        return Panel(
            body,
            title=title,
            border_style=border,
            padding=(1, 2),
        )
