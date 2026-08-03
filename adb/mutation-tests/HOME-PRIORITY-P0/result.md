# HOME-PRIORITY-P0

- Package: `org.fireosresearch.home.p0`
- Declared priority: `0`
- Install, explicit start, HOME intent, Home key, preferred write, lock/wake, and reboot commands were captured before the runner was interrupted.
- The first post-reboot resolver probe ran before the PackageManager service was available; its raw error is preserved.
- Recovery: `adb/mutation-tests/HOME-PRIORITY-P0/recovery-20260803T062741Z/restore.sh`-equivalent restore sequence completed with exit `0`.
- Recovery after-state: resolver remained `com.amazon.firelauncher/.Launcher`; `pm path org.fireosresearch.home.p0` returned no path.
- Final classification: `RESTORED_FIRE`.
- Confidence: `Strong evidence` for the observed candidate/resolver result; `Hypothesis` for the incomplete full runner sequence.
