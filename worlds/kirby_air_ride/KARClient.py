import asyncio
import time
import traceback
from typing import Any, List, Optional

import dolphin_memory_engine
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

from .Items import ITEM_TABLE, LOOKUP_ID_TO_NAME
from .Locations import (
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_LOOKUP_ID_TO_NAME,
    KARLocationType,
)

CONNECTION_REFUSED_GAME_STATUS = "Dolphin failed to connect. Please load an ISO for Kirby Air Ride. Trying again in 5 seconds..."
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Kirby Air Ride is running. Trying again in 5 seconds..."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

# Number of patches for player 1 is stored at these addresses. Values start at -2 float except for HP, which starts at 0
PLAYER_1_STAT_BOOST_PATCH_AMOUNT = 0x81578630
PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT = 0x81578634
PLAYER_1_STAT_TURN_PATCH_AMOUNT = 0x81578638
PLAYER_1_STAT_CHARGE_PATCH_AMOUNT = 0x8157863C
PLAYER_1_STAT_GLIDE_PATCH_AMOUNT = 0x81578640
PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT = 0x8157862C
PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT = 0x81578644
PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT = 0x81578648
PLAYER_1_STAT_HP_PATCH_AMOUNT = 0x8157864C

# TODO: find a true pointer or address to the current machine health. This address currently only works for some vehicles
# for whatever reason
# this is a float value from initially 0-100, that gets scaled by heart patches to be over 100.
# used to write to for death link
PLAYER_1_CURRENT_MACHINE_HP_ADDRESS = 0x8055AA30

# This address is used to check the player's health for DeathLink.
# this is a float value from initially 0-100, that gets scaled by heart patches to be over 100.
# always player HP, always reflects the PLAYER_1_CURRENT_MACHINE_HP_ADDRESS
# maybe read only? is overwritten every frame? but can still use to check actual current player HP
# is 0 for the entire time the player is off of a machine
PLAYER_1_CURRENT_HP_ADDRESS = 0x8055AA24

# Address that holds the currently selected menu
# This address is used to check the stage name to verify that the player is in-game before sending items.
# 00 = Air Ride, 01 = Top Ride, 02 = City Trial, 03 = Options, 04 = LAN
MENU_STAGE_ID_ADDR = 0x80535A0C
# this will be 9 for city trial, and only when in city trial
CURR_STAGE_ID_ADDR = 0x81333A64


