"""
Tests for KARWorld._random_filler, _random_trap, and get_filler_item_name.

These helpers run during create_items and as AP-framework callbacks. The fallback
path (filler_pool empty -> ITEM_TABLE) isn't exercised by happy-path generation, so we
drive it directly here. None of these helpers are mode-aware: cross-mode placement only
restricts progression items (via item_rules), never filler/traps.
"""

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARItems import ITEM_TABLE
from . import ALL_MODES, CT_ONLY, KARTestBase


class TestGetFillerItemNameCrossModeOff(KARTestBase):
    """get_filler_item_name returns a valid ITEM_TABLE filler (or a trap when traps are
    enabled). It is not mode-aware, so cross_mode_placement=false changes nothing here."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_false}

    def test_returns_a_valid_item_name(self):
        name = self.world.get_filler_item_name()
        self.assertIn(name, ITEM_TABLE)


class TestGetFillerItemNameCrossModeOn(KARTestBase):
    """Under cross_mode_placement=true the behavior is identical (same full filler_pool)."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_true}

    def test_returns_a_valid_item_name(self):
        name = self.world.get_filler_item_name()
        self.assertIn(name, ITEM_TABLE)


class TestRandomFillerFallbackWhenPoolEmpty(KARTestBase):
    """When the filler_pool is empty (e.g. an ItemLink path that bypasses _build_item_pools),
    _random_filler falls back to the broadest ITEM_TABLE filler set."""

    options = CT_ONLY

    def test_fallback_to_item_table_filler(self):
        self.world.filler_pool = set()
        name = self.world._random_filler()
        self.assertIn(name, ITEM_TABLE)
        self.assertEqual(
            ITEM_TABLE[name].classification,
            ItemClassification.filler,
            f"Fallback returned {name!r} which is not classified as pure filler",
        )


class TestRandomTrap(KARTestBase):
    """_random_trap returns None when no traps are enabled, otherwise a weighted trap name."""

    options = CT_ONLY

    def test_none_when_no_traps(self):
        self.world.trap_weights = {}
        self.assertIsNone(self.world._random_trap())

    def test_returns_a_weighted_trap(self):
        # Force a single known trap weight so the pick is deterministic and in ITEM_TABLE.
        name = next(iter(self.world.trap_weights), None) if self.world.trap_weights else None
        if name is None:
            # No traps in this config's pool; nothing to assert.
            return
        self.world.trap_weights = {name: 1}
        self.assertEqual(self.world._random_trap(), name)
