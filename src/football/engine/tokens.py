from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class PlayType(Enum):
    RUN = auto()
    SHORT_PASS = auto()
    LONG_PASS = auto()
    SCREEN = auto()
    SPECIAL = auto()


class Focus(Enum):
    RUN = auto()
    PASS = auto()
    BALANCED = auto()


Direction = Optional[str]  # "LEFT" | "MIDDLE" | "RIGHT" | None


@dataclass(frozen=True)
class PlaycallOffense:
    play_type: PlayType
    target: str  # "RB", "WR1", "WR2", "TE"
    direction: Direction = None


@dataclass(frozen=True)
class PlaycallDefense:
    focus: Focus
    blitz: bool = False
    key_target: Optional[str] = None  # "RB", "WR1", "WR2", "TE"
    shift_direction: Direction = None  # "LEFT" | "MIDDLE" | "RIGHT" | None
