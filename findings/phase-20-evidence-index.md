# Phase 20 evidence index

Phase 20 is host-only. A row documents an artifact or a bounded prior result;
it does not authorize a private Binder call, driver operation, OTA execution or
root attempt.

## Raw worker ledgers

| IDs | File | Scope |
|---|---|---|
| `P20A-001`–`P20A-006` | `work/luna_worker_phase20_ipc_closure_20260810.csv` | IPC caller, gate, identity and user scope |
| `P20B-01`–`P20B-11` | `work/luna_worker_phase20_ota_closure_20260810.csv` | OTA/recovery/verifier boundary |
| `P20C-001`–`P20C-010` | `work/luna_worker_phase20_driver_closure_20260810.csv` | MTK/Amazon driver caller closure |
| `P20D-*` | `work/luna_worker_phase20_reconciliation_20260810.csv` | no-repeat and residual test boundary |
| `P20E-*` | `work/luna_worker_phase20_provenance_20260810.csv` | version/path/hash/source scope |

The normalized 43-row table is
[phase20-caller-gate-sink.csv](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/tables/phase20-caller-gate-sink.csv).

## Interpretation labels

- `Confirmed`: the bounded artifact or saved observation directly supports the
  stated fact.
- `Strong evidence`: static capability or a partial caller join is supported,
  but a security or runtime edge remains open.
- `Probable`: multiple supporting indicators exist, with an unresolved edge.
- `Hypothesis`: the required edge is not closed.
- `Disproved`: only the named route is contradicted by saved evidence; this is
  not a universal absence claim.

## Key evidence IDs

| ID | Bounded statement | Status |
|---|---|---|
| `P20A-001` | H2 child-user workflow reaches KFT tx3; identity is not shown to be laundered and User 0 is not established | Strong evidence |
| `P20A-004` | H2 service is signature-bound and feeds profile/KFT workflow; no direct HOME/PMS setter | Strong evidence |
| `P20A-006` | DCPMS is signature-bound and bounded decision/callback paths have no sensitive platform sink | Confirmed, bounded |
| `P20B-02` | Java OTA verification/install handoff is statically present; caller reachability is not established | Strong evidence |
| `P20B-03`–`P20B-05` | `update_verifier` and recovery repair/write capabilities are present | Confirmed static capability |
| `P20B-07`–`P20B-10` | AVB/rollback and recovery UID/SELinux reachability remain unresolved | Hypothesis / negative boundary |
| `P20C-004` | `meta_tst` has gsensor imports, init identity and CIL edge | Strong evidence, partial |
| `P20C-005` | `rpmb_svc` has TEE/RPMB static caller/policy edge | Strong evidence, partial |
| `P20C-007` | `meta_tst` has USB sysfs diagnostic edge | Strong evidence, partial |
| `P20D-FOSINIT-001`–`P20D-DENYLIST-004` | residuals are host-only or risk-rejected; no equivalent device test is justified | Confirmed boundary |
| `P20E-001`–`P20E-012` | PS7331 and saved PS7330 provenance are separated | Confirmed provenance |

## Device evidence boundary

No fresh device output was used to claim a Phase 20 runtime effect. Existing
PS7331/PS7330 captures remain separated by timestamp and provenance. Device
mutations and high-risk operations are explicitly excluded in the Phase 20
report.
