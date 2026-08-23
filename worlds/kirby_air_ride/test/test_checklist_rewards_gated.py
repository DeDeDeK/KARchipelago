"""
Tests for the checklist_rewards_gated option.

Off by default: the generator removes every non-progression checklist reward from the pool and the mod
unlocks them all at connect. The 6 progression Dragoon/Hydra part markers stay and float as ordinary
progression.

These tests pin:
  - on => non-progression rewards present (the opt-in behavior);
  - off => none in pool or precollected, reward_pool empty, only part markers left, and the pool still
    exactly fills placeable locations (the generic backfill absorbs the freed boxes);
  - off relaxes capacity (a tight config that OptionErrors with rewards on generates with them off);
  - a full distribute_items_restrictive places no non-progression reward and stays beatable.
"""

from typing import TYPE_CHECKING

from Options import OptionError, Toggle

from ..KARItems import CHECKLIST_REWARD_TYPES, ITEM_TABLE, ItemClassification
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

# Type-check time: mixin inherits KARTestBase so self.* resolves. Runtime: `object`, so concrete
# `class X(Mixin, KARTestBase)` keeps the correct MRO.
_MixinBase = KARTestBase if TYPE_CHECKING else object

NONPROG_REWARDS = {
    str(name)
    for name, data in ITEM_TABLE.items()
    if data.type in CHECKLIST_REWARD_TYPES and not (data.classification & ItemClassification.progression)
}
PROG_REWARD_MARKERS = {
    str(name)
    for name, data in ITEM_TABLE.items()
    if data.type in CHECKLIST_REWARD_TYPES and (data.classification & ItemClassification.progression)
}

_GATED_OFF = {"checklist_rewards_gated": Toggle.option_false}
_GATED_ON = {"checklist_rewards_gated": Toggle.option_true}


class TestRewardsGatedOnBaseline(KARTestBase):
    """Opt-in (on): non-progression rewards are in the pool."""

    options = {**ALL_MODES, **_GATED_ON}

    def test_rewards_present(self):
        self.assertTrue(self.world.reward_pool, "reward_pool should be non-empty with rewards gated on")
        self.assertTrue(
            NONPROG_REWARDS & self.world_item_names(),
            "expected non-progression rewards in the pool with rewards gated on",
        )


class _GatedOffInvariantMixin(_MixinBase):
    """Shared invariants for any mode combination with checklist_rewards_gated off."""

    def test_no_nonprog_rewards_anywhere(self):
        present = NONPROG_REWARDS & self.world_item_names()
        self.assertFalse(present, f"non-progression rewards leaked into the seed: {sorted(present)[:5]}")

    def test_reward_pool_empty(self):
        self.assertEqual(self.world.reward_pool, [], "reward_pool must be empty with rewards gated off")

    def test_only_progression_reward_markers_remain(self):
        all_reward_names = NONPROG_REWARDS | PROG_REWARD_MARKERS
        present_rewards = all_reward_names & self.world_item_names()
        self.assertTrue(
            present_rewards <= PROG_REWARD_MARKERS,
            f"only progression part markers may remain; found {sorted(present_rewards - PROG_REWARD_MARKERS)[:5]}",
        )

    def test_pool_fills_placeable_locations(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


class TestGatedOffAllModes(_GatedOffInvariantMixin, KARTestBase):
    options = {**ALL_MODES, **_GATED_OFF}

    def test_part_markers_retained(self):
        # City Trial is enabled here, so all 6 progression part markers stay in the pool untouched.
        self.assertEqual(PROG_REWARD_MARKERS & self.world_item_names(), PROG_REWARD_MARKERS)


class TestGatedOffCTOnly(_GatedOffInvariantMixin, KARTestBase):
    options = {**CT_ONLY, **_GATED_OFF}


class TestGatedOffAROnly(_GatedOffInvariantMixin, KARTestBase):
    options = {**AR_ONLY, **_GATED_OFF}


class TestGatedOffTROnly(_GatedOffInvariantMixin, KARTestBase):
    options = {**TR_ONLY, **_GATED_OFF}


class TestGatedOffFullFill(KARTestBase):
    """A full fill succeeds, places no non-progression reward anywhere, and stays beatable."""

    options = {**ALL_MODES, **_GATED_OFF}

    def test_no_nonprog_reward_placed(self):
        from Fill import distribute_items_restrictive

        distribute_items_restrictive(self.multiworld)
        placed = [
            loc.item.name
            for loc in self.multiworld.get_locations()
            if loc.item is not None and loc.item.player == self.player and loc.item.name in NONPROG_REWARDS
        ]
        self.assertEqual(placed, [], f"non-progression reward(s) placed despite gated off: {placed[:5]}")

    def test_beatable_after_collect_all(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


# CT-only config tuned so the 7 useful City Trial checklist rewards decide the needs-default budget:
# 75 base CT progression + 6 Patch Cap Increases + 5 checkbox fillers = 86 with rewards off (fits under
# City Trial's 90 default locations) vs 93 with the rewards on (overflows).
_REWARD_RELAX_OPTIONS = {
    **CT_ONLY,
    "city_trial_patch_cap_min": 12,
    "city_trial_patch_cap_max": 18,
}


class TestGatedOnTightPoolRaises(KARTestBase):
    """With rewards gated on, the tight fixture's useful rewards tip the needs-default budget over."""

    options = {**_REWARD_RELAX_OPTIONS, **_GATED_ON}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestGatedOffRelaxesCapacity(KARTestBase):
    """Removing the non-progression rewards relaxes the needs-default budget, so the same tight config
    that OptionErrors with rewards on generates with rewards off."""

    options = {**_REWARD_RELAX_OPTIONS, **_GATED_OFF}

    def test_generates(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))
        self.assertFalse(NONPROG_REWARDS & self.world_item_names())
