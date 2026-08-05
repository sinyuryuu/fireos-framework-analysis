#!/usr/bin/env python3
"""Close the saved PS7331 PackageManagerDenyList data-flow evidence.

This is a host-only, read-only audit.  It reads preserved VDEX disassembly,
the saved fosinit registration, and the earlier read-only device ACL capture.
It never contacts ADB, sends a broadcast, invokes Binder, changes a property,
or writes a device/system file.  The report intentionally distinguishes the
static deny-list source shape from the still-unreadable live membership set.
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


DEFAULT_OUTPUT = Path("artifacts/phase6ai/denylist-flow-20260805-01")
FOS_REL = Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
SERVICES_REL = Path("decompiled/baksmali/vdexExtractor/services/disassembly.log")
FOSINIT_REL = Path("artifacts/amazon-services/amazonpackagemanager_fosinit.xml")
ACL_FILES = (
    Path("artifacts/phase6k/readonly-device-20260805-01/deny_list_ls.stdout.txt"),
    Path("artifacts/phase6k/readonly-device-20260805-01/deny_list_stat.stdout.txt"),
    Path("artifacts/phase6k/readonly-device-20260805-01/deny_list_shared_pref_ls.stderr.txt"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def line_numbers(text: str, needle: str) -> list[int]:
    return [n for n, line in enumerate(text.splitlines(), 1) if needle in line]


def first_line(text: str, needle: str) -> int | None:
    hits = line_numbers(text, needle)
    return hits[0] if hits else None


def require_inputs(root: Path) -> list[Path]:
    paths = [root / FOS_REL, root / SERVICES_REL, root / FOSINIT_REL]
    paths.extend(root / rel for rel in ACL_FILES)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing input(s): " + ", ".join(missing))
    return paths


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def add_row(rows: list[dict[str, str]], evidence_id: str, stage: str, owner: str,
            method: str, source: str, location: str, operation: str,
            condition: str, effect: str, trigger: str, shell_boundary: str,
            confidence: str, status: str) -> None:
    rows.append({
        "evidence_id": evidence_id,
        "stage": stage,
        "owner": owner,
        "method_or_artifact": method,
        "source": source,
        "location": location,
        "operation": operation,
        "input_or_condition": condition,
        "output_effect": effect,
        "caller_or_trigger": trigger,
        "shell_boundary": shell_boundary,
        "confidence": confidence,
        "status": status,
    })


def build_rows(root: Path, fos: str, services: str, fosinit: str,
               acl_text: str) -> tuple[list[dict[str, str]], dict[str, object]]:
    fos_source = rel(root, root / FOS_REL)
    services_source = rel(root, root / SERVICES_REL)
    fosinit_source = rel(root, root / FOSINIT_REL)
    rows: list[dict[str, str]] = []

    gate_line = first_line(fos, "virtual_method #7607: shouldProtectPackage")
    gate_end = first_line(fos, "06a640:")
    add_row(
        rows, "6AI-DL-002", "consumer_gate", "Amazon system-server callback",
        "ControlProtectedPackagesCallback.shouldProtectPackage(int,String,Context)",
        fos_source, f"lines {gate_line}-{gate_end}; smali 0x06a61a-0x06a640",
        "isSystemApp -> shouldDisableAmazonApp -> contains(package) -> UID comparison",
        "system/updated-system application AND deny-list membership AND caller UID == 2000",
        "returns true to the vendor callback dispatcher; the PackageManager protection path can reject the mutation",
        "VendorProtectedPackagesCallback.callShouldProtectPackage",
        "system-server code; no shell input to this method was found",
        "Confirmed", "static predicate; live literal membership pending",
    )

    dispatcher_line = first_line(services, "direct_method #42965: callShouldProtectPackage")
    dispatcher_end = first_line(services, "302b52:")
    add_row(
        rows, "6AI-DL-003", "callback_dispatch", "AOSP-shaped Fire OS framework",
        "VendorProtectedPackagesCallback.callShouldProtectPackage(callbacks,uid,package,context)",
        services_source, f"lines {dispatcher_line}-{dispatcher_end}; smali 0x302b34-0x302b52",
        "iterate callback array; invoke shouldProtectPackage; OR each boolean result",
        "any registered vendor callback may return true",
        "propagates a vendor protection decision to the caller",
        "PackageManagerService / ActivityManagerService callers in saved services VDEX",
        "not a shell command; callback array is framework-owned",
        "Confirmed", "framework callback fan-in",
    )

    registration_line = first_line(fosinit, 'base="com.android.server.pm.VendorProtectedPackagesCallback"')
    add_row(
        rows, "6AI-DL-004", "callback_registration", "Amazon fosinit",
        "ControlProtectedPackagesCallback registration",
        fosinit_source, f"XML line {registration_line or 'not resolved'}",
        "register Amazon callback as a SYSTEMSERVER VendorProtectedPackagesCallback",
        "callback implementation is declared with classLoader=SYSTEMSERVER",
        "makes the Amazon callback discoverable by VendorProtectedPackagesCallback.findCallbacks",
        "system-server startup callback discovery",
        "not user-writable; no shell registration route",
        "Confirmed", "registration provenance",
    )

    service_init_line = first_line(fos, "virtual_method #7558: onBootPhase")
    helper_new_line = first_line(fos, "new-instance v0, Lcom/amazon/android/service/pm/DenyListArcusHelper;")
    add_row(
        rows, "6AI-DL-005", "helper_initialization", "AmazonPackageManagerService",
        "AmazonPackageManagerService.onBootPhase(int)",
        fos_source, f"onBootPhase line {service_init_line}; helper construction line {helper_new_line}",
        "construct DenyListArcusHelper at the package-manager vendor service boot phase",
        "saved code constructs the helper at boot phase 500; this is distinct from the phase-550 OTA broadcast branch",
        "creates the persistent deny-list reader/producer and schedules initialization",
        "AmazonPackageManagerService.onBootPhase",
        "system-server service lifecycle; no shell trigger identified",
        "Confirmed", "startup path",
    )

    helper_ctor_line = first_line(fos, "direct_method #7615: <init> (Landroid/content/Context;)V")
    add_row(
        rows, "6AI-DL-006", "persistent_store", "DenyListArcusHelper",
        "DenyListArcusHelper(Context)",
        fos_source, f"constructor line {helper_ctor_line}; smali 0x06a9ce-0x06aa68",
        "createDeviceProtectedStorageContext -> Environment.getDataSystemDirectory -> SharedPreferences(File,0); post Runnable",
        "file basename PackageManagerDenyList; device-protected storage; handler thread initialized",
        "establishes the backing store before seed or Arcus refresh",
        "constructor from AmazonPackageManagerService.onBootPhase",
        "live file metadata is visible to shell, content is not",
        "Confirmed", "persistent-store shape",
    )

    get_shared_line = first_line(fos, "direct_method #7604: getSharedPrefPackages")
    add_row(
        rows, "6AI-DL-007", "consumer_read", "ControlProtectedPackagesCallback",
        "getSharedPrefPackages(Context)",
        fos_source, f"method line {get_shared_line}; smali 0x06a648-0x06a69a",
        "open device-protected PackageManagerDenyList and getStringSet(DenyListKeyPackages)",
        "returns the stored set, or null/empty fallback when unavailable",
        "feeds shouldDisableAmazonApp.contains(packageName)",
        "ControlProtectedPackagesCallback.shouldDisableAmazonApp",
        "shell cannot read the contents of the backing file in the saved capture",
        "Confirmed", "read path",
    )

    seed_line = first_line(fos, "direct_method #7621: extractListFromResorces")
    add_row(
        rows, "6AI-DL-008", "initial_seed", "DenyListArcusHelper",
        "extractListFromResorces()",
        fos_source, f"method line {seed_line}; smali 0x06aa86-0x06aaca",
        "if SharedPreferences does not contain DenyListKeyPackages, parse processJSON and commit a HashSet",
        "seed is conditional on key absence; existing persisted set is not replaced by this branch",
        "creates initial deny-list state from a system raw resource",
        "DenyListArcusHelper constructor",
        "resource is system-owned; no shell writer identified",
        "Confirmed", "resource-backed seed",
    )

    process_line = first_line(fos, "direct_method #7624: processJSON ()Ljava/util/List;")
    add_row(
        rows, "6AI-DL-009", "initial_seed", "DenyListArcusHelper",
        "processJSON()",
        fos_source, f"method line {process_line}; smali 0x06a7f0-0x06a95e",
        "Resources.getSystem().openRawResource(0x7e05000a); parse JSON; read packages_deny_list array",
        "resource ID and JSON key are observed; human-readable resource name/content is not in current readable scope",
        "returns package-name strings to extractListFromResorces",
        "extractListFromResorces",
        "no shell path to replace the system raw resource",
        "Confirmed", "resource identity/content unresolved",
    )

    property_line = first_line(fos, 'const-string v0, "persist.sys.denylist_arcusid"')
    add_row(
        rows, "6AI-DL-010", "refresh_selector", "DenyListArcusHelper",
        "initialize()",
        fos_source, f"method line {first_line(fos, 'direct_method #7623: initialize ()V')}; property line {property_line}; smali 0x06ab96-0x06abf2",
        "read SystemProperties.get(persist.sys.denylist_arcusid, resource-default); register Arcus and syncId when non-empty",
        "property selects the Arcus configuration identifier; empty value returns without registering the refresh receiver",
        "selects the dynamic refresh channel; it does not itself write the package set",
        "constructor-posted DenyListArcusHelper$1.run -> access$000 -> initialize",
        "property mutation deliberately not attempted; shell writability not established",
        "Confirmed", "runtime refresh selector",
    )

    receiver_line = first_line(fos, "direct_method #7625: registerArcusBroadcastReceivers")
    add_row(
        rows, "6AI-DL-011", "refresh_registration", "DenyListArcusHelper",
        "registerArcusBroadcastReceivers(String)",
        fos_source, f"method line {receiver_line}; smali 0x06abf8-0x06ac66",
        "construct amazon.arcus.sync.<id> and amazon.arcus.sync.unmod.<id>; register an in-process BroadcastReceiver",
        "actions are data-derived from the Arcus ID; receiver is registered by a system-server-owned Context",
        "connects Arcus configuration updates to the refresh worker",
        "initialize",
        "no broadcast was sent; action replay is authorization-sensitive and excluded",
        "Confirmed", "dynamic trigger registration",
    )

    on_receive_line = first_line(fos, "virtual_method #7613: onReceive (Landroid/content/Context;Landroid/content/Intent;)V")
    add_row(
        rows, "6AI-DL-012", "refresh_trigger", "DenyListArcusHelper$2",
        "onReceive(Context,Intent)",
        fos_source, f"method line {on_receive_line}; smali 0x06a742-0x06a7cc",
        "compare action to sync/unmod strings; post a worker Runnable when either matches",
        "only the two registered action strings reach the worker branch",
        "schedules ArcusFwkManager.openConfiguration(arcusId)",
        "registered BroadcastReceiver",
        "no exported component or shell broadcast route is established by this method",
        "Confirmed", "refresh trigger",
    )

    worker_line = first_line(fos, "virtual_method #7611: run ()V")
    add_row(
        rows, "6AI-DL-013", "refresh_worker", "DenyListArcusHelper$2$1",
        "run()",
        fos_source, f"worker method line {worker_line}; smali 0x06a6f2-0x06a720",
        "ArcusFwkManager.openConfiguration(arcusId) -> synthetic access$300 -> getDenyList(String)",
        "configuration payload is obtained from Arcus before local parsing",
        "passes the JSON string to getDenyList",
        "BroadcastReceiver.onReceive posted worker",
        "Arcus manager is a system service dependency; no shell API was invoked",
        "Confirmed", "refresh worker",
    )

    deny_line = first_line(fos, "direct_method #7622: getDenyList (Ljava/lang/String;)V")
    add_row(
        rows, "6AI-DL-014", "refresh_parse", "DenyListArcusHelper",
        "getDenyList(String)",
        fos_source, f"method line {deny_line}; smali 0x06aad0-0x06ab80",
        "parse JSON; read packages_deny_list JSONArray; convert elements to List<String>; call saveProtectedPackages",
        "empty/missing list logs no protected apps; JSON/IO exceptions return without a write",
        "invokes saveProtectedPackages(List)",
        "DenyListArcusHelper$2$1.run",
        "payload source is Arcus; no shell-controlled payload path observed",
        "Confirmed", "runtime replacement parser",
    )

    save_line = first_line(fos, "direct_method #7626: saveProtectedPackages (Ljava/util/List;)V")
    save_call_line = first_line(fos, "invoke-direct {v5, v2}, Lcom/amazon/android/service/pm/DenyListArcusHelper;.saveProtectedPackages")
    add_row(
        rows, "6AI-DL-015", "persistent_writer", "DenyListArcusHelper",
        "saveProtectedPackages(List<String>)",
        fos_source, f"method line {save_line}; call site line {save_call_line}; smali 0x06ac6c-0x06acd4",
        "copy List to HashSet; if key exists remove it; putStringSet(DenyListKeyPackages); commit()",
        "writer replaces the persisted set atomically at the SharedPreferences API level",
        "only observed direct caller is getDenyList; initial seed writes through its own putStringSet/commit branch",
        "getDenyList; no public Binder or shell caller found in saved disassembly",
        "device-protected system-owned SharedPreferences; shell content read denied",
        "Confirmed", "writer closure",
    )

    registration_call = first_line(fos, "invoke-direct {v0, v1}, Lcom/amazon/android/service/pm/DenyListArcusHelper;.<init>:(Landroid/content/Context;)V")
    add_row(
        rows, "6AI-DL-016", "external_caller_search", "Saved PS7331 artifacts",
        "DenyListArcusHelper caller inventory",
        fos_source, f"constructor call line {registration_call}; all symbol occurrences audited by script",
        "search direct constructor/getDenyList/saveProtectedPackages references across saved fosservices disassembly",
        "external entry found: AmazonPackageManagerService.onBootPhase constructs the helper; subsequent writes are internal callbacks/workers",
        "no separate shell/exported/public writer found in the selected saved disassembly",
        "AmazonPackageManagerService.onBootPhase; helper inner classes",
        "negative result is limited to the preserved artifact scope; it is not a proof that no other binary can influence Arcus",
        "Strong evidence", "scope-limited caller inventory",
    )

    acl_mode = re.search(r"-rw-rw---- .* /data/system/PackageManagerDenyList", acl_text)
    acl_stat = "system:system mode 0660 and 2645 bytes" if acl_mode else "metadata pattern not resolved"
    add_row(
        rows, "6AI-DL-017", "live_acl", "PS7331 device shell capture",
        "PackageManagerDenyList live metadata",
        rel(root, root / ACL_FILES[0]), "saved read-only capture; see ACL files and hashes",
        "ls/stat metadata succeeds; content and shared-preference XML listing are denied",
        acl_stat,
        "does not expose literal package membership to shell",
        "adb shell ls/stat only; no pull/content read",
        "no mutation, no elevated read, no attempt to bypass SELinux/file ACL",
        "Confirmed", "membership boundary",
    )

    occurrences = {
        "saveProtectedPackages": line_numbers(fos, "saveProtectedPackages"),
        "getDenyList": line_numbers(fos, "getDenyList"),
        "DenyListArcusHelper_constructor": line_numbers(fos, "new-instance v0, Lcom/amazon/android/service/pm/DenyListArcusHelper;"),
        "DenyListKeyPackages": line_numbers(fos, '"DenyListKeyPackages"'),
        "packages_deny_list": line_numbers(fos, '"packages_deny_list"'),
        "denylist_property": line_numbers(fos, '"persist.sys.denylist_arcusid"'),
    }
    caller_classification = {
        "save_definition_lines": [n for n in occurrences["saveProtectedPackages"] if n == save_line],
        "save_direct_call_lines": [n for n in occurrences["saveProtectedPackages"] if n != save_line],
        "get_definition_lines": [n for n in occurrences["getDenyList"] if n == deny_line],
        "constructor_lines": occurrences["DenyListArcusHelper_constructor"],
        "note": "The saved disassembly exposes the helper constructor as the external service entry and the receiver worker as the refresh entry; no public shell/Binder writer was found in this scope.",
    }
    details = {
        "line_occurrences": occurrences,
        "caller_classification": caller_classification,
        "resource_ids": {
            "deny_list_json": "0x7e05000a",
            "arcus_default_id": "0x7e060058",
        },
    }
    return rows, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--table-output", type=Path, default=Path("output/tables/phase6ai-denylist-flow.csv"))
    parser.add_argument("--graph-output", type=Path, default=Path("output/call-graphs/phase6ai-denylist-flow.mmd"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    table_output = args.table_output if args.table_output.is_absolute() else root / args.table_output
    graph_output = args.graph_output if args.graph_output.is_absolute() else root / args.graph_output

    try:
        inputs = require_inputs(root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    fos = (root / FOS_REL).read_text(encoding="utf-8", errors="replace")
    services = (root / SERVICES_REL).read_text(encoding="utf-8", errors="replace")
    fosinit = (root / FOSINIT_REL).read_text(encoding="utf-8", errors="replace")
    acl_text = "\n".join((root / relpath).read_text(encoding="utf-8", errors="replace") for relpath in ACL_FILES)
    rows, details = build_rows(root, fos, services, fosinit, acl_text)

    if args.dry_run:
        print(json.dumps({
            "device_contacted": False,
            "would_write": str(output),
            "would_write_table": str(table_output),
            "would_write_graph": str(graph_output),
            "input_count": len(inputs),
            "row_count": len(rows),
            "stages": sorted({row["stage"] for row in rows}),
            "direct_save_call_lines": details["caller_classification"]["save_direct_call_lines"],
        }, indent=2))
        return 0

    if output.exists() and any(output.iterdir()):
        print(f"refusing to overwrite non-empty output: {output}", file=sys.stderr)
        return 2
    output.mkdir(parents=True, exist_ok=True)

    input_manifest = [
        {"path": rel(root, path), "sha256": sha256(path), "size": path.stat().st_size}
        for path in inputs
    ]
    write_json(output / "input-sha256.json", input_manifest)
    write_json(output / "flow-details.json", details)
    fields = list(rows[0].keys())
    with (output / "denylist-flow.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    graph = """flowchart TD
  A[pm / cmd package shell UID 2000] --> B[PackageManagerService enabled-state path]
  B --> C[ProtectedPackages.isPackageStateProtected]
  C --> D[VendorProtectedPackagesCallback.callShouldProtectPackage]
  D --> E[ControlProtectedPackagesCallback.shouldProtectPackage]
  E --> F{system or privileged app?}
  F -->|yes| G[getSharedPrefPackages]
  G --> H[PackageManagerDenyList / DenyListKeyPackages]
  H --> I{package in set?}
  I -->|yes + UID 2000| J[protected=true]
  J --> K[PackageManager rejects before state write]

  L[AmazonPackageManagerService.onBootPhase 500] --> M[DenyListArcusHelper constructor]
  M --> N[device-protected SharedPreferences]
  M --> O[extractListFromResorces]
  O --> P[Resources.getSystem raw 0x7e05000a]
  P --> Q[packages_deny_list JSON]
  Q --> R[putStringSet + commit initial seed]
  M --> S[initialize]
  S --> T[persist.sys.denylist_arcusid]
  S --> U[Arcus register + syncId + dynamic receiver]
  U --> V[amazon.arcus.sync.<id> / unmod.<id>]
  V --> W[onReceive -> Handler worker]
  W --> X[ArcusFwkManager.openConfiguration]
  X --> Y[getDenyList JSON parser]
  Y --> Z[saveProtectedPackages]
  Z --> N
