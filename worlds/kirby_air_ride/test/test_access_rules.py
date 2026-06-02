"""
Access-rule tests for KARRules.set_rules().

Each test exercises one rule branch by asserting the rule-protected locations are unreachable
without the gating item and reachable when it is collected. only_check_listed=True keeps each
test focused on its rule without cross-checking unrelated locations.

Random starter picks are non-deterministic under default options. Where a test depends on a
specific starter not having been chosen, it pins the starter via start_inventory.
"""

from BaseClasses import CollectionState, ItemClassification
from Options import Toggle

from ..KARItems import (
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    STADIUM_UNLOCK_ITEMS,
    STADIUM_UNLOCK_TO_CHECKLIST_REWARD,
    TR_ITEM_UNLOCK_TO_CHECKLIST_REWARD,
    KARItemName,
    KARItemType,
)
from ..KARLocations import ARLocation, CTLocation, TRLocation
from ..KAROptions import CityTrialGoal, TopRideGoal
from ..KARRegions import KARRegion
from . import ALL_MODES, AR_AND_TR, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, items_of_type

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
    Covers Air Ride "finish/swallow with ability" locations, the CT Copy Chance Wheel
    locations, and the TR locations gated by ability unlocks
    (_ABILITY_TR_ITEM_RULES: Fire, Bomb, Walky)."""

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

    def test_ar_swallow_ability_enemies_need_their_unlock(self):
        # Swallowing a named copy-ability enemy needs that ability unlocked. Each location is in
        # the top-level AIR_RIDE region, so the only gate is the ability. One assertion per enemy
        # since each depends on a different ability unlock.
        for location, unlock in (
            (ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_SWORD),
            (ARLocation.SWALL_WHEELIE_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_WHEEL),
            (ARLocation.SWALL_CHILLY_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_FREEZE),
            (ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_PLASMA),
        ):
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[unlock]], only_check_listed=True)

    def test_tr_walky_location_needs_mic_unlock(self):
        # GET_20_WALKY_ITEMS is in the top-level TOP_RIDE region; the Walky item is gated by the
        # Mic copy-ability unlock rather than the TR item mask (_ABILITY_TR_ITEM_RULES).
        self.assertAccessDependency(
            [TRLocation.GET_20_WALKY_ITEMS],
            [[KARItemName.UNLOCK_ABILITY_MIC]],
            only_check_listed=True,
        )

    def test_generic_swallow_locations_ungated(self):
        # "Swallow N enemies" / "garbage enemies (no copy abilities)" take any enemy, so they carry
        # no ability rule. These two live in the top-level AIR_RIDE region (the per-course generic
        # swallow checkboxes only differ by course gating), so they are reachable with nothing
        # collected even while abilities are gated.
        for location in (
            ARLocation.SWALL_200_ENEMIES,
            ARLocation.SWALL_5_GARBAGE_AND_FIRST,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))


class TestAbilitiesGatingNotApplied(KARTestBase):
    """abilities_gated OFF: ability unlocks aren't in the pool and ability locations have no rule."""

    options = {**ALL_MODES, "abilities_gated": Toggle.option_false}

    def test_ability_locations_reachable_empty(self):
        # Gate off means no rule, so each ability-specific location is reachable with nothing collected.
        for location in (
            ARLocation.FIRST_WITH_WING_ABILITY,
            ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST,
            ARLocation.SWALL_CHILLY_3_AND_FIRST,
            TRLocation.GET_20_WALKY_ITEMS,
            TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM,
            CTLocation.COPY_CHANCE_WHEEL_BOMB,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))

    def test_ability_unlock_items_absent_from_pool(self):
        item_names = self.world_item_names()
        for unlock in (
            KARItemName.UNLOCK_ABILITY_SWORD,
            KARItemName.UNLOCK_ABILITY_WHEEL,
            KARItemName.UNLOCK_ABILITY_FREEZE,
            KARItemName.UNLOCK_ABILITY_PLASMA,
            KARItemName.UNLOCK_ABILITY_MIC,
        ):
            self.assertNotIn(unlock, item_names)


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

    def test_eat_drink_food_locations_need_their_unlock(self):
        # Each "eat/drink N <food>" checkbox needs that food spawning, which the gate locks behind its
        # unlock item. All are in the top-level CITY_TRIAL region, so the food unlock is the only gate.
        for location, unlock in (
            (CTLocation.EAT_3_PLATES_OF_SUSHI, KARItemName.UNLOCK_ITEM_SUSHI),
            (CTLocation.EAT_2_MAXIM_TOMATOES, KARItemName.UNLOCK_ITEM_MAXIM_TOMATO),
            (CTLocation.DRINK_3_ENERGY_DRINKS, KARItemName.UNLOCK_ITEM_ENERGY_DRINK),
        ):
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[unlock]], only_check_listed=True)

    def test_item_pickup_locations_need_any_counting_item_unlock(self):
        # "Get/pick up N items" cells count every collected itemkind except the three boxes, so patches,
        # copy abilities, and the food/special/hazard/legendary items ALL count toward them. With items +
        # patches + abilities all gated (the defaults here), each cell is reachable once ANY ONE of those
        # unlocks is collected and unreachable with all held back (HasAny over all three sets). Boxes are
        # deliberately not a source. patches_gated grants a random patch starter (itself a counting
        # unlock), so precollected counting unlocks are dropped from the state to exercise the rule rather
        # than that incidental starter -- the rule must hold regardless of starter items.
        pickup_locations = [
            CTLocation.GET_50_ITEMS,
            CTLocation.GET_10_ITEMS_IN_20S,
            CTLocation.PICKUP_100_ITEMS,
            CTLocation.PICKUP_500_ITEMS,
            CTLocation.PICKUP_1000_ITEMS,
            CTLocation.PICKUP_3000_ITEMS,
        ]
        counting_unlocks = (
            items_of_type(KARItemType.CT_ITEM_UNLOCK)
            | items_of_type(KARItemType.CT_PATCH_UNLOCK)
            | items_of_type(KARItemType.ABILITY_UNLOCK)
        )

        state = CollectionState(self.multiworld)
        self.collect_all_but(counting_unlocks, state)
        # Drop any precollected counting unlock (e.g. the random patch starter) so the cells are gated by
        # the rule alone, not by a starter that happens to be one of the counting types.
        for item in self.multiworld.precollected_items[self.player]:
            if item.name in counting_unlocks:
                state.remove(item)

        # Everything EXCEPT counting unlocks is now collected -- including the box unlocks. Boxes are not
        # a counting source, so the cells must still be unreachable here (this doubles as the "breaking a
        # box does not count" check).
        for location in pickup_locations:
            self.assertFalse(
                state.can_reach(location, "Location", self.player),
                f"{location} reachable with no counting-item unlock held",
            )
        # Any single counting unlock -- patch, ability, or item -- makes every cell reachable. Build via
        # create_item so the check covers unlocks that left the itempool (e.g. the precollected starter).
        for unlock in sorted(counting_unlocks):
            item = self.world.create_item(unlock)
            state.collect(item)
            for location in pickup_locations:
                self.assertTrue(
                    state.can_reach(location, "Location", self.player),
                    f"{location} not reachable with only {unlock}",
                )
            state.remove(item)


