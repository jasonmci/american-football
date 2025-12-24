from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Sequence

from football.engine.play_call import (
    PersonnelGroup,
    OffensePlayType,
    PlayDirection,
    TargetType,
    PassDepth,
)


class Formation(Enum):
    # start small; expand later
    SINGLEBACK = auto()
    I_FORM = auto()
    SHOTGUN = auto()
    PISTOL = auto()
    EMPTY = auto()
    TRIPS = auto()
    BUNCH = auto()


@dataclass(frozen=True, slots=True)
class PlayOption:
    """One selectable row on the card."""

    label: str  # UI label ("Inside Zone", "Mesh", "PA Shot")
    play_type: OffensePlayType
    allowed_directions: tuple[PlayDirection, ...] = (
        PlayDirection.LEFT,
        PlayDirection.MIDDLE,
        PlayDirection.RIGHT,
    )
    default_direction: PlayDirection = PlayDirection.MIDDLE

    # Passing hints (optional)
    default_target: Optional[TargetType] = None
    default_depth: Optional[PassDepth] = None

    # Later: tags for logic / UI (RPO, Motion, Shot, etc.)
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class OffensivePlaycallingCard:
    name: str
    personnel: PersonnelGroup
    formations: tuple[Formation, ...]
    plays: tuple[PlayOption, ...]

    def plays_for_formation(self, formation: Formation) -> Sequence[PlayOption]:
        # For now, all plays are allowed in all formations listed on the card.
        # Later we can add per-play allowed_formations.
        if formation not in self.formations:
            return []
        return self.plays
