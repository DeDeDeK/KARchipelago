"""Access rules for set_rules(): each case pins its locations unreachable without the gating item and
reachable once it is collected. A random starter that would shadow an item under test is pinned via
start_inventory."""

import unittest
from typing import TYPE_CHECKING

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARData import GameMode
from ..KARItems import (
    AP_STAR_PIECE_UNLOCK_ITEMS,
    CHARACTER_MACHINE_UNLOCKS,
    DAMAGING_ABILITY_UNLOCKS,
    DD5_DAMAGING_ABILITY_UNLOCKS,
    ITEM_TABLE,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    STADIUM_CHECKLIST_REWARDS,
    STADIUM_UNLOCK_ITEMS,
    KARItemName,
    KARItemType,
)
from ..KARLocations import CITY_TRIAL_PROGRESSION_GROUPS, APLocation, ARLocation, CTLocation, TRLocation
from ..KAROptions import ArchipelagoGoal, CityTrialGoal, TopRideGoal
from ..KARRegions import KARRegion
from ..KARRules import (
    _AP_ITEM_LOCATION_RULES,
    _AR_COURSE_SUBSET_RULES,
    _BLUE_BOX_FOOD_ITEMS,
    _CHARGE_DEPENDENT_CT_MACHINES,
    _CT_ANY_MACHINE_LOCATIONS,
    _CT_FLIGHT_MACHINES,
    _CT_MACHINE_UNLOCKS,
    _FM_20MPH_EXCLUDED_MACHINES,
    _FM_20MPH_MACHINES,
    _FM_SHORTCUT_EXCLUDED_MACHINES,
    _FM_SHORTCUT_MACHINES,
    _GOOD_GLIDE_MACHINES,
    _GREEN_BOX_ITEMS,
    _PATCH_LOCATION_RULES,
    _POOR_GLIDE_MACHINES,
    _STEERABLE_CT_MACHINES,
    _SWALLOW_ENEMY_COURSE_RULES,
    _TAC_LOOT_ABILITY_UNLOCK,
    _TAC_LOOT_ITEM_UNLOCKS,
    _TR_ABILITY_ITEM_KEYS,
    _TR_COURSE_SUBSET_RULES,
    _TR_ITEM_LOCATION_RULES,
)
from . import (
    ALL_MODES,
    AR_AND_TR,
    AR_ONLY,
    CT_ONLY,
    OVERLAP_REWARDS,
    TR_ONLY,
    KARTestBase,
    items_of_type,
    names,
)

# Type-check time the mixin below inherits KARTestBase so `self.*` resolves; at runtime it is `object`.
_MixinBase = KARTestBase if TYPE_CHECKING else object


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


# Pin random starter picks so they cannot shadow an item under test. Only the categories that grant a
# random starter need pinning: stadiums, machines, AR/TR courses and colors.
_PIN_MACHINE_STARTER = {"start_inventory": {KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: 1}}
_PIN_AR_COURSE_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: 1}}
_PIN_TR_COURSE_STARTER = {"start_inventory": {KARItemName.UNLOCK_TR_COURSE_GRASS: 1}}
_PIN_STADIUM_STARTER = {"start_inventory": {KARItemName.UNLOCK_STADIUM_AIR_GLIDER: 1}}
_PIN_COLOR_STARTER = {"start_inventory": {KARItemName.UNLOCK_COLOR_PINK: 1}}
# Beanstalk Park is the one standard Air Ride course none of the four named swallow-enemies spawn on.
_PIN_BEANSTALK_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK: 1}}

