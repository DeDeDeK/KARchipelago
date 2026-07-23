import typing
from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum

from BaseClasses import CollectionState, LocationProgressType, Region
from rule_builder.rules import CanReachLocation, Has, HasAll, Rule

from .KARData import GameMode, location_code_to_mode_clear
from .KARItems import LEGENDARY_PIECE_UNLOCK_ITEMS, KARItem, KARItemName, KARItemType, items_by_type
from .KAROptions import CityTrialGoal


class KARRegion(StrEnum):
    """Region names for Kirby Air Ride."""

    # City Trial
    CITY_TRIAL = "City Trial"
    CT_FREE_RUN = "City Trial: Free Run"

    # Stadiums
    STADIUM_DR1 = "Stadium: DRAG RACE 1"
    STADIUM_DR2 = "Stadium: DRAG RACE 2"
    STADIUM_DR3 = "Stadium: DRAG RACE 3"
    STADIUM_DR4 = "Stadium: DRAG RACE 4"
    STADIUM_HJ = "Stadium: HIGH JUMP"
    STADIUM_TF = "Stadium: TARGET FLIGHT"
    STADIUM_AG = "Stadium: AIR GLIDER"
    STADIUM_DD_ALL = "Stadium: DESTRUCTION DERBY ALL"
    STADIUM_DD1 = "Stadium: DESTRUCTION DERBY 1"
    STADIUM_DD2 = "Stadium: DESTRUCTION DERBY 2"
    STADIUM_DD3 = "Stadium: DESTRUCTION DERBY 3"
    STADIUM_DD4 = "Stadium: DESTRUCTION DERBY 4"
    STADIUM_DD5 = "Stadium: DESTRUCTION DERBY 5"
    STADIUM_KM_ALL = "Stadium: KIRBY MELEE ALL"
    STADIUM_KM1 = "Stadium: KIRBY MELEE 1"
    STADIUM_KM2 = "Stadium: KIRBY MELEE 2"
    STADIUM_VSKD = "Stadium: VS. KING DEDEDE"
    STADIUM_SR1 = "Stadium: SINGLE RACE 1"
    STADIUM_SR2 = "Stadium: SINGLE RACE 2"
    STADIUM_SR3 = "Stadium: SINGLE RACE 3"
    STADIUM_SR4 = "Stadium: SINGLE RACE 4"
    STADIUM_SR5 = "Stadium: SINGLE RACE 5"
    STADIUM_SR6 = "Stadium: SINGLE RACE 6"
    STADIUM_SR7 = "Stadium: SINGLE RACE 7"
    STADIUM_SR8 = "Stadium: SINGLE RACE 8"
    STADIUM_SR9 = "Stadium: SINGLE RACE 9"

    # Air Ride
    AIR_RIDE = "Air Ride"
    AR_TIME_ATTACK = "Air Ride: Time Attack"
    AR_FREE_RUN = "Air Ride: Free Run"
    AR_MAGMA_FLOWS = "Air Ride: MAGMA FLOWS"
    AR_FANTASY_MEADOWS = "Air Ride: FANTASY MEADOWS"
    AR_CELESTIAL_VALLEY = "Air Ride: CELESTIAL VALLEY"
    AR_BEANSTALK_PARK = "Air Ride: BEANSTALK PARK"
    AR_FROZEN_HILLSIDE = "Air Ride: FROZEN HILLSIDE"
    AR_MACHINE_PASSAGE = "Air Ride: MACHINE PASSAGE"
    AR_SKY_SANDS = "Air Ride: SKY SANDS"
    AR_CHECKER_KNIGHTS = "Air Ride: CHECKER KNIGHTS"
    AR_NEBULA_BELT = "Air Ride: NEBULA BELT"
    AR_TA_MAGMA_FLOWS = "Air Ride: Time Attack: MAGMA FLOWS"
    AR_TA_FANTASY_MEADOWS = "Air Ride: Time Attack: FANTASY MEADOWS"
    AR_TA_CELESTIAL_VALLEY = "Air Ride: Time Attack: CELESTIAL VALLEY"
    AR_TA_BEANSTALK_PARK = "Air Ride: Time Attack: BEANSTALK PARK"
    AR_TA_FROZEN_HILLSIDE = "Air Ride: Time Attack: FROZEN HILLSIDE"
    AR_TA_MACHINE_PASSAGE = "Air Ride: Time Attack: MACHINE PASSAGE"
    AR_TA_SKY_SANDS = "Air Ride: Time Attack: SKY SANDS"
    AR_TA_CHECKER_KNIGHTS = "Air Ride: Time Attack: CHECKER KNIGHTS"
    AR_TA_NEBULA_BELT = "Air Ride: Time Attack: NEBULA BELT"
    AR_FR_MAGMA_FLOWS = "Air Ride: Free Run: MAGMA FLOWS"
    AR_FR_FANTASY_MEADOWS = "Air Ride: Free Run: FANTASY MEADOWS"
    AR_FR_CELESTIAL_VALLEY = "Air Ride: Free Run: CELESTIAL VALLEY"
    AR_FR_BEANSTALK_PARK = "Air Ride: Free Run: BEANSTALK PARK"
    AR_FR_FROZEN_HILLSIDE = "Air Ride: Free Run: FROZEN HILLSIDE"
    AR_FR_MACHINE_PASSAGE = "Air Ride: Free Run: MACHINE PASSAGE"
    AR_FR_SKY_SANDS = "Air Ride: Free Run: SKY SANDS"
    AR_FR_CHECKER_KNIGHTS = "Air Ride: Free Run: CHECKER KNIGHTS"
    AR_FR_NEBULA_BELT = "Air Ride: Free Run: NEBULA BELT"

    # Top Ride
    TOP_RIDE = "Top Ride"
    TR_TIME_ATTACK = "Top Ride: Time Attack"
    TR_FREE_RUN = "Top Ride: Free Run"
    TR_GRASS = "Top Ride: GRASS"
    TR_SAND = "Top Ride: SAND"
    TR_SKY = "Top Ride: SKY"
    TR_FIRE = "Top Ride: FIRE"
    TR_LIGHT = "Top Ride: LIGHT"
    TR_WATER = "Top Ride: WATER"
    TR_METAL = "Top Ride: METAL"
    TR_TA_GRASS = "Top Ride: Time Attack: GRASS"
    TR_TA_SAND = "Top Ride: Time Attack: SAND"
    TR_TA_SKY = "Top Ride: Time Attack: SKY"
    TR_TA_FIRE = "Top Ride: Time Attack: FIRE"
    TR_TA_LIGHT = "Top Ride: Time Attack: LIGHT"
    TR_TA_WATER = "Top Ride: Time Attack: WATER"
    TR_TA_METAL = "Top Ride: Time Attack: METAL"
    TR_FR_GRASS = "Top Ride: Free Run: GRASS"
    TR_FR_SAND = "Top Ride: Free Run: SAND"
    TR_FR_SKY = "Top Ride: Free Run: SKY"
    TR_FR_FIRE = "Top Ride: Free Run: FIRE"
    TR_FR_LIGHT = "Top Ride: Free Run: LIGHT"
    TR_FR_WATER = "Top Ride: Free Run: WATER"
    TR_FR_METAL = "Top Ride: Free Run: METAL"

    # Archipelago checklist. The mode-agnostic Archipelago boxes live here; boxes describing an
    # activity in another mode live in that mode's region instead, so the AP checklist is a tab, not a
    # place. No sub-regions.
    ARCHIPELAGO = "Archipelago"


