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

    P00 = "00"  # 0 RB, 0 TE, 5 WR
    P01 = "01"  # 0 RB, 1 TE, 4 WR
    P02 = "02"  # 0 RB, 2 TE, 3 WR
    P03 = "03"  # 0 RB, 3 TE, 2 WR
    P04 = "04"  # 0 RB, 4 TE, 1 WR
    P10 = "10"  # 1 RB, 0 TE, 4 WR
    P11 = "11"  # 1 RB, 1 TE, 3 WR
    P12 = "12"  # 1 RB, 2 TE, 2 WR
    P13 = "13"  # 1 RB, 3 TE, 1 WR
    P20 = "20"  # 2 RB, 0 TE, 3 WR
    P21 = "21"  # 2 RB, 1 TE, 2 WR
    P22 = "22"  # 2 RB, 2 TE, 1 WR
    P23 = "23"  # 2 RB, 3 TE, 0 WR
    P30 = "30"  # 3 RB, 0 TE (rare, but fun)
    P31 = "31"
    P32 = "32"

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
    QUICK = auto()  # 0–3
    SHORT = auto()  # 4–10
    INTERMEDIATE = auto()  # 11–19
    DEEP = auto()  # 20+


class TargetType(Enum):
    """Primary offensive target / ball carrier archetype."""

    RB1 = auto()
    RB2 = auto()
    WR1 = auto()
    WR2 = auto()
    WR3 = auto()
    WR4 = auto()
    WR5 = auto()
    TE1 = auto()
    TE2 = auto()
    QB = auto()


class OffensePlayType(Enum):
    """High-level offensive play families."""

    # Runs (core)
    INSIDE_ZONE = auto()
    OUTSIDE_ZONE = auto()
    POWER = auto()
    COUNTER = auto()
    TRAP = auto()
    ISO = auto()
    SWEEP = auto()
    TOSS = auto()

    # Specialty runs
    DRAW = auto()
    DELAY = auto()
    QB_SNEAK = auto()
    QB_KEEPER = auto()
    READ_OPTION = auto()
    SPEED_OPTION = auto()
    JET_SWEEP = auto()
    REVERSE = auto()

    # Quick game / short passing
    QUICK_SLANT = auto()
    QUICK_OUT = auto()
    QUICK_HITCH = auto()
    BUBBLE_SCREEN = auto()
    SMOKE_SCREEN = auto()
    RB_SCREEN = auto()
    TE_SCREEN = auto()

    # Intermediate concepts
    DIG = auto()
    COMEBACK = auto()
    DEEP_OUT = auto()
    CROSSERS = auto()
    MESH = auto()
    SEAM = auto()

    # Deep concepts
    GO = auto()
    POST = auto()
    CORNER = auto()
    FADE = auto()
    DEEP_CROSS = auto()

    # Play-action / movement
    PLAY_ACTION_SHORT = auto()
    PLAY_ACTION_SHOT = auto()
    BOOTLEG = auto()
    ROLL_OUT = auto()

    # Game management
    SPIKE = auto()
    KNEEL = auto()


@dataclass(slots=True)
class OffensivePlayCall:

    side: Side
    personnel: PersonnelGroup
    play_type: OffensePlayType
    direction: Optional[PlayDirection] = None
    pass_depth: Optional[PassDepth] = None
    primary_target: Optional[TargetType] = None

    # For future: token/hidden selection mechanism, audibles, etc.
    token_id: Optional[str] = None  # Techno-Bowl-style token reference


# ---------- Defense ----------


class DefenseFront(Enum):
    # Base families
    FOUR_THREE = auto()
    THREE_FOUR = auto()

    # Sub packages
    NICKEL = auto()
    DIME = auto()
    QUARTER = auto()  # 7 DB looks
    GOAL_LINE = auto()


class DefensePlayFlavor(Enum):
    BASE = auto()

    # Run emphasis
    RUN_FOCUS = auto()
    RUN_BLITZ = auto()
    GOAL_LINE_SOLD_OUT = auto()

    # Pass emphasis
    PASS_FOCUS = auto()
    PASS_BLITZ = auto()
    ALL_OUT_BLITZ = auto()

    # Situational
    PREVENT = auto()
    CONTAIN = auto()
    QB_SPY = auto()


class CoverageShell(Enum):
    ZERO = auto()
    COVER_1 = auto()
    COVER_2 = auto()
    TAMPA_2 = auto()
    COVER_3 = auto()
    COVER_4 = auto()
    COVER_6 = auto()  # quarter-quarter-half


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
