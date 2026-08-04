"""
Access-rule tests for set_rules().

Each test asserts the rule-protected locations are unreachable without the gating item and reachable
when it is collected; only_check_listed=True keeps each focused on its own rule. Random starter picks
are non-deterministic, so a test that depends on one not being chosen pins it via start_inventory.
"""

from BaseClasses import CollectionState, ItemClassification
from Options import Toggle

from ..KARItems import (
    CHARACTER_MACHINE_UNLOCKS,
    DAMAGING_ABILITY_UNLOCKS,
    GATING_CATEGORIES,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    STADIUM_CHECKLIST_REWARDS,
    STADIUM_UNLOCK_ITEMS,
    KARItemName,
    KARItemType,
)
from ..KARLocations import APLocation, ARLocation, CTLocation, TRLocation
from ..KAROptions import ArchipelagoGoal, CityTrialGoal, TopRideGoal
from ..KARRegions import KARRegion
from ..KARRules import (
    _AR_COURSE_SUBSET_RULES,
    _BLUE_BOX_FOOD_ITEMS,
    _FM_20MPH_EXCLUDED_MACHINES,
    _FM_20MPH_MACHINES,
    _GREEN_BOX_ITEMS,
    _SWALLOW_ENEMY_COURSE_RULES,
    _TR_ABILITY_ITEM_KEYS,
    _TR_COURSE_SUBSET_RULES,
)
from . import ALL_MODES, AR_AND_TR, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, items_of_type

# Overlapping checklist rewards per gating option (always excluded from the pool).
_OVERLAP = {cat.option: cat.overlapping_rewards for cat in GATING_CATEGORIES}

# Pin random starter picks so they don't shadow items under test. Only categories that grant a
# random starter need pinning: stadiums, machines, AR/TR courses, and colors.
_PIN_MACHINE_STARTER = {"start_inventory": {KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1}}
_PIN_AR_COURSE_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1}}
_PIN_TR_COURSE_STARTER = {"start_inventory": {KARItemName.UNLOCK_TR_COURSE_GRASS: 1}}
_PIN_STADIUM_STARTER = {"start_inventory": {KARItemName.UNLOCK_STADIUM_AIR_GLIDER: 1}}
_PIN_COLOR_STARTER = {"start_inventory": {KARItemName.UNLOCK_COLOR_PINK: 1}}
# Beanstalk Park is the one standard Air Ride course that none of the four named swallow-enemies
# spawn on, so precollecting it disables the random AR-course starter without satisfying any swallow rule.
_PIN_BEANSTALK_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK: 1}}

# Every alternative key of a combat stadium's damage rule, as assertAccessDependency groups. The lists
# must be exhaustive: the helper collects everything NOT listed, so a missing key fails the test.
_MELEE_DAMAGE_KEYS = [
    [KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN],
    [KARItemName.UNLOCK_BASE_ABILITY_INHALE],
    *([machine] for machine in CHARACTER_MACHINE_UNLOCKS),
]
_DEDEDE_DAMAGE_KEYS = [
    [KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN],
    *([machine] for machine in CHARACTER_MACHINE_UNLOCKS),
    *([ability] for ability in DAMAGING_ABILITY_UNLOCKS),
]
_DERBY_DAMAGE_KEYS = [
    *_DEDEDE_DAMAGE_KEYS,
    # Hydra only counts alongside Charge, so it is one group rather than two.
    [KARItemName.UNLOCK_MACHINE_HYDRA, KARItemName.UNLOCK_BASE_ABILITY_CHARGE],
]


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
    """abilities_gated ON: ability-specific locations need their unlock items. Covers the Air Ride
    "finish/swallow with ability" cells and the CT Copy Chance Wheel cells; the TR ability-themed item
    cells take either key and are covered by TestTRAbilityItemEitherKey."""

    options = {**ALL_MODES, "abilities_gated": Toggle.option_true}

    def test_ar_wing_location_needs_wing_unlock(self):
        # FIRST_WITH_WING_ABILITY is in the top-level AIR_RIDE region (not course-gated).
        self.assertAccessDependency(
            [ARLocation.FIRST_WITH_WING_ABILITY],
            [[KARItemName.UNLOCK_ABILITY_WING]],
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
        # Swallowing a named copy-ability enemy needs that ability unlocked. Each location is in the
        # top-level AIR_RIDE region, so the ability is the only gate - one assertion per enemy.
        for location, unlock in (
            (ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_SWORD),
            (ARLocation.SWALL_WHEELIE_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_WHEEL),
            (ARLocation.SWALL_CHILLY_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_FREEZE),
            (ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST, KARItemName.UNLOCK_ABILITY_PLASMA),
        ):
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[unlock]], only_check_listed=True)

    def test_generic_swallow_locations_ungated(self):
        # "Swallow N enemies" / "garbage enemies" take any enemy, so they carry no ability rule and
        # are reachable with nothing collected even while abilities are gated.
        for location in (
            ARLocation.SWALL_200_ENEMIES,
            ARLocation.SWALL_5_GARBAGE_AND_FIRST,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))


class TestAbilitiesGatingNotApplied(KARTestBase):
    """abilities_gated OFF: ability unlocks aren't in the pool and ability locations have no rule.
    air_ride_courses_gated and top_ride_items_gated are also off so the swallow-named-enemy and TR
    ability-themed item cells are rule-free here, isolating the ability gate."""

    options = {
        **ALL_MODES,
        "abilities_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_items_gated": Toggle.option_false,
    }

    def test_ability_locations_reachable_empty(self):
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