# Ordered name-prefix table backing REGION_TO_MODE. First match wins, so the exact mode-root names come
# before their short prefixes. "ARCHIPELAGO" leads defensively; it does not collide with "AR_" today
# (str.startswith("AR_") is False for it) but the intent is clearer stated than inferred.
_REGION_MODE_NAME_PREFIXES: tuple[tuple[str, GameMode], ...] = (
    ("ARCHIPELAGO", GameMode.ARCHIPELAGO),
    ("CITY_TRIAL", GameMode.CITYTRIAL),
    ("CT_", GameMode.CITYTRIAL),
    ("STADIUM_", GameMode.CITYTRIAL),
    ("AIR_RIDE", GameMode.AIRRIDE),
    ("AR_", GameMode.AIRRIDE),
    ("TOP_RIDE", GameMode.TOPRIDE),
    ("TR_", GameMode.TOPRIDE),
)


def _build_region_to_mode() -> dict[str, GameMode]:
    """Classify every KARRegion by the game mode it belongs to, keyed by region name.

    Derived from the enum member names rather than hand-listed, and checked exhaustive here: a region
    matching no prefix raises at import instead of silently going unclassified, which would strand an
    Archipelago box in a tree that logic_modes never builds.
    """
    mapping: dict[str, GameMode] = {}
    for region in KARRegion:
        for prefix, mode in _REGION_MODE_NAME_PREFIXES:
            if region.name.startswith(prefix):
                mapping[region.value] = mode
                break
        else:
            raise ValueError(
                f"KARRegion.{region.name} matches no entry in _REGION_MODE_NAME_PREFIXES. "
                f"Every region must map to a game mode; add a prefix for it."
            )
    return mapping


