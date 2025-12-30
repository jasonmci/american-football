from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import TabbedContent, TabPane
from football.engine.engine import resolve_play
from football.engine.game_state import GameState, Side
from football.engine.play_call import PlayCall
from football.ui.widgets.playbook.offense_playbook_view import OffensePlaybookView
from football.ui.widgets.playbook.defense_playbook_view import DefensePlaybookView
from football.ui.theme import team_style

# --- Widgets (adjust import paths if your filenames differ) ---
from football.ui.widgets.playcall_panel import PlaycallPanel
from football.ui.widgets.scoreboard import Scoreboard
from football.ui.widgets.field_view import FieldView
from football.ui.widgets.down_distance import DownDistance
from football.ui.widgets.current_drive import CurrentDrive
from football.ui.widgets.play_log import PlayLog

from football.ui.widgets.playbook.offense_playbook_view import OffensePlaySelected
from football.ui.widgets.playbook.defense_playbook_view import DefensePlaySelected


class FootballApp(App):
    @property
    def game_state(self) -> GameState:
        return self.state

    TITLE = "American Football Hybrid Sim"
    CSS_PATH = "app.tcss"  # optional; ok if you don't have it yet

    BINDINGS = [
        ("space", "call_play", "Call Play"),
        ("a", "focus_away", "Focus Away"),
        ("h", "focus_home", "Focus Home"),
        ("l", "focus_log", "Focus Log"),
    ]

    def __init__(self) -> None:
        super().__init__()

        # Initial state: you said you set BAL home, DAL away
        # If your GameState uses a different initializer, swap this call.
        self.state: GameState = GameState.initial(
            home_name="Seattle Seahawks",
            home_abbr="SEA",
            home_color="green",
            away_name="Dallas Cowboys",
            away_abbr="DAL",
            away_color="dodger_blue2",
        )

        # Widgets get assigned in compose()
        self.away_panel: PlaycallPanel
        self.home_panel: PlaycallPanel
        self.scoreboard: Scoreboard
        self.field: FieldView
        self.situation: DownDistance
        self.current_drive: CurrentDrive
        self.play_log: PlayLog

    # ----------------------------
    # Layout
    # ----------------------------

    def compose(self) -> ComposeResult:

        with TabbedContent(id="tabs"):
            with TabPane("Game", id="tab-game"):
                yield from self._compose_game_tab()

            with TabPane("Offense", id="tab-offense"):
                self.offense_playbook = OffensePlaybookView(id="offense-playbook")
                yield self.offense_playbook

            with TabPane("Defense", id="tab-defense"):
                self.defense_playbook = DefensePlaybookView(id="defense-playbook")
                yield self.defense_playbook

    def _compose_game_tab(self) -> ComposeResult:
        # This is basically your current compose(), but as a helper
        with Vertical(id="root"):
            with Horizontal(id="top-row"):
                self.away_panel = PlaycallPanel(team_side=Side.AWAY, id="away-playcall")
                yield self.away_panel

                self.scoreboard = Scoreboard(id="scoreboard", state=self.state)
                yield self.scoreboard

                self.home_panel = PlaycallPanel(team_side=Side.HOME, id="home-playcall")
                yield self.home_panel

            with Horizontal(id="middle-row"):
                with Vertical(id="left-mid"):
                    self.situation = DownDistance(id="situation", state=self.state)
                    yield self.situation

                    self.current_drive = CurrentDrive(id="current-drive", state=self.state)
                    yield self.current_drive

                with Vertical(id="center-mid"):
                    self.field = FieldView(id="field", state=self.state)
                    yield self.field

            with Vertical(id="bottom-row"):
                self.play_log = PlayLog(id="play-log")
                yield self.play_log

    def on_mount(self) -> None:
        self.play_log.add_line("[bold green]Play log online.[/bold green]")
        self._sync_playcall_modes()
        self._update_all_stateful_widgets()
        # Start focused on the offense panel
        self._focus_offense_panel()

    def on_offense_play_selected(self, message: OffensePlaySelected) -> None:
        """Handle play selection from Offense tab and apply to the current offense panel."""
        # Determine which side is currently on offense
        if self.state.possession is Side.HOME:
            offense_panel = self.home_panel
        else:
            offense_panel = self.away_panel

        offense_panel.apply_offense_playbook_selection(
            personnel=message.personnel,
            play_type=message.play_type,
            direction=message.direction,
            target=message.target,
            depth=message.depth,
        )

        # Switch back to Game tab
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = "tab-game"

        # Ensure panels are in correct OFFENSE/DEFENSE mode and focus offense
        self._sync_playcall_modes()
        self._focus_offense_panel()

    def on_defense_play_selected(self, message: DefensePlaySelected) -> None:
        # team on defense is the opposite of possession
        defense_side = Side.AWAY if self.state.possession is Side.HOME else Side.HOME
        defense_panel = self.away_panel if defense_side is Side.AWAY else self.home_panel

        defense_panel.apply_defense_playbook_selection(
            front=message.front,
            flavor=message.flavor,
            coverage=message.coverage,
        )

        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = "tab-game"

        self._sync_playcall_modes()
        self._focus_defense_panel()

    # ----------------------------
    # Helpers
    # ----------------------------

    def _update_all_stateful_widgets(self) -> None:
        """Push current GameState into stateful widgets."""
        # Each widget should implement a lightweight setter/update.
        # If your widgets use different method names, adapt here in ONE place.
        self.scoreboard.set_state(self.state)
        self.situation.set_state(self.state)
        self.current_drive.set_state(self.state)
        self.field.set_state(self.state)

        # Playcall panels don't need state to render (they hold selections),
        # but if you display context like DOWN/DIST, you can pass state too.
        # if hasattr(self.away_panel, "set_state"):
        #     self.away_panel.set_state(self.state)  # optional
        # if hasattr(self.home_panel, "set_state"):
        #     self.home_panel.set_state(self.state)  # optional

    def _sync_playcall_modes(self) -> None:
        if self.state.possession is Side.AWAY:
            self.away_panel.set_unit("OFFENSE")
            self.home_panel.set_unit("DEFENSE")
        else:
            self.away_panel.set_unit("DEFENSE")
            self.home_panel.set_unit("OFFENSE")

    def _focus_offense_panel(self) -> None:
        if self.state.possession is Side.HOME:
            self.home_panel.focus()
        else:
            self.away_panel.focus()

    def _focus_defense_panel(self) -> None:
        if self.state.possession is Side.HOME:
            self.away_panel.focus()
        else:
            self.home_panel.focus()

    def _team_abbr_for_side(self, side: Side) -> str:
        return self.state.home_abbr if side is Side.HOME else self.state.away_abbr

    # ----------------------------
    # Actions / key bindings
    # ----------------------------

    def action_focus_away(self) -> None:
        self.away_panel.focus()

    def action_focus_home(self) -> None:
        self.home_panel.focus()

    def action_focus_log(self) -> None:
        self.play_log.focus()

    def action_call_play(self) -> None:
        """Resolve the play using current panel selections."""
        s = self.state
        offense_side: Side = s.possession
        defense_side: Side = Side.HOME if offense_side is Side.AWAY else Side.AWAY

        # Build calls from the correct panels depending on who has possession
        if offense_side is Side.HOME:
            offense_call = self.home_panel.get_offensive_play_call(s)
            defense_call = self.away_panel.get_defensive_play_call(s)
        else:
            offense_call = self.away_panel.get_offensive_play_call(s)
            defense_call = self.home_panel.get_defensive_play_call(s)

        play_call = PlayCall(offense=offense_call, defense=defense_call)

        # Run engine
        new_state, result = resolve_play(s, play_call)
        self.state = new_state

        # Sync UI + modes
        self._sync_playcall_modes()
        self._update_all_stateful_widgets()

        # Pretty log line using team abbr + team colors
        off_abbr = self._team_abbr_for_side(offense_side)
        def_abbr = self._team_abbr_for_side(defense_side)

        off_tag = f"[{team_style(off_abbr)}]{off_abbr}[/]"
        def_tag = f"[{team_style(def_abbr)}]{def_abbr}[/]"

        # Yardage styling
        y = result.yards_gained
        y_style = "bold green" if y > 0 else "bold red" if y < 0 else "bold yellow"

        # Describe the chosen calls (works for both your old and new enums)
        off_play_name = getattr(offense_call.play_type, "name", str(offense_call.play_type))
        def_flavor_name = getattr(defense_call.flavor, "name", str(defense_call.flavor))
        def_front_name = getattr(defense_call.front, "name", str(defense_call.front))
        def_cov_name = getattr(defense_call.coverage, "name", str(defense_call.coverage))

        line = (
            f"{off_tag} [dim]OFF[/dim] {off_play_name}"
            f"  [dim]|[/dim]  "
            f"{def_tag} [dim]DEF[/dim] {def_front_name}/{def_flavor_name}/{def_cov_name}"
            f"  [dim]→[/dim] [{y_style}]{y:+d}y[/{y_style}]"
        )

        if result.touchdown:
            line += "  [bold magenta]TD![/bold magenta]"
        elif result.first_down:
            line += "  [bold cyan]1st Down[/bold cyan]"

        # Add contextual down/distance/spot
        # (yard_line is stored from HOME goal line; your situation widget already formats nicely)
        line += f"  [dim]({self.state.down}&{self.state.distance} @ {self.state.yard_line})[/dim]"

        self.play_log.add_line(line)

        # Keep focus on offense panel after play
        self._focus_offense_panel()


def run() -> None:
    FootballApp().run()
