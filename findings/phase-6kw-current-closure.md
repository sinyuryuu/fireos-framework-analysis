# Phase 6KW — Current HOME-control closure

Status: host-only/static closure plus prior read-only device evidence. No new device mutation was performed in this work unit.

## Executive result

**已證實：** the newly audited vendor `ActivityStackSupervisor` callback boundary does not provide a new Fire Launcher selector in the collected PS7331 artifacts.

- `ActivityStackSupervisor.resolveIntent()` calls `VendorActivityStackSupervisorCallback.callResolveIntent()` first.
- The collected AppCompat implementation delegates to `IPackageManager.resolveIntent()` and only filters the observed uninstalled-app flag.
- The collected Eve supervisor implementation does not override `resolveIntent()`; it inherits the base null result and its observed method is restart telemetry.
- `LauncherHijackPreventer` fosinit registrations are ActivityStack/AMS or PM/permission callbacks, not the supervisor resolver callback.
- When callbacks return null, the framework proceeds to `PackageManagerInternal.resolveIntent()`.

This supports the existing AOSP-shaped explanation for the observed User 0 result (`com.amazon.firelauncher/.Launcher`, priority 50), but it does not prove that every possible runtime-loaded component outside the collected artifacts is absent.

## Evidence

| Evidence | Source | Observation | Confidence |
|---|---|---|---|
| 6KW-CB-001 | `artifacts/amazon-services/appcompatsupport_fosinit.xml` SHA-256 `e89888106c2cdde0b39f2c97e3ebefde7502919adf688cd5c2b9db458302ee8e` | Registers `AppCompatActivityStackSupervisorCallback` under `VendorActivityStackSupervisorCallback`. | Confirmed |
| 6KW-CB-002 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:41123-41144` SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | AppCompat `resolveIntent` calls `IPackageManager.resolveIntent`, then `isUninstalledApp`, returning the result or null on exception. | Confirmed |
| 6KW-CB-003 | `artifacts/amazon-services/eve_launch_time_fosinit.xml` SHA-256 `95f31591f3fd288565bb6901b3e9cb59a13ae782fc3de3f66ad48020a9b22efd` | Registers Eve under the same supervisor callback base. | Confirmed |
| 6KW-CB-004 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:204452-204476` | Eve class has `callOnRestartActivity`, but no concrete `resolveIntent` override. | Confirmed |
| 6KW-CB-005 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:222435-222489` SHA-256 `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` | Base callback loops until a non-null result; base `resolveIntent` returns null. | Confirmed |
| 6KW-CB-006 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:796458-796504` | `ActivityStackSupervisor.resolveIntent` returns a non-null callback result, otherwise calls `PackageManagerInternal.resolveIntent` after the normal flags/identity handling. | Confirmed |
| 6KW-CB-007 | `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml`, `tabletlauncherhijackpreventer_fosinit.xml` | No `VendorActivityStackSupervisorCallback` registration in the collected launcher-hijack-preventer configuration. | Strong evidence |
| 6KV-DEV-001 | `adb/phase6ep/PHASE6EP-AMAZON-WRITER-REACHABILITY-20260809-191243/` | Read-only reachability capture: private Amazon service checks returned `not found`; User 0 Fire package state and HOME resolver were unchanged. | Confirmed for this capture |
| 6KV-SRC-001 | `findings/phase-6kv-pms-home-caller-closure.md` and `artifacts/phase6kv/source-scope-20260810-01/` | 25 exact VDEX package/preferred sink call sites audited; no new Amazon User 0 HOME writer; PS7331 GPL scope is kernel/vendor, not complete framework source. | Strong evidence |

## Worker audit results

Three independent host/worktree read-only audits added no new route:

1. OTA/framework inventory found no new post-install HOME/package writer. The PS7331 updater script contains partition/recovery writes only and was not executed.
2. GPL/MediaTek driver inventory found no source bridge from CMDQ, GED, IDME, lifecycle, metrics or sysenv into PackageManager/HOME. CMDQ remains a sensitive static-only surface; no ioctl, DMA, malformed input or race was run.
3. Existing HOME/IPC inventory found only the known child-user KFT writer, trusted DPM/backup writers, and existing callbacks; none is a reachable User 0 formal HOME replacement under the tested conditions.

## Classification

- **已證實：** standard resolver fallback remains reachable after the collected vendor callback chain returns null.
- **高可信推論：** the collected callback boundary is not the reason Fire Launcher wins User 0 HOME; the observed priority 50 / AOSP resolver path remains the best supported explanation.
- **待驗證：** completeness of runtime `fosinit` loading outside the collected XML set and any native callback not represented in the VDEX artifacts.
- **已排除（目前證據範圍）：** a new shell-callable Amazon service or MediaTek driver route that directly writes User 0 formal HOME.
- **因風險拒絕測試：** unknown Binder transaction codes, driver ioctl/DMA/race probes, OTA/recovery execution, Fire Launcher disable/hide/suspend/uninstall/clear, Root and partition writes.

## Reproduction

Run the host-only audit from the project root:

```sh
python3 tools/scripts/audit_phase6kw_vendor_home_callbacks.py
```

It regenerates `artifacts/phase6kw-vendor-home-callbacks/manifest.json`, `result.md`, `vendor-home-callbacks.csv`, and `vendor-home-callbacks.mmd` from the collected XML and disassembly files. The script does not invoke `adb`.

## Next smallest safe question

If the project continues, the next useful step is not another HOME mutation. It is a completeness check of the runtime-loaded `fosinit` manifest set and the exact callback class-loader inventory, using only existing artifacts or read-only extraction. A new User 0 HOME writer should be claimed only if it has both a concrete package/component state sink and a reachable caller under the actual user/permission gate.
