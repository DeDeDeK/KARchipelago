from enum import StrEnum
from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .KARData import GameMode, RewardType


class KARItemType(StrEnum):
    """Categories of items in Kirby Air Ride. Each type maps to distinct pool-building behavior."""

    # Meta/progression items
    CHECKBOX_FILLER = "Checkbox Filler"
    PATCH_CAP_INCREASE = "Patch Cap Increase"
    PERMANENT_PATCH = "Permanent Patch"
    SPAWN_RATE = "Spawn Rate"

    # Give items: the mod spawns/applies the game thing on receipt.
    # Trap-ness is carried by ItemClassification.trap, not by a separate type.
    CT_ITEM_GIVE = "City Trial Item Give"
    CT_EVENT_GIVE = "City Trial Event Give"
    ABILITY_GIVE = "Copy Ability Give"

    # Unlock items. Single-mode types carry a mode prefix (CT_/AR_/TR_); cross-mode
    # ones (ABILITY/COLOR/MACHINE) stay unprefixed because their items span modes.
    CT_STADIUM_UNLOCK = "City Trial Stadium Unlock"
    CT_EVENT_UNLOCK = "City Trial Event Unlock"
    CT_PATCH_UNLOCK = "City Trial Patch Type Unlock"
    CT_ITEM_UNLOCK = "City Trial Item Unlock"
    CT_BOX_UNLOCK = "City Trial Box Unlock"
    AR_COURSE_UNLOCK = "Air Ride Course Unlock"
    TR_COURSE_UNLOCK = "Top Ride Course Unlock"
    TR_ITEM_UNLOCK = "Top Ride Item Unlock"
    ABILITY_UNLOCK = "Copy Ability Unlock"
    BASE_ABILITY_UNLOCK = "Base Ability Unlock"
    MACHINE_UNLOCK = "Machine Unlock"
    COLOR_UNLOCK = "Color Unlock"

    # Top Ride item give: spawns the item at human Kirby positions (Top Ride scene only)
    TR_ITEM_GIVE = "Top Ride Item Give"

    # Cosmetic all-mode filler. Outside the allowed_items categories so it can never be removed.
    FILLER = "Filler"

    # Checklist rewards (the vanilla rewards for completing checklist entries). Single-mode, so prefixed.
    CT_CHECKLIST_REWARD = "City Trial Checklist Reward"
    AR_CHECKLIST_REWARD = "Air Ride Checklist Reward"
    TR_CHECKLIST_REWARD = "Top Ride Checklist Reward"

    # Internal (event items with no network code)
    GOAL = "Goal"
    AP_PATCH_GROUP = "AP Patch Group"


class KARItemGroup(StrEnum):
    """Player-facing item-group names. Reference these members instead of hardcoding the strings (YAML
    configs must match the values verbatim). Most map 1:1 from a KARItemType via _TYPE_TO_GROUP; TRAPS
    is classification-derived."""

    CHECKBOX_FILLERS = "Checkbox Fillers"
    PATCH_CAP_INCREASES = "Patch Cap Increases"
    PERMANENT_PATCHES = "Permanent Patches"
    SPAWN_RATES = "Spawn Rates"
    CT_ITEM_GIVES = "City Trial Item Gives"
    CT_EVENT_GIVES = "City Trial Event Gives"
    ABILITY_GIVES = "Copy Ability Gives"
    TR_ITEM_GIVES = "Top Ride Item Gives"
    CT_STADIUM_UNLOCKS = "City Trial Stadium Unlocks"
    CT_EVENT_UNLOCKS = "City Trial Event Unlocks"
    CT_PATCH_UNLOCKS = "City Trial Patch Type Unlocks"
    CT_ITEM_UNLOCKS = "City Trial Item Unlocks"
    CT_BOX_UNLOCKS = "City Trial Box Unlocks"
    AR_COURSE_UNLOCKS = "Air Ride Course Unlocks"
    TR_COURSE_UNLOCKS = "Top Ride Course Unlocks"
    TR_ITEM_UNLOCKS = "Top Ride Item Unlocks"
    ABILITY_UNLOCKS = "Copy Ability Unlocks"
    BASE_ABILITY_UNLOCKS = "Base Ability Unlocks"
    MACHINE_UNLOCKS = "Machine Unlocks"
    COLOR_UNLOCKS = "Color Unlocks"
    CT_REWARDS = "City Trial Rewards"
    AR_REWARDS = "Air Ride Rewards"
    TR_REWARDS = "Top Ride Rewards"
    FILLER_ITEMS = "Filler Items"
    TRAPS = "Traps"


