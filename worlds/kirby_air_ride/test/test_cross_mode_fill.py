"""
Cross-mode placement tests.

cross_mode_placement is a progression-only concern. When it is off, KAR locks only its
PROGRESSION items to their source mode(s) via item_rules (so each mode's required progression
stays reachable by playing that mode). Non-progression items (checklist rewards, traps, filler,
counted-useful) are deliberately left unrestricted and may be placed in any mode, since they
gate nothing.

These tests pin three things:
  - progression items are mode-locked by item_rule; non-progression items are not;
  - configurations that overcommit a mode with non-progression rewards generate fine (no FillError);
  - a config whose PROGRESSION genuinely can't fit a mode raises a clean OptionError, while the same
    config with cross_mode_placement ON (progression free to spread) generates.
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


class TestProgressionModeLockedRewardsFree(KARTestBase):
    """Under cross_mode_placement=false, an Air Ride location's item_rule rejects a City-Trial
    progression item but accepts a (non-progression) City-Trial reward and remote items."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_false}

    def _location_of_mode(self, mode: GameMode):
        for loc in self.multiworld.get_locations(self.player):
            if loc.address is not None and location_code_to_mode(loc.address) == mode:
                return loc
        raise AssertionError(f"no real location found for mode {mode}")

    def test_progression_locked_but_rewards_cross(self):
        ar_loc = self._location_of_mode(GameMode.AIRRIDE)

        ct_progression_name = _first_item(
            lambda d: (d.classification & ItemClassification.progression) and d.source_modes == {GameMode.CITYTRIAL}
        )
        ct_reward_name = _first_item(
            lambda d: not (d.classification & ItemClassification.progression) and d.source_modes == {GameMode.CITYTRIAL}
        )

        ct_progression = self.world.create_item(ct_progression_name)
        ct_reward = self.world.create_item(ct_reward_name)

        # Progression CT item must not be allowed at an AR location; a CT reward (non-prog) may.
        self.assertFalse(ar_loc.item_rule(ct_progression), "CT progression should be locked out of an AR location")
        self.assertTrue(ar_loc.item_rule(ct_reward), "CT reward (non-progression) should be allowed at an AR location")

    def test_progression_allowed_in_its_own_mode(self):
        ct_loc = self._location_of_mode(GameMode.CITYTRIAL)
        ct_progression_name = _first_item(
            lambda d: (d.classification & ItemClassification.progression) and d.source_modes == {GameMode.CITYTRIAL}
        )
        self.assertTrue(ct_loc.item_rule(self.world.create_item(ct_progression_name)))


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


class TestCrossModeOffRewardOvercommitOk(KARTestBase):
    """A config that crams far more (non-progression) Air Ride rewards into the pool than AR has
    locations used to crash fill. Now that only progression is mode-locked, the rewards spill into
    other modes freely and generation succeeds. We just assert the world built and the pool matches
    the placeable location count."""

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


# A config whose City-Trial PROGRESSION (126 Patch Cap Increase + stadium unlocks = 149 items) cannot
# fit City Trial's 90 default locations, while Top Ride supplies enough empty locations that the global
# pool-fits check still passes. With cross-mode off this must raise the per-mode OptionError; with
# cross-mode on the progression is free to spill into Top Ride, so it generates.
_PROGRESSION_OVERFLOW_OPTIONS = {
    "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
    "city_trial_patch_cap_amount": 127,
    "city_trial_progressive_patch_caps": Toggle.option_true,
    "spawn_rate_progressive": Toggle.option_false,
    "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
    "top_ride_checklist_amount": 5,
    "top_ride_checkbox_fillers": 0,
    "city_trial_events_gated": Toggle.option_false,
    "abilities_gated": Toggle.option_false,
    "city_trial_patches_gated": Toggle.option_false,
    "city_trial_items_gated": Toggle.option_false,
    "machines_gated": Toggle.option_false,
    "city_trial_boxes_gated": Toggle.option_false,
    "colors_gated": Toggle.option_false,
    "top_ride_courses_gated": Toggle.option_false,
    "top_ride_items_gated": Toggle.option_false,
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
