from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from .game_state import Side


# ------ Personnel ------
class PersonnelGroup(Enum):
    """Offensive skill-position grouping.

    Name follows NFL shorthand:
    - XYY where X = RB count, Y = TE count, and WR is implied (5 - RB - TE).
      e.g. "11" = 1 RB, 1 TE, 3 WR.
    """

    P10 = "10"  # 1 RB, 0 TE, 4 WR
    P11 = "11"  # 1 RB, 1 TE, 3 WR
    P12 = "12"  # 1 RB, 2 TE, 2 WR
    P13 = "13"  # 1 RB, 3 TE, 1 WR
    P20 = "20"  # 2 RB, 0 TE, 3 WR
    P21 = "21"  # 2 RB, 1 TE, 2 WR
    P22 = "22"  # 2 RB, 2 TE, 1 WR
    P23 = "23"  # 2 RB, 3 TE, 0 WR
    P00 = "00"  # 0 RB, 0 TE, 5 WR
    P01 = "01"  # 0 RB, 1 TE, 4 WR
    P02 = "02"  # 0 RB, 2 TE, 3 WR
    P03 = "03"  # 0 RB, 3 TE, 2 WR
    P04 = "04"  # 0 RB, 4 TE, 1 WR

    @property
    def rb(self) -> int:
        return int(self.value[0])

    @property
    def te(self) -> int:
        return int(self.value[1])

    @property
    def wr(self) -> int:
        return 5 - self.rb - self.te

# ---- Shared enums ----


class PlayDirection(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


class PassDepth(Enum):
    """Optional pass depth classification for flavor / tables."""
    SHORT = auto()       # 0–10 yards
    INTERMEDIATE = auto()  # 11–19
    DEEP = auto()        # 20+


class TargetType(Enum):
    """Primary offensive target / ball carrier archetype."""

    RB1 = auto()
    RB2 = auto()
    WR1 = auto()
    WR2 = auto()
    WR3 = auto()
    TE1 = auto()
    TE2 = auto()
    QB = auto()  # keepers, sneaks, scrambles


class OffensePlayType(Enum):
    """High-level offensive play families.

    We can expand later, but this is enough for a first-cut engine.
    """

    # Run game
    INSIDE_RUN = auto()  # dives, inside zone, iso
    OUTSIDE_RUN = auto()  # stretch, toss, outside zone
    DRAW = auto()  # draw / delay handoff
    QB_SNEAK = auto()
    QB_KEEPER = auto()  # boots, read keepers

    # Pass game
    SHORT_PASS = auto()  # slants, quick outs, hitches
    INTERMEDIATE_PASS = auto()  # digs, comebacks, deep outs
    DEEP_SHOT = auto()  # posts, go routes, bombs
    SCREEN_PASS = auto()  # RB/WR screens
    PLAY_ACTION = auto()  # PA shot or intermediate

    # Game-management
    SPIKE = auto()
    KNEEL = auto()


@dataclass(slots=True)
class OffensivePlayCall:

    side: Side
    personnel: PersonnelGroup
    play_type: OffensePlayType
    direction: Optional[PlayDirection] = None
    pass_depth: Optional[PassDepth] = None
    target: Optional[TargetType] = None

    # For future: token/hidden selection mechanism, audibles, etc.
    token_id: Optional[str] = None  # Techno-Bowl-style token reference


# ---------- Defense ----------


class DefenseFront(Enum):
    """Defensive front / sub-package."""

    BASE = auto()  # 3-4 / 4-3 base
    NICKEL = auto()  # 5 DBs
    DIME = auto()  # 6 DBs
    GOAL_LINE = auto()  # heavy, many DL/LB


class DefensePlayFlavor(Enum):
    """What the defense is 'trying' to stop / emphasize."""

    BASE = auto()  # balanced
    RUN_FOCUS = auto()  # selling out vs run (boxes, slants)
    PASS_FOCUS = auto()  # lighter box, coverage emphasis
    RUN_BLITZ = auto()  # run-focused pressure
    PASS_BLITZ = auto()  # pressure vs pass, extra rushers
    ALL_OUT_BLITZ = auto()  # zero-style heat
    PREVENT = auto()  # back off, protect deep
    CONTAIN = auto()  # edges, QB contain/spies


class CoverageShell(Enum):
    """Coverage structure (simplified)."""

    COVER_1 = auto()
    COVER_2 = auto()
    COVER_3 = auto()
    COVER_4 = auto()
    ZERO = auto()  # man-zero / no deep help


@dataclass(slots=True)
class DefensivePlayCall:
    """Full description of the defense's chosen concept."""

    side: Side  # which team is on defense
    front: DefenseFront
    flavor: DefensePlayFlavor
    coverage: CoverageShell

    # For future: stunts, specific blitzers, show/bluff, etc.
    token_id: Optional[str] = None  # Techno-Bowl-style hidden call id


# ---------- Unified wrapper ----------


class Unit(Enum):
    OFFENSE = "OFFENSE"
    DEFENSE = "DEFENSE"


@dataclass(slots=True)
class PlayCall:
    """Wrapper used by the engine to bundle both sides' decisions.

    For a given play, the controller (UI / AI) will produce one
    OffensivePlayCall for the offense and one DefensivePlayCall for the defense,
    then pass both into the engine.
    """

    offense: OffensivePlayCall
    defense: DefensivePlayCall

    @property
    def offense_side(self) -> Side:
        return self.offense.side

    @property
    def defense_side(self) -> Side:
        return self.defense.side