# The Air Ride machine pool the Fantasy Meadows rules carve their exclusions out of, derived the way
# KARRules derives it so an excluded name that is not one of them fails rather than excluding nothing.
_AR_MACHINE_UNLOCKS = frozenset(
    name for name in items_of_type(KARItemType.MACHINE_UNLOCK) if GameMode.AIRRIDE in ITEM_TABLE[name].source_modes
)

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
# Derby 5 spawns only four of the copy panels, so it keeps its own, shorter list.
_DERBY5_DAMAGE_KEYS = [
    [KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN],
    *([machine] for machine in CHARACTER_MACHINE_UNLOCKS),
    *([ability] for ability in DD5_DAMAGING_ABILITY_UNLOCKS),
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
        # These take any enemy, so their only rule is the course one every enemy cell carries - and the
        # random starter can be Nebula Belt, so collect a course that actually spawns enemies.
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS))
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

    def test_ability_cells_need_no_inhale_when_courses_are_open(self):
        """A ground copy panel grants an ability without inhaling. With Air Ride courses ungated, Nebula
        Belt and Celestial Valley are always open, so the cells naming an ability carry no Inhale rule."""
        for location in (
            ARLocation.FIRST_WITH_FIRE_ABILITY,
            ARLocation.FIRST_WITH_SLEEP_ABILITY,
            ARLocation.SWORD_CHALLENGE_10_SWINGS,
            ARLocation.TORNADO_CHALLENGE_15_KO,
        ):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))

    def test_ar_quick_spin_locations_need_unlock(self):
        self.assertAccessDependency(
            [
                ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN,
                ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
                ARLocation.FINISH_SPINNING_AND_FIRST,
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
                ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR,
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

    def test_melee_ability_boxes_need_inhale(self):
        self.assertAccessDependency(
            [APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY, APLocation.KM1_KO_100_ENEMIES_BY_YOURSELF],
            [[KARItemName.UNLOCK_BASE_ABILITY_INHALE]],
            only_check_listed=True,
        )


class TestBaseAbilitiesGatingArchipelagoBulkStar(KARTestBase):
    """Bulk Star is one of the machines Charge makes usable, so the Archipelago "1st on Bulk Star" box
    needs Charge on top of whatever the machine gate asks for. machines_gated is OFF here so the machine
    unlock isn't a second key, isolating the base-ability rule."""

    options = {
        **AR_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "base_abilities_gated": Toggle.option_true,
        "machines_gated": Toggle.option_false,
    }

    def test_bulk_star_box_needs_charge(self):
        self.assertAccessDependency(
            [APLocation.SR1_FINISH_1ST_ON_BULK_STAR],
            [[KARItemName.UNLOCK_BASE_ABILITY_CHARGE]],
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
                CTLocation.STADIUM_DD4_KO_YOUR_RIVALS_5,
                CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X,
            ],
            _DERBY_DAMAGE_KEYS,
            only_check_listed=True,
        )

    def test_destruction_derby_5_needs_one_of_its_own_panels(self):
        self.assertAccessDependency(
            [CTLocation.STADIUM_DD5_KO_A_RIVAL_10X, CTLocation.STADIUM_DD5_KO_YOUR_RIVALS_5],
            _DERBY5_DAMAGE_KEYS,
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
        state = self.state_without([name for group in _DERBY_DAMAGE_KEYS for name in group])
        for item in self.get_items_by_name([KARItemName.UNLOCK_MACHINE_HYDRA]):
            state.collect(item)
        self.assertFalse(self.reaches(state, CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5))


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
    Uses ALL_MODES because the 36 added unlock items need more default locations than CT-only provides."""

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
        # "Steal over 8 items from Tac" needs a kind carrying weight in Tac's own column of the event
        # drop table: the nine patches, Sleep, All Up or one of the twelve foods. Every other item kind
        # sits at 0 there, and the six legendary pieces have no row at all.
        item_unlocks = items_of_type(KARItemType.CT_ITEM_UNLOCK)
        patch_unlocks = items_of_type(KARItemType.CT_PATCH_UNLOCK)
        held_out = item_unlocks | patch_unlocks | {_TAC_LOOT_ABILITY_UNLOCK}

        loot = [*sorted(_TAC_LOOT_ITEM_UNLOCKS), *sorted(patch_unlocks), _TAC_LOOT_ABILITY_UNLOCK]
        not_loot = sorted(item_unlocks - set(_TAC_LOOT_ITEM_UNLOCKS))

        state = self.state_without(held_out)

        self.assertFalse(
            self.reaches(state, CTLocation.STEAL_8_FROM_TAC),
            "reachable with no Tac loot held",
        )

        # Any single kind with weight in his column is enough - one type respawns as he throws.
        for unlock in loot:
            item = self.world.create_item(unlock)
            state.collect(item)
            self.assertTrue(
                self.reaches(state, CTLocation.STEAL_8_FROM_TAC),
                f"not reachable with only {unlock}",
            )
            state.remove(item)

        # Nothing else is loot, the legendary pieces included: Tac throws a roll over his column, never
        # the carrier box that is the pieces' only delivery.
        for unlock in not_loot:
            item = self.world.create_item(unlock)
            state.collect(item)
            self.assertFalse(
                self.reaches(state, CTLocation.STEAL_8_FROM_TAC),
                f"reachable with only {unlock}, which has no weight in Tac's column",
            )
            state.remove(item)

    def test_item_pickup_locations_need_any_counting_item_unlock(self):
        # "Get/pick up N items" cells count every itemkind except the three boxes, so with items, patches
        # and abilities all gated, one unlock from any of the three sets suffices.
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

        # Everything but the counting unlocks, precollected copies included.
        state = self.state_without(counting_unlocks)

        # Everything except counting unlocks is now collected, including box unlocks. Boxes are not a
        # counting source, so the cells stay unreachable (doubles as the "breaking a box does not count" check).
        for location in pickup_locations:
            self.assertFalse(
                self.reaches(state, location),
                f"{location} reachable with no counting-item unlock held",
            )
        # Any single counting unlock makes every cell reachable. Build via create_item so the check
        # covers unlocks that left the itempool (e.g. the precollected starter).
        for unlock in sorted(counting_unlocks):
            item = self.world.create_item(unlock)
            state.collect(item)
            for location in pickup_locations:
                self.assertTrue(
                    self.reaches(state, location),
                    f"{location} not reachable with only {unlock}",
                )
            state.remove(item)


class TestCityTrialItemsGatingNotApplied(KARTestBase):
    """city_trial_items_gated OFF: every item type spawns from connect, so no item unlock exists and the
    cells that count items carry no item rule. What they keep is whatever else still gates them - Tac's
    event unlock, and the Red Box the legendary pieces arrive in."""

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
        world_items = self.world_item_names()
        self.assertNotIn(KARItemName.UNLOCK_ITEM_ALL_UP, world_items)
        self.assertNotIn(KARItemName.UNLOCK_ITEM_HOT_DOG, world_items)

    def test_tac_keeps_only_its_event_rule(self):
        # Tac always has loot now, so the event unlock alone must open the cell.
        state = self.state_without([KARItemName.UNLOCK_EVENT_TAC])
        self.assertFalse(self.reaches(state, CTLocation.STEAL_8_FROM_TAC))
        state.collect(self.world.create_item(KARItemName.UNLOCK_EVENT_TAC))
        self.assertTrue(self.reaches(state, CTLocation.STEAL_8_FROM_TAC))

    def test_assemble_cell_keeps_only_its_red_box_rule(self):
        state = self.state_without([KARItemName.UNLOCK_BOX_RED])
        self.assertFalse(self.reaches(state, CTLocation.COMPLETE_DRAGOON_AND_HYDRA))
        state.collect(self.world.create_item(KARItemName.UNLOCK_BOX_RED))
        self.assertTrue(self.reaches(state, CTLocation.COMPLETE_DRAGOON_AND_HYDRA))


class TestCTTacNeedsEventAndLoot(KARTestBase):
    """Events + items gated: the Tac cell composes both rules -- Tac has to show up AND have something to
    steal. Either key alone leaves it unreachable. ALL_MODES because the 36 item unlocks the item gate
    adds need more default locations than CT-only provides."""

    options = {
        **ALL_MODES,
        "city_trial_events_gated": Toggle.option_true,
        "city_trial_items_gated": Toggle.option_true,
    }

    def test_needs_both_the_event_and_an_item(self):
        # Patches and Sleep carry weight in Tac's column too, so they are held out alongside the item
        # unlocks - otherwise the loot half is already satisfied before the test starts.
        keys = (
            items_of_type(KARItemType.CT_ITEM_UNLOCK)
            | items_of_type(KARItemType.CT_PATCH_UNLOCK)
            | {_TAC_LOOT_ABILITY_UNLOCK, KARItemName.UNLOCK_EVENT_TAC}
        )
        state = self.state_without(keys)

        loc = CTLocation.STEAL_8_FROM_TAC
        self.assertFalse(self.reaches(state, loc), "reachable with neither key")

        event = self.world.create_item(KARItemName.UNLOCK_EVENT_TAC)
        state.collect(event)
        self.assertFalse(self.reaches(state, loc), "reachable with the event but no loot")
        state.remove(event)

        loot = self.world.create_item(KARItemName.UNLOCK_ITEM_APPLE)
        state.collect(loot)
        self.assertFalse(self.reaches(state, loc), "reachable with loot but no event")

        state.collect(self.world.create_item(KARItemName.UNLOCK_EVENT_TAC))
        self.assertTrue(self.reaches(state, loc), "not reachable with both keys")


class TestMachinesGatingApplied(KARTestBase):
    """machines_gated ON: a cell naming a machine needs that machine's unlock, and a "bust X on Y" cell
    needs both. The Free Run swap cell needs two distinct ones, since Free Run only ever places machines
    other than the rider's current one."""

    options = {**ALL_MODES, "machines_gated": Toggle.option_true, **_PIN_MACHINE_STARTER}

    def test_named_machine_cells_need_their_unlock(self):
        for loc, unlock in (
            (CTLocation.STADIUM_DR1_17_00_FORMULA, KARItemName.UNLOCK_MACHINE_FORMULA_STAR),
            (ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR, KARItemName.UNLOCK_MACHINE_SHADOW_STAR),
        ):
            with self.subTest(location=loc):
                self.assertAccessDependency([loc], [[unlock]], only_check_listed=True)

    def test_bust_cells_need_both_machines(self):
        self.assertAccessDependency(
            [CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR],
            [[KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE, KARItemName.UNLOCK_MACHINE_WARP_STAR]],
            only_check_listed=True,
        )

    def test_free_run_swap_cell_needs_two_distinct_machines(self):
        loc = CTLocation.FR_CHANGE_AIR_RIDE_MACHINES_10X
        # The pinned Flight Warp Star is one of the two; one more machine completes the pair.
        state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
        state.collect(self.world.create_item(KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR))
        self.assertFalse(self.reaches(state, loc), "one machine cannot be swapped away from")
        state.collect(self.world.create_item(KARItemName.UNLOCK_MACHINE_WARP_STAR))
        self.assertTrue(self.reaches(state, loc))


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
        for reward in OVERLAP_REWARDS["machines_gated"]:
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
        # FIRST_WHILE_HOLDING_HAMMER is in the TOP_RIDE root region (not course-gated).
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


class TestStadiumGatingApplied(KARTestBase):
    """Stadiums gated: every one of the 24, the six vanilla hands out as checklist rewards included, is
    gated by its own Unlock Stadium item, so all 24 are obtainable and progression-classified and the
    overlapping stadium rewards leave the pool. Starter pinned to Air Glider so the rest stay locked."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true, **_PIN_STADIUM_STARTER}

    # (location, its own stadium unlock, the vanilla predecessor unlock it must NOT need). They used to
    # sit behind a DD3<-DD2 / DR4<-DR3 / KM2<-KM1 chain, which the mod does not reproduce - stadium
    # availability comes from the AP unlock mask, never from completing the box.
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

    def test_unlocks_are_obtainable_and_progression(self):
        world_items = self.world_item_names()
        pool = {it.name: it for it in self.itempool_items()}
        for unlock in items_of_type(KARItemType.CT_STADIUM_UNLOCK):
            with self.subTest(unlock=unlock):
                self.assertIn(unlock, world_items, f"{unlock} must be obtainable when stadiums are gated")
                if unlock in pool:
                    self.assertTrue(
                        pool[unlock].classification & ItemClassification.progression,
                        f"{unlock} must be progression-classified to gate its stadium",
                    )

    def test_overlap_rewards_excluded(self):
        world_items = self.world_item_names()
        for reward in STADIUM_CHECKLIST_REWARDS:
            with self.subTest(reward=reward):
                self.assertNotIn(reward, world_items, "a gated stadium is keyed by its unlock, not its reward")

    def test_a_stadium_cell_needs_its_own_unlock(self):
        # DRAG_RACE_1 has no checklist-reward overlap; DRAG_RACE_4 does, and still gates on its unlock.
        for loc, unlock in (
            (CTLocation.STADIUM_DR1_FINISH_00_24_00, KARItemName.UNLOCK_STADIUM_DRAG_RACE_1),
            (CTLocation.STADIUM_DR4_FINISH_00_24_00, KARItemName.UNLOCK_STADIUM_DRAG_RACE_4),
        ):
            with self.subTest(location=loc):
                self.assertAccessDependency([loc], [[unlock]], only_check_listed=True)

    def test_an_all_group_cell_opens_on_any_of_its_sub_stadiums(self):
        # The HasAny rule accepts any one, so every member has to be listed for the helper to pass.
        for loc, unlocks in (
            (
                CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X,
                [
                    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1,
                    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2,
                    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3,
                    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4,
                    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5,
                ],
            ),
            (
                CTLocation.STADIUM_KM_ALL_KO_500_ENEMIES,
                [KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1, KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2],
            ),
        ):
            with self.subTest(location=loc):
                self.assertAccessDependency([loc], [[unlock] for unlock in unlocks], only_check_listed=True)

    def test_a_reward_stadium_needs_no_vanilla_predecessor(self):
        for loc, own_unlock, predecessor in self._CHAIN_STADIUMS:
            with self.subTest(location=loc, withheld=predecessor):
                state = self.state_with(own_unlock)
                self.assertFalse(
                    state.has(predecessor, self.player), f"{predecessor} leaked in, making this subtest vacuous"
                )
                self.assertTrue(self.reaches(state, loc), f"{loc} should be reachable on {own_unlock} alone")
                # Guard against the above passing for the wrong reason.
                self.assertAccessDependency([loc], [[own_unlock]], only_check_listed=True)

    def test_play_count_cells_need_more_than_that_many_stadiums(self):
        # "Play in over 10/20 stadium modes" needs 11 / 21 unlocked, since a locked one cannot be
        # entered. Withholding `short_by` non-starter stadiums leaves exactly one short of that.
        others = sorted(names(STADIUM_UNLOCK_ITEMS) - {str(KARItemName.UNLOCK_STADIUM_AIR_GLIDER)})
        for loc, short_by in (
            (CTLocation.STADIUM_PLAY_10_STADIUM_MODES, 14),
            (CTLocation.STADIUM_PLAY_20_STADIUM_MODES, 4),
        ):
            with self.subTest(location=loc):
                # Only the pinned Air Glider starter is held - far short of either threshold.
                self.assertFalse(self.can_reach_location(loc))
                missing = others[:short_by]
                state = self.state_without(missing)
                self.assertFalse(self.reaches(state, loc), "reachable one stadium short of the threshold")
                state.collect(self.world.create_item(missing[0]))
                self.assertTrue(self.reaches(state, loc))


class TestStadiumDragRaceAllGating(KARTestBase):
    """DR_ALL's only box is the Archipelago photo finish, which the mod counts in all four DRAG RACE
    stadiums, so this case needs the AP checklist on."""

    options = {
        **CT_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "city_trial_stadiums_gated": Toggle.option_true,
        **_PIN_STADIUM_STARTER,
    }

    def test_dr_all_reachable_via_any_dr_unlock(self):
        self.assertAccessDependency(
            [APLocation.DR_PHOTO_FINISH],
            [
                [KARItemName.UNLOCK_STADIUM_DRAG_RACE_1],
                [KARItemName.UNLOCK_STADIUM_DRAG_RACE_2],
                [KARItemName.UNLOCK_STADIUM_DRAG_RACE_3],
                [KARItemName.UNLOCK_STADIUM_DRAG_RACE_4],
            ],
            only_check_listed=True,
        )


class TestStadiumGatingNotApplied(KARTestBase):
    """Stadiums ungated: the mod unlocks all 24 at connect, so every stadium cell - the six that double
    as checklist rewards and both play-count cells included - is reachable from the start, and the six
    stadium reward items are excluded from the pool."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_false}

    def test_stadium_cells_reachable_empty(self):
        for loc in (
            CTLocation.STADIUM_DR1_FINISH_00_24_00,
            # DR4 / DD3 are the reward-overlap stadiums.
            CTLocation.STADIUM_DR4_FINISH_00_24_00,
            CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5,
            # 24 unlocked is over both thresholds.
            CTLocation.STADIUM_PLAY_10_STADIUM_MODES,
            CTLocation.STADIUM_PLAY_20_STADIUM_MODES,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))

    def test_stadium_rewards_excluded(self):
        world_items = self.world_item_names()
        for reward in STADIUM_CHECKLIST_REWARDS:
            with self.subTest(reward=reward):
                self.assertNotIn(reward, world_items)


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


class TestBoxesGatedWithContentsGated(KARTestBase):
    """Boxes gated alongside the gates that own their contents: a color that is unlocked but whose whole
    contents pool is still locked never spawns, so the break-box cells need both halves."""

    options = {
        **ALL_MODES,
        "city_trial_boxes_gated": Toggle.option_true,
        "city_trial_items_gated": Toggle.option_true,
        "city_trial_patches_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
    }

    def test_box_unlocks_alone_do_not_open_break_box_cells(self):
        state = self.state_with(
            KARItemName.UNLOCK_BOX_BLUE,
            KARItemName.UNLOCK_BOX_GREEN,
            KARItemName.UNLOCK_BOX_RED,
        )
        for location in (CTLocation.BREAK_500_BOXES, CTLocation.BREAK_1000_BOXES):
            with self.subTest(location=location):
                self.assertFalse(
                    self.reaches(state, location),
                    f"{location} should need contents for an unlocked color, not just the color",
                )

    def test_a_color_with_contents_opens_break_box_cells(self):
        state = self.state_with(KARItemName.UNLOCK_BOX_BLUE, KARItemName.UNLOCK_PATCH_BOOST)
        for location in (CTLocation.BREAK_500_BOXES, CTLocation.BREAK_1000_BOXES):
            with self.subTest(location=location):
                self.assertTrue(self.reaches(state, location))

    def test_contents_without_the_color_does_not_open_break_box_cells(self):
        state = self.state_with(KARItemName.UNLOCK_PATCH_BOOST, *_GREEN_BOX_ITEMS)
        for location in (CTLocation.BREAK_500_BOXES, CTLocation.BREAK_1000_BOXES):
            with self.subTest(location=location):
                self.assertFalse(self.reaches(state, location))


class TestBoxesUngatedWithContentsGated(KARTestBase):
    """Boxes ungated but their contents gated: every color is unlocked at connect, yet none can spawn
    until something is left in one of the three pools, so the break-box cells still carry a rule."""

    options = {
        **ALL_MODES,
        "city_trial_boxes_gated": Toggle.option_false,
        "city_trial_items_gated": Toggle.option_true,
        "city_trial_patches_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
    }

    def test_break_box_locations_need_some_box_contents(self):
        self.assertAccessDependency(
            [CTLocation.BREAK_500_BOXES, CTLocation.BREAK_1000_BOXES],
            [
                sorted(items_of_type(KARItemType.CT_PATCH_UNLOCK)),
                list(_BLUE_BOX_FOOD_ITEMS),
                list(_GREEN_BOX_ITEMS),
                sorted(items_of_type(KARItemType.ABILITY_UNLOCK)),
                list(LEGENDARY_PIECE_UNLOCK_ITEMS),
            ],
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


_ALL_AR_COURSE_UNLOCKS = frozenset(items_of_type(KARItemType.AR_COURSE_UNLOCK))
_ALL_TR_COURSE_UNLOCKS = frozenset(items_of_type(KARItemType.TR_COURSE_UNLOCK))

# Courses pinned as the starter for each subset rule below: one the rule does NOT accept, so it
# suppresses the random pick without satisfying the rule under test.
_PIN_AR_CHECKER_STARTER = {"start_inventory": {KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS: 1}}
_PIN_TR_SKY_STARTER = {"start_inventory": {KARItemName.UNLOCK_TR_COURSE_SKY: 1}}

_CLIFF_COURSES = frozenset(
    {
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    }
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
_NO_WALL_COURSES = frozenset(
    {
        KARItemName.UNLOCK_TR_COURSE_GRASS,
        KARItemName.UNLOCK_TR_COURSE_SAND,
        KARItemName.UNLOCK_TR_COURSE_LIGHT,
        KARItemName.UNLOCK_TR_COURSE_METAL,
    }
)


def _make_course_subset_test(opts: dict, all_courses: frozenset, rules: dict) -> type:
    """A cell only some courses can complete. Without its own rule the blanket "any course" rule would
    call it reachable on any one of them, so each listed course has to satisfy it alone and the unlisted
    ones must not satisfy it even all together."""

    class _CourseSubset(KARTestBase):
        options = opts

        def test_unreachable_with_every_course_held_back(self):
            state = self.state_without(all_courses)
            for location in rules:
                with self.subTest(location=location):
                    self.assertFalse(self.reaches(state, location), f"{location} reachable with no course")

        def test_each_listed_course_independently_satisfies(self):
            for location, courses in rules.items():
                for course in courses:
                    with self.subTest(location=location, course=course):
                        state = self.state_without(all_courses)
                        state.collect(self.world.create_item(course))
                        self.assertTrue(self.reaches(state, location), f"{location} needs only {course}")

        def test_the_unlisted_courses_together_do_not_satisfy(self):
            # Collecting EVERY course the rule leaves out pins the accepted set exactly: a wrongly
            # omitted course would make the cell reachable here.
            for location, courses in rules.items():
                unlisted = sorted(all_courses - frozenset(courses))
                with self.subTest(location=location):
                    state = self.state_without(all_courses)
                    for course in unlisted:
                        state.collect(self.world.create_item(course))
                    self.assertFalse(self.reaches(state, location), f"{location} reachable on {unlisted}")

    return _CourseSubset


class TestCourseSubsetRuleTables(unittest.TestCase):
    """Non-vacuity for the behavioural cases below: they prove whatever the production tables happen to
    hold, so the hand-written expectations are pinned against them here. The swallow rules are the
    exception - their production table IS the enemy-spawn map, so there is nothing to restate."""

    def test_tables_list_exactly_the_expected_courses(self):
        for table, location, expected in (
            (_AR_COURSE_SUBSET_RULES, ARLocation.DROP_FROM_CLIFFS_3X, _CLIFF_COURSES),
            (_AR_COURSE_SUBSET_RULES, ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR, _AIR_FINISH_COURSES),
            (_TR_COURSE_SUBSET_RULES, TRLocation.LAP_NO_WALLS_AND_FIRST, _NO_WALL_COURSES),
        ):
            with self.subTest(location=location):
                self.assertEqual(frozenset(table[location]), expected)


_COURSE_SUBSET_CASES: list[tuple[str, dict, frozenset, dict]] = [
    # Swallowing a named copy-ability enemy needs a course that enemy actually spawns on, not merely the
    # ability. Beanstalk Park is the pin: the one standard course none of these four enemies spawn on.
    (
        "ar_swallow_enemies",
        {
            **AR_ONLY,
            "abilities_gated": Toggle.option_false,
            "air_ride_courses_gated": Toggle.option_true,
            **_PIN_BEANSTALK_STARTER,
        },
        _ALL_AR_COURSE_UNLOCKS,
        _SWALLOW_ENEMY_COURSE_RULES,
    ),
    # "Drop from the cliffs 3 times" only completes where there is a cliff that drops you.
    (
        "ar_drop_from_cliffs",
        {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER},
        _ALL_AR_COURSE_UNLOCKS,
        {ARLocation.DROP_FROM_CLIFFS_3X: _CLIFF_COURSES},
    ),
    # "Finish 1st while flying through the air" needs something to launch off near the finish line.
    (
        "ar_air_finish",
        {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_CHECKER_STARTER},
        _ALL_AR_COURSE_UNLOCKS,
        {ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR: _AIR_FINISH_COURSES},
    ),
    # "Race one lap without hitting a wall and finish 1st" only completes on the four open courses.
    (
        "tr_no_wall_lap",
        {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true, **_PIN_TR_SKY_STARTER},
        _ALL_TR_COURSE_UNLOCKS,
        {TRLocation.LAP_NO_WALLS_AND_FIRST: _NO_WALL_COURSES},
    ),
]

for _label, _opts, _all, _rules in _COURSE_SUBSET_CASES:
    _register(_make_course_subset_test(_opts, _all, _rules), f"TestCourseSubsetRule_{_label}")


class TestARSwallowEnemyAbilityAndCourseGating(KARTestBase):
    """abilities_gated AND air_ride_courses_gated both ON: a swallow-named-enemy cell needs BOTH the copy
    ability unlock AND a course the enemy spawns on, so the two rules compose with AND."""

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
        base = self.state_without(_ALL_AR_COURSE_UNLOCKS | {ability})

        def reachable(*items: str) -> bool:
            state = base.copy()
            for name in items:
                state.collect(self.world.create_item(name))
            return self.reaches(state, location)

        self.assertFalse(reachable(), "reachable with neither ability nor course")
        self.assertFalse(reachable(course), "reachable with course but no ability")
        self.assertFalse(reachable(ability), "reachable with ability but no course")
        self.assertTrue(reachable(course, ability), "not reachable with both ability and course")


_NEBULA_REGIONS = (
    KARRegion.AIR_RIDE_NEBULA_BELT,
    KARRegion.AIR_RIDE_TA_NEBULA_BELT,
    KARRegion.AIR_RIDE_FR_NEBULA_BELT,
)


class TestARNebulaBeltUnlockGate(KARTestBase):
    """Nebula Belt is gated by its course unlock item like every other course, not by the Race-100-laps
    checkbox. Its regions hold no AP locations, so this goes through region reachability. Starter pinned
    to Fantasy Meadows so Nebula's own unlock is not precollected."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    def test_nebula_regions_need_the_unlock(self):
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                self.assertFalse(self.multiworld.get_region(region_name, self.player).can_reach(self.multiworld.state))
        self.collect_by_name(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT)
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                self.assertTrue(self.multiworld.get_region(region_name, self.player).can_reach(self.multiworld.state))


class TestCourseGatingNotApplied(KARTestBase):
    """Both course gates OFF: the mod unlocks every course at connect and no course-unlock item exists,
    so nothing keyed on one may carry a rule - a Has()-style rule here would strand cells behind items
    that were never created."""

    options = {
        **AR_AND_TR,
        "air_ride_courses_gated": Toggle.option_false,
        "top_ride_courses_gated": Toggle.option_false,
    }

    def test_subset_rule_cells_reachable_empty(self):
        state = self.state_without(_ALL_AR_COURSE_UNLOCKS | _ALL_TR_COURSE_UNLOCKS)
        for loc in (
            ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR,
            ARLocation.DROP_FROM_CLIFFS_3X,
            TRLocation.LAP_NO_WALLS_AND_FIRST,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.reaches(state, loc))

    def test_root_and_all_courses_cells_reachable_empty(self):
        for loc in (
            ARLocation.SWALL_200_ENEMIES,
            ARLocation.RACE_100_LAPS,
            ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES,
            TRLocation.CROSS_GOAL_20,
            TRLocation.FR_RACE_100_LAPS,
            TRLocation.TA_CROSS_GOAL_30,
            TRLocation.FIRST_ON_ALL_COURSES,
            TRLocation.ALL_COURSES_NO_BOOST,
            TRLocation.FIRST_ON_ALL_COURSES_WITHOUT_BOOST,
            TRLocation.NOITEMS_ALL_COURSES,
            TRLocation.NOITEMS_FIRST_ALL_COURSES,
        ):
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))

    def test_nebula_regions_reachable_and_its_reward_excluded(self):
        for region_name in _NEBULA_REGIONS:
            with self.subTest(region=region_name):
                self.assertTrue(self.multiworld.get_region(region_name, self.player).can_reach(self.multiworld.state))
        self.assertNotIn(KARItemName.AR_REWARD_NEBULA_BELT_COURSE, self.world_item_names())


class TestARMachineCellNeedsOnlyOwnCourse(KARTestBase):
    """Regression: a machine-specific AR cell needs its machine and its OWN course, nothing else. It used
    to chain onto the box that awards the machine in vanilla, silently demanding that box's course too -
    the reported case was Swerve Star's Machine Passage cell held behind Sky Sands. Nebula Belt is the
    pin because no cell below names it, and both pins share one start_inventory dict."""

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
                state = self.state_with()
                for name in (machine, own_course):
                    state.collect(self.get_item_by_name(name), prevent_sweep=True)
                # Non-vacuity: the course the removed chain used to drag in must still be missing.
                if foreign_course != own_course:
                    self.assertFalse(
                        state.has(foreign_course, self.player),
                        f"{foreign_course} leaked into the state, making this subtest vacuous",
                    )
                self.assertTrue(
                    self.reaches(state, loc),
                    f"{loc} should be reachable on {machine} + {own_course} alone",
                )

    def test_unreachable_without_machine(self):
        # Guard against the above passing for the wrong reason: with the course but no machine, no.
        for loc, machine, own_course, _ in self._MACHINE_CELLS:
            with self.subTest(location=loc, stripped=machine):
                state = self.state_with()
                state.collect(self.get_item_by_name(own_course), prevent_sweep=True)
                self.assertFalse(
                    self.reaches(state, loc),
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
        state = self.state_with()
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
            self.reaches(state, ARLocation.FM_LAP_ABOVE_20_MPH),
            "the 20 mph cell should not be reachable on the excluded machines",
        )

    def test_reachable_on_each_capable_machine(self):
        for machine in _FM_20MPH_MACHINES:
            with self.subTest(machine=machine):
                state = self.state_with()
                state.collect(self.get_item_by_name(machine), prevent_sweep=True)
                self.assertTrue(
                    self.reaches(state, ARLocation.FM_LAP_ABOVE_20_MPH),
                    f"the 20 mph cell should be reachable on {machine} alone",
                )

    def test_excluded_machines_are_air_ride_machines(self):
        # Guards against a typo'd or Top-Ride-only name silently excluding nothing.
        for name in _FM_20MPH_EXCLUDED_MACHINES:
            self.assertIn(name, _AR_MACHINE_UNLOCKS)
        self.assertEqual(len(_FM_20MPH_EXCLUDED_MACHINES), 4)
        self.assertFalse(set(_FM_20MPH_MACHINES) & _FM_20MPH_EXCLUDED_MACHINES)


class TestTargetFlightAirborneNeedsAGlidingMachine(KARTestBase):
    """TARGET FLIGHT's airtime cell names no machine, but the flight is scored off a launch ramp, so a
    seed handing out only the wheelie/bike class or one of the four poor gliders would leave it
    unwinnable. The Wheelie Bike pin is itself excluded, so it suppresses the draw without satisfying."""

    options = {
        **CT_ONLY,
        "machines_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
        "start_inventory": {KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE: 1},
    }

    _LOCATION = CTLocation.STADIUM_TF_AIRBORNE_15_SECONDS

    def test_unreachable_on_the_excluded_machines_alone(self):
        # Every excluded machine at once still is not enough - this is not just "some machine".
        state = self.state_with()
        for name in sorted(_POOR_GLIDE_MACHINES):
            if not state.has(name, self.player):  # the pinned starter is already in
                state.collect(self.get_item_by_name(name), prevent_sweep=True)
        for name in _GOOD_GLIDE_MACHINES:
            self.assertFalse(
                state.has(name, self.player),
                f"{name} leaked into the state, making this test vacuous",
            )
        self.assertFalse(
            self.reaches(state, self._LOCATION),
            "the airtime cell should not be reachable on the excluded machines",
        )

    def test_reachable_on_each_gliding_machine(self):
        for machine in _GOOD_GLIDE_MACHINES:
            with self.subTest(machine=machine):
                state = self.state_with()
                state.collect(self.get_item_by_name(machine), prevent_sweep=True)
                self.assertTrue(
                    self.reaches(state, self._LOCATION),
                    f"the airtime cell should be reachable on {machine} alone",
                )

    def test_excluded_machines_are_city_trial_machines(self):
        # Guards against a typo'd or non-City-Trial name silently excluding nothing.
        for name in _POOR_GLIDE_MACHINES:
            self.assertIn(name, _CT_MACHINE_UNLOCKS)
        self.assertEqual(len(_POOR_GLIDE_MACHINES), 9)
        self.assertFalse(set(_GOOD_GLIDE_MACHINES) & _POOR_GLIDE_MACHINES)


class TestAirGliderNeedsGlideOrPatches(KARTestBase):
    """Every AIR GLIDER cell scores one launch off the ramp on the machine built in the city, so a seed
    handing out only poor gliders and no Glide Patches would leave the whole stadium unwinnable. The
    Wheelie Bike pin is itself a poor glider, so it suppresses the machine starter draw without
    satisfying the rule. The AP checklist is on so the 2,000-foot cell is covered too."""

    options = {
        **CT_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "machines_gated": Toggle.option_true,
        "city_trial_patches_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
        "start_inventory": {KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE: 1},
    }

    # Every cell the region holds, so a newly added AIR GLIDER box fails here rather than shipping ungated.
    _CELLS = (
        CTLocation.STADIUM_AG_FLY_330_FEET,
        CTLocation.STADIUM_AG_FLY_660_FEET,
        CTLocation.STADIUM_AG_FLY_1300_FEET,
        CTLocation.STADIUM_AG_AIRBORNE_30_SECONDS,
        APLocation.AG_FLY_2000_FEET,
    )

    def test_the_cell_list_is_the_whole_region(self):
        region = self.world.get_region(KARRegion.CITY_TRIAL_STADIUM_AG)
        self.assertEqual({loc.name for loc in region.locations}, set(self._CELLS))

    def _poor_glider_state(self):
        """Every poor glider held at once and nothing that glides - not just "some machine"."""
        state = self.state_with()
        for name in sorted(_POOR_GLIDE_MACHINES):
            if not state.has(name, self.player):  # the pinned starter is already in
                state.collect(self.world.create_item(name), prevent_sweep=True)
        for name in (*_GOOD_GLIDE_MACHINES, KARItemName.UNLOCK_PATCH_GLIDE):
            self.assertFalse(state.has(name, self.player), f"{name} leaked in, making this test vacuous")
        return state

    def test_unreachable_on_the_poor_gliders_alone(self):
        state = self._poor_glider_state()
        for cell in self._CELLS:
            with self.subTest(location=cell):
                self.assertFalse(self.reaches(state, cell), "a machine that cannot glide should not open AIR GLIDER")

    def test_reachable_on_each_gliding_machine(self):
        for machine in _GOOD_GLIDE_MACHINES:
            state = self.state_with(machine)
            for cell in self._CELLS:
                with self.subTest(machine=machine, location=cell):
                    self.assertTrue(self.reaches(state, cell), f"{cell} should be reachable on {machine} alone")

    def test_the_glide_patch_carries_a_poor_glider(self):
        state = self._poor_glider_state()
        state.collect(self.world.create_item(KARItemName.UNLOCK_PATCH_GLIDE), prevent_sweep=True)
        for cell in self._CELLS:
            with self.subTest(location=cell):
                self.assertTrue(self.reaches(state, cell), f"{cell} should be reachable on Glide Patches alone")


# Every named TR cell whose item has a copy-ability stand-in, read off the production tables so a new
# pairing is covered without editing this file.
_TR_EITHER_KEY_CELLS = [
    (location, tr_item, _TR_ABILITY_ITEM_KEYS[tr_item])
    for location, tr_item in _TR_ITEM_LOCATION_RULES.items()
    if tr_item in _TR_ABILITY_ITEM_KEYS
]


class TestTRAbilityItemEitherKey(KARTestBase):
    """Both gates ON: an ability-themed TR item accepts either key -- its own TR item unlock or the
    matching copy ability unlock -- so a cell needing that item to spawn is reachable with either alone
    and unreachable with neither."""

    options = {**ALL_MODES, "abilities_gated": Toggle.option_true, "top_ride_items_gated": Toggle.option_true}

    def test_either_key_alone_suffices(self):
        # Two single-item groups: unreachable with neither key, reachable with each on its own.
        for location, tr_item, ability in _TR_EITHER_KEY_CELLS:
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[tr_item], [ability]], only_check_listed=True)

    def test_freeze_fan_is_keyed_only_through_the_generic_count(self):
        # Non-vacuity for the pairing table: Freeze Fan is the fourth ability-themed item but no cell
        # names it, so its stand-in is only ever exercised by the "any item type" cells.
        named = {tr_item for _, tr_item, _ in _TR_EITHER_KEY_CELLS}
        self.assertEqual(set(_TR_ABILITY_ITEM_KEYS) - named, {str(KARItemName.UNLOCK_TR_ITEM_FREEZE_FAN)})


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
    """A color spawns only while its own unlock is held and its contents pool still holds something, so
    each per-color count needs the color plus a key to that pool. Red also accepts a legendary piece,
    whose carrier box the game spawns without consulting the color picker."""

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
        # All Up's City Trial fall chance is zero, so it never joins the blue pool on its own and must
        # not make blue boxes spawn.
        withheld = [
            *items_of_type(KARItemType.CT_PATCH_UNLOCK),
            *_BLUE_BOX_FOOD_ITEMS,
            KARItemName.UNLOCK_ITEM_ALL_UP,
        ]
        state = self.state_without(withheld)
        for item in self.get_items_by_name(KARItemName.UNLOCK_ITEM_ALL_UP):
            state.collect(item)
        self.assertFalse(
            self.reaches(state, APLocation.BREAK_20_BLUE_BOXES),
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


class TestARRootCourseGating(KARTestBase):
    """air_ride_courses_gated ON: mode-root Air Ride cells need at least one course, since you cannot
    race without one. The pinned starter normally satisfies that, so each case removes it to expose the
    rule."""

    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true, **_PIN_AR_COURSE_STARTER}

    # Cells needing an enemy on the course, which Nebula Belt has none of. The ability-named ones need
    # their ability unlock too, so they are covered separately below.
    _ENEMY_LOCATIONS = (
        ARLocation.SWALL_200_ENEMIES,
        ARLocation.SWALL_5_GARBAGE_AND_FIRST,
        ARLocation.DEFEAT_300_OF_YOUR_ENEMIES,
        ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
    )

    def test_root_location_needs_any_course(self):
        # REACH_GOAL_3X_NOT_FR is a mode-root cell with no other gating - just cross the line.
        loc = ARLocation.REACH_GOAL_3X_NOT_FR
        self.assertTrue(self.can_reach_location(loc))  # pinned Fantasy Meadows starter present
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.assertFalse(self.can_reach_location(loc))  # no course in state
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT))
        self.assertTrue(self.can_reach_location(loc))  # any course, even the secret one, restores it

    def test_enemy_locations_need_more_than_nebula_belt(self):
        """Nebula Belt spawns no enemies, so it alone leaves every enemy-dependent cell unreachable."""
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT))
        for loc in self._ENEMY_LOCATIONS:
            with self.subTest(location=loc):
                self.assertFalse(self.can_reach_location(loc))
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE))
        for loc in self._ENEMY_LOCATIONS:
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))

    def test_ability_location_needs_an_enemy_or_panel_course(self):
        """An ability cell needs a course that either spawns its enemy or carries a ground copy panel.
        Celestial Valley is the one standard course with no Phan Phan and no Dayl, but it carries the
        tree panel; Machine Passage is the plain enemy case."""
        loc = ARLocation.FIRST_WITH_FIRE_ABILITY
        self.collect(self.world.create_item(KARItemName.UNLOCK_ABILITY_FIRE))
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.assertFalse(self.can_reach_location(loc))
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY))
        self.assertTrue(self.can_reach_location(loc))
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY)])
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE))
        self.assertTrue(self.can_reach_location(loc))

    def test_nebula_belt_grants_abilities_despite_having_no_enemies(self):
        """Nebula Belt spawns nothing to swallow but ships four ground copy panels, so it works for every
        ability cell except Tornado's, which also wants 15 enemies defeated."""
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT))
        for loc, item in (
            (ARLocation.FIRST_WITH_FIRE_ABILITY, KARItemName.UNLOCK_ABILITY_FIRE),
            (ARLocation.FIRST_WITH_SLEEP_ABILITY, KARItemName.UNLOCK_ABILITY_SLEEP),
            (ARLocation.FIRST_WITH_WING_ABILITY, KARItemName.UNLOCK_ABILITY_WING),
            (ARLocation.FIRST_WITH_NEEDLE_ABILITY, KARItemName.UNLOCK_ABILITY_NEEDLE),
            (ARLocation.SWORD_CHALLENGE_10_SWINGS, KARItemName.UNLOCK_ABILITY_SWORD),
        ):
            self.collect(self.world.create_item(item))
            with self.subTest(location=loc):
                self.assertTrue(self.can_reach_location(loc))
        self.collect(self.world.create_item(KARItemName.UNLOCK_ABILITY_TORNADO))
        self.assertFalse(self.can_reach_location(ARLocation.TORNADO_CHALLENGE_15_KO))

    def test_needle_ability_excludes_beanstalk_park(self):
        """Beanstalk Park is too short to carry a swallowed ability to the line in 1st."""
        loc = ARLocation.FIRST_WITH_NEEDLE_ABILITY
        self.collect(self.world.create_item(KARItemName.UNLOCK_ABILITY_NEEDLE))
        self.remove([self.world.create_item(KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS)])
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK))
        self.assertFalse(self.can_reach_location(loc))
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_SKY_SANDS))
        self.assertTrue(self.can_reach_location(loc))


