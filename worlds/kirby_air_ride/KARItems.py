from enum import StrEnum
from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .KARData import (
    CheckboxFillerType,
    EffectType,
    PatchCapIncreaseType,
    PatchType,
    ProgressiveStadiumUnlockType,
    VictoryEventType,
)


class KARItemType(StrEnum):
    PATCH = "Patch"
    EFFECT = "Effect"
    CHECKBOX_FILLER = "Checkbox Filler"
    PROGRESSIVE_STADIUM = "Progressive Stadium"
    PATCH_CAP_INCREASE = "Patch Cap Increase"
    FILLER = "Filler"
    GOAL = "Goal"


class KARItemData(NamedTuple):
    """
    This class represents the data for an item in Kirby Air Ride.

    :param type: The type of the item (e.g., "Patch", "Air Ride Machine").
    :param classification: The item's classification (progression, useful, filler, trap).
    :param code: The unique code identifier for the item.
    :param quantity: The number of this item available.
    """

    type: str
    classification: ItemClassification
    code: int | None
    quantity: int


class KARItem(Item):
    """
    This class represents an item in Kirby Air Ride.

    :param name: The item's name.
    :param player: The ID of the player who owns the item.
    :param data: The data associated with this item.
    """

    game: str = "Kirby Air Ride"
    type: str = ""

    def __init__(
        self,
        name: str,
        player: int,
        data: KARItemData,
    ) -> None:
        super().__init__(
            name,
            data.classification,
            data.code,
            player,
        )

        self.type = data.type


ITEM_TABLE: dict[str, KARItemData] = {
    PatchType.BOOST_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 30, 10),
    PatchType.BOOST_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 31, 10),
    PatchType.TOP_SPEED_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 32, 10),
    PatchType.TOP_SPEED_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 33, 10),
    PatchType.OFFENSE_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 34, 10),
    PatchType.OFFENSE_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 35, 10),
    PatchType.DEFENSE_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 36, 10),
    PatchType.DEFENSE_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 37, 10),
    PatchType.TURN_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 38, 10),
    PatchType.TURN_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 39, 10),
    PatchType.GLIDE_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 40, 10),
    PatchType.GLIDE_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 41, 10),
    PatchType.CHARGE_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 42, 10),
    PatchType.CHARGE_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 43, 10),
    PatchType.WEIGHT_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 44, 10),
    PatchType.WEIGHT_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 45, 10),
    PatchType.HP_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 46, 10),
    PatchType.HP_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 47, 10),
    PatchType.ALL_UP.value: KARItemData(KARItemType.PATCH.value, ItemClassification.useful, 48, 5),
    PatchType.ALL_DOWN.value: KARItemData(KARItemType.PATCH.value, ItemClassification.trap, 49, 5),
    PatchType.BOOST_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value, ItemClassification.progression, 50, 5
    ),
    PatchType.TOP_SPEED_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        51,
        5,
    ),
    PatchType.OFFENSE_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        52,
        5,
    ),
    PatchType.DEFENSE_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        53,
        5,
    ),
    PatchType.TURN_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        54,
        5,
    ),
    PatchType.GLIDE_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        55,
        5,
    ),
    PatchType.CHARGE_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        56,
        5,
    ),
    PatchType.WEIGHT_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        57,
        5,
    ),
    PatchType.HP_UP_PERMANENT_PLUS_ONE.value: KARItemData(
        KARItemType.PATCH.value,
        ItemClassification.progression,
        58,
        5,
    ),
    EffectType.ONE_HP.value: KARItemData(KARItemType.EFFECT.value, ItemClassification.trap, 59, 10),
    EffectType.FULL_HEAL.value: KARItemData(KARItemType.EFFECT.value, ItemClassification.filler, 60, 10),
    KARItemType.FILLER.value: KARItemData(KARItemType.FILLER.value, ItemClassification.filler, 61, 10),
    CheckboxFillerType.CITY_TRIAL_CHECKBOX_FILLER.value: KARItemData(
        KARItemType.CHECKBOX_FILLER.value,
        ItemClassification.progression,
        62,
        10,
    ),
    CheckboxFillerType.AIR_RIDE_CHECKBOX_FILLER.value: KARItemData(
        KARItemType.CHECKBOX_FILLER.value,
        ItemClassification.progression,
        63,
        10,
    ),
    CheckboxFillerType.TOP_RIDE_CHECKBOX_FILLER.value: KARItemData(
        KARItemType.CHECKBOX_FILLER.value,
        ItemClassification.progression,
        64,
        10,
    ),
    PatchCapIncreaseType.ALL_CAP_INCREASE.value: KARItemData(
        KARItemType.PATCH_CAP_INCREASE.value,
        ItemClassification.progression,
        65,
        5,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_1.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        66,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_2.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        67,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_3.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        68,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_4.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        69,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_HIGH_JUMP.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        70,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_TARGET_FLIGHT.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        71,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_AIR_GLIDER.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        72,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_1.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        73,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_2.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        74,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_3.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        75,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_4.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        76,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_5.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        77,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_KIRBY_MELEE_1.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        78,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_KIRBY_MELEE_2.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        79,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_1.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        80,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_2.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        81,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_3.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        82,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_4.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        83,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_5.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        84,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_6.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        85,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_7.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        86,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_8.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        87,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_9.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        88,
        1,
    ),
    ProgressiveStadiumUnlockType.STADIUM_VS_KING_DEDEDE.value: KARItemData(
        KARItemType.PROGRESSIVE_STADIUM.value,
        ItemClassification.progression,
        89,
        1,
    ),
    # Event items (for goal completion)
    VictoryEventType.CITY_TRIAL_VICTORY.value: KARItemData(KARItemType.GOAL, ItemClassification.progression, None, 1),
    VictoryEventType.AIR_RIDE_VICTORY.value: KARItemData(KARItemType.GOAL, ItemClassification.progression, None, 1),
    VictoryEventType.TOP_RIDE_VICTORY.value: KARItemData(KARItemType.GOAL, ItemClassification.progression, None, 1),
}

