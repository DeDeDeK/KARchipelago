from BaseClasses import ItemClassification
from Options import Toggle

from ..KARItems import STADIUM_UNLOCK_TO_CHECKLIST_REWARD, KARItemName, KARItemType
from ..KAROptions import CityTrialGoal
from ..KARRegions import KARRegion
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, items_of_type


class TestPatchCapIncreaseCount(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_progressive_patch_caps": Toggle.option_true,
        "city_trial_patch_cap_amount": 10,
    }

    def test_count_equals_target_minus_one(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 9)


class TestPatchCapDisabled(KARTestBase):
    options = {**CT_ONLY, "city_trial_progressive_patch_caps": Toggle.option_false}

    def test_no_patch_cap_items(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 0)


class TestSpawnRateUpCount(KARTestBase):
    # Use ALL_MODES so there's room for 20 Spawn Rate Up items alongside the
    # gating unlock progression items.
    options = {
        **ALL_MODES,
        "spawn_rate_progressive": Toggle.option_true,
        "spawn_rate_min": 100,
        "spawn_rate_max": 300,
    }

    def test_count_equals_range_steps(self):
        # (300 - 100) // 10 = 20
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 20)


class TestSpawnRateProgressiveDisabled(KARTestBase):
    options = {**CT_ONLY, "spawn_rate_progressive": Toggle.option_false}

    def test_no_spawn_rate_items(self):
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 0)


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


class TestEffectItemsDisabled(KARTestBase):
    options = {**CT_ONLY, "effect_items_enabled": Toggle.option_false}

    def test_no_effect_items_in_pool(self):
        # SPAWN_RATE_UP is EFFECT-typed but governed by spawn_rate_progressive, so it
        # legitimately can appear even with effect_items_enabled off when progressive is on.
        # CT_ONLY defaults to progressive off, so we don't need to exclude it here.
        effect_names = items_of_type(KARItemType.EFFECT)
        pool_names = set(self.itempool_names())
        leaked = pool_names & effect_names
        self.assertFalse(leaked, f"Effect items leaked when disabled: {sorted(leaked)}")


class TestSpawnRateUpSurvivesEffectItemsDisabled(KARTestBase):
    # Regression: SPAWN_RATE_UP was typed EFFECT and got swept out by effect_items_enabled=off,
    # contradicting spawn_rate_progressive's docstring promise that it ships these items.
    options = {
        **ALL_MODES,
        "effect_items_enabled": Toggle.option_false,
        "spawn_rate_progressive": Toggle.option_true,
        "spawn_rate_min": 100,
        "spawn_rate_max": 200,
    }

    def test_spawn_rate_up_in_pool(self):
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 10)

    def test_other_effect_items_still_absent(self):
        other_effects = items_of_type(KARItemType.EFFECT) - {KARItemName.SPAWN_RATE_UP}
        pool_names = set(self.itempool_names())
        leaked = pool_names & other_effects
        self.assertFalse(leaked, f"Non-SPAWN_RATE_UP effect items leaked: {sorted(leaked)}")


class TestPermanentPatchesDisabled(KARTestBase):
    options = {**CT_ONLY, "city_trial_permanent_patches": Toggle.option_false}

    def test_no_permanent_patches_in_pool(self):
        perm_names = items_of_type(KARItemType.PERMANENT_PATCH)
        pool_names = set(self.itempool_names())
        leaked = pool_names & perm_names
        self.assertFalse(leaked, f"Permanent patches leaked when disabled: {sorted(leaked)}")


class TestNoTrapsWhenChanceZero(KARTestBase):
    options = {**CT_ONLY, "trap_chance": 0}

    def test_no_trap_classification_in_pool(self):
        traps = [item for item in self.itempool_items() if item.classification & ItemClassification.trap]
        self.assertEqual(traps, [], f"Traps placed with trap_chance=0: {[t.name for t in traps]}")


class TestPatchCapAmountOne(KARTestBase):
    """Boundary: patch_cap_amount=1 means 0 progressive items (target - 1 = 0)."""

    options = {
        **CT_ONLY,
        "city_trial_progressive_patch_caps": Toggle.option_true,
        "city_trial_patch_cap_amount": 1,
    }

    def test_zero_patch_cap_items(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 0)


