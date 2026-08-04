import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/audit_phase5cc_ps7331_identity_invariant.py"


class Phase5CCTests(unittest.TestCase):
    def test_records_separate_task_roles_without_claiming_runtime_race(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            futex = root / "futex.c"
            rtmutex = root / "rtmutex.c"
            output = root / "out"
            futex.write_text(
                """
/** struct futex_q - one per waiting task */
struct futex_q {
    struct task_struct *task;
    struct rt_mutex_waiter *rt_waiter;
};
static inline void queue_me(struct futex_q *q) {
    q->task = current;
}
static void futex_wait_queue_me(struct futex_q *q) {
    queue_me(q);
    schedule();
}
static int futex_wait_requeue_pi(void) {
    struct rt_mutex_waiter rt_waiter;
    struct futex_q q = futex_q_init;
    rt_waiter.task = NULL;
    q.rt_waiter = &rt_waiter;
    futex_wait_queue_me(&q);
    return 0;
}
static int futex_requeue(void) {
    ret = rt_mutex_start_proxy_lock(&pi->lock, this->rt_waiter,
                                    this->task);
    return ret;
}
"""
            )
            rtmutex.write_text(
                """
static int task_blocks_on_rt_mutex(struct rt_mutex *lock,
                                   struct rt_mutex_waiter *waiter,
                                   struct task_struct *task) {
    if (owner == task)
        return -EDEADLK;
    waiter->task = task;
    return 0;
}
int rt_mutex_start_proxy_lock(struct rt_mutex *lock,
                              struct rt_mutex_waiter *waiter,
                              struct task_struct *task) {
    ret = task_blocks_on_rt_mutex(lock, waiter, task);
    if (unlikely(ret))
        remove_waiter(lock, waiter);
    return ret;
}
static void remove_waiter(struct rt_mutex *lock,
                          struct rt_mutex_waiter *waiter) {
    raw_spin_lock(&current->pi_lock);
    current->pi_blocked_on = NULL;
    raw_spin_unlock(&current->pi_lock);
}
"""
            )
            subprocess.run([
                sys.executable, str(SCRIPT), "--futex", str(futex),
                "--rtmutex", str(rtmutex), "--output", str(output)
            ], check=True)
            result = json.loads((output / "identity-audit.json").read_text())
            model = result["identity_model"]
            self.assertTrue(model["queue_task_bound_to_waiting_current_at_enqueue"])
            self.assertTrue(model["proxy_waiter_is_separate_object"])
            self.assertTrue(model["requeue_passes_stored_task_to_proxy_api"])
            self.assertTrue(model["cleanup_reads_current_pi_lock"])
            self.assertTrue(model["identity_mismatch_allowed_by_source_interface"])
            self.assertFalse(model["identity_mismatch_observed_runtime"])
            self.assertFalse(model["race_window_proven"])
            self.assertFalse(model["root_or_privilege_gain_proven"])


if __name__ == "__main__":
    unittest.main()
