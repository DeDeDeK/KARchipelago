"""The seven CT / AR / TR on-off combinations: a mode is enabled by its goal option, and a disabled one
contributes neither locations nor its mode-specific checklist rewards (no box exists to award them)."""

from ..KARItems import KARItemGroup, item_name_groups
from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    ARLocation,
    CTLocation,
    TRLocation,
)
from . import ALL_MODES, AR_AND_TR, AR_ONLY, CT_AND_AR, CT_AND_TR, CT_ONLY, TR_ONLY, KARTestBase

# Per mode: the enabled-flag attribute, its location table, its reward group, and a sentinel box no
# goal replaces, so it exists as a location whenever the mode is on.
_MODES: dict[str, tuple[str, dict, str, str]] = {
    "ct": ("city_trial_enabled", CITY_TRIAL_LOCATION_TABLE, KARItemGroup.CT_REWARDS, CTLocation.DESTROY_ALL_HOUSES),
    "ar": ("air_ride_enabled", AIR_RIDE_LOCATION_TABLE, KARItemGroup.AR_REWARDS, ARLocation.RACE_100_LAPS),
    "tr": (
        "top_ride_enabled",
        TOP_RIDE_LOCATION_TABLE,
        KARItemGroup.TR_REWARDS,
        TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS,
    ),
}

_COMBINATIONS: list[tuple[str, dict, set[str]]] = [
    ("ct", CT_ONLY, {"ct"}),
    ("ar", AR_ONLY, {"ar"}),
    ("tr", TR_ONLY, {"tr"}),
    ("ct_ar", CT_AND_AR, {"ct", "ar"}),
    ("ct_tr", CT_AND_TR, {"ct", "tr"}),
    ("ar_tr", AR_AND_TR, {"ar", "tr"}),
    ("all", ALL_MODES, {"ct", "ar", "tr"}),
]


def _make_combination_test(label: str, preset: dict, enabled: set[str]) -> type:
    class _Combination(KARTestBase):
        options = preset

        def test_enabled_flags_match_the_preset(self):
            for mode, (flag, _, _, _) in _MODES.items():
                with self.subTest(mode=mode):
                    self.assertEqual(getattr(self.world, flag), mode in enabled)
            # The Archipelago checklist is opt-in on top of the three real modes, never implied by them.
            self.assertFalse(self.world.archipelago_enabled)

        def test_only_enabled_modes_contribute_locations(self):
            loc_names = self.real_location_names()
            for mode, (_, table, _, sentinel) in _MODES.items():
                with self.subTest(mode=mode):
                    if mode in enabled:
                        self.assertIn(sentinel, loc_names)
                    else:
                        self.assertFalse(loc_names & set(table))

        def test_disabled_modes_mint_no_rewards(self):
            pool = set(self.itempool_names())
            for mode, (_, _, group, _) in _MODES.items():
                if mode not in enabled:
                    with self.subTest(mode=mode):
                        self.assertFalse(pool & item_name_groups[group])

    _Combination.__name__ = f"TestModes_{label}"
    _Combination.__qualname__ = _Combination.__name__
    return _Combination


for _label, _preset, _enabled in _COMBINATIONS:
    globals()[f"TestModes_{_label}"] = _make_combination_test(_label, _preset, _enabled)
