from Options import Toggle

from ..KARItems import KARItemName
from ..KARLocations import (
    AIR_RIDE_GOAL_TO_LOCATION,
    CITY_TRIAL_GOAL_TO_LOCATION,
    TOP_RIDE_GOAL_TO_LOCATION,
    ARLocation,
    CTLocation,
    TRLocation,
)
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from ..KARRegions import KARRegion
from . import ALL_MODES, CT_ONLY, KARTestBase


# Event-name templates mirror the synthesis in KARRegions._create_goal_events.
# Keep these in lockstep with that file.
def _n_blocks_event(mode_region: str, n: int) -> str:
    return f"{mode_region}: Complete {n} Checklist Blocks"


def _victory_event(goal_location_name: str) -> str:
    return f"{goal_location_name} (Victory)"


_MAX_STATS_EVENT = f"{KARRegion.CITY_TRIAL}: Max Stats (Insanity)"


class TestCTGoal100Blocks(KARTestBase):
    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_100_checklist_blocks}

    def test_goal_location_excluded_and_victory_placed(self):
        real = self.real_location_names()
        goal_loc = CITY_TRIAL_GOAL_TO_LOCATION[CityTrialGoal.option_100_checklist_blocks]
        self.assertNotIn(goal_loc, real)
        self.assertIn(KARItemName.CITY_TRIAL_VICTORY, self.placed_event_items())


class TestCTGoalNBlocks(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_n_checklist_blocks,
        "city_trial_checklist_amount": 30,
        "city_trial_checkbox_fillers": 0,
    }

    def test_creates_event_and_completion(self):
        events = self.event_location_names()
        self.assertIn(_n_blocks_event(KARRegion.CITY_TRIAL, 30), events)
        self.assertIn(KARItemName.CITY_TRIAL_VICTORY, self.placed_event_items())


class TestCTGoalHydraAndDragoon(KARTestBase):
    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon}

    def test_goal_location_replaced_by_victory_event(self):
        goal_loc = CITY_TRIAL_GOAL_TO_LOCATION[CityTrialGoal.option_hydra_and_dragoon]
        real = self.real_location_names()
        self.assertNotIn(goal_loc, real)
        self.assertIn(_victory_event(goal_loc), self.event_location_names())


class TestCTGoalBeatKingDedede(KARTestBase):
    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_beat_king_dedede}

    def test_goal_location_replaced_by_victory_event(self):
        goal_loc = CITY_TRIAL_GOAL_TO_LOCATION[CityTrialGoal.option_beat_king_dedede]
        real = self.real_location_names()
        self.assertNotIn(goal_loc, real)
        self.assertIn(_victory_event(goal_loc), self.event_location_names())


class TestCTGoalChecklistList(KARTestBase):
    _GOAL_LOCS = [
        CTLocation.DESTROY_ALL_HOUSES,
        CTLocation.BUST_STAR_POLE,
    ]
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_checklist_list,
        "city_trial_goal_locations": _GOAL_LOCS,
    }

    def test_goal_locations_remain_real(self):
        # checklist_list keeps the goal locations as real locations (they back the event rule).
        real = self.real_location_names()
        for loc in self._GOAL_LOCS:
            self.assertIn(loc, real)
        self.assertIn(KARItemName.CITY_TRIAL_VICTORY, self.placed_event_items())


class TestCTGoalMaxStats(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
        "city_trial_progressive_patch_caps": Toggle.option_true,
        "city_trial_patch_cap_amount": 5,
        # max_stats pool is dominated by patch-cap items; turn off broad gating so it fits.
        "city_trial_events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "city_trial_patches_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "city_trial_progressive_stadiums": Toggle.option_false,
    }

    def test_synthetic_victory_event_exists(self):
        self.assertIn(_MAX_STATS_EVENT, self.event_location_names())


class TestARGoal100Blocks(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
    }

    def test_goal_location_excluded(self):
        real = self.real_location_names()
        goal_loc = AIR_RIDE_GOAL_TO_LOCATION[AirRideGoal.option_100_checklist_blocks]
        self.assertNotIn(goal_loc, real)
        self.assertIn(KARItemName.AIR_RIDE_VICTORY, self.placed_event_items())


class TestTRGoal100Blocks(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
    }

    def test_goal_location_excluded(self):
        real = self.real_location_names()
        goal_loc = TOP_RIDE_GOAL_TO_LOCATION[TopRideGoal.option_100_checklist_blocks]
        self.assertNotIn(goal_loc, real)
        self.assertIn(KARItemName.TOP_RIDE_VICTORY, self.placed_event_items())


class TestARGoalNBlocks(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 30,
        "air_ride_checkbox_fillers": 0,
    }

    def test_creates_event_and_completion(self):
        events = self.event_location_names()
        self.assertIn(_n_blocks_event(KARRegion.AIR_RIDE, 30), events)
        self.assertIn(KARItemName.AIR_RIDE_VICTORY, self.placed_event_items())


class TestTRGoalNBlocks(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 30,
        "top_ride_checkbox_fillers": 0,
    }

    def test_creates_event_and_completion(self):
        events = self.event_location_names()
        self.assertIn(_n_blocks_event(KARRegion.TOP_RIDE, 30), events)
        self.assertIn(KARItemName.TOP_RIDE_VICTORY, self.placed_event_items())


class TestARGoalChecklistList(KARTestBase):
    _GOAL_LOCS = [
        ARLocation.RACE_100_LAPS,
        ARLocation.DEFEAT_300_OF_YOUR_ENEMIES,
    ]
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_checklist_list,
        "air_ride_goal_locations": _GOAL_LOCS,
    }

    def test_goal_locations_remain_real(self):
        real = self.real_location_names()
        for loc in self._GOAL_LOCS:
            self.assertIn(loc, real)
        self.assertIn(KARItemName.AIR_RIDE_VICTORY, self.placed_event_items())


class TestTRGoalChecklistList(KARTestBase):
    _GOAL_LOCS = [
        TRLocation.CROSS_GOAL_20,
        TRLocation.FR_RACE_100_LAPS,
    ]
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "top_ride_goal": TopRideGoal.option_checklist_list,
        "top_ride_goal_locations": _GOAL_LOCS,
    }

    def test_goal_locations_remain_real(self):
        real = self.real_location_names()
        for loc in self._GOAL_LOCS:
            self.assertIn(loc, real)
        self.assertIn(KARItemName.TOP_RIDE_VICTORY, self.placed_event_items())


class TestAllModesVictoryRequiresAll(KARTestBase):
    options = ALL_MODES

    def test_all_three_victories_placed(self):
        placed = self.placed_event_items()
        self.assertIn(KARItemName.CITY_TRIAL_VICTORY, placed)
        self.assertIn(KARItemName.AIR_RIDE_VICTORY, placed)
        self.assertIn(KARItemName.TOP_RIDE_VICTORY, placed)
