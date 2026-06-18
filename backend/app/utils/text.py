"""Shared text helpers."""
from __future__ import annotations

import re

_EM_DASH = "\u2014"


def strip_em_dashes(text: str) -> str:
    """Replace em dashes with comma spacing (never emit em dashes in user-facing copy)."""
    if not text or _EM_DASH not in text:
        return text
    return re.sub(r"\s*—\s*", ", ", text)
