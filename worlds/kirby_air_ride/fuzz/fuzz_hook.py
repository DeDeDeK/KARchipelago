"""
KAR-specific fuzzer hook.

Runs after each successful generation and asserts that the populated MultiWorld matches the intent of
the rolled options. Raising here makes the fuzzer dump the seed's YAML + traceback under
fuzz/output/error/. Invoke via:

    uv run python fuzz/fuzz.py -g kirby_air_ride -m worlds/kirby_air_ride/fuzz/fuzz_meta.yaml \
        --hook worlds.kirby_air_ride.fuzz.fuzz_hook:KARHook -r 200

Deliberately does NOT inherit from fuzz.BaseHook: fuzz.find_hook has an inverted issubclass check that
rejects real BaseHook subclasses, so duck-typing drops the hook in without patching the fuzzer.
"""

from __future__ import annotations

from collections import Counter

from BaseClasses import ItemClassification

from worlds.kirby_air_ride.KARItems import (
    ALLOWED_ITEM_CATEGORY_ITEMS,
    CHARGE_DEPENDENT_MACHINES,
    CHECKLIST_REWARD_TYPES,
    GATING_CATEGORIES,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    KARItemGroup,
    KARItemName,
    item_name_groups,
    items_by_type,
)
from worlds.kirby_air_ride.KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    NATIVE_REWARD_TO_LOCATION,
    TOP_RIDE_LOCATION_TABLE,
)
from worlds.kirby_air_ride.KAROptions import AirRideGoal, ArchipelagoGoal, CityTrialGoal, TopRideGoal


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

        # Cross-slot sanity: every KAR player's enabled-mode victory events were placed. Fill already
        # enforces the completion condition; this is a second line that catches accidental rule changes.
        for player, world in kar_players:
            self._check_victory_events_placed(mw, player, world)

    def _check_slot(self, mw, player, world):
        opts = world.options
        slot_name = mw.get_player_name(player)
        tag = _fmt_slot(player, slot_name)

        ct_on = opts.city_trial_goal.value != CityTrialGoal.option_none
        ar_on = opts.air_ride_goal.value != AirRideGoal.option_none
        tr_on = opts.top_ride_goal.value != TopRideGoal.option_none
        ap_on = opts.archipelago_goal.value != ArchipelagoGoal.option_none

        if not any((ct_on, ar_on, tr_on, ap_on)):
            raise HookError(f"{tag} Generated with all modes disabled, should have OptionError'd in generate_early")

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

        # Every distinct item this player owns, counted once, whether still loose in the itempool or
        # already placed - fill and _pin_native_rewards both move items out of the pool, so a pool-only
        # Counter would miss them. Union by object identity so a pool+placed item is not double counted.
        owned_by_id = {id(it): it for it in pool_items}
        for it in items_we_own:
            owned_by_id[id(it)] = it
        owned_counts = Counter(it.name for it in owned_by_id.values())

        self._check_item_counts(tag, opts, pool_counts, ct_on, ar_on, tr_on, ap_on)
        self._check_generic_filler_present(tag, world)
        self._check_unlock_classifications(tag, pool_items)
        self._check_excluded_items_absent(tag, pool_counts, precollected_counts, opts, ct_on, ar_on, tr_on)
        self._check_reward_uniqueness(tag, world, owned_counts)
        self._check_checklist_rewards_gated(tag, opts, pool_counts, precollected_counts)
        self._check_pinned_native_rewards(tag, mw, player, world, pool_counts)
        self._check_starter_precollected(tag, opts, precollected_names, precollected_counts, ct_on, ar_on, tr_on)
        self._check_start_inventory(tag, opts, pool_counts, precollected_counts)
        self._check_checklist_list_goal_locations(tag, mw, player, opts, ct_on, ar_on, tr_on, ap_on)
        self._check_non_local_items(tag, opts, player, items_at_our_locations)
        self._check_local_items(tag, opts, player, items_we_own)
        self._check_priority_locations(tag, opts, our_locations)
        self._check_exclude_locations(tag, opts, our_locations)

    def _check_item_counts(self, tag, opts, pool_counts, ct_on, ar_on, tr_on, ap_on):
        # PATCH_CAP_INCREASE = max - min when CT enabled, else 0
        if ct_on:
            expected = max(0, opts.city_trial_patch_cap_max.value - opts.city_trial_patch_cap_min.value)
        else:
            expected = 0
        actual = pool_counts.get(str(KARItemName.PATCH_CAP_INCREASE), 0)
        if actual != expected:
            raise HookError(
                f"{tag} PATCH_CAP_INCREASE count={actual}, expected {expected} "
                f"(ct_on={ct_on}, patch_cap_min={opts.city_trial_patch_cap_min.value}, "
                f"patch_cap_max={opts.city_trial_patch_cap_max.value})"
            )

        # SPAWN_RATE_UP = (max - min) // 10, else 0. Its source_modes are {CITYTRIAL, TOPRIDE}, so the
        # world's source-mode backstop drops it entirely when neither is enabled. Mirror that here.
        if ct_on or tr_on:
            expected = max(0, (opts.spawn_rate_max.value - opts.spawn_rate_min.value) // 10)
        else:
            expected = 0
        actual = pool_counts.get(str(KARItemName.SPAWN_RATE_UP), 0)
        if actual != expected:
            raise HookError(
                f"{tag} SPAWN_RATE_UP count={actual}, expected {expected} "
                f"(min={opts.spawn_rate_min.value}, max={opts.spawn_rate_max.value})"
            )

        # Checkbox fillers per mode
        for enabled, name, amount in [
            (ct_on, KARItemName.CHECKBOX_FILLER_CITY_TRIAL, opts.city_trial_checkbox_fillers.value),
            (ar_on, KARItemName.CHECKBOX_FILLER_AIR_RIDE, opts.air_ride_checkbox_fillers.value),
            (tr_on, KARItemName.CHECKBOX_FILLER_TOP_RIDE, opts.top_ride_checkbox_fillers.value),
            (ap_on, KARItemName.CHECKBOX_FILLER_ARCHIPELAGO, opts.archipelago_checkbox_fillers.value),
        ]:
            expected = amount if enabled else 0
            actual = pool_counts.get(str(name), 0)
            if actual != expected:
                raise HookError(f"{tag} {name} count={actual}, expected {expected} (enabled={enabled}, opt={amount})")

    def _check_generic_filler_present(self, tag, world):
        # Big Kirby / Small Kirby are immune to allowed_items (FILLER is not a category) and carry
        # _ALL_MODES, and every KAR slot has >=1 mode enabled, so both are always in filler_pool. This is
        # the invariant that makes filler starvation impossible.
        for name in (KARItemName.BIG_KIRBY, KARItemName.SMALL_KIRBY):
            if str(name) not in world.filler_pool:
                raise HookError(
                    f"{tag} cosmetic filler {str(name)!r} missing from filler_pool; it must always be "
                    f"present so filler is never starved"
                )

    def _check_reward_uniqueness(self, tag, world, owned_counts):
        # Checklist rewards are unique one-time unlocks, not draw-with-replacement filler: each one routed
        # to reward_pool is minted exactly once, so it must appear exactly once among the owned items.
        # Pinned rewards (shuffle off) leave reward_pool, so see _check_pinned_native_rewards for those.
        for name in world.reward_pool:
            data = ITEM_TABLE.get(name)
            if data is None:
                continue
            count = owned_counts.get(str(name), 0)
            if count != 1:
                kind = "useful" if data.classification & ItemClassification.useful else "filler"
                raise HookError(
                    f"{tag} {kind} checklist reward {str(name)!r} count={count}, expected exactly 1 "
                    f"(rewards must be unique one-time items)"
                )

    def _check_checklist_rewards_gated(self, tag, opts, pool_counts, precollected_counts):
        # checklist_rewards_gated off: the mod unlocks every non-progression reward at connect, so none
        # may appear in the itempool or precollected. The 6 progression part markers are unaffected.
        if opts.checklist_rewards_gated:
            return
        offenders = []
        for name, data in ITEM_TABLE.items():
            if data.type not in CHECKLIST_REWARD_TYPES:
                continue
            if data.classification & ItemClassification.progression:
                continue
            n = pool_counts.get(str(name), 0) + precollected_counts.get(str(name), 0)
            if n:
                offenders.append((str(name), n))
        if offenders:
            raise HookError(
                f"{tag} checklist_rewards_gated off but {len(offenders)} non-progression checklist "
                f"reward(s) still present (e.g. {offenders[:5]})"
            )

    def _check_pinned_native_rewards(self, tag, mw, player, world, pool_counts):
        # shuffle_checklist_rewards off pins each in-scope reward onto the box that awards it in the base
        # game (place_locked_item) and drops it from the pool. With shuffle on, nothing is pinned.
        pins = getattr(world, "pinned_native_rewards", {})
        shuffle_off = not world.options.shuffle_checklist_rewards
        if not shuffle_off:
            if pins:
                raise HookError(f"{tag} shuffle_checklist_rewards on but {len(pins)} rewards were pinned")
            return

        for loc_name, reward in pins.items():
            if NATIVE_REWARD_TO_LOCATION.get(str(reward)) != loc_name:
                raise HookError(f"{tag} pin {str(reward)!r} on {loc_name!r} is not that reward's native box")
            loc = mw.get_location(loc_name, player)
            if not loc.locked:
                raise HookError(f"{tag} pinned reward location {loc_name!r} is not locked")
            if loc.item is None or loc.item.player != player or loc.item.name != str(reward):
                placed = None if loc.item is None else (loc.item.player, loc.item.name)
                raise HookError(f"{tag} pinned box {loc_name!r} should hold local {str(reward)!r}, holds {placed}")
            # A pinned reward is the unique copy: _pin_native_rewards removed it from reward_pool and
            # rewards never enter the filler pool, so it must not also be minted into the itempool.
            extra = pool_counts.get(str(reward), 0)
            if extra:
                raise HookError(
                    f"{tag} pinned reward {str(reward)!r} also appears {extra}x in the pool "
                    f"(pinned rewards must be unique)"
                )

    def _check_unlock_classifications(self, tag, pool_items):
        # All UNLOCK-type items in the pool must be progression-classified. Every gated unlock type comes
        # from GATING_CATEGORIES, stadiums included.
        unlock_types = {cat.item_type for cat in GATING_CATEGORIES}
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
        # When a mode is disabled, its reward items must not appear in the pool or precollected. Only a
        # start_inventory force-add could put one in precollected, which is a misconfigured YAML.
        mode_groups = [
            (ct_on, KARItemGroup.CT_REWARDS),
            (ar_on, KARItemGroup.AR_REWARDS),
            (tr_on, KARItemGroup.TR_REWARDS),
        ]
        for enabled, group in mode_groups:
            if enabled:
                continue
            for item_name in item_name_groups[group]:
                in_pool = pool_counts.get(item_name, 0)
                # Precollected from start_inventory is the player's fault, skip those.
                in_precollected_from_start = opts.start_inventory.value.get(item_name, 0)
                in_precollected = precollected_counts.get(item_name, 0) - in_precollected_from_start
                if in_pool or in_precollected:
                    raise HookError(
                        f"{tag} {group} contains {item_name!r} but that mode is disabled "
                        f"(pool={in_pool}, precollected_non_start={in_precollected})"
                    )

        # Overlapping checklist rewards are excluded whenever the mod handles their category directly:
        # UNLOCK items deliver it when the gate is ON, the mod pre-unlocks at connect when OFF.
        for cat in GATING_CATEGORIES:
            if not cat.overlapping_rewards:
                continue
            gated = bool(getattr(opts, cat.option))
            for reward in cat.overlapping_rewards:
                in_pool = pool_counts.get(str(reward), 0)
                if in_pool:
                    raise HookError(
                        f"{tag} overlapping checklist reward {str(reward)!r} for {cat.option} is in the "
                        f"pool (count={in_pool}); the mod handles its category directly "
                        f"({cat.option}={gated}), so the reward should be excluded"
                    )

        # allowed_items: a category absent from the set removes all of its non-trap items from the pool.
        # (Trap items of these types stay governed by `traps`, so ALLOWED_ITEM_CATEGORY_ITEMS omits them.)
        allowed = opts.allowed_items.value
        for category, names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            if category in allowed:
                continue
            for n in names:
                c = pool_counts.get(n, 0)
                if c > 0:
                    raise HookError(
                        f"{tag} {category} item {n!r} in pool (count={c}) but that category is disabled "
                        f"via allowed_items"
                    )

    def _check_starter_precollected(self, tag, opts, precollected_names, precollected_counts, ct_on, ar_on, tr_on):
        # For each gated category whose mode is enabled, expect either a start_inventory item from that
        # category (in which case no random starter is picked), or exactly one random precollected starter.

        def category_members(group):
            return {str(n) for n in item_name_groups[group]}

        # Stadium starter: CT enabled + progressive_stadiums on
        if ct_on and opts.city_trial_stadiums_gated:
            stadium_pool = {str(s) for s in STADIUM_UNLOCK_ITEMS}
            # Handing over the goal stadium for free would hand over the goal, so the world drops it
            # from the pick when beat_king_dedede is the City Trial goal.
            beat_dedede = opts.city_trial_goal.value == opts.city_trial_goal.option_beat_king_dedede
            self._check_one_starter(
                tag,
                "stadium",
                stadium_pool,
                opts.start_inventory.value,
                precollected_counts,
                ineligible={str(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)} if beat_dedede else frozenset(),
            )

        if (ct_on or ar_on) and opts.machines_gated:
            machines = category_members(KARItemGroup.MACHINE_UNLOCKS) - {
                str(KARItemName.UNLOCK_MACHINE_HYDRA),
                str(KARItemName.UNLOCK_MACHINE_DRAGOON),
                # Free/Steer are Top Ride machines, never an AR/CT starter (see _determine_starter_items).
                str(KARItemName.UNLOCK_MACHINE_FREE_STAR),
                str(KARItemName.UNLOCK_MACHINE_STEER_STAR),
            }
            # Slick and Turbo Star only turn by charge-drifting, so either as the sole machine with Charge
            # locked is a dead end. The world holds them out while base abilities are gated.
            self._check_one_starter(
                tag,
                "machine",
                machines,
                opts.start_inventory.value,
                precollected_counts,
                ineligible={str(m) for m in CHARGE_DEPENDENT_MACHINES} if opts.base_abilities_gated else frozenset(),
            )

        if tr_on and opts.machines_gated:
            tr_machines = {
                str(KARItemName.UNLOCK_MACHINE_FREE_STAR),
                str(KARItemName.UNLOCK_MACHINE_STEER_STAR),
            }
            self._check_one_starter(tag, "TR machine", tr_machines, opts.start_inventory.value, precollected_counts)

        if ar_on and opts.air_ride_courses_gated:
            self._check_one_starter(
                tag,
                "AR course",
                category_members(KARItemGroup.AR_COURSE_UNLOCKS),
                opts.start_inventory.value,
                precollected_counts,
            )

        if tr_on and opts.top_ride_courses_gated:
            self._check_one_starter(
                tag,
                "TR course",
                category_members(KARItemGroup.TR_COURSE_UNLOCKS),
                opts.start_inventory.value,
                precollected_counts,
            )

        # Colors are cross-mode: the gate alone decides, no mode condition.
        if opts.colors_gated:
            self._check_one_starter(
                tag,
                "color",
                category_members(KARItemGroup.COLOR_UNLOCKS),
                opts.start_inventory.value,
                precollected_counts,
            )

    def _check_one_starter(
        self, tag, label, category_set, start_inventory, precollected_counts, ineligible=frozenset()
    ):
        """
        `ineligible` names members the world holds out of the *random pick* for this seed. It narrows only
        the pick assertion, never `category_set`: the world tests start_inventory against the whole
        category, so shrinking the set here would make a preset ineligible item look like no preset at all.
        """
        si_in_cat = {n: c for n, c in start_inventory.items() if n in category_set and c > 0}
        if si_in_cat:
            # Player preset items: those should all be precollected; no random starter added.
            for n, c in si_in_cat.items():
                if precollected_counts.get(n, 0) < c:
                    raise HookError(
                        f"{tag} start_inventory specified {c}x {n!r} ({label}) but only "
                        f"{precollected_counts.get(n, 0)} in precollected"
                    )
            return
        # No start_inventory override: expect exactly one random pick from this category in precollected.
        picked = [n for n, c in precollected_counts.items() if n in category_set and c > 0]
        precollected_in_cat = sum(c for n, c in precollected_counts.items() if n in category_set)
        if precollected_in_cat != 1:
            raise HookError(
                f"{tag} expected exactly 1 random {label} starter in precollected, got {precollected_in_cat}"
            )
        if ineligible and picked[0] in ineligible:
            raise HookError(
                f"{tag} random {label} starter is {picked[0]!r}, which this seed's options make "
                f"ineligible (unplayable as a sole starter)"
            )

    def _check_start_inventory(self, tag, opts, pool_counts, precollected_counts):
        # Every start_inventory item should appear in precollected with at least that count. Unlock items
        # and checklist rewards are one-time, so _build_item_pools drops their pool copy and they must not
        # remain loose in the itempool. Filler and stackable counts stay.
        one_time_items = {str(n) for cat in GATING_CATEGORIES for n in items_by_type[cat.item_type]}
        one_time_items |= {str(n) for t in CHECKLIST_REWARD_TYPES for n in items_by_type[t]}
        for name, count in opts.start_inventory.value.items():
            if count <= 0:
                continue
            in_pc = precollected_counts.get(name, 0)
            if in_pc < count:
                raise HookError(f"{tag} start_inventory {count}x {name!r} but only {in_pc} in precollected")
            if name in one_time_items and pool_counts.get(name, 0) > 0:
                raise HookError(
                    f"{tag} preset one-time item {name!r} but {pool_counts[name]} copies remain in the "
                    f"itempool; it should be deduped out in _build_item_pools"
                )

    def _check_checklist_list_goal_locations(self, tag, mw, player, opts, ct_on, ar_on, tr_on, ap_on):
        for enabled, goal_opt, locs_opt, table, label in [
            (ct_on, opts.city_trial_goal, opts.city_trial_goal_locations, CITY_TRIAL_LOCATION_TABLE, "City Trial"),
            (ar_on, opts.air_ride_goal, opts.air_ride_goal_locations, AIR_RIDE_LOCATION_TABLE, "Air Ride"),
            (tr_on, opts.top_ride_goal, opts.top_ride_goal_locations, TOP_RIDE_LOCATION_TABLE, "Top Ride"),
            (ap_on, opts.archipelago_goal, opts.archipelago_goal_locations, AP_CHECKLIST_LOCATION_TABLE, "Archipelago"),
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
        if world.archipelago_enabled:
            expected.append(str(KARItemName.ARCHIPELAGO_VICTORY))

        placed_event_items = {
            loc.item.name for loc in mw.get_locations(player) if loc.address is None and loc.item is not None
        }
        for name in expected:
            if name not in placed_event_items:
                raise HookError(f"{tag} victory event {name!r} not placed (enabled mode requires it)")
