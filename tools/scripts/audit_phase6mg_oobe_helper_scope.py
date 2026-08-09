#!/usr/bin/env python3
"""Audit OOBE helper user-scope signals from preserved JADX source.

Host-only and intentionally narrow.  It reads four already-preserved source
files, records settings/component writes and whether an explicit user argument
is visible, and writes review artifacts.  It never calls adb, sends a
broadcast, executes an APK, or mutates a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUTPUT = Path("artifacts/phase6mg-oobe-helper-scope-20260810-01")
INPUTS = (
    Path("artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/SettingsDBUtils.java"),
    Path("artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/PackageHelper.java"),
    Path("artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java"),
    Path("artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java"),
)

SIGNALS = (
    ("secure_settings_write", re.compile(r"Settings\.Secure\.put(?:Int|String)\s*\(")),
    ("global_settings_write", re.compile(r"Settings\.Global\.put(?:Int|String)\s*\(")),
    ("component_state_write", re.compile(r"setComponentEnabledSetting\s*\(")),
    ("oobe_activation_call", re.compile(r"activateOOBE(?:IF|FG|MyAccountFlow)?\s*\(")),
    ("oobe_helper_fg_method", re.compile(r"setSetting(?:Secure|Global)Put(?:Int|String)FG\s*\(")),
)

METHOD_RE = re.compile(
    r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?"
    r"[\w<>\[\], ?]+\s+(\w+)\s*\([^;{}]*\)\s*\{"
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def method_at(lines: list[str], index: int) -> str:
    for pos in range(index, max(-1, index - 80), -1):
        match = METHOD_RE.match(lines[pos].strip())
        if match:
            return match.group(1)
    return "<unknown>"


def classify(signal: str, line: str, method: str) -> tuple[str, str]:
    if signal == "component_state_write":
        return "no explicit user argument visible", "PackageManager component state"
    if signal == "oobe_activation_call":
        return "delegated to helper; user scope not explicit at call site", "OOBE setup state"
    if signal == "oobe_helper_fg_method":
        return "method name says FG; underlying API still requires context scope", "OOBE setup state"
    if "ForUser" in line or "userId" in line or "userHandle" in line:
        return "explicit user-shaped API/argument", "settings provider"
    return "no explicit user argument visible", "Settings.Secure/Global"


def scan(path: Path) -> list[dict[str, str | int]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rows: list[dict[str, str | int]] = []
    for number, line in enumerate(lines, start=1):
        for signal, pattern in SIGNALS:
            if not pattern.search(line):
                continue
            method = method_at(lines, number - 1)
            scope, domain = classify(signal, line, method)
            rows.append(
                {
                    "source": path.as_posix(),
                    "source_sha256": digest(path),
                    "line": number,
                    "method": method,
                    "signal": signal,
                    "user_scope": scope,
                    "state_domain": domain,
                    "source_text": " ".join(line.strip().split()),
                }
            )
    return rows


def write_outputs(rows: list[dict[str, str | int]], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    table = output / "helper-scope.csv"
    fields = ["source", "source_sha256", "line", "method", "signal", "user_scope", "state_domain", "source_text"]
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    with (output / "input-hashes.tsv").open("w", encoding="utf-8") as handle:
        handle.write("source\tsha256\n")
        for path in INPUTS:
            handle.write(f"{path.as_posix()}\t{digest(path)}\n")

    explicit = sum(str(row["user_scope"]) == "explicit user-shaped API/argument" for row in rows)
    summary = {
        "schema": "phase6mg-oobe-helper-scope-v1",
        "input_count": len(INPUTS),
        "signal_count": len(rows),
        "explicit_user_scope_signal_count": explicit,
        "no_explicit_user_scope_signal_count": len(rows) - explicit,
        "package_helper_component_write_values": {"enable": 1, "disable": 2, "flags": 1},
        "settings_api_observation": "Settings.Secure/Global.putInt/putString are invoked with ContentResolver and key/value; no put*ForUser call is present in the reviewed helper source.",
        "device_mutation": False,
        "adb": False,
        "broadcast_sent": False,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    graph = """flowchart LR
  B[BootAfterSystemOTAReceiver] --> E[enableIncrementalFlow]
  E --> P[PackageHelper.enableComponent]
  P --> C[setComponentEnabledSetting state=1 flags=1]
  E --> A[OOBEActivationHelper.activateOOBEIF]
  A --> S[SettingsDBUtils.setSettingSecurePutIntFG]
  S --> U[Settings.Secure.putInt ContentResolver key value]
  U -. context-bound scope; exact user mapping pending .-> D[Context-bound user scope]
"""
    (output / "helper-scope.mmd").write_text(graph, encoding="utf-8")

    checks = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        checks.append(f"{digest(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    missing = [path for path in INPUTS if not path.is_file()]
    if missing:
        raise SystemExit("missing input: " + ", ".join(str(path) for path in missing))
    if args.dry_run:
        print(f"input_count={len(INPUTS)}")
        print("inputs_exist=true")
        return 0
    rows = [row for path in INPUTS for row in scan(path)]
    write_outputs(rows, args.output)
    print(json.dumps({"output": str(args.output), "signal_count": len(rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
