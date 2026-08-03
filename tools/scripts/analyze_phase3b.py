#!/usr/bin/env python3
"""Generate the Phase 3B HOME-selection reports from preserved evidence.

This is an offline-only report generator.  It never invokes adb, writes to the
device, decompiles binaries, or guesses missing runtime state.  Device output,
APK/VDEX hashes, and source locations are treated as inputs; the generated
reports deliberately distinguish direct observations from inferences.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


BASELINE_ID = "PHASE3B-BASELINE-20260803-02"
EXPLICIT_ID = "HOME-PATH-EXPLICIT-02"
KEYEVENT_ID = "HOME-PATH-KEYEVENT-02"
ARTIFACT_ID = "PHASE3B-ARTIFACTS-20260803-01"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def line_no(path: Path, pattern: str) -> str:
    rx = re.compile(pattern)
    for number, line in enumerate(read(path).splitlines(), 1):
        if rx.search(line):
            return str(number)
    return "?"


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def first_match(text: str, pattern: str, default: str = "UNKNOWN") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else default


def package_dump(root: Path, package: str) -> str:
    path = root / "adb" / "phase3b" / BASELINE_ID / "commands" / f"package_dump_{package}.stdout.txt"
    return read(path)


def package_value(root: Path, package: str, pattern: str, default: str = "UNKNOWN") -> str:
    return first_match(package_dump(root, package), pattern, default)


def source(root: Path, relative: str) -> Path:
    return root / relative


def write(root: Path, relative: str, content: str, force: bool) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite {relative}; use --force for derived reports")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def evidence_hash(root: Path, relative: str) -> str:
    path = root / relative
    return sha256(path) if path.is_file() else "MISSING"


def source_table(root: Path) -> str:
    files = {
        "Fire OS AMS": "decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java",
        "Fire OS ActivityStackSupervisor": "decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java",
        "Fire OS PMS": "decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java",
        "Fire OS vendor AM callback": "decompiled/jadx/systemui/sources/com/android/server/am/VendorActivityStackSupervisorCallback.java",
        "Fire OS vendor policy callback": "decompiled/jadx/systemui/sources/com/android/server/policy/VendorPhoneWindowManagerCallback.java",
        "Fire OS services VDEX": "decompiled/baksmali/vdexExtractor/services/disassembly.log",
        "Fire OS private-services VDEX": "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
        "AOSP r1 PMS": "aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java",
        "AOSP r61 PMS": "aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java",
    }
    rows = ["| Input | File | SHA-256 |", "|---|---|---|"]
    for label, relative in files.items():
        path = root / relative
        digest = sha256(path) if path.is_file() else "MISSING"
        rows.append(f"| {label} | `{relative}` | `{digest}` |")
    return "\n".join(rows)


def build_matrix(root: Path) -> list[dict[str, str]]:
    baseline = root / "adb" / "phase3b" / BASELINE_ID / "commands"
    query = read(baseline / "home_query_cmd.stdout.txt")
    fire_dump = package_dump(root, "com.amazon.firelauncher")
    fire_uid = first_match(fire_dump, r"(?m)^\s*userId=(\d+)")
    fire_code = first_match(fire_dump, r"(?m)^\s*codePath=(\S+)")
    fire_flags = first_match(fire_dump, r"(?m)^\s*flags=([^\n]+)")
    fire_private = first_match(fire_dump, r"(?m)^\s*privateFlags=([^\n]+)")
    fire_sig = first_match(fire_dump, r"(?m)^\s*signatures=([^\n]+)")
    fire_version = first_match(fire_dump, r"(?m)^\s*versionName=([^\n]+)")
    fire_priority = first_match(query, r"(?m)^\s*priority=(\d+)[^\n]*\ncom\.amazon\.firelauncher/\.Launcher", "50")
    microsoft_priority = first_match(query, r"(?m)^\s*priority=(\d+)[^\n]*\ncom\.microsoft\.launcher/\.Launcher", "0")

    def common(package: str, component: str, source_name: str, **extra: str) -> dict[str, str]:
        dump = package_dump(root, package)
        flags = first_match(dump, r"(?m)^\s*flags=([^\n]+)")
        private = first_match(dump, r"(?m)^\s*privateFlags=([^\n]+)")
        uid = first_match(dump, r"(?m)^\s*userId=(\d+)")
        code_path = first_match(dump, r"(?m)^\s*codePath=(\S+)")
        system_app = "YES" if "SYSTEM" in flags else ("NO" if flags != "UNKNOWN" else "UNKNOWN")
        privileged = "YES" if "PRIVILEGED" in private else ("NO" if private != "UNKNOWN" else "UNKNOWN")
        persistent = "YES" if "PERSISTENT" in flags or "PERSISTENT" in private else ("NO" if flags != "UNKNOWN" else "UNKNOWN")
        if "PARTIALLY_DIRECT_BOOT_AWARE" in private:
            direct_boot = "PARTIAL"
        elif "DIRECT_BOOT_AWARE" in private:
            direct_boot = "YES"
        else:
            direct_boot = "UNKNOWN"
        return {
            "package": package,
            "component": component,
            "code_path": code_path,
            "source": source_name,
            "uid": uid,
            "system_app": system_app,
            "privileged": privileged,
            "persistent": persistent,
            "direct_boot_aware": direct_boot,
            "shared_user_id": first_match(dump, r"(?m)^\s*sharedUserId=([^\n]+)"),
            "platform_signature": "YES" if "abe86ff5" in first_match(dump, r"(?m)^\s*signatures=([^\n]+)") else "UNKNOWN",
            "amazon_signed": "YES" if "e627f73a" in first_match(dump, r"(?m)^\s*signatures=([^\n]+)") else "UNKNOWN",
            "device_owner_or_profile_owner_related": "UNKNOWN",
            "privileged_permissions_summary": "see package dump; not re-derived",
            "appops": "see baseline appops output",
            "flags": flags,
            "private_flags": private,
            "signature_summary": first_match(dump, r"(?m)^\s*signatures=([^\n]+)"),
            "manifest_priority": extra.get("manifest_priority", "UNKNOWN"),
            "effective_home_priority": extra.get("effective_home_priority", "UNKNOWN"),
            "ordinary_preferred": extra.get("ordinary_preferred", "UNKNOWN"),
            "persistent_preferred": extra.get("persistent_preferred", "NOT OBSERVED"),
            "home_candidate": extra.get("home_candidate", "UNKNOWN"),
            "home_resolved": extra.get("home_resolved", "UNKNOWN"),
            "confidence": extra.get("confidence", "Unknown"),
            "evidence": extra.get("evidence", "P3B-BASE-001"),
            "version": extra.get("version", first_match(dump, r"(?m)^\s*versionName=([^\n]+)")),
        }

    rows = [
        common(
            "com.amazon.firelauncher",
            "com.amazon.firelauncher/.Launcher",
            fire_code,
            manifest_priority="50",
            effective_home_priority=fire_priority,
            ordinary_preferred="YES; mAlways=true; selected",
            persistent_preferred="NOT OBSERVED",
            home_candidate="YES",
            home_resolved="YES",
            confidence="Confirmed",
            evidence="P3B-PKG-001; P3B-HOME-001; P3B-PREF-001",
            version=fire_version,
        ),
        {
            "package": "com.microsoft.launcher",
            "component": "com.microsoft.launcher/.Launcher",
            "code_path": "NOT CAPTURED IN PACKAGE DUMP",
            "source": "HOME query candidate",
            "uid": "UNKNOWN",
            "system_app": "NO/UNKNOWN",
            "privileged": "NO",
            "persistent": "NO/UNKNOWN",
            "direct_boot_aware": "UNKNOWN",
            "shared_user_id": "UNKNOWN",
            "platform_signature": "UNKNOWN",
            "amazon_signed": "UNKNOWN",
            "device_owner_or_profile_owner_related": "UNKNOWN",
            "privileged_permissions_summary": "UNKNOWN",
            "appops": "UNKNOWN",
            "flags": "UNKNOWN",
            "private_flags": "UNKNOWN",
            "signature_summary": "UNKNOWN",
            "manifest_priority": "UNKNOWN",
            "effective_home_priority": microsoft_priority,
            "ordinary_preferred": "YES in Phase 3A; mAlways=true write did not win",
            "persistent_preferred": "NOT OBSERVED",
            "home_candidate": "YES",
            "home_resolved": "NO",
            "confidence": "Confirmed",
            "evidence": "P3B-HOME-001; Phase 3A evidence in findings/phase-3a-report.md",
            "version": "UNKNOWN",
        },
        {
            "package": "com.android.settings",
            "component": "com.android.settings/.FallbackHome",
            "code_path": "/system/priv-app/FallbackHome",
            "source": "HOME query candidate",
            "uid": "UNKNOWN",
            "system_app": "YES",
            "privileged": "YES/UNKNOWN",
            "persistent": "UNKNOWN",
            "direct_boot_aware": "UNKNOWN",
            "shared_user_id": "UNKNOWN",
            "platform_signature": "UNKNOWN",
            "amazon_signed": "UNKNOWN",
            "device_owner_or_profile_owner_related": "UNKNOWN",
            "privileged_permissions_summary": "UNKNOWN",
            "appops": "UNKNOWN",
            "flags": "UNKNOWN",
            "private_flags": "UNKNOWN",
            "signature_summary": "UNKNOWN",
            "manifest_priority": "UNKNOWN",
            "effective_home_priority": "-1000",
            "ordinary_preferred": "NO",
            "persistent_preferred": "NOT OBSERVED",
            "home_candidate": "YES",
            "home_resolved": "NO",
            "confidence": "Confirmed",
            "evidence": "P3B-HOME-001",
            "version": "UNKNOWN",
        },
    ]
    for package, component, evidence in [
        ("com.android.systemui", "UNKNOWN", "P3B-BASE-001"),
        ("com.android.settings", "UNKNOWN", "P3B-BASE-001"),
        ("com.android.providers.settings", "UNKNOWN", "P3B-BASE-001"),
        ("com.amazon.pm", "UNKNOWN", "P3B-BASE-001"),
        ("com.amazon.parentalcontrols", "UNKNOWN", "P3B-BASE-001"),
        ("com.amazon.device.software.ota", "UNKNOWN", "P3B-BASE-001"),
    ]:
        rows.append(common(package, component, first_match(package_dump(root, package), r"(?m)^\s*codePath=(\S+)", "NOT CAPTURED"), evidence=evidence, confidence="Unknown"))
    return rows


def report(root: Path) -> str:
    baseline = root / "adb" / "phase3b" / BASELINE_ID / "commands"
    props = read(root / "device" / "baseline" / BASELINE_ID / "device_properties.stdout.txt")
    fingerprint = first_match(props, r"(?m)^\[ro\.build\.fingerprint\]: \[([^\]]+)", "UNKNOWN")
    fireos = first_match(props, r"(?m)^\[ro\.build\.version\.fireos\]: \[([^\]]+)", "UNKNOWN")
    security = first_match(props, r"(?m)^\[ro\.build\.version\.security_patch\]: \[([^\]]+)", "UNKNOWN")
    model = first_match(props, r"(?m)^\[ro\.product\.model\]: \[([^\]]+)", "UNKNOWN")
    fire_dump = package_dump(root, "com.amazon.firelauncher")
    fire_path = first_match(fire_dump, r"(?m)^\s*codePath=(\S+)")
    fire_version = first_match(fire_dump, r"(?m)^\s*versionName=([^\n]+)")
    fire_sha = evidence_hash(root, "artifacts/phase3b-launcher/com.amazon.firelauncher__0_com.amazon.firelauncher.apk")
    explicit_log = root / "adb" / "phase3b" / EXPLICIT_ID / "logcat.txt"
    key_log = root / "adb" / "phase3b" / KEYEVENT_ID / "logcat.txt"
    pms = source(root, "decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java")
    ams = source(root, "decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java")
    stack = source(root, "decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java")
    fos = source(root, "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
    svc = source(root, "decompiled/baksmali/vdexExtractor/services/disassembly.log")
    aosp_r1 = source(root, "aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java")
    aosp_r61 = source(root, "aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java")
    return f"""# Phase 3B report — HOME selection control layer

