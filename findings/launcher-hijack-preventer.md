# LauncherHijackPreventer — Preliminary Finding

Status: `CONFIRMED` as an Amazon framework policy component; direct Fire Launcher launch is `DISPROVED` for the inspected callback method.

## Static evidence

Amazon registers the component in system_server:

- `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml:9-18` registers `LauncherHijackPreventerActivityStackCallback` and an ActivityManager callback.
- `artifacts/amazon-services/tabletlauncherhijackpreventer_fosinit.xml:9-16` registers PackageManager and PermissionManager callbacks.

`LauncherHijackPreventerActivityStackCallback.canSeeHomeTask(int, Context)`:

1. Resolves the calling UID to `ApplicationInfo`.
2. Builds the app SELinux context.
3. Calls `SELinux.checkSELinuxAccess(..., "amazon_policies", "see_home_task")`.
4. Allows the caller when that check succeeds.
5. Otherwise allows an Android-signature match; all other callers are denied.

Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136880-136953`.

Android's `ActivityStack.getRunningTasks()` invokes the vendor callback when evaluating a Home task. The task is included only when the normal `allowed` condition, the callback result, or the task's effective UID permits it: `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStack.java:3438-3445`. The callback aggregator ANDs registered callbacks: `decompiled/baksmali/vdexExtractor/services/disassembly.log:222322-222331`.

## Dynamic evidence

The device emitted SELinux denials for `see_home_task` during an unlocked Home-key run:

- `adb/home-key-tests/HOME-T15/logcat_full.txt:2586-2588`
- The same pattern is also present in `HOME-T14` and `HOME-PREF-T17`.

The same `HOME-T15` run then logged the standard HOME start and Fire resumption at `logcat_full.txt:2594-2606`, with `mKeyguardShowing=false` in `after_activity_activities.txt:183-190`.

## Determination

- `Confirmed`: Amazon changed the framework's Home-task visibility policy.
- `Strong evidence`: the component is explicitly registered, its method contains the SELinux/signature policy, and the matching runtime denial is observable.
- `Disproved for the inspected method`: `canSeeHomeTask()` does not construct or start a Fire Launcher component.
- `Hypothesis`: this policy may support launcher-hijack prevention by limiting task visibility or foreground-app inspection. The current evidence does not prove that it is the mechanism that selects Fire Launcher.

This finding must not be merged with the separate PackageManager protected-package mechanism. The former controls task visibility; the latter rejects `pm disable-user` before package state mutation.
