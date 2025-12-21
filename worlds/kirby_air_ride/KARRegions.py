import typing
from collections.abc import Callable

from BaseClasses import CollectionState, LocationProgressType, Region

from .KARData import VictoryEventType
from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    KARLocation,
    KARLocationData,
    KARLocationType,
)

if typing.TYPE_CHECKING:
    from . import KARWorld


def create_event_location(
    world: "KARWorld",
    region: Region,
    event_name: str,
    event_item_name: str,
    rule: Callable[[CollectionState], bool] | None = None,
) -> None:
    """
    Create an event location and place the associated event item on it.

    :param world: The KARWorld instance
    :param region: The region to place the event location in
    :param event_name: Name of the event location
    :param event_item_name: Name of the event item to place
    :param rule: Optional rule to apply to this event location
    """
    from worlds.generic.Rules import set_rule

    # Create event location with code=None
    event_location_data = KARLocationData(
        code=None, region=region.name, reward=event_item_name, type=KARLocationType.EVENT, mem_address=None
    )

    event_location = KARLocation(world.player, event_name, region, event_location_data)
    region.locations.append(event_location)

    # Apply rule if provided
    if rule is not None:
        set_rule(event_location, rule)

    # Create and place locked event item
    event_item = world.create_item(event_item_name)
    event_location.place_locked_item(event_item)


def create_regions(world: "KARWorld"):
    """
    Create regions, place locations in regions, and connect regions for the Kirby Air Ride world.
    """
    # Collect goal locations that should be excluded from the multiworld
    # These will be replaced by event locations
    goal_locations_to_exclude: set[str] = set()

    # Check each mode's goal - if it's a specific location (not "N checklist blocks"), exclude it
    if world.city_trial_enabled and world.options.city_trial_goal.current_key not in [
        world.options.city_trial_goal.option_none,
        world.options.city_trial_goal.option_n_checklist_blocks,
    ]:
        goal_locations_to_exclude.add(world.options.city_trial_goal.current_key)

    if world.air_ride_enabled and world.options.air_ride_goal.current_key not in [
        world.options.air_ride_goal.option_none,
        world.options.air_ride_goal.option_n_checklist_blocks,
    ]:
        goal_locations_to_exclude.add(world.options.air_ride_goal.current_key)

    if world.top_ride_enabled and world.options.top_ride_goal.current_key not in [
        world.options.top_ride_goal.option_none,
        world.options.top_ride_goal.option_n_checklist_blocks,
    ]:
        goal_locations_to_exclude.add(world.options.top_ride_goal.current_key)

    # create the "Menu" default Region, which will connect all game modes.
    menu_region = Region(world.origin_region_name, world.player, world.multiworld)
    world.multiworld.regions.append(menu_region)

    # create and connect "City Trial" region to menu
    if world.city_trial_enabled:
        city_trial_region = Region("City Trial", world.player, world.multiworld)
        world.multiworld.regions.append(city_trial_region)
        menu_region.connect(city_trial_region)
        connect_city_trial_region(world, city_trial_region)

    # create and connect "Air Ride" region to menu
    if world.air_ride_enabled:
        air_ride_region = Region("Air Ride", world.player, world.multiworld)
        world.multiworld.regions.append(air_ride_region)
        menu_region.connect(air_ride_region)
        connect_air_ride_region(world, air_ride_region)

    # create and connect "Top Ride" region to menu
    if world.top_ride_enabled:
        top_ride_region = Region("Top Ride", world.player, world.multiworld)
        world.multiworld.regions.append(top_ride_region)
        menu_region.connect(top_ride_region)
        connect_top_ride_region(world, top_ride_region)

    # Assign City Trial progress locations to their region if City Trial is not disabled in options.
    # Progress locations are sorted for deterministic results.
    if world.city_trial_enabled:
        # priority locations
        for location_name in sorted(world.city_trial_priority_locations):
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.PRIORITY
            region.locations.append(location)

        # default locations
        for location_name in world.city_trial_default_locations:
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.DEFAULT
            region.locations.append(location)

        # excluded locations
        for location_name in world.city_trial_excluded_locations:
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.EXCLUDED
            region.locations.append(location)

    # Assign Air Ride locations to their region if Air Ride is not disabled in options.
    # Progress locations are sorted for deterministic results.
    if world.air_ride_enabled:
        # priority locations
        for location_name in sorted(world.air_ride_priority_locations):
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = AIR_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.PRIORITY
            region.locations.append(location)

        # default locations
        for location_name in world.air_ride_default_locations:
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = AIR_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.DEFAULT
            region.locations.append(location)

        # excluded locations
        for location_name in world.air_ride_excluded_locations:
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = AIR_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.EXCLUDED
            region.locations.append(location)

    # Assign Top Ride locations to their region if Top Ride is not disabled in options.
    # Progress locations are sorted for deterministic results.
    if world.top_ride_enabled:
        # priority locations
        for location_name in sorted(world.top_ride_priority_locations):
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = TOP_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.PRIORITY
            region.locations.append(location)

        # default locations
        for location_name in world.top_ride_default_locations:
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = TOP_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.DEFAULT
            region.locations.append(location)

        # excluded locations
        for location_name in world.top_ride_excluded_locations:
            if location_name in goal_locations_to_exclude:
                continue  # Skip goal locations - they'll be replaced by event locations
            data = TOP_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.EXCLUDED
            region.locations.append(location)

    # determine the goal for the world, given player options
    determine_goal(world)

    # from Utils import visualize_regions
    # visualize_regions(world.multiworld.get_region("Menu", world.player), "my_world.puml", show_entrance_names=True)


