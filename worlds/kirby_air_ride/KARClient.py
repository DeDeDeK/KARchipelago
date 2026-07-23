import asyncio
import time
import uuid
from typing import Any

import Utils
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, logger, server_loop
from NetUtils import ClientStatus, NetworkItem

from .DolphinInterface import DolphinInterface
from .KARData import (
    CLIENT_BACKFILL_PER_MODE,
    LOCATIONS_PER_MODE,
    OPTION_GOAL_CHECKS_PER_MODE,
    REWARDS_PER_MODE,
    SENT_CHECKS_PER_MODE,
    GameMode,
    GoalKind,
    MemoryAddress,
    TrapLinkKind,
    location_code_to_mode_clear,
    mode_clear_to_location_code,
    reward_code_to_mode_index,
)
from .KARLocations import LOCATION_TABLE

# 1 raw KAR energy unit = 1 MJ in the multiworld pool (AP stores integer Joules).
ENERGY_LINK_EXCHANGE_RATE = 1_000_000

# Sent in the outgoing Bounce so other worlds can translate to local equivalents.
TRAPLINK_NAMES: dict[TrapLinkKind, str] = {
    TrapLinkKind.BAD_PATCH: "Bad Patch",
    TrapLinkKind.SLEEP: "Sleep",
    TrapLinkKind.SPEED_DOWN: "Speed Down",
}