class KARItemName(StrEnum):
    """Canonical item names for Kirby Air Ride. Single source of truth for all item name strings."""

    # Standalone Items (1-14)
    CHECKBOX_FILLER_AIR_RIDE = "Checkbox Filler (Air Ride)"
    CHECKBOX_FILLER_TOP_RIDE = "Checkbox Filler (Top Ride)"
    CHECKBOX_FILLER_CITY_TRIAL = "Checkbox Filler (City Trial)"
    CHECKBOX_FILLER_ARCHIPELAGO = "Checkbox Filler (Archipelago)"
    PATCH_CAP_INCREASE = "Patch Cap Increase"
    ONE_HP_TRAP = "1 HP Trap"
    ALL_UP = "All Up"
    PERMANENT_ALL_UP = "Permanent All Up"
    ALL_DOWN = "All Down"
    GIVE_DRAGOON = "Give Dragoon"
    GIVE_HYDRA = "Give Hydra"
    SPAWN_RATE_UP = "Spawn Rate Up"
    DROP_PATCHES_TRAP = "Drop Patches Trap"
    GIVE_ARCHIPELAGO_STAR = "Give Archipelago Star"

    # Permanent +1 Patches (100-108)
    PERMANENT_WEIGHT_UP = "Permanent Weight Up"
    PERMANENT_BOOST_UP = "Permanent Boost Up"
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

    # Direct Game Items: Boxes (300-302)
    BLUE_BOX = "Blue Box"
    GREEN_BOX = "Green Box"
    RED_BOX = "Red Box"

    # Direct Game Items: Stat Patches Up (303-320)
    BOOST_PATCH = "Boost Patch"
    TOP_SPEED_PATCH = "Top Speed Patch"
    OFFENSE_PATCH = "Offense Patch"
    DEFENSE_PATCH = "Defense Patch"
    TURN_PATCH = "Turn Patch"
    GLIDE_PATCH = "Glide Patch"
    CHARGE_PATCH = "Charge Patch"
    WEIGHT_PATCH = "Weight Patch"
    HP_PATCH = "HP Patch"
    ALL_UP_PATCH = "All Up Patch"

    # Direct Game Items: Stat Patches Down (304-318)
    BOOST_DOWN_PATCH = "Boost Down Patch"
    TOP_SPEED_DOWN_PATCH = "Top Speed Down Patch"
    OFFENSE_DOWN_PATCH = "Offense Down Patch"
    DEFENSE_DOWN_PATCH = "Defense Down Patch"
    TURN_DOWN_PATCH = "Turn Down Patch"
    GLIDE_DOWN_PATCH = "Glide Down Patch"
    CHARGE_DOWN_PATCH = "Charge Down Patch"
    WEIGHT_DOWN_PATCH = "Weight Down Patch"

    # Direct Game Items: Extreme Stat Patches (321-326)
    SPEED_MAX_PATCH = "Speed Max Patch"
    SPEED_MIN_PATCH = "Speed Min Patch"
    OFFENSE_MAX_PATCH = "Offense Max Patch"
    DEFENSE_MAX_PATCH = "Defense Max Patch"
    CHARGE_MAX_PATCH = "Charge Max Patch"
    CHARGE_NONE_PATCH = "Charge None Patch"

    # Direct Game Items: Special (327)
    CANDY = "Candy"

    # Direct Game Items: Copy Abilities (328-338)
    COPY_ABILITY_BOMB = "Copy Ability: Bomb"
    COPY_ABILITY_FIRE = "Copy Ability: Fire"
    COPY_ABILITY_FREEZE = "Copy Ability: Freeze"
    COPY_ABILITY_SLEEP = "Copy Ability: Sleep"
    COPY_ABILITY_WHEEL = "Copy Ability: Wheel"
    COPY_ABILITY_WING = "Copy Ability: Wing"
    COPY_ABILITY_PLASMA = "Copy Ability: Plasma"
    COPY_ABILITY_TORNADO = "Copy Ability: Tornado"
    COPY_ABILITY_SWORD = "Copy Ability: Sword"
    COPY_ABILITY_NEEDLE = "Copy Ability: Needle"
    COPY_ABILITY_MIC = "Copy Ability: Mic"

    # Direct Game Items: Food (339-350)
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

    # Direct Game Items: miscellaneous (351-354)
    FIREWORKS = "Fireworks"
    PANIC_SPIN = "Panic Spin"
    SENSOR_BOMB = "Sensor Bomb"
    GORDO = "Gordo"

    # Direct Game Items: Legendary Machine Parts (355-360)
    HYDRA_PART_X = "Hydra Part X"
    HYDRA_PART_Y = "Hydra Part Y"
    HYDRA_PART_Z = "Hydra Part Z"
    DRAGOON_PART_A = "Dragoon Part A"
    DRAGOON_PART_B = "Dragoon Part B"
    DRAGOON_PART_C = "Dragoon Part C"

    # Direct Game Items: Fake Patches (361-368)
    FAKE_BOOST_PATCH = "Fake Boost Patch"
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

    # Checklist Rewards: Air Ride (500-545)
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

    # Checklist Rewards: Top Ride (550-582)
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

    # Checklist Rewards: City Trial (600-643)
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
    UNLOCK_ABILITY_FIRE = "Unlock Copy Ability: Fire"
    UNLOCK_ABILITY_WHEEL = "Unlock Copy Ability: Wheel"
    UNLOCK_ABILITY_SLEEP = "Unlock Copy Ability: Sleep"
    UNLOCK_ABILITY_SWORD = "Unlock Copy Ability: Sword"
    UNLOCK_ABILITY_BOMB = "Unlock Copy Ability: Bomb"
    UNLOCK_ABILITY_PLASMA = "Unlock Copy Ability: Plasma"
    UNLOCK_ABILITY_NEEDLE = "Unlock Copy Ability: Needle"
    UNLOCK_ABILITY_MIC = "Unlock Copy Ability: Mic"
    UNLOCK_ABILITY_FREEZE = "Unlock Copy Ability: Freeze"
    UNLOCK_ABILITY_TORNADO = "Unlock Copy Ability: Tornado"
    UNLOCK_ABILITY_WING = "Unlock Copy Ability: Wing"

    # Base Ability Unlocks (771-773)
    UNLOCK_BASE_ABILITY_INHALE = "Unlock Base Ability: Inhale"
    UNLOCK_BASE_ABILITY_QUICK_SPIN = "Unlock Base Ability: Quick Spin"
    UNLOCK_BASE_ABILITY_CHARGE = "Unlock Base Ability: Charge"

    # Patch Type Unlocks (780-788)
    UNLOCK_PATCH_WEIGHT = "Unlock Patch: Weight"
    UNLOCK_PATCH_BOOST = "Unlock Patch: Boost"
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
    UNLOCK_ITEM_HYDRA_PART_X = "Unlock Item: Hydra Part X"
    UNLOCK_ITEM_HYDRA_PART_Y = "Unlock Item: Hydra Part Y"
    UNLOCK_ITEM_HYDRA_PART_Z = "Unlock Item: Hydra Part Z"
    UNLOCK_ITEM_DRAGOON_PART_A = "Unlock Item: Dragoon Part A"
    UNLOCK_ITEM_DRAGOON_PART_B = "Unlock Item: Dragoon Part B"
    UNLOCK_ITEM_DRAGOON_PART_C = "Unlock Item: Dragoon Part C"

    # Archipelago Star sphere unlocks (820-825). The six assembly pieces, gated one per item like the
    # Hydra and Dragoon parts. The machine unlock at 856 is separate.
    UNLOCK_ITEM_AP_SPHERE_ROSE = "Unlock Item: Archipelago Sphere (Rose)"
    UNLOCK_ITEM_AP_SPHERE_GREEN = "Unlock Item: Archipelago Sphere (Green)"
    UNLOCK_ITEM_AP_SPHERE_VIOLET = "Unlock Item: Archipelago Sphere (Violet)"
    UNLOCK_ITEM_AP_SPHERE_TAN = "Unlock Item: Archipelago Sphere (Tan)"
    UNLOCK_ITEM_AP_SPHERE_BLUE = "Unlock Item: Archipelago Sphere (Blue)"
    UNLOCK_ITEM_AP_SPHERE_YELLOW = "Unlock Item: Archipelago Sphere (Yellow)"

    # Machine Unlocks (830-854, plus the appended 856). 855 VCKIND_WHEELVSDEDEDE excluded: CPU-only,
    # not player-rideable.
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
    UNLOCK_MACHINE_WING_META_KNIGHT = "Unlock Machine: Meta Knight"
    UNLOCK_MACHINE_WHEELIE_BIKE = "Unlock Machine: Wheelie Bike"
    UNLOCK_MACHINE_REX_WHEELIE = "Unlock Machine: Rex Wheelie"
    UNLOCK_MACHINE_WHEELIE_SCOOTER = "Unlock Machine: Wheelie Scooter"
    UNLOCK_MACHINE_WHEELIE_DEDEDE = "Unlock Machine: King Dedede"
    UNLOCK_MACHINE_ARCHIPELAGO_STAR = "Unlock Machine: Archipelago Star"

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
    UNLOCK_COLOR_PINK = "Unlock Kirby Color: Pink"
    UNLOCK_COLOR_YELLOW = "Unlock Kirby Color: Yellow"
    UNLOCK_COLOR_BLUE = "Unlock Kirby Color: Blue"
    UNLOCK_COLOR_RED = "Unlock Kirby Color: Red"
    UNLOCK_COLOR_GREEN = "Unlock Kirby Color: Green"
    UNLOCK_COLOR_PURPLE = "Unlock Kirby Color: Purple"
    UNLOCK_COLOR_BROWN = "Unlock Kirby Color: Brown"
    UNLOCK_COLOR_WHITE = "Unlock Kirby Color: White"

    # Top Ride Course Unlocks (890-896)
    UNLOCK_TR_COURSE_GRASS = "Unlock TR Course: Grass"
    UNLOCK_TR_COURSE_SAND = "Unlock TR Course: Sand"
    UNLOCK_TR_COURSE_SKY = "Unlock TR Course: Sky"
    UNLOCK_TR_COURSE_FIRE = "Unlock TR Course: Fire"
    UNLOCK_TR_COURSE_LIGHT = "Unlock TR Course: Light"
    UNLOCK_TR_COURSE_WATER = "Unlock TR Course: Water"
    UNLOCK_TR_COURSE_METAL = "Unlock TR Course: Metal"

    # Top Ride Item Unlocks (900-921, minus 912: the KirbyKusdama Party Ball, mirrored onto the visible
    # Party Ball at 921). The four ability-themed items (909/911/913/916) also unlock via their ability.
    UNLOCK_TR_ITEM_HAMMER = "Unlock TR Item: Hammer"
    UNLOCK_TR_ITEM_BIG_CAKE = "Unlock TR Item: Big Cake"
    UNLOCK_TR_ITEM_SPEED_UP = "Unlock TR Item: Speed Up"
    UNLOCK_TR_ITEM_SPEED_DOWN = "Unlock TR Item: Speed Down"
    UNLOCK_TR_ITEM_SPINNER = "Unlock TR Item: Spinner"
    UNLOCK_TR_ITEM_CHARGE_TANK = "Unlock TR Item: Charge Tank"
    UNLOCK_TR_ITEM_INVINCIBLE_CANDY = "Unlock TR Item: Invincible Candy"
    UNLOCK_TR_ITEM_BUZZ_SAW = "Unlock TR Item: Buzz Saw"
    UNLOCK_TR_ITEM_DRILL = "Unlock TR Item: Drill"
    UNLOCK_TR_ITEM_FREEZE_FAN = "Unlock TR Item: Freeze Fan"
    UNLOCK_TR_ITEM_MISSILE = "Unlock TR Item: Missile"
    UNLOCK_TR_ITEM_FIRE = "Unlock TR Item: Fire"
    UNLOCK_TR_ITEM_BOMB = "Unlock TR Item: Bomb"
    UNLOCK_TR_ITEM_STEP_BOOM = "Unlock TR Item: Step-boom"
    UNLOCK_TR_ITEM_LANTERN = "Unlock TR Item: Lantern"
    UNLOCK_TR_ITEM_WALKY = "Unlock TR Item: Walky"
    UNLOCK_TR_ITEM_KRACKO = "Unlock TR Item: Kracko"
    UNLOCK_TR_ITEM_WHO_PAINT = "Unlock TR Item: Who? Paint"
    UNLOCK_TR_ITEM_SMOKESCREEN = "Unlock TR Item: Smokescreen"
    UNLOCK_TR_ITEM_CHICKIE = "Unlock TR Item: Chickie"
    UNLOCK_TR_ITEM_PARTY_BALL = "Unlock TR Item: Party Ball"

    # Top Ride Item Gives (950-971). Spawn at each human Kirby's position; queued outside a TR scene.
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

    # Cosmetic all-mode filler (972-973): the mod scales Kirby's model on receipt, in any mode.
    BIG_KIRBY = "Big Kirby"
    SMALL_KIRBY = "Small Kirby"

    # Archipelago Star sphere gives (980-985), in the same ring order as the unlocks.
    GIVE_AP_SPHERE_ROSE = "Give Archipelago Sphere (Rose)"
    GIVE_AP_SPHERE_GREEN = "Give Archipelago Sphere (Green)"
    GIVE_AP_SPHERE_VIOLET = "Give Archipelago Sphere (Violet)"
    GIVE_AP_SPHERE_TAN = "Give Archipelago Sphere (Tan)"
    GIVE_AP_SPHERE_BLUE = "Give Archipelago Sphere (Blue)"
    GIVE_AP_SPHERE_YELLOW = "Give Archipelago Sphere (Yellow)"

    # Goal Events (no network code, internal AP events only)
    CITY_TRIAL_VICTORY = "City Trial Victory"
    AIR_RIDE_VICTORY = "Air Ride Victory"
    TOP_RIDE_VICTORY = "Top Ride Victory"
    ARCHIPELAGO_VICTORY = "Archipelago Victory"

    # AP Patch group events (no network code, internal AP events only). One per group that gates the
    # next, so the last group of a seed has none - nine covers the widest block.
    AP_PATCH_GROUP_1_CLEARED = "AP Patch Group 1 Cleared"
    AP_PATCH_GROUP_2_CLEARED = "AP Patch Group 2 Cleared"
    AP_PATCH_GROUP_3_CLEARED = "AP Patch Group 3 Cleared"
    AP_PATCH_GROUP_4_CLEARED = "AP Patch Group 4 Cleared"
    AP_PATCH_GROUP_5_CLEARED = "AP Patch Group 5 Cleared"
    AP_PATCH_GROUP_6_CLEARED = "AP Patch Group 6 Cleared"
    AP_PATCH_GROUP_7_CLEARED = "AP Patch Group 7 Cleared"
    AP_PATCH_GROUP_8_CLEARED = "AP Patch Group 8 Cleared"
    AP_PATCH_GROUP_9_CLEARED = "AP Patch Group 9 Cleared"


class KARItemData(NamedTuple):
    type: KARItemType
    classification: ItemClassification
    # Matches the mod's APItemId enum. None for event-only items.
    code: int | None
    # Modes the item is meaningful for; empty means mode-neutral. A non-empty set that misses every
    # enabled mode drops the item from the pool. Placement is otherwise unrestricted.
    source_modes: frozenset[GameMode] = frozenset()


# Mode-source aliases: concise tags for ITEM_TABLE rows.
_AR = frozenset({GameMode.AIRRIDE})
_TR = frozenset({GameMode.TOPRIDE})
_CT = frozenset({GameMode.CITYTRIAL})
_AP = frozenset({GameMode.ARCHIPELAGO})
_AR_CT = frozenset({GameMode.AIRRIDE, GameMode.CITYTRIAL})
_AR_CT_AP = frozenset({GameMode.AIRRIDE, GameMode.CITYTRIAL, GameMode.ARCHIPELAGO})
_CT_TR = frozenset({GameMode.CITYTRIAL, GameMode.TOPRIDE})
# Every mode, including the Archipelago checklist: game-wide items (copy abilities, colors, cosmetic
# filler) apply in any scene. The filler must stay all-mode to guarantee a non-empty filler pool.
_ALL_MODES = frozenset({GameMode.AIRRIDE, GameMode.TOPRIDE, GameMode.CITYTRIAL, GameMode.ARCHIPELAGO})


