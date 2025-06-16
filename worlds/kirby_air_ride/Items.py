from typing import NamedTuple, Optional

from BaseClasses import Item, ItemClassification

from .Locations import CITY_TRIAL_LOCATION_TABLE


class KARItemData(NamedTuple):
    """
    This class represents the data for an item in Kirby Air Ride.

    :param type: The type of the item (e.g., "Patch", "Air Ride Machine").
    :param classification: The item's classification (progression, useful, filler, trap).
    :param code: The unique code identifier for the item.
    :param quantity: The number of this item available.
    :param item_id: The ID (if any) used to represent the item in-game.
    """

    type: str
    classification: ItemClassification
    code: Optional[int]
    quantity: int
    item_id: Optional[int]


class KARItem(Item):
    """
    This class represents an item in Kirby Air Ride.

    :param name: The item's name.
    :param player: The ID of the player who owns the item.
    :param data: The data associated with this item.
    :param classification: Optional classification to override the default.
    """

    game: str = "Kirby Air Ride"
    type: Optional[str]

    def __init__(
        self,
        name: str,
        player: int,
        data: KARItemData,
        classification: Optional[ItemClassification] = None,
    ) -> None:
        super().__init__(
            name,
            data.classification if classification is None else classification,
            None if data.code is None else data.code,
            player,
        )

        self.type = data.type
        self.item_id = data.item_id


