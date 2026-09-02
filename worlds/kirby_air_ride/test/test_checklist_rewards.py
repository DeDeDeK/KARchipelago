"""
Tests for the checklist_rewards option.

Empty by default: the generator removes every non-progression checklist reward from the pool and the mod
unlocks them all at connect. The 6 progression Dragoon/Hydra part markers stay and float as ordinary
progression.

These tests pin:
  - every category selected => non-progression rewards present (the opt-in behavior);
  - none selected => none in pool or precollected, reward_pool empty, only part markers left, and the
    pool still exactly fills placeable locations (the generic backfill absorbs the freed boxes);
  - a partial selection places exactly the chosen categories and drops the rest;
  - the shipped bitmask names exactly the (mode, reward type) pairs that reached the pool, so a mode the
    seed disabled ships no bits and the mod unlocks its rewards outright;
  - dropping categories relaxes capacity (a tight config that OptionErrors with every category on
    generates with them off);
  - a full distribute_items_restrictive places no non-progression reward and stays beatable.
"""

from typing import TYPE_CHECKING

from Options import OptionError

from ..KARData import GameMode, RewardType, checklist_reward_placed_bit
from ..KARItems import (
    CHECKLIST_REWARD_CATEGORIES,
    CHECKLIST_REWARD_ITEM_TYPES,
    CHECKLIST_REWARD_TYPE_MODES,
    CHECKLIST_REWARD_TYPES,
    ITEM_TABLE,
    ItemClassification,
)
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

_NONE_SELECTED = {"checklist_rewards": []}
_ALL_SELECTED = {"checklist_rewards": sorted(CHECKLIST_REWARD_CATEGORIES)}


def mode_bits(mask: int, mode: GameMode) -> set[RewardType]:
    """The reward types `mask` marks placed for one checklist mode."""
    return {t for t in RewardType if mask >> checklist_reward_placed_bit(mode, t) & 1}


class _MaskMatchesPoolMixin(_MixinBase):
    """The shipped mask must name exactly the (mode, reward type) pairs that reached the pool. A pair the
    mask claims but the pool never got is content no item can unlock and the mod will not grant."""

    def test_mask_matches_pool(self):
        mask = self.world.fill_slot_data()["checklist_rewards"]
        present = self.world_item_names()
        expected = {
            checklist_reward_placed_bit(CHECKLIST_REWARD_TYPE_MODES[ITEM_TABLE[name].type], reward_type)
            for name, reward_type in CHECKLIST_REWARD_ITEM_TYPES.items()
            if str(name) in present
        }
        actual = {bit for bit in range(32) if mask >> bit & 1}
        self.assertEqual(
            actual,
            expected,
            f"mask claims {sorted(actual - expected)} with nothing in the pool, and misses "
            f"{sorted(expected - actual)} that is",
        )


class TestAllCategoriesBaseline(_MaskMatchesPoolMixin, KARTestBase):
    """Opt-in (every category): non-progression rewards are in the pool."""

    options = {**ALL_MODES, **_ALL_SELECTED}

    def test_rewards_present(self):
        self.assertTrue(self.world.reward_pool, "reward_pool should be non-empty with every category selected")
        self.assertTrue(
            NONPROG_REWARDS & self.world_item_names(),
            "expected non-progression rewards in the pool with every category selected",
        )

    def test_every_category_represented(self):
        present = self.world_item_names()
        for category, names in CHECKLIST_REWARD_CATEGORIES.items():
            self.assertTrue(
                {str(n) for n in names} & present,
                f"category {category!r} selected but none of its rewards reached the pool",
            )

    def test_mask_names_each_mode_own_reward_types(self):
        # Three reward types are exclusive to one mode: the Special Machine Intros movie to Air Ride,
        # extra rules to Top Ride, the pause-screen power-up display to City Trial.
        mask = self.world.fill_slot_data()["checklist_rewards"]
        shared = {RewardType.FILLER, RewardType.SOUND_TEST, RewardType.MUSIC, RewardType.ENDING}
        self.assertEqual(mode_bits(mask, GameMode.AIRRIDE), shared | {RewardType.BONUS_MOVIE})
        self.assertEqual(mode_bits(mask, GameMode.TOPRIDE), shared | {RewardType.EXTRA_RULE})
        self.assertEqual(mode_bits(mask, GameMode.CITYTRIAL), shared | {RewardType.PAUSE_POWERUPS})


