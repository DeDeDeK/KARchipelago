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

from .KARData import AP_CHECKLIST_CODE_NUM, AP_PATCH_CODE_MAX
from .KARItems import ALLOWED_ITEM_CATEGORIES, CHECKLIST_REWARD_CATEGORIES, TRAP_CATEGORIES, KARItemGroup


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

    Defaults to "Permanent Patches" only; add the others to put their gives in your pool.

    Valid categories are:
    - "Permanent Patches"
    - "City Trial Item Gives"
    - "City Trial Event Gives"
    - "Copy Ability Gives"
    - "Top Ride Item Gives"
    """

    display_name = "Allowed Item Types"
    valid_keys = frozenset(str(category) for category in ALLOWED_ITEM_CATEGORIES)
    default = frozenset({str(KARItemGroup.PERMANENT_PATCHES)})


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
    and Top Ride.
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


class ChecklistRewards(OptionSet):
    """
    Which categories of the game's vanilla checklist rewards (red boxes) are placed as items into the
    multiworld. Valid categories are:

    - "Sound Test": sound test entries
    - "Music": course and stadium music tracks
    - "Filler Boxes": boxes awarding a checkbox filler
    - "Endings": the ending movie for each mode
    - "Gameplay Extras": Top Ride extra rules, Air Ride's Special Machine Intros, City Trial's pause-screen
      power-up display

    Only categories you specify are added to the pool. Others are left out, and automatically unlocked in-game
    from the start. In-game checklists will not contain these items.

    Other reward categories are gated by other options. This option only covers the categories above.
    """

    display_name = "Checklist Rewards"
    valid_keys = frozenset(CHECKLIST_REWARD_CATEGORIES)
    default = frozenset()


class CityTrialGoal(Choice):
    """
    Sets the goal for City Trial.

    - 100 Checklist Blocks: Get the checkbox for getting 100 checkboxes in the City Trial Checklist
    - N Checklist Blocks: Get the specified number of checkboxes
    - Hydra and Dragoon: Get the checkbox for assembling Hydra and Dragoon in a single CT run
    - Beat King DeDeDe: Get the checkbox for defeating King DeDeDe in under a minute
    - Checklist List: Specify a custom list of City Trial checkboxes (locations) to complete
    - Max Stats in One Run: Get max stats for every patch in one CT run

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
    Number of "checkbox filler" items added to pool for the City Trial Checklist.
    Set to 0 to disable.
    """

    display_name = "City Trial Checkbox Fillers"
    default = 5
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class APPatches(NamedRange):
    """
    Number of AP Patches in the seed. AP Patches drop from Archipelago boxes in City Trial.
    Every AP patch collected is a check, and any rider can collect one, even CPUs.

    Use this to add more locations to the world that can hold items.

    Patches are collected in order, so logic splits larger counts into groups of 20 that open one
    after another rather than treating them as one flat pool.

    Set to 0 to disable AP patches.
    """

    display_name = "AP Patches"
    default = 20
    range_start = 0
    range_end = AP_PATCH_CODE_MAX
    special_range_names = {  # noqa: RUF012
        "disabled": 0,
        "low": 20,
        "normal": 50,
        "high": AP_PATCH_CODE_MAX,
    }


class APPatchPlacement(Choice):
    """
    Whether AP Patch locations can hold progression.

    - Default: treated like any other location.
    - Excluded: filler only.
    """

    display_name = "AP Patch Placement"
    option_default = 0
    option_excluded = 1
    default = 0


class CityTrialRevealChecklist(Toggle):
    """
    If enabled, the City Trial checklist starts off completely revealed.
    Revealing is visual only: it does not complete or unlock anything.
    """

    default = 0
    display_name = "City Trial Reveal Checklist"


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
    When enabled, City Trial stadiums are locked and must be unlocked by finding their
    corresponding Unlock Stadium items.

    When disabled, every stadium is available from the start and no Unlock Stadium items are added to the
    pool.
    """

    display_name = "City Trial Stadiums Gated"


