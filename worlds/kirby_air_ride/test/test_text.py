"""KARText packs client messages into the mod's fixed APTextMessage buffer. Every step is a pure
function over a byte layout nothing else validates, so a miscount here corrupts the struct silently."""

import unittest
from typing import cast

from NetUtils import HintStatus, JSONMessagePart, JSONTypes, add_json_text

from ..KARData import (
    AP_TEXT_BLOB_LEN,
    AP_TEXT_MESSAGE_SIZE,
    AP_TEXT_SEG_NUM,
    APTextColor,
    APTextKind,
)
from ..KARText import (
    HINT_STATUS_LABELS,
    Segment,
    SegmentCollector,
    _coalesce,
    _fit,
    _sanitize,
    _truncate,
    add_hint_prefix,
    pack_message,
    relay_segments,
)


def packed(kind: APTextKind, segments: list[Segment]) -> bytes:
    """pack_message, asserting it produced something so the byte checks read straight through."""
    payload = pack_message(kind, segments)
    assert payload is not None, "expected a packed message"
    return payload


def hint_data(status: int) -> list[JSONMessagePart]:
    """The `data` block a PrintJSON hint carries, with a raw status so unknown values can be fed in."""
    return [cast(JSONMessagePart, {"type": JSONTypes.hint_status, "hint_status": status})]


def unpack(payload: bytes) -> tuple[int, list[Segment]]:
    """Decode an APTextMessage back into its kind and segments, the way the mod reads it."""
    kind, count = payload[0], payload[1]
    colors = payload[2 : 2 + AP_TEXT_SEG_NUM]
    blob = payload[2 + AP_TEXT_SEG_NUM + 2 :]
    texts = blob.split(b"\0")[:count]
    return kind, [Segment(text.decode("ascii"), APTextColor(colors[i])) for i, text in enumerate(texts)]


class TestSanitize(unittest.TestCase):
    """The game font renders a fixed glyph set; anything else has to be folded or dropped."""

    def test_renderable_text_passes_through(self):
        self.assertEqual(_sanitize("Kirby's Air Ride #1 (100%)"), "Kirby's Air Ride #1 (100%)")

    def test_accents_decompose_to_their_base_letter(self):
        # NFKD splits the accent off as a combining mark, which then drops as unrenderable.
        self.assertEqual(_sanitize("Café Ridé"), "Cafe Ride")

    def test_whitespace_runs_collapse_to_one_space(self):
        self.assertEqual(_sanitize("a \t\n  b"), "a b")

    def test_unrenderable_glyphs_are_dropped(self):
        self.assertEqual(_sanitize("hi ☃ there"), "hi there")


class TestSegmentCollector(unittest.TestCase):
    """Resolves JSON message parts into colored runs instead of an ANSI string."""

    def setUp(self) -> None:
        self.parser = SegmentCollector(ctx=None)

    def test_plain_text_is_one_default_segment(self):
        parts: list[JSONMessagePart] = []
        add_json_text(parts, "hello")
        self.assertEqual(self.parser.collect(parts), [Segment("hello", APTextColor.DEFAULT)])

    def test_the_first_recognised_code_in_a_color_list_wins(self):
        parts = [cast(JSONMessagePart, {"type": JSONTypes.color, "color": "bold;red", "text": "danger"})]
        self.assertEqual(self.parser.collect(parts), [Segment("danger", APTextColor.RED)])

    def test_an_unmapped_color_falls_back_to_default(self):
        parts = [cast(JSONMessagePart, {"type": JSONTypes.color, "color": "underline", "text": "plain"})]
        self.assertEqual(self.parser.collect(parts), [Segment("plain", APTextColor.DEFAULT)])

    def test_a_name_of_only_unrenderable_glyphs_becomes_a_placeholder(self):
        # Otherwise the name would vanish mid-sentence and the line would read as nonsense.
        parts: list[JSONMessagePart] = []
        add_json_text(parts, "こんにちは")
        self.assertEqual(self.parser.collect(parts), [Segment("?", APTextColor.DEFAULT)])

    def test_whitespace_only_text_is_not_a_placeholder(self):
        # The "?" stand-in is for text that had glyphs and lost them, not for a plain run of spaces.
        parts: list[JSONMessagePart] = []
        add_json_text(parts, "   ")
        self.assertEqual(self.parser.collect(parts), [Segment(" ", APTextColor.DEFAULT)])

    def test_collect_resets_between_calls(self):
        parts: list[JSONMessagePart] = []
        add_json_text(parts, "one")
        self.parser.collect(parts)
        self.assertEqual(self.parser.collect(parts), [Segment("one", APTextColor.DEFAULT)])


