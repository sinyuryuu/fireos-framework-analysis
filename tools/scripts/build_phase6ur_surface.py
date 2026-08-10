#!/usr/bin/env python3
"""Integrate Phase 6UN–UQ artifact-completeness and caller/sink audits."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6UN native node join": (
        ROOT / "work/luna_worker_phase6un_native_node_join_20260810.md",
        ROOT / "work/luna_worker_phase6un_native_node_join_20260810.csv",
    ),
    "6UO OTA verifier/handoff": (
        ROOT / "work/luna_worker_phase6uo_ota_verifier_handoff_20260810.md",
        ROOT / "work/luna_worker_phase6uo_ota_verifier_handoff_20260810.csv",
    ),
    "6UP ASP/prewarm closure": (
        ROOT / "work/luna_worker_phase6up_asp_prewarm_closure_20260810.md",
        ROOT / "work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv",
    ),
    "6UQ fosinit completeness": (
        ROOT / "work/luna_worker_phase6uq_fosinit_completeness_20260810.md",
        ROOT / "work/luna_worker_phase6uq_fosinit_completeness_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6um-report.md",
    ROOT / "output/tables/phase6um-control-surface.csv",
    ROOT / "findings/phase-6ui-readonly-snapshot.md",
    ROOT / "output/tables/phase6ui-readonly-state.csv",
    ROOT / "findings/phase-6py-service-state-exported-closure.md",
    ROOT / "findings/phase-6nj-followup-synthesis.md",
)
OUTPUTS = (
    ROOT / "findings/phase-6ur-report.md",
    ROOT / "findings/phase-6ur-evidence-index.md",
    ROOT / "output/tables/phase6ur-control-surface.csv",
    ROOT / "output/tables/phase6ur-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6ur-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6ur-control-surfaces.md",
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


def rows(path: Path, family: str) -> tuple[list[dict[str, str]], list[str], list[str]]:
    warnings: list[str] = []
    notes: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream, skipinitialspace=True)
        if not reader.fieldnames:
            return [], [f"{path.relative_to(ROOT)}: missing header"]
        result: list[dict[str, str]] = []
        for line_number, raw in enumerate(reader, start=2):
            extras = raw.pop(None, None)
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row.update(surface_family=family, source_csv=str(path.relative_to(ROOT)), source_sha256=sha(path))
            if extras:
                note = f"{path.relative_to(ROOT)}:{line_number}: extra_fields={len(extras)}"
                # The 6UQ ledger uses INPUT_HASH rows as provenance records and
                # places a human-readable description in an additional column.
                # Preserve the raw file/hash and classify this as a source-format
                # note, not an evidence-row warning. Any extra field on a normal
                # evidence row remains a warning.
                if row.get("edge", "").startswith("INPUT_HASH:") or row.get("edge", "") == "corpus completeness":
                    notes.append(note)
                    row["csv_parse_note"] = f"extra_fields={len(extras)} on provenance row"
                else:
                    warnings.append(note)
                    row["csv_parse_warning"] = f"extra_fields={len(extras)}"
            result.append(row)
        return result, warnings, notes


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite output: {path}")
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

    all_inputs = [path for pair in INPUTS.values() for path in pair] + list(CONTEXT)
    missing = [str(path.relative_to(ROOT)) for path in all_inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))
    existing = [str(path.relative_to(ROOT)) for path in OUTPUTS if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite output(s):\n" + "\n".join(existing))

    integrated: list[dict[str, str]] = []
    warnings: list[str] = []
    notes: list[str] = []
    manifest: list[str] = []
    input_lines: list[str] = []
    evidence_blocks: list[str] = []
    for family, (report, ledger) in INPUTS.items():
        report_hash, ledger_hash = sha(report), sha(ledger)
        manifest.extend([f"{report_hash}  {report.relative_to(ROOT)}", f"{ledger_hash}  {ledger.relative_to(ROOT)}"])
        family_rows, family_warnings, family_notes = rows(ledger, family)
        integrated.extend(family_rows)
        warnings.extend(family_warnings)
        notes.extend(family_notes)
        input_lines.append(
            f"- **{family}:** `{report.relative_to(ROOT)}` ({report_hash}); `{ledger.relative_to(ROOT)}` "
            f"({ledger_hash}); {len(family_rows)} row(s)."
        )
        evidence_blocks.append(
            f"## {family}\n\nReport SHA-256: `{report_hash}`\n\nCSV SHA-256: `{ledger_hash}`\n\n"
            f"Sources: `{report.relative_to(ROOT)}`, `{ledger.relative_to(ROOT)}`"
        )
    context_hashes = [(path, sha(path)) for path in CONTEXT]
    manifest.extend(f"{digest}  {path.relative_to(ROOT)}" for path, digest in context_hashes)

    fieldnames: list[str] = []
    for row in integrated:
        for field in row:
            if field not in fieldnames:
                fieldnames.append(field)
    fieldnames = ["surface_family", "source_csv", "source_sha256"] + [
        field for field in fieldnames if field not in {"surface_family", "source_csv", "source_sha256"}
    ]
    matrix = io.StringIO(newline="")
    writer = csv.DictWriter(matrix, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in integrated:
        writer.writerow({field: row.get(field, "") for field in fieldnames})

    warning_text = "- None detected.\n" if not warnings else "\n".join(f"- `{item}`" for item in warnings) + "\n"
    report = "# Phase 6UR — caller/sink and artifact-completeness closure\n\n"
    report += (
        "This host-only bundle follows Phase 6UM by closing four residual evidence groups: native "
        "node joins, OTA verifier/handoff, ASP/prewarm caller/sink analysis, and fosinit/classloader "
        "completeness. The acceptance rule remains caller → gate → identity/user scope → exact sink "
        "→ observed effect.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No Binder or service transaction, driver/node/ioctl operation, OTA/recovery/updater execution, "
        "malformed input, package/settings mutation, user provisioning, reboot, Root/exploit attempt, "
        "Fire Launcher mutation, or partition write was performed.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## Findings\n\n"
        "### Native node joins — **已證實 capability / 待驗證 reachability**\n\n"
        "CMDQ, ION/MTK ION and Amazon-LD are selected or registered in the preserved source/config "
        "scope. The exact shipped object/module, DT/init instance, ueventd/file_contexts/vendor-TE "
        "policy and native client edges are not all present. Source-declared mode or an ioctl fops "
        "path is not proof that an ordinary app can reach a state-changing effect. No PackageManager, "
        "HOME or privilege-transition sink was found in this join.\n\n"
        "### OTA verifier/handoff — **已證實 gates and recovery capability / 待驗證 handoff**\n\n"
        "The signed PS7331 block OTA has product/build/timestamp checks, certificate/recovery-verification "
        "contracts, block verification symbols and fixed partition targets. Native recovery-to-updater "
        "caller identity, AVB/rollback implementation and canonicalization dataflow remain incomplete. "
        "The partition writer is a recovery capability, not an ADB or ordinary-app route.\n\n"
        "### ASP/prewarm — **已證實 bounded runtime boundary / no accepted low-privilege route**\n\n"
        "The tablet ASP branch consumes `ASP_PERMISSION` and the saved shell transaction returned `-13`; "
        "the non-tablet allow branch is cross-build static evidence only. Prewarm shows an ignored "
        "permission result before identity clear and process prewarm, but saved service lookup/dispatch "
        "evidence closes shell reachability on KFTRWI and no package/HOME/settings/root sink is present. "
        "These remain code-review anomalies, not exploit findings.\n\n"
        "### fosinit/classloader — **高可信 bounded completeness / residual static gaps**\n\n"
        "The preserved corpus contains 244 XML entries, 186 listed services and principal Amazon Binder "
        "contracts. Private service lookup is denied to shell in saved enforcing evidence. Several "
        "HOME-adjacent, package/settings-adjacent and OTA callback groups remain source-to-effect gaps, "
        "but no unreviewed ordinary external path to User-0 HOME/package/settings/user/OTA state is "
        "closed. Registration, listing and class presence are not method reachability.\n\n"
        "## Final bounded conclusion\n\n"
        "The remaining surfaces are now classified as protected lifecycle writers, high-impact static "
        "capabilities, or bounded code-review anomalies. No evidence justifies claiming a root path, "
        "confused deputy, Fire Launcher disable route, or formal User-0 HOME replacement. The next "
        "safe work is a finite host-only closure of the seven fosinit residual groups; if that produces "
        "no caller→gate→sink edge, the privileged-control branch should be archived as unclosed rather "
        "than tested by guessing Binder codes, opening drivers, or executing OTA/recovery.\n\n"
        "## Verdict labels\n\n"
        "- **已證實:** exact static edge or saved read-only runtime result within scope.\n"
        "- **高可信推論:** bounded interpretation with named missing edge.\n"
        "- **待驗證:** source/registration/caller/gate/identity/sink or runtime effect is incomplete.\n"
        "- **已排除:** target effect did not occur under recorded conditions.\n"
        "- **因風險拒絕測試:** operation was not performed because it crosses the safety boundary.\n\n"
        f"Integrated rows: `{len(integrated)}`; parse warnings: `{len(warnings)}`; "
        f"source-format notes: `{len(notes)}`.\n\n"
        "Warnings:\n" + warning_text +
        ("\nSource-format notes (raw provenance rows retained unchanged):\n" +
         "\n".join(f"- `{item}`" for item in notes) + "\n" if notes else "")
    )
    evidence = "# Phase 6UR evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += (
        "## Acceptance rules\n\n"
        "- Capability, registration, or missing method-local checks do not prove external reachability.\n"
        "- Runtime service listing is not a valid Binder handle or caller authorization.\n"
        "- `UNKNOWN` is bounded missing evidence, not universal absence.\n"
        "- No row authorizes live Binder, driver, OTA/recovery or exploit execution.\n"
    )
    graph = """flowchart LR
  C["caller"] --> G["permission / SELinux / phase gate"]
  G -. "identity or handle missing" .-> X["No accepted low-privilege effect"]
  N["CMDQ / ION / Amazon-LD"] -. "DT/module/node/policy/client incomplete" .-> X
  O["signed OTA"] --> V["product/build/cert/recovery gates"]
  V --> W["recovery partition/cache writer"]
  W -. "handoff/AVB/caller unknown" .-> X
  A["ASP tablet"] --> A2["ASP_PERMISSION → -EACCES saved result"]
  P["prewarm"] --> P2["clear identity → process prewarm"]
  P2 -. "service lookup/dispatch denied; no HOME/package sink" .-> X
  F["fosinit corpus"] --> F2["services/callbacks/receivers"]
  F2 -. "residual source-to-effect gaps" .-> X
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class G,O,V,W,A,A2,P,P2,F,F2 bound;
  class C,N,X unknown;
"""
    graph_md = "# Phase 6UR control-surface graph\n\n```mermaid\n" + graph + "```\n"

    for path, content in zip(OUTPUTS, (report, evidence, matrix.getvalue(), "\n".join(manifest) + "\n", graph, graph_md)):
        write_new(path, content, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(integrated)} warnings={len(warnings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
