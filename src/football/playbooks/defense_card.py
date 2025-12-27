from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from football.engine.play_call import DefenseFront, DefensePlayFlavor, CoverageShell


@dataclass(frozen=True, slots=True)
class DefenseOption:
    label: str
    front: DefenseFront
    flavor: DefensePlayFlavor
    coverage: CoverageShell
    tags: Tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DefensivePlaycallingCard:
    name: str
    front: DefenseFront
    calls: Tuple[DefenseOption, ...]
