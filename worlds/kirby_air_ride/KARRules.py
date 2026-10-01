import typing

from rule_builder.rules import And, AtLeast, Has, HasAll, HasAny, HasFromListUnique, Or, Rule

from .KARData import GameMode
from .KARItems import (
    AP_STAR_PIECE_UNLOCK_ITEMS,
    CHARACTER_MACHINE_UNLOCKS,
    CHARGE_DEPENDENT_MACHINES,
    DAMAGING_ABILITY_UNLOCKS,
    DD5_DAMAGING_ABILITY_UNLOCKS,
    ITEM_TABLE,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    STADIUM_UNLOCK_ITEMS,
    KARItemName,
    KARItemType,
    items_by_type,
)
from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    APLocation,
    ARLocation,
    CTLocation,
    TRLocation,
)
from .KARRegions import (
    AR_COURSE_REGIONS,
    AR_FR_COURSE_REGIONS,
    AR_TA_COURSE_REGIONS,
    REGION_TO_MODE,
    REGION_TREE,
    TR_COURSE_REGIONS,
    TR_FR_COURSE_REGIONS,
    TR_TA_COURSE_REGIONS,
    KARRegion,
    create_n_blocks_rule,
)

if typing.TYPE_CHECKING:
    from . import KARWorld

# Stadium regions, by the unlock that puts each stadium in the rotation
STADIUM_REGION_TO_UNLOCK: dict[str, KARItemName] = {
    KARRegion.CITY_TRIAL_STADIUM_DR1: KARItemName.UNLOCK_STADIUM_DRAG_RACE_1,
    KARRegion.CITY_TRIAL_STADIUM_DR2: KARItemName.UNLOCK_STADIUM_DRAG_RACE_2,
    KARRegion.CITY_TRIAL_STADIUM_DR3: KARItemName.UNLOCK_STADIUM_DRAG_RACE_3,
    KARRegion.CITY_TRIAL_STADIUM_DR4: KARItemName.UNLOCK_STADIUM_DRAG_RACE_4,
    KARRegion.CITY_TRIAL_STADIUM_HJ: KARItemName.UNLOCK_STADIUM_HIGH_JUMP,
    KARRegion.CITY_TRIAL_STADIUM_TF: KARItemName.UNLOCK_STADIUM_TARGET_FLIGHT,
    KARRegion.CITY_TRIAL_STADIUM_AG: KARItemName.UNLOCK_STADIUM_AIR_GLIDER,
    KARRegion.CITY_TRIAL_STADIUM_KM1: KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1,
    KARRegion.CITY_TRIAL_STADIUM_KM2: KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2,
    KARRegion.CITY_TRIAL_STADIUM_DD1: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1,
    KARRegion.CITY_TRIAL_STADIUM_DD2: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2,
    KARRegion.CITY_TRIAL_STADIUM_DD3: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3,
    KARRegion.CITY_TRIAL_STADIUM_DD4: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4,
    KARRegion.CITY_TRIAL_STADIUM_DD5: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5,
    KARRegion.CITY_TRIAL_STADIUM_SR1: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_1,
    KARRegion.CITY_TRIAL_STADIUM_SR2: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_2,
    KARRegion.CITY_TRIAL_STADIUM_SR3: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_3,
    KARRegion.CITY_TRIAL_STADIUM_SR4: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_4,
    KARRegion.CITY_TRIAL_STADIUM_SR5: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_5,
    KARRegion.CITY_TRIAL_STADIUM_SR6: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_6,
    KARRegion.CITY_TRIAL_STADIUM_SR7: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_7,
    KARRegion.CITY_TRIAL_STADIUM_SR8: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_8,
    KARRegion.CITY_TRIAL_STADIUM_SR9: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_9,
    KARRegion.CITY_TRIAL_STADIUM_VSKD: KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,
}

# DD_ALL, DR_ALL and KM_ALL open once any of their numbered sub-stadiums is unlocked.
STADIUM_ALL_REGION_TO_UNLOCKS: dict[str, list[KARItemName]] = {
    parent: [STADIUM_REGION_TO_UNLOCK[child] for child in REGION_TREE[parent]]
    for parent in (
        KARRegion.CITY_TRIAL_STADIUM_DD_ALL,
        KARRegion.CITY_TRIAL_STADIUM_DR_ALL,
        KARRegion.CITY_TRIAL_STADIUM_KM_ALL,
    )
}

# A course's unlock opens its standard, Time Attack and Free Run regions alike.
_AR_COURSE_UNLOCKS: dict[str, KARItemName] = {
    KARRegion.AIR_RIDE_MAGMA_FLOWS: KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARRegion.AIR_RIDE_FANTASY_MEADOWS: KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARRegion.AIR_RIDE_CELESTIAL_VALLEY: KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARRegion.AIR_RIDE_BEANSTALK_PARK: KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARRegion.AIR_RIDE_FROZEN_HILLSIDE: KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARRegion.AIR_RIDE_MACHINE_PASSAGE: KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARRegion.AIR_RIDE_SKY_SANDS: KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARRegion.AIR_RIDE_CHECKER_KNIGHTS: KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    KARRegion.AIR_RIDE_NEBULA_BELT: KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
}
AR_COURSE_REGION_TO_UNLOCK: dict[str, KARItemName] = {
    region: _AR_COURSE_UNLOCKS[course]
    for variant in (AR_COURSE_REGIONS, AR_TA_COURSE_REGIONS, AR_FR_COURSE_REGIONS)
    for course, region in zip(AR_COURSE_REGIONS, variant, strict=True)
}

_TR_COURSE_UNLOCKS: dict[str, KARItemName] = {
    KARRegion.TOP_RIDE_GRASS: KARItemName.UNLOCK_TR_COURSE_GRASS,
    KARRegion.TOP_RIDE_SAND: KARItemName.UNLOCK_TR_COURSE_SAND,
    KARRegion.TOP_RIDE_SKY: KARItemName.UNLOCK_TR_COURSE_SKY,
    KARRegion.TOP_RIDE_FIRE: KARItemName.UNLOCK_TR_COURSE_FIRE,
    KARRegion.TOP_RIDE_LIGHT: KARItemName.UNLOCK_TR_COURSE_LIGHT,
    KARRegion.TOP_RIDE_WATER: KARItemName.UNLOCK_TR_COURSE_WATER,
    KARRegion.TOP_RIDE_METAL: KARItemName.UNLOCK_TR_COURSE_METAL,
}
TR_COURSE_REGION_TO_UNLOCK: dict[str, KARItemName] = {
    region: _TR_COURSE_UNLOCKS[course]
    for variant in (TR_COURSE_REGIONS, TR_TA_COURSE_REGIONS, TR_FR_COURSE_REGIONS)
    for course, region in zip(TR_COURSE_REGIONS, variant, strict=True)
}

