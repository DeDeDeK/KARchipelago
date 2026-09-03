import asyncio
import contextlib
import time
import uuid
from collections import deque
from typing import Any, ClassVar

import Utils
from CommonClient import CommonContext as APCommonContext
from CommonClient import get_base_parser, logger, server_loop
from NetUtils import (
    ClientStatus,
    JSONMessagePart,
    JSONTypes,
    NetworkItem,
    add_json_item,
    add_json_location,
    add_json_text,
)

from .DolphinInterface import DolphinInterface
from .KARData import (
    AP_PATCH_CODE_MAX,
    AP_PATCH_WORDS,
    CLIENT_BACKFILL_PER_MODE,
    LOCATIONS_PER_MODE,
    OPTION_GOAL_CHECKS_PER_MODE,
    OPTION_REVEAL_CHECKLIST_PER_MODE,
    REWARDS_PER_MODE,
    SENT_CHECKS_PER_MODE,
    APTextColor,
    APTextKind,
    GameMode,
    GoalForcedGate,
    GoalKind,
    MemoryAddress,
    TrapLinkKind,
    ap_patch_index_to_location_code,
    location_code_to_ap_patch_index,
    location_code_to_mode_clear,
    mode_clear_to_location_code,
    reward_code_to_mode_index,
)
from .KARItems import MODE_VICTORY_EVENTS
from .KARLocations import LOCATION_TABLE
from .KARText import (
    RELAYED_PRINT_JSON,
    Segment,
    SegmentCollector,
    add_hint_prefix,
    pack_message,
    relay_segments,
)

# Universal Tracker integration: subclass UT's context when installed, gaining its tracker tab and commands.
try:
    from worlds.tracker import TrackerClient  # ty: ignore[unresolved-import]

    ClientCommandProcessor = TrackerClient.TrackerCommandProcessor
    CommonContext = TrackerClient.TrackerGameContext
    tracker_version = getattr(TrackerClient, "UT_VERSION", "of unknown version")
    tracker_loaded = True
except ImportError:
    from CommonClient import ClientCommandProcessor

    CommonContext = APCommonContext
    tracker_version = ""
    tracker_loaded = False

# 1 raw KAR energy unit = 1 MJ in the multiworld pool (AP stores integer Joules).
ENERGY_LINK_EXCHANGE_RATE = 1_000_000

# Sent in the outgoing Bounce so other worlds can translate to local equivalents.
TRAPLINK_NAMES: dict[TrapLinkKind, str] = {
    TrapLinkKind.BAD_PATCH: "Bad Patch",
    TrapLinkKind.SLEEP: "Sleep",
    TrapLinkKind.SPEED_DOWN: "Speed Down",
}

# Poll period for the Dolphin sync task, and the wait before retrying a failed attach. Neither
# direction is event-driven - server items are written on a tick, game events (checks, energy sends,
# deathlink/traplink, goal) are found on one - so the poll period is the latency floor throughout.
DOLPHIN_POLL_INTERVAL = 0.1
DOLPHIN_RETRY_INTERVAL = 5.0

# Menu labels for the per-kind message toggles, for the log line when one is flipped in-game.
AP_TEXT_KIND_LABELS: dict[APTextKind, str] = {
    APTextKind.CHECK: "Check",
    APTextKind.ITEM: "Item",
    APTextKind.HINT: "Hint",
    APTextKind.STATUS: "Status",
    APTextKind.CHAT: "Chat",
}

GOAL_NAMES: dict[GoalKind, str] = {
    GoalKind.CHECKLIST_100: "100 Checklist Blocks",
    GoalKind.N_CHECKLIST: "N Checklist Blocks",
    GoalKind.HYDRA_AND_DRAGOON: "Hydra and Dragoon",
    GoalKind.BEAT_KING_DEDEDE: "Beat King Dedede",
    GoalKind.NONE: "None",
    GoalKind.CHECKLIST_LIST: "Checklist List",
    GoalKind.MAX_STATS_CT: "Max Stats CT",
    GoalKind.ASSEMBLE_AP_STAR: "Assemble Archipelago Star",
    GoalKind.ALL_LEGENDARIES_CT: "Assemble All Three Legendaries in One Run",
}


# Friendly text for DolphinInterface.status_name()'s raw DME status values, so
# "Not connected" can say *why* (Dolphin closed vs open-but-unreadable).
_DOLPHIN_STATUS_TEXT = {
    "hooked": "hooked",
    "notRunning": "Dolphin not running",
    "noEmu": "Dolphin running, but no game/emulation detected",
    "unHooked": "not hooked yet",
    "unknown": "status unavailable",
}


def log_color(ctx: CommonContext, text: str, color: str = "white") -> None:
    """Log `text` in `color` to the GUI log, the terminal, and the log file.

    Plain `logger` calls cannot be colored - the Kivy GUI escapes markup in log records - so this routes
    through `on_print_json`, which sends nothing to the server and works while disconnected. `color` must
    name a `NetUtils.JSONtoTextParser.color_codes` entry; `orange` is GUI-only.
    """
    parts: list[JSONMessagePart] = []
    add_json_text(parts, text, type=JSONTypes.color, color=color)
    ctx.on_print_json({"data": parts, "cmd": "PrintJSON"})


def log_toggle(name: str, enabled: bool) -> None:
    """Record an in-game menu toggle in the log file only. The player made the change on screen and
    the mod already acknowledged it there, so repeating it in the GUI and terminal is noise."""
    log_quiet(f"{name} toggled {'on' if enabled else 'off'} from in-game menu.")


def log_quiet(text: str) -> None:
    """Log `text` to the log file only, keeping it out of the terminal and the GUI.

    For handshake bookkeeping worth reading after the fact but noise during play. `logger.debug` will not
    do: `init_logging` leaves the root logger at INFO with no flag to lower it. `NoStream` filters the
    stdout handler; `skip_gui` is checked by `kvui.LogtoUI.handle`.
    """
    logger.info(text, extra={"NoStream": True, "skip_gui": True})


class KARCommandProcessor(ClientCommandProcessor):
    def _cmd_dolphin(self) -> None:
        """Display the current Dolphin emulator connection status."""
        if not isinstance(self.ctx, KARContext):
            return
        ctx = self.ctx
        status, color = self._status(ctx)
        log_color(ctx, f"Dolphin Status: {status}", color)

    @staticmethod
    def _status(ctx: "KARContext") -> tuple[str, str]:
        """The connection state as (text, color). Yellow means hooked but mid-handshake; the red and
        green branches below override it."""
        color = "yellow"
        if not ctx.dolphin.is_hooked():
            color = "red"
            # Prefer the last attempt's real outcome (e.g. "hooked, but the game id was wrong") over
            # the bare DME status, which after an unhook is just "unHooked" and hides that we attached.
            if ctx.last_attach_detail:
                status = f"Not connected - {ctx.last_attach_detail}"
            else:
                name = ctx.dolphin.status_name()
                status = f"Not connected ({_DOLPHIN_STATUS_TEXT.get(name, name)})"
        elif not ctx.dolphin.check_game_running():
            status = "Hooked, game not running"
            color = "red"
        elif ctx.ap_data_base is None:
            status = "Waiting for APData struct"
        elif not ctx.game_ready:
            status = "Waiting for game ready"
        elif not ctx.options_written:
            status = "Waiting for slot options"
        elif not ctx.locations_written:
            status = "Waiting for location data"
        else:
            status = "Connected"
            color = "green"
        return status, color


