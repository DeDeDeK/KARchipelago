"""
Access-rule tests for KARRules.set_rules().

Each test exercises one rule branch by asserting the rule-protected locations are unreachable
without the gating item and reachable when it is collected. only_check_listed=True keeps each
test focused on its rule without cross-checking unrelated locations.

Random starter picks are non-deterministic under default options. Where a test depends on a
specific starter not having been chosen, it pins the starter via start_inventory.
"""

from Options import Toggle

from ..KARItems import KARItemName
from ..KARLocations import ARLocation, CTLocation, TRLocation
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

# Pin the random starter picks so they don't shadow items under test.
_PIN_MACHINE_STARTER = {"start_inventory": {KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1}}
_PIN_PATCH_STARTER = {"start_inventory": {KARItemName.UNLOCK_PATCH_HP: 1}}
_PIN_AR_COURSE_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1}}
_PIN_TR_COURSE_STARTER = {"start_inventory": {KARItemName.UNLOCK_TR_COURSE_GRASS: 1}}
_PIN_STADIUM_STARTER = {"start_inventory": {KARItemName.UNLOCK_STADIUM_AIR_GLIDER: 1}}


class TestEventsGatingApplied(KARTestBase):
    """city_trial_events_gated ON: event-specific locations need their unlock items."""

    options = {**CT_ONLY, "city_trial_events_gated": Toggle.option_true}

    def test_dyna_blade_locations_need_unlock(self):
        self.assertAccessDependency(
            [CTLocation.DO_SOME_DAMAGE_TO_DYNA_BLADE, CTLocation.GET_TRAMPLED_BY_DYNA_BLADE],
            [[KARItemName.UNLOCK_EVENT_DYNA_BLADE]],
            only_check_listed=True,
        )

    def test_tac_location_needs_unlock(self):
        self.assertAccessDependency(
            [CTLocation.STEAL_8_FROM_TAC],
            [[KARItemName.UNLOCK_EVENT_TAC]],
            only_check_listed=True,
        )


class TestEventsGatingNotApplied(KARTestBase):
    """city_trial_events_gated OFF: event unlocks aren't in the pool and event locations have no rule."""

    options = {**CT_ONLY, "city_trial_events_gated": Toggle.option_false}

    def test_dyna_blade_location_reachable_empty(self):
        # No unlocks collected, but gate off means no rule, so reachable.
        self.assertTrue(self.can_reach_location(CTLocation.DO_SOME_DAMAGE_TO_DYNA_BLADE))

    def test_event_unlock_items_absent_from_pool(self):
        self.assertNotIn(KARItemName.UNLOCK_EVENT_DYNA_BLADE, self.world_item_names())
        self.assertNotIn(KARItemName.UNLOCK_EVENT_TAC, self.world_item_names())


class TestAbilitiesGatingApplied(KARTestBase):
    """abilities_gated ON: ability-specific locations need their unlock items.
    Covers Air Ride locations and the TR locations gated by ability unlocks
    (_ABILITY_TR_ITEM_RULES: Fire, Bomb)."""

    options = {**ALL_MODES, "abilities_gated": Toggle.option_true}

    def test_ar_wing_location_needs_wing_unlock(self):
        # FIRST_WITH_WING_ABILITY is in the top-level AIR_RIDE region (not course-gated).
        self.assertAccessDependency(
            [ARLocation.FIRST_WITH_WING_ABILITY],
            [[KARItemName.UNLOCK_ABILITY_WING]],
            only_check_listed=True,
        )

    def test_tr_fire_location_needs_fire_unlock(self):
        # TORCH_3_RIVALS is in the top-level TOP_RIDE region (no course gating);
        # the fire requirement comes from _ABILITY_TR_ITEM_RULES, not course gating.
        self.assertAccessDependency(
            [TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM],
            [[KARItemName.UNLOCK_ABILITY_FIRE]],
            only_check_listed=True,
        )

    def test_ct_bomb_location_needs_bomb_unlock(self):
        # COPY_CHANCE_WHEEL_BOMB is in the top-level CITY_TRIAL region.
        self.assertAccessDependency(
            [CTLocation.COPY_CHANCE_WHEEL_BOMB],
            [[KARItemName.UNLOCK_ABILITY_BOMB]],
            only_check_listed=True,
        )


class TestPatchesGatingApplied(KARTestBase):
    """city_trial_patches_gated ON: patch-specific locations need their unlock items."""

    # Pin the random patch starter to UNLOCK_PATCH_HP so the locations we test
    # (which all require non-HP patch unlocks) aren't accidentally pre-unlocked.
    options = {**CT_ONLY, "city_trial_patches_gated": Toggle.option_true, **_PIN_PATCH_STARTER}

    def test_boost_patches_need_accel_unlock(self):
        self.assertAccessDependency(
            [CTLocation.GET_10_BOOST_PATCHES],
            [[KARItemName.UNLOCK_PATCH_ACCEL]],
            only_check_listed=True,
        )

    def test_glide_30_needs_glide_unlock(self):
        self.assertAccessDependency(
            [CTLocation.GET_30_GLIDE_PATCHES],
            [[KARItemName.UNLOCK_PATCH_GLIDE]],
            only_check_listed=True,
        )


