"""Which unlock items a seed mints and which gate flags it ships, every case derived from
GATING_CATEGORIES. The mod applies gate flags goal-independently, so what ships is the category's
*effective* state - gate on AND some mode that gives its unlocks meaning has a goal."""

from Options import Toggle

from ..KARItems import (
    AP_STAR_PIECE_UNLOCK_ITEMS,
    GATING_CATEGORIES,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    KARItemName,
    KARItemType,
)
from ..KAROptions import ArchipelagoGoal, CityTrialGoal
from . import ALL_MODES, AR_ONLY, OVERLAP_REWARDS, TR_ONLY, KARTestBase, items_of_type


def _all_modes_with(**overrides):
    return {**ALL_MODES, **overrides}


# The unlock items each gate mints when it is ON.
_GATE_GROUPS: dict[str, set[str]] = {cat.option: items_of_type(cat.item_type) for cat in GATING_CATEGORIES}

_ALL_ON = dict.fromkeys(_GATE_GROUPS, Toggle.option_true)
_ALL_OFF = dict.fromkeys(_GATE_GROUPS, Toggle.option_false)


def _assert_no_overlap_rewards(test: KARTestBase) -> None:
    """A gate's overlapping checklist rewards never reach the pool: the mod owns that category either way."""
    world_items = test.world_item_names()
    for option_name, overlap in OVERLAP_REWARDS.items():
        with test.subTest(gate=option_name):
            leaked = world_items & overlap
            test.assertFalse(leaked, f"{option_name} leaked overlap rewards: {sorted(leaked)}")


class TestAllGatesOn(KARTestBase):
    options = _all_modes_with(**_ALL_ON)

    def test_all_unlock_groups_present(self):
        world_items = self.world_item_names()
        for option_name, group in _GATE_GROUPS.items():
            with self.subTest(gate=option_name):
                missing = group - world_items
                self.assertFalse(missing, f"{option_name} ON but missing unlocks: {sorted(missing)}")

    def test_gated_checklist_rewards_excluded(self):
        _assert_no_overlap_rewards(self)


class TestAllGatesOff(KARTestBase):
    options = _all_modes_with(**_ALL_OFF)

    def test_no_unlock_items_present(self):
        world_items = self.world_item_names()
        for option_name, group in _GATE_GROUPS.items():
            with self.subTest(gate=option_name):
                present = world_items & group
                self.assertFalse(present, f"{option_name} OFF but unlocks leaked: {sorted(present)}")

    def test_gated_checklist_rewards_excluded(self):
        _assert_no_overlap_rewards(self)


def _make_single_gate_test(gate_name: str, group: set[str]) -> type:
    class _SingleGateOn(KARTestBase):
        """Exactly one gate ON: its whole group is minted and no other gate's group leaks in."""

        options = _all_modes_with(**{**_ALL_OFF, gate_name: Toggle.option_true})

        def test_only_this_gate_group_present(self):
            world_items = self.world_item_names()
            present = world_items & group
            self.assertEqual(
                present, group, f"{gate_name} ON should add the full group; missing: {sorted(group - present)}"
            )
            for other_gate, other_group in _GATE_GROUPS.items():
                if other_gate == gate_name:
                    continue
                leaked = world_items & (other_group - group)
                self.assertFalse(leaked, f"{other_gate} OFF leaked: {sorted(leaked)}")

    _SingleGateOn.__name__ = f"TestOnly_{gate_name}_On"
    _SingleGateOn.__qualname__ = _SingleGateOn.__name__
    return _SingleGateOn


for _gate, _group in _GATE_GROUPS.items():
    globals()[f"TestOnly_{_gate}_On"] = _make_single_gate_test(_gate, _group)


class TestEffectiveGateShipping(KARTestBase):
    """A gate ships ON only when the seed actually holds that category's keys. An AR-only seed is the
    sharpest case: City Trial's events, patches, boxes and stadiums are DefaultOnToggles whose unlocks an
    AR-only pool drops, and shipping them locked would strand that content behind items that never exist.
    """

    options = _all_modes_with(**_ALL_ON, **AR_ONLY)

    def test_gate_ships_exactly_when_the_seed_holds_its_keys(self):
        slot_data = self.world.fill_slot_data()
        world_items = self.world_item_names()
        for cat in GATING_CATEGORIES:
            with self.subTest(gate=cat.option):
                has_keys = bool(items_of_type(cat.item_type) & world_items)
                self.assertEqual(
                    slot_data[cat.option],
                    int(has_keys),
                    f"{cat.option} ships {slot_data[cat.option]} but the seed "
                    f"{'holds' if has_keys else 'holds none of'} its unlock items",
                )

    def test_mode_agnostic_colors_stay_keyed(self):
        # colors_gated declares no required_modes, so the membership test must read
        # `not required_modes or any(...)` - an intersection would silently drop colors here.
        self.assertIn("colors_gated", self.world.effective_gates)
        self.assertEqual(self.world.fill_slot_data()["colors_gated"], 1)
        self.assertTrue(items_of_type(KARItemType.COLOR_UNLOCK) & self.world_item_names())


