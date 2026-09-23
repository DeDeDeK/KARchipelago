"""Goal wiring: every enabled mode contributes one victory event and the completion rule ANDs them.
Some goal kinds replace a real box with a `<box> (Victory)` event, some synthesize one in the mode's
root region. The event names are a contract with the mod, which resynthesizes them."""

from typing import Any, NamedTuple

from Options import Toggle

from ..KARItems import AP_STAR_PIECE_UNLOCK_ITEMS, LEGENDARY_PIECE_UNLOCK_ITEMS, KARItemName, KARItemType
from ..KARLocations import (
    AIR_RIDE_GOAL_TO_LOCATION,
    ARCHIPELAGO_GOAL_TO_LOCATION,
    CITY_TRIAL_GOAL_TO_LOCATION,
    CITY_TRIAL_PROGRESSION_GROUPS,
    TOP_RIDE_GOAL_TO_LOCATION,
    APLocation,
    ARLocation,
    CTLocation,
    TRLocation,
)
from ..KAROptions import AirRideGoal, ArchipelagoGoal, CityTrialGoal, TopRideGoal
from ..KARRegions import KARRegion
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, items_of_type

_MAX_STATS_EVENT = f"{KARRegion.CITY_TRIAL}: Max Stats"


class _Mode(NamedTuple):
    """Everything a mode's goal wiring is driven by; `prefix` also names its four *_goal* options."""

    label: str
    prefix: str
    preset: dict
    goal_option: Any
    goal_to_box: dict
    root_region: str
    victory: str
    sample_boxes: list


# The Archipelago row rides on top of City Trial, which keeps its own default goal.
_MODES = [
    _Mode(
        "ct",
        "city_trial",
        CT_ONLY,
        CityTrialGoal,
        CITY_TRIAL_GOAL_TO_LOCATION,
        KARRegion.CITY_TRIAL,
        KARItemName.CITY_TRIAL_VICTORY,
        [CTLocation.DESTROY_ALL_HOUSES, CTLocation.BUST_STAR_POLE],
    ),
    _Mode(
        "ar",
        "air_ride",
        AR_ONLY,
        AirRideGoal,
        AIR_RIDE_GOAL_TO_LOCATION,
        KARRegion.AIR_RIDE,
        KARItemName.AIR_RIDE_VICTORY,
        [ARLocation.RACE_100_LAPS, ARLocation.DEFEAT_300_OF_YOUR_ENEMIES],
    ),
    _Mode(
        "tr",
        "top_ride",
        TR_ONLY,
        TopRideGoal,
        TOP_RIDE_GOAL_TO_LOCATION,
        KARRegion.TOP_RIDE,
        KARItemName.TOP_RIDE_VICTORY,
        [TRLocation.CROSS_GOAL_20, TRLocation.FR_RACE_100_LAPS],
    ),
    _Mode(
        "ap",
        "archipelago",
        CT_ONLY,
        ArchipelagoGoal,
        ARCHIPELAGO_GOAL_TO_LOCATION,
        KARRegion.ARCHIPELAGO,
        KARItemName.ARCHIPELAGO_VICTORY,
        [APLocation.BREAK_ALL_CORAL, APLocation.GET_10_HP_PATCHES],
    ),
]


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


def _make_box_replacing_goal_test(mode: _Mode, goal_value: int) -> type:
    class _BoxReplaced(KARTestBase):
        options = {**mode.preset, f"{mode.prefix}_goal": goal_value}

        def test_box_leaves_the_table_for_a_victory_event(self):
            goal_box = mode.goal_to_box[goal_value]
            self.assertNotIn(goal_box, self.real_location_names())
            self.assertIn(f"{goal_box} (Victory)", self.event_location_names())
            self.assertIn(mode.victory, self.placed_event_items())

    return _BoxReplaced