class TestCityTrialItemsGatingNotApplied(KARTestBase):
    """city_trial_items_gated OFF: item unlocks aren't in the pool and the item-count cells have no
    rule, so they are reachable with nothing collected."""

    options = {**CT_ONLY, "city_trial_items_gated": Toggle.option_false}

    def test_item_pickup_locations_reachable_empty(self):
        for location in (
            CTLocation.GET_50_ITEMS,
            CTLocation.PICKUP_100_ITEMS,
            CTLocation.PICKUP_3000_ITEMS,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))

    def test_item_unlock_items_absent_from_pool(self):
        names = self.world_item_names()
        self.assertNotIn(KARItemName.UNLOCK_ITEM_ALL_UP, names)
        self.assertNotIn(KARItemName.UNLOCK_ITEM_HOT_DOG, names)


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


class TestMachinesGatingNotApplied(KARTestBase):
    """machines_gated OFF (Air Ride enabled): machines that vanilla unlocks via an Air Ride checklist
    reward stay gated behind that (shuffled) reward, so the machine-specific cells require the reward
    instead of an Unlock Machine item. Vanilla start machines (Warp Star, Compact Star) have no reward
    and drop out of the requirement. Mirrors TestMachinesSingleGatingApplied / TestMachinesPairGatingApplied."""

    options = {**ALL_MODES, "machines_gated": Toggle.option_false}

    def test_formula_ct_location_needs_reward(self):
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR1_17_00_FORMULA],
            [[KARItemName.AR_REWARD_FORMULA_STAR]],
            only_check_listed=True,
        )

    def test_shadow_ar_location_needs_reward(self):
        self.assertAccessDependency(
            [ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR],
            [[KARItemName.AR_REWARD_SHADOW_STAR]],
            only_check_listed=True,
        )

    def test_bust_wheelie_bike_on_warpstar_needs_only_wheelie_reward(self):
        # Wheelie Bike has a reward; Warp Star is a vanilla start machine (no reward), so it drops out
        # and the reward is the sole requirement.
        self.assertAccessDependency(
            [CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR],
            [[KARItemName.AR_REWARD_WHEELIE_BIKE]],
            only_check_listed=True,
        )

    def test_bust_slick_on_formula_needs_both_rewards(self):
        # Both machines have rewards, so both rewards are required (HasAll).
        self.assertAccessDependency(
            [CTLocation.BUST_SLICK_STAR_ON_FORMULA_STAR],
            [[KARItemName.AR_REWARD_SLICK_STAR, KARItemName.AR_REWARD_FORMULA_STAR]],
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

    def test_spinner_location_needs_unlock(self):
        # "Get more than 20 Spinner items!" names a specific (mask-gated) item.
        self.assertAccessDependency(
            [TRLocation.GET_20_SPINNER_ITEMS],
            [[KARItemName.UNLOCK_TR_ITEM_SPINNER]],
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


class TestProgressiveStadiumRewardPromotion(KARTestBase):
    """progressive_stadiums ON: the six stadiums that double as checklist rewards are gated on their
    CT_REWARD_*_STADIUM item, so each such reward must be promoted to progression and placed in the
    pool, and the overlapping Unlock Stadium item must be excluded. Locks the implicit contract that
    the Has/HasAny/AtLeast stadium rules rely on (the substitution would otherwise be unsatisfiable)."""

    options = {
        **CT_ONLY,
        "city_trial_progressive_stadiums": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_overlap_rewards_present_and_progression(self):
        pool = {it.name: it for it in self.itempool_items()}
        for reward in STADIUM_UNLOCK_TO_CHECKLIST_REWARD.values():
            self.assertIn(reward, pool, f"{reward} must be in the pool when progressive stadiums is on")
            self.assertTrue(
                pool[reward].classification & ItemClassification.progression,
                f"{reward} must be progression-classified to gate its stadium",
            )

    def test_overlap_unlocks_excluded(self):
        names = self.world_item_names()
        for unlock in STADIUM_UNLOCK_TO_CHECKLIST_REWARD:
            self.assertNotIn(unlock, names, f"{unlock} should be excluded in favor of its reward item")


class TestStadiumRewardGatingProgressiveOff(KARTestBase):
    """progressive stadiums OFF: the 18 ordinary stadiums open via the vanilla roulette (no rule), but
    the six that double as checklist rewards stay gated behind their CT_REWARD_*_STADIUM item (promoted
    to progression). No Unlock Stadium items exist in this configuration."""

    options = {**CT_ONLY, "city_trial_progressive_stadiums": Toggle.option_false}

    def test_ordinary_stadium_reachable_empty(self):
        # Drag Race 1 is an ordinary (non-reward) stadium: it opens via the roulette, so its cell has
        # no gate and is reachable with nothing collected.
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_DR1_FINISH_00_24_00))

    def test_dr4_location_needs_reward(self):
        # DR4's chain prereq (DR3 finish) stays reachable since DR3 opens via the roulette, so the
        # reward is the binding constraint.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR4_FINISH_00_24_00],
            [[KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM]],
            only_check_listed=True,
        )

    def test_dd3_location_needs_reward(self):
        self.assertAccessDependency(
            [CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5],
            [[KARItemName.CT_REWARD_DESTRUCTION_DERBY_3_STADIUM]],
            only_check_listed=True,
        )


