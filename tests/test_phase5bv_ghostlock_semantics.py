import unittest

from tools.scripts.model_phase5bv_ghostlock_semantics import (
    Task,
    fixed_remove_waiter,
    pre_fix_remove_waiter,
    run_model,
)


class GhostLockSemanticModelTest(unittest.TestCase):
    def test_proxy_waiter_pre_fix_clears_wrong_task(self):
        current = Task("current", "current-lock")
        waiter = Task("proxy-waiter", "proxy-lock")

        pre_fix_remove_waiter(current, waiter)

        self.assertIsNone(current.pi_blocked_on)
        self.assertEqual(waiter.pi_blocked_on, "proxy-lock")

    def test_fixed_reference_clears_waiter_task(self):
        current = Task("current", "current-lock")
        waiter = Task("proxy-waiter", "proxy-lock")

        fixed_remove_waiter(current, waiter)

        self.assertEqual(current.pi_blocked_on, "current-lock")
        self.assertIsNone(waiter.pi_blocked_on)

    def test_non_proxy_same_task_does_not_show_mismatch(self):
        task = Task("same-task", "same-lock")

        pre_fix_remove_waiter(task, task)

        self.assertIsNone(task.pi_blocked_on)

    def test_model_verdict_is_bounded(self):
        result = run_model()

        self.assertTrue(result["verdict"]["semantic_mismatch_reproduced"])
        self.assertTrue(result["verdict"]["fixed_cleanup_clears_waiter_task"])
        self.assertFalse(result["verdict"]["live_kernel_exploitability_proven"])
        self.assertFalse(result["verdict"]["root_or_privilege_gain_proven"])


if __name__ == "__main__":
    unittest.main()
