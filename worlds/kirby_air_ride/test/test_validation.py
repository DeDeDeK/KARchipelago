"""
Option validation tests: every OptionError-raising branch in KARWorld lives here.

Covers KARWorld.generate_early, _validate_options, _validate_pool_fits_locations,
and _determine_starter_items. Co-located so the exercised error branches are
auditable at a glance.
"""

from Options import OptionError, Toggle

from ..KARItems import KARItemName
from ..KARLocations import ARLocation, CTLocation
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase


class TestNoModesEnabled(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_none,
        "top_ride_goal": TopRideGoal.option_none,
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestCTFillerExceedsGoalAmount(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_n_checklist_blocks,
        "city_trial_checklist_amount": 5,
        "city_trial_checkbox_fillers": 5,
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestARFillerExceedsGoalAmount(KARTestBase):
    options = {
        **AR_ONLY,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 4,
        "air_ride_checkbox_fillers": 4,
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestTRFillerExceedsGoalAmount(KARTestBase):
    options = {
        **TR_ONLY,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 3,
        "top_ride_checkbox_fillers": 3,
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestCTChecklistListWrongMode(KARTestBase):
    # CT goal_locations containing an AR location should be rejected.
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_checklist_list,
        "city_trial_goal_locations": [ARLocation.RACE_100_LAPS],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestARChecklistListWrongMode(KARTestBase):
    # AR goal_locations containing a CT location should be rejected.
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_checklist_list,
        "air_ride_goal_locations": [CTLocation.DESTROY_ALL_HOUSES],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestTRChecklistListWrongMode(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "top_ride_goal": TopRideGoal.option_checklist_list,
        "top_ride_goal_locations": [ARLocation.RACE_100_LAPS],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestCTChecklistListEmpty(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_checklist_list,
        "city_trial_goal_locations": [],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestARChecklistListEmpty(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_checklist_list,
        "air_ride_goal_locations": [],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestTRChecklistListEmpty(KARTestBase):
    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "top_ride_goal": TopRideGoal.option_checklist_list,
        "top_ride_goal_locations": [],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestGuaranteedPoolExceedsLocations(KARTestBase):
    # CT-only with the patch cap spanning 1 -> 30 (29 Patch Cap Increase items) on top of the default
    # gated unlocks inflates the guaranteed pool to 116 items needing default locations (104 progression
    # + 5 counted-useful + 7 useful rewards) against only 90 CT default locations, tripping
    # _validate_pool_fits_locations. Rewards are gated on so the 7 useful rewards count toward the budget
    # (they are off by default).
    options = {
        **CT_ONLY,
        "checklist_rewards_gated": Toggle.option_true,
        "city_trial_patch_cap_min": 1,
        "city_trial_patch_cap_max": 30,
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


# A config tuned to fit by exactly 1 location, now that checklist rewards are guaranteed once each
# and so count against the default-location budget. Rewards are off by default, so this gates them on
# to keep the 7 useful rewards in the budget. With the gating categories at their defaults (ON),
# City Trial's progression is dominated by the gated unlock items rather than patch caps, so the patch
# cap span (min 16 -> max 18) is kept small to land the budget right at the edge:
#   75 CT progression with all gates on (gated unlocks + 6 legendary part markers + the CT/AR-tagged
#       items that fall to City Trial when Air Ride is disabled + multi-mode unlocks; the stadium and
#       color starters are precollected and removed, while patch types get no starter)
#   + 2 PATCH_CAP_INCREASE items (max 18 - min 16) -> 77 progression total
#   + 5 default checkbox fillers
#   + 7 useful checklist rewards (the non-overlapping CT rewards that must sit on default locations)
#   = 89 items needing default locations
#   = exactly 1 under the 90 CT default locations
# Without exclude_locations: fits. With the pair's 3 excludes: doesn't fit. Used by the pair below to
# pin that _validate_pool_fits_locations subtracts exclude_locations from the default count.
_TIGHT_POOL = {
    **CT_ONLY,
    "checklist_rewards_gated": Toggle.option_true,
    # 2 Patch Cap Increases (max 18 - min 16) on top of the 75 gates-on progression (stadium and
    # color starters precollected; no patch starter) = 77 progression, + 5 checkbox fillers + 7 useful
    # checklist rewards = 89 needing default, which just fits the 90 default CT locations. Filler-classified
    # rewards are not counted here - they may sit on excluded boxes - so only the 7 useful rewards add.
    "city_trial_patch_cap_min": 16,
    "city_trial_patch_cap_max": 18,
}


class TestTightPoolFitsWithoutExcludeLocations(KARTestBase):
    """Baseline for the exclude_locations pair: 89-items-needing-default just fit 90 default CT locations."""

    options = _TIGHT_POOL

    def test_setup_succeeds(self):
        # If this stops fitting (e.g. due to a default-locations rebalance or a reward-classification
        # change), the paired exclude_locations test below will need its excludes count tuned.
        self.assertEqual(len(self.world.progression_pool), 77)
        self.assertEqual(len(self.world.counted_useful_pool), 5)


class TestExcludeLocationsTipsValidatorOver(KARTestBase):
    """Same tight pool, but enough exclude_locations to push guaranteed > available."""

    options = {
        **_TIGHT_POOL,
        "exclude_locations": [
            CTLocation.DESTROY_ALL_HOUSES,
            CTLocation.BUST_STAR_POLE,
            CTLocation.BREAK_ALL_ROCKS,
        ],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestStadiumStarterDededeInInventoryRaises(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_true,
        "start_inventory": {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE: 1},
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


# allowed_items can no longer starve the draw pools: the cosmetic all-mode filler items (Big Kirby /
# Small Kirby, KARItemType.FILLER) are immune to allowed_items and carry _ALL_MODES, so filler_pool is
# always non-empty. These configs used to OptionError; they now generate using the cosmetic filler.


class TestAllowedItemsAllOffStillFills(KARTestBase):
    """Every give category off and traps off used to be unfillable. The cosmetic all-mode filler now
    covers every excluded box and leftover slot, so the config generates cleanly."""

    options = {**ALL_MODES, "allowed_items": [], "trap_chance": 0}

    def test_generates_with_cosmetic_filler(self):
        self.assertTrue(self.world.item_pools_built)
        self.assertIn(KARItemName.BIG_KIRBY, self.world.filler_pool)
        self.assertIn(KARItemName.SMALL_KIRBY, self.world.filler_pool)
        self.assertTrue(self.itempool_items(), "expected a populated item pool")


class TestAllowedItemsTopRideOnlyNoTRGivesStillFills(KARTestBase):
    """Top Ride Item Gives is Top Ride's only give-item filler source. With it off (and traps off), a
    TR-only seed with many excluded boxes used to OptionError; the cosmetic all-mode filler now fills
    those boxes. Low n_checklist amount forces many excluded boxes."""

    options = {
        **TR_ONLY,
        "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
        "top_ride_checklist_amount": 5,
        "top_ride_checkbox_fillers": 0,
        "allowed_items": ["Permanent Patches", "City Trial Item Gives", "City Trial Event Gives", "Copy Ability Gives"],
        "trap_chance": 0,
    }

    def test_generates_with_cosmetic_filler(self):
        self.assertTrue(self.world.item_pools_built)
        self.assertIn(KARItemName.BIG_KIRBY, self.world.filler_pool)
        self.assertTrue(self.itempool_items(), "expected a populated item pool")


class TestAllowedItemsAirRideOnlyNoCTGivesStillFills(KARTestBase):
    """City Trial Item Gives doubles as Air Ride's give-item filler source (the _AR_CT single-stat
    patches). With it off (and traps off), an AR-only seed with many excluded boxes used to OptionError;
    the cosmetic all-mode filler now fills those boxes."""

    options = {
        **AR_ONLY,
        "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
        "air_ride_checklist_amount": 5,
        "air_ride_checkbox_fillers": 0,
        "allowed_items": ["Permanent Patches", "City Trial Event Gives", "Copy Ability Gives", "Top Ride Item Gives"],
        "trap_chance": 0,
    }

    def test_generates_with_cosmetic_filler(self):
        self.assertTrue(self.world.item_pools_built)
        self.assertIn(KARItemName.BIG_KIRBY, self.world.filler_pool)
        self.assertTrue(self.itempool_items(), "expected a populated item pool")


class TestAllowedItemsAllOffWithFullTrapsFills(KARTestBase):
    """With every give category off and trap_chance 100 (traps default on), traps fill both leftover
    slots and excluded boxes alongside the cosmetic filler, so the config generates cleanly."""

    options = {**ALL_MODES, "allowed_items": [], "trap_chance": 100}

    def test_generates_with_traps_only(self):
        self.assertTrue(self.world.item_pools_built)
        self.assertTrue(self.itempool_items(), "expected a populated item pool")
