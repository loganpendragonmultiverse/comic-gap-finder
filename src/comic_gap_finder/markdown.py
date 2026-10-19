from __future__ import annotations

import re


def literal(value: str) -> str:
    """Render authored text literally; JSON retains exact line endings."""
    text = value.replace("\r", r"\r").replace("\n", r"\n")
    runs = re.findall(r"`+", text)
    fence = "`" * (max(map(len, runs), default=0) + 1)
    padding = " " if text.startswith(("`", " ")) or text.endswith(("`", " ")) else ""
    return fence + padding + text + padding + fence
