"""
Tests for KARWorld._random_filler, _random_trap, and get_filler_item_name.

The fallback path (filler_pool empty -> ITEM_TABLE) isn't exercised by happy-path generation, so we
drive it directly here. None of these helpers are mode-aware: every item floats freely across enabled
modes.
"""

from BaseClasses import ItemClassification

from ..KARItems import ITEM_TABLE, KARItemName
from . import ALL_MODES, CT_ONLY, KARTestBase


class TestGetFillerItemName(KARTestBase):
    """get_filler_item_name returns a valid ITEM_TABLE filler (or a trap when traps are enabled).
    It is not mode-aware: items float freely across enabled modes."""

    options = ALL_MODES

    def test_returns_a_valid_item_name(self):
        name = self.world.get_filler_item_name()
        self.assertIn(name, ITEM_TABLE)


class TestRandomFillerFallbackWhenPoolNeverBuilt(KARTestBase):
    """When the pools were never built (e.g. an ItemLink path), an empty filler_pool falls back to the
    broadest ITEM_TABLE filler set."""

    options = CT_ONLY

    def test_fallback_to_item_table_filler(self):
        self.world.item_pools_built = False
        self.world.filler_pool = set()
        name = self.world._random_filler()
        self.assertIn(name, ITEM_TABLE)
        self.assertEqual(
            ITEM_TABLE[name].classification,
            ItemClassification.filler,
            f"Fallback returned {name!r} which is not classified as pure filler",
        )


class TestRandomFillerNoResurrectWhenBuilt(KARTestBase):
    """Once the pools are built, _random_filler draws ONLY from filler_pool and never resurrects
    ITEM_TABLE filler. This keeps allowed_items honest: a category the player disabled must not reappear
    via the fallback."""

    options = CT_ONLY

    def test_draws_only_from_filler_pool(self):
        self.assertTrue(self.world.item_pools_built)
        self.world.filler_pool = {KARItemName.HOT_DOG}
        for _ in range(20):
            self.assertEqual(self.world._random_filler(), KARItemName.HOT_DOG)


class TestRandomTrap(KARTestBase):
    """_random_trap returns None when no traps are active, otherwise an active trap name.

    trap_chance is set above 0 so the trap_pool is actually populated (it stays empty when
    trap_chance == 0, which would silently skip the active-trap path)."""

    options = {**CT_ONLY, "trap_chance": 50}

    def test_none_when_no_traps(self):
        self.world.trap_pool = set()
        self.assertIsNone(self.world._random_trap())

    def test_returns_an_active_trap(self):
        # Assert the pool is populated rather than skipping, so this can never silently become a no-op.
        self.assertTrue(self.world.trap_pool, "trap_chance > 0 with CT enabled should populate trap_pool")
        # Force a single known trap so the pick is deterministic.
        name = next(iter(self.world.trap_pool))
        self.world.trap_pool = {name}
        self.assertEqual(self.world._random_trap(), name)
