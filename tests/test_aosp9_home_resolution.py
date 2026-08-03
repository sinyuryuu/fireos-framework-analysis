#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "scripts"))

from model_aosp9_home_resolution import (  # noqa: E402
    Candidate,
    PreferredRecord,
    choose_best_activity,
    fire_vs_priority_zero,
)


class Aosp9HomeResolutionTests(unittest.TestCase):
    def test_fire_priority_wins_before_ordinary_preferred(self):
        decision = fire_vs_priority_zero()
        self.assertEqual(decision.selected, "com.amazon.firelauncher/.Launcher")
        self.assertEqual(decision.branch, "top-ranking-fields-differ")
        self.assertFalse(decision.preferred_considered)

    def test_ordinary_preferred_is_used_for_a_real_tie(self):
        fire = Candidate("com.amazon.firelauncher/.Launcher", "com.amazon.firelauncher", 0)
        p0 = Candidate("org.example/.Home", "org.example", 0)
        record = PreferredRecord(
            component=p0.component,
            match=0x100000,
            always=True,
            set_components=(fire.component, p0.component),
        )
        decision = choose_best_activity([fire, p0], ordinary_preferred=record)
        self.assertEqual(decision.selected, p0.component)
        self.assertEqual(decision.branch, "ordinary-preferred")
        self.assertTrue(decision.preferred_considered)

    def test_match_mismatch_rejects_preferred(self):
        a = Candidate("a/.Home", "a", 0, match=0x108000)
        b = Candidate("b/.Home", "b", 0, match=0x108000)
        record = PreferredRecord(b.component, match=0x200000, set_components=(a.component, b.component))
        decision = choose_best_activity([a, b], ordinary_preferred=record)
        self.assertEqual(decision.branch, "resolver-or-chooser")
        self.assertFalse(decision.preferred_accepted)

    def test_result_set_change_rejects_non_superset_record(self):
        a = Candidate("a/.Home", "a", 0)
        b = Candidate("b/.Home", "b", 0)
        c = Candidate("c/.Home", "c", 0)
        record = PreferredRecord(b.component, match=0x100000, set_components=(a.component, b.component))
        decision = choose_best_activity([a, b, c], ordinary_preferred=record)
        self.assertEqual(decision.branch, "resolver-or-chooser")

    def test_persistent_preferred_is_checked_before_ordinary(self):
        a = Candidate("a/.Home", "a", 0)
        b = Candidate("b/.Home", "b", 0)
        persistent = PreferredRecord(b.component, match=0x100000, set_components=(a.component, b.component), persistent=True)
        ordinary = PreferredRecord(a.component, match=0x100000, set_components=(a.component, b.component))
        decision = choose_best_activity([a, b], ordinary, persistent)
        self.assertEqual(decision.selected, b.component)
        self.assertEqual(decision.branch, "persistent-preferred")

    def test_priority_precedes_match_and_system_tiebreak(self):
        a = Candidate("a/.Home", "a", 1, match=0x100000, system=False)
        b = Candidate("b/.Home", "b", 0, match=0x108000, system=True)
        decision = choose_best_activity([a, b])
        self.assertEqual(decision.selected, a.component)


if __name__ == "__main__":
    unittest.main()
