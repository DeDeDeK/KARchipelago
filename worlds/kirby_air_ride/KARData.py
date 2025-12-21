from enum import IntEnum, IntFlag, StrEnum
from typing import NamedTuple


class MemoryAddress(IntEnum):
    BASE_MEMORY_ADDRESS = 0x80000000

    # this address holds a pointer to a value that then needs offsets applied to get to the relevant machine data
    # TODO: find a true pointer or address to the current machine health. This address currently only works for some
    # machines/some of the time
    PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS = 0x8055AA30
    # current machine health float value from initially 0-100, that gets scaled by heart patches to be over 100
    PLAYER_1_CURRENT_MACHINE_HP_OFFSET = 0xA78

    # Player 1 stat patch offsets. These are offsets from the PLAYER_1_CURRENT_MACHINE_POINTER_ADDRESS.
    # Float values. Values start at -2 except for HP, which starts at 0
    PLAYER_1_STAT_WEIGHT_PATCH_OFFSET = 0x9AC
    PLAYER_1_STAT_BOOST_PATCH_OFFSET = 0x9B0
    PLAYER_1_STAT_TOP_SPEED_PATCH_OFFSET = 0x9B4
    PLAYER_1_STAT_TURN_PATCH_OFFSET = 0x9B8
    PLAYER_1_STAT_CHARGE_PATCH_OFFSET = 0x9BC
    PLAYER_1_STAT_GLIDE_PATCH_OFFSET = 0x9C0
    PLAYER_1_STAT_OFFENSE_PATCH_OFFSET = 0x9C4
    PLAYER_1_STAT_DEFENSE_PATCH_OFFSET = 0x9C8
    PLAYER_1_STAT_HP_PATCH_OFFSET = 0x9CC

    # This address is used to check the player's health for DeathLink.
    # this is a float value from initially 0-100, that gets scaled by heart patches to be over 100.
    # always player HP, always reflects the PLAYER_1_CURRENT_MACHINE_HP_ADDRESS
    # this is overwritten by the game every frame but can still use to check actual current player HP
    # is 0 for the entire time the player is off of a machine
    PLAYER_1_CURRENT_HP_ADDRESS = 0x8055AA24
    # max health of the player. overwritten every frame, so effectively read-only. float value.
    PLAYER_1_CURRENT_MAX_HP_ADDRESS = 0x8055AA28

    # number of things destroyed in city trial:
    # trees, rocks, coral, houses, star pole, volcano entrances, underground walls
    # Byte value. Starts at 00. Reset only when entering City Trial.
    PLAYER_1_DESTRUCTION_COUNT_ADDRESS = 0x8055B2A3

    # number of total laps in the current Air Ride course.
    # Byte value. Initialized as 1, then 0 when choosing courses, then the value of laps for the course.
    PLAYER_1_AIR_RIDE_TOTAL_LAP_COUNT_ADDRESS = 0x80536472

    # Address that holds the currently selected menu item. This is set persistently once a menu selection
    # is chosen, and only changes once the player is back to the main menu.
    # This is a byte value.
    # This address is used to check the stage type to verify that the player is in-game before sending items.
    # 00 = Air Ride, 01 = Top Ride, 02 = City Trial, 03 = Options, 04 = LAN
    MENU_STAGE_ID_ADDR = 0x80535A0C
    # the submenu within the current menu selection "air ride -> start game, free run, etc." byte value.
    # persistent once selected, even in-game. reset once the menu has been backed out of
    # 00 -> 0X
    SUB_MENU_STAGE_ID_ADDR = 0x80535A0D
    # sub-sub menu selection. byte value 00 -> 0X
    # persistent once selected, even in-game. reset once the menu has been backed out of
    # ONLY RELIABLE IF SUBMENU_FLAG is ON
    SUB_SUB_MENU_STAGE_ID_ADDR = 0x80535A0E

    # byte value. this is 0 when there are no simple submenus for the current active selection. this 1 when there are
    # simple submenus active for the current selection. For example, air ride and top ride free run selections have
    # 2 more options for time attack and free run. This is 1 for those. Any "Records" menu has submenus as well.
    # This is an easy way to differentiate if the value we read from sub_sub_menu_stage_id_addr is 0 because the
    # first sub sub menu item was selected, vs. it being 0 because that's it's default state.
    SUBMENU_FLAG = 0x80535A0F

    # the current stage the player is in.
    # this is a pointer to a 4 byte word. an offset of 4 needs to be applied to get to the address of the current stage.
    # before main menu: very high positive or negative numbers, jumping around
    # on main menu: 22
    # after main menu but not in a stage: uninitialized
    # after exiting a stage: 0, but can randomly be high positive or negative numbers at any time
    CURR_STAGE_ID_ADDR = 0x805DD6CC

    # The starting addresses for each checklist.
    CITY_TRIAL_BASE_CHECKLIST_ADDRESS = 0x805369FC
    AIR_RIDE_BASE_CHECKLIST_ADDRESS = 0x805367BC
    TOP_RIDE_BASE_CHECKLIST_ADDRESS = 0x805368D4

    # number of checklist box fillers for city trial. this is a byte value. this should be a positive integer > 0.
    # can set to any number at any time and that will be the number the player has. unlocking a filler through a
    # checklist box will only go to a maximum of 5, but this can go higher.
    CITY_TRIAL_CHECKLIST_BOX_FILLER_NUM = 0x80536982
    # the length of the list of checkbox fillers on the side of the checklist. this is a byte value. this should be
    # an integer between 0 and 5, since it will only show 5 max. it does not matter if this is below the value of
    # the number of fillers available to the player - they can continue to use them as long as this is at least 1.
    # setting this to 0 will disable the use of fillers, as there will be no box to select.
    CITY_TRIAL_CHECKLIST_BOX_FILLER_LIST_LENGTH = 0x80536983
    AIR_RIDE_CHECKLIST_BOX_FILLER_NUM = 0x80536742
    AIR_RIDE_CHECKLIST_BOX_FILLER_LIST_LENGTH = 0x80536743
    TOP_RIDE_CHECKLIST_BOX_FILLER_NUM = 0x8053685A
    TOP_RIDE_CHECKLIST_BOX_FILLER_LIST_LENGTH = 0x8053685B

    # this is an address that starts at the last 3 bytes of a 4 byte word. for this address,
    # we treat each byte as binary, and each bit is a stadium unlock. 0 = locked, 1 = unlocked.
    # enumerating which bit unlocks which stadiums:
    # byte 1 (starting at most significant bit):
    # 1: vs. king dedede (stadium 24)
    # 2: single race 9 (stadium 23)
    # 3: single race 8 (stadium 22)
    # 4: single race 7 (stadium 21)
    # 5: single race 6 (stadium 20)
    # 6: single race 5 (stadium 19)
    # 7: single race 4 (stadium 18)
    # 8: single race 3 (stadium 17)
    # byte 2 (starting at most significant bit):
    # 1: single race 2 (stadium 16)
    # 2: single race 1 (stadium 15)
    # 3: destruction derby 5 (stadium 14)
    # 4: destruction derby 4 (stadium 13)
    # 5: destruction derby 3 (stadium 12)
    # 6: destruction derby 2 (stadium 11)
    # 7: destruction derby 1 (stadium 10)
    # 8: kirby melee 2 (stadium 9)
    # byte 3 (starting at most significant bit):
    # 1: kirby melee 1 (stadium 8)
    # 2: high jump (stadium 7)
    # 3: target flight (stadium 6)
    # 4: air glider (stadium 5)
    # 5: drag race 4 (stadium 4)
    # 6: drag race 3 (stadium 3)
    # 7: drag race 2 (stadium 2)
    # 8: drag race 1 (stadium 1)
    CITY_TRIAL_UNLOCKED_STADIUMS_ADDRESS = 0x80536EE9
    # the same as above, but for each bit, whether it says "NEW" or not next to the stadium
    CITY_TRIAL_UNLOCKED_STADIUMS_NEW_LABEL_ADDRESS = 0x80536EED

    # this address is the decimal number of the stadium event, from 0-23, which will occur after City Trial.
    # this is the stadium number in the list -1.
    # this can be set to a negative value at the beginning of the city trial, which (for some values) selects a stage
    # and prevents it from actually being unlocked after the stadium is finished. In this way, we can
    # gate stadiums by always selecting one that's already been unlocked or in the case that none have been unlocked,
    # select the same one each time until more are unlocked.
    CITY_TRIAL_STADIUM_EVENT_ADDRESS = 0x80535F85
    # -1: sky sands race 1 lap
    # -2: fantasy meadows race 1 lap
    # -3: sky sands race 1 lap
    # -4: fantasy meadows race 1 lap
    # -5: sky sands race 1 lap
    # -6: fantasy meadows race 1 lap
    # -7: beanstalk park race 1 lap
    # -8: fantasy meadows race 1 lap
    # -9: beanstalk park race 1 lap
    # -10: fantasy meadows race 1 lap
    # -11: drag race 1
    # -12: fantasy meadows race 1 lap
    # -13: drag race 1
    # ...