class TestBaseAbilitiesGatingApplied(KARTestBase):
    """base_abilities_gated ON: swallow cells need Inhale, quick-spin cells need Quick Spin. Copy-ability
    and AR/TR course gates are OFF so those requirements don't stack, isolating the base-ability rule."""

    options = {
        **ALL_MODES,
        "base_abilities_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_swallow_locations_need_inhale(self):
        for location in (
            ARLocation.SWALL_200_ENEMIES,
            ARLocation.SWALL_5_GARBAGE_AND_FIRST,
            ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST,
            ARLocation.SWALL_CHILLY_3_AND_FIRST,
        ):
            with self.subTest(location=location):
                self.assertAccessDependency(
                    [location], [[KARItemName.UNLOCK_BASE_ABILITY_INHALE]], only_check_listed=True
                )

    def test_ar_quick_spin_locations_need_unlock(self):
        self.assertAccessDependency(
            [
                ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN,
                ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
            ],
            [[KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN]],
            only_check_listed=True,
        )

    def test_tr_quick_spin_locations_need_unlock(self):
        self.assertAccessDependency(
            [
                TRLocation.QUICK_SPIN_20_AND_FIRST,
                TRLocation.FIRST_WHILE_DOING_A_QUICK_SPIN,
            ],
            [[KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN]],
            only_check_listed=True,
        )

    def test_charge_dependent_ride_locations_need_charge(self):
        self.assertAccessDependency(
            [
                ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
                ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR,
                ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR,
                ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR,
                CTLocation.STADIUM_DR4_33_00_TURBO,
                CTLocation.BUST_ROCKET_STAR_ON_SLICK_STAR,
            ],
            [[KARItemName.UNLOCK_BASE_ABILITY_CHARGE]],
            only_check_listed=True,
        )

    def test_tr_cpu_level_5_locations_need_charge(self):
        self.assertAccessDependency(
            [
                TRLocation.GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
                TRLocation.SAND_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
                TRLocation.SKY_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
                TRLocation.FIRE_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
                TRLocation.WATER_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
                TRLocation.LIGHT_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
                TRLocation.METAL_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
            ],
            [[KARItemName.UNLOCK_BASE_ABILITY_CHARGE]],
            only_check_listed=True,
        )


class TestBaseAbilitiesGatingNotApplied(KARTestBase):
    """base_abilities_gated OFF: no base-ability unlocks in the pool and no base-ability rule on the
    swallow/quick-spin cells. Copy-ability and course gates are OFF too, so the listed cells are rule-free."""

    options = {
        **ALL_MODES,
        "base_abilities_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_base_ability_locations_reachable_empty(self):
        for location in (
            ARLocation.SWALL_200_ENEMIES,
            ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST,
            ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN,
            TRLocation.QUICK_SPIN_20_AND_FIRST,
            TRLocation.GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
            ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))

    def test_base_ability_unlock_items_absent_from_pool(self):
        item_names = self.world_item_names()
        for unlock in (
            KARItemName.UNLOCK_BASE_ABILITY_INHALE,
            KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
            KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
        ):
            self.assertNotIn(unlock, item_names)


class TestBaseAbilitiesGatingArchipelagoOnlyInhale(KARTestBase):
    """Top Ride is the only mode with a goal, so base_abilities_gated holds keys through Top Ride alone -
    but the Archipelago checklist still puts a City Trial box behind Inhale. The unlock has to be minted
    anyway, or the mod gates a move whose item never exists and the box is impossible in-game."""

    options = {
        **TR_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "base_abilities_gated": Toggle.option_true,
    }

    def test_inhale_in_pool(self):
        self.assertIn(KARItemName.UNLOCK_BASE_ABILITY_INHALE, self.world_item_names())

    def test_mic_kirby_box_needs_inhale(self):
        self.assertAccessDependency(
            [APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY],
            [[KARItemName.UNLOCK_BASE_ABILITY_INHALE]],
            only_check_listed=True,
        )


class TestCombatStadiumDamageRules(KARTestBase):
    """Machines, base abilities and copy abilities all gated: the three combat stadiums are unreachable
    until the player holds something that can KO. Stadium gating is off so the stadium unlock doesn't
    stack, and the machine starter is pinned so a random Dedede/Meta Knight pick can't satisfy the rule."""

    options = {
        **CT_ONLY,
        "machines_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
        **_PIN_MACHINE_STARTER,
    }

    def test_kirby_melee_needs_damage_source(self):
        self.assertAccessDependency(
            [
                CTLocation.STADIUM_KM1_KO_ENEMIES_50X,
                CTLocation.STADIUM_KM2_KO_ENEMIES_30X,
                CTLocation.STADIUM_KM_ALL_KO_500_ENEMIES,
            ],
            _MELEE_DAMAGE_KEYS,
            only_check_listed=True,
        )

    def test_destruction_derby_needs_damage_source(self):
        self.assertAccessDependency(
            [
                CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5,
                CTLocation.STADIUM_DD5_KO_A_RIVAL_10X,
                CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X,
            ],
            _DERBY_DAMAGE_KEYS,
            only_check_listed=True,
        )

    def test_vs_king_dedede_needs_damage_source(self):
        self.assertAccessDependency(
            [CTLocation.STADIUM_VSKD_KO_DEDEDE_1MIN],
            _DEDEDE_DAMAGE_KEYS,
            only_check_listed=True,
        )

    def test_hydra_alone_does_not_open_the_derby(self):
        # Hydra is the only machine that KOs by ramming, and it needs Charge to move at all.
        state = CollectionState(self.multiworld)
        self.collect_all_but([name for group in _DERBY_DAMAGE_KEYS for name in group], state)
        for item in self.get_items_by_name([KARItemName.UNLOCK_MACHINE_HYDRA]):
            state.collect(item)
        self.assertFalse(state.can_reach(CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5, "Location", self.player))


class TestCombatStadiumDamageRulesAbilitiesUngated(KARTestBase):
    """Copy abilities ungated hands over a damage source in the arenas that spawn copy panels, so only
    Kirby Melee - whose stages ship no ItemNode - keeps its rule."""

    options = {
        **CT_ONLY,
        "machines_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
        **_PIN_MACHINE_STARTER,
    }

    def test_derby_and_dedede_reachable_empty(self):
        for location in (
            CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5,
            CTLocation.STADIUM_VSKD_KO_DEDEDE_1MIN,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))

    def test_kirby_melee_still_needs_damage_source(self):
        self.assertAccessDependency(
            [CTLocation.STADIUM_KM1_KO_ENEMIES_50X],
            _MELEE_DAMAGE_KEYS,
            only_check_listed=True,
        )


class TestCombatStadiumDamageRulesMachinesUngated(KARTestBase):
    """Machines ungated hands over King Dedede and Meta Knight from the start, and their hammer and
    sword cover every combat stadium, so none of the three carries a rule."""

    options = {
        **CT_ONLY,
        "machines_gated": Toggle.option_false,
        "base_abilities_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_combat_stadiums_reachable_empty(self):
        for location in (
            CTLocation.STADIUM_KM1_KO_ENEMIES_50X,
            CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5,
            CTLocation.STADIUM_VSKD_KO_DEDEDE_1MIN,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))


