# Home Flow

The Amazon tablet-specific short-Home branch is confirmed in the extracted Amazon services code: TabletKeyPolicyManager calls getTopActivity(), checkKillAppGoingIntoBg(), and HomeEventHandler.handleCustomHome(). HomeEventHandler only consumes the event when the foreground app exposes the expected custom receiver and permission; otherwise the method returns 0 and PhoneWindowManager continues with the normal Home path. See decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:314232-314270 and :141271-141328.

Status: `PHASE_1_PRELIMINARY_RESULT`.

## Evidence-backed flow

```text
input keyevent 3
      |
      v
PhoneWindowManager.handleShortPressOnHome()
      |
      +--> Amazon KeyPolicyManager.handleShortPressOnHome()
      |       |
      |       +--> true: custom path (not observed)
      |       +--> false: continue
      |
      v
PhoneWindowManager.launchHomeFromHotKey()
      |
      v
PhoneWindowManager.startDockOrHome()
      |
      +--> VendorPhoneWindowManagerCallback.callCustomDockOrHome()
      |       |
      |       +--> AlexaModeSwitchManagerPhoneWindowManagerCallback
      |       |       +--> mode=1: getMultimodalHomeIntent(); startActivity()
      |       |       +--> otherwise: false / continue
      |       +--> other custom path: not observed
      |
      v
startActivityAsUser(mHomeIntent, UserHandle.CURRENT)
      |
      v
ActivityManager / ActivityStackSupervisor
      |
      v
PackageManagerService.resolveIntentInternal()
      |
      v
PackageManagerService.chooseBestActivity()
      |
      +--> Fire Launcher priority 50
      +--> Microsoft Launcher priority 0
      +--> Settings FallbackHome priority -1000
      |
      v
com.amazon.firelauncher/.Launcher
```

The framework positions and callback branches are in `decompiled/baksmali/vdexExtractor/services/disassembly.log:977415-977448` and `:988383-988465`. Resolver and ranking positions are in `:951258-951309` and `:934336-934420`.

## Dynamic confirmation

- `HOME-T01`: `adb/home-key-tests/HOME-T01/logcat_full.txt:2747` records ActivityManager starting a HOME intent with `cmp=com.amazon.firelauncher/.Launcher` after `input keyevent 3`.
- `HOME-T02`: `adb/home-key-tests/HOME-T02/logcat_full.txt:2925` records the same Fire component after explicit `ACTION_MAIN + CATEGORY_HOME`.
- `HOME-PREF-T01`: `adb/launcher-tests/HOME-PREF-T01/logcat_full.txt:3204-3222` records Fire after a Microsoft preferred-home record was written.
- `HOME-T14`: `adb/home-key-tests/HOME-T14/after_activity_activities.txt:183-190` shows Fire resumed with `mKeyguardShowing=false`; `logcat_full.txt:1389-1403` records the HOME start and resumed activity.
- `HOME-T15`: `adb/home-key-tests/HOME-T15/after_activity_activities.txt:183-190` shows the same result from Firefox; `logcat_full.txt:2594-2606` records Fire.
- `HOME-T16`: `adb/home-key-tests/HOME-T16/after_activity_activities.txt:183-190` shows explicit HOME from unlocked Firefox resumed Fire; `logcat_full.txt:1752-1763` records the start.
- `HOME-PREF-T17`: `adb/launcher-tests/HOME-PREF-T17/after_target_preferred_activities.txt:8874-8883` retains Microsoft as a preferred activity, while `logcat_full.txt:1764-1774` and the after snapshot show Fire after unlocked `KEYCODE_HOME`.
- `REBOOT-T02`: `adb/logs/REBOOT-T02/after_home_resolve.txt:1-2` returns Fire after a reboot and PackageManager readiness wait.
- `HOME-T18`: Microsoft was explicitly brought to the unlocked foreground; `logcat_focus.txt:36,45,52-53` records the Microsoft launch followed by a Fire HOME start, and `after_activity_activities.txt:60` / `after_window_windows.txt:316-317` show Fire resumed and focused.
- `HOME-T19`: Microsoft was explicitly brought to the unlocked foreground; fresh logcat `logcat_focus.txt:7-11` records the explicit HOME request resolving to Fire, and `after_activity_activities.txt:60` / `after_window_windows.txt:316-317` show Fire resumed and focused.

## Conditional Amazon direct-home branch

