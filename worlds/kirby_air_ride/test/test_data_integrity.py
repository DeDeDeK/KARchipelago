"""
Data integrity tests for ITEM_TABLE, the per-mode location tables, and the derived lookup maps.

These are all static structures generation reads without re-validating, so a mistake in one shows up
as a silent behaviour change rather than an error: a duplicate code corrupts the wire contract with
the mod, a trap item in no `traps` category can never be selected, and a second box claiming an
existing native reward silently drops one of the two from the derived map. Each is cheap to pin here
and expensive to notice anywhere else.

The Archipelago band (361-480) is checked for shape in test_archipelago_checklist.py; what it needs
from this module is only that its codes do not collide with the three real modes'.
"""

import unittest

from BaseClasses import ItemClassification

from ..KARData import GameMode, location_code_to_mode_clear
from ..KARItems import (
    CHECKLIST_REWARD_CATEGORIES,
    CHECKLIST_REWARD_CATEGORY_TYPES,
    CHECKLIST_REWARD_TYPE_ITEMS,
    CHECKLIST_REWARD_TYPE_MODES,
    CHECKLIST_REWARD_TYPES,
    GATING_CATEGORIES,
    ITEM_TABLE,
    TRAP_CATEGORIES,
)
from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_TABLE,
    NATIVE_REWARD_TO_LOCATION,
    TOP_RIDE_LOCATION_TABLE,
)


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
    """Location codes partition into CT 1-120, AR 121-240, TR 241-360, and must round-trip to the expected
    GameMode."""

    _BANDS = [
        (CITY_TRIAL_LOCATION_TABLE, GameMode.CITYTRIAL, 1, 120),
        (AIR_RIDE_LOCATION_TABLE, GameMode.AIRRIDE, 121, 240),
        (TOP_RIDE_LOCATION_TABLE, GameMode.TOPRIDE, 241, 360),
    ]

    def test_codes_unique_globally(self):
        # Across all four tables, Archipelago included: LOCATION_TABLE merges them and the client
        # decodes a bare code back to (mode, clear_kind), so one code may mean only one box.
        seen: dict[int, str] = {}
        duplicates: list[tuple[int, str, str]] = []
        for table in (*(band[0] for band in self._BANDS), AP_CHECKLIST_LOCATION_TABLE):
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
    """Each per-mode location table has exactly 120 entries and codes form a contiguous range starting at
    the band's low end. A gap would indicate a removed location that left an unused code."""

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


class TestNativeRewardMap(unittest.TestCase):
    """NATIVE_REWARD_TO_LOCATION inverts the tables' `native_reward` field. A dict comprehension
    silently keeps the last writer, so two boxes claiming the same reward would drop one entry with no
    error anywhere."""

    def test_every_native_reward_is_claimed_by_one_box(self):
        claims: dict[str, list[str]] = {}
        for name, data in LOCATION_TABLE.items():
            if data.native_reward is not None:
                claims.setdefault(str(data.native_reward), []).append(str(name))
        contested = {reward: boxes for reward, boxes in claims.items() if len(boxes) > 1}
        self.assertEqual(contested, {}, f"native rewards claimed by more than one box: {contested}")
        self.assertEqual(len(NATIVE_REWARD_TO_LOCATION), len(claims), "the inverse map lost an entry")

    def test_map_round_trips_through_the_tables(self):
        self.assertTrue(NATIVE_REWARD_TO_LOCATION, "no box declares a native reward")
        for reward, location in NATIVE_REWARD_TO_LOCATION.items():
            with self.subTest(reward=reward):
                self.assertIn(reward, ITEM_TABLE, "a native reward must be a real item")
                self.assertIn(location, LOCATION_TABLE, "a native reward's box must be a real location")
                self.assertEqual(str(LOCATION_TABLE[location].native_reward), reward)