class TestPatchesGatingApplied(KARTestBase):
    """city_trial_patches_gated ON: patch-specific locations need their unlock items.

    Patch types grant no random starter, so nothing pre-unlocks the patches under test (no pin needed)."""

    options = {**CT_ONLY, "city_trial_patches_gated": Toggle.option_true}

    def test_boost_patches_need_boost_unlock(self):
        self.assertAccessDependency(
            [CTLocation.GET_10_BOOST_PATCHES],
            [[KARItemName.UNLOCK_PATCH_BOOST]],
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
    Uses ALL_MODES because the 30 added unlock items need more default locations than CT-only provides."""

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

    def test_tac_location_needs_something_to_steal(self):
        # "Steal over 8 items from Tac" needs some item type able to spawn for Tac to carry off - any CT
        # item unlock except All Up, whose city fall chance is zero. The event gate is on by default, so
        # collect_all_but leaves the Tac event unlock held and isolates the item rule.
        item_unlocks = items_of_type(KARItemType.CT_ITEM_UNLOCK)
        stealable = sorted(item_unlocks - {KARItemName.UNLOCK_ITEM_ALL_UP})

        state = CollectionState(self.multiworld)
        self.collect_all_but(item_unlocks, state)
        for item in self.multiworld.precollected_items[self.player]:
            if item.name in item_unlocks:
                state.remove(item)

        self.assertFalse(
            state.can_reach(CTLocation.STEAL_8_FROM_TAC, "Location", self.player),
            "reachable with no item unlock held",
        )

        # All Up never spawns in the city on its own, so it alone must not open the cell.
        all_up = self.world.create_item(KARItemName.UNLOCK_ITEM_ALL_UP)
        state.collect(all_up)
        self.assertFalse(
            state.can_reach(CTLocation.STEAL_8_FROM_TAC, "Location", self.player),
            "reachable with only All Up held",
        )
        state.remove(all_up)

        # Any other single item unlock is enough.
        for unlock in stealable:
            item = self.world.create_item(unlock)
            state.collect(item)
            self.assertTrue(
                state.can_reach(CTLocation.STEAL_8_FROM_TAC, "Location", self.player),
                f"not reachable with only {unlock}",
            )
            state.remove(item)

    def test_item_pickup_locations_need_any_counting_item_unlock(self):
        # "Get/pick up N items" cells count every itemkind except the three boxes, so with items, patches
        # and abilities all gated, one unlock from any of the three sets suffices and none leaves the cell
        # unreachable. Boxes are deliberately not a source.
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
        # Drop any precollected counting unlock so the cells are gated by the rule alone.
        for item in self.multiworld.precollected_items[self.player]:
            if item.name in counting_unlocks:
                state.remove(item)

        # Everything except counting unlocks is now collected, including box unlocks. Boxes are not a
        # counting source, so the cells stay unreachable (doubles as the "breaking a box does not count" check).
        for location in pickup_locations:
            self.assertFalse(
                state.can_reach(location, "Location", self.player),
                f"{location} reachable with no counting-item unlock held",
            )
        # Any single counting unlock makes every cell reachable. Build via create_item so the check
        # covers unlocks that left the itempool (e.g. the precollected starter).
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

    def test_tac_location_carries_no_item_rule(self):
        # Every item type spawns with the gate off, so Tac always has loot and the cell keeps only its
        # event rule (that gate is on by default here). The event unlock alone must open it.
        self.assertFalse(self.can_reach_location(CTLocation.STEAL_8_FROM_TAC))
        self.collect_by_name(KARItemName.UNLOCK_EVENT_TAC)
        self.assertTrue(self.can_reach_location(CTLocation.STEAL_8_FROM_TAC))

    def test_item_unlock_items_absent_from_pool(self):
        names = self.world_item_names()
        self.assertNotIn(KARItemName.UNLOCK_ITEM_ALL_UP, names)
        self.assertNotIn(KARItemName.UNLOCK_ITEM_HOT_DOG, names)


class TestCTTacNeedsEventAndLoot(KARTestBase):
    """Events + items gated: the Tac cell composes both rules -- Tac has to show up AND have something to
    steal. Either key alone leaves it unreachable. ALL_MODES because the ~30 item unlocks the item gate
    adds need more default locations than CT-only provides."""

    options = {
        **ALL_MODES,
        "city_trial_events_gated": Toggle.option_true,
        "city_trial_items_gated": Toggle.option_true,
    }

    def test_needs_both_the_event_and_an_item(self):
        keys = items_of_type(KARItemType.CT_ITEM_UNLOCK) | {KARItemName.UNLOCK_EVENT_TAC}
        state = CollectionState(self.multiworld)
        self.collect_all_but(keys, state)
        for item in self.multiworld.precollected_items[self.player]:
            if item.name in keys:
                state.remove(item)

        loc = CTLocation.STEAL_8_FROM_TAC
        self.assertFalse(state.can_reach(loc, "Location", self.player), "reachable with neither key")

        event = self.world.create_item(KARItemName.UNLOCK_EVENT_TAC)
        state.collect(event)
        self.assertFalse(state.can_reach(loc, "Location", self.player), "reachable with the event but no loot")
        state.remove(event)

        loot = self.world.create_item(KARItemName.UNLOCK_ITEM_APPLE)
        state.collect(loot)
        self.assertFalse(state.can_reach(loc, "Location", self.player), "reachable with loot but no event")

        state.collect(self.world.create_item(KARItemName.UNLOCK_EVENT_TAC))
        self.assertTrue(state.can_reach(loc, "Location", self.player), "not reachable with both keys")


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
    """machines_gated OFF: the mod unlocks every machine at connect whatever the enabled modes, so the
    machine-specific finish/bust cells carry no rule and the AR machine rewards leave the pool. Stadiums
    ungated so the named stadiums are open and the machine question is isolated."""

    options = {
        **ALL_MODES,
        "machines_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_machine_reward_items_excluded(self):
        names = self.world_item_names()
        for reward in (
            KARItemName.AR_REWARD_FORMULA_STAR,
            KARItemName.AR_REWARD_SHADOW_STAR,
            KARItemName.AR_REWARD_WHEELIE_BIKE,
            KARItemName.AR_REWARD_SLICK_STAR,
        ):
            self.assertNotIn(reward, names, f"{reward} should be excluded when machines_gated is off")

    def test_machine_cells_reachable_without_reward(self):
        # CT stadium + bust cells that name a machine carry no machine rule (the named machines are
        # unlocked at connect), so they are reachable with nothing collected.
        for loc in (
            CTLocation.STADIUM_DR1_17_00_FORMULA,
            CTLocation.STADIUM_DR2_27_00_WAGON,
            CTLocation.BUST_SLICK_STAR_ON_FORMULA_STAR,
            CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


class TestCTOnlyMachinesGatingNotApplied(KARTestBase):
    """City-Trial-only + machines_gated OFF (edge case): with AR disabled there are no machine reward
    items and no Unlock Machine items, yet the mod still unlocks every machine at connect, so the CT
    machine cells carry no rule and nothing is stranded. Stadiums ungated to isolate the question."""

    options = {
        **CT_ONLY,
        "machines_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_no_machine_unlock_or_reward_items(self):
        names = self.world_item_names()
        self.assertEqual(sorted(n for n in names if n in items_of_type(KARItemType.MACHINE_UNLOCK)), [])
        for reward in _OVERLAP["machines_gated"]:
            self.assertNotIn(reward, names, f"{reward} (machine overlap reward) must be absent")

    def test_machine_cells_reachable_without_gate(self):
        for loc in (
            CTLocation.STADIUM_DR1_17_00_FORMULA,
            CTLocation.STADIUM_DR2_27_00_WAGON,
            CTLocation.BUST_SLICK_STAR_ON_FORMULA_STAR,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


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
        # "Get more than 20 Spinner items!" names a specific mask-gated item.
        self.assertAccessDependency(
            [TRLocation.GET_20_SPINNER_ITEMS],
            [[KARItemName.UNLOCK_TR_ITEM_SPINNER]],
            only_check_listed=True,
        )


class TestProgressiveStadiumGating(KARTestBase):
    """progressive_stadiums ON: each stadium region requires its unlock item.
    Pin starter to Air Glider so other stadiums remain locked."""

    options = {
        **CT_ONLY,
        "city_trial_stadiums_gated": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_dr1_stadium_location_needs_dr1_unlock(self):
        # DRAG_RACE_1 has no checklist-reward overlap, so the unlock item gates it directly.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR1_FINISH_00_24_00],
            [[KARItemName.UNLOCK_STADIUM_DRAG_RACE_1]],
            only_check_listed=True,
        )

    def test_dr4_stadium_location_needs_dr4_unlock(self):
        # DRAG_RACE_4 gates on its own Unlock Stadium item like every other stadium, even though vanilla
        # hands it out as a checklist reward.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DR4_FINISH_00_24_00],
            [[KARItemName.UNLOCK_STADIUM_DRAG_RACE_4]],
            only_check_listed=True,
        )


class TestProgressiveStadiumAllGroupGating(KARTestBase):
    """STADIUM_DD_ALL and STADIUM_KM_ALL are reachable via ANY of their sub-stadium unlocks
    (HasAny rule). Pin starter so neither DD nor KM unlocks are pre-collected."""

    options = {
        **CT_ONLY,
        "city_trial_stadiums_gated": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_dd_all_reachable_via_any_dd_unlock(self):
        # Every DD stadium gates on its own Unlock Stadium item. The HasAny rule accepts any of these
        # five, so all five must be listed.
        self.assertAccessDependency(
            [CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X],
            [
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1],
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2],
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3],
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4],
                [KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5],
            ],
            only_check_listed=True,
        )

    def test_km_all_reachable_via_any_km_unlock(self):
        # Either Kirby Melee unlock opens the KM (All) cell, so both must be listed.
        self.assertAccessDependency(
            [CTLocation.STADIUM_KM_ALL_KO_500_ENEMIES],
            [
                [KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1],
                [KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2],
            ],
            only_check_listed=True,
        )


class TestStadiumNeedsOnlyOwnUnlock(KARTestBase):
    """Regression: the five stadiums vanilla hands out as checklist rewards need only their own Unlock
    Stadium item, not their vanilla predecessor's. They used to sit behind a DD3<-DD2 / DR4<-DR3 /
    KM2<-KM1 style chain, which the mod does not reproduce - stadium availability comes from the AP
    unlock mask, never from completing the box. Same class of stale rule as the AR machine chains."""

    options = {
        **CT_ONLY,
        "city_trial_stadiums_gated": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    # (location, its own stadium unlock, the predecessor unlock it must NOT need).
    _CHAIN_STADIUMS: list[tuple[str, str, str]] = [
        (
            CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5,
            KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3,
            KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2,
        ),
        (
            CTLocation.STADIUM_DD4_KO_YOUR_RIVALS_5,
            KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4,
            KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3,
        ),
        (
            CTLocation.STADIUM_DD5_KO_YOUR_RIVALS_5,
            KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5,
            KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4,
        ),
        (
            CTLocation.STADIUM_DR4_FINISH_00_24_00,
            KARItemName.UNLOCK_STADIUM_DRAG_RACE_4,
            KARItemName.UNLOCK_STADIUM_DRAG_RACE_3,
        ),
        (
            CTLocation.STADIUM_KM2_KO_ENEMIES_30X,
            KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2,
            KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1,
        ),
    ]

    def test_reachable_on_own_unlock_alone(self):
        for loc, own_unlock, predecessor in self._CHAIN_STADIUMS:
            with self.subTest(location=loc, withheld=predecessor):
                state = CollectionState(self.multiworld)
                state.collect(self.get_item_by_name(own_unlock), prevent_sweep=True)
                self.assertFalse(
                    state.has(predecessor, self.player),
                    f"{predecessor} leaked into the state, making this subtest vacuous",
                )
                self.assertTrue(
                    state.can_reach(loc, "Location", self.player),
                    f"{loc} should be reachable on {own_unlock} alone",
                )

    def test_unreachable_without_own_unlock(self):
        # Guard against the above passing for the wrong reason.
        for loc, own_unlock, _ in self._CHAIN_STADIUMS:
            with self.subTest(location=loc, stripped=own_unlock):
                self.assertAccessDependency(
                    [loc],
                    [[own_unlock]],
                    only_check_listed=True,
                )


class TestStadiumGatingUsesUnlockItems(KARTestBase):
    """Stadiums gated: every stadium, including the six vanilla unlocks via a checklist reward, is gated
    by its own Unlock Stadium item. So all 24 are obtainable and progression-classified, while the
    overlapping stadium checklist rewards leave the pool - they gate nothing."""

    options = {
        **CT_ONLY,
        "city_trial_stadiums_gated": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_stadium_unlocks_obtainable_and_progression(self):
        names = self.world_item_names()
        pool = {it.name: it for it in self.itempool_items()}
        for unlock in items_of_type(KARItemType.CT_STADIUM_UNLOCK):
            self.assertIn(unlock, names, f"{unlock} must be obtainable when stadiums are gated")
            if unlock in pool:
                self.assertTrue(
                    pool[unlock].classification & ItemClassification.progression,
                    f"{unlock} must be progression-classified to gate its stadium",
                )

    def test_overlap_rewards_excluded(self):
        names = self.world_item_names()
        for reward in STADIUM_CHECKLIST_REWARDS:
            self.assertNotIn(reward, names, f"{reward} should be excluded (stadium gated by its unlock item)")


class TestStadiumUngatedReachable(KARTestBase):
    """Stadiums ungated: the mod unlocks all 24 stadiums at connect, so every stadium cell - including the
    six that double as checklist rewards - is reachable from the start, no Unlock Stadium items exist, and
    the six stadium reward items are excluded from the pool."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_false}

    def test_ordinary_stadium_reachable_empty(self):
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_DR1_FINISH_00_24_00))

    def test_reward_overlap_stadium_cells_reachable_empty(self):
        # DR4 / DD3 are reward-overlap stadiums; they open from the start like every other stadium.
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_DR4_FINISH_00_24_00))
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5))

    def test_stadium_rewards_excluded(self):
        names = self.world_item_names()
        for reward in STADIUM_CHECKLIST_REWARDS:
            self.assertNotIn(reward, names, f"{reward} should be excluded when stadiums are ungated")


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


