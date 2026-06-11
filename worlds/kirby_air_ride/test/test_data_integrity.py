"""
Data integrity tests for ITEM_TABLE and the per-mode location tables.

These are static-data invariants the rest of the code depends on:
- Item codes are unique (or None).
- Location codes are unique, contiguous within their mode partition, and round-trip
  through location_code_to_mode to the expected GameMode.

A duplicate code or a partition violation would be caught at generation only as a weird
silent crash; pinning these directly gives a clear error message.
"""

import unittest

from ..KARData import GameMode, location_code_to_mode_clear
from ..KARItems import ITEM_TABLE
from ..KARLocations import AIR_RIDE_LOCATION_TABLE, CITY_TRIAL_LOCATION_TABLE, TOP_RIDE_LOCATION_TABLE


def location_code_to_mode(code: int | None) -> GameMode | None:
    """Return only the GameMode for a location code, or None if out of range / None."""
    result = location_code_to_mode_clear(code)
    return result[0] if result is not None else None


class TestItemCodeUniqueness(unittest.TestCase):
    """No two distinct items in ITEM_TABLE share a code (None excluded, events)."""

    def test_codes_unique(self):
        codes: dict[int, str] = {}
        duplicates: list[tuple[int, str, str]] = []
        for name, data in ITEM_TABLE.items():
            if data.code is None:
                continue
            if data.code in codes:
                duplicates.append((data.code, codes[data.code], name))
            else:
                codes[data.code] = name
        self.assertEqual(duplicates, [], f"Duplicate item codes: {duplicates}")


class TestLocationCodePartitioning(unittest.TestCase):
    """Per CLAUDE.md: CT 1-120, AR 121-240, TR 241-360. Codes must round-trip through
    location_code_to_mode to the expected GameMode."""

    _BANDS = [
        (CITY_TRIAL_LOCATION_TABLE, GameMode.CITYTRIAL, 1, 120),
        (AIR_RIDE_LOCATION_TABLE, GameMode.AIRRIDE, 121, 240),
        (TOP_RIDE_LOCATION_TABLE, GameMode.TOPRIDE, 241, 360),
    ]

    def test_codes_unique_globally(self):
        seen: dict[int, str] = {}
        duplicates: list[tuple[int, str, str]] = []
        for table, _, _, _ in self._BANDS:
            for name, data in table.items():
                if data.code is None:
                    continue
                if data.code in seen:
                    duplicates.append((data.code, seen[data.code], name))
                else:
                    seen[data.code] = name
        self.assertEqual(duplicates, [], f"Duplicate location codes: {duplicates}")

    def test_codes_in_band_for_each_mode(self):
        for table, mode, lo, hi in self._BANDS:
            for name, data in table.items():
                with self.subTest(mode=mode.name, location=name):
                    if data.code is None:
                        continue
                    self.assertGreaterEqual(
                        data.code,
                        lo,
                        f"{name} code {data.code} below {mode.name} band [{lo},{hi}]",
                    )
                    self.assertLessEqual(
                        data.code,
                        hi,
                        f"{name} code {data.code} above {mode.name} band [{lo},{hi}]",
                    )

    def test_location_code_to_mode_roundtrip(self):
        for table, mode, _, _ in self._BANDS:
            for name, data in table.items():
                with self.subTest(mode=mode.name, location=name):
                    if data.code is None:
                        continue
                    self.assertEqual(
                        location_code_to_mode(data.code),
                        mode,
                        f"{name} code {data.code} round-tripped to {location_code_to_mode(data.code)}, expected {mode}",
                    )


class TestLocationCodeContiguity(unittest.TestCase):
    """Each per-mode location table has exactly 120 entries and codes form a contiguous
    range starting at the band's low end. CLAUDE.md describes them as 'sequential
    indices'; a gap would indicate a removed location that left an unused code."""

    _BANDS = [
        (CITY_TRIAL_LOCATION_TABLE, 1, 120),
        (AIR_RIDE_LOCATION_TABLE, 121, 240),
        (TOP_RIDE_LOCATION_TABLE, 241, 360),
    ]

    def test_each_mode_has_120_entries(self):
        for table, _, _ in self._BANDS:
            self.assertEqual(len(table), 120, f"Expected 120 entries, got {len(table)}")

    def test_codes_form_contiguous_range(self):
        for table, lo, hi in self._BANDS:
            codes = sorted(d.code for d in table.values() if d.code is not None)
            self.assertEqual(codes, list(range(lo, hi + 1)), f"Codes not contiguous in [{lo},{hi}]: got {codes}")
