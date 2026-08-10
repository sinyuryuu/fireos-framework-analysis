#!/usr/bin/env python3
"""Build the Phase 7 broad-route evidence bundle.

Host-only synthesis of the 7.3.3.1 source/installer, Amazon IPC, kernel/driver,
existing-runtime, and launcher-watchdog audits.  It never contacts a device,
executes an updater, calls Binder, opens a driver, or mutates any artifact.
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def require(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))


def normalize_prior(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(path):
        rows.append({
            "evidence_id": first(row, "evidence_id", "id"),
            "phase": first(row, "phase") or "6X4",
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
            "scope": "previous public Phase 6X4 corpus",
        })
    return rows


def normalize_worker(path: Path, kind: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(path), start=1):
        worker_id = first(row, "id", "evidence_id", "row_id", "route", "test_or_route")
        evidence_id = f"P7-{kind}-{index:03d}"

        if kind == "SOURCE":
            surface = "7.3.3.1 source/installer scope"
            source = first(row, "source")
            artifact = first(row, "artifact")
            caller = artifact
            gate = first(row, "claim")
            identity = "UNKNOWN"
            sink = "source/build/installer provenance"
            effect = first(row, "claim")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
            missing = first(row, "missing_edge")
        elif kind == "IPC":
            surface = "Amazon Framework/System Services IPC"
            source = first(row, "evidence")
            caller = first(row, "caller")
            gate = first(row, "gate")
            identity = "; ".join(x for x in [first(row, "binder_identity"), first(row, "user_scope")] if x)
            sink = first(row, "sink")
            effect = first(row, "effect")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
            missing = first(row, "missing_edge")
        elif kind == "KERNEL":
            surface = first(row, "surface") or "kernel/driver"
            source = first(row, "source")
            caller = first(row, "caller")
            gate = "; ".join(x for x in [first(row, "policy"), first(row, "gate")] if x)
            identity = "; ".join(x for x in [first(row, "caller"), first(row, "node_or_entry")] if x)
            sink = first(row, "sink")
            effect = first(row, "effect")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
            missing = first(row, "missing_edge")
        elif kind == "RUNTIME":
            surface = "existing runtime/workaround reconciliation"
            source = first(row, "evidence")
            caller = first(row, "test_or_route")
            gate = first(row, "mutation")
            identity = first(row, "device_user")
            sink = first(row, "observed_result")
            effect = "; ".join(x for x in [first(row, "persistence"), first(row, "rollback")] if x)
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
            missing = first(row, "next_minimal_test")
        else:
            surface = "Amazon package-state/HOME watchdog"
            source = first(row, "evidence")
            caller = first(row, "caller", "entry")
            gate = first(row, "gate")
            identity = "; ".join(x for x in [first(row, "identity"), first(row, "user_scope")] if x)
            sink = "; ".join(x for x in [first(row, "target"), first(row, "sink")] if x)
            effect = first(row, "effect")
            confidence = first(row, "status") or "UNKNOWN"
            status = first(row, "status") or "HOST_ONLY"
            missing = first(row, "missing_edge")

        source_label = source or rel(path)
        evidence_label = (artifact if kind == "SOURCE" else source_label) or rel(path)
        evidence_hash = first(row, "evidence_sha256", "sha256") or sha256(path)
        output.append({
            "evidence_id": evidence_id,
            "phase": "7",
            "surface": surface,
            "source": source_label,
            "caller": caller,
            "gate": gate,
            "identity_scope": identity or "UNKNOWN",
            "sink": sink,
            "observed_effect": effect,
            "confidence": confidence,
            "evidence_file": evidence_label,
            "evidence_sha256": evidence_hash,
            "status": status,
            "scope": "; ".join(x for x in [
                f"Phase 7 {kind} worker row {worker_id or index}",
                f"missing_edge={missing}" if missing else "",
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
        "# Phase 7 evidence index",
        "",
        "Phase 7 combines preserved Phase 6X4 evidence, the current read-only device baseline, and five host-only worker audits. Missing edges remain UNKNOWN and do not become privilege claims.",
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
    new_rows = [row for row in rows if row["phase"] == "7"]
    surfaces: dict[str, int] = {}
    for row in new_rows:
        surfaces[row["surface"]] = surfaces.get(row["surface"], 0) + 1
    lines = [
        "# Phase 7 — broad privilege and system-control route audit",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope and safety",
        "",
        "This phase broadens the search beyond Launcher to Amazon IPC, OTA/source provenance, kernel/driver surfaces, package-state/watchdog paths, and previously measured runtime workarounds. The source/IPC/kernel/watchdog audits are host-only; the device evidence is a serial-bound read-only baseline. No exploit, root attempt, unknown Binder/service transaction, driver open/ioctl, updater/recovery execution, package/settings mutation, reboot, remount, or partition write was performed in this phase.",
        "",
        "Every candidate is evaluated as `caller → gate → Binder identity → user scope → exact sink → observed effect`. Static source capability, an exported component, a permission declaration, a native writer, or an address/string hit is not treated as a privilege transition without the missing edges.",
        "",
        "## Evidence counts",
        "",
        f"- Combined ledger rows: **{len(rows)}**; unique IDs: **{len({row['evidence_id'] for row in rows})}**.",
        f"- Prior public Phase 6X4 rows: **{len(rows) - len(new_rows)}**.",
        f"- New Phase 7 rows: **{len(new_rows)}**.",
        "- Input manifest: `output/tables/phase7-input-manifest.sha256`.",
        "",
        "| Phase | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in sorted(counts.items()))
    lines.extend(["", "| New surface | Rows |", "|---|---:|"])
    lines.extend(f"| {key} | {value} |" for key, value in sorted(surfaces.items()))
    lines.extend([
        "",
        "## Current read-only device baseline",
        "",
        "The serial-bound capture `adb/phase7/PHASE7-BASELINE-20260810-01/` reports PS7331.4463N, SELinux Enforcing, User 0 current, User 0 HOME `com.amazon.firelauncher/.Launcher` at priority 50, Microsoft at 0, and Settings FallbackHome at -1000. User 10 resolves FallbackHome in this snapshot. The capture contains original stdout/stderr, metadata, and a verified SHA-256 manifest; it is not a vulnerability result.",
        "",
        "## Findings",
        "",
        "- **7A source/installer provenance — status follows the worker evidence:** the official 7.3.3.1 source/package scope is recorded without executing an updater or constructing an OTA. Absence from a bounded archive listing is only a bounded negative; build provenance and signed-image equivalence remain separate questions.",
        "- **7B IPC — residual edges, no completed low-privilege chain:** 15 routes retain a small set of unknown caller/user-validation joins (prewarm, KFT tx3, DPM→PMS, SettingsProvider caller, DCPMS bind). The remainder are duplicate or bounded-negative. No route establishes an ordinary App/shell caller reaching User-0 Fire package/HOME state.",
        "- **7C kernel/driver — capability without reachability:** 15 user-facing surfaces retain UNKNOWN for at least one final shipped object/node policy/caller-domain join. No driver or kernel runtime was touched, and no route establishes a package/HOME/UID-0 sink.",
        "- **7D runtime/workarounds — confirmed scope:** User 0 formal HOME remains Fire. Accessibility and ADB monitor behavior are foreground redirects only; Accessibility HOME consumption failed 0/3. Child/Tahoe HOME is per-user and does not replace User 0.",
        "- **7E watchdog/config — no new User-0 writer:** the only new Fire-targeted literal is a package-scoped external-app availability notification. KFT child writers, deny-list resource/property reads, and LauncherHijackPreventer callbacks do not close a Fire User-0 HOME/package-state writer.",
        "",
        "## Main verdict",
        "",
        "The expanded evidence still does not establish a reproducible ordinary-App or shell route to disable Fire Launcher, replace User-0 HOME, obtain UID 0, or write a protected partition. The best verified rootless behavior remains a foreground redirect that is not a formal HOME replacement. The remaining unknowns are provenance/authorization joins, not a demonstrated exploit. Running unknown Binder payloads, driver ioctls, malformed OTA packages, or root exploits would add device risk without closing those missing edges and is rejected.",
        "",
        "## Next smallest evidence targets",
        "",
        "1. Host-only recover the exact production bind client and permission/grant path for prewarm, DCPMS, H2, and SettingsProvider; do not call the services.",
        "2. Host-only map final DTB/ueventd/file_contexts/TE allow and shipped native caller for the highest-value driver surfaces; do not open nodes.",
        "3. If a future authorized test is needed, perform only the existing read-only HOME/package/accessibility foreground guard; do not repeat closed disable/priority/DPM/Accessibility-consume tests.",
        "",
        "## Reproduction",
        "",
        "Use `python3 tools/scripts/build_phase7_surface.py --dry-run` to verify inputs and `--force` to regenerate the host-only bundle. The device baseline was captured with `tools/scripts/capture_phase6ee_current_baseline.py --serial G001LT0511550CFT --output adb/phase7/PHASE7-BASELINE-20260810-01`; its per-file manifest was verified inside the capture directory.",
        "",
        "## Explicitly not claimed",
        "",
        "This phase does not claim that every kernel driver, Amazon service, permission, or updater path is safe, nor that no future vulnerability exists. It records only joined evidence and preserves every unresolved edge as UNKNOWN.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    capture_dir = ROOT / "adb/phase7/PHASE7-BASELINE-20260810-01"
    files = [
        ROOT / "output/tables/phase6x4-control-surface.csv",
        ROOT / "work/luna_worker_phase7a_source_ota_scope_20260810.csv",
        ROOT / "work/luna_worker_phase7b_ipc_residual_20260810.csv",
        ROOT / "work/luna_worker_phase7c_kernel_driver_closure_20260810.csv",
        ROOT / "work/luna_worker_phase7d_runtime_workaround_reconciliation_20260810.csv",
        ROOT / "work/luna_worker_phase7e_launcher_watchdog_surface_20260810.csv",
        ROOT / "work/luna_worker_phase7a_source_ota_scope_20260810.md",
        ROOT / "work/luna_worker_phase7b_ipc_residual_20260810.md",
        ROOT / "work/luna_worker_phase7c_kernel_driver_closure_20260810.md",
        ROOT / "work/luna_worker_phase7d_runtime_workaround_reconciliation_20260810.md",
        ROOT / "work/luna_worker_phase7e_launcher_watchdog_surface_20260810.md",
        ROOT / "findings/phase-6x4-report.md",
        ROOT / "findings/phase-7-readonly-baseline.md",
    ]
    require(files)
    if capture_dir.exists():
        files.extend(sorted(path for path in capture_dir.iterdir() if path.is_file()))

    outputs = [
        ROOT / "findings/phase-7-report.md",
        ROOT / "findings/phase-7-evidence-index.md",
        ROOT / "output/tables/phase7-control-surface.csv",
        ROOT / "output/tables/phase7-input-manifest.sha256",
        ROOT / "output/call-graphs/phase7-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase7-control-surfaces.md",
    ]
    if args.dry_run:
        print(f"inputs verified ({len(files)} files); Phase 7 host-only outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))

    rows = normalize_prior(files[0])
    for path, kind in zip(files[1:6], ["SOURCE", "IPC", "KERNEL", "RUNTIME", "WATCHDOG"]):
        rows.extend(normalize_worker(path, kind))
    ids = [row["evidence_id"] for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise SystemExit("duplicate evidence IDs: " + ", ".join(duplicates))

    write_csv(ROOT / "output/tables/phase7-control-surface.csv", rows)
    write_index(ROOT / "findings/phase-7-evidence-index.md", rows)
    write_report(ROOT / "findings/phase-7-report.md", rows, files)
    graph = ROOT / "output/call-graphs/phase7-control-surfaces.mmd"
    write_graph(graph, rows)
    (ROOT / "output/call-graphs/phase7-control-surfaces.md").write_text(
        "# Phase 7 control surfaces\n\n```mermaid\n" + graph.read_text(encoding="utf-8") + "```\n",
        encoding="utf-8",
    )
    manifest = ROOT / "output/tables/phase7-input-manifest.sha256"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(f"{sha256(path)}  {rel(path)}" for path in files) + "\n", encoding="utf-8")
    print(f"generated {len(rows)} rows; {len(set(ids))} unique IDs; inputs={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
