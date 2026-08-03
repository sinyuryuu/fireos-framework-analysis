# Fire OS 7 Launcher Framework Analysis — Phase 1 Report

Status: `PHASE_1_PRELIMINARY_RESULT`  
Run date: 2026-08-03  
Device serial: `G001LT0511550CFT`  
Evidence rule: every conclusion below is labeled `Confirmed`, `Probable`, `Hypothesis` or `Disproved`.

## 1. Executive Summary

### 1.1 Where Fire Launcher is selected

The valid unlocked tests show the same result from Settings, Firefox and a Microsoft preferred-home state: the Home key reaches Fire Launcher. Earlier runs that appeared to leave Microsoft focused were collected with `mKeyguardShowing=true`; they are lock-screen observations and are not evidence that Microsoft bypasses the resolver.

`HOME-T14` and `HOME-T15` woke and dismissed keyguard before injecting `KEYCODE_HOME`; both resumed Fire. `HOME-T16` sent explicit HOME from unlocked Firefox and resumed Fire. `HOME-PREF-T17` retained a Microsoft preferred record, then sent `KEYCODE_HOME` from unlocked Firefox; Fire still resumed.

`Confirmed`: the tested HOME resolver returns `com.amazon.firelauncher/.Launcher`. The candidate's declared HOME activity priority is `50`; Microsoft Launcher is `0`, and Settings `FallbackHome` is `-1000`.

`Probable`: in the tested unlocked paths, Fire Launcher is selected by the standard PackageManager candidate-ranking path rather than by a SystemUI explicit launch. The framework VDEX contains the normal `PackageManagerService.chooseBestActivity()` priority comparison, and the corresponding logcat records ActivityManager starting `com.amazon.firelauncher/.Launcher` after a HOME intent.

### 1.2 Whether Amazon modified the Android framework

Confirmed: Amazon's tablet key-policy implementation is not only a no-op hook. TabletKeyPolicyManager.handleShortPressOnHome() obtains the foreground activity, calls AmazonActivityManager.checkKillAppGoingIntoBg(), and then calls HomeEventHandler.handleCustomHome(). The custom branch can broadcast com.amazon.tablet.action.CUSTOM_HOME to a foreground app only when that app advertises the required metadata/receiver and permission. The inspected branch does not name Fire Launcher as its target.

`Confirmed`: Amazon added system-server integration points. Android 9 `PhoneWindowManager.handleShortPressOnHome()` calls Amazon `KeyPolicyManager.handleShortPressOnHome()` before continuing. Amazon also registers `VendorPhoneWindowManagerCallback`, PackageManager protected-package callbacks and other framework callbacks through Fire OS configuration XML.

`Confirmed`: Amazon also adds `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()`, which gates visibility of Home tasks through the SELinux permission `amazon_policies:see_home_task` or an Android-signature check. This is a real framework policy modification, but the inspected callback does not start Fire Launcher.

`Hypothesis`: the Amazon Home hook may implement additional behavior for device-specific contexts. The captured unlocked normal path did not show that hook directly launching Fire Launcher, and the extracted callback implementation inspected so far does not contain a Fire Launcher component launch.

### 1.3 Why `pm disable-user` fails

