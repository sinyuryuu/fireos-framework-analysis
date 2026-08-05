#!/usr/bin/env python3
"""Audit the PS7331 AmazonActivityManagerService Binder surface.

This is a host-only parser for the preserved Fire OS VDEX disassembly.  It
does not contact ADB, obtain a Binder handle, send a transaction, start or
kill a process, inject input, change settings, or mutate package state.

The purpose is to separate activity observation and process-control methods
from an actual HOME selector.  A public Binder method is not treated as
reachable merely because its Java access flag is PUBLIC: the saved SELinux
service-manager boundary and method-local permission evidence remain
separate columns in the output.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
DEFAULT_OUTPUT = Path("artifacts/phase6ax/activity-manager-home-surface-20260805-01")
CLASS_MARKER = "class #374: AmazonActivityManagerService.BinderService"
END_MARKER = "class #375: AmazonActivityManagerService.TestHelper"

FIELDS = [
    "method_number",
    "kind",
    "signature",
    "access",
    "line_start",
    "line_end",
    "permission_literals",
    "permission_calls",
    "activity_calls",
    "home_terms",
    "state_writes",
    "classification",
    "reachability_note",
]

METHOD_RE = re.compile(r"^\s+(direct_method|virtual_method) #(\d+): (.+)$")
ACCESS_RE = re.compile(r"^\s+access=([^ ]+)(?: \((.*)\))?$")
PERMISSION_LITERAL_RE = re.compile(r'const-string [^,]+, "([^"]*permission[^"]*)"', re.I)
CALL_RE = re.compile(r"invoke-[^|]*\|[^:]*: (.+?) \(.*?\)|invoke-[^|]*\s+.*?\|[^:]*: (.+?) \(.*?\)")

ACTIVITY_MARKERS = (
    "Activity",
    "activity",
    "Home",
    "home",
    "ComponentName",
    "Process",
    "process",
    "Pip",
    "MultiWindow",
)
HOME_MARKERS = (
    "getFocusedStackInfo",
    "isOnHomeStack",
    "mHomeProcess",
    "Home",
    "home",
    "startHome",
    "resolveActivity",
    "resolveIntent",
    "Preferred",
    "preferred",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_methods(text: str) -> tuple[list[dict[str, str]], int, int]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if CLASS_MARKER in line), None)
    end = next((i for i, line in enumerate(lines) if END_MARKER in line), None)
    if start is None or end is None or end <= start:
        raise RuntimeError("AmazonActivityManagerService.BinderService class bounds not found")

    headers: list[tuple[int, re.Match[str]]] = []
    for index in range(start, end):
        match = METHOD_RE.match(lines[index])
        if match:
            headers.append((index, match))

    rows: list[dict[str, str]] = []
    for position, (header_index, match) in enumerate(headers):
        method_end = headers[position + 1][0] if position + 1 < len(headers) else end
        body = lines[header_index:method_end]
        header = match.group(3)
        access = ""
        if header_index + 1 < method_end:
            access_match = ACCESS_RE.match(lines[header_index + 1])
            if access_match:
                access = access_match.group(1)
                if access_match.group(2):
                    access += " (" + access_match.group(2) + ")"

        permission_literals = sorted(set(
            literal for line in body for literal in PERMISSION_LITERAL_RE.findall(line)
        ))
        permission_calls = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if "checkCallingPermission" in line
            or "enforceCallingPermission" in line
            or "checkCallingOrSelfPermission" in line
            or "enforceCallingOrSelfPermission" in line
        ))
        activity_calls = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if any(marker in line for marker in ACTIVITY_MARKERS)
            and "invoke-" in line
        ))
        home_terms = sorted(set(
            marker for marker in HOME_MARKERS if marker in "\n".join(body)
        ))
        state_writes = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if " iput" in line or " sput" in line
        ))

        if "isOnHomeStack" in header:
            classification = "HOME_STATE_QUERY"
        elif "onActivityResume" in header:
            classification = "FOREGROUND_STATE_WRITE_AND_OBSERVER_NOTIFY"
        elif "notifyActivitySwitch" in header:
            classification = "OBSERVER_NOTIFICATION_INTERNAL"
        elif "registerActivitySwitchObserver" in header or "unregisterActivitySwitchObserver" in header:
            classification = "OBSERVER_REGISTRATION_PERMISSION_GATED"
        elif "preWarmApplicationForUser" in header:
            classification = "PROCESS_PREWARM_PERMISSION_CHECK_NOT_CONSUMED"
        elif "checkKillAppGoingIntoBg" in header:
            classification = "PROCESS_KILL_CANDIDATE"
        elif any(name in header for name in ("disablePip", "enablePip", "dismissPip", "dismissMultiWindow")):
            classification = "PIP_OR_MULTIWINDOW_CONTROL"
        elif "packageLifetimeHint" in header:
            classification = "PROCESS_LIFETIME_HINT_PERMISSION_GATED"
        elif "requestCpuBoost" in header:
            classification = "PERFORMANCE_CONTROL_PERMISSION_GATED"
        elif "dump" in header:
            classification = "DIAGNOSTIC_DUMP_PERMISSION_GATED"
        elif "getCpuLoad" in header or "getRecentCrashes" in header:
            classification = "DIAGNOSTIC_QUERY"
        else:
            classification = "OTHER_BINDER_METHOD"

        if classification == "FOREGROUND_STATE_WRITE_AND_OBSERVER_NOTIFY":
            note = "PUBLIC Binder method in saved VDEX; saved service-manager AVC still denies shell handle. No HOME resolver call in body."
        elif classification == "PROCESS_PREWARM_PERMISSION_CHECK_NOT_CONSUMED":
            note = "Static authorization anomaly candidate only; no service handle, transaction, process start, or bypass was tested."
        elif classification == "PROCESS_KILL_CANDIDATE":
            note = "High-impact process-control body; no local permission literal in bounded method. Service reachability remains separately denied in saved shell capture."
        else:
            note = "Classified from bounded method body; absence of a call is limited to this disassembly scope."

        rows.append({
            "method_number": match.group(2),
            "kind": match.group(1),
            "signature": header,
            "access": access,
            "line_start": str(header_index + 1),
            "line_end": str(method_end),
            "permission_literals": "; ".join(permission_literals),
            "permission_calls": "; ".join(permission_calls),
            "activity_calls": "; ".join(activity_calls),
            "home_terms": "; ".join(home_terms),
            "state_writes": "; ".join(state_writes),
            "classification": classification,
            "reachability_note": note,
        })
    return rows, start + 1, end


def graph() -> str:
    return """flowchart TD
  S[AmazonActivityManagerService publishes amazonactivitymanager] --> V[Saved SELinux service-manager boundary]
  V -->|shell uid 2000 find denied| X[No ordinary shell Binder handle]
  V --> T[Trusted/internal caller]
  T --> Q[isOnHomeStack: query focused stack]
  T --> F[onActivityResume: stores mComponentInForeground and notifies observers]
  F --> O[ActivitySwitchHandler -> authorized observers]
  T --> P[packageLifetimeHint: SMARTOOM_HINTING]
  T --> W[preWarmApplicationForUser: APP_PREWARM check then process prewarm]
  T --> K[checkKillAppGoingIntoBg: process-control candidate]
  T --> M[PIP / multi-window controls]
  Q -. no bounded resolver or Fire component write .-> H[HOME resolver remains in PackageManager/ActivityManager path]
  F -. foreground telemetry/observer path, not HOME selection .-> H
  W -. no bounded HOME selector .-> H
