from Options import Toggle

from ..KARItems import (
    CHARGE_DEPENDENT_MACHINES,
    STADIUM_UNLOCK_ITEMS,
    KARItemGroup,
    KARItemName,
    item_name_groups,
)
from ..KAROptions import CityTrialGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase


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


class TestStadiumStarterExcludesKingDedede(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_stadiums_gated": Toggle.option_true,
    }

    def test_starter_not_vs_king_dedede(self):
        self.assertNotIn(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE, self.precollected_names())


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

    def test_arct_starter_not_free_or_steer(self):
        # The AR/CT machine starter must never be a Top Ride control machine (they don't spawn in
        # City Trial and can't be ridden in Air Ride).
        self.assertNotIn(self.world.machine_starter_choice, _TR_MACHINES)

    def test_starter_not_hydra_or_dragoon(self):
        precollected = self.precollected_names()
        self.assertNotIn(KARItemName.UNLOCK_MACHINE_HYDRA, precollected)
        self.assertNotIn(KARItemName.UNLOCK_MACHINE_DRAGOON, precollected)


class TestMachineStarterChargeGated(KARTestBase):
    # machines + base abilities both gated: the starter has to be a machine the player can steer before
    # Charge arrives, so Slick and Turbo Star join Hydra in being held out of the pick.
    options = {**ALL_MODES, "machines_gated": Toggle.option_true, "base_abilities_gated": Toggle.option_true}

    def test_starter_is_steerable_without_charge(self):
        self.assertNotIn(self.world.machine_starter_choice, CHARGE_DEPENDENT_MACHINES)

    def test_no_charge_dependent_machine_precollected(self):
        precollected = self.precollected_names()
        for machine in CHARGE_DEPENDENT_MACHINES:
            self.assertNotIn(machine, precollected)

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


class TestTRCourseStarter(KARTestBase):
    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true}

    def test_exactly_one_tr_course_precollected(self):
        precollected = self.precollected_names()
        tr_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.TR_COURSE_UNLOCKS]]
        self.assertEqual(len(tr_starters), 1)


class TestColorStarter(KARTestBase):
    # Colors are cross-mode: a random color starter is granted whenever colors_gated is on, regardless of
    # which mode is enabled. Pink is eligible like any other color.
    options = {**CT_ONLY, "colors_gated": Toggle.option_true}

    def test_exactly_one_color_precollected(self):
        precollected = self.precollected_names()
        color_starters = [n for n in precollected if n in item_name_groups[KARItemGroup.COLOR_UNLOCKS]]
        self.assertEqual(len(color_starters), 1)

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
    # Checklist rewards are one-time too: a reward preset in start_inventory must be deduped out of the pool.
    # CT_REWARD_MUSIC_CITY is a plain in-scope CT reward (shuffled into the pool under the default
    # Shuffle Checklist Rewards), so presetting it exercises the reward_pool dedup.
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
