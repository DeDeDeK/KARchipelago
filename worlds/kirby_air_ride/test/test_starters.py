"""
Random-starter tests: which categories grant a precollected starter, which items are barred from the
pick, and how start_inventory suppresses it.

`world_setup` takes a fresh random seed each run, so one generation observes exactly one draw out of a
category of 8-24. "This run's pick was not X" would therefore catch a broken exclusion only as often as
X happened to come up - a 1-in-24 detection rate for the VS King Dedede case, and a test that passes or
fails on the seed rather than on the code. So nothing here asserts on a draw: `starter_candidates`
re-runs the picker with `world.random` recording instead of drawing and returns the exact candidate
list the world built, which turns every exclusion question into one deterministic set comparison.
"""

from Options import Toggle

from ..KARItems import (
    CHARGE_DEPENDENT_MACHINES,
    STADIUM_UNLOCK_ITEMS,
    KARItemGroup,
    KARItemName,
    item_name_groups,
)
from ..KAROptions import CityTrialGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase, recording_random

# Every attribute _determine_starter_items assigns. Saved and restored around a recorded re-run so
# the helper leaves the world exactly as it found it.
_STARTER_ATTRS = (
    "stadium_starter_choice",
    "machine_starter_choice",
    "tr_machine_starter_choice",
    "ar_course_starter_choice",
    "tr_course_starter_choice",
    "color_starter_choice",
)


def starter_candidates(world, attr: str) -> set[str]:
    """Every item the `attr` starter pick was willing to draw, captured exactly rather than sampled.

    Re-runs `_determine_starter_items` once with a recording `world.random`, so what comes back is the
    candidate list the world assembled - not a sample of its output. A category whose pick was skipped
    (the player preset one in start_inventory) yields the empty set.

    The recorder always returns the first entry it is offered, so the call that produced `attr` is the
    one whose first entry is the chosen value; the categories draw from disjoint item groups, so that
    identification is unambiguous and is asserted rather than assumed.
    """
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
    return {str(name) for name in matching[0]}


class TestStadiumStarter(KARTestBase):
    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true}

    def test_exactly_one_stadium_precollected(self):
        precollected = self.precollected_names()
        stadium_starters = [n for n in precollected if n in STADIUM_UNLOCK_ITEMS]
        self.assertEqual(len(stadium_starters), 1)

    def test_starter_not_in_pool(self):
        pool = self.itempool_names()
        for name in self.precollected_names():
            if name in STADIUM_UNLOCK_ITEMS:
                self.assertNotIn(name, pool, f"{name} precollected but also in pool")

    def test_the_chosen_stadium_is_the_precollected_one(self):
        # Closes the loop between the pick and the push: whichever stadium the draw landed on is the one
        # generate_early handed over. Holds for every seed, so it needs no assumption about the draw.
        self.assertIsNotNone(self.world.stadium_starter_choice)
        self.assertIn(str(self.world.stadium_starter_choice), self.precollected_names())


class TestStadiumStarterExcludesKingDedede(KARTestBase):
    """beat_king_dedede goal: the VS King Dedede stadium is the goal's own key, so handing it over as the
    free starter would hand over the goal. Every other stadium stays eligible."""

    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_true,
    }

    def test_eligible_stadiums_are_every_one_but_dedede(self):
        candidates = starter_candidates(self.world, "stadium_starter_choice")
        expected = {str(s) for s in STADIUM_UNLOCK_ITEMS} - {str(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE)}
        self.assertEqual(
            candidates,
            expected,
            "the beat_king_dedede starter pool must be every stadium except VS King Dedede itself",
        )


class TestStadiumStarterWithoutDededeGoal(KARTestBase):
    """Counter-case: with any other goal the VS King Dedede stadium is an ordinary starter candidate, so
    the exclusion above is goal-specific rather than a blanket ban."""

    options = {**CT_ONLY, "city_trial_stadiums_gated": Toggle.option_true}

    def test_all_24_stadiums_eligible(self):
        candidates = starter_candidates(self.world, "stadium_starter_choice")
        self.assertEqual(candidates, {str(s) for s in STADIUM_UNLOCK_ITEMS})


class TestStadiumStarterRespectsStartInventory(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_stadiums_gated": Toggle.option_true,
        "start_inventory": {KARItemName.UNLOCK_STADIUM_AIR_GLIDER: 1},
    }

    def test_no_random_pick_when_preset(self):
        # World skips its random pick when the player presets a stadium; the preset still lands in precollected.
        self.assertIsNone(self.world.stadium_starter_choice)
        self.assertIn(KARItemName.UNLOCK_STADIUM_AIR_GLIDER, self.precollected_names())


_TR_MACHINES = frozenset({KARItemName.UNLOCK_MACHINE_FREE_STAR, KARItemName.UNLOCK_MACHINE_STEER_STAR})
_TR_MACHINE_NAMES = frozenset(str(m) for m in _TR_MACHINES)


