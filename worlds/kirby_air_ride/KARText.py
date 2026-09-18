from __future__ import annotations

import re
import string
import unicodedata
from typing import Any, NamedTuple

from NetUtils import HintStatus, JSONMessagePart, JSONtoTextParser, add_json_hint_status, status_names

from .KARData import (
    AP_TEXT_BLOB_LEN,
    AP_TEXT_COLOR_BY_NAME,
    AP_TEXT_MESSAGE_SIZE,
    AP_TEXT_SEG_NUM,
    APTextColor,
    APTextKind,
)

# Glyphs the game font renders: alphanumerics go through untouched.
RENDERABLE = frozenset(string.ascii_letters + string.digits + " !\"#$%&'()*+,-./:;<=>?@[]_")

# Derived from Archipelago's own table
HINT_STATUS_LABELS: dict[int, str] = {
    status: name.strip("()") for status, name in status_names.items() if status != HintStatus.HINT_UNSPECIFIED
}

# Server-authored PrintJSON lines worth relaying in-game
RELAYED_PRINT_JSON: dict[str, tuple[APTextKind, APTextColor]] = {
    "Goal": (APTextKind.STATUS, APTextColor.GREEN),
    "Release": (APTextKind.STATUS, APTextColor.YELLOW),
    "Collect": (APTextKind.STATUS, APTextColor.YELLOW),
    "Chat": (APTextKind.CHAT, APTextColor.DEFAULT),
    "ServerChat": (APTextKind.CHAT, APTextColor.ORANGE),
}

# The server stamps a team number onto its broadcast lines
_TEAM_SUFFIX = re.compile(r"\s*\(Team #\d+\)")


class Segment(NamedTuple):
    """One colored run of a message."""

    text: str
    color: APTextColor = APTextColor.DEFAULT


def _sanitize(text: str) -> str:
    """Fold `text` to RENDERABLE glyphs. Collapses whitespace runs."""
    folded = unicodedata.normalize("NFKD", text)
    out: list[str] = []
    prev_space = False
    for raw in folded:
        if raw in RENDERABLE:
            c = raw
        elif raw.isspace():
            c = " "
        else:
            continue
        if c == " " and prev_space:
            continue
        prev_space = c == " "
        out.append(c)
    return "".join(out)


class SegmentCollector(JSONtoTextParser):
    """Resolves JSON message parts into colored segments instead of an ANSI string."""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx)
        self.segments: list[Segment] = []

    def collect(self, parts: list[JSONMessagePart]) -> list[Segment]:
        """Resolve `parts` to colored segments; the base walk's joined string is discarded."""
        self.segments = []
        super().__call__(parts)
        return self.segments

    def _emit(self, node: JSONMessagePart, color: APTextColor) -> str:
        raw = node.get("text", "")
        text = _sanitize(raw)
        # A name written entirely in glyphs the font lacks would otherwise disappear mid-sentence.
        if raw.strip() and not text.strip():
            text = "?"
        if text:
            self.segments.append(Segment(text, color))
        return ""

    def _handle_color(self, node: JSONMessagePart) -> str:
        # A node may carry several codes ("bold;red"); only the ones that name a real color have
        # an in-game equivalent, and the first of those wins.
        for code in node["color"].split(";"):
            if code in AP_TEXT_COLOR_BY_NAME:
                return self._emit(node, AP_TEXT_COLOR_BY_NAME[code])
        return self._emit(node, APTextColor.DEFAULT)

    def _handle_text(self, node: JSONMessagePart) -> str:
        return self._emit(node, APTextColor.DEFAULT)


def _coalesce(segments: list[Segment]) -> list[Segment]:
    """Merge adjacent runs sharing a color, then fold any overflow past AP_TEXT_SEG_NUM into the
    last run.
    """
    merged: list[Segment] = []
    for seg in segments:
        if not seg.text:
            continue
        if merged and merged[-1].color == seg.color:
            merged[-1] = Segment(merged[-1].text + seg.text, seg.color)
        else:
            merged.append(seg)

    if len(merged) > AP_TEXT_SEG_NUM:
        tail = "".join(s.text for s in merged[AP_TEXT_SEG_NUM - 1 :])
        merged = [*merged[: AP_TEXT_SEG_NUM - 1], Segment(tail, merged[AP_TEXT_SEG_NUM - 1].color)]
    return merged


def _truncate(text: str, keep: int) -> str:
    if keep >= len(text):
        return text
    if keep <= 2:
        return text[:keep]
    return text[: keep - 2].rstrip() + ".."


def _fit(segments: list[Segment]) -> list[Segment]:
    """Trim segments until the whole message fits the blob, always cutting the longest run first
    so a long location name gives way before the words around it."""
    segs = list(segments)
    budget = AP_TEXT_BLOB_LEN - len(segs)  # one NUL terminator per segment
    while segs:
        total = sum(len(s.text) for s in segs)
        if total <= budget:
            break
        longest = max(range(len(segs)), key=lambda i: len(segs[i].text))
        over = total - budget
        keep = max(1, len(segs[longest].text) - over)
        if keep >= len(segs[longest].text):
            break  # every run is down to one character; nothing left to give
        segs[longest] = Segment(_truncate(segs[longest].text, keep), segs[longest].color)
    return segs


def pack_message(kind: APTextKind, segments: list[Segment]) -> bytes | None:
    """Serialize one APTextMessage, or None if there is nothing to show.

    Layout: u8 kind, u8 seg_count, u8 colors[AP_TEXT_SEG_NUM], u8 pad[2], then the segment
    strings NUL-terminated back to back in a AP_TEXT_BLOB_LEN byte blob.
    """
    segs = _fit(_coalesce(segments))
    if not segs:
        return None

    colors = bytes(int(s.color) for s in segs) + bytes(AP_TEXT_SEG_NUM - len(segs))
    blob = b"".join(s.text.encode("ascii", "ignore") + b"\0" for s in segs)
    blob = blob[:AP_TEXT_BLOB_LEN].ljust(AP_TEXT_BLOB_LEN, b"\0")

    payload = bytes([int(kind), len(segs)]) + colors + b"\0\0" + blob
    assert len(payload) == AP_TEXT_MESSAGE_SIZE
    return payload


def add_hint_prefix(parts: list[JSONMessagePart], data: list[JSONMessagePart]) -> None:
    """Open a hint line with the "Hint (status):" """
    status = HintStatus.HINT_UNSPECIFIED
    for node in data:
        if node.get("type") == "hint_status":
            try:
                status = HintStatus(int(node.get("hint_status", HintStatus.HINT_UNSPECIFIED)))
            except ValueError:
                # A status this client's NetUtils does not know: print the bare "Hint: " prefix.
                status = HintStatus.HINT_UNSPECIFIED
            break
    label = HINT_STATUS_LABELS.get(status)
    add_json_hint_status(parts, status, text=f"Hint ({label}): " if label else "Hint: ")


def relay_segments(segments: list[Segment], color: APTextColor) -> list[Segment]:
    """Strip the server's team stamp and give the line its kind's color."""
    return [
        Segment(_TEAM_SUFFIX.sub("", seg.text), color if seg.color == APTextColor.DEFAULT else seg.color)
        for seg in segments
    ]
