#!/usr/bin/env python3
"""Generate Phase 3C reports and matrices from preserved evidence only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


BASELINE = "PHASE3C-BASELINE-20260803-02"
PILOT = "PHASE3C-PREFERRED-P0-01"
EXPERIMENT = "PHASE3C-PREFERRED-P0-02"
LOGGED_EXPERIMENT = "PHASE3C-PREFERRED-P0-03"
FIRE = "com.amazon.firelauncher/.Launcher"
TEST = "org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity"
SETTING_TERMS = re.compile(
    r"home|launcher|default|resolver|preferred|amazon|fire|navigation|kiosk|desktop|role|activity|intent|startup|device_provisioned|user_setup_complete",
    re.I,
)
SENSITIVE = re.compile(
    r"account|customer|default_pfm|foreground_customer|first_cold_start|wifi_p2p_device_name",
    re.I,
)
STATIC_TEXTS: list[tuple[str, str, list[str]]] | None = None
STATIC_CACHE: dict[str, tuple[str, str]] = {}


def p(root: Path, relative: str) -> Path:
    return root / relative


def read(root: Path, relative: str) -> str:
    target = p(root, relative)
    return target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""


def digest(target: Path) -> str:
    if not target.is_file():
        return "MISSING"
    h = hashlib.sha256()
    with target.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def snap(name: str, relative: str) -> str:
    return f"adb/phase3c/{name}/{relative}"


def exit_code(root: Path, relative: str) -> str:
    return read(root, relative).strip() or "MISSING"


def write(root: Path, relative: str, content: str) -> None:
    target = p(root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def settings(root: Path) -> list[dict[str, str]]:
    rows = []
    for namespace in ("system", "secure", "global"):
        text = read(root, snap(BASELINE, f"settings/{namespace}.stdout.txt"))
        for line in text.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            if SETTING_TERMS.search(key):
                rows.append(
                    {
                        "namespace": namespace,
                        "key": key,
                        "baseline_value": "<redacted>" if SENSITIVE.search(key) else value,
                    }
                )
    return rows


def static_matches(root: Path, term: str, limit: int = 6) -> tuple[str, str]:
    global STATIC_TEXTS
    if term in STATIC_CACHE:
        return STATIC_CACHE[term]
    # Avoid repeatedly scanning broad Android vocabulary such as activity and
    # intent. The inventory still records those keys, but exact causal code
    # evidence is only indexed for launcher-specific terms.
    if term.lower() in {"activity", "intent", "default", "role"} or len(term) < 6:
        result = ("NOT INDEXED (generic key)", "NOT INDEXED (generic key)")
        STATIC_CACHE[term] = result
        return result
    reads: list[str] = []
    writes: list[str] = []
    if STATIC_TEXTS is None:
        STATIC_TEXTS = []
        roots = [
            root / "decompiled/jadx/firelauncher",
            root / "decompiled/jadx/systemui",
            root / "decompiled/jadx/settings",
            root / "decompiled/jadx/amazon-settings",
            root / "decompiled/baksmali/vdexExtractor",
            root / "decompiled/baksmali/vdex-extracted",
            root / "artifacts/amazon-services",
        ]
        for base in roots:
            if not base.is_dir():
                continue
            for file in base.rglob("*"):
                if not file.is_file() or file.stat().st_size > 8 * 1024 * 1024:
                    continue
                try:
                    text = file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                STATIC_TEXTS.append((str(file.relative_to(root)), text.lower(), text.splitlines()))
    wanted = term.lower()
    for relative, lower_text, lines in STATIC_TEXTS:
        if wanted not in lower_text:
            continue
        for number, line in enumerate(lines, 1):
            if wanted not in line.lower():
                continue
            item = f"{relative}:{number}"
            target = writes if ("put" in line.lower() or "write" in line.lower()) else reads
            if item not in target:
                target.append(item)
            if len(reads) >= limit and len(writes) >= limit:
                break
        if len(reads) >= limit and len(writes) >= limit:
            break
    result = ("; ".join(reads[:limit]) or "NONE OBSERVED", "; ".join(writes[:limit]) or "NONE OBSERVED")
    STATIC_CACHE[term] = result
    return result


def effect(key: str) -> str:
    lower = key.lower()
    if "tb_custom_launcher" in lower:
        return "Launcher-shaped runtime key; no inspected reader/writer"
    if "launcher" in lower or "fire" in lower:
        return "Launcher UI/content; no HOME resolver evidence"
    if "home" in lower or "default" in lower or "preferred" in lower or "resolver" in lower:
        return "Could affect defaults only with a matching reader"
    if "navigation" in lower:
        return "Navigation UI; not a resolver input in inspected code"
    if "device_provisioned" in lower or "user_setup_complete" in lower:
        return "Provisioning state; not a HOME selector"
    return "Keyword candidate; no causal HOME evidence"


def build_settings_matrix(root: Path) -> None:
    fields = [
        "namespace", "key", "baseline_value", "reader_class", "writer_class",
        "package", "suspected_effect", "writable_by_shell", "reversible",
        "tested", "result",
    ]
    targets = [
        p(root, "output/tables/phase-3c-settings-matrix.csv"),
        p(root, "findings/phase-3c-settings-key-inventory.csv"),
    ]
    rows = []
    for row in settings(root):
        readers, writers = static_matches(root, row["key"])
        source = readers if readers != "NONE OBSERVED" else writers
        if "firelauncher" in source.lower():
            package = "com.amazon.firelauncher"
        elif "systemui" in source.lower():
            package = "com.android.systemui"
        elif "settings" in source.lower():
            package = "Settings/SettingsProvider"
        elif "vdex" in source.lower() or "fosservices" in source.lower():
            package = "Amazon framework services"
        else:
            package = "UNKNOWN"
        if row["key"] in {"device_provisioned", "user_setup_complete"}:
            result = "REJECTED: provisioning mutation outside safe HOME scope"
        else:
            result = "NOT TESTED: no HOME-specific reader/writer evidence"
        rows.append(
            {
                **row,
                "reader_class": readers,
                "writer_class": writers,
                "package": package,
                "suspected_effect": effect(row["key"]),
                "writable_by_shell": "NOT TESTED",
                "reversible": "YES with original snapshot",
                "tested": "NO",
                "result": result,
            }
        )
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


def resolver_for(root: Path, experiment: str, phase: str) -> str:
    return read(root, snap(experiment, f"{phase}/package/home_resolve.stdout.txt")).strip().replace("\n", " | ")


def resolver(root: Path, phase: str) -> str:
    return resolver_for(root, EXPERIMENT, phase)


def foreground(root: Path, phase: str) -> str:
    text = read(root, snap(EXPERIMENT, f"{phase}/activity/activities.stdout.txt"))
    lines = [
        line.strip()
        for line in text.splitlines()
        if any(x in line for x in ("mResumedActivity", "topResumedActivity", "mFocusedApp", "mCurrentFocus", "realActivity"))
    ]
    return " | ".join(lines[:5]) or "NOT OBSERVED"


def preferred_for(root: Path, experiment: str, phase: str) -> str:
    text = read(root, snap(experiment, f"{phase}/package/preferred_xml.stdout.txt"))
    match = re.search(r'<item name="([^"]+)"', text)
    return match.group(1) if match else "NONE OBSERVED"


def preferred(root: Path, phase: str) -> str:
    return preferred_for(root, EXPERIMENT, phase)


def build_experiment_matrix(root: Path) -> None:
    fields = [
        "experiment", "mutation", "immediate_result", "resolver", "preferred_record",
        "home_key_result", "explicit_home_result", "lock_unlock_result",
        "reboot_result", "rollback_result", "classification", "evidence",
    ]
    target = p(root, "output/tables/phase-3c-experiment-matrix.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "experiment": PILOT,
            "mutation": "Wrong p0 class name",
            "immediate_result": "IllegalArgumentException; no test path run",
            "resolver": "Fire", "preferred_record": "unchanged",
            "home_key_result": "not run", "explicit_home_result": "not run",
            "lock_unlock_result": "not run", "reboot_result": "not run",
            "rollback_result": "emergency restore/uninstall exit 0",
            "classification": "Rejected test harness",
            "evidence": f"adb/phase3c/{PILOT}/mutations/set_preferred.stderr.txt",
        },
        {
            "experiment": EXPERIMENT,
            "mutation": "Install p0 and set ordinary preferred HOME",
            "immediate_result": "Success; exact HOME filter and mAlways=true",
            "resolver": resolver(root, "after_preferred"),
            "preferred_record": preferred(root, "after_preferred"),
            "home_key_result": "Fire", "explicit_home_result": "Fire",
            "lock_unlock_result": "Fire", "reboot_result": "Fire; record persisted",
            "rollback_result": "Fire restore and p0 uninstall exit 0",
            "classification": "E: writable but ineffective HOME state",
            "evidence": "P3C-PREF-001; P3C-HOME-001; P3C-REBOOT-001; P3C-ROLLBACK-001",
        },
        {
            "experiment": "HOME role",
            "mutation": "cmd role holders android.app.role.HOME --user 0",
            "immediate_result": "No holder output; command status preserved",
            "resolver": "not changed", "preferred_record": "not applicable",
            "home_key_result": "not run", "explicit_home_result": "not run",
            "lock_unlock_result": "not run", "reboot_result": "not run",
            "rollback_result": "none", "classification": "Unavailable API",
            "evidence": "P3C-ROLE-001",
        },
        {
            "experiment": "device_config",
            "mutation": "device_config list",
            "immediate_result": "Command unavailable; status 127",
            "resolver": "not changed", "preferred_record": "not applicable",
            "home_key_result": "not run", "explicit_home_result": "not run",
            "lock_unlock_result": "not run", "reboot_result": "not run",
            "rollback_result": "none", "classification": "Unavailable API",
            "evidence": "P3C-ROLE-001",
        },
    ]
    logged_dir = p(root, f"adb/phase3c/{LOGGED_EXPERIMENT}")
    if logged_dir.is_dir():
        rows.insert(
            2,
            {
                "experiment": LOGGED_EXPERIMENT,
                "mutation": "Logged repeat of ordinary preferred HOME experiment",
                "immediate_result": "Success; event logcat captured",
                "resolver": resolver_for(root, LOGGED_EXPERIMENT, "after_preferred"),
                "preferred_record": preferred_for(root, LOGGED_EXPERIMENT, "after_preferred"),
                "home_key_result": "Fire", "explicit_home_result": "Fire",
                "lock_unlock_result": "Fire", "reboot_result": "Fire; record persisted",
                "rollback_result": "Fire restore and p0 uninstall exit 0",
                "classification": "E: writable but ineffective HOME state; logged",
                "evidence": "P3C-LOGCAT-001; P3C-PREF-001",
            },
        )
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fingerprint(root: Path) -> str:
    for line in read(root, snap(BASELINE, "properties/getprop.stdout.txt")).splitlines():
        if "[ro.build.fingerprint]:" in line:
            return line.split(":", 1)[1].strip().strip("[]")
    return "UNKNOWN"


def reports(root: Path) -> None:
    base = f"adb/phase3c/{BASELINE}"
    exp = f"adb/phase3c/{EXPERIMENT}"
    logged_exp = f"adb/phase3c/{LOGGED_EXPERIMENT}"
    fire_result = read(root, f"{base}/package/home_resolve.stdout.txt").strip().replace("\n", " | ")
    p0_record = preferred(root, "after_preferred")
    reboot_record = preferred(root, "after_reboot")
    final_record = preferred(root, "after_rollback")

    write(root, "findings/phase-3c-settings-key-analysis.md", f"""# Phase 3C settings key analysis

