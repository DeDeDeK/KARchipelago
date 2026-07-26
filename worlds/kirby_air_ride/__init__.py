from collections.abc import Mapping
from typing import Any, ClassVar, NamedTuple

from BaseClasses import ItemClassification, Location, Tutorial
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

from .KARData import GameMode
from .KARItems import (
    ALLOWED_ITEM_CATEGORY_ITEMS,
    CHECKLIST_REWARD_TYPES,
    GATING_CATEGORIES,
    ITEM_TABLE,
    STADIUM_UNLOCK_ITEMS,
    TRAP_CATEGORIES,
    GatingCategory,
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
    AP_CHECKLIST_LOCATION_TABLE,
    ARCHIPELAGO_GOAL_TO_LOCATION,
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
    ArchipelagoGoal,
    CityTrialGoal,
    KAROptions,
    TopRideGoal,
    kar_option_groups,
)
from .KARRegions import REGION_TO_MODE, create_regions
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
        # Max Stats Insanity bundles a runnable seed: City Trial goal is hitting the patch cap target
        # (30) on every stat in one round; pool is heavy on Patch Cap Increase and Spawn Rate Up, most
        # gating off so they fit. Target and ceiling stay modest so the counted items fit even a CT-only
        # single-world pool. Players can still enable AR/TR for more locations.
        "Max Stats Insanity": {
            "city_trial_goal": "max_stats_in_one_run",
            "city_trial_patch_cap_min": 1,
            "city_trial_patch_cap_max": 30,
            "spawn_rate_min": 100,
            "spawn_rate_max": 300,
            "air_ride_goal": "n_checklist_blocks",
            "air_ride_checklist_amount": 20,
            "top_ride_goal": "n_checklist_blocks",
            "top_ride_checklist_amount": 20,
            # Disable most gating so the pool isn't dominated by unlock items.
            "city_trial_events_gated": False,
            "abilities_gated": False,
            "base_abilities_gated": False,
            "city_trial_patches_gated": False,
            "city_trial_items_gated": False,
            "machines_gated": False,
            "city_trial_boxes_gated": False,
            "air_ride_courses_gated": False,
            "colors_gated": False,
            "top_ride_courses_gated": False,
            "top_ride_items_gated": False,
            "city_trial_stadiums_gated": False,
            # Keep the preset's "no permanent patches" intent; all other give categories stay on.
            "allowed_items": [
                "City Trial Item Gives",
                "City Trial Event Gives",
                "Copy Ability Gives",
                "Top Ride Item Gives",
            ],
        },
    }


