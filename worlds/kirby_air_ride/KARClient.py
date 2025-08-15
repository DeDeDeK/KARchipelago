import asyncio
import random
import time
import traceback
from typing import Any, List, Optional

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
    PatchCapIncreaseType,
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
from .KARItems import ITEM_TABLE, LOOKUP_ID_TO_NAME, KARItemType
from .KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_LOOKUP_ID_TO_NAME,
    TOP_RIDE_LOCATION_TABLE,
    KARLocationType,
)
from .KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal

CLIENT_VERSION = "v0.5.0"


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
        """Spend energy from EnergyLink on patches or other items. Specify items like: /energylink_spend "Top Speed Up" 1"""
        if isinstance(self.ctx, KARContext):
            if self.ctx.energy_link_enabled:
                Utils.async_start(self.ctx.energy_link_spend(item_name, amount))
            else:
                logger.info("You must enable energylink first with /energylink.")


class KARContext(CommonContext):
    """
    The context for Kirby Air Ride client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Kirby Air Ride.
    """

    game: str = "Kirby Air Ride"
    items_handling = 0b111  # receive items from the server for starting inventory, our own world, and other worlds
    want_slot_data = True  # need slot data for player options specified at generation
    command_processor = KARCommandProcessor

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        """
        Initialize the KAR context.

        Args:
            server_address: Address of the Archipelago server.
            password: Password for server authentication.
        """
        super().__init__(server_address, password)
        self.connection_refused_game_status = "Dolphin failed to connect. Please make sure your emulator is running and load an ISO for Kirby Air Ride. Trying again in 5 seconds..."
        self.connection_connected_game_status = "Dolphin connected successfully."
        self.connection_initial_status = "Dolphin connection has not been initiated."
        self.dolphin_interface = DolphinInterface()
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
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
        self.air_ride_enabled: bool = False
        self.air_ride_goal: str = ""
        self.air_ride_goal_checklist_amount: int = 0
        self.air_ride_goal_achieved: bool = False
        self.air_ride_num_locations_checked: int = 0
        self.top_ride_enabled: bool = False
        self.top_ride_goal: str = ""
        self.top_ride_goal_checklist_amount: int = 0
        self.top_ride_goal_achieved: bool = False
        self.top_ride_num_locations_checked: int = 0
        self.enabled_modes: tuple[str, ...] = ()
        self.items_queue: List[NetworkItem] = []
        self.energy_link_enabled: bool = False
        self.energy_link_items_queue: list[int] = []
        self.energy_link_base_item_cost: int = 10
        self.death_link_enabled: bool = False
        self.death_link_cooldown: int = 120
        # 00 = locked, not visible
        # 01 = flagged for unlocking
        # 10 = locked, visible
        # 11 = visible, flagged for unlocking
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
                logger.info(f"set city trial patch cap to {self.city_trial_patch_cap_amount} from player options")

            if "city_trial_progressive_stadiums" in args["slot_data"]:
                self.city_trial_progressive_stadiums_enabled = bool(
                    args["slot_data"]["city_trial_progressive_stadiums"]
                )

            self.enabled_modes = tuple(
                mode for mode in ("city_trial", "air_ride", "top_ride") if getattr(self, f"{mode}_enabled")
            )

            # reset local location checks so that a client that has already won its game but hasn't closed can't connect to a server
            # and accidentally auto-win. This doesn't solve the problem of using a save file that already has won, but does solve this smaller problem.
            self.locations_checked.clear()

            # also reset goals achieved for the same reason
            self.city_trial_goal_achieved = False
            self.air_ride_goal_achieved = False
            self.top_ride_goal_achieved = False
            self.finished_game = False

        # ReceivedItems is a list of items that are in a guaranteed order.
        # {"index": 0, "items": [{"item_1"}, {"item_2"}]}
        # if the index is 0, the whole items list is sent.
        # the server sends the whole item list with index = 0 upon every connection
        # TODO: fix this ignoring starting inventory?
        if cmd == "ReceivedItems":
            logger.debug("Got ReceivedItems packet, index: %s, items: %s", args["index"], args["items"])
            if args["index"] == 0:
                # set patch cap max based on how many progressive patch cap items we've received
                # TODO: since the index is also 0 for the first item, if the first item received is a
                # patch cap increase, this will add one on top of the item being received and adding one
                for network_item in args["items"]:
                    if ITEM_TABLE[LOOKUP_ID_TO_NAME[network_item.item]].type == KARItemType.PATCH_CAP_INCREASE:
                        self.city_trial_patch_cap_amount += 1
                logger.info(f"set city trial patch cap to {self.city_trial_patch_cap_amount} from items received")
                # trigger the Retrieved packet to update the patch cap amount based on items purchased
                Utils.async_start(self.get_server_purhased_item(PatchCapIncreaseType.ALL_CAP_INCREASE.value))

                # set unlocked stadiums based on the stadium unlock items we've received
                for network_item in args["items"]:
                    item_name = LOOKUP_ID_TO_NAME[network_item.item]
                    if ITEM_TABLE[item_name].type == KARItemType.PROGRESSIVE_STADIUM:
                        stadium = get_progressive_stadium_unlock_type_from_item_name(item_name)
                        if stadium is not None:
                            stage_name = get_stage_name_from_stadium_unlock_type(stadium)
                            self.dolphin_interface.unlocked_stadiums.add(stage_name)

            if args["index"] != 0:
                self.items_queue.extend(args["items"])

        # Retrieved is sent in repsonse to any Get command. It returns a dict[str, any].
        if cmd == "Retrieved":
            logger.info(f"got Retrieved packet: {args}")
            # add to city trial patch cap amount based on the number of cap increases purchased
            item = f"EnergyLink{self.team}PurchasedItem-{PatchCapIncreaseType.ALL_CAP_INCREASE.value}"
            if item in args["keys"]:
                if args["keys"][item] is not None:
                    self.city_trial_patch_cap_amount += int(args["keys"][item])
                    logger.info(f"patch cap increased to {self.city_trial_patch_cap_amount} from purchased items")

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
            for location_data in CITY_TRIAL_LOCATION_TABLE.values():
                if location_data.type == KARLocationType.CHECKLISTBOX and location_data.mem_address is not None:
                    if self.dolphin_interface.read_byte(location_data.mem_address) not in self.excluded_checkbox_bytes:
                        if location_data.code is not None:
                            self.city_trial_num_locations_checked += 1
                            self.locations_checked.add(location_data.code)

            # check goals
            if not (self.city_trial_goal_achieved or self.finished_game):
                # check for victory condition location
                if self.city_trial_goal != CityTrialGoal.option_n_checklist_blocks:
                    if CITY_TRIAL_LOCATION_TABLE[self.city_trial_goal].code in self.locations_checked:
                        logger.info(f"Victory location found for City Trial: {self.city_trial_goal}")
                        self.city_trial_goal_achieved = True

                # check for n checklist blocks goal victory
                if (
                    self.city_trial_goal == CityTrialGoal.option_n_checklist_blocks
                    and self.city_trial_num_locations_checked >= self.city_trial_goal_checklist_amount
                ):
                    logger.info(
                        f"N Checklist Blocks Goal Acheived for City Trial - locations checked: {self.city_trial_num_locations_checked} goal amount: {self.city_trial_goal_checklist_amount}"
                    )
                    self.city_trial_goal_achieved = True

        # check Air Ride Checklist if Air Ride is enabled
        if self.air_ride_enabled:
            self.air_ride_num_locations_checked = 0
            for location_data in AIR_RIDE_LOCATION_TABLE.values():
                if location_data.type == KARLocationType.CHECKLISTBOX and location_data.mem_address is not None:
                    if self.dolphin_interface.read_byte(location_data.mem_address) not in self.excluded_checkbox_bytes:
                        if location_data.code is not None:
                            self.air_ride_num_locations_checked += 1
                            self.locations_checked.add(location_data.code)

            # check goals
            if not (self.air_ride_goal_achieved or self.finished_game):
                # check for victory condition location
                if self.air_ride_goal != AirRideGoal.option_n_checklist_blocks:
                    if AIR_RIDE_LOCATION_TABLE[self.air_ride_goal].code in self.locations_checked:
                        logger.info(f"Victory location found for Air Ride: {self.air_ride_goal}")
                        self.air_ride_goal_achieved = True

                # check for n checklist blocks goal victory
                if (
                    self.air_ride_goal == AirRideGoal.option_n_checklist_blocks
                    and self.air_ride_num_locations_checked >= self.air_ride_goal_checklist_amount
                ):
                    logger.info(
                        f"N Checklist Blocks Goal Acheived for Air Ride - locations checked: {self.air_ride_num_locations_checked} goal amount: {self.air_ride_goal_checklist_amount}"
                    )
                    self.air_ride_goal_achieved = True

        # check Top Ride Checklist if Top Ride is enabled
        if self.top_ride_enabled:
            self.top_ride_num_locations_checked = 0
            for location_data in TOP_RIDE_LOCATION_TABLE.values():
                if location_data.type == KARLocationType.CHECKLISTBOX and location_data.mem_address is not None:
                    if self.dolphin_interface.read_byte(location_data.mem_address) not in self.excluded_checkbox_bytes:
                        if location_data.code is not None:
                            self.top_ride_num_locations_checked += 1
                            self.locations_checked.add(location_data.code)

            # check goals
            if not (self.top_ride_goal_achieved or self.finished_game):
                # check for victory condition location
                if self.top_ride_goal != TopRideGoal.option_n_checklist_blocks:
                    if TOP_RIDE_LOCATION_TABLE[self.top_ride_goal].code in self.locations_checked:
                        logger.info(f"Victory location found for Top Ride: {self.top_ride_goal}")
                        self.top_ride_goal_achieved = True

                # check for n checklist blocks goal victory
                if (
                    self.top_ride_goal == TopRideGoal.option_n_checklist_blocks
                    and self.top_ride_num_locations_checked >= self.top_ride_goal_checklist_amount
                ):
                    logger.info(
                        f"N Checklist Blocks Goal Acheived for Top Ride - locations checked: {self.top_ride_num_locations_checked} goal amount: {self.top_ride_goal_checklist_amount}"
                    )
                    self.top_ride_goal_achieved = True

        # determine if overall goal has been achieved
        if not self.finished_game:
            await self.determine_goal_achieved()

        # Send newly checked locations to the server
        new_locations_checked = await self.check_locations(self.locations_checked)
        if new_locations_checked:
            logger.debug(
                "New locations checked and sent to server: %s",
                [f"{LOCATION_LOOKUP_ID_TO_NAME[location_id]} ({location_id})" for location_id in new_locations_checked],
            )

    async def determine_goal_achieved(self) -> None:
        if all(getattr(self, f"{mode}_goal_achieved") for mode in self.enabled_modes):
            self.finished_game = True
            await self.send_victory()

    def give_item(self, item: NetworkItem) -> NetworkItem | None:
        """
        Give an item to the player in-game. Returns the item if it was successfully given.

        Args:
            item: NetworkItem
        """
        item_name = LOOKUP_ID_TO_NAME[item.item]
        item_data = ITEM_TABLE[item_name]

        match item_data.type:
            case KARItemType.PATCH.value:
                logger.info("In patch item give...")
                if self.dolphin_interface.current_stage == StageName.CITY_TRIAL:
                    patch_type = get_patch_type_from_item_name(item_name)
                    logger.info(f"giving patch type: {patch_type}")
                    if patch_type is not None:
                        stat_type = patch_type_to_stat_type(patch_type)
                        logger.info(f"patch type has stat type of {stat_type}")
                        delta = 1 if "Up" in patch_type.value else -1
                        if stat_type is not None:
                            self.dolphin_interface.increment_player_patch_stat(stat_type, delta)
                            return item
                        else:
                            # stat_type returned None, either invalid or All patch type
                            if "All" in patch_type.value:
                                for stat in self.dolphin_interface.player_1_patches:
                                    logger.info(f"incrementing stat {stat_type} by {delta}")
                                    self.dolphin_interface.increment_player_patch_stat(stat, delta)
                                return item
                            else:
                                logger.warning(f"Failed to parse stat type from patch type: {patch_type}")
                                return item
                    else:
                        logger.warning(f"Failed to parse patch type from item name: {item_name}")
                        return item
            case KARItemType.PATCH_CAP_INCREASE.value:
                logger.info("in patch cap increase item give...")
                patch_cap_increase_type = get_patch_cap_increase_type_from_item_name(item_name)
                if patch_cap_increase_type is not None:
                    self.city_trial_patch_cap_amount += 1
                    logger.info(f"patch cap increased to {self.city_trial_patch_cap_amount}")
                else:
                    logger.warning(f"Failed to parse patch cap increase type from item name: {item_name}")
                return item
            case KARItemType.CHECKBOX_REWARD.value:
                return item
            case KARItemType.CHECKBOX_FILLER.value:
                logger.info("in checkbox filler item give...")
                checkbox_filler_type = get_checkbox_filler_type_from_item_name(item_name)
                if checkbox_filler_type is not None:
                    logger.info(f"applying checkbox filler type: {checkbox_filler_type}")
                    self.dolphin_interface.apply_checkbox_filler(checkbox_filler_type)
                else:
                    logger.warning(f"Failed to parse checkbox filler type from item name: {item_name}")
                return item
            case KARItemType.PROGRESSIVE_STADIUM.value:
                prog_stadium_type = get_progressive_stadium_unlock_type_from_item_name(item_name)
                if prog_stadium_type is not None:
                    stage_name = get_stage_name_from_stadium_unlock_type(prog_stadium_type)
                    self.dolphin_interface.unlocked_stadiums.add(stage_name)
                else:
                    logger.warning(f"invalid progressive stadium type: {item_name}")
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
                    effect_type = get_effect_type_from_item_name(item_name)
                    if effect_type is not None:
                        self.dolphin_interface.apply_effect_item(effect_type)
                    else:
                        logger.warning(f"Failed to parse effect type from item name: {item_name}")
                    return item

    async def give_items(self, items: List[NetworkItem]) -> List[NetworkItem]:
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

    async def update_server_purchased_item(self, item_name: str, amount: int) -> None:
        """
        Updates the server storage key for the item purchased through energylink. Adds the amount to the
        existing amount.
        """
        logger.info(f"updating server storage for {item_name}: amount: {amount}")
        Utils.async_start(
            self.send_msgs(
                [
                    {
                        "cmd": "Set",
                        "key": f"EnergyLink{self.team}PurchasedItem-{item_name}",
                        "default": amount,
                        "want_reply": True,
                        "operations": [{"operation": "add", "value": amount}],
                    }
                ]
            )
        )

    async def get_server_purhased_item(self, item_name: str) -> None:
        """
        Get the server-stores data for the everylink purchased item of the given item_name.
        The data will be sent back in a Retrieved package.
        """
        logger.info(f"getting server storage for {item_name}")
        Utils.async_start(
            self.send_msgs(
                [
                    {
                        "cmd": "Get",
                        "keys": [f"EnergyLink{self.team}PurchasedItem-{item_name}"],
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
            logger.info(f"No energy in pool. Current value: {self.current_energy_link_value}")
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
                    if patch_type == PatchType.ALL_UP or patch_type == PatchType.ALL_DOWN:
                        # ALL patches cost 9x as much
                        cost *= 9
            case KARItemType.CHECKBOX_FILLER:
                # cost *= 60
                pass
            case KARItemType.PATCH_CAP_INCREASE:
                # cost *= 50
                pass
            case KARItemType.PROGRESSIVE_STADIUM:
                # cost *= 100
                pass

        if self.current_energy_link_value < cost:
            logger.info(
                f"Not enough energy. Current amount: {self.current_energy_link_value} Need: {cost} for {amount} {item_name}."
            )
            return

        self.energy_link_items_queue.extend([item_data.code] * int(amount))
        Utils.async_start(self.remove_energy(cost))
        logger.info(f"Spent {cost} energy on {amount} {item_name}.")

        if item_data.type == KARItemType.PATCH_CAP_INCREASE:
            # update the server storage for the patch cap increase
            Utils.async_start(self.update_server_purchased_item(item_name, int(amount)))

    def make_gui(self):
        """
        Initialize the GUI for Kirby Air Ride client.

        Returns:
            The client's GUI.
        """
        ui = super().make_gui()
        ui.base_title = f"Archipelago Kirby Air Ride Client ({CLIENT_VERSION})"
        return ui

    async def handle_connected_state(self) -> None:
        """Handle the logic when Dolphin is connected."""
        if self.slot is None:
            return

        # update current_stage and check if a transition into a stage has happend
        _, transition_trigger = self.dolphin_interface.check_transition()

        # handle stage transitions
        if transition_trigger:
            # queue up permanent patches if player has transitioned into City Trial
            # TODO: fix this giving the player items again if they close and reopen the client.
            # TODO: this will not give players permanent patches if they are off of a vehicle when the patches
            # are given. The game resets the patches to 0 when off of a vehicle, and then seems to set the values
            # back to whatever the value was when they got off of the vehicle
            if self.dolphin_interface.current_stage == StageName.CITY_TRIAL:
                logger.debug("queueing permanent patches...")
                # skip adding permanent patches to the item queue if they are already in it (from ReceivedItems)
                items = [
                    item
                    for item in self.items_received
                    if "Permanent" in LOOKUP_ID_TO_NAME[item.item] and item not in self.items_queue
                ]
                self.items_queue.extend(items)

                # set the stadium event
                if self.city_trial_progressive_stadiums_enabled:
                    try:
                        rand_stadium = random.choice(list(self.dolphin_interface.unlocked_stadiums))
                        logger.info(f"setting stadium to {rand_stadium.value}")
                    except IndexError:
                        # no stadiums unlocked yet, set None to prevent stadiums from being unlocked until we receive a
                        # stadium unlock item
                        # TODO: this causes the game to crash when the stadium hint event happens. Might have to switch
                        # to starting with a single stadium unlocked at first
                        rand_stadium = None
                    self.dolphin_interface.set_city_trial_current_stadium(rand_stadium)

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
                        logger.info(
                            f"incrementing player stat {stat_type} by {diff} due to being over the cap of {self.city_trial_patch_cap_amount}"
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
                logger.debug("in deathlink check...")
                await self.check_death()

        # check if any items are in the items queue and give them
        if len(self.items_queue) > 0:
            # give items that do not require a player to be in a stage
            # give checkbox fillers
            if self.dolphin_interface.current_stage is None:
                checkbox_fillers = [
                    item
                    for item in self.items_queue
                    if ITEM_TABLE[LOOKUP_ID_TO_NAME[item.item]].type == KARItemType.CHECKBOX_FILLER
                ]
                if len(checkbox_fillers) > 0:
                    given_items = await self.give_items(checkbox_fillers)
                    for item in given_items:
                        self.items_queue.remove(item)

                # give patch cap increases
                patch_cap_increases = [
                    item
                    for item in self.items_queue
                    if ITEM_TABLE[LOOKUP_ID_TO_NAME[item.item]].type == KARItemType.PATCH_CAP_INCREASE
                ]
                if len(patch_cap_increases) > 0:
                    given_items = await self.give_items(patch_cap_increases)
                    for item in given_items:
                        self.items_queue.remove(item)

            # give items that were received/purchased while in a stage
            if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
                logger.info("in items give...")
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
            except asyncio.TimeoutError:
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


async def async_main(connect: Optional[str], password: Optional[str]) -> None:
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


def main(connect: Optional[str] = None, password: Optional[str] = None) -> None:
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
