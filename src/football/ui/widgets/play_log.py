from __future__ import annotations

from textual.widgets import RichLog


class PlayLog(RichLog):
    """Scrollable play-by-play log."""

    def on_mount(self) -> None:
        # ensure it behaves like a tailing log
        self.auto_scroll = True
        self.highlight = False
        self.markup = True
        self.wrap = True

    def add_line(self, message: str) -> None:
        """Append a line to the log."""
        # RichLog already appends; this keeps a stable API for the app.
        self.write(message)
