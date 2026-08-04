import dolphin_memory_engine
from CommonClient import logger

from .KARData import MemoryAddress


class DolphinInterface:
    """Low-level interface for reading/writing Dolphin emulator memory.

    Reads return a sensible zero-value on failure and log a warning; writes return True/False.
    """

    def __init__(self) -> None:
        self.kar_game_id = b"GKYE01"

    def hook(self) -> bool:
        """Establish a connection to Dolphin memory."""
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
        """Check if currently connected to Dolphin memory. Defensive: never raises. The sync loop calls
        this outside its inner error handler and the task has no supervisor, so an escaping exception
        would permanently kill the connector; a failed call is logged and treated as not hooked."""
        try:
            return dolphin_memory_engine.is_hooked()
        except Exception as e:
            logger.warning(f"Error checking Dolphin hook state: {e}")
            return False

    def status_name(self) -> str:
        """Raw dolphin_memory_engine connection status name. Never raises.

        One of "hooked", "notRunning" (no Dolphin process), "noEmu" (running but no readable game),
        "unHooked" (not yet attached), or "unknown" on error. is_hooked() collapses these to a bool; this
        preserves the distinction between "Dolphin closed" and "Dolphin open but unreadable".
        """
        try:
            return dolphin_memory_engine.get_status().name
        except Exception as e:
            logger.warning(f"Error reading Dolphin status: {e}")
            return "unknown"

    def check_game_running(self) -> bool:
        """Check whether Kirby Air Ride (NTSC-U) is the game running in Dolphin. Reads through read_bytes
        so a failed read is logged, not silently swallowed; a wrong or empty game id returns False."""
        return self.read_bytes(MemoryAddress.MEM1_START, 6) == self.kar_game_id

    # Resolve APData pointer

    def resolve_ap_data(self) -> int | None:
        """Read the APData struct pointer. Returns the base address, or None if not yet allocated.

        Before the mod's OnBoot writes it, AP_DATA_POINTER holds zero or stale memory, so anything
        outside MEM1 is rejected and the caller keeps waiting rather than latching a garbage address.
        A failed read returns 0, which falls outside MEM1 -> None.
        """
        ptr = self.read_u32(MemoryAddress.AP_DATA_POINTER)
        return ptr if MemoryAddress.MEM1_START <= ptr < MemoryAddress.MEM1_END else None

    # Primitive reads. int(address) because DME's native read/write reject an int subclass (our
    # MemoryAddress IntEnum) on some builds; coercing here covers every caller and every DME build.

    def read_u8(self, address: int) -> int:
        """Read an unsigned 8-bit integer."""
        try:
            return dolphin_memory_engine.read_byte(int(address))
        except Exception as e:
            logger.warning(f"Failed to read u8 at {address:#x}: {e}")
            return 0

    def read_u16(self, address: int) -> int:
        """Read an unsigned 16-bit big-endian integer."""
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(int(address), 2), byteorder="big")
        except Exception as e:
            logger.warning(f"Failed to read u16 at {address:#x}: {e}")
            return 0

    def read_u32(self, address: int) -> int:
        """Read an unsigned 32-bit big-endian integer."""
        try:
            return dolphin_memory_engine.read_word(int(address))
        except Exception as e:
            logger.warning(f"Failed to read u32 at {address:#x}: {e}")
            return 0

    def read_u64(self, address: int) -> int:
        """Read an unsigned 64-bit big-endian integer."""
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(int(address), 8), byteorder="big")
        except Exception as e:
            logger.warning(f"Failed to read u64 at {address:#x}: {e}")
            return 0

    def read_float(self, address: int) -> float:
        """Read a 32-bit big-endian float."""
        try:
            return dolphin_memory_engine.read_float(int(address))
        except Exception as e:
            logger.warning(f"Failed to read float at {address:#x}: {e}")
            return 0.0

    def read_bytes(self, address: int, length: int) -> bytes:
        """Read `length` raw bytes."""
        try:
            return dolphin_memory_engine.read_bytes(int(address), length)
        except Exception as e:
            logger.warning(f"Failed to read {length} bytes at {address:#x}: {e}")
            return b""

    # Primitive writes

    def write_u8(self, address: int, value: int) -> bool:
        """Write an unsigned 8-bit integer."""
        try:
            dolphin_memory_engine.write_byte(int(address), value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write u8 at {address:#x}: {e}")
            return False

    def write_u16(self, address: int, value: int) -> bool:
        """Write an unsigned 16-bit big-endian integer."""
        try:
            dolphin_memory_engine.write_bytes(int(address), value.to_bytes(2, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(f"Failed to write u16 at {address:#x}: {e}")
            return False

    def write_u32(self, address: int, value: int) -> bool:
        """Write an unsigned 32-bit big-endian integer."""
        try:
            dolphin_memory_engine.write_word(int(address), value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write u32 at {address:#x}: {e}")
            return False

    def write_u64(self, address: int, value: int) -> bool:
        """Write an unsigned 64-bit big-endian integer."""
        try:
            dolphin_memory_engine.write_bytes(int(address), value.to_bytes(8, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(f"Failed to write u64 at {address:#x}: {e}")
            return False

    def write_float(self, address: int, value: float) -> bool:
        """Write a 32-bit big-endian float."""
        try:
            dolphin_memory_engine.write_float(int(address), value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write float at {address:#x}: {e}")
            return False

    def write_bytes(self, address: int, data: bytes) -> bool:
        """Write raw bytes."""
        try:
            dolphin_memory_engine.write_bytes(int(address), data)
            return True
        except Exception as e:
            logger.warning(f"Failed to write {len(data)} bytes at {address:#x}: {e}")
            return False
