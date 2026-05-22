"""
Tests for KARWorld._pick_filler, get_filler_item_name, and _sample_useful.

These helpers run during create_items and as AP-framework callbacks. The fallback
paths (filler_pool empty -> ITEM_TABLE) and the cross-mode-off restrictions aren't
exercised by happy-path generation, so we drive them directly here.
"""

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARData import GameMode
from ..KARItems import ITEM_TABLE, KARItemName
from . import ALL_MODES, CT_ONLY, KARTestBase


class TestGetFillerItemNameCrossModeOff(KARTestBase):
    """get_filler_item_name (the AP framework hook) calls _pick_filler(None).
    Under cross_mode_placement=false, only mode-neutral filler is eligible, since the
    framework doesn't tell us the target location. Today no ITEM_TABLE filler is mode-
    neutral, so we exercise the ITEM_TABLE-classification fallback at the same time."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_false}

    def test_returns_a_valid_filler_name(self):
        name = self.world.get_filler_item_name()
        self.assertIn(name, ITEM_TABLE)
        # Either neutral pool item OR the ITEM_TABLE fallback (filler-classification) item.
        data = ITEM_TABLE[name]
        is_neutral_filler = data.classification == ItemClassification.filler and not data.source_modes
        is_pure_filler = data.classification == ItemClassification.filler
        self.assertTrue(
            is_neutral_filler or is_pure_filler,
            f"get_filler_item_name returned {name!r} which is neither neutral-filler nor ITEM_TABLE-filler",
        )


class TestGetFillerItemNameCrossModeOn(KARTestBase):
    """Under cross_mode_placement=true, get_filler_item_name has the full filler_pool
    to choose from (no neutral-only restriction)."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_true}

    def test_returns_a_valid_filler_name(self):
        name = self.world.get_filler_item_name()
        self.assertIn(name, ITEM_TABLE)


class TestPickFillerFallbackWhenPoolEmpty(KARTestBase):
    """When the filler_pool is empty (e.g. an ItemLink path that bypasses _build_item_pools),
    _pick_filler falls back to the broadest ITEM_TABLE filler set. Simulate by emptying
    filler_pool and calling _pick_filler directly."""

    options = CT_ONLY

    def test_fallback_to_item_table_filler(self):
        # Drop the filler_pool so the eligibility set is empty and the fallback path runs.
        # Also drop trap_weights so _pick_filler doesn't enter the trap branch.
        self.world.filler_pool = set()
        self.world.trap_weights = {}
        name = self.world._pick_filler(target_mode=None)
        self.assertIn(name, ITEM_TABLE)
        self.assertEqual(
            ITEM_TABLE[name].classification,
            ItemClassification.filler,
            f"Fallback returned {name!r} which is not classified as pure filler",
        )

    def test_fallback_with_target_mode(self):
        self.world.filler_pool = set()
        self.world.trap_weights = {}
        # target_mode=CITYTRIAL — fallback still returns ITEM_TABLE filler regardless.
        name = self.world._pick_filler(target_mode=GameMode.CITYTRIAL)
        self.assertEqual(ITEM_TABLE[name].classification, ItemClassification.filler)


class TestSampleUsefulReturnsNoneWhenEmpty(KARTestBase):
    """Caller (_sample_useful) returns None when no eligible items remain so the caller
    can fall back to filler. Pin that contract."""

    options = CT_ONLY

    def test_none_when_useful_pool_empty(self):
        self.world.useful_pool = set()
        self.assertIsNone(self.world._sample_useful(mode_capacity=None))

    def test_none_when_no_mode_has_capacity(self):
        # All caps zeroed and the useful pool has no mode-neutral items — nothing eligible.
        # SPAWN_RATE_UP is _CT_TR so it would still be eligible if CT/TR have capacity.
        # With all caps zeroed and no neutral items, sample must return None.
        # Keep a couple of mode-tagged items so the assertion is meaningful.
        self.world.useful_pool = {KARItemName.AR_REWARD_FILLER_BOX_1}
        zeroed = dict.fromkeys(GameMode, 0)
        self.assertIsNone(self.world._sample_useful(mode_capacity=zeroed))