def connect_city_trial_region(world: "KARWorld", city_trial_region: Region) -> None:
    # free run region
    free_run = Region("City Trial: Free Run", world.player, world.multiworld)
    world.multiworld.regions.append(free_run)
    city_trial_region.connect(free_run)

    # stadium regions
    stadium_destruction_derby_all = Region("Stadium: DESTRUCTION DERBY ALL", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_destruction_derby_all)
    stadium_destruction_derby_1 = Region("Stadium: DESTRUCTION DERBY 1", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_destruction_derby_1)
    stadium_destruction_derby_2 = Region("Stadium: DESTRUCTION DERBY 2", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_destruction_derby_2)
    stadium_destruction_derby_3 = Region("Stadium: DESTRUCTION DERBY 3", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_destruction_derby_3)
    stadium_destruction_derby_4 = Region("Stadium: DESTRUCTION DERBY 4", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_destruction_derby_4)
    stadium_destruction_derby_5 = Region("Stadium: DESTRUCTION DERBY 5", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_destruction_derby_5)

    stadium_drag_race_1 = Region("Stadium: DRAG RACE 1", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_drag_race_1)
    stadium_drag_race_2 = Region("Stadium: DRAG RACE 2", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_drag_race_2)
    stadium_drag_race_3 = Region("Stadium: DRAG RACE 3", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_drag_race_3)
    stadium_drag_race_4 = Region("Stadium: DRAG RACE 4", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_drag_race_4)

    stadium_high_jump = Region("Stadium: HIGH JUMP", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_high_jump)

    stadium_target_flight = Region("Stadium: TARGET FLIGHT", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_target_flight)

    stadium_air_glider = Region("Stadium: AIR GLIDER", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_air_glider)

    stadium_kirby_melee_all = Region("Stadium: KIRBY MELEE ALL", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_kirby_melee_all)
    stadium_kirby_melee_1 = Region("Stadium: KIRBY MELEE 1", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_kirby_melee_1)
    stadium_kirby_melee_2 = Region("Stadium: KIRBY MELEE 2", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_kirby_melee_2)

    stadium_vs_king_dedede = Region("Stadium: VS. KING DEDEDE", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_vs_king_dedede)

    stadium_single_race_1 = Region("Stadium: SINGLE RACE 1", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_1)
    stadium_single_race_2 = Region("Stadium: SINGLE RACE 2", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_2)
    stadium_single_race_3 = Region("Stadium: SINGLE RACE 3", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_3)
    stadium_single_race_4 = Region("Stadium: SINGLE RACE 4", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_4)
    stadium_single_race_5 = Region("Stadium: SINGLE RACE 5", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_5)
    stadium_single_race_6 = Region("Stadium: SINGLE RACE 6", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_6)
    stadium_single_race_7 = Region("Stadium: SINGLE RACE 7", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_7)
    stadium_single_race_8 = Region("Stadium: SINGLE RACE 8", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_8)
    stadium_single_race_9 = Region("Stadium: SINGLE RACE 9", world.player, world.multiworld)
    world.multiworld.regions.append(stadium_single_race_9)

    # connect stadium regions
    city_trial_region.connect(stadium_destruction_derby_all)
    stadium_destruction_derby_all.connect(stadium_destruction_derby_1)
    stadium_destruction_derby_all.connect(stadium_destruction_derby_2)
    stadium_destruction_derby_all.connect(
        stadium_destruction_derby_3,
        None,
        lambda state: state.can_reach_location(
            "Stadium: DESTRUCTION DERBY 2 In one game, KO a rival 10 times or more!", world.player
        ),
    )
    stadium_destruction_derby_all.connect(
        stadium_destruction_derby_4,
        None,
        lambda state: state.can_reach_location(
            "Stadium: DESTRUCTION DERBY 3 In one game, KO your rivals 5 or more times!", world.player
        ),
    )
    stadium_destruction_derby_all.connect(
        stadium_destruction_derby_5,
        None,
        lambda state: state.can_reach_location(
            "Stadium: DESTRUCTION DERBY 4 In one game, KO a rival 10 times or more!", world.player
        ),
    )

    city_trial_region.connect(stadium_drag_race_1)
    city_trial_region.connect(stadium_drag_race_2)
    city_trial_region.connect(stadium_drag_race_3)
    city_trial_region.connect(
        stadium_drag_race_4,
        None,
        lambda state: state.can_reach_location("Stadium: DRAG RACE 3 Finish in less than 00:27:00!", world.player),
    )

    city_trial_region.connect(stadium_high_jump)
    city_trial_region.connect(stadium_target_flight)
    city_trial_region.connect(stadium_air_glider)

    city_trial_region.connect(stadium_kirby_melee_all)
    stadium_kirby_melee_all.connect(stadium_kirby_melee_1)
    stadium_kirby_melee_all.connect(
        stadium_kirby_melee_2,
        None,
        lambda state: state.can_reach_location(
            "Stadium: KIRBY MELEE 1 In one game, KO over 75 enemies by yourself!", world.player
        ),
    )

    city_trial_region.connect(stadium_vs_king_dedede)

    city_trial_region.connect(stadium_single_race_1)
    city_trial_region.connect(stadium_single_race_2)
    city_trial_region.connect(stadium_single_race_3)
    city_trial_region.connect(stadium_single_race_4)
    city_trial_region.connect(stadium_single_race_5)
    city_trial_region.connect(stadium_single_race_6)
    city_trial_region.connect(stadium_single_race_7)
    city_trial_region.connect(stadium_single_race_8)
    city_trial_region.connect(stadium_single_race_9)


