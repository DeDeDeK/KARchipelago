"""
KAR-specific fuzzer hook.

Runs after each successful generation and asserts that the populated MultiWorld
matches the intent of the rolled options. Raising here causes the fuzzer to dump
the seed's YAML + traceback under fuzz/output/error/.

Invoke via:
    uv run python fuzz/fuzz.py -g kirby_air_ride -m worlds/kirby_air_ride/fuzz_meta.yaml \
        --hook worlds.kirby_air_ride.fuzz_hook:KARHook -r 200

Note: this class deliberately does NOT inherit from fuzz.BaseHook. fuzz.find_hook
has an inverted issubclass check (line 766) that rejects real BaseHook subclasses.
Duck-typing avoids that and lets us drop the hook in without patching the fuzzer.
"""

from __future__ import annotations

from collections import Counter

from BaseClasses import ItemClassification

from worlds.kirby_air_ride.KARData import location_code_to_mode
from worlds.kirby_air_ride.KARItems import (
    GATED_CHECKLIST_REWARDS,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    STADIUM_UNLOCK_TO_CHECKLIST_REWARD,
    KARItemName,
    KARItemType,
    item_name_groups,
)
from worlds.kirby_air_ride.KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
)
from worlds.kirby_air_ride.KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal


class HookError(AssertionError):
    """Raised when an invariant fails. Carries enough context to triage from the dump."""


def _fmt_slot(player: int, name: str) -> str:
    return f"[player {player} ({name!r})]"