"""
    write_text(output / "denylist-flow.mmd", graph)

    if table_output.exists() or graph_output.exists():
        raise FileExistsError(
            f"refusing to overwrite canonical output: {table_output} or {graph_output}"
        )
    table_output.parent.mkdir(parents=True, exist_ok=True)
    with table_output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    write_text(graph_output, graph)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted": False,
        "unsafe_operations_performed": False,
        "conclusions": {
            "consumer_gate": "Amazon ControlProtectedPackagesCallback is registered under the Fire OS VendorProtectedPackagesCallback fan-in and checks system/privileged status, deny-list membership, and UID 2000.",
            "initial_seed": "The first seed is resource-backed JSON (resource ID 0x7e05000a, key packages_deny_list) and is committed only when DenyListKeyPackages is absent.",
            "runtime_refresh": "An Arcus-selected, dynamically registered sync/unmod receiver obtains JSON and replaces the stored set through saveProtectedPackages.",
            "writer": "The saved disassembly shows no public shell/Binder writer; the direct writer path is internal to DenyListArcusHelper and its Arcus worker.",
            "membership": "The live shell capture does not expose the set contents; literal com.amazon.firelauncher membership remains unobserved in this artifact scope.",
            "home_relation": "This is a package-state protection flow, not a HOME resolver or preferred-activity selector.",
        },
        "input_manifest": input_manifest,
        "details": details,
        "rows": rows,
    }
    write_json(output / "summary.json", summary)

    manifest = [
        f"{sha256(path)}  {path.name}"
        for path in sorted(output.iterdir())
        if path.name != "sha256sums.txt"
    ]
    write_text(output / "sha256sums.txt", "\n".join(manifest) + "\n")
    print(json.dumps({"output": str(output), "row_count": len(rows), "device_contacted": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