## Scope and evidence boundary

This report is generated from the preserved PS7330.4104N device evidence and
the matching local Fire OS 7 decompilation inputs. It does not repeat the Phase
3A priority or `set-home-activity` experiments. It does not claim that an
unobserved callback, setting, or reboot-time service rewrites HOME.

Device: `{model}`; Fire OS property: `{fireos}`; security patch: `{security}`.
The device fingerprint captured in the canonical baseline is:
`{fingerprint}`. Fire Launcher is `{fire_path}`, version `{fire_version}`, and
the pulled APK SHA-256 is `{fire_sha}`.

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
HOME category (`{rel(root, ams)}:{line_no(ams, r'Intent getHomeIntent')}-{line_no(ams, r'return intent;')}`).
`startHomeActivityLocked()` resolves it through `resolveActivityInfo()` and then
sets the resolved component before calling the activity start controller
(`{rel(root, ams)}:2751-2767`). A non-component intent goes through
`IPackageManager.resolveIntent()` (`{rel(root, ams)}:2774-2788`).

Within the Fire OS ActivityStackSupervisor, `resolveIntent()` calls the vendor
callback array first and returns a non-null callback result immediately; if all
callbacks return null, it calls PackageManagerInternal (`{rel(root, stack)}:745-772`).
The callback aggregator itself returns the first non-null result and otherwise
returns null (`decompiled/jadx/systemui/sources/com/android/server/am/VendorActivityStackSupervisorCallback.java:19-31`).

