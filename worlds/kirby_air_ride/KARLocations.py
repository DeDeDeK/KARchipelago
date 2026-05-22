from enum import StrEnum
from typing import NamedTuple

from BaseClasses import Location

from .KAROptions import AirRideGoal, CityTrialGoal, TopRideGoal
from .KARRegions import KARRegion


class KARLocationData(NamedTuple):
    """Data for a location in Kirby Air Ride.

    code: Unique AP location code (sequential 1-360).
    region: Name of the region this location belongs to.
    """

    code: int
    region: str


class KARLocation(Location):
    """An Archipelago location for Kirby Air Ride."""

    game: str = "Kirby Air Ride"


class CTLocation(StrEnum):
    """City Trial checklist location names."""

    RACE_60_MILES = "City Trial: race over 60 miles!"
    PICKUP_1000_ITEMS = "City Trial: pick up a total of over 1000 items!"
    BREAK_1000_BOXES = "City Trial: break more than 1000 boxes!"
    STADIUM_PLAY_10_STADIUM_MODES = "Stadium: play in over 10 stadium modes!"
    STADIUM_DR2_FINISH_00_24_00 = "Stadium: DRAG RACE 2 Finish in less than 00:24:00!"
    STADIUM_DR4_FINISH_00_24_00 = "Stadium: DRAG RACE 4 Finish in less than 00:24:00!"
    STADIUM_HJ_AIRBORNE_10_SECONDS = "Stadium: HIGH JUMP Stay airborne longer than 10 seconds!"
    STADIUM_TF_AIRBORNE_15_SECONDS = "Stadium: TARGET FLIGHT stay airborne longer than 15 seconds!"
    STADIUM_AG_FLY_660_FEET = "Stadium: AIR GLIDER fly more than 660 feet!"
    STADIUM_DD2_KO_YOUR_RIVALS_5 = "Stadium: DESTRUCTION DERBY 2 In one game, KO your rivals 5 or more times!"
    STADIUM_DD1_BUST_ALL_ROCKS_ON_FIELD = "Stadium: DESTRUCTION DERBY 1 bust all the rocks on the field!"
    STADIUM_KM2_KO_ENEMIES_30X = "Stadium: KIRBY MELEE 2 In one game, KO enemies over 30 times!"
    DO_SOME_DAMAGE_TO_DYNA_BLADE = "City Trial: Do some damage to Dyna Blade!"
    STEAL_8_FROM_TAC = "City Trial: Steal over 8 items from Tac by yourself!"
    ENTER_CASTLE_CHAMBER = "City Trial: Go into the castle chamber when it opens!"
    OPEN_ALL_VOLCANO_HOLES = "City Trial: Open up all the holes around the base of the volcano!"
    HIGH_PLAINS_HOLE_3X = "City Trial: During one game, go into the hole in the high plains 3 times or more!"
    DESTROY_ALL_HOUSES = "City Trial: Destroy all of the dilapidated houses!"
    GET_10_ITEMS_IN_20S = "City Trial: Get 10 items within the first 20 seconds of the match!"
    TIMEOUT_ALL_ON_RAILS = "City Trial: Let time run out while all players are on the rails!"
    GET_10_BOOST_PATCHES = "City Trial: In one game, get over 10 Boost Patches!"
    GET_10_TURN_PATCHES = "City Trial: In one game, get 10 or more Turn Patches!"
    GET_10_WEIGHT_PATCHES = "City Trial: In one game, get 10 or more Weight Patches!"
    GET_10_GLIDE_PATCHES = "City Trial: In one game, get 10 or more Glide Patches!"
    USE_FIREWORKS_TO_KO_RIVALS_10X = "City Trial: Use Fireworks to KO rivals 10 times or more!"
    STADIUM_DR1_17_00_FORMULA = "Stadium: DRAG RACE 1 Finish in less than 00:17:00 on Formula Star!"
    STADIUM_DR3_31_00_WHEELIE_BIKE = "Stadium: DRAG RACE 3 Finish in less than 00:31:00 on Wheelie Bike!"
    EAT_3_HOT_DOGS = "City Trial: In one race, eat 3 or more Hot Dogs!"
    BUST_WHEELIE_BIKE_ON_WARPSTAR = "City Trial: In the city, bust Wheelie Bike while riding on Warpstar!"
    BUST_SLICK_STAR_ON_FORMULA_STAR = "City Trial: In the city, bust Slick Star while riding on Formula Star!"
    RACE_200_MILES = "City Trial: Race over 200 miles!"
    PICKUP_3000_ITEMS = "City Trial: Pick up a total of over 3000 items!"
    FR_DRIVE_FOR_10_MINUTES = "City Trial: Free Run: Drive for a total of 10 minutes or more!"
    STADIUM_PLAY_20_STADIUM_MODES = "Stadium: play in over 20 stadium modes!"
    STADIUM_DR2_FINISH_00_20_00 = "Stadium: DRAG RACE 2 Finish in less than 00:20:00!"
    STADIUM_DR4_FINISH_00_19_00 = "Stadium: DRAG RACE 4 Finish in less than 00:19:00!"
    STADIUM_TF_GET_150_POINTS = "Stadium: TARGET FLIGHT In one game, get over 150 points!"
    STADIUM_TF_PLAY_15X = "Stadium: TARGET FLIGHT play 15 times or more!"
    STADIUM_AG_FLY_1300_FEET = "Stadium: AIR GLIDER fly more than 1,300 feet!"
    STADIUM_DD3_KO_YOUR_RIVALS_5 = "Stadium: DESTRUCTION DERBY 3 In one game, KO your rivals 5 or more times!"
    STADIUM_DD_ALL_KO_ENEMIES_50X = "Stadium: DESTRUCTION DERBY (All) KO enemies over 50 times!"
    STADIUM_KM_ALL_KO_500_ENEMIES = "Stadium: KIRBY MELEE (All) KO over 500 enemies!"
    GET_TRAMPLED_BY_DYNA_BLADE = "City Trial: Get trampled by Dyna Blade!"
    THE_METEOR_ATTACKS_CITY_3 = "City Trial: The meteor attacks the city 3 or more times!"
    FLY_THROUGH_RINGS_IN_SKY_5X = "City Trial: During one game, fly through the rings in the sky 5 times or more!"
    LET_WATERWHEEL_CARRY_YOU_10X = "City Trial: Let the waterwheel carry you 10 times or more!"
    BREAK_ALL_ROCKS = "City Trial: During one game, break all of the volcano rocks and high plains rocks!"
    KNOCK_DOWN_ALL_OF_TREES_IN_FOREST = "City Trial: Knock down all of the trees in the forest!"
    DAMAGE_RIVAL_WITHIN_10S = "City Trial: Do damage to a rival within the first 10 seconds of a match!"
    BREAK_A_CPUS_MACHINE_5_X = "City Trial: Break a CPU's machine 5 times or more in the city!"
    STADIUM_DD1_KO_A_RIVAL_10X = "Stadium: DESTRUCTION DERBY 1 In one game, KO a rival 10 times or more!"
    STADIUM_DD4_KO_A_RIVAL_10X = "Stadium: DESTRUCTION DERBY 4 In one game, KO a rival 10 times or more!"
    STADIUM_KM1_KO_75_ENEMIES_BY_YOURSELF = "Stadium: KIRBY MELEE 1 In one game, KO over 75 enemies by yourself!"
    GET_30_GLIDE_PATCHES = "City Trial: Get 30 or more Glide Patches!"
    EAT_2_MAXIM_TOMATOES = "City Trial: In one game, eat 2 or more maxim tomatoes!"
    STADIUM_DR2_27_00_WAGON = "Stadium: DRAG RACE 2 Finish in less than 00:27:00 on Wagon Star!"
    STADIUM_DR4_33_00_TURBO = "Stadium: DRAG RACE 4 Finish in less than 00:33:00 on Turbo Star!"
    UNLOCK_DRAGOON_CHECKLIST = "City Trial: Unlock Dragoon Parts A, B, and C on the Checklist!"
    BUST_SWERVE_STAR_ON_WHEELIE_BIKE = "City Trial: In the city, bust Swerve Star while riding on Wheelie Bike!"
    BUST_ROCKET_STAR_ON_SLICK_STAR = "City Trial: In the city, bust Rocket Star while riding on Slick Star!"
    PICKUP_100_ITEMS = "City Trial: Pick up a total of over 100 items!"
    FR_CHANGE_AIR_RIDE_MACHINES_10X = "City Trial: Free Run: Change Air Ride Machines 10 times or more!"
    FR_DRIVE_FOR_30_MINUTES = "City Trial: Free Run: Drive for a total of 30 minutes or more!"
    STADIUM_DR1_FINISH_00_24_00 = "Stadium: DRAG RACE 1 Finish in less than 00:24:00!"
    STADIUM_DR3_FINISH_00_35_00 = "Stadium: DRAG RACE 3 Finish in less than 00:35:00!"
    STADIUM_HJ_JUMP_HIGHER_THAN_500_FEET = "Stadium: HIGH JUMP Jump higher than 500 feet!"
    STADIUM_TF_GET_EXACTLY_90_POINTS = "Stadium: TARGET FLIGHT In one game, get exactly 90 points!"
    STADIUM_TF_GET_1500_POINTS = "Stadium: TARGET FLIGHT get more than 1,500 points!"
    STADIUM_AG_AIRBORNE_30_SECONDS = "Stadium: AIR GLIDER stay airborne longer than 30 seconds!"
    STADIUM_DD4_KO_YOUR_RIVALS_5 = "Stadium: DESTRUCTION DERBY 4 In one game, KO your rivals 5 or more times!"
    STADIUM_DD_ALL_KO_ENEMIES_150X = "Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!"
    STADIUM_KM_ALL_KO_1500_ENEMIES = "Stadium: KIRBY MELEE (All) KO over 1,500 enemies!"
    BREAK_5_OF_HUGE_PILLARS_THAT_APPEAR = "City Trial: Break 5 or more of the huge pillars that appear!"
    USE_UP_ONE_OF_RESTORATION_AREAS = "City Trial: Use up one of the restoration areas!"
    BUST_STAR_POLE = "City Trial: Bust the star pole!"
    MAKE_YOUR_WAY_TO_GARDEN_IN_SKY = "City Trial: Make your way to the garden in the sky!"
    USE_GRIND_RAIL_TO_BREAK_INTO_CRATER = "City Trial: Use the grind rail to break into the crater!"
    COPY_CHANCE_WHEEL_BOMB = "City Trial: Get the Bomb ability from the Copy Chance Wheel!"
    ALL_PLAYERS_OFF_MACHINES = "City Trial: Have all players simultaneously get off of their machines!"
    DAMAGE_ALL_3_CPUS = "City Trial: Enter a race with 3 CPU Players and do damage to all of them in the city!"
    GET_10_TOP_SPEED_PATCHES = "City Trial: In one game, get 10 or more Top Speed Patches!"
    GET_10_CHARGE_PATCHES = "City Trial: In one game, get 10 or more Charge Patches!"
    GET_10_DEFENSE_PATCHES = "City Trial: In one game, get 10 or more Defense Patches!"
    USE_SENSOR_BOMBS_TO_KO_RIVALS_3X = "City Trial: Use Sensor Bombs to KO rivals 3 times or more!"
    DRINK_3_ENERGY_DRINKS = "City Trial: In one game, drink 3 or more energy drinks!"
    STADIUM_DR2_29_00_WINGED = "Stadium: DRAG RACE 2 Finish in less than 00:29:00 on Winged Star!"
    STADIUM_DR4_24_00_REX = "Stadium: DRAG RACE 4 Finish in less than 00:24:00 on Rex Wheelie!"
    UNLOCK_HYDRA_CHECKLIST = "City Trial: Unlock Hydra Parts X, Y, and Z on the Checklist!"
    BUST_WARPSTAR_ON_SWERVE_STAR = "City Trial: In the city, bust Warpstar while riding on Swerve Star!"
    BUST_TURBO_STAR_ON_ROCKET_STAR = "City Trial: In the city, bust Turbo Star while riding on Rocket Star!"
    PICKUP_500_ITEMS = "City Trial: pick up a total of over 500 items!"
    BREAK_500_BOXES = "City Trial: break more than 500 boxes!"
    FR_DRIVE_FOR_2_HOURS = "City Trial: Free Run: Drive for a total of 2 hours or more!"
    STADIUM_DR1_FINISH_00_20_00 = "Stadium: DRAG RACE 1 Finish in less than 00:20:00!"
    STADIUM_DR3_FINISH_00_27_00 = "Stadium: DRAG RACE 3 Finish in less than 00:27:00!"
    STADIUM_HJ_JUMP_HIGHER_THAN_1000_FEET = "Stadium: HIGH JUMP Jump higher than 1,000 feet!"
    STADIUM_TF_PERFECT_200 = "Stadium: TARGET FLIGHT In one game, get a perfect score: 200 points!"
    STADIUM_AG_FLY_330_FEET = "Stadium: AIR GLIDER fly more than 330 feet!"
    STADIUM_DD1_KO_YOUR_RIVALS_5 = "Stadium: DESTRUCTION DERBY 1 In one game, KO your rivals 5 or more times!"
    STADIUM_DD5_KO_YOUR_RIVALS_5 = "Stadium: DESTRUCTION DERBY 5 In one game, KO your rivals 5 or more times!"
    STADIUM_KM1_KO_ENEMIES_50X = "Stadium: KIRBY MELEE 1 In one game, KO enemies over 50 times!"
    STADIUM_VSKD_KO_DEDEDE_1MIN = "Stadium: VS. KING DEDEDE KO King Dedede in less than a minute!"
    BREAK_PILLAR_WITHIN_40S = "City Trial: Break a huge pillar within 40 seconds of the time it appears!"
    FILL_IN_100_CHECKLIST_BLOCKS = "City Trial: Fill in over 100 Checklist blocks!"
    BUST_STAR_POLE_10X = "City Trial: Bust the star pole 10 times or more!"
    OPEN_UP_PITFALL_IN_FOREST = "City Trial: Open up the pitfall in the forest!"
    SUPER_JUMP_RAMP_10X = "City Trial: Jump on top of the building 10 times or more using the super jump ramp!"
    COPY_CHANCE_WHEEL_SLEEP = "City Trial: Get the Sleep ability from the Copy Chance Wheel!"
    TIMEOUT_ALL_OFF_MACHINES = "City Trial: Let time run out while all players are off of their machines!"
    GET_50_ITEMS = "City Trial: In one game, get 50 or more items!"
    STADIUM_DD2_KO_A_RIVAL_10X = "Stadium: DESTRUCTION DERBY 2 In one game, KO a rival 10 times or more!"
    STADIUM_DD5_KO_A_RIVAL_10X = "Stadium: DESTRUCTION DERBY 5 In one game, KO a rival 10 times or more!"
    STADIUM_KM2_KO_40_ENEMIES_BY_YOURSELF = "Stadium: KIRBY MELEE 2 In one game, KO over 40 enemies by yourself!"
    USE_GOLD_SPIKES_TO_KO_RIVALS_3X = "City Trial: Use Gold Spikes to KO rivals 3 times or more!"
    STADIUM_DR1_26_00_WARPSTAR = "Stadium: DRAG RACE 1 Finish in less than 00:26:00 on Warpstar!"
    STADIUM_DR3_28_00_SWERVE = "Stadium: DRAG RACE 3 Finish in less than 00:28:00 on Swerve Star!"
    EAT_3_PLATES_OF_SUSHI = "City Trial: In one race, eat 3 or more plates of sushi!"
    BUST_WHEELIE_SCOOTER_ON_COMPACT_STAR = "City Trial: In the city, bust Wheelie Scooter while riding Compact Star!"
    BUST_FORMULA_STAR_ON_TURBO_STAR = "City Trial: In the city, bust Formula Star while riding on Turbo Star!"
    COMPLETE_DRAGOON_AND_HYDRA = "City Trial: In one match, complete both Dragoon and Hydra!"


