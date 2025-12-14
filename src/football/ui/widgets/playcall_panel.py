from __future__ import annotations
from typing import Optional, Literal

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from football.engine.tokens import PlayType, Focus
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


class PlaycallPanel(Static):
    """Top-row panel for a team, which can show / edit both offensive and defensive calls."""

    def __init__(self, team: str, team_side: Side, **kwargs) -> None:
        super().__init__(**kwargs)
        self.team = team
        self.team_side = team_side  # Side.HOME or Side.AWAY

        # UI mode: what are we currently editing / showing?
        self.mode: Literal["OFFENSE", "DEFENSE"] = "OFFENSE"

        # --- Offense selection state (with sensible defaults) ---
        self.off_personnel: PersonnelGroup = PersonnelGroup.P11
        self.off_play_type: OffensePlayType = OffensePlayType.INSIDE_RUN
        self.off_direction: PlayDirection | None = None
        self.off_pass_depth: PassDepth | None = None
        self.off_primary_target: TargetType | None = None

        # --- Defense selection state (with sensible defaults) ---
        self.def_front: DefenseFront = DefenseFront.BASE
        self.def_flavor: DefensePlayFlavor = DefensePlayFlavor.BASE
        self.def_coverage: CoverageShell = CoverageShell.COVER_2

        # you probably already call something like self.update() in on_mount or similar

    # -------- Engine wiring helpers --------

    def get_offensive_play_call(self, state: GameState) -> OffensivePlayCall:
        """Build an OffensivePlayCall from the current offensive selection for this team."""

        # If you want to infer pass depth from play type, you can do that here;
        # for now we just pass through whatever is set (can be None).
        return OffensivePlayCall(
            side=self.team_side,
            personnel=self.off_personnel,
            play_type=self.off_play_type,
            direction=self.off_direction,
            pass_depth=self.off_pass_depth,
            target=self.off_primary_target,
            token_id=None,  # hook up Techno-Bowl tokens later
        )

    def get_defensive_play_call(self, state: GameState) -> DefensivePlayCall:
        """Build a DefensivePlayCall from the current defensive selection for this team."""

        return DefensivePlayCall(
            side=self.team_side,
            front=self.def_front,
            flavor=self.def_flavor,
            coverage=self.def_coverage,
            token_id=None,
        )

    # --- Public API to set state ---

    def set_offense(self, *, play_type: PlayType, target: str, direction: Optional[str]) -> None:
        self._mode = "OFFENSE"
        self._off_play_type = play_type
        self._off_target = target
        self._off_direction = direction
        self.refresh()

    def set_defense(
        self,
        *,
        focus: Focus,
        blitz: bool,
        key_target: Optional[str],
        shift_direction: Optional[str],
    ) -> None:
        self._mode = "DEFENSE"
        self._def_focus = focus
        self._def_blitz = blitz
        self._def_key_target = key_target
        self._def_shift_direction = shift_direction
        self.refresh()

    # --- Rendering ---

    def render(self) -> Panel:
        if self._mode == "OFFENSE":
            content = self._render_offense()
            title = f"{self.team} Playcall (OFFENSE)"
        else:
            content = self._render_defense()
            title = f"{self.team} Playcall (DEFENSE)"

        return Panel(
            content,
            title=title,
            border_style="magenta" if self._mode == "OFFENSE" else "blue",
            padding=(1, 2),
        )

    def _render_offense(self) -> Table:
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right", ratio=1)

        table.add_row(
            Text("Play Type", style="bold"),
            Text(self._off_play_type.name, style="bold yellow"),
        )
        table.add_row(
            Text("Target", style="bold"),
            Text(self._off_target, style="bold magenta"),
        )
        table.add_row(
            Text("Direction", style="bold"),
            Text(self._off_direction or "N/A", style="bold cyan"),
        )

        hints = Text.from_markup(
            "Keys: [dim]\n[/dim]"
            "[bold]1[/bold]=Play Type  "
            "[bold]2[/bold]=Target  "
            "[bold]3[/bold]=Direction  "
            "[bold]Space[/bold]=Call Play"
        )

        layout = Table.grid(expand=True)
        layout.add_row(table)
        layout.add_row(hints)

        return layout

    def _render_defense(self) -> Table:
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right", ratio=1)

        table.add_row(
            Text("Focus", style="bold"),
            Text(self._def_focus.name, style="bold yellow"),
        )
        table.add_row(
            Text("Blitz", style="bold"),
            Text(
                "YES" if self._def_blitz else "NO", style="bold red" if self._def_blitz else "dim"
            ),
        )
        table.add_row(
            Text("Key", style="bold"),
            Text(self._def_key_target or "NONE", style="bold magenta"),
        )
        table.add_row(
            Text("Shift", style="bold"),
            Text(self._def_shift_direction or "NONE", style="bold cyan"),
        )

        info = Text()
        info.append("Defense is AI-controlled for now.\n", style="dim")
        info.append("Future: call defensive tokens here.", style="dim")

        layout = Table.grid(expand=True)
        layout.add_row(table)
        layout.add_row(info)

        return layout
