from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Optional, Tuple

from .game_state import GameState, Side
from .play_call import (
    PlayCall,
    OffensePlayType,
    DefensePlayFlavor,
)


@dataclass(slots=True)
class ResolvedPlay:
    """Result of a single play for logging / stats."""

    offense_side: Side
    defense_side: Side
    yards_gained: int
    description: str

    first_down: bool
    turnover: bool
    touchdown: bool

    # snapshot-ish info after the play
    new_down: int
    new_distance: int
    new_yard_line: int
    new_time_remaining: int


# ---------- Internal helpers ----------


def _yardage_band(
    offense_type: OffensePlayType,
    defense_flavor: DefensePlayFlavor,
) -> Tuple[int, int]:
    """Return (min_yards, max_yards) for this offense/defense matchup.

    This is intentionally simple for now; we can refine probabilities later.
    Negative values represent losses, sacks, etc.
    """

    # Base defaults
    base = {
        OffensePlayType.INSIDE_RUN: (-2, 6),
        OffensePlayType.OUTSIDE_RUN: (-3, 8),
        OffensePlayType.DRAW: (-2, 10),
        OffensePlayType.QB_SNEAK: (0, 3),
        OffensePlayType.QB_KEEPER: (-3, 10),
        OffensePlayType.SHORT_PASS: (-5, 12),  # sacks / incompletions to YAC
        OffensePlayType.INTERMEDIATE_PASS: (-8, 18),
        OffensePlayType.DEEP_SHOT: (-10, 35),
        OffensePlayType.SCREEN_PASS: (-6, 18),
        OffensePlayType.PLAY_ACTION: (-5, 25),
        OffensePlayType.SPIKE: (0, 0),
        OffensePlayType.KNEEL: (0, 0),
    }

    min_y, max_y = base[offense_type]

    # Simple adjustments based on defense flavor
    if defense_flavor == DefensePlayFlavor.RUN_FOCUS:
        if offense_type in (OffensePlayType.INSIDE_RUN, OffensePlayType.OUTSIDE_RUN, OffensePlayType.DRAW):
            min_y -= 2
            max_y -= 1
        else:
            max_y += 3  # passes can pop bigger

    elif defense_flavor == DefensePlayFlavor.RUN_BLITZ:
        if offense_type in (OffensePlayType.INSIDE_RUN, OffensePlayType.OUTSIDE_RUN, OffensePlayType.DRAW):
            min_y -= 3
            max_y += 1  # boom/bust vs run
        else:
            min_y -= 6  # sacks / drive-kill

    elif defense_flavor == DefensePlayFlavor.PASS_FOCUS:
        if offense_type in (
            OffensePlayType.SHORT_PASS,
            OffensePlayType.INTERMEDIATE_PASS,
            OffensePlayType.DEEP_SHOT,
            OffensePlayType.SCREEN_PASS,
            OffensePlayType.PLAY_ACTION,
        ):
            min_y -= 3
            max_y -= 3  # tighter coverage
        else:
            max_y += 4  # run light boxes

    elif defense_flavor == DefensePlayFlavor.PASS_BLITZ:
        if offense_type in (
            OffensePlayType.SHORT_PASS,
            OffensePlayType.INTERMEDIATE_PASS,
            OffensePlayType.DEEP_SHOT,
            OffensePlayType.SCREEN_PASS,
            OffensePlayType.PLAY_ACTION,
        ):
            min_y -= 8  # big sack risk
            max_y += 8  # big play risk
        else:
            min_y -= 2

    elif defense_flavor == DefensePlayFlavor.ALL_OUT_BLITZ:
        min_y -= 10
        max_y += 15  # totally boom/bust

    elif defense_flavor == DefensePlayFlavor.PREVENT:
        if offense_type in (
            OffensePlayType.SHORT_PASS,
            OffensePlayType.SCREEN_PASS,
            OffensePlayType.INSIDE_RUN,
            OffensePlayType.DRAW,
        ):
            min_y += 0
            max_y += 4  # soft underneath
        else:
            min_y -= 3
            max_y -= 5  # deep shots limited

    elif defense_flavor == DefensePlayFlavor.CONTAIN:
        # Try to cap explosives, keep things modest
        max_y = min(max_y, 12)
        min_y = max(min_y, -3)

    # Clamp bands a bit
    min_y = max(min_y, -15)
    max_y = min(max_y, 50)

    if min_y > max_y:
        min_y, max_y = max_y, min_y

    return min_y, max_y


