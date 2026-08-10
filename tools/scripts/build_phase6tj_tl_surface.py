#!/usr/bin/env python3
"""Integrate Phase 6TJ–TL host-only evidence and citation corrections."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6TJ H2 bind/client": (
        ROOT / "work/luna_worker_phase6tj_h2_bind_clients_20260810.md",
        ROOT / "work/luna_worker_phase6tj_h2_bind_clients_20260810.csv",
    ),
    "6TK ION provenance": (
        ROOT / "work/luna_worker_phase6tk_ion_process_provenance_20260810.md",
        ROOT / "work/luna_worker_phase6tk_ion_process_provenance_20260810.csv",
    ),
    "6TL evidence QA": (
        ROOT / "work/luna_worker_phase6tl_evidence_qa_20260810.md",
        ROOT / "work/luna_worker_phase6tl_evidence_qa_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6te-th-report.md",
    ROOT / "findings/phase-6te-th-evidence-index.md",
    ROOT / "output/tables/phase6te-th-input-manifest.sha256",
)
OUTPUTS = (
    ROOT / "findings/phase-6tj-tl-report.md",
    ROOT / "findings/phase-6tj-tl-evidence-index.md",
    ROOT / "output/tables/phase6tj-tl-control-surface.csv",
    ROOT / "output/tables/phase6tj-input-manifest.sha256",
    ROOT / "output/tables/phase6tj-citation-map.csv",
    ROOT / "output/call-graphs/phase6tj-tl-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6tj-tl-control-surfaces.md",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def read_rows(path: Path, family: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            return []
        rows: list[dict[str, str]] = []
        for raw in reader:
            extras = raw.pop(None, None)
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row["surface_family"] = family
            row["source_csv"] = str(path.relative_to(ROOT))
            row["source_sha256"] = sha(path)
            if extras:
                row["csv_parse_warning"] = f"extra_fields={len(extras)}"
            rows.append(row)
        return rows


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
        print("context:", ", ".join(str(path.relative_to(ROOT)) for path in CONTEXT))
        return

    inputs = [path for pair in INPUTS.values() for path in pair] + list(CONTEXT)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))
    existing = [str(path) for path in OUTPUTS if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite output(s):\n" + "\n".join(existing))

    all_rows: list[dict[str, str]] = []
    manifest: list[str] = []
    input_lines: list[str] = []
    evidence_blocks: list[str] = []
    for family, (report_path, ledger_path) in INPUTS.items():
        report_hash, ledger_hash = sha(report_path), sha(ledger_path)
        manifest.extend([f"{report_hash}  {report_path.relative_to(ROOT)}", f"{ledger_hash}  {ledger_path.relative_to(ROOT)}"])
        family_rows = read_rows(ledger_path, family)
        all_rows.extend(family_rows)
        input_lines.append(
            f"- **{family}:** `{report_path.relative_to(ROOT)}` ({report_hash}); "
            f"`{ledger_path.relative_to(ROOT)}` ({ledger_hash}); {len(family_rows)} row(s)."
        )
        evidence_blocks.append(
            f"## {family}\n\nReport SHA-256: `{report_hash}`\n\n"
            f"CSV SHA-256: `{ledger_hash}`\n\nSources: `{report_path.relative_to(ROOT)}`, `{ledger_path.relative_to(ROOT)}`"
        )
    context_hashes = [(path, sha(path)) for path in CONTEXT]
    manifest.extend(f"{digest}  {path.relative_to(ROOT)}" for path, digest in context_hashes)

    fields: list[str] = []
    for row in all_rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    fields = ["surface_family", "source_csv", "source_sha256"] + [
        key for key in fields if key not in {"surface_family", "source_csv", "source_sha256"}
    ]
    matrix = io.StringIO(newline="")
    writer = csv.DictWriter(matrix, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in all_rows:
        writer.writerow({key: row.get(key, "") for key in fields})

    with INPUTS["6TL evidence QA"][1].open(newline="", encoding="utf-8", errors="replace") as stream:
        qa_reader = csv.DictReader(stream)
        qa_fields = qa_reader.fieldnames or []
        qa_rows = list(qa_reader)
    citation = io.StringIO(newline="")
    qa_writer = csv.DictWriter(citation, fieldnames=qa_fields, extrasaction="ignore", lineterminator="\n")
    qa_writer.writeheader()
    qa_writer.writerows(qa_rows)

    report = "# Phase 6TJ–TL host-only closure and citation QA\n\n"
    report += (
        "This bundle closes the H2 service declaration/client inventory and ION library-to-ELF "
        "static provenance, then records citation corrections for the previous Phase 6TE–TI OTA "
        "ledger. It does not infer low-privilege reachability from an exported service, a signature "
        "permission declaration, a library relocation, or a recovery writer.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "Host-only analysis was used. No device, Binder bind/call, service call, driver open/ioctl, "
        "Root/exploit, OTA/recovery/sideload/flash, reboot, package/settings mutation, or partition "
        "write was performed.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: " + "; ".join(f"`{p.relative_to(ROOT)}` ({d})" for p, d in context_hashes) + "\n\n"
        "## H2 service result\n\n"
        "`H2ClientService` is declared exported, single-user and direct-boot-aware with a custom "
        "signature-level `BIND_SERVICE`. The recovered Stub reaches production user/profile and "
        "per-profile state workflows, but the custom permission holder/grant and external clients "
        "are not proven. No H2 path reaches `setComponentEnabledSetting`, formal preferred HOME, or "
        "Fire Launcher selection.\n\n"
        "## ION result\n\n"
        "`libion.so` and `libion_mtk.so` have ION callsites; gralloc and hwcomposer relocations "
        "establish library-level ELF callers. The top-level process/load path, runtime invocation, "
        "and downstream privileged effect are not all joined, so process-level provenance remains "
        "`UNKNOWN`. No launcher, package-state, credential, or OTA effect is shown.\n\n"
        "## Citation QA corrections\n\n"
        "The prior Phase 6TG ledger remains a bounded/local evidence record. QA found TG-01/TG-03/"
        "TG-04 paths absent from the public tree, TG-05 path/hash mismatch, and TG-06 summary/source "
        "hash conflation. The canonical correction table is emitted separately; these issues are "
        "provenance/label corrections, not new runtime findings. Phase 6TF `production_caller=YES` "
        "should be read as an internal production edge only; external reachability remains `UNKNOWN`.\n\n"
        "## Acceptance rule\n\n"
        "A positive privilege or replacement finding requires caller → gate → identity/user scope → "
        "exact sink. Missing holder, caller, loader, or policy edges remain `UNKNOWN`; no current "
        "result justifies a root claim or Fire Launcher mutation.\n"
    )
    evidence = "# Phase 6TJ–TL evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Context\n\n" + "\n".join(f"- `{path.relative_to(ROOT)}`: `{digest}`" for path, digest in context_hashes) + "\n"

    graph = """flowchart LR
  H["H2 exported service"] --> G["signature BIND_SERVICE"]
  G --> U["user/profile workflow sink"]
  G -. "holder/client UNKNOWN" .-> X["No ordinary reachability claim"]
  L["ION library callsites"] --> E["gralloc/hwcomposer ELF relocations"]
  E -. "top-level process/load/runtime UNKNOWN" .-> Y["Library-only result"]
  Q["Prior OTA ledger"] --> C["Citation QA map"]
  C -. "path/hash corrections" .-> R["Do not upgrade capability to caller"]
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f03;
  class H,G,U,L,E,Q,C,R bound;
  class X,Y unknown;
"""
    graph_md = "# Phase 6TJ–TL control-surface graph\n\n```mermaid\n" + graph + "```\n"

    write_new(OUTPUTS[0], report, args.force)
    write_new(OUTPUTS[1], evidence, args.force)
    write_new(OUTPUTS[2], matrix.getvalue(), args.force)
    write_new(OUTPUTS[3], "\n".join(manifest) + "\n", args.force)
    write_new(OUTPUTS[4], citation.getvalue(), args.force)
    write_new(OUTPUTS[5], graph, args.force)
    write_new(OUTPUTS[6], graph_md, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(all_rows)} qa_rows={len(qa_rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
