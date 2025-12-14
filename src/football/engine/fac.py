from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass(frozen=True)
class FACCard:
    play_result_code: str
    timing: int
    penalty_check: str
    turnover_check: str
    special: Dict[str, Any]


class FACDeck:
    def __init__(self, cards: List[FACCard]) -> None:
        self._cards = cards[:]
        self._index = 0

    def next(self) -> FACCard:
        card = self._cards[self._index]
        self._index = (self._index + 1) % len(self._cards)
        return card
