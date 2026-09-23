"""The Archipelago checklist: a synthetic 4th mode with no base-game equivalent - 52 boxes, no native
rewards, and each box living in the region of the activity it describes. Its goal wiring lives in
test_goals.py and its validation branches in test_validation.py."""

import unittest

from ..KARData import (
    AP_CHECKLIST_CODE_BASE,
    AP_CHECKLIST_CODE_NUM,
    AP_PATCH_CODE_BASE,
    GameMode,
    location_code_to_ap_patch_index,
    location_code_to_mode_clear,
    mode_clear_to_location_code,
)
from ..KARItems import CHECKLIST_REWARD_TYPES, ITEM_TABLE, KARItemName
from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    AP_PATCH_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    KARLocationGroup,
    ProgressionCategory,
    location_name_groups,
)
from ..KAROptions import (
    AirRideGoal,
    ArchipelagoChecklistAmount,
    ArchipelagoGoal,
    CityTrialGoal,
    TopRideGoal,
)
from ..KARRegions import REGION_TO_MODE, KARRegion
from . import CT_ONLY, KARTestBase

# City Trial on its default goal plus a small Archipelago n_checklist goal.
AP_WITH_CT: dict = {
    "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
    "archipelago_checklist_amount": 3,
}


class TestArchipelagoLocationTable(unittest.TestCase):
    """The band's code <-> clear_kind pairing is a wire contract with the mod's ap_checks[] array that
    nothing mechanically catches a desync in, and the band stops exactly where AP Patches begin."""

    def test_codes_contiguous_from_the_band_base(self):
        codes = sorted(d.code for d in AP_CHECKLIST_LOCATION_TABLE.values())
        self.assertEqual(codes, list(range(AP_CHECKLIST_CODE_BASE, AP_CHECKLIST_CODE_BASE + AP_CHECKLIST_CODE_NUM)))
        self.assertEqual(len(AP_CHECKLIST_LOCATION_TABLE), AP_CHECKLIST_CODE_NUM)

    def test_every_code_round_trips_through_the_codec(self):
        for clear_kind in range(AP_CHECKLIST_CODE_NUM):
            with self.subTest(clear_kind=clear_kind):
                code = mode_clear_to_location_code(GameMode.ARCHIPELAGO, clear_kind)
                self.assertEqual(code, AP_CHECKLIST_CODE_BASE + clear_kind)
                self.assertEqual(location_code_to_mode_clear(code), (GameMode.ARCHIPELAGO, clear_kind))

    def test_the_band_sits_between_top_ride_and_the_ap_patches(self):
        self.assertEqual(location_code_to_mode_clear(AP_CHECKLIST_CODE_BASE - 1), (GameMode.TOPRIDE, 119))
        last = AP_CHECKLIST_CODE_BASE + AP_CHECKLIST_CODE_NUM - 1
        self.assertEqual(last + 1, AP_PATCH_CODE_BASE)
        # AP Patch codes are their own category, never checkboxes.
        self.assertIsNone(location_code_to_mode_clear(AP_PATCH_CODE_BASE))
        self.assertIsNone(location_code_to_ap_patch_index(last))

    def test_no_native_rewards(self):
        # The AP checklist awards none of its own; it only hosts other modes' shuffled ones.
        for name, data in AP_CHECKLIST_LOCATION_TABLE.items():
            with self.subTest(location=name):
                self.assertIsNone(data.native_reward)

    def test_names_do_not_collide_with_other_tables(self):
        """LOCATION_TABLE merges the four mode tables by name, so a collision would silently drop one of
        the two boxes. The "Archipelago: " prefix is what keeps them apart."""
        others = (
            set(CITY_TRIAL_LOCATION_TABLE)
            | set(AIR_RIDE_LOCATION_TABLE)
            | set(TOP_RIDE_LOCATION_TABLE)
            | set(AP_PATCH_LOCATION_TABLE)
        )
        self.assertEqual(sorted(set(AP_CHECKLIST_LOCATION_TABLE) & others), [])
        self.assertEqual(len(LOCATION_TABLE), len(others) + len(AP_CHECKLIST_LOCATION_TABLE))

    def test_every_box_region_is_classified(self):
        # A box's region decides which mode it pulls into logic, via REGION_TO_MODE.
        for name, data in AP_CHECKLIST_LOCATION_TABLE.items():
            with self.subTest(location=name):
                self.assertIn(data.region, REGION_TO_MODE)

    # Each area group owns exactly the boxes whose name carries its prefix.
    _AREA_GROUP_PREFIXES = {
        KARLocationGroup.AP_CITY_TRIAL: "Archipelago: City Trial: ",
        KARLocationGroup.AP_STADIUMS: "Archipelago: Stadium: ",
        KARLocationGroup.AP_AIR_RIDE: "Archipelago: Air Ride: ",
    }

    def test_area_groups_partition_the_table(self):
        grouped = sorted(name for group in self._AREA_GROUP_PREFIXES for name in location_name_groups[group])
        self.assertEqual(grouped, sorted(AP_CHECKLIST_LOCATION_TABLE))
        for group, prefix in self._AREA_GROUP_PREFIXES.items():
            for name in location_name_groups[group]:
                with self.subTest(group=group, location=name):
                    self.assertTrue(name.startswith(prefix), f"{name} is filed under {group}")

    def test_ap_groups_hold_only_ap_boxes(self):
        ap_groups = [group for group in KARLocationGroup if group.startswith("Archipelago: ")]
        self.assertTrue(ap_groups)
        for group in ap_groups:
            with self.subTest(group=group):
                self.assertLessEqual(location_name_groups[group], set(AP_CHECKLIST_LOCATION_TABLE))


