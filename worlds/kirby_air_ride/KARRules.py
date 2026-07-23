import typing

from rule_builder.rules import CanReachLocation, CanReachRegion, Has, HasAll, HasAny, HasFromListUnique, Rule

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
    # Air Ride: swallowing a named copy-ability enemy needs that ability unlocked. That is only HALF the
    # requirement -- the enemy must also spawn, and each spawns on only a subset of courses, so under
    # air_ride_courses_gated these cells also need a spawn course.
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_SWORD,
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_WHEEL,
    ARLocation.SWALL_CHILLY_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_FREEZE,
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: KARItemName.UNLOCK_ABILITY_PLASMA,
}

# Base-ability-dependent locations (when base_abilities_gated is ON): swallow cells need Inhale,
# quick-spin cells need Quick Spin. Charge is intentionally absent - no check obviously needs it yet.
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

# Item-dependent Archipelago checklist locations (when city_trial_items_gated actually holds keys).
# The 8 foods the vanilla checklist leaves uncovered, plus the All Up counter.
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

# Machines that can be ridden in the City Trial city. Derived from source_modes rather than listed, so
# a new machine is classified by the same field the item pool already uses. Free Star and Steer Star are
# Top Ride control machines and drop out here.
_CT_MACHINE_UNLOCKS: list[str] = sorted(
    name for name in items_by_type[KARItemType.MACHINE_UNLOCK] if GameMode.CITYTRIAL in ITEM_TABLE[name].source_modes
)

# Item-count CT locations. The in-game pickup counter tallies every collected itemkind EXCEPT the three
# box types, so a cell here just needs one counting type able to spawn -- gated together by
# city_trial_items_gated (food/special/misc/legendary), city_trial_patches_gated (patches) and
# abilities_gated (copy panels). One unlock suffices since types respawn. Breaking a box does not
# advance the counter, so boxes are not a source here.
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

# Box-dependent CT locations (when city_trial_boxes_gated is ON). Breaking boxes needs some box type
# spawning, gated behind the box unlocks, so these cells gate on HasAny(box unlocks). When off, all box
# types spawn from the start and no rule is needed.
_BOX_BREAK_LOCATIONS: tuple[str, ...] = (
    CTLocation.BREAK_500_BOXES,
    CTLocation.BREAK_1000_BOXES,
)

# TR item-dependent locations (when top_ride_items_gated is ON). The four ability-themed TR items
# (Freeze Fan, Fire, Bomb, Walky) accept a second key and live in _TR_ABILITY_ITEM_LOCATION_RULES.
_TR_ITEM_LOCATION_RULES: dict[str, str] = {
    TRLocation.FIRST_WHILE_HOLDING_HAMMER: KARItemName.UNLOCK_TR_ITEM_HAMMER,
    TRLocation.GET_20_INVINCIBLE_CANDY_ITEMS: KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY,
    TRLocation.BUZZ_SAW_SEND_3_RIVALS: KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW,
    TRLocation.GET_20_SPINNER_ITEMS: KARItemName.UNLOCK_TR_ITEM_SPINNER,
}

# Generic item-count TR locations: completing them only needs SOME Top Ride item type able to spawn,
# so they gate on HasAny over every item type's keys when top_ride_items_gated is on.
_TR_ANY_ITEM_LOCATIONS: tuple[str, ...] = (
    TRLocation.COLLECT_500_ITEMS,
    TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE,
)

# TR locations that depend on an ability-themed TR item spawning, mapped to that item's two keys:
# (TR item unlock, copy ability unlock). Applied when top_ride_items_gated is ON, taking the ability
# key as an alternative only while abilities_gated is also on.
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

# Course-aggregate checkboxes ("all courses ...") complete in-game only once every course they cover is
# unlocked, since a locked course can't be raced. They gate on HasAll(course unlocks) when that mode's
# course gating is on; when off, the courses all unlock at connect and no rule is needed.

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
# tables. Applied when air_ride_courses_gated is on -- the cell only completes on a course where the
# enemy appears, so it needs HasAny(those courses). Independent of the ability half: both gates can be
# on at once, and they compose with AND.
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

