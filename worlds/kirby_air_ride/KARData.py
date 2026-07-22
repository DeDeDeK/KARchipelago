from enum import IntEnum


class GameMode(IntEnum):
    """Mirrors the mod's GameMode enum. Indexes per-mode arrays (locations, goal checks)."""

    AIRRIDE = 0
    TOPRIDE = 1
    CITYTRIAL = 2


class GoalKind(IntEnum):
    """Mirrors the mod's GoalKind enum. Value written to OPTION_GOAL_<MODE>."""

    CHECKLIST_100 = 0
    N_CHECKLIST = 1
    HYDRA_AND_DRAGOON = 2
    BEAT_KING_DEDEDE = 3
    NONE = 4
    CHECKLIST_LIST = 5
    MAX_STATS_CT = 6


class TrapLinkKind(IntEnum):
    """Mirrors the mod's TrapLinkKind enum."""

    BAD_PATCH = 1
    SLEEP = 2
    SPEED_DOWN = 3


class MemoryAddress(IntEnum):
    # GameCube MEM1 cached address range (24 MB). The mod's heap-allocated APData struct always lands
    # here; a pointer outside this window is stale or read before OnBoot wrote the real pointer.
    # MEM1_START is also the read base for the game-id check (the disc's game id sits at MEM1's start).
    MEM1_START = 0x80000000
    MEM1_END = 0x81800000

    # Static pointer to the APData struct, written by the mod in OnBoot().
    # Read this to get the struct base address; poll until non-zero.
    AP_DATA_POINTER = 0x805D52D4

    # Communication fields (offsets relative to APData struct base)

    # EnergyLink pool balance. Client writes, game reads. s64 raw units (1 unit = 1 MJ), widened to
    # s64 so multiworld pools exceeding u64 joules still fit at MJ scale.
    ENERGY_BALANCE = 0x000  # s64
    # EnergyLink cumulative send counter. Game-owned: the game only adds (deposits) / subtracts
    # (withdrawals); the client reads-and-diffs it (delta since last poll) and NEVER writes it. s64
    # signed raw MJ. Resets to 0 on each mod boot; persists across scene loads.
    ENERGY_SENT_TOTAL = 0x008  # s64
    # DeathLink receive flag. Client writes 1, game reads and clears to 0.
    DEATHLINK_RECEIVE = 0x010  # u32
    # DeathLink send flag. Game writes 1, client reads and clears to 0.
    DEATHLINK_SEND = 0x014  # u32
    # TrapLink receive flag. Client writes 1, game reads and clears to 0.
    TRAPLINK_RECEIVE = 0x018  # u32
    # TrapLink send flag. Game writes 1, client reads and clears to 0.
    # Game may set rapidly; client must debounce.
    TRAPLINK_SEND = 0x01C  # u32
    # Item delivery mailbox. Client writes AP item ID, game reads and clears to 0.
    # ID 0 is reserved as the "empty" sentinel.
    INCOMING_ITEM_ID = 0x020  # u32
    # Number of items the game has received from the mailbox.
    # Game increments on receipt (before application). Client reads only.
    ITEM_RECEIVED_INDEX = 0x024  # u32

    # Handshake fields

    # 1 when mod is fully initialized and save data is loaded. Client polls until 1.
    GAME_READY = 0x028  # u32
    # Client writes 1 after all option fields are written. Game reads.
    OPTIONS_VALID = 0x02C  # u32

    # APSlotOptions block (starts at 0x030)

    OPTION_DEATH_LINK_ENABLED = 0x030  # u32, 0 or 1
    OPTION_ENERGY_LINK_ENABLED = 0x034  # u32, 0 or 1
    OPTION_TRAP_LINK_ENABLED = 0x038  # u32, 0 or 1
    OPTION_REVEAL_CHECKLISTS = 0x03C  # u32, 0 or 1
    # Goal per mode (indexed by GameMode). Values are GoalKind.
    OPTION_GOAL_AIRRIDE = 0x040  # u32
    OPTION_GOAL_TOPRIDE = 0x044  # u32
    OPTION_GOAL_CITYTRIAL = 0x048  # u32
    # N for GOAL_N_CHECKLIST, per mode.
    OPTION_CHECKLIST_AMOUNT_AIRRIDE = 0x04C  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_TOPRIDE = 0x050  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_CITYTRIAL = 0x054  # u32, 1-120
    OPTION_CT_PATCH_CAP_MIN = 0x058  # u32, 1-30 - per-stat cap the player starts at
    OPTION_CT_PATCH_CAP_MAX = 0x05C  # u32, 1-30 - per-stat cap ceiling / Max Stats goal threshold
    # Spawn rate floor (percent). Applies to CT + TR items; AR has none to scale. 100 = vanilla, 300 =
    # 3x (mod hard cap). World floors it at 10; sub-100 values suppress spawns below vanilla and must be
    # honored (do not clamp to 100). Each Spawn Rate Up item adds +10% on top.
    OPTION_SPAWN_RATE_MIN = 0x060  # u32, 10-100
    # 4 bytes of padding here (struct contains u64; next field needs 8-byte alignment).

    # Required checkboxes for GOAL_CHECKLIST_LIST, per mode. 2 x u64 (128 bits); bit (k%64) of word
    # (k/64) for clear_kind k. Client writes big-endian u64s; zero-fill modes not using CHECKLIST_LIST.
    OPTION_GOAL_CHECKS_AIRRIDE = 0x068  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_TOPRIDE = 0x078  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_CITYTRIAL = 0x088  # u64[2], 16 bytes

    # Per-category access gating toggles. 1 = gated (players unlock via AP items). 0 = ungated (mod
    # pre-fills that unlock mask all-1s at connect; AP world ships no unlock items for the category).
    OPTION_MACHINE_GATING_ENABLED = 0x098  # u32, 0 or 1
    OPTION_ABILITY_GATING_ENABLED = 0x09C  # u32, 0 or 1
    OPTION_EVENT_GATING_ENABLED = 0x0A0  # u32, 0 or 1
    OPTION_PATCH_GATING_ENABLED = 0x0A4  # u32, 0 or 1
    OPTION_ITEM_GATING_ENABLED = 0x0A8  # u32, 0 or 1
    OPTION_BOX_GATING_ENABLED = 0x0AC  # u32, 0 or 1
    OPTION_AIRRIDE_STAGE_GATING_ENABLED = 0x0B0  # u32, 0 or 1
    OPTION_TOPRIDE_STAGE_GATING_ENABLED = 0x0B4  # u32, 0 or 1
    OPTION_TOPRIDE_ITEM_GATING_ENABLED = 0x0B8  # u32, 0 or 1
    OPTION_COLOR_GATING_ENABLED = 0x0BC  # u32, 0 or 1
    # Mirrors the KAROptions `city_trial_stadiums_gated` toggle.
    OPTION_STADIUM_GATING_ENABLED = 0x0C0  # u32, 0 or 1
    # Mirrors the KAROptions `base_abilities_gated` toggle. Gates Kirby's inhale / quick spin / machine
    # charge behind AP unlock items. APSlotOptions is 8-byte aligned (it holds a u64), so it ends with 4
    # bytes of trailing pad at 0x0CC before LOCATION_DATA_VALID at 0x0D0.
    OPTION_BASE_ABILITY_GATING_ENABLED = 0x0C4  # u32, 0 or 1
    # Mirrors the `checklist_rewards_gated` toggle. Off => mod unlocks every non-progression checklist
    # reward at connect.
    OPTION_CHECKLIST_REWARDS_GATING_ENABLED = 0x0C8  # u32, 0 or 1

    # Location data fields

    # Client writes 1 after all location arrays are written. Game reads and clears to 0.
    LOCATION_DATA_VALID = 0x0D0  # u32

    # Location arrays: u16[3][46], locations[source_mode][source_reward_index], indexed by which
    # vanilla checklist reward the entry refers to. Value: (target_mode << 8) | clear_kind for a local
    # placement (the cell holding this reward), 0xFFFF for remote or unused slots. 92 bytes per mode.
    LOCATIONS_AIRRIDE = 0x0D4  # u16[46], 92 bytes (reward indices 0-45)
    LOCATIONS_TOPRIDE = 0x130  # u16[46], 92 bytes (reward indices 0-45; only 0-32 used)
    LOCATIONS_CITYTRIAL = 0x18C  # u16[46], 92 bytes (reward indices 0-45; only 0-43 used)

    # Check detection fields

    # Bitmask of completed checkboxes per mode. Game writes, client reads.
    # 2 x u64 per mode (128 bits). Bit (k % 64) of word (k / 64) for clear_kind k.
    SENT_CHECKS_AIRRIDE = 0x1E8  # u64[2], 16 bytes
    SENT_CHECKS_TOPRIDE = 0x1F8  # u64[2], 16 bytes
    SENT_CHECKS_CITYTRIAL = 0x208  # u64[2], 16 bytes

    # Backfill bitmask. Client writes bits for checks the AP server knows but the mod doesn't (fresh
    # save / slot takeover / !collect). Game ORs into sent_checks, updates clear[], re-evaluates goal,
    # then clears.
    CLIENT_BACKFILL_AIRRIDE = 0x218  # u64[2], 16 bytes
    CLIENT_BACKFILL_TOPRIDE = 0x228  # u64[2], 16 bytes
    CLIENT_BACKFILL_CITYTRIAL = 0x238  # u64[2], 16 bytes

    # Sticky goal completion flag. Game writes 1 when goal is satisfied. Client reads.
    GOAL_COMPLETE = 0x248  # u8

    # Live menu toggle mirrors. Game writes (on boot, first-connect option transfer, and every menu
    # change); client reads only. Authoritative current state of the in-game DeathLink/EnergyLink/
    # TrapLink toggles; diff against last-seen to forward to the AP server (tags / pool membership).
    # The OPTION_*_ENABLED slot fields set initial values on first connect only, not on later toggles.
    DEATHLINK_MENU_ENABLED = 0x24C  # u32
    ENERGYLINK_MENU_ENABLED = 0x250  # u32
    TRAPLINK_MENU_ENABLED = 0x254  # u32


