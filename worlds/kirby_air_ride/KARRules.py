import typing

from rule_builder.rules import Has, HasAll, HasAny, HasFromListUnique, Rule

from .KARData import GameMode
from .KARItems import (
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

# Base-ability-dependent locations (when base_abilities_gated is ON). Charge is intentionally absent --
# no check obviously needs it yet.
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
    # Air Ride + Top Ride quick-spin cells
    ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    TRLocation.QUICK_SPIN_20_AND_FIRST: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
    TRLocation.FIRST_WHILE_DOING_A_QUICK_SPIN: KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN,
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
    APLocation.COLLECT_10_ALL_UPS: KARItemName.UNLOCK_ITEM_ALL_UP,
    APLocation.EAT_3_ICE_CREAMS: KARItemName.UNLOCK_ITEM_ICE_CREAM,
    APLocation.EAT_3_RICE_BALLS: KARItemName.UNLOCK_ITEM_RICE_BALL,
    APLocation.EAT_3_CHICKENS: KARItemName.UNLOCK_ITEM_CHICKEN,
    APLocation.EAT_3_CURRIES: KARItemName.UNLOCK_ITEM_CURRY,
    APLocation.EAT_3_RAMENS: KARItemName.UNLOCK_ITEM_RAMEN,
    APLocation.EAT_3_OMELETS: KARItemName.UNLOCK_ITEM_OMELET,
    APLocation.EAT_3_HAMBURGERS: KARItemName.UNLOCK_ITEM_HAMBURGER,
    APLocation.EAT_3_APPLES: KARItemName.UNLOCK_ITEM_APPLE,
}