`Confirmed`: the command is rejected synchronously by `PackageManagerService.setEnabledSetting()` with:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
```

The call reaches `ProtectedPackages.isPackageStateProtected()`, which consults vendor protected-package callbacks. Amazon registers `ControlProtectedPackagesCallback`; its extracted code protects a system app when the package is in Amazon's `PackageManagerDenyList` and the caller UID is `2000` (ADB shell). The package state therefore never changes; a watchdog is not required to explain this test.

### 1.4 Whether a no-root workaround was found

`Confirmed`: `cmd package set-home-activity com.microsoft.launcher/.Launcher` reports `Success` and writes a normal preferred activity record, but the resolver still selects Fire Launcher. The preferred record does not outrank Fire Launcher's priority-50 candidate.

`Probable`: no stable no-root default-home workaround has been identified on this build. A physical-button capture, exact-match OTA comparison and cross-version comparison remain pending.

## 2. Device and Firmware Identification

| Field | Value | Evidence |
|---|---|---|
| Model | `KFTRWI` | `device/baseline/BASELINE-20260803-02/device_properties.txt:297` |
| Product/device | `trona` | `device/baseline/BASELINE-20260803-02/device_properties.txt:293,298` |
| Android release/API | `9` / `28` | `device/baseline/BASELINE-20260803-02/device_properties.txt:258-259` |
| Fire OS build | `Fire OS 7.3.3.0` | `device/baseline/BASELINE-20260803-02/device_properties.txt:242` |
| Build ID | `PS7330.4104N` | `device/baseline/BASELINE-20260803-02/device_properties.txt:234-235` |
| Security patch | `2024-02-01` | `device/baseline/BASELINE-20260803-02/device_properties.txt:260` |
| Hardware | `mt8183` | `device/baseline/BASELINE-20260803-02/device_properties.txt:203,279` |
| Verified Boot | green; flash locked | `device/baseline/BASELINE-20260803-02/device_properties.txt:202,221` |
| Launcher package | `com.amazon.firelauncher` | package dump and HOME query |
| Launcher activity | `com.amazon.firelauncher/.Launcher` | `home_resolve_cmd.txt:1-2` |
| Launcher code path | `/system/priv-app/com.amazon.firelauncher` | `adb/baseline/BASELINE-20260803-02/package_com.amazon.firelauncher.txt:551-565` |
| Launcher version | `1.3.232663.0_82020310`, code `82020310` | `adb/baseline/BASELINE-20260803-02/package_com.amazon.firelauncher.txt:551-565` |

The baseline and artifact hashes are preserved in:

- `device/baseline/BASELINE-20260803-02/sha256sums.txt`
- `adb/baseline/BASELINE-20260803-02/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-01/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-02/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-03/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-06/sha256sums.txt`

The artifacts marked `ARTIFACT-*` in this phase were pulled from the device. An exact matching official OTA has not yet been acquired; OTA-dependent conclusions remain `Hypothesis` until that provenance is established.

## 3. Standard Android 9 HOME Flow

The device-derived Android 9 VDEX shows this relevant framework flow:

```text
Home key
  -> PhoneWindowManager.handleShortPressOnHome()
  -> PhoneWindowManager.launchHomeFromHotKey()
  -> PhoneWindowManager.startDockOrHome()
  -> startActivityAsUser(mHomeIntent, UserHandle.CURRENT)
  -> ActivityManager / ActivityStackSupervisor
  -> PackageManagerService.resolveIntentInternal()
  -> queryIntentActivitiesInternal()
  -> PackageManagerService.chooseBestActivity()
  -> selected HOME activity
```

Evidence:

- `decompiled/baksmali/vdexExtractor/services/disassembly.log:977415-977448` — `PhoneWindowManager.handleShortPressOnHome()` calls `mKeyPolicyManager.handleShortPressOnHome()` and, when it returns false, calls `launchHomeFromHotKey()`.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:988383-988465` — `startDockOrHome()` creates the Home intent, offers the vendor custom-dock callback, and otherwise calls `startActivityAsUser()` with `mHomeIntent`.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:951258-951309` — `resolveIntentInternal()` reaches query and candidate selection.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:934336-934420` — `chooseBestActivity()` compares candidate priority, preferred order and default status; only the equal-ranking path calls `findPreferredActivity()`.

The `chooseBestActivity()` control flow is important: when the top two candidates have different priorities, the method takes the ranking path; the preferred-activity lookup is reached only after the relevant priority/order/default comparisons are equal. This explains why a normal preferred record written for Microsoft Launcher did not replace Fire Launcher in this build.

## 4. Fire OS Tested Home Flow

For a tablet short press, the Amazon branch is:

