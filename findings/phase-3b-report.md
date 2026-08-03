# Phase 3B report — HOME selection control layer

## Scope and evidence boundary

This report is generated from the preserved PS7330.4104N device evidence and
the matching local Fire OS 7 decompilation inputs. It does not repeat the Phase
3A priority or `set-home-activity` experiments. It does not claim that an
unobserved callback, setting, or reboot-time service rewrites HOME.

Device: `KFTRWI`; Fire OS property: `7.0`; security patch: `2024-02-01`.
The device fingerprint captured in the canonical baseline is:
`Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`. Fire Launcher is `/system/priv-app/com.amazon.firelauncher`, version `1.3.232663.0_82020310`, and
the pulled APK SHA-256 is `601c510df94ddf2701ef8eb662ad565a5108688e562ca29fa56c1b14289b4ddf`.

## Executive summary

- **Confirmed — baseline resolver:** Fire Launcher is the top HOME candidate at
  effective priority `50`; Microsoft Launcher remains a candidate at effective
  priority `0`; FallbackHome is `-1000`. The HOME resolver returns
  `com.amazon.firelauncher/.Launcher`. Evidence: `P3B-HOME-001`.
- **Confirmed — ordinary preferred record:** the package dump contains a User 0
  ordinary preferred HOME record for Fire Launcher with `mAlways=true` at
  `preferred_activities.stdout.txt:8874-8885`; the captured persistent-preferred
  command did not expose a separate HOME record.
  Evidence: `P3B-PREF-001`.
- **Strong evidence — why the Phase 3A Microsoft record did not win:** Android 9
  `chooseBestActivity()` first compares the leading candidates' priority and
  only consults the ordinary preferred resolver on the priority tie path. A
  `mAlways=true` record for a priority-0 Microsoft candidate therefore cannot
  outrank Fire's priority-50 candidate. This is an AOSP-shaped decision point,
  not evidence of an Amazon package-name branch. Evidence: `P3B-STATIC-PMS-001`,
  Phase 3A preserved set-home evidence.
- **Confirmed — explicit HOME observation:** the clean `am start` sample was
  logged by ActivityManager as a standard MAIN+HOME intent that had already
  become explicit `cmp=com.amazon.firelauncher/.Launcher`. Evidence:
  `P3B-PATH-EXPLICIT-001`.
- **Confirmed — keyevent observation:** the clean injected Home key sample
  produced the same explicit Fire component in `am_new_intent` after the
  MAIN+HOME key path. The clean capture did not retain a matching
  `ActivityManager: START` line, so it does not infer a caller UID from that
  sample. Evidence: `P3B-PATH-KEYEVENT-001`.
- **Confirmed — Fire-specific key-policy boundary:** Fire OS adds a
  `TabletKeyPolicyManager` pre-hook and PhoneWindowManager vendor callback
  boundary. The observed Amazon key-policy code builds a standard HOME intent;
  its custom-home path is permission-gated and broadcasts to the foreground app,
  not directly to Fire Launcher. Evidence: `P3B-STATIC-KEYPOLICY-001`,
  `P3B-STATIC-DOCK-001`.
- **Not confirmed:** a callback returning a Fire-specific `ResolveInfo`, a
  persistent preferred HOME record, an Amazon resolver ranking override, or a
  watchdog that rewrites the Phase 3A record. These remain open rather than
  being inferred from the final foreground component.

The smallest current explanation is therefore **privileged Fire Launcher
manifest priority + the standard Android 9 resolver ordering**, with Amazon
key-policy and ActivityStack callback extension points present around the path.
The extension points are real, but the preserved evidence does not show them
overriding the current HOME result.

## 1. Complete HOME flow

### Explicit HOME intent and boot/start-home path

`ActivityManagerService.getHomeIntent()` creates the HOME intent and adds the
HOME category (`decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java:2741-2748`).
`startHomeActivityLocked()` resolves it through `resolveActivityInfo()` and then
sets the resolved component before calling the activity start controller
(`decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java:2751-2767`). A non-component intent goes through
`IPackageManager.resolveIntent()` (`decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java:2774-2788`).

Within the Fire OS ActivityStackSupervisor, `resolveIntent()` calls the vendor
callback array first and returns a non-null callback result immediately; if all
callbacks return null, it calls PackageManagerInternal (`decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772`).
The callback aggregator itself returns the first non-null result and otherwise
returns null (`decompiled/jadx/systemui/sources/com/android/server/am/VendorActivityStackSupervisorCallback.java:19-31`).

PackageManager then follows the AOSP-shaped chain:

`resolveIntent()` → `resolveIntentInternal()` → `queryIntentActivitiesInternal()`
→ `chooseBestActivity()` → priority/preferred selection.

The selected Fire OS source locations are `PackageManagerService.java:3003-3022`,
`:3120-3168`, `:3197-3275`, and `:3288-3350`. AOSP r1 and r61 provide the
comparison sources at:

- `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java: resolveIntent / chooseBestActivity / findPreferredActivity`
- `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java: resolveIntent / chooseBestActivity / findPreferredActivity`