class KARItem(Item):
    """An Archipelago item for Kirby Air Ride. Keeps the base Item constructor signature so it composes
    with helpers like Region.add_event; table-driven items should use KARItem.from_data instead."""

    game: str = "Kirby Air Ride"
    type: KARItemType | None = None  # None for event items (no ITEM_TABLE entry)
    source_modes: frozenset[GameMode] = frozenset()

    @classmethod
    def from_data(cls, name: str, player: int, data: KARItemData) -> "KARItem":
        item = cls(name, data.classification, data.code, player)
        item.type = data.type
        item.source_modes = data.source_modes
        return item


# Master table of all items. Codes match the mod's APItemId enum exactly (the value written to
# Dolphin memory). Pool quantities are determined by options and pool-building logic.

ITEM_TABLE: dict[str, KARItemData] = {
    # Standalone Items (1-14). The 4 checkbox fillers lead, one per checklist mode, in row order.
    KARItemName.CHECKBOX_FILLER_AIR_RIDE: KARItemData(KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 1, _AR),
    KARItemName.CHECKBOX_FILLER_TOP_RIDE: KARItemData(KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 2, _TR),
    KARItemName.CHECKBOX_FILLER_CITY_TRIAL: KARItemData(KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 3, _CT),
    KARItemName.CHECKBOX_FILLER_ARCHIPELAGO: KARItemData(
        KARItemType.CHECKBOX_FILLER, ItemClassification.useful, 4, _AP
    ),
    KARItemName.PATCH_CAP_INCREASE: KARItemData(
        KARItemType.PATCH_CAP_INCREASE, ItemClassification.progression_deprioritized_skip_balancing, 5, _CT
    ),
    KARItemName.ONE_HP_TRAP: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 6, _AR_CT),
    KARItemName.ALL_UP: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 7, _AR_CT),
    KARItemName.PERMANENT_ALL_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 8, _CT),
    KARItemName.ALL_DOWN: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 9, _AR_CT),
    KARItemName.GIVE_DRAGOON: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 10, _CT),
    KARItemName.GIVE_HYDRA: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 11, _CT),
    KARItemName.SPAWN_RATE_UP: KARItemData(KARItemType.SPAWN_RATE, ItemClassification.useful, 12, _CT_TR),
    KARItemName.DROP_PATCHES_TRAP: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 13, _CT),
    KARItemName.GIVE_ARCHIPELAGO_STAR: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 14, _CT),
    # Permanent +1 Patches (100-108)
    KARItemName.PERMANENT_WEIGHT_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 100, _CT),
    KARItemName.PERMANENT_BOOST_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 101, _CT),
    KARItemName.PERMANENT_TOP_SPEED_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 102, _CT),
    KARItemName.PERMANENT_TURN_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 103, _CT),
    KARItemName.PERMANENT_CHARGE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 104, _CT),
    KARItemName.PERMANENT_GLIDE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 105, _CT),
    KARItemName.PERMANENT_OFFENSE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 106, _CT),
    KARItemName.PERMANENT_DEFENSE_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 107, _CT),
    KARItemName.PERMANENT_HP_UP: KARItemData(KARItemType.PERMANENT_PATCH, ItemClassification.useful, 108, _CT),
    # City Trial Event Triggers (200-215). Receiving one fires that event immediately. Separate from
    # event unlocks (700+), which gate whether events occur naturally.
    KARItemName.EVENT_TRIGGER_DYNA_BLADE: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 200, _CT),
    KARItemName.EVENT_TRIGGER_TAC: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 201, _CT),
    KARItemName.EVENT_TRIGGER_METEOR: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 202, _CT),
    KARItemName.EVENT_TRIGGER_PILLAR: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 203, _CT),
    KARItemName.EVENT_TRIGGER_RUN_AMOK: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 204, _CT),
    KARItemName.EVENT_TRIGGER_RESTORATION_AREA: KARItemData(
        KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 205, _CT
    ),
    KARItemName.EVENT_TRIGGER_RAIL_FIRE: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 206, _CT),
    KARItemName.EVENT_TRIGGER_SAME_ITEM: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 207, _CT),
    KARItemName.EVENT_TRIGGER_LIGHTHOUSE: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 208, _CT),
    KARItemName.EVENT_TRIGGER_SECRET_CHAMBER: KARItemData(
        KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 209, _CT
    ),
    KARItemName.EVENT_TRIGGER_PREDICTION: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 210, _CT),
    KARItemName.EVENT_TRIGGER_MACHINE_FORMATION: KARItemData(
        KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 211, _CT
    ),
    KARItemName.EVENT_TRIGGER_UFO: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 212, _CT),
    KARItemName.EVENT_TRIGGER_BOUNCE: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 213, _CT),
    KARItemName.EVENT_TRIGGER_FOG: KARItemData(KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 214, _CT),
    KARItemName.EVENT_TRIGGER_FAKE_POWERUPS: KARItemData(
        KARItemType.CT_EVENT_GIVE, ItemClassification.useful, 215, _CT
    ),
    # Direct Game Items (300-368). The mod spawns/applies the actual in-game item when received.
    KARItemName.BLUE_BOX: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 300, _CT),
    KARItemName.GREEN_BOX: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 301, _CT),
    KARItemName.RED_BOX: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 302, _CT),
    # Stat patches (up). A single +1 is minor, so filler. _AR_CT gives Air Ride its only repeatable
    # filler source (food is CT, give-items are TR).
    KARItemName.BOOST_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 303, _AR_CT),
    KARItemName.TOP_SPEED_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 305, _AR_CT),
    KARItemName.OFFENSE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 307, _AR_CT),
    KARItemName.DEFENSE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 309, _AR_CT),
    KARItemName.TURN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 311, _AR_CT),
    KARItemName.GLIDE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 313, _AR_CT),
    KARItemName.CHARGE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 315, _AR_CT),
    KARItemName.WEIGHT_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 317, _AR_CT),
    KARItemName.HP_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 319, _AR_CT),
    KARItemName.ALL_UP_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 320, _CT),
    KARItemName.BOOST_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 304, _CT),
    KARItemName.TOP_SPEED_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 306, _CT),
    KARItemName.OFFENSE_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 308, _CT),
    KARItemName.DEFENSE_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 310, _CT),
    KARItemName.TURN_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 312, _CT),
    KARItemName.GLIDE_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 314, _CT),
    KARItemName.CHARGE_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 316, _CT),
    KARItemName.WEIGHT_DOWN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 318, _CT),
    KARItemName.SPEED_MAX_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 321, _CT),
    KARItemName.SPEED_MIN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 322, _CT),
    KARItemName.OFFENSE_MAX_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 323, _CT),
    KARItemName.DEFENSE_MAX_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 324, _CT),
    KARItemName.CHARGE_MAX_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 325, _CT),
    KARItemName.CHARGE_NONE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 326, _CT),
    KARItemName.CANDY: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 327, _CT),
    # Copy abilities (in-game item form)
    KARItemName.COPY_ABILITY_BOMB: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 328, _ALL_MODES),
    KARItemName.COPY_ABILITY_FIRE: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 329, _ALL_MODES),
    KARItemName.COPY_ABILITY_FREEZE: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 330, _ALL_MODES),
    KARItemName.COPY_ABILITY_SLEEP: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.trap, 331, _AR_CT),
    KARItemName.COPY_ABILITY_WHEEL: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 332, _AR_CT),
    KARItemName.COPY_ABILITY_WING: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 333, _AR_CT),
    KARItemName.COPY_ABILITY_PLASMA: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 334, _AR_CT),
    KARItemName.COPY_ABILITY_TORNADO: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 335, _AR_CT),
    KARItemName.COPY_ABILITY_SWORD: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 336, _AR_CT),
    KARItemName.COPY_ABILITY_NEEDLE: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 337, _AR_CT),
    KARItemName.COPY_ABILITY_MIC: KARItemData(KARItemType.ABILITY_GIVE, ItemClassification.useful, 338, _ALL_MODES),
    KARItemName.MAXIM_TOMATO: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 339, _CT),
    KARItemName.ENERGY_DRINK: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 340, _CT),
    KARItemName.ICE_CREAM: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 341, _CT),
    KARItemName.RICE_BALL: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 342, _CT),
    KARItemName.CHICKEN: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 343, _CT),
    KARItemName.CURRY: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 344, _CT),
    KARItemName.RAMEN: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 345, _CT),
    KARItemName.OMELET: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 346, _CT),
    KARItemName.HAMBURGER: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 347, _CT),
    KARItemName.SUSHI: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 348, _CT),
    KARItemName.HOT_DOG: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 349, _CT),
    KARItemName.APPLE: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.filler, 350, _CT),
    KARItemName.FIREWORKS: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 351, _CT),
    KARItemName.PANIC_SPIN: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 352, _CT),
    KARItemName.SENSOR_BOMB: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 353, _CT),
    KARItemName.GORDO: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 354, _CT),
    KARItemName.HYDRA_PART_X: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 355, _CT),
    KARItemName.HYDRA_PART_Y: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 356, _CT),
    KARItemName.HYDRA_PART_Z: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 357, _CT),
    KARItemName.DRAGOON_PART_A: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 358, _CT),
    KARItemName.DRAGOON_PART_B: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 359, _CT),
    KARItemName.DRAGOON_PART_C: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 360, _CT),
    # Fake patches (look like stat ups but are traps)
    KARItemName.FAKE_BOOST_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 361, _CT),
    KARItemName.FAKE_TOP_SPEED_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 362, _CT),
    KARItemName.FAKE_OFFENSE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 363, _CT),
    KARItemName.FAKE_DEFENSE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 364, _CT),
    KARItemName.FAKE_TURN_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 365, _CT),
    KARItemName.FAKE_GLIDE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 366, _CT),
    KARItemName.FAKE_CHARGE_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 367, _CT),
    KARItemName.FAKE_WEIGHT_PATCH: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.trap, 368, _CT),
    # Stadium Unlocks (400-423)
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_1: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 400, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_2: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 401, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_3: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 402, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DRAG_RACE_4: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 403, _CT
    ),
    KARItemName.UNLOCK_STADIUM_AIR_GLIDER: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 404, _CT
    ),
    KARItemName.UNLOCK_STADIUM_TARGET_FLIGHT: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 405, _CT
    ),
    KARItemName.UNLOCK_STADIUM_HIGH_JUMP: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 406, _CT
    ),
    KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_1: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 407, _CT
    ),
    KARItemName.UNLOCK_STADIUM_KIRBY_MELEE_2: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 408, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_1: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 409, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_2: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 410, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_3: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 411, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_4: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 412, _CT
    ),
    KARItemName.UNLOCK_STADIUM_DESTRUCTION_DERBY_5: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 413, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_1: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 414, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_2: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 415, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_3: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 416, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_4: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 417, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_5: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 418, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_6: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 419, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_7: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 420, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_8: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 421, _CT
    ),
    KARItemName.UNLOCK_STADIUM_SINGLE_RACE_9: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 422, _CT
    ),
    KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE: KARItemData(
        KARItemType.CT_STADIUM_UNLOCK, ItemClassification.progression, 423, _CT
    ),
    # Checklist Rewards: Air Ride (500-545). Receiving one performs the vanilla unlock (machine, music).
    KARItemName.AR_REWARD_NEBULA_BELT_COURSE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 500, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_NEBULA: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 501, _AR
    ),
    KARItemName.AR_REWARD_META_KNIGHT: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 502, _AR
    ),
    KARItemName.AR_REWARD_SPECIAL_MACHINE_INTROS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 503, _AR
    ),
    KARItemName.AR_REWARD_KING_DEDEDE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 504, _AR
    ),
    KARItemName.AR_REWARD_GREEN_KIRBY: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 505, _AR
    ),
    KARItemName.AR_REWARD_WAGON_STAR: KARItemData(KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 506, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_MAGMA_FLOWS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 507, _AR
    ),
    KARItemName.AR_REWARD_FILLER_BOX_1: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 508, _AR
    ),
    KARItemName.AR_REWARD_REX_WHEELIE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 509, _AR
    ),
    KARItemName.AR_REWARD_PURPLE_KIRBY: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 510, _AR
    ),
    KARItemName.AR_REWARD_SLICK_STAR: KARItemData(KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 511, _AR),
    KARItemName.AR_REWARD_ENDING: KARItemData(KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 512, _AR),
    KARItemName.AR_REWARD_WHITE_KIRBY: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 513, _AR
    ),
    KARItemName.AR_REWARD_SWERVE_STAR: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 514, _AR
    ),
    KARItemName.AR_REWARD_SHADOW_STAR: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 515, _AR
    ),
    KARItemName.AR_REWARD_JET_STAR: KARItemData(KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 516, _AR),
    KARItemName.AR_REWARD_MUSIC_HILLSIDE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 517, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_CHECKER_KNIGHTS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 518, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_MEADOWS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 519, _AR
    ),
    KARItemName.AR_REWARD_BULK_STAR: KARItemData(KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 520, _AR),
    KARItemName.AR_REWARD_SOUND_TEST_SKY_SANDS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 521, _AR
    ),
    KARItemName.AR_REWARD_FORMULA_STAR: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 522, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_MAGMA: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 523, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_BEANSTALK: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 524, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_MACHINE_PASSAGE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 525, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_FANTASY_MEADOWS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 526, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_CELESTIAL_VALLEY: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 527, _AR
    ),
    KARItemName.AR_REWARD_BROWN_KIRBY: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 528, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_FROZEN_HILLSIDE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 529, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_BEANSTALK_PARK: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 530, _AR
    ),
    KARItemName.AR_REWARD_ROCKET_STAR: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 531, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_RESULTS_SCREEN: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 532, _AR
    ),
    KARItemName.AR_REWARD_WHEELIE_BIKE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 533, _AR
    ),
    KARItemName.AR_REWARD_WHEELIE_SCOOTER: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 534, _AR
    ),
    KARItemName.AR_REWARD_WINGED_STAR: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 535, _AR
    ),
    KARItemName.AR_REWARD_FILLER_BOX_2: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 536, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_CHECKER: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 537, _AR
    ),
    KARItemName.AR_REWARD_FILLER_BOX_3: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 538, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_SKY_SANDS: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 539, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_MACHINE: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 540, _AR
    ),
    KARItemName.AR_REWARD_TURBO_STAR: KARItemData(KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 541, _AR),
    KARItemName.AR_REWARD_FILLER_BOX_4: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 542, _AR
    ),
    KARItemName.AR_REWARD_MUSIC_CELESTIAL: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 543, _AR
    ),
    KARItemName.AR_REWARD_FILLER_BOX_5: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.useful, 544, _AR
    ),
    KARItemName.AR_REWARD_SOUND_TEST_NEBULA_BELT: KARItemData(
        KARItemType.AR_CHECKLIST_REWARD, ItemClassification.filler, 545, _AR
    ),
    # Checklist Rewards: Top Ride (550-582)
    KARItemName.TR_REWARD_GREEN_KIRBY: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 550, _TR
    ),
    KARItemName.TR_REWARD_PURPLE_KIRBY: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 551, _TR
    ),
    KARItemName.TR_REWARD_DIAGONAL_CAMERA_RULE: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 552, _TR
    ),
    KARItemName.TR_REWARD_MYSTERY_ITEM_SET_RULE: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 553, _TR
    ),
    KARItemName.TR_REWARD_LANTERN_ITEM: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 554, _TR
    ),
    KARItemName.TR_REWARD_WHO_PAINT_ITEM: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 555, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_1: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 556, _TR
    ),
    KARItemName.TR_REWARD_CHICKIE_ITEM: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 557, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_GRASS: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 558, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_GRASS: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 559, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_SAND: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 560, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_2: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 561, _TR
    ),
    KARItemName.TR_REWARD_BROWN_KIRBY: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 562, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_SKY: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 563, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_FIRE: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 564, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_3: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 565, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_FIRE: KARItemData(KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 566, _TR),
    KARItemName.TR_REWARD_SOUND_TEST_WATER: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 567, _TR
    ),
    KARItemName.TR_REWARD_DEVICE_QUANTITY_RULE: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 568, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_WATER: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 569, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_LIGHT: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 570, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_4: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 571, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_METAL: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 572, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_METAL: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 573, _TR
    ),
    KARItemName.TR_REWARD_WHITE_KIRBY: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 574, _TR
    ),
    KARItemName.TR_REWARD_FILLER_BOX_5: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 575, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_SAND: KARItemData(KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 576, _TR),
    KARItemName.TR_REWARD_MUSIC_LIGHT: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 577, _TR
    ),
    KARItemName.TR_REWARD_ATTACK_ITEM_SET_RULE: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 578, _TR
    ),
    KARItemName.TR_REWARD_SOUND_TEST_RESULTS_SCREEN: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 579, _TR
    ),
    KARItemName.TR_REWARD_MUSIC_SKY: KARItemData(KARItemType.TR_CHECKLIST_REWARD, ItemClassification.filler, 580, _TR),
    KARItemName.TR_REWARD_SIDE_CAMERA_RULE: KARItemData(
        KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 581, _TR
    ),
    KARItemName.TR_REWARD_ENDING: KARItemData(KARItemType.TR_CHECKLIST_REWARD, ItemClassification.useful, 582, _TR),
    # Checklist Rewards: City Trial (600-643). The six legendary part rewards are progression, not
    # useful: their checkboxes complete only once all three parts unlock.
    KARItemName.CT_REWARD_FILLER_BOX_1: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 600, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_ITEM_BOUNCE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 601, _CT
    ),
    KARItemName.CT_REWARD_PAUSE_SCREEN_POWERUPS: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 602, _CT
    ),
    KARItemName.CT_REWARD_MUSIC_CITY: KARItemData(KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 603, _CT),
    KARItemName.CT_REWARD_SOUND_TEST_LEGENDARY_MACHINE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 604, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_DENSE_FOG: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 605, _CT
    ),
    KARItemName.CT_REWARD_META_KNIGHT_FREE_RUN: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 606, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_CITY_TRIAL: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 607, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_2: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 608, _CT
    ),
    KARItemName.CT_REWARD_SINGLE_RACE_NEBULA_STADIUM: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 609, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_ROWDY_CHARGE_TANK: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 610, _CT
    ),
    KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 611, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_DRAG_RACE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 612, _CT
    ),
    KARItemName.CT_REWARD_DRAGOON_PART_A: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.progression, 613, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_TARGET_FLIGHT: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 614, _CT
    ),
    KARItemName.CT_REWARD_DRAGOON_PART_C: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.progression, 615, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_AIR_GLIDER: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 616, _CT
    ),
    KARItemName.CT_REWARD_DESTRUCTION_DERBY_4_STADIUM: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 617, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_3: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 618, _CT
    ),
    KARItemName.CT_REWARD_HYDRA_PART_Y: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.progression, 619, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_WHATS_IN_THE_BOX: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 620, _CT
    ),
    KARItemName.CT_REWARD_HYDRA_PART_Z: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.progression, 621, _CT
    ),
    KARItemName.CT_REWARD_KING_DEDEDE_FREE_RUN: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 622, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_DYNA_BLADE_INTRO: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 623, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_4: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 624, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_HUGE_PILLAR: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 625, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_TAC_CHALLENGE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 626, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_FLYING_METEOR: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 627, _CT
    ),
    KARItemName.CT_REWARD_ENDING: KARItemData(KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 628, _CT),
    KARItemName.CT_REWARD_DRAGOON_PART_B: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.progression, 629, _CT
    ),
    KARItemName.CT_REWARD_FILLER_BOX_5: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 630, _CT
    ),
    KARItemName.CT_REWARD_HYDRA_PART_X: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.progression, 631, _CT
    ),
    KARItemName.CT_REWARD_PURPLE_KIRBY: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 632, _CT
    ),
    KARItemName.CT_REWARD_DESTRUCTION_DERBY_3_STADIUM: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 633, _CT
    ),
    KARItemName.CT_REWARD_DESTRUCTION_DERBY_5_STADIUM: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 634, _CT
    ),
    KARItemName.CT_REWARD_KIRBY_MELEE_2_STADIUM: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 635, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_KIRBY_MELEE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 636, _CT
    ),
    KARItemName.CT_REWARD_GREEN_KIRBY: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 637, _CT
    ),
    KARItemName.CT_REWARD_BROWN_KIRBY: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 638, _CT
    ),
    KARItemName.CT_REWARD_DRAGOON_FREE_RUN: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 639, _CT
    ),
    KARItemName.CT_REWARD_HYDRA_FREE_RUN: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.useful, 640, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_LIGHTHOUSE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 641, _CT
    ),
    KARItemName.CT_REWARD_SOUND_TEST_STATION_FIRE: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 642, _CT
    ),
    KARItemName.CT_REWARD_WHITE_KIRBY: KARItemData(
        KARItemType.CT_CHECKLIST_REWARD, ItemClassification.filler, 643, _CT
    ),
    # Event Unlocks (700-715). Gate whether City Trial events occur naturally.
    KARItemName.UNLOCK_EVENT_DYNA_BLADE: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 700, _CT
    ),
    KARItemName.UNLOCK_EVENT_TAC: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 701, _CT
    ),
    KARItemName.UNLOCK_EVENT_METEOR: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 702, _CT
    ),
    KARItemName.UNLOCK_EVENT_PILLAR: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 703, _CT
    ),
    KARItemName.UNLOCK_EVENT_RUN_AMOK: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 704, _CT
    ),
    KARItemName.UNLOCK_EVENT_RESTORATION_AREA: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 705, _CT
    ),
    KARItemName.UNLOCK_EVENT_RAIL_FIRE: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 706, _CT
    ),
    KARItemName.UNLOCK_EVENT_SAME_ITEM: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 707, _CT
    ),
    KARItemName.UNLOCK_EVENT_LIGHTHOUSE: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 708, _CT
    ),
    KARItemName.UNLOCK_EVENT_SECRET_CHAMBER: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 709, _CT
    ),
    KARItemName.UNLOCK_EVENT_PREDICTION: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 710, _CT
    ),
    KARItemName.UNLOCK_EVENT_MACHINE_FORMATION: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 711, _CT
    ),
    KARItemName.UNLOCK_EVENT_UFO: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 712, _CT
    ),
    KARItemName.UNLOCK_EVENT_BOUNCE: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 713, _CT
    ),
    KARItemName.UNLOCK_EVENT_FOG: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 714, _CT
    ),
    KARItemName.UNLOCK_EVENT_FAKE_POWERUPS: KARItemData(
        KARItemType.CT_EVENT_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 715, _CT
    ),
    # Copy Ability Unlocks (760-770). Gate whether copy abilities appear in the game world.
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
    KARItemName.UNLOCK_ABILITY_FREEZE: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 768, _ALL_MODES
    ),
    KARItemName.UNLOCK_ABILITY_TORNADO: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 769, _AR_CT
    ),
    KARItemName.UNLOCK_ABILITY_WING: KARItemData(
        KARItemType.ABILITY_UNLOCK, ItemClassification.progression, 770, _AR_CT
    ),
    # Base Ability Unlocks (771-773, BaseAbilityKind order). Inhale has no Top Ride half, but AP boxes
    # need it (swallowing a Walky for Mic Kirby), so _AR_CT_AP keeps it minted for AP-checklist seeds.
    KARItemName.UNLOCK_BASE_ABILITY_INHALE: KARItemData(
        KARItemType.BASE_ABILITY_UNLOCK, ItemClassification.progression, 771, _AR_CT_AP
    ),
    KARItemName.UNLOCK_BASE_ABILITY_QUICK_SPIN: KARItemData(
        KARItemType.BASE_ABILITY_UNLOCK, ItemClassification.progression, 772, _ALL_MODES
    ),
    KARItemName.UNLOCK_BASE_ABILITY_CHARGE: KARItemData(
        KARItemType.BASE_ABILITY_UNLOCK, ItemClassification.progression, 773, _ALL_MODES
    ),
    # Patch Type Unlocks (780-788). Gate whether a patch stat type appears as an in-game item.
    KARItemName.UNLOCK_PATCH_WEIGHT: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 780, _CT
    ),
    KARItemName.UNLOCK_PATCH_BOOST: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 781, _CT
    ),
    KARItemName.UNLOCK_PATCH_TOP_SPEED: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 782, _CT
    ),
    KARItemName.UNLOCK_PATCH_TURN: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 783, _CT
    ),
    KARItemName.UNLOCK_PATCH_CHARGE: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 784, _CT
    ),
    KARItemName.UNLOCK_PATCH_GLIDE: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 785, _CT
    ),
    KARItemName.UNLOCK_PATCH_OFFENSE: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 786, _CT
    ),
    KARItemName.UNLOCK_PATCH_DEFENSE: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 787, _CT
    ),
    KARItemName.UNLOCK_PATCH_HP: KARItemData(
        KARItemType.CT_PATCH_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 788, _CT
    ),
    # Item Unlocks (790-819). Gate whether an item appears in the game world.
    KARItemName.UNLOCK_ITEM_ALL_UP: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 790, _CT
    ),
    KARItemName.UNLOCK_ITEM_SPEED_MAX: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 791, _CT
    ),
    KARItemName.UNLOCK_ITEM_SPEED_MIN: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 792, _CT
    ),
    KARItemName.UNLOCK_ITEM_OFFENSE_MAX: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 793, _CT
    ),
    KARItemName.UNLOCK_ITEM_DEFENSE_MAX: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 794, _CT
    ),
    KARItemName.UNLOCK_ITEM_CHARGE_MAX: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 795, _CT
    ),
    KARItemName.UNLOCK_ITEM_CHARGE_NONE: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 796, _CT
    ),
    KARItemName.UNLOCK_ITEM_CANDY: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 797, _CT
    ),
    KARItemName.UNLOCK_ITEM_MAXIM_TOMATO: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 798, _CT
    ),
    KARItemName.UNLOCK_ITEM_ENERGY_DRINK: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 799, _CT
    ),
    KARItemName.UNLOCK_ITEM_ICE_CREAM: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 800, _CT
    ),
    KARItemName.UNLOCK_ITEM_RICE_BALL: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 801, _CT
    ),
    KARItemName.UNLOCK_ITEM_CHICKEN: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 802, _CT
    ),
    KARItemName.UNLOCK_ITEM_CURRY: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 803, _CT
    ),
    KARItemName.UNLOCK_ITEM_RAMEN: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 804, _CT
    ),
    KARItemName.UNLOCK_ITEM_OMELET: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 805, _CT
    ),
    KARItemName.UNLOCK_ITEM_HAMBURGER: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 806, _CT
    ),
    KARItemName.UNLOCK_ITEM_SUSHI: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 807, _CT
    ),
    KARItemName.UNLOCK_ITEM_HOT_DOG: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 808, _CT
    ),
    KARItemName.UNLOCK_ITEM_APPLE: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 809, _CT
    ),
    KARItemName.UNLOCK_ITEM_FIREWORKS: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 810, _CT
    ),
    KARItemName.UNLOCK_ITEM_PANIC_SPIN: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 811, _CT
    ),
    KARItemName.UNLOCK_ITEM_SENSOR_BOMB: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 812, _CT
    ),
    KARItemName.UNLOCK_ITEM_GORDO: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 813, _CT
    ),
    KARItemName.UNLOCK_ITEM_HYDRA_PART_X: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 814, _CT
    ),
    KARItemName.UNLOCK_ITEM_HYDRA_PART_Y: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 815, _CT
    ),
    KARItemName.UNLOCK_ITEM_HYDRA_PART_Z: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 816, _CT
    ),
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_A: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 817, _CT
    ),
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_B: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 818, _CT
    ),
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_C: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 819, _CT
    ),
    # Archipelago Star sphere unlocks (820-825), in the logo's ring order. A sphere stays out of City
    # Trial's item registry until its own item arrives, so all six are needed to assemble the star.
    KARItemName.UNLOCK_ITEM_AP_SPHERE_ROSE: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 820, _CT
    ),
    KARItemName.UNLOCK_ITEM_AP_SPHERE_GREEN: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 821, _CT
    ),
    KARItemName.UNLOCK_ITEM_AP_SPHERE_VIOLET: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 822, _CT
    ),
    KARItemName.UNLOCK_ITEM_AP_SPHERE_TAN: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 823, _CT
    ),
    KARItemName.UNLOCK_ITEM_AP_SPHERE_BLUE: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 824, _CT
    ),
    KARItemName.UNLOCK_ITEM_AP_SPHERE_YELLOW: KARItemData(
        KARItemType.CT_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 825, _CT
    ),
    # Machine Unlocks (830-854, plus the appended 856). Gate whether a machine can be ridden. Excluded
    # VCKINDs (not selectable player machines): 847 WINGKIRBY and 850 WHEELIEKIRBY (ability states),
    # 849 WHEELIE (enemy form; the ridable machine is Wheelie Bike 851), 855 WHEELVSDEDEDE (CPU-only).
    # 856 is the Archipelago Star, which also puts its six spheres into City Trial's item pool.
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
    # Free Star and Steer Star are Top Ride control machines: they gate the Top Ride lobby rather than
    # spawning in the city, so _TR pins them to Top Ride locations.
    KARItemName.UNLOCK_MACHINE_FREE_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 845, _TR
    ),
    KARItemName.UNLOCK_MACHINE_STEER_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 846, _TR
    ),
    # 847 (VCKIND_WINGKIRBY) intentionally omitted.
    KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 848, _AR_CT
    ),
    # 849 (VCKIND_WHEELIE) and 850 (VCKIND_WHEELIEKIRBY) intentionally omitted.
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
    KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR: KARItemData(
        KARItemType.MACHINE_UNLOCK, ItemClassification.progression, 856, _AR_CT
    ),
    # Box Unlocks (860-862). Gate whether a box color appears in-game.
    KARItemName.UNLOCK_BOX_BLUE: KARItemData(
        KARItemType.CT_BOX_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 860, _CT
    ),
    KARItemName.UNLOCK_BOX_GREEN: KARItemData(
        KARItemType.CT_BOX_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 861, _CT
    ),
    KARItemName.UNLOCK_BOX_RED: KARItemData(
        KARItemType.CT_BOX_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 862, _CT
    ),
    # Air Ride Course Unlocks (870-878)
    KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 870, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_MAGMA_FLOWS: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 871, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_SKY_SANDS: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 872, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_FROZEN_HILLSIDE: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 873, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_BEANSTALK_PARK: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 874, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_CELESTIAL_VALLEY: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 875, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_MACHINE_PASSAGE: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 876, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_CHECKER_KNIGHTS: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 877, _AR
    ),
    KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT: KARItemData(
        KARItemType.AR_COURSE_UNLOCK, ItemClassification.progression, 878, _AR
    ),
    # Kirby Color Unlocks (880-887)
    KARItemName.UNLOCK_COLOR_PINK: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 880, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_YELLOW: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 881, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_BLUE: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 882, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_RED: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 883, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_GREEN: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 884, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_PURPLE: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 885, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_BROWN: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 886, _ALL_MODES
    ),
    KARItemName.UNLOCK_COLOR_WHITE: KARItemData(
        KARItemType.COLOR_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 887, _ALL_MODES
    ),
    # Top Ride Course Unlocks (890-896)
    KARItemName.UNLOCK_TR_COURSE_GRASS: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 890, _TR
    ),
    KARItemName.UNLOCK_TR_COURSE_SAND: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 891, _TR
    ),
    KARItemName.UNLOCK_TR_COURSE_SKY: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 892, _TR
    ),
    KARItemName.UNLOCK_TR_COURSE_FIRE: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 893, _TR
    ),
    KARItemName.UNLOCK_TR_COURSE_LIGHT: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 894, _TR
    ),
    KARItemName.UNLOCK_TR_COURSE_WATER: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 895, _TR
    ),
    KARItemName.UNLOCK_TR_COURSE_METAL: KARItemData(
        KARItemType.TR_COURSE_UNLOCK, ItemClassification.progression, 896, _TR
    ),
    # Top Ride Item Unlocks (900-921, minus 912, mirrored onto the visible Party Ball at 921). The four
    # ability-themed items (909/911/913/916) are also enabled by their copy ability unlock.
    KARItemName.UNLOCK_TR_ITEM_HAMMER: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 900, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_BIG_CAKE: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 901, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SPEED_UP: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 902, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SPEED_DOWN: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 903, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SPINNER: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 904, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_CHARGE_TANK: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 905, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_INVINCIBLE_CANDY: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 906, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_BUZZ_SAW: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 907, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_DRILL: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 908, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_FREEZE_FAN: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 909, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_MISSILE: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 910, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_FIRE: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 911, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_BOMB: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 913, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_STEP_BOOM: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 914, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_LANTERN: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 915, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_WALKY: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 916, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_KRACKO: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 917, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_WHO_PAINT: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 918, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_SMOKESCREEN: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 919, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_CHICKIE: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 920, _TR
    ),
    KARItemName.UNLOCK_TR_ITEM_PARTY_BALL: KARItemData(
        KARItemType.TR_ITEM_UNLOCK, ItemClassification.progression_deprioritized_skip_balancing, 921, _TR
    ),
    # Top Ride Item Gives (950-971)
    KARItemName.GIVE_TR_ITEM_HAMMER: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 950, _TR),
    KARItemName.GIVE_TR_ITEM_BIG_CAKE: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 951, _TR),
    KARItemName.GIVE_TR_ITEM_SPEED_UP: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 952, _TR),
    KARItemName.GIVE_TR_ITEM_SPEED_DOWN: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.trap, 953, _TR),
    KARItemName.GIVE_TR_ITEM_SPINNER: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 954, _TR),
    KARItemName.GIVE_TR_ITEM_CHARGE_TANK: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 955, _TR),
    KARItemName.GIVE_TR_ITEM_INVINCIBLE_CANDY: KARItemData(
        KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 956, _TR
    ),
    KARItemName.GIVE_TR_ITEM_BUZZ_SAW: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 957, _TR),
    KARItemName.GIVE_TR_ITEM_DRILL: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 958, _TR),
    KARItemName.GIVE_TR_ITEM_FREEZE_FAN: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 959, _TR),
    KARItemName.GIVE_TR_ITEM_MISSILE: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 960, _TR),
    KARItemName.GIVE_TR_ITEM_FIRE: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 961, _TR),
    KARItemName.GIVE_TR_ITEM_BOMB: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 963, _TR),
    KARItemName.GIVE_TR_ITEM_STEP_BOOM: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 964, _TR),
    KARItemName.GIVE_TR_ITEM_LANTERN: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 965, _TR),
    KARItemName.GIVE_TR_ITEM_WALKY: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 966, _TR),
    KARItemName.GIVE_TR_ITEM_KRACKO: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 967, _TR),
    KARItemName.GIVE_TR_ITEM_WHO_PAINT: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 968, _TR),
    KARItemName.GIVE_TR_ITEM_SMOKESCREEN: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 969, _TR),
    KARItemName.GIVE_TR_ITEM_CHICKIE: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 970, _TR),
    KARItemName.GIVE_TR_ITEM_PARTY_BALL: KARItemData(KARItemType.TR_ITEM_GIVE, ItemClassification.filler, 971, _TR),
    # Cosmetic all-mode filler.
    KARItemName.BIG_KIRBY: KARItemData(KARItemType.FILLER, ItemClassification.filler, 972, _ALL_MODES),
    KARItemName.SMALL_KIRBY: KARItemData(KARItemType.FILLER, ItemClassification.filler, 973, _ALL_MODES),
    # Archipelago Star sphere gives (980-985). Collect the sphere into the round's set, the way 355-360
    # hand over a Hydra or Dragoon part, and assemble the star on the sixth. Like those, the give ignores
    # the matching unlock (820-825) - it does not spawn the sphere, so it needs no item registry slot.
    KARItemName.GIVE_AP_SPHERE_ROSE: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 980, _CT),
    KARItemName.GIVE_AP_SPHERE_GREEN: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 981, _CT),
    KARItemName.GIVE_AP_SPHERE_VIOLET: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 982, _CT),
    KARItemName.GIVE_AP_SPHERE_TAN: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 983, _CT),
    KARItemName.GIVE_AP_SPHERE_BLUE: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 984, _CT),
    KARItemName.GIVE_AP_SPHERE_YELLOW: KARItemData(KARItemType.CT_ITEM_GIVE, ItemClassification.useful, 985, _CT),
    # Goal Events (no network code, internal AP events only)
    KARItemName.CITY_TRIAL_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
    KARItemName.AIR_RIDE_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
    KARItemName.TOP_RIDE_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
    KARItemName.ARCHIPELAGO_VICTORY: KARItemData(KARItemType.GOAL, ItemClassification.progression, None),
    # AP Patch group events (no network code, internal AP events only)
    KARItemName.AP_PATCH_GROUP_1_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_2_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_3_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_4_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_5_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_6_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_7_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_8_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
    KARItemName.AP_PATCH_GROUP_9_CLEARED: KARItemData(KARItemType.AP_PATCH_GROUP, ItemClassification.progression, None),
}