TabletKeyPolicyManager.handleShortPressOnHome()
  -> getTopActivity()
  -> AmazonActivityManager.checkKillAppGoingIntoBg()
  -> HomeEventHandler.handleCustomHome()
       | custom receiver/permission present: broadcast CUSTOM_HOME and return 1
       | otherwise: return 0
  -> PhoneWindowManager continues to launchHomeFromHotKey()

This code is in decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:314232-314270 for TabletKeyPolicyManager and :141271-141328 for HomeEventHandler.

```text
ADB input keyevent 3
  -> Android input/policy path
  -> PhoneWindowManager.handleShortPressOnHome()
  -> Amazon KeyPolicyManager.handleShortPressOnHome()
       | returns true: custom handling (not observed in this run)
       | returns false: standard Android home path
  -> launchHomeFromHotKey()
  -> startDockOrHome()
  -> optional VendorPhoneWindowManagerCallback.callCustomDockOrHome()
  -> mHomeIntent / startActivityAsUser()
  -> ActivityManager resolver
  -> PackageManagerService.chooseBestActivity()
  -> com.amazon.firelauncher/.Launcher
```

`Confirmed`: the Amazon hook exists and is on the framework path.  
`Strong evidence`: for `HOME-T01`, ActivityManager logged the HOME start with UID 1000 and an explicit Fire Launcher component; the post-event activity/window state was Fire Launcher.  
`Confirmed`: for `HOME-T02`, an explicit `ACTION_MAIN + CATEGORY_HOME` command logged the same Fire Launcher component from UID 2000.  
`Hypothesis`: the physical hardware Home key is identical to this ADB-generated keyevent; it has not yet been manually sampled.

The current evidence does not support the claim that SystemUI directly launches Fire Launcher. SystemUI and Fire Launcher searches did not find a Fire Launcher Home-launch call, but the SystemUI APK also contains copied framework classes, so absence from that APK is not by itself proof of absence from system_server.

Earlier apparent exception: `HOME-PREF-T02` and `HOME-PREF-T03` were collected while the device was keyguard-locked; their snapshots show `mKeyguardShowing=true`. The controlled unlocked comparison `HOME-PREF-T17` shows the Microsoft preferred activity still present at `adb/launcher-tests/HOME-PREF-T17/after_target_preferred_activities.txt:8874-8883`, while `KEYCODE_HOME` starts Fire at `logcat_full.txt:1764-1774`. The earlier differential is therefore classified as a keyguard confounder, not as a resolver bypass.

## 5. Amazon Modifications Observed

| Layer | Observation | Status |
|---|---|---|
| PhoneWindowManager | Calls Amazon `KeyPolicyManager` before normal short-Home handling | Confirmed |
| PhoneWindowManager vendor callback | `startDockOrHome()` offers `callCustomDockOrHome()` and `callOnStartDockOrHome()` | Confirmed |
| KeyPolicyManager | `tabletkeypolicymanager_fosinit.xml` binds `TabletKeyPolicyManager` and `KeyInterceptorCallback` in `SYSTEMSERVER` | Confirmed |
| PackageManager / ProtectedPackages | Standard-looking protected-package gate calls vendor callbacks | Confirmed |
| Amazon package policy | `ControlProtectedPackagesCallback` protects deny-listed system packages for shell UID 2000 | Strong evidence |
| ActivityManager / ActivityStack | `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()` applies SELinux/signature policy to Home-task visibility | Confirmed code path; launch effect unproven |
| SystemUI | No direct Fire Launcher launch was found in focused decompiled search | Disproved for the inspected search; not a universal absence proof |
| Fire Launcher APK | Manifest declares the standard HOME activity; focused search found no Home-key interception or explicit HOME-launch logic | Strong evidence |
| Settings | `DefaultHomePreferenceController` and `DefaultHomePicker` exist; `config_show_default_home` controls the UI | Confirmed |
| Overlay | No Fire Launcher-specific overlay appeared in the device overlay list | Confirmed observation; OTA resource coverage pending |

Relevant Amazon configuration:

