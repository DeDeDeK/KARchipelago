import typing

from rule_builder.rules import CanReachLocation, Has, HasAll, HasAny, Rule

from .KARItems import STADIUM_UNLOCK_TO_CHECKLIST_REWARD, KARItemName
from .KARLocations import ARLocation, CTLocation, TRLocation
from .KARRegions import (
    AR_COURSE_REGION_TO_UNLOCK,
    STADIUM_ALL_REGION_TO_UNLOCKS,
    STADIUM_REGION_TO_UNLOCK,
    TR_COURSE_REGION_TO_UNLOCK,
    KARRegion,
)

if typing.TYPE_CHECKING:
    from . import KARWorld

# Event-dependent CT locations (when city_trial_events_gated is ON)
_EVENT_LOCATION_RULES: dict[str, str] = {
    CTLocation.DO_SOME_DAMAGE_TO_DYNA_BLADE: KARItemName.UNLOCK_EVENT_DYNA_BLADE,
    CTLocation.GET_TRAMPLED_BY_DYNA_BLADE: KARItemName.UNLOCK_EVENT_DYNA_BLADE,
    CTLocation.STEAL_8_FROM_TAC: KARItemName.UNLOCK_EVENT_TAC,
    CTLocation.THE_METEOR_ATTACKS_CITY_3: KARItemName.UNLOCK_EVENT_METEOR,
    CTLocation.BREAK_5_OF_HUGE_PILLARS_THAT_APPEAR: KARItemName.UNLOCK_EVENT_PILLAR,
    CTLocation.BREAK_PILLAR_WITHIN_40S: KARItemName.UNLOCK_EVENT_PILLAR,
    CTLocation.USE_UP_ONE_OF_RESTORATION_AREAS: KARItemName.UNLOCK_EVENT_RESTORATION_AREA,
    CTLocation.ENTER_CASTLE_CHAMBER: KARItemName.UNLOCK_EVENT_SECRET_CHAMBER,
}

# Ability-dependent locations (when abilities_gated is ON)
_ABILITY_LOCATION_RULES: dict[str, str] = {
    # City Trial
    CTLocation.COPY_CHANCE_WHEEL_BOMB: KARItemName.UNLOCK_ABILITY_BOMB,
    CTLocation.COPY_CHANCE_WHEEL_SLEEP: KARItemName.UNLOCK_ABILITY_SLEEP,
    # Air Ride
    ARLocation.FIRST_WITH_WING_ABILITY: KARItemName.UNLOCK_ABILITY_WING,
    ARLocation.FIRST_WITH_SLEEP_ABILITY: KARItemName.UNLOCK_ABILITY_SLEEP,
    ARLocation.FIRST_WITH_FIRE_ABILITY: KARItemName.UNLOCK_ABILITY_FIRE,
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: KARItemName.UNLOCK_ABILITY_NEEDLE,
    ARLocation.TORNADO_CHALLENGE_15_KO: KARItemName.UNLOCK_ABILITY_TORNADO,
    ARLocation.SWORD_CHALLENGE_10_SWINGS: KARItemName.UNLOCK_ABILITY_SWORD,
}

