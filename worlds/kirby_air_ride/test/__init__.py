from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from random import Random
from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from test.bases import WorldTestBase

from ..KARItems import GATING_CATEGORIES, KARItemName, KARItemType, items_by_type
from ..KAROptions import AirRideGoal, ArchipelagoGoal, CityTrialGoal, TopRideGoal

if TYPE_CHECKING:
    from .. import KARWorld


def items_of_type(t: KARItemType) -> set[str]:
    """All item names in ITEM_TABLE whose type matches `t`, copied so callers can't mutate the shared bucket."""
    return set(items_by_type.get(t, set()))


def names(items: Iterable) -> set[str]:
    """Plain-str view of a collection of KARItemName / KARLocation members."""
    return {str(item) for item in items}


# The checklist rewards each gating category subsumes; always excluded from the pool, gate on or off.
OVERLAP_REWARDS: dict[str, frozenset] = {cat.option: cat.overlapping_rewards for cat in GATING_CATEGORIES}


class KARTestBase(WorldTestBase):
    game = "Kirby Air Ride"
    world: "KARWorld"

    def setUp(self) -> None:
        super().setUp()
        # gen_steps skips the start_inventory push real generation does; do it here so start_inventory
        # tests behave like a real generation.
        if not getattr(self, "constructed", False):
            return
        for item_name, count in self.world.options.start_inventory.value.items():
            for _ in range(count):
                self.multiworld.push_precollected(self.multiworld.worlds[self.player].create_item(item_name))

    def itempool_items(self) -> list:
        return [item for item in self.multiworld.itempool if item.player == self.player]

    def itempool_names(self) -> list[str]:
        return [item.name for item in self.itempool_items()]

    def precollected_names(self) -> list[str]:
        return [item.name for item in self.multiworld.precollected_items[self.player]]

    def world_item_names(self) -> set[str]:
        """Items either in the itempool or precollected - everything the player can end up holding."""
        return set(self.itempool_names()) | set(self.precollected_names())

    def precollected_in(self, group: Iterable[str]) -> list[str]:
        """The precollected items belonging to `group` - one starter per gated category."""
        return [name for name in self.precollected_names() if name in set(group)]

    def count_in_pool(self, name: str) -> int:
        """Copies of `name` in the itempool, as distinct from the inherited `count(...)`, which reads state."""
        return sum(1 for n in self.itempool_names() if n == name)

    def real_location_names(self) -> set[str]:
        return {loc.name for loc in self.multiworld.get_locations(self.player) if loc.address is not None}

    def event_location_names(self) -> set[str]:
        return {loc.name for loc in self.multiworld.get_locations(self.player) if loc.address is None}

    def placed_event_items(self) -> set[str]:
        """Names of the items placed at event locations, e.g. the per-mode victories."""
        return {
            loc.item.name
            for loc in self.multiworld.get_locations(self.player)
            if loc.address is None and loc.item is not None
        }

    def placeable_locations(self) -> list:
        """The locations create_items has to fill: real, unlocked ones."""
        return [loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked]

    def collect_all_but_victories(self) -> None:
        """`collect_all_but([])` minus the `*_VICTORY` events, which are already placed and would make any
        following `assertBeatable(True)` tautological."""
        self.collect_all_but(
            [
                KARItemName.CITY_TRIAL_VICTORY,
                KARItemName.AIR_RIDE_VICTORY,
                KARItemName.TOP_RIDE_VICTORY,
                KARItemName.ARCHIPELAGO_VICTORY,
            ]
        )

    def assert_victory_needs_all(self, keys: Iterable[str], victory: str) -> None:
        """Collect everything but `keys` and the `victory` event item, then hand the keys over one at a
        time: the seed stays unbeatable until the last of them arrives."""
        keys = list(keys)
        self.collect_all_but([*keys, victory])
        self.assertBeatable(False)
        for key in keys[:-1]:
            self.collect_by_name(key)
            self.assertBeatable(False)
        self.collect_by_name(keys[-1])
        self.assertBeatable(True)

    def state_without(self, withheld: Iterable[str]) -> CollectionState:
        """Everything collected except `withheld`, precollected starter copies stripped out too."""
        held_out = names(withheld)
        state = CollectionState(self.multiworld)
        self.collect_all_but(held_out, state)
        for item in self.multiworld.precollected_items[self.player]:
            if item.name in held_out:
                state.remove(item)
        return state

    def state_with(self, *item_names: str) -> CollectionState:
        """A fresh state holding only the named items (plus whatever is precollected)."""
        state = CollectionState(self.multiworld)
        for name in item_names:
            state.collect(self.world.create_item(name), prevent_sweep=True)
        return state

    def reaches(self, state: CollectionState, location: str) -> bool:
        return state.can_reach(location, "Location", self.player)


# Mode presets. CityTrialGoal defaults to 100_checklist_blocks and AR/TR to none, so CT_ONLY is empty.
CT_ONLY: dict = {}

AR_ONLY: dict = {
    "city_trial_goal": CityTrialGoal.option_none,
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
}

TR_ONLY: dict = {
    "city_trial_goal": CityTrialGoal.option_none,
    "top_ride_goal": TopRideGoal.option_100_checklist_blocks,
}

# The AP checklist holds 52 boxes, so its goal amount is well under what the other modes ask for.
AP_ONLY: dict = {
    "city_trial_goal": CityTrialGoal.option_none,
    "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
    "archipelago_checklist_amount": 5,
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


class RecordingRandom(Random):
    """Stand-in for `world.random` recording the list `choice` was offered and returning its first entry,
    so "is X barred from this pick?" is answered exactly rather than sampled. The record is `offers`, not
    `choices` - Random.choices() is a real method and shadowing it would break callers."""

    def __init__(self, seed: int = 0) -> None:
        super().__init__(seed)
        self.offers: list[list] = []

    def choice(self, seq):
        offered = list(seq)
        self.offers.append(offered)
        return offered[0]


@contextmanager
def recording_random(world: "KARWorld") -> Iterator[RecordingRandom]:
    """Swap `world.random` for a RecordingRandom for the duration of the block, then put it back."""
    original = world.random
    recorder = RecordingRandom()
    world.random = recorder
    try:
        yield recorder
    finally:
        world.random = original
