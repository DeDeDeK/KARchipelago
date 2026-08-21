"""
Tests for KARWorld._random_filler, _random_trap, and get_filler_item_name.

The fallback path (filler_pool empty -> ITEM_TABLE) isn't exercised by happy-path generation, so it is
driven directly here. None of these helpers are mode-aware; every item floats across enabled modes.

Each helper ends in `self.random.choice(sorted(...))`, so what matters is the candidate list it built,
not the entry that came back. These tests record the candidate list (`recording_random`) and assert on
it exhaustively. Drawing N times instead would only sample it: a single non-filler item among fifteen
survives 50 draws about 3% of the time, which is a test that passes on the seed rather than the code.
"""

from BaseClasses import ItemClassification

from ..KARItems import ITEM_TABLE, KARItemName
from . import ALL_MODES, CT_ONLY, KARTestBase, recording_random


class TestGetFillerItemName(KARTestBase):
    """With traps off, get_filler_item_name always returns pure filler - the framework calls it to top
    up a pool, so a progression or useful item coming back here would quietly inflate the pool. It is
    not mode-aware: items float freely across enabled modes."""

    options = {**ALL_MODES, "trap_chance": 0}

    def test_draws_from_exactly_the_filler_pool(self):
        with recording_random(self.world) as recorder:
            name = self.world.get_filler_item_name()
        self.assertEqual(recorder.offers, [sorted(self.world.filler_pool)])
        self.assertIn(name, self.world.filler_pool)

    def test_every_drawable_name_is_pure_filler(self):
        self.assertTrue(self.world.filler_pool, "ALL_MODES should leave something to draw from")
        for name in sorted(self.world.filler_pool):
            with self.subTest(item=name):
                self.assertIn(name, ITEM_TABLE)
                self.assertEqual(
                    ITEM_TABLE[name].classification,
                    ItemClassification.filler,
                    f"{name!r} is drawable as filler but is not pure filler",
                )


class TestGetFillerItemNameRollsTraps(KARTestBase):
    """trap_chance 100 makes every roll a trap, which is the branch that turns filler slots into traps.
    Pinned separately because the default trap_chance is 0, so the branch is dead in every other test."""

    options = {**ALL_MODES, "trap_chance": 100}

    def test_full_chance_draws_from_the_trap_pool_not_the_filler_pool(self):
        self.assertTrue(self.world.trap_pool, "trap_chance 100 with all modes on should populate trap_pool")
        with recording_random(self.world) as recorder:
            name = self.world.get_filler_item_name()
        # `random() * 100 < 100` can never be false, so the trap branch is taken on every call and the
        # only candidate list offered is the trap pool.
        self.assertEqual(recorder.offers, [sorted(self.world.trap_pool)])
        self.assertNotIn(name, self.world.filler_pool)
        self.assertTrue(ITEM_TABLE[name].classification & ItemClassification.trap)


class TestRandomFillerFallbackWhenPoolNeverBuilt(KARTestBase):
    """When the pools were never built (e.g. an ItemLink path), an empty filler_pool falls back to the
    broadest ITEM_TABLE filler set."""

    options = CT_ONLY

    def test_fallback_offers_only_pure_filler(self):
        self.world.item_pools_built = False
        self.world.filler_pool = set()
        with recording_random(self.world) as recorder:
            self.world._random_filler()
        self.assertEqual(len(recorder.offers), 1)
        offered = recorder.offers[0]
        self.assertTrue(offered, "the fallback offered nothing to draw from")
        for name in offered:
            with self.subTest(item=name):
                self.assertEqual(
                    ITEM_TABLE[name].classification,
                    ItemClassification.filler,
                    f"fallback offers {name!r}, which is not classified as pure filler",
                )


class TestRandomFillerNoResurrectWhenBuilt(KARTestBase):
    """Once the pools are built, _random_filler draws ONLY from filler_pool and never resurrects
    ITEM_TABLE filler. This keeps allowed_items honest: a category the player disabled must not reappear
    via the fallback."""

    options = CT_ONLY

    def test_draws_only_from_filler_pool(self):
        self.assertTrue(self.world.item_pools_built)
        self.world.filler_pool = {KARItemName.HOT_DOG}
        with recording_random(self.world) as recorder:
            name = self.world._random_filler()
        self.assertEqual(
            recorder.offers,
            [[KARItemName.HOT_DOG]],
            "a built pool is authoritative - nothing outside it may be offered",
        )
        self.assertEqual(name, KARItemName.HOT_DOG)


class TestRandomTrap(KARTestBase):
    """_random_trap returns None when no traps are active, otherwise an active trap name. trap_chance is
    set above 0 so trap_pool is populated - at 0 it stays empty and silently skips the active path."""

    options = {**CT_ONLY, "trap_chance": 50}

    def test_none_when_no_traps(self):
        self.world.trap_pool = set()
        self.assertIsNone(self.world._random_trap())

    def test_offers_exactly_the_active_trap_pool(self):
        # Assert the pool is populated rather than skipping, so this can never silently become a no-op.
        self.assertTrue(self.world.trap_pool, "trap_chance > 0 with CT enabled should populate trap_pool")
        with recording_random(self.world) as recorder:
            name = self.world._random_trap()
        self.assertEqual(recorder.offers, [sorted(self.world.trap_pool)])
        self.assertIn(name, self.world.trap_pool)
