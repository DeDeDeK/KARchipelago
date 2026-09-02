import typing
from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum

from BaseClasses import CollectionState, LocationProgressType, Region
from rule_builder.rules import CanReachLocation, Has, HasAll, Rule

from .KARData import AP_PATCH_GROUP_MAX, GameMode, location_code_to_mode_clear
from .KARItems import (
    AP_PATCH_GROUP_EVENT_ITEMS,
    AP_STAR_PIECE_UNLOCK_ITEMS,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    KARItem,
    KARItemName,
    KARItemType,
    items_by_type,
)
from .KAROptions import ArchipelagoGoal, CityTrialGoal


class KARRegion(StrEnum):
    # City Trial
    CITY_TRIAL = "City Trial"
    CT_FREE_RUN = "City Trial: Free Run"

    # AP Patch groups: consecutive slices of the AP Patch block, chained one into the next. A seed uses
    # the first N of them and leaves the rest uncreated.
    CT_AP_PATCHES_1 = "City Trial: AP Patches 1"
    CT_AP_PATCHES_2 = "City Trial: AP Patches 2"
    CT_AP_PATCHES_3 = "City Trial: AP Patches 3"
    CT_AP_PATCHES_4 = "City Trial: AP Patches 4"
    CT_AP_PATCHES_5 = "City Trial: AP Patches 5"
    CT_AP_PATCHES_6 = "City Trial: AP Patches 6"
    CT_AP_PATCHES_7 = "City Trial: AP Patches 7"
    CT_AP_PATCHES_8 = "City Trial: AP Patches 8"
    CT_AP_PATCHES_9 = "City Trial: AP Patches 9"
    CT_AP_PATCHES_10 = "City Trial: AP Patches 10"

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

    # Archipelago checklist: a tab, not a place. Only mode-agnostic boxes live here - a box describing an
    # activity in another mode sits in that mode's region instead. No sub-regions.
    ARCHIPELAGO = "Archipelago"


# Ordered name-prefix table backing REGION_TO_MODE. First match wins, so exact mode-root names come
# before their short prefixes. "ARCHIPELAGO" leads defensively - it does not collide with "AR_" today.
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
    """Classify every KARRegion by the game mode it belongs to, keyed by region name. Derived from the
    enum member names and checked exhaustive: a region matching no prefix raises at import instead of
    silently stranding an Archipelago box in a tree that logic_modes never builds."""
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


# Which game mode each region belongs to. Static by construction and deliberately so: logic_modes derives
# itself from this table, so inspecting built regions here would be circular.
REGION_TO_MODE: dict[str, GameMode] = _build_region_to_mode()


# The AP Patch group regions in chain order, read off the enum so declaration order is the chain.
AP_PATCH_GROUP_REGIONS: tuple[str, ...] = tuple(
    region.value for region in KARRegion if region.name.startswith("CT_AP_PATCHES_")
)

if len(AP_PATCH_GROUP_REGIONS) != AP_PATCH_GROUP_MAX:
    raise ValueError(
        f"KARRegion declares {len(AP_PATCH_GROUP_REGIONS)} AP Patch group regions, but the widest seed "
        f"splits into {AP_PATCH_GROUP_MAX}. Add or remove CT_AP_PATCHES_* members to match."
    )


# KARLocations imports KARRegion from this module, so its imports are deferred into function bodies.
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
    """Assign locations to their regions with the appropriate progress type."""
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
    """Create regions, place locations in them, and connect them up."""
    from .KARLocations import (
        AIR_RIDE_LOCATION_TABLE,
        AP_CHECKLIST_LOCATION_TABLE,
        CITY_TRIAL_LOCATION_TABLE,
        TOP_RIDE_LOCATION_TABLE,
    )

    # The Menu region is the origin that connects all enabled game modes.
    menu_region = Region(world.origin_region_name, world.player, world.multiworld)
    world.multiworld.regions.append(menu_region)

    # A mode's tree is BUILT when `mode in logic_modes` (it has a goal or hosts an Archipelago box); its
    # OWN checklist locations are assigned (below) only when `*_enabled`. So a goal-less City Trial
    # hosting one AP box gets all 28 CT regions with 27 empty - there are no partial trees.
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
        # Holds no locations - every Archipelago box lives in the region of the mode it describes. The
        # region exists to host the Archipelago victory event. No sub-regions.
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

    if world.ap_patch_locations:
        connect_ap_patch_regions(world)
        assign_locations_to_regions(
            world,
            world.ap_patch_locations,
            world.ap_patch_default_locations,
            world.ap_patch_excluded_locations,
            world.goal_locations_to_exclude,
        )

    determine_goal(world)


