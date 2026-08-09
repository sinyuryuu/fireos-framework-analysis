#!/usr/bin/env python3
"""Build a host-only caller -> permission -> sink/user-scope evidence ledger.

This tool intentionally consumes preserved Phase 6 artifacts only.  It does not
connect to a device, invoke Binder/service calls, inspect live state, or modify
any input evidence.  The output directory is write-once by default.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUTS = [
    ROOT / "artifacts/phase6mc-caller-provenance-20260810-01/caller-provenance.csv",
    ROOT / "artifacts/phase6kv/pms-home-caller-closure-20260810-01/pms-home-callers.csv",
    ROOT / "artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv",
    ROOT / "artifacts/phase6mg-oobe-helper-scope-20260810-01/helper-scope.csv",
    ROOT / "artifacts/phase6bk/ipc-ota-closure-20260810-02/method-map.csv",
    ROOT / "findings/phase-6kv-pms-home-caller-closure.md",
    ROOT / "findings/phase-6mg-oobe-helper-scope.md",
    ROOT / "findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md",
    ROOT / "findings/phase-6er-amazon-prewarm-confused-deputy.md",
    ROOT / "findings/phase-6r-bootafter-system-ota-authorization.md",
]

MATRIX_FIELDS = [
    "route_id",
    "surface",
    "caller_or_entry",
    "registration_or_interface",
    "permission_or_gate",
    "identity_handling",
    "sink",
    "user_scope",
    "home_or_package_relevance",
    "service_manager_or_runtime_boundary",
    "low_privilege_caller_found",
    "dynamic_test_allowed",
    "classification",
    "confidence",
    "evidence",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def evidence_for(row: Dict[str, str]) -> str:
    return row.get("evidence", "") or row.get("source", "")


def base_route(route_id: str, **values: str) -> Dict[str, str]:
    route = {field: "" for field in MATRIX_FIELDS}
    route["route_id"] = route_id
    route.update({key: str(value) for key, value in values.items() if key in route})
    return route


def caller_routes(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    routes: List[Dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        surface = row["surface"]
        if surface == "H2 household service":
            classification = "TRUSTED_PROFILE_LIFECYCLE_NO_HOME"
            relevance = "Creates/removes child or adult users; no Fire/HOME writer in bounded APK evidence"
            boundary = "Exported service is signature-bound; no shell route"
            confidence = "Strong evidence"
        elif surface == "H2 create-child path":
            classification = "CHILD_PROFILE_ONLY_NO_USER0_HOME"
            relevance = "Child-user lifecycle only; no User-0 HOME selection"
            boundary = "Signature-bound H2 workflow; no shell route"
            confidence = "Strong evidence"
        elif surface == "IAmazonUserManager tx3":
            classification = "CHILD_SCOPED_PACKAGE_STATE_NO_USER0_HOME"
            relevance = "Launcher package/component state writer, but scoped by supplied child UserInfo.id"
            boundary = "Private service-manager/SELinux boundary; tx3 not replayed"
            confidence = "Strong evidence"
        elif surface == "IAmazonUserManager tx4":
            classification = "LOW_PRIVILEGE_SETTINGS_ONLY_NO_HOME"
            relevance = "Writes setup-state settings; no package, resolver, or HOME sink"
            boundary = "Private service boundary; prior controlled APK reachability only"
            confidence = "Confirmed"
        elif surface == "AmazonActivityManager prewarm":
            classification = "PREWARM_PROCESS_START_NO_HOME"
            relevance = "Starts/prewarms a requested process; no HOME component or preferred writer"
            boundary = "Private service-manager/SELinux boundary; APP_PREWARM gate"
            confidence = "Strong evidence"
        elif surface == "post-system-OTA OOBE sender":
            classification = "SYSTEM_LIFECYCLE_OOBE_NOT_SHELL_RELAY"
            relevance = "May change OOBE/setup state and OobeHomeActivity during system OTA lifecycle"
            boundary = "system_server boot phase + protected broadcast; no ordinary caller"
            confidence = "Strong evidence"
        else:
            classification = "GENERIC_STATE_WRITER_NO_HOME_EVIDENCE"
            relevance = "Generic package/component state writer; no Fire/HOME controller in bounded scan"
            boundary = "Data-app or internal path; exact caller not invoked"
            confidence = "Probable"

        routes.append(
            base_route(
                f"CALLER-{index:02d}",
                surface=surface,
                caller_or_entry=row["caller_or_entry"],
                registration_or_interface=row["registration_or_interface"],
                permission_or_gate=row["permission_or_gate"],
                identity_handling=row["identity_handling"],
                sink=row["sink"],
                user_scope=row["user_scope"],
                home_or_package_relevance=relevance,
                service_manager_or_runtime_boundary=boundary,
                low_privilege_caller_found=row["low_privilege_caller_found"],
                dynamic_test_allowed=row["dynamic_test_allowed"],
                classification=classification,
                confidence=confidence,
                evidence=evidence_for(row),
            )
        )
    return routes


def pms_routes(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    routes: List[Dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        classification = row["classification"]
        if classification == "amazon_launcher_state_writer_child_scoped":
            route_class = "CHILD_SCOPED_PACKAGE_STATE_NO_USER0_HOME"
            relevance = "Fire/Launcher3/Tahoe state writer; not a formal User-0 HOME selector"
            scope = "Supplied UserInfo.id; child lifecycle scope"
            boundary = "AmazonUserManagerService internal/system-server path"
            confidence = "Strong evidence"
        elif classification == "shell_command_to_framework_writer":
            route_class = "FORMAL_PACKAGE_STATE_FRONTEND_GATED"
            relevance = "Formal package-state API; protected-package checks remain in framework"
            scope = "Requested package/component and user; framework gate applies"
            boundary = "PackageManagerShellCommand → IPackageManager → PackageManagerService"
            confidence = "Confirmed"
        elif classification == "framework_internal_sink_or_helper" and (
            "Preferred" in row["sink"] or "replacePreferred" in row["sink"]
        ):
            route_class = "FORMAL_HOME_INTERNAL_WRITER"
            relevance = "Internal preferred/HOME writer; no low-privilege caller established"
            scope = "Framework-selected user; internal caller context"
            boundary = "PackageManagerService internal helper"
            confidence = "Confirmed"
        elif classification.startswith("amazon_oobe"):
            route_class = "OOBE_COMPONENT_WRITER"
            relevance = "OOBE registration component; not Fire Launcher HOME selection"
            scope = "Context-bound; explicit user mapping not present at call site"
            boundary = "Amazon OOBE lifecycle path"
            confidence = "Strong evidence"
        elif classification == "device_policy_trusted_writer":
            route_class = "DEVICE_POLICY_TRUSTED_WRITER"
            relevance = "Device/profile-owner package state; no ordinary shell path"
            scope = "Device/profile-owner controlled user"
            boundary = "DevicePolicyManagerService internal path"
            confidence = "Strong evidence"
        else:
            route_class = "OTHER_SYSTEM_STATE_WRITER"
            relevance = "Package/component or preferred-state related system writer"
            scope = row["scope_or_limit"]
            boundary = "System-server or privileged component; caller provenance bounded"
            confidence = "Probable"

        routes.append(
            base_route(
                f"PMS-{index:03d}",
                surface="PMS/HOME caller inventory",
                caller_or_entry=f"{row['caller_class']}.{row['caller_method']} {row['caller_descriptor']}",
                registration_or_interface=row["source_kind"],
                permission_or_gate="Not established at this static invoke site",
                identity_handling="Not established at this static invoke site",
                sink=row["sink"],
                user_scope=scope,
                home_or_package_relevance=relevance,
                service_manager_or_runtime_boundary=boundary,
                low_privilege_caller_found="false",
                dynamic_test_allowed="false",
                classification=route_class,
                confidence=confidence,
                evidence=f"{row['source_file']}:{row['source_line']} (offset {row['instruction_offset']})",
            )
        )
    return routes


def callback_routes(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    routes: List[Dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        if row["resolve_override"] == "yes" and row["direct_ipm_resolve"] == "yes":
            route_class = "STANDARD_RESOLVER_DELEGATION_NO_FIRE_OVERRIDE"
            relevance = "HOME resolution delegates to IPackageManager then applies an uninstalled-app filter"
            sink = "IPackageManager.resolveIntent → ResolveInfo filter"
            confidence = row["confidence"] or "Confirmed"
        else:
            route_class = "NO_CONCRETE_HOME_CALLBACK_OVERRIDE"
            relevance = "No concrete resolveIntent override; no Fire Launcher selection evidence"
            sink = "Inherited callback/base behavior"
            confidence = row["confidence"] or "Confirmed"
        routes.append(
            base_route(
                f"CALLBACK-{index:02d}",
                surface="Vendor HOME callback inventory",
                caller_or_entry=row["implementation"],
                registration_or_interface=f"base={row['base']}; registered={row['registered']}",
                permission_or_gate="Vendor callback registration; caller permission not shown in selected artifact",
                identity_handling="No identity rewrite shown in selected callback evidence",
                sink=sink,
                user_scope="Framework resolver user; no separate Amazon user writer shown",
                home_or_package_relevance=relevance,
                service_manager_or_runtime_boundary="fosinit callback registration",
                low_privilege_caller_found="unknown",
                dynamic_test_allowed="false",
                classification=route_class,
                confidence=confidence,
                evidence=f"{row['source']}; resolve_line={row['resolve_line'] or 'n/a'}",
            )
        )
    return routes


def oobe_routes(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = {}
    for row in rows:
        key = (row["source"], row["signal"], row["state_domain"])
        grouped.setdefault(key, row)

    routes: List[Dict[str, str]] = []
    for index, row in enumerate(grouped.values(), 1):
        signal = row["signal"]
        if signal == "global_settings_write":
            route_class = "OOBE_GLOBAL_SETUP_STATE_WRITER_CONTEXT_BOUND"
            relevance = "Writes OOBE/provisioning state; global namespace is not a HOME selection record"
        elif signal == "secure_settings_write" or signal == "oobe_helper_fg_method":
            route_class = "OOBE_SECURE_SETUP_STATE_WRITER_CONTEXT_BOUND"
            relevance = "Writes setup-state secure setting; no package/resolver sink"
        elif signal == "component_state_write":
            route_class = "OOBE_COMPONENT_STATE_WRITER_CONTEXT_BOUND"
            relevance = "Enables/disables OOBE receiver/component; not Fire Launcher selector"
        else:
            route_class = "OOBE_HELPER_DELEGATED_SCOPE_UNKNOWN"
            relevance = "OOBE helper call; context/user mapping not explicit"

        routes.append(
            base_route(
                f"OOBE-{index:02d}",
                surface="OOBE helper scope inventory",
                caller_or_entry=f"{Path(row['source']).name}:{row['method']}",
                registration_or_interface="JADX helper call site",
                permission_or_gate="OOBE lifecycle/receiver permission established outside helper",
                identity_handling="No Binder identity operation at helper call site",
                sink=row["source_text"],
                user_scope=row["user_scope"],
                home_or_package_relevance=relevance,
                service_manager_or_runtime_boundary="BootAfterSystemOTAReceiver / OOBE helper; no shell trigger permitted",
                low_privilege_caller_found="false",
                dynamic_test_allowed="false",
                classification=route_class,
                confidence="Strong evidence" if signal != "oobe_helper_fg_method" else "Probable",
                evidence=f"{row['source']}:{row['line']}",
            )
        )
    return routes


def write_csv(path: Path, rows: Sequence[Dict[str, str]], fields: Sequence[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mermaid() -> str:
    return """%% Phase 6MN host-only provenance closure; no live Binder or device action