class CheckboxFlags(IntFlag):
    # 0b00000000 = locked, not visible
    # 0b00000001 = flagged for unlocking
    # 0b00010000 = locked, visible
    # 0b00010001 = visible, flagged for unlocking
    # 0b00000100 = unlocked, green box
    # 0b00001100 = unlocked, red box
    # 0b00011010 = checkbox filler, reward, previously visible
    # 0b00001010 = checkbox filler, reward, not previously visible
    # 0b00010010 = checkbox filler, no reward, previously visible
    # 0b00000010 = checkbox filler, no reward, not previously visible

    # 0b00010000 = visible bit?
    # 0b00001000 = reward/red bit?
    # 0b00000100 = unlocked/green bit?
    # 0b00000010 = checkbox filler/purple bit?
    # 0b00000001 = flagged for unlocking bit?
    VISIBLE = 0b00010000
    REWARD_RED = 0b00001000
    UNLOCKED_GREEN = 0b00000100
    FILLER_PURPLE = 0b00000010
    FLAGGED_FOR_UNLOCK = 0b00000001


def convert_stadium_unlocks_bytes_to_bits(b: bytes) -> list[int]:
    """
    convert the bytes value to a list of integer bits
    b is assumed to be 3 bytes from dolphin_memory_engine.read_bytes
    """
    integer_value = int.from_bytes(b, byteorder="big")
    binary_string = f"{integer_value:024b}"
    return [int(i) for i in binary_string]


def compose_stadium_unlocks_number(bits: list[int]) -> int:
    """
    compose a 24-bit 3-byte hex number to write to memory with dolphin_memory_engine.write_bytes
    bits is a list of 24 bits, least significant last.
    """
    int_val = 0
    for i, bit in enumerate(reversed(bits)):  # process from LSB to MSB
        int_val |= bit << i
    return int_val


class MenuSelectionID(IntEnum):
    AIR_RIDE = 0
    TOP_RIDE = 1
    CITY_TRIAL = 2
    OPTIONS = 3
    LAN = 4


class SubMenuSelectionIDCityTrial(IntEnum):
    START_GAME = 0
    STADIUM = 1
    FREE_RUN = 2
    GAME_SETTINGS = 3
    RECORDS = 4
    HOW_TO_PLAY = 5


class SubSubMenuSelectionIDCityTrial(IntEnum):
    NONE = 0


class SubMenuSelectionIDAirRide(IntEnum):
    START_GAME = 0
    FREE_RUN = 1
    GAME_SETTINGS = 2
    RECORDS = 3
    HOW_TO_PLAY = 4


class SubSubMenuSelectionIDAirRideFreeRun(IntEnum):
    TIME_ATTACK = 0
    FREE_RUN = 1


class SubMenuSelectionIDTopRide(IntEnum):
    START_GAME = 0
    FREE_RUN = 1
    GAME_SETTINGS = 2
    RECORDS = 3
    HOW_TO_PLAY = 4


class SubSubMenuSelectionIDTopRideFreeRun(IntEnum):
    TIME_ATTACK = 0
    FREE_RUN = 1


class SubMenuFlag(IntEnum):
    OFF = 0
    ON = 1