# Which game mode each region belongs to. Static by construction and deliberately so: logic_modes
# decides which region trees get built and derives itself from this table (via the AP location table's
# regions), so this must never inspect built regions - that would be circular.
REGION_TO_MODE: dict[str, GameMode] = _build_region_to_mode()


# KARLocations imports are deferred into function bodies to break the circular
# dependency: KARLocations imports KARRegion from this module.
if typing.TYPE_CHECKING:
    from . import KARWorld


def create_regions_batch(world: "KARWorld", *names: str) -> list[Region]:
    """Create multiple regions and register them all with the multiworld at once."""
    regions = [Region(name, world.player, world.multiworld) for name in names]
    world.multiworld.regions += regions
    return regions


def assign_locations_to_regions(
    world: "KARWorld",
    location_table: dict,
    default_locations: Iterable[str],
    excluded_locations: Iterable[str],
    goal_locations_to_exclude: set[str],
) -> None:
    """
    Assign locations to their regions with the appropriate progress type.
    """
    from .KARLocations import KARLocation

    for locations, progress_type in [
        (default_locations, LocationProgressType.DEFAULT),
        (excluded_locations, LocationProgressType.EXCLUDED),
    ]:
        for location_name in locations:
            if location_name in goal_locations_to_exclude:
                continue
            data = location_table[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, data.code, region)
            location.progress_type = progress_type
            region.locations.append(location)


def create_regions(world: "KARWorld"):
    """
    Create regions, place locations in regions, and connect regions for the Kirby Air Ride world.
    """
    from .KARLocations import (
        AIR_RIDE_LOCATION_TABLE,
        AP_CHECKLIST_LOCATION_TABLE,
        CITY_TRIAL_LOCATION_TABLE,
        TOP_RIDE_LOCATION_TABLE,
    )

    # The Menu region is the origin that connects all enabled game modes.
    menu_region = Region(world.origin_region_name, world.player, world.multiworld)
    world.multiworld.regions.append(menu_region)

    # Two different questions, two different conditions. Whether a mode's tree is BUILT is
    # `mode in logic_modes` - a mode has a tree if it has a goal or hosts an Archipelago box. Whether
    # the mode's OWN checklist locations are assigned (below) is `*_enabled` - only a mode with a goal
    # brings its own boxes. A goal-less City Trial hosting one AP box in a stadium gets all 28 CT
    # regions with 27 of them empty; that is correct. Trees are built whole - the DD/KM/DR prerequisite
    # chains need the structure, so there are no partial trees.
    if GameMode.CITYTRIAL in world.logic_modes:
        city_trial_region = Region(KARRegion.CITY_TRIAL, world.player, world.multiworld)
        world.multiworld.regions.append(city_trial_region)
        menu_region.connect(city_trial_region)
        connect_city_trial_region(world, city_trial_region)

    if GameMode.AIRRIDE in world.logic_modes:
        air_ride_region = Region(KARRegion.AIR_RIDE, world.player, world.multiworld)
        world.multiworld.regions.append(air_ride_region)
        menu_region.connect(air_ride_region)
        connect_air_ride_region(world, air_ride_region)

    if GameMode.TOPRIDE in world.logic_modes:
        top_ride_region = Region(KARRegion.TOP_RIDE, world.player, world.multiworld)
        world.multiworld.regions.append(top_ride_region)
        menu_region.connect(top_ride_region)
        connect_top_ride_region(world, top_ride_region)

    if GameMode.ARCHIPELAGO in world.logic_modes:
        # Holds only the mode-agnostic Archipelago boxes; the rest live in the region of the mode they
        # describe. No sub-regions.
        archipelago_region = Region(KARRegion.ARCHIPELAGO, world.player, world.multiworld)
        world.multiworld.regions.append(archipelago_region)
        menu_region.connect(archipelago_region)

    if world.city_trial_enabled:
        assign_locations_to_regions(
            world,
            CITY_TRIAL_LOCATION_TABLE,
            world.city_trial_default_locations,
            world.city_trial_excluded_locations,
            world.goal_locations_to_exclude,
        )

    if world.air_ride_enabled:
        assign_locations_to_regions(
            world,
            AIR_RIDE_LOCATION_TABLE,
            world.air_ride_default_locations,
            world.air_ride_excluded_locations,
            world.goal_locations_to_exclude,
        )

    if world.top_ride_enabled:
        assign_locations_to_regions(
            world,
            TOP_RIDE_LOCATION_TABLE,
            world.top_ride_default_locations,
            world.top_ride_excluded_locations,
            world.goal_locations_to_exclude,
        )

    if world.archipelago_enabled:
        assign_locations_to_regions(
            world,
            AP_CHECKLIST_LOCATION_TABLE,
            world.archipelago_default_locations,
            world.archipelago_excluded_locations,
            world.goal_locations_to_exclude,
        )

    determine_goal(world)


