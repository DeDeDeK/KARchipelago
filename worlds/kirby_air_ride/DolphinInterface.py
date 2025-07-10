import time
from enum import Enum
from typing import Optional

import dolphin_memory_engine

from CommonClient import logger

# Player 1 stat patch addresses
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

# this address holds a pointer to a value that then needs an offset of 0xA78 applied to get to the player's
# current machine health.
# float value from initially 0-100, that gets scaled by heart patches to be over 100.
# used to write to for death link
# TODO: find a true pointer or address to the current machine health. This address currently only works for some vehicles or
# some of the time
PLAYER_1_CURRENT_MACHINE_HP_ADDRESS = 0x8055AA30

# This address is used to check the player's health for DeathLink.
# this is a float value from initially 0-100, that gets scaled by heart patches to be over 100.
# always player HP, always reflects the PLAYER_1_CURRENT_MACHINE_HP_ADDRESS
# maybe read only? is overwritten every frame but can still use to check actual current player HP
# is 0 for the entire time the player is off of a machine
PLAYER_1_CURRENT_HP_ADDRESS = 0x8055AA24
# max health of the player. overwritten every frame, so effectively read-only. float value.
PLAYER_1_CURRENT_MAX_HP_ADDRESS = 0x8055AA28

# Game state addresses
# Address that holds the currently selected menu
# This address is used to check the stage name to verify that the player is in-game before sending items.
# 00 = Air Ride, 01 = Top Ride, 02 = City Trial, 03 = Options, 04 = LAN
MENU_STAGE_ID_ADDR = 0x80535A0C
# this will be 9 for city trial, and only when in city trial
CURR_STAGE_ID_ADDR = 0x81333A64

# Constants for memory checking
CITY_TRIAL_MENU_SELECTION = 0x0200
CITY_TRIAL_STAGE_ID = 0x0009
KAR_GAME_ID = b"GKYE01"

# Memory access error messages
MEMORY_READ_ERROR = "Failed to read {type} at {addr}: {error}"
MEMORY_WRITE_ERROR = "Failed to write {type} at {addr}: {error}"


class PatchType(Enum):
    """Types of patches that can be applied to player stats."""

    TURN = "Turn"
    BOOST = "Boost"
    CHARGE = "Charge"
    DEFENSE = "Defense"
    GLIDE = "Glide"
    HP = "HP"
    WEIGHT = "Weight"
    OFFENSE = "Offense"
    TOP_SPEED = "Top Speed"
    ALL = "All"


PATCH_ADDRESS_MAP = {
    PatchType.TURN: PLAYER_1_STAT_TURN_PATCH_AMOUNT,
    PatchType.BOOST: PLAYER_1_STAT_BOOST_PATCH_AMOUNT,
    PatchType.CHARGE: PLAYER_1_STAT_CHARGE_PATCH_AMOUNT,
    PatchType.DEFENSE: PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT,
    PatchType.GLIDE: PLAYER_1_STAT_GLIDE_PATCH_AMOUNT,
    PatchType.HP: PLAYER_1_STAT_HP_PATCH_AMOUNT,
    PatchType.WEIGHT: PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT,
    PatchType.OFFENSE: PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT,
    PatchType.TOP_SPEED: PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT,
}


def get_patch_type_from_item_name(item_name: str) -> Optional[PatchType]:
    """
    Determine the patch type from an item name.

    Args:
        item_name: Name of the item

    Returns:
        The patch type or None if no match
    """
    for patch_type in PatchType:
        if patch_type.value in item_name:
            return patch_type
    return None