class TestARAbilityCellInhaleOrPanel(KARTestBase):
    """base_abilities_gated + air_ride_courses_gated ON: reaching an ability cell by swallowing its enemy
    needs Inhale, but a ground copy panel hands over an ability without one, so a panel course stands in
    for the Inhale unlock. Starter pinned to Beanstalk Park: it spawns Fire's enemy and carries no panel."""

    options = {
        **AR_ONLY,
        "base_abilities_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_true,
        **_PIN_BEANSTALK_STARTER,
    }

    def test_enemy_course_needs_inhale(self):
        loc = ARLocation.FIRST_WITH_FIRE_ABILITY
        self.assertFalse(self.can_reach_location(loc))  # Phan Phan is there, but nothing to swallow with
        self.collect(self.world.create_item(KARItemName.UNLOCK_BASE_ABILITY_INHALE))
        self.assertTrue(self.can_reach_location(loc))

    def test_panel_course_stands_in_for_inhale(self):
        loc = ARLocation.FIRST_WITH_FIRE_ABILITY
        self.assertFalse(self.can_reach_location(loc))
        self.collect(self.world.create_item(KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT))
        self.assertTrue(self.can_reach_location(loc))


class TestTRRootCourseGating(KARTestBase):
    """top_ride_courses_gated ON: the TOP_RIDE-root cell and the mode-level Free Run / Time Attack cells
    all need at least one course. Starter pinned so its removal is deterministic."""

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


