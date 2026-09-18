"""The `checklist_rewards` option: which native rewards become AP items and which the mod unlocks itself.
Empty by default, but the six progression Dragoon/Hydra part markers stay whatever it says."""

from typing import TYPE_CHECKING

from Options import OptionError, Toggle

from ..KARData import GameMode, RewardType, checklist_reward_placed_bit
from ..KARItems import (
    CHECKLIST_REWARD_CATEGORIES,
    CHECKLIST_REWARD_ITEM_TYPES,
    CHECKLIST_REWARD_TYPE_MODES,
    CHECKLIST_REWARD_TYPES,
    ITEM_TABLE,
    ItemClassification,
)
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, names

# Type-check time the mixin inherits KARTestBase so `self.*` resolves; at runtime it is `object`, so a
# concrete `class X(Mixin, KARTestBase)` keeps the correct MRO.
_MixinBase = KARTestBase if TYPE_CHECKING else object

NONPROG_REWARDS = names(
    name
    for name, data in ITEM_TABLE.items()
    if data.type in CHECKLIST_REWARD_TYPES and not (data.classification & ItemClassification.progression)
)
PROG_REWARD_MARKERS = names(
    name
    for name, data in ITEM_TABLE.items()
    if data.type in CHECKLIST_REWARD_TYPES and (data.classification & ItemClassification.progression)
)

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


class TestAllCategoriesSelected(_MaskMatchesPoolMixin, KARTestBase):
    options = {**ALL_MODES, **_ALL_SELECTED}

    def test_every_category_reaches_the_pool(self):
        present = self.world_item_names()
        self.assertTrue(NONPROG_REWARDS & present, "no non-progression reward reached the pool")
        for category, category_names in CHECKLIST_REWARD_CATEGORIES.items():
            with self.subTest(category=category):
                self.assertTrue(names(category_names) & present, f"{category!r} selected but placed nothing")

    def test_mask_names_each_mode_own_reward_types(self):
        # Three reward types are exclusive to one mode: the Special Machine Intros movie to Air Ride,
        # extra rules to Top Ride, the pause-screen power-up display to City Trial.
        mask = self.world.fill_slot_data()["checklist_rewards"]
        shared = {RewardType.FILLER, RewardType.SOUND_TEST, RewardType.MUSIC, RewardType.ENDING}
        self.assertEqual(mode_bits(mask, GameMode.AIRRIDE), shared | {RewardType.BONUS_MOVIE})
        self.assertEqual(mode_bits(mask, GameMode.TOPRIDE), shared | {RewardType.EXTRA_RULE})
        self.assertEqual(mode_bits(mask, GameMode.CITYTRIAL), shared | {RewardType.PAUSE_POWERUPS})


class _NoneSelectedInvariantMixin(_MixinBase):
    """Invariants for any mode combination with no checklist_rewards category selected."""

    def test_no_nonprog_rewards_anywhere(self):
        present = NONPROG_REWARDS & self.world_item_names()
        self.assertFalse(present, f"non-progression rewards leaked: {sorted(present)[:5]}")
        self.assertEqual(self.world.reward_pool, [])
        self.assertEqual(self.world.fill_slot_data()["checklist_rewards"], 0)

    def test_progression_part_markers_are_the_only_rewards_left(self):
        present_rewards = (NONPROG_REWARDS | PROG_REWARD_MARKERS) & self.world_item_names()
        self.assertTrue(
            present_rewards <= PROG_REWARD_MARKERS,
            f"only part markers may remain; found {sorted(present_rewards - PROG_REWARD_MARKERS)[:5]}",
        )

    def test_the_freed_boxes_are_backfilled(self):
        self.assertEqual(len(self.itempool_items()), len(self.placeable_locations()))


def _make_none_selected_test(label: str, preset: dict) -> None:
    class _NoneSelected(_NoneSelectedInvariantMixin, KARTestBase):
        options = {**preset, **_NONE_SELECTED}

    _NoneSelected.__name__ = f"TestNoneSelected_{label}"
    _NoneSelected.__qualname__ = _NoneSelected.__name__
    globals()[_NoneSelected.__name__] = _NoneSelected


