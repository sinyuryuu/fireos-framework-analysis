# Fire OS 7 Framework Analysis — Phase 2 Report

Date: 2026-08-03

Device build: Amazon Fire HD 10 (11th generation), `KFTRWI` / `trona`, Fire OS 7.3.3.0, Android 9/API 28, build `PS7330.4104N`, security patch `2024-02-01`.

Scope: protected-package enforcement and HOME resolution. The report uses preserved runtime evidence and focused Fire OS/AOSP static analysis. It does not claim more than the evidence supports.

## 1. Executive Summary

### Where does the rejection occur?

`Confirmed`: the tested `pm` and `cmd package` component requests are rejected by `PackageManagerService.setEnabledSetting()` before enabled-state persistence. The runtime stack reports `PackageManagerService.java:21128`; the Fire OS VDEX branch is at `services/disassembly.log:953377-953543`, where instruction `0x2d458e` calls `ProtectedPackages.isPackageStateProtected()` and `0x2d45aa` builds the protected-package exception. Evidence: `P2-RUN-001`, `P2-RUN-002`, `P2-STATIC-001`.

### Is the gate AOSP or Amazon?

Both layers are involved. `Confirmed`: the underlying protected-package gate and Device Owner/Profile Owner/provisioning concepts are standard Android 9 behavior (`P2-AOSP-001`). `Confirmed`: Fire OS adds `VendorProtectedPackagesCallback` aggregation to `ProtectedPackages` and Amazon registers `ControlProtectedPackagesCallback` (`P2-STATIC-002`, `P2-STATIC-003`, `P2-STATIC-005`).

### How does Fire Launcher enter the protected set?

`Strong evidence`: Amazon’s callback protects system apps when their package names occur in `DenyListKeyPackages`, and the tested caller is shell UID 2000. The deny-list is backed by `/data/system/PackageManagerDenyList` and can be seeded from a `packages_deny_list` resource or updated through the Arcus helper (`P2-STATIC-004`–`P2-STATIC-007`). The exact current file content was not readable as shell, so a literal `com.amazon.firelauncher` entry is not marked `Confirmed`.

### Where does priority 50 come from?

`Confirmed`: `com.amazon.firelauncher/.Launcher` declares `android:priority="50"` in its HOME intent filter (`AndroidManifest.xml:316-330`; `P2-MAN-001`).

### Why does HOME resolve to Fire?

`Confirmed`: the query contains Fire, Microsoft, and Settings FallbackHome; Fire has priority 50 and the effective resolver returns Fire (`P2-HOME-001`). `Confirmed`: an ordinary Fire preferred record is present in the baseline (`P2-HOME-002`). `Strong evidence`: setting Microsoft as the preferred HOME writes a Microsoft record but leaves the effective resolver and Home result at Fire (`P2-HOME-003`). The leading explanation is priority/ranking plus the Fire preferred state. A separate Amazon resolver filter or direct Fire component launch is not proven.

### Can Preferred Activity be changed?

`Confirmed`: `cmd package set-home-activity` returns success and changes the visible preferred record in the preserved test. `Strong evidence`: that write does not change the effective HOME resolver on this build. Cross-reboot persistence for this exact route was not tested; it is `Unknown`.

### Is there a stable no-root workaround?

`Disproved`: Fire package/component disable and the ordinary `set-home-activity` route are not working default-HOME changes under the tested conditions. `Only a redirect workaround`: direct activity launch or an after-key redirect could display a third-party launcher but would not change the resolver. No persistent no-root workaround is confirmed (`findings/workaround-assessment.md`).

## 2. Existing Confirmed Results

The Phase 2 input review is in `findings/phase-2-input-summary.md`. The original tests were not repeated.

| Result | Evidence |
|---|---|
| `pm disable-user` Fire HOME component returns protected-package exception | `P2-RUN-001` |
| `cmd package disable-user` returns the same exception | `P2-RUN-002` |
| Package/component state did not change | `P2-STATE-001` |
| HOME resolver, resumed activity, and window focus remained Fire | `P2-STATE-002` |
| Existing Microsoft preferred-home test writes a record but effective HOME remains Fire | `P2-HOME-003` |
| No Root, factory reset, flashing, remount, or boot-image modification was executed | `P2-SHA-001` and Phase 2 input summary |