# AP item code layout for checklist rewards. Codes 500..649 split into 3 mode bands
# of stride 50: 500-549 Air Ride, 550-599 Top Ride, 600-649 City Trial. Indices into
# each band match GameMode (Air Ride=0, Top Ride=1, City Trial=2).
REWARD_CODE_BASE = 500
REWARD_CODE_STRIDE = 50

# Padded reward slots per mode in the mod's locations[3][46] array.
REWARDS_PER_MODE = 46


# Per-mode base addresses for the mod's u16[46] locations array (reward → checkbox mapping).
LOCATIONS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.LOCATIONS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.LOCATIONS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.LOCATIONS_CITYTRIAL,
}

# Per-mode base addresses for the game-writes-checked-bits u64[2] bitmasks.
SENT_CHECKS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.SENT_CHECKS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.SENT_CHECKS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.SENT_CHECKS_CITYTRIAL,
}

# Per-mode base addresses for the client-writes-backfill-bits u64[2] bitmasks.
CLIENT_BACKFILL_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.CLIENT_BACKFILL_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.CLIENT_BACKFILL_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.CLIENT_BACKFILL_CITYTRIAL,
}

# Per-mode base addresses for the GOAL_CHECKLIST_LIST required-checkboxes u64[2] bitmasks.
OPTION_GOAL_CHECKS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.OPTION_GOAL_CHECKS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.OPTION_GOAL_CHECKS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.OPTION_GOAL_CHECKS_CITYTRIAL,
}


