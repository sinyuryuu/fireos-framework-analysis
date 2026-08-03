# Fire OS 7 Launcher Framework Analysis — Phase 1 Report

Status: `PHASE_1_PRELIMINARY_RESULT`  
Run date: 2026-08-03  
Device serial: `G001LT0511550CFT`  
Evidence rule: every conclusion below is labeled `Confirmed`, `Probable`, `Hypothesis` or `Disproved`.

## 1. Executive Summary

### 1.1 Where Fire Launcher is selected

The valid unlocked tests show the same result from Settings, Firefox and a Microsoft preferred-home state: the Home key reaches Fire Launcher. Earlier runs that appeared to leave Microsoft focused were collected with `mKeyguardShowing=true`; they are lock-screen observations and are not evidence that Microsoft bypasses the resolver.

`HOME-T14` and `HOME-T15` woke and dismissed keyguard before injecting `KEYCODE_HOME`; both resumed Fire. `HOME-T16` sent explicit HOME from unlocked Firefox and resumed Fire. `HOME-PREF-T17` retained a Microsoft preferred record, then sent `KEYCODE_HOME` from unlocked Firefox; Fire still resumed. The stronger foreground controls `HOME-T18` and `HOME-T19` first launched Microsoft Launcher while unlocked, then produced Fire for both `KEYCODE_HOME` and an explicit HOME Intent.

`Confirmed`: the tested HOME resolver returns `com.amazon.firelauncher/.Launcher`. The candidate's declared HOME activity priority is `50`; Microsoft Launcher is `0`, and Settings `FallbackHome` is `-1000`.

`Probable`: in the tested unlocked paths, Fire Launcher is selected by the standard PackageManager candidate-ranking path rather than by a SystemUI explicit launch. The framework VDEX contains the normal `PackageManagerService.chooseBestActivity()` priority comparison, and the corresponding logcat records ActivityManager starting `com.amazon.firelauncher/.Launcher` after a HOME intent.

### 1.2 Whether Amazon modified the Android framework

Confirmed: Amazon's tablet key-policy implementation is not only a no-op hook. TabletKeyPolicyManager.handleShortPressOnHome() obtains the foreground activity, calls AmazonActivityManager.checkKillAppGoingIntoBg(), and then calls HomeEventHandler.handleCustomHome(). The custom branch can broadcast com.amazon.tablet.action.CUSTOM_HOME to a foreground app only when that app advertises the required metadata/receiver and permission. The inspected branch does not name Fire Launcher as its target.

`Confirmed`: Amazon added system-server integration points. Android 9 `PhoneWindowManager.handleShortPressOnHome()` calls Amazon `KeyPolicyManager.handleShortPressOnHome()` before continuing. Amazon also registers `VendorPhoneWindowManagerCallback`, PackageManager protected-package callbacks and other framework callbacks through Fire OS configuration XML.

`Confirmed`: Amazon also adds `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()`, which gates visibility of Home tasks through the SELinux permission `amazon_policies:see_home_task` or an Android-signature check. This is a real framework policy modification, but the inspected callback does not start Fire Launcher.

`Confirmed code path; not a Fire Launcher path`: Amazon also ships `AlexaModeSwitchManagerPhoneWindowManagerCallback.startCustomDockOrHome(Context)`. Its `launchEchoShowHome()` branch calls `getMode()`, and only for mode `1` obtains `HomeIntentProvider.getMultimodalHomeIntent()` and calls `Context.startActivity(Intent)`; the inspected code contains no Fire Launcher component target (`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:196259-196277,196362-196368`). A read-only probe found a service-list entry but `dumpsys`/Binder access was unavailable and `settings get secure mss_mode` returned `null`, so activation of that branch was not inferred.

`Hypothesis`: the Amazon Home hook may implement additional behavior for other device-specific contexts. The captured unlocked normal path did not show that hook directly launching Fire Launcher, and the extracted callback implementations inspected so far do not contain a Fire Launcher component launch.

### 1.3 Why `pm disable-user` fails