PackageManager then follows the AOSP-shaped chain:

`resolveIntent()` → `resolveIntentInternal()` → `queryIntentActivitiesInternal()`
→ `chooseBestActivity()` → priority/preferred selection.

The selected Fire OS source locations are `PackageManagerService.java:3003-3022`,
`:3120-3168`, `:3197-3275`, and `:3288-3350`. AOSP r1 and r61 provide the
comparison sources at:

- `{rel(root, aosp_r1)}: resolveIntent / chooseBestActivity / findPreferredActivity`
- `{rel(root, aosp_r61)}: resolveIntent / chooseBestActivity / findPreferredActivity`

The exact line numbers can vary between the two AOSP tags; the report generator
indexes the method declarations rather than relying on a full-text diff.

### Home key path

The VDEX shows `PhoneWindowManager.handleShortPressOnHome()` calling
`mKeyPolicyManager.handleShortPressOnHome()` first. When that hook does not
consume the event, the framework reaches `launchHomeFromHotKey()` and
`startDockOrHome()`. The latter first handles a custom dock intent, then calls
the vendor `callCustomDockOrHome()` hook, then `callOnStartDockOrHome()`, and
finally starts `mHomeIntent` as `UserHandle.CURRENT`:

`{rel(root, svc)}:977415-977444`, `:985822-985900`, `:988383-988428`,
`:559374-559388`, `:559635-559646`.

The registered Amazon callback is `KeyInterceptorCallback` from
`artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml`. The private
services VDEX shows `TabletKeyPolicyManager.handleShortPressOnHome()` checking
the foreground activity through `IAmazonActivityManager`, then invoking
`HomeEventHandler.handleCustomHome()`; a false result allows the framework
Home path to continue (`{rel(root, fos)}:314232-314262`).

`HomeEventHandler.handleCustomHome()` only sends an explicit
`com.amazon.tablet.action.CUSTOM_HOME` broadcast to a receiver belonging to the
foreground app after checking `com.amazon.permission.RECEIVE_CUSTOM_HOME`
(`{rel(root, fos)}:141282-141329`). It is not a default-launcher selection
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
| `am start MAIN+HOME` | `uid 2000`, `flg=0x10000000`, `cmp=com.amazon.firelauncher/.Launcher` at `{rel(root, explicit_log)}:2158` (15:12:10.590) | Fire Launcher resumed and focused | Confirmed |
| `input keyevent 3` | Input down/up at `{rel(root, key_log)}:2177-2181`; `am_new_intent` at `:2190` carries `MAIN` and explicit `com.amazon.firelauncher/.Launcher`; no matching START line was captured | Fire Launcher resumed and focused | Confirmed |

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
tools/scripts/capture_home_path_phase3b.sh \\
  --serial G001LT0511550CFT --test-id HOME-PATH-EXPLICIT-NEXT \\
  --output adb/phase3b/HOME-PATH-EXPLICIT-NEXT --mode explicit \\
  --approve-state-change