item_name_groups = {
    "Effects": {
        EffectType.ONE_HP.value,
        EffectType.FULL_HEAL.value,
    },
    "Patches": {
        PatchType.BOOST_UP.value,
        PatchType.BOOST_DOWN.value,
        PatchType.TOP_SPEED_UP.value,
        PatchType.TOP_SPEED_DOWN.value,
        PatchType.OFFENSE_UP.value,
        PatchType.OFFENSE_DOWN.value,
        PatchType.DEFENSE_UP.value,
        PatchType.DEFENSE_DOWN.value,
        PatchType.TURN_UP.value,
        PatchType.TURN_DOWN.value,
        PatchType.GLIDE_UP.value,
        PatchType.GLIDE_DOWN.value,
        PatchType.CHARGE_UP.value,
        PatchType.CHARGE_DOWN.value,
        PatchType.WEIGHT_UP.value,
        PatchType.WEIGHT_DOWN.value,
        PatchType.HP_UP.value,
        PatchType.HP_DOWN.value,
        PatchType.ALL_UP.value,
        PatchType.ALL_DOWN.value,
        PatchType.BOOST_UP_PERMANENT_PLUS_ONE.value,
        PatchType.TOP_SPEED_UP_PERMANENT_PLUS_ONE.value,
        PatchType.OFFENSE_UP_PERMANENT_PLUS_ONE.value,
        PatchType.DEFENSE_UP_PERMANENT_PLUS_ONE.value,
        PatchType.TURN_UP_PERMANENT_PLUS_ONE.value,
        PatchType.GLIDE_UP_PERMANENT_PLUS_ONE.value,
        PatchType.CHARGE_UP_PERMANENT_PLUS_ONE.value,
        PatchType.WEIGHT_UP_PERMANENT_PLUS_ONE.value,
        PatchType.HP_UP_PERMANENT_PLUS_ONE.value,
    },
    "Patch Cap Increases": {
        PatchCapIncreaseType.ALL_CAP_INCREASE.value,
    },
    "Progressive Stadium Unlocks": {
        ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_1.value,
        ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_2.value,
        ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_3.value,
        ProgressiveStadiumUnlockType.STADIUM_DRAG_RACE_4.value,
        ProgressiveStadiumUnlockType.STADIUM_HIGH_JUMP.value,
        ProgressiveStadiumUnlockType.STADIUM_TARGET_FLIGHT.value,
        ProgressiveStadiumUnlockType.STADIUM_AIR_GLIDER.value,
        ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_1.value,
        ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_2.value,
        ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_3.value,
        ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_4.value,
        ProgressiveStadiumUnlockType.STADIUM_DESTRUCTION_DERBY_5.value,
        ProgressiveStadiumUnlockType.STADIUM_KIRBY_MELEE_1.value,
        ProgressiveStadiumUnlockType.STADIUM_KIRBY_MELEE_2.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_1.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_2.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_3.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_4.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_5.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_6.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_7.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_8.value,
        ProgressiveStadiumUnlockType.STADIUM_SINGLE_RACE_9.value,
        ProgressiveStadiumUnlockType.STADIUM_VS_KING_DEDEDE.value,
    },
}
