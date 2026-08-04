import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/analyze_phase5by_ghostlock_fix_chain.py"


SOURCE = """
static int task_blocks_on_rt_mutex(struct rt_mutex *lock,
                                   struct rt_mutex_waiter *waiter,
                                   struct task_struct *task)
{
    if (owner == task)
        return -EDEADLK;
    waiter->task = task;
    return 0;
}
static void remove_waiter(struct rt_mutex *lock, struct rt_mutex_waiter *waiter)
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


class FixChainTests(unittest.TestCase):
    def test_detects_pre_fix_and_follow_up_guard_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "rtmutex.c"
            output = root / "out"
            source.write_text(SOURCE)
            subprocess.run(
                [sys.executable, str(SCRIPT), "--source", str(source),
                 "--output", str(output)], check=True
            )
            result = json.loads((output / "fix-chain.json").read_text())
            self.assertTrue(result["primary_fix_shape"])
            self.assertTrue(result["follow_up_guard_review_needed"])
            self.assertEqual(
                result["classification"],
                "PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW",
            )
            self.assertFalse(result["runtime_exploitability_proven"])


if __name__ == "__main__":
    unittest.main()
