from enum import IntEnum


class GameMode(IntEnum):
    """Row index for every game mode."""

    AIRRIDE = 0
    TOPRIDE = 1
    CITYTRIAL = 2
    ARCHIPELAGO = 3


class RewardType(IntEnum):
    """Mirrors the mod's RewardType enum (`RewardEntry.reward_type`). Lists only the types no gating category covers."""

    FILLER = 0x00
    BONUS_MOVIE = 0x01
    EXTRA_RULE = 0x02
    SOUND_TEST = 0x04
    MUSIC = 0x05
    ENDING = 0x06
    PAUSE_POWERUPS = 0x08


# Bits per mode in OPTION_CHECKLIST_REWARD_PLACED_TYPES
CHECKLIST_REWARD_MODE_BITS = 9


def checklist_reward_placed_bit(mode: GameMode, reward_type: RewardType) -> int:
    """Bit index of (mode, reward_type) in OPTION_CHECKLIST_REWARD_PLACED_TYPES; AIRRIDE/TOPRIDE/CITYTRIAL only."""
    return mode * CHECKLIST_REWARD_MODE_BITS + reward_type


class GoalKind(IntEnum):
    """Mirrors the mod's APGoalKind: written to OPTION_GOAL_<MODE>."""

    CHECKLIST_100 = 0
    N_CHECKLIST = 1
    CHECKLIST_LIST = 2
    HYDRA_AND_DRAGOON = 3
    BEAT_KING_DEDEDE = 4
    MAX_STATS_CT = 5
    ASSEMBLE_AP_STAR = 6
    ALL_LEGENDARIES_CT = 7
    NONE = 8


class GoalForcedGate(IntEnum):
    """Mirrors the mod's GOALGATE_* bits, written as a bitmask to OPTION_GOAL_FORCED_GATES."""

    LEGENDARY_PIECES = 0x1
    VS_KING_DEDEDE = 0x2
    AP_STAR_PIECES = 0x4


class TrapLinkKind(IntEnum):
    """Mirrors the mod's TrapLinkKind enum."""

    BAD_PATCH = 1
    SLEEP = 2
    SPEED_DOWN = 3


class APTextColor(IntEnum):
    """Mirrors the mod's APTextColor enum."""

    DEFAULT = 0
    BLACK = 1
    RED = 2
    GREEN = 3
    YELLOW = 4
    BLUE = 5
    MAGENTA = 6
    CYAN = 7
    WHITE = 8
    ORANGE = 9
    SLATEBLUE = 10
    PLUM = 11
    SALMON = 12


class APTextKind(IntEnum):
    """Mirrors the mod's APTextKind enum."""

    CHECK = 0
    ITEM = 1
    HINT = 2
    STATUS = 3
    CHAT = 4
    LINK = 5


# CommonClient GUI color name -> palette index.
AP_TEXT_COLOR_BY_NAME: dict[str, APTextColor] = {
    "black": APTextColor.BLACK,
    "red": APTextColor.RED,
    "green": APTextColor.GREEN,
    "yellow": APTextColor.YELLOW,
    "blue": APTextColor.BLUE,
    "magenta": APTextColor.MAGENTA,
    "cyan": APTextColor.CYAN,
    "white": APTextColor.WHITE,
    "orange": APTextColor.ORANGE,
    "slateblue": APTextColor.SLATEBLUE,
    "plum": APTextColor.PLUM,
    "salmon": APTextColor.SALMON,
}

# Fixed by the mod's APTextMessage layout.
AP_TEXT_SEG_NUM = 8
AP_TEXT_BLOB_LEN = 244
AP_TEXT_MESSAGE_SIZE = 256