class KARContext(CommonContext):
    game = "Kirby Air Ride"
    # UT tags its own context "Tracker", which makes it connect as a spectator with no game. This
    # client is the real game client, so reset the tag set to the plain one.
    tags: ClassVar[set[str]] = {"AP"}
    items_handling = 0b111
    want_slot_data = True
    command_processor = KARCommandProcessor

    def __init__(self, server_address: str | None, password: str | None) -> None:
        super().__init__(server_address, password)
        self.dolphin = DolphinInterface()
        self.dolphin_sync_task: asyncio.Task[None] | None = None
        self._dolphin_was_connected: bool | None = None
        # Last Dolphin connect result, shown by /dolphin; the _logged copy keeps the retry loop from repeating it.
        self.last_attach_detail: str | None = None
        self._logged_attach_detail: str | None = None

        # APData struct base address (resolved from static pointer).
        self.ap_data_base: int | None = None

        self.game_ready = False
        self.options_written = False
        self.options_acked = False
        self.locations_written = False

        # Slot data received from the AP server on connect.
        self.slot_options: dict[str, Any] = {}

        # Location arrays built from scout results. Per-mode u16[REWARDS_PER_MODE], default 0xFFFF (remote).
        self.location_arrays: dict[GameMode, list[int]] = {m: [0xFFFF] * REWARDS_PER_MODE for m in GameMode}
        self.location_arrays_ready = False
        # Outstanding scouted location IDs: populated on LocationScouts, drained as LocationInfo
        # replies arrive. Ready flag flips only when empty, so split replies can't signal early.
        self.pending_scout_ids: set[int] = set()

        # Index into items_received: next item to deliver to the game via the mailbox.
        self.item_send_index = 0

        # Last-seen sent_checks bitmask from game memory. Per mode: [word0, word1].
        self.last_sent_checks: dict[GameMode, list[int]] = {m: [0, 0] for m in GameMode}
        # Last-seen AP Patch bitmask from game memory, one flat block of AP_PATCH_WORDS words.
        self.last_ap_patch_checks: list[int] = [0] * AP_PATCH_WORDS

        # Backfill: True when the client should write server-known checks the game is missing.
        self.backfill_pending = False

        # TrapLink: pending incoming traps and dedupe state.
        self.pending_trap_receives = 0
        # Timestamp of the most recently accepted incoming TrapLink bounce, used to dedupe server
        # resends (the AP server may re-broadcast a bounce on reconnect or proto-level retry).
        self.last_traplink_receive = 0.0

        # EnergyLink.
        self.energy_link_enabled = False
        # `{tag: expected_subtraction_joules}`, reconciled against SetReply to catch server-clamped withdrawals.
        self.pending_energy_withdrawals: dict[str, int] = {}
        # Watermark on the game's energy_sent_total, so we diff forward. None means "needs (re)seeding".
        self.energy_last_seen: int | None = None

        # In-game text. Composed wherever the event happens, packed immediately, and handed to the
        # mod's mailbox one per poll, so Dolphin access stays in one place. Unbounded: goaling a
        # world releases every check this slot placed at once, and each is a 256-byte record.
        self.text_out: deque[bytes] = deque()
        self.segment_parser = SegmentCollector(self)
        # Mirrors the in-game Messages menu. Chat starts off, matching the mod's defaults, until
        # the first _poll_menu_toggles read replaces these with the real state.
        self.text_enabled: dict[APTextKind, bool] = {k: k is not APTextKind.CHAT for k in APTextKind}

    def _reset_dolphin_state(self) -> None:
        """Reset state tied to the Dolphin connection / mod memory. Safe to call whenever the hook drops
        or the APData pointer changes; this state is rebuilt from memory on the next handshake."""
        self.ap_data_base = None
        self.game_ready = False
        self.options_written = False
        self.options_acked = False
        self.locations_written = False
        self.item_send_index = 0
        self.last_sent_checks = {m: [0, 0] for m in GameMode}
        self.last_ap_patch_checks = [0] * AP_PATCH_WORDS
        self.energy_last_seen = None
        self.text_out.clear()

    def _reset_server_state(self) -> None:
        """Reset state tied to the AP server session (scouts, bounces). Only call on an actual server
        disconnect, not on Dolphin flapping: server packets populate this once per session."""
        self.location_arrays = {m: [0xFFFF] * REWARDS_PER_MODE for m in GameMode}
        self.location_arrays_ready = False
        self.pending_scout_ids.clear()
        self.backfill_pending = False
        self.pending_trap_receives = 0

    def _reset_game_state(self) -> None:
        """Reset everything: both Dolphin and server-side state."""
        self._reset_dolphin_state()
        self._reset_server_state()

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            # Not super(): under the UT swap that is TrackerGameContext.server_auth, which sends its
            # own Connect, and we would then send a second one below.
            await APCommonContext.server_auth(self, password_requested)
        await self.get_username()
        await self.send_connect()

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        self.auth = None
        self._reset_game_state()
        await super().disconnect(allow_autoreconnect)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        # UT drives its tracker off network packets, so it has to see them first. A no-op otherwise.
        super().on_package(cmd, args)
        if cmd == "Connected":
            self._handle_connected(args)
        elif cmd == "RoomUpdate":
            if "checked_locations" in args:
                self.backfill_pending = True
        elif cmd == "Bounced":
            self._handle_bounced(args)
        elif cmd == "LocationInfo":
            self._handle_location_info(args)
        elif cmd == "SetReply":
            self._handle_set_reply(args)
        elif cmd == "InvalidPacket":
            self._handle_invalid_packet(args)

    def _handle_invalid_packet(self, args: dict[str, Any]) -> None:
        """Server rejected a packet we sent. InvalidPacket doesn't echo the offending packet, so for
        tagged Set flows we cannot pinpoint which tag failed. Drop all pending_energy_withdrawals to
        prevent an indefinite accounting leak, at the cost of in-flight under-subtraction warnings."""
        logger.error(
            "[KAR] AP server rejected %s: %s",
            args.get("type"),
            args.get("text"),
        )
        if args.get("type") == "Set" and self.pending_energy_withdrawals:
            logger.warning(
                "[KAR] Dropping %d pending EnergyLink withdrawals due to schema error.",
                len(self.pending_energy_withdrawals),
            )
            self.pending_energy_withdrawals.clear()

    def _handle_set_reply(self, args: dict[str, Any]) -> None:
        """Reconcile tagged EnergyLink withdrawals against the server's actual subtraction: for a
        withdrawal (negative add + max:0), `original_value - value` is what the server really took.
        Less than the mod asked for means the pool ran out; log the discrepancy."""
        tag = args.get("tag")
        if not tag or tag not in self.pending_energy_withdrawals:
            return
        expected = self.pending_energy_withdrawals.pop(tag)
        original_value = args.get("original_value")
        value = args.get("value")
        if original_value is None or value is None:
            return
        actual = original_value - value
        if actual < expected:
            shortfall = expected - actual
            logger.warning(
                "[EnergyLink] withdrawal under-subtracted by %d J "
                "(asked %d, got %d). Pool was lower than the mod expected.",
                shortfall,
                expected,
                actual,
            )

    def _handle_connected(self, args: dict[str, Any]) -> None:
        sd = args.get("slot_data", {})
        self.slot_options = sd

        # Reset connection-dependent state so the handshake re-runs. `finished_game` deliberately stays:
        # the base client re-sends StatusUpdate(CLIENT_GOAL) on reconnect while it is True.
        self.options_written = False
        self.options_acked = False
        self.locations_written = False
        self.location_arrays = {m: [0xFFFF] * REWARDS_PER_MODE for m in GameMode}
        self.location_arrays_ready = False
        self.pending_scout_ids.clear()
        self.backfill_pending = True

        Utils.async_start(self.update_death_link(bool(sd.get("death_link", 0))))

        self.energy_link_enabled = bool(sd.get("energy_link", 0))
        Utils.async_start(self._update_link_tag("EnergyLink", self.energy_link_enabled))
        if self.energy_link_enabled:
            self._enable_energy_link()

        # Seeded from the yaml; the in-game menu may override later. Independent of trap_chance - a
        # player can participate in TrapLink without traps in their own pool.
        trap_enabled = bool(sd.get("trap_link", 0))
        Utils.async_start(self._update_link_tag("TrapLink", trap_enabled))

        # Scout all our locations to build the reward→checkbox mapping.
        all_locs = list(self.missing_locations | self.checked_locations)
        if all_locs:
            self.pending_scout_ids = set(all_locs)
            Utils.async_start(
                self.send_msgs(
                    [
                        {
                            "cmd": "LocationScouts",
                            "locations": all_locs,
                            "create_as_hint": 0,
                        }
                    ]
                )
            )
        else:
            self.location_arrays_ready = True

        goals = []
        for mode_name, goal_key, amount_key, goal_loc_key in [
            ("City Trial", "city_trial_goal", "city_trial_checklist_amount", "city_trial_goal_locations"),
            ("Air Ride", "air_ride_goal", "air_ride_checklist_amount", "air_ride_goal_locations"),
            ("Top Ride", "top_ride_goal", "top_ride_checklist_amount", "top_ride_goal_locations"),
            ("Archipelago", "archipelago_goal", "archipelago_checklist_amount", "archipelago_goal_locations"),
        ]:
            goal_val = GoalKind(int(sd.get(goal_key, GoalKind.NONE)))
            if goal_val != GoalKind.NONE:
                goal_str = GOAL_NAMES.get(goal_val, str(int(goal_val)))
                if goal_val == GoalKind.N_CHECKLIST:
                    goal_str += f" ({int(sd.get(amount_key, 60))})"
                elif goal_val == GoalKind.CHECKLIST_LIST:
                    goal_str += f" ({len(sd.get(goal_loc_key, []))} locations)"
                goals.append(f"{mode_name}: {goal_str}")
        if goals:
            log_color(self, f"Goal(s): {', '.join(goals)}", "yellow")

    def _handle_bounced(self, args: dict[str, Any]) -> None:
        tags = args.get("tags", [])
        # The server filters Bounced by tag, but re-check against a race during tag updates and filter
        # our own source so traps don't loop back. `trap_name` is ignored - cross-world names have no
        # clean 1:1 mapping, so KAR rolls a local trap.
        if "TrapLink" in self.tags and "TrapLink" in tags:
            data = args.get("data", {})
            if self.slot is None or data.get("source") == self.player_names.get(self.slot, ""):
                return
            # Dedupe server resends by payload timestamp. Missing or non-numeric `time` accepts once
            # then blocks (won't match the float comparison again until a real timestamp arrives).
            t = data.get("time")
            if isinstance(t, (int, float)) and t == self.last_traplink_receive:
                return
            if isinstance(t, (int, float)):
                self.last_traplink_receive = t
            self.pending_trap_receives += 1

    def _handle_location_info(self, args: dict[str, Any]) -> None:
        """Build location arrays from scout results: for each of our checklist reward items placed at a
        location in our own world, record which checkbox it maps to. Everything else stays 0xFFFF."""
        for raw in args["locations"]:
            item = NetworkItem(*raw) if not isinstance(raw, NetworkItem) else raw
            # Drain regardless of item type - LocationScouts requested every location we own.
            self.pending_scout_ids.discard(item.location)
            # Only care about checklist rewards belonging to us.
            if item.player != self.slot:
                continue
            decoded = reward_code_to_mode_index(item.item)
            if decoded is None:
                continue
            reward_mode, reward_index = decoded
            mapping = location_code_to_mode_clear(item.location)
            if mapping is not None and reward_index < REWARDS_PER_MODE:
                target_mode, clear_kind = mapping
                self.location_arrays[reward_mode][reward_index] = (target_mode << 8) | clear_kind

        if not self.pending_scout_ids:
            self.location_arrays_ready = True
            log_quiet("Location data built from scout results.")

    async def _update_link_tag(self, tag: str, enabled: bool) -> None:
        """Add or drop one link tag, telling the server only when the set actually changed."""
        old = self.tags.copy()
        if enabled:
            self.tags.add(tag)
        else:
            self.tags.discard(tag)
        if old != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    def on_deathlink(self, data: dict[str, Any]) -> None:
        super().on_deathlink(data)
        if "DeathLink" not in self.tags:
            return
        if self.ap_data_base is not None:
            self.dolphin.write_u32(self._addr(MemoryAddress.DEATHLINK_RECEIVE), 1)

    def _addr(self, offset: int) -> int:
        """Compute an absolute Dolphin address from an APData struct offset."""
        assert self.ap_data_base is not None
        return self.ap_data_base + offset

    async def run_dolphin_sync(self) -> None:
        """Poll game memory at a fixed cadence."""
        logger.info("Starting Dolphin connector. Use /dolphin for status information.")
        while not self.exit_event.is_set():
            await asyncio.sleep(DOLPHIN_POLL_INTERVAL)
            try:
                backoff = False
                # One probe per iteration, shared by the branch below and the edge detection:
                # check_game_running is a live read, so asking twice reports a Dolphin that
                # closed mid-tick one iteration sooner at the cost of a second read every tick.
                connected = self.dolphin.is_hooked() and self.dolphin.check_game_running()
                try:
                    if connected:
                        await self._dolphin_tick()
                    else:
                        connected = self._try_connect_dolphin()
                        backoff = not connected
                except Exception as e:  # noqa: BLE001
                    # Any tick failure means the hook is untrustworthy; drop it and re-attach.
                    logger.error(f"Dolphin sync error: {e}")
                    if self.dolphin.is_hooked():
                        self.dolphin.unhook()
                    self._reset_dolphin_state()
                    connected = False

                if connected and not self._dolphin_was_connected:
                    log_color(self, "Dolphin connected.", "green")
                    self.last_attach_detail = None
                    self._logged_attach_detail = None
                elif not connected and self._dolphin_was_connected:
                    # _note_attach_failure logs the reason on the next connect attempt.
                    log_color(self, "Lost connection to Dolphin.", "red")
                self._dolphin_was_connected = connected

                if backoff:
                    await asyncio.sleep(DOLPHIN_RETRY_INTERVAL)
            except Exception as e:  # noqa: BLE001
                # Last-resort guard: this task has no supervisor, so an escaping exception would
                # silently kill the connector. CancelledError is a BaseException, so shutdown still
                # propagates.
                logger.error(f"Unexpected error in Dolphin sync loop: {e}")

    def _try_connect_dolphin(self) -> bool:
        """Attach to Dolphin. True once fully connected; False tells the caller to back off and retry."""
        if self.dolphin.is_hooked():
            self.dolphin.unhook()
        self._reset_dolphin_state()

        self.dolphin.hook()
        if self.dolphin.is_hooked() and self.dolphin.check_game_running():
            return True  # Fully attached; the loop ticks on the next iteration.

        # Not fully connected. Record an accurate reason *before* dropping any hook, so /dolphin and
        # the log reflect the real state instead of the bare "not hooked yet" that unhooking leaves.
        if self.dolphin.is_hooked():
            # DME attached and found a MEM1-sized region, but GKYE01 wasn't at MEM1_START. The bytes there
            # say why: all 0x00 -> no game booted; another valid id -> wrong-region disc (mod is NTSC-U
            # only); arbitrary bytes -> DME picked the wrong MEM1-sized mapping.
            addr = int(MemoryAddress.MEM1_START)
            raw = self.dolphin.read_bytes(addr, 6)
            self._note_attach_failure(
                f"hooked Dolphin, but {addr:#010x} reads {raw!r}, not {self.dolphin.kar_game_id!r}"
            )
            self.dolphin.unhook()
        else:
            # Never attached. status distinguishes no-process from no-emulation.
            status = self.dolphin.status_name()
            if status == "notRunning":
                self._note_attach_failure("no Dolphin process found")
            elif status == "noEmu":
                self._note_attach_failure("Dolphin open, but no emulated game readable yet")
            else:
                # unHooked here means hook() raised; DolphinInterface.hook() logged why.
                self._note_attach_failure(f"hook attempt failed (status: {status})")
        return False

    def _note_attach_failure(self, detail: str) -> None:
        """Record why the latest connect attempt didn't fully connect, and log it only when it changes,
        so an unchanging failure isn't repeated on every retry. Feeds /dolphin."""
        self.last_attach_detail = detail
        if detail != self._logged_attach_detail:
            self._logged_attach_detail = detail
            log_color(self, f"Dolphin not fully connected: {detail}", "red")

    async def _dolphin_tick(self) -> None:
        ptr = self.dolphin.resolve_ap_data()
        if ptr is None:
            if self.ap_data_base is not None:
                log_color(self, "APData pointer lost. Game may have restarted.", "yellow")
                self._reset_dolphin_state()
            return
        if ptr != self.ap_data_base:
            if self.ap_data_base is not None:
                log_color(self, "APData pointer changed. Re-handshaking.", "yellow")
                self._reset_dolphin_state()
            self.ap_data_base = ptr
            log_color(self, f"Found APData at {ptr:#010x}", "yellow")

        # Wait for game_ready, and detect restarts. The mod sets it once in OnBoot and never clears it, so
        # reading 0 after a 1 means the game rebooted (APData re-zeroed) and the handshake must re-run.
        game_ready_mem = self.dolphin.read_u32(self._addr(MemoryAddress.GAME_READY))
        if not self.game_ready:
            if game_ready_mem != 1:
                return
            self.game_ready = True
            log_color(self, "Game initialized and save loaded.", "yellow")
        elif game_ready_mem != 1:
            log_color(self, "game_ready cleared - game restarted. Re-handshaking.", "yellow")
            self._reset_dolphin_state()
            return

        if not self.options_written:
            if not self.slot_options:
                return  # Waiting for AP server Connected packet.
            self._write_options()
            self.options_written = True
            self.item_send_index = self.dolphin.read_u32(self._addr(MemoryAddress.ITEM_RECEIVED_INDEX))
            log_color(self, f"Options written. Game has received {self.item_send_index} items.", "yellow")

        # The mod clears options_valid once it has taken the options in and republished the live menu
        # mirrors. Until then those mirrors still hold the save's own defaults, and diffing the link
        # toggles against them reads as the player having turned the links off in the menu - which
        # drops the DeathLink and TrapLink tags for as long as it takes to correct.
        if not self.options_acked:
            if self.dolphin.read_u32(self._addr(MemoryAddress.OPTIONS_VALID)) != 0:
                return
            self.options_acked = True

        if not self.locations_written:
            if not self.location_arrays_ready:
                return  # Waiting for LocationInfo scout response.
            self._write_location_data()
            self.locations_written = True
            log_color(self, "Location data written. Client fully operational.", "green")
            self._push_text(APTextKind.STATUS, self._client_status_segments(True))

            # Re-arm on every handshake, not just on "Connected": a mod restart with a fresh save leaves
            # the AP session alive, so the server knows checks the save lacks.
            self.backfill_pending = True

        await self._poll_game()

    def _write_options(self) -> None:
        """Write all APSlotOptions fields to game memory and signal options_valid."""
        sd = self.slot_options
        d = self.dolphin
        a = self._addr

        d.write_u32(a(MemoryAddress.OPTION_DEATH_LINK_ENABLED), int(bool(sd.get("death_link", 0))))
        d.write_u32(a(MemoryAddress.OPTION_ENERGY_LINK_ENABLED), int(bool(sd.get("energy_link", 0))))
        d.write_u32(a(MemoryAddress.OPTION_TRAP_LINK_ENABLED), int(bool(sd.get("trap_link", 0))))
        # Start-revealed checklists, per mode.
        for addr, key in OPTION_REVEAL_CHECKLIST_PER_MODE.values():
            d.write_u32(a(addr), int(bool(sd.get(key, 0))))

        # Goals per mode: option values map directly to the GoalKind enum.
        d.write_u32(a(MemoryAddress.OPTION_GOAL_AIRRIDE), int(sd.get("air_ride_goal", 4)))
        d.write_u32(a(MemoryAddress.OPTION_GOAL_TOPRIDE), int(sd.get("top_ride_goal", 4)))
        d.write_u32(a(MemoryAddress.OPTION_GOAL_CITYTRIAL), int(sd.get("city_trial_goal", 0)))
        d.write_u32(a(MemoryAddress.OPTION_GOAL_ARCHIPELAGO), int(sd.get("archipelago_goal", 4)))

        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_AIRRIDE), int(sd.get("air_ride_checklist_amount", 60)))
        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_TOPRIDE), int(sd.get("top_ride_checklist_amount", 60)))
        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_CITYTRIAL), int(sd.get("city_trial_checklist_amount", 60)))
        d.write_u32(
            a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_ARCHIPELAGO), int(sd.get("archipelago_checklist_amount", 25))
        )

        d.write_u32(a(MemoryAddress.OPTION_AP_PATCHES), int(sd.get("ap_patches", 0)))
        d.write_u32(a(MemoryAddress.OPTION_CT_PATCH_CAP_MIN), int(sd.get("city_trial_patch_cap_min", 18)))
        d.write_u32(a(MemoryAddress.OPTION_CT_PATCH_CAP_MAX), int(sd.get("city_trial_patch_cap_max", 18)))
        d.write_u32(a(MemoryAddress.OPTION_SPAWN_RATE_MIN), int(sd.get("spawn_rate_min", 100)))

        # Goal checks bitmasks for GOAL_CHECKLIST_LIST.
        goal_loc_keys = {
            GameMode.AIRRIDE: "air_ride_goal_locations",
            GameMode.TOPRIDE: "top_ride_goal_locations",
            GameMode.CITYTRIAL: "city_trial_goal_locations",
            GameMode.ARCHIPELAGO: "archipelago_goal_locations",
        }
        for mode, addr in OPTION_GOAL_CHECKS_PER_MODE.items():
            self._write_goal_checks_bitmask(mode, sd.get(goal_loc_keys[mode], []), a(addr))

        # Per-category access gating. 1 = gated (AP unlock items required); 0 = ungated (mod pre-fills
        # the unlock mask at connect). Stadiums gate on `city_trial_stadiums_gated` like the rest.
        d.write_u32(a(MemoryAddress.OPTION_MACHINE_GATING_ENABLED), int(bool(sd.get("machines_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_ABILITY_GATING_ENABLED), int(bool(sd.get("abilities_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_EVENT_GATING_ENABLED), int(bool(sd.get("city_trial_events_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_PATCH_GATING_ENABLED), int(bool(sd.get("city_trial_patches_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_ITEM_GATING_ENABLED), int(bool(sd.get("city_trial_items_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_BOX_GATING_ENABLED), int(bool(sd.get("city_trial_boxes_gated", 1))))
        d.write_u32(
            a(MemoryAddress.OPTION_AIRRIDE_STAGE_GATING_ENABLED), int(bool(sd.get("air_ride_courses_gated", 1)))
        )
        d.write_u32(
            a(MemoryAddress.OPTION_TOPRIDE_STAGE_GATING_ENABLED), int(bool(sd.get("top_ride_courses_gated", 1)))
        )
        d.write_u32(a(MemoryAddress.OPTION_TOPRIDE_ITEM_GATING_ENABLED), int(bool(sd.get("top_ride_items_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_COLOR_GATING_ENABLED), int(bool(sd.get("colors_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_STADIUM_GATING_ENABLED), int(bool(sd.get("city_trial_stadiums_gated", 1))))
        d.write_u32(a(MemoryAddress.OPTION_BASE_ABILITY_GATING_ENABLED), int(bool(sd.get("base_abilities_gated", 0))))
        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_REWARD_PLACED_TYPES), int(sd.get("checklist_rewards", 0)))

        # Goal keys: unlocks the pool ships even with their category ungated, so the mod's pre-fill has
        # to leave them locked. Both default off - an older world ships neither key.
        forced_gates = 0
        if sd.get("legendary_pieces_goal_gated", 0):
            forced_gates |= GoalForcedGate.LEGENDARY_PIECES
        if sd.get("vs_king_dedede_goal_gated", 0):
            forced_gates |= GoalForcedGate.VS_KING_DEDEDE
        if sd.get("ap_star_pieces_goal_gated", 0):
            forced_gates |= GoalForcedGate.AP_STAR_PIECES
        d.write_u32(a(MemoryAddress.OPTION_GOAL_FORCED_GATES), forced_gates)

        d.write_u32(a(MemoryAddress.OPTIONS_VALID), 1)

    def _write_goal_checks_bitmask(self, mode: GameMode, location_names: list | set, addr: int) -> None:
        """Convert a set of location names to a u64[2] bitmask and write to memory."""
        words = [0, 0]
        for name in location_names:
            data = LOCATION_TABLE.get(name)
            if data is None:
                continue
            mapping = location_code_to_mode_clear(data.code)
            if mapping is None or mapping[0] != mode:
                continue
            ck = mapping[1]
            words[ck // 64] |= 1 << (ck % 64)
        self.dolphin.write_u64(addr, words[0])
        self.dolphin.write_u64(addr + 8, words[1])

    def _write_location_data(self) -> None:
        """Write the three location arrays to game memory and signal location_data_valid."""
        for mode, offset in LOCATIONS_PER_MODE.items():
            base_addr = self._addr(offset)
            for i, val in enumerate(self.location_arrays[mode]):
                self.dolphin.write_u16(base_addr + i * 2, val)
        self.dolphin.write_u32(self._addr(MemoryAddress.LOCATION_DATA_VALID), 1)

    async def _poll_game(self) -> None:
        if self.slot is None:
            return
        self._deliver_items()
        await self._check_locations()
        await self._check_goal()
        self._update_ut_goals()
        await self._poll_menu_toggles()
        await self._handle_deathlink()
        await self._handle_traplink()
        await self._handle_energylink()
        self._handle_backfill()
        self._flush_text()

    def _deliver_items(self) -> None:
        """Deliver pending items to the game one at a time via the incoming_item_id mailbox."""
        while self.item_send_index < len(self.items_received):
            if self.dolphin.read_u32(self._addr(MemoryAddress.INCOMING_ITEM_ID)) != 0:
                return  # Game hasn't consumed the previous item yet.
            item = self.items_received[self.item_send_index]
            self.dolphin.write_u32(self._addr(MemoryAddress.INCOMING_ITEM_ID), item.item)
            logger.debug(f"Delivered item #{self.item_send_index}: {self.item_names.lookup_in_game(item.item)}")
            self._push_item_text(item)
            self.item_send_index += 1

    async def _check_locations(self) -> None:
        """Read the sent_checks bitmask and report any newly-set bits."""
        new_checks: set[int] = set()
        for mode, offset in SENT_CHECKS_PER_MODE.items():
            for word_idx in range(2):
                addr = self._addr(offset) + word_idx * 8
                current = self.dolphin.read_u64(addr)
                diff = current & ~self.last_sent_checks[mode][word_idx]
                if diff:
                    self.last_sent_checks[mode][word_idx] = current
                    for bit in range(64):
                        if diff & (1 << bit):
                            code = mode_clear_to_location_code(mode, word_idx * 64 + bit)
                            if code:
                                new_checks.add(code)

        for word_idx in range(AP_PATCH_WORDS):
            addr = self._addr(MemoryAddress.AP_PATCH_CHECKS) + word_idx * 8
            current = self.dolphin.read_u64(addr)
            diff = current & ~self.last_ap_patch_checks[word_idx]
            if diff:
                self.last_ap_patch_checks[word_idx] = current
                for bit in range(64):
                    if diff & (1 << bit):
                        # The mod's mask is AP_PATCH_MOD_MAX bits wide; only the first
                        # AP_PATCH_CODE_MAX of them are locations.
                        index = word_idx * 64 + bit
                        if index < AP_PATCH_CODE_MAX:
                            new_checks.add(ap_patch_index_to_location_code(index))

        if new_checks:
            await self._report_checks(new_checks)

    async def _report_checks(self, new_checks: set[int]) -> None:
        """Report newly completed locations to the server and compose their in-game lines."""
        sent = await self.check_locations(new_checks)
        # A non-empty `sent` already implies a slot; the explicit check just narrows the type.
        if sent and self.slot is not None:
            locations = sorted(sent)
            # Log file only: the server broadcasts its own line for every one of these, so printing
            # them again would double up the client log.
            names = ", ".join(self.location_names.lookup_in_game(loc) for loc in locations)
            log_quiet(f"New checks sent: {names}")
            self._push_check_text(locations)

    def _push_text(self, kind: APTextKind, segments: list[Segment]) -> None:
        """Queue one in-game message. Composition happens at the event; the write happens on the
        next poll, so this is safe to call from the network task and before Dolphin is attached."""
        if not self.text_enabled[kind]:
            return
        payload = pack_message(kind, segments)
        if payload is None:
            return
        self.text_out.append(payload)

    def _flush_text(self) -> None:
        """Hand the next queued message to the mod's mailbox, the same handshake as items.

        A message still pending means the game has not shown it yet - during a scene load it holds
        one for as long as the text box has no canvas - so a full mailbox is backpressure, and the
        deque keeps the whole backlog until it clears.
        """
        if not self.text_out:
            return
        if self.dolphin.read_u32(self._addr(MemoryAddress.TEXT_PENDING)) != 0:
            return
        payload = self.text_out[0]
        # The body has to land before the flag that publishes it.
        if not self.dolphin.write_bytes(self._addr(MemoryAddress.TEXT_MSG), payload):
            return
        self.dolphin.write_u32(self._addr(MemoryAddress.TEXT_PENDING), 1)
        self.text_out.popleft()

    @staticmethod
    def _client_status_segments(connected: bool) -> list[Segment]:
        color = APTextColor.GREEN if connected else APTextColor.RED
        return [Segment("Archipelago client", color), Segment(" connected" if connected else " disconnected")]

    def _announce_disconnect(self) -> None:
        """Make the leaving line the last thing the mod hears from us. The queued backlog is dropped -
        nothing drains it after this - and so is the line itself if the mod is still holding an earlier
        message, since it will not read a second one before the hook goes."""
        if not self.dolphin.is_hooked() or self.ap_data_base is None:
            return
        self.text_out.clear()
        self._push_text(APTextKind.STATUS, self._client_status_segments(False))
        self._flush_text()

    def _push_check_text(self, locations: list[int]) -> None:
        """Compose "<you> sent <item> to <player>" for each location just reported to the server,
        one line per location, worded like the server's own ItemSend.

        `locations_info` holds a scout result for every location this slot owns, so the item and
        its owner are known locally and the line does not wait on a server round trip.
        """
        if self.slot is None:
            return
        for loc in locations:
            info = self.locations_info.get(loc)
            parts: list[JSONMessagePart] = []
            if info is None:
                add_json_text(parts, self.slot, type=JSONTypes.player_id)
                add_json_text(parts, " sent an item")
            # In a LocationInfo result NetworkItem.player is the *receiving* player, not the finder.
            elif self.slot_concerns_self(info.player):
                add_json_text(parts, info.player, type=JSONTypes.player_id)
                add_json_text(parts, " found their ")
                add_json_item(parts, info.item, info.player, info.flags)
            else:
                add_json_text(parts, self.slot, type=JSONTypes.player_id)
                add_json_text(parts, " sent ")
                add_json_item(parts, info.item, info.player, info.flags)
                add_json_text(parts, " to ")
                add_json_text(parts, info.player, type=JSONTypes.player_id)
            self._push_text(APTextKind.CHECK, self.segment_parser.collect(parts))

    def _push_item_text(self, item: NetworkItem) -> None:
        """Compose "<item> received from <player>" as the item goes into the mailbox.

        An item this slot placed for itself is skipped while check messages are on: its check line
        already named it, so the pair would say the same thing twice. With those off this is the
        only line it would get, so it prints. Player 0 is the server's starting inventory.
        """
        own = bool(item.player) and self.slot_concerns_self(item.player)
        if own and self.text_enabled[APTextKind.CHECK]:
            return
        parts: list[JSONMessagePart] = []
        add_json_item(parts, item.item, self.slot, item.flags)
        if own or not item.player:
            add_json_text(parts, " received")
        else:
            add_json_text(parts, " received from ")
            add_json_text(parts, item.player, type=JSONTypes.player_id)
        self._push_text(APTextKind.ITEM, self.segment_parser.collect(parts))

    def on_print_json(self, args: dict[str, Any]) -> None:
        super().on_print_json(args)
        try:
            self._relay_print_json(args)
        except Exception:  # noqa: BLE001
            # This runs inside the server-packet loop; a malformed line must not take it down.
            logger.exception("[KAR] Failed to relay a server message to the game")

    def _relay_print_json(self, args: dict[str, Any]) -> None:
        """Forward the server-authored lines worth seeing in-game. ItemSend is deliberately absent:
        the team gets one for every check anyone makes, and this slot's own are already covered by
        _push_check_text and _push_item_text.

        Relaying keys off `args["type"]`, which only server packets carry - that is what keeps the
        client's own `log_color` lines, which reach `on_print_json` untyped, from looping back in.
        """
        msg_type = args.get("type")
        if msg_type == "Hint":
            self._push_hint_text(args)
            return
        relayed = RELAYED_PRINT_JSON.get(str(msg_type))
        if relayed is None:
            return
        kind, color = relayed
        segments = self.segment_parser.collect(args.get("data", []))
        if not segments:
            return
        self._push_text(kind, relay_segments(segments, color))

    def _push_hint_text(self, args: dict[str, Any]) -> None:
        """A compact hint line: the status rides in the "Hint:" prefix, and the half of the hint
        this slot already knows is dropped.

        The server only sends a hint to the two slots it concerns, so exactly one of "who receives
        the item" and "whose world holds it" is always us, and spelling both out costs the room the
        location name needs.
        """
        raw = args.get("item")
        if raw is None:
            return
        info = raw if isinstance(raw, NetworkItem) else NetworkItem(*raw)
        receiving = int(args.get("receiving", -1))
        finding = info.player  # in a Hint the NetworkItem carries the finding player

        # Naming the half that is this slot would be redundant, and naming both spends the room
        # the location name needs. At most one name is ever shown.
        parts: list[JSONMessagePart] = []
        add_hint_prefix(parts, args.get("data", []))
        if not self.slot_concerns_self(receiving):
            add_json_text(parts, f"{self.player_names.get(receiving, receiving)}'s ", type=JSONTypes.player_name)
        add_json_item(parts, info.item, receiving, info.flags)
        add_json_text(parts, " is at ")
        add_json_location(parts, info.location, finding)
        if self.slot_concerns_self(receiving) and not self.slot_concerns_self(finding):
            add_json_text(parts, f" ({self.player_names.get(finding, finding)})", type=JSONTypes.player_name)

        self._push_text(APTextKind.HINT, self.segment_parser.collect(parts))

    async def _check_goal(self) -> None:
        """Forward the game's goal_complete flag to the AP server as a victory."""
        if self.finished_game:
            return
        if self.dolphin.read_u8(self._addr(MemoryAddress.GOAL_COMPLETE)) == 1:
            self.finished_game = True
            log_color(self, "Goal complete! Sending victory.", "yellow")
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

    def _update_ut_goals(self) -> None:
        """Publish the per-mode goals the game reports satisfied onto the world Universal Tracker
        regenerated from this slot. Its go-mode readout is the world's completion condition, which under
        UT skips goals listed here - logic alone can only say a goal is reachable, never that it is done."""
        if not tracker_loaded:
            return
        world = self.tracker_core.get_current_world()
        if world is None:
            return
        mask = self.dolphin.read_u8(self._addr(MemoryAddress.GOAL_SATISFIED_MASK))
        completed = {MODE_VICTORY_EVENTS[mode] for mode in GameMode if mask & (1 << mode)}
        if completed == world.ut_goals_completed:
            return
        world.ut_goals_completed = completed
        self.updateTracker()

    async def _poll_menu_toggles(self) -> None:
        """Read the mod's live in-game menu toggle mirrors and update AP server state if changed. The
        OPTION_*_ENABLED fields only seed the initial values; the mirrors are the live state."""
        dl_enabled = self.dolphin.read_u32(self._addr(MemoryAddress.DEATHLINK_MENU_ENABLED)) != 0
        dl_currently_on = "DeathLink" in self.tags
        if dl_enabled != dl_currently_on:
            log_toggle("DeathLink", dl_enabled)
            await self.update_death_link(dl_enabled)

        tl_enabled = self.dolphin.read_u32(self._addr(MemoryAddress.TRAPLINK_MENU_ENABLED)) != 0
        tl_currently_on = "TrapLink" in self.tags
        if tl_enabled != tl_currently_on:
            log_toggle("TrapLink", tl_enabled)
            await self._update_link_tag("TrapLink", tl_enabled)

        el_enabled = self.dolphin.read_u32(self._addr(MemoryAddress.ENERGYLINK_MENU_ENABLED)) != 0
        if el_enabled != self.energy_link_enabled:
            log_toggle("EnergyLink", el_enabled)
            self.energy_link_enabled = el_enabled
            await self._update_link_tag("EnergyLink", el_enabled)
            # The pool subscription is one-way: CommonContext has no remove_notify, so a re-enable
            # after a disable reuses the one taken here.
            if el_enabled:
                self._enable_energy_link()

        # The mod filters on render and is the authority; reading the mask just keeps messages the
        # player turned off from being composed and occupying the mailbox.
        mask = self.dolphin.read_u32(self._addr(MemoryAddress.TEXT_MENU_MASK))
        for kind in APTextKind:
            enabled = mask & (1 << int(kind)) != 0
            if enabled != self.text_enabled[kind]:
                log_toggle(f"{AP_TEXT_KIND_LABELS[kind]} messages", enabled)
                self.text_enabled[kind] = enabled

    def _enable_energy_link(self) -> None:
        """Subscribe to the pool and show the GUI's EnergyLink readout."""
        self.set_notify(f"EnergyLink{self.team}")
        if self.ui:
            self.ui.enable_energy_link()

    async def _handle_deathlink(self) -> None:
        if "DeathLink" not in self.tags:
            return

        # forward death to AP server and clear the flag.
        if self.dolphin.read_u32(self._addr(MemoryAddress.DEATHLINK_SEND)) == 1:
            self.dolphin.write_u32(self._addr(MemoryAddress.DEATHLINK_SEND), 0)
            assert self.slot is not None
            name = self.player_names.get(self.slot, "Unknown")
            await self.send_death(f"{name} exploded.")

    async def _handle_traplink(self) -> None:
        if "TrapLink" not in self.tags:
            return

        # Forward trap to AP server. The mod writes a TrapLinkKind enum (>0) into TRAPLINK_SEND; we map it
        # to a name so other worlds can translate. Bursts collapse mod-side into one final u32 per poll.
        kind = self.dolphin.read_u32(self._addr(MemoryAddress.TRAPLINK_SEND))
        if kind != 0:
            self.dolphin.write_u32(self._addr(MemoryAddress.TRAPLINK_SEND), 0)
            assert self.slot is not None
            name = self.player_names.get(self.slot, "Unknown")
            try:
                trap_name = TRAPLINK_NAMES[TrapLinkKind(kind)]
            except ValueError:
                # Mod wrote a kind value this client doesn't know about yet.
                trap_name = "Trap"
            await self.send_msgs(
                [
                    {
                        "cmd": "Bounce",
                        "tags": ["TrapLink"],
                        "data": {"time": time.time(), "source": name, "trap_name": trap_name},
                    }
                ]
            )

        # deliver one pending trap when the game's receive flag is clear.
        if self.pending_trap_receives > 0 and self.dolphin.read_u32(self._addr(MemoryAddress.TRAPLINK_RECEIVE)) == 0:
            self.pending_trap_receives -= 1
            self.dolphin.write_u32(self._addr(MemoryAddress.TRAPLINK_RECEIVE), 1)

    async def _handle_energylink(self) -> None:
        if not self.energy_link_enabled:
            return

        # Sends FIRST, balance write LAST: the balance write seeds from the last server-pushed pool, so
        # running it first would bounce the mod's local decrement back up to a stale value and let the
        # affordability gate overdraw. energy_sent_total is game-owned and cumulative - read-and-diff only.
        raw = self.dolphin.read_u64(self._addr(MemoryAddress.ENERGY_SENT_TOTAL))
        cur = raw - (1 << 64) if raw >= (1 << 63) else raw

        if self.energy_last_seen is None:
            # Seed on connect / after a restart: record the total without applying it, so we diff forward
            # rather than replaying the session. Falls through to refresh the balance.
            self.energy_last_seen = cur
        else:
            delta_mj = cur - self.energy_last_seen
            if delta_mj != 0:
                # Advance the watermark now: a dropped send self-heals on the next diff, since the counter
                # is the source of truth. Restarts are caught upstream by the game_ready 1->0 re-check.
                self.energy_last_seen = cur

                joules = delta_mj * ENERGY_LINK_EXCHANGE_RATE
                ops: list[dict[str, Any]] = [{"operation": "add", "value": joules}]
                if joules < 0:
                    # Withdraw: tag + want_reply so we can match the SetReply and detect server-side
                    # clamping at 0 (pool was emptier than the mod thought).
                    ops.append({"operation": "max", "value": 0})
                    await self._send_energy_withdrawal(uuid.uuid4().hex, joules, ops)
                else:
                    # Deposit: no tag needed, set_notify delivers the updated balance to all clients.
                    await self.send_msgs(
                        [
                            {
                                "cmd": "Set",
                                "key": f"EnergyLink{self.team}",
                                "default": 0,
                                "operations": ops,
                            }
                        ]
                    )

                # Fold our delta into the cached pool so the balance below reflects this spend before the
                # server's SetReply round-trips. set_notify later overwrites the cache with the server's
                # absolute pool; max(0, ...) mirrors the server's withdrawal clamp.
                if self.current_energy_link_value is not None:
                    self.current_energy_link_value = max(0, self.current_energy_link_value + joules)

        # Write the pool balance LAST and unconditionally each poll, so seed polls, no-delta polls and
        # other players' deposits all keep the mod's view fresh. Server stores Joules, the mod raw MJ;
        # floor division because sub-MJ isn't representable mod-side.
        if self.current_energy_link_value is not None:
            raw_mj = self.current_energy_link_value // ENERGY_LINK_EXCHANGE_RATE
            # The mod's field is s64; raw_mj is always non-negative (pool clamped at 0). write_u64 is
            # fine: DME has no signed variant and the bytes are identical for non-negative values.
            self.dolphin.write_u64(self._addr(MemoryAddress.ENERGY_BALANCE), raw_mj)

    async def _send_energy_withdrawal(self, tag: str, joules: int, ops: list[dict[str, Any]]) -> None:
        """Send a tagged withdrawal, then record the tag: send_msgs silently no-ops on a closed socket,
        so a pre-send insert would leak the entry on a drop. Both halves run on the loop that handles
        SetReply, so the reply cannot be processed before the tag is in the dict."""
        await self.send_msgs(
            [
                {
                    "cmd": "Set",
                    "key": f"EnergyLink{self.team}",
                    "default": 0,
                    "tag": tag,
                    "want_reply": True,
                    "operations": ops,
                }
            ]
        )
        self.pending_energy_withdrawals[tag] = -joules  # store as positive expected subtraction

    def _handle_backfill(self) -> None:
        """Write bits to client_backfill for checks the AP server knows about but the game doesn't -
        fresh saves, slot takeovers, and !collect from other players."""
        if not self.backfill_pending:
            return

        # Wait for the game to finish processing previous backfill.
        for off in CLIENT_BACKFILL_PER_MODE.values():
            if self.dolphin.read_u64(self._addr(off)) != 0 or self.dolphin.read_u64(self._addr(off) + 8) != 0:
                return
        for word_idx in range(AP_PATCH_WORDS):
            if self.dolphin.read_u64(self._addr(MemoryAddress.AP_PATCH_BACKFILL) + word_idx * 8) != 0:
                return

        # Build bitmask of all server-known checks.
        server_bits: dict[GameMode, list[int]] = {m: [0, 0] for m in GameMode}
        server_patch_bits: list[int] = [0] * AP_PATCH_WORDS
        for loc_code in self.checked_locations:
            patch_index = location_code_to_ap_patch_index(loc_code)
            if patch_index is not None:
                server_patch_bits[patch_index // 64] |= 1 << (patch_index % 64)
                continue
            mapping = location_code_to_mode_clear(loc_code)
            if mapping is None:
                continue
            mode, ck = mapping
            server_bits[mode][ck // 64] |= 1 << (ck % 64)

        # Diff against the game's sent_checks (using the last-read values to avoid extra reads).
        wrote_any = False
        for mode, backfill_addr in CLIENT_BACKFILL_PER_MODE.items():
            for word_idx in range(2):
                diff = server_bits[mode][word_idx] & ~self.last_sent_checks[mode][word_idx]
                if diff:
                    self.dolphin.write_u64(self._addr(backfill_addr) + word_idx * 8, diff)
                    wrote_any = True
        for word_idx in range(AP_PATCH_WORDS):
            diff = server_patch_bits[word_idx] & ~self.last_ap_patch_checks[word_idx]
            if diff:
                self.dolphin.write_u64(self._addr(MemoryAddress.AP_PATCH_BACKFILL) + word_idx * 8, diff)
                wrote_any = True

        if wrote_any:
            logger.info("Backfilled server-known checks to game.")
        self.backfill_pending = False

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago Kirby Air Ride Client"
        return ui

    async def shutdown(self) -> None:
        self._announce_disconnect()
        if self.dolphin.is_hooked():
            self.dolphin.unhook()
        await super().shutdown()


async def async_main(connect: str | None, password: str | None) -> None:
    ctx = KARContext(connect, password)
    if tracker_loaded:
        logger.info(f"Universal Tracker {tracker_version} found.")
    # No ctx.run_generator(): KARWorld is yaml-less, so UT rebuilds the slot from slot_data on connect.
    if Utils.gui_enabled:
        ctx.run_gui()
    ctx.run_cli()
    await asyncio.sleep(1)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    ctx.dolphin_sync_task = asyncio.create_task(ctx.run_dolphin_sync(), name="dolphin sync")
    try:
        await ctx.exit_event.wait()
    finally:
        # Under Universal Tracker the base class is TrackerGameContext, whose GameWatcher task waits
        # on this one.
        ctx.watcher_event.set()
        # Cancelled rather than waited out: a retry backoff would hold up exit for seconds. Before
        # shutdown(), which drops the hook the poll reads through.
        ctx.dolphin_sync_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ctx.dolphin_sync_task
        await ctx.shutdown()


def main(connect: str | None = None, password: str | None = None) -> None:
    Utils.init_logging("Kirby Air Ride Client")
    import colorama

    try:
        colorama.init()
        asyncio.run(async_main(connect, password))
    finally:
        colorama.deinit()


if __name__ == "__main__":
    parser = get_base_parser()
    args = parser.parse_args()
    main(args.connect, args.password)
