#!/usr/bin/env python3
"""Integrate Phase 6TA–TD static evidence without contacting a device."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6TA Amazon PM proxy": (
        ROOT / "work/luna_worker_phase6ta_proxy_closure_20260810.md",
        ROOT / "work/luna_worker_phase6ta_proxy_closure_20260810.csv",
    ),
    "6TB DCPMS consumer": (
        ROOT / "work/luna_worker_phase6tb_dcpms_consumer_20260810.md",
        ROOT / "work/luna_worker_phase6tb_dcpms_consumer_20260810.csv",
    ),
    "6TC native caller join": (
        ROOT / "work/luna_worker_phase6tc_native_caller_join_20260810.md",
        ROOT / "work/luna_worker_phase6tc_native_caller_join_20260810.csv",
    ),
    "6TD unintegrated evidence": (
        ROOT / "work/luna_worker_phase6td_unintegrated_evidence_20260810.md",
        ROOT / "work/luna_worker_phase6td_unintegrated_evidence_20260810.csv",
    ),
}
OUTPUTS = (
    ROOT / "findings/phase-6ta-td-report.md",
    ROOT / "findings/phase-6ta-td-evidence-index.md",
    ROOT / "output/tables/phase6ta-td-control-surface.csv",
    ROOT / "output/tables/phase6ta-td-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6ta-td-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6ta-td-control-surfaces.md",
)


def sha(path: Path) -> str:
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


def rows(path: Path, family: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        out: list[dict[str, str]] = []
        for raw in reader:
            extra = raw.pop(None, None)
            row = {k: (v or "").strip() for k, v in raw.items() if k}
            row["surface_family"] = family
            row["source_csv"] = str(path.relative_to(ROOT))
            row["source_sha256"] = sha(path)
            if extra:
                row["csv_parse_warning"] = f"extra_fields={len(extra)}"
            out.append(row)
        return out


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> None:
    if args.dry_run:
        print("host-only dry run; no output written")
        for family, (report, ledger) in INPUTS.items():
            print(f"{family}: {report.relative_to(ROOT)}, {ledger.relative_to(ROOT)}")
        return

    missing = [str(p) for pair in INPUTS.values() for p in pair if not p.is_file()]
    if missing:
        raise SystemExit("missing worker input(s):\n" + "\n".join(missing))
    existing = [str(p) for p in OUTPUTS if p.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite existing output(s):\n" + "\n".join(existing))

    all_rows: list[dict[str, str]] = []
    # Keep this file in native sha256sum(1) check format. Provenance and the
    # host-only safety boundary are recorded in the generated report/index.
    manifest: list[str] = []
    input_lines: list[str] = []
    blocks: list[str] = []
    for family, (report, ledger) in INPUTS.items():
        rh, lh = sha(report), sha(ledger)
        manifest.extend([f"{rh}  {report.relative_to(ROOT)}", f"{lh}  {ledger.relative_to(ROOT)}"])
        part = rows(ledger, family)
        all_rows.extend(part)
        input_lines.append(f"- **{family}:** `{report.relative_to(ROOT)}` ({rh}); `{ledger.relative_to(ROOT)}` ({lh}); {len(part)} row(s).")
        blocks.append(f"## {family}\n\nReport SHA-256: `{rh}`\n\nCSV SHA-256: `{lh}`\n\nSources: `{report.relative_to(ROOT)}`, `{ledger.relative_to(ROOT)}`")

    fields: list[str] = []
    for row in all_rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    fields = ["surface_family", "source_csv", "source_sha256"] + [k for k in fields if k not in {"surface_family", "source_csv", "source_sha256"}]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in all_rows:
        writer.writerow({key: row.get(key, "") for key in fields})

    report = "# Phase 6TA–TD static control-surface continuation\n\n"
    report += (
        "This host-only bundle validates an existing Amazon PM proxy analysis, traces "
        "DCPMS consumers, joins exact native callers where available, and inventories "
        "previously unintegrated evidence. It does not infer a low-privilege route from "
        "an exported component, missing local permission check, or source capability.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No ADB, Binder transaction, broadcast, driver operation, OTA/recovery execution, "
        "Root/exploit, reboot, package/settings mutation, or partition write was performed.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "## Acceptance rule\n\n"
        "A meaningful privilege finding requires caller → authorization/ownership gate → "
        "identity and user scope → exact state/capability sink. `UNKNOWN` remains an "
        "evidence boundary; test-only callers and generated Proxy/Stub code are not "
        "production caller proof.\n\n"
        "## Result handling\n\n"
        "Proxy receiver results are limited to system-app PendingIntent creator and caller-UID "
        "ownership gates plus receiver dispatch; no HOME/PMS writer was accepted. DCPMS "
        "consumer results are limited to CDE policy persistence/evaluation unless an exact "
        "downstream system sink is shown. Native rows require path-specific shipped ELF "
        "operation; source/config/library names alone remain UNKNOWN.\n"
    )
    evidence = "# Phase 6TA–TD evidence index\n\n" + "\n\n".join(blocks) + "\n"
    graph = """flowchart LR
  A["External caller / system-created PendingIntent"] --> B["Permission or creator/UID gate"]
  B --> C["Binder identity + ownership/user scope"]
  C --> D["Proxy receiver or CDE policy sink"]
  K["Source/config"] --> N["Shipped node/policy"]
  N --> E["Exact native operation"]
  E --> B
  D -. "no HOME/PMS sink unless proven" .-> X["Bounded result"]
  U["UNKNOWN caller or consumer"] --> R["Do not claim reachability"]
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f03;
  classDef boundary fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  class U,R unknown;
  class A,B,C,D,K,N,E,X boundary;
"""
    graph_md = "# Phase 6TA–TD control-surface graph\n\n```mermaid\n" + graph + "```\n"

    write_new(OUTPUTS[0], report, args.force)
    write_new(OUTPUTS[1], evidence, args.force)
    write_new(OUTPUTS[2], buffer.getvalue(), args.force)
    write_new(OUTPUTS[3], "\n".join(manifest) + "\n", args.force)
    write_new(OUTPUTS[4], graph, args.force)
    write_new(OUTPUTS[5], graph_md, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(all_rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
