#!/usr/bin/env python3
"""Build a reproducible, host-only Phase 6SN–6SQ evidence bundle.

This script consumes four delegated worker reports and their CSV ledgers.  It
does not contact a device, execute Binder calls, inspect live state, or mutate
the repository's existing evidence.  Existing output files are never
overwritten unless --force is explicitly supplied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

INPUTS = {
    "6SN permission-holder/caller": (
        ROOT / "work/luna_worker_phase6sn_permission_caller_20260810.md",
        ROOT / "work/luna_worker_phase6sn_permission_caller_20260810.csv",
    ),
    "6SO native driver caller": (
        ROOT / "work/luna_worker_phase6so_driver_native_20260810.md",
        ROOT / "work/luna_worker_phase6so_driver_native_20260810.csv",
    ),
    "6SP OTA/recovery native boundary": (
        ROOT / "work/luna_worker_phase6sp_ota_native_20260810.md",
        ROOT / "work/luna_worker_phase6sp_ota_native_20260810.csv",
    ),
    "6SQ HOME/PackageManager writer": (
        ROOT / "work/luna_worker_phase6sq_home_pms_writer_20260810.md",
        ROOT / "work/luna_worker_phase6sq_home_pms_writer_20260810.csv",
    ),
}

OUTPUTS = (
    ROOT / "findings/phase-6sn-sq-report.md",
    ROOT / "findings/phase-6sn-sq-evidence-index.md",
    ROOT / "output/tables/phase6sn-sq-control-surface.csv",
    ROOT / "output/tables/phase6sn-sq-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6sn-sq-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6sn-sq-control-surfaces.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def load_csv(path: Path, family: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        rows: list[dict[str, str]] = []
        for row in reader:
            normalized = {key: (value or "").strip() for key, value in row.items()}
            normalized["surface_family"] = family
            normalized["source_csv"] = str(path.relative_to(ROOT))
            normalized["source_sha256"] = sha256(path)
            rows.append(normalized)
        return rows


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> None:
    if args.dry_run:
        print("host-only dry run; no outputs written")
        for family, (markdown, ledger) in INPUTS.items():
            print(f"{family}: {markdown.relative_to(ROOT)}, {ledger.relative_to(ROOT)}")
        return

    missing = [str(path) for pair in INPUTS.values() for path in pair if not path.is_file()]
    if missing:
        raise SystemExit("missing worker input(s):\n" + "\n".join(missing))

    if not args.force:
        existing = [str(path) for path in OUTPUTS if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite existing output(s):\n" + "\n".join(existing))

    all_rows: list[dict[str, str]] = []
    manifest_lines = [
        "# Phase 6SN–6SQ input manifest",
        f"generated_utc={datetime.now(timezone.utc).isoformat()}",
        f"git_head={git_head()}",
        "device_contacted=false",
        "device_mutation=false",
        "binder_transaction_sent=false",
        "driver_open_or_ioctl=false",
        "ota_or_recovery_executed=false",
        "",
    ]
    evidence_blocks: list[str] = []
    report_inputs: list[str] = []

    for family, (markdown, ledger) in INPUTS.items():
        md_hash = sha256(markdown)
        csv_hash = sha256(ledger)
        manifest_lines.extend(
            [
                f"{md_hash}  {markdown.relative_to(ROOT)}",
                f"{csv_hash}  {ledger.relative_to(ROOT)}",
            ]
        )
        rows = load_csv(ledger, family)
        all_rows.extend(rows)
        report_inputs.append(
            f"- **{family}:** `{markdown.relative_to(ROOT)}` ({md_hash}); "
            f"`{ledger.relative_to(ROOT)}` ({csv_hash}); {len(rows)} ledger row(s)."
        )
        evidence_blocks.append(
            "## " + family + "\n\n"
            f"Markdown SHA-256: `{md_hash}`\n\n"
            f"CSV SHA-256: `{csv_hash}`\n\n"
            f"Source: `{markdown.relative_to(ROOT)}`; `{ledger.relative_to(ROOT)}`\n\n"
            "The worker report is the authoritative interpretation for this surface; "
            "the CSV is the row-level ledger."
        )

    fieldnames: list[str] = []
    for row in all_rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    fieldnames = ["surface_family", "source_csv", "source_sha256"] + [
        key for key in fieldnames if key not in {"surface_family", "source_csv", "source_sha256"}
    ]

    import io

    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in all_rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})

    report = """# Phase 6SN–6SQ broad privilege-surface closure\n\n"""
    report += (
        "This is a host-only integration of four bounded static reviews. It does not "
        "claim a privilege path merely because a permission, service, native symbol, "
        "or sink exists. A positive route requires an evidence-complete caller → gate → "
        "identity/user scope → state or capability sink chain.\n\n"
        f"Integration HEAD at generation: `{git_head()}`.\n\n"
        "## Safety boundary\n\n"
        "No ADB, Binder transaction, service call, driver open/ioctl, OTA/recovery "
        "execution, reboot, package/settings mutation, Root, exploit, or partition "
        "write was performed. Existing device evidence and raw worker files were not "
        "overwritten.\n\n"
        "## Inputs\n\n" + "\n".join(report_inputs) + "\n\n"
        "## Integrated interpretation\n\n"
        "- **Permission/caller surface:** declaration, holder, grant, and production "
        "caller are separate claims. A `signature|privileged` declaration or a "
        "published Binder service is not an ordinary-app or shell capability.\n"
        "- **Native drivers:** source/config strings and a shipped node do not establish "
        "a caller. A positive driver route requires an exact shipped native caller and "
        "policy/permission edge; unresolved edges remain `UNKNOWN`.\n"
        "- **OTA/recovery:** privileged write capability is not a safe shell route and "
        "is not a HOME/package-state bypass. Parser or indirect-call gaps remain static "
        "unknowns and are not tested with crafted input.\n"
        "- **HOME/PMS writers:** a writer must be shown to target User 0 and the Fire "
        "component/preferred record. Child/profile-scoped writers, OOBE setup writers, "
        "metadata stores, and process/window sinks are not equivalent.\n\n"
        "## Evidence status rule\n\n"
        "`Confirmed` means directly shown by the cited exact-build source/artifact; "
        "`Strong evidence` means a bounded edge is shown but runtime or a downstream "
        "condition remains; `Unknown` means the corpus does not establish the edge; "
        "`Disproved` means the cited evidence contradicts the hypothesis. No row is "
        "upgraded solely by naming, exported status, or a missing local check.\n\n"
        "## Remaining safe work\n\n"
        "Only additional exact-build corpus completeness, source-to-DEX/native mapping, "
        "and naturally obtained read-only captures are justified. Unknown Binder "
        "transactions, driver ioctls, OTA/recovery execution, package-state changes, "
        "and exploit/root testing remain out of scope for this safe closure.\n"
    )

    evidence = "# Phase 6SN–6SQ evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n"

    mermaid = """flowchart LR
  P["Permission declaration / service registration"] --> H["Holder / grant / caller inventory"]
  H --> G["Caller and permission gate"]
  G --> U["Identity and user-scope propagation"]
  U --> S["State or capability sink"]
  N["Exact source/config/native marker"] --> D["Shipped node and policy"]
  D --> C["Exact native caller"]
  C --> G
  O["OTA parser / verifier"] --> W["Privileged updater write boundary"]
  W -. "not a shell route" .-> X["No safe direct execution claim"]
  S --> Q["HOME/package/component effect only if exact target is proven"]
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f03;
  classDef boundary fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  class H,G,U,S,C,Q unknown;
  class P,N,D,O,W,X boundary;
"""
    mermaid_md = "# Phase 6SN–6SQ control-surface graph\n\n```mermaid\n" + mermaid + "```\n\n" + (
        "Text interpretation: every route requires a proven caller, gate, identity, "
        "user scope, and exact sink. Dashed OTA edge is intentionally marked as not a "
        "safe shell route.\n"
    )

    write_new(OUTPUTS[0], report, args.force)
    write_new(OUTPUTS[1], evidence, args.force)
    write_new(OUTPUTS[2], csv_buffer.getvalue(), args.force)
    write_new(OUTPUTS[3], "\n".join(manifest_lines) + "\n", args.force)
    write_new(OUTPUTS[4], mermaid, args.force)
    write_new(OUTPUTS[5], mermaid_md, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(all_rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="list inputs without writing")
    parser.add_argument("--force", action="store_true", help="explicitly permit replacing this bundle")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