- `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24` registers `com.amazon.android.service.pm.ControlProtectedPackagesCallback` against `com.android.server.pm.VendorProtectedPackagesCallback`.
- `artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml:9-18` registers `TabletKeyPolicyManager` and `KeyInterceptorCallback` in system_server.
- `artifacts/amazon-services/amazonwindowmanager_fosinit.xml:9-18` registers Amazon WindowManager and PhoneWindowManager callback components.
- `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml` and `tabletlauncherhijackpreventer_fosinit.xml` register additional ActivityStack, ActivityManager, PackageManager and PermissionManager callbacks. The inspected LauncherHijackPreventer methods did not provide direct Fire Launcher launch evidence.

- decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:314232-314270 shows TabletKeyPolicyManager's short-Home branch and its HomeEventHandler call.
- decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:141271-141328 shows HomeEventHandler's receiver, permission and CUSTOM_HOME broadcast checks.

## 6. Package Protection Mechanism

### Runtime evidence

`adb/package-tests/PACKAGE-T01/disable_user.txt:1-14` records:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
at com.android.server.pm.PackageManagerService.setEnabledSetting(PackageManagerService.java:21128)
at com.android.server.pm.PackageManagerService.setApplicationEnabledSetting(PackageManagerService.java:21039)
```

Before, after-failure and final package snapshots all show User 0 as installed, enabled, not hidden, not suspended and not stopped: `adb/package-tests/PACKAGE-T01/{before,after_disable,final}_package.txt:825`.

### Static evidence

1. `PackageManagerService.setEnabledSetting()` calls `ProtectedPackages.isPackageStateProtected()` and constructs the exact `Cannot disable a protected package:` `SecurityException`: `decompiled/baksmali/vdexExtractor/services/disassembly.log:953377-953546`.
2. `ProtectedPackages.isPackageStateProtected()` delegates to `isProtectedPackage()`, which invokes `VendorProtectedPackagesCallback.callShouldProtectPackage()` with the Binder caller UID: `services/disassembly.log:505771-505837`.
3. `VendorProtectedPackagesCallback.callShouldProtectPackage()` ORs the results of registered callbacks: `services/disassembly.log:539225-539250`.
4. Amazon's `ControlProtectedPackagesCallback.shouldProtectPackage()` requires a system app, membership in the shared-preference deny list, and UID `2000`: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96999-97049`.
5. The callback reads the `DenyListKeyPackages` set from a device-protected `PackageManagerDenyList` preference file: `fosservices/disassembly.log:96950-96999`.

The device exposes `/data/system/PackageManagerDenyList`, but shell access to its contents was denied; the failed read is preserved in the artifact collection logs. Therefore:

- `Confirmed`: this Fire Launcher disable request is rejected at PackageManager protected-package enforcement.
- `Strong evidence`: Amazon's deny-list callback is the effective vendor extension that makes the package protected for shell UID 2000.
- `Hypothesis`: the exact deny-list file entry is the source of this package's membership; the file contents cannot be directly verified without elevated access.
- `Disproved`: a post-disable watchdog is the cause of this specific failure, because no state mutation occurred.

The package is a system/privileged package, but the captured flags do not show `PERSISTENT` or `CORE_APP`. “Privileged/system” and “protected from shell disable” are separate properties in this evidence set.

## 7. HOME and Package Test Matrix

| Test ID | Operation | Result | Status |
|---|---|---|---|
| `HOME-T01` | Prepare Settings; `input keyevent 3` | Fire Launcher became foreground; logcat shows HOME start | Confirmed |
| `HOME-T02` | `am start -a MAIN -c HOME` | Fire Launcher became foreground; logcat shows HOME start | Confirmed |
| `HOME-DEFAULT-T01` | Set Microsoft as home, inspect, restore Fire | Both set operations report `Success`; resolver remains Fire | Confirmed |
| `HOME-PREF-T01` | Set Microsoft, generate keyevent, inspect, restore Fire | Preferred record exists; keyevent still resolves to Fire | Confirmed |
| `PACKAGE-T01` | `pm disable-user --user 0 com.amazon.firelauncher` | Security exception; package state unchanged | Confirmed |
| `REBOOT-T01` | Reboot and capture | Package service was not ready for post snapshot | Timing-invalid; retained, not used |
| `REBOOT-T02` | Reboot, wait for ADB and PackageManager | Resolver returns Fire priority 50 after service readiness | Confirmed |

