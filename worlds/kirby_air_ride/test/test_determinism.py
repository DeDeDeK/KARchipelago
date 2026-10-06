"""One seed must generate the same multiworld in every process. String hashing is salted per process
(PYTHONHASHSEED), so iterating a set of names anywhere generation order matters makes the same seed and
YAML fill differently from run to run. That can only be seen across processes, so each configuration is
generated in subprocesses under different hash seeds and their fingerprints compared.

A correct world never fails this. A regression on a small set could slip past two hash seeds that happen
to agree, but every set this has caught so far holds dozens of names."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from NetUtils import encode

from worlds.AutoWorld import call_all

from ..KAROptions import AirRideGoal, APPatchPlacement, ArchipelagoGoal, NonProgressionCheckboxes, TopRideGoal
from . import KARTestBase

_REPO_ROOT = Path(__file__).resolve().parents[3]

_HASH_SEEDS = ("1", "2")

_ALL_GATES: dict = dict.fromkeys(
    (
        "city_trial_stadiums_gated",
        "city_trial_events_gated",
        "city_trial_patches_gated",
        "city_trial_items_gated",
        "city_trial_boxes_gated",
        "air_ride_courses_gated",
        "top_ride_courses_gated",
        "top_ride_items_gated",
        "abilities_gated",
        "base_abilities_gated",
        "machines_gated",
        "colors_gated",
    ),
    True,
)

_ALL_MODES_ALL_GATES: dict = {
    **_ALL_GATES,
    "air_ride_goal": AirRideGoal.option_100_checklist_blocks,
    "top_ride_goal": TopRideGoal.option_n_checklist_blocks,
    "archipelago_goal": ArchipelagoGoal.option_n_checklist_blocks,
    "archipelago_checklist_amount": 30,
}

# Between them these build all three location sets (default, excluded, removed) in every mode, plus
# both AP Patch placements.
_CONFIGS: dict[str, dict] = {
    "removed": {
        **_ALL_MODES_ALL_GATES,
        "non_progression_checkboxes": NonProgressionCheckboxes.option_removed,
    },
    "excluded": {
        **_ALL_MODES_ALL_GATES,
        "non_progression_checkboxes": NonProgressionCheckboxes.option_excluded,
        "ap_patch_placement": APPatchPlacement.option_excluded,
    },
}


def fingerprint(config: str) -> str:
    """Generate `config` through fill and serialize everything about the result whose order could leak."""
    from Fill import distribute_items_restrictive

    class _Probe(KARTestBase):
        options = _CONFIGS[config]

    probe = _Probe()
    probe.world_setup(seed=1)
    multiworld = probe.multiworld
    distribute_items_restrictive(multiworld)
    call_all(multiworld, "post_fill")

    return json.dumps(
        {
            "locations": [
                [
                    location.name,
                    location.parent_region.name if location.parent_region else None,
                    int(location.progress_type),
                    location.item.name if location.item else None,
                ]
                for location in multiworld.get_locations()
            ],
            "precollected": [item.name for item in multiworld.precollected_items[probe.player]],
            # As the server sends it, sets and all
            "slot_data": encode(probe.world.fill_slot_data()),
        }
    )


class TestHashSeedIndependence(unittest.TestCase):
    def test_same_seed_generates_identically_under_any_hash_seed(self):
        env = {**os.environ, "AP_TEST_WORLDS": "kirby_air_ride"}
        # unittest first: AP_TEST_WORLDS only scopes world loading under a test runner.
        script = (
            "import sys, unittest\n"
            "from worlds.kirby_air_ride.test.test_determinism import fingerprint\n"
            "print(fingerprint(sys.argv[1]))\n"
        )
        runs = {
            (config, hash_seed): subprocess.Popen(
                [sys.executable, "-c", script, config],
                cwd=_REPO_ROOT,
                env={**env, "PYTHONHASHSEED": hash_seed},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for config in _CONFIGS
            for hash_seed in _HASH_SEEDS
        }
        outputs: dict[tuple[str, str], dict] = {}
        for key, run in runs.items():
            stdout, stderr = run.communicate(timeout=300)
            self.assertEqual(run.returncode, 0, f"{key} failed to generate:\n{stderr}")
            outputs[key] = json.loads(stdout.splitlines()[-1])

        for config in _CONFIGS:
            first = outputs[config, _HASH_SEEDS[0]]
            for hash_seed in _HASH_SEEDS[1:]:
                other = outputs[config, hash_seed]
                for part in first:
                    with self.subTest(config=config, hash_seed=hash_seed, part=part):
                        self.assertEqual(first[part], other[part])