_CT_ALL_PROGRESSION_LOCATIONS = {"city_trial_progression": sorted(CITY_TRIAL_PROGRESSION_GROUPS)}


_TR_GENERIC_ITEM_CELLS = (TRLocation.COLLECT_500_ITEMS, TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE)


class _TRItemCountMixin(_MixinBase):
    """The two item-count shapes top_ride_items_gated drives, shared by the gate-on configurations."""

    def assert_18_types_needs_nineteen_unlocks(self):
        # The four ability-themed types accept a copy ability as a second key, but counting both would
        # score one type twice, so the rule reads the 21 TR item unlocks only.
        tr_unlocks = sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK))
        loc = TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS
        state = self.state_without(tr_unlocks[:3])  # 18 held < 19
        self.assertFalse(self.reaches(state, loc))
        state.collect(self.world.create_item(tr_unlocks[0]))  # 19
        self.assertTrue(self.reaches(state, loc))

    def assert_generic_cells_need_any_of(self, keys: list[str]):
        state = self.state_without(keys)
        for loc in _TR_GENERIC_ITEM_CELLS:
            with self.subTest(location=loc, phase="no type"):
                self.assertFalse(self.reaches(state, loc))
        state.collect(self.world.create_item(keys[0]))
        for loc in _TR_GENERIC_ITEM_CELLS:
            with self.subTest(location=loc, phase="one type"):
                self.assertTrue(self.reaches(state, loc))