# Machines that can be ridden in the City Trial city. Derived from source_modes so a new machine is
# classified by the same field the item pool uses; Free Star and Steer Star are Top Ride control
# machines and drop out here.
_CT_MACHINE_UNLOCKS: list[str] = sorted(
    name for name in items_by_type[KARItemType.MACHINE_UNLOCK] if GameMode.CITYTRIAL in ITEM_TABLE[name].source_modes
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

# Box-dependent CT locations (when city_trial_boxes_gated is ON): breaking boxes needs some box type
# able to spawn.
_BOX_BREAK_LOCATIONS: tuple[str, ...] = (
    CTLocation.BREAK_500_BOXES,
    CTLocation.BREAK_1000_BOXES,
)

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

# Swallow-a-named-enemy checkboxes: the course(s) each enemy can spawn on, from the vanilla stage spawn
# tables. Independent of the ability half in _ABILITY_LOCATION_RULES -- both gates can be on at once,
# and they compose with AND.
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

# Air Ride cells that live in the mode-root region but only complete on a subset of courses. Without a
# rule here the blanket "any course unlocked" rule below would call them reachable on any single course.
_AR_COURSE_SUBSET_RULES: dict[str, tuple[str, ...]] = {
    **_SWALLOW_ENEMY_COURSE_RULES,
    # Celestial Valley and Beanstalk Park are the only courses with a cliff that drops you.
    ARLocation.DROP_FROM_CLIFFS_3X: (
        KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
        KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
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
    """
    Define the logic rules for locations in Kirby Air Ride.
    Rules are only set for locations if they are present in the world.

    :param world: Kirby Air Ride game world.
    """

    # Accumulate rules per entrance/location, then apply once at the end. world.set_rule() resolves a
    # Rule into a Rule.Resolved that does not subclass Rule, so composing after set_rule would silently
    # overwrite instead of AND-ing.
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

    # Entrance rules: progressive stadiums. Gating OFF needs none -- the mod unlocks all 24 at connect.
    #
    # The guard is effective_gates, not `*_enabled and *_gated`: an entrance guard asks "does this
    # category hold keys", and a goal-less logic mode holds none. The old question would leave an
    # Archipelago box in a goal-less mode's tree unguarded, letting fill hide progression behind it.
    if "city_trial_stadiums_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in STADIUM_REGION_TO_UNLOCK and region.entrances:
                unlock = STADIUM_REGION_TO_UNLOCK[region.name]
                add_entrance_rule(region.entrances[0].name, Has(unlock))
            elif region.name in STADIUM_ALL_REGION_TO_UNLOCKS and region.entrances:
                unlocks = STADIUM_ALL_REGION_TO_UNLOCKS[region.name]
                add_entrance_rule(region.entrances[0].name, HasAny(*unlocks))

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

    # Location rules: gating categories (applied only when gating option is ON)
    if world.options.city_trial_events_gated:
        for loc, item in _EVENT_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.abilities_gated:
        for loc, item in _ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.base_abilities_gated:
        for loc, item in _BASE_ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

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

    if world.options.city_trial_items_gated:
        for loc, item in _ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))
        # "In one match, complete both Dragoon and Hydra!" needs every piece to spawn. (As the
        # hydra_and_dragoon goal the cell is excluded here and its victory event is gated instead.)
        add_location_rule(CTLocation.COMPLETE_DRAGOON_AND_HYDRA, HasAll(*LEGENDARY_PIECE_UNLOCK_ITEMS))

    if world.options.city_trial_patches_gated:
        for loc, item in _PATCH_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if world.options.city_trial_boxes_gated:
        box_unlocks = sorted(items_by_type[KARItemType.CT_BOX_UNLOCK])
        for loc in _BOX_BREAK_LOCATIONS:
            add_location_rule(loc, HasAny(*box_unlocks))

    if (
        world.options.city_trial_items_gated
        and world.options.city_trial_patches_gated
        and world.options.abilities_gated
    ):
        # Three gates split the counting types between them -- items (food/special/misc/legendary),
        # patches, and abilities (copy panels) -- so a rule is only needed when all three are on. If any
        # is off, its types always spawn.
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
        # course entrance. FILL_100 is skipped because its count rule, applied later, would overwrite
        # this one; RACE_ALL gets the stronger all-eight-standard-courses rule instead. The course-subset
        # cells already carry a stricter HasAny over their own courses, which implies this one.
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
        # As with Air Ride: mode-root cells need at least one course, FILL_100 is skipped (count rule,
        # set later), and the all-courses cells need all seven.
        any_tr_course = HasAny(*sorted(items_by_type[KARItemType.TR_COURSE_UNLOCK]))
        tr_course_skip = (TRLocation.FILL_IN_100_CHECKLIST_BLOCKS, *_TR_ALL_COURSES_LOCATIONS)
        for name, data in TOP_RIDE_LOCATION_TABLE.items():
            if data.region in TR_COURSE_REGION_TO_UNLOCK:
                continue
            if name in tr_course_skip:
                continue
            add_location_rule(name, any_tr_course)
        for loc in _TR_ALL_COURSES_LOCATIONS:
            add_location_rule(loc, HasAll(*_TR_COURSE_UNLOCKS))

    if world.city_trial_enabled and world.options.city_trial_stadiums_gated:
        # "Play in over N stadium modes!" needs strictly more than N unlocked (a locked stadium can't be
        # entered), so "over 10"/"over 20" require 11/21 of the 24.
        add_location_rule(CTLocation.STADIUM_PLAY_10_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=11))
        add_location_rule(CTLocation.STADIUM_PLAY_20_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=21))

    if world.top_ride_enabled and world.options.top_ride_items_gated:
        tr_unlocks = sorted(items_by_type[KARItemType.TR_ITEM_UNLOCK])

        # "Get over 18 different types of items!" needs 19 of the 21 distinct TR item types able to
        # spawn, and every type carries a TR item unlock. The ability-themed types' second key is
        # deliberately left out: HasFromListUnique counts distinct held items, so listing both keys
        # would score one type twice. Omitting it only ever makes the rule stricter.
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

    # Archipelago checklist item rules, guarded on effective_gates rather than the raw *_gated options.
    # The mode blocks above may read the raw option because add_location_rule skips locations that don't
    # exist, and a goal-less mode assigns none of its own boxes. Archipelago boxes exist in every AP seed
    # regardless, so the raw option would gate one on an unlock a goal-less mode never put in the pool,
    # making it unreachable and failing the fill.
    #
    # Each box's stadium / course requirement is inherited from its region's entrance rule, so only
    # item-spawn dependencies appear here.
    if "city_trial_items_gated" in world.effective_gates:
        for loc, item in _AP_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if "city_trial_patches_gated" in world.effective_gates:
        add_location_rule(APLocation.GET_10_HP_PATCHES, Has(KARItemName.UNLOCK_PATCH_HP))

    if "machines_gated" in world.effective_gates:
        # Breaking the coral and leaving the map both need a machine to ride; any City Trial one does.
        any_ct_machine = HasAny(*_CT_MACHINE_UNLOCKS)
        add_location_rule(APLocation.BREAK_ALL_CORAL, any_ct_machine)
        add_location_rule(APLocation.GO_OUT_OF_BOUNDS, any_ct_machine)
        add_location_rule(APLocation.SR1_FINISH_1ST_ON_BULK_STAR, Has(KARItemName.UNLOCK_MACHINE_BULK_STAR))

    if "colors_gated" in world.effective_gates:
        add_location_rule(APLocation.SR1_FINISH_1ST_3X_AS_PURPLE, Has(KARItemName.UNLOCK_COLOR_PURPLE))

    # Single apply pass: write the composed rules out to the multiworld.
    for entrance_name, rule in entrance_rules.items():
        world.set_rule(world.get_entrance(entrance_name), rule)
    for location_name, rule in location_rules.items():
        world.set_rule(world.get_location(location_name), rule)

    # "Fill in over 100 Checklist blocks!" auto-completes only once 100 of that mode's OTHER boxes are
    # filled -- without the rule, fill could strand an early item behind ~100 checks. The count excludes
    # the cell itself, else it would recurse. When it IS the mode's goal it is excluded from the pool and
    # its victory event carries the equivalent rule. Raw callable, so it bypasses the compose pass above.
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
