from dataclasses import dataclass

from Options import (
    Choice,
    DeathLinkMixin,
    DefaultOnToggle,
    LocationSet,
    NamedRange,
    OptionGroup,
    PerGameCommonOptions,
    Range,
    Toggle,
)


class TrapChance(Range):
    """
    Percentage chance for non-progression item slots to contain traps.
    Set to 0 to disable traps entirely.
    """

    display_name = "Trap Chance"
    default = 0
    range_start = 0
    range_end = 100


class TrapWeight(Choice):
    """Base class for trap weight options."""

    option_disabled = 0
    option_low = 1
    option_medium = 2
    option_high = 4
    default = 2


class TrapWeightDirectDamage(TrapWeight):
    """
    Weight for direct damage traps: 1 HP Trap.
    """

    display_name = "Direct Damage Trap Weight"


class TrapWeightStatDebuff(TrapWeight):
    """
    Weight for stat debuff traps: All Down, stat-down patches, Speed Min, Charge None,
    Drop Patches Trap.
    """

    display_name = "Stat Debuff Trap Weight"


class TrapWeightFakePatches(TrapWeight):
    """
    Weight for fake patch traps: items that look like stat-ups but are harmful.
    """

    display_name = "Fake Patch Trap Weight"


class TrapWeightHazards(TrapWeight):
    """
    Weight for hazard item traps: Panic Spin, Sensor Bomb, Gordo.
    """

    display_name = "Hazard Trap Weight"


class ProgressiveSpawnRate(Toggle):
    """
    If on, the City Trial / Top Ride item spawn rate starts at "Spawn Rate Min" and grows toward
    "Spawn Rate Max" as you receive "Spawn Rate Up" items (each grants +10%). The item pool will
    contain (max - min) / 10 Spawn Rate Up items, so collecting all of them reaches the max.
    If off, spawn rate stays at the vanilla baseline (100%) and no Spawn Rate Up items are placed.
    Air Ride has no spawn-rate scaling and is unaffected either way.
    """

    default = 0
    display_name = "Progressive Spawn Rate"


class SpawnRateMin(Range):
    """
    Starting spawn rate percent when "Progressive Spawn Rate" is on. 100 = vanilla baseline,
    200 = 2x as many items spawn, etc. Ignored when progressive is off.
    """

    display_name = "Spawn Rate Min"
    default = 100
    range_start = 100
    range_end = 500


class SpawnRateMax(Range):
    """
    Spawn rate percent reached after collecting every "Spawn Rate Up" item. The item pool will
    contain (max - min) / 10 Spawn Rate Up items (rounded down). Must be >= "Spawn Rate Min".
    The mod's hard cap is 500% regardless of this value. Ignored when progressive is off.
    """

    display_name = "Spawn Rate Max"
    default = 500
    range_start = 100
    range_end = 500


class EnergyLink(Toggle):
    """
    This enables or disables EnergyLink features. This means that collected patches or destroyed objects in
    City Trial will send energy to the collective energy pool of the Multiworld. You can spend some of this
    energy to get specific patches or other items immediately.

    This value seeds the in-game Energy Link menu toggle on first connect. After that, the in-game menu
    is authoritative: toggling it there will override this setting for the rest of the session.
    """

    default = 0
    display_name = "Energy Link"


class TrapLink(Toggle):
    """
    This enables or disables TrapLink. When on, traps you receive in-game are broadcast to other players
    with TrapLink enabled, and you receive traps they broadcast in return. Independent of "Trap Chance":
    you can participate in TrapLink even with no traps in your own pool (you'll still receive others'),
    and you can disable TrapLink while keeping traps in your pool.

    This value seeds the in-game Trap Link menu toggle on first connect. After that, the in-game menu
    is authoritative: toggling it there will override this setting for the rest of the session.
    """

    default = 0
    display_name = "Trap Link"


class RevealChecklists(Toggle):
    """
    If this is enabled, the checklists for each of your enabled game modes will start off as completely revealed.
    """

    default = 0
    display_name = "Reveal Checklists"


