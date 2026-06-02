from Options import Toggle

from ..KARItems import GATING_CATEGORIES
from . import ALL_MODES, KARTestBase, items_of_type


def _all_modes_with(**overrides):
    return {**ALL_MODES, **overrides}


# Group expectations per gate: the unlock items that should appear when the gate is ON.
# Derived from GATING_CATEGORIES so this stays in sync with the gating source of truth.
_GATE_GROUPS: dict[str, set[str]] = {cat.option: items_of_type(cat.item_type) for cat in GATING_CATEGORIES}

# Overlapping checklist rewards per gate (always excluded from the pool). Same source of truth.
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


# Per-gate isolation: turn ON exactly one gate at a time (all others off).
# Verifies that toggling each gate independently flips its group on/off.
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
