import typing

from BaseClasses import Callable, CollectionState
from worlds.generic.Rules import set_rule

from .KARData import ProgressiveStadiumUnlockType
from .KARLocations import CITY_TRIAL_LOCATION_TABLE

if typing.TYPE_CHECKING:
    from . import KARWorld


def set_rules(world: "KARWorld"):
    """
    Define the logic rules for locations in Kirby Air Ride.
    Rules are only set for locations if they are present in the world.

    :param world: Kirby Air Ride game world.
    """

    def set_rule_if_exists(location_name: str, rule: Callable[[CollectionState], bool]) -> None:
        """
        Set rule on location if it exists in the multiworld.
        """
        try:
            if world.get_location(location_name):
                set_rule(world.get_location(location_name), rule)
        except KeyError:
            # location was not added to the multiworld due to player options
            pass

    # City Trial Rules
    set_rule_if_exists(
        "City Trial: Unlock Hydra Parts X, Y, and Z on the Checklist!",
        lambda state: state.can_reach_location("City Trial: Destroy all of the dilapidated houses!", world.player)  # X
        and state.can_reach_location("Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", world.player)  # Y
        and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", world.player),  # Z
    )

    set_rule_if_exists(
        "City Trial: Unlock Dragoon Parts A, B, and C on the Checklist!",
        lambda state: state.can_reach_location("Stadium: HIGH JUMP Jump higher than 1,000 feet!", world.player)  # A
        and state.can_reach_location("Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", world.player)  # B
        and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", world.player),  # C
    )

    set_rule_if_exists(
        "City Trial: In one match, complete both Dragoon and Hydra!",
        lambda state: state.can_reach_location(
            "City Trial: Unlock Hydra Parts X, Y, and Z on the Checklist!", world.player
        )
        and state.can_reach_location("City Trial: Unlock Dragoon Parts A, B, and C on the Checklist!", world.player),
    )

    # City trial stadium rules (if progressive stadiums are enabled). Player must have the stadium unlock item to access
    # the stadium
    if world.options.city_trial_progressive_stadiums:
        for location_name, location_data in CITY_TRIAL_LOCATION_TABLE.items():
            if "Stadium:" in location_data.region:
                if "ALL" in location_data.region:
                    # location that applies to any of the given stadium, so any of the unlock items for that stadium will work
                    stadium_unlocks = [
                        stadium_unlock_type.value
                        for stadium_unlock_type in ProgressiveStadiumUnlockType
                        if location_data.region.rstrip(" ALL") in stadium_unlock_type.value
                    ]
                    set_rule_if_exists(location_name, lambda state: state.has_any(stadium_unlocks, world.player))
                else:
                    stadium_unlock_type = ProgressiveStadiumUnlockType("Unlock " + location_data.region)
                    set_rule_if_exists(location_name, lambda state: state.has(stadium_unlock_type.value, world.player))

    # Air Ride Rules
    set_rule_if_exists(
        "Air Ride: Time Attack: MAGMA FLOWS Finish in under 03:15:00 on Shadow Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Defeat 10 or more enemies using the Quick Spin!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Time Attack: SKY SANDS Finish in under 02:40:00 on Wagon Star!",
        lambda state: state.can_reach_location(
            "Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: FANTASY MEADOWS Do 1 lap under 00:23:00 on Wagon Star!",
        lambda state: state.can_reach_location(
            "Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: FROZEN HILLSIDE Do 1 lap under 01:10:00 on Formula Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:14:00!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: CELESTIAL VALLEY Do 1 lap under 01:02:00 on Slick Star!",
        lambda state: state.can_reach_location(
            "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Time Attack: FANTASY MEADOWS Finish in under 01:05:00 on Slick Star!",
        lambda state: state.can_reach_location(
            "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: MAGMA FLOWS Do 1 lap under 01:02:00 on Turbo Star!",
        lambda state: state.can_reach_location(
            "Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:10:00 on Turbo Star!",
        lambda state: state.can_reach_location(
            "Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Time Attack: BEANSTALK PARK Finish in under 03:00:00 on Rocket Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: CHECKER KNIGHTS Do 1 lap under 01:25:00 on Rocket Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: BEANSTALK PARK Do 1 lap under 00:58:00 on Winged Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Finish in 1st place while flying through the air!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 02:58:00 on Jet Star!",
        lambda state: state.can_reach_location(
            "Air Ride: MACHINE PASSAGE Race over 4,500 feet in 2 minutes!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: SKY SANDS Do 1 lap under 01:05:00 on Bulk Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 03:20:00!", world.player
        ),
    )

    set_rule_if_exists(
        "Air Ride: Free Run: MACHINE PASSAGE Do 1 lap under 00:57:00 on Swerve Star!",
        lambda state: state.can_reach_location("Air Ride: SKY SANDS Finish 2 laps in under 02:05:00!", world.player),
    )
