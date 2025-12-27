# src/football/playbooks/offense_cards_default.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

from football.engine.play_call import (
    PersonnelGroup,
    OffensePlayType,
    PlayDirection,
)

# Targets / depths are optional; import only if you have them
try:
    from football.engine.play_call import TargetType, PassDepth
except Exception:  # pragma: no cover
    TargetType = None  # type: ignore
    PassDepth = None  # type: ignore

from football.playbooks.offense_card import (
    OffensivePlaycallingCard,
    PlayOption,
    Formation,
)

# -----------------------------
# Helpers: safe enum access
# -----------------------------


def _pg(name: str) -> Optional[PersonnelGroup]:
    return getattr(PersonnelGroup, name, None)


def _pt(name: str) -> Optional[OffensePlayType]:
    return getattr(OffensePlayType, name, None)


def _tgt(name: str):
    if TargetType is None:
        return None
    return getattr(TargetType, name, None)


def _depth(name: str):
    if PassDepth is None:
        return None
    return getattr(PassDepth, name, None)


def _opt(
    label: str,
    play_type_name: str,
    *,
    statis: str,
    tags: Tuple[str, ...] = (),
    allowed_dirs: Tuple[PlayDirection, ...] = (
        PlayDirection.LEFT,
        PlayDirection.MIDDLE,
        PlayDirection.RIGHT,
    ),
    default_dir: PlayDirection = PlayDirection.MIDDLE,
    default_target: Optional[str] = None,
    default_depth: Optional[str] = None,
) -> Optional[PlayOption]:
    """Create a PlayOption if the OffensePlayType exists; otherwise return None."""
    pt = _pt(play_type_name)
    if pt is None:
        return None

    # Notes are shown in the playbook view; we embed statis mapping here.
    merged_tags = tuple(tags) + (f"statis:{statis}",)

    return PlayOption(
        label=label,
        play_type=pt,
        allowed_directions=allowed_dirs,
        default_direction=default_dir,
        default_target=_tgt(default_target) if default_target else None,
        default_depth=_depth(default_depth) if default_depth else None,
        tags=merged_tags,
    )


def _card(
    name: str,
    personnel_name: str,
    formations: Tuple[Formation, ...],
    plays: Iterable[Optional[PlayOption]],
) -> Optional[OffensivePlaycallingCard]:
    pg = _pg(personnel_name)
    if pg is None:
        return None

    filtered = tuple(p for p in plays if p is not None)
    return OffensivePlaycallingCard(
        name=name,
        personnel=pg,
        formations=formations,
        plays=filtered,
    )


# -----------------------------
# Default Cards (broad coverage)
# -----------------------------


