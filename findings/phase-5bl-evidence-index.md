# Phase 5BL evidence index

| Evidence ID | File | SHA-256 / source | Observation | Confidence |
|---|---|---|---|---|
| `P5BL-RUNTIME-001` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/identity.stdout.txt` | Per-file manifest | PS7330.4104N, Linux 4.4.146+, shell UID 2000, SELinux Enforcing | Confirmed, snapshot scope |
| `P5BL-RUNTIME-002` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/kernel_sysctls.stdout.txt` | Per-file manifest | Most selected sysctls denied; `perf_event_paranoid=3` readable | Confirmed, permission scope |
| `P5BL-RUNTIME-003` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/proc_visibility.stdout.txt` | Per-file manifest | `/proc/kallsyms` denied; no usable `/proc/kcore` or `/dev/kmem` | Confirmed, snapshot scope |
| `P5BL-RUNTIME-004` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/futex_symbols.stdout.txt` | Per-file manifest | Symbol result unavailable because kallsyms read was denied | Confirmed, negative observation only |
| `P5BL-RUNTIME-005` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/proc_visibility.stdout.txt` | Per-file manifest | ION/CMDQ metadata only; no open/ioctl | Confirmed, metadata scope |
| `P5BL-SAFETY-001` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/result.md` | Per-file manifest | No futex trigger or device mutation | Confirmed |
| `P5BL-HOST-001` | `artifacts/phase5/phase5bl-futex-gates-analysis-20260804-01/summary.json` | Per-file manifest | Host-only normalized summary | Confirmed, analyzer scope |
| `P5BF-SOURCE-001` | Phase 5BF source artifact | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | PS7331 build-selected `rtmutex.c` retains pre-fix markers | Confirmed, source scope |
| `P5BF-CONFIG-001` | Phase 5BF captured config | `9fae0dc507c20842b68f8d0c26b8db8fe7d86c7459acb29cfa5b622e2666cbc9` | `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y` | Confirmed, config scope |
| `P5BF-BINARY-001` | Phase 5BF PS7331 Image review | Existing artifact hash | Inspected adjacent Image matches old current-task pattern | Confirmed, inspected-function scope |
| `P5BJ-UPSTREAM-001` | Linux stable patch | Web source | Upstream fix changes cleanup to waiter task | Confirmed, upstream scope |

All raw capture files are immutable inputs for the host-only analyzer. The raw
capture's `sha256sums.txt` and analyzer output's `sha256sums.txt` must pass from
the repository root.
