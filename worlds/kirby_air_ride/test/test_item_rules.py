"""
Item-rule tests.

Two helpers in KARWorld.set_rules attach item_rule callables to specific locations:

- `_set_goal_location_item_rules`: restricts checklist_list goal locations to
  local items (item.player == self.player). Prevents other players' /collect
  from auto-completing the goal.
- `_set_cross_mode_placement_rules`: under cross_mode_placement=false, restricts
  our own mode-tagged PROGRESSION and CHECKLIST REWARD items so each only lands at a
  location whose mode is in the item's source_modes. Other non-progression items
  (traps, filler, counted-useful) and items with empty source_modes are unrestricted.

Both are tested by constructing stub items and invoking the location's
item_rule callable directly: the rule is a property of the Location object,
so we don't need to drive a full fill to inspect it.
"""

from BaseClasses import Item, ItemClassification
from Options import Toggle

from ..KARData import GameMode
from ..KARItems import KARItem, KARItemName
from ..KARLocations import ARLocation, CTLocation, TRLocation
from ..KAROptions import CityTrialGoal
from . import ALL_MODES, CT_ONLY, KARTestBase


def _make_kar_item(world, name: str) -> KARItem:
    """KARItem instance owned by this player (carries source_modes from ITEM_TABLE)."""
    return world.create_item(name)


def _make_foreign_item(name: str, *, code: int = 1234) -> Item:
    """Bare AP Item from a different player slot. Has no source_modes attribute."""
    return Item(name, ItemClassification.filler, code, player=999)


class TestGoalLocationsLocalOnly(KARTestBase):
    """checklist_list goal locations: item_rule rejects foreign items, accepts local items."""

    _GOAL_LOCS = [CTLocation.DESTROY_ALL_HOUSES, CTLocation.BUST_STAR_POLE]
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_checklist_list,
        "city_trial_goal_locations": _GOAL_LOCS,
    }

    def test_foreign_item_rejected_on_each_goal_location(self):
        foreign = _make_foreign_item(KARItemName.AR_REWARD_FILLER_BOX_1)
        for loc_name in self._GOAL_LOCS:
            with self.subTest(location=loc_name):
                loc = self.world.get_location(loc_name)
                self.assertFalse(
                    loc.item_rule(foreign),
                    f"{loc_name} accepted a foreign item: local-only rule missing or broken",
                )

    def test_local_item_accepted_on_each_goal_location(self):
        local = _make_kar_item(self.world, KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM)
        for loc_name in self._GOAL_LOCS:
            with self.subTest(location=loc_name):
                loc = self.world.get_location(loc_name)
                self.assertTrue(
                    loc.item_rule(local),
                    f"{loc_name} rejected a local item",
                )

    def test_non_goal_location_has_no_local_only_rule(self):
        # Sanity counter: a non-goal CT location does NOT have the local-only rule.
        # (Under cross_mode_placement=on by default, item_rule should be Location.item_rule,
        # i.e. accept everything including foreign items.)
        foreign = _make_foreign_item(KARItemName.AR_REWARD_FILLER_BOX_1)
        loc = self.world.get_location(CTLocation.GET_10_BOOST_PATCHES)
        self.assertTrue(
            loc.item_rule(foreign),
            "non-goal location wrongly rejected foreign item: rule leaked outside the goal-locs set",
        )


class TestCrossModePlacementRulesOff(KARTestBase):
    """cross_mode_placement OFF: own AR-tagged PROGRESSION and CHECKLIST REWARD items rejected on CT
    locations, other own non-progression AR items (give-items/filler) accepted anywhere, neutral items
    accepted anywhere, foreign items unaffected."""

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_false}

    def _ct_location(self):
        return self.world.get_location(CTLocation.GET_10_BOOST_PATCHES)

    def _ar_location(self):
        return self.world.get_location(ARLocation.RACE_100_LAPS)

    def _tr_location(self):
        return self.world.get_location(TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS)

    def test_own_ar_progression_rejected_on_ct_location(self):
        # An AR course unlock is progression tagged with source_modes = {AIRRIDE}.
        ar_item = _make_kar_item(self.world, KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK)
        self.assertIn(GameMode.AIRRIDE, ar_item.source_modes)
        self.assertTrue(ar_item.classification & ItemClassification.progression)
        self.assertFalse(
            self._ct_location().item_rule(ar_item),
            "AR-tagged progression item should be rejected on a CT location under cross-mode-off",
        )

    def test_own_ar_progression_accepted_on_ar_location(self):
        ar_item = _make_kar_item(self.world, KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK)
        self.assertTrue(
            self._ar_location().item_rule(ar_item),
            "AR-tagged progression item should be accepted on an AR location",
        )

    def test_own_ar_reward_rejected_on_ct_location(self):
        # AR_REWARD_FILLER_BOX_1 is tagged {AIRRIDE} and is a checklist reward, so under cross-mode-off
        # it is confined to Air Ride (alongside progression) and must NOT land on a CT location.
        ar_reward = _make_kar_item(self.world, KARItemName.AR_REWARD_FILLER_BOX_1)
        self.assertIn(GameMode.AIRRIDE, ar_reward.source_modes)
        self.assertFalse(ar_reward.classification & ItemClassification.progression)
        self.assertFalse(
            self._ct_location().item_rule(ar_reward),
            "AR checklist reward should be rejected on a CT location (rewards are mode-locked under cross-off)",
        )

    def test_neutral_own_progression_accepted_on_ct_and_ar(self):
        # A progression item with empty source_modes is mode-neutral and skips the mode
        # constraint. No real ITEM_TABLE entry is like this today, so use a synthetic item.
        neutral = KARItem(KARItemName.SPAWN_RATE_UP, ItemClassification.progression, 11, self.player)
        neutral.source_modes = frozenset()
        self.assertTrue(self._ct_location().item_rule(neutral))
        self.assertTrue(self._ar_location().item_rule(neutral))
        self.assertTrue(self._tr_location().item_rule(neutral))

    def test_foreign_ar_named_item_unaffected_by_cross_mode_rule(self):
        # The cross-mode rule short-circuits on item.player != self.player, so even an
        # AR-named foreign item is accepted on a CT location. (Other players' items are
        # not under our control to mode-constrain.)
        foreign = _make_foreign_item(KARItemName.AR_REWARD_FILLER_BOX_1)
        self.assertTrue(
            self._ct_location().item_rule(foreign),
            "foreign item should not be filtered by our cross-mode rule",
        )


class TestCrossModePlacementRulesOn(KARTestBase):
    """cross_mode_placement ON: the helper is a no-op; no item_rule is installed.

    Counter-test that proves _set_cross_mode_placement_rules respects its own gate.
    """

    options = {**ALL_MODES, "cross_mode_placement": Toggle.option_true}

    def test_ar_reward_accepted_on_ct_location(self):
        ar_item = _make_kar_item(self.world, KARItemName.AR_REWARD_FILLER_BOX_1)
        ct_loc = self.world.get_location(CTLocation.GET_10_BOOST_PATCHES)
        self.assertTrue(
            ct_loc.item_rule(ar_item),
            "cross-mode-on should not install a mode-locking rule",
        )
