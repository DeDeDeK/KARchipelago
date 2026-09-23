"""Universal Tracker rebuilds this slot's logic graph by re-running generation from an empty YAML, so
everything that shapes the graph has to survive the trip through slot_data and come back out in
generate_early - otherwise UT silently reports the wrong locations as in logic."""

import inspect
import json
from collections.abc import Iterator
from contextlib import contextmanager

from BaseClasses import CollectionState, LocationProgressType, MultiWorld
from Options import OptionError, PerGameCommonOptions
from test.general import gen_steps, setup_multiworld

from worlds.AutoWorld import call_all

from .. import UT_OPTIONS_KEY, UT_PASSTHROUGH_OPTIONS, KARWorld
from ..KARData import GameMode
from ..KARItems import MODE_VICTORY_EVENTS, KARItemName
from ..KARLocations import ProgressionCategory
from ..KAROptions import AirRideGoal, ArchipelagoGoal, CityTrialGoal, KAROptions, TopRideGoal
from . import ALL_MODES, CT_ONLY, KARTestBase

# A deliberately un-default seed: every mode on with a different goal shape, gates flipped away from
# their defaults, and the progression sub-flags on so the EXCLUDED split moves too. Regenerating this
# from slot_data alone is the whole contract, so it differs from the defaults on every axis.
DISTINCTIVE_OPTIONS: dict = {
    "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon,
    "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
    "air_ride_checklist_amount": 23,
    "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
    "top_ride_checklist_amount": 17,
    "archipelago_goal": ArchipelagoGoal.option_none,
    "city_trial_stadiums_gated": False,
    "city_trial_events_gated": False,
    "abilities_gated": False,
    "base_abilities_gated": True,
    "city_trial_patches_gated": False,
    "city_trial_items_gated": True,
    "machines_gated": True,
    "city_trial_boxes_gated": False,
    "air_ride_courses_gated": False,
    "colors_gated": False,
    "top_ride_courses_gated": False,
    "top_ride_items_gated": False,
    "city_trial_patch_cap_min": 7,
    "city_trial_patch_cap_max": 24,
    "city_trial_progression": [ProgressionCategory.HIGH_EFFORT, ProgressionCategory.RNG_EVENTS],
    "air_ride_progression": [ProgressionCategory.TIME_ATTACK],
    "top_ride_progression": [ProgressionCategory.MULTIPLAYER],
    "non_progression_checkboxes": "removed",
}


@contextmanager
def attached_passthrough(multiworld: MultiWorld, passthrough: dict) -> Iterator[None]:
    """Attach a `re_gen_passthrough` for the block, then take it off again. UT injects the attribute onto
    the MultiWorld it generates; core never declares it, which is why the suppression lives here."""
    multiworld.re_gen_passthrough = passthrough  # ty: ignore[unresolved-attribute]
    try:
        yield
    finally:
        del multiworld.re_gen_passthrough  # ty: ignore[unresolved-attribute]


def graph_snapshot(multiworld: MultiWorld, player: int = 1) -> dict[str, list[str]]:
    """Everything about a generated slot that UT's logic answers depend on.

    Deliberately excludes the item pool: the random starter is precollected rather than pooled, so two
    generations of the same options hold different pools - and UT never reads the pool anyway.
    """
    locations = list(multiworld.get_locations(player))
    entrances = [
        f"{e.parent_region.name if e.parent_region else None} -> "
        f"{e.connected_region.name if e.connected_region else None}"
        for e in multiworld.get_entrances(player)
    ]
    return {
        "locations": sorted(str(loc.name) for loc in locations if loc.address is not None),
        "events": sorted(str(loc.name) for loc in locations if loc.address is None),
        "excluded": sorted(str(loc.name) for loc in locations if loc.progress_type == LocationProgressType.EXCLUDED),
        "regions": sorted(str(region.name) for region in multiworld.get_regions(player)),
        "entrances": sorted(entrances),
    }


