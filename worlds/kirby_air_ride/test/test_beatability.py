"""
Beatability tests for KAR.

`assertBeatable(bool)` checks whether `multiworld.state` can satisfy the completion condition (one
victory per enabled mode), so these verify which items are load-bearing for the goal and which goal
variants have no AP-side gate. `multiworld.state` starts with precollected items only (the random
starters); collect_all_but / collect_by_name extend it with itempool items.

Deliberately absent: "collect everything, assert beatable" sanity classes. WorldTestBase auto-runs
`test_all_state_can_reach_everything` for every class with options, which asserts beatable from
all-state *and* that every location is reachable - strictly stronger. What is worth pinning here is
the other direction: unbeatable from the precollected starters alone, and which single item flips it.
"""

from Options import Toggle

from ..KARItems import LEGENDARY_PIECE_UNLOCK_ITEMS, KARItemName
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase


class TestCT100BlocksNotBeatableFromPrecollected(KARTestBase):
    """Default CT options (100-blocks goal, most gates ON): precollected-only state cannot reach 100 locations."""

    options = CT_ONLY

    def test_not_beatable_with_precollected_only(self):
        self.assertBeatable(False)


class TestALLMODES100BlocksNotBeatableFromPrecollected(KARTestBase):
    """ALL_MODES with 100 blocks each requires 100 reachable locations per mode. From precollected-only state
    far fewer are reachable, so the game cannot be beaten."""

    options = ALL_MODES

    def test_not_beatable_with_precollected_only(self):
        self.assertBeatable(False)


class TestCTBeatKingDededeRequiresStadiumUnlock(KARTestBase):
    """beat_king_dedede + stadiums gated on: UNLOCK_STADIUM_VS_KING_DEDEDE is required to reach the victory
    event in the VSKD stadium region. collect_all_but iterates get_items(), which includes the filled
    victory event, so CITY_TRIAL_VICTORY is excluded explicitly to let the sweep decide it."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_true,
    }

    def test_unlock_required(self):
        self.collect_all_but(
            [
                KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,
                KARItemName.CITY_TRIAL_VICTORY,
            ]
        )
        self.assertBeatable(False)
        self.collect_by_name(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)
        self.assertBeatable(True)


class TestCTBeatKingDededeUngatedStadiumsStillRequiresUnlock(KARTestBase):
    """beat_king_dedede + stadiums gated off: the other 23 stadiums are handed over at connect, but the
    goal's own stadium unlock stays in the pool, so the victory event is still behind it."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_not_beatable_from_precollected(self):
        self.assertBeatable(False)

    def test_unlock_required(self):
        self.collect_all_but(
            [
                KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,
                KARItemName.CITY_TRIAL_VICTORY,
            ]
        )
        self.assertBeatable(False)
        self.collect_by_name(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)
        self.assertBeatable(True)


class TestCTHydraAndDragoonNoItemGate(KARTestBase):
    """hydra_and_dragoon goal + item gating off: every other City Trial item is handed over at connect,
    but the six legendary piece unlocks stay in the pool, so the victory event is still behind them."""

    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon}

    def test_not_beatable_from_precollected(self):
        self.assertBeatable(False)

    def test_all_six_pieces_required(self):
        self.collect_all_but([*LEGENDARY_PIECE_UNLOCK_ITEMS, KARItemName.CITY_TRIAL_VICTORY])
        self.assertBeatable(False)
        for piece in LEGENDARY_PIECE_UNLOCK_ITEMS[:-1]:
            self.collect_by_name(piece)
            self.assertBeatable(False)
        self.collect_by_name(LEGENDARY_PIECE_UNLOCK_ITEMS[-1])
        self.assertBeatable(True)


class TestCTNBlocksSmallGoalBeatableFromPrecollected(KARTestBase):
    """n_checklist_blocks goal with a very small N: from precollected-only state, enough locations are
    reachable (the CITY_TRIAL root has many trivially-reachable ones) to satisfy the goal."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_n_checklist_blocks,
        "city_trial_checklist_amount": 2,
        "city_trial_checkbox_fillers": 0,
    }

    def test_beatable_from_precollected(self):
        self.assertBeatable(True)


class TestALLMODESNeedsCTVictory(KARTestBase):
    """ALL_MODES + CT beat_king_dedede: removing the CT-binding item makes the multi-mode goal unbeatable
    even with AR and TR fully collectible. CITY_TRIAL_VICTORY is excluded because get_items() includes the
    filled victory event, which would otherwise short-circuit the completion check."""

    options = {**ALL_MODES, "city_trial_goal": CityTrialGoal.option_beat_king_dedede}

    def test_ct_dedede_unlock_required_for_all_victory(self):
        self.collect_all_but(
            [
                KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,
                KARItemName.CITY_TRIAL_VICTORY,
            ]
        )
        self.assertBeatable(False)
        self.collect_by_name(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)
        self.assertBeatable(True)


class TestAR100BlocksNotBeatableFromPrecollected(KARTestBase):
    """AR-only 100-blocks goal: many AR locations sit behind course/machine gates, so precollected can't reach
    100 AR locations."""

    options = AR_ONLY

    def test_not_beatable_with_precollected_only(self):
        self.assertBeatable(False)


class TestTR100BlocksNotBeatableFromPrecollected(KARTestBase):
    """TR-only 100-blocks goal: TR locations are gated behind course unlocks, so precollected can't reach 100."""

    options = TR_ONLY

    def test_not_beatable_with_precollected_only(self):
        self.assertBeatable(False)


class TestARNBlocksSmallGoalBeatableFromPrecollected(KARTestBase):
    """AR n_checklist_blocks with very small N: enough AR root locations are reachable from precollected."""

    options = {
        **AR_ONLY,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 2,
        "air_ride_checkbox_fillers": 0,
    }

    def test_beatable_from_precollected(self):
        self.assertBeatable(True)


class TestTRNBlocksSmallGoalBeatableFromPrecollected(KARTestBase):
    """TR n_checklist_blocks with very small N: enough TR root locations are reachable from precollected."""

    options = {
        **TR_ONLY,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 2,
        "top_ride_checkbox_fillers": 0,
    }

    def test_beatable_from_precollected(self):
        self.assertBeatable(True)


class TestARGoalAloneNotEnoughForALLMODES(KARTestBase):
    """ALL_MODES requires every enabled mode's victory: reaching AR's goal alone is insufficient."""

    options = {
        "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 1,
        "air_ride_checkbox_fillers": 0,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 1,
        "top_ride_checkbox_fillers": 0,
    }

    def test_precollected_not_beatable_even_with_trivial_ar_tr_goals(self):
        # AR and TR goals are trivial (N=1) and reachable from precollected, but CT 100-blocks is not.
        self.assertBeatable(False)