def connect_city_trial_region(world: "KARWorld", city_trial_region: Region) -> None:
    create_regions_batch(
        world,
        KARRegion.CT_FREE_RUN,
        KARRegion.STADIUM_DD_ALL,
        KARRegion.STADIUM_DD1,
        KARRegion.STADIUM_DD2,
        KARRegion.STADIUM_DD3,
        KARRegion.STADIUM_DD4,
        KARRegion.STADIUM_DD5,
        KARRegion.STADIUM_DR1,
        KARRegion.STADIUM_DR2,
        KARRegion.STADIUM_DR3,
        KARRegion.STADIUM_DR4,
        KARRegion.STADIUM_HJ,
        KARRegion.STADIUM_TF,
        KARRegion.STADIUM_AG,
        KARRegion.STADIUM_KM_ALL,
        KARRegion.STADIUM_KM1,
        KARRegion.STADIUM_KM2,
        KARRegion.STADIUM_VSKD,
        KARRegion.STADIUM_SR1,
        KARRegion.STADIUM_SR2,
        KARRegion.STADIUM_SR3,
        KARRegion.STADIUM_SR4,
        KARRegion.STADIUM_SR5,
        KARRegion.STADIUM_SR6,
        KARRegion.STADIUM_SR7,
        KARRegion.STADIUM_SR8,
        KARRegion.STADIUM_SR9,
    )

    # Entrance gating rules for these exits are applied later, during rule setup.
    city_trial_region.add_exits(
        [
            KARRegion.CT_FREE_RUN,
            KARRegion.STADIUM_DD_ALL,
            KARRegion.STADIUM_DR1,
            KARRegion.STADIUM_DR2,
            KARRegion.STADIUM_DR3,
            KARRegion.STADIUM_DR4,
            KARRegion.STADIUM_HJ,
            KARRegion.STADIUM_TF,
            KARRegion.STADIUM_AG,
            KARRegion.STADIUM_KM_ALL,
            KARRegion.STADIUM_VSKD,
            KARRegion.STADIUM_SR1,
            KARRegion.STADIUM_SR2,
            KARRegion.STADIUM_SR3,
            KARRegion.STADIUM_SR4,
            KARRegion.STADIUM_SR5,
            KARRegion.STADIUM_SR6,
            KARRegion.STADIUM_SR7,
            KARRegion.STADIUM_SR8,
            KARRegion.STADIUM_SR9,
        ]
    )

    # DD_ALL and KM_ALL are parents nesting their numbered sub-stadiums.
    world.get_region(KARRegion.STADIUM_DD_ALL).add_exits(
        [
            KARRegion.STADIUM_DD1,
            KARRegion.STADIUM_DD2,
            KARRegion.STADIUM_DD3,
            KARRegion.STADIUM_DD4,
            KARRegion.STADIUM_DD5,
        ]
    )

    world.get_region(KARRegion.STADIUM_KM_ALL).add_exits(
        [
            KARRegion.STADIUM_KM1,
            KARRegion.STADIUM_KM2,
        ]
    )


AR_COURSE_REGIONS = [
    KARRegion.AR_MAGMA_FLOWS,
    KARRegion.AR_FANTASY_MEADOWS,
    KARRegion.AR_CELESTIAL_VALLEY,
    KARRegion.AR_BEANSTALK_PARK,
    KARRegion.AR_FROZEN_HILLSIDE,
    KARRegion.AR_MACHINE_PASSAGE,
    KARRegion.AR_SKY_SANDS,
    KARRegion.AR_CHECKER_KNIGHTS,
    KARRegion.AR_NEBULA_BELT,
]
AR_TA_COURSE_REGIONS = [
    KARRegion.AR_TA_MAGMA_FLOWS,
    KARRegion.AR_TA_FANTASY_MEADOWS,
    KARRegion.AR_TA_CELESTIAL_VALLEY,
    KARRegion.AR_TA_BEANSTALK_PARK,
    KARRegion.AR_TA_FROZEN_HILLSIDE,
    KARRegion.AR_TA_MACHINE_PASSAGE,
    KARRegion.AR_TA_SKY_SANDS,
    KARRegion.AR_TA_CHECKER_KNIGHTS,
    KARRegion.AR_TA_NEBULA_BELT,
]
AR_FR_COURSE_REGIONS = [
    KARRegion.AR_FR_MAGMA_FLOWS,
    KARRegion.AR_FR_FANTASY_MEADOWS,
    KARRegion.AR_FR_CELESTIAL_VALLEY,
    KARRegion.AR_FR_BEANSTALK_PARK,
    KARRegion.AR_FR_FROZEN_HILLSIDE,
    KARRegion.AR_FR_MACHINE_PASSAGE,
    KARRegion.AR_FR_SKY_SANDS,
    KARRegion.AR_FR_CHECKER_KNIGHTS,
    KARRegion.AR_FR_NEBULA_BELT,
]

