#!/usr/bin/env python3
"""Index preserved PS7331 DEX/VDEX disassembly calls into package/HOME sinks.

This is a host-only, read-only parser.  It reads already extracted disassembly
text; it never invokes ADB, a Binder service, an APK, or a native executable.
The output is an evidence index of exact invoke instructions, not a claim that
the caller is reachable from shell or that the call changes User 0.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_INPUTS = {
    "fosservices": Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"),
    "services": Path("decompiled/baksmali/vdexExtractor/services/disassembly.log"),
}

TARGETS = (
    ("AmazonPackageManager.setComponentEnabledSetting", "AmazonPackageManager;.setComponentEnabledSetting"),
    ("AmazonPackageManager.setApplicationEnabledSetting", "AmazonPackageManager;.setApplicationEnabledSetting"),
    ("PackageManager.setComponentEnabledSetting", "PackageManager;.setComponentEnabledSetting"),
    ("PackageManager.setApplicationEnabledSetting", "PackageManager;.setApplicationEnabledSetting"),
    ("IPackageManager.setComponentEnabledSetting", "IPackageManager;.setComponentEnabledSetting"),
    ("IPackageManager.setApplicationEnabledSetting", "IPackageManager;.setApplicationEnabledSetting"),
    ("PackageManagerService.setComponentEnabledSetting", "PackageManagerService;.setComponentEnabledSetting"),
    ("PackageManagerService.setApplicationEnabledSetting", "PackageManagerService;.setApplicationEnabledSetting"),
    ("PackageManagerService.setHomeActivity", "PackageManagerService;.setHomeActivity"),
    ("PackageManagerService.replacePreferredActivity", "PackageManagerService;.replacePreferredActivity"),
    ("PackageManagerService.addPersistentPreferredActivity", "PackageManagerService;.addPersistentPreferredActivity"),
    ("PackageManagerService.restorePreferredActivities", "PackageManagerService;.restorePreferredActivities"),
    ("PackageManagerService.clearPackagePreferredActivities", "PackageManagerService;.clearPackagePreferredActivities"),
)

CLASS_RE = re.compile(r"^\s*class\s+#\d+:\s+([^\s(]+)")
METHOD_RE = re.compile(
    r"^\s*(?:direct_method|virtual_method)\s+#\d+:\s+([^\s]+)\s+(\([^)]*\)[^\s]+)"
)
INSTRUCTION_RE = re.compile(r"^\s*([0-9a-f]+):\s+.*?\|[^:]+:\s+(.*)$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def descriptor_to_class(descriptor: str) -> str:
    value = descriptor.strip("'")
    if value.startswith("L") and value.endswith(";"):
        value = value[1:-1]
    return value.replace("/", ".")


def classify(class_name: str, method_name: str, target: str) -> Tuple[str, str]:
    """Return a conservative static classification and scope note."""
    joined = f"{class_name}#{method_name}"
    if (
        ("AmazonUserManagerService$BinderService" in class_name
         or "AmazonUserManagerService.BinderService" in class_name)
        and "enableKftLauncherComponent" in method_name
    ):
        return "amazon_launcher_state_writer_child_scoped", "literal Tahoe/Fire/Launcher3 targets; scope is supplied UserInfo.id"
    if "EnableDisableComponentAction" in class_name:
        return "amazon_product_policy_fixed_component_writer", "in-process ProductPolicy action; supplied fixed policy component/package"
    if "AppAdapterHandler" in class_name:
        return "amazon_oobe_fixed_component_writer", "OOBE registration component path"
    if "GeminiHandler" in class_name:
        return "amazon_fixed_gemini_package_writer", "fixed Gemini package path"
    if "EspressoShotCallback" in class_name:
        return "amazon_boot_receiver_component_writer", "BOOT receiver lifecycle path"
    if "PackageManagerShellCommand" in class_name:
        return "shell_command_to_framework_writer", "shell command front end; framework caller checks still apply"
    if "DevicePolicyManagerService" in class_name:
        return "device_policy_trusted_writer", "device/profile-owner path; not ordinary shell evidence"
    if "PackageManagerService" in class_name:
        return "framework_internal_sink_or_helper", "framework implementation or internal helper"
    if target.startswith("IPackageManager."):
        return "binder_client_to_package_manager", "client-side Binder call; no server authorization conclusion"
    return "other_system_component_writer", joined


def parse_file(root: Path, relative: Path, source_kind: str) -> List[Dict[str, str]]:
    path = root / relative
    current_class = ""
    current_method = ""
    current_descriptor = ""
    rows: List[Dict[str, str]] = []
    for line_number, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        class_match = CLASS_RE.match(raw)
        if class_match:
            current_class = descriptor_to_class(class_match.group(1))
            current_method = ""
            current_descriptor = ""
            continue
        method_match = METHOD_RE.match(raw)
        if method_match:
            current_method = method_match.group(1)
            current_descriptor = method_match.group(2)
            continue
        instruction_match = INSTRUCTION_RE.match(raw)
        if not instruction_match or "invoke-" not in raw:
            continue
        body = instruction_match.group(2)
        for target, needle in TARGETS:
            if needle not in body:
                continue
            classification, scope = classify(current_class, current_method, target)
            rows.append(
                {
                    "source_kind": source_kind,
                    "source_file": str(relative),
                    "source_line": str(line_number),
                    "instruction_offset": "0x" + instruction_match.group(1),
                    "caller_class": current_class,
                    "caller_method": current_method,
                    "caller_descriptor": current_descriptor,
                    "sink": target,
                    "classification": classification,
                    "scope_or_limit": scope,
                    "evidence_status": "static_invoke_site_only",
                }
            )
            break
    return rows


def write_csv(path: Path, rows: Iterable[Dict[str, str]]) -> None:
    rows = list(rows)
    fields = [
        "source_kind",
        "source_file",
        "source_line",
        "instruction_offset",
        "caller_class",
        "caller_method",
        "caller_descriptor",
        "sink",
        "classification",
        "scope_or_limit",
        "evidence_status",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or root / "artifacts/phase6kv/pms-home-caller-closure-20260810-01").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, str]] = []
    inputs: List[Dict[str, str]] = []
    for source_kind, relative in DEFAULT_INPUTS.items():
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        inputs.append({"source_kind": source_kind, "path": str(relative), "sha256": sha256(path)})
        rows.extend(parse_file(root, relative, source_kind))
    rows.sort(key=lambda row: (row["source_file"], int(row["source_line"]), row["sink"]))
    csv_path = output_dir / "pms-home-callers.csv"
    write_csv(csv_path, rows)
    canonical_csv = root / "output/tables/phase6kv-pms-home-callers.csv"
    canonical_csv.parent.mkdir(parents=True, exist_ok=True)
    write_csv(canonical_csv, rows)
    manifest = {
        "tool": "audit_phase6kv_pms_home_callers.py",
        "mode": "HOST_ONLY_READ_ONLY",
        "inputs": inputs,
        "output": {
            "artifact_path": str(csv_path.relative_to(root)),
            "artifact_sha256": sha256(csv_path),
            "canonical_path": str(canonical_csv.relative_to(root)),
            "canonical_sha256": sha256(canonical_csv),
        },
        "row_count": len(rows),
        "target_count": len(TARGETS),
        "interpretation_limit": "Rows are exact disassembly invoke sites; they do not prove runtime reachability, shell access, or User-0 mutation.",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