class MemoryAddress(IntEnum):
    # MEM1 cached range.
    MEM1_START = 0x80000000
    MEM1_END = 0x81800000

    # Static pointer to the APData struct
    AP_DATA_POINTER = 0x805D52D4

    # EnergyLink pool balance, client-written. s64 raw units (1 unit = 1 MJ)
    ENERGY_BALANCE = 0x000  # s64
    # EnergyLink raw-MJ counters
    ENERGY_DEPOSIT_TOTAL = 0x008  # u32
    ENERGY_WITHDRAW_TOTAL = 0x00C  # u32
    # DeathLink flags
    DEATHLINK_RECEIVE = 0x010  # u32
    DEATHLINK_SEND = 0x014  # u32
    # TrapLink flags
    TRAPLINK_RECEIVE = 0x018  # u32
    TRAPLINK_SEND = 0x01C  # u32
    # Item mailbox
    INCOMING_ITEM_ID = 0x020  # u32
    ITEM_RECEIVED_INDEX = 0x024  # u32

    # 1 when mod is fully initialized and save data is loaded
    GAME_READY = 0x028  # u32

    OPTIONS_VALID = 0x02C  # u32

    OPTION_DEATH_LINK_ENABLED = 0x030  # u32, 0 or 1
    OPTION_ENERGY_LINK_ENABLED = 0x034  # u32, 0 or 1
    OPTION_TRAP_LINK_ENABLED = 0x038  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_AIRRIDE = 0x03C  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_TOPRIDE = 0x040  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_CITYTRIAL = 0x044  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_ARCHIPELAGO = 0x048  # u32, 0 or 1
    OPTION_GOAL_AIRRIDE = 0x04C  # u32
    OPTION_GOAL_TOPRIDE = 0x050  # u32
    OPTION_GOAL_CITYTRIAL = 0x054  # u32
    OPTION_GOAL_ARCHIPELAGO = 0x058  # u32
    OPTION_CHECKLIST_AMOUNT_AIRRIDE = 0x05C  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_TOPRIDE = 0x060  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_CITYTRIAL = 0x064  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_ARCHIPELAGO = 0x068  # u32, 1-120
    OPTION_CT_PATCH_CAP_MIN = 0x06C  # u32, 1-30
    OPTION_CT_PATCH_CAP_MAX = 0x070  # u32, 1-30
    OPTION_SPAWN_RATE_MIN = 0x074  # u32, 10-100
    OPTION_GOAL_CHECKS_AIRRIDE = 0x078  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_TOPRIDE = 0x088  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_CITYTRIAL = 0x098  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_ARCHIPELAGO = 0x0A8  # u64[2], 16 bytes
    OPTION_MACHINE_GATING_ENABLED = 0x0B8  # u32, 0 or 1
    OPTION_ABILITY_GATING_ENABLED = 0x0BC  # u32, 0 or 1
    OPTION_EVENT_GATING_ENABLED = 0x0C0  # u32, 0 or 1
    OPTION_PATCH_GATING_ENABLED = 0x0C4  # u32, 0 or 1
    OPTION_ITEM_GATING_ENABLED = 0x0C8  # u32, 0 or 1
    OPTION_BOX_GATING_ENABLED = 0x0CC  # u32, 0 or 1
    OPTION_AIRRIDE_STAGE_GATING_ENABLED = 0x0D0  # u32, 0 or 1
    OPTION_TOPRIDE_STAGE_GATING_ENABLED = 0x0D4  # u32, 0 or 1
    OPTION_TOPRIDE_ITEM_GATING_ENABLED = 0x0D8  # u32, 0 or 1
    OPTION_COLOR_GATING_ENABLED = 0x0DC  # u32, 0 or 1
    OPTION_STADIUM_GATING_ENABLED = 0x0E0  # u32, 0 or 1
    OPTION_BASE_ABILITY_GATING_ENABLED = 0x0E4  # u32, 0 or 1
    OPTION_CHECKLIST_REWARD_PLACED_TYPES = 0x0E8  # u32 bitmask, 1 << RewardType
    OPTION_GOAL_FORCED_GATES = 0x0EC  # u32 bitmask, GOAL_FORCED_GATE_*
    OPTION_AP_PATCHES = 0x0F0  # u32, 0-AP_PATCH_MOD_MAX
    # APSlotOptions is 8-byte aligned, so 4 bytes of tail padding end the block at 0x0F8 (200 bytes).

    # Client writes 1 after all location arrays are written
    LOCATION_DATA_VALID = 0x0F8  # u32

    LOCATIONS_AIRRIDE = 0x0FC  # u16[46], 92 bytes (reward indices 0-45)
    LOCATIONS_TOPRIDE = 0x158  # u16[46], 92 bytes (reward indices 0-45; only 0-32 used)
    LOCATIONS_CITYTRIAL = 0x1B4  # u16[46], 92 bytes (reward indices 0-45; only 0-43 used)

    # Completed checkboxes per mode
    SENT_CHECKS_AIRRIDE = 0x210  # u64[2], 16 bytes
    SENT_CHECKS_TOPRIDE = 0x220  # u64[2], 16 bytes
    SENT_CHECKS_CITYTRIAL = 0x230  # u64[2], 16 bytes
    SENT_CHECKS_ARCHIPELAGO = 0x240  # u64[2], 16 bytes

    # Checks the server knows but the mod doesn't
    CLIENT_BACKFILL_AIRRIDE = 0x250  # u64[2], 16 bytes
    CLIENT_BACKFILL_TOPRIDE = 0x260  # u64[2], 16 bytes
    CLIENT_BACKFILL_CITYTRIAL = 0x270  # u64[2], 16 bytes
    CLIENT_BACKFILL_ARCHIPELAGO = 0x280  # u64[2], 16 bytes

    # Sticky goal completion flag. Game writes 1 when goal is satisfied
    GOAL_COMPLETE = 0x290  # u8
    GOAL_SATISFIED_MASK = 0x291  # u8, bit per GameMode row

    # Live in-game link toggles
    DEATHLINK_MENU_ENABLED = 0x294  # u32
    ENERGYLINK_MENU_ENABLED = 0x298  # u32
    TRAPLINK_MENU_ENABLED = 0x29C  # u32

    # Text mailbox
    TEXT_PENDING = 0x2A0  # u32
    # Live per-kind message toggles
    TEXT_MENU_MASK = 0x2A4  # u32
    TEXT_MSG = 0x2A8  # APTextMessage, 256 bytes

    # AP Patches
    AP_PATCH_CHECKS = 0x3A8  # u64[8], 64 bytes
    AP_PATCH_BACKFILL = 0x3E8  # u64[8], 64 bytes

    BACKFILL_VALID = 0x428  # u32