GOAL_NAMES: dict[GoalKind, str] = {
    GoalKind.CHECKLIST_100: "100 Checklist Blocks",
    GoalKind.N_CHECKLIST: "N Checklist Blocks",
    GoalKind.HYDRA_AND_DRAGOON: "Hydra and Dragoon",
    GoalKind.BEAT_KING_DEDEDE: "Beat King Dedede",
    GoalKind.NONE: "None",
    GoalKind.CHECKLIST_LIST: "Checklist List",
    GoalKind.MAX_STATS_CT: "Max Stats CT",
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


class KARCommandProcessor(ClientCommandProcessor):
    def _cmd_dolphin(self) -> None:
        """Display the current Dolphin emulator connection status."""
        if not isinstance(self.ctx, KARContext):
            return
        ctx = self.ctx
        if not ctx.dolphin.is_hooked():
            # Prefer the last attempt's real outcome (e.g. "hooked, but the game id was wrong") over
            # the bare DME status, which after an unhook is just "unHooked" and hides that we attached.
            if ctx.last_attach_detail:
                status = f"Not connected - {ctx.last_attach_detail}"
            else:
                name = ctx.dolphin.status_name()
                status = f"Not connected ({_DOLPHIN_STATUS_TEXT.get(name, name)})"
        elif not ctx.dolphin.check_game_running():
            status = "Hooked, game not running"
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
        logger.info(f"Dolphin Status: {status}")


class KARContext(CommonContext):
    game = "Kirby Air Ride"
    items_handling = 0b111
    want_slot_data = True
    command_processor = KARCommandProcessor

    def __init__(self, server_address: str | None, password: str | None) -> None:
        super().__init__(server_address, password)
        self.dolphin = DolphinInterface()
        self.dolphin_sync_task: asyncio.Task[None] | None = None
        self._dolphin_was_connected: bool | None = None
        # Human-readable result of the most recent Dolphin connect attempt ("hooked, but the game id
        # is wrong" vs "no process" vs "no emulation"). Surfaced by /dolphin and cleared once fully
        # connected, so status never bottoms out at a bare "not hooked yet" when DME actually attached.
        # _logged_attach_detail dedups the loop log so an unchanging failure is logged once, not each retry.
        self.last_attach_detail: str | None = None
        self._logged_attach_detail: str | None = None

        # APData struct base address (resolved from static pointer).
        self.ap_data_base: int | None = None

        self.game_ready = False
        self.options_written = False
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

        # Backfill: True when the client should write server-known checks the game is missing.
        self.backfill_pending = False

        # TrapLink: pending incoming traps and dedupe state.
        self.pending_trap_receives = 0
        # Timestamp of the most recently accepted incoming TrapLink bounce, used to dedupe server
        # resends (the AP server may re-broadcast a bounce on reconnect or proto-level retry).
        self.last_traplink_receive = 0.0

        # EnergyLink.
        self.energy_link_enabled = False
        # Withdrawals map `{tag: expected_subtraction_joules}`, reconciled against
        # SetReply.original_value - value to detect server-clamped under-withdraws (pool too low).
        self.pending_energy_withdrawals: dict[str, int] = {}
        # Watermark for the game-owned energy_sent_total cumulative counter. None means "needs
        # (re)seeding" - set on connect and after any game restart so we diff forward from the current
        # value rather than replaying history or misreading the boot reset as a giant withdrawal.
        self.energy_last_seen: int | None = None

    def _reset_dolphin_state(self) -> None:
        """Reset state tied to the Dolphin connection/mod memory.

        Safe to call whenever the Dolphin hook drops or the APData pointer
        changes; this state is rebuilt from memory on the next handshake.
        """
        self.ap_data_base = None
        self.game_ready = False
        self.options_written = False
        self.locations_written = False
        self.item_send_index = 0
        self.last_sent_checks = {m: [0, 0] for m in GameMode}
        self.energy_last_seen = None

    def _reset_server_state(self) -> None:
        """Reset state tied to the AP server session (scouts, bounces).

        Only call on actual server disconnect, not on Dolphin flapping,
        since this state is populated by server packets that arrive once
        per session (LocationInfo, RoomUpdate, bounces).
        """
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
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        self.auth = None
        self._reset_game_state()
        await super().disconnect(allow_autoreconnect)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
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
        """Server rejected a packet we sent. InvalidPacket doesn't echo the offending
        packet's contents, so for tagged Set flows we can't pinpoint which tag failed.
        Drop all pending_energy_withdrawals to prevent indefinite accounting leak; the cost is
        losing under-subtraction warnings for any in-flight withdrawal at the time."""
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
        """Reconcile tagged EnergyLink withdrawals against the server's actual subtraction.

        For a withdrawal (negative add + max:0), `original_value - value` is the
        amount the server actually subtracted from the pool. If less than what
        the mod asked to withdraw, the pool ran out; log the discrepancy.
        """
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

        # Reset connection-dependent state so the handshake re-runs. `finished_game` is intentionally
        # NOT reset: the base client re-sends StatusUpdate(CLIENT_GOAL) on reconnect while it stays
        # True, which recovers a post-goal disconnect/reconnect.
        self.options_written = False
        self.locations_written = False
        self.location_arrays = {m: [0xFFFF] * REWARDS_PER_MODE for m in GameMode}
        self.location_arrays_ready = False
        self.pending_scout_ids.clear()
        self.backfill_pending = True

        # DeathLink setup (initial toggle from slot options).
        Utils.async_start(self.update_death_link(bool(sd.get("death_link", 0))))

        # EnergyLink setup.
        self.energy_link_enabled = bool(sd.get("energy_link", 0))
        if self.energy_link_enabled:
            self.set_notify(f"EnergyLink{self.team}")
            if self.ui:
                self.ui.enable_energy_link()

        # TrapLink setup (seed from yaml; the in-game menu may override later). Independent of
        # trap_chance: a player can participate in TrapLink without traps in their own pool.
        trap_enabled = bool(sd.get("trap_link", 0))
        Utils.async_start(self._update_traplink_tags(trap_enabled))

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

        # Log goals for the player.
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
            logger.info(f"Goal(s): {', '.join(goals)}")

    def _handle_bounced(self, args: dict[str, Any]) -> None:
        tags = args.get("tags", [])
        # Defensive: the AP server filters Bounced by tag, but double-check in case of a race during
        # tag updates, and self-source filter so our own traps don't loop back. The incoming
        # `trap_name` is ignored; KAR picks a random local trap since cross-world names have no clean
        # 1:1 mapping to our kinds.
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
        """Build location arrays from scout results.

        For each of our checklist reward items placed at a location in our world,
        record which checkbox it maps to. Everything else stays 0xFFFF (remote).
        """
        for raw in args["locations"]:
            item = NetworkItem(*raw) if not isinstance(raw, NetworkItem) else raw
            # Drain outstanding scout IDs regardless of whether the item is a reward,
            # since LocationScouts requested every location we own.
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
            logger.info("Location data built from scout results.")

    async def _update_traplink_tags(self, enabled: bool) -> None:
        old = self.tags.copy()
        if enabled:
            self.tags.add("TrapLink")
        else:
            self.tags.discard("TrapLink")
        if old != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    def on_deathlink(self, data: dict[str, Any]) -> None:
        super().on_deathlink(data)
        if "DeathLink" in self.tags and self.ap_data_base is not None:
            self.dolphin.write_u32(self._addr(MemoryAddress.DEATHLINK_RECEIVE), 1)

    def _addr(self, offset: int) -> int:
        """Compute an absolute Dolphin address from an APData struct offset."""
        assert self.ap_data_base is not None
        return self.ap_data_base + offset

    async def run_dolphin_sync(self) -> None:
        logger.info("Starting Dolphin connector. Use /dolphin for status information.")
        while not self.exit_event.is_set():
            # Poll game memory at a fixed 0.1s cadence. Game-initiated events (checks, energy sends,
            # deathlink/traplink, goal) are found only by polling - nothing server-side wakes the loop -
            # so the poll interval is their latency floor. watcher_event still early-wakes when items
            # arrive from the server, so delivery isn't gated on the 0.1s tick.
            try:
                try:
                    async with asyncio.timeout(0.1):
                        await self.watcher_event.wait()
                except TimeoutError:
                    pass
                finally:
                    self.watcher_event.clear()

                try:
                    if self.dolphin.is_hooked() and self.dolphin.check_game_running():
                        await self._dolphin_tick()
                    else:
                        await self._try_connect_dolphin()
                except Exception as e:
                    logger.error(f"Dolphin sync error: {e}")
                    if self.dolphin.is_hooked():
                        self.dolphin.unhook()
                    self._reset_dolphin_state()

                now_connected = self.dolphin.is_hooked() and self.dolphin.check_game_running()
                if now_connected and not self._dolphin_was_connected:
                    logger.info("Dolphin connected.")
                    self.last_attach_detail = None
                    self._logged_attach_detail = None
                elif not now_connected and self._dolphin_was_connected:
                    # The specific reason is logged by _note_attach_failure on the
                    # next connect attempt; this is just the state marker.
                    logger.info("Lost connection to Dolphin.")
                self._dolphin_was_connected = now_connected
            except Exception as e:
                # Last-resort guard. This task has no supervisor, so an unhandled exception escaping
                # the loop body would silently kill the connector until a full restart. Log and
                # continue instead. CancelledError is a BaseException, so shutdown still propagates.
                logger.error(f"Unexpected error in Dolphin sync loop: {e}")

    async def _try_connect_dolphin(self) -> None:
        if self.dolphin.is_hooked():
            self.dolphin.unhook()
        self._reset_dolphin_state()

        self.dolphin.hook()
        if self.dolphin.is_hooked() and self.dolphin.check_game_running():
            return  # Fully attached; the main loop ticks on the next iteration.

        # Not fully connected. Record an accurate reason *before* dropping any hook, so /dolphin and
        # the log reflect the real state instead of the bare "not hooked yet" that unhooking leaves.
        if self.dolphin.is_hooked():
            # DME attached and found a MEM1-sized region, but GKYE01 wasn't at MEM1_START. The bytes
            # there say why: all 0x00 -> no game booted yet (menu); another valid id like 'GKYP01'/
            # 'GKYJ01' -> wrong-region disc (mod is NTSC-U only); arbitrary bytes -> DME attached to
            # the wrong memory region (it picks a MEM1-sized mapping without checking contents).
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
                # unHooked here means hook() raised; DolphinInterface.hook() already
                # logged the underlying exception.
                self._note_attach_failure(f"hook attempt failed (status: {status})")

        await asyncio.sleep(5)

    def _note_attach_failure(self, detail: str) -> None:
        """Record why the latest connect attempt didn't fully connect, and log it
        only when it changes. last_attach_detail feeds /dolphin; the dedup means an
        unchanging failure is logged once rather than on every 5s retry."""
        self.last_attach_detail = detail
        if detail != self._logged_attach_detail:
            self._logged_attach_detail = detail
            logger.info(f"Dolphin not fully connected: {detail}")

    async def _dolphin_tick(self) -> None:
        # Resolve / verify APData pointer
        ptr = self.dolphin.resolve_ap_data()
        if ptr is None:
            if self.ap_data_base is not None:
                logger.info("APData pointer lost. Game may have restarted.")
                self._reset_dolphin_state()
            return
        if ptr != self.ap_data_base:
            if self.ap_data_base is not None:
                logger.info("APData pointer changed. Re-handshaking.")
                self._reset_dolphin_state()
            self.ap_data_base = ptr
            logger.info(f"Found APData at {ptr:#010x}")

        # Wait for game_ready, and detect restarts. The mod sets game_ready once in OnBoot and never
        # clears it during play, so reading 0 after we've seen 1 means the game rebooted (APData
        # re-zeroed). Re-run the handshake to re-seed and re-write options/locations.
        game_ready_mem = self.dolphin.read_u32(self._addr(MemoryAddress.GAME_READY))
        if not self.game_ready:
            if game_ready_mem != 1:
                return
            self.game_ready = True
            logger.info("Game initialized and save loaded.")
        elif game_ready_mem != 1:
            logger.info("game_ready cleared - game restarted. Re-handshaking.")
            self._reset_dolphin_state()
            return

        # Write slot options (requires AP server connection)
        if not self.options_written:
            if not self.slot_options:
                return  # Waiting for AP server Connected packet.
            self._write_options()
            self.options_written = True
            self.item_send_index = self.dolphin.read_u32(self._addr(MemoryAddress.ITEM_RECEIVED_INDEX))
            logger.info(f"Options written. Game has received {self.item_send_index} items.")

        # Write location data (requires scout results)
        if not self.locations_written:
            if not self.location_arrays_ready:
                return  # Waiting for LocationInfo scout response.
            self._write_location_data()
            self.locations_written = True
            logger.info("Location data written. Client fully operational.")

            # Re-arm backfill on every completed handshake, not just on an AP "Connected" packet. When
            # the mod restarts with a fresh save while the AP session stays alive (Dolphin reboot, no
            # new Connected), the server may know checks the fresh save lacks. Backfill then diffs
            # checked_locations against the game's sent_checks and writes the missing bits. Without
            # this, only re-delivered reward items mark their cells; non-reward locations stay lost.
            self.backfill_pending = True

        # Normal operation
        await self._poll_game()

    def _write_options(self) -> None:
        """Write all APSlotOptions fields to game memory and signal options_valid."""
        sd = self.slot_options
        d = self.dolphin
        a = self._addr

        d.write_u32(a(MemoryAddress.OPTION_DEATH_LINK_ENABLED), int(bool(sd.get("death_link", 0))))
        d.write_u32(a(MemoryAddress.OPTION_ENERGY_LINK_ENABLED), int(bool(sd.get("energy_link", 0))))
        d.write_u32(a(MemoryAddress.OPTION_TRAP_LINK_ENABLED), int(bool(sd.get("trap_link", 0))))
        d.write_u32(a(MemoryAddress.OPTION_REVEAL_CHECKLISTS), int(bool(sd.get("reveal_checklists", 0))))

        # Goals per mode: option values map directly to the GoalKind enum.
        d.write_u32(a(MemoryAddress.OPTION_GOAL_AIRRIDE), int(sd.get("air_ride_goal", 4)))
        d.write_u32(a(MemoryAddress.OPTION_GOAL_TOPRIDE), int(sd.get("top_ride_goal", 4)))
        d.write_u32(a(MemoryAddress.OPTION_GOAL_CITYTRIAL), int(sd.get("city_trial_goal", 0)))
        d.write_u32(a(MemoryAddress.OPTION_GOAL_ARCHIPELAGO), int(sd.get("archipelago_goal", 4)))

        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_AIRRIDE), int(sd.get("air_ride_checklist_amount", 60)))
        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_TOPRIDE), int(sd.get("top_ride_checklist_amount", 60)))
        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_CITYTRIAL), int(sd.get("city_trial_checklist_amount", 60)))
        d.write_u32(a(MemoryAddress.OPTION_CHECKLIST_AMOUNT_ARCHIPELAGO), int(sd.get("archipelago_checklist_amount", 60)))

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
        d.write_u32(
            a(MemoryAddress.OPTION_CHECKLIST_REWARDS_GATING_ENABLED),
            int(bool(sd.get("checklist_rewards_gated", 1))),
        )

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
        self._check_goal()
        await self._poll_menu_toggles()
        await self._handle_deathlink()
        await self._handle_traplink()
        await self._handle_energylink()
        self._handle_backfill()

    def _deliver_items(self) -> None:
        """Deliver pending items to the game one at a time via the incoming_item_id mailbox."""
        while self.item_send_index < len(self.items_received):
            if self.dolphin.read_u32(self._addr(MemoryAddress.INCOMING_ITEM_ID)) != 0:
                return  # Game hasn't consumed the previous item yet.
            item = self.items_received[self.item_send_index]
            self.dolphin.write_u32(self._addr(MemoryAddress.INCOMING_ITEM_ID), item.item)
            logger.debug(f"Delivered item #{self.item_send_index}: {self.item_names.lookup_in_game(item.item)}")
            self.item_send_index += 1

    async def _check_locations(self) -> None:
        """Read the sent_checks bitmask and send any newly-set bits to the AP server."""
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
                            ck = word_idx * 64 + bit
                            new_checks.add(mode_clear_to_location_code(mode, ck))

        if new_checks:
            sent = await self.check_locations(new_checks)
            if sent:
                names = [self.location_names.lookup_in_game(loc) for loc in sent]
                logger.info(f"New checks sent: {names}")

    def _check_goal(self) -> None:
        """Forward the game's goal_complete flag to the AP server as a victory."""
        if self.finished_game:
            return
        if self.dolphin.read_u8(self._addr(MemoryAddress.GOAL_COMPLETE)) == 1:
            self.finished_game = True
            logger.info("Goal complete! Sending victory.")
            Utils.async_start(self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]))

    async def _poll_menu_toggles(self) -> None:
        """Read the mod's live in-game menu toggle mirrors and update AP server state if changed.

        The OPTION_*_ENABLED fields only set initial values on first connect and are not
        updated when the player toggles in-game. The *_MENU_ENABLED mirrors are
        the authoritative live state, written by the mod on every menu change.
        """
        dl_enabled = self.dolphin.read_u32(self._addr(MemoryAddress.DEATHLINK_MENU_ENABLED)) != 0
        dl_currently_on = "DeathLink" in self.tags
        if dl_enabled != dl_currently_on:
            logger.info(f"DeathLink toggled {'on' if dl_enabled else 'off'} from in-game menu.")
            await self.update_death_link(dl_enabled)

        tl_enabled = self.dolphin.read_u32(self._addr(MemoryAddress.TRAPLINK_MENU_ENABLED)) != 0
        tl_currently_on = "TrapLink" in self.tags
        if tl_enabled != tl_currently_on:
            logger.info(f"TrapLink toggled {'on' if tl_enabled else 'off'} from in-game menu.")
            await self._update_traplink_tags(tl_enabled)

        el_enabled = self.dolphin.read_u32(self._addr(MemoryAddress.ENERGYLINK_MENU_ENABLED)) != 0
        if el_enabled != self.energy_link_enabled:
            logger.info(f"EnergyLink toggled {'on' if el_enabled else 'off'} from in-game menu.")
            self.energy_link_enabled = el_enabled
            if el_enabled:
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

        # forward trap to AP server. The mod writes a TrapLinkKind enum (>0) into TRAPLINK_SEND; we map
        # it to a name for the Bounce so other worlds can translate. Bursts collapse mod-side: rapid
        # triggers overwrite the same u32, and the ≥0.1s poll reads one final value per burst.
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
        if self.pending_trap_receives > 0:
            if self.dolphin.read_u32(self._addr(MemoryAddress.TRAPLINK_RECEIVE)) == 0:
                self.pending_trap_receives -= 1
                self.dolphin.write_u32(self._addr(MemoryAddress.TRAPLINK_RECEIVE), 1)

    async def _handle_energylink(self) -> None:
        if not self.energy_link_enabled:
            return

        # Process energy sends FIRST, then write the balance LAST. Order matters: the balance write
        # seeds from current_energy_link_value (the last server-pushed pool), so running it before the
        # diff would bounce the mod's local decrement back up to the stale pool, letting the
        # affordability gate briefly overdraw across the server round-trip. Fold our delta in first.
        #
        # energy_sent_total is a game-owned CUMULATIVE counter (s64 signed raw MJ): the game only adds
        # (deposits) / subtracts (withdrawals); we only read-and-diff, never write. Any number of
        # game-side writes between polls collapse into one net delta.
        raw = self.dolphin.read_u64(self._addr(MemoryAddress.ENERGY_SENT_TOTAL))
        cur = raw - (1 << 64) if raw >= (1 << 63) else raw

        if self.energy_last_seen is None:
            # Seed on connect / after a game restart: record the current total without applying it, so
            # we diff forward from here rather than replaying the session. Falls through to refresh the
            # balance.
            self.energy_last_seen = cur
        else:
            delta_mj = cur - self.energy_last_seen
            if delta_mj != 0:
                # Advance the watermark now. A dropped send self-heals on the next diff (the counter is
                # the source of truth), so we never replay this delta. Restarts are caught upstream by
                # the game_ready 1->0 re-check, so we don't second-guess a backward delta with a
                # magnitude heuristic here.
                self.energy_last_seen = cur

                joules = delta_mj * ENERGY_LINK_EXCHANGE_RATE
                ops: list[dict[str, Any]] = [{"operation": "add", "value": joules}]
                if joules < 0:
                    # Withdraw: tag + want_reply so we can match the SetReply and detect server-side
                    # clamping at 0 (pool was emptier than the mod thought).
                    ops.append({"operation": "max", "value": 0})
                    tag = uuid.uuid4().hex
                    # Record the pending tag only after the send is dispatched: send_msgs silently
                    # no-ops on a closed socket, so a pre-send insert would leak the entry on a drop.
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
                else:
                    # Deposit: no tag needed, the set_notify subscription delivers
                    # the updated balance to all clients.
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

                # Optimistically fold our delta into the cached pool value so the balance written below
                # reflects this spend/deposit now, before the server's SetReply round-trips. This closes
                # the self-induced overdraw window. The set_notify subscription later overwrites
                # current_energy_link_value with the server's ABSOLUTE pool on every SetReply, so a
                # concurrent change from another player self-corrects within one poll and we never
                # double-count. max(0, ...) mirrors the server's max:0 withdrawal clamp.
                if self.current_energy_link_value is not None:
                    self.current_energy_link_value = max(0, self.current_energy_link_value + joules)

        # Write the (possibly optimistically-updated) pool balance to the game LAST, unconditionally
        # each poll, so seed polls, no-delta polls, and other players' deposits all keep the mod's view
        # fresh. Server stores Joules; the mod expects raw MJ. Floor division - sub-MJ isn't
        # representable mod-side.
        if self.current_energy_link_value is not None:
            raw_mj = self.current_energy_link_value // ENERGY_LINK_EXCHANGE_RATE
            # The mod's field is s64; raw_mj is always non-negative (pool clamped at 0). write_u64 is
            # fine: DME has no signed variant and the bytes are identical for non-negative values.
            self.dolphin.write_u64(self._addr(MemoryAddress.ENERGY_BALANCE), raw_mj)

    def _handle_backfill(self) -> None:
        """Write bits to client_backfill for checks the AP server knows about but the game doesn't.

        This handles fresh saves, slot takeovers, and !collect from other players.
        """
        if not self.backfill_pending:
            return

        # Wait for the game to finish processing previous backfill.
        for off in CLIENT_BACKFILL_PER_MODE.values():
            if self.dolphin.read_u64(self._addr(off)) != 0 or self.dolphin.read_u64(self._addr(off) + 8) != 0:
                return

        # Build bitmask of all server-known checks.
        server_bits: dict[GameMode, list[int]] = {m: [0, 0] for m in GameMode}
        for loc_code in self.checked_locations:
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

        if wrote_any:
            logger.info("Backfilled server-known checks to game.")
        self.backfill_pending = False

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago Kirby Air Ride Client"
        return ui

    async def shutdown(self) -> None:
        if self.dolphin.is_hooked():
            self.dolphin.unhook()
        await super().shutdown()


async def async_main(connect: str | None, password: str | None) -> None:
    ctx = KARContext(connect, password)
    if Utils.gui_enabled:
        ctx.run_gui()
    ctx.run_cli()
    await asyncio.sleep(1)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    ctx.dolphin_sync_task = asyncio.create_task(ctx.run_dolphin_sync(), name="dolphin sync")
    try:
        await ctx.exit_event.wait()
    finally:
        ctx.watcher_event.set()
        await ctx.shutdown()
        if ctx.dolphin_sync_task:
            await ctx.dolphin_sync_task


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