def _clock_runoff_seconds(offense_type: OffensePlayType, yards_gained: int) -> int:
    """Very simplified clock rules.

    We can refine this later with incompletions, out-of-bounds, 2-min drill, etc.
    """
    if offense_type in (OffensePlayType.SPIKE, OffensePlayType.KNEEL):
        return 5

    # crude: short plays or negative plays = shorter time
    if yards_gained <= 0:
        return 15
    return 25


# ---------- Public API ----------


def resolve_play(
    state: GameState,
    play_call: PlayCall,
    rng: Optional[Random] = None,
) -> tuple[GameState, ResolvedPlay]:
    """Core engine: given state + play calls, return (new_state, result).

    This is intentionally first-pass and will get smarter over time.
    """

    if rng is None:
        rng = Random()

    offense = play_call.offense
    defense = play_call.defense

    offense_side = offense.side
    defense_side = defense.side

    # Safety check: if state.possession doesn't match offense_side, trust state.
    if state.possession is not offense_side:
        offense_side = state.possession
        defense_side = Side.HOME if offense_side is Side.AWAY else Side.AWAY

    # Special plays
    if offense.play_type in (OffensePlayType.SPIKE, OffensePlayType.KNEEL):
        yards = 0
    else:
        min_y, max_y = _yardage_band(offense.play_type, defense.flavor)
        yards = rng.randint(min_y, max_y)

    # Figure out first-down vs TD from offense perspective
    offense_yard_before = state.yard_line_from_offense_perspective()
    offense_yard_after = max(0, min(100, offense_yard_before + yards))

    touchdown = offense_yard_after >= 100
    first_down = (not touchdown) and (yards >= state.distance)

    # No turnover logic yet (INTs, fumbles, picks on downs).
    turnover = False

    # Let GameState handle down/distance/spot logic
    state_after_downs = state.next_down_after_play(
        yards_gained=yards,
        first_down_gained=first_down,
        touchdown=touchdown,
        turnover=turnover,
    )

    # Scoring
    scored_state = state_after_downs
    if touchdown:
        # Add 6 points
        scored_state = scored_state.with_added_points(offense_side, 6)

        # Kickoff / change possession:
        # receiving team is the defense (since offense just scored)
        receiving_side = defense_side

        # Put ball at receiving team's own 25:
        # Our yard_line is "from HOME goal line" (0=HOME goal, 100=AWAY goal).
        kickoff_spot = 25 if receiving_side is Side.HOME else 75  # 75 = AWAY own 25

        scored_state = scored_state.copy(
            possession=receiving_side,
            down=1,
            distance=10,
            yard_line=kickoff_spot,
            current_drive_play_count=0,
            current_drive_yards=0,
            current_drive_start_yard_line=kickoff_spot,
            clock_running=False,
        )

    # Clock
    time_runoff = _clock_runoff_seconds(offense.play_type, yards)
    new_time = max(0, scored_state.time_remaining - time_runoff)

    final_state = scored_state.copy(time_remaining=new_time)

    # Build result summary for logging / stats
    desc = f"{offense_side.name} {offense.play_type.name.replace('_', ' ').title()} for {yards:+d} yards"
    if touchdown:
        desc += " — TOUCHDOWN"

    result = ResolvedPlay(
        offense_side=offense_side,
        defense_side=defense_side,
        yards_gained=yards,
        description=desc,
        first_down=first_down,
        turnover=turnover,
        touchdown=touchdown,
        new_down=final_state.down,
        new_distance=final_state.distance,
        new_yard_line=final_state.yard_line,
        new_time_remaining=final_state.time_remaining,
    )

    return final_state, result