class _NoneSelectedInvariantMixin(_MixinBase):
    """Shared invariants for any mode combination with no checklist_rewards category selected."""

    def test_no_nonprog_rewards_anywhere(self):
        present = NONPROG_REWARDS & self.world_item_names()
        self.assertFalse(present, f"non-progression rewards leaked into the seed: {sorted(present)[:5]}")

    def test_reward_pool_empty(self):
        self.assertEqual(self.world.reward_pool, [], "reward_pool must be empty with no category selected")

    def test_only_progression_reward_markers_remain(self):
        all_reward_names = NONPROG_REWARDS | PROG_REWARD_MARKERS
        present_rewards = all_reward_names & self.world_item_names()
        self.assertTrue(
            present_rewards <= PROG_REWARD_MARKERS,
            f"only progression part markers may remain; found {sorted(present_rewards - PROG_REWARD_MARKERS)[:5]}",
        )

    def test_mask_empty(self):
        self.assertEqual(self.world.fill_slot_data()["checklist_rewards"], 0)

    def test_pool_fills_placeable_locations(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


class TestNoneSelectedAllModes(_NoneSelectedInvariantMixin, KARTestBase):
    options = {**ALL_MODES, **_NONE_SELECTED}

    def test_part_markers_retained(self):
        # City Trial is enabled here, so all 6 progression part markers stay in the pool untouched.
        self.assertEqual(PROG_REWARD_MARKERS & self.world_item_names(), PROG_REWARD_MARKERS)


class TestNoneSelectedCTOnly(_NoneSelectedInvariantMixin, KARTestBase):
    options = {**CT_ONLY, **_NONE_SELECTED}


class TestNoneSelectedAROnly(_NoneSelectedInvariantMixin, KARTestBase):
    options = {**AR_ONLY, **_NONE_SELECTED}


class TestNoneSelectedTROnly(_NoneSelectedInvariantMixin, KARTestBase):
    options = {**TR_ONLY, **_NONE_SELECTED}


class TestPartialSelection(_MaskMatchesPoolMixin, KARTestBase):
    """Only the selected categories are placed; the rest leave the pool for the mod to unlock."""

    _KEPT = ["Filler Boxes", "Gameplay Extras"]
    options = {**ALL_MODES, "checklist_rewards": _KEPT}

    def test_kept_categories_present(self):
        present = self.world_item_names()
        for category in self._KEPT:
            self.assertTrue(
                {str(n) for n in CHECKLIST_REWARD_CATEGORIES[category]} & present,
                f"category {category!r} selected but none of its rewards reached the pool",
            )

    def test_dropped_categories_absent(self):
        present = self.world_item_names()
        for category, names in CHECKLIST_REWARD_CATEGORIES.items():
            if category in self._KEPT:
                continue
            leaked = {str(n) for n in names} & present
            self.assertFalse(leaked, f"category {category!r} not selected but leaked {sorted(leaked)[:5]}")

    def test_reward_pool_only_kept_categories(self):
        kept_names = {str(n) for category in self._KEPT for n in CHECKLIST_REWARD_CATEGORIES[category]}
        self.assertTrue(self.world.reward_pool)
        self.assertTrue(set(self.world.reward_pool) <= kept_names)

    def test_mask_names_only_kept_categories(self):
        mask = self.world.fill_slot_data()["checklist_rewards"]
        self.assertEqual(mode_bits(mask, GameMode.AIRRIDE), {RewardType.FILLER, RewardType.BONUS_MOVIE})
        self.assertEqual(mode_bits(mask, GameMode.TOPRIDE), {RewardType.FILLER, RewardType.EXTRA_RULE})
        self.assertEqual(mode_bits(mask, GameMode.CITYTRIAL), {RewardType.FILLER, RewardType.PAUSE_POWERUPS})


class TestDisabledModeShipsNoBits(_MaskMatchesPoolMixin, KARTestBase):
    """Every category selected, but only City Trial enabled. Air Ride and Top Ride rewards are never
    placed, so their bits must stay clear and the mod unlocks that content at connect - otherwise the
    16 music tracks, 18 sound test entries and the rest of their rewards would be unreachable."""

    options = {**CT_ONLY, **_ALL_SELECTED}

    def test_disabled_modes_ship_no_bits(self):
        mask = self.world.fill_slot_data()["checklist_rewards"]
        self.assertEqual(mode_bits(mask, GameMode.AIRRIDE), set())
        self.assertEqual(mode_bits(mask, GameMode.TOPRIDE), set())

    def test_enabled_mode_ships_its_types(self):
        mask = self.world.fill_slot_data()["checklist_rewards"]
        self.assertEqual(
            mode_bits(mask, GameMode.CITYTRIAL),
            {
                RewardType.FILLER,
                RewardType.SOUND_TEST,
                RewardType.MUSIC,
                RewardType.ENDING,
                RewardType.PAUSE_POWERUPS,
            },
        )


class TestNoneSelectedFullFill(KARTestBase):
    """A full fill succeeds, places no non-progression reward anywhere, and stays beatable."""

    options = {**ALL_MODES, **_NONE_SELECTED}

    def test_no_nonprog_reward_placed(self):
        from Fill import distribute_items_restrictive

        distribute_items_restrictive(self.multiworld)
        placed = [
            loc.item.name
            for loc in self.multiworld.get_locations()
            if loc.item is not None and loc.item.player == self.player and loc.item.name in NONPROG_REWARDS
        ]
        self.assertEqual(placed, [], f"non-progression reward(s) placed despite no category selected: {placed[:5]}")

    def test_beatable_after_collect_all(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


# CT-only config tuned so the 7 useful City Trial checklist rewards decide the needs-default budget:
# 75 base CT progression + 6 Patch Cap Increases + 5 checkbox fillers = 86 with rewards off (fits under
# City Trial's 90 default locations) vs 93 with the rewards on (overflows). AP Patches are held out so
# the budget is the checklist's alone - any count of them just adds default locations to absorb it.
_REWARD_RELAX_OPTIONS = {
    **CT_ONLY,
    "ap_patches": 0,
    "city_trial_patch_cap_min": 12,
    "city_trial_patch_cap_max": 18,
}


class TestAllCategoriesTightPoolRaises(KARTestBase):
    """With every category selected, the tight fixture's useful rewards tip the needs-default budget over."""

    options = {**_REWARD_RELAX_OPTIONS, **_ALL_SELECTED}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestNoneSelectedRelaxesCapacity(KARTestBase):
    """Dropping the non-progression rewards relaxes the needs-default budget, so the same tight config
    that OptionErrors with every category selected generates with none."""

    options = {**_REWARD_RELAX_OPTIONS, **_NONE_SELECTED}

    def test_generates(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))
        self.assertFalse(NONPROG_REWARDS & self.world_item_names())
