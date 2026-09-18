"""KARWorld._random_filler, _random_trap and get_filler_item_name. Each ends in
`self.random.choice(sorted(...))`, so these record the candidate list it built rather than sampling the
entry that came back - drawing N times would pass on the seed rather than on the code."""

from BaseClasses import ItemClassification

from ..KARItems import ITEM_TABLE, KARItemName
from . import ALL_MODES, CT_ONLY, KARTestBase, recording_random


class TestGetFillerItemName(KARTestBase):
    """With traps off, get_filler_item_name always returns pure filler - the framework calls it to top up
    a pool, so a progression or useful item coming back would quietly inflate it."""

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
                self.assertEqual(
                    ITEM_TABLE[name].classification,
                    ItemClassification.filler,
                    f"{name!r} is drawable as filler but is not pure filler",
                )


class TestGetFillerItemNameRollsTraps(KARTestBase):
    """trap_chance 100 makes `random() * 100 < 100` always true, so the trap branch is taken on every
    call. Pinned separately because the default trap_chance is 0, leaving the branch dead elsewhere."""

    options = {**ALL_MODES, "trap_chance": 100}

    def test_full_chance_draws_from_the_trap_pool(self):
        self.assertTrue(self.world.trap_pool, "trap_chance 100 with all modes on should populate trap_pool")
        with recording_random(self.world) as recorder:
            name = self.world.get_filler_item_name()
        self.assertEqual(recorder.offers, [sorted(self.world.trap_pool)])
        self.assertTrue(ITEM_TABLE[name].classification & ItemClassification.trap)


class TestRandomFiller(KARTestBase):
    options = CT_ONLY

    def test_fallback_offers_only_pure_filler_when_the_pool_was_never_built(self):
        # The pools go unbuilt on e.g. an ItemLink path, where the broadest ITEM_TABLE filler set stands in.
        self.world.item_pools_built = False
        self.world.filler_pool = set()
        with recording_random(self.world) as recorder:
            self.world._random_filler()
        self.assertEqual(len(recorder.offers), 1)
        self.assertTrue(recorder.offers[0], "the fallback offered nothing to draw from")
        for name in recorder.offers[0]:
            with self.subTest(item=name):
                self.assertEqual(ITEM_TABLE[name].classification, ItemClassification.filler)

    def test_a_built_pool_is_authoritative(self):
        # Nothing outside it may be offered, or a category the player disabled would reappear.
        self.assertTrue(self.world.item_pools_built)
        self.world.filler_pool = {KARItemName.HOT_DOG}
        with recording_random(self.world) as recorder:
            name = self.world._random_filler()
        self.assertEqual(recorder.offers, [[KARItemName.HOT_DOG]])
        self.assertEqual(name, KARItemName.HOT_DOG)


class TestRandomTrap(KARTestBase):
    """trap_chance is above 0 so trap_pool is populated - at 0 it stays empty and the active path is
    silently skipped."""

    options = {**CT_ONLY, "trap_chance": 50}

    def test_none_when_no_traps(self):
        self.world.trap_pool = set()
        self.assertIsNone(self.world._random_trap())

    def test_offers_exactly_the_active_trap_pool(self):
        self.assertTrue(self.world.trap_pool, "trap_chance > 0 with CT enabled should populate trap_pool")
        with recording_random(self.world) as recorder:
            name = self.world._random_trap()
        self.assertEqual(recorder.offers, [sorted(self.world.trap_pool)])
        self.assertIn(name, self.world.trap_pool)