The exact line numbers can vary between the two AOSP tags; the report generator
indexes the method declarations rather than relying on a full-text diff.

### Home key path

The VDEX shows `PhoneWindowManager.handleShortPressOnHome()` calling
`mKeyPolicyManager.handleShortPressOnHome()` first. When that hook does not
consume the event, the framework reaches `launchHomeFromHotKey()` and
`startDockOrHome()`. The latter first handles a custom dock intent, then calls
the vendor `callCustomDockOrHome()` hook, then `callOnStartDockOrHome()`, and
finally starts `mHomeIntent` as `UserHandle.CURRENT`:

`decompiled/baksmali/vdexExtractor/services/disassembly.log:977415-977444`, `:985822-985900`, `:988383-988428`,
`:559374-559388`, `:559635-559646`.

The registered Amazon callback is `KeyInterceptorCallback` from
`artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml`. The private
services VDEX shows `TabletKeyPolicyManager.handleShortPressOnHome()` checking
the foreground activity through `IAmazonActivityManager`, then invoking
`HomeEventHandler.handleCustomHome()`; a false result allows the framework
Home path to continue (`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:314232-314262`).

`HomeEventHandler.handleCustomHome()` only sends an explicit
`com.amazon.tablet.action.CUSTOM_HOME` broadcast to a receiver belonging to the
foreground app after checking `com.amazon.permission.RECEIVE_CUSTOM_HOME`
(`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:141282-141329`). It is not a default-launcher selection
operation.

### Mermaid overview

See `output/call-graphs/home-resolution-phase3b.mmd` for the machine-readable
graph and `findings/home-resolution-call-path.md` for the text equivalent.

## 2. What the clean runtime samples show

The samples were run sequentially. The earlier parallel pilot samples are
retained but not used as independent evidence because they shared logcat and
foreground state.

| Entry | ActivityManager START evidence | Result | Confidence |
|---|---|---|---|
| `am start MAIN+HOME` | `uid 2000`, `flg=0x10000000`, `cmp=com.amazon.firelauncher/.Launcher` at `adb/phase3b/HOME-PATH-EXPLICIT-02/logcat.txt:2158` (15:12:10.590) | Fire Launcher resumed and focused | Confirmed |
| `input keyevent 3` | Input down/up at `adb/phase3b/HOME-PATH-KEYEVENT-02/logcat.txt:2177-2181`; `am_new_intent` at `:2190` carries `MAIN` and explicit `com.amazon.firelauncher/.Launcher`; no matching START line was captured | Fire Launcher resumed and focused | Confirmed |

The log files contain older retained buffer lines because the original capture
used a main-buffer clear followed by `-b all`. The evidence interpretation is
limited to the current test timestamp windows recorded in each `metadata.tsv`
and result file. The capture script now clears all buffers with
`logcat -b all -c` for future runs.

These samples prove that both tested entry points ended at the same explicit
component. They do not by themselves prove whether the explicit component was
selected by PackageManager, by ActivityTaskManager after a callback, or by a
different earlier hook. The static path makes the normal resolver the leading
explanation, while preserving the Amazon callback boundary as an unresolved
observation point.

## 3. Preferred record that exists but does not win

The preserved Phase 3A operation wrote an ordinary `mAlways=true` record for
Microsoft Launcher. It did not change the effective HOME result or reboot
result. In the current baseline, Fire remains the priority-50 candidate and
Microsoft is priority 0. This is the decision tree:

1. Build the enabled HOME candidate set.
2. Apply persistent preferred activity if a valid record exists. No separate
   active HOME record was observed in the canonical persistent dump; the command
   was not a clean supported query on this build, so the negative is bounded.
3. Compare the leading candidates. If their priority/order/default status does
   not tie, `chooseBestActivity()` returns the stronger candidate without
   entering the ordinary preferred selection branch.
4. Fire priority 50 beats Microsoft effective priority 0.
5. The Microsoft `mAlways=true` record can remain stored while not being
   selected.
6. The resulting component is passed into ActivityManager/ActivityTaskManager
   and appears as an explicit `cmp` in the START log.

This explains the preserved result without requiring a Fire package-name special
case. See `findings/preferred-record-decision-tree.md`.

## 4. Amazon extension points found

| Layer | Evidence | Interpretation |
|---|---|---|
| ActivityStackSupervisor | `VendorActivityStackSupervisorCallback.callResolveIntent()` before PM internal resolution | Amazon can override a resolve result; no Fire-specific return was found in the inspected callback evidence | Strong evidence for hook; override unconfirmed |
| PhoneWindowManager | `KeyPolicyManager` pre-hook, custom dock hook, on-start hook | Amazon can intercept Home key handling | Confirmed extension point |
| TabletKeyPolicyManager | foreground-app check and `HomeEventHandler` call | Custom-home/game-controller behavior, not demonstrated default Fire selection | Confirmed code; default effect unconfirmed |
| LauncherHijackPreventer | `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()` and SELinux `see_home_task` check | Restricts who can see the Home task; not a direct Fire launch in the inspected method | Confirmed task-visibility feature |
| PackageManager resolver | AOSP-shaped priority comparison; no selected Fire package branch | Current evidence favors standard ranking over Amazon ranking patch | Strong evidence, not universal proof |

