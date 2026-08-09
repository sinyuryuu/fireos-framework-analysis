# Phase 6MW evidence index

Classification: host-only static inventory. No device contact, Binder
transaction, ioctl, reboot, OTA, Root/exploit, APK execution, or package/HOME
mutation occurred.

| Evidence ID | Source | Observation | Classification |
|---|---|---|---|
| 6MW-001 | `artifacts/phase6mw-home-state-sinks-20260810-01/summary.json` | 21,875 preserved Java/disassembly input files were scanned and 175 direct sink/reference rows were indexed. | Confirmed |
| 6MW-002 | `artifacts/phase6mw-home-state-sinks-20260810-01/sink-calls.csv` | 19 Amazon/OEM-scope rows and 2 bounded-context rows containing a direct Fire Launcher literal are preserved for review. | Confirmed static |
| 6MW-003 | `artifacts/phase6mw-home-state-sinks-20260810-01/input-manifest.csv` | All source/disassembly inputs have SHA-256 values; the corpus is reproducible without device access. | Confirmed |
| 6MW-004 | `artifacts/phase6mw-home-state-sinks-20260810-01/summary.json` | The audit records `adb=false`, `binder_transaction=false`, and `device_mutation=false`. | Confirmed |
| 6MW-005 | `findings/phase-6mh-package-state-writer-closure.md`, `findings/phase-6ia-amazon-package-manager-closure.md` | Existing bounded reviews remain the authority for KFT child user scope and the absence of a private Amazon HOME setter. | Strong evidence |
| 6MW-006 | `artifacts/phase6mw-home-state-sinks-20260810-01/sink-calls.csv` | Native, reflective, indirect, or runtime-only consumers are not established by this direct-reference scan. | Pending |

Every row is a reference/callsite candidate, not proof of runtime
reachability, authorization failure, or exploitability.