The scripts preserve command manifests, raw output, summary and SHA-256 files for each run. `REBOOT-T02/package_service_poll.tsv` shows the resolver becoming usable only after the temporary boot-time service-unavailable period.

Additional foreground matrix rows:

| Test ID | Starting foreground | Action | Result | Status |
|---|---|---|---|---|
| HOME-PREF-T02 | Microsoft Launcher; keyguard locked | ADB KEYCODE_HOME | Microsoft remained focused; `mKeyguardShowing=true` | Confirmed lock-screen observation; not resolver evidence |
| HOME-PREF-T03 | Microsoft Launcher; keyguard locked | Explicit ACTION_MAIN + CATEGORY_HOME | Fire Launcher start was logged, but the comparison is keyguard-confounded | Confirmed log; not a valid unlocked differential |
| HOME-T14 | Settings; keyguard dismissed | ADB KEYCODE_HOME | Fire Launcher resumed; `mKeyguardShowing=false` | Confirmed |
| HOME-T15 | Firefox; keyguard dismissed | ADB KEYCODE_HOME | Fire Launcher resumed; `mKeyguardShowing=false` | Confirmed |
| HOME-T16 | Firefox; keyguard dismissed | Explicit ACTION_MAIN + CATEGORY_HOME | Fire Launcher resumed; `mKeyguardShowing=false` | Confirmed |
| HOME-PREF-T17 | Firefox; Microsoft preferred record; keyguard dismissed | ADB KEYCODE_HOME | Fire Launcher resumed while Microsoft preferred record remained | Confirmed |

## 8. Settings and Overlay

`Confirmed`: the Settings APK still contains the standard default-home UI path:

- `decompiled/jadx/settings/sources/com/android/settings/applications/defaultapps/DefaultHomePreferenceController.java:38-44` reads `R.bool.config_show_default_home` and calls `getHomeActivities()`.
- `decompiled/jadx/settings/sources/com/android/settings/applications/defaultapps/DefaultHomePicker.java:30,69-90` loads `R.xml.default_home_settings`, enumerates home activities and calls `replacePreferredActivity()`.
- `decompiled/jadx/settings/resources/res/xml/default_home_settings.xml` and `decompiled/jadx/settings/resources/res/values/bools.xml:36` contain the corresponding default-home resources.

`Confirmed observation`: the current `cmd overlay list` output does not show a Fire Launcher-specific overlay. A complete OTA resource comparison is still required before concluding that no product overlay changes the UI on every boot variant.

## 9. Workaround Assessment

| Route | Assessment | Status |
|---|---|---|
| Standard `set-home-activity` | Preferred record is accepted but loses to Fire's priority-50 candidate | Not effective on this build |
| Physical/default-home Settings UI | UI code exists; device behavior after a manual UI selection is not yet tested | Hypothesis |
| `pm disable-user` | Directly blocked by protected-package enforcement | Not available to shell |
| Repeated activity launch / delayed redirect | Could simulate a launcher, but would not change the HOME default | Not tested; not a real default-home workaround |
| Device Owner | Requires a separate authorized provisioning experiment and commonly resets user state | Not attempted |
| Root/framework modification | Outside phase-1 scope | Not attempted |

No command that clears package data, changes settings, provisions Device Owner, sideloads, flashes or factory-resets the device was executed.

## 10. Remaining Unknowns

- Does a manually pressed physical Home button produce the same callback and ActivityManager trace as `input keyevent 3`?
- Does `KeyInterceptorCallback` or another Amazon callback return `true` in any special mode, user state, keyguard state or foreground package context? The ordinary unlocked Firefox/Settings paths continued to the standard resolver.
- Does any Amazon service repopulate or synchronize the deny list after boot?
- What exact Fire OS build introduced the priority/protection policy?
- Does the exact official OTA contain additional overlays or framework code absent from device-readable artifacts?
- Are there other users/profile states in which the preferred-home path behaves differently?
- Does the current foreground package advertise Amazon's CUSTOM_HOME metadata/receiver and therefore consume the custom branch?

