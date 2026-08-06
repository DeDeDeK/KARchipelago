from enum import IntEnum


class GameMode(IntEnum):
    """Checklist modes the client tracks. 0-2 mirror the mod's GameMode enum; ARCHIPELAGO is the
    synthetic 4th "Archipelago checklist" mode.

    These are checklist-mode ROW indices - what every per-mode array on the wire is indexed by, and what
    the mod stores a reward placement's target as. The AP tab's *runtime* index is assigned dynamically
    by the custom_checklist framework and may be higher; the mod maps it back to this row. The exception
    is LOCATIONS_*, which stays 3 wide: the AP checklist awards no native rewards of its own."""

    AIRRIDE = 0
    TOPRIDE = 1
    CITYTRIAL = 2
    ARCHIPELAGO = 3


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
    # GameCube MEM1 cached address range (24 MB). The mod's APData struct always lands here, so a pointer
    # outside it is stale. MEM1_START also bases the game-id check (the disc id sits at MEM1's start).
    MEM1_START = 0x80000000
    MEM1_END = 0x81800000

    # Static pointer to the APData struct, written by the mod in OnBoot().
    # Read this to get the struct base address; poll until non-zero.
    AP_DATA_POINTER = 0x805D52D4

    # Communication fields (offsets relative to APData struct base)

    # EnergyLink pool balance. Client writes, game reads. s64 raw units (1 unit = 1 MJ), widened to
    # s64 so multiworld pools exceeding u64 joules still fit at MJ scale.
    ENERGY_BALANCE = 0x000  # s64
    # EnergyLink cumulative send counter, s64 signed raw MJ. Game-owned: only the game adds/subtracts,
    # the client reads-and-diffs and NEVER writes. Resets on mod boot; persists across scene loads.
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
    # Reveal every checkbox at the start, per mode. Visual only - unlock state is untouched.
    OPTION_REVEAL_CHECKLIST_AIRRIDE = 0x03C  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_TOPRIDE = 0x040  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_CITYTRIAL = 0x044  # u32, 0 or 1
    OPTION_REVEAL_CHECKLIST_ARCHIPELAGO = 0x048  # u32, 0 or 1
    # Goal per mode (indexed by GameMode). Values are GoalKind.
    OPTION_GOAL_AIRRIDE = 0x04C  # u32
    OPTION_GOAL_TOPRIDE = 0x050  # u32
    OPTION_GOAL_CITYTRIAL = 0x054  # u32
    OPTION_GOAL_ARCHIPELAGO = 0x058  # u32
    # N for GOAL_N_CHECKLIST, per mode.
    OPTION_CHECKLIST_AMOUNT_AIRRIDE = 0x05C  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_TOPRIDE = 0x060  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_CITYTRIAL = 0x064  # u32, 1-120
    OPTION_CHECKLIST_AMOUNT_ARCHIPELAGO = 0x068  # u32, 1-120
    OPTION_CT_PATCH_CAP_MIN = 0x06C  # u32, 1-30 - per-stat cap the player starts at
    OPTION_CT_PATCH_CAP_MAX = 0x070  # u32, 1-30 - per-stat cap ceiling / Max Stats goal threshold
    # Spawn rate floor (percent), CT + TR items only. 100 = vanilla, 300 = 3x (mod hard cap); sub-100
    # values deliberately suppress spawns and must not be clamped up. Each Spawn Rate Up adds +10%.
    OPTION_SPAWN_RATE_MIN = 0x074  # u32, 10-100

    # Required checkboxes for GOAL_CHECKLIST_LIST, per mode. 2 x u64 (128 bits); bit (k%64) of word
    # (k/64) for clear_kind k. Client writes big-endian u64s; zero-fill modes not using CHECKLIST_LIST.
    OPTION_GOAL_CHECKS_AIRRIDE = 0x078  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_TOPRIDE = 0x088  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_CITYTRIAL = 0x098  # u64[2], 16 bytes
    OPTION_GOAL_CHECKS_ARCHIPELAGO = 0x0A8  # u64[2], 16 bytes

    # Per-category access gating toggles. 1 = gated (players unlock via AP items). 0 = ungated (mod
    # pre-fills that unlock mask all-1s at connect; AP world ships no unlock items for the category).
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
    # Mirrors the KAROptions `city_trial_stadiums_gated` toggle.
    OPTION_STADIUM_GATING_ENABLED = 0x0E0  # u32, 0 or 1
    # Mirrors the KAROptions `base_abilities_gated` toggle. Gates Kirby's inhale / quick spin / machine
    # charge behind AP unlock items.
    OPTION_BASE_ABILITY_GATING_ENABLED = 0x0E4  # u32, 0 or 1
    # Mirrors the `checklist_rewards_gated` toggle. Off => mod unlocks every non-progression checklist
    # reward at connect.
    OPTION_CHECKLIST_REWARDS_GATING_ENABLED = 0x0E8  # u32, 0 or 1
    # APSlotOptions is 8-byte aligned (it holds u64s), so the block ends at 0x0F0 (192 bytes) with
    # LOCATION_DATA_VALID immediately after.

    # Location data fields

    # Client writes 1 after all location arrays are written. Game reads and clears to 0.
    LOCATION_DATA_VALID = 0x0F0  # u32

    # Location arrays: u16[3][46], locations[source_mode][source_reward_index], 92 bytes per mode. Value
    # is (target_mode << 8) | clear_kind for a local placement, 0xFFFF for remote or unused slots. The AP
    # checklist awards no native rewards, so it has no array.
    LOCATIONS_AIRRIDE = 0x0F4  # u16[46], 92 bytes (reward indices 0-45)
    LOCATIONS_TOPRIDE = 0x150  # u16[46], 92 bytes (reward indices 0-45; only 0-32 used)
    LOCATIONS_CITYTRIAL = 0x1AC  # u16[46], 92 bytes (reward indices 0-45; only 0-43 used)

    # Check detection fields

    # Bitmask of completed checkboxes per mode. Game writes, client reads.
    # 2 x u64 per mode (128 bits). Bit (k % 64) of word (k / 64) for clear_kind k.
    SENT_CHECKS_AIRRIDE = 0x208  # u64[2], 16 bytes
    SENT_CHECKS_TOPRIDE = 0x218  # u64[2], 16 bytes
    SENT_CHECKS_CITYTRIAL = 0x228  # u64[2], 16 bytes
    SENT_CHECKS_ARCHIPELAGO = 0x238  # u64[2], 16 bytes

    # Backfill bitmask. Client writes bits for checks the server knows but the mod doesn't (fresh save,
    # slot takeover, !collect); the game ORs into sent_checks, updates clear[], re-checks goal, clears.
    CLIENT_BACKFILL_AIRRIDE = 0x248  # u64[2], 16 bytes
    CLIENT_BACKFILL_TOPRIDE = 0x258  # u64[2], 16 bytes
    CLIENT_BACKFILL_CITYTRIAL = 0x268  # u64[2], 16 bytes
    CLIENT_BACKFILL_ARCHIPELAGO = 0x278  # u64[2], 16 bytes

    # Sticky goal completion flag. Game writes 1 when goal is satisfied. Client reads.
    GOAL_COMPLETE = 0x288  # u8

    # Live menu toggle mirrors, game-written and client-read-only: the authoritative state of the in-game
    # DeathLink/EnergyLink/TrapLink toggles, diffed against last-seen to forward to the server. The
    # OPTION_*_ENABLED slot fields set initial values on first connect only, not on later toggles.
    DEATHLINK_MENU_ENABLED = 0x28C  # u32
    ENERGYLINK_MENU_ENABLED = 0x290  # u32
    TRAPLINK_MENU_ENABLED = 0x294  # u32


