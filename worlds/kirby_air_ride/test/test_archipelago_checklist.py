"""Tests for the Archipelago checklist - the synthetic 4th checklist mode (an early stub of
Archipelago-specific objectives). Covers mode enable/disable, the checkbox-filler item, the stub
location table + codec, goal wiring, and the option-validation branches specific to the AP mode."""

import unittest

from Options import OptionError

from ..KARData import (
    CLIENT_BACKFILL_PER_MODE,
    SENT_CHECKS_PER_MODE,
    GameMode,
    location_code_to_mode_clear,
    mode_clear_to_location_code,
)
from ..KARItems import ITEM_TABLE, KARItemName, KARItemType
from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
    APLocation,
    CTLocation,
)
from ..KAROptions import ArchipelagoChecklistAmount, ArchipelagoGoal, CityTrialGoal
from ..KARRegions import REGION_TO_MODE, KARRegion
from . import CT_ONLY, KARTestBase

CHECKLIST_REWARD_TYPES = {
    KARItemType.CT_CHECKLIST_REWARD,
    KARItemType.AR_CHECKLIST_REWARD,
    KARItemType.TR_CHECKLIST_REWARD,
}

# City Trial (default goal) plus a small Archipelago n_checklist goal.
AP_WITH_CT: dict = {
    "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
    "archipelago_checklist_amount": 3,
}


class TestArchipelagoCodec(unittest.TestCase):
    """The AP location band (361-480) round-trips through the mode/clear_kind codec, and the stub
    table's codes match 361 + clear_kind in ap_checks[] order."""

    def test_band_roundtrip(self):
        for clear_kind in range(120):
            code = mode_clear_to_location_code(GameMode.ARCHIPELAGO, clear_kind)
            self.assertEqual(code, 361 + clear_kind)
            self.assertEqual(location_code_to_mode_clear(code), (GameMode.ARCHIPELAGO, clear_kind))

    def test_stub_location_codes(self):
        self.assertEqual(AP_CHECKLIST_LOCATION_TABLE[APLocation.BOOT_THE_GAME].code, 361)
        self.assertEqual(AP_CHECKLIST_LOCATION_TABLE[APLocation.RECEIVE_AN_ITEM].code, 362)
        self.assertEqual(AP_CHECKLIST_LOCATION_TABLE[APLocation.RECEIVE_5_ITEMS].code, 363)

    def test_boundaries(self):
        self.assertEqual(location_code_to_mode_clear(360), (GameMode.TOPRIDE, 119))  # last Top Ride code
        self.assertEqual(location_code_to_mode_clear(361), (GameMode.ARCHIPELAGO, 0))
        self.assertEqual(location_code_to_mode_clear(480), (GameMode.ARCHIPELAGO, 119))
        self.assertIsNone(location_code_to_mode_clear(481))


class TestArchipelagoRewardWireEncoding(unittest.TestCase):
    """An Archipelago box addresses itself as target_mode=ARCHIPELAGO on the wire.

    The client writes locations[source_mode][reward_index] = (target_mode << 8) | clear_kind, so a
    reward shuffled onto an AP box reaches the mod as target_mode=ARCHIPELAGO - a value the mod's
    cross_mode_slots table must have a row for."""

    def test_ap_box_wire_encoding(self):
        for data in AP_CHECKLIST_LOCATION_TABLE.values():
            mapping = location_code_to_mode_clear(data.code)
            assert mapping is not None
            mode, clear_kind = mapping
            self.assertEqual(mode, GameMode.ARCHIPELAGO)
            self.assertEqual(((mode << 8) | clear_kind) >> 8, int(GameMode.ARCHIPELAGO))


class TestArchipelagoAcceptsChecklistRewards(KARTestBase):
    """Archipelago boxes are eligible to host other modes' checklist rewards when the rewards are
    shuffled. The AP checklist awards no *native* rewards, but create_items is mode-agnostic and AP
    boxes are ordinary fill targets, so rewards can land there. Asserts eligibility directly rather
    than sampling fill outcomes, which would depend on seed and pool ordering."""

    options = {**AP_WITH_CT, "shuffle_checklist_rewards": True}

    def test_ap_boxes_accept_a_checklist_reward(self):
        reward_name = next(
            name for name, data in ITEM_TABLE.items() if data.type in CHECKLIST_REWARD_TYPES and data.code is not None
        )
        item = self.world.create_item(reward_name)
        state = self.multiworld.get_all_state(False)
        for name in AP_CHECKLIST_LOCATION_TABLE:
            with self.subTest(location=name):
                location = self.world.get_location(name)
                self.assertTrue(
                    location.can_fill(state, item, check_access=False),
                    f"{name} rejects checklist reward {reward_name}",
                )