# Event-dependent City Trial locations
_EVENT_LOCATION_RULES: dict[str, str] = {
    CTLocation.DO_SOME_DAMAGE_TO_DYNA_BLADE: KARItemName.UNLOCK_EVENT_DYNA_BLADE,
    CTLocation.GET_TRAMPLED_BY_DYNA_BLADE: KARItemName.UNLOCK_EVENT_DYNA_BLADE,
    CTLocation.STEAL_8_FROM_TAC: KARItemName.UNLOCK_EVENT_TAC,
    CTLocation.THE_METEOR_ATTACKS_CITY_3: KARItemName.UNLOCK_EVENT_METEOR,
    CTLocation.BREAK_5_OF_HUGE_PILLARS_THAT_APPEAR: KARItemName.UNLOCK_EVENT_PILLAR,
    CTLocation.BREAK_PILLAR_WITHIN_40S: KARItemName.UNLOCK_EVENT_PILLAR,
    CTLocation.USE_UP_ONE_OF_RESTORATION_AREAS: KARItemName.UNLOCK_EVENT_RESTORATION_AREA,
    CTLocation.ENTER_CASTLE_CHAMBER: KARItemName.UNLOCK_EVENT_SECRET_CHAMBER,
    APLocation.EVENT_RUN_AMOK_1000_FEET: KARItemName.UNLOCK_EVENT_RUN_AMOK,
    APLocation.EVENT_RAIL_FIRE_ALL_STATIONS: KARItemName.UNLOCK_EVENT_RAIL_FIRE,
    APLocation.EVENT_SAME_ITEM_GET_20: KARItemName.UNLOCK_EVENT_SAME_ITEM,
    APLocation.EVENT_LIGHTHOUSE_BOTH_LIGHTS: KARItemName.UNLOCK_EVENT_LIGHTHOUSE,
    APLocation.EVENT_PREDICTION_WRONG: KARItemName.UNLOCK_EVENT_PREDICTION,
    APLocation.EVENT_UFO_ALL_UP: KARItemName.UNLOCK_EVENT_UFO,
    APLocation.EVENT_BUMP_MACHINE_FORMATION: KARItemName.UNLOCK_EVENT_MACHINE_FORMATION,
    APLocation.EVENT_BOUNCE_OVER_10_ITEMS: KARItemName.UNLOCK_EVENT_BOUNCE,
    APLocation.EVENT_FOG_KO_A_RIVAL: KARItemName.UNLOCK_EVENT_FOG,
    APLocation.EVENT_FAKE_POWERUPS_5_NO_FAKES: KARItemName.UNLOCK_EVENT_FAKE_POWERUPS,
    APLocation.EVENT_DYNA_BLADE_5_ITEMS: KARItemName.UNLOCK_EVENT_DYNA_BLADE,
    APLocation.EVENT_METEOR_NO_DAMAGE: KARItemName.UNLOCK_EVENT_METEOR,
}

# Ability-dependent locations
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
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_SWORD,
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_WHEEL,
    ARLocation.SWALL_CHILLY_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_FREEZE,
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_PLASMA,
}

# Base-ability-dependent locations
_BASE_ABILITY_LOCATION_RULES: dict[str, str] = {
    # Air Ride "Swallow ..."
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_5_GARBAGE_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.CK_SWALL_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_CHILLY_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_200_ENEMIES: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.BP_SWALL_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.FM_SWALL_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    # An exhaled star is a swallowed enemy spat back out
    ARLocation.DEFEAT_100_ENEMIES_WITH_EXHALED_STARS: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    # Quick Spin
    ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    ARLocation.FINISH_SPINNING_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    TRLocation.QUICK_SPIN_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    TRLocation.FIRST_WHILE_DOING_A_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    # Require machines that need charge
    ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    APLocation.TA_NB_FINISH_03_15_00_ON_HYDRA: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    APLocation.FR_CV_LAP_01_00_00_ON_ARCHIPELAGO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    APLocation.AIR_RIDE_1ST_ON_ARCHIPELAGO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    APLocation.BUST_SHADOW_STAR_ON_ARCHIPELAGO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    APLocation.KO_CPU_WITH_AP_STAR_SPHERE_SHOT: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    CTLocation.STADIUM_DR4_33_00_TURBO: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    CTLocation.BUST_ROCKET_STAR_ON_SLICK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    CTLocation.BUST_FORMULA_STAR_ON_TURBO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    # Level-5 CPUs are very difficult without charge
    TRLocation.GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.SAND_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.SKY_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.FIRE_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.WATER_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.LIGHT_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.METAL_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    APLocation.TR_1ST_AGAINST_3_LEVEL_5_CPUS: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
}

# The faster of each Top Ride course's two Free Run lap times, which needs Charge
_TR_FR_HARD_TIME_LOCATIONS: tuple[str, ...] = (
    TRLocation.FR_GRASS_LAP_00_04_50,
    TRLocation.FR_SAND_LAP_00_05_00,
    TRLocation.FR_SKY_LAP_00_09_00,
    TRLocation.FR_FIRE_LAP_00_06_50,
    TRLocation.FR_WATER_LAP_00_10_50,
    TRLocation.FR_LIGHT_LAP_00_06_00,
    TRLocation.FR_METAL_LAP_00_09_50,
)

# The faster of each Top Ride course's two Time Attack times, which needs Charge or the Speed Up item
_TR_TA_HARD_TIME_LOCATIONS: tuple[str, ...] = (
    TRLocation.TA_GRASS_FINISH_00_28_00,
    TRLocation.TA_SAND_FINISH_00_29_00,
    TRLocation.TA_SKY_FINISH_00_47_00,
    TRLocation.TA_FIRE_FINISH_00_39_00,
    TRLocation.TA_WATER_FINISH_00_56_00,
    TRLocation.TA_LIGHT_FINISH_00_33_00,
    TRLocation.TA_METAL_FINISH_00_51_00,
)

# Machine-dependent locations needing one specific machine
_MACHINE_SINGLE_RULES: dict[str, str] = {
    # City Trial
    CTLocation.STADIUM_DR1_17_00_FORMULA: KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
    CTLocation.STADIUM_DR3_31_00_WHEELIE_BIKE: KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
    CTLocation.STADIUM_DR2_27_00_WAGON: KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    CTLocation.STADIUM_DR4_33_00_TURBO: KARItemName.UNLOCK_MACHINE_TURBO_STAR,
    CTLocation.STADIUM_DR2_29_00_WINGED: KARItemName.UNLOCK_MACHINE_WINGED_STAR,
    CTLocation.STADIUM_DR4_24_00_REX: KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
    CTLocation.STADIUM_DR1_26_00_WARPSTAR: KARItemName.UNLOCK_MACHINE_WARP_STAR,
    CTLocation.STADIUM_DR3_28_00_SWERVE: KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
    # Air Ride
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
    # Archipelago
    APLocation.TA_NB_FINISH_03_15_00_ON_HYDRA: KARItemName.UNLOCK_MACHINE_HYDRA,
    APLocation.FR_NB_LAP_01_10_00_ON_WARPSTAR: KARItemName.UNLOCK_MACHINE_WARP_STAR,
    APLocation.FR_CV_LAP_01_00_00_ON_ARCHIPELAGO_STAR: KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    APLocation.TA_CK_FINISH_04_00_00_ON_FLIGHT_WARP_STAR: KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
    APLocation.FR_MP_LAP_01_05_00_ON_COMPACT_STAR: KARItemName.UNLOCK_MACHINE_COMPACT_STAR,
    APLocation.TA_FH_FINISH_03_00_00_ON_WHEELIE_BIKE: KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
    APLocation.TA_SS_FINISH_02_50_00_ON_FLIGHT_WARP_STAR: KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
    APLocation.TA_MF_FINISH_03_15_00_AS_META_KNIGHT: KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT,
    APLocation.AIR_RIDE_1ST_ON_ARCHIPELAGO_STAR: KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    APLocation.KO_CPU_WITH_AP_STAR_SPHERE_SHOT: KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    APLocation.KM_KO_30_ENEMIES_AS_KING_DEDEDE: KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE,
    APLocation.VSKD_KO_KING_DEDEDE_AS_META_KNIGHT: KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT,
}

# Machine-dependent locations needing two specific machines
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
    APLocation.BUST_REX_WHEELIE_ON_WHEELIE_SCOOTER: (
        KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
        KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER,
    ),
    APLocation.BUST_WINGED_STAR_ON_FLIGHT_WARP_STAR: (
        KARItemName.UNLOCK_MACHINE_WINGED_STAR,
        KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
    ),
    APLocation.BUST_SHADOW_STAR_ON_ARCHIPELAGO_STAR: (
        KARItemName.UNLOCK_MACHINE_SHADOW_STAR,
        KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    ),
}

