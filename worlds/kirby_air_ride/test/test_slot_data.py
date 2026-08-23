"""
Slot data contract tests.

fill_slot_data() returns the dict the client consumes on connect. These pin the contract: required keys
present, types correct, and the spawn-rate min shipped to the mod verbatim. Only options the client or
mod consume are shipped - generation-only ones (trap_chance, spawn_rate_max) are deliberately omitted.

Update EXPECTED_KEYS when intentionally adding or removing a field; the client moves in lockstep.
"""

import json

from Options import Toggle

from .. import UT_OPTIONS_KEY
from ..KARLocations import CTLocation
from ..KAROptions import CityTrialGoal
from . import ALL_MODES, CT_ONLY, KARTestBase

EXPECTED_KEYS: frozenset[str] = frozenset(
    {
        # General
        "death_link",
        "energy_link",
        "trap_link",
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
        "archipelago_goal",
        "archipelago_checklist_amount",
        "archipelago_goal_locations",
        # Per-checklist start-revealed toggles
        "city_trial_reveal_checklist",
        "air_ride_reveal_checklist",
        "top_ride_reveal_checklist",
        "archipelago_reveal_checklist",
        # City Trial specifics
        "city_trial_patch_cap_min",
        "city_trial_patch_cap_max",
        "city_trial_stadiums_gated",
        # Item generation (runtime spawn-rate min; max is generation-only)
        "spawn_rate_min",
        # Gating
        "city_trial_events_gated",
        "abilities_gated",
        "base_abilities_gated",
        "city_trial_patches_gated",
        "city_trial_items_gated",
        "machines_gated",
        "city_trial_boxes_gated",
        "air_ride_courses_gated",
        "colors_gated",
        "top_ride_courses_gated",
        "top_ride_items_gated",
        "checklist_rewards",
        # Goal keys held back from an ungated category's pre-fill
        "legendary_pieces_goal_gated",
        "vs_king_dedede_goal_gated",
        "ap_star_pieces_goal_gated",
        # Universal Tracker's raw-option record; not consumed by the client or the mod.
        UT_OPTIONS_KEY,
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
            "city_trial_checklist_amount",
            "air_ride_checklist_amount",
            "top_ride_checklist_amount",
            "city_trial_patch_cap_min",
            "city_trial_patch_cap_max",
            "spawn_rate_min",
            "city_trial_goal",
            "air_ride_goal",
            "top_ride_goal",
            "archipelago_goal",
            "archipelago_checklist_amount",
        ):
            with self.subTest(key=int_key):
                self.assertIsInstance(data[int_key], int, f"{int_key} should be int-like")
        # LocationSet fields serialize as iterable of strings.
        for locset_key in (
            "city_trial_goal_locations",
            "air_ride_goal_locations",
            "top_ride_goal_locations",
            "archipelago_goal_locations",
        ):
            with self.subTest(key=locset_key):
                self.assertIsInstance(list(data[locset_key]), list)


class TestSlotDataSpawnRateMinShips(KARTestBase):
    """The player's spawn_rate_min flows through to the mod verbatim. An on-grid sub-vanilla
    min (80) ships unchanged. Uses ALL_MODES so the Spawn Rate Up items the range generates
    fit in the available default locations."""

    options = {**ALL_MODES, "spawn_rate_min": 80, "spawn_rate_max": 200}

    def test_min_passes_through(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["spawn_rate_min"], 80)


class TestSlotDataSpawnRateSnapped(KARTestBase):
    """Spawn rate moves in 10% steps, so the min is snapped to the nearest multiple of 10 at generation
    and the snapped value is what ships. spawn_rate_max is snapped too but isn't shipped: it only sizes
    the Spawn Rate Up pool."""

    options = {
        **ALL_MODES,
        "spawn_rate_min": 64,
        "spawn_rate_max": 227,
    }

    def test_min_snapped_to_nearest_ten(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["spawn_rate_min"], 60)


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


class TestSlotDataChecklistListShipsItsLocations(KARTestBase):
    """The checklist_list goal is the one goal the mod cannot evaluate from a count: it has to be told
    which boxes to watch, so the LocationSet ships by name. An empty or reordered set would leave the
    mod watching nothing."""

    _GOAL_LOCS = [CTLocation.DESTROY_ALL_HOUSES, CTLocation.BUST_STAR_POLE]
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_checklist_list,
        "city_trial_goal_locations": _GOAL_LOCS,
    }

    def test_goal_locations_ship_by_name(self):
        data = self.world.fill_slot_data()
        self.assertEqual(set(data["city_trial_goal_locations"]), {str(loc) for loc in self._GOAL_LOCS})

    def test_other_modes_ship_empty_sets(self):
        data = self.world.fill_slot_data()
        for key in ("air_ride_goal_locations", "top_ride_goal_locations", "archipelago_goal_locations"):
            with self.subTest(key=key):
                self.assertEqual(set(data[key]), set())


class TestSlotDataGoalKeysUnsetByDefault(KARTestBase):
    """None of the three goal-key holdback flags ship for a goal no single unlock hands over. The
    default City Trial goal is a checklist count, which nothing in the pool short-circuits."""

    options = CT_ONLY

    def test_both_flags_zero(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["legendary_pieces_goal_gated"], 0)
        self.assertEqual(data["vs_king_dedede_goal_gated"], 0)
        self.assertEqual(data["ap_star_pieces_goal_gated"], 0)


class TestSlotDataLegendaryPiecesGoalGated(KARTestBase):
    """hydra_and_dragoon + item gating off: the mod must leave the six piece bits locked when it
    pre-fills the ungated item mask."""

    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon}

    def test_flag_set(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["city_trial_items_gated"], 0)
        self.assertEqual(data["legendary_pieces_goal_gated"], 1)


class TestSlotDataGoalKeyFlagOffWhenCategoryGated(KARTestBase):
    """With the category gated the mod never pre-fills its mask, so the goal-key flag stays 0 - the
    category's own gate flag already keeps every bit locked."""

    options = {
        **ALL_MODES,
        "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon,
        "city_trial_items_gated": Toggle.option_true,
    }

    def test_flag_clear(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["city_trial_items_gated"], 1)
        self.assertEqual(data["legendary_pieces_goal_gated"], 0)


class TestSlotDataVsKingDededeGoalGated(KARTestBase):
    """beat_king_dedede + stadium gating off: the mod must leave the Vs. King Dedede bit locked when it
    pre-fills the ungated stadium mask."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_flag_set(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["city_trial_stadiums_gated"], 0)
        self.assertEqual(data["vs_king_dedede_goal_gated"], 1)
