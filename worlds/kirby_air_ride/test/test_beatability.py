"""Which items are load-bearing for a goal. `multiworld.state` starts with the precollected starters
alone, so what is pinned here is the direction WorldTestBase's automatic
`test_all_state_can_reach_everything` does not cover: unbeatable from the starters, and what flips it."""

from Options import Toggle

from ..KARItems import GATING_CATEGORIES, LEGENDARY_PIECE_UNLOCK_ITEMS, KARItemName
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from . import ALL_MODES, AR_AND_TR, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

_OFF = Toggle.option_false

# (label, preset). Every 100-block goal needs 100 reachable boxes in its mode, which course, machine
# and stadium gating keep well out of reach of the precollected starters.
_HUNDRED_BLOCK_PRESETS = [("ct", CT_ONLY), ("ar", AR_ONLY), ("tr", TR_ONLY), ("all_modes", ALL_MODES)]

# (label, options) for a goal small enough that the mode root's freely-reachable boxes satisfy it.
_TRIVIAL_GOAL_PRESETS = [
    (
        "ct",
        {
            **CT_ONLY,
            "city_trial_goal": CityTrialGoal.option_n_checklist_blocks,
            "city_trial_checklist_amount": 2,
            "city_trial_checkbox_fillers": 0,
        },
    ),
    (
        "ar",
        {
            **AR_ONLY,
            "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
            "air_ride_checklist_amount": 2,
            "air_ride_checkbox_fillers": 0,
        },
    ),
    (
        "tr",
        {
            **TR_ONLY,
            "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
            "top_ride_checklist_amount": 2,
            "top_ride_checkbox_fillers": 0,
        },
    ),
]


def _make_beatable_from_precollected_test(label: str, opts: dict, beatable: bool) -> type:
    class _FromPrecollected(KARTestBase):
        options = opts

        def test_beatable_from_precollected(self):
            self.assertBeatable(beatable)

    name = f"Test{'Trivial' if beatable else 'HundredBlock'}Goal_{label}"
    _FromPrecollected.__name__ = name
    _FromPrecollected.__qualname__ = name
    return _FromPrecollected


for _label, _preset in _HUNDRED_BLOCK_PRESETS:
    _cls = _make_beatable_from_precollected_test(_label, _preset, beatable=False)
    globals()[_cls.__name__] = _cls

for _label, _preset in _TRIVIAL_GOAL_PRESETS:
    _cls = _make_beatable_from_precollected_test(_label, _preset, beatable=True)
    globals()[_cls.__name__] = _cls


class TestTrivialARTRGoalsDoNotBeatAllModes(KARTestBase):
    """Every enabled mode's victory is required: trivial AR and TR goals leave CT's 100 blocks standing."""

    options = {
        "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 1,
        "air_ride_checkbox_fillers": 0,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 1,
        "top_ride_checkbox_fillers": 0,
    }

    def test_not_beatable_from_precollected(self):
        self.assertBeatable(False)


# The Vs. King Dedede unlock keys the beat_king_dedede goal whichever way the stadium gate is set: with
# it off the mod hands over the other 23 at connect, but goal_forced_unlocks keeps this one in the pool.
_DEDEDE_GOAL = {"city_trial_goal": CityTrialGoal.option_beat_king_dedede}


def _make_dedede_test(label: str, opts: dict) -> type:
    class _DededeGoal(KARTestBase):
        options = opts

        def test_not_beatable_from_precollected(self):
            self.assertBeatable(False)

        def test_stadium_unlock_is_the_key(self):
            self.assert_victory_needs_all([KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE], KARItemName.CITY_TRIAL_VICTORY)

    _DededeGoal.__name__ = f"TestBeatKingDedede_{label}"
    _DededeGoal.__qualname__ = _DededeGoal.__name__
    return _DededeGoal


for _label, _opts in (
    ("stadiums_gated", {**CT_ONLY, **_DEDEDE_GOAL, "city_trial_stadiums_gated": Toggle.option_true}),
    ("stadiums_ungated", {**CT_ONLY, **_DEDEDE_GOAL, "city_trial_stadiums_gated": _OFF}),
    # With AR and TR fully collectible, the CT-binding item still decides the multi-mode goal.
    ("all_modes", {**ALL_MODES, **_DEDEDE_GOAL}),
):
    _cls = _make_dedede_test(_label, _opts)
    globals()[_cls.__name__] = _cls


class TestHydraAndDragoonGoalNeedsEveryPiece(KARTestBase):
    """hydra_and_dragoon with item gating off: every other City Trial item is handed over at connect, but
    the six legendary piece unlocks stay in the pool and all six are required."""

    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon}

    def test_not_beatable_from_precollected(self):
        self.assertBeatable(False)

    def test_all_six_pieces_required(self):
        self.assert_victory_needs_all(LEGENDARY_PIECE_UNLOCK_ITEMS, KARItemName.CITY_TRIAL_VICTORY)


# Gate-off reconciliation: a gate OFF makes the mod pre-unlock the whole category at connect, so its
# unlocks and overlapping rewards both leave the pool. These pin that the reconciled configs still
# generate a beatable seed - the failure mode is a rule keyed on an item generation never minted.
_ALL_RECONCILABLE_OFF = {cat.option: _OFF for cat in GATING_CATEGORIES if cat.overlapping_rewards}


def _make_gate_off_beatable_test(label: str, opts: dict) -> type:
    class _GateOffBeatable(KARTestBase):
        options = opts

        def test_beatable(self):
            self.collect_all_but_victories()
            self.assertBeatable(True)

    _GateOffBeatable.__name__ = f"TestGateOffBeatable_{label}"
    _GateOffBeatable.__qualname__ = _GateOffBeatable.__name__
    return _GateOffBeatable


for _label, _opts in (
    ("ct_machines_and_stadiums_off", {**CT_ONLY, "machines_gated": _OFF, "city_trial_stadiums_gated": _OFF}),
    # Stadiums still gated: their unlocks carry the gate, so the stadium rewards drop rather than promote.
    ("ct_machines_off_stadiums_on", {**CT_ONLY, "machines_gated": _OFF}),
    ("all_modes_every_reconcilable_gate_off", {**ALL_MODES, **_ALL_RECONCILABLE_OFF}),
    # No City Trial: the Air Ride machine cells lose their reward gate.
    ("ar_tr_machines_off", {**AR_AND_TR, "machines_gated": _OFF}),
):
    _cls = _make_gate_off_beatable_test(_label, _opts)
    globals()[_cls.__name__] = _cls
