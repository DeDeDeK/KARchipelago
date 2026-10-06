"""Launching the client: the launcher forwards its arguments to it, and a slot link on a WebHost room page
(archipelago://slot:password@host:port?game=...) offers it in the launcher's client picker and connects it."""

import contextlib
import io
import sys
import unittest
from unittest import mock

import Launcher

from worlds.LauncherComponents import Component, components

from .. import KARWorld
from ..KARClient import main, parse_args

# As a room page links a slot. WebHost always writes a literal "None" password; the client's server_auth
# prompts for the real one if the room turns out to need it.
_ROOM_LINK = "archipelago://Kirby%20Fan:None@archipelago.gg:38281?game=Kirby%20Air%20Ride&room=abc123"


def _client_component() -> Component:
    return next(component for component in components if component.display_name == "Kirby Air Ride Client")


class TestRoomLink(unittest.TestCase):
    def test_launcher_offers_this_client_for_the_games_links(self):
        offered, _text_client = Launcher.handle_uri(_ROOM_LINK)
        self.assertIn(_client_component(), offered)

    def test_game_name_matches_the_world(self):
        # The launcher matches the link's game query against this exactly
        self.assertEqual(_client_component().game_name, KARWorld.game)

    def test_link_parses_into_address_and_slot(self):
        parsed = parse_args(_ROOM_LINK)
        self.assertEqual(parsed.connect, "Kirby%20Fan:None@archipelago.gg:38281")
        self.assertEqual(parsed.name, "Kirby Fan")

    def test_link_carries_a_real_password(self):
        parsed = parse_args("archipelago://Kirby:hunter2@localhost:38281")
        self.assertEqual(parsed.password, "hunter2")

    def test_non_archipelago_link_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args("http://archipelago.gg:38281")


class TestLaunchArguments(unittest.TestCase):
    def test_component_forwards_its_arguments_to_the_client(self):
        # The launcher's client picker runs the component with the link as its only argument
        with mock.patch(f"{KARWorld.__module__}.launch") as launch:
            _client_component().run(_ROOM_LINK)
        launch.assert_called_once_with(main, name="KirbyAirRideClient", args=(_ROOM_LINK,))

    def test_flags(self):
        parsed = parse_args("--connect", "localhost:38281", "--name", "Kirby", "--password", "pw")
        self.assertEqual((parsed.connect, parsed.name, parsed.password), ("localhost:38281", "Kirby", "pw"))

    def test_no_arguments_ignores_the_launchers_own_argv(self):
        # A plain launcher button press passes nothing; the launcher's argv must not leak into the client.
        with mock.patch.object(sys, "argv", ["Launcher.py", "--not-a-client-flag"]):
            parsed = parse_args()
        self.assertEqual((parsed.connect, parsed.name, parsed.password, parsed.url), (None, None, None, None))