The canonical input is {base}. The inventory is generated from all three
settings list outputs and exact-string searches in the existing Fire Launcher,
Settings, SystemUI, and Amazon framework decompilations.

Runtime launcher-shaped keys include tb_custom_launcher,
firelauncher_appsgrid_version, launcher_zero_margin_enabled, and
LAUNCHER_FTUE_FLAG. The inspected code has UI/content readers for some of
these keys, but no HOME-selector reader/writer; tb_custom_launcher itself had
no exact reader/writer. They were not randomly modified.
device_provisioned and user_setup_complete are provisioning state and were
rejected as unsafe HOME experiments.

Status:

- 已證實: no tested settings key changed HOME; system and secure settings were
  unchanged before and after rollback.
- 高可信推論: tb_custom_launcher is legacy/tool or UI state on this build,
  not the PackageManager HOME selector.
- 待驗證: an uncollected native/account service could read a key indirectly.
- 因風險拒絕測試: provisioning and navigation-bar settings.

The global differences after reboot were boot_count and atz_response_provider
timestamps, not launcher control. Raw values remain in {base}/settings; the
derived inventory redacts identity-shaped values.
""")

    write(root, "findings/phase-3c-preferred-activity-analysis.md", f"""# Phase 3C preferred activity analysis

Before mutation, preferred XML selected {FIRE}. After set-home-activity
targeted p0, XML selected {p0_record}; the preferred dump reported mAlways=true
with MAIN, HOME, and DEFAULT. Resolver still returned {fire_result}.

