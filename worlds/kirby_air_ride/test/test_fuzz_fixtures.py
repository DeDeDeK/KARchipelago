"""Guards for the dev-only fuzz fixtures in ``fuzz/``. Archipelago only logs a warning for an unknown
option key, so a fixture that keeps writing one after a rename silently exercises that option's default
- three once claimed to stress the patch-cap stack while minting zero Patch Cap Increase items."""

import unittest
from pathlib import Path
from typing import Any

import yaml
from BaseClasses import PlandoOptions

from .. import KARWorld
from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
)
from ..KAROptions import KAROptions

_FUZZ_DIR = Path(__file__).resolve().parent.parent / "fuzz"
_STATIC_DIR = _FUZZ_DIR / "static"
_META_PATH = _FUZZ_DIR / "fuzz_meta.yaml"

_GAME = "Kirby Air Ride"

# Keys the fuzzer's meta format adds on top of the option surface; only legal in the meta file.
_META_ONLY_KEYS = frozenset({"fuzz_constraints"})

# Keys Archipelago understands inside a game section but that are not options.
_NON_OPTION_GAME_KEYS = frozenset({"triggers"})

# Every plando module enabled, so a fixture's plando_items block is verified rather than skipped.
_ALL_PLANDO = PlandoOptions.items | PlandoOptions.connections | PlandoOptions.texts | PlandoOptions.bosses

# The per-mode goal-location option paired with the table its names must come from.
_GOAL_LOCATION_OPTIONS: dict[str, dict[str, Any]] = {
    "city_trial_goal_locations": CITY_TRIAL_LOCATION_TABLE,
    "air_ride_goal_locations": AIR_RIDE_LOCATION_TABLE,
    "top_ride_goal_locations": TOP_RIDE_LOCATION_TABLE,
    "archipelago_goal_locations": AP_CHECKLIST_LOCATION_TABLE,
}


def _static_fixtures() -> list[tuple[str, dict]]:
    return [(path.name, yaml.safe_load(path.read_text())) for path in sorted(_STATIC_DIR.glob("*.yaml"))]


class TestStaticFixturesAreWellFormed(unittest.TestCase):
    """Every fixture is a valid single-slot Kirby Air Ride YAML."""

    def test_at_least_one_fixture_exists(self):
        # Non-vacuity guard: an empty or moved directory would make every loop below pass.
        self.assertTrue(_STATIC_DIR.is_dir(), f"{_STATIC_DIR} is missing")
        self.assertGreaterEqual(len(_static_fixtures()), 5)

    def test_headers_present_and_unique(self):
        names: dict[str, str] = {}
        for filename, doc in _static_fixtures():
            with self.subTest(fixture=filename):
                self.assertEqual(doc.get("game"), _GAME, "fixture must target Kirby Air Ride")
                for key in ("name", "description"):
                    self.assertTrue(str(doc.get(key, "")).strip(), f"fixture needs a non-empty {key}")
                self.assertIn(_GAME, doc, "fixture needs a 'Kirby Air Ride:' options section")
                # Generation puts every fixture in one multiworld, so duplicate slot names would collide.
                name = doc["name"]
                self.assertNotIn(name, names, f"slot name {name!r} is already used by {names.get(name)}")
                names[name] = filename

    def test_every_option_key_is_real(self):
        valid = set(KAROptions.type_hints) | _NON_OPTION_GAME_KEYS
        for filename, doc in _static_fixtures():
            for key in doc[_GAME]:
                with self.subTest(fixture=filename, option=key):
                    self.assertIn(key, valid, f"{key!r} is not a Kirby Air Ride option, so it would be ignored")

    def test_every_option_value_parses_and_verifies(self):
        # `from_any` catches bad Choice spellings, out-of-range numbers and unknown OptionSet keys;
        # `verify` additionally checks location and item names, including inside `plando_items`.
        for filename, doc in _static_fixtures():
            slot_name = doc.get("name", filename)
            for key, value in doc[_GAME].items():
                if key not in KAROptions.type_hints:
                    continue  # reported by test_every_option_key_is_real
                with self.subTest(fixture=filename, option=key):
                    KAROptions.type_hints[key].from_any(value).verify(KARWorld, slot_name, _ALL_PLANDO)

    def test_goal_locations_belong_to_their_mode(self):
        # The world rejects a cross-mode goal location at generation; catching it here names the fixture
        # instead of surfacing as an OptionError mid-campaign.
        for filename, doc in _static_fixtures():
            for key, table in _GOAL_LOCATION_OPTIONS.items():
                for name in doc[_GAME].get(key) or []:
                    with self.subTest(fixture=filename, option=key, location=name):
                        self.assertIn(name, table, f"{name!r} is not a {key.rsplit('_goal', 1)[0]} location")


class TestFuzzMetaIsCurrent(unittest.TestCase):
    """The meta prunes YAMLs the world would reject by design. A constraint naming an option or a
    location that no longer exists prunes nothing, and the only symptom is a quietly higher `ignored`
    count in the fuzz report."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.meta = yaml.safe_load(_META_PATH.read_text())
        cls.constraints = cls.meta[_GAME]["fuzz_constraints"]

    def test_meta_targets_this_game(self):
        self.assertIn(_GAME, self.meta)
        self.assertTrue(self.constraints, "meta has no constraints, so it prunes nothing")

    def test_meta_keys_are_options_or_meta_directives(self):
        valid = set(KAROptions.type_hints) | _META_ONLY_KEYS | _NON_OPTION_GAME_KEYS
        for key in self.meta[_GAME]:
            with self.subTest(key=key):
                self.assertIn(key, valid)

    def test_constraints_name_real_options(self):
        for index, constraint in enumerate(self.constraints):
            with self.subTest(constraint=index):
                self.assertIn(constraint["option"], KAROptions.type_hints)
                for clause in ("then", "then_include", "then_exclude"):
                    for target in constraint.get(clause, {}):
                        self.assertIn(target, KAROptions.type_hints, f"{clause} target {target!r}")

    def test_if_value_matches_a_real_choice(self):
        for index, constraint in enumerate(self.constraints):
            if "if_value" not in constraint:
                continue
            option = KAROptions.type_hints[constraint["option"]]
            with self.subTest(constraint=index, option=constraint["option"]):
                self.assertIn(
                    constraint["if_value"],
                    getattr(option, "options", {}),
                    "if_value must name a choice the option still offers, or the constraint never fires",
                )

    def test_seeded_goal_locations_are_valid_for_their_mode(self):
        # `checklist_list` always OptionErrors on an empty list, so the meta seeds one location per mode.
        seeded = 0
        for index, constraint in enumerate(self.constraints):
            for target, names in constraint.get("then_include", {}).items():
                table = _GOAL_LOCATION_OPTIONS.get(target)
                if table is None:
                    continue
                for name in names:
                    seeded += 1
                    with self.subTest(constraint=index, option=target, location=name):
                        self.assertIn(name, table)
        self.assertEqual(seeded, len(_GOAL_LOCATION_OPTIONS), "every mode's checklist_list goal needs a seed")
