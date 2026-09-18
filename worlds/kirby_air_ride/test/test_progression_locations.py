"""The *_progression_* toggles decide whether a category of checklist boxes counts toward progression:
OFF - the default - EXCLUDES the group, ON makes it DEFAULT. Both directions are pinned, so each option
is shown wired to its own group. run_default_tests is off: a fill would be wasted on static state."""

from Options import Toggle

from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    KARLocationGroup,
    location_name_groups,
)
from ..KAROptions import ArchipelagoGoal, CityTrialGoal
from . import AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, names

# (label, preset, default-set attr, excluded-set attr, location table, [(option, group), ...]).
_MODES: list[tuple[str, dict, str, str, dict, list[tuple[str, KARLocationGroup]]]] = [
    (
        "city_trial",
        CT_ONLY,
        "city_trial_default_locations",
        "city_trial_excluded_locations",
        CITY_TRIAL_LOCATION_TABLE,
        [
            ("city_trial_progression_high_effort", KARLocationGroup.CT_HIGH_EFFORT),
            ("city_trial_progression_multiplayer", KARLocationGroup.CT_MULTIPLAYER),
            ("city_trial_progression_free_run", KARLocationGroup.CT_FREE_RUN),
            ("city_trial_progression_rng", KARLocationGroup.CT_RNG),
            ("city_trial_progression_bust_vehicles", KARLocationGroup.CT_BUST_VEHICLE_ON_VEHICLE),
        ],
    ),
    (
        "air_ride",
        AR_ONLY,
        "air_ride_default_locations",
        "air_ride_excluded_locations",
        AIR_RIDE_LOCATION_TABLE,
        [
            ("air_ride_progression_high_effort", KARLocationGroup.AR_HIGH_EFFORT),
            ("air_ride_progression_free_run", KARLocationGroup.AR_FREE_RUN),
            ("air_ride_progression_time_attack", KARLocationGroup.AR_TIME_ATTACK),
            ("air_ride_progression_rng", KARLocationGroup.AR_RNG),
        ],
    ),
    (
        "top_ride",
        TR_ONLY,
        "top_ride_default_locations",
        "top_ride_excluded_locations",
        TOP_RIDE_LOCATION_TABLE,
        [
            ("top_ride_progression_high_effort", KARLocationGroup.TR_HIGH_EFFORT),
            ("top_ride_progression_free_run", KARLocationGroup.TR_FREE_RUN),
            ("top_ride_progression_time_attack", KARLocationGroup.TR_TIME_ATTACK),
            ("top_ride_progression_multiplayer", KARLocationGroup.TR_MULTIPLAYER),
        ],
    ),
]


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


def _make_default_off_test(preset, default_attr, excluded_attr, table, toggles) -> type:
    class _DefaultOff(KARTestBase):
        options = preset
        run_default_tests = False

        def test_default_excludes_every_category(self):
            default = getattr(self.world, default_attr)
            excluded = getattr(self.world, excluded_attr)
            self.assertEqual(default | excluded, names(table), "default/excluded must partition the table")
            self.assertEqual(default & excluded, set(), "a location cannot be both default and excluded")
            union: set[str] = set().union(*(location_name_groups[group] for _, group in toggles))
            self.assertEqual(excluded, union, "default-off excluded set must equal the union of all categories")

    return _DefaultOff


def _make_toggle_isolation_test(preset, default_attr, excluded_attr, table, toggles, option, group) -> type:
    class _ToggleOn(KARTestBase):
        options = {**preset, option: Toggle.option_true}
        run_default_tests = False

        def test_only_this_category_becomes_default(self):
            default = getattr(self.world, default_attr)
            excluded = getattr(self.world, excluded_attr)
            others: set[str] = set().union(*(location_name_groups[g] for opt, g in toggles if opt != option), set())
            self.assertEqual(excluded, others, f"{option} on should leave only the other categories excluded")
            self.assertEqual(default, names(table) - others)
            # The locations unique to this category must have moved; this also guards against a vacuous
            # test, where a group is fully shadowed by its siblings.
            unique = location_name_groups[group] - others
            self.assertTrue(unique, f"{option}'s category has no locations of its own; effect is unobservable")
            self.assertTrue(unique <= default, f"{option} on should make its own-category locations default")

    return _ToggleOn


for _label, _preset, _default_attr, _excluded_attr, _table, _toggles in _MODES:
    _register(
        _make_default_off_test(_preset, _default_attr, _excluded_attr, _table, _toggles),
        f"TestProgressionDefaultOff_{_label}",
    )
    for _option, _group in _toggles:
        _register(
            _make_toggle_isolation_test(_preset, _default_attr, _excluded_attr, _table, _toggles, _option, _group),
            f"TestProgressionToggleOn_{_option}",
        )


class TestArchipelagoHasNoProgressionFlags(KARTestBase):
    """The Archipelago checklist exposes no progression sub-toggles, so every AP box is DEFAULT and none
    is ever excluded. That is what lets an AP-enabled seed absorb the cross-mode color keys, so if a flag
    is ever added its excluded set has to be budgeted for in _compute_capacity."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 5,
    }
    run_default_tests = False

    def test_every_ap_location_is_default(self):
        self.assertEqual(self.world.archipelago_excluded_locations, set())
        self.assertEqual(self.world.archipelago_default_locations, set(AP_CHECKLIST_LOCATION_TABLE))
