from Options import Toggle

from ..KARItems import (
    STADIUM_UNLOCK_ITEMS,
    STADIUM_UNLOCK_TO_CHECKLIST_REWARD,
    KARItemName,
    item_name_groups,
)
from ..KAROptions import CityTrialGoal
from . import ALL_MODES, AR_ONLY, CT_ONLY, TR_ONLY, KARTestBase


class TestStadiumStarter(KARTestBase):
    options = {**CT_ONLY, "city_trial_progressive_stadiums": Toggle.option_true}

    def test_exactly_one_stadium_precollected(self):
        precollected = self.precollected_names()
        stadium_starters = [n for n in precollected if n in STADIUM_UNLOCK_ITEMS]
        self.assertEqual(len(stadium_starters), 1)

    def test_starter_not_a_checklist_overlap(self):
        for name in self.precollected_names():
            self.assertNotIn(
                name,
                STADIUM_UNLOCK_TO_CHECKLIST_REWARD,
                "Stadium starter should not double as a checklist reward unlock",
            )

    def test_starter_not_in_pool(self):
        pool = self.itempool_names()
        for name in self.precollected_names():
            if name in STADIUM_UNLOCK_ITEMS:
                self.assertNotIn(name, pool, f"{name} precollected but also in pool")


class TestStadiumStarterExcludesKingDedede(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_goal": CityTrialGoal.option_beat_king_dedede,
        "city_trial_progressive_stadiums": Toggle.option_true,
    }

    def test_starter_not_vs_king_dedede(self):
        self.assertNotIn(KARItemName.UNLOCK_STADIUM_VS_KING_DEDEDE, self.precollected_names())


class TestStadiumStarterRespectsStartInventory(KARTestBase):
    options = {
        **CT_ONLY,
        "city_trial_progressive_stadiums": Toggle.option_true,
        "start_inventory": {KARItemName.UNLOCK_STADIUM_AIR_GLIDER: 1},
    }

    def test_no_random_pick_when_preset(self):
        # The world should skip its random pick when the player presets a stadium.
        self.assertIsNone(self.world.stadium_starter_choice)
        # And the preset stadium should still end up in precollected (pushed by setUp).
        self.assertIn(KARItemName.UNLOCK_STADIUM_AIR_GLIDER, self.precollected_names())


# Dedede-as-stadium-starter rejection lives in test_validation.py.


class TestMachineStarter(KARTestBase):
    options = {**ALL_MODES, "machines_gated": Toggle.option_true}

    def test_exactly_one_machine_precollected(self):
        precollected = self.precollected_names()
        machine_starters = [n for n in precollected if n in item_name_groups["Machine Unlocks"]]
        self.assertEqual(len(machine_starters), 1)

    def test_starter_not_hydra_or_dragoon(self):
        precollected = self.precollected_names()
        self.assertNotIn(KARItemName.UNLOCK_MACHINE_HYDRA, precollected)
        self.assertNotIn(KARItemName.UNLOCK_MACHINE_DRAGOON, precollected)


class TestPatchStarter(KARTestBase):
    options = {**CT_ONLY, "patches_gated": Toggle.option_true}

    def test_exactly_one_patch_precollected(self):
        precollected = self.precollected_names()
        patch_starters = [n for n in precollected if n in item_name_groups["Patch Type Unlocks"]]
        self.assertEqual(len(patch_starters), 1)


class TestARCourseStarter(KARTestBase):
    options = {**AR_ONLY, "air_ride_courses_gated": Toggle.option_true}

    def test_exactly_one_ar_course_precollected(self):
        precollected = self.precollected_names()
        ar_starters = [n for n in precollected if n in item_name_groups["AR Course Unlocks"]]
        self.assertEqual(len(ar_starters), 1)


class TestTRCourseStarter(KARTestBase):
    options = {**TR_ONLY, "top_ride_courses_gated": Toggle.option_true}

    def test_exactly_one_tr_course_precollected(self):
        precollected = self.precollected_names()
        tr_starters = [n for n in precollected if n in item_name_groups["TR Course Unlocks"]]
        self.assertEqual(len(tr_starters), 1)


class TestAROnlyMachineAndPatchGating(KARTestBase):
    # AR on, CT off. machines apply to CT or AR (AR is on, so picked), patches apply
    # to CT only (CT is off, so skipped). Covers both halves of "starter only when its
    # owning mode is enabled" without claiming to test the no-mode-enabled case.
    options = {**AR_ONLY, "machines_gated": Toggle.option_true, "patches_gated": Toggle.option_true}

    def test_machine_starter_picked(self):
        precollected = self.precollected_names()
        machine_starters = [n for n in precollected if n in item_name_groups["Machine Unlocks"]]
        self.assertEqual(len(machine_starters), 1)

    def test_no_patch_starter_when_ct_disabled(self):
        precollected = self.precollected_names()
        patch_starters = [n for n in precollected if n in item_name_groups["Patch Type Unlocks"]]
        self.assertEqual(patch_starters, [])


class TestNoMachineStarterWhenOnlyTREnabled(KARTestBase):
    # TR on, CT+AR off. machines apply only to CT or AR, so the machine starter should
    # not be precollected. Patch-starter-skip is covered by TestAROnlyMachineAndPatchGating.
    options = {**TR_ONLY, "machines_gated": Toggle.option_true, "patches_gated": Toggle.option_true}

    def test_no_machine_starter(self):
        precollected = self.precollected_names()
        machine_starters = [n for n in precollected if n in item_name_groups["Machine Unlocks"]]
        self.assertEqual(machine_starters, [])


# Each starter category: when the player presets an item from that category in start_inventory,
# the world should skip its random pick (starter_choice attr is None) and the preset item should
# end up in precollected (pushed by KARTestBase.setUp). Generated as a parametric block so adding
# a new starter category requires one row, not a copy-pasted class.
_PRESET_RESPECT_CASES: list[tuple[str, dict, str, str]] = [
    # (label, options, world starter_choice attribute, preset item name)
    (
        "machine",
        {**ALL_MODES, "machines_gated": Toggle.option_true},
        "machine_starter_choice",
        KARItemName.UNLOCK_MACHINE_WAGON_STAR,
    ),
    (
        "patch",
        {**CT_ONLY, "patches_gated": Toggle.option_true},
        "patch_starter_choice",
        KARItemName.UNLOCK_PATCH_HP,
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
