from enum import IntEnum, StrEnum
from typing import NamedTuple


class MemoryAddress(IntEnum):
    # Player 1 stat patch addresses
    # Number of patches for player 1 is stored at these addresses. Values start at -2 float except for HP, which starts at 0
    PLAYER_1_STAT_BOOST_PATCH_AMOUNT = 0x81578630
    PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT = 0x81578634
    PLAYER_1_STAT_TURN_PATCH_AMOUNT = 0x81578638
    PLAYER_1_STAT_CHARGE_PATCH_AMOUNT = 0x8157863C
    PLAYER_1_STAT_GLIDE_PATCH_AMOUNT = 0x81578640
    PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT = 0x8157862C
    PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT = 0x81578644
    PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT = 0x81578648
    PLAYER_1_STAT_HP_PATCH_AMOUNT = 0x8157864C

    # this address holds a pointer to a value that then needs offsets applied to get to the relevant machine data
    PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS = 0x8055AA30
    # TODO: find a true pointer or address to the current machine health. This address currently only works for some vehicles or
    # some of the time
    # current machine health float value from initially 0-100, that gets scaled by heart patches to be over 100
    PLAYER_1_CURRENT_MACHINE_HP_OFFSET = 0xA78

    # This address is used to check the player's health for DeathLink.
    # this is a float value from initially 0-100, that gets scaled by heart patches to be over 100.
    # always player HP, always reflects the PLAYER_1_CURRENT_MACHINE_HP_ADDRESS
    # maybe read only? is overwritten every frame but can still use to check actual current player HP
    # is 0 for the entire time the player is off of a machine
    PLAYER_1_CURRENT_HP_ADDRESS = 0x8055AA24
    # max health of the player. overwritten every frame, so effectively read-only. float value.
    PLAYER_1_CURRENT_MAX_HP_ADDRESS = 0x8055AA28

    # number of things destroyed:
    # trees, rocks, coral, houses, star pole, volcano entrances, underground walls
    # Byte value. Starts at 00. Reset only when entering City Trial.
    PLAYER_1_DESTRUCTION_COUNT_ADDRESS = 0x8055B2A3

    # number of total laps in the current Air Ride course.
    # Byte value. Initialized as 1, then 0 when choosing courses, then the value of laps for the course.
    PLAYER_1_AIR_RIDE_TOTAL_LAP_COUNT_ADDRESS = 0x80536472

    # Address that holds the currently selected menu
    # This address is used to check the stage name to verify that the player is in-game before sending items.
    # 00 = Air Ride, 01 = Top Ride, 02 = City Trial, 03 = Options, 04 = LAN
    MENU_STAGE_ID_ADDR = 0x80535A0C

    # the current stage the player is in
    # this is a pointer to a 4 byte word. an offset of 4 needs to be applied to get to the address of the current stage.
    # before main menu: very high positive or negative numbers, jumping around
    # on main menu: 22
    # after main menu but not in a stage: uninitialized
    # after exiting a stage: 0, but can randomly be high positive or negative numbers at any time
    CURR_STAGE_ID_ADDR = 0x805DD6CC


class MenuSelectionID(IntEnum):
    AIR_RIDE = 0
    TOP_RIDE = 1
    CITY_TRIAL = 2
    OPTIONS = 3
    LAN = 4


class StageID(IntEnum):
    MAIN_MENU = 22
    CITY_TRIAL = 9
    STADIUM_DRAG_RACE_1 = 13
    STADIUM_DRAG_RACE_2 = 11
    STADIUM_DRAG_RACE_3 = 10
    STADIUM_DRAG_RACE_4 = 12
    STADIUM_HIGH_JUMP = 18
    STADIUM_TARGET_FLIGHT = 19
    STADIUM_AIR_GLIDER = 20
    STADIUM_DESTRUCTION_DERBY_1 = 15
    STADIUM_DESTRUCTION_DERBY_2 = 16
    STADIUM_DESTRUCTION_DERBY_3 = 21
    # STADIUM_DESTRUCTION_DERBY_4 = 9 # conflicts with City Trial
    # STADIUM_DESTRUCTION_DERBY_5 = 9 # conflicts with City Trial
    STADIUM_KIRBY_MELEE_1 = 14
    STADIUM_KIRBY_MELEE_2 = 17
    STADIUM_VS_KING_DEDEDE = 15
    # FANTASY_MEADOWS = 0 # indistinguishable
    CELESTIAL_VALLEY = 4
    SKY_SANDS = 2
    FROZEN_HILLSIDE = 8
    MAGMA_FLOWS = 1
    BEANSTALK_PARK = 7
    MACHINE_PASSAGE = 5
    CHECKER_KNIGHTS = 3
    NEBULA_BELT = 6


