import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/compare_phase5cw_upstream_followup.py"


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


FIXED = """
static int task_blocks_on_rt_mutex(struct rt_mutex *lock,
                                   struct rt_mutex_waiter *waiter,
                                   struct task_struct *task)
{
    waiter->task = task;
    return 0;
}
static void remove_waiter(struct rt_mutex *lock, struct rt_mutex_waiter *waiter)
{
    struct task_struct *waiter_task = waiter->task;
    if (!waiter_task)
        return;
    waiter_task->pi_blocked_on = NULL;
}
int rt_mutex_start_proxy_lock(struct rt_mutex *lock,
                              struct rt_mutex_waiter *waiter,
                              struct task_struct *task)
{
    ret = task_blocks_on_rt_mutex(lock, waiter, task);
    if (unlikely(ret < 0))
        remove_waiter(lock, waiter);
    return ret;
}
"""


class Phase5CWTests(unittest.TestCase):
    def test_separates_primary_and_followup_shapes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ps7331 = root / "ps7331.c"
            fixed = root / "fixed.c"
            output = root / "out"
            ps7331.write_text(SOURCE)
            fixed.write_text(FIXED)
            subprocess.run(
                [sys.executable, str(SCRIPT), "--ps7331", str(ps7331),
                 "--fixed-reference", str(fixed), "--output", str(output)],
                check=True,
            )
            result = json.loads((output / "summary.json").read_text())
            self.assertTrue(result["verdict"]["ps7331_matches_pre_primary_shape"])
            self.assertFalse(result["verdict"]["ps7331_has_followup_guard_shape"])
            self.assertFalse(result["verdict"]["runtime_identity_mismatch_observed"])


if __name__ == "__main__":
    unittest.main()