class TestArchipelagoMemoryMaps(unittest.TestCase):
    """Every per-mode memory map covers the Archipelago mode. These are dicts the client iterates, so
    a missing entry is silent: _handle_backfill builds server_bits for every GameMode but only writes
    the modes present in CLIENT_BACKFILL_PER_MODE, so an AP omission drops AP backfill on the floor
    with no error."""

    def test_sent_checks_covers_every_mode(self):
        self.assertEqual(set(SENT_CHECKS_PER_MODE), set(GameMode))

    def test_backfill_covers_every_mode(self):
        self.assertEqual(set(CLIENT_BACKFILL_PER_MODE), set(GameMode))

    def test_backfill_and_sent_checks_agree(self):
        # _handle_backfill diffs one against the other per mode; divergent keys would KeyError or skip.
        self.assertEqual(set(CLIENT_BACKFILL_PER_MODE), set(SENT_CHECKS_PER_MODE))

    def test_no_overlapping_bitmask_slots(self):
        # Each u64[2] slot is 16 bytes; two modes sharing a base would cross-contaminate.
        addrs = [int(a) for a in (*SENT_CHECKS_PER_MODE.values(), *CLIENT_BACKFILL_PER_MODE.values())]
        self.assertEqual(len(addrs), len(set(addrs)))
        for a in addrs:
            for b in addrs:
                if a != b:
                    self.assertGreaterEqual(abs(a - b), 16, f"slots at {a:#x} and {b:#x} overlap")


class TestArchipelagoDisabledByDefault(KARTestBase):
    """The AP checklist defaults to none: its region and locations are absent from the world and its
    checkbox filler is never minted, even though the tab still appears in-game."""

    options = CT_ONLY

    def test_no_ap_region(self):
        region_names = {region.name for region in self.multiworld.get_regions(self.player)}
        self.assertNotIn(KARRegion.ARCHIPELAGO, region_names)

    def test_no_ap_locations(self):
        real = self.real_location_names()
        for name in AP_CHECKLIST_LOCATION_TABLE:
            self.assertNotIn(name, real)

    def test_no_ap_filler_in_pool(self):
        self.assertNotIn(KARItemName.CHECKBOX_FILLER_ARCHIPELAGO, self.world_item_names())


class TestArchipelagoEnabledLocations(KARTestBase):
    """With the AP mode enabled, every AP location exists as a real (address-bearing) location and the
    victory event is placed. Boxes live in the region of the mode they describe, so only the
    mode-agnostic ones are in the Archipelago region itself."""

    options = AP_WITH_CT

    def test_ap_region_present(self):
        region_names = {region.name for region in self.multiworld.get_regions(self.player)}
        self.assertIn(KARRegion.ARCHIPELAGO, region_names)

    def test_ap_locations_present(self):
        real = self.real_location_names()
        for name in AP_CHECKLIST_LOCATION_TABLE:
            self.assertIn(name, real)

    def test_victory_event_placed(self):
        self.assertIn(KARItemName.ARCHIPELAGO_VICTORY, self.placed_event_items())


class TestArchipelagoBeatable(KARTestBase):
    """With CT + AP goals, collecting everything but the victory events makes both victories
    reachable."""

    options = AP_WITH_CT

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestArchipelagoFillerInPool(KARTestBase):
    """The Archipelago checkbox filler is minted at the requested quantity when the AP mode is
    enabled and the count is nonzero."""

    options = {**AP_WITH_CT, "archipelago_checkbox_fillers": 2}

    def test_filler_count(self):
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_ARCHIPELAGO), 2)


class TestArchipelagoChecklistListGoal(KARTestBase):
    """A checklist_list AP goal binds its victory to the listed AP location."""

    options = {
        **CT_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_checklist_list,
        "archipelago_goal_locations": [APLocation.RECEIVE_AN_ITEM],
    }

    def test_victory_event_placed(self):
        self.assertIn(KARItemName.ARCHIPELAGO_VICTORY, self.placed_event_items())


