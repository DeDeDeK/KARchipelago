"""
AP Patch tests.

The patches are their own location category: a flat block of numbered City Trial locations, sized by
`ap_patches` and switched between default and excluded by `ap_patch_placement`. They carry no
checklist cell, so they never decode through the mode/clear_kind codec, and they are pure extra
capacity for the item pool - no goal reads them.
"""

from BaseClasses import CollectionState
from Options import Toggle

from ..KARData import (
    AP_PATCH_CODE_BASE,
    AP_PATCH_CODE_MAX,
    AP_PATCH_GROUP_MAX,
    AP_PATCH_GROUP_SIZE,
    AP_PATCH_MOD_MAX,
    AP_PATCH_WORDS,
    ap_patch_group_sizes,
    location_code_to_mode_clear,
)
from ..KARItems import AP_PATCH_GROUP_EVENT_ITEMS
from ..KARLocations import (
    AP_PATCH_LOCATION_TABLE,
    LOCATION_TABLE,
    KARLocationGroup,
    ap_patch_location_name,
    location_name_groups,
)
from ..KAROptions import APPatches, APPatchPlacement, ArchipelagoGoal, CityTrialGoal
from ..KARRegions import AP_PATCH_GROUP_REGIONS, KARRegion
from . import CT_ONLY, KARTestBase


class TestAPPatchTable(KARTestBase):
    options = CT_ONLY

    def test_codes_are_contiguous_from_the_block_base(self):
        for n in (1, 2, AP_PATCH_CODE_MAX):
            self.assertEqual(AP_PATCH_LOCATION_TABLE[ap_patch_location_name(n)].code, AP_PATCH_CODE_BASE + n - 1)

    def test_names_are_zero_padded_to_three_digits(self):
        self.assertEqual(ap_patch_location_name(1), "City Trial: AP Patch #001")
        self.assertEqual(ap_patch_location_name(20), "City Trial: AP Patch #020")
        self.assertEqual(ap_patch_location_name(512), "City Trial: AP Patch #512")

    def test_every_patch_is_city_trial_content(self):
        """The static table names the chain's root; a seed restamps each entry into its group region."""
        for name, data in AP_PATCH_LOCATION_TABLE.items():
            with self.subTest(location=name):
                self.assertEqual(data.region, KARRegion.CITY_TRIAL)
                self.assertIsNone(data.native_reward)

    def test_patch_codes_are_not_checkboxes(self):
        """The AP checklist band stops where this block starts, so a patch never decodes to a cell."""
        for n in (1, 2, AP_PATCH_CODE_MAX):
            self.assertIsNone(location_code_to_mode_clear(AP_PATCH_CODE_BASE + n - 1))

    def test_location_group_covers_the_whole_block(self):
        self.assertEqual(location_name_groups[KARLocationGroup.CT_AP_PATCHES], set(AP_PATCH_LOCATION_TABLE))

    def test_the_block_is_exactly_the_max_wide(self):
        codes = [data.code for data in AP_PATCH_LOCATION_TABLE.values()]
        self.assertEqual(codes, list(range(AP_PATCH_CODE_BASE, AP_PATCH_CODE_BASE + AP_PATCH_CODE_MAX)))

    def test_no_other_location_lands_in_the_patch_band(self):
        band = range(AP_PATCH_CODE_BASE, AP_PATCH_CODE_BASE + AP_PATCH_CODE_MAX)
        for name, data in LOCATION_TABLE.items():
            if name not in AP_PATCH_LOCATION_TABLE:
                with self.subTest(location=name):
                    self.assertNotIn(data.code, band)

    def test_the_block_is_exactly_the_option_ceiling(self):
        """No published name is one that no seed could ever create."""
        self.assertEqual(len(AP_PATCH_LOCATION_TABLE), APPatches.range_end)
        for name, value in APPatches.special_range_names.items():
            with self.subTest(special=name):
                self.assertLessEqual(value, APPatches.range_end)

    def test_the_wire_mask_covers_the_whole_mod_side_range(self):
        """The mod's masks are AP_PATCH_MOD_MAX bits whatever a seed uses, so the client reads that many."""
        self.assertEqual(AP_PATCH_WORDS * 64, AP_PATCH_MOD_MAX)
        self.assertLessEqual(AP_PATCH_CODE_MAX, AP_PATCH_MOD_MAX)