# Machine-dependent locations requiring a SINGLE specific machine (when machines_gated is ON)
_MACHINE_SINGLE_RULES: dict[str, str] = {
    # CT stadium locations requiring specific machines
    CTLocation.STADIUM_DR1_17_00_FORMULA: KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
    CTLocation.STADIUM_DR3_31_00_WHEELIE_BIKE: KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
    CTLocation.STADIUM_DR2_27_00_WAGON: KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    CTLocation.STADIUM_DR4_33_00_TURBO: KARItemName.UNLOCK_MACHINE_TURBO_STAR,
    CTLocation.STADIUM_DR2_29_00_WINGED: KARItemName.UNLOCK_MACHINE_WINGED_STAR,
    CTLocation.STADIUM_DR4_24_00_REX: KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
    CTLocation.STADIUM_DR1_26_00_WARPSTAR: KARItemName.UNLOCK_MACHINE_WARP_STAR,
    CTLocation.STADIUM_DR3_28_00_SWERVE: KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
    # AR locations requiring specific machines
    ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR: KARItemName.UNLOCK_MACHINE_SHADOW_STAR,
    ARLocation.TA_SS_FINISH_02_40_00_ON_WAGON_STAR: KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    ARLocation.FR_FM_LAP_00_23_00_ON_WAGON_STAR: KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR: KARItemName.UNLOCK_MACHINE_SLICK_STAR,
    ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR: KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
    ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR: KARItemName.UNLOCK_MACHINE_TURBO_STAR,
    ARLocation.FR_BP_LAP_00_58_00_ON_WINGED_STAR: KARItemName.UNLOCK_MACHINE_WINGED_STAR,
    ARLocation.FR_CK_LAP_01_25_00_ON_ROCKET_STAR: KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
    ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR: KARItemName.UNLOCK_MACHINE_BULK_STAR,
    ARLocation.FR_MP_LAP_00_57_00_ON_SWERVE_STAR: KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
    ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR: KARItemName.UNLOCK_MACHINE_SLICK_STAR,
    ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR: KARItemName.UNLOCK_MACHINE_JET_STAR,
    ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR: KARItemName.UNLOCK_MACHINE_TURBO_STAR,
    ARLocation.TA_BP_FINISH_03_00_00_ON_ROCKET_STAR: KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
    ARLocation.TA_MP_FINISH_02_50_00_ON_REX_WHEELIE: KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
    ARLocation.TA_CK_FINISH_03_55_00_ON_WARPSTAR: KARItemName.UNLOCK_MACHINE_WARP_STAR,
}

# Machine-dependent locations requiring TWO specific machines (bust X while riding Y)
_MACHINE_PAIR_RULES: dict[str, tuple[str, str]] = {
    CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR: (
        KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
        KARItemName.UNLOCK_MACHINE_WARP_STAR,
    ),
    CTLocation.BUST_SLICK_STAR_ON_FORMULA_STAR: (
        KARItemName.UNLOCK_MACHINE_SLICK_STAR,
        KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
    ),
    CTLocation.BUST_SWERVE_STAR_ON_WHEELIE_BIKE: (
        KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
        KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
    ),
    CTLocation.BUST_ROCKET_STAR_ON_SLICK_STAR: (
        KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
        KARItemName.UNLOCK_MACHINE_SLICK_STAR,
    ),
    CTLocation.BUST_WARPSTAR_ON_SWERVE_STAR: (
        KARItemName.UNLOCK_MACHINE_WARP_STAR,
        KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
    ),
    CTLocation.BUST_TURBO_STAR_ON_ROCKET_STAR: (
        KARItemName.UNLOCK_MACHINE_TURBO_STAR,
        KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
    ),
    CTLocation.BUST_WHEELIE_SCOOTER_ON_COMPACT_STAR: (
        KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER,
        KARItemName.UNLOCK_MACHINE_COMPACT_STAR,
    ),
    CTLocation.BUST_FORMULA_STAR_ON_TURBO_STAR: (
        KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
        KARItemName.UNLOCK_MACHINE_TURBO_STAR,
    ),
}

# Item-dependent CT locations (when city_trial_items_gated is ON)
_ITEM_LOCATION_RULES: dict[str, str] = {
    CTLocation.EAT_3_HOT_DOGS: KARItemName.UNLOCK_ITEM_HOT_DOG,
    CTLocation.EAT_3_PLATES_OF_SUSHI: KARItemName.UNLOCK_ITEM_SUSHI,
    CTLocation.EAT_2_MAXIM_TOMATOES: KARItemName.UNLOCK_ITEM_MAXIM_TOMATO,
    CTLocation.DRINK_3_ENERGY_DRINKS: KARItemName.UNLOCK_ITEM_ENERGY_DRINK,
    CTLocation.USE_FIREWORKS_TO_KO_RIVALS_10X: KARItemName.UNLOCK_ITEM_FIREWORKS,
    CTLocation.USE_SENSOR_BOMBS_TO_KO_RIVALS_3X: KARItemName.UNLOCK_ITEM_SENSOR_BOMB,
    CTLocation.USE_GOLD_SPIKES_TO_KO_RIVALS_3X: KARItemName.UNLOCK_ITEM_GORDO,
}

