#!/usr/bin/env python3
"""Build the Phase 6X3 broad privilege-surface evidence bundle.

Host-only.  The generator normalizes four disjoint worker outputs on top of
the public Phase 6X2 ledger.  It never contacts a device or executes any
artifact.
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
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def require(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))


def first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def normalize_prior(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(path):
        rows.append({
            "evidence_id": first(row, "evidence_id", "id"),
            "phase": first(row, "phase") or "6X2",
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
            "scope": "previous public Phase 6X2 corpus",
        })
    return rows


def normalize_worker(path: Path, kind: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(path), start=1):
        evidence_id = first(row, "id", "evidence_id", "row_id", "route_id")
        if not evidence_id:
            evidence_id = f"6X3-{kind}-{index:03d}"

        if kind == "IPC":
            surface = first(row, "category") or "IPC"
            source = first(row, "evidence_file_method_line_or_offset")
            caller = first(row, "caller_to_sink")
            gate = first(row, "permission_or_gate")
            identity = "; ".join(x for x in [first(row, "binder_identity"), first(row, "user_scope")] if x)
            sink = first(row, "exact_sink")
            effect = first(row, "observed_effect")
            confidence = first(row, "classification") or "UNKNOWN"
            status = first(row, "classification") or "HOST_ONLY"
        elif kind == "OTA":
            surface = first(row, "stage") or "OTA"
            source = first(row, "evidence_file_offset")
            caller = first(row, "caller_identity_gate")
            gate = first(row, "caller_identity_gate")
            identity = "UNKNOWN"
            sink = first(row, "provenance_or_sink")
            effect = first(row, "indirect_edge_or_error_branch")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
        elif kind == "DRIVER":
            surface = first(row, "surface") or "kernel/driver"
            source = first(row, "evidence")
            caller = first(row, "caller_reachability")
            gate = first(row, "permission_identity")
            identity = first(row, "permission_identity") or "UNKNOWN"
            sink = first(row, "security_effect")
            effect = first(row, "source_capability", "shipped_artifact")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
        else:
            surface = first(row, "category") or "legacy route"
            source = first(row, "evidence")
            caller = first(row, "scope_or_identity")
            gate = "; ".join(x for x in [first(row, "disposition"), first(row, "risk_boundary")] if x)
            identity = first(row, "scope_or_identity")
            sink = first(row, "route_family")
            effect = first(row, "evidence_success_rate", "true_permission_change")
            confidence = first(row, "disposition") or "UNKNOWN"
            status = first(row, "disposition") or "HOST_ONLY"

        evidence_file = source or rel(path)
        evidence_hash = first(row, "evidence_sha256", "sha256") or sha256(path)
        output.append({
            "evidence_id": evidence_id,
            "phase": "6X3",
            "surface": surface,
            "source": source or rel(path),
            "caller": caller,
            "gate": gate,
            "identity_scope": identity,
            "sink": sink,
            "observed_effect": effect,
            "confidence": confidence,
            "evidence_file": evidence_file,
            "evidence_sha256": evidence_hash,
            "status": status,
            "scope": f"new Phase 6X3 {kind} worker evidence",
        })
    return output


def compact(value: str, limit: int = 190) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in HEADER} for row in rows)


def write_index(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Phase 6X3 evidence index",
        "",
        "The index retains unknown caller, gate, identity, user-scope, and sink edges as UNKNOWN. Static capability is not treated as a privilege transition.",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['evidence_id']}",
            f"- Phase/surface: `{row['phase']}` / `{row['surface']}`",
            f"- Source: `{row['source'] or 'UNKNOWN'}`",
            f"- Evidence file: `{row['evidence_file'] or 'UNKNOWN'}`",
            f"- SHA-256: `{row['evidence_sha256'] or 'UNKNOWN'}`",
            f"- Caller: {row['caller'] or 'UNKNOWN'}",
            f"- Gate: {row['gate'] or 'UNKNOWN'}",
            f"- Identity/user scope: {row['identity_scope'] or 'UNKNOWN'}",
            f"- Sink: {row['sink'] or 'UNKNOWN'}",
            f"- Effect: {row['observed_effect'] or 'UNKNOWN'}",
            f"- Confidence: **{row['confidence']}**; status `{row['status'] or 'UNKNOWN'}`",
            "",
        ])
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
        ids: list[str] = []
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


def write_report(path: Path, rows: list[dict[str, str]], inputs: list[Path]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["phase"]] = counts.get(row["phase"], 0) + 1
    new_rows = [row for row in rows if row["phase"] == "6X3"]
    lines = [
        "# Phase 6X3 — broad privilege route continuation",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope and safety",
        "",
        "This phase adds four disjoint host-only audits to the public Phase 6X2 ledger. The four delegated audits performed no device command, private Binder transaction, driver open/ioctl, OTA/recovery execution, exploit/root attempt, package mutation, reboot, remount, or partition write.",
        "",
        "The acceptance rule is still `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges are retained as UNKNOWN; they do not become a vulnerability claim.",
        "",
        "## Evidence counts",
        "",
        f"- Combined ledger rows: **{len(rows)}**; unique IDs: **{len({row['evidence_id'] for row in rows})}**.",
        f"- Prior Phase 6X2 rows: **{len(rows) - len(new_rows)}**.",
        f"- New Phase 6X3 rows: **{len(new_rows)}**.",
        "- Input manifest: `output/tables/phase6x3-input-manifest.sha256`.",
        "",
        "| Phase | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {phase} | {count} |" for phase, count in sorted(counts.items()))
    lines.extend([
        "",
        "## New audit conclusions",
        "",
        "- **IPC residuals — 待驗證/高可信靜態邊界:** eight deduplicated routes retain lifecycle, profile-policy, prewarm, permission-declaration, and OTA staging sinks, but no new ordinary caller-to-User-0 package/HOME/root chain.",
        "- **OTA verifier — 因風險拒絕 runtime:** date/product checks, cache error branches, indirect dispatch, canonicalization markers, and named-writer argument provenance are more precisely mapped; this is not evidence of signature, AVB, rollback, symlink, or shell bypass.",
        "- **Kernel/driver — capability/provenance gap:** eleven rows cover Amazon/MediaTek debug, performance, AUXADC, PMIC, touchscreen, power-supply, uinput, and CMDQ/ION surfaces. Exact shipped object, node policy, caller UID/domain, and package/HOME/root effect remain unjoined.",
        "- **Legacy routes — 已排除/待驗證:** 29 route families confirm that User 0 formal HOME remains Fire; User 10/11 child state and consented foreground assist are scoped alternatives, not a privilege transition.",
        "",
        "## Main verdict",
        "",
        "No new evidence closes a low-privilege path to User-0 package-state mutation, formal HOME replacement, UID 0, or partition writing. The most useful remaining work is host-only closure of exact service publication/SELinux joins and the six route gaps already identified in Phase 6X2; running risky payloads would not repair the missing provenance and is therefore rejected.",
        "",
        "A separate post-synthesis serial-bound read-only check is recorded in `findings/phase-6x3-readonly-check.md`: User 0 still resolves Fire Launcher at priority 50, with Microsoft at 0 and FallbackHome at -1000; Fire's saved User 0 state remains enabled. The check did not mutate package/settings state, call Binder transactions, reboot, or access a driver.",
        "",
        "## Explicitly not claimed",
        "",
        "This report does not claim that every driver or updater path is safe, that every permission is correctly protected, or that no future vulnerability exists. It records only the evidence that was actually joined and the minimum missing edge for each route.",
        "",
        "## Reproduction",
        "",
        "Use `python3 tools/scripts/build_phase6x3_surface.py --dry-run` to verify inputs, then `--force` to regenerate the host-only outputs. Raw worker CSV/Markdown files are included as separate evidence inputs.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    files = [
        ROOT / "output/tables/phase6x2-control-surface.csv",
        ROOT / "work/luna_worker_phase6ae_ipc_sink_sweep_20260810.csv",
        ROOT / "work/luna_worker_phase6af_ota_verifier_gap_20260810.csv",
        ROOT / "work/luna_worker_phase6ag_driver_source_gap_20260810.csv",
        ROOT / "work/luna_worker_phase6ah_legacy_route_reconciliation_20260810.csv",
        ROOT / "work/luna_worker_phase6ae_ipc_sink_sweep_20260810.md",
        ROOT / "work/luna_worker_phase6af_ota_verifier_gap_20260810.md",
        ROOT / "work/luna_worker_phase6ag_driver_source_gap_20260810.md",
        ROOT / "work/luna_worker_phase6ah_legacy_route_reconciliation_20260810.md",
        ROOT / "findings/phase-6x3-readonly-check.md",
    ]
    require(files)
    outputs = [
        ROOT / "findings/phase-6x3-report.md",
        ROOT / "findings/phase-6x3-evidence-index.md",
        ROOT / "output/tables/phase6x3-control-surface.csv",
        ROOT / "output/tables/phase6x3-input-manifest.sha256",
        ROOT / "output/call-graphs/phase6x3-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase6x3-control-surfaces.md",
    ]
    if args.dry_run:
        print("inputs verified; Phase 6X3 host-only outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))

    rows = normalize_prior(files[0])
    for path, kind in zip(files[1:5], ["IPC", "OTA", "DRIVER", "ROUTES"]):
        rows.extend(normalize_worker(path, kind))
    write_csv(ROOT / "output/tables/phase6x3-control-surface.csv", rows)
    write_index(ROOT / "findings/phase-6x3-evidence-index.md", rows)
    write_report(ROOT / "findings/phase-6x3-report.md", rows, files)
    graph = ROOT / "output/call-graphs/phase6x3-control-surfaces.mmd"
    write_graph(graph, rows)
    (ROOT / "output/call-graphs/phase6x3-control-surfaces.md").write_text(
        "# Phase 6X3 control surfaces\n\n```mermaid\n" + graph.read_text(encoding="utf-8") + "```\n",
        encoding="utf-8",
    )
    manifest = ROOT / "output/tables/phase6x3-input-manifest.sha256"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(f"{sha256(path)}  {rel(path)}" for path in files) + "\n", encoding="utf-8")
    print(f"generated {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