class TestMachineStarter(KARTestBase):
    options = {**ALL_MODES, "machines_gated": Toggle.option_true}

    def test_one_arct_and_one_tr_machine_precollected(self):
        # All modes + machines_gated yields two machine starters: one Air Ride / City Trial machine and one
        # Top Ride control machine (Free/Steer), since the mod hard-gates the Top Ride lobby on Free/Steer.
        precollected = self.precollected_names()
        machine_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.MACHINE_UNLOCKS]]
        self.assertEqual(len(machine_starters), 2)
        tr_starters = [n for n in machine_starters if n in _TR_MACHINES]
        arct_starters = [n for n in machine_starters if n not in _TR_MACHINES]
        self.assertEqual(len(tr_starters), 1)
        self.assertEqual(len(arct_starters), 1)

    def test_arct_eligible_set_excludes_tr_and_assembled_machines(self):
        # The AR/CT machine starter must never be a Top Ride control machine (unrideable in AR and CT)
        # nor one of the three legendaries, which are assembled from pieces rather than selected.
        candidates = starter_candidates(self.world, "machine_starter_choice")
        assembled = {
            str(KARItemName.UNLOCK_MACHINE_HYDRA),
            str(KARItemName.UNLOCK_MACHINE_DRAGOON),
            str(KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR),
        }
        expected = {str(m) for m in item_name_groups[KARItemGroup.MACHINE_UNLOCKS]} - _TR_MACHINE_NAMES - assembled
        self.assertEqual(candidates, expected)

    def test_tr_eligible_set_is_free_and_steer_only(self):
        candidates = starter_candidates(self.world, "tr_machine_starter_choice")
        self.assertEqual(candidates, _TR_MACHINE_NAMES)


class TestMachineStarterChargeGated(KARTestBase):
    # machines + base abilities both gated: the starter has to be a machine the player can steer before
    # Charge arrives, so Bulk, Slick and Turbo Star join Hydra in being held out of the pick.
    options = {**ALL_MODES, "machines_gated": Toggle.option_true, "base_abilities_gated": Toggle.option_true}

    def test_eligible_set_holds_out_every_charge_dependent_machine(self):
        # Set equality rather than disjointness: it pins both halves at once, and a "no overlap"
        # assertion alone would also pass on an empty candidate list.
        candidates = starter_candidates(self.world, "machine_starter_choice")
        assembled = {
            str(KARItemName.UNLOCK_MACHINE_HYDRA),
            str(KARItemName.UNLOCK_MACHINE_DRAGOON),
            str(KARItemName.UNLOCK_MACHINE_ARCHIPELAGO_STAR),
        }
        charge_dependent = {str(m) for m in CHARGE_DEPENDENT_MACHINES}
        expected = (
            {str(m) for m in item_name_groups[KARItemGroup.MACHINE_UNLOCKS]}
            - _TR_MACHINE_NAMES
            - assembled
            - charge_dependent
        )
        self.assertEqual(candidates, expected)
        self.assertFalse(candidates & charge_dependent)

    def test_charge_dependent_machines_still_in_pool(self):
        # Held out of the starter pick only - they stay normal progression items.
        pool = self.itempool_names()
        for machine in CHARGE_DEPENDENT_MACHINES:
            self.assertIn(machine, pool)


class TestARCourseStarter(KARTestBase):
    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true}

    def test_exactly_one_ar_course_precollected(self):
        precollected = self.precollected_names()
        ar_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.AR_COURSE_UNLOCKS]]
        self.assertEqual(len(ar_starters), 1)

    def test_every_ar_course_is_a_candidate(self):
        # No course is held back, secret ones included - unlike stadiums (VS King Dedede) and machines
        # (the assembled legendaries), Air Ride courses have no barred member.
        candidates = starter_candidates(self.world, "ar_course_starter_choice")
        self.assertEqual(candidates, {str(c) for c in item_name_groups[KARItemGroup.AR_COURSE_UNLOCKS]})


class TestTRCourseStarter(KARTestBase):
    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true}

    def test_exactly_one_tr_course_precollected(self):
        precollected = self.precollected_names()
        tr_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.TR_COURSE_UNLOCKS]]
        self.assertEqual(len(tr_starters), 1)

    def test_every_tr_course_is_a_candidate(self):
        candidates = starter_candidates(self.world, "tr_course_starter_choice")
        self.assertEqual(candidates, {str(c) for c in item_name_groups[KARItemGroup.TR_COURSE_UNLOCKS]})


