import asyncio
import json
import random
import time
import traceback
from typing import Any

import Utils
from CommonClient import (
    ClientCommandProcessor,
    CommonContext,
    get_base_parser,
    gui_enabled,
    logger,
    server_loop,
)
from NetUtils import ClientStatus, NetworkItem

from .DolphinInterface import DolphinInterface
from .KARData import (
    CheckboxFillerType,
    CheckboxFlags,
    PatchType,
    StageName,
    StatType,
    get_checkbox_filler_type_from_item_name,
    get_effect_type_from_item_name,
    get_patch_cap_increase_type_from_item_name,
    get_patch_type_from_item_name,
    get_progressive_stadium_unlock_type_from_item_name,
    get_stage_name_from_stadium_unlock_type,
    patch_type_to_stat_type,
)
from .KARItems import ITEM_TABLE, KARItemType
from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    KARLocationData,
    KARLocationType,
)
from .KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal


class KARCommandProcessor(ClientCommandProcessor):
    """
    Command Processor for Kirby Air Ride client commands.

    This class handles commands specific to Kirby Air Ride.
    """

    def __init__(self, ctx: CommonContext) -> None:
        """
        Initialize the command processor with the provided context.

        Args:
            ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_dolphin(self) -> None:
        """Display the current Dolphin emulator connection status."""
        if isinstance(self.ctx, KARContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")

    def _cmd_deathlink(self) -> None:
        """Toggle DeathLink."""
        if isinstance(self.ctx, KARContext):
            if "DeathLink" in self.ctx.tags:
                Utils.async_start(self.ctx.update_death_link(False))
                logger.info("Deathlink disabled.")
            else:
                Utils.async_start(self.ctx.update_death_link(True))
                logger.info("Deathlink enabled.")

    def _cmd_energylink(self) -> None:
        """Toggle EnergyLink features."""
        if isinstance(self.ctx, KARContext):
            if self.ctx.energy_link_enabled:
                self.ctx.energy_link_enabled = False
                self.ctx.stored_data_notification_keys.remove(f"EnergyLink{self.ctx.team}")
                logger.info("EnergyLink disabled.")
            else:
                self.ctx.energy_link_enabled = True
                self.ctx.set_notify(f"EnergyLink{self.ctx.team}")
                if self.ctx.ui:
                    self.ctx.ui.enable_energy_link()
                logger.info("EnergyLink enabled.")

    def _cmd_energylink_spend(self, item_name: str, amount: str) -> None:
        """Spend energy from EnergyLink on patches or other items. Specify items like: \
            /energylink_spend "Top Speed Up" 1"""
        if isinstance(self.ctx, KARContext):
            if self.ctx.energy_link_enabled:
                Utils.async_start(self.ctx.energy_link_spend(item_name, amount))
            else:
                logger.info("You must enable energylink first with /energylink.")

    def _cmd_patch_cap(self) -> None:
        """See what the current value of the patch cap is."""
        if isinstance(self.ctx, KARContext):
            if self.ctx.city_trial_patch_cap_enabled:
                logger.info(f"Patch cap: {self.ctx.city_trial_patch_cap_amount}")
            else:
                logger.info("Patch caps were not enabled for this run.")


class KARContext(CommonContext):
    """
    The context for Kirby Air Ride client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Kirby Air Ride.
    """

    game: str = "Kirby Air Ride"
    items_handling = 0b111  # receive items from the server for starting inventory, our own world, and other worlds
    want_slot_data = True  # need slot data for player options specified at generation
    command_processor = KARCommandProcessor

    def __init__(self, server_address: str | None, password: str | None) -> None:
        """
        Initialize the KAR context.

        Args:
            server_address: Address of the Archipelago server.
            password: Password for server authentication.
        """
        super().__init__(server_address, password)
        self.connection_refused_game_status = (
            "Dolphin failed to connect. Please make sure your emulator is running and \
            load an ISO for Kirby Air Ride. Trying again in 5 seconds..."
        )
        self.connection_connected_game_status = "Dolphin connected successfully."
        self.connection_initial_status = "Dolphin connection has not been initiated."
        self.dolphin_interface = DolphinInterface()
        self.dolphin_sync_task: asyncio.Task[None] | None = None
        self.dolphin_status: str = self.connection_initial_status
        self.dolphin_reconnect_delay: int = 5
        self.city_trial_enabled: bool = False
        self.city_trial_goal: str = ""
        self.city_trial_goal_checklist_amount: int = 0
        self.city_trial_goal_achieved: bool = False
        self.city_trial_num_locations_checked: int = 0
        self.city_trial_patch_cap_enabled: bool = False
        self.city_trial_patch_cap_amount: int = 0
        self.city_trial_progressive_stadiums_enabled: bool = False
        self.city_trial_checklist_locations: list[KARLocationData] = [
            location_data
            for location_data in CITY_TRIAL_LOCATION_TABLE.values()
            if location_data.type == KARLocationType.CHECKLISTBOX
        ]
        self.air_ride_enabled: bool = False
        self.air_ride_goal: str = ""
        self.air_ride_goal_checklist_amount: int = 0
        self.air_ride_goal_achieved: bool = False
        self.air_ride_num_locations_checked: int = 0
        self.air_ride_checklist_locations: list[KARLocationData] = [
            location_data
            for location_data in AIR_RIDE_LOCATION_TABLE.values()
            if location_data.type == KARLocationType.CHECKLISTBOX
        ]
        self.top_ride_enabled: bool = False
        self.top_ride_goal: str = ""
        self.top_ride_goal_checklist_amount: int = 0
        self.top_ride_goal_achieved: bool = False
        self.top_ride_num_locations_checked: int = 0
        self.top_ride_checklist_locations: list[KARLocationData] = [
            location_data
            for location_data in TOP_RIDE_LOCATION_TABLE.values()
            if location_data.type == KARLocationType.CHECKLISTBOX
        ]
        self.enabled_modes: tuple[str, ...] = ()
        self.items_queue: list[NetworkItem] = []
        self.energy_link_enabled: bool = False
        self.energy_link_items_queue: list[int] = []
        self.energy_link_base_item_cost: int = 10
        self.death_link_enabled: bool = False
        self.death_link_cooldown: int = 120
        self.reveal_checklists: bool = False
        self.item_processed_index: int = 0
        self.purchased_permanent_patches: dict[str, int] = {}
        self.items_file_path: str = Utils.user_path("kirby_air_ride_items.json")
        self.excluded_checkbox_bytes: tuple[int, ...] = (0x00, 0x01, 0x10, 0x11)

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        Args:
            allow_autoreconnect: Allow the client to auto-reconnect to the server.
        """
        self.auth = None
        await super().disconnect(allow_autoreconnect)

    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.

        Args:
            password_requested: Whether the server requires a password.
        """
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def process_items_file(self, data: dict) -> None:
        """
        Process the data from the items file and set class variables accordingly.
        """
        logger.debug("Processing items file...")

        # process items_processed_index
        item_index = data.get("item_processed_index", 0)
        if item_index in range(0, 99999):
            logger.debug(
                f"read file for item_processed_index value: {item_index}, setting item_processed_index to {item_index}"
            )
            self.item_processed_index = item_index
        else:
            # invalid value, assume 0
            logger.debug("read an invalid value for item_processed_index: setting item_processed_index to default 0")
            self.item_processed_index = 0

        # process permanent patches
        purchased_permanent_patches: dict = data.get("purchased_permanent_patches", {})
        if purchased_permanent_patches:
            logger.debug(f"setting permanent patches from items file: {purchased_permanent_patches}")
        self.purchased_permanent_patches = purchased_permanent_patches

        # process patch cap amount
        patch_cap_increase: int = data.get("patch_cap_increase", self.city_trial_patch_cap_amount)
        if patch_cap_increase:
            logger.debug(f"setting patch cap amount from items file: {patch_cap_increase}")
        self.city_trial_patch_cap_amount = patch_cap_increase

        # process unlocked stadiums
        unlocked_stadiums: list[str] = data.get("unlocked_stadiums", [])
        if unlocked_stadiums:
            logger.debug(f"setting unlocked stadiums from items file: {unlocked_stadiums}")
        for stage_name in unlocked_stadiums:
            # this is already the stage name
            self.dolphin_interface.unlocked_stadiums.add(StageName(stage_name))

    def read_items_file(self) -> None:
        """
        Reads data from the kirby air ride items file and sets data accordingly.
        """
        try:
            with open(self.items_file_path, "r") as items_file:
                data: dict = json.load(items_file)
                if not data:
                    logger.warning(f"No data in {self.items_file_path}. Overwriting with blank schema.")
                    self.write_items_file()
                else:
                    self.process_items_file(data)
        except OSError:
            # file did not exist or could not be read from
            # create new file
            logger.warning(
                f"{self.items_file_path} did not exist or could not be read from (possible new game), creating..."
            )
            self.write_items_file()

    def write_items_file(self) -> None:
        """
        Write the data values from the current state into the items file.
        """
        try:
            logger.debug(f"Writing items data to {self.items_file_path}")
            with open(self.items_file_path, "w") as items_file:
                data = {
                    "item_processed_index": self.item_processed_index,
                    "purchased_permanent_patches": self.purchased_permanent_patches,
                    "patch_cap_increase": self.city_trial_patch_cap_amount,
                    "unlocked_stadiums": list(self.dolphin_interface.unlocked_stadiums),
                }
                json.dump(data, items_file, indent=4, sort_keys=True)
                logger.debug(f"Items data written to {self.items_file_path}")
        except OSError as e:
            logger.warning(f"Could not open or create {self.items_file_path} to read items information: {e}")

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        """
        Handle incoming packages from the server.

        Args:
            cmd: The command received from the server.
            args: The command arguments.
        """
        if cmd == "Connected":
            if "death_link" in args["slot_data"]:
                self.death_link_enabled = bool(args["slot_data"]["death_link"])
                Utils.async_start(self.update_death_link(self.death_link_enabled))

            if "energy_link" in args["slot_data"]:
                self.energy_link_enabled = bool(args["slot_data"]["energy_link"])
                if self.energy_link_enabled:
                    self.set_notify(f"EnergyLink{self.team}")
                    if self.ui:
                        self.ui.enable_energy_link()
                    logger.info("EnergyLink enabled.")

            if "reveal_checklists" in args["slot_data"]:
                self.reveal_checklists = bool(args["slot_data"]["reveal_checklists"])

            if "city_trial_goal" in args["slot_data"]:
                self.city_trial_goal = args["slot_data"]["city_trial_goal"]
                if self.city_trial_goal != CityTrialGoal.option_none:
                    self.city_trial_enabled = True

            if "air_ride_goal" in args["slot_data"]:
                self.air_ride_goal = args["slot_data"]["air_ride_goal"]
                if self.air_ride_goal != AirRideGoal.option_none:
                    self.air_ride_enabled = True

            if "top_ride_goal" in args["slot_data"]:
                self.top_ride_goal = args["slot_data"]["top_ride_goal"]
                if self.top_ride_goal != TopRideGoal.option_none:
                    self.top_ride_enabled = True

            if "city_trial_checklist_amount" in args["slot_data"]:
                self.city_trial_goal_checklist_amount = int(args["slot_data"]["city_trial_checklist_amount"])

            if "air_ride_checklist_amount" in args["slot_data"]:
                self.air_ride_goal_checklist_amount = int(args["slot_data"]["air_ride_checklist_amount"])

            if "top_ride_checklist_amount" in args["slot_data"]:
                self.top_ride_goal_checklist_amount = int(args["slot_data"]["top_ride_checklist_amount"])

            if "city_trial_progressive_patch_caps" in args["slot_data"]:
                self.city_trial_patch_cap_enabled = bool(args["slot_data"]["city_trial_progressive_patch_caps"])

            if "city_trial_patch_cap_amount" in args["slot_data"]:
                self.city_trial_patch_cap_amount = int(args["slot_data"]["city_trial_patch_cap_amount"])
                logger.debug(f"set city trial patch cap to {self.city_trial_patch_cap_amount} from player options")

            if "city_trial_progressive_stadiums" in args["slot_data"]:
                self.city_trial_progressive_stadiums_enabled = bool(
                    args["slot_data"]["city_trial_progressive_stadiums"]
                )

            self.enabled_modes = tuple(
                mode for mode in ("city_trial", "air_ride", "top_ride") if getattr(self, f"{mode}_enabled")
            )

            # reset local location checks and goals achieved so that a client that has already won its game but
            # hasn't closed can't connect to a server and accidentally auto-win. This doesn't solve the problem
            # of using a save file that already has won, but does solve this smaller problem.
            self.locations_checked.clear()
            self.city_trial_goal_achieved = False
            self.air_ride_goal_achieved = False
            self.top_ride_goal_achieved = False
            self.finished_game = False
            # also reset unlocked stadiums for the same reason
            self.dolphin_interface.unlocked_stadiums.clear()

            # if "reveal checklists" option is set, loop through the enabled checklists and set the visible bit.
            if self.reveal_checklists:
                if self.city_trial_enabled:
                    for location_data in CITY_TRIAL_LOCATION_TABLE.values():
                        if location_data.mem_address is not None:
                            current_val = self.dolphin_interface.read_byte(location_data.mem_address)
                            # set visible bit on the current val int
                            new_int = int(current_val | CheckboxFlags.VISIBLE)
                            self.dolphin_interface.write_byte(location_data.mem_address, new_int)
                if self.air_ride_enabled:
                    for location_data in AIR_RIDE_LOCATION_TABLE.values():
                        if location_data.mem_address is not None:
                            current_val = self.dolphin_interface.read_byte(location_data.mem_address)
                            # set visible bit on the current val int
                            new_int = int(current_val | CheckboxFlags.VISIBLE)
                            self.dolphin_interface.write_byte(location_data.mem_address, new_int)
                if self.top_ride_enabled:
                    for location_data in TOP_RIDE_LOCATION_TABLE.values():
                        if location_data.mem_address is not None:
                            current_val = self.dolphin_interface.read_byte(location_data.mem_address)
                            # set visible bit on the current val int
                            new_int = int(current_val | CheckboxFlags.VISIBLE)
                            self.dolphin_interface.write_byte(location_data.mem_address, new_int)

            # sync the local checklist state with the locations that have been checked according to the server.
            # this is useful for same-slot co-op, recovering from losing a save file, and picking up a slot in an
            # async. This is also needed to support other players in a multiworld collecting their items from our world.
            if len(args["checked_locations"]) > 0:
                location_table = CITY_TRIAL_LOCATION_TABLE | AIR_RIDE_LOCATION_TABLE | TOP_RIDE_LOCATION_TABLE
                for location_int in args["checked_locations"]:
                    location_name = self.location_names.lookup_in_game(location_int)
                    mem_address = location_table[location_name].mem_address
                    if mem_address is not None:
                        current_val = self.dolphin_interface.read_byte(mem_address)
                        # only unlock the checkbox if it isn't unlocked yet
                        if current_val in self.excluded_checkbox_bytes:
                            new_val = int(current_val | CheckboxFlags.FLAGGED_FOR_UNLOCK | CheckboxFlags.VISIBLE)
                            self.dolphin_interface.write_byte(mem_address, new_val)

            # read and process the items file and set class vars accordingly
            self.read_items_file()

            # print the goal(s) to the player
            goals = []
            if self.city_trial_enabled:
                if self.city_trial_goal == CityTrialGoal.option_n_checklist_blocks:
                    goals.append(f"{self.city_trial_goal}: {self.city_trial_goal_checklist_amount}")
                else:
                    goals.append(f"{self.city_trial_goal}")
            if self.air_ride_enabled:
                if self.air_ride_goal == AirRideGoal.option_n_checklist_blocks:
                    goals.append(f"{self.air_ride_goal}: {self.air_ride_goal_checklist_amount}")
                else:
                    goals.append(f"{self.air_ride_goal}")
            if self.top_ride_enabled:
                if self.top_ride_goal == TopRideGoal.option_n_checklist_blocks:
                    goals.append(f"{self.top_ride_goal}: {self.top_ride_goal_checklist_amount}")
                else:
                    goals.append(f"{self.top_ride_goal}")

            logger.info(f"Goal(s): {goals}")

        # ReceivedItems is a list of items that we have received from the server that are in a guaranteed order.
        # {"index": 0, "items": [NetworkItem, NetworkItem, ...]}
        # if we have a starting inventory or are returning to a game where we have already received items,
        # a ReceivedItems packet will be sent alongside Connected, with index = 0. This is the whole of items received.
        # This will include items we've received while being offline.
        if cmd == "ReceivedItems":
            logger.debug(
                f"Got ReceivedItems packet: {args}, \
                    ({[self.item_names.lookup_in_game(item.item) for item in args['items']]})"
            )
            new_items = list(self.items_received[self.item_processed_index :])
            logger.debug(
                f"adding new items to the queue: {[self.item_names.lookup_in_game(item.item) for item in new_items]}"
            )
            self.items_queue.extend(new_items)
            self.item_processed_index = len(self.items_received)
            self.write_items_file()

        # SetReply is sent when a server data storage key was updated by us with Set(), and we requested a
        # reply afterwards. Also received when SetNotify was requested for a certain key.
        if cmd == "SetReply":
            logger.debug(f"Got SetReply from the server: {args}")

    def on_deathlink(self, data: dict[str, Any]) -> None:
        """
        Handle a DeathLink event.

        Args:
            data: The data associated with the DeathLink event.
        """
        super().on_deathlink(data)
        # TODO: queue up a deathlink if the player is not in a stage when it happens
        if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
            self.dolphin_interface.give_death()

    async def check_death(self) -> None:
        """
        Check if the player is currently dead in-game.
        If DeathLink is on, notify the server of the player's death.
        """
        if not self.dolphin_interface.check_alive() and self.slot is not None:
            logger.debug("player is not alive")
            # in city trial, give the player 2 minutes to get back on an air ride machine until death is sent again
            # TODO: configurable option for length of time?
            # TODO: player can keep sending death by not getting on a vehicle. turn this into a trigger
            # TODO: currently, receiving a death also will reset this cooldown. might want to separate this from
            # self.last_death_link
            if time.time() >= self.last_death_link + self.death_link_cooldown:
                await self.send_death(self.player_names[self.slot] + " exploded.")
            else:
                logger.debug("did not send death (cooldown not elapsed)")

    async def send_victory(self) -> None:
        """Send a message to the server that the player has completed their goal."""
        await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

    async def send_check_locations(self) -> None:
        """
        Check all locations and notify the server of any newly checked locations.
        If the goal has been completed, notify the server of victory.
        """
        # check City Trial Checklist if City Trial is enabled
        if self.city_trial_enabled:
            self.city_trial_num_locations_checked = 0
            for location_data in self.city_trial_checklist_locations:
                if location_data.mem_address is not None and location_data.code is not None:
                    checkbox_byte = self.dolphin_interface.read_byte(location_data.mem_address)
                    if checkbox_byte not in self.excluded_checkbox_bytes:
                        self.city_trial_num_locations_checked += 1
                        self.locations_checked.add(location_data.code)

        # check Air Ride Checklist if Air Ride is enabled
        if self.air_ride_enabled:
            self.air_ride_num_locations_checked = 0
            for location_data in self.air_ride_checklist_locations:
                if location_data.mem_address is not None and location_data.code is not None:
                    checkbox_byte = self.dolphin_interface.read_byte(location_data.mem_address)
                    if checkbox_byte not in self.excluded_checkbox_bytes:
                        self.air_ride_num_locations_checked += 1
                        self.locations_checked.add(location_data.code)

        # check Top Ride Checklist if Top Ride is enabled
        if self.top_ride_enabled:
            self.top_ride_num_locations_checked = 0
            for location_data in self.top_ride_checklist_locations:
                if location_data.mem_address is not None and location_data.code is not None:
                    checkbox_byte = self.dolphin_interface.read_byte(location_data.mem_address)
                    if checkbox_byte not in self.excluded_checkbox_bytes:
                        self.top_ride_num_locations_checked += 1
                        self.locations_checked.add(location_data.code)

        # determine if overall goal has been achieved
        if not self.finished_game:
            await self.determine_goal_achieved()

        # Send newly checked locations to the server
        new_locations_checked = await self.check_locations(self.locations_checked)
        if new_locations_checked:
            location_names = [self.location_names.lookup_in_game(location_id) for location_id in new_locations_checked]
            logger.debug(f"New locations checked and sent to server: {new_locations_checked} ({location_names})")

    async def determine_goal_achieved(self) -> None:
        # check city trial goals
        if self.city_trial_enabled and not self.city_trial_goal_achieved:
            # check for victory condition location
            if self.city_trial_goal != CityTrialGoal.option_n_checklist_blocks:
                goal_location_data = CITY_TRIAL_LOCATION_TABLE[self.city_trial_goal]
                if goal_location_data.code in self.locations_checked:
                    if goal_location_data.mem_address is not None:
                        checkbox_byte = self.dolphin_interface.read_byte(goal_location_data.mem_address)
                        if checkbox_byte & CheckboxFlags.FILLER_PURPLE.value:
                            # if the checkbox is a goal checkbox and checked off via checkbox filler, reset it
                            # to locked and do not add it to locations_checked
                            self.locations_checked.remove(goal_location_data.code)
                            self.dolphin_interface.write_byte(
                                goal_location_data.mem_address, int(CheckboxFlags.VISIBLE)
                            )
                            # refund checkbox filler
                            self.dolphin_interface.apply_checkbox_filler(CheckboxFillerType.CITY_TRIAL_CHECKBOX_FILLER)
                        else:
                            logger.info(f"Victory location found for City Trial: {self.city_trial_goal}")
                            self.city_trial_goal_achieved = True

            # check for n checklist blocks goal victory
            if (
                self.city_trial_goal == CityTrialGoal.option_n_checklist_blocks
                and self.city_trial_num_locations_checked >= self.city_trial_goal_checklist_amount
            ):
                logger.info(
                    f"N Checklist Blocks Goal Acheived for City Trial - locations checked: \
                        {self.city_trial_num_locations_checked} goal amount: {self.city_trial_goal_checklist_amount}",
                )
                self.city_trial_goal_achieved = True

        # check air ride goals
        if self.air_ride_enabled and not self.air_ride_goal_achieved:
            # check for victory condition location
            if self.air_ride_goal != AirRideGoal.option_n_checklist_blocks:
                goal_location_data = AIR_RIDE_LOCATION_TABLE[self.air_ride_goal]
                if goal_location_data.code in self.locations_checked:
                    if goal_location_data.mem_address is not None:
                        checkbox_byte = self.dolphin_interface.read_byte(goal_location_data.mem_address)
                        if checkbox_byte & CheckboxFlags.FILLER_PURPLE.value:
                            # if the checkbox is a goal checkbox and checked off via checkbox filler, reset it
                            # to locked and do not add it to locations_checked
                            self.locations_checked.remove(goal_location_data.code)
                            self.dolphin_interface.write_byte(
                                goal_location_data.mem_address, int(CheckboxFlags.VISIBLE)
                            )
                            # refund checkbox filler
                            self.dolphin_interface.apply_checkbox_filler(CheckboxFillerType.AIR_RIDE_CHECKBOX_FILLER)
                        else:
                            logger.info(f"Victory location found for Air Ride: {self.air_ride_goal}")
                            self.air_ride_goal_achieved = True

            # check for n checklist blocks goal victory
            if (
                self.air_ride_goal == AirRideGoal.option_n_checklist_blocks
                and self.air_ride_num_locations_checked >= self.air_ride_goal_checklist_amount
            ):
                logger.info(
                    f"N Checklist Blocks Goal Acheived for Air Ride - locations checked: \
                        {self.air_ride_num_locations_checked} goal amount: {self.air_ride_goal_checklist_amount}",
                )
                self.air_ride_goal_achieved = True

        # check top ride goals
        if self.top_ride_enabled and not self.top_ride_goal_achieved:
            # check for victory condition location
            if self.top_ride_goal != TopRideGoal.option_n_checklist_blocks:
                goal_location_data = TOP_RIDE_LOCATION_TABLE[self.top_ride_goal]
                if goal_location_data.code in self.locations_checked:
                    if goal_location_data.mem_address is not None:
                        checkbox_byte = self.dolphin_interface.read_byte(goal_location_data.mem_address)
                        if checkbox_byte & CheckboxFlags.FILLER_PURPLE.value:
                            # if the checkbox is a goal checkbox and checked off via checkbox filler, reset it
                            # to locked and do not add it to locations_checked
                            self.locations_checked.remove(goal_location_data.code)
                            self.dolphin_interface.write_byte(
                                goal_location_data.mem_address, int(CheckboxFlags.VISIBLE)
                            )
                            # refund checkbox filler
                            self.dolphin_interface.apply_checkbox_filler(CheckboxFillerType.TOP_RIDE_CHECKBOX_FILLER)
                        else:
                            logger.info(f"Victory location found for Top Ride: {self.top_ride_goal}")
                            self.top_ride_goal_achieved = True

            # check for n checklist blocks goal victory
            if (
                self.top_ride_goal == TopRideGoal.option_n_checklist_blocks
                and self.top_ride_num_locations_checked >= self.top_ride_goal_checklist_amount
            ):
                logger.info(
                    f"N Checklist Blocks Goal Acheived for Top Ride - locations checked: \
                        {self.top_ride_num_locations_checked} goal amount: {self.top_ride_goal_checklist_amount}",
                )
                self.top_ride_goal_achieved = True

        # check for game complete (completed goals for all enabled modes)
        if all(getattr(self, f"{mode}_goal_achieved") for mode in self.enabled_modes):
            self.finished_game = True
            await self.send_victory()

    def give_item(self, item: NetworkItem) -> NetworkItem | None:
        """
        Give an item to the player in-game. Returns the item if it was successfully given.

        Args:
            item: NetworkItem
        """
        item_name = self.item_names.lookup_in_game(item.item)
        item_data = ITEM_TABLE[item_name]

        match item_data.type:
            case KARItemType.PATCH.value:
                if self.dolphin_interface.current_stage in (
                    StageName.CITY_TRIAL,
                    StageName.STADIUM_DESTRUCTION_DERBY_4,
                    StageName.STADIUM_DESTRUCTION_DERBY_5,
                ):
                    logger.debug("in patch item give...")
                    patch_type = get_patch_type_from_item_name(item_name)
                    logger.debug(f"giving patch type: {patch_type}")
                    if patch_type is not None:
                        stat_type = patch_type_to_stat_type(patch_type)
                        logger.debug(f"patch type has stat type of {stat_type}")
                        delta = 1 if "Up" in patch_type.value else -1
                        if stat_type is not None:
                            self.dolphin_interface.increment_player_patch_stat(stat_type, delta)
                            return item
                        # stat_type returned None, either invalid or All patch type
                        if "All" in patch_type.value:
                            for stat in self.dolphin_interface.player_1_patches:
                                logger.debug(f"incrementing stat {stat_type} by {delta}")
                                self.dolphin_interface.increment_player_patch_stat(stat, delta)
                            return item
                        logger.debug(f"Failed to parse stat type from patch type: {patch_type}")
                        return item
                    logger.debug(f"Failed to parse patch type from item name: {item_name}")
                    return item
            case KARItemType.PATCH_CAP_INCREASE.value:
                logger.debug("in patch cap increase item give...")
                patch_cap_increase_type = get_patch_cap_increase_type_from_item_name(item_name)
                if patch_cap_increase_type is not None:
                    self.city_trial_patch_cap_amount += 1
                    logger.debug(f"Patch cap increased to {self.city_trial_patch_cap_amount}")
                else:
                    logger.debug(f"Failed to parse patch cap increase type from item name: {item_name}")
                return item
            case KARItemType.CHECKBOX_FILLER.value:
                logger.debug("in checkbox filler item give...")
                checkbox_filler_type = get_checkbox_filler_type_from_item_name(item_name)
                if checkbox_filler_type is not None:
                    logger.debug(f"applying checkbox filler type: {checkbox_filler_type}")
                    self.dolphin_interface.apply_checkbox_filler(checkbox_filler_type)
                else:
                    logger.debug(f"Failed to parse checkbox filler type from item name: {item_name}")
                return item
            case KARItemType.PROGRESSIVE_STADIUM.value:
                logger.debug("in progressive stadium item give...")
                prog_stadium_type = get_progressive_stadium_unlock_type_from_item_name(item_name)
                if prog_stadium_type is not None:
                    stage_name = get_stage_name_from_stadium_unlock_type(prog_stadium_type)
                    self.dolphin_interface.unlocked_stadiums.add(stage_name)
                else:
                    logger.debug(f"invalid progressive stadium type: {item_name}")
                return item
            case KARItemType.EFFECT.value:
                if self.dolphin_interface.current_stage in (
                    StageName.CITY_TRIAL,
                    StageName.STADIUM_DESTRUCTION_DERBY_1,
                    StageName.STADIUM_DESTRUCTION_DERBY_2,
                    StageName.STADIUM_DESTRUCTION_DERBY_3,
                    StageName.STADIUM_VS_KING_DEDEDE,
                    StageName.STADIUM_KIRBY_MELEE_1,
                    StageName.STADIUM_KIRBY_MELEE_2,
                ):
                    logger.debug("in effect item give...")
                    effect_type = get_effect_type_from_item_name(item_name)
                    if effect_type is not None:
                        self.dolphin_interface.apply_effect_item(effect_type)
                    else:
                        logger.debug(f"Failed to parse effect type from item name: {item_name}")
                    return item
        return None

    async def give_items(self, items: list[NetworkItem]) -> list[NetworkItem]:
        """
        Give the player the list of items. Returns only the list of items successfully given.

        Args:
            items: The list of NetworkItems from the server.
        """
        given_items: list[NetworkItem] = []
        # create a copy of the list to avoid iterating over a possibly changing item list
        for item in list(items):
            item_given = self.give_item(item)
            if item_given is not None:
                given_items.append(item_given)

        # write to the items file to ensure we've saved items that were given
        if given_items:
            self.write_items_file()

        return given_items

    async def shutdown(self) -> None:
        """Shutdown the client and clean up resources."""
        if self.dolphin_interface.is_hooked():
            self.dolphin_interface.unhook()

        await super().shutdown()

    async def send_energy(self, value: float) -> None:
        """
        Adds the given amount of energy to energylink.
        """
        Utils.async_start(
            self.send_msgs(
                [{"cmd": "Set", "key": f"EnergyLink{self.team}", "operations": [{"operation": "add", "value": value}]}]
            )
        )

    async def remove_energy(self, value: int) -> None:
        """
        Removes the given amount of energy from energylink.
        """
        if self.current_energy_link_value is not None:
            Utils.async_start(
                self.send_msgs(
                    [
                        {
                            "cmd": "Set",
                            "key": f"EnergyLink{self.team}",
                            "operations": [{"operation": "add", "value": -value}, {"operation": "max", "value": 0}],
                        }
                    ]
                )
            )

    async def update_energy_link(self) -> None:
        """
        Check if the player has created energy and update the energy link value accordingly.
        Additionally, add spent items to the item queue.

        Energylink value is increased for each patch a player collects and for each object destroyed in City Trial.
        """
        energy = 0

        if self.dolphin_interface.current_stage == StageName.CITY_TRIAL:
            # TODO: fix this giving energy from patches received from /energylink_spend
            # TODO: fix this giving energy for permanent patches when transitioning into City Trial
            diff = 0
            for stat_type, stat_count in self.dolphin_interface.player_1_patches.items():
                if stat_count > self.dolphin_interface.player_1_patches_old[stat_type]:
                    diff += stat_count - self.dolphin_interface.player_1_patches_old[stat_type]
            if diff > 0:
                energy += diff

            # give energy for destroying things
            old_count = self.dolphin_interface.destruction_count
            self.dolphin_interface.update_destruction_count()
            if self.dolphin_interface.destruction_count > old_count:
                # send .1 Joules of energy for every thing destroyed
                destruction_energy = (self.dolphin_interface.destruction_count - old_count) / 10
                energy += destruction_energy

        # send energy to the server
        if energy > 0:
            Utils.async_start(self.send_energy(energy))

    async def energy_link_spend(self, item_name: str, amount: str) -> None:
        """
        Spends EnergyLink energy on the requested amount of an item.
        """

        if self.current_energy_link_value is None:
            logger.info("No energy in pool.")
            return

        if int(amount) > 20:
            logger.info("The max amount of items you can purchase at once is 20.")
            return

        item_data = ITEM_TABLE.get(item_name)
        if not item_data or not item_data.code:
            logger.info(f"Invalid item name: {item_name}")
            return

        # base cost
        cost = self.energy_link_base_item_cost * int(amount)

        # determine costs for specific items
        match item_data.type:
            case KARItemType.PATCH:
                patch_type = get_patch_type_from_item_name(item_name)
                if patch_type is not None:
                    if patch_type in (PatchType.ALL_UP, PatchType.ALL_DOWN):
                        # ALL patches cost 9x as much
                        cost *= 9
                    # set purchased dict for the permanent patch type
                    if "Permanent" in patch_type.value:
                        cost *= 20
            case KARItemType.CHECKBOX_FILLER:
                cost *= 150
            case KARItemType.PATCH_CAP_INCREASE:
                cost *= 150
            case KARItemType.PROGRESSIVE_STADIUM:
                logger.info(f"Cannot buy a {KARItemType.PROGRESSIVE_STADIUM} item with energy.")
                return

        if self.current_energy_link_value < cost:
            logger.info(
                f"Not enough energy. Current amount: {self.current_energy_link_value:.2f} \
                    Need: {cost} for {amount} {item_name}."
            )
            return

        # save purchased permanent patches
        if item_data.type == KARItemType.PATCH and "Permanent" in item_name:
            if self.purchased_permanent_patches.get(item_name, False):
                self.purchased_permanent_patches[item_name] += int(amount)
            else:
                self.purchased_permanent_patches[item_name] = int(amount)
            self.write_items_file()

        self.energy_link_items_queue.extend([item_data.code] * int(amount))
        Utils.async_start(self.remove_energy(cost))
        logger.info(f"Spent {cost} energy on {amount} {item_name}.")

    def make_gui(self):
        """
        Initialize the GUI for Kirby Air Ride client.

        Returns:
            The client's GUI.
        """
        ui = super().make_gui()
        ui.base_title = "Archipelago Kirby Air Ride Client"
        return ui

    async def handle_connected_state(self) -> None:
        """Handle the logic when Dolphin is connected."""
        if self.slot is None:
            return

        # update current_stage and check if a transition into a stage has happend
        _, transition_trigger = self.dolphin_interface.check_transition()

        # handle stage transitions
        if transition_trigger:
            # handle the trigger events needed for transitioning into city trial
            # TODO: fix this giving the player items again if they close and reopen the client.
            if self.dolphin_interface.current_stage == StageName.CITY_TRIAL:
                logger.debug("queueing permanent patches...")
                # skip adding permanent patches to the item queue if they are already in it (from ReceivedItems)
                permanent_patches = [
                    item
                    for item in self.items_received
                    if "Permanent" in self.item_names.lookup_in_game(item.item) and item not in self.items_queue
                ]

                logger.debug("queueing purchased permanent patches...")
                for patch_name, patch_amount in self.purchased_permanent_patches.items():
                    item_data = ITEM_TABLE.get(patch_name)
                    if not item_data or not item_data.code:
                        logger.debug(f"Invalid item name: {patch_name}")
                        return
                    item = NetworkItem(item_data.code, 0, 0, 0)
                    permanent_patches.extend([item] * patch_amount)

                self.items_queue.extend(permanent_patches)

                # set the stadium event. if the game-chosen stadium (which will either be random or selected at
                # random via category specified by the player in city trial settings) is one that is already unlocked,
                # no need to choose one here. if it is locked, still select randomly from the category of stadium that
                # was selected.
                if self.city_trial_progressive_stadiums_enabled:
                    _, current_stage_name = self.dolphin_interface.get_city_trial_current_stadium()
                    if current_stage_name not in self.dolphin_interface.unlocked_stadiums:
                        logger.debug(f"game chose a locked stadium: {current_stage_name.value}")
                        # get the unlocked stadiums that are in the same category as the current stadium
                        category_unlocks = [
                            stage
                            for stage in self.dolphin_interface.unlocked_stadiums
                            if " ".join(current_stage_name.split(" ")[1:-1]) in stage.value
                        ]
                        if category_unlocks:
                            logger.debug(
                                f"choosing a random unlocked stadium from the same category: \
                                      {[stage.value for stage in category_unlocks]}"
                            )
                            rand_stadium = random.choice(category_unlocks)
                            logger.debug(f"setting stadium to {rand_stadium.value}")
                            self.dolphin_interface.set_city_trial_current_stadium(rand_stadium)
                        else:
                            logger.debug("no unlocked stadiums in the same category.")
                            try:
                                logger.debug(
                                    f"choosing a random unlocked stadium from: \
                                        {list(self.dolphin_interface.unlocked_stadiums)}"
                                )
                                rand_stadium = random.choice(list(self.dolphin_interface.unlocked_stadiums))
                                logger.debug(f"setting stadium to {rand_stadium.value}")
                                self.dolphin_interface.set_city_trial_current_stadium(rand_stadium)
                            except IndexError:
                                # no stadiums unlocked yet, just use the game-chosen value in this case
                                logger.debug(
                                    f"no stadiums were unlocked, leaving the game-set value of \
                                        {current_stage_name.value}"
                                )

        # set the stadium event at the end of the current trial. will only choose randomly from unlocked stadiums
        if self.city_trial_progressive_stadiums_enabled:
            # update the unlocked stadiums in-game to reflect our local state. this does not require the player
            # to be in a stage
            self.dolphin_interface.update_unlocked_stadiums()

        # update player patch counts and handle patch caps if player is in City Trial
        if self.dolphin_interface.current_stage == StageName.CITY_TRIAL and self.dolphin_interface.transition_waited():
            self.dolphin_interface.update_player_patch_counts()

            # reset the values for each patch to the cap if they are over the cap
            if self.city_trial_patch_cap_enabled:
                for stat_type, stat_count in self.dolphin_interface.player_1_patches.items():
                    # +2 offset for everything but HP
                    offset = 2 if stat_type != StatType.HP else 0
                    if stat_count + offset > self.city_trial_patch_cap_amount:
                        diff = int(self.city_trial_patch_cap_amount - (stat_count + offset))
                        logger.debug(
                            f"incrementing player stat {stat_type} by {diff} due to being over the cap of \
                            {self.city_trial_patch_cap_amount}"
                        )
                        self.dolphin_interface.increment_player_patch_stat(stat_type, diff)

        # handle energylink
        if self.energy_link_enabled:
            if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
                await self.update_energy_link()

            # if there are items that have been aquired by spending energy, queue those to be received
            # spending does not require the player to be in a stage
            if len(self.energy_link_items_queue) > 0:
                for item_id in self.energy_link_items_queue:
                    self.items_queue.append(NetworkItem(item_id, 0, 0, 0))
                self.energy_link_items_queue.clear()

        # check for death when in City Trial and past transition period
        if self.death_link_enabled:
            if (
                self.dolphin_interface.current_stage == StageName.CITY_TRIAL
                and self.dolphin_interface.transition_waited()
            ):
                # logger.debug("in deathlink check...")
                await self.check_death()

        # check if any items are in the items queue and give them
        if len(self.items_queue) > 0:
            # give items that do not require a player to be in a stage
            if self.dolphin_interface.current_stage is None:
                items = [
                    item
                    for item in self.items_queue
                    if ITEM_TABLE[self.item_names.lookup_in_game(item.item)].type
                    in (KARItemType.CHECKBOX_FILLER, KARItemType.PATCH_CAP_INCREASE, KARItemType.PROGRESSIVE_STADIUM)
                ]
                if len(items) > 0:
                    given_items = await self.give_items(items)
                    for item in given_items:
                        self.items_queue.remove(item)

            # give items that were received/purchased while in a stage
            if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
                given_items = await self.give_items(self.items_queue)
                for item in given_items:
                    self.items_queue.remove(item)

        # check locations
        await self.send_check_locations()

    async def handle_disconnected_state(self) -> None:
        """Handle the logic when Dolphin is disconnected."""

        logger.info("Attempting to connect to Dolphin...")
        await self.attempt_dolphin_connection()

    async def attempt_dolphin_connection(self) -> bool:
        """
        Try to establish a connection to Dolphin.

        Returns:
            Whether connection was successful
        """
        self.dolphin_interface.hook()
        if self.dolphin_interface.is_hooked():
            if not self.dolphin_interface.check_game_running():
                self.dolphin_interface.unhook()
                self.dolphin_status = self.connection_refused_game_status
                logger.info(self.dolphin_status)
                await asyncio.sleep(self.dolphin_reconnect_delay)
                return False

            self.dolphin_status = self.connection_connected_game_status
            logger.info(self.dolphin_status)
            return True

        self.dolphin_status = self.connection_refused_game_status
        logger.info(self.dolphin_status)
        await asyncio.sleep(self.dolphin_reconnect_delay)
        return False

    async def run_dolphin_sync(self) -> None:
        """The task loop for managing the connection to Dolphin."""
        logger.info("Starting Dolphin connector. Use /dolphin for status information.")

        while not self.exit_event.is_set():
            try:
                # self.watcher_event gets set when receiving ReceivedItems or LocationInfo, or when shutting down.
                await asyncio.wait_for(self.watcher_event.wait(), 1)
            except TimeoutError:
                pass
            finally:
                self.watcher_event.clear()

            try:
                if (
                    self.dolphin_interface.is_hooked()
                    and self.dolphin_interface.check_game_running()
                    and self.dolphin_status == self.connection_connected_game_status
                ):
                    await self.handle_connected_state()
                else:
                    self.dolphin_interface.unhook()
                    await self.handle_disconnected_state()
            except Exception as e:
                if self.dolphin_interface.is_hooked():
                    self.dolphin_interface.unhook()
                self.dolphin_status = self.connection_refused_game_status
                logger.info(self.dolphin_status)
                logger.error(f"Error in dolphin sync task: {e}")
                logger.error(traceback.format_exc())


async def async_main(connect: str | None, password: str | None) -> None:
    """
    Main async function to run the Kirby Air Ride client.

    Args:
        connect: Address of the Archipelago server
        password: Password for server authentication
    """
    ctx = KARContext(connect, password)

    # Start UI if enabled
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    # Give time for UI/CLI to initialize
    await asyncio.sleep(1)

    # Create and start server task
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    # Create and start dolphin sync task
    ctx.dolphin_sync_task = asyncio.create_task(ctx.run_dolphin_sync(), name="dolphin sync")

    try:
        await ctx.exit_event.wait()
    finally:
        # Signal the dolphin sync task to check for exit_event
        ctx.watcher_event.set()

        await ctx.shutdown()

        # Wait for the dolphin sync task to finish if it exists
        if ctx.dolphin_sync_task:
            await ctx.dolphin_sync_task


def main(connect: str | None = None, password: str | None = None) -> None:
    """
    Run the main async loop for the Kirby Air Ride client.

    Args:
        connect: Address of the Archipelago server.
        password: Password for server authentication.
    """
    Utils.init_logging("Kirby Air Ride Client")

    import colorama

    try:
        colorama.init()
        asyncio.run(async_main(connect, password))
    finally:
        colorama.deinit()


if __name__ == "__main__":
    parser = get_base_parser()
    args = parser.parse_args()
    main(args.connect, args.password)