## 11. Reproduction Steps

Use the existing scripts with the known serial. Each live state-changing script requires an explicit approval phrase and has a `--dry-run` mode.

```sh
tools/scripts/collect_device_baseline.sh \
  --serial G001LT0511550CFT \
  --output-dir . \
  --run-id BASELINE-REPRO

tools/scripts/capture_home_event.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-T90 \
  --duration 5 \
  --output adb/home-key-tests/HOME-T90 \
  --prepare org.mozilla.firefox/.App \
  --wake --dismiss-keyguard \
  --action keyevent \
  --approve-state-change

tools/scripts/test_home_activity.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-T91 \
  --target com.microsoft.launcher/.Launcher \
  --restore com.amazon.firelauncher/.Launcher \
  --output adb/launcher-tests/HOME-T91 \
  --approve-state-change

tools/scripts/test_package_disable.sh \
  --serial G001LT0511550CFT \
  --package com.amazon.firelauncher \
  --user 0 \
  --test-id PACKAGE-REPRO-T01 \
  --approve-state-change
```

Do not reuse an existing output directory; scripts preserve raw files and reject collisions where configured.

## 12. Appendix: Main Artifact References

### APK hashes

Microsoft Launcher artifact pulled for the foreground differential test: ba0f400ab36aabb873311c7b07b242615b67b070c6b304ac7b1371146c406e30. The source and pull manifest are ARTIFACT-20260803-07.

The raw values are in `firmware/manifests/ARTIFACT-20260803-01/sha256sums.txt`:

- Fire Launcher: `601c510df94ddf2701ef8eb662ad565a5108688e562ca29fa56c1b14289b4ddf`
- SystemUI: `9c75f1657c9e52b9f66287c1ff92a2dfc50a135d86de149cdb4ae2bb127cc4ee`
- Settings: `034e39c02f80feba3974e76079fdab6af03ca67ad53fde0b46b07d493ad8ec86`
- framework-res: `a8ac705f290b4aaf432e25d680b3a022a04091e9d5d3f5fcf4e5ac2234964e99`

### Framework/service hashes

The raw values are in `firmware/manifests/ARTIFACT-20260803-02/sha256sums.txt`:

- `services.vdex`: `06cb78333df89d97da741b921d7c62680b4a931aade45b83581b39d498cdbdc4`
- `fosservices.vdex`: `584673e398894936dcba7a79c07d1f5abda7f2d03b3e36bd1792f764dd4dcffa`
- `boot-fosframework.vdex`: `d91bb12295e9ac55da414347643ff0e880e431eedc675f0944ad3f30cae06714`
- `boot-framework.vdex`: `9a160fc8d64b147beb3c19a16bbf40a9ccc2007c3d595092d15ae4437dfc6404`

### Tooling and evidence directories

- Dynamic raw evidence: `adb/home-key-tests/`, `adb/launcher-tests/`, `adb/package-tests/`, `adb/logs/`
- Device baseline: `device/baseline/BASELINE-20260803-02/`
- Decompiled APKs: `decompiled/jadx/` (JADX completed for the readable APKs)
- VDEX disassembly: `decompiled/baksmali/vdexExtractor/`
- HOME reference index: `diff/reports/home-reference-index.tsv`
- Initial call graph: `output/call-graphs/home-flow-phase1.txt`

`tools/tool_versions.txt` records that Java, apktool, baksmali, smali and several image/OTA utilities were unavailable in this environment. Accordingly, this phase does not claim apktool output or exact OTA extraction; the framework findings use device-pulled VDEX/ODEX disassembly and JADX resources/source where available.

---

Generated evidence-index SHA-256: [70571aff11f01105af43f736f4190c3e837bc28302f5c87d9a2dc1096719369a]
