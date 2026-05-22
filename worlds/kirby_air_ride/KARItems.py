from enum import StrEnum
from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .KARData import GameMode


class KARItemType(StrEnum):
    """Categories of items in Kirby Air Ride. Each type maps to distinct pool-building behavior."""

    # Meta/progression items
    CHECKBOX_FILLER = "Checkbox Filler"
    PATCH_CAP_INCREASE = "Patch Cap Increase"
    PERMANENT_PATCH = "Permanent Patch"

    # Immediate effect items
    TRAP = "Trap"
    EFFECT = "Effect"
    EVENT_TRIGGER = "Event Trigger"
    GAME_ITEM = "Game Item"

    # Unlock items (each potentially toggled by player options)
    STADIUM_UNLOCK = "Stadium Unlock"
    EVENT_UNLOCK = "Event Unlock"
    ABILITY_UNLOCK = "Copy Ability Unlock"
    PATCH_UNLOCK = "Patch Type Unlock"
    ITEM_UNLOCK = "Item Unlock"
    MACHINE_UNLOCK = "Machine Unlock"
    BOX_UNLOCK = "Box Unlock"
    STAGE_UNLOCK = "Stage Unlock"
    COLOR_UNLOCK = "Color Unlock"
    TOPRIDE_ITEM_UNLOCK = "Top Ride Item Unlock"

    # Top Ride item give — spawns the item at human Kirby positions (Top Ride scene only)
    TOPRIDE_ITEM_GIVE = "Top Ride Item Give"

    # Checklist rewards (vanilla rewards from completing checklist entries)
    CHECKLIST_REWARD = "Checklist Reward"

    # Internal (event items with no network code)
    GOAL = "Goal"