class StageID(IntEnum):
    MAIN_MENU = 22
    CITY_TRIAL = 9
    CITY_TRIAL_FREE_RUN = 9
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
    STADIUM_DESTRUCTION_DERBY_4 = 9
    STADIUM_DESTRUCTION_DERBY_5 = 9
    STADIUM_SINGLE_RACE_9 = 6
    STADIUM_SINGLE_RACE_8 = 3
    STADIUM_SINGLE_RACE_7 = 5
    STADIUM_SINGLE_RACE_6 = 4
    STADIUM_SINGLE_RACE_5 = 7
    STADIUM_SINGLE_RACE_4 = 8
    STADIUM_SINGLE_RACE_3 = 2
    STADIUM_SINGLE_RACE_2 = 1
    STADIUM_SINGLE_RACE_1 = 0
    STADIUM_KIRBY_MELEE_1 = 14
    STADIUM_KIRBY_MELEE_2 = 17
    STADIUM_VS_KING_DEDEDE = 15
    AIR_RIDE_FANTASY_MEADOWS = 0
    AIR_RIDE_CELESTIAL_VALLEY = 4
    AIR_RIDE_SKY_SANDS = 2
    AIR_RIDE_FROZEN_HILLSIDE = 8
    AIR_RIDE_MAGMA_FLOWS = 1
    AIR_RIDE_BEANSTALK_PARK = 7
    AIR_RIDE_MACHINE_PASSAGE = 5
    AIR_RIDE_CHECKER_KNIGHTS = 3
    AIR_RIDE_NEBULA_BELT = 6
    AIR_RIDE_FANTASY_MEADOWS_FREE_RUN = 0
    AIR_RIDE_CELESTIAL_VALLEY_FREE_RUN = 4
    AIR_RIDE_SKY_SANDS_FREE_RUN = 2
    AIR_RIDE_FROZEN_HILLSIDE_FREE_RUN = 8
    AIR_RIDE_MAGMA_FLOWS_FREE_RUN = 1
    AIR_RIDE_BEANSTALK_PARK_FREE_RUN = 7
    AIR_RIDE_MACHINE_PASSAGE_FREE_RUN = 5
    AIR_RIDE_CHECKER_KNIGHTS_FREE_RUN = 3
    AIR_RIDE_NEBULA_BELT_FREE_RUN = 6
    AIR_RIDE_FANTASY_MEADOWS_TIME_ATTACK = 0
    AIR_RIDE_CELESTIAL_VALLEY_TIME_ATTACK = 4
    AIR_RIDE_SKY_SANDS_TIME_ATTACK = 2
    AIR_RIDE_FROZEN_HILLSIDE_TIME_ATTACK = 8
    AIR_RIDE_MAGMA_FLOWS_TIME_ATTACK = 1
    AIR_RIDE_BEANSTALK_PARK_TIME_ATTACK = 7
    AIR_RIDE_MACHINE_PASSAGE_TIME_ATTACK = 5
    AIR_RIDE_CHECKER_KNIGHTS_TIME_ATTACK = 3
    AIR_RIDE_NEBULA_BELT_TIME_ATTACK = 6
    TOP_RIDE_GRASS = 0
    TOP_RIDE_SAND = 0
    TOP_RIDE_SKY = 0
    TOP_RIDE_FIRE = 0
    TOP_RIDE_LIGHT = 0
    TOP_RIDE_WATER = 0
    TOP_RIDE_METAL = 0
    TOP_RIDE_GRASS_FREE_RUN = 0
    TOP_RIDE_SAND_FREE_RUN = 0
    TOP_RIDE_SKY_FREE_RUN = 0
    TOP_RIDE_FIRE_FREE_RUN = 0
    TOP_RIDE_LIGHT_FREE_RUN = 0
    TOP_RIDE_WATER_FREE_RUN = 0
    TOP_RIDE_METAL_FREE_RUN = 0
    TOP_RIDE_GRASS_TIME_ATTACK = 0
    TOP_RIDE_SAND_TIME_ATTACK = 0
    TOP_RIDE_SKY_TIME_ATTACK = 0
    TOP_RIDE_FIRE_TIME_ATTACK = 0
    TOP_RIDE_LIGHT_TIME_ATTACK = 0
    TOP_RIDE_WATER_TIME_ATTACK = 0
    TOP_RIDE_METAL_TIME_ATTACK = 0


