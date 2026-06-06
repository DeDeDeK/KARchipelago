"""
Cross-mode placement tests.

When cross_mode_placement is off, KAR locks both its PROGRESSION and its CHECKLIST REWARD items to
their source mode(s) via item_rules (so each mode's required progression stays reachable by playing
that mode, and its native rewards are earned within it). Other non-progression items (traps, filler,
counted-useful) gate nothing and are left unrestricted, so they may be placed in any mode.

These tests pin:
  - progression and reward items are mode-locked by item_rule; other non-progression items are not;
  - a config whose PROGRESSION genuinely can't fit a mode raises a clean OptionError, while the same
    config with cross_mode_placement ON (progression free to spread) generates;
  - a config whose confined REWARDS push a mode past its default locations raises a clean OptionError
    under cross-off but generates under cross-on.
"""

from BaseClasses import ItemClassification
from Options import OptionError, Toggle

from ..KARData import GameMode, location_code_to_mode
from ..KARItems import ITEM_TABLE
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from . import ALL_MODES, KARTestBase


def _first_item(predicate) -> str:
    """First ITEM_TABLE entry (sorted by name) matching predicate, for deterministic tests."""
    for name, data in sorted(ITEM_TABLE.items(), key=lambda kv: str(kv[0])):
        if predicate(data):
            return str(name)
    raise AssertionError("no ITEM_TABLE entry matched predicate")