class TestColorStarter(KARTestBase):
    # Colors are cross-mode: a random color starter is granted whenever colors_gated is on, regardless of
    # which mode is enabled. Pink is eligible like any other color.
    options = {**CT_ONLY, "colors_gated": Toggle.option_true}

    def test_exactly_one_color_precollected(self):
        precollected = self.precollected_names()
        color_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.COLOR_UNLOCKS]]
        self.assertEqual(len(color_starters), 1)

    def test_pink_is_a_candidate_like_any_other_color(self):
        # The deliberate cosmetic exception: the mod falls back to Pink when nothing is unlocked, so it
        # would be reasonable to bar it from the pick. The world does not, and this pins that choice.
        candidates = starter_candidates(self.world, "color_starter_choice")
        self.assertEqual(candidates, {str(c) for c in item_name_groups[KARItemGroup.COLOR_UNLOCKS]})
        self.assertIn(str(KARItemName.UNLOCK_COLOR_PINK), candidates)

    def test_starter_not_in_pool(self):
        pool = self.itempool_names()
        for name in self.precollected_names():
            if name in item_name_groups[KARItemGroup.COLOR_UNLOCKS]:
                self.assertNotIn(name, pool, f"{name} precollected but also in pool")


class TestAROnlyMachineStarter(KARTestBase):
    # AR on, CT off. A machine starter is picked (machines apply to AR), but no stadium starter (CT-only).
    # Covers both halves of "starter only when its owning mode is enabled".
    options = {**AR_ONLY, "machines_gated": Toggle.option_true, "city_trial_stadiums_gated": Toggle.option_true}

    def test_machine_starter_picked(self):
        precollected = self.precollected_names()
        machine_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.MACHINE_UNLOCKS]]
        self.assertEqual(len(machine_starters), 1)

    def test_no_stadium_starter_when_ct_disabled(self):
        precollected = self.precollected_names()
        stadium_starters = [n for n in precollected if n in STADIUM_UNLOCK_ITEMS]
        self.assertEqual(stadium_starters, [])


class TestTRMachineStarterWhenOnlyTREnabled(KARTestBase):
    # TR on, CT+AR off. The mod hard-gates the Top Ride lobby on Free/Steer, so a Top Ride machine starter
    # (one of Free/Steer) must be precollected even with no AR/CT machine - else a gated TR-only seed softlocks.
    options = {**TR_ONLY, "machines_gated": Toggle.option_true}

    def test_exactly_one_tr_machine_starter(self):
        precollected = self.precollected_names()
        machine_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.MACHINE_UNLOCKS]]
        self.assertEqual(len(machine_starters), 1)
        # Exact rather than "the one drawn happened to be a TR machine": Free and Steer are the whole
        # candidate list, so no seed can hand out anything else.
        self.assertEqual(starter_candidates(self.world, "tr_machine_starter_choice"), _TR_MACHINE_NAMES)
        self.assertIn(machine_starters[0], _TR_MACHINES)

    def test_no_arct_machine_starter(self):
        # No Air Ride / City Trial machine starter in a Top-Ride-only seed.
        self.assertIsNone(self.world.machine_starter_choice)


class TestPresetUnlockNotDuplicatedInPool(KARTestBase):
    # Unlock items are one-time, so presetting one in start_inventory must drop its pool copy. Copy abilities
    # grant no starter, so they exercise the general (non-starter) dedup path.
    options = {
        **CT_ONLY,
        "abilities_gated": Toggle.option_true,
        "start_inventory": {KARItemName.UNLOCK_ABILITY_FIRE: 1},
    }

    def test_preset_ability_precollected_and_absent_from_pool(self):
        self.assertIn(KARItemName.UNLOCK_ABILITY_FIRE, self.precollected_names())
        self.assertNotIn(KARItemName.UNLOCK_ABILITY_FIRE, self.itempool_names())


class TestPresetRewardNotDuplicatedInPool(KARTestBase):
    # Checklist rewards are one-time too, so a reward preset in start_inventory must be deduped out of the
    # pool. CT_REWARD_MUSIC_CITY is a plain in-scope CT reward, so presetting it exercises reward_pool.
    options = {
        **CT_ONLY,
        "start_inventory": {KARItemName.CT_REWARD_MUSIC_CITY: 1},
    }

    def test_preset_reward_precollected_and_absent_from_pool(self):
        self.assertIn(KARItemName.CT_REWARD_MUSIC_CITY, self.precollected_names())
        self.assertNotIn(KARItemName.CT_REWARD_MUSIC_CITY, self.itempool_names())


# Per starter category: presetting an item in start_inventory makes the world skip its random pick
# (starter_choice attr is None) and the preset lands in precollected. Parametric so a new category is one row.
_PRESET_RESPECT_CASES: list[tuple[str, dict, str, str]] = [
    # (label, options, world starter_choice attribute, preset item name)
    (
        "machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    ),
    (
        "tr_machine",
        {**TR_ONLY, "machines_gated": Toggle.option_true},
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
                f"world should skip random {label} pick when player presets one in start_inventory",
            )

        def test_preset_item_in_precollected(self):
            self.assertIn(preset, self.precollected_names())

    _StarterPresetRespect.__name__ = f"TestStarterRespectsStartInventory_{label}"
    _StarterPresetRespect.__qualname__ = _StarterPresetRespect.__name__
    return _StarterPresetRespect


for _label, _opts, _attr, _preset in _PRESET_RESPECT_CASES:
    globals()[f"TestStarterRespectsStartInventory_{_label}"] = _make_starter_preset_test(_label, _opts, _attr, _preset)