class TestBoxesGatingApplied(KARTestBase):
    """city_trial_boxes_gated ON: the break-box cells need at least one box type unlocked, since no
    boxes spawn until a box unlock is received (HasAny over the three box unlocks)."""

    options = {**CT_ONLY, "city_trial_boxes_gated": Toggle.option_true}

    def test_break_box_locations_need_any_box_unlock(self):
        self.assertAccessDependency(
            [CTLocation.BREAK_500_BOXES, CTLocation.BREAK_1000_BOXES],
            [
                [KARItemName.UNLOCK_BOX_BLUE],
                [KARItemName.UNLOCK_BOX_GREEN],
                [KARItemName.UNLOCK_BOX_RED],
            ],
            only_check_listed=True,
        )


class TestBoxesGatingNotApplied(KARTestBase):
    """city_trial_boxes_gated OFF: box unlocks aren't in the pool and the break-box cells have no rule."""

    options = {**CT_ONLY, "city_trial_boxes_gated": Toggle.option_false}

    def test_break_box_locations_reachable_empty(self):
        self.assertTrue(self.can_reach_location(CTLocation.BREAK_500_BOXES))
        self.assertTrue(self.can_reach_location(CTLocation.BREAK_1000_BOXES))

    def test_box_unlock_items_absent_from_pool(self):
        names = self.world_item_names()
        self.assertNotIn(KARItemName.UNLOCK_BOX_BLUE, names)
        self.assertNotIn(KARItemName.UNLOCK_BOX_GREEN, names)
        self.assertNotIn(KARItemName.UNLOCK_BOX_RED, names)


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


_NEBULA_REGIONS = (
    KARRegion.AR_NEBULA_BELT,
    KARRegion.AR_TA_NEBULA_BELT,
    KARRegion.AR_FR_NEBULA_BELT,
)


