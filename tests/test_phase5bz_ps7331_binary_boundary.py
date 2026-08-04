import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/analyze_phase5bz_ps7331_binary_boundary.py"


class Phase5BZTests(unittest.TestCase):
    def test_preserves_binary_boundary_without_inventing_followup_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            patterns = root / "patterns.csv"
            patterns.write_text(
                "symbol,pattern,instruction,interpretation\n"
                "remove_waiter,current_task_source,mrs,old\n"
                "remove_waiter,current_task_blocked_on_clear,str,old\n"
                "rt_mutex_start_proxy_lock,proxy_error_calls_remove_waiter,bl,proxy\n"
            )
            summary = root / "summary.json"
            summary.write_text(json.dumps({
                "address_output": "intentionally omitted",
                "symbols_present": ["remove_waiter", "rt_mutex_start_proxy_lock"],
            }))
            source = root / "source.json"
            source.write_text(json.dumps({
                "primary_fix_present": False,
                "primary_fix_shape": True,
                "follow_up_guard_review_needed": True,
                "classification": "PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW",
            }))
            metadata = root / "metadata.md"
            metadata.write_text("Raw disassembly is intentionally omitted.\n")
            image = root / "Image"
            image.write_bytes(b"test image")
            config = root / "config"
            config.write_text(
                "CONFIG_FUTEX=y\n"
                "CONFIG_RT_MUTEXES=y\n"
                "# CONFIG_RANDOMIZE_KSTACK_OFFSET is not set\n"
            )
            output = root / "out"
            subprocess.run([
                sys.executable, str(SCRIPT),
                "--patterns", str(patterns),
                "--summary", str(summary),
                "--source-result", str(source),
                "--parser-metadata", str(metadata),
                "--kernel-image", str(image),
                "--kernel-config", str(config),
                "--output", str(output),
            ], check=True)
            result = json.loads((output / "analysis.json").read_text())
            self.assertTrue(result["primary_binary_markers_complete"])
            self.assertEqual(
                result["followup_guard_binary_status"],
                "NOT_OBSERVABLE_FROM_SAVED_SANITIZED_OUTPUT",
            )
            self.assertFalse(result["runtime_exploitability_proven"])
            with (output / "config-observations.csv").open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            statuses = {row["key"]: row["status"] for row in rows}
            self.assertEqual(statuses["CONFIG_FUTEX"], "present")
            self.assertEqual(statuses["CONFIG_RANDOMIZE_KSTACK_OFFSET"], "explicit_not_set")


if __name__ == "__main__":
    unittest.main()