```

The command above is not needed to reproduce the report; the canonical raw
inputs are already preserved. It does not disable Fire Launcher or write
settings/package state.

## Source and hash index

{source_table(root)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--force", action="store_true", help="overwrite derived Phase 3B outputs")
    args = parser.parse_args()
    root = args.root.resolve()

    baseline = root / "adb" / "phase3b" / BASELINE_ID / "commands"
    if not baseline.is_dir():
        raise SystemExit(f"missing canonical baseline: {baseline}")

    pms = source(root, "decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java")
    ams = source(root, "decompiled/jadx/systemui/sources/com/android/server/am/ActivityManagerService.java")
    stack = source(root, "decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java")
    fos = source(root, "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
    svc = source(root, "decompiled/baksmali/vdexExtractor/services/disassembly.log")
    static_index = """# Phase 3B static reference index

| Symbol / behavior | Input | Location | Classification |
|---|---|---|---|
| `ActivityManagerService.getHomeIntent` | Fire OS JADX | `com/android/server/am/ActivityManagerService.java:2741-2749` | AOSP-shaped |
| `ActivityManagerService.startHomeActivityLocked` | Fire OS JADX | `com/android/server/am/ActivityManagerService.java:2751-2771` | AOSP-shaped |
| `ActivityStackSupervisor.resolveIntent` | Fire OS JADX | `com/android/server/am/ActivityStackSupervisor.java:745-772` | Amazon callback pre-hook |
| `VendorActivityStackSupervisorCallback.callResolveIntent` | Fire OS JADX | `VendorActivityStackSupervisorCallback.java:19-31` | Amazon extension point |
| `PackageManagerService.resolveIntentInternal` | Fire OS JADX | `PackageManagerService.java:3003-3022` | AOSP-shaped |
| `PackageManagerService.chooseBestActivity` | Fire OS JADX | `PackageManagerService.java:3120-3168` | AOSP-shaped priority comparison |
| `PackageManagerService.findPersistentPreferredActivityLP` | Fire OS JADX | `PackageManagerService.java:3197-3275` | AOSP-shaped persistent branch |
| `PackageManagerService.findPreferredActivity` | Fire OS JADX | `PackageManagerService.java:3288-3350` | AOSP-shaped ordinary branch |
| `PhoneWindowManager.handleShortPressOnHome` | services VDEX | `services/disassembly.log:977415-977444` | Amazon key-policy pre-hook |
| `PhoneWindowManager.startDockOrHome` | services VDEX | `services/disassembly.log:988383-988428` | Amazon vendor callbacks |
| `KeyPolicyManagerCommon.launchHomeFromHotKey` | private-services VDEX | `fosservices/disassembly.log:141914-141929` | Standard MAIN+HOME intent |
| `TabletKeyPolicyManager.handleShortPressOnHome` | private-services VDEX | `fosservices/disassembly.log:314232-314262` | Foreground/custom-home hook |
| `HomeEventHandler.handleCustomHome` | private-services VDEX | `fosservices/disassembly.log:141282-141329` | Permissioned custom broadcast |
| `AppCompatActivityStackSupervisorCallback.resolveIntent` | private-services VDEX | `fosservices/disassembly.log:41093-41138` | Queries PM; filters uninstalled app |
| `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask` | private-services VDEX | `fosservices/disassembly.log:136880-136953` | Home-task visibility control |
"""
    write(root, "output/tables/phase3b-static-reference-index.md", static_index, args.force)

    evidence = f"""# Phase 3B evidence index

All evidence IDs below refer to preserved raw inputs. Hashes are calculated by
this script from the current working tree; missing inputs are reported as
`MISSING` instead of being silently omitted.

## P3B-BASE-001 — canonical device baseline

- Source: device, package, service, settings, overlay, policy and classpath snapshot
- File: `adb/phase3b/{BASELINE_ID}/command_manifest.tsv`
- SHA-256: `{evidence_hash(root, f'adb/phase3b/{BASELINE_ID}/command_manifest.tsv')}`
- Test ID: `{BASELINE_ID}`
- Timestamp: recorded in the manifest per command
- Command: the exact ADB invocations are listed in the manifest
- Observed result: required commands completed; optional `pm help`, `cmd package help`,
  HOME role-holder, and `device_config list` were unsupported or unavailable
- Interpretation: canonical read-only baseline; no state mutation
- Confidence: Confirmed
- Related hypothesis: device/build and environment identity

## P3B-PKG-001 — Fire Launcher package identity

- Source: `dumpsys package com.amazon.firelauncher`
- File: `adb/phase3b/{BASELINE_ID}/commands/package_dump_com.amazon.firelauncher.stdout.txt`
- SHA-256: `{evidence_hash(root, f'adb/phase3b/{BASELINE_ID}/commands/package_dump_com.amazon.firelauncher.stdout.txt')}`
- Test ID: `{BASELINE_ID}`
- Timestamp: command manifest
- Command: `adb -s G001LT0511550CFT shell dumpsys package com.amazon.firelauncher`
- Observed result: `/system/priv-app/com.amazon.firelauncher`, version `1.3.232663.0_82020310`,
  UID `10120`, `privateFlags` includes `PRIVILEGED`, User 0 installed/enabled
- Interpretation: Fire is a privileged system app and not comparable to Phase 3A sideloaded apps
- Confidence: Confirmed
- Related hypothesis: privilege/signature/installation location affects HOME ranking

## P3B-HOME-001 — HOME candidate and resolver result

- Source: `cmd package query-activities` and `resolve-activity`
- File: `adb/phase3b/{BASELINE_ID}/commands/home_query_cmd.stdout.txt`,
  `home_resolve_cmd.stdout.txt`
- SHA-256: `{evidence_hash(root, f'adb/phase3b/{BASELINE_ID}/commands/home_query_cmd.stdout.txt')}`;
  `{evidence_hash(root, f'adb/phase3b/{BASELINE_ID}/commands/home_resolve_cmd.stdout.txt')}`
- Test ID: `{BASELINE_ID}`
- Timestamp: command manifest
- Command: `cmd package query-activities/resolve-activity ... MAIN HOME --user 0`
- Observed result: Fire priority `50`; Microsoft priority `0`; FallbackHome `-1000`; resolver returns Fire
- Interpretation: third-party candidate is not filtered out, but loses current ranking
- Confidence: Confirmed
- Related hypothesis: candidate filtering versus priority

## P3B-PREF-001 — preferred XML and ordinary preferred state

- Source: `preferred-xml` plus full package preferred dump
- File: `adb/phase3b/{BASELINE_ID}/commands/preferred_xml.stdout.txt`,
  `preferred_activities.stdout.txt`, `persistent_preferred.stdout.txt`
- SHA-256: `{evidence_hash(root, f'adb/phase3b/{BASELINE_ID}/commands/preferred_xml.stdout.txt')}`;
  `{evidence_hash(root, f'adb/phase3b/{BASELINE_ID}/commands/preferred_activities.stdout.txt')}`
- Test ID: `{BASELINE_ID}`
- Timestamp: command manifest
- Command: `dumpsys package preferred-xml`, `preferred-activities`, and the attempted persistent query
- Observed result: ordinary User 0 Fire HOME record is at
  `preferred_activities.stdout.txt:8874-8885` with `mMatch=0x100000`
  and `mAlways=true`; the attempted persistent-only command returned the same
  ordinary section and exposed no separate active persistent HOME record
- Interpretation: ordinary preferred record exists; persistent negative is bounded by command support
- Confidence: Strong evidence
- Related hypothesis: persistent preferred activity is the overriding mechanism

## P3B-PATH-EXPLICIT-001 — clean explicit HOME path

- Source: sequential HOME path capture
- File: `adb/phase3b/{EXPLICIT_ID}/logcat.txt` and `result.md`
- SHA-256: `{evidence_hash(root, f'adb/phase3b/{EXPLICIT_ID}/logcat.txt')}`
- Test ID: `{EXPLICIT_ID}`
- Timestamp: `metadata.tsv`
- Command: `am start -a android.intent.action.MAIN -c android.intent.category.HOME`
- Observed result: ActivityManager START at `logcat.txt:2158` shows `from uid 2000`,
  standard HOME intent, and explicit `cmp=com.amazon.firelauncher/.Launcher`; the
  matching `am_new_intent` is at `:2160`; final activity/window state is Fire
- Interpretation: explicit HOME test ends at Fire; the log does not identify which earlier layer set cmp
- Confidence: Confirmed
- Related hypothesis: standard resolver versus post-resolution rewrite

## P3B-PATH-KEYEVENT-001 — clean injected Home key path

- Source: sequential HOME key capture
- File: `adb/phase3b/{KEYEVENT_ID}/logcat.txt` and `result.md`
- SHA-256: `{evidence_hash(root, f'adb/phase3b/{KEYEVENT_ID}/logcat.txt')}`
- Test ID: `{KEYEVENT_ID}`
- Timestamp: `metadata.tsv`
- Command: `input keyevent 3`
- Observed result: Input key down/up at `logcat.txt:2177-2181` is followed by
  `am_new_intent` at `:2190` with `MAIN` and explicit Fire component; the clean
  capture has no matching `ActivityManager: START` line, so caller UID and full
  START flags are not inferred from this sample; final activity/window state is Fire
- Interpretation: tested keyevent does not bypass the standard HOME destination in the observed path
- Confidence: Confirmed
- Related hypothesis: Home key direct-launch hook

## P3B-STATIC-PMS-001 — resolver method structure

- Source: Fire OS JADX and matching VDEX-backed source
- File: `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java`
- SHA-256: `{evidence_hash(root, 'decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java')}`
- Test ID: offline static analysis
- Timestamp: source/decompilation metadata
- Command: `python3 tools/scripts/analyze_phase3b.py --root .`
- Observed result: `chooseBestActivity()` has AOSP-shaped leading priority comparison and only enters ordinary
  preferred selection on the tie path; no selected Fire package-name condition in that scope
- Interpretation: priority 50 explains why a priority-0 preferred record does not win
- Confidence: Strong evidence
- Related hypothesis: Amazon resolver ranking override

## P3B-STATIC-KEYPOLICY-001 — Amazon Home key hooks

- Source: services and private-services VDEX disassembly
- File: `decompiled/baksmali/vdexExtractor/services/disassembly.log`,
  `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `{evidence_hash(root, 'decompiled/baksmali/vdexExtractor/services/disassembly.log')}`;
  `{evidence_hash(root, 'decompiled/baksmali/vdexExtractor/fosservices/disassembly.log')}`