def connect_ap_patch_regions(world: "KARWorld") -> None:
    """Chain the seed's AP Patch groups off City Trial, one region per group, each opened by an event in
    the group before it. The mod claims the lowest unclaimed patch index, so the chain is the order the
    block is really collected in; without it every patch is one flat sphere and fill has no reason to
    keep a key out of the two-hundredth. The last group gates nothing and so carries no event.

    The chain is structural, not option-driven gating, so its entrance rules are set here rather than
    deferred to rule setup.
    """
    from .KARLocations import KARLocation

    regions = create_regions_batch(world, *AP_PATCH_GROUP_REGIONS[: world.ap_patch_group_count])
    world.get_region(KARRegion.CITY_TRIAL).connect(regions[0])
    for index, region in enumerate(regions[:-1]):
        event_item = AP_PATCH_GROUP_EVENT_ITEMS[index]
        region.add_event(
            f"{region.name} Cleared",
            event_item,
            location_type=KARLocation,
            item_type=KARItem,
        )
        region.connect(regions[index + 1], rule=Has(event_item))


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
    A rule that passes once N of a mode's locations are reachable. Mode membership is the location's
    code band (CT 1-120, AR 121-240, TR 241-360, AP 361-412), not the region name: an AP box lives in
    the region where its activity happens, so one in "Air Ride: MAGMA FLOWS" would otherwise count
    toward the Air Ride goal. `exclude_location_name` drops one location, so a cell gated on this rule
    is not asked to reach itself and recurse.
    """
    player = world.player

    def can_access_n_blocks(state: CollectionState) -> bool:
        count = 0
        # Skip event locations (address is None) - the victory event's rule is this function.
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
    Build the access rule for the Max Stats Insanity goal event: all Patch Cap Increase items (only when
    cap max > cap min, else none exist), plus a route to maxing all 9 stats - the 9 patch type unlocks or
    the All-Up unlock, emitted only when both gates are on. None when every clause is trivial.
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
    Create goal event locations for a single game mode. `mode` identifies which locations count toward a
    block goal (by code band); `mode_prefix` is the root region name where the victory event is hung.
    Returns the victory event item name, or None when the mode has no goal.
    """
    if goal_option.value == goal_option.option_none:
        return None

    # Deferred to break the import cycle; only needed for the add_event item_type/location_type.
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
        # getattr, not attribute access: ArchipelagoGoal has no 100_checklist_blocks (its checklist is
        # under 100 boxes). Goal values are ints, so the None default can never compare equal.
        if goal_option.value == getattr(goal_option, "option_100_checklist_blocks", None):
            blocks_rule = create_n_blocks_rule(world, mode, 100)
        elif goal_option.value == CityTrialGoal.option_hydra_and_dragoon:
            # Assembling both legendary machines needs every piece to spawn, which the six piece-spawn
            # unlocks control. They are in the pool either way - gated ships the whole category, ungated
            # still ships these six as the goal's keys.
            blocks_rule = HasAll(*LEGENDARY_PIECE_UNLOCK_ITEMS)
        elif goal_option.value == CityTrialGoal.option_beat_king_dedede:
            # Dedede has to come up in the stadium rotation, which his stadium's unlock controls. Also
            # in the pool either way - stadium gating on ships all 24, off still ships this one.
            blocks_rule = Has(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)
        elif goal_option.value == ArchipelagoGoal.option_assemble_archipelago_star:
            # Every sphere has to spawn, which the six sphere unlocks control. The machine unlock is
            # not among them: assembling the star mounts it either way.
            blocks_rule = HasAll(*AP_STAR_PIECE_UNLOCK_ITEMS)
        elif goal_option.value == ArchipelagoGoal.option_all_three_legendaries_in_one_run:
            blocks_rule = HasAll(*LEGENDARY_PIECE_UNLOCK_ITEMS, *AP_STAR_PIECE_UNLOCK_ITEMS)

        goal_region.add_event(
            f"{goal_location_name} (Victory)",
            victory_event_type,
            blocks_rule,
            location_type=KARLocation,
            item_type=KARItem,
        )
    elif goal_option.value == CityTrialGoal.option_max_stats_in_one_run:
        # Synthetic goal event in the City Trial region - no checklist location to bind to. The mod sets
        # max_stats_ct_achieved when every stat hits the per-slot patch-cap target.
        region.add_event(
            f"{mode_prefix}: Max Stats (Insanity)",
            victory_event_type,
            _build_max_stats_goal_rule(world),
            location_type=KARLocation,
            item_type=KARItem,
        )

    return victory_event_type


def determine_goal(world: "KARWorld") -> None:
    """Create the victory event for each enabled mode's goal and set the completion rule."""
    # Deferred to break the import cycle.
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