TR_COURSE_REGIONS = [
    KARRegion.TR_GRASS,
    KARRegion.TR_METAL,
    KARRegion.TR_LIGHT,
    KARRegion.TR_SAND,
    KARRegion.TR_FIRE,
    KARRegion.TR_WATER,
    KARRegion.TR_SKY,
]
TR_TA_COURSE_REGIONS = [
    KARRegion.TR_TA_GRASS,
    KARRegion.TR_TA_METAL,
    KARRegion.TR_TA_LIGHT,
    KARRegion.TR_TA_SAND,
    KARRegion.TR_TA_FIRE,
    KARRegion.TR_TA_WATER,
    KARRegion.TR_TA_SKY,
]
TR_FR_COURSE_REGIONS = [
    KARRegion.TR_FR_GRASS,
    KARRegion.TR_FR_METAL,
    KARRegion.TR_FR_LIGHT,
    KARRegion.TR_FR_SAND,
    KARRegion.TR_FR_FIRE,
    KARRegion.TR_FR_WATER,
    KARRegion.TR_FR_SKY,
]


# Region-to-unlock-item mappings used for entrance gating during rule setup.

STADIUM_REGION_TO_UNLOCK: dict[str, KARItemName] = {
    KARRegion.STADIUM_DR1: KARItemName.UNLOCK_STADIUM_DRAG_RACE_1,
    KARRegion.STADIUM_DR2: KARItemName.UNLOCK_STADIUM_DRAG_RACE_2,
    KARRegion.STADIUM_DR3: KARItemName.UNLOCK_STADIUM_DRAG_RACE_3,
    KARRegion.STADIUM_DR4: KARItemName.UNLOCK_STADIUM_DRAG_RACE_4,
    KARRegion.STADIUM_HJ: KARItemName.UNLOCK_STADIUM_HIGH_JUMP,
    KARRegion.STADIUM_TF: KARItemName.UNLOCK_STADIUM_TARGET_FLIGHT,
    KARRegion.STADIUM_AG: KARItemName.UNLOCK_STADIUM_AIR_GLIDER,
    KARRegion.STADIUM_KM1: KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1,
    KARRegion.STADIUM_KM2: KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2,
    KARRegion.STADIUM_DD1: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1,
    KARRegion.STADIUM_DD2: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2,
    KARRegion.STADIUM_DD3: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3,
    KARRegion.STADIUM_DD4: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4,
    KARRegion.STADIUM_DD5: KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5,
    KARRegion.STADIUM_SR1: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_1,
    KARRegion.STADIUM_SR2: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_2,
    KARRegion.STADIUM_SR3: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_3,
    KARRegion.STADIUM_SR4: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_4,
    KARRegion.STADIUM_SR5: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_5,
    KARRegion.STADIUM_SR6: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_6,
    KARRegion.STADIUM_SR7: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_7,
    KARRegion.STADIUM_SR8: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_8,
    KARRegion.STADIUM_SR9: KARItemName.UNLOCK_STADIUM_SINGLE_RACE_9,
    KARRegion.STADIUM_VSKD: KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,
}

STADIUM_ALL_REGION_TO_UNLOCKS: dict[str, list[KARItemName]] = {
    KARRegion.STADIUM_DD_ALL: [
        KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1,
        KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2,
        KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3,
        KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4,
        KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5,
    ],
    KARRegion.STADIUM_KM_ALL: [
        KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1,
        KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2,
    ],
}