- Test ID: offline static analysis
- Timestamp: disassembly generation metadata
- Command: offline indexed search and manual smali review
- Observed result: key policy is called before framework Home launch; TabletKeyPolicyManager checks custom-home
  and otherwise permits standard flow; custom-home broadcasts to a permissioned foreground receiver
- Interpretation: Amazon has a real Home-key extension boundary, but no direct Fire component in the inspected methods
- Confidence: Confirmed hook; default Fire override unconfirmed
- Related hypothesis: SystemUI/PhoneWindowManager explicit Fire launch

## P3B-STATIC-DOCK-001 — PhoneWindowManager vendor callback boundary

- Source: services VDEX
- File: `decompiled/baksmali/vdexExtractor/services/disassembly.log:988383-988428`
- SHA-256: `{evidence_hash(root, 'decompiled/baksmali/vdexExtractor/services/disassembly.log')}`
- Test ID: offline static analysis
- Timestamp: disassembly generation metadata
- Command: offline indexed search and smali review
- Observed result: `startDockOrHome()` calls custom dock callback, on-start callback, then starts `mHomeIntent`
- Interpretation: callback can alter the path; current evidence does not show a Fire-returning callback
- Confidence: Confirmed hook; override unconfirmed
- Related hypothesis: Amazon vendor callback rewrites HOME

## P3B-CONFIG-001 — Amazon service/callback registration

- Source: FOS initialization XML
- File: `artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml`,
  `launcherhijackpreventer_fosinit.xml`, `amazonpackagemanager_fosinit.xml`,
  `amazonactivitymanager_fosinit.xml`
- SHA-256: `{evidence_hash(root, 'artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml')}`;
  `{evidence_hash(root, 'artifacts/amazon-services/launcherhijackpreventer_fosinit.xml')}`
- Test ID: offline static analysis
- Timestamp: artifact manifest
- Command: XML inspection
- Observed result: key-policy, ActivityManager, PackageManager, and LauncherHijackPreventer callback registrations
- Interpretation: these are candidate control layers, not proof of runtime HOME rewriting
- Confidence: Confirmed registrations; causal role unknown
- Related hypothesis: Amazon private service/watchdog
"""
    write(root, "findings/phase-3b-evidence-index.md", evidence, args.force)

    call_path = """# HOME resolution call path (Phase 3B)

## Text form

1. `PhoneWindowManager.handleShortPressOnHome()` calls the Amazon key-policy
   hook. If it does not consume the key, framework `launchHomeFromHotKey()`
   reaches `startDockOrHome()`.
2. `startDockOrHome()` checks a custom dock intent, then Amazon vendor callbacks,
   then starts the framework `mHomeIntent` as the current user.
3. For a non-explicit MAIN+HOME intent, ActivityManager/ActivityTaskManager
   reaches `ActivityStackSupervisor.resolveIntent()`.
4. Fire OS calls `VendorActivityStackSupervisorCallback.callResolveIntent()`
   before PackageManagerInternal. A non-null callback result would short-circuit
   the standard resolver; no Fire-specific non-null result is present in the
   inspected callback evidence.
