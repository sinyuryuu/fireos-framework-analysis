#!/usr/bin/env python3
"""Audit Amazon launcher-state and OTA service methods in PS7331 VDEX.

Host-only parser.  It does not contact ADB, obtain a Binder handle, send a
transaction, invoke a DPM/profile-owner operation, change package state, send
an OTA broadcast, or write a device partition.
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
DEFAULT_OUTPUT = ROOT / "artifacts/phase6ay/launcher-state-services-20260805-01"
METHOD_RE = re.compile(r"^\s+(direct_method|virtual_method) #(\d+): (.+)$")
CLASS_RE = re.compile(r"^  class #\d+:")
PERMISSION_LITERAL_RE = re.compile(r'const-string [^,]+, "([^\"]*permission[^\"]*)"', re.I)

TARGET_CLASSES = {
    "AmazonUserManagerService":
        "class #441: AmazonUserManagerService (",
    "AmazonUserManagerService.BinderService":
        "class #440: AmazonUserManagerService.BinderService",
    "AmazonPackageManagerService":
        "class #652: AmazonPackageManagerService (",
    "AmazonPackageManagerService.BinderService":
        "class #651: AmazonPackageManagerService.BinderService",
}

FIELDS = [
    "service_class", "method_number", "kind", "signature", "access",
    "line_start", "line_end", "permissions", "package_literals",
    "state_calls", "dpm_calls", "ota_calls", "identity_calls",
    "classification", "risk_boundary", "device_tested",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def class_region(lines: list[str], marker: str) -> tuple[int, int]:
    start = next((i for i, line in enumerate(lines) if marker in line), None)
    if start is None:
        raise RuntimeError(f"class marker not found: {marker}")
    end = next((i for i in range(start + 1, len(lines)) if CLASS_RE.match(lines[i])), len(lines))
    return start, end


def parse_class(lines: list[str], service_class: str, marker: str) -> tuple[list[dict[str, str]], int, int]:
    start, end = class_region(lines, marker)
    headers: list[tuple[int, re.Match[str]]] = []
    for index in range(start, end):
        match = METHOD_RE.match(lines[index])
        if match:
            headers.append((index, match))

    rows: list[dict[str, str]] = []
    for pos, (header_index, match) in enumerate(headers):
        method_end = headers[pos + 1][0] if pos + 1 < len(headers) else end
        body = lines[header_index:method_end]
        signature = match.group(3)
        access = ""
        if header_index + 1 < method_end:
            access = lines[header_index + 1].strip()

        joined = "\n".join(body)
        permissions = sorted(set(PERMISSION_LITERAL_RE.findall(joined)))
        package_literals = sorted(set(
            literal for line in body
            for literal in re.findall(r'const-string [^,]+, "([^\"]+)"', line)
            if any(term in literal.lower() for term in (
                "launcher", "amazon.firelauncher", "amazon.tahoe", "amazon.intent.action",
                "com.android.launcher3", "free time",
            ))
        ))
        state_calls = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if any(term in line for term in (
                "setComponentEnabledSetting", "setApplicationEnabledSetting",
                "setUserSetupComplete", "Settings$", "putString", "putInt",
            ))
        ))
        dpm_calls = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if "DevicePolicy" in line or "setActiveAdmin" in line or "setProfileOwner" in line
        ))
        ota_calls = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if "BOOT_AFTER_SYSTEM_OTA" in line or "sendBroadcast" in line or "isUpgrade" in line
        ))
        identity_calls = sorted(set(
            line.strip().split("|", 1)[-1].strip()
            for line in body
            if "clearCallingIdentity" in line or "restoreCallingIdentity" in line
        ))

        if "enableKftLauncherComponent" in signature:
            classification = "KFT_LAUNCHER_STATE_WRITE"
            risk = "High-impact package/component mutation; private helper; do not invoke on retail device."
        elif "enableKftLauncher" in signature:
            classification = "KFT_PROFILE_OWNER_FLOW"
            risk = "High-impact KFT/DPM/profile-owner flow; service is private and invocation is rejected."
        elif "tryEnableKftLauncherComponent" in signature:
            classification = "KFT_LAUNCHER_STATE_GATE"
            risk = "KFT/TV/existence gate before state write; host-only evidence."
        elif "onBootPhase" in signature and service_class == "AmazonPackageManagerService":
            classification = "POST_OTA_BROADCAST_GATE"
            risk = "Runs only in system-server lifecycle; protected OTA broadcast; do not replay."
        elif "onBootPhase" in signature and service_class == "AmazonUserManagerService":
            classification = "KFT_BOOT_LIFECYCLE"
            risk = "Internal user/upgrade lifecycle; may invoke KFT path; do not trigger or alter setup state."
        elif "setAmazon" in signature or "removeAmazon" in signature:
            classification = "PACKAGE_METADATA_PERMISSION_GATED"
            risk = "Amazon package metadata mutation; explicit Amazon permission branch; not HOME."
        elif "onStart" in signature:
            classification = "SERVICE_REGISTRATION"
            risk = "Publishes private Binder service; no transaction sent."
        elif "setUserSetupComplete" in signature:
            classification = "SETUP_STATE_MUTATION"
            risk = "Setup/user state mutation in internal user lifecycle; not a third-party HOME API."
        else:
            classification = "OTHER_METHOD"
            risk = "Bounded method classification only; no live invocation."

        rows.append({
            "service_class": service_class,
            "method_number": match.group(2),
            "kind": match.group(1),
            "signature": signature,
            "access": access,
            "line_start": str(header_index + 1),
            "line_end": str(method_end),
            "permissions": "; ".join(permissions),
            "package_literals": "; ".join(package_literals),
            "state_calls": "; ".join(state_calls),
            "dpm_calls": "; ".join(dpm_calls),
            "ota_calls": "; ".join(ota_calls),
            "identity_calls": "; ".join(identity_calls),
            "classification": classification,
            "risk_boundary": risk,
            "device_tested": "NO",
        })
    return rows, start + 1, end


def graph() -> str:
    return """flowchart TD
  U[AmazonUserManagerService.onBootPhase / child-user lifecycle] --> K[enableKftLauncher]
  K --> G[isMMDevice / isTv / KFT component existence]
  G --> W[tryEnableKftLauncherComponent]
  W --> T[enable com.amazon.tahoe FreeTimeLauncherActivity]
  W --> F[disable com.amazon.firelauncher application]
  W --> L[disable com.android.launcher3 application]
  K --> D[clearCallingIdentity]
  D --> P[setActiveAdmin / setProfileOwner for KFT user]
  S[AmazonPackageManagerService.onBootPhase] --> I[phase 550 + PackageManagerService.isUpgrade]
  I --> B[BOOT_AFTER_SYSTEM_OTA]
  B --> R[sendBroadcast with RECEIVE_BOOT_AFTER_SYSTEM_OTA permission]
  X[ordinary shell UID 2000] -. service_manager find denied in saved enforcing capture .-> U
  X -.-> S
  F -. special user lifecycle, not ordinary HOME .-> H[No safe ADB HOME replacement established]
  R -. OOBE/OTA lifecycle, not a shell selector .-> H
