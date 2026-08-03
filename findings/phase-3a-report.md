# Phase 3A report

## 1. Executive summary

Phase 3A is complete for the no-Root, ADB-installable test condition.

- `Confirmed`: Fire Launcher declares HOME priority `50` in its manifest and
  is a privileged system package. Evidence: `P3A-PRE-002`, `P3A-STATIC-004`.
- `Confirmed`: the five research APK manifests contain declared priorities
  `0`, `49`, `50`, `51`, and `100`. Evidence: `P3A-BUILD-002`.
- `Confirmed`: PackageManager reports every sideloaded research APK at
  effective priority `0`. Fire VDEX `ActivityIntentResolver.adjustPriority()`
  matches Android 9 AOSP's non-privileged priority cap. Evidence:
  `P3A-STATIC-004`, `P3A-RUN-P49`, `P3A-RUN-P50`, `P3A-RUN-P51`,
  `P3A-RUN-P100`.
- `Strong evidence`: the effective HOME result is explained by standard
  priority normalization plus Fire's privileged priority 50, followed by the
  standard `chooseBestActivity()` ranking path. Evidence:
  `P3A-STATIC-001`, `P3A-STATIC-004`, `P3A-RUN-001`.
- `Confirmed`: ordinary `set-home-activity` accepts a research component and
  writes an `mAlways=true` preferred record, including across reboot, but the
  effective resolver and Home key still select Fire. Evidence:
  `P3A-RUN-P49`, `P3A-RUN-P50`, `P3A-RUN-P51`, `P3A-RUN-P100`.
- `Confirmed`: explicit HOME intent and `input keyevent 3` both ended at Fire
  in the tested foreground path. A transient `FallbackHome` result was seen
  immediately after several reboots before the post-boot Home event brought
  Fire forward. Evidence: `P3A-RUN-001`, `P3A-RUN-P49`, `P3A-RUN-P50`,
  `P3A-RUN-P51`, `P3A-RUN-P100`.
- `Unknown`: whether a privileged/system-signed third-party package with an
  effective priority above 50 would win. Creating that condition is outside
  this no-Root experiment.
- `Disproved`: a normal ADB-installed APK declaring priority 51 or 100 can
  outrank Fire on this build.

The experiment does not establish an Amazon-only resolver ranking patch. The
Amazon `VendorActivityStackSupervisorCallback` remains a real interception
boundary, but no callback-specific Fire return was proven here. Evidence:
`P3A-STATIC-002`, `P3A-STATIC-003`.

## 2. Static resolver analysis

The generated static outputs are:

- `findings/home-resolver-method-analysis.md`
- `diff/reports/home-resolver-aosp-fireos-diff.md`
- `output/call-graphs/home-resolver-method-flow.mmd`
- `aosp/references/aosp-baseline.md`

The key Fire VDEX locations are:

- `PackageManagerService.chooseBestActivity`: line `934336`, codeOff
  `0x2b5b2e`; priority/preferredOrder/isDefault comparison occurs before the
  ordinary preferred-activity call.
- `PackageManagerService.findPreferredActivity`: line `959826`, codeOff
  `0x2b6206`.
- `PackageManagerService.findPersistentPreferredActivityLP`: line `938922`,
  codeOff `0x2b5fc2`.
- `PackageManagerService.resolveIntent` / `resolveIntentInternal`: lines
  `966090` / `951258`.
- `PackageManagerService.queryIntentActivitiesInternal`: lines `947548` and
  `947566`.
- `PackageManagerService.ActivityIntentResolver.adjustPriority`: line
  `925124`, codeOff `0x2abde4`.

`adjustPriority()` checks `ApplicationInfo.privateFlags & 0x8`, and calls
`ActivityIntentInfo.setPriority(0)` for a non-privileged positive-priority
filter. The matching AOSP r1/r61 method has the same behavior. This explains
the runtime candidate output without requiring an Amazon package-name special
case. Evidence: `P3A-STATIC-004`.