# A gate OFF drops its whole group except the unlocks this seed's goal is gated on - without those the
# goal is one in-game feat winnable in the first match with nothing from the pool.
_GOAL_KEY_CASES: list[tuple[str, dict, str, set, str]] = [
    (
        "legendary_pieces",
        {"city_trial_goal": CityTrialGoal.option_hydra_and_dragoon, "city_trial_items_gated": Toggle.option_false},
        "city_trial_items_gated",
        set(LEGENDARY_PIECE_UNLOCK_ITEMS),
        "legendary_pieces_goal_gated",
    ),
    (
        "vs_king_dedede",
        {"city_trial_goal": CityTrialGoal.option_beat_king_dedede, "city_trial_stadiums_gated": Toggle.option_false},
        "city_trial_stadiums_gated",
        {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE},
        "vs_king_dedede_goal_gated",
    ),
    (
        "ap_star_pieces",
        {
            "archipelago_goal": ArchipelagoGoal.option_assemble_archipelago_star,
            "city_trial_items_gated": Toggle.option_false,
        },
        "city_trial_items_gated",
        set(AP_STAR_PIECE_UNLOCK_ITEMS),
        "ap_star_pieces_goal_gated",
    ),
]


def _make_goal_key_test(label: str, opts: dict, gate: str, forced: set, flag: str) -> type:
    class _GoalKeysSurviveGateOff(KARTestBase):
        options = _all_modes_with(**opts)

        def test_only_the_goal_keys_ship(self):
            self.assertEqual(self.world_item_names() & _GATE_GROUPS[gate], forced)

        def test_category_ships_ungated_with_the_keys_held_back(self):
            slot_data = self.world.fill_slot_data()
            self.assertEqual(slot_data[gate], 0)
            self.assertEqual(slot_data[flag], 1)

    _GoalKeysSurviveGateOff.__name__ = f"TestGoalKeysSurviveGateOff_{label}"
    _GoalKeysSurviveGateOff.__qualname__ = _GoalKeysSurviveGateOff.__name__
    return _GoalKeysSurviveGateOff


for _label, _opts, _gate, _forced, _flag in _GOAL_KEY_CASES:
    _cls = _make_goal_key_test(_label, _opts, _gate, _forced, _flag)
    globals()[_cls.__name__] = _cls


class TestGoalKeysUnaffectedWhenGateOn(KARTestBase):
    """The gate being ON already ships the goal's keys, so nothing is forced and the whole group is in."""

    options = _all_modes_with(
        city_trial_items_gated=Toggle.option_true,
        city_trial_goal=CityTrialGoal.option_hydra_and_dragoon,
    )

    def test_whole_group_ships_and_nothing_is_forced(self):
        group = _GATE_GROUPS["city_trial_items_gated"]
        self.assertEqual(self.world_item_names() & group, group)
        self.assertFalse(self.world.goal_forced_unlocks)


class TestGoalKeysForcedWhenTheCategoryHoldsNoKeys(KARTestBase):
    """Regression: City Trial has no goal, so city_trial_items_gated never becomes effective - but the
    Archipelago star goal is keyed on six City Trial spheres, which must be minted anyway. The gate is
    left ON to pin the case the source-modes backstop used to eat."""

    options = {
        **TR_ONLY,
        "archipelago_goal": ArchipelagoGoal.option_assemble_archipelago_star,
        "city_trial_items_gated": Toggle.option_true,
    }

    def test_only_the_spheres_are_forced_into_the_pool(self):
        self.assertNotIn("city_trial_items_gated", self.world.effective_gates)
        pool = self.world_item_names()
        self.assertTrue(set(AP_STAR_PIECE_UNLOCK_ITEMS) <= self.world.goal_forced_unlocks)
        self.assertTrue(set(AP_STAR_PIECE_UNLOCK_ITEMS) <= pool)
        # The rest of the ungated, goal-less category stays out.
        self.assertNotIn(KARItemName.UNLOCK_ITEM_GORDO, pool)

    def test_slot_data_flags_the_holdback(self):
        data = self.world.fill_slot_data()
        self.assertEqual(data["city_trial_items_gated"], 0)
        self.assertEqual(data["ap_star_pieces_goal_gated"], 1)
