import time
from enum import Enum
from typing import NamedTuple, Optional, Tuple

import dolphin_memory_engine

from CommonClient import logger

KAR_GAME_ID = b"GKYE01"

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

# number of things destroyed:
# trees, rocks, coral, houses, star pole, volcano entrances, underground walls
# Byte value. Starts at 00. Reset only when entering City Trial.
PLAYER_1_DESTRUCTION_COUNT_ADDRESS = 0x8055B2A3

# number of total laps in the current Air Ride course.
# Byte value. Initialized as 1, then 0 when choosing courses, then the value of laps for the course.
PLAYER_1_AIR_RIDE_TOTAL_LAP_COUNT_ADDRESS = 0x80536472

# Address that holds the currently selected menu
# This address is used to check the stage name to verify that the player is in-game before sending items.
# 00 = Air Ride, 01 = Top Ride, 02 = City Trial, 03 = Options, 04 = LAN
MENU_STAGE_ID_ADDR = 0x80535A0C

# the current stage the player is in
# this is a pointer to a 4 byte word. an offset of 4 needs to be applied to get to the address of the current stage.
# TODO: this pointer hops around all over the place, but does always end up pointing to the right thing. Solve this
# by doing a rolling average of the last 5 or 6 readings and maybe put them into a set or something and test if there
# is only one unique value in it to guarantee we are in a stage. Have to think about transitioning out of stages too though,
# that needs to be quicker. Alternative is finding the pointed-to address for every stage, as those seem to be the same
# every time.
# before main menu: very high positive or negative numbers, jumping around
# on main menu: 22
# after main menu but not in a stage: uninitialized
# after exiting a stage: 0, but can randomly be high positive or negative numbers at any time
CURR_STAGE_ID_ADDR = 0x805DD6CC

# menu selection IDs for all stages
AIR_RIDE_MENU_SELECTION = 0x00
TOP_RIDE_MENU_SELECTION = 0x01
CITY_TRIAL_MENU_SELECTION = 0x02

# stage IDs for all stages
MAIN_MENU_STAGE_ID = 22
CITY_TRIAL_STAGE_ID = 9
STADIUM_DRAG_RACE_1_STAGE_ID = 13
STADIUM_DRAG_RACE_2_STAGE_ID = 11
STADIUM_DRAG_RACE_3_STAGE_ID = 10
STADIUM_DRAG_RACE_4_STAGE_ID = 12
STADIUM_HIGH_JUMP_STAGE_ID = 18
STADIUM_TARGET_FLIGHT_STAGE_ID = 19
STADIUM_AIR_GLIDER_STAGE_ID = 20
STADIUM_DESTRUCTION_DERBY_1_STAGE_ID = 15
STADIUM_DESTRUCTION_DERBY_2_STAGE_ID = 16
STADIUM_DESTRUCTION_DERBY_3_STAGE_ID = 21
STADIUM_DESTRUCTION_DERBY_4_STAGE_ID = 9  # this will cause a conflict
STADIUM_DESTRUCTION_DERBY_5_STAGE_ID = 9  # this will cause a conflict
STADIUM_KIRBY_MELEE_1_STAGE_ID = 14
STADIUM_KIRBY_MELEE_2_STAGE_ID = 17
# STADIUM_SINGLE_RACE_1_STAGE_ID = 0x00000000
STADIUM_SINGLE_RACE_2_STAGE_ID = 1
STADIUM_SINGLE_RACE_3_STAGE_ID = 2
STADIUM_SINGLE_RACE_4_STAGE_ID = 8
STADIUM_SINGLE_RACE_5_STAGE_ID = 7
STADIUM_SINGLE_RACE_6_STAGE_ID = 4
STADIUM_SINGLE_RACE_7_STAGE_ID = 5
STADIUM_SINGLE_RACE_8_STAGE_ID = 3
STADIUM_SINGLE_RACE_9_STAGE_ID = 6
STADIUM_VS_KING_DEDEDE_STAGE_ID = 15
# FANTASY_MEADOWS_STAGE_ID = 0x00000000
CELESTIAL_VALLEY_STAGE_ID = 4
SKY_SANDS_STAGE_ID = 2
FROZEN_HILLSIDE_STAGE_ID = 8
MAGMA_FLOWS_STAGE_ID = 1
BEANSTALK_PARK_STAGE_ID = 7
MACHINE_PASSAGE_STAGE_ID = 5
CHECKER_KNIGHTS_STAGE_ID = 3
NEBULA_BELT_STAGE_ID = 6


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