class KARItemName(StrEnum):
    """Canonical item names for Kirby Air Ride. Single source of truth for all item name strings."""

    # Standalone Items (1-12)
    CHECKBOX_FILLER_AIR_RIDE = "Checkbox Filler (Air Ride)"
    CHECKBOX_FILLER_TOP_RIDE = "Checkbox Filler (Top Ride)"
    CHECKBOX_FILLER_CITY_TRIAL = "Checkbox Filler (City Trial)"
    PATCH_CAP_INCREASE = "Patch Cap Increase"
    ONE_HP_TRAP = "1 HP Trap"
    ALL_UP = "All Up"
    PERMANENT_ALL_UP = "Permanent All Up"
    ALL_DOWN = "All Down"
    GIVE_DRAGOON = "Give Dragoon"
    GIVE_HYDRA = "Give Hydra"
    SPAWN_RATE_UP = "Spawn Rate Up"
    DROP_PATCHES_TRAP = "Drop Patches Trap"

    # Permanent +1 Patches (100-108)
    PERMANENT_WEIGHT_UP = "Permanent Weight Up"
    PERMANENT_ACCEL_UP = "Permanent Accel Up"
    PERMANENT_TOP_SPEED_UP = "Permanent Top Speed Up"
    PERMANENT_TURN_UP = "Permanent Turn Up"
    PERMANENT_CHARGE_UP = "Permanent Charge Up"
    PERMANENT_GLIDE_UP = "Permanent Glide Up"
    PERMANENT_OFFENSE_UP = "Permanent Offense Up"
    PERMANENT_DEFENSE_UP = "Permanent Defense Up"
    PERMANENT_HP_UP = "Permanent HP Up"

    # City Trial Event Triggers (200-215)
    EVENT_TRIGGER_DYNA_BLADE = "Event Trigger: Dyna Blade"
    EVENT_TRIGGER_TAC = "Event Trigger: Tac"
    EVENT_TRIGGER_METEOR = "Event Trigger: Meteor"
    EVENT_TRIGGER_PILLAR = "Event Trigger: Pillar"
    EVENT_TRIGGER_RUN_AMOK = "Event Trigger: Run Amok"
    EVENT_TRIGGER_RESTORATION_AREA = "Event Trigger: Restoration Area"
    EVENT_TRIGGER_RAIL_FIRE = "Event Trigger: Rail Fire"
    EVENT_TRIGGER_SAME_ITEM = "Event Trigger: Same Item"
    EVENT_TRIGGER_LIGHTHOUSE = "Event Trigger: Lighthouse"
    EVENT_TRIGGER_SECRET_CHAMBER = "Event Trigger: Secret Chamber"
    EVENT_TRIGGER_PREDICTION = "Event Trigger: Prediction"
    EVENT_TRIGGER_MACHINE_FORMATION = "Event Trigger: Machine Formation"
    EVENT_TRIGGER_UFO = "Event Trigger: UFO"
    EVENT_TRIGGER_BOUNCE = "Event Trigger: Bounce"
    EVENT_TRIGGER_FOG = "Event Trigger: Fog"
    EVENT_TRIGGER_FAKE_POWERUPS = "Event Trigger: Fake Powerups"

    # Direct Game Items — Boxes (300-302)
    BLUE_BOX = "Blue Box"
    GREEN_BOX = "Green Box"
    RED_BOX = "Red Box"

    # Direct Game Items — Stat Patches Up (303-320)
    ACCEL_PATCH = "Accel Patch"
    TOP_SPEED_PATCH = "Top Speed Patch"
    OFFENSE_PATCH = "Offense Patch"
    DEFENSE_PATCH = "Defense Patch"
    TURN_PATCH = "Turn Patch"
    GLIDE_PATCH = "Glide Patch"
    CHARGE_PATCH = "Charge Patch"
    WEIGHT_PATCH = "Weight Patch"
    HP_PATCH = "HP Patch"
    ALL_UP_PATCH = "All Up Patch"

    # Direct Game Items — Stat Patches Down (304-318)
    ACCEL_DOWN_PATCH = "Accel Down Patch"
    TOP_SPEED_DOWN_PATCH = "Top Speed Down Patch"
    OFFENSE_DOWN_PATCH = "Offense Down Patch"
    DEFENSE_DOWN_PATCH = "Defense Down Patch"
    TURN_DOWN_PATCH = "Turn Down Patch"
    GLIDE_DOWN_PATCH = "Glide Down Patch"
    CHARGE_DOWN_PATCH = "Charge Down Patch"
    WEIGHT_DOWN_PATCH = "Weight Down Patch"

    # Direct Game Items — Extreme Stat Patches (321-326)
    SPEED_MAX_PATCH = "Speed Max Patch"
    SPEED_MIN_PATCH = "Speed Min Patch"
    OFFENSE_MAX_PATCH = "Offense Max Patch"
    DEFENSE_MAX_PATCH = "Defense Max Patch"
    CHARGE_MAX_PATCH = "Charge Max Patch"
    CHARGE_NONE_PATCH = "Charge None Patch"

    # Direct Game Items — Special (327)
    CANDY = "Candy"

    # Direct Game Items — Copy Abilities (328-338)
    COPY_ABILITY_BOMB = "Copy Ability: Bomb"
    COPY_ABILITY_FIRE = "Copy Ability: Fire"
    COPY_ABILITY_ICE = "Copy Ability: Ice"
    COPY_ABILITY_SLEEP = "Copy Ability: Sleep"
    COPY_ABILITY_WHEEL = "Copy Ability: Wheel"
    COPY_ABILITY_WING = "Copy Ability: Wing"
    COPY_ABILITY_PLASMA = "Copy Ability: Plasma"
    COPY_ABILITY_TORNADO = "Copy Ability: Tornado"
    COPY_ABILITY_SWORD = "Copy Ability: Sword"
    COPY_ABILITY_NEEDLE = "Copy Ability: Needle"
    COPY_ABILITY_MIC = "Copy Ability: Mic"

    # Direct Game Items — Food (339-350)
    MAXIM_TOMATO = "Maxim Tomato"
    ENERGY_DRINK = "Energy Drink"
    ICE_CREAM = "Ice Cream"
    RICE_BALL = "Rice Ball"
    CHICKEN = "Chicken"
    CURRY = "Curry"
    RAMEN = "Ramen"
    OMELET = "Omelet"
    HAMBURGER = "Hamburger"
    SUSHI = "Sushi"
    HOT_DOG = "Hot Dog"
    APPLE = "Apple"

    # Direct Game Items — Hazards (351-354)
    FIREWORKS = "Fireworks"
    PANIC_SPIN = "Panic Spin"
    SENSOR_BOMB = "Sensor Bomb"
    GORDO = "Gordo"

    # Direct Game Items — Legendary Machine Parts (355-360)
    HYDRA_PART_1 = "Hydra Part 1"
    HYDRA_PART_2 = "Hydra Part 2"
    HYDRA_PART_3 = "Hydra Part 3"
    DRAGOON_PART_1 = "Dragoon Part 1"
    DRAGOON_PART_2 = "Dragoon Part 2"
    DRAGOON_PART_3 = "Dragoon Part 3"

    # Direct Game Items — Fake Patches (361-368)
    FAKE_ACCEL_PATCH = "Fake Accel Patch"
    FAKE_TOP_SPEED_PATCH = "Fake Top Speed Patch"
    FAKE_OFFENSE_PATCH = "Fake Offense Patch"
    FAKE_DEFENSE_PATCH = "Fake Defense Patch"
    FAKE_TURN_PATCH = "Fake Turn Patch"
    FAKE_GLIDE_PATCH = "Fake Glide Patch"
    FAKE_CHARGE_PATCH = "Fake Charge Patch"
    FAKE_WEIGHT_PATCH = "Fake Weight Patch"

    # Stadium Unlocks (400-423)
    UNLOCK_STADIUM_DRAG_RACE_1 = "Unlock Stadium: DRAG RACE 1"
    UNLOCK_STADIUM_DRAG_RACE_2 = "Unlock Stadium: DRAG RACE 2"
    UNLOCK_STADIUM_DRAG_RACE_3 = "Unlock Stadium: DRAG RACE 3"
    UNLOCK_STADIUM_DRAG_RACE_4 = "Unlock Stadium: DRAG RACE 4"
    UNLOCK_STADIUM_AIR_GLIDER = "Unlock Stadium: AIR GLIDER"
    UNLOCK_STADIUM_TARGET_FLIGHT = "Unlock Stadium: TARGET FLIGHT"
    UNLOCK_STADIUM_HIGH_JUMP = "Unlock Stadium: HIGH JUMP"
    UNLOCK_STADIUM_KIRBY_MELEE_1 = "Unlock Stadium: KIRBY MELEE 1"
    UNLOCK_STADIUM_KIRBY_MELEE_2 = "Unlock Stadium: KIRBY MELEE 2"
    UNLOCK_STADIUM_DESTRUCTION_DERBY_1 = "Unlock Stadium: DESTRUCTION DERBY 1"
    UNLOCK_STADIUM_DESTRUCTION_DERBY_2 = "Unlock Stadium: DESTRUCTION DERBY 2"
    UNLOCK_STADIUM_DESTRUCTION_DERBY_3 = "Unlock Stadium: DESTRUCTION DERBY 3"
    UNLOCK_STADIUM_DESTRUCTION_DERBY_4 = "Unlock Stadium: DESTRUCTION DERBY 4"
    UNLOCK_STADIUM_DESTRUCTION_DERBY_5 = "Unlock Stadium: DESTRUCTION DERBY 5"
    UNLOCK_STADIUM_SINGLE_RACE_1 = "Unlock Stadium: SINGLE RACE 1"
    UNLOCK_STADIUM_SINGLE_RACE_2 = "Unlock Stadium: SINGLE RACE 2"
    UNLOCK_STADIUM_SINGLE_RACE_3 = "Unlock Stadium: SINGLE RACE 3"
    UNLOCK_STADIUM_SINGLE_RACE_4 = "Unlock Stadium: SINGLE RACE 4"
    UNLOCK_STADIUM_SINGLE_RACE_5 = "Unlock Stadium: SINGLE RACE 5"
    UNLOCK_STADIUM_SINGLE_RACE_6 = "Unlock Stadium: SINGLE RACE 6"
    UNLOCK_STADIUM_SINGLE_RACE_7 = "Unlock Stadium: SINGLE RACE 7"
    UNLOCK_STADIUM_SINGLE_RACE_8 = "Unlock Stadium: SINGLE RACE 8"
    UNLOCK_STADIUM_SINGLE_RACE_9 = "Unlock Stadium: SINGLE RACE 9"
    UNLOCK_STADIUM_VS_KING_DEDEDE = "Unlock Stadium: VS. KING DEDEDE"

    # Checklist Rewards — Air Ride (500-545)
    AR_REWARD_NEBULA_BELT_COURSE = "Air Ride Reward: Nebula Belt Course"
    AR_REWARD_MUSIC_NEBULA = "Air Ride Reward: Music - Nebula"
    AR_REWARD_META_KNIGHT = "Air Ride Reward: Meta Knight"
    AR_REWARD_SPECIAL_MACHINE_INTROS = "Air Ride Reward: Special Machine Intros"
    AR_REWARD_KING_DEDEDE = "Air Ride Reward: King Dedede"
    AR_REWARD_GREEN_KIRBY = "Air Ride Reward: Green Kirby"
    AR_REWARD_WAGON_STAR = "Air Ride Reward: Wagon Star"
    AR_REWARD_SOUND_TEST_MAGMA_FLOWS = "Air Ride Reward: Sound Test - Magma Flows"
    AR_REWARD_FILLER_BOX_1 = "Air Ride Reward: Filler Box 1"
    AR_REWARD_REX_WHEELIE = "Air Ride Reward: Rex Wheelie"
    AR_REWARD_PURPLE_KIRBY = "Air Ride Reward: Purple Kirby"
    AR_REWARD_SLICK_STAR = "Air Ride Reward: Slick Star"
    AR_REWARD_ENDING = "Air Ride Reward: Ending"
    AR_REWARD_WHITE_KIRBY = "Air Ride Reward: White Kirby"
    AR_REWARD_SWERVE_STAR = "Air Ride Reward: Swerve Star"
    AR_REWARD_SHADOW_STAR = "Air Ride Reward: Shadow Star"
    AR_REWARD_JET_STAR = "Air Ride Reward: Jet Star"
    AR_REWARD_MUSIC_HILLSIDE = "Air Ride Reward: Music - Hillside"
    AR_REWARD_SOUND_TEST_CHECKER_KNIGHTS = "Air Ride Reward: Sound Test - Checker Knights"
    AR_REWARD_MUSIC_MEADOWS = "Air Ride Reward: Music - Meadows"
    AR_REWARD_BULK_STAR = "Air Ride Reward: Bulk Star"
    AR_REWARD_SOUND_TEST_SKY_SANDS = "Air Ride Reward: Sound Test - Sky Sands"
    AR_REWARD_FORMULA_STAR = "Air Ride Reward: Formula Star"
    AR_REWARD_MUSIC_MAGMA = "Air Ride Reward: Music - Magma"
    AR_REWARD_MUSIC_BEANSTALK = "Air Ride Reward: Music - Beanstalk"
    AR_REWARD_SOUND_TEST_MACHINE_PASSAGE = "Air Ride Reward: Sound Test - Machine Passage"
    AR_REWARD_SOUND_TEST_FANTASY_MEADOWS = "Air Ride Reward: Sound Test - Fantasy Meadows"
    AR_REWARD_SOUND_TEST_CELESTIAL_VALLEY = "Air Ride Reward: Sound Test - Celestial Valley"
    AR_REWARD_BROWN_KIRBY = "Air Ride Reward: Brown Kirby"
    AR_REWARD_SOUND_TEST_FROZEN_HILLSIDE = "Air Ride Reward: Sound Test - Frozen Hillside"
    AR_REWARD_SOUND_TEST_BEANSTALK_PARK = "Air Ride Reward: Sound Test - Beanstalk Park"
    AR_REWARD_ROCKET_STAR = "Air Ride Reward: Rocket Star"
    AR_REWARD_SOUND_TEST_RESULTS_SCREEN = "Air Ride Reward: Sound Test - Results Screen"
    AR_REWARD_WHEELIE_BIKE = "Air Ride Reward: Wheelie Bike"
    AR_REWARD_WHEELIE_SCOOTER = "Air Ride Reward: Wheelie Scooter"
    AR_REWARD_WINGED_STAR = "Air Ride Reward: Winged Star"
    AR_REWARD_FILLER_BOX_2 = "Air Ride Reward: Filler Box 2"
    AR_REWARD_MUSIC_CHECKER = "Air Ride Reward: Music - Checker"
    AR_REWARD_FILLER_BOX_3 = "Air Ride Reward: Filler Box 3"
    AR_REWARD_MUSIC_SKY_SANDS = "Air Ride Reward: Music - Sky Sands"
    AR_REWARD_MUSIC_MACHINE = "Air Ride Reward: Music - Machine"
    AR_REWARD_TURBO_STAR = "Air Ride Reward: Turbo Star"
    AR_REWARD_FILLER_BOX_4 = "Air Ride Reward: Filler Box 4"
    AR_REWARD_MUSIC_CELESTIAL = "Air Ride Reward: Music - Celestial"
    AR_REWARD_FILLER_BOX_5 = "Air Ride Reward: Filler Box 5"
    AR_REWARD_SOUND_TEST_NEBULA_BELT = "Air Ride Reward: Sound Test - Nebula Belt"

    # Checklist Rewards — Top Ride (550-582)
    TR_REWARD_GREEN_KIRBY = "Top Ride Reward: Green Kirby"
    TR_REWARD_PURPLE_KIRBY = "Top Ride Reward: Purple Kirby"
    TR_REWARD_DIAGONAL_CAMERA_RULE = "Top Ride Reward: Diagonal Camera Rule"
    TR_REWARD_MYSTERY_ITEM_SET_RULE = "Top Ride Reward: Mystery Item Set Rule"
    TR_REWARD_LANTERN_ITEM = "Top Ride Reward: Lantern Item"
    TR_REWARD_WHO_PAINT_ITEM = "Top Ride Reward: Who? Paint Item"
    TR_REWARD_FILLER_BOX_1 = "Top Ride Reward: Filler Box 1"
    TR_REWARD_CHICKIE_ITEM = "Top Ride Reward: Chickie Item"
    TR_REWARD_SOUND_TEST_GRASS = "Top Ride Reward: Sound Test - Grass"
    TR_REWARD_MUSIC_GRASS = "Top Ride Reward: Music - Grass"
    TR_REWARD_SOUND_TEST_SAND = "Top Ride Reward: Sound Test - Sand"
    TR_REWARD_FILLER_BOX_2 = "Top Ride Reward: Filler Box 2"
    TR_REWARD_BROWN_KIRBY = "Top Ride Reward: Brown Kirby"
    TR_REWARD_SOUND_TEST_SKY = "Top Ride Reward: Sound Test - Sky"
    TR_REWARD_SOUND_TEST_FIRE = "Top Ride Reward: Sound Test - Fire"
    TR_REWARD_FILLER_BOX_3 = "Top Ride Reward: Filler Box 3"
    TR_REWARD_MUSIC_FIRE = "Top Ride Reward: Music - Fire"
    TR_REWARD_SOUND_TEST_WATER = "Top Ride Reward: Sound Test - Water"
    TR_REWARD_DEVICE_QUANTITY_RULE = "Top Ride Reward: Device Quantity Rule"
    TR_REWARD_MUSIC_WATER = "Top Ride Reward: Music - Water"
    TR_REWARD_SOUND_TEST_LIGHT = "Top Ride Reward: Sound Test - Light"
    TR_REWARD_FILLER_BOX_4 = "Top Ride Reward: Filler Box 4"
    TR_REWARD_MUSIC_METAL = "Top Ride Reward: Music - Metal"
    TR_REWARD_SOUND_TEST_METAL = "Top Ride Reward: Sound Test - Metal"
    TR_REWARD_WHITE_KIRBY = "Top Ride Reward: White Kirby"
    TR_REWARD_FILLER_BOX_5 = "Top Ride Reward: Filler Box 5"
    TR_REWARD_MUSIC_SAND = "Top Ride Reward: Music - Sand"
    TR_REWARD_MUSIC_LIGHT = "Top Ride Reward: Music - Light"
    TR_REWARD_ATTACK_ITEM_SET_RULE = "Top Ride Reward: Attack Item Set Rule"
    TR_REWARD_SOUND_TEST_RESULTS_SCREEN = "Top Ride Reward: Sound Test - Results Screen"
    TR_REWARD_MUSIC_SKY = "Top Ride Reward: Music - Sky"
    TR_REWARD_SIDE_CAMERA_RULE = "Top Ride Reward: Side Camera Rule"
    TR_REWARD_ENDING = "Top Ride Reward: Ending"

    # Checklist Rewards — City Trial (600-643)
    CT_REWARD_FILLER_BOX_1 = "City Trial Reward: Filler Box 1"
    CT_REWARD_SOUND_TEST_ITEM_BOUNCE = "City Trial Reward: Sound Test - Item Bounce"
    CT_REWARD_PAUSE_SCREEN_POWERUPS = "City Trial Reward: Pause Screen Power-ups"
    CT_REWARD_MUSIC_CITY = "City Trial Reward: Music - City"
    CT_REWARD_SOUND_TEST_LEGENDARY_MACHINE = "City Trial Reward: Sound Test - Legendary Machine"
    CT_REWARD_SOUND_TEST_DENSE_FOG = "City Trial Reward: Sound Test - Dense Fog"
    CT_REWARD_META_KNIGHT_FREE_RUN = "City Trial Reward: Meta Knight Free Run"
    CT_REWARD_SOUND_TEST_CITY_TRIAL = "City Trial Reward: Sound Test - City Trial"
    CT_REWARD_FILLER_BOX_2 = "City Trial Reward: Filler Box 2"
    CT_REWARD_SINGLE_RACE_NEBULA_STADIUM = "City Trial Reward: Single Race Nebula Stadium"
    CT_REWARD_SOUND_TEST_ROWDY_CHARGE_TANK = "City Trial Reward: Sound Test - Rowdy Charge Tank"
    CT_REWARD_DRAG_RACE_4_STADIUM = "City Trial Reward: Drag Race 4 Stadium"
    CT_REWARD_SOUND_TEST_DRAG_RACE = "City Trial Reward: Sound Test - Drag Race"
    CT_REWARD_DRAGOON_PART_A = "City Trial Reward: Dragoon Part A"
    CT_REWARD_SOUND_TEST_TARGET_FLIGHT = "City Trial Reward: Sound Test - Target Flight"
    CT_REWARD_DRAGOON_PART_C = "City Trial Reward: Dragoon Part C"
    CT_REWARD_SOUND_TEST_AIR_GLIDER = "City Trial Reward: Sound Test - Air Glider"
    CT_REWARD_DESTRUCTION_DERBY_4_STADIUM = "City Trial Reward: Destruction Derby 4 Stadium"
    CT_REWARD_FILLER_BOX_3 = "City Trial Reward: Filler Box 3"
    CT_REWARD_HYDRA_PART_Y = "City Trial Reward: Hydra Part Y"
    CT_REWARD_SOUND_TEST_WHATS_IN_THE_BOX = "City Trial Reward: Sound Test - What's in the Box?"
    CT_REWARD_HYDRA_PART_Z = "City Trial Reward: Hydra Part Z"
    CT_REWARD_KING_DEDEDE_FREE_RUN = "City Trial Reward: King Dedede Free Run"
    CT_REWARD_SOUND_TEST_DYNA_BLADE_INTRO = "City Trial Reward: Sound Test - Dyna Blade Intro"
    CT_REWARD_FILLER_BOX_4 = "City Trial Reward: Filler Box 4"
    CT_REWARD_SOUND_TEST_HUGE_PILLAR = "City Trial Reward: Sound Test - Huge Pillar"
    CT_REWARD_SOUND_TEST_TAC_CHALLENGE = "City Trial Reward: Sound Test - Tac Challenge"
    CT_REWARD_SOUND_TEST_FLYING_METEOR = "City Trial Reward: Sound Test - Flying Meteor"
    CT_REWARD_ENDING = "City Trial Reward: Ending"
    CT_REWARD_DRAGOON_PART_B = "City Trial Reward: Dragoon Part B"
    CT_REWARD_FILLER_BOX_5 = "City Trial Reward: Filler Box 5"
    CT_REWARD_HYDRA_PART_X = "City Trial Reward: Hydra Part X"
    CT_REWARD_PURPLE_KIRBY = "City Trial Reward: Purple Kirby"
    CT_REWARD_DESTRUCTION_DERBY_3_STADIUM = "City Trial Reward: Destruction Derby 3 Stadium"
    CT_REWARD_DESTRUCTION_DERBY_5_STADIUM = "City Trial Reward: Destruction Derby 5 Stadium"
    CT_REWARD_KIRBY_MELEE_2_STADIUM = "City Trial Reward: Kirby Melee 2 Stadium"
    CT_REWARD_SOUND_TEST_KIRBY_MELEE = "City Trial Reward: Sound Test - Kirby Melee"
    CT_REWARD_GREEN_KIRBY = "City Trial Reward: Green Kirby"
    CT_REWARD_BROWN_KIRBY = "City Trial Reward: Brown Kirby"
    CT_REWARD_DRAGOON_FREE_RUN = "City Trial Reward: Dragoon Free Run"
    CT_REWARD_HYDRA_FREE_RUN = "City Trial Reward: Hydra Free Run"
    CT_REWARD_SOUND_TEST_LIGHTHOUSE = "City Trial Reward: Sound Test - Lighthouse"
    CT_REWARD_SOUND_TEST_STATION_FIRE = "City Trial Reward: Sound Test - Station Fire"
    CT_REWARD_WHITE_KIRBY = "City Trial Reward: White Kirby"

    # Event Unlocks (700-715)
    UNLOCK_EVENT_DYNA_BLADE = "Unlock Event: Dyna Blade"
    UNLOCK_EVENT_TAC = "Unlock Event: Tac"
    UNLOCK_EVENT_METEOR = "Unlock Event: Meteor"
    UNLOCK_EVENT_PILLAR = "Unlock Event: Pillar"
    UNLOCK_EVENT_RUN_AMOK = "Unlock Event: Run Amok"
    UNLOCK_EVENT_RESTORATION_AREA = "Unlock Event: Restoration Area"
    UNLOCK_EVENT_RAIL_FIRE = "Unlock Event: Rail Fire"
    UNLOCK_EVENT_SAME_ITEM = "Unlock Event: Same Item"
    UNLOCK_EVENT_LIGHTHOUSE = "Unlock Event: Lighthouse"
    UNLOCK_EVENT_SECRET_CHAMBER = "Unlock Event: Secret Chamber"
    UNLOCK_EVENT_PREDICTION = "Unlock Event: Prediction"
    UNLOCK_EVENT_MACHINE_FORMATION = "Unlock Event: Machine Formation"
    UNLOCK_EVENT_UFO = "Unlock Event: UFO"
    UNLOCK_EVENT_BOUNCE = "Unlock Event: Bounce"
    UNLOCK_EVENT_FOG = "Unlock Event: Fog"
    UNLOCK_EVENT_FAKE_POWERUPS = "Unlock Event: Fake Powerups"

    # Copy Ability Unlocks (760-770)
    UNLOCK_ABILITY_FIRE = "Unlock Ability: Fire"
    UNLOCK_ABILITY_WHEEL = "Unlock Ability: Wheel"
    UNLOCK_ABILITY_SLEEP = "Unlock Ability: Sleep"
    UNLOCK_ABILITY_SWORD = "Unlock Ability: Sword"
    UNLOCK_ABILITY_BOMB = "Unlock Ability: Bomb"
    UNLOCK_ABILITY_PLASMA = "Unlock Ability: Plasma"
    UNLOCK_ABILITY_NEEDLE = "Unlock Ability: Needle"
    UNLOCK_ABILITY_MIC = "Unlock Ability: Mic"
    UNLOCK_ABILITY_ICE = "Unlock Ability: Ice"
    UNLOCK_ABILITY_TORNADO = "Unlock Ability: Tornado"
    UNLOCK_ABILITY_WING = "Unlock Ability: Wing"

    # Patch Type Unlocks (780-788)
    UNLOCK_PATCH_WEIGHT = "Unlock Patch: Weight"
    UNLOCK_PATCH_ACCEL = "Unlock Patch: Accel"
    UNLOCK_PATCH_TOP_SPEED = "Unlock Patch: Top Speed"
    UNLOCK_PATCH_TURN = "Unlock Patch: Turn"
    UNLOCK_PATCH_CHARGE = "Unlock Patch: Charge"
    UNLOCK_PATCH_GLIDE = "Unlock Patch: Glide"
    UNLOCK_PATCH_OFFENSE = "Unlock Patch: Offense"
    UNLOCK_PATCH_DEFENSE = "Unlock Patch: Defense"
    UNLOCK_PATCH_HP = "Unlock Patch: HP"

    # Item Unlocks (790-819)
    UNLOCK_ITEM_ALL_UP = "Unlock Item: All Up"
    UNLOCK_ITEM_SPEED_MAX = "Unlock Item: Speed Max"
    UNLOCK_ITEM_SPEED_MIN = "Unlock Item: Speed Min"
    UNLOCK_ITEM_OFFENSE_MAX = "Unlock Item: Offense Max"
    UNLOCK_ITEM_DEFENSE_MAX = "Unlock Item: Defense Max"
    UNLOCK_ITEM_CHARGE_MAX = "Unlock Item: Charge Max"
    UNLOCK_ITEM_CHARGE_NONE = "Unlock Item: Charge None"
    UNLOCK_ITEM_CANDY = "Unlock Item: Candy"
    UNLOCK_ITEM_MAXIM_TOMATO = "Unlock Item: Maxim Tomato"
    UNLOCK_ITEM_ENERGY_DRINK = "Unlock Item: Energy Drink"
    UNLOCK_ITEM_ICE_CREAM = "Unlock Item: Ice Cream"
    UNLOCK_ITEM_RICE_BALL = "Unlock Item: Rice Ball"
    UNLOCK_ITEM_CHICKEN = "Unlock Item: Chicken"
    UNLOCK_ITEM_CURRY = "Unlock Item: Curry"
    UNLOCK_ITEM_RAMEN = "Unlock Item: Ramen"
    UNLOCK_ITEM_OMELET = "Unlock Item: Omelet"
    UNLOCK_ITEM_HAMBURGER = "Unlock Item: Hamburger"
    UNLOCK_ITEM_SUSHI = "Unlock Item: Sushi"
    UNLOCK_ITEM_HOT_DOG = "Unlock Item: Hot Dog"
    UNLOCK_ITEM_APPLE = "Unlock Item: Apple"
    UNLOCK_ITEM_FIREWORKS = "Unlock Item: Fireworks"
    UNLOCK_ITEM_PANIC_SPIN = "Unlock Item: Panic Spin"
    UNLOCK_ITEM_SENSOR_BOMB = "Unlock Item: Sensor Bomb"
    UNLOCK_ITEM_GORDO = "Unlock Item: Gordo"
    UNLOCK_ITEM_HYDRA_PART_1 = "Unlock Item: Hydra Part 1"
    UNLOCK_ITEM_HYDRA_PART_2 = "Unlock Item: Hydra Part 2"
    UNLOCK_ITEM_HYDRA_PART_3 = "Unlock Item: Hydra Part 3"
    UNLOCK_ITEM_DRAGOON_PART_1 = "Unlock Item: Dragoon Part 1"
    UNLOCK_ITEM_DRAGOON_PART_2 = "Unlock Item: Dragoon Part 2"
    UNLOCK_ITEM_DRAGOON_PART_3 = "Unlock Item: Dragoon Part 3"

    # Machine Unlocks (830-854)
    # VCKIND_WHEELVSDEDEDE (would be 855) is intentionally excluded — it is the
    # Vs. King Dedede stadium's CPU-only machine and is not player-rideable.
    UNLOCK_MACHINE_WARP_STAR = "Unlock Machine: Warp Star"
    UNLOCK_MACHINE_COMPACT_STAR = "Unlock Machine: Compact Star"
    UNLOCK_MACHINE_WINGED_STAR = "Unlock Machine: Winged Star"
    UNLOCK_MACHINE_SHADOW_STAR = "Unlock Machine: Shadow Star"
    UNLOCK_MACHINE_HYDRA = "Unlock Machine: Hydra"
    UNLOCK_MACHINE_BULK_STAR = "Unlock Machine: Bulk Star"
    UNLOCK_MACHINE_SLICK_STAR = "Unlock Machine: Slick Star"
    UNLOCK_MACHINE_FORMULA_STAR = "Unlock Machine: Formula Star"
    UNLOCK_MACHINE_DRAGOON = "Unlock Machine: Dragoon"
    UNLOCK_MACHINE_WAGON_STAR = "Unlock Machine: Wagon Star"
    UNLOCK_MACHINE_ROCKET_STAR = "Unlock Machine: Rocket Star"
    UNLOCK_MACHINE_SWERVE_STAR = "Unlock Machine: Swerve Star"
    UNLOCK_MACHINE_TURBO_STAR = "Unlock Machine: Turbo Star"
    UNLOCK_MACHINE_JET_STAR = "Unlock Machine: Jet Star"
    UNLOCK_MACHINE_FLIGHT_WARP_STAR = "Unlock Machine: Flight Warp Star"
    UNLOCK_MACHINE_FREE_STAR = "Unlock Machine: Free Star"
    UNLOCK_MACHINE_STEER_STAR = "Unlock Machine: Steer Star"
    UNLOCK_MACHINE_WING_KIRBY = "Unlock Machine: Wing Kirby"
    UNLOCK_MACHINE_WING_META_KNIGHT = "Unlock Machine: Wing Meta Knight"
    UNLOCK_MACHINE_WHEELIE = "Unlock Machine: Wheelie"
    UNLOCK_MACHINE_WHEELIE_KIRBY = "Unlock Machine: Wheelie Kirby"
    UNLOCK_MACHINE_WHEELIE_BIKE = "Unlock Machine: Wheelie Bike"
    UNLOCK_MACHINE_REX_WHEELIE = "Unlock Machine: Rex Wheelie"
    UNLOCK_MACHINE_WHEELIE_SCOOTER = "Unlock Machine: Wheelie Scooter"
    UNLOCK_MACHINE_WHEELIE_DEDEDE = "Unlock Machine: Wheelie Dedede"

    # Box Unlocks (860-862)
    UNLOCK_BOX_BLUE = "Unlock Box: Blue"
    UNLOCK_BOX_GREEN = "Unlock Box: Green"
    UNLOCK_BOX_RED = "Unlock Box: Red"

    # Air Ride Course Unlocks (870-878)
    UNLOCK_AR_COURSE_FANTASY_MEADOWS = "Unlock AR Course: Fantasy Meadows"
    UNLOCK_AR_COURSE_MAGMA_FLOWS = "Unlock AR Course: Magma Flows"
    UNLOCK_AR_COURSE_SKY_SANDS = "Unlock AR Course: Sky Sands"
    UNLOCK_AR_COURSE_FROZEN_HILLSIDE = "Unlock AR Course: Frozen Hillside"
    UNLOCK_AR_COURSE_BEANSTALK_PARK = "Unlock AR Course: Beanstalk Park"
    UNLOCK_AR_COURSE_CELESTIAL_VALLEY = "Unlock AR Course: Celestial Valley"
    UNLOCK_AR_COURSE_MACHINE_PASSAGE = "Unlock AR Course: Machine Passage"
    UNLOCK_AR_COURSE_CHECKER_KNIGHTS = "Unlock AR Course: Checker Knights"
    UNLOCK_AR_COURSE_NEBULA_BELT = "Unlock AR Course: Nebula Belt"

    # Kirby Color Unlocks (880-887)
    UNLOCK_COLOR_PINK = "Unlock Color: Pink"
    UNLOCK_COLOR_YELLOW = "Unlock Color: Yellow"
    UNLOCK_COLOR_BLUE = "Unlock Color: Blue"
    UNLOCK_COLOR_RED = "Unlock Color: Red"
    UNLOCK_COLOR_GREEN = "Unlock Color: Green"
    UNLOCK_COLOR_PURPLE = "Unlock Color: Purple"
    UNLOCK_COLOR_BROWN = "Unlock Color: Brown"
    UNLOCK_COLOR_WHITE = "Unlock Color: White"

    # Top Ride Course Unlocks (890-896)
    UNLOCK_TR_COURSE_GRASS = "Unlock TR Course: Grass"
    UNLOCK_TR_COURSE_SAND = "Unlock TR Course: Sand"
    UNLOCK_TR_COURSE_SKY = "Unlock TR Course: Sky"
    UNLOCK_TR_COURSE_FIRE = "Unlock TR Course: Fire"
    UNLOCK_TR_COURSE_LIGHT = "Unlock TR Course: Light"
    UNLOCK_TR_COURSE_WATER = "Unlock TR Course: Water"
    UNLOCK_TR_COURSE_METAL = "Unlock TR Course: Metal"

    # Top Ride Item Unlocks (900-921, minus 5 reserved slots)
    # Freeze Fan (909), Fire (911), Bomb (913), Walky (916) are gated
    # by `ability_unlocked_mask` in the mod, not by `topride_item_unlocked_mask`,
    # so they have no unlock-item form here — the corresponding ability unlock
    # is the gate. Their immediate-give forms still exist at 959/961/963/966.
    # ID 912 is the engine's KirbyKusdama Party Ball variant; the visible
    # Party Ball item lives at slot 21 (ID 921), and the mod mirrors bit 12
    # onto bit 21's unlock state so both variants spawn together.
    UNLOCK_TR_ITEM_HAMMER = "Unlock TR Item: Hammer"
    UNLOCK_TR_ITEM_BIG_CAKE = "Unlock TR Item: Big Cake"
    UNLOCK_TR_ITEM_SPEED_UP = "Unlock TR Item: Speed Up"
    UNLOCK_TR_ITEM_SPEED_DOWN = "Unlock TR Item: Speed Down"
    UNLOCK_TR_ITEM_SPINNER = "Unlock TR Item: Spinner"
    UNLOCK_TR_ITEM_CHARGE_TANK = "Unlock TR Item: Charge Tank"
    UNLOCK_TR_ITEM_INVINCIBLE_CANDY = "Unlock TR Item: Invincible Candy"
    UNLOCK_TR_ITEM_BUZZ_SAW = "Unlock TR Item: Buzz Saw"
    UNLOCK_TR_ITEM_DRILL = "Unlock TR Item: Drill"
    UNLOCK_TR_ITEM_MISSILE = "Unlock TR Item: Missile"
    UNLOCK_TR_ITEM_STEP_BOOM = "Unlock TR Item: Step-boom"
    UNLOCK_TR_ITEM_LANTERN = "Unlock TR Item: Lantern"
    UNLOCK_TR_ITEM_KRACKO = "Unlock TR Item: Kracko"
    UNLOCK_TR_ITEM_WHO_PAINT = "Unlock TR Item: Who? Paint"
    UNLOCK_TR_ITEM_SMOKESCREEN = "Unlock TR Item: Smokescreen"
    UNLOCK_TR_ITEM_CHICKIE = "Unlock TR Item: Chickie"
    UNLOCK_TR_ITEM_PARTY_BALL = "Unlock TR Item: Party Ball"

    # Top Ride Item Gives (950-971)
    # Spawn the TR item at every human Kirby's position so it's collected next frame.
    # Only effective in a Top Ride scene; queued otherwise until scene matches.
    GIVE_TR_ITEM_HAMMER = "Give TR Item: Hammer"
    GIVE_TR_ITEM_BIG_CAKE = "Give TR Item: Big Cake"
    GIVE_TR_ITEM_SPEED_UP = "Give TR Item: Speed Up"
    GIVE_TR_ITEM_SPEED_DOWN = "Give TR Item: Speed Down"
    GIVE_TR_ITEM_SPINNER = "Give TR Item: Spinner"
    GIVE_TR_ITEM_CHARGE_TANK = "Give TR Item: Charge Tank"
    GIVE_TR_ITEM_INVINCIBLE_CANDY = "Give TR Item: Invincible Candy"
    GIVE_TR_ITEM_BUZZ_SAW = "Give TR Item: Buzz Saw"
    GIVE_TR_ITEM_DRILL = "Give TR Item: Drill"
    GIVE_TR_ITEM_FREEZE_FAN = "Give TR Item: Freeze Fan"
    GIVE_TR_ITEM_MISSILE = "Give TR Item: Missile"
    GIVE_TR_ITEM_FIRE = "Give TR Item: Fire"
    GIVE_TR_ITEM_BOMB = "Give TR Item: Bomb"
    GIVE_TR_ITEM_STEP_BOOM = "Give TR Item: Step-boom"
    GIVE_TR_ITEM_LANTERN = "Give TR Item: Lantern"
    GIVE_TR_ITEM_WALKY = "Give TR Item: Walky"
    GIVE_TR_ITEM_KRACKO = "Give TR Item: Kracko"
    GIVE_TR_ITEM_WHO_PAINT = "Give TR Item: Who? Paint"
    GIVE_TR_ITEM_SMOKESCREEN = "Give TR Item: Smokescreen"
    GIVE_TR_ITEM_CHICKIE = "Give TR Item: Chickie"
    GIVE_TR_ITEM_PARTY_BALL = "Give TR Item: Party Ball"

    # Goal Events (no network code — internal AP events only)
    CITY_TRIAL_VICTORY = "City Trial Victory"
    AIR_RIDE_VICTORY = "Air Ride Victory"
    TOP_RIDE_VICTORY = "Top Ride Victory"