class TestAPPatchesOff(KARTestBase):
    # RNG boxes count as progression here: with no AP patch locations, City Trial's remaining default
    # boxes are one short of its guaranteed pool.
    options = {**CT_ONLY, "ap_patches": 0, "city_trial_progression_rng": Toggle.option_true}

    def test_no_patch_locations_exist(self):
        self.assertFalse(self.real_location_names() & set(AP_PATCH_LOCATION_TABLE))


class TestAPPatchesCreatesThatMany(KARTestBase):
    options = {**CT_ONLY, "ap_patches": 20}

    def test_only_the_first_n_are_created(self):
        created = self.real_location_names() & set(AP_PATCH_LOCATION_TABLE)
        self.assertEqual(created, {ap_patch_location_name(n) for n in range(1, 21)})

    def test_they_are_default_progress_type(self):
        for loc in self.multiworld.get_locations(self.player):
            if loc.name in AP_PATCH_LOCATION_TABLE:
                with self.subTest(location=loc.name):
                    self.assertNotIn(loc.name, self.world.ap_patch_excluded_locations)

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestAPPatchWordBoundaryCounts(KARTestBase):
    """The mod tracks patches in u64 words, so the counts either side of one are worth pinning."""

    options = CT_ONLY
    auto_construct = False

    def test_exactly_the_first_n_are_created(self):
        for count in (1, 63, 64, 65, APPatches.range_end):
            with self.subTest(ap_patches=count):
                self.options = {**CT_ONLY, "ap_patches": count}
                self.world_setup()
                created = self.real_location_names() & set(AP_PATCH_LOCATION_TABLE)
                self.assertEqual(created, {ap_patch_location_name(n) for n in range(1, count + 1)})
                codes = [data.code for name, data in AP_PATCH_LOCATION_TABLE.items() if name in created]
                self.assertEqual(codes, list(range(AP_PATCH_CODE_BASE, AP_PATCH_CODE_BASE + count)))


class TestAPPatchExcludedPlacement(KARTestBase):
    # Excluding all 20 leaves the same shortfall as having none, so RNG boxes count as progression.
    options = {
        **CT_ONLY,
        "ap_patches": 20,
        "ap_patch_placement": APPatchPlacement.option_excluded,
        "city_trial_progression_rng": Toggle.option_true,
    }

    def test_all_of_them_are_excluded(self):
        self.assertEqual(self.world.ap_patch_excluded_locations, set(self.world.ap_patch_locations))
        self.assertEqual(self.world.ap_patch_default_locations, set())


