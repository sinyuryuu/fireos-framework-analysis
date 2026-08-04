import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/scripts/audit_phase5cb_ps7331_futex_entry.py"


class Phase5CBTests(unittest.TestCase):
    def test_detects_entry_path_without_claiming_runtime_policy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            futex = root / "futex.c"
            rtmutex = root / "rtmutex.c"
            config = root / "config"
            output = root / "out"
            futex.write_text(
                """
long do_futex(u32 __user *uaddr, int op) {
    if (!futex_cmpxchg_enabled) return -ENOSYS;
    case FUTEX_CMP_REQUEUE_PI:
        return futex_requeue(uaddr, flags, uaddr2, val, val2, &val3, 1);
}
static int futex_requeue(u32 __user *uaddr1) {
    ret = rt_mutex_start_proxy_lock(&pi->lock, waiter, task);
}
SYSCALL_DEFINE6(futex, u32 __user *, uaddr, int, op, u32, val,
                struct timespec __user *, utime, u32 __user *, uaddr2,
                u32, val3) {
    return do_futex(uaddr, op);
}
"""
            )
            rtmutex.write_text("int rt_mutex_start_proxy_lock(struct rt_mutex *lock) { return 0; }\n")
            config.write_text("CONFIG_FUTEX=y\nCONFIG_RT_MUTEXES=y\nCONFIG_SECURITY_SELINUX=y\n")
            subprocess.run([
                sys.executable, str(SCRIPT), "--futex", str(futex),
                "--rtmutex", str(rtmutex), "--config", str(config),
                "--output", str(output)
            ], check=True)
            result = json.loads((output / "entry-audit.json").read_text())
            self.assertEqual(result["source_reachability_status"], "SYSCALL_TO_PI_REQUEUE_PROXY_PATH_PRESENT")
            self.assertEqual(result["direct_credential_gate"]["status"], "not_observed_in_scoped_functions")
            self.assertEqual(result["userspace_policy_status"], "UNRESOLVED_FROM_KERNEL_SOURCE_ONLY")
            self.assertFalse(result["runtime_exploitability_proven"])


if __name__ == "__main__":
    unittest.main()