class StageName(StrEnum):
    MAIN_MENU = "Main Menu"
    CITY_TRIAL = "City Trial"
    STADIUM_DRAG_RACE_1 = "Stadium: DRAG RACE 1"
    STADIUM_DRAG_RACE_2 = "Stadium: DRAG RACE 2"
    STADIUM_DRAG_RACE_3 = "Stadium: DRAG RACE 3"
    STADIUM_DRAG_RACE_4 = "Stadium: DRAG RACE 4"
    STADIUM_HIGH_JUMP = "Stadium: HIGH JUMP"
    STADIUM_TARGET_FLIGHT = "Stadium: TARGET FLIGHT"
    STADIUM_AIR_GLIDER = "Stadium: AIR GLIDER"
    STADIUM_DESTRUCTION_DERBY_1 = "Stadium: DESTRUCTION DERBY 1"
    STADIUM_DESTRUCTION_DERBY_2 = "Stadium: DESTRUCTION DERBY 2"
    STADIUM_DESTRUCTION_DERBY_3 = "Stadium: DESTRUCTION DERBY 3"
    STADIUM_KIRBY_MELEE_1 = "Stadium: KIRBY MELEE 1"
    STADIUM_KIRBY_MELEE_2 = "Stadium: KIRBY MELEE 2"
    STADIUM_VS_KING_DEDEDE = "Stadium: VS. KING DEDEDE"
    CELESTIAL_VALLEY = "CELESTIAL VALLEY"
    SKY_SANDS = "SKY SANDS"
    FROZEN_HILLSIDE = "FROZEN HILLSIDE"
    MAGMA_FLOWS = "MAGMA FLOWS"
    BEANSTALK_PARK = "BEANSTALK PARK"
    MACHINE_PASSAGE = "MACHINE PASSAGE"
    CHECKER_KNIGHTS = "CHECKER KNIGHTS"
    NEBULA_BELT = "NEBULA BELT"


class PatchType(StrEnum):
    TURN_UP = "Turn Up"
    TURN_UP_PERMANENT_PLUS_ONE = "Turn Up Permanent +1"
    TURN_DOWN = "Turn Down"
    BOOST_UP = "Boost Up"
    BOOST_UP_PERMANENT_PLUS_ONE = "Boost Up Permanent +1"
    BOOST_DOWN = "Boost Down"
    CHARGE_UP = "Charge Up"
    CHARGE_UP_PERMANENT_PLUS_ONE = "Charge Up Permanent +1"
    CHARGE_DOWN = "Charge Down"
    DEFENSE_UP = "Defense Up"
    DEFENSE_UP_PERMANENT_PLUS_ONE = "Defense Up Permanent +1"
    DEFENSE_DOWN = "Defense Down"
    GLIDE_UP = "Glide Up"
    GLIDE_UP_PERMANENT_PLUS_ONE = "Glide Up Permanent +1"
    GLIDE_DOWN = "Glide Down"
    HP_UP = "HP Up"
    HP_UP_PERMANENT_PLUS_ONE = "HP Up Permanent +1"
    HP_DOWN = "HP Down"
    WEIGHT_UP = "Weight Up"
    WEIGHT_UP_PERMANENT_PLUS_ONE = "Weight Up Permanent +1"
    WEIGHT_DOWN = "Weight Down"
    OFFENSE_UP = "Offense Up"
    OFFENSE_UP_PERMANENT_PLUS_ONE = "Offense Up Permanent +1"
    OFFENSE_DOWN = "Offense Down"
    TOP_SPEED_UP = "Top Speed Up"
    TOP_SPEED_UP_PERMANENT_PLUS_ONE = "Top Speed Up Permanent +1"
    TOP_SPEED_DOWN = "Top Speed Down"
    ALL_UP = "All Up"
    ALL_DOWN = "All Down"