class KARCommandProcessor(ClientCommandProcessor):
    """
    Command Processor for Kirby Air Ride client commands.

    This class handles commands specific to Kirby Air Ride.
    """

    def __init__(self, ctx: CommonContext) -> None:
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_dolphin(self) -> None:
        """
        Display the current Dolphin emulator connection status.
        """
        if isinstance(self.ctx, KARContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")

    def _cmd_deathlink(self) -> None:
        """
        Toggle deathlink from client. Overrides default setting.
        """
        if "DeathLink" in self.ctx.tags:
            Utils.async_start(
                self.ctx.update_death_link(False),
                name="Update Deathlink",
            )
            logger.info("Deathlink disabled.")
        else:
            Utils.async_start(
                self.ctx.update_death_link(True),
                name="Update Deathlink",
            )
            logger.info("Deathlink enabled.")


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

        :param server_address: Address of the Archipelago server.
        :param password: Password for server authentication.
        """

        super().__init__(server_address, password)
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.transitioned: bool = False
        self.goal: str = ""
        self.goal_checklist_amount: int = 0
        self.transitioned_time: float = 0

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        :param allow_autoreconnect: Allow the client to auto-reconnect to the server. Defaults to `False`.

        """
        self.auth = None
        await super().disconnect(allow_autoreconnect)

    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.

        :param password_requested: Whether the server requires a password. Defaults to `False`.
        """
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        """
        Handle incoming packages from the server.

        :param cmd: The command received from the server.
        :param args: The command arguments.
        """
        if cmd == "Connected":
            if "death_link" in args["slot_data"]:
                Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"])))
            # get the goal location from the slot data, which is included during generation
            if "goal" in args["slot_data"]:
                self.goal = args["slot_data"]["goal"]
            if "checklist_amount" in args["slot_data"]:
                self.goal_checklist_amount = int(args["slot_data"]["checklist_amount"])
            # reset local location checks so that a client that has already won its game but hasn't closed can't connect to a server
            # and accidentally auto-win. This doesn't solve the problem of using a save file that already has won, but does solve this smaller problem.
            self.locations_checked.clear()

        # ReceivedItems is a list of items that are in a guaranteed order.
        # {"index": 0, "items": [{"item_1"}, {"item_2"}]}
        # if the index is 0, the whole items list is sent.
        if cmd == "ReceivedItems":
            logger.debug("Got ReceivedItems packet, index: %s, items: %s", args["index"], args["items"])
            if args["index"] != 0:
                Utils.async_start(self.give_items(args["items"], False))
                Utils.async_start(self.update_server_items_received_index(args["index"]))

        # SetReply is sent when a server data storage key was updated by us with Set(), and we requested a
        # reply afterwards.
        if cmd == "SetReply":
            logger.debug(f"Got SetReply from the server: {args}")

    def give_death(self) -> None:
        """
        Trigger the player's death in-game by setting their current health to zero.

        :param ctx: Kirby Air Ride client context.
        """
        if (
            self.slot is not None
            and dolphin_memory_engine.is_hooked()
            and self.dolphin_status == CONNECTION_CONNECTED_STATUS
            and self.check_ingame_city_trial()
        ):
            write_pointer(PLAYER_1_CURRENT_MACHINE_HP_ADDRESS, 0xA78, 0)

    def on_deathlink(self, data: dict[str, Any]) -> None:
        """
        Handle a DeathLink event.

        :param data: The data associated with the DeathLink event.
        """
        super().on_deathlink(data)
        self.give_death()

    async def check_death(self) -> None:
        """
        Check if the player is currently dead in-game.
        If DeathLink is on, notify the server of the player's death.

        :return: `True` if the player is dead, otherwise `False`.
        """
        if (self.slot is not None) and self.check_ingame_city_trial():
            if not check_alive():
                logger.debug("player is not alive")
                # in city trial, give the player 2 minutes to get back on an air ride machine until death is
                # sent again
                # TODO: configurable option for length of time?
                # TODO: player can keep sending death by not getting on a vehicle. turn this into a trigger
                if time.time() >= self.last_death_link + 120:
                    await self.send_death(self.player_names[self.slot] + " exploded.")
                else:
                    logger.debug("did not send death (conditions not met)")

    async def send_victory(self) -> None:
        await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

    async def update_server_items_received_index(self, index: int) -> None:
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
        Iterate through all locations and check whether the player has checked each location.

        Update the server with all newly checked locations since the last update. If the player has completed the goal,
        notify the server.

        :param ctx: Kirby Air Ride client context.
        """
        for location, data in CITY_TRIAL_LOCATION_TABLE.items():
            checked = False
            if data.type == KARLocationType.CHECKLISTBOX:
                if data.mem_address is not None:
                    # 00 = locked, not visible
                    # 01 = flagged for unlocking
                    # 10 = locked, visible
                    # TODO: there seems to be one additional value the game uses sometimes that isn't included here
                    checked = bool(read_byte(data.mem_address) not in [0x00, 0x01, 0x10])

            if checked:
                # check for victory condition location
                if location == self.goal:
                    logger.debug(f"location: {location}, self.goal: {self.goal}")
                    if not self.finished_game:
                        self.finished_game = True
                        await self.send_victory()
                # TODO: can gate stadium unlocks and other locations by checking if we've received a "progressive stadium"
                # or similar item, and then re-writing the checked value to 0 if we haven't gotten that item yet.
                # elif "progressive stadium: drag race 4" in self.items_received:
                #     logger.debug("player has not received the progressive stadium required to progress. re-locking...")
                #     checked = False
                #     dolphin_memory_engine.write_byte(data.mem_address, 0x00)
                if data.code is not None:
                    self.locations_checked.add(data.code)

        # check for N checklist boxes filled victory condition
        if self.goal == "Fill in N Checklist Boxes!":
            logger.debug(
                f"len(self.locations_checked: {len(self.locations_checked)}, self.goal_checklist_amount: {self.goal_checklist_amount})"
            )
            if len(self.locations_checked) >= self.goal_checklist_amount:
                if not self.finished_game:
                    self.finished_game = True
                    await self.send_victory()

        # Send the list of newly-checked locations to the server.
        new_locations_checked = await self.check_locations(self.locations_checked)
        if new_locations_checked:
            logger.debug(
                "New locations checked and sent to server: %s",
                [f"{LOCATION_LOOKUP_ID_TO_NAME[location_id]} ({location_id})" for location_id in new_locations_checked],
            )

    def give_item(self, item_name: str) -> bool:
        """
        Give an item to the player in-game.

        :param ctx: Kirby Air Ride client context.
        :param item_name: Name of the item to give.
        :return: Whether the item was successfully given.
        """
        if not (self.check_ingame_city_trial() or time.time() < self.transitioned_time + 6):
            return False

        item_data = ITEM_TABLE[item_name]

        # Handle patches
        if item_data.type == "Patch":
            if "Up" in item_name:
                increment_player_patch(item_name, 1)
            if "Down" in item_name:
                increment_player_patch(item_name, -1)
        # Handle checkbox unlocks
        if item_data.type == "Checkbox Reward":
            pass
        # Handle progressive stadiums
        if item_data.type == "Progressive Stadium":
            # write 01 to the checkbox location corresponding to the next stadium unlock
            pass
        # Handle effects
        if "Effect" in item_data.type:
            apply_effect_item(item_name)

        return True

    async def give_items(self, items: List[NetworkItem], permanent_only: bool) -> None:
        """
        Give the player all outstanding items they have yet to receive.

        :param ctx: Kirby Air Ride client context.
        """
        for item in items:
            item_name = LOOKUP_ID_TO_NAME[item.item]
            if permanent_only:
                if "Permanent" in item_name:
                    while not self.give_item(item_name):
                        await asyncio.sleep(1)
            else:
                while not self.give_item(item_name):
                    await asyncio.sleep(1)

    async def check_transitioned(self) -> bool:
        """
        Check if the player has transitioned in or out of City Trial. If transitioning in, give the player any
        permanent patches they've collected.
        """
        in_city_trial = self.check_ingame_city_trial()
        if in_city_trial and not self.transitioned:
            logger.debug("transition into city trial detected")
            self.transitioned = True
            self.transitioned_time = time.time()
            logger.debug("applying permanent patches...")
            # TODO: fix this giving the player items again if they close and reopen the client.
            Utils.async_start(self.give_items(self.items_received, True))
        elif not in_city_trial and self.transitioned:
            logger.debug("transition out of city trial detected")
            self.transitioned = False

        return self.transitioned

    def check_ingame_city_trial(self) -> bool:
        """
        Check if the player is currently in-game in City Trial.

        :return: `True` if the player is in-game, otherwise `False`.
        """
        # city trial was selected at menu and the current stage address for city trial is 9
        menu_selected_city_trial = read_short(MENU_STAGE_ID_ADDR) == 0x0200
        in_city_trial = read_short(CURR_STAGE_ID_ADDR + 2) == 0x0009

        return menu_selected_city_trial and in_city_trial

    def make_gui(self):
        """
        Initialize the GUI for Kirby Air Ride client.

        :return: The client's GUI.
        """
        ui = super().make_gui()
        ui.base_title = "Archipelago Kirby Air Ride Client"
        return ui


def read_byte(console_address: int) -> int:
    """
    Read a byte from Dolphin memory.

    :param console_address: Address to read from.
    :return: The value read from memory.
    """

    # read_byte returns an int on windows
    return dolphin_memory_engine.read_byte(console_address)


def read_short(console_address: int) -> int:
    """
    Read a 2-byte short from Dolphin memory.

    :param console_address: Address to read from.
    :return: The value read from memory.
    """
    return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 2), byteorder="big")