# Ordered tuple of all stadium unlock item names, for mappings and iteration in __init__.py.
STADIUM_UNLOCK_ITEMS: tuple[KARItemName, ...] = tuple(
    KARItemName(name) for name, data in ITEM_TABLE.items() if data.type == KARItemType.CT_STADIUM_UNLOCK
)

# The six City Trial stadiums vanilla unlocks via a checklist reward square. The mod unlocks stadiums
# by the stadium mask instead, so these reward squares gate nothing and stay out of the pool.
STADIUM_CHECKLIST_REWARDS: frozenset[KARItemName] = frozenset(
    {
        KARItemName.CT_REWARD_DRAG_RACE_4_STADIUM,
        KARItemName.CT_REWARD_KIRBY_MELEE_2_STADIUM,
        KARItemName.CT_REWARD_DESTRUCTION_DERBY_3_STADIUM,
        KARItemName.CT_REWARD_DESTRUCTION_DERBY_4_STADIUM,
        KARItemName.CT_REWARD_DESTRUCTION_DERBY_5_STADIUM,
        KARItemName.CT_REWARD_SINGLE_RACE_NEBULA_STADIUM,
    }
)

# The three per-mode checklist reward item types, and the checklist mode each belongs to. Every native
# checklist reward is one of these.
CHECKLIST_REWARD_TYPE_MODES: dict[KARItemType, GameMode] = {
    KARItemType.CT_CHECKLIST_REWARD: GameMode.CITYTRIAL,
    KARItemType.AR_CHECKLIST_REWARD: GameMode.AIRRIDE,
    KARItemType.TR_CHECKLIST_REWARD: GameMode.TOPRIDE,
}
CHECKLIST_REWARD_TYPES: frozenset[KARItemType] = frozenset(CHECKLIST_REWARD_TYPE_MODES)


