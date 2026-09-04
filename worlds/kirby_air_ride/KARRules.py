import typing

from rule_builder.rules import Has, HasAll, HasAny, HasFromListUnique, Rule

from .KARData import GameMode
from .KARItems import (
    AP_STAR_PIECE_UNLOCK_ITEMS,
    CHARACTER_MACHINE_UNLOCKS,
    CHARGE_DEPENDENT_MACHINES,
    DAMAGING_ABILITY_UNLOCKS,
    ITEM_TABLE,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    STADIUM_UNLOCK_ITEMS,
    KARItemName,
    KARItemType,
    items_by_type,
)
from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    APLocation,
    ARLocation,
    CTLocation,
    TRLocation,
)
from .KARRegions import (
    AR_COURSE_REGION_TO_UNLOCK,
    STADIUM_ALL_REGION_TO_UNLOCKS,
    STADIUM_REGION_TO_UNLOCK,
    TR_COURSE_REGION_TO_UNLOCK,
    KARRegion,
    create_n_blocks_rule,
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
    # Air Ride: finish/challenge checkboxes that name a copy ability
    ARLocation.FIRST_WITH_WING_ABILITY: KARItemName.UNLOCK_ABILITY_WING,
    ARLocation.FIRST_WITH_SLEEP_ABILITY: KARItemName.UNLOCK_ABILITY_SLEEP,
    ARLocation.FIRST_WITH_FIRE_ABILITY: KARItemName.UNLOCK_ABILITY_FIRE,
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: KARItemName.UNLOCK_ABILITY_NEEDLE,
    ARLocation.TORNADO_CHALLENGE_15_KO: KARItemName.UNLOCK_ABILITY_TORNADO,
    ARLocation.SWORD_CHALLENGE_10_SWINGS: KARItemName.UNLOCK_ABILITY_SWORD,
    # Air Ride: swallowing a named enemy needs its ability. That is only half the requirement -- the
    # enemy must also spawn, see _SWALLOW_ENEMY_COURSE_RULES.
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_SWORD,
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_WHEEL,
    ARLocation.SWALL_CHILLY_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_FREEZE,
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_PLASMA,
}

# Base-ability-dependent locations (when base_abilities_gated is ON).
_BASE_ABILITY_LOCATION_RULES: dict[str, str] = {
    # Air Ride "Swallow ..." cells
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_5_GARBAGE_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.CK_SWALL_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_CHILLY_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_200_ENEMIES: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.BP_SWALL_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    ARLocation.FM_SWALL_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_INHALE,
    # The Air Ride cells naming a copy ability are not here: a ground copy panel grants one without
    # inhaling, so their Inhale requirement is conditional -- see _AR_ABILITY_PANEL_COURSES.
    # Air Ride + Top Ride quick-spin cells. "Cross the finish line while spinning" names the animation,
    # but Quick Spin is the only way to be mid-spin on the line.
    ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    ARLocation.FINISH_SPINNING_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    TRLocation.QUICK_SPIN_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    TRLocation.FIRST_WHILE_DOING_A_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    # Cells ridden on a machine Charge makes usable: Slick and Turbo Star only turn by charge-drifting,
    # and Bulk Star has almost no speed of its own - a lap time on it is a chain of charge releases.
    ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    CTLocation.STADIUM_DR4_33_00_TURBO: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    CTLocation.BUST_ROCKET_STAR_ON_SLICK_STAR: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    # Top Ride cells naming level-5 CPUs: those outrun a Kirby who cannot boost, so 1st needs Charge.
    # Plain "take 1st" cells leave the CPU level to the player, and "without Boost" rules it out anyway.
    TRLocation.GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.SAND_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.SKY_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.FIRE_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.WATER_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.LIGHT_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
    TRLocation.METAL_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARItemName.UNLOCK_BASE_ABILITY_CHARGE,
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

# Item-dependent Archipelago checklist locations: the 8 foods the vanilla checklist leaves uncovered,
# plus the All Up counter.
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

# Machines rideable in the City Trial city, derived from source_modes so a new machine is classified by
# the same field the item pool uses. Free Star and Steer Star are Top Ride controls and drop out here.
_CT_MACHINE_UNLOCKS: list[str] = sorted(
    name for name in items_by_type[KARItemType.MACHINE_UNLOCK] if GameMode.CITYTRIAL in ITEM_TABLE[name].source_modes
)

# The same list split by whether Charge is what makes the machine rideable, for the "some machine to
# ride" rules while base abilities are gated.
_CHARGE_DEPENDENT_CT_MACHINES: list[str] = [name for name in _CT_MACHINE_UNLOCKS if name in CHARGE_DEPENDENT_MACHINES]
_STEERABLE_CT_MACHINES: list[str] = [name for name in _CT_MACHINE_UNLOCKS if name not in CHARGE_DEPENDENT_MACHINES]

# Target Flight scores the flight off its launch ramp, so "stay airborne longer than 15 seconds" is a
# glide check. The wheelie/bike class holds no air at all and drops straight off the ramp, Dedede's
# ride included, and Formula, Wagon, Bulk, Rocket Star and Hydra glide too poorly to hold the launch
# that long. The stadium grid offers every unlocked machine, so any other one clears it.
_TF_AIRBORNE_EXCLUDED_MACHINES: frozenset[str] = frozenset(
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
    }
)

