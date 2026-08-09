# Phase 6KU — Low-Privilege IPC and Native Updater Boundary

Date: 2026-08-10
Device context: KFTRWI / trona / Android 9 / PS7331
Scope: host-only synthesis of preserved PS7331 artifacts and previously captured runtime evidence
Device mutation in this phase: **none**

## Executive result

Phase 6KU closes three candidate surfaces without treating capability as
reachability:

1. **已證實 — secondary confused deputy:** an ordinary, no-permission APK can
   reach `AmazonActivityManagerService.BinderService.preWarmApplicationForUser()`.
   The service ignores the result of its `APP_PREWARM` check, clears caller
   identity, and starts a target process. The observed sink is process/resource
   use only. The method does not call a HOME resolver, preferred-activity writer,
   package-state setter, or Fire Launcher restoration path.
2. **已證實 — KFT writer boundary:** the Amazon User Manager tx3 path reaches
   the KFT package/component writer, but the preserved device runs into the
   standard PackageManager cross-user or component-state caller gates. The
   User-10 and User-0 probes produced no launcher or HOME mutation.
3. **已證實 — private PackageManager contract:** the private
   `IAmazonPackageManager` Binder exposes metadata, flags, proxy, and query
   operations; it does not expose a HOME/package-enabled/component-enabled
   setter. Its facade delegates setters to ordinary `IPackageManager` calls.
4. **已證實 — native updater capability:** the PS7331 `update-binary` registers
   24 install callbacks and its preserved script names system/vendor/boot and
   other partitions. The callback map and write edges are now reproduced by a
   host-only parser. No updater, recovery, OTA, Binder transaction, or native
   executable was run.

**結論：** this phase found no new low-privilege User-0 HOME writer, no safe
launcher-replacement route, and no justification for executing the updater or
sending private transactions. The updater is a high-privilege capability behind
an unresolved recovery/provenance boundary, not an ADB workaround.

## Evidence status

### 已證實

- `P4-ER-01`: ordinary-app prewarm confused deputy and process PID effect. See
  `findings/phase-6er-amazon-prewarm-confused-deputy.md:8-11,31-39,50-56`.
- KFT tx3 enters the Amazon writer but is rejected by downstream PMS gates for
  both tested user contexts. See
  `findings/phase-6fi-fk-amazon-user-manager-tx-boundary.md:35-45,93-112`.
- The private Amazon PackageManager interface has no relevant HOME or package
  state setter and shell lookup returned `not found`. See
  `findings/phase-6ia-amazon-package-manager-closure.md:7-11,63-74,103-116,133-151`.
- The native updater's callback registration and fixed script targets are
  reproduced in `artifacts/phase6ku/boundary-20260810-01/`.

### 高可信推論

- The native updater is intended to be entered from an accepted recovery/update
  context, not directly by a shell or ordinary app. This is supported by the
  Java verification/handoff analysis and by the absence of a low-privilege
  caller in the preserved artifacts, but the complete recovery-to-updater
  provenance is not present in this phase.
- The standard PMS gates, rather than a newly discovered Amazon private relay,
  remain the effective User-0 package/component boundary on the observed build.

### 待驗證

- The complete platform recovery verifier and its end-to-end handoff to
  `update-binary`.
- Indirect function-pointer dispatch outside the recovered direct call-edge
  slice.
- Full platform/native staging canonicalization and any recovery-only caller
  restrictions.
- Any low-privilege User-0 writer not represented by the analyzed Amazon
  service contracts.

### 已排除（目前證據範圍）

- `AmazonActivityManager` prewarm as a HOME replacement or root path.
- `IAmazonPackageManager` private Binder as a User-0 package-state/HOME relay.
- KFT tx3 as an ordinary-app User-0 Fire Launcher disable path.
- A shell/ordinary-app direct updater invocation.

### 因風險拒絕測試

- Executing `update-binary`, recovery, or an OTA archive.
- Supplying crafted OTA, updater-script, symlink, traversal, or partition input.
- Sending guessed/private Binder transaction parcels.
- Writing boot, system, vendor, preloader, LK, TEE, or any other partition.
- Disabling, hiding, suspending, uninstalling, or clearing Fire Launcher.

## IPC boundary findings

### Ordinary-app prewarm

The preserved runtime and VDEX evidence establish this path:

```text
ordinary no-permission APK
  -> ServiceManager.getService("amazonactivitymanager")
  -> IAmazonActivityManager transaction 1
  -> BinderService.preWarmApplicationForUser()
  -> checkCallingPermission(APP_PREWARM) [result ignored]
  -> clearCallingIdentity()
  -> IPackageManager.getApplicationInfo()
  -> ActivityManagerService.startProcessLocked(..., "prewarm", ...)
  -> target process appears
```

The method does not call `setHomeActivity`, preferred-activity APIs,
`setApplicationEnabledSetting`, or `setComponentEnabledSetting`. The finding is
important for authorization review, but its demonstrated sink is not in the
launcher control plane.