## 3. Protected Package Enforcement Path

```text
pm / cmd package
  -> PackageManagerShellCommand.runSetEnabledSetting(I)I
  -> IPackageManager.setComponentEnabledSetting(ComponentName,int,int,int)
  -> PackageManagerService.setComponentEnabledSetting(...)
  -> PackageManagerService.setEnabledSetting(...)
  -> ProtectedPackages.isPackageStateProtected(userId,packageName)
  -> ProtectedPackages.isProtectedPackage(packageName)
  -> VendorProtectedPackagesCallback.callShouldProtectPackage(...)
  -> ControlProtectedPackagesCallback.shouldProtectPackage(uid,packageName,context)
  -> system-app + deny-list + shell UID 2000
  -> SecurityException
```

The same private `setEnabledSetting` helper is used by the whole-package enabled-state path. The shell command’s component invocation is explicitly visible at VDEX `services/disassembly.log:500701-500765`, instruction `0x2dbbc2`; the component service method is at `966830-966833`, code offset `0x2d42f0`; the private gate is at `953377-953543`, code offset `0x2d432c`.

The Mermaid and text forms are in `output/call-graphs/component-disable-call-path.mmd` and `findings/component-disable-call-path.md`.

## 4. AOSP vs Fire OS Difference

The minimal AOSP comparison found:

```text
AOSP Android 9:
  setEnabledSetting
    -> mProtectedPackages.isPackageStateProtected
    -> provisioning/Device Owner/Profile Owner checks
    -> SecurityException

Fire OS:
  same base gate
    + VendorProtectedPackagesCallback.findCallbacks()
    + callback aggregation in isProtectedPackage()
    + Amazon ControlProtectedPackagesCallback
    + Amazon deny-list / shell UID rule
```

Classifications:

- `AOSP_STANDARD`: base gate, protected exception, Device Owner/Profile Owner/provisioning logic.
- `AMAZON_ADDITION`: vendor callback type, callback aggregation, Amazon registration, shell deny-list callback, Arcus/resource producer.
- `VERSION_DIFFERENCE`: r1/r61 source line drift.
- `UNKNOWN`: exact current deny-list membership source/content.

No full `services.jar` textual diff was used as proof. Critical Fire OS decisions are based on VDEX instructions and runtime output, in accordance with the project rule to inspect low-level output when decompilation is uncertain.

## 5. Protected Package Source

The protected set has at least two logically separate sources:

1. Standard Android provisioning and Device Owner/Profile Owner ownership.
2. Fire OS vendor callback protection.

The callback source is Amazon’s `PackageManagerDenyList` SharedPreferences key `DenyListKeyPackages`. `DenyListArcusHelper` can initialize it from a system raw JSON resource with key `packages_deny_list` and can replace it from an Arcus-delivered JSON list. Device metadata confirms the data-system file exists, but shell access to its contents is denied.

The Fire Launcher’s system/priv-app placement satisfies the callback’s system-app class of input. The runtime protected error demonstrates that the callback’s final result is true for the tested shell request, but it does not disclose the list contents.

## 6. HOME Resolver Mechanism

### Candidate table

| Candidate | Priority | State |
|---|---:|---|
| `com.amazon.firelauncher/.Launcher` | 50 | Enabled/exported; effective result |
| `com.microsoft.launcher/.Launcher` | 0 | Enabled/exported; still a candidate |
| `com.android.settings/.FallbackHome` | -1000 | Enabled fallback |

Evidence: `P2-HOME-001`.

### Manifest and preferred state

The Fire Launcher manifest declares MAIN + HOME + DEFAULT at priority 50 (`P2-MAN-001`). The baseline preferred dump contains Fire as an ordinary User 0 HOME preferred record; no explicit persistent-preferred heading was observed (`P2-HOME-002`).

`set-home-activity Microsoft` produces a preferred record for Microsoft with `mAlways=true` in the mutation snapshot, but `resolve-activity` continues to output Fire priority 50 and the Home action resumes Fire (`P2-HOME-003`).

### Decision

`Strong evidence`: the effective result is currently explained by standard-looking candidate ranking combined with Fire’s manifest priority and the current preferred state. `Hypothesis`: an Amazon resolver-specific modification may still be involved; it has not been isolated from ordinary ranking.

