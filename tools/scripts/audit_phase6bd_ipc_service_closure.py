#!/usr/bin/env python3
"""Build a host-only closure report for selected PS7331 control surfaces.

The script reads preserved VDEX disassembly, saved permission evidence and a
read-only service-visibility capture.  It never contacts a device, obtains a
Binder handle, sends a transaction, changes package/settings state, starts a
process, or invokes an OTA/OOBE path.

Missing markers are reported as unresolved; they are never treated as an
authorization bypass or as proof that a path is exploitable.
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
DEFAULTS = {
    "disassembly": ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
    "permission_manifest": ROOT / "artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/manifest-aapt.xmltree.txt",
    "device_permission_dump": ROOT / "artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt",
    "service_capture": ROOT / "adb/phase6bd/PHASE6BD-SERVICE-RO-20260805-01",
}

TABLE_FIELDS = [
    "evidence_id",
    "surface",
    "static_location",
    "static_observation",
    "runtime_observation",
    "classification",
    "confidence",
    "safe_boundary",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def repo_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def service_visibility(capture: Path) -> dict[str, object]:
    private_names = [
        "amazonpackagemanager",
        "amazonactivitymanager",
        "amazonwindowmanager",
        "amazondevicepolicymanager",
        "amazonprofileservice",
        "amazonusermanagerservice",
        "amazon_input",
        "amazon_keyevent",
    ]
    statuses: dict[str, str] = {}
    for name in private_names + ["fosdebug", "otadexopt"]:
        path = capture / f"service_check_{name}.stdout.txt"
        statuses[name] = read(path).strip() if path.is_file() else "MISSING_CAPTURE"
    metadata_path = capture / "metadata.json"
    metadata = json.loads(read(metadata_path)) if metadata_path.is_file() else {}
    return {
        "statuses": statuses,
        "private_all_not_found": all("not found" in statuses[name].lower() for name in private_names),
        "fosdebug_observed": "found" in statuses["fosdebug"].lower(),
        "otadexopt_observed": "found" in statuses["otadexopt"].lower(),
        "metadata": metadata,
    }


def match_or_fail(label: str, pattern: str, text: str) -> bool:
    if not re.search(pattern, text, re.MULTILINE | re.DOTALL):
        raise SystemExit(f"required evidence marker missing: {label}: {pattern}")
    return True


def write_table(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=TABLE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_hash_manifest(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "sha256sums.txt")
    (directory / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in files),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=default)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--public-table", type=Path)
    parser.add_argument("--public-graph", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = {name: getattr(args, name) for name in DEFAULTS}
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "binder_invoked": False,
            "package_state_changed": False,
            "reboot_requested": False,
            "inputs": {name: repo_path(path) for name, path in inputs.items()},
            "output": str(args.output),
        }, indent=2))
        return 0

    missing = [str(path) for path in inputs.values() if not path.exists()]
    if missing:
        raise SystemExit("missing preserved input(s):\n" + "\n".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    disassembly = read(inputs["disassembly"])
    manifest = read(inputs["permission_manifest"])
    device_permissions = read(inputs["device_permission_dump"])
    visibility = service_visibility(inputs["service_capture"])

    # Exact local instruction relationships.  These checks intentionally use
    # the preserved disassembly rather than reconstructed Java.
    match_or_fail(
        "setInputFilter delegates to access$600",
        r"setInputFilter \(Landroid/view/IInputFilter;\).*?access\$600",
        disassembly,
    )
    match_or_fail(
        "access$600 calls validateInputFilterAccessPermission",
        r"access\$600 \(Lcom/amazon/android/internal/server/input/AmazonInputManagerService;\)V.*?validateInputFilterAccessPermission",
        disassembly,
    )
    match_or_fail(
        "validator checks system/updated-system app",
        r"isCallerSystemApp \(\)Z.*?getCallingUid.*?getPackagesForUid.*?isSystemApp.*?isUpdatedSystemApp",
        disassembly,
    )
    match_or_fail(
        "validator enforces FILTER_INPUT_EVENTS",
        r"validateInputFilterAccessPermission \(\)V.*?FILTER_INPUT_EVENTS.*?enforceCallingPermission",
        disassembly,
    )
    match_or_fail("source declares FILTER_INPUT_EVENTS", r'FILTER_INPUT_EVENTS.*?0x80000002', manifest)
    match_or_fail("device records signature|amazon", r'FILTER_INPUT_EVENTS.*?prot=signature\|amazon', device_permissions)

    # The KFT method is a high-impact static path.  Keep the check narrow: it
    # must show both the FreeTime enable and the Fire Launcher state=2 request.
    kft_lines = disassembly.splitlines()[54296:54325]
    kft_block = "\n".join(kft_lines)
    match_or_fail("KFT enables FreeTime launcher", r"com\.amazon\.tahoe.*?FreeTimeLauncherActivity", kft_block)
    match_or_fail("KFT disables Fire Launcher", r"com\.amazon\.firelauncher.*?const/4 v4, #int 2.*?setApplicationEnabledSetting", kft_block)
    match_or_fail("KFT disables Launcher3", r"com\.android\.launcher3.*?setApplicationEnabledSetting", kft_block)

    match_or_fail("debug dump checks android.permission.DUMP", r"FireOSDebugService\.BinderService.*?android\.permission\.DUMP", disassembly)
    match_or_fail("debug dump is diagnostic inventory", r"Vendor Services:.*?getVendorServices.*?VendorManagers:.*?getVendorManagers.*?VendorCallbacks:.*?getVendorCallbackTypes.*?native_dump_vendor_callbacks", disassembly)

    private_status = visibility["statuses"]
    private_runtime = (
        "fresh read-only service-check capture: all selected Amazon private service names were not discoverable to shell"
        if visibility["private_all_not_found"]
        else "fresh read-only service-check capture was incomplete or had a non-not-found private service result"
    )
    fos_runtime = "dumpsys fosdebug completed in the capture" if visibility["fosdebug_observed"] else "fosdebug was not observed by service check"
    ota_runtime = "otadexopt was observed by service check; no private transaction was sent" if visibility["otadexopt_observed"] else "otadexopt was not observed by service check"

    rows = [
        {
            "evidence_id": "6BD-INPUT-001",
            "surface": "AmazonInputManagerService.setInputFilter",
            "static_location": "fosservices/disassembly.log:20112-20122; 21687-21692; 22437-22448",
            "static_observation": "Binder entry delegates to access$600; access$600 calls validateInputFilterAccessPermission; validator accepts system/updated-system apps or enforces FILTER_INPUT_EVENTS.",
            "runtime_observation": private_runtime,
            "classification": "CLOSED_FOR_SHELL_INPUT_ROUTE",
            "confidence": "Confirmed",
            "safe_boundary": "No service call, Binder transaction, input filter installation, or package mutation.",
        },
        {
            "evidence_id": "6BD-PERM-001",
            "surface": "FILTER_INPUT_EVENTS permission",
            "static_location": "manifest-aapt.xmltree.txt:1431-1433; preferred_activities.stdout.txt:9897-9901",
            "static_observation": "Permission is declared by android.amazon.perm with protection level signature|amazon (0x80000002); device dump records the same protection.",
            "runtime_observation": private_runtime,
            "classification": "NOT_SHELL_WRITABLE",
            "confidence": "Confirmed",
            "safe_boundary": "No attempt to grant, spoof, or invoke the private permission.",
        },
        {
            "evidence_id": "6BD-KFT-001",
            "surface": "AmazonUserManagerService.enableKftLauncherComponent",
            "static_location": "fosservices/disassembly.log:54297-54325",
            "static_observation": "For a supplied UserInfo, enables com.amazon.tahoe FreeTimeLauncherActivity and requests application state=2 for com.amazon.firelauncher and com.android.launcher3.",
            "runtime_observation": private_runtime + "; current capture did not invoke the KFT helper.",
            "classification": "STATIC_CAPABILITY_CONFIRMED_DEVICE_MUTATION_REJECTED",
            "confidence": "Confirmed",
            "safe_boundary": "No direct User 0 invocation; no child-user provisioning; Fire Launcher was not disabled, hidden, suspended, uninstalled, force-stopped, or cleared.",
        },
        {
            "evidence_id": "6BD-DEBUG-001",
            "surface": "FireOSDebugService.BinderService.dump",
            "static_location": "fosservices/disassembly.log:196-387",
            "static_observation": "dump checks android.permission.DUMP, clears calling identity only after the check, and prints vendor services/managers/callbacks/instances via FireOSInit plus native_dump_vendor_callbacks.",
            "runtime_observation": fos_runtime + "; output was an inventory, not a selector or write operation.",
            "classification": "DIAGNOSTIC_ONLY",
            "confidence": "Strong evidence",
            "safe_boundary": "Read-only dumpsys only; no native callback or Binder method replay.",
        },
        {
            "evidence_id": "6BD-OTA-001",
            "surface": "otadexopt visibility",
            "static_location": "service visibility capture; OTA analysis remains in phase-6bc artifacts",
            "static_observation": "The service name may be visible to diagnostics, but this closure does not infer an OTA control contract from visibility alone.",
            "runtime_observation": ota_runtime,
            "classification": "NO_SAFE_CONTROL_SURFACE_ESTABLISHED",
            "confidence": "Strong evidence",
            "safe_boundary": "No OTA command, package staging, recovery, sideload, or update execution.",
        },
    ]

    table = args.output / "phase6bd-ipc-control-surface.csv"
    write_table(table, rows)
    if args.public_table:
        write_table(args.public_table, rows)

    graph = """flowchart TD
    A[Shell / ordinary app] -->|service check only| B{Amazon private service visible?}
    B -->|not found in enforcing capture| C[No Binder handle / no transaction]
    A --> D[AmazonInputManagerService.setInputFilter]
    D --> E[access$600]
    E --> F[validateInputFilterAccessPermission]
    F -->|system or updated-system app| G[allowed]
    F -->|otherwise| H[enforce FILTER_INPUT_EVENTS]
    H --> I[signature|amazon permission]
    J[KFT child-user lifecycle] --> K[enableKftLauncherComponent(UserInfo)]
    K --> L[enable FreeTime launcher]
    K --> M[request Fire Launcher state=2]
    M --> N[High-impact mutation; not invoked]
    O[dumpsys fosdebug] --> P[DUMP-gated diagnostic inventory]
    P --> Q[Vendor services/managers/callbacks; no selector write]