class KARItemData(NamedTuple):
    """Data for an item in Kirby Air Ride.

    type: The item's functional category.
    classification: Default AP classification (progression, useful, filler, trap).
    code: AP item code matching the mod's APItemId enum. None for event-only items.
    source_modes: Modes the item is meaningful for. Under cross_mode_placement=false,
        the item can only land in a location belonging to one of these modes. Empty
        frozenset means no restriction (item places anywhere).
    """

    type: KARItemType
    classification: ItemClassification
    code: int | None
    source_modes: frozenset[GameMode] = frozenset()


# Mode-source aliases — concise tags for ITEM_TABLE rows.
_AR = frozenset({GameMode.AIRRIDE})
_TR = frozenset({GameMode.TOPRIDE})
_CT = frozenset({GameMode.CITYTRIAL})
_AR_CT = frozenset({GameMode.AIRRIDE, GameMode.CITYTRIAL})
_CT_TR = frozenset({GameMode.CITYTRIAL, GameMode.TOPRIDE})
_ALL_MODES = frozenset({GameMode.AIRRIDE, GameMode.TOPRIDE, GameMode.CITYTRIAL})


class KARItem(Item):
    """An Archipelago item for Kirby Air Ride.

    Uses the base Item constructor signature so it composes with helpers like
    Region.add_event that instantiate items as Item(name, classification, code, player).
    Table-driven items should be created via KARItem.from_data instead.
    """

    game: str = "Kirby Air Ride"
    type: KARItemType | None = None  # None for event items (no ITEM_TABLE entry)
    source_modes: frozenset[GameMode] = frozenset()

    @classmethod
    def from_data(cls, name: str, player: int, data: KARItemData) -> "KARItem":
        item = cls(name, data.classification, data.code, player)
        item.type = data.type
        item.source_modes = data.source_modes
        return item