def connect_air_ride_region(world: "KARWorld", air_ride_region: Region) -> None:
    # create Air Ride Regions
    time_attack_region = Region("Air Ride: Time Attack", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_region)

    free_run_region = Region("Air Ride: Free Run", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_region)

    air_ride_magma_flows = Region("Air Ride: MAGMA FLOWS", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_magma_flows)
    air_ride_fantasy_meadows = Region("Air Ride: FANTASY MEADOWS", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_fantasy_meadows)
    air_ride_celestial_valley = Region("Air Ride: CELESTIAL VALLEY", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_celestial_valley)
    air_ride_beanstalk_park = Region("Air Ride: BEANSTALK PARK", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_beanstalk_park)
    air_ride_frozen_hillside = Region("Air Ride: FROZEN HILLSIDE", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_frozen_hillside)
    air_ride_machine_passage = Region("Air Ride: MACHINE PASSAGE", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_machine_passage)
    air_ride_sky_sands = Region("Air Ride: SKY SANDS", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_sky_sands)
    air_ride_checker_knights = Region("Air Ride: CHECKER KNIGHTS", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_checker_knights)
    air_ride_nebula_belt = Region("Air Ride: NEBULA BELT", world.player, world.multiworld)
    world.multiworld.regions.append(air_ride_nebula_belt)

    time_attack_magma_flows = Region("Air Ride: Time Attack: MAGMA FLOWS", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_magma_flows)
    time_attack_fantasy_meadows = Region("Air Ride: Time Attack: FANTASY MEADOWS", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_fantasy_meadows)
    time_attack_celestial_valley = Region("Air Ride: Time Attack: CELESTIAL VALLEY", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_celestial_valley)
    time_attack_beanstalk_park = Region("Air Ride: Time Attack: BEANSTALK PARK", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_beanstalk_park)
    time_attack_frozen_hillside = Region("Air Ride: Time Attack: FROZEN HILLSIDE", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_frozen_hillside)
    time_attack_machine_passage = Region("Air Ride: Time Attack: MACHINE PASSAGE", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_machine_passage)
    time_attack_sky_sands = Region("Air Ride: Time Attack: SKY SANDS", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_sky_sands)
    time_attack_checker_knights = Region("Air Ride: Time Attack: CHECKER KNIGHTS", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_checker_knights)
    time_attack_nebula_belt = Region("Air Ride: Time Attack: NEBULA BELT", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_nebula_belt)

    free_run_magma_flows = Region("Air Ride: Free Run: MAGMA FLOWS", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_magma_flows)
    free_run_fantasy_meadows = Region("Air Ride: Free Run: FANTASY MEADOWS", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_fantasy_meadows)
    free_run_celestial_valley = Region("Air Ride: Free Run: CELESTIAL VALLEY", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_celestial_valley)
    free_run_beanstalk_park = Region("Air Ride: Free Run: BEANSTALK PARK", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_beanstalk_park)
    free_run_frozen_hillside = Region("Air Ride: Free Run: FROZEN HILLSIDE", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_frozen_hillside)
    free_run_machine_passage = Region("Air Ride: Free Run: MACHINE PASSAGE", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_machine_passage)
    free_run_sky_sands = Region("Air Ride: Free Run: SKY SANDS", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_sky_sands)
    free_run_checker_knights = Region("Air Ride: Free Run: CHECKER KNIGHTS", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_checker_knights)
    free_run_nebula_belt = Region("Air Ride: Free Run: NEBULA BELT", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_nebula_belt)

    # connect main Air Ride Regions
    air_ride_region.connect(time_attack_region)
    air_ride_region.connect(free_run_region)

    # connect courses to air ride
    air_ride_region.connect(air_ride_magma_flows)
    air_ride_region.connect(air_ride_fantasy_meadows)
    air_ride_region.connect(air_ride_celestial_valley)
    air_ride_region.connect(air_ride_beanstalk_park)
    air_ride_region.connect(air_ride_frozen_hillside)
    air_ride_region.connect(air_ride_machine_passage)
    air_ride_region.connect(air_ride_sky_sands)
    air_ride_region.connect(air_ride_checker_knights)
    air_ride_region.connect(
        air_ride_nebula_belt,
        None,
        lambda state: state.can_reach_location("Air Ride: Race over 100 laps!", world.player),
    )

    # connect courses to time attack
    time_attack_region.connect(time_attack_magma_flows)
    time_attack_region.connect(time_attack_fantasy_meadows)
    time_attack_region.connect(time_attack_celestial_valley)
    time_attack_region.connect(time_attack_beanstalk_park)
    time_attack_region.connect(time_attack_frozen_hillside)
    time_attack_region.connect(time_attack_machine_passage)
    time_attack_region.connect(time_attack_sky_sands)
    time_attack_region.connect(time_attack_checker_knights)
    time_attack_region.connect(
        time_attack_nebula_belt,
        None,
        lambda state: state.can_reach_location("Air Ride: Race over 100 laps!", world.player),
    )

    # connect courses to free run
    free_run_region.connect(free_run_magma_flows)
    free_run_region.connect(free_run_fantasy_meadows)
    free_run_region.connect(free_run_celestial_valley)
    free_run_region.connect(free_run_beanstalk_park)
    free_run_region.connect(free_run_frozen_hillside)
    free_run_region.connect(free_run_machine_passage)
    free_run_region.connect(free_run_sky_sands)
    free_run_region.connect(free_run_checker_knights)
    free_run_region.connect(
        free_run_nebula_belt,
        None,
        lambda state: state.can_reach_location("Air Ride: Race over 100 laps!", world.player),
    )