"""
    graph_path = args.output / "phase6bd-ipc-control-surface.mmd"
    graph_path.write_text(graph, encoding="utf-8")
    if args.public_graph:
        args.public_graph.parent.mkdir(parents=True, exist_ok=True)
        args.public_graph.write_text(graph, encoding="utf-8")

    input_hashes = {}
    for name, path in inputs.items():
        if path.is_file():
            input_hashes[repo_path(path)] = sha256(path)
        else:
            # Include the files in a directory capture without exposing names
            # or contents in the report; the capture has its own manifest.
            manifest_path = path / "sha256sums.txt"
            input_hashes[repo_path(manifest_path)] = sha256(manifest_path)
    (args.output / "input-sha256.json").write_text(json.dumps(input_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "phase": "6BD",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "binder_invoked": False,
        "package_state_changed": False,
        "reboot_requested": False,
        "set_input_filter_gate_closed": True,
        "kft_static_launcher_mutation_confirmed": True,
        "kft_device_invoked": False,
        "private_service_visibility": private_status,
        "input_sha256": input_hashes,
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "result.md").write_text(
        "# Phase 6BD — IPC/service closure\n\n"
        "This output is host-only and consumes preserved PS7331 disassembly, permission evidence, and a read-only service visibility capture.\n\n"
        "- **Confirmed:** `setInputFilter()` is gated by system/updated-system app identity or `signature|amazon` `FILTER_INPUT_EVENTS`.\n"
        "- **Confirmed (static):** the KFT helper requests Fire Launcher state=2 for a supplied user.\n"
        "- **Not executed:** KFT mutation, private Binder transaction, input-filter installation, OTA/OOBE replay, and any Fire Launcher state change.\n"
        "- **Strong evidence:** `fosdebug` is a DUMP-gated diagnostic inventory, not a demonstrated HOME selector.\n",
        encoding="utf-8",
    )
    write_hash_manifest(args.output)
    print(json.dumps({
        "output": str(args.output),
        "host_only": True,
        "device_contacted": False,
        "binder_invoked": False,
        "kft_device_invoked": False,
        "rows": len(rows),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
