from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from random import Random
from typing import Optional, Tuple

from .game_state import GameState, Side
from .play_call import PlayCall


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


# ---------- Core "Statis style" families ----------


class CoreOffenseFamily(Enum):
    INSIDE_RUN = auto()
    OUTSIDE_RUN = auto()
    OPTION_RUN = auto()
    QUICK_PASS = auto()
    SHORT_PASS = auto()
    INTERMEDIATE_PASS = auto()
    DEEP_PASS = auto()
    SCREEN_PASS = auto()
    PLAY_ACTION = auto()
    SPIKE = auto()
    KNEEL = auto()


class CoreDefenseFamily(Enum):
    BASE = auto()
    RUN_FOCUS = auto()
    RUN_BLITZ = auto()
    PASS_FOCUS = auto()
    PASS_BLITZ = auto()
    ALL_OUT_BLITZ = auto()
    PREVENT = auto()
    CONTAIN = auto()
    QB_SPY = auto()


# ---------- Mapping helpers ----------


def _map_offense_to_core(play_type: object) -> CoreOffenseFamily:
    """Map a rich offense play type (or legacy one) to a core Statis-family.

    Supports either:
    - the earlier simplified enums (INSIDE_RUN, OUTSIDE_RUN, SHORT_PASS, etc.)
    - the newer expanded enums (INSIDE_ZONE, POST, MESH, PLAY_ACTION_SHOT, etc.)

    We intentionally key on .name so this works across enum versions.
    """
    name = getattr(play_type, "name", str(play_type)).upper()

    # Legacy fast-path
    legacy = {
        "INSIDE_RUN": CoreOffenseFamily.INSIDE_RUN,
        "OUTSIDE_RUN": CoreOffenseFamily.OUTSIDE_RUN,
        "DRAW": CoreOffenseFamily.INSIDE_RUN,
        "QB_SNEAK": CoreOffenseFamily.SPIKE,  # special handling (0 yards)
        "QB_KEEPER": CoreOffenseFamily.OPTION_RUN,
        "SHORT_PASS": CoreOffenseFamily.SHORT_PASS,
        "INTERMEDIATE_PASS": CoreOffenseFamily.INTERMEDIATE_PASS,
        "DEEP_SHOT": CoreOffenseFamily.DEEP_PASS,
        "SCREEN_PASS": CoreOffenseFamily.SCREEN_PASS,
        "PLAY_ACTION": CoreOffenseFamily.PLAY_ACTION,
        "SPIKE": CoreOffenseFamily.SPIKE,
        "KNEEL": CoreOffenseFamily.KNEEL,
    }
    if name in legacy:
        return legacy[name]

    # Expanded heuristic mapping
    if name in ("SPIKE",):
        return CoreOffenseFamily.SPIKE
    if name in ("KNEEL",):
        return CoreOffenseFamily.KNEEL

    if "SCREEN" in name:
        return CoreOffenseFamily.SCREEN_PASS

    if "PLAY_ACTION" in name or name in ("BOOTLEG", "ROLL_OUT"):
        return CoreOffenseFamily.PLAY_ACTION

    # Runs
    if any(k in name for k in ("INSIDE", "POWER", "COUNTER", "TRAP", "ISO", "DRAW", "DELAY")):
        return CoreOffenseFamily.INSIDE_RUN
    if any(k in name for k in ("OUTSIDE", "SWEEP", "TOSS", "JET", "REVERSE")):
        return CoreOffenseFamily.OUTSIDE_RUN
    if any(k in name for k in ("OPTION", "KEEPER", "SNEAK", "QB_")):
        return CoreOffenseFamily.OPTION_RUN

    # Passes by concept depth buckets
    if any(k in name for k in ("QUICK", "HITCH", "SLANT", "BUBBLE", "SMOKE")):
        return CoreOffenseFamily.QUICK_PASS
    if any(k in name for k in ("MESH", "OUT", "CROSS", "SEAM")):
        return CoreOffenseFamily.SHORT_PASS
    if any(k in name for k in ("DIG", "COMEBACK", "DEEP_OUT", "CROSSERS")):
        return CoreOffenseFamily.INTERMEDIATE_PASS
    if any(k in name for k in ("GO", "POST", "CORNER", "FADE", "DEEP")):
        return CoreOffenseFamily.DEEP_PASS

    # Default
    return CoreOffenseFamily.SHORT_PASS