class StageName(StrEnum):
    MAIN_MENU = "Main Menu"
    CITY_TRIAL = "City Trial"
    CITY_TRIAL_FREE_RUN = "City Trial (Free Run)"
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
    STADIUM_DESTRUCTION_DERBY_4 = "Stadium: DESTRUCTION DERBY 4"
    STADIUM_DESTRUCTION_DERBY_5 = "Stadium: DESTRUCTION DERBY 5"
    STADIUM_KIRBY_MELEE_1 = "Stadium: KIRBY MELEE 1"
    STADIUM_KIRBY_MELEE_2 = "Stadium: KIRBY MELEE 2"
    STADIUM_SINGLE_RACE_1 = "Stadium: SINGLE RACE 1"
    STADIUM_SINGLE_RACE_2 = "Stadium: SINGLE RACE 2"
    STADIUM_SINGLE_RACE_3 = "Stadium: SINGLE RACE 3"
    STADIUM_SINGLE_RACE_4 = "Stadium: SINGLE RACE 4"
    STADIUM_SINGLE_RACE_5 = "Stadium: SINGLE RACE 5"
    STADIUM_SINGLE_RACE_6 = "Stadium: SINGLE RACE 6"
    STADIUM_SINGLE_RACE_7 = "Stadium: SINGLE RACE 7"
    STADIUM_SINGLE_RACE_8 = "Stadium: SINGLE RACE 8"
    STADIUM_SINGLE_RACE_9 = "Stadium: SINGLE RACE 9"
    STADIUM_VS_KING_DEDEDE = "Stadium: VS. KING DEDEDE"
    AIR_RIDE_FANTASY_MEADOWS = "FANTASY MEADOWS"
    AIR_RIDE_CELESTIAL_VALLEY = "CELESTIAL VALLEY"
    AIR_RIDE_SKY_SANDS = "SKY SANDS"
    AIR_RIDE_FROZEN_HILLSIDE = "FROZEN HILLSIDE"
    AIR_RIDE_MAGMA_FLOWS = "MAGMA FLOWS"
    AIR_RIDE_BEANSTALK_PARK = "BEANSTALK PARK"
    AIR_RIDE_MACHINE_PASSAGE = "MACHINE PASSAGE"
    AIR_RIDE_CHECKER_KNIGHTS = "CHECKER KNIGHTS"
    AIR_RIDE_NEBULA_BELT = "NEBULA BELT"
    AIR_RIDE_FANTASY_MEADOWS_FREE_RUN = "FANTASY MEADOWS (Free Run)"
    AIR_RIDE_CELESTIAL_VALLEY_FREE_RUN = "CELESTIAL VALLEY (Free Run)"
    AIR_RIDE_SKY_SANDS_FREE_RUN = "SKY SANDS (Free Run)"
    AIR_RIDE_FROZEN_HILLSIDE_FREE_RUN = "FROZEN HILLSIDE (Free Run)"
    AIR_RIDE_MAGMA_FLOWS_FREE_RUN = "MAGMA FLOWS (Free Run)"
    AIR_RIDE_BEANSTALK_PARK_FREE_RUN = "BEANSTALK PARK (Free Run)"
    AIR_RIDE_MACHINE_PASSAGE_FREE_RUN = "MACHINE PASSAGE (Free Run)"
    AIR_RIDE_CHECKER_KNIGHTS_FREE_RUN = "CHECKER KNIGHTS (Free Run)"
    AIR_RIDE_NEBULA_BELT_FREE_RUN = "NEBULA BELT (Free Run)"
    AIR_RIDE_FANTASY_MEADOWS_TIME_ATTACK = "FANTASY MEADOWS (Time Attack)"
    AIR_RIDE_CELESTIAL_VALLEY_TIME_ATTACK = "CELESTIAL VALLEY (Time Attack)"
    AIR_RIDE_SKY_SANDS_TIME_ATTACK = "SKY SANDS (Time Attack)"
    AIR_RIDE_FROZEN_HILLSIDE_TIME_ATTACK = "FROZEN HILLSIDE (Time Attack)"
    AIR_RIDE_MAGMA_FLOWS_TIME_ATTACK = "MAGMA FLOWS (Time Attack)"
    AIR_RIDE_BEANSTALK_PARK_TIME_ATTACK = "BEANSTALK PARK (Time Attack)"
    AIR_RIDE_MACHINE_PASSAGE_TIME_ATTACK = "MACHINE PASSAGE (Time Attack)"
    AIR_RIDE_CHECKER_KNIGHTS_TIME_ATTACK = "CHECKER KNIGHTS (Time Attack)"
    AIR_RIDE_NEBULA_BELT_TIME_ATTACK = "NEBULA BELT (Time Attack)"
    TOP_RIDE_GRASS = "Top Ride: GRASS"
    TOP_RIDE_SAND = "Top Ride: SAND"
    TOP_RIDE_SKY = "Top Ride: SKY"
    TOP_RIDE_FIRE = "Top Ride: FIRE"
    TOP_RIDE_LIGHT = "Top Ride: LIGHT"
    TOP_RIDE_WATER = "Top Ride: WATER"
    TOP_RIDE_METAL = "Top Ride: METAL"
    TOP_RIDE_GRASS_FREE_RUN = "Top Ride: GRASS (Free Run)"
    TOP_RIDE_SAND_FREE_RUN = "Top Ride: SAND (Free Run)"
    TOP_RIDE_SKY_FREE_RUN = "Top Ride: SKY (Free Run)"
    TOP_RIDE_FIRE_FREE_RUN = "Top Ride: FIRE (Free Run)"
    TOP_RIDE_LIGHT_FREE_RUN = "Top Ride: LIGHT (Free Run)"
    TOP_RIDE_WATER_FREE_RUN = "Top Ride: WATER (Free Run)"
    TOP_RIDE_METAL_FREE_RUN = "Top Ride: METAL (Free Run)"
    TOP_RIDE_GRASS_TIME_ATTACK = "Top Ride: GRASS (Time Attack)"
    TOP_RIDE_SAND_TIME_ATTACK = "Top Ride: SAND (Time Attack)"
    TOP_RIDE_SKY_TIME_ATTACK = "Top Ride: SKY (Time Attack)"
    TOP_RIDE_FIRE_TIME_ATTACK = "Top Ride: FIRE (Time Attack)"
    TOP_RIDE_LIGHT_TIME_ATTACK = "Top Ride: LIGHT (Time Attack)"
    TOP_RIDE_WATER_TIME_ATTACK = "Top Ride: WATER (Time Attack)"
    TOP_RIDE_METAL_TIME_ATTACK = "Top Ride: METAL (Time Attack)"


class ProgressiveStadiumUnlockType(StrEnum):
    STADIUM_DRAG_RACE_1 = "Unlock Stadium: DRAG RACE 1"
    STADIUM_DRAG_RACE_2 = "Unlock Stadium: DRAG RACE 2"
    STADIUM_DRAG_RACE_3 = "Unlock Stadium: DRAG RACE 3"
    STADIUM_DRAG_RACE_4 = "Unlock Stadium: DRAG RACE 4"
    STADIUM_HIGH_JUMP = "Unlock Stadium: HIGH JUMP"
    STADIUM_TARGET_FLIGHT = "Unlock Stadium: TARGET FLIGHT"
    STADIUM_AIR_GLIDER = "Unlock Stadium: AIR GLIDER"
    STADIUM_DESTRUCTION_DERBY_1 = "Unlock Stadium: DESTRUCTION DERBY 1"
    STADIUM_DESTRUCTION_DERBY_2 = "Unlock Stadium: DESTRUCTION DERBY 2"
    STADIUM_DESTRUCTION_DERBY_3 = "Unlock Stadium: DESTRUCTION DERBY 3"
    STADIUM_DESTRUCTION_DERBY_4 = "Unlock Stadium: DESTRUCTION DERBY 4"
    STADIUM_DESTRUCTION_DERBY_5 = "Unlock Stadium: DESTRUCTION DERBY 5"
    STADIUM_KIRBY_MELEE_1 = "Unlock Stadium: KIRBY MELEE 1"
    STADIUM_KIRBY_MELEE_2 = "Unlock Stadium: KIRBY MELEE 2"
    STADIUM_SINGLE_RACE_1 = "Unlock Stadium: SINGLE RACE 1"
    STADIUM_SINGLE_RACE_2 = "Unlock Stadium: SINGLE RACE 2"
    STADIUM_SINGLE_RACE_3 = "Unlock Stadium: SINGLE RACE 3"
    STADIUM_SINGLE_RACE_4 = "Unlock Stadium: SINGLE RACE 4"
    STADIUM_SINGLE_RACE_5 = "Unlock Stadium: SINGLE RACE 5"
    STADIUM_SINGLE_RACE_6 = "Unlock Stadium: SINGLE RACE 6"
    STADIUM_SINGLE_RACE_7 = "Unlock Stadium: SINGLE RACE 7"
    STADIUM_SINGLE_RACE_8 = "Unlock Stadium: SINGLE RACE 8"
    STADIUM_SINGLE_RACE_9 = "Unlock Stadium: SINGLE RACE 9"
    STADIUM_VS_KING_DEDEDE = "Unlock Stadium: VS. KING DEDEDE"


