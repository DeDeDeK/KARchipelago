"""
shuffle_checklist_rewards tests.

The option governs whether native checklist reward items are shuffled into the multiworld (on, default)
or pinned back onto the boxes that award them in the base game (off). Pinning is pre-placement: each
in-scope reward is locked onto its native box and dropped from the pool, so the counts self-balance.

In scope are the non-progression rewards (reward_pool) plus the six progression part markers. A reward
whose native box is excluded is pinned only when it is filler, since an excluded box accepts only
filler; a useful/progression reward there floats and is placed by normal fill.

These tests set checklist_rewards_gated on (off by default), since the shuffle option only has the
non-progression rewards to act on when they are gated into the pool.
"""

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARItems import CHECKLIST_REWARD_TYPES, ITEM_TABLE
from ..KARLocations import LOCATION_TABLE, NATIVE_REWARD_TO_LOCATION
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

# Runtime base is `object` so the mixin is not collected as a standalone test (it would run shuffle-on
# and fail its shuffle-off asserts). Under type checking it resolves as KARTestBase so self.* checks.
_MixinBase = KARTestBase if TYPE_CHECKING else object

_SHUFFLE_OFF = {"shuffle_checklist_rewards": Toggle.option_false}
_SHUFFLE_ON = {"shuffle_checklist_rewards": Toggle.option_true}
# Rewards are off by default; gate them into the pool so the shuffle option has something to act on.
_GATED_ON = {"checklist_rewards_gated": Toggle.option_true}


def _legendary_parts() -> set[str]:
    """The six progression Dragoon/Hydra part-marker reward items."""
    return {
        str(name)
        for name, data in ITEM_TABLE.items()
        if data.type in CHECKLIST_REWARD_TYPES and (data.classification & ItemClassification.progression)
    }


class _ShuffleOffInvariantMixin(_MixinBase):
    """Shared assertions for any shuffle-off config. Subclasses set `options`."""

    def _in_scope_rewards(self) -> set[str]:
        """Rewards the world actually placed/keeps: pinned + still-floating reward_pool + the part
        markers still in progression_pool. Excludes rewards dropped entirely (overlapping / mode-off)."""
        world = self.world
        in_scope = set(world.pinned_native_rewards.values()) | set(world.reward_pool)
        in_scope |= {n for n in world.progression_pool if ITEM_TABLE[n].type in CHECKLIST_REWARD_TYPES}
        return in_scope

    def _default_location_names(self) -> set[str]:
        # Mirrors create_items' own union, Archipelago included: an AP box hosts other modes' shuffled
        # rewards, so leaving it out would understate the default budget in an AP-enabled seed.
        world = self.world
        names: set[str] = set()
        for enabled, default_locations in (
            (world.city_trial_enabled, world.city_trial_default_locations),
            (world.air_ride_enabled, world.air_ride_default_locations),
            (world.top_ride_enabled, world.top_ride_default_locations),
            (world.archipelago_enabled, world.archipelago_default_locations),
        ):
            if enabled:
                names |= default_locations
        return names - set(world.goal_locations_to_exclude) - set(world.options.exclude_locations)

    def test_pins_are_locked_local_and_correct(self):
        """Every recorded pin holds exactly that reward, locked, and owned by this player."""
        self.assertTrue(self.world.pinned_native_rewards, "shuffle off should pin at least one reward")
        for loc_name, reward in self.world.pinned_native_rewards.items():
            loc = self.world.get_location(loc_name)
            self.assertTrue(loc.locked, f"{loc_name} should be locked")
            item = loc.item
            self.assertIsNotNone(item, f"{loc_name} should hold an item")
            assert item is not None
            self.assertEqual(item.name, reward, f"{loc_name} should hold its native reward")
            self.assertEqual(item.player, self.player, f"{loc_name} pin should be local")
            self.assertEqual(NATIVE_REWARD_TO_LOCATION[reward], loc_name, "pin must be on the reward's native box")

    def test_needs_default_reward_on_default_box_is_pinned(self):
        """A useful/progression reward whose native box is a real default box is always pinned there:
        it is a needs-default item, so pinning is capacity-neutral. (Filler rewards on default boxes are
        budget-limited and may float, so they are excluded from this invariant.)"""
        default_names = self._default_location_names()
        for reward in self._in_scope_rewards():
            cls = ITEM_TABLE[reward].classification
            if not (cls & (ItemClassification.useful | ItemClassification.progression)):
                continue  # filler-on-default is budgeted, may float
            box = NATIVE_REWARD_TO_LOCATION[reward]
            if box not in default_names:
                continue
            self.assertIn(box, self.world.pinned_native_rewards, f"{reward} on default box {box} must be pinned")
            self.assertEqual(self.world.pinned_native_rewards[box], reward)

    def test_filler_on_excluded_native_box_is_pinned(self):
        """A filler reward whose native box is excluded is always pinned (capacity-neutral: excluded
        boxes only take filler anyway)."""
        default_names = self._default_location_names()
        excluded_names = set()
        world = self.world
        for enabled, excluded_locations in (
            (world.city_trial_enabled, world.city_trial_excluded_locations),
            (world.air_ride_enabled, world.air_ride_excluded_locations),
            (world.top_ride_enabled, world.top_ride_excluded_locations),
            (world.archipelago_enabled, world.archipelago_excluded_locations),
        ):
            if enabled:
                excluded_names |= excluded_locations
        excluded_names |= set(world.options.exclude_locations)
        excluded_names -= set(world.goal_locations_to_exclude)
        for reward in self._in_scope_rewards():
            cls = ITEM_TABLE[reward].classification
            if cls & (ItemClassification.useful | ItemClassification.progression):
                continue
            box = NATIVE_REWARD_TO_LOCATION[reward]
            if box not in excluded_names or box in default_names:
                continue
            self.assertIn(box, self.world.pinned_native_rewards, f"filler {reward} on excluded box {box} must pin")

    def test_no_pinned_reward_left_in_pool(self):
        """A pinned reward must not also be minted into the itempool (would double the unique unlock)."""
        pinned = set(self.world.pinned_native_rewards.values())
        self.assertEqual(pinned & set(self.world.reward_pool), set())
        self.assertEqual(pinned & set(self.world.progression_pool), set())

    def test_pool_size_matches_unfilled_locations(self):
        """Pinning locks boxes out of the placeable count, so the minted pool still exactly fills the
        remaining (unlocked) real locations."""
        unfilled = [
            loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None and not loc.locked
        ]
        self.assertEqual(len(self.itempool_items()), len(unfilled))