# The six Archipelago Star spheres. Under city_trial_items_gated a sphere only spawns once its own
# unlock arrives, so assembling the star needs all six.
AP_STAR_PIECE_UNLOCK_ITEMS: tuple[KARItemName, ...] = (
    KARItemName.UNLOCK_ITEM_AP_SPHERE_ROSE,
    KARItemName.UNLOCK_ITEM_AP_SPHERE_GREEN,
    KARItemName.UNLOCK_ITEM_AP_SPHERE_VIOLET,
    KARItemName.UNLOCK_ITEM_AP_SPHERE_TAN,
    KARItemName.UNLOCK_ITEM_AP_SPHERE_BLUE,
    KARItemName.UNLOCK_ITEM_AP_SPHERE_YELLOW,
)


# The AP Patch group events in chain order: index k is the event that opens group k+2. A seed of N
# groups uses the first N-1.
AP_PATCH_GROUP_EVENT_ITEMS: tuple[KARItemName, ...] = (
    KARItemName.AP_PATCH_GROUP_1_CLEARED,
    KARItemName.AP_PATCH_GROUP_2_CLEARED,
    KARItemName.AP_PATCH_GROUP_3_CLEARED,
    KARItemName.AP_PATCH_GROUP_4_CLEARED,
    KARItemName.AP_PATCH_GROUP_5_CLEARED,
    KARItemName.AP_PATCH_GROUP_6_CLEARED,
    KARItemName.AP_PATCH_GROUP_7_CLEARED,
    KARItemName.AP_PATCH_GROUP_8_CLEARED,
    KARItemName.AP_PATCH_GROUP_9_CLEARED,
)


