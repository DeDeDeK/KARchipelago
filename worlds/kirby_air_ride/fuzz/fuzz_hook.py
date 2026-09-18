"""
KAR-specific fuzzer hook.

Runs after each successful generation and asserts that the populated MultiWorld matches the intent of
the rolled options. A failing invariant makes the fuzzer dump the seed's YAML + traceback under
fuzz/output/error/. Invoke via:

    uv run python fuzz/fuzz.py -g kirby_air_ride -m worlds/kirby_air_ride/fuzz/fuzz_meta.yaml \
        --hook worlds.kirby_air_ride.fuzz.fuzz_hook:KARHook -r 200

Deliberately does NOT inherit from fuzz.BaseHook: fuzz.find_hook has an inverted issubclass check that
rejects real BaseHook subclasses, so duck-typing drops the hook in without patching the fuzzer.

Failures are reported through `reclassify_outcome` rather than raised out of `after_generate`. Raising
escapes gen_wrapper's dump path as a bare FuzzerException whose payload the fuzzer records as the
literal string "None", so report.json names no invariant at all and every hook failure of every kind
lands in one bucket. Stashing the error and handing it back as the run's outcome instead gets the
normal dump, and keys report.json by `HookError.kind` so a campaign's clusters are readable without
opening a single log.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from BaseClasses import ItemClassification, LocationProgressType

from worlds.kirby_air_ride.KARData import GameMode, checklist_reward_placed_bit
from worlds.kirby_air_ride.KARItems import (
    ALLOWED_ITEM_CATEGORY_ITEMS,
    AP_STAR_PIECE_UNLOCK_ITEMS,
    AR_COURSE_UNLOCK_ITEMS,
    AR_CT_MACHINE_UNLOCK_ITEMS,
    CHARGE_DEPENDENT_MACHINES,
    CHECKLIST_REWARD_CATEGORIES,
    CHECKLIST_REWARD_ITEM_TYPES,
    CHECKLIST_REWARD_TYPE_MODES,
    CHECKLIST_REWARD_TYPES,
    COLOR_UNLOCK_ITEMS,
    GATING_CATEGORIES,
    ITEM_TABLE,
    LEGENDARY_PIECE_UNLOCK_ITEMS,
    STADIUM_UNLOCK_ITEMS,
    TR_COURSE_UNLOCK_ITEMS,
    TR_MACHINE_UNLOCK_ITEMS,
    TRAP_CATEGORIES,
    KARItemGroup,
    KARItemName,
    KARItemType,
    item_name_groups,
    items_by_type,
)
from worlds.kirby_air_ride.KARLocations import (
    AIR_RIDE_LOCATION_TABLE,
    AP_CHECKLIST_LOCATION_TABLE,
    AP_PATCH_LOCATION_TABLE,
    CITY_TRIAL_LOCATION_TABLE,
    TOP_RIDE_LOCATION_TABLE,
)
from worlds.kirby_air_ride.KAROptions import (
    AirRideGoal,
    ArchipelagoGoal,
    CityTrialGoal,
    TopRideGoal,
)
from worlds.kirby_air_ride.KARRules import _EVENT_LOCATION_RULES

# The City Trial events a location rule keys; only these ship as progression.
_KEYED_EVENT_UNLOCKS: frozenset[str] = frozenset(str(name) for name in _EVENT_LOCATION_RULES.values())

# fuzz.GenOutcome, mirrored rather than imported: the fuzzer runs as __main__, so importing it here
# would re-execute the module in every worker.
_OUTCOME_SUCCESS = 0
_OUTCOME_FAILURE = 1


class HookError(AssertionError):
    """
    Raised when an invariant fails. `kind` is a stable slug naming the invariant, which is what
    report.json clusters on; the message carries the slot and the numbers needed to triage from the dump.
    """

    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        self.detail = detail
        super().__init__(f"{kind}: {detail}" if detail else kind)


def _fmt_slot(player: int, name: str) -> str:
    return f"[player {player} ({name!r})]"


class KARHook:
    GAME = "Kirby Air Ride"

    def __init__(self) -> None:
        # Set by after_generate, consumed by reclassify_outcome, one generation later at most.
        self._failure: HookError | None = None

    def setup_main(self, args):
        pass

    def setup_worker(self, args):
        pass

    def before_generate(self, args):
        # A generation that dies before after_generate leaves last run's error behind otherwise.
        self._failure = None

    def reclassify_outcome(self, outcome, raised):
        # Only a run the fuzzer thinks succeeded gets reclassified; a real crash or OptionError is
        # always the more informative report.
        if self._failure is not None and outcome == _OUTCOME_SUCCESS:
            failure, self._failure = self._failure, None
            # The detailed error becomes the cause so the dumped traceback keeps every number, while
            # the summary's str() stays the bare kind for report.json to group on.
            summary = HookError(failure.kind)
            summary.__cause__ = failure
            return _OUTCOME_FAILURE, summary
        return outcome, raised

    def finalize(self):
        pass

    def after_generate(self, mw, output_path):
        self._failure = None
        if mw is None:
            return

        # get_game_players, not a scan of mw.worlds: an item link group is a synthetic player whose
        # world reports our game too, and it has no entry in precollected_items or options.
        kar_players = [p for p in mw.get_game_players(self.GAME) if p not in mw.groups]
        # An item link moves the linked copies onto the group's player id and collapses the members'
        # duplicates into one shared copy, so a linked slot's items are neither owned by it nor present
        # in the counts every invariant below is written against. Modelling that is its own job; until
        # then the honest thing is to leave those slots alone rather than report invented failures.
        kar_players = [p for p in kar_players if not mw.get_player_groups(p)]
        if not kar_players:
            return

        # Every KAR slot needs the items it owns wherever they landed, so walk the whole multiworld's
        # locations once here instead of once per slot.
        items_by_owner: dict[int, list] = defaultdict(list)
        for loc in mw.get_locations():
            if loc.item is not None:
                items_by_owner[loc.item.player].append(loc.item)

        try:
            for player in kar_players:
                self._check_slot(mw, player, mw.worlds[player], items_by_owner[player])
        except HookError as err:
            self._failure = err

    def _check_slot(self, mw, player, world, items_we_own):
        opts = world.options
        slot_name = mw.get_player_name(player)
        tag = _fmt_slot(player, slot_name)
        # One call: fill_slot_data re-serializes the whole option set, UT's copy included.
        slot_data = world.fill_slot_data()

        ct_on = opts.city_trial_goal.value != CityTrialGoal.option_none
        ar_on = opts.air_ride_goal.value != AirRideGoal.option_none
        tr_on = opts.top_ride_goal.value != TopRideGoal.option_none
        ap_on = opts.archipelago_goal.value != ArchipelagoGoal.option_none

        if not any((ct_on, ar_on, tr_on, ap_on)):
            raise HookError("all_modes_disabled", f"{tag} generated with all modes disabled, should have OptionError'd")

        # Items in our slot, partitioned by where they live.
        pool_items = [it for it in mw.itempool if it.player == player]
        pool_counts = Counter(it.name for it in pool_items)

        precollected = list(mw.precollected_items[player])
        precollected_names = [it.name for it in precollected]
        precollected_counts = Counter(precollected_names)

        our_locations = list(mw.get_locations(player))
        items_at_our_locations = [loc.item for loc in our_locations if loc.item is not None]

        # Every distinct item this player owns, loose in the itempool or already placed - fill moves
        # items out of the pool. Unioned by identity, so no double count.
        owned_by_id = {id(it): it for it in pool_items}
        for it in items_we_own:
            owned_by_id[id(it)] = it
        owned_counts = Counter(it.name for it in owned_by_id.values())

        self._check_item_counts(tag, opts, pool_counts, world, ct_on, ar_on, tr_on, ap_on)
        self._check_generic_filler_present(tag, world)
        self._check_unlock_classifications(tag, pool_items)
        self._check_traps(tag, opts, pool_items)
        self._check_excluded_items_absent(tag, pool_counts, precollected_counts, opts, ct_on, ar_on, tr_on)
        self._check_reward_uniqueness(tag, world, owned_counts)
        self._check_checklist_rewards(tag, slot_data, opts, pool_counts, precollected_counts)
        self._check_effective_gates_shipped(tag, world, slot_data, owned_counts, precollected_counts)
        self._check_goal_forced_unlocks(tag, world, slot_data, owned_counts, precollected_counts)
        self._check_starter_precollected(tag, world, opts, precollected_counts, pool_counts, ct_on, ar_on, tr_on)
        self._check_start_inventory(tag, opts, pool_counts, precollected_counts)
        self._check_checklist_list_goal_locations(tag, mw, player, opts, ct_on, ar_on, tr_on, ap_on)
        self._check_ap_patches(tag, world, opts, slot_data, our_locations)
        self._check_location_progress_types(tag, world, opts, our_locations, ct_on, ar_on, tr_on, ap_on)
        self._check_non_local_items(tag, opts, player, items_at_our_locations)
        self._check_local_items(tag, opts, player, items_we_own)
        self._check_priority_locations(tag, opts, our_locations)
        self._check_exclude_locations(tag, opts, our_locations)
        self._check_victory_events_placed(tag, world, our_locations)

    def _check_item_counts(self, tag, opts, pool_counts, world, ct_on, ar_on, tr_on, ap_on):
        # PATCH_CAP_INCREASE = max - min when CT enabled, else 0
        if ct_on:
            expected = max(0, opts.city_trial_patch_cap_max.value - opts.city_trial_patch_cap_min.value)
        else:
            expected = 0
        actual = pool_counts.get(str(KARItemName.PATCH_CAP_INCREASE), 0)
        if actual != expected:
            raise HookError(
                "patch_cap_increase_count",
                f"{tag} PATCH_CAP_INCREASE count={actual}, expected {expected} "
                f"(ct_on={ct_on}, patch_cap_min={opts.city_trial_patch_cap_min.value}, "
                f"patch_cap_max={opts.city_trial_patch_cap_max.value})",
            )

        # SPAWN_RATE_UP = (max - min) // 10, else 0. Its source_modes are {CITYTRIAL, TOPRIDE}, so the
        # world's source-mode backstop drops it entirely when neither is in logic_modes. Mirror that
        # here off logic_modes, not the goal flags: AP Patches and Archipelago boxes are City Trial
        # content, so a goal-less City Trial still gets played and its spawn rate still matters.
        if world.logic_modes & {GameMode.CITYTRIAL, GameMode.TOPRIDE}:
            expected = max(0, (opts.spawn_rate_max.value - opts.spawn_rate_min.value) // 10)
        else:
            expected = 0
        actual = pool_counts.get(str(KARItemName.SPAWN_RATE_UP), 0)
        if actual != expected:
            raise HookError(
                "spawn_rate_up_count",
                f"{tag} SPAWN_RATE_UP count={actual}, expected {expected} "
                f"(min={opts.spawn_rate_min.value}, max={opts.spawn_rate_max.value})",
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
                raise HookError(
                    "checkbox_filler_count",
                    f"{tag} {name} count={actual}, expected {expected} (enabled={enabled}, opt={amount})",
                )

    def _check_generic_filler_present(self, tag, world):
        # Big Kirby / Small Kirby are immune to allowed_items (FILLER is not a category) and carry
        # _ALL_MODES, so both are always in filler_pool - the invariant that rules out filler starvation.
        for name in (KARItemName.BIG_KIRBY, KARItemName.SMALL_KIRBY):
            if str(name) not in world.filler_pool:
                raise HookError(
                    "cosmetic_filler_missing",
                    f"{tag} cosmetic filler {str(name)!r} missing from filler_pool; it must always be "
                    f"present so filler is never starved",
                )

    def _check_traps(self, tag, opts, pool_items):
        # `traps` governs trap membership the way `allowed_items` governs the optional gives: a category
        # left out keeps every trap it owns out of the pool. At trap_chance 0 no trap is ever drawn, so
        # none may reach the pool at all.
        active = {name for category in opts.traps.value for name in TRAP_CATEGORIES.get(category, frozenset())}
        for it in pool_items:
            if not (it.classification & ItemClassification.trap):
                continue
            if opts.trap_chance.value == 0:
                raise HookError(
                    "trap_with_zero_chance",
                    f"{tag} trap {it.name!r} is in the pool with trap_chance=0; no trap may be drawn at all",
                )
            if it.name not in active:
                raise HookError(
                    "trap_outside_categories",
                    f"{tag} trap {it.name!r} is in the pool but its category is not in "
                    f"traps={sorted(opts.traps.value)}",
                )

    def _check_reward_uniqueness(self, tag, world, owned_counts):
        # Checklist rewards are unique one-time unlocks, so each one in reward_pool must appear exactly
        # once among the owned items.
        for name in world.reward_pool:
            data = ITEM_TABLE.get(name)
            if data is None:
                continue
            count = owned_counts.get(str(name), 0)
            if count != 1:
                kind = "useful" if data.classification & ItemClassification.useful else "filler"
                raise HookError(
                    "reward_not_unique",
                    f"{tag} {kind} checklist reward {str(name)!r} count={count}, expected exactly 1 "
                    f"(rewards must be unique one-time items)",
                )

    def _check_checklist_rewards(self, tag, slot_data, opts, pool_counts, precollected_counts):
        # A category left out of checklist_rewards is unlocked by the mod at connect, so none of its
        # rewards may appear in the itempool or precollected. Rewards in no category - the 6 progression
        # part markers, and the ones a gating category owns - are unaffected.
        chosen = set(opts.checklist_rewards.value)
        dropped = sorted(set(CHECKLIST_REWARD_CATEGORIES) - chosen)
        offenders = []
        for category in dropped:
            for name in CHECKLIST_REWARD_CATEGORIES[category]:
                n = pool_counts.get(str(name), 0) + precollected_counts.get(str(name), 0)
                if n:
                    offenders.append((category, str(name), n))
        if offenders:
            raise HookError(
                "dropped_reward_present",
                f"{tag} checklist_rewards excludes {dropped} but {len(offenders)} of their reward(s) "
                f"still present (e.g. {offenders[:5]})",
            )

        # The shipped mask must name exactly the (mode, reward type) pairs that reached the pool. A pair
        # the mask claims but the pool never got - a disabled mode's rewards, most of all - is content no
        # item can unlock and the mod will not grant at connect.
        placed = {
            checklist_reward_placed_bit(CHECKLIST_REWARD_TYPE_MODES[ITEM_TABLE[name].type], reward_type)
            for name, reward_type in CHECKLIST_REWARD_ITEM_TYPES.items()
            if pool_counts.get(str(name), 0) or precollected_counts.get(str(name), 0)
        }
        mask = slot_data["checklist_rewards"]
        shipped = {bit for bit in range(32) if mask >> bit & 1}
        if shipped != placed:
            raise HookError(
                "reward_mask_mismatch",
                f"{tag} checklist_rewards mask {mask:#x} claims bits {sorted(shipped - placed)} with "
                f"nothing in the pool and misses {sorted(placed - shipped)} that is",
            )

    def _check_effective_gates_shipped(self, tag, world, slot_data, owned_counts, precollected_counts):
        # A gate ships as its *effective* state and the mod applies gate flags goal-independently, so a
        # category shipping ON with none of its unlocks obtainable locks that content permanently. The
        # unit tests pin a couple of mode combos; this holds across the whole random option space.
        for cat in GATING_CATEGORIES:
            shipped = slot_data.get(cat.option)
            expected = int(cat.option in world.effective_gates)
            if shipped != expected:
                raise HookError(
                    "gate_flag_mismatch",
                    f"{tag} {cat.option} ships as {shipped} but effective_gates says {expected}; "
                    f"the mod reads the shipped flag, so the two must agree",
                )
            if not shipped:
                continue
            keys = {str(n) for n in items_by_type[cat.item_type]}
            obtainable = {n for n in keys if owned_counts.get(n, 0) or precollected_counts.get(n, 0)}
            if not obtainable:
                raise HookError(
                    "gated_without_keys",
                    f"{tag} {cat.option} ships ON but none of its {len(keys)} unlock items exist in the "
                    f"seed, so that content could never be unlocked",
                )

    def _check_goal_forced_unlocks(self, tag, world, slot_data, owned_counts, precollected_counts):
        # The keys the pool must ship even with their category's gate off. The mod withholds exactly
        # these bits at connect, so one missing is an unwinnable seed that nothing else notices.
        for name in sorted(world.goal_forced_unlocks):
            if not (owned_counts.get(str(name), 0) or precollected_counts.get(str(name), 0)):
                raise HookError(
                    "goal_unlock_absent",
                    f"{tag} goal-forced unlock {str(name)!r} is absent from the seed; the mod withholds "
                    f"its bit at connect, so the goal is unreachable",
                )

        # The three holdback flags are how the mod learns which bits to withhold, so they have to track
        # goal_forced_unlocks exactly - a stale 0 hands the goal over at connect.
        for flag, keys in (
            ("legendary_pieces_goal_gated", LEGENDARY_PIECE_UNLOCK_ITEMS),
            ("ap_star_pieces_goal_gated", AP_STAR_PIECE_UNLOCK_ITEMS),
            ("vs_king_dedede_goal_gated", (KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,)),
        ):
            expected = int(bool(world.goal_forced_unlocks & set(keys)))
            if slot_data.get(flag) != expected:
                raise HookError(
                    "goal_holdback_flag",
                    f"{tag} {flag} ships as {slot_data.get(flag)}, expected {expected} from "
                    f"goal_forced_unlocks={sorted(str(n) for n in world.goal_forced_unlocks)}",
                )

        # Handing a goal's own key over for free wins the seed at connect. start_inventory is rejected in
        # _validate_options; this covers the other route in, a random starter pick.
        for name in sorted(world._goal_required_unlocks()):
            if precollected_counts.get(str(name), 0):
                raise HookError(
                    "goal_key_precollected",
                    f"{tag} goal key {str(name)!r} is precollected; this seed's goal is gated on it, so "
                    f"the player would start already able to win",
                )

    def _check_unlock_classifications(self, tag, pool_items):
        # Every UNLOCK-type item in the pool that logic keys must be progression-classified. Gated unlock
        # types come from GATING_CATEGORIES, stadiums included. The ten City Trial event unlocks no
        # location rule names are the documented exception: they gate nothing, so they ship useful.
        unlock_types = {cat.item_type for cat in GATING_CATEGORIES}
        for it in pool_items:
            data = ITEM_TABLE.get(it.name)
            if data is None or data.type not in unlock_types:
                continue
            if data.type == KARItemType.CT_EVENT_UNLOCK and it.name not in _KEYED_EVENT_UNLOCKS:
                if it.classification & ItemClassification.progression:
                    raise HookError(
                        "event_unlock_progression",
                        f"{tag} event unlock {it.name!r} is progression but no location rule keys it; "
                        f"either add the rule or leave it useful",
                    )
                continue
            if not (it.classification & ItemClassification.progression):
                raise HookError(
                    "unlock_not_progression",
                    f"{tag} unlock item {it.name!r} (type {data.type}) in pool with "
                    f"non-progression classification {it.classification!r}",
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
                        "disabled_mode_reward_present",
                        f"{tag} {group} contains {item_name!r} but that mode is disabled "
                        f"(pool={in_pool}, precollected_non_start={in_precollected})",
                    )

        # Overlapping checklist rewards are excluded whenever the mod handles their category directly:
        # UNLOCK items deliver it when the gate is ON, the mod pre-unlocks at connect when OFF. So the
        # reward is out of the pool either way, which is why this does not branch on the gate.
        for cat in GATING_CATEGORIES:
            if not cat.overlapping_rewards:
                continue
            for reward in cat.overlapping_rewards:
                in_pool = pool_counts.get(str(reward), 0)
                if in_pool:
                    raise HookError(
                        "overlapping_reward_present",
                        f"{tag} overlapping checklist reward {str(reward)!r} for {cat.option} is in the "
                        f"pool (count={in_pool}); the mod handles its category directly, so the reward "
                        f"should be excluded whatever {cat.option} is set to",
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
                        "disallowed_item_present",
                        f"{tag} {category} item {n!r} in pool (count={c}) but that category is disabled "
                        f"via allowed_items",
                    )

    def _check_starter_precollected(self, tag, world, opts, precollected_counts, pool_counts, ct_on, ar_on, tr_on):
        # For each gated category whose mode is enabled, expect either the starting_* option's named pick,
        # a start_inventory item from that category (either suppresses the draw), or exactly one random
        # precollected starter.

        def category_members(group):
            return {str(n) for n in item_name_groups[group]}

        # Stadium starter: CT enabled + progressive_stadiums on
        if ct_on and opts.city_trial_stadiums_gated:
            stadium_pool = {str(s) for s in STADIUM_UNLOCK_ITEMS}
            # Handing over the goal stadium for free would hand over the goal, so the world drops it
            # from the pick when beat_king_dedede is the City Trial goal.
            beat_dedede = opts.city_trial_goal.value == opts.city_trial_goal.option_beat_king_dedede
            held_out = {str(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)} if beat_dedede else frozenset()
            self._check_one_starter(
                tag,
                "stadium",
                opts.starting_stadium,
                STADIUM_UNLOCK_ITEMS,
                stadium_pool - held_out,
                opts.start_inventory.value,
                precollected_counts,
                pool_counts,
                held_out=held_out,
                # The stadium branch does not go through _pick_random_starter: it tests start_inventory
                # against all 24 unlocks, VS King Dedede included, while picking from the other 23.
                suppression_set=stadium_pool,
            )

        # Both machine branches key on the effective gate: `machines_gated` requires City Trial or Air
        # Ride, so a Top-Ride-only seed mints no machine unlocks and must hand out no machine starter.
        machines_keyed = "machines_gated" in world.effective_gates
        if machines_keyed:
            # Hydra, Dragoon and the Archipelago Star are assembled in City Trial from their pieces, so
            # none is ever a starting machine. Free/Steer are Top Ride controls and get their own pick.
            machines = category_members(KARItemGroup.MACHINE_UNLOCKS) - {
                str(KARItemName.UNLOCK_MACHINE_FREE_STAR),
                str(KARItemName.UNLOCK_MACHINE_STEER_STAR),
            }
            held_out = {
                str(KARItemName.UNLOCK_MACHINE_HYDRA),
                str(KARItemName.UNLOCK_MACHINE_DRAGOON),
                str(KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR),
            }
            # Slick and Turbo Star only turn by charge-drifting and Hydra / Bulk Star barely move, so the
            # world holds them out of the pick while base abilities are gated.
            if opts.base_abilities_gated:
                held_out |= {str(m) for m in CHARGE_DEPENDENT_MACHINES}
            self._check_one_starter(
                tag,
                "machine",
                opts.starting_machine,
                AR_CT_MACHINE_UNLOCK_ITEMS,
                machines - held_out,
                opts.start_inventory.value,
                precollected_counts,
                pool_counts,
                held_out=held_out,
            )

        if tr_on and machines_keyed:
            tr_machines = {
                str(KARItemName.UNLOCK_MACHINE_FREE_STAR),
                str(KARItemName.UNLOCK_MACHINE_STEER_STAR),
            }
            self._check_one_starter(
                tag,
                "TR machine",
                opts.starting_top_ride_machine,
                TR_MACHINE_UNLOCK_ITEMS,
                tr_machines,
                opts.start_inventory.value,
                precollected_counts,
                pool_counts,
            )

        if ar_on and opts.air_ride_courses_gated:
            self._check_one_starter(
                tag,
                "AR course",
                opts.starting_air_ride_course,
                AR_COURSE_UNLOCK_ITEMS,
                category_members(KARItemGroup.AR_COURSE_UNLOCKS),
                opts.start_inventory.value,
                precollected_counts,
                pool_counts,
            )

        if tr_on and opts.top_ride_courses_gated:
            self._check_one_starter(
                tag,
                "TR course",
                opts.starting_top_ride_course,
                TR_COURSE_UNLOCK_ITEMS,
                category_members(KARItemGroup.TR_COURSE_UNLOCKS),
                opts.start_inventory.value,
                precollected_counts,
                pool_counts,
            )

        # Colors are cross-mode: the gate alone decides, no mode condition.
        if opts.colors_gated:
            self._check_one_starter(
                tag,
                "color",
                opts.starting_kirby_color,
                COLOR_UNLOCK_ITEMS,
                category_members(KARItemGroup.COLOR_UNLOCKS),
                opts.start_inventory.value,
                precollected_counts,
                pool_counts,
            )

    def _check_one_starter(
        self,
        tag,
        label,
        option,
        candidates,
        eligible,
        start_inventory,
        precollected_counts,
        pool_counts,
        held_out=frozenset(),
        suppression_set=None,
    ):
        """
        `option` is the category's starting_* option, numbering its choices as 1-based indices into
        `candidates` with 0 for "randomized". On "randomized", `eligible` is exactly the set the world's
        draw picks from, so precollected must hold one of its members and nothing more; on a named pick,
        precollected must hold that one item instead.

        `held_out` names category members this seed's options bar from the pick (unplayable as a sole
        starter, or the goal's own key). They may still reach precollected through start_inventory, so the
        check subtracts the player's presets before complaining.

        `suppression_set` is the set the world tests start_inventory against when deciding to skip the
        draw, which is not always `eligible`: most categories test the narrowed eligible set, while the
        stadium branch tests the whole category. Defaults to `eligible`.
        """
        suppression = eligible if suppression_set is None else suppression_set

        # Unlocks are one-time, so a starter that reached precollected - drawn, named or preset - must
        # have had its pool copy dropped in _build_item_pools.
        for name in sorted(set(eligible) | set(held_out)):
            if precollected_counts.get(name, 0) and pool_counts.get(name, 0):
                raise HookError(
                    "starter_also_in_pool",
                    f"{tag} {label} starter {name!r} is precollected but {pool_counts[name]} copies "
                    f"remain in the itempool",
                )

        for name in sorted(held_out):
            unexplained = precollected_counts.get(name, 0) - start_inventory.get(name, 0)
            if unexplained > 0:
                raise HookError(
                    "held_out_starter_precollected",
                    f"{tag} {label} starter {name!r} is held out of the pick for this seed (unplayable "
                    f"as a sole starter, or the goal's own key) but was precollected anyway",
                )

        if option.value:
            named = str(candidates[option.value - 1])
            if named not in precollected_counts:
                raise HookError(
                    "named_starter_missing",
                    f"{tag} {label} starter was set to {option.current_key!r} but {named!r} is not precollected",
                )
            # Nothing else from the category on top of it: a named pick replaces the random draw rather
            # than adding to it. A pick the player also preset is precollected once, by start_inventory.
            category = set(eligible) | set(held_out)
            unexplained = sum(
                max(count - start_inventory.get(name, 0), 0)
                for name, count in precollected_counts.items()
                if name in category
            )
            expected = 0 if start_inventory.get(named, 0) else 1
            if unexplained != expected:
                raise HookError(
                    "named_starter_extra",
                    f"{tag} {label} starter was set to {option.current_key!r}; expected {expected} "
                    f"precollected beyond start_inventory, got {unexplained}",
                )
            return

        si_in_cat = {n: c for n, c in start_inventory.items() if n in suppression and c > 0}
        if si_in_cat:
            # Player preset items: those should all be precollected; no random starter added.
            for n, c in si_in_cat.items():
                if precollected_counts.get(n, 0) < c:
                    raise HookError(
                        "preset_starter_missing",
                        f"{tag} start_inventory specified {c}x {n!r} ({label}) but only "
                        f"{precollected_counts.get(n, 0)} in precollected",
                    )
            return
        # No start_inventory override: expect exactly one random pick from this category in precollected.
        precollected_in_cat = sum(c for n, c in precollected_counts.items() if n in eligible)
        if precollected_in_cat != 1:
            raise HookError(
                "random_starter_count",
                f"{tag} expected exactly 1 random {label} starter in precollected, got {precollected_in_cat}",
            )

    def _check_start_inventory(self, tag, opts, pool_counts, precollected_counts):
        # Every start_inventory item should appear in precollected with at least that count. One-time
        # items lose their pool copy in _build_item_pools; filler and stackable counts stay.
        one_time_items = {str(n) for cat in GATING_CATEGORIES for n in items_by_type[cat.item_type]}
        one_time_items |= {str(n) for t in CHECKLIST_REWARD_TYPES for n in items_by_type[t]}
        for name, count in opts.start_inventory.value.items():
            if count <= 0:
                continue
            in_pc = precollected_counts.get(name, 0)
            if in_pc < count:
                raise HookError(
                    "start_inventory_missing",
                    f"{tag} start_inventory {count}x {name!r} but only {in_pc} in precollected",
                )
            if name in one_time_items and pool_counts.get(name, 0) > 0:
                raise HookError(
                    "preset_one_time_in_pool",
                    f"{tag} preset one-time item {name!r} but {pool_counts[name]} copies remain in the "
                    f"itempool; it should be deduped out in _build_item_pools",
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
                    raise HookError(
                        "goal_location_misfiled", f"{tag} {label} goal location {name!r} not in {label} table"
                    )
                loc = mw.get_location(name, player)
                if loc.item is None:
                    raise HookError("goal_location_empty", f"{tag} {label} goal location {name!r} has no item")
                if loc.item.player != player:
                    raise HookError(
                        "goal_location_foreign",
                        f"{tag} {label} goal location {name!r} contains a non-local item "
                        f"({loc.item.name!r} from player {loc.item.player})",
                    )

    def _check_ap_patches(self, tag, world, opts, slot_data, our_locations):
        # The AP Patch band is sized in generate_early off the raw option, then zeroed when City Trial is
        # not in logic_modes at all. The mod reads the shipped count to size its own array, so a seed that
        # creates a different number of boxes than it ships desynchronises the two.
        expected = opts.ap_patches.value if GameMode.CITYTRIAL in world.logic_modes else 0
        if world.ap_patch_count != expected:
            raise HookError(
                "ap_patch_count",
                f"{tag} ap_patch_count={world.ap_patch_count}, expected {expected} "
                f"(ap_patches={opts.ap_patches.value}, logic_modes={sorted(str(m) for m in world.logic_modes)})",
            )
        if len(world.ap_patch_locations) != world.ap_patch_count:
            raise HookError(
                "ap_patch_table_size",
                f"{tag} sized {len(world.ap_patch_locations)} AP Patch locations for a count of {world.ap_patch_count}",
            )
        if slot_data.get("ap_patches") != world.ap_patch_count:
            raise HookError(
                "ap_patch_slot_data",
                f"{tag} slot_data ships ap_patches={slot_data.get('ap_patches')} but the seed created "
                f"{world.ap_patch_count}; the mod sizes its array off the shipped value",
            )

        # Every sized patch has to exist as a real location, and none beyond the count may.
        real = {loc.name for loc in our_locations if loc.address is not None and loc.name in AP_PATCH_LOCATION_TABLE}
        if real != set(world.ap_patch_locations):
            missing = sorted(set(world.ap_patch_locations) - real)[:5]
            extra = sorted(real - set(world.ap_patch_locations))[:5]
            raise HookError(
                "ap_patch_locations_mismatch",
                f"{tag} AP Patch locations do not match the sized band (missing {missing}, extra {extra})",
            )

    def _check_location_progress_types(self, tag, world, opts, our_locations, ct_on, ar_on, tr_on, ap_on):
        """
        The progression sub-flags and ap_patch_placement do all their work by sorting each mode's boxes
        into DEFAULT or EXCLUDED, which nothing downstream re-derives. Checking the placed locations
        against the world's own split covers all fourteen of those options in one pass.
        """
        # Archipelago applies the player's own lists after create_regions, excludes first and then
        # priority, so a name in priority_locations wins whatever the world assigned.
        user_excluded = set(opts.exclude_locations.value)
        user_priority = set(opts.priority_locations.value)
        by_name = {loc.name: loc for loc in our_locations}

        # Goal locations backed by a real checkbox are replaced by an event, so the box must be gone.
        for name in sorted(world.goal_locations_to_exclude):
            if name in by_name and by_name[name].address is not None:
                raise HookError(
                    "goal_replaced_location_present",
                    f"{tag} {name!r} backs this seed's goal and should have been replaced by an event, "
                    f"but still exists as a real location",
                )

        bands = [
            (ct_on, world.city_trial_default_locations, world.city_trial_excluded_locations, "City Trial"),
            (ar_on, world.air_ride_default_locations, world.air_ride_excluded_locations, "Air Ride"),
            (tr_on, world.top_ride_default_locations, world.top_ride_excluded_locations, "Top Ride"),
            (ap_on, world.archipelago_default_locations, world.archipelago_excluded_locations, "Archipelago"),
            (
                bool(world.ap_patch_locations),
                world.ap_patch_default_locations,
                world.ap_patch_excluded_locations,
                "AP Patches",
            ),
        ]
        for enabled, default_locs, excluded_locs, label in bands:
            if not enabled:
                continue
            for names, want_excluded in ((excluded_locs, True), (default_locs, False)):
                for name in names:
                    if name in world.goal_locations_to_exclude or name in user_priority:
                        continue
                    loc = by_name.get(name)
                    if loc is None:
                        raise HookError(
                            "band_location_missing",
                            f"{tag} {label} location {name!r} was sorted into the "
                            f"{'excluded' if want_excluded else 'default'} set but never created",
                        )
                    is_excluded = loc.progress_type == LocationProgressType.EXCLUDED
                    # A default box the player excluded by hand is excluded for that reason, not a bug.
                    if is_excluded != want_excluded and not (is_excluded and name in user_excluded):
                        raise HookError(
                            "progress_type_mismatch",
                            f"{tag} {label} location {name!r} has progress_type {loc.progress_type!r} but "
                            f"the world sorted it into the {'excluded' if want_excluded else 'default'} set",
                        )

    def _check_non_local_items(self, tag, opts, player, items_at_our_locations):
        non_local: set[str] = set(opts.non_local_items.value)
        if not non_local:
            return
        for item in items_at_our_locations:
            if item.player != player:
                continue
            if item.name in non_local:
                raise HookError(
                    "non_local_violation",
                    f"{tag} non_local_items {item.name!r} placed at our location, violating non_local rule",
                )

    def _check_local_items(self, tag, opts, player, items_we_own):
        local: set[str] = set(opts.local_items.value)
        if not local:
            return
        for item in items_we_own:
            if item.name in local:
                loc = item.location
                if loc is None or loc.player != player:
                    raise HookError(
                        "local_violation",
                        f"{tag} local_items {item.name!r} placed at non-local location "
                        f"({loc.name!r} player {loc.player if loc else None})",
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
                raise HookError("priority_location_empty", f"{tag} priority location {loc.name!r} has no item")
            if not (loc.item.classification & (ItemClassification.progression | ItemClassification.useful)):
                raise HookError(
                    "priority_location_filler",
                    f"{tag} priority location {loc.name!r} has filler/trap item "
                    f"{loc.item.name!r} ({loc.item.classification!r})",
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
                raise HookError(
                    "excluded_location_progression",
                    f"{tag} excluded location {loc.name!r} got progression item {loc.item.name!r}",
                )

    def _check_victory_events_placed(self, tag, world, our_locations):
        # Fill already enforces the completion condition; this is a second line that catches accidental
        # rule changes that drop a mode's victory event without making the seed unbeatable.
        expected = []
        if world.city_trial_enabled:
            expected.append(str(KARItemName.CITY_TRIAL_VICTORY))
        if world.air_ride_enabled:
            expected.append(str(KARItemName.AIR_RIDE_VICTORY))
        if world.top_ride_enabled:
            expected.append(str(KARItemName.TOP_RIDE_VICTORY))
        if world.archipelago_enabled:
            expected.append(str(KARItemName.ARCHIPELAGO_VICTORY))

        placed_event_items = {loc.item.name for loc in our_locations if loc.address is None and loc.item is not None}
        for name in expected:
            if name not in placed_event_items:
                raise HookError(
                    "victory_event_missing", f"{tag} victory event {name!r} not placed (enabled mode requires it)"
                )
