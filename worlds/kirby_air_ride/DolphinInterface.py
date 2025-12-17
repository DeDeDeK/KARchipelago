import time

import dolphin_memory_engine
from CommonClient import logger

from .KARData import (
    BIT_POSITION_TO_STADIUM_MAP,
    STAGE_MAP,
    STAT_TO_MEMORY_MAP,
    CheckboxFillerType,
    EffectType,
    MemoryAddress,
    StageName,
    StatType,
    SubMenuFlag,
    compose_stadium_unlocks_number,
)


class DolphinInterface:
    """Interface for all interactions with the Dolphin emulator."""

    def __init__(self) -> None:
        """Initialize the Dolphin interface with default values."""
        self.kar_game_id = b"GKYE01"
        self.memory_read_error_fmt = "Failed to read {type} at {addr}: {error}"
        self.memory_write_error_fmt = "Failed to write {type} at {addr}: {error}"
        self.transitioned_time: float = time.time()
        self.transition_wait: int = 6
        self.player_1_patches_old: dict[StatType, float] = dict.fromkeys(StatType, 0)
        self.player_1_patches: dict[StatType, float] = dict.fromkeys(StatType, 0)
        self.unlocked_stadiums: set[StageName] = set()
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
            logger.warning(self.memory_read_error_fmt.format(type="byte", addr=hex(console_address), error=str(e)))
            return 0

    def read_bytes(self, console_address: int, num_bytes: int) -> bytes:
        """Read multiple bytes from Dolphin memory."""
        try:
            # returns bytes
            return dolphin_memory_engine.read_bytes(console_address, num_bytes)
        except Exception as e:
            logger.warning(
                self.memory_read_error_fmt.format(type=f"{num_bytes} bytes", addr=hex(console_address), error=str(e))
            )
            return b""

    def read_short(self, console_address: int) -> int:
        """Read a 2-byte short from Dolphin memory."""
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 2), byteorder="big")
        except Exception as e:
            logger.warning(self.memory_read_error_fmt.format(type="short", addr=hex(console_address), error=str(e)))
            return 0

    def read_float(self, console_address: int) -> float:
        """Read a float value from Dolphin memory."""
        try:
            # returns a float
            return dolphin_memory_engine.read_float(console_address)
        except Exception as e:
            logger.warning(self.memory_read_error_fmt.format(type="float", addr=hex(console_address), error=str(e)))
            return 0.0

    def write_byte(self, console_address: int, value: int) -> bool:
        """
        Write a byte to Dolphin memory. Converts the int value to a single byte before writing to console_address.

        Returns:
            Whether the write operation was successful
        """
        try:
            dolphin_memory_engine.write_bytes(console_address, value.to_bytes(1, byteorder="big", signed=True))
            return True
        except Exception as e:
            logger.warning(self.memory_write_error_fmt.format(type="byte", addr=hex(console_address), error=str(e)))
            return False

    def write_bytes(self, console_address: int, value: int, num_bytes: int) -> bool:
        """
        Write multiple bytes to Dolphin memory. Converts the integer argument to the specified number of bytes,
        and then writes that number of bytes starting a console_address.

        Returns:
            Whether the write operation was successful
        """
        try:
            dolphin_memory_engine.write_bytes(console_address, value.to_bytes(num_bytes, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(self.memory_write_error_fmt.format(type="byte", addr=hex(console_address), error=str(e)))
            return False

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
            logger.warning(self.memory_write_error_fmt.format(type="short", addr=hex(console_address), error=str(e)))
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
            logger.warning(self.memory_write_error_fmt.format(type="float", addr=hex(console_address), error=str(e)))
            return False

    def read_pointer_bytes(self, console_address: int, offset: int, byte_count: int) -> bytes | None:
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
                self.memory_read_error_fmt.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e))
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
                self.memory_write_error_fmt.format(
                    type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e)
                )
            )
            return False

    def read_pointer_float(self, console_address: int, offset: int) -> float | None:
        """
        Follow the pointer at console_address and apply the given offset, then read the value from it.

        Args:
            console_address: Address of the pointer
            offset: Offset to apply when reading from the pointed location
        Returns:
            Float value from memory, or None if the operation failed.
        """
        try:
            address = dolphin_memory_engine.follow_pointers(console_address, [0])
            address += offset
            return dolphin_memory_engine.read_float(address)
        except RuntimeError:
            # player is dead or off vehicle, pointer resolves to address 0 and is invalid
            return None
        except Exception as e:
            logger.warning(
                self.memory_read_error_fmt.format(type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e))
            )
            return None

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
                self.memory_write_error_fmt.format(
                    type="pointer", addr=f"{hex(console_address)}+{offset}", error=str(e)
                )
            )
            return False

    def get_city_trial_current_stadium(self) -> tuple[int, StageName]:
        """
        Get the current stadium that has been selected by the game to happen at the end of City Trial.
        Returns the number read from memory and the corresponding StageName.
        """
        # num from 0-23
        stadium_number = self.read_byte(MemoryAddress.CITY_TRIAL_STADIUM_EVENT_ADDRESS.value)
        # needs to be reversed as the map is in significant bit order, not stage number order
        stage_name = list(reversed(BIT_POSITION_TO_STADIUM_MAP))[stadium_number]
        return stadium_number, stage_name

    def set_city_trial_current_stadium(self, stadium: StageName | None) -> None:
        """
        sets the stadium that will occur at the end of the current city trial run to be the given stadium.

        if stadium is None, this sets the stadium to -2, which sets the stadium to fantasy meadows race 1 lap,
        and prevents unlocking of the stadium.
        """
        # TODO: this causes the game to crash when the stadium prediction event happens. For now, we always have
        # a starting stadium unlock item to prevent this.
        if stadium is None:
            self.write_byte(MemoryAddress.CITY_TRIAL_STADIUM_EVENT_ADDRESS.value, -2)
            return

        if stadium in BIT_POSITION_TO_STADIUM_MAP:
            # the number written to the memory address must be in range 0-23, or a negative number
            # if wanting to prevent unlocking the stadium
            # index already 0-indexes, but it's in reverse order, so we need to take 23 - value
            stadium_number = 23 - BIT_POSITION_TO_STADIUM_MAP.index(stadium)
            self.write_byte(MemoryAddress.CITY_TRIAL_STADIUM_EVENT_ADDRESS.value, stadium_number)
        else:
            logger.warning(f"invalid stadium name: {stadium} is not a stadium")

    def update_unlocked_stadiums(self) -> None:
        """
        Sets the game state of unlocked stadiums based on self.unlocked_stadiums.
        """
        bit_list = [0] * 24
        for stadium in self.unlocked_stadiums:
            i = BIT_POSITION_TO_STADIUM_MAP.index(stadium)
            bit_list[i] = 1
        value = compose_stadium_unlocks_number(bit_list)
        self.write_bytes(MemoryAddress.CITY_TRIAL_UNLOCKED_STADIUMS_ADDRESS.value, value, 3)

    def increment_player_patch_stat(self, stat_type: StatType, delta: int) -> None:
        """
        Change the player patch stat count by delta.

        Args:
            stat_type: StatType of the patch to be incremented
            delta: Amount to change the patch value (positive or negative)
        """
        memory_offset = STAT_TO_MEMORY_MAP.get(stat_type)
        if memory_offset is not None:
            current = self.read_pointer_float(
                MemoryAddress.PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.value, memory_offset.value
            )
            if current is not None:
                self.write_pointer_float(
                    MemoryAddress.PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.value, memory_offset.value, current + delta
                )
        else:
            logger.warning(f"unknown stat to memory address mapping for stat type: {stat_type}")

    def update_player_patch_counts(self) -> None:
        """
        Read in the current player patch counts to self.player_1_patches. Save the old values for patch counts
        to facilitate energylink and other features that need a diff of the counts.
        """
        self.player_1_patches_old = dict(self.player_1_patches)
        for stat_type in self.player_1_patches:
            value = self.read_pointer_float(
                MemoryAddress.PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.value, STAT_TO_MEMORY_MAP[stat_type].value
            )
            if value is not None:
                self.player_1_patches[stat_type] = value

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
            effect: EffectType to apply.
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

    def apply_checkbox_filler(self, type: CheckboxFillerType) -> None:
        """
        Apply checkbox filler items to the appropriate checklist.
        """
        match type:
            case CheckboxFillerType.CITY_TRIAL_CHECKBOX_FILLER:
                current_value = self.read_byte(MemoryAddress.CITY_TRIAL_CHECKLIST_BOX_FILLER_NUM.value)
                current_list_length = self.read_byte(MemoryAddress.CITY_TRIAL_CHECKLIST_BOX_FILLER_LIST_LENGTH.value)
                self.write_byte(MemoryAddress.CITY_TRIAL_CHECKLIST_BOX_FILLER_NUM.value, current_value + 1)
                if current_list_length <= 4:
                    # increase list length to ensure checkbox filler is visible and useable. this caps out at 5
                    self.write_byte(
                        MemoryAddress.CITY_TRIAL_CHECKLIST_BOX_FILLER_LIST_LENGTH.value, current_list_length + 1
                    )
            case CheckboxFillerType.AIR_RIDE_CHECKBOX_FILLER:
                current_value = self.read_byte(MemoryAddress.AIR_RIDE_CHECKLIST_BOX_FILLER_NUM.value)
                current_list_length = self.read_byte(MemoryAddress.AIR_RIDE_CHECKLIST_BOX_FILLER_LIST_LENGTH.value)
                self.write_byte(MemoryAddress.AIR_RIDE_CHECKLIST_BOX_FILLER_NUM.value, current_value + 1)
                if current_list_length <= 4:
                    # increase list length to ensure checkbox filler is visible and useable. this caps out at 5
                    self.write_byte(
                        MemoryAddress.AIR_RIDE_CHECKLIST_BOX_FILLER_LIST_LENGTH.value, current_list_length + 1
                    )
            case CheckboxFillerType.TOP_RIDE_CHECKBOX_FILLER:
                current_value = self.read_byte(MemoryAddress.TOP_RIDE_CHECKLIST_BOX_FILLER_NUM.value)
                current_list_length = self.read_byte(MemoryAddress.TOP_RIDE_CHECKLIST_BOX_FILLER_LIST_LENGTH.value)
                self.write_byte(MemoryAddress.TOP_RIDE_CHECKLIST_BOX_FILLER_NUM.value, current_value + 1)
                if current_list_length <= 4:
                    # increase list length to ensure checkbox filler is visible and useable. this caps out at 5
                    self.write_byte(
                        MemoryAddress.TOP_RIDE_CHECKLIST_BOX_FILLER_LIST_LENGTH.value, current_list_length + 1
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
            0.0,
        )

    def check_game_running(self) -> bool:
        """
        Check if the game is running within Dolphin.

        Returns:
            True if the game is running, False otherwise
        """
        return self.read_bytes(MemoryAddress.BASE_MEMORY_ADDRESS.value, 6) == self.kar_game_id

    def get_current_stage(self) -> StageName | None:
        """
        Check which stage the player is currently in in-game. Returns None if the player is not in a stage.
        """
        menu_selection = self.read_byte(MemoryAddress.MENU_STAGE_ID_ADDR.value)
        sub_menu_selection = self.read_byte(MemoryAddress.SUB_MENU_STAGE_ID_ADDR.value)
        sub_sub_menu_selection = self.read_byte(MemoryAddress.SUB_SUB_MENU_STAGE_ID_ADDR.value)
        submenu_flag = self.read_byte(MemoryAddress.SUBMENU_FLAG.value)
        current_stage = self.read_pointer_bytes(MemoryAddress.CURR_STAGE_ID_ADDR.value, 0x4, 4)

        if current_stage is not None:
            current_stage = int.from_bytes(current_stage, byteorder="big")
            if current_stage not in range(0, 22):
                return None
        else:
            return None

        for stage in STAGE_MAP.values():
            if (
                stage.menu_selection.value == menu_selection
                and stage.sub_menu_selection.value == sub_menu_selection
                and stage.stage_id.value == current_stage
            ):
                if stage.submenu_flag.value == submenu_flag:
                    if stage.submenu_flag.value == SubMenuFlag.ON.value:
                        if stage.sub_sub_menu_selection.value == sub_sub_menu_selection:
                            return stage.name
                    else:
                        return stage.name

        return None

    def check_transition(self) -> tuple[StageName | None, bool]:
        """
        Detect a transition into a stage. Sets the current stage once a transition into that stage is detected.

        Returns:
            The stage type of the stage transitioned into (this will be None if no transition has happened).
            True ONLY IF a transition INTO the stage has happened.
        """
        trigger = False
        # Detect transition into the stage
        stage = self.get_current_stage()
        if stage is not None and stage != self.current_stage:
            logger.debug(f"transition into stage {stage.value} detected")
            trigger = True
            self.transitioned_time = time.time()
        # Detect transition out of the stage
        elif stage is None and stage != self.current_stage:
            logger.debug(f"transition out of stage {self.current_stage} detected")

        self.current_stage = stage
        return stage, trigger

    def transition_waited(self) -> bool:
        """
        Check if the stage transition time wait after entering a stage has elapsed.

        Returns:
            True if the wait time has elapsed.
        """
        return time.time() >= self.transitioned_time + self.transition_wait