# ITEM TABLE
# Master table of all items. Codes match the mod's APItemId enum exactly —
# the code is the value written to Dolphin memory for the mod to interpret.
# Pool quantities are determined by options and pool-building logic in __init__.py.

ITEM_TABLE: dict[str, KARItemData] = {
    # Standalone Items (1-12)
    KARItemName.CHECKBOX_FILLER_AIR_RIDE: KARItemData(KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 1, _AR),
    KARItemName.CHECKBOX_FILLER_TOP_RIDE: KARItemData(KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 2, _TR),
    KARItemName.CHECKBOX_FILLER_CITY_TRIAL: KARItemData(KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 3, _CT),
    KARItemName.PATCH_CAP_INCREASE: KARItemData(KARItemType.PATCH_CAP_INCREASE, ItemClassification.progression, 4, _CT),
    KARItemName.ONE_HP_TRAP: KARItemData(KARItemType.TRAP, ItemClassification.trap, 5, _AR_CT),
    KARItemName.ALL_UP: KARItemData(KARItemType.EFFECT, ItemClassification.useful, 6, _AR_CT),
    KARItemName.PERMANENT_ALL_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 7, _CT),
    KARItemName.ALL_DOWN: KARItemData(KARItemType.TRAP, ItemClassification.trap, 8, _AR_CT),
    KARItemName.GIVE_DRAGOON: KARItemData(KARItemType.EFFECT, ItemClassification.useful, 9, _CT),
    KARItemName.GIVE_HYDRA: KARItemData(KARItemType.EFFECT, ItemClassification.useful, 10, _CT),
    KARItemName.SPAWN_RATE_UP: KARItemData(KARItemType.EFFECT, ItemClassification.useful, 11, _CT_TR),
    KARItemName.DROP_PATCHES_TRAP: KARItemData(KARItemType.TRAP, ItemClassification.trap, 12, _CT),
    # Permanent +1 Patches (100-108)
    KARItemName.PERMANENT_WEIGHT_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 100, _CT),
    KARItemName.PERMANENT_ACCEL_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 101, _CT),
    KARItemName.PERMANENT_TOP_SPEED_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 102, _CT),
    KARItemName.PERMANENT_TURN_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 103, _CT),
    KARItemName.PERMANENT_CHARGE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 104, _CT),
    KARItemName.PERMANENT_GLIDE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 105, _CT),
    KARItemName.PERMANENT_OFFENSE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 106, _CT),
    KARItemName.PERMANENT_DEFENSE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 107, _CT),
    KARItemName.PERMANENT_HP_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 108, _CT),
    # City Trial Event Triggers (200-215)
    # Receiving one of these fires the corresponding event immediately.
    # Separate from event unlocks (700+), which gate whether events occur naturally.
    KARItemName.EVENT_TRIGGER_DYNA_BLADE: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 200, _CT),
    KARItemName.EVENT_TRIGGER_TAC: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 201, _CT),
    KARItemName.EVENT_TRIGGER_METEOR: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 202, _CT),
    KARItemName.EVENT_TRIGGER_PILLAR: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 203, _CT),
    KARItemName.EVENT_TRIGGER_RUN_AMOK: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 204, _CT),
    KARItemName.EVENT_TRIGGER_RESTORATION_AREA: KARItemData(
        KARItemType.EVENT_TRIGGER, ItemClassification.useful, 205, _CT
    ),
    KARItemName.EVENT_TRIGGER_RAIL_FIRE: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 206, _CT),
    KARItemName.EVENT_TRIGGER_SAME_ITEM: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 207, _CT),
    KARItemName.EVENT_TRIGGER_LIGHTHOUSE: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 208, _CT),
    KARItemName.EVENT_TRIGGER_SECRET_CHAMBER: KARItemData(
        KARItemType.EVENT_TRIGGER, ItemClassification.useful, 209, _CT
    ),
    KARItemName.EVENT_TRIGGER_PREDICTION: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 210, _CT),
    KARItemName.EVENT_TRIGGER_MACHINE_FORMATION: KARItemData(
        KARItemType.EVENT_TRIGGER, ItemClassification.useful, 211, _CT
    ),
    KARItemName.EVENT_TRIGGER_UFO: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 212, _CT),
    KARItemName.EVENT_TRIGGER_BOUNCE: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 213, _CT),
    KARItemName.EVENT_TRIGGER_FOG: KARItemData(KARItemType.EVENT_TRIGGER, ItemClassification.useful, 214, _CT),
    KARItemName.EVENT_TRIGGER_FAKE_POWERUPS: KARItemData(
        KARItemType.EVENT_TRIGGER, ItemClassification.useful, 215, _CT
    ),
    # Direct Game Items (300-368)
    # The mod spawns/applies the actual in-game item when received.
    # Available in fill pools, drawn as needed during pool building.
    # Can be overridden to progression by options.
    # Boxes
    KARItemName.BLUE_BOX: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 300, _CT),
    KARItemName.GREEN_BOX: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 301, _CT),
    KARItemName.RED_BOX: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 302, _CT),
    # Stat patches (up)
    KARItemName.ACCEL_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 303, _CT),
    KARItemName.TOP_SPEED_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 305, _CT),
    KARItemName.OFFENSE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 307, _CT),
    KARItemName.DEFENSE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 309, _CT),
    KARItemName.TURN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 311, _CT),
    KARItemName.GLIDE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 313, _CT),
    KARItemName.CHARGE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 315, _CT),
    KARItemName.WEIGHT_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 317, _CT),
    KARItemName.HP_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 319, _CT),
    KARItemName.ALL_UP_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 320, _CT),
    # Stat patches (down)
    KARItemName.ACCEL_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 304, _CT),
    KARItemName.TOP_SPEED_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 306, _CT),
    KARItemName.OFFENSE_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 308, _CT),
    KARItemName.DEFENSE_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 310, _CT),
    KARItemName.TURN_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 312, _CT),
    KARItemName.GLIDE_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 314, _CT),
    KARItemName.CHARGE_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 316, _CT),
    KARItemName.WEIGHT_DOWN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 318, _CT),
    # Extreme stat patches
    KARItemName.SPEED_MAX_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 321, _CT),
    KARItemName.SPEED_MIN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 322, _CT),
    KARItemName.OFFENSE_MAX_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 323, _CT),
    KARItemName.DEFENSE_MAX_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 324, _CT),
    KARItemName.CHARGE_MAX_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 325, _CT),
    KARItemName.CHARGE_NONE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 326, _CT),
    # Special items
    KARItemName.CANDY: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 327, _CT),
    # Copy abilities (in-game item form)
    KARItemName.COPY_ABILITY_BOMB: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 328, _ALL_MODES),
    KARItemName.COPY_ABILITY_FIRE: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 329, _ALL_MODES),
    KARItemName.COPY_ABILITY_ICE: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 330, _ALL_MODES),
    KARItemName.COPY_ABILITY_SLEEP: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 331, _AR_CT),
    KARItemName.COPY_ABILITY_WHEEL: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 332, _AR_CT),
    KARItemName.COPY_ABILITY_WING: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 333, _AR_CT),
    KARItemName.COPY_ABILITY_PLASMA: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 334, _AR_CT),
    KARItemName.COPY_ABILITY_TORNADO: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 335, _AR_CT),
    KARItemName.COPY_ABILITY_SWORD: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 336, _AR_CT),
    KARItemName.COPY_ABILITY_NEEDLE: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 337, _AR_CT),
    KARItemName.COPY_ABILITY_MIC: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 338, _ALL_MODES),
    # Food
    KARItemName.MAXIM_TOMATO: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 339, _CT),
    KARItemName.ENERGY_DRINK: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 340, _CT),
    KARItemName.ICE_CREAM: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 341, _CT),
    KARItemName.RICE_BALL: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 342, _CT),
    KARItemName.CHICKEN: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 343, _CT),
    KARItemName.CURRY: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 344, _CT),
    KARItemName.RAMEN: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 345, _CT),
    KARItemName.OMELET: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 346, _CT),
    KARItemName.HAMBURGER: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 347, _CT),
    KARItemName.SUSHI: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 348, _CT),
    KARItemName.HOT_DOG: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 349, _CT),
    KARItemName.APPLE: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 350, _CT),
    # Hazards / miscellaneous
    KARItemName.FIREWORKS: KARItemData(KARItemType.GAME_ITEM, ItemClassification.filler, 351, _CT),
    KARItemName.PANIC_SPIN: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 352, _CT),
    KARItemName.SENSOR_BOMB: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 353, _CT),
    KARItemName.GORDO: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 354, _CT),
    # Legendary machine parts
    KARItemName.HYDRA_PART_1: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 355, _CT),
    KARItemName.HYDRA_PART_2: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 356, _CT),
    KARItemName.HYDRA_PART_3: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 357, _CT),
    KARItemName.DRAGOON_PART_1: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 358, _CT),
    KARItemName.DRAGOON_PART_2: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 359, _CT),
    KARItemName.DRAGOON_PART_3: KARItemData(KARItemType.GAME_ITEM, ItemClassification.useful, 360, _CT),
    # Fake patches (look like stat ups but are traps)
    KARItemName.FAKE_ACCEL_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 361, _CT),
    KARItemName.FAKE_TOP_SPEED_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 362, _CT),
    KARItemName.FAKE_OFFENSE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 363, _CT),
    KARItemName.FAKE_DEFENSE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 364, _CT),
    KARItemName.FAKE_TURN_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 365, _CT),
    KARItemName.FAKE_GLIDE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 366, _CT),
    KARItemName.FAKE_CHARGE_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 367, _CT),
    KARItemName.FAKE_WEIGHT_PATCH: KARItemData(KARItemType.GAME_ITEM, ItemClassification.trap, 368, _CT),
    # Stadium Unlocks (400-423)
    # Each unlocks a specific City Trial stadium.
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_1: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 400, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_2: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 401, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_3: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 402, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_4: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 403, _CT
    ),
    KARItemName.UNLOCK_STADIUM_AIR_GLIDER: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 404, _CT
    ),
    KARItemName.UNLOCK_STADIUM_TARGET_FLIGHT: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 405, _CT
    ),
    KARItemName.UNLOCK_STADIUM_HIGH_JUMP: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 406, _CT
    ),
    KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 407, _CT
    ),
    KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 408, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 409, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 410, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 411, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 412, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 413, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_1: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 414, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_2: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 415, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_3: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 416, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_4: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 417, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_5: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 418, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_6: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 419, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_7: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 420, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_8: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 421, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_9: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 422, _CT
    ),
    KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE: KARItemData(
        KARItemType.STADIUM_UNLOCK, ItemClassification.progression, 423, _CT
    ),
    # Checklist Rewards — Air Ride (500-545)
    # Vanilla rewards from completing Air Ride checklist entries.
    # Receiving these performs the actual unlock (machine, music, etc.)
    KARItemName.AR_REWARD_NEBULA_BELT_COURSE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 500, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_NEBULA: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 501, _AR),
    KARItemName.AR_REWARD_META_KNIGHT: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 502, _AR),
    KARItemName.AR_REWARD_SPECIAL_MACHINE_INTROS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 503, _AR
    ),
    KARItemName.AR_REWARD_KING_DEDEDE: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 504, _AR),
    KARItemName.AR_REWARD_GREEN_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 505, _AR),
    KARItemName.AR_REWARD_WAGON_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 506, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_MAGMA_FLOWS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 507, _AR
    ),
    KARItemName.AR_REWARD_FILLER_BOX_1: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 508, _AR),
    KARItemName.AR_REWARD_REX_WHEELIE: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 509, _AR),
    KARItemName.AR_REWARD_PURPLE_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 510, _AR),
    KARItemName.AR_REWARD_SLICK_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 511, _AR),
    KARItemName.AR_REWARD_ENDING: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 512, _AR),
    KARItemName.AR_REWARD_WHITE_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 513, _AR),
    KARItemName.AR_REWARD_SWERVE_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 514, _AR),
    KARItemName.AR_REWARD_SHADOW_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 515, _AR),
    KARItemName.AR_REWARD_JET_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 516, _AR),
    KARItemName.AR_REWARD_MUSIC_HILLSIDE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 517, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_CHECKER_KNIGHTS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 518, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_MEADOWS: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 519, _AR),
    KARItemName.AR_REWARD_BULK_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 520, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_SKY_SANDS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 521, _AR
    ),
    KARItemName.AR_REWARD_FORMULA_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 522, _AR),
    KARItemName.AR_REWARD_MUSIC_MAGMA: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 523, _AR),
    KARItemName.AR_REWARD_MUSIC_BEANSTALK: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 524, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_MACHINE_PASSAGE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 525, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_FANTASY_MEADOWS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 526, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_CELESTIAL_VALLEY: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 527, _AR
    ),
    KARItemName.AR_REWARD_BROWN_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 528, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_FROZEN_HILLSIDE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 529, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_BEANSTALK_PARK: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 530, _AR
    ),
    KARItemName.AR_REWARD_ROCKET_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 531, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_RESULTS_SCREEN: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 532, _AR
    ),
    KARItemName.AR_REWARD_WHEELIE_BIKE: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 533, _AR),
    KARItemName.AR_REWARD_WHEELIE_SCOOTER: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 534, _AR
    ),
    KARItemName.AR_REWARD_WINGED_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 535, _AR),
    KARItemName.AR_REWARD_FILLER_BOX_2: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 536, _AR),
    KARItemName.AR_REWARD_MUSIC_CHECKER: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 537, _AR),
    KARItemName.AR_REWARD_FILLER_BOX_3: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 538, _AR),
    KARItemName.AR_REWARD_MUSIC_SKY_SANDS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 539, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_MACHINE: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 540, _AR),
    KARItemName.AR_REWARD_TURBO_STAR: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 541, _AR),
    KARItemName.AR_REWARD_FILLER_BOX_4: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 542, _AR),
    KARItemName.AR_REWARD_MUSIC_CELESTIAL: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 543, _AR
    ),
    KARItemName.AR_REWARD_FILLER_BOX_5: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 544, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_NEBULA_BELT: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 545, _AR
    ),
    # Checklist Rewards — Top Ride (550-582)
    KARItemName.TR_REWARD_GREEN_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 550, _TR),
    KARItemName.TR_REWARD_PURPLE_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 551, _TR),
    KARItemName.TR_REWARD_DIAGONAL_CAMERA_RULE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 552, _TR
    ),
    KARItemName.TR_REWARD_MYSTERY_ITEM_SET_RULE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 553, _TR
    ),
    KARItemName.TR_REWARD_LANTERN_ITEM: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 554, _TR),
    KARItemName.TR_REWARD_WHO_PAINT_ITEM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 555, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_1: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 556, _TR),
    KARItemName.TR_REWARD_CHICKIE_ITEM: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 557, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_GRASS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 558, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_GRASS: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 559, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_SAND: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 560, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_2: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 561, _TR),
    KARItemName.TR_REWARD_BROWN_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 562, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_SKY: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 563, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_FIRE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 564, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_3: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 565, _TR),
    KARItemName.TR_REWARD_MUSIC_FIRE: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 566, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_WATER: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 567, _TR
    ),
    KARItemName.TR_REWARD_DEVICE_QUANTITY_RULE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 568, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_WATER: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 569, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_LIGHT: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 570, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_4: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 571, _TR),
    KARItemName.TR_REWARD_MUSIC_METAL: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 572, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_METAL: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 573, _TR
    ),
    KARItemName.TR_REWARD_WHITE_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 574, _TR),
    KARItemName.TR_REWARD_FILLER_BOX_5: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 575, _TR),
    KARItemName.TR_REWARD_MUSIC_SAND: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 576, _TR),
    KARItemName.TR_REWARD_MUSIC_LIGHT: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 577, _TR),
    KARItemName.TR_REWARD_ATTACK_ITEM_SET_RULE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 578, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_RESULTS_SCREEN: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 579, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_SKY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 580, _TR),
    KARItemName.TR_REWARD_SIDE_CAMERA_RULE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 581, _TR
    ),
    KARItemName.TR_REWARD_ENDING: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 582, _TR),
    # Checklist Rewards — City Trial (600-643)
    KARItemName.CT_REWARD_FILLER_BOX_1: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 600, _CT),
    KARItemName.CT_REWARD_SOUND_TEST_ITEM_BOUNCE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 601, _CT
    ),
    KARItemName.CT_REWARD_PAUSE_SCREEN_POWERUPS: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 602, _CT
    ),
    KARItemName.CT_REWARD_MUSIC_CITY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 603, _CT),
    KARItemName.CT_REWARD_SOUND_TEST_LEGENDARY_MACHINE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 604, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_DENSE_FOG: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 605, _CT
    ),
    KARItemName.CT_REWARD_META_KNIGHT_FREE_RUN: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 606, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_CITY_TRIAL: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 607, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_2: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 608, _CT),
    KARItemName.CT_REWARD_SINGLE_RACE_NEBULA_STADIUM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 609, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_ROWDY_CHARGE_TANK: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 610, _CT
    ),
    KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 611, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_DRAG_RACE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 612, _CT
    ),
    KARItemName.CT_REWARD_DRAGOON_PART_A: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 613, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_TARGET_FLIGHT: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 614, _CT
    ),
    KARItemName.CT_REWARD_DRAGOON_PART_C: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 615, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_AIR_GLIDER: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 616, _CT
    ),
    KARItemName.CT_REWARD_DESTRUCTION_DERBY_4_STADIUM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 617, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_3: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 618, _CT),
    KARItemName.CT_REWARD_HYDRA_PART_Y: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 619, _CT),
    KARItemName.CT_REWARD_SOUND_TEST_WHATS_IN_THE_BOX: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 620, _CT
    ),
    KARItemName.CT_REWARD_HYDRA_PART_Z: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 621, _CT),
    KARItemName.CT_REWARD_KING_DEDEDE_FREE_RUN: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 622, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_DYNA_BLADE_INTRO: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 623, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_4: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 624, _CT),
    KARItemName.CT_REWARD_SOUND_TEST_HUGE_PILLAR: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 625, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_TAC_CHALLENGE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 626, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_FLYING_METEOR: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 627, _CT
    ),
    KARItemName.CT_REWARD_ENDING: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 628, _CT),
    KARItemName.CT_REWARD_DRAGOON_PART_B: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 629, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_5: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 630, _CT),
    KARItemName.CT_REWARD_HYDRA_PART_X: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 631, _CT),
    KARItemName.CT_REWARD_PURPLE_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 632, _CT),
    KARItemName.CT_REWARD_DESTRUCTION_DERBY_3_STADIUM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 633, _CT
    ),
    KARItemName.CT_REWARD_DESTRUCTION_DERBY_5_STADIUM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 634, _CT
    ),
    KARItemName.CT_REWARD_KIRBY_MELEE_2_STADIUM: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 635, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_KIRBY_MELEE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 636, _CT
    ),
    KARItemName.CT_REWARD_GREEN_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 637, _CT),
    KARItemName.CT_REWARD_BROWN_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 638, _CT),
    KARItemName.CT_REWARD_DRAGOON_FREE_RUN: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 639, _CT
    ),
    KARItemName.CT_REWARD_HYDRA_FREE_RUN: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.useful, 640, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_LIGHTHOUSE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 641, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_STATION_FIRE: KARItemData(
        KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 642, _CT
    ),
    KARItemName.CT_REWARD_WHITE_KIRBY: KARItemData(KARItemType.CHECKLIST_REWARD, ItemClassification.filler, 643, _CT),
    # Event Unlocks (700-715)
    # Gate whether City Trial events can occur naturally during gameplay.
    KARItemName.UNLOCK_EVENT_DYNA_BLADE: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 700, _CT
    ),
    KARItemName.UNLOCK_EVENT_TAC: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 701, _CT),
    KARItemName.UNLOCK_EVENT_METEOR: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 702, _CT),
    KARItemName.UNLOCK_EVENT_PILLAR: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 703, _CT),
    KARItemName.UNLOCK_EVENT_RUN_AMOK: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 704, _CT),
    KARItemName.UNLOCK_EVENT_RESTORATION_AREA: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 705, _CT
    ),
    KARItemName.UNLOCK_EVENT_RAIL_FIRE: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 706, _CT),
    KARItemName.UNLOCK_EVENT_SAME_ITEM: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 707, _CT),
    KARItemName.UNLOCK_EVENT_LIGHTHOUSE: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 708, _CT
    ),
    KARItemName.UNLOCK_EVENT_SECRET_CHAMBER: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 709, _CT
    ),
    KARItemName.UNLOCK_EVENT_PREDICTION: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 710, _CT
    ),
    KARItemName.UNLOCK_EVENT_MACHINE_FORMATION: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 711, _CT
    ),
    KARItemName.UNLOCK_EVENT_UFO: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 712, _CT),
    KARItemName.UNLOCK_EVENT_BOUNCE: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 713, _CT),
    KARItemName.UNLOCK_EVENT_FOG: KARItemData(KARItemType.EVENT_UNLOCK, ItemClassification.progression, 714, _CT),
    KARItemName.UNLOCK_EVENT_FAKE_POWERUPS: KARItemData(
        KARItemType.EVENT_UNLOCK, ItemClassification.progression, 715, _CT
    ),
    # Copy Ability Unlocks (760-770)
    # Gate whether copy abilities can appear in the game world.
    KARItemName.UNLOCK_ABILITY_FIRE: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 760, _ALL_MODES
    ),
    KARItemName.UNLOCK_ABILITY_WHEEL: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 761, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_SLEEP: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 762, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_SWORD: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 763, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_BOMB: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 764, _ALL_MODES
    ),
    KARItemName.UNLOCK_ABILITY_PLASMA: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 765, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_NEEDLE: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 766, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_MIC: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 767, _ALL_MODES
    ),
    KARItemName.UNLOCK_ABILITY_ICE: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 768, _ALL_MODES
    ),
    KARItemName.UNLOCK_ABILITY_TORNADO: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 769, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_WING: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 770, _AR_CT
    ),
    # Patch Type Unlocks (780-788)
    # Gate whether specific patch stat types can appear as in-game items.
    KARItemName.UNLOCK_PATCH_WEIGHT: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 780, _CT),
    KARItemName.UNLOCK_PATCH_ACCEL: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 781, _CT),
    KARItemName.UNLOCK_PATCH_TOP_SPEED: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 782, _CT),
    KARItemName.UNLOCK_PATCH_TURN: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 783, _CT),
    KARItemName.UNLOCK_PATCH_CHARGE: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 784, _CT),
    KARItemName.UNLOCK_PATCH_GLIDE: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 785, _CT),
    KARItemName.UNLOCK_PATCH_OFFENSE: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 786, _CT),
    KARItemName.UNLOCK_PATCH_DEFENSE: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 787, _CT),
    KARItemName.UNLOCK_PATCH_HP: KARItemData(KARItemType.PATCH_UNLOCK, ItemClassification.progression, 788, _CT),
    # Item Unlocks (790-819)
    # Gate whether specific items can appear in the game world.
    KARItemName.UNLOCK_ITEM_ALL_UP: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 790, _CT),
    KARItemName.UNLOCK_ITEM_SPEED_MAX: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 791, _CT),
    KARItemName.UNLOCK_ITEM_SPEED_MIN: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 792, _CT),
    KARItemName.UNLOCK_ITEM_OFFENSE_MAX: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 793, _CT),
    KARItemName.UNLOCK_ITEM_DEFENSE_MAX: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 794, _CT),
    KARItemName.UNLOCK_ITEM_CHARGE_MAX: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 795, _CT),
    KARItemName.UNLOCK_ITEM_CHARGE_NONE: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 796, _CT),
    KARItemName.UNLOCK_ITEM_CANDY: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 797, _CT),
    KARItemName.UNLOCK_ITEM_MAXIM_TOMATO: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 798, _CT
    ),
    KARItemName.UNLOCK_ITEM_ENERGY_DRINK: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 799, _CT
    ),
    KARItemName.UNLOCK_ITEM_ICE_CREAM: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 800, _CT),
    KARItemName.UNLOCK_ITEM_RICE_BALL: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 801, _CT),
    KARItemName.UNLOCK_ITEM_CHICKEN: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 802, _CT),
    KARItemName.UNLOCK_ITEM_CURRY: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 803, _CT),
    KARItemName.UNLOCK_ITEM_RAMEN: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 804, _CT),
    KARItemName.UNLOCK_ITEM_OMELET: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 805, _CT),
    KARItemName.UNLOCK_ITEM_HAMBURGER: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 806, _CT),
    KARItemName.UNLOCK_ITEM_SUSHI: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 807, _CT),
    KARItemName.UNLOCK_ITEM_HOT_DOG: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 808, _CT),
    KARItemName.UNLOCK_ITEM_APPLE: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 809, _CT),
    KARItemName.UNLOCK_ITEM_FIREWORKS: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 810, _CT),
    KARItemName.UNLOCK_ITEM_PANIC_SPIN: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 811, _CT),
    KARItemName.UNLOCK_ITEM_SENSOR_BOMB: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 812, _CT),
    KARItemName.UNLOCK_ITEM_GORDO: KARItemData(KARItemType.ITEM_UNLOCK, ItemClassification.progression, 813, _CT),
    KARItemName.UNLOCK_ITEM_HYDRA_PART_1: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 814, _CT
    ),
    KARItemName.UNLOCK_ITEM_HYDRA_PART_2: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 815, _CT
    ),
    KARItemName.UNLOCK_ITEM_HYDRA_PART_3: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 816, _CT
    ),
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_1: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 817, _CT
    ),
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_2: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 818, _CT
    ),
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_3: KARItemData(
        KARItemType.ITEM_UNLOCK, ItemClassification.progression, 819, _CT
    ),
    # Machine Unlocks (830-854)
    # Gate whether specific air ride machines can be ridden. VCKIND_WHEELVSDEDEDE
    # (would be 855) is intentionally excluded — CPU-only stadium machine.
    KARItemName.UNLOCK_MACHINE_WARP_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 830, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_COMPACT_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 831, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WINGED_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 832, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_SHADOW_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 833, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_HYDRA: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 834, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_BULK_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 835, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_SLICK_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 836, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_FORMULA_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 837, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_DRAGOON: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 838, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WAGON_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 839, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_ROCKET_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 840, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_SWERVE_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 841, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_TURBO_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 842, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_JET_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 843, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_FLIGHT_WARP_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 844, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_FREE_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 845, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_STEER_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 846, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WING_KIRBY: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 847, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 848, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WHEELIE: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 849, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WHEELIE_KIRBY: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 850, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WHEELIE_BIKE: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 851, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_REX_WHEELIE: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 852, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WHEELIE_SCOOTER: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 853, _AR_CT
    ),
    KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 854, _AR_CT
    ),
    # Box Unlocks (860-862)
    # Gate whether specific box colors can appear in-game.
    KARItemName.UNLOCK_BOX_BLUE: KARItemData(KARItemType.BOX_UNLOCK, ItemClassification.progression, 860, _CT),
    KARItemName.UNLOCK_BOX_GREEN: KARItemData(KARItemType.BOX_UNLOCK, ItemClassification.progression, 861, _CT),
    KARItemName.UNLOCK_BOX_RED: KARItemData(KARItemType.BOX_UNLOCK, ItemClassification.progression, 862, _CT),
    # Air Ride Course Unlocks (870-878)
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 870, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 871, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 872, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 873, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 874, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 875, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 876, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 877, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT: KARItemData(
        KARItemType.STAGE_UNLOCK, ItemClassification.progression, 878, _AR
    ),
    # Kirby Color Unlocks (880-887)
    KARItemName.UNLOCK_COLOR_PINK: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 880, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_YELLOW: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 881, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_BLUE: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 882, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_RED: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 883, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_GREEN: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 884, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_PURPLE: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 885, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_BROWN: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 886, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_WHITE: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression, 887, _ALL_MODES
    ),
    # Top Ride Course Unlocks (890-896)
    KARItemName.UNLOCK_TR_COURSE_GRASS: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 890, _TR),
    KARItemName.UNLOCK_TR_COURSE_SAND: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 891, _TR),
    KARItemName.UNLOCK_TR_COURSE_SKY: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 892, _TR),
    KARItemName.UNLOCK_TR_COURSE_FIRE: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 893, _TR),
    KARItemName.UNLOCK_TR_COURSE_LIGHT: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 894, _TR),
    KARItemName.UNLOCK_TR_COURSE_WATER: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 895, _TR),
    KARItemName.UNLOCK_TR_COURSE_METAL: KARItemData(KARItemType.STAGE_UNLOCK, ItemClassification.progression, 896, _TR),
    # Top Ride Item Unlocks (900-921, minus 5 reserved slots).
    # IDs 909/911/913/916 (Freeze Fan/Fire/Bomb/Walky) are gated by the
    # ability_unlocked_mask in the mod, not by topride_item_unlocked_mask, so
    # they intentionally have no unlock-item form. The corresponding ability
    # unlock (760-770 range) serves as the gate.
    # ID 912 is the engine's KirbyKusdama Party Ball variant — the visible
    # Party Ball at slot 21 (921) is the single AP item, and the mod sets
    # bit 12 alongside bit 21 so both engine variants can spawn.
    KARItemName.UNLOCK_TR_ITEM_HAMMER: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 900, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_BIG_CAKE: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 901, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SPEED_UP: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 902, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SPEED_DOWN: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 903, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SPINNER: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 904, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_CHARGE_TANK: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 905, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 906, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 907, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_DRILL: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 908, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_MISSILE: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 910, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_STEP_BOOM: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 914, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_LANTERN: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 915, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_KRACKO: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 917, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_WHO_PAINT: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 918, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SMOKESCREEN: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 919, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_CHICKIE: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 920, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_PARTY_BALL: KARItemData(
        KARItemType.TOPRIDE_ITEM_UNLOCK, ItemClassification.progression, 921, _TR
    ),
    # Top Ride Item Gives (950-971)
    # Spawn the matching TR item at every human Kirby's position. Only effective
    # in a Top Ride scene; queued until the player is in one.
    KARItemName.GIVE_TR_ITEM_HAMMER: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 950, _TR),
    KARItemName.GIVE_TR_ITEM_BIG_CAKE: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 951, _TR),
    KARItemName.GIVE_TR_ITEM_SPEED_UP: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 952, _TR),
    KARItemName.GIVE_TR_ITEM_SPEED_DOWN: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.trap, 953, _TR),
    KARItemName.GIVE_TR_ITEM_SPINNER: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 954, _TR),
    KARItemName.GIVE_TR_ITEM_CHARGE_TANK: KARItemData(
        KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 955, _TR
    ),
    KARItemName.GIVE_TR_ITEM_INVINCIBLE_CANDY: KARItemData(
        KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 956, _TR
    ),
    KARItemName.GIVE_TR_ITEM_BUZZ_SAW: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 957, _TR),
    KARItemName.GIVE_TR_ITEM_DRILL: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 958, _TR),
    KARItemName.GIVE_TR_ITEM_FREEZE_FAN: KARItemData(
        KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 959, _TR
    ),
    KARItemName.GIVE_TR_ITEM_MISSILE: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 960, _TR),
    KARItemName.GIVE_TR_ITEM_FIRE: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 961, _TR),
    KARItemName.GIVE_TR_ITEM_BOMB: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 963, _TR),
    KARItemName.GIVE_TR_ITEM_STEP_BOOM: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 964, _TR),
    KARItemName.GIVE_TR_ITEM_LANTERN: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 965, _TR),
    KARItemName.GIVE_TR_ITEM_WALKY: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 966, _TR),
    KARItemName.GIVE_TR_ITEM_KRACKO: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 967, _TR),
    KARItemName.GIVE_TR_ITEM_WHO_PAINT: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 968, _TR),
    KARItemName.GIVE_TR_ITEM_SMOKESCREEN: KARItemData(
        KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 969, _TR
    ),
    KARItemName.GIVE_TR_ITEM_CHICKIE: KARItemData(KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 970, _TR),
    KARItemName.GIVE_TR_ITEM_PARTY_BALL: KARItemData(
        KARItemType.TOPRIDE_ITEM_GIVE, ItemClassification.filler, 971, _TR
    ),
    # Goal Events (no network code — internal AP events only)
    KARItemName.CITY_TRIAL_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
    KARItemName.AIR_RIDE_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
    KARItemName.TOP_RIDE_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
}