class TestTRItemGatingBothGates(_TRItemCountMixin, KARTestBase):
    """top_ride_items_gated AND abilities_gated ON: the generic "collect/get items" cells name no
    specific item, so they take any of the 21 TR item unlocks or the four copy abilities that stand in
    for an ability-themed one."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_true}

    def test_18_types_cell_counts_item_unlocks_only(self):
        self.assert_18_types_needs_nineteen_unlocks()

    def test_generic_cells_need_any_type(self):
        self.assert_generic_cells_need_any_of(
            [*sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK)), *sorted(_TR_ABILITY_ITEM_KEYS.values())]
        )


class TestTRItemGatingAbilitiesUngated(_TRItemCountMixin, KARTestBase):
    """top_ride_items_gated ON, abilities OFF: an ungated world's copy abilities are handed out at
    connect and the mod ignores them as a key, so every TR item type is keyed solely by its own unlock."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_true, "abilities_gated": Toggle.option_false}

    def test_18_types_cell_counts_item_unlocks_only(self):
        self.assert_18_types_needs_nineteen_unlocks()

    def test_generic_cells_need_any_item_unlock(self):
        self.assert_generic_cells_need_any_of(sorted(items_of_type(KARItemType.TR_ITEM_UNLOCK)))

    def test_ability_themed_cell_needs_its_tr_item_unlock(self):
        self.assertAccessDependency(
            [TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS],
            [[KARItemName.UNLOCK_TR_ITEM_BOMB]],
            only_check_listed=True,
        )