class TestCityTrialItemsGatingApplied(KARTestBase):
    """city_trial_items_gated ON: item-specific locations need their unlock items.
    Uses ALL_MODES because the 30 added unlock items need more default locations
    than CT-only provides."""

    options = {**ALL_MODES, "city_trial_items_gated": Toggle.option_true}

    def test_hot_dogs_location_needs_unlock(self):
        self.assertAccessDependency(
            [CTLocation.EAT_3_HOT_DOGS],
            [[KARItemName.UNLOCK_ITEM_HOT_DOG]],
            only_check_listed=True,
        )

    def test_fireworks_location_needs_unlock(self):
        self.assertAccessDependency(
            [CTLocation.USE_FIREWORKS_TO_KO_RIVALS_10X],
            [[KARItemName.UNLOCK_ITEM_FIREWORKS]],
            only_check_listed=True,
        )


class TestMachinesSingleGatingApplied(KARTestBase):
    """machines_gated ON: machine-specific locations need their unlock items."""

    options = {**ALL_MODES, "machines_gated": Toggle.option_true, **_PIN_MACHINE_STARTER}

    def test_formula_ct_location_needs_unlock(self):
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR1_17_00_FORMULA],
            [[KARItemName.UNLOCK_MACHINE_FORMULA_STAR]],
            only_check_listed=True,
        )

    def test_shadow_ar_location_needs_unlock(self):
        # The location also has a CanReachLocation prereq on DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
        # but that AR-root location stays reachable, so SHADOW_STAR is the binding constraint.
        self.assertAccessDependency(
            [ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR],
            [[KARItemName.UNLOCK_MACHINE_SHADOW_STAR]],
            only_check_listed=True,
        )


class TestMachinesPairGatingApplied(KARTestBase):
    """machines_gated ON: 'bust X on Y' locations need BOTH machine unlocks."""

    options = {**ALL_MODES, "machines_gated": Toggle.option_true, **_PIN_MACHINE_STARTER}

    def test_bust_wheelie_bike_on_warpstar_needs_both(self):
        self.assertAccessDependency(
            [CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR],
            [[KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE, KARItemName.UNLOCK_MACHINE_WARP_STAR]],
            only_check_listed=True,
        )