def generate_with_passthrough(slot_data: dict) -> MultiWorld:
    """Generate the way UT does: default options everywhere, with the recorded slot_data supplied through
    `re_gen_passthrough`. The steps run by hand because the passthrough has to be attached before
    generate_early reads its first option."""
    multiworld = setup_multiworld(KARWorld, steps=())
    with attached_passthrough(multiworld, {KARWorld.game: slot_data}):
        for step in gen_steps:
            call_all(multiworld, step)
    return multiworld


class TestPassthroughContract(KARTestBase):
    """The recorded option set covers everything that shapes generation, and UT finds the hook it needs
    as a staticmethod - a plain method would still work, but would cost every player a full throwaway
    generation on client start."""

    options = CT_ONLY

    def test_every_kar_option_is_recorded(self):
        kar_specific = set(KAROptions.type_hints) - set(PerGameCommonOptions.type_hints)
        self.assertLessEqual(kar_specific, set(UT_PASSTHROUGH_OPTIONS))
        # Generic, but it decides which boxes come out EXCLUDED, which is how UT groups them in the tab.
        self.assertIn("exclude_locations", UT_PASSTHROUGH_OPTIONS)

    def test_every_recorded_name_is_a_real_option(self):
        for name in UT_PASSTHROUGH_OPTIONS:
            with self.subTest(option=name):
                self.assertIn(name, KAROptions.type_hints)

    def test_interpret_slot_data_is_a_staticmethod_that_echoes(self):
        # Returning non-None is what tells UT to regenerate rather than track its launch-time world.
        self.assertTrue(KARWorld.ut_can_gen_without_yaml)
        self.assertIsInstance(inspect.getattr_static(KARWorld, "interpret_slot_data"), staticmethod)
        slot_data = dict(self.world.fill_slot_data())
        self.assertEqual(KARWorld.interpret_slot_data(slot_data), slot_data)


class TestRegenerationReproducesTheSeed(KARTestBase):
    """The contract itself: a generation driven only by a recorded slot_data must land on the same graph
    as the generation that produced it, starting from defaults that share none of its option values."""

    options = DISTINCTIVE_OPTIONS

    def test_every_recorded_value_survives_the_wire(self):
        # JSON over the network, then `from_any` back into an Option - exactly what
        # _apply_ut_passthrough does. A value that cannot round-trip would restore as something else
        # without ever raising.
        record = json.loads(json.dumps(self.world.fill_slot_data()[UT_OPTIONS_KEY]))
        self.assertEqual(set(record), set(UT_PASSTHROUGH_OPTIONS))
        for name, value in record.items():
            with self.subTest(option=name):
                option = getattr(self.world.options, name)
                self.assertEqual(type(option).from_any(value).value, option.value)

    def test_options_are_restored(self):
        regenerated = generate_with_passthrough(dict(self.world.fill_slot_data())).worlds[1]
        for name in UT_PASSTHROUGH_OPTIONS:
            with self.subTest(option=name):
                self.assertEqual(getattr(regenerated.options, name).value, getattr(self.world.options, name).value)

    def test_graph_is_reproduced(self):
        actual = graph_snapshot(generate_with_passthrough(dict(self.world.fill_slot_data())), 1)
        expected = graph_snapshot(self.multiworld, self.player)
        for key in expected:
            with self.subTest(part=key):
                self.assertEqual(actual[key], expected[key])

    def test_derived_generation_state_is_reproduced(self):
        # effective_gates and logic_modes are computed from the options rather than read from them, so
        # they are the check that the restore happened early enough to matter.
        regenerated = generate_with_passthrough(dict(self.world.fill_slot_data())).worlds[1]
        self.assertEqual(regenerated.effective_gates, self.world.effective_gates)
        self.assertEqual(regenerated.logic_modes, self.world.logic_modes)
        self.assertEqual(regenerated.goal_forced_unlocks, self.world.goal_forced_unlocks)