# The enemy -> spawn-course map under test is the production table itself, reused here so the wiring
# tests can't drift from it. Beanstalk Park and Nebula Belt are in no enemy's set.
_ALL_AR_COURSE_UNLOCKS = frozenset(items_of_type(KARItemType.AR_COURSE_UNLOCK))


class TestARSwallowEnemyCourseGatingApplied(KARTestBase):
    """air_ride_courses_gated ON: a "swallow a named copy-ability enemy" cell needs one of the courses
    that enemy actually spawns on, not merely the ability - these cells live in the generic Air Ride
    region and would otherwise be reachable with no course unlocked. abilities_gated is OFF so the course
    HasAny is the only gate under test, and Beanstalk Park is pinned as the starter: the one standard
    course none of these enemies spawn on, so it suppresses the random pick without satisfying a rule."""

    options = {
        **AR_ONLY,
        "abilities_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_true,
        **_PIN_BEANSTALK_STARTER,
    }

    def test_unreachable_with_all_courses_held_back(self):
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
        for location in _SWALLOW_ENEMY_COURSE_RULES:
            with self.subTest(location=location):
                self.assertFalse(
                    state.can_reach(location, "Location", self.player),
                    f"{location} reachable with no spawn course held",
                )

    def test_each_spawn_course_independently_satisfies(self):
        for location, courses in _SWALLOW_ENEMY_COURSE_RULES.items():
            for course in courses:
                with self.subTest(location=location, course=course):
                    state = CollectionState(self.multiworld)
                    self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
                    state.collect(self.world.create_item(course))
                    self.assertTrue(
                        state.can_reach(location, "Location", self.player),
                        f"{location} not reachable with only {course}",
                    )

    def test_non_spawn_courses_do_not_satisfy(self):
        # Collecting EVERY course the enemy does not spawn on must still leave the cell unreachable, which
        # pins the spawn-course set exactly: a wrongly omitted course would make it reachable here.
        for location, courses in _SWALLOW_ENEMY_COURSE_RULES.items():
            non_spawn = sorted(_ALL_AR_COURSE_UNLOCKS - set(courses))
            with self.subTest(location=location):
                state = CollectionState(self.multiworld)
                self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
                for course in non_spawn:
                    state.collect(self.world.create_item(course))
                self.assertFalse(
                    state.can_reach(location, "Location", self.player),
                    f"{location} reachable with only non-spawn courses {non_spawn}",
                )


class TestARSwallowEnemyAbilityAndCourseGating(KARTestBase):
    """abilities_gated AND air_ride_courses_gated both ON: a swallow-named-enemy cell needs BOTH the
    copy-ability unlock AND a course the enemy spawns on. Verifies the two rules compose with AND."""

    options = {
        **AR_ONLY,
        "abilities_gated": Toggle.option_true,
        "air_ride_courses_gated": Toggle.option_true,
        **_PIN_BEANSTALK_STARTER,
    }

    def test_needs_both_ability_and_a_spawn_course(self):
        location = ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST
        ability = KARItemName.UNLOCK_ABILITY_SWORD
        course = KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS  # one of Sword Knight's spawn courses

        base = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_AR_COURSE_UNLOCKS | {ability}, base)

        def reachable(*items: str) -> bool:
            state = base.copy()
            for name in items:
                state.collect(self.world.create_item(name))
            return state.can_reach(location, "Location", self.player)

        self.assertFalse(reachable(), "reachable with neither ability nor course")
        self.assertFalse(reachable(course), "reachable with course but no ability")
        self.assertFalse(reachable(ability), "reachable with ability but no course")
        self.assertTrue(reachable(course, ability), "not reachable with both ability and course")


_CLIFF_COURSES = frozenset(
    {
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    }
)