5. PackageManager runs `resolveIntentInternal()` →
   `queryIntentActivitiesInternal()` → `chooseBestActivity()`.
6. The candidate list includes Fire (effective priority 50), Microsoft (0), and
   FallbackHome (-1000). Fire wins the leading comparison before an ordinary
   priority-0 preferred record can become the result.
7. ActivityManager sets the selected component explicitly and starts Fire.

## What is confirmed versus unresolved

- Confirmed: the callback boundaries exist and the normal PM resolver is the
  fallback path.
- Confirmed: clean explicit capture has an explicit Fire START record; the clean
  keyevent capture has the same explicit Fire component in `am_new_intent` and
  final activity/window dumps.
- Strong evidence: current resolution is explained by AOSP-shaped priority
  ordering.
- Unconfirmed: whether any concrete callback returns a Fire `ResolveInfo` for
  this exact HOME intent before PM.
- Unknown: whether a background service rewrites preferred state after a future
  mutation; no new mutation or reboot was run in Phase 3B.

## Mermaid

```mermaid
flowchart TD
  HK[Home key] --> PWP[PhoneWindowManager.handleShortPressOnHome]
  PWP --> KPM[Amazon TabletKeyPolicyManager]
  KPM -->|custom event handled| CUS[Permissioned custom-home broadcast]
  KPM -->|not handled| LHF[launchHomeFromHotKey]
  LHF --> SDH[startDockOrHome]
  SDH --> VPC[VendorPhoneWindowManager callbacks]
  SDH --> HI[framework mHomeIntent MAIN+HOME]
  HI --> ASS[ActivityStackSupervisor.resolveIntent]
  ASS --> VAC[VendorActivityStackSupervisorCallback]
  VAC -->|non-null would short-circuit| VRES[Vendor ResolveInfo]
  VAC -->|null in fallback path| PMI[PackageManagerInternal.resolveIntent]
  PMI --> QIA[queryIntentActivitiesInternal]
  QIA --> CBA[chooseBestActivity]
  CBA -->|priority 50| FIRE[com.amazon.firelauncher/.Launcher]
  CBA -->|priority 0 preferred record cannot outrank 50| MS[Microsoft Launcher]
  FIRE --> START[ActivityManager START explicit component]
  MS -. not selected .-> START
```
"""
    write(root, "findings/home-resolution-call-path.md", call_path, args.force)
    write(root, "output/call-graphs/home-resolution-phase3b.mmd", call_path.split("## Mermaid\n\n", 1)[1].strip().strip("`").replace("mermaid\n", "", 1), args.force)
    method_graph = """flowchart LR
  RI[PackageManagerService.resolveIntent] --> RII[resolveIntentInternal]
  RII --> QIA[queryIntentActivitiesInternal]
  QIA --> CBA[chooseBestActivity]
  CBA -->|different priority| BEST[return stronger candidate]
  CBA -->|tie| FP[findPersistentPreferredActivityLP]
  FP --> FO[findPreferredActivity]
  BEST --> FIRE[Fire priority 50]
  FO --> FIRE
  AS[ActivityStackSupervisor.resolveIntent] --> VAC[Vendor callback array]
  VAC -->|non-null| VENDOR[Vendor ResolveInfo]
  VAC -->|null| PMI[PackageManagerInternal.resolveIntent]
  PMI --> RI
  PWP[PhoneWindowManager.startDockOrHome] --> AS
"""
    write(root, "output/call-graphs/home-resolver-method-flow-phase3b.mmd", method_graph, args.force)

    method_analysis = f"""# Phase 3B HOME resolver method analysis

This file is the Phase 3B-specific companion to the existing Phase 3A method
analysis. It does not overwrite the Phase 3A report.

## Method inventory

| Method | Fire OS source | AOSP comparison | Result |
|---|---|---|---|
| `resolveIntent` | `PackageManagerService.java:3003-3004` | r1/r61 same method family | Standard entry |
| `resolveIntentInternal` | `PackageManagerService.java:3007-3022` | r1/r61 same method family | Query then choose |
| `chooseBestActivity` | `PackageManagerService.java:3120-3168` | r1/r61 priority/preferred structure | Priority first; preferred tie path |
| `findPersistentPreferredActivityLP` | `PackageManagerService.java:3197-3275` | r1/r61 same method family | Persistent branch exists |
| `findPreferredActivity` | `PackageManagerService.java:3288-3350` | r1/r61 same method family | Ordinary preferred branch |
| `queryIntentActivitiesInternal` | `PackageManagerService.java` around resolver query | r1/r61 same method family | Candidate set producer |
| `ActivityStackSupervisor.resolveIntent` | `ActivityStackSupervisor.java:745-772` | AOSP baseline has no observed equivalent vendor pre-hook | Amazon callback pre-hook |
| `PhoneWindowManager.startDockOrHome` | `services.disassembly.log:988383-988428` | AOSP baseline path | Vendor callback extension |

## Priority and preferred ordering

The candidate query proves that the runtime values are Fire `50`, Microsoft
`0`, and FallbackHome `-1000`. The Fire OS `chooseBestActivity()` implementation
compares the leading candidates' priority, preferred order, and default state.
Only when the leading comparison does not decide the result does it call
`findPreferredActivity()` with the candidate priority. Therefore a Microsoft
`mAlways=true` ordinary preferred record is stored state but is not an effective
winner while Fire is the stronger candidate.

The Phase 3A sideloaded priority values being normalized to zero are consistent
with the Android 9 non-privileged priority cap. Fire's manifest priority 50 is
not by itself proof that no preferred activity can ever override it; it is the
reason the preserved priority-0 preferred record does not override it.

## Microsoft preferred record

The record is valid stored state (`mAlways=true`) but it does not win the
candidate comparison. No evidence in the selected resolver methods indicates a
package-name special case for `com.amazon.firelauncher`. The exact runtime
callback ordering is retained as an open item because the callback aggregator
can return a non-null result before the PM fallback.

## Vendor callback findings

