from football.engine.play_call import PersonnelGroup, OffensePlayType, PlayDirection, TargetType, PassDepth
from football.playbooks.offense_card import OffensivePlaycallingCard, PlayOption, Formation


CARD_11 = OffensivePlaycallingCard(
    name="11 Personnel Core",
    personnel=PersonnelGroup.P11,
    formations=(Formation.SHOTGUN, Formation.SINGLEBACK, Formation.TRIPS),
    plays=(
        PlayOption("Inside Zone", OffensePlayType.INSIDE_ZONE, tags=("run", "inside")),
        PlayOption("Outside Zone", OffensePlayType.OUTSIDE_ZONE, tags=("run", "outside")),
        PlayOption("Power", OffensePlayType.POWER, tags=("run", "inside")),
        PlayOption(
            "Quick Slant",
            OffensePlayType.QUICK_SLANT,
            default_target=TargetType.WR1,
            default_depth=PassDepth.QUICK,
            tags=("pass", "quick"),
        ),
        PlayOption(
            "Mesh",
            OffensePlayType.MESH,
            default_target=TargetType.WR2,
            default_depth=PassDepth.SHORT,
            tags=("pass", "short"),
        ),
        PlayOption(
            "Seam",
            OffensePlayType.SEAM,
            default_target=TargetType.TE1,
            default_depth=PassDepth.INTERMEDIATE,
            tags=("pass", "intermediate"),
        ),
        PlayOption(
            "Post",
            OffensePlayType.POST,
            default_target=TargetType.WR1,
            default_depth=PassDepth.DEEP,
            tags=("pass", "deep"),
        ),
        PlayOption(
            "RB Screen",
            OffensePlayType.RB_SCREEN,
            default_target=TargetType.RB1,
            default_depth=PassDepth.QUICK,
            tags=("screen",),
        ),
        PlayOption(
            "Play Action Shot",
            OffensePlayType.PLAY_ACTION_SHOT,
            default_target=TargetType.WR1,
            default_depth=PassDepth.DEEP,
            tags=("playaction", "shot"),
        ),
    ),
)

CARD_12 = OffensivePlaycallingCard(
    name="12 Personnel Core",
    personnel=PersonnelGroup.P12,
    formations=(Formation.SINGLEBACK, Formation.SHOTGUN, Formation.BUNCH),
    plays=(
        PlayOption("Inside Zone", OffensePlayType.INSIDE_ZONE),
        PlayOption("Counter", OffensePlayType.COUNTER),
        PlayOption(
            "Bootleg",
            OffensePlayType.BOOTLEG,
            default_target=TargetType.TE1,
            default_depth=PassDepth.SHORT,
            tags=("playaction",),
        ),
        PlayOption(
            "Crossers", OffensePlayType.CROSSERS, default_target=TargetType.WR1, default_depth=PassDepth.INTERMEDIATE
        ),
        PlayOption(
            "TE Seam", OffensePlayType.SEAM, default_target=TargetType.TE1, default_depth=PassDepth.INTERMEDIATE
        ),
        PlayOption("Fade", OffensePlayType.FADE, default_target=TargetType.WR1, default_depth=PassDepth.DEEP),
        PlayOption(
            "TE Screen",
            OffensePlayType.TE_SCREEN,
            default_target=TargetType.TE1,
            default_depth=PassDepth.QUICK,
            tags=("screen",),
        ),
    ),
)

CARD_21 = OffensivePlaycallingCard(
    name="21 Personnel Core",
    personnel=PersonnelGroup.P21,
    formations=(Formation.I_FORM, Formation.SINGLEBACK, Formation.PISTOL),
    plays=(
        PlayOption("ISO", OffensePlayType.ISO),
        PlayOption("Power", OffensePlayType.POWER),
        PlayOption("Toss", OffensePlayType.TOSS),
        PlayOption(
            "Play Action Short",
            OffensePlayType.PLAY_ACTION_SHORT,
            default_target=TargetType.TE1,
            default_depth=PassDepth.SHORT,
        ),
        PlayOption(
            "Deep Cross", OffensePlayType.DEEP_CROSS, default_target=TargetType.WR1, default_depth=PassDepth.DEEP
        ),
        PlayOption(
            "RB Screen", OffensePlayType.RB_SCREEN, default_target=TargetType.RB1, default_depth=PassDepth.QUICK
        ),
    ),
)

OFFENSIVE_CARDS = {
    PersonnelGroup.P11: CARD_11,
    PersonnelGroup.P12: CARD_12,
    PersonnelGroup.P21: CARD_21,
}