After one reboot, p0 record {reboot_record} remained stored, but resolver and
foreground remained Fire. Rollback wrote {final_record} back and p0 uninstall
returned exit 0.

Decision tree:

    set-home-activity(p0)
      -> record written: exact filter, mAlways=true
      -> p0 enabled/queryable: effective priority 0
      -> no separate active persistent HOME record observed
      -> chooseBestActivity compares Fire priority 50 first
      -> ordinary priority-0 preferred record is not selected
      -> resolver and Home key remain Fire
      -> reboot preserves record, not effectiveness

已證實: writable ordinary preferred state is not sufficient.
高可信推論: the observed failure point is candidate ranking before the
ordinary preferred tie branch.
待驗證: a concrete non-null Amazon resolve callback for this exact intent.
""")

    write(root, "findings/phase-3c-home-callback-analysis.md", """# Phase 3C Home callback analysis

Phase 3B static evidence remains the code baseline. PhoneWindowManager calls
the Amazon KeyPolicyManager hook before the framework Home path. startDockOrHome
exposes vendor PhoneWindowManager callbacks. ActivityStackSupervisor calls the
VendorActivityStackSupervisorCallback before PackageManagerInternal.

The inspected Amazon AppCompatActivityStackSupervisorCallback delegates to
IPackageManager.resolveIntent and filters uninstalled apps; it does not name
Fire Launcher. LauncherHijackPreventerActivityStackCallback.canSeeHomeTask is
a visibility/policy check, not a direct Fire launch in the inspected method.

