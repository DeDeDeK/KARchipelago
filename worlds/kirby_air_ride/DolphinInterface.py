import dolphin_memory_engine
from CommonClient import logger

from .KARData import MemoryAddress


class DolphinInterface:
    """Low-level interface for reading/writing Dolphin emulator memory.

    Every multi-byte primitive (u16/u32/u64/float) is big-endian, matching the GameCube's PowerPC;
    read_bytes/write_bytes pass raw bytes through untouched. Reads return a zero-value on failure
    and log a warning; writes return True/False.
    """

    def __init__(self) -> None:
        self.kar_game_id = b"GKYE01"

    def hook(self) -> bool:
        try:
            dolphin_memory_engine.hook()
            return dolphin_memory_engine.is_hooked()
        except Exception as e:
            logger.warning(f"Failed to hook into Dolphin: {e}")
            return False

    def unhook(self) -> None:
        try:
            if dolphin_memory_engine.is_hooked():
                dolphin_memory_engine.un_hook()
        except Exception as e:
            logger.warning(f"Error while unhooking from Dolphin: {e}")

    def is_hooked(self) -> bool:
        """Never raises: the sync loop calls this outside its inner error handler and the task has no
        supervisor, so a failed call is logged and treated as not hooked."""
        try:
            return dolphin_memory_engine.is_hooked()
        except Exception as e:
            logger.warning(f"Error checking Dolphin hook state: {e}")
            return False

    def status_name(self) -> str:
        """Raw dolphin_memory_engine connection status name; never raises. One of "hooked", "notRunning"
        (no Dolphin process), "noEmu" (running but no readable game), "unHooked" (not yet attached), or
        "unknown" on error - the distinction is_hooked() collapses into a bool."""
        try:
            return dolphin_memory_engine.get_status().name
        except Exception as e:
            logger.warning(f"Error reading Dolphin status: {e}")
            return "unknown"

    def check_game_running(self) -> bool:
        """Check whether Kirby Air Ride (NTSC-U) is the game running in Dolphin. Reads through read_bytes
        so a failed read is logged, not silently swallowed; a wrong or empty game id returns False."""
        return self.read_bytes(MemoryAddress.MEM1_START, 6) == self.kar_game_id

    def resolve_ap_data(self) -> int | None:
        """Read the APData struct pointer, or None if not yet allocated. Before the mod's OnBoot writes
        it, AP_DATA_POINTER holds zero or stale memory, so anything outside MEM1 is rejected rather than
        latched as a garbage address (a failed read returns 0, also outside MEM1)."""
        ptr = self.read_u32(MemoryAddress.AP_DATA_POINTER)
        return ptr if MemoryAddress.MEM1_START <= ptr < MemoryAddress.MEM1_END else None

    def read_u8(self, address: int) -> int:
        try:
            return dolphin_memory_engine.read_byte(int(address))
        except Exception as e:
            logger.warning(f"Failed to read u8 at {address:#x}: {e}")
            return 0

    def read_u16(self, address: int) -> int:
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(int(address), 2), byteorder="big")
        except Exception as e:
            logger.warning(f"Failed to read u16 at {address:#x}: {e}")
            return 0

    def read_u32(self, address: int) -> int:
        try:
            return dolphin_memory_engine.read_word(int(address))
        except Exception as e:
            logger.warning(f"Failed to read u32 at {address:#x}: {e}")
            return 0

    def read_u64(self, address: int) -> int:
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(int(address), 8), byteorder="big")
        except Exception as e:
            logger.warning(f"Failed to read u64 at {address:#x}: {e}")
            return 0

    def read_float(self, address: int) -> float:
        try:
            return dolphin_memory_engine.read_float(int(address))
        except Exception as e:
            logger.warning(f"Failed to read float at {address:#x}: {e}")
            return 0.0

    def read_bytes(self, address: int, length: int) -> bytes:
        try:
            return dolphin_memory_engine.read_bytes(int(address), length)
        except Exception as e:
            logger.warning(f"Failed to read {length} bytes at {address:#x}: {e}")
            return b""

    def write_u8(self, address: int, value: int) -> bool:
        try:
            dolphin_memory_engine.write_byte(int(address), value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write u8 at {address:#x}: {e}")
            return False

    def write_u16(self, address: int, value: int) -> bool:
        try:
            dolphin_memory_engine.write_bytes(int(address), value.to_bytes(2, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(f"Failed to write u16 at {address:#x}: {e}")
            return False

    def write_u32(self, address: int, value: int) -> bool:
        try:
            dolphin_memory_engine.write_word(int(address), value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write u32 at {address:#x}: {e}")
            return False

    def write_u64(self, address: int, value: int) -> bool:
        try:
            dolphin_memory_engine.write_bytes(int(address), value.to_bytes(8, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(f"Failed to write u64 at {address:#x}: {e}")
            return False

    def write_float(self, address: int, value: float) -> bool:
        try:
            dolphin_memory_engine.write_float(int(address), value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write float at {address:#x}: {e}")
            return False

    def write_bytes(self, address: int, data: bytes) -> bool:
        try:
            dolphin_memory_engine.write_bytes(int(address), data)
            return True
        except Exception as e:
            logger.warning(f"Failed to write {len(data)} bytes at {address:#x}: {e}")
            return False
