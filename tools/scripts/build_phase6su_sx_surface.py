#!/usr/bin/env python3
"""Integrate the Phase 6SU–SX host-only evidence ledgers.

The inputs are static worker reports.  This utility never contacts a device,
executes a Binder transaction, opens a driver, runs OTA/recovery code, or
changes existing evidence.  It refuses to replace an existing output bundle
unless --force is explicit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6SU IPC residual": (
        ROOT / "work/luna_worker_phase6su_ipc_residual_20260810.md",
        ROOT / "work/luna_worker_phase6su_ipc_residual_20260810.csv",
    ),
    "6SV exported/protected surface": (
        ROOT / "work/luna_worker_phase6sv_exported_surface_20260810.md",
        ROOT / "work/luna_worker_phase6sv_exported_surface_20260810.csv",
    ),
    "6SW kernel surface": (
        ROOT / "work/luna_worker_phase6sw_kernel_surface_20260810.md",
        ROOT / "work/luna_worker_phase6sw_kernel_surface_20260810.csv",
    ),
    "6SX evidence audit": (
        ROOT / "work/luna_worker_phase6sx_evidence_audit_20260810.md",
        ROOT / "work/luna_worker_phase6sx_evidence_audit_20260810.csv",
    ),
}
OUTPUTS = (
    ROOT / "findings/phase-6su-sx-report.md",
    ROOT / "findings/phase-6su-sx-evidence-index.md",
    ROOT / "output/tables/phase6su-sx-control-surface.csv",
    ROOT / "output/tables/phase6su-sx-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6su-sx-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6su-sx-control-surfaces.md",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def read_rows(path: Path, family: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return rows
        for row in reader:
            extras = row.pop(None, None)
            normalized = {k: (v or "").strip() for k, v in row.items() if k}
            normalized["surface_family"] = family
            normalized["source_csv"] = str(path.relative_to(ROOT))
            normalized["source_sha256"] = digest(path)
            if extras:
                normalized["csv_parse_warning"] = "unquoted_extra_fields"
                normalized["csv_extra_field_count"] = str(len(extras))
            rows.append(normalized)
    return rows


def write_new(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> None:
    if args.dry_run:
        print("host-only dry run; no outputs written")
        for family, pair in INPUTS.items():
            print(f"{family}: {pair[0].relative_to(ROOT)}, {pair[1].relative_to(ROOT)}")
        return

    missing = [str(p) for pair in INPUTS.values() for p in pair if not p.is_file()]
    if missing:
        raise SystemExit("missing worker input(s):\n" + "\n".join(missing))
    existing = [str(p) for p in OUTPUTS if p.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite existing output(s):\n" + "\n".join(existing))

    rows: list[dict[str, str]] = []
    manifest = [
        "# Phase 6SU–SX input manifest",
        f"generated_utc={datetime.now(timezone.utc).isoformat()}",
        f"git_head={head()}",
        "device_contacted=false",
        "device_mutation=false",
        "binder_transaction_sent=false",
        "driver_open_or_ioctl=false",
        "ota_or_recovery_executed=false",
        "",
    ]
    evidence: list[str] = []
    input_lines: list[str] = []
    for family, (report, ledger) in INPUTS.items():
        report_hash, ledger_hash = digest(report), digest(ledger)
        manifest += [
            f"{report_hash}  {report.relative_to(ROOT)}",
            f"{ledger_hash}  {ledger.relative_to(ROOT)}",
        ]
        part = read_rows(ledger, family)
        rows.extend(part)
        input_lines.append(
            f"- **{family}:** `{report.relative_to(ROOT)}` ({report_hash}); "
            f"`{ledger.relative_to(ROOT)}` ({ledger_hash}); {len(part)} data row(s)."
        )
        evidence.append(
            f"## {family}\n\n"
            f"Report SHA-256: `{report_hash}`\n\n"
            f"CSV SHA-256: `{ledger_hash}`\n\n"
            f"Sources: `{report.relative_to(ROOT)}`, `{ledger.relative_to(ROOT)}`\n\n"
            "Interpretation remains bounded by the worker's cited exact-build evidence."
        )

    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    ordered = ["surface_family", "source_csv", "source_sha256"] + [
        f for f in fields if f not in {"surface_family", "source_csv", "source_sha256"}
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=ordered, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in ordered})

    report = """# Phase 6SU–SX broad privilege-surface continuation\n\n"""
    report += (
        "This bundle integrates four host-only static/evidence audits. It does not "
        "treat exported status, a missing local permission check, a kernel symbol, "
        "or a privileged capability as proof of low-privilege reachability. A route "
        "must show caller → gate → identity/user scope → exact sink.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No ADB, Binder transaction, broadcast, driver open/ioctl, OTA/recovery "
        "execution, Root/exploit, reboot, package/settings mutation, or partition "
        "write was performed. Raw worker files are retained and output files are "
        "generated without overwriting previous evidence.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "## Interpretation\n\n"
        "- IPC rows separate declaration, publication, caller, permission, identity "
        "and sink. `UNKNOWN` means the saved corpus does not close that edge.\n"
        "- Exported components and protected broadcasts are inventory evidence only; "
        "sender permission, UID, lifecycle predicate and downstream target are required.\n"
        "- Kernel rows distinguish source/config presence, shipped node/policy, and "
        "exact native caller. Source-only ioctl/proc/debugfs code is not a runtime route.\n"
        "- Evidence-audit rows are a completeness catalog, not new runtime observations.\n\n"
        "## Safe continuation\n\n"
        "The next justified work is exact-build corpus completeness and naturally "
        "obtained read-only state. Unknown Binder transactions, crafted OTA input, "
        "driver ioctl/proc writes, Root/exploit payloads and Fire Launcher mutation "
        "are not safe validation steps and remain excluded.\n"
    )
    evidence_text = "# Phase 6SU–SX evidence index\n\n" + "\n\n".join(evidence) + "\n"
    graph = """flowchart LR
  C["Caller / sender"] --> G["Permission + lifecycle gate"]
  G --> I["Binder identity + user scope"]
  I --> S["Exact system/package/HOME/OTA sink"]
  K["GPL source + config"] --> N["Shipped node + policy"]
  N --> E["Exact native caller"]
  E --> G
  X["Exported component / broadcast"] -. "inventory only" .-> G
  U["UNKNOWN edge"] --> R["Do not claim reachability"]
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f03;
  classDef boundary fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  class U,R unknown;
  class C,G,I,S,K,N,E,X boundary;
"""
    graph_md = "# Phase 6SU–SX control-surface graph\n\n```mermaid\n" + graph + "```\n"

    write_new(OUTPUTS[0], report, args.force)
    write_new(OUTPUTS[1], evidence_text, args.force)
    write_new(OUTPUTS[2], buffer.getvalue(), args.force)
    write_new(OUTPUTS[3], "\n".join(manifest) + "\n", args.force)
    write_new(OUTPUTS[4], graph, args.force)
    write_new(OUTPUTS[5], graph_md, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