# AP item code layout for checklist rewards: 500..649 in 3 mode bands of stride 50 (500-549 Air Ride,
# 550-599 Top Ride, 600-649 City Trial), band order matching GameMode.
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

# Per-mode base addresses for the game-writes-checked-bits u64[2] bitmasks. Includes the AP checklist,
# so its completed boxes are forwarded as checks like any mode's.
SENT_CHECKS_PER_MODE: dict[GameMode, MemoryAddress] = {
    GameMode.AIRRIDE: MemoryAddress.SENT_CHECKS_AIRRIDE,
    GameMode.TOPRIDE: MemoryAddress.SENT_CHECKS_TOPRIDE,
    GameMode.CITYTRIAL: MemoryAddress.SENT_CHECKS_CITYTRIAL,
    GameMode.ARCHIPELAGO: MemoryAddress.SENT_CHECKS_ARCHIPELAGO,
}

# Per-mode base addresses for the client-writes-backfill-bits u64[2] bitmasks, AP checklist included.
# Must stay key-for-key with SENT_CHECKS_PER_MODE: _handle_backfill diffs one against the other.
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


def location_code_to_mode_clear(code: int | None) -> tuple[GameMode, int] | None:
    """Decode an AP location code (1-480) to (game_mode, clear_kind)."""
    if code is None:
        return None
    if 1 <= code <= 120:
        return GameMode.CITYTRIAL, code - 1
    if 121 <= code <= 240:
        return GameMode.AIRRIDE, code - 121
    if 241 <= code <= 360:
        return GameMode.TOPRIDE, code - 241
    if 361 <= code <= 480:
        return GameMode.ARCHIPELAGO, code - 361
    return None


def mode_clear_to_location_code(mode: GameMode, clear_kind: int) -> int:
    """Encode (game_mode, clear_kind) to an AP location code."""
    if mode == GameMode.CITYTRIAL:
        return clear_kind + 1
    if mode == GameMode.AIRRIDE:
        return clear_kind + 121
    if mode == GameMode.TOPRIDE:
        return clear_kind + 241
    if mode == GameMode.ARCHIPELAGO:
        return clear_kind + 361
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
