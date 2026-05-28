from typing import TYPE_CHECKING

from test.bases import WorldTestBase

from ..KARItems import KARItemName, KARItemType, items_by_type
from ..KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal

if TYPE_CHECKING:
    from .. import KARWorld


def items_of_type(t: KARItemType) -> set[str]:
    """All item names in ITEM_TABLE whose type matches `t`. Thin wrapper over the
    precomputed items_by_type (copied so callers can't mutate the shared bucket)."""
    return set(items_by_type.get(t, set()))


class KARTestBase(WorldTestBase):
    game = "Kirby Air Ride"
    world: "KARWorld"

    def setUp(self) -> None:
        super().setUp()
        # Main.py normally pushes start_inventory between generate_early and the rest,
        # but the test framework's gen_steps skips that. Push them here so tests that
        # use start_inventory behave like a real generation.
        if not getattr(self, "constructed", False):
            return
        for item_name, count in self.world.options.start_inventory.value.items():
            for _ in range(count):
                self.multiworld.push_precollected(self.multiworld.worlds[self.player].create_item(item_name))

    def itempool_items(self) -> list:
        """Items in the multiworld itempool belonging to this player."""
        return [item for item in self.multiworld.itempool if item.player == self.player]

    def itempool_names(self) -> list[str]:
        """Names of items in the multiworld itempool belonging to this player."""
        return [item.name for item in self.itempool_items()]

    def precollected_items(self) -> list:
        """Precollected items for this player."""
        return list(self.multiworld.precollected_items[self.player])

    def precollected_names(self) -> list[str]:
        """Names of precollected items for this player."""
        return [item.name for item in self.precollected_items()]

    def world_item_names(self) -> set[str]:
        """Items either in the itempool or precollected (the player will see both)."""
        return set(self.itempool_names()) | set(self.precollected_names())

    def count_in_pool(self, name: str) -> int:
        """Count of items in the itempool with this name. Distinct from the inherited
        `count(...)` helper, which counts the item in the multiworld state."""
        return sum(1 for n in self.itempool_names() if n == name)

    def real_location_names(self) -> set[str]:
        """Names of real (address-bearing) locations for this player."""
        return {loc.name for loc in self.multiworld.get_locations(self.player) if loc.address is not None}

    def event_location_names(self) -> set[str]:
        """Names of event (no-address) locations for this player."""
        return {loc.name for loc in self.multiworld.get_locations(self.player) if loc.address is None}

    def placed_event_items(self) -> set[str]:
        """Names of items placed at event locations (e.g. victory events)."""
        return {
            loc.item.name
            for loc in self.multiworld.get_locations(self.player)
            if loc.address is None and loc.item is not None
        }

    def collect_all_but_victories(self) -> None:
        """Like `collect_all_but([])` but excludes the three `*_VICTORY` event items.
        `get_items()` includes items already placed at event locations, so a bare
        `collect_all_but([])` auto-collects the victory events and makes any subsequent
        `assertBeatable(True)` tautological. Use this for beatability sweeps."""
        self.collect_all_but(
            [
                KARItemName.CITY_TRIAL_VICTORY,
                KARItemName.AIR_RIDE_VICTORY,
                KARItemName.TOP_RIDE_VICTORY,
            ]
        )


# Mode presets. CityTrialGoal defaults to 100_checklist_blocks, AR and TR default
# to none, so CT_ONLY is the empty dict. Other presets explicitly toggle modes.
CT_ONLY: dict = {}

AR_ONLY: dict = {
    "city_trial_goal": CityTrialGoal.option_none,
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
}

TR_ONLY: dict = {
    "city_trial_goal": CityTrialGoal.option_none,
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
}

CT_AND_AR: dict = {
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
}

CT_AND_TR: dict = {
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
}

AR_AND_TR: dict = {
    "city_trial_goal": CityTrialGoal.option_none,
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
}

ALL_MODES: dict = {
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
}
