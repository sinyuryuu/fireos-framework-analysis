# Phase 6WJ — post-6VF test/result reconciliation

Date: 2026-08-10 (Asia/Taipei). This is a host-only audit of existing `adb/`,
`findings/`, `artifacts/`, `output/`, and `tools/` evidence. No device tests,
ADB mutations, Binder transactions, driver/ioctl operations, OTA/recovery,
reboot, root, exploit, or partition operation was run.

The companion CSV is the deduplicated matrix. It has ten route families covering
the requested HOME, package state, KFT/child, DPM, settings/overlay, private
Binder, OTA, native driver, PI-futex/root, and alternate-launcher surfaces.

## Reconciliation result

No genuinely contradictory runtime result was found. The recurring apparent
conflicts resolve to different evidence classes or scopes:

- child/profile KFT state changes are not User-0 HOME changes;
- static enabled-state/HOME/OTA/driver/Binder sinks are not caller reachability;
- foreground/accessibility/ADB behavior is not formal persistent HOME state;
- service visibility and interface candidates are not successful Binder calls;
- OTA and native writer graphs are not executed partition effects; and
- PI-futex/root source or probe evidence is not a retail privilege transition.

Phase 6VF explicitly records 6VA–6VE as its five worker ledgers and 6VD as the
prior 19-family reconciliation. This report integrates those ledgers without
promoting any previously rejected or unexecuted operation. The 6VF report itself
has no corresponding `adb/phase6vf` directory; its evidence is the findings and
work ledgers listed in the CSV.

## Deduplication decisions

The canonical result for User-0 remains Fire Launcher under the saved resolver
evidence. Package/component setters, preferred activity, accessibility/ADB,
child/KFT, DPM, settings/overlay, private IPC, OTA, native-driver, and
PI-futex/root families do not close the full chain
`caller → gate → identity/user scope → sink → observed effect`.

The static 6VE inventory is retained as a sink inventory, not a test result.
The 6VB/6VC ledgers are retained as static OTA/driver closure, not execution
evidence. KFT rows are retained with explicit child/profile scope. No denied
component-disable replay or unknown Binder/driver/OTA operation is recommended.

## Genuinely new safe read-only probes

Only host-side joins not already represented as a completed route result are
listed in the CSV's `new_safe_read_only_probe` column:

1. Join HOME sinks to saved resolver outputs by target and user.
2. Normalize package writers and alternate-launcher targets by caller, method,
   and user argument.
3. Join KFT `UserInfo.id` flow to saved child and User-0 snapshots.
4. Cross-reference DPM sink rows with saved policy/user/HOME outputs.
5. Map overlay/default-home keys to concrete settings sinks and saved keys.
6. Join private Binder method candidates to saved publication and permission
   artifacts without issuing a transaction.
7. Reconcile OTA EOF/manifest/path/caller provenance while leaving AVB handoff
   unknown.
8. Join driver control edges to DT_NEEDED/relocation/domain/node policy.
9. Compare saved PI-futex/root logs and source/config hashes for missing
   identity/scope/sink fields.
10. Build a target-by-user persistence matrix for alternate launchers.

These are organization/static-analysis probes only. They do not authorize a
device replay. The CSV preserves exact source paths and SHA-256 values; source
evidence was not modified.

## Evidence and limits

The authoritative 6VF ledger hashes are:

| source | SHA-256 |
|---|---|
| `work/luna_worker_phase6va_fosinit_residual_closure_20260810.csv` | `834676c20c53cb7910f2ed56f382fd4d90e0f04c56aaba23433a4b770c3eab2c` |
| `work/luna_worker_phase6vb_ota_postinstall_closure_20260810.csv` | `4eaeb6302d1fde0752bc052cd9c67b0b5ee1d3bac7f93935352dced1c36d3fd5` |
| `work/luna_worker_phase6vc_driver_caller_policy_20260810.csv` | `8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0` |
| `work/luna_worker_phase6vd_test_reconciliation_20260810.csv` | `78462b8645a0c05bb134a0bae89a62cf154d0126c4aae24a93afe03d3be8a95e` |
| `work/luna_worker_phase6ve_framework_sink_inventory_20260810.csv` | `42d609d5d427fb691031e54caf9d25ee62718f9be64f7bf32fbc53d7eb88ab6a` |

The matrix deliberately keeps `UNKNOWN`/incomplete caller, permission,
identity, user-scope, and runtime-effect fields unresolved. A static marker,
registration, package visibility result, or writer callsite must not be read as
proof of external reachability.
