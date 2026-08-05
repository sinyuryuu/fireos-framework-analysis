#!/usr/bin/env python3
"""Close the saved PS7331 OtaDexoptService implementation boundary.

This is an offline parser plus a bounded read-only evidence join.  It never
invokes an OTA/dexopt command.  The only device evidence it consumes is an
already-preserved status capture containing the documented ``done`` and
``progress`` commands.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_DISASSEMBLY = Path("decompiled/baksmali/vdexExtractor/services/disassembly.log")
DEFAULT_ADJACENT = Path("decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log")
DEFAULT_STATUS = Path("adb/phase6ae/PHASE6AE-STATUS-20260805-01")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def class_slice(lines: list[str], marker: str, next_marker: str | None = None) -> tuple[int, int]:
    start = next(i for i, line in enumerate(lines) if marker in line)
    if next_marker is None:
        end = len(lines)
    else:
        end = next((i for i in range(start + 1, len(lines)) if next_marker in lines[i]), len(lines))
    return start, end


METHOD_RE = re.compile(r"^\s+(?:direct|virtual)_method #\d+: ([^\s(]+)")


def method_ranges(lines: list[str], start: int, end: int) -> list[dict[str, object]]:
    headers: list[tuple[int, str]] = []
    for i in range(start, end):
        match = METHOD_RE.match(lines[i])
        if match:
            headers.append((i, match.group(1)))
    methods: list[dict[str, object]] = []
    for index, (header, name) in enumerate(headers):
        body_end = headers[index + 1][0] if index + 1 < len(headers) else end
        body = lines[header:body_end]
        code_off = next((line.split("=", 1)[1].split()[0] for line in body if "codeOff=" in line), None)
        addresses = [m.group(1) for line in body if (m := re.match(r"^\s+([0-9a-f]+):", line))]
        methods.append({
            "name": name,
            "start_line": header + 1,
            "end_line": body_end,
            "code_off": code_off,
            "first_instruction": addresses[0] if addresses else None,
            "lines": body,
        })
    return methods


def contains_any(lines: Iterable[str], patterns: Iterable[str]) -> list[str]:
    joined = "\n".join(lines)
    return [pattern for pattern in patterns if pattern in joined]


def describe_service_methods(lines: list[str]) -> list[dict[str, object]]:
    start, end = class_slice(lines, "class #2649: OtaDexoptService", "class #2650: OtaDexoptShellCommand")
    permission_patterns = [
        "checkCallingPermission",
        "checkPermission",
        "enforceCallingPermission",
        "enforcePermission",
        "getCallingUid",
        "Binder;.getCallingUid",
    ]
    all_class_lines = lines[start:end]
    class_permissions = contains_any(all_class_lines, permission_patterns)
    selected = {"main", "cleanup", "dexoptNextPackage", "getProgress", "isDone", "nextDexoptCommand", "onShellCommand", "prepare"}
    marker_map = {
        "main": ["ServiceManager;.addService", '"otadexopt"', "moveAbArtifacts"],
        "cleanup": ["mDexoptCommands", "getAvailableSpace", "performMetricsLogging"],
        "dexoptNextPackage": ["UnsupportedOperationException"],
        "getProgress": ["completeSize", "mDexoptCommands", "const/high16 v0, #int 1065353216"],
        "isDone": ["mDexoptCommands", "List;.isEmpty", "done() called before prepare()"],
        "nextDexoptCommand": ["List;.remove:(I)", "getAvailableSpace", "List;.clear", "dexoptCommandCountExecuted"],
        "onShellCommand": ["OtaDexoptShellCommand", "OtaDexoptShellCommand;.exec"],
        "prepare": ["getPackagesForDexopt", "mDexoptCommands", "generatePackageDexopts", "deleteOatArtifactsOfPackage"],
    }
    rows: list[dict[str, object]] = []
    for method in method_ranges(lines, start, end):
        name = str(method["name"])
        if name not in selected:
            continue
        body = method["lines"]
        markers = contains_any(body, marker_map[name])
        if name == "main":
            classification = "registration_and_startup"
            effect = "publishes otadexopt and calls moveAbArtifacts"
        elif name in {"cleanup", "nextDexoptCommand", "prepare"}:
            classification = "state_mutating_rejected"
            effect = {
                "cleanup": "clears mDexoptCommands and records metrics",
                "nextDexoptCommand": "removes one command; may clear remaining commands on low space",
                "prepare": "builds dexopt command list and may delete OAT artifacts on low space",
            }[name]
        elif name == "dexoptNextPackage":
            classification = "throws_before_effect"
            effect = "throws UnsupportedOperationException"
        elif name in {"getProgress", "isDone"}:
            classification = "state_read_or_precondition_check"
            effect = {
                "getProgress": "reads completeSize and command-list size",
                "isDone": "reads command-list state or throws before prepare",
            }[name]
        else:
            classification = "shell_dispatch"
            effect = "constructs OtaDexoptShellCommand and calls exec"
        rows.append({
            "class": "com.android.server.pm.OtaDexoptService",
            "method": name,
            "static_location": f"disassembly.log:{method['start_line']}-{method['end_line']}",
            "code_off": method["code_off"],
            "first_instruction": method["first_instruction"],
            "classification": classification,
            "markers": ";".join(markers),
            "direct_effect": effect,
            "permission_markers_in_class": ";".join(class_permissions) if class_permissions else "NONE_OBSERVED",
            "device_invocation": "done/progress only" if name in {"isDone", "getProgress"} else "NOT_INVOKED",
            "evidence": "PS7331 services VDEX + PHASE6AE-STATUS-20260805-01",
        })
    return rows


def describe_shell_command(lines: list[str]) -> list[dict[str, object]]:
    start, end = class_slice(lines, "class #2650: OtaDexoptShellCommand", "class #2651: PackageDexOptimizer")
    methods = method_ranges(lines, start, end)
    on_command = next(m for m in methods if m["name"] == "onCommand")
    body = on_command["lines"]
    command_map = {
        "cleanup": ("cleanup", "runOtaCleanup"),
        "done": ("isDone", "runOtaDone"),
        "next": ("nextDexoptCommand", "runOtaNext"),
        "prepare": ("prepare", "runOtaPrepare"),
        "progress": ("getProgress", "runOtaProgress"),
        "step": ("dexoptNextPackage", "runOtaStep"),
    }
    rows: list[dict[str, object]] = []
    for command, (iface_method, runner_method) in command_map.items():
        command_lines = [(i, line) for i, line in enumerate(body) if f'"{command}"' in line]
        runner = next((m for m in methods if m["name"] == runner_method), None)
        runner_body = runner["lines"] if runner else []
        call_lines = [(i, line) for i, line in enumerate(runner_body) if f"IOtaDexopt;.{iface_method}" in line]
        command_line = command_lines[0][0] + int(on_command["start_line"])
        call_line = call_lines[0][0] + int(runner["start_line"]) if call_lines and runner else None
        rows.append({
            "class": "com.android.server.pm.OtaDexoptShellCommand",
            "command": command,
            "interface_method": iface_method,
            "command_location": f"disassembly.log:{command_line}",
            "call_location": f"disassembly.log:{call_line}" if call_line else "NOT_FOUND",
            "runner_method": runner_method,
            "invoked_on_device": "YES" if command in {"done", "progress"} else "NO",
            "risk": "read/precondition" if command in {"done", "progress"} else "state mutation or dexopt execution",
        })
    return rows


def system_server_hits(lines: list[str]) -> list[dict[str, object]]:
    hits = []
    for i, line in enumerate(lines):
        if "config.disable_otadexopt" in line or "OtaDexoptService;.main" in line:
            hits.append({"file": "services/disassembly.log", "line": i + 1, "text": line.strip()})
    return hits


def adjacent_hits(path: Path) -> list[dict[str, object]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hits = []
    for i, line in enumerate(lines):
        if "config.disable_otadexopt" in line or "OtaDexoptService;.main" in line or "class #2649: OtaDexoptService" in line:
            hits.append({"file": str(path), "line": i + 1, "text": line.strip()})
    return hits


def status_summary(status_dir: Path) -> dict[str, object]:
    metadata_path = status_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    done = (status_dir / "otadexopt_done.stderr.txt").read_text(encoding="utf-8", errors="replace")
    progress = (status_dir / "otadexopt_progress.stdout.txt").read_text(encoding="utf-8", errors="replace").strip()
    home = (status_dir / "home_resolve.stdout.txt").read_text(encoding="utf-8", errors="replace").strip()
    return {
        "capture": str(status_dir),
        "serial": metadata.get("serial"),
        "captured_at_utc": metadata.get("captured_at_utc"),
        "read_only": metadata.get("read_only"),
        "unknown_binder_transaction": metadata.get("unknown_binder_transaction"),
        "excluded_mutating_commands": metadata.get("excluded_otadexopt_commands"),
        "done_returncode": next((x.get("returncode") for x in metadata.get("results", []) if x.get("name") == "otadexopt_done"), None),
        "done_stack_contains_service": "OtaDexoptService.java:176" in done,
        "done_stack_contains_shell_command": "OtaDexoptShellCommand.java:76" in done,
        "done_stack_contains_binder_stub": "IOtaDexopt$Stub.onTransact" in done,
        "progress_return_value": progress,
        "home_result": home,
        "home_is_fire_launcher": "com.amazon.firelauncher/.Launcher" in home,
    }


def render_graph() -> str:
    return """flowchart TD
    SS[SystemServer start path\nservices/disassembly.log:107990-108045] -->|mOnlyCore=false && !config.disable_otadexopt| MAIN[OtaDexoptService.main\n:482249-482263]
    MAIN --> PUB[ServiceManager.addService(otadexopt)\n:482249-482263]
    PUB --> SHELL[Binder shellCommand / OtaDexoptShellCommand\n:482598-482611]
    SHELL --> DONE[done -> isDone\n:482514-482532]
    SHELL --> PROGRESS[progress -> getProgress\n:482490-482513]
    SHELL --> PREPARE[prepare -> prepare\n:482613-482?]
    SHELL --> NEXT[next -> nextDexoptCommand\n:482533-482597]
    SHELL --> CLEANUP[cleanup -> cleanup\n:482460-482478]
    SHELL --> STEP[step -> dexoptNextPackage\n:482479-482489]
    DONE -->|captured done before prepare| ERR[IllegalStateException\nPHASE6AE status capture]
    PROGRESS -->|captured| ONE[1.00\nPHASE6AE status capture]
    PREPARE -->|rejected| MUT[builds command list; may delete OAT artifacts on low space]
    NEXT -->|rejected| MUT2[removes command; may clear list]
    CLEANUP -->|rejected| MUT3[clears state and logs metrics]
    STEP --> UNSUP[UnsupportedOperationException]
    """


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--disassembly", type=Path, default=DEFAULT_DISASSEMBLY)
    parser.add_argument("--adjacent-disassembly", type=Path, default=DEFAULT_ADJACENT)
    parser.add_argument("--status-dir", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--table-output", type=Path, required=True)
    parser.add_argument("--graph-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.disassembly, args.adjacent_disassembly, args.status_dir / "metadata.json",
              args.status_dir / "otadexopt_done.stderr.txt", args.status_dir / "otadexopt_progress.stdout.txt",
              args.status_dir / "home_resolve.stdout.txt"]
    missing = [str(p) for p in inputs if not p.exists()]
    if missing:
        parser.error("missing input(s): " + ", ".join(missing))
    targets = [args.output, args.table_output, args.graph_output, args.report_output]
    existing = [str(p) for p in targets if p.exists()]
    if existing and not args.dry_run:
        parser.error("refusing to overwrite: " + ", ".join(existing))
    if args.dry_run:
        print(json.dumps({"dry_run": True, "inputs": [str(p) for p in inputs], "outputs": [str(p) for p in targets]}, indent=2))
        return 0

    service_text = args.disassembly.read_text(encoding="utf-8", errors="replace")
    service_lines = service_text.splitlines()
    methods = describe_service_methods(service_lines)
    shell_rows = describe_shell_command(service_lines)
    status = status_summary(args.status_dir)
    evidence = {
        "phase": "6AF",
        "title": "PS7331 OtaDexoptService implementation closure",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_this_parser": False,
        "mutating_otadexopt_command_invoked": False,
        "unknown_binder_transaction": False,
        "input_sha256": {str(p): sha256(p) for p in inputs if p.is_file()},
        "services_disassembly_sha256": sha256(args.disassembly),
        "adjacent_ps7331_disassembly_sha256": sha256(args.adjacent_disassembly),
        "service_class": "com.android.server.pm.OtaDexoptService",
        "service_registration": "ServiceManager.addService(\"otadexopt\", service)",
        "methods": methods,
        "shell_commands": shell_rows,
        "system_server_hits": system_server_hits(service_lines),
        "adjacent_ps7331_hits": adjacent_hits(args.adjacent_disassembly),
        "runtime_status": status,
        "conclusions": [
            {"finding": "Concrete OtaDexoptService implementation and registration are present in the saved PS7331 services VDEX.", "classification": "Confirmed"},
            {"finding": "The documented shell path reaches the installed service; done() before prepare() produced the expected OtaDexoptService precondition stack.", "classification": "Confirmed"},
            {"finding": "prepare, next, cleanup and any dexopt execution remain uninvoked because they mutate state or may delete OAT artifacts.", "classification": "Confirmed / risk-rejected"},
            {"finding": "No HOME selector, Fire Launcher hardcode, privilege transition or root path is present in this service boundary.", "classification": "Strong evidence"},
            {"finding": "No method-local permission check marker was observed in the saved OtaDexoptService class; this is not evidence of a bypass because shell reachability is also governed by Binder/SELinux/service policy.", "classification": "Static bounded result"},
        ],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "implementation.json", evidence)
    write_text(args.output / "implementation.mmd", render_graph())
    rows = methods + [{**row, "class": row["class"]} for row in shell_rows]
    fieldnames = ["class", "method", "command", "interface_method", "static_location", "command_location", "call_location", "code_off", "first_instruction", "classification", "markers", "direct_effect", "permission_markers_in_class", "device_invocation", "invoked_on_device", "risk", "evidence"]
    with (args.output / "implementation.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    write_text(args.table_output, (args.output / "implementation.csv").read_text(encoding="utf-8"))
    write_text(args.graph_output, render_graph())
    report = """# Phase 6AF：PS7331 `OtaDexoptService` implementation closure