class TestAPPatchesWithoutACityTrialGoal(KARTestBase):
    """They are City Trial content, so their region's tree has to exist even with no City Trial goal."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
        "archipelago_checklist_amount": 3,
        "ap_patches": 10,
    }

    def test_locations_exist(self):
        created = self.real_location_names() & set(AP_PATCH_LOCATION_TABLE)
        self.assertEqual(len(created), 10)


class TestAPPatchSlotData(KARTestBase):
    options = {**CT_ONLY, "ap_patches": 30}

    def test_ships_the_patch_count(self):
        self.assertEqual(self.world.fill_slot_data()["ap_patches"], 30)


class TestAPPatchGroupSizes(KARTestBase):
    """The split is by group size, not group count, so the sphere a group represents is the same amount
    of play whatever `ap_patches` is."""

    options = CT_ONLY
    auto_construct = False

    def test_sizes_sum_to_the_count_and_fit_the_declared_width(self):
        for count in range(AP_PATCH_CODE_MAX + 1):
            with self.subTest(ap_patches=count):
                sizes = ap_patch_group_sizes(count)
                self.assertEqual(sum(sizes), count)
                self.assertLessEqual(len(sizes), AP_PATCH_GROUP_MAX)
                self.assertTrue(all(size > 0 for size in sizes))

    def test_a_short_count_is_one_group(self):
        """Under one and a half groups' worth stays a single sphere - splitting it buys nothing."""
        for count in (1, AP_PATCH_GROUP_SIZE, AP_PATCH_GROUP_SIZE + AP_PATCH_GROUP_SIZE // 2 - 1):
            with self.subTest(ap_patches=count):
                self.assertEqual(ap_patch_group_sizes(count), [count])

    def test_no_group_is_shorter_than_half(self):
        for count in range(1, AP_PATCH_CODE_MAX + 1):
            with self.subTest(ap_patches=count):
                sizes = ap_patch_group_sizes(count)
                if len(sizes) > 1:
                    self.assertGreaterEqual(min(sizes) * 2, AP_PATCH_GROUP_SIZE)

    def test_the_widest_seed_uses_every_declared_region(self):
        self.assertEqual(len(ap_patch_group_sizes(AP_PATCH_CODE_MAX)), len(AP_PATCH_GROUP_REGIONS))


class TestAPPatchChain(KARTestBase):
    """A full-width block: ten groups, each entered from the one before it through an event."""

    options = {**CT_ONLY, "ap_patches": AP_PATCH_CODE_MAX}

    def group_regions(self) -> list[str]:
        return list(AP_PATCH_GROUP_REGIONS[: self.world.ap_patch_group_count])

    def test_one_region_per_group_and_no_more(self):
        self.assertEqual(self.world.ap_patch_group_count, AP_PATCH_GROUP_MAX)
        built = {region.name for region in self.multiworld.get_regions(self.player)}
        self.assertTrue(set(self.group_regions()) <= built)

    def test_patches_land_in_their_group_in_index_order(self):
        expected: dict[str, str] = {}
        number = 1
        for group_index, size in enumerate(ap_patch_group_sizes(AP_PATCH_CODE_MAX)):
            for _ in range(size):
                expected[ap_patch_location_name(number)] = AP_PATCH_GROUP_REGIONS[group_index]
                number += 1
        for loc in self.multiworld.get_locations(self.player):
            if loc.name in expected:
                with self.subTest(location=loc.name):
                    self.assertEqual(loc.parent_region.name, expected[loc.name])

    def test_every_group_but_the_last_carries_its_event(self):
        """The last group opens nothing, so it has no event - N groups means N-1 of them."""
        placed = self.placed_event_items() & set(AP_PATCH_GROUP_EVENT_ITEMS)
        self.assertEqual(placed, set(AP_PATCH_GROUP_EVENT_ITEMS[: self.world.ap_patch_group_count - 1]))

    def test_each_group_is_entered_only_from_the_one_before_it(self):
        regions = self.group_regions()
        first = self.multiworld.get_region(regions[0], self.player)
        self.assertEqual([entrance.parent_region.name for entrance in first.entrances], [KARRegion.CITY_TRIAL])
        for index in range(1, len(regions)):
            with self.subTest(group=index + 1):
                entrances = self.multiworld.get_region(regions[index], self.player).entrances
                self.assertEqual([entrance.parent_region.name for entrance in entrances], [regions[index - 1]])
                state = CollectionState(self.multiworld)
                self.assertFalse(entrances[0].access_rule(state))
                state.collect(self.world.create_item(AP_PATCH_GROUP_EVENT_ITEMS[index - 1]), True)
                self.assertTrue(entrances[0].access_rule(state))

    def test_the_groups_land_in_ascending_spheres(self):
        """The whole point: a flat block is one sphere, which is what hides a late key from fill and from
        progression balancing. Each group has to be a step of its own instead."""
        first_sphere: dict[str, int] = {}
        for index, sphere in enumerate(self.multiworld.get_spheres()):
            for loc in sphere:
                if loc.player == self.player and loc.item is not None:
                    first_sphere.setdefault(loc.item.name, index)
        seen = [first_sphere[item] for item in AP_PATCH_GROUP_EVENT_ITEMS[: self.world.ap_patch_group_count - 1]]
        self.assertEqual(seen, sorted(seen))
        self.assertEqual(len(set(seen)), len(seen))

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestAPPatchSingleGroup(KARTestBase):
    """A count that fits one group gets one region and no events - the chain costs nothing there."""

    options = {**CT_ONLY, "ap_patches": AP_PATCH_GROUP_SIZE}

    def test_one_group(self):
        self.assertEqual(self.world.ap_patch_group_count, 1)

    def test_no_group_events_exist(self):
        self.assertFalse(self.placed_event_items() & set(AP_PATCH_GROUP_EVENT_ITEMS))

    def test_every_patch_is_in_the_first_group(self):
        for loc in self.multiworld.get_locations(self.player):
            if loc.name in AP_PATCH_LOCATION_TABLE:
                with self.subTest(location=loc.name):
                    self.assertEqual(loc.parent_region.name, AP_PATCH_GROUP_REGIONS[0])
