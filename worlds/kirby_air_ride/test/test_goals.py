"""
Goal wiring tests.

Every enabled mode contributes one victory event, and the completion rule ANDs them together. Which
location the event hangs off, and what rule guards it, depends on the goal kind:
  - 100_checklist_blocks / hydra_and_dragoon / beat_king_dedede and the two Archipelago assembly goals
    replace a real checklist box - the box leaves the location table and a `<box> (Victory)` event takes
    its place, carrying the requirement the box used to carry;
  - n_checklist_blocks and checklist_list synthesize an event in the mode's root region and leave every
    box a normal location;
  - max_stats_in_one_run has no box at all, so its event is purely synthetic.

The event *names* are a contract with the mod, which resynthesizes them, so they are spelled out here.
"""

from BaseClasses import CollectionState
from Options import Toggle

from ..KARItems import KARItemName, KARItemType
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
from . import ALL_MODES, CT_ONLY, KARTestBase, items_of_type


# Event-name templates; must stay in lockstep with the mod's goal-event synthesis.
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
        # checklist_list keeps the goal locations real (they back the victory event rule).
        real = self.real_location_names()
        for loc in self._GOAL_LOCS:
            self.assertIn(loc, real)
        self.assertIn(KARItemName.CITY_TRIAL_VICTORY, self.placed_event_items())


class TestCTGoalMaxStats(KARTestBase):
    """max_stats_in_one_run binds to no checklist box, so its victory event is synthesized in the City
    Trial region. With patches and items both ungated there is no stat route to gate on, so the only
    clause left is "hold every Patch Cap Increase"."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
        "city_trial_patch_cap_min": 14,
        "city_trial_patch_cap_max": 18,
        # max_stats pool is dominated by patch-cap items; turn off broad gating so it fits.
        "city_trial_events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "city_trial_patches_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_synthetic_victory_event_exists(self):
        self.assertIn(_MAX_STATS_EVENT, self.event_location_names())

    def test_needs_every_patch_cap_increase(self):
        # The cap has to reach the target for the goal to be achievable at all, so the event is behind
        # all (max - min) copies - not merely one.
        caps = self.get_items_by_name(KARItemName.PATCH_CAP_INCREASE)
        self.assertEqual(len(caps), 4, "18 - 14 should mint 4 Patch Cap Increase items")
        self.collect_all_but([KARItemName.PATCH_CAP_INCREASE, KARItemName.CITY_TRIAL_VICTORY])
        self.assertFalse(self.can_reach_location(_MAX_STATS_EVENT))
        self.collect(caps[:-1])
        self.assertFalse(self.can_reach_location(_MAX_STATS_EVENT), "reachable one Patch Cap Increase short")
        self.collect(caps[-1:])
        self.assertTrue(self.can_reach_location(_MAX_STATS_EVENT))


class TestCTGoalMaxStatsFlatCapNoRule(KARTestBase):
    """A flat cap (min == max) mints no Patch Cap Increase, and with both stat gates off every clause of
    the rule drops out, so the event is attached with no access rule at all."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
        "city_trial_patch_cap_min": 18,
        "city_trial_patch_cap_max": 18,
        "city_trial_patches_gated": Toggle.option_false,
        "city_trial_items_gated": Toggle.option_false,
    }

    def test_event_reachable_from_empty_state(self):
        self.assertEqual(self.count_in_pool(KARItemName.PATCH_CAP_INCREASE), 0)
        self.assertTrue(self.can_reach_location(_MAX_STATS_EVENT))


class TestCTGoalMaxStatsStatRoute(KARTestBase):
    """Patches AND items both gated: maxing all nine stats needs either every patch type able to spawn
    or the All Up item, so the rule is an OR of those two routes ANDed onto the cap clause. Either gate
    being off hands one route over for free, which is why the clause is only emitted when both are on.
    Every CT progression flag is opened to make room for the ~30 item unlocks the item gate adds."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
        "city_trial_patch_cap_min": 17,
        "city_trial_patch_cap_max": 18,
        "city_trial_patches_gated": Toggle.option_true,
        "city_trial_items_gated": Toggle.option_true,
        "city_trial_progression_high_effort": Toggle.option_true,
        "city_trial_progression_multiplayer": Toggle.option_true,
        "city_trial_progression_free_run": Toggle.option_true,
        "city_trial_progression_rng": Toggle.option_true,
        "city_trial_progression_bust_vehicles": Toggle.option_true,
        "city_trial_events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "machines_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_either_all_patch_types_or_all_up(self):
        self.assertAccessDependency(
            [_MAX_STATS_EVENT],
            [sorted(items_of_type(KARItemType.CT_PATCH_UNLOCK)), [KARItemName.UNLOCK_ITEM_ALL_UP]],
            only_check_listed=True,
        )

    def test_one_patch_type_short_is_not_enough(self):
        # HasAll, not HasAny: eight of the nine stats maxed is not "max stats".
        patches = sorted(items_of_type(KARItemType.CT_PATCH_UNLOCK))
        self.collect_all_but([*patches, KARItemName.UNLOCK_ITEM_ALL_UP, KARItemName.CITY_TRIAL_VICTORY])
        self.collect_by_name(patches[:-1])
        self.assertFalse(self.can_reach_location(_MAX_STATS_EVENT))
        self.collect_by_name(patches[-1])
        self.assertTrue(self.can_reach_location(_MAX_STATS_EVENT))


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
    """Three enabled modes means three victory events, and the completion rule needs all three."""

    options = ALL_MODES
    _VICTORIES = (
        KARItemName.CITY_TRIAL_VICTORY,
        KARItemName.AIR_RIDE_VICTORY,
        KARItemName.TOP_RIDE_VICTORY,
    )

    def test_all_three_victories_placed(self):
        placed = self.placed_event_items()
        for victory in self._VICTORIES:
            self.assertIn(victory, placed)

    def test_completion_needs_every_victory(self):
        # Drive the completion rule directly with hand-built states rather than collecting items: a
        # sweep would re-derive any victory event whose location is already reachable, so an "all but
        # one" state is not otherwise constructible.
        rule = self.multiworld.completion_condition[self.player]
        for withheld in self._VICTORIES:
            with self.subTest(withheld=withheld):
                state = CollectionState(self.multiworld)
                for victory in self._VICTORIES:
                    if victory != withheld:
                        state.collect(self.world.create_item(victory), prevent_sweep=True)
                self.assertFalse(rule(state), f"completion satisfied without {withheld}")
                state.collect(self.world.create_item(withheld), prevent_sweep=True)
                self.assertTrue(rule(state), "completion not satisfied with all three victories")


class TestSingleModeCompletionIgnoresOtherModes(KARTestBase):
    """The flip side: a one-mode seed's completion rule names only that mode's victory, so a disabled
    mode cannot leak into the requirement."""

    options = CT_ONLY

    def test_city_trial_victory_alone_completes(self):
        state = CollectionState(self.multiworld)
        state.collect(self.world.create_item(KARItemName.CITY_TRIAL_VICTORY), prevent_sweep=True)
        self.assertTrue(self.multiworld.completion_condition[self.player](state))