def connect_top_ride_region(world: "KARWorld", top_ride_region: Region) -> None:
    # create Top Ride Regions
    time_attack_region = Region("Top Ride: Time Attack", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_region)

    free_run_region = Region("Top Ride: Free Run", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_region)

    top_ride_grass = Region("Top Ride: GRASS", world.player, world.multiworld)
    top_ride_metal = Region("Top Ride: METAL", world.player, world.multiworld)
    top_ride_light = Region("Top Ride: LIGHT", world.player, world.multiworld)
    top_ride_sand = Region("Top Ride: SAND", world.player, world.multiworld)
    top_ride_fire = Region("Top Ride: FIRE", world.player, world.multiworld)
    top_ride_water = Region("Top Ride: WATER", world.player, world.multiworld)
    top_ride_sky = Region("Top Ride: SKY", world.player, world.multiworld)
    world.multiworld.regions.append(top_ride_grass)
    world.multiworld.regions.append(top_ride_metal)
    world.multiworld.regions.append(top_ride_light)
    world.multiworld.regions.append(top_ride_sand)
    world.multiworld.regions.append(top_ride_fire)
    world.multiworld.regions.append(top_ride_water)
    world.multiworld.regions.append(top_ride_sky)

    free_run_grass = Region("Top Ride: Free Run: GRASS", world.player, world.multiworld)
    free_run_metal = Region("Top Ride: Free Run: METAL", world.player, world.multiworld)
    free_run_light = Region("Top Ride: Free Run: LIGHT", world.player, world.multiworld)
    free_run_sand = Region("Top Ride: Free Run: SAND", world.player, world.multiworld)
    free_run_fire = Region("Top Ride: Free Run: FIRE", world.player, world.multiworld)
    free_run_water = Region("Top Ride: Free Run: WATER", world.player, world.multiworld)
    free_run_sky = Region("Top Ride: Free Run: SKY", world.player, world.multiworld)
    world.multiworld.regions.append(free_run_grass)
    world.multiworld.regions.append(free_run_metal)
    world.multiworld.regions.append(free_run_light)
    world.multiworld.regions.append(free_run_sand)
    world.multiworld.regions.append(free_run_fire)
    world.multiworld.regions.append(free_run_water)
    world.multiworld.regions.append(free_run_sky)

    time_attack_grass = Region("Top Ride: Time Attack: GRASS", world.player, world.multiworld)
    time_attack_metal = Region("Top Ride: Time Attack: METAL", world.player, world.multiworld)
    time_attack_light = Region("Top Ride: Time Attack: LIGHT", world.player, world.multiworld)
    time_attack_sand = Region("Top Ride: Time Attack: SAND", world.player, world.multiworld)
    time_attack_fire = Region("Top Ride: Time Attack: FIRE", world.player, world.multiworld)
    time_attack_water = Region("Top Ride: Time Attack: WATER", world.player, world.multiworld)
    time_attack_sky = Region("Top Ride: Time Attack: SKY", world.player, world.multiworld)
    world.multiworld.regions.append(time_attack_grass)
    world.multiworld.regions.append(time_attack_metal)
    world.multiworld.regions.append(time_attack_light)
    world.multiworld.regions.append(time_attack_sand)
    world.multiworld.regions.append(time_attack_fire)
    world.multiworld.regions.append(time_attack_water)
    world.multiworld.regions.append(time_attack_sky)

    # connect main Top Ride regions
    top_ride_region.connect(time_attack_region)
    top_ride_region.connect(free_run_region)

    # connect courses to Top Ride region
    top_ride_region.connect(top_ride_grass)
    top_ride_region.connect(top_ride_metal)
    top_ride_region.connect(top_ride_light)
    top_ride_region.connect(top_ride_sand)
    top_ride_region.connect(top_ride_fire)
    top_ride_region.connect(top_ride_water)
    top_ride_region.connect(top_ride_sky)

    # connect free run courses to free run region
    free_run_region.connect(free_run_grass)
    free_run_region.connect(free_run_metal)
    free_run_region.connect(free_run_light)
    free_run_region.connect(free_run_sand)
    free_run_region.connect(free_run_fire)
    free_run_region.connect(free_run_water)
    free_run_region.connect(free_run_sky)

    # connect time attack courses to time attack region
    time_attack_region.connect(time_attack_grass)
    time_attack_region.connect(time_attack_metal)
    time_attack_region.connect(time_attack_light)
    time_attack_region.connect(time_attack_sand)
    time_attack_region.connect(time_attack_fire)
    time_attack_region.connect(time_attack_water)
    time_attack_region.connect(time_attack_sky)


