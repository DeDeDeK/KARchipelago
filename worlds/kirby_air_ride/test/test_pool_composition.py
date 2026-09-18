"""Item-pool composition: what _build_item_pools and create_items mint, and how many. Several options
default to a state that leaves their pool empty - `checklist_rewards` most of all - so a config meant to
exercise one selects its categories explicitly, or the assertions pass over nothing."""

from collections import Counter

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARData import GameMode
from ..KARItems import (
    ALLOWED_ITEM_CATEGORY_ITEMS,
    CHECKLIST_REWARD_TYPES,
    ITEM_TABLE,
    STADIUM_CHECKLIST_REWARDS,
    KARItemGroup,
    KARItemName,
    KARItemType,
)
from ..KAROptions import ArchipelagoGoal, CityTrialGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, items_of_type

_ALL_REWARD_CATEGORIES = ["Endings", "Filler Boxes", "Gameplay Extras", "Music", "Sound Test"]

# Every gate off, for the configs that need room for a maximal counted pool.
_NO_GATES = {
    "city_trial_stadiums_gated": Toggle.option_false,
    "city_trial_events_gated": Toggle.option_false,
    "abilities_gated": Toggle.option_false,
    "city_trial_patches_gated": Toggle.option_false,
    "machines_gated": Toggle.option_false,
    "city_trial_boxes_gated": Toggle.option_false,
    "city_trial_items_gated": Toggle.option_false,
    "colors_gated": Toggle.option_false,
    "top_ride_items_gated": Toggle.option_false,
    "air_ride_courses_gated": Toggle.option_false,
    "top_ride_courses_gated": Toggle.option_false,
}


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


# (label, options, item, expected copies). ALL_MODES appears wherever a large counted pool needs more
# default locations than one mode provides; the counts themselves are mode-independent.
_QUANTITY_CASES: list[tuple[str, dict, str, int]] = [
    # Patch Cap Increase: one per step of the cap span, and a City-Trial-only mechanic.
    (
        "patch_cap_span",
        {**ALL_MODES, "city_trial_patch_cap_min": 9, "city_trial_patch_cap_max": 18},
        KARItemName.PATCH_CAP_INCREASE,
        9,
    ),
    (
        "patch_cap_flat",
        {**CT_ONLY, "city_trial_patch_cap_min": 18, "city_trial_patch_cap_max": 18},
        KARItemName.PATCH_CAP_INCREASE,
        0,
    ),
    (
        "patch_cap_full_span",
        {**ALL_MODES, **_NO_GATES, "city_trial_patch_cap_min": 1, "city_trial_patch_cap_max": 30},
        KARItemName.PATCH_CAP_INCREASE,
        29,
    ),
    (
        "patch_cap_without_city_trial",
        {**AR_ONLY, "city_trial_patch_cap_min": 1, "city_trial_patch_cap_max": 30},
        KARItemName.PATCH_CAP_INCREASE,
        0,
    ),
    # Spawn Rate Up: one per 10% step, with off-grid bounds snapped first (64 -> 60, 227 -> 230).
    ("spawn_rate_span", {**ALL_MODES, "spawn_rate_min": 100, "spawn_rate_max": 300}, KARItemName.SPAWN_RATE_UP, 20),
    ("spawn_rate_off_grid", {**ALL_MODES, "spawn_rate_min": 64, "spawn_rate_max": 227}, KARItemName.SPAWN_RATE_UP, 17),
    ("spawn_rate_flat", {**CT_ONLY, "spawn_rate_min": 100, "spawn_rate_max": 100}, KARItemName.SPAWN_RATE_UP, 0),
    (
        "spawn_rate_sub_vanilla_min",
        {**CT_ONLY, "spawn_rate_min": 50, "spawn_rate_max": 100},
        KARItemName.SPAWN_RATE_UP,
        5,
    ),
    # Drop Patches Trap only fires in City Trial scenes, so it is excluded without one.
    ("drop_patches_trap_without_city_trial", {**TR_ONLY, "trap_chance": 50}, KARItemName.DROP_PATCHES_TRAP, 0),
]


def _make_quantity_test(opts: dict, item: str, expected: int) -> type:
    class _Quantity(KARTestBase):
        options = opts

        def test_pool_holds_the_expected_count(self):
            self.assertEqual(self.count_in_pool(item), expected)

    return _Quantity


for _label, _opts, _item, _expected in _QUANTITY_CASES:
    _register(_make_quantity_test(_opts, _item, _expected), f"TestQuantity_{_label}")


class TestCheckboxFillerCounts(KARTestBase):
    options = {
        **ALL_MODES,
        "city_trial_checkbox_fillers": 3,
        "air_ride_checkbox_fillers": 7,
        "top_ride_checkbox_fillers": 2,
    }

    def test_per_mode_counts(self):
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_CITY_TRIAL), 3)
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_AIR_RIDE), 7)
        self.assertEqual(self.count_in_pool(KARItemName.CHECKBOX_FILLER_TOP_RIDE), 2)