# The same deal for the six vanilla Hydra/Dragoon pieces. Distinct from the CT_REWARD_*_PART_*
# checklist markers behind the "Unlock Parts" cells.
LEGENDARY_PIECE_UNLOCK_ITEMS: tuple[KARItemName, ...] = (
    KARItemName.UNLOCK_ITEM_HYDRA_PART_X,
    KARItemName.UNLOCK_ITEM_HYDRA_PART_Y,
    KARItemName.UNLOCK_ITEM_HYDRA_PART_Z,
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_A,
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_B,
    KARItemName.UNLOCK_ITEM_DRAGOON_PART_C,
)


# Machines the Charge base ability makes usable at all: Hydra and Bulk Star barely move without a
# charge boost, and Slick / Turbo Star can only be steered by charge-drifting.
CHARGE_DEPENDENT_MACHINES: frozenset[KARItemName] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_HYDRA,
        KARItemName.UNLOCK_MACHINE_BULK_STAR,
        KARItemName.UNLOCK_MACHINE_SLICK_STAR,
        KARItemName.UNLOCK_MACHINE_TURBO_STAR,
        # The Archipelago Star inherits the Slick Star's handling attributes.
        KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    }
)


# Assembled in City Trial from their spheres rather than selected, so none is ever a starting machine.
ASSEMBLED_MACHINE_UNLOCKS: frozenset[KARItemName] = frozenset(
    {
        KARItemName.UNLOCK_MACHINE_HYDRA,
        KARItemName.UNLOCK_MACHINE_DRAGOON,
        KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR,
    }
)