class ARLocation(StrEnum):
    """Air Ride checklist location names."""

    RACE_100_LAPS = "Air Ride: Race over 100 laps!"
    DEFEAT_300_OF_YOUR_ENEMIES = "Air Ride: Defeat over 300 of your enemies!"
    SWALL_SWORD_KNIGHT_3_AND_FIRST = (
        "Air Ride: Swallow Sword Knight (sword-wielding enemy) 3 times or more and take 1st place!"
    )
    MF_RACE_4800_FEET = "Air Ride: MAGMA FLOWS Race over 4,800 feet in 2 minutes!"
    SWALL_5_GARBAGE_AND_FIRST = "Air Ride: Swallow 5 consecutive garbage enemies (with no copy abilities) and take 1st!"
    FM_RACE_4500_FEET = "Air Ride: FANTASY MEADOWS Race over 4,500 feet in 2 minutes!"
    FILL_IN_100_CHECKLIST_BLOCKS = "Air Ride: Fill in over 100 Checklist blocks!"
    SWORD_CHALLENGE_10_SWINGS = (
        "Air Ride: Sword Challenge: During a race, swing your sword exactly 10 times and take 1st!"
    )
    HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN = "Air Ride: Hit 20 or more rivals with your Quick Spin!"
    CV_FINISH_2_LAPS_IN_UNDER_01_56_00 = "Air Ride: CELESTIAL VALLEY Finish 2 laps in under 01:56:00!"
    BP_FINISH_2_LAPS_IN_UNDER_01_56_00 = "Air Ride: BEANSTALK PARK Finish 2 laps in under 01:56:00!"
    TA_FM_FINISH_01_00_00 = "Air Ride: Time Attack: FANTASY MEADOWS Finish in under 01:00:00!"
    TA_SS_FINISH_02_40_00 = "Air Ride: Time Attack: SKY SANDS Finish in under 02:40:00!"
    TA_MF_FINISH_03_04_00 = "Air Ride: Time Attack: MAGMA FLOWS Finish in under 03:04:00!"
    TA_MP_FINISH_02_48_00 = "Air Ride: Time Attack: MACHINE PASSAGE Finish in under 02:48:00!"
    FR_FM_LAP_00_21_00 = "Air Ride: Free Run: FANTASY MEADOWS Finish 1 lap in under 00:21:00!"
    FR_CV_LAP_01_02_00_ON_SLICK_STAR = "Air Ride: Free Run: CELESTIAL VALLEY Do 1 lap under 01:02:00 on Slick Star!"
    FR_FH_LAP_01_10_00 = "Air Ride: Free Run: FROZEN HILLSIDE Finish 1 lap in under 01:10:00!"
    FR_MF_LAP_01_01_00 = "Air Ride: Free Run: MAGMA FLOWS Finish 1 lap in under 01:01:00!"
    FR_BP_LAP_00_58_00_ON_WINGED_STAR = "Air Ride: Free Run: BEANSTALK PARK Do 1 lap under 00:58:00 on Winged Star!"
    FR_CK_LAP_01_35_00 = "Air Ride: Free Run: CHECKER KNIGHTS Finish 1 lap in under 01:35:00!"
    RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES = "Air Ride: Race all of the standard Air Ride courses!"
    FIRST_WHILE_FLYING_THROUGH_AIR = "Air Ride: Finish in 1st place while flying through the air!"
    FIRST_WITH_WING_ABILITY = "Air Ride: Finish in 1st place with Wing ability!"
    FM_LAP_ABOVE_20_MPH = "Air Ride: FANTASY MEADOWS: Race 1 lap without dropping below 20 mph!"
    CK_BREAK_2_WALLS_AND_FIRST = "Air Ride: CHECKER KNIGHTS: Break at least 2 walls and finish in 1st place!"
    SS_ENTER_QUICKSAND_3_X_AND_FIRST = "Air Ride: SKY SANDS: Enter the quicksand 3 times and finish in 1st place!"
    TA_SS_FINISH_02_40_00_ON_WAGON_STAR = "Air Ride: Time Attack: SKY SANDS Finish in under 02:40:00 on Wagon Star!"
    MF_ALL_BOOST_PANELS_AND_FIRST = "Air Ride: MAGMA FLOWS: Use all of the Boost Panels and finish in 1st place!"
    CV_COPY_CHANCE_WHEEL_TREE = "Air Ride: CELESTIAL VALLEY: Use the Copy Chance Wheel on top of the tree!"
    RACE_300_LAPS = "Air Ride: Race over 300 laps!"
    DEFEAT_1000_OF_YOUR_ENEMIES = "Air Ride: Defeat over 1,000 of your enemies!"
    SWALL_WHEELIE_3_AND_FIRST = "Air Ride: Swallow Wheelie (motorcycle enemy) 3 times or more and take 1st place!"
    MF_FINISH_2_LAPS_IN_UNDER_02_20_00 = "Air Ride: MAGMA FLOWS Finish 2 laps in under 02:20:00!"
    BP_FINISH_2_LAPS_IN_UNDER_02_18_00 = "Air Ride: BEANSTALK PARK Finish 2 laps in under 02:18:00!"
    CV_RACE_6000_FEET = "Air Ride: CELESTIAL VALLEY Race over 6,000 feet in 2 minutes!"
    FM_FINISH_3_LAPS_IN_UNDER_01_20_00 = "Air Ride: FANTASY MEADOWS Finish 3 laps in under 01:20:00!"
    FH_RACE_2_LAPS_IN_UNDER_02_20_00 = "Air Ride: FROZEN HILLSIDE Race 2 laps in under 02:20:00!"
    MP_RACE_4500_FEET = "Air Ride: MACHINE PASSAGE Race over 4,500 feet in 2 minutes!"
    SS_FINISH_2_LAPS_IN_UNDER_01_45_00 = "Air Ride: SKY SANDS Finish 2 laps in under 01:45:00!"
    MP_FINISH_2_LAPS_IN_UNDER_01_48_00 = "Air Ride: MACHINE PASSAGE Finish 2 laps in under 01:48:00!"
    TA_CV_FINISH_03_20_00 = "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 03:20:00!"
    TA_FH_FINISH_03_14_00 = "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:14:00!"
    TA_BP_FINISH_03_10_00 = "Air Ride: Time Attack: BEANSTALK PARK Finish in under 03:10:00!"
    TA_CK_FINISH_04_30_00 = "Air Ride: Time Attack: CHECKER KNIGHTS Finish in under 04:30:00!"
    FR_FM_LAP_00_23_00_ON_WAGON_STAR = "Air Ride: Free Run: FANTASY MEADOWS Do 1 lap under 00:23:00 on Wagon Star!"
    FR_SS_LAP_01_05_00 = "Air Ride: Free Run: SKY SANDS Finish 1 lap in under 01:05:00!"
    FR_FH_LAP_00_58_00 = "Air Ride: Free Run: FROZEN HILLSIDE Finish 1 lap in under 00:58:00!"
    FR_MF_LAP_01_02_00_ON_TURBO_STAR = "Air Ride: Free Run: MAGMA FLOWS Do 1 lap under 01:02:00 on Turbo Star!"
    FR_MP_LAP_01_05_00 = "Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!"
    FR_CK_LAP_01_20_00 = "Air Ride: Free Run: CHECKER KNIGHTS Finish 1 lap in under 01:20:00!"
    LAST_TO_FIRST_FINAL_LAP = "Air Ride: Start the final lap in 4th place and move to 1st to win."
    FIRST_WITH_SLEEP_ABILITY = "Air Ride: Finish in 1st place with Sleep ability!"
    TA_FM_FINISH_01_05_00_ON_SLICK_STAR = (
        "Air Ride: Time Attack: FANTASY MEADOWS Finish in under 01:05:00 on Slick Star!"
    )
    BP_3_LAPS_NO_FERRIS_WHEEL = "Air Ride: BEANSTALK PARK: Race over 3 laps without riding the Ferris wheel!"
    CK_SWALL_20_AND_FIRST = "Air Ride: CHECKER KNIGHTS: Swallow over 20 enemies and finish in 1st place!"
    TA_CV_FINISH_02_58_00_ON_JET_STAR = "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 02:58:00 on Jet Star!"
    MP_FIRST_NO_WALL_TOUCH = "Air Ride: MACHINE PASSAGE: Finish in 1st place without touching the walls even once!"
    TA_FH_FINISH_03_10_00_ON_TURBO_STAR = (
        "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:10:00 on Turbo Star!"
    )
    TA_BP_FINISH_03_00_00_ON_ROCKET_STAR = (
        "Air Ride: Time Attack: BEANSTALK PARK Finish in under 03:00:00 on Rocket Star!"
    )
    GLIDE_FOR_30_MINUTES = "Air Ride: Glide for more than 30 minutes!"
    SWALL_CHILLY_3_AND_FIRST = "Air Ride: Swallow Chilly (snowman enemy) 3 or more times and take 1st place!"
    REACH_GOAL_3X_NOT_FR = "Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!"
    SWALL_200_ENEMIES = "Air Ride: Swallow 200 or more enemies!"
    MP_FINISH_2_LAPS_IN_UNDER_02_10_00 = "Air Ride: MACHINE PASSAGE Finish 2 laps in under 02:10:00!"
    SS_RACE_4000_FEET = "Air Ride: SKY SANDS Race over 4,000 feet in 2 minutes!"
    CV_FINISH_2_LAPS_IN_UNDER_02_20_00 = "Air Ride: CELESTIAL VALLEY Finish 2 laps in under 02:20:00!"
    TORNADO_CHALLENGE_15_KO = (
        "Air Ride: Tornado Challenge: Defeat over 15 enemies as Tornado Kirby and finish in 1st place!"
    )
    BP_RACE_5500_FEET = "Air Ride: BEANSTALK PARK Race over 5,500 feet in 2 minutes!"
    FH_FINISH_2_LAPS_IN_UNDER_01_56_00 = "Air Ride: FROZEN HILLSIDE Finish 2 laps in under 01:56:00!"
    CK_FINISH_2_LAPS_IN_UNDER_02_40_00 = "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 02:40:00!"
    TA_CV_FINISH_02_56_00 = "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 02:56:00!"
    TA_FH_FINISH_02_50_00 = "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 02:50:00!"
    TA_BP_FINISH_02_55_00 = "Air Ride: Time Attack: BEANSTALK PARK Finish in under 02:55:00!"
    TA_CK_FINISH_04_00_00 = "Air Ride: Time Attack: CHECKER KNIGHTS Finish in under 04:00:00!"
    FR_CV_LAP_01_10_00 = "Air Ride: Free Run: CELESTIAL VALLEY Finish 1 lap in under 01:10:00!"
    FR_SS_LAP_00_53_00 = "Air Ride: Free Run: SKY SANDS Finish 1 lap in under 00:53:00!"
    FR_FH_LAP_01_10_00_ON_FORMULA_STAR = "Air Ride: Free Run: FROZEN HILLSIDE Do 1 lap under 01:10:00 on Formula Star!"
    FR_BP_LAP_01_07_00 = "Air Ride: Free Run: BEANSTALK PARK Finish 1 lap in under 01:07:00!"
    FR_MP_LAP_00_56_00 = "Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 00:56:00!"
    FR_CK_LAP_01_25_00_ON_ROCKET_STAR = "Air Ride: Free Run: CHECKER KNIGHTS Do 1 lap under 01:25:00 on Rocket Star!"
    FINISH_SPINNING_AND_FIRST = "Air Ride: Cross the finish line while spinning and take 1st place!"
    FIRST_WITH_FIRE_ABILITY = "Air Ride: Finish in 1st place with Fire ability!"
    DROP_FROM_CLIFFS_3X = "Air Ride: In one game, drop from the cliffs 3 times!"
    BP_SWALL_20_AND_FIRST = "Air Ride: BEANSTALK PARK: Swallow over 20 enemies and take 1st place!"
    FH_SPLIT_20_ICE_AND_FIRST = "Air Ride: FROZEN HILLSIDE: Split at least 20 ice platforms and finish in 1st place!"
    SS_TRAPDOOR_3X_AND_FIRST = "Air Ride: SKY SANDS: Open the trapdoor exactly 3 times and finish in 1st place!"
    MF_USE_ALL_VOLCANO_RAILS_AND_FIRST = "Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!"
    CV_RIDE_BOTH_BRIDGE_RAILS = (
        "Air Ride: CELESTIAL VALLEY: Over one race, ride on both the left and right bridge railings!"
    )
    TA_MP_FINISH_02_50_00_ON_REX_WHEELIE = (
        "Air Ride: Time Attack: MACHINE PASSAGE Finish in under 02:50:00 on Rex Wheelie!"
    )
    GLIDE_FOR_1_HOUR = "Air Ride: Glide for more than 1 hour!"
    SWALL_PLASMA_WISP_3_AND_FIRST = (
        "Air Ride: Swallow Plasma Wisp (electrical enemy) 3 or more times and take 1st place!"
    )
    CK_RACE_5500_FEET = "Air Ride: CHECKER KNIGHTS Race over 5,500 feet in 2 minutes!"
    DEFEAT_100_ENEMIES_WITH_EXHALED_STARS = "Air Ride: Defeat 100 or more enemies with exhaled stars!"
    CK_FINISH_2_LAPS_IN_UNDER_03_05_00 = "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!"
    FH_RACE_5300_FEET = "Air Ride: FROZEN HILLSIDE Race over 5,300 feet in 2 minutes!"
    SS_FINISH_2_LAPS_IN_UNDER_02_05_00 = "Air Ride: SKY SANDS Finish 2 laps in under 02:05:00!"
    DEFEAT_10_ENEMIES_USING_QUICK_SPIN = "Air Ride: Defeat 10 or more enemies using the Quick Spin!"
    FM_FINISH_3_LAPS_IN_UNDER_01_03_00 = "Air Ride: FANTASY MEADOWS Finish 3 laps in under 01:03:00!"
    MF_FINISH_2_LAPS_IN_UNDER_02_01_00 = "Air Ride: MAGMA FLOWS Finish 2 laps in under 02:01:00!"
    TA_FM_FINISH_01_12_00 = "Air Ride: Time Attack: FANTASY MEADOWS Finish in under 01:12:00!"
    TA_SS_FINISH_03_10_00 = "Air Ride: Time Attack: SKY SANDS Finish in under 03:10:00!"
    TA_MF_FINISH_03_20_00 = "Air Ride: Time Attack: MAGMA FLOWS Finish in under 03:20:00!"
    TA_MP_FINISH_03_10_00 = "Air Ride: Time Attack: MACHINE PASSAGE Finish in under 03:10:00!"
    FR_FM_LAP_00_24_00 = "Air Ride: Free Run: FANTASY MEADOWS Finish 1 lap in under 00:24:00!"
    FR_CV_LAP_00_57_00 = "Air Ride: Free Run: CELESTIAL VALLEY Finish 1 lap in under 00:57:00!"
    FR_SS_LAP_01_05_00_ON_BULK_STAR = "Air Ride: Free Run: SKY SANDS Do 1 lap under 01:05:00 on Bulk Star!"
    FR_MF_LAP_01_10_00 = "Air Ride: Free Run: MAGMA FLOWS Finish 1 lap in under 01:10:00!"
    FR_BP_LAP_00_58_00 = "Air Ride: Free Run: BEANSTALK PARK Finish 1 lap in under 00:58:00!"
    FR_MP_LAP_00_57_00_ON_SWERVE_STAR = "Air Ride: Free Run: MACHINE PASSAGE Do 1 lap under 00:57:00 on Swerve Star!"
    MAKE_YOUR_LAP_X_LAST_TWO_DIGITS_SAME = "Air Ride: Make your lap time's last two digits the same!"
    FIRST_WHILE_TAKING_DAMAGE = "Air Ride: Finish in 1st place while taking damage!"
    FIRST_WITH_NEEDLE_ABILITY = "Air Ride: Finish in 1st place with Needle ability!"
    FM_SWALL_20_AND_FIRST = "Air Ride: FANTASY MEADOWS: Swallow over 20 enemies and take 1st place!"
    CK_USE_SPIN_PANELS_7_X_AND_FIRST = "Air Ride: CHECKER KNIGHTS: Use spin panels 7 times or more and take 1st place!"
    SS_BREAK_ALL_CORAL_AND_FIRST = "Air Ride: SKY SANDS: Break all of the coral and finish in 1st place!"
    MP_CANNON_SHOOT_3 = "Air Ride: MACHINE PASSAGE: Shoot 3 characters out of the cannon at one time!"
    MF_BUMP_INTO_A_FLAMING_DRAGON = "Air Ride: MAGMA FLOWS: Bump into a flaming dragon!"
    TA_MF_FINISH_03_15_00_ON_SHADOW_STAR = "Air Ride: Time Attack: MAGMA FLOWS Finish in under 03:15:00 on Shadow Star!"
    TA_CK_FINISH_03_55_00_ON_WARPSTAR = "Air Ride: Time Attack: CHECKER KNIGHTS Finish in under 03:55:00 on Warpstar!"