### Settings, DeviceConfig, and Overlay

`Confirmed`: the Settings APK still contains `DefaultHomePicker`, `DefaultHomePreferenceController`, `default_home_settings.xml`, and a `config_show_default_home` resource, but the main `app_default_settings.xml` omits the `default_home` preference. The live Settings tests likewise showed no Home row in the Default apps page. This is a Settings UI/resource-level restriction, not proof of a PackageManager resolver patch (`P2-SET-001`).

`Confirmed observation`: the captured overlay list contains only internal cutout overlays and `com.android.systemui.theme.dark`; no Fire Launcher-specific overlay was observed (`P2-OVL-001`). This does not prove that no resource overlay exists in an unlisted partition or another build.

No DeviceConfig or Settings mutation was performed in this pass. The available evidence does not identify a single causal key, so changing arbitrary keys would not be a controlled test.

## 7. Home Key Flow

The inspected normal tablet path is:

```text
Home key
  -> PhoneWindowManager.handleShortPressOnHome()
  -> Amazon KeyPolicyManager hook
  -> PhoneWindowManager.launchHomeFromHotKey()
  -> startDockOrHome()
  -> ACTION_MAIN + CATEGORY_HOME
  -> ActivityManager/PackageManager resolver
  -> com.amazon.firelauncher/.Launcher
```

`KeyPolicyManagerCommon.launchHomeFromHotKey()` constructs a standard HOME intent and starts it as the current user. Amazon custom-home and custom-dock hooks exist, but the inspected normal branch does not directly name Fire Launcher. Existing ADB keyevent and explicit HOME tests both end at Fire. The physical hardware button has not been sampled, so equivalence is `Hypothesis` (`P2-KEY-001`).

The current evidence does not support “SystemUI directly starts Fire Launcher” for the inspected path. The SystemUI Fire reference found in `SGObserver` is used for foreground detection before a Smart Genie popup, not as a HOME launch (`P2-KEY-001`).

## 8. Mutation Test Results

No new mutation was required for the protected-component path. Existing controlled tests show:

| Test | Mutation | Result | Restore/persistence |
|---|---|---|---|
| `HOME-DEFAULT-T01` | Set Microsoft HOME | Command success; effective resolver remained Fire | Fire restore success; no reboot persistence check |
| `HOME-PREF-T17` | Set Microsoft HOME + keyevent | Microsoft preferred record visible; effective resolver and foreground Fire | Fire restore success; no reboot persistence check |
| `COMPONENT-T01` | Disable Fire HOME component | Protected exception, no state change | Final state matched before; no watchdog explanation |
| `COMPONENT-T02` | Same through `cmd package` | Same protected exception, no state change | Restore skipped after rejected request |

The new `capture_mutation_snapshot.sh` creates a read-only pre-state snapshot and restore template. It was not used to issue a new state-changing command.

## 9. Workaround Assessment

| Classification | Routes |
|---|---|
| `Disproved` | Fire package/component disable; effective `set-home-activity` Microsoft change |
| `Potentially viable` | An explicitly authorized API with a different policy boundary, after static proof and recovery plan |
| `Temporary` | Manual explicit start of a third-party launcher |
| `Only a redirect workaround` | Accessibility/foreground interception concepts; not a true HOME change |
| `Requires system UID` | Reading the protected deny-list content through a system-server diagnostic, if no OTA equivalent exists |
| `Requires Root` | Direct protected data extraction or framework/partition modifications unavailable through authorized ADB/OTA |
| `Unknown` | Settings, DeviceConfig, AppOps, Overlay, suspend/hide semantics, Amazon watchdog persistence |

No route is labeled `Viable` or `Persistent` at this stage.

## 10. Deep-System Operations Requiring Approval

No Level 3 operation was executed or is required for the current evidence set. The following remain explicitly out of scope without a separate approval report:

- Root/Root exploit or BootROM exploit.
- Bootloader unlock, fastboot/recovery/OTA sideload, downgrade, or rollback-index changes.
- Any write to boot, recovery, vbmeta, system, vendor, product, super, preloader, LK, seccfg, NVRAM, persist, or partition table.
- System remount read-write, SELinux/init/kernel changes.
- Factory reset, userdata erase, or partition formatting.

