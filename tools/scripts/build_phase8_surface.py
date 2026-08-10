#!/usr/bin/env python3
"""Build the Phase 8 targeted caller/scope/policy closure bundle.

This is a host-only evidence normalizer.  It does not access the device,
invoke Binder, open a driver, execute OTA/recovery code, or mutate artifacts.
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
    output: list[dict[str, str]] = []
    for row in read_csv(path):
        output.append({
            "evidence_id": first(row, "evidence_id", "id"),
            "phase": first(row, "phase") or "7",
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
            "scope": "previous public Phase 7 corpus",
        })
    return output


def normalize_worker(path: Path, kind: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(path), start=1):
        worker_id = first(row, "id", "evidence_id", "row_id")
        if kind == "PREWARM":
            surface = "prewarm caller/user-scope closure"
            source = first(row, "evidence")
            caller = first(row, "caller", "entry")
            gate = first(row, "permission", "holder")
            identity = first(row, "identity")
            sink = first(row, "sink")
            effect = first(row, "effect")
            status = first(row, "status") or "UNKNOWN"
            missing = first(row, "missing_edge")
        elif kind == "KFT":
            surface = "KFT tx3 caller/user-scope closure"
            source = first(row, "evidence")
            caller = first(row, "client", "entry")
            gate = first(row, "caller_gate")
            identity = first(row, "binder_identity")
            sink = "; ".join(x for x in [first(row, "target"), first(row, "sink")] if x)
            effect = first(row, "effect")
            status = first(row, "status") or "UNKNOWN"
            missing = first(row, "missing_edge")
        elif kind == "SETTINGS":
            surface = "SettingsProvider/HOME-key closure"
            source = first(row, "evidence")
            caller = first(row, "caller", "provider_or_key")
            gate = first(row, "permission")
            identity = first(row, "identity")
            sink = "; ".join(x for x in [first(row, "home_relevance"), first(row, "sink")] if x)
            effect = first(row, "effect")
            status = first(row, "status") or "UNKNOWN"
            missing = first(row, "missing_edge")
        else:
            surface = "driver final node/policy/caller closure"
            source = first(row, "evidence")
            caller = first(row, "caller", "surface")
            gate = "; ".join(x for x in [first(row, "mode_policy"), first(row, "gate")] if x)
            identity = first(row, "caller")
            sink = first(row, "sink")
            effect = first(row, "effect")
            status = first(row, "status") or "UNKNOWN"
            missing = first(row, "missing_edge")

        evidence_file = source or rel(path)
        evidence_hash = first(row, "evidence_sha256", "sha256") or sha256(path)
        output.append({
            "evidence_id": f"P8-{kind}-{index:03d}",
            "phase": "8",
            "surface": surface,
            "source": source or rel(path),
            "caller": caller,
            "gate": gate,
            "identity_scope": identity or "UNKNOWN",
            "sink": sink,
            "observed_effect": effect,
            "confidence": status,
            "evidence_file": evidence_file,
            "evidence_sha256": evidence_hash,
            "status": status,
            "scope": "; ".join(x for x in [
                f"Phase 8 {kind} worker row {worker_id or index}",
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
        "# Phase 8 evidence index",
        "",
        "Phase 8 adds targeted host-only closure audits. Missing caller, gate, identity, user-scope, sink, and effect edges remain UNKNOWN; no row is a permission-escalation claim by itself.",
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
    new_rows = [row for row in rows if row["phase"] == "8"]
    counts: dict[str, int] = {}
    for row in new_rows:
        counts[row["surface"]] = counts.get(row["surface"], 0) + 1
    lines = [
        "# Phase 8 — targeted caller, user-scope, and policy closure",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Safety",
        "",
        "All four audits are host-only. No device command, private Binder/service transaction, broadcast, package/settings mutation, driver open/ioctl, OTA/recovery execution, reboot, root attempt, or partition write was performed.",
        "",
        "The acceptance rule remains `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges are preserved as UNKNOWN.",
        "",
        f"Combined ledger rows: **{len(rows)}**; unique IDs: **{len({row['evidence_id'] for row in rows})}**. New Phase 8 rows: **{len(new_rows)}**.",
        "",
        "| New surface | Rows |",
        "|---|---:|",
    ]
    lines.extend(f"| {surface} | {count} |" for surface, count in sorted(counts.items()))
    lines.extend([
        "",
        "## Concrete results",
        "",
        "- **Prewarm:** the saved ordinary-app observation reaches transaction 1 and starts a target process, but the sink is process/resource prewarm only. No HOME selector, preferred-activity writer, package/component-state writer, permission grant, UID-0 transition, or partition sink is present. The saved enforcing-policy shell path is bounded-negative.",
        "- **KFT tx3:** the recovered `enableKftLauncher(UserInfo)` path reaches three package/component setters, but each setter consumes the supplied `UserInfo.id` and is child/profile scoped. The static slice does not establish an accepted arbitrary external caller, a complete method-local cross-user gate, or a User-0 restoration writer; the shell service-manager boundary is separately blocked in saved enforcing evidence.",
        "- **SettingsProvider:** the production provider persists system/secure/global values through `SettingsRegistry`/`SettingsState`. HOME-adjacent keys are card or personalization state, and the searched provider path has no bridge to `setHomeActivity`, `replacePreferredActivity`, or a package/component-state setter. The production caller for generic writes remains unknown.",
        "- **Drivers:** CMDQ/MDP, ION, MTK ION, M4U, uinput, and AUXADC retain at least one missing final-artifact, node/policy, shipped-native-caller, or input-boundary edge. They remain UNKNOWN; no device node was opened and no ioctl was sent.",
        "",
        "The Phase 8 evidence therefore expands the permission/control inventory without proving a new low-privilege privilege transition. A complete route still requires the full caller → gate → Binder identity → user scope → exact sink → observed effect chain.",
        "",
        "## Closure questions",
        "",
        "- **Prewarm:** only promote a permission anomaly if the exact requester, holder/grant, calling UID, target-user validation, and observed process sink all join. A boolean check whose return is not consumed is not by itself a bypass.",
        "- **KFT tx3:** distinguish the child/profile `UserInfo.id` writer from a User-0 writer. A transaction code or Stub without an accepted external caller and cross-user gate is not a usable route.",
        "- **SettingsProvider:** distinguish a real provider write implementation from a shell/App caller that can write a HOME-relevant key and then reach PMS/ATM. Key strings alone are not HOME control.",
        "- **Drivers:** require final node/DT registration, mode/SELinux policy, shipped native caller, input boundary, and sensitive effect. Source ioctl capability without that join remains UNKNOWN.",
        "",
        "## Verdict",
        "",
        "This phase is designed to reduce the remaining uncertainty, not to manufacture a POC. It does not authorize or implement exploit payloads. Any row that lacks a complete chain remains a host-only research lead and must not be tested with unknown Binder codes, driver ioctls, malformed OTA data, or root tooling.",
        "",
        "## Reproduction",
        "",
        "Run `python3 tools/scripts/build_phase8_surface.py --dry-run` to verify inputs, then `--force` to regenerate the bundle after all four worker CSVs exist. No device is required.",
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
        ROOT / "output/tables/phase7-control-surface.csv",
        ROOT / "work/luna_worker_phase8a_prewarm_caller_user_20260810.csv",
        ROOT / "work/luna_worker_phase8b_kft_tx3_closure_20260810.csv",
        ROOT / "work/luna_worker_phase8c_settingsprovider_home_20260810.csv",
        ROOT / "work/luna_worker_phase8d_driver_final_join_20260810.csv",
        ROOT / "work/luna_worker_phase8a_prewarm_caller_user_20260810.md",
        ROOT / "work/luna_worker_phase8b_kft_tx3_closure_20260810.md",
        ROOT / "work/luna_worker_phase8c_settingsprovider_home_20260810.md",
        ROOT / "work/luna_worker_phase8d_driver_final_join_20260810.md",
        ROOT / "findings/phase-7-report.md",
    ]
    require(files)
    outputs = [
        ROOT / "findings/phase-8-report.md",
        ROOT / "findings/phase-8-evidence-index.md",
        ROOT / "output/tables/phase8-control-surface.csv",
        ROOT / "output/tables/phase8-input-manifest.sha256",
        ROOT / "output/call-graphs/phase8-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase8-control-surfaces.md",
    ]
    if args.dry_run:
        print(f"inputs verified ({len(files)} files); Phase 8 outputs would be generated")
        return 0
    if not args.force:
        existing = [str(path) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))
    rows = normalize_prior(files[0])
    for path, kind in zip(files[1:5], ["PREWARM", "KFT", "SETTINGS", "DRIVER"]):
        rows.extend(normalize_worker(path, kind))
    ids = [row["evidence_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate evidence IDs")
    write_csv(ROOT / "output/tables/phase8-control-surface.csv", rows)
    write_index(ROOT / "findings/phase-8-evidence-index.md", rows)
    write_report(ROOT / "findings/phase-8-report.md", rows, files)
    graph = ROOT / "output/call-graphs/phase8-control-surfaces.mmd"
    write_graph(graph, rows)
    (ROOT / "output/call-graphs/phase8-control-surfaces.md").write_text(
        "# Phase 8 control surfaces\n\n```mermaid\n" + graph.read_text(encoding="utf-8") + "```\n",
        encoding="utf-8",
    )
    manifest = ROOT / "output/tables/phase8-input-manifest.sha256"
    manifest.write_text("\n".join(f"{sha256(path)}  {rel(path)}" for path in files) + "\n", encoding="utf-8")
    print(f"generated {len(rows)} rows; {len(set(ids))} unique IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
