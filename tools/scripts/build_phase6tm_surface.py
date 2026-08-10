#!/usr/bin/env python3
"""Build the Phase 6TM host-only provenance bundle.

The script consumes independent worker ledgers and creates new, non-overwriting
integration artifacts.  It never reads from or writes to a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6TM-A H2 permission": (
        ROOT / "work/luna_worker_phase6tm_h2_permission_20260810.md",
        ROOT / "work/luna_worker_phase6tm_h2_permission_20260810.csv",
    ),
    "6TM-B ION loader": (
        ROOT / "work/luna_worker_phase6tn_ion_loader_graph_20260810.md",
        ROOT / "work/luna_worker_phase6tn_ion_loader_graph_20260810.csv",
    ),
    "6TM-C OTA citation repair": (
        ROOT / "work/luna_worker_phase6tm_ota_public_repair_20260810.md",
        ROOT / "work/luna_worker_phase6tm_ota_public_repair_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6tj-tl-report.md",
    ROOT / "findings/phase-6tj-tl-evidence-index.md",
    ROOT / "output/tables/phase6tj-citation-map.csv",
    ROOT / "findings/phase-6ti-readonly-snapshot.md",
)
OUTPUTS = (
    ROOT / "findings/phase-6tm-report.md",
    ROOT / "findings/phase-6tm-evidence-index.md",
    ROOT / "output/tables/phase6tm-control-surface.csv",
    ROOT / "output/tables/phase6tm-input-manifest.sha256",
    ROOT / "output/tables/phase6tm-public-citation-repair.csv",
    ROOT / "output/call-graphs/phase6tm-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6tm-control-surfaces.md",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def read_rows(path: Path, family: str) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            return [], [f"{path}: missing CSV header"]
        rows: list[dict[str, str]] = []
        for number, raw in enumerate(reader, start=2):
            extras = raw.pop(None, None)
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row["surface_family"] = family
            row["source_csv"] = str(path.relative_to(ROOT))
            row["source_sha256"] = sha(path)
            if extras:
                warnings.append(f"{path.relative_to(ROOT)}:{number}: extra_fields={len(extras)}")
                row["csv_parse_warning"] = f"extra_fields={len(extras)}"
            rows.append(row)
        return rows, warnings


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
        print("outputs:", ", ".join(str(path.relative_to(ROOT)) for path in OUTPUTS))
        return

    inputs = [path for pair in INPUTS.values() for path in pair] + list(CONTEXT)
    missing = [str(path.relative_to(ROOT)) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))
    existing = [str(path.relative_to(ROOT)) for path in OUTPUTS if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite output(s):\n" + "\n".join(existing))

    all_rows: list[dict[str, str]] = []
    warnings: list[str] = []
    manifest: list[str] = []
    input_lines: list[str] = []
    evidence_blocks: list[str] = []
    for family, (report_path, ledger_path) in INPUTS.items():
        report_hash, ledger_hash = sha(report_path), sha(ledger_path)
        manifest.extend(
            [
                f"{report_hash}  {report_path.relative_to(ROOT)}",
                f"{ledger_hash}  {ledger_path.relative_to(ROOT)}",
            ]
        )
        rows, row_warnings = read_rows(ledger_path, family)
        warnings.extend(row_warnings)
        all_rows.extend(rows)
        input_lines.append(
            f"- **{family}:** `{report_path.relative_to(ROOT)}` ({report_hash}); "
            f"`{ledger_path.relative_to(ROOT)}` ({ledger_hash}); {len(rows)} row(s)."
        )
        evidence_blocks.append(
            f"## {family}\n\nReport SHA-256: `{report_hash}`\n\n"
            f"CSV SHA-256: `{ledger_hash}`\n\n"
            f"Sources: `{report_path.relative_to(ROOT)}`, `{ledger_path.relative_to(ROOT)}`"
        )
    context_hashes = [(path, sha(path)) for path in CONTEXT]
    manifest.extend(
        f"{digest}  {path.relative_to(ROOT)}" for path, digest in context_hashes
    )

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

    ota_rows: list[dict[str, str]] = []
    with INPUTS["6TM-C OTA citation repair"][1].open(
        newline="", encoding="utf-8", errors="replace"
    ) as stream:
        reader = csv.DictReader(stream)
        ota_fields = reader.fieldnames or []
        ota_rows = list(reader)
    citation = io.StringIO(newline="")
    citation_writer = csv.DictWriter(
        citation, fieldnames=ota_fields, extrasaction="ignore", lineterminator="\n"
    )
    citation_writer.writeheader()
    citation_writer.writerows(ota_rows)

    warning_text = (
        "- None detected.\n" if not warnings else "\n".join(f"- `{item}`" for item in warnings) + "\n"
    )
    report = "# Phase 6TM host-only provenance closure\n\n"
    report += (
        "This bundle extends Phase 6TJ–TL with the H2 custom-permission provenance check, "
        "the ION loader/process static graph, and the corrected public citation map for the "
        "PS7331 OTA evidence. It does not turn a capability, exported component, library "
        "caller, or recovery writer into proof of low-privilege reachability.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "Host-only analysis was used. No device, Binder bind/call, `service call`, driver "
        "open/ioctl, Root/exploit, OTA/recovery/sideload/flash, reboot, package/settings "
        "mutation, or partition write was performed.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## H2 permission result — confirmed boundary\n\n"
        "The exact-build H2 XML-tree declares `com.amazon.alta.h2clientservice.permission.BIND_SERVICE` "
        "with raw `protectionLevel=0x2` (`signature`), and the exported H2 service references it. "
        "The custom holder, grant, and external production caller remain `UNKNOWN`; UID, placement, "
        "platform grants, and package signing digest do not prove custom-permission ownership. The "
        "recovered static path reaches user/profile lifecycle sinks but not HOME or PackageManager "
        "component-state selection.\n\n"
        "Classification: `DECLARATION_CONFIRMED_PROVENANCE_OPEN`; low-privilege reachability is "
        "not established.\n\n"
        "## ION loader result — bounded static evidence\n\n"
        "The ION worker output is accepted only to the level supported by its exact-build loader, "
        "manifest, ELF, and SELinux evidence. A complete process→loaded library→device node→ioctl "
        "→privileged effect chain is required before any driver capability is treated as reachable. "
        "Missing loader, caller, permission, or downstream-effect edges remain `UNKNOWN`. No HOME, "
        "package-state, credential, OTA, or root effect is inferred from library presence alone.\n\n"
        "## OTA citation result — provenance correction\n\n"
        "The canonical citation map separates public committed manifests and derived static outputs "
        "from local-only raw OTA/extracted paths. TG-05 uses the `phase6mk...-04` registration table "
        "and TG-06 keeps selected-functions, direct-call-edges, and summary hashes distinct. These "
        "corrections change citation scope, not device behavior or caller reachability.\n\n"
        "## Evidence acceptance rule\n\n"
        "A positive privilege or replacement finding requires caller → gate → identity/user scope → "
        "exact sink. `UNKNOWN` is not a negative finding, but it is also not permission to invoke an "
        "unverified Binder, service, driver, OTA, or boot path.\n\n"
        "## CSV validation\n\n"
        f"Integrated rows: `{len(all_rows)}`; OTA citation rows: `{len(ota_rows)}`; parse warnings: `{len(warnings)}`.\n\n"
        "Warnings:\n" + warning_text
    )
    evidence = "# Phase 6TM evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Context\n\n" + "\n".join(
        f"- `{path.relative_to(ROOT)}`: `{digest}`" for path, digest in context_hashes
    ) + "\n\n"
    evidence += "## Acceptance labels\n\n"
    evidence += (
        "- `CONFIRMED`: exact declaration, hash, or committed artifact bytes are directly shown.\n"
        "- `STRONG_STATIC`: a bounded static edge is joined, but runtime or external caller is not.\n"
        "- `UNKNOWN`: one or more caller, holder, loader, policy, or effect edges are missing.\n"
        "- `LOCAL_ONLY`: raw path is preserved locally and is not claimed as public-tree content.\n"
    )

    graph = """flowchart LR
  H["H2ClientService"] --> P["custom BIND_SERVICE\nprotectionLevel=signature"]
  P --> U["user/profile lifecycle\nstatic sink"]
  P -. "holder/grant/caller UNKNOWN" .-> X["No low-privilege claim"]
  I["ION libraries"] --> L["loader / manifest / ELF evidence"]
  L -. "process→node→ioctl→effect incomplete" .-> Y["bounded static only"]
  O["PS7331 OTA records"] --> C["canonical citation map"]
  C -. "raw archive/extracted paths LOCAL_ONLY" .-> R["scope corrected"]
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f03;
  class H,P,U,I,L,O,C,R bound;
  class X,Y unknown;
"""
    graph_md = "# Phase 6TM control-surface graph\n\n```mermaid\n" + graph + "```\n"

    for path, content in zip(
        OUTPUTS,
        (
            report,
            evidence,
            matrix.getvalue(),
            "\n".join(manifest) + "\n",
            citation.getvalue(),
            graph,
            graph_md,
        ),
    ):
        write_new(path, content, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(all_rows)} ota_rows={len(ota_rows)} warnings={len(warnings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