# Item-dependent CT locations
_ITEM_LOCATION_RULES: dict[str, str] = {
    CTLocation.EAT_3_HOT_DOGS: KARItemName.UNLOCK_ITEM_HOT_DOG,
    CTLocation.EAT_3_PLATES_OF_SUSHI: KARItemName.UNLOCK_ITEM_SUSHI,
    CTLocation.EAT_2_MAXIM_TOMATOES: KARItemName.UNLOCK_ITEM_MAXIM_TOMATO,
    CTLocation.DRINK_3_ENERGY_DRINKS: KARItemName.UNLOCK_ITEM_ENERGY_DRINK,
    CTLocation.USE_FIREWORKS_TO_KO_RIVALS_10X: KARItemName.UNLOCK_ITEM_FIREWORKS,
    CTLocation.USE_SENSOR_BOMBS_TO_KO_RIVALS_3X: KARItemName.UNLOCK_ITEM_SENSOR_BOMB,
    CTLocation.USE_GOLD_SPIKES_TO_KO_RIVALS_3X: KARItemName.UNLOCK_ITEM_GORDO,
}

# Item-dependent Archipelago checklist locations
_AP_ITEM_LOCATION_RULES: dict[str, str] = {
    APLocation.COLLECT_5_ALL_UPS: KARItemName.UNLOCK_ITEM_ALL_UP,
    APLocation.EAT_3_ICE_CREAMS: KARItemName.UNLOCK_ITEM_ICE_CREAM,
    APLocation.EAT_3_RICE_BALLS: KARItemName.UNLOCK_ITEM_RICE_BALL,
    APLocation.EAT_3_CHICKENS: KARItemName.UNLOCK_ITEM_CHICKEN,
    APLocation.EAT_3_CURRIES: KARItemName.UNLOCK_ITEM_CURRY,
    APLocation.EAT_3_RAMENS: KARItemName.UNLOCK_ITEM_RAMEN,
    APLocation.EAT_3_OMELETS: KARItemName.UNLOCK_ITEM_OMELET,
    APLocation.EAT_3_HAMBURGERS: KARItemName.UNLOCK_ITEM_HAMBURGER,
    APLocation.EAT_3_APPLES: KARItemName.UNLOCK_ITEM_APPLE,
}

# The KIRBY MELEE solo-KO counts too high to reach without a fast-KOing ability
_KM_SOLO_KO_LOCATIONS: tuple[str, ...] = (
    CTLocation.STADIUM_KM1_KO_75_ENEMIES_BY_YOURSELF,
    APLocation.KM1_KO_100_ENEMIES_BY_YOURSELF,
    APLocation.KM2_KO_60_ENEMIES_BY_YOURSELF,
)

# Abilities that KO fast enough for those counts. All four spawn in both KIRBY MELEE stages, on Sword Knight,
# Pichikuri, Caller and Plasma Wisp.
_KM_SOLO_KO_ABILITY_UNLOCKS: tuple[str, ...] = (
    KARItemName.UNLOCK_ABILITY_SWORD,
    KARItemName.UNLOCK_ABILITY_NEEDLE,
    KARItemName.UNLOCK_ABILITY_TORNADO,
    KARItemName.UNLOCK_ABILITY_PLASMA,
)

# The City Trial items that damage rivals
_DAMAGING_CT_ITEM_UNLOCKS: tuple[str, ...] = (
    KARItemName.UNLOCK_ITEM_FIREWORKS,
    KARItemName.UNLOCK_ITEM_SENSOR_BOMB,
    KARItemName.UNLOCK_ITEM_GORDO,
    KARItemName.UNLOCK_ITEM_PANIC_SPIN,
)

# Air Ride enemy-defeat counts. Ramming is off in Air Ride, so these need a damage source.
_AR_DEFEAT_LOCATIONS: tuple[str, ...] = (
    ARLocation.DEFEAT_300_OF_YOUR_ENEMIES,
    ARLocation.DEFEAT_1000_OF_YOUR_ENEMIES,
)

# Machines rideable in City Trial
_CT_MACHINE_UNLOCKS: list[str] = sorted(
    name for name in items_by_type[KARItemType.MACHINE_UNLOCK] if GameMode.CITYTRIAL in ITEM_TABLE[name].source_modes
)


def _any_rideable(machines: list[str], charge_gated: bool) -> Rule:
    """Any one of `machines`, counting a charge-dependent one only alongside Charge while Charge is gated."""
    steerable = [name for name in machines if name not in CHARGE_DEPENDENT_MACHINES]
    charge_dependent = [name for name in machines if name in CHARGE_DEPENDENT_MACHINES]
    if not charge_gated or not charge_dependent:
        return HasAny(*machines)
    return HasAny(*steerable) | (Has(KARItemName.UNLOCK_BASE_ABILITY_CHARGE) & HasAny(*charge_dependent))


# Locations needing any rideable City Trial machine
_CT_ANY_MACHINE_LOCATIONS: tuple[str, ...] = (
    APLocation.BREAK_ALL_CORAL,
    APLocation.CASTLE_FLOWER_ON_FOOT,
    APLocation.SKY_GARDEN_TOP_ON_FOOT,
    CTLocation.RACE_60_MILES,
    CTLocation.RACE_200_MILES,
    APLocation.EVENT_RUN_AMOK_1000_FEET,
    APLocation.EVENT_RAIL_FIRE_ALL_STATIONS,
    APLocation.EVENT_BUMP_MACHINE_FORMATION,
    APLocation.USE_ALL_GRIND_RAILS,
)

# Machines that can turn up in the city. King Dedede and Meta Knight only ever ride their own.
_CT_FIELD_MACHINE_UNLOCKS: list[str] = [name for name in _CT_MACHINE_UNLOCKS if name not in CHARACTER_MACHINE_UNLOCKS]

_CT_FLIGHT_MACHINES: tuple[str, ...] = (
    KARItemName.UNLOCK_MACHINE_DRAGOON,
    KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
    KARItemName.UNLOCK_MACHINE_WINGED_STAR,
)

# Machines that glide too poorly to stay airborne 15 seconds in TF, even on Glide Patches, or to carry an
# AIR GLIDER launch without them. Charge doesn't change how any machine glides.
_POOR_GLIDE_MACHINES: frozenset[str] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
        KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
        KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER,
        KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE,
        KARItemName.UNLOCK_MACHINE_FORMULA_STAR,
        KARItemName.UNLOCK_MACHINE_WAGON_STAR,
        KARItemName.UNLOCK_MACHINE_BULK_STAR,
        KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
        KARItemName.UNLOCK_MACHINE_HYDRA,
        KARItemName.UNLOCK_MACHINE_SLICK_STAR,
        KARItemName.UNLOCK_MACHINE_TURBO_STAR,
        KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    }
)

_GOOD_GLIDE_MACHINES: list[str] = [name for name in _CT_MACHINE_UNLOCKS if name not in _POOR_GLIDE_MACHINES]

# Stadium glide checks that need a long glide
_HARD_GLIDE_LOCATIONS: tuple[str, ...] = (
    CTLocation.STADIUM_TF_AIRBORNE_15_SECONDS,
    CTLocation.STADIUM_AG_FLY_1300_FEET,
    CTLocation.STADIUM_AG_AIRBORNE_30_SECONDS,
    APLocation.AG_FLY_2000_FEET,
)

# The good gliders that make those glides without Glide Patches
_UNPATCHED_GLIDE_MACHINES: tuple[str, ...] = (
    KARItemName.UNLOCK_MACHINE_DRAGOON,
    KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
)

_HJ_MACHINE_RULES: dict[str, tuple[str, ...]] = {
    CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_500_FEET: (
        KARItemName.UNLOCK_MACHINE_DRAGOON,
        KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
        KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER,
    ),
    CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_1000_FEET: (
        KARItemName.UNLOCK_MACHINE_DRAGOON,
        KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
    ),
    APLocation.HJ_JUMP_HIGHER_THAN_1500_FEET: (
        KARItemName.UNLOCK_MACHINE_DRAGOON,
        KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
    ),
    # The Winged Star only just makes it
    CTLocation.STADIUM_HJ_AIRBORNE_10_SECONDS: _CT_FLIGHT_MACHINES,
}

# Machines that can't hold 20 mph for a whole Fantasy Meadows lap
_FM_20MPH_EXCLUDED_MACHINES: frozenset[str] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
        KARItemName.UNLOCK_MACHINE_SHADOW_STAR,
        KARItemName.UNLOCK_MACHINE_COMPACT_STAR,
        KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
    }
)