class TestTopRideItemsGatingApplied(KARTestBase):
    """top_ride_items_gated ON: TR-item-specific locations need their unlock items."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true}

    def test_hammer_location_needs_unlock(self):
        # FIRST_WHILE_HOLDING_HAMMER is in TR_TIME_ATTACK (not course-gated).
        self.assertAccessDependency(
            [TRLocation.FIRST_WHILE_HOLDING_HAMMER],
            [[KARItemName.UNLOCK_TR_ITEM_HAMMER]],
            only_check_listed=True,
        )

    def test_invincible_location_needs_unlock(self):
        self.assertAccessDependency(
            [TRLocation.GET_20_INVINCIBLE_CANDY_ITEMS],
            [[KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY]],
            only_check_listed=True,
        )


class TestProgressiveStadiumGating(KARTestBase):
    """progressive_stadiums ON: each stadium region requires its unlock item.
    Pin starter to AIR_GLIDER so other stadiums remain locked."""

    options = {
        **CT_ONLY,
        "city_trial_progressive_stadiums": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_dr1_stadium_location_needs_dr1_unlock(self):
        # DRAG_RACE_1 has no checklist-reward overlap, so the unlock item gates it directly.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR1_FINISH_00_24_00],
            [[KARItemName.UNLOCK_STADIUM_DRAG_RACE_1]],
            only_check_listed=True,
        )

    def test_dr4_stadium_location_needs_reward_item(self):
        # DRAG_RACE_4 IS a checklist-reward overlap: its unlock item is excluded from the
        # pool and CT_REWARD_DRAG_RACE_4_STADIUM carries progression instead. DR4 also has a
        # CanReachLocation(DR3_FINISH) prereq, but collect_all_but leaves DR3 reachable here.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR4_FINISH_00_24_00],
            [[KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM]],
            only_check_listed=True,
        )


class TestProgressiveStadiumAllGroupGating(KARTestBase):
    """STADIUM_DD_ALL and STADIUM_KM_ALL are reachable via ANY of their sub-stadium unlocks
    (HasAny rule). Pin starter so neither DD nor KM unlocks are pre-collected."""

    options = {
        **CT_ONLY,
        "city_trial_progressive_stadiums": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_dd_all_reachable_via_any_dd_unlock(self):
        # DD3/4/5 are checklist-reward overlaps, so their CT_REWARD_* items carry
        # progression in place of the excluded unlocks. The HasAny rule accepts any of
        # these five, so all five must be listed for the unreachable-without assertion.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X],
            [
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1],
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2],
                [KARItemName.CT_REWARD_DESTRUCTION_DERBY_3_STADIUM],
                [KARItemName.CT_REWARD_DESTRUCTION_DERBY_4_STADIUM],
                [KARItemName.CT_REWARD_DESTRUCTION_DERBY_5_STADIUM],
            ],
            only_check_listed=True,
        )

    def test_km_all_reachable_via_any_km_unlock(self):
        # KM2 is a checklist-reward overlap (uses CT_REWARD_KIRBY_MELEE_2_STADIUM
        # instead of UNLOCK_STADIUM_KIRBY_MELEE_2). Both alternatives must be
        # listed for the unreachable-without assertion to hold.
        self.assertAccessDependency(
            [CTLocation.STADIUM_KM_ALL_KO_500_ENEMIES],
            [
                [KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1],
                [KARItemName.CT_REWARD_KIRBY_MELEE_2_STADIUM],
            ],
            only_check_listed=True,
        )


class TestProgressiveStadiumPreservesChain(KARTestBase):
    """Regression: progressive_stadiums must compose with the DD/KM/DR chain prereqs, not overwrite.

    Stripping only the chain prerequisite (via [[chain_unlock]]) leaves the stadium's own gating
    item collected. If the chain rule were overwritten, the stadium would become reachable from
    its own gate alone, with the chain broken. Preserving the chain keeps it unreachable until
    the chain prereq is also satisfied."""

    options = {
        **CT_ONLY,
        "city_trial_progressive_stadiums": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_dd3_requires_dd2_chain_prereq(self):
        # DD_ALL -> DD3 entrance: CanReachLocation(DD2_KO_A_RIVAL_10X) & Has(DD3_REWARD).
        # Without DD2 unlock, DD2 is unreachable, DD2_KO is unreachable, chain fails.
        # DD3_REWARD stays collected (it's "everything else"), so a chain-overwrite bug
        # would make DD3 reachable purely from its own Has rule.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5],
            [[KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2]],
            only_check_listed=True,
        )

    def test_dr4_requires_dr3_chain_prereq(self):
        # CT -> DR4 entrance: CanReachLocation(DR3_FINISH_00_27_00) & Has(DR4_REWARD).
        # DR3 is not a checklist-reward overlap, so removing UNLOCK_STADIUM_DRAG_RACE_3
        # makes DR3 unreachable, the prereq location unreachable, and the chain fails.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR4_FINISH_00_24_00],
            [[KARItemName.UNLOCK_STADIUM_DRAG_RACE_3]],
            only_check_listed=True,
        )


class TestARCourseGatingApplied(KARTestBase):
    """air_ride_courses_gated ON: course-region locations need their course unlock."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    def test_checker_knights_location_needs_unlock(self):
        self.assertAccessDependency(
            [ARLocation.CK_RACE_5500_FEET],
            [[KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS]],
            only_check_listed=True,
        )

    def test_magma_flows_location_needs_unlock(self):
        self.assertAccessDependency(
            [ARLocation.MF_RACE_4800_FEET],
            [[KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS]],
            only_check_listed=True,
        )


class TestTRCourseGatingApplied(KARTestBase):
    """top_ride_courses_gated ON: course-region locations need their course unlock."""

    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true, **_PIN_TR_COURSE_STARTER}

    def test_sand_location_needs_unlock(self):
        self.assertAccessDependency(
            [TRLocation.SAND_NOITEMS_FIRST],
            [[KARItemName.UNLOCK_TR_COURSE_SAND]],
            only_check_listed=True,
        )


class TestARNebulaBeltEntranceRule(KARTestBase):
    """The three Nebula Belt regions are gated by CanReachLocation(RACE_100_LAPS).
    No AP checklist locations live inside Nebula Belt, so we pin the rule structurally:
    each entrance must have a non-default access_rule. If KARRules ever drops the rule,
    the entrance reverts to the framework's no-op access_rule and this test fails."""

    options = AR_ONLY

    def test_nebula_belt_entrances_have_access_rules(self):
        from BaseClasses import Entrance

        from ..KARRegions import KARRegion

        nebula_regions = [
            KARRegion.AR_NEBULA_BELT,
            KARRegion.AR_TA_NEBULA_BELT,
            KARRegion.AR_FR_NEBULA_BELT,
        ]
        for region_name in nebula_regions:
            with self.subTest(region=region_name):
                region = self.world.get_region(region_name)
                self.assertTrue(region.entrances, f"{region_name} should have an entrance")
                entrance = region.entrances[0]
                self.assertIsNot(
                    entrance.access_rule,
                    Entrance.access_rule,
                    f"{region_name} entrance is missing the RACE_100_LAPS gate",
                )


