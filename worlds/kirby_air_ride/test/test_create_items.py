"""
Item creation and classification tests.

For every entry in ITEM_TABLE, KARWorld.create_item must produce a KARItem with:
- the correct name, code, and player slot
- a classification matching the ITEM_TABLE entry verbatim (create_item no longer overrides
  any classification — every gated category, stadiums included, is handled by exclusion)

Also pins the invariant that every UNLOCK-type item is progression: players cannot
soft-lock through misclassified UNLOCK items getting placed at non-progression slots.
"""

from ..KARItems import GATING_CATEGORIES, ITEM_TABLE, KARItem, KARItemType
from . import CT_ONLY, KARTestBase

# Every gated unlock type plus stadium unlocks (which gate separately).
_UNLOCK_TYPES: frozenset[KARItemType] = frozenset(
    {cat.item_type for cat in GATING_CATEGORIES} | {KARItemType.CT_STADIUM_UNLOCK}
)


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

    def test_classification_matches_table(self):
        """create_item preserves the ITEM_TABLE classification for every item verbatim — there is no
        longer any create-time promotion (stadiums and every other gated category are handled purely by
        pool exclusion, so the six stadium rewards keep their table classification)."""
        for name, data in ITEM_TABLE.items():
            with self.subTest(item=name):
                item = self.world.create_item(name)
                self.assertEqual(item.classification, data.classification)


class TestAllUnlocksAreProgression(KARTestBase):
    """Per the project convention, every UNLOCK-type item in ITEM_TABLE must be classified
    as progression. UNLOCK items gate access to locations; misclassification as filler/useful
    would risk placing them at non-progression slots and soft-locking the player."""

    options = CT_ONLY

    def test_every_unlock_item_is_progression(self):
        from BaseClasses import ItemClassification

        for name, data in ITEM_TABLE.items():
            if data.type not in _UNLOCK_TYPES:
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
