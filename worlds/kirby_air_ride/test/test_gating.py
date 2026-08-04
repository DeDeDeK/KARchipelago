from Options import Toggle

from ..KARItems import GATING_CATEGORIES, KARItemType
from . import ALL_MODES, AR_ONLY, KARTestBase, items_of_type


def _all_modes_with(**overrides):
    return {**ALL_MODES, **overrides}


# The unlock items that should appear when each gate is ON. Derived from GATING_CATEGORIES.
_GATE_GROUPS: dict[str, set[str]] = {cat.option: items_of_type(cat.item_type) for cat in GATING_CATEGORIES}

# Overlapping checklist rewards per gate (always excluded from the pool).
_GATED_CHECKLIST_REWARDS: dict[str, frozenset] = {
    cat.option: cat.overlapping_rewards for cat in GATING_CATEGORIES if cat.overlapping_rewards
}


_ALL_ON = dict.fromkeys(_GATE_GROUPS, Toggle.option_true)
_ALL_OFF = dict.fromkeys(_GATE_GROUPS, Toggle.option_false)


class TestAllGatesOn(KARTestBase):
    """With every mode enabled and every gate ON, every UNLOCK group should appear."""

    options = _all_modes_with(**_ALL_ON)

    def test_all_unlock_groups_present(self):
        world_items = self.world_item_names()
        for option_name, group in _GATE_GROUPS.items():
            with self.subTest(gate=option_name):
                missing = group - world_items
                self.assertFalse(missing, f"{option_name} ON but missing unlocks: {sorted(missing)}")

    def test_gated_checklist_rewards_excluded(self):
        """A gate's overlapping checklist rewards are excluded from the pool (here with the gate ON; they
        are also excluded when OFF, since the mod handles the category either way)."""
        world_items = self.world_item_names()
        for option_name, overlap in _GATED_CHECKLIST_REWARDS.items():
            with self.subTest(gate=option_name):
                leaked = world_items & overlap
                self.assertFalse(leaked, f"{option_name} ON should exclude overlap rewards, found: {sorted(leaked)}")


class TestAllGatesOff(KARTestBase):
    """With every gate OFF, no UNLOCK item from any gate group should appear."""

    options = _all_modes_with(**_ALL_OFF)

    def test_no_unlock_items_present(self):
        world_items = self.world_item_names()
        for option_name, group in _GATE_GROUPS.items():
            with self.subTest(gate=option_name):
                present = world_items & group
                self.assertFalse(present, f"{option_name} OFF but unlocks leaked: {sorted(present)}")


# Per-gate isolation: turn ON exactly one gate at a time and verify only its group appears.
def _make_single_gate_test(gate_name: str, group: set[str]) -> type:
    class _SingleGateOn(KARTestBase):
        options = _all_modes_with(**{**_ALL_OFF, gate_name: Toggle.option_true})

        def test_only_this_gate_group_present(self):
            world_items = self.world_item_names()
            present = world_items & group
            self.assertEqual(
                present, group, f"{gate_name} ON should add the full group; missing: {sorted(group - present)}"
            )
            # No other gate's group should leak in.
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
    """A gate ships to the mod as ON only when the seed actually holds that category's keys.

    The mod applies gate flags goal-independently (no gate_*.c consults goal[]), so shipping a raw YAML
    toggle for a category whose modes all lack a goal would permanently lock that content behind unlock
    items that were never minted. An AR-only seed is the sharpest case: City Trial's events, patches,
    boxes and stadiums are DefaultOnToggles whose unlocks an AR-only pool drops. Derived from
    GATING_CATEGORIES so a new category is covered automatically.
    """

    options = _all_modes_with(**_ALL_ON, **AR_ONLY)

    def test_no_category_ships_locked_without_keys(self):
        slot_data = self.world.fill_slot_data()
        world_items = self.world_item_names()
        for cat in GATING_CATEGORIES:
            with self.subTest(gate=cat.option):
                has_keys = bool(items_of_type(cat.item_type) & world_items)
                if not has_keys:
                    self.assertEqual(
                        slot_data[cat.option],
                        0,
                        f"{cat.option} ships ON but the seed contains none of its unlock items, "
                        f"so that content could never be unlocked",
                    )

    def test_category_with_keys_still_ships_on(self):
        """The fix must not over-correct: a category that does hold keys still ships ON."""
        slot_data = self.world.fill_slot_data()
        world_items = self.world_item_names()
        for cat in GATING_CATEGORIES:
            with self.subTest(gate=cat.option):
                if items_of_type(cat.item_type) & world_items:
                    self.assertEqual(slot_data[cat.option], 1, f"{cat.option} holds keys but ships OFF")

    def test_effective_gates_matches_shipped_flags(self):
        slot_data = self.world.fill_slot_data()
        for cat in GATING_CATEGORIES:
            with self.subTest(gate=cat.option):
                self.assertEqual(slot_data[cat.option], int(cat.option in self.world.effective_gates))


class TestColorsGateSurvivesModeAgnostic(KARTestBase):
    """colors_gated has an empty required_modes, meaning mode-agnostic: always keyed, never mode-excluded.
    The membership test must read `not required_modes or any(...)` - an intersection would treat "no
    required modes" as "no match" and silently drop colors. Pinned in the least forgiving mode combo."""

    options = _all_modes_with(**_ALL_ON, **AR_ONLY)

    def test_colors_effective_and_shipped(self):
        self.assertIn("colors_gated", self.world.effective_gates)
        self.assertEqual(self.world.fill_slot_data()["colors_gated"], 1)

    def test_color_unlocks_in_pool(self):
        self.assertTrue(items_of_type(KARItemType.COLOR_UNLOCK) & self.world_item_names())
