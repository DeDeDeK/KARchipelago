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


class TestCTOnly(KARTestBase):
    options = CT_ONLY

    def test_flags(self):
        self.assertTrue(self.world.city_trial_enabled)
        self.assertFalse(self.world.air_ride_enabled)
        self.assertFalse(self.world.top_ride_enabled)

    def test_no_off_mode_locations(self):
        loc_names = self.real_location_names()
        self.assertFalse(loc_names & set(AIR_RIDE_LOCATION_TABLE))
        self.assertFalse(loc_names & set(TOP_RIDE_LOCATION_TABLE))

    def test_no_off_mode_rewards_in_pool(self):
        pool = set(self.itempool_names())
        self.assertFalse(pool & item_name_groups[KARItemGroup.AR_REWARDS])
        self.assertFalse(pool & item_name_groups[KARItemGroup.TR_REWARDS])


class TestAROnly(KARTestBase):
    options = AR_ONLY

    def test_flags(self):
        self.assertFalse(self.world.city_trial_enabled)
        self.assertTrue(self.world.air_ride_enabled)
        self.assertFalse(self.world.top_ride_enabled)

    def test_no_off_mode_locations(self):
        loc_names = self.real_location_names()
        self.assertFalse(loc_names & set(CITY_TRIAL_LOCATION_TABLE))
        self.assertFalse(loc_names & set(TOP_RIDE_LOCATION_TABLE))

    def test_no_off_mode_rewards_in_pool(self):
        pool = set(self.itempool_names())
        self.assertFalse(pool & item_name_groups[KARItemGroup.CT_REWARDS])
        self.assertFalse(pool & item_name_groups[KARItemGroup.TR_REWARDS])


class TestTROnly(KARTestBase):
    options = TR_ONLY

    def test_flags(self):
        self.assertFalse(self.world.city_trial_enabled)
        self.assertFalse(self.world.air_ride_enabled)
        self.assertTrue(self.world.top_ride_enabled)

    def test_no_off_mode_locations(self):
        loc_names = self.real_location_names()
        self.assertFalse(loc_names & set(CITY_TRIAL_LOCATION_TABLE))
        self.assertFalse(loc_names & set(AIR_RIDE_LOCATION_TABLE))

    def test_no_off_mode_rewards_in_pool(self):
        pool = set(self.itempool_names())
        self.assertFalse(pool & item_name_groups[KARItemGroup.CT_REWARDS])
        self.assertFalse(pool & item_name_groups[KARItemGroup.AR_REWARDS])


class TestCTAndAR(KARTestBase):
    options = CT_AND_AR

    def test_flags(self):
        self.assertTrue(self.world.city_trial_enabled)
        self.assertTrue(self.world.air_ride_enabled)
        self.assertFalse(self.world.top_ride_enabled)

    def test_no_tr_rewards_in_pool(self):
        pool = set(self.itempool_names())
        self.assertFalse(pool & item_name_groups[KARItemGroup.TR_REWARDS])


class TestCTAndTR(KARTestBase):
    options = CT_AND_TR

    def test_flags(self):
        self.assertTrue(self.world.city_trial_enabled)
        self.assertFalse(self.world.air_ride_enabled)
        self.assertTrue(self.world.top_ride_enabled)

    def test_no_ar_locations(self):
        loc_names = self.real_location_names()
        self.assertFalse(loc_names & set(AIR_RIDE_LOCATION_TABLE))

    def test_no_ar_rewards_in_pool(self):
        pool = set(self.itempool_names())
        self.assertFalse(pool & item_name_groups[KARItemGroup.AR_REWARDS])


class TestARAndTR(KARTestBase):
    options = AR_AND_TR

    def test_flags(self):
        self.assertFalse(self.world.city_trial_enabled)
        self.assertTrue(self.world.air_ride_enabled)
        self.assertTrue(self.world.top_ride_enabled)

    def test_no_ct_locations(self):
        loc_names = self.real_location_names()
        self.assertFalse(loc_names & set(CITY_TRIAL_LOCATION_TABLE))

    def test_no_ct_rewards_in_pool(self):
        pool = set(self.itempool_names())
        self.assertFalse(pool & item_name_groups[KARItemGroup.CT_REWARDS])


class TestAllModes(KARTestBase):
    options = ALL_MODES

    def test_flags(self):
        self.assertTrue(self.world.city_trial_enabled)
        self.assertTrue(self.world.air_ride_enabled)
        self.assertTrue(self.world.top_ride_enabled)

    def test_all_mode_locations_present(self):
        loc_names = self.real_location_names()
        # Use a sentinel non-excluded location per mode (excluded-by-default progression locations
        # still exist as locations, so they wouldn't prove the mode is present).
        self.assertIn(CTLocation.DESTROY_ALL_HOUSES, loc_names)
        self.assertIn(ARLocation.RACE_100_LAPS, loc_names)
        self.assertIn(TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS, loc_names)