# Patch-dependent CT locations (when city_trial_patches_gated is ON)
_PATCH_LOCATION_RULES: dict[str, str] = {
    CTLocation.GET_10_BOOST_PATCHES: KARItemName.UNLOCK_PATCH_ACCEL,
    CTLocation.GET_10_TURN_PATCHES: KARItemName.UNLOCK_PATCH_TURN,
    CTLocation.GET_10_WEIGHT_PATCHES: KARItemName.UNLOCK_PATCH_WEIGHT,
    CTLocation.GET_10_GLIDE_PATCHES: KARItemName.UNLOCK_PATCH_GLIDE,
    CTLocation.GET_30_GLIDE_PATCHES: KARItemName.UNLOCK_PATCH_GLIDE,
    CTLocation.GET_10_TOP_SPEED_PATCHES: KARItemName.UNLOCK_PATCH_TOP_SPEED,
    CTLocation.GET_10_CHARGE_PATCHES: KARItemName.UNLOCK_PATCH_CHARGE,
    CTLocation.GET_10_DEFENSE_PATCHES: KARItemName.UNLOCK_PATCH_DEFENSE,
}

# TR item-dependent locations (when top_ride_items_gated is ON).
# TR items tied to copy abilities (Freeze Fan, Fire, Bomb, Walky) are gated
# by the ability unlock in the mod, not by topride_item_unlocked_mask, so the
# corresponding locations are gated via _ABILITY_TR_ITEM_RULES below (under
# abilities_gated), not here.
_TR_ITEM_LOCATION_RULES: dict[str, str] = {
    TRLocation.FIRST_WHILE_HOLDING_HAMMER: KARItemName.UNLOCK_TR_ITEM_HAMMER,
    TRLocation.GET_20_INVINCIBLE_CANDY_ITEMS: KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY,
    TRLocation.BUZZ_SAW_SEND_3_RIVALS: KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW,
}

# TR locations that depend on ability-themed TR items (Fire, Bomb, etc.).
# Applied when abilities_gated is ON: the ability unlock is the gate for both
# the Air-Ride ability and the corresponding Top-Ride item.
_ABILITY_TR_ITEM_RULES: dict[str, str] = {
    TRLocation.FIRE_FIRST_WHILE_HOLDING_FIRE_ITEM: KARItemName.UNLOCK_ABILITY_FIRE,
    TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM: KARItemName.UNLOCK_ABILITY_FIRE,
    TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS: KARItemName.UNLOCK_ABILITY_BOMB,
}


