#!/usr/bin/env python3
"""Build the Phase 6X4 privilege-surface closure bundle.

Host-only.  This generator adds four bounded closure audits to the public
Phase 6X3 ledger.  It never contacts a device, calls Binder, opens a driver,
executes an updater, or mutates repository evidence.

The worker identifiers are retained in the normalized ``scope`` field, while
the public ledger receives fresh Phase 6X4 IDs so duplicated historical route
IDs cannot be mistaken for new evidence.
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


PERMISSION_HEADER = [
    "row_id", "baseline", "permission", "artifact_role", "requester",
    "uses_permission", "holder_grant", "exported_component_service",
    "method_local_check", "binder_identity", "user_scope",
    "downstream_sensitive_sink", "status", "evidence_path",
    "evidence_sha256", "line", "notes",
]


def read_permission_csv(path: Path) -> list[dict[str, str]]:
    """Read the worker CSV while explicitly recording its malformed rows.

    The raw worker file is preserved as an input.  Rows 6AK-009 and 6AK-011
    have one extra unquoted comma; 6AK-010 has three fewer fields than the
    header.  Reconstruct only the unambiguous semantic columns and mark the
    affected row so the normalized ledger cannot overclaim precision.
    """
    with path.open(newline="", encoding="utf-8") as stream:
        raw_rows = list(csv.reader(stream))
    if not raw_rows or raw_rows[0] != PERMISSION_HEADER:
        raise SystemExit(f"unexpected permission CSV header: {path}")

    output: list[dict[str, str]] = []
    for raw in raw_rows[1:]:
        row_id = raw[0] if raw else ""
        note = ""
        if len(raw) == len(PERMISSION_HEADER):
            row = dict(zip(PERMISSION_HEADER, raw))
        elif row_id == "6AK-009" and len(raw) == 18:
            # The extra comma is between the exported-service description and
            # its signature gate; merge those two pieces into one field.
            row = dict(zip(PERMISSION_HEADER, raw[:7] + [
                raw[7] + "; " + raw[8],
                raw[9], raw[10], raw[11], raw[12], raw[13], raw[14],
                raw[15], raw[16], raw[17],
            ]))
            note = "raw CSV had 18 fields; exported-service/signature fields merged"
        elif row_id == "6AK-011" and len(raw) == 18:
            # The extra comma splits the profile-workflow sink description.
            row = dict(zip(PERMISSION_HEADER, raw[:11] + [
                raw[11] + "; " + raw[12],
                raw[13], raw[14], raw[15], raw[16], raw[17],
            ]))
            note = "raw CSV had 18 fields; downstream-sink fields merged"
        elif row_id == "6AK-010" and len(raw) == 14:
            # This row omitted/merged several columns.  Keep the requester,
            # permission evidence, sink, paths, hashes and line numbers, and
            # mark the missing caller/scope fields as unknown.
            row = {key: "" for key in PERMISSION_HEADER}
            row.update({
                "row_id": raw[0],
                "baseline": raw[1],
                "permission": raw[2],
                "artifact_role": raw[3],
                "requester": raw[4],
                "uses_permission": raw[5],
                "holder_grant": raw[6],
                "exported_component_service": "H2 service exported; signature permission (raw holder/grant field)",
                "method_local_check": raw[7],
                "binder_identity": raw[8],
                "user_scope": "UNKNOWN",
                "downstream_sensitive_sink": raw[9],
                "status": "MALFORMED_WORKER_CSV_ROW_RECONCILED",
                "evidence_path": raw[10],
                "evidence_sha256": raw[11],
                "line": raw[12],
                "notes": raw[13],
            })
            note = "raw CSV had 14 fields; missing caller/scope/status columns set UNKNOWN or explicit reconciliation status"
        else:
            raise SystemExit(f"unexpected field count {len(raw)} for {row_id} in {path}")
        row["_parser_note"] = note
        output.append(row)
    return output


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
            "phase": first(row, "phase") or "6X3",
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
            "scope": "previous public Phase 6X3 corpus",
        })
    return rows


def normalize_worker(path: Path, kind: str, ordinal: int) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    source_rows = read_permission_csv(path) if kind == "PERMISSION" else read_csv(path)
    for index, row in enumerate(source_rows, start=1):
        worker_id = first(row, "id", "evidence_id", "row_id", "route_id", "route")
        evidence_id = f"6X4-{kind}-{index:03d}"

        if kind == "PRODUCTPOLICY":
            surface = "ProductPolicy/DCPMS closure"
            source = first(row, "evidence")
            caller = first(row, "entry_or_surface")
            gate = first(row, "caller_gate")
            identity = "; ".join(x for x in [
                first(row, "binder_identity"),
                first(row, "user_profile_scope"),
            ] if x)
            sink = first(row, "downstream_sink")
            effect = first(row, "verdict")
            confidence = first(row, "verdict") or "UNKNOWN"
            status = first(row, "verdict") or "HOST_ONLY"
        elif kind == "USERSCOPE":
            surface = "OOBE/prewarm user-scope closure"
            source = first(row, "evidence")
            caller = first(row, "source_surface", "caller_identity")
            gate = first(row, "permission")
            identity = "; ".join(x for x in [
                first(row, "caller_identity"),
                first(row, "clear_restore_identity"),
                first(row, "context_or_handle"),
                "User0=" + (first(row, "user_scope_user0") or "UNKNOWN"),
                "User10=" + (first(row, "user_scope_user10") or "UNKNOWN"),
                "profile=" + (first(row, "user_scope_profile") or "UNKNOWN"),
            ] if x)
            sink = first(row, "sink")
            effect = first(row, "evidence_status")
            confidence = first(row, "evidence_status") or "UNKNOWN"
            status = first(row, "evidence_status") or "HOST_ONLY"
        elif kind == "PERMISSION":
            surface = "permission consumer/holder closure"
            source = first(row, "evidence_path")
            caller = "; ".join(x for x in [
                first(row, "requester"), first(row, "artifact_role"),
            ] if x)
            gate = "; ".join(x for x in [
                first(row, "uses_permission"), first(row, "holder_grant"),
                first(row, "method_local_check"),
            ] if x)
            identity = "; ".join(x for x in [
                first(row, "binder_identity"), first(row, "user_scope"),
            ] if x)
            sink = first(row, "downstream_sensitive_sink")
            effect = first(row, "notes")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
        else:
            surface = "OTA indirect/update closure"
            source = first(row, "evidence")
            caller = first(row, "boundary")
            gate = first(row, "boundary")
            identity = first(row, "boundary") or "UNKNOWN"
            sink = first(row, "claim")
            effect = first(row, "static_result")
            confidence = first(row, "class") or "UNKNOWN"
            status = first(row, "class") or "HOST_ONLY"

        evidence_file = source or rel(path)
        evidence_hash = first(row, "evidence_sha256", "sha256", "sha256_or_offset") or sha256(path)
        parser_note = first(row, "_parser_note")
        output.append({
            "evidence_id": evidence_id,
            "phase": "6X4",
            "surface": surface,
            "source": source or rel(path),
            "caller": caller,
            "gate": gate,
            "identity_scope": identity or "UNKNOWN",
            "sink": sink,
            "observed_effect": effect,
            "confidence": confidence,
            "evidence_file": evidence_file,
            "evidence_sha256": evidence_hash,
            "status": status,
            "scope": "; ".join(x for x in [
                f"Phase 6X4 {kind} worker row {worker_id or index}",
                parser_note,
            ] if x),
        })
    return output


def compact(value: str, limit: int = 180) -> str:
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
        "# Phase 6X4 evidence index",
        "",
        "This index adds host-only closure evidence to the public Phase 6X3 ledger. Missing caller, gate, Binder identity, user-scope, sink, and observed-effect edges remain UNKNOWN; static capability is not a privilege transition.",
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
            f"- Scope: {row['scope']}",
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
                label = part.replace('"', "'")
                lines.append(f'  {node_id}["{label}"]')
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
    new_rows = [row for row in rows if row["phase"] == "6X4"]
    new_counts: dict[str, int] = {}
    for row in new_rows:
        new_counts[row["surface"]] = new_counts.get(row["surface"], 0) + 1
    lines = [
        "# Phase 6X4 — privilege-surface closure and residual route audit",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope and safety",
        "",
        "This phase adds four host-only closure audits to the public Phase 6X3 ledger. No worker executed an ADB command, private Binder transaction, service-call payload, driver open/ioctl, OTA/recovery updater, exploit/root attempt, package mutation, reboot, remount, or partition write.",
        "",
        "The acceptance rule remains `caller → gate → Binder identity → user scope → exact sink → observed effect`. A capability, exported component, permission declaration, local system-server service, or native writer is not treated as an elevation path until every relevant edge is joined.",
        "",
        "The raw permission-consumer CSV is preserved byte-for-byte as an input. Three rows do not match its declared CSV header; the generator reconciles only the unambiguous fields, marks those rows in `scope`, and leaves missing caller/scope/status data explicitly unknown rather than silently shifting columns.",
        "",
        "## Evidence counts",
        "",
        f"- Combined ledger rows: **{len(rows)}**; unique IDs: **{len({row['evidence_id'] for row in rows})}**.",
        f"- Prior public Phase 6X3 rows: **{len(rows) - len(new_rows)}**.",
        f"- New Phase 6X4 rows: **{len(new_rows)}**.",
        "- Input manifest: `output/tables/phase6x4-input-manifest.sha256`.",
        "",
        "| Phase | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {phase} | {count} |" for phase, count in sorted(counts.items()))
    lines.extend([
        "",
        "| New surface | Rows |",
        "|---|---:|",
    ])
    lines.extend(f"| {surface} | {count} |" for surface, count in sorted(new_counts.items()))
    lines.extend([
        "",
        "## New closure conclusions",
        "",
        "- **ProductPolicy/DCPMS — 已證實的邊界:** `productpolicyservice_fosinit.xml` loads Amazon ProductPolicy into system_server as a local service; the recovered `onStart` publishes a local service, not an external Binder service. Its trusted component/application setters are internal event/user/profile sinks and do not contain a Fire Launcher, HOME, or User-0 restoration edge. The separate beta-build factory-reset branch is trusted boot policy and was not executed.",
        "- **OOBE/prewarm user scope — 待驗證:** OOBE receivers inherit a lifecycle `Context` without a recovered numeric `UserHandle`; the prewarm contract carries an explicit integer user argument and calls package/process APIs after `clearCallingIdentity`, but the saved slice does not prove the caller, cross-user validation, or a User-0/User-10 target. This is a scope gap, not a shell bypass.",
        "- **Permission consumer/holder — 高可信靜態邊界:** normal/dangerous/custom Amazon permission declarations do not close a requester → grant → exported consumer → method check → sensitive sink chain. The separate H2 service has an exported signature|amazon surface and a profile/user-creation sink, but no recovered edge to HOME, package/component state, or UID 0; actual bind caller remains unknown.",
        "- **OTA indirect/update — 已證實的能力邊界:** the saved native graph closes cache-size error handling, indirect registries, fixed updater-script arguments, and the signed-recovery writer chain. It does not close untrusted input control, AVB/rollback verifier handoff, canonicalization-to-writer control, or low-privilege reachability. No updater or recovery runtime was run.",
        "",
        "## Main verdict",
        "",
        "Phase 6X4 adds useful exclusions and explicitly bounded unknowns, but no new evidence establishes an ordinary-app or shell route to User-0 package-state mutation, formal HOME replacement, UID 0, or partition writing. The ProductPolicy external-Binder hypothesis is rejected for the recovered build; the trusted local setter is not an externally callable confused deputy. H2 and prewarm remain static follow-up surfaces only until their real caller and user-scope edges are recovered.",
        "",
        "The correct next step is further host-only artifact closure (exact requester/bind client, SELinux/service publication, and native verifier handoff), not a risky payload. A driver ioctl, updater execution, unknown Binder transaction, Fire Launcher mutation, or root attempt would add risk without repairing the missing evidence edges and is therefore rejected.",
        "",
        "## Explicitly not claimed",
        "",
        "This report does not claim that every Amazon service, permission, driver, or updater path is safe, and it does not claim that no future vulnerability exists. It records only the evidence actually joined in the preserved artifacts and identifies the minimum missing edge for each residual route.",
        "",
        "## Reproduction",
        "",
        "Use `python3 tools/scripts/build_phase6x4_surface.py --dry-run` to verify all inputs, then `--force` to regenerate the host-only outputs. The four raw worker CSV/Markdown files are included as separate evidence inputs; no device access is required.",
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
        ROOT / "output/tables/phase6x3-control-surface.csv",
        ROOT / "work/luna_worker_phase6ai_productpolicy_dcpms_closure_20260810.csv",
        ROOT / "work/luna_worker_phase6aj_user_scope_closure_20260810.csv",
        ROOT / "work/luna_worker_phase6ak_permission_consumer_closure_20260810.csv",
        ROOT / "work/luna_worker_phase6al_ota_indirect_closure_20260810.csv",
        ROOT / "work/luna_worker_phase6ai_productpolicy_dcpms_closure_20260810.md",
        ROOT / "work/luna_worker_phase6aj_user_scope_closure_20260810.md",
        ROOT / "work/luna_worker_phase6ak_permission_consumer_closure_20260810.md",
        ROOT / "work/luna_worker_phase6al_ota_indirect_closure_20260810.md",
        ROOT / "findings/phase-6x3-report.md",
        ROOT / "findings/phase-6x3-evidence-index.md",
    ]
    require(files)
    outputs = [
        ROOT / "findings/phase-6x4-report.md",
        ROOT / "findings/phase-6x4-evidence-index.md",
        ROOT / "output/tables/phase6x4-control-surface.csv",
        ROOT / "output/tables/phase6x4-input-manifest.sha256",
        ROOT / "output/call-graphs/phase6x4-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase6x4-control-surfaces.md",
    ]
    if args.dry_run:
        print("inputs verified; Phase 6X4 host-only outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))

    rows = normalize_prior(files[0])
    for path, kind in zip(files[1:5], ["PRODUCTPOLICY", "USERSCOPE", "PERMISSION", "OTA"]):
        rows.extend(normalize_worker(path, kind, len(rows) + 1))

    ids = [row["evidence_id"] for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise SystemExit("duplicate evidence IDs: " + ", ".join(duplicates))

    write_csv(ROOT / "output/tables/phase6x4-control-surface.csv", rows)
    write_index(ROOT / "findings/phase-6x4-evidence-index.md", rows)
    write_report(ROOT / "findings/phase-6x4-report.md", rows, files)

    graph = ROOT / "output/call-graphs/phase6x4-control-surfaces.mmd"
    write_graph(graph, rows)
    (ROOT / "output/call-graphs/phase6x4-control-surfaces.md").write_text(
        "# Phase 6X4 control surfaces\n\n```mermaid\n" +
        graph.read_text(encoding="utf-8") + "```\n",
        encoding="utf-8",
    )

    manifest = ROOT / "output/tables/phase6x4-input-manifest.sha256"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {rel(path)}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(f"generated {len(rows)} rows; {len(set(ids))} unique IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