class TestARChainPrereqs(KARTestBase):
    """Sanity that each chain's dependent location is gated by its own machine unlock under
    collect_all_but. The chain rule itself is tested in TestARChainBreaksWhenPrereqGated."""

    options = {
        **AR_ONLY,
        "air_ride_courses_gated": Toggle.option_true,
        "machines_gated": Toggle.option_true,
        "start_inventory": {
            KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1,
            KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1,
        },
    }

    # (dependent location, prereq location, item-to-strip).
    # The prereq here is the AR-root DEFEAT_10_ENEMIES, which course gating can't make
    # unreachable, so we strip SHADOW_STAR to exercise the dependent's own gate in isolation.
    _CHAINS: list[tuple[str, str, str]] = [
        (
            ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR,
            ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
            KARItemName.UNLOCK_MACHINE_SHADOW_STAR,
        ),
    ]

    def test_dependent_unreachable_when_its_own_unlock_missing(self):
        for dep, _, strip in self._CHAINS:
            with self.subTest(location=dep):
                self.assertAccessDependency(
                    [dep],
                    [[strip]],
                    only_check_listed=True,
                )


class TestARChainBreaksWhenPrereqGated(KARTestBase):
    """Subset of AR chains where the prereq location lives in a *course* region. Stripping the
    course unlock makes the prereq unreachable, which must make the dependent unreachable too
    (the chain rule must compose with the dependent's own gate).

    Both starter pins live in one start_inventory dict: a naive merge of two
    `{"start_inventory": {...}}` shapes would drop the first. Pinning matters because the random
    AR-course pick could otherwise precollect a course we strip, making the assertion vacuous."""

    options = {
        **AR_ONLY,
        "air_ride_courses_gated": Toggle.option_true,
        "machines_gated": Toggle.option_true,
        "start_inventory": {
            KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1,
            KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1,
        },
    }

    # (dependent, prereq, course-unlock-of-prereq).
    _COURSE_CHAINS: list[tuple[str, str, str]] = [
        (
            ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR,
            ARLocation.TA_FH_FINISH_03_14_00,
            KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
        ),
        (
            ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
            ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00,
            KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
        ),
        (
            ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR,
            ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00,
            KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
        ),
        (
            ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR,
            ARLocation.MF_USE_ALL_VOLCANO_RAILS_AND_FIRST,
            KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
        ),
        (
            ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR,
            ARLocation.MF_USE_ALL_VOLCANO_RAILS_AND_FIRST,
            KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
        ),
        (
            ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR,
            ARLocation.MP_RACE_4500_FEET,
            KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        ),
    ]

    def test_chain_break_makes_dependent_unreachable(self):
        for dep, prereq, course_unlock in self._COURSE_CHAINS:
            with self.subTest(dependent=dep, prereq=prereq, stripped=course_unlock):
                self.assertAccessDependency(
                    [dep],
                    [[course_unlock]],
                    only_check_listed=True,
                )


class TestTRBombAbilityGating(KARTestBase):
    """abilities_gated ON: HIT_ENEMIES_3_X_WITH_BOMB_ITEMS needs UNLOCK_ABILITY_BOMB
    via _ABILITY_TR_ITEM_RULES. Companion to test_tr_fire_location_needs_fire_unlock."""

    options = {**ALL_MODES, "abilities_gated": Toggle.option_true}

    def test_tr_bomb_location_needs_bomb_unlock(self):
        self.assertAccessDependency(
            [TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS],
            [[KARItemName.UNLOCK_ABILITY_BOMB]],
            only_check_listed=True,
        )


class TestCTPrerequisiteChainsAllGatingOff(KARTestBase):
    """With every gate off, the CanReachLocation prerequisite chains
    (UNLOCK_HYDRA_CHECKLIST, UNLOCK_DRAGOON_CHECKLIST) should still be reachable:
    no item gate blocks the constituent prereq locations."""

    options = {
        **CT_ONLY,
        "city_trial_events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "city_trial_patches_gated": Toggle.option_false,
        "city_trial_items_gated": Toggle.option_false,
        "machines_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "city_trial_progressive_stadiums": Toggle.option_false,
    }

    def test_hydra_checklist_reachable(self):
        self.assertTrue(self.can_reach_location(CTLocation.UNLOCK_HYDRA_CHECKLIST))

    def test_dragoon_checklist_reachable(self):
        self.assertTrue(self.can_reach_location(CTLocation.UNLOCK_DRAGOON_CHECKLIST))