class TestPatchCapAmountMax(KARTestBase):
    """Boundary: patch_cap_amount=127 (the PowerPC hardware ceiling) with most gating
    off so the 126-item pool fits. Pins that the max value is reachable in a real config."""

    options = {
        **ALL_MODES,
        "city_trial_progressive_patch_caps": Toggle.option_true,
        "city_trial_patch_cap_amount": 127,
        "city_trial_progressive_stadiums": Toggle.option_false,
        "events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "patches_gated": Toggle.option_false,
        "machines_gated": Toggle.option_false,
        "boxes_gated": Toggle.option_false,
        "city_trial_items_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "top_ride_items_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_count_equals_target_minus_one(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 126)


class TestChecklistAmountMin(KARTestBase):
    """Boundary: city_trial_checklist_amount=1. The n_checklist_blocks event should
    still be created and victory placed."""

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


class TestSpawnRateMinEqualsMax(KARTestBase):
    """Boundary: spawn_rate_min == spawn_rate_max produces no Spawn Rate Up items.
    The exclusion at KARWorld._build_item_pools must trigger; otherwise stale items
    would land in the pool with no progression range to traverse."""

    options = {
        **CT_ONLY,
        "spawn_rate_progressive": Toggle.option_true,
        "spawn_rate_min": 150,
        "spawn_rate_max": 150,
    }

    def test_no_spawn_rate_items(self):
        self.assertEqual(self.count_in_pool(KARItemName.SPAWN_RATE_UP), 0)


class TestPoolFillsAllLocations(KARTestBase):
    """The itempool item count should equal the placeable (non-locked, non-event) location count."""

    options = ALL_MODES

    def test_pool_size_matches_locations(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


class TestStadiumRewardsNotPromotedWhenProgressiveOff(KARTestBase):
    """Counter-test for TestStadiumRewardsPromotedWhenProgressiveOn: when progressive_stadiums
    is OFF, the 6 checklist-reward stadium overlaps keep their ITEM_TABLE classification and
    do NOT get promoted to progression. Pins the second branch of the conditional in
    _build_item_pools / create_item."""

    options = {**CT_ONLY, "city_trial_progressive_stadiums": Toggle.option_false}

    def test_stadium_rewards_as_progression_empty(self):
        self.assertEqual(
            self.world.stadium_rewards_as_progression,
            set(),
            "promotion set should be empty when progressive_stadiums is OFF",
        )

    def test_overlapping_rewards_keep_table_classification(self):
        # The same 6 reward items that would be promoted under progressive ON should
        # NOT be progression-classified under progressive OFF — they keep their
        # ITEM_TABLE classification (filler / useful).
        from ..KARItems import ITEM_TABLE

        for reward in STADIUM_UNLOCK_TO_CHECKLIST_REWARD.values():
            with self.subTest(reward=reward):
                item = self.world.create_item(reward)
                self.assertEqual(
                    item.classification,
                    ITEM_TABLE[reward].classification,
                    f"{reward} should keep its table classification when progressive_stadiums is OFF",
                )


class TestPatchCapExcludedWhenCTDisabled(KARTestBase):
    """progressive_patch_caps is a CT-only mechanic. With CT disabled (AR-only goal) and
    progressive_patch_caps ON, the Patch Cap Increase items should still be excluded —
    they have no effect outside CT."""

    options = {
        **AR_ONLY,
        "city_trial_progressive_patch_caps": Toggle.option_true,
        "city_trial_patch_cap_amount": 50,
    }

    def test_no_patch_cap_items_in_pool(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 0)


class TestPermanentPatchesExcludedWhenCTDisabled(KARTestBase):
    """Permanent patches are CT-only. Even with the toggle ON, with CT disabled they
    should not appear in the pool."""

    options = {**AR_ONLY, "city_trial_permanent_patches": Toggle.option_true}

    def test_no_permanent_patches_in_pool(self):
        perm_names = items_of_type(KARItemType.PERMANENT_PATCH)
        leaked = set(self.itempool_names()) & perm_names
        self.assertFalse(leaked, f"Permanent patches leaked when CT disabled: {sorted(leaked)}")


class TestDropPatchesTrapExcludedWhenCTDisabled(KARTestBase):
    """Drop Patches Trap only fires in City Trial scenes (mod gates on Gm_IsInCity).
    With CT disabled, it should be excluded even if trap_chance > 0."""

    options = {
        **TR_ONLY,
        "trap_chance": 50,
    }

    def test_no_drop_patches_trap_in_pool(self):
        self.assertEqual(self.count_in_pool(KARItemName.DROP_PATCHES_TRAP), 0)


class TestAllTrapWeightsZeroWithTrapChance(KARTestBase):
    """trap_chance > 0 but every per-category trap weight = 0: trap_weights dict ends up
    empty, _pick_trap is never called, and no trap items land in the pool. Regression pin
    that the weight=0 short-circuit in _build_item_pools is honoured."""

    options = {
        **ALL_MODES,
        "trap_chance": 50,
        "trap_weight_direct_damage": 0,
        "trap_weight_stat_debuff": 0,
        "trap_weight_fake_patches": 0,
        "trap_weight_hazards": 0,
    }

    def test_trap_weights_empty(self):
        self.assertEqual(self.world.trap_weights, {})

    def test_no_traps_in_pool(self):
        traps = [item for item in self.itempool_items() if item.classification & ItemClassification.trap]
        self.assertEqual(traps, [], f"Traps in pool despite all weights zero: {[t.name for t in traps]}")