class TestPassthroughGuards(KARTestBase):
    options = ALL_MODES

    def test_absent_passthrough_is_a_noop(self):
        # Real generation never sets the attribute; pinned so the guard is not quietly inverted.
        self.assertFalse(hasattr(self.multiworld, "re_gen_passthrough"))
        self.world._apply_ut_passthrough()

    def test_another_games_passthrough_is_ignored(self):
        before = self.world.options.colors_gated.value
        with attached_passthrough(self.multiworld, {"Some Other Game": {UT_OPTIONS_KEY: {"colors_gated": 1}}}):
            self.world._apply_ut_passthrough()
        self.assertEqual(self.world.options.colors_gated.value, before)

    def test_missing_option_record_raises(self):
        # A seed rolled before this apworld recorded its options. Tracking it would report default-option
        # logic as if it were the truth, so generation has to fail instead.
        with (
            attached_passthrough(self.multiworld, {KARWorld.game: {"city_trial_goal": 0}}),
            self.assertRaises(OptionError),
        ):
            self.world._apply_ut_passthrough()


class TestGoModeRule(KARTestBase):
    """ANDing every victory answers "is the whole seed finishable from here", which reads No until the
    last mode comes into logic - and block goals go reachable long before they are done. The passthrough
    build swaps in the question a tracker wants: is some goal still outstanding and in logic."""

    options = ALL_MODES
    _VICTORIES = (
        KARItemName.CITY_TRIAL_VICTORY,
        KARItemName.AIR_RIDE_VICTORY,
        KARItemName.TOP_RIDE_VICTORY,
    )

    def setUp(self) -> None:
        super().setUp()
        self.tracked = generate_with_passthrough(dict(self.world.fill_slot_data()))
        self.tracked_world = self.tracked.worlds[1]

    def _go_mode(self, reachable: tuple, completed: set | None) -> bool:
        """`reachable` stands in for the victories UT's sweep would collect, `completed` for what
        KARClient reports the game has actually finished."""
        self.tracked_world.ut_goals_completed = completed
        state = CollectionState(self.tracked)
        for victory in reachable:
            state.collect(self.tracked_world.create_item(victory), prevent_sweep=True)
        return self.tracked.has_beaten_game(state, 1)

    def test_real_generation_keeps_the_and(self):
        # Only UT's build swaps the rule; the one fill runs against still needs every victory.
        state = self.state_with(KARItemName.CITY_TRIAL_VICTORY)
        self.assertFalse(self.multiworld.has_beaten_game(state, self.player))

    def test_victory_event_names_match_the_mapping(self):
        # The client maps goal_satisfied_mask bits through MODE_VICTORY_EVENTS. A name that drifted from
        # what determine_goal mints would match no goal, and the finished goal would keep counting.
        rows = (GameMode.CITYTRIAL, GameMode.AIRRIDE, GameMode.TOPRIDE)
        self.assertEqual({MODE_VICTORY_EVENTS[row] for row in rows}, set(self._VICTORIES))

    def test_an_open_goal_in_logic_is_go_mode(self):
        self.assertTrue(self._go_mode((KARItemName.CITY_TRIAL_VICTORY,), set()))
        self.assertFalse(self._go_mode((), set()))

    def test_a_finished_goal_stops_counting(self):
        # Reachability never regresses, so without the client's report the label would latch to Yes the
        # moment any goal came into logic and stay there for the rest of the seed.
        self.assertFalse(self._go_mode((KARItemName.CITY_TRIAL_VICTORY,), {KARItemName.CITY_TRIAL_VICTORY}))
        self.assertTrue(
            self._go_mode(
                (KARItemName.CITY_TRIAL_VICTORY, KARItemName.AIR_RIDE_VICTORY),
                {KARItemName.CITY_TRIAL_VICTORY},
            )
        )

    def test_every_goal_finished_reads_as_beaten(self):
        self.assertTrue(self._go_mode((), set(self._VICTORIES)))

    def test_no_client_reporting_falls_back_to_any_reachable(self):
        # Stock UT tracking the slot: nothing stamps the set, and the label still has to say something.
        self.assertTrue(self._go_mode((KARItemName.AIR_RIDE_VICTORY,), None))
        self.assertFalse(self._go_mode((), None))