class TRLocation(StrEnum):
    """Top Ride checklist location names."""

    CROSS_GOAL_20 = "Top Ride: Cross the goal 20 or more times!"
    FR_RACE_100_LAPS = "Top Ride: Free Run: Race more than 100 laps!"
    QUICK_SPIN_20_AND_FIRST = "Top Ride: Do 20 or more Quick Spins in one lap and finish 1st!"
    ALL_COURSES_NO_BOOST = "Top Ride: Finish all courses without using Boost!"
    FIRST_WHILE_HOLDING_HAMMER = "Top Ride: Take 1st place while holding the Hammer!"
    GET_20_INVINCIBLE_CANDY_ITEMS = "Top Ride: Get more than 20 Invincible Candy items!"
    HIT_ENEMIES_3_X_WITH_BOMB_ITEMS = "Top Ride: In one game, hit enemies 3 times or more with Bomb items!"
    GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: GRASS Finish 1st with CPUs set to level 5!"
    GRASS_FIRST_AND_HIT_5_DASH_PANELS = "Top Ride: GRASS Finish 1st and hit 5 or more Dash Panels!"
    SAND_FIRST_WITHOUT_USING_BOOST = "Top Ride: SAND Take 1st place without using Boost!"
    SAND_RACE_100_LAPS = "Top Ride: SAND Race more than 100 laps!"
    SAND_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: SAND Finish 1st 5 seconds faster than #2!"
    SKY_FIRST_10X = "Top Ride: SKY Take 1st place 10 times or more!"
    SKY_FIRST_WITHOUT_USING_JUMP_PLATE = "Top Ride: SKY Finish 1st without using the Jump Plate!"
    FIRE_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: FIRE Finish 1st with CPUs set to level 5!"
    FIRE_CAUSE_A_HUGE_ERUPTION_3X = "Top Ride: FIRE Cause a huge eruption 3 times or more!"
    WATER_FIRST_WITHOUT_USING_BOOST = "Top Ride: WATER Take 1st place without using Boost!"
    WATER_RACE_100_LAPS = "Top Ride: WATER Race more than 100 laps!"
    LIGHT_FIRST_WITHOUT_USING_BOOST = "Top Ride: LIGHT Take 1st place without using Boost!"
    LIGHT_RACE_100_LAPS = "Top Ride: LIGHT Race more than 100 laps!"
    LIGHT_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: LIGHT Finish 1st 5 seconds faster than #2!"
    METAL_FIRST_10X = "Top Ride: METAL Take 1st place 10 times or more!"
    METAL_FIRST_AND_HIT_SWITCH_10X = "Top Ride: METAL Take 1st and hit the switch 10 times or more!"
    TA_SAND_FINISH_00_35_00 = "Top Ride: Time Attack: SAND Finish in under 00:35:00!"
    TA_FIRE_FINISH_00_46_00 = "Top Ride: Time Attack: FIRE Finish in under 00:46:00!"
    TA_LIGHT_FINISH_00_33_00 = "Top Ride: Time Attack: LIGHT Finish in under 00:33:00!"
    TA_METAL_FINISH_00_51_00 = "Top Ride: Time Attack: METAL Finish in under 00:51:00!"
    FR_SKY_LAP_00_11_00 = "Top Ride: Free Run: SKY Do one lap in under 00:11:00!"
    FR_GRASS_LAP_00_04_50 = "Top Ride: Free Run: GRASS Do one lap in under 00:04:50!"
    FR_WATER_LAP_00_10_50 = "Top Ride: Free Run: WATER Do one lap in under 00:10:50!"
    RACE_300_LAPS = "Top Ride: Race over 300 laps!"
    TA_CROSS_GOAL_30 = "Top Ride: Time Attack: Cross the goal 30 or more times!"
    NOITEMS_ALL_COURSES = "Top Ride: (No 'Zero Items' rule) Complete all courses without using items!"
    FIRST_ON_ALL_COURSES_WITHOUT_BOOST = "Top Ride: Finish 1st on all courses without Boost!"
    FIRST_WITH_1_LAP_BETWEEN_YOU_AND_NO2 = "Top Ride: Finish 1st with 1 lap between you and #2!"
    GET_20_WALKY_ITEMS = "Top Ride: Get more than 20 Walky items!"
    GET_18_DIFFERENT_TYPES_OF_ITEMS = "Top Ride: Get over 18 different types of items!"
    GRASS_FIRST_10X = "Top Ride: GRASS Take 1st place 10 times or more!"
    GRASS_IN_ONE_RACE_DROP_30_TREE_BOMBS = "Top Ride: GRASS In one race, drop 30 or more tree bombs!"
    SAND_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: SAND Finish 1st with CPUs set to level 5!"
    SAND_FIRST_AND_CATCH_WORM_3 = "Top Ride: SAND Take 1st and catch the worm 3 or more times!"
    SKY_NOITEMS_FIRST = "Top Ride: SKY (No 'Zero Items' rule) Take 1st place without using items!"
    SKY_FINISH_6_LAPS_IN_UNDER_01_02_00 = "Top Ride: SKY Finish 6 laps in under 01:02:00!"
    SKY_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: SKY Finish 1st 5 seconds faster than #2!"
    FIRE_FIRST_10X = "Top Ride: FIRE Take 1st place 10 times or more!"
    FIRE_FIRST_WHILE_HOLDING_FIRE_ITEM = "Top Ride: FIRE Finish 1st while holding the Fire item."
    WATER_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: WATER Finish 1st with CPUs set to level 5!"
    WATER_FIRST_AND_ENTER_FALLS_5X = "Top Ride: WATER Take 1st and enter the falls 5 times or more!"
    LIGHT_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: LIGHT Finish 1st with CPUs set to level 5!"
    LIGHT_RIDE_GRIND_RAIL_50X = "Top Ride: LIGHT Ride the grind rail 50 times or more!"
    METAL_NOITEMS_FIRST = "Top Ride: METAL (No 'Zero Items' rule) Take 1st place without using items!"
    METAL_FINISH_5_LAPS_IN_UNDER_00_58_00 = "Top Ride: METAL Finish 5 laps in under 00:58:00!"
    METAL_FIRST_AND_BREAK_5_GEAR_WALLS = "Top Ride: METAL Take 1st and break 5 or more gear walls!"
    TA_LIGHT_FINISH_00_38_00 = "Top Ride: Time Attack: LIGHT Finish in under 00:38:00!"
    TA_METAL_FINISH_00_57_00 = "Top Ride: Time Attack: METAL Finish in under 00:57:00!"
    TA_SKY_FINISH_00_47_00 = "Top Ride: Time Attack: SKY Finish in under 00:47:00!"
    FR_GRASS_LAP_00_06_00 = "Top Ride: Free Run: GRASS Do one lap in under 00:06:00!"
    FR_WATER_LAP_00_12_00 = "Top Ride: Free Run: WATER Do one lap in under 00:12:00!"
    FR_SAND_LAP_00_05_00 = "Top Ride: Free Run: SAND Do one lap in under 00:05:00!"
    FR_FIRE_LAP_00_06_50 = "Top Ride: Free Run: FIRE Do one lap in under 00:06:50!"
    COMPETE_IN_10_MULTIPLAYER_RACES = "Top Ride: Compete in more than 10 multiplayer races!"
    FIRST_ON_ALL_COURSES = "Top Ride: Take 1st place on all courses!"
    NOITEMS_FIRST_ALL_COURSES = "Top Ride: (No 'Zero Items' rule) Finish 1st on all courses using no items!"
    GET_SAME_ITEM_3_X_IN_ONE_RACE = "Top Ride: Get the same item 3 times in one race!"
    FIRST_WITH_2_LAPS_BETWEEN_YOU_AND_NO2 = "Top Ride: Finish 1st with 2 laps between you and #2!"
    TORCH_3_RIVALS_USING_ONE_FIRE_ITEM = "Top Ride: Torch 3 or more rivals using one Fire item!"
    GRASS_NOITEMS_FIRST = "Top Ride: GRASS (No 'Zero Items' rule) Take 1st place without using items!"
    GRASS_FINISH_7_LAPS_IN_UNDER_00_43_00 = "Top Ride: GRASS Finish 7 laps in under 00:43:00!"
    GRASS_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: GRASS Finish 1st 5 seconds faster than #2!"
    SAND_FIRST_10X = "Top Ride: SAND Take 1st place 10 times or more!"
    SAND_DROP_INTO_ANT_DOOM_50X = "Top Ride: SAND Drop into Ant Doom 50 times or more!"
    SKY_FIRST_WITHOUT_USING_BOOST = "Top Ride: SKY Take 1st place without using Boost!"
    SKY_RACE_100_LAPS = "Top Ride: SKY Race more than 100 laps!"
    FIRE_NOITEMS_FIRST = "Top Ride: FIRE (No 'Zero Items' rule) Take 1st place without using items!"
    FIRE_FINISH_6_LAPS_IN_UNDER_00_53_00 = "Top Ride: FIRE Finish 6 laps in under 00:53:00!"
    FIRE_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: FIRE Finish 1st 5 seconds faster than #2!"
    WATER_FIRST_10X = "Top Ride: WATER Take 1st place 10 times or more!"
    WATER_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: WATER Finish 1st 5 seconds faster than #2!"
    LIGHT_FIRST_10X = "Top Ride: LIGHT Take 1st place 10 times or more!"
    LIGHT_FIRST_AND_GRIND_RAIL_5X = "Top Ride: LIGHT Take 1st place and grind the rail 5 times or more!"
    METAL_FIRST_WITHOUT_USING_BOOST = "Top Ride: METAL Take 1st place without using Boost!"
    METAL_RACE_100_LAPS = "Top Ride: METAL Race more than 100 laps!"
    METAL_FIRST_5_SECONDS_FASTER_THAN_NO2 = "Top Ride: METAL Finish 1st 5 seconds faster than #2!"
    TA_SKY_FINISH_00_57_00 = "Top Ride: Time Attack: SKY Finish in under 00:57:00!"
    TA_GRASS_FINISH_00_28_00 = "Top Ride: Time Attack: GRASS Finish in under 00:28:00!"
    TA_WATER_FINISH_00_56_00 = "Top Ride: Time Attack: WATER Finish in under 00:56:00!"
    FR_SAND_LAP_00_06_50 = "Top Ride: Free Run: SAND Do one lap in under 00:06:50!"
    FR_FIRE_LAP_00_08_00 = "Top Ride: Free Run: FIRE Do one lap in under 00:08:00!"
    FR_LIGHT_LAP_00_06_00 = "Top Ride: Free Run: LIGHT Do one lap in under 00:06:00!"
    FR_METAL_LAP_00_09_50 = "Top Ride: Free Run: METAL Do one lap in under 00:09:50!"
    COMPETE_IN_50_MULTIPLAYER_RACES = "Top Ride: Compete in more than 50 multiplayer races!"
    LAP_NO_WALLS_AND_FIRST = "Top Ride: Race one lap without hitting a wall and finish 1st!"
    COLLECT_500_ITEMS = "Top Ride: Collect 500 items or more!"
    FIRST_WHILE_DOING_A_QUICK_SPIN = "Top Ride: Take 1st place while doing a Quick Spin!"
    GET_20_SPINNER_ITEMS = "Top Ride: Get more than 20 Spinner items!"
    BUZZ_SAW_SEND_3_RIVALS = "Top Ride: Send 3 or more rivals sailing using one Buzz Saw item!"
    GRASS_FIRST_WITHOUT_USING_BOOST = "Top Ride: GRASS Take 1st place without using Boost!"
    GRASS_RACE_100_LAPS = "Top Ride: GRASS Race more than 100 laps!"
    SAND_NOITEMS_FIRST = "Top Ride: SAND (No 'Zero Items' rule) Take 1st place without using items!"
    SAND_FINISH_7_LAPS_IN_UNDER_00_52_00 = "Top Ride: SAND Finish 7 laps in under 00:52:00!"
    SAND_ANT_DOOM_20X = "Top Ride: SAND Drop into Ant Doom 20 times in one game!"
    SKY_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: SKY Finish 1st with CPUs set to level 5!"
    SKY_FIRST_AND_HIT_ISLE_KNOB_5 = "Top Ride: SKY Take 1st and hit the Isle Knob 5 or more times!"
    FIRE_FIRST_WITHOUT_USING_BOOST = "Top Ride: FIRE Take 1st place without using Boost!"
    FIRE_RACE_100_LAPS = "Top Ride: FIRE Race more than 100 laps!"
    WATER_NOITEMS_FIRST = "Top Ride: WATER (No 'Zero Items' rule) Take 1st place without using items!"
    WATER_FINISH_5_LAPS_IN_UNDER_01_02_00 = "Top Ride: WATER Finish 5 laps in under 01:02:00!"
    LIGHT_NOITEMS_FIRST = "Top Ride: LIGHT (No 'Zero Items' rule) Take 1st place without using items!"
    LIGHT_FINISH_6_LAPS_IN_UNDER_00_43_00 = "Top Ride: LIGHT Finish 6 laps in under 00:43:00!"
    LIGHT_FIRST_AND_BUST_6_COLUMNS = "Top Ride: LIGHT Finish 1st and bust 6 or more columns!"
    METAL_FIRST_WITH_CPUS_SET_TO_LEVEL_5 = "Top Ride: METAL Finish 1st with CPUs set to level 5!"
    METAL_FIRST_NO_GEAR_WALLS = "Top Ride: METAL Take 1st without breaking any gear walls!"
    TA_GRASS_FINISH_00_33_00 = "Top Ride: Time Attack: GRASS Finish in under 00:33:00!"
    TA_WATER_FINISH_01_06_00 = "Top Ride: Time Attack: WATER Finish in under 01:06:00!"
    TA_SAND_FINISH_00_29_00 = "Top Ride: Time Attack: SAND Finish in under 00:29:00!"
    TA_FIRE_FINISH_00_39_00 = "Top Ride: Time Attack: FIRE Finish in under 00:39:00!"
    FR_LIGHT_LAP_00_07_50 = "Top Ride: Free Run: LIGHT Do one lap in under 00:07:50!"
    FR_METAL_LAP_00_11_50 = "Top Ride: Free Run: METAL Do one lap in under 00:11:50!"
    FR_SKY_LAP_00_09_00 = "Top Ride: Free Run: SKY Do one lap in under 00:09:00!"
    FILL_IN_100_CHECKLIST_BLOCKS = "Top Ride: Fill in over 100 Checklist blocks!"