class DolphinInterface:
    """Interface for all interactions with the Dolphin emulator."""

    def __init__(self) -> None:
        """Initialize the Dolphin interface with default values."""
        self.transitioned_time: float = time.time()
        self.transition_wait: int = 6
        self.transitioned: bool = False
        pass

    def hook(self) -> bool:
        """
        Establish a connection to Dolphin memory.

        Returns:
            Whether the connection was successful
        """
        try:
            dolphin_memory_engine.hook()
            return dolphin_memory_engine.is_hooked()
        except Exception as e:
            logger.warning(f"Failed to hook into Dolphin: {e}")
            return False

    def unhook(self) -> None:
        """Disconnect from Dolphin memory."""
        try:
            if dolphin_memory_engine.is_hooked():
                dolphin_memory_engine.un_hook()
        except Exception as e:
            logger.warning(f"Error while unhooking from Dolphin: {e}")

    def is_hooked(self) -> bool:
        """
        Check if currently connected to Dolphin memory.

        Returns:
            Whether currently hooked to Dolphin
        """
        return dolphin_memory_engine.is_hooked()

    def read_byte(self, console_address: int) -> int:
        """Read a single byte from Dolphin memory."""
        try:
            # returns an int
            return dolphin_memory_engine.read_byte(console_address)
        except Exception as e:
            logger.warning(MEMORY_READ_ERROR.format(type="byte", addr=hex(console_address), error=str(e)))
            return 0

    def read_bytes(self, console_address: int, num_bytes: int) -> bytes:
        """Read multiple bytes from Dolphin memory."""
        try:
            # returns bytes
            return dolphin_memory_engine.read_bytes(console_address, num_bytes)
        except Exception as e:
            logger.warning(MEMORY_READ_ERROR.format(type=f"{num_bytes} bytes", addr=hex(console_address), error=str(e)))
            return b""

    def read_short(self, console_address: int) -> int:
        """Read a 2-byte short from Dolphin memory."""
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 2), byteorder="big")
        except Exception as e:
            logger.warning(MEMORY_READ_ERROR.format(type="short", addr=hex(console_address), error=str(e)))
            return 0

    def read_float(self, console_address: int) -> float:
        """Read a float value from Dolphin memory."""
        try:
            # returns a float
            return dolphin_memory_engine.read_float(console_address)
        except Exception as e:
            logger.warning(MEMORY_READ_ERROR.format(type="float", addr=hex(console_address), error=str(e)))
            return 0.0

    def write_short(self, console_address: int, value: int) -> bool:
        """
        Write a 2-byte short to Dolphin memory.

        Returns:
            Whether the write operation was successful
        """
        try:
            dolphin_memory_engine.write_bytes(console_address, value.to_bytes(2, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(MEMORY_WRITE_ERROR.format(type="short", addr=hex(console_address), error=str(e)))
            return False

    def write_float(self, console_address: int, value: float) -> bool:
        """
        Write a float value to Dolphin memory.

        Returns:
            Whether the write operation was successful
        """
        try:
            # value can be an int or a float
            dolphin_memory_engine.write_float(console_address, value)
            return True
        except Exception as e:
            logger.warning(MEMORY_WRITE_ERROR.format(type="float", addr=hex(console_address), error=str(e)))
            return False

    def read_pointer(self, console_address: int, offset: int, byte_count: int) -> Optional[bytes]:
        """
        Follow the pointer at console_address and apply the given offset, then read byte_count amount of bytes from it.

        Args:
            console_address: Address of the pointer
            offset: Offset to apply when reading from the pointed location
            byte_count: number of bytes to read

        Returns:
            Bytes read from memory or None if operation failed
        """
        try:
            address = dolphin_memory_engine.follow_pointers(console_address, [0])
            address += offset
            return self.read_bytes(address, byte_count)
        except Exception as e:
            logger.warning(MEMORY_READ_ERROR.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e)))
            return None

    def write_pointer_byte(self, console_address: int, offset: int, value: int) -> bool:
        """
        Follow the pointer at console_address and apply the given offset, then write the value to it.

        Args:
            console_address: Address of the pointer
            offset: Offset to apply when reading from the pointed location
            value: value to write (1 byte)

        Returns:
            Whether the write operation was successful
        """
        try:
            address = dolphin_memory_engine.follow_pointers(console_address, [0])
            address += offset
            dolphin_memory_engine.write_bytes(address, value.to_bytes(1, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(MEMORY_WRITE_ERROR.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e)))
            return False

    def write_pointer_float(self, console_address: int, offset: int, value: float) -> bool:
        """
        Follow the pointer at console_address and apply the given offset, then write the value to it.

        Args:
            console_address: Address of the pointer
            offset: Offset to apply when reading from the pointed location
            value: value to write (float)

        Returns:
            Whether the write operation was successful
        """
        try:
            address = dolphin_memory_engine.follow_pointers(console_address, [0])
            address += offset
            dolphin_memory_engine.write_float(address, value)
            return True
        except Exception as e:
            logger.warning(MEMORY_WRITE_ERROR.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e)))
            return False

    def increment_player_patch(self, item_name: str, delta: int) -> None:
        """
        Change the player patch count by delta.

        Args:
            item_name: Name of the item to apply patch for
            delta: Amount to change the patch value (positive or negative)
        """
        patch_type = get_patch_type_from_item_name(item_name)
        if patch_type is None:
            logger.warning(f"Unrecognized patch type in item: {item_name}")
            return

        # Handle "ALL" patch type which updates all stats
        if patch_type == PatchType.ALL:
            for addr in PATCH_ADDRESS_MAP.values():
                current = self.read_float(addr)
                self.write_float(addr, current + delta)
        else:
            # Handle specific patch type
            addr = PATCH_ADDRESS_MAP.get(patch_type)
            if addr is not None:
                current = self.read_float(addr)
                self.write_float(addr, current + delta)

    def apply_effect_item(self, item_name: str) -> None:
        """
        Apply special effect items.

        Args:
            item_name: Name of the effect item to apply
        """
        match item_name:
            case "1 HP":
                self.write_pointer_float(PLAYER_1_CURRENT_MACHINE_HP_ADDRESS, 0xA78, 1)
            case "Full Heal":
                current_max_hp = self.read_float(PLAYER_1_CURRENT_MAX_HP_ADDRESS)
                self.write_pointer_float(PLAYER_1_CURRENT_MACHINE_HP_ADDRESS, 0xA78, current_max_hp)

    def check_alive(self) -> bool:
        """
        Check if the player is currently alive in-game.

        Returns:
            True if the player is alive, False otherwise
        """
        return self.read_float(PLAYER_1_CURRENT_HP_ADDRESS) > 0.0

    def give_death(self) -> None:
        """Trigger the player's death in-game by setting their current health to zero."""
        self.write_pointer_float(PLAYER_1_CURRENT_MACHINE_HP_ADDRESS, 0xA78, 0)

    def check_game_running(self) -> bool:
        """
        Check if the game is running within Dolphin.

        Returns:
            True if the game is running, False otherwise
        """
        return self.read_bytes(0x80000000, 6) == KAR_GAME_ID

    def is_in_city_trial(self) -> bool:
        """
        Check if the player is currently in City Trial mode.

        Returns:
            True if in City Trial, False otherwise
        """
        menu_selection = self.read_short(MENU_STAGE_ID_ADDR) == CITY_TRIAL_MENU_SELECTION
        current_stage = self.read_short(CURR_STAGE_ID_ADDR + 2) == CITY_TRIAL_STAGE_ID

        return menu_selection and current_stage

    def check_transition(self) -> bool:
        """
        Detect a transition into city trial.

        Returns:
            True ONLY IF a transition INTO City Trial has happened.
        """
        trigger = False
        # Detect transition into City Trial
        if self.is_in_city_trial() and not self.transitioned:
            logger.debug("transition into city trial detected")
            trigger = True
            self.transitioned = True
            self.transitioned_time = time.time()
        # Detect transition out of City Trial
        elif not self.is_in_city_trial() and self.transitioned:
            logger.debug("transition out of city trial detected")
            self.transitioned = False

        return trigger

    def transition_waited(self) -> bool:
        """
        Check if the transition time wait after entering City Trial has elapsed.

        Returns:
            True if the wait time has elapsed.
        """
        return time.time() >= self.transitioned_time + self.transition_wait