def get_progressive_stadium_unlock_type_from_item_name(item_name: str) -> ProgressiveStadiumUnlockType | None:
    try:
        return ProgressiveStadiumUnlockType(item_name)
    except ValueError:
        return None


def get_stage_name_from_stadium_unlock_type(stadium: ProgressiveStadiumUnlockType) -> StageName:
    return StageName[stadium.name]


# a tuple of the stadiums, in order from most significant bit to least significant bit in a 24 bit binary number
BIT_POSITION_TO_STADIUM_MAP = (
    StageName.STADIUM_VS_KING_DEDEDE,
    StageName.STADIUM_SINGLE_RACE_9,
    StageName.STADIUM_SINGLE_RACE_8,
    StageName.STADIUM_SINGLE_RACE_7,
    StageName.STADIUM_SINGLE_RACE_6,
    StageName.STADIUM_SINGLE_RACE_5,
    StageName.STADIUM_SINGLE_RACE_4,
    StageName.STADIUM_SINGLE_RACE_3,
    StageName.STADIUM_SINGLE_RACE_2,
    StageName.STADIUM_SINGLE_RACE_1,
    StageName.STADIUM_DESTRUCTION_DERBY_5,
    StageName.STADIUM_DESTRUCTION_DERBY_4,
    StageName.STADIUM_DESTRUCTION_DERBY_3,
    StageName.STADIUM_DESTRUCTION_DERBY_2,
    StageName.STADIUM_DESTRUCTION_DERBY_1,
    StageName.STADIUM_KIRBY_MELEE_2,
    StageName.STADIUM_KIRBY_MELEE_1,
    StageName.STADIUM_HIGH_JUMP,
    StageName.STADIUM_TARGET_FLIGHT,
    StageName.STADIUM_AIR_GLIDER,
    StageName.STADIUM_DRAG_RACE_4,
    StageName.STADIUM_DRAG_RACE_3,
    StageName.STADIUM_DRAG_RACE_2,
    StageName.STADIUM_DRAG_RACE_1,
)


class PatchType(StrEnum):
    # Up types
    TURN_UP = "Turn Up"
    BOOST_UP = "Boost Up"
    CHARGE_UP = "Charge Up"
    DEFENSE_UP = "Defense Up"
    GLIDE_UP = "Glide Up"
    HP_UP = "HP Up"
    WEIGHT_UP = "Weight Up"
    OFFENSE_UP = "Offense Up"
    TOP_SPEED_UP = "Top Speed Up"
    ALL_UP = "All Up"

    # Down types
    TURN_DOWN = "Turn Down"
    BOOST_DOWN = "Boost Down"
    CHARGE_DOWN = "Charge Down"
    DEFENSE_DOWN = "Defense Down"
    GLIDE_DOWN = "Glide Down"
    HP_DOWN = "HP Down"
    WEIGHT_DOWN = "Weight Down"
    OFFENSE_DOWN = "Offense Down"
    TOP_SPEED_DOWN = "Top Speed Down"
    ALL_DOWN = "All Down"

    # Permanent types
    TURN_UP_PERMANENT_PLUS_ONE = "Turn Up Permanent +1"
    BOOST_UP_PERMANENT_PLUS_ONE = "Boost Up Permanent +1"
    CHARGE_UP_PERMANENT_PLUS_ONE = "Charge Up Permanent +1"
    DEFENSE_UP_PERMANENT_PLUS_ONE = "Defense Up Permanent +1"
    GLIDE_UP_PERMANENT_PLUS_ONE = "Glide Up Permanent +1"
    HP_UP_PERMANENT_PLUS_ONE = "HP Up Permanent +1"
    WEIGHT_UP_PERMANENT_PLUS_ONE = "Weight Up Permanent +1"
    OFFENSE_UP_PERMANENT_PLUS_ONE = "Offense Up Permanent +1"
    TOP_SPEED_UP_PERMANENT_PLUS_ONE = "Top Speed Up Permanent +1"


class PatchCapIncreaseType(StrEnum):
    TURN_CAP_INCREASE = "Turn Cap Increase +1"
    BOOST_CAP_INCREASE = "Boost Cap Increase +1"
    CHARGE_CAP_INCREASE = "Charge Cap Increase +1"
    DEFENSE_CAP_INCREASE = "Defense Cap Increase +1"
    GLIDE_CAP_INCREASE = "Glide Cap Increase +1"
    HP_CAP_INCREASE = "HP Cap Increase +1"
    WEIGHT_CAP_INCREASE = "Weight Cap Increase +1"
    OFFENSE_CAP_INCREASE = "Offense Cap Increase +1"
    TOP_SPEED_CAP_INCREASE = "Top Speed Cap Increase +1"
    ALL_CAP_INCREASE = "Patch Cap Increase +1"


def get_patch_cap_increase_type_from_item_name(item_name: str) -> PatchCapIncreaseType | None:
    """Get patch cap increase type from item name using the PatchCapIncreaseType enum."""
    try:
        return PatchCapIncreaseType(item_name)
    except ValueError:
        return None


class PatchConstants:
    """Constants related to patch stat mechanics."""

    MAX_PATCH_CAP = 18  # Maximum cap for most patch stats (HP max is 16)
    MIN_PATCH_CAP = 1  # Minimum starting patch cap
    DEFAULT_PATCH_VALUE = -2  # Starting value for most patches (HP starts at 0)


class StatType(StrEnum):
    """Base stat types that correspond to unique memory addresses."""

    TURN = "Turn"
    BOOST = "Boost"
    CHARGE = "Charge"
    DEFENSE = "Defense"
    GLIDE = "Glide"
    HP = "HP"
    WEIGHT = "Weight"
    OFFENSE = "Offense"
    TOP_SPEED = "Top Speed"


def get_patch_type_from_item_name(item_name: str) -> PatchType | None:
    """Get patch type from item name using the combined PatchType enum."""
    try:
        return PatchType(item_name)
    except ValueError:
        return None


def patch_type_to_stat_type(patch_type: PatchType) -> StatType | None:
    """Convert PatchType to its corresponding StatType"""
    for stat_type in StatType:
        if stat_type.value in patch_type.value:
            return stat_type
    return None