AR_COURSE_REGION_TO_UNLOCK: dict[str, KARItemName] = {
    KARRegion.AR_MAGMA_FLOWS: KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARRegion.AR_FANTASY_MEADOWS: KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARRegion.AR_CELESTIAL_VALLEY: KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARRegion.AR_BEANSTALK_PARK: KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARRegion.AR_FROZEN_HILLSIDE: KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARRegion.AR_MACHINE_PASSAGE: KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARRegion.AR_SKY_SANDS: KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARRegion.AR_CHECKER_KNIGHTS: KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    KARRegion.AR_NEBULA_BELT: KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    KARRegion.AR_TA_MAGMA_FLOWS: KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARRegion.AR_TA_FANTASY_MEADOWS: KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARRegion.AR_TA_CELESTIAL_VALLEY: KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARRegion.AR_TA_BEANSTALK_PARK: KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARRegion.AR_TA_FROZEN_HILLSIDE: KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARRegion.AR_TA_MACHINE_PASSAGE: KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARRegion.AR_TA_SKY_SANDS: KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARRegion.AR_TA_CHECKER_KNIGHTS: KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    KARRegion.AR_TA_NEBULA_BELT: KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
    KARRegion.AR_FR_MAGMA_FLOWS: KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS,
    KARRegion.AR_FR_FANTASY_MEADOWS: KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    KARRegion.AR_FR_CELESTIAL_VALLEY: KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY,
    KARRegion.AR_FR_BEANSTALK_PARK: KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK,
    KARRegion.AR_FR_FROZEN_HILLSIDE: KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE,
    KARRegion.AR_FR_MACHINE_PASSAGE: KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE,
    KARRegion.AR_FR_SKY_SANDS: KARItemName.UNLOCK_AR_COURSE_SKY_SANDS,
    KARRegion.AR_FR_CHECKER_KNIGHTS: KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS,
    KARRegion.AR_FR_NEBULA_BELT: KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
}

TR_COURSE_REGION_TO_UNLOCK: dict[str, KARItemName] = {
    KARRegion.TR_GRASS: KARItemName.UNLOCK_TR_COURSE_GRASS,
    KARRegion.TR_SAND: KARItemName.UNLOCK_TR_COURSE_SAND,
    KARRegion.TR_SKY: KARItemName.UNLOCK_TR_COURSE_SKY,
    KARRegion.TR_FIRE: KARItemName.UNLOCK_TR_COURSE_FIRE,
    KARRegion.TR_LIGHT: KARItemName.UNLOCK_TR_COURSE_LIGHT,
    KARRegion.TR_WATER: KARItemName.UNLOCK_TR_COURSE_WATER,
    KARRegion.TR_METAL: KARItemName.UNLOCK_TR_COURSE_METAL,
    KARRegion.TR_TA_GRASS: KARItemName.UNLOCK_TR_COURSE_GRASS,
    KARRegion.TR_TA_SAND: KARItemName.UNLOCK_TR_COURSE_SAND,
    KARRegion.TR_TA_SKY: KARItemName.UNLOCK_TR_COURSE_SKY,
    KARRegion.TR_TA_FIRE: KARItemName.UNLOCK_TR_COURSE_FIRE,
    KARRegion.TR_TA_LIGHT: KARItemName.UNLOCK_TR_COURSE_LIGHT,
    KARRegion.TR_TA_WATER: KARItemName.UNLOCK_TR_COURSE_WATER,
    KARRegion.TR_TA_METAL: KARItemName.UNLOCK_TR_COURSE_METAL,
    KARRegion.TR_FR_GRASS: KARItemName.UNLOCK_TR_COURSE_GRASS,
    KARRegion.TR_FR_SAND: KARItemName.UNLOCK_TR_COURSE_SAND,
    KARRegion.TR_FR_SKY: KARItemName.UNLOCK_TR_COURSE_SKY,
    KARRegion.TR_FR_FIRE: KARItemName.UNLOCK_TR_COURSE_FIRE,
    KARRegion.TR_FR_LIGHT: KARItemName.UNLOCK_TR_COURSE_LIGHT,
    KARRegion.TR_FR_WATER: KARItemName.UNLOCK_TR_COURSE_WATER,
    KARRegion.TR_FR_METAL: KARItemName.UNLOCK_TR_COURSE_METAL,
}


def connect_air_ride_region(world: "KARWorld", air_ride_region: Region) -> None:
    create_regions_batch(
        world,
        KARRegion.AR_TIME_ATTACK,
        KARRegion.AR_FREE_RUN,
        *AR_COURSE_REGIONS,
        *AR_TA_COURSE_REGIONS,
        *AR_FR_COURSE_REGIONS,
    )

    air_ride_region.add_exits([KARRegion.AR_TIME_ATTACK, KARRegion.AR_FREE_RUN])

    # Course entrance rules (e.g. Nebula Belt) are applied later, during rule setup.
    air_ride_region.add_exits(AR_COURSE_REGIONS)

    world.get_region(KARRegion.AR_TIME_ATTACK).add_exits(AR_TA_COURSE_REGIONS)
    world.get_region(KARRegion.AR_FREE_RUN).add_exits(AR_FR_COURSE_REGIONS)