CITY_TRIAL_LOCATION_TABLE: dict[str, KARLocationData] = {
    CTLocation.RACE_60_MILES: KARLocationData(1, KARRegion.CITY_TRIAL),
    CTLocation.RACE_200_MILES: KARLocationData(2, KARRegion.CITY_TRIAL),
    CTLocation.PICKUP_100_ITEMS: KARLocationData(3, KARRegion.CITY_TRIAL),
    CTLocation.PICKUP_500_ITEMS: KARLocationData(4, KARRegion.CITY_TRIAL),
    CTLocation.PICKUP_1000_ITEMS: KARLocationData(5, KARRegion.CITY_TRIAL),
    CTLocation.PICKUP_3000_ITEMS: KARLocationData(6, KARRegion.CITY_TRIAL),
    CTLocation.FR_CHANGE_AIR_RIDE_MACHINES_10X: KARLocationData(7, KARRegion.CT_FREE_RUN),
    CTLocation.BREAK_500_BOXES: KARLocationData(8, KARRegion.CITY_TRIAL),
    CTLocation.BREAK_1000_BOXES: KARLocationData(9, KARRegion.CITY_TRIAL),
    CTLocation.FR_DRIVE_FOR_10_MINUTES: KARLocationData(10, KARRegion.CT_FREE_RUN),
    CTLocation.FR_DRIVE_FOR_30_MINUTES: KARLocationData(11, KARRegion.CT_FREE_RUN),
    CTLocation.FR_DRIVE_FOR_2_HOURS: KARLocationData(12, KARRegion.CT_FREE_RUN),
    CTLocation.STADIUM_PLAY_10_STADIUM_MODES: KARLocationData(13, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_PLAY_20_STADIUM_MODES: KARLocationData(14, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_DR1_FINISH_00_24_00: KARLocationData(15, KARRegion.STADIUM_DR1),
    CTLocation.STADIUM_DR1_FINISH_00_20_00: KARLocationData(16, KARRegion.STADIUM_DR1),
    CTLocation.STADIUM_DR2_FINISH_00_24_00: KARLocationData(17, KARRegion.STADIUM_DR2),
    CTLocation.STADIUM_DR2_FINISH_00_20_00: KARLocationData(18, KARRegion.STADIUM_DR2),
    CTLocation.STADIUM_DR3_FINISH_00_35_00: KARLocationData(19, KARRegion.STADIUM_DR3),
    CTLocation.STADIUM_DR3_FINISH_00_27_00: KARLocationData(20, KARRegion.STADIUM_DR3),
    CTLocation.STADIUM_DR4_FINISH_00_24_00: KARLocationData(21, KARRegion.STADIUM_DR4),
    CTLocation.STADIUM_DR4_FINISH_00_19_00: KARLocationData(22, KARRegion.STADIUM_DR4),
    CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_500_FEET: KARLocationData(23, KARRegion.STADIUM_HJ),
    CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_1000_FEET: KARLocationData(24, KARRegion.STADIUM_HJ),
    CTLocation.STADIUM_HJ_AIRBORNE_10_SECONDS: KARLocationData(25, KARRegion.STADIUM_HJ),
    CTLocation.STADIUM_TF_GET_150_POINTS: KARLocationData(26, KARRegion.STADIUM_TF),
    CTLocation.STADIUM_TF_GET_EXACTLY_90_POINTS: KARLocationData(27, KARRegion.STADIUM_TF),
    CTLocation.STADIUM_TF_PERFECT_200: KARLocationData(28, KARRegion.STADIUM_TF),
    CTLocation.STADIUM_TF_AIRBORNE_15_SECONDS: KARLocationData(29, KARRegion.STADIUM_TF),
    CTLocation.STADIUM_TF_PLAY_15X: KARLocationData(30, KARRegion.STADIUM_TF),
    CTLocation.STADIUM_TF_GET_1500_POINTS: KARLocationData(31, KARRegion.STADIUM_TF),
    CTLocation.STADIUM_AG_FLY_330_FEET: KARLocationData(32, KARRegion.STADIUM_AG),
    CTLocation.STADIUM_AG_FLY_660_FEET: KARLocationData(33, KARRegion.STADIUM_AG),
    CTLocation.STADIUM_AG_FLY_1300_FEET: KARLocationData(34, KARRegion.STADIUM_AG),
    CTLocation.STADIUM_AG_AIRBORNE_30_SECONDS: KARLocationData(35, KARRegion.STADIUM_AG),
    CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5: KARLocationData(36, KARRegion.STADIUM_DD1),
    CTLocation.STADIUM_DD2_KO_YOUR_RIVALS_5: KARLocationData(37, KARRegion.STADIUM_DD2),
    CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5: KARLocationData(38, KARRegion.STADIUM_DD3),
    CTLocation.STADIUM_DD4_KO_YOUR_RIVALS_5: KARLocationData(39, KARRegion.STADIUM_DD4),
    CTLocation.STADIUM_DD5_KO_YOUR_RIVALS_5: KARLocationData(40, KARRegion.STADIUM_DD5),
    CTLocation.STADIUM_DD1_BUST_ALL_ROCKS_ON_FIELD: KARLocationData(41, KARRegion.STADIUM_DD1),
    CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X: KARLocationData(42, KARRegion.STADIUM_DD_ALL),
    CTLocation.STADIUM_DD_ALL_KO_ENEMIES_150X: KARLocationData(43, KARRegion.STADIUM_DD_ALL),
    CTLocation.STADIUM_KM1_KO_ENEMIES_50X: KARLocationData(44, KARRegion.STADIUM_KM1),
    CTLocation.STADIUM_KM2_KO_ENEMIES_30X: KARLocationData(45, KARRegion.STADIUM_KM2),
    CTLocation.STADIUM_KM_ALL_KO_500_ENEMIES: KARLocationData(46, KARRegion.STADIUM_KM_ALL),
    CTLocation.STADIUM_KM_ALL_KO_1500_ENEMIES: KARLocationData(47, KARRegion.STADIUM_KM_ALL),
    CTLocation.STADIUM_VSKD_KO_DEDEDE_1MIN: KARLocationData(48, KARRegion.STADIUM_VSKD),
    CTLocation.DO_SOME_DAMAGE_TO_DYNA_BLADE: KARLocationData(49, KARRegion.CITY_TRIAL),
    CTLocation.GET_TRAMPLED_BY_DYNA_BLADE: KARLocationData(50, KARRegion.CITY_TRIAL),
    CTLocation.BREAK_5_OF_HUGE_PILLARS_THAT_APPEAR: KARLocationData(51, KARRegion.CITY_TRIAL),
    CTLocation.BREAK_PILLAR_WITHIN_40S: KARLocationData(52, KARRegion.CITY_TRIAL),
    CTLocation.STEAL_8_FROM_TAC: KARLocationData(53, KARRegion.CITY_TRIAL),
    CTLocation.THE_METEOR_ATTACKS_CITY_3: KARLocationData(54, KARRegion.CITY_TRIAL),
    CTLocation.USE_UP_ONE_OF_RESTORATION_AREAS: KARLocationData(55, KARRegion.CITY_TRIAL),
    CTLocation.FILL_IN_100_CHECKLIST_BLOCKS: KARLocationData(56, KARRegion.CITY_TRIAL),
    CTLocation.ENTER_CASTLE_CHAMBER: KARLocationData(57, KARRegion.CITY_TRIAL),
    CTLocation.FLY_THROUGH_RINGS_IN_SKY_5X: KARLocationData(58, KARRegion.CITY_TRIAL),
    CTLocation.BUST_STAR_POLE: KARLocationData(59, KARRegion.CITY_TRIAL),
    CTLocation.BUST_STAR_POLE_10X: KARLocationData(60, KARRegion.CITY_TRIAL),
    CTLocation.OPEN_ALL_VOLCANO_HOLES: KARLocationData(61, KARRegion.CITY_TRIAL),
    CTLocation.LET_WATERWHEEL_CARRY_YOU_10X: KARLocationData(62, KARRegion.CITY_TRIAL),
    CTLocation.MAKE_YOUR_WAY_TO_GARDEN_IN_SKY: KARLocationData(63, KARRegion.CITY_TRIAL),
    CTLocation.OPEN_UP_PITFALL_IN_FOREST: KARLocationData(64, KARRegion.CITY_TRIAL),
    CTLocation.HIGH_PLAINS_HOLE_3X: KARLocationData(65, KARRegion.CITY_TRIAL),
    CTLocation.BREAK_ALL_ROCKS: KARLocationData(66, KARRegion.CITY_TRIAL),
    CTLocation.USE_GRIND_RAIL_TO_BREAK_INTO_CRATER: KARLocationData(67, KARRegion.CITY_TRIAL),
    CTLocation.SUPER_JUMP_RAMP_10X: KARLocationData(68, KARRegion.CITY_TRIAL),
    CTLocation.DESTROY_ALL_HOUSES: KARLocationData(69, KARRegion.CITY_TRIAL),
    CTLocation.KNOCK_DOWN_ALL_OF_TREES_IN_FOREST: KARLocationData(70, KARRegion.CITY_TRIAL),
    CTLocation.COPY_CHANCE_WHEEL_BOMB: KARLocationData(71, KARRegion.CITY_TRIAL),
    CTLocation.COPY_CHANCE_WHEEL_SLEEP: KARLocationData(72, KARRegion.CITY_TRIAL),
    CTLocation.GET_10_ITEMS_IN_20S: KARLocationData(73, KARRegion.CITY_TRIAL),
    CTLocation.DAMAGE_RIVAL_WITHIN_10S: KARLocationData(74, KARRegion.CITY_TRIAL),
    CTLocation.ALL_PLAYERS_OFF_MACHINES: KARLocationData(75, KARRegion.CITY_TRIAL),
    CTLocation.TIMEOUT_ALL_OFF_MACHINES: KARLocationData(76, KARRegion.CITY_TRIAL),
    CTLocation.TIMEOUT_ALL_ON_RAILS: KARLocationData(77, KARRegion.CITY_TRIAL),
    CTLocation.BREAK_A_CPUS_MACHINE_5_X: KARLocationData(78, KARRegion.CITY_TRIAL),
    CTLocation.DAMAGE_ALL_3_CPUS: KARLocationData(79, KARRegion.CITY_TRIAL),
    CTLocation.GET_50_ITEMS: KARLocationData(80, KARRegion.CITY_TRIAL),
    CTLocation.GET_10_BOOST_PATCHES: KARLocationData(81, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_DD1_KO_A_RIVAL_10X: KARLocationData(82, KARRegion.STADIUM_DD1),
    CTLocation.GET_10_TOP_SPEED_PATCHES: KARLocationData(83, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_DD2_KO_A_RIVAL_10X: KARLocationData(84, KARRegion.STADIUM_DD2),
    CTLocation.GET_10_TURN_PATCHES: KARLocationData(85, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_DD4_KO_A_RIVAL_10X: KARLocationData(86, KARRegion.STADIUM_DD4),
    CTLocation.GET_10_CHARGE_PATCHES: KARLocationData(87, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_DD5_KO_A_RIVAL_10X: KARLocationData(88, KARRegion.STADIUM_DD5),
    CTLocation.GET_10_WEIGHT_PATCHES: KARLocationData(89, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_KM1_KO_75_ENEMIES_BY_YOURSELF: KARLocationData(90, KARRegion.STADIUM_KM1),
    CTLocation.GET_10_DEFENSE_PATCHES: KARLocationData(91, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_KM2_KO_40_ENEMIES_BY_YOURSELF: KARLocationData(92, KARRegion.STADIUM_KM2),
    CTLocation.GET_10_GLIDE_PATCHES: KARLocationData(93, KARRegion.CITY_TRIAL),
    CTLocation.GET_30_GLIDE_PATCHES: KARLocationData(94, KARRegion.CITY_TRIAL),
    CTLocation.USE_SENSOR_BOMBS_TO_KO_RIVALS_3X: KARLocationData(95, KARRegion.CITY_TRIAL),
    CTLocation.USE_GOLD_SPIKES_TO_KO_RIVALS_3X: KARLocationData(96, KARRegion.CITY_TRIAL),
    CTLocation.USE_FIREWORKS_TO_KO_RIVALS_10X: KARLocationData(97, KARRegion.CITY_TRIAL),
    CTLocation.EAT_2_MAXIM_TOMATOES: KARLocationData(98, KARRegion.CITY_TRIAL),
    CTLocation.DRINK_3_ENERGY_DRINKS: KARLocationData(99, KARRegion.CITY_TRIAL),
    CTLocation.STADIUM_DR1_26_00_WARPSTAR: KARLocationData(100, KARRegion.STADIUM_DR1),
    CTLocation.STADIUM_DR1_17_00_FORMULA: KARLocationData(101, KARRegion.STADIUM_DR1),
    CTLocation.STADIUM_DR2_27_00_WAGON: KARLocationData(102, KARRegion.STADIUM_DR2),
    CTLocation.STADIUM_DR2_29_00_WINGED: KARLocationData(103, KARRegion.STADIUM_DR2),
    CTLocation.STADIUM_DR3_28_00_SWERVE: KARLocationData(104, KARRegion.STADIUM_DR3),
    CTLocation.STADIUM_DR3_31_00_WHEELIE_BIKE: KARLocationData(105, KARRegion.STADIUM_DR3),
    CTLocation.STADIUM_DR4_33_00_TURBO: KARLocationData(106, KARRegion.STADIUM_DR4),
    CTLocation.STADIUM_DR4_24_00_REX: KARLocationData(107, KARRegion.STADIUM_DR4),
    CTLocation.EAT_3_PLATES_OF_SUSHI: KARLocationData(108, KARRegion.CITY_TRIAL),
    CTLocation.EAT_3_HOT_DOGS: KARLocationData(109, KARRegion.CITY_TRIAL),
    CTLocation.UNLOCK_DRAGOON_CHECKLIST: KARLocationData(110, KARRegion.CITY_TRIAL),
    CTLocation.UNLOCK_HYDRA_CHECKLIST: KARLocationData(111, KARRegion.CITY_TRIAL),
    CTLocation.BUST_WHEELIE_SCOOTER_ON_COMPACT_STAR: KARLocationData(112, KARRegion.CITY_TRIAL),
    CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR: KARLocationData(113, KARRegion.CITY_TRIAL),
    CTLocation.BUST_SWERVE_STAR_ON_WHEELIE_BIKE: KARLocationData(114, KARRegion.CITY_TRIAL),
    CTLocation.BUST_WARPSTAR_ON_SWERVE_STAR: KARLocationData(115, KARRegion.CITY_TRIAL),
    CTLocation.BUST_FORMULA_STAR_ON_TURBO_STAR: KARLocationData(116, KARRegion.CITY_TRIAL),
    CTLocation.BUST_SLICK_STAR_ON_FORMULA_STAR: KARLocationData(117, KARRegion.CITY_TRIAL),
    CTLocation.BUST_ROCKET_STAR_ON_SLICK_STAR: KARLocationData(118, KARRegion.CITY_TRIAL),
    CTLocation.BUST_TURBO_STAR_ON_ROCKET_STAR: KARLocationData(119, KARRegion.CITY_TRIAL),
    CTLocation.COMPLETE_DRAGOON_AND_HYDRA: KARLocationData(120, KARRegion.CITY_TRIAL),
}


AIR_RIDE_LOCATION_TABLE: dict[str, KARLocationData] = {
    ARLocation.RACE_100_LAPS: KARLocationData(121, KARRegion.AIR_RIDE),
    ARLocation.RACE_300_LAPS: KARLocationData(122, KARRegion.AIR_RIDE),
    ARLocation.GLIDE_FOR_30_MINUTES: KARLocationData(123, KARRegion.AIR_RIDE),
    ARLocation.GLIDE_FOR_1_HOUR: KARLocationData(124, KARRegion.AIR_RIDE),
    ARLocation.DEFEAT_300_OF_YOUR_ENEMIES: KARLocationData(125, KARRegion.AIR_RIDE),
    ARLocation.DEFEAT_1000_OF_YOUR_ENEMIES: KARLocationData(126, KARRegion.AIR_RIDE),
    ARLocation.SWALL_CHILLY_3_AND_FIRST: KARLocationData(127, KARRegion.AIR_RIDE),
    ARLocation.SWALL_PLASMA_WISP_3_AND_FIRST: KARLocationData(128, KARRegion.AIR_RIDE),
    ARLocation.SWALL_SWORD_KNIGHT_3_AND_FIRST: KARLocationData(129, KARRegion.AIR_RIDE),
    ARLocation.SWALL_WHEELIE_3_AND_FIRST: KARLocationData(130, KARRegion.AIR_RIDE),
    ARLocation.REACH_GOAL_3X_NOT_FR: KARLocationData(131, KARRegion.AIR_RIDE),
    ARLocation.CK_RACE_5500_FEET: KARLocationData(132, KARRegion.AR_CHECKER_KNIGHTS),
    ARLocation.MF_RACE_4800_FEET: KARLocationData(133, KARRegion.AR_MAGMA_FLOWS),
    ARLocation.MF_FINISH_2_LAPS_IN_UNDER_02_20_00: KARLocationData(134, KARRegion.AR_MAGMA_FLOWS),
    ARLocation.SWALL_200_ENEMIES: KARLocationData(135, KARRegion.AIR_RIDE),
    ARLocation.DEFEAT_100_ENEMIES_WITH_EXHALED_STARS: KARLocationData(136, KARRegion.AIR_RIDE),
    ARLocation.SWALL_5_GARBAGE_AND_FIRST: KARLocationData(137, KARRegion.AIR_RIDE),
    ARLocation.BP_FINISH_2_LAPS_IN_UNDER_02_18_00: KARLocationData(138, KARRegion.AR_BEANSTALK_PARK),
    ARLocation.MP_FINISH_2_LAPS_IN_UNDER_02_10_00: KARLocationData(139, KARRegion.AR_MACHINE_PASSAGE),
    ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00: KARLocationData(140, KARRegion.AR_CHECKER_KNIGHTS),
    ARLocation.FM_RACE_4500_FEET: KARLocationData(141, KARRegion.AR_FANTASY_MEADOWS),
    ARLocation.CV_RACE_6000_FEET: KARLocationData(142, KARRegion.AR_CELESTIAL_VALLEY),
    ARLocation.SS_RACE_4000_FEET: KARLocationData(143, KARRegion.AR_SKY_SANDS),
    ARLocation.FH_RACE_5300_FEET: KARLocationData(144, KARRegion.AR_FROZEN_HILLSIDE),
    ARLocation.FILL_IN_100_CHECKLIST_BLOCKS: KARLocationData(145, KARRegion.AIR_RIDE),
    ARLocation.FM_FINISH_3_LAPS_IN_UNDER_01_20_00: KARLocationData(146, KARRegion.AR_FANTASY_MEADOWS),
    ARLocation.CV_FINISH_2_LAPS_IN_UNDER_02_20_00: KARLocationData(147, KARRegion.AR_CELESTIAL_VALLEY),
    ARLocation.SS_FINISH_2_LAPS_IN_UNDER_02_05_00: KARLocationData(148, KARRegion.AR_SKY_SANDS),
    ARLocation.SWORD_CHALLENGE_10_SWINGS: KARLocationData(149, KARRegion.AIR_RIDE),
    ARLocation.FH_RACE_2_LAPS_IN_UNDER_02_20_00: KARLocationData(150, KARRegion.AR_FROZEN_HILLSIDE),
    ARLocation.TORNADO_CHALLENGE_15_KO: KARLocationData(151, KARRegion.AIR_RIDE),
    ARLocation.DEFEAT_10_ENEMIES_USING_QUICK_SPIN: KARLocationData(152, KARRegion.AIR_RIDE),
    ARLocation.HIT_20_RIVALS_WITH_YOUR_QUICK_SPIN: KARLocationData(153, KARRegion.AIR_RIDE),
    ARLocation.MP_RACE_4500_FEET: KARLocationData(154, KARRegion.AR_MACHINE_PASSAGE),
    ARLocation.BP_RACE_5500_FEET: KARLocationData(155, KARRegion.AR_BEANSTALK_PARK),
    ARLocation.FM_FINISH_3_LAPS_IN_UNDER_01_03_00: KARLocationData(156, KARRegion.AR_FANTASY_MEADOWS),
    ARLocation.CV_FINISH_2_LAPS_IN_UNDER_01_56_00: KARLocationData(157, KARRegion.AR_CELESTIAL_VALLEY),
    ARLocation.SS_FINISH_2_LAPS_IN_UNDER_01_45_00: KARLocationData(158, KARRegion.AR_SKY_SANDS),
    ARLocation.FH_FINISH_2_LAPS_IN_UNDER_01_56_00: KARLocationData(159, KARRegion.AR_FROZEN_HILLSIDE),
    ARLocation.MF_FINISH_2_LAPS_IN_UNDER_02_01_00: KARLocationData(160, KARRegion.AR_MAGMA_FLOWS),
    ARLocation.BP_FINISH_2_LAPS_IN_UNDER_01_56_00: KARLocationData(161, KARRegion.AR_BEANSTALK_PARK),
    ARLocation.MP_FINISH_2_LAPS_IN_UNDER_01_48_00: KARLocationData(162, KARRegion.AR_MACHINE_PASSAGE),
    ARLocation.CK_FINISH_2_LAPS_IN_UNDER_02_40_00: KARLocationData(163, KARRegion.AR_CHECKER_KNIGHTS),
    ARLocation.TA_FM_FINISH_01_12_00: KARLocationData(164, KARRegion.AR_TA_FANTASY_MEADOWS),
    ARLocation.TA_FM_FINISH_01_00_00: KARLocationData(165, KARRegion.AR_TA_FANTASY_MEADOWS),
    ARLocation.TA_CV_FINISH_03_20_00: KARLocationData(166, KARRegion.AR_TA_CELESTIAL_VALLEY),
    ARLocation.TA_CV_FINISH_02_56_00: KARLocationData(167, KARRegion.AR_TA_CELESTIAL_VALLEY),
    ARLocation.TA_SS_FINISH_03_10_00: KARLocationData(168, KARRegion.AR_TA_SKY_SANDS),
    ARLocation.TA_SS_FINISH_02_40_00: KARLocationData(169, KARRegion.AR_TA_SKY_SANDS),
    ARLocation.TA_FH_FINISH_03_14_00: KARLocationData(170, KARRegion.AR_TA_FROZEN_HILLSIDE),
    ARLocation.TA_FH_FINISH_02_50_00: KARLocationData(171, KARRegion.AR_TA_FROZEN_HILLSIDE),
    ARLocation.TA_MF_FINISH_03_20_00: KARLocationData(172, KARRegion.AR_TA_MAGMA_FLOWS),
    ARLocation.TA_MF_FINISH_03_04_00: KARLocationData(173, KARRegion.AR_TA_MAGMA_FLOWS),
    ARLocation.TA_BP_FINISH_03_10_00: KARLocationData(174, KARRegion.AR_TA_BEANSTALK_PARK),
    ARLocation.TA_BP_FINISH_02_55_00: KARLocationData(175, KARRegion.AR_TA_BEANSTALK_PARK),
    ARLocation.TA_MP_FINISH_03_10_00: KARLocationData(176, KARRegion.AR_TA_MACHINE_PASSAGE),
    ARLocation.TA_MP_FINISH_02_48_00: KARLocationData(177, KARRegion.AR_TA_MACHINE_PASSAGE),
    ARLocation.TA_CK_FINISH_04_30_00: KARLocationData(178, KARRegion.AR_TA_CHECKER_KNIGHTS),
    ARLocation.TA_CK_FINISH_04_00_00: KARLocationData(179, KARRegion.AR_TA_CHECKER_KNIGHTS),
    ARLocation.FR_FM_LAP_00_24_00: KARLocationData(180, KARRegion.AR_FR_FANTASY_MEADOWS),
    ARLocation.FR_FM_LAP_00_21_00: KARLocationData(181, KARRegion.AR_FR_FANTASY_MEADOWS),
    ARLocation.FR_FM_LAP_00_23_00_ON_WAGON_STAR: KARLocationData(182, KARRegion.AR_FR_FANTASY_MEADOWS),
    ARLocation.FR_CV_LAP_01_10_00: KARLocationData(183, KARRegion.AR_FR_CELESTIAL_VALLEY),
    ARLocation.FR_CV_LAP_00_57_00: KARLocationData(184, KARRegion.AR_FR_CELESTIAL_VALLEY),
    ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR: KARLocationData(185, KARRegion.AR_FR_CELESTIAL_VALLEY),
    ARLocation.FR_SS_LAP_01_05_00: KARLocationData(186, KARRegion.AR_FR_SKY_SANDS),
    ARLocation.FR_SS_LAP_00_53_00: KARLocationData(187, KARRegion.AR_FR_SKY_SANDS),
    ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR: KARLocationData(188, KARRegion.AR_FR_SKY_SANDS),
    ARLocation.FR_FH_LAP_01_10_00: KARLocationData(189, KARRegion.AR_FR_FROZEN_HILLSIDE),
    ARLocation.FR_FH_LAP_00_58_00: KARLocationData(190, KARRegion.AR_FR_FROZEN_HILLSIDE),
    ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR: KARLocationData(191, KARRegion.AR_FR_FROZEN_HILLSIDE),
    ARLocation.FR_MF_LAP_01_10_00: KARLocationData(192, KARRegion.AR_FR_MAGMA_FLOWS),
    ARLocation.FR_MF_LAP_01_01_00: KARLocationData(193, KARRegion.AR_FR_MAGMA_FLOWS),
    ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR: KARLocationData(194, KARRegion.AR_FR_MAGMA_FLOWS),
    ARLocation.FR_BP_LAP_01_07_00: KARLocationData(195, KARRegion.AR_FR_BEANSTALK_PARK),
    ARLocation.FR_BP_LAP_00_58_00: KARLocationData(196, KARRegion.AR_FR_BEANSTALK_PARK),
    ARLocation.FR_BP_LAP_00_58_00_ON_WINGED_STAR: KARLocationData(197, KARRegion.AR_FR_BEANSTALK_PARK),
    ARLocation.FR_MP_LAP_01_05_00: KARLocationData(198, KARRegion.AR_FR_MACHINE_PASSAGE),
    ARLocation.FR_MP_LAP_00_56_00: KARLocationData(199, KARRegion.AR_FR_MACHINE_PASSAGE),
    ARLocation.FR_MP_LAP_00_57_00_ON_SWERVE_STAR: KARLocationData(200, KARRegion.AR_FR_MACHINE_PASSAGE),
    ARLocation.FR_CK_LAP_01_35_00: KARLocationData(201, KARRegion.AR_FR_CHECKER_KNIGHTS),
    ARLocation.FR_CK_LAP_01_20_00: KARLocationData(202, KARRegion.AR_FR_CHECKER_KNIGHTS),
    ARLocation.FR_CK_LAP_01_25_00_ON_ROCKET_STAR: KARLocationData(203, KARRegion.AR_FR_CHECKER_KNIGHTS),
    ARLocation.MAKE_YOUR_LAP_X_LAST_TWO_DIGITS_SAME: KARLocationData(204, KARRegion.AIR_RIDE),
    ARLocation.RACE_ALL_OF_STANDARD_AIR_RIDE_COURSES: KARLocationData(205, KARRegion.AIR_RIDE),
    ARLocation.LAST_TO_FIRST_FINAL_LAP: KARLocationData(206, KARRegion.AIR_RIDE),
    ARLocation.FINISH_SPINNING_AND_FIRST: KARLocationData(207, KARRegion.AIR_RIDE),
    ARLocation.FIRST_WHILE_TAKING_DAMAGE: KARLocationData(208, KARRegion.AIR_RIDE),
    ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR: KARLocationData(209, KARRegion.AIR_RIDE),
    ARLocation.FIRST_WITH_SLEEP_ABILITY: KARLocationData(210, KARRegion.AIR_RIDE),
    ARLocation.FIRST_WITH_FIRE_ABILITY: KARLocationData(211, KARRegion.AIR_RIDE),
    ARLocation.FIRST_WITH_NEEDLE_ABILITY: KARLocationData(212, KARRegion.AIR_RIDE),
    ARLocation.FIRST_WITH_WING_ABILITY: KARLocationData(213, KARRegion.AIR_RIDE),
    ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR: KARLocationData(214, KARRegion.AR_TA_FANTASY_MEADOWS),
    ARLocation.DROP_FROM_CLIFFS_3X: KARLocationData(215, KARRegion.AIR_RIDE),
    ARLocation.FM_SWALL_20_AND_FIRST: KARLocationData(216, KARRegion.AR_FANTASY_MEADOWS),
    ARLocation.FM_LAP_ABOVE_20_MPH: KARLocationData(217, KARRegion.AR_FANTASY_MEADOWS),
    ARLocation.BP_3_LAPS_NO_FERRIS_WHEEL: KARLocationData(218, KARRegion.AR_BEANSTALK_PARK),
    ARLocation.BP_SWALL_20_AND_FIRST: KARLocationData(219, KARRegion.AR_BEANSTALK_PARK),
    ARLocation.CK_USE_SPIN_PANELS_7_X_AND_FIRST: KARLocationData(220, KARRegion.AR_CHECKER_KNIGHTS),
    ARLocation.CK_BREAK_2_WALLS_AND_FIRST: KARLocationData(221, KARRegion.AR_CHECKER_KNIGHTS),
    ARLocation.CK_SWALL_20_AND_FIRST: KARLocationData(222, KARRegion.AR_CHECKER_KNIGHTS),
    ARLocation.FH_SPLIT_20_ICE_AND_FIRST: KARLocationData(223, KARRegion.AR_FROZEN_HILLSIDE),
    ARLocation.SS_BREAK_ALL_CORAL_AND_FIRST: KARLocationData(224, KARRegion.AR_SKY_SANDS),
    ARLocation.SS_ENTER_QUICKSAND_3_X_AND_FIRST: KARLocationData(225, KARRegion.AR_SKY_SANDS),
    ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR: KARLocationData(226, KARRegion.AR_TA_CELESTIAL_VALLEY),
    ARLocation.SS_TRAPDOOR_3X_AND_FIRST: KARLocationData(227, KARRegion.AR_SKY_SANDS),
    ARLocation.MP_CANNON_SHOOT_3: KARLocationData(228, KARRegion.AR_MACHINE_PASSAGE),
    ARLocation.TA_SS_FINISH_02_40_00_ON_WAGON_STAR: KARLocationData(229, KARRegion.AR_TA_SKY_SANDS),
    ARLocation.MP_FIRST_NO_WALL_TOUCH: KARLocationData(230, KARRegion.AR_MACHINE_PASSAGE),
    ARLocation.MF_USE_ALL_VOLCANO_RAILS_AND_FIRST: KARLocationData(231, KARRegion.AR_MAGMA_FLOWS),
    ARLocation.MF_BUMP_INTO_A_FLAMING_DRAGON: KARLocationData(232, KARRegion.AR_MAGMA_FLOWS),
    ARLocation.MF_ALL_BOOST_PANELS_AND_FIRST: KARLocationData(233, KARRegion.AR_MAGMA_FLOWS),
    ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR: KARLocationData(234, KARRegion.AR_TA_FROZEN_HILLSIDE),
    ARLocation.CV_RIDE_BOTH_BRIDGE_RAILS: KARLocationData(235, KARRegion.AR_CELESTIAL_VALLEY),
    ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR: KARLocationData(236, KARRegion.AR_TA_MAGMA_FLOWS),
    ARLocation.CV_COPY_CHANCE_WHEEL_TREE: KARLocationData(237, KARRegion.AR_CELESTIAL_VALLEY),
    ARLocation.TA_BP_FINISH_03_00_00_ON_ROCKET_STAR: KARLocationData(238, KARRegion.AR_TA_BEANSTALK_PARK),
    ARLocation.TA_MP_FINISH_02_50_00_ON_REX_WHEELIE: KARLocationData(239, KARRegion.AR_TA_MACHINE_PASSAGE),
    ARLocation.TA_CK_FINISH_03_55_00_ON_WARPSTAR: KARLocationData(240, KARRegion.AR_TA_CHECKER_KNIGHTS),
}


TOP_RIDE_LOCATION_TABLE: dict[str, KARLocationData] = {
    TRLocation.CROSS_GOAL_20: KARLocationData(241, KARRegion.TOP_RIDE),
    TRLocation.RACE_300_LAPS: KARLocationData(242, KARRegion.TOP_RIDE),
    TRLocation.COMPETE_IN_10_MULTIPLAYER_RACES: KARLocationData(243, KARRegion.TOP_RIDE),
    TRLocation.COMPETE_IN_50_MULTIPLAYER_RACES: KARLocationData(244, KARRegion.TOP_RIDE),
    TRLocation.FR_RACE_100_LAPS: KARLocationData(245, KARRegion.TR_FREE_RUN),
    TRLocation.TA_CROSS_GOAL_30: KARLocationData(246, KARRegion.TR_TIME_ATTACK),
    TRLocation.FIRST_ON_ALL_COURSES: KARLocationData(247, KARRegion.TOP_RIDE),
    TRLocation.LAP_NO_WALLS_AND_FIRST: KARLocationData(248, KARRegion.TOP_RIDE),
    TRLocation.QUICK_SPIN_20_AND_FIRST: KARLocationData(249, KARRegion.TOP_RIDE),
    TRLocation.NOITEMS_ALL_COURSES: KARLocationData(250, KARRegion.TOP_RIDE),
    TRLocation.NOITEMS_FIRST_ALL_COURSES: KARLocationData(251, KARRegion.TOP_RIDE),
    TRLocation.COLLECT_500_ITEMS: KARLocationData(252, KARRegion.TOP_RIDE),
    TRLocation.ALL_COURSES_NO_BOOST: KARLocationData(253, KARRegion.TOP_RIDE),
    TRLocation.FIRST_ON_ALL_COURSES_WITHOUT_BOOST: KARLocationData(254, KARRegion.TOP_RIDE),
    TRLocation.GET_SAME_ITEM_3_X_IN_ONE_RACE: KARLocationData(255, KARRegion.TOP_RIDE),
    TRLocation.FIRST_WHILE_DOING_A_QUICK_SPIN: KARLocationData(256, KARRegion.TOP_RIDE),
    TRLocation.FIRST_WHILE_HOLDING_HAMMER: KARLocationData(257, KARRegion.TOP_RIDE),
    TRLocation.FIRST_WITH_1_LAP_BETWEEN_YOU_AND_NO2: KARLocationData(258, KARRegion.TOP_RIDE),
    TRLocation.FIRST_WITH_2_LAPS_BETWEEN_YOU_AND_NO2: KARLocationData(259, KARRegion.TOP_RIDE),
    TRLocation.GET_20_SPINNER_ITEMS: KARLocationData(260, KARRegion.TOP_RIDE),
    TRLocation.GET_20_INVINCIBLE_CANDY_ITEMS: KARLocationData(261, KARRegion.TOP_RIDE),
    TRLocation.GET_20_WALKY_ITEMS: KARLocationData(262, KARRegion.TOP_RIDE),
    TRLocation.TORCH_3_RIVALS_USING_ONE_FIRE_ITEM: KARLocationData(263, KARRegion.TOP_RIDE),
    TRLocation.BUZZ_SAW_SEND_3_RIVALS: KARLocationData(264, KARRegion.TOP_RIDE),
    TRLocation.HIT_ENEMIES_3_X_WITH_BOMB_ITEMS: KARLocationData(265, KARRegion.TOP_RIDE),
    TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS: KARLocationData(266, KARRegion.TOP_RIDE),
    TRLocation.GRASS_NOITEMS_FIRST: KARLocationData(267, KARRegion.TR_GRASS),
    TRLocation.GRASS_FIRST_WITHOUT_USING_BOOST: KARLocationData(268, KARRegion.TR_GRASS),
    TRLocation.GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(269, KARRegion.TR_GRASS),
    TRLocation.GRASS_FIRST_10X: KARLocationData(270, KARRegion.TR_GRASS),
    TRLocation.GRASS_FINISH_7_LAPS_IN_UNDER_00_43_00: KARLocationData(271, KARRegion.TR_GRASS),
    TRLocation.GRASS_RACE_100_LAPS: KARLocationData(272, KARRegion.TR_GRASS),
    TRLocation.GRASS_FIRST_AND_HIT_5_DASH_PANELS: KARLocationData(273, KARRegion.TR_GRASS),
    TRLocation.GRASS_IN_ONE_RACE_DROP_30_TREE_BOMBS: KARLocationData(274, KARRegion.TR_GRASS),
    TRLocation.GRASS_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(275, KARRegion.TR_GRASS),
    TRLocation.SAND_NOITEMS_FIRST: KARLocationData(276, KARRegion.TR_SAND),
    TRLocation.SAND_FIRST_WITHOUT_USING_BOOST: KARLocationData(277, KARRegion.TR_SAND),
    TRLocation.SAND_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(278, KARRegion.TR_SAND),
    TRLocation.SAND_FIRST_10X: KARLocationData(279, KARRegion.TR_SAND),
    TRLocation.SAND_FINISH_7_LAPS_IN_UNDER_00_52_00: KARLocationData(280, KARRegion.TR_SAND),
    TRLocation.SAND_RACE_100_LAPS: KARLocationData(281, KARRegion.TR_SAND),
    TRLocation.SAND_FIRST_AND_CATCH_WORM_3: KARLocationData(282, KARRegion.TR_SAND),
    TRLocation.SAND_DROP_INTO_ANT_DOOM_50X: KARLocationData(283, KARRegion.TR_SAND),
    TRLocation.SAND_ANT_DOOM_20X: KARLocationData(284, KARRegion.TR_SAND),
    TRLocation.SAND_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(285, KARRegion.TR_SAND),
    TRLocation.SKY_NOITEMS_FIRST: KARLocationData(286, KARRegion.TR_SKY),
    TRLocation.SKY_FIRST_WITHOUT_USING_BOOST: KARLocationData(287, KARRegion.TR_SKY),
    TRLocation.SKY_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(288, KARRegion.TR_SKY),
    TRLocation.SKY_FIRST_10X: KARLocationData(289, KARRegion.TR_SKY),
    TRLocation.SKY_FINISH_6_LAPS_IN_UNDER_01_02_00: KARLocationData(290, KARRegion.TR_SKY),
    TRLocation.SKY_RACE_100_LAPS: KARLocationData(291, KARRegion.TR_SKY),
    TRLocation.SKY_FIRST_AND_HIT_ISLE_KNOB_5: KARLocationData(292, KARRegion.TR_SKY),
    TRLocation.SKY_FIRST_WITHOUT_USING_JUMP_PLATE: KARLocationData(293, KARRegion.TR_SKY),
    TRLocation.SKY_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(294, KARRegion.TR_SKY),
    TRLocation.FIRE_NOITEMS_FIRST: KARLocationData(295, KARRegion.TR_FIRE),
    TRLocation.FIRE_FIRST_WITHOUT_USING_BOOST: KARLocationData(296, KARRegion.TR_FIRE),
    TRLocation.FIRE_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(297, KARRegion.TR_FIRE),
    TRLocation.FIRE_FIRST_10X: KARLocationData(298, KARRegion.TR_FIRE),
    TRLocation.FIRE_FINISH_6_LAPS_IN_UNDER_00_53_00: KARLocationData(299, KARRegion.TR_FIRE),
    TRLocation.FIRE_RACE_100_LAPS: KARLocationData(300, KARRegion.TR_FIRE),
    TRLocation.FIRE_CAUSE_A_HUGE_ERUPTION_3X: KARLocationData(301, KARRegion.TR_FIRE),
    TRLocation.FIRE_FIRST_WHILE_HOLDING_FIRE_ITEM: KARLocationData(302, KARRegion.TR_FIRE),
    TRLocation.FIRE_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(303, KARRegion.TR_FIRE),
    TRLocation.WATER_NOITEMS_FIRST: KARLocationData(304, KARRegion.TR_WATER),
    TRLocation.WATER_FIRST_WITHOUT_USING_BOOST: KARLocationData(305, KARRegion.TR_WATER),
    TRLocation.WATER_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(306, KARRegion.TR_WATER),
    TRLocation.WATER_FIRST_10X: KARLocationData(307, KARRegion.TR_WATER),
    TRLocation.WATER_FINISH_5_LAPS_IN_UNDER_01_02_00: KARLocationData(308, KARRegion.TR_WATER),
    TRLocation.WATER_RACE_100_LAPS: KARLocationData(309, KARRegion.TR_WATER),
    TRLocation.WATER_FIRST_AND_ENTER_FALLS_5X: KARLocationData(310, KARRegion.TR_WATER),
    TRLocation.WATER_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(311, KARRegion.TR_WATER),
    TRLocation.LIGHT_NOITEMS_FIRST: KARLocationData(312, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FIRST_WITHOUT_USING_BOOST: KARLocationData(313, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(314, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FIRST_10X: KARLocationData(315, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FINISH_6_LAPS_IN_UNDER_00_43_00: KARLocationData(316, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_RACE_100_LAPS: KARLocationData(317, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_RIDE_GRIND_RAIL_50X: KARLocationData(318, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FIRST_AND_GRIND_RAIL_5X: KARLocationData(319, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FIRST_AND_BUST_6_COLUMNS: KARLocationData(320, KARRegion.TR_LIGHT),
    TRLocation.LIGHT_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(321, KARRegion.TR_LIGHT),
    TRLocation.METAL_NOITEMS_FIRST: KARLocationData(322, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_WITHOUT_USING_BOOST: KARLocationData(323, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_WITH_CPUS_SET_TO_LEVEL_5: KARLocationData(324, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_10X: KARLocationData(325, KARRegion.TR_METAL),
    TRLocation.METAL_FINISH_5_LAPS_IN_UNDER_00_58_00: KARLocationData(326, KARRegion.TR_METAL),
    TRLocation.METAL_RACE_100_LAPS: KARLocationData(327, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_NO_GEAR_WALLS: KARLocationData(328, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_AND_HIT_SWITCH_10X: KARLocationData(329, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_AND_BREAK_5_GEAR_WALLS: KARLocationData(330, KARRegion.TR_METAL),
    TRLocation.METAL_FIRST_5_SECONDS_FASTER_THAN_NO2: KARLocationData(331, KARRegion.TR_METAL),
    TRLocation.TA_GRASS_FINISH_00_33_00: KARLocationData(332, KARRegion.TR_TA_GRASS),
    TRLocation.TA_SAND_FINISH_00_35_00: KARLocationData(333, KARRegion.TR_TA_SAND),
    TRLocation.TA_LIGHT_FINISH_00_38_00: KARLocationData(334, KARRegion.TR_TA_LIGHT),
    TRLocation.TA_SKY_FINISH_00_57_00: KARLocationData(335, KARRegion.TR_TA_SKY),
    TRLocation.TA_WATER_FINISH_01_06_00: KARLocationData(336, KARRegion.TR_TA_WATER),
    TRLocation.TA_FIRE_FINISH_00_46_00: KARLocationData(337, KARRegion.TR_TA_FIRE),
    TRLocation.TA_METAL_FINISH_00_57_00: KARLocationData(338, KARRegion.TR_TA_METAL),
    TRLocation.TA_GRASS_FINISH_00_28_00: KARLocationData(339, KARRegion.TR_TA_GRASS),
    TRLocation.TA_SAND_FINISH_00_29_00: KARLocationData(340, KARRegion.TR_TA_SAND),
    TRLocation.TA_LIGHT_FINISH_00_33_00: KARLocationData(341, KARRegion.TR_TA_LIGHT),
    TRLocation.TA_SKY_FINISH_00_47_00: KARLocationData(342, KARRegion.TR_TA_SKY),
    TRLocation.TA_WATER_FINISH_00_56_00: KARLocationData(343, KARRegion.TR_TA_WATER),
    TRLocation.TA_FIRE_FINISH_00_39_00: KARLocationData(344, KARRegion.TR_TA_FIRE),
    TRLocation.TA_METAL_FINISH_00_51_00: KARLocationData(345, KARRegion.TR_TA_METAL),
    TRLocation.FR_GRASS_LAP_00_06_00: KARLocationData(346, KARRegion.TR_FR_GRASS),
    TRLocation.FR_SAND_LAP_00_06_50: KARLocationData(347, KARRegion.TR_FR_SAND),
    TRLocation.FR_LIGHT_LAP_00_07_50: KARLocationData(348, KARRegion.TR_FR_LIGHT),
    TRLocation.FR_SKY_LAP_00_11_00: KARLocationData(349, KARRegion.TR_FR_SKY),
    TRLocation.FR_WATER_LAP_00_12_00: KARLocationData(350, KARRegion.TR_FR_WATER),
    TRLocation.FR_FIRE_LAP_00_08_00: KARLocationData(351, KARRegion.TR_FR_FIRE),
    TRLocation.FR_METAL_LAP_00_11_50: KARLocationData(352, KARRegion.TR_FR_METAL),
    TRLocation.FR_GRASS_LAP_00_04_50: KARLocationData(353, KARRegion.TR_FR_GRASS),
    TRLocation.FR_SAND_LAP_00_05_00: KARLocationData(354, KARRegion.TR_FR_SAND),
    TRLocation.FR_LIGHT_LAP_00_06_00: KARLocationData(355, KARRegion.TR_FR_LIGHT),
    TRLocation.FR_SKY_LAP_00_09_00: KARLocationData(356, KARRegion.TR_FR_SKY),
    TRLocation.FR_WATER_LAP_00_10_50: KARLocationData(357, KARRegion.TR_FR_WATER),
    TRLocation.FR_FIRE_LAP_00_06_50: KARLocationData(358, KARRegion.TR_FR_FIRE),
    TRLocation.FR_METAL_LAP_00_09_50: KARLocationData(359, KARRegion.TR_FR_METAL),
    TRLocation.FILL_IN_100_CHECKLIST_BLOCKS: KARLocationData(360, KARRegion.TOP_RIDE),
}


# Merged view across all modes for lookups by location name.
LOCATION_TABLE: dict[str, KARLocationData] = (
    CITY_TRIAL_LOCATION_TABLE | AIR_RIDE_LOCATION_TABLE | TOP_RIDE_LOCATION_TABLE
)


location_name_groups: dict[str, set[str]] = {
    "City Trial: Stadiums": {
        CTLocation.STADIUM_PLAY_10_STADIUM_MODES,
        CTLocation.STADIUM_DR2_FINISH_00_24_00,
        CTLocation.STADIUM_DR4_FINISH_00_24_00,
        CTLocation.STADIUM_HJ_AIRBORNE_10_SECONDS,
        CTLocation.STADIUM_TF_AIRBORNE_15_SECONDS,
        CTLocation.STADIUM_AG_FLY_660_FEET,
        CTLocation.STADIUM_DD2_KO_YOUR_RIVALS_5,
        CTLocation.STADIUM_DD1_BUST_ALL_ROCKS_ON_FIELD,
        CTLocation.STADIUM_KM2_KO_ENEMIES_30X,
        CTLocation.STADIUM_DR1_17_00_FORMULA,
        CTLocation.STADIUM_DR3_31_00_WHEELIE_BIKE,
        CTLocation.STADIUM_PLAY_20_STADIUM_MODES,
        CTLocation.STADIUM_DR2_FINISH_00_20_00,
        CTLocation.STADIUM_DR4_FINISH_00_19_00,
        CTLocation.STADIUM_TF_GET_150_POINTS,
        CTLocation.STADIUM_TF_PLAY_15X,
        CTLocation.STADIUM_AG_FLY_1300_FEET,
        CTLocation.STADIUM_DD3_KO_YOUR_RIVALS_5,
        CTLocation.STADIUM_DD_ALL_KO_ENEMIES_50X,
        CTLocation.STADIUM_KM_ALL_KO_500_ENEMIES,
        CTLocation.STADIUM_DD1_KO_A_RIVAL_10X,
        CTLocation.STADIUM_DD4_KO_A_RIVAL_10X,
        CTLocation.STADIUM_KM1_KO_75_ENEMIES_BY_YOURSELF,
        CTLocation.STADIUM_DR2_27_00_WAGON,
        CTLocation.STADIUM_DR4_33_00_TURBO,
        CTLocation.STADIUM_DR1_FINISH_00_24_00,
        CTLocation.STADIUM_DR3_FINISH_00_35_00,
        CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_500_FEET,
        CTLocation.STADIUM_TF_GET_EXACTLY_90_POINTS,
        CTLocation.STADIUM_TF_GET_1500_POINTS,
        CTLocation.STADIUM_AG_AIRBORNE_30_SECONDS,
        CTLocation.STADIUM_DD4_KO_YOUR_RIVALS_5,
        CTLocation.STADIUM_DD_ALL_KO_ENEMIES_150X,
        CTLocation.STADIUM_KM_ALL_KO_1500_ENEMIES,
        CTLocation.STADIUM_DR2_29_00_WINGED,
        CTLocation.STADIUM_DR4_24_00_REX,
        CTLocation.STADIUM_DR1_FINISH_00_20_00,
        CTLocation.STADIUM_DR3_FINISH_00_27_00,
        CTLocation.STADIUM_HJ_JUMP_HIGHER_THAN_1000_FEET,
        CTLocation.STADIUM_TF_PERFECT_200,
        CTLocation.STADIUM_AG_FLY_330_FEET,
        CTLocation.STADIUM_DD1_KO_YOUR_RIVALS_5,
        CTLocation.STADIUM_DD5_KO_YOUR_RIVALS_5,
        CTLocation.STADIUM_KM1_KO_ENEMIES_50X,
        CTLocation.STADIUM_VSKD_KO_DEDEDE_1MIN,
        CTLocation.STADIUM_DD2_KO_A_RIVAL_10X,
        CTLocation.STADIUM_DD5_KO_A_RIVAL_10X,
        CTLocation.STADIUM_KM2_KO_40_ENEMIES_BY_YOURSELF,
        CTLocation.STADIUM_DR1_26_00_WARPSTAR,
        CTLocation.STADIUM_DR3_28_00_SWERVE,
    },
    "City Trial: Free Run": {
        CTLocation.FR_DRIVE_FOR_2_HOURS,
        CTLocation.FR_DRIVE_FOR_30_MINUTES,
        CTLocation.FR_DRIVE_FOR_10_MINUTES,
        CTLocation.FR_CHANGE_AIR_RIDE_MACHINES_10X,
    },
    "City Trial: Multiplayer": {
        CTLocation.TIMEOUT_ALL_ON_RAILS,
        CTLocation.ALL_PLAYERS_OFF_MACHINES,
        CTLocation.TIMEOUT_ALL_OFF_MACHINES,
    },
    "City Trial: CPUs": {
        CTLocation.BREAK_A_CPUS_MACHINE_5_X,
        CTLocation.DAMAGE_ALL_3_CPUS,
        CTLocation.DAMAGE_RIVAL_WITHIN_10S,
    },
    "City Trial: Bust Vehicle on Vehicle": {
        CTLocation.BUST_WHEELIE_BIKE_ON_WARPSTAR,
        CTLocation.BUST_SLICK_STAR_ON_FORMULA_STAR,
        CTLocation.BUST_SWERVE_STAR_ON_WHEELIE_BIKE,
        CTLocation.BUST_ROCKET_STAR_ON_SLICK_STAR,
        CTLocation.BUST_WARPSTAR_ON_SWERVE_STAR,
        CTLocation.BUST_TURBO_STAR_ON_ROCKET_STAR,
        CTLocation.BUST_WHEELIE_SCOOTER_ON_COMPACT_STAR,
        CTLocation.BUST_FORMULA_STAR_ON_TURBO_STAR,
    },
    "City Trial: Events": {
        CTLocation.USE_UP_ONE_OF_RESTORATION_AREAS,
        CTLocation.THE_METEOR_ATTACKS_CITY_3,
        CTLocation.DO_SOME_DAMAGE_TO_DYNA_BLADE,
        CTLocation.GET_TRAMPLED_BY_DYNA_BLADE,
        CTLocation.STEAL_8_FROM_TAC,
        CTLocation.BREAK_5_OF_HUGE_PILLARS_THAT_APPEAR,
        CTLocation.BREAK_PILLAR_WITHIN_40S,
        CTLocation.ENTER_CASTLE_CHAMBER,
    },
    "City Trial: Patches": {
        CTLocation.GET_10_BOOST_PATCHES,
        CTLocation.GET_10_TURN_PATCHES,
        CTLocation.GET_10_WEIGHT_PATCHES,
        CTLocation.GET_10_GLIDE_PATCHES,
        CTLocation.GET_30_GLIDE_PATCHES,
        CTLocation.GET_10_TOP_SPEED_PATCHES,
        CTLocation.GET_10_CHARGE_PATCHES,
        CTLocation.GET_10_DEFENSE_PATCHES,
    },
    "City Trial: High Effort": {
        CTLocation.BREAK_500_BOXES,
        CTLocation.BREAK_1000_BOXES,
        CTLocation.PICKUP_1000_ITEMS,
        CTLocation.PICKUP_3000_ITEMS,
        CTLocation.FR_DRIVE_FOR_2_HOURS,
        CTLocation.FR_DRIVE_FOR_30_MINUTES,
        CTLocation.FR_DRIVE_FOR_10_MINUTES,
        CTLocation.COMPLETE_DRAGOON_AND_HYDRA,
        CTLocation.FILL_IN_100_CHECKLIST_BLOCKS,
        CTLocation.GET_10_ITEMS_IN_20S,
        CTLocation.GET_50_ITEMS,
        CTLocation.RACE_200_MILES,
    },
    "City Trial: RNG": {
        CTLocation.EAT_3_PLATES_OF_SUSHI,
        CTLocation.EAT_3_HOT_DOGS,
        CTLocation.EAT_2_MAXIM_TOMATOES,
        CTLocation.DRINK_3_ENERGY_DRINKS,
        CTLocation.COPY_CHANCE_WHEEL_BOMB,
        CTLocation.COPY_CHANCE_WHEEL_SLEEP,
    },
    "City Trial: PVP": {
        CTLocation.USE_FIREWORKS_TO_KO_RIVALS_10X,
        CTLocation.USE_SENSOR_BOMBS_TO_KO_RIVALS_3X,
        CTLocation.USE_GOLD_SPIKES_TO_KO_RIVALS_3X,
    },
    "Air Ride: Races": {
        ARLocation.MF_RACE_4800_FEET,
        ARLocation.SWALL_5_GARBAGE_AND_FIRST,
        ARLocation.FM_RACE_4500_FEET,
        ARLocation.CV_FINISH_2_LAPS_IN_UNDER_01_56_00,
        ARLocation.BP_FINISH_2_LAPS_IN_UNDER_01_56_00,
        ARLocation.FIRST_WHILE_FLYING_THROUGH_AIR,
        ARLocation.FIRST_WITH_WING_ABILITY,
        ARLocation.MF_FINISH_2_LAPS_IN_UNDER_02_20_00,
        ARLocation.BP_FINISH_2_LAPS_IN_UNDER_02_18_00,
        ARLocation.CV_RACE_6000_FEET,
        ARLocation.FM_FINISH_3_LAPS_IN_UNDER_01_20_00,
        ARLocation.FH_RACE_2_LAPS_IN_UNDER_02_20_00,
        ARLocation.MP_RACE_4500_FEET,
        ARLocation.SS_FINISH_2_LAPS_IN_UNDER_01_45_00,
        ARLocation.MP_FINISH_2_LAPS_IN_UNDER_01_48_00,
        ARLocation.LAST_TO_FIRST_FINAL_LAP,
        ARLocation.FIRST_WITH_SLEEP_ABILITY,
        ARLocation.MP_FINISH_2_LAPS_IN_UNDER_02_10_00,
        ARLocation.SS_RACE_4000_FEET,
        ARLocation.CV_FINISH_2_LAPS_IN_UNDER_02_20_00,
        ARLocation.BP_RACE_5500_FEET,
        ARLocation.FH_FINISH_2_LAPS_IN_UNDER_01_56_00,
        ARLocation.CK_FINISH_2_LAPS_IN_UNDER_02_40_00,
        ARLocation.FINISH_SPINNING_AND_FIRST,
        ARLocation.FIRST_WITH_FIRE_ABILITY,
        ARLocation.CK_RACE_5500_FEET,
        ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00,
        ARLocation.FH_RACE_5300_FEET,
        ARLocation.SS_FINISH_2_LAPS_IN_UNDER_02_05_00,
        ARLocation.FM_FINISH_3_LAPS_IN_UNDER_01_03_00,
        ARLocation.MF_FINISH_2_LAPS_IN_UNDER_02_01_00,
        ARLocation.FIRST_WHILE_TAKING_DAMAGE,
        ARLocation.FIRST_WITH_NEEDLE_ABILITY,
    },
    "Air Ride: Free Run": {
        ARLocation.FR_FM_LAP_00_21_00,
        ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
        ARLocation.FR_FH_LAP_01_10_00,
        ARLocation.FR_MF_LAP_01_01_00,
        ARLocation.FR_BP_LAP_00_58_00_ON_WINGED_STAR,
        ARLocation.FR_CK_LAP_01_35_00,
        ARLocation.FR_FM_LAP_00_23_00_ON_WAGON_STAR,
        ARLocation.FR_SS_LAP_01_05_00,
        ARLocation.FR_FH_LAP_00_58_00,
        ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR,
        ARLocation.FR_MP_LAP_01_05_00,
        ARLocation.FR_CK_LAP_01_20_00,
        ARLocation.FR_CV_LAP_01_10_00,
        ARLocation.FR_SS_LAP_00_53_00,
        ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR,
        ARLocation.FR_BP_LAP_01_07_00,
        ARLocation.FR_MP_LAP_00_56_00,
        ARLocation.FR_CK_LAP_01_25_00_ON_ROCKET_STAR,
        ARLocation.FR_FM_LAP_00_24_00,
        ARLocation.FR_CV_LAP_00_57_00,
        ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR,
        ARLocation.FR_MF_LAP_01_10_00,
        ARLocation.FR_BP_LAP_00_58_00,
        ARLocation.FR_MP_LAP_00_57_00_ON_SWERVE_STAR,
    },
    "Air Ride: Time Attack": {
        ARLocation.TA_FM_FINISH_01_00_00,
        ARLocation.TA_SS_FINISH_02_40_00,
        ARLocation.TA_MF_FINISH_03_04_00,
        ARLocation.TA_MP_FINISH_02_48_00,
        ARLocation.TA_SS_FINISH_02_40_00_ON_WAGON_STAR,
        ARLocation.TA_CV_FINISH_03_20_00,
        ARLocation.TA_FH_FINISH_03_14_00,
        ARLocation.TA_BP_FINISH_03_10_00,
        ARLocation.TA_CK_FINISH_04_30_00,
        ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR,
        ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR,
        ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR,
        ARLocation.TA_BP_FINISH_03_00_00_ON_ROCKET_STAR,
        ARLocation.TA_CV_FINISH_02_56_00,
        ARLocation.TA_FH_FINISH_02_50_00,
        ARLocation.TA_BP_FINISH_02_55_00,
        ARLocation.TA_CK_FINISH_04_00_00,
        ARLocation.TA_MP_FINISH_02_50_00_ON_REX_WHEELIE,
        ARLocation.TA_FM_FINISH_01_12_00,
        ARLocation.TA_SS_FINISH_03_10_00,
        ARLocation.TA_MF_FINISH_03_20_00,
        ARLocation.TA_MP_FINISH_03_10_00,
        ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR,
        ARLocation.TA_CK_FINISH_03_55_00_ON_WARPSTAR,
    },
    "Air Ride: MAGMA FLOWS": {
        ARLocation.MF_RACE_4800_FEET,
        ARLocation.TA_MF_FINISH_03_04_00,
        ARLocation.FR_MF_LAP_01_01_00,
        ARLocation.MF_ALL_BOOST_PANELS_AND_FIRST,
        ARLocation.MF_FINISH_2_LAPS_IN_UNDER_02_20_00,
        ARLocation.FR_MF_LAP_01_02_00_ON_TURBO_STAR,
        ARLocation.MF_USE_ALL_VOLCANO_RAILS_AND_FIRST,
        ARLocation.MF_FINISH_2_LAPS_IN_UNDER_02_01_00,
        ARLocation.TA_MF_FINISH_03_20_00,
        ARLocation.FR_MF_LAP_01_10_00,
        ARLocation.MF_BUMP_INTO_A_FLAMING_DRAGON,
        ARLocation.TA_MF_FINISH_03_15_00_ON_SHADOW_STAR,
    },
    "Air Ride: FANTASY MEADOWS": {
        ARLocation.FM_RACE_4500_FEET,
        ARLocation.TA_FM_FINISH_01_00_00,
        ARLocation.FR_FM_LAP_00_21_00,
        ARLocation.FM_LAP_ABOVE_20_MPH,
        ARLocation.FM_FINISH_3_LAPS_IN_UNDER_01_20_00,
        ARLocation.FR_FM_LAP_00_23_00_ON_WAGON_STAR,
        ARLocation.TA_FM_FINISH_01_05_00_ON_SLICK_STAR,
        ARLocation.FM_FINISH_3_LAPS_IN_UNDER_01_03_00,
        ARLocation.TA_FM_FINISH_01_12_00,
        ARLocation.FR_FM_LAP_00_24_00,
        ARLocation.FM_SWALL_20_AND_FIRST,
    },
    "Air Ride: SKY SANDS": {
        ARLocation.TA_SS_FINISH_02_40_00,
        ARLocation.SS_ENTER_QUICKSAND_3_X_AND_FIRST,
        ARLocation.TA_SS_FINISH_02_40_00_ON_WAGON_STAR,
        ARLocation.SS_FINISH_2_LAPS_IN_UNDER_01_45_00,
        ARLocation.FR_SS_LAP_01_05_00,
        ARLocation.SS_RACE_4000_FEET,
        ARLocation.FR_SS_LAP_00_53_00,
        ARLocation.SS_TRAPDOOR_3X_AND_FIRST,
        ARLocation.SS_FINISH_2_LAPS_IN_UNDER_02_05_00,
        ARLocation.TA_SS_FINISH_03_10_00,
        ARLocation.FR_SS_LAP_01_05_00_ON_BULK_STAR,
        ARLocation.SS_BREAK_ALL_CORAL_AND_FIRST,
    },
    "Air Ride: MACHINE PASSAGE": {
        ARLocation.TA_MP_FINISH_02_48_00,
        ARLocation.MP_RACE_4500_FEET,
        ARLocation.MP_FINISH_2_LAPS_IN_UNDER_01_48_00,
        ARLocation.FR_MP_LAP_01_05_00,
        ARLocation.MP_FIRST_NO_WALL_TOUCH,
        ARLocation.MP_FINISH_2_LAPS_IN_UNDER_02_10_00,
        ARLocation.FR_MP_LAP_00_56_00,
        ARLocation.TA_MP_FINISH_02_50_00_ON_REX_WHEELIE,
        ARLocation.TA_MP_FINISH_03_10_00,
        ARLocation.FR_MP_LAP_00_57_00_ON_SWERVE_STAR,
        ARLocation.MP_CANNON_SHOOT_3,
    },
    "Air Ride: CELESTIAL VALLEY": {
        ARLocation.CV_FINISH_2_LAPS_IN_UNDER_01_56_00,
        ARLocation.FR_CV_LAP_01_02_00_ON_SLICK_STAR,
        ARLocation.CV_COPY_CHANCE_WHEEL_TREE,
        ARLocation.CV_RACE_6000_FEET,
        ARLocation.TA_CV_FINISH_03_20_00,
        ARLocation.TA_CV_FINISH_02_58_00_ON_JET_STAR,
        ARLocation.CV_FINISH_2_LAPS_IN_UNDER_02_20_00,
        ARLocation.TA_CV_FINISH_02_56_00,
        ARLocation.FR_CV_LAP_01_10_00,
        ARLocation.CV_RIDE_BOTH_BRIDGE_RAILS,
        ARLocation.FR_CV_LAP_00_57_00,
    },
    "Air Ride: FROZEN HILLSIDE": {
        ARLocation.FR_FH_LAP_01_10_00,
        ARLocation.FH_RACE_2_LAPS_IN_UNDER_02_20_00,
        ARLocation.TA_FH_FINISH_03_14_00,
        ARLocation.FR_FH_LAP_00_58_00,
        ARLocation.TA_FH_FINISH_03_10_00_ON_TURBO_STAR,
        ARLocation.FH_FINISH_2_LAPS_IN_UNDER_01_56_00,
        ARLocation.TA_FH_FINISH_02_50_00,
        ARLocation.FR_FH_LAP_01_10_00_ON_FORMULA_STAR,
        ARLocation.FH_SPLIT_20_ICE_AND_FIRST,
        ARLocation.FH_RACE_5300_FEET,
    },
    "Air Ride: BEANSTALK PARK": {
        ARLocation.BP_FINISH_2_LAPS_IN_UNDER_01_56_00,
        ARLocation.FR_BP_LAP_00_58_00_ON_WINGED_STAR,
        ARLocation.BP_FINISH_2_LAPS_IN_UNDER_02_18_00,
        ARLocation.TA_BP_FINISH_03_10_00,
        ARLocation.BP_3_LAPS_NO_FERRIS_WHEEL,
        ARLocation.TA_BP_FINISH_03_00_00_ON_ROCKET_STAR,
        ARLocation.BP_RACE_5500_FEET,
        ARLocation.TA_BP_FINISH_02_55_00,
        ARLocation.FR_BP_LAP_01_07_00,
        ARLocation.BP_SWALL_20_AND_FIRST,
        ARLocation.FR_BP_LAP_00_58_00,
    },
    "Air Ride: CHECKER KNIGHTS": {
        ARLocation.FR_CK_LAP_01_35_00,
        ARLocation.CK_BREAK_2_WALLS_AND_FIRST,
        ARLocation.TA_CK_FINISH_04_30_00,
        ARLocation.FR_CK_LAP_01_20_00,
        ARLocation.CK_SWALL_20_AND_FIRST,
        ARLocation.CK_FINISH_2_LAPS_IN_UNDER_02_40_00,
        ARLocation.TA_CK_FINISH_04_00_00,
        ARLocation.FR_CK_LAP_01_25_00_ON_ROCKET_STAR,
        ARLocation.CK_RACE_5500_FEET,
        ARLocation.CK_FINISH_2_LAPS_IN_UNDER_03_05_00,
        ARLocation.CK_USE_SPIN_PANELS_7_X_AND_FIRST,
        ARLocation.TA_CK_FINISH_03_55_00_ON_WARPSTAR,
    },
    "Air Ride: High Effort": {
        ARLocation.DEFEAT_100_ENEMIES_WITH_EXHALED_STARS,
        ARLocation.GLIDE_FOR_1_HOUR,
        ARLocation.SWALL_200_ENEMIES,
        ARLocation.GLIDE_FOR_30_MINUTES,
        ARLocation.DEFEAT_1000_OF_YOUR_ENEMIES,
        ARLocation.RACE_300_LAPS,
        ARLocation.FILL_IN_100_CHECKLIST_BLOCKS,
        ARLocation.DEFEAT_300_OF_YOUR_ENEMIES,
        ARLocation.RACE_100_LAPS,
    },
    "Top Ride: Time Attack": {
        TRLocation.TA_SAND_FINISH_00_35_00,
        TRLocation.TA_FIRE_FINISH_00_46_00,
        TRLocation.TA_LIGHT_FINISH_00_33_00,
        TRLocation.TA_METAL_FINISH_00_51_00,
        TRLocation.TA_CROSS_GOAL_30,
        TRLocation.TA_LIGHT_FINISH_00_38_00,
        TRLocation.TA_METAL_FINISH_00_57_00,
        TRLocation.TA_SKY_FINISH_00_47_00,
        TRLocation.TA_SKY_FINISH_00_57_00,
        TRLocation.TA_GRASS_FINISH_00_28_00,
        TRLocation.TA_WATER_FINISH_00_56_00,
        TRLocation.TA_GRASS_FINISH_00_33_00,
        TRLocation.TA_WATER_FINISH_01_06_00,
        TRLocation.TA_SAND_FINISH_00_29_00,
        TRLocation.TA_FIRE_FINISH_00_39_00,
    },
    "Top Ride: Free Run": {
        TRLocation.FR_RACE_100_LAPS,
        TRLocation.FR_SKY_LAP_00_11_00,
        TRLocation.FR_GRASS_LAP_00_04_50,
        TRLocation.FR_WATER_LAP_00_10_50,
        TRLocation.FR_GRASS_LAP_00_06_00,
        TRLocation.FR_WATER_LAP_00_12_00,
        TRLocation.FR_SAND_LAP_00_05_00,
        TRLocation.FR_FIRE_LAP_00_06_50,
        TRLocation.FR_SAND_LAP_00_06_50,
        TRLocation.FR_FIRE_LAP_00_08_00,
        TRLocation.FR_LIGHT_LAP_00_06_00,
        TRLocation.FR_METAL_LAP_00_09_50,
        TRLocation.FR_LIGHT_LAP_00_07_50,
        TRLocation.FR_METAL_LAP_00_11_50,
        TRLocation.FR_SKY_LAP_00_09_00,
    },
    "Top Ride: LIGHT": {
        TRLocation.LIGHT_FIRST_WITHOUT_USING_BOOST,
        TRLocation.LIGHT_RACE_100_LAPS,
        TRLocation.TA_LIGHT_FINISH_00_33_00,
        TRLocation.LIGHT_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.LIGHT_RIDE_GRIND_RAIL_50X,
        TRLocation.TA_LIGHT_FINISH_00_38_00,
        TRLocation.LIGHT_FIRST_10X,
        TRLocation.LIGHT_FIRST_AND_GRIND_RAIL_5X,
        TRLocation.FR_LIGHT_LAP_00_06_00,
        TRLocation.LIGHT_FINISH_6_LAPS_IN_UNDER_00_43_00,
        TRLocation.LIGHT_FIRST_AND_BUST_6_COLUMNS,
        TRLocation.FR_LIGHT_LAP_00_07_50,
    },
    "Top Ride: SKY": {
        TRLocation.SKY_FIRST_10X,
        TRLocation.SKY_FIRST_WITHOUT_USING_JUMP_PLATE,
        TRLocation.FR_SKY_LAP_00_11_00,
        TRLocation.SKY_FINISH_6_LAPS_IN_UNDER_01_02_00,
        TRLocation.TA_SKY_FINISH_00_47_00,
        TRLocation.SKY_FIRST_WITHOUT_USING_BOOST,
        TRLocation.SKY_RACE_100_LAPS,
        TRLocation.TA_SKY_FINISH_00_57_00,
        TRLocation.SKY_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.SKY_FIRST_AND_HIT_ISLE_KNOB_5,
        TRLocation.FR_SKY_LAP_00_09_00,
    },
    "Top Ride: GRASS": {
        TRLocation.GRASS_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.GRASS_FIRST_AND_HIT_5_DASH_PANELS,
        TRLocation.FR_GRASS_LAP_00_04_50,
        TRLocation.GRASS_FIRST_10X,
        TRLocation.FR_GRASS_LAP_00_06_00,
        TRLocation.GRASS_FINISH_7_LAPS_IN_UNDER_00_43_00,
        TRLocation.TA_GRASS_FINISH_00_28_00,
        TRLocation.GRASS_FIRST_WITHOUT_USING_BOOST,
        TRLocation.GRASS_RACE_100_LAPS,
        TRLocation.TA_GRASS_FINISH_00_33_00,
    },
    "Top Ride: WATER": {
        TRLocation.WATER_FIRST_WITHOUT_USING_BOOST,
        TRLocation.WATER_RACE_100_LAPS,
        TRLocation.FR_WATER_LAP_00_10_50,
        TRLocation.WATER_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.WATER_FIRST_AND_ENTER_FALLS_5X,
        TRLocation.FR_WATER_LAP_00_12_00,
        TRLocation.WATER_FIRST_10X,
        TRLocation.TA_WATER_FINISH_00_56_00,
        TRLocation.WATER_FINISH_5_LAPS_IN_UNDER_01_02_00,
        TRLocation.TA_WATER_FINISH_01_06_00,
    },
    "Top Ride: SAND": {
        TRLocation.SAND_FIRST_WITHOUT_USING_BOOST,
        TRLocation.SAND_RACE_100_LAPS,
        TRLocation.TA_SAND_FINISH_00_35_00,
        TRLocation.SAND_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.SAND_FIRST_AND_CATCH_WORM_3,
        TRLocation.FR_SAND_LAP_00_05_00,
        TRLocation.SAND_FIRST_10X,
        TRLocation.SAND_DROP_INTO_ANT_DOOM_50X,
        TRLocation.FR_SAND_LAP_00_06_50,
        TRLocation.SAND_FINISH_7_LAPS_IN_UNDER_00_52_00,
        TRLocation.SAND_ANT_DOOM_20X,
        TRLocation.TA_SAND_FINISH_00_29_00,
    },
    "Top Ride: FIRE": {
        TRLocation.FIRE_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.FIRE_CAUSE_A_HUGE_ERUPTION_3X,
        TRLocation.TA_FIRE_FINISH_00_46_00,
        TRLocation.FIRE_FIRST_10X,
        TRLocation.FR_FIRE_LAP_00_06_50,
        TRLocation.FIRE_FINISH_6_LAPS_IN_UNDER_00_53_00,
        TRLocation.FR_FIRE_LAP_00_08_00,
        TRLocation.FIRE_FIRST_WITHOUT_USING_BOOST,
        TRLocation.FIRE_RACE_100_LAPS,
        TRLocation.TA_FIRE_FINISH_00_39_00,
    },
    "Top Ride: METAL": {
        TRLocation.METAL_FIRST_10X,
        TRLocation.METAL_FIRST_AND_HIT_SWITCH_10X,
        TRLocation.TA_METAL_FINISH_00_51_00,
        TRLocation.METAL_FINISH_5_LAPS_IN_UNDER_00_58_00,
        TRLocation.METAL_FIRST_AND_BREAK_5_GEAR_WALLS,
        TRLocation.TA_METAL_FINISH_00_57_00,
        TRLocation.METAL_FIRST_WITHOUT_USING_BOOST,
        TRLocation.METAL_RACE_100_LAPS,
        TRLocation.FR_METAL_LAP_00_09_50,
        TRLocation.METAL_FIRST_WITH_CPUS_SET_TO_LEVEL_5,
        TRLocation.METAL_FIRST_NO_GEAR_WALLS,
        TRLocation.FR_METAL_LAP_00_11_50,
    },
    "Top Ride: High Effort": {
        TRLocation.FILL_IN_100_CHECKLIST_BLOCKS,
        TRLocation.FR_RACE_100_LAPS,
        TRLocation.SAND_RACE_100_LAPS,
        TRLocation.WATER_RACE_100_LAPS,
        TRLocation.LIGHT_RACE_100_LAPS,
        TRLocation.SKY_RACE_100_LAPS,
        TRLocation.METAL_RACE_100_LAPS,
        TRLocation.GRASS_RACE_100_LAPS,
        TRLocation.FIRE_RACE_100_LAPS,
        TRLocation.COLLECT_500_ITEMS,
        TRLocation.SAND_DROP_INTO_ANT_DOOM_50X,
        TRLocation.LIGHT_RIDE_GRIND_RAIL_50X,
        TRLocation.GET_18_DIFFERENT_TYPES_OF_ITEMS,
        TRLocation.RACE_300_LAPS,
    },
    "Top Ride: Multiplayer": {
        TRLocation.COMPETE_IN_50_MULTIPLAYER_RACES,
        TRLocation.COMPETE_IN_10_MULTIPLAYER_RACES,
    },
}


# Maps a goal option value to the location that represents that goal in the world.
# Used both to exclude the underlying location from generation and to attach the
# victory event to the goal location's region.
CITY_TRIAL_GOAL_TO_LOCATION: dict[int, str] = {
    CityTrialGoal.option_100_checklist_blocks: CTLocation.FILL_IN_100_CHECKLIST_BLOCKS,
    CityTrialGoal.option_hydra_and_dragoon: CTLocation.COMPLETE_DRAGOON_AND_HYDRA,
    CityTrialGoal.option_beat_king_dedede: CTLocation.STADIUM_VSKD_KO_DEDEDE_1MIN,
}
AIR_RIDE_GOAL_TO_LOCATION: dict[int, str] = {
    AirRideGoal.option_100_checklist_blocks: ARLocation.FILL_IN_100_CHECKLIST_BLOCKS,
}
TOP_RIDE_GOAL_TO_LOCATION: dict[int, str] = {
    TopRideGoal.option_100_checklist_blocks: TRLocation.FILL_IN_100_CHECKLIST_BLOCKS,
}