def get_patch_type_from_item_name(item_name: str | None):
    for patch_type in PatchType:
        if patch_type.value == item_name:
            return patch_type
    return None


class EffectType(StrEnum):
    ONE_HP = "1 HP"
    FULL_HEAL = "Full Heal"


def get_effect_type_from_item_name(item_name: str | None):
    for effect_type in EffectType:
        if effect_type.value == item_name:
            return effect_type
    return None


class Stage(NamedTuple):
    name: StageName
    menu_selection: MenuSelectionID
    stage_id: StageID


class Patch(NamedTuple):
    type: PatchType
    memory_address: MemoryAddress


PATCH_MAP: dict[PatchType, Patch] = {
    PatchType.TURN_UP: Patch(PatchType.TURN_UP, MemoryAddress.PLAYER_1_STAT_TURN_PATCH_AMOUNT),
    PatchType.BOOST_UP: Patch(PatchType.BOOST_UP, MemoryAddress.PLAYER_1_STAT_BOOST_PATCH_AMOUNT),
    PatchType.CHARGE_UP: Patch(PatchType.CHARGE_UP, MemoryAddress.PLAYER_1_STAT_CHARGE_PATCH_AMOUNT),
    PatchType.DEFENSE_UP: Patch(PatchType.DEFENSE_UP, MemoryAddress.PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT),
    PatchType.GLIDE_UP: Patch(PatchType.GLIDE_UP, MemoryAddress.PLAYER_1_STAT_GLIDE_PATCH_AMOUNT),
    PatchType.HP_UP: Patch(PatchType.HP_UP, MemoryAddress.PLAYER_1_STAT_HP_PATCH_AMOUNT),
    PatchType.WEIGHT_UP: Patch(PatchType.WEIGHT_UP, MemoryAddress.PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT),
    PatchType.OFFENSE_UP: Patch(PatchType.OFFENSE_UP, MemoryAddress.PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT),
    PatchType.TOP_SPEED_UP: Patch(PatchType.TOP_SPEED_UP, MemoryAddress.PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT),
    PatchType.TURN_DOWN: Patch(PatchType.TURN_DOWN, MemoryAddress.PLAYER_1_STAT_TURN_PATCH_AMOUNT),
    PatchType.BOOST_DOWN: Patch(PatchType.BOOST_DOWN, MemoryAddress.PLAYER_1_STAT_BOOST_PATCH_AMOUNT),
    PatchType.CHARGE_DOWN: Patch(PatchType.CHARGE_DOWN, MemoryAddress.PLAYER_1_STAT_CHARGE_PATCH_AMOUNT),
    PatchType.DEFENSE_DOWN: Patch(PatchType.DEFENSE_DOWN, MemoryAddress.PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT),
    PatchType.GLIDE_DOWN: Patch(PatchType.GLIDE_DOWN, MemoryAddress.PLAYER_1_STAT_GLIDE_PATCH_AMOUNT),
    PatchType.HP_DOWN: Patch(PatchType.HP_DOWN, MemoryAddress.PLAYER_1_STAT_HP_PATCH_AMOUNT),
    PatchType.WEIGHT_DOWN: Patch(PatchType.WEIGHT_DOWN, MemoryAddress.PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT),
    PatchType.OFFENSE_DOWN: Patch(PatchType.OFFENSE_DOWN, MemoryAddress.PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT),
    PatchType.TOP_SPEED_DOWN: Patch(PatchType.TOP_SPEED_DOWN, MemoryAddress.PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT),
    PatchType.TURN_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.TURN_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_TURN_PATCH_AMOUNT
    ),
    PatchType.BOOST_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.BOOST_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_BOOST_PATCH_AMOUNT
    ),
    PatchType.CHARGE_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.CHARGE_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_CHARGE_PATCH_AMOUNT
    ),
    PatchType.DEFENSE_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.DEFENSE_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_DEFENSE_PATCH_AMOUNT
    ),
    PatchType.GLIDE_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.GLIDE_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_GLIDE_PATCH_AMOUNT
    ),
    PatchType.HP_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.HP_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_HP_PATCH_AMOUNT
    ),
    PatchType.WEIGHT_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.WEIGHT_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_WEIGHT_PATCH_AMOUNT
    ),
    PatchType.OFFENSE_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.OFFENSE_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_OFFENSE_PATCH_AMOUNT
    ),
    PatchType.TOP_SPEED_UP_PERMANENT_PLUS_ONE: Patch(
        PatchType.TOP_SPEED_UP_PERMANENT_PLUS_ONE, MemoryAddress.PLAYER_1_STAT_TOP_SPEED_PATCH_AMOUNT
    ),
}