`Confirmed`: the command is rejected synchronously by `PackageManagerService.setEnabledSetting()` with:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
```

The call reaches `ProtectedPackages.isPackageStateProtected()`, which consults vendor protected-package callbacks. Amazon registers `ControlProtectedPackagesCallback`; its extracted code protects a system app when the package is in Amazon's `PackageManagerDenyList` and the caller UID is `2000` (ADB shell). The package state therefore never changes; a watchdog is not required to explain this test.

### 1.4 Whether a no-root workaround was found

`Confirmed`: `cmd package set-home-activity com.microsoft.launcher/.Launcher` reports `Success` and writes a normal preferred activity record, but the resolver still selects Fire Launcher. The preferred record does not outrank Fire Launcher's priority-50 candidate.

`Confirmed`: the main Settings Default apps page does not expose a Home-app row on this build. The installed Settings XML omits the `default_home` preference that is present in both the official Android 9 r1 and r61 AOSP references; `HOME-T21` independently shows the same omission in the live UI.

`Confirmed`: Fire Launcher's App info page still exposes a `Home app: Yes` row, but `HOME-T23` shows that tapping it only opens the Settings Default apps page, which still has no Home row. No launcher selection or default-setting write was performed.

`Probable`: no stable no-root default-home workaround has been identified on this build. A physical-button capture and exact-match OTA comparison remain pending; an adjacent official PS7331 OTA and two AOSP Android 9 references are available as explicitly version-mismatched/reference-only material.

## 2. Device and Firmware Identification

| Field | Value | Evidence |
|---|---|---|
| Model | `KFTRWI` | `device/baseline/BASELINE-20260803-04/device_properties.txt:297` |
| Product/device | `trona` | `device/baseline/BASELINE-20260803-04/device_properties.txt:293,298` |
| Android release/API | `9` / `28` | `device/baseline/BASELINE-20260803-04/device_properties.txt:258-259` |
| Fire OS build | `Fire OS 7.3.3.0` | `device/baseline/BASELINE-20260803-04/device_properties.txt:242` |
| Build ID | `PS7330.4104N` | `device/baseline/BASELINE-20260803-04/device_properties.txt:234-235` |
| Security patch | `2024-02-01` | `device/baseline/BASELINE-20260803-04/device_properties.txt:260` |
| Hardware | `mt8183` | `device/baseline/BASELINE-20260803-04/device_properties.txt:203,279` |
| Verified Boot | green; flash locked | `device/baseline/BASELINE-20260803-04/device_properties.txt:202,221` |
| Launcher package | `com.amazon.firelauncher` | package dump and HOME query |
| Launcher activity | `com.amazon.firelauncher/.Launcher` | `home_resolve_cmd.txt:1-2` |
| Launcher code path | `/system/priv-app/com.amazon.firelauncher` | `adb/baseline/BASELINE-20260803-04/package_com.amazon.firelauncher.txt:551-565` |
| Launcher version | `1.3.232663.0_82020310`, code `82020310` | `adb/baseline/BASELINE-20260803-04/package_com.amazon.firelauncher.txt:551-565` |

The baseline and artifact hashes are preserved in:

- `device/baseline/BASELINE-20260803-02/sha256sums.txt`
- `adb/baseline/BASELINE-20260803-02/sha256sums.txt`
- `device/baseline/BASELINE-20260803-04/sha256sums.txt`
- `adb/baseline/BASELINE-20260803-04/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-01/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-02/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-03/sha256sums.txt`
- `firmware/manifests/ARTIFACT-20260803-06/sha256sums.txt`

The artifacts marked `ARTIFACT-*` in this phase were pulled from the device. The downloaded official PS7331 OTA is recorded as `VERSION_MISMATCH` because the device is PS7330.4104N; it is used only for adjacent-version and extraction-pipeline validation. Conclusions about the installed build remain device-derived unless explicitly labeled otherwise.

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

The AOSP Android 9 reference files provide the corresponding baseline control points: `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java:1861-1876,4384-4450,7941-7986` and `.../pm/PackageManagerService.java:6149-6180,6306-6380,20712`; the r61 copies are retained for tag comparison. These references establish the standard flow and protected-package locations, but a source-level difference alone is not treated as an Amazon patch.

The enhanced structural comparison outputs are `diff/reports/aosp-r1-vs-fireos-jadx-phase3/` and `diff/reports/aosp-r61-vs-fireos-jadx-phase3/`. Each contains `class_similarity.csv`, `method_signature_diff.csv`, `confidence_score.txt`, a manual-review queue and SHA-256 manifest. The reported score is only a class-matching aid; it is deliberately not a patch-confidence claim.

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
       | Alexa mode callback: mode=1 -> multimodal Home Intent (not Fire)
       | otherwise: false / continue
  -> mHomeIntent / startActivityAsUser()
  -> ActivityManager resolver
  -> PackageManagerService.chooseBestActivity()
  -> com.amazon.firelauncher/.Launcher
```

