import time
from typing import Optional, Tuple

import dolphin_memory_engine

from CommonClient import logger

from .KARData import PATCH_MAP, STAGE_MAP, EffectType, MemoryAddress, PatchType, StageName

KAR_GAME_ID = b"GKYE01"

# Memory access error messages
MEMORY_READ_ERROR = "Failed to read {type} at {addr}: {error}"
MEMORY_WRITE_ERROR = "Failed to write {type} at {addr}: {error}"


class DolphinInterface:
    """Interface for all interactions with the Dolphin emulator."""

    def __init__(self) -> None:
        """Initialize the Dolphin interface with default values."""
        self.transitioned_time: float = time.time()
        self.transition_wait: int = 6
        self.transitioned: bool = False
        self.player_1_patches: dict[PatchType, float] = {
            patch_type: 0 for patch_type in PATCH_MAP if "Up" in patch_type and "Permanent" not in patch_type
        }
        self.destruction_count: int = 0
        self.current_stage: StageName | None = None

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

    def increment_player_patch(self, patch_type: PatchType, delta: int) -> None:
        """
        Change the player patch count by delta.

        Args:
            patch_type: PatchType of the patch to be incremented
            delta: Amount to change the patch value (positive or negative)
        """
        # Handle "ALL" patch type which updates all stats
        if "All" in patch_type:
            for patch in PATCH_MAP.values():
                if "Up" in patch.type and "Permanent" not in patch.type:
                    current = self.read_float(patch.memory_address.value)
                    self.write_float(patch.memory_address.value, current + delta)
        else:
            # Handle specific patch type
            patch = PATCH_MAP[patch_type]
            current = self.read_float(patch.memory_address.value)
            self.write_float(patch.memory_address.value, current + delta)

    def update_player_patch_counts(self) -> None:
        """
        Read in the current player patch counts to self.player_1_patches.
        """
        for patch_type in self.player_1_patches:
            self.player_1_patches[patch_type] = self.read_float(PATCH_MAP[patch_type].memory_address.value)

    def update_destruction_count(self) -> None:
        """
        Read the current number of destroyed objects into self.destruction_count. Clamps the value
        to be >= 0.
        """
        self.destruction_count = max(0, self.read_byte(MemoryAddress.PLAYER_1_DESTRUCTION_COUNT_ADDRESS.value))

    def apply_effect_item(self, effect: EffectType) -> None:
        """
        Apply special effect items.

        Args:
            item_name: Name of the effect item to apply
        """
        match effect:
            case EffectType.ONE_HP:
                self.write_pointer_float(
                    MemoryAddress.PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.value,
                    MemoryAddress.PLAYER_1_CURRENT_MACHINE_HP_OFFSET.value,
                    1,
                )
            case EffectType.FULL_HEAL:
                current_max_hp = self.read_float(MemoryAddress.PLAYER_1_CURRENT_MAX_HP_ADDRESS.value)
                self.write_pointer_float(
                    MemoryAddress.PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.value,
                    MemoryAddress.PLAYER_1_CURRENT_MACHINE_HP_OFFSET.value,
                    current_max_hp,
                )

    def check_alive(self) -> bool:
        """
        Check if the player is currently alive in-game.

        Returns:
            True if the player is alive, False otherwise
        """
        return self.read_float(MemoryAddress.PLAYER_1_CURRENT_HP_ADDRESS.value) > 0.0

    def give_death(self) -> None:
        """Trigger the player's death in-game by setting their current health to zero."""
        self.write_pointer_float(
            MemoryAddress.PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.value,
            MemoryAddress.PLAYER_1_CURRENT_MACHINE_HP_OFFSET.value,
            0,
        )

    def check_game_running(self) -> bool:
        """
        Check if the game is running within Dolphin.

        Returns:
            True if the game is running, False otherwise
        """
        return self.read_bytes(0x80000000, 6) == KAR_GAME_ID

    def get_current_stage(self) -> StageName | None:
        """
        Check which stage the player is currently in in-game. Returns None if the player is not in a stage.
        """
        menu_selection = self.read_byte(MemoryAddress.MENU_STAGE_ID_ADDR.value)
        current_stage = self.read_pointer(MemoryAddress.CURR_STAGE_ID_ADDR.value, 0x4, 4)

        if current_stage is not None:
            current_stage = int.from_bytes(current_stage, byteorder="big")
            if current_stage not in range(0, 22):
                return None
        else:
            return None

        for stage in STAGE_MAP.values():
            if stage.menu_selection == menu_selection and stage.stage_id == current_stage:
                return stage.name

    def check_transition(self) -> Tuple[StageName | None, bool]:
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
            logger.debug(f"transition into stage {stage.value} detected")
            trigger = True
            self.transitioned = True
            self.transitioned_time = time.time()
            self.current_stage = stage
        # Detect transition out of the stage
        elif stage is None and stage != self.current_stage and self.transitioned:
            logger.debug(f"transition out of stage {self.current_stage} detected")
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
