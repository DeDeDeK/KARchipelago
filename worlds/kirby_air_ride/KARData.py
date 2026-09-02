from enum import IntEnum


class GameMode(IntEnum):
    """Checklist modes the client tracks. 0-2 mirror the mod's GameMode enum; ARCHIPELAGO is the
    synthetic 4th "Archipelago checklist" mode.

    These are ROW indices - what every per-mode array on the wire is indexed by. The AP tab's *runtime*
    index is assigned dynamically by the custom_checklist framework and may be higher; the mod maps it
    back to this row. LOCATIONS_* stays 3 wide: the AP checklist awards no native rewards of its own."""

    AIRRIDE = 0
    TOPRIDE = 1
    CITYTRIAL = 2
    ARCHIPELAGO = 3


class RewardType(IntEnum):
    """Mirrors the mod's RewardType enum (`RewardEntry.reward_type`). Only the types no gating category
    owns are listed - machines, colors, stadiums, courses and Top Ride items are unlocked by their own
    category's item, and the Dragoon/Hydra part markers are progression."""

    FILLER = 0x00
    BONUS_MOVIE = 0x01
    EXTRA_RULE = 0x02
    SOUND_TEST = 0x04
    MUSIC = 0x05
    ENDING = 0x06
    PAUSE_POWERUPS = 0x08


# Bits per checklist mode in OPTION_CHECKLIST_REWARD_PLACED_TYPES. RewardType tops out at
# PAUSE_POWERUPS (8), so the three reward-bearing modes pack into 27 bits of the u32.
CHECKLIST_REWARD_MODE_BITS = 9


def checklist_reward_placed_bit(mode: GameMode, reward_type: RewardType) -> int:
    """Bit index of (mode, reward_type) in OPTION_CHECKLIST_REWARD_PLACED_TYPES. Only AIRRIDE, TOPRIDE
    and CITYTRIAL are addressable - the Archipelago checklist awards no native rewards."""
    return mode * CHECKLIST_REWARD_MODE_BITS + reward_type


class GoalKind(IntEnum):
    """Mirrors the mod's GoalKind enum. Value written to OPTION_GOAL_<MODE>."""

    CHECKLIST_100 = 0
    N_CHECKLIST = 1
    HYDRA_AND_DRAGOON = 2
    BEAT_KING_DEDEDE = 3
    NONE = 4
    CHECKLIST_LIST = 5
    MAX_STATS_CT = 6
    ASSEMBLE_AP_STAR = 7
    ALL_LEGENDARIES_CT = 8


class GoalForcedGate(IntEnum):
    """Mirrors the mod's GOALGATE_* bits. Written as a bitmask to OPTION_GOAL_FORCED_GATES.

    Each bit names unlocks that stay locked at connect even though their category's gate is off,
    because the seed's goal is exactly what they gate."""

    LEGENDARY_PIECES = 0x1
    VS_KING_DEDEDE = 0x2
    AP_STAR_PIECES = 0x4


class TrapLinkKind(IntEnum):
    """Mirrors the mod's TrapLinkKind enum."""

    BAD_PATCH = 1
    SLEEP = 2
    SPEED_DOWN = 3


class APTextColor(IntEnum):
    """Mirrors the mod's APTextColor enum. DEFAULT follows the textbox's own default color;
    the rest are Archipelago's CommonClient GUI palette, by name."""

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
    """Mirrors the mod's APTextKind enum. Each kind has its own in-game Settings toggle,
    mirrored back to the client as a bit of TEXT_MENU_MASK."""

    CHECK = 0
    ITEM = 1
    HINT = 2
    STATUS = 3
    CHAT = 4


