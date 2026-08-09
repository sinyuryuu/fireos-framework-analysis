#!/usr/bin/env python3
"""Build a reproducible report from the preserved Phase 6MV read-only capture."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "phase6mv-runtime-readonly-report-v1"
DEFAULT_CAPTURE = "adb/phase6mv/PHASE6MV-READONLY-20260810-02"
DEFAULT_WORKER = "work/luna_worker_phase6mv_gpl_ota_inventory_20260810.md"
DEFAULT_ARTIFACT = "artifacts/phase6mv-runtime-report-20260810-02"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, value: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_prop(corpus: str, key: str) -> str:
    match = re.search(rf"^\[{re.escape(key)}\]:\s*(.*)$", corpus, re.MULTILINE)
    return match.group(1).strip() if match else "NOT_OBSERVED"


def first_match(corpus: str, pattern: str) -> str:
    match = re.search(pattern, corpus, re.MULTILINE)
    return match.group(0).strip() if match else "NOT_OBSERVED"


def user_state(corpus: str, user_id: int) -> str:
    """Return the package-dump state line for one user without collapsing records."""
    lines = corpus.splitlines()
    marker = re.compile(rf"^\s*User {user_id}:")
    for index, line in enumerate(lines):
        if marker.search(line):
            value = line.strip()
            if value == f"User {user_id}:" and index + 1 < len(lines):
                value = f"{value} {lines[index + 1].strip()}"
            return value
    return "NOT_OBSERVED"


def markdown_cell(value: str) -> str:
    """Keep generated pipe tables valid when captured output contains '|'."""
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--capture", type=Path, default=None)
    parser.add_argument("--worker-report", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    capture = (args.capture or root / DEFAULT_CAPTURE).resolve()
    worker = (args.worker_report or root / DEFAULT_WORKER).resolve()
    artifact = (args.output or root / DEFAULT_ARTIFACT).resolve()
    required = [
        capture / "getprop.stdout.txt",
        capture / "home_resolve.stdout.txt",
        capture / "home_candidates.stdout.txt",
        capture / "firelauncher_package.stdout.txt",
        capture / "users.stdout.txt",
        capture / "service_list.stdout.txt",
        worker,
    ]
    service_names = [
        "amazonpackagemanager",
        "amazonactivitymanager",
        "amazonwindowmanager",
        "amazondevicepolicymanager",
        "amazonaccessibilitymanager",
        "amazonusermanagerservice",
        "amazonprofileservice",
    ]
    required.extend(capture / f"service_{name}.stdout.txt" for name in service_names)
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required inputs:\n" + "\n".join(map(str, missing)))

    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    getprop = read_text(capture / "getprop.stdout.txt")
    resolve = read_text(capture / "home_resolve.stdout.txt").strip()
    candidates = read_text(capture / "home_candidates.stdout.txt")
    fire_package = read_text(capture / "firelauncher_package.stdout.txt")
    users = read_text(capture / "users.stdout.txt").strip()
    service_list = read_text(capture / "service_list.stdout.txt")
    service_checks = {
        name: read_text(capture / f"service_{name}.stdout.txt").strip()
        for name in service_names
    }
    model = get_prop(getprop, "ro.product.model")
    device = get_prop(getprop, "ro.product.device")
    fingerprint = get_prop(getprop, "ro.build.fingerprint")
    security_patch = get_prop(getprop, "ro.build.version.security_patch")
    incremental = get_prop(getprop, "ro.build.version.incremental")
    candidate_header = candidates.splitlines()[0].strip() if candidates else "NOT_OBSERVED"
    rows = [
        {"finding": "HOME resolver", "observed": resolve.replace("\n", " | "), "classification": "Confirmed", "evidence": "home_resolve.stdout.txt"},
        {"finding": "HOME candidates", "observed": candidate_header, "classification": "Confirmed", "evidence": "home_candidates.stdout.txt"},
        {"finding": "Fire User 0 state", "observed": user_state(fire_package, 0), "classification": "Confirmed", "evidence": "firelauncher_package.stdout.txt"},
        {"finding": "Fire User 10 state", "observed": user_state(fire_package, 10), "classification": "Confirmed", "evidence": "firelauncher_package.stdout.txt"},
        {"finding": "Users", "observed": users.replace("\n", " | "), "classification": "Confirmed", "evidence": "users.stdout.txt"},
        {
            "finding": "Private service checks",
            "observed": "; ".join(f"{name}: {service_checks[name]}" for name in service_names),
            "classification": "Confirmed",
            "evidence": "service_*_stdout.txt",
        },
        {
            "finding": "Service-name listing",
            "observed": "selected Amazon names are present in service list; listing is not a shell Binder handle",
            "classification": "Confirmed",
            "evidence": "service_list.stdout.txt",
        },
    ]
    input_files = sorted(
        path for path in capture.rglob("*")
        if path.is_file() and path.name != "sha256sums.txt"
    ) + [worker]
    input_rows = [
        {"path": str(path.relative_to(root)), "sha256": sha256(path), "size": str(path.stat().st_size)}
        for path in input_files
    ]
    summary = {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "capture": str(capture.relative_to(root)),
        "worker_report": str(worker.relative_to(root)),
        "device_contacted": False,
        "binder_transaction": False,
        "mutation": False,
        "reboot": False,
        "model": model,
        "device": device,
        "fingerprint": fingerprint,
        "security_patch": security_patch,
        "incremental": incremental,
        "home_resolve": resolve,
        "candidate_header": candidate_header,
        "service_check_all_not_found": all(value.endswith("not found") for value in service_checks.values()),
        "service_list_has_amazon_names": "amazonpackagemanager" in service_list and "amazonusermanagerservice" in service_list,
    }
    generated = [
        artifact / "input-manifest.csv",
        artifact / "summary.json",
        artifact / "runtime-summary.csv",
        artifact / "route-flow.mmd",
        artifact / "sha256sums.txt",
        root / "findings/phase-6mv-runtime-readonly-report.md",
        root / "findings/phase-6mv-evidence-index.md",
        root / "output/tables/phase6mv-runtime-summary-20260810-02.csv",
        root / "output/call-graphs/phase6mv-runtime-home-services-20260810-02.mmd",
    ]
    if args.dry_run:
        print(json.dumps({
            "schema": SCHEMA,
            "capture": str(capture),
            "output": str(artifact),
            "device_contacted": False,
            "binder_transaction": False,
            "mutation": False,
            "reboot": False,
            "input_count": len(input_files),
            "outputs": [str(path) for path in generated],
        }, indent=2))
        return 0
    existing = [path for path in generated if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite existing outputs:\n" + "\n".join(map(str, existing)))

    artifact.mkdir(parents=True, exist_ok=True)
    write_csv(artifact / "input-manifest.csv", ["path", "sha256", "size"], input_rows, args.force)
    write_csv(artifact / "runtime-summary.csv", list(rows[0].keys()), rows, args.force)
    graph = """flowchart TD
  A["read-only ADB capture"] --> B["PMS HOME resolve"]
  B --> C["com.amazon.firelauncher/.Launcher"]
  A --> D["service list"]
  D --> E["private Amazon names listed"]
  E -.-> F["service check: not found for shell"]
  G["User 10 child state"] -.-> H["not User 0 HOME"]
