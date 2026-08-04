import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/model_phase5cg_ps7331_cleanup_semantics.py"


class Phase5CGTests(unittest.TestCase):
    def test_models_ret_and_identity_without_runtime_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            futex = root / "futex.c"
            rtmutex = root / "rtmutex.c"
            output = root / "out"
            futex.write_text(
                """
static int futex_requeue(void) {
    if (ret == 1) { wake(); }
    else if (ret) { fail(); }
    return 0;
}
"""
            )
            rtmutex.write_text(
                """
static int task_blocks_on_rt_mutex(void) {
    if (owner == task)
        return -EDEADLK;
    waiter->task = task;
    return 0;
}
static void remove_waiter(void) {
    current->pi_blocked_on = NULL;
}
int rt_mutex_start_proxy_lock(void) {
    if (ret && !rt_mutex_owner(lock))
        ret = 0;
    if (unlikely(ret))
        remove_waiter(lock, waiter);
    return ret;
}
"""
            )
            subprocess.run([
                sys.executable, str(SCRIPT), "--futex", str(futex),
                "--rtmutex", str(rtmutex), "--output", str(output)
            ], check=True)
            result = json.loads((output / "cleanup-semantics.json").read_text())
            self.assertTrue(result["source_evidence_complete"])
            verdict = result["verdict"]
            self.assertTrue(verdict["early_return_precedes_waiter_assignment"])
            self.assertTrue(verdict["broad_nonzero_cleanup_guard_present"])
            self.assertTrue(verdict["cleanup_targets_current"])
            self.assertTrue(verdict["abstract_identity_mismatch_can_leave_target_state_conditionally"])
            self.assertFalse(verdict["runtime_identity_mismatch_observed"])
            self.assertFalse(verdict["root_or_privilege_gain_proven"])
            cases = {row["case"]: row for row in result["decision_rows"]}
            self.assertTrue(cases["early_deadlock_owner_present"]["wrapper_cleanup_called"])
            self.assertTrue(cases["early_deadlock_owner_present"]["followup_null_waiter_guard_relevant"])
            self.assertTrue(cases["identity_different_task_target_state_present"]["conditional_target_residue"])


if __name__ == "__main__":
    unittest.main()
