"""
Slot data contract tests.

KARWorld.fill_slot_data() returns the dict that the client (KARClient.py) consumes on
connect. These tests pin the contract: required keys present, types correct, and
the spawn_rate_min override applied when progressive spawn rate is off.

Update the EXPECTED_KEYS set when intentionally adding or removing a slot_data field —
the client must be updated in lockstep.
"""

import json

from Options import Toggle

from ..KAROptions import CityTrialGoal
from . import ALL_MODES, CT_ONLY, KARTestBase

EXPECTED_KEYS: frozenset[str] = frozenset(
    {
        # General
        "death_link",
        "energy_link",
        "trap_link",
        "reveal_checklists",
        "trap_chance",
        "effect_items_enabled",
        # Goals
        "city_trial_goal",
        "city_trial_checklist_amount",
        "city_trial_goal_locations",
        "air_ride_goal",
        "air_ride_checklist_amount",
        "air_ride_goal_locations",
        "top_ride_goal",
        "top_ride_checklist_amount",
        "top_ride_goal_locations",
        # City Trial specifics
        "city_trial_progressive_patch_caps",
        "city_trial_patch_cap_amount",
        "city_trial_progressive_stadiums",
        # Item generation
        "spawn_rate_progressive",
        "spawn_rate_min",
        "spawn_rate_max",
        # Gating
        "events_gated",
        "abilities_gated",
        "patches_gated",
        "city_trial_items_gated",
        "machines_gated",
        "boxes_gated",
        "air_ride_courses_gated",
        "colors_gated",
        "top_ride_courses_gated",
        "top_ride_items_gated",
    }
)


class TestSlotDataDefaults(KARTestBase):
    """Default CT options produce a slot_data with the expected key set and types."""

    options = CT_ONLY

    def test_exact_key_set(self):
        data = self.world.fill_slot_data()
        actual = set(data.keys())
        missing = EXPECTED_KEYS - actual
        extra = actual - EXPECTED_KEYS
        self.assertFalse(missing, f"slot_data missing expected keys: {sorted(missing)}")
        self.assertFalse(extra, f"slot_data has unexpected keys: {sorted(extra)}")

    def test_serializes_as_json(self):
        # The network layer round-trips slot_data as JSON; non-JSON-serializable values
        # would fail at connect time.
        data = self.world.fill_slot_data()
        try:
            json.dumps(dict(data))
        except (TypeError, ValueError) as exc:
            self.fail(f"slot_data is not JSON-serializable: {exc}")

    def test_value_types(self):
        data = self.world.fill_slot_data()
        # Numeric fields the client treats as ints/bools.
        for int_key in (
            "trap_chance",
            "city_trial_checklist_amount",
            "air_ride_checklist_amount",
            "top_ride_checklist_amount",
            "city_trial_patch_cap_amount",
            "spawn_rate_min",
            "spawn_rate_max",
            "city_trial_goal",
            "air_ride_goal",
            "top_ride_goal",
        ):
            with self.subTest(key=int_key):
                self.assertIsInstance(data[int_key], int, f"{int_key} should be int-like")
        # LocationSet fields serialize as iterable of strings.
        for locset_key in ("city_trial_goal_locations", "air_ride_goal_locations", "top_ride_goal_locations"):
            with self.subTest(key=locset_key):
                # LocationSet's serialized form is iterable; coerce to list and check.
                self.assertIsInstance(list(data[locset_key]), list)


class TestSlotDataSpawnRateProgressiveOff(KARTestBase):
    """spawn_rate_min must be pinned to 100 when spawn_rate_progressive is off,
    regardless of the player's spawn_rate_min option value. The mod consumes a
    single floor; shipping the player-provided value when progressive is off would
    inappropriately elevate the static rate."""

    options = {**CT_ONLY, "spawn_rate_progressive": Toggle.option_false, "spawn_rate_min": 250}

    def test_min_pinned_to_100(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["spawn_rate_min"], 100, "spawn_rate_min should be 100 when spawn_rate_progressive is off")


class TestSlotDataSpawnRateProgressiveOn(KARTestBase):
    """When progressive is on, the player's spawn_rate_min flows through unchanged.
    Uses ALL_MODES so the 30 Spawn Rate Up items the range (200-500) generates fit
    in the available default locations."""

    options = {
        **ALL_MODES,
        "spawn_rate_progressive": Toggle.option_true,
        "spawn_rate_min": 200,
        "spawn_rate_max": 500,
    }

    def test_min_passes_through(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["spawn_rate_min"], 200)
        self.assertEqual(data["spawn_rate_max"], 500)


class TestSlotDataAllModes(KARTestBase):
    """The same key set is produced for any enabled-modes combination."""

    options = ALL_MODES

    def test_all_modes_keys_match_default(self):
        data = self.world.fill_slot_data()
        self.assertEqual(set(data.keys()), EXPECTED_KEYS)


class TestSlotDataGoalValueReflectsOption(KARTestBase):
    """Goal field carries the player's selected goal value."""

    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_beat_king_dedede}

    def test_ct_goal_value(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["city_trial_goal"], CityTrialGoal.option_beat_king_dedede)