# STADIUM UNLOCK ITEMS
# Ordered tuple of all stadium unlock item names. Used to build mappings
# and for iterating over stadium unlocks in __init__.py.
STADIUM_UNLOCK_ITEMS: tuple[KARItemName, ...] = tuple(
    KARItemName(name) for name, data in ITEM_TABLE.items() if data.type == KARItemType.STADIUM_UNLOCK
)

# Stadium unlock items that have equivalent checklist reward items.
# When progressive stadiums is ON, these unlock items are excluded and the
# checklist rewards serve as the progression items for those stadiums instead.
STADIUM_UNLOCK_TO_CHECKLIST_REWARD: dict[KARItemName, KARItemName] = {
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_4: KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM,
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3: KARItemName.CT_REWARD_DESTRUCTION_DERBY_3_STADIUM,
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4: KARItemName.CT_REWARD_DESTRUCTION_DERBY_4_STADIUM,
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5: KARItemName.CT_REWARD_DESTRUCTION_DERBY_5_STADIUM,
    KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2: KARItemName.CT_REWARD_KIRBY_MELEE_2_STADIUM,
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_9: KARItemName.CT_REWARD_SINGLE_RACE_NEBULA_STADIUM,
}


# Checklist rewards that overlap with gating unlock items.
# When a gating option is ON, the corresponding UNLOCK items handle the functionality,
# so these checklist rewards should be excluded from the pool to avoid duplication.
# When gating is OFF, these rewards stay in the pool and handle unlocks via vanilla systems.
GATED_CHECKLIST_REWARDS: dict[str, frozenset[KARItemName]] = {
    "machines_gated": frozenset(
        {
            KARItemName.AR_REWARD_WAGON_STAR,
            KARItemName.AR_REWARD_REX_WHEELIE,
            KARItemName.AR_REWARD_SLICK_STAR,
            KARItemName.AR_REWARD_SWERVE_STAR,
            KARItemName.AR_REWARD_SHADOW_STAR,
            KARItemName.AR_REWARD_JET_STAR,
            KARItemName.AR_REWARD_BULK_STAR,
            KARItemName.AR_REWARD_FORMULA_STAR,
            KARItemName.AR_REWARD_ROCKET_STAR,
            KARItemName.AR_REWARD_WHEELIE_BIKE,
            KARItemName.AR_REWARD_WHEELIE_SCOOTER,
            KARItemName.AR_REWARD_WINGED_STAR,
            KARItemName.AR_REWARD_TURBO_STAR,
            KARItemName.AR_REWARD_META_KNIGHT,
            KARItemName.AR_REWARD_KING_DEDEDE,
            KARItemName.CT_REWARD_META_KNIGHT_FREE_RUN,
            KARItemName.CT_REWARD_KING_DEDEDE_FREE_RUN,
            KARItemName.CT_REWARD_DRAGOON_FREE_RUN,
            KARItemName.CT_REWARD_HYDRA_FREE_RUN,
        }
    ),
    "colors_gated": frozenset(
        {
            KARItemName.AR_REWARD_GREEN_KIRBY,
            KARItemName.AR_REWARD_PURPLE_KIRBY,
            KARItemName.AR_REWARD_WHITE_KIRBY,
            KARItemName.AR_REWARD_BROWN_KIRBY,
            KARItemName.TR_REWARD_GREEN_KIRBY,
            KARItemName.TR_REWARD_PURPLE_KIRBY,
            KARItemName.TR_REWARD_BROWN_KIRBY,
            KARItemName.TR_REWARD_WHITE_KIRBY,
            KARItemName.CT_REWARD_PURPLE_KIRBY,
            KARItemName.CT_REWARD_GREEN_KIRBY,
            KARItemName.CT_REWARD_BROWN_KIRBY,
            KARItemName.CT_REWARD_WHITE_KIRBY,
        }
    ),
    "air_ride_courses_gated": frozenset(
        {
            KARItemName.AR_REWARD_NEBULA_BELT_COURSE,
        }
    ),
    "top_ride_items_gated": frozenset(
        {
            KARItemName.TR_REWARD_LANTERN_ITEM,
            KARItemName.TR_REWARD_WHO_PAINT_ITEM,
            KARItemName.TR_REWARD_CHICKIE_ITEM,
        }
    ),
}


