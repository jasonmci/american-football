TEAM_STYLE: dict[str, tuple[str, str]] = {
    # abbr: (foreground, background)
    "BAL": ("purple4", "black"),
    "DAL": ("dodger_blue2", "grey93"),
}


def team_style(abbr: str) -> str:
    fg, bg = TEAM_STYLE.get(abbr.upper(), ("white", "grey35"))
    return f"bold {fg} on {bg}"