## Scope

This correction closes the concrete implementation gap left in Phase 6AE. It
uses the saved PS7331 services VDEX and the already-preserved, read-only
`PHASE6AE-STATUS-20260805-01` capture. This parser did not contact the device.
No Binder transaction, OTA command, OOBE broadcast, package/settings mutation,
reboot, or partition operation was performed.

## Result

**Confirmed:** the installed PS7331 services VDEX contains
`com.android.server.pm.OtaDexoptService`, its `main()` registration under the
`otadexopt` service name, and its `onShellCommand()` bridge to
`OtaDexoptShellCommand`.

**Confirmed:** the preserved device capture reached the real service through
documented shell commands. `cmd otadexopt done` returned the service's
`IllegalStateException: done() called before prepare()` stack, including
`OtaDexoptService.java:176`, `OtaDexoptShellCommand.java:76`, and
`IOtaDexopt$Stub.onTransact`. `cmd otadexopt progress` returned `1.00`.

**Risk-rejected:** `prepare`, `next`, `cleanup`, and dexopt execution were not
run. Static code shows that `prepare` builds dexopt commands and can delete OAT
artifacts when space is low; `next` removes commands and can clear the list;
`cleanup` clears service state; `step` reaches an
`UnsupportedOperationException` in this build but was not invoked.

