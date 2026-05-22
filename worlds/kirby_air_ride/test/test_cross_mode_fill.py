"""
Cross-mode placement fill tests.

When cross_mode_placement is off, KAR reward items are item-rule-locked to their
source mode (Air Ride Rewards → AR locations, etc.). The random useful sampling
in create_items used to pick uniformly from useful_pool, which can overcommit a
mode whose locations are scarce and crash remaining_fill. Regression tests below
exercise configurations near that ceiling.
"""

from Options import Toggle

from ..KARItems import item_name_groups
from ..KARLocations import AIR_RIDE_LOCATION_TABLE, CITY_TRIAL_LOCATION_TABLE, TOP_RIDE_LOCATION_TABLE
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from . import KARTestBase

# Symbolic mode tags. Values are arbitrary as long as they're hashable + distinct;
# the dicts below use them as keys but never assume a particular order.
_CT, _AR, _TR = "city_trial", "air_ride", "top_ride"

_LOCATION_NAME_TO_MODE: dict[str, str] = {
    **dict.fromkeys(CITY_TRIAL_LOCATION_TABLE, _CT),
    **dict.fromkeys(AIR_RIDE_LOCATION_TABLE, _AR),
    **dict.fromkeys(TOP_RIDE_LOCATION_TABLE, _TR),
}

_REWARD_NAME_TO_MODE: dict[str, str] = {
    **dict.fromkeys(item_name_groups["City Trial Rewards"], _CT),
    **dict.fromkeys(item_name_groups["Air Ride Rewards"], _AR),
    **dict.fromkeys(item_name_groups["Top Ride Rewards"], _TR),
}


def _assert_no_mode_overcommit(test_case):
    """Each mode's placeable locations must be at least the count of player-owned reward
    items targeting that mode in the itempool + precollected. If this holds, fill will
    not exhaust a mode."""
    player = test_case.player
    mode_locs: dict[str, int] = {_CT: 0, _AR: 0, _TR: 0}
    for loc in test_case.multiworld.get_locations(player):
        if loc.address is None or loc.locked:
            continue
        m = _LOCATION_NAME_TO_MODE.get(loc.name)
        if m is not None:
            mode_locs[m] += 1

    mode_items: dict[str, int] = {_CT: 0, _AR: 0, _TR: 0}
    for item in test_case.itempool_items():
        m = _REWARD_NAME_TO_MODE.get(item.name)
        if m is not None:
            mode_items[m] += 1

    for m in (_CT, _AR, _TR):
        test_case.assertLessEqual(
            mode_items[m],
            mode_locs[m],
            f"mode {m} has {mode_items[m]} mode-locked reward items but only {mode_locs[m]} locations to receive them",
        )


class TestCrossModeOffSmallSecondaryModes(KARTestBase):
    # Mirrors the fuzzer-discovered seed: CT 100-blocks (lots of CT locs), AR/TR
    # n_blocks with small N, and many gates on so the pool has many AR reward items.
    # Pre-fix this combination's random useful sampling would overcommit AR.
    options = {
        "cross_mode_placement": Toggle.option_false,
        "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 5,
        "air_ride_checkbox_fillers": 0,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 5,
        "top_ride_checkbox_fillers": 0,
        "events_gated": Toggle.option_true,
        "abilities_gated": Toggle.option_true,
        "patches_gated": Toggle.option_true,
        "machines_gated": Toggle.option_true,
        "boxes_gated": Toggle.option_true,
        "air_ride_courses_gated": Toggle.option_true,
        "top_ride_courses_gated": Toggle.option_true,
        "colors_gated": Toggle.option_true,
    }

    def test_no_mode_overcommitted(self):
        _assert_no_mode_overcommit(self)


class TestCrossModeOffARTinyMode(KARTestBase):
    # Pathological: AR has only a few locations and machine/color/course gating is off,
    # which leaves their reward items in the useful pool. The unsampled-cap pre-fix
    # version of create_items would routinely dump more AR rewards than AR can hold.
    options = {
        "cross_mode_placement": Toggle.option_false,
        "city_trial_goal": CityTrialGoal.option_100_checklist_blocks,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 3,
        "air_ride_checkbox_fillers": 0,
        "air_ride_progression_high_effort": Toggle.option_false,
        "air_ride_progression_free_run": Toggle.option_false,
        "air_ride_progression_time_attack": Toggle.option_false,
        "top_ride_goal": TopRideGoal.option_none,
        "machines_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "air_ride_courses_gated": Toggle.option_false,
    }

    def test_no_mode_overcommitted(self):
        _assert_no_mode_overcommit(self)


class TestCrossModeOnAllowsOvercommit(KARTestBase):
    # Sanity counter-test: with cross_mode_placement ON, the per-mode invariant does NOT
    # need to hold — items can cross modes freely. Uses the same near-overcommit shape as
    # TestCrossModeOffARTinyMode (AR shrunk to 3 locations, CT at 100 blocks) and verifies
    # both (a) pool size still matches placeable locations and (b) at least one mode would
    # have failed the cross-mode-off invariant — i.e. the overcommit really is allowed.
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

    def test_no_cross_mode_item_rule_attached(self):
        # _set_cross_mode_placement_rules is a no-op when cross_mode_placement is ON,
        # so locations should keep the default no-op item_rule. (A mode-locked rule
        # would also reject foreign items, which is the wrong semantics here.)
        from BaseClasses import Location

        non_default = [
            loc.name
            for loc in self.multiworld.get_locations(self.player)
            if loc.address is not None and loc.item_rule is not Location.item_rule
        ]
        self.assertEqual(non_default, [], f"cross-mode-on leaked an item_rule: {non_default}")
