from collections.abc import Mapping
from typing import Any, Callable, ClassVar, Dict, Set

from BaseClasses import CollectionState, ItemClassification, LocationProgressType, Region, Tutorial
from Fill import FillError
from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import set_rule
from worlds.LauncherComponents import (
    Component,
    Type,
    components,
    icon_paths,
    launch_subprocess,
)

from .Items import ITEM_TABLE, KARItem, item_name_groups
from .KAROptions import KAROptions, kar_option_groups
from .Locations import AIR_RIDE_LOCATION_TABLE, CITY_TRIAL_LOCATION_TABLE, KARLocation, location_name_groups


def run_client() -> None:
    """
    Launch Kirby Air Ride client.
    """
    print("Running Kirby Air Ride Client")
    from .KARClient import main

    launch_subprocess(main, name="KirbyAirRideClient")


components.append(
    Component(
        "Kirby Air Ride Client",
        func=run_client,
        component_type=Type.CLIENT,
        icon="Kirby Air Ride",
    )
)
icon_paths["Kirby Air Ride"] = "ap:worlds.kirby_air_ride/assets/allpatch.png"


class KARWeb(WebWorld):
    """
    This class handles the web interface for Kirby Air Ride.

    The web interface includes the setup guide and the options page for generating YAMLs.
    """

    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up the Archipelago Kirby Air Ride software on your computer.",
            "English",
            "setup_en.md",
            "setup/en",
            ["DeDeDK"],
        )
    ]
    theme = "partyTime"
    option_groups = kar_option_groups
    rich_text_options_doc = True


