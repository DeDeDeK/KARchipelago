import dolphin_memory_engine
from CommonClient import logger

from .KARData import MEM1_END, MEM1_START, MemoryAddress


class DolphinInterface:
    """Low-level interface for reading/writing Dolphin emulator memory.

    All read methods return a sensible zero-value on failure and log a warning.
    All write methods return True on success, False on failure.
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
        """Check if currently connected to Dolphin memory.

        Defensive: never raises. The dolphin sync loop calls this outside its
        inner error handler, and the task has no supervisor, so a raised
        exception here would escape and permanently kill the connector. The
        underlying call doesn't normally fail; if it ever does, log it (never
        silently) and treat it as not hooked.
        """
        try:
            return dolphin_memory_engine.is_hooked()
        except Exception as e:
            logger.warning(f"Error checking Dolphin hook state: {e}")
            return False

    def status_name(self) -> str:
        """Raw dolphin_memory_engine connection status name. Never raises.

        One of "hooked", "notRunning" (no Dolphin process), "noEmu" (Dolphin
        running but no readable emulated game), "unHooked" (not yet attached),
        or "unknown" on error. is_hooked() collapses all of these to a bool;
        this preserves the distinction so the client can tell "Dolphin closed"
        apart from "Dolphin open but its memory is unreadable" (wrong Dolphin
        version, no game booted, or a permission/sandbox mismatch) - on every
        platform those otherwise surface identically as is_hooked() == False.
        """
        try:
            return dolphin_memory_engine.get_status().name
        except Exception as e:
            logger.warning(f"Error reading Dolphin status: {e}")
            return "unknown"

    def check_game_running(self) -> bool:
        """Check whether Kirby Air Ride (NTSC-U) is the game running in Dolphin.

        Reads through read_bytes so a failed read is logged rather than silently
        swallowed (a wrong or empty game id simply returns False). int(): some
        dolphin-memory-engine builds reject an IntEnum address with "expected int,
        got MemoryAddress". BASE_MEMORY_ADDRESS and AP_DATA_POINTER (resolve_ap_data)
        are the only fixed addresses passed straight to DME; everything else gets a
        plain int via _addr().
        """
        return self.read_bytes(int(MemoryAddress.BASE_MEMORY_ADDRESS), 6) == self.kar_game_id

    # Resolve APData pointer

    def resolve_ap_data(self) -> int | None:
        """Read the APData struct pointer. Returns the base address, or None if not yet allocated.

        Before the mod's OnBoot writes the real pointer, AP_DATA_POINTER holds zero or
        stale/uninitialized memory. Reject anything outside MEM1 so the caller keeps
        waiting instead of latching a garbage address and spamming failed struct reads.
        """
        try:
            ptr = dolphin_memory_engine.read_word(int(MemoryAddress.AP_DATA_POINTER))
            return ptr if MEM1_START <= ptr < MEM1_END else None
        except Exception as e:
            logger.warning(f"Failed to read APData pointer: {e}")
            return None

    # Primitive reads

    def read_u8(self, address: int) -> int:
        """Read an unsigned 8-bit integer."""
        try:
            return dolphin_memory_engine.read_byte(address)
        except Exception as e:
            logger.warning(f"Failed to read u8 at {address:#x}: {e}")
            return 0

    def read_u16(self, address: int) -> int:
        """Read an unsigned 16-bit big-endian integer."""
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(address, 2), byteorder="big")
        except Exception as e:
            logger.warning(f"Failed to read u16 at {address:#x}: {e}")
            return 0

    def read_u32(self, address: int) -> int:
        """Read an unsigned 32-bit big-endian integer."""
        try:
            return dolphin_memory_engine.read_word(address)
        except Exception as e:
            logger.warning(f"Failed to read u32 at {address:#x}: {e}")
            return 0

    def read_u64(self, address: int) -> int:
        """Read an unsigned 64-bit big-endian integer."""
        try:
            return int.from_bytes(dolphin_memory_engine.read_bytes(address, 8), byteorder="big")
        except Exception as e:
            logger.warning(f"Failed to read u64 at {address:#x}: {e}")
            return 0

    def read_float(self, address: int) -> float:
        """Read a 32-bit big-endian float."""
        try:
            return dolphin_memory_engine.read_float(address)
        except Exception as e:
            logger.warning(f"Failed to read float at {address:#x}: {e}")
            return 0.0

    def read_bytes(self, address: int, length: int) -> bytes:
        """Read `length` raw bytes."""
        try:
            return dolphin_memory_engine.read_bytes(address, length)
        except Exception as e:
            logger.warning(f"Failed to read {length} bytes at {address:#x}: {e}")
            return b""

    # Primitive writes

    def write_u8(self, address: int, value: int) -> bool:
        """Write an unsigned 8-bit integer."""
        try:
            dolphin_memory_engine.write_byte(address, value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write u8 at {address:#x}: {e}")
            return False

    def write_u16(self, address: int, value: int) -> bool:
        """Write an unsigned 16-bit big-endian integer."""
        try:
            dolphin_memory_engine.write_bytes(address, value.to_bytes(2, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(f"Failed to write u16 at {address:#x}: {e}")
            return False

    def write_u32(self, address: int, value: int) -> bool:
        """Write an unsigned 32-bit big-endian integer."""
        try:
            dolphin_memory_engine.write_word(address, value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write u32 at {address:#x}: {e}")
            return False

    def write_u64(self, address: int, value: int) -> bool:
        """Write an unsigned 64-bit big-endian integer."""
        try:
            dolphin_memory_engine.write_bytes(address, value.to_bytes(8, byteorder="big"))
            return True
        except Exception as e:
            logger.warning(f"Failed to write u64 at {address:#x}: {e}")
            return False

    def write_float(self, address: int, value: float) -> bool:
        """Write a 32-bit big-endian float."""
        try:
            dolphin_memory_engine.write_float(address, value)
            return True
        except Exception as e:
            logger.warning(f"Failed to write float at {address:#x}: {e}")
            return False

    def write_bytes(self, address: int, data: bytes) -> bool:
        """Write raw bytes."""
        try:
            dolphin_memory_engine.write_bytes(address, data)
            return True
        except Exception as e:
            logger.warning(f"Failed to write {len(data)} bytes at {address:#x}: {e}")
            return False