def _map_defense_to_core(def_flavor: object) -> CoreDefenseFamily:
    """Map defense flavor to core family (supports legacy and expanded enums)."""
    name = getattr(def_flavor, "name", str(def_flavor)).upper()

    legacy = {
        "BASE": CoreDefenseFamily.BASE,
        "RUN_FOCUS": CoreDefenseFamily.RUN_FOCUS,
        "RUN_BLITZ": CoreDefenseFamily.RUN_BLITZ,
        "PASS_FOCUS": CoreDefenseFamily.PASS_FOCUS,
        "PASS_BLITZ": CoreDefenseFamily.PASS_BLITZ,
        "ALL_OUT_BLITZ": CoreDefenseFamily.ALL_OUT_BLITZ,
        "PREVENT": CoreDefenseFamily.PREVENT,
        "CONTAIN": CoreDefenseFamily.CONTAIN,
        "QB_SPY": CoreDefenseFamily.QB_SPY,
        "GOAL_LINE_SOLD_OUT": CoreDefenseFamily.RUN_FOCUS,
    }
    return legacy.get(name, CoreDefenseFamily.BASE)


# ---------- Internal helpers ----------


def _yardage_band(
    offense_family: CoreOffenseFamily,
    defense_family: CoreDefenseFamily,
) -> Tuple[int, int]:
    """Return (min_yards, max_yards) for core offense/defense families.

    This mirrors your existing base defaults and defense adjustments.
    """

    base: dict[CoreOffenseFamily, tuple[int, int]] = {
        CoreOffenseFamily.INSIDE_RUN: (-2, 6),
        CoreOffenseFamily.OUTSIDE_RUN: (-3, 8),
        CoreOffenseFamily.OPTION_RUN: (-3, 10),
        CoreOffenseFamily.QUICK_PASS: (-4, 10),
        CoreOffenseFamily.SHORT_PASS: (-5, 12),
        CoreOffenseFamily.INTERMEDIATE_PASS: (-8, 18),
        CoreOffenseFamily.DEEP_PASS: (-10, 35),
        CoreOffenseFamily.SCREEN_PASS: (-6, 18),
        CoreOffenseFamily.PLAY_ACTION: (-5, 25),
        CoreOffenseFamily.SPIKE: (0, 0),
        CoreOffenseFamily.KNEEL: (-1, -1),
    }

    min_y, max_y = base[offense_family]

    # Defense adjustments (same spirit as your original)
    if defense_family == CoreDefenseFamily.RUN_FOCUS:
        if offense_family in (
            CoreOffenseFamily.INSIDE_RUN,
            CoreOffenseFamily.OUTSIDE_RUN,
            CoreOffenseFamily.OPTION_RUN,
        ):
            min_y -= 2
            max_y -= 1
        else:
            max_y += 3

    elif defense_family == CoreDefenseFamily.RUN_BLITZ:
        if offense_family in (
            CoreOffenseFamily.INSIDE_RUN,
            CoreOffenseFamily.OUTSIDE_RUN,
            CoreOffenseFamily.OPTION_RUN,
        ):
            min_y -= 3
            max_y += 1
        else:
            min_y -= 6

    elif defense_family == CoreDefenseFamily.PASS_FOCUS:
        if offense_family in (
            CoreOffenseFamily.QUICK_PASS,
            CoreOffenseFamily.SHORT_PASS,
            CoreOffenseFamily.INTERMEDIATE_PASS,
            CoreOffenseFamily.DEEP_PASS,
            CoreOffenseFamily.SCREEN_PASS,
            CoreOffenseFamily.PLAY_ACTION,
        ):
            min_y -= 3
            max_y -= 3
        else:
            max_y += 4

    elif defense_family == CoreDefenseFamily.PASS_BLITZ:
        if offense_family in (
            CoreOffenseFamily.QUICK_PASS,
            CoreOffenseFamily.SHORT_PASS,
            CoreOffenseFamily.INTERMEDIATE_PASS,
            CoreOffenseFamily.DEEP_PASS,
            CoreOffenseFamily.SCREEN_PASS,
            CoreOffenseFamily.PLAY_ACTION,
        ):
            min_y -= 8
            max_y += 8
        else:
            min_y -= 2

    elif defense_family == CoreDefenseFamily.ALL_OUT_BLITZ:
        min_y -= 10
        max_y += 15

    elif defense_family == CoreDefenseFamily.PREVENT:
        if offense_family in (
            CoreOffenseFamily.QUICK_PASS,
            CoreOffenseFamily.SHORT_PASS,
            CoreOffenseFamily.SCREEN_PASS,
            CoreOffenseFamily.INSIDE_RUN,
        ):
            max_y += 4
        else:
            min_y -= 3
            max_y -= 5

    elif defense_family == CoreDefenseFamily.CONTAIN:
        max_y = min(max_y, 12)
        min_y = max(min_y, -3)

    # Clamp bands
    min_y = max(min_y, -15)
    max_y = min(max_y, 50)
    if min_y > max_y:
        min_y, max_y = max_y, min_y

    return min_y, max_y