_FM_20MPH_MACHINES: list[str] = sorted(
    name
    for name in items_by_type[KARItemType.MACHINE_UNLOCK]
    if GameMode.AIRRIDE in ITEM_TABLE[name].source_modes and name not in _FM_20MPH_EXCLUDED_MACHINES
)

# Machines that can't glide up to Fantasy Meadows' shortcut easily
_FM_SHORTCUT_EXCLUDED_MACHINES: frozenset[str] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
        KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
        KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER,
        KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE,
    }
)

_FM_SHORTCUT_MACHINES: list[str] = sorted(
    name
    for name in items_by_type[KARItemType.MACHINE_UNLOCK]
    if GameMode.AIRRIDE in ITEM_TABLE[name].source_modes and name not in _FM_SHORTCUT_EXCLUDED_MACHINES
)

# Item-count CT locations
_ITEM_PICKUP_LOCATIONS: tuple[str, ...] = (
    CTLocation.GET_50_ITEMS,
    CTLocation.GET_10_ITEMS_IN_20S,
    CTLocation.PICKUP_100_ITEMS,
    CTLocation.PICKUP_500_ITEMS,
    CTLocation.PICKUP_1000_ITEMS,
    CTLocation.PICKUP_3000_ITEMS,
    APLocation.EVENT_BOUNCE_OVER_10_ITEMS,
)

_PATCH_EVENT_LOCATIONS: tuple[str, ...] = (
    APLocation.EVENT_SAME_ITEM_GET_20,
    APLocation.EVENT_FAKE_POWERUPS_5_NO_FAKES,
    # Dyna Blade drops nothing but stat patches
    APLocation.EVENT_DYNA_BLADE_5_ITEMS,
    APLocation.MAX_OUT_A_STAT,
)

_RARE_CT_ITEM_UNLOCKS: frozenset[str] = frozenset({*LEGENDARY_PIECE_UNLOCK_ITEMS, *AP_STAR_PIECE_UNLOCK_ITEMS})

# Patch-dependent CT locations
_PATCH_LOCATION_RULES: dict[str, str] = {
    CTLocation.GET_10_BOOST_PATCHES: KARItemName.UNLOCK_PATCH_BOOST,
    CTLocation.GET_10_TURN_PATCHES: KARItemName.UNLOCK_PATCH_TURN,
    CTLocation.GET_10_WEIGHT_PATCHES: KARItemName.UNLOCK_PATCH_WEIGHT,
    CTLocation.GET_10_GLIDE_PATCHES: KARItemName.UNLOCK_PATCH_GLIDE,
    CTLocation.GET_30_GLIDE_PATCHES: KARItemName.UNLOCK_PATCH_GLIDE,
    CTLocation.GET_10_TOP_SPEED_PATCHES: KARItemName.UNLOCK_PATCH_TOP_SPEED,
    CTLocation.GET_10_CHARGE_PATCHES: KARItemName.UNLOCK_PATCH_CHARGE,
    CTLocation.GET_10_DEFENSE_PATCHES: KARItemName.UNLOCK_PATCH_DEFENSE,
}

# Box-break CT locations
_BOX_BREAK_LOCATIONS: tuple[str, ...] = (
    CTLocation.BREAK_500_BOXES,
    CTLocation.BREAK_1000_BOXES,
)

# Per-color Archipelago box counts
_AP_BOX_COLOR_RULES: dict[str, str] = {
    APLocation.BREAK_20_BLUE_BOXES: KARItemName.UNLOCK_BOX_BLUE,
    APLocation.BREAK_10_GREEN_BOXES: KARItemName.UNLOCK_BOX_GREEN,
    APLocation.BREAK_10_RED_BOXES: KARItemName.UNLOCK_BOX_RED,
}

_GREEN_BOX_ITEMS: tuple[str, ...] = (
    KARItemName.UNLOCK_ITEM_SPEED_MAX,
    KARItemName.UNLOCK_ITEM_SPEED_MIN,
    KARItemName.UNLOCK_ITEM_OFFENSE_MAX,
    KARItemName.UNLOCK_ITEM_DEFENSE_MAX,
    KARItemName.UNLOCK_ITEM_CHARGE_MAX,
    KARItemName.UNLOCK_ITEM_CHARGE_NONE,
    KARItemName.UNLOCK_ITEM_CANDY,
    KARItemName.UNLOCK_ITEM_FIREWORKS,
    KARItemName.UNLOCK_ITEM_PANIC_SPIN,
    KARItemName.UNLOCK_ITEM_SENSOR_BOMB,
    KARItemName.UNLOCK_ITEM_GORDO,
)

_BLUE_BOX_FOOD_ITEMS: tuple[str, ...] = (
    KARItemName.UNLOCK_ITEM_MAXIM_TOMATO,
    KARItemName.UNLOCK_ITEM_ENERGY_DRINK,
    KARItemName.UNLOCK_ITEM_ICE_CREAM,
    KARItemName.UNLOCK_ITEM_RICE_BALL,
    KARItemName.UNLOCK_ITEM_CHICKEN,
    KARItemName.UNLOCK_ITEM_CURRY,
    KARItemName.UNLOCK_ITEM_RAMEN,
    KARItemName.UNLOCK_ITEM_OMELET,
    KARItemName.UNLOCK_ITEM_HAMBURGER,
    KARItemName.UNLOCK_ITEM_SUSHI,
    KARItemName.UNLOCK_ITEM_HOT_DOG,
    KARItemName.UNLOCK_ITEM_APPLE,
)

# The only loot Tac drops: the twelve foods, All Up, Sleep and the nine patches
_TAC_LOOT_ITEM_UNLOCKS: tuple[str, ...] = (*_BLUE_BOX_FOOD_ITEMS, KARItemName.UNLOCK_ITEM_ALL_UP)
_TAC_LOOT_ABILITY_UNLOCK: str = KARItemName.UNLOCK_ABILITY_SLEEP

_CT_LOOT_GATES: frozenset[str] = frozenset({"city_trial_items_gated", "city_trial_patches_gated", "abilities_gated"})


def _box_color_requirements(effective_gates: set[str]) -> dict[str, list[Rule]]:
    requirements: dict[str, list[Rule]] = {
        KARItemName.UNLOCK_BOX_BLUE: [],
        KARItemName.UNLOCK_BOX_GREEN: [],
        KARItemName.UNLOCK_BOX_RED: [],
    }

    if "city_trial_boxes_gated" in effective_gates:
        for color, rules in requirements.items():
            rules.append(Has(color))

    if "city_trial_items_gated" in effective_gates:
        requirements[KARItemName.UNLOCK_BOX_GREEN].append(HasAny(*_GREEN_BOX_ITEMS))
        if "city_trial_patches_gated" in effective_gates:
            requirements[KARItemName.UNLOCK_BOX_BLUE].append(
                HasAny(*sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK]), *_BLUE_BOX_FOOD_ITEMS)
            )
        if "abilities_gated" in effective_gates:
            requirements[KARItemName.UNLOCK_BOX_RED].append(
                HasAny(*sorted(items_by_type[KARItemType.ABILITY_UNLOCK]), *LEGENDARY_PIECE_UNLOCK_ITEMS)
            )

    return requirements


# The ability-themed Top Ride items
_TR_ABILITY_ITEM_KEYS: dict[str, str] = {
    KARItemName.UNLOCK_TR_ITEM_FREEZE_FAN: KARItemName.UNLOCK_ABILITY_FREEZE,
    KARItemName.UNLOCK_TR_ITEM_FIRE: KARItemName.UNLOCK_ABILITY_FIRE,
    KARItemName.UNLOCK_TR_ITEM_BOMB: KARItemName.UNLOCK_ABILITY_BOMB,
    KARItemName.UNLOCK_TR_ITEM_WALKY: KARItemName.UNLOCK_ABILITY_MIC,
}


def _tr_item_key(tr_item: str, abilities_gated: bool) -> Rule:
    """A Top Ride item's own unlock or, while abilities are gated, the copy ability that also unlocks it."""
    ability = _TR_ABILITY_ITEM_KEYS.get(tr_item) if abilities_gated else None
    return HasAny(tr_item, ability) if ability else Has(tr_item)