def count_locations_by_region(world: "KARWorld") -> dict[str, int]:
    """
    Count the number of locations in each region.

    :param world: The KARWorld instance
    :return: Dict mapping region name to location count
    """
    region_location_counts: dict[str, int] = {}

    for region in world.multiworld.get_regions(world.player):
        # Count actual locations (not event locations, which have address=None)
        location_count = sum(1 for loc in region.locations if loc.address is not None)
        if location_count > 0:
            region_location_counts[region.name] = location_count

    return region_location_counts


def create_n_blocks_rule(
    world: "KARWorld", mode_prefix: str, required_blocks: int
) -> Callable[[CollectionState], bool]:
    """
    Create a rule that checks if the player can access enough locations to complete N blocks.

    :param world: The KARWorld instance
    :param mode_prefix: The mode prefix (e.g., "City Trial", "Air Ride", "Top Ride")
    :param required_blocks: The number of blocks required for victory
    :return: A rule function that checks if N blocks can be completed
    """
    from .KARData import ProgressiveStadiumUnlockType

    # Get location counts per region
    region_counts = count_locations_by_region(world)

    # Separate base locations from stadium locations
    # Map specific stadium unlocks to their region location counts
    # Track "ALL" regions separately to avoid double-counting
    base_count = 0
    stadium_unlock_to_count: dict[str, int] = {}
    all_region_to_unlocks: dict[str, tuple[int, list[str]]] = {}  # region_name -> (count, [unlock_items])

    for region_name, count in region_counts.items():
        # For City Trial, stadium regions are separate regions that start with "Stadium:"
        # For Air Ride and Top Ride, all regions start with the mode prefix
        is_stadium_region = region_name.startswith("Stadium:")
        is_mode_region = region_name.startswith(mode_prefix)

        # Include this region if it's either a mode-specific region OR a stadium (for City Trial only)
        if is_mode_region or (mode_prefix == "City Trial" and is_stadium_region):
            if is_stadium_region:
                # This is a stadium region
                if "ALL" in region_name:
                    # This is an "ALL" region - track it separately
                    # Extract base stadium name (e.g., "Stadium: DESTRUCTION DERBY ALL" -> "DESTRUCTION DERBY")
                    stadium_base = region_name.replace("Stadium:", "").replace("ALL", "").strip()

                    # Find all unlocks that match this stadium type
                    matching_unlocks = []
                    for unlock in ProgressiveStadiumUnlockType:
                        unlock_name = unlock.value.replace("Unlock Stadium:", "").strip()
                        if stadium_base in unlock_name:
                            matching_unlocks.append(unlock.value)

                    all_region_to_unlocks[region_name] = (count, matching_unlocks)
                else:
                    # This is a specific numbered region - find exact match
                    stadium_name = region_name.replace("Stadium:", "").strip()

                    # Find exact matching unlock item
                    for unlock in ProgressiveStadiumUnlockType:
                        unlock_name = unlock.value.replace("Unlock Stadium:", "").strip()
                        if unlock_name == stadium_name:
                            stadium_unlock_to_count[unlock.value] = count
                            break
            else:
                # This is a base region (e.g., "City Trial", "Air Ride", "Top Ride")
                base_count += count

    # If we can already reach the required blocks without stadiums, no rule needed
    if base_count >= required_blocks:
        return lambda state: True

    # Create a rule that counts accessible locations based on stadium unlocks
    def can_access_n_blocks(state: CollectionState) -> bool:
        accessible_count = base_count

        # Add specific stadium region counts
        for unlock_item, count in stadium_unlock_to_count.items():
            if state.has(unlock_item, world.player):
                accessible_count += count

        # Add "ALL" region counts (only once per ALL region, if ANY matching unlock is present)
        for count, matching_unlocks in all_region_to_unlocks.values():
            if state.has_any(matching_unlocks, world.player):
                accessible_count += count

        return accessible_count >= required_blocks

    return can_access_n_blocks


