"""Attaching to Dolphin: the client tells apart a different game, a still-booting game, and Kirby Air Ride
running without the mod, which shares the modded game's id. /dolphin words each state like the line the client
printed on entering it."""

import unittest
from unittest import mock

from .. import KARClient
from ..KARClient import KARCommandProcessor, KARContext


class _FakeDolphin:
    """A hooked Dolphin whose disc header reads `header`, running a game the mod never loaded into."""

    kar_game_id = b"GKYE01"

    def __init__(self, header: bytes) -> None:
        self.header = header
        self.hooked = False

    def hook(self) -> bool:
        self.hooked = True
        return True

    def unhook(self) -> None:
        self.hooked = False

    def is_hooked(self) -> bool:
        return self.hooked

    def status_name(self) -> str:
        return "hooked" if self.hooked else "unHooked"

    def read_bytes(self, address: int, length: int) -> bytes:
        return self.header[:length]

    def check_game_running(self) -> bool:
        return self.hooked and self.header == self.kar_game_id

    def resolve_ap_data(self) -> int | None:
        return None


def _context(header: bytes) -> KARContext:
    ctx = KARContext(None, None)
    ctx.dolphin = _FakeDolphin(header)
    return ctx


class TestWrongGame(unittest.IsolatedAsyncioTestCase):
    # KARContext starts tasks, so it needs a running loop
    def _attach(self, header: bytes) -> str:
        """The line printed for a failed attach, after checking /dolphin repeats it."""
        ctx = _context(header)
        with mock.patch.object(KARClient, "log_detailed") as log:
            self.assertFalse(ctx._try_connect_dolphin())
        summary, color = log.call_args.args[2], log.call_args.args[4]
        self.assertEqual(KARCommandProcessor._status(ctx), (summary, color))
        return summary

    async def test_other_game(self):
        self.assertIn("different game (GALE01)", self._attach(b"GALE01"))

    async def test_other_region(self):
        self.assertIn("the PAL version of Kirby Air Ride (GKYP01), not NTSC-U", self._attach(b"GKYP01"))

    async def test_unknown_region_shows_the_id(self):
        self.assertIn("Kirby Air Ride GKYX01, not NTSC-U", self._attach(b"GKYX01"))

    async def test_empty_header_is_still_booting(self):
        self.assertIn("Waiting for Kirby Air Ride to start", self._attach(b"\0" * 6))


class TestHandshakeStatus(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.ctx = _context(b"GKYE01")
        self.assertTrue(self.ctx._try_connect_dolphin())

    def _status(self) -> str:
        return KARCommandProcessor._status(self.ctx)[0]

    def _finish_handshake(self) -> None:
        self.ctx.ap_data_base = 0x80001000
        self.ctx.game_ready = True
        self.ctx.slot_options = {"death_link": 0}
        self.ctx.options_written = self.ctx.options_acked = self.ctx.locations_written = True

    async def test_reports_waiting_for_the_mod_once(self):
        with mock.patch.object(KARClient, "log_detailed") as log:
            await self.ctx._dolphin_tick()
            await self.ctx._dolphin_tick()
        log.assert_called_once()
        self.assertIn("Kirby Air Ride is running. Waiting for the KARchipelago mod", log.call_args.args[2])
        self.assertEqual(self._status(), log.call_args.args[2])

    async def test_each_step(self):
        self.ctx.ap_data_base = 0x80001000
        self.assertIn("Waiting for the game to load its save", self._status())
        self.ctx.game_ready = True
        self.assertIn("Waiting for connection to the Archipelago server", self._status())
        self.ctx.slot_options = {"death_link": 0}
        self.assertIn("Finishing the handshake", self._status())
        self._finish_handshake()
        self.assertEqual(KARCommandProcessor._status(self.ctx), (KARClient._READY_TO_PLAY, "green"))

    async def test_leaving_the_room_after_the_handshake(self):
        self._finish_handshake()
        self.ctx.reset_server_state()
        self.assertIn("Waiting for connection to the Archipelago server", self._status())
