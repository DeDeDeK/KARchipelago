from collections.abc import Mapping
from typing import Any, Callable, ClassVar, Dict, Set

from BaseClasses import CollectionState, ItemClassification, Region, Tutorial
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
from .Locations import CITY_TRIAL_LOCATION_TABLE, KARLocation, location_name_groups


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
        for location_name, location_data in CITY_TRIAL_LOCATION_TABLE.items()
        if location_data.code is not None
    }

    item_name_groups: ClassVar[Dict[str, Set[str]]] = item_name_groups
    location_name_groups: ClassVar[Dict[str, Set[str]]] = location_name_groups

    web: ClassVar[KARWeb] = KARWeb()

    origin_region_name: str = "City Trial"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.progress_locations: set[str] = set()
        self.nonprogress_locations: set[str] = set()
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
        if self.options.permanent_patches and not self.options.permanent_patch_progression:
            override_as_useful.extend([item_name for item_name in ITEM_TABLE.keys() if "Permanent" in item_name])

        for item_name in override_as_useful:
            self.item_classification_overrides[item_name] = ItemClassification.useful

    def _determine_progress_and_nonprogress_locations(
        self,
    ) -> tuple[set[str], set[str]]:
        """
        Determine which locations are progress and nonprogress in the world based on the player's options.

        :return: A tuple of two sets, the first containing the names of the progress locations and the second containing
        the names of the nonprogress locations.
        """

        progress_locations: set[str] = set()
        nonprogress_locations: set[str] = set()

        # set some locations as options based on player options choices
        for location, data in CITY_TRIAL_LOCATION_TABLE.items():
            if not self.options.progression_high_effort and location in [
                "City Trial: break more than 500 boxes!",
                "City Trial: break more than 1000 boxes!",
                "City Trial: pick up a total of over 1000 items!",
                "City Trial: Pick up a total of over 3000 items!",
                "Free Run: Drive for a total of 2 hours or more!",
                "Free Run: Drive for a total of 30 minutes or more!",
                "Free Run: Drive for a total of 10 minutes or more!",
                "In one match, complete both Dragoon and Hydra!",
            ]:
                nonprogress_locations.add(location)
            elif not self.options.progression_multiplayer and location in [
                "City Trial: Let time run out while all players are on the rails!",
                "City Trial: Have all players simultaneously get off of their machines!",
                "City Trial: Let time run out while all players are off of their machines!",
            ]:
                nonprogress_locations.add(location)
            elif not self.options.free_run_progression and location in [
                "Free Run: Drive for a total of 2 hours or more!",
                "Free Run: Drive for a total of 30 minutes or more!",
                "Free Run: Drive for a total of 10 minutes or more!",
                "Free Run: Change Air Ride Machines 10 times or more!",
            ]:
                nonprogress_locations.add(location)
            else:
                progress_locations.add(location)

        assert progress_locations.isdisjoint(nonprogress_locations)

        return progress_locations, nonprogress_locations

    def generate_early(self) -> None:
        """
        Run before any general steps of the MultiWorld other than options.
        """

        # Determine which locations are progression and which are not from options.
        self.progress_locations, self.nonprogress_locations = self._determine_progress_and_nonprogress_locations()

        # Determine any item classification overrides based on user options.
        self._determine_item_classification_overrides()

    def create_regions(self) -> None:
        """
        Create and connect regions for the Kirby Air Ride world.

        """
        # TODO: player will eventually be able to choose any/all of the 3 locations: City Trial, Air Ride, Top Ride
        # That will appear in self.options and need to be handled here.

        # "City Trial" region contains all locations that are a part of City Trial
        city_trial_region = Region("City Trial", self.player, self.multiworld)
        self.multiworld.regions.append(city_trial_region)

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
            lambda state: state.can_reach_location("Stadium: DESTRUCTION DERBY 2 In one game, KO a rival 10 times or more!", self.player),
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
            lambda state: state.can_reach_location("Stadium: DESTRUCTION DERBY 4 In one game, KO a rival 10 times or more!", self.player),
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
            lambda state: state.can_reach_location("Stadium: KIRBY MELEE 1 In one game, KO over 75 enemies by yourself!", self.player),
        )

        city_trial_region.connect(stadium_vs_king_dedede)

        # Assign progress locations to their region
        # Progress locations are sorted for deterministic results.
        for location_name in sorted(self.progress_locations):
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = self.get_region(data.region)
            location = KARLocation(self.player, location_name, region, data)
            region.locations.append(location)

        # Assign non-progress locations to their region
        for location_name in self.nonprogress_locations:
            data = CITY_TRIAL_LOCATION_TABLE[location_name]
            region = self.get_region(data.region)
            location = KARLocation(self.player, location_name, region, data)
            region.locations.append(location)

        # set completion condition to being able to reach the goal location. This is for GENERATION ONLY.
        if self.options.goal.value == "Fill in N Checklist Boxes!":
            # if city trial region has enough locations, that will suffice for this goal
            if len(city_trial_region.locations) >= self.options.checklist_amount.value:
                self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_region(
                    city_trial_region.name, self.player
                )
        else:
            self.multiworld.completion_condition[self.player] = lambda state: state.can_reach_location(
                str(self.options.goal.value), self.player
            )

        # place checkbox reward items as locked items on their repective locations if the player option is enabled.
        # these are locked because until checkbox reward randomization is possible in-game, only the player's game can
        # collect these.
        if self.options.checkbox_reward_items:
            for location_name, location_data in CITY_TRIAL_LOCATION_TABLE.items():
                if location_data.code is not None and location_data.reward != "None":
                    item = self.create_item(location_data.reward)
                    self.get_location(location_name).place_locked_item(item)

    def set_rules(self) -> None:
        """
        Define the logic rules for locations in Kirby Air Ride.
        Rules are only set for locations if they are present in the world.

        :param world: Kirby Air Ride game world.
        """

        # set an access rule on the location if it is a progression location
        def set_rule_if_exists(location_name: str, rule: Callable[[CollectionState], bool]) -> None:
            if location_name in self.progress_locations:
                set_rule(self.get_location(location_name), rule)

        # checks relating to dragoon and hydra
        set_rule_if_exists(
            "Unlock Hydra Parts X, Y, and Z on the Checklist!",
            lambda state: state.can_reach_location("City Trial: Destroy all of the dilapidated houses!", self.player)  # X
            and state.can_reach_location("Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", self.player)  # Y
            and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", self.player),  # Z
        )

        set_rule_if_exists(
            "Unlock Dragoon Parts A, B, and C on the Checklist!",
            lambda state: state.can_reach_location("Stadium: HIGH JUMP Jump higher than 1,000 feet!", self.player)  # A
            and state.can_reach_location("Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", self.player)  # B
            and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", self.player),  # C
        )

        set_rule_if_exists(
            "In one match, complete both Dragoon and Hydra!",
            lambda state: state.can_reach_location("Unlock Hydra Parts X, Y, and Z on the Checklist!", self.player)
            and state.can_reach_location("Unlock Dragoon Parts A, B, and C on the Checklist!", self.player),
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

        # assign progression, useful, and filler items to the pools
        for item_name, item_data in ITEM_TABLE.items():
            classification = self.item_classification_overrides.get(item_name, item_data.classification)

            # don't add checkbox reward items to the pool, they are already placed as locked if the option is enabled
            if item_data.type == "Checkbox Reward":
                continue
            # don't add permanent patches to the pool if the option disables them
            if not self.options.permanent_patches and "Permanent" in item_name:
                continue

            if classification == ItemClassification.progression:
                progression_pool.extend([item_name] * item_data.quantity)
            elif classification == ItemClassification.useful:
                self.useful_pool.add(item_name)
            elif classification == ItemClassification.trap:
                self.trap_pool.add(item_name)
            elif classification == ItemClassification.filler:
                self.filler_pool.add(item_name)

        # Add filler items to place into excluded locations.
        pool.extend([self.get_filler_item_name() for _ in self.options.exclude_locations])

        # The remaining of items left to place should be the same as the number of non-excluded locations in the world.
        nonexcluded_locations = [
            location for location in self.get_locations() if location.name not in self.options.exclude_locations and not location.locked
        ]
        num_items_left_to_place = len(nonexcluded_locations)

        # All progression items are added to the item pool.
        if len(progression_pool) > num_items_left_to_place:
            raise FillError(
                "There are insufficient locations to place progression items! "
                f"Trying to place {len(progression_pool)} items in only {num_items_left_to_place} locations."
            )
        pool.extend(progression_pool)
        num_items_left_to_place -= len(progression_pool)

        # place filler items to fill out remaining locations
        pool.extend([self.get_filler_item_name() for _ in range(num_items_left_to_place)])

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

        return self.random.choices(list(self.filler_pool | self.useful_pool), k=1)[0]

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Return the `slot_data` field that will be in the `Connected` network package.

        This is a way the generator can give custom data to the client.
        The client will receive this as JSON in the `Connected` response.

        :return: A dictionary to be sent to the client when it connects to the server.
        """
        slot_data = self.options.get_output_dict()

        return slot_data
