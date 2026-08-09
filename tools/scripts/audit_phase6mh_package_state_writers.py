#!/usr/bin/env python3
"""Inventory preserved PS7331 package/component-state setter call sites.

This is a host-only provenance audit.  It reads the already-preserved
services/fosservices disassembly, records the enclosing class/method and nearby
constant context, and classifies the bounded writer surface.  It never calls
ADB, Binder, an APK, a device node, or a mutating command.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


INPUTS = (
    Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"),
    Path("decompiled/baksmali/vdexExtractor/services/disassembly.log"),
)
DEFAULT_OUTPUT = Path("artifacts/phase6mh-package-state-writers-20260810-01")

CLASS_RE = re.compile(r"^\s+(?:class|interface) #\d+: .*\('(?P<descriptor>L[^;]+;)'\)")
METHOD_RE = re.compile(r"^\s+(?:direct|virtual)_method #\d+: (?P<signature>.+)$")
CALL_RE = re.compile(r"(setComponentEnabledSetting|setApplicationEnabledSetting):")
STRING_RE = re.compile(r'const-string[^\n]*, "([^"]*)"')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(class_name: str, method: str, text: str) -> tuple[str, str]:
    if "EnableDisableComponentAction" in class_name:
        return "amazon_product_policy", "policy-file/user-list driven; trusted system service"
    if "AmazonUserManagerService" in class_name:
        return "amazon_kft_child_user", "UserInfo.id supplied; child/profile lifecycle"
    if "EspressoShotCallback" in class_name:
        return "espresso_boot_receiver", "boot-complete receiver map; metadata/permission gated"
    if "PackageManagerShellCommand" in class_name:
        return "standard_shell_command", "shell command reaches standard PMS gate"
    if "PackageManagerService" in class_name:
        return "standard_pms_internal", "system_server internal path"
    if "ActivityManagerService" in class_name:
        return "standard_ams_internal", "system_server fixed/system path"
    if "AppAdapterHandler" in class_name:
        return "amazon_app_adapter", "fixed registration component"
    if "BluetoothManagerService" in class_name:
        return "standard_bluetooth_internal", "fixed Bluetooth component"
    return "other_state_writer", "requires caller/data-flow review"


def scan(path: Path) -> list[dict[str, str | int]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    source_hash = sha256(path)
    current_class = "<unknown>"
    current_method = "<unknown>"
    rows: list[dict[str, str | int]] = []
    for index, line in enumerate(lines):
        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_match.group("descriptor")[1:-1].replace("/", ".")
            current_method = "<class-init>"
        method_match = METHOD_RE.match(line)
        if method_match:
            current_method = method_match.group("signature")
        call_match = CALL_RE.search(line)
        if not call_match or "virtual_method" in line:
            continue
        start = max(0, index - 40)
        nearby = lines[start : index + 1]
        literals = [m.group(1) for item in nearby for m in [STRING_RE.search(item)] if m]
        # Preserve order while avoiding repeated log/tag strings.
        literal_context = "; ".join(dict.fromkeys(literals))
        context = "\n".join(nearby)
        category, scope = classify(current_class, current_method, context)
        rows.append(
            {
                "source": path.as_posix(),
                "source_sha256": source_hash,
                "line": index + 1,
                "class": current_class,
                "method": current_method,
                "setter": call_match.group(1),
                "category": category,
                "scope_observation": scope,
                "nearby_literals": literal_context,
                "callsite": " ".join(line.strip().split()),
                "device_mutation": "false",
            }
        )
    return rows


def write_outputs(rows: list[dict[str, str | int]], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fields = [
        "source",
        "source_sha256",
        "line",
        "class",
        "method",
        "setter",
        "category",
        "scope_observation",
        "nearby_literals",
        "callsite",
        "device_mutation",
    ]
    with (output / "writer-calls.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "schema": "phase6mh-package-state-writers-v1",
        "input_count": len(INPUTS),
        "callsite_count": len(rows),
        "categories": {category: sum(row["category"] == category for row in rows)
                        for category in sorted({str(row["category"]) for row in rows})},
        "set_component_count": sum(row["setter"] == "setComponentEnabledSetting" for row in rows),
        "set_application_count": sum(row["setter"] == "setApplicationEnabledSetting" for row in rows),
        "host_only": True,
        "adb": False,
        "binder_transaction": False,
        "device_mutation": False,
        "interpretation": (
            "Callsite inventory only; a setter call is not evidence of a reachable shell "
            "caller or a Fire Launcher target."
        ),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    graph = """flowchart LR
  S[PS7331 services/fosservices disassembly] --> I[setter callsite inventory]
  I --> K[KFT child/profile writer]
  I --> P[Product policy action]
  I --> E[Espresso boot receiver toggler]
  I --> G[standard shell/PMS path]
  P -. signed /system/etc policy input .-> U[user list and policy components]
  K -. UserInfo.id .-> C[child/profile scope]
  E -. boot-complete metadata gate .-> B[receiver components]
  G --> X[standard PMS protected/caller gates]
  I -. no direct HOME/Fire target proven by inventory .-> H[HOME objective]
"""
    (output / "writer-calls.mmd").write_text(graph, encoding="utf-8")

    checks = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        checks.append(f"{sha256(path)}  {path.name}")
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
    print(json.dumps({"output": str(args.output), "callsite_count": len(rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