The Phase 3C p0 mutation changed the preferred XML but did not change resolver
or foreground output at Home key, explicit HOME, lock/unlock, or reboot.

已證實: callback boundaries exist.
高可信推論: the observed normal path falls through to the standard resolver.
待驗證: a callback could return a special result in an unobserved mode,
profile, or native service condition.
""")

    write(root, "findings/phase-3c-overlay-analysis.md", f"""# Phase 3C overlay and runtime-resource analysis

The canonical cmd overlay list contained only internal cutout overlays and
com.android.systemui.theme.dark: {base}/overlay/list.stdout.txt.
No mutable Fire Launcher, HOME resolver, or default-home overlay was observed.
No overlay was switched in Phase 3C.

已證實: no relevant enabled overlay was observed in the baseline.
高可信推論: overlay switching is not needed to explain p0's stored-but-unused
preferred record.
待驗證: an overlay in an unlisted partition or another firmware build.
因風險拒絕測試: changing core SystemUI/framework overlays.
""")

    write(root, "findings/phase-3c-fallback-analysis.md", f"""# Phase 3C startup-failure and fallback analysis

No crash, forced-stop, missing-activity, or intentionally failing Launcher was
executed. The p0 APK was a normal reversible test app. This avoids a crash
loop or a preferred component without a recovery Activity.

p0 was installed only for {EXPERIMENT}, removed with pm uninstall --user 0
exit 0, and absent from the final pm path. Fire remained installed, visible,
unsuspended, unstopped, and enabled. Final HOME resolver and foreground were
Fire.

待驗證: retry limits and fallback behavior after a test component fails. The
smallest safe next test is a dedicated recovery-first APK; it was deferred.
""")

    write(root, "findings/phase-3c-workaround-classification.md", """# Phase 3C workaround classification

| Class | Result | Status |
|---|---|---|
| A. True HOME replacement | ordinary p0 preferred record does not change resolver | 已排除 |
| B. Persistent system setting workaround | no supported HOME setting reader found | 待驗證 |
| C. Temporary shell workaround | explicit activity start can display a launcher, not HOME | 高可信推論 |
| D. Accessibility/foreground workaround | not implemented; no hidden persistence designed | 待驗證 |
| E. Invalid/unavailable | p0 preferred state ineffective; HOME role/device_config unavailable | 已證實 |
| F. High risk | Fire mutation, core overlay, provisioning, Device Owner | 因風險拒絕測試 |

