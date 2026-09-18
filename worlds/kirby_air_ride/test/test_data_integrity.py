"""Static-data integrity: ITEM_TABLE, the location tables, the derived lookup maps and the code codecs.
Generation reads all of these without re-validating, so a mistake surfaces as a silent behaviour change
rather than an error."""

import re
import unittest
from itertools import pairwise

from BaseClasses import ItemClassification

from ..KARData import (
    CLIENT_BACKFILL_PER_MODE,
    CODE_BAND_PER_MODE,
    REWARD_CODE_BASE,
    REWARD_CODE_STRIDE,
    REWARDS_PER_MODE,
    SENT_CHECKS_PER_MODE,
    GameMode,
    GoalKind,
    location_code_to_mode_clear,
    mode_clear_to_location_code,
    reward_code_to_mode_index,
)
from ..KARItems import (
    AR_COURSE_UNLOCK_ITEMS,
    AR_CT_MACHINE_UNLOCK_ITEMS,
    CHECKLIST_REWARD_CATEGORIES,
    CHECKLIST_REWARD_CATEGORY_TYPES,
    CHECKLIST_REWARD_TYPE_ITEMS,
    CHECKLIST_REWARD_TYPE_MODES,
    CHECKLIST_REWARD_TYPES,
    COLOR_UNLOCK_ITEMS,
    GATING_CATEGORIES,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    TR_COURSE_UNLOCK_ITEMS,
    TR_MACHINE_UNLOCK_ITEMS,
    TRAP_CATEGORIES,
)
from ..KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    AP_PATCH_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_TABLE,
    NATIVE_REWARD_TO_LOCATION,
    TOP_RIDE_LOCATION_TABLE,
)
from ..KAROptions import (
    AirRideGoal,
    ArchipelagoGoal,
    CityTrialGoal,
    StartingAirRideCourse,
    StartingKirbyColor,
    StartingMachine,
    StartingStadium,
    StartingTopRideCourse,
    StartingTopRideMachine,
    TopRideGoal,
)
from ..KARRegions import REGION_TO_MODE, KARRegion

# (table, mode, first code, last code) for the three modes that fill a whole 120-wide band.
_MODE_BANDS = [
    (CITY_TRIAL_LOCATION_TABLE, GameMode.CITYTRIAL, 1, 120),
    (AIR_RIDE_LOCATION_TABLE, GameMode.AIRRIDE, 121, 240),
    (TOP_RIDE_LOCATION_TABLE, GameMode.TOPRIDE, 241, 360),
]


def _duplicate_codes(tables) -> list[tuple[int, str, str]]:
    seen: dict[int, str] = {}
    duplicates: list[tuple[int, str, str]] = []
    for table in tables:
        for name, data in table.items():
            if data.code is None:
                continue
            if data.code in seen:
                duplicates.append((data.code, seen[data.code], str(name)))
            else:
                seen[data.code] = str(name)
    return duplicates


class TestCodesAreUnique(unittest.TestCase):
    """The client decodes a bare code back to an item or a mode/clear_kind, so one code means one thing."""

    def test_item_codes_unique(self):
        self.assertEqual(_duplicate_codes([ITEM_TABLE]), [])

    def test_location_codes_unique_across_every_table(self):
        self.assertEqual(
            _duplicate_codes(
                [*(band[0] for band in _MODE_BANDS), AP_CHECKLIST_LOCATION_TABLE, AP_PATCH_LOCATION_TABLE]
            ),
            [],
        )


class TestLocationCodeBands(unittest.TestCase):
    """Each real mode fills its 120-wide band exactly: a gap would mean a removed location left a dead
    code, and every code has to decode back to its own mode."""

    def test_each_mode_fills_its_band(self):
        for table, mode, lo, hi in _MODE_BANDS:
            with self.subTest(mode=mode.name):
                self.assertEqual(len(table), 120)
                codes = sorted(d.code for d in table.values() if d.code is not None)
                self.assertEqual(codes, list(range(lo, hi + 1)))

    def test_codes_decode_to_their_own_mode(self):
        for table, mode, lo, _ in _MODE_BANDS:
            for name, data in table.items():
                with self.subTest(mode=mode.name, location=name):
                    self.assertEqual(location_code_to_mode_clear(data.code), (mode, data.code - lo))


