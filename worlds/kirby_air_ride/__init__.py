from collections.abc import Mapping
from itertools import combinations
from typing import Any, ClassVar

from BaseClasses import ItemClassification, Tutorial
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
    GATING_CATEGORIES,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    STADIUM_UNLOCK_TO_CHECKLIST_REWARD,
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
        # target (50) on every stat in one trial round; pool is heavy on Patch Cap Increase and
        # Spawn Rate Up items; most gating is off so the patch-cap items fit. The patch-cap target
        # and spawn-rate ceiling are kept modest so the guaranteed counted items fit even in a
        # CT-only single-world pool. Players can still enable AR and/or TR for more locations.
        "Max Stats Insanity": {
            "city_trial_goal": "max_stats_in_one_run",
            "city_trial_patch_cap_amount": 50,
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
            "city_trial_progressive_stadiums": False,
            "city_trial_permanent_patches": False,
        },
    }


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
        self.trap_weights: dict[str, int] = {}
        self.progression_pool: list[str] = []
        self.counted_useful_pool: list[str] = []
        self.stadium_starter_choice: KARItemName | None = None
        self.goal_locations_to_exclude: set[str] = set()
        self.stadium_rewards_as_progression: set[str] = set()
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
          - Stadiums (when city_trial_progressive_stadiums + CT): excludes the 6 stadium
            unlocks that double as checklist rewards, plus VS King Dedede when it's the goal.
          - Machines (when machines_gated + CT or AR): excludes Hydra/Dragoon (legendary).
          - Patch types (when city_trial_patches_gated + CT).
          - Air Ride courses (when air_ride_courses_gated + AR).
          - Top Ride courses (when top_ride_courses_gated + TR).

        Deliberately skipped (playable without): events, abilities, boxes, CT items, TR items,
        colors (Pink is the implicit default starter).
        """
        if self.city_trial_enabled and self.options.city_trial_progressive_stadiums:
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
                stadiums: list[KARItemName] = [
                    s for s in STADIUM_UNLOCK_ITEMS if s not in STADIUM_UNLOCK_TO_CHECKLIST_REWARD
                ]
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
        # exclude a category's unlock items when its gate is OFF or no relevant mode is
        # enabled. When the gate is ON, exclude the overlapping checklist rewards instead
        # so only the UNLOCK items handle that content.
        excluded: set[str] = set()
        for cat in GATING_CATEGORIES:
            gated_off = not getattr(self.options, cat.option)
            no_mode = cat.required_modes and not any(getattr(self, mode) for mode in cat.required_modes)
            if gated_off or no_mode:
                excluded |= items_by_type[cat.item_type]
            elif cat.overlapping_rewards:
                excluded |= set(cat.overlapping_rewards)

        # Mode-specific checklist rewards - excluded when their mode is disabled.
        # Without this, with cross_mode_placement off, rewards have no valid landing spots.
        if not self.air_ride_enabled:
            excluded |= items_by_type[KARItemType.AR_CHECKLIST_REWARD]
        if not self.top_ride_enabled:
            excluded |= items_by_type[KARItemType.TR_CHECKLIST_REWARD]
        if not self.city_trial_enabled:
            excluded |= items_by_type[KARItemType.CT_CHECKLIST_REWARD]

        # Stadium unlocks: excluded unless CT enabled AND progressive stadiums ON.
        # When progressive stadiums IS on, the 6 unlock items that overlap with
        # checklist rewards are still excluded; those stadiums are gated by their
        # checklist reward items instead (promoted to progression).
        if not self.city_trial_enabled or not self.options.city_trial_progressive_stadiums:
            excluded |= items_by_type[KARItemType.CT_STADIUM_UNLOCK]
        else:
            excluded |= set(STADIUM_UNLOCK_TO_CHECKLIST_REWARD.keys())
            self.stadium_rewards_as_progression = set(STADIUM_UNLOCK_TO_CHECKLIST_REWARD.values())

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
            if item_name in self.stadium_rewards_as_progression:
                classification = ItemClassification.progression

            if classification & ItemClassification.progression:
                quantity = self._get_item_quantity(item_name, item_data)
                self.progression_pool.extend([item_name] * quantity)
            elif item_data.type in (KARItemType.CHECKBOX_FILLER, KARItemType.SPAWN_RATE):
                quantity = self._get_item_quantity(item_name, item_data)
                self.counted_useful_pool.extend([item_name] * quantity)
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
        self._validate_pool_fits_locations()
        if not self.options.cross_mode_placement:
            self._validate_progression_fits_modes()

    def _validate_pool_fits_locations(self) -> None:
        """
        Verify that progression + counted-useful items will fit in the available default
        (non-excluded) location count. Runs after _build_item_pools so the pool sizes
        are final. Raises OptionError with a hint about the likely culprit options.
        """
        default_count = 0
        for enabled, default_locs in [
            (self.city_trial_enabled, self.city_trial_default_locations),
            (self.air_ride_enabled, self.air_ride_default_locations),
            (self.top_ride_enabled, self.top_ride_default_locations),
        ]:
            if not enabled:
                continue
            default_count += sum(
                1
                for loc in default_locs
                if loc not in self.goal_locations_to_exclude and loc not in self.options.exclude_locations
            )

        guaranteed_count = len(self.progression_pool) + len(self.counted_useful_pool)
        if guaranteed_count <= default_count:
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
        raise OptionError(
            f"Guaranteed item pool ({guaranteed_count} items) exceeds available default locations "
            f"({default_count}). Reduce option values or enable more modes / progression flags to "
            f"make room.{hint_str}"
        )

    def _validate_progression_fits_modes(self) -> None:
        """
        Under cross_mode_placement=false, progression items are item-rule-locked to their source
        mode(s), so each enabled mode's locations must hold the progression that can only land there.
        Multi-mode progression (abilities/machines/colors) may go in any of its modes, making this a
        bipartite feasibility check: for every subset S of enabled modes, the progression whose source
        modes all fall within S must fit S's combined default locations (Hall's condition, exact for
        the at-most-three modes here). Raises OptionError naming the overcommitted modes so the player
        gets a clear message instead of a downstream FillError.
        """
        mode_locs: dict[GameMode, int] = {}
        for mode_enum, enabled, default_locs in [
            (GameMode.CITYTRIAL, self.city_trial_enabled, self.city_trial_default_locations),
            (GameMode.AIRRIDE, self.air_ride_enabled, self.air_ride_default_locations),
            (GameMode.TOPRIDE, self.top_ride_enabled, self.top_ride_default_locations),
        ]:
            if not enabled:
                continue
            mode_locs[mode_enum] = sum(
                1
                for loc in default_locs
                if loc not in self.goal_locations_to_exclude and loc not in self.options.exclude_locations
            )
        enabled_set = frozenset(mode_locs)

        # Effective placement modes of each progression item, intersected with the enabled set.
        # Empty source_modes means mode-neutral progression, placeable in any enabled mode.
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

        modes = sorted(enabled_set, key=lambda m: m.value)
        for r in range(1, len(modes) + 1):
            for subset in combinations(modes, r):
                subset_set = frozenset(subset)
                demand = sum(1 for eff in prog_effective if eff <= subset_set)
                capacity = sum(mode_locs[m] for m in subset)
                if demand > capacity:
                    mode_names = ", ".join(m.name for m in subset)
                    raise OptionError(
                        f"Cross-mode placement is off, but {demand} progression items can only be placed "
                        f"in mode(s) [{mode_names}], which have {capacity} available locations between them. "
                        f"Enable cross_mode_placement, enable more modes, reduce gating / progressive options, "
                        f"or turn on more progression location flags to make room."
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
        When cross_mode_placement is off, lock our own PROGRESSION items to their declared source
        mode(s): a mode-tagged progression item only lands at a location of one of its source modes,
        keeping each mode's required progression reachable by playing that mode. Non-progression
        items (checklist rewards, traps, filler, counted-useful) gate nothing and are left
        unrestricted, so they may land in any mode. Progression with empty source_modes is
        mode-neutral and unrestricted. Items from other worlds (item.player != self.player) are
        remote and unaffected.
        """
        if self.options.cross_mode_placement:
            return

        player = self.player
        for location in self.get_locations():
            loc_mode = location_code_to_mode(location.address)
            if loc_mode is None:
                continue
            add_item_rule(
                location,
                lambda item, lm=loc_mode, p=player: (
                    item.player != p
                    or not (item.classification & ItemClassification.progression)
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
            if name in self.stadium_rewards_as_progression:
                data = data._replace(classification=ItemClassification.progression)
            return KARItem.from_data(str(name), self.player, data)
        raise KeyError(f"Invalid item name: {name}")

    def create_items(self) -> None:
        # Cross-mode placement is purely a progression concern (see _set_cross_mode_placement_rules):
        # only progression items are mode-locked, so create_items mints everything with no mode
        # awareness and AP's fill enforces the item rules.
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

        nonexcluded_locations = [
            location
            for location in self.get_locations()
            if location.name not in excluded_locations and not location.locked
        ]
        num_excluded = sum(
            1 for location in self.get_locations() if location.name in excluded_locations and not location.locked
        )

        # One filler per excluded location (get_filler_item_name may roll a trap).
        pool.extend(self.get_filler_item_name() for _ in range(num_excluded))

        # Progression items. Under cross_mode_placement=false these are item-rule-locked to their
        # source mode(s); multi-mode unlocks (ability/machine/color) may land in any applicable
        # mode. _validate_progression_fits_modes guarantees they fit per mode.
        pool.extend(self.progression_pool)

        # Counted-useful items (checkbox fillers, spawn rate up): guaranteed quantities, but
        # non-progression so never mode-locked.
        pool.extend(self.counted_useful_pool)

        # Remaining locations: random useful items, traps, and filler. None are mode-restricted.
        num_items_left_to_place = (
            len(nonexcluded_locations) - len(self.progression_pool) - len(self.counted_useful_pool)
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
                "city_trial_progressive_stadiums",
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
            )
        )