# TRAP WEIGHT GROUPS
# Maps a KAROptions attribute name to the set of trap item names whose weight
# is controlled by that option. Used in __init__.py to look up per-item weights
# when filling the junk/trap pool.
TRAP_WEIGHT_GROUPS: list[tuple[str, frozenset[str]]] = [
    (
        "trap_weight_direct_damage",
        frozenset(
            {
                KARItemName.ONE_HP_TRAP,
            }
        ),
    ),
    (
        "trap_weight_stat_debuff",
        frozenset(
            {
                KARItemName.ALL_DOWN,
                KARItemName.ACCEL_DOWN_PATCH,
                KARItemName.TOP_SPEED_DOWN_PATCH,
                KARItemName.OFFENSE_DOWN_PATCH,
                KARItemName.DEFENSE_DOWN_PATCH,
                KARItemName.TURN_DOWN_PATCH,
                KARItemName.GLIDE_DOWN_PATCH,
                KARItemName.CHARGE_DOWN_PATCH,
                KARItemName.WEIGHT_DOWN_PATCH,
                KARItemName.SPEED_MIN_PATCH,
                KARItemName.CHARGE_NONE_PATCH,
                KARItemName.DROP_PATCHES_TRAP,
                KARItemName.COPY_ABILITY_SLEEP,
                KARItemName.GIVE_TR_ITEM_SPEED_DOWN,
            }
        ),
    ),
    (
        "trap_weight_fake_patches",
        frozenset(
            {
                KARItemName.FAKE_ACCEL_PATCH,
                KARItemName.FAKE_TOP_SPEED_PATCH,
                KARItemName.FAKE_OFFENSE_PATCH,
                KARItemName.FAKE_DEFENSE_PATCH,
                KARItemName.FAKE_TURN_PATCH,
                KARItemName.FAKE_GLIDE_PATCH,
                KARItemName.FAKE_CHARGE_PATCH,
                KARItemName.FAKE_WEIGHT_PATCH,
            }
        ),
    ),
    (
        "trap_weight_hazards",
        frozenset(
            {
                KARItemName.PANIC_SPIN,
                KARItemName.SENSOR_BOMB,
                KARItemName.GORDO,
            }
        ),
    ),
]


