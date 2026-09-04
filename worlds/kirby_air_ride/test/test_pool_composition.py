"""
Item-pool composition tests: what _build_item_pools and create_items mint, and how many.

Covers the option-derived quantities (patch caps, spawn-rate ups, checkbox fillers), the exclusion
paths (allowed_items, traps, the source-modes backstop, gate reconciliation), and the invariant that
the minted pool exactly fills the placeable locations. Several options here default to a state that
makes their pool empty - `checklist_rewards` most of all - so a config that means to exercise one has
to select its categories explicitly or the assertions pass over nothing.
"""

from collections import Counter

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARItems import (
    ALLOWED_ITEM_CATEGORY_ITEMS,
    CHECKLIST_REWARD_TYPES,
    ITEM_TABLE,
    STADIUM_CHECKLIST_REWARDS,
    KARItemGroup,
    KARItemName,
    KARItemType,
)
from ..KAROptions import CityTrialGoal
from ..KARRegions import KARRegion
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, items_of_type


class TestPatchCapIncreaseCount(KARTestBase):
    # ALL_MODES gives the pool room for 9 Patch Cap Increases on top of full gating + unique CT rewards;
    # patch caps stay City-Trial items, so the count is still 9.
    options = {
        **ALL_MODES,
        "city_trial_patch_cap_min": 9,
        "city_trial_patch_cap_max": 18,
    }

    def test_count_equals_range_span(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 9)


class TestSpawnRateUpCount(KARTestBase):
    # ALL_MODES gives room for 20 Spawn Rate Up items alongside the gating unlocks.
    options = {
        **ALL_MODES,
        "spawn_rate_min": 100,
        "spawn_rate_max": 300,
    }

    def test_count_equals_range_steps(self):
        # (300 - 100) // 10 = 20
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 20)


class TestSpawnRateUpCountOffGrid(KARTestBase):
    # Spawn rate moves in 10% steps, so off-grid bounds snap to the nearest multiple of 10 before the pool
    # size is computed: min 64 -> 60, max 227 -> 230, giving (230 - 60) // 10 = 17.
    options = {
        **ALL_MODES,
        "spawn_rate_min": 64,
        "spawn_rate_max": 227,
    }

    def test_count_uses_snapped_bounds(self):
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 17)


class TestSpawnRateNoGrowth(KARTestBase):
    # min == max (the default 100/100): no growth, so no Spawn Rate Up items are placed.
    options = {**CT_ONLY, "spawn_rate_min": 100, "spawn_rate_max": 100}

    def test_no_spawn_rate_items(self):
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 0)


class TestSpawnRateSubVanillaMin(KARTestBase):
    # A sub-vanilla min grows toward the ceiling: (100 - 50) // 10 = 5 Spawn Rate Up items climb 50% -> 100%.
    options = {**CT_ONLY, "spawn_rate_min": 50, "spawn_rate_max": 100}

    def test_count_equals_range_steps(self):
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 5)


class TestCheckboxFillerCounts(KARTestBase):
    options = {
        **ALL_MODES,
        "city_trial_checkbox_fillers": 3,
        "air_ride_checkbox_fillers": 7,
        "top_ride_checkbox_fillers": 2,
    }

    def test_per_mode_counts(self):
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_CITY_TRIAL), 3)
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_AIR_RIDE), 7)
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_TOP_RIDE), 2)


class TestPermanentPatchesDisabled(KARTestBase):
    # Permanent Patches dropped from allowed_items (the other categories stay on).
    options = {
        **CT_ONLY,
        "allowed_items": [
            "City Trial Item Gives",
            "City Trial Event Gives",
            "Copy Ability Gives",
            "Top Ride Item Gives",
        ],
    }

    def test_no_permanent_patches_in_pool(self):
        perm_names = items_of_type(KARItemType.PERMANENT_PATCH)
        pool_names = set(self.itempool_names())
        leaked = pool_names & perm_names
        self.assertFalse(leaked, f"Permanent patches leaked when disabled: {sorted(leaked)}")


