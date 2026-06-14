"""
Item-rule tests.

set_rules attaches an item_rule callable to each checklist_list goal location, restricting it to local
items (item.player == self.player). This prevents other players' /collect from auto-completing the goal.

Tested by invoking each location's item_rule callable directly with stub items - no full fill needed.
"""

from BaseClasses import Item, ItemClassification

from ..KARItems import KARItem, KARItemName
from ..KARLocations import CTLocation
from ..KAROptions import CityTrialGoal
from . import CT_ONLY, KARTestBase


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
        # Sanity counter: a non-goal CT location has no local-only rule, so it accepts everything
        # including foreign items.
        foreign = _make_foreign_item(KARItemName.AR_REWARD_FILLER_BOX_1)
        loc = self.world.get_location(CTLocation.GET_10_BOOST_PATCHES)
        self.assertTrue(
            loc.item_rule(foreign),
            "non-goal location wrongly rejected foreign item: rule leaked outside the goal-locs set",
        )
