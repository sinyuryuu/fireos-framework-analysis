# Phase 19 evidence index

All Phase 19 evidence below is host-side unless explicitly marked
`LOCAL-ONLY`. No row is evidence that an unknown Binder, driver, OTA, or root
operation is safe or reachable.

## Source ledgers

| Evidence IDs | Source | SHA-256 | Scope |
|---|---|---|---|
| `P19A-001`–`P19A-006` | `work/luna_worker_phase19_ipc_audit_20260810.csv` | `98ad9f77810372561ee5de4eb361f73270e4a1a53b3ca62db41c3a5d7d0b6418` | Amazon IPC/service boundaries |
| `P19B-01`–`P19B-09` | `work/luna_worker_phase19_ota_audit_20260810.csv` | `9f785ce3d5abe747b3bc86f6408e2118a8ce6ca8228076fc7c2a8aff42f0181a` | OTA/recovery/post-install |
| `P19C-C01`–`P19C-C11` | `work/luna_worker_phase19_driver_audit_20260810.csv` | `60c06d1cc8ae4f11a158ae84dddd47bae77e83feebb33f958441c9b095251808` | MTK/Amazon driver caller closure |
| `P19D-*` | `work/luna_worker_phase19_reconciliation_20260810.csv` | `b51341892438e860e0623ba05619e0a5ca497fc5a811c24e6e0306a3c7df9f9a` | Phase 1–18 no-repeat boundary |
| `P19E-*` | `work/luna_worker_phase19_provenance_20260810.csv` | `6ce141d54f8ed290bd0b82610854e444b4287ea91c3e329dfce482ea9563f320` | PS7331 provenance/version alignment |

The corresponding Markdown audits are retained beside the CSVs. Their hashes
are recorded in the commit manifest and can be regenerated with `sha256sum`.

## Device baseline

`adb/baseline/PHASE19-BASELINE-20260810-01/` is **LOCAL-ONLY** because the raw
capture includes the device serial. Its SHA-256 manifest hash is
`3b443878d4db4e870b7d23f9047906e66370635f11c070f9e7cd65278e00bc77`.

Observed in that read-only capture: PS7331 fingerprint, 2024-08-01 security
patch, SELinux enforcing, User 0 plus existing User 10, and HOME resolving to
`com.amazon.firelauncher/.Launcher`. The capture did not mutate the device.

## Evidence interpretation

- `Confirmed` means the cited artifact or previously saved observation directly
  supports the bounded statement.
- `Strong evidence` means a static capability or boundary is well supported but
  an important caller/runtime edge remains open.
- `Hypothesis` means the saved corpus has not closed the edge.
- `Disproved` is bounded to the named route/test, not a universal absence claim.

The normalized 50-row table is
[phase19-caller-gate-sink.csv](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/tables/phase19-caller-gate-sink.csv).