class TestArchipelagoOptionSurface(unittest.TestCase):
    """The AP checklist short-fills the 120-cell grid, so its two count-shaped options track the table's
    size rather than the grid's - and a 100-blocks goal it could never satisfy is simply not offered."""

    def test_checklist_amount_range_stops_at_the_table(self):
        self.assertEqual(ArchipelagoChecklistAmount.range_end, len(AP_CHECKLIST_LOCATION_TABLE))
        self.assertEqual(ArchipelagoChecklistAmount.range_end, AP_CHECKLIST_CODE_NUM)
        self.assertGreaterEqual(ArchipelagoChecklistAmount.default, ArchipelagoChecklistAmount.range_start)
        self.assertLessEqual(ArchipelagoChecklistAmount.default, ArchipelagoChecklistAmount.range_end)

    def test_100_blocks_is_offered_by_the_other_modes_only(self):
        # Add it back alongside the 100th box; until then this keeps the option surface honest.
        self.assertNotIn("100_checklist_blocks", ArchipelagoGoal.options)
        for goal in (CityTrialGoal, AirRideGoal, TopRideGoal):
            with self.subTest(goal=goal.__name__):
                self.assertIn("100_checklist_blocks", goal.options)


class TestArchipelagoDisabledByDefault(KARTestBase):
    """The AP checklist defaults to none: its region and boxes are absent and its checkbox filler is
    never minted, even though the tab still appears in-game."""

    options = CT_ONLY

    def test_nothing_is_created(self):
        region_names = {region.name for region in self.multiworld.get_regions(self.player)}
        self.assertNotIn(KARRegion.ARCHIPELAGO, region_names)
        self.assertFalse(self.real_location_names() & set(AP_CHECKLIST_LOCATION_TABLE))
        self.assertNotIn(KARItemName.CHECKBOX_FILLER_ARCHIPELAGO, self.world_item_names())


class TestArchipelagoEnabled(KARTestBase):
    """Every AP box exists as a real location and the victory event is placed. The boxes live in the
    regions of the modes they describe, so the Archipelago region itself holds only the victory."""

    options = AP_WITH_CT

    def test_region_and_boxes_present(self):
        region_names = {region.name for region in self.multiworld.get_regions(self.player)}
        self.assertIn(KARRegion.ARCHIPELAGO, region_names)
        self.assertTrue(set(AP_CHECKLIST_LOCATION_TABLE) <= self.real_location_names())
        self.assertIn(KARItemName.ARCHIPELAGO_VICTORY, self.placed_event_items())

    def test_boxes_accept_another_mode_checklist_reward(self):
        # create_items is mode-agnostic and AP boxes are ordinary fill targets. Asserted through
        # can_fill rather than by sampling a seed- and order-dependent fill. Boxes in an unselected
        # category are EXCLUDED, so a useful reward is barred from them by design.
        categorised = self.world.archipelago_excluded_locations
        reward_name = next(
            name for name, data in ITEM_TABLE.items() if data.type in CHECKLIST_REWARD_TYPES and data.code is not None
        )
        item = self.world.create_item(reward_name)
        state = self.multiworld.get_all_state()
        for name in AP_CHECKLIST_LOCATION_TABLE:
            with self.subTest(location=name):
                can_fill = self.world.get_location(name).can_fill(state, item, check_access=False)
                self.assertEqual(can_fill, name not in categorised)

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestArchipelagoHighEffortProgression(KARTestBase):
    """Selected, the high-effort boxes are DEFAULT and take a useful reward like any other box."""

    options = {**AP_WITH_CT, "archipelago_progression": [ProgressionCategory.HIGH_EFFORT]}

    def test_high_effort_boxes_accept_a_useful_reward(self):
        reward_name = next(
            name for name, data in ITEM_TABLE.items() if data.type in CHECKLIST_REWARD_TYPES and data.code is not None
        )
        item = self.world.create_item(reward_name)
        state = self.multiworld.get_all_state()
        for name in location_name_groups[KARLocationGroup.AP_HIGH_EFFORT]:
            with self.subTest(location=name):
                self.assertTrue(self.world.get_location(name).can_fill(state, item, check_access=False))