**Strong evidence:** this service boundary contains no HOME selection,
Fire-Launcher package comparison, privilege transition, or root path. The
absence of a method-local permission marker is only a bounded static result;
it is not an authorization bypass claim.

## Static locations

The authoritative installed VDEX is
`decompiled/baksmali/vdexExtractor/services/disassembly.log` (SHA-256 is in
`implementation.json`). The key locations are:

| Path | Location | Meaning |
|---|---:|---|
| `OtaDexoptService` | `482129` | class and source file declaration |
| `main(Context, PackageManagerService)` | `482249-482263` | constructs service, publishes `otadexopt`, moves A/B artifacts |
| `cleanup()` | `482460-482478` | clears command state and logs metrics; not invoked |
| `dexoptNextPackage()` | `482479-482489` | throws `UnsupportedOperationException`; not invoked |
| `getProgress()` | `482490-482513` | reads progress state; captured result `1.00` |
| `isDone()` | `482514-482532` | precondition/read path; captured `done()` exception |
| `nextDexoptCommand()` | `482533-482597` | removes/possibly clears command list; not invoked |
| `onShellCommand()` | `482598-482611` | delegates to `OtaDexoptShellCommand`; reached by capture |
| `prepare()` | `482613-482734` | builds dexopt command list and may delete OAT artifacts; not invoked |
| `OtaDexoptShellCommand` | `482735+` | maps `prepare`, `done`, `step`, `next`, `cleanup`, `progress` |
| `SystemServer` | `107990-108045` | starts service unless `mOnlyCore` or `config.disable_otadexopt` blocks it |