# Top Ride controls: the mod hard-gates the Top Ride lobby on these two, and neither is rideable in
# City Trial or Air Ride.
TR_MACHINE_UNLOCK_ITEMS: tuple[KARItemName, ...] = (
    KARItemName.UNLOCK_MACHINE_FREE_STAR,
    KARItemName.UNLOCK_MACHINE_STEER_STAR,
)

AR_CT_MACHINE_UNLOCK_ITEMS: tuple[KARItemName, ...] = tuple(
    KARItemName(name)
    for name, data in ITEM_TABLE.items()
    if data.type == KARItemType.MACHINE_UNLOCK
    and KARItemName(name) not in ASSEMBLED_MACHINE_UNLOCKS
    and KARItemName(name) not in TR_MACHINE_UNLOCK_ITEMS
)

AR_COURSE_UNLOCK_ITEMS: tuple[KARItemName, ...] = tuple(
    KARItemName(name) for name, data in ITEM_TABLE.items() if data.type == KARItemType.AR_COURSE_UNLOCK
)

TR_COURSE_UNLOCK_ITEMS: tuple[KARItemName, ...] = tuple(
    KARItemName(name) for name, data in ITEM_TABLE.items() if data.type == KARItemType.TR_COURSE_UNLOCK
)

COLOR_UNLOCK_ITEMS: tuple[KARItemName, ...] = tuple(
    KARItemName(name) for name, data in ITEM_TABLE.items() if data.type == KARItemType.COLOR_UNLOCK
)


# The two playable non-Kirby characters, by the machine unlock that makes each selectable. Each keeps
# its own melee attack, which no base-ability gate touches, so either is a damage source on its own.
CHARACTER_MACHINE_UNLOCKS: tuple[KARItemName, ...] = (
    KARItemName.UNLOCK_MACHINE_WHEELIE_DEDEDE,
    KARItemName.UNLOCK_MACHINE_WING_META_KNIGHT,
)


# Copy abilities that can KO. Sleep has no attack; Wheel and Wing only ram, which an ordinary machine
# already does and which cannot finish a derby or a Dedede fight.
DAMAGING_ABILITY_UNLOCKS: tuple[KARItemName, ...] = (
    KARItemName.UNLOCK_ABILITY_FIRE,
    KARItemName.UNLOCK_ABILITY_SWORD,
    KARItemName.UNLOCK_ABILITY_BOMB,
    KARItemName.UNLOCK_ABILITY_PLASMA,
    KARItemName.UNLOCK_ABILITY_NEEDLE,
    KARItemName.UNLOCK_ABILITY_MIC,
    KARItemName.UNLOCK_ABILITY_FREEZE,
    KARItemName.UNLOCK_ABILITY_TORNADO,
)


# Single source of truth for the optional "gating" mechanic. Pool building, the fuzzer, and the gating
# tests all derive from this table, so adding a gated category only needs a new row.
class GatingCategory(NamedTuple):
    option: str
    item_type: KARItemType
    # KARWorld flag names; the unlock items drop out when no listed mode is on. Empty = never excluded.
    required_modes: frozenset[str]
    # Rewards always excluded from the pool: the mod handles the category itself, gate ON or OFF.
    overlapping_rewards: frozenset[KARItemName] = frozenset()