"""


def plain_graph() -> str:
    return """AmazonUserManagerService
  -> private KFT/child-user lifecycle
  -> enableKftLauncher(UserInfo)
  -> isMMDevice / isTv / existsKftLauncher
  -> tryEnableKftLauncherComponent
  -> enable com.amazon.tahoe FreeTimeLauncherActivity
  -> setApplicationEnabledSetting(com.amazon.firelauncher, DISABLED, user)
  -> setApplicationEnabledSetting(com.android.launcher3, DISABLED, user)
  -> DPM setActiveAdmin / setProfileOwner after clearCallingIdentity

AmazonPackageManagerService
  -> onBootPhase(550)
  -> PackageManagerService.isUpgrade()
  -> sendBroadcast(amazon.intent.action.BOOT_AFTER_SYSTEM_OTA,
                   com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA)

Saved enforcing live evidence: ordinary shell uid=2000 cannot find the private
Amazon user/package-manager services. No Binder transaction or lifecycle trigger
was sent. These are high-impact internal paths, not ADB launcher selectors.
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

    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    rows: list[dict[str, str]] = []
    bounds = {}
    for service_class, marker in TARGET_CLASSES.items():
        parsed, start, end = parse_class(lines, service_class, marker)
        rows.extend(parsed)
        bounds[service_class] = {"line_start": start, "line_end": end, "method_count": len(parsed)}

    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "source_sha256": sha256(source),
        "class_bounds": bounds,
        "method_count": len(rows),
        "device_contacted": False,
        "binder_invoked": False,
        "dpm_or_profile_owner_invoked": False,
        "package_or_settings_state_changed": False,
        "ota_broadcast_sent": False,
        "partition_written": False,
        "safety": "host-only static parser; no ADB, Binder, DPM, package state, setup state, OTA, reboot, or partition operation",
        "classification_counts": {
            name: sum(row["classification"] == name for row in rows)
            for name in sorted({row["classification"] for row in rows})
        },
    }
    if args.dry_run:
        print(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2))
        return 0

    output.mkdir(parents=True)
    with (output / "launcher-state-service-methods.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "launcher-state-services.mmd").write_text(graph(), encoding="utf-8")
    (output / "launcher-state-services.md").write_text(plain_graph(), encoding="utf-8")

    wanted = ("enableKftLauncher", "tryEnableKftLauncherComponent", "enableKftLauncherComponent",
              "setUserSetupComplete", "setAmazonFlagsForUser", "setAmazonMetadataForUser",
              "removeAmazonFlagsForUser", "removeAmazonMetadataForUser", "onBootPhase", "onStart")
    snippets: list[str] = []
    for row in rows:
        if not any(name in row["signature"] for name in wanted):
            continue
        start = int(row["line_start"]) - 1
        end = min(int(row["line_end"]), start + 70)
        snippets.append(f"### {row['service_class']}.{row['signature']} (lines {row['line_start']}-{row['line_end']})")
        snippets.extend(f"{index + 1}: {lines[index]}" for index in range(start, end))
        snippets.append("")
    (output / "selected-method-snippets.txt").write_text("\n".join(snippets), encoding="utf-8")

    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(output)}\n" for path in files), encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "methods": len(rows), "source_sha256": summary["source_sha256"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