def write_short(console_address: int, value: int) -> None:
    """
    Write a 2-byte short to Dolphin memory.

    :param console_address: Address to write to.
    :param value: Value to write.
    """
    dolphin_memory_engine.write_bytes(console_address, value.to_bytes(2, byteorder="big"))


def read_float(console_address: int) -> float:
    """
    Read a float from Dolphin memory.
    """
    return dolphin_memory_engine.read_float(console_address)


def write_float(console_address: int, value: float) -> None:
    """
    Write a float to Dolphin memory.
    """
    dolphin_memory_engine.write_float(console_address, value)


def read_pointer(console_address: int, offset: int, byte_count: int):
    """
    Follows the pointer at console_address and applies the given offset, then reads byte_count amount of bytes from it.

    :param console_address: Address of the pointer
    :param offset: Offset to apply when reading from the pointed location
    :param byte_count: number of byes to read
    """
    try:
        address = dolphin_memory_engine.follow_pointers(console_address, [0])
    except RuntimeError:
        return None

    address += offset
    return dolphin_memory_engine.read_bytes(address, byte_count)


def write_pointer(console_address: int, offset: int, value: int):
    """
    Follows the pointer at console_address and applies the given offset, then writes the value to it.

    :param console_address: Address of the pointer
    :param offset: Offset to apply when reading from the pointed location
    :param value: value to write
    """
    address = None
    try:
        address = dolphin_memory_engine.follow_pointers(console_address, [0])
    except RuntimeError:
        return None

    address += offset
    return dolphin_memory_engine.write_bytes(address, value.to_bytes(1))