class TestCheckboxCodecBands(unittest.TestCase):
    """The two checkbox codecs must be exact inverses over every band. _check_locations feeds
    mode_clear_to_location_code bits 0-127 of a two-word mask while no band is wider than 120, so an
    unbounded encode would report a neighbouring mode's location for a bit the game never sets."""

    def test_every_mode_has_a_band(self):
        self.assertEqual(set(CODE_BAND_PER_MODE), set(GameMode))

    def test_bands_do_not_overlap(self):
        codes = [c for base, width in CODE_BAND_PER_MODE.values() for c in range(base, base + width)]
        self.assertEqual(len(codes), len(set(codes)), "Two modes claim the same location code")

    def test_in_band_clear_kinds_round_trip(self):
        for mode, (base, width) in CODE_BAND_PER_MODE.items():
            for clear_kind in range(width):
                with self.subTest(mode=mode.name, clear_kind=clear_kind):
                    code = mode_clear_to_location_code(mode, clear_kind)
                    self.assertEqual(code, base + clear_kind)
                    self.assertEqual(location_code_to_mode_clear(code), (mode, clear_kind))

    def test_out_of_band_clear_kinds_encode_to_zero(self):
        for mode, (_, width) in CODE_BAND_PER_MODE.items():
            for clear_kind in (-1, width, width + 1, 127):
                with self.subTest(mode=mode.name, clear_kind=clear_kind):
                    self.assertEqual(mode_clear_to_location_code(mode, clear_kind), 0)


class TestRewardCodeDecoding(unittest.TestCase):
    """reward_code_to_mode_index is the only filter on scouted reward items before they are written into
    the mod's locations[3][REWARDS_PER_MODE] array, so the padding codes per band must decode to None."""

    def test_band_edges_decode(self):
        for index in range(3):
            mode = GameMode(index)
            base = REWARD_CODE_BASE + index * REWARD_CODE_STRIDE
            with self.subTest(mode=mode.name):
                self.assertEqual(reward_code_to_mode_index(base), (mode, 0))
                last = REWARDS_PER_MODE - 1
                self.assertEqual(reward_code_to_mode_index(base + last), (mode, last))

    def test_padding_above_the_array_decodes_to_none(self):
        for index in range(3):
            base = REWARD_CODE_BASE + index * REWARD_CODE_STRIDE
            for offset in range(REWARDS_PER_MODE, REWARD_CODE_STRIDE):
                with self.subTest(mode=GameMode(index).name, offset=offset):
                    self.assertIsNone(reward_code_to_mode_index(base + offset))

    def test_codes_outside_the_block_decode_to_none(self):
        self.assertIsNone(reward_code_to_mode_index(None))
        self.assertIsNone(reward_code_to_mode_index(REWARD_CODE_BASE - 1))
        self.assertIsNone(reward_code_to_mode_index(REWARD_CODE_BASE + 3 * REWARD_CODE_STRIDE))


class TestPerModeMemoryMaps(unittest.TestCase):
    """The client iterates these dicts, so a missing mode is silent: _handle_backfill builds server_bits
    for every GameMode but writes only the modes present in CLIENT_BACKFILL_PER_MODE."""

    def test_both_maps_cover_every_mode(self):
        self.assertEqual(set(SENT_CHECKS_PER_MODE), set(GameMode))
        self.assertEqual(set(CLIENT_BACKFILL_PER_MODE), set(GameMode))

    def test_no_overlapping_bitmask_slots(self):
        # Each u64[2] slot is 16 bytes; two modes sharing a base would cross-contaminate.
        addrs = sorted(int(a) for a in (*SENT_CHECKS_PER_MODE.values(), *CLIENT_BACKFILL_PER_MODE.values()))
        self.assertEqual(len(addrs), len(set(addrs)))
        for lower, upper in pairwise(addrs):
            self.assertGreaterEqual(upper - lower, 16, f"slots at {lower:#x} and {upper:#x} overlap")


class TestRegionToMode(unittest.TestCase):
    """_build_region_to_mode raises at import for an unclassified region, so what is left to catch here
    is a region classified into the wrong mode."""

    def test_every_region_present(self):
        self.assertEqual(set(REGION_TO_MODE), {region.value for region in KARRegion})

    def test_spot_check_classifications(self):
        self.assertEqual(REGION_TO_MODE[KARRegion.CITY_TRIAL_STADIUM_KM2], GameMode.CITYTRIAL)
        self.assertEqual(REGION_TO_MODE[KARRegion.CITY_TRIAL_FREE_RUN], GameMode.CITYTRIAL)
        self.assertEqual(REGION_TO_MODE[KARRegion.AIR_RIDE_MAGMA_FLOWS], GameMode.AIRRIDE)
        self.assertEqual(REGION_TO_MODE[KARRegion.TOP_RIDE_TA_GRASS], GameMode.TOPRIDE)
        self.assertEqual(REGION_TO_MODE[KARRegion.ARCHIPELAGO], GameMode.ARCHIPELAGO)