class TestArchipelago100BlocksRejected(KARTestBase):
    """The AP checklist is still incomplete and holds well under 100 boxes, so a 100_checklist_blocks
    goal is unsatisfiable and is rejected at generation. This is the only AP block goal that can be:
    every in-range n_checklist_blocks target fits by construction (see
    TestArchipelagoChecklistAmountRangeTracksTable)."""

    options = {**CT_ONLY, "archipelago_goal": ArchipelagoGoal.option_100_checklist_blocks}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestArchipelagoChecklistAmountRangeTracksTable(unittest.TestCase):
    """ArchipelagoChecklistAmount must never offer more boxes than the AP table actually holds.

    City Trial / Air Ride / Top Ride each have a full 120 boxes, so their range_end is 120. The
    Archipelago checklist is still being built out, so its range is capped at the real table size -
    otherwise the option surface promises targets that can only fail at generation. Raise range_end as
    boxes are added; this test is what keeps the two in step.
    """

    def test_range_end_matches_table_size(self):
        self.assertEqual(ArchipelagoChecklistAmount.range_end, len(AP_CHECKLIST_LOCATION_TABLE))

    def test_default_within_range(self):
        self.assertGreaterEqual(ArchipelagoChecklistAmount.default, ArchipelagoChecklistAmount.range_start)
        self.assertLessEqual(ArchipelagoChecklistAmount.default, ArchipelagoChecklistAmount.range_end)


