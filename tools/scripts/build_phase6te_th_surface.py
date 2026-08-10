#!/usr/bin/env python3
"""Integrate Phase 6TE–TH host-only evidence without contacting a device."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6TE existing test audit": (
        ROOT / "work/luna_worker_phase6te_test_audit_20260810.md",
        ROOT / "work/luna_worker_phase6te_test_audit_20260810.csv",
    ),
    "6TF IPC residual": (
        ROOT / "work/luna_worker_phase6tf_ipc_residual_20260810.md",
        ROOT / "work/luna_worker_phase6tf_ipc_residual_20260810.csv",
    ),
    "6TG OTA/source scope": (
        ROOT / "work/luna_worker_phase6tg_ota_scope_20260810.md",
        ROOT / "work/luna_worker_phase6tg_ota_scope_20260810.csv",
    ),
    "6TH kernel/native residual": (
        ROOT / "work/luna_worker_phase6th_kernel_residual_20260810.md",
        ROOT / "work/luna_worker_phase6th_kernel_residual_20260810.csv",
    ),
}
DEVICE_SUMMARY = ROOT / "findings/phase-6ti-readonly-snapshot.md"
DEVICE_TABLE = ROOT / "output/tables/phase6ti-readonly-state.csv"
OUTPUTS = (
    ROOT / "findings/phase-6te-th-report.md",
    ROOT / "findings/phase-6te-th-evidence-index.md",
    ROOT / "output/tables/phase6te-th-control-surface.csv",
    ROOT / "output/tables/phase6te-th-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6te-th-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6te-th-control-surfaces.md",
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
        out: list[dict[str, str]] = []
        for raw in reader:
            extras = raw.pop(None, None)
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row["surface_family"] = family
            row["source_csv"] = str(path.relative_to(ROOT))
            row["source_sha256"] = sha(path)
            if extras:
                row["csv_parse_warning"] = f"extra_fields={len(extras)}"
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
        print(f"device summary: {DEVICE_SUMMARY.relative_to(ROOT)}")
        print(f"device table: {DEVICE_TABLE.relative_to(ROOT)}")
        return

    inputs = [path for pair in INPUTS.values() for path in pair] + [DEVICE_SUMMARY, DEVICE_TABLE]
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

    device_summary_hash, device_table_hash = sha(DEVICE_SUMMARY), sha(DEVICE_TABLE)
    manifest.extend([f"{device_summary_hash}  {DEVICE_SUMMARY.relative_to(ROOT)}", f"{device_table_hash}  {DEVICE_TABLE.relative_to(ROOT)}"])

    fields: list[str] = []
    for row in all_rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    fields = ["surface_family", "source_csv", "source_sha256"] + [
        key for key in fields if key not in {"surface_family", "source_csv", "source_sha256"}
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in all_rows:
        writer.writerow({key: row.get(key, "") for key in fields})

    report = "# Phase 6TE–TH host-only continuation\n\n"
    report += (
        "This bundle integrates the delegated existing-test audit, Amazon IPC residual search, "
        "PS7331 OTA/source audit, and kernel/native residual audit. It also records a fresh "
        "serial-bound read-only state snapshot. It does not infer low-privilege reachability "
        "from capability, exported status, source/config presence, or an unresolved caller.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "The device snapshot used only getprop, read-only dumpsys, resolver queries, package/user/"
        "service/overlay lists, and settings list. No package/settings mutation, Binder transaction, "
        "driver operation, Root/exploit, OTA/recovery execution, reboot, or partition write was performed.\n\n"
        "## Delegated inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "## Current device state\n\n"
        f"Redacted summary: `{DEVICE_SUMMARY.relative_to(ROOT)}` ({device_summary_hash}); "
        f"state table: `{DEVICE_TABLE.relative_to(ROOT)}` ({device_table_hash}).\n\n"
        "The exact PS7331 device remains `KFTRWI`/`trona`, build `PS7331.4463N`, verified boot "
        "green, and the selected User 0 HOME is `com.amazon.firelauncher/.Launcher` at priority 50. "
        "This is current-state evidence, not a new privilege or replacement result.\n\n"
        "## Acceptance rule\n\n"
        "A positive privilege or replacement finding requires caller → authorization/ownership gate "
        "→ identity and user scope → exact state/capability sink. `UNKNOWN` remains an evidence "
        "boundary. Test-only callers, generated Stub/Proxy code, source-only driver capability, "
        "and recovery-context writers are not ordinary shell/APK routes.\n\n"
        "## Bounded result\n\n"
        "The H2/Amazon user workflow provides exact user creation/removal and per-profile settings "
        "sinks, but its bind permission, external caller and reachability remain unknown; no formal "
        "HOME/package-state sink was found. OTA/recovery writer capability is confirmed in its "
        "privileged context, with no ordinary caller chain. Kernel/native residuals retain only the "
        "library-level ION positive; other driver surfaces lack an exact shipped caller and final "
        "policy/effect join. Existing tests confirm User 0 Fire HOME and classify child/foreground "
        "routes as scoped or temporary, not durable User 0 replacement.\n"
    )
    evidence = "# Phase 6TE–TH evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += (
        f"## 6TI read-only snapshot\n\nSummary SHA-256: `{device_summary_hash}`\n\n"
        f"Table SHA-256: `{device_table_hash}`\n\nSources: `{DEVICE_SUMMARY.relative_to(ROOT)}`, `{DEVICE_TABLE.relative_to(ROOT)}`\n"
    )
    graph = """flowchart LR
  T["Saved tests / child / foreground evidence"] --> G["User and package/HOME guards"]
  R["Read-only PS7331 snapshot"] --> H["Fire HOME priority 50"]
  I["Alta H2 Binder workflow"] --> P["Bind gate / external caller UNKNOWN"]
  P --> U["User/profile and Settings sinks"]
  O["OTA/update-binary"] --> W["Recovery-context partition writer"]
  W -. "no ordinary caller" .-> X["Bounded capability only"]
  K["Kernel/native surfaces"] --> N["Exact shipped caller missing except ION library-level"]
  T -. "no User 0 formal replacement" .-> H
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f03;
  class T,R,H,I,U,O,W,X,K,N bound;
  class P unknown;
"""
    graph_md = "# Phase 6TE–TH control-surface graph\n\n```mermaid\n" + graph + "```\n"

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