`chooseBestActivity()` compares the first two candidates before ordinary
preferred lookup. The preferred record's `mAlways=true` is therefore not
enough when the ranked candidates do not tie. Persistent-preferred lookup is
present in the method inventory, but Phase 3A did not create or observe a
DevicePolicy persistent-preferred record.

The ActivityManager path also contains an Amazon callback boundary:
`ActivityStackSupervisor.resolveIntent()` calls
`VendorActivityStackSupervisorCallback.callResolveIntent()` before the normal
`PackageManagerInternal.resolveIntent()` path. The inspected FOS callback
calls PackageManager and applies `isUninstalledApp`; it does not expose a
proven explicit Fire component return in this artifact. Evidence:
`P3A-STATIC-003`.

## 3. APK build and integrity

Build output: `tools/test-launcher/dist/20260803-jdk26/`. Evidence:
`P3A-BUILD-001`, `P3A-BUILD-002`.

- JDK: OpenJDK `26.0.1`
- Android platform: API 35
- Build-tools: `35.0.0`
- AGP: `NOT_USED`
- Gradle: `NOT_USED`
- APK signing: v3 verified; temporary keystore was outside the repository
- Source archive: `phase3a-launcher-source.tar.gz`
- Complete output manifest: `sha256sums.txt`

| Package | Declared priority | APK SHA-256 |
|---|---:|---|
| `org.fireosresearch.home.p0` | 0 | `957f6cc71fd608730582400175f64306aa5ca65eb35ec3e98f4964980df52f70` |
| `org.fireosresearch.home.p49` | 49 | `bad23c71ea344d0106eeed36ceb97c1f144e31a64a7981787b9512cf0b248998` |
| `org.fireosresearch.home.p50` | 50 | `a5cab06fc763dfc99f1b51c2df177f3d79786fa7b4e5a410d74f4e12e3aca007` |
| `org.fireosresearch.home.p51` | 51 | `350d497d9603b479e1453b36685646760bd62a65e8c4a02c1ff9d1665653713c` |
| `org.fireosresearch.home.p100` | 100 | `4fd22ad14b02635a72733d062f3d999f9fb37b758f7434b7addc32db38b20c12` |

## 4. Runtime mutation results

The read-only baseline is `adb/mutation-tests/HOME-PRIORITY-PRE/`. Each
variant directory contains before/after dumps, command manifests, logcat,
reboot polling, restore script, result, and SHA-256 manifest.

| Test ID | Effective candidate priority | Preferred write | Resolver after write | Reboot observation | Final state |
|---|---:|---|---|---|---|
| `HOME-PRIORITY-P0` | 0 | Captured before interruption | Fire | PackageManager unavailable at interrupted probe | Fire restored by recovery |
| `HOME-PRIORITY-P49` | 0 | Success; `mAlways=true` | Fire | FallbackHome transient, then Fire after Home | `RESTORED_FIRE` |
| `HOME-PRIORITY-P50` | 0 | Success; `mAlways=true` | Fire | FallbackHome transient, then Fire after Home | `RESTORED_FIRE` |
| `HOME-PRIORITY-P51` | 0 | Success; `mAlways=true` | Fire | FallbackHome transient, then Fire after Home | `RESTORED_FIRE` |
| `HOME-PRIORITY-P100` | 0 | Success; `mAlways=true` | Fire | FallbackHome transient, then Fire after Home | `RESTORED_FIRE` |

P49/P50/P51/P100 completed install, explicit activity start, explicit HOME
intent, Settings foreground plus Home key, ordinary preferred HOME write,
Home key, lock/wake, reboot, post-reboot Home, restore, and uninstall. P0's
raw directory is retained; recovery evidence is under
`adb/mutation-tests/HOME-PRIORITY-P0/recovery-20260803T062741Z/`.

The final device checks are:

```text
adb get-state -> device
cmd package resolve-activity ... HOME -> com.amazon.firelauncher/.Launcher
pm path org.fireosresearch.home.p0/p49/p50/p51/p100 -> no path
```

Evidence: `P3A-P0-RECOVERY`, `P3A-CLEAN-001`, `P3A-POST-001`.

## 5. Preferred activity behavior