The adjacent PS7331 VDEX contains the same service-start shape and is retained
as provenance evidence; exact hashes and hit lines are in the artifact JSON.

## Security and research disposition

The service is a real shell-visible OTA dexopt control surface, but it is not a
safe launcher or privilege-escalation control surface. Future work is limited
to host-side comparison, documented read/precondition queries, or naturally
occurring OTA observation. Do not invoke `prepare`, `next`, `cleanup`, `step`,
private Binder transactions, or updater/recovery paths on the retail device.

## Reproduction

```sh
python3 tools/scripts/audit_phase6af_otadexopt_implementation.py --dry-run \\
  --output /tmp/phase6af-artifact \\
  --table-output /tmp/phase6af-methods.csv \\
  --graph-output /tmp/phase6af-flow.mmd \\
  --report-output /tmp/phase6af-report.md

python3 tools/scripts/audit_phase6af_otadexopt_implementation.py \\
  --output artifacts/phase6af/otadexopt-implementation-closure-20260805-01 \\
  --table-output output/tables/phase6af-otadexopt-implementation.csv \\
  --graph-output output/call-graphs/phase6af-otadexopt-implementation.mmd \\
  --report-output findings/phase-6af-otadexopt-implementation-closure.md
```
"""
    write_text(args.report_output, report)
    # The report is also retained inside the immutable artifact directory.
    write_text(args.output / "result.md", report)
    # Input manifest is deliberately generated after all primary outputs.
    manifest_lines = []
    for path in sorted(args.output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    write_text(args.output / "sha256sums.txt", "\n".join(manifest_lines) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileExistsError, StopIteration) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