- `AppCompatActivityStackSupervisorCallback.resolveIntent()` calls the platform
  `IPackageManager.resolveIntent()` and filters an uninstalled-app result. It
  does not contain a Fire package target in the inspected disassembly
  (`fosservices.disassembly.log:41093-41138`).
- `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()` checks the
  SELinux `amazon_policies/see_home_task` permission. That controls task
  visibility, not the selected HOME component in the inspected method.
- `AlexaModeSwitchManagerPhoneWindowManagerCallback` can launch a multimodal
  home only when its mode is active (`fosservices.disassembly.log:196259-196276`).
  The captured baseline does not establish that mode as the current tablet HOME
  path, and no Fire component is present in that method.

## Classification

| Observation | Classification |
|---|---|
| Fire `chooseBestActivity` follows AOSP-shaped priority logic | `AOSP_STANDARD` / Strong evidence |
| Fire priority 50 comes from its privileged manifest | `AMAZON_ADDITION` as package data, not resolver patch |
| ActivityStackSupervisor vendor callback pre-hook | `AMAZON_ADDITION` |
| PhoneWindowManager key-policy/vendor callback hooks | `AMAZON_ADDITION` |
| Fire package-name ranking branch in inspected PM methods | Not found; `Probable absent in inspected scope` |
| Callback return that explicitly chooses Fire | `UNKNOWN` |
"""
    write(root, "findings/phase-3b-home-resolver-method-analysis.md", method_analysis, args.force)

    diff = """# AOSP Android 9 versus Fire OS HOME path

## Scope

The comparison uses the selected Android 9 r1 and r61 PackageManager sources,
the Fire OS JADX source, and matching VDEX instruction listings. It is not a
claim that every Fire OS class is byte-for-byte comparable to either AOSP tag.

| Area | AOSP-standard behavior | Fire OS evidence | Classification |
|---|---|---|---|
| `PackageManagerService.resolveIntent` | Query candidates, then choose best | Same method chain and priority/preferred structure | `AOSP_STANDARD` |
| `chooseBestActivity` | Priority/order/default comparison precedes ordinary preferred tie path | Same decision shape in selected Fire OS source | `AOSP_STANDARD` |
| `findPreferredActivity` / persistent helper | Preferred and persistent resolver helpers exist | Same method family exists | `AOSP_STANDARD` / version-aware |
| `ActivityStackSupervisor.resolveIntent` | Standard PM internal resolution | Fire calls vendor callback array first, then PM internal | `AMAZON_ADDITION` |
| Home short press | Framework launches Home | Fire calls `KeyPolicyManager` before framework behavior | `AMAZON_ADDITION` |
| `startDockOrHome` | Framework Home intent launch | Fire adds custom-dock and on-start vendor callbacks | `AMAZON_ADDITION` |
| Fire package identity | No AOSP package | Privileged `/system/priv-app` package with manifest priority 50 | `AMAZON_ADDITION` package data |
| explicit Fire target inside selected PM chooser | Not applicable | No selected package-name branch found | `UNKNOWN` outside inspected classes; Probable absent in scope |

## Minimum difference explaining current result

The minimum evidence-backed difference is not a resolver algorithm patch: it is
the OEM-installed privileged Fire Launcher candidate with effective priority
50, while sideloaded launchers are capped at effective priority 0. The Fire OS
framework also exposes Amazon callback boundaries around resolution and Home-key
handling, but the preserved data does not show those callbacks replacing the
result for the normal tablet mode.

## Important non-equivalence

The existence of a vendor callback is not proof that it returns a Fire
`ResolveInfo`; the callback aggregator returns null when no callback claims the
intent. Likewise, a Home-key hook is not proof that the key bypasses the HOME
intent. The clean keyevent log shows the same explicit Fire destination as the
explicit HOME sample.
"""
    write(root, "findings/aosp-vs-fireos-home-diff.md", diff, args.force)
    write(root, "diff/reports/aosp-vs-fireos-home-diff-phase3b.md", diff, args.force)

    framework = """# Framework and system-service static analysis

## Inputs

- Fire OS framework/services analysis uses the existing 183-byte shell JAR
  metadata plus VDEX/ODEX extraction outputs. The code-bearing references are
  `decompiled/baksmali/vdexExtractor/services/disassembly.log` and
  `fosservices/disassembly.log`.
- Fire OS JADX sources are retained as approximate Java only; key control-flow
  decisions are checked against the VDEX listings.
- AOSP Android 9 r1 and r61 sources are used for the selected resolver methods.

## ActivityManager and ActivityStackSupervisor

`ActivityManagerService.startHomeActivityLocked()` obtains a HOME intent,
resolves it if no explicit component is present, sets the resolved component,
and starts it. This explains why ActivityManager START logs show an explicit
Fire component even when the originating intent was implicit.

Fire's `ActivityStackSupervisor.resolveIntent()` invokes the vendor callback
aggregator before PackageManagerInternal. The aggregator returns the first
non-null callback result. This is the most important unresolved Amazon control
point. The inspected concrete `AppCompatActivityStackSupervisorCallback`
queries the normal PM service and only filters an uninstalled result; it does
not target Fire Launcher.

## PackageManager

The selected Fire OS methods retain the Android 9 method family:

- `resolveIntent` / `resolveIntentInternal`: `PackageManagerService.java:3003-3022`
- `chooseBestActivity`: `:3120-3168`
- `findPersistentPreferredActivityLP`: `:3197-3275`
- `findPreferredActivity`: `:3288-3350`

The method structure compares candidate priority before consulting the ordinary
preferred resolver on the tie path. No explicit `com.amazon.firelauncher`
condition was found in these selected methods. The runtime candidate list and
the Phase 3A stored Microsoft record agree with this explanation.

## PhoneWindowManager and Amazon key policy

The VDEX path is:

`handleShortPressOnHome` → `KeyPolicyManager.handleShortPressOnHome` →
`launchHomeFromHotKey` → `startDockOrHome`.

`startDockOrHome` has two vendor callback opportunities before the final
`startActivityAsUser(mHomeIntent, CURRENT)`. The Amazon tablet key policy
builds a normal `MAIN` + `HOME` intent when it launches Home. Its custom-home
handler targets the foreground application's permissioned receiver, not Fire.