class TestTRItemGatingNotApplied(KARTestBase):
    """top_ride_items_gated OFF: every TR item type spawns from connect - the three New-Item types via a
    has_reward nudge, the rest as vanilla defaults - so none of the item-count cells carries a rule.
    Abilities stay gated to show the item gate alone decides this."""

    options = {**TR_ONLY, "top_ride_items_gated": Toggle.option_false, "abilities_gated": Toggle.option_true}

    def test_item_count_cells_reachable_empty(self):
        for loc in (TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS, *_TR_GENERIC_ITEM_CELLS):
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

    def test_unreachable_without_red_box(self):
        # The pieces arrive in a red carrier box, so all six unlocks are not enough on their own.
        self.collect_all_but([KARItemName.UNLOCK_BOX_RED])
        self.assertFalse(self.can_reach_location(CTLocation.COMPLETE_DRAGOON_AND_HYDRA))
        self.collect_by_name(KARItemName.UNLOCK_BOX_RED)
        self.assertTrue(self.can_reach_location(CTLocation.COMPLETE_DRAGOON_AND_HYDRA))


class TestCTCompleteDragoonHydraAllGatingOff(KARTestBase):
    """Both gates OFF: nothing keys the pieces or their carrier, so the checkbox is reachable empty."""

    options = {
        **CT_ONLY,
        "city_trial_items_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
    }

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
        # The carrier box is red, so the six pieces alone still do not open the goal.
        self.assertFalse(self.can_reach_location(victory))
        self.collect_by_name(KARItemName.UNLOCK_BOX_RED)
        self.assertTrue(self.can_reach_location(victory))


