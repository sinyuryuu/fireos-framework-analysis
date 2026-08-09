#!/usr/bin/env python3
"""Build a host-only Phase 6O control-boundary evidence bundle.

This script reads preserved source/disassembly, manifest, JSON, and device
result files.  It never contacts ADB, opens a device node, sends Binder
transactions, changes package/settings state, or executes OTA/recovery code.
The output directory must be new so that original evidence is not overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path


DEFAULT_OUTPUT = Path("artifacts/phase6o/control-boundary-20260810-01")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def contains(text: str, pattern: str, label: str) -> None:
    if not re.search(pattern, text, re.MULTILINE | re.DOTALL):
        raise ValueError(f"required marker missing: {label}")


def build_rows(root: Path, inputs: dict[str, Path]) -> list[dict[str, str]]:
    methods = inputs["kft_methods"].read_text(encoding="utf-8", errors="replace")
    snippets = inputs["kft_snippets"].read_text(encoding="utf-8", errors="replace")
    child = json.loads(inputs["child_result"].read_text(encoding="utf-8"))
    updater = inputs["updater"].read_text(encoding="utf-8", errors="replace")
    ota_audit = json.loads(inputs["ota_audit"].read_text(encoding="utf-8"))
    ota_manifest = inputs["ota_manifest"].read_text(encoding="utf-8", errors="replace")
    broadcasts = inputs["broadcasts"].read_text(encoding="utf-8", errors="replace")

    contains(methods, r"AmazonUserManagerService\.BinderService,5625.*enableKftLauncherComponent", "KFT helper row")
    contains(methods, r"KFT_LAUNCHER_STATE_WRITE", "KFT state-write classification")
    contains(snippets, r"com\.amazon\.firelauncher.*const/4 v4, #int 2.*setApplicationEnabledSetting", "Fire Launcher state 2")
    contains(snippets, r"com\.android\.launcher3.*setApplicationEnabledSetting", "Launcher3 state write")
    if child.get("after_owner_home", "").find("com.amazon.firelauncher/.Launcher") < 0:
        raise ValueError("User 0 Fire Launcher result missing")
    if child.get("child_home_last", {}).get("home", "").find("com.amazon.tahoe/.launcher.FreeTimeLauncherActivity") < 0:
        raise ValueError("User 10 Tahoe result missing")
    if not child.get("rollback_succeeded"):
        raise ValueError("child-user rollback marker is not true")
    contains(updater, r"block_image_update\(\"/dev/block/platform/bootdevice/by-name/system\"", "fixed system target")
    contains(updater, r"block_image_update\(\"/dev/block/platform/bootdevice/by-name/vendor\"", "fixed vendor target")
    contains(updater, r"package_extract_file\(\"boot\.img\", \"/dev/block/platform/bootdevice/by-name/boot\"", "fixed boot target")
    if re.search(r"run_program|symlink\s*\(|delete_recursive\s*\(", updater):
        raise ValueError("unexpected dynamic updater operation marker")
    assessment = ota_audit.get("assessment", {})
    if not assessment.get("fixed_partition_targets_only"):
        raise ValueError("OTA audit is not fixed-target")
    if assessment.get("post_install_executor_observed"):
        raise ValueError("OTA audit reports a post-install executor")
    contains(ota_manifest, r"com\.amazon\.dcp\.ota\.permission\.CONTROLLER.*protectionLevel.*0x3", "OTA controller protection")
    contains(ota_manifest, r"OtaService.*com\.amazon\.dcp\.ota\.permission\.CONTROLLER", "OTA service gate")
    contains(broadcasts, r"BOOT_AFTER_SYSTEM_OTA", "protected OTA broadcast")

    return [
        {
            "evidence_id": "6O-KFT-001",
            "source": rel(root, inputs["kft_methods"]),
            "location": "lines 54297-54325",
            "observation": "Private enableKftLauncherComponent(UserInfo) enables Tahoe's FreeTimeLauncherActivity and requests state 2 for Fire Launcher and Launcher3 for the supplied user.",
            "classification": "KFT_PER_USER_STATE_WRITER",
            "confidence": "Confirmed (static)",
            "safe_boundary": "No invocation; Fire Launcher was not disabled, hidden, suspended, uninstalled, force-stopped, or cleared.",
        },
        {
            "evidence_id": "6O-KFT-002",
            "source": rel(root, inputs["kft_methods"]),
            "location": "lines 55053-55105",
            "observation": "AmazonUserManagerService.onBootPhase iterates internal user lifecycle and can reach setup/KFT helpers; the preserved method classification is internal and no transaction was sent.",
            "classification": "INTERNAL_LIFECYCLE_ONLY",
            "confidence": "Strong evidence",
            "safe_boundary": "No setup-state mutation or boot lifecycle replay.",
        },
        {
            "evidence_id": "6O-USER-001",
            "source": rel(root, inputs["child_result"]),
            "location": "result.json fields child_home_last / after_owner_home",
            "observation": "The observed child-user HOME was Tahoe at priority 975; after returning to User 0, HOME was Fire Launcher at priority 50; rollback succeeded.",
            "classification": "PER_USER_HOME_SEPARATION",
            "confidence": "Confirmed (runtime)",
            "safe_boundary": "Existing GUI profile-switch capture only; no new user/profile mutation in this phase.",
        },
        {
            "evidence_id": "6O-OTA-001",
            "source": rel(root, inputs["updater"]),
            "location": "lines 1-25",
            "observation": "The PS7331 updater script uses fixed system/vendor block-image targets and fixed boot/firmware partition extraction targets, plus a cache blocklist write; no dynamic post-install executor marker is present.",
            "classification": "FIXED_TARGET_RECOVERY_LOGIC",
            "confidence": "Confirmed (static)",
            "safe_boundary": "No recovery, sideload, partition write, or malformed-package test.",
        },
        {
            "evidence_id": "6O-OTA-002",
            "source": rel(root, inputs["ota_audit"]),
            "location": "assessment / blocklist fields",
            "observation": "The preserved audit reports fixed partition targets only, no archive traversal or symlink entries, no duplicate file-map paths, and no post-install executor; OTA SHA-256 is 9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5.",
            "classification": "OTA_INPUT_BOUNDARY_CLOSED_FOR_SAFE_SCOPE",
            "confidence": "Strong evidence",
            "safe_boundary": "Block-image contents remain outside this conclusion; flashing is prohibited.",
        },
        {
            "evidence_id": "6O-OTA-003",
            "source": rel(root, inputs["ota_manifest"]),
            "location": "lines 12-37, 114-164",
            "observation": "The OTA controller permission is protection level 0x3 (signature|privileged); OtaService and update-control receivers require it and are single-user/exported according to the manifest.",
            "classification": "PRIVILEGED_OTA_CONTROL_PLANE",
            "confidence": "Confirmed (static)",
            "safe_boundary": "No protected broadcast, service transaction, or package update was invoked.",
        },
        {
            "evidence_id": "6O-OTA-004",
            "source": rel(root, inputs["broadcasts"]),
            "location": "protected-broadcast inventory rows containing BOOT_AFTER_SYSTEM_OTA and OTA status actions",
            "observation": "OTA lifecycle broadcasts are sourced from android.amazon.perm under android.uid.system; this does not establish an ordinary-app caller.",
            "classification": "SYSTEM_PROTECTED_LIFECYCLE_SIGNAL",
            "confidence": "Confirmed (static)",
            "safe_boundary": "No synthetic broadcast or OOBE replay.",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    inputs = {
        "kft_methods": root / "artifacts/phase6ay/launcher-state-services-20260805-02/launcher-state-service-methods.csv",
        "kft_snippets": root / "artifacts/phase6ay/launcher-state-services-20260805-02/selected-method-snippets.txt",
        "child_result": root / "adb/phase6gr/PHASE6GR-GUI-SYSTEMUI-SWITCH-20260807-07/result.json",
        "updater": root / "artifacts/phase6bp/ota-manifest-20260805-01/META-INF/com/google/android/updater-script",
        "ota_audit": root / "artifacts/phase6bp/ota-path-audit-20260805-02/ota-path-audit.json",
        "ota_manifest": root / "artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/011_com.amazon.device.software.ota__0_DeviceSoftwareOTA.xmltree.txt",
        "broadcasts": root / "artifacts/phase6bk/protected-broadcast-union-20260810-02/protected-broadcast-inventory.csv",
    }
    try:
        for path in inputs.values():
            require(path)
        rows = build_rows(root, inputs)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"phase6o input validation failed: {exc}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "binder_invoked": False,
            "row_count": len(rows),
            "output": str(output),
            "inputs": {name: rel(root, path) for name, path in inputs.items()},
        }, indent=2))
        return 0
    if output.exists():
        print(f"refusing to overwrite existing output: {output}", file=sys.stderr)
        return 2
    output.mkdir(parents=True)
    input_manifest = [
        {"name": name, "path": rel(root, path), "sha256": sha256(path), "size": path.stat().st_size}
        for name, path in inputs.items()
    ]
    (output / "input-sha256.json").write_text(json.dumps(input_manifest, indent=2) + "\n", encoding="utf-8")
    fields = list(rows[0])
    with (output / "evidence.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = "# Phase 6O — KFT per-user and OTA fixed-target boundary\n\n"
    report += "Date: 2026-08-10\n\n"
    report += "## Scope\n\n"
    report += "This is a host-only closure of two remaining research surfaces: the KFT launcher state writer and the PS7331 OTA/OOBE update boundary. It consumes preserved artifacts and a prior, rolled-back child-user observation. It does not contact the device, send Binder transactions, execute an OTA, or mutate Fire Launcher.\n\n"
    report += "## Findings\n\n"
    report += "- **已證實：** `enableKftLauncherComponent(UserInfo)` is a private per-user state writer. Its static call sites request Tahoe's FreeTime launcher and state 2 for `com.amazon.firelauncher` and `com.android.launcher3` for the supplied user.\n"
    report += "- **已證實：** the preserved runtime profile-switch result is user-scoped: User 10 resolved Tahoe at priority 975, while returning to User 0 resolved Fire Launcher at priority 50; rollback succeeded. This does not provide a User-0 replacement.\n"
    report += "- **已證實：** the PS7331 updater script is fixed-target recovery logic for system/vendor block updates and fixed boot/firmware partitions. The preserved audit found no archive traversal/symlink path or post-install executor.\n"
    report += "- **已證實：** OTA control receivers/service are behind `signature|privileged` controller permission and single-user policy. OTA lifecycle broadcasts are system-protected.\n"
    report += "- **已排除（目前證據範圍）：** no ordinary shell/App caller to the KFT writer, no ordinary caller to the OTA writer, and no evidence that these paths change User-0 HOME.\n"
    report += "- **待驗證：** a complete CFG review of the native `update-binary` parser and a byte-complete audit of the outer source archive remain host-only gaps; neither justifies device execution.\n\n"
    report += "## Evidence\n\n"
    report += "| ID | Source | Classification | Confidence |\n|---|---|---|---|\n"
    for row in rows:
        report += f"| {row['evidence_id']} | `{row['source']}:{row['location']}` | {row['classification']} | {row['confidence']} |\n"
    report += "\n## Safety boundary\n\n"
    report += "No root attempt, unknown Binder transaction, malformed ioctl, synthetic protected broadcast, recovery/sideload, partition write, Fire Launcher disable/hide/suspend/uninstall/clear, or factory reset was performed. The child-user evidence used here records a prior successful rollback; no new profile mutation was performed.\n\n"
    report += "## Decision\n\n"
    report += "The highest-value remaining safe work is host-only completion of the native updater CFG and broader artifact inventory. If it does not identify a legitimate unprivileged writer, the research should return to measuring a reversible launcher foreground fallback rather than retrying protected package-state routes.\n"
    (output / "result.md").write_text(report, encoding="utf-8")
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in files), encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "row_count": len(rows), "host_only": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