class TestPoolFillsAllLocations(KARTestBase):
    options = ALL_MODES

    def test_pool_size_matches_locations(self):
        self.assertEqual(len(self.itempool_items()), len(self.placeable_locations()))


# allowed_items governs the give-item categories. (label, preset, the categories to keep - None leaves
# the option at its default, which is Permanent Patches alone.)
_ALLOWED_ITEM_CASES: list[tuple[str, dict, list[str] | None]] = [
    ("all_on", ALL_MODES, sorted(ALLOWED_ITEM_CATEGORY_ITEMS)),
    ("default_is_permanent_patches_only", ALL_MODES, None),
    (
        "permanent_patches_dropped",
        ALL_MODES,
        ["City Trial Item Gives", "City Trial Event Gives", "Copy Ability Gives", "Top Ride Item Gives"],
    ),
    # Filler-providing categories stay on so the config still fills.
    ("three_kept", ALL_MODES, ["Permanent Patches", "City Trial Item Gives", "Top Ride Item Gives"]),
]


def _make_allowed_items_test(preset: dict, kept: list[str] | None) -> type:
    keep = [KARItemGroup.PERMANENT_PATCHES] if kept is None else kept

    class _AllowedItems(KARTestBase):
        options = preset if kept is None else {**preset, "allowed_items": kept}

        def test_kept_categories_eligible_and_dropped_ones_absent(self):
            # None of these types are progression / reward / counted, so eligibility is exactly
            # useful_pool | filler_pool.
            eligible = self.world.useful_pool | self.world.filler_pool
            pool_names = set(self.itempool_names())
            for category, category_names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
                with self.subTest(category=category):
                    if category in keep:
                        missing = set(category_names) - eligible
                        self.assertFalse(missing, f"{category} kept but not eligible: {sorted(missing)}")
                    else:
                        self.assertFalse(set(category_names) & eligible, f"{category} eligible when dropped")
                        self.assertFalse(set(category_names) & pool_names, f"{category} in pool when dropped")

    return _AllowedItems


for _label, _preset, _kept in _ALLOWED_ITEM_CASES:
    _register(_make_allowed_items_test(_preset, _kept), f"TestAllowedItems_{_label}")


class TestAllowedItemsTrapsOrthogonal(KARTestBase):
    """allowed_items governs only NON-trap items. With every give category disabled, the trap-class items
    of those same types stay trap-eligible, since `traps` is the sole governor of traps."""

    options = {
        **ALL_MODES,
        "allowed_items": [],
        "trap_chance": 100,
        "traps": ["Direct Damage", "Stat Debuff", "Fake Patches"],
    }

    def test_non_trap_gives_absent_but_traps_eligible(self):
        eligible = self.world.useful_pool | self.world.filler_pool
        for category, category_names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            with self.subTest(category=category):
                self.assertFalse(set(category_names) & eligible, f"{category} non-trap items eligible when disabled")
        for trap_name in (
            KARItemName.FAKE_BOOST_PATCH,
            KARItemName.BOOST_DOWN_PATCH,
            KARItemName.COPY_ABILITY_SLEEP,
            KARItemName.GIVE_TR_ITEM_SPEED_DOWN,
        ):
            with self.subTest(trap=trap_name):
                self.assertIn(trap_name, self.world.trap_pool)


# Two ways to end up with no traps: the chance is zero, or no `traps` category is selected.
def _make_no_traps_test(opts: dict) -> type:
    class _NoTraps(KARTestBase):
        options = opts

        def test_trap_pool_and_itempool_are_trap_free(self):
            traps = [item for item in self.itempool_items() if item.classification & ItemClassification.trap]
            self.assertEqual(traps, [], f"traps placed: {[t.name for t in traps]}")

    return _NoTraps


for _label, _opts in (
    ("chance_zero", {**CT_ONLY, "trap_chance": 0}),
    ("no_categories_selected", {**ALL_MODES, "trap_chance": 50, "traps": []}),
):
    _register(_make_no_traps_test(_opts), f"TestNoTraps_{_label}")


class TestNoTrapCategoriesLeavesTrapPoolEmpty(KARTestBase):
    """trap_chance > 0 but `traps` selects nothing: an empty category selection short-circuits placement."""

    options = {**ALL_MODES, "trap_chance": 50, "traps": []}

    def test_trap_pool_empty(self):
        self.assertEqual(self.world.trap_pool, set())