_TF_AIRBORNE_MACHINES: list[str] = [name for name in _CT_MACHINE_UNLOCKS if name not in _TF_AIRBORNE_EXCLUDED_MACHINES]

# Machines that cannot hold Fantasy Meadows' 20 mph floor for a whole lap. The cell polls per-frame
# displacement, so it wants sustained speed, not a lap time. Shadow Star (19.9 mph), Compact Star (18.0)
# and Rocket Star (15.5) never reach it; Swerve Star clears it (31.2) but stops dead to steer.
_FM_20MPH_EXCLUDED_MACHINES: frozenset[str] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_SWERVE_STAR,
        KARItemName.UNLOCK_MACHINE_SHADOW_STAR,
        KARItemName.UNLOCK_MACHINE_COMPACT_STAR,
        KARItemName.UNLOCK_MACHINE_ROCKET_STAR,
    }
)

# Every Air Ride machine that can actually complete that cell.
_FM_20MPH_MACHINES: list[str] = sorted(
    name
    for name in items_by_type[KARItemType.MACHINE_UNLOCK]
    if GameMode.AIRRIDE in ITEM_TABLE[name].source_modes and name not in _FM_20MPH_EXCLUDED_MACHINES
)

# Machines that cannot take Fantasy Meadows' shortcut: an elevated arc 40 to 60 units above the racing
# line, so reaching it means holding a glide - the wheelie/bike class cannot, and Dedede rides one.
_FM_SHORTCUT_EXCLUDED_MACHINES: frozenset[str] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE,
        KARItemName.UNLOCK_MACHINE_REX_WHEELIE,
        KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER,
        KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE,
    }
)

# Every Air Ride machine that can glide onto the shortcut.
_FM_SHORTCUT_MACHINES: list[str] = sorted(
    name
    for name in items_by_type[KARItemType.MACHINE_UNLOCK]
    if GameMode.AIRRIDE in ITEM_TABLE[name].source_modes and name not in _FM_SHORTCUT_EXCLUDED_MACHINES
)

# Item types Tac can carry off in the city: every City Trial item unlock except All Up, whose city fall
# chance is zero. The legendary pieces stay in - their carrier box is a real pickup.
_TAC_STEALABLE_ITEM_UNLOCKS: list[str] = sorted(
    items_by_type[KARItemType.CT_ITEM_UNLOCK] - {KARItemName.UNLOCK_ITEM_ALL_UP}
)

# Item-count CT locations. The in-game pickup counter tallies every itemkind EXCEPT the three box types,
# so a cell here just needs one counting type able to spawn -- types respawn, so one unlock suffices.
_ITEM_PICKUP_LOCATIONS: tuple[str, ...] = (
    CTLocation.GET_50_ITEMS,
    CTLocation.GET_10_ITEMS_IN_20S,
    CTLocation.PICKUP_100_ITEMS,
    CTLocation.PICKUP_500_ITEMS,
    CTLocation.PICKUP_1000_ITEMS,
    CTLocation.PICKUP_3000_ITEMS,
)

# Patch-dependent CT locations (when city_trial_patches_gated is ON)
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

# Box-break CT locations: breaking boxes needs some box color able to spawn.
_BOX_BREAK_LOCATIONS: tuple[str, ...] = (
    CTLocation.BREAK_500_BOXES,
    CTLocation.BREAK_1000_BOXES,
)

# The per-color Archipelago counts: a locked color never spawns, so each needs its own color rather
# than any of the three.
_AP_BOX_COLOR_RULES: dict[str, str] = {
    APLocation.BREAK_20_BLUE_BOXES: KARItemName.UNLOCK_BOX_BLUE,
    APLocation.BREAK_10_GREEN_BOXES: KARItemName.UNLOCK_BOX_GREEN,
    APLocation.BREAK_10_RED_BOXES: KARItemName.UNLOCK_BOX_RED,
}

# A box color spawns only when it is unlocked AND its contents pool still holds something: the three
# colors draw from disjoint pools, and the mod drops a color whose whole pool is locked out. Blue holds
# the patches plus the 12 foods (only the patch and item gates together empty it), green the special
# items (item gate), red the 11 copy abilities (ability gate) plus the ungated legendary-piece carrier
# box, which keeps red coming while any piece is unlocked. All Up never joins blue - its fall chance
# in the city is zero.
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


