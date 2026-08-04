"""
Progress-type tests for the *_progression_* location-category toggles.

Each mode exposes several toggles (high effort, multiplayer, free run, RNG, bust-vehicle, time attack)
deciding whether a whole category of checklist locations counts toward progression: OFF (the default)
EXCLUDES the group, ON makes it DEFAULT. The result lands in the per-mode location name sets.

These tests pin both directions:
  - all toggles off: the excluded set is exactly the union of the categories, nothing more;
  - one toggle on: only that category leaves the excluded set, proving each option is wired to its own
    group and not a sibling's.

run_default_tests is off: these assert static categorization only, so a full fill would be wasted here.
"""

from Options import Toggle

from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    KARLocationGroup,
    location_name_groups,
)
from . import AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

# (label, mode preset, default-set attr, excluded-set attr, location table, [(option, group), ...]).
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


def _make_default_off_test(label, preset, default_attr, excluded_attr, table, toggles):
    class _DefaultOff(KARTestBase):
        options = preset
        run_default_tests = False

        def test_default_excludes_every_category(self):
            default = getattr(self.world, default_attr)
            excluded = getattr(self.world, excluded_attr)
            table_names = {str(name) for name in table}
            # The two sets partition the whole mode table.
            self.assertEqual(default | excluded, table_names, "default/excluded must partition the table")
            self.assertEqual(default & excluded, set(), "a location cannot be both default and excluded")
            # All toggles off: excluded set is exactly the union of the progression categories.
            union: set[str] = set().union(*(location_name_groups[group] for _, group in toggles))
            self.assertEqual(excluded, union, "default-off excluded set must equal the union of all categories")
            for option, group in toggles:
                with self.subTest(option=option):
                    self.assertTrue(
                        location_name_groups[group] <= excluded,
                        f"{option} off should exclude its whole category",
                    )

    _DefaultOff.__name__ = f"TestProgressionDefaultOff_{label}"
    _DefaultOff.__qualname__ = _DefaultOff.__name__
    return _DefaultOff


def _make_toggle_isolation_test(label, preset, default_attr, excluded_attr, table, toggles, option, group):
    class _ToggleOn(KARTestBase):
        options = {**preset, option: Toggle.option_true}
        run_default_tests = False

        def test_only_this_category_becomes_default(self):
            default = getattr(self.world, default_attr)
            excluded = getattr(self.world, excluded_attr)
            table_names = {str(name) for name in table}
            others: set[str] = set().union(*(location_name_groups[g] for opt, g in toggles if opt != option), set())
            # Turning this one toggle on removes exactly its category's contribution: only the
            # still-off categories remain excluded.
            self.assertEqual(excluded, others, f"{option} on should leave only the other categories excluded")
            self.assertEqual(default, table_names - others)
            # Locations unique to this category must have moved to default; also guards against a
            # vacuous test (a group fully shadowed by its siblings).
            unique = location_name_groups[group] - others
            self.assertTrue(unique, f"{option}'s category has no locations of its own; effect is unobservable")
            self.assertTrue(unique <= default, f"{option} on should make its own-category locations default")
            self.assertTrue(unique.isdisjoint(excluded))

    _ToggleOn.__name__ = f"TestProgressionToggleOn_{option}"
    _ToggleOn.__qualname__ = _ToggleOn.__name__
    return _ToggleOn


for _label, _preset, _default_attr, _excluded_attr, _table, _toggles in _MODES:
    _default_cls = _make_default_off_test(_label, _preset, _default_attr, _excluded_attr, _table, _toggles)
    globals()[_default_cls.__name__] = _default_cls
    for _option, _group in _toggles:
        _iso_cls = _make_toggle_isolation_test(
            _label, _preset, _default_attr, _excluded_attr, _table, _toggles, _option, _group
        )
        globals()[_iso_cls.__name__] = _iso_cls
