import typing
from collections.abc import Callable
from typing import List

from BaseClasses import CollectionState, LocationProgressType, Region

from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    KARLocation,
)

if typing.TYPE_CHECKING:
    from . import KARWorld


def create_regions(world: "KARWorld"):
    """
    Create regions, place locations in regions, and connect regions for the Kirby Air Ride world.
    """
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
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.PRIORITY
            region.locations.append(location)

        # default locations
        for location_name in world.city_trial_default_locations:
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.DEFAULT
            region.locations.append(location)

        # excluded locations
        for location_name in world.city_trial_excluded_locations:
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
            data = AIR_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.PRIORITY
            region.locations.append(location)

        # default locations
        for location_name in world.air_ride_default_locations:
            data = AIR_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.DEFAULT
            region.locations.append(location)

        # excluded locations
        for location_name in world.air_ride_excluded_locations:
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
            data = TOP_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.PRIORITY
            region.locations.append(location)

        # default locations
        for location_name in world.top_ride_default_locations:
            data = TOP_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.DEFAULT
            region.locations.append(location)

        # excluded locations
        for location_name in world.top_ride_excluded_locations:
            data = TOP_RIDE_LOCATION_TABLE[location_name]
            region = world.get_region(data.region)
            location = KARLocation(world.player, location_name, region, data)
            location.progress_type = LocationProgressType.EXCLUDED
            region.locations.append(location)

    # place checkbox reward items as locked items on their respective locations if the player option is enabled.
    # these are locked because until checkbox reward randomization is possible in-game, only the player's game can
    # collect these.
    if world.options.checkbox_reward_items:
        if world.city_trial_enabled:
            for location_name, location_data in CITY_TRIAL_LOCATION_TABLE.items():
                if location_data.code is not None and location_data.reward != "None":
                    item = world.create_item(location_data.reward)
                    world.get_location(location_name).place_locked_item(item)
        if world.air_ride_enabled:
            for location_name, location_data in AIR_RIDE_LOCATION_TABLE.items():
                if location_data.code is not None and location_data.reward != "None":
                    item = world.create_item(location_data.reward)
                    world.get_location(location_name).place_locked_item(item)
        if world.top_ride_enabled:
            for location_name, location_data in TOP_RIDE_LOCATION_TABLE.items():
                if location_data.code is not None and location_data.reward != "None":
                    item = world.create_item(location_data.reward)
                    world.get_location(location_name).place_locked_item(item)

    # TODO:
    # might need to place stadium unlock items for those stadiums that are unlocked by checkboxes in-game,
    # since we can't prevent these from being unlocked by the checkbox. Currently, this is just overwritten
    # by us right after the stadium is unlocked, so we effectively ignore these checkbox rewards in favor of the AP
    # item

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


def determine_goal(world: "KARWorld") -> None:
    """
    Determine the goal for the world, given the player options of goals selected for each game mode.
    """
    goal_func_list: List[Callable[[CollectionState], bool]] = []

    match world.options.city_trial_goal.current_key:
        case world.options.city_trial_goal.option_none:
            pass
        case world.options.city_trial_goal.option_n_checklist_blocks:
            # can't currently gate anything and the player can always complete all checklist blocks regardless,
            # so just being able to reach the city trial region is enough
            goal_func_list.append(lambda state: state.can_reach_region("City Trial", world.player))
        case _:
            goal_func_list.append(
                lambda state: state.can_reach_location(world.options.city_trial_goal.current_key, world.player)
            )

    match world.options.air_ride_goal.current_key:
        case world.options.air_ride_goal.option_none:
            pass
        case world.options.air_ride_goal.option_n_checklist_blocks:
            # can't currently gate anything and the player can always complete all checklist blocks regardless,
            # so just being able to reach the air ride region is enough
            goal_func_list.append(lambda state: state.can_reach_region("Air Ride", world.player))
        case _:
            goal_func_list.append(
                lambda state: state.can_reach_location(world.options.air_ride_goal.current_key, world.player)
            )

    match world.options.top_ride_goal.current_key:
        case world.options.top_ride_goal.option_none:
            pass
        case world.options.top_ride_goal.option_n_checklist_blocks:
            # can't currently gate anything and the player can always complete all checklist blocks regardless,
            # so just being able to reach the top ride region is enough
            goal_func_list.append(lambda state: state.can_reach_region("Top Ride", world.player))
        case _:
            goal_func_list.append(
                lambda state: state.can_reach_location(world.options.top_ride_goal.current_key, world.player)
            )

    # multiworld completion condition is all goal conditions being true
    if len(goal_func_list) > 0:
        world.multiworld.completion_condition[world.player] = lambda state: all(
            [func(state) for func in goal_func_list]
        )