class TestGoalOptionValues(unittest.TestCase):
    """The four *_goal options are one enum: the client writes the raw value into APSlotOptions.goal[row]
    and the mod switches on it as APGoalKind, so a name means the same number in every option."""

    # Must stay in step with APGoalKind in the mod's mods/archipelago/src/main.h.
    GOAL_KIND = {
        "100_checklist_blocks": GoalKind.CHECKLIST_100,
        "n_checklist_blocks": GoalKind.N_CHECKLIST,
        "checklist_list": GoalKind.CHECKLIST_LIST,
        "hydra_and_dragoon": GoalKind.HYDRA_AND_DRAGOON,
        "beat_king_dedede": GoalKind.BEAT_KING_DEDEDE,
        "max_stats_in_one_run": GoalKind.MAX_STATS_CT,
        "assemble_archipelago_star": GoalKind.ASSEMBLE_AP_STAR,
        "all_three_legendaries_in_one_run": GoalKind.ALL_LEGENDARIES_CT,
        "none": GoalKind.NONE,
    }
    GOALS = (CityTrialGoal, AirRideGoal, TopRideGoal, ArchipelagoGoal)

    def test_values_match_the_shared_enum(self):
        for goal in self.GOALS:
            for name, value in goal.options.items():
                with self.subTest(goal=goal.__name__, option=name):
                    self.assertEqual(value, self.GOAL_KIND[name])

    def test_every_enum_value_is_offered_somewhere(self):
        self.assertEqual({name for goal in self.GOALS for name in goal.options}, set(self.GOAL_KIND))

    def test_none_is_the_last_option_and_defaults_are_offered(self):
        for goal in self.GOALS:
            with self.subTest(goal=goal.__name__):
                self.assertEqual(goal.option_none, max(goal.options.values()))
                self.assertEqual(list(goal.options)[-1], "none")
                self.assertIn(goal.default, goal.options.values())


class TestNativeRewardMap(unittest.TestCase):
    """NATIVE_REWARD_TO_LOCATION inverts the tables' `native_reward` field. A dict comprehension silently
    keeps the last writer, so two boxes claiming the same reward would drop one entry with no error."""

    def test_every_native_reward_is_claimed_by_one_box(self):
        claims: dict[str, list[str]] = {}
        for name, data in LOCATION_TABLE.items():
            if data.native_reward is not None:
                claims.setdefault(str(data.native_reward), []).append(str(name))
        contested = {reward: boxes for reward, boxes in claims.items() if len(boxes) > 1}
        self.assertEqual(contested, {}, f"native rewards claimed by more than one box: {contested}")
        self.assertEqual(len(NATIVE_REWARD_TO_LOCATION), len(claims), "the inverse map lost an entry")

    def test_map_round_trips_through_the_tables(self):
        self.assertTrue(NATIVE_REWARD_TO_LOCATION, "no box declares a native reward")
        for reward, location in NATIVE_REWARD_TO_LOCATION.items():
            with self.subTest(reward=reward):
                self.assertIn(reward, ITEM_TABLE, "a native reward must be a real item")
                self.assertIn(location, LOCATION_TABLE, "a native reward's box must be a real location")
                self.assertEqual(str(LOCATION_TABLE[location].native_reward), reward)


class TestChecklistRewardTypesPartitionRewards(unittest.TestCase):
    """CHECKLIST_REWARD_TYPE_ITEMS is what `checklist_rewards` resolves to and what the placed-types mask
    is built from. A reward under no type is dropped from the pool whatever the player picks, and its bit
    never reaches the mod, so the mod unlocks it at connect - reachable, but never a check."""

    def in_scope_rewards(self) -> set[str]:
        owned_by_a_gate = {str(name) for cat in GATING_CATEGORIES for name in cat.overlapping_rewards}
        return {
            str(name)
            for name, data in ITEM_TABLE.items()
            if data.type in CHECKLIST_REWARD_TYPES
            and not (data.classification & ItemClassification.progression)
            and str(name) not in owned_by_a_gate
        }

    def test_every_in_scope_reward_is_under_exactly_one_type(self):
        rewards = self.in_scope_rewards()
        self.assertTrue(rewards, "ITEM_TABLE has no in-scope checklist rewards")

        membership: dict[str, list[str]] = {}
        for reward_type, type_names in CHECKLIST_REWARD_TYPE_ITEMS.items():
            for name in type_names:
                membership.setdefault(str(name), []).append(str(reward_type))

        unplaceable = sorted(rewards - set(membership))
        self.assertEqual(unplaceable, [], f"rewards under no reward type: {unplaceable}")
        duplicated = {name: types for name, types in membership.items() if len(types) > 1}
        self.assertEqual(duplicated, {}, f"rewards under more than one reward type: {duplicated}")

    def test_types_only_list_in_scope_rewards(self):
        rewards = self.in_scope_rewards()
        for reward_type, type_names in CHECKLIST_REWARD_TYPE_ITEMS.items():
            for name in type_names:
                with self.subTest(reward_type=reward_type, item=name):
                    self.assertIn(str(name), ITEM_TABLE, "reward type lists an item that does not exist")
                    self.assertIn(
                        str(name),
                        rewards,
                        "reward type lists a reward another option owns, which would double-govern it",
                    )

    def test_every_reward_item_type_maps_to_its_own_mode(self):
        # The mask packs one bit per (mode, reward type), so a type with no mode has nowhere to record.
        self.assertEqual(set(CHECKLIST_REWARD_TYPE_MODES), set(CHECKLIST_REWARD_TYPES))
        modes = set(CHECKLIST_REWARD_TYPE_MODES.values())
        self.assertEqual(len(modes), len(CHECKLIST_REWARD_TYPE_MODES), "two item types share a mode")

    def test_every_category_claims_reward_types_exclusively(self):
        self.assertEqual(set(CHECKLIST_REWARD_CATEGORY_TYPES), set(CHECKLIST_REWARD_CATEGORIES))
        self.assertEqual(
            {t for types in CHECKLIST_REWARD_CATEGORY_TYPES.values() for t in types},
            set(CHECKLIST_REWARD_TYPE_ITEMS),
            "a reward type no category claims can never be placed",
        )
        seen: dict[int, str] = {}
        for category, types in CHECKLIST_REWARD_CATEGORY_TYPES.items():
            self.assertTrue(types, f"category {category!r} maps to no reward type, so the mod would ungate it")
            for reward_type in types:
                self.assertNotIn(
                    int(reward_type),
                    seen,
                    f"reward type {reward_type!r} claimed by both {seen.get(int(reward_type))!r} and {category!r}",
                )
                seen[int(reward_type)] = category


