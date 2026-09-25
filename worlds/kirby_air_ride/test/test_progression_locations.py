"""The per-mode progression options decide which categories of checklist box count toward progression:
a category left out is EXCLUDED by default, or removed from the world when `non_progression_checkboxes` says
so. All three directions are pinned, so each key is shown wired to its own group. run_default_tests is
off for the static ones: a fill would be wasted on state that generate_early already settled."""

from BaseClasses import Item, ItemClassification, LocationProgressType

from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AIR_RIDE_PROGRESSION_GROUPS,
    AP_CHECKLIST_LOCATION_TABLE,
    ARCHIPELAGO_PROGRESSION_GROUPS,
    CITY_TRIAL_LOCATION_TABLE,
    CITY_TRIAL_PROGRESSION_GROUPS,
    TOP_RIDE_LOCATION_TABLE,
    TOP_RIDE_PROGRESSION_GROUPS,
    CTLocation,
    KARLocationGroup,
    ProgressionCategory,
    location_name_groups,
)
from ..KARRegions import REMOVED_CHECKBOX_SUFFIX
from . import AP_ONLY, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, names

_REMOVED: dict = {"non_progression_checkboxes": "removed"}

# (label, preset, attribute prefix, location table, category key -> group).
_MODES: list[tuple[str, dict, str, dict, dict[str, str]]] = [
    ("city_trial", CT_ONLY, "city_trial", CITY_TRIAL_LOCATION_TABLE, CITY_TRIAL_PROGRESSION_GROUPS),
    ("air_ride", AR_ONLY, "air_ride", AIR_RIDE_LOCATION_TABLE, AIR_RIDE_PROGRESSION_GROUPS),
    ("top_ride", TR_ONLY, "top_ride", TOP_RIDE_LOCATION_TABLE, TOP_RIDE_PROGRESSION_GROUPS),
    ("archipelago", AP_ONLY, "archipelago", AP_CHECKLIST_LOCATION_TABLE, ARCHIPELAGO_PROGRESSION_GROUPS),
]


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


def _region_name(location) -> str | None:
    """`parent_region` is optional, but never unset on anything a generated world holds."""
    return location.parent_region.name if location.parent_region else None


def _split(world, prefix: str) -> tuple[set[str], set[str], set[str]]:
    return (
        getattr(world, f"{prefix}_default_locations"),
        getattr(world, f"{prefix}_excluded_locations"),
        getattr(world, f"{prefix}_removed_locations"),
    )


def _all_category_locations(category_groups: dict[str, str]) -> set[str]:
    return set().union(*(location_name_groups[group] for group in category_groups.values()))


def _make_default_off_test(preset, prefix, table, category_groups) -> type:
    # Pinned empty rather than left at the option's default, which is not empty for every mode.
    class _DefaultOff(KARTestBase):
        options = {**preset, f"{prefix}_progression": []}
        run_default_tests = False

        def test_empty_set_excludes_every_category(self):
            default, excluded, removed = _split(self.world, prefix)
            self.assertEqual(default | excluded, names(table), "default/excluded must partition the table")
            self.assertEqual(default & excluded, set(), "a location cannot be both default and excluded")
            self.assertEqual(removed, set(), "nothing is removed unless non_progression_checkboxes asks for it")
            self.assertEqual(
                excluded,
                _all_category_locations(category_groups),
                "an empty set must exclude exactly the union of the mode's categories",
            )

    return _DefaultOff


def _make_key_isolation_test(preset, prefix, table, category_groups, key) -> type:
    option = f"{prefix}_progression"
    group = category_groups[key]

    class _KeySelected(KARTestBase):
        options = {**preset, option: [key]}
        run_default_tests = False

        def test_only_this_category_becomes_default(self):
            default, excluded, _removed = _split(self.world, prefix)
            others: set[str] = set().union(
                *(location_name_groups[g] for k, g in category_groups.items() if k != key), set()
            )
            self.assertEqual(excluded, others, f"{key!r} alone should leave only the other categories excluded")
            self.assertEqual(default, names(table) - others)
            # The locations unique to this category must have moved; this also guards against a vacuous
            # test, where a group is fully shadowed by its siblings.
            unique = location_name_groups[group] - others
            self.assertTrue(unique, f"{key!r} has no locations of its own; its effect is unobservable")
            self.assertTrue(unique <= default, f"{key!r} should make its own-category locations default")

    return _KeySelected


