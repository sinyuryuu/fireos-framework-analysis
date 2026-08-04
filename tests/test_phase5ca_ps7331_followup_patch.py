import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/analyze_phase5ca_ps7331_followup_patch.py"


RTMUTEX = """
static int task_blocks_on_rt_mutex(struct rt_mutex *lock,
                                   struct rt_mutex_waiter *waiter,
                                   struct task_struct *task)
{
    if (owner == task)
        return -EDEADLK;
    waiter->task = task;
    return 0;
}
static void remove_waiter(struct rt_mutex *lock,
                          struct rt_mutex_waiter *waiter)
{
    current->pi_blocked_on = NULL;
}
int rt_mutex_start_proxy_lock(struct rt_mutex *lock,
                              struct rt_mutex_waiter *waiter,
                              struct task_struct *task)
{
    ret = task_blocks_on_rt_mutex(lock, waiter, task);
    if (unlikely(ret))
        remove_waiter(lock, waiter);
    return ret;
}
"""


class Phase5CATests(unittest.TestCase):
    def test_maps_old_source_to_both_required_review_points(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rtmutex = root / "rtmutex.c"
            futex = root / "futex.c"
            output = root / "out"
            rtmutex.write_text(RTMUTEX)
            futex.write_text("case FUTEX_CMP_REQUEUE_PI:\n  rt_mutex_start_proxy_lock(lock, waiter, task);\n")
            subprocess.run([
                sys.executable, str(SCRIPT), "--rtmutex", str(rtmutex),
                "--futex", str(futex), "--output", str(output)
            ], check=True)
            result = json.loads((output / "followup-mapping.json").read_text())
            self.assertFalse(result["primary_fix_present"])
            self.assertFalse(result["followup_guard_present"])
            self.assertEqual(
                result["classification"],
                "PS7331_REQUIRES_PRIMARY_FIX_AND_FOLLOWUP_GUARD_REVIEW",
            )
            self.assertFalse(result["runtime_exploitability_proven"])


if __name__ == "__main__":
    unittest.main()