class StartingStadium(Choice):
    """
    The City Trial stadium unlocked from the start.

    Only applies when City Trial is enabled and "City Trial Stadiums Gated" is on; otherwise ignored.
    VS. KING DEDEDE cannot be picked when it is your City Trial goal.
    """

    display_name = "Starting Stadium"
    default = 0
    option_randomized = 0
    option_drag_race_1 = 1
    option_drag_race_2 = 2
    option_drag_race_3 = 3
    option_drag_race_4 = 4
    option_air_glider = 5
    option_target_flight = 6
    option_high_jump = 7
    option_kirby_melee_1 = 8
    option_kirby_melee_2 = 9
    option_destruction_derby_1 = 10
    option_destruction_derby_2 = 11
    option_destruction_derby_3 = 12
    option_destruction_derby_4 = 13
    option_destruction_derby_5 = 14
    option_single_race_1 = 15
    option_single_race_2 = 16
    option_single_race_3 = 17
    option_single_race_4 = 18
    option_single_race_5 = 19
    option_single_race_6 = 20
    option_single_race_7 = 21
    option_single_race_8 = 22
    option_single_race_9 = 23
    option_vs_king_dedede = 24


class AirRideGoal(Choice):
    """
    Sets the goal for Air Ride.

    - 100 Checklist Blocks: Get the checkbox for getting 100 checkboxes in the Air Ride Checklist
    - N Checklist Blocks: Get the specified number of checkboxes
    - Checklist List: Specify a custom list of Air Ride checkboxes (locations) to complete

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


class AirRideProgressionRNG(Toggle):
    """
    This controls whether checkboxes that require RNG elements of the game are a part of progression.
    This applies to Air Ride only.
    """

    default = 0
    display_name = "Air Ride RNG checkboxes are progression"


class AirRideCheckboxFillers(NamedRange):
    """
    Number of "checkbox filler" items added to the pool for the Air Ride Checklist.
    Set to 0 to disable.
    """

    display_name = "Air Ride Checkbox Fillers"
    default = 5
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class AirRideRevealChecklist(Toggle):
    """
    If enabled, the Air Ride checklist starts off completely revealed.
    Revealing is visual only: it does not complete or unlock anything.
    """

    default = 0
    display_name = "Air Ride Reveal Checklist"


class TopRideGoal(Choice):
    """
    Sets the goal for Top Ride.

    - 100 Checklist Blocks: Get the checkbox for getting 100 checkboxes in the Top Ride Checklist
    - N Checklist Blocks: Get the specified number of checkboxes
    - Checklist List: Specify a custom list of Top Ride checkboxes (locations) to complete

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
    Number of "checkbox filler" items added to the pool for the Top Ride Checklist.
    Set to 0 to disable.
    """

    display_name = "Top Ride Checkbox Fillers"
    default = 5
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class TopRideRevealChecklist(Toggle):
    """
    If enabled, the Top Ride checklist starts off completely revealed instead of filling in around
    the squares you complete. Revealing is visual only: it does not complete or unlock anything.
    """

    default = 0
    display_name = "Top Ride Reveal Checklist"


class ArchipelagoGoal(Choice):
    """
    EXPERIMENTAL - ONLY USE IF YOU WANT TO TEST - SOME CHECKS LIKELY BROKEN
    Sets the goal for the Archipelago checklist.

    - N Checklist Blocks: Get the specified number of checkboxes in the Archipelago Checklist
    - Checklist List: Specify a custom list of Archipelago checkboxes (locations) to complete
    - Assemble Archipelago Star: Assemble the Archipelago Star Legendary Machine in one CT run
    - Assemble All Three Legendaries in One Run: Assemble all 3 legendary machines in one CT run

    Select "None" to exclude archipelago checklist locations completely.
    """

    display_name = "Archipelago Checklist Goal"
    option_n_checklist_blocks = 1
    option_none = 4
    option_checklist_list = 5
    option_assemble_archipelago_star = 7
    option_all_three_legendaries_in_one_run = 8
    default = 4


class ArchipelagoChecklistAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for the
    Archipelago checklist.

    The Archipelago checklist holds fewer boxes than the other modes, so the range stops at what
    the checklist actually has rather than the grid's 120 cells.
    """

    display_name = "Number of Checklist Boxes for Archipelago"
    default = 25
    range_start = 1
    range_end = AP_CHECKLIST_CODE_NUM


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
    Number of "checkbox filler" items added to the pool for the Archipelago checklist.
    Set to 0 to disable.
    """

    display_name = "Archipelago Checkbox Fillers"
    default = 0
    range_start = 0
    range_end = 20
    special_range_names = {"disabled": 0}  # noqa: RUF012


class ArchipelagoRevealChecklist(Toggle):
    """
    If enabled, the Archipelago checklist starts off completely revealed.
    Revealing is visual only: it does not complete or unlock anything.
    """

    default = 0
    display_name = "Archipelago Reveal Checklist"


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
    When enabled, base abilities - inhale, quick spin, and machine charge - start locked and must
    each be unlocked by finding their item.

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
    When enabled, City Trial items (All Up, Speed Max, Candy, food, legendary parts, etc.)
    are locked and must be unlocked by finding their corresponding items.

    When disabled, all game items are available from the start and no item unlock items are added to
    the pool - except with the Hydra and Dragoon goal, which always keeps the six legendary part
    unlocks in the pool so the goal is not winnable in the first match.
    """

    display_name = "City Trial Items Gated"