def location_code_to_mode_clear(code: int | None) -> tuple[GameMode, int] | None:
    """Decode an AP location code (1-360) to (game_mode, clear_kind)."""
    if code is None:
        return None
    if 1 <= code <= 120:
        return GameMode.CITYTRIAL, code - 1
    if 121 <= code <= 240:
        return GameMode.AIRRIDE, code - 121
    if 241 <= code <= 360:
        return GameMode.TOPRIDE, code - 241
    return None


def mode_clear_to_location_code(mode: GameMode, clear_kind: int) -> int:
    """Encode (game_mode, clear_kind) to an AP location code."""
    if mode == GameMode.CITYTRIAL:
        return clear_kind + 1
    if mode == GameMode.AIRRIDE:
        return clear_kind + 121
    if mode == GameMode.TOPRIDE:
        return clear_kind + 241
    return 0


def reward_code_to_mode_index(code: int | None) -> tuple[GameMode, int] | None:
    """Decode an AP reward item code (500-649) to (source_mode, reward_index)."""
    if code is None:
        return None
    offset = code - REWARD_CODE_BASE
    if not (0 <= offset < 3 * REWARD_CODE_STRIDE):
        return None
    mode_idx, reward_index = divmod(offset, REWARD_CODE_STRIDE)
    return GameMode(mode_idx), reward_index
