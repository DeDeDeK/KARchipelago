import typing

from BaseClasses import Callable, CollectionState, Region

from worlds.generic.Rules import add_rule, set_rule

from .KARData import ProgressiveStadiumUnlockType

if typing.TYPE_CHECKING:
    from . import KARWorld


def set_rules(world: "KARWorld"):
    """
    Define the logic rules for locations in Kirby Air Ride.
    Rules are only set for locations if they are present in the world.

    :param world: Kirby Air Ride game world.
    """

    def set_location_rule_if_exists(location_name: str, rule: Callable[[CollectionState], bool]) -> None:
        """
        Set rule on location if it exists in the multiworld.
        """
        try:
            # print(f"adding rule for location: {location_name}: {rule}")
            if world.get_location(location_name):
                add_rule(world.get_location(location_name), rule, "or")
        except KeyError:
            # print(f"didn't set rule for location due to it not existing in the multiworld: {location_name}")
            # location was not added to the multiworld due to player options
            pass

    def set_region_rule_if_exists(region: Region, rule: Callable[[CollectionState], bool]) -> None:
        """
        Set rule on region if it exists in the multiworld.
        """
        try:
            # print(f"adding rule for region: {region.name}: {rule}")
            if world.get_region(region.name):
                # assuming all regions only have one entrance, and that we're adding an additional rule
                # on top of any that might exist, with OR logic.
                add_rule(region.entrances[0], rule, "or")
        except KeyError:
            # print(f"didn't set rule for region due to it not existing in the multiworld: {region.name}")
            # region was not added to the multiworld due to player options
            pass

    # City Trial Rules
    set_location_rule_if_exists(
        "City Trial: Unlock Hydra Parts X, Y, and Z on the Checklist!",
        lambda state: state.can_reach_location("City Trial: Destroy all of the dilapidated houses!", world.player)  # X
        and state.can_reach_location("Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", world.player)  # Y
        and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", world.player),  # Z
    )

    set_location_rule_if_exists(
        "City Trial: Unlock Dragoon Parts A, B, and C on the Checklist!",
        lambda state: state.can_reach_location("Stadium: HIGH JUMP Jump higher than 1,000 feet!", world.player)  # A
        and state.can_reach_location("Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!", world.player)  # B
        and state.can_reach_location("Stadium: KIRBY MELEE (All) KO over 1,500 enemies!", world.player),  # C
    )

    # City trial stadium rules (if progressive stadiums are enabled). Player must have the stadium unlock item to access
    # the stadium
    if world.options.city_trial_progressive_stadiums:

        def extract_stadium_name(name: str) -> str:
            """Extract stadium identifier like 'DRAG RACE 1' from region or item names."""
            if "Unlock Stadium:" in name:
                return name.replace("Unlock Stadium:", "").strip()
            if "Stadium:" in name:
                # Remove "Stadium:" prefix and "ALL" suffix if present
                return name.replace("Stadium:", "").replace("ALL", "").strip()
            return name

        for region in world.get_regions():
            if "Stadium:" in region.name and region.entrances:
                stadium_name = extract_stadium_name(region.name)

                if "ALL" in region.name:
                    # For ALL regions, accept any variant of this stadium type
                    stadium_unlocks = [
                        unlock.value
                        for unlock in ProgressiveStadiumUnlockType
                        if stadium_name in extract_stadium_name(unlock.value)
                    ]

                    if stadium_unlocks:
                        # Use has_any for OR logic - requires ANY of the unlock items
                        set_rule(
                            region.entrances[0],
                            lambda state, unlocks=stadium_unlocks: state.has_any(unlocks, world.player),
                        )
                else:
                    # For specific stadium regions, require exact unlock item
                    matching_unlock = None
                    for unlock in ProgressiveStadiumUnlockType:
                        if stadium_name == extract_stadium_name(unlock.value):
                            matching_unlock = unlock.value
                            break

                    if matching_unlock:
                        set_rule(
                            region.entrances[0], lambda state, unlock=matching_unlock: state.has(unlock, world.player)
                        )

    # Air Ride Rules
    set_location_rule_if_exists(
        "Air Ride: Time Attack: MAGMA FLOWS Finish in under 03:15:00 on Shadow Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Defeat 10 or more enemies using the Quick Spin!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Time Attack: SKY SANDS Finish in under 02:40:00 on Wagon Star!",
        lambda state: state.can_reach_location(
            "Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: FANTASY MEADOWS Do 1 lap under 00:23:00 on Wagon Star!",
        lambda state: state.can_reach_location(
            "Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: FROZEN HILLSIDE Do 1 lap under 01:10:00 on Formula Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:14:00!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: CELESTIAL VALLEY Do 1 lap under 01:02:00 on Slick Star!",
        lambda state: state.can_reach_location(
            "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Time Attack: FANTASY MEADOWS Finish in under 01:05:00 on Slick Star!",
        lambda state: state.can_reach_location(
            "Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: MAGMA FLOWS Do 1 lap under 01:02:00 on Turbo Star!",
        lambda state: state.can_reach_location(
            "Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:10:00 on Turbo Star!",
        lambda state: state.can_reach_location(
            "Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Time Attack: BEANSTALK PARK Finish in under 03:00:00 on Rocket Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: CHECKER KNIGHTS Do 1 lap under 01:25:00 on Rocket Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: BEANSTALK PARK Do 1 lap under 00:58:00 on Winged Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Finish in 1st place while flying through the air!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 02:58:00 on Jet Star!",
        lambda state: state.can_reach_location(
            "Air Ride: MACHINE PASSAGE Race over 4,500 feet in 2 minutes!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: SKY SANDS Do 1 lap under 01:05:00 on Bulk Star!",
        lambda state: state.can_reach_location(
            "Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 03:20:00!", world.player
        ),
    )

    set_location_rule_if_exists(
        "Air Ride: Free Run: MACHINE PASSAGE Do 1 lap under 00:57:00 on Swerve Star!",
        lambda state: state.can_reach_location("Air Ride: SKY SANDS Finish 2 laps in under 02:05:00!", world.player),
    )