No persistent no-root HOME replacement was confirmed.
""")

    write(root, "findings/phase-3c-risk-register.md", """# Phase 3C risk register

| Operation | Decision | Rollback or reason |
|---|---|---|
| Ordinary preferred HOME write | Executed once | set Fire preferred |
| Test APK install/remove | Executed once | uninstall p0 exit 0 |
| Settings mutation | Not executed | no exact HOME reader/writer |
| HOME role set | Not executed | role API output unavailable |
| device_config mutation | Not executed | command unavailable |
| Core overlay switch | Rejected | SystemUI/navigation risk |
| Fire package state/data | Prohibited | project safety boundary |
| Device Owner/provisioning | Rejected | possible reset requirement |
| Crash/fallback APK | Deferred | recovery-first APK required |
| Reboot | Executed once | ADB returned and state was captured |

No stop condition was triggered. Final ADB state was device and Fire HOME was
resolved.
""")

    logged_note = (
        f"Supplemental logged run: {logged_exp}; event logcats were captured "
        "around preferred write, Home key, explicit HOME, lock/unlock, reboot, "
        "rollback, and test-package removal."
        if p(root, logged_exp).is_dir()
        else "No supplemental event-log run is present in this checkout."
    )
    write(root, "findings/phase-3c-report.md", f"""# Phase 3C report — HOME selection state mutation experiments

## Executive summary

No shell-writable state tested in Phase 3C produced a true third-party HOME
replacement without modifying Fire Launcher.

The controlled p0 mutation successfully wrote an exact MAIN+HOME+DEFAULT
ordinary preferred record with mAlways=true. The record survived one reboot.
Nevertheless resolver remained {fire_result}, Home key and explicit HOME
remained Fire, and foreground remained Fire. This directly explains why
set-home-activity can report success without changing effective HOME.

The strongest explanation remains the Phase 3B/AOSP-shaped chooseBestActivity
ordering: Fire effective priority 50 wins before an ordinary priority-0
preferred record can be used as a tie-breaker. A concrete Amazon callback
override is not proven.

## Evidence status

- 已證實: baseline, p0 preferred write, p0 persistence, Fire result through
  Home key, explicit HOME, lock/unlock, reboot, and explicit rollback.
- 高可信推論: ordinary preferred state is lower priority than Fire in the
  observed resolver path.
- 待驗證: non-null Amazon resolve callback, native indirect settings reader,
  and intentional failure fallback.
- 已排除: p0 ordinary preferred state as a true HOME replacement.
- 因風險拒絕測試: Fire mutation, core overlays, provisioning/Device Owner,
  and crash-loop fallback.

## Device and evidence

- Model: KFTRWI
- Fingerprint: {fingerprint(root)}
- Fire OS: 7.0
- Security patch: 2024-02-01
- Canonical snapshot: {base}
- Experiment: {exp}
- {logged_note}

The candidate set was Fire priority 50, Microsoft priority 0, p0 priority 0
during the experiment, and FallbackHome -1000.

## Preferred mutation and rollback

Before: preferred XML selected Fire.

After write: XML selected {p0_record}; preferred dump had mAlways=true; query
still selected Fire.

After reboot: XML still selected {reboot_record}; query and foreground remained
Fire.

Rollback: XML selected {final_record}; restore and p0 uninstall returned exit
0. Final p0 path was absent and Fire remained installed/enabled/visible/
unsuspended.

## Settings, roles, AppOps, overlays, callbacks

Settings were captured but not changed. Custom launcher-shaped keys had no
HOME-selector reader/writer evidence. HOME role holder output was empty with a
non-success status; device_config was unavailable. Overlay listing had no
relevant mutable HOME overlay. AppOps were captured but no HOME-specific
mutation was justified.

Amazon callback boundaries are documented separately. The experiment shows no
third-party or Fire-specific ResolveInfo returned by an observed callback.

## Final classification

The nearest safe route is a temporary visible explicit Launcher start, not a
HOME replacement. The next highest-value hypothesis is a positive trace of a
non-null Amazon resolveIntent callback during a HOME request, including its
caller/service and returned component.

