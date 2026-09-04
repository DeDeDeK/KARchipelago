from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, ClassVar, NamedTuple

from BaseClasses import ItemClassification, Tutorial
from Options import Choice, OptionError, PerGameCommonOptions

from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import add_item_rule
from worlds.LauncherComponents import (
    Component,
    Type,
    components,
    icon_paths,
    launch_subprocess,
)

from .KARData import GameMode, ap_patch_group_sizes, checklist_reward_placed_bit
from .KARItems import (
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
    AP_PATCH_LOCATION_TABLE,
    ARCHIPELAGO_GOAL_TO_LOCATION,
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
    APPatchPlacement,
    ArchipelagoGoal,
    CityTrialGoal,
    KAROptions,
    TopRideGoal,
    kar_option_groups,
)
from .KARRegions import AP_PATCH_GROUP_REGIONS, REGION_TO_MODE, create_regions
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


# Universal Tracker regenerates the slot from these instead of the player's local YAML, which may not be
# the one the seed came from.
UT_OPTIONS_KEY = "ut_options"
UT_PASSTHROUGH_OPTIONS: tuple[str, ...] = tuple(
    [name for name in KAROptions.type_hints if name not in PerGameCommonOptions.type_hints] + ["exclude_locations"]
)


class _CapacityModel(NamedTuple):
    """Location budget and reward demand, as the capacity validator sees it. Items float freely across
    the enabled modes, so only global totals matter."""

    # Real, non-goal boxes across all enabled modes: default (non-user-excluded) and excluded (filler-only).
    total_default: int
    total_excluded: int
    # In-pool checklist rewards needing a default box; the filler-classified rest may sit on excluded ones.
    useful_rewards: int


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

    # UT has everything it needs in slot_data, so it skips its launch-time generation and rolls a solo
    # one from the slot data instead. See interpret_slot_data.
    ut_can_gen_without_yaml: ClassVar[bool] = True

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
        # The first ap_patches entries of AP_PATCH_LOCATION_TABLE; the rest are not created.
        self.ap_patch_locations: dict[str, Any] = {}
        self.ap_patch_default_locations: set[str] = set()
        self.ap_patch_excluded_locations: set[str] = set()
        # How many group regions the chain those locations hang off is long.
        self.ap_patch_group_count: int = 0
        # Gating categories (option names) that really hold keys this seed; see _compute_effective_gates.
        self.effective_gates: set[str] = set()
        # Unlocks the pool ships despite their category's gate being off, because the goal is gated on
        # them; see _compute_goal_forced_unlocks.
        self.goal_forced_unlocks: set[str] = set()
        # Modes whose region trees are built; a superset of the modes with a goal.
        self.logic_modes: set[GameMode] = set()
        self.useful_pool: set[str] = set()
        self.filler_pool: set[str] = set()
        self.reward_pool: list[str] = []
        self.trap_pool: set[str] = set()
        self.item_pools_built: bool = False
        self.progression_pool: list[str] = []
        self.counted_useful_pool: list[str] = []
        self.stadium_starter_choice: str | None = None
        self.goal_locations_to_exclude: set[str] = set()
        # Universal Tracker only: victory events whose goal the game reports already achieved. KARClient
        # stamps it before each tracker refresh; None means nothing is reporting, so go mode falls back
        # to "any goal reachable".
        self.ut_goals_completed: set[str] | None = None
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
        """Split a location table into default and excluded sets by option-driven exclusion groups."""
        default_locations: set[str] = set()
        excluded_locations: set[str] = set()
        for location in location_table:
            if any(should_exclude and location in group for should_exclude, group in exclusion_groups):
                excluded_locations.add(location)
            else:
                default_locations.add(location)
        return default_locations, excluded_locations

    def _determine_locations_progress_type(self) -> None:
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
                (not self.options.air_ride_progression_rng, location_name_groups[KARLocationGroup.AR_RNG]),
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

        # One switch over the whole AP Patch category
        self.ap_patch_default_locations, self.ap_patch_excluded_locations = self._categorize_locations(
            self.ap_patch_locations,
            [
                (
                    self.options.ap_patch_placement.value == APPatchPlacement.option_excluded,
                    set(self.ap_patch_locations),
                ),
            ],
        )

    def _determine_goal_locations_to_exclude(self) -> None:
        """Goal locations backed by a specific checklist entry are replaced by event locations, so the
        original must not exist as a real location."""
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

    def _resolve_starter(
        self,
        option: Choice,
        candidates: tuple[KARItemName, ...],
        eligible: set[str],
        barred: Mapping[KARItemName, str] = MappingProxyType({}),
        suppression_set: set[str] | None = None,
    ) -> str | None:
        """The starting unlock for one category: the player's named pick, or a random draw from
        `eligible` when the option is on "randomized". None when there is nothing to hand over.

        Options number their choices as 1-based indices into `candidates`, with 0 for "randomized".
        `barred` maps a member held out of this seed's draw to the reason why; naming one is an error
        rather than a silent downgrade. `suppression_set` is what start_inventory is tested against when
        deciding to skip the draw - the stadium category tests 24 unlocks while drawing from 23.
        """
        if option.value:
            named = candidates[option.value - 1]
            if named in barred:
                # getattr: AP declares display_name on each option class, never on the Option base.
                label = getattr(option, "display_name", type(option).__name__)
                raise OptionError(f"{label} cannot be '{option.current_key}': {barred[named]}.")
            return None if named in self.options.start_inventory else str(named)
        if not eligible:
            return None
        if any(item in self.options.start_inventory for item in (suppression_set if suppression_set else eligible)):
            return None
        return self.random.choice(sorted(eligible))

    def _determine_starter_items(self) -> None:
        """
        One starter per gated category the player should not boot into without; generate_early
        push_precollects each. Deliberately skipped as playable without: events, abilities, boxes,
        CT items, TR items, patch types.
        """
        if self.city_trial_enabled and self.options.city_trial_stadiums_gated:
            # Handing over the goal stadium for free would hand over the goal.
            beat_dedede = self.options.city_trial_goal.value == self.options.city_trial_goal.option_beat_king_dedede
            barred_stadiums = (
                {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE: "it is your City Trial goal"} if beat_dedede else {}
            )
            stadiums = {str(name) for name in STADIUM_UNLOCK_ITEMS}
            self.stadium_starter_choice = self._resolve_starter(
                self.options.starting_stadium,
                STADIUM_UNLOCK_ITEMS,
                stadiums - {str(name) for name in barred_stadiums},
                barred_stadiums,
                suppression_set=stadiums,
            )

        if (self.city_trial_enabled or self.air_ride_enabled) and self.options.machines_gated:
            machines = {str(name) for name in AR_CT_MACHINE_UNLOCK_ITEMS}
            # Slick/Turbo only turn by charge-drifting and Bulk has almost no speed of its own, so
            # any of them as the sole machine with Charge locked strands the player.
            barred_machines = (
                {
                    name: "it needs Machine Charge to move or steer, which Base Abilities Gated locks"
                    for name in CHARGE_DEPENDENT_MACHINES
                    if str(name) in machines
                }
                if self.options.base_abilities_gated
                else {}
            )
            self.machine_starter_choice = self._resolve_starter(
                self.options.starting_machine,
                AR_CT_MACHINE_UNLOCK_ITEMS,
                machines - {str(name) for name in barred_machines},
                barred_machines,
            )

        # The mod hard-gates the Top Ride lobby on Free or Steer, so a machine-gated Top Ride needs one
        # of them up front.
        if self.top_ride_enabled and self.options.machines_gated:
            self.tr_machine_starter_choice = self._resolve_starter(
                self.options.starting_top_ride_machine,
                TR_MACHINE_UNLOCK_ITEMS,
                {str(name) for name in TR_MACHINE_UNLOCK_ITEMS},
            )

        if self.air_ride_enabled and self.options.air_ride_courses_gated:
            self.ar_course_starter_choice = self._resolve_starter(
                self.options.starting_air_ride_course,
                AR_COURSE_UNLOCK_ITEMS,
                items_by_type[KARItemType.AR_COURSE_UNLOCK],
            )

        if self.top_ride_enabled and self.options.top_ride_courses_gated:
            self.tr_course_starter_choice = self._resolve_starter(
                self.options.starting_top_ride_course,
                TR_COURSE_UNLOCK_ITEMS,
                items_by_type[KARItemType.TR_COURSE_UNLOCK],
            )

        # A cosmetic exception, but the mod falls back to Pink only while no color is unlocked. Colors
        # have no required_modes, so the gate alone decides.
        if self.options.colors_gated:
            self.color_starter_choice = self._resolve_starter(
                self.options.starting_kirby_color,
                COLOR_UNLOCK_ITEMS,
                items_by_type[KARItemType.COLOR_UNLOCK],
            )

    def _compute_logic_modes(self) -> set[GameMode]:
        """
        The modes whose region trees get built: every mode with a goal, plus every mode an Archipelago
        checklist box names when the AP checklist is on - an AP box inherits the entrance chain of the
        region its activity happens in, which needs that tree to exist. A mode pulled in this way has no
        goal, so it mints no unlocks, lands in no effective_gates and ships its gates as 0: free. Reads
        the static REGION_TO_MODE table; inspecting the built regions would be circular.
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
        # AP Patches sit in the City Trial region, so they need its tree even with no City Trial goal.
        if self.options.ap_patches.value:
            modes.add(GameMode.CITYTRIAL)
        return modes

    def _category_holds_keys(self, cat: GatingCategory) -> bool:
        """
        Whether a category holds unlock items this seed: gate on AND some mode giving its items meaning
        has a goal. Tests the *_enabled flags, not logic_modes - a goal-less mode mints no unlocks.
        Empty required_modes means mode-agnostic (colors), always keyed - never an intersection test.
        """
        if not getattr(self.options, cat.option):
            return False
        return not cat.required_modes or any(getattr(self, mode) for mode in cat.required_modes)

    def _compute_effective_gates(self) -> set[str]:
        """
        The gating categories that really hold keys this seed, by option name. The YAML toggle alone does
        not establish that: a category whose modes all lack a goal has its unlocks dropped from the pool,
        so shipping its toggle would lock content behind keys that were never minted.
        """
        return {cat.option for cat in GATING_CATEGORIES if self._category_holds_keys(cat)}

    def _goal_required_unlocks(self) -> set[str]:
        """
        The unlocks this seed's goal is gated on, whatever their category's gate says. Only the goals
        that are one in-game feat qualify: legendary pieces have to spawn to be assembled and the Vs.
        King Dedede stadium has to come up in the rotation. A checklist count needs no single unlock.
        """
        required: set[str] = set()

        if self.city_trial_enabled:
            goal = self.options.city_trial_goal.value
            if goal == CityTrialGoal.option_hydra_and_dragoon:
                required |= set(LEGENDARY_PIECE_UNLOCK_ITEMS)
            elif goal == CityTrialGoal.option_beat_king_dedede:
                required.add(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)

        if self.archipelago_enabled:
            goal = self.options.archipelago_goal.value
            if goal == ArchipelagoGoal.option_assemble_archipelago_star:
                required |= set(AP_STAR_PIECE_UNLOCK_ITEMS)
            elif goal == ArchipelagoGoal.option_all_three_legendaries_in_one_run:
                required |= set(AP_STAR_PIECE_UNLOCK_ITEMS) | set(LEGENDARY_PIECE_UNLOCK_ITEMS)

        return required

    def _compute_goal_forced_unlocks(self) -> set[str]:
        """
        The goal's keys the pool must ship even though their category's gate is off. Ungated, the mod
        hands the whole unlock mask over at connect, making a one-feat goal winnable before any item
        arrives; it withholds exactly these bits instead. Empty when the category is already gated.
        """
        required = self._goal_required_unlocks()
        forced: set[str] = set()
        if "city_trial_items_gated" not in self.effective_gates:
            forced |= required & (set(LEGENDARY_PIECE_UNLOCK_ITEMS) | set(AP_STAR_PIECE_UNLOCK_ITEMS))
        if "city_trial_stadiums_gated" not in self.effective_gates:
            forced |= required & {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE}
        return forced

    def _validate_options(self) -> None:
        """Validate that option combinations are coherent: checklist goals achievable, filler amounts sane."""
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
            # getattr, not attribute access: ArchipelagoGoal has no 100_checklist_blocks (its checklist is
            # under 100 boxes). Goal values are ints, so the None default can never compare equal.
            elif goal_option.value == getattr(goal_option, "option_100_checklist_blocks", None):
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

        # "Spawn Rate Up" adds a fixed 10% over the min, so snap both bounds to a multiple of 10 for
        # collecting every copy to land exactly on the max. The ranges meet at vanilla, so max >= min holds.
        self.options.spawn_rate_min.value = ((self.options.spawn_rate_min.value + 5) // 10) * 10
        self.options.spawn_rate_max.value = ((self.options.spawn_rate_max.value + 5) // 10) * 10

        # Starting with a goal's own key wins the seed on the spot.
        for goal_key in sorted(self._goal_required_unlocks()):
            if goal_key in self.options.start_inventory:
                raise OptionError(f"Cannot have {goal_key} in starting inventory - this seed's goal is gated on it")

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
        """Determine which items the player's options exclude, then sort the rest into pools (progression,
        useful, filler, trap) for create_items() to place."""

        # A category outside effective_gates has its gate off or no relevant mode enabled, so its
        # unlocks are excluded. Overlapping checklist rewards go too, gate on or off.
        excluded: set[str] = set()
        for cat in GATING_CATEGORIES:
            if cat.option not in self.effective_gates:
                excluded |= items_by_type[cat.item_type]
            if cat.overlapping_rewards:
                excluded |= set(cat.overlapping_rewards)

        # A disabled mode's checklist rewards: the box that would award them isn't a location.
        if not self.air_ride_enabled:
            excluded |= items_by_type[KARItemType.AR_CHECKLIST_REWARD]
        if not self.top_ride_enabled:
            excluded |= items_by_type[KARItemType.TR_CHECKLIST_REWARD]
        if not self.city_trial_enabled:
            excluded |= items_by_type[KARItemType.CT_CHECKLIST_REWARD]

        # A checklist reward category left out of `checklist_rewards` drops its rewards: the mod unlocks
        # them at connect. Rewards belonging to no category - the 6 progression Dragoon/Hydra part markers,
        # and the overlapping rewards already dropped above - are unaffected.
        for category, names in CHECKLIST_REWARD_CATEGORIES.items():
            if category not in self.options.checklist_rewards.value:
                excluded |= names

        # A category absent from `allowed_items` drops its optional non-trap items (traps are governed
        # solely by `traps`). The source-modes backstop below covers mode-disabled ones on top.
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

        # Drop Patches Trap: the mod's handler guards on Gm_IsInCity, so City Trial only.
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

        # Backstop: a non-empty source_modes that misses every enabled mode means the item has no
        # in-game effect here.
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

        # A goal's own keys survive their category's gate being off. Must sit after the source-modes
        # backstop: an AP-checklist goal can be keyed on another mode's items (the star's six spheres
        # are City Trial items), which a goal-less City Trial would otherwise drop straight back out.
        excluded -= self.goal_forced_unlocks

        # start_inventory precollects without removing from the pool, so drop the pool copy of any
        # one-time item (unlocks, checklist rewards) preset there. Stackables keep their extra copies.
        one_time_items: set[str] = set()
        for cat in GATING_CATEGORIES:
            one_time_items |= items_by_type[cat.item_type]
        for reward_type in CHECKLIST_REWARD_TYPES:
            one_time_items |= items_by_type[reward_type]
        for item_name in self.options.start_inventory:
            if item_name in one_time_items:
                excluded.add(item_name)

        # Precollected starter picks: exclude each so it isn't also placed in the pool.
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

        # Trap-classified items whose category the player kept in `traps`; the rest never reach the pool.
        active_traps = {
            name for category in self.options.traps.value for name in TRAP_CATEGORIES.get(category, frozenset())
        }

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
                # Unique one-time unlocks tied to a specific box, so exactly one copy each.
                self.reward_pool.append(item_name)
            elif classification & ItemClassification.useful:
                self.useful_pool.add(item_name)
            elif classification & ItemClassification.trap:
                if item_name in active_traps:
                    self.trap_pool.add(item_name)
            else:
                self.filler_pool.add(item_name)

        self.item_pools_built = True

    def _apply_ut_passthrough(self) -> None:
        """Restore this slot's recorded option values when Universal Tracker is re-generating. A no-op
        during a real generation: `re_gen_passthrough` only exists on UT's MultiWorld. UT regenerates
        from an empty YAML, so every option arrives at its default and must be put back here before
        generate_early reads the first one.
        """
        passthrough = getattr(self.multiworld, "re_gen_passthrough", None)
        if not passthrough or self.game not in passthrough:
            return
        recorded = passthrough[self.game].get(UT_OPTIONS_KEY)
        if not recorded:
            # Too old to record its options; tracking it would silently report default-option logic.
            raise OptionError(
                "This seed's slot data carries no Kirby Air Ride option record, so Universal Tracker "
                "cannot rebuild its logic. The seed was generated by an older version of the apworld."
            )
        for name, value in recorded.items():
            option = getattr(self.options, name, None)
            if option is not None:
                # from_any, not .value: OptionSets and Choices need their own parsing.
                setattr(self.options, name, type(option).from_any(value))

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        """Universal Tracker hook. Returning the slot data tells UT to regenerate this slot from it
        rather than the player's local YAML; _apply_ut_passthrough picks it back up in generate_early."""
        return slot_data

    def generate_early(self) -> None:
        self._apply_ut_passthrough()

        self.city_trial_enabled = self.options.city_trial_goal.value != CityTrialGoal.option_none
        self.air_ride_enabled = self.options.air_ride_goal.value != AirRideGoal.option_none
        self.top_ride_enabled = self.options.top_ride_goal.value != TopRideGoal.option_none
        self.archipelago_enabled = self.options.archipelago_goal.value != ArchipelagoGoal.option_none

        if not any((self.city_trial_enabled, self.air_ride_enabled, self.top_ride_enabled, self.archipelago_enabled)):
            raise OptionError("No modes enabled. You need to have at least one goal in a mode!")

        # Only the first ap_patches table entries become locations; the table is full width so
        # location_name_to_id covers every seed's names. Each is restamped into its group's region: the
        # static table names City Trial, which is the chain's root rather than where a patch ends up.
        group_sizes = ap_patch_group_sizes(self.options.ap_patches.value)
        self.ap_patch_group_count = len(group_sizes)
        self.ap_patch_locations = {}
        entries = list(AP_PATCH_LOCATION_TABLE.items())[: self.options.ap_patches.value]
        offset = 0
        for group_index, size in enumerate(group_sizes):
            region = AP_PATCH_GROUP_REGIONS[group_index]
            for name, data in entries[offset : offset + size]:
                self.ap_patch_locations[name] = data._replace(region=region)
            offset += size

        # Order matters: both read the *_enabled flags above, goal_forced_unlocks reads effective_gates,
        # and the pool build, create_regions and set_rules read all three.
        self.effective_gates = self._compute_effective_gates()
        self.logic_modes = self._compute_logic_modes()
        self.goal_forced_unlocks = self._compute_goal_forced_unlocks()

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
        self._validate_allowed_items_filler()
        self._validate_pool_fits_locations(self._compute_capacity())

    def _compute_capacity(self) -> _CapacityModel:
        """Build the capacity model. Only valid once the pools are built."""
        total_default = 0
        total_excluded = 0
        for enabled, default_locs, excluded_locs in [
            (self.city_trial_enabled, self.city_trial_default_locations, self.city_trial_excluded_locations),
            (self.air_ride_enabled, self.air_ride_default_locations, self.air_ride_excluded_locations),
            (self.top_ride_enabled, self.top_ride_default_locations, self.top_ride_excluded_locations),
            (self.archipelago_enabled, self.archipelago_default_locations, self.archipelago_excluded_locations),
            (bool(self.ap_patch_locations), self.ap_patch_default_locations, self.ap_patch_excluded_locations),
        ]:
            if not enabled:
                continue
            mode_default = sum(
                1
                for loc in default_locs
                if loc not in self.goal_locations_to_exclude and loc not in self.options.exclude_locations
            )
            # User-excluded locations still exist and receive filler, so they count toward the excluded
            # budget, not the default one.
            mode_total = sum(1 for loc in (default_locs | excluded_locs) if loc not in self.goal_locations_to_exclude)
            total_default += mode_default
            total_excluded += mode_total - mode_default

        # Progression part-markers live in progression_pool, so reward_pool is purely useful/filler.
        useful_rewards = sum(
            1 for name in self.reward_pool if ITEM_TABLE[name].classification & ItemClassification.useful
        )
        return _CapacityModel(
            total_default=total_default,
            total_excluded=total_excluded,
            useful_rewards=useful_rewards,
        )

    def _validate_allowed_items_filler(self) -> None:
        """Defensive backstop: Big Kirby / Small Kirby are immune to allowed_items and carry _ALL_MODES,
        so filler_pool is never empty. Fires only on a regression, turning a downstream FillError into a
        clean generate_early one."""
        if not self.filler_pool:
            raise OptionError(
                "Internal invariant violated: filler_pool is empty after pool building. The cosmetic "
                "all-mode filler items (Big Kirby / Small Kirby) are expected to keep it non-empty "
                "regardless of allowed_items; this indicates a regression in item classification or "
                "pool construction, not a user configuration error."
            )

    def _validate_pool_fits_locations(self, cap: _CapacityModel) -> None:
        """
        Verify the guaranteed item pool fits the available locations, on two budgets:
          - needs-default: progression + counted-useful + useful rewards, which need non-excluded boxes.
          - total: those plus filler-classified rewards, which may sit on excluded boxes.
        """
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
        """Restrict checklist_list goal locations to local items, so another player's /collect cannot check
        them, auto-complete the checklist entries and prematurely satisfy the goal."""
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
        if name in self.item_names or name in ITEM_TABLE:
            data = ITEM_TABLE[name]
            return KARItem.from_data(str(name), self.player, data)
        raise KeyError(f"Invalid item name: {name}")

    def create_items(self) -> None:
        # Everything floats freely across the enabled modes, so this mints with no mode awareness.
        pool: list[str] = []

        # A disabled mode's locations don't exist in the multiworld, so only fold in enabled ones.
        excluded_locations = set(self.options.exclude_locations)
        if self.city_trial_enabled:
            excluded_locations |= self.city_trial_excluded_locations
        if self.air_ride_enabled:
            excluded_locations |= self.air_ride_excluded_locations
        if self.top_ride_enabled:
            excluded_locations |= self.top_ride_excluded_locations
        if self.archipelago_enabled:
            excluded_locations |= self.archipelago_excluded_locations
        excluded_locations |= self.ap_patch_excluded_locations

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

        # Checklist rewards are minted once each. Filler-classified ones may sit on excluded boxes, so
        # they offset the generic filler minted there; useful ones need default boxes like progression.
        num_reward_filler = sum(
            1 for name in self.reward_pool if not (ITEM_TABLE[name].classification & ItemClassification.useful)
        )

        # One filler per excluded location (get_filler_item_name may roll a trap), minus the filler
        # rewards already destined for those boxes.
        generic_filler = max(0, num_excluded - num_reward_filler)
        pool.extend(self.get_filler_item_name() for _ in range(generic_filler))

        pool.extend(self.progression_pool)
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
        """Random filler from the built filler_pool. Falls back to the whole ITEM_TABLE filler set only
        when the pools were never built (e.g. an ItemLink path bypassing _build_item_pools)."""
        eligible = set(self.filler_pool)
        if not eligible and not self.item_pools_built:
            eligible = {n for n, d in ITEM_TABLE.items() if d.classification == ItemClassification.filler}
        return self.random.choice(sorted(eligible))

    def get_filler_item_name(self) -> str:
        """AP framework hook for extra filler. Rolls a trap by trap_chance, otherwise plain filler."""
        if (
            self.trap_pool
            and self.options.trap_chance.value > 0
            and self.random.random() * 100 < self.options.trap_chance.value
        ):
            trap = self._random_trap()
            if trap is not None:
                return trap
        return self._random_filler()

    def _checklist_reward_placed_types(self) -> int:
        """Bitmask of the (mode, RewardType) pairs this seed placed as AP items. Read off the built pool
        rather than the option, so every path that drops a reward - an unselected category, a disabled
        mode - leaves its bit clear and the mod unlocks that content at connect."""
        mask = 0
        for name in self.reward_pool:
            mode = CHECKLIST_REWARD_TYPE_MODES[ITEM_TABLE[name].type]
            mask |= 1 << checklist_reward_placed_bit(mode, CHECKLIST_REWARD_ITEM_TYPES[name])
        return mask

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Only options the client or mod actually consume are shipped; generation-only ones (`trap_chance`,
        `spawn_rate_max`) are omitted, while `spawn_rate_min` ships as the mod's runtime floor.
        """
        slot_data = dict(
            self.options.as_dict(
                "death_link",
                "energy_link",
                "trap_link",
                "city_trial_goal",
                "city_trial_checklist_amount",
                "city_trial_goal_locations",
                "city_trial_reveal_checklist",
                "air_ride_goal",
                "air_ride_checklist_amount",
                "air_ride_goal_locations",
                "air_ride_reveal_checklist",
                "top_ride_goal",
                "top_ride_checklist_amount",
                "top_ride_goal_locations",
                "top_ride_reveal_checklist",
                "archipelago_goal",
                "archipelago_checklist_amount",
                "archipelago_goal_locations",
                "archipelago_reveal_checklist",
                "city_trial_patch_cap_min",
                "city_trial_patch_cap_max",
                "city_trial_stadiums_gated",
                "ap_patches",
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
            )
        )

        # The reward types this seed placed, as the mod's RewardType bits; it unlocks every unset type at
        # connect.
        slot_data["checklist_rewards"] = self._checklist_reward_placed_types()

        # Effective state, not the raw toggle: the mod applies gate flags goal-independently, so a
        # category whose keys never entered the pool would ship locked with nothing able to unlock it.
        for cat in GATING_CATEGORIES:
            slot_data[cat.option] = int(cat.option in self.effective_gates)

        # Goal keys held back from an ungated category's pre-fill, so the goal is not free at connect.
        # Both are 0 when the category is gated - its own flag above already keeps the bits locked.
        slot_data["legendary_pieces_goal_gated"] = int(
            bool(self.goal_forced_unlocks & set(LEGENDARY_PIECE_UNLOCK_ITEMS))
        )
        slot_data["vs_king_dedede_goal_gated"] = int(
            KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE in self.goal_forced_unlocks
        )
        slot_data["ap_star_pieces_goal_gated"] = int(bool(self.goal_forced_unlocks & set(AP_STAR_PIECE_UNLOCK_ITEMS)))

        # UT's copy: it regenerates from the raw YAML values and recomputes the effective set itself,
        # so it cannot reuse the effective-state keys above.
        slot_data[UT_OPTIONS_KEY] = self.options.as_dict(*UT_PASSTHROUGH_OPTIONS)

        return slot_data