# ITEM NAME GROUPS
# Auto-generated from ITEM_TABLE by type, plus mode-specific sub-groups.
# Players can reference these in YAML configs (e.g., exclude_locations, priority_locations).
_TYPE_TO_GROUP: dict[KARItemType, str] = {
    KARItemType.CHECKBOX_FILLER: "Checkbox Fillers",
    KARItemType.PATCH_CAP_INCREASE: "Patch Cap Increases",
    KARItemType.PERMANENT_PATCH: "Permanent Patches",
    KARItemType.TRAP: "Traps",
    KARItemType.EFFECT: "Effects",
    KARItemType.EVENT_TRIGGER: "Event Triggers",
    KARItemType.GAME_ITEM: "Game Items",
    KARItemType.STADIUM_UNLOCK: "Stadium Unlocks",
    KARItemType.CHECKLIST_REWARD: "Checklist Rewards",
    KARItemType.EVENT_UNLOCK: "Event Unlocks",
    KARItemType.ABILITY_UNLOCK: "Copy Ability Unlocks",
    KARItemType.PATCH_UNLOCK: "Patch Type Unlocks",
    KARItemType.ITEM_UNLOCK: "Item Unlocks",
    KARItemType.MACHINE_UNLOCK: "Machine Unlocks",
    KARItemType.BOX_UNLOCK: "Box Unlocks",
    KARItemType.STAGE_UNLOCK: "Stage Unlocks",
    KARItemType.COLOR_UNLOCK: "Color Unlocks",
    KARItemType.TOPRIDE_ITEM_UNLOCK: "Top Ride Item Unlocks",
    KARItemType.TOPRIDE_ITEM_GIVE: "Top Ride Item Gives",
}

item_name_groups: dict[str, set[str]] = {}
for _name, _data in ITEM_TABLE.items():
    _group = _TYPE_TO_GROUP.get(_data.type)
    if _group:
        item_name_groups.setdefault(_group, set()).add(_name)

# Mode-specific sub-groups for checklist rewards
item_name_groups["Air Ride Rewards"] = {n for n in ITEM_TABLE if n.startswith("Air Ride Reward:")}
item_name_groups["Top Ride Rewards"] = {n for n in ITEM_TABLE if n.startswith("Top Ride Reward:")}
item_name_groups["City Trial Rewards"] = {n for n in ITEM_TABLE if n.startswith("City Trial Reward:")}

# Mode-specific sub-groups for course unlocks
item_name_groups["AR Course Unlocks"] = {n for n in ITEM_TABLE if n.startswith("Unlock AR Course:")}
item_name_groups["TR Course Unlocks"] = {n for n in ITEM_TABLE if n.startswith("Unlock TR Course:")}