class TestARNebulaBeltRewardGate(KARTestBase):
    """AR course gating OFF: Nebula Belt (the secret course) is unlocked by its checklist reward, not
    by reaching the Race-100-laps checkbox (rewards are shuffled). The eight standard courses open from
    the start, but the three Nebula Belt regions stay gated behind AR_REWARD_NEBULA_BELT_COURSE. Nebula
    regions hold no AP locations, so this is pinned via region reachability."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_false}

    def test_nebula_regions_need_reward(self):
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                region = self.multiworld.get_region(region_name, self.player)
                self.assertFalse(region.can_reach(self.multiworld.state))
        self.collect_by_name(KARItemName.AR_REWARD_NEBULA_BELT_COURSE)
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                region = self.multiworld.get_region(region_name, self.player)
                self.assertTrue(region.can_reach(self.multiworld.state))


class TestARNebulaBeltUnlockGate(KARTestBase):
    """AR course gating ON: Nebula Belt is gated by its course unlock item (like every other course),
    not by the Race-100-laps checkbox. Starter pinned to Fantasy Meadows so Nebula's unlock is not
    precollected."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    def test_nebula_regions_need_unlock(self):
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                region = self.multiworld.get_region(region_name, self.player)
                self.assertFalse(region.can_reach(self.multiworld.state))
        self.collect_by_name(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT)
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                region = self.multiworld.get_region(region_name, self.player)
                self.assertTrue(region.can_reach(self.multiworld.state))


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


class TestCTLegendaryPartChecklistGating(KARTestBase):
    """The "Unlock Hydra/Dragoon Parts ... on the Checklist!" checkboxes complete in-game only
    once the player has received all three of the corresponding part reward items (each performs
    the vanilla "unlock this part on the Checklist"). The rule is intrinsic to City Trial and does
    not depend on any gating option, so this runs with default gates."""

    options = CT_ONLY

    _HYDRA_PARTS = [
        KARItemName.CT_REWARD_HYDRA_PART_X,
        KARItemName.CT_REWARD_HYDRA_PART_Y,
        KARItemName.CT_REWARD_HYDRA_PART_Z,
    ]
    _DRAGOON_PARTS = [
        KARItemName.CT_REWARD_DRAGOON_PART_A,
        KARItemName.CT_REWARD_DRAGOON_PART_B,
        KARItemName.CT_REWARD_DRAGOON_PART_C,
    ]

    def test_hydra_checklist_needs_all_three_parts(self):
        self.assertAccessDependency(
            [CTLocation.UNLOCK_HYDRA_CHECKLIST],
            [self._HYDRA_PARTS],
            only_check_listed=True,
        )

    def test_dragoon_checklist_needs_all_three_parts(self):
        self.assertAccessDependency(
            [CTLocation.UNLOCK_DRAGOON_CHECKLIST],
            [self._DRAGOON_PARTS],
            only_check_listed=True,
        )

    def test_hydra_checklist_unreachable_with_only_two_parts(self):
        # Pin that all three are required, not just any/most: hold back one part and the
        # checkbox stays unreachable even with everything else collected.
        self.collect_all_but([KARItemName.CT_REWARD_HYDRA_PART_Z])
        self.assertFalse(self.can_reach_location(CTLocation.UNLOCK_HYDRA_CHECKLIST))
        self.collect_by_name(KARItemName.CT_REWARD_HYDRA_PART_Z)
        self.assertTrue(self.can_reach_location(CTLocation.UNLOCK_HYDRA_CHECKLIST))