class TestProgressionAndRewardsModeLocked(KARTestBase):
    """Under cross_mode_placement=false, an Air Ride location's item_rule rejects a City-Trial
    progression item AND a City-Trial checklist reward, but still accepts other non-progression
    City-Trial items (e.g. a give-item) that gate nothing, plus remote items."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_false}

    def _location_of_mode(self, mode: GameMode):
        for loc in self.multiworld.get_locations(self.player):
            if loc.address is not None and location_code_to_mode(loc.address) == mode:
                return loc
        raise AssertionError(f"no real location found for mode {mode}")

    def test_progression_and_rewards_locked_other_nonprog_free(self):
        from ..KARItems import CHECKLIST_REWARD_TYPES

        ar_loc = self._location_of_mode(GameMode.AIRRIDE)

        ct_progression_name = _first_item(
            lambda d: (d.classification & ItemClassification.progression) and d.source_modes == {GameMode.CITYTRIAL}
        )
        ct_reward_name = _first_item(
            lambda d: d.type in CHECKLIST_REWARD_TYPES and d.source_modes == {GameMode.CITYTRIAL}
        )
        # A non-progression, non-reward CT item (give-item / filler): gates nothing, floats freely.
        ct_free_name = _first_item(
            lambda d: (
                not (d.classification & ItemClassification.progression)
                and d.type not in CHECKLIST_REWARD_TYPES
                and d.source_modes == {GameMode.CITYTRIAL}
            )
        )

        ct_progression = self.world.create_item(ct_progression_name)
        ct_reward = self.world.create_item(ct_reward_name)
        ct_free = self.world.create_item(ct_free_name)

        self.assertFalse(ar_loc.item_rule(ct_progression), "CT progression should be locked out of an AR location")
        self.assertFalse(ar_loc.item_rule(ct_reward), "CT reward should be locked out of an AR location")
        self.assertTrue(ar_loc.item_rule(ct_free), "Non-reward non-prog CT item should float to an AR location")

    def test_progression_and_reward_allowed_in_own_mode(self):
        from ..KARItems import CHECKLIST_REWARD_TYPES

        ct_loc = self._location_of_mode(GameMode.CITYTRIAL)
        ct_progression_name = _first_item(
            lambda d: (d.classification & ItemClassification.progression) and d.source_modes == {GameMode.CITYTRIAL}
        )
        ct_reward_name = _first_item(
            lambda d: d.type in CHECKLIST_REWARD_TYPES and d.source_modes == {GameMode.CITYTRIAL}
        )
        self.assertTrue(ct_loc.item_rule(self.world.create_item(ct_progression_name)))
        self.assertTrue(ct_loc.item_rule(self.world.create_item(ct_reward_name)))


class TestCrossModeOnNoItemRule(KARTestBase):
    """With cross_mode_placement ON, _set_cross_mode_placement_rules is a no-op: locations keep the
    default no-op item_rule and the pool still exactly fills the placeable locations."""

    options = {
        "cross_mode_placement": Toggle.option_true,
        "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 3,
        "air_ride_checkbox_fillers": 0,
        "top_ride_goal": TopRideGoal.option_none,
        "machines_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
    }

    def test_pool_size_matches_locations(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))

    def test_no_item_rule_attached(self):
        from BaseClasses import Location

        non_default = [
            loc.name
            for loc in self.multiworld.get_locations(self.player)
            if loc.address is not None and loc.item_rule is not Location.item_rule
        ]
        self.assertEqual(non_default, [], f"cross-mode-on leaked an item_rule: {non_default}")


class TestCrossModeOffRewardsFitGenerate(KARTestBase):
    """Rewards are confined to their mode under cross-off, but because they are unique one-time items
    each mode's reward load is small (Air Ride here carries only its own handful of rewards), so it
    fits comfortably and generation succeeds. (This config was a fill crash in the old soup era when
    rewards were unbounded draw-with-replacement.) Assert the world built and the pool exactly fills
    the placeable locations."""

    options = {
        "cross_mode_placement": Toggle.option_false,
        "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 3,
        "air_ride_checkbox_fillers": 0,
        "top_ride_goal": TopRideGoal.option_none,
        "machines_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
    }

    def test_pool_size_matches_locations(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


# A config whose City-Trial confined REWARDS tip it over: with the gating categories at their defaults
# (ON), City Trial holds 85 confined progression items (the gated unlocks + 6 legendary part markers +
# the CT/AR-tagged items that fall to City Trial when Air Ride is disabled + 22 Patch Cap Increase from
# patch_cap_amount=23) which fit its 90 default locations on their own, but adding the 7 useful CT
# checklist rewards (also confined under cross-off) pushes the needs-default demand to 92 > 90. With
# cross-off this must raise the per-mode OptionError; with cross-on the progression+rewards are free to
# spill into Top Ride, so it generates. Isolates that reward demand is counted in
# _validate_local_fits_modes, not just progression. (Top Ride supplies the overflow room.)
_REWARD_OVERFLOW_OPTIONS = {
    "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
    "city_trial_patch_cap_amount": 23,
    "city_trial_progressive_patch_caps": Toggle.option_true,
    "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
    "top_ride_checklist_amount": 5,
    "top_ride_checkbox_fillers": 0,
}


class TestCrossModeOffRewardOverflowRaises(KARTestBase):
    options = {**_REWARD_OVERFLOW_OPTIONS, "cross_mode_placement": Toggle.option_false}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestCrossModeOnRewardOverflowGenerates(KARTestBase):
    options = {**_REWARD_OVERFLOW_OPTIONS, "cross_mode_placement": Toggle.option_true}

    def test_generates(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


# A config whose City-Trial PROGRESSION alone cannot fit City Trial's 90 default locations, while Top
# Ride supplies enough empty locations that the global pool-fits check still passes. With the gating
# categories at their defaults (ON), City Trial holds 92 confined progression items (the gated unlocks +
# 6 legendary part markers + the CT/AR-tagged items that fall to City Trial when Air Ride is disabled +
# 29 Patch Cap Increase from patch_cap_amount=30, the max) > 90 default. With cross-mode off this must
# raise the per-mode OptionError; with cross-mode on the progression is free to spill into Top Ride, so
# it generates. Unlike _REWARD_OVERFLOW_OPTIONS, progression overflows here without counting any rewards.
_PROGRESSION_OVERFLOW_OPTIONS = {
    "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
    "city_trial_patch_cap_amount": 30,
    "city_trial_progressive_patch_caps": Toggle.option_true,
    "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
    "top_ride_checklist_amount": 5,
    "top_ride_checkbox_fillers": 0,
}


class TestCrossModeOffProgressionOverflowRaises(KARTestBase):
    options = {**_PROGRESSION_OVERFLOW_OPTIONS, "cross_mode_placement": Toggle.option_false}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestCrossModeOnProgressionOverflowGenerates(KARTestBase):
    options = {**_PROGRESSION_OVERFLOW_OPTIONS, "cross_mode_placement": Toggle.option_true}

    def test_generates(self):
        # No per-mode lock with cross-mode on, so the same item counts fit across both modes.
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))


# A config whose excluded (filler-only) locations can't be filled under cross-off. Excluded boxes accept
# only filler-classified items; under cross-off the filler checklist rewards are mode-locked while only
# the mode-neutral generic filler floats. Here City Trial keeps all its progression flags ON (so it has
# very few excluded boxes) but still mints its 17 filler rewards, which "waste" generic-filler capacity:
# create_items sizes generic_filler = max(0, total_excluded - total_filler_rewards), so City Trial's
# surplus filler rewards shrink the shared generic pool. Air Ride meanwhile turns all its progression
# flags OFF, excluding ~57 of its location groups; with only its own ~23 filler rewards plus the depleted
# generic pool it cannot fill them. This must raise the per-mode OptionError under cross-off (the
# excluded-filler Hall check in _validate_local_fits_modes), while cross-on lets the filler rewards float
# freely and fill any mode's excluded boxes, so it generates. Pins that excluded-box filler economy is
# validated, not just default-box demand.
_EXCLUDED_FILLER_OVERFLOW_OPTIONS = {
    "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
    "city_trial_progression_high_effort": Toggle.option_true,
    "city_trial_progression_multiplayer": Toggle.option_true,
    "city_trial_progression_free_run": Toggle.option_true,
    "city_trial_progression_rng": Toggle.option_true,
    "city_trial_progression_bust_vehicles": Toggle.option_true,
    "city_trial_checkbox_fillers": 0,
    "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
    "air_ride_checklist_amount": 3,
    "air_ride_checkbox_fillers": 0,
    "air_ride_progression_free_run": Toggle.option_false,
    "air_ride_progression_time_attack": Toggle.option_false,
    "air_ride_progression_high_effort": Toggle.option_false,
    "top_ride_goal": TopRideGoal.option_none,
}


class TestCrossModeOffExcludedFillerOverflowRaises(KARTestBase):
    options = {**_EXCLUDED_FILLER_OVERFLOW_OPTIONS, "cross_mode_placement": Toggle.option_false}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestCrossModeOnExcludedFillerOverflowGenerates(KARTestBase):
    options = {**_EXCLUDED_FILLER_OVERFLOW_OPTIONS, "cross_mode_placement": Toggle.option_true}

    def test_generates(self):
        placeable = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(placeable))