def _clock_runoff_seconds(offense_family: CoreOffenseFamily, yards_gained: int) -> int:
    """Very simplified clock rules (core families)."""
    if offense_family in (CoreOffenseFamily.SPIKE, CoreOffenseFamily.KNEEL):
        return 5

    if yards_gained <= 0:
        return 15
    return 25


# ---------- Public API ----------


def resolve_play(
    state: GameState,
    play_call: PlayCall,
    rng: Optional[Random] = None,
) -> tuple[GameState, ResolvedPlay]:
    """Core engine: state + play calls -> (new_state, result).

    Uses a Statis-style mapping layer: any detailed play type resolves into a
    small set of core families, then we use the current base defaults.
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

    off_family = _map_offense_to_core(offense.play_type)
    def_family = _map_defense_to_core(defense.flavor)

    # Special plays / yardage
    if off_family in (CoreOffenseFamily.SPIKE, CoreOffenseFamily.KNEEL):
        yards = 0 if off_family == CoreOffenseFamily.SPIKE else -1
    else:
        min_y, max_y = _yardage_band(off_family, def_family)
        yards = rng.randint(min_y, max_y)

    # First down vs TD from offense perspective
    offense_yard_before = state.yard_line_from_offense_perspective()
    offense_yard_after = max(0, min(100, offense_yard_before + yards))

    touchdown = offense_yard_after >= 100
    first_down = (not touchdown) and (yards >= state.distance)

    turnover = False  # not yet

    # Advance downs/spot
    state_after_downs = state.next_down_after_play(
        yards_gained=yards,
        first_down_gained=first_down,
        touchdown=touchdown,
        turnover=turnover,
    )

    # Scoring + kickoff reset after TD
    scored_state = state_after_downs
    if touchdown:
        scored_state = scored_state.with_added_points(offense_side, 6)

        receiving_side = defense_side
        kickoff_spot = 25 if receiving_side is Side.HOME else 75

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
    time_runoff = _clock_runoff_seconds(off_family, yards)
    new_time = max(0, scored_state.time_remaining - time_runoff)
    final_state = scored_state.copy(time_remaining=new_time)

    # Description
    pt_name = getattr(offense.play_type, "name", str(offense.play_type))
    df_name = getattr(defense.flavor, "name", str(defense.flavor))
    desc = (
        f"{offense_side.name} {pt_name.replace('_', ' ').title()} "
        f"(core={off_family.name}) vs {df_name.replace('_', ' ').title()} "
        f"(core={def_family.name}) for {yards:+d} yards"
    )
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