class TestARAllStandardCoursesGating(KARTestBase):
    """air_ride_courses_gated ON: 'Race all of the standard Air Ride courses!' completes in-game only
    once every standard course is unlocked (a locked course cannot be raced). Nebula Belt is the
    secret course and is intentionally NOT required by the 'standard' wording. Starter is pinned to a
    standard course so the secret course is never pre-collected for the exclusion test below."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    _STANDARD_COURSES = [
        KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
        KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
        KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    ]

    def test_race_all_standard_needs_every_standard_course(self):
        self.assertAccessDependency(
            [ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES],
            [self._STANDARD_COURSES],
            only_check_listed=True,
        )

    def test_unreachable_with_one_standard_course_missing(self):
        # Hold back a single standard course; the cell stays unreachable even with all else.
        self.collect_all_but([KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE])
        self.assertFalse(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))
        self.collect_by_name(KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE)
        self.assertTrue(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))

    def test_nebula_belt_not_required(self):
        # Nebula Belt is excluded from "standard": collect everything except its unlock and the
        # cell is still reachable (all eight standard courses are in hand).
        self.collect_all_but([KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT])
        self.assertTrue(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))


class TestTRAllCoursesGating(KARTestBase):
    """top_ride_courses_gated ON: every 'all courses' checkbox needs all seven Top Ride courses
    (Top Ride has no secret course)."""

    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true, **_PIN_TR_COURSE_STARTER}

    _ALL_COURSES = [
        KARItemName.UNLOCK_TR_COURSE_GRASS,
        KARItemName.UNLOCK_TR_COURSE_SAND,
        KARItemName.UNLOCK_TR_COURSE_SKY,
        KARItemName.UNLOCK_TR_COURSE_FIRE,
        KARItemName.UNLOCK_TR_COURSE_WATER,
        KARItemName.UNLOCK_TR_COURSE_LIGHT,
        KARItemName.UNLOCK_TR_COURSE_METAL,
    ]
    _ALL_COURSES_LOCATIONS: list[str] = [
        TRLocation.FIRST_ON_ALL_COURSES,
        TRLocation.ALL_COURSES_NO_BOOST,
        TRLocation.FIRST_ON_ALL_COURSES_WITHOUT_BOOST,
        TRLocation.NOITEMS_ALL_COURSES,
        TRLocation.NOITEMS_FIRST_ALL_COURSES,
    ]

    def test_all_courses_cells_need_every_course(self):
        self.assertAccessDependency(
            self._ALL_COURSES_LOCATIONS,
            [self._ALL_COURSES],
            only_check_listed=True,
        )

    def test_unreachable_with_one_course_missing(self):
        # Hold back a single course; every 'all courses' cell stays unreachable.
        self.collect_all_but([KARItemName.UNLOCK_TR_COURSE_METAL])
        for loc in self._ALL_COURSES_LOCATIONS:
            with self.subTest(location=loc):
                self.assertFalse(self.can_reach_location(loc))
        self.collect_by_name(KARItemName.UNLOCK_TR_COURSE_METAL)
        for loc in self._ALL_COURSES_LOCATIONS:
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


class TestCourseAggregatesGatingNotApplied(KARTestBase):
    """Course gating OFF: the 'all courses' checkboxes carry no rule. All courses are available from
    the start and no course-unlock items exist in the pool, so the cells are reachable empty (a
    Has()-style rule here would wrongly strand them behind items that were never created)."""

    options = {
        **ALL_MODES,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_ar_race_all_standard_reachable_empty(self):
        self.assertTrue(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))

    def test_tr_all_courses_reachable_empty(self):
        for loc in (
            TRLocation.FIRST_ON_ALL_COURSES,
            TRLocation.ALL_COURSES_NO_BOOST,
            TRLocation.FIRST_ON_ALL_COURSES_WITHOUT_BOOST,
            TRLocation.NOITEMS_ALL_COURSES,
            TRLocation.NOITEMS_FIRST_ALL_COURSES,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


class TestARRootCourseGating(KARTestBase):
    """air_ride_courses_gated ON: non-course-specific (mode-root) Air Ride cells need at least one AR
    course unlocked, since you cannot race without a course. The course starter normally satisfies this
    in the base state, so the test removes it to expose the rule. Any single course restores access,
    Nebula Belt included (holding its unlock makes it raceable directly). Starter is pinned to a known
    course so the removal below is deterministic."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    def test_root_location_needs_any_course(self):
        # SWALL_200_ENEMIES is a mode-root cell with no other gating (generic swallow).
        loc = ARLocation.SWALL_200_ENEMIES
        self.assertTrue(self.can_reach_location(loc))  # pinned starter (Fantasy Meadows) present
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.assertFalse(self.can_reach_location(loc))  # no course in state -> unreachable
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT))
        self.assertTrue(self.can_reach_location(loc))  # any course (even the secret one) restores it


class TestTRRootCourseGating(KARTestBase):
    """top_ride_courses_gated ON: non-course-specific Top Ride cells need at least one TR course. Covers
    a TOP_RIDE-root cell plus the mode-level Free Run / Time Attack cells (which live in the
    TR_FREE_RUN / TR_TIME_ATTACK regions, not a course region). Starter pinned for deterministic
    removal."""

    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true, **_PIN_TR_COURSE_STARTER}

    _ROOT_LOCATIONS = (
        TRLocation.CROSS_GOAL_20,
        TRLocation.FR_RACE_100_LAPS,
        TRLocation.TA_CROSS_GOAL_30,
    )

    def test_root_locations_need_any_course(self):
        for loc in self._ROOT_LOCATIONS:
            with self.subTest(location=loc, phase="starter present"):
                self.assertTrue(self.can_reach_location(loc))  # pinned starter (Grass) present
        self.remove([self.world.create_item(KARItemName.UNLOCK_TR_COURSE_GRASS)])
        for loc in self._ROOT_LOCATIONS:
            with self.subTest(location=loc, phase="no course"):
                self.assertFalse(self.can_reach_location(loc))
        self.collect(self.world.create_item(KARItemName.UNLOCK_TR_COURSE_METAL))
        for loc in self._ROOT_LOCATIONS:
            with self.subTest(location=loc, phase="one course"):
                self.assertTrue(self.can_reach_location(loc))