PATCH_ADDRESS_MAP: dict[PatchType, int] = {
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


class StageType(Enum):
    """Types of stages in the game"""

    CITY_TRIAL = NamedTuple("CITY_TRIAL", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, CITY_TRIAL_STAGE_ID
    )
    STADIUM_DRAG_RACE_1 = NamedTuple("STADIUM_DRAG_RACE_1", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_DRAG_RACE_1_STAGE_ID
    )
    STADIUM_DRAG_RACE_2 = NamedTuple("STADIUM_DRAG_RACE_2", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_DRAG_RACE_2_STAGE_ID
    )
    STADIUM_DRAG_RACE_3 = NamedTuple("STADIUM_DRAG_RACE_3", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_DRAG_RACE_3_STAGE_ID
    )
    STADIUM_DRAG_RACE_4 = NamedTuple("STADIUM_DRAG_RACE_4", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_DRAG_RACE_4_STAGE_ID
    )
    STADIUM_HIGH_JUMP = NamedTuple("STADIUM_HIGH_JUMP", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_HIGH_JUMP_STAGE_ID
    )
    STADIUM_TARGET_FLIGHT = NamedTuple("STADIUM_TARGET_FLIGHT", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_TARGET_FLIGHT_STAGE_ID
    )
    STADIUM_AIR_GLIDER = NamedTuple("STADIUM_AIR_GLIDER", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_AIR_GLIDER_STAGE_ID
    )
    STADIUM_DESTRUCTION_DERBY_1 = NamedTuple(
        "STADIUM_DESTRUCTION_DERBY_1", [("menu_selection_id", int), ("stage_id", int)]
    )(CITY_TRIAL_MENU_SELECTION, STADIUM_DESTRUCTION_DERBY_1_STAGE_ID)
    STADIUM_DESTRUCTION_DERBY_2 = NamedTuple(
        "STADIUM_DESTRUCTION_DERBY_2", [("menu_selection_id", int), ("stage_id", int)]
    )(CITY_TRIAL_MENU_SELECTION, STADIUM_DESTRUCTION_DERBY_2_STAGE_ID)
    STADIUM_DESTRUCTION_DERBY_3 = NamedTuple(
        "STADIUM_DESTRUCTION_DERBY_3", [("menu_selection_id", int), ("stage_id", int)]
    )(CITY_TRIAL_MENU_SELECTION, STADIUM_DESTRUCTION_DERBY_3_STAGE_ID)
    STADIUM_DESTRUCTION_DERBY_4 = NamedTuple(
        "STADIUM_DESTRUCTION_DERBY_4", [("menu_selection_id", int), ("stage_id", int)]
    )(CITY_TRIAL_MENU_SELECTION, STADIUM_DESTRUCTION_DERBY_4_STAGE_ID)
    STADIUM_DESTRUCTION_DERBY_5 = NamedTuple(
        "STADIUM_DESTRUCTION_DERBY_5", [("menu_selection_id", int), ("stage_id", int)]
    )(CITY_TRIAL_MENU_SELECTION, STADIUM_DESTRUCTION_DERBY_5_STAGE_ID)
    STADIUM_KIRBY_MELEE_1 = NamedTuple("STADIUM_KIRBY_MELEE_1", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_KIRBY_MELEE_1_STAGE_ID
    )
    STADIUM_KIRBY_MELEE_2 = NamedTuple("STADIUM_KIRBY_MELEE_2", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_KIRBY_MELEE_2_STAGE_ID
    )
    # STADIUM_SINGLE_RACE_1 = NamedTuple("STADIUM_SINGLE_RACE_1", [("menu_selection_id", int), ("stage_id", int)])(
    #    CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_1_STAGE_ID
    # )
    STADIUM_SINGLE_RACE_2 = NamedTuple("STADIUM_SINGLE_RACE_2", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_2_STAGE_ID
    )
    STADIUM_SINGLE_RACE_3 = NamedTuple("STADIUM_SINGLE_RACE_3", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_3_STAGE_ID
    )
    STADIUM_SINGLE_RACE_4 = NamedTuple("STADIUM_SINGLE_RACE_4", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_4_STAGE_ID
    )
    STADIUM_SINGLE_RACE_5 = NamedTuple("STADIUM_SINGLE_RACE_5", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_5_STAGE_ID
    )
    STADIUM_SINGLE_RACE_6 = NamedTuple("STADIUM_SINGLE_RACE_6", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_6_STAGE_ID
    )
    STADIUM_SINGLE_RACE_7 = NamedTuple("STADIUM_SINGLE_RACE_7", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_7_STAGE_ID
    )
    STADIUM_SINGLE_RACE_8 = NamedTuple("STADIUM_SINGLE_RACE_8", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_8_STAGE_ID
    )
    STADIUM_SINGLE_RACE_9 = NamedTuple("STADIUM_SINGLE_RACE_9", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_SINGLE_RACE_9_STAGE_ID
    )
    STADIUM_VS_KING_DEDEDE = NamedTuple("STADIUM_VS_KING_DEDEDE", [("menu_selection_id", int), ("stage_id", int)])(
        CITY_TRIAL_MENU_SELECTION, STADIUM_VS_KING_DEDEDE_STAGE_ID
    )
    MAGMA_FLOWS = NamedTuple("MAGMA_FLOWS", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, MAGMA_FLOWS_STAGE_ID
    )
    # FANTASY_MEADOWS = NamedTuple("FANTASY_MEADOWS", [("menu_selection_id", int), ("stage_id", int)])(
    #    AIR_RIDE_MENU_SELECTION, FANTASY_MEADOWS_STAGE_ID
    # )
    CELESTIAL_VALLEY = NamedTuple("CELESTIAL_VALLEY", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, CELESTIAL_VALLEY_STAGE_ID
    )
    BEANSTALK_PARK = NamedTuple("BEANSTALK_PARK", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, BEANSTALK_PARK_STAGE_ID
    )
    FROZEN_HILLSIDE = NamedTuple("FROZEN_HILLSIDE", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, FROZEN_HILLSIDE_STAGE_ID
    )
    MACHINE_PASSAGE = NamedTuple("MACHINE_PASSAGE", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, MACHINE_PASSAGE_STAGE_ID
    )
    SKY_SANDS = NamedTuple("SKY_SANDS", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, SKY_SANDS_STAGE_ID
    )
    CHECKER_KNIGHTS = NamedTuple("CHECKER_KNIGHTS", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, CHECKER_KNIGHTS_STAGE_ID
    )
    NEBULA_BELT = NamedTuple("NEBULA_BELT", [("menu_selection_id", int), ("stage_id", int)])(
        AIR_RIDE_MENU_SELECTION, NEBULA_BELT_STAGE_ID
    )


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
        self.player_1_patches: dict[PatchType, float] = {key: 0 for key in PATCH_ADDRESS_MAP.keys()}
        self.destruction_count: int = 0
        self.current_stage: StageType | None = None

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
        except RuntimeError:
            # pointer is not initialized yet in-game, ignore this
            return None
        except Exception as e:
            logger.warning(
                MEMORY_READ_ERROR.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e))
            )
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
            logger.warning(
                MEMORY_WRITE_ERROR.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e))
            )
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
            logger.warning(
                MEMORY_WRITE_ERROR.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e))
            )
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

    def update_player_patch_counts(self) -> None:
        """
        Read in the current player patch counts to self.player_1_patches.
        """
        for patch_type in self.player_1_patches:
            self.player_1_patches[patch_type] = self.read_float(PATCH_ADDRESS_MAP[patch_type])

    def update_destruction_count(self) -> None:
        """
        Read the current number of destroyed objects into self.destruction_count. Clamps the value
        to be >= 0.
        """
        self.destruction_count = max(0, self.read_byte(PLAYER_1_DESTRUCTION_COUNT_ADDRESS))

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

    def get_current_stage(self) -> StageType | None:
        """
        Check which stage the player is currently in in-game. Returns None if the player is not in a stage.
        """
        menu_selection = self.read_byte(MENU_STAGE_ID_ADDR)
        current_stage = self.read_pointer(CURR_STAGE_ID_ADDR, 0x4, 4)

        if current_stage is not None:
            current_stage = int.from_bytes(current_stage, byteorder="big")
            if current_stage not in range(0, 22):
                return None
        else:
            return None

        for stage_type in StageType:
            if stage_type.value.menu_selection_id == menu_selection and stage_type.value.stage_id == current_stage:
                logger.info(f"Current stage: {stage_type}")
                return stage_type

    def check_transition(self) -> Tuple[StageType | None, bool]:
        """
        Detect a transition into a stage. Sets the current stage once a transition into that stage is detected.

        Returns:
            The stage type of the stage transitioned into (this will be None if no transition has happened).
            True ONLY IF a transition INTO the stage has happened.
        """
        trigger = False
        # Detect transition into the stage
        stage = self.get_current_stage()
        if stage is not None and stage != self.current_stage and not self.transitioned:
            logger.info(f"transition into stage {stage.name} detected")
            trigger = True
            self.transitioned = True
            self.transitioned_time = time.time()
            self.current_stage = stage
        # Detect transition out of the stage
        elif stage is None and stage != self.current_stage and self.transitioned:
            logger.info(f"transition out of stage {self.current_stage} detected")
            self.transitioned = False
            self.current_stage = None

        return stage, trigger

    def transition_waited(self) -> bool:
        """
        Check if the stage transition time wait after entering a stage has elapsed.

        Returns:
            True if the wait time has elapsed.
        """
        return time.time() >= self.transitioned_time + self.transition_wait