class _CapacityModel(NamedTuple):
    """Location budget and reward demand, computed once and shared by the capacity validators
    (_validate_pool_fits_locations, _validate_allowed_items_filler) and the reward-pin budgeter
    (_reward_pin_filler_headroom). Items float freely across the player's enabled modes, so only
    global totals matter. All counts derive from the location name-sets and the built item pools, so
    the model is pre-pin and stays valid through create_items' pin step.

    total_default: real, non-goal, non-user-excluded default boxes across all enabled modes.
    total_excluded: real, non-goal excluded (filler-only) boxes across all enabled modes.
    useful_rewards / filler_rewards: in-pool checklist rewards split by classification.
    """

    total_default: int
    total_excluded: int
    useful_rewards: int
    filler_rewards: int


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
        self.archipelago_enabled: bool = False
        self.archipelago_default_locations: set[str] = set()
        self.archipelago_excluded_locations: set[str] = set()
        # The gating categories that really hold keys this seed (option names). Computed in
        # generate_early; see _compute_effective_gates for why this differs from the raw YAML toggles.
        self.effective_gates: set[str] = set()
        # The modes whose region trees are built. A superset of the modes with a goal; see
        # _compute_logic_modes.
        self.logic_modes: set[GameMode] = set()
        self.useful_pool: set[str] = set()
        self.filler_pool: set[str] = set()
        self.reward_pool: list[str] = []
        # Shared location capacity/demand model, built once in generate_early after the pools are
        # built; read by the capacity validators and the pin budgeter.
        self._capacity_model: _CapacityModel | None = None
        # Native checklist rewards pinned back onto their vanilla boxes (shuffle_checklist_rewards off).
        # Maps location name -> reward item name; populated in create_items via _pin_native_rewards.
        self.pinned_native_rewards: dict[str, str] = {}
        self.trap_pool: set[str] = set()
        self.item_pools_built: bool = False
        self.progression_pool: list[str] = []
        self.counted_useful_pool: list[str] = []
        self.stadium_starter_choice: KARItemName | None = None
        self.goal_locations_to_exclude: set[str] = set()
        self.machine_starter_choice: str | None = None
        self.tr_machine_starter_choice: str | None = None
        self.ar_course_starter_choice: str | None = None
        self.tr_course_starter_choice: str | None = None
        self.color_starter_choice: str | None = None

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

        # The Archipelago checklist has no progression sub-flags, so every AP location is DEFAULT.
        self.archipelago_default_locations, self.archipelago_excluded_locations = self._categorize_locations(
            AP_CHECKLIST_LOCATION_TABLE,
            [],
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
            (self.archipelago_enabled, self.options.archipelago_goal, ARCHIPELAGO_GOAL_TO_LOCATION),
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
          - Air Ride courses (when air_ride_courses_gated + AR).
          - Top Ride courses (when top_ride_courses_gated + TR).
          - Colors (when colors_gated): any of the 8 Kirby colors, Pink included - the mod
            falls back to Pink only when no color is unlocked, so Pink is a valid starter.
            Colors are a deliberate cosmetic-variety exception to the "needed to play" rule
            below; every other starter opens a mode's core loop.

        Deliberately skipped (playable without): events, abilities, boxes, CT items, TR items,
        patch types.
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
                # Exclude TR-only machines
                KARItemName.UNLOCK_MACHINE_FREE_STAR,
                KARItemName.UNLOCK_MACHINE_STEER_STAR,
            }
            self.machine_starter_choice = self._pick_random_starter(machines)

        # Top Ride needs Free or Steer to start at all - the mod hard-gates the Top Ride lobby on one
        # of them. Mirror the AR/CT machine starter so a machine-gated Top Ride is playable from the
        # start (and the _TR-tagged Free/Steer unlocks have a reachable home).
        if self.top_ride_enabled and self.options.machines_gated:
            self.tr_machine_starter_choice = self._pick_random_starter(
                {KARItemName.UNLOCK_MACHINE_FREE_STAR, KARItemName.UNLOCK_MACHINE_STEER_STAR}
            )

        if self.air_ride_enabled and self.options.air_ride_courses_gated:
            self.ar_course_starter_choice = self._pick_random_starter(items_by_type[KARItemType.AR_COURSE_UNLOCK])

        if self.top_ride_enabled and self.options.top_ride_courses_gated:
            self.tr_course_starter_choice = self._pick_random_starter(items_by_type[KARItemType.TR_COURSE_UNLOCK])

        # Colors apply across all modes (no required_modes), and at least one mode is always
        # enabled, so the gate alone decides.
        if self.options.colors_gated:
            self.color_starter_choice = self._pick_random_starter(items_by_type[KARItemType.COLOR_UNLOCK])

    def _compute_logic_modes(self) -> set[GameMode]:
        """
        The modes whose region trees get built: every mode with a goal, plus every mode an Archipelago
        checklist box names, when the AP checklist is on.

        An AP box lives in the region where its activity happens - a "win a race on Magma Flows" box
        sits in AR_MAGMA_FLOWS - so it inherits that region's entrance chain instead of hand-copying it
        as Has(...) rules that drift. That only works if the tree exists, which is what pulls a goal-less
        mode into logic here.

        Reads the *static* REGION_TO_MODE table, never the built regions and never a filtered location
        set: logic_modes is what decides which regions get built, so inspecting them would be circular.

        A mode pulled in this way has a tree but no goal, so it contributes no unlock items, none of its
        categories land in effective_gates, set_rules adds no entrance guard for them and fill_slot_data
        ships its gates as 0. The tree is present, reachable and free - which is exactly what an AP box
        in a City Trial stadium needs, and what the upstream all-regions-reachable test requires.

        The cost to accept: an AP+TR seed still builds the CT and AR trees. They are empty and ungated,
        and cost nothing but region count.
        """
        modes = {
            mode
            for mode, enabled in (
                (GameMode.CITYTRIAL, self.city_trial_enabled),
                (GameMode.AIRRIDE, self.air_ride_enabled),
                (GameMode.TOPRIDE, self.top_ride_enabled),
                (GameMode.ARCHIPELAGO, self.archipelago_enabled),
            )
            if enabled
        }
        if self.archipelago_enabled:
            modes |= {REGION_TO_MODE[data.region] for data in AP_CHECKLIST_LOCATION_TABLE.values()}
        return modes

    def _category_holds_keys(self, cat: GatingCategory) -> bool:
        """
        Whether a gating category actually holds unlock items in this seed: its gate is on AND some mode
        that gives its items meaning has a goal.

        An empty required_modes means mode-agnostic (colors) - always keyed, never mode-excluded. The
        mode test must read `not cat.required_modes or any(...)`: an intersection against the enabled
        modes would treat "no required modes" as "no match" and silently drop colors from every seed.

        The mode test uses the *_enabled flags (modes with a goal), not logic_modes - a goal-less mode
        contributes no unlock items, which is what makes it a free side mode.
        """
        if not getattr(self.options, cat.option):
            return False
        return not cat.required_modes or any(getattr(self, mode) for mode in cat.required_modes)

    def _compute_effective_gates(self) -> set[str]:
        """
        The gating categories that really hold keys this seed, by option name.

        A gate is only meaningful when the seed contains its unlock items. The YAML toggle alone does not
        establish that: a category whose modes all lack a goal has its unlocks dropped from the pool, so
        shipping its toggle to the mod would lock that content behind keys that were never minted. This
        set is the single answer three consumers share - _build_item_pools (where it is the definition of
        the exclusion), the entrance-rule guards in set_rules, and fill_slot_data.
        """
        return {cat.option for cat in GATING_CATEGORIES if self._category_holds_keys(cat)}

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
            (
                self.archipelago_enabled,
                self.options.archipelago_goal,
                self.options.archipelago_checklist_amount,
                self.options.archipelago_checkbox_fillers,
                "Archipelago",
                AP_CHECKLIST_LOCATION_TABLE,
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

            if (
                goal_option.value == goal_option.option_n_checklist_blocks
                and filler_option.value >= checklist_amount_option.value
            ):
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
            (
                self.archipelago_enabled,
                self.options.archipelago_goal,
                self.options.archipelago_goal_locations,
                "Archipelago",
                AP_CHECKLIST_LOCATION_TABLE,
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

        # The spawn-rate mechanic moves in fixed +10% steps (mod starts at the min, adds 10% per "Spawn
        # Rate Up"). Snap both bounds to a multiple of 10 so they match what the game can reach and
        # collecting every item lands exactly on the max - else a typed 255 acts as 250 and an off-grid
        # min like 67 gives an odd 67/77/87 progression. The min (10-100) and max (100-300) ranges meet
        # at vanilla, so max >= min always holds.
        self.options.spawn_rate_min.value = ((self.options.spawn_rate_min.value + 5) // 10) * 10
        self.options.spawn_rate_max.value = ((self.options.spawn_rate_max.value + 5) // 10) * 10

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
                case KARItemName.CHECKBOX_FILLER_ARCHIPELAGO:
                    return self.options.archipelago_checkbox_fillers.value
            return 1

        if item_data.type == KARItemType.PATCH_CAP_INCREASE:
            # The mod starts the per-stat cap at the patch-cap min and adds one per Patch Cap Increase
            # received, so pool size = max - min reaches the ceiling. min == max yields 0 (flat cap).
            return max(0, self.options.city_trial_patch_cap_max.value - self.options.city_trial_patch_cap_min.value)

        if item_name == KARItemName.SPAWN_RATE_UP:
            # Each item grants +10%. Pool size = floor((max - min) / 10) so collecting all reaches max.
            return max(0, (self.options.spawn_rate_max.value - self.options.spawn_rate_min.value) // 10)

        return 1

    def _build_item_pools(self) -> None:
        """
        Determine which items are excluded based on player options, then sort the remaining items into pools
        (progression, useful, filler, trap) for placement during create_items().
        """

        # Gating categories (GATING_CATEGORIES, the single source of truth): a category not in
        # effective_gates has its gate OFF or no relevant mode enabled, so its unlock items are excluded.
        # This is the definition of effective_gates, not a separate reading of it. Overlapping checklist
        # rewards are always excluded too - the UNLOCK items deliver that content when gated ON, and the
        # mod pre-unlocks the whole category at connect when OFF, so the reward gates nothing either way.
        excluded: set[str] = set()
        for cat in GATING_CATEGORIES:
            if cat.option not in self.effective_gates:
                excluded |= items_by_type[cat.item_type]
            if cat.overlapping_rewards:
                excluded |= set(cat.overlapping_rewards)

        # Mode-specific checklist rewards - excluded when their mode is disabled, since the box that
        # would award the reward doesn't exist as a location.
        if not self.air_ride_enabled:
            excluded |= items_by_type[KARItemType.AR_CHECKLIST_REWARD]
        if not self.top_ride_enabled:
            excluded |= items_by_type[KARItemType.TR_CHECKLIST_REWARD]
        if not self.city_trial_enabled:
            excluded |= items_by_type[KARItemType.CT_CHECKLIST_REWARD]

        # Non-progression checklist rewards: removed from the pool when checklist_rewards_gated is off.
        # The mod unlocks them all at connect, so their boxes carry ordinary items instead. The 6
        # Dragoon/Hydra part markers are progression (they gate the legendary machines) and stay.
        if not self.options.checklist_rewards_gated:
            for name, data in ITEM_TABLE.items():
                if data.type in CHECKLIST_REWARD_TYPES and not (data.classification & ItemClassification.progression):
                    excluded.add(name)

        # Allowed item categories: a category absent from `allowed_items` removes all of that category's
        # optional NON-TRAP items. (Trap items stay governed solely by `traps`, so
        # ALLOWED_ITEM_CATEGORY_ITEMS omits them.) The source-modes backstop still applies on top, so
        # e.g. Permanent Patches (all _CT) are also dropped when City Trial is off, no separate guard.
        allowed = self.options.allowed_items.value
        for category, names in ALLOWED_ITEM_CATEGORY_ITEMS.items():
            if category not in allowed:
                excluded |= names

        # Patch cap increase: excluded unless CT enabled AND the cap can grow (max > min).
        cap_can_grow = self.options.city_trial_patch_cap_max.value > self.options.city_trial_patch_cap_min.value
        if not self.city_trial_enabled or not cap_can_grow:
            excluded.add(KARItemName.PATCH_CAP_INCREASE)

        # Spawn Rate Up: excluded when the ceiling is at or below the min (no room to grow).
        if self.options.spawn_rate_max.value <= self.options.spawn_rate_min.value:
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
        if not self.archipelago_enabled or self.options.archipelago_checkbox_fillers.value == 0:
            excluded.add(KARItemName.CHECKBOX_FILLER_ARCHIPELAGO)

        # Backstop: any item whose source_modes is non-empty but doesn't intersect with the
        # enabled modes has no in-game effect in the modes that ARE enabled. Drop it from the pool.
        enabled_modes: set[GameMode] = set()
        if self.city_trial_enabled:
            enabled_modes.add(GameMode.CITYTRIAL)
        if self.air_ride_enabled:
            enabled_modes.add(GameMode.AIRRIDE)
        if self.top_ride_enabled:
            enabled_modes.add(GameMode.TOPRIDE)
        if self.archipelago_enabled:
            enabled_modes.add(GameMode.ARCHIPELAGO)
        for name, data in ITEM_TABLE.items():
            if data.source_modes and not (data.source_modes & enabled_modes):
                excluded.add(name)

        # One-time items the player preset in start_inventory: drop the pool copy. Plain start_inventory
        # only precollects an item; AP does NOT remove it from the pool, so without this a second
        # findable copy gets minted. Every gating-category unlock and checklist reward is placed once,
        # so dedup them all (including the six progression part markers, which are still one-time).
        # Stackable items (patch caps, spawn-rate ups, checkbox fillers) and filler/give-items are left
        # in the pool: extra preset copies are harmless there.
        one_time_items: set[str] = set()
        for cat in GATING_CATEGORIES:
            one_time_items |= items_by_type[cat.item_type]
        for reward_type in CHECKLIST_REWARD_TYPES:
            one_time_items |= items_by_type[reward_type]
        for item_name in self.options.start_inventory:
            if item_name in one_time_items:
                excluded.add(item_name)

        # Precollected random starter picks (one per eligible gated category): exclude each chosen
        # unlock so it isn't also placed in the pool.
        for choice in (
            self.stadium_starter_choice,
            self.machine_starter_choice,
            self.tr_machine_starter_choice,
            self.ar_course_starter_choice,
            self.tr_course_starter_choice,
            self.color_starter_choice,
        ):
            if choice is not None:
                excluded.add(choice)

        # Active trap items: every trap-classified item whose category the player kept in `traps`.
        # Unselected categories contribute nothing, so their traps never reach the pool.
        active_traps = {
            name for category in self.options.traps.value for name in TRAP_CATEGORIES.get(category, frozenset())
        }

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
                # interchangeable filler. Route each into reward_pool once so every in-scope reward is
                # placed. (Progression part-markers go to progression_pool; overlapping and
                # mode-disabled rewards are already excluded.)
                self.reward_pool.append(item_name)
            elif classification & ItemClassification.useful:
                self.useful_pool.add(item_name)
            elif classification & ItemClassification.trap:
                if item_name in active_traps:
                    self.trap_pool.add(item_name)
            else:
                self.filler_pool.add(item_name)

        # Pools are now authoritative. _random_filler keys off this to avoid resurrecting items the
        # player disabled via allowed_items (an empty filler_pool after a real build is intentional,
        # not a "pools never built" ItemLink bypass).
        self.item_pools_built = True

    def generate_early(self) -> None:
        """
        Run before any general steps of the MultiWorld other than options.
        """
        self.city_trial_enabled = self.options.city_trial_goal.value != CityTrialGoal.option_none
        self.air_ride_enabled = self.options.air_ride_goal.value != AirRideGoal.option_none
        self.top_ride_enabled = self.options.top_ride_goal.value != TopRideGoal.option_none
        self.archipelago_enabled = self.options.archipelago_goal.value != ArchipelagoGoal.option_none

        if not any((self.city_trial_enabled, self.air_ride_enabled, self.top_ride_enabled, self.archipelago_enabled)):
            raise OptionError("No modes enabled. You need to have at least one goal in a mode!")

        # Both depend only on the *_enabled flags above. effective_gates must precede _build_item_pools
        # (which it defines) and set_rules (whose entrance guards read it); logic_modes must precede
        # create_regions, which it drives.
        self.effective_gates = self._compute_effective_gates()
        self.logic_modes = self._compute_logic_modes()

        self._determine_goal_locations_to_exclude()
        self._determine_locations_progress_type()
        self._validate_options()

        self._determine_starter_items()
        for choice in (
            self.stadium_starter_choice,
            self.machine_starter_choice,
            self.tr_machine_starter_choice,
            self.ar_course_starter_choice,
            self.tr_course_starter_choice,
            self.color_starter_choice,
        ):
            if choice is not None:
                self.push_precollected(self.create_item(choice))

        self._build_item_pools()
        self._capacity_model = self._compute_capacity()
        self._validate_allowed_items_filler()
        self._validate_pool_fits_locations()

    @property
    def _capacity(self) -> _CapacityModel:
        """The shared capacity model built in generate_early."""
        assert self._capacity_model is not None, "capacity model accessed before generate_early built it"
        return self._capacity_model

    def _compute_capacity(self) -> _CapacityModel:
        """
        Build the location capacity/demand model shared by the capacity validators and the reward-pin
        budgeter. Computed once from the location name-sets and built item pools, so it stays valid from
        the end of generate_early through create_items' pin step. Items float across all enabled modes,
        so only global totals are tracked.
        """
        total_default = 0
        total_excluded = 0
        for enabled, default_locs, excluded_locs in [
            (self.city_trial_enabled, self.city_trial_default_locations, self.city_trial_excluded_locations),
            (self.air_ride_enabled, self.air_ride_default_locations, self.air_ride_excluded_locations),
            (self.top_ride_enabled, self.top_ride_default_locations, self.top_ride_excluded_locations),
            (self.archipelago_enabled, self.archipelago_default_locations, self.archipelago_excluded_locations),
        ]:
            if not enabled:
                continue
            mode_default = sum(
                1
                for loc in default_locs
                if loc not in self.goal_locations_to_exclude and loc not in self.options.exclude_locations
            )
            # Total placeable: every real non-goal location of the mode. User-excluded locations still
            # exist (they receive filler) so they count toward the excluded budget, not the default one.
            mode_total = sum(1 for loc in (default_locs | excluded_locs) if loc not in self.goal_locations_to_exclude)
            total_default += mode_default
            total_excluded += mode_total - mode_default

        # In-pool checklist rewards split by classification. Progression part-markers live in
        # progression_pool, not reward_pool, so reward_pool is purely useful/filler.
        useful_rewards = sum(
            1 for name in self.reward_pool if ITEM_TABLE[name].classification & ItemClassification.useful
        )
        filler_rewards = len(self.reward_pool) - useful_rewards

        return _CapacityModel(
            total_default=total_default,
            total_excluded=total_excluded,
            useful_rewards=useful_rewards,
            filler_rewards=filler_rewards,
        )

    def _validate_allowed_items_filler(self) -> None:
        """Defensive backstop: generic filler is always available, so allowed_items can no longer
        starve the pool.

        The cosmetic all-mode filler (Big Kirby / Small Kirby, KARItemType.FILLER) is immune to
        allowed_items and carries _ALL_MODES, so it always lands in filler_pool while any mode is
        enabled, covering every excluded box and leftover slot. This fires only if a future change
        breaks that invariant, turning a would-be downstream FillError into a clean generate_early error.
        """
        if not self.filler_pool:
            raise OptionError(
                "Internal invariant violated: filler_pool is empty after pool building. The cosmetic "
                "all-mode filler items (Big Kirby / Small Kirby) are expected to keep it non-empty "
                "regardless of allowed_items; this indicates a regression in item classification or "
                "pool construction, not a user configuration error."
            )

    def _validate_pool_fits_locations(self) -> None:
        """
        Verify the guaranteed item pool fits the available locations. Two budgets are checked:
          - "needs-default": progression + counted-useful + useful-classified rewards can only sit on
            default (non-excluded) locations.
          - "total": every guaranteed item (the needs-default items plus filler-classified rewards,
            which may sit on excluded boxes) must fit the total placeable location count.
        Rewards are unique one-time unlocks, so each counts once. Raises OptionError with a hint about
        the likely culprit options.
        """
        cap = self._capacity
        default_count = cap.total_default
        total_count = default_count + cap.total_excluded
        reward_useful = cap.useful_rewards
        base_guaranteed = len(self.progression_pool) + len(self.counted_useful_pool)
        needs_default = base_guaranteed + reward_useful
        total_guaranteed = base_guaranteed + len(self.reward_pool)

        if needs_default <= default_count and total_guaranteed <= total_count:
            return

        hints: list[str] = []
        cap_count = max(0, self.options.city_trial_patch_cap_max.value - self.options.city_trial_patch_cap_min.value)
        if cap_count > 0:
            hints.append(
                f"patch cap range ({self.options.city_trial_patch_cap_min.value}-"
                f"{self.options.city_trial_patch_cap_max.value}) adds {cap_count} Patch Cap Increase items"
            )
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

    def create_regions(self) -> None:
        create_regions(self)

    def set_rules(self) -> None:
        set_rules(self)
        self._set_goal_location_item_rules()

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
            (self.archipelago_enabled, self.options.archipelago_goal, self.options.archipelago_goal_locations),
        ]:
            if not enabled or goal_option.value != goal_option.option_checklist_list:
                continue
            for location_name in goal_locations_option.value:
                location = self.get_location(location_name)
                add_item_rule(location, lambda item, player=self.player: item.player == player)

    def create_item(self, name: str) -> KARItem:
        """
        Create a KARItem from the given item_name.
        """
        if name in self.item_names or name in ITEM_TABLE:
            data = ITEM_TABLE[name]
            return KARItem.from_data(str(name), self.player, data)
        raise KeyError(f"Invalid item name: {name}")

    def _reward_pin_filler_headroom(self) -> int:
        """
        Headroom for pinning *filler* checklist rewards onto default boxes without starving progression
        of the default locations it needs: (all default boxes) - (all needs-default items: progression +
        counted-useful + useful rewards). Guaranteed >= 0 by _validate_pool_fits_locations.
        """
        cap = self._capacity
        needs_default = len(self.progression_pool) + len(self.counted_useful_pool) + cap.useful_rewards
        return cap.total_default - needs_default

    def _pin_native_rewards(self, excluded_locations: set[str]) -> None:
        """
        When shuffle_checklist_rewards is off, pin each in-pool checklist reward back onto its vanilla box
        (place_locked_item) and drop it from its pool so create_items mints no duplicate. In scope: the
        non-progression rewards in reward_pool plus the six progression Dragoon/Hydra part markers. Runs
        before create_items counts locations, so the locked boxes self-balance the mint.

        No-op when checklist_rewards_gated is off: the cosmetic rewards have already left the pool (the mod
        grants them at connect), so reward_pool is empty and the only remaining in-scope items would be the
        part markers. Those are left to float like any other progression item rather than pinned, so that
        shuffle_checklist_rewards has no effect at all when rewards are gated off.

        Default boxes are the only home for progression / counted-useful / useful rewards, so default-box
        pins are rationed:
          - Always pin (capacity-neutral): a part marker on a default box (already in progression demand;
            parts gate the Hydra/Dragoon cells, not their own boxes, so this never self-locks), or a filler
            reward on an excluded box (its proper home).
          - Budgeted: a useful reward pins onto its native default box (it needs a default box regardless,
            so this is capacity-neutral), and a filler reward pins onto its native default box only while
            global filler headroom remains. Non-fitting filler rewards float back into the pool.
        """
        if self.options.shuffle_checklist_rewards:
            return

        # Rewards gated off: nothing findable to pin (reward_pool is empty) and the part markers are left
        # to float, so shuffle_checklist_rewards is inert here - same outcome as the shuffle-on early-out.
        if not self.options.checklist_rewards_gated:
            return

        in_scope = list(self.reward_pool) + [
            name for name in self.progression_pool if ITEM_TABLE[name].type in CHECKLIST_REWARD_TYPES
        ]
        # Resolve each in-scope reward to a pinnable native box and bucket it. always_pin: capacity-
        # neutral (part on default box, filler on excluded box). budgeted: default-box pins competing for
        # capacity (useful rewards + filler-on-default), useful first so it wins the scarce slots.
        always_pin: list[tuple[str, Location]] = []
        budgeted: list[tuple[str, Location, bool]] = []
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
            else:
                budgeted.append((reward, location, is_filler))

        pinned: list[tuple[str, Location]] = list(always_pin)
        global_spare = self._reward_pin_filler_headroom()
        # Useful rewards before filler so they claim scarce default slots first.
        for reward, location, is_filler in sorted(budgeted, key=lambda b: (b[2], b[0])):
            if is_filler and global_spare <= 0:
                continue
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

    def create_items(self) -> None:
        # Progression, checklist rewards, and filler all float freely across the player's enabled modes,
        # so create_items mints everything with no mode awareness. (source_modes only governs which items
        # exist in the pool at all, via the disabled-mode pool backstop.)
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
        if self.archipelago_enabled:
            excluded_locations |= self.archipelago_excluded_locations

        # Remove goal locations from excluded_locations since they don't actually exist as real locations
        excluded_locations -= self.goal_locations_to_exclude

        # Shuffle off: pin native rewards onto their vanilla boxes before counting, so the locked boxes
        # drop out of the tallies that follow and the minted-item count self-balances against them.
        self._pin_native_rewards(excluded_locations)

        nonexcluded_locations = [
            location
            for location in self.get_locations()
            if location.name not in excluded_locations and not location.locked
        ]
        num_excluded = sum(
            1 for location in self.get_locations() if location.name in excluded_locations and not location.locked
        )

        # Checklist rewards are unique one-time unlocks, each minted once. Filler-classified rewards are
        # eligible for excluded boxes, so they offset the generic filler minted there; useful-classified
        # rewards need default locations like progression. _validate_pool_fits_locations guarantees fit.
        num_reward_filler = sum(
            1 for name in self.reward_pool if not (ITEM_TABLE[name].classification & ItemClassification.useful)
        )

        # One filler per excluded location (get_filler_item_name may roll a trap), minus the filler
        # rewards already destined for those boxes.
        generic_filler = max(0, num_excluded - num_reward_filler)
        pool.extend(self.get_filler_item_name() for _ in range(generic_filler))

        # Progression items. These float freely across the player's enabled modes;
        # _validate_pool_fits_locations guarantees they fit the available default locations.
        pool.extend(self.progression_pool)

        # Counted-useful items (checkbox fillers, spawn rate up): guaranteed quantities.
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
        has_traps = self.trap_pool and self.options.trap_chance.value > 0
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
        """Pick a random active trap (uniform over the categories the player selected in `traps`),
        or None if no trap categories are active."""
        if not self.trap_pool:
            return None
        return self.random.choice(sorted(self.trap_pool))

    def _random_filler(self) -> str:
        """Pick a random filler item from the built filler_pool. Falls back to the broadest ITEM_TABLE
        filler set ONLY when the pools were never built (e.g. an ItemLink path that bypasses
        _build_item_pools). Once pools are built, an empty filler_pool is authoritative (the player
        disabled every filler category via allowed_items), so we must not resurrect disabled items here;
        _validate_allowed_items_filler guarantees _random_filler is never called in that state."""
        eligible = set(self.filler_pool)
        if not eligible and not self.item_pools_built:
            eligible = {n for n, d in ITEM_TABLE.items() if d.classification == ItemClassification.filler}
        return self.random.choice(sorted(eligible))

    def get_filler_item_name(self) -> str:
        """Called by the AP framework when the item pool needs additional filler. Rolls a trap when
        traps are enabled (by trap_chance), otherwise returns a plain filler item."""
        if (
            self.trap_pool
            and self.options.trap_chance.value > 0
            and self.random.random() * 100 < self.options.trap_chance.value
        ):
            trap = self._random_trap()
            if trap is not None:
                return trap
        return self._random_filler()

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Return the `slot_data` field that will be in the `Connected` network package.

        Only options the client or mod actually consume are shipped: the client uses
        these directly (link toggles, goal logging) or writes them into the mod's
        `APSlotOptions` struct via Dolphin. Generation-only options that no downstream
        consumer reads (`trap_chance`, `spawn_rate_max`) are deliberately omitted - they
        only size item pools at generation time. `spawn_rate_min` ships because it is the
        runtime floor the mod reads.

        Every gating category ships its *effective* state rather than the raw YAML toggle; see below.
        """
        slot_data = dict(
            self.options.as_dict(
                "death_link",
                "energy_link",
                "trap_link",
                "reveal_checklists",
                "city_trial_goal",
                "city_trial_checklist_amount",
                "city_trial_goal_locations",
                "air_ride_goal",
                "air_ride_checklist_amount",
                "air_ride_goal_locations",
                "top_ride_goal",
                "top_ride_checklist_amount",
                "top_ride_goal_locations",
                "archipelago_goal",
                "archipelago_checklist_amount",
                "archipelago_goal_locations",
                "city_trial_patch_cap_min",
                "city_trial_patch_cap_max",
                "city_trial_stadiums_gated",
                "spawn_rate_min",
                "city_trial_events_gated",
                "abilities_gated",
                "base_abilities_gated",
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

        # Ship each gating category's effective state, not the player's raw toggle. The mod applies gate
        # flags goal-independently, so a category whose keys never entered the pool (none of its modes
        # has a goal) would otherwise ship locked with nothing able to unlock it - permanently locking
        # that content. An AR-only seed shipped City Trial's events, patches, boxes and stadiums locked
        # with zero keys before this. checklist_rewards_gated is not a gating category and ships raw.
        for cat in GATING_CATEGORIES:
            slot_data[cat.option] = int(cat.option in self.effective_gates)

        return slot_data