class TestARDropFromCliffsCourseGating(KARTestBase):
    """air_ride_courses_gated ON: "drop from the cliffs 3 times" only completes on Celestial Valley or
    Beanstalk Park, the only courses with a cliff that drops you. Without its rule the blanket "any
    course" rule would call it reachable on any one. Starter pinned to Fantasy Meadows, neither of them."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    def test_rule_table_lists_exactly_the_cliff_courses(self):
        self.assertEqual(
            frozenset(_AR_COURSE_SUBSET_RULES[ARLocation.DROP_FROM_CLIFFS_3X]),
            _CLIFF_COURSES,
        )

    def test_each_cliff_course_independently_satisfies(self):
        for course in _CLIFF_COURSES:
            with self.subTest(course=course):
                state = CollectionState(self.multiworld)
                self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
                state.collect(self.world.create_item(course))
                self.assertTrue(
                    state.can_reach(ARLocation.DROP_FROM_CLIFFS_3X, "Location", self.player),
                    f"not reachable with only {course}",
                )

    def test_non_cliff_courses_do_not_satisfy(self):
        # Every course without a cliff, collected together, must still leave the cell unreachable.
        non_cliff = sorted(_ALL_AR_COURSE_UNLOCKS - _CLIFF_COURSES)
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
        for course in non_cliff:
            state.collect(self.world.create_item(course))
        self.assertFalse(
            state.can_reach(ARLocation.DROP_FROM_CLIFFS_3X, "Location", self.player),
            f"reachable with only non-cliff courses {non_cliff}",
        )


_AIR_FINISH_COURSES = frozenset(
    {
        KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
        KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    }
)
# Checker Knights is one of the three cut courses, so pinning it disables the random AR-course starter
# without satisfying the air-finish rule.
_PIN_AR_CHECKER_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS: 1}}


class TestARAirFinishCourseGating(KARTestBase):
    """air_ride_courses_gated ON: "finish 1st while flying through the air" needs a course with something
    to launch off near the finish. Checker Knights, Frozen Hillside and Magma Flows are out; without its
    rule the blanket "any course" rule would call it reachable on any of the three. Starter pinned to
    Checker Knights, which is one of them."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_CHECKER_STARTER}

    def test_rule_table_lists_exactly_the_air_finish_courses(self):
        self.assertEqual(
            frozenset(_AR_COURSE_SUBSET_RULES[ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR]),
            _AIR_FINISH_COURSES,
        )

    def test_each_air_finish_course_independently_satisfies(self):
        for course in _AIR_FINISH_COURSES:
            with self.subTest(course=course):
                state = CollectionState(self.multiworld)
                self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
                state.collect(self.world.create_item(course))
                self.assertTrue(
                    state.can_reach(ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR, "Location", self.player),
                    f"not reachable with only {course}",
                )

    def test_cut_courses_do_not_satisfy(self):
        # Checker Knights, Frozen Hillside and Magma Flows together must still leave the cell unreachable.
        cut = sorted(_ALL_AR_COURSE_UNLOCKS - _AIR_FINISH_COURSES)
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
        for course in cut:
            state.collect(self.world.create_item(course))
        self.assertFalse(
            state.can_reach(ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR, "Location", self.player),
            f"reachable with only the cut courses {cut}",
        )


class TestARAirFinishGatingNotApplied(KARTestBase):
    """AR course gating OFF: all nine courses unlock at connect, so the air-finish cell needs no rule."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_false}

    def test_reachable_with_no_courses(self):
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
        self.assertTrue(state.can_reach(ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR, "Location", self.player))


class TestARDropFromCliffsGatingNotApplied(KARTestBase):
    """AR course gating OFF: all nine courses unlock at connect, so the cliff cell needs no rule."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_false}

    def test_reachable_with_no_courses(self):
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_AR_COURSE_UNLOCKS, state)
        self.assertTrue(state.can_reach(ARLocation.DROP_FROM_CLIFFS_3X, "Location", self.player))


_NEBULA_REGIONS = (
    KARRegion.AR_NEBULA_BELT,
    KARRegion.AR_TA_NEBULA_BELT,
    KARRegion.AR_FR_NEBULA_BELT,
)


class TestARNebulaBeltGatingNotApplied(KARTestBase):
    """AR course gating OFF: the mod unlocks all nine courses at connect, so the three Nebula Belt
    regions are reachable from the start and the Nebula reward is excluded from the pool. Nebula
    regions hold no AP locations, so this is checked via region reachability."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_false}

    def test_nebula_regions_reachable_empty(self):
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                region = self.multiworld.get_region(region_name, self.player)
                self.assertTrue(region.can_reach(self.multiworld.state))

    def test_nebula_reward_excluded(self):
        self.assertNotIn(KARItemName.AR_REWARD_NEBULA_BELT_COURSE, self.world_item_names())


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


class TestARMachineCellPrereqs(KARTestBase):
    """Sanity that a machine-specific AR location is gated by its own machine unlock under
    collect_all_but."""

    options = {
        **AR_ONLY,
        "air_ride_courses_gated": Toggle.option_true,
        "machines_gated": Toggle.option_true,
        "start_inventory": {
            KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1,
            KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1,
        },
    }

    # (location, its machine unlock).
    _MACHINE_CELLS: list[tuple[str, str]] = [
        (
            ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR,
            KARItemName.UNLOCK_MACHINE_SHADOW_STAR,
        ),
    ]

    def test_location_unreachable_when_its_own_unlock_missing(self):
        for loc, strip in self._MACHINE_CELLS:
            with self.subTest(location=loc):
                self.assertAccessDependency(
                    [loc],
                    [[strip]],
                    only_check_listed=True,
                )


class TestARMachineCellNeedsOnlyOwnCourse(KARTestBase):
    """Regression: a machine-specific AR cell needs its machine and its OWN course, nothing else. It used
    to chain onto the box that awards the machine in vanilla - which the mod does not reproduce - and
    where that box lived in another course's region the chain silently demanded that course too. The
    reported case was Swerve Star's Machine Passage cell held behind Sky Sands.

    Both starter pins live in one start_inventory dict (a naive merge of two would drop one). Pinning
    matters because a random AR-course / machine pick could precollect something a subtest withholds,
    making it vacuous. Nebula Belt is pinned because no cell below names it: it suppresses the random
    pick while being neither an own-course nor a withheld course."""

    options = {
        **AR_ONLY,
        "air_ride_courses_gated": Toggle.option_true,
        "machines_gated": Toggle.option_true,
        "start_inventory": {
            KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT: 1,
            KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1,
        },
    }

    # (location, its machine unlock, its own course unlock, a course it must NOT need -- the one whose
    # region holds the box that awards that machine in vanilla).
    _MACHINE_CELLS: list[tuple[str, str, str, str]] = [
        (
            ARLocation.FR_MP_LAP_00_57_00_ON_SWERVE_STAR,
            KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
            KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
            KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        ),
        (
            ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR,
            KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
            KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
            # Formula Star's vanilla box is TA_FH_FINISH_03_14_00, same course, so there is no
            # foreign course to withhold; re-use its own as a no-op third entry.
            KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
        ),
        (
            ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
            KARItemName.UNLOCK_MACHINE_SLICK_STAR,
            KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
            KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
        ),
        (
            ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR,
            KARItemName.UNLOCK_MACHINE_SLICK_STAR,
            KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
            KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
        ),
        (
            ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR,
            KARItemName.UNLOCK_MACHINE_TURBO_STAR,
            KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
            KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
        ),
        (
            ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR,
            KARItemName.UNLOCK_MACHINE_JET_STAR,
            KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
            KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        ),
        (
            ARLocation.TA_BP_FINISH_03_00_00_ON_ROCKET_STAR,
            KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
            KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
            KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        ),
        (
            ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR,
            KARItemName.UNLOCK_MACHINE_BULK_STAR,
            KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
            KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        ),
    ]

    def test_reachable_on_machine_plus_own_course_alone(self):
        for loc, machine, own_course, foreign_course in self._MACHINE_CELLS:
            with self.subTest(location=loc, withheld=foreign_course):
                state = CollectionState(self.multiworld)
                for name in (machine, own_course):
                    state.collect(self.get_item_by_name(name), prevent_sweep=True)
                # Non-vacuity: the course the removed chain used to drag in must still be missing.
                if foreign_course != own_course:
                    self.assertFalse(
                        state.has(foreign_course, self.player),
                        f"{foreign_course} leaked into the state, making this subtest vacuous",
                    )
                self.assertTrue(
                    state.can_reach(loc, "Location", self.player),
                    f"{loc} should be reachable on {machine} + {own_course} alone",
                )

    def test_unreachable_without_machine(self):
        # Guard against the above passing for the wrong reason: with the course but no machine, no.
        for loc, machine, own_course, _ in self._MACHINE_CELLS:
            with self.subTest(location=loc, stripped=machine):
                state = CollectionState(self.multiworld)
                state.collect(self.get_item_by_name(own_course), prevent_sweep=True)
                self.assertFalse(
                    state.can_reach(loc, "Location", self.player),
                    f"{loc} should need {machine}",
                )


class TestFantasyMeadows20MphNeedsCapableMachine(KARTestBase):
    """The FANTASY MEADOWS 20 mph cell names no machine, so it used to carry no machine rule at all --
    a seed could hand out only Rocket Star and leave it unwinnable. It polls speed every frame, so it
    needs a machine that both caps above the floor and can corner without stopping."""

    # Pinning the starter machine matters: a random pick could hand out a capable machine and make the
    # negative test vacuous. Rocket Star is both the pin and part of the excluded set under test.
    options = {
        **AR_ONLY,
        "air_ride_courses_gated": Toggle.option_true,
        "machines_gated": Toggle.option_true,
        "start_inventory": {
            KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1,
            KARItemName.UNLOCK_MACHINE_ROCKET_STAR: 1,
        },
    }

    def test_unreachable_on_excluded_machines_alone(self):
        # Every excluded machine at once still is not enough - this is not just "some machine".
        state = CollectionState(self.multiworld)
        for name in sorted(_FM_20MPH_EXCLUDED_MACHINES):
            if not state.has(name, self.player):  # the pinned starter is already in
                state.collect(self.get_item_by_name(name), prevent_sweep=True)
        self.assertTrue(
            state.has(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS, self.player),
            "the course pin did not land, making this test vacuous",
        )
        for name in _FM_20MPH_MACHINES:
            self.assertFalse(
                state.has(name, self.player),
                f"{name} leaked into the state, making this test vacuous",
            )
        self.assertFalse(
            state.can_reach(ARLocation.FM_LAP_ABOVE_20_MPH, "Location", self.player),
            "the 20 mph cell should not be reachable on the excluded machines",
        )

    def test_reachable_on_each_capable_machine(self):
        for machine in _FM_20MPH_MACHINES:
            with self.subTest(machine=machine):
                state = CollectionState(self.multiworld)
                state.collect(self.get_item_by_name(machine), prevent_sweep=True)
                self.assertTrue(
                    state.can_reach(ARLocation.FM_LAP_ABOVE_20_MPH, "Location", self.player),
                    f"the 20 mph cell should be reachable on {machine} alone",
                )

    def test_excluded_machines_are_air_ride_machines(self):
        # Guards against a typo'd or Top-Ride-only name silently excluding nothing.
        ar_machines = set(_FM_20MPH_MACHINES) | _FM_20MPH_EXCLUDED_MACHINES
        for name in _FM_20MPH_EXCLUDED_MACHINES:
            self.assertIn(name, ar_machines)
        self.assertEqual(len(_FM_20MPH_EXCLUDED_MACHINES), 4)


class TestTRAbilityItemEitherKey(KARTestBase):
    """Both gates ON: the four ability-themed TR items (Freeze Fan, Fire, Bomb, Walky) accept either
    key -- their own TR item unlock or the matching copy ability unlock -- so the cells that need one
    of those items spawning are reachable with either alone and unreachable with neither."""

    options = {**ALL_MODES, "abilities_gated": Toggle.option_true, "top_ride_items_gated": Toggle.option_true}

    _EITHER_KEY = (
        (
            TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM,
            KARItemName.UNLOCK_TR_ITEM_FIRE,
            KARItemName.UNLOCK_ABILITY_FIRE,
        ),
        (
            TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS,
            KARItemName.UNLOCK_TR_ITEM_BOMB,
            KARItemName.UNLOCK_ABILITY_BOMB,
        ),
        (
            TRLocation.GET_20_WALKY_ITEMS,
            KARItemName.UNLOCK_TR_ITEM_WALKY,
            KARItemName.UNLOCK_ABILITY_MIC,
        ),
    )

    def test_either_key_alone_suffices(self):
        # Two single-item groups: unreachable with neither key, reachable with each on its own.
        for location, tr_item, ability in self._EITHER_KEY:
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[tr_item], [ability]], only_check_listed=True)


class TestTRAbilityItemAbilitiesUngated(KARTestBase):
    """top_ride_items_gated ON, abilities OFF: the copy ability key is handed out at connect, so the
    mod ignores it and the TR item unlock is the only key for the four ability-themed items."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_false}

    def test_tr_bomb_location_needs_tr_item_unlock(self):
        self.assertAccessDependency(
            [TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS],
            [[KARItemName.UNLOCK_TR_ITEM_BOMB]],
            only_check_listed=True,
        )


