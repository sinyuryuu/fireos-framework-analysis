#!/usr/bin/env python3
"""Build the Phase 10 privilege-control closure bundle.

This script only normalizes saved host/device evidence. It never invokes ADB,
Binder, package/settings mutation, a driver, OTA/recovery, root, or exploit
code.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = [
    "evidence_id", "phase", "surface", "source", "caller", "gate",
    "identity_scope", "sink", "observed_effect", "confidence",
    "evidence_file", "evidence_sha256", "status", "scope",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def first(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = (row.get(name) or "").strip()
        if value:
            return value
    return ""


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def require(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))


def normalize_prior(path: Path, phase: str) -> list[dict[str, str]]:
    rows = []
    for row in read_csv(path):
        rows.append({
            "evidence_id": first(row, "evidence_id", "id"),
            "phase": first(row, "phase") or phase,
            "surface": first(row, "surface", "surface_family"),
            "source": first(row, "source", "source_csv"),
            "caller": first(row, "caller", "caller_or_publisher"),
            "gate": first(row, "gate", "permission_selinux_service_manager_gate"),
            "identity_scope": first(row, "identity_scope", "user_scope", "identity_policy_sink"),
            "sink": first(row, "sink", "sink_class", "operation"),
            "observed_effect": first(row, "observed_effect", "canonical_result", "result"),
            "confidence": first(row, "confidence") or "UNKNOWN",
            "evidence_file": first(row, "evidence_file", "evidence_location"),
            "evidence_sha256": first(row, "evidence_sha256", "provenance_sha256"),
            "status": first(row, "status", "integrated_status"),
            "scope": f"previous public Phase {phase} corpus",
        })
    return rows


def normalize_worker(path: Path, label: str, prefix: str) -> list[dict[str, str]]:
    rows = []
    for index, row in enumerate(read_csv(path), start=1):
        source = first(row, "evidence", "source")
        caller = first(row, "caller", "entry", "client")
        gate = first(row, "gate", "caller_gate", "permission")
        identity = first(row, "binder_identity", "identity", "identity_scope")
        user_scope = first(row, "user_scope", "scope")
        sink = first(row, "sink", "target")
        effect = first(row, "effect", "observed_effect")
        status = first(row, "status") or "UNKNOWN"
        evidence_hash = first(row, "evidence_sha256", "sha256") or sha256(path)
        missing = first(row, "missing_edge") or "UNKNOWN"
        rows.append({
            "evidence_id": f"P10-{prefix}-{index:03d}",
            "phase": "10",
            "surface": label,
            "source": source or rel(path),
            "caller": caller or "UNKNOWN",
            "gate": gate or "UNKNOWN",
            "identity_scope": "; ".join(x for x in [identity, user_scope] if x) or "UNKNOWN",
            "sink": sink or "UNKNOWN",
            "observed_effect": effect or "UNKNOWN",
            "confidence": status,
            "evidence_file": source or rel(path),
            "evidence_sha256": evidence_hash,
            "status": status,
            "scope": f"Phase 10 worker row {first(row, 'id') or index}; missing_edge={missing}",
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in HEADER} for row in rows)


def compact(value: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def write_index(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Phase 10 evidence index",
        "",
        "Phase 10 expands the privilege/control audit to package-management, policy/profile, OTA, and driver caller boundaries. Missing edges remain UNKNOWN; static capability is not a privilege-escalation claim.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['evidence_id']}",
            f"- Phase/surface: `{row['phase']}` / `{row['surface']}`",
            f"- Source: `{row['source'] or 'UNKNOWN'}`",
            f"- Evidence: `{row['evidence_file'] or 'UNKNOWN'}`",
            f"- SHA-256: `{row['evidence_sha256'] or 'UNKNOWN'}`",
            f"- Caller: {row['caller'] or 'UNKNOWN'}",
            f"- Gate: {row['gate'] or 'UNKNOWN'}",
            f"- Identity/user scope: {row['identity_scope'] or 'UNKNOWN'}",
            f"- Sink: {row['sink'] or 'UNKNOWN'}",
            f"- Effect: {row['observed_effect'] or 'UNKNOWN'}",
            f"- Confidence/status: **{row['confidence']}** / `{row['status'] or 'UNKNOWN'}`",
            f"- Scope: {row['scope']}",
            "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_graph(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "flowchart LR",
        "  classDef unknown fill:#fff3cd,stroke:#856404",
        "  classDef sink fill:#d1ecf1,stroke:#0c5460",
    ]
    seen: set[str] = set()
    for row in rows:
        parts = [row["caller"], row["gate"], row["identity_scope"], row["sink"]]
        parts = [compact(part, 90) or "UNKNOWN" for part in parts]
        ids = []
        for part in parts:
            node_id = "N" + hashlib.sha1(part.encode()).hexdigest()[:10]
            ids.append(node_id)
            if node_id not in seen:
                lines.append(f'  {node_id}["{part.replace(chr(34), chr(39))}"]')
                seen.add(node_id)
        for left, right in zip(ids, ids[1:]):
            lines.append(f"  {left} -->|{row['evidence_id']}| {right}")
        lines.append(f"  {ids[-1]}:::{'unknown' if parts[-1] == 'UNKNOWN' else 'sink'}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(path: Path, rows: list[dict[str, str]], baseline: Path) -> None:
    new_rows = [row for row in rows if row["phase"] == "10"]
    counts: dict[str, int] = {}
    for row in new_rows:
        counts[row["surface"]] = counts.get(row["surface"], 0) + 1
    lines = [
        "# Phase 10 — broad privilege-control closure",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Safety",
        "",
        "Worker analyses are host-only. The only device activity in this phase was a serial-bound read-only baseline: no Binder transaction, package/settings mutation, driver open/ioctl, OTA/recovery execution, reboot, root, exploit, or partition write.",
        "",
        "Acceptance rule: `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges remain UNKNOWN.",
        "",
        f"Combined ledger rows: **{len(rows)}**; unique IDs: **{len({row['evidence_id'] for row in rows})}**. New Phase 10 rows: **{len(new_rows)}**.",
        "",
        "| New surface | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {surface} | {count} |" for surface, count in sorted(counts.items()))
    lines += [
        "",
        "## Current device baseline",
        "",
        f"Raw capture: `{baseline}`. The saved PS7331 fingerprint is `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`; SELinux is Enforcing; current user is 0; User 0 HOME resolves to `com.amazon.firelauncher/.Launcher` at priority 50. The capture manifest is independently hash-verified.",
        "",
        "## Findings",
        "",
        "- AmazonPackageManager metadata mutators retain a signature-level `ADD_RM_PKG_METADATA` gate and no joined ordinary caller. KFT package-state writers remain child/profile scoped through `UserInfo.id`; no User-0 writer was found.",
        "- DevicePolicy/Profile and remaining system-service paths must be read as trusted lifecycle or policy surfaces until their external caller, owner/admin gate, and target-user join is recovered. A missing method-local UID check alone is not a usable route.",
        "- OTA/update-binary artifacts expose privileged recovery-time sinks, but the fixed release OTA, verifier handoff, product/version gates, and absent external recovery caller do not establish an untrusted arbitrary-write path. Malformed/symlink/OTA execution was not performed.",
        "- Driver candidates remain UNKNOWN unless the final node, mode/SELinux policy, shipped native caller, input boundary, and sensitive effect all join. No device node was opened.",
        "",
        "## Verdict",
        "",
        "Phase 10 adds evidence across non-Launcher privilege surfaces but does not establish a reproducible ordinary-App or shell path to disable Fire Launcher, replace User-0 HOME, obtain UID 0, or write a protected partition. Existing rootless foreground redirect behavior remains the closest workaround; it is not formal HOME replacement.",
        "",
        "## Reproduction",
        "",
        "Run `python3 tools/scripts/build_phase10_surface.py --dry-run` and then `--force` after all four worker CSVs are present. No device is required for the host-side bundle.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    files = [
        ROOT / "output/tables/phase9-control-surface.csv",
        ROOT / "work/luna_worker_phase10a_package_manager_closure_20260810.csv",
        ROOT / "work/luna_worker_phase10b_dpm_profile_closure_20260810.csv",
        ROOT / "work/luna_worker_phase10c_ota_postinstall_closure_20260810.csv",
        ROOT / "work/luna_worker_phase10d_driver_caller_closure_20260810.csv",
        ROOT / "work/luna_worker_phase10a_package_manager_closure_20260810.md",
        ROOT / "work/luna_worker_phase10b_dpm_profile_closure_20260810.md",
        ROOT / "findings/phase-10c-ota-postinstall-summary.md",
        ROOT / "work/luna_worker_phase10c_ota_postinstall_closure_20260810.md",
        ROOT / "work/luna_worker_phase10d_driver_caller_closure_20260810.md",
        ROOT / "adb/phase10/PHASE10-BASELINE-20260810-01/sha256sums.txt",
        ROOT / "findings/phase-10-readonly-baseline.md",
    ]
    require(files)
    outputs = [
        ROOT / "findings/phase-10-report.md",
        ROOT / "findings/phase-10-evidence-index.md",
        ROOT / "output/tables/phase10-control-surface.csv",
        ROOT / "output/tables/phase10-input-manifest.sha256",
        ROOT / "output/call-graphs/phase10-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase10-control-surfaces.md",
    ]
    if args.dry_run:
        print(f"inputs verified ({len(files)} files); Phase 10 outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))
    rows = normalize_prior(files[0], "9")
    rows.extend(normalize_worker(files[1], "AmazonPackageManager/package-state closure", "APM"))
    rows.extend(normalize_worker(files[2], "DevicePolicy/Profile IPC closure", "DPM"))
    rows.extend(normalize_worker(files[3], "OTA post-install/update closure", "OTA"))
    rows.extend(normalize_worker(files[4], "MTK/Amazon driver caller closure", "DRV"))
    ids = [row["evidence_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate evidence IDs")
    write_csv(ROOT / "output/tables/phase10-control-surface.csv", rows)
    write_index(ROOT / "findings/phase-10-evidence-index.md", rows)
    write_report(ROOT / "findings/phase-10-report.md", rows, files[-1])
    graph = ROOT / "output/call-graphs/phase10-control-surfaces.mmd"
    write_graph(graph, rows)
    (ROOT / "output/call-graphs/phase10-control-surfaces.md").write_text(
        "# Phase 10 control surfaces\n\n```mermaid\n" + graph.read_text(encoding="utf-8") + "```\n",
        encoding="utf-8",
    )
    (ROOT / "output/tables/phase10-input-manifest.sha256").write_text(
        "\n".join(f"{sha256(path)}  {rel(path)}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(f"generated {len(rows)} rows; {len(set(ids))} unique IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