class KARWorld(World):
    """
    Kirby's Ready to Ride! Prepare for fast and furious racing action as Kirby hits Warpstar speed! Use ultra-simple
    controls to race and battle your pals in one of three hectic game modes!
    """

    options_dataclass = KAROptions
    options: KAROptions
    game: ClassVar[str] = "Kirby Air Ride"
    topology_present: bool = False
    explicit_indirect_conditions = False

    item_name_to_id: ClassVar[dict[str, int]] = {
        item_name: item_data.code for item_name, item_data in ITEM_TABLE.items() if item_data.code is not None
    }
    location_name_to_id: ClassVar[dict[str, int]] = {
        location_name: location_data.code
        for location_name, location_data in (CITY_TRIAL_LOCATION_TABLE | AIR_RIDE_LOCATION_TABLE).items()
        if location_data.code is not None
    }

    item_name_groups: ClassVar[Dict[str, Set[str]]] = item_name_groups
    location_name_groups: ClassVar[Dict[str, Set[str]]] = location_name_groups

    web: ClassVar[KARWeb] = KARWeb()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.city_trial_priority_locations: set[str] = set()
        self.city_trial_default_locations: set[str] = set()
        self.city_trial_excluded_locations: set[str] = set()
        self.air_ride_priority_locations: set[str] = set()
        self.air_ride_default_locations: set[str] = set()
        self.air_ride_excluded_locations: set[str] = set()
        self.item_classification_overrides: dict[str, ItemClassification] = {}
        self.useful_pool: set[str] = set()
        self.filler_pool: set[str] = set()
        self.trap_pool: set[str] = set()

    def _determine_item_classification_overrides(self) -> None:
        """
        Determine item classification overrides. The classification of an item may be affected by which options are
        enabled or disabled.
        """
        # Override certain items to be filler depending on user options.
        override_as_filler = []
        for item_name in override_as_filler:
            self.item_classification_overrides[item_name] = ItemClassification.filler

        # Override certain items to be useful depending on user options.
        override_as_useful = []
        # if permanent patches are not progression but are enabled, override as useful
        if self.options.city_trial_permanent_patches and not self.options.city_trial_permanent_patch_progression:
            override_as_useful.extend([item_name for item_name in ITEM_TABLE if "Permanent" in item_name])

        for item_name in override_as_useful:
            self.item_classification_overrides[item_name] = ItemClassification.useful

    def _determine_locations_progress_type(self) -> None:
        """
        Determine the progress type of each location based on player options. Progress types are:
        PRIORITY = will have progression items placed on them
        DEFAULT = useful or progression?
        EXCLUDED = will only have filler/trap placed on them
        """
        # categorzie City Trial locations progress type based on player options choices
        # currently, we do not have any options that prioritize locations other than the core options,
        # so priority_locations is not used.
        for location in CITY_TRIAL_LOCATION_TABLE:
            if (
                not self.options.city_trial_progression_high_effort
                and location in location_name_groups["City Trial: High Effort"]
            ):
                self.city_trial_excluded_locations.add(location)
            elif (
                not self.options.city_trial_progression_multiplayer
                and location in location_name_groups["City Trial: Multiplayer"]
            ):
                self.city_trial_excluded_locations.add(location)
            elif (
                not self.options.city_trial_progression_free_run
                and location in location_name_groups["City Trial: Free Run"]
            ):
                self.city_trial_excluded_locations.add(location)
            else:
                self.city_trial_default_locations.add(location)

        assert self.city_trial_default_locations.isdisjoint(self.city_trial_excluded_locations)

        # categorzie Air Ride locations progress type based on player options choices
        # currently, we do not have any options that prioritize locations other than the core options,
        # so priority_locations is not used.
        for location in AIR_RIDE_LOCATION_TABLE:
            if (
                not self.options.air_ride_progression_high_effort
                and location in location_name_groups["Air Ride: High Effort"]
            ):
                self.air_ride_excluded_locations.add(location)
            elif (
                not self.options.air_ride_progression_free_run
                and location in location_name_groups["Air Ride: Free Run"]
            ):
                self.air_ride_excluded_locations.add(location)
            elif (
                not self.options.air_ride_progression_time_attack
                and location in location_name_groups["Air Ride: Time Attack"]
            ):
                self.air_ride_excluded_locations.add(location)
            else:
                self.air_ride_default_locations.add(location)

        assert self.air_ride_default_locations.isdisjoint(self.air_ride_excluded_locations)

    def generate_early(self) -> None:
        """
        Run before any general steps of the MultiWorld other than options.
        """

        # Determine locations progress types from player options.
        self._determine_locations_progress_type()

        # Determine any item classification overrides from player options.
        self._determine_item_classification_overrides()

    def create_regions(self) -> None:
        """
        Create and connect regions for the Kirby Air Ride world.

        """
        # create the "Menu" default Region, which will connect all game modes.
        menu_region = Region(self.origin_region_name, self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        # create and connect "City Trial" region to menu
        if self.options.city_trial_goal.value != self.options.city_trial_goal.option_none:
            city_trial_region = Region("City Trial", self.player, self.multiworld)
            self.multiworld.regions.append(city_trial_region)
            menu_region.connect(city_trial_region)
            # connect City Trial Region
            self.connect_city_trial_region(city_trial_region)

        # create and connect "Air Ride" region to menu
        if self.options.air_ride_goal.value != self.options.air_ride_goal.option_none:
            air_ride_region = Region("Air Ride", self.player, self.multiworld)
            self.multiworld.regions.append(air_ride_region)
            menu_region.connect(air_ride_region)
            # connect Air Ride Region
            self.connect_air_ride_region(air_ride_region)

        # Assign City Trial progress locations to their region if City Trial is not disabled in options.
        # Progress locations are sorted for deterministic results.
        if self.options.city_trial_goal.value != self.options.city_trial_goal.option_none:
            # priority locations
            for location_name in sorted(self.city_trial_priority_locations):
                data = CITY_TRIAL_LOCATION_TABLE[location_name]
                region = self.get_region(data.region)
                location = KARLocation(self.player, location_name, region, data)
                location.progress_type = LocationProgressType.PRIORITY
                region.locations.append(location)

            # default locations
            for location_name in self.city_trial_default_locations:
                data = CITY_TRIAL_LOCATION_TABLE[location_name]
                region = self.get_region(data.region)
                location = KARLocation(self.player, location_name, region, data)
                location.progress_type = LocationProgressType.DEFAULT
                region.locations.append(location)

            # excluded locations
            for location_name in self.city_trial_excluded_locations:
                data = CITY_TRIAL_LOCATION_TABLE[location_name]
                region = self.get_region(data.region)
                location = KARLocation(self.player, location_name, region, data)
                location.progress_type = LocationProgressType.EXCLUDED
                region.locations.append(location)

        # Assign Air Ride locations to their region if Air Ride is not disabled in options.
        # Progress locations are sorted for deterministic results.
        if self.options.air_ride_goal.value != self.options.air_ride_goal.option_none:
            # priority locations
            for location_name in sorted(self.air_ride_priority_locations):
                data = AIR_RIDE_LOCATION_TABLE[location_name]
                region = self.get_region(data.region)
                location = KARLocation(self.player, location_name, region, data)
                location.progress_type = LocationProgressType.PRIORITY
                region.locations.append(location)

            # default locations
            for location_name in self.air_ride_default_locations:
                data = AIR_RIDE_LOCATION_TABLE[location_name]
                region = self.get_region(data.region)
                location = KARLocation(self.player, location_name, region, data)
                location.progress_type = LocationProgressType.DEFAULT
                region.locations.append(location)

            # excluded locations
            for location_name in self.air_ride_excluded_locations:
                data = AIR_RIDE_LOCATION_TABLE[location_name]
                region = self.get_region(data.region)
                location = KARLocation(self.player, location_name, region, data)
                location.progress_type = LocationProgressType.EXCLUDED
                region.locations.append(location)

        # place checkbox reward items as locked items on their repective locations if the player option is enabled.
        # these are locked because until checkbox reward randomization is possible in-game, only the player's game can
        # collect these.
        # TODO: better place to put this? generate_early?
        if self.options.checkbox_reward_items:
            if self.options.city_trial_goal.value != self.options.city_trial_goal.option_none:
                for location_name, location_data in CITY_TRIAL_LOCATION_TABLE.items():
                    if location_data.code is not None and location_data.reward != "None":
                        item = self.create_item(location_data.reward)
                        self.get_location(location_name).place_locked_item(item)
            if self.options.city_trial_goal.value != self.options.city_trial_goal.option_none:
                for location_name, location_data in AIR_RIDE_LOCATION_TABLE.items():
                    if location_data.code is not None and location_data.reward != "None":
                        item = self.create_item(location_data.reward)
                        self.get_location(location_name).place_locked_item(item)

        # determine goal for City Trial enabled but Air Ride disabled
        if (
            self.options.city_trial_goal.value != self.options.city_trial_goal.option_none
            and self.options.air_ride_goal.value == self.options.air_ride_goal.option_none
        ):
            if self.options.city_trial_goal.value == self.options.city_trial_goal.option_n_checklist_blocks:
                # can't currently gate anything and the player can always complete all checklist blocks regardless,
                # so just being able to reach the city trial region is enough
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_region(
                    city_trial_region.name, self.player
                )
            else:
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_location(
                    str(self.options.city_trial_goal.value), self.player
                )

        # determine goal for Air Ride enabled but City Trial disabled
        if (
            self.options.air_ride_goal.value != self.options.air_ride_goal.option_none
            and self.options.city_trial_goal.value == self.options.city_trial_goal.option_none
        ):
            if self.options.air_ride_goal.value == self.options.air_ride_goal.option_n_checklist_blocks:
                # can't currently gate anything and the player can always complete all checklist blocks regardless,
                # so just being able to reach the air ride region is enough
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_region(
                    air_ride_region.name, self.player
                )
            else:
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_location(
                    str(self.options.air_ride_goal.value), self.player
                )

        # determine completion condition if both Air Ride and City Trial have goals specified
        if (
            self.options.air_ride_goal.value != self.options.air_ride_goal.option_none
            and self.options.city_trial_goal.value != self.options.city_trial_goal.option_none
        ):
            # both specify N checklist blocks goal
            if (
                self.options.air_ride_goal.value == self.options.air_ride_goal.option_n_checklist_blocks
                and self.options.city_trial_goal.value == self.options.city_trial_goal.option_n_checklist_blocks
            ):
                # can't currently gate anything and the player can always complete all checklist blocks regardless,
                # so just being able to reach the air ride + city trial regions is enough
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_region(
                    air_ride_region.name, self.player
                ) and state.can_reach_region(city_trial_region.name, self.player)
            # city trial specifies N checklist blocks goal but air ride does not
            if (
                self.options.city_trial_goal.value == self.options.city_trial_goal.option_n_checklist_blocks
                and self.options.air_ride_goal.value != self.options.air_ride_goal.option_n_checklist_blocks
            ):
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_region(
                    city_trial_region.name, self.player
                ) and state.can_reach_location(str(self.options.air_ride_goal.value), self.player)
            # air ride specifies N checklist blocks goal but city trial does not
            if (
                self.options.air_ride_goal.value == self.options.air_ride_goal.option_n_checklist_blocks
                and self.options.city_trial_goal.value != self.options.city_trial_goal.option_n_checklist_blocks
            ):
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_region(
                    air_ride_region.name, self.player
                ) and state.can_reach_location(str(self.options.city_trial_goal.value), self.player)

        from Utils import visualize_regions

        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml", show_entrance_names=True)

    def connect_city_trial_region(self, city_trial_region: Region) -> None:
        # free run region
        free_run = Region("City Trial: Free Run", self.player, self.multiworld)
        self.multiworld.regions.append(free_run)
        city_trial_region.connect(free_run)

        # stadium regions
        stadium_destruction_derby_all = Region("Stadium: DESTRUCTION DERBY ALL", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_destruction_derby_all)
        stadium_destruction_derby_1 = Region("Stadium: DESTRUCTION DERBY 1", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_destruction_derby_1)
        stadium_destruction_derby_2 = Region("Stadium: DESTRUCTION DERBY 2", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_destruction_derby_2)
        stadium_destruction_derby_3 = Region("Stadium: DESTRUCTION DERBY 3", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_destruction_derby_3)
        stadium_destruction_derby_4 = Region("Stadium: DESTRUCTION DERBY 4", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_destruction_derby_4)
        stadium_destruction_derby_5 = Region("Stadium: DESTRUCTION DERBY 5", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_destruction_derby_5)

        stadium_drag_race_1 = Region("Stadium: DRAG RACE 1", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_drag_race_1)
        stadium_drag_race_2 = Region("Stadium: DRAG RACE 2", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_drag_race_2)
        stadium_drag_race_3 = Region("Stadium: DRAG RACE 3", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_drag_race_3)
        stadium_drag_race_4 = Region("Stadium: DRAG RACE 4", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_drag_race_4)

        stadium_high_jump = Region("Stadium: HIGH JUMP", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_high_jump)

        stadium_target_flight = Region("Stadium: TARGET FLIGHT", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_target_flight)

        stadium_air_glider = Region("Stadium: AIR GLIDER", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_air_glider)

        stadium_kirby_melee_all = Region("Stadium: KIRBY MELEE ALL", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_kirby_melee_all)
        stadium_kirby_melee_1 = Region("Stadium: KIRBY MELEE 1", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_kirby_melee_1)
        stadium_kirby_melee_2 = Region("Stadium: KIRBY MELEE 2", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_kirby_melee_2)

        stadium_vs_king_dedede = Region("Stadium: VS. KING DEDEDE", self.player, self.multiworld)
        self.multiworld.regions.append(stadium_vs_king_dedede)

        # connect stadium regions
        city_trial_region.connect(stadium_destruction_derby_all)
        stadium_destruction_derby_all.connect(stadium_destruction_derby_1)
        stadium_destruction_derby_all.connect(stadium_destruction_derby_2)
        stadium_destruction_derby_2.connect(
            stadium_destruction_derby_3,
            None,
            lambda state: state.can_reach_location(
                "Stadium: DESTRUCTION DERBY 2 In one game, KO a rival 10 times or more!", self.player
            ),
        )
        stadium_destruction_derby_3.connect(
            stadium_destruction_derby_4,
            None,
            lambda state: state.can_reach_location(
                "Stadium: DESTRUCTION DERBY 3 In one game, KO your rivals 5 or more times!", self.player
            ),
        )
        stadium_destruction_derby_4.connect(
            stadium_destruction_derby_5,
            None,
            lambda state: state.can_reach_location(
                "Stadium: DESTRUCTION DERBY 4 In one game, KO a rival 10 times or more!", self.player
            ),
        )

        city_trial_region.connect(stadium_drag_race_1)
        city_trial_region.connect(stadium_drag_race_2)
        city_trial_region.connect(stadium_drag_race_3)
        stadium_drag_race_3.connect(
            stadium_drag_race_4,
            None,
            lambda state: state.can_reach_location("Stadium: DRAG RACE 3 Finish in less than 00:27:00!", self.player),
        )

        city_trial_region.connect(stadium_high_jump)
        city_trial_region.connect(stadium_target_flight)
        city_trial_region.connect(stadium_air_glider)

        city_trial_region.connect(stadium_kirby_melee_all)
        stadium_kirby_melee_all.connect(stadium_kirby_melee_1)
        stadium_kirby_melee_1.connect(
            stadium_kirby_melee_2,
            None,
            lambda state: state.can_reach_location(
                "Stadium: KIRBY MELEE 1 In one game, KO over 75 enemies by yourself!", self.player
            ),
        )

        city_trial_region.connect(stadium_vs_king_dedede)

    def connect_air_ride_region(self, air_ride_region: Region) -> None:
        # create Air Ride Regions
        time_attack_region = Region("Air Ride: Time Attack", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_region)

        free_run_region = Region("Air Ride: Free Run", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_region)

        air_ride_magma_flows = Region("Air Ride: MAGMA FLOWS", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_magma_flows)
        air_ride_fantasy_meadows = Region("Air Ride: FANTASY MEADOWS", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_fantasy_meadows)
        air_ride_celestial_valley = Region("Air Ride: CELESTIAL VALLEY", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_celestial_valley)
        air_ride_beanstalk_park = Region("Air Ride: BEANSTALK PARK", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_beanstalk_park)
        air_ride_frozen_hillside = Region("Air Ride: FROZEN HILLSIDE", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_frozen_hillside)
        air_ride_machine_passage = Region("Air Ride: MACHINE PASSAGE", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_machine_passage)
        air_ride_sky_sands = Region("Air Ride: SKY SANDS", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_sky_sands)
        air_ride_checker_knights = Region("Air Ride: CHECKER KNIGHTS", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_checker_knights)
        air_ride_nebula_belt = Region("Air Ride: NEBULA BELT", self.player, self.multiworld)
        self.multiworld.regions.append(air_ride_nebula_belt)

        time_attack_magma_flows = Region("Time Attack: MAGMA FLOWS", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_magma_flows)
        time_attack_fantasy_meadows = Region("Time Attack: FANTASY MEADOWS", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_fantasy_meadows)
        time_attack_celestial_valley = Region("Time Attack: CELESTIAL VALLEY", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_celestial_valley)
        time_attack_beanstalk_park = Region("Time Attack: BEANSTALK PARK", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_beanstalk_park)
        time_attack_frozen_hillside = Region("Time Attack: FROZEN HILLSIDE", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_frozen_hillside)
        time_attack_machine_passage = Region("Time Attack: MACHINE PASSAGE", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_machine_passage)
        time_attack_sky_sands = Region("Time Attack: SKY SANDS", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_sky_sands)
        time_attack_checker_knights = Region("Time Attack: CHECKER KNIGHTS", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_checker_knights)
        time_attack_nebula_belt = Region("Time Attack: NEBULA BELT", self.player, self.multiworld)
        self.multiworld.regions.append(time_attack_nebula_belt)

        free_run_magma_flows = Region("Free Run: MAGMA FLOWS", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_magma_flows)
        free_run_fantasy_meadows = Region("Free Run: FANTASY MEADOWS", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_fantasy_meadows)
        free_run_celestial_valley = Region("Free Run: CELESTIAL VALLEY", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_celestial_valley)
        free_run_beanstalk_park = Region("Free Run: BEANSTALK PARK", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_beanstalk_park)
        free_run_frozen_hillside = Region("Free Run: FROZEN HILLSIDE", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_frozen_hillside)
        free_run_machine_passage = Region("Free Run: MACHINE PASSAGE", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_machine_passage)
        free_run_sky_sands = Region("Free Run: SKY SANDS", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_sky_sands)
        free_run_checker_knights = Region("Free Run: CHECKER KNIGHTS", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_checker_knights)
        free_run_nebula_belt = Region("Free Run: NEBULA BELT", self.player, self.multiworld)
        self.multiworld.regions.append(free_run_nebula_belt)

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
            air_ride_nebula_belt, None, lambda state: state.can_reach_location("Race over 100 laps!", self.player)
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
            time_attack_nebula_belt, None, lambda state: state.can_reach_location("Race over 100 laps!", self.player)
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
            free_run_nebula_belt, None, lambda state: state.can_reach_location("Race over 100 laps!", self.player)
        )

    def set_rules(self) -> None:
        """
        Define the logic rules for locations in Kirby Air Ride.
        Rules are only set for locations if they are present in the world.

        :param world: Kirby Air Ride game world.
        """

        def set_rule_if_exists(location_name: str, rule: Callable[[CollectionState], bool]) -> None:
            """
            Set rule on location if it exists in the multiworld.
            """
            try:
                if self.get_location(location_name):
                    set_rule(self.get_location(location_name), rule)
            except KeyError:
                # location was not added to the multuworld due to player options
                pass

        # City Trial Rules
        set_rule_if_exists(
            "Unlock Hydra Parts X, Y, and Z on the Checklist!",
            lambda state: state.can_reach_location(
                "City Trial: Destroy all of the dilapidated houses!", self.player
            )  # X
            and state.can_reach_location(
                "Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", self.player
            )  # Y
            and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", self.player),  # Z
        )

        set_rule_if_exists(
            "Unlock Dragoon Parts A, B, and C on the Checklist!",
            lambda state: state.can_reach_location("Stadium: HIGH JUMP Jump higher than 1,000 feet!", self.player)  # A
            and state.can_reach_location(
                "Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", self.player
            )  # B
            and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", self.player),  # C
        )

        set_rule_if_exists(
            "In one match, complete both Dragoon and Hydra!",
            lambda state: state.can_reach_location("Unlock Hydra Parts X, Y, and Z on the Checklist!", self.player)
            and state.can_reach_location("Unlock Dragoon Parts A, B, and C on the Checklist!", self.player),
        )

        # Air Ride Rules
        set_rule_if_exists(
            "Time Attack: MAGMA FLOWS Finish in under 03:15:00 on Shadow Star!",
            lambda state: state.can_reach_location("Defeat 10 or more enemies using the Quick Spin!", self.player),
        )

        set_rule_if_exists(
            "Time Attack: SKY SANDS Finish in under 02:40:00 on Wagon Star!",
            lambda state: state.can_reach_location(
                "In any mode other than Free Run, reach the goal a total of 3 times!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: FANTASY MEADOWS Do 1 lap under 00:23:00 on Wagon Star!",
            lambda state: state.can_reach_location(
                "In any mode other than Free Run, reach the goal a total of 3 times!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: FROZEN HILLSIDE Do 1 lap under 01:10:00 on Formula Star!",
            lambda state: state.can_reach_location(
                "Time Attack: FROZEN HILLSIDE Finish in under 03:14:00!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: CELESTIAL VALLEY Do 1 lap under 01:02:00 on Slick Star!",
            lambda state: state.can_reach_location(
                "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!", self.player
            ),
        )

        set_rule_if_exists(
            "Time Attack: FANTASY MEADOWS Finish in under 01:05:00 on Slick Star!",
            lambda state: state.can_reach_location(
                "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: MAGMA FLOWS Do 1 lap under 01:02:00 on Turbo Star!",
            lambda state: state.can_reach_location(
                "MAGMA FLOWS: Use all the volcano rails and finish in 1st place!", self.player
            ),
        )

        set_rule_if_exists(
            "Time Attack: FROZEN HILLSIDE Finish in under 03:10:00 on Turbo Star!",
            lambda state: state.can_reach_location(
                "MAGMA FLOWS: Use all the volcano rails and finish in 1st place!", self.player
            ),
        )

        set_rule_if_exists(
            "Time Attack: BEANSTALK PARK Finish in under 03:00:00 on Rocket Star!",
            lambda state: state.can_reach_location(
                "Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: CHECKER KNIGHTS Do 1 lap under 01:25:00 on Rocket Star!",
            lambda state: state.can_reach_location(
                "Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: BEANSTALK PARK Do 1 lap under 00:58:00 on Winged Star!",
            lambda state: state.can_reach_location(
                "Air Ride: Finish in 1st place while flying through the air!", self.player
            ),
        )

        set_rule_if_exists(
            "Time Attack: CELESTIAL VALLEY Finish in under 02:58:00 on Jet Star!",
            lambda state: state.can_reach_location(
                "Air Ride: MACHINE PASSAGE Race over 4,500 feet in 2 minutes!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: SKY SANDS Do 1 lap under 01:05:00 on Bulk Star!",
            lambda state: state.can_reach_location(
                "Time Attack: CELESTIAL VALLEY Finish in under 03:20:00!", self.player
            ),
        )

        set_rule_if_exists(
            "Free Run: MACHINE PASSAGE Do 1 lap under 00:57:00 on Swerve Star!",
            lambda state: state.can_reach_location("Air Ride: SKY SANDS Finish 2 laps in under 02:05:00!", self.player),
        )

    def create_item(self, name: str) -> KARItem:
        """
        Create an item for this world type and player.

        :param name: The name of the item to create.
        :raises KeyError: If an invalid item name is provided.
        """
        if name in ITEM_TABLE:
            return KARItem(
                name,
                self.player,
                ITEM_TABLE[name],
                self.item_classification_overrides.get(name, ITEM_TABLE[name].classification),
            )
        raise KeyError(f"Invalid item name: {name}")

    def create_items(self) -> None:
        pool: list[str] = []
        progression_pool: list[str] = []

        # assign progression, useful, filler and trap items to the pools
        for item_name, item_data in ITEM_TABLE.items():
            classification = self.item_classification_overrides.get(item_name, item_data.classification)

            # don't add checkbox reward items to the pool, they are already placed as locked if the option is enabled
            if item_data.type == "Checkbox Reward":
                continue
            # don't add permanent patches to the pool if the option disables them
            if not self.options.city_trial_permanent_patches and "Permanent" in item_name:
                continue
            # don't add effect items to the pool if they are not enabled
            if not self.options.effect_items_enabled and item_data.type == "Effect":
                continue

            if classification & ItemClassification.progression:
                progression_pool.extend([item_name] * item_data.quantity)
            elif classification & ItemClassification.useful:
                self.useful_pool.add(item_name)
            elif classification & ItemClassification.trap:
                self.trap_pool.add(item_name)
            else:
                self.filler_pool.add(item_name)

        # Determine excluded locations. Add in City Trial or Air Ride excluded locations only if they are enabled,
        # as the locations won't exist in the multiworld if they haven't been enabled.
        excluded_locations = set(self.options.exclude_locations)
        if self.options.city_trial_goal.value != self.options.city_trial_goal.option_none:
            excluded_locations |= self.city_trial_excluded_locations
        if self.options.air_ride_goal.value != self.options.air_ride_goal.option_none:
            excluded_locations |= self.air_ride_excluded_locations

        nonexcluded_locations = [
            location
            for location in self.get_locations()
            if location.name not in excluded_locations and not location.locked
        ]

        # Add filler items to place into excluded locations.
        pool.extend([self.get_filler_item_name() for _ in excluded_locations])

        # The remaining number of items left to place should be the same as the number of non-excluded
        # locations in the world.
        num_items_left_to_place = len(nonexcluded_locations)

        # All progression items are added to the item pool.
        if len(progression_pool) > num_items_left_to_place:
            raise FillError(
                "There are insufficient locations to place progression items! "
                f"Trying to place {len(progression_pool)} items in only {num_items_left_to_place} locations."
            )
        # Add progression items into the pool
        pool.extend(progression_pool)
        num_items_left_to_place -= len(progression_pool)

        # place useful items to fill out the remaining locations
        pool.extend(self.random.choices(list(self.useful_pool), k=num_items_left_to_place))

        # Create the pool of the remaining shuffled items.
        items = [self.create_item(item) for item in pool]
        self.random.shuffle(items)

        self.multiworld.itempool += items

    def get_filler_item_name(self) -> str:
        """
        This method is called when the item pool needs to be filled with additional items to match the location count.

        :return: The name of a filler item from this world.
        """
        if self.options.traps_enabled and self.options.trap_chance.value > 0:
            if self.random.random() * 100 < self.options.trap_chance.value:
                return self.random.choices(list(self.trap_pool), k=1)[0]

        return self.random.choices(list(self.filler_pool), k=1)[0]

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Return the `slot_data` field that will be in the `Connected` network package.

        This is a way the generator can give custom data to the client.
        The client will receive this as JSON in the `Connected` response.

        :return: A dictionary to be sent to the client when it connects to the server.
        """
        slot_data = self.options.get_output_dict()

        return slot_data