class TestRootCourseGatingNotApplied(KARTestBase):
    """Course gating OFF: mode-root cells carry no course rule (no course unlocks exist), so they are
    reachable with nothing collected."""

    options = {
        **AR_AND_TR,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_root_locations_reachable_empty(self):
        for loc in (
            ARLocation.SWALL_200_ENEMIES,
            ARLocation.RACE_100_LAPS,
            TRLocation.CROSS_GOAL_20,
            TRLocation.FR_RACE_100_LAPS,
            TRLocation.TA_CROSS_GOAL_30,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


# Every stadium mode's effective unlock item (reward item for the six that double as checklist
# rewards, own unlock item otherwise). Mirrors KARRules._EFFECTIVE_STADIUM_UNLOCKS.
_EFFECTIVE_STADIUMS: list[str] = [str(STADIUM_UNLOCK_TO_CHECKLIST_REWARD.get(u, u)) for u in STADIUM_UNLOCK_ITEMS]


class TestStadiumPlayCountGating(KARTestBase):
    """progressive stadiums ON: 'play in over 10/20 stadium modes!' need more than that many of the
    24 stadium modes unlocked (11 / 21), since a locked stadium can't be entered. The Air Glider
    starter is pinned so the precollected mode is known when counting."""

    options = {**CT_ONLY, "city_trial_progressive_stadiums": Toggle.option_true, **_PIN_STADIUM_STARTER}

    def _missing_other_than_starter(self, n: int) -> list[str]:
        return [s for s in _EFFECTIVE_STADIUMS if s != KARItemName.UNLOCK_STADIUM_AIR_GLIDER][:n]

    def test_unreachable_with_only_starter(self):
        # Only the pinned Air Glider starter is held — far short of either threshold.
        self.assertFalse(self.can_reach_location(CTLocation.STADIUM_PLAY_10_STADIUM_MODES))
        self.assertFalse(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))

    def test_play_10_needs_eleven_modes(self):
        # Hold back 14 non-starter modes -> 10 held (incl. starter) -> unreachable; one more -> 11.
        missing = self._missing_other_than_starter(14)
        self.collect_all_but(missing)
        self.assertFalse(self.can_reach_location(CTLocation.STADIUM_PLAY_10_STADIUM_MODES))
        self.collect_by_name(missing[0])
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_PLAY_10_STADIUM_MODES))

    def test_play_20_needs_twenty_one_modes(self):
        # Hold back 4 non-starter modes -> 20 held -> unreachable; one more -> 21.
        missing = self._missing_other_than_starter(4)
        self.collect_all_but(missing)
        self.assertFalse(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))
        self.collect_by_name(missing[0])
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))


class TestStadiumPlayCountProgressiveOff(KARTestBase):
    """progressive stadiums OFF: the 18 ordinary stadiums open via the vanilla roulette (always
    available), but the six that double as checklist rewards stay gated behind their reward. So 'play
    in over 10 modes!' (needs 11) is reachable from the start, while 'play in over 20 modes!' (needs 21)
    requires three of the six reward-overlap stadiums."""

    options = {**CT_ONLY, "city_trial_progressive_stadiums": Toggle.option_false}

    def test_play_10_reachable_empty(self):
        # 18 ordinary modes are always available, comfortably over the threshold of 11.
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_PLAY_10_STADIUM_MODES))

    def test_play_20_needs_three_reward_stadiums(self):
        rewards = [str(reward) for reward in STADIUM_UNLOCK_TO_CHECKLIST_REWARD.values()]
        # 18 ordinary modes < 21 -> unreachable with nothing collected.
        self.assertFalse(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))
        # Two rewards -> 20 modes -> still short.
        self.collect_by_name(rewards[0])
        self.collect_by_name(rewards[1])
        self.assertFalse(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))
        # Third reward -> 21 modes -> reachable.
        self.collect_by_name(rewards[2])
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))


_TR_ABILITY_TYPE_UNLOCKS = [
    KARItemName.UNLOCK_ABILITY_FREEZE,
    KARItemName.UNLOCK_ABILITY_FIRE,
    KARItemName.UNLOCK_ABILITY_BOMB,
    KARItemName.UNLOCK_ABILITY_MIC,
]