## Reproduction

    tools/scripts/capture_phase3c_state.sh --serial SERIAL --test-id ID --output DIR
    tools/scripts/run_phase3c_preferred_experiment.sh --serial SERIAL --test-id ID --apk tools/test-launcher/dist/20260803-jdk26/org.fireosresearch.home.p0.apk --output DIR --reboot --lock-unlock --approve-state-change
    tools/scripts/compare_phase3c_state.py --before DIR/before --after DIR/after_rollback --output DIR/rollback-diff.md

The runner's restore plan contains only Fire preferred state and p0 absent
state; it never replays all settings.
""")

    base_sha = digest(p(root, f"{base}/sha256sums.txt"))
    exp_resolve_sha = digest(p(root, f"{exp}/after_preferred/package/home_resolve.stdout.txt"))
    pref_xml_sha = digest(p(root, f"{exp}/after_preferred/package/preferred_xml.stdout.txt"))
    rollback_sha = digest(p(root, f"{exp}/mutations/restore.exit_code.txt"))
    evidence = f"""# Phase 3C evidence index

All raw command output is preserved under adb/phase3c. Each snapshot and
experiment has a SHA-256 manifest. Unavailable command output is not treated
as negative runtime evidence.

## P3C-BASE-001 — canonical baseline

- Source: Phase 3C-0 read-only snapshot
- File: {base}/summary.md and {base}/sha256sums.txt
- SHA-256: {base_sha}
- Test ID: {BASELINE}
- Command: capture_phase3c_state.sh with explicit serial
- Observed: Fire HOME resolver priority 50; settings, package, activity,
  role, policy, overlay, appops, user and XML probes preserved.
- Interpretation: canonical pre-mutation state
- Confidence: Confirmed

## P3C-ROLE-001 — role/device_config availability

- Source: read-only command probes
- File: {base}/config/home_role_holders.stdout.txt,
  {base}/config/home_role_holders.exit_code.txt,
  {base}/config/device_config.exit_code.txt
- Test ID: {BASELINE}
- Command: cmd role holders android.app.role.HOME --user 0; device_config list
- Observed: no HOME holder output and device_config command unavailable
- Interpretation: no safe role/device_config mutation target on this build
- Confidence: Confirmed availability result

## P3C-PREF-001 — ordinary preferred record writes but does not win

- Source: controlled p0 experiment
- File: {exp}/after_preferred/package/preferred_xml.stdout.txt,
  {exp}/after_preferred/package/preferred_activities.stdout.txt,
  {exp}/after_preferred/package/home_resolve.stdout.txt
- SHA-256: preferred XML {pref_xml_sha}; resolver {exp_resolve_sha}
- Test ID: {EXPERIMENT}
- Command: cmd package set-home-activity --user 0 {TEST}
- Observed: success; exact MAIN+HOME+DEFAULT record selected p0 with
  mAlways=true; resolver still selected Fire priority 50
- Interpretation: preferred storage is not the decisive selection layer
- Confidence: Confirmed

## P3C-HOME-001 — Home entry paths remain Fire

- Source: p0 experiment snapshots
- File: {exp}/after_home_key, {exp}/after_explicit_home,
  {exp}/after_lock_unlock
- Test ID: {EXPERIMENT}
- Command: input keyevent 3; am start MAIN+HOME; power key lock/unlock
- Observed: resolver, task, and foreground remained Fire
- Interpretation: preferred mutation did not change either tested HOME path
- Confidence: Confirmed

## P3C-REBOOT-001 — preferred record persists but is ineffective

- Source: one controlled reboot after safe preferred mutation
- File: {exp}/after_reboot/package/preferred_xml.stdout.txt,
  {exp}/after_reboot/package/home_resolve.stdout.txt,
  {exp}/after_reboot/activity/activities.stdout.txt
- Test ID: {EXPERIMENT}
- Command: adb reboot; wait for sys.boot_completed=1
- Observed: p0 record persisted; resolver and foreground were Fire
- Interpretation: persistence is distinct from resolver effectiveness
- Confidence: Confirmed

## P3C-ROLLBACK-001 — explicit rollback

- Source: restore plan and final snapshot
- File: {exp}/mutations/restore.exit_code.txt,
  {exp}/mutations/uninstall_test.exit_code.txt,
  {exp}/after_rollback/package/home_resolve.stdout.txt