class TestFill100NonGoalGating(KARTestBase):
    """ "Fill in over 100 Checklist blocks!" is a real in-game meta checkbox, distinct from the synthetic
    N-blocks goal. When it is not the mode's goal it stays a normal location and must carry that same
    requirement, or fill could strand progression behind ~100 checks."""

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
        # Six of seven courses locked, so well under 100 boxes are reachable. Evaluating this also
        # proves the self-excluding count rule terminates.
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


# Archipelago checklist access rules. An AP box inherits the entrance chain of the region it sits in, so
# every class below turns OFF the stadium / course gates that would stack an entrance rule on top of the
# rule under test. They guard on effective_gates, so City Trial needs a goal - hence CT_ONLY as the base.

_AP_ON = {"archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks, "archipelago_checklist_amount": 3}


class TestAPFoodBoxesNeedTheirItemUnlock(KARTestBase):
    """city_trial_items_gated ON: the nine Archipelago food / All Up counters each need that item type
    able to spawn. These are the eight foods the vanilla checklist never covers plus the All Up counter,
    so nothing else in the world pins them."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        **_CT_ALL_PROGRESSION_LOCATIONS,
        "city_trial_items_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_each_box_needs_its_own_item(self):
        for location, unlock in _AP_ITEM_LOCATION_RULES.items():
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[unlock]], only_check_listed=True)

    def test_rule_table_covers_every_uncovered_food(self):
        # Non-vacuity: the loop above proves whatever the table happens to hold, so pin its shape too.
        self.assertIn(APLocation.COLLECT_5_ALL_UPS, _AP_ITEM_LOCATION_RULES)
        self.assertEqual(len(_AP_ITEM_LOCATION_RULES), 9)


class TestAPFoodBoxesUngated(KARTestBase):
    """city_trial_items_gated OFF: every item type spawns from connect, so the food counters carry no
    rule and no item unlock exists to gate them with."""

    options = {**CT_ONLY, **_AP_ON, "city_trial_items_gated": Toggle.option_false}

    def test_boxes_reachable_empty(self):
        for location in _AP_ITEM_LOCATION_RULES:
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))


class TestAPPatchAndAbilityBoxes(KARTestBase):
    """The two patch counters need their patch type, and the Copy Chance Mic box needs the Mic ability.
    None is covered by a vanilla checklist box: HP and Offense are the two stats with no "get 10 patches"
    cell, and Mic is the one ability the wheel can hand over that no vanilla box names."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "city_trial_patches_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_hp_patch_box_needs_hp_patch_unlock(self):
        self.assertAccessDependency(
            [APLocation.GET_10_HP_PATCHES],
            [[KARItemName.UNLOCK_PATCH_HP]],
            only_check_listed=True,
        )

    def test_offense_patch_box_needs_offense_patch_unlock(self):
        self.assertAccessDependency(
            [APLocation.GET_10_OFFENSE_PATCHES],
            [[KARItemName.UNLOCK_PATCH_OFFENSE]],
            only_check_listed=True,
        )

    def test_the_two_counters_cover_the_stats_vanilla_misses(self):
        # Non-vacuity: every other patch type is counted on the City Trial checklist, so these two
        # are exactly the gap the AP tab fills. A new vanilla-covered counter here would be a duplicate.
        vanilla_counted = set(_PATCH_LOCATION_RULES.values())
        ap_counted = {KARItemName.UNLOCK_PATCH_HP, KARItemName.UNLOCK_PATCH_OFFENSE}
        self.assertFalse(vanilla_counted & ap_counted)
        self.assertEqual(vanilla_counted | ap_counted, set(items_of_type(KARItemType.CT_PATCH_UNLOCK)))

    def test_copy_chance_mic_box_needs_mic(self):
        # The wheel hands the ability over in the city, so this one needs no Inhale - unlike the melee
        # box, which has no copy panel to draw from.
        self.assertAccessDependency(
            [APLocation.GET_MIC_FROM_COPY_CHANCE],
            [[KARItemName.UNLOCK_ABILITY_MIC]],
            only_check_listed=True,
        )


class TestAPMicKirbyMeleeBoxNeedsBothKeys(KARTestBase):
    """The melee Mic box composes the two halves: the ability itself AND Inhale, since neither melee
    stage spawns a copy panel and the only Mic in there is a swallowed Walky. machines_gated is OFF so
    the combat-damage entrance rule on KIRBY MELEE drops out and the box's own rule is isolated."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "abilities_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_true,
        "machines_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_needs_mic_and_inhale(self):
        location = APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY
        keys = [KARItemName.UNLOCK_ABILITY_MIC, KARItemName.UNLOCK_BASE_ABILITY_INHALE]
        base = self.state_without(keys)

        def reachable(*items: str) -> bool:
            state = base.copy()
            for name in items:
                state.collect(self.world.create_item(name))
            return self.reaches(state, location)

        self.assertFalse(reachable(), "reachable with neither key")
        self.assertFalse(reachable(KARItemName.UNLOCK_ABILITY_MIC), "reachable with Mic but no Inhale")
        self.assertFalse(reachable(KARItemName.UNLOCK_BASE_ABILITY_INHALE), "reachable with Inhale but no Mic")
        self.assertTrue(reachable(*keys), "not reachable with both keys")


class TestAPKirbyMelee1HundredKOBox(KARTestBase):
    """The KIRBY MELEE 1 100-KO box needs one of Sword, Needle, Tornado or Plasma, and Inhale to swallow its
    enemy, as KM1 spawns no copy panels. machines_gated is OFF so the combat-damage entrance rule on KIRBY
    MELEE drops out and the box's own rule is isolated."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "abilities_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_true,
        "machines_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    abilities = (
        KARItemName.UNLOCK_ABILITY_SWORD,
        KARItemName.UNLOCK_ABILITY_NEEDLE,
        KARItemName.UNLOCK_ABILITY_TORNADO,
        KARItemName.UNLOCK_ABILITY_PLASMA,
    )

    def test_needs_any_of_the_four_abilities(self):
        self.assertAccessDependency(
            [APLocation.KM1_KO_100_ENEMIES_BY_YOURSELF],
            [[ability] for ability in self.abilities],
            only_check_listed=True,
        )

    def test_needs_inhale_alongside_the_ability(self):
        location = APLocation.KM1_KO_100_ENEMIES_BY_YOURSELF
        inhale = KARItemName.UNLOCK_BASE_ABILITY_INHALE
        base = self.state_without([*self.abilities, inhale])

        def reachable(*items: str) -> bool:
            state = base.copy()
            for name in items:
                state.collect(self.world.create_item(name))
            return self.reaches(state, location)

        self.assertFalse(reachable(inhale), "reachable with Inhale but no ability")
        for ability in self.abilities:
            with self.subTest(ability=ability):
                self.assertFalse(reachable(ability), "reachable with the ability but no Inhale")
                self.assertTrue(reachable(ability, inhale), "not reachable with the ability and Inhale")


class TestAPPurpleKirbyBox(KARTestBase):
    """colors_gated ON: the "finish 1st three times as Purple Kirby" box needs Purple specifically, not
    any color. The starter is pinned to Pink so the random pick cannot be Purple."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "colors_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
        **_PIN_COLOR_STARTER,
    }

    def test_box_needs_purple(self):
        self.assertAccessDependency(
            [APLocation.SR1_FINISH_1ST_3X_AS_PURPLE],
            [[KARItemName.UNLOCK_COLOR_PURPLE]],
            only_check_listed=True,
        )


# Jet Star is named by none of the character / Nebula boxes below, so pinning it suppresses the random
# machine pick without satisfying any rule under test.
_PIN_JET_STAR_STARTER = {"start_inventory": {KARItemName.UNLOCK_MACHINE_JET_STAR: 1}}


class TestAPCharacterAndNamedMachineBoxes(KARTestBase):
    """machines_gated ON: the AP boxes that name a machine or a character need that machine's unlock.
    Both character grids (Air Ride's and the City Trial stadium one) resolve a character through its
    machine, so Meta Knight's and Dedede's machine unlocks are what make them selectable."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "machines_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
        **_PIN_JET_STAR_STARTER,
    }

    _NAMED = (
        (APLocation.AIR_RIDE_1ST_AS_META_KNIGHT, KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT),
        (APLocation.AIR_RIDE_1ST_AS_KING_DEDEDE, KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE),
        (APLocation.DD_KO_10_KIRBYS_AS_KING_DEDEDE, KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE),
        (APLocation.NEBULA_BELT_1ST_ON_WHEELIE_SCOOTER, KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER),
        (APLocation.SR1_FINISH_1ST_ON_BULK_STAR, KARItemName.UNLOCK_MACHINE_BULK_STAR),
    )

    def test_each_named_box_needs_its_machine(self):
        for location, machine in self._NAMED:
            with self.subTest(location=location):
                self.assertAccessDependency([location], [[machine]], only_check_listed=True)

    def test_the_nebula_glide_box_takes_any_of_its_three_machines(self):
        # The mod counts the 10-second glide only on the machines the cell names.
        self.assertAccessDependency(
            [APLocation.NEBULA_BELT_AIRBORNE_10_SECONDS],
            [[machine] for machine in _CT_FLIGHT_MACHINES],
            only_check_listed=True,
        )

    def test_character_machine_rewards_are_not_a_second_key(self):
        # The vanilla checklist rewards that grant Meta Knight / Dedede are listed as machines_gated
        # overlapping_rewards, so they are out of the pool entirely and cannot open these boxes.
        world_items = self.world_item_names()
        for reward in (KARItemName.AR_REWARD_META_KNIGHT, KARItemName.AR_REWARD_KING_DEDEDE):
            self.assertNotIn(reward, world_items)


