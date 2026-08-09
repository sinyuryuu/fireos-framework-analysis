# Phase 6MV evidence index

Generated: 2026-08-09T22:22:27.376830+00:00
Scope: read-only runtime capture plus host-only GPL/OTA inventory.

| Evidence ID | Source | Observed | Confidence |
|---|---|---|---|
| 6MV-RUNTIME-001 | adb/phase6mv/PHASE6MV-READONLY-20260810-02/home_resolve.stdout.txt | User 0 HOME resolves to Fire Launcher priority 50 | Confirmed |
| 6MV-RUNTIME-002 | adb/phase6mv/PHASE6MV-READONLY-20260810-02/home_candidates.stdout.txt | Fire, Microsoft, and FallbackHome are the three listed candidates | Confirmed |
| 6MV-RUNTIME-003 | adb/phase6mv/PHASE6MV-READONLY-20260810-02/firelauncher_package.stdout.txt | Fire has distinct User 0 and User 10 records | Confirmed |
| 6MV-RUNTIME-004 | adb/phase6mv/PHASE6MV-READONLY-20260810-02/service_*_stdout.txt | Seven selected private service checks report not found for shell | Confirmed |
| 6MV-RUNTIME-005 | adb/phase6mv/PHASE6MV-READONLY-20260810-02/service_list.stdout.txt | Service-name listing alone does not prove a shell Binder handle | Confirmed |
| 6MV-SOURCE-001 | work/luna_worker_phase6mv_gpl_ota_inventory_20260810.md | GPL/OTA/source scope and hashes are inventoried without execution | Strong |

The report builder itself contacted no device and performed no mutation.
