"""Option validation: every OptionError-raising branch in KARWorld, plus the near-miss configs that
deliberately no longer raise. Co-located so the exercised error branches stay auditable at a glance."""

from Options import OptionError, Toggle

from ..KARItems import KARItemName
from ..KARLocations import ARLocation, CTLocation, ProgressionCategory
from ..KAROptions import AirRideGoal, ArchipelagoGoal, CityTrialGoal, TopRideGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase

_ALL_REWARD_CATEGORIES = ["Endings", "Filler Boxes", "Gameplay Extras", "Music", "Sound Test"]


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


def _make_raises_test(name: str, opts: dict, pattern: str) -> None:
    class _Raises(KARTestBase):
        options = opts
        auto_construct = False

        def test_raises_option_error(self):
            with self.assertRaisesRegex(OptionError, pattern):
                self.world_setup()

    _register(_Raises, name)


_make_raises_test(
    "TestNoModesEnabled",
    {
        "city_trial_goal": CityTrialGoal.option_none,
        "air_ride_goal": AirRideGoal.option_none,
        "top_ride_goal": TopRideGoal.option_none,
    },
    r"No modes enabled",
)


# (label, preset, option prefix, goal option class, display name, a location from another mode).
_MODES = [
    ("ct", CT_ONLY, "city_trial", CityTrialGoal, "City Trial", ARLocation.RACE_100_LAPS),
    ("ar", AR_ONLY, "air_ride", AirRideGoal, "Air Ride", CTLocation.DESTROY_ALL_HOUSES),
    ("tr", TR_ONLY, "top_ride", TopRideGoal, "Top Ride", ARLocation.RACE_100_LAPS),
    ("ap", CT_ONLY, "archipelago", ArchipelagoGoal, "Archipelago", CTLocation.RACE_60_MILES),
]

for _label, _preset, _prefix, _goal, _display, _foreign in _MODES:
    # Checkbox fillers pre-complete boxes, so at or above the target they would win the seed outright.
    _make_raises_test(
        f"TestFillerExceedsGoalAmount_{_label}",
        {
            **_preset,
            f"{_prefix}_goal": _goal.option_n_checklist_blocks,
            f"{_prefix}_checklist_amount": 4,
            f"{_prefix}_checkbox_fillers": 4,
        },
        rf"{_display} checkbox fillers",
    )
    _make_raises_test(
        f"TestChecklistListEmpty_{_label}",
        {**_preset, f"{_prefix}_goal": _goal.option_checklist_list, f"{_prefix}_goal_locations": []},
        rf"{_prefix}_goal_locations is empty",
    )
    _make_raises_test(
        f"TestChecklistListWrongMode_{_label}",
        {**_preset, f"{_prefix}_goal": _goal.option_checklist_list, f"{_prefix}_goal_locations": [_foreign]},
        rf"{_display} goal locations include names that are not {_display} locations",
    )


# Starting with a goal's own key would win the seed on the spot, whatever the category's gate says.
for _label, _opts in (
    (
        "dedede_stadiums_gated",
        {
            "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
            "city_trial_stadiums_gated": Toggle.option_true,
            "start_inventory": {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE: 1},
        },
    ),
    (
        "dedede_stadiums_ungated",
        {
            "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
            "city_trial_stadiums_gated": Toggle.option_false,
            "start_inventory": {KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE: 1},
        },
    ),
    (
        "legendary_piece",
        {
            "city_trial_goal": CityTrialGoal.option_hydra_and_dragoon,
            "start_inventory": {KARItemName.UNLOCK_ITEM_DRAGOON_PART_A: 1},
        },
    ),
    (
        "archipelago_sphere",
        {
            "archipelago_goal": ArchipelagoGoal.option_assemble_archipelago_star,
            "start_inventory": {KARItemName.UNLOCK_ITEM_AP_SPHERE_TAN: 1},
        },
    ),
):
    _make_raises_test(
        f"TestGoalKeyInStartInventory_{_label}",
        {**CT_ONLY, **_opts},
        r"starting inventory - this seed's goal is gated on it",
    )


# A named starting_* pick the world must refuse rather than quietly draw something else.
_make_raises_test(
    "TestStartingStadiumIsTheDededeGoal",
    {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_true,
        "starting_stadium": "vs_king_dedede",
    },
    r"Starting Stadium cannot be 'vs_king_dedede'",
)
# Slick Star can only be steered by charge-drifting, so naming it while Charge is gated strands the
# player on their sole machine.
_make_raises_test(
    "TestStartingMachineNeedsLockedCharge",
    {
        **CT_ONLY,
        "machines_gated": Toggle.option_true,
        "base_abilities_gated": Toggle.option_true,
        "starting_machine": "slick_star",
    },
    r"Starting Machine cannot be 'slick_star'",
)