class TestAPFantasyMeadowsShortcutNeedsAGlidingMachine(KARTestBase):
    """The shortcut is an arc 40-60 units above the racing line, so reaching it means holding a glide,
    which the wheelie/bike class cannot. The box names no machine, so without this rule any machine at
    all would appear to do. The Wheelie Bike pin is itself excluded."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "machines_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
        "start_inventory": {KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE: 1},
    }

    _LOCATION = APLocation.FANTASY_MEADOWS_TAKE_SHORTCUT

    def test_unreachable_on_the_excluded_machines_alone(self):
        state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
        for name in sorted(_FM_SHORTCUT_EXCLUDED_MACHINES):
            state.collect(self.world.create_item(name))
        self.assertFalse(
            self.reaches(state, self._LOCATION),
            "the shortcut should not be reachable on the wheelie/bike class",
        )

    def test_reachable_on_each_gliding_machine(self):
        for machine in _FM_SHORTCUT_MACHINES:
            with self.subTest(machine=machine):
                state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
                state.collect(self.world.create_item(machine))
                self.assertTrue(
                    self.reaches(state, self._LOCATION),
                    f"the shortcut should be reachable on {machine} alone",
                )

    def test_excluded_machines_are_air_ride_machines(self):
        # Guards against a typo'd or non-Air-Ride name silently excluding nothing.
        for name in _FM_SHORTCUT_EXCLUDED_MACHINES:
            self.assertIn(name, _AR_MACHINE_UNLOCKS)
        self.assertEqual(len(_FM_SHORTCUT_EXCLUDED_MACHINES), 4)
        self.assertFalse(set(_FM_SHORTCUT_MACHINES) & _FM_SHORTCUT_EXCLUDED_MACHINES)


class TestCityAnyMachineCells(KARTestBase):
    """base_abilities_gated OFF: the "you need something to ride" City Trial cells - breaking the coral,
    reaching the sky garden or Castle Hall's roof, and the two mileage counters - take any City Trial
    machine, so every one of them opens all five on its own."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "machines_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_unreachable_with_no_machine(self):
        state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
        for location in _CT_ANY_MACHINE_LOCATIONS:
            with self.subTest(location=location):
                self.assertFalse(self.reaches(state, location))

    def test_any_city_trial_machine_opens_them(self):
        for machine in _CT_MACHINE_UNLOCKS:
            state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
            state.collect(self.world.create_item(machine))
            for location in _CT_ANY_MACHINE_LOCATIONS:
                with self.subTest(machine=machine, location=location):
                    self.assertTrue(self.reaches(state, location))

    def test_top_ride_machines_are_not_a_city_ride(self):
        # Free and Steer Star are Top Ride controls; _CT_MACHINE_UNLOCKS is derived from source_modes so
        # they must not appear in it, and holding both must not open a City Trial box.
        state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
        for name in (KARItemName.UNLOCK_MACHINE_FREE_STAR, KARItemName.UNLOCK_MACHINE_STEER_STAR):
            self.assertNotIn(name, _CT_MACHINE_UNLOCKS)
            state.collect(self.world.create_item(name))
        self.assertFalse(self.reaches(state, APLocation.BREAK_ALL_CORAL))


class TestAPCityMachineBoxesChargeSplit(KARTestBase):
    """machines AND base abilities both gated: Hydra and Bulk Star barely move without a charge boost and
    Slick / Turbo Star only turn by charge-drifting, so those count as a ride only alongside Charge. The
    rule splits into "a steerable machine" OR "Charge AND a charge-dependent machine"."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "machines_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_true,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    _LOCATION = APLocation.BREAK_ALL_CORAL

    def _reachable(self, *names: str) -> bool:
        state = self.state_without(
            items_of_type(KARItemType.MACHINE_UNLOCK) | {str(KARItemName.UNLOCK_BASE_ABILITY_CHARGE)}
        )
        for name in names:
            state.collect(self.world.create_item(name))
        return self.reaches(state, self._LOCATION)

    def test_the_split_is_non_trivial(self):
        # Both halves have to be non-empty or the two tests below prove nothing.
        self.assertTrue(_STEERABLE_CT_MACHINES)
        self.assertTrue(_CHARGE_DEPENDENT_CT_MACHINES)
        self.assertFalse(set(_STEERABLE_CT_MACHINES) & set(_CHARGE_DEPENDENT_CT_MACHINES))

    def test_nothing_and_charge_alone_do_not_suffice(self):
        self.assertFalse(self._reachable(), "reachable with no machine at all")
        self.assertFalse(
            self._reachable(KARItemName.UNLOCK_BASE_ABILITY_CHARGE),
            "Charge is not a ride on its own",
        )

    def test_each_steerable_machine_suffices_alone(self):
        for machine in _STEERABLE_CT_MACHINES:
            with self.subTest(machine=machine):
                self.assertTrue(self._reachable(machine), f"{machine} should be rideable without Charge")

    def test_charge_dependent_machines_need_charge(self):
        for machine in _CHARGE_DEPENDENT_CT_MACHINES:
            with self.subTest(machine=machine):
                self.assertFalse(self._reachable(machine), f"{machine} should not be a ride without Charge")
                self.assertTrue(
                    self._reachable(machine, KARItemName.UNLOCK_BASE_ABILITY_CHARGE),
                    f"{machine} should be a ride once Charge is in",
                )


class TestAPFlyToHighestPointNeedsFlight(KARTestBase):
    """Touching the city's ceiling is not just "have a ride": the box needs the Dragoon, the Flight Warp
    Star or the Winged Star, the only City Trial machines that climb that high."""

    options = {
        **CT_ONLY,
        **_AP_ON,
        "machines_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    _LOCATION = APLocation.FLY_TO_HIGHEST_POINT

    def _reachable_with(self, machine: str) -> bool:
        state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
        state.collect(self.world.create_item(machine))
        return self.reaches(state, self._LOCATION)

    def test_the_flight_set_is_a_strict_subset(self):
        # Non-vacuity: a typo'd name or the whole machine list would make the loops below prove nothing.
        self.assertEqual(len(_CT_FLIGHT_MACHINES), 3)
        self.assertTrue(set(_CT_FLIGHT_MACHINES) < set(_CT_MACHINE_UNLOCKS))

    def test_unreachable_with_no_machine(self):
        state = self.state_without(items_of_type(KARItemType.MACHINE_UNLOCK))
        self.assertFalse(self.reaches(state, self._LOCATION))

    def test_each_flight_machine_suffices_alone(self):
        for machine in _CT_FLIGHT_MACHINES:
            with self.subTest(machine=machine):
                self.assertTrue(self._reachable_with(machine), f"{machine} should reach the ceiling on its own")

    def test_grounded_machines_do_not_suffice(self):
        for machine in _CT_MACHINE_UNLOCKS:
            if machine in _CT_FLIGHT_MACHINES:
                continue
            with self.subTest(machine=machine):
                self.assertFalse(self._reachable_with(machine), f"{machine} should not reach the ceiling")


class TestAssembleBoxesFreeWhenPiecesUngatedWithoutCityTrial(KARTestBase):
    """No City Trial goal and a plain block count for Archipelago: no sphere is a goal key, so none is
    minted and both "assemble" boxes are free. A rule read off the raw option would instead ask for six
    items that do not exist."""

    options = {
        **TR_ONLY,
        **_AP_ON,
        "city_trial_items_gated": Toggle.option_true,
    }

    def test_no_sphere_is_minted(self):
        pool = self.world_item_names()
        for name in AP_STAR_PIECE_UNLOCK_ITEMS:
            with self.subTest(item=name):
                self.assertNotIn(name, pool)

    def test_assemble_boxes_reachable_with_nothing(self):
        for location in (APLocation.ASSEMBLE_ARCHIPELAGO_STAR, APLocation.ASSEMBLE_ALL_THREE_LEGENDARIES):
            with self.subTest(location=location):
                self.assertTrue(self.can_reach_location(location))