class TestCTLegendaryPartChecklistGating(KARTestBase):
    """The "Unlock Hydra/Dragoon Parts ... on the Checklist!" checkboxes complete in-game only once the
    player has received all three corresponding part reward items. The rule is intrinsic to City Trial
    and does not depend on any gating option, so this runs with default gates."""

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
        # All three are required, not just most: hold back one part and the checkbox stays unreachable.
        self.collect_all_but([KARItemName.CT_REWARD_HYDRA_PART_Z])
        self.assertFalse(self.can_reach_location(CTLocation.UNLOCK_HYDRA_CHECKLIST))
        self.collect_by_name(KARItemName.CT_REWARD_HYDRA_PART_Z)
        self.assertTrue(self.can_reach_location(CTLocation.UNLOCK_HYDRA_CHECKLIST))


class TestARAllStandardCoursesGating(KARTestBase):
    """air_ride_courses_gated ON: 'Race all of the standard Air Ride courses!' completes only once every
    standard course is unlocked. Nebula Belt is the secret course and is intentionally NOT required by
    the 'standard' wording. Starter pinned to a standard course so the secret one is never precollected."""

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
        # Hold back a single standard course; the cell stays unreachable.
        self.collect_all_but([KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE])
        self.assertFalse(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))
        self.collect_by_name(KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE)
        self.assertTrue(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))

    def test_nebula_belt_not_required(self):
        # Nebula Belt is excluded from "standard": collect everything except its unlock and the
        # cell is still reachable (all eight standard courses are in hand).
        self.collect_all_but([KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT])
        self.assertTrue(self.can_reach_location(ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES))


class TestAPEveryColorGating(KARTestBase):
    """colors_gated ON: the Archipelago 'Finish a race as every Kirby color' box needs all eight colors -
    the mod counts one finished Air Ride race per color, and a locked color can never be raced as. The
    color starter is pinned to Pink so the random pick cannot shadow another color."""

    options = {
        **AR_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "colors_gated": Toggle.option_true,
        **_PIN_COLOR_STARTER,
    }

    _ALL_COLORS = [
        KARItemName.UNLOCK_COLOR_PINK,
        KARItemName.UNLOCK_COLOR_YELLOW,
        KARItemName.UNLOCK_COLOR_BLUE,
        KARItemName.UNLOCK_COLOR_RED,
        KARItemName.UNLOCK_COLOR_GREEN,
        KARItemName.UNLOCK_COLOR_PURPLE,
        KARItemName.UNLOCK_COLOR_BROWN,
        KARItemName.UNLOCK_COLOR_WHITE,
    ]

    def test_needs_every_color(self):
        self.assertAccessDependency(
            [APLocation.AIR_RIDE_RACE_AS_EVERY_COLOR],
            [self._ALL_COLORS],
            only_check_listed=True,
        )

    def test_unreachable_with_one_color_missing(self):
        self.collect_all_but([KARItemName.UNLOCK_COLOR_WHITE])
        self.assertFalse(self.can_reach_location(APLocation.AIR_RIDE_RACE_AS_EVERY_COLOR))
        self.collect_by_name(KARItemName.UNLOCK_COLOR_WHITE)
        self.assertTrue(self.can_reach_location(APLocation.AIR_RIDE_RACE_AS_EVERY_COLOR))


