"""
shuffle_checklist_rewards tests (Part 2).

The option governs whether the game's native checklist reward items are shuffled into the
multiworld (on, default) or pinned back onto the boxes that award them in the base game (off).
Pinning is pre-placement: create_items place_locked_item's each in-scope reward onto its native
box and drops it from the pool, so the item/location counts self-balance.

In scope are the non-progression rewards (reward_pool) plus the six progression Dragoon/Hydra
part markers. Guard: a reward whose native box is excluded under the current flags is only pinned
when it is filler (an excluded box accepts only filler during fill); a useful/progression reward
on an excluded box is left to float and is placed by normal fill.

cross_mode_placement is independent: it locks only progression to its source mode(s). With shuffle
on, rewards stay in the pool and float per that setting as before; with shuffle off they are pinned
regardless of cross_mode_placement. Each class here also runs the inherited test_fill, which does a
full distribute_items_restrictive and a beatability sweep.
"""

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification
from Options import Toggle

from ..KARItems import CHECKLIST_REWARD_TYPES, ITEM_TABLE
from ..KARLocations import LOCATION_TABLE, NATIVE_REWARD_TO_LOCATION
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

# Runtime base is `object` so the mixin is not collected as a standalone test (it would run with
# default shuffle-on options and fail its shuffle-off asserts). Under type checking it resolves as
# KARTestBase so `self.world` / `self.multiworld` / helper methods type-check.
_MixinBase = KARTestBase if TYPE_CHECKING else object

_SHUFFLE_OFF = {"shuffle_checklist_rewards": Toggle.option_false}
_SHUFFLE_ON = {"shuffle_checklist_rewards": Toggle.option_true}


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
        world = self.world
        names: set[str] = set()
        if world.city_trial_enabled:
            names |= world.city_trial_default_locations
        if world.air_ride_enabled:
            names |= world.air_ride_default_locations
        if world.top_ride_enabled:
            names |= world.top_ride_default_locations
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
        if world.city_trial_enabled:
            excluded_names |= world.city_trial_excluded_locations
        if world.air_ride_enabled:
            excluded_names |= world.air_ride_excluded_locations
        if world.top_ride_enabled:
            excluded_names |= world.top_ride_excluded_locations
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
    options = {**ALL_MODES, **_SHUFFLE_OFF}

    def test_all_legendary_parts_accounted_for(self):
        """Each of the six progression part markers is either pinned to its native box or floating
        (native box excluded); none vanish."""
        parts = _legendary_parts()
        pinned = set(self.world.pinned_native_rewards.values())
        floating = set(self.world.progression_pool)
        for part in parts:
            self.assertTrue(part in pinned or part in floating, f"{part} must be pinned or floating")


class TestShuffleOffAllModesCrossOff(_ShuffleOffInvariantMixin, KARTestBase):
    """Shuffle off composes with cross-mode off: parts (CT progression) pin on CT boxes, and the full
    fill (inherited test_fill) still produces a beatable seed."""

    options = {**ALL_MODES, **_SHUFFLE_OFF, "cross_mode_placement": Toggle.option_false}


class TestShuffleOffCTOnly(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**CT_ONLY, **_SHUFFLE_OFF}


class TestShuffleOffAROnly(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**AR_ONLY, **_SHUFFLE_OFF}


class TestShuffleOffTROnly(_ShuffleOffInvariantMixin, KARTestBase):
    options = {**TR_ONLY, **_SHUFFLE_OFF}


class TestShuffleOnDoesNotPin(KARTestBase):
    """Shuffle on (default): nothing is pinned and the rewards live in the itempool to be shuffled."""

    options = {**ALL_MODES, **_SHUFFLE_ON}

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

    options = {**CT_ONLY, **_SHUFFLE_OFF}

    def test_race_60_miles_holds_filler_box_1(self):
        from ..KARItems import KARItemName
        from ..KARLocations import CTLocation

        loc = self.world.get_location(CTLocation.RACE_60_MILES)
        self.assertTrue(loc.locked)
        item = loc.item
        assert item is not None
        self.assertEqual(item.name, str(KARItemName.CT_REWARD_FILLER_BOX_1))


class TestShuffleOnCrossOffConfinesRewards(KARTestBase):
    """shuffle on + cross off: rewards are NOT pinned (still shuffled by fill), but the cross-mode
    item-rule keeps each local reward within its native mode. After a full distribute_items_restrictive
    every local reward sits on a box of its source mode. (Solo seed, so no reward can export to another
    world; all stay in KAR and must therefore be in-mode.)"""

    options = {**ALL_MODES, **_SHUFFLE_ON, "cross_mode_placement": Toggle.option_false}

    def test_nothing_pinned(self):
        self.assertEqual(self.world.pinned_native_rewards, {})

    def test_rewards_land_in_native_mode(self):
        from Fill import distribute_items_restrictive

        from ..KARData import location_code_to_mode

        distribute_items_restrictive(self.multiworld)
        checked = 0
        for loc in self.multiworld.get_locations():
            item = loc.item
            if item is None or item.player != self.player or loc.address is None:
                continue
            data = ITEM_TABLE.get(item.name)
            if data is None or data.type not in CHECKLIST_REWARD_TYPES:
                continue
            lm = location_code_to_mode(loc.address)
            self.assertIn(
                lm,
                data.source_modes,
                f"{item.name} (modes {sorted(m.name for m in data.source_modes)}) landed on "
                f"{loc.name} (mode {lm.name if lm else None}) under cross-off",
            )
            checked += 1
        self.assertGreater(checked, 0, "expected at least one shuffled reward to verify")
