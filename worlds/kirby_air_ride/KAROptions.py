from dataclasses import dataclass

from Options import (
    Choice,
    DeathLinkMixin,
    DefaultOnToggle,
    LocationSet,
    NamedRange,
    OptionGroup,
    OptionSet,
    PerGameCommonOptions,
    Range,
    Toggle,
)

from .KARItems import ALLOWED_ITEM_CATEGORIES, TRAP_CATEGORIES


class TrapChance(Range):
    """
    Percentage chance for non-progression item slots to contain traps.
    Set to 0 to disable traps entirely.
    """

    display_name = "Trap Chance"
    default = 0
    range_start = 0
    range_end = 100


class Traps(OptionSet):
    """
    Which categories of trap may appear in your item pool. Has no effect unless "Trap Chance" is above 0.
    """

    display_name = "Trap Types"
    valid_keys = frozenset(TRAP_CATEGORIES)
    default = frozenset(TRAP_CATEGORIES)


class AllowedItems(OptionSet):
    """
    Which categories of optional (non-progression) give items may appear in your item pool. Removing a
    category keeps all of its optional items out of your pool. Trap items are unaffected.
    """

    display_name = "Allowed Item Types"
    valid_keys = frozenset(str(category) for category in ALLOWED_ITEM_CATEGORIES)
    default = frozenset(str(category) for category in ALLOWED_ITEM_CATEGORIES)


class SpawnRateMin(Range):
    """
    Starting item spawn rate percent. The rate climbs from here as "Spawn Rate Up" items are received
    (+10% each); set it equal to "Spawn Rate Max" for a flat rate with no such items.
    """

    display_name = "Spawn Rate Min"
    default = 100
    range_start = 10
    range_end = 100


class SpawnRateMax(Range):
    """
    Item spawn rate ceiling percent, reached after collecting every "Spawn Rate Up" item; the pool
    contains (max - min) / 10 of them. Snapped to the nearest multiple of 10. Applies to City Trial
    and Top Ride; Air Ride has no spawn-rate scaling.
    """

    display_name = "Spawn Rate Max"
    default = 100
    range_start = 100
    range_end = 300


class EnergyLink(Toggle):
    """
    Enables EnergyLink: collecting patches or destroying objects in City Trial sends energy to the
    Multiworld's shared pool, which you can spend on patches or other items.
    """

    default = 0
    display_name = "Energy Link"


class TrapLink(Toggle):
    """
    When on, traps you receive in-game are broadcast to other TrapLink players and you receive theirs.
    Independent of "Trap Chance".
    """

    default = 0
    display_name = "Trap Link"


class RevealChecklists(Toggle):
    """
    If this is enabled, the checklists for each of your enabled game modes will start off as completely revealed.
    """

    default = 0
    display_name = "Reveal Checklists"


class ChecklistRewardsGated(Toggle):
    """
    Controls whether the game's non-progression checklist rewards (music tracks, sound test entries,
    endings, a Top Ride rule, and so on) are gated behind the multiworld.

    When disabled (default), they are left out of the pool: the mod unlocks them all from the start,
    freeing their checklist boxes to hold other items. When enabled, each must be found, and "Shuffle
    Checklist Rewards" decides where it can land.

    The Dragoon and Hydra parts are always in the pool (they are progression).
    """

    display_name = "Checklist Rewards Gated"


class ShuffleChecklistRewards(DefaultOnToggle):
    """
    Controls where the game's native checklist reward items (a machine, a Kirby color, a music track,
    the Dragoon/Hydra parts, and so on) are placed. Governs only those reward items.

    If on (default), each reward is shuffled into the multiworld and can be found anywhere your other
    items can, across any enabled mode. If off, each is placed back on the box that awards it in the
    base game.

    Boxes that award nothing, and content from other unlock items (extra machines, hidden stadiums,
    spare colors), randomize regardless. When off, a reward whose native box is excluded or is needed
    to keep progression placeable is shuffled instead of pinned.
    """

    display_name = "Shuffle Checklist Rewards"


class CityTrialGoal(Choice):
    """
    Sets the goal for City Trial. If you have goals on multiple game modes, all must be achieved to win.
    Select "None" to disable City Trial.
    """

    display_name = "City Trial Goal"
    option_100_checklist_blocks = 0
    option_n_checklist_blocks = 1
    option_hydra_and_dragoon = 2
    option_beat_king_dedede = 3
    option_none = 4
    option_checklist_list = 5
    option_max_stats_in_one_run = 6
    default = 0


class CityTrialChecklistAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for City Trial.
    """

    display_name = "Number of Checklist Boxes for City Trial"
    default = 60
    range_start = 1
    range_end = 120


class CityTrialGoalLocations(LocationSet):
    """
    The specific checklist locations required for the "checklist_list" goal in City Trial.
    Only used when City Trial Goal is set to "checklist_list". Supports location group names.
    """

    display_name = "City Trial Goal Locations"
    verify_location_name = True


class CityTrialProgressionHighEffort(Toggle):
    """
    This controls whether difficult or extremely high effort checkboxes are counted in progression.
    This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial Long/High effort checkboxes are progression"


class CityTrialProgressionMultiplayer(Toggle):
    """
    This controls whether checkboxes that require multiple players are a part of progression.
    This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial Multiplayer checkboxes are progression"


class CityTrialProgressionFreeRun(Toggle):
    """
    This controls whether Free Run checkboxes are a part of progression. This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial Free Run checkboxes are progression"


class CityTrialProgressionRNG(Toggle):
    """
    This controls whether checkboxes that require RNG elements of the game are a part of progression.
    This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial RNG checkboxes are progression"


class CityTrialProgressionBustVehicles(Toggle):
    """
    This controls whether checkboxes that require busting a vehicle on another vehicle are a part of progression.
    This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial bust vehicle checkboxes are progression"


class CityTrialCheckboxFillers(NamedRange):
    """
    Number of "checkbox filler" items added to the City Trial pool.
    These auto-complete checklist blocks when received. Set to 0 to disable.
    """

    display_name = "City Trial Checkbox Fillers"
    default = 5
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class CityTrialPatchCapMin(Range):
    """
    Per-stat patch cap the player starts with (18 = vanilla). The cap climbs from here as "Patch Cap
    Increase" items are received (+1 each); set it equal to "Patch Cap Max" for a flat cap with none.
    """

    default = 18
    range_start = 1
    range_end = 18
    display_name = "Patch Cap Min"


class CityTrialPatchCapMax(Range):
    """
    Per-stat patch cap ceiling (18 = vanilla), reached after collecting every "Patch Cap Increase"
    item; the pool contains (max - min) of them. Also the per-stat threshold for the
    "max_stats_in_one_run" goal.
    """

    default = 18
    range_start = 18
    range_end = 30
    display_name = "Patch Cap Max"


class CityTrialStadiumsGated(DefaultOnToggle):
    """
    When enabled (the default), City Trial stadiums are locked and must be unlocked by finding their
    corresponding Unlock Stadium items. The game starts with one random stadium already unlocked (any of
    the 24, except VS King Dedede when that is the goal).

    When disabled, every stadium is available from the start and no Unlock Stadium items are added to the pool.
    """

    display_name = "City Trial Stadiums Gated"


class AirRideGoal(Choice):
    """
    Sets the goal for Air Ride. If you have goals on multiple game modes, all must be achieved to win.
    Select "None" to disable Air Ride.
    """

    display_name = "Air Ride Goal"
    option_100_checklist_blocks = 0
    option_n_checklist_blocks = 1
    option_none = 4
    option_checklist_list = 5
    default = 4


class AirRideChecklistAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for Air Ride.
    """

    display_name = "Number of Checklist Boxes for Air Ride"
    default = 60
    range_start = 1
    range_end = 120


class AirRideGoalLocations(LocationSet):
    """
    The specific checklist locations required for the "checklist_list" goal in Air Ride.
    Only used when Air Ride Goal is set to "checklist_list". Supports location group names.
    """

    display_name = "Air Ride Goal Locations"
    verify_location_name = True


class AirRideProgressionFreeRun(Toggle):
    """
    This controls whether Free Run checkboxes are a part of progression. This applies to Air Ride only.
    """

    default = 0
    display_name = "Air Ride Free Run checkboxes are progression"


class AirRideProgressionTimeAttack(Toggle):
    """
    This controls whether Time Attack checkboxes are a part of progression. This applies to Air Ride only.
    """

    default = 0
    display_name = "Air Ride Time Attack checkboxes are progression"


class AirRideProgressionHighEffort(Toggle):
    """
    This controls whether difficult or extremely high effort checkboxes are counted in progression.
    This applies to Air Ride only.
    """

    default = 0
    display_name = "Air Ride Long/High effort checkboxes are progression"


class AirRideCheckboxFillers(NamedRange):
    """
    Number of "checkbox filler" items added to the Air Ride pool.
    These auto-complete checklist blocks when received. Set to 0 to disable.
    """

    display_name = "Air Ride Checkbox Fillers"
    default = 5
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class TopRideGoal(Choice):
    """
    Sets the goal for Top Ride. If you have goals on multiple game modes, all must be achieved to win.
    Select "None" to disable Top Ride.
    """

    display_name = "Top Ride Goal"
    option_100_checklist_blocks = 0
    option_n_checklist_blocks = 1
    option_none = 4
    option_checklist_list = 5
    default = 4


class TopRideChecklistAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for Top Ride.
    """

    display_name = "Number of Checklist Boxes for Top Ride"
    default = 60
    range_start = 1
    range_end = 120


