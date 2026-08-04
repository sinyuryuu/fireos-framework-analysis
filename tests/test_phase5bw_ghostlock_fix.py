import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/compare_phase5bw_ghostlock_fix.py"


PRE_FIX = """
static void remove_waiter(struct rt_mutex *lock, struct rt_mutex_waiter *waiter)
{
    raw_spin_lock_irqsave(&current->pi_lock, flags);
    rt_mutex_dequeue(lock, waiter);
    current->pi_blocked_on = NULL;
    raw_spin_unlock_irqrestore(&current->pi_lock, flags);
    rt_mutex_adjust_prio_chain(owner, 0, lock, next_lock, NULL, current);
}
int rt_mutex_start_proxy_lock(struct rt_mutex *lock, struct rt_mutex_waiter *waiter,
                              struct task_struct *task)
{
    if (unlikely(ret))
        remove_waiter(lock, waiter);
}
"""

FIXED = """
static void remove_waiter(struct rt_mutex *lock, struct rt_mutex_waiter *waiter)
{
    struct task_struct *waiter_task = waiter->task;
    scoped_guard(raw_spinlock, &waiter_task->pi_lock) {
        rt_mutex_dequeue(lock, waiter);
        waiter_task->pi_blocked_on = NULL;
    }
    rt_mutex_adjust_prio_chain(owner, 0, lock, next_lock, NULL, waiter_task);
}
int rt_mutex_start_proxy_lock(struct rt_mutex *lock, struct rt_mutex_waiter *waiter,
                              struct task_struct *task)
{
    if (unlikely(ret))
        remove_waiter(lock, waiter);
}
"""


class GhostLockFixComparisonTests(unittest.TestCase):
    def test_classifies_target_as_pre_fix_and_reference_as_fixed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "target.c"
            fixed = root / "fixed.c"
            output = root / "out"
            target.write_text(PRE_FIX)
            fixed.write_text(FIXED)
            subprocess.run(
                [sys.executable, str(SCRIPT), "--target", str(target),
                 "--fixed-reference", str(fixed), "--output", str(output)],
                check=True,
            )
            result = json.loads((output / "comparison.json").read_text())
            self.assertEqual(result["target"]["classification"],
                             "PRE_FIX_CURRENT_TASK_CLEANUP")
            self.assertEqual(result["fixed_reference"]["classification"],
                             "FIXED_WAITER_TASK_CLEANUP")
            self.assertEqual(result["verdict"],
                             "PS7331_SOURCE_MATCHES_PRE_FIX_SEMANTICS")


if __name__ == "__main__":
    unittest.main()