def _box_color_requirements(gated: typing.Callable[[str], bool]) -> dict[str, list[Rule]]:
    """
    What each box color needs before one can spawn, as a list of rules to AND; `gated(option)` answers
    whether that category holds keys this seed. Both halves are conditional - the color's own unlock only
    while the box gate is on, its contents only while the gates that can empty the pool are - so an empty
    list means the color spawns unconditionally.
    """
    requirements: dict[str, list[Rule]] = {
        KARItemName.UNLOCK_BOX_BLUE: [],
        KARItemName.UNLOCK_BOX_GREEN: [],
        KARItemName.UNLOCK_BOX_RED: [],
    }

    if gated("city_trial_boxes_gated"):
        for color, rules in requirements.items():
            rules.append(Has(color))

    if gated("city_trial_items_gated"):
        requirements[KARItemName.UNLOCK_BOX_GREEN].append(HasAny(*_GREEN_BOX_ITEMS))
        if gated("city_trial_patches_gated"):
            requirements[KARItemName.UNLOCK_BOX_BLUE].append(
                HasAny(*sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK]), *_BLUE_BOX_FOOD_ITEMS)
            )
        if gated("abilities_gated"):
            requirements[KARItemName.UNLOCK_BOX_RED].append(
                HasAny(*sorted(items_by_type[KARItemType.ABILITY_UNLOCK]), *LEGENDARY_PIECE_UNLOCK_ITEMS)
            )

    return requirements


def _all_of(rules: list[Rule]) -> Rule:
    """AND a non-empty list of rules together."""
    combined = rules[0]
    for rule in rules[1:]:
        combined &= rule
    return combined


# TR item-dependent locations (when top_ride_items_gated is ON). The four ability-themed TR items accept
# a second key and live in _TR_ABILITY_ITEM_LOCATION_RULES.
_TR_ITEM_LOCATION_RULES: dict[str, str] = {
    TRLocation.FIRST_WHILE_HOLDING_HAMMER: KARItemName.UNLOCK_TR_ITEM_HAMMER,
    TRLocation.GET_20_INVINCIBLE_CANDY_ITEMS: KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY,
    TRLocation.BUZZ_SAW_SEND_3_RIVALS: KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW,
    TRLocation.GET_20_SPINNER_ITEMS: KARItemName.UNLOCK_TR_ITEM_SPINNER,
}

# Generic item-count TR locations: completing them only needs SOME Top Ride item type able to spawn.
_TR_ANY_ITEM_LOCATIONS: tuple[str, ...] = (
    TRLocation.COLLECT_500_ITEMS,
    TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE,
)

# TR locations that depend on an ability-themed TR item spawning, mapped to that item's two keys:
# (TR item unlock, copy ability unlock).
_TR_ABILITY_ITEM_LOCATION_RULES: dict[str, tuple[str, str]] = {
    TRLocation.FIRE_FIRST_WHILE_HOLDING_FIRE_ITEM: (
        KARItemName.UNLOCK_TR_ITEM_FIRE,
        KARItemName.UNLOCK_ABILITY_FIRE,
    ),
    TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM: (
        KARItemName.UNLOCK_TR_ITEM_FIRE,
        KARItemName.UNLOCK_ABILITY_FIRE,
    ),
    TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS: (
        KARItemName.UNLOCK_TR_ITEM_BOMB,
        KARItemName.UNLOCK_ABILITY_BOMB,
    ),
    TRLocation.GET_20_WALKY_ITEMS: (
        KARItemName.UNLOCK_TR_ITEM_WALKY,
        KARItemName.UNLOCK_ABILITY_MIC,
    ),
}

# The eight standard Air Ride courses. Nebula Belt (the secret course) is excluded: the cell is worded
# "standard" courses, so requiring it would be too strict.
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

# Swallow-a-named-enemy checkboxes: the course(s) each enemy spawns on, from the vanilla stage spawn
# tables. Independent of the ability half in _ABILITY_LOCATION_RULES; the two compose with AND.
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

# Nebula Belt ships no enemy spawn table at all, so nothing that needs an enemy can be done there.
# Every other course spawns enemies.
_AR_ENEMY_COURSE_UNLOCKS: tuple[str, ...] = _AR_STANDARD_COURSE_UNLOCKS

# Mode-root cells that just need enemies on the course - some to inhale, or some to run a count up on.
_AR_ENEMY_DEPENDENT_LOCATIONS: tuple[str, ...] = (
    ARLocation.SWALL_5_GARBAGE_AND_FIRST,
    ARLocation.SWALL_200_ENEMIES,
    ARLocation.DEFEAT_300_OF_YOUR_ENEMIES,
    ARLocation.DEFEAT_1000_OF_YOUR_ENEMIES,
    ARLocation.DEFEAT_100_ENEMIES_WITH_EXHALED_STARS,
    ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN,
)

# Courses each ability's source enemy spawns on. Swallowing that one enemy is one of the two ways to an
# ability in Air Ride (the other is a ground copy panel below); the mode ships no item spawns, and the
# random wheel a multi-enemy swallow opens is not logic. Sword Knight's list is shared with its swallow cell.
_SWORD_KNIGHT_COURSES: tuple[str, ...] = _SWALLOW_ENEMY_COURSE_RULES[ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST]

# Phan Phan and Dayl - every course but Celestial Valley.
_FIRE_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Noddy.
_SLEEP_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Flappy.
_WING_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Pichikuri. Beanstalk Park is left out although it spawns them: its enemies sit too late on a track too
# short to take the ability to the line in 1st.
_NEEDLE_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
)

# Caller.
_TORNADO_ENEMY_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
)

# Courses carrying a ground copy panel. Driving over one spins the wheel for a random unlocked ability
# with no enemy and no inhale involved, so it reaches any ability given retries. Nebula Belt ships four -
# its only ability source, since it spawns no enemies at all - and Celestial Valley the single one on top
# of the tree. No other course ships any.
_AR_COPY_PANEL_COURSES: tuple[str, ...] = (
    KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
)