# Checklist reward item codes: 500-649, three mode bands of stride 50 in GameMode order.
REWARD_CODE_BASE = 500
REWARD_CODE_STRIDE = 50

# Padded reward slots per mode in the mod's locations[3][46] array.
REWARDS_PER_MODE = 46


# Per-mode base addresses for the mod's u16[46] locations array
LOCATIONS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.LOCATIONS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.LOCATIONS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.LOCATIONS_CITYTRIAL,
}

# Per-mode game-written checked-bits masks
SENT_CHECKS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.SENT_CHECKS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.SENT_CHECKS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.SENT_CHECKS_CITYTRIAL,
    GameMode.ARCHIPELAGO: MemoryAddress.SENT_CHECKS_ARCHIPELAGO,
}

# Client-written backfill masks
CLIENT_BACKFILL_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.CLIENT_BACKFILL_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.CLIENT_BACKFILL_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.CLIENT_BACKFILL_CITYTRIAL,
    GameMode.ARCHIPELAGO: MemoryAddress.CLIENT_BACKFILL_ARCHIPELAGO,
}

# Per-mode base addresses for the GOAL_CHECKLIST_LIST required-checkboxes u64[2] bitmasks.
OPTION_GOAL_CHECKS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.OPTION_GOAL_CHECKS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.OPTION_GOAL_CHECKS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.OPTION_GOAL_CHECKS_CITYTRIAL,
    GameMode.ARCHIPELAGO: MemoryAddress.OPTION_GOAL_CHECKS_ARCHIPELAGO,
}