def _make_removal_test(preset, prefix, table, category_groups) -> type:
    class _Removed(KARTestBase):
        options = {**preset, f"{prefix}_progression": [], **_REMOVED}
        run_default_tests = False

        def test_unselected_categories_are_removed(self):
            default, excluded, removed = _split(self.world, prefix)
            # This mode's goal cell is protected: it is an event either way, never a removed box.
            protected = self.world.goal_locations_to_exclude & names(table)
            self.assertEqual(removed, _all_category_locations(category_groups) - protected)
            self.assertEqual(default | excluded | removed, names(table), "the three sets must partition the table")
            self.assertEqual(excluded, protected, "only protected boxes stay excluded when removal is on")

        def test_removed_boxes_are_events_not_locations(self):
            _default, _excluded, removed = _split(self.world, prefix)
            for name in removed:
                with self.subTest(location=name):
                    self.assertRaises(KeyError, self.multiworld.get_location, name, self.player)
                    stand_in = self.multiworld.get_location(name + REMOVED_CHECKBOX_SUFFIX, self.player)
                    self.assertIsNone(stand_in.address, "a stand-in must not be a real check")
                    self.assertTrue(stand_in.locked, "a stand-in must not accept a placement")
                    self.assertEqual(self.world.checkbox_location_name(name), stand_in.name)

    return _Removed


for _label, _preset, _prefix, _table, _groups in _MODES:
    _register(
        _make_default_off_test(_preset, _prefix, _table, _groups),
        f"TestProgressionEmpty_{_label}",
    )
    _register(
        _make_removal_test(_preset, _prefix, _table, _groups),
        f"TestProgressionRemoved_{_label}",
    )
    for _key in _groups:
        _register(
            _make_key_isolation_test(_preset, _prefix, _table, _groups, _key),
            f"TestProgressionSelected_{_prefix}_{_key.replace(':', '').replace(' ', '_').lower()}",
        )


class TestOverlappingCategoriesNeedBoth(KARTestBase):
    """A box in two categories is progression only when both are selected. The 2-hour Free Run box is
    both City Trial Free Run and High Effort."""

    options = {**CT_ONLY, "city_trial_progression": [ProgressionCategory.FREE_RUN]}
    run_default_tests = False

    def test_free_run_alone_leaves_the_high_effort_overlap_excluded(self):
        default, excluded, _removed = _split(self.world, "city_trial")
        overlap = (
            location_name_groups[KARLocationGroup.CT_FREE_RUN] & location_name_groups[KARLocationGroup.CT_HIGH_EFFORT]
        )
        self.assertTrue(overlap, "CT Free Run and High Effort no longer overlap; this test is vacuous")
        self.assertTrue(overlap <= excluded, "a box needs every one of its categories selected")
        # The rest of Free Run did move, so the option is not simply inert.
        self.assertTrue(location_name_groups[KARLocationGroup.CT_FREE_RUN] - overlap <= default)


class TestOverlappingCategoriesBothSelected(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_progression": [ProgressionCategory.FREE_RUN, ProgressionCategory.HIGH_EFFORT],
    }
    run_default_tests = False

    def test_both_selected_makes_the_overlap_default(self):
        default, _excluded, _removed = _split(self.world, "city_trial")
        overlap = (
            location_name_groups[KARLocationGroup.CT_FREE_RUN] & location_name_groups[KARLocationGroup.CT_HIGH_EFFORT]
        )
        self.assertTrue(overlap <= default | self.world.goal_locations_to_exclude)