ITEM_TABLE: dict[str, KARItemData] = {
    # "Warpstar": KARItemData("Air Ride Machine", ItemClassification.progression, 1, 1, 0x0000),
    # "Compact Star": KARItemData("Air Ride Machine", ItemClassification.progression, 2, 1, 0x0001),
    # "Winged Star": KARItemData("Air Ride Machine", ItemClassification.progression, 3, 1, 0x0002),
    # "Shadow Star": KARItemData("Air Ride Machine", ItemClassification.progression, 4, 1, 0x0003),
    # "Hydra Star": KARItemData("Air Ride Machine", ItemClassification.progression, 5, 1, 0x0004),
    # "Bulk Star": KARItemData("Air Ride Machine", ItemClassification.progression, 6, 1, 0x0005),
    # "Slick Star": KARItemData("Air Ride Machine", ItemClassification.progression, 7, 1, 0x0006),
    # "Formula Star": KARItemData("Air Ride Machine", ItemClassification.progression, 8, 1, 0x0007),
    # "Dragoon Star": KARItemData("Air Ride Machine", ItemClassification.progression, 9, 1, 0x0008),
    # "Wagon Star": KARItemData("Air Ride Machine", ItemClassification.progression, 10, 1, 0x0009),
    # "Rocket Star": KARItemData("Air Ride Machine", ItemClassification.progression, 11, 1, 0x000A),
    # "Swerve Star": KARItemData("Air Ride Machine", ItemClassification.progression, 12, 1, 0x000B),
    # "Turbo Star": KARItemData("Air Ride Machine", ItemClassification.progression, 13, 1, 0x000C),
    # "Jet Star": KARItemData("Air Ride Machine", ItemClassification.progression, 14, 1, 0x000D),
    # "Flight Warpstar": KARItemData("Air Ride Machine", ItemClassification.progression, 15, 1, 0x000E),
    # "Free Star": KARItemData("Air Ride Machine", ItemClassification.progression, 16, 1, 0x000F),
    # "Steer Star": KARItemData("Air Ride Machine", ItemClassification.progression, 17, 1, 0x0010),
    # "Invisible Star (Kirby)": KARItemData("Air Ride Machine", ItemClassification.progression, 18, 1, 0x0011),
    # "Invisible Star (Meta Knight)": KARItemData("Air Ride Machine", ItemClassification.progression, 19, 1, 0x0012),
    # "Beta Wheelie": KARItemData("Air Ride Machine", ItemClassification.progression, 20, 1, 0x1000),
    # "Wheelie": KARItemData("Air Ride Machine", ItemClassification.progression, 21, 1, 0x1001),
    # "Wheelie Bike": KARItemData("Air Ride Machine", ItemClassification.progression, 22, 1, 0x1002),
    # "Rex Wheelie": KARItemData("Air Ride Machine", ItemClassification.progression, 23, 1, 0x1003),
    # "Wheelie Scooter": KARItemData("Air Ride Machine", ItemClassification.progression, 24, 1, 0x1004),
    # "King Dedede Wheelie": KARItemData("Air Ride Machine", ItemClassification.progression, 25, 1, 0x1005),
    # "King Dedede VS Wheelie": KARItemData("Air Ride Machine", ItemClassification.progression, 26, 1, 0x1006),
    # "Blue Box": KARItemData("Box", ItemClassification.filler, 27, 20, 0x00),
    # "Green Box": KARItemData("Box", ItemClassification.filler, 28, 20, 0x01),
    # "Red Box": KARItemData("Box", ItemClassification.filler, 29, 20, 0x02),
    "Boost Up": KARItemData("Patch", ItemClassification.useful, 30, 10, 0x03),
    "Boost Down": KARItemData("Patch", ItemClassification.trap, 31, 10, 0x04),
    "Top Speed Up": KARItemData("Patch", ItemClassification.useful, 32, 10, 0x05),
    "Top Speed Down": KARItemData("Patch", ItemClassification.trap, 33, 10, 0x06),
    "Offense Up": KARItemData("Patch", ItemClassification.useful, 34, 10, 0x07),
    "Offense Down": KARItemData("Patch", ItemClassification.trap, 35, 10, 0x08),
    "Defense Up": KARItemData("Patch", ItemClassification.useful, 36, 10, 0x09),
    "Defense Down": KARItemData("Patch", ItemClassification.trap, 37, 10, 0x0A),
    "Turn Up": KARItemData("Patch", ItemClassification.useful, 38, 10, 0x0B),
    "Turn Down": KARItemData("Patch", ItemClassification.trap, 39, 10, 0x0C),
    "Glide Up": KARItemData("Patch", ItemClassification.useful, 40, 10, 0x0D),
    "Glide Down": KARItemData("Patch", ItemClassification.trap, 41, 10, 0x0E),
    "Charge Up": KARItemData("Patch", ItemClassification.useful, 42, 10, 0x0F),
    "Charge Down": KARItemData("Patch", ItemClassification.trap, 43, 10, 0x10),
    "Weight Up": KARItemData("Patch", ItemClassification.useful, 44, 10, 0x11),
    "Weight Down": KARItemData("Patch", ItemClassification.trap, 45, 10, 0x12),
    "HP Up": KARItemData("Patch", ItemClassification.useful, 46, 10, 0x13),
    "HP Down": KARItemData("Patch", ItemClassification.trap, 47, 10, None),
    "Boost Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 48, 5, None),
    "Top Speed Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 49, 5, None),
    "Offense Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 50, 5, None),
    "Defense Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 51, 5, None),
    "Turn Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 52, 5, None),
    "Glide Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 53, 5, None),
    "Charge Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 54, 5, None),
    "Weight Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 55, 5, None),
    "HP Up: Permanent +1": KARItemData("Patch", ItemClassification.progression, 56, 5, None),
    "All Up": KARItemData("Patch", ItemClassification.useful, 57, 5, 0x14),
    # "Speed Up": KARItemData("Patch", ItemClassification.useful, 48, 20, 0x15),
    # "Speed Down": KARItemData("Patch", ItemClassification.trap, 49, 20, 0x16),
    # "Attack Up": KARItemData("Patch", ItemClassification.useful, 50, 20, 0x17),
    # "Attack Down": KARItemData("Patch", ItemClassification.trap, 51, 20, 0x18),  # this might also be Defense Up?
    # "Run Amok": KARItemData("Effect", ItemClassification.trap, 52, 20, 0x19),
    # "No Charge": KARItemData("Effect", ItemClassification.trap, 53, 20, 0x1A),
    # "Invincible Candy": KARItemData("Effect", ItemClassification.useful, 54, 20, 0x1B),
    # "Bomb Ability": KARItemData("Ability", ItemClassification.useful, 55, 20, 0x1C),
    # "Flame Ability": KARItemData("Ability", ItemClassification.useful, 56, 20, 0x1D),
    # "Ice Ability": KARItemData("Ability", ItemClassification.useful, 57, 20, 0x1E),
    # "Sleep Ability": KARItemData("Ability", ItemClassification.trap, 58, 20, 0x1F),
    # "Wheel Ability": KARItemData("Ability", ItemClassification.trap, 59, 20, 0x20),
    # "Bird Ability": KARItemData("Ability", ItemClassification.trap, 60, 20, 0x21),
    # "Electric Ability": KARItemData("Ability", ItemClassification.useful, 61, 20, 0x22),
    # "Tornado Ability": KARItemData("Ability", ItemClassification.useful, 62, 20, 0x23),
    # "Sword Ability": KARItemData("Ability", ItemClassification.useful, 63, 20, 0x24),
    # "Spike Ability": KARItemData("Ability", ItemClassification.useful, 64, 20, 0x25),
    # "Mic Ability": KARItemData("Ability", ItemClassification.useful, 65, 20, 0x26),
    # "Maxim Tomato": KARItemData("Food", ItemClassification.useful, 66, 10, 0x27),
    # "Drink": KARItemData("Food", ItemClassification.filler, 67, 10, 0x28),
    # "Ice Cream Cone": KARItemData("Food", ItemClassification.filler, 68, 10, 0x29),
    # "Riceball": KARItemData("Food", ItemClassification.filler, 69, 10, 0x2A),
    # "Turkey": KARItemData("Food", ItemClassification.filler, 70, 10, 0x2B),
    # "Bowl": KARItemData("Food", ItemClassification.filler, 71, 10, 0x2C),
    # "Bowl 2": KARItemData("Food", ItemClassification.filler, 72, 10, 0x2D),
    # "Omurice": KARItemData("Food", ItemClassification.filler, 73, 10, 0x2E),
    # "Hamburger": KARItemData("Food", ItemClassification.filler, 74, 10, 0x2F),
    # "Sushi": KARItemData("Food", ItemClassification.filler, 75, 10, 0x30),
    # "Hot Dog": KARItemData("Food", ItemClassification.filler, 76, 10, 0x31),
    # "Apple": KARItemData("Food", ItemClassification.filler, 77, 10, 0x32),
    # "Cracker": KARItemData("Food", ItemClassification.filler, 78, 10, 0x33),
    # "Panic Spin": KARItemData("Ability", ItemClassification.useful, 79, 10, 0x34),
    # "Time Bomb": KARItemData("Ability", ItemClassification.useful, 80, 10, 0x35),
    # "Gordo": KARItemData("Ability", ItemClassification.useful, 81, 10, 0x36),
    # "Hydra Piece 1": KARItemData("Legendary Piece", ItemClassification.progression, 82, 1, 0x37),
    # "Hydra Piece 2": KARItemData("Legendary Piece", ItemClassification.progression, 83, 1, 0x38),
    # "Hydra Piece 3": KARItemData("Legendary Piece", ItemClassification.progression, 84, 1, 0x39),
    # "Dragoon Piece 1": KARItemData("Legendary Piece", ItemClassification.progression, 85, 1, 0x3A),
    # "Dragoon Piece 2": KARItemData("Legendary Piece", ItemClassification.progression, 86, 1, 0x3B),
    # "Dragoon Piece 3": KARItemData("Legendary Piece", ItemClassification.progression, 87, 1, 0x3C),
    # "Fake Boost": KARItemData("Fake Patch", ItemClassification.trap, 88, 10, 0x3D),
    # "Fake Top Speed": KARItemData("Fake Patch", ItemClassification.trap, 89, 10, 0x3E),
    # "Fake Offense": KARItemData("Fake Patch", ItemClassification.trap, 90, 10, 0x3F),
    # "Fake Defense": KARItemData("Fake Patch", ItemClassification.trap, 91, 10, 0x40),
    # "Fake Turn": KARItemData("Fake Patch", ItemClassification.trap, 92, 10, 0x41),
    # "Fake Glide": KARItemData("Fake Patch", ItemClassification.trap, 93, 10, 0x42),
    # "Fake Charge": KARItemData("Fake Patch", ItemClassification.trap, 94, 10, 0x43),
    # "Fake Weight": KARItemData("Fake Patch", ItemClassification.trap, 95, 10, 0x44),
}