class TestCoalesce(unittest.TestCase):
    """The struct holds AP_TEXT_SEG_NUM colored runs, so adjacent same-color runs merge and anything
    past the limit is folded into the last one rather than dropped."""

    def test_adjacent_same_color_runs_merge(self):
        merged = _coalesce([Segment("a"), Segment("b"), Segment("c", APTextColor.RED)])
        self.assertEqual(merged, [Segment("ab"), Segment("c", APTextColor.RED)])

    def test_empty_runs_are_dropped(self):
        self.assertEqual(_coalesce([Segment(""), Segment("x", APTextColor.RED)]), [Segment("x", APTextColor.RED)])

    def test_overflow_folds_into_the_last_kept_run(self):
        colors = list(APTextColor)[: AP_TEXT_SEG_NUM + 3]
        merged = _coalesce([Segment(f"s{i}", color) for i, color in enumerate(colors)])
        self.assertEqual(len(merged), AP_TEXT_SEG_NUM)
        # The tail keeps the color of the run it was folded into, and loses no text.
        self.assertEqual(merged[-1].color, colors[AP_TEXT_SEG_NUM - 1])
        self.assertEqual("".join(s.text for s in merged), "".join(f"s{i}" for i in range(len(colors))))


class TestTruncate(unittest.TestCase):
    def test_short_enough_text_is_untouched(self):
        self.assertEqual(_truncate("abcdef", 6), "abcdef")
        self.assertEqual(_truncate("abcdef", 99), "abcdef")

    def test_an_ellipsis_replaces_the_last_two_characters(self):
        self.assertEqual(_truncate("abcdefgh", 5), "abc..")

    def test_trailing_space_before_the_ellipsis_is_dropped(self):
        self.assertEqual(_truncate("ab cdefgh", 5), "ab..")

    def test_a_budget_too_small_for_an_ellipsis_is_a_hard_cut(self):
        self.assertEqual(_truncate("abcdef", 2), "ab")
        self.assertEqual(_truncate("abcdef", 0), "")


class TestFit(unittest.TestCase):
    """The blob holds AP_TEXT_BLOB_LEN bytes including one NUL per segment, and the longest run always
    gives way first so a long location name shrinks before the words around it."""

    def budget(self, segments: list[Segment]) -> int:
        return AP_TEXT_BLOB_LEN - len(segments)

    def test_a_message_that_already_fits_is_untouched(self):
        segments = [Segment("short"), Segment("also short", APTextColor.RED)]
        self.assertEqual(_fit(segments), segments)

    def test_the_longest_run_is_trimmed_first(self):
        segments = [Segment("x" * 10), Segment("y" * AP_TEXT_BLOB_LEN, APTextColor.RED)]
        fitted = _fit(segments)
        self.assertEqual(fitted[0].text, "x" * 10, "the short run should be left alone")
        self.assertLessEqual(sum(len(s.text) for s in fitted), self.budget(fitted))

    def test_an_oversized_message_always_ends_up_within_budget(self):
        segments = [Segment("z" * 200, color) for color in list(APTextColor)[:AP_TEXT_SEG_NUM]]
        fitted = _fit(segments)
        self.assertEqual(len(fitted), len(segments), "fitting trims runs, it does not drop them")
        self.assertLessEqual(sum(len(s.text) for s in fitted), self.budget(fitted))