# Mapping from StatType to MemoryAddress for easy lookup
STAT_TO_MEMORY_MAP: dict[StatType, MemoryAddress] = {
    StatType.TURN: MemoryAddress.PLAYER_1_STAT_TURN_PATCH_OFFSET,
    StatType.BOOST: MemoryAddress.PLAYER_1_STAT_BOOST_PATCH_OFFSET,
    StatType.CHARGE: MemoryAddress.PLAYER_1_STAT_CHARGE_PATCH_OFFSET,
    StatType.DEFENSE: MemoryAddress.PLAYER_1_STAT_DEFENSE_PATCH_OFFSET,
    StatType.GLIDE: MemoryAddress.PLAYER_1_STAT_GLIDE_PATCH_OFFSET,
    StatType.HP: MemoryAddress.PLAYER_1_STAT_HP_PATCH_OFFSET,
    StatType.WEIGHT: MemoryAddress.PLAYER_1_STAT_WEIGHT_PATCH_OFFSET,
    StatType.OFFENSE: MemoryAddress.PLAYER_1_STAT_OFFENSE_PATCH_OFFSET,
    StatType.TOP_SPEED: MemoryAddress.PLAYER_1_STAT_TOP_SPEED_PATCH_OFFSET,
}


class CheckboxFillerType(StrEnum):
    CITY_TRIAL_CHECKBOX_FILLER = "Checkbox Filler (City Trial)"
    AIR_RIDE_CHECKBOX_FILLER = "Checkbox Filler (Air Ride)"
    TOP_RIDE_CHECKBOX_FILLER = "Checkbox Filler (Top Ride)"


def get_checkbox_filler_type_from_item_name(item_name: str) -> CheckboxFillerType | None:
    """Get checkbox filler type from item name using the CheckboxFillerType enum."""
    try:
        return CheckboxFillerType(item_name)
    except ValueError:
        return None


class EffectType(StrEnum):
    ONE_HP = "1 HP"
    FULL_HEAL = "Full Heal"


def get_effect_type_from_item_name(item_name: str) -> EffectType | None:
    """Get effect type from item name using the EffectType enum."""
    try:
        return EffectType(item_name)
    except ValueError:
        return None


class VictoryEventType(StrEnum):
    CITY_TRIAL_VICTORY = "City Trial Victory"
    AIR_RIDE_VICTORY = "Air Ride Victory"
    TOP_RIDE_VICTORY = "Top Ride Victory"


class Stage(NamedTuple):
    name: StageName
    menu_selection: MenuSelectionID
    sub_menu_selection: SubMenuSelectionIDCityTrial | SubMenuSelectionIDAirRide | SubMenuSelectionIDTopRide
    sub_sub_menu_selection: (
        SubSubMenuSelectionIDAirRideFreeRun | SubSubMenuSelectionIDTopRideFreeRun | SubSubMenuSelectionIDCityTrial
    )
    submenu_flag: SubMenuFlag
    stage_id: StageID


class Patch(NamedTuple):
    type: PatchType
    memory_address: MemoryAddress


