"""Starter picks: which categories grant a precollected unlock, what is barred from the draw, and how a
named `starting_*` pick or a start_inventory preset replaces it. Nothing here asserts on a draw -
`starter_candidates` records the candidate list instead, so an exclusion is one set comparison."""

from Options import Toggle

from ..KARItems import (
    ASSEMBLED_MACHINE_UNLOCKS,
    CHARGE_DEPENDENT_MACHINES,
    STADIUM_UNLOCK_ITEMS,
    KARItemGroup,
    KARItemName,
    item_name_groups,
)
from ..KAROptions import CityTrialGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, names, recording_random

# Every attribute _determine_starter_items assigns, saved and restored around a recorded re-run so the
# helper leaves the world exactly as it found it.
_STARTER_ATTRS = (
    "stadium_starter_choice",
    "machine_starter_choice",
    "tr_machine_starter_choice",
    "ar_course_starter_choice",
    "tr_course_starter_choice",
    "color_starter_choice",
)

_ALL_STADIUMS = names(STADIUM_UNLOCK_ITEMS)
_ALL_MACHINES = names(item_name_groups[KARItemGroup.MACHINE_UNLOCKS])
_TR_MACHINES = names({KARItemName.UNLOCK_MACHINE_FREE_STAR, KARItemName.UNLOCK_MACHINE_STEER_STAR})
# The legendaries are assembled from pieces rather than selected, so they are never a starter.
_ASSEMBLED = names(ASSEMBLED_MACHINE_UNLOCKS)
# The AR/CT starter must be rideable in Air Ride and City Trial, which the Top Ride controls are not.
_ARCT_MACHINES = _ALL_MACHINES - _TR_MACHINES - _ASSEMBLED


def starter_candidates(world, attr: str) -> set[str]:
    """Every item the `attr` pick was willing to draw, by re-running `_determine_starter_items` with a
    recording `world.random`. The recorder returns the first entry offered, so the call that produced
    `attr` is the one whose first entry is the chosen value - asserted, not assumed."""
    saved = {name: getattr(world, name) for name in _STARTER_ATTRS}
    try:
        with recording_random(world) as recorder:
            for name in _STARTER_ATTRS:
                setattr(world, name, None)
            world._determine_starter_items()
            chosen = getattr(world, attr)
    finally:
        for name, value in saved.items():
            setattr(world, name, value)

    if chosen is None:
        return set()
    matching = [offered for offered in recorder.offers if offered and offered[0] == chosen]
    if len(matching) != 1:
        raise AssertionError(f"could not identify the {attr} draw among {len(recorder.offers)} recorded picks")
    return names(matching[0])


def _register(cls: type, name: str) -> None:
    cls.__name__ = name
    cls.__qualname__ = name
    globals()[name] = cls


# (label, options, starter attribute, item group, eligible candidate set). One starter is handed over per
# gated category whose mode is in play, it is excluded from the pool, and the draw is taken from exactly
# the listed set.
_STARTER_CASES: list[tuple[str, dict, str, set[str], set[str]]] = [
    (
        "stadium",
        {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true},
        "stadium_starter_choice",
        _ALL_STADIUMS,
        # No stadium is barred while VS King Dedede is not the goal, secret ones included.
        _ALL_STADIUMS,
    ),
    (
        "stadium_with_dedede_goal",
        {
            **CT_ONLY,
            "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
            "city_trial_stadiums_gated": Toggle.option_true,
        },
        "stadium_starter_choice",
        _ALL_STADIUMS,
        # Handing over the goal's own stadium would hand over the goal.
        _ALL_STADIUMS - {str(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)},
    ),
    (
        "ar_course",
        {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true},
        "ar_course_starter_choice",
        names(item_name_groups[KARItemGroup.AR_COURSE_UNLOCKS]),
        names(item_name_groups[KARItemGroup.AR_COURSE_UNLOCKS]),
    ),
    (
        "tr_course",
        {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true},
        "tr_course_starter_choice",
        names(item_name_groups[KARItemGroup.TR_COURSE_UNLOCKS]),
        names(item_name_groups[KARItemGroup.TR_COURSE_UNLOCKS]),
    ),
    (
        # Colors are cross-mode: a starter is granted whenever colors_gated is on. Pink is eligible like
        # any other, even though the mod falls back to it when nothing is unlocked.
        "color",
        {**CT_ONLY, "colors_gated": Toggle.option_true},
        "color_starter_choice",
        names(item_name_groups[KARItemGroup.COLOR_UNLOCKS]),
        names(item_name_groups[KARItemGroup.COLOR_UNLOCKS]),
    ),
    (
        # Top Ride is not one of machines_gated's required modes, so the TR control machine is only a
        # starter when City Trial or Air Ride is also enabled to make the gate hold keys. The group is
        # narrowed to the TR pair because such a seed also draws an Air Ride / City Trial machine.
        "tr_machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "tr_machine_starter_choice",
        _TR_MACHINES,
        _TR_MACHINES,
    ),
    (
        "arct_machine",
        {**AR_ONLY, "machines_gated": Toggle.option_true},
        "machine_starter_choice",
        _ALL_MACHINES,
        _ARCT_MACHINES,
    ),
    (
        # Both machine gates plus base abilities: the starter has to be steerable before Charge arrives.
        "arct_machine_charge_gated",
        {**AR_ONLY, "machines_gated": Toggle.option_true, "base_abilities_gated": Toggle.option_true},
        "machine_starter_choice",
        _ALL_MACHINES,
        _ARCT_MACHINES - names(CHARGE_DEPENDENT_MACHINES),
    ),
]


