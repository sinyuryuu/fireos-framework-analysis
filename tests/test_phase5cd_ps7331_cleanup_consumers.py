import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/audit_phase5cd_ps7331_cleanup_consumers.py"


class Phase5CDTests(unittest.TestCase):
    def test_maps_cleanup_and_later_consumers_without_runtime_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "rtmutex.c"
            output = root / "out"
            source.write_text(
                """
static void
rt_mutex_dequeue(struct rt_mutex *lock,
                 struct rt_mutex_waiter *waiter) {
    rb_erase(&waiter->tree_entry, &lock->waiters);
    RB_CLEAR_NODE(&waiter->tree_entry);
}
static void
rt_mutex_dequeue_pi(struct task_struct *task,
                     struct rt_mutex_waiter *waiter) {
    rb_erase(&waiter->pi_tree_entry, &task->pi_waiters);
    RB_CLEAR_NODE(&waiter->pi_tree_entry);
}
static inline struct rt_mutex *task_blocked_on_lock(struct task_struct *p) {
    return p->pi_blocked_on ? p->pi_blocked_on->lock : NULL;
}
static int rt_mutex_adjust_prio_chain(struct task_struct *task) {
    waiter = task->pi_blocked_on;
    next_lock = waiter->lock;
    return 0;
}
static int try_to_take_rt_mutex(struct rt_mutex *lock,
                                struct task_struct *task) {
    task->pi_blocked_on = NULL;
    return 1;
}
static int task_blocks_on_rt_mutex(struct rt_mutex *lock,
                                   struct rt_mutex_waiter *waiter,
                                   struct task_struct *task) {
    if (owner == task)
        return -EDEADLK;
    waiter->task = task;
    task->pi_blocked_on = waiter;
    return 0;
}
static void mark_wakeup_next_waiter(struct wake_q_head *wake_q,
                                    struct rt_mutex *lock) {
    wake_q_add(wake_q, waiter->task);
}
static void remove_waiter(struct rt_mutex *lock,
                          struct rt_mutex_waiter *waiter) {
    rt_mutex_dequeue(lock, waiter);
    current->pi_blocked_on = NULL;
    rt_mutex_dequeue_pi(owner, waiter);
}
void rt_mutex_adjust_pi(struct task_struct *task) {
    waiter = task->pi_blocked_on;
}
int rt_mutex_start_proxy_lock(struct rt_mutex *lock,
                              struct rt_mutex_waiter *waiter,
                              struct task_struct *task) {
    ret = task_blocks_on_rt_mutex(lock, waiter, task);
    if (unlikely(ret))
        remove_waiter(lock, waiter);
    return ret;
}
"""
            )
            subprocess.run([
                sys.executable, str(SCRIPT), "--rtmutex", str(source),
                "--output", str(output)
            ], check=True)
            result = json.loads((output / "cleanup-consumer-audit.json").read_text())
            effects = result["cleanup_effect_model"]
            self.assertTrue(effects["writes_current_pi_blocked_on"])
            self.assertFalse(effects["writes_waiter_task"])
            self.assertTrue(effects["dequeues_lock_tree_via_helper"])
            self.assertTrue(effects["dequeues_owner_pi_tree_via_helper"])
            self.assertFalse(effects["persistent_target_state_violation_proven"])
            consumers = result["consumer_model"]["potential_second_consumers"]
            self.assertIn("task_blocked_on_lock", consumers)
            self.assertIn("rt_mutex_adjust_prio_chain", consumers)
            self.assertIn("rt_mutex_adjust_pi", consumers)
            self.assertFalse(result["consumer_model"]["runtime_second_consumer_observed"])


if __name__ == "__main__":
    unittest.main()