def build_default_offense_cards() -> Dict[PersonnelGroup, OffensivePlaycallingCard]:
    cards: Dict[PersonnelGroup, OffensivePlaycallingCard] = {}

    # ---- P11 (3WR/1TE/1RB) ----
    c = _card(
        name="11 Personnel Core",
        personnel_name="P11",
        formations=(Formation.SHOTGUN, Formation.SINGLEBACK, Formation.TRIPS, Formation.BUNCH),
        plays=(
            # Runs
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run", "inside")),
            _opt("Outside Zone", "OUTSIDE_ZONE", statis="OUTSIDE_RUN", tags=("run", "outside")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "gap")),
            _opt("Counter", "COUNTER", statis="INSIDE_RUN", tags=("run", "counter")),
            _opt("Draw", "DRAW", statis="DRAW", tags=("run", "shotgun")),
            # Quick / short pass game
            _opt(
                "Quick Slant", "QUICK_SLANT", statis="SHORT_PASS",
                tags=("pass", "quick"), default_target="WR1", default_depth="QUICK"
            ),
            _opt(
                "Stick", "STICK", statis="SHORT_PASS",
                tags=("pass", "quick"), default_target="TE1", default_depth="QUICK",
            ),
            _opt(
                "Mesh", "MESH", statis="SHORT_PASS",
                tags=("pass", "short"), default_target="WR2", default_depth="SHORT"
            ),
            _opt(
                "Spacing", "SPACING", statis="SHORT_PASS",
                tags=("pass", "short"), default_target="WR3", default_depth="SHORT",
            ),
            # Intermediate / shot plays
            _opt(
                "Seam",
                "SEAM",
                statis="INTERMEDIATE_PASS",
                tags=("pass", "intermediate"),
                default_target="TE1",
                default_depth="INTERMEDIATE",
            ),
            _opt(
                "Dig",
                "DIG",
                statis="INTERMEDIATE_PASS",
                tags=("pass", "intermediate"),
                default_target="WR1",
                default_depth="INTERMEDIATE",
            ),
            _opt("Post", "POST", statis="DEEP_SHOT", tags=("pass", "deep"), default_target="WR1", default_depth="DEEP"),
            _opt(
                "Go/Fade", "FADE", statis="DEEP_SHOT", tags=("pass", "deep"), default_target="WR1", default_depth="DEEP"
            ),
            # Screens / play action
            _opt(
                "RB Screen",
                "RB_SCREEN",
                statis="SCREEN_PASS",
                tags=("screen",),
                default_target="RB1",
                default_depth="QUICK",
            ),
            _opt(
                "Play Action Shot",
                "PLAY_ACTION_SHOT",
                statis="PLAY_ACTION",
                tags=("playaction", "shot"),
                default_target="WR1",
                default_depth="DEEP",
            ),
            _opt(
                "Bootleg",
                "BOOTLEG",
                statis="PLAY_ACTION",
                tags=("playaction",),
                default_target="TE1",
                default_depth="SHORT",
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P12 (2TE/2WR/1RB) ----
    c = _card(
        name="12 Personnel Core",
        personnel_name="P12",
        formations=(Formation.SINGLEBACK, Formation.SHOTGUN, Formation.BUNCH),
        plays=(
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run", "inside")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "gap")),
            _opt("Counter", "COUNTER", statis="INSIDE_RUN", tags=("run", "counter")),
            _opt("Outside Zone", "OUTSIDE_ZONE", statis="OUTSIDE_RUN", tags=("run", "outside")),
            _opt(
                "TE Seam",
                "SEAM",
                statis="INTERMEDIATE_PASS",
                tags=("pass", "intermediate"),
                default_target="TE1",
                default_depth="INTERMEDIATE",
            ),
            _opt(
                "Crossers",
                "CROSSERS",
                statis="INTERMEDIATE_PASS",
                tags=("pass", "intermediate"),
                default_target="WR1",
                default_depth="INTERMEDIATE",
            ),
            _opt(
                "Bootleg",
                "BOOTLEG",
                statis="PLAY_ACTION",
                tags=("playaction",),
                default_target="TE1",
                default_depth="SHORT",
            ),
            _opt(
                "Play Action Short",
                "PLAY_ACTION_SHORT",
                statis="PLAY_ACTION",
                tags=("playaction", "short"),
                default_target="TE2",
                default_depth="SHORT",
            ),
            _opt(
                "TE Screen",
                "TE_SCREEN",
                statis="SCREEN_PASS",
                tags=("screen",),
                default_target="TE1",
                default_depth="QUICK",
            ),
            _opt(
                "RB Screen",
                "RB_SCREEN",
                statis="SCREEN_PASS",
                tags=("screen",),
                default_target="RB1",
                default_depth="QUICK",
            ),
            _opt("Post", "POST", statis="DEEP_SHOT", tags=("pass", "deep"), default_target="WR1", default_depth="DEEP"),
            _opt("Fade", "FADE", statis="DEEP_SHOT", tags=("pass", "deep"), default_target="WR1", default_depth="DEEP"),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P21 (2RB/1TE/2WR) ----
    c = _card(
        name="21 Personnel Core",
        personnel_name="P21",
        formations=(Formation.I_FORM, Formation.SINGLEBACK, Formation.PISTOL),
        plays=(
            _opt("ISO", "ISO", statis="INSIDE_RUN", tags=("run", "iso")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "gap")),
            _opt("Counter", "COUNTER", statis="INSIDE_RUN", tags=("run", "counter")),
            _opt("Toss", "TOSS", statis="OUTSIDE_RUN", tags=("run", "outside")),
            _opt("Sweep", "SWEEP", statis="OUTSIDE_RUN", tags=("run", "outside")),
            _opt(
                "Play Action Short",
                "PLAY_ACTION_SHORT",
                statis="PLAY_ACTION",
                tags=("playaction", "short"),
                default_target="TE1",
                default_depth="SHORT",
            ),
            _opt(
                "Play Action Shot",
                "PLAY_ACTION_SHOT",
                statis="PLAY_ACTION",
                tags=("playaction", "shot"),
                default_target="WR1",
                default_depth="DEEP",
            ),
            _opt(
                "RB Screen",
                "RB_SCREEN",
                statis="SCREEN_PASS",
                tags=("screen",),
                default_target="RB1",
                default_depth="QUICK",
            ),
            _opt(
                "Flat", "FLAT", statis="SHORT_PASS", tags=("pass", "quick"), default_target="RB2", default_depth="QUICK"
            ),
            _opt(
                "Deep Cross",
                "DEEP_CROSS",
                statis="DEEP_SHOT",
                tags=("pass", "deep"),
                default_target="WR1",
                default_depth="DEEP",
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P22 (2RB/2TE/1WR) ----
    c = _card(
        name="22 Personnel Heavy",
        personnel_name="P22",
        formations=(Formation.I_FORM, Formation.SINGLEBACK),
        plays=(
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run", "inside")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "gap")),
            _opt("Counter", "COUNTER", statis="INSIDE_RUN", tags=("run", "counter")),
            _opt("Toss", "TOSS", statis="OUTSIDE_RUN", tags=("run", "outside")),
            _opt(
                "Play Action Short",
                "PLAY_ACTION_SHORT",
                statis="PLAY_ACTION",
                tags=("playaction", "short"),
                default_target="TE1",
                default_depth="SHORT",
            ),
            _opt(
                "TE Seam",
                "SEAM",
                statis="INTERMEDIATE_PASS",
                tags=("pass", "intermediate"),
                default_target="TE1",
                default_depth="INTERMEDIATE",
            ),
            _opt(
                "RB Screen",
                "RB_SCREEN",
                statis="SCREEN_PASS",
                tags=("screen",),
                default_target="RB1",
                default_depth="QUICK",
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P10 (4WR/1TE/0RB) ----
    c = _card(
        name="10 Personnel Spread",
        personnel_name="P10",
        formations=(Formation.SHOTGUN, Formation.TRIPS, Formation.EMPTY),
        plays=(
            _opt(
                "Quick Slant",
                "QUICK_SLANT",
                statis="SHORT_PASS",
                tags=("pass", "quick"),
                default_target="WR1",
                default_depth="QUICK",
            ),
            _opt(
                "Hitch",
                "HITCH",
                statis="SHORT_PASS",
                tags=("pass", "quick"),
                default_target="WR2",
                default_depth="QUICK",
            ),
            _opt(
                "Mesh", "MESH", statis="SHORT_PASS", tags=("pass", "short"), default_target="WR3", default_depth="SHORT"
            ),
            _opt(
                "Four Verts",
                "FOUR_VERTS",
                statis="DEEP_SHOT",
                tags=("pass", "deep"),
                default_target="WR1",
                default_depth="DEEP",
            ),
            _opt("Post", "POST", statis="DEEP_SHOT", tags=("pass", "deep"), default_target="WR1", default_depth="DEEP"),
            _opt(
                "Corner",
                "CORNER",
                statis="DEEP_SHOT",
                tags=("pass", "deep"),
                default_target="WR2",
                default_depth="DEEP",
            ),
            _opt(
                "WR Screen",
                "WR_SCREEN",
                statis="SCREEN_PASS",
                tags=("screen",),
                default_target="WR1",
                default_depth="QUICK",
            ),
            _opt("QB Draw", "QB_DRAW", statis="DRAW", tags=("run", "qb")),
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run", "lightbox")),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P00 (5WR Empty) ----
    c = _card(
        name="00 Personnel Empty",
        personnel_name="P00",
        formations=(Formation.EMPTY, Formation.SHOTGUN),
        plays=(
            _opt("Quick Slant", "QUICK_SLANT", statis="SHORT_PASS", tags=("pass", "quick")),
            _opt("Hitch", "HITCH", statis="SHORT_PASS", tags=("pass", "quick")),
            _opt("Spacing", "SPACING", statis="SHORT_PASS", tags=("pass", "short")),
            _opt("Mesh", "MESH", statis="SHORT_PASS", tags=("pass", "short")),
            _opt("Four Verts", "FOUR_VERTS", statis="DEEP_SHOT", tags=("pass", "deep")),
            _opt("Post", "POST", statis="DEEP_SHOT", tags=("pass", "deep")),
            _opt("Corner", "CORNER", statis="DEEP_SHOT", tags=("pass", "deep")),
            _opt("QB Draw", "QB_DRAW", statis="DRAW", tags=("run", "qb")),
            _opt(
                "Spike",
                "SPIKE",
                statis="SPIKE",
                tags=("clock",),
                allowed_dirs=(PlayDirection.MIDDLE,),
                default_dir=PlayDirection.MIDDLE,
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P01 / P02 (Empty-ish with RB/TE variants) ----
    c = _card(
        name="01 Personnel (4WR/1RB)",
        personnel_name="P01",
        formations=(Formation.SHOTGUN, Formation.EMPTY),
        plays=(
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run",)),
            _opt("Draw", "DRAW", statis="DRAW", tags=("run",)),
            _opt("RB Screen", "RB_SCREEN", statis="SCREEN_PASS", tags=("screen",)),
            _opt("Quick Slant", "QUICK_SLANT", statis="SHORT_PASS", tags=("pass", "quick")),
            _opt("Mesh", "MESH", statis="SHORT_PASS", tags=("pass", "short")),
            _opt("Four Verts", "FOUR_VERTS", statis="DEEP_SHOT", tags=("pass", "deep")),
        ),
    )
    if c:
        cards[c.personnel] = c

    c = _card(
        name="02 Personnel (4WR/1TE)",
        personnel_name="P02",
        formations=(Formation.SHOTGUN, Formation.EMPTY),
        plays=(
            _opt("TE Seam", "SEAM", statis="INTERMEDIATE_PASS", tags=("pass", "intermediate")),
            _opt("Stick", "STICK", statis="SHORT_PASS", tags=("pass", "quick")),
            _opt("Crossers", "CROSSERS", statis="INTERMEDIATE_PASS", tags=("pass", "intermediate")),
            _opt("Four Verts", "FOUR_VERTS", statis="DEEP_SHOT", tags=("pass", "deep")),
            _opt("WR Screen", "WR_SCREEN", statis="SCREEN_PASS", tags=("screen",)),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P13 (1RB/3TE/1WR) ----
    c = _card(
        name="13 Personnel Heavy",
        personnel_name="P13",
        formations=(Formation.SINGLEBACK, Formation.I_FORM),
        plays=(
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run", "inside")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "gap")),
            _opt("Counter", "COUNTER", statis="INSIDE_RUN", tags=("run", "counter")),
            _opt("Play Action Short", "PLAY_ACTION_SHORT", statis="PLAY_ACTION", tags=("playaction", "short")),
            _opt("TE Seam", "SEAM", statis="INTERMEDIATE_PASS", tags=("pass", "intermediate")),
            _opt("TE Screen", "TE_SCREEN", statis="SCREEN_PASS", tags=("screen",)),
            _opt(
                "Kneel",
                "KNEEL",
                statis="KNEEL",
                tags=("clock",),
                allowed_dirs=(PlayDirection.MIDDLE,),
                default_dir=PlayDirection.MIDDLE,
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P20 (2RB/0TE/3WR) ----
    c = _card(
        name="20 Personnel Spread Run/Pass",
        personnel_name="P20",
        formations=(Formation.SHOTGUN, Formation.PISTOL, Formation.TRIPS),
        plays=(
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run",)),
            _opt("Outside Zone", "OUTSIDE_ZONE", statis="OUTSIDE_RUN", tags=("run",)),
            _opt("Draw", "DRAW", statis="DRAW", tags=("run",)),
            _opt("RB Screen", "RB_SCREEN", statis="SCREEN_PASS", tags=("screen",)),
            _opt("Quick Slant", "QUICK_SLANT", statis="SHORT_PASS", tags=("pass", "quick")),
            _opt("Mesh", "MESH", statis="SHORT_PASS", tags=("pass", "short")),
            _opt("Post", "POST", statis="DEEP_SHOT", tags=("pass", "deep")),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P23 (2RB/3TE/0WR) goal-line-ish ----
    c = _card(
        name="23 Personnel Goal-Line",
        personnel_name="P23",
        formations=(Formation.I_FORM, Formation.SINGLEBACK),
        plays=(
            _opt(
                "QB Sneak",
                "QB_SNEAK",
                statis="QB_SNEAK",
                tags=("run", "shortyardage"),
                allowed_dirs=(PlayDirection.MIDDLE,),
                default_dir=PlayDirection.MIDDLE,
            ),
            _opt("ISO", "ISO", statis="INSIDE_RUN", tags=("run", "shortyardage")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "shortyardage")),
            _opt("Play Action Short", "PLAY_ACTION_SHORT", statis="PLAY_ACTION", tags=("playaction", "goalline")),
            _opt("TE Fade", "FADE", statis="DEEP_SHOT", tags=("pass", "goalline")),
            _opt(
                "Kneel",
                "KNEEL",
                statis="KNEEL",
                tags=("clock",),
                allowed_dirs=(PlayDirection.MIDDLE,),
                default_dir=PlayDirection.MIDDLE,
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    # ---- P30 / P31 / P32 (3RB packages) ----
    c = _card(
        name="30 Personnel (3RB/0TE/2WR)",
        personnel_name="P30",
        formations=(Formation.I_FORM, Formation.PISTOL, Formation.SINGLEBACK),
        plays=(
            _opt("Inside Zone", "INSIDE_ZONE", statis="INSIDE_RUN", tags=("run",)),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run",)),
            _opt("Toss", "TOSS", statis="OUTSIDE_RUN", tags=("run",)),
            _opt("RB Screen", "RB_SCREEN", statis="SCREEN_PASS", tags=("screen",)),
            _opt("Play Action Short", "PLAY_ACTION_SHORT", statis="PLAY_ACTION", tags=("playaction",)),
        ),
    )
    if c:
        cards[c.personnel] = c

    c = _card(
        name="31 Personnel (3RB/1TE/1WR)",
        personnel_name="P31",
        formations=(Formation.I_FORM, Formation.SINGLEBACK),
        plays=(
            _opt("ISO", "ISO", statis="INSIDE_RUN", tags=("run",)),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run",)),
            _opt("Counter", "COUNTER", statis="INSIDE_RUN", tags=("run",)),
            _opt("Play Action Short", "PLAY_ACTION_SHORT", statis="PLAY_ACTION", tags=("playaction",)),
            _opt("TE Seam", "SEAM", statis="INTERMEDIATE_PASS", tags=("pass",)),
        ),
    )
    if c:
        cards[c.personnel] = c

    c = _card(
        name="32 Personnel (3RB/2TE/0WR) Jumbo",
        personnel_name="P32",
        formations=(Formation.I_FORM, Formation.SINGLEBACK),
        plays=(
            _opt(
                "QB Sneak",
                "QB_SNEAK",
                statis="QB_SNEAK",
                tags=("run", "shortyardage"),
                allowed_dirs=(PlayDirection.MIDDLE,),
                default_dir=PlayDirection.MIDDLE,
            ),
            _opt("ISO", "ISO", statis="INSIDE_RUN", tags=("run", "shortyardage")),
            _opt("Power", "POWER", statis="INSIDE_RUN", tags=("run", "shortyardage")),
            _opt("Play Action Short", "PLAY_ACTION_SHORT", statis="PLAY_ACTION", tags=("playaction", "goalline")),
            _opt(
                "Kneel",
                "KNEEL",
                statis="KNEEL",
                tags=("clock",),
                allowed_dirs=(PlayDirection.MIDDLE,),
                default_dir=PlayDirection.MIDDLE,
            ),
        ),
    )
    if c:
        cards[c.personnel] = c

    return cards


# This is what the UI imports today
OFFENSIVE_CARDS: Dict[PersonnelGroup, OffensivePlaycallingCard] = build_default_offense_cards()