# TR item-dependent locations
_TR_ITEM_LOCATION_RULES: dict[str, str] = {
    APLocation.TR_FREEZE_3_RIVALS_WITH_ONE_FREEZE_FAN: KARItemName.UNLOCK_TR_ITEM_FREEZE_FAN,
    APLocation.TR_3_SPEED_DOWNS_AND_1ST: KARItemName.UNLOCK_TR_ITEM_SPEED_DOWN,
    TRLocation.FIRST_WHILE_HOLDING_HAMMER: KARItemName.UNLOCK_TR_ITEM_HAMMER,
    TRLocation.GET_20_INVINCIBLE_CANDY_ITEMS: KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY,
    TRLocation.BUZZ_SAW_SEND_3_RIVALS: KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW,
    TRLocation.GET_20_SPINNER_ITEMS: KARItemName.UNLOCK_TR_ITEM_SPINNER,
    TRLocation.FIRE_FIRST_WHILE_HOLDING_FIRE_ITEM: KARItemName.UNLOCK_TR_ITEM_FIRE,
    TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM: KARItemName.UNLOCK_TR_ITEM_FIRE,
    TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS: KARItemName.UNLOCK_TR_ITEM_BOMB,
    TRLocation.GET_20_WALKY_ITEMS: KARItemName.UNLOCK_TR_ITEM_WALKY,
}

# The Top Ride items that land a hit, so a rival holding one can knock the player around
_TR_ATTACK_ITEM_UNLOCKS: tuple[str, ...] = (
    KARItemName.UNLOCK_TR_ITEM_HAMMER,
    KARItemName.UNLOCK_TR_ITEM_SPINNER,
    KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW,
    KARItemName.UNLOCK_TR_ITEM_DRILL,
    KARItemName.UNLOCK_TR_ITEM_FREEZE_FAN,
    KARItemName.UNLOCK_TR_ITEM_MISSILE,
    KARItemName.UNLOCK_TR_ITEM_FIRE,
    KARItemName.UNLOCK_TR_ITEM_BOMB,
    KARItemName.UNLOCK_TR_ITEM_STEP_BOOM,
    KARItemName.UNLOCK_TR_ITEM_WALKY,
    KARItemName.UNLOCK_TR_ITEM_KRACKO,
)

# The Archipelago box that names every ability-themed Top Ride item
_AP_TR_ALL_ABILITY_ITEMS_LOCATION = APLocation.TR_USE_ALL_ABILITY_ITEMS

# The Archipelago boxes the mod only counts on Steer Star
_AP_TR_STEER_STAR_LOCATIONS: tuple[str, ...] = (
    APLocation.TA_GRASS_FINISH_00_33_00_ON_STEER_STAR,
    APLocation.TA_METAL_FINISH_00_57_00_ON_STEER_STAR,
    APLocation.FR_SKY_LAP_00_11_00_ON_STEER_STAR,
    APLocation.TR_1ST_ON_ALL_COURSES_ON_STEER_STAR,
)

# The Archipelago boxes that sit in a Top Ride region
_AP_TR_LOCATION_TABLE = {
    name: data for name, data in AP_CHECKLIST_LOCATION_TABLE.items() if REGION_TO_MODE[data.region] == GameMode.TOPRIDE
}

# Generic item-count TR locations
_TR_ANY_ITEM_LOCATIONS: tuple[str, ...] = (
    TRLocation.COLLECT_500_ITEMS,
    TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE,
)

# The eight standard Air Ride courses
_AR_STANDARD_COURSE_UNLOCKS: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# which courses the swallow enemy checks have those enemies actually spawn in
_SWALLOW_ENEMY_COURSE_RULES: dict[str, tuple[str, ...]] = {
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: (
        KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
        KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
        KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    ),
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: (
        KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    ),
    ARLocation.SWALL_CHILLY_3_AND_FIRST: (
        KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    ),
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: (
        KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    ),
}

# Mode-root cells that only need enemies on the course, which every standard course spawns
_AR_ENEMY_DEPENDENT_LOCATIONS: tuple[str, ...] = (
    ARLocation.SWALL_5_GARBAGE_AND_FIRST,
    ARLocation.SWALL_200_ENEMIES,
    ARLocation.DEFEAT_300_OF_YOUR_ENEMIES,
    ARLocation.DEFEAT_1000_OF_YOUR_ENEMIES,
    ARLocation.DEFEAT_100_ENEMIES_WITH_EXHALED_STARS,
    ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
)

# The courses each ability's enemy spawns on
# Phan Phan and Dayl
_FIRE_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Noddy
_SLEEP_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Flappy
_WING_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Pichikuri, except on Beanstalk Park, where they spawn too late to carry Needle to the line in 1st
_NEEDLE_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
)

# Caller
_TORNADO_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# The only courses with a ground copy panel
_AR_COPY_PANEL_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
)

# The panel courses that can finish each ability cell
_AR_ABILITY_PANEL_COURSES: dict[str, tuple[str, ...]] = {
    ARLocation.FIRST_WITH_FIRE_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.FIRST_WITH_SLEEP_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.FIRST_WITH_WING_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.SWORD_CHALLENGE_10_SWINGS: _AR_COPY_PANEL_COURSES,
    ARLocation.TORNADO_CHALLENGE_15_KO: (KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,),
}

_AR_ABILITY_ENEMY_COURSES: dict[str, tuple[str, ...]] = {
    ARLocation.FIRST_WITH_FIRE_ABILITY: _FIRE_ENEMY_COURSES,
    ARLocation.FIRST_WITH_SLEEP_ABILITY: _SLEEP_ENEMY_COURSES,
    ARLocation.FIRST_WITH_WING_ABILITY: _WING_ENEMY_COURSES,
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: _NEEDLE_ENEMY_COURSES,
    ARLocation.TORNADO_CHALLENGE_15_KO: _TORNADO_ENEMY_COURSES,
    ARLocation.SWORD_CHALLENGE_10_SWINGS: _SWALLOW_ENEMY_COURSE_RULES[ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST],
}


# Air Ride mode-root cells only some courses can complete
_AR_COURSE_SUBSET_RULES: dict[str, tuple[str, ...]] = {
    **_SWALLOW_ENEMY_COURSE_RULES,
    **dict.fromkeys(_AR_ENEMY_DEPENDENT_LOCATIONS, _AR_STANDARD_COURSE_UNLOCKS),
    # Cells naming a copy ability: the course has to spawn that ability's enemy or carry a copy panel.
    **{
        loc: enemy + tuple(c for c in _AR_ABILITY_PANEL_COURSES[loc] if c not in enemy)
        for loc, enemy in _AR_ABILITY_ENEMY_COURSES.items()
    },
    # The only courses with a cliff to drop from
    ARLocation.DROP_FROM_CLIFFS_3X: (
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    ),
    # Courses with a launch near the finish line
    ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR: (
        KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
        KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    ),
}

# Air Ride locations that need every standard course
_AR_ALL_COURSES_LOCATIONS: tuple[str, ...] = (ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES,)

# Top Ride's counterpart to _AR_COURSE_SUBSET_RULES
_TR_COURSE_SUBSET_RULES: dict[str, tuple[str, ...]] = {
    # chosen to be easily completable
    TRLocation.LAP_NO_WALLS_AND_FIRST: (
        KARItemName.UNLOCK_TR_COURSE_GRASS,
        KARItemName.UNLOCK_TR_COURSE_SAND,
        KARItemName.UNLOCK_TR_COURSE_LIGHT,
        KARItemName.UNLOCK_TR_COURSE_METAL,
    ),
}

# Top Ride locations that need every course
_TR_ALL_COURSES_LOCATIONS: tuple[str, ...] = (
    TRLocation.FIRST_ON_ALL_COURSES,
    TRLocation.ALL_COURSES_NO_BOOST,
    TRLocation.FIRST_ON_ALL_COURSES_WITHOUT_BOOST,
    TRLocation.NOITEMS_ALL_COURSES,
    TRLocation.NOITEMS_FIRST_ALL_COURSES,
    APLocation.TR_1ST_ON_ALL_COURSES_ON_STEER_STAR,
)