class TestRemovedBoxesKeepTheirRules(KARTestBase):
    """A stand-in carries the box's own access rule, so removing a box cannot quietly hand its block
    credit out for free. City Trial's Free Run boxes sit behind the Free Run region either way."""

    options = {**CT_ONLY, **_REMOVED}
    run_default_tests = False

    def test_stand_in_sits_in_the_boxs_region(self):
        for name in location_name_groups[KARLocationGroup.CT_FREE_RUN]:
            if name not in self.world.city_trial_removed_locations:
                continue
            with self.subTest(location=name):
                stand_in = self.multiworld.get_location(name + REMOVED_CHECKBOX_SUFFIX, self.player)
                self.assertEqual(_region_name(stand_in), CITY_TRIAL_LOCATION_TABLE[name].region)


class TestRemovedBoxesLeaveTheItemPool(KARTestBase):
    """Removal shrinks the placeable-location count, so the pool shrinks with it: create_items fills the
    locations that are left and mints nothing for a box that no longer exists."""

    options = {**CT_ONLY, **_REMOVED}

    def test_pool_matches_the_locations_that_remain(self):
        placeable = [loc for loc in self.multiworld.get_locations(self.player) if not loc.locked]
        self.assertEqual(len(self.itempool_items()), len(placeable))

    def test_removed_boxes_are_absent_from_the_multiworld(self):
        placed = {loc.name for loc in self.multiworld.get_locations(self.player)}
        self.assertFalse(placed & self.world.city_trial_removed_locations)


class TestRemovedStillReachesTheBlockGoal(KARTestBase):
    """City Trial's default goal wants 100 blocks but removal leaves only 77 real ones, so it is
    reachable at all only because the stand-ins count toward it."""

    options = {**CT_ONLY, **_REMOVED}

    def test_goal_is_reachable_with_everything_collected(self):
        self.assertLess(len(self.world.city_trial_default_locations), 100, "removal no longer bites here")
        self.assertTrue(self.multiworld.can_beat_game(self.multiworld.get_all_state(False)))


class TestChecklistListGoalBoxesSurviveRemoval(KARTestBase):
    """A checklist_list goal has to hold one of the player's own items, so its cells stay real locations
    even when their category is unselected. Both of these are High Effort."""

    _GOAL_BOXES = [CTLocation.BREAK_1000_BOXES, CTLocation.PICKUP_3000_ITEMS]
    options = {
        **CT_ONLY,
        **_REMOVED,
        "city_trial_goal": "checklist_list",
        "city_trial_goal_locations": _GOAL_BOXES,
    }

    def test_goal_boxes_stay_real_and_excluded(self):
        for name in self._GOAL_BOXES:
            with self.subTest(location=name):
                self.assertNotIn(name, self.world.city_trial_removed_locations)
                self.assertIn(name, self.world.city_trial_excluded_locations)
                location = self.multiworld.get_location(name, self.player)
                self.assertIsNotNone(location.address)
                self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)

    def test_goal_boxes_still_take_the_local_item_rule(self):
        foreign = Item("Not Ours", ItemClassification.filler, None, self.player + 1)
        for name in self._GOAL_BOXES:
            with self.subTest(location=name):
                self.assertFalse(self.multiworld.get_location(name, self.player).item_rule(foreign))


class TestArchipelagoExcludedIsBudgeted(KARTestBase):
    """An AP-enabled seed absorbs the cross-mode color keys, so the boxes an unselected category excludes
    have to stay placeable: _compute_capacity counts them toward the excluded budget, never the default
    one. Anything that grows the AP categories shrinks that default budget."""

    # Pinned empty: the option's default selects the Copy Chance Wheel, which would leave that group default.
    options = {**AP_ONLY, "archipelago_progression": []}
    run_default_tests = False

    def test_excluded_locations_still_exist(self):
        excluded = self.world.archipelago_excluded_locations
        self.assertEqual(excluded, _all_category_locations(ARCHIPELAGO_PROGRESSION_GROUPS))
        for name in excluded:
            self.assertIsNotNone(self.multiworld.get_location(name, self.player))
