import asyncio
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

from .DolphinInterface import DolphinInterface, PatchType, StageType, get_patch_type_from_item_name
from .Items import ITEM_TABLE, LOOKUP_ID_TO_NAME
from .KAROptions import AirRideGoal, CityTrialGoal
from .Locations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_LOOKUP_ID_TO_NAME,
    KARLocationType,
)

# Connection status messages
CONNECTION_REFUSED_GAME_STATUS = "Dolphin failed to connect. Please make sure your emulator is running and load an ISO for Kirby Air Ride. Trying again in 5 seconds..."
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

# Constants for game state
DEATH_LINK_COOLDOWN = 120  # seconds
DOLPHIN_RECONNECT_DELAY = 5  # seconds
ENERGYLINK_ITEM_COST = 10  # Joules

CLIENT_VERSION = "v0.3.0"


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
    items_handling = 0b111  # receive items from starting inventory, our own world, and other worlds
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
        self.dolphin_interface = DolphinInterface()
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.city_trial_enabled: bool = False
        self.city_trial_goal: str = ""
        self.city_trial_goal_checklist_amount: int = 0
        self.city_trial_goal_acheived: bool = False
        self.air_ride_enabled: bool = False
        self.air_ride_goal: str = ""
        self.air_ride_goal_checklist_amount: int = 0
        self.air_ride_goal_acheived: bool = False
        self.items_queue: List[NetworkItem] = []
        self.energy_link_enabled: bool = False
        self.energy_link_items_queue: list[int] = []
        self.death_link_enabled: bool = False

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

            if "city_trial_checklist_amount" in args["slot_data"]:
                self.city_trial_goal_checklist_amount = int(args["slot_data"]["city_trial_checklist_amount"])

            if "air_ride_checklist_amount" in args["slot_data"]:
                self.air_ride_goal_checklist_amount = int(args["slot_data"]["air_ride_checklist_amount"])

            # reset local location checks so that a client that has already won its game but hasn't closed can't connect to a server
            # and accidentally auto-win. This doesn't solve the problem of using a save file that already has won, but does solve this smaller problem.
            self.locations_checked.clear()

        # ReceivedItems is a list of items that are in a guaranteed order.
        # {"index": 0, "items": [{"item_1"}, {"item_2"}]}
        # if the index is 0, the whole items list is sent.
        if cmd == "ReceivedItems":
            logger.debug("Got ReceivedItems packet, index: %s, items: %s", args["index"], args["items"])
            if args["index"] != 0:
                self.items_queue.extend(args["items"])

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
        if not self.dolphin_interface.check_alive():
            logger.debug("player is not alive")
            # in city trial, give the player 2 minutes to get back on an air ride machine until death is sent again
            # TODO: configurable option for length of time?
            # TODO: player can keep sending death by not getting on a vehicle. turn this into a trigger
            if time.time() >= self.last_death_link + DEATH_LINK_COOLDOWN and self.slot is not None:
                await self.send_death(self.player_names[self.slot] + " exploded.")
            else:
                logger.debug("did not send death (cooldown not elapsed)")

    async def send_victory(self) -> None:
        """Send a message to the server that the player has completed their goal."""
        await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

    async def update_server_items_received_index(self, index: int) -> None:
        """
        Update the server with the index of the last received item.

        Args:
            index: Index of the last received item
        """
        logger.debug(f"Sending server data storage update for items received index: {index}...")
        await self.send_msgs(
            [
                {
                    "cmd": "Set",
                    "key": "last_received_index",
                    "default": 0,
                    "want_reply": True,
                    "operations": [{"operation": "replace", "value": index}],
                }
            ]
        )

    async def send_check_locations(self) -> None:
        """
        Check all locations and notify the server of any newly checked locations.
        If the goal has been completed, notify the server of victory.
        """
        # Check City Trial Checklist if City Trial is enabled
        if self.city_trial_enabled:
            for location, data in CITY_TRIAL_LOCATION_TABLE.items():
                checked = False
                if data.type == KARLocationType.CHECKLISTBOX and data.mem_address is not None:
                    # 00 = locked, not visible
                    # 01 = flagged for unlocking
                    # 10 = locked, visible
                    # TODO: there seems to be one additional value the game uses sometimes that isn't included here
                    checked = bool(self.dolphin_interface.read_byte(data.mem_address) not in [0x00, 0x01, 0x10])

                if checked:
                    # TODO: can gate stadium unlocks and other locations by checking if we've received a "progressive stadium"
                    # or similar item, and then re-writing the checked value to 0 if we haven't gotten that item yet.
                    # if not [LOOKUP_ID_TO_NAME[item.item] for item in self.items_received]:
                    #     logger.debug("player has not received the progressive stadium required to progress. re-locking...")
                    #     checked = False
                    #     self.dolphin_interface.write_byte(data.mem_address, 0x00)
                    #     continue
                    if data.code is not None:
                        self.locations_checked.add(data.code)

            # check goals
            if not (self.city_trial_goal_acheived or self.finished_game):
                # Check for victory condition location
                if self.city_trial_goal != CityTrialGoal.option_n_checklist_blocks:
                    if CITY_TRIAL_LOCATION_TABLE[self.city_trial_goal].code in self.locations_checked:
                        logger.info(f"Victory location found for City Trial: {location}")
                        self.city_trial_goal_acheived = True

                # check for n checklist blocks goal victory
                if (
                    self.city_trial_goal == CityTrialGoal.option_n_checklist_blocks
                    and len(self.locations_checked) >= self.city_trial_goal_checklist_amount
                ):
                    logger.info(
                        f"N Checklist Blocks Goal Acheived for City Trial - locations checked: {len(self.locations_checked)} goal amount: {self.city_trial_goal_checklist_amount} "
                    )
                    self.city_trial_goal_acheived = True

        # Check Air Ride Checklist if Air Ride is enabled
        if self.air_ride_enabled:
            for location, data in AIR_RIDE_LOCATION_TABLE.items():
                checked = False
                if data.type == KARLocationType.CHECKLISTBOX and data.mem_address is not None:
                    # 00 = locked, not visible
                    # 01 = flagged for unlocking
                    # 10 = locked, visible
                    # TODO: there seems to be one additional value the game uses sometimes that isn't included here
                    checked = bool(self.dolphin_interface.read_byte(data.mem_address) not in [0x00, 0x01, 0x10])

                if checked:
                    if data.code is not None:
                        self.locations_checked.add(data.code)

            # check goals
            if not (self.air_ride_goal_acheived or self.finished_game):
                # Check for victory condition location
                if self.air_ride_goal != AirRideGoal.option_n_checklist_blocks:
                    if AIR_RIDE_LOCATION_TABLE[self.air_ride_goal].code in self.locations_checked:
                        logger.info(f"Victory location found for Air Ride: {location}")
                        self.air_ride_goal_acheived = True

                # check for n checklist blocks goal victory
                if (
                    self.air_ride_goal == AirRideGoal.option_n_checklist_blocks
                    and len(self.locations_checked) >= self.air_ride_goal_checklist_amount
                ):
                    logger.info(
                        f"N Checklist Blocks Goal Acheived for Air Ride - locations checked: {len(self.locations_checked)} goal amount: {self.air_ride_goal_checklist_amount} "
                    )
                    self.air_ride_goal_acheived = True

        # determine if overall goal has been acheived
        if not self.finished_game:
            if self.city_trial_enabled:
                if self.air_ride_enabled:
                    if self.city_trial_goal_acheived and self.air_ride_goal_acheived:
                        self.finished_game = True
                        await self.send_victory()
                else:
                    if self.city_trial_goal_acheived:
                        self.finished_game = True
                        await self.send_victory()
            if self.air_ride_enabled:
                if self.city_trial_enabled:
                    if self.air_ride_goal_acheived and self.city_trial_goal_acheived:
                        self.finished_game = True
                        await self.send_victory()
                else:
                    if self.air_ride_goal_acheived:
                        self.finished_game = True
                        await self.send_victory()

        # Send newly checked locations to the server
        new_locations_checked = await self.check_locations(self.locations_checked)
        if new_locations_checked:
            logger.debug(
                "New locations checked and sent to server: %s",
                [f"{LOCATION_LOOKUP_ID_TO_NAME[location_id]} ({location_id})" for location_id in new_locations_checked],
            )

    def give_item(self, item: NetworkItem) -> None:
        """
        Give an item to the player in-game. Removes the item from the item queue only if it was given.

        Args:
            item: NetworkItems
        """
        item_name = LOOKUP_ID_TO_NAME[item.item]
        item_data = ITEM_TABLE[item_name]

        match item_data.type:
            case "Patch":
                if self.dolphin_interface.current_stage == StageType.CITY_TRIAL:
                    delta = 1 if "Up" in item_name else -1
                    self.dolphin_interface.increment_player_patch(item_name, delta)
                    self.items_queue.remove(item)
            case "Checkbox Reward":
                pass
            case "Progressive Stadium":
                # determine the next progressive stadium in logic
                # write 01 to the checkbox location corresponding to the next stadium unlock to flag it for unlocking
                pass
            case "Effect":
                if self.dolphin_interface.current_stage in (
                    StageType.CITY_TRIAL,
                    StageType.STADIUM_DESTRUCTION_DERBY_1,
                    StageType.STADIUM_DESTRUCTION_DERBY_2,
                    StageType.STADIUM_DESTRUCTION_DERBY_3,
                    StageType.STADIUM_DESTRUCTION_DERBY_4,
                    StageType.STADIUM_DESTRUCTION_DERBY_5,
                    StageType.STADIUM_VS_KING_DEDEDE,
                ):
                    self.dolphin_interface.apply_effect_item(item_name)
                    self.items_queue.remove(item)

    async def give_items(self, items: List[NetworkItem]) -> None:
        """
        Give the player all outstanding items they have yet to receive.

        Args:
            items: The list of NetworkItems from the server.
        """
        for item in items:
            self.give_item(item)

    async def shutdown(self) -> None:
        """Shutdown the client and clean up resources."""
        # Unhook from Dolphin if still hooked
        if self.dolphin_interface.is_hooked():
            self.dolphin_interface.unhook()

        # Continue with parent shutdown
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
        Removes the given amount of energy for energylink.
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
        Check if the player has received patches and update the energy link value accordingly. Additionally,
        add spent items to the item queue.

        Energylink value is increased for each patch a player collects.
        """
        energy = 0

        if self.dolphin_interface.current_stage == StageType.CITY_TRIAL:
            # shallow copy of original to preserve old count values
            old_counts = dict(self.dolphin_interface.player_1_patches)

            # get new player patch counts
            self.dolphin_interface.update_player_patch_counts()

            # TODO: fix this giving energy from items received from /energylink_spend
            # TODO: fix this (sometimes) giving energy for permanent patches when transitioning into City Trial
            # (likely races with item_give after transition?)
            diff = 0
            for patch_type, patch_count in self.dolphin_interface.player_1_patches.items():
                if patch_count > old_counts[patch_type]:
                    diff += patch_count - old_counts[patch_type]
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

        # if there are items that have been aquired by spending energy, queue those to be received
        if len(self.energy_link_items_queue) > 0:
            for item_id in self.energy_link_items_queue:
                self.items_queue.append(NetworkItem(item_id, 0, 0, 0))
            self.energy_link_items_queue.clear()

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

        cost = ENERGYLINK_ITEM_COST * int(amount)
        if get_patch_type_from_item_name(item_name) == PatchType.ALL:
            # ALL patches cost 9x as much
            cost = ENERGYLINK_ITEM_COST * 9 * int(amount)

        if self.current_energy_link_value < cost:
            logger.info(f"Not enough energy. Current value: {self.current_energy_link_value} Need: {cost}")
            return

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
        ui.base_title = f"Archipelago Kirby Air Ride Client ({CLIENT_VERSION})"
        return ui

    async def handle_connected_state(self) -> None:
        """Handle the logic when Dolphin is connected."""
        if self.slot is None:
            return

        # update current_stage and check if a transition into a stage has happend
        stage_type, transition_trigger = self.dolphin_interface.check_transition()
        if transition_trigger:
            # queue up permanent patches if player has transitioned into City Trial
            # TODO: fix this giving the player items again if they close and reopen the client.
            if stage_type == StageType.CITY_TRIAL:
                logger.debug("queueing permanent patches...")
                # skip adding permanent patches to the item queue if they are already in it (from ReceivedItems)
                items = [
                    item
                    for item in self.items_received
                    if "Permanent" in LOOKUP_ID_TO_NAME[item.item] and item not in self.items_queue
                ]
                self.items_queue.extend(items)

        # handle energylink for the current stage
        if self.energy_link_enabled:
            if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
                logger.debug("in energylink update...")
                await self.update_energy_link()

        # check for death when in any stage and past transition period
        if self.death_link_enabled:
            if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
                logger.debug("in deathlink check...")
                await self.check_death()

        # check if any items are in the items queue and apply them if we're in game
        if len(self.items_queue) > 0:
            if self.dolphin_interface.current_stage is not None and self.dolphin_interface.transition_waited():
                logger.debug("in items give...")
                await self.give_items(self.items_queue)
                # self.items_queue.clear()

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
                self.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                logger.info(self.dolphin_status)
                await asyncio.sleep(DOLPHIN_RECONNECT_DELAY)
                return False

            self.dolphin_status = CONNECTION_CONNECTED_STATUS
            logger.info(self.dolphin_status)
            return True

        self.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
        logger.info(self.dolphin_status)
        await asyncio.sleep(DOLPHIN_RECONNECT_DELAY)
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
                    and self.dolphin_status == CONNECTION_CONNECTED_STATUS
                ):
                    await self.handle_connected_state()
                else:
                    self.dolphin_interface.unhook()
                    await self.handle_disconnected_state()
            except Exception as e:
                if self.dolphin_interface.is_hooked():
                    self.dolphin_interface.unhook()
                self.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
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