# update the item table with chekcbox reward items. use a 500 offset to avoid colliding with item_table items
ITEM_TABLE.update(
    {
        location_data.reward: KARItemData("Checkbox Reward", ItemClassification.progression, location_data.code + 500, 1, None)
        for location_name, location_data in CITY_TRIAL_LOCATION_TABLE.items()
        if location_data.code is not None and location_data.reward != "None"
    }
)

LOOKUP_ID_TO_NAME: dict[int, str] = {data.code: item for item, data in ITEM_TABLE.items() if data.code is not None}

item_name_groups = {
    "Abilities": {
        "Bomb Ability",
        "Flame Ability",
        "Ice Ability",
        "Sleep Ability",
        "Wheel Ability",
        "Bird Ability",
        "Electric Ability",
        "Tornado Ability",
        "Sword Ability",
        "Spike Ability",
        "Mic Ability",
        "Panic Spin",
        "Time Bomb",
        "Gordo",
    },
    "Foods": {
        "Maxim Tomato",
        "Drink",
        "Ice Cream Cone",
        "Riceball",
        "Turkey",
        "Bowl",
        "Bowl 2",
        "Omurice",
        "Hamburger",
        "Sushi",
        "Hot Dog",
        "Apple",
        "Cracker",
    },
    "Boxes": {
        "Blue Box",
        "Green Box",
        "Red Box",
    },
    "Effects": {
        "Run Amok",
        "No Charge",
        "Invincible Candy",
    },
    "Air Ride Machines": {
        "Warpstar",
        "Compact Star",
        "Winged Star",
        "Shadow Star",
        "Hydra Star",
        "Bulk Star",
        "Slick Star",
        "Formula Star",
        "Dragoon Star",
        "Wagon Star",
        "Rocket Star",
        "Swerve Star",
        "Turbo Star",
        "Jet Star",
        "Flight Warpstar",
        "Free Star",
        "Steer Star",
        "Invisible Star (Kirby)",
        "Invisible Star (Meta Knight)",
        "Beta Wheelie",
        "Wheelie",
        "Wheelie Bike",
        "Rex Wheelie",
        "Wheelie Scooter",
        "King Dedede Wheelie",
        "King Dedede VS Wheelie",
    },
    "Patches": {
        "Boost Up",
        "Boost Down",
        "Top Speed Up",
        "Top Speed Down",
        "Offense Up",
        "Offense Down",
        "Defense Up",
        "Defense Down",
        "Turn Up",
        "Turn Down",
        "Glide Up",
        "Glide Down",
        "Charge Up",
        "Charge Down",
        "Weight Up",
        "Weight Down",
        "HP Up",
        "All Up",
        "Speed Up",
        "Speed Down",
        "Attack Up",
        "Attack Down",
        "Boost Up: Permanent +1",
        "Top Speed Up: Permanent +1",
        "Offense Up: Permanent +1",
        "Defense Up: Permanent +1",
        "Turn Up: Permanent +1",
        "Glide Up: Permanent +1",
        "Charge Up: Permanent +1",
        "Weight Up: Permanent +1",
        "HP Up: Permanent +1",
    },
    "Fake Patches": {
        "Fake Boost",
        "Fake Top Speed",
        "Fake Offense",
        "Fake Defense",
        "Fake Turn",
        "Fake Glide",
        "Fake Charge",
        "Fake Weight",
    },
    "Legendary Pieces": {
        "Hydra Piece 1",
        "Hydra Piece 2",
        "Hydra Piece 3",
        "Dragoon Piece 1",
        "Dragoon Piece 2",
        "Dragoon Piece 3",
    },
}
