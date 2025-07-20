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


class CheckboxRewardItems(Toggle):
    """
    This controls whether the in-game default checkbox rewards will be placed as locked items for their checkbox location.
    Currently, only your game will be able to collect these. This applies to all game modes.
    """

    display_name = "Checkbox rewards are items"
    default = 0


class EnergyLink(Toggle):
    """
    This enables or disables EnergyLink features. This means that collected patches or destroyed objects in
    City Trial will send energy to the collective energy pool of the Multiworld. You can spend some of this
    energy to get specific patches or other items immediately.
    """

    default = 1
    display_name = "Energy Link"


class CityTrialGoal(TextChoice):
    """
    This sets the Goal for the run. You can also input a custom location from the location list as a goal.
    You can have a goal for both City Trial and Air Ride if you wish.
    If you have goals on both, both will need to be acheived in order to complete your game.
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
    This controls whether difficult or extremely high effort checkboxes are counted in progression. This applies to City Trial only.
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
    This controls whether checkboxes that require multiple players are a part of progression. This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial Multiplayer checkboxes are progression"


class CityTrialProgressionFreeRun(Toggle):
    """
    This controls whether Free Run checkboxes are a part of progression. This applies to City Trial only.
    """

    default = 0
    display_name = "City Trial Free Run checkboxes are progression"


class AirRideGoal(TextChoice):
    """
    This sets the Goal for the run. You can also input a custom location from the location list as a goal.
    You can have a goal for both City Trial and Air Ride if you wish.
    If you have goals on both, both will need to be acheived in order to complete your game.
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
    This controls whether difficult or extremely high effort checkboxes are counted in progression. This applies to Air Ride only.
    """

    default = 0
    display_name = "Air Ride Long/High effort checkboxes are progression"


@dataclass
class KAROptions(PerGameCommonOptions, DeathLinkMixin):
    """
    A data class that encapsulates all configuration options for Kirby Air Ride.
    """

    traps_enabled: TrapsEnabled
    trap_chance: TrapChance
    effect_items_enabled: EffectItemsEnabled
    checkbox_reward_items: CheckboxRewardItems
    energy_link: EnergyLink
    city_trial_goal: CityTrialGoal
    city_trial_checklist_amount: CityTrialCheckListAmount
    city_trial_progression_high_effort: CityTrialProgressionHighEffort
    city_trial_progression_free_run: CityTrialProgressionFreeRun
    city_trial_progression_multiplayer: CityTrialProgressionMultiplayer
    city_trial_permanent_patches: CityTrialPermanentPatches
    city_trial_permanent_patch_progression: CityTrialPermanentPatchProgression
    air_ride_goal: AirRideGoal
    air_ride_checklist_amount: AirRideCheckListAmount
    air_ride_progression_high_effort: AirRideProgressionHighEffort
    air_ride_progression_free_run: AirRideProgressionFreeRun
    air_ride_progression_time_attack: AirRideProgressionTimeAttack

    def get_output_dict(self) -> dict[str, Any]:
        """
        Returns a dictionary of option name to value. This is used later in slot_data.
        """

        return self.as_dict(
            "traps_enabled",
            "trap_chance",
            "effect_items_enabled",
            "checkbox_reward_items",
            "energy_link",
            "death_link",
            "city_trial_goal",
            "city_trial_checklist_amount",
            "city_trial_progression_high_effort",
            "city_trial_progression_free_run",
            "city_trial_progression_multiplayer",
            "city_trial_permanent_patches",
            "city_trial_permanent_patch_progression",
            "air_ride_goal",
            "air_ride_checklist_amount",
            "air_ride_progression_high_effort",
            "air_ride_progression_free_run",
            "air_ride_progression_time_attack",
        )


kar_option_groups = [
    OptionGroup("Item Options", [TrapsEnabled, TrapChance, EffectItemsEnabled, CheckboxRewardItems]),
    OptionGroup(
        "City Trial Options",
        [
            CityTrialGoal,
            CityTrialCheckListAmount,
            CityTrialProgressionHighEffort,
            CityTrialProgressionFreeRun,
            CityTrialProgressionMultiplayer,
            CityTrialPermanentPatches,
            CityTrialPermanentPatchProgression,
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
        ],
    ),
]
