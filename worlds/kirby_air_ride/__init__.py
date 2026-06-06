from collections.abc import Mapping
from itertools import combinations
from typing import Any, ClassVar, NamedTuple

from BaseClasses import Item, ItemClassification, Location, Tutorial
from Options import OptionError

from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import add_item_rule
from worlds.LauncherComponents import (
    Component,
    Type,
    components,
    icon_paths,
    launch_subprocess,
)

from .KARData import GameMode, location_code_to_mode
from .KARItems import (
    CHECKLIST_REWARD_TYPES,
    GATING_CATEGORIES,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    TRAP_WEIGHT_GROUPS,
    KARItem,
    KARItemData,
    KARItemName,
    KARItemType,
    item_name_groups,
    items_by_type,
)
from .KARLocations import (
    AIR_RIDE_GOAL_TO_LOCATION,
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_GOAL_TO_LOCATION,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_TABLE,
    NATIVE_REWARD_TO_LOCATION,
    TOP_RIDE_GOAL_TO_LOCATION,
    TOP_RIDE_LOCATION_TABLE,
    KARLocationGroup,
    location_name_groups,
)
from .KAROptions import (
    AirRideGoal,
    CityTrialGoal,
    KAROptions,
    TopRideGoal,
    kar_option_groups,
)
from .KARRegions import create_regions
from .KARRules import set_rules


def run_client() -> None:
    from .KARClient import main

    launch_subprocess(main, name="KirbyAirRideClient")


components.append(
    Component(
        "Kirby Air Ride Client",
        func=run_client,
        component_type=Type.CLIENT,
        icon="Kirby Air Ride",
    )
)
icon_paths["Kirby Air Ride"] = "ap:worlds.kirby_air_ride/assets/allpatch.png"


class KARWeb(WebWorld):
    """
    Web interface for Kirby Air Ride: setup guide and the YAML options page.
    """

    tutorials = [  # noqa: RUF012
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Kirby Air Ride Archipelago on your computer.",
            "English",
            "setup_en.md",
            "setup/en",
            ["DeDeDK"],
        )
    ]
    theme = "partyTime"
    option_groups = kar_option_groups
    rich_text_options_doc = True
    options_presets = {  # noqa: RUF012
        # Max Stats Insanity bundles a runnable seed: City Trial goal is reaching the patch cap
        # target (30) on every stat in one trial round; pool is heavy on Patch Cap Increase and
        # Spawn Rate Up items; most gating is off so the patch-cap items fit. The patch-cap target
        # and spawn-rate ceiling are kept modest so the guaranteed counted items fit even in a
        # CT-only single-world pool. Players can still enable AR and/or TR for more locations.
        "Max Stats Insanity": {
            "city_trial_goal": "max_stats_in_one_run",
            "city_trial_patch_cap_amount": 30,
            "city_trial_progressive_patch_caps": True,
            "spawn_rate_progressive": True,
            "spawn_rate_min": 100,
            "spawn_rate_max": 300,
            "air_ride_goal": "n_checklist_blocks",
            "air_ride_checklist_amount": 20,
            "top_ride_goal": "n_checklist_blocks",
            "top_ride_checklist_amount": 20,
            # Disable most gating so the pool isn't dominated by unlock items.
            "city_trial_events_gated": False,
            "abilities_gated": False,
            "city_trial_patches_gated": False,
            "city_trial_items_gated": False,
            "machines_gated": False,
            "city_trial_boxes_gated": False,
            "air_ride_courses_gated": False,
            "colors_gated": False,
            "top_ride_courses_gated": False,
            "top_ride_items_gated": False,
            "city_trial_stadiums_gated": False,
            "city_trial_permanent_patches": False,
        },
    }


class _ModeCapacity(NamedTuple):
    """Per-mode location budget and progression/reward demand, computed once and shared by the
    capacity validators (_validate_pool_fits_locations, _validate_local_fits_modes) and the
    reward-pin budgeter (_reward_pin_capacity). All counts derive from the location name-sets and the
    built item pools, so the model is pre-pin and stays valid through create_items' pin step.

    default_by_mode: real, non-goal, non-user-excluded default boxes of each enabled mode.
    excluded_by_mode: real, non-goal excluded (filler-only) boxes of each enabled mode.
    prog_demand_by_subset: progression items whose effective source modes fall within subset S, i.e.
        the progression that must land in S under cross_mode_placement off. Keyed by every non-empty
        subset of the enabled modes.
    useful_rewards_by_mode / filler_rewards_by_mode: checklist rewards (single-source-mode) bucketed
        into their mode by classification.
    """

    default_by_mode: dict[GameMode, int]
    excluded_by_mode: dict[GameMode, int]
    prog_demand_by_subset: dict[frozenset[GameMode], int]
    useful_rewards_by_mode: dict[GameMode, int]
    filler_rewards_by_mode: dict[GameMode, int]


