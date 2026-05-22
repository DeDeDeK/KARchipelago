from collections.abc import Mapping
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
    GATED_CHECKLIST_REWARDS,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    STADIUM_UNLOCK_TO_CHECKLIST_REWARD,
    TRAP_WEIGHT_GROUPS,
    KARItem,
    KARItemData,
    KARItemName,
    KARItemType,
    item_name_groups,
)
from .KARLocations import (
    AIR_RIDE_GOAL_TO_LOCATION,
    AIR_RIDE_LOCATION_TABLE,
    CITY_TRIAL_GOAL_TO_LOCATION,
    CITY_TRIAL_LOCATION_TABLE,
    LOCATION_TABLE,
    TOP_RIDE_GOAL_TO_LOCATION,
    TOP_RIDE_LOCATION_TABLE,
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
    """
    Launch Kirby Air Ride client.
    """
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
    This class handles the web interface for Kirby Air Ride.

    The web interface includes the setup guide and the options page for generating YAMLs.
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
        # target (127) on every stat in one trial round; pool is heavy on Patch Cap Increase and
        # Spawn Rate Up items; most gating is off so the patch-cap items fit. Players will likely
        # also want to enable AR and/or TR with low-effort goals to add more locations.
        "Max Stats Insanity": {
            "city_trial_goal": "max_stats_in_one_run",
            "city_trial_patch_cap_amount": 127,
            "city_trial_progressive_patch_caps": True,
            "spawn_rate_progressive": True,
            "spawn_rate_min": 100,
            "spawn_rate_max": 500,
            "air_ride_goal": "n_checklist_blocks",
            "air_ride_checklist_amount": 20,
            "top_ride_goal": "n_checklist_blocks",
            "top_ride_checklist_amount": 20,
            # Disable most gating so the pool isn't dominated by unlock items.
            "events_gated": False,
            "abilities_gated": False,
            "patches_gated": False,
            "city_trial_items_gated": False,
            "machines_gated": False,
            "boxes_gated": False,
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

    item_name_groups: ClassVar[dict[str, set[str]]] = {k: {str(v) for v in vs} for k, vs in item_name_groups.items()}
    location_name_groups: ClassVar[dict[str, set[str]]] = {
        k: {str(v) for v in vs} for k, vs in location_name_groups.items()
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

        # Flat pools of useful and filler items. Each item carries its own source_modes
        # (frozenset of GameMode) in ITEM_TABLE — sampling consults that field to enforce
        # cross-mode constraints rather than pre-bucketing here. Empty source_modes means
        # the item is mode-neutral (places anywhere).
        self.useful_pool: set[str] = set()
        self.filler_pool: set[str] = set()
        # Maps each enabled trap item to its weight (the per-category trap_weight_* option
        # value). Empty when no traps are eligible. Sampled with random.choices.
        self.trap_weights: dict[str, int] = {}
        self.progression_pool: list[str] = []
        self.counted_useful_pool: list[str] = []
        self.stadium_starter_choice: KARItemName | None = None
        self.goal_locations_to_exclude: set[str] = set()
        self.stadium_rewards_as_progression: set[str] = set()

        # One random starter per gated category to avoid soft-locking the player at boot.
        # Each is filled by _determine_starter_items() in generate_early if the player
        # didn't preset an item from that category in start_inventory.
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
                (not self.options.city_trial_progression_high_effort, location_name_groups["City Trial: High Effort"]),
                (not self.options.city_trial_progression_multiplayer, location_name_groups["City Trial: Multiplayer"]),
                (not self.options.city_trial_progression_free_run, location_name_groups["City Trial: Free Run"]),
                (not self.options.city_trial_progression_rng, location_name_groups["City Trial: RNG"]),
                (
                    not self.options.city_trial_progression_bust_vehicles,
                    location_name_groups["City Trial: Bust Vehicle on Vehicle"],
                ),
            ],
        )

        self.air_ride_default_locations, self.air_ride_excluded_locations = self._categorize_locations(
            AIR_RIDE_LOCATION_TABLE,
            [
                (not self.options.air_ride_progression_high_effort, location_name_groups["Air Ride: High Effort"]),
                (not self.options.air_ride_progression_free_run, location_name_groups["Air Ride: Free Run"]),
                (not self.options.air_ride_progression_time_attack, location_name_groups["Air Ride: Time Attack"]),
            ],
        )

        self.top_ride_default_locations, self.top_ride_excluded_locations = self._categorize_locations(
            TOP_RIDE_LOCATION_TABLE,
            [
                (not self.options.top_ride_progression_high_effort, location_name_groups["Top Ride: High Effort"]),
                (not self.options.top_ride_progression_free_run, location_name_groups["Top Ride: Free Run"]),
                (not self.options.top_ride_progression_time_attack, location_name_groups["Top Ride: Time Attack"]),
                (not self.options.top_ride_progression_multiplayer, location_name_groups["Top Ride: Multiplayer"]),
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
        Pre-determine one random starter item per gated category that the player should not
        boot into without. Each is push_precollected in generate_early. Categories handled:
          - Stadiums (excludes the 6 stadium unlocks that double as checklist rewards, plus
            VS King Dedede when that's the goal) when city_trial_progressive_stadiums and
            CT enabled
          - Machines (excludes Hydra/Dragoon — special legendary vehicles) when machines_gated
            and CT or AR enabled
          - Patch types when patches_gated and CT enabled
          - Air Ride courses when air_ride_courses_gated and AR enabled
          - Top Ride courses when top_ride_courses_gated and TR enabled

        Categories deliberately skipped (player can play without): events, abilities, boxes,
        CT items, TR items, colors (Pink is the implicit default starter).
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
            machines = item_name_groups["Machine Unlocks"] - {
                KARItemName.UNLOCK_MACHINE_HYDRA,
                KARItemName.UNLOCK_MACHINE_DRAGOON,
            }
            self.machine_starter_choice = self._pick_random_starter(machines)

        if self.city_trial_enabled and self.options.patches_gated:
            self.patch_starter_choice = self._pick_random_starter(item_name_groups["Patch Type Unlocks"])

        if self.air_ride_enabled and self.options.air_ride_courses_gated:
            self.ar_course_starter_choice = self._pick_random_starter(item_name_groups["AR Course Unlocks"])

        if self.top_ride_enabled and self.options.top_ride_courses_gated:
            self.tr_course_starter_choice = self._pick_random_starter(item_name_groups["TR Course Unlocks"])

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
        Determine which items are excluded, then sort the remaining items into pools
        (progression, useful, filler, trap) for placement during create_items().
        """

        def items_of_type(item_type: KARItemType) -> set[str]:
            return {n for n, d in ITEM_TABLE.items() if d.type == item_type}

        def items_matching(item_filter: KARItemType | str) -> set[str]:
            if isinstance(item_filter, KARItemType):
                return items_of_type(item_filter)
            return set(item_name_groups[item_filter])

        # Gating categories — exclude when gating is OFF or no relevant mode is enabled
        gating_config: list[tuple[str, KARItemType | str, set[str]]] = [
            ("events_gated", KARItemType.EVENT_UNLOCK, {"city_trial_enabled"}),
            # TR is included because _ABILITY_TR_ITEM_RULES gates 3 TR locations (Fire/Bomb)
            # behind ability unlocks whenever abilities_gated is on.
            (
                "abilities_gated",
                KARItemType.ABILITY_UNLOCK,
                {"city_trial_enabled", "air_ride_enabled", "top_ride_enabled"},
            ),
            ("patches_gated", KARItemType.PATCH_UNLOCK, {"city_trial_enabled"}),
            ("city_trial_items_gated", KARItemType.ITEM_UNLOCK, {"city_trial_enabled"}),
            ("machines_gated", KARItemType.MACHINE_UNLOCK, {"city_trial_enabled", "air_ride_enabled"}),
            ("boxes_gated", KARItemType.BOX_UNLOCK, {"city_trial_enabled"}),
            ("air_ride_courses_gated", "AR Course Unlocks", {"air_ride_enabled"}),
            ("colors_gated", KARItemType.COLOR_UNLOCK, set()),
            ("top_ride_courses_gated", "TR Course Unlocks", {"top_ride_enabled"}),
            ("top_ride_items_gated", KARItemType.TOPRIDE_ITEM_UNLOCK, {"top_ride_enabled"}),
        ]

        excluded: set[str] = set()
        for gated_attr, item_filter, required_modes in gating_config:
            gated_off = not getattr(self.options, gated_attr)
            no_mode = required_modes and not any(getattr(self, mode) for mode in required_modes)
            if gated_off or no_mode:
                excluded |= items_matching(item_filter)
            elif gated_attr in GATED_CHECKLIST_REWARDS:
                # Gating is ON — exclude the overlapping checklist rewards so only
                # the UNLOCK items handle this functionality.
                excluded |= GATED_CHECKLIST_REWARDS[gated_attr]

        # Mode-specific checklist rewards — excluded when their mode is disabled.
        # Without this, with cross_mode_placement off, rewards have no valid landing spots.
        if not self.air_ride_enabled:
            excluded |= item_name_groups["Air Ride Rewards"]
        if not self.top_ride_enabled:
            excluded |= item_name_groups["Top Ride Rewards"]
        if not self.city_trial_enabled:
            excluded |= item_name_groups["City Trial Rewards"]

        # Stadium unlocks — excluded unless CT enabled AND progressive stadiums ON.
        # When progressive stadiums IS on, the 6 unlock items that overlap with
        # checklist rewards are still excluded — those stadiums are gated by their
        # checklist reward items instead (promoted to progression).
        if not self.city_trial_enabled or not self.options.city_trial_progressive_stadiums:
            excluded |= items_of_type(KARItemType.STADIUM_UNLOCK)
        else:
            excluded |= set(STADIUM_UNLOCK_TO_CHECKLIST_REWARD.keys())
            self.stadium_rewards_as_progression = set(STADIUM_UNLOCK_TO_CHECKLIST_REWARD.values())

        # Permanent patches — excluded unless CT enabled AND option ON
        if not self.city_trial_enabled or not self.options.city_trial_permanent_patches:
            excluded |= items_of_type(KARItemType.PERMANENT_PATCH)

        # Patch cap increase — excluded unless CT enabled AND progressive caps ON
        if not self.city_trial_enabled or not self.options.city_trial_progressive_patch_caps:
            excluded.add(KARItemName.PATCH_CAP_INCREASE)

        # Effect items. SPAWN_RATE_UP is typed EFFECT but governed by spawn_rate_progressive,
        # not effect_items_enabled — exclude it via that option only.
        if not self.options.effect_items_enabled:
            excluded |= items_of_type(KARItemType.EFFECT) - {KARItemName.SPAWN_RATE_UP}

        # Spawn Rate Up — excluded unless progressive spawn rate is ON and there's room to grow.
        if (
            not self.options.spawn_rate_progressive
            or self.options.spawn_rate_max.value <= self.options.spawn_rate_min.value
        ):
            excluded.add(KARItemName.SPAWN_RATE_UP)

        # Top Ride item gives — spawn an item at the player's Kirby position. Only
        # effective in a Top Ride scene, so exclude when Top Ride is disabled.
        # Also folded under effect_items_enabled (these are in-race effect items).
        if not self.top_ride_enabled or not self.options.effect_items_enabled:
            excluded |= items_of_type(KARItemType.TOPRIDE_ITEM_GIVE)

        # Drop Patches Trap — only meaningful in City Trial (the mod's handler
        # guards on Gm_IsInCity), and only when traps are enabled at all.
        if not self.city_trial_enabled or self.options.trap_chance.value == 0:
            excluded.add(KARItemName.DROP_PATCHES_TRAP)

        # Checkbox fillers — excluded per mode when mode disabled or amount is 0
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

        # Precollected starter items (one per gated category — see _determine_starter_items).
        # Exclude start_inventory items of each category plus the random pick so they don't
        # show up in the multiworld pool a second time.
        starter_groups: list[tuple[str | None, set[str]]] = [
            (self.stadium_starter_choice, set(STADIUM_UNLOCK_ITEMS)),
            (self.machine_starter_choice, item_name_groups["Machine Unlocks"]),
            (self.patch_starter_choice, item_name_groups["Patch Type Unlocks"]),
            (self.ar_course_starter_choice, item_name_groups["AR Course Unlocks"]),
            (self.tr_course_starter_choice, item_name_groups["TR Course Unlocks"]),
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
            elif item_data.type == KARItemType.CHECKBOX_FILLER or item_name == KARItemName.SPAWN_RATE_UP:
                # SPAWN_RATE_UP's docstring promises a specific count tied to the min/max range;
                # routing it through counted_useful_pool enforces that, rather than dropping it
                # into useful_pool where it would be sampled randomly.
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

    def create_regions(self) -> None:
        """Method for creating and connecting regions for the World."""
        create_regions(self)

    def set_rules(self) -> None:
        """Method for setting the rules on the World's regions and locations."""
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
        When cross_mode_placement is off, restrict our own mode-tagged items so each one
        only lands at a location belonging to one of its declared source modes. Items with
        empty source_modes are mode-neutral and unrestricted. Items from other worlds
        (item.player != self.player) are unaffected — they're remote and not under our control.
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
                    item.player != p or not (sm := getattr(item, "source_modes", frozenset())) or lm in sm
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

        # Filler for excluded locations. Under cross_mode_placement=false, _pick_filler
        # restricts to neutral + target_mode so the item-rule can't reject the placement.
        # Under cross_mode_placement=true, target_mode is ignored.
        for loc_name in excluded_locations:
            loc_mode = location_code_to_mode(self.get_location(loc_name).address)
            pool.append(self._pick_filler(loc_mode))

        # Add items with guaranteed quantities (progression items + counted useful items like checkbox fillers).
        # _validate_pool_fits_locations() in generate_early already enforced that this fits.
        pool.extend(self.progression_pool)
        pool.extend(self.counted_useful_pool)
        num_items_left_to_place = (
            len(nonexcluded_locations) - len(self.progression_pool) - len(self.counted_useful_pool)
        )

        # Fill remaining locations with a mix of useful items and traps. Under cross-mode-off,
        # mode_capacity caps how many mode-locked rewards we add per mode so fill can't over-
        # commit (which would explode remaining_fill). Under cross-mode-on, capacity is unused.
        mode_capacity: dict[GameMode, int] | None = (
            None if self.options.cross_mode_placement else self._compute_initial_mode_capacity(nonexcluded_locations)
        )
        has_traps = self.trap_weights and self.options.trap_chance.value > 0
        for _ in range(num_items_left_to_place):
            if has_traps and self.random.random() * 100 < self.options.trap_chance.value:
                pool.append(self._pick_trap())
                continue
            picked = self._sample_useful(mode_capacity)
            if picked is None:
                # All mode capacity hit zero and no neutral useful items — fall back to
                # neutral filler (target_mode=None forces neutral-only under cross-mode-off).
                picked = self._pick_filler(None)
            pool.append(picked)

        self.multiworld.itempool += [self.create_item(name) for name in pool]

    def _compute_initial_mode_capacity(self, nonexcluded_locations: list) -> dict[GameMode, int]:
        """
        Per-mode remaining capacity for the random-fill phase: mode_M nonexcluded locations
        minus items already committed (progression + counted_useful) that consume mode_M's
        capacity. Multi-mode items charge one of their source modes weighted by remaining
        capacity (see _charge_to_mode).

        Only meaningful under cross_mode_placement=false, where source-mode tags constrain
        placement to one of the item's source modes.
        """
        mode_remaining: dict[GameMode, int] = dict.fromkeys(GameMode, 0)
        for loc in nonexcluded_locations:
            m = location_code_to_mode(loc.address)
            if m is not None:
                mode_remaining[m] += 1
        for name in self.progression_pool + self.counted_useful_pool:
            data = ITEM_TABLE.get(name)
            if data is None:
                continue
            self._charge_to_mode(data.source_modes, mode_remaining)
        return mode_remaining

    def _charge_to_mode(self, source_modes: frozenset[GameMode], mode_capacity: dict[GameMode, int]) -> None:
        """Decrement one of the item's source modes from mode_capacity, weighted by remaining
        capacity (proportional charging). No-op for mode-neutral items (empty source_modes)."""
        if not source_modes:
            return
        eligible = [m for m in source_modes if mode_capacity.get(m, 0) > 0]
        if eligible:
            weights = [mode_capacity[m] for m in eligible]
        else:
            # All of the item's modes already at zero — charge anyway so the over-commit
            # shows up in the accounting instead of being silently swallowed.
            eligible = sorted(source_modes, key=lambda m: m.value)
            weights = [1] * len(eligible)
        chosen = self.random.choices(eligible, weights=weights, k=1)[0]
        mode_capacity[chosen] -= 1

    def _pick_trap(self) -> str:
        """Pick a random trap, weighted by per-type trap weight options. Caller must check
        that trap_weights is non-empty and that a trap_chance roll has succeeded."""
        return self.random.choices(
            list(self.trap_weights.keys()),
            weights=list(self.trap_weights.values()),
            k=1,
        )[0]

    def _pick_filler(self, target_mode: GameMode | None) -> str:
        """
        Pick a filler item (or trap, by trap_chance roll).

        Under cross_mode_placement=true, any filler is eligible regardless of target_mode.
        Under cross_mode_placement=false:
          - target_mode=GameMode.X → items with empty source_modes or containing X.
          - target_mode=None → only items with empty source_modes (safe at any location).
        Falls back to the broadest filler set in ITEM_TABLE if filler_pool hasn't been built
        (e.g. ItemLink generation) or the restricted eligibility set is empty.
        """
        if self.trap_weights and self.options.trap_chance.value > 0:
            if self.random.random() * 100 < self.options.trap_chance.value:
                return self._pick_trap()

        if self.options.cross_mode_placement:
            eligible = set(self.filler_pool)
        elif target_mode is None:
            eligible = {n for n in self.filler_pool if not ITEM_TABLE[n].source_modes}
        else:
            eligible = {
                n
                for n in self.filler_pool
                if not ITEM_TABLE[n].source_modes or target_mode in ITEM_TABLE[n].source_modes
            }

        if not eligible:
            # Pool was empty (pathological config or ItemLink path that bypasses _build_item_pools).
            # Fall back to any filler item declared in ITEM_TABLE so the framework gets a name.
            eligible = {n for n, d in ITEM_TABLE.items() if d.classification == ItemClassification.filler}
        return self.random.choice(sorted(eligible))

    def _sample_useful(self, mode_capacity: dict[GameMode, int] | None) -> str | None:
        """
        Pick a random useful item. When mode_capacity is None (cross_mode_placement=true),
        sample uniformly from useful_pool. When mode_capacity is provided (cross-mode-off),
        an item is eligible if it's mode-neutral (empty source_modes) or its source_modes
        intersects with the set of modes still holding capacity. After picking, charge one
        of the item's source modes (weighted by remaining capacity).

        Returns None when no eligible items remain (caller should fall back to filler).
        """
        if mode_capacity is None:
            eligible = self.useful_pool
        else:
            active_modes = {m for m, cap in mode_capacity.items() if cap > 0}
            eligible = {
                n
                for n in self.useful_pool
                if not ITEM_TABLE[n].source_modes or (ITEM_TABLE[n].source_modes & active_modes)
            }
        if not eligible:
            return None
        picked = self.random.choice(sorted(eligible))
        if mode_capacity is not None:
            self._charge_to_mode(ITEM_TABLE[picked].source_modes, mode_capacity)
        return picked

    def get_filler_item_name(self) -> str:
        """
        Called by the AP framework when the item pool needs additional filler. The caller has
        no location context, so under cross-mode-off we restrict to neutral filler (safe at
        any location); under cross-mode-on, any filler is eligible.
        """
        return self._pick_filler(None)

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Return the `slot_data` field that will be in the `Connected` network package.
        """
        data = dict(
            self.options.as_dict(
                # General
                "death_link",
                "energy_link",
                "trap_link",
                "reveal_checklists",
                "trap_chance",
                "effect_items_enabled",
                # Goals
                "city_trial_goal",
                "city_trial_checklist_amount",
                "city_trial_goal_locations",
                "air_ride_goal",
                "air_ride_checklist_amount",
                "air_ride_goal_locations",
                "top_ride_goal",
                "top_ride_checklist_amount",
                "top_ride_goal_locations",
                # City Trial specifics
                "city_trial_progressive_patch_caps",
                "city_trial_patch_cap_amount",
                "city_trial_progressive_stadiums",
                # Item generation
                "spawn_rate_progressive",
                "spawn_rate_min",
                "spawn_rate_max",
                # Gating
                "events_gated",
                "abilities_gated",
                "patches_gated",
                "city_trial_items_gated",
                "machines_gated",
                "boxes_gated",
                "air_ride_courses_gated",
                "colors_gated",
                "top_ride_courses_gated",
                "top_ride_items_gated",
            )
        )
        # The mod only consumes a single spawn rate floor. When progressive is off,
        # ship vanilla baseline (100) so no static rate elevation is applied.
        if not self.options.spawn_rate_progressive:
            data["spawn_rate_min"] = 100
        return data