class TestChecklistRewardTypesPartitionRewards(unittest.TestCase):
    """CHECKLIST_REWARD_TYPE_ITEMS is what `checklist_rewards` resolves to and what the placed-types mask
    is built from. A reward listed under no type is dropped from the pool whatever the player picks, and
    its bit never reaches the mod, so the mod unlocks it at connect - the content is still reachable but
    can never be a check."""

    def in_scope_rewards(self) -> set[str]:
        owned_by_a_gate = {str(name) for cat in GATING_CATEGORIES for name in cat.overlapping_rewards}
        return {
            str(name)
            for name, data in ITEM_TABLE.items()
            if data.type in CHECKLIST_REWARD_TYPES
            and not (data.classification & ItemClassification.progression)
            and str(name) not in owned_by_a_gate
        }

    def test_every_in_scope_reward_is_under_exactly_one_type(self):
        rewards = self.in_scope_rewards()
        self.assertTrue(rewards, "ITEM_TABLE has no in-scope checklist rewards")

        membership: dict[str, list[str]] = {}
        for reward_type, names in CHECKLIST_REWARD_TYPE_ITEMS.items():
            for name in names:
                membership.setdefault(str(name), []).append(str(reward_type))

        unplaceable = sorted(rewards - set(membership))
        self.assertEqual(unplaceable, [], f"rewards under no reward type: {unplaceable}")
        duplicated = {name: types for name, types in membership.items() if len(types) > 1}
        self.assertEqual(duplicated, {}, f"rewards under more than one reward type: {duplicated}")

    def test_types_only_list_in_scope_rewards(self):
        rewards = self.in_scope_rewards()
        for reward_type, names in CHECKLIST_REWARD_TYPE_ITEMS.items():
            for name in names:
                with self.subTest(reward_type=reward_type, item=name):
                    self.assertIn(str(name), ITEM_TABLE, "reward type lists an item that does not exist")
                    self.assertIn(
                        str(name),
                        rewards,
                        "reward type lists a reward another option owns, which would double-govern it",
                    )

    def test_every_reward_item_type_maps_to_a_mode(self):
        # The mask packs one bit per (mode, reward type), so a reward whose item type has no mode has
        # nowhere to be recorded.
        self.assertEqual(set(CHECKLIST_REWARD_TYPE_MODES), set(CHECKLIST_REWARD_TYPES))
        modes = set(CHECKLIST_REWARD_TYPE_MODES.values())
        self.assertEqual(len(modes), len(CHECKLIST_REWARD_TYPE_MODES), "two item types share a mode")

    def test_every_category_maps_to_reward_types(self):
        self.assertEqual(set(CHECKLIST_REWARD_CATEGORY_TYPES), set(CHECKLIST_REWARD_CATEGORIES))
        self.assertEqual(
            {t for types in CHECKLIST_REWARD_CATEGORY_TYPES.values() for t in types},
            set(CHECKLIST_REWARD_TYPE_ITEMS),
            "a reward type no category claims can never be placed",
        )
        seen: dict[int, str] = {}
        for category, types in CHECKLIST_REWARD_CATEGORY_TYPES.items():
            self.assertTrue(types, f"category {category!r} maps to no reward type, so the mod would ungate it")
            for reward_type in types:
                self.assertNotIn(
                    int(reward_type),
                    seen,
                    f"reward type {reward_type!r} claimed by both {seen.get(int(reward_type))!r} and {category!r}",
                )
                seen[int(reward_type)] = category


class TestTrapCategoriesPartitionTraps(unittest.TestCase):
    """`traps` is the sole governor of which traps may be drawn, and its valid keys are TRAP_CATEGORIES.
    A trap-classified item listed in no category can therefore never be selected, however high
    trap_chance goes - and, since the pool just fills with something else, generation stays green."""

    def test_every_trap_item_is_in_exactly_one_category(self):
        trap_items = {str(name) for name, data in ITEM_TABLE.items() if data.classification & ItemClassification.trap}
        self.assertTrue(trap_items, "ITEM_TABLE has no trap-classified items")

        membership: dict[str, list[str]] = {}
        for category, names in TRAP_CATEGORIES.items():
            for name in names:
                membership.setdefault(str(name), []).append(category)

        unreachable = sorted(trap_items - set(membership))
        self.assertEqual(unreachable, [], f"trap items in no `traps` category, so never selectable: {unreachable}")
        duplicated = {name: cats for name, cats in membership.items() if len(cats) > 1}
        self.assertEqual(duplicated, {}, f"trap items in more than one category: {duplicated}")

    def test_categories_only_list_real_trap_items(self):
        for category, names in TRAP_CATEGORIES.items():
            for name in names:
                with self.subTest(category=category, item=name):
                    self.assertIn(str(name), ITEM_TABLE, "category lists an item that does not exist")
                    self.assertTrue(
                        ITEM_TABLE[name].classification & ItemClassification.trap,
                        "category lists a non-trap item, which `traps` would then wrongly govern",
                    )
