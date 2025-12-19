from dataclasses import dataclass
from typing import Any

from Options import (
    DeathLinkMixin,
    OptionGroup,
    PerGameCommonOptions,
    Range,
    TextChoice,
    Toggle,
)


class TrapsEnabled(Toggle):
    """
    This controls whether trap items will be placed into the item pool. These will only replace filler items.
    """

    display_name = "Traps Enabled"
    default = 0


class TrapChance(Range):
    """
    Percentage chance for filler items to be replaced with traps. Only has an effect if traps are enabled.
    """

    display_name = "Trap Chance"
    default = 10
    range_start = 0
    range_end = 100


class EffectItemsEnabled(Toggle):
    """
    This controls whether "effect" items such as "1 HP" trap, "Full Heal", etc. will be placed into the item pool.
    """

    display_name = "Effect Items Enabled"
    default = 1


class CheckboxFillersProgression(Toggle):
    """
    Toggles whether "checkbox filler" items are progression items.
    """

    display_name = "Checkbox fillers are progression"
    default = 1


class EnergyLink(Toggle):
    """
    This enables or disables EnergyLink features. This means that collected patches or destroyed objects in
    City Trial will send energy to the collective energy pool of the Multiworld. You can spend some of this
    energy to get specific patches or other items immediately.
    """

    default = 1
    display_name = "Energy Link"


class RevealChecklists(Toggle):
    """
    If this is enabled, the checklists for each of your enabled game modes will start off as completely revealed.
    """

    default = 0
    display_name = "Reveal Checklists"


class CityTrialGoal(TextChoice):
    """
    This sets the Goal for the run. You can also input a custom location from the location list as a goal.
    You can have a goal for each game mode if you wish.
    If you have goals on multiple game modes, all goals will need to be achieved in order to complete your game.
    Select "None" if you wish to disable City Trial in your game.
    """

    display_name = "City Trial Goal"
    option_100_checklist_blocks = "City Trial: Fill in over 100 Checklist blocks!"
    option_n_checklist_blocks = "City Trial: Fill in N Checklist blocks!"
    option_hydra_and_dragoon = "City Trial: In one match, complete both Dragoon and Hydra!"
    option_beat_king_dedede = "Stadium: VS. KING DEDEDE KO King Dedede in less than a minute!"
    option_none = "None"
    default = option_100_checklist_blocks


class CityTrialCheckListAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for City Trial.
    """

    display_name = "Number of Checklist Boxes for City Trial"
    default = 60
    range_start = 1
    range_end = 120


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


class CityTrialPermanentPatchProgression(Toggle):
    """
    This controls whether permanent patch increase items are a part of progression. This applies only to City Trial, and
    only if Permanent Patches are enabled.
    """

    default = 1
    display_name = "Permanent Patches are progression"


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


class CityTrialCheckboxFillers(Toggle):
    """
    This controls whether "checkbox filler" items for City Trial are added to the pool.
    """

    default = 1
    display_name = "City Trial Checkbox Fillers"


class CityTrialCheckboxFillersAmount(Range):
    """
    This controls the number of "checkbox filler" items that are added to the pool for City Trial.
    """

    default = 5
    range_start = 1
    range_end = 20
    display_name = "Number of City Trial Checkbox Fillers"


class CityTrialProgressivePatchCaps(Toggle):
    """
    This controls whether the maxiumum value you can have for patches is capped. If so, you can unlock higher
    patch caps by getting "Patch Cap Increase" items.
    """

    default = 0
    display_name = "City Trial Progressive Patch Caps"


class CityTrialPatchCapAmount(Range):
    """
    Sets the starting cap on patch maximum amount.
    """

    default = 10
    range_start = 1
    range_end = 17
    display_name = "Patch Cap Starting Amount"


class CityTrialProgressiveStadiums(Toggle):
    """
    Toggles whether stadiums need to be found and unlocked. If on, the game starts with a single stadium
    unlocked. To unlock more, you will need to find the corresponding stadium unlock item for that stadium.
    If off, stadiums are unlocked via random chance and checkboxes as usual.
    """

    default = 1
    display_name = "City Trial Progressive Stadiums"


class AirRideGoal(TextChoice):
    """
    This sets the Goal for the run. You can also input a custom location from the location list as a goal.
    You can have a goal for each game mode if you wish.
    If you have goals on multiple game modes, all goals will need to be achieved in order to complete your game.
    Select "None" if you wish to disable Air Ride in your game.
    """

    display_name = "Air Ride Goal"
    option_100_checklist_blocks = "Air Ride: Fill in over 100 Checklist blocks!"
    option_n_checklist_blocks = "Air Ride: Fill in N Checklist blocks!"
    option_none = "None"
    default = option_none


class AirRideCheckListAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for Air Ride.
    """

    display_name = "Number of Checklist Boxes for Air Ride"
    default = 60
    range_start = 1
    range_end = 120


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