# AP color name -> the mod's palette index. Keys are the CommonClient GUI color names; anything
# outside this set (bold/underline, the *_bg terminal codes) has no in-game equivalent.
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
    # GameCube MEM1 cached address range (24 MB). The mod's APData struct always lands here, so a pointer
    # outside it is stale. MEM1_START also bases the game-id check (the disc id sits at MEM1's start).
    MEM1_START = 0x80000000
    MEM1_END = 0x81800000

    # Static pointer to the APData struct, written by the mod in OnBoot(); poll until non-zero.
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
    # TrapLink send flag. Game writes 1 (rapidly, so the client debounces), client reads and clears to 0.
    TRAPLINK_SEND = 0x01C  # u32
    # Item delivery mailbox. Client writes AP item ID, game reads and clears to 0; 0 means empty.
    INCOMING_ITEM_ID = 0x020  # u32
    # Items the game has received from the mailbox. Game increments on receipt; client reads only.
    ITEM_RECEIVED_INDEX = 0x024  # u32

    # Handshake fields

    # 1 when mod is fully initialized and save data is loaded. Client polls until 1.
    GAME_READY = 0x028  # u32
    # Client writes 1 after all option fields are written. The game takes the options in, republishes
    # the live menu mirrors below, and clears it back to 0 - so this doubles as the transfer ack, and
    # the client must not diff those mirrors until it reads 0 here.
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
    # Which checklist reward types the world placed as AP items, from the `checklist_rewards` option.
    # The mod unlocks every unset type at connect; bit N = RewardType N.
    OPTION_CHECKLIST_REWARD_PLACED_TYPES = 0x0E8  # u32 bitmask, 1 << RewardType
    # Unlocks the pool ships even though their category's gate is off, because this seed's goal is the
    # thing they gate. The mod withholds exactly these bits when it pre-fills that category's mask.
    OPTION_GOAL_FORCED_GATES = 0x0EC  # u32 bitmask, GOAL_FORCED_GATE_*
    # AP Patch locations in this seed, 0 = category off. The mod accepts and clamps to
    # AP_PATCH_MOD_MAX; the option only ever sends up to AP_PATCH_CODE_MAX.
    OPTION_AP_PATCHES = 0x0F0  # u32, 0-AP_PATCH_MOD_MAX
    # APSlotOptions is 8-byte aligned (it holds u64s), so 4 bytes of tail padding follow and the
    # block ends at 0x0F8 (200 bytes) with LOCATION_DATA_VALID immediately after.

    # Location data fields

    # Client writes 1 after all location arrays are written. Game reads and clears to 0.
    LOCATION_DATA_VALID = 0x0F8  # u32

    # Location arrays: u16[3][46], locations[source_mode][source_reward_index], 92 bytes per mode. Value
    # is (target_mode << 8) | clear_kind for a local placement, 0xFFFF for remote or unused slots. The AP
    # checklist awards no native rewards, so it has no array.
    LOCATIONS_AIRRIDE = 0x0FC  # u16[46], 92 bytes (reward indices 0-45)
    LOCATIONS_TOPRIDE = 0x158  # u16[46], 92 bytes (reward indices 0-45; only 0-32 used)
    LOCATIONS_CITYTRIAL = 0x1B4  # u16[46], 92 bytes (reward indices 0-45; only 0-43 used)

    # Check detection fields

    # Bitmask of completed checkboxes per mode, game-written: bit (k % 64) of word (k / 64) for
    # clear_kind k.
    SENT_CHECKS_AIRRIDE = 0x210  # u64[2], 16 bytes
    SENT_CHECKS_TOPRIDE = 0x220  # u64[2], 16 bytes
    SENT_CHECKS_CITYTRIAL = 0x230  # u64[2], 16 bytes
    SENT_CHECKS_ARCHIPELAGO = 0x240  # u64[2], 16 bytes

    # Backfill bitmask. Client writes bits for checks the server knows but the mod doesn't (fresh save,
    # slot takeover, !collect); the game ORs into sent_checks, updates clear[], re-checks goal, clears.
    CLIENT_BACKFILL_AIRRIDE = 0x250  # u64[2], 16 bytes
    CLIENT_BACKFILL_TOPRIDE = 0x260  # u64[2], 16 bytes
    CLIENT_BACKFILL_CITYTRIAL = 0x270  # u64[2], 16 bytes
    CLIENT_BACKFILL_ARCHIPELAGO = 0x280  # u64[2], 16 bytes

    # Sticky goal completion flag. Game writes 1 when goal is satisfied. Client reads.
    GOAL_COMPLETE = 0x290  # u8

    # Live state of the in-game DeathLink/EnergyLink/TrapLink toggles, game-written and diffed against
    # last-seen to forward to the server. The OPTION_*_ENABLED fields only seed the initial values.
    DEATHLINK_MENU_ENABLED = 0x294  # u32
    ENERGYLINK_MENU_ENABLED = 0x298  # u32
    TRAPLINK_MENU_ENABLED = 0x29C  # u32

    # Text queue fields

    # Text mailbox, the same handshake as INCOMING_ITEM_ID: fill TEXT_MSG, then set TEXT_PENDING.
    # The game clears it once the message is on screen, and holds it while the text box has no
    # canvas, so a scene load backpressures instead of losing the message.
    TEXT_PENDING = 0x2A0  # u32
    # Live state of the in-game per-kind message toggles, bit (1 << APTextKind). Game-written; the
    # client reads it to skip composing messages the player has turned off.
    TEXT_MENU_MASK = 0x2A4  # u32
    TEXT_MSG = 0x2A8  # APTextMessage, 256 bytes; see KARText.pack_message for the layout

    # AP Patch fields

    # Bit w*64+i of word w is AP Patch w*64+i, location code AP_PATCH_CODE_BASE + w*64 + i. Same
    # single-writer split as SENT_CHECKS / CLIENT_BACKFILL: the game owns the first, the client the
    # second, and the game ORs the second in and clears it.
    AP_PATCH_CHECKS = 0x3A8  # u64[8], 64 bytes
    AP_PATCH_BACKFILL = 0x3E8  # u64[8], 64 bytes


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

