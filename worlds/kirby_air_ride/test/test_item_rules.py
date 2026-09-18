"""Item rules: set_rules pins each checklist_list goal location to local items, so another player's
/collect cannot auto-complete the goal. Driven by invoking each location's item_rule with stub items."""

from BaseClasses import Item, ItemClassification

from ..KARItems import KARItemName
from ..KARLocations import APLocation, CTLocation
from ..KAROptions import ArchipelagoGoal, CityTrialGoal
from . import CT_ONLY, KARTestBase

# A bare AP Item from a different player slot.
_FOREIGN = Item(str(KARItemName.AR_REWARD_FILLER_BOX_1), ItemClassification.filler, 1234, player=999)


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


# (label, options, the goal locations, a box of the same mode that is not a goal location). The
# Archipelago row is worth its own case: an AP box lives in another mode's region, so it is the one goal
# location whose parent region belongs to a mode that may have no goal at all.
_CASES: list[tuple[str, dict, list[str], str]] = [
    (
        "city_trial",
        {
            **CT_ONLY,
            "city_trial_goal": CityTrialGoal.option_checklist_list,
            "city_trial_goal_locations": [CTLocation.DESTROY_ALL_HOUSES, CTLocation.BUST_STAR_POLE],
        },
        [CTLocation.DESTROY_ALL_HOUSES, CTLocation.BUST_STAR_POLE],
        CTLocation.GET_10_BOOST_PATCHES,
    ),
    (
        "archipelago",
        {
            **CT_ONLY,
            "archipelago_goal": ArchipelagoGoal.option_checklist_list,
            "archipelago_goal_locations": [APLocation.GET_10_HP_PATCHES, APLocation.BREAK_ALL_CORAL],
        },
        [APLocation.GET_10_HP_PATCHES, APLocation.BREAK_ALL_CORAL],
        APLocation.CASTLE_FLOWER_ON_FOOT,
    ),
]


def _make_local_only_test(goal_locs: list[str], non_goal: str, opts: dict) -> type:
    class _LocalOnly(KARTestBase):
        options = opts

        def test_goal_locations_take_local_items_only(self):
            local = self.world.create_item(KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM)
            for loc_name in goal_locs:
                with self.subTest(location=loc_name):
                    loc = self.world.get_location(loc_name)
                    self.assertFalse(loc.item_rule(_FOREIGN), f"{loc_name} accepted a foreign item")
                    self.assertTrue(loc.item_rule(local), f"{loc_name} rejected a local item")

        def test_the_rule_does_not_leak_past_the_goal_locations(self):
            self.assertTrue(
                self.world.get_location(non_goal).item_rule(_FOREIGN),
                f"{non_goal} is not a goal location but rejected a foreign item",
            )

    return _LocalOnly


for _label, _opts, _goal_locs, _non_goal in _CASES:
    _register(_make_local_only_test(_goal_locs, _non_goal, _opts), f"TestGoalLocationsLocalOnly_{_label}")