flowchart LR
    A["Ordinary app / shell entry"] -->|"permission + service boundary"| B["Amazon Binder service"]
    B -->|"clearCallingIdentity where observed"| C["Privileged implementation"]
    C --> D{"State sink and user scope"}
    D -->|"tx4"| E["setup settings only; no HOME"]
    D -->|"tx3"| F["KFT launcher state for supplied child UserInfo.id"]
    D -->|"prewarm"| G["process start only; no HOME"]
    D -->|"OOBE"| H["context-bound setup/OobeHome state"]
    D -->|"PMS internal"| I["formal package/preferred writers; trusted path"]
    J["Vendor HOME callback"] -->|"delegates to IPackageManager.resolveIntent"| K["standard resolver + uninstalled filter"]
    F -.->|"no User-0 selector evidence"| L["Fire Launcher remains formal HOME"]
    E -.->|"no package/HOME sink"| L
    G -.->|"no component selection"| L
    K -.->|"no Fire literal / override in selected callback"| L
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=ROOT / "artifacts/phase6mn-ipc-user-scope-20260810-01",
    )
    parser.add_argument(
        "--table-output",
        type=Path,
        default=ROOT / "output/tables/phase6mn-ipc-user-scope-20260810-01.csv",
    )
    parser.add_argument(
        "--graph-output",
        type=Path,
        default=ROOT / "output/call-graphs/phase6mn-ipc-user-scope-20260810-01.mmd",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report inputs/outputs without writing files")
    parser.add_argument("--force", action="store_true", help="Overwrite only this tool's generated outputs")
    args = parser.parse_args()

    inputs = [path.resolve() for path in DEFAULT_INPUTS]
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        parser.error("missing preserved input(s): " + ", ".join(missing))

    outputs = [args.artifact_dir, args.table_output, args.graph_output]
    existing = [str(path) for path in outputs if path.exists()]
    if existing and not args.dry_run and not args.force:
        parser.error("refusing to overwrite existing output(s): " + ", ".join(existing))

    caller_file, pms_file, callback_file, oobe_file, method_file = inputs[:5]
    routes = []
    routes.extend(caller_routes(read_csv(caller_file)))
    routes.extend(pms_routes(read_csv(pms_file)))
    routes.extend(callback_routes(read_csv(callback_file)))
    routes.extend(oobe_routes(read_csv(oobe_file)))

    input_manifest = []
    for path in inputs:
        input_manifest.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size})

    classifications = Counter(route["classification"] for route in routes)
    summary = {
        "analysis": "Phase 6MN IPC/OOBE caller-to-user-scope closure",
        "mode": "host-only; preserved evidence only",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_head": "not resolved by this script; see git metadata",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "route_count": len(routes),
        "classification_counts": dict(sorted(classifications.items())),
        "device_contacted": False,
        "binder_or_service_call": False,
        "ioctl": False,
        "mutation": False,
        "reboot": False,
        "input_manifest": input_manifest,
        "bounded_negative": "No selected untrusted-to-Amazon route reaches a proven User-0 HOME/package-state sink; tx4 is settings-only and tx3 is child-scoped.",
        "scope_limit": "This is a selected-artifact provenance closure, not a binary-wide proof of absence.",
    }

    if args.dry_run:
        print(json.dumps({"inputs": input_manifest, "outputs": [str(path) for path in outputs], "routes": len(routes)}, indent=2))
        return 0

    args.artifact_dir.mkdir(parents=True, exist_ok=args.force)
    args.table_output.parent.mkdir(parents=True, exist_ok=True)
    args.graph_output.parent.mkdir(parents=True, exist_ok=True)

    artifact_table = args.artifact_dir / "route-matrix.csv"
    artifact_graph = args.artifact_dir / "route-flow.mmd"
    artifact_manifest = args.artifact_dir / "input-manifest.csv"
    artifact_summary = args.artifact_dir / "summary.json"
    write_csv(artifact_table, routes, MATRIX_FIELDS)
    args.table_output.write_text(artifact_table.read_text(encoding="utf-8"), encoding="utf-8")
    artifact_graph.write_text(mermaid(), encoding="utf-8")
    args.graph_output.write_text(mermaid(), encoding="utf-8")
    write_csv(artifact_manifest, input_manifest, ["path", "sha256", "bytes"])
    artifact_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    generated = [artifact_table, artifact_graph, artifact_manifest, artifact_summary, args.table_output, args.graph_output]
    with (args.artifact_dir / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for path in generated:
            stream.write(f"{sha256(path)}  {path.relative_to(ROOT)}\n")

    print(json.dumps({"artifact_dir": str(args.artifact_dir), "route_count": len(routes), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
