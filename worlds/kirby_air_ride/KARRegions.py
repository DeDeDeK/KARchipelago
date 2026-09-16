import typing
from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum

from BaseClasses import CollectionState, LocationProgressType, Region
from rule_builder.rules import And, CanReachLocation, Has, HasAll, Rule

from .KARData import AP_PATCH_GROUP_MAX, GameMode, GoalKind, location_code_to_mode_clear
from .KARItems import (
    AP_PATCH_GROUP_EVENT_ITEMS,
    AP_STAR_PIECE_UNLOCK_ITEMS,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    MODE_VICTORY_EVENTS,
    KARItem,
    KARItemName,
    KARItemType,
    items_by_type,
)


class KARRegion(StrEnum):
    # City Trial
    CITY_TRIAL = "City Trial"
    CITY_TRIAL_FREE_RUN = "City Trial: Free Run"

    # AP Patch groups: consecutive slices of the AP Patch block, chained one into the next. A seed uses
    # the first N of them and leaves the rest uncreated.
    CITY_TRIAL_AP_PATCHES_1 = "City Trial: AP Patches 1"
    CITY_TRIAL_AP_PATCHES_2 = "City Trial: AP Patches 2"
    CITY_TRIAL_AP_PATCHES_3 = "City Trial: AP Patches 3"
    CITY_TRIAL_AP_PATCHES_4 = "City Trial: AP Patches 4"
    CITY_TRIAL_AP_PATCHES_5 = "City Trial: AP Patches 5"
    CITY_TRIAL_AP_PATCHES_6 = "City Trial: AP Patches 6"
    CITY_TRIAL_AP_PATCHES_7 = "City Trial: AP Patches 7"
    CITY_TRIAL_AP_PATCHES_8 = "City Trial: AP Patches 8"
    CITY_TRIAL_AP_PATCHES_9 = "City Trial: AP Patches 9"
    CITY_TRIAL_AP_PATCHES_10 = "City Trial: AP Patches 10"

    # Stadiums
    CITY_TRIAL_STADIUM_DR_ALL = "Stadium: DRAG RACE ALL"
    CITY_TRIAL_STADIUM_DR1 = "Stadium: DRAG RACE 1"
    CITY_TRIAL_STADIUM_DR2 = "Stadium: DRAG RACE 2"
    CITY_TRIAL_STADIUM_DR3 = "Stadium: DRAG RACE 3"
    CITY_TRIAL_STADIUM_DR4 = "Stadium: DRAG RACE 4"
    CITY_TRIAL_STADIUM_HJ = "Stadium: HIGH JUMP"
    CITY_TRIAL_STADIUM_TF = "Stadium: TARGET FLIGHT"
    CITY_TRIAL_STADIUM_AG = "Stadium: AIR GLIDER"
    CITY_TRIAL_STADIUM_DD_ALL = "Stadium: DESTRUCTION DERBY ALL"
    CITY_TRIAL_STADIUM_DD1 = "Stadium: DESTRUCTION DERBY 1"
    CITY_TRIAL_STADIUM_DD2 = "Stadium: DESTRUCTION DERBY 2"
    CITY_TRIAL_STADIUM_DD3 = "Stadium: DESTRUCTION DERBY 3"
    CITY_TRIAL_STADIUM_DD4 = "Stadium: DESTRUCTION DERBY 4"
    CITY_TRIAL_STADIUM_DD5 = "Stadium: DESTRUCTION DERBY 5"
    CITY_TRIAL_STADIUM_KM_ALL = "Stadium: KIRBY MELEE ALL"
    CITY_TRIAL_STADIUM_KM1 = "Stadium: KIRBY MELEE 1"
    CITY_TRIAL_STADIUM_KM2 = "Stadium: KIRBY MELEE 2"
    CITY_TRIAL_STADIUM_VSKD = "Stadium: VS. KING DEDEDE"
    CITY_TRIAL_STADIUM_SR1 = "Stadium: SINGLE RACE 1"
    CITY_TRIAL_STADIUM_SR2 = "Stadium: SINGLE RACE 2"
    CITY_TRIAL_STADIUM_SR3 = "Stadium: SINGLE RACE 3"
    CITY_TRIAL_STADIUM_SR4 = "Stadium: SINGLE RACE 4"
    CITY_TRIAL_STADIUM_SR5 = "Stadium: SINGLE RACE 5"
    CITY_TRIAL_STADIUM_SR6 = "Stadium: SINGLE RACE 6"
    CITY_TRIAL_STADIUM_SR7 = "Stadium: SINGLE RACE 7"
    CITY_TRIAL_STADIUM_SR8 = "Stadium: SINGLE RACE 8"
    CITY_TRIAL_STADIUM_SR9 = "Stadium: SINGLE RACE 9"

    # Air Ride
    AIR_RIDE = "Air Ride"
    AIR_RIDE_TIME_ATTACK = "Air Ride: Time Attack"
    AIR_RIDE_FREE_RUN = "Air Ride: Free Run"
    AIR_RIDE_MAGMA_FLOWS = "Air Ride: MAGMA FLOWS"
    AIR_RIDE_FANTASY_MEADOWS = "Air Ride: FANTASY MEADOWS"
    AIR_RIDE_CELESTIAL_VALLEY = "Air Ride: CELESTIAL VALLEY"
    AIR_RIDE_BEANSTALK_PARK = "Air Ride: BEANSTALK PARK"
    AIR_RIDE_FROZEN_HILLSIDE = "Air Ride: FROZEN HILLSIDE"
    AIR_RIDE_MACHINE_PASSAGE = "Air Ride: MACHINE PASSAGE"
    AIR_RIDE_SKY_SANDS = "Air Ride: SKY SANDS"
    AIR_RIDE_CHECKER_KNIGHTS = "Air Ride: CHECKER KNIGHTS"
    AIR_RIDE_NEBULA_BELT = "Air Ride: NEBULA BELT"
    AIR_RIDE_TA_MAGMA_FLOWS = "Air Ride: Time Attack: MAGMA FLOWS"
    AIR_RIDE_TA_FANTASY_MEADOWS = "Air Ride: Time Attack: FANTASY MEADOWS"
    AIR_RIDE_TA_CELESTIAL_VALLEY = "Air Ride: Time Attack: CELESTIAL VALLEY"
    AIR_RIDE_TA_BEANSTALK_PARK = "Air Ride: Time Attack: BEANSTALK PARK"
    AIR_RIDE_TA_FROZEN_HILLSIDE = "Air Ride: Time Attack: FROZEN HILLSIDE"
    AIR_RIDE_TA_MACHINE_PASSAGE = "Air Ride: Time Attack: MACHINE PASSAGE"
    AIR_RIDE_TA_SKY_SANDS = "Air Ride: Time Attack: SKY SANDS"
    AIR_RIDE_TA_CHECKER_KNIGHTS = "Air Ride: Time Attack: CHECKER KNIGHTS"
    AIR_RIDE_TA_NEBULA_BELT = "Air Ride: Time Attack: NEBULA BELT"
    AIR_RIDE_FR_MAGMA_FLOWS = "Air Ride: Free Run: MAGMA FLOWS"
    AIR_RIDE_FR_FANTASY_MEADOWS = "Air Ride: Free Run: FANTASY MEADOWS"
    AIR_RIDE_FR_CELESTIAL_VALLEY = "Air Ride: Free Run: CELESTIAL VALLEY"
    AIR_RIDE_FR_BEANSTALK_PARK = "Air Ride: Free Run: BEANSTALK PARK"
    AIR_RIDE_FR_FROZEN_HILLSIDE = "Air Ride: Free Run: FROZEN HILLSIDE"
    AIR_RIDE_FR_MACHINE_PASSAGE = "Air Ride: Free Run: MACHINE PASSAGE"
    AIR_RIDE_FR_SKY_SANDS = "Air Ride: Free Run: SKY SANDS"
    AIR_RIDE_FR_CHECKER_KNIGHTS = "Air Ride: Free Run: CHECKER KNIGHTS"
    AIR_RIDE_FR_NEBULA_BELT = "Air Ride: Free Run: NEBULA BELT"

    # Top Ride
    TOP_RIDE = "Top Ride"
    TOP_RIDE_TIME_ATTACK = "Top Ride: Time Attack"
    TOP_RIDE_FREE_RUN = "Top Ride: Free Run"
    TOP_RIDE_GRASS = "Top Ride: GRASS"
    TOP_RIDE_SAND = "Top Ride: SAND"
    TOP_RIDE_SKY = "Top Ride: SKY"
    TOP_RIDE_FIRE = "Top Ride: FIRE"
    TOP_RIDE_LIGHT = "Top Ride: LIGHT"
    TOP_RIDE_WATER = "Top Ride: WATER"
    TOP_RIDE_METAL = "Top Ride: METAL"
    TOP_RIDE_TA_GRASS = "Top Ride: Time Attack: GRASS"
    TOP_RIDE_TA_SAND = "Top Ride: Time Attack: SAND"
    TOP_RIDE_TA_SKY = "Top Ride: Time Attack: SKY"
    TOP_RIDE_TA_FIRE = "Top Ride: Time Attack: FIRE"
    TOP_RIDE_TA_LIGHT = "Top Ride: Time Attack: LIGHT"
    TOP_RIDE_TA_WATER = "Top Ride: Time Attack: WATER"
    TOP_RIDE_TA_METAL = "Top Ride: Time Attack: METAL"
    TOP_RIDE_FR_GRASS = "Top Ride: Free Run: GRASS"
    TOP_RIDE_FR_SAND = "Top Ride: Free Run: SAND"
    TOP_RIDE_FR_SKY = "Top Ride: Free Run: SKY"
    TOP_RIDE_FR_FIRE = "Top Ride: Free Run: FIRE"
    TOP_RIDE_FR_LIGHT = "Top Ride: Free Run: LIGHT"
    TOP_RIDE_FR_WATER = "Top Ride: Free Run: WATER"
    TOP_RIDE_FR_METAL = "Top Ride: Free Run: METAL"

    # Archipelago - technically not an in-game region but contains other regions
    ARCHIPELAGO = "Archipelago"