## 5. Package identity and privilege matrix

Fire Launcher is a `/system/priv-app` package with `privateFlags` including
`PRIVILEGED`, UID `10120`, and many privileged/signature permissions. Its
privileged identity distinguishes it from Phase 3A sideloaded launchers. The
full machine-readable matrix is `output/tables/fire-launcher-privilege-matrix.csv`.

The matrix deliberately uses `UNKNOWN` where a package dump or signature
comparison was not captured. It does not infer platform signing from a truncated
signature summary or infer device-owner control from the existence of a
parental-controls profile owner.

## 6. Settings, overlay, and background rewrite boundary

The canonical baseline preserved `cmd overlay list`, settings lists, device
policy, package lists, service list, and the system/server classpath. The
`device_config list` command was unavailable on this build (exit 127), and the
HOME role-holder query was unsupported (exit 20). Therefore this phase cannot
claim a complete DeviceConfig or RoleManager negative.

The inspected Amazon `fosinit` registrations include PackageManager,
ActivityManager, key-policy, and launcher-hijack callbacks. No captured log or
static reference proves that one of these services rewrites the ordinary
preferred record after Phase 3A. The priority comparison alone explains the
observed result. The bounded overlay/config review is in
`findings/overlay-and-config-analysis.md`.

## 7. Answers and status labels

| Question | Answer | Status |
|---|---|---|
| Is HOME fixed before or after PackageManager resolution? | Current baseline resolves Fire as the highest effective candidate; both clean entry points end at Fire. | Confirmed observation; mechanism Strong evidence |
| Does Home key bypass HOME intent? | Not in the tested keyevent sample; static code reaches the standard Home intent path after Amazon hooks return. | Strong evidence |
| Does an Amazon resolver callback exist? | Yes, an ActivityStackSupervisor callback boundary exists. | Confirmed hook; Fire override unconfirmed |
| Is a persistent preferred HOME record active? | No separate active HOME record was observed; the command output is not a clean supported persistent-only query. | Strong evidence / bounded negative |
| Why did Microsoft `mAlways=true` not win? | Effective priority 0 loses to Fire priority 50 before the ordinary preferred tie branch. | Strong evidence |
| Is there a Fire package-name ranking branch? | Not found in the inspected resolver methods. | Probable absent in inspected scope |
| Is a background watchdog proven? | No. | Unknown |
| Is a no-Root workaround established? | No. This phase intentionally did not attempt one. | Unknown / not demonstrated |

## 8. Next smallest high-value test

The single most valuable next test is **a clean, one-shot tracing run that
captures the exact `VendorActivityStackSupervisorCallback` callback ordering
and any non-null `ResolveInfo` result for a HOME intent**, using only logcat and
before/after dumps. Static analysis should first enumerate all concrete callback
classes registered in the matching private-services VDEX. No package state,
settings, overlay, or partition mutation is required.

## 9. Reproduction

Offline report generation:

```sh
python3 tools/scripts/analyze_phase3b.py --root . --force
```

Read-only device collection, only if a new baseline is needed:

```sh
tools/scripts/collect_phase3b_baseline.sh --serial G001LT0511550CFT
```

HOME path observation only (foreground action and all-buffer logcat clear):

```sh
tools/scripts/capture_home_path_phase3b.sh \
  --serial G001LT0511550CFT --test-id HOME-PATH-EXPLICIT-NEXT \
  --output adb/phase3b/HOME-PATH-EXPLICIT-NEXT --mode explicit \
  --approve-state-change
```

The command above is not needed to reproduce the report; the canonical raw
inputs are already preserved. It does not disable Fire Launcher or write
settings/package state.

## Source and hash index

| Input | File | SHA-256 |
|---|---|---|
| Fire OS AMS | `decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java` | `4cdcb70290f9a88abcb9997bedc1b19f8518f2b03fc770052c7dd29e53ae4be6` |
| Fire OS ActivityStackSupervisor | `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java` | `f08a19bb871b08d91fd5e9dfe35754a1e2c810e5c279a126f43e4f873e6ef683` |
| Fire OS PMS | `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java` | `f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074` |
| Fire OS vendor AM callback | `decompiled/jadx/systemui/sources/com/android/server/am/VendorActivityStackSupervisorCallback.java` | `206671ec27f3d554c76c9658b3754979e2a04b28ff7fe05e5c18d57f7d3bce1b` |
| Fire OS vendor policy callback | `decompiled/jadx/systemui/sources/com/android/server/policy/VendorPhoneWindowManagerCallback.java` | `fd03ac905d06bd528ba5802ec5933f2db9317eb97b6e4676dadcf243364668dc` |
| Fire OS services VDEX | `decompiled/baksmali/vdexExtractor/services/disassembly.log` | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |
| Fire OS private-services VDEX | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| AOSP r1 PMS | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | `c36adc88a410335e980214fdc11bf4919675546e8691d0784f2e59ae4f33886b` |
| AOSP r61 PMS | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | `bb8d33fbb976c3463d932f65a679dafb2d541845b2989b63d07060d0db8ef179` |