- SHA-256: restore status {rollback_sha}
- Test ID: {EXPERIMENT}
- Command: restore Fire preferred; pm uninstall --user 0 p0
- Observed: both exit 0; p0 absent; Fire installed/enabled/visible/unsuspended
- Interpretation: complete rollback succeeded
- Confidence: Confirmed

## P3C-HARNESS-001 — rejected pilot

- Source: first runner attempt
- File: adb/phase3c/{PILOT}/mutations/set_preferred.stderr.txt
- Test ID: {PILOT}
- Observed: IllegalArgumentException because the runner used the wrong class
  name; emergency restore/uninstall exit 0
- Interpretation: test harness failure, not Fire behavior
- Confidence: Confirmed

## P3C-SETTINGS-001 — settings inventory boundary

- Source: baseline settings and static search
- File: output/tables/phase-3c-settings-matrix.csv,
  findings/phase-3c-settings-key-inventory.csv and
  findings/phase-3c-settings-key-analysis.md
- Test ID: {BASELINE}
- Observed: launcher-shaped custom keys had no HOME-selector reader/writer in
  inspected code; no settings mutation was executed
- Interpretation: random settings writes were rejected by evidence standard
- Confidence: Strong evidence

## P3C-OVERLAY-001 — overlay boundary

- Source: overlay list/dump
- File: {base}/overlay/list.stdout.txt and {base}/overlay/dump.stdout.txt
- Test ID: {BASELINE}
- Observed: only internal cutout and SystemUI dark overlays; no HOME-specific
  mutable overlay
- Interpretation: no justified overlay mutation
- Confidence: Confirmed observation

## P3C-CALLBACK-001 — Amazon callback remains open

- Source: Phase 3B static evidence
- File: decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772;
  decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:41093-41138
- Test ID: PHASE3B
- Observed: vendor resolve callback boundary exists; inspected implementation
  delegates to PM and does not name Fire
- Interpretation: callback participation possible, direct override unproven
- Confidence: Strong evidence / unresolved return value
"""
    if p(root, f"adb/phase3c/{LOGGED_EXPERIMENT}").is_dir():
        evidence += f"""

## P3C-LOGCAT-001 — logged preferred experiment

- Source: supplemental controlled p0 experiment with event logcat capture
- File: adb/phase3c/{LOGGED_EXPERIMENT}/logs/set_preferred.logcat.txt,
  adb/phase3c/{LOGGED_EXPERIMENT}/logs/home_key.logcat.txt,
  adb/phase3c/{LOGGED_EXPERIMENT}/logs/explicit_home.logcat.txt,
  adb/phase3c/{LOGGED_EXPERIMENT}/logs/after_reboot.logcat.txt,
  adb/phase3c/{LOGGED_EXPERIMENT}/logs/restore.logcat.txt and final SHA-256
  manifest
- Test ID: {LOGGED_EXPERIMENT}
- Command: clear logcat, perform one controlled event, dump all buffers;
  repeat for the recorded mutation and rollback boundaries
- Observed: all logcat dump commands exited 0; the matching snapshots still
  resolved Fire before, after preferred write, after Home/explicit HOME,
  after lock/unlock, after reboot, and after rollback
- Interpretation: event-level raw logcat is preserved, but the state
  snapshots remain the authoritative resolver result; no callback override is
  inferred from logcat alone
- Confidence: Confirmed evidence preservation; Strong evidence for unchanged
  observed result
"""
    write(root, "findings/phase-3c-evidence-index.md", evidence)

    write(root, "output/call-graphs/phase-3c-home-state-flow.mmd", """flowchart TD
  B[Phase 3C baseline] --> S[set-home-activity p0]
  S --> R[ordinary preferred XML p0 mAlways true]
  R --> Q[HOME candidate query]
  Q --> C[chooseBestActivity]
  C -->|Fire effective priority 50| F[Fire Launcher]
  C -->|p0 effective priority 0| P[p0 record stored but not selected]
  F --> H[Home key explicit HOME reboot foreground]
  P -. persists across reboot .-> R
  H --> RB[restore Fire preferred]
  RB --> U[uninstall p0]
""")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    build_settings_matrix(root)
    build_experiment_matrix(root)
    reports(root)
    print("generated Phase 3C reports and matrices")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