def _make_starter_test(opts: dict, attr: str, group: set[str], eligible: set[str]) -> type:
    class _Starter(KARTestBase):
        options = opts

        def test_exactly_one_starter_from_the_group(self):
            self.assertEqual(len(self.precollected_in(group)), 1)

        def test_the_chosen_item_is_the_precollected_one_and_left_the_pool(self):
            chosen = getattr(self.world, attr)
            self.assertIsNotNone(chosen)
            self.assertIn(str(chosen), self.precollected_names())
            self.assertNotIn(str(chosen), self.itempool_names())

        def test_the_draw_was_offered_exactly_the_eligible_set(self):
            # Set equality rather than disjointness: a "no overlap" assertion would also pass on an
            # empty candidate list.
            self.assertEqual(starter_candidates(self.world, attr), eligible)

    return _Starter


for _label, _opts, _attr, _group, _eligible in _STARTER_CASES:
    _register(_make_starter_test(_opts, _attr, _group, _eligible), f"TestStarter_{_label}")


class TestMachineStarterAllModes(KARTestBase):
    """All modes plus machine gating yields two machine starters - one Air Ride / City Trial machine and
    one Top Ride control machine - because the two lobbies gate on disjoint sets."""

    options = {**ALL_MODES, "machines_gated": Toggle.option_true}

    def test_one_starter_from_each_half(self):
        starters = [n for n in self.precollected_names() if n in _ALL_MACHINES]
        self.assertEqual(len(starters), 2)
        self.assertEqual(len([n for n in starters if n in _TR_MACHINES]), 1)
        self.assertEqual(len([n for n in starters if n not in _TR_MACHINES]), 1)


class TestChargeDependentMachinesStayInThePool(KARTestBase):
    """Held out of the starter pick only - they remain ordinary progression items."""

    options = {**ALL_MODES, "machines_gated": Toggle.option_true, "base_abilities_gated": Toggle.option_true}

    def test_still_in_pool(self):
        pool = self.itempool_names()
        for machine in CHARGE_DEPENDENT_MACHINES:
            with self.subTest(machine=machine):
                self.assertIn(machine, pool)


class TestNoStarterForADisabledMode(KARTestBase):
    """A starter is granted only when its owning mode is enabled: an Air-Ride-only seed picks a machine
    but no stadium, even with stadium gating on."""

    options = {**AR_ONLY, "machines_gated": Toggle.option_true, "city_trial_stadiums_gated": Toggle.option_true}

    def test_machine_picked_but_no_stadium(self):
        self.assertEqual(len(self.precollected_in(_ALL_MACHINES)), 1)
        self.assertEqual(self.precollected_in(_ALL_STADIUMS), [])
        self.assertIsNone(self.world.tr_machine_starter_choice)


class TestNoMachineStarterWhenOnlyTopRideIsEnabled(KARTestBase):
    """`machines_gated` needs City Trial or Air Ride to hold keys, so a Top-Ride-only seed mints no
    machine unlocks however the option is set - and must therefore hand out no machine starter. The
    starter branch used to read the raw option and precollect a Free/Steer Star for a category the
    mod opens wholesale at connect."""

    options = {**TR_ONLY, "machines_gated": Toggle.option_true}

    def test_gate_does_not_hold_keys(self):
        self.assertNotIn("machines_gated", self.world.effective_gates)
        self.assertEqual(self.world.fill_slot_data()["machines_gated"], 0)

    def test_no_machine_starter_and_no_machine_items(self):
        self.assertIsNone(self.world.tr_machine_starter_choice)
        self.assertIsNone(self.world.machine_starter_choice)
        self.assertEqual(self.precollected_in(_ALL_MACHINES), [])
        # Nothing to precollect precisely because nothing was minted.
        self.assertEqual([n for n in self.itempool_names() if n in _ALL_MACHINES], [])