class TestAPBoxColorGating(KARTestBase):
    """The three per-color box counts. A color spawns only while its own unlock is held and its contents
    pool still holds something, so each needs the color plus a key to that pool: patches or food for
    blue, the special items for green, a copy ability for red. Red also accepts a legendary piece, whose
    carrier box the game spawns without consulting the color picker."""

    options = {
        **CT_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "city_trial_boxes_gated": Toggle.option_true,
        "city_trial_items_gated": Toggle.option_true,
        "city_trial_patches_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
    }

    def test_each_count_needs_its_own_color(self):
        for location, box in (
            (APLocation.BREAK_20_BLUE_BOXES, KARItemName.UNLOCK_BOX_BLUE),
            (APLocation.BREAK_10_GREEN_BOXES, KARItemName.UNLOCK_BOX_GREEN),
            (APLocation.BREAK_10_RED_BOXES, KARItemName.UNLOCK_BOX_RED),
        ):
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[box]], only_check_listed=True)

    def test_green_needs_a_green_item(self):
        self.assertAccessDependency(
            [APLocation.BREAK_10_GREEN_BOXES],
            [list(_GREEN_BOX_ITEMS)],
            only_check_listed=True,
        )

    def test_blue_needs_a_patch_or_food(self):
        self.assertAccessDependency(
            [APLocation.BREAK_20_BLUE_BOXES],
            [sorted(items_of_type(KARItemType.CT_PATCH_UNLOCK)), list(_BLUE_BOX_FOOD_ITEMS)],
            only_check_listed=True,
        )

    def test_all_up_alone_does_not_open_blue(self):
        # All Up's City Trial fall chance is zero, so it never joins the blue pool on its own (the mod
        # injects it only under Max Stats Insanity). Holding it must not make blue boxes spawn.
        withheld = [
            *items_of_type(KARItemType.CT_PATCH_UNLOCK),
            *_BLUE_BOX_FOOD_ITEMS,
            KARItemName.UNLOCK_ITEM_ALL_UP,
        ]
        state = CollectionState(self.multiworld)
        self.collect_all_but(withheld, state)
        for item in self.get_items_by_name(KARItemName.UNLOCK_ITEM_ALL_UP):
            state.collect(item)
        self.assertFalse(
            state.can_reach(APLocation.BREAK_20_BLUE_BOXES, "Location", self.player),
            "All Up alone must not satisfy the blue box count",
        )

    def test_red_needs_an_ability_or_a_legendary_piece(self):
        self.assertAccessDependency(
            [APLocation.BREAK_10_RED_BOXES],
            [sorted(items_of_type(KARItemType.ABILITY_UNLOCK)), list(LEGENDARY_PIECE_UNLOCK_ITEMS)],
            only_check_listed=True,
        )


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


_ALL_TR_COURSE_UNLOCKS = frozenset(items_of_type(KARItemType.TR_COURSE_UNLOCK))
_NO_WALL_COURSES = frozenset(
    {
        KARItemName.UNLOCK_TR_COURSE_GRASS,
        KARItemName.UNLOCK_TR_COURSE_SAND,
        KARItemName.UNLOCK_TR_COURSE_LIGHT,
        KARItemName.UNLOCK_TR_COURSE_METAL,
    }
)
# Sky is one of the three cut courses, so pinning it disables the random TR-course starter without
# satisfying the no-wall rule.
_PIN_TR_SKY_STARTER = {"start_inventory": {KARItemName.UNLOCK_TR_COURSE_SKY: 1}}


class TestTRNoWallLapCourseGating(KARTestBase):
    """top_ride_courses_gated ON: "race one lap without hitting a wall and finish 1st" only completes on
    Grass, Sand, Light or Metal. Without its rule the blanket "any course" rule would call it reachable
    on Sky, Water or Fire alone. Starter pinned to Sky, one of the cut courses."""

    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true, **_PIN_TR_SKY_STARTER}

    def test_rule_table_lists_exactly_the_no_wall_courses(self):
        self.assertEqual(
            frozenset(_TR_COURSE_SUBSET_RULES[TRLocation.LAP_NO_WALLS_AND_FIRST]),
            _NO_WALL_COURSES,
        )

    def test_each_no_wall_course_independently_satisfies(self):
        for course in _NO_WALL_COURSES:
            with self.subTest(course=course):
                state = CollectionState(self.multiworld)
                self.collect_all_but(_ALL_TR_COURSE_UNLOCKS, state)
                state.collect(self.world.create_item(course))
                self.assertTrue(
                    state.can_reach(TRLocation.LAP_NO_WALLS_AND_FIRST, "Location", self.player),
                    f"not reachable with only {course}",
                )

    def test_cut_courses_do_not_satisfy(self):
        # Sky, Water and Fire together must still leave the cell unreachable.
        cut = sorted(_ALL_TR_COURSE_UNLOCKS - _NO_WALL_COURSES)
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_TR_COURSE_UNLOCKS, state)
        for course in cut:
            state.collect(self.world.create_item(course))
        self.assertFalse(
            state.can_reach(TRLocation.LAP_NO_WALLS_AND_FIRST, "Location", self.player),
            f"reachable with only the cut courses {cut}",
        )