# city_trial_items_gated adds the ~30 CT_ITEM_UNLOCK items as progression, which overflows the 90
# default CT-only locations. Opening every CT progression-location flag raises capacity to all 120 CT
# cells so the world fills (also makes the HIGH_EFFORT cell COMPLETE_DRAGOON_AND_HYDRA a real
# placement target). Independent of the access rules under test.
_CT_ALL_PROGRESSION_LOCATIONS = {
    "city_trial_progression_high_effort": Toggle.option_true,
    "city_trial_progression_multiplayer": Toggle.option_true,
    "city_trial_progression_free_run": Toggle.option_true,
    "city_trial_progression_rng": Toggle.option_true,
    "city_trial_progression_bust_vehicles": Toggle.option_true,
}


class TestTRItemTypeCountItemGateOnly(KARTestBase):
    """top_ride_items_gated ON, abilities OFF: 'get over 18 different types of items!' needs 19 of the
    21 TR item types. The 4 ability-themed types are always available (abilities gating off), so this
    reduces to 15 of the 17 mask-gated TR item unlocks."""

    options = {
        **TR_ONLY,
        "top_ride_items_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_false,
    }

    def test_needs_fifteen_of_seventeen_item_unlocks(self):
        tr_unlocks = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK))
        # Hold back 3 -> 14 held + 4 free ability types = 18 < 19 -> unreachable.
        self.collect_all_but(tr_unlocks[:3])
        self.assertFalse(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))
        self.collect_by_name(tr_unlocks[0])  # 15th unlock -> 19 total
        self.assertTrue(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))


class TestTRItemTypeCountBothGates(KARTestBase):
    """top_ride_items_gated AND abilities_gated ON: 'get over 18 different types!' needs 19 of all 21
    types (17 item unlocks + 4 ability unlocks)."""

    options = {
        **TR_ONLY,
        "top_ride_items_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
    }

    def test_needs_nineteen_of_twenty_one_types(self):
        all_types = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK)) + _TR_ABILITY_TYPE_UNLOCKS
        # Hold back 3 -> 18 held -> unreachable; one more -> 19.
        self.collect_all_but(all_types[:3])
        self.assertFalse(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))
        self.collect_by_name(all_types[0])
        self.assertTrue(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))


class TestTRItemTypeCountNoGates(KARTestBase):
    """Both TR-item and ability gating OFF: 18 of the 21 types are vanilla defaults, but the three that
    vanilla unlocks via a checklist reward (Lantern/Who?Paint/Chickie) still need that (shuffled)
    reward. So 'get over 18 different types!' (needs 19) is unreachable until one of those three rewards
    is collected."""

    options = {
        **TR_ONLY,
        "top_ride_items_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
    }

    def test_needs_one_reward_type(self):
        rewards = [str(reward) for reward in TR_ITEM_UNLOCK_TO_CHECKLIST_REWARD.values()]
        # 18 default types < 19 -> unreachable with nothing collected.
        self.assertFalse(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))
        # Any one of the three reward-gated types -> 19 -> reachable.
        self.collect_by_name(rewards[0])
        self.assertTrue(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))