for _label, _preset in (("all_modes", ALL_MODES), ("ct_only", CT_ONLY), ("ar_only", AR_ONLY), ("tr_only", TR_ONLY)):
    _make_none_selected_test(_label, _preset)


class TestPartialSelection(_MaskMatchesPoolMixin, KARTestBase):
    """Only the selected categories are placed; the rest leave the pool for the mod to unlock."""

    _KEPT = ["Filler Boxes", "Gameplay Extras"]
    options = {**ALL_MODES, "checklist_rewards": _KEPT}

    def test_only_kept_categories_reach_the_pool(self):
        present = self.world_item_names()
        for category, category_names in CHECKLIST_REWARD_CATEGORIES.items():
            with self.subTest(category=category):
                overlap = names(category_names) & present
                if category in self._KEPT:
                    self.assertTrue(overlap, f"{category!r} selected but placed nothing")
                else:
                    self.assertFalse(overlap, f"{category!r} not selected but leaked {sorted(overlap)[:5]}")

    def test_reward_pool_holds_only_kept_categories(self):
        kept_names = {str(n) for category in self._KEPT for n in CHECKLIST_REWARD_CATEGORIES[category]}
        self.assertTrue(self.world.reward_pool)
        self.assertTrue(set(self.world.reward_pool) <= kept_names)

    def test_mask_names_only_kept_categories(self):
        mask = self.world.fill_slot_data()["checklist_rewards"]
        self.assertEqual(mode_bits(mask, GameMode.AIRRIDE), {RewardType.FILLER, RewardType.BONUS_MOVIE})
        self.assertEqual(mode_bits(mask, GameMode.TOPRIDE), {RewardType.FILLER, RewardType.EXTRA_RULE})
        self.assertEqual(mode_bits(mask, GameMode.CITYTRIAL), {RewardType.FILLER, RewardType.PAUSE_POWERUPS})


class TestDisabledModeShipsNoBits(_MaskMatchesPoolMixin, KARTestBase):
    """Every category selected but only City Trial enabled: Air Ride and Top Ride rewards are never
    placed, so their bits must stay clear and the mod unlocks that content at connect - otherwise their
    16 music tracks, 18 sound test entries and the rest would be unreachable."""

    options = {**CT_ONLY, **_ALL_SELECTED}

    def test_disabled_modes_ship_no_bits(self):
        mask = self.world.fill_slot_data()["checklist_rewards"]
        self.assertEqual(mode_bits(mask, GameMode.AIRRIDE), set())
        self.assertEqual(mode_bits(mask, GameMode.TOPRIDE), set())
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
    """A full distribute_items_restrictive places no non-progression reward and stays beatable."""

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


# Tuned so the useful City Trial rewards alone decide the needs-default budget: 65 progression + 15
# counted-useful = exactly the 80 default boxes City Trial has once multiplayer counts as progression,
# which the 6 useful rewards then overflow to 86. AP Patches are held out so the budget is the
# checklist's alone - any count of them just adds default locations to absorb it.
_REWARD_RELAX_OPTIONS = {
    **CT_ONLY,
    "ap_patches": 0,
    "city_trial_progression_multiplayer": Toggle.option_true,
    "city_trial_patch_cap_min": 18,
    "city_trial_patch_cap_max": 18,
}


class TestAllCategoriesTightPoolRaises(KARTestBase):
    options = {**_REWARD_RELAX_OPTIONS, **_ALL_SELECTED}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaisesRegex(OptionError, r"needs \d+ non-excluded locations"):
            self.world_setup()


class TestNoneSelectedRelaxesCapacity(KARTestBase):
    """Dropping the non-progression rewards relaxes the needs-default budget, so the same tight config
    that OptionErrors with every category selected generates with none."""

    options = {**_REWARD_RELAX_OPTIONS, **_NONE_SELECTED}

    def test_generates(self):
        self.assertEqual(len(self.itempool_items()), len(self.placeable_locations()))
        self.assertFalse(NONPROG_REWARDS & self.world_item_names())
