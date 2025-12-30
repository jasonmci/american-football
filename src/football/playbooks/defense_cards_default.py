from __future__ import annotations

from typing import Dict, Tuple

from football.engine.play_call import DefenseFront, DefensePlayFlavor, CoverageShell
from football.playbooks.defense_card import DefensivePlaycallingCard, DefenseOption


def _opt(
    label: str,
    front: DefenseFront,
    flavor: DefensePlayFlavor,
    coverage: CoverageShell,
    *,
    tags: Tuple[str, ...] = (),
    statis: str | None = None,
) -> DefenseOption:
    t = tuple(tags)
    if statis:
        t = t + (f"statis:{statis}",)
    return DefenseOption(
        label=label,
        front=front,
        flavor=flavor,
        coverage=coverage,
        tags=t,
    )


def _card(name: str, front: DefenseFront, calls: Tuple[DefenseOption, ...]) -> DefensivePlaycallingCard:
    return DefensivePlaycallingCard(name=name, front=front, calls=calls)


def build_default_defense_cards() -> Dict[DefenseFront, DefensivePlaycallingCard]:
    cards: Dict[DefenseFront, DefensivePlaycallingCard] = {}

    # ---- 4-3 base ----
    cards[DefenseFront.FOUR_THREE] = _card(
        "4-3 Base",
        DefenseFront.FOUR_THREE,
        (
            _opt(
                "Base Cover 3",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_3,
                tags=("base",),
                statis="BASE",
            ),
            _opt(
                "Base Cover 2",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_2,
                tags=("base",),
                statis="BASE",
            ),
            _opt(
                "Run Focus (8-man)",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.RUN_FOCUS,
                CoverageShell.COVER_1,
                tags=("run",),
                statis="RUN_FOCUS",
            ),
            _opt(
                "Run Blitz",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.RUN_BLITZ,
                CoverageShell.ZERO,
                tags=("run", "blitz"),
                statis="RUN_BLITZ",
            ),
            _opt(
                "Pass Focus (Cover 2)",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.PASS_FOCUS,
                CoverageShell.COVER_2,
                tags=("pass",),
                statis="PASS_FOCUS",
            ),
            _opt(
                "Pass Blitz (Cover 1)",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.PASS_BLITZ,
                CoverageShell.COVER_1,
                tags=("pass", "blitz"),
                statis="PASS_BLITZ",
            ),
            _opt(
                "All Out Blitz (0)",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.ALL_OUT_BLITZ,
                CoverageShell.ZERO,
                tags=("blitz", "highrisk"),
                statis="ALL_OUT",
            ),
            _opt(
                "Contain (C3)",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.CONTAIN,
                CoverageShell.COVER_3,
                tags=("contain",),
                statis="CONTAIN",
            ),
            _opt(
                "QB Spy (C1)",
                DefenseFront.FOUR_THREE,
                DefensePlayFlavor.QB_SPY,
                CoverageShell.COVER_1,
                tags=("spy",),
                statis="SPY",
            ),
        ),
    )

    # ---- 3-4 base ----
    cards[DefenseFront.THREE_FOUR] = _card(
        "3-4 Base",
        DefenseFront.THREE_FOUR,
        (
            _opt(
                "Base Cover 4",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_4,
                tags=("base",),
                statis="BASE",
            ),
            _opt(
                "Base Cover 3",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_3,
                tags=("base",),
                statis="BASE",
            ),
            _opt(
                "Run Focus (C1)",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.RUN_FOCUS,
                CoverageShell.COVER_1,
                tags=("run",),
                statis="RUN_FOCUS",
            ),
            _opt(
                "Run Blitz (0)",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.RUN_BLITZ,
                CoverageShell.ZERO,
                tags=("run", "blitz"),
                statis="RUN_BLITZ",
            ),
            _opt(
                "Pass Focus (C4)",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.PASS_FOCUS,
                CoverageShell.COVER_4,
                tags=("pass",),
                statis="PASS_FOCUS",
            ),
            _opt(
                "Pass Blitz (C1)",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.PASS_BLITZ,
                CoverageShell.COVER_1,
                tags=("pass", "blitz"),
                statis="PASS_BLITZ",
            ),
            _opt(
                "Contain (C6)",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.CONTAIN,
                CoverageShell.COVER_6,
                tags=("contain",),
                statis="CONTAIN",
            ),
            _opt(
                "QB Spy (C1)",
                DefenseFront.THREE_FOUR,
                DefensePlayFlavor.QB_SPY,
                CoverageShell.COVER_1,
                tags=("spy",),
                statis="SPY",
            ),
        ),
    )

    # ---- Nickel ----
    cards[DefenseFront.NICKEL] = _card(
        "Nickel",
        DefenseFront.NICKEL,
        (
            _opt(
                "Nickel Cover 2",
                DefenseFront.NICKEL,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_2,
                tags=("nickel",),
                statis="BASE",
            ),
            _opt(
                "Nickel Cover 3",
                DefenseFront.NICKEL,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_3,
                tags=("nickel",),
                statis="BASE",
            ),
            _opt(
                "Pass Focus (C4)",
                DefenseFront.NICKEL,
                DefensePlayFlavor.PASS_FOCUS,
                CoverageShell.COVER_4,
                tags=("pass", "dbs"),
                statis="PASS_FOCUS",
            ),
            _opt(
                "Pass Blitz (C1)",
                DefenseFront.NICKEL,
                DefensePlayFlavor.PASS_BLITZ,
                CoverageShell.COVER_1,
                tags=("pass", "blitz"),
                statis="PASS_BLITZ",
            ),
            _opt(
                "All Out Blitz (0)",
                DefenseFront.NICKEL,
                DefensePlayFlavor.ALL_OUT_BLITZ,
                CoverageShell.ZERO,
                tags=("blitz", "highrisk"),
                statis="ALL_OUT",
            ),
            _opt(
                "Contain (C3)",
                DefenseFront.NICKEL,
                DefensePlayFlavor.CONTAIN,
                CoverageShell.COVER_3,
                tags=("contain",),
                statis="CONTAIN",
            ),
        ),
    )

    # ---- Dime ----
    cards[DefenseFront.DIME] = _card(
        "Dime",
        DefenseFront.DIME,
        (
            _opt(
                "Dime Cover 4",
                DefenseFront.DIME,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_4,
                tags=("dime",),
                statis="BASE",
            ),
            _opt(
                "Dime Cover 6",
                DefenseFront.DIME,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_6,
                tags=("dime",),
                statis="BASE",
            ),
            _opt(
                "Prevent-ish (C4)",
                DefenseFront.DIME,
                DefensePlayFlavor.PREVENT,
                CoverageShell.COVER_4,
                tags=("prevent",),
                statis="PREVENT",
            ),
            _opt(
                "Pass Focus (C4)",
                DefenseFront.DIME,
                DefensePlayFlavor.PASS_FOCUS,
                CoverageShell.COVER_4,
                tags=("pass",),
                statis="PASS_FOCUS",
            ),
            _opt(
                "Pass Blitz (C1)",
                DefenseFront.DIME,
                DefensePlayFlavor.PASS_BLITZ,
                CoverageShell.COVER_1,
                tags=("pass", "blitz"),
                statis="PASS_BLITZ",
            ),
        ),
    )

    # ---- Quarter (7 DB) ----
    cards[DefenseFront.QUARTER] = _card(
        "Quarter (7 DB)",
        DefenseFront.QUARTER,
        (
            _opt(
                "Quarter Cover 4",
                DefenseFront.QUARTER,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_4,
                tags=("7db",),
                statis="BASE",
            ),
            _opt(
                "Prevent (C4)",
                DefenseFront.QUARTER,
                DefensePlayFlavor.PREVENT,
                CoverageShell.COVER_4,
                tags=("prevent",),
                statis="PREVENT",
            ),
            _opt(
                "Prevent (C3)",
                DefenseFront.QUARTER,
                DefensePlayFlavor.PREVENT,
                CoverageShell.COVER_3,
                tags=("prevent",),
                statis="PREVENT",
            ),
            _opt(
                "Contain (C4)",
                DefenseFront.QUARTER,
                DefensePlayFlavor.CONTAIN,
                CoverageShell.COVER_4,
                tags=("contain",),
                statis="CONTAIN",
            ),
        ),
    )

    # ---- Goal line ----
    cards[DefenseFront.GOAL_LINE] = _card(
        "Goal Line",
        DefenseFront.GOAL_LINE,
        (
            _opt(
                "Sold Out (0)",
                DefenseFront.GOAL_LINE,
                DefensePlayFlavor.GOAL_LINE_SOLD_OUT,
                CoverageShell.ZERO,
                tags=("goalline", "run"),
                statis="GOAL_LINE",
            ),
            _opt(
                "Run Blitz (0)",
                DefenseFront.GOAL_LINE,
                DefensePlayFlavor.RUN_BLITZ,
                CoverageShell.ZERO,
                tags=("goalline", "blitz"),
                statis="RUN_BLITZ",
            ),
            _opt(
                "Base (C1)",
                DefenseFront.GOAL_LINE,
                DefensePlayFlavor.BASE,
                CoverageShell.COVER_1,
                tags=("goalline",),
                statis="BASE",
            ),
            _opt(
                "Pass Focus (C2)",
                DefenseFront.GOAL_LINE,
                DefensePlayFlavor.PASS_FOCUS,
                CoverageShell.COVER_2,
                tags=("goalline", "pass"),
                statis="PASS_FOCUS",
            ),
        ),
    )

    return cards


DEFENSIVE_CARDS: Dict[DefenseFront, DefensivePlaycallingCard] = build_default_defense_cards()
