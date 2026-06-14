"""
Beatability tests for KAR.

`assertBeatable(bool)` checks whether `multiworld.state` can satisfy the completion condition (one victory per
enabled mode). These tests verify which items are load-bearing for the goal, and which goal variants have no
AP-side gate (the game itself enforces).

`multiworld.state` starts with precollected items only (random starters per gated category);
collect_all_but / collect_by_name extend it with itempool items.
"""

from Options import Toggle

from ..KARItems import KARItemName
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase


class TestCTBeatableWithAllItems(KARTestBase):
    """Sanity check: CT default goal is beatable after collecting every itempool item."""

    options = CT_ONLY

    def test_beatable_after_collect_all(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestALLMODESBeatableWithAllItems(KARTestBase):
    """Sanity check: 3-mode 100-blocks-each goal is beatable after collecting every item."""

    options = ALL_MODES

    def test_beatable_after_collect_all(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


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
    event (placed in the VSKD stadium region).

    collect_all_but iterates get_items(), which includes the filled victory event. CITY_TRIAL_VICTORY must be
    excluded explicitly so the sweep, not the pre-population, decides whether it gets collected."""

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


class TestCTBeatKingDededeNoGateWithoutProgressiveStadiums(KARTestBase):
    """beat_king_dedede + stadiums gated off: the victory event sits in the VSKD region but no AP-side rule
    guards the entrance; the game enforces stadium unlock via its vanilla path. Pins current behavior."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_beatable_from_precollected(self):
        self.assertBeatable(True)


class TestCTHydraAndDragoonNoItemGate(KARTestBase):
    """hydra_and_dragoon goal: the victory event sits in the CITY_TRIAL root region with no AP-side access rule,
    so it is beatable from precollected state. Pins current behavior."""

    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon}

    def test_beatable_from_precollected(self):
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
    """ALL_MODES + CT beat_king_dedede: removing the CT-binding item makes the overall multi-mode goal
    unbeatable even with AR and TR fully collectible.

    CITY_TRIAL_VICTORY is excluded because get_items() includes the filled victory event, which would otherwise
    short-circuit the completion check."""

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


class TestARBeatableWithAllItems(KARTestBase):
    """Sanity check: AR-only default goal is beatable after collecting every itempool item."""

    options = AR_ONLY

    def test_beatable_after_collect_all(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestTRBeatableWithAllItems(KARTestBase):
    """Sanity check: TR-only default goal is beatable after collecting every itempool item."""

    options = TR_ONLY

    def test_beatable_after_collect_all(self):
        self.collect_all_but_victories()
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