STAGE_MAP: dict[StageName, Stage] = {
    StageName.CITY_TRIAL: Stage(StageName.CITY_TRIAL, MenuSelectionID.CITY_TRIAL, StageID.CITY_TRIAL),
    StageName.STADIUM_DRAG_RACE_1: Stage(
        StageName.STADIUM_DRAG_RACE_1, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DRAG_RACE_1
    ),
    StageName.STADIUM_DRAG_RACE_2: Stage(
        StageName.STADIUM_DRAG_RACE_2, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DRAG_RACE_2
    ),
    StageName.STADIUM_DRAG_RACE_3: Stage(
        StageName.STADIUM_DRAG_RACE_3, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DRAG_RACE_3
    ),
    StageName.STADIUM_DRAG_RACE_4: Stage(
        StageName.STADIUM_DRAG_RACE_4, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DRAG_RACE_4
    ),
    StageName.STADIUM_HIGH_JUMP: Stage(
        StageName.STADIUM_HIGH_JUMP, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_HIGH_JUMP
    ),
    StageName.STADIUM_TARGET_FLIGHT: Stage(
        StageName.STADIUM_TARGET_FLIGHT, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_TARGET_FLIGHT
    ),
    StageName.STADIUM_AIR_GLIDER: Stage(
        StageName.STADIUM_AIR_GLIDER, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_AIR_GLIDER
    ),
    StageName.STADIUM_DESTRUCTION_DERBY_1: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_1, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DESTRUCTION_DERBY_1
    ),
    StageName.STADIUM_DESTRUCTION_DERBY_2: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_2, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DESTRUCTION_DERBY_2
    ),
    StageName.STADIUM_DESTRUCTION_DERBY_3: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_3, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_DESTRUCTION_DERBY_3
    ),
    StageName.STADIUM_KIRBY_MELEE_1: Stage(
        StageName.STADIUM_KIRBY_MELEE_1, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_KIRBY_MELEE_1
    ),
    StageName.STADIUM_KIRBY_MELEE_2: Stage(
        StageName.STADIUM_KIRBY_MELEE_2, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_KIRBY_MELEE_2
    ),
    StageName.STADIUM_VS_KING_DEDEDE: Stage(
        StageName.STADIUM_VS_KING_DEDEDE, MenuSelectionID.CITY_TRIAL, StageID.STADIUM_VS_KING_DEDEDE
    ),
    StageName.CELESTIAL_VALLEY: Stage(StageName.CELESTIAL_VALLEY, MenuSelectionID.AIR_RIDE, StageID.CELESTIAL_VALLEY),
    StageName.SKY_SANDS: Stage(StageName.SKY_SANDS, MenuSelectionID.AIR_RIDE, StageID.SKY_SANDS),
    StageName.FROZEN_HILLSIDE: Stage(StageName.FROZEN_HILLSIDE, MenuSelectionID.AIR_RIDE, StageID.FROZEN_HILLSIDE),
    StageName.MAGMA_FLOWS: Stage(StageName.MAGMA_FLOWS, MenuSelectionID.AIR_RIDE, StageID.MAGMA_FLOWS),
    StageName.BEANSTALK_PARK: Stage(StageName.BEANSTALK_PARK, MenuSelectionID.AIR_RIDE, StageID.BEANSTALK_PARK),
    StageName.MACHINE_PASSAGE: Stage(StageName.MACHINE_PASSAGE, MenuSelectionID.AIR_RIDE, StageID.MACHINE_PASSAGE),
    StageName.CHECKER_KNIGHTS: Stage(StageName.CHECKER_KNIGHTS, MenuSelectionID.AIR_RIDE, StageID.CHECKER_KNIGHTS),
    StageName.NEBULA_BELT: Stage(StageName.NEBULA_BELT, MenuSelectionID.AIR_RIDE, StageID.NEBULA_BELT),
}