def read_string(console_address: int, strlen: int) -> str:
    """
    Read a string from Dolphin memory.

    :param console_address: Address to start reading from.
    :param strlen: Length of the string to read.
    :return: The string.
    """
    return dolphin_memory_engine.read_bytes(console_address, strlen).split(b"\0", 1)[0].decode()


def increment_player_patch(item_name: str, delta: int) -> None:
    """
    Change the player patch count by delta.
    """

    if "Turn" in item_name:
        current_amount = read_float(PLAYER_1_STAT_TURN_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_TURN_PATCH_AMOUNT, current_amount + delta)
    elif "Boost" in item_name:
        current_amount = read_float(PLAYER_1_STAT_BOOST_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_BOOST_PATCH_AMOUNT, current_amount + delta)
    elif "Charge" in item_name:
        current_amount = read_float(PLAYER_1_STAT_CHARGE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_CHARGE_PATCH_AMOUNT, current_amount + delta)
    elif "Defense" in item_name:
        current_amount = read_float(PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT, current_amount + delta)
    elif "Glide" in item_name:
        current_amount = read_float(PLAYER_1_STAT_GLIDE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_GLIDE_PATCH_AMOUNT, current_amount + delta)
    elif "HP" in item_name:
        current_amount = read_float(PLAYER_1_STAT_HP_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_HP_PATCH_AMOUNT, current_amount + delta)
    elif "Weight" in item_name:
        current_amount = read_float(PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT, current_amount + delta)
    elif "Offense" in item_name:
        current_amount = read_float(PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT, current_amount + delta)
    elif "Top Speed" in item_name:
        current_amount = read_float(PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT, current_amount + delta)
    elif "All" in item_name:
        current_amount = read_float(PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_HP_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_HP_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_GLIDE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_GLIDE_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_CHARGE_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_CHARGE_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_BOOST_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_BOOST_PATCH_AMOUNT, current_amount + delta)
        current_amount = read_float(PLAYER_1_STAT_TURN_PATCH_AMOUNT)
        write_float(PLAYER_1_STAT_TURN_PATCH_AMOUNT, current_amount + delta)


