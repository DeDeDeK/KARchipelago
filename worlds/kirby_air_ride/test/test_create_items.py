"""create_item must hand back a KARItem matching ITEM_TABLE for every entry, carrying the table's
classification verbatim except for the two options-dependent cases _item_classification owns."""

import unittest

from BaseClasses import ItemClassification

from .. import KARWorld
from ..KARItems import (
    GATING_CATEGORIES,
    ITEM_TABLE,
    MAX_STATS_GOAL_KEYS,
    KARItem,
    KARItemName,
    KARItemType,
    items_by_type,
)
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from ..KARRules import _EVENT_LOCATION_RULES
from . import CT_ONLY, KARTestBase, names

# Every gated unlock type plus stadium unlocks, which gate separately.
_UNLOCK_TYPES: frozenset[KARItemType] = frozenset(
    {cat.item_type for cat in GATING_CATEGORIES} | {KARItemType.CT_STADIUM_UNLOCK}
)

# City Trial event unlocks a location rule keys. The rest gate nothing and are deliberately not progression.
_KEYED_EVENT_UNLOCKS: frozenset[str] = frozenset(_EVENT_LOCATION_RULES.values())

# Reaches the Max Stats classification branch: the goal plus the two gates its rule needs. Air Ride and
# Top Ride come along because City Trial alone has too few default locations for its gated pool plus a
# patch cap range.
_MAX_STATS: dict = {
    "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
    "city_trial_patches_gated": True,
    "city_trial_items_gated": True,
    "city_trial_patch_cap_min": 14,
    "city_trial_patch_cap_max": 18,
}


class TestItemTableClassifications(unittest.TestCase):
    """Static ITEM_TABLE invariants - no generation needed, so they run against the table directly."""

    def test_every_keyed_unlock_item_is_progression(self):
        """An UNLOCK item gates location access; misclassifying one lets fill place it at a
        non-progression slot and soft-lock the player."""
        for name, data in ITEM_TABLE.items():
            if data.type not in _UNLOCK_TYPES:
                continue
            if data.type == KARItemType.CT_EVENT_UNLOCK and name not in _KEYED_EVENT_UNLOCKS:
                continue
            with self.subTest(item=name, type=data.type):
                self.assertTrue(data.classification & ItemClassification.progression, f"{name} must be progression")

    def test_event_unlock_split_tracks_the_rule_table(self):
        """The event unlocks' progression/useful split is exactly "does a location rule name it", so
        adding a rule without promoting its unlock fails here rather than producing an unreachable box."""
        progression = {
            str(name)
            for name in items_by_type[KARItemType.CT_EVENT_UNLOCK]
            if ITEM_TABLE[name].classification & ItemClassification.progression
        }
        self.assertEqual(progression, names(_KEYED_EVENT_UNLOCKS))
        for name in sorted(items_by_type[KARItemType.CT_EVENT_UNLOCK] - _KEYED_EVENT_UNLOCKS):
            with self.subTest(item=name):
                self.assertEqual(ITEM_TABLE[name].classification, ItemClassification.useful)

    def test_every_coded_item_is_registered(self):
        """Event items carry code None and have no network id; everything else must be registered."""
        for name, data in ITEM_TABLE.items():
            if data.code is None:
                continue
            with self.subTest(item=name):
                self.assertEqual(KARWorld.item_name_to_id.get(str(name)), data.code)


class TestCreateItem(KARTestBase):
    options = CT_ONLY

    def test_create_item_for_each_table_entry(self):
        for name, data in ITEM_TABLE.items():
            with self.subTest(item=name):
                item = self.world.create_item(name)
                self.assertIsInstance(item, KARItem)
                self.assertEqual(item.name, str(name))
                self.assertEqual(item.code, data.code)
                self.assertEqual(item.player, self.player)
                self.assertEqual(item.game, "Kirby Air Ride")
                self.assertEqual(item.type, data.type)

    def test_unknown_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.world.create_item("Not An Item")

    def test_only_the_documented_cases_differ_from_the_table(self):
        """The override is narrow by design: outside Max Stats it moves Patch Cap Increase and nothing
        else, so an accidental promotion shows up here rather than silently in a seed."""
        moved = {
            str(name)
            for name, data in ITEM_TABLE.items()
            if self.world._item_classification(name, data) != data.classification
        }
        self.assertEqual(moved, {str(KARItemName.PATCH_CAP_INCREASE)})

    def test_patch_cap_is_useful_but_still_counted(self):
        """Only the Max Stats goal reads Patch Cap Increase, so elsewhere it is useful - but it keeps its
        counted quantity rather than joining the randomly-drawn useful_pool."""
        self.assertEqual(
            self.world.create_item(KARItemName.PATCH_CAP_INCREASE).classification, ItemClassification.useful
        )
        self.assertNotIn(KARItemName.PATCH_CAP_INCREASE, self.world.useful_pool)

    def test_unkeyed_event_unlocks_ship_exactly_once(self):
        """Useful, but a one-time unlock: it must not fall into the randomly-drawn useful_pool."""
        for name in sorted(items_by_type[KARItemType.CT_EVENT_UNLOCK] - _KEYED_EVENT_UNLOCKS):
            with self.subTest(item=name):
                self.assertNotIn(name, self.world.useful_pool)
                self.assertEqual(self.world.counted_useful_pool.count(name), 1)


class TestMaxStatsGoalKeyClassifications(KARTestBase):
    """Under Max Stats the patch type unlocks and All Up are the goal's own keys, so they must not carry
    `deprioritized` - that flag tells priority fill to pass an item over."""

    options = _MAX_STATS

    def test_patch_cap_is_progression_but_stays_deprioritized(self):
        # Up to 29 copies is the "plentiful" case deprioritized exists for, so it keeps the flag.
        item = self.world.create_item(KARItemName.PATCH_CAP_INCREASE)
        self.assertTrue(item.classification & ItemClassification.progression)
        self.assertTrue(item.classification & ItemClassification.deprioritized)

    def test_goal_keys_are_not_deprioritized(self):
        for name in sorted(MAX_STATS_GOAL_KEYS):
            with self.subTest(item=name):
                item = self.world.create_item(name)
                self.assertTrue(item.classification & ItemClassification.progression)
                self.assertFalse(item.classification & ItemClassification.deprioritized)

    def test_other_item_unlocks_keep_deprioritized(self):
        item = self.world.create_item(KARItemName.UNLOCK_ITEM_APPLE)
        self.assertTrue(item.classification & ItemClassification.deprioritized)
