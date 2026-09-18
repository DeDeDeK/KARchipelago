"""
Item creation and classification tests.

create_item must produce, for every ITEM_TABLE entry, a KARItem with the correct name, code, player
slot, and the classification this slot assigns it. That is the table's verbatim, except for the two
options-dependent cases KARWorld._item_classification owns - gated categories are still handled purely
by exclusion, not by promotion.

Also pins that every UNLOCK-type item logic keys is progression: a misclassified one could land at a
non-progression slot and soft-lock the player. The exception is the ten City Trial event unlocks no
location rule names, which are useful; TestEventUnlockSplitTracksLogic holds that split to the rules.
"""

from BaseClasses import ItemClassification

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
from . import CT_ONLY, KARTestBase

# Every gated unlock type plus stadium unlocks (which gate separately).
_UNLOCK_TYPES: frozenset[KARItemType] = frozenset(
    {cat.item_type for cat in GATING_CATEGORIES} | {KARItemType.CT_STADIUM_UNLOCK}
)

# City Trial event unlocks a location rule keys. The rest gate nothing and are deliberately not progression.
_KEYED_EVENT_UNLOCKS: frozenset[str] = frozenset(_EVENT_LOCATION_RULES.values())

# Reaches the Max Stats goal's classification branch: the goal plus the two gates its rule needs. Air
# Ride and Top Ride come along because City Trial alone has too few default locations to hold its own
# gated pool plus a patch cap range.
_MAX_STATS: dict = {
    "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
    "city_trial_patches_gated": True,
    "city_trial_items_gated": True,
    "city_trial_patch_cap_min": 14,
    "city_trial_patch_cap_max": 18,
}


class TestCreateEveryItem(KARTestBase):
    """Every ITEM_TABLE entry can be instantiated via create_item without raising,
    and the resulting KARItem matches the table's name, code, and player."""

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

    def test_classification_matches_slot(self):
        """create_item hands back the slot's classification, which is the table's for everything but
        the options-dependent cases. Gated categories (stadiums included) are still never promoted."""
        for name, data in ITEM_TABLE.items():
            with self.subTest(item=name):
                item = self.world.create_item(name)
                self.assertEqual(item.classification, self.world._item_classification(name, data))

    def test_only_the_documented_cases_differ_from_the_table(self):
        """The override is narrow by design: outside Max Stats it moves Patch Cap Increase and nothing
        else, so an accidental promotion elsewhere shows up here rather than silently in a seed."""
        moved = {
            str(name)
            for name, data in ITEM_TABLE.items()
            if self.world._item_classification(name, data) != data.classification
        }
        self.assertEqual(moved, {str(KARItemName.PATCH_CAP_INCREASE)})


class TestPatchCapIsProgressionOnlyForMaxStats(KARTestBase):
    """Patch Cap Increase is read by exactly one rule, the Max Stats goal's. Under every other goal it
    gates nothing, so shipping up to 29 copies as progression would be dead weight on the ledger."""

    options = CT_ONLY

    def test_useful_without_the_max_stats_goal(self):
        item = self.world.create_item(KARItemName.PATCH_CAP_INCREASE)
        self.assertEqual(item.classification, ItemClassification.useful)

    def test_counted_copies_still_guaranteed(self):
        """Useful, but not a random draw: it keeps its counted quantity in counted_useful_pool, so the
        player still receives exactly (cap max - cap min) of them."""
        self.assertNotIn(KARItemName.PATCH_CAP_INCREASE, self.world.useful_pool)