# Per-mode start-revealed toggles, paired with the slot_data key each one is written from.
OPTION_REVEAL_CHECKLIST_PER_MODE: dict[GameMode, tuple[MemoryAddress, str]] = {
    GameMode.AIRRIDE: (MemoryAddress.OPTION_REVEAL_CHECKLIST_AIRRIDE, "air_ride_reveal_checklist"),
    GameMode.TOPRIDE: (MemoryAddress.OPTION_REVEAL_CHECKLIST_TOPRIDE, "top_ride_reveal_checklist"),
    GameMode.CITYTRIAL: (MemoryAddress.OPTION_REVEAL_CHECKLIST_CITYTRIAL, "city_trial_reveal_checklist"),
    GameMode.ARCHIPELAGO: (MemoryAddress.OPTION_REVEAL_CHECKLIST_ARCHIPELAGO, "archipelago_reveal_checklist"),
}

AP_CHECKLIST_CODE_BASE = 361
AP_CHECKLIST_CODE_NUM = 52

# The AP Patch block starts where the Archipelago band ends
AP_PATCH_CODE_BASE = AP_CHECKLIST_CODE_BASE + AP_CHECKLIST_CODE_NUM
AP_PATCH_CODE_MAX = 200

# Checkbox location codes per mode
CODE_BAND_PER_MODE: dict[GameMode, tuple[int, int]] = {
    GameMode.CITYTRIAL: (1, 120),
    GameMode.AIRRIDE: (121, 120),
    GameMode.TOPRIDE: (241, 120),
    GameMode.ARCHIPELAGO: (AP_CHECKLIST_CODE_BASE, AP_CHECKLIST_CODE_NUM),
}

AP_PATCH_MOD_MAX = 512
AP_PATCH_WORDS = AP_PATCH_MOD_MAX // 64
AP_PATCH_GROUP_SIZE = 20
AP_PATCH_GROUP_MAX = (AP_PATCH_CODE_MAX + AP_PATCH_GROUP_SIZE - 1) // AP_PATCH_GROUP_SIZE


def ap_patch_group_sizes(count: int) -> list[int]:
    """Split `count` AP Patches into consecutive group sizes."""
    if count <= 0:
        return []
    sizes = [AP_PATCH_GROUP_SIZE] * (count // AP_PATCH_GROUP_SIZE)
    remainder = count % AP_PATCH_GROUP_SIZE
    if remainder:
        if sizes and remainder * 2 < AP_PATCH_GROUP_SIZE:
            sizes[-1] += remainder
        else:
            sizes.append(remainder)
    return sizes


def location_code_to_mode_clear(code: int | None) -> tuple[GameMode, int] | None:
    """Decode a checkbox location code to (game_mode, clear_kind)."""
    if code is None:
        return None
    for mode, (base, width) in CODE_BAND_PER_MODE.items():
        if base <= code < base + width:
            return mode, code - base
    return None


def ap_patch_index_to_location_code(index: int) -> int:
    """Encode a 0-based AP Patch index to its location code."""
    return AP_PATCH_CODE_BASE + index


def location_code_to_ap_patch_index(code: int | None) -> int | None:
    """Decode a location code to its 0-based AP Patch index, or None if it is not one."""
    if code is None:
        return None
    index = code - AP_PATCH_CODE_BASE
    return index if 0 <= index < AP_PATCH_CODE_MAX else None


def mode_clear_to_location_code(mode: GameMode, clear_kind: int) -> int:
    """Encode (game_mode, clear_kind) to an AP location code, or 0 if the pair has none."""
    base, width = CODE_BAND_PER_MODE[mode]
    return base + clear_kind if 0 <= clear_kind < width else 0


def reward_code_to_mode_index(code: int | None) -> tuple[GameMode, int] | None:
    """Decode an AP reward item code to (source_mode, reward_index)."""
    if code is None:
        return None
    offset = code - REWARD_CODE_BASE
    if not (0 <= offset < 3 * REWARD_CODE_STRIDE):
        return None
    mode_idx, reward_index = divmod(offset, REWARD_CODE_STRIDE)
    if reward_index >= REWARDS_PER_MODE:
        return None
    return GameMode(mode_idx), reward_index