def _make_n_blocks_goal_test(mode: _Mode) -> type:
    class _NBlocks(KARTestBase):
        options = {
            **mode.preset,
            f"{mode.prefix}_goal": mode.goal_option.option_n_checklist_blocks,
            f"{mode.prefix}_checklist_amount": 30,
            f"{mode.prefix}_checkbox_fillers": 0,
        }

        def test_synthetic_event_named_for_the_count(self):
            self.assertIn(f"{mode.root_region}: Complete 30 Checklist Blocks", self.event_location_names())
            self.assertIn(mode.victory, self.placed_event_items())

    return _NBlocks


def _make_checklist_list_goal_test(mode: _Mode) -> type:
    class _ChecklistList(KARTestBase):
        options = {
            **mode.preset,
            f"{mode.prefix}_goal": mode.goal_option.option_checklist_list,
            f"{mode.prefix}_goal_locations": mode.sample_boxes,
        }

        def test_goal_boxes_stay_real(self):
            # checklist_list keeps them as locations - they back the victory event's rule.
            real = self.real_location_names()
            for loc in mode.sample_boxes:
                self.assertIn(loc, real)
            self.assertIn(mode.victory, self.placed_event_items())

    return _ChecklistList


for _mode in _MODES:
    # The Archipelago checklist is well under 100 boxes wide, so it offers no 100-blocks goal.
    if hasattr(_mode.goal_option, "option_100_checklist_blocks"):
        _register(
            _make_box_replacing_goal_test(_mode, _mode.goal_option.option_100_checklist_blocks),
            f"TestGoal100Blocks_{_mode.label}",
        )
    _register(_make_n_blocks_goal_test(_mode), f"TestGoalNBlocks_{_mode.label}")
    _register(_make_checklist_list_goal_test(_mode), f"TestGoalChecklistList_{_mode.label}")


# The remaining box-replacing goal kinds, each carrying its box's requirement onto the victory event.
_BY_LABEL = {mode.label: mode for mode in _MODES}
for _label, _goal_value in (
    ("ct", CityTrialGoal.option_hydra_and_dragoon),
    ("ct", CityTrialGoal.option_beat_king_dedede),
    ("ap", ArchipelagoGoal.option_assemble_archipelago_star),
    ("ap", ArchipelagoGoal.option_all_three_legendaries_in_one_run),
):
    _mode = _BY_LABEL[_label]
    _register(
        _make_box_replacing_goal_test(_mode, _goal_value),
        f"TestGoalBoxReplaced_{_label}_{_mode.goal_option(_goal_value).current_key}",
    )


class TestNBlocksGoalRangeBounds(KARTestBase):
    """Both ends of city_trial_checklist_amount generate: 1 block, and the full 120-cell grid."""

    options = {**CT_ONLY, "city_trial_goal": CityTrialGoal.option_n_checklist_blocks, "city_trial_checkbox_fillers": 0}
    auto_construct = False

    def test_event_created_at_each_bound(self):
        for amount in (1, 120):
            with self.subTest(city_trial_checklist_amount=amount):
                self.options = {**self.options, "city_trial_checklist_amount": amount}
                self.world_setup()
                self.assertIn(
                    f"{KARRegion.CITY_TRIAL}: Complete {amount} Checklist Blocks", self.event_location_names()
                )
                self.assertIn(KARItemName.CITY_TRIAL_VICTORY, self.placed_event_items())


class TestArchipelagoStarGoalNeedsEverySphere(KARTestBase):
    """The six Archipelago sphere unlocks stay in the pool even with City Trial items ungated, and all
    six gate the victory. The machine unlock is not part of it - assembling the star mounts it."""

    options = {**CT_ONLY, "archipelago_goal": ArchipelagoGoal.option_assemble_archipelago_star}

    def test_spheres_are_in_the_pool(self):
        self.assertTrue(set(AP_STAR_PIECE_UNLOCK_ITEMS) <= self.world_item_names())

    def test_victory_needs_every_sphere(self):
        self.assert_victory_needs_all(AP_STAR_PIECE_UNLOCK_ITEMS, KARItemName.ARCHIPELAGO_VICTORY)


