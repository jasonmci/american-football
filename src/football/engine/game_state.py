from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import List


class Side(str, Enum):
    HOME = "HOME"
    AWAY = "AWAY"


@dataclass(slots=True)
class ScoreByQuarter:
    """Tracks scores per quarter for both teams.

    We keep flexible lists so OT can be added as an extra entry.
    Index 0 = Q1, 1 = Q2, 2 = Q3, 3 = Q4, 4+ = OT periods.
    """

    home: List[int]
    away: List[int]

    @staticmethod
    def initial() -> "ScoreByQuarter":
        # Start with 4 quarters, all zeros.
        return ScoreByQuarter(home=[0, 0, 0, 0], away=[0, 0, 0, 0])

    def add_points(self, side: Side, quarter_index: int, points: int) -> None:
        # Grow lists if we enter OT, etc.
        while quarter_index >= len(self.home):
            self.home.append(0)
            self.away.append(0)

        if side is Side.HOME:
            self.home[quarter_index] += points
        else:
            self.away[quarter_index] += points

    @property
    def home_total(self) -> int:
        return sum(self.home)

    @property
    def away_total(self) -> int:
        return sum(self.away)


@property
def home_quarter_scores(self) -> list[int]:
    """UI compatibility: returns list of home quarter scores."""
    return self.scores.home


@property
def away_quarter_scores(self) -> list[int]:
    """UI compatibility: returns list of away quarter scores."""
    return self.scores.away


@dataclass(slots=True)
class GameState:
    """Immutable-ish snapshot of the game at a point in time.

    This is the core model used by the engine and the UI.
    """

    # Teams / metadata
    home_name: str
    home_abbr: str
    away_name: str
    away_abbr: str

    # Game progress
    quarter: int  # 1–4 (5+ = OT)
    time_remaining: int  # 0–900 (per quarter)
    possession: Side  # Side.HOME or Side.AWAY

    # Field / down info
    down: int  # 1–4
    distance: int  # yards to first down (1–99)
    yard_line: int  # 0–100, relative to HOME goal line
    hash_mark: str  # "LEFT", "MIDDLE", "RIGHT" (for future expansion)

    # Timeouts
    home_timeouts: int  # 0–3
    away_timeouts: int  # 0–3

    # Scoreboard
    scores: ScoreByQuarter

    # Drive-level info (summary; detailed drive log can be separate)
    current_drive_play_count: int
    current_drive_yards: int
    current_drive_start_yard_line: int

    # Flags
    clock_running: bool  # is the game clock currently moving?
    game_over: bool

    @staticmethod
    def initial(
        *,
        home_name: str,
        home_abbr: str,
        away_name: str,
        away_abbr: str,
        home_receives: bool = True,
    ) -> "GameState":
        """Create a fresh game at 1st & 10 on the 25 for the receiving team."""
        receiving_side = Side.HOME if home_receives else Side.AWAY
        yard_line = 25 if receiving_side is Side.HOME else 75  # 75 = OTHER 25

        return GameState(
            home_name=home_name,
            home_abbr=home_abbr,
            away_name=away_name,
            away_abbr=away_abbr,
            quarter=1,
            time_remaining=15 * 60,  # 15:00 per quarter
            possession=receiving_side,
            down=1,
            distance=10,
            yard_line=yard_line,
            hash_mark="MIDDLE",
            home_timeouts=3,
            away_timeouts=3,
            scores=ScoreByQuarter.initial(),
            current_drive_play_count=0,
            current_drive_yards=0,
            current_drive_start_yard_line=yard_line,
            clock_running=False,
            game_over=False,
        )

    # -------- Convenience helpers (pure-ish) --------

    def copy(self, **changes) -> "GameState":
        """Return a shallow copy with some fields changed."""
        return replace(self, **changes)

    def offense_side(self) -> Side:
        """Which side currently has the ball."""
        return self.possession

    def defense_side(self) -> Side:
        return Side.HOME if self.possession is Side.AWAY else Side.AWAY

    def yard_line_from_offense_perspective(self) -> int:
        """Return yard line as 0–100 from the offense's perspective.

        If HOME has the ball, this is just yard_line.
        If AWAY has the ball, flip the field (100 - yard_line).
        Useful for play tables that assume 'offense drives left→right'.
        """
        if self.possession is Side.HOME:
            return self.yard_line
        return 100 - self.yard_line

    def with_added_points(self, side: Side, points: int) -> "GameState":
        """Return a new state with points added & scoreboard updated."""
        new_scores = ScoreByQuarter(
            home=list(self.scores.home),
            away=list(self.scores.away),
        )
        # quarter index is quarter-1
        new_scores.add_points(side, self.quarter - 1, points)
        return self.copy(scores=new_scores)

    def home_score_total(self) -> int:
        return self.scores.home_total

    def away_score_total(self) -> int:
        return self.scores.away_total

    def is_first_down(self) -> bool:
        return self.down == 1

    def is_red_zone(self) -> bool:
        """Simple flag: offense inside opponent's 20."""
        y = self.yard_line_from_offense_perspective()
        return 80 <= y <= 100

    def next_down_after_play(
        self,
        yards_gained: int,
        first_down_gained: bool,
        touchdown: bool = False,
        turnover: bool = False,
    ) -> "GameState":
        """Return a new GameState with updated down/distance/yard_line/drive.

        This is intentionally simple; the engine can decide when to call this
        and how to handle touchdowns, turnovers, etc.
        """
        new_yard_line = self.yard_line + (
            yards_gained if self.possession is Side.HOME else -yards_gained
        )

        # Clamp to field
        new_yard_line = max(0, min(100, new_yard_line))

        if touchdown or new_yard_line in (0, 100):
            # Engine will handle scoring & KO; we just mark game state as end-of-play on goal line.
            return self.copy(
                yard_line=new_yard_line,
                # distance/down will be reinitialized by engine after score
            )

        if turnover:
            # Switch sides; new offense gets 1st & 10 from spot
            new_possession = self.defense_side()
            return self.copy(
                possession=new_possession,
                down=1,
                distance=10,
                yard_line=new_yard_line,
                current_drive_play_count=0,
                current_drive_yards=0,
                current_drive_start_yard_line=new_yard_line,
            )

        if first_down_gained:
            # Reset to 1st & 10 from new spot
            return self.copy(
                down=1,
                distance=10,
                yard_line=new_yard_line,
                current_drive_play_count=self.current_drive_play_count + 1,
                current_drive_yards=self.current_drive_yards + yards_gained,
            )

        # Standard next down logic
        next_down = self.down + 1
        if next_down > 4:
            # Turnover on downs – engine may want to treat as full turnover
            new_possession = self.defense_side()
            return self.copy(
                possession=new_possession,
                down=1,
                distance=10,
                yard_line=new_yard_line,
                current_drive_play_count=0,
                current_drive_yards=0,
                current_drive_start_yard_line=new_yard_line,
            )

        # Still same drive, just advancing down & distance
        new_distance = max(1, self.distance - yards_gained)
        return self.copy(
            down=next_down,
            distance=new_distance,
            yard_line=new_yard_line,
            current_drive_play_count=self.current_drive_play_count + 1,
            current_drive_yards=self.current_drive_yards + yards_gained,
        )