# Per ability cell, the panel courses that can finish it. Tornado's cell also wants 15 enemies defeated,
# which rules out enemy-less Nebula Belt however the ability was obtained.
_AR_ABILITY_PANEL_COURSES: dict[str, tuple[str, ...]] = {
    ARLocation.FIRST_WITH_FIRE_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.FIRST_WITH_SLEEP_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.FIRST_WITH_WING_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: _AR_COPY_PANEL_COURSES,
    ARLocation.SWORD_CHALLENGE_10_SWINGS: _AR_COPY_PANEL_COURSES,
    ARLocation.TORNADO_CHALLENGE_15_KO: (KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,),
}


def _with_panels(enemy_courses: tuple[str, ...], location: str) -> tuple[str, ...]:
    """Enemy courses for an ability cell plus the panel courses that can stand in for them."""
    panels = _AR_ABILITY_PANEL_COURSES[location]
    return enemy_courses + tuple(c for c in panels if c not in enemy_courses)


# Air Ride cells that live in the mode-root region but only complete on a subset of courses. Without a
# rule here the blanket "any course unlocked" rule below would call them reachable on any single course.
_AR_COURSE_SUBSET_RULES: dict[str, tuple[str, ...]] = {
    **_SWALLOW_ENEMY_COURSE_RULES,
    **dict.fromkeys(_AR_ENEMY_DEPENDENT_LOCATIONS, _AR_ENEMY_COURSE_UNLOCKS),
    # Cells naming a copy ability: the course has to spawn that ability's enemy or carry a copy panel.
    ARLocation.FIRST_WITH_FIRE_ABILITY: _with_panels(_FIRE_ENEMY_COURSES, ARLocation.FIRST_WITH_FIRE_ABILITY),
    ARLocation.FIRST_WITH_SLEEP_ABILITY: _with_panels(_SLEEP_ENEMY_COURSES, ARLocation.FIRST_WITH_SLEEP_ABILITY),
    ARLocation.FIRST_WITH_WING_ABILITY: _with_panels(_WING_ENEMY_COURSES, ARLocation.FIRST_WITH_WING_ABILITY),
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: _with_panels(_NEEDLE_ENEMY_COURSES, ARLocation.FIRST_WITH_NEEDLE_ABILITY),
    ARLocation.TORNADO_CHALLENGE_15_KO: _with_panels(_TORNADO_ENEMY_COURSES, ARLocation.TORNADO_CHALLENGE_15_KO),
    ARLocation.SWORD_CHALLENGE_10_SWINGS: _with_panels(_SWORD_KNIGHT_COURSES, ARLocation.SWORD_CHALLENGE_10_SWINGS),
    # Celestial Valley and Beanstalk Park are the only courses with a cliff that drops you.
    ARLocation.DROP_FROM_CLIFFS_3X: (
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    ),
    # Crossing the line airborne needs something to launch off near the finish. Checker Knights and
    # Frozen Hillside have nothing usable there; Magma Flows only works with a patch stack, which is not logic.
    ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR: (
        KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
        KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
        KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    ),
}

# All seven Top Ride courses -- Top Ride has no secret course, so "all courses" means every one.
_TR_COURSE_UNLOCKS: tuple[str, ...] = (
    KARItemName.UNLOCK_TR_COURSE_GRASS,
    KARItemName.UNLOCK_TR_COURSE_SAND,
    KARItemName.UNLOCK_TR_COURSE_SKY,
    KARItemName.UNLOCK_TR_COURSE_FIRE,
    KARItemName.UNLOCK_TR_COURSE_WATER,
    KARItemName.UNLOCK_TR_COURSE_LIGHT,
    KARItemName.UNLOCK_TR_COURSE_METAL,
)

# Top Ride cells in the mode-root region that only complete on a subset of courses - the twin of
# _AR_COURSE_SUBSET_RULES. Without a rule the blanket "any course unlocked" rule would call them reachable.
_TR_COURSE_SUBSET_RULES: dict[str, tuple[str, ...]] = {
    # Four of the seven. Sky, Water and Fire are clearable but grind long enough that logic should not
    # require them (Fire only comes close with the handicap slider at 1). Metal is the hardest one kept.
    TRLocation.LAP_NO_WALLS_AND_FIRST: (
        KARItemName.UNLOCK_TR_COURSE_GRASS,
        KARItemName.UNLOCK_TR_COURSE_SAND,
        KARItemName.UNLOCK_TR_COURSE_LIGHT,
        KARItemName.UNLOCK_TR_COURSE_METAL,
    ),
}

# Top Ride checkboxes that require finishing/placing on every course.
_TR_ALL_COURSES_LOCATIONS: tuple[str, ...] = (
    TRLocation.FIRST_ON_ALL_COURSES,
    TRLocation.ALL_COURSES_NO_BOOST,
    TRLocation.FIRST_ON_ALL_COURSES_WITHOUT_BOOST,
    TRLocation.NOITEMS_ALL_COURSES,
    TRLocation.NOITEMS_FIRST_ALL_COURSES,
)