The extracted Amazon callback `AlexaModeSwitchManagerPhoneWindowManagerCallback.startCustomDockOrHome(Context)` calls `launchEchoShowHome(Context)`. That method obtains the mode through the `alexa_modeswitch` system service; when the mode equals `1`, it obtains `HomeIntentProvider.getMultimodalHomeIntent()` and calls `Context.startActivity(Intent)`, returning `true`. Otherwise it returns `false` and the standard path continues: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:196230-196277,196362-196368`.

`Confirmed code path`: this is a genuine Amazon explicit-start opportunity in the framework callback chain. `Disproved for the inspected callback`: it does not name or construct `com.amazon.firelauncher/.Launcher`; its target is the provider-supplied multimodal Home Intent. The read-only probe at `adb/probes/ALEXA-MODE-T01/` records `mss_mode=null`, `dumpsys alexa_modeswitch` failure and Binder transaction-2 failure, so current shell visibility is insufficient to classify the live mode. The normal unlocked tablet tests therefore remain the evidence for the Fire Launcher path.

## Keyguard control

The earlier `HOME-PREF-T02`/`T03` pair was collected with `mKeyguardShowing=true`. Those runs are useful lock-screen observations, but not a valid comparison of resolver and Home-key routing. The later `HOME-T14`/`T15`/`T16`/`HOME-PREF-T17` runs explicitly woke and dismissed keyguard and all reached Fire. `mKeyguardShowing` is therefore a required control variable for future Home tests.

## Settings path and retained picker

The Settings UI result is separate from the HOME resolver result. The installed `app_default_settings.xml` omits the `default_home` preference that official Android 9 r1/r61 include, while `DefaultHomePreferenceController` and `DefaultHomePicker` remain in the APK. `HOME-T21` shows the live Default apps page without a Home row. `HOME-T22` shows Fire Launcher's App info row `Home app: Yes`; `HOME-T23` taps only that row and reaches `com.android.settings/.SubSettings` with the same Home-less Default apps page. This confirms a Settings entry-point removal/hiding behavior, not a direct change to the PackageManager HOME ranking evidence.

Static route: `DefaultHomeShortcutPreferenceController` is added by `AppInfoDashboardFragment` and its base controller launches `DefaultAppSettings` for the `default_home` preference (`decompiled/jadx/settings/sources/com/android/settings/applications/appinfo/AppInfoDashboardFragment.java:192-197`; `DefaultAppShortcutPreferenceControllerBase.java:41-48`). No tested UI action reached `DefaultHomePicker` or called its `replacePreferredActivity()` method.

The retained picker was tested as an alternate shell-visible entry point. `SETTINGS-T01` was rejected because `com.android.settings/.SubSettings` is not exported (`adb/settings-tests/SETTINGS-T01/open_fragment.txt`; `decompiled/jadx/settings/resources/AndroidManifest.xml:232-234`). `SETTINGS-T03` used corrected quoting for `Settings$AdvancedAppsActivity` and started successfully, but the activity still displayed the metadata-selected `DefaultAppSettings` dashboard; `SettingsActivity.isValidFragment()` allows the gateway entry list, which includes `DefaultAppSettings` but not `DefaultHomePicker` (`decompiled/jadx/settings/sources/com/android/settings/SettingsActivity.java:403-410`; `core/gateway/SettingsGateway.java:131`). `SETTINGS-T02` is retained as a command-quoting artifact. `Probable`: the picker is unavailable through the tested standard shell routes; a privileged/internal caller remains untested.

## Amazon Home-task visibility policy

Amazon registers `LauncherHijackPreventerActivityStackCallback` in system_server. Its `canSeeHomeTask()` method checks `SELinux.checkSELinuxAccess(..., "amazon_policies", "see_home_task")` and then allows Android-signed packages as a fallback: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136880-136953`. Android's `ActivityStack.getRunningTasks()` applies this callback when deciding whether a Home task is visible: `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStack.java:3438-3445`. Dynamic `see_home_task` AVC denials appear during unlocked Home tests, for example `adb/home-key-tests/HOME-T15/logcat_full.txt:2586-2588`.

`Confirmed`: Amazon modified Home-task visibility policy. `Hypothesis`: this policy may affect Amazon's foreground-task inspection or launcher-hijack prevention behavior. The current evidence does not show it directly choosing or starting Fire Launcher.

## Interpretation

`Confirmed`: Amazon modified the framework path by inserting a key-policy hook.  
`Confirmed for tested unlocked paths`: HOME-T14, HOME-T15, HOME-T16 and HOME-PREF-T17 continue through a HOME start and resume Fire; the Microsoft preferred record does not outrank Fire's priority-50 candidate.  
`Disproved for the tested path`: the available evidence does not show SystemUI directly starting Fire Launcher or the explicit HOME command bypassing PackageManager resolution.  
`Hypothesis`: a physical hardware button or a special Amazon callback branch could activate a different path; no such branch was observed in the unlocked ADB tests. The Alexa branch is statically confirmed but was not shown to target Fire or to be active.

SystemUI contains a bounded Fire Launcher reference in `decompiled/jadx/systemui/sources/com/amazon/systemui/SGObserver.java:162-170`: it detects `com.amazon.firelauncher.Launcher` as the current task and then launches Smart Genie, not Fire Launcher. This supports the negative SystemUI-launch finding for the inspected path; see `findings/systemui-launch-search.md`.

The initial call graph is also stored at `output/call-graphs/home-flow-phase1.txt`.
