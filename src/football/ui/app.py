from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical

from football.engine.engine import resolve_play
from football.engine.game_state import GameState, Side
from football.engine.fac import FACDeck, FACCard
from football.engine.play_call import PlayCall
from football.engine.tokens import (
    PlayType,
    Focus,
    PlaycallOffense,
    PlaycallDefense,
)

from football.ui.widgets.scoreboard import Scoreboard
from football.ui.widgets.play_log import PlayLog
from football.ui.widgets.field_view import FieldView
from football.ui.widgets.playcall_panel import PlaycallPanel
from football.ui.widgets.current_drive import CurrentDrive
from football.ui.widgets.down_distance import DownDistance
from football.ui.theme import team_style


class FootballApp(App):
    """Main Textual UI for the american-football project."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "call_play", "Call Play"),
    ]

    TITLE = "American Football Hybrid Sim"
    SUB_TITLE = "Playcall UI Prototype"

    CSS = """
    Screen {
        layout: vertical;
        background: #001219;
        color: #f1faee;
    }

    /* Row heights */
    #top-row {
        height: 24%;
        layout: horizontal;
    }

    #middle-row {
        height: 46%;
        layout: horizontal;
        padding: 0 1;
    }

    #bottom-row {
        height: 30%;
    }

    /* Top row: AWAY | SCOREBOARD | HOME (same height) */
    #away-playcall, #scoreboard, #home-playcall {
        width: 1fr;
        height: 100%;
        padding: 1;
    }

    /* Middle row: left column (situation + drive) and right field */
    #situation-column {
        width: 1fr;
        align-vertical: top;
        padding: 0 1 0 0;
    }

    #situation {
        /* let content define height */
    }

    #current-drive {
        margin-top: 1;
    }

    #field {
        width: 126;      /* fixed to ASCII field width */
        height: 100%;
        padding: 0;
    }

    /* Bottom row: play log */
    #play-log {
        height: 100%;
        padding: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.state = GameState.initial(
            home_name="Baltimore Ravens",
            home_abbr="BAL",
            away_name="Dallas Cowboys",
            away_abbr="DAL",
            home_receives=True,
        )
        # Simple mock FAC deck for now
        self.fac_deck = FACDeck(
            [
                FACCard("R1", 30, "NONE", "NONE", {}),
                FACCard("P1", 10, "NONE", "NONE", {}),
                FACCard("R0", 30, "NONE", "NONE", {}),
                FACCard("P0", 10, "NONE", "NONE", {}),
            ]
        )

        # Offensive playcall state (for the team currently on offense)
        self._play_types = [PlayType.RUN, PlayType.SHORT_PASS, PlayType.LONG_PASS, PlayType.SCREEN]
        self._targets = ["RB1", "WR1", "TE1"]
        self._directions = ["LEFT", "MIDDLE", "RIGHT"]

        self._play_type_index = 0
        self._target_index = 0
        self._direction_index = 1  # default MIDDLE

        # Last defensive call (used to display in DEF panels)
        self._last_defense_call: PlaycallDefense = PlaycallDefense(focus=Focus.BALANCED)

        # Widgets (set in compose)
        self.scoreboard: Scoreboard
        self.field_view: FieldView
        self.play_log: PlayLog
        self.home_panel: PlaycallPanel
        self.away_panel: PlaycallPanel

    def compose(self) -> ComposeResult:
        # Top row: AWAY playcall | SCOREBOARD | HOME playcall
        with Vertical():
            with Horizontal(id="top-row"):
                self.away_panel = PlaycallPanel(team="AWAY", team_side=Side.AWAY, id="away-playcall")
                yield self.away_panel

                self.scoreboard = Scoreboard(id="scoreboard", state=self.state)
                yield self.scoreboard

                self.home_panel = PlaycallPanel(team="HOME", team_side=Side.HOME, id="home-playcall")
                yield self.home_panel

            # Middle row: left (situation + current drive), right (field)
            with Horizontal(id="middle-row"):
                with Vertical(id="situation-column"):
                    self.situation = DownDistance(id="situation", state=self.state)
                    yield self.situation

                    self.current_drive = CurrentDrive(id="current-drive", state=self.state)
                    yield self.current_drive

                self.field_view = FieldView(id="field", state=self.state)
                yield self.field_view

            # Bottom row: play log
            with Vertical(id="bottom-row"):
                self.play_log = PlayLog(id="play-log")
                yield self.play_log

    def on_mount(self) -> None:
        self.play_log.add_line("Welcome! Use 1/2/3 to adjust play, Space to call a play.")
        self._update_all_stateful_widgets()
        self._update_playcall_panels()

    # --- Helpers ---

    def _current_playcall(self) -> PlaycallOffense:
        return PlaycallOffense(
            play_type=self._play_types[self._play_type_index],
            target=self._targets[self._target_index],
            direction=self._directions[self._direction_index],
        )

    def _update_playcall_panels(self) -> None:
        """Update left/right panels based on who has possession."""
        off_call = self._current_playcall()
        deff = self._last_defense_call

        if self.state.possession == "HOME":
            # Home is offense, away is defense
            self.home_panel.set_offense(
                play_type=off_call.play_type,
                target=off_call.target,
                direction=off_call.direction,
            )
            self.away_panel.set_defense(
                focus=deff.focus,
                blitz=deff.blitz,
                key_target=deff.key_target,
                shift_direction=deff.shift_direction,
            )
        else:
            # Away is offense, home is defense
            self.away_panel.set_offense(
                play_type=off_call.play_type,
                target=off_call.target,
                direction=off_call.direction,
            )
            self.home_panel.set_defense(
                focus=deff.focus,
                blitz=deff.blitz,
                key_target=deff.key_target,
                shift_direction=deff.shift_direction,
            )

    def _update_all_stateful_widgets(self) -> None:
        self.scoreboard.set_state(self.state)
        self.field_view.set_state(self.state)
        self.situation.set_state(self.state)
        self.current_drive.set_state(self.state)

    # --- Key handling: playcall UI ---

    def on_key(self, event) -> None:
        key = event.key

        if key == "1":
            # cycle play type
            self._play_type_index = (self._play_type_index + 1) % len(self._play_types)
            self._update_playcall_panels()
        elif key == "2":
            # cycle target
            self._target_index = (self._target_index + 1) % len(self._targets)
            self._update_playcall_panels()
        elif key == "3":
            # cycle direction
            self._direction_index = (self._direction_index + 1) % len(self._directions)
            self._update_playcall_panels()
        elif key == " ":
            # call the play
            off = self._current_playcall()
            deff = self._simple_defense_ai(off)
            self._last_defense_call = deff

            result = resolve_play(self.state, off, deff, self.fac_deck)
            self.state = result.new_state

            self._update_all_stateful_widgets()
            self._update_playcall_panels()
            self.play_log.add_line(result.description)

    def action_call_play(self) -> None:
        """Triggered when the user presses Space.

        This should gather the current play selections and resolve a play.
        """
        self._call_play()

    def _simple_defense_ai(self, off: PlaycallOffense) -> PlaycallDefense:
        """Very dumb AI just to have something to play against."""
        if off.play_type == PlayType.RUN:
            focus = Focus.RUN
        else:
            focus = Focus.PASS

        # For now, no blitz, no key, no shift
        return PlaycallDefense(
            focus=focus,
            blitz=False,
            key_target=None,
            shift_direction=None,
        )

    def _call_play(self) -> None:
        """Collect current offensive and defensive play calls and hand them to the engine.

        For now, we just build a PlayCall and log it; the real yardage/clock/score
        logic will live in engine.resolve_play soon.
        """

        s = self.state
        offense_side: Side = s.possession
        defense_side: Side = Side.HOME if offense_side is Side.AWAY else Side.AWAY

        # Build calls based on which panel is on offense / defense this play
        if offense_side is Side.HOME:
            offense_call = self.home_panel.get_offensive_play_call(s)
            defense_call = self.away_panel.get_defensive_play_call(s)
        else:
            offense_call = self.away_panel.get_offensive_play_call(s)
            defense_call = self.home_panel.get_defensive_play_call(s)

        play_call = PlayCall(offense=offense_call, defense=defense_call)

        new_state, result = resolve_play(s, play_call)

        off_abbr = self.state.home_abbr if offense_side.name == "HOME" else self.state.away_abbr
        def_abbr = self.state.home_abbr if defense_side.name == "HOME" else self.state.away_abbr

        off_tag = f"[{team_style(off_abbr)}]{off_abbr}[/]"
        def_tag = f"[{team_style(def_abbr)}]{def_abbr}[/]"

        # Update app state
        self.state = new_state

        # TODO: plug into engine.resolve_play(self.state, play_call, rng)
        # For now, just show that it works and avoid any crashes regardless of choices.

        # Trivial dummy state update: advance play count so drive panel visibly changes soon.
        # self.state = s.copy(current_drive_play_count=s.current_drive_play_count + 1)

        self._update_all_stateful_widgets()

        # Log what was called for debugging
        off = play_call.offense
        deff = play_call.defense

        line = f"{off_tag} [dim]OFF[/dim]: {off.play_type.name} ({off.personnel.value})"

        if off.direction:
            line += f" {off.direction.name}"
        if off.target:
            line += f" → {off.target.name}"

        line += (
            f"  [dim]|[/dim]  {def_tag} [dim]DEF[/dim]: "
            f"{deff.front.name}, {deff.flavor.name}, {deff.coverage.name}"
        )

        yards = result.yards_gained
        yards_style = "bold green" if yards > 0 else "bold red" if yards < 0 else "bold yellow"
        line += f"  [dim]→[/dim] [{yards_style}]{yards:+d}y[/{yards_style}]"

        # Situational info
        line += (
            f"  [dim]({new_state.down}&{new_state.distance} "
            f"at {'OWN' if new_state.possession == off.side else 'THEIR'} "
            f"{new_state.yard_line})[/dim]"
        )

        if result.touchdown:
            line += "  [bold magenta]TD![/bold magenta]"
        elif result.first_down:
            line += "  [bold cyan]1st[/bold cyan]"

        self.play_log.add_line(line)


def run() -> None:
    app = FootballApp()
    app.run()