class TestArchipelagoFillerInPool(KARTestBase):
    options = {**AP_WITH_CT, "archipelago_checkbox_fillers": 2}

    def test_filler_count(self):
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_ARCHIPELAGO), 2)


class TestArchipelagoPullsModesIntoLogic(KARTestBase):
    """An AP box inherits the entrance chain of the region it sits in, so enabling the checklist builds
    the trees of every mode its boxes name. Such a mode stays free: no goal means no unlock items, which
    is what makes those trees reachable and what the upstream reachability test requires."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 5,
    }

    def test_only_the_modes_with_boxes_are_pulled_in(self):
        self.assertIn(GameMode.CITYTRIAL, self.world.logic_modes)
        self.assertIn(GameMode.AIRRIDE, self.world.logic_modes)
        # No AP box names a Top Ride region, so logic_modes is not simply "everything".
        self.assertNotIn(GameMode.TOPRIDE, self.world.logic_modes)

    def test_goalless_mode_trees_exist_without_their_own_boxes(self):
        region_names = {r.name for r in self.multiworld.get_regions(self.player)}
        self.assertIn(KARRegion.CITY_TRIAL_STADIUM_KM2, region_names)
        self.assertIn(KARRegion.AIR_RIDE_MAGMA_FLOWS, region_names)
        self.assertFalse(self.real_location_names() & set(CITY_TRIAL_LOCATION_TABLE))

    def test_goalless_modes_hold_no_keys_and_ship_free(self):
        slot_data = self.world.fill_slot_data()
        for option in ("city_trial_stadiums_gated", "city_trial_events_gated", "air_ride_courses_gated"):
            with self.subTest(gate=option):
                self.assertNotIn(option, self.world.effective_gates)
                self.assertEqual(slot_data[option], 0)

    def test_every_region_and_box_is_reachable(self):
        state = self.multiworld.get_all_state()
        unreachable = [
            r.name for r in self.multiworld.get_regions(self.player) if not state.can_reach_region(r.name, self.player)
        ]
        self.assertEqual(unreachable, [])
        self.assertEqual([name for name in AP_CHECKLIST_LOCATION_TABLE if not self.reaches(state, name)], [])


class TestArchipelagoOnlyDefaultGates(KARTestBase):
    """AP-only at default gate settings. Colors are mode-agnostic, so this seed genuinely holds 7 color
    keys (8 minus the starter) needing default boxes to land on - which pins the AP box count and would
    fail if the table shrank far enough to stop absorbing them."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 5,
    }

    def test_colors_are_effective_and_present(self):
        self.assertIn("colors_gated", self.world.effective_gates)
        self.assertEqual(self.world.fill_slot_data()["colors_gated"], 1)

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestArchipelagoOnlyEveryGateOff(KARTestBase):
    """The AP checklist standing completely alone: every item-injecting gate off so the guaranteed pool
    fits the small AP-only world, and AP Patches held out because they are City Trial locations that
    would exist here whatever the City Trial goal is."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "ap_patches": 0,
        "colors_gated": False,
        "machines_gated": False,
        "abilities_gated": False,
        "city_trial_events_gated": False,
        "city_trial_patches_gated": False,
        "city_trial_items_gated": False,
        "city_trial_boxes_gated": False,
        "air_ride_courses_gated": False,
        "top_ride_courses_gated": False,
        "top_ride_items_gated": False,
        "city_trial_stadiums_gated": False,
        "checklist_rewards": [],
    }

    def test_only_ap_locations(self):
        self.assertEqual(self.real_location_names(), set(AP_CHECKLIST_LOCATION_TABLE))

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)