# The four ability-themed Top Ride items, TR item unlock -> copy ability unlock. The mod enables the
# item when either is held; the other 17 TR item types are keyed solely by their TR item unlock.
_TR_ABILITY_ITEM_KEYS: dict[str, str] = {
    KARItemName.UNLOCK_TR_ITEM_FREEZE_FAN: KARItemName.UNLOCK_ABILITY_FREEZE,
    KARItemName.UNLOCK_TR_ITEM_FIRE: KARItemName.UNLOCK_ABILITY_FIRE,
    KARItemName.UNLOCK_TR_ITEM_BOMB: KARItemName.UNLOCK_ABILITY_BOMB,
    KARItemName.UNLOCK_TR_ITEM_WALKY: KARItemName.UNLOCK_ABILITY_MIC,
}


def set_rules(world: "KARWorld"):
    """Define the logic rules, skipping locations and regions absent from this world."""

    # Accumulate rules per entrance/location, then apply once at the end: world.set_rule() resolves a
    # Rule into a Rule.Resolved that is not a Rule, so composing afterwards would overwrite, not AND.
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

    def add_region_entrance_rule(region_name: str, rule: Rule) -> None:
        # Skip silently if the region wasn't built (its mode is absent from logic_modes).
        try:
            region = world.get_region(region_name)
        except KeyError:
            return
        if region.entrances:
            add_entrance_rule(region.entrances[0].name, rule)

    # Entrance rules: progressive stadiums. Gating OFF needs none - the mod unlocks all 24 at connect.
    # The guard is effective_gates, not the raw option: a goal-less logic mode holds no keys, so its
    # Archipelago boxes would sit behind an unguarded entrance for fill to hide progression behind.
    if "city_trial_stadiums_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in STADIUM_REGION_TO_UNLOCK and region.entrances:
                unlock = STADIUM_REGION_TO_UNLOCK[region.name]
                add_entrance_rule(region.entrances[0].name, Has(unlock))
            elif region.name in STADIUM_ALL_REGION_TO_UNLOCKS and region.entrances:
                unlocks = STADIUM_ALL_REGION_TO_UNLOCKS[region.name]
                add_entrance_rule(region.entrances[0].name, HasAny(*unlocks))
    elif KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE in world.goal_forced_unlocks:
        # Gating off, but the beat_king_dedede goal keeps this one unlock in the pool, so its stadium is
        # the only one in the rotation that still needs a key. Every cell in there is behind it.
        add_region_entrance_rule(KARRegion.STADIUM_VSKD, Has(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE))

    # Entrance rules: AR course unlocks (effective_gates guard - see above)
    if "air_ride_courses_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in AR_COURSE_REGION_TO_UNLOCK and region.entrances:
                add_entrance_rule(region.entrances[0].name, Has(AR_COURSE_REGION_TO_UNLOCK[region.name]))

    # Entrance rules: TR course unlocks (effective_gates guard - see above)
    if "top_ride_courses_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in TR_COURSE_REGION_TO_UNLOCK and region.entrances:
                add_entrance_rule(region.entrances[0].name, Has(TR_COURSE_REGION_TO_UNLOCK[region.name]))

    # Entrance rules: the combat stadiums need some way to deal damage - every cell there is a KO count.
    # Only while both gates hold keys: machines OFF hands over Dedede and Meta Knight, base abilities OFF
    # hands over quick spin. Ramming does not count; a machine is transport here, not a weapon.
    if {"machines_gated", "base_abilities_gated"} <= world.effective_gates:
        combat_keys = (KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN, *CHARACTER_MACHINE_UNLOCKS)

        # Neither melee stage ships an ItemNode, so no copy panel spawns and a copy ability is no answer
        # whatever the ability gate. Inhale is: an inhaled enemy is spat back at the rest.
        add_region_entrance_rule(
            KARRegion.STADIUM_KM_ALL,
            HasAny(*combat_keys, KARItemName.UNLOCK_BASE_ABILITY_INHALE),
        )

        # The derby arena and the Dedede arena both spawn copy panels, so abilities OFF is a third way
        # to have a damage source and drops the rule entirely.
        if "abilities_gated" in world.effective_gates:
            add_region_entrance_rule(
                KARRegion.STADIUM_DD_ALL,
                # Hydra is the one machine heavy enough to KO by ramming, and it only moves on a boost.
                HasAny(*combat_keys, *DAMAGING_ABILITY_UNLOCKS)
                | HasAll(KARItemName.UNLOCK_MACHINE_HYDRA, KARItemName.UNLOCK_BASE_ABILITY_CHARGE),
            )
            # VS King Dedede is fought on foot, so no machine is an answer there.
            add_region_entrance_rule(
                KARRegion.STADIUM_VSKD,
                HasAny(*combat_keys, *DAMAGING_ABILITY_UNLOCKS),
            )

    # "Unlock Hydra/Dragoon Parts ... on the Checklist!" completes only once the player has received the
    # three corresponding CT_REWARD_*_PART_* items -- each performs the in-game part unlock on delivery.
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

    if world.options.city_trial_events_gated:
        for loc, item in _EVENT_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.abilities_gated:
        for loc, item in _ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.base_abilities_gated:
        for loc, item in _BASE_ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

        # The Air Ride cells naming a copy ability have two sources: swallow that ability's enemy, which
        # needs Inhale, or drive over a ground copy panel, which needs neither Inhale nor an enemy. Which
        # courses offer which is the course rule's job; this only drops the Inhale half once a panel
        # course is in play. With courses ungated every course is open, so a panel always is too and the
        # cells need no Inhale at all.
        if world.air_ride_enabled and world.options.air_ride_courses_gated:
            inhale = Has(KARItemName.UNLOCK_BASE_ABILITY_INHALE)
            for loc, panels in _AR_ABILITY_PANEL_COURSES.items():
                add_location_rule(loc, inhale | HasAny(*panels))

    # Course-subset cells sit in the generic Air Ride region, so without this they would be reachable
    # with no course that can actually complete them unlocked.
    if world.air_ride_enabled and world.options.air_ride_courses_gated:
        for loc, courses in _AR_COURSE_SUBSET_RULES.items():
            add_location_rule(loc, HasAny(*courses))

    # machines_gated OFF needs no machine rules: the mod unlocks every machine at connect, in all modes.
    if world.options.machines_gated:
        for loc, item in _MACHINE_SINGLE_RULES.items():
            add_location_rule(loc, Has(item))
        for loc, (item_a, item_b) in _MACHINE_PAIR_RULES.items():
            add_location_rule(loc, HasAll(item_a, item_b))
        # Unlike the "on <machine>" cells this one names no machine, but it still needs a specific
        # kind of one - see _FM_20MPH_EXCLUDED_MACHINES.
        add_location_rule(ARLocation.FM_LAP_ABOVE_20_MPH, HasAny(*_FM_20MPH_MACHINES))
        # Same shape in the Target Flight stadium - see _TF_AIRBORNE_EXCLUDED_MACHINES.
        add_location_rule(CTLocation.STADIUM_TF_AIRBORNE_15_SECONDS, HasAny(*_TF_AIRBORNE_MACHINES))

    if world.options.city_trial_items_gated:
        for loc, item in _ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))
        # "Steal over 8 items from Tac" needs something in the city for Tac to steal. Composes with the
        # Tac event unlock above when the event gate is on as well: Tac has to show up AND have loot.
        add_location_rule(CTLocation.STEAL_8_FROM_TAC, HasAny(*_TAC_STEALABLE_ITEM_UNLOCKS))
        # "In one match, complete both Dragoon and Hydra!" needs every piece to spawn. (As the
        # hydra_and_dragoon goal the cell is excluded here and its victory event is gated instead.)
        add_location_rule(CTLocation.COMPLETE_DRAGOON_AND_HYDRA, HasAll(*LEGENDARY_PIECE_UNLOCK_ITEMS))

    if world.options.city_trial_patches_gated:
        for loc, item in _PATCH_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    # Breaking boxes needs one color both unlocked and still holding contents. effective_gates and the
    # raw options agree here (the cells only exist with a City Trial goal); sharing the helper keeps the
    # per-color halves in one place.
    box_requirements = _box_color_requirements(lambda option: option in world.effective_gates)
    if all(box_requirements.values()):
        colors = [_all_of(rules) for rules in box_requirements.values()]
        any_box = colors[0]
        for color in colors[1:]:
            any_box |= color
        for loc in _BOX_BREAK_LOCATIONS:
            add_location_rule(loc, any_box)

    if (
        world.options.city_trial_items_gated
        and world.options.city_trial_patches_gated
        and world.options.abilities_gated
    ):
        # Three gates split the counting types between them -- items, patches, and abilities (copy
        # panels) -- so a rule is only needed when all three are on; otherwise some type always spawns.
        any_ct_counting_item = HasAny(
            *sorted(items_by_type[KARItemType.CT_ITEM_UNLOCK]),
            *sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK]),
            *sorted(items_by_type[KARItemType.ABILITY_UNLOCK]),
        )
        for loc in _ITEM_PICKUP_LOCATIONS:
            add_location_rule(loc, any_ct_counting_item)

    if world.options.top_ride_items_gated:
        for loc, item in _TR_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))
        # The copy ability counts as a second key only while abilities are gated -- otherwise they are
        # handed out at connect and the mod ignores them here.
        for loc, (tr_item, ability) in _TR_ABILITY_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, HasAny(tr_item, ability) if world.options.abilities_gated else Has(tr_item))

    if world.air_ride_enabled and world.options.air_ride_courses_gated:
        # Mode-root cells still need SOME course to race on; course-specific ones already gate on their
        # course entrance. FILL_100 is skipped because its count rule, applied later, would overwrite this
        # one; RACE_ALL gets the stronger all-eight rule; course-subset cells carry a stricter one already.
        any_ar_course = HasAny(*sorted(items_by_type[KARItemType.AR_COURSE_UNLOCK]))
        ar_course_skip = (
            ARLocation.FILL_IN_100_CHECKLIST_BLOCKS,
            ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES,
            *_AR_COURSE_SUBSET_RULES,
        )
        for name, data in AIR_RIDE_LOCATION_TABLE.items():
            if data.region in AR_COURSE_REGION_TO_UNLOCK:
                continue
            if name in ar_course_skip:
                continue
            add_location_rule(name, any_ar_course)
        add_location_rule(
            ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES,
            HasAll(*_AR_STANDARD_COURSE_UNLOCKS),
        )

    if world.top_ride_enabled and world.options.top_ride_courses_gated:
        # As with Air Ride: mode-root cells need one course, FILL_100 is skipped (count rule set later),
        # the all-courses cells need all seven, and course-subset cells already carry a stricter rule.
        any_tr_course = HasAny(*sorted(items_by_type[KARItemType.TR_COURSE_UNLOCK]))
        tr_course_skip = (
            TRLocation.FILL_IN_100_CHECKLIST_BLOCKS,
            *_TR_ALL_COURSES_LOCATIONS,
            *_TR_COURSE_SUBSET_RULES,
        )
        for name, data in TOP_RIDE_LOCATION_TABLE.items():
            if data.region in TR_COURSE_REGION_TO_UNLOCK:
                continue
            if name in tr_course_skip:
                continue
            add_location_rule(name, any_tr_course)
        for loc in _TR_ALL_COURSES_LOCATIONS:
            add_location_rule(loc, HasAll(*_TR_COURSE_UNLOCKS))
        for loc, courses in _TR_COURSE_SUBSET_RULES.items():
            add_location_rule(loc, HasAny(*courses))

    if world.city_trial_enabled and world.options.city_trial_stadiums_gated:
        # "Play in over N stadium modes!" needs strictly more than N unlocked (a locked stadium can't be
        # entered), so "over 10"/"over 20" require 11/21 of the 24.
        add_location_rule(CTLocation.STADIUM_PLAY_10_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=11))
        add_location_rule(CTLocation.STADIUM_PLAY_20_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=21))

    if world.top_ride_enabled and world.options.top_ride_items_gated:
        tr_unlocks = sorted(items_by_type[KARItemType.TR_ITEM_UNLOCK])

        # "Get over 18 different types of items!" needs 19 of the 21 distinct TR item types able to spawn.
        # The ability-themed types' second key is left out - HasFromListUnique counts distinct held
        # items, so listing both would score one type twice - which only makes the rule stricter.
        add_location_rule(
            TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS,
            HasFromListUnique(*tr_unlocks, count=19),
        )

        # "Collect N items" / "get the same item 3 times" only need ONE type able to spawn, so any of
        # the 21 TR item unlocks does -- plus the four copy abilities when abilities are gated.
        any_item_keys = list(tr_unlocks)
        if world.options.abilities_gated:
            any_item_keys += sorted(_TR_ABILITY_ITEM_KEYS.values())
        any_tr_item = HasAny(*any_item_keys)
        for loc in _TR_ANY_ITEM_LOCATIONS:
            add_location_rule(loc, any_tr_item)

    # Archipelago checklist rules read effective_gates, not the raw options: the mode blocks above can
    # use the raw option because a goal-less mode assigns none of its own boxes, but Archipelago boxes
    # exist in every AP seed and the raw option would gate one on an unlock that was never minted.
    if "city_trial_items_gated" in world.effective_gates:
        for loc, item in _AP_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    # The two "assemble" boxes need every piece of their set able to spawn: a piece is spawn-gated when
    # its whole category is, or - with that gate off - when it is one of this seed's goal keys and the
    # mod is withholding just those bits.
    ct_items_keyed = "city_trial_items_gated" in world.effective_gates
    star_pieces_keyed = ct_items_keyed or set(AP_STAR_PIECE_UNLOCK_ITEMS) <= world.goal_forced_unlocks
    legendary_pieces_keyed = ct_items_keyed or set(LEGENDARY_PIECE_UNLOCK_ITEMS) <= world.goal_forced_unlocks
    if star_pieces_keyed:
        # The machine item is not required: assembling the star mounts it, the same way assembling
        # Hydra from parts hands over Hydra.
        add_location_rule(APLocation.ASSEMBLE_ARCHIPELAGO_STAR, HasAll(*AP_STAR_PIECE_UNLOCK_ITEMS))
    # Twelve pieces inside one round: both vanilla sets plus the whole Archipelago set. The two halves
    # are gated independently - a City Trial goal can key the vanilla pieces while the spheres stay free.
    all_three_keys = (
        *(AP_STAR_PIECE_UNLOCK_ITEMS if star_pieces_keyed else ()),
        *(LEGENDARY_PIECE_UNLOCK_ITEMS if legendary_pieces_keyed else ()),
    )
    if all_three_keys:
        add_location_rule(APLocation.ASSEMBLE_ALL_THREE_LEGENDARIES, HasAll(*all_three_keys))

    if "abilities_gated" in world.effective_gates:
        # Both Mic boxes need the ability itself. The wheel one does not need inhale - the Copy Chance
        # Wheel hands the ability over in the city.
        add_location_rule(APLocation.GET_MIC_FROM_COPY_CHANCE, Has(KARItemName.UNLOCK_ABILITY_MIC))
        add_location_rule(APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY, Has(KARItemName.UNLOCK_ABILITY_MIC))

    if "base_abilities_gated" in world.effective_gates:
        # A melee stadium spawns no copy panels, so the only Mic there is a swallowed Walky.
        add_location_rule(APLocation.KM_KO_10_ENEMIES_AS_MIC_KIRBY, Has(KARItemName.UNLOCK_BASE_ABILITY_INHALE))
        # Bulk Star gets its speed from charge releases, so 1st place on it needs Charge. Independent of
        # machines_gated, which only decides whether the machine itself is a key.
        add_location_rule(APLocation.SR1_FINISH_1ST_ON_BULK_STAR, Has(KARItemName.UNLOCK_BASE_ABILITY_CHARGE))

    if "city_trial_patches_gated" in world.effective_gates:
        add_location_rule(APLocation.GET_10_HP_PATCHES, Has(KARItemName.UNLOCK_PATCH_HP))

    for loc, box_item in _AP_BOX_COLOR_RULES.items():
        if box_requirements[box_item]:
            add_location_rule(loc, _all_of(box_requirements[box_item]))

    if "machines_gated" in world.effective_gates:
        # Breaking the coral, leaving the map, riding up to the sky garden or Castle Hall's roof, and
        # climbing to the city's ceiling all need a machine; any City Trial one does. The rooftop boxes
        # ask for a dismount up top, but only a machine gets there - low spots stay region-only.
        any_ct_machine = HasAny(*_CT_MACHINE_UNLOCKS)
        if "base_abilities_gated" in world.effective_gates:
            # Hydra and Bulk Star cannot move and Slick / Turbo Star cannot be steered until Charge is
            # in, so those only count as a ride alongside it.
            any_ct_machine = HasAny(*_STEERABLE_CT_MACHINES) | (
                Has(KARItemName.UNLOCK_BASE_ABILITY_CHARGE) & HasAny(*_CHARGE_DEPENDENT_CT_MACHINES)
            )
        add_location_rule(APLocation.BREAK_ALL_CORAL, any_ct_machine)
        add_location_rule(APLocation.GO_OUT_OF_BOUNDS, any_ct_machine)
        add_location_rule(APLocation.CASTLE_FLOWER_ON_FOOT, any_ct_machine)
        add_location_rule(APLocation.SKY_GARDEN_TOP_ON_FOOT, any_ct_machine)
        add_location_rule(APLocation.FLY_TO_HIGHEST_POINT, any_ct_machine)
        add_location_rule(APLocation.SR1_FINISH_1ST_ON_BULK_STAR, Has(KARItemName.UNLOCK_MACHINE_BULK_STAR))
        # The AR character gate resolves a character through its machine, so Meta Knight's / Dedede's
        # machine unlock is what makes them selectable. The vanilla reward granting the same machine is
        # not a second key - machines_gated lists those as overlapping_rewards.
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
        # The City Trial stadium character grid resolves a character through its machine the same way
        # the Air Ride one does, so Dedede's machine is what makes him selectable for a derby.
        add_location_rule(APLocation.DD_KO_10_KIRBYS_AS_KING_DEDEDE, Has(KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE))
        # Like the 20 mph cell this one names no machine but still needs a specific kind of one -
        # see _FM_SHORTCUT_EXCLUDED_MACHINES.
        add_location_rule(APLocation.FANTASY_MEADOWS_TAKE_SHORTCUT, HasAny(*_FM_SHORTCUT_MACHINES))

    if "colors_gated" in world.effective_gates:
        add_location_rule(APLocation.SR1_FINISH_1ST_3X_AS_PURPLE, Has(KARItemName.UNLOCK_COLOR_PURPLE))
        # The mod counts one finished Air Ride race per color, so every color has to be selectable.
        add_location_rule(
            APLocation.AIR_RIDE_RACE_AS_EVERY_COLOR,
            HasAll(*sorted(items_by_type[KARItemType.COLOR_UNLOCK])),
        )

    for entrance_name, rule in entrance_rules.items():
        world.set_rule(world.get_entrance(entrance_name), rule)
    for location_name, rule in location_rules.items():
        world.set_rule(world.get_location(location_name), rule)

    # "Fill in over 100 Checklist blocks!" auto-completes once 100 of that mode's OTHER boxes are filled;
    # without the rule, fill could strand an early item behind ~100 checks. The count excludes the cell
    # itself, else it recurses. Raw callable, so it bypasses the compose pass above.
    for enabled, mode, fill_100_location in (
        (world.city_trial_enabled, GameMode.CITYTRIAL, CTLocation.FILL_IN_100_CHECKLIST_BLOCKS),
        (world.air_ride_enabled, GameMode.AIRRIDE, ARLocation.FILL_IN_100_CHECKLIST_BLOCKS),
        (world.top_ride_enabled, GameMode.TOPRIDE, TRLocation.FILL_IN_100_CHECKLIST_BLOCKS),
    ):
        if not enabled:
            continue
        try:
            fill_100 = world.get_location(fill_100_location)
        except KeyError:
            continue  # excluded as this mode's goal, or otherwise absent
        world.set_rule(
            fill_100,
            create_n_blocks_rule(world, mode, 100, exclude_location_name=fill_100_location),
        )