class TopRideGoalLocations(LocationSet):
    """
    The specific checklist locations required for the "checklist_list" goal in Top Ride.
    Only used when Top Ride Goal is set to "checklist_list". Supports location group names.
    """

    display_name = "Top Ride Goal Locations"
    verify_location_name = True


class TopRideProgressionFreeRun(Toggle):
    """
    This controls whether Free Run checkboxes are a part of progression. This applies to Top Ride only.
    """

    default = 0
    display_name = "Top Ride Free Run checkboxes are progression"


class TopRideProgressionTimeAttack(Toggle):
    """
    This controls whether Time Attack checkboxes are a part of progression. This applies to Top Ride only.
    """

    default = 0
    display_name = "Top Ride Time Attack checkboxes are progression"


class TopRideProgressionHighEffort(Toggle):
    """
    This controls whether difficult or extremely high effort checkboxes are counted in progression.
    This applies to Top Ride only.
    """

    default = 0
    display_name = "Top Ride Long/High effort checkboxes are progression"


class TopRideProgressionMultiplayer(Toggle):
    """
    This controls whether checkboxes that require multiple players are a part of progression.
    This applies to Top Ride only.
    """

    default = 0
    display_name = "Top Ride Multiplayer checkboxes are progression"


class TopRideCheckboxFillers(NamedRange):
    """
    Number of "checkbox filler" items added to the Top Ride pool.
    These auto-complete checklist blocks when received. Set to 0 to disable.
    """

    display_name = "Top Ride Checkbox Fillers"
    default = 5
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class ArchipelagoGoal(Choice):
    """
    Sets the goal for the Archipelago checklist - the synthetic in-game checklist tab of
    Archipelago-specific objectives. If you have goals on multiple game modes, all must be achieved to
    win. Select "None" to disable the Archipelago checklist: its locations are then left out of the
    multiworld, though the tab still appears in-game.

    EXPERIMENTAL: the Archipelago checklist is incomplete and under active development. It offers far
    fewer objectives than the 120 its options allow, so a large "n_checklist_blocks" target (or the
    "100_checklist_blocks" goal) cannot be satisfied. Objective names and thresholds may still change
    in ways that break existing YAMLs. Enable it only if you want to try it.
    """

    display_name = "Archipelago Checklist Goal"
    option_100_checklist_blocks = 0
    option_n_checklist_blocks = 1
    option_none = 4
    option_checklist_list = 5
    default = 4


class ArchipelagoChecklistAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for the
    Archipelago checklist.

    The Archipelago checklist is still incomplete, so it offers fewer boxes than the other modes and
    this range is correspondingly smaller.
    """

    display_name = "Number of Checklist Boxes for Archipelago"
    # range_end tracks the real size of AP_CHECKLIST_LOCATION_TABLE - unlike City Trial / Air Ride /
    # Top Ride, which each have a full 120 boxes, the Archipelago checklist is still being built out.
    # Offering more than exists would only produce an OptionError at generation. A data-integrity test
    # pins this to the table; raise it as boxes are added. Default is half the table, as elsewhere.
    default = 18
    range_start = 1
    range_end = 36


class ArchipelagoGoalLocations(LocationSet):
    """
    The specific checklist locations required for the "checklist_list" goal on the Archipelago
    checklist. Only used when Archipelago Checklist Goal is set to "checklist_list". Supports location
    group names.
    """

    display_name = "Archipelago Goal Locations"
    verify_location_name = True


class ArchipelagoCheckboxFillers(NamedRange):
    """
    Number of "checkbox filler" items added to the pool for the Archipelago checklist. These
    auto-complete an Archipelago checklist block when received. Set to 0 to disable.

    Defaults to 0: the Archipelago checklist is an early stub with only a few boxes, so most fillers
    would have nothing to fill.
    """

    display_name = "Archipelago Checkbox Fillers"
    default = 0
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class CityTrialEventsGated(DefaultOnToggle):
    """
    When enabled, City Trial events (Dyna Blade, Meteor, Tac, etc.) are locked and must be
    unlocked by finding their corresponding items.

    When disabled, all events are available from the start and no event unlock items are added to
    the pool.
    """

    display_name = "City Trial Events Gated"


class AbilitiesGated(DefaultOnToggle):
    """
    When enabled, copy abilities (Fire, Sword, Bomb, etc.) are locked and must be unlocked
    by finding their corresponding items.

    When disabled, all copy abilities are available from the start and no ability unlock items are
    added to the pool.
    """

    display_name = "Copy Abilities Gated"


class BaseAbilitiesGated(Toggle):
    """
    When enabled, Kirby's base moves - inhale, quick spin, and machine charge - start locked and must
    each be unlocked by finding their item. Until then the human player cannot swallow, quick spin, or
    charge for a boost (CPUs are unaffected); swallow and quick-spin checkboxes gate behind the unlock.

    When disabled, all three moves are available from the start and no base ability unlock items are
    added to the pool.
    """

    display_name = "Base Abilities Gated"


class CityTrialPatchesGated(DefaultOnToggle):
    """
    When enabled, patch stat types (Boost, Top Speed, Offense, etc.) are locked and must be
    unlocked by finding their corresponding items.

    When disabled, all patch stat types are available from the start and no patch type unlock items
    are added to the pool.
    """

    display_name = "City Trial Patch Types Gated"


class CityTrialItemsGated(Toggle):
    """
    When enabled, game items (All Up, Speed Max, Candy, food, legendary parts, etc.)
    are locked and must be unlocked by finding their corresponding items.

    When disabled, all game items are available from the start and no item unlock items are added to
    the pool.
    """

    display_name = "City Trial Items Gated"


class MachinesGated(Toggle):
    """
    When enabled, air ride machines are locked and must be unlocked by finding their
    corresponding items. Applies to both City Trial and Air Ride. The game starts with one random
    machine already unlocked (and, when Top Ride is enabled, one random Top Ride control machine).

    When disabled, all machines are available from the start and no machine unlock items are added
    to the pool.
    """

    display_name = "Machines Gated"


class CityTrialBoxesGated(DefaultOnToggle):
    """
    When enabled, box types (Blue, Green, Red) are locked and must be unlocked by finding
    their corresponding items.

    When disabled, all box types are available from the start and no box unlock items are added to
    the pool.
    """

    display_name = "City Trial Boxes Gated"


class AirRideCoursesGated(DefaultOnToggle):
    """
    When enabled, Air Ride courses are locked and must be unlocked by finding their
    corresponding items. The game starts with one random Air Ride course already unlocked.

    When disabled, all Air Ride courses are available from the start and no course unlock items are
    added to the pool.
    """

    display_name = "Air Ride Courses Gated"


class ColorsGated(DefaultOnToggle):
    """
    When enabled, Kirby colors are locked and must be unlocked by finding their corresponding
    items. The game starts with one random color already unlocked.

    When disabled, all Kirby colors are available from the start and no color unlock items are added
    to the pool.
    """

    display_name = "Kirby Colors Gated"


class TopRideCoursesGated(DefaultOnToggle):
    """
    When enabled, Top Ride courses are locked and must be unlocked by finding their
    corresponding items. The game starts with one random Top Ride course already unlocked.

    When disabled, all Top Ride courses are available from the start and no course unlock items are
    added to the pool.
    """

    display_name = "Top Ride Courses Gated"


class TopRideItemsGated(DefaultOnToggle):
    """
    When enabled, Top Ride items are locked and must be unlocked by finding their
    corresponding items. The four items tied to copy abilities (Freeze Fan, Fire, Bomb, Walky) accept
    either key: their own Top Ride item unlock, or the matching copy ability unlock.

    When disabled, all Top Ride items are available from the start and no item unlock items are added
    to the pool.
    """

    display_name = "Top Ride Items Gated"


@dataclass
class KAROptions(PerGameCommonOptions, DeathLinkMixin):
    """Configuration options for Kirby Air Ride."""

    # General
    trap_chance: TrapChance
    traps: Traps
    allowed_items: AllowedItems
    trap_link: TrapLink
    spawn_rate_min: SpawnRateMin
    spawn_rate_max: SpawnRateMax
    energy_link: EnergyLink
    reveal_checklists: RevealChecklists
    shuffle_checklist_rewards: ShuffleChecklistRewards
    checklist_rewards_gated: ChecklistRewardsGated

    # City Trial
    city_trial_goal: CityTrialGoal
    city_trial_checklist_amount: CityTrialChecklistAmount
    city_trial_goal_locations: CityTrialGoalLocations
    city_trial_progression_high_effort: CityTrialProgressionHighEffort
    city_trial_progression_free_run: CityTrialProgressionFreeRun
    city_trial_progression_multiplayer: CityTrialProgressionMultiplayer
    city_trial_progression_rng: CityTrialProgressionRNG
    city_trial_progression_bust_vehicles: CityTrialProgressionBustVehicles
    city_trial_checkbox_fillers: CityTrialCheckboxFillers
    city_trial_patch_cap_min: CityTrialPatchCapMin
    city_trial_patch_cap_max: CityTrialPatchCapMax
    city_trial_stadiums_gated: CityTrialStadiumsGated

    # Air Ride
    air_ride_goal: AirRideGoal
    air_ride_checklist_amount: AirRideChecklistAmount
    air_ride_goal_locations: AirRideGoalLocations
    air_ride_progression_high_effort: AirRideProgressionHighEffort
    air_ride_progression_free_run: AirRideProgressionFreeRun
    air_ride_progression_time_attack: AirRideProgressionTimeAttack
    air_ride_checkbox_fillers: AirRideCheckboxFillers

    # Top Ride
    top_ride_goal: TopRideGoal
    top_ride_checklist_amount: TopRideChecklistAmount
    top_ride_goal_locations: TopRideGoalLocations
    top_ride_progression_high_effort: TopRideProgressionHighEffort
    top_ride_progression_free_run: TopRideProgressionFreeRun
    top_ride_progression_time_attack: TopRideProgressionTimeAttack
    top_ride_progression_multiplayer: TopRideProgressionMultiplayer
    top_ride_checkbox_fillers: TopRideCheckboxFillers

    # Archipelago Checklist
    archipelago_goal: ArchipelagoGoal
    archipelago_checklist_amount: ArchipelagoChecklistAmount
    archipelago_goal_locations: ArchipelagoGoalLocations
    archipelago_checkbox_fillers: ArchipelagoCheckboxFillers

    # Access Gating
    city_trial_events_gated: CityTrialEventsGated
    abilities_gated: AbilitiesGated
    base_abilities_gated: BaseAbilitiesGated
    city_trial_patches_gated: CityTrialPatchesGated
    city_trial_items_gated: CityTrialItemsGated
    machines_gated: MachinesGated
    city_trial_boxes_gated: CityTrialBoxesGated
    air_ride_courses_gated: AirRideCoursesGated
    colors_gated: ColorsGated
    top_ride_courses_gated: TopRideCoursesGated
    top_ride_items_gated: TopRideItemsGated


kar_option_groups = [
    OptionGroup(
        "General Options",
        [EnergyLink, TrapLink, RevealChecklists, ShuffleChecklistRewards, ChecklistRewardsGated],
    ),
    OptionGroup(
        "Item Options",
        [
            SpawnRateMin,
            SpawnRateMax,
            TrapChance,
            Traps,
            AllowedItems,
        ],
    ),
    OptionGroup(
        "City Trial Options",
        [
            CityTrialGoal,
            CityTrialChecklistAmount,
            CityTrialGoalLocations,
            CityTrialProgressionHighEffort,
            CityTrialProgressionFreeRun,
            CityTrialProgressionMultiplayer,
            CityTrialProgressionRNG,
            CityTrialProgressionBustVehicles,
            CityTrialCheckboxFillers,
            CityTrialPatchCapMin,
            CityTrialPatchCapMax,
            CityTrialStadiumsGated,
            CityTrialEventsGated,
            CityTrialPatchesGated,
            CityTrialItemsGated,
            CityTrialBoxesGated,
        ],
    ),
    OptionGroup(
        "Air Ride Options",
        [
            AirRideGoal,
            AirRideChecklistAmount,
            AirRideGoalLocations,
            AirRideProgressionFreeRun,
            AirRideProgressionTimeAttack,
            AirRideProgressionHighEffort,
            AirRideCheckboxFillers,
            AirRideCoursesGated,
        ],
    ),
    OptionGroup(
        "Top Ride Options",
        [
            TopRideGoal,
            TopRideChecklistAmount,
            TopRideGoalLocations,
            TopRideProgressionFreeRun,
            TopRideProgressionTimeAttack,
            TopRideProgressionHighEffort,
            TopRideProgressionMultiplayer,
            TopRideCheckboxFillers,
            TopRideCoursesGated,
            TopRideItemsGated,
        ],
    ),
    OptionGroup(
        "Archipelago Checklist Options",
        [
            ArchipelagoGoal,
            ArchipelagoChecklistAmount,
            ArchipelagoGoalLocations,
            ArchipelagoCheckboxFillers,
        ],
    ),
    OptionGroup(
        "Other Gating",
        [
            AbilitiesGated,
            BaseAbilitiesGated,
            ColorsGated,
            MachinesGated,
        ],
    ),
]