class AirRideCheckboxFillers(Toggle):
    """
    This controls whether "checkbox filler" items for Air Ride are added to the pool.
    """

    default = 1
    display_name = "Air Ride Checkbox Fillers"


class AirRideCheckboxFillersAmount(Range):
    """
    This controls the number of "checkbox filler" items that are added to the pool for Air Ride.
    """

    default = 5
    range_start = 1
    range_end = 20
    display_name = "Number of Air Ride Checkbox Fillers"


class TopRideGoal(TextChoice):
    """
    This sets the Goal for the run. You can also input a custom location from the location list as a goal.
    You can have a goal for each game mode if you wish.
    If you have goals on multiple game modes, all goals will need to be achieved in order to complete your game.
    Select "None" if you wish to disable Top Ride in your game.
    """

    display_name = "Top Ride Goal"
    option_100_checklist_blocks = "Top Ride: Fill in over 100 Checklist blocks!"
    option_n_checklist_blocks = "Top Ride: Fill in N Checklist blocks!"
    option_none = "None"
    default = option_none


class TopRideCheckListAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist blocks!' goal for Top Ride.
    """

    display_name = "Number of Checklist Boxes for Top Ride"
    default = 60
    range_start = 1
    range_end = 120


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


class TopRideCheckboxFillers(Toggle):
    """
    This controls whether "checkbox filler" items for Top Ride are added to the pool.
    """

    default = 1
    display_name = "Top Ride Checkbox Fillers"


class TopRideCheckboxFillersAmount(Range):
    """
    This controls the number of "checkbox filler" items that are added to the pool for Top Ride.
    """

    default = 5
    range_start = 1
    range_end = 20
    display_name = "Number of Top Ride Checkbox Fillers"


@dataclass
class KAROptions(PerGameCommonOptions, DeathLinkMixin):
    """
    A data class that encapsulates all configuration options for Kirby Air Ride.
    """

    traps_enabled: TrapsEnabled
    trap_chance: TrapChance
    effect_items_enabled: EffectItemsEnabled
    checkbox_fillers_progression: CheckboxFillersProgression
    energy_link: EnergyLink
    reveal_checklists: RevealChecklists
    city_trial_goal: CityTrialGoal
    city_trial_checklist_amount: CityTrialCheckListAmount
    city_trial_progression_high_effort: CityTrialProgressionHighEffort
    city_trial_progression_free_run: CityTrialProgressionFreeRun
    city_trial_progression_multiplayer: CityTrialProgressionMultiplayer
    city_trial_progression_rng: CityTrialProgressionRNG
    city_trial_progression_bust_vehicles: CityTrialProgressionBustVehicles
    city_trial_permanent_patches: CityTrialPermanentPatches
    city_trial_permanent_patch_progression: CityTrialPermanentPatchProgression
    city_trial_checkbox_fillers: CityTrialCheckboxFillers
    city_trial_checkbox_fillers_amount: CityTrialCheckboxFillersAmount
    city_trial_progressive_patch_caps: CityTrialProgressivePatchCaps
    city_trial_patch_cap_amount: CityTrialPatchCapAmount
    city_trial_progressive_stadiums: CityTrialProgressiveStadiums
    air_ride_goal: AirRideGoal
    air_ride_checklist_amount: AirRideCheckListAmount
    air_ride_progression_high_effort: AirRideProgressionHighEffort
    air_ride_progression_free_run: AirRideProgressionFreeRun
    air_ride_progression_time_attack: AirRideProgressionTimeAttack
    air_ride_checkbox_fillers: AirRideCheckboxFillers
    air_ride_checkbox_fillers_amount: AirRideCheckboxFillersAmount
    top_ride_goal: TopRideGoal
    top_ride_checklist_amount: TopRideCheckListAmount
    top_ride_progression_high_effort: TopRideProgressionHighEffort
    top_ride_progression_free_run: TopRideProgressionFreeRun
    top_ride_progression_time_attack: TopRideProgressionTimeAttack
    top_ride_progression_multiplayer: TopRideProgressionMultiplayer
    top_ride_checkbox_fillers: TopRideCheckboxFillers
    top_ride_checkbox_fillers_amount: TopRideCheckboxFillersAmount

    def get_output_dict(self) -> dict[str, Any]:
        """
        Returns a dictionary of option name to value. This is used later in slot_data.
        """

        return self.as_dict(
            "traps_enabled",
            "trap_chance",
            "effect_items_enabled",
            "checkbox_fillers_progression",
            "energy_link",
            "reveal_checklists",
            "death_link",
            "city_trial_goal",
            "city_trial_checklist_amount",
            "city_trial_progression_high_effort",
            "city_trial_progression_free_run",
            "city_trial_progression_multiplayer",
            "city_trial_progression_rng",
            "city_trial_progression_bust_vehicles",
            "city_trial_permanent_patches",
            "city_trial_permanent_patch_progression",
            "city_trial_checkbox_fillers",
            "city_trial_checkbox_fillers_amount",
            "city_trial_progressive_patch_caps",
            "city_trial_patch_cap_amount",
            "city_trial_progressive_stadiums",
            "air_ride_goal",
            "air_ride_checklist_amount",
            "air_ride_progression_high_effort",
            "air_ride_progression_free_run",
            "air_ride_progression_time_attack",
            "air_ride_checkbox_fillers",
            "air_ride_checkbox_fillers_amount",
            "top_ride_goal",
            "top_ride_checklist_amount",
            "top_ride_progression_high_effort",
            "top_ride_progression_free_run",
            "top_ride_progression_time_attack",
            "top_ride_progression_multiplayer",
            "top_ride_checkbox_fillers",
            "top_ride_checkbox_fillers_amount",
        )


kar_option_groups = [
    OptionGroup("Item Options", [TrapsEnabled, TrapChance, EffectItemsEnabled, CheckboxFillersProgression]),
    OptionGroup(
        "City Trial Options",
        [
            CityTrialGoal,
            CityTrialCheckListAmount,
            CityTrialProgressionHighEffort,
            CityTrialProgressionFreeRun,
            CityTrialProgressionMultiplayer,
            CityTrialProgressionRNG,
            CityTrialProgressionBustVehicles,
            CityTrialPermanentPatches,
            CityTrialPermanentPatchProgression,
            CityTrialCheckboxFillers,
            CityTrialCheckboxFillersAmount,
            CityTrialProgressivePatchCaps,
            CityTrialPatchCapAmount,
            CityTrialProgressiveStadiums,
        ],
    ),
    OptionGroup(
        "Air Ride Options",
        [
            AirRideGoal,
            AirRideCheckListAmount,
            AirRideProgressionFreeRun,
            AirRideProgressionTimeAttack,
            AirRideProgressionHighEffort,
            AirRideCheckboxFillers,
            AirRideCheckboxFillersAmount,
        ],
    ),
    OptionGroup(
        "Top Ride Options",
        [
            TopRideGoal,
            TopRideCheckListAmount,
            TopRideProgressionFreeRun,
            TopRideProgressionTimeAttack,
            TopRideProgressionHighEffort,
            TopRideProgressionMultiplayer,
            TopRideCheckboxFillers,
            TopRideCheckboxFillersAmount,
        ],
    ),
]
