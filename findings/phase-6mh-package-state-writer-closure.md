# Phase 6MH — Package/component state-writer inventory closure

Date: 2026-08-10
Classification: host-only smali/disassembly inventory; no device mutation.

## Result

The exact PS7331 `fosservices` and `services` disassembly contains **21**
references to `setComponentEnabledSetting` or
`setApplicationEnabledSetting`:

| Category | Count | Disposition |
|---|---:|---|
| `amazon_app_adapter` | 1 | Fixed OOBE registration component; not HOME. |
| `amazon_kft_child_user` | 3 | Child/profile lifecycle; supplied `UserInfo.id`; not a proven User-0 path. |
| `amazon_product_policy` | 4 | Trusted policy-file/user-list action; exact PS7331 policy inputs contain no Fire Launcher entry. |
| `espresso_boot_receiver` | 2 | Metadata/permission-gated boot-complete receiver map; no HOME/Fire target established. |
| `standard_shell_command` | 2 | Standard shell → IPackageManager path; existing protected-package gate. |
| `standard_pms_internal` | 1 | PMS sink. |
| remaining Android internal writers | 8 | Bluetooth, input method, AMS, DPM, WebView, and related fixed/system paths; no new HOME writer in the inventory. |

The inventory is a callsite list, not proof that every caller is reachable by
shell. The `device_mutation` field is `false` for every row.

## High-value rows

1. `AmazonUserManagerService$BinderService.enableKftLauncherComponent` at
   `fosservices/disassembly.log:54310-54324` includes Fire/Tahoe/Launcher3
   literals but takes `UserInfo` and passes `UserInfo.id`. This is the already
   closed child/profile control branch, not a newly discovered User-0 writer.
2. `EnableDisableComponentAction.enableDisableComponent` at
   `fosservices/disassembly.log:293712-293738` can request package/component
   state for users selected by the policy action. Its input is policy-file and
   user-list driven. Phase 6CE independently established that the exact
   PS7331 policy files contain no `com.amazon.firelauncher`, and that the
   service publishes a local service rather than a public ProductPolicy Binder.
3. `EspressoShotCallback.disableBootCompleteReceivers` and
   `reEnableBootCompleteReceivers` at
   `fosservices/disassembly.log:191881` and `192065` operate on a gated map of
   boot-complete receivers. No HOME or Fire Launcher target is present in the
   bounded callsite context.
4. `PackageManagerShellCommand.runSetEnabledSetting` at
   `services/disassembly.log:500744-500765` is the ordinary shell path and
   terminates at the known PMS protected-package boundary. Re-running its Fire
   component test would duplicate an established result and was not done.

## Reproducibility

- Script: `tools/scripts/audit_phase6mh_package_state_writers.py`
- Table: `output/tables/phase6mh-package-state-writers.csv`
- Graph: `output/call-graphs/phase6mh-package-state-writers.mmd`
- Artifact: `artifacts/phase6mh-package-state-writers-20260810-01/`
- Source hashes:
  - `fosservices/disassembly.log`: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
  - `services/disassembly.log`: `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`
- Artifact hashes are recorded in `artifacts/phase6mh-package-state-writers-20260810-01/sha256sums.txt`.

## Verdict

- **已證實：** all 21 setter callsites in the preserved two-disassembly
  corpus are indexed and classified.
- **高可信推論：** no ordinary shell/ordinary-app User-0 HOME writer was
  added by the newly inventoried Amazon state writers.
- **已排除：** Product Policy as the normal PS7331 User-0 Fire restoration
  writer, based on the exact policy-input audit in Phase 6CE.
- **待驗證：** exact runtime user mapping for the OOBE helper, and the exact
  deny-list entry provenance. Neither is a safe reason to mutate Fire Launcher.