AP_CHECKLIST_CODE_BASE = 361
AP_CHECKLIST_CODE_NUM = 52

AP_PATCH_CODE_BASE = 413
AP_PATCH_CODE_MAX = 200

# The mod's masks are a fixed 512 bits whatever a seed asks for, so the wire arrays are 8 words
# wide and stay that width independent of how many patches are locations.
AP_PATCH_MOD_MAX = 512
AP_PATCH_WORDS = AP_PATCH_MOD_MAX // 64

# The mod claims the lowest unclaimed patch index, so the block is collected as a linear chain rather
# than a flat pool. Logic mirrors that by splitting it into consecutive groups, each entered from the
# one before it through an event, which gives fill and progression balancing the sphere ordering a flat
# block hides. The size is roughly one City Trial round of collecting at the default box frequency, so a
# group is a sphere's worth of play rather than a fraction of one.
AP_PATCH_GROUP_SIZE = 20
AP_PATCH_GROUP_MAX = (AP_PATCH_CODE_MAX + AP_PATCH_GROUP_SIZE - 1) // AP_PATCH_GROUP_SIZE


def ap_patch_group_sizes(count: int) -> list[int]:
    """Split `count` AP Patches into consecutive group sizes, longest-first. A trailing group under half
    a full one is folded into its predecessor, so a seed never ends on a group too short to be a sphere
    of its own. Empty when the category is off."""
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
    """Decode a checkbox location code to (game_mode, clear_kind). AP Patch codes decode to None -
    they are their own category with no checklist cell."""
    if code is None:
        return None
    if 1 <= code <= 120:
        return GameMode.CITYTRIAL, code - 1
    if 121 <= code <= 240:
        return GameMode.AIRRIDE, code - 121
    if 241 <= code <= 360:
        return GameMode.TOPRIDE, code - 241
    if AP_CHECKLIST_CODE_BASE <= code < AP_CHECKLIST_CODE_BASE + AP_CHECKLIST_CODE_NUM:
        return GameMode.ARCHIPELAGO, code - AP_CHECKLIST_CODE_BASE
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
    """Encode (game_mode, clear_kind) to an AP location code, or 0 if it has none."""
    if mode == GameMode.CITYTRIAL:
        return clear_kind + 1
    if mode == GameMode.AIRRIDE:
        return clear_kind + 121
    if mode == GameMode.TOPRIDE:
        return clear_kind + 241
    if mode == GameMode.ARCHIPELAGO:
        # The Archipelago band is short-filled and the AP Patch block starts where it
        # ends, so a blank cell encodes to nothing rather than to a patch's code.
        if clear_kind >= AP_CHECKLIST_CODE_NUM:
            return 0
        return clear_kind + AP_CHECKLIST_CODE_BASE
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
