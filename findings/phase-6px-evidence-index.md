# Phase 6PX evidence index

公開基準：`a51db9cbb758785687312dc01888ebb9764140b2`

| Evidence ID | Source | File | SHA-256 | Result | Confidence |
|---|---|---|---|---|---|
| `PX-DENY-01` | deny-list worker | `work/luna_worker_denylist_provenance_followup_20260810.csv` | `3c24274403383899e74dc78eb08670217a795698b00ad36aa89f60c1aa07721f` | 12 rows; extracted resource directly lists Fire Launcher | Confirmed static |
| `PX-DENY-02` | deny-list report | `work/luna_worker_denylist_provenance_followup_20260810.md` | `38670978ad7adb8f420474ab306ab051e25caf592bb5125942651f4d016ef699` | resource seed, callback reader and live-set limitation separated | Strong evidence |
| `PX-OTA-01` | BOOT_AFTER_SYSTEM_OTA worker | `work/luna_worker_bootafter_ota_provenance_followup_20260810.csv` | `b4ccec9253be7da78ba77e36e536bf6078b871bde1227ad3e4884b20f647954e` | 12 static edges; system-server/lifecycle/OOBE chain | Confirmed static |
| `PX-OTA-02` | BOOT_AFTER_SYSTEM_OTA report | `work/luna_worker_bootafter_ota_provenance_followup_20260810.md` | `c858b0e8de5ed87bddd11b9dde9fb26747b65ad8bc21c80c56c28de03f5af9aa` | no ordinary caller or Fire HOME writer found | Strong evidence |
| `PX-REC-01` | OTA/recovery worker | `work/luna_worker_ota_recovery_handoff_followup_20260810.csv` | `5050cc6cdfee2970f5179bb9a8efc24c5175e42e362ae5e1b2a35dbe96c11a9f` | 9 routes; capability separated from caller reachability | Strong evidence |
| `PX-REC-02` | OTA/recovery report | `work/luna_worker_ota_recovery_handoff_followup_20260810.md` | `c6f9bd54af7aa4235ab0ae65f17c840b81ed9249260af9fe8b96ccc201b3ddd4` | no low-privilege recovery/updater handoff established | Strong evidence |
| `PX-NORM-01` | normalized closure | `output/tables/phase6px-provenance-closure.csv` | `4c914ca5cf7446eeb0f84fd19de4c1267ee32f5719c740a417357c397e852a11` | 33 rows across deny-list, OOBE and recovery | Confirmed |
| `PX-NORM-02` | normalization manifest | `output/tables/phase6px-provenance-closure.csv.manifest.json` | `bb14b100a14033d71694766845560eccec67287271750651213299895d38495e` | device_contacted=false; mutation=false; OTA=false | Confirmed |
| `PX-LIVE-01` | current comparator | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | User 0 Fire HOME priority 50 | Confirmed |
