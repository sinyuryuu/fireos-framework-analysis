#!/usr/bin/env python3
"""Build the Phase 6X2 broad, host-only privilege-surface evidence bundle.

This generator deliberately treats worker CSVs as evidence tables, not as
proof of reachability.  It preserves the required chain:
caller -> gate -> identity/user scope -> sink -> observed effect.
It never contacts a device and never executes artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CONTROL_HEADER = [
    "evidence_id",
    "phase",
    "surface",
    "source",
    "caller",
    "gate",
    "identity_scope",
    "sink",
    "observed_effect",
    "confidence",
    "evidence_file",
    "evidence_sha256",
    "status",
    "scope",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def require(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))


def value(row: dict[str, str], *names: str) -> str:
    for name in names:
        if row.get(name):
            return row[name].strip()
    return ""


def normalise_worker(path: Path, tag: str) -> list[dict[str, str]]:
    rows = read_csv(path)
    output: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        evidence_id = value(row, "evidence_id", "id", "finding_id")
        if not evidence_id:
            evidence_id = f"6X2-{tag}-{index:03d}"
        source = value(row, "source", "source_file", "definition_or_component", "component_or_key", "caller_or_component", "stage", "scope")
        evidence_file = value(row, "evidence_file", "evidence_location", "evidence", "evidence_path_and_location", "file", "artifact")
        evidence_sha = value(row, "evidence_sha256", "sha256", "provenance_sha256")
        if not evidence_file:
            evidence_file = rel(path)
        if not evidence_sha:
            evidence_sha = digest(path)
        output.append({
            "evidence_id": evidence_id,
        "phase": "6X2",
            "surface": value(row, "surface", "surface_family", "route", "category") or tag,
            "source": source,
            "caller": value(row, "caller", "caller_or_publisher", "caller_identity", "caller_or_component", "caller_or_sender"),
            "gate": value(row, "gate", "permission", "permission_selinux_service_manager_gate", "authorization", "permission_protection", "operation_or_gate"),
            "identity_scope": value(row, "identity_scope", "user_scope", "identity", "scope"),
            "sink": value(row, "sink", "sink_class", "operation", "node_or_api", "target"),
            "observed_effect": value(row, "observed_effect", "result", "canonical_result", "finding", "interpretation", "positive_or_negative", "notes", "reachability"),
            "confidence": value(row, "confidence", "status_confidence") or "UNKNOWN",
            "evidence_file": evidence_file,
            "evidence_sha256": evidence_sha,
            "status": value(row, "status", "classification", "disposition") or "HOST_ONLY",
            "scope": f"new Phase 6X2 {tag} worker evidence",
        })
    return output


def normalise_prior(path: Path) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in read_csv(path):
        output.append({
            "evidence_id": value(row, "evidence_id", "id"),
            "phase": value(row, "phase") or "6X",
            "surface": value(row, "surface", "surface_family"),
            "source": value(row, "source", "source_csv"),
            "caller": value(row, "caller", "caller_or_publisher"),
            "gate": value(row, "gate", "permission_selinux_service_manager_gate"),
            "identity_scope": value(row, "identity_scope", "user_scope", "identity_policy_sink"),
            "sink": value(row, "sink", "sink_class", "operation"),
            "observed_effect": value(row, "observed_effect", "canonical_result", "result"),
            "confidence": value(row, "confidence") or "UNKNOWN",
            "evidence_file": value(row, "evidence_file", "evidence_location"),
            "evidence_sha256": value(row, "evidence_sha256", "provenance_sha256"),
            "status": value(row, "status", "integrated_status"),
            "scope": "previous public Phase 6X corpus",
        })
    return output


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_csv(path: Path, rows: list[dict[str, str]], header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in header} for row in rows)


def safe_text(text: str, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def write_report(path: Path, rows: list[dict[str, str]], inputs: list[Path]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["surface"]] = counts.get(row["surface"], 0) + 1
    snapshot_files = [item for item in inputs if str(item).startswith(str(ROOT / "adb"))]
    lines = [
        "# Phase 6X2 — broad privilege surface continuation",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope and safety",
        "",
        "This is a host-only synthesis of the prior public Phase 6X ledger and four disjoint residual audits. It does not contact a device, execute an OTA, call a private Binder transaction, open a driver node, run an exploit, mutate Fire Launcher, reboot, or write a partition.",
        "",
        "The acceptance rule remains `caller → gate → identity/user scope → exact sink → observed effect`. A capability, declaration, exported component, or source-level writer without that chain is not an elevation finding.",
        "",
        "## Evidence inventory",
        "",
        f"- Combined rows: **{len(rows)}** (including the prior Phase 6X corpus).",
        "- New worker inputs: " + ", ".join(f"`{rel(path)}`" for path in inputs if "phase6x-control" not in path.name),
        "- Prior corpus: `output/tables/phase6x-control-surface.csv`.",
        "- Fresh exact-serial read-only capture: " + (f"`{rel(snapshot_files[0].parent)}`" if snapshot_files else "NONE"),
        "",
        "| Surface | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {surface} | {count} |" for surface, count in sorted(counts.items()))
    lines.extend([
        "",
        "## Classification rules",
        "",
        "- **已證實** is reserved for a directly observed, reproducible effect or a complete static authorization/sink chain.",
        "- **高可信推論** means the static path is coherent but a required runtime edge remains open.",
        "- **待驗證** records a missing caller, publication, SELinux/service-manager rule, numeric user scope, or downstream writer.",
        "- **已排除** records a negative result within a stated bounded search; it is not a universal absence claim.",
        "- **因風險拒絕測試** covers OTA/recovery execution, unknown Binder payloads, driver ioctls, exploit attempts, and destructive package/partition operations.",
        "",
        "## New residual audit summary",
        "",
    ])
    for row in rows:
        if row["scope"].startswith("new Phase 6X2"):
            lines.append(f"- `{row['evidence_id']}` — **{row['surface']}** — {safe_text(row['observed_effect']) or safe_text(row['status'])} ({row['confidence']}).")
    lines.extend([
        "",
        "## Main conclusion",
        "",
        "The broad search remains useful only when it closes a real caller-to-sink chain. On the current evidence, no new ordinary app/shell path has demonstrated User-0 package-state mutation, formal HOME replacement, root identity, or partition effect. Any residual row with UNKNOWN caller/publication/identity/sink must remain a research lead rather than a bypass claim.",
        "",
        "The new exact-serial capture records `mutation=false`, `binder_transaction=false`, and `reboot=false`; it is a fresh observation only, not a new mutation experiment.",
        "",
        "## Reproduction",
        "",
        "All inputs and hashes are listed in `output/tables/phase6x2-input-manifest.sha256`. The generator is host-only and supports `--dry-run`; it refuses to overwrite outputs unless `--force` is supplied.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_index(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Phase 6X2 evidence index",
        "",
        "Each row below is normalized from a preserved CSV. Empty caller/gate/identity/sink fields are intentional UNKNOWNs; they are not inferred.",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['evidence_id']}",
            f"- Source: `{row['source'] or 'UNKNOWN'}`",
            f"- Evidence file: `{row['evidence_file'] or 'UNKNOWN'}`",
            f"- SHA-256: `{row['evidence_sha256'] or 'UNKNOWN'}`",
            f"- Caller: {row['caller'] or 'UNKNOWN'}",
            f"- Gate: {row['gate'] or 'UNKNOWN'}",
            f"- Identity/user scope: {row['identity_scope'] or 'UNKNOWN'}",
            f"- Sink: {row['sink'] or 'UNKNOWN'}",
            f"- Observed effect: {row['observed_effect'] or 'UNKNOWN'}",
            f"- Confidence: **{row['confidence']}**",
            f"- Status: `{row['status'] or 'UNKNOWN'}`",
            "",
        ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_graph(path: Path, rows: list[dict[str, str]]) -> None:
    lines = ["flowchart LR", "  classDef unknown fill:#fff3cd,stroke:#856404", "  classDef sink fill:#d1ecf1,stroke:#0c5460"]
    seen: set[str] = set()
    edge_index = 0
    for row in rows:
        parts = [row["caller"], row["gate"], row["identity_scope"], row["sink"]]
        parts = [safe_text(part, 80) or "UNKNOWN" for part in parts]
        ids = []
        for part in parts:
            node_id = "N" + hashlib.sha1(part.encode()).hexdigest()[:10]
            ids.append(node_id)
            if node_id not in seen:
                label = part.replace('"', "'")
                lines.append(f'  {node_id}["{label}"]')
                seen.add(node_id)
        for left, right in zip(ids, ids[1:]):
            edge_index += 1
            lines.append(f"  {left} -->|{row['evidence_id']}| {right}")
        if parts[-1] == "UNKNOWN":
            lines.append(f"  {ids[-1]}:::unknown")
        else:
            lines.append(f"  {ids[-1]}:::sink")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    snapshot = ROOT / "adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01"
    inputs = [
        ROOT / "output/tables/phase6x-control-surface.csv",
        ROOT / "work/luna_worker_phase6aa_ipc_residual_20260810.csv",
        ROOT / "work/luna_worker_phase6ab_ota_exact_20260810.csv",
        ROOT / "work/luna_worker_phase6ac_accessibility_review_20260810.csv",
        ROOT / "work/luna_worker_phase6ad_untested_routes_20260810.csv",
        ROOT / "work/luna_worker_phase6aa_ipc_residual_20260810.md",
        ROOT / "work/luna_worker_phase6ab_ota_exact_20260810.md",
        ROOT / "work/luna_worker_phase6ac_accessibility_review_20260810.md",
        ROOT / "work/luna_worker_phase6ad_untested_routes_20260810.md",
        snapshot / "metadata.txt",
        snapshot / "getprop.stdout.txt",
        snapshot / "home_resolve.stdout.txt",
        snapshot / "home_candidates.stdout.txt",
        snapshot / "preferred_xml.stdout.txt",
        snapshot / "firelauncher_package.stdout.txt",
        snapshot / "sha256sums.txt",
    ]
    require(inputs)
    outputs = [
        ROOT / "findings/phase-6x2-report.md",
        ROOT / "findings/phase-6x2-evidence-index.md",
        ROOT / "output/tables/phase6x2-control-surface.csv",
        ROOT / "output/tables/phase6x2-input-manifest.sha256",
        ROOT / "output/call-graphs/phase6x2-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase6x2-control-surfaces.md",
    ]
    if args.dry_run:
        print("inputs verified; host-only outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))

    rows = normalise_prior(inputs[0])
    for path, tag in zip(inputs[1:5], ["IPC", "OTA", "ACCESS", "ROUTES"]):
        rows.extend(normalise_worker(path, tag))
    write_csv(ROOT / "output/tables/phase6x2-control-surface.csv", rows, CONTROL_HEADER)
    write_report(ROOT / "findings/phase-6x2-report.md", rows, inputs)
    write_index(ROOT / "findings/phase-6x2-evidence-index.md", rows)
    write_graph(ROOT / "output/call-graphs/phase6x2-control-surfaces.mmd", rows)
    graph_md = ROOT / "output/call-graphs/phase6x2-control-surfaces.md"
    graph_md.write_text("# Phase 6X2 control surfaces\n\n```mermaid\n" + (ROOT / "output/call-graphs/phase6x2-control-surfaces.mmd").read_text(encoding="utf-8") + "```\n", encoding="utf-8")
    manifest = ROOT / "output/tables/phase6x2-input-manifest.sha256"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(f"{digest(path)}  {rel(path)}" for path in inputs) + "\n", encoding="utf-8")
    print(f"generated {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