class MachinesGated(Toggle):
    """
    When enabled, air ride machines are locked and must be unlocked by finding their
    corresponding items. Applies to all modes.

    When disabled, all machines are available from the start and no machine unlock items are added
    to the pool.
    """

    display_name = "Machines Gated"


class StartingMachine(Choice):
    """
    The machine unlocked unlocked from the start.

    Only applies when "Machines Gated" is on and City Trial or Air Ride is enabled; otherwise ignored.

    With "Base Abilities Gated" on, Bulk, Slick and Turbo Star cannot be picked.
    """

    display_name = "Starting Machine"
    default = 0
    option_randomized = 0
    option_warp_star = 1
    option_compact_star = 2
    option_winged_star = 3
    option_shadow_star = 4
    option_bulk_star = 5
    option_slick_star = 6
    option_formula_star = 7
    option_wagon_star = 8
    option_rocket_star = 9
    option_swerve_star = 10
    option_turbo_star = 11
    option_jet_star = 12
    option_flight_warp_star = 13
    option_meta_knight = 14
    option_wheelie_bike = 15
    option_rex_wheelie = 16
    option_wheelie_scooter = 17
    option_king_dedede = 18


class StartingTopRideMachine(Choice):
    """
    The Top Ride machine unlocked from the start.

    Only applies when "Machines Gated" is on and Top Ride is enabled; otherwise ignored.
    """

    display_name = "Starting Top Ride Machine"
    default = 0
    option_randomized = 0
    option_free_star = 1
    option_steer_star = 2


class CityTrialBoxesGated(DefaultOnToggle):
    """
    When enabled, box types (Blue, Green, Red) are locked and must be unlocked by finding
    their corresponding items.

    Boxes will still not spawn if none of their containing items are unlocked yet.

    When disabled, all box types are available from the start and no box unlock items are added to
    the pool.
    """

    display_name = "City Trial Boxes Gated"


class AirRideCoursesGated(DefaultOnToggle):
    """
    When enabled, Air Ride courses are locked and must be unlocked by finding their
    corresponding items.

    When disabled, all Air Ride courses are available from the start and no course unlock items are
    added to the pool.
    """

    display_name = "Air Ride Courses Gated"


class StartingAirRideCourse(Choice):
    """
    The Air Ride course unlocked from the start.

    Only applies when Air Ride is enabled and "Air Ride Courses Gated" is on; otherwise ignored.
    """

    display_name = "Starting Air Ride Course"
    default = 0
    option_randomized = 0
    option_fantasy_meadows = 1
    option_magma_flows = 2
    option_sky_sands = 3
    option_frozen_hillside = 4
    option_beanstalk_park = 5
    option_celestial_valley = 6
    option_machine_passage = 7
    option_checker_knights = 8
    option_nebula_belt = 9


class ColorsGated(DefaultOnToggle):
    """
    When enabled, Kirby colors are locked and must be unlocked by finding their corresponding
    items.

    When disabled, all Kirby colors are available from the start and no color unlock items are added
    to the pool.
    """

    display_name = "Kirby Colors Gated"


class StartingKirbyColor(Choice):
    """
    The Kirby color unlocked from the start.

    Only applies when "Kirby Colors Gated" is on; otherwise ignored.
    """

    display_name = "Starting Kirby Color"
    default = 0
    option_randomized = 0
    option_pink = 1
    option_yellow = 2
    option_blue = 3
    option_red = 4
    option_green = 5
    option_purple = 6
    option_brown = 7
    option_white = 8


class TopRideCoursesGated(DefaultOnToggle):
    """
    When enabled, Top Ride courses are locked and must be unlocked by finding their
    corresponding items.

    When disabled, all Top Ride courses are available from the start and no course unlock items are
    added to the pool.
    """

    display_name = "Top Ride Courses Gated"