class TestArchipelagoFillerExceedsGoalAmount(KARTestBase):
    """Checkbox fillers must be fewer than the n_checklist target, like every other mode."""

    options = {
        **CT_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 2,
        "archipelago_checkbox_fillers": 2,
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestArchipelagoChecklistListEmptyRejected(KARTestBase):
    """A checklist_list AP goal with no listed locations is rejected."""

    options = {**CT_ONLY, "archipelago_goal": ArchipelagoGoal.option_checklist_list}
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestArchipelagoChecklistListWrongModeRejected(KARTestBase):
    """A checklist_list AP goal listing a non-AP location is rejected."""

    options = {
        **CT_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_checklist_list,
        "archipelago_goal_locations": [CTLocation.RACE_60_MILES],
    }
    auto_construct = False

    def test_raises_option_error(self):
        with self.assertRaises(OptionError):
            self.world_setup()


class TestArchipelagoOnly(KARTestBase):
    """The AP checklist can stand alone as the only enabled mode. Item-injecting gates are turned off
    so the guaranteed pool fits the tiny 3-location world (analogous to a tightly-scoped single-mode
    seed); the world still generates and is beatable."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
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
        "checklist_rewards_gated": False,
    }

    def test_only_ap_locations(self):
        real = self.real_location_names()
        self.assertEqual(real, set(AP_CHECKLIST_LOCATION_TABLE))

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestArchipelagoLocationTableIntegrity(unittest.TestCase):
    """Static invariants of the AP location table.

    The code<->clear_kind pairing is a cross-repo wire contract with the mod's ap_checks[] array, and
    nothing mechanically catches a desync, so it is pinned here.
    """

    def test_codes_contiguous_from_361(self):
        codes = sorted(d.code for d in AP_CHECKLIST_LOCATION_TABLE.values())
        expected = list(range(361, 361 + len(AP_CHECKLIST_LOCATION_TABLE)))
        self.assertEqual(codes, expected, "AP codes must be contiguous from 361 (code == 361 + clear_kind)")

    def test_codes_within_ap_band(self):
        for name, data in AP_CHECKLIST_LOCATION_TABLE.items():
            with self.subTest(location=name):
                self.assertEqual(location_code_to_mode_clear(data.code), (GameMode.ARCHIPELAGO, data.code - 361))

    def test_no_native_rewards(self):
        """The AP checklist awards no native rewards; it only hosts other modes' shuffled ones."""
        for name, data in AP_CHECKLIST_LOCATION_TABLE.items():
            with self.subTest(location=name):
                self.assertIsNone(data.native_reward)

    def test_names_do_not_collide_with_other_tables(self):
        """LOCATION_TABLE merges the four mode tables by name, so a collision would silently drop one of
        the two boxes. The "Archipelago: " prefix is what keeps them apart - this is the guard."""
        others = set(CITY_TRIAL_LOCATION_TABLE) | set(AIR_RIDE_LOCATION_TABLE) | set(TOP_RIDE_LOCATION_TABLE)
        collisions = sorted(set(AP_CHECKLIST_LOCATION_TABLE) & others)
        self.assertEqual(collisions, [], f"AP location names collide with another mode's table: {collisions}")
        self.assertEqual(
            len(LOCATION_TABLE),
            len(others) + len(AP_CHECKLIST_LOCATION_TABLE),
            "merged LOCATION_TABLE lost entries, indicating a name collision",
        )

    def test_every_ap_region_is_classified(self):
        """An AP box's region decides which mode it pulls into logic, via REGION_TO_MODE."""
        for name, data in AP_CHECKLIST_LOCATION_TABLE.items():
            with self.subTest(location=name):
                self.assertIn(data.region, REGION_TO_MODE)


class TestRegionToModeExhaustive(unittest.TestCase):
    """Every region is classified. _build_region_to_mode raises at import for an unclassified region, so
    this mostly documents the contract - and catches a region classified into the wrong mode."""

    def test_every_region_present(self):
        for region in KARRegion:
            with self.subTest(region=region.name):
                self.assertIn(region.value, REGION_TO_MODE)

    def test_spot_check_classifications(self):
        self.assertEqual(REGION_TO_MODE[KARRegion.STADIUM_KM2], GameMode.CITYTRIAL)
        self.assertEqual(REGION_TO_MODE[KARRegion.CT_FREE_RUN], GameMode.CITYTRIAL)
        self.assertEqual(REGION_TO_MODE[KARRegion.AR_MAGMA_FLOWS], GameMode.AIRRIDE)
        self.assertEqual(REGION_TO_MODE[KARRegion.TR_TA_GRASS], GameMode.TOPRIDE)
        self.assertEqual(REGION_TO_MODE[KARRegion.ARCHIPELAGO], GameMode.ARCHIPELAGO)


class TestArchipelagoPullsModesIntoLogic(KARTestBase):
    """Enabling the AP checklist builds the trees of every mode its boxes name, even with no goal there.

    An AP box lives in the region of the activity it describes, so it inherits that region's entrance
    chain. That requires the tree to exist. A mode pulled in this way stays free: no goal means no
    unlock items, so none of its categories are effective and it ships ungated.
    """

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 5,
    }

    def test_goalless_modes_pulled_into_logic(self):
        self.assertIn(GameMode.CITYTRIAL, self.world.logic_modes)
        self.assertIn(GameMode.AIRRIDE, self.world.logic_modes)

    def test_mode_without_ap_boxes_not_pulled_in(self):
        """No AP box names a Top Ride region, so Top Ride stays out - logic_modes is not "everything"."""
        self.assertNotIn(GameMode.TOPRIDE, self.world.logic_modes)

    def test_goalless_mode_trees_are_built(self):
        region_names = {r.name for r in self.multiworld.get_regions(self.player)}
        self.assertIn(KARRegion.STADIUM_KM2, region_names)
        self.assertIn(KARRegion.AR_MAGMA_FLOWS, region_names)

    def test_goalless_mode_assigns_no_own_locations(self):
        """In logic is not the same as having a goal: City Trial's own boxes are still absent."""
        real = self.real_location_names()
        self.assertFalse(real & set(CITY_TRIAL_LOCATION_TABLE))

    def test_goalless_mode_holds_no_keys_and_ships_free(self):
        slot_data = self.world.fill_slot_data()
        for option in ("city_trial_stadiums_gated", "city_trial_events_gated", "air_ride_courses_gated"):
            with self.subTest(gate=option):
                self.assertNotIn(option, self.world.effective_gates)
                self.assertEqual(slot_data[option], 0)

    def test_all_regions_reachable(self):
        """A goal-less tree is reachable precisely BECAUSE its unlock items are absent: no keys means no
        effective gate, means set_rules hangs it off Menu ungated. The upstream reachability test
        requires this."""
        state = self.multiworld.get_all_state(False)
        unreachable = [
            r.name for r in self.multiworld.get_regions(self.player) if not state.can_reach_region(r.name, self.player)
        ]
        self.assertEqual(unreachable, [])

    def test_all_ap_boxes_reachable(self):
        state = self.multiworld.get_all_state(False)
        unreachable = [
            name
            for name in AP_CHECKLIST_LOCATION_TABLE
            if not self.multiworld.get_location(name, self.player).can_reach(state)
        ]
        self.assertEqual(unreachable, [])


class TestArchipelagoOnlyDefaultGates(KARTestBase):
    """AP-only generates at default gate settings.

    It could not before the table grew: colors are mode-agnostic, so an AP-only seed genuinely holds 7
    color keys (8 minus the starter) and they need default boxes. Against 3 stub boxes that raised
    OptionError, and AP-only was only generatable with colors_gated off. The boxes, not the gate logic,
    are what fixed this - so this test guards the box count, and would fail again if the table shrank.
    """

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