class TestAllThreeLegendariesGoalNeedsTwelvePieces(KARTestBase):
    """all_three_legendaries_in_one_run needs both vanilla sets plus all six spheres."""

    options = {**CT_ONLY, "archipelago_goal": ArchipelagoGoal.option_all_three_legendaries_in_one_run}

    def test_victory_needs_all_twelve_pieces(self):
        self.assert_victory_needs_all(
            [*LEGENDARY_PIECE_UNLOCK_ITEMS, *AP_STAR_PIECE_UNLOCK_ITEMS], KARItemName.ARCHIPELAGO_VICTORY
        )


class TestCTGoalMaxStats(KARTestBase):
    """max_stats_in_one_run binds to no checklist box, so its victory event is synthesized in the City
    Trial region. With patches and items both ungated the only clause left is "hold every Patch Cap
    Increase" - and every copy is needed, since the cap has to reach the target at all."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
        "city_trial_patch_cap_min": 14,
        "city_trial_patch_cap_max": 18,
        # The pool is dominated by patch-cap items; turn off broad gating so it fits.
        "city_trial_events_gated": Toggle.option_false,
        "abilities_gated": Toggle.option_false,
        "city_trial_patches_gated": Toggle.option_false,
        "city_trial_boxes_gated": Toggle.option_false,
        "colors_gated": Toggle.option_false,
        "city_trial_stadiums_gated": Toggle.option_false,
    }

    def test_synthetic_event_needs_every_patch_cap_increase(self):
        self.assertIn(_MAX_STATS_EVENT, self.event_location_names())
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
    """Patches AND items both gated: maxing all nine stats needs either every patch type able to spawn or
    the All Up item, so the rule ORs those two routes onto the cap clause. Either gate being off hands one
    route over for free, which is why the clause is only emitted when both are on."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_max_stats_in_one_run,
        "city_trial_patch_cap_min": 17,
        "city_trial_patch_cap_max": 18,
        "city_trial_patches_gated": Toggle.option_true,
        "city_trial_items_gated": Toggle.option_true,
        # Every CT category selected to make room for the 36 item unlocks the item gate adds.
        "city_trial_progression": sorted(CITY_TRIAL_PROGRESSION_GROUPS),
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


class TestAllModesVictoryRequiresAll(KARTestBase):
    """Three enabled modes means three victory events, and the completion rule needs all three."""

    options = ALL_MODES
    _VICTORIES = (
        KARItemName.CITY_TRIAL_VICTORY,
        KARItemName.AIR_RIDE_VICTORY,
        KARItemName.TOP_RIDE_VICTORY,
    )

    def test_completion_needs_every_victory(self):
        # Hand-built states rather than collected items: a sweep would re-derive any victory event whose
        # location is already reachable, so an "all but one" state is not otherwise constructible.
        self.assertTrue(set(self._VICTORIES) <= self.placed_event_items())
        rule = self.multiworld.completion_condition[self.player]
        for withheld in self._VICTORIES:
            with self.subTest(withheld=withheld):
                state = self.state_with(*(v for v in self._VICTORIES if v != withheld))
                self.assertFalse(rule(state), f"completion satisfied without {withheld}")
                state.collect(self.world.create_item(withheld), prevent_sweep=True)
                self.assertTrue(rule(state), "completion not satisfied with all three victories")


class TestSingleModeCompletionIgnoresOtherModes(KARTestBase):
    """The flip side: a one-mode seed's completion rule names only that mode's victory."""

    options = CT_ONLY

    def test_city_trial_victory_alone_completes(self):
        state = self.state_with(KARItemName.CITY_TRIAL_VICTORY)
        self.assertTrue(self.multiworld.completion_condition[self.player](state))