class StartingTopRideCourse(Choice):
    """
    The Top Ride course unlocked from the start.

    Only applies when Top Ride is enabled and "Top Ride Courses Gated" is on; otherwise ignored.
    """

    display_name = "Starting Top Ride Course"
    default = 0
    option_randomized = 0
    option_grass = 1
    option_sand = 2
    option_sky = 3
    option_fire = 4
    option_light = 5
    option_water = 6
    option_metal = 7


class TopRideItemsGated(DefaultOnToggle):
    """
    When enabled, Top Ride items are locked and must be unlocked by finding their
    corresponding items.

    The four items tied to copy abilities (Freeze Fan, Fire, Bomb, Walky) are additionally unlocked
    by the copy ability unlock items.

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
    checklist_rewards: ChecklistRewards

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
    city_trial_reveal_checklist: CityTrialRevealChecklist
    city_trial_patch_cap_min: CityTrialPatchCapMin
    city_trial_patch_cap_max: CityTrialPatchCapMax
    city_trial_stadiums_gated: CityTrialStadiumsGated
    starting_stadium: StartingStadium
    ap_patches: APPatches
    ap_patch_placement: APPatchPlacement

    # Air Ride
    air_ride_goal: AirRideGoal
    air_ride_checklist_amount: AirRideChecklistAmount
    air_ride_goal_locations: AirRideGoalLocations
    air_ride_progression_high_effort: AirRideProgressionHighEffort
    air_ride_progression_free_run: AirRideProgressionFreeRun
    air_ride_progression_time_attack: AirRideProgressionTimeAttack
    air_ride_progression_rng: AirRideProgressionRNG
    air_ride_checkbox_fillers: AirRideCheckboxFillers
    air_ride_reveal_checklist: AirRideRevealChecklist

    # Top Ride
    top_ride_goal: TopRideGoal
    top_ride_checklist_amount: TopRideChecklistAmount
    top_ride_goal_locations: TopRideGoalLocations
    top_ride_progression_high_effort: TopRideProgressionHighEffort
    top_ride_progression_free_run: TopRideProgressionFreeRun
    top_ride_progression_time_attack: TopRideProgressionTimeAttack
    top_ride_progression_multiplayer: TopRideProgressionMultiplayer
    top_ride_checkbox_fillers: TopRideCheckboxFillers
    top_ride_reveal_checklist: TopRideRevealChecklist

    # Archipelago Checklist
    archipelago_goal: ArchipelagoGoal
    archipelago_checklist_amount: ArchipelagoChecklistAmount
    archipelago_goal_locations: ArchipelagoGoalLocations
    archipelago_checkbox_fillers: ArchipelagoCheckboxFillers
    archipelago_reveal_checklist: ArchipelagoRevealChecklist

    # Access Gating
    city_trial_events_gated: CityTrialEventsGated
    abilities_gated: AbilitiesGated
    base_abilities_gated: BaseAbilitiesGated
    city_trial_patches_gated: CityTrialPatchesGated
    city_trial_items_gated: CityTrialItemsGated
    machines_gated: MachinesGated
    starting_machine: StartingMachine
    starting_top_ride_machine: StartingTopRideMachine
    city_trial_boxes_gated: CityTrialBoxesGated
    air_ride_courses_gated: AirRideCoursesGated
    starting_air_ride_course: StartingAirRideCourse
    colors_gated: ColorsGated
    starting_kirby_color: StartingKirbyColor
    top_ride_courses_gated: TopRideCoursesGated
    starting_top_ride_course: StartingTopRideCourse
    top_ride_items_gated: TopRideItemsGated


kar_option_groups = [
    OptionGroup(
        "General Options",
        [EnergyLink, TrapLink, ChecklistRewards],
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
            CityTrialRevealChecklist,
            CityTrialPatchCapMin,
            CityTrialPatchCapMax,
            CityTrialStadiumsGated,
            StartingStadium,
            APPatches,
            APPatchPlacement,
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
            AirRideProgressionRNG,
            AirRideCheckboxFillers,
            AirRideRevealChecklist,
            AirRideCoursesGated,
            StartingAirRideCourse,
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
            TopRideRevealChecklist,
            TopRideCoursesGated,
            StartingTopRideCourse,
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
            ArchipelagoRevealChecklist,
        ],
    ),
    OptionGroup(
        "Other Gating",
        [
            AbilitiesGated,
            BaseAbilitiesGated,
            ColorsGated,
            StartingKirbyColor,
            MachinesGated,
            StartingMachine,
            StartingTopRideMachine,
        ],
    ),
]
