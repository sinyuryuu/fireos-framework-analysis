# Phase 6A PI smoke evidence index

| Evidence ID | Source | File | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P6A-PI-001 | Device baseline | adb/phase6a/PHASE6A-PI-SMOKE-T02/before/ | PS7331 fingerprint, shell UID 2000, SELinux Enforcing | Test ran in expected shell domain | Confirmed |
| P6A-PI-002 | Binary | artifacts/phase6a/phase6a-pi-lock-smoke-T02/pi_lock_smoke | AArch64 static ELF, SHA-256 6795a3... | Exact benign test artifact was identified | Confirmed |
| P6A-PI-003 | Device execution | adb/phase6a/PHASE6A-PI-SMOKE-T02/run_exit_code_attempt01.txt | One execution, exit code 0, no stdout/stderr, no timeout | Ordinary uncontended PI lock/unlock completed | Confirmed |
| P6A-PI-004 | Cleanup | adb/phase6a/PHASE6A-PI-SMOKE-T02/remove_attempt01.txt and after/path_check_after_cleanup_attempt01.txt | Test file removed; ADB remains device | Temporary mutation was restored | Confirmed |
| P6A-PI-005 | Logcat | adb/phase6a/PHASE6A-PI-SMOKE-T02/after/logcat_after_run_attempt01.txt | No named futex/requeue marker | Logcat does not expose this syscall path | Strong evidence |
| P6A-PI-006 | Scope boundary | artifacts/phase6a/phase6a-pi-lock-smoke-T02/metadata.json | requeue_pi_used=false, race_created=false, root=false | No GhostLock exploitability claim is supported | Confirmed |