def apply_effect_item(item_name: str) -> None:
    if item_name == "1 HP":
        write_float(PLAYER_1_CURRENT_MACHINE_HP_ADDRESS, 1)


def check_alive() -> bool:
    """
    Check if the player is currently alive in-game.

    :return: `True` if the player is alive, otherwise `False`.
    """
    cur_health = read_float(PLAYER_1_CURRENT_HP_ADDRESS)
    return cur_health > float(0)


def check_game_running() -> bool:
    """
    Check if the game is running within Dolphin.

    :return: `True` if the game is running, otherwise `False`.
    """
    return dolphin_memory_engine.read_bytes(0x80000000, 6) == b"GKYE01"


async def handle_connected_state(ctx: "KARContext") -> None:
    """Handle the logic when Dolphin is connected."""
    if ctx.slot is not None:
        await ctx.check_transitioned()

        if ctx.check_ingame_city_trial() and time.time() >= ctx.transitioned_time + 6:
            if "DeathLink" in ctx.tags:
                await ctx.check_death()

        await ctx.send_check_locations()


async def handle_disconnected_state(ctx: "KARContext") -> None:
    """Handle the logic when Dolphin is disconnected."""
    if ctx.dolphin_status != CONNECTION_CONNECTED_STATUS:
        logger.info(CONNECTION_LOST_STATUS)
        ctx.dolphin_status = CONNECTION_LOST_STATUS

    logger.info("Attempting to connect to Dolphin...")
    await attempt_dolphin_connection(ctx)


async def attempt_dolphin_connection(ctx: "KARContext") -> bool:
    """Try to establish a connection to Dolphin and return whether successful."""
    dolphin_memory_engine.hook()

    if dolphin_memory_engine.is_hooked():
        if not check_game_running():
            logger.info(CONNECTION_REFUSED_GAME_STATUS)
            ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
            dolphin_memory_engine.un_hook()
            await asyncio.sleep(5)
            return False

        logger.info(CONNECTION_CONNECTED_STATUS)
        ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
        return True

    logger.info(CONNECTION_LOST_STATUS)
    ctx.dolphin_status = CONNECTION_LOST_STATUS
    await asyncio.sleep(5)
    return False


async def dolphin_sync_task(ctx: KARContext) -> None:
    """
    The task loop for managing the connection to Dolphin.

    While connected, read the emulator's memory to look for any relevant changes made by the player in the game.

    :param ctx: Kirby Air Ride client context.
    """
    logger.info("Starting Dolphin connector. Use /dolphin for status information.")

    while not ctx.exit_event.is_set():
        try:
            # ctx.watcher_event gets set when receiving ReceivedItems or LocationInfo, or when shutting down.
            await asyncio.wait_for(ctx.watcher_event.wait(), 1)
        except asyncio.TimeoutError:
            pass
        finally:
            ctx.watcher_event.clear()

        try:
            if dolphin_memory_engine.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                await handle_connected_state(ctx)
            else:
                await handle_disconnected_state(ctx)
        except Exception:
            dolphin_memory_engine.un_hook()
            logger.info(CONNECTION_LOST_STATUS)
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            logger.error(traceback.format_exc())
            continue


def main(connect: Optional[str] = None, password: Optional[str] = None) -> None:
    """
    Run the main async loop for the Kirby Air Ride client.

    :param connect: Address of the Archipelago server.
    :param password: Password for server authentication.
    """
    Utils.init_logging("Kirby Air Ride Client")

    async def _main(connect: Optional[str], password: Optional[str]) -> None:
        ctx = KARContext(connect, password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        await asyncio.sleep(1)

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="dolphin sync")

        await ctx.exit_event.wait()
        # Wake the sync task, if it is currently sleeping, so it can start shutting down when it sees that the
        # exit_event is set.
        ctx.watcher_event.set()

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await ctx.dolphin_sync_task

    import colorama

    colorama.init()
    asyncio.run(_main(connect, password))
    colorama.deinit()


if __name__ == "__main__":
    parser = get_base_parser()
    args = parser.parse_args()
    main(args.connect, args.password)
