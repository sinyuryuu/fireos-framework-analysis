#!/usr/bin/env python3
"""Validate the bounded Phase 6KY Amazon IPC/HOME route inventory.

This is a host-only evidence checker.  It reads already-collected VDEX,
source, callback, and report artifacts; it never contacts a device, obtains a
Binder handle, sends a transaction, executes native code, or changes state.
The route rows are deliberately conservative: a static authorization anomaly
is not promoted to a reachable exploit or a HOME writer.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOSSERVICES = ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
SERVICES = ROOT / "decompiled/baksmali/vdexExtractor/services/disassembly.log"
CALLBACK_CSV = ROOT / "artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv"
AMZ_ACTIVITY_XML = ROOT / "artifacts/amazon-services/amazonactivitymanager_fosinit.xml"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def first_line(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    return text.count("\n", 0, match.start()) + 1


def file_record(path: Path, patterns: list[str]) -> dict[str, object]:
    if not path.exists():
        return {"file": str(path.relative_to(ROOT)), "exists": False, "sha256": None, "anchors": {}}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "file": str(path.relative_to(ROOT)),
        "exists": True,
        "sha256": sha256(path),
        "anchors": {pattern: first_line(text, pattern) for pattern in patterns},
    }


def route_rows() -> list[dict[str, str]]:
    return [
        {
            "route_id": "PMS-HOME-001",
            "surface": "PackageManagerService.setHomeActivity",
            "sink": "formal HOME preferred writer",
            "caller_gate": "standard Android shell/package-manager path",
            "home_effect": "writes ordinary preferred record; Fire still resolves in saved tests",
            "shell_reachable": "yes (already tested)",
            "device_action": "no new mutation",
            "disposition": "KNOWN_STANDARD_PATH",
            "confidence": "Confirmed",
            "evidence": "findings/phase-6kv-pms-home-caller-closure.md: setHomeActivity/replacePreferredActivity closure",
        },
        {
            "route_id": "KFT-USER-001",
            "surface": "AmazonUserManagerService.enableKftLauncherComponent",
            "sink": "per-user Tahoe/Fire/Launcher3 component state writer",
            "caller_gate": "KFT child-user lifecycle and private service visibility",
            "home_effect": "can change launcher state for supplied child UserInfo.id; no unconditional User 0 route",
            "shell_reachable": "no (saved service check not found)",
            "device_action": "STATIC_ONLY_REJECTED_FOR_DEVICE_TEST",
            "disposition": "PROFILE_SCOPED_WRITER",
            "confidence": "Confirmed",
            "evidence": "fosservices/disassembly.log:54310-54324; artifacts/phase6av/ipc-method-closure-20260805-05/ipc-method-closure.csv",
        },
        {
            "route_id": "CALLBACK-001",
            "surface": "AppCompatActivityStackSupervisorCallback.resolveIntent",
            "sink": "vendor resolver callback",
            "caller_gate": "registered SYSTEMSERVER fosinit callback",
            "home_effect": "delegates to IPackageManager.resolveIntent and filters observed uninstalled flag; no Fire literal",
            "shell_reachable": "not an app-facing shell service",
            "device_action": "HOST_ONLY",
            "disposition": "NO_DIRECT_HOME_OVERRIDE",
            "confidence": "Strong evidence",
            "evidence": "artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv; result.md",
        },
        {
            "route_id": "CALLBACK-002",
            "surface": "EveActivityStackSupervisorCallback",
            "sink": "vendor resolver callback",
            "caller_gate": "registered SYSTEMSERVER fosinit callback",
            "home_effect": "no concrete resolveIntent override; inherited base returns null",
            "shell_reachable": "not an app-facing shell service",
            "device_action": "HOST_ONLY",
            "disposition": "NO_DIRECT_HOME_OVERRIDE",
            "confidence": "Confirmed",
            "evidence": "artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv; services/disassembly.log:222435-222489,796458-796504",
        },
        {
            "route_id": "OOBE-OTA-001",
            "surface": "BootAfterSystemOTAReceiver / OOBEActivationHelper",
            "sink": "OOBE component and setup-state writer",
            "caller_gate": "OTA/OOBE lifecycle and protected OobeHomeActivity",
            "home_effect": "setup-only HOME state; not a normal Fire Launcher preferred writer",
            "shell_reachable": "not established",
            "device_action": "NOT_TRIGGERED",
            "disposition": "OOBE_ONLY",
            "confidence": "Confirmed",
            "evidence": "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java; findings/phase-6ku-low-privilege-boundary.md",
        },
        {
            "route_id": "AMS-001",
            "surface": "AmazonActivityManagerService.preWarmApplicationForUser",
            "sink": "process prewarm via startProcessLocked",
            "caller_gate": "APP_PREWARM check result is not consumed in bounded method block",
            "home_effect": "no HOME resolver, preferred writer, or Fire component write observed",
            "shell_reachable": "no (saved enforcing service lookup denied/not found)",
            "device_action": "HOST_ONLY; no transaction",
            "disposition": "AUTHORIZATION_ANOMALY_NON_HOME",
            "confidence": "Strong evidence",
            "evidence": "fosservices/disassembly.log:40453-40534; artifacts/phase6av/ipc-method-closure-20260805-05/result.md",
        },
        {
            "route_id": "AMS-002",
            "surface": "AmazonActivityManagerService.registerActivitySwitchObserver / onActivityResume",
            "sink": "foreground component cache and observer notification",
            "caller_gate": "ACTIVITY_SWITCH_WATCHER permission for registration",
            "home_effect": "observes foreground state; no resolver or package-state write",
            "shell_reachable": "no saved shell service handle",
            "device_action": "HOST_ONLY",
            "disposition": "OBSERVER_ONLY",
            "confidence": "Confirmed",
            "evidence": "fosservices/disassembly.log:40374-40416,40535-40564; artifacts/phase6ax/activity-manager-home-surface-20260805-01/activity-manager-binder-methods.csv",
        },
        {
            "route_id": "ASP-001",
            "surface": "AmazonAspService.hasCallerGotPermission / command",
            "sink": "audio signal processor command handler",
            "caller_gate": "tablet branch returns true before ASP_PERMISSION check",
            "home_effect": "no PackageManager, ActivityTaskManager, or HOME sink in bounded body",
            "shell_reachable": "service visibility is not a proof of safe command authorization",
            "device_action": "NO TRANSACTION; NO NATIVE COMMAND",
            "disposition": "SENSITIVE_NON_HOME",
            "confidence": "Confirmed",
            "evidence": "fosservices/disassembly.log:82014-82077",
        },
        {
            "route_id": "DRIVER-001",
            "surface": "MT8183 CMDQ/GED/sysenv/IDME/lifecycle source scope",
            "sink": "hardware, telemetry, or boot-environment surfaces",
            "caller_gate": "driver/file-context/configuration dependent",
            "home_effect": "no source edge to PMS/AMS/HOME in audited PS7331 source scope",
            "shell_reachable": "mixed; existing read-only GED evidence only",
            "device_action": "NO ioctl/write/malformed payload",
            "disposition": "SENSITIVE_SURFACE_NO_HOME_EDGE",
            "confidence": "Strong evidence",
            "evidence": "findings/phase-6bq-ged-readonly-ioctl.md; findings/phase-6br-amazon-kernel-user-surfaces.md; findings/phase-6fs-p5-driver-source-audit.md",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/tables/phase6ky-validation")
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    records = {
        "inputs": [
            file_record(FOSSERVICES, [r"class #440: AmazonUserManagerService", r"enableKftLauncherComponent", r"hasCallerGotPermission", r"preWarmApplicationForUser"]),
            file_record(SERVICES, [r"setHomeActivity", r"VendorActivityStackSupervisorCallback", r"ActivityStackSupervisor\.resolveIntent"]),
            file_record(CALLBACK_CSV, [r"AppCompatActivityStackSupervisorCallback", r"EveActivityStackSupervisorCallback"]),
            file_record(AMZ_ACTIVITY_XML, [r"AmazonActivityManagerService"]),
        ],
        "device_actions": "none",
        "binder_transactions": "none",
        "routes": route_rows(),
    }
    (out / "result.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / "route-classification.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(route_rows()[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(route_rows())
    print(json.dumps({"output": str(out), "route_count": len(route_rows()), "device_actions": "none"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
