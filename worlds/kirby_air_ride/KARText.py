"""Composition of the in-game text-box messages the mod renders.

The mod owns no name tables for other worlds, so the client composes each line here - resolving
item, location and player names with Archipelago's own rules - and ships it as pre-colored
segments through the APData text mailbox.

Two constraints shape everything below. The game font has no lowercase-safe fallback for
non-ASCII, so text is folded to the glyph set `Text_Sanitize` can render; and the wire record
holds `AP_TEXT_SEG_NUM` colored runs in `AP_TEXT_BLOB_LEN` bytes. That blob is sized past what
the screen can show, because the mod owns the fit: it knows the player's font size, wraps onto
three lines and truncates what is left over.
"""

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

# Glyphs the game font renders: alphanumerics go through untouched, and every symbol here is in
# either `Text_Sanitize`'s Shift-JIS table or `Text_ConvertASCIIToShiftJIS`'s Latin one. Anything
# else would emit an undefined code, so it is dropped.
RENDERABLE = frozenset(string.ascii_letters + string.digits + " !\"#$%&'()*+,-./:;<=>?@[]_")

# Derived from Archipelago's own table so a status added upstream is carried through. The labels
# lose their parentheses because they are printed inside the "Hint (x): " prefix, and unspecified
# is dropped: it carries no information, so that hint prints a bare "Hint: ".
HINT_STATUS_LABELS: dict[int, str] = {
    status: name.strip("()") for status, name in status_names.items() if status != HintStatus.HINT_UNSPECIFIED
}

# Server-authored PrintJSON lines worth relaying in-game, with the kind that gates them and the
# color they get: they arrive as one uncolored text run, so the line carries the meaning.
RELAYED_PRINT_JSON: dict[str, tuple[APTextKind, APTextColor]] = {
    "Goal": (APTextKind.STATUS, APTextColor.GREEN),
    "Release": (APTextKind.STATUS, APTextColor.YELLOW),
    "Collect": (APTextKind.STATUS, APTextColor.YELLOW),
    "Chat": (APTextKind.CHAT, APTextColor.DEFAULT),
    "ServerChat": (APTextKind.CHAT, APTextColor.ORANGE),
}

# The server stamps a team number onto its broadcast lines; it is noise on one line of screen.
_TEAM_SUFFIX = re.compile(r"\s*\(Team #\d+\)")


class Segment(NamedTuple):
    """One colored run of a message."""

    text: str
    color: APTextColor = APTextColor.DEFAULT


def _sanitize(text: str) -> str:
    """Fold `text` to the glyphs the game font can render.

    NFKD decomposition turns accented letters into a base letter plus a combining mark, and the
    mark is then dropped along with everything else outside RENDERABLE, so "Cafe\u0301" renders
    "Cafe" rather than losing the word. Runs of whitespace collapse to one space, but leading and
    trailing spaces survive - segments are concatenated, so their edge spaces are the word gaps.
    """
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
    """Resolves JSON message parts into colored segments instead of an ANSI string.

    Subclassing rather than reimplementing keeps item/location/player name lookup and the
    flags-to-color and hint-status-to-color rules identical to the rest of Archipelago: the
    `_handle_*` methods set `node["color"]`/`node["text"]` and then delegate here.
    """

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
    last run - a colored run costs a subtext object in the renderer, so the cap is hard."""
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
    so a long location name gives way before the words around it. This is a transport limit, not
    a display one - the mod does the wrapping and the on-screen truncation."""
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
    """Open a hint line with the "Hint (status): " lead-in, reading the status out of the server's
    own `data` parts - the Hint packet's other fields are receiving/item/found.

    Archipelago's own wording repeats what the reader already knows - one side of every hint is
    always this slot - and would not fit one line. Folding the status into the prefix leaves the
    room the location name needs. It goes in as a real `hint_status` part, so the color comes from
    Archipelago's status table rather than a second table here.
    """
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
    """Strip the server's team stamp and give the line its kind's color.

    A relayed line arrives as one uncolored run, so the color is the only thing marking what it
    is; any run the server did color keeps it.
    """
    return [
        Segment(_TEAM_SUFFIX.sub("", seg.text), color if seg.color == APTextColor.DEFAULT else seg.color)
        for seg in segments
    ]