class TestTRNoWallLapGatingNotApplied(KARTestBase):
    """TR course gating OFF: all seven courses unlock at connect, so the no-wall cell needs no rule."""

    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_false}

    def test_reachable_with_no_courses(self):
        state = CollectionState(self.multiworld)
        self.collect_all_but(_ALL_TR_COURSE_UNLOCKS, state)
        self.assertTrue(state.can_reach(TRLocation.LAP_NO_WALLS_AND_FIRST, "Location", self.player))


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
    """air_ride_courses_gated ON: mode-root Air Ride cells need at least one AR course, since you cannot
    race without one. The course starter normally satisfies this, so the test removes it to expose the
    rule; any single course restores access, Nebula Belt included. The starter is pinned so removal is
    deterministic."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    def test_root_location_needs_any_course(self):
        # SWALL_200_ENEMIES is a mode-root cell with no other gating (generic swallow).
        loc = ARLocation.SWALL_200_ENEMIES
        self.assertTrue(self.can_reach_location(loc))  # pinned Fantasy Meadows starter present
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.assertFalse(self.can_reach_location(loc))  # no course in state
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT))
        self.assertTrue(self.can_reach_location(loc))  # any course, even the secret one, restores it


class TestTRRootCourseGating(KARTestBase):
    """top_ride_courses_gated ON: non-course-specific Top Ride cells need at least one TR course. Covers
    a TOP_RIDE-root cell plus the mode-level Free Run / Time Attack cells (which live in the
    TR_FREE_RUN / TR_TIME_ATTACK regions, not a course region). Starter pinned for deterministic removal."""

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


# Every stadium mode is gated by its own Unlock Stadium item.
_STADIUM_UNLOCKS: list[str] = [str(u) for u in STADIUM_UNLOCK_ITEMS]


class TestStadiumPlayCountGating(KARTestBase):
    """progressive stadiums ON: 'play in over 10/20 stadium modes!' need more than that many of the
    24 stadium modes unlocked (11 / 21), since a locked stadium can't be entered. The Air Glider
    starter is pinned so the precollected mode is known when counting."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true, **_PIN_STADIUM_STARTER}

    def _missing_other_than_starter(self, n: int) -> list[str]:
        return [s for s in _STADIUM_UNLOCKS if s != KARItemName.UNLOCK_STADIUM_AIR_GLIDER][:n]

    def test_unreachable_with_only_starter(self):
        # Only the pinned Air Glider starter is held - far short of either threshold.
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
    """progressive stadiums OFF: the mod unlocks all 24 stadiums at connect, so both 'play in over
    10/20 stadium modes!' cells are reachable from the start (24 >= 21)."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_false}

    def test_play_counts_reachable_empty(self):
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_PLAY_10_STADIUM_MODES))
        self.assertTrue(self.can_reach_location(CTLocation.STADIUM_PLAY_20_STADIUM_MODES))


# city_trial_items_gated adds ~30 CT_ITEM_UNLOCK progression items, overflowing the 90 default CT-only
# locations. Opening every CT progression-location flag raises capacity to all 120 CT cells so it fills.
_CT_ALL_PROGRESSION_LOCATIONS = {
    "city_trial_progression_high_effort": Toggle.option_true,
    "city_trial_progression_multiplayer": Toggle.option_true,
    "city_trial_progression_free_run": Toggle.option_true,
    "city_trial_progression_rng": Toggle.option_true,
    "city_trial_progression_bust_vehicles": Toggle.option_true,
}


class TestTRItemTypeCountItemGateOnly(KARTestBase):
    """top_ride_items_gated ON, abilities OFF: every TR item type is keyed solely by its own unlock
    (an ungated world's copy abilities are handed out at connect and the mod ignores them as a key),
    so 'get over 18 different types of items!' needs 19 of the 21 TR item unlocks."""

    options = {
        **TR_ONLY,
        "top_ride_items_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_false,
    }

    def test_needs_nineteen_of_twenty_one_item_unlocks(self):
        tr_unlocks = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK))
        # Hold back 3 -> 18 held < 19 -> unreachable; one more -> 19.
        self.collect_all_but(tr_unlocks[:3])
        self.assertFalse(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))
        self.collect_by_name(tr_unlocks[0])
        self.assertTrue(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))


class TestTRItemTypeCountBothGates(KARTestBase):
    """top_ride_items_gated AND abilities_gated ON: 'get over 18 different types!' still counts the 21
    TR item unlocks only. The four ability-themed types accept a copy ability unlock as a second key,
    but counting both keys would score one type twice, so the rule ignores the ability form."""

    options = {
        **TR_ONLY,
        "top_ride_items_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
    }

    def test_needs_nineteen_of_twenty_one_item_unlocks(self):
        tr_unlocks = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK))
        # Hold back 3 -> 18 held -> unreachable; one more -> 19.
        self.collect_all_but(tr_unlocks[:3])
        self.assertFalse(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))
        self.collect_by_name(tr_unlocks[0])
        self.assertTrue(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))


class TestTRItemTypeCountNoGates(KARTestBase):
    """Both TR-item and ability gating OFF: the mod unlocks every TR item type at connect - the three
    New-Item types (Lantern/Who?Paint/Chickie) via a has_reward nudge, the rest as vanilla defaults -
    so all 21 types can spawn and 'get over 18 different types!' is reachable with nothing collected."""

    options = {
        **TR_ONLY,
        "top_ride_items_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
    }

    def test_reachable_from_empty(self):
        self.assertTrue(self.can_reach_location(TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS))


class TestTRAnyItemBothGates(KARTestBase):
    """top_ride_items_gated AND abilities_gated ON: the generic 'collect/get items' cells name no specific
    item, so they need any one of the 21 TR item types able to spawn. Holding back every key makes them
    unreachable; any single one restores them (the 21 unlocks plus the four copy abilities)."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_true}

    _GENERIC = [TRLocation.COLLECT_500_ITEMS, TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE]

    def test_generic_item_cells_need_any_type(self):
        all_keys = [*sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK)), *sorted(_TR_ABILITY_ITEM_KEYS.values())]
        self.collect_all_but(all_keys)  # everything but the type keys (courses included)
        for loc in self._GENERIC:
            with self.subTest(location=loc, phase="no type"):
                self.assertFalse(self.can_reach_location(loc))
        self.collect_by_name(all_keys[0])  # any single key
        for loc in self._GENERIC:
            with self.subTest(location=loc, phase="one type"):
                self.assertTrue(self.can_reach_location(loc))


class TestTRAnyItemAbilitiesUngated(KARTestBase):
    """top_ride_items_gated ON, abilities OFF: the copy ability key is out of play, so the generic
    'collect/get items' cells need one of the 21 TR item unlocks and nothing else."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_false}

    _GENERIC = [TRLocation.COLLECT_500_ITEMS, TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE]

    def test_generic_item_cells_need_any_item_unlock(self):
        tr_unlocks = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK))
        self.collect_all_but(tr_unlocks)
        for loc in self._GENERIC:
            with self.subTest(location=loc, phase="no type"):
                self.assertFalse(self.can_reach_location(loc))
        self.collect_by_name(tr_unlocks[0])
        for loc in self._GENERIC:
            with self.subTest(location=loc, phase="one type"):
                self.assertTrue(self.can_reach_location(loc))


class TestTRAnyItemGateOff(KARTestBase):
    """top_ride_items_gated OFF: every TR item type spawns from connect, so the generic 'collect/get
    items' cells carry no HasAny rule and are reachable with nothing collected."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_false, "abilities_gated": Toggle.option_true}

    def test_generic_item_cells_reachable_empty(self):
        for loc in (TRLocation.COLLECT_500_ITEMS, TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))


class TestCTCompleteDragoonHydraItemGating(KARTestBase):
    """city_trial_items_gated ON, non-goal: 'In one match, complete both Dragoon and Hydra!' needs every
    Hydra/Dragoon piece to spawn, gated behind the six piece-spawn unlocks. (Default CT goal is
    100_checklist, so this cell exists as a normal location here rather than the victory event.)"""

    # Stadiums ungated to free ~23 progression slots: CT-only with items_gated ON + full default gating
    # would otherwise over-subscribe the 120 CT locations. Orthogonal to the item-gating logic under test.
    options = {
        **CT_ONLY,
        **_CT_ALL_PROGRESSION_LOCATIONS,
        "city_trial_items_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

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
    """city_trial_items_gated OFF: pieces always spawn, so the checkbox carries no rule and is reachable empty."""

    options = {**CT_ONLY, "city_trial_items_gated": Toggle.option_false}

    def test_reachable_empty(self):
        self.assertTrue(self.can_reach_location(CTLocation.COMPLETE_DRAGOON_AND_HYDRA))


class TestCTHydraAndDragoonGoalItemGating(KARTestBase):
    """hydra_and_dragoon goal + city_trial_items_gated ON: the victory event (which replaces the
    excluded COMPLETE_DRAGOON_AND_HYDRA location) is gated on the six piece-spawn unlocks, like the
    location rule for other goals."""

    options = {
        **CT_ONLY,
        **_CT_ALL_PROGRESSION_LOCATIONS,
        "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon,
        "city_trial_items_gated": Toggle.option_true,
        # Stadiums ungated for headroom; orthogonal to the victory-event item-gating under test.
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_victory_event_needs_six_piece_unlocks(self):
        victory = f"{CTLocation.COMPLETE_DRAGOON_AND_HYDRA} (Victory)"
        self.assertFalse(self.can_reach_location(victory))
        for piece in LEGENDARY_PIECE_UNLOCK_ITEMS:
            self.collect_by_name(piece)
        self.assertTrue(self.can_reach_location(victory))


class TestFill100NonGoalGating(KARTestBase):
    """'Fill in over 100 Checklist blocks!' is a real in-game meta checkbox the game auto-completes once
    the player fills over 100 of that mode's other boxes - distinct from the synthetic 'N checklist
    blocks' goal. When it is NOT the mode's goal it stays a normal location and must carry that same
    requirement, or fill could strand progression behind ~100 checks. Top Ride is on the N-blocks goal
    here, with course gating holding six of seven courses."""

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
        """Count of reachable Top Ride boxes excluding the FILL_100 cell itself."""
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
        # Collect everything bar victory events: all courses open, far over 100 boxes reachable.
        self.collect_all_but_victories()
        self.assertGreaterEqual(self._reachable_other_tr_boxes(), 100)
        self.assertTrue(self.can_reach_location(self._FILL_100))


class TestFill100AsGoalNotARealLocation(KARTestBase):
    """The flip side: when 'Fill in over 100' IS the mode's goal it is excluded from the pool (its
    victory event carries the count rule instead), so it is not a normal location at all. The
    cell-vs-goal split matches the mod, where GOAL_100_CHECKLIST keys off this same cell."""

    options = {**TR_ONLY, "top_ride_goal": TopRideGoal.option_100_checklist_blocks}

    def test_cell_excluded_when_it_is_the_goal(self):
        self.assertNotIn(TRLocation.FILL_IN_100_CHECKLIST_BLOCKS, self.real_location_names())