For each complete variant, `cmd package set-home-activity` returned `Success`.
The post-write preferred dump selected the test component with `mAlways=true`;
the same ordinary preferred record was still present in the post-reboot dump
while the test package remained installed. Despite that record, the effective
HOME resolver remained Fire because the effective candidate ranking did not
tie. Evidence: `P3A-RUN-001`, `P3A-RUN-P49`, `P3A-RUN-P50`, `P3A-RUN-P51`,
`P3A-RUN-P100`.

The requested cleanup command is not implemented on this Fire OS build:

```text
cmd package clear-package-preferred-activities PACKAGE
Unknown command: clear-package-preferred-activities
```

This error is preserved in every complete variant's `clear_preferred` output.
It is a command-availability result, not a Fire Launcher protection result.
The restore path used supported `set-home-activity` for Fire and then
uninstalled only the research package.

## 6. Home key versus HOME intent

For each complete variant, the direct HOME intent and `input keyevent 3`
resulted in Fire in the captured activity/window state. The direct explicit
start of the research activity worked, proving that the research APK itself
was launchable. This separates ordinary activity launch from effective HOME
selection.

The immediate post-reboot resolver sometimes reported
`com.android.settings/.FallbackHome` priority -1000 while boot services were
settling. After the controlled post-reboot Home key and follow-up snapshot,
Fire was the foreground/resolved HOME. This is recorded as a transient boot
state, not as evidence of an Amazon watchdog. Evidence: `P3A-RUN-001`,
`P3A-RUN-P49`, `P3A-RUN-P50`, `P3A-RUN-P51`, `P3A-RUN-P100`.

## 7. Safety and operations not performed

Performed only the authorized reversible operations: research APK install and
uninstall, foreground activity starts, ordinary HOME preferred writes, Home
and sleep/wake key events, and reboot with ADB reconnection verification.

Not performed: Fire Launcher disable/hide/suspend/uninstall/data clear, deny
list modification, Settings/DeviceConfig/AppOps/Overlay writes, Root, exploit
tooling, bootloader unlock, fastboot/recovery/OTA sideload, partition write,
system remount, downgrade, factory reset, or userdata erase. Evidence:
`P3A-PRE-001`, `P3A-P0-RECOVERY`, `P3A-POST-001`.

## 8. Remaining unknowns

- Whether a privileged/system-signed third-party HOME activity with effective
  priority above 50 would win. Next minimum target: static-only comparison of
  the system-image priority path; no privileged APK installation is proposed.
- Whether the Amazon vendor callback changes a HOME result on this build. Next
  minimum target: trace callback implementations and return paths in the
  matching FOS-services artifact.
- Whether a DevicePolicy persistent-preferred record exists outside the normal
  preferred dump. Next minimum target: read-only DevicePolicy dump and exact
  persistent-preferred sections; no policy mutation is proposed.
- Whether the transient FallbackHome boot state is standard Android startup or
  Amazon-specific. Next minimum target: compare boot-completion timing and
  AOSP Android 9 behavior in a controlled reference build.

## 9. Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/scripts/analyze_home_resolver_methods.py \
  --fire-disassembly decompiled/baksmali/vdexExtractor/services/disassembly.log \
  --aosp-r1 aosp/android-9/android-9.0.0_r1/platform \
  --aosp-r61 aosp/android-9/android-9.0.0_r61/platform \
  --fosservices-disassembly decompiled/baksmali/vdexExtractor/fosservices/disassembly.log \
  --output-findings findings/home-resolver-method-analysis.md \
  --output-diff diff/reports/home-resolver-aosp-fireos-diff.md \
  --output-graph output/call-graphs/home-resolver-method-flow.mmd

tools/scripts/run_home_priority_experiment.sh \
  --serial G001LT0511550CFT \
  --apk-dir tools/test-launcher/dist/20260803-jdk26 \
  --reuse-pre-snapshot --append-matrix --approve-state-change
```

The runner requires the visible phrase `APPROVE HOME-PRIORITY-PHASE3A` and
refuses to overwrite existing evidence directories.
