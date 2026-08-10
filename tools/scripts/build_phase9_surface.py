#!/usr/bin/env python3
"""Build the Phase 9 broad privilege-route closure bundle.

Host-only evidence normalizer.  It does not access a device, invoke Binder,
open a driver, execute OTA/recovery code, or mutate any artifact.
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


def first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def require(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))


def normalize_prior(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(path):
        rows.append({
            "evidence_id": first(row, "evidence_id", "id"),
            "phase": first(row, "phase") or "8",
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
            "scope": "previous public Phase 8 corpus",
        })
    return rows


def base_row(evidence_id: str, surface: str, source: str, caller: str,
             gate: str, identity: str, sink: str, effect: str,
             status: str, evidence: str, evidence_hash: str,
             scope: str) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "phase": "9",
        "surface": surface,
        "source": source or "UNKNOWN",
        "caller": caller or "UNKNOWN",
        "gate": gate or "UNKNOWN",
        "identity_scope": identity or "UNKNOWN",
        "sink": sink or "UNKNOWN",
        "observed_effect": effect or "UNKNOWN",
        "confidence": status or "UNKNOWN",
        "evidence_file": evidence or "UNKNOWN",
        "evidence_sha256": evidence_hash or "UNKNOWN",
        "status": status or "UNKNOWN",
        "scope": scope,
    }


def normalize_9a(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(path), start=1):
        edge = first(row, "edge") or f"row-{index}"
        exact = first(row, "exact_value")
        status = first(row, "status") or "UNKNOWN"
        source = first(row, "evidence")
        notes = first(row, "notes")
        caller = exact if edge in {"caller", "production_uid"} else ""
        gate = exact if edge in {"app_prewarm_manifest_request", "app_prewarm_effective_grant", "method_gate", "selinux_service_gate"} else ""
        identity = exact if edge == "identity" else ""
        scope = exact if edge == "user_scope" else ""
        sink = exact if edge == "sink" else ""
        effect = exact if edge == "effect" else ""
        rows.append(base_row(
            f"P9-PREWARM-{index:03d}",
            "prewarm caller/grant closure",
            source,
            caller,
            gate,
            "; ".join(x for x in [identity, scope] if x),
            sink,
            effect,
            status,
            source,
            first(row, "sha256"),
            f"Phase 9A worker edge={edge}; notes={notes or 'UNKNOWN'}",
        ))
    return rows


def normalize_generic(path: Path, surface: str, prefix: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(path), start=1):
        rows.append(base_row(
            f"P9-{prefix}-{index:03d}",
            surface,
            first(row, "evidence", "source"),
            first(row, "caller", "entry"),
            first(row, "gate", "caller_gate"),
            first(row, "binder_identity", "identity", "identity_scope", "user_scope"),
            first(row, "sink", "target"),
            first(row, "effect", "observed_effect"),
            first(row, "status") or "UNKNOWN",
            first(row, "evidence", "source"),
            first(row, "evidence_sha256", "sha256") or sha256(path),
            "; ".join(x for x in [
                f"worker_row={first(row, 'id') or index}",
                f"missing_edge={first(row, 'missing_edge') or 'UNKNOWN'}",
            ]),
        ))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in HEADER} for row in rows)


def compact(value: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def write_index(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Phase 9 evidence index",
        "",
        "Phase 9 broadens the permission/control audit beyond Launcher. Missing caller, gate, identity, user-scope, sink, and observed-effect edges remain UNKNOWN. No row is a privilege-escalation claim by itself.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['evidence_id']}",
            f"- Surface: `{row['surface']}`",
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
    new_rows = [row for row in rows if row["phase"] == "9"]
    counts: dict[str, int] = {}
    for row in new_rows:
        counts[row["surface"]] = counts.get(row["surface"], 0) + 1
    lines = [
        "# Phase 9 — broad privilege-route closure",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Safety",
        "",
        "All Phase 9 worker analyses are host-only. No device command, private Binder/service transaction, package/settings mutation, driver open/ioctl, OTA/recovery execution, reboot, root attempt, exploit payload, or partition write was performed.",
        "",
        "The acceptance rule remains `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges are preserved as UNKNOWN.",
        "",
        f"Combined ledger rows: **{len(rows)}**; unique IDs: **{len({row['evidence_id'] for row in rows})}**. New Phase 9 rows: **{len(new_rows)}**.",
        "",
        "| New surface | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {surface} | {count} |" for surface, count in sorted(counts.items()))
    lines += [
        "",
        "## Concrete results",
        "",
        "- **Prewarm:** Alexa is joined to a saved UID/grant snapshot and the sink is `startProcessLocked(..., \"prewarm\", ...)`; this is process/resource prewarm, not a package-state, HOME, UID-0, or permission-grant sink. User mapping and complete caller universe remain UNKNOWN.",
        "- **KFT tx3:** the recovered semantic caller is `AmazonUserManagerImpl.createChildUser()`. The `frameworksettings` and `h2settingsfortablet` packages are candidates based on privileges, not confirmed tx3 callers. The local upgrade `onBootPhase` path is separate from external Binder tx3, and writer scope follows `UserInfo.id` rather than User 0.",
        "- **Residual IPC:** exported/system-facing DCPMS or profile/package-management surfaces remain bounded UNKNOWN when the production client, service-manager gate, or downstream privileged sink is missing. Exported AIDL, a permission declaration, or a missing method-local UID check is not promoted to a usable shell/app route.",
        "- **Broad surfaces:** every new non-Launcher candidate is retained with its exact missing edge; no new route closes to Fire User-0 state, formal HOME, UID 0, or partition write.",
        "",
        "## Verdict",
        "",
        "This phase expands the search to any permission/control path that could theoretically change package state, users, settings, policy, update state, or privileged device behavior. It finds no new reproducible low-privilege privilege transition. The next evidence must be offline artifact completion or a documented, authorized API contract—not unknown Binder codes, driver ioctls, malformed OTA data, or root tooling.",
        "",
        "## Reproduction",
        "",
        "Run `python3 tools/scripts/build_phase9_surface.py --dry-run` to verify inputs, then `--force` to regenerate the host-only bundle. No device is required.",
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
        ROOT / "output/tables/phase8-control-surface.csv",
        ROOT / "work/luna_worker_phase9a_prewarm_grant_20260810.csv",
        ROOT / "work/luna_worker_phase9b_kft_client_identity_20260810.csv",
        ROOT / "work/luna_worker_phase9c_residual_ipc_20260810.csv",
        ROOT / "work/luna_worker_phase9d_broad_surface_triage_20260810.csv",
        ROOT / "work/luna_worker_phase9a_prewarm_grant_20260810.md",
        ROOT / "work/luna_worker_phase9b_kft_client_identity_20260810.md",
        ROOT / "work/luna_worker_phase9c_residual_ipc_20260810.md",
        ROOT / "work/luna_worker_phase9d_broad_surface_triage_20260810.md",
        ROOT / "findings/phase-8-report.md",
    ]
    require(files)
    outputs = [
        ROOT / "findings/phase-9-report.md",
        ROOT / "findings/phase-9-evidence-index.md",
        ROOT / "output/tables/phase9-control-surface.csv",
        ROOT / "output/tables/phase9-input-manifest.sha256",
        ROOT / "output/call-graphs/phase9-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase9-control-surfaces.md",
    ]
    if args.dry_run:
        print(f"inputs verified ({len(files)} files); Phase 9 outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))
    rows = normalize_prior(files[0])
    rows.extend(normalize_9a(files[1]))
    rows.extend(normalize_generic(files[2], "KFT tx3 caller identity closure", "KFT"))
    rows.extend(normalize_generic(files[3], "residual IPC privilege-sink closure", "IPC"))
    rows.extend(normalize_generic(files[4], "broad non-Launcher privilege surfaces", "BROAD"))
    ids = [row["evidence_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate evidence IDs")
    write_csv(ROOT / "output/tables/phase9-control-surface.csv", rows)
    write_index(ROOT / "findings/phase-9-evidence-index.md", rows)
    write_report(ROOT / "findings/phase-9-report.md", rows, files)
    graph = ROOT / "output/call-graphs/phase9-control-surfaces.mmd"
    write_graph(graph, rows)
    (ROOT / "output/call-graphs/phase9-control-surfaces.md").write_text(
        "# Phase 9 control surfaces\n\n```mermaid\n" + graph.read_text(encoding="utf-8") + "```\n",
        encoding="utf-8",
    )
    manifest = ROOT / "output/tables/phase9-input-manifest.sha256"
    manifest.write_text("\n".join(f"{sha256(path)}  {rel(path)}" for path in files) + "\n", encoding="utf-8")
    print(f"generated {len(rows)} rows; {len(set(ids))} unique IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
