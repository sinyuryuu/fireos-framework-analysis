# Phase 6AP evidence index

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AP-RSRC-001` | PS7331 `system.img` debugfs inventory/dump | `/system/framework/fireos-res/fireos-res.apk` exists in the matched system image | Confirmed |
| `6AP-RSRC-002` | `fireos-res.apk` `resources.arsc` | Package ID `0x7e` is named `amazon.fireos` | Confirmed |
| `6AP-RSRC-003` | `resources.arsc` resource map | `0x7e05000a` is `raw/package_manager_deny_list` | Confirmed |
| `6AP-RSRC-004` | `package_manager_deny_list.json` | `com.amazon.firelauncher` is an explicit deny-list member | Confirmed |
| `6AP-RSRC-005` | `resources.arsc` resource map | `0x7e060058` is `string/config_amzpackagemanager_denyListArcusId` | Confirmed |
| `6AP-RSRC-006` | Existing `fosservices` consumer + new resource closure | Resource seed and protected-package consumer form a closed static chain | Strong evidence |

Device contact: none in this static phase. The separate read-only live capture
is `adb/phase6ao/PHASE6AO-RO-20260805-01/`.