# maps staged to their menu selections and stage IDs, to faciliatate detecting when the player is in a game
STAGE_MAP: dict[StageName, Stage] = {
    StageName.CITY_TRIAL: Stage(
        StageName.CITY_TRIAL,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.CITY_TRIAL,
    ),
    StageName.CITY_TRIAL_FREE_RUN: Stage(
        StageName.CITY_TRIAL_FREE_RUN,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.FREE_RUN,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.CITY_TRIAL_FREE_RUN,
    ),
    StageName.STADIUM_DRAG_RACE_1: Stage(
        StageName.STADIUM_DRAG_RACE_1,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_1,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DRAG_RACE_2: Stage(
        StageName.STADIUM_DRAG_RACE_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_2,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DRAG_RACE_3: Stage(
        StageName.STADIUM_DRAG_RACE_3,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_3,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DRAG_RACE_4: Stage(
        StageName.STADIUM_DRAG_RACE_4,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_4,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_HIGH_JUMP: Stage(
        StageName.STADIUM_HIGH_JUMP,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_HIGH_JUMP,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_TARGET_FLIGHT: Stage(
        StageName.STADIUM_TARGET_FLIGHT,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_TARGET_FLIGHT,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_AIR_GLIDER: Stage(
        StageName.STADIUM_AIR_GLIDER,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_AIR_GLIDER,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DESTRUCTION_DERBY_1: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_1,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_1,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DESTRUCTION_DERBY_2: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_2,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DESTRUCTION_DERBY_3: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_3,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_3,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DESTRUCTION_DERBY_4: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_4,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_4,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DESTRUCTION_DERBY_5: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_5,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_5,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_KIRBY_MELEE_1: Stage(
        StageName.STADIUM_KIRBY_MELEE_1,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_KIRBY_MELEE_1,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_KIRBY_MELEE_2: Stage(
        StageName.STADIUM_KIRBY_MELEE_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_KIRBY_MELEE_2,
    ),  # from city trial menu (stadium after game of city trial)
    # StageName.STADIUM_SINGLE_RACE_1: Stage(
    #     StageName.STADIUM_SINGLE_RACE_1,
    #     MenuSelectionID.CITY_TRIAL,
    #     SubMenuSelectionIDCityTrial.START_GAME,
    #     SubSubMenuSelectionIDCityTrial.NONE,
    #     SubMenuFlag.OFF,
    #     StageID.STADIUM_SINGLE_RACE_1,
    # ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_2: Stage(
        StageName.STADIUM_SINGLE_RACE_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_2,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_3: Stage(
        StageName.STADIUM_SINGLE_RACE_3,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_3,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_4: Stage(
        StageName.STADIUM_SINGLE_RACE_4,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_4,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_5: Stage(
        StageName.STADIUM_SINGLE_RACE_5,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_5,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_6: Stage(
        StageName.STADIUM_SINGLE_RACE_6,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_6,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_7: Stage(
        StageName.STADIUM_SINGLE_RACE_7,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_7,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_8: Stage(
        StageName.STADIUM_SINGLE_RACE_8,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_8,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_SINGLE_RACE_9: Stage(
        StageName.STADIUM_SINGLE_RACE_9,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_9,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_VS_KING_DEDEDE: Stage(
        StageName.STADIUM_VS_KING_DEDEDE,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_VS_KING_DEDEDE,
    ),  # from city trial menu (stadium after game of city trial)
    StageName.STADIUM_DRAG_RACE_1: Stage(
        StageName.STADIUM_DRAG_RACE_1,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_1,
    ),  # from stadium menu
    StageName.STADIUM_DRAG_RACE_2: Stage(
        StageName.STADIUM_DRAG_RACE_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_2,
    ),  # from stadium menu
    StageName.STADIUM_DRAG_RACE_3: Stage(
        StageName.STADIUM_DRAG_RACE_3,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_3,
    ),  # from stadium menu
    StageName.STADIUM_DRAG_RACE_4: Stage(
        StageName.STADIUM_DRAG_RACE_4,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DRAG_RACE_4,
    ),  # from stadium menu
    StageName.STADIUM_HIGH_JUMP: Stage(
        StageName.STADIUM_HIGH_JUMP,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_HIGH_JUMP,
    ),  # from stadium menu
    StageName.STADIUM_TARGET_FLIGHT: Stage(
        StageName.STADIUM_TARGET_FLIGHT,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_TARGET_FLIGHT,
    ),  # from stadium menu
    StageName.STADIUM_AIR_GLIDER: Stage(
        StageName.STADIUM_AIR_GLIDER,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_AIR_GLIDER,
    ),  # from stadium menu
    StageName.STADIUM_DESTRUCTION_DERBY_1: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_1,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_1,
    ),  # from stadium menu
    StageName.STADIUM_DESTRUCTION_DERBY_2: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_2,
    ),  # from stadium menu
    StageName.STADIUM_DESTRUCTION_DERBY_3: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_3,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_3,
    ),  # from stadium menu
    StageName.STADIUM_DESTRUCTION_DERBY_4: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_4,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_4,
    ),  # from stadium menu
    StageName.STADIUM_DESTRUCTION_DERBY_5: Stage(
        StageName.STADIUM_DESTRUCTION_DERBY_5,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_DESTRUCTION_DERBY_5,
    ),  # from stadium menu
    StageName.STADIUM_KIRBY_MELEE_1: Stage(
        StageName.STADIUM_KIRBY_MELEE_1,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_KIRBY_MELEE_1,
    ),  # from stadium menu
    StageName.STADIUM_KIRBY_MELEE_2: Stage(
        StageName.STADIUM_KIRBY_MELEE_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_KIRBY_MELEE_2,
    ),  # from stadium menu
    # StageName.STADIUM_SINGLE_RACE_1: Stage(
    #     StageName.STADIUM_SINGLE_RACE_1,
    #     MenuSelectionID.CITY_TRIAL,
    #     SubMenuSelectionIDCityTrial.STADIUM,
    #     SubSubMenuSelectionIDCityTrial.NONE,
    #     SubMenuFlag.OFF,
    #     StageID.STADIUM_SINGLE_RACE_1,
    # ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_2: Stage(
        StageName.STADIUM_SINGLE_RACE_2,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_2,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_3: Stage(
        StageName.STADIUM_SINGLE_RACE_3,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_3,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_4: Stage(
        StageName.STADIUM_SINGLE_RACE_4,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_4,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_5: Stage(
        StageName.STADIUM_SINGLE_RACE_5,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_5,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_6: Stage(
        StageName.STADIUM_SINGLE_RACE_6,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_6,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_7: Stage(
        StageName.STADIUM_SINGLE_RACE_7,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_7,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_8: Stage(
        StageName.STADIUM_SINGLE_RACE_8,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_8,
    ),  # from stadium menu
    StageName.STADIUM_SINGLE_RACE_9: Stage(
        StageName.STADIUM_SINGLE_RACE_9,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_SINGLE_RACE_9,
    ),  # from stadium menu
    StageName.STADIUM_VS_KING_DEDEDE: Stage(
        StageName.STADIUM_VS_KING_DEDEDE,
        MenuSelectionID.CITY_TRIAL,
        SubMenuSelectionIDCityTrial.STADIUM,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.STADIUM_VS_KING_DEDEDE,
    ),  # from stadium menu
    # StageName.AIR_RIDE_FANTASY_MEADOWS: Stage(
    #     StageName.AIR_RIDE_FANTASY_MEADOWS,
    #     MenuSelectionID.AIR_RIDE,
    #     SubMenuSelectionIDAirRide.START_GAME,
    #     SubSubMenuSelectionIDCityTrial.NONE,
    #     SubMenuFlag.OFF,
    #     StageID.AIR_RIDE_FANTASY_MEADOWS,
    # ),
    StageName.AIR_RIDE_CELESTIAL_VALLEY: Stage(
        StageName.AIR_RIDE_CELESTIAL_VALLEY,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_CELESTIAL_VALLEY,
    ),
    StageName.AIR_RIDE_SKY_SANDS: Stage(
        StageName.AIR_RIDE_SKY_SANDS,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_SKY_SANDS,
    ),
    StageName.AIR_RIDE_FROZEN_HILLSIDE: Stage(
        StageName.AIR_RIDE_FROZEN_HILLSIDE,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_FROZEN_HILLSIDE,
    ),
    StageName.AIR_RIDE_MAGMA_FLOWS: Stage(
        StageName.AIR_RIDE_MAGMA_FLOWS,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_MAGMA_FLOWS,
    ),
    StageName.AIR_RIDE_BEANSTALK_PARK: Stage(
        StageName.AIR_RIDE_BEANSTALK_PARK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_BEANSTALK_PARK,
    ),
    StageName.AIR_RIDE_MACHINE_PASSAGE: Stage(
        StageName.AIR_RIDE_MACHINE_PASSAGE,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_MACHINE_PASSAGE,
    ),
    StageName.AIR_RIDE_CHECKER_KNIGHTS: Stage(
        StageName.AIR_RIDE_CHECKER_KNIGHTS,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_CHECKER_KNIGHTS,
    ),
    StageName.AIR_RIDE_NEBULA_BELT: Stage(
        StageName.AIR_RIDE_NEBULA_BELT,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.START_GAME,
        SubSubMenuSelectionIDCityTrial.NONE,
        SubMenuFlag.OFF,
        StageID.AIR_RIDE_NEBULA_BELT,
    ),
    # StageName.AIR_RIDE_FANTASY_MEADOWS_FREE_RUN: Stage(
    #     StageName.AIR_RIDE_FANTASY_MEADOWS_FREE_RUN,
    #     MenuSelectionID.AIR_RIDE,
    #     SubMenuSelectionIDAirRide.FREE_RUN,
    #     SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.AIR_RIDE_FANTASY_MEADOWS_FREE_RUN,
    # ),
    StageName.AIR_RIDE_CELESTIAL_VALLEY_FREE_RUN: Stage(
        StageName.AIR_RIDE_CELESTIAL_VALLEY_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_CELESTIAL_VALLEY_FREE_RUN,
    ),
    StageName.AIR_RIDE_SKY_SANDS_FREE_RUN: Stage(
        StageName.AIR_RIDE_SKY_SANDS_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_SKY_SANDS_FREE_RUN,
    ),
    StageName.AIR_RIDE_FROZEN_HILLSIDE_FREE_RUN: Stage(
        StageName.AIR_RIDE_FROZEN_HILLSIDE_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_FROZEN_HILLSIDE_FREE_RUN,
    ),
    StageName.AIR_RIDE_MAGMA_FLOWS_FREE_RUN: Stage(
        StageName.AIR_RIDE_MAGMA_FLOWS_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_MAGMA_FLOWS_FREE_RUN,
    ),
    StageName.AIR_RIDE_BEANSTALK_PARK_FREE_RUN: Stage(
        StageName.AIR_RIDE_BEANSTALK_PARK_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_BEANSTALK_PARK_FREE_RUN,
    ),
    StageName.AIR_RIDE_MACHINE_PASSAGE_FREE_RUN: Stage(
        StageName.AIR_RIDE_MACHINE_PASSAGE_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_MACHINE_PASSAGE_FREE_RUN,
    ),
    StageName.AIR_RIDE_CHECKER_KNIGHTS_FREE_RUN: Stage(
        StageName.AIR_RIDE_CHECKER_KNIGHTS_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_CHECKER_KNIGHTS_FREE_RUN,
    ),
    StageName.AIR_RIDE_NEBULA_BELT_FREE_RUN: Stage(
        StageName.AIR_RIDE_NEBULA_BELT_FREE_RUN,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.FREE_RUN,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_NEBULA_BELT_FREE_RUN,
    ),
    # StageName.AIR_RIDE_FANTASY_MEADOWS_TIME_ATTACK: Stage(
    #     StageName.AIR_RIDE_FANTASY_MEADOWS_TIME_ATTACK,
    #     MenuSelectionID.AIR_RIDE,
    #     SubMenuSelectionIDAirRide.FREE_RUN,
    #     SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.AIR_RIDE_FANTASY_MEADOWS_TIME_ATTACK,
    # ),
    StageName.AIR_RIDE_CELESTIAL_VALLEY_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_CELESTIAL_VALLEY_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_CELESTIAL_VALLEY_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_SKY_SANDS_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_SKY_SANDS_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_SKY_SANDS_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_FROZEN_HILLSIDE_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_FROZEN_HILLSIDE_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_FROZEN_HILLSIDE_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_MAGMA_FLOWS_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_MAGMA_FLOWS_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_MAGMA_FLOWS_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_BEANSTALK_PARK_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_BEANSTALK_PARK_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_BEANSTALK_PARK_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_MACHINE_PASSAGE_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_MACHINE_PASSAGE_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_MACHINE_PASSAGE_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_CHECKER_KNIGHTS_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_CHECKER_KNIGHTS_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_CHECKER_KNIGHTS_TIME_ATTACK,
    ),
    StageName.AIR_RIDE_NEBULA_BELT_TIME_ATTACK: Stage(
        StageName.AIR_RIDE_NEBULA_BELT_TIME_ATTACK,
        MenuSelectionID.AIR_RIDE,
        SubMenuSelectionIDAirRide.FREE_RUN,
        SubSubMenuSelectionIDAirRideFreeRun.TIME_ATTACK,
        SubMenuFlag.ON,
        StageID.AIR_RIDE_NEBULA_BELT_TIME_ATTACK,
    ),
    # StageName.TOP_RIDE_GRASS: Stage(
    #     StageName.TOP_RIDE_GRASS,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_GRASS,
    # ),
    # StageName.TOP_RIDE_SAND: Stage(
    #     StageName.TOP_RIDE_SAND,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_SAND,
    # ),
    # StageName.TOP_RIDE_SKY: Stage(
    #     StageName.TOP_RIDE_SKY,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_SKY,
    # ),
    # StageName.TOP_RIDE_FIRE: Stage(
    #     StageName.TOP_RIDE_FIRE,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_FIRE,
    # ),
    # StageName.TOP_RIDE_LIGHT: Stage(
    #     StageName.TOP_RIDE_LIGHT,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_LIGHT,
    # ),
    # StageName.TOP_RIDE_WATER: Stage(
    #     StageName.TOP_RIDE_WATER,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_WATER,
    # ),
    # StageName.TOP_RIDE_METAL: Stage(
    #     StageName.TOP_RIDE_METAL,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.START_GAME,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.OFF,
    #     StageID.TOP_RIDE_METAL,
    # ),
    # StageName.TOP_RIDE_GRASS_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_GRASS_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_GRASS_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_SAND_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_SAND_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_SAND_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_SKY_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_SKY_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_SKY_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_FIRE_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_FIRE_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_FIRE_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_LIGHT_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_LIGHT_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_LIGHT_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_WATER_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_WATER_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_WATER_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_METAL_FREE_RUN: Stage(
    #     StageName.TOP_RIDE_METAL_FREE_RUN,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.FREE_RUN,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_METAL_FREE_RUN,
    # ),
    # StageName.TOP_RIDE_GRASS_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_GRASS_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_GRASS_TIME_ATTACK,
    # ),
    # StageName.TOP_RIDE_SAND_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_SAND_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_SAND_TIME_ATTACK,
    # ),
    # StageName.TOP_RIDE_SKY_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_SKY_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_SKY_TIME_ATTACK,
    # ),
    # StageName.TOP_RIDE_FIRE_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_FIRE_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_FIRE_TIME_ATTACK,
    # ),
    # StageName.TOP_RIDE_LIGHT_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_LIGHT_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_LIGHT_TIME_ATTACK,
    # ),
    # StageName.TOP_RIDE_WATER_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_WATER_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_WATER_TIME_ATTACK,
    # ),
    # StageName.TOP_RIDE_METAL_TIME_ATTACK: Stage(
    #     StageName.TOP_RIDE_METAL_TIME_ATTACK,
    #     MenuSelectionID.TOP_RIDE,
    #     SubMenuSelectionIDTopRide.FREE_RUN,
    #     SubSubMenuSelectionIDTopRideFreeRun.TIME_ATTACK,
    #     SubMenuFlag.ON,
    #     StageID.TOP_RIDE_METAL_TIME_ATTACK,
    # ),
}