# Stadiums gated or not, the six overlapping stadium checklist rewards leave the pool: gated they are
# superseded by the Unlock Stadium items, ungated the mod unlocks all 24 at connect.
def _make_stadium_gate_test(gated: bool) -> type:
    class _StadiumGate(KARTestBase):
        options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true if gated else Toggle.option_false}

        def test_unlocks_follow_the_gate(self):
            names = self.world_item_names()
            for unlock in items_of_type(KARItemType.CT_STADIUM_UNLOCK):
                with self.subTest(unlock=unlock):
                    self.assertEqual(unlock in names, gated)

        def test_overlapping_rewards_always_excluded(self):
            names = self.world_item_names()
            for reward in STADIUM_CHECKLIST_REWARDS:
                with self.subTest(reward=reward):
                    self.assertNotIn(reward, names)

    return _StadiumGate


for _gated in (True, False):
    _register(_make_stadium_gate_test(_gated), f"TestStadiumUnlocks_{'gated' if _gated else 'ungated'}")


# Permanent patches carry _AR_CT: the mod applies them at Air Ride round start too, but Top Ride has no
# MachineData, so its apply loop reaches nobody there.
def _make_permanent_patch_test(preset: dict, present: bool) -> type:
    class _PermanentPatches(KARTestBase):
        options = preset

        def test_presence_follows_the_enabled_modes(self):
            leaked = set(self.itempool_names()) & items_of_type(KARItemType.PERMANENT_PATCH)
            self.assertEqual(bool(leaked), present, f"permanent patches: {sorted(leaked)[:5]}")

    return _PermanentPatches


for _label, _preset, _present in (("air_ride", AR_ONLY, True), ("top_ride", TR_ONLY, False)):
    _register(_make_permanent_patch_test(_preset, _present), f"TestPermanentPatches_{_label}")


class TestArchipelagoChecklistMakesCityTrialAPlayedMode(KARTestBase):
    """The source-modes backstop reads logic_modes, not the goal flags, and the Archipelago checklist is
    the one thing that still separates them: its boxes are City Trial and Air Ride activities, so
    choosing that goal is choosing those modes, and their items work."""

    options = {
        "city_trial_goal": CityTrialGoal.option_none,
        "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
    }

    def test_city_trial_items_admitted(self):
        self.assertIn(GameMode.CITYTRIAL, self.world.logic_modes)
        self.assertTrue(set(self.itempool_names()) & items_of_type(KARItemType.PERMANENT_PATCH))


# Checklist rewards are unique one-time unlocks, not draw-with-replacement filler - a regression pin for
# the old "reward soup" bug, where about half were absent while others repeated. Air Ride is the tight
# single-mode case: its only repeatable filler is the reclassified CT+AR patch-gives.
def _make_reward_uniqueness_test(preset: dict, expected_types: set) -> type:
    class _RewardUniqueness(KARTestBase):
        options = {**preset, "checklist_rewards": _ALL_REWARD_CATEGORIES}

        def test_useful_rewards_appear_exactly_once(self):
            counts = Counter(self.itempool_names())
            self.assertTrue(self.world.reward_pool, "reward_pool should be populated with every category on")
            self.assertEqual(
                len(self.world.reward_pool), len(set(self.world.reward_pool)), "duplicate reward_pool entry"
            )
            for name in self.world.reward_pool:
                with self.subTest(reward=name):
                    if ITEM_TABLE[name].classification & ItemClassification.useful:
                        # Useful rewards consume scarce default locations, so exactly one each.
                        self.assertEqual(counts[name], 1)
                    else:
                        # Filler rewards may repeat as junk-box filler, but must appear at least once.
                        self.assertGreaterEqual(counts[name], 1)

        def test_no_useful_reward_is_duplicated_anywhere(self):
            counts = Counter(self.itempool_names())
            for name, data in ITEM_TABLE.items():
                if data.type in CHECKLIST_REWARD_TYPES and (data.classification & ItemClassification.useful):
                    with self.subTest(reward=name):
                        self.assertLessEqual(counts[name], 1, f"useful reward {name} duplicated")

        def test_only_the_enabled_modes_rewards_are_in_scope(self):
            self.assertEqual({ITEM_TABLE[name].type for name in self.world.reward_pool}, expected_types)
            pool = set(self.itempool_names())
            for name, data in ITEM_TABLE.items():
                if data.type in CHECKLIST_REWARD_TYPES - expected_types:
                    with self.subTest(reward=name):
                        self.assertNotIn(name, pool, f"{name} is an off-mode reward and must not be minted")

    return _RewardUniqueness


for _label, _preset, _types in (
    ("all_modes", ALL_MODES, set(CHECKLIST_REWARD_TYPES)),
    ("air_ride_only", AR_ONLY, {KARItemType.AR_CHECKLIST_REWARD}),
):
    _register(_make_reward_uniqueness_test(_preset, _types), f"TestChecklistRewardsUnique_{_label}")