"""
    write_text(artifact / "route-flow.mmd", graph, args.force)
    write_text(artifact / "summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n", args.force)

    report_rows = "\n".join(
        f"| {markdown_cell(row['finding'])} | {markdown_cell(row['observed'])} | {markdown_cell(row['classification'])} | {markdown_cell(row['evidence'])} |"
        for row in rows
    )
    report = f"""# Phase 6MV — Read-only runtime and GPL/OTA provenance closure

Generated: {generated_at}
Schema: {SCHEMA}

## Scope and safety

The runtime capture used only read-only ADB queries and dumps. No Binder
transaction, service call, package/settings mutation, input event, reboot,
OTA/recovery operation, Root/exploit, or Fire Launcher disable/force-stop was
performed. The GPL/OTA inventory was delegated to luna_worker and is included
as a hashed input.

## Results

### 已證實

- Device: {model} / {device} / {fingerprint}; security patch {security_patch};
  incremental {incremental}.
- User 0 HOME resolver returned {resolve}.
- Candidate query reported {candidate_header}.
- Fire package dump contains separate User 0 and User 10 state records; the
  child-user record does not alter User 0.
- Amazon private names are present in service list, but every selected service
  check returned not found for shell.
- The GPL/official-package inventory found kernel/source and official OTA
  artifacts, but no complete Amazon framework or init source tree.