class TestMaxStatsGoalKeyClassifications(KARTestBase):
    """Under Max Stats the patch type unlocks and All Up are the goal's own keys, so they must not carry
    `deprioritized` - that flag tells priority fill to pass an item over."""

    options = _MAX_STATS

    def test_patch_cap_is_progression(self):
        item = self.world.create_item(KARItemName.PATCH_CAP_INCREASE)
        self.assertTrue(item.classification & ItemClassification.progression)
        # Up to 29 copies is the "plentiful" case deprioritized exists for, so it keeps the flag.
        self.assertTrue(item.classification & ItemClassification.deprioritized)

    def test_goal_keys_are_not_deprioritized(self):
        for name in sorted(MAX_STATS_GOAL_KEYS):
            with self.subTest(item=name):
                item = self.world.create_item(name)
                self.assertTrue(item.classification & ItemClassification.progression)
                self.assertFalse(
                    item.classification & ItemClassification.deprioritized,
                    f"{name} keys this seed's goal and must stay eligible for priority locations",
                )

    def test_other_item_unlocks_keep_deprioritized(self):
        """The rest of the City Trial item unlocks are genuinely insignificant and keep the flag."""
        item = self.world.create_item(KARItemName.UNLOCK_ITEM_APPLE)
        self.assertTrue(item.classification & ItemClassification.deprioritized)


class TestEventUnlockSplitTracksLogic(KARTestBase):
    """The event unlocks' progression/useful split is exactly "does a location rule name it". Pinned to
    _EVENT_LOCATION_RULES so adding a rule for, say, the UFO event without promoting its unlock fails
    here instead of producing an unreachable check."""

    options = CT_ONLY

    def test_split_matches_event_location_rules(self):
        progression = {
            str(name)
            for name in items_by_type[KARItemType.CT_EVENT_UNLOCK]
            if ITEM_TABLE[name].classification & ItemClassification.progression
        }
        self.assertEqual(progression, {str(name) for name in _KEYED_EVENT_UNLOCKS})

    def test_unkeyed_event_unlocks_are_useful(self):
        for name in sorted(items_by_type[KARItemType.CT_EVENT_UNLOCK]):
            if name in _KEYED_EVENT_UNLOCKS:
                continue
            with self.subTest(item=name):
                self.assertEqual(ITEM_TABLE[name].classification, ItemClassification.useful)

    def test_unkeyed_event_unlocks_still_ship_exactly_once(self):
        """Useful, but a one-time unlock: it must not fall into the randomly-drawn useful_pool."""
        counts = {
            name: self.world.counted_useful_pool.count(name) for name in items_by_type[KARItemType.CT_EVENT_UNLOCK]
        }
        for name in sorted(items_by_type[KARItemType.CT_EVENT_UNLOCK]):
            if name in _KEYED_EVENT_UNLOCKS:
                continue
            with self.subTest(item=name):
                self.assertNotIn(name, self.world.useful_pool)
                self.assertEqual(counts[name], 1)


class TestAllUnlocksAreProgression(KARTestBase):
    """Every UNLOCK-type item that logic keys must be progression. UNLOCK items gate location access;
    classifying one as filler/useful risks placing it at a non-progression slot and soft-locking the
    player. The ten unkeyed City Trial event unlocks are the sole exception, covered above."""

    options = CT_ONLY

    def test_every_keyed_unlock_item_is_progression(self):
        for name, data in ITEM_TABLE.items():
            if data.type not in _UNLOCK_TYPES:
                continue
            if data.type == KARItemType.CT_EVENT_UNLOCK and name not in _KEYED_EVENT_UNLOCKS:
                continue
            with self.subTest(item=name, type=data.type):
                self.assertTrue(
                    data.classification & ItemClassification.progression,
                    f"{name} ({data.type}) must be progression: UNLOCK items gate access "
                    "and cannot be classified as useful/filler",
                )


class TestCreateItemUnknownNameRaises(KARTestBase):
    """create_item with a bogus name should raise KeyError rather than silently
    constructing a broken item."""

    options = CT_ONLY

    def test_unknown_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.world.create_item("Not An Item")


class TestEveryItemRegisteredInItemNameToId(KARTestBase):
    """Every ITEM_TABLE entry with a non-None code is registered in item_name_to_id.
    Event items (code=None) are intentionally excluded; they have no network code."""

    options = CT_ONLY

    def test_every_coded_item_registered(self):
        registered = self.world.item_name_to_id
        for name, data in ITEM_TABLE.items():
            if data.code is None:
                continue
            with self.subTest(item=name):
                self.assertIn(str(name), registered, f"{name} has code {data.code} but is missing from item_name_to_id")
                self.assertEqual(
                    registered[str(name)],
                    data.code,
                    f"{name} code mismatch: table={data.code}, registered={registered[str(name)]}",
                )