class KARWorld(World):
    """
    Kirby's Ready to Ride! Prepare for fast and furious racing action as Kirby hits Warpstar speed! Use ultra-simple
    controls to race and battle your pals in one of three hectic game modes!
    """

    options_dataclass = KAROptions
    options: KAROptions
    game: ClassVar[str] = "Kirby Air Ride"
    topology_present: bool = True

    # Keys must be plain str, not StrEnum, to survive the restricted pickler in multidata serialization.
    item_name_to_id: ClassVar[dict[str, int]] = {
        str(item_name): item_data.code for item_name, item_data in ITEM_TABLE.items() if item_data.code is not None
    }
    location_name_to_id: ClassVar[dict[str, int]] = {
        str(location_name): location_data.code
        for location_name, location_data in LOCATION_TABLE.items()
        if location_data.code is not None
    }

    item_name_groups: ClassVar[dict[str, set[str]]] = {
        str(k): {str(v) for v in vs} for k, vs in item_name_groups.items()
    }
    location_name_groups: ClassVar[dict[str, set[str]]] = {
        str(k): {str(v) for v in vs} for k, vs in location_name_groups.items()
    }

    web: ClassVar[KARWeb] = KARWeb()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.city_trial_enabled: bool = False
        self.city_trial_default_locations: set[str] = set()
        self.city_trial_excluded_locations: set[str] = set()
        self.air_ride_enabled: bool = False
        self.air_ride_default_locations: set[str] = set()
        self.air_ride_excluded_locations: set[str] = set()
        self.top_ride_enabled: bool = False
        self.top_ride_default_locations: set[str] = set()
        self.top_ride_excluded_locations: set[str] = set()
        self.useful_pool: set[str] = set()
        self.filler_pool: set[str] = set()
        self.reward_pool: list[str] = []
        # Shared per-mode capacity/demand model, built once in generate_early after the pools are
        # built (see _compute_mode_capacity); read by the capacity validators and the pin budgeter.
        self._mode_capacity: _ModeCapacity | None = None
        # Native checklist rewards pinned back onto their vanilla boxes (shuffle_checklist_rewards off).
        # Maps location name -> reward item name; populated in create_items via _pin_native_rewards.
        self.pinned_native_rewards: dict[str, str] = {}
        self.trap_weights: dict[str, int] = {}
        self.progression_pool: list[str] = []
        self.counted_useful_pool: list[str] = []
        self.stadium_starter_choice: KARItemName | None = None
        self.goal_locations_to_exclude: set[str] = set()
        self.machine_starter_choice: str | None = None
        self.patch_starter_choice: str | None = None
        self.ar_course_starter_choice: str | None = None
        self.tr_course_starter_choice: str | None = None

    @staticmethod
    def _categorize_locations(
        location_table: dict[str, Any],
        exclusion_groups: list[tuple[bool, set[str]]],
    ) -> tuple[set[str], set[str]]:
        """
        Categorize locations into default and excluded sets based on option-driven exclusion groups.
        """
        default_locations: set[str] = set()
        excluded_locations: set[str] = set()
        for location in location_table:
            if any(should_exclude and location in group for should_exclude, group in exclusion_groups):
                excluded_locations.add(location)
            else:
                default_locations.add(location)
        return default_locations, excluded_locations

    def _determine_locations_progress_type(self) -> None:
        """
        Determine the progress type of each location based on player options.
        """
        self.city_trial_default_locations, self.city_trial_excluded_locations = self._categorize_locations(
            CITY_TRIAL_LOCATION_TABLE,
            [
                (
                    not self.options.city_trial_progression_high_effort,
                    location_name_groups[KARLocationGroup.CT_HIGH_EFFORT],
                ),
                (
                    not self.options.city_trial_progression_multiplayer,
                    location_name_groups[KARLocationGroup.CT_MULTIPLAYER],
                ),
                (not self.options.city_trial_progression_free_run, location_name_groups[KARLocationGroup.CT_FREE_RUN]),
                (not self.options.city_trial_progression_rng, location_name_groups[KARLocationGroup.CT_RNG]),
                (
                    not self.options.city_trial_progression_bust_vehicles,
                    location_name_groups[KARLocationGroup.CT_BUST_VEHICLE_ON_VEHICLE],
                ),
            ],
        )

        self.air_ride_default_locations, self.air_ride_excluded_locations = self._categorize_locations(
            AIR_RIDE_LOCATION_TABLE,
            [
                (
                    not self.options.air_ride_progression_high_effort,
                    location_name_groups[KARLocationGroup.AR_HIGH_EFFORT],
                ),
                (not self.options.air_ride_progression_free_run, location_name_groups[KARLocationGroup.AR_FREE_RUN]),
                (
                    not self.options.air_ride_progression_time_attack,
                    location_name_groups[KARLocationGroup.AR_TIME_ATTACK],
                ),
            ],
        )

        self.top_ride_default_locations, self.top_ride_excluded_locations = self._categorize_locations(
            TOP_RIDE_LOCATION_TABLE,
            [
                (
                    not self.options.top_ride_progression_high_effort,
                    location_name_groups[KARLocationGroup.TR_HIGH_EFFORT],
                ),
                (not self.options.top_ride_progression_free_run, location_name_groups[KARLocationGroup.TR_FREE_RUN]),
                (
                    not self.options.top_ride_progression_time_attack,
                    location_name_groups[KARLocationGroup.TR_TIME_ATTACK],
                ),
                (
                    not self.options.top_ride_progression_multiplayer,
                    location_name_groups[KARLocationGroup.TR_MULTIPLAYER],
                ),
            ],
        )

    def _determine_goal_locations_to_exclude(self) -> None:
        """
        Determine which goal locations should be excluded from the multiworld.
        Goal locations that correspond to specific checklist entries are replaced by event locations,
        so the original location must not exist as a real location.
        """
        for enabled, goal_option, goal_location_map in [
            (self.city_trial_enabled, self.options.city_trial_goal, CITY_TRIAL_GOAL_TO_LOCATION),
            (self.air_ride_enabled, self.options.air_ride_goal, AIR_RIDE_GOAL_TO_LOCATION),
            (self.top_ride_enabled, self.options.top_ride_goal, TOP_RIDE_GOAL_TO_LOCATION),
        ]:
            if not enabled:
                continue
            if goal_option.value in goal_location_map:
                self.goal_locations_to_exclude.add(goal_location_map[goal_option.value])

    def _pick_random_starter(self, eligible: set[str]) -> str | None:
        """
        Pick a deterministic random item from `eligible`. Returns None if the pool is empty.
        Skips the pick entirely if the player already preset an item from this category via
        start_inventory.
        """
        if not eligible:
            return None
        if any(item in self.options.start_inventory for item in eligible):
            return None
        return self.random.choice(sorted(eligible))

    def _determine_starter_items(self) -> None:
        """
        Pre-determine one random starter item per gated category the player should not boot
        into without. Each is push_precollected in generate_early. Categories:
          - Stadiums (when city_trial_stadiums_gated + CT): any of the 24 stadium unlocks,
            excluding VS King Dedede when it's the goal.
          - Machines (when machines_gated + CT or AR): excludes Hydra/Dragoon (legendary).
          - Patch types (when city_trial_patches_gated + CT).
          - Air Ride courses (when air_ride_courses_gated + AR).
          - Top Ride courses (when top_ride_courses_gated + TR).

        Deliberately skipped (playable without): events, abilities, boxes, CT items, TR items,
        colors (Pink is the implicit default starter).
        """
        if self.city_trial_enabled and self.options.city_trial_stadiums_gated:
            beat_dedede = self.options.city_trial_goal.value == self.options.city_trial_goal.option_beat_king_dedede
            player_stadium_unlocks = [
                item_name for item_name in self.options.start_inventory if item_name in STADIUM_UNLOCK_ITEMS
            ]
            if player_stadium_unlocks:
                if beat_dedede and KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE in player_stadium_unlocks:
                    raise OptionError(
                        f"Cannot have {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE} "
                        f"in starting inventory if the goal is Beat King Dedede"
                    )
            else:
                stadiums: list[KARItemName] = list(STADIUM_UNLOCK_ITEMS)
                if beat_dedede:
                    stadiums.remove(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)
                self.stadium_starter_choice = self.random.choice(stadiums)

        if (self.city_trial_enabled or self.air_ride_enabled) and self.options.machines_gated:
            machines = items_by_type[KARItemType.MACHINE_UNLOCK] - {
                KARItemName.UNLOCK_MACHINE_HYDRA,
                KARItemName.UNLOCK_MACHINE_DRAGOON,
            }
            self.machine_starter_choice = self._pick_random_starter(machines)

        if self.city_trial_enabled and self.options.city_trial_patches_gated:
            self.patch_starter_choice = self._pick_random_starter(items_by_type[KARItemType.CT_PATCH_UNLOCK])

        if self.air_ride_enabled and self.options.air_ride_courses_gated:
            self.ar_course_starter_choice = self._pick_random_starter(items_by_type[KARItemType.AR_COURSE_UNLOCK])

        if self.top_ride_enabled and self.options.top_ride_courses_gated:
            self.tr_course_starter_choice = self._pick_random_starter(items_by_type[KARItemType.TR_COURSE_UNLOCK])

    def _validate_options(self) -> None:
        """
        Validate that option combinations are coherent.
        Checks checklist block goals are achievable and checkbox filler amounts are valid.
        """
        for enabled, goal_option, checklist_amount_option, filler_option, mode_name, location_table in [
            (
                self.city_trial_enabled,
                self.options.city_trial_goal,
                self.options.city_trial_checklist_amount,
                self.options.city_trial_checkbox_fillers,
                "City Trial",
                CITY_TRIAL_LOCATION_TABLE,
            ),
            (
                self.air_ride_enabled,
                self.options.air_ride_goal,
                self.options.air_ride_checklist_amount,
                self.options.air_ride_checkbox_fillers,
                "Air Ride",
                AIR_RIDE_LOCATION_TABLE,
            ),
            (
                self.top_ride_enabled,
                self.options.top_ride_goal,
                self.options.top_ride_checklist_amount,
                self.options.top_ride_checkbox_fillers,
                "Top Ride",
                TOP_RIDE_LOCATION_TABLE,
            ),
        ]:
            if not enabled:
                continue

            if goal_option.value == goal_option.option_n_checklist_blocks:
                required = checklist_amount_option.value
            elif goal_option.value == goal_option.option_100_checklist_blocks:
                required = 100
            else:
                continue

            available = len(set(location_table) - self.goal_locations_to_exclude)
            if available < required:
                raise OptionError(
                    f"{mode_name} goal requires {required} checklist blocks, but only "
                    f"{available} locations exist for this mode."
                )

            if goal_option.value == goal_option.option_n_checklist_blocks:
                if filler_option.value >= checklist_amount_option.value:
                    raise OptionError(
                        f"Cannot start with {filler_option.value} {mode_name} checkbox fillers with "
                        f"{checklist_amount_option.value} checklist blocks as a goal. "
                        f"Checkbox filler number must be less than goal amount."
                    )

        # Validate that checklist_list goal locations belong to their own mode.
        for enabled, goal_option, goal_locations_option, mode_name, location_table in [
            (
                self.city_trial_enabled,
                self.options.city_trial_goal,
                self.options.city_trial_goal_locations,
                "City Trial",
                CITY_TRIAL_LOCATION_TABLE,
            ),
            (
                self.air_ride_enabled,
                self.options.air_ride_goal,
                self.options.air_ride_goal_locations,
                "Air Ride",
                AIR_RIDE_LOCATION_TABLE,
            ),
            (
                self.top_ride_enabled,
                self.options.top_ride_goal,
                self.options.top_ride_goal_locations,
                "Top Ride",
                TOP_RIDE_LOCATION_TABLE,
            ),
        ]:
            if not enabled or goal_option.value != goal_option.option_checklist_list:
                continue
            if not goal_locations_option.value:
                option_name = f"{mode_name.lower().replace(' ', '_')}_goal_locations"
                raise OptionError(
                    f"{mode_name} goal is checklist_list but {option_name} is empty. "
                    f"Specify at least one {mode_name} location to use as a goal checkpoint."
                )
            misfiled = sorted(name for name in goal_locations_option.value if name not in location_table)
            if misfiled:
                raise OptionError(
                    f"{mode_name} goal locations include names that are not {mode_name} locations: {misfiled}"
                )

        if self.options.spawn_rate_progressive:
            sr_min = self.options.spawn_rate_min.value
            sr_max = self.options.spawn_rate_max.value
            if sr_max < sr_min:
                raise OptionError(f"Spawn Rate Max ({sr_max}) must be >= Spawn Rate Min ({sr_min}).")

    def _get_item_quantity(self, item_name: str, item_data: KARItemData) -> int:
        """Determine how many copies of an item to add to the pool."""
        if item_data.type == KARItemType.CHECKBOX_FILLER:
            match item_name:
                case KARItemName.CHECKBOX_FILLER_CITY_TRIAL:
                    return self.options.city_trial_checkbox_fillers.value
                case KARItemName.CHECKBOX_FILLER_AIR_RIDE:
                    return self.options.air_ride_checkbox_fillers.value
                case KARItemName.CHECKBOX_FILLER_TOP_RIDE:
                    return self.options.top_ride_checkbox_fillers.value
            return 1

        if item_data.type == KARItemType.PATCH_CAP_INCREASE:
            # Cap progressives from 1 up to the target. The mod's progressive
            # path (PatchCap_GetCap in patch_cap.c) starts the cap at 1 and adds
            # one for each Patch Cap Increase received, so we need (target - 1)
            # items in the pool to make the target reachable.
            return max(0, self.options.city_trial_patch_cap_amount.value - 1)

        if item_name == KARItemName.SPAWN_RATE_UP:
            # Each item grants +10%. Pool size = floor((max - min) / 10) so collecting all reaches max.
            return max(0, (self.options.spawn_rate_max.value - self.options.spawn_rate_min.value) // 10)

        return 1

    def _build_item_pools(self) -> None:
        """
        Determine which items are excluded based on player options, then sort the remaining items into pools
        (progression, useful, filler, trap) for placement during create_items().
        """

        # Gating categories (GATING_CATEGORIES, the single source of truth in KARItems):
        # exclude a category's unlock items when its gate is OFF or no relevant mode is enabled.
        # Overlapping checklist rewards are redundant with the mod's own unlock handling, so they are
        # always excluded: when the gate is ON the UNLOCK items deliver that content, and when it is OFF
        # the mod pre-unlocks the whole category at connect (APOptions_ApplyUngatedCategories). Either
        # way the reward gates nothing.
        excluded: set[str] = set()
        for cat in GATING_CATEGORIES:
            gated_off = not getattr(self.options, cat.option)
            no_mode = cat.required_modes and not any(getattr(self, mode) for mode in cat.required_modes)
            if gated_off or no_mode:
                excluded |= items_by_type[cat.item_type]
            if cat.overlapping_rewards:
                excluded |= set(cat.overlapping_rewards)

        # Mode-specific checklist rewards - excluded when their mode is disabled.
        # Without this, with cross_mode_placement off, rewards have no valid landing spots.
        if not self.air_ride_enabled:
            excluded |= items_by_type[KARItemType.AR_CHECKLIST_REWARD]
        if not self.top_ride_enabled:
            excluded |= items_by_type[KARItemType.TR_CHECKLIST_REWARD]
        if not self.city_trial_enabled:
            excluded |= items_by_type[KARItemType.CT_CHECKLIST_REWARD]

        # Non-progression checklist rewards: removed from the pool when checklist_rewards_gated is
        # off. The mod unlocks them all at connect (APOptions_ApplyUngatedCategories), so their boxes
        # carry ordinary items instead. The 6 Dragoon/Hydra part markers are progression (they gate
        # the legendary machines) and stay in the pool regardless.
        if not self.options.checklist_rewards_gated:
            for name, data in ITEM_TABLE.items():
                if data.type in CHECKLIST_REWARD_TYPES and not (data.classification & ItemClassification.progression):
                    excluded.add(name)

        # Permanent patches: excluded unless CT enabled AND option ON
        if not self.city_trial_enabled or not self.options.city_trial_permanent_patches:
            excluded |= items_by_type[KARItemType.PERMANENT_PATCH]

        # Patch cap increase: excluded unless CT enabled AND progressive caps ON
        if not self.city_trial_enabled or not self.options.city_trial_progressive_patch_caps:
            excluded.add(KARItemName.PATCH_CAP_INCREASE)

        # Spawn Rate Up: excluded unless progressive spawn rate is ON and there's room to grow.
        if (
            not self.options.spawn_rate_progressive
            or self.options.spawn_rate_max.value <= self.options.spawn_rate_min.value
        ):
            excluded.add(KARItemName.SPAWN_RATE_UP)

        # Drop Patches Trap: only meaningful in City Trial (the mod's handler
        # guards on Gm_IsInCity), and only when traps are enabled at all.
        if not self.city_trial_enabled or self.options.trap_chance.value == 0:
            excluded.add(KARItemName.DROP_PATCHES_TRAP)

        # Checkbox fillers: excluded per mode when mode disabled or amount is 0
        if not self.city_trial_enabled or self.options.city_trial_checkbox_fillers.value == 0:
            excluded.add(KARItemName.CHECKBOX_FILLER_CITY_TRIAL)
        if not self.air_ride_enabled or self.options.air_ride_checkbox_fillers.value == 0:
            excluded.add(KARItemName.CHECKBOX_FILLER_AIR_RIDE)
        if not self.top_ride_enabled or self.options.top_ride_checkbox_fillers.value == 0:
            excluded.add(KARItemName.CHECKBOX_FILLER_TOP_RIDE)

        # Backstop: any item whose source_modes is non-empty but doesn't intersect with the
        # enabled modes can't be placed under cross_mode_placement=false and has no in-game
        # effect in the modes that ARE enabled. Drop it regardless of the cross-mode setting.
        enabled_modes: set[GameMode] = set()
        if self.city_trial_enabled:
            enabled_modes.add(GameMode.CITYTRIAL)
        if self.air_ride_enabled:
            enabled_modes.add(GameMode.AIRRIDE)
        if self.top_ride_enabled:
            enabled_modes.add(GameMode.TOPRIDE)
        for name, data in ITEM_TABLE.items():
            if data.source_modes and not (data.source_modes & enabled_modes):
                excluded.add(name)

        # Precollected starter items (one per gated category, see _determine_starter_items).
        # Exclude start_inventory items of each category plus the random pick so they don't
        # show up in the multiworld pool a second time.
        starter_groups: list[tuple[str | None, set[str]]] = [
            (self.stadium_starter_choice, set(STADIUM_UNLOCK_ITEMS)),
            (self.machine_starter_choice, items_by_type[KARItemType.MACHINE_UNLOCK]),
            (self.patch_starter_choice, items_by_type[KARItemType.CT_PATCH_UNLOCK]),
            (self.ar_course_starter_choice, items_by_type[KARItemType.AR_COURSE_UNLOCK]),
            (self.tr_course_starter_choice, items_by_type[KARItemType.TR_COURSE_UNLOCK]),
        ]
        for choice, group in starter_groups:
            for item_name in self.options.start_inventory:
                if item_name in group:
                    excluded.add(item_name)
            if choice is not None:
                excluded.add(choice)

        def trap_weight(name: str) -> int:
            for option_attr, names in TRAP_WEIGHT_GROUPS:
                if name in names:
                    return getattr(self.options, option_attr).value
            return 0

        # Sort non-excluded items into pools
        for item_name, item_data in ITEM_TABLE.items():
            if item_data.code is None:
                continue
            if item_name in excluded:
                continue

            classification = item_data.classification
            if classification & ItemClassification.progression:
                quantity = self._get_item_quantity(item_name, item_data)
                self.progression_pool.extend([item_name] * quantity)
            elif item_data.type in (KARItemType.CHECKBOX_FILLER, KARItemType.SPAWN_RATE):
                quantity = self._get_item_quantity(item_name, item_data)
                self.counted_useful_pool.extend([item_name] * quantity)
            elif item_data.type in (
                KARItemType.CT_CHECKLIST_REWARD,
                KARItemType.AR_CHECKLIST_REWARD,
                KARItemType.TR_CHECKLIST_REWARD,
            ):
                # Checklist rewards are unique one-time unlocks, each tied to a specific box - not
                # interchangeable filler. Route each into reward_pool exactly once so every in-scope
                # reward is placed. (Progression part-markers are caught by the branch above and stay
                # in progression_pool; overlapping and mode-disabled rewards are already excluded.)
                self.reward_pool.append(item_name)
            elif classification & ItemClassification.useful:
                self.useful_pool.add(item_name)
            elif classification & ItemClassification.trap:
                weight = trap_weight(item_name)
                if weight > 0:
                    self.trap_weights[item_name] = weight
            else:
                self.filler_pool.add(item_name)

    def generate_early(self) -> None:
        """
        Run before any general steps of the MultiWorld other than options.
        """
        self.city_trial_enabled = self.options.city_trial_goal.value != CityTrialGoal.option_none
        self.air_ride_enabled = self.options.air_ride_goal.value != AirRideGoal.option_none
        self.top_ride_enabled = self.options.top_ride_goal.value != TopRideGoal.option_none

        if not any((self.city_trial_enabled, self.air_ride_enabled, self.top_ride_enabled)):
            raise OptionError("No modes enabled. You need to have at least one goal in a mode!")

        self._determine_goal_locations_to_exclude()
        self._determine_locations_progress_type()
        self._validate_options()

        self._determine_starter_items()
        for choice in (
            self.stadium_starter_choice,
            self.machine_starter_choice,
            self.patch_starter_choice,
            self.ar_course_starter_choice,
            self.tr_course_starter_choice,
        ):
            if choice is not None:
                self.push_precollected(self.create_item(choice))

        self._build_item_pools()
        self._mode_capacity = self._compute_mode_capacity()
        self._validate_pool_fits_locations()
        if not self.options.cross_mode_placement:
            self._validate_local_fits_modes()

    @property
    def _capacity(self) -> _ModeCapacity:
        """The shared per-mode capacity model built in generate_early (see _compute_mode_capacity)."""
        assert self._mode_capacity is not None, "capacity model accessed before generate_early built it"
        return self._mode_capacity

    def _compute_mode_capacity(self) -> _ModeCapacity:
        """
        Build the per-mode capacity/demand model shared by the capacity validators and the reward-pin
        budgeter (see _ModeCapacity). Computed once from the location name-sets and the built item
        pools, so it stays valid from the end of generate_early through create_items' pin step (which
        reads it before mutating the pools). The counting and effective-mode logic match the inline
        computations these consumers each carried before.
        """
        default_by_mode: dict[GameMode, int] = {}
        excluded_by_mode: dict[GameMode, int] = {}
        for mode_enum, enabled, default_locs, excluded_locs in [
            (
                GameMode.CITYTRIAL,
                self.city_trial_enabled,
                self.city_trial_default_locations,
                self.city_trial_excluded_locations,
            ),
            (
                GameMode.AIRRIDE,
                self.air_ride_enabled,
                self.air_ride_default_locations,
                self.air_ride_excluded_locations,
            ),
            (
                GameMode.TOPRIDE,
                self.top_ride_enabled,
                self.top_ride_default_locations,
                self.top_ride_excluded_locations,
            ),
        ]:
            if not enabled:
                continue
            default_by_mode[mode_enum] = sum(
                1
                for loc in default_locs
                if loc not in self.goal_locations_to_exclude and loc not in self.options.exclude_locations
            )
            # Total placeable: every real non-goal location of the mode. User-excluded locations still
            # exist (they receive filler) so they count toward the excluded budget, not the default one.
            total = sum(1 for loc in (default_locs | excluded_locs) if loc not in self.goal_locations_to_exclude)
            excluded_by_mode[mode_enum] = total - default_by_mode[mode_enum]
        enabled_set = frozenset(default_by_mode)

        # Effective placement modes of each progression item, intersected with the enabled set. Empty
        # source_modes means mode-neutral progression, placeable in any enabled mode. Items whose
        # source_modes don't intersect the enabled set are already excluded from the pool, but skip them
        # defensively so they can never inflate a subset's demand.
        prog_effective: list[frozenset[GameMode]] = []
        for name in self.progression_pool:
            data = ITEM_TABLE.get(name)
            if data is None:
                continue
            if data.source_modes:
                eff = data.source_modes & enabled_set
                if not eff:
                    continue
            else:
                eff = enabled_set
            prog_effective.append(eff)

        prog_demand_by_subset: dict[frozenset[GameMode], int] = {}
        modes = sorted(enabled_set, key=lambda m: m.value)
        for r in range(1, len(modes) + 1):
            for combo in combinations(modes, r):
                subset = frozenset(combo)
                prog_demand_by_subset[subset] = sum(1 for eff in prog_effective if eff <= subset)

        # Checklist rewards are single-source-mode; bucket each into its (enabled) mode by class.
        useful_rewards_by_mode: dict[GameMode, int] = dict.fromkeys(default_by_mode, 0)
        filler_rewards_by_mode: dict[GameMode, int] = dict.fromkeys(default_by_mode, 0)
        for name in self.reward_pool:
            data = ITEM_TABLE[name]
            eff = data.source_modes & enabled_set
            if not eff:
                continue
            mode = next(iter(eff))
            if data.classification & ItemClassification.useful:
                useful_rewards_by_mode[mode] += 1
            else:
                filler_rewards_by_mode[mode] += 1

        return _ModeCapacity(
            default_by_mode=default_by_mode,
            excluded_by_mode=excluded_by_mode,
            prog_demand_by_subset=prog_demand_by_subset,
            useful_rewards_by_mode=useful_rewards_by_mode,
            filler_rewards_by_mode=filler_rewards_by_mode,
        )

    def _validate_pool_fits_locations(self) -> None:
        """
        Verify the guaranteed item pool fits the available locations. Two budgets are checked, mirroring
        create_items:
          - "needs-default": progression + counted-useful + the useful-classified checklist rewards can
            only sit on default (non-excluded) locations.
          - "total": every guaranteed item (the above plus the filler-classified rewards, which may sit on
            excluded boxes) must fit the total placeable location count.
        Rewards are unique one-time unlocks (not draw-with-replacement filler), so each counts once. Runs
        after _build_item_pools so the pool sizes are final. Raises OptionError with a hint about the
        likely culprit options.
        """
        cap = self._capacity
        default_count = sum(cap.default_by_mode.values())
        total_count = default_count + sum(cap.excluded_by_mode.values())
        reward_useful = sum(cap.useful_rewards_by_mode.values())
        base_guaranteed = len(self.progression_pool) + len(self.counted_useful_pool)
        needs_default = base_guaranteed + reward_useful
        total_guaranteed = base_guaranteed + len(self.reward_pool)

        if needs_default <= default_count and total_guaranteed <= total_count:
            return

        hints: list[str] = []
        if self.options.city_trial_progressive_patch_caps and self.options.city_trial_patch_cap_amount.value > 1:
            hints.append(
                f"city_trial_patch_cap_amount={self.options.city_trial_patch_cap_amount.value} "
                f"adds {self.options.city_trial_patch_cap_amount.value - 1} Patch Cap Increase items"
            )
        if self.options.spawn_rate_progressive:
            sr_count = max(0, (self.options.spawn_rate_max.value - self.options.spawn_rate_min.value) // 10)
            if sr_count > 0:
                hints.append(
                    f"spawn_rate range ({self.options.spawn_rate_min.value}-{self.options.spawn_rate_max.value}) "
                    f"adds {sr_count} Spawn Rate Up items"
                )
        hint_str = (" Likely culprits: " + "; ".join(hints) + ".") if hints else ""
        if needs_default > default_count:
            raise OptionError(
                f"Guaranteed item pool needing default locations ({needs_default} items: "
                f"{len(self.progression_pool)} progression, {len(self.counted_useful_pool)} counted-useful, "
                f"{reward_useful} useful checklist rewards) exceeds available default locations "
                f"({default_count}). Reduce option values, exclude fewer locations, or enable more modes / "
                f"progression flags to make room.{hint_str}"
            )
        raise OptionError(
            f"Guaranteed item pool ({total_guaranteed} items: {len(self.progression_pool)} progression, "
            f"{len(self.counted_useful_pool)} counted-useful, {len(self.reward_pool)} checklist rewards) "
            f"exceeds total placeable locations ({total_count}). Reduce option values or enable more modes / "
            f"progression flags to make room.{hint_str}"
        )

    def _validate_local_fits_modes(self) -> None:
        """
        Under cross_mode_placement=false, KAR item-rule-locks both progression and checklist rewards to
        their source mode(s), so each enabled mode's locations must hold the items confined to it.
        Multi-mode progression (abilities/machines/colors) may go in any of its modes, making this a
        Hall's-condition check over subsets S of enabled modes (exact for the <=3 modes here); rewards are
        single-source-mode. Two budgets per subset, which together imply the per-subset total-boxes budget:
          - needs-default: progression + useful rewards + filler-reward spill (filler rewards beyond a
            mode's excluded boxes spill onto its own default boxes) must fit the subset's default boxes.
          - excluded-filler: excluded boxes take only filler, so each subset's excluded boxes must be
            coverable by its confined filler rewards plus the shared generic filler create_items mints.
        Mode-neutral demand (counted-useful, generic filler/useful) floats and is covered by
        _validate_pool_fits_locations' global budgets. Shuffle-independent. Raises OptionError naming the
        overcommitted modes.
        """
        cap = self._capacity
        default_by_mode = cap.default_by_mode
        excluded_by_mode = cap.excluded_by_mode
        useful_rewards_by_mode = cap.useful_rewards_by_mode
        filler_rewards_by_mode = cap.filler_rewards_by_mode
        enabled_set = frozenset(default_by_mode)

        # generic_filler is the mode-neutral filler create_items mints for excluded boxes the confined
        # filler rewards don't cover (= max(0, excluded - reward_filler)). The full enabled set always
        # holds, so only proper subsets can fail the excluded(S) <= filler_rewards(S) + generic_filler
        # check below.
        num_excluded = sum(excluded_by_mode.values())
        num_reward_filler = sum(filler_rewards_by_mode.values())
        generic_filler = max(0, num_excluded - num_reward_filler)

        modes = sorted(enabled_set, key=lambda m: m.value)
        for r in range(1, len(modes) + 1):
            for subset in combinations(modes, r):
                subset_set = frozenset(subset)
                mode_names = ", ".join(m.name for m in subset)
                prog_demand = cap.prog_demand_by_subset[subset_set]
                useful_demand = sum(useful_rewards_by_mode[m] for m in subset)
                filler_demand = sum(filler_rewards_by_mode[m] for m in subset)
                default_cap = sum(default_by_mode[m] for m in subset)
                # Filler rewards prefer excluded boxes, but a mode whose filler rewards outnumber its
                # excluded boxes must spill the surplus onto its own default boxes (they are mode-locked,
                # so they cannot escape to another mode's excluded boxes). That surplus competes with
                # progression and useful rewards for default boxes, so it is part of the needs-default
                # demand. (Generic filler is mode-neutral and never spills here; only confined rewards do.)
                filler_spill = sum(max(0, filler_rewards_by_mode[m] - excluded_by_mode[m]) for m in subset)
                if prog_demand + useful_demand + filler_spill > default_cap:
                    raise OptionError(
                        f"Cross-mode placement is off, but mode(s) [{mode_names}] must hold {prog_demand} "
                        f"progression, {useful_demand} useful checklist reward, and {filler_spill} surplus "
                        f"filler checklist reward items (filler rewards with no excluded box left in their "
                        f"mode) on only {default_cap} default locations between them. Enable "
                        f"cross_mode_placement, enable more modes, reduce gating / progressive options, turn "
                        f"on more progression location flags, or turn off checklist_rewards_gated to make room."
                    )
                excluded_demand = sum(excluded_by_mode[m] for m in subset)
                if excluded_demand > filler_demand + generic_filler:
                    raise OptionError(
                        f"Cross-mode placement is off, but mode(s) [{mode_names}] have {excluded_demand} "
                        f"excluded (filler-only) locations and can supply only {filler_demand} confined "
                        f"filler checklist reward(s) plus {generic_filler} shared generic filler item(s) "
                        f"to fill them. Excluded boxes accept only filler, and filler rewards are locked to "
                        f"their mode while cross-mode placement is off. Enable cross_mode_placement, lower "
                        f"this mode's checkbox_fillers, exclude fewer of its locations, or turn off "
                        f"checklist_rewards_gated to make room."
                    )

    def create_regions(self) -> None:
        create_regions(self)

    def set_rules(self) -> None:
        set_rules(self)
        self._set_goal_location_item_rules()
        self._set_cross_mode_placement_rules()

    def _set_goal_location_item_rules(self) -> None:
        """
        Restrict checklist_list goal locations to local items only.

        This prevents other players' /collect from checking these locations,
        which would auto-complete checklist entries and prematurely satisfy the goal.
        """
        for enabled, goal_option, goal_locations_option in [
            (self.city_trial_enabled, self.options.city_trial_goal, self.options.city_trial_goal_locations),
            (self.air_ride_enabled, self.options.air_ride_goal, self.options.air_ride_goal_locations),
            (self.top_ride_enabled, self.options.top_ride_goal, self.options.top_ride_goal_locations),
        ]:
            if not enabled or goal_option.value != goal_option.option_checklist_list:
                continue
            for location_name in goal_locations_option.value:
                location = self.get_location(location_name)
                add_item_rule(location, lambda item, player=self.player: item.player == player)

    def _set_cross_mode_placement_rules(self) -> None:
        """
        When cross_mode_placement is off, lock our own mode-tagged progression and checklist-reward items
        to their source mode(s): each may only land at a location of one of its source modes. Everything
        non-confined (traps, filler, counted-useful) and mode-neutral items (empty source_modes) float
        freely; remote items (other players') are unaffected - confinement is intra-KAR only.

        Composes with shuffle_checklist_rewards: shuffle-off pins the reward onto its native box (already
        in-mode); shuffle-on lets it float but this rule keeps fill from carrying it out of its mode.
        _validate_local_fits_modes guarantees each mode can hold its own confined items.
        """
        if self.options.cross_mode_placement:
            return

        player = self.player
        reward_names = {str(name) for name, data in ITEM_TABLE.items() if data.type in CHECKLIST_REWARD_TYPES}
        for location in self.get_locations():
            loc_mode = location_code_to_mode(location.address)
            if loc_mode is None:
                continue
            add_item_rule(
                location,
                lambda item, lm=loc_mode, p=player, rewards=reward_names: (
                    item.player != p
                    or not ((item.classification & ItemClassification.progression) or item.name in rewards)
                    or not (sm := getattr(item, "source_modes", frozenset()))
                    or lm in sm
                ),
            )

    def create_item(self, name: str) -> KARItem:
        """
        Create a KARItem from the given item_name.
        """
        if name in self.item_names or name in ITEM_TABLE:
            data = ITEM_TABLE[name]
            return KARItem.from_data(str(name), self.player, data)
        raise KeyError(f"Invalid item name: {name}")

    def _reward_pin_capacity(self) -> tuple[dict[GameMode, int], dict[frozenset[GameMode], int], int]:
        """
        Capacity data used to budget which checklist rewards may pin onto a *default* box without
        starving progression of the default locations it needs.

        Returns (default_by_mode, demand_by_subset, global_spare):
          - default_by_mode[m] = real, non-goal, non-user-excluded default boxes of enabled mode m.
          - demand_by_subset[S] = progression items (the full pool, part markers included) whose
            effective source modes fall entirely within S, i.e. the progression that *must* land in S
            under cross_mode_placement off. Mirrors _validate_local_fits_modes' Hall accounting.
          - global_spare = (all default boxes) - (all needs-default items: progression + counted-useful
            + useful rewards). The headroom for pinning *filler* onto default boxes. >= 0 by
            _validate_pool_fits_locations.
        """
        cap = self._capacity
        useful_reward_total = sum(cap.useful_rewards_by_mode.values())
        needs_default = len(self.progression_pool) + len(self.counted_useful_pool) + useful_reward_total
        global_spare = sum(cap.default_by_mode.values()) - needs_default
        return cap.default_by_mode, cap.prog_demand_by_subset, global_spare

    def _pin_native_rewards(self, excluded_locations: set[str]) -> None:
        """
        When shuffle_checklist_rewards is off, pin each in-pool checklist reward back onto its vanilla box
        (place_locked_item) and drop it from its pool so create_items mints no duplicate. In scope: the
        non-progression rewards in reward_pool plus the six progression Dragoon/Hydra part markers. Runs
        before create_items counts locations, so the locked boxes self-balance the mint.

        Default boxes are the only home for progression / counted-useful / useful rewards, so default-box
        pins are rationed:
          - Always pin (capacity-neutral): a part marker on a default box (already in progression demand;
            parts gate the Hydra/Dragoon cells, not their own boxes, so this never self-locks), or a filler
            reward on an excluded box (its proper home).
          - Budgeted (useful rewards, plus filler-on-default under cross-on), useful first: cross-on bounds
            on global filler headroom; cross-off requires each pin to keep every progression subset within
            Hall's condition (_pin_keeps_progression_feasible). Non-fitting rewards float. Filler-on-default
            under cross-off is deferred to pre_fill (excluded-first) so realized spill matches the validated
            optimum max(0, filler_rewards(m) - excluded(m)).
        """
        if self.options.shuffle_checklist_rewards:
            return

        cross = bool(self.options.cross_mode_placement)
        in_scope = list(self.reward_pool) + [
            name for name in self.progression_pool if ITEM_TABLE[name].type in CHECKLIST_REWARD_TYPES
        ]
        # Resolve each in-scope reward to a pinnable native box and bucket it. always_pin: capacity-neutral
        # (part on default box, filler on excluded box). budgeted: default-box pins competing for capacity
        # (useful rewards, plus filler-on-default only under cross-on), with useful first so it wins the
        # scarce slots. Sorted for determinism.
        always_pin: list[tuple[str, Location]] = []
        budgeted: list[tuple[str, Location, GameMode, bool]] = []
        for reward in sorted(in_scope):
            location_name = NATIVE_REWARD_TO_LOCATION.get(reward)
            if location_name is None or location_name in self.goal_locations_to_exclude:
                continue
            try:
                location = self.get_location(location_name)
            except KeyError:
                continue  # box belongs to a disabled mode, so no real location exists
            if location.locked or location.address is None:
                continue
            mode = location_code_to_mode(location.address)
            if mode is None:
                continue
            classification = ITEM_TABLE[reward].classification
            is_progression = bool(classification & ItemClassification.progression)
            is_filler = not (classification & (ItemClassification.useful | ItemClassification.progression))
            is_excluded_box = location_name in excluded_locations
            if is_progression:
                if not is_excluded_box:
                    always_pin.append((reward, location))  # part on default box: counted in demand already
            elif is_filler and is_excluded_box:
                always_pin.append((reward, location))  # filler on its proper home (excluded box)
            elif not is_filler and is_excluded_box:
                continue  # useful reward can't sit on a filler-only excluded box; float
            elif is_filler and not cross:
                continue  # cross-off: float filler-on-default so pre_fill places it excluded-first (optimal)
            else:
                budgeted.append((reward, location, mode, is_filler))

        pinned: list[tuple[str, Location]] = list(always_pin)
        default_by_mode, demand_by_subset, global_spare = self._reward_pin_capacity()
        pins_by_mode: dict[GameMode, int] = dict.fromkeys(default_by_mode, 0)
        # Useful rewards before filler so they claim scarce default slots first.
        for reward, location, mode, is_filler in sorted(budgeted, key=lambda b: (b[3], b[0])):
            if is_filler and global_spare <= 0:
                continue
            if not cross and not self._pin_keeps_progression_feasible(
                mode, pins_by_mode, demand_by_subset, default_by_mode
            ):
                continue
            pins_by_mode[mode] += 1
            if is_filler:
                global_spare -= 1
            pinned.append((reward, location))

        pinned_rewards: list[str] = []
        pinned_parts: list[str] = []
        for reward, location in pinned:
            location.place_locked_item(self.create_item(reward))
            self.pinned_native_rewards[location.name] = reward
            if ITEM_TABLE[reward].classification & ItemClassification.progression:
                pinned_parts.append(reward)
            else:
                pinned_rewards.append(reward)

        for reward in pinned_rewards:
            self.reward_pool.remove(reward)
        for part in pinned_parts:
            self.progression_pool.remove(part)

    @staticmethod
    def _pin_keeps_progression_feasible(
        mode: GameMode,
        pins_by_mode: dict[GameMode, int],
        demand_by_subset: dict[frozenset[GameMode], int],
        default_by_mode: dict[GameMode, int],
    ) -> bool:
        """
        Would adding one non-progression default-box pin in `mode` keep every progression mode-subset
        within Hall's condition? For each subset S containing `mode`, the progression forced into S plus
        the non-progression rewards pinned across S must not exceed S's default boxes:
        demand(S) + pins(S) + 1 <= default(S). Only meaningful under cross_mode_placement off.
        """
        for subset, demand in demand_by_subset.items():
            if mode not in subset:
                continue
            pins_in_subset = sum(pins_by_mode[m] for m in subset) + 1
            capacity = sum(default_by_mode[m] for m in subset)
            if demand + pins_in_subset > capacity:
                return False
        return True

    def create_items(self) -> None:
        # Cross-mode placement is enforced entirely by item-rules (see _set_cross_mode_placement_rules):
        # progression and checklist rewards are mode-locked there, so create_items mints everything with
        # no mode awareness and AP's fill enforces the item rules.
        pool: list[str] = []

        # Determine excluded locations. Add in excluded locations only if the respective game modes are
        # enabled, as the locations won't exist in the multiworld if they haven't been enabled.
        excluded_locations = set(self.options.exclude_locations)
        if self.city_trial_enabled:
            excluded_locations |= self.city_trial_excluded_locations
        if self.air_ride_enabled:
            excluded_locations |= self.air_ride_excluded_locations
        if self.top_ride_enabled:
            excluded_locations |= self.top_ride_excluded_locations

        # Remove goal locations from excluded_locations since they don't actually exist as real locations
        excluded_locations -= self.goal_locations_to_exclude

        # Shuffle off: pin native rewards onto their vanilla boxes before counting, so the locked boxes
        # drop out of the tallies below and the minted-item count self-balances against them.
        self._pin_native_rewards(excluded_locations)

        nonexcluded_locations = [
            location
            for location in self.get_locations()
            if location.name not in excluded_locations and not location.locked
        ]
        num_excluded = sum(
            1 for location in self.get_locations() if location.name in excluded_locations and not location.locked
        )

        # Checklist rewards are unique one-time unlocks, each minted exactly once (not draw-with-
        # replacement filler). Filler-classified rewards are eligible for excluded boxes, so they
        # offset the generic filler we mint for those boxes; useful-classified rewards need default
        # locations like progression. _validate_pool_fits_locations guarantees they fit.
        num_reward_filler = sum(
            1 for name in self.reward_pool if not (ITEM_TABLE[name].classification & ItemClassification.useful)
        )

        # One filler per excluded location (get_filler_item_name may roll a trap), minus the filler
        # rewards already destined for those boxes.
        generic_filler = max(0, num_excluded - num_reward_filler)
        pool.extend(self.get_filler_item_name() for _ in range(generic_filler))

        # Progression items. Under cross_mode_placement=false these are item-rule-locked to their
        # source mode(s); multi-mode unlocks (ability/machine/color) may land in any applicable
        # mode. _validate_local_fits_modes guarantees they fit per mode.
        pool.extend(self.progression_pool)

        # Counted-useful items (checkbox fillers, spawn rate up): guaranteed quantities, but
        # non-progression so never mode-locked.
        pool.extend(self.counted_useful_pool)

        pool.extend(self.reward_pool)

        # Remaining locations: random useful items, traps, and filler. None are mode-restricted.
        num_items_left_to_place = (
            len(nonexcluded_locations)
            + num_excluded
            - generic_filler
            - len(self.progression_pool)
            - len(self.counted_useful_pool)
            - len(self.reward_pool)
        )
        has_traps = self.trap_weights and self.options.trap_chance.value > 0
        for _ in range(num_items_left_to_place):
            name: str | None = None
            if has_traps and self.random.random() * 100 < self.options.trap_chance.value:
                name = self._random_trap()
            if name is None and self.useful_pool:
                name = self.random.choice(sorted(self.useful_pool))
            if name is None:
                name = self._random_filler()
            pool.append(name)

        self.multiworld.itempool += [self.create_item(name) for name in pool]

    def _random_trap(self) -> str | None:
        """Pick a random trap weighted by per-type trap weight options, or None if none are enabled."""
        if not self.trap_weights:
            return None
        return self.random.choices(list(self.trap_weights), weights=list(self.trap_weights.values()), k=1)[0]

    def _random_filler(self) -> str:
        """Pick a random filler item. Falls back to the broadest filler set in ITEM_TABLE if
        filler_pool hasn't been built (e.g. the ItemLink path that bypasses _build_item_pools)."""
        eligible = set(self.filler_pool)
        if not eligible:
            eligible = {n for n, d in ITEM_TABLE.items() if d.classification == ItemClassification.filler}
        return self.random.choice(sorted(eligible))

    def get_filler_item_name(self) -> str:
        """Called by the AP framework when the item pool needs additional filler. Rolls a trap when
        traps are enabled (by trap_chance), otherwise returns a plain filler item."""
        if self.trap_weights and self.options.trap_chance.value > 0:
            if self.random.random() * 100 < self.options.trap_chance.value:
                trap = self._random_trap()
                if trap is not None:
                    return trap
        return self._random_filler()

    def pre_fill(self) -> None:
        """
        Under cross_mode_placement off, place the confined non-progression checklist rewards into in-mode
        locations before AP's generic fill.

        AP's greedy remaining_fill is not matching-aware: mode-neutral / multi-mode items can squat a
        constrained mode's scarce default boxes and strand a confined reward even when a valid assignment
        exists (Hall's condition can hold with slack while greedy mis-allocates). Pre-placing the confined
        rewards guarantees each an in-mode home; _validate_local_fits_modes pre-validates capacity so it
        always fits, and progression is left to AP's backtracking fill_restrictive. With shuffle off,
        _pin_native_rewards has already taken what it could, so only leftovers reach here. Side effect:
        rewards become KAR-local under cross-off (no export to other worlds).
        """
        if self.options.cross_mode_placement:
            return
        self._prefill_confined_rewards()

    def _prefill_confined_rewards(self) -> None:
        reward_names = {
            str(name)
            for name, data in ITEM_TABLE.items()
            if data.type in CHECKLIST_REWARD_TYPES and not (data.classification & ItemClassification.progression)
        }
        floating = [
            item for item in self.multiworld.itempool if item.player == self.player and item.name in reward_names
        ]
        if not floating:
            return

        default_sets = {
            GameMode.CITYTRIAL: self.city_trial_default_locations,
            GameMode.AIRRIDE: self.air_ride_default_locations,
            GameMode.TOPRIDE: self.top_ride_default_locations,
        }
        empty_default: dict[GameMode, list[Location]] = {m: [] for m in default_sets}
        empty_excluded: dict[GameMode, list[Location]] = {m: [] for m in default_sets}
        for loc in self.multiworld.get_locations(self.player):
            if loc.address is None or loc.locked or loc.item is not None:
                continue
            if loc.name in self.goal_locations_to_exclude:
                continue
            mode = location_code_to_mode(loc.address)
            if mode is None:
                continue
            (empty_default if loc.name in default_sets[mode] else empty_excluded)[mode].append(loc)
        for bucket in (empty_default, empty_excluded):
            for locs in bucket.values():
                self.random.shuffle(locs)

        # Useful rewards first so they claim default boxes (their only legal home) before filler does.
        def sort_key(item: Item) -> tuple[int, str]:
            return (0 if ITEM_TABLE[item.name].classification & ItemClassification.useful else 1, item.name)

        placed: list[Item] = []
        for item in sorted(floating, key=sort_key):
            data = ITEM_TABLE[item.name]
            modes = data.source_modes & set(default_sets)
            if not modes:
                continue
            mode = next(iter(modes))
            is_useful = bool(data.classification & ItemClassification.useful)
            location = None
            if is_useful:
                if empty_default[mode]:
                    location = empty_default[mode].pop()
            elif empty_excluded[mode]:
                location = empty_excluded[mode].pop()  # filler's proper home
            elif empty_default[mode]:
                location = empty_default[mode].pop()
            if location is None:
                continue  # capacity is pre-validated, so this is unreachable; fall back to greedy fill
            location.place_locked_item(item)
            placed.append(item)

        for item in placed:
            self.multiworld.itempool.remove(item)

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Return the `slot_data` field that will be in the `Connected` network package.
        """
        return dict(
            self.options.as_dict(
                "death_link",
                "energy_link",
                "trap_link",
                "reveal_checklists",
                "trap_chance",
                "city_trial_goal",
                "city_trial_checklist_amount",
                "city_trial_goal_locations",
                "air_ride_goal",
                "air_ride_checklist_amount",
                "air_ride_goal_locations",
                "top_ride_goal",
                "top_ride_checklist_amount",
                "top_ride_goal_locations",
                "city_trial_progressive_patch_caps",
                "city_trial_patch_cap_amount",
                "city_trial_stadiums_gated",
                "spawn_rate_progressive",
                "spawn_rate_min",
                "spawn_rate_max",
                "city_trial_events_gated",
                "abilities_gated",
                "city_trial_patches_gated",
                "city_trial_items_gated",
                "machines_gated",
                "city_trial_boxes_gated",
                "air_ride_courses_gated",
                "colors_gated",
                "top_ride_courses_gated",
                "top_ride_items_gated",
                "checklist_rewards_gated",
            )
        )