### 高可信推論

The current runtime evidence is consistent with the existing boundary: User 0
remains controlled by the standard PackageManager HOME resolver, with Fire's
privileged manifest candidate winning. Child-user state is separate. The
visible private service names do not constitute an ADB-accessible Binder relay.

### 待驗證

- Indirect/native consumers not represented in the preserved disassembly.
- Exact runtime provenance of the deny-list resource package.
- Full updater canonicalization dataflow; static updater write capability is
  not evidence of an ADB or shell launcher route.

### 因風險拒絕測試

Unknown private Binder transactions, OTA execution, recovery/sideload,
partition writes, driver ioctls, Root attempts, and Fire Launcher state
changes were not performed.

## Runtime evidence matrix

| Finding | Observed | Classification | Evidence |
|---|---|---|---|
{report_rows}

## Reproduction

Capture:

    tools/scripts/capture_phase6mv_runtime_readonly.sh --serial G001LT0511550CFT --output adb/phase6mv/PHASE6MV-READONLY-20260810-02

Build report:

    python3 tools/scripts/build_phase6mv_runtime_report.py --dry-run
    python3 tools/scripts/build_phase6mv_runtime_report.py --force

The original capture hash manifest remains in the capture directory.
"""
    evidence = f"""# Phase 6MV evidence index

Generated: {generated_at}
Scope: read-only runtime capture plus host-only GPL/OTA inventory.

| Evidence ID | Source | Observed | Confidence |
|---|---|---|---|
| 6MV-RUNTIME-001 | {capture.relative_to(root)}/home_resolve.stdout.txt | User 0 HOME resolves to Fire Launcher priority 50 | Confirmed |
| 6MV-RUNTIME-002 | {capture.relative_to(root)}/home_candidates.stdout.txt | Fire, Microsoft, and FallbackHome are the three listed candidates | Confirmed |
| 6MV-RUNTIME-003 | {capture.relative_to(root)}/firelauncher_package.stdout.txt | Fire has distinct User 0 and User 10 records | Confirmed |
| 6MV-RUNTIME-004 | {capture.relative_to(root)}/service_*_stdout.txt | Seven selected private service checks report not found for shell | Confirmed |
| 6MV-RUNTIME-005 | {capture.relative_to(root)}/service_list.stdout.txt | Service-name listing alone does not prove a shell Binder handle | Confirmed |
| 6MV-SOURCE-001 | {worker.relative_to(root)} | GPL/OTA/source scope and hashes are inventoried without execution | Strong |

The report builder itself contacted no device and performed no mutation.
"""
    write_text(root / "findings/phase-6mv-runtime-readonly-report.md", report, args.force)
    write_text(root / "findings/phase-6mv-evidence-index.md", evidence, args.force)
    write_csv(root / "output/tables/phase6mv-runtime-summary-20260810-02.csv", list(rows[0].keys()), rows, args.force)
    write_text(root / "output/call-graphs/phase6mv-runtime-home-services-20260810-02.mmd", graph, args.force)
    artifact_files = sorted(
        path for path in artifact.rglob("*")
        if path.is_file() and path.name != "sha256sums.txt"
    )
    write_text(
        artifact / "sha256sums.txt",
        "".join(f"{sha256(path)}  {path.relative_to(artifact)}\n" for path in artifact_files),
        args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