class TestTRAnyItemBothGates(KARTestBase):
    """top_ride_items_gated AND abilities_gated ON: the generic 'collect/get items' cells (which name no
    specific item) need at least one of the 21 TR item types able to spawn. Holding back every type
    unlock makes them unreachable; any single one restores them (HasAny over the 17 mask items + 4
    ability-themed types)."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_true}

    _GENERIC = [TRLocation.COLLECT_500_ITEMS, TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE]

    def test_generic_item_cells_need_any_type(self):
        all_types = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK)) + _TR_ABILITY_TYPE_UNLOCKS
        self.collect_all_but(all_types)  # everything but the 21 type unlocks (courses included)
        for loc in self._GENERIC:
            with self.subTest(location=loc, phase="no type"):
                self.assertFalse(self.can_reach_location(loc))
        self.collect_by_name(all_types[0])  # any single type
        for loc in self._GENERIC:
            with self.subTest(location=loc, phase="one type"):
                self.assertTrue(self.can_reach_location(loc))


class TestTRAnyItemOneGateOff(KARTestBase):
    """Only one of the two item-type gates on: the other gate's item types always spawn, so the generic
    'collect/get items' cells carry no HasAny rule and are reachable with nothing collected. Tested with
    items gated but abilities off (the 4 ability-themed types always spawn)."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_false}

    def test_generic_item_cells_reachable_empty(self):
        for loc in (TRLocation.COLLECT_500_ITEMS, TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


class TestCTCompleteDragoonHydraItemGating(KARTestBase):
    """city_trial_items_gated ON, non-goal: 'In one match, complete both Dragoon and Hydra!' needs
    every Hydra/Dragoon piece to spawn, gated behind the six piece-spawn unlocks. (Default CT goal is
    100_checklist, so this cell exists as a normal location here rather than the victory event.)"""

    options = {**CT_ONLY, **_CT_ALL_PROGRESSION_LOCATIONS, "city_trial_items_gated": Toggle.option_true}

    def test_needs_all_six_piece_unlocks(self):
        self.assertAccessDependency(
            [CTLocation.COMPLETE_DRAGOON_AND_HYDRA],
            [list(LEGENDARY_PIECE_UNLOCK_ITEMS)],
            only_check_listed=True,
        )

    def test_unreachable_with_one_piece_missing(self):
        self.collect_all_but([KARItemName.UNLOCK_ITEM_DRAGOON_PART_C])
        self.assertFalse(self.can_reach_location(CTLocation.COMPLETE_DRAGOON_AND_HYDRA))
        self.collect_by_name(KARItemName.UNLOCK_ITEM_DRAGOON_PART_C)
        self.assertTrue(self.can_reach_location(CTLocation.COMPLETE_DRAGOON_AND_HYDRA))


class TestCTCompleteDragoonHydraItemGatingOff(KARTestBase):
    """city_trial_items_gated OFF: pieces always spawn, so the checkbox carries no rule and is
    reachable empty (matches the historical no-gate behavior)."""

    options = {**CT_ONLY, "city_trial_items_gated": Toggle.option_false}

    def test_reachable_empty(self):
        self.assertTrue(self.can_reach_location(CTLocation.COMPLETE_DRAGOON_AND_HYDRA))


class TestCTHydraAndDragoonGoalItemGating(KARTestBase):
    """hydra_and_dragoon goal + city_trial_items_gated ON: the victory event (which replaces the
    excluded COMPLETE_DRAGOON_AND_HYDRA location) is gated on the six piece-spawn unlocks, mirroring
    the location rule for other goals."""

    options = {
        **CT_ONLY,
        **_CT_ALL_PROGRESSION_LOCATIONS,
        "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon,
        "city_trial_items_gated": Toggle.option_true,
    }

    def test_victory_event_needs_six_piece_unlocks(self):
        victory = f"{CTLocation.COMPLETE_DRAGOON_AND_HYDRA} (Victory)"
        self.assertFalse(self.can_reach_location(victory))
        for piece in LEGENDARY_PIECE_UNLOCK_ITEMS:
            self.collect_by_name(piece)
        self.assertTrue(self.can_reach_location(victory))


class TestFill100NonGoalGating(KARTestBase):
    """'Fill in over 100 Checklist blocks!' is a real in-game meta checkbox the game auto-completes
    only after the player fills over 100 of that mode's other boxes — distinct from the synthetic
    'N checklist blocks' goal. When it is NOT this mode's goal it stays a normal location and must
    carry that same requirement (100 OTHER reachable boxes), or fill could strand progression on a
    cell the player cannot reach until ~100 checks are done. Top Ride is on the N-blocks goal (so the
    cell stays a real location), with course gating holding six of seven courses behind unlocks."""

    options = {
        **TR_ONLY,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 30,
        "top_ride_checkbox_fillers": 0,
        "top_ride_courses_gated": Toggle.option_true,
        **_PIN_TR_COURSE_STARTER,
    }

    _FILL_100 = TRLocation.FILL_IN_100_CHECKLIST_BLOCKS

    def _reachable_other_tr_boxes(self) -> int:
        """Reachable Top Ride boxes excluding the FILL_100 cell itself, mirroring the count rule."""
        state = self.multiworld.state
        return sum(
            1
            for loc in self.multiworld.get_locations(self.player)
            if loc.address is not None
            and loc.parent_region is not None
            and loc.name != self._FILL_100
            and loc.parent_region.name.startswith(KARRegion.TOP_RIDE)
            and loc.can_reach(state)
        )

    def test_unreachable_at_start_below_threshold(self):
        # Six of seven courses locked: well under 100 boxes reachable, so the cell is gated off.
        # Evaluating its reachability also proves the self-excluding count rule terminates.
        self.assertLess(self._reachable_other_tr_boxes(), 100)
        self.assertFalse(self.can_reach_location(self._FILL_100))

    def test_reachable_once_enough_boxes_open(self):
        # Collect everything (sans victory events): all courses open, far over 100 boxes reachable.
        self.collect_all_but_victories()
        self.assertGreaterEqual(self._reachable_other_tr_boxes(), 100)
        self.assertTrue(self.can_reach_location(self._FILL_100))


class TestFill100AsGoalNotARealLocation(KARTestBase):
    """The flip side: when 'Fill in over 100' IS the mode's goal it is excluded from the pool (its
    victory event carries the count rule instead), so it is not a normal location at all. This pins
    that the cell-vs-goal split matches the mod, where GOAL_100_CHECKLIST keys off this same cell."""

    options = {**TR_ONLY, "top_ride_goal": TopRideGoal.option_100_checklist_blocks}

    def test_cell_excluded_when_it_is_the_goal(self):
        self.assertNotIn(TRLocation.FILL_IN_100_CHECKLIST_BLOCKS, self.real_location_names())