If exact deny-list content becomes impossible to obtain from matching OTA artifacts and requires privileged device access, the next report must include the requested operation, target data, compatibility, failure modes, data-loss/brick risks, rollback plan, and lower-risk alternatives. It must not be executed automatically.

## 11. Remaining Unknowns

| Unknown | Minimum next target |
|---|---|
| Literal presence of Fire Launcher in current deny-list | Authorized exact-build file/artifact content; preserve hash |
| Exact Amazon producer that last updated deny-list | Trace Arcus receiver/broadcast and matching build runtime logs |
| Whether Fire resolver selection differs from AOSP beyond priority | Compare Fire `chooseBestActivity`/preferred methods with AOSP smali/VDEX |
| Physical hardware Home equivalence | Manual unlocked physical-button capture with timestamped logcat |
| Persistent preferred activity after reboot | One controlled set-home test with full snapshot/restore and reboot, only if needed |
| Settings/DeviceConfig/Overlay control | Read-only key/resource map first; one-variable reversible test only after causal evidence |
| Suspend/hide/uninstall policy boundary | Static call-path proof and verified ADB recovery path before any Level 2 mutation |
| Amazon watchdog or service restoration | Static receiver/service mapping plus long, non-destructive observation |

## 12. Evidence Table

| Finding | Evidence ID | File / method | Confidence |
|---|---|---|---|
| Shell component mutation is rejected | `P2-RUN-001`, `P2-RUN-002` | T01/T02 command manifests and stderr | Confirmed |
| Rejection occurs before state mutation | `P2-STATE-001`, `P2-STATE-002` | Before/after package, resolver, activity, window dumps | Confirmed |
| Exact Fire OS gate | `P2-STATIC-001` | `PackageManagerService.setEnabledSetting`, `0x2d458e` | Confirmed |
| Vendor callback extension | `P2-STATIC-002`, `P2-STATIC-003` | `ProtectedPackages`, `VendorProtectedPackagesCallback` | Confirmed |
| Amazon shell deny-list logic | `P2-STATIC-004`, `P2-STATIC-005` | `ControlProtectedPackagesCallback`, `amazonpackagemanager_fosinit.xml` | Strong evidence |
| Deny-list storage/producer | `P2-STATIC-006`, `P2-STATIC-007` | `DenyListArcusHelper`, device file metadata | Strong evidence |
| Priority 50 source | `P2-MAN-001` | Fire Launcher `AndroidManifest.xml:316-330` | Confirmed |
| Third-party candidates remain visible | `P2-HOME-001` | `home_query_cmd.txt` | Confirmed |
| Fire preferred state observed | `P2-HOME-002` | `preferred_activities.txt` | Strong evidence |
| Preferred write not effective | `P2-HOME-003` | `HOME-PREF-T17` snapshots | Strong evidence |
| Normal Home path uses HOME intent | `P2-KEY-001` | PhoneWindowManager/KeyPolicyManager VDEX plus runtime tests | Strong evidence |
| Settings default-home row omitted | `P2-SET-001` | Settings `app_default_settings.xml`, default-home resources, live UI tests | Confirmed |
| No Fire Launcher-specific overlay observed | `P2-OVL-001` | `device/baseline/BASELINE-20260803-07/overlay_list.txt` | Confirmed observation |

## Appendix: key artifact hashes

| Artifact | SHA-256 |
|---|---|
| Fire OS services VDEX disassembly | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |
| Amazon FOS services VDEX disassembly | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| Amazon PackageManager `fosinit` | `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286` |
| Fire Launcher manifest | `ba88dc674466a2c4561e7258586ca31f739e8527153d81dc6cd2a262a3f2fdab` |
| HOME query baseline | `1be13029fed592ecfb838026e848c3f80e3201018d8b1d4c550d06f5ccaacbd8` |
| Preferred-activities baseline | `a680bc14902b1d7af9e219418dbfe5cc18ce01c28a39d22b498eb85fb290eece` |
| AOSP r61 PackageManagerService | `bb8d33fbb976c3463d932f65a679dafb2d541845b2989b63d07060d0db8ef179` |
| AOSP r61 ProtectedPackages | `fb64ec70c224f527890a28385eb163129a4f235fb8818cd42d31c69ec7cf4508` |