class CrossModePlacement(DefaultOnToggle):
    """
    Controls whether your own game modes share progression, when you have more than one enabled.

    If on (default), all of your items can be placed at any of your checklist locations across every
    enabled mode: an Air Ride unlock might be found on a City Trial checkbox, and vice versa.

    If off, your modes are kept separate for progression: an item needed to progress a single mode is
    restricted to that mode's locations, so City Trial progress comes only from City Trial checks, Air
    Ride from Air Ride, and Top Ride from Top Ride. Two caveats:
      - Unlocks that genuinely apply to more than one mode (copy abilities and machines affect both
        City Trial and Air Ride; colors affect all three) may be placed in any mode they apply to, so
        those few items can still tie modes together.
      - Only progression is locked. Non-progression items (checklist rewards, spawn-rate-ups, traps,
        and filler) gate nothing, so they are still placed freely across all enabled modes.

    Items placed remotely (in other players' worlds) are never affected either way.
    """

    display_name = "Cross-Mode Placement"


class CityTrialGoal(Choice):
    """
    Sets the goal for City Trial. If you have goals on multiple game modes, all must be achieved to win.
    Select "None" to disable City Trial.

    "max_stats_in_one_run" requires reaching the patch cap target (City Trial Patch Cap Amount) on
    every stat in a single City Trial trial round. Pairs with Progressive Patch Caps to make the
    target reachable only after collecting Patch Cap Increase items.
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


class CityTrialPermanentPatches(Toggle):
    """
    This controls whether permanent patch increase items are generated. This applies to City Trial only.
    """

    default = 1
    display_name = "City Trial Permanent Patches"


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


class CityTrialProgressivePatchCaps(Toggle):
    """
    This controls whether the maxiumum value you can have for patches is capped. If so, you can unlock higher
    patch caps by getting "Patch Cap Increase" items.
    """

    default = 0
    display_name = "City Trial Progressive Patch Caps"


class CityTrialPatchCapAmount(Range):
    """
    Sets the target (maximum) per-stat patch cap.

    With Progressive Patch Caps ON, the cap starts at 1 and grows toward this value as Patch Cap
    Increase items are received (one item is added to the pool for each step, target - 1 items).
    With Progressive Patch Caps OFF, the cap is locked at this value from the start.

    The "max_stats_in_one_run" City Trial goal uses this value as the per-stat threshold all 9 stats
    must reach in a single trial round to win. Default 18 matches the vanilla per-stat cap.
    The PowerPC hardware ceiling is 127.
    """

    default = 18
    range_start = 1
    range_end = 127
    display_name = "Patch Cap Target"


class CityTrialProgressiveStadiums(Toggle):
    """
    Toggles whether stadiums need to be found and unlocked. If on, the game starts with one random
    stadium unlocked (chosen from stadiums that aren't checklist rewards, and not VS King Dedede when
    that is the goal). To unlock more, you will need to find the corresponding stadium unlock item
    for that stadium. If off, stadiums are unlocked via random chance and checkboxes as usual.
    """

    default = 1
    display_name = "City Trial Progressive Stadiums"


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


class CityTrialEventsGated(DefaultOnToggle):
    """
    When enabled, City Trial events (Dyna Blade, Meteor, Tac, etc.) are locked and must be
    unlocked by finding their corresponding items.
    """

    display_name = "City Trial Events Gated"


class AbilitiesGated(DefaultOnToggle):
    """
    When enabled, copy abilities (Fire, Sword, Bomb, etc.) are locked and must be unlocked
    by finding their corresponding items.
    """

    display_name = "Copy Abilities Gated"


class CityTrialPatchesGated(DefaultOnToggle):
    """
    When enabled, patch stat types (Accel, Top Speed, Offense, etc.) are locked and must be
    unlocked by finding their corresponding items.
    """

    display_name = "City Trial Patch Types Gated"


class CityTrialItemsGated(Toggle):
    """
    When enabled, game items (All Up, Speed Max, Candy, food, hazards, legendary parts, etc.)
    are locked and must be unlocked by finding their corresponding items.
    Adds 30 unlock items to the progression pool; enable more game modes for more locations.
    """

    display_name = "City Trial Items Gated"


class MachinesGated(Toggle):
    """
    When enabled, air ride machines are locked and must be unlocked by finding their
    corresponding items. Applies to both City Trial and Air Ride.
    Adds 25 unlock items to the progression pool; enable more game modes for more locations.
    """

    display_name = "Machines Gated"


class CityTrialBoxesGated(DefaultOnToggle):
    """
    When enabled, box types (Blue, Green, Red) are locked and must be unlocked by finding
    their corresponding items.
    """

    display_name = "City Trial Boxes Gated"


class AirRideCoursesGated(DefaultOnToggle):
    """
    When enabled, Air Ride courses are locked and must be unlocked by finding their
    corresponding items.
    """

    display_name = "Air Ride Courses Gated"


class ColorsGated(DefaultOnToggle):
    """
    When enabled, Kirby colors (other than Pink) are locked and must be unlocked by finding
    their corresponding items.
    """

    display_name = "Kirby Colors Gated"


class TopRideCoursesGated(DefaultOnToggle):
    """
    When enabled, Top Ride courses are locked and must be unlocked by finding their
    corresponding items.
    """

    display_name = "Top Ride Courses Gated"


class TopRideItemsGated(DefaultOnToggle):
    """
    When enabled, Top Ride items are locked and must be unlocked by finding their
    corresponding items. Items tied to copy abilities (Freeze Fan, Fire, Bomb, Walky)
    are gated by the copy ability unlock instead.
    """

    display_name = "Top Ride Items Gated"


@dataclass
class KAROptions(PerGameCommonOptions, DeathLinkMixin):
    """Configuration options for Kirby Air Ride."""

    # General
    trap_chance: TrapChance
    trap_weight_direct_damage: TrapWeightDirectDamage
    trap_weight_stat_debuff: TrapWeightStatDebuff
    trap_weight_fake_patches: TrapWeightFakePatches
    trap_weight_hazards: TrapWeightHazards
    trap_link: TrapLink
    spawn_rate_progressive: ProgressiveSpawnRate
    spawn_rate_min: SpawnRateMin
    spawn_rate_max: SpawnRateMax
    energy_link: EnergyLink
    reveal_checklists: RevealChecklists
    cross_mode_placement: CrossModePlacement

    # City Trial
    city_trial_goal: CityTrialGoal
    city_trial_checklist_amount: CityTrialChecklistAmount
    city_trial_goal_locations: CityTrialGoalLocations
    city_trial_progression_high_effort: CityTrialProgressionHighEffort
    city_trial_progression_free_run: CityTrialProgressionFreeRun
    city_trial_progression_multiplayer: CityTrialProgressionMultiplayer
    city_trial_progression_rng: CityTrialProgressionRNG
    city_trial_progression_bust_vehicles: CityTrialProgressionBustVehicles
    city_trial_permanent_patches: CityTrialPermanentPatches
    city_trial_checkbox_fillers: CityTrialCheckboxFillers
    city_trial_progressive_patch_caps: CityTrialProgressivePatchCaps
    city_trial_patch_cap_amount: CityTrialPatchCapAmount
    city_trial_progressive_stadiums: CityTrialProgressiveStadiums

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

    # Access Gating
    city_trial_events_gated: CityTrialEventsGated
    abilities_gated: AbilitiesGated
    city_trial_patches_gated: CityTrialPatchesGated
    city_trial_items_gated: CityTrialItemsGated
    machines_gated: MachinesGated
    city_trial_boxes_gated: CityTrialBoxesGated
    air_ride_courses_gated: AirRideCoursesGated
    colors_gated: ColorsGated
    top_ride_courses_gated: TopRideCoursesGated
    top_ride_items_gated: TopRideItemsGated


kar_option_groups = [
    OptionGroup("General Options", [EnergyLink, TrapLink, RevealChecklists, CrossModePlacement]),
    OptionGroup(
        "Item Options",
        [
            ProgressiveSpawnRate,
            SpawnRateMin,
            SpawnRateMax,
            TrapChance,
            TrapWeightDirectDamage,
            TrapWeightStatDebuff,
            TrapWeightFakePatches,
            TrapWeightHazards,
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
            CityTrialPermanentPatches,
            CityTrialCheckboxFillers,
            CityTrialProgressivePatchCaps,
            CityTrialPatchCapAmount,
            CityTrialProgressiveStadiums,
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
        "Other Gating",
        [
            AbilitiesGated,
            ColorsGated,
            MachinesGated,
        ],
    ),
]