`Confirmed`: the Amazon hook exists and is on the framework path.  
`Strong evidence`: for `HOME-T01`, ActivityManager logged the HOME start with UID 1000 and an explicit Fire Launcher component; the post-event activity/window state was Fire Launcher.  
`Confirmed`: for `HOME-T02`, an explicit `ACTION_MAIN + CATEGORY_HOME` command logged the same Fire Launcher component from UID 2000.  
`Confirmed`: `HOME-T18` placed Microsoft Launcher in the unlocked foreground and then `KEYCODE_HOME` produced Fire; `HOME-T19` placed Microsoft Launcher in the unlocked foreground and then an explicit HOME Intent produced Fire. Fresh logcat shows the Fire start in both cases.  
`Hypothesis`: the physical hardware Home key is identical to this ADB-generated keyevent; it has not yet been manually sampled.

The current evidence does not support the claim that SystemUI directly launches Fire Launcher. `decompiled/jadx/systemui/sources/com/amazon/systemui/SGObserver.java:162-170` does reference `com.amazon.firelauncher.Launcher`, but only to detect the current foreground task before launching the explicit Smart Genie popup `com.amazon.smartgenie.ui.EducationalPopupActivity`. The focused search found no Fire Launcher Home-launch call. Because the SystemUI APK also contains copied framework classes, this remains a bounded negative result rather than proof that no other component can launch Fire Launcher. See `findings/systemui-launch-search.md`.

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
| PhoneWindowManager vendor callback | `AlexaModeSwitchManagerPhoneWindowManagerCallback` can directly start a multimodal Home Intent only when mode is `1`; no Fire Launcher target was found | Confirmed code path; activation not established |
| SystemUI | `SGObserver` observes Fire Launcher and launches Smart Genie; no direct Fire Launcher Home launch was found in the inspected path | Confirmed observation; direct SystemUI Home launch disproved for inspected path |
| Fire Launcher APK | Manifest declares the standard HOME activity; focused search found no Home-key interception or explicit HOME-launch logic | Strong evidence |
| Settings | Default-home controller/picker code and resources remain, but the main `app_default_settings.xml` omits the `default_home` preference; live Default apps UI has no Home row | Confirmed |
| Overlay | No Fire Launcher-specific overlay appeared in the device overlay list | Confirmed observation; OTA resource coverage pending |

Relevant Amazon configuration:

- `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24` registers `com.amazon.android.service.pm.ControlProtectedPackagesCallback` against `com.android.server.pm.VendorProtectedPackagesCallback`.
- `artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml:9-18` registers `TabletKeyPolicyManager` and `KeyInterceptorCallback` in system_server.
- `artifacts/amazon-services/amazonwindowmanager_fosinit.xml:9-18` registers Amazon WindowManager and PhoneWindowManager callback components.
- `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml` and `tabletlauncherhijackpreventer_fosinit.xml` register additional ActivityStack, ActivityManager, PackageManager and PermissionManager callbacks. The inspected LauncherHijackPreventer methods did not provide direct Fire Launcher launch evidence.

- decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:314232-314270 shows TabletKeyPolicyManager's short-Home branch and its HomeEventHandler call.
- decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:141271-141328 shows HomeEventHandler's receiver, permission and CUSTOM_HOME broadcast checks.
- decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:196259-196277,196362-196368 shows the conditional Alexa multimodal-Home callback; `adb/probes/ALEXA-MODE-T01/` preserves its read-only service/settings probes.

## 6. Package Protection Mechanism

### Runtime evidence

`adb/package-tests/PACKAGE-T01/disable_user.txt:1-14`, `PACKAGE-T03/disable_user.txt:1-14` and `PACKAGE-T05/disable_user.txt:1-14` record:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
at com.android.server.pm.PackageManagerService.setEnabledSetting(PackageManagerService.java:21128)
at com.android.server.pm.PackageManagerService.setApplicationEnabledSetting(PackageManagerService.java:21039)
```

Before, after-failure and final package snapshots all show User 0 as installed, enabled, not hidden, not suspended and not stopped: `adb/package-tests/PACKAGE-T01/{before,after_disable,final}_package.txt:825`.

The control test `PACKAGE-T02` disabled Microsoft Launcher successfully (`disable_user.txt:1`, state `enabled=3` in `after_disable_package.txt`) and restored it to `enabled=0` in `final_package.txt`. This disproves a blanket rule that ADB shell UID cannot change any package state. `PACKAGE-T05` used `cmd package disable-user` and reached the same protected-package exception and `PackageManagerService.setEnabledSetting()` stack as the `pm` invocation; the earlier `PACKAGE-T04` used the invalid `cmd disable-user` alias and is retained as a command-validation artifact, not causal evidence.

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

Final read-only verification after all tests: `adb/baseline/BASELINE-20260803-04/home_resolve_cmd.txt:1-2` returns Fire priority 50; `device/baseline/BASELINE-20260803-04` and `adb/baseline/BASELINE-20260803-04` hash manifests pass. A live final read-only check reports `com.amazon.firelauncher/.Launcher` as `ResumedActivity` and as the `mFocusedApp` token; the status bar is the transient `mCurrentFocus` window.

## 7. HOME and Package Test Matrix

| Test ID | Operation | Result | Status |
|---|---|---|---|
| `HOME-T01` | Prepare Settings; `input keyevent 3` | Fire Launcher became foreground; logcat shows HOME start | Confirmed |
| `HOME-T02` | `am start -a MAIN -c HOME` | Fire Launcher became foreground; logcat shows HOME start | Confirmed |
| `HOME-DEFAULT-T01` | Set Microsoft as home, inspect, restore Fire | Both set operations report `Success`; resolver remains Fire | Confirmed |
| `HOME-PREF-T01` | Set Microsoft, generate keyevent, inspect, restore Fire | Preferred record exists; keyevent still resolves to Fire | Confirmed |
| `PACKAGE-T01` | `pm disable-user --user 0 com.amazon.firelauncher` | Security exception; package state unchanged | Confirmed |
| `PACKAGE-T02` | Control: disable/restore Microsoft Launcher with `pm` | Disable succeeds (`enabled=3`), restore returns `enabled=0` | Confirmed; shell blanket restriction disproved |
| `PACKAGE-T03` | `pm disable-user --user 0 com.amazon.firelauncher` | Security exception; package state unchanged | Confirmed |
| `PACKAGE-T04` | Initial invalid `cmd disable-user` invocation | `cmd` reports missing service; not a valid package command | Disqualified command-validation artifact |
| `PACKAGE-T05` | `cmd package disable-user --user 0 com.amazon.firelauncher` | Same protected-package exception and unchanged state | Confirmed |
| `REBOOT-T01` | Reboot and capture | Package service was not ready for post snapshot | Timing-invalid; retained, not used |
| `REBOOT-T02` | Reboot, wait for ADB and PackageManager | Resolver returns Fire priority 50 after service readiness | Confirmed |
| `REBOOT-T03` | Reboot, poll resolver, capture after service ready | FallbackHome appeared during boot; resolver became Fire and Fire remained foreground | Confirmed |

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
| HOME-T18 | Microsoft Launcher directly foregrounded; keyguard dismissed | ADB KEYCODE_HOME | Fresh logcat and after snapshots show Fire Launcher | Confirmed |
| HOME-T19 | Microsoft Launcher directly foregrounded; keyguard dismissed | Explicit ACTION_MAIN + CATEGORY_HOME | Fresh logcat and after snapshots show Fire Launcher | Confirmed |
| HOME-T20 | Open `android.settings.HOME_SETTINGS`; restore Home | Read-only Settings activity/UI probe | `Settings$AdvancedAppsActivity` opens; Fire restored; first UI-dump transport was invalid, retained as a tooling artifact | Confirmed activity result; UI dump not used |
| HOME-T21 | Open `android.settings.HOME_SETTINGS`; restore Home | Read-only UI hierarchy capture | Default apps page shows Assistant, Browser and Link rows, but no Home-app row | Confirmed |
| HOME-T22 | Open Fire Launcher App info; restore Home | Read-only App info/UI probe | App info shows `Home app` / `ホームアプリ` with summary `Yes` / `はい` | Confirmed |
| HOME-T23 | Tap only App info `Home app` row; restore Home | Read-only foreground/navigation probe | Opens `com.android.settings/.SubSettings` Default apps page; no Home-app row or launcher picker appears | Confirmed |

## 8. Settings and Overlay

`Confirmed`: the installed Settings APK retains the default-home implementation pieces, but removes the main entry from the Default apps screen:

- `decompiled/jadx/settings/sources/com/android/settings/applications/DefaultAppSettings.java:79-93` still adds `DefaultHomePreferenceController`.
- `decompiled/jadx/settings/sources/com/android/settings/applications/defaultapps/DefaultHomePreferenceController.java:33-48` still exposes key `default_home`, reads `config_show_default_home` and queries `getHomeActivities()`.
- `decompiled/jadx/settings/sources/com/android/settings/applications/defaultapps/DefaultHomePicker.java:30,69-90` still loads `default_home_settings`, enumerates HOME activities and calls `replacePreferredActivity()` if a candidate is selected.
- `decompiled/jadx/settings/resources/res/xml/default_home_settings.xml` and `decompiled/jadx/settings/resources/res/values/bools.xml:36` still contain the secondary picker resources; the installed boolean is `true`, so a false resource flag is not the reason the row is absent.
- `decompiled/jadx/settings/resources/res/xml/app_default_settings.xml:1-65` contains no `default_home` preference. By contrast, official AOSP Android 9 r1 and r61 both contain the `GearPreference` block at `aosp/android-9/android-9.0.0_r1/platform/packages/apps/Settings/res/xml/app_default_settings.xml:38-42` and the corresponding r61 path.

`Confirmed` dynamic UI evidence:

- `HOME-T21` (`adb/home-settings-tests/HOME-T21/settings_ui.xml`) opens `com.android.settings/.Settings$AdvancedAppsActivity` and shows the Default apps page without a Home row.
- `HOME-T22` (`adb/home-settings-tests/HOME-T22/app_info_ui.xml`) shows Fire Launcher's App info `Home app` row with summary `Yes` (`ホームアプリ` / `はい` in the device locale).
- `HOME-T23` (`adb/home-settings-tests/HOME-T23/after_home_row_tap_activity.txt:90,210` and `after_tap_ui.xml`) shows the row navigating to `com.android.settings/.SubSettings` with the same Default apps page and no Home row. The script never selected a candidate, and the final snapshot restored Fire Launcher.

The reproducible static/UI comparison, including input hashes, is `output/tables/settings-home-ui-analysis-20260803-05.md`, generated by `tools/scripts/analyze_settings_home_ui.py`.

The static route explains the runtime result: `DefaultHomeShortcutPreferenceController` is registered by `AppInfoDashboardFragment` at `decompiled/jadx/settings/sources/com/android/settings/applications/appinfo/AppInfoDashboardFragment.java:192-197`; its base controller handles the `default_home` click by launching `DefaultAppSettings` at `decompiled/jadx/settings/sources/com/android/settings/applications/appinfo/DefaultAppShortcutPreferenceControllerBase.java:41-48`. Since the installed `app_default_settings.xml` lacks the matching preference, the navigation ends at a page with no Home selector.

`Confirmed observation`: the current `cmd overlay list` output does not show a Fire Launcher-specific overlay. The adjacent PS7331 OTA was extracted and its selected framework/APK/VDEX artifacts were indexed, but it is `VERSION_MISMATCH`; a complete exact-build resource comparison is still required before concluding that no product overlay changes the UI on every boot variant.

## 9. Workaround Assessment

| Route | Assessment | Status |
|---|---|---|
| Standard `set-home-activity` | Preferred record is accepted but loses to Fire's priority-50 candidate | Not effective on this build |
| Physical/default-home Settings UI | Main Default apps page has no Home row; Fire App info row only returns to that page | Confirmed; no selector exposed by tested UI route |
| `pm disable-user` / `cmd package disable-user` | Directly blocked by protected-package enforcement for Fire; Microsoft control succeeds | Not available for Fire to shell |
| Repeated activity launch / delayed redirect | Could simulate a launcher, but would not change the HOME default | Not tested; not a real default-home workaround |
| Device Owner | Requires a separate authorized provisioning experiment and commonly resets user state | Not attempted |
| Root/framework modification | Outside phase-1 scope | Not attempted |

No command that clears package data, changes settings, provisions Device Owner, sideloads, flashes or factory-resets the device was executed.

## 10. Remaining Unknowns

- Does a manually pressed physical Home button produce the same callback and ActivityManager trace as `input keyevent 3`?
- Does `KeyInterceptorCallback` or another Amazon callback return `true` in any special mode, user state, keyguard state or foreground package context? The ordinary unlocked Firefox/Settings paths continued to the standard resolver.
- Does any Amazon service repopulate or synchronize the deny list after boot?
- What exact Fire OS build introduced the priority/protection policy?
- Does an exact official OTA for `PS7330.4104N` contain additional overlays or framework code absent from device-readable artifacts? The acquired PS7331 OTA cannot answer this for the installed build.
- Are there other users/profile states in which the preferred-home path behaves differently?
- Does any alternate Settings entry point expose `DefaultHomePicker` directly, or is the retained picker code unreachable because the main preference is removed? The tested App info route only returns to `DefaultAppSettings`.
- Does the current foreground package advertise Amazon's CUSTOM_HOME metadata/receiver and therefore consume the custom branch?
- Is `alexa_modeswitch` intentionally hidden from shell despite appearing in `service list`, and what mode does the system-server client observe at runtime? The current read-only probe returned `null` for `mss_mode` and no shell-readable Binder/dumpsys result.

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
  --command pm \
  --output adb/package-tests/PACKAGE-REPRO-T01 \
  --approve-state-change

tools/scripts/probe_alexa_mode.sh \
  --serial G001LT0511550CFT \
  --output adb/probes/ALEXA-MODE-REPRO
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
- Adjacent official OTA provenance and extraction: `firmware/manifests/OTA-20260803-01/`, `firmware/extracted/PS7331/`
- AOSP Android 9 references: `aosp/android-9/`
- SystemUI launch-reference finding: `findings/systemui-launch-search.md`
- AOSP structural comparison: `diff/reports/aosp-r1-vs-fireos-jadx-phase3/`, `diff/reports/aosp-r61-vs-fireos-jadx-phase3/`

`tools/tool_versions.txt` records the original environment inventory; `tools/tool_versions.phase2.txt` records the follow-up inventory, and `tools/tool_versions.phase2-tools.txt` additionally records the explicit Brotli, debugfs and vdexExtractor paths used for OTA analysis. This phase does not claim an exact-match OTA. The framework findings for the installed build use device-pulled VDEX/ODEX disassembly and JADX resources/source; PS7331 outputs are explicitly adjacent-version references.

---

Generated evidence-index SHA-256: [154e77f41e8af9b1ca4291d71ef25bcd0fec913d094aaedff8114d070093f9aa]
