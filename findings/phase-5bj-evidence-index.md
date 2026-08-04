# Phase 5BJ evidence index

| Evidence ID | File / source | Observation | Confidence |
|---|---|---|---|
| `P5BJ-UPSTREAM-001` | [Linux stable patch](https://www.spinics.net/lists/stable/msg940814.html) | Fix changes `remove_waiter()` from `current` to `waiter->task` for proxy-lock rollback | Confirmed, upstream scope |
| `P5BJ-NVD-001` | [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499) | CVE description matches dangling `pi_blocked_on` / wrong-task cleanup model | Confirmed, advisory scope |
| `P5BJ-SOURCE-001` | `artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/comparison.csv` | PS7330 source-family classified pre-fix | Confirmed, source scope |
| `P5BJ-SOURCE-002` | `artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/comparison.csv` | PS7331 build-selected source classified pre-fix | Confirmed, source scope |
| `P5BJ-SOURCE-003` | `artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/comparison.csv` | Fixed reference classified waiter-task cleanup | Confirmed, reference scope |
| `P5BJ-DEVICE-001` | `adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/props.stdout.txt` | Device remains PS7330.4104N / KFTRWI / trona / MT8183; verified boot green and locked | Confirmed |
| `P5BJ-DEVICE-002` | `adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/identity.stdout.txt` | Caller remains shell UID 2000, SELinux shell domain | Confirmed |
| `P5BJ-HOME-001` | `adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/home.stdout.txt` | HOME still resolves to `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| `P5BJ-SAFETY-001` | `adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/result.md` | No device writes, exploit execution, node opens, or block reads | Confirmed |

## Integrity

The host-only comparison artifact is verified by:
`artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/sha256sums.txt`.

The device snapshot has its own `sha256sums.txt`; its checks pass when verified from
the repository root because the manifest stores repository-relative paths.