# All seven Top Ride courses (Top Ride has no secret course; "all courses" means every one).
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

# The four ability-themed Top Ride items, mapping each one's TR item unlock to its copy ability
# unlock. The mod enables the item when either is held, so these four types are the only ones with two
# keys -- the other 17 TR item types are keyed solely by their TR item unlock.
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
    # Rule into a Rule.Resolved that does not subclass Rule, so a later `existing & new` compose would
    # silently overwrite instead of AND-ing. Composing one Rule per spot before set_rule avoids that.
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

    # Entrance rules: stadium sub-region prerequisites (region-based chains).
    # Guarded on logic_modes, not city_trial_enabled: a goal-less City Trial that hosts an Archipelago
    # box still has the tree, and that box must sit behind the same chain a CT player faces.
    #
    # These chain on REGIONS, not on the prerequisite locations, because a goal-less City Trial builds
    # its regions but assigns none of its own locations - and CanReachLocation resolves via
    # world.get_location(), which raises KeyError for a location that doesn't exist. add_entrance_rule
    # has no try/except (unlike add_location_rule), so that is a hard generation crash, not a soft miss.
    # Behaviour is unchanged for seeds that generate today: every prerequisite location is the sole
    # gatekeeper of the region named here and carries no location-specific rule, so CanReachLocation(X)
    # was already exactly CanReachRegion(X's region).
    if GameMode.CITYTRIAL in world.logic_modes:
        add_entrance_rule(
            f"{KARRegion.STADIUM_DD_ALL} -> {KARRegion.STADIUM_DD3}",
            CanReachRegion(KARRegion.STADIUM_DD2),
        )
        add_entrance_rule(
            f"{KARRegion.STADIUM_DD_ALL} -> {KARRegion.STADIUM_DD4}",
            CanReachRegion(KARRegion.STADIUM_DD3),
        )
        add_entrance_rule(
            f"{KARRegion.STADIUM_DD_ALL} -> {KARRegion.STADIUM_DD5}",
            CanReachRegion(KARRegion.STADIUM_DD4),
        )
        add_entrance_rule(
            f"{KARRegion.CITY_TRIAL} -> {KARRegion.STADIUM_DR4}",
            CanReachRegion(KARRegion.STADIUM_DR3),
        )
        add_entrance_rule(
            f"{KARRegion.STADIUM_KM_ALL} -> {KARRegion.STADIUM_KM2}",
            CanReachRegion(KARRegion.STADIUM_KM1),
        )

    # Entrance rules: progressive stadiums (when the category actually holds keys)
    # Stadium gating OFF needs no entrance rules: the mod unlocks all 24 stadiums at connect, so every
    # one is open from the start. The DD/KM/DR chain prerequisites are unconditional and still apply.
    #
    # The guard is effective_gates, not `*_enabled and *_gated`: the question an entrance guard asks is
    # "does this category hold keys", and a goal-less logic mode holds none. Asking the old question
    # would leave an Archipelago box in a goal-less mode's tree with no entrance rule at all - a free
    # check fill could hide progression behind. For every seed that generates today the two agree
    # exactly; they differ only where the old expression had no defined answer.
    if "city_trial_stadiums_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in STADIUM_REGION_TO_UNLOCK and region.entrances:
                unlock = STADIUM_REGION_TO_UNLOCK[region.name]
                add_entrance_rule(region.entrances[0].name, Has(unlock))
            elif region.name in STADIUM_ALL_REGION_TO_UNLOCKS and region.entrances:
                unlocks = STADIUM_ALL_REGION_TO_UNLOCKS[region.name]
                add_entrance_rule(region.entrances[0].name, HasAny(*unlocks))

    # Entrance rules: AR course unlocks (when the category actually holds keys - see above)
    if "air_ride_courses_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in AR_COURSE_REGION_TO_UNLOCK and region.entrances:
                add_entrance_rule(region.entrances[0].name, Has(AR_COURSE_REGION_TO_UNLOCK[region.name]))

    # Entrance rules: TR course unlocks (when the category actually holds keys - see above)
    if "top_ride_courses_gated" in world.effective_gates:
        for region in world.get_regions():
            if region.name in TR_COURSE_REGION_TO_UNLOCK and region.entrances:
                add_entrance_rule(region.entrances[0].name, Has(TR_COURSE_REGION_TO_UNLOCK[region.name]))

    # Location rules: legendary part checklist checkboxes (always applied when CT enabled).
    # "Unlock Hydra/Dragoon Parts ... on the Checklist!" completes in-game only once the player has
    # received the three corresponding CT_REWARD_*_PART_* items (each performs the in-game "unlock this
    # part" when delivered). Gating on those items reflects the real requirement; they are progression
    # so fill honors it.
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

    if world.options.base_abilities_gated:
        for loc, item in _BASE_ABILITY_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    # Swallow-a-named-enemy cells also need a course where that enemy spawns (independent of the ability
    # half). They live in the generic Air Ride region, so without this they would be reachable even with
    # no spawn course unlocked. When course gating is off all courses unlock at connect, so no rule.
    if world.air_ride_enabled and world.options.air_ride_courses_gated:
        for loc, courses in _SWALLOW_ENEMY_COURSE_RULES.items():
            add_location_rule(loc, HasAny(*courses))

    # machine rules, when gating is on.
    # machines_gated OFF needs no machine rules: the mod unlocks every machine at connect (all modes),
    # so the machine-specific finish/bust checkboxes are reachable from the start, City-Trial-only seeds
    # included.
    if world.options.machines_gated:
        for loc, item in _MACHINE_SINGLE_RULES.items():
            add_location_rule(loc, Has(item))
        for loc, (item_a, item_b) in _MACHINE_PAIR_RULES.items():
            add_location_rule(loc, HasAll(item_a, item_b))

    if world.options.city_trial_items_gated:
        for loc, item in _ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))
        # "In one match, complete both Dragoon and Hydra!" needs every Hydra/Dragoon piece to spawn,
        # which item gating locks behind the six piece-spawn unlocks. (When this cell is the
        # hydra_and_dragoon goal it is excluded here and its victory event is gated instead.)
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
        # These cells need one counting item type able to spawn. The counting types are locked by three
        # gates together -- items (food/special/misc/legendary), patches and abilities (copy panels) --
        # so only when all three are on is nothing available until one unlock is held. If any gate is
        # off, its types always spawn and no rule is needed.
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
        # The ability-themed items take the copy ability unlock as a second key, but only while
        # abilities are gated -- an ungated world's abilities are handed out at connect and the mod
        # ignores them here, leaving the TR item unlock as the only key.
        for loc, (tr_item, ability) in _TR_ABILITY_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, HasAny(tr_item, ability) if world.options.abilities_gated else Has(tr_item))

    if world.air_ride_enabled and world.options.air_ride_courses_gated:
        # Every non-course-specific Air Ride cell still needs SOME course to race on. Course-specific
        # cells already gate on their course entrance, so only the mode-root cells (the AIR_RIDE region)
        # get a blanket "any course unlocked" rule. FILL_100 is skipped (its count rule, applied later,
        # would be overwritten); RACE_ALL needs all eight standard courses, a stronger requirement.
        any_ar_course = HasAny(*sorted(items_by_type[KARItemType.AR_COURSE_UNLOCK]))
        for name, data in AIR_RIDE_LOCATION_TABLE.items():
            if data.region in AR_COURSE_REGION_TO_UNLOCK:
                continue
            if name in (
                ARLocation.FILL_IN_100_CHECKLIST_BLOCKS,
                ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES,
            ):
                continue
            add_location_rule(name, any_ar_course)
        add_location_rule(
            ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES,
            HasAll(*_AR_STANDARD_COURSE_UNLOCKS),
        )

    if world.top_ride_enabled and world.options.top_ride_courses_gated:
        # As with Air Ride: every non-course-specific Top Ride cell needs at least one course. Course-
        # specific cells gate on their course entrance, so only the mode-root cells get the blanket rule.
        # FILL_100 is skipped (count rule, set later); the all-courses cells need all seven.
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
        # "Play in over N stadium modes!" needs strictly more than N modes unlocked (a locked stadium
        # can't be entered), so "over 10"/"over 20" require 11/21 of the 24. When stadium gating is off
        # all 24 unlock at connect and no rule is needed.
        add_location_rule(CTLocation.STADIUM_PLAY_10_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=11))
        add_location_rule(CTLocation.STADIUM_PLAY_20_STADIUM_MODES, HasFromListUnique(*STADIUM_UNLOCK_ITEMS, count=21))

    if world.top_ride_enabled and world.options.top_ride_items_gated:
        tr_unlocks = sorted(items_by_type[KARItemType.TR_ITEM_UNLOCK])

        # "Get over 18 different types of items!" needs 19 of the 21 distinct TR item types able to
        # spawn. Every type carries a TR item unlock, so the threshold is a straight 19 of the 21.
        # The four ability-themed types accept a copy ability unlock as a second key, but that form is
        # deliberately left out: HasFromListUnique counts distinct held items, so listing both keys
        # would score one type twice. Ignoring it only ever makes the rule stricter. (With the gate OFF
        # the mod unlocks all 21 types at connect and the cell needs no rule at all.)
        add_location_rule(
            TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS,
            HasFromListUnique(*tr_unlocks, count=19),
        )

        # "Collect N items" / "get the same item 3 times" only need ONE item type able to spawn, so
        # they take any single key: any of the 21 TR item unlocks, plus the four copy abilities that
        # double as a key when abilities are gated.
        any_item_keys = list(tr_unlocks)
        if world.options.abilities_gated:
            any_item_keys += sorted(_TR_ABILITY_ITEM_KEYS.values())
        any_tr_item = HasAny(*any_item_keys)
        for loc in _TR_ANY_ITEM_LOCATIONS:
            add_location_rule(loc, any_tr_item)

    # Archipelago checklist item rules.
    #
    # Guarded on effective_gates, NOT on the raw *_gated options like the mode blocks above. Those
    # blocks may read the raw option safely because add_location_rule skips a location that doesn't
    # exist, and a goal-less mode assigns none of its own boxes. Archipelago boxes are different: they
    # exist in every AP seed regardless of which modes have goals. Reading the raw option would gate an
    # AP box on an unlock item that a goal-less mode never put in the pool, making it unreachable and
    # failing the fill. effective_gates asks the right question - does this category hold keys.
    #
    # Each box's stadium / course requirement is inherited from its region's entrance rule, so only
    # item-spawn dependencies appear here.
    if "city_trial_items_gated" in world.effective_gates:
        for loc, item in _AP_ITEM_LOCATION_RULES.items():
            add_location_rule(loc, Has(item))

    if "city_trial_patches_gated" in world.effective_gates:
        add_location_rule(APLocation.GET_10_HP_PATCHES, Has(KARItemName.UNLOCK_PATCH_HP))

    if "machines_gated" in world.effective_gates:
        # Breaking the coral and leaving the map both need a machine to ride; any City Trial machine
        # does. (Free Star and Steer Star are Top Ride control machines that never spawn in the city,
        # so they are excluded via source_modes.)
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
    # filled. When it is not this mode's goal it stays a normal location and must carry that rule, or
    # fill could strand an early item behind ~100 checks. The count rule excludes the cell itself (else
    # it would recurse). When it IS the goal it is excluded from the pool and its victory event carries
    # the equivalent rule. This rule is a raw callable, so it is applied directly here.
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
            continue  # excluded because it is this mode's goal, or otherwise absent
        world.set_rule(
            fill_100,
            create_n_blocks_rule(world, mode, 100, exclude_location_name=fill_100_location),
        )