class TestTrapCategoriesPartitionTraps(unittest.TestCase):
    """`traps` is the sole governor of which traps may be drawn, and its valid keys are TRAP_CATEGORIES.
    A trap in no category can never be selected however high trap_chance goes - and since the pool just
    fills with something else, generation stays green."""

    def test_every_trap_item_is_in_exactly_one_category(self):
        trap_items = {str(name) for name, data in ITEM_TABLE.items() if data.classification & ItemClassification.trap}
        self.assertTrue(trap_items, "ITEM_TABLE has no trap-classified items")

        membership: dict[str, list[str]] = {}
        for category, category_names in TRAP_CATEGORIES.items():
            for name in category_names:
                membership.setdefault(str(name), []).append(category)

        unreachable = sorted(trap_items - set(membership))
        self.assertEqual(unreachable, [], f"trap items in no `traps` category, so never selectable: {unreachable}")
        duplicated = {name: cats for name, cats in membership.items() if len(cats) > 1}
        self.assertEqual(duplicated, {}, f"trap items in more than one category: {duplicated}")

    def test_categories_only_list_real_trap_items(self):
        for category, category_names in TRAP_CATEGORIES.items():
            for name in category_names:
                with self.subTest(category=category, item=name):
                    self.assertIn(str(name), ITEM_TABLE, "category lists an item that does not exist")
                    self.assertTrue(
                        ITEM_TABLE[name].classification & ItemClassification.trap,
                        "category lists a non-trap item, which `traps` would then wrongly govern",
                    )


class TestStartingUnlockOptionsMatchCandidates(unittest.TestCase):
    """Each starting_* option numbers its choices as 1-based indices into a candidate tuple, which is how
    the world turns a pick back into an item. Nothing generates the two halves from each other, so a
    reordered tuple would hand out the wrong unlock in silence."""

    CASES = (
        ("starting_stadium", StartingStadium, STADIUM_UNLOCK_ITEMS),
        ("starting_machine", StartingMachine, AR_CT_MACHINE_UNLOCK_ITEMS),
        ("starting_top_ride_machine", StartingTopRideMachine, TR_MACHINE_UNLOCK_ITEMS),
        ("starting_air_ride_course", StartingAirRideCourse, AR_COURSE_UNLOCK_ITEMS),
        ("starting_top_ride_course", StartingTopRideCourse, TR_COURSE_UNLOCK_ITEMS),
        ("starting_kirby_color", StartingKirbyColor, COLOR_UNLOCK_ITEMS),
    )

    @staticmethod
    def expected_key(item_name: str) -> str:
        """The option key an unlock earns: its name past the "Unlock ...:" prefix, lowercased with
        punctuation folded to underscores."""
        return re.sub(r"[^a-z0-9]+", "_", item_name.split(": ", 1)[1].lower()).strip("_")

    def test_keys_and_values_line_up_with_the_candidate_tuple(self):
        for option_name, option, candidates in self.CASES:
            with self.subTest(option_name):
                expected = {self.expected_key(item): index for index, item in enumerate(candidates, start=1)}
                expected["randomized"] = 0
                self.assertEqual(option.options, expected)
                self.assertEqual(option.default, option.options["randomized"])
