from __future__ import annotations
from enum import Enum, auto

from .play_call import OffensePlayType, DefensePlayFlavor


class CoreOffenseFamily(Enum):
    INSIDE_RUN = auto()
    OUTSIDE_RUN = auto()
    OPTION_RUN = auto()
    QUICK_PASS = auto()
    SHORT_PASS = auto()
    INTERMEDIATE_PASS = auto()
    DEEP_PASS = auto()
    SCREEN = auto()
    PLAY_ACTION = auto()
    QB_KNEEL_SPIKE = auto()


class CoreDefenseFamily(Enum):
    BASE = auto()
    RUN_FOCUS = auto()
    PASS_FOCUS = auto()
    RUN_BLITZ = auto()
    PASS_BLITZ = auto()
    ALL_OUT_BLITZ = auto()
    PREVENT = auto()
    CONTAIN = auto()
    QB_SPY = auto()


OFFENSE_MAP: dict[OffensePlayType, CoreOffenseFamily] = {
    # Inside-ish
    OffensePlayType.INSIDE_ZONE: CoreOffenseFamily.INSIDE_RUN,
    OffensePlayType.POWER: CoreOffenseFamily.INSIDE_RUN,
    OffensePlayType.COUNTER: CoreOffenseFamily.INSIDE_RUN,
    OffensePlayType.TRAP: CoreOffenseFamily.INSIDE_RUN,
    OffensePlayType.ISO: CoreOffenseFamily.INSIDE_RUN,
    OffensePlayType.QB_SNEAK: CoreOffenseFamily.QB_KNEEL_SPIKE,
    # Outside-ish
    OffensePlayType.OUTSIDE_ZONE: CoreOffenseFamily.OUTSIDE_RUN,
    OffensePlayType.SWEEP: CoreOffenseFamily.OUTSIDE_RUN,
    OffensePlayType.TOSS: CoreOffenseFamily.OUTSIDE_RUN,
    # Option / gadget runs
    OffensePlayType.READ_OPTION: CoreOffenseFamily.OPTION_RUN,
    OffensePlayType.SPEED_OPTION: CoreOffenseFamily.OPTION_RUN,
    OffensePlayType.QB_KEEPER: CoreOffenseFamily.OPTION_RUN,
    OffensePlayType.JET_SWEEP: CoreOffenseFamily.OUTSIDE_RUN,
    OffensePlayType.REVERSE: CoreOffenseFamily.OUTSIDE_RUN,
    OffensePlayType.DRAW: CoreOffenseFamily.INSIDE_RUN,
    OffensePlayType.DELAY: CoreOffenseFamily.INSIDE_RUN,
    # Quick game + screens
    OffensePlayType.QUICK_SLANT: CoreOffenseFamily.QUICK_PASS,
    OffensePlayType.QUICK_OUT: CoreOffenseFamily.QUICK_PASS,
    OffensePlayType.QUICK_HITCH: CoreOffenseFamily.QUICK_PASS,
    OffensePlayType.BUBBLE_SCREEN: CoreOffenseFamily.SCREEN,
    OffensePlayType.SMOKE_SCREEN: CoreOffenseFamily.SCREEN,
    OffensePlayType.RB_SCREEN: CoreOffenseFamily.SCREEN,
    OffensePlayType.TE_SCREEN: CoreOffenseFamily.SCREEN,
    # Intermediate
    OffensePlayType.DIG: CoreOffenseFamily.INTERMEDIATE_PASS,
    OffensePlayType.COMEBACK: CoreOffenseFamily.INTERMEDIATE_PASS,
    OffensePlayType.DEEP_OUT: CoreOffenseFamily.INTERMEDIATE_PASS,
    OffensePlayType.CROSSERS: CoreOffenseFamily.INTERMEDIATE_PASS,
    OffensePlayType.MESH: CoreOffenseFamily.SHORT_PASS,
    OffensePlayType.SEAM: CoreOffenseFamily.INTERMEDIATE_PASS,
    # Deep
    OffensePlayType.GO: CoreOffenseFamily.DEEP_PASS,
    OffensePlayType.POST: CoreOffenseFamily.DEEP_PASS,
    OffensePlayType.CORNER: CoreOffenseFamily.DEEP_PASS,
    OffensePlayType.FADE: CoreOffenseFamily.DEEP_PASS,
    OffensePlayType.DEEP_CROSS: CoreOffenseFamily.DEEP_PASS,
    # Play action / movement passes
    OffensePlayType.PLAY_ACTION_SHORT: CoreOffenseFamily.PLAY_ACTION,
    OffensePlayType.PLAY_ACTION_SHOT: CoreOffenseFamily.PLAY_ACTION,
    OffensePlayType.BOOTLEG: CoreOffenseFamily.PLAY_ACTION,
    OffensePlayType.ROLL_OUT: CoreOffenseFamily.SHORT_PASS,
    # Management
    OffensePlayType.SPIKE: CoreOffenseFamily.QB_KNEEL_SPIKE,
    OffensePlayType.KNEEL: CoreOffenseFamily.QB_KNEEL_SPIKE,
}

DEFENSE_MAP: dict[DefensePlayFlavor, CoreDefenseFamily] = {
    DefensePlayFlavor.BASE: CoreDefenseFamily.BASE,
    DefensePlayFlavor.RUN_FOCUS: CoreDefenseFamily.RUN_FOCUS,
    DefensePlayFlavor.RUN_BLITZ: CoreDefenseFamily.RUN_BLITZ,
    DefensePlayFlavor.GOAL_LINE_SOLD_OUT: CoreDefenseFamily.RUN_FOCUS,
    DefensePlayFlavor.PASS_FOCUS: CoreDefenseFamily.PASS_FOCUS,
    DefensePlayFlavor.PASS_BLITZ: CoreDefenseFamily.PASS_BLITZ,
    DefensePlayFlavor.ALL_OUT_BLITZ: CoreDefenseFamily.ALL_OUT_BLITZ,
    DefensePlayFlavor.PREVENT: CoreDefenseFamily.PREVENT,
    DefensePlayFlavor.CONTAIN: CoreDefenseFamily.CONTAIN,
    DefensePlayFlavor.QB_SPY: CoreDefenseFamily.QB_SPY,
}