def determine_goal(world: "KARWorld") -> None:
    """
    Determine the goal for the world and create event locations for each enabled mode's goal.
    Event items placed on these locations are checked for completion.
    """

    goal_event_items: list[str] = []

    # City Trial goal handling
    if world.options.city_trial_goal.value != world.options.city_trial_goal.option_none:
        goal_event_items.append(VictoryEventType.CITY_TRIAL_VICTORY.value)

        match world.options.city_trial_goal.current_key:
            case world.options.city_trial_goal.option_n_checklist_blocks:
                # For N checklist blocks, place event in the main City Trial region
                city_trial_region = world.get_region("City Trial")
                # Create rule to ensure player has access to enough locations
                n_blocks_rule = (
                    create_n_blocks_rule(world, "City Trial", world.options.city_trial_checklist_amount.value)
                    if world.options.city_trial_progressive_stadiums
                    else None
                )
                create_event_location(
                    world,
                    city_trial_region,
                    f"City Trial: Complete {world.options.city_trial_checklist_amount.value} Checklist Blocks",
                    VictoryEventType.CITY_TRIAL_VICTORY.value,
                    n_blocks_rule,
                )
            case _:
                # For specific goal locations (100 blocks, Hydra+Dragoon, King Dedede)
                # Get the region from the location table since the actual location was excluded
                goal_location_data = CITY_TRIAL_LOCATION_TABLE[world.options.city_trial_goal.current_key]
                goal_region = world.get_region(goal_location_data.region)

                # For 100 blocks goal in main region, add rule if progressive stadiums enabled
                blocks_rule = None
                if (
                    world.options.city_trial_progressive_stadiums
                    and world.options.city_trial_goal.current_key
                    == world.options.city_trial_goal.option_100_checklist_blocks
                    and goal_location_data.region == "City Trial"
                ):
                    blocks_rule = create_n_blocks_rule(world, "City Trial", 100)

                create_event_location(
                    world,
                    goal_region,
                    f"{world.options.city_trial_goal.current_key} (Victory)",
                    VictoryEventType.CITY_TRIAL_VICTORY.value,
                    blocks_rule,
                )

    # Air Ride goal handling
    if world.options.air_ride_goal.value != world.options.air_ride_goal.option_none:
        goal_event_items.append(VictoryEventType.AIR_RIDE_VICTORY.value)

        match world.options.air_ride_goal.current_key:
            case world.options.air_ride_goal.option_n_checklist_blocks:
                air_ride_region = world.get_region("Air Ride")
                # Create rule to ensure player has access to enough locations
                n_blocks_rule = create_n_blocks_rule(world, "Air Ride", world.options.air_ride_checklist_amount.value)
                create_event_location(
                    world,
                    air_ride_region,
                    f"Air Ride: Complete {world.options.air_ride_checklist_amount.value} Checklist Blocks",
                    VictoryEventType.AIR_RIDE_VICTORY.value,
                    n_blocks_rule,
                )
            case _:
                # For 100 blocks goal
                # Get the region from the location table since the actual location was excluded
                goal_location_data = AIR_RIDE_LOCATION_TABLE[world.options.air_ride_goal.current_key]
                goal_region = world.get_region(goal_location_data.region)

                # For 100 blocks goal in main region, add rule
                blocks_rule = None
                if (
                    world.options.air_ride_goal.current_key == world.options.air_ride_goal.option_100_checklist_blocks
                    and goal_location_data.region == "Air Ride"
                ):
                    blocks_rule = create_n_blocks_rule(world, "Air Ride", 100)

                create_event_location(
                    world,
                    goal_region,
                    f"{world.options.air_ride_goal.current_key} (Victory)",
                    VictoryEventType.AIR_RIDE_VICTORY.value,
                    blocks_rule,
                )

    # Top Ride goal handling
    if world.options.top_ride_goal.value != world.options.top_ride_goal.option_none:
        goal_event_items.append(VictoryEventType.TOP_RIDE_VICTORY.value)

        match world.options.top_ride_goal.current_key:
            case world.options.top_ride_goal.option_n_checklist_blocks:
                top_ride_region = world.get_region("Top Ride")
                # Create rule to ensure player has access to enough locations
                n_blocks_rule = create_n_blocks_rule(world, "Top Ride", world.options.top_ride_checklist_amount.value)
                create_event_location(
                    world,
                    top_ride_region,
                    f"Top Ride: Complete {world.options.top_ride_checklist_amount.value} Checklist Blocks",
                    VictoryEventType.TOP_RIDE_VICTORY.value,
                    n_blocks_rule,
                )
            case _:
                # For 100 blocks goal
                # Get the region from the location table since the actual location was excluded
                goal_location_data = TOP_RIDE_LOCATION_TABLE[world.options.top_ride_goal.current_key]
                goal_region = world.get_region(goal_location_data.region)

                # For 100 blocks goal in main region, add rule
                blocks_rule = None
                if (
                    world.options.top_ride_goal.current_key == world.options.top_ride_goal.option_100_checklist_blocks
                    and goal_location_data.region == "Top Ride"
                ):
                    blocks_rule = create_n_blocks_rule(world, "Top Ride", 100)

                create_event_location(
                    world,
                    goal_region,
                    f"{world.options.top_ride_goal.current_key} (Victory)",
                    VictoryEventType.TOP_RIDE_VICTORY.value,
                    blocks_rule,
                )

    # Set multiworld completion condition to check for all victory event items
    if len(goal_event_items) > 0:
        world.multiworld.completion_condition[world.player] = lambda state: all(
            state.has(event_item, world.player) for event_item in goal_event_items
        )