class TestAllowedItemsAllOn(KARTestBase):
    """With all five categories on, every category's non-trap items are eligible. None of these types are
    progression/reward/counted, so eligibility is exactly useful_pool | filler_pool."""

    options = {**ALL_MODES, "allowed_items": sorted(ALLOWED_ITEM_CATEGORY_ITEMS)}

    def test_all_categories_eligible(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        for category, names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            with self.subTest(category=category):
                missing = set(names) - eligible
                self.assertFalse(missing, f"{category} items not eligible when allowed: {sorted(missing)}")


class TestAllowedItemsDefaultPermanentPatchesOnly(KARTestBase):
    """The default is "Permanent Patches" alone: its non-trap items are eligible and every other category's
    are kept out of the pool and the draw pools."""

    options = ALL_MODES

    def test_permanent_patches_eligible(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        names = set(ALLOWED_ITEM_CATEGORY_ITEMS[KARItemGroup.PERMANENT_PATCHES])
        self.assertTrue(names <= eligible, f"Permanent patches not eligible by default: {sorted(names - eligible)}")

    def test_other_categories_absent(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        pool_names = set(self.itempool_names())
        for category, names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            if category == KARItemGroup.PERMANENT_PATCHES:
                continue
            with self.subTest(category=category):
                self.assertFalse(set(names) & eligible, f"{category} eligible by default")
                self.assertFalse(set(names) & pool_names, f"{category} item in pool by default")


class TestAllowedItemsCategoryDisabled(KARTestBase):
    """Removing categories from allowed_items keeps all of their non-trap items out of the pool and the draw
    pools, while kept categories stay eligible. Keeps filler-providing categories on so the config fills."""

    _KEPT = ["Permanent Patches", "City Trial Item Gives", "Top Ride Item Gives"]
    options = {**ALL_MODES, "allowed_items": _KEPT}

    def test_disabled_categories_absent(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        pool_names = set(self.itempool_names())
        for category, names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            if category in self._KEPT:
                continue
            with self.subTest(category=category):
                self.assertFalse(set(names) & eligible, f"{category} still eligible when disabled")
                self.assertFalse(set(names) & pool_names, f"{category} item in pool when disabled")

    def test_kept_categories_eligible(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        for category in self._KEPT:
            with self.subTest(category=category):
                self.assertTrue(set(ALLOWED_ITEM_CATEGORY_ITEMS[category]) <= eligible)


class TestAllowedItemsTrapsOrthogonal(KARTestBase):
    """allowed_items governs only NON-trap items. With every give category disabled, the trap-class items of
    those same types (fake patches, down patches, Copy Ability: Sleep, TR Speed Down) must still be
    trap-eligible, since `traps` is the sole governor of traps. (trap_chance 100 + traps on so it fills.)"""

    options = {
        **ALL_MODES,
        "allowed_items": [],
        "trap_chance": 100,
        "traps": ["Direct Damage", "Stat Debuff", "Fake Patches"],
    }

    def test_non_trap_gives_absent_but_traps_eligible(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        for category, names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            with self.subTest(category=category):
                self.assertFalse(set(names) & eligible, f"{category} non-trap items eligible when disabled")
        # Trap-class items of these give-types remain governed by `traps`, not allowed_items.
        for trap_name in (
            KARItemName.FAKE_BOOST_PATCH,
            KARItemName.BOOST_DOWN_PATCH,
            KARItemName.COPY_ABILITY_SLEEP,
            KARItemName.GIVE_TR_ITEM_SPEED_DOWN,
        ):
            with self.subTest(trap=trap_name):
                self.assertIn(trap_name, self.world.trap_pool)


class TestNoTrapsWhenChanceZero(KARTestBase):
    options = {**CT_ONLY, "trap_chance": 0}

    def test_no_trap_classification_in_pool(self):
        traps = [item for item in self.itempool_items() if item.classification & ItemClassification.trap]
        self.assertEqual(traps, [], f"Traps placed with trap_chance=0: {[t.name for t in traps]}")


class TestPatchCapMinEqualsMax(KARTestBase):
    """Boundary: min == max (here the vanilla 18) means a flat cap and 0 Patch Cap Increase items."""

    options = {
        **CT_ONLY,
        "city_trial_patch_cap_min": 18,
        "city_trial_patch_cap_max": 18,
    }

    def test_zero_patch_cap_items(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 0)


class TestPatchCapFullSpan(KARTestBase):
    """Boundary: full span min=1 -> max=30 (the option extremes) with most gating off so the 29-item pool
    fits. Pins that the max value is reachable in a real config."""

    options = {
        **ALL_MODES,
        "city_trial_patch_cap_min": 1,
        "city_trial_patch_cap_max": 30,
        "city_trial_stadiums_gated": Toggle.option_false,
        "city_trial_events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "city_trial_patches_gated": Toggle.option_false,
        "machines_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
        "city_trial_items_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "top_ride_items_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_count_equals_range_span(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 29)


class TestChecklistAmountMin(KARTestBase):
    """Boundary: city_trial_checklist_amount=1. The n_checklist_blocks event is still created and victory
    placed."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_n_checklist_blocks,
        "city_trial_checklist_amount": 1,
        "city_trial_checkbox_fillers": 0,
    }

    def test_victory_placed(self):
        self.assertIn(KARItemName.CITY_TRIAL_VICTORY, self.placed_event_items())


class TestChecklistAmountMax(KARTestBase):
    """Boundary: city_trial_checklist_amount=120 (the full CT checklist count)."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_n_checklist_blocks,
        "city_trial_checklist_amount": 120,
        "city_trial_checkbox_fillers": 0,
    }

    def test_event_created_for_full_count(self):
        self.assertIn(
            f"{KARRegion.CITY_TRIAL}: Complete 120 Checklist Blocks",
            self.event_location_names(),
        )


class TestPoolFillsAllLocations(KARTestBase):
    """The itempool item count should equal the placeable (non-locked, non-event) location count."""

    options = ALL_MODES

    def test_pool_size_matches_locations(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


class TestStadiumRewardsExcludedWhenUngated(KARTestBase):
    """Stadiums ungated: the mod unlocks all 24 at connect, so every Unlock Stadium item is excluded AND the
    six overlapping stadium checklist rewards are excluded (they gate nothing). No reward is ever promoted to
    progression."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_false}

    def test_stadium_rewards_excluded_from_pool(self):
        names = self.world_item_names()
        for reward in STADIUM_CHECKLIST_REWARDS:
            with self.subTest(reward=reward):
                self.assertNotIn(reward, names, f"{reward} should be excluded when stadiums are ungated")

    def test_stadium_unlocks_excluded_when_ungated(self):
        names = self.world_item_names()
        for unlock in items_of_type(KARItemType.CT_STADIUM_UNLOCK):
            self.assertNotIn(unlock, names, f"{unlock} should be excluded when stadiums are ungated")


class TestStadiumUnlocksPlacedWhenGated(KARTestBase):
    """Stadiums gated: every Unlock Stadium item is obtainable (23 in the pool + 1 precollected starter),
    and the six overlapping stadium checklist rewards are still excluded (gated by their unlock instead)."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true}

    def test_all_stadium_unlocks_obtainable(self):
        names = self.world_item_names()
        for unlock in items_of_type(KARItemType.CT_STADIUM_UNLOCK):
            with self.subTest(unlock=unlock):
                self.assertIn(unlock, names, f"{unlock} should be placed or precollected when stadiums gated")

    def test_stadium_rewards_excluded(self):
        names = self.world_item_names()
        for reward in STADIUM_CHECKLIST_REWARDS:
            with self.subTest(reward=reward):
                self.assertNotIn(reward, names)


class TestPatchCapExcludedWhenCTDisabled(KARTestBase):
    """Patch caps are a CT-only mechanic. With CT disabled (AR-only) and a growing cap span set,
    Patch Cap Increase items are still excluded: they have no effect outside CT."""

    options = {
        **AR_ONLY,
        "city_trial_patch_cap_min": 1,
        "city_trial_patch_cap_max": 30,
    }

    def test_no_patch_cap_items_in_pool(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 0)


class TestPermanentPatchesExcludedWhenCTDisabled(KARTestBase):
    """Permanent patches are CT-only. Even with their allowed_items category ON (the default),
    with CT disabled they should not appear in the pool (source-modes backstop)."""

    options = AR_ONLY

    def test_no_permanent_patches_in_pool(self):
        perm_names = items_of_type(KARItemType.PERMANENT_PATCH)
        leaked = set(self.itempool_names()) & perm_names
        self.assertFalse(leaked, f"Permanent patches leaked when CT disabled: {sorted(leaked)}")


class TestDropPatchesTrapExcludedWhenCTDisabled(KARTestBase):
    """Drop Patches Trap only fires in City Trial scenes. With CT disabled, it is excluded even if
    trap_chance > 0."""

    options = {
        **TR_ONLY,
        "trap_chance": 50,
    }

    def test_no_drop_patches_trap_in_pool(self):
        self.assertEqual(self.count_in_pool(KARItemName.DROP_PATCHES_TRAP), 0)


class TestChecklistRewardsUnique(KARTestBase):
    """Checklist rewards are unique one-time unlocks, not draw-with-replacement filler. Regression pin for
    the old 'reward soup' bug, where ~half were absent while others repeated. Now: useful rewards appear
    exactly once (they consume scarce default locations); filler rewards appear at least once and may
    repeat as junk-box filler. No reward category is selected by default, so this selects them all."""

    options = {**ALL_MODES, "checklist_rewards": ["Endings", "Filler Boxes", "Gameplay Extras", "Music", "Sound Test"]}

    def test_in_scope_rewards_present_useful_exactly_once(self):
        counts = Counter(self.itempool_names())
        self.assertTrue(self.world.reward_pool, "reward_pool should be populated for ALL_MODES")
        for name in self.world.reward_pool:
            data = ITEM_TABLE[name]
            with self.subTest(reward=name):
                if data.classification & ItemClassification.useful:
                    self.assertEqual(counts[name], 1, f"{name} (useful reward) should appear exactly once")
                else:
                    self.assertGreaterEqual(counts[name], 1, f"{name} (filler reward) should appear at least once")

    def test_no_useful_reward_duplicated(self):
        # Useful checklist rewards must never duplicate - the core of the soup bug.
        counts = Counter(self.itempool_names())
        for name, data in ITEM_TABLE.items():
            if data.type in CHECKLIST_REWARD_TYPES and (data.classification & ItemClassification.useful):
                with self.subTest(reward=name):
                    self.assertLessEqual(counts[name], 1, f"useful reward {name} duplicated (soup-bug regression)")

    def test_reward_pool_has_no_duplicates(self):
        # The world's reward_pool itself lists each in-scope reward exactly once.
        self.assertEqual(
            len(self.world.reward_pool),
            len(set(self.world.reward_pool)),
            "reward_pool contains duplicate entries",
        )


class TestChecklistRewardsUniqueSingleModes(KARTestBase):
    """Same uniqueness contract in a single-mode config. Air Ride is the tight one: its only repeatable
    filler is the reclassified CT+AR patch-gives, so rewards must still each appear rather than be
    crowded out. No reward category is selected by default, so this selects them all too - without that
    reward_pool is empty and every assertion below passes over nothing."""

    options = {**AR_ONLY, "checklist_rewards": ["Endings", "Filler Boxes", "Gameplay Extras", "Music", "Sound Test"]}

    def test_ar_rewards_present_useful_exactly_once(self):
        counts = Counter(self.itempool_names())
        self.assertTrue(self.world.reward_pool, "reward_pool should be populated for AR_ONLY + every reward category")
        for name in self.world.reward_pool:
            data = ITEM_TABLE[name]
            with self.subTest(reward=name):
                if data.classification & ItemClassification.useful:
                    self.assertEqual(counts[name], 1)
                else:
                    self.assertGreaterEqual(counts[name], 1)

    def test_only_air_ride_rewards_are_in_scope(self):
        # The single-mode half of the contract: reward_pool holds Air Ride rewards and nothing else, and
        # no other mode's reward reaches the itempool.
        in_scope_types = {ITEM_TABLE[name].type for name in self.world.reward_pool}
        self.assertEqual(in_scope_types, {KARItemType.AR_CHECKLIST_REWARD})
        pool = set(self.itempool_names())
        for name, data in ITEM_TABLE.items():
            if data.type in (KARItemType.CT_CHECKLIST_REWARD, KARItemType.TR_CHECKLIST_REWARD):
                with self.subTest(reward=name):
                    self.assertNotIn(name, pool, f"{name} is an off-mode reward and must not be minted")


class TestNoTrapCategoriesWithTrapChance(KARTestBase):
    """trap_chance > 0 but `traps` selects no categories: trap_pool ends up empty and no trap items land in
    the pool. Regression pin that an empty category selection short-circuits trap placement."""

    options = {
        **ALL_MODES,
        "trap_chance": 50,
        "traps": [],
    }

    def test_trap_pool_empty(self):
        self.assertEqual(self.world.trap_pool, set())

    def test_no_traps_in_pool(self):
        traps = [item for item in self.itempool_items() if item.classification & ItemClassification.trap]
        self.assertEqual(traps, [], f"Traps in pool despite no trap categories selected: {[t.name for t in traps]}")