"""


def plain_graph() -> str:
    return """AmazonActivityManagerService.onStart
  -> publish amazonactivitymanager
  -> saved enforcing AVC: shell uid=2000 cannot find service
  -> trusted/internal callers only in observed deployment

BinderService methods
  -> isOnHomeStack(): reads focused stack activity type; no resolver write
  -> onActivityResume(ComponentName): writes mComponentInForeground, queues observer notification
  -> register/unregisterActivitySwitchObserver(): ACTIVITY_SWITCH_WATCHER permission
  -> packageLifetimeHint(): SMARTOOM_HINTING permission, process-LRU adjustment
  -> preWarmApplicationForUser(): APP_PREWARM check result not consumed locally; process prewarm only
  -> checkKillAppGoingIntoBg(): process-control candidate; no local permission literal in bounded body
  -> PIP/multi-window methods: CONTROL_PIP_WINDOW permission

No method in this BinderService bounded class body calls a HOME resolver, writes a
preferred activity, selects a Fire Launcher component, or calls startHomeActivity.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if not source.is_file():
        raise SystemExit(f"missing source: {source}")
    if output.exists() and not args.dry_run:
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    rows, class_start, class_end = parse_methods(source.read_text(encoding="utf-8", errors="replace"))
    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "source_sha256": sha256(source),
        "class": CLASS_MARKER,
        "class_line_start": class_start,
        "class_line_end": class_end,
        "method_count": len(rows),
        "device_contacted": False,
        "binder_invoked": False,
        "process_started_or_killed": False,
        "input_injected": False,
        "settings_or_package_state_changed": False,
        "partition_written": False,
        "classification_counts": {
            name: sum(row["classification"] == name for row in rows)
            for name in sorted({row["classification"] for row in rows})
        },
        "bounded_negative": "No HOME resolver/preferred-activity/startHomeActivity call observed in the BinderService class body.",
        "safety": "host-only static parser; no ADB, Binder transaction, process control, input injection, package/settings mutation, reboot, OTA, or partition operation",
    }
    if args.dry_run:
        print(json.dumps({"summary": summary, "methods": rows}, ensure_ascii=False, indent=2))
        return 0

    output.mkdir(parents=True)
    with (output / "activity-manager-binder-methods.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "activity-manager-home-surface.mmd").write_text(graph(), encoding="utf-8")
    (output / "activity-manager-home-surface.md").write_text(plain_graph(), encoding="utf-8")
    selected = []
    text = source.read_text(encoding="utf-8", errors="replace").splitlines()
    wanted = {"checkKillAppGoingIntoBg", "disablePipWindows", "dismissMultiWindow", "dismissPipWindow", "enablePipWindows", "isOnHomeStack", "onActivityResume", "packageLifetimeHint", "preWarmApplicationForUser", "registerActivitySwitchObserver", "requestCpuBoost", "unregisterActivitySwitchObserver"}
    for row in rows:
        if not any(name in row["signature"] for name in wanted):
            continue
        start = int(row["line_start"]) - 1
        end = min(int(row["line_end"]), start + 40)
        selected.append(f"### {row['signature']} (lines {row['line_start']}-{row['line_end']})")
        selected.extend(f"{index + 1}: {text[index]}" for index in range(start, end))
        selected.append("")
    (output / "method-snippets.txt").write_text("\n".join(selected), encoding="utf-8")
    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(output), "methods": len(rows), "source_sha256": summary["source_sha256"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