class TestShuffleOffAllModes(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**ALL_MODES, **_GATED_ON, **_SHUFFLE_OFF}

    def test_all_legendary_parts_accounted_for(self):
        """Each of the six progression part markers is either pinned to its native box or floating
        (native box excluded); none vanish."""
        parts = _legendary_parts()
        pinned = set(self.world.pinned_native_rewards.values())
        floating = set(self.world.progression_pool)
        for part in parts:
            self.assertTrue(part in pinned or part in floating, f"{part} must be pinned or floating")


class TestShuffleOffCTOnly(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**CT_ONLY, **_GATED_ON, **_SHUFFLE_OFF}


class TestShuffleOffAROnly(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**AR_ONLY, **_GATED_ON, **_SHUFFLE_OFF}


class TestShuffleOffTROnly(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**TR_ONLY, **_GATED_ON, **_SHUFFLE_OFF}


class TestShuffleOnDoesNotPin(KARTestBase):
    """Shuffle on (default): nothing is pinned and the rewards live in the itempool to be shuffled."""

    options = {**ALL_MODES, **_GATED_ON, **_SHUFFLE_ON}

    def test_nothing_pinned(self):
        self.assertEqual(self.world.pinned_native_rewards, {})

    def test_no_native_box_locked(self):
        reward_boxes = {str(loc) for loc, data in LOCATION_TABLE.items() if data.native_reward is not None}
        locked_reward_boxes = [
            loc.name for loc in self.multiworld.get_locations(self.player) if loc.name in reward_boxes and loc.locked
        ]
        self.assertEqual(locked_reward_boxes, [])


class TestShuffleOffKnownPin(KARTestBase):
    """A spot-check on a known vanilla mapping: 'race over 60 miles!' awards Filler Box 1."""

    options = {**CT_ONLY, **_GATED_ON, **_SHUFFLE_OFF}

    def test_race_60_miles_holds_filler_box_1(self):
        from ..KARItems import KARItemName
        from ..KARLocations import CTLocation

        loc = self.world.get_location(CTLocation.RACE_60_MILES)
        self.assertTrue(loc.locked)
        item = loc.item
        assert item is not None
        self.assertEqual(item.name, str(KARItemName.CT_REWARD_FILLER_BOX_1))