class TestPackMessage(unittest.TestCase):
    def test_nothing_to_show_packs_to_none(self):
        self.assertIsNone(pack_message(APTextKind.CHAT, []))
        self.assertIsNone(pack_message(APTextKind.CHAT, [Segment("")]))

    def test_layout_round_trips(self):
        segments = [Segment("Found "), Segment("Warp Star", APTextColor.CYAN)]
        payload = packed(APTextKind.ITEM, segments)
        self.assertEqual(len(payload), AP_TEXT_MESSAGE_SIZE)
        kind, decoded = unpack(payload)
        self.assertEqual(kind, APTextKind.ITEM)
        self.assertEqual(decoded, segments)

    def test_unused_color_slots_and_padding_are_zeroed(self):
        payload = packed(APTextKind.CHECK, [Segment("one", APTextColor.GREEN)])
        self.assertEqual(payload[1], 1)
        self.assertEqual(payload[2], int(APTextColor.GREEN))
        self.assertEqual(payload[3 : 2 + AP_TEXT_SEG_NUM], bytes(AP_TEXT_SEG_NUM - 1))
        self.assertEqual(payload[2 + AP_TEXT_SEG_NUM : 4 + AP_TEXT_SEG_NUM], b"\0\0")

    def test_an_oversized_message_still_fills_exactly_one_struct(self):
        segments = [Segment("q" * 500, color) for color in list(APTextColor)[: AP_TEXT_SEG_NUM + 4]]
        payload = packed(APTextKind.HINT, segments)
        self.assertEqual(len(payload), AP_TEXT_MESSAGE_SIZE)
        # Coalescing caps the run count, and the blob is NUL-terminated inside its own length.
        self.assertLessEqual(payload[1], AP_TEXT_SEG_NUM)
        self.assertEqual(payload[-1], 0)


class TestRelaySegments(unittest.TestCase):
    """Server broadcasts carry a team stamp and arrive uncolored; the relay strips one and supplies the
    other without overriding a color the server already chose."""

    def test_team_stamp_is_stripped(self):
        relayed = relay_segments([Segment("Tester (Team #1) goaled")], APTextColor.GREEN)
        self.assertEqual(relayed, [Segment("Tester goaled", APTextColor.GREEN)])

    def test_an_explicit_color_survives_the_relay(self):
        relayed = relay_segments([Segment("hi", APTextColor.RED)], APTextColor.YELLOW)
        self.assertEqual(relayed, [Segment("hi", APTextColor.RED)])


class TestHintPrefix(unittest.TestCase):
    def test_a_known_status_names_itself(self):
        parts: list[JSONMessagePart] = []
        add_hint_prefix(parts, hint_data(HintStatus.HINT_PRIORITY))
        self.assertEqual(parts[0]["text"], "Hint (priority): ")

    def test_an_unspecified_status_gets_the_bare_prefix(self):
        parts: list[JSONMessagePart] = []
        add_hint_prefix(parts, hint_data(HintStatus.HINT_UNSPECIFIED))
        self.assertEqual(parts[0]["text"], "Hint: ")

    def test_a_status_this_client_does_not_know_gets_the_bare_prefix(self):
        parts: list[JSONMessagePart] = []
        add_hint_prefix(parts, hint_data(99))
        self.assertEqual(parts[0]["text"], "Hint: ")

    def test_data_without_a_status_node_gets_the_bare_prefix(self):
        parts: list[JSONMessagePart] = []
        add_hint_prefix(parts, [cast(JSONMessagePart, {"type": "text", "text": "whatever"})])
        self.assertEqual(parts[0]["text"], "Hint: ")

    def test_labels_are_unparenthesised_and_skip_unspecified(self):
        self.assertNotIn(HintStatus.HINT_UNSPECIFIED, HINT_STATUS_LABELS)
        for status, label in HINT_STATUS_LABELS.items():
            with self.subTest(status=status):
                self.assertFalse(label.startswith("(") or label.endswith(")"))