def set_rules(world: "KARWorld"):
    """Define the logic rules, skipping locations and regions absent from this world."""

    # Collect rules and set them once at the end
    entrance_rules: dict[str, Rule] = {}
    location_rules: dict[str, Rule] = {}

    def add_location_rule(location_name: str, rule: Rule) -> None:
        location_name = world.checkbox_location_name(location_name)
        try:
            world.get_location(location_name)
        except KeyError:
            return
        existing = location_rules.get(location_name)
        location_rules[location_name] = existing & rule if existing is not None else rule

    def add_region_entrance_rule(region_name: str, rule: Rule) -> None:
        """Gate a region on `rule`, keyed by its sole entrance. A no-op when the region is absent this seed."""
        try:
            region = world.get_region(region_name)
        except KeyError:
            return
        if not region.entrances:
            return
        entrance_name = region.entrances[0].name
        existing = entrance_rules.get(entrance_name)
        entrance_rules[entrance_name] = existing & rule if existing is not None else rule

    # Every gate below reads effective_gates rather than the raw option
    if "city_trial_stadiums_gated" in world.effective_gates:
        for region_name, unlock in STADIUM_REGION_TO_UNLOCK.items():
            add_region_entrance_rule(region_name, Has(unlock))
        for region_name, unlocks in STADIUM_ALL_REGION_TO_UNLOCKS.items():
            add_region_entrance_rule(region_name, HasAny(*unlocks))
    elif KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE in world.goal_forced_unlocks:
        add_region_entrance_rule(KARRegion.CITY_TRIAL_STADIUM_VSKD, Has(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE))

    # Air Ride course entrances
    if "air_ride_courses_gated" in world.effective_gates:
        for region_name, unlock in AR_COURSE_REGION_TO_UNLOCK.items():
            add_region_entrance_rule(region_name, Has(unlock))

    # Top Ride course entrances
    if "top_ride_courses_gated" in world.effective_gates:
        for region_name, unlock in TR_COURSE_REGION_TO_UNLOCK.items():
            add_region_entrance_rule(region_name, Has(unlock))

    # Every combat stadium cell and Air Ride defeat count is a KO count, needing a damage source.
    if {"machines_gated", "base_abilities_gated"} <= world.effective_gates:
        combat_keys = (KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN, *CHARACTER_MACHINE_UNLOCKS)

        # Kirby Melee's two stages have no item node, so no copy panels spawn there and Inhale is
        # the only ability route.
        add_region_entrance_rule(
            KARRegion.CITY_TRIAL_STADIUM_KM_ALL,
            HasAny(*combat_keys, KARItemName.UNLOCK_BASE_ABILITY_INHALE),
        )

        if "abilities_gated" in world.effective_gates:
            add_region_entrance_rule(
                KARRegion.CITY_TRIAL_STADIUM_DD_ALL,
                HasAny(*combat_keys, *DAMAGING_ABILITY_UNLOCKS),
            )
            # Derby 5 panel pool is only Ice, Plasma, Sword and Needle.
            add_region_entrance_rule(
                KARRegion.CITY_TRIAL_STADIUM_DD5,
                HasAny(*combat_keys, *DD5_DAMAGING_ABILITY_UNLOCKS),
            )
            # Dedede's arena spawns copy panels and food and nothing else.
            add_region_entrance_rule(
                KARRegion.CITY_TRIAL_STADIUM_VSKD,
                HasAny(*combat_keys, *DAMAGING_ABILITY_UNLOCKS),
            )

        # Air Ride has no items and its abilities come from swallowed enemies, so Inhale is the other
        # source: exhaled stars defeat enemies.
        for loc in _AR_DEFEAT_LOCATIONS:
            add_location_rule(loc, HasAny(*combat_keys, KARItemName.UNLOCK_BASE_ABILITY_INHALE))

    if {"base_abilities_gated", "abilities_gated", "city_trial_items_gated"} <= world.effective_gates:
        city_damage_keys = (
            KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
            *DAMAGING_ABILITY_UNLOCKS,
            *_DAMAGING_CT_ITEM_UNLOCKS,
        )
        # A bust cell names the machine you ride, so King Dedede and Meta Knight can't land its hits.
        for loc in _MACHINE_PAIR_RULES:
            add_location_rule(loc, HasAny(*city_damage_keys))
        if "machines_gated" in world.effective_gates:
            # A KO in the city is a rival's machine destroyed, the same as a machine break.
            for loc in (CTLocation.BREAK_A_CPUS_MACHINE_5_X, APLocation.EVENT_FOG_KO_A_RIVAL):
                add_location_rule(loc, HasAny(*city_damage_keys, *CHARACTER_MACHINE_UNLOCKS))

    # Air Glider requires glide machines or glide patches unlocked
    if {"machines_gated", "city_trial_patches_gated"} <= world.effective_gates:
        add_region_entrance_rule(
            KARRegion.CITY_TRIAL_STADIUM_AG,
            HasAny(*_GOOD_GLIDE_MACHINES) | Has(KARItemName.UNLOCK_PATCH_GLIDE),
        )

    # Celestial Valley's tree-top Copy Chance Wheel takes a good glider or Wing
    if {"machines_gated", "abilities_gated"} <= world.effective_gates:
        add_location_rule(
            ARLocation.CV_COPY_CHANCE_WHEEL_TREE,
            HasAny(*_GOOD_GLIDE_MACHINES) | Has(KARItemName.UNLOCK_ABILITY_WING),
        )

    # Free run needs any machine
    if "machines_gated" in world.effective_gates:
        add_region_entrance_rule(KARRegion.CITY_TRIAL_FREE_RUN, HasAny(*_CT_MACHINE_UNLOCKS))

    # The unlock-parts cells complete once all three of their part rewards have been received.
    add_location_rule(
        CTLocation.UNLOCK_HYDRA_CHECKLIST,
        HasAll(
            KARItemName.CT_REWARD_HYDRA_PART_X,
            KARItemName.CT_REWARD_HYDRA_PART_Y,
            KARItemName.CT_REWARD_HYDRA_PART_Z,
        ),
    )

    add_location_rule(
        CTLocation.UNLOCK_DRAGOON_CHECKLIST,
        HasAll(
            KARItemName.CT_REWARD_DRAGOON_PART_A,
            KARItemName.CT_REWARD_DRAGOON_PART_B,
            KARItemName.CT_REWARD_DRAGOON_PART_C,
        ),
    )

    if "city_trial_events_gated" in world.effective_gates:
        for loc, item in _EVENT_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if "abilities_gated" in world.effective_gates:
        for loc, item in _ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if "base_abilities_gated" in world.effective_gates:
        for loc, item in _BASE_ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

        charge = Has(KARItemName.UNLOCK_BASE_ABILITY_CHARGE)
        for loc in _TR_FR_HARD_TIME_LOCATIONS:
            add_location_rule(loc, charge)
        if "top_ride_items_gated" in world.effective_gates:
            charge_or_speed_up = charge | Has(KARItemName.UNLOCK_TR_ITEM_SPEED_UP)
            for loc in _TR_TA_HARD_TIME_LOCATIONS:
                add_location_rule(loc, charge_or_speed_up)

        # Air Ride ability cells need Inhale unless a copy panel course is unlocked.
        if "air_ride_courses_gated" in world.effective_gates:
            inhale = Has(KARItemName.UNLOCK_BASE_ABILITY_INHALE)
            for loc, panels in _AR_ABILITY_PANEL_COURSES.items():
                add_location_rule(loc, inhale | HasAny(*panels))

    # Hydra, Bulk, Slick, Turbo and the Archipelago Star can't get anywhere without Charge
    charge_gated = "base_abilities_gated" in world.effective_gates

    if "machines_gated" in world.effective_gates:
        for loc, item in _MACHINE_SINGLE_RULES.items():
            add_location_rule(loc, Has(item))
        for loc, (item_a, item_b) in _MACHINE_PAIR_RULES.items():
            add_location_rule(loc, HasAll(item_a, item_b))
        add_location_rule(ARLocation.FM_LAP_ABOVE_20_MPH, _any_rideable(_FM_20MPH_MACHINES, charge_gated))
        hard_glider = HasAny(*_GOOD_GLIDE_MACHINES)
        if "city_trial_patches_gated" in world.effective_gates:
            hard_glider = HasAny(*_UNPATCHED_GLIDE_MACHINES) | (hard_glider & Has(KARItemName.UNLOCK_PATCH_GLIDE))
        for loc in _HARD_GLIDE_LOCATIONS:
            add_location_rule(loc, hard_glider)
        for loc, machines in _HJ_MACHINE_RULES.items():
            add_location_rule(loc, HasAny(*machines))

    if "city_trial_items_gated" in world.effective_gates:
        for loc, item in _ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    # Pieces and spheres arrive in a red box, so the assemble cells also need Red while boxes are gated.
    if "city_trial_boxes_gated" in world.effective_gates:
        add_location_rule(CTLocation.COMPLETE_DRAGOON_AND_HYDRA, Has(KARItemName.UNLOCK_BOX_RED))
        add_location_rule(APLocation.ASSEMBLE_ARCHIPELAGO_STAR, Has(KARItemName.UNLOCK_BOX_RED))
        add_location_rule(APLocation.ASSEMBLE_ALL_THREE_LEGENDARIES, Has(KARItemName.UNLOCK_BOX_RED))

    if "city_trial_patches_gated" in world.effective_gates:
        for loc, item in _PATCH_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    # Tac needs loot to spawn
    if _CT_LOOT_GATES <= world.effective_gates:
        add_location_rule(
            CTLocation.STEAL_8_FROM_TAC,
            HasAny(*_TAC_LOOT_ITEM_UNLOCKS)
            | HasAny(*sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK]))
            | Has(_TAC_LOOT_ABILITY_UNLOCK),
        )

    # Box-break cells need some color able to spawn
    box_requirements = _box_color_requirements(world.effective_gates)
    if all(box_requirements.values()):
        any_box = Or(*(And(*rules) for rules in box_requirements.values()))
        for loc in _BOX_BREAK_LOCATIONS:
            add_location_rule(loc, any_box)
        # Only a box hands out the Same Item event's item.
        add_location_rule(APLocation.EVENT_SAME_ITEM_GET_20, any_box)

    if _CT_LOOT_GATES <= world.effective_gates:
        any_ct_counting_item = HasAny(
            *sorted(items_by_type[KARItemType.CT_ITEM_UNLOCK] - _RARE_CT_ITEM_UNLOCKS),
            *sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK]),
            *sorted(items_by_type[KARItemType.ABILITY_UNLOCK]),
        )
        for loc in _ITEM_PICKUP_LOCATIONS:
            add_location_rule(loc, any_ct_counting_item)

    if "air_ride_courses_gated" in world.effective_gates:
        any_ar_course = HasAny(*sorted(items_by_type[KARItemType.AR_COURSE_UNLOCK]))
        ar_course_skip = (
            ARLocation.FILL_IN_100_CHECKLIST_BLOCKS,
            *_AR_ALL_COURSES_LOCATIONS,
            *_AR_COURSE_SUBSET_RULES,
        )
        for name, data in AIR_RIDE_LOCATION_TABLE.items():
            if data.region in AR_COURSE_REGION_TO_UNLOCK:
                continue
            if name in ar_course_skip:
                continue
            add_location_rule(name, any_ar_course)
        for loc in _AR_ALL_COURSES_LOCATIONS:
            add_location_rule(loc, HasAll(*_AR_STANDARD_COURSE_UNLOCKS))
        for loc, courses in _AR_COURSE_SUBSET_RULES.items():
            add_location_rule(loc, HasAny(*courses))
        add_location_rule(APLocation.AIR_RIDE_1ST_ON_EVERY_COURSE, HasAll(*_AR_COURSE_UNLOCKS.values()))

    if "top_ride_courses_gated" in world.effective_gates:
        tr_courses = sorted(items_by_type[KARItemType.TR_COURSE_UNLOCK])
        any_tr_course = HasAny(*tr_courses)
        tr_course_skip = (
            TRLocation.FILL_IN_100_CHECKLIST_BLOCKS,
            *_TR_ALL_COURSES_LOCATIONS,
            *_TR_COURSE_SUBSET_RULES,
        )
        for name, data in (TOP_RIDE_LOCATION_TABLE | _AP_TR_LOCATION_TABLE).items():
            if data.region in TR_COURSE_REGION_TO_UNLOCK:
                continue
            if name in tr_course_skip:
                continue
            add_location_rule(name, any_tr_course)
        for loc in _TR_ALL_COURSES_LOCATIONS:
            add_location_rule(loc, HasAll(*tr_courses))
        for loc, courses in _TR_COURSE_SUBSET_RULES.items():
            add_location_rule(loc, HasAny(*courses))

    if "city_trial_stadiums_gated" in world.effective_gates:
        # Despite the wording, "Play in over 10/20 stadium modes" checks 10/20 unlocked stadiums.
        add_location_rule(CTLocation.STADIUM_PLAY_10_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=10))
        add_location_rule(CTLocation.STADIUM_PLAY_20_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=20))
        add_location_rule(
            APLocation.DR_1ST_IN_EVERY_DRAG_RACE,
            HasAll(*(STADIUM_REGION_TO_UNLOCK[r] for r in REGION_TREE[KARRegion.CITY_TRIAL_STADIUM_DR_ALL])),
        )

    if "top_ride_items_gated" in world.effective_gates:
        abilities_keyed = "abilities_gated" in world.effective_gates
        tr_unlocks = sorted(items_by_type[KARItemType.TR_ITEM_UNLOCK])

        for loc, tr_item in _TR_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, _tr_item_key(tr_item, abilities_keyed))

        # "Get over 18 different types of items" needs 19 of the 21 types
        add_location_rule(
            TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS,
            AtLeast(19, *(_tr_item_key(tr_item, abilities_keyed) for tr_item in tr_unlocks)),
        )

        # The other item-count cells need any one type, by its item or, while abilities are gated, its ability.
        any_item_keys = list(tr_unlocks)
        if abilities_keyed:
            any_item_keys += sorted(_TR_ABILITY_ITEM_KEYS.values())
        any_tr_item = HasAny(*any_item_keys)
        for loc in _TR_ANY_ITEM_LOCATIONS:
            add_location_rule(loc, any_tr_item)

        add_location_rule(
            _AP_TR_ALL_ABILITY_ITEMS_LOCATION,
            And(*(_tr_item_key(tr_item, abilities_keyed) for tr_item in _TR_ABILITY_ITEM_KEYS)),
        )
        add_location_rule(
            APLocation.TR_USE_EVERY_KIND_OF_ITEM,
            And(*(_tr_item_key(tr_item, abilities_keyed) for tr_item in tr_unlocks)),
        )
        # Five hits in one race take a rival holding something that lands one.
        add_location_rule(
            APLocation.TR_1ST_AFTER_5_HITS,
            Or(*(_tr_item_key(tr_item, abilities_keyed) for tr_item in _TR_ATTACK_ITEM_UNLOCKS)),
        )

    # Archipelago rules read effective_gates: Archipelago boxes exist even when a gate's
    # modes have no goal
    if "city_trial_items_gated" in world.effective_gates:
        for loc, item in _AP_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))
        # The UFO's All Up is gated like any other, so its cell needs the unlock too.
        add_location_rule(APLocation.EVENT_UFO_ALL_UP, Has(KARItemName.UNLOCK_ITEM_ALL_UP))
        add_location_rule(APLocation.KO_A_RIVAL_WITH_PANIC_SPIN, Has(KARItemName.UNLOCK_ITEM_PANIC_SPIN))

    # Assemble cells need their pieces
    ct_items_keyed = "city_trial_items_gated" in world.effective_gates
    star_pieces_keyed = ct_items_keyed or set(AP_STAR_PIECE_UNLOCK_ITEMS) <= world.goal_forced_unlocks
    legendary_pieces_keyed = ct_items_keyed or set(LEGENDARY_PIECE_UNLOCK_ITEMS) <= world.goal_forced_unlocks
    if legendary_pieces_keyed:
        # Under the hydra_and_dragoon goal this cell is the victory event, which gets the rule instead.
        add_location_rule(CTLocation.COMPLETE_DRAGOON_AND_HYDRA, HasAll(*LEGENDARY_PIECE_UNLOCK_ITEMS))
    if star_pieces_keyed:
        # Not the machine unlock: assembling the star mounts it.
        add_location_rule(APLocation.ASSEMBLE_ARCHIPELAGO_STAR, HasAll(*AP_STAR_PIECE_UNLOCK_ITEMS))
    # All twelve pieces in one round
    all_three_keys = (
        *(AP_STAR_PIECE_UNLOCK_ITEMS if star_pieces_keyed else ()),
        *(LEGENDARY_PIECE_UNLOCK_ITEMS if legendary_pieces_keyed else ()),
    )
    if all_three_keys:
        add_location_rule(APLocation.ASSEMBLE_ALL_THREE_LEGENDARIES, HasAll(*all_three_keys))

    if "abilities_gated" in world.effective_gates:
        # Both Mic cells need Mic, which you can also get from the copy chance wheel
        add_location_rule(APLocation.GET_MIC_FROM_COPY_CHANCE, Has(KARItemName.UNLOCK_ABILITY_MIC))
        add_location_rule(APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY, Has(KARItemName.UNLOCK_ABILITY_MIC))
        add_location_rule(
            APLocation.SAME_COPY_ABILITY_3_IN_A_ROW, HasAny(*sorted(items_by_type[KARItemType.ABILITY_UNLOCK]))
        )
        # The same swap means the wheel only ever hands out unlocked abilities.
        add_location_rule(
            APLocation.GET_6_DIFFERENT_COPY_ABILITIES,
            HasFromListUnique(*sorted(items_by_type[KARItemType.ABILITY_UNLOCK]), count=6),
        )
        fast_ko_ability = HasAny(*_KM_SOLO_KO_ABILITY_UNLOCKS)
        for loc in _KM_SOLO_KO_LOCATIONS:
            add_location_rule(loc, fast_ko_ability)

    if "base_abilities_gated" in world.effective_gates:
        # A melee stadium spawns no copy panels, so every ability there comes from a swallowed enemy.
        add_location_rule(APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY, Has(KARItemName.UNLOCK_BASE_ABILITY_INHALE))
        for loc in _KM_SOLO_KO_LOCATIONS:
            add_location_rule(loc, Has(KARItemName.UNLOCK_BASE_ABILITY_INHALE))
        # Bulk Star needs charge
        add_location_rule(APLocation.SR1_FINISH_1ST_ON_BULK_STAR, Has(KARItemName.UNLOCK_BASE_ABILITY_CHARGE))

    if "city_trial_patches_gated" in world.effective_gates:
        add_location_rule(APLocation.GET_10_HP_PATCHES, Has(KARItemName.UNLOCK_PATCH_HP))
        add_location_rule(APLocation.GET_10_OFFENSE_PATCHES, Has(KARItemName.UNLOCK_PATCH_OFFENSE))
        any_patch = HasAny(*sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK]))
        for loc in _PATCH_EVENT_LOCATIONS:
            add_location_rule(loc, any_patch)

    for loc, box_item in _AP_BOX_COLOR_RULES.items():
        if box_requirements[box_item]:
            add_location_rule(loc, And(*box_requirements[box_item]))

    if "machines_gated" in world.effective_gates:
        any_ct_machine = _any_rideable(_CT_MACHINE_UNLOCKS, charge_gated)
        for loc in _CT_ANY_MACHINE_LOCATIONS:
            add_location_rule(loc, any_ct_machine)
        add_location_rule(APLocation.FLY_TO_HIGHEST_POINT, HasAny(*_CT_FLIGHT_MACHINES))
        add_location_rule(APLocation.AIRBORNE_20_SECONDS_IN_CITY, HasAny(*_CT_FLIGHT_MACHINES))
        add_location_rule(APLocation.LIGHTHOUSE_TOP_ON_FOOT, HasAny(*_CT_FLIGHT_MACHINES))
        add_location_rule(APLocation.RIDE_5_DIFFERENT_MACHINES, HasFromListUnique(*_CT_FIELD_MACHINE_UNLOCKS, count=5))
        add_location_rule(
            CTLocation.FR_CHANGE_AIR_RIDE_MACHINES_10X,
            HasFromListUnique(*_CT_MACHINE_UNLOCKS, count=2),
        )
        add_location_rule(APLocation.SR1_FINISH_1ST_ON_BULK_STAR, Has(KARItemName.UNLOCK_MACHINE_BULK_STAR))
        add_location_rule(APLocation.AIR_RIDE_1ST_AS_META_KNIGHT, Has(KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT))
        add_location_rule(APLocation.AIR_RIDE_1ST_AS_KING_DEDEDE, Has(KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE))
        add_location_rule(
            APLocation.NEBULA_BELT_1ST_ON_WHEELIE_SCOOTER, Has(KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER)
        )
        # The mod only counts the glide on the three machines the cell names.
        add_location_rule(
            APLocation.NEBULA_BELT_AIRBORNE_10_SECONDS,
            HasAny(
                KARItemName.UNLOCK_MACHINE_DRAGOON,
                KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR,
                KARItemName.UNLOCK_MACHINE_WINGED_STAR,
            ),
        )
        add_location_rule(APLocation.DD_KO_10_KIRBYS_AS_KING_DEDEDE, Has(KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE))
        add_location_rule(APLocation.FANTASY_MEADOWS_TAKE_SHORTCUT, _any_rideable(_FM_SHORTCUT_MACHINES, charge_gated))

    # The Top Ride control types ship only while Top Ride has a goal; without one the mod unlocks both.
    if "machines_gated" in world.effective_gates and world.top_ride_enabled:
        for loc in _AP_TR_STEER_STAR_LOCATIONS:
            add_location_rule(loc, Has(KARItemName.UNLOCK_MACHINE_STEER_STAR))

    if "colors_gated" in world.effective_gates:
        add_location_rule(APLocation.SR1_FINISH_1ST_3X_AS_PURPLE, Has(KARItemName.UNLOCK_COLOR_PURPLE))
        # The mod counts one finished race per color, so every color has to be selectable.
        all_colors = HasAll(*sorted(items_by_type[KARItemType.COLOR_UNLOCK]))
        add_location_rule(APLocation.AIR_RIDE_RACE_AS_EVERY_COLOR, all_colors)
        add_location_rule(APLocation.TR_RACE_AS_EVERY_COLOR, all_colors)

    for entrance_name, rule in entrance_rules.items():
        world.set_rule(world.get_entrance(entrance_name), rule)
    for location_name, rule in location_rules.items():
        world.set_rule(world.get_location(location_name), rule)

    # Each "Fill in over 100 Checklist blocks" cell needs 100 of its mode's other cells, excluding itself to avoid
    # recursion.
    for enabled, mode, fill_100_location in (
        (world.city_trial_enabled, GameMode.CITYTRIAL, CTLocation.FILL_IN_100_CHECKLIST_BLOCKS),
        (world.air_ride_enabled, GameMode.AIRRIDE, ARLocation.FILL_IN_100_CHECKLIST_BLOCKS),
        (world.top_ride_enabled, GameMode.TOPRIDE, TRLocation.FILL_IN_100_CHECKLIST_BLOCKS),
    ):
        if not enabled:
            continue
        try:
            fill_100 = world.get_location(world.checkbox_location_name(fill_100_location))
        except KeyError:
            continue  # excluded as this mode's goal, or otherwise absent
        world.set_rule(
            fill_100,
            create_n_blocks_rule(world, mode, 100, exclude_location_name=fill_100_location),
        )