def connect_top_ride_region(world: "KARWorld", top_ride_region: Region) -> None:
    create_regions_batch(
        world,
        KARRegion.TR_TIME_ATTACK,
        KARRegion.TR_FREE_RUN,
        *TR_COURSE_REGIONS,
        *TR_TA_COURSE_REGIONS,
        *TR_FR_COURSE_REGIONS,
    )

    top_ride_region.add_exits([KARRegion.TR_TIME_ATTACK, KARRegion.TR_FREE_RUN, *TR_COURSE_REGIONS])

    world.get_region(KARRegion.TR_FREE_RUN).add_exits(TR_FR_COURSE_REGIONS)

    world.get_region(KARRegion.TR_TIME_ATTACK).add_exits(TR_TA_COURSE_REGIONS)


def create_n_blocks_rule(
    world: "KARWorld", mode: GameMode, required_blocks: int, exclude_location_name: str | None = None
) -> Callable[[CollectionState], bool]:
    """
    Create a rule that passes when the player can reach N blocks in a mode, by counting reachable
    locations belonging to that mode.

    Mode membership is the location's code band (CT 1-120, AR 121-240, TR 241-360, AP 361-480), which is
    the canonical mode identity. Not the region name: an Archipelago box lives in the region where its
    activity happens, so an AP box in "Air Ride: MAGMA FLOWS" would otherwise count toward the Air Ride
    goal and never toward its own.

    `exclude_location_name` drops one location from the count: pass the gated cell's own name when this
    rule gates a real checkbox (e.g. "Fill in over 100"), so the count means "N OTHER boxes" and the
    cell isn't asked to reach itself, which would recurse infinitely.
    """
    player = world.player

    def can_access_n_blocks(state: CollectionState) -> bool:
        count = 0
        # Skip event locations (address is None), notably the victory event whose
        # access rule is this very function; iterating it would recurse infinitely.
        for loc in state.multiworld.get_locations(player):
            if loc.address is None:
                continue
            if exclude_location_name is not None and loc.name == exclude_location_name:
                continue
            decoded = location_code_to_mode_clear(loc.address)
            if decoded is None or decoded[0] != mode:
                continue
            if loc.can_reach(state):
                count += 1
                if count >= required_blocks:
                    return True
        return False

    return can_access_n_blocks


def _build_max_stats_goal_rule(world: "KARWorld") -> Rule | None:
    """
    Build the access rule for the Max Stats Insanity goal event.

    Requires:
      - All Patch Cap Increase items (only when cap max > cap min; otherwise the cap is fixed and no
        cap items exist).
      - A route to maxing all 9 stats: all 9 patch type unlocks (patches-gated path) or the All-Up
        unlock (items-gated path). Only emitted when both gates are on, since ungated routes are open.

    Returns None if every clause would be trivially satisfied; the caller then attaches the event
    with no access rule.
    """
    options = world.options
    rule_parts: list[Rule] = []

    count = max(0, options.city_trial_patch_cap_max.value - options.city_trial_patch_cap_min.value)
    if count > 0:
        rule_parts.append(Has(KARItemName.PATCH_CAP_INCREASE, count=count))

    if options.city_trial_patches_gated and options.city_trial_items_gated:
        # HasAll/HasAny only accept item names, not nested rules. Compose with the | operator
        # (defined on Rule) to express "all 9 patches OR all-up unlock".
        all_patch_unlocks = sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK])
        rule_parts.append(HasAll(*all_patch_unlocks) | Has(KARItemName.UNLOCK_ITEM_ALL_UP))

    if not rule_parts:
        return None
    rule = rule_parts[0]
    for part in rule_parts[1:]:
        rule = rule & part
    return rule