# Name-prefix table backing REGION_TO_MODE. Every member name starts with its mode spelled out in full, so each
# mode has exactly one prefix and none overlaps another.
_REGION_MODE_NAME_PREFIXES: tuple[tuple[str, GameMode], ...] = (
    ("CITY_TRIAL", GameMode.CITYTRIAL),
    ("AIR_RIDE", GameMode.AIRRIDE),
    ("TOP_RIDE", GameMode.TOPRIDE),
    ("ARCHIPELAGO", GameMode.ARCHIPELAGO),
)


def _build_region_to_mode() -> dict[str, GameMode]:
    """Classify every KARRegion by the game mode it belongs to, keyed by region name. Derived from the
    enum member names and checked exhaustive.
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
                f"Every region must map to a game mode; start its name with that mode's prefix."
            )
    return mapping


# Which game mode each region belongs to. Static by construction and deliberately so: logic_modes derives
# itself from this table, so inspecting built regions here would be circular.
REGION_TO_MODE: dict[str, GameMode] = _build_region_to_mode()


# The AP Patch group regions in chain order
AP_PATCH_GROUP_REGIONS: tuple[str, ...] = tuple(
    region.value for region in KARRegion if region.name.startswith("CITY_TRIAL_AP_PATCHES_")
)

if len(AP_PATCH_GROUP_REGIONS) != AP_PATCH_GROUP_MAX:
    raise ValueError(
        f"KARRegion declares {len(AP_PATCH_GROUP_REGIONS)} AP Patch group regions, but the widest seed "
        f"splits into {AP_PATCH_GROUP_MAX}. Add or remove CITY_TRIAL_AP_PATCHES_* members to match."
    )


# KARLocations imports KARRegion from this module, so its imports are deferred into function bodies.
if typing.TYPE_CHECKING:
    from . import KARWorld


# Each mode's root region, entered from the origin region
MODE_ROOT_REGION: dict[GameMode, str] = {
    GameMode.CITYTRIAL: KARRegion.CITY_TRIAL,
    GameMode.AIRRIDE: KARRegion.AIR_RIDE,
    GameMode.TOPRIDE: KARRegion.TOP_RIDE,
    GameMode.ARCHIPELAGO: KARRegion.ARCHIPELAGO,
}

# Course regions by variant. KARRules pairs them by index, so a mode's three tuples keep the same course order.
AR_COURSE_REGIONS: tuple[str, ...] = (
    KARRegion.AIR_RIDE_MAGMA_FLOWS,
    KARRegion.AIR_RIDE_FANTASY_MEADOWS,
    KARRegion.AIR_RIDE_CELESTIAL_VALLEY,
    KARRegion.AIR_RIDE_BEANSTALK_PARK,
    KARRegion.AIR_RIDE_FROZEN_HILLSIDE,
    KARRegion.AIR_RIDE_MACHINE_PASSAGE,
    KARRegion.AIR_RIDE_SKY_SANDS,
    KARRegion.AIR_RIDE_CHECKER_KNIGHTS,
    KARRegion.AIR_RIDE_NEBULA_BELT,
)
AR_TA_COURSE_REGIONS: tuple[str, ...] = (
    KARRegion.AIR_RIDE_TA_MAGMA_FLOWS,
    KARRegion.AIR_RIDE_TA_FANTASY_MEADOWS,
    KARRegion.AIR_RIDE_TA_CELESTIAL_VALLEY,
    KARRegion.AIR_RIDE_TA_BEANSTALK_PARK,
    KARRegion.AIR_RIDE_TA_FROZEN_HILLSIDE,
    KARRegion.AIR_RIDE_TA_MACHINE_PASSAGE,
    KARRegion.AIR_RIDE_TA_SKY_SANDS,
    KARRegion.AIR_RIDE_TA_CHECKER_KNIGHTS,
    KARRegion.AIR_RIDE_TA_NEBULA_BELT,
)
AR_FR_COURSE_REGIONS: tuple[str, ...] = (
    KARRegion.AIR_RIDE_FR_MAGMA_FLOWS,
    KARRegion.AIR_RIDE_FR_FANTASY_MEADOWS,
    KARRegion.AIR_RIDE_FR_CELESTIAL_VALLEY,
    KARRegion.AIR_RIDE_FR_BEANSTALK_PARK,
    KARRegion.AIR_RIDE_FR_FROZEN_HILLSIDE,
    KARRegion.AIR_RIDE_FR_MACHINE_PASSAGE,
    KARRegion.AIR_RIDE_FR_SKY_SANDS,
    KARRegion.AIR_RIDE_FR_CHECKER_KNIGHTS,
    KARRegion.AIR_RIDE_FR_NEBULA_BELT,
)

TR_COURSE_REGIONS: tuple[str, ...] = (
    KARRegion.TOP_RIDE_GRASS,
    KARRegion.TOP_RIDE_METAL,
    KARRegion.TOP_RIDE_LIGHT,
    KARRegion.TOP_RIDE_SAND,
    KARRegion.TOP_RIDE_FIRE,
    KARRegion.TOP_RIDE_WATER,
    KARRegion.TOP_RIDE_SKY,
)
TR_TA_COURSE_REGIONS: tuple[str, ...] = (
    KARRegion.TOP_RIDE_TA_GRASS,
    KARRegion.TOP_RIDE_TA_METAL,
    KARRegion.TOP_RIDE_TA_LIGHT,
    KARRegion.TOP_RIDE_TA_SAND,
    KARRegion.TOP_RIDE_TA_FIRE,
    KARRegion.TOP_RIDE_TA_WATER,
    KARRegion.TOP_RIDE_TA_SKY,
)
TR_FR_COURSE_REGIONS: tuple[str, ...] = (
    KARRegion.TOP_RIDE_FR_GRASS,
    KARRegion.TOP_RIDE_FR_METAL,
    KARRegion.TOP_RIDE_FR_LIGHT,
    KARRegion.TOP_RIDE_FR_SAND,
    KARRegion.TOP_RIDE_FR_FIRE,
    KARRegion.TOP_RIDE_FR_WATER,
    KARRegion.TOP_RIDE_FR_SKY,
)

# Each region's child regions. create_regions builds a mode's tree from its root; set_rules gates the entrances.
REGION_TREE: dict[str, tuple[str, ...]] = {
    KARRegion.CITY_TRIAL: (
        KARRegion.CITY_TRIAL_FREE_RUN,
        KARRegion.CITY_TRIAL_STADIUM_DD_ALL,
        KARRegion.CITY_TRIAL_STADIUM_DR_ALL,
        KARRegion.CITY_TRIAL_STADIUM_HJ,
        KARRegion.CITY_TRIAL_STADIUM_TF,
        KARRegion.CITY_TRIAL_STADIUM_AG,
        KARRegion.CITY_TRIAL_STADIUM_KM_ALL,
        KARRegion.CITY_TRIAL_STADIUM_VSKD,
        KARRegion.CITY_TRIAL_STADIUM_SR1,
        KARRegion.CITY_TRIAL_STADIUM_SR2,
        KARRegion.CITY_TRIAL_STADIUM_SR3,
        KARRegion.CITY_TRIAL_STADIUM_SR4,
        KARRegion.CITY_TRIAL_STADIUM_SR5,
        KARRegion.CITY_TRIAL_STADIUM_SR6,
        KARRegion.CITY_TRIAL_STADIUM_SR7,
        KARRegion.CITY_TRIAL_STADIUM_SR8,
        KARRegion.CITY_TRIAL_STADIUM_SR9,
    ),
    # DD_ALL, DR_ALL and KM_ALL are parents nesting their numbered sub-stadiums.
    KARRegion.CITY_TRIAL_STADIUM_DD_ALL: (
        KARRegion.CITY_TRIAL_STADIUM_DD1,
        KARRegion.CITY_TRIAL_STADIUM_DD2,
        KARRegion.CITY_TRIAL_STADIUM_DD3,
        KARRegion.CITY_TRIAL_STADIUM_DD4,
        KARRegion.CITY_TRIAL_STADIUM_DD5,
    ),
    KARRegion.CITY_TRIAL_STADIUM_DR_ALL: (
        KARRegion.CITY_TRIAL_STADIUM_DR1,
        KARRegion.CITY_TRIAL_STADIUM_DR2,
        KARRegion.CITY_TRIAL_STADIUM_DR3,
        KARRegion.CITY_TRIAL_STADIUM_DR4,
    ),
    KARRegion.CITY_TRIAL_STADIUM_KM_ALL: (KARRegion.CITY_TRIAL_STADIUM_KM1, KARRegion.CITY_TRIAL_STADIUM_KM2),
    KARRegion.AIR_RIDE: (KARRegion.AIR_RIDE_TIME_ATTACK, KARRegion.AIR_RIDE_FREE_RUN, *AR_COURSE_REGIONS),
    KARRegion.AIR_RIDE_TIME_ATTACK: AR_TA_COURSE_REGIONS,
    KARRegion.AIR_RIDE_FREE_RUN: AR_FR_COURSE_REGIONS,
    KARRegion.TOP_RIDE: (KARRegion.TOP_RIDE_TIME_ATTACK, KARRegion.TOP_RIDE_FREE_RUN, *TR_COURSE_REGIONS),
    KARRegion.TOP_RIDE_TIME_ATTACK: TR_TA_COURSE_REGIONS,
    KARRegion.TOP_RIDE_FREE_RUN: TR_FR_COURSE_REGIONS,
}


def _add_region(world: "KARWorld", name: str, parent: Region, rule: Rule | None = None) -> Region:
    """Create region `name`, register it, and connect `parent` to it."""
    region = Region(name, world.player, world.multiworld)
    world.multiworld.regions.append(region)
    parent.connect(region, rule=rule)
    return region


def _add_region_tree(world: "KARWorld", name: str, parent: Region) -> None:
    """Create region `name` under `parent`, then its REGION_TREE descendants beneath it."""
    region = _add_region(world, name, parent)
    for child in REGION_TREE.get(name, ()):
        _add_region_tree(world, child, region)


def assign_locations_to_regions(
    world: "KARWorld",
    location_table: dict,
    default_locations: Iterable[str],
    excluded_locations: Iterable[str],
) -> None:
    """Assign locations to their regions with the appropriate progress type, skipping goal-replaced ones."""
    from .KARLocations import KARLocation

    for locations, progress_type in [
        (default_locations, LocationProgressType.DEFAULT),
        (excluded_locations, LocationProgressType.EXCLUDED),
    ]:
        for location_name in locations:
            if location_name in world.goal_locations_to_exclude:
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

    # Every mode in `logic_modes` gets its full tree; its own locations are assigned below only when `*_enabled`.
    for mode, root in MODE_ROOT_REGION.items():
        if mode in world.logic_modes:
            _add_region_tree(world, root, menu_region)

    for enabled, location_table, default_locations, excluded_locations in (
        (
            world.city_trial_enabled,
            CITY_TRIAL_LOCATION_TABLE,
            world.city_trial_default_locations,
            world.city_trial_excluded_locations,
        ),
        (
            world.air_ride_enabled,
            AIR_RIDE_LOCATION_TABLE,
            world.air_ride_default_locations,
            world.air_ride_excluded_locations,
        ),
        (
            world.top_ride_enabled,
            TOP_RIDE_LOCATION_TABLE,
            world.top_ride_default_locations,
            world.top_ride_excluded_locations,
        ),
        (
            world.archipelago_enabled,
            AP_CHECKLIST_LOCATION_TABLE,
            world.archipelago_default_locations,
            world.archipelago_excluded_locations,
        ),
    ):
        if enabled:
            assign_locations_to_regions(world, location_table, default_locations, excluded_locations)

    if world.ap_patch_locations:
        connect_ap_patch_regions(world)
        assign_locations_to_regions(
            world, world.ap_patch_locations, world.ap_patch_default_locations, world.ap_patch_excluded_locations
        )

    determine_goal(world)


def connect_ap_patch_regions(world: "KARWorld") -> None:
    """Chain the seed's AP Patch groups off City Trial, one region per group, each opened by an event in
    the group before it.
    """
    from .KARLocations import KARLocation

    names = AP_PATCH_GROUP_REGIONS[: world.ap_patch_group_count]
    region = _add_region(world, names[0], world.get_region(KARRegion.CITY_TRIAL))
    for event_item, name in zip(AP_PATCH_GROUP_EVENT_ITEMS, names[1:]):
        region.add_event(f"{region.name} Cleared", event_item, location_type=KARLocation, item_type=KARItem)
        region = _add_region(world, name, region, Has(event_item))


def create_n_blocks_rule(
    world: "KARWorld", mode: GameMode, required_blocks: int, exclude_location_name: str | None = None
) -> Callable[[CollectionState], bool]:
    """A rule that passes once `required_blocks` of `mode`'s locations are reachable."""
    player = world.player

    def can_access_n_blocks(state: CollectionState) -> bool:
        count = 0
        for loc in state.multiworld.get_locations(player):
            # Skip event locations (address is None) - the victory event's rule is this function.
            if loc.address is None:
                continue
            # So a cell gated on this rule is not asked to reach itself and recurse.
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
    Build the access rule for the Max Stats CT goal event: all Patch Cap Increase items (only when
    cap max > cap min, else none exist), plus a route to maxing all 9 stats - the 9 patch type unlocks or
    the All-Up unlock, emitted only when both gates are on. None when every clause is trivial.
    """
    options = world.options
    rule_parts: list[Rule] = []

    count = max(0, options.city_trial_patch_cap_max.value - options.city_trial_patch_cap_min.value)
    if count > 0:
        rule_parts.append(Has(KARItemName.PATCH_CAP_INCREASE, count=count))

    if options.city_trial_patches_gated and options.city_trial_items_gated:
        all_patch_unlocks = sorted(items_by_type[KARItemType.CT_PATCH_UNLOCK])
        rule_parts.append(HasAll(*all_patch_unlocks) | Has(KARItemName.UNLOCK_ITEM_ALL_UP))

    return And(*rule_parts) if rule_parts else None


# Each assemble goal's piece unlocks. The Archipelago Star's machine unlock isn't one: assembling the star mounts it.
_ASSEMBLE_GOAL_UNLOCKS: dict[int, tuple[str, ...]] = {
    GoalKind.HYDRA_AND_DRAGOON: LEGENDARY_PIECE_UNLOCK_ITEMS,
    GoalKind.ASSEMBLE_AP_STAR: AP_STAR_PIECE_UNLOCK_ITEMS,
    GoalKind.ALL_LEGENDARIES_CT: (*LEGENDARY_PIECE_UNLOCK_ITEMS, *AP_STAR_PIECE_UNLOCK_ITEMS),
}


def _create_goal_event(
    world: "KARWorld",
    mode: GameMode,
    goal_option,
    checklist_amount_option,
    goal_locations_option,
    goal_location_map: Mapping[int, str],
) -> None:
    """
    Create the victory event for one mode's goal: in the region of the checklist cell backing the goal, or the
    mode's root region when no cell does.
    """
    # Deferred to break the import cycle.
    from .KARLocations import LOCATION_TABLE, KARLocation

    region = world.get_region(MODE_ROOT_REGION[mode])

    if goal_option.value == goal_option.option_n_checklist_blocks:
        name = f"{region.name}: Complete {checklist_amount_option.value} Checklist Blocks"
        rule = create_n_blocks_rule(world, mode, checklist_amount_option.value)
    elif goal_option.value == goal_option.option_checklist_list:
        name = f"{region.name}: Complete Required Checklist Locations"
        rule = And(*(CanReachLocation(location) for location in goal_locations_option.value))
    elif goal_option.value in goal_location_map:
        goal_location_name = goal_location_map[goal_option.value]
        region = world.get_region(LOCATION_TABLE[goal_location_name].region)
        name = f"{goal_location_name} (Victory)"
        if goal_option.value == GoalKind.CHECKLIST_100:
            rule = create_n_blocks_rule(world, mode, 100)
        elif goal_option.value == GoalKind.BEAT_KING_DEDEDE:
            # Dedede's stadium must come up; goal_forced_unlocks keeps its unlock in the pool even when ungated.
            rule = Has(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)
        else:
            # Every piece must spawn; goal_forced_unlocks keeps them in the pool even when items are ungated.
            rule = HasAll(*_ASSEMBLE_GOAL_UNLOCKS[goal_option.value])
            if "city_trial_boxes_gated" in world.effective_gates:
                rule &= Has(KARItemName.UNLOCK_BOX_RED)
    elif goal_option.value == GoalKind.MAX_STATS_CT:
        # No checklist cell backs this goal; the mod sets max_stats_ct_achieved once every stat hits the patch cap.
        name = f"{region.name}: Max Stats"
        rule = _build_max_stats_goal_rule(world)
    else:
        raise ValueError(f"{mode.name} goal {goal_option.value} has no victory event")

    region.add_event(name, MODE_VICTORY_EVENTS[mode], rule, location_type=KARLocation, item_type=KARItem)


def _build_ut_go_mode_rule(world: "KARWorld", goal_event_items: list[str]) -> Callable[[CollectionState], bool]:
    """
    Universal Tracker's go-mode: whether some goal not yet reported done (`ut_goals_completed`) is in logic now.
    The real completion rule ANDs every mode's victory, so it would read "No" until the last goal is in logic.
    """
    player = world.player

    def can_go(state: CollectionState) -> bool:
        completed = world.ut_goals_completed
        if completed is None:
            # No client reporting - stock UT tracking the slot. Best available answer.
            return any(state.has(item, player) for item in goal_event_items)
        remaining = [item for item in goal_event_items if item not in completed]
        if not remaining:
            return True  # every goal done; the seed is won
        return any(state.has(item, player) for item in remaining)

    return can_go


def determine_goal(world: "KARWorld") -> None:
    """Create the victory event for each enabled mode's goal and set the completion rule."""
    # Deferred to break the import cycle.
    from .KARLocations import (
        AIR_RIDE_GOAL_TO_LOCATION,
        ARCHIPELAGO_GOAL_TO_LOCATION,
        CITY_TRIAL_GOAL_TO_LOCATION,
        TOP_RIDE_GOAL_TO_LOCATION,
    )

    options = world.options
    goal_event_items: list[str] = []
    for mode, goal_option, checklist_amount_option, goal_locations_option, goal_location_map in (
        (
            GameMode.CITYTRIAL,
            options.city_trial_goal,
            options.city_trial_checklist_amount,
            options.city_trial_goal_locations,
            CITY_TRIAL_GOAL_TO_LOCATION,
        ),
        (
            GameMode.AIRRIDE,
            options.air_ride_goal,
            options.air_ride_checklist_amount,
            options.air_ride_goal_locations,
            AIR_RIDE_GOAL_TO_LOCATION,
        ),
        (
            GameMode.TOPRIDE,
            options.top_ride_goal,
            options.top_ride_checklist_amount,
            options.top_ride_goal_locations,
            TOP_RIDE_GOAL_TO_LOCATION,
        ),
        (
            GameMode.ARCHIPELAGO,
            options.archipelago_goal,
            options.archipelago_checklist_amount,
            options.archipelago_goal_locations,
            ARCHIPELAGO_GOAL_TO_LOCATION,
        ),
    ):
        if goal_option.value != goal_option.option_none:
            _create_goal_event(
                world, mode, goal_option, checklist_amount_option, goal_locations_option, goal_location_map
            )
            goal_event_items.append(MODE_VICTORY_EVENTS[mode])

    # Under Universal Tracker (re_gen_passthrough set) nothing fills, so the completion rule only drives go-mode.
    if getattr(world.multiworld, "re_gen_passthrough", None) is not None:
        world.set_completion_rule(_build_ut_go_mode_rule(world, goal_event_items))
    else:
        world.set_completion_rule(HasAll(*goal_event_items))