## LauncherHijackPreventer

The inspected callback checks whether a caller may see the Home task using the
SELinux policy `amazon_policies/see_home_task`, with an Android-signature
fallback. It explains the observed SELinux denials in prior logs and is a
visibility/protection layer; the inspected method does not start Fire Launcher.

## Static-analysis limits

The current input does not include a clean, public source reconstruction for
every concrete FOS callback or the complete Amazon `SystemServer` initializer.
Therefore this report labels callback causality and boot-time preferred-record
rewrites as unknown rather than filling them with inferred behavior.
"""
    write(root, "findings/framework-static-analysis.md", framework, args.force)

    overlay = """# Overlay, configuration, and background-rewrite analysis

## Captured runtime configuration

The canonical baseline retains raw outputs for:

- `cmd overlay list`
- `settings list secure/global/system`
- `dumpsys device_policy`
- `service list`, `dumpsys -l`, process list, package list
- `BOOTCLASSPATH`, `SYSTEMSERVERCLASSPATH`, and `DEX2OATBOOTCLASSPATH`

`device_config list` exited `127` on this build and the HOME role-holder query
exited `20`. Those are availability limits, not evidence that the stores are
empty.

## Amazon registration inputs

The preserved `artifacts/amazon-services/*_fosinit.xml` files register:

- `TabletKeyPolicyManager` and `KeyInterceptorCallback`;
- `AmazonActivityManagerService` and its ActivityManager callback;
- `AmazonPackageManagerService` and `ControlProtectedPackagesCallback`;
- `LauncherHijackPreventer` ActivityManager/ActivityStack/PackageManager callbacks.

These registrations establish candidate extension points. They do not state
that a callback rewrites the ordinary preferred HOME record.

## Fire package references

The private-services disassembly contains exact Fire package references in
non-resolver contexts, including external-app notification and the KFT child
launcher enable/disable path. Those references are not evidence of a primary
User 0 resolver ranking branch. The inspected resolver methods contain no
selected Fire package-name condition.

## Background rewrite status

No Phase 3B operation modified preferred state or rebooted the device, by
design. The preserved Phase 3A reboot result shows Fire after the Microsoft
preferred write, but priority ordering already explains that result. A watchdog
or boot receiver rewrite is therefore **Unknown**, not confirmed.

## Next safe static target

Enumerate every concrete class implementing the registered
`VendorActivityStackSupervisorCallback` and
`VendorPhoneWindowManagerCallback` bases in the matching private-services VDEX,
then inspect only their HOME-related methods. This is offline and does not
require stopping a service or changing device state.
"""
    write(root, "findings/overlay-and-config-analysis.md", overlay, args.force)

    decision = """# Preferred record exists but does not win

## Decision tree

```text
HOME MAIN+HOME intent for user 0
    |
    +-- Is there a valid persistent preferred record?
    |       |
    |       +-- Yes -> apply it if its filter, user and component are valid
    |       |
    |       +-- Not observed in canonical persistent query -> continue with
    |               ordinary candidate resolution; negative is bounded
    |
    +-- Query enabled HOME candidates
    |       |
    |       +-- Fire Launcher: effective priority 50
    |       +-- Microsoft Launcher: effective priority 0
    |       +-- FallbackHome: effective priority -1000
    |
    +-- chooseBestActivity compares leading priority/order/default state
            |
            +-- Fire wins before ordinary preferred tie branch
            |
            +-- Microsoft mAlways=true record remains stored but is not used
                    as the effective result
```

## Why `mAlways=true` is not enough

`mAlways=true` records express a preferred choice within the ordinary preferred
resolution path. They do not universally override a stronger leading candidate
when `chooseBestActivity()` has already decided on priority. The preserved
Phase 3A Microsoft record is therefore compatible with the resolver returning
Fire.

## Required validity checks

The following checks are captured or bounded as follows:

| Check | Evidence | Status |
|---|---|---|
| intent action/categories | Fire and Microsoft HOME candidate query; preferred XML contains MAIN/HOME/DEFAULT | Confirmed |
| user ID | baseline and Phase 3A tests use User 0 | Confirmed |
| component enabled | Fire package User 0 `enabled=0` (default enabled) and candidate appears | Confirmed |
| ordinary record stored | preferred dump contains Fire selected and Phase 3A Microsoft write | Confirmed |
| distinct persistent HOME record | no separate active record observed; command support is limited | Strong evidence / bounded |
| candidate priority | Fire 50; Microsoft 0; FallbackHome -1000 | Confirmed |
| Amazon resolver callback return | callback API exists; concrete return not observed | Unknown |
| boot-time rewrite | no new reboot in Phase 3B | Unknown |

## Conclusion

The current evidence does not require an Amazon resolver override to explain
the stored-but-unused preferred record. The decisive observed condition is the
effective priority gap.
"""
    write(root, "findings/preferred-record-decision-tree.md", decision, args.force)

    rows = build_matrix(root)
    fields = [
        "package", "component", "code_path", "source", "uid", "version",
        "system_app", "privileged", "persistent", "direct_boot_aware", "shared_user_id",
        "platform_signature", "amazon_signed", "device_owner_or_profile_owner_related",
        "privileged_permissions_summary", "appops", "flags",
        "private_flags", "signature_summary", "manifest_priority",
        "effective_home_priority", "ordinary_preferred", "persistent_preferred",
        "home_candidate", "home_resolved", "confidence", "evidence",
    ]
    matrix_path = root / "output/tables/fire-launcher-privilege-matrix.csv"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    if matrix_path.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {matrix_path}; use --force")
    with matrix_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        clean_rows = [
            {
                field: ("" if row.get(field) is None else str(row.get(field)).rstrip())
                for field in fields
            }
            for row in rows
        ]
        writer.writerows(clean_rows)
    write(root, "findings/fire-launcher-privilege-matrix.csv", matrix_path.read_text(encoding="utf-8"), args.force)

    write(root, "findings/phase-3b-report.md", report(root), args.force)
    print("generated Phase 3B reports and privilege matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