def _create_goal_events(
    world: "KARWorld",
    goal_option,
    checklist_amount_option,
    goal_locations_option,
    mode: GameMode,
    mode_prefix: str,
    location_table: dict,
    goal_location_map: Mapping[int, str],
    victory_event_type: str,
) -> str | None:
    """
    Create goal event locations for a single game mode.

    `mode` identifies which locations count toward a block goal (by code band); `mode_prefix` is the
    mode's root region name, where the victory event is hung.

    :return: The victory event item name if a goal was created, None otherwise.
    """
    if goal_option.value == goal_option.option_none:
        return None

    # Local import: KARLocations imports KARRegion from this module, so a top-level
    # import would cycle. Only needed here for the add_event item_type/location_type.
    from .KARLocations import KARLocation

    region = world.get_region(mode_prefix)

    if goal_option.value == goal_option.option_n_checklist_blocks:
        n_blocks_rule = create_n_blocks_rule(world, mode, checklist_amount_option.value)
        region.add_event(
            f"{mode_prefix}: Complete {checklist_amount_option.value} Checklist Blocks",
            victory_event_type,
            n_blocks_rule,
            location_type=KARLocation,
            item_type=KARItem,
        )
    elif goal_option.value == goal_option.option_checklist_list:
        goal_locs = list(goal_locations_option.value)
        rule: Rule | None = None
        if goal_locs:
            rule = CanReachLocation(goal_locs[0])
            for loc in goal_locs[1:]:
                rule = rule & CanReachLocation(loc)
        region.add_event(
            f"{mode_prefix}: Complete Required Checklist Locations",
            victory_event_type,
            rule,
            location_type=KARLocation,
            item_type=KARItem,
        )
    elif goal_option.value in goal_location_map:
        goal_location_name = goal_location_map[goal_option.value]
        goal_location_data = location_table[goal_location_name]
        goal_region = world.get_region(goal_location_data.region)

        blocks_rule = None
        if goal_option.value == goal_option.option_100_checklist_blocks:
            blocks_rule = create_n_blocks_rule(world, mode, 100)
        elif goal_option.value == CityTrialGoal.option_hydra_and_dragoon and world.options.city_trial_items_gated:
            # Assembling both legendary machines needs every piece to spawn; item gating locks that
            # behind the six piece-spawn unlocks (the same requirement the COMPLETE_DRAGOON_AND_HYDRA
            # cell carries when this is not the goal).
            blocks_rule = HasAll(*LEGENDARY_PIECE_UNLOCK_ITEMS)

        goal_region.add_event(
            f"{goal_location_name} (Victory)",
            victory_event_type,
            blocks_rule,
            location_type=KARLocation,
            item_type=KARItem,
        )
    elif goal_option.value == CityTrialGoal.option_max_stats_in_one_run:
        # Synthetic goal event in the City Trial region. There is no checklist
        # location to bind to; the mod sets max_stats_ct_achieved at runtime
        # when the player's stats all hit the per-slot patch-cap target.
        region.add_event(
            f"{mode_prefix}: Max Stats (Insanity)",
            victory_event_type,
            _build_max_stats_goal_rule(world),
            location_type=KARLocation,
            item_type=KARItem,
        )

    return victory_event_type


def determine_goal(world: "KARWorld") -> None:
    """
    Determine the goal for the world and create event locations for each enabled mode's goal.
    """
    # Imports are deferred because KARLocations imports KARRegion from this module.
    from .KARLocations import (
        AIR_RIDE_GOAL_TO_LOCATION,
        AIR_RIDE_LOCATION_TABLE,
        AP_CHECKLIST_LOCATION_TABLE,
        ARCHIPELAGO_GOAL_TO_LOCATION,
        CITY_TRIAL_GOAL_TO_LOCATION,
        CITY_TRIAL_LOCATION_TABLE,
        TOP_RIDE_GOAL_TO_LOCATION,
        TOP_RIDE_LOCATION_TABLE,
    )

    goal_event_items = [
        result
        for result in [
            _create_goal_events(
                world,
                world.options.city_trial_goal,
                world.options.city_trial_checklist_amount,
                world.options.city_trial_goal_locations,
                GameMode.CITYTRIAL,
                KARRegion.CITY_TRIAL,
                CITY_TRIAL_LOCATION_TABLE,
                CITY_TRIAL_GOAL_TO_LOCATION,
                KARItemName.CITY_TRIAL_VICTORY,
            ),
            _create_goal_events(
                world,
                world.options.air_ride_goal,
                world.options.air_ride_checklist_amount,
                world.options.air_ride_goal_locations,
                GameMode.AIRRIDE,
                KARRegion.AIR_RIDE,
                AIR_RIDE_LOCATION_TABLE,
                AIR_RIDE_GOAL_TO_LOCATION,
                KARItemName.AIR_RIDE_VICTORY,
            ),
            _create_goal_events(
                world,
                world.options.top_ride_goal,
                world.options.top_ride_checklist_amount,
                world.options.top_ride_goal_locations,
                GameMode.TOPRIDE,
                KARRegion.TOP_RIDE,
                TOP_RIDE_LOCATION_TABLE,
                TOP_RIDE_GOAL_TO_LOCATION,
                KARItemName.TOP_RIDE_VICTORY,
            ),
            _create_goal_events(
                world,
                world.options.archipelago_goal,
                world.options.archipelago_checklist_amount,
                world.options.archipelago_goal_locations,
                GameMode.ARCHIPELAGO,
                KARRegion.ARCHIPELAGO,
                AP_CHECKLIST_LOCATION_TABLE,
                ARCHIPELAGO_GOAL_TO_LOCATION,
                KARItemName.ARCHIPELAGO_VICTORY,
            ),
        ]
        if result is not None
    ]

    if goal_event_items:
        world.set_completion_rule(HasAll(*goal_event_items))
