from collections.abc import Mapping
from typing import Any, ClassVar

from BaseClasses import ItemClassification, Tutorial
from Fill import FillError
from Options import OptionError

from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import (
    Component,
    Type,
    components,
    icon_paths,
    launch_subprocess,
)

from .KARData import CheckboxFillerType, PatchConstants, ProgressiveStadiumUnlockType
from .KARItems import ITEM_TABLE, KARItem, KARItemData, KARItemType, item_name_groups
from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    location_name_groups,
)
from .KAROptions import AirRideGoal, CityTrialGoal, KAROptions, TopRideGoal, kar_option_groups
from .KARRegions import create_regions
from .KARRules import set_rules


def run_client() -> None:
    """
    Launch Kirby Air Ride client.
    """
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

    tutorials = [  # noqa: RUF012
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Kirby Air Ride Archipelago on your computer.",
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
    topology_present: bool = True
    explicit_indirect_conditions = False

    item_name_to_id: ClassVar[dict[str, int]] = {
        item_name: item_data.code for item_name, item_data in ITEM_TABLE.items() if item_data.code is not None
    }
    location_name_to_id: ClassVar[dict[str, int]] = {
        location_name: location_data.code
        for location_name, location_data in (
            CITY_TRIAL_LOCATION_TABLE | AIR_RIDE_LOCATION_TABLE | TOP_RIDE_LOCATION_TABLE
        ).items()
        if location_data.code is not None
    }

    item_name_groups: ClassVar[dict[str, set[str]]] = item_name_groups
    location_name_groups: ClassVar[dict[str, set[str]]] = location_name_groups

    web: ClassVar[KARWeb] = KARWeb()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.city_trial_enabled: bool = False
        self.city_trial_priority_locations: set[str] = set()
        self.city_trial_default_locations: set[str] = set()
        self.city_trial_excluded_locations: set[str] = set()
        self.air_ride_enabled: bool = False
        self.air_ride_priority_locations: set[str] = set()
        self.air_ride_default_locations: set[str] = set()
        self.air_ride_excluded_locations: set[str] = set()
        self.top_ride_enabled: bool = False
        self.top_ride_priority_locations: set[str] = set()
        self.top_ride_default_locations: set[str] = set()
        self.top_ride_excluded_locations: set[str] = set()
        self.item_classification_overrides: dict[str, ItemClassification] = {}
        self.useful_pool: set[str] = set()
        self.filler_pool: set[str] = set()
        self.trap_pool: set[str] = set()
        self.progression_pool: list = []
        self.city_trial_random_stadium_choice: ProgressiveStadiumUnlockType | None = None

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

        # if checkbox fillers are not progression, override as useful
        if not self.options.checkbox_fillers_progression:
            override_as_useful.extend(
                [
                    item_name
                    for item_name, item_data in ITEM_TABLE.items()
                    if item_data.type == KARItemType.CHECKBOX_FILLER.value
                ]
            )

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
            elif not self.options.city_trial_progression_rng and location in location_name_groups["City Trial: RNG"]:
                self.city_trial_excluded_locations.add(location)
            elif (
                not self.options.city_trial_progression_bust_vehicles
                and location in location_name_groups["City Trial: Bust Vehicle on Vehicle"]
            ):
                self.city_trial_excluded_locations.add(location)
            else:
                self.city_trial_default_locations.add(location)

        assert self.city_trial_default_locations.isdisjoint(self.city_trial_excluded_locations), (
            "City Trial default and excluded locations must not overlap"
        )

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

        assert self.air_ride_default_locations.isdisjoint(self.air_ride_excluded_locations), (
            "Air Ride default and excluded locations must not overlap"
        )

        # categorzie Top Ride locations progress type based on player options choices
        # currently, we do not have any options that prioritize locations other than the core options,
        # so priority_locations is not used.
        for location in TOP_RIDE_LOCATION_TABLE:
            if (
                not self.options.top_ride_progression_high_effort
                and location in location_name_groups["Top Ride: High Effort"]
            ):
                self.top_ride_excluded_locations.add(location)
            elif (
                not self.options.top_ride_progression_free_run
                and location in location_name_groups["Top Ride: Free Run"]
            ):
                self.top_ride_excluded_locations.add(location)
            elif (
                not self.options.top_ride_progression_time_attack
                and location in location_name_groups["Top Ride: Time Attack"]
            ):
                self.top_ride_excluded_locations.add(location)
            elif (
                not self.options.top_ride_progression_multiplayer
                and location in location_name_groups["Top Ride: Multiplayer"]
            ):
                self.top_ride_excluded_locations.add(location)
            else:
                self.top_ride_default_locations.add(location)

        assert self.top_ride_default_locations.isdisjoint(self.top_ride_excluded_locations), (
            "Top Ride default and excluded locations must not overlap"
        )

    def _determine_city_trial_random_stadium(self) -> None:
        """
        Choose an initial random stadium for the player to receive if there is not one already specified by the player.
        """
        player_stadium_unlocks = [
            item_name
            for item_name in self.options.start_inventory
            if item_name in (stadium.value for stadium in ProgressiveStadiumUnlockType)
        ]
        if player_stadium_unlocks:
            # Player specified king dedede stadium to exist, but that's also the goal
            if self.options.city_trial_goal.value == self.options.city_trial_goal.option_beat_king_dedede:
                if ProgressiveStadiumUnlockType.STADIUM_VS_KING_DEDEDE.value in player_stadium_unlocks:
                    raise OptionError(
                        f"Cannot have {ProgressiveStadiumUnlockType.STADIUM_VS_KING_DEDEDE.value} \
                            in starting inventory if the goal is {self.options.city_trial_goal.option_beat_king_dedede}"
                    )
            # don't need to generate a starting stadium unlock if the player has specified one in the starting inventory
            self.city_trial_random_stadium_choice = None
            return

        stadiums = list(ProgressiveStadiumUnlockType)
        if self.options.city_trial_goal.value == self.options.city_trial_goal.option_beat_king_dedede:
            stadiums.remove(ProgressiveStadiumUnlockType.STADIUM_VS_KING_DEDEDE)
        self.city_trial_random_stadium_choice = self.random.choice(stadiums)

    def _populate_item_pools(self) -> None:
        """
        Populate progression, useful, filler, and trap item pools based on player options.

        Must run after _determine_item_classification_overrides() to respect any
        classification changes from player settings.
        """
        # assign progression, useful, filler and trap items to the pools
        for item_name, item_data in ITEM_TABLE.items():
            classification = self.item_classification_overrides.get(item_name, item_data.classification)

            # don't add event items to the pool - they are only placed on event locations
            if item_data.code is None:
                continue

            # don't add permanent patches to the pool if they are not enabled or City Trial is disabled
            if (
                not self.city_trial_enabled or not self.options.city_trial_permanent_patches
            ) and "Permanent" in item_name:
                continue
            # don't add effect items to the pool if they are not enabled
            if not self.options.effect_items_enabled and item_data.type == KARItemType.EFFECT.value:
                continue
            # don't add city trial checkbox fillers to the pool if they are not enabled or City Trial is disabled
            if item_name == CheckboxFillerType.CITY_TRIAL_CHECKBOX_FILLER.value and (
                not self.city_trial_enabled or not self.options.city_trial_checkbox_fillers
            ):
                continue
            # don't add air ride checkbox fillers to the pool if they are not enabled or Air Ride is disabled
            if item_name == CheckboxFillerType.AIR_RIDE_CHECKBOX_FILLER.value and (
                not self.air_ride_enabled or not self.options.air_ride_checkbox_fillers
            ):
                continue
            # don't add top ride checkbox fillers to the pool if they are not enabled or Top Ride is disabled
            if item_name == CheckboxFillerType.TOP_RIDE_CHECKBOX_FILLER.value and (
                not self.top_ride_enabled or not self.options.top_ride_checkbox_fillers
            ):
                continue
            # don't add patch cap increase items to the pool if they are not enabled or City Trial is disabled
            if item_data.type == KARItemType.PATCH_CAP_INCREASE.value and (
                not self.city_trial_enabled or not self.options.city_trial_progressive_patch_caps
            ):
                continue
            # don't add progressive stadium items to the pool if they are not enabled or City Trial is disabled
            if item_data.type == KARItemType.PROGRESSIVE_STADIUM.value and (
                not self.city_trial_enabled or not self.options.city_trial_progressive_stadiums
            ):
                continue
            # don't add stadium unlocks if they are in the starting inventory or the randomly chosen precollected
            # stadium
            if (
                self.city_trial_enabled
                and self.options.city_trial_progressive_stadiums
                and item_data.type == KARItemType.PROGRESSIVE_STADIUM.value
            ):
                if item_name in self.options.start_inventory or (
                    self.city_trial_random_stadium_choice is not None
                    and item_name == self.city_trial_random_stadium_choice.value
                ):
                    continue

            if classification & ItemClassification.progression:
                # take care of checkbox filler items first, as they have quantity specified by the player
                if item_data.type == KARItemType.CHECKBOX_FILLER.value:
                    match item_name:
                        case CheckboxFillerType.CITY_TRIAL_CHECKBOX_FILLER.value:
                            if self.city_trial_enabled:
                                self.progression_pool.extend(
                                    [item_name] * self.options.city_trial_checkbox_fillers_amount.value
                                )
                        case CheckboxFillerType.AIR_RIDE_CHECKBOX_FILLER.value:
                            if self.air_ride_enabled:
                                self.progression_pool.extend(
                                    [item_name] * self.options.air_ride_checkbox_fillers_amount.value
                                )
                        case CheckboxFillerType.TOP_RIDE_CHECKBOX_FILLER.value:
                            if self.top_ride_enabled:
                                self.progression_pool.extend(
                                    [item_name] * self.options.top_ride_checkbox_fillers_amount.value
                                )
                    continue

                # cap increase items need to make as many as is required to get to the max stat count
                # (18 for most patches, 16 for HP)
                # assumes the range of patch_cap_amount is 1-17.
                if item_data.type == KARItemType.PATCH_CAP_INCREASE.value:
                    num_needed = max(1, PatchConstants.MAX_PATCH_CAP - self.options.city_trial_patch_cap_amount.value)
                    self.progression_pool.extend([item_name] * num_needed)
                    continue

                self.progression_pool.extend([item_name] * item_data.quantity)
            elif classification & ItemClassification.useful:
                # add checkbox fillers only if the modes for them are enabled
                if item_data.type == KARItemType.CHECKBOX_FILLER.value:
                    match item_name:
                        case CheckboxFillerType.CITY_TRIAL_CHECKBOX_FILLER.value:
                            if self.city_trial_enabled:
                                self.useful_pool.add(item_name)
                        case CheckboxFillerType.AIR_RIDE_CHECKBOX_FILLER.value:
                            if self.air_ride_enabled:
                                self.useful_pool.add(item_name)
                        case CheckboxFillerType.TOP_RIDE_CHECKBOX_FILLER.value:
                            if self.top_ride_enabled:
                                self.useful_pool.add(item_name)
                    continue

                self.useful_pool.add(item_name)
            elif classification & ItemClassification.trap:
                self.trap_pool.add(item_name)
            else:
                self.filler_pool.add(item_name)

    def generate_early(self) -> None:
        """
        Run before any general steps of the MultiWorld other than options. Useful for getting and adjusting option
        results and determining layouts for entrance rando etc. start inventory gets pushed after this step.
        """
        self.city_trial_enabled = self.options.city_trial_goal.value != CityTrialGoal.option_none
        self.air_ride_enabled = self.options.air_ride_goal.value != AirRideGoal.option_none
        self.top_ride_enabled = self.options.top_ride_goal.value != TopRideGoal.option_none

        if not any((self.city_trial_enabled, self.air_ride_enabled, self.top_ride_enabled)):
            raise OptionError("No modes enabled. You need to have at least one goal in a mode!")

        # Determine locations progress types from player options.
        self._determine_locations_progress_type()

        # Determine any item classification overrides from player options.
        self._determine_item_classification_overrides()

        # Populate item pools for create_items, based on user options. must run after
        # _determine_item_classification_overrides
        self._populate_item_pools()

        # if city trial progressive stadiums are enabled, choose and precollect the initial stadium unlock
        if self.city_trial_enabled and self.options.city_trial_progressive_stadiums:
            self._determine_city_trial_random_stadium()
            if self.city_trial_random_stadium_choice is not None:
                item = self.create_item(self.city_trial_random_stadium_choice.value)
                self.push_precollected(item)

        # raise an error if the number of checkbox fillers the player specified for a mode is greater than or equal
        # to the number of checklist blocks required for the goal
        if (
            self.city_trial_enabled
            and self.options.city_trial_goal.current_key == self.options.city_trial_goal.option_n_checklist_blocks
        ):
            if self.options.city_trial_checkbox_fillers_amount.value >= self.options.city_trial_checklist_amount.value:
                raise OptionError(
                    f"Cannot start with {self.options.city_trial_checkbox_fillers_amount.value} \
                        City Trial checkbox fillers with {self.options.city_trial_checklist_amount.value} \
                            checklist blocks as a goal. Checkbox filler number must be less than goal amount."
                )
        if (
            self.air_ride_enabled
            and self.options.air_ride_goal.current_key == self.options.air_ride_goal.option_n_checklist_blocks
        ):
            if self.options.air_ride_checkbox_fillers_amount.value >= self.options.air_ride_checklist_amount.value:
                raise OptionError(
                    f"Cannot start with {self.options.air_ride_checkbox_fillers_amount.value} \
                        Air Ride checkbox fillers with {self.options.air_ride_checklist_amount.value} \
                            checklist blocks as a goal. Checkbox filler number must be less than goal amount."
                )
        if (
            self.top_ride_enabled
            and self.options.top_ride_goal.current_key == self.options.top_ride_goal.option_n_checklist_blocks
        ):
            if self.options.top_ride_checkbox_fillers_amount.value >= self.options.top_ride_checklist_amount.value:
                raise OptionError(
                    f"Cannot start with {self.options.top_ride_checkbox_fillers_amount.value} \
                        Top Ride checkbox fillers with {self.options.top_ride_checklist_amount.value} \
                            checklist blocks as a goal. Checkbox filler number must be less than goal amount."
                )

    def create_regions(self) -> None:
        """Method for creating and connecting regions for the World."""
        create_regions(self)

    def set_rules(self) -> None:
        """Method for setting the rules on the World's regions and locations."""
        set_rules(self)

    def create_item(self, name: str) -> KARItem:
        """
        Create a KARItem from the given item_name.
        """
        # Check both item_names (for regular items) and ITEM_TABLE (for event items with code=None)
        if name in self.item_names or name in ITEM_TABLE:
            data = ITEM_TABLE[name]
            new_item_data = KARItemData(
                data.type,
                self.item_classification_overrides.get(name, data.classification),
                data.code,
                data.quantity,
            )
            return KARItem(
                name,
                self.player,
                new_item_data,
            )
        raise KeyError(f"Invalid item name: {name}")

    def create_items(self) -> None:
        pool: list[str] = []

        # Determine excluded locations. Add in excluded locations only if the respective game modes are
        # enabled, as the locations won't exist in the multiworld if they haven't been enabled.
        excluded_locations = set(self.options.exclude_locations)
        if self.city_trial_enabled:
            excluded_locations |= self.city_trial_excluded_locations
        if self.air_ride_enabled:
            excluded_locations |= self.air_ride_excluded_locations
        if self.top_ride_enabled:
            excluded_locations |= self.top_ride_excluded_locations

        # Determine which locations are goal locations (these were excluded from region creation)
        # Goal locations don't exist as real locations, so we shouldn't create items for them
        goal_locations_to_exclude: set[str] = set()

        if self.city_trial_enabled and self.options.city_trial_goal.current_key not in [
            self.options.city_trial_goal.option_none,
            self.options.city_trial_goal.option_n_checklist_blocks,
        ]:
            goal_locations_to_exclude.add(self.options.city_trial_goal.current_key)

        if self.air_ride_enabled and self.options.air_ride_goal.current_key not in [
            self.options.air_ride_goal.option_none,
            self.options.air_ride_goal.option_n_checklist_blocks,
        ]:
            goal_locations_to_exclude.add(self.options.air_ride_goal.current_key)

        if self.top_ride_enabled and self.options.top_ride_goal.current_key not in [
            self.options.top_ride_goal.option_none,
            self.options.top_ride_goal.option_n_checklist_blocks,
        ]:
            goal_locations_to_exclude.add(self.options.top_ride_goal.current_key)

        # Remove goal locations from excluded_locations since they don't actually exist as real locations
        excluded_locations -= goal_locations_to_exclude

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
        if len(self.progression_pool) > num_items_left_to_place:
            raise FillError(
                "There are insufficient locations to place progression items! "
                f"Trying to place {len(self.progression_pool)} items in only {num_items_left_to_place} locations."
            )

        # Add progression items into the pool
        pool.extend(self.progression_pool)
        num_items_left_to_place -= len(self.progression_pool)

        # place useful items to fill out the remaining locations
        pool.extend(self.random.choices(list(self.useful_pool), k=num_items_left_to_place))

        # Create the pool of the remaining shuffled items.
        items = [self.create_item(item_name) for item_name in pool]
        self.random.shuffle(items)

        # Final validation that pool matches location count
        # Pool contains items for both excluded and nonexcluded locations
        total_location_count = len(excluded_locations) + len(nonexcluded_locations)
        if len(items) != total_location_count:
            raise FillError(
                f"Item pool size ({len(items)}) does not match total location count "
                f"({total_location_count}). Excluded: {len(excluded_locations)}, "
                f"Nonexcluded: {len(nonexcluded_locations)}. This indicates a logic error in item pool generation."
            )

        self.multiworld.itempool += items

    def get_filler_item_name(self) -> str:
        """
        This method is called when the item pool needs to be filled with additional items to match the location count.

        :return: The name of a filler item from this world.
        """

        # check if filler_pool has been populated. if not, we are in the instance that this world is a part of ItemLink
        # generation instead of regular generation. no other generation steps have happened yet.
        # filler_pool will be populated in every other case
        if not self.filler_pool:
            filler_pool = set()
            for item_name, item_data in ITEM_TABLE.items():
                # check specifically for 0 value
                if item_data.classification == ItemClassification.filler:
                    filler_pool.add(item_name)
            return self.random.choices(list(filler_pool), k=1)[0]

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
        return self.options.get_output_dict()