### KFT tx3

The relevant path is:

```text
ordinary APK
  -> IAmazonUserManager.Stub.onTransact(tx3)
  -> UserInfo.CREATOR.createFromParcel()
  -> AmazonUserManagerService.enableKftLauncher(UserInfo.id)
  -> tryEnableKftLauncherComponent()
  -> AmazonPackageManager facade
  -> standard IPackageManager component setter
  -> PMS cross-user/component-state gate
  -> false / SecurityException
```

The service-side missing method-local caller check is a static weakness, but the
runtime PMS sees the ordinary caller for the tested writes. User 10 failed the
cross-user gate; User 0 failed the component-state caller gate before mutation.

### Private Amazon PackageManager

The private contract publishes metadata/flag/proxy/query operations. The facade
methods that look like package-state or preferred-activity writers are standard
PMS calls, not an alternate privileged transaction. The shell could not obtain
the private service (`Service amazonpackagemanager: not found`) and no private
transaction was dispatched.

## Native updater boundary

The reproducible script is:

```sh
python3 tools/scripts/build_phase6ku_boundary.py \
  --root . \
  --output artifacts/phase6ku/boundary-20260810-01
sha256sum -c artifacts/phase6ku/boundary-20260810-01/sha256sums.txt
```

The parser reads the original ELF, the saved direct call-edge CSV, recovered
mini-debug symbols, disassembly, and the original updater-script. It does not
load or execute the ELF. It recovers:

- `RegisterInstallFunctions`: `0x406978–0x407078`.
- 24/24 callback registrations, including `package_extract_file`,
  `block_image_update` support through the updater’s expression engine,
  `write_value`, `run_program`, and `reboot_now`.
- `LoadSrcTgtVersion3 -> VerifyBlocks` call sites and the
  `WriteToPartition -> ota_write` / `ota_open -> libc open` edges selected from
  the saved call-edge table.
- 17 relevant updater-script commands, all marked `NOT_EXECUTED`.

The original script contains fixed targets including:

```text
/dev/block/platform/bootdevice/by-name/system
/dev/block/platform/bootdevice/by-name/vendor
/dev/block/platform/bootdevice/by-name/boot
/dev/block/platform/bootdevice/by-name/preloader
/dev/block/platform/bootdevice/by-name/lk
/dev/block/platform/bootdevice/by-name/tee1
/dev/block/platform/bootdevice/by-name/tee2
/dev/block/platform/bootdevice/by-name/spmfw
/dev/block/platform/bootdevice/by-name/sspm_1
/dev/block/platform/bootdevice/by-name/cam_vpu1
/dev/block/platform/bootdevice/by-name/cam_vpu2
/dev/block/platform/bootdevice/by-name/cam_vpu3
```

This proves a conditional high-privilege capability, not a caller path. Phase
6KT separately records the Java verification wrapper and the unresolved
recovery/native handoff; see `findings/phase-6kt-recovery-verifier-provenance.md:8-20,44-72,140-154`.

## Reproduction and provenance

The generated bundle is self-contained for this bounded audit:

| Artifact | Purpose | SHA-256 |
|---|---|---|
| `result.json` | inputs, policy, 24-entry map, unresolved items | `9ea29dec2c17a72ed0758549a7a975a4245bed76739b78d8cda098264c6054de` |
| `updater-dispatch.csv` | callback names, GOT/handler addresses, symbols | `83f6416cad7d5aba74e550059dd3b8aecaabbc951f61ae9b1df18e855de000e1` |
| `updater-script-commands.csv` | parsed fixed commands and targets | `a4c57723ae0744516409bab371a4bf7282ed457d5dd42b05d5784f3a8966d8ee` |
| `relevant-call-edges.csv` | bounded native call-edge slice | `5bb41aa79721cd62dc419d0f48faaaf66833a0f1826c93dd1906e64be14bbefd` |
| `sha256sums.txt` | manifest for the generated bundle | `472fa2612e429a4d0f7be16e069b627d18848877cfc59b50c2ee7a759d93f704` |

The input hashes and execution policy are recorded in `result.json`. The
policy fields are all false for ADB, Binder, APK execution, native execution,
OTA/recovery, and partition write.

## Decision

The best current research result is a **boundary closure**, not a new
workaround:

```text
ordinary app -> prewarm -> process/resource effect only
ordinary app -> KFT tx3 -> standard PMS gate -> no User-0 mutation
shell -> private Amazon PM -> service-manager boundary / no relevant setter
recovery-accepted context -> native updater -> partition capability
                                      ^
                                      unresolved low-privilege provenance
```

No additional device experiment is justified by this phase. The next useful
work, if retained, is host-only identification of the platform recovery verifier
and exact caller provenance. It should not be converted into an OTA execution
test or a crafted-input test without a separate high-risk approval report.