def set_rules(world: "KARWorld"):
    """
    Define the logic rules for locations in Kirby Air Ride.
    Rules are only set for locations if they are present in the world.

    :param world: Kirby Air Ride game world.
    """

    # Accumulate rules per entrance/location across all passes, then apply once at the end.
    # This is required because world.set_rule() resolves the Rule into a Rule.Resolved object,
    # and Resolved does not subclass Rule, so a follow-up `existing & new` compose would silently
    # fall through and overwrite. Building one composed Rule per spot before set_rule avoids it.
    entrance_rules: dict[str, Rule] = {}
    location_rules: dict[str, Rule] = {}

    def add_entrance_rule(entrance_name: str, rule: Rule) -> None:
        existing = entrance_rules.get(entrance_name)
        entrance_rules[entrance_name] = existing & rule if existing is not None else rule

    def add_location_rule(location_name: str, rule: Rule) -> None:
        # Skip silently if the location doesn't exist (mode disabled, location excluded, etc.).
        try:
            world.get_location(location_name)
        except KeyError:
            return
        existing = location_rules.get(location_name)
        location_rules[location_name] = existing & rule if existing is not None else rule

    # Entrance rules: stadium sub-region prerequisites (location-based chains)
    if world.city_trial_enabled:
        add_entrance_rule(
            f"{KARRegion.STADIUM_DD_ALL} -> {KARRegion.STADIUM_DD3}",
            CanReachLocation(CTLocation.STADIUM_DD2_KO_A_RIVAL_10X),
        )
        add_entrance_rule(
            f"{KARRegion.STADIUM_DD_ALL} -> {KARRegion.STADIUM_DD4}",
            CanReachLocation(CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5),
        )
        add_entrance_rule(
            f"{KARRegion.STADIUM_DD_ALL} -> {KARRegion.STADIUM_DD5}",
            CanReachLocation(CTLocation.STADIUM_DD4_KO_A_RIVAL_10X),
        )
        add_entrance_rule(
            f"{KARRegion.CITY_TRIAL} -> {KARRegion.STADIUM_DR4}",
            CanReachLocation(CTLocation.STADIUM_DR3_FINISH_00_27_00),
        )
        add_entrance_rule(
            f"{KARRegion.STADIUM_KM_ALL} -> {KARRegion.STADIUM_KM2}",
            CanReachLocation(CTLocation.STADIUM_KM1_KO_75_ENEMIES_BY_YOURSELF),
        )

    # Entrance rules: Nebula Belt (gated by location prerequisite)
    if world.air_ride_enabled:
        nebula_belt_rule = CanReachLocation(ARLocation.RACE_100_LAPS)
        add_entrance_rule(f"{KARRegion.AIR_RIDE} -> {KARRegion.AR_NEBULA_BELT}", nebula_belt_rule)
        add_entrance_rule(f"{KARRegion.AR_TIME_ATTACK} -> {KARRegion.AR_TA_NEBULA_BELT}", nebula_belt_rule)
        add_entrance_rule(f"{KARRegion.AR_FREE_RUN} -> {KARRegion.AR_FR_NEBULA_BELT}", nebula_belt_rule)

    # Entrance rules: progressive stadiums (when enabled)
    if world.city_trial_enabled and world.options.city_trial_progressive_stadiums:
        for region in world.get_regions():
            if region.name in STADIUM_REGION_TO_UNLOCK and region.entrances:
                unlock = STADIUM_REGION_TO_UNLOCK[region.name]
                item = STADIUM_UNLOCK_TO_CHECKLIST_REWARD.get(unlock, unlock)
                add_entrance_rule(region.entrances[0].name, Has(item))
            elif region.name in STADIUM_ALL_REGION_TO_UNLOCKS and region.entrances:
                unlocks = STADIUM_ALL_REGION_TO_UNLOCKS[region.name]
                items = [STADIUM_UNLOCK_TO_CHECKLIST_REWARD.get(u, u) for u in unlocks]
                add_entrance_rule(region.entrances[0].name, HasAny(*items))

    # Entrance rules: AR course unlocks (when enabled)
    if world.air_ride_enabled and world.options.air_ride_courses_gated:
        for region in world.get_regions():
            if region.name in AR_COURSE_REGION_TO_UNLOCK and region.entrances:
                add_entrance_rule(region.entrances[0].name, Has(AR_COURSE_REGION_TO_UNLOCK[region.name]))

    # Entrance rules: TR course unlocks (when enabled)
    if world.top_ride_enabled and world.options.top_ride_courses_gated:
        for region in world.get_regions():
            if region.name in TR_COURSE_REGION_TO_UNLOCK and region.entrances:
                add_entrance_rule(region.entrances[0].name, Has(TR_COURSE_REGION_TO_UNLOCK[region.name]))

    # Location rules: CT prerequisite chains (always applied when CT enabled)
    add_location_rule(
        CTLocation.UNLOCK_HYDRA_CHECKLIST,
        CanReachLocation(CTLocation.DESTROY_ALL_HOUSES)
        & CanReachLocation(CTLocation.STADIUM_DD_ALL_KO_ENEMIES_150X)
        & CanReachLocation(CTLocation.STADIUM_KM_ALL_KO_1500_ENEMIES),
    )

    add_location_rule(
        CTLocation.UNLOCK_DRAGOON_CHECKLIST,
        CanReachLocation(CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_1000_FEET)
        & CanReachLocation(CTLocation.FLY_THROUGH_RINGS_IN_SKY_5X)
        & CanReachLocation(CTLocation.STADIUM_AG_FLY_1300_FEET),
    )

    # Location rules: AR prerequisite chains (always applied when AR enabled)
    add_location_rule(
        ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR,
        CanReachLocation(ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN),
    )
    add_location_rule(
        ARLocation.TA_SS_FINISH_02_40_00_ON_WAGON_STAR,
        CanReachLocation(ARLocation.REACH_GOAL_3X_NOT_FR),
    )
    add_location_rule(
        ARLocation.FR_FM_LAP_00_23_00_ON_WAGON_STAR,
        CanReachLocation(ARLocation.REACH_GOAL_3X_NOT_FR),
    )
    add_location_rule(
        ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR,
        CanReachLocation(ARLocation.TA_FH_FINISH_03_14_00),
    )
    add_location_rule(
        ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
        CanReachLocation(ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00),
    )
    add_location_rule(
        ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR,
        CanReachLocation(ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00),
    )
    add_location_rule(
        ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR,
        CanReachLocation(ARLocation.MF_USE_ALL_VOLCANO_RAILS_AND_FIRST),
    )
    add_location_rule(
        ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR,
        CanReachLocation(ARLocation.MF_USE_ALL_VOLCANO_RAILS_AND_FIRST),
    )
    add_location_rule(
        ARLocation.TA_BP_FINISH_03_00_00_ON_ROCKET_STAR,
        CanReachLocation(ARLocation.FR_MP_LAP_01_05_00),
    )
    add_location_rule(
        ARLocation.FR_CK_LAP_01_25_00_ON_ROCKET_STAR,
        CanReachLocation(ARLocation.FR_MP_LAP_01_05_00),
    )
    add_location_rule(
        ARLocation.FR_BP_LAP_00_58_00_ON_WINGED_STAR,
        CanReachLocation(ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR),
    )
    add_location_rule(
        ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR,
        CanReachLocation(ARLocation.MP_RACE_4500_FEET),
    )
    add_location_rule(
        ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR,
        CanReachLocation(ARLocation.TA_CV_FINISH_03_20_00),
    )
    add_location_rule(
        ARLocation.FR_MP_LAP_00_57_00_ON_SWERVE_STAR,
        CanReachLocation(ARLocation.SS_FINISH_2_LAPS_IN_UNDER_02_05_00),
    )

    # Location rules: gating categories (applied only when gating option is ON)
    if world.options.city_trial_events_gated:
        for loc, item in _EVENT_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.abilities_gated:
        for loc, item in _ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))
        for loc, item in _ABILITY_TR_ITEM_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.machines_gated:
        for loc, item in _MACHINE_SINGLE_RULES.items():
            add_location_rule(loc, Has(item))
        for loc, (item_a, item_b) in _MACHINE_PAIR_RULES.items():
            add_location_rule(loc, HasAll(item_a, item_b))

    if world.options.city_trial_items_gated:
        for loc, item in _ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.city_trial_patches_gated:
        for loc, item in _PATCH_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.top_ride_items_gated:
        for loc, item in _TR_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    # Single apply pass: write the composed rules out to the multiworld.
    for entrance_name, rule in entrance_rules.items():
        world.set_rule(world.get_entrance(entrance_name), rule)
    for location_name, rule in location_rules.items():
        world.set_rule(world.get_location(location_name), rule)
