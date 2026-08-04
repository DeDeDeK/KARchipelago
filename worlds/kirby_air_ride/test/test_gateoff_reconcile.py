"""Beatability + pool guards for the gate-off reward reconciliation.

When a gating category's gate is OFF the mod pre-unlocks the whole category at connect, so its checklist
rewards gate nothing and leave the pool - uniformly, top_ride_items and stadiums included. These tests
pin that the reconciled configs still generate a beatable seed, and that overlapping rewards drop while
the gate's own Unlock items carry progression.
"""

from Options import Toggle

from ..KARItems import GATING_CATEGORIES, KARItemType
from . import ALL_MODES, AR_AND_TR, CT_ONLY, KARTestBase, items_of_type

_OFF = Toggle.option_false
_ON = Toggle.option_true

# Overlapping checklist rewards per gating option (the rewards always excluded from the pool).
_OVERLAP = {cat.option: cat.overlapping_rewards for cat in GATING_CATEGORIES}


class TestReconcileCTOnlyMachinesStadiumsOff(KARTestBase):
    """City-Trial-only with machines and stadiums both ungated: their overlapping checklist rewards are
    excluded (the mod unlocks everything at connect) and the seed is still beatable."""

    options = {**CT_ONLY, "machines_gated": _OFF, "city_trial_stadiums_gated": _OFF}

    def test_machine_and_stadium_rewards_excluded(self):
        names = self.world_item_names()
        for reward in (*_OVERLAP["machines_gated"], *_OVERLAP["city_trial_stadiums_gated"]):
            self.assertNotIn(reward, names)

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestReconcileCTOnlyMachinesOffStadiumsOn(KARTestBase):
    """machines ungated but stadiums gated: the stadiums are gated by their own Unlock Stadium items, so
    the stadium checklist rewards are excluded (not promoted), and machine rewards drop too. Beatable."""

    options = {**CT_ONLY, "machines_gated": _OFF, "city_trial_stadiums_gated": _ON}

    def test_stadium_unlocks_present_rewards_excluded(self):
        names = self.world_item_names()
        # Stadiums gated: the Unlock Stadium items carry the gate (one is the precollected starter).
        self.assertTrue(any(unlock in names for unlock in items_of_type(KARItemType.CT_STADIUM_UNLOCK)))
        for reward in (*_OVERLAP["city_trial_stadiums_gated"], *_OVERLAP["machines_gated"]):
            self.assertNotIn(reward, names)

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestReconcileAllModesMaxGateOff(KARTestBase):
    """Every reconcilable gate OFF: the mod unlocks each category fully at connect, so every overlapping
    reward - machine / Nebula / stadium / TR-item - drops from the pool. Still beatable."""

    options = {
        **ALL_MODES,
        "machines_gated": _OFF,
        "colors_gated": _OFF,
        "air_ride_courses_gated": _OFF,
        "top_ride_items_gated": _OFF,
        "city_trial_stadiums_gated": _OFF,
    }

    def test_all_overlapping_rewards_dropped(self):
        names = self.world_item_names()
        for cat in GATING_CATEGORIES:
            for reward in cat.overlapping_rewards:
                self.assertNotIn(reward, names)

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)


class TestReconcileARTRMachinesOff(KARTestBase):
    """Air Ride + Top Ride (no City Trial) with machines OFF: the AR machine cells lose their reward
    gate and the seed is still beatable."""

    options = {**AR_AND_TR, "machines_gated": _OFF}

    def test_beatable(self):
        self.collect_all_but_victories()
        self.assertBeatable(True)