# The capacity validator. Spanning the patch cap 1 -> 30 mints 29 Patch Cap Increases, which needs 115
# non-excluded locations against the 97 a default CT-only seed offers.
_make_raises_test(
    "TestGuaranteedPoolExceedsLocations",
    {
        **CT_ONLY,
        "checklist_rewards": _ALL_REWARD_CATEGORIES,
        "city_trial_patch_cap_min": 1,
        "city_trial_patch_cap_max": 30,
    },
    r"needs \d+ non-excluded locations",
)


# Tuned to fit by one: 65 progression + 19 counted-useful + 6 useful checklist rewards = 90 items needing
# a default location, against the 91 City Trial has once RNG boxes count as progression. Filler rewards
# are not counted - they may sit on excluded boxes. AP Patches are held out, or their locations would
# absorb the excludes the paired test relies on.
_CT_RNG_CATEGORIES = [
    ProgressionCategory.RNG_EVENTS,
    ProgressionCategory.RNG_FOOD,
    ProgressionCategory.RNG_COPY_CHANCE_WHEEL,
]

_TIGHT_POOL = {
    **CT_ONLY,
    "ap_patches": 0,
    "checklist_rewards": _ALL_REWARD_CATEGORIES,
    "city_trial_progression": _CT_RNG_CATEGORIES,
    "city_trial_patch_cap_min": 14,
    "city_trial_patch_cap_max": 18,
}


class TestTightPoolFitsWithoutExcludeLocations(KARTestBase):
    """Baseline for the exclude_locations pair. If this stops fitting - a default-location rebalance, a
    reward reclassification - the paired test's exclude count needs retuning; the split between the two
    pools moves whenever an item's classification does, and their sum is what the validator budgets."""

    options = _TIGHT_POOL

    def test_pool_sizes_are_unchanged(self):
        self.assertEqual(len(self.world.progression_pool), 65)
        self.assertEqual(len(self.world.counted_useful_pool), 19)


_make_raises_test(
    "TestExcludeLocationsTipsValidatorOver",
    {
        **_TIGHT_POOL,
        "exclude_locations": [
            CTLocation.DESTROY_ALL_HOUSES,
            CTLocation.BUST_STAR_POLE,
            CTLocation.BREAK_ALL_ROCKS,
        ],
    },
    r"needs \d+ non-excluded locations",
)


# allowed_items can no longer starve the draw pools: Big Kirby / Small Kirby are immune to it and carry
# every mode, so filler_pool is never empty. These configs used to OptionError; they now generate.
_STILL_FILLS_CASES: list[tuple[str, dict]] = [
    ("every_category_off", {**ALL_MODES, "allowed_items": [], "trap_chance": 0}),
    # Traps fill leftover slots and excluded boxes alongside the cosmetic filler.
    ("every_category_off_full_traps", {**ALL_MODES, "allowed_items": [], "trap_chance": 100}),
    # Top Ride Item Gives is Top Ride's only give-item filler source; a low n_checklist amount forces
    # many excluded boxes on top.
    (
        "top_ride_only_without_tr_gives",
        {
            **TR_ONLY,
            "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
            "top_ride_checklist_amount": 5,
            "top_ride_checkbox_fillers": 0,
            "allowed_items": [
                "Permanent Patches",
                "City Trial Item Gives",
                "City Trial Event Gives",
                "Copy Ability Gives",
            ],
            "trap_chance": 0,
        },
    ),
    # City Trial Item Gives doubles as Air Ride's give-item filler source (the _AR_CT single-stat patches).
    (
        "air_ride_only_without_ct_gives",
        {
            **AR_ONLY,
            "air_ride_goal": AirRideGoal.option_n_checklist_blocks,
            "air_ride_checklist_amount": 5,
            "air_ride_checkbox_fillers": 0,
            "allowed_items": [
                "Permanent Patches",
                "City Trial Event Gives",
                "Copy Ability Gives",
                "Top Ride Item Gives",
            ],
            "trap_chance": 0,
        },
    ),
]


def _make_still_fills_test(opts: dict) -> type:
    class _StillFills(KARTestBase):
        options = opts

        def test_generates_with_a_populated_pool(self):
            self.assertTrue(self.world.item_pools_built)
            self.assertIn(KARItemName.BIG_KIRBY, self.world.filler_pool)
            self.assertEqual(len(self.itempool_items()), len(self.placeable_locations()))

    return _StillFills


for _label, _opts in _STILL_FILLS_CASES:
    _register(_make_still_fills_test(_opts), f"TestAllowedItemsStillFills_{_label}")
