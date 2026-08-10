# Phase 6PW evidence index

公開基準：`a86d013611fcb3c2c5279cbe9c2f74b4069dca2d`

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| `PV-LIVE-RO-01` | read-only runtime capture | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/metadata.txt` | `3c1adbbe8bdbfcd2e322647203157a68d5d45ab854ac4a40001fc8b0cf5c3f16` | mutation=false, binder_transaction=false, reboot=false | Confirmed |
| `PV-LIVE-RO-02` | HOME resolver | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | Fire Launcher priority 50 resolved for User 0 | Confirmed |
| `PV-LIVE-RO-03` | HOME candidates | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/home_candidates.stdout.txt` | `e868693c97bce5ec4c93c6e5e144225797c2219fafde54d46fdbd3bdf462442c` | Fire 50, Microsoft 0, FallbackHome -1000 | Confirmed |
| `PV-LIVE-RO-04` | shell/build capture | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/getprop.stdout.txt` | `f60e1f2b9050d355da7f197e362e59ec87ac4ac24e43a27b72669c6264ce6e29` | Current PS7331 build properties preserved | Confirmed |
| `PV-LIVE-RO-05` | capture manifest | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/sha256sums.txt` | `c5c957b23ac4f8a5e244781b88a8cc74aab0c52efeb22b1a85a4bcbefd9f40e2` | All capture files verified | Confirmed |
| `PV-WORKER-01` | evidence audit | `work/luna_worker_evidence_audit_followup_20260810.csv` | `22071e755ab29f5485b0d6f55404a517d3d795577226253ccc50312036587a7b` | 12 existing evidence rows; no new accepted privilege/HOME route | Strong evidence |
| `PV-WORKER-02` | IPC boundary audit | `work/luna_worker_ipc_boundary_followup_20260810.csv` | `86593bcec3839f87ef1b3843ab1c82390630e4acd2ca1457f56d8a5715278e39` | 9 de-duplicated IPC routes; all closed | Strong evidence |
| `PV-WORKER-03` | workaround/HOME audit | `work/luna_worker_workaround_audit_followup_20260810.csv` | `ecc4dec437dc3fce3431ebce164ea12d475362b388200311dccc2f3f1ac7765d` | 18 routes; child HOME only and redirect temporary | Strong evidence |
| `PV-NORM-01` | reproducible normalization | `output/tables/phase6pw-route-classification.csv` | `d79ec8ebfb3d9e21f28dc4c3162f7ba7da5282fb5c7f40d1a5c91df9d39968b3` | 40 normalized rows across evidence, IPC, workaround and live state | Confirmed |
| `PV-NORM-02` | normalization manifest | `output/tables/phase6pw-route-classification.csv.manifest.json` | `66172dde10cf704e7970524f6577572bfe054799583c1273441eb0209b072a02` | input hashes and device_contacted_by_script=false | Confirmed |
