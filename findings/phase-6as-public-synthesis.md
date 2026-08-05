# Phase 6AS — PS7331 public synthesis

## Scope

This report is a bounded, host-only synthesis of the latest PS7331 service,
HOME, package-protection and OTA evidence. It uses the serial-redacted Phase
6AQ public summary and static reports; raw device captures remain local.

The generator performs no ADB access, Binder transaction, broadcast, OTA or
recovery action, package mutation, reboot, or partition write.

## Findings

### 已證實

- The bounded Home-key implementation constructs an implicit
  `MAIN + CATEGORY_HOME` intent and calls `startActivityAsUser`; it does not
  construct an explicit Fire Launcher component in that method.
- The saved enforcing-policy capture blocks shell discovery of the selected
  Amazon private services. A service name in `service list` is not evidence
  that shell can obtain or transact on its Binder interface.
- PS7331's `amazon.fireos` deny-list resource contains
  `com.amazon.firelauncher` and is connected by the saved consumer evidence to
  the PackageManager protected-package callback.
- The official PS7331 updater has static system/vendor and direct block-device
  write intent. The updater, recovery and partition paths were not executed.
- `BootAfterSystemOTAReceiver` is a guarded post-OTA/OOBE lifecycle surface,
  not a normal shell HOME setter.

### 高可信推論

The ordinary HOME result is best explained by the privileged Fire Launcher
candidate plus the standard implicit resolver, with Amazon task-visibility and
package-protection callbacks forming separate boundaries. The inspected
bounded callback methods do not show a direct `com.amazon.firelauncher`
component injection.

### 已排除目前安全範圍

- A shell-accessible Amazon private-service HOME setter.
- Replaying the OTA/OOBE lifecycle as a normal launcher replacement.
- Treating OTA/updater execution as a safe runtime experiment.

### 待驗證

- Caller authorization for every private Binder method outside the bounded
  method inventory.
- Native/recovery canonicalization and atomicity details.
- Any privilege transition or root path. No such path is established.

## Reproduction

```sh
python3 tools/scripts/build_phase6as_public_synthesis.py --dry-run
python3 tools/scripts/build_phase6as_public_synthesis.py \
  --output artifacts/phase6as/public-synthesis-20260805-02
shasum -a 256 -c artifacts/phase6as/public-synthesis-20260805-02/sha256sums.txt
```

The generated artifact contains the input hash map, CSV control-surface
matrix, Mermaid graph, metadata, bounded summary and SHA-256 manifest.
