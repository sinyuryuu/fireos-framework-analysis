#!/usr/bin/env python3
"""Host-only provenance audit for AmazonUserManagerService KFT tx3.

This script reads preserved PS7331 disassembly and emits a bounded,
reproducible authorization/sink inventory.  It never contacts a device,
obtains a Binder handle, constructs a Parcel, or invokes a transaction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FOS = ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
DEFAULT_FRAMEWORK = ROOT / "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ranges_for(lines: List[str], patterns: Iterable[str]) -> List[Tuple[int, int, str]]:
    """Return source line ranges for matching method/class headers.

    Disassembly uses a new method/class header before each body.  The end of a
    bounded slice is therefore the line before the next header at the same
    listing level.  This is intentionally conservative: it is an index, not a
    decompiler or control-flow proof.
    """

    compiled = [re.compile(pattern) for pattern in patterns]
    headers = re.compile(r"^\s+(?:class |(?:direct|virtual)_method )")
    matches: List[Tuple[int, str]] = []
    for index, line in enumerate(lines):
        if any(pattern.search(line) for pattern in compiled):
            matches.append((index, line.rstrip()))
    results: List[Tuple[int, int, str]] = []
    for index, header in matches:
        end = len(lines) - 1
        for probe in range(index + 1, len(lines)):
            if headers.match(lines[probe]) and not lines[probe].lstrip().startswith("[new]"):
                end = probe - 1
                break
        results.append((index + 1, end + 1, header))
    return results


def class_region(lines: List[str], class_pattern: str) -> Tuple[List[str], int, int]:
    """Return one disassembly class region and its 1-based source bounds."""

    class_re = re.compile(class_pattern)
    start = next((index for index, line in enumerate(lines) if class_re.search(line)), None)
    if start is None:
        return [], 0, 0
    end = len(lines)
    for probe in range(start + 1, len(lines)):
        if re.match(r"^  class #", lines[probe]):
            end = probe
            break
    return lines[start:end], start + 1, end


def joined(lines: List[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def count_markers(text: str) -> Dict[str, int]:
    marker_patterns = {
        "calling_identity_reads": r"Binder;\.getCalling(?:Uid|Pid)",
        "calling_permission_checks": r"checkCalling(?:OrSelf)?Permission|enforceCalling(?:OrSelf)?Permission",
        "manage_users_literal": r"android\.permission\.MANAGE_USERS",
        "cross_user_literal": r"INTERACT_ACROSS_USERS",
        "clear_calling_identity": r"Binder;\.clearCallingIdentity",
        "restore_calling_identity": r"Binder;\.restoreCallingIdentity",
        "component_state_setters": r"setComponentEnabledSetting",
        "application_state_setters": r"setApplicationEnabledSetting",
        "user_info_id_reads": r"UserInfo;\.id:I",
        "user_info_parcel_reads": r"UserInfo\$?;.*createFromParcel|UserInfo;.*createFromParcel",
    }
    return {name: len(re.findall(pattern, text)) for name, pattern in marker_patterns.items()}


def method_rows(path: Path, lines: List[str], specs: Dict[str, List[str]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for name, patterns in specs.items():
        matches = ranges_for(lines, patterns)
        if not matches:
            rows.append({
                "source": str(path),
                "method": name,
                "start_line": "NOT_FOUND",
                "end_line": "NOT_FOUND",
                "header": "",
                **count_markers(""),
            })
            continue
        for ordinal, (start, end, header) in enumerate(matches, 1):
            text = joined(lines, start, end)
            rows.append({
                "source": str(path),
                "method": f"{name}#{ordinal}" if len(matches) > 1 else name,
                "start_line": start,
                "end_line": end,
                "header": header,
                **count_markers(text),
            })
    return rows


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    fields = [
        "source", "method", "start_line", "end_line", "header",
        "calling_identity_reads", "calling_permission_checks",
        "manage_users_literal", "cross_user_literal", "clear_calling_identity",
        "restore_calling_identity", "component_state_setters",
        "application_state_setters", "user_info_id_reads", "user_info_parcel_reads",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fosservices", type=Path, default=DEFAULT_FOS)
    parser.add_argument("--framework", type=Path, default=DEFAULT_FRAMEWORK)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fos_path = args.fosservices.resolve()
    framework_path = args.framework.resolve()
    output = args.output.resolve()
    if not fos_path.is_file() or not framework_path.is_file():
        parser.error("both disassembly inputs must exist")
    output.mkdir(parents=True, exist_ok=False)

    # Use LF as the physical listing delimiter.  ``splitlines()`` also treats
    # stray CR characters inside quoted disassembly strings as line breaks and
    # would shift all reported source line numbers.
    fos_lines = fos_path.read_bytes().decode("utf-8", errors="replace").split("\n")
    framework_lines = framework_path.read_bytes().decode("utf-8", errors="replace").split("\n")

    fos_specs = {
        "BinderService.<init>": [r"direct_method .*<init> \(Lcom/amazon/android/server/pm/AmazonUserManagerService;\)"],
        "enableKftLauncherComponent(UserInfo)": [r"direct_method .*enableKftLauncherComponent \(Landroid/content/pm/UserInfo;\)"],
        "tryEnableKftLauncherComponent(UserInfo)": [r"direct_method .*tryEnableKftLauncherComponent \(Landroid/content/pm/UserInfo;\)"],
        "enableKftLauncher(UserInfo)": [r"virtual_method .*enableKftLauncher \(Landroid/content/pm/UserInfo;\)"],
        "AmazonUserManagerService.checkManageUsersPermission": [r"direct_method .*checkManageUsersPermission \(Ljava/lang/String;\)"],
        "AmazonUserManagerService.onBootPhase": [r"virtual_method .*onBootPhase \(I\)V"],
        "AmazonUserManagerService.onStart": [r"virtual_method .*onStart \(\)V"],
        "AmazonUserManagerService.getSystemServiceName": [r"direct_method .*getSystemServiceName \(\)Ljava/lang/String;"],
    }
    framework_specs = {
        "IAmazonUserManager.Proxy.enableKftLauncher": [r"virtual_method .*enableKftLauncher \(Landroid/content/pm/UserInfo;\)Z"],
        "IAmazonUserManager.Stub.onTransact": [r"virtual_method .*onTransact \(ILandroid/os/Parcel;Landroid/os/Parcel;I\)Z"],
        "AmazonUserManagerImpl.createChildUser": [r"virtual_method .*createChildUser \(Ljava/lang/String;\)Lamazon/os/AmazonUserInfo;"],
    }
    # Restrict each search to the owning class.  A raw VDEX listing contains
    # hundreds of unrelated onBootPhase/onStart/onTransact methods, so a
    # global regex would create a misleading caller inventory.
    fos_regions = [
        ("fosservices.BinderService", r"^  class #440: AmazonUserManagerService\.BinderService", {
            name: fos_specs[name] for name in (
                "BinderService.<init>",
                "enableKftLauncherComponent(UserInfo)",
                "tryEnableKftLauncherComponent(UserInfo)",
                "enableKftLauncher(UserInfo)",
            )
        }),
        ("fosservices.AmazonUserManagerService", r"^  class #441: AmazonUserManagerService ", {
            "AmazonUserManagerService.checkManageUsersPermission": fos_specs["AmazonUserManagerService.checkManageUsersPermission"],
            "AmazonUserManagerService.onBootPhase": fos_specs["AmazonUserManagerService.onBootPhase"],
            "AmazonUserManagerService.onStart": fos_specs["AmazonUserManagerService.onStart"],
            "AmazonUserManagerService.getSystemServiceName": fos_specs["AmazonUserManagerService.getSystemServiceName"],
        }),
    ]
    framework_regions = [
        ("boot-fosframework.AmazonUserManagerImpl", r"^  class #2131: AmazonUserManagerImpl ", {
            "AmazonUserManagerImpl.createChildUser": framework_specs["AmazonUserManagerImpl.createChildUser"],
        }),
        ("boot-fosframework.IAmazonUserManager.Stub.Proxy", r"^  class #2135: IAmazonUserManager\.Stub\.Proxy ", {
            "IAmazonUserManager.Proxy.enableKftLauncher": framework_specs["IAmazonUserManager.Proxy.enableKftLauncher"],
        }),
        ("boot-fosframework.IAmazonUserManager.Stub", r"^  class #2136: IAmazonUserManager\.Stub ", {
            "IAmazonUserManager.Stub.onTransact": framework_specs["IAmazonUserManager.Stub.onTransact"],
        }),
    ]
    rows: List[Dict[str, object]] = []
    for _label, pattern_map, spec_map in fos_regions:
        region, base, _end = class_region(fos_lines, pattern_map)
        region_rows = method_rows(fos_path, region, spec_map) if region else []
        for row in region_rows:
            if isinstance(row["start_line"], int):
                row["start_line"] += base - 1
                row["end_line"] += base - 1
        rows.extend(region_rows)
    for _label, pattern_map, spec_map in framework_regions:
        region, base, _end = class_region(framework_lines, pattern_map)
        region_rows = method_rows(framework_path, region, spec_map) if region else []
        for row in region_rows:
            if isinstance(row["start_line"], int):
                row["start_line"] += base - 1
                row["end_line"] += base - 1
        rows.extend(region_rows)
    write_csv(output / "kft_tx3_method_security.csv", rows)

    service_rows = [row for row in rows if row["method"] in {
        "BinderService.<init>", "enableKftLauncherComponent(UserInfo)",
        "tryEnableKftLauncherComponent(UserInfo)", "enableKftLauncher(UserInfo)",
        "AmazonUserManagerService.checkManageUsersPermission", "AmazonUserManagerService.onBootPhase",
        "AmazonUserManagerService.onStart", "AmazonUserManagerService.getSystemServiceName",
    }]
    tx3 = next((row for row in rows if row["method"] == "enableKftLauncher(UserInfo)" and isinstance(row["start_line"], int)), None)
    check = next((row for row in rows if row["method"] == "AmazonUserManagerService.checkManageUsersPermission" and isinstance(row["start_line"], int)), None)
    tx3_has_local_check = bool(tx3 and (tx3["calling_permission_checks"] or tx3["calling_identity_reads"]))
    check_has_manage = bool(check and check["manage_users_literal"])
    summary = {
        "device_contacted": False,
        "binder_invoked": False,
        "exploit_attempted": False,
        "source_sha256": {str(fos_path): sha256(fos_path), str(framework_path): sha256(framework_path)},
        "service_name": "amazonusermanagerservice",
        "descriptor": "amazon.os.IAmazonUserManager",
        "transaction": 3,
        "static_sink": {
            "method": "AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)",
            "effects": [
                "enable com.amazon.tahoe/.launcher.FreeTimeLauncherActivity",
                "disable com.amazon.firelauncher",
                "disable com.android.launcher3",
            ],
            "user_selector": "UserInfo.id",
        },
        "authorization_review": {
            "tx3_local_caller_check_visible": tx3_has_local_check,
            "checkManageUsersPermission_exists": check_has_manage,
            "checkManageUsersPermission_direct_callers_in_bounded_slice": [
                "AmazonUserManagerService.getUserSortedListFromFile"
            ],
            "enableKftLauncher_calls_checkManageUsersPermission": False,
            "enableKftLauncher_clears_calling_identity": bool(tx3 and tx3["clear_calling_identity"]),
            "tryEnable_path_calls_setters_before_identity_clear": True,
            "classification": "static deputy review point; runtime exploitability not established",
        },
        "method_rows": len(rows),
        "outputs": ["kft_tx3_method_security.csv", "kft_tx3_summary.json", "kft_tx3_call_graph.mmd"],
    }
    (output / "kft_tx3_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (output / "kft_tx3_call_graph.mmd").write_text(
        "flowchart TD\n"
        "  C[AmazonUserManagerImpl.createChildUser] --> P[IAmazonUserManager.Proxy.enableKftLauncher]\n"
        "  P --> T[Binder.transact code 3]\n"
        "  T --> S[IAmazonUserManager.Stub.onTransact]\n"
        "  S --> B[BinderService.enableKftLauncher(UserInfo)]\n"
        "  B --> E[tryEnableKftLauncherComponent(UserInfo)]\n"
        "  E --> W[enableKftLauncherComponent(UserInfo)]\n"
        "  W --> Q[AmazonPackageManager setters using UserInfo.id]\n"
        "  Q --> F[Fire Launcher state=2 for supplied user]\n"
        "  B -. after try path .-> I[clearCallingIdentity before DPM empowerment]\n"
        "  M[checkManageUsersPermission] -. bounded caller .-> U[getUserSortedListFromFile]\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
