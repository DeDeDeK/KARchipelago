"""fill_slot_data() returns the dict the client consumes on connect; generation-only options are
deliberately omitted. Update EXPECTED_KEYS when a field is intentionally added or removed."""

import json

from Options import Toggle

from .. import UT_OPTIONS_KEY
from ..KARLocations import CTLocation
from ..KAROptions import ArchipelagoGoal, CityTrialGoal
from . import ALL_MODES, CT_ONLY, KARTestBase, names

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
        "ap_patches",
        # Runtime spawn-rate floor; the ceiling is generation-only
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
        # Universal Tracker's raw-option record; not consumed by the client or the mod
        UT_OPTIONS_KEY,
    }
)

_INT_KEYS = (
    "city_trial_checklist_amount",
    "air_ride_checklist_amount",
    "top_ride_checklist_amount",
    "archipelago_checklist_amount",
    "city_trial_patch_cap_min",
    "city_trial_patch_cap_max",
    "spawn_rate_min",
    "city_trial_goal",
    "air_ride_goal",
    "top_ride_goal",
    "archipelago_goal",
)
_LOCATION_SET_KEYS = (
    "city_trial_goal_locations",
    "air_ride_goal_locations",
    "top_ride_goal_locations",
    "archipelago_goal_locations",
)


def _make_key_set_test(label: str, preset: dict) -> None:
    class _KeySet(KARTestBase):
        options = preset

        def test_exact_key_set(self):
            self.assertEqual(set(self.world.fill_slot_data()), EXPECTED_KEYS)

        def test_serializes_as_json(self):
            # The network layer round-trips slot_data as JSON; a non-serializable value fails at connect.
            json.dumps(dict(self.world.fill_slot_data()))

        def test_value_types(self):
            data = self.world.fill_slot_data()
            for key in _INT_KEYS:
                with self.subTest(key=key):
                    self.assertIsInstance(data[key], int)
            for key in _LOCATION_SET_KEYS:
                with self.subTest(key=key):
                    self.assertIsInstance(list(data[key]), list)

    _KeySet.__name__ = f"TestSlotDataShape_{label}"
    _KeySet.__qualname__ = _KeySet.__name__
    globals()[_KeySet.__name__] = _KeySet


for _label, _preset in (("ct_only", CT_ONLY), ("all_modes", ALL_MODES)):
    _make_key_set_test(_label, _preset)


class TestSlotDataSpawnRateMin(KARTestBase):
    """Spawn rate moves in 10% steps, so the min is snapped to the nearest multiple of 10 at generation
    and the snapped value is what ships. ALL_MODES gives the Spawn Rate Up items the range mints room to
    land."""

    options = ALL_MODES
    auto_construct = False

    def test_min_ships_snapped(self):
        for raw_min, raw_max, shipped in ((80, 200, 80), (64, 227, 60)):
            with self.subTest(spawn_rate_min=raw_min):
                self.options = {**self.options, "spawn_rate_min": raw_min, "spawn_rate_max": raw_max}
                self.world_setup()
                self.assertEqual(self.world.fill_slot_data()["spawn_rate_min"], shipped)


class TestSlotDataGoalFields(KARTestBase):
    """The checklist_list goal is the one the mod cannot evaluate from a count: it has to be told which
    boxes to watch, so the LocationSet ships by name and the other modes ship empty."""

    _GOAL_LOCS = [CTLocation.DESTROY_ALL_HOUSES, CTLocation.BUST_STAR_POLE]
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_checklist_list,
        "city_trial_goal_locations": _GOAL_LOCS,
    }

    def test_goal_value_and_locations_ship(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["city_trial_goal"], CityTrialGoal.option_checklist_list)
        self.assertEqual(set(data["city_trial_goal_locations"]), names(self._GOAL_LOCS))

    def test_other_modes_ship_empty_sets(self):
        data = self.world.fill_slot_data()
        for key in _LOCATION_SET_KEYS[1:]:
            with self.subTest(key=key):
                self.assertEqual(set(data[key]), set())


# The three goal-key holdback flags. Each ships 1 only when its category is ungated AND the goal is keyed
# on part of it, so the mod knows to leave exactly those bits locked while pre-filling the rest.
# (label, options, the flags expected to be set).
_HOLDBACK_CASES: list[tuple[str, dict, set[str]]] = [
    ("no_goal_key", CT_ONLY, set()),
    (
        "legendary_pieces",
        {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon},
        {"legendary_pieces_goal_gated"},
    ),
    # With the category gated the mod never pre-fills its mask, so the flag stays clear.
    (
        "legendary_pieces_category_gated",
        {
            **ALL_MODES,
            "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon,
            "city_trial_items_gated": Toggle.option_true,
        },
        set(),
    ),
    (
        "vs_king_dedede",
        {
            **CT_ONLY,
            "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
            "city_trial_stadiums_gated": Toggle.option_false,
        },
        {"vs_king_dedede_goal_gated"},
    ),
    (
        "ap_star_pieces",
        {**CT_ONLY, "archipelago_goal": ArchipelagoGoal.option_assemble_archipelago_star},
        {"ap_star_pieces_goal_gated"},
    ),
]

_HOLDBACK_FLAGS = ("legendary_pieces_goal_gated", "vs_king_dedede_goal_gated", "ap_star_pieces_goal_gated")


def _make_holdback_test(label: str, opts: dict, expected: set[str]) -> None:
    class _Holdback(KARTestBase):
        options = opts

        def test_holdback_flags(self):
            data = self.world.fill_slot_data()
            for flag in _HOLDBACK_FLAGS:
                with self.subTest(flag=flag):
                    self.assertEqual(data[flag], int(flag in expected))

    _Holdback.__name__ = f"TestSlotDataGoalHoldback_{label}"
    _Holdback.__qualname__ = _Holdback.__name__
    globals()[_Holdback.__name__] = _Holdback


for _label, _opts, _expected in _HOLDBACK_CASES:
    _make_holdback_test(_label, _opts, _expected)