# Unlock items and checklist rewards are one-time, so presetting one in start_inventory must drop its
# pool copy. Copy abilities and rewards grant no starter, so they exercise the general dedup path.
def _make_preset_dedup_test(preset_item: str, opts: dict) -> type:
    class _PresetDedup(KARTestBase):
        options = {**opts, "start_inventory": {preset_item: 1}}

        def test_precollected_and_absent_from_pool(self):
            self.assertIn(preset_item, self.precollected_names())
            self.assertNotIn(preset_item, self.itempool_names())

    return _PresetDedup


for _label, _item, _opts in (
    ("ability", KARItemName.UNLOCK_ABILITY_FIRE, {**CT_ONLY, "abilities_gated": Toggle.option_true}),
    ("checklist_reward", KARItemName.CT_REWARD_MUSIC_CITY, CT_ONLY),
):
    _register(_make_preset_dedup_test(_item, _opts), f"TestPresetNotDuplicatedInPool_{_label}")


# Per category: presetting an item in start_inventory makes the world skip its random pick, and the
# preset still lands in precollected.
_PRESET_RESPECT_CASES: list[tuple[str, dict, str, str]] = [
    (
        "stadium",
        {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true},
        "stadium_starter_choice",
        KARItemName.UNLOCK_STADIUM_AIR_GLIDER,
    ),
    (
        "machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    ),
    (
        "tr_machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "tr_machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_FREE_STAR,
    ),
    (
        "ar_course",
        {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true},
        "ar_course_starter_choice",
        KARItemName.UNLOCK_AR_COURSE_FANTASY_MEADOWS,
    ),
    (
        "tr_course",
        {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true},
        "tr_course_starter_choice",
        KARItemName.UNLOCK_TR_COURSE_GRASS,
    ),
    (
        "color",
        {**CT_ONLY, "colors_gated": Toggle.option_true},
        "color_starter_choice",
        KARItemName.UNLOCK_COLOR_BLUE,
    ),
]


def _make_starter_preset_test(label: str, opts: dict, choice_attr: str, preset: str) -> type:
    class _StarterPresetRespect(KARTestBase):
        options = {**opts, "start_inventory": {preset: 1}}

        def test_no_random_pick_when_preset(self):
            self.assertIsNone(
                getattr(self.world, choice_attr),
                f"world should skip its random {label} pick when the player presets one",
            )
            self.assertIn(preset, self.precollected_names())

    return _StarterPresetRespect


for _label, _opts, _attr, _preset in _PRESET_RESPECT_CASES:
    _register(_make_starter_preset_test(_label, _opts, _attr, _preset), f"TestStarterRespectsStartInventory_{_label}")


# Per category: naming an unlock in its starting_* option hands over exactly that one instead of a draw.
# (label, options, starting_* option, its choice key, starter attribute, named item, item group, how
# many starters that group should end up holding - the all-modes machine case hands out two.)
_NAMED_STARTER_CASES: list[tuple[str, dict, str, str, str, str, str, int]] = [
    (
        "stadium",
        {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true},
        "starting_stadium",
        "air_glider",
        "stadium_starter_choice",
        KARItemName.UNLOCK_STADIUM_AIR_GLIDER,
        KARItemGroup.CT_STADIUM_UNLOCKS,
        1,
    ),
    (
        "machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "starting_machine",
        "jet_star",
        "machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_JET_STAR,
        KARItemGroup.MACHINE_UNLOCKS,
        2,
    ),
    (
        "tr_machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "starting_top_ride_machine",
        "steer_star",
        "tr_machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_STEER_STAR,
        KARItemGroup.MACHINE_UNLOCKS,
        2,
    ),
    (
        "ar_course",
        {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true},
        "starting_air_ride_course",
        "nebula_belt",
        "ar_course_starter_choice",
        KARItemName.UNLOCK_AR_COURSE_NEBULA_BELT,
        KARItemGroup.AR_COURSE_UNLOCKS,
        1,
    ),
    (
        "tr_course",
        {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true},
        "starting_top_ride_course",
        "metal",
        "tr_course_starter_choice",
        KARItemName.UNLOCK_TR_COURSE_METAL,
        KARItemGroup.TR_COURSE_UNLOCKS,
        1,
    ),
    (
        "color",
        {**CT_ONLY, "colors_gated": Toggle.option_true},
        "starting_kirby_color",
        "white",
        "color_starter_choice",
        KARItemName.UNLOCK_COLOR_WHITE,
        KARItemGroup.COLOR_UNLOCKS,
        1,
    ),
    (
        # The charge-dependent bar is specific to base_abilities_gated: with Charge free from the start,
        # Slick Star is an ordinary named pick.
        "charge_dependent_machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "starting_machine",
        "slick_star",
        "machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_SLICK_STAR,
        KARItemGroup.MACHINE_UNLOCKS,
        2,
    ),
    (
        # VS. KING DEDEDE is barred only when it is the goal; under any other goal it is nameable.
        "dedede_stadium_without_that_goal",
        {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true},
        "starting_stadium",
        "vs_king_dedede",
        "stadium_starter_choice",
        KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE,
        KARItemGroup.CT_STADIUM_UNLOCKS,
        1,
    ),
]


def _make_named_starter_test(opts: dict, option: str, key: str, attr: str, named: str, group: str, count: int) -> type:
    class _NamedStarter(KARTestBase):
        options = {**opts, option: key}

        def test_named_item_is_the_only_starter_from_its_category(self):
            self.assertEqual(getattr(self.world, attr), named)
            self.assertIn(named, self.precollected_names())
            self.assertNotIn(named, self.itempool_names())
            self.assertEqual(len(self.precollected_in(item_name_groups[group])), count)

    return _NamedStarter


for _label, _opts, _option, _key, _attr, _named, _group, _count in _NAMED_STARTER_CASES:
    _register(
        _make_named_starter_test(_opts, _option, _key, _attr, _named, _group, _count), f"TestNamedStarter_{_label}"
    )


class TestNamedStarterAlsoPresetIsNotDuplicated(KARTestBase):
    """Naming the unlock the player already preset precollects it once: the world hands over nothing on
    top of a pick start_inventory already covers."""

    options = {
        **CT_ONLY,
        "colors_gated": Toggle.option_true,
        "starting_kirby_color": "blue",
        "start_inventory": {KARItemName.UNLOCK_COLOR_BLUE: 1},
    }

    def test_single_precollected_copy(self):
        self.assertIsNone(self.world.color_starter_choice)
        self.assertEqual(self.precollected_names().count(KARItemName.UNLOCK_COLOR_BLUE), 1)


class TestNamedStarterStacksWithADifferentPreset(KARTestBase):
    """A preset from the same category suppresses the random draw but not an explicit pick, so a player
    who asks for both gets both."""

    options = {
        **CT_ONLY,
        "colors_gated": Toggle.option_true,
        "starting_kirby_color": "white",
        "start_inventory": {KARItemName.UNLOCK_COLOR_BLUE: 1},
    }

    def test_both_colors_precollected(self):
        precollected = self.precollected_names()
        self.assertEqual(self.world.color_starter_choice, KARItemName.UNLOCK_COLOR_WHITE)
        self.assertIn(KARItemName.UNLOCK_COLOR_WHITE, precollected)
        self.assertIn(KARItemName.UNLOCK_COLOR_BLUE, precollected)


# A starting_* option with nothing to hand over is ignored rather than rejected: the category is either
# ungated (fully unlocked at connect) or belongs to a mode this seed disabled.
def _make_ignored_starter_test(opts: dict, attr: str, group: str) -> type:
    class _Ignored(KARTestBase):
        options = opts

        def test_nothing_precollected(self):
            self.assertIsNone(getattr(self.world, attr))
            self.assertEqual(self.precollected_in(item_name_groups[group]), [])

    return _Ignored


for _label, _opts, _attr, _group in (
    (
        "gate_off",
        {**CT_ONLY, "colors_gated": Toggle.option_false, "starting_kirby_color": "white"},
        "color_starter_choice",
        KARItemGroup.COLOR_UNLOCKS,
    ),
    (
        "mode_off",
        {**CT_ONLY, "air_ride_courses_gated": Toggle.option_true, "starting_air_ride_course": "nebula_belt"},
        "ar_course_starter_choice",
        KARItemGroup.AR_COURSE_UNLOCKS,
    ),
    (
        # Top Ride is not one of machines_gated's required modes, so the gate holds no keys here even
        # though the mode owning the named pick is enabled and the option is on.
        "gate_holds_no_keys",
        {**TR_ONLY, "machines_gated": Toggle.option_true, "starting_top_ride_machine": "steer_star"},
        "tr_machine_starter_choice",
        KARItemGroup.MACHINE_UNLOCKS,
    ),
):
    _register(_make_ignored_starter_test(_opts, _attr, _group), f"TestNamedStarterIgnoredWhen_{_label}")