GATING_CATEGORIES: tuple[GatingCategory, ...] = (
    GatingCategory("city_trial_events_gated", KARItemType.CT_EVENT_UNLOCK, frozenset({"city_trial_enabled"})),
    # TR included: 4 TR locations (Fire/Bomb/Walky) gate behind ability unlocks when abilities_gated is on.
    GatingCategory(
        "abilities_gated",
        KARItemType.ABILITY_UNLOCK,
        frozenset({"city_trial_enabled", "air_ride_enabled", "top_ride_enabled"}),
    ),
    # Quick spin and charge apply in all modes; inhale has no Top Ride half (see its _AR_CT_AP entry).
    GatingCategory(
        "base_abilities_gated",
        KARItemType.BASE_ABILITY_UNLOCK,
        frozenset({"city_trial_enabled", "air_ride_enabled", "top_ride_enabled"}),
    ),
    GatingCategory("city_trial_patches_gated", KARItemType.CT_PATCH_UNLOCK, frozenset({"city_trial_enabled"})),
    GatingCategory("city_trial_items_gated", KARItemType.CT_ITEM_UNLOCK, frozenset({"city_trial_enabled"})),
    GatingCategory(
        "machines_gated",
        KARItemType.MACHINE_UNLOCK,
        frozenset({"city_trial_enabled", "air_ride_enabled"}),
        frozenset(
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
    ),
    GatingCategory("city_trial_boxes_gated", KARItemType.CT_BOX_UNLOCK, frozenset({"city_trial_enabled"})),
    GatingCategory(
        "air_ride_courses_gated",
        KARItemType.AR_COURSE_UNLOCK,
        frozenset({"air_ride_enabled"}),
        frozenset({KARItemName.AR_REWARD_NEBULA_BELT_COURSE}),
    ),
    GatingCategory(
        "colors_gated",
        KARItemType.COLOR_UNLOCK,
        frozenset(),
        frozenset(
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
    ),
    GatingCategory("top_ride_courses_gated", KARItemType.TR_COURSE_UNLOCK, frozenset({"top_ride_enabled"})),
    GatingCategory(
        "top_ride_items_gated",
        KARItemType.TR_ITEM_UNLOCK,
        frozenset({"top_ride_enabled"}),
        frozenset(
            {
                KARItemName.TR_REWARD_LANTERN_ITEM,
                KARItemName.TR_REWARD_WHO_PAINT_ITEM,
                KARItemName.TR_REWARD_CHICKIE_ITEM,
            }
        ),
    ),
    # Stadiums: gated ON = each Unlock Stadium item gates its stadium; OFF = the mod unlocks all 24 at
    # connect. The six reward-overlap stadiums behave like the other 18.
    GatingCategory(
        "city_trial_stadiums_gated",
        KARItemType.CT_STADIUM_UNLOCK,
        frozenset({"city_trial_enabled"}),
        STADIUM_CHECKLIST_REWARDS,
    ),
)


# The reward items behind each of the mod's placeable reward types. Only rewards no gating category
# owns appear - the overlapping_rewards above and the progression Dragoon/Hydra part markers are placed
# regardless of this option, so they belong to no type here.
CHECKLIST_REWARD_TYPE_ITEMS: dict[RewardType, frozenset[str]] = {
    RewardType.FILLER: frozenset(
        {
            KARItemName.AR_REWARD_FILLER_BOX_1,
            KARItemName.AR_REWARD_FILLER_BOX_2,
            KARItemName.AR_REWARD_FILLER_BOX_3,
            KARItemName.AR_REWARD_FILLER_BOX_4,
            KARItemName.AR_REWARD_FILLER_BOX_5,
            KARItemName.TR_REWARD_FILLER_BOX_1,
            KARItemName.TR_REWARD_FILLER_BOX_2,
            KARItemName.TR_REWARD_FILLER_BOX_3,
            KARItemName.TR_REWARD_FILLER_BOX_4,
            KARItemName.TR_REWARD_FILLER_BOX_5,
            KARItemName.CT_REWARD_FILLER_BOX_1,
            KARItemName.CT_REWARD_FILLER_BOX_2,
            KARItemName.CT_REWARD_FILLER_BOX_3,
            KARItemName.CT_REWARD_FILLER_BOX_4,
            KARItemName.CT_REWARD_FILLER_BOX_5,
        }
    ),
    RewardType.BONUS_MOVIE: frozenset(
        {
            KARItemName.AR_REWARD_SPECIAL_MACHINE_INTROS,
        }
    ),
    RewardType.EXTRA_RULE: frozenset(
        {
            KARItemName.TR_REWARD_DIAGONAL_CAMERA_RULE,
            KARItemName.TR_REWARD_MYSTERY_ITEM_SET_RULE,
            KARItemName.TR_REWARD_DEVICE_QUANTITY_RULE,
            KARItemName.TR_REWARD_ATTACK_ITEM_SET_RULE,
            KARItemName.TR_REWARD_SIDE_CAMERA_RULE,
        }
    ),
    RewardType.SOUND_TEST: frozenset(
        {
            KARItemName.AR_REWARD_SOUND_TEST_MAGMA_FLOWS,
            KARItemName.AR_REWARD_SOUND_TEST_CHECKER_KNIGHTS,
            KARItemName.AR_REWARD_SOUND_TEST_SKY_SANDS,
            KARItemName.AR_REWARD_SOUND_TEST_MACHINE_PASSAGE,
            KARItemName.AR_REWARD_SOUND_TEST_FANTASY_MEADOWS,
            KARItemName.AR_REWARD_SOUND_TEST_CELESTIAL_VALLEY,
            KARItemName.AR_REWARD_SOUND_TEST_FROZEN_HILLSIDE,
            KARItemName.AR_REWARD_SOUND_TEST_BEANSTALK_PARK,
            KARItemName.AR_REWARD_SOUND_TEST_RESULTS_SCREEN,
            KARItemName.AR_REWARD_SOUND_TEST_NEBULA_BELT,
            KARItemName.TR_REWARD_SOUND_TEST_GRASS,
            KARItemName.TR_REWARD_SOUND_TEST_SAND,
            KARItemName.TR_REWARD_SOUND_TEST_SKY,
            KARItemName.TR_REWARD_SOUND_TEST_FIRE,
            KARItemName.TR_REWARD_SOUND_TEST_WATER,
            KARItemName.TR_REWARD_SOUND_TEST_LIGHT,
            KARItemName.TR_REWARD_SOUND_TEST_METAL,
            KARItemName.TR_REWARD_SOUND_TEST_RESULTS_SCREEN,
            KARItemName.CT_REWARD_SOUND_TEST_ITEM_BOUNCE,
            KARItemName.CT_REWARD_SOUND_TEST_LEGENDARY_MACHINE,
            KARItemName.CT_REWARD_SOUND_TEST_DENSE_FOG,
            KARItemName.CT_REWARD_SOUND_TEST_CITY_TRIAL,
            KARItemName.CT_REWARD_SOUND_TEST_ROWDY_CHARGE_TANK,
            KARItemName.CT_REWARD_SOUND_TEST_DRAG_RACE,
            KARItemName.CT_REWARD_SOUND_TEST_TARGET_FLIGHT,
            KARItemName.CT_REWARD_SOUND_TEST_AIR_GLIDER,
            KARItemName.CT_REWARD_SOUND_TEST_WHATS_IN_THE_BOX,
            KARItemName.CT_REWARD_SOUND_TEST_DYNA_BLADE_INTRO,
            KARItemName.CT_REWARD_SOUND_TEST_HUGE_PILLAR,
            KARItemName.CT_REWARD_SOUND_TEST_TAC_CHALLENGE,
            KARItemName.CT_REWARD_SOUND_TEST_FLYING_METEOR,
            KARItemName.CT_REWARD_SOUND_TEST_KIRBY_MELEE,
            KARItemName.CT_REWARD_SOUND_TEST_LIGHTHOUSE,
            KARItemName.CT_REWARD_SOUND_TEST_STATION_FIRE,
        }
    ),
    RewardType.MUSIC: frozenset(
        {
            KARItemName.AR_REWARD_MUSIC_NEBULA,
            KARItemName.AR_REWARD_MUSIC_HILLSIDE,
            KARItemName.AR_REWARD_MUSIC_MEADOWS,
            KARItemName.AR_REWARD_MUSIC_MAGMA,
            KARItemName.AR_REWARD_MUSIC_BEANSTALK,
            KARItemName.AR_REWARD_MUSIC_CHECKER,
            KARItemName.AR_REWARD_MUSIC_SKY_SANDS,
            KARItemName.AR_REWARD_MUSIC_MACHINE,
            KARItemName.AR_REWARD_MUSIC_CELESTIAL,
            KARItemName.TR_REWARD_MUSIC_GRASS,
            KARItemName.TR_REWARD_MUSIC_FIRE,
            KARItemName.TR_REWARD_MUSIC_WATER,
            KARItemName.TR_REWARD_MUSIC_METAL,
            KARItemName.TR_REWARD_MUSIC_SAND,
            KARItemName.TR_REWARD_MUSIC_LIGHT,
            KARItemName.TR_REWARD_MUSIC_SKY,
            KARItemName.CT_REWARD_MUSIC_CITY,
        }
    ),
    RewardType.ENDING: frozenset(
        {
            KARItemName.AR_REWARD_ENDING,
            KARItemName.TR_REWARD_ENDING,
            KARItemName.CT_REWARD_ENDING,
        }
    ),
    RewardType.PAUSE_POWERUPS: frozenset(
        {
            KARItemName.CT_REWARD_PAUSE_SCREEN_POWERUPS,
        }
    ),
}


# The reward types each `checklist_rewards` category covers. A category the player selects has its
# types placed as AP items; the rest are unlocked by the mod at connect.
CHECKLIST_REWARD_CATEGORY_TYPES: dict[str, frozenset[RewardType]] = {
    "Sound Test": frozenset({RewardType.SOUND_TEST}),
    "Music": frozenset({RewardType.MUSIC}),
    "Filler Boxes": frozenset({RewardType.FILLER}),
    "Endings": frozenset({RewardType.ENDING}),
    "Gameplay Extras": frozenset({RewardType.EXTRA_RULE, RewardType.BONUS_MOVIE, RewardType.PAUSE_POWERUPS}),
}


# Keys of the `checklist_rewards` OptionSet, mapped to the reward items each selects.
CHECKLIST_REWARD_CATEGORIES: dict[str, frozenset[str]] = {
    category: frozenset().union(*(CHECKLIST_REWARD_TYPE_ITEMS[t] for t in types))
    for category, types in CHECKLIST_REWARD_CATEGORY_TYPES.items()
}

# The reward type each in-scope checklist reward belongs to, for building the placed-types mask.
CHECKLIST_REWARD_ITEM_TYPES: dict[str, RewardType] = {
    name: reward_type for reward_type, names in CHECKLIST_REWARD_TYPE_ITEMS.items() for name in names
}


# Maps a trap category name (keys of the `traps` OptionSet) to its trap items. Every trap-classified
# item must appear in exactly one category, or it could never be selected.
TRAP_CATEGORIES: dict[str, frozenset[str]] = {
    "Direct Damage": frozenset(
        {
            KARItemName.ONE_HP_TRAP,
        }
    ),
    "Stat Debuff": frozenset(
        {
            KARItemName.ALL_DOWN,
            KARItemName.BOOST_DOWN_PATCH,
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
    "Fake Patches": frozenset(
        {
            KARItemName.FAKE_BOOST_PATCH,
            KARItemName.FAKE_TOP_SPEED_PATCH,
            KARItemName.FAKE_OFFENSE_PATCH,
            KARItemName.FAKE_DEFENSE_PATCH,
            KARItemName.FAKE_TURN_PATCH,
            KARItemName.FAKE_GLIDE_PATCH,
            KARItemName.FAKE_CHARGE_PATCH,
            KARItemName.FAKE_WEIGHT_PATCH,
        }
    ),
}


# Maps each KARItemType to its player-facing KARItemGroup (1:1). Groups are exposed in YAML configs.
_TYPE_TO_GROUP: dict[KARItemType, KARItemGroup] = {
    KARItemType.CHECKBOX_FILLER: KARItemGroup.CHECKBOX_FILLERS,
    KARItemType.PATCH_CAP_INCREASE: KARItemGroup.PATCH_CAP_INCREASES,
    KARItemType.PERMANENT_PATCH: KARItemGroup.PERMANENT_PATCHES,
    KARItemType.SPAWN_RATE: KARItemGroup.SPAWN_RATES,
    KARItemType.CT_ITEM_GIVE: KARItemGroup.CT_ITEM_GIVES,
    KARItemType.CT_EVENT_GIVE: KARItemGroup.CT_EVENT_GIVES,
    KARItemType.ABILITY_GIVE: KARItemGroup.ABILITY_GIVES,
    KARItemType.CT_STADIUM_UNLOCK: KARItemGroup.CT_STADIUM_UNLOCKS,
    KARItemType.CT_CHECKLIST_REWARD: KARItemGroup.CT_REWARDS,
    KARItemType.AR_CHECKLIST_REWARD: KARItemGroup.AR_REWARDS,
    KARItemType.TR_CHECKLIST_REWARD: KARItemGroup.TR_REWARDS,
    KARItemType.CT_EVENT_UNLOCK: KARItemGroup.CT_EVENT_UNLOCKS,
    KARItemType.ABILITY_UNLOCK: KARItemGroup.ABILITY_UNLOCKS,
    KARItemType.BASE_ABILITY_UNLOCK: KARItemGroup.BASE_ABILITY_UNLOCKS,
    KARItemType.CT_PATCH_UNLOCK: KARItemGroup.CT_PATCH_UNLOCKS,
    KARItemType.CT_ITEM_UNLOCK: KARItemGroup.CT_ITEM_UNLOCKS,
    KARItemType.MACHINE_UNLOCK: KARItemGroup.MACHINE_UNLOCKS,
    KARItemType.CT_BOX_UNLOCK: KARItemGroup.CT_BOX_UNLOCKS,
    KARItemType.AR_COURSE_UNLOCK: KARItemGroup.AR_COURSE_UNLOCKS,
    KARItemType.TR_COURSE_UNLOCK: KARItemGroup.TR_COURSE_UNLOCKS,
    KARItemType.COLOR_UNLOCK: KARItemGroup.COLOR_UNLOCKS,
    KARItemType.TR_ITEM_UNLOCK: KARItemGroup.TR_ITEM_UNLOCKS,
    KARItemType.TR_ITEM_GIVE: KARItemGroup.TR_ITEM_GIVES,
    KARItemType.FILLER: KARItemGroup.FILLER_ITEMS,
}

# All item names bucketed by KARItemType - the view generation uses, kept separate from the
# player-facing group strings so generation never depends on them.
items_by_type: dict[KARItemType, set[str]] = {}
for _name, _data in ITEM_TABLE.items():
    items_by_type.setdefault(_data.type, set()).add(_name)

# Player-facing groups, derived from items_by_type via the type->group map (copied so the two views
# can't alias-mutate). "Traps" spans several types, so it's derived from the trap classification.
item_name_groups: dict[str, set[str]] = {
    group: set(items_by_type.get(item_type, set())) for item_type, group in _TYPE_TO_GROUP.items()
}
item_name_groups[KARItemGroup.TRAPS] = {n for n, d in ITEM_TABLE.items() if d.classification & ItemClassification.trap}


# Maps an "allowed items" category name (keys of the `allowed_items` OptionSet) to the KARItemType it
# governs; keys reuse the KARItemGroup display strings.
ALLOWED_ITEM_CATEGORIES: dict[str, KARItemType] = {
    KARItemGroup.PERMANENT_PATCHES: KARItemType.PERMANENT_PATCH,
    KARItemGroup.CT_ITEM_GIVES: KARItemType.CT_ITEM_GIVE,
    KARItemGroup.CT_EVENT_GIVES: KARItemType.CT_EVENT_GIVE,
    KARItemGroup.ABILITY_GIVES: KARItemType.ABILITY_GIVE,
    KARItemGroup.TR_ITEM_GIVES: KARItemType.TR_ITEM_GIVE,
}

# The non-trap item names each allowed-items category governs; `traps` alone governs trap membership.
ALLOWED_ITEM_CATEGORY_ITEMS: dict[str, frozenset[str]] = {
    category: frozenset(
        name
        for name in items_by_type.get(item_type, set())
        if not (ITEM_TABLE[name].classification & ItemClassification.trap)
    )
    for category, item_type in ALLOWED_ITEM_CATEGORIES.items()
}
