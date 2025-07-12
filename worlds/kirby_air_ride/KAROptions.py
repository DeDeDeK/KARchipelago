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


class Goal(TextChoice):
    """
    This sets the Goal for the run. Alternatively, input a custom location from the location list as a goal.

    """

    display_name = "Goal"
    option_100_checklist_boxes = "Fill in over 100 Checklist blocks!"
    option_hydra_and_dragoon = "In one match, complete both Dragoon and Hydra!"
    option_beat_king_dedede = "Stadium: VS. KING DEDEDE KO King Dedede in less than a minute!"
    option_n_checklist_boxes = "Fill in N Checklist Boxes!"
    default = option_100_checklist_boxes


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
    default = 0


class CheckListAmount(Range):
    """
    This sets the number of checklist boxes for the 'Fill in N Checklist Boxes!' goal.
    """

    display_name = "Number of Checklist Boxes"
    default = 100
    range_start = 1
    range_end = 120


class CheckboxRewardsItems(Toggle):
    """
    This controls whether the in-game default checkbox rewards will be placed as locked items for their checkbox location.
    Currently, only your game will be able to collect these.
    """

    display_name = "Checkbox rewards are items"
    default = 0


class ProgressionHighEffort(Toggle):
    """
    This controls whether difficult or extremely high effort checkboxes are counted in progression.

    """

    default = 0
    display_name = "Long/High effort checkboxes are progression"


class PermanentPatches(Toggle):
    """
    This controls whether permanent patch increase items are generated.

    """

    default = 1
    display_name = "Permanent Patches"


class PermanentPatchProgression(Toggle):
    """
    This controls whether permanent patch increase items are a part of progression.

    """

    default = 1
    display_name = "Permanent Patches are progression"


class ProgressionMultiPlayer(Toggle):
    """
    This controls whether checkboxes that require multiple players are a part of progression.
    """

    default = 0
    display_name = "Multiplayer checkboxes are progression"


class ProgressionFreeRun(Toggle):
    """
    This controls whether Free Run checkboxes are a part of progression.
    """

    default = 0
    display_name = "Free Run checkboxes are progression"


class EnergyLink(Toggle):
    """
    This enables or disables EnergyLink features. This means that collected patches will send energy
    to the collective energy pool of the Multiworld. You can spend some of this energy to get specific patches
    or other items immediately.
    """

    default = 0
    display_name = "Energy Link"


@dataclass
class KAROptions(PerGameCommonOptions, DeathLinkMixin):
    """
    A data class that encapsulates all configuration options for Kirby Air Ride.
    """

    goal: Goal
    traps_enabled: TrapsEnabled
    trap_chance: TrapChance
    effect_items_enabled: EffectItemsEnabled
    checklist_amount: CheckListAmount
    checkbox_reward_items: CheckboxRewardsItems
    progression_high_effort: ProgressionHighEffort
    progression_multiplayer: ProgressionMultiPlayer
    permanent_patches: PermanentPatches
    permanent_patch_progression: PermanentPatchProgression
    free_run_progression: ProgressionFreeRun
    energy_link: EnergyLink

    def get_output_dict(self) -> dict[str, Any]:
        """
        Returns a dictionary of option name to value to be placed in
        the output APKAR file.

        :return: Dictionary of option name to value for the output file.
        """

        # Note: these options' values must be able to be passed through
        # `yaml.safe_dump`.
        return self.as_dict(
            "goal",
            "traps_enabled",
            "trap_chance",
            "effect_items_enabled",
            "checklist_amount",
            "checkbox_reward_items",
            "progression_high_effort",
            "progression_multiplayer",
            "permanent_patches",
            "permanent_patch_progression",
            "free_run_progression",
            "death_link",
            "energy_link",
        )


kar_option_groups = [
    OptionGroup(
        "Progression Options",
        [
            ProgressionHighEffort,
            ProgressionFreeRun,
            ProgressionMultiPlayer,
            PermanentPatchProgression,
        ],
    ),
    OptionGroup(
        "Items Options",
        [
            TrapsEnabled,
            TrapChance,
            EffectItemsEnabled,
            CheckboxRewardsItems,
            PermanentPatches,
        ],
    ),
]