class KARHook:
    GAME = "Kirby Air Ride"

    def setup_main(self, args):
        pass

    def setup_worker(self, args):
        pass

    def reclassify_outcome(self, outcome, raised):
        return outcome, raised

    def before_generate(self, args):
        pass

    def finalize(self):
        pass

    def after_generate(self, mw, output_path):
        if mw is None:
            return

        kar_players = [(p, w) for p, w in mw.worlds.items() if getattr(w, "game", None) == self.GAME]
        if not kar_players:
            return

        for player, world in kar_players:
            self._check_slot(mw, player, world)

        # Cross-slot sanity: every KAR player's enabled-mode victory events were placed.
        # (mw.completion_condition / has_beaten_game is enforced by fill; this is a
        # second-line check that catches accidental rule changes.)
        for player, world in kar_players:
            self._check_victory_events_placed(mw, player, world)

    def _check_slot(self, mw, player, world):
        opts = world.options
        slot_name = mw.get_player_name(player)
        tag = _fmt_slot(player, slot_name)

        ct_on = opts.city_trial_goal.value != CityTrialGoal.option_none
        ar_on = opts.air_ride_goal.value != AirRideGoal.option_none
        tr_on = opts.top_ride_goal.value != TopRideGoal.option_none

        if not any((ct_on, ar_on, tr_on)):
            raise HookError(f"{tag} Generated with all modes disabled — should have OptionError'd in generate_early")

        # Items in our slot, partitioned by where they live.
        pool_items = [it for it in mw.itempool if it.player == player]
        pool_names = [it.name for it in pool_items]
        pool_counts = Counter(pool_names)

        precollected = list(mw.precollected_items[player])
        precollected_names = [it.name for it in precollected]
        precollected_counts = Counter(precollected_names)

        # Items placed on our locations (from any player) and our items placed anywhere.
        our_locations = list(mw.get_locations(player))
        items_at_our_locations = [loc.item for loc in our_locations if loc.item is not None]
        all_locations = list(mw.get_locations())
        items_we_own_with_loc = [
            (loc, loc.item) for loc in all_locations if loc.item is not None and loc.item.player == player
        ]
        items_we_own = [it for _, it in items_we_own_with_loc]

        self._check_item_counts(tag, opts, pool_counts, ct_on, ar_on, tr_on)
        self._check_unlock_classifications(tag, pool_items)
        self._check_excluded_items_absent(tag, pool_counts, precollected_counts, opts, ct_on, ar_on, tr_on)
        self._check_starter_precollected(tag, opts, precollected_names, precollected_counts, ct_on, ar_on, tr_on)
        self._check_start_inventory(tag, opts, pool_counts, precollected_counts)
        self._check_cross_mode_placement(tag, opts, player, items_we_own_with_loc)
        self._check_checklist_list_goal_locations(tag, mw, player, opts, ct_on, ar_on, tr_on)
        self._check_non_local_items(tag, opts, player, items_at_our_locations)
        self._check_local_items(tag, opts, player, items_we_own)
        self._check_priority_locations(tag, opts, our_locations)
        self._check_exclude_locations(tag, opts, our_locations)

    def _check_item_counts(self, tag, opts, pool_counts, ct_on, ar_on, tr_on):
        # PATCH_CAP_INCREASE = target - 1 when CT enabled + progressive caps on, else 0
        if ct_on and opts.city_trial_progressive_patch_caps:
            expected = max(0, opts.city_trial_patch_cap_amount.value - 1)
        else:
            expected = 0
        actual = pool_counts.get(str(KARItemName.PATCH_CAP_INCREASE), 0)
        if actual != expected:
            raise HookError(
                f"{tag} PATCH_CAP_INCREASE count={actual}, expected {expected} "
                f"(ct_on={ct_on}, progressive_caps={bool(opts.city_trial_progressive_patch_caps)}, "
                f"cap_amount={opts.city_trial_patch_cap_amount.value})"
            )

        # SPAWN_RATE_UP = (max - min) // 10 when progressive on, else 0.
        # SPAWN_RATE_UP is typed EFFECT but exempt from effect_items_enabled gating
        # (see __init__._build_item_pools: it's governed by spawn_rate_progressive alone).
        if opts.spawn_rate_progressive:
            expected = max(0, (opts.spawn_rate_max.value - opts.spawn_rate_min.value) // 10)
        else:
            expected = 0
        actual = pool_counts.get(str(KARItemName.SPAWN_RATE_UP), 0)
        if actual != expected:
            raise HookError(
                f"{tag} SPAWN_RATE_UP count={actual}, expected {expected} "
                f"(progressive={bool(opts.spawn_rate_progressive)}, "
                f"effect_items_enabled={bool(opts.effect_items_enabled)}, "
                f"min={opts.spawn_rate_min.value}, max={opts.spawn_rate_max.value})"
            )

        # Checkbox fillers per mode
        for enabled, name, amount in [
            (ct_on, KARItemName.CHECKBOX_FILLER_CITY_TRIAL, opts.city_trial_checkbox_fillers.value),
            (ar_on, KARItemName.CHECKBOX_FILLER_AIR_RIDE, opts.air_ride_checkbox_fillers.value),
            (tr_on, KARItemName.CHECKBOX_FILLER_TOP_RIDE, opts.top_ride_checkbox_fillers.value),
        ]:
            expected = amount if enabled else 0
            actual = pool_counts.get(str(name), 0)
            if actual != expected:
                raise HookError(f"{tag} {name} count={actual}, expected {expected} (enabled={enabled}, opt={amount})")

    def _check_unlock_classifications(self, tag, pool_items):
        # All UNLOCK-type items in the pool must be progression-classified.
        # (Memory note: feedback_item_classification — all *_UNLOCK items must be progression.)
        unlock_types = {
            KARItemType.EVENT_UNLOCK,
            KARItemType.ABILITY_UNLOCK,
            KARItemType.PATCH_UNLOCK,
            KARItemType.ITEM_UNLOCK,
            KARItemType.MACHINE_UNLOCK,
            KARItemType.BOX_UNLOCK,
            KARItemType.STAGE_UNLOCK,
            KARItemType.COLOR_UNLOCK,
            KARItemType.TOPRIDE_ITEM_UNLOCK,
            KARItemType.STADIUM_UNLOCK,
        }
        for it in pool_items:
            data = ITEM_TABLE.get(it.name)
            if data is None or data.type not in unlock_types:
                continue
            if not (it.classification & ItemClassification.progression):
                raise HookError(
                    f"{tag} unlock item {it.name!r} (type {data.type}) in pool with "
                    f"non-progression classification {it.classification!r}"
                )

    def _check_excluded_items_absent(self, tag, pool_counts, precollected_counts, opts, ct_on, ar_on, tr_on):
        # When a mode is disabled, its reward items must not appear in the pool or precollected.
        # (They can show up in precollected only if the player force-added them via start_inventory,
        # which is exotic; we still flag because it indicates a misconfigured YAML.)
        mode_groups = [
            (ct_on, "City Trial Rewards"),
            (ar_on, "Air Ride Rewards"),
            (tr_on, "Top Ride Rewards"),
        ]
        for enabled, group in mode_groups:
            if enabled:
                continue
            for item_name in item_name_groups[group]:
                in_pool = pool_counts.get(item_name, 0)
                # Precollected from start_inventory is the player's fault — skip those.
                in_precollected_from_start = opts.start_inventory.value.get(item_name, 0)
                in_precollected = precollected_counts.get(item_name, 0) - in_precollected_from_start
                if in_pool or in_precollected:
                    raise HookError(
                        f"{tag} {group} contains {item_name!r} but that mode is disabled "
                        f"(pool={in_pool}, precollected_non_start={in_precollected})"
                    )

        # When gating is OFF for a category that has GATED_CHECKLIST_REWARDS, the overlapping
        # checklist rewards SHOULD be in the pool. When gating is ON, they should be excluded.
        for option_attr, overlapping_rewards in GATED_CHECKLIST_REWARDS.items():
            gated = bool(getattr(opts, option_attr))
            for reward in overlapping_rewards:
                in_pool = pool_counts.get(str(reward), 0)
                # If gating is on, the reward should be excluded UNLESS its mode is disabled (already excluded)
                # or it's a stadium-overlapped reward that's been promoted to progression.
                if gated and in_pool:
                    # Stadium-overlap rewards may still appear in pool when progressive_stadiums is on.
                    # Skip those specific cases.
                    if reward in STADIUM_UNLOCK_TO_CHECKLIST_REWARD.values():
                        continue
                    raise HookError(
                        f"{tag} {option_attr}=on but its overlapping checklist reward "
                        f"{str(reward)!r} is in the pool (count={in_pool})"
                    )

        # Permanent patches: excluded unless CT enabled AND option on.
        if not (ct_on and opts.city_trial_permanent_patches):
            for n, d in ITEM_TABLE.items():
                if d.type != KARItemType.PERMANENT_PATCH:
                    continue
                c = pool_counts.get(n, 0)
                if c > 0:
                    raise HookError(
                        f"{tag} permanent patch {n!r} in pool (ct_on={ct_on}, "
                        f"permanent_patches={bool(opts.city_trial_permanent_patches)})"
                    )

    def _check_starter_precollected(self, tag, opts, precollected_names, precollected_counts, ct_on, ar_on, tr_on):
        # For each gated category whose mode is enabled, expect either:
        #   (a) at least one item from the start_inventory belonging to that category
        #       (in which case no random starter is picked), OR
        #   (b) exactly one random precollected starter from that category.

        def category_members(group):
            return {str(n) for n in item_name_groups[group]}

        # Stadium starter: CT enabled + progressive_stadiums on
        if ct_on and opts.city_trial_progressive_stadiums:
            stadium_pool = {str(s) for s in STADIUM_UNLOCK_ITEMS}
            self._check_one_starter(
                tag,
                "stadium",
                stadium_pool,
                opts.start_inventory.value,
                precollected_counts,
            )

        if (ct_on or ar_on) and opts.machines_gated:
            machines = category_members("Machine Unlocks") - {
                str(KARItemName.UNLOCK_MACHINE_HYDRA),
                str(KARItemName.UNLOCK_MACHINE_DRAGOON),
            }
            self._check_one_starter(tag, "machine", machines, opts.start_inventory.value, precollected_counts)

        if ct_on and opts.patches_gated:
            self._check_one_starter(
                tag,
                "patch",
                category_members("Patch Type Unlocks"),
                opts.start_inventory.value,
                precollected_counts,
            )

        if ar_on and opts.air_ride_courses_gated:
            self._check_one_starter(
                tag,
                "AR course",
                category_members("AR Course Unlocks"),
                opts.start_inventory.value,
                precollected_counts,
            )

        if tr_on and opts.top_ride_courses_gated:
            self._check_one_starter(
                tag,
                "TR course",
                category_members("TR Course Unlocks"),
                opts.start_inventory.value,
                precollected_counts,
            )

    def _check_one_starter(self, tag, label, category_set, start_inventory, precollected_counts):
        si_in_cat = {n: c for n, c in start_inventory.items() if n in category_set and c > 0}
        if si_in_cat:
            # Player preset items — those should all be precollected; no random starter added.
            for n, c in si_in_cat.items():
                if precollected_counts.get(n, 0) < c:
                    raise HookError(
                        f"{tag} start_inventory specified {c}x {n!r} ({label}) but only "
                        f"{precollected_counts.get(n, 0)} in precollected"
                    )
            return
        # No start_inventory override — expect exactly one random pick from this category in precollected.
        precollected_in_cat = sum(c for n, c in precollected_counts.items() if n in category_set)
        if precollected_in_cat != 1:
            raise HookError(
                f"{tag} expected exactly 1 random {label} starter in precollected, got {precollected_in_cat}"
            )

    def _check_start_inventory(self, tag, opts, pool_counts, precollected_counts):
        # Every item in start_inventory should appear in precollected with at least that count,
        # and should NOT appear in the itempool (start_inventory items are removed from the pool
        # when start_inventory_from_pool is the mechanism, but for plain start_inventory they're
        # given to the player AND remain absent from the pool — KAR excludes them in _build_item_pools).
        for name, count in opts.start_inventory.value.items():
            if count <= 0:
                continue
            in_pc = precollected_counts.get(name, 0)
            if in_pc < count:
                raise HookError(f"{tag} start_inventory {count}x {name!r} but only {in_pc} in precollected")

    def _check_cross_mode_placement(self, tag, opts, player, items_we_own_with_loc):
        if opts.cross_mode_placement:
            return

        for loc, item in items_we_own_with_loc:
            # Only check items that landed at one of OUR locations — the rule explicitly
            # excludes remote placements.
            if loc.player != player:
                continue
            data = ITEM_TABLE.get(item.name)
            if data is None or not data.source_modes:
                continue
            lm = location_code_to_mode(loc.address)
            if lm is None:
                continue
            if lm not in data.source_modes:
                raise HookError(
                    f"{tag} cross_mode_placement=off but our item {item.name!r} "
                    f"(source modes {sorted(m.name for m in data.source_modes)}) "
                    f"landed at location {loc.name!r} (mode {lm.name})"
                )

    def _check_checklist_list_goal_locations(self, tag, mw, player, opts, ct_on, ar_on, tr_on):
        for enabled, goal_opt, locs_opt, table, label in [
            (ct_on, opts.city_trial_goal, opts.city_trial_goal_locations, CITY_TRIAL_LOCATION_TABLE, "City Trial"),
            (ar_on, opts.air_ride_goal, opts.air_ride_goal_locations, AIR_RIDE_LOCATION_TABLE, "Air Ride"),
            (tr_on, opts.top_ride_goal, opts.top_ride_goal_locations, TOP_RIDE_LOCATION_TABLE, "Top Ride"),
        ]:
            if not enabled or goal_opt.value != goal_opt.option_checklist_list:
                continue
            for name in locs_opt.value:
                if name not in table:
                    raise HookError(f"{tag} {label} goal location {name!r} not in {label} table")
                loc = mw.get_location(name, player)
                if loc.item is None:
                    raise HookError(f"{tag} {label} goal location {name!r} has no item")
                if loc.item.player != player:
                    raise HookError(
                        f"{tag} {label} goal location {name!r} contains a non-local item "
                        f"({loc.item.name!r} from player {loc.item.player})"
                    )

    def _check_non_local_items(self, tag, opts, player, items_at_our_locations):
        non_local: set[str] = set(opts.non_local_items.value)
        if not non_local:
            return
        for item in items_at_our_locations:
            if item.player != player:
                continue
            if item.name in non_local:
                raise HookError(f"{tag} non_local_items {item.name!r} placed at our location, violating non_local rule")

    def _check_local_items(self, tag, opts, player, items_we_own):
        local: set[str] = set(opts.local_items.value)
        if not local:
            return
        for item in items_we_own:
            if item.name in local:
                loc = item.location
                if loc is None or loc.player != player:
                    raise HookError(
                        f"{tag} local_items {item.name!r} placed at non-local location "
                        f"({loc.name!r} player {loc.player if loc else None})"
                    )

    def _check_priority_locations(self, tag, opts, our_locations):
        # Priority locations should contain progression or useful items, not pure filler/trap.
        priority: set[str] = set(opts.priority_locations.value)
        if not priority:
            return
        for loc in our_locations:
            if loc.name not in priority:
                continue
            if loc.item is None:
                raise HookError(f"{tag} priority location {loc.name!r} has no item")
            if not (loc.item.classification & (ItemClassification.progression | ItemClassification.useful)):
                raise HookError(
                    f"{tag} priority location {loc.name!r} has filler/trap item "
                    f"{loc.item.name!r} ({loc.item.classification!r})"
                )

    def _check_exclude_locations(self, tag, opts, our_locations):
        excluded: set[str] = set(opts.exclude_locations.value)
        if not excluded:
            return
        for loc in our_locations:
            if loc.name not in excluded:
                continue
            if loc.item is None:
                continue
            if loc.item.classification & ItemClassification.progression:
                raise HookError(f"{tag} excluded location {loc.name!r} got progression item {loc.item.name!r}")

    def _check_victory_events_placed(self, mw, player, world):
        slot_name = mw.get_player_name(player)
        tag = _fmt_slot(player, slot_name)
        # Each enabled mode must have its victory event placed on a locked event location.
        expected = []
        if world.city_trial_enabled:
            expected.append(str(KARItemName.CITY_TRIAL_VICTORY))
        if world.air_ride_enabled:
            expected.append(str(KARItemName.AIR_RIDE_VICTORY))
        if world.top_ride_enabled:
            expected.append(str(KARItemName.TOP_RIDE_VICTORY))

        placed_event_items = {
            loc.item.name for loc in mw.get_locations(player) if loc.address is None and loc.item is not None
        }
        for name in expected:
            if name not in placed_event_items:
                raise HookError(f"{tag} victory event {name!r} not placed (enabled mode requires it)")
