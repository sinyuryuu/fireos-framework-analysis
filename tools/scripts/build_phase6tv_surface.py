#!/usr/bin/env python3
"""Integrate Phase 6TO–TQ static audits, 6TR reconciliation and 6TU state."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6TO IPC sink audit": (
        ROOT / "work/luna_worker_phase6to_ipc_sink_audit_20260810.md",
        ROOT / "work/luna_worker_phase6to_ipc_sink_audit_20260810.csv",
    ),
    "6TP OTA writer audit": (
        ROOT / "work/luna_worker_phase6tp_ota_writer_audit_20260810.md",
        ROOT / "work/luna_worker_phase6tp_ota_writer_audit_20260810.csv",
    ),
    "6TQ driver inventory": (
        ROOT / "work/luna_worker_phase6tq_driver_inventory_20260810.md",
        ROOT / "work/luna_worker_phase6tq_driver_inventory_20260810.csv",
    ),
    "6TR test reconciliation": (
        ROOT / "work/luna_worker_phase6tr_test_reconciliation_20260810.md",
        ROOT / "work/luna_worker_phase6tr_test_reconciliation_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6tm-report.md",
    ROOT / "findings/phase-6tm-evidence-index.md",
    ROOT / "output/tables/phase6tm-control-surface.csv",
    ROOT / "findings/phase-6tu-readonly-snapshot.md",
    ROOT / "output/tables/phase6tu-readonly-state.csv",
)
OUTPUTS = (
    ROOT / "findings/phase-6tv-report.md",
    ROOT / "findings/phase-6tv-evidence-index.md",
    ROOT / "output/tables/phase6tv-control-surface.csv",
    ROOT / "output/tables/phase6tv-input-manifest.sha256",
    ROOT / "output/tables/phase6tv-test-reconciliation.csv",
    ROOT / "output/call-graphs/phase6tv-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6tv-control-surfaces.md",
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def read_rows(path: Path, family: str) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream, skipinitialspace=True)
        if not reader.fieldnames:
            return [], [f"{path.relative_to(ROOT)}: missing header"]
        rows: list[dict[str, str]] = []
        for line_number, raw in enumerate(reader, start=2):
            extras = raw.pop(None, None)
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row["surface_family"] = family
            row["source_csv"] = str(path.relative_to(ROOT))
            row["source_sha256"] = sha(path)
            if extras:
                warning = f"{path.relative_to(ROOT)}:{line_number}: extra_fields={len(extras)}"
                warnings.append(warning)
                row["csv_parse_warning"] = f"extra_fields={len(extras)}"
            rows.append(row)
        return rows, warnings


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

    inputs = [path for pair in INPUTS.values() for path in pair] + list(CONTEXT)
    missing = [str(path.relative_to(ROOT)) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))
    existing = [str(path.relative_to(ROOT)) for path in OUTPUTS if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite output(s):\n" + "\n".join(existing))

    rows: list[dict[str, str]] = []
    warnings: list[str] = []
    manifest: list[str] = []
    input_lines: list[str] = []
    evidence_blocks: list[str] = []
    for family, (report, ledger) in INPUTS.items():
        report_hash, ledger_hash = sha(report), sha(ledger)
        manifest.extend(
            [
                f"{report_hash}  {report.relative_to(ROOT)}",
                f"{ledger_hash}  {ledger.relative_to(ROOT)}",
            ]
        )
        family_rows, family_warnings = read_rows(ledger, family)
        rows.extend(family_rows)
        warnings.extend(family_warnings)
        input_lines.append(
            f"- **{family}:** `{report.relative_to(ROOT)}` ({report_hash}); "
            f"`{ledger.relative_to(ROOT)}` ({ledger_hash}); {len(family_rows)} row(s)."
        )
        evidence_blocks.append(
            f"## {family}\n\nReport SHA-256: `{report_hash}`\n\n"
            f"CSV SHA-256: `{ledger_hash}`\n\n"
            f"Sources: `{report.relative_to(ROOT)}`, `{ledger.relative_to(ROOT)}`"
        )
    context_hashes = [(path, sha(path)) for path in CONTEXT]
    manifest.extend(f"{digest}  {path.relative_to(ROOT)}" for path, digest in context_hashes)

    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    fields = ["surface_family", "source_csv", "source_sha256"] + [
        key for key in fields if key not in {"surface_family", "source_csv", "source_sha256"}
    ]
    matrix = io.StringIO(newline="")
    writer = csv.DictWriter(matrix, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fields})

    reconciliation = io.StringIO(newline="")
    source_csv = INPUTS["6TR test reconciliation"][1]
    with source_csv.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream, skipinitialspace=True)
        source_fields = reader.fieldnames or []
        reconciliation_writer = csv.DictWriter(
            reconciliation, fieldnames=source_fields, extrasaction="ignore", lineterminator="\n"
        )
        reconciliation_writer.writeheader()
        reconciliation_writer.writerows(reader)

    warning_text = "- None detected.\n" if not warnings else "\n".join(f"- `{w}`" for w in warnings) + "\n"
    report = "# Phase 6TV host-only control-surface and test reconciliation\n\n"
    report += (
        "This bundle integrates Phase 6TO IPC sink audit, Phase 6TP OTA writer audit, "
        "Phase 6TQ GPL/exact-image driver inventory, Phase 6TR historical-test reconciliation, "
        "and the fresh Phase 6TU read-only device summary. It preserves the caller → gate → "
        "identity/user scope → exact sink acceptance rule.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No Binder/service call, driver `open/ioctl`, proc/sysfs/debugfs write, OTA construction "
        "or execution, recovery/sideload/flash, Root/exploit, reboot, package/settings mutation, "
        "Fire Launcher mutation, or partition write was performed. Phase 6TU used only read-only "
        "ADB queries with the specified device serial; raw settings remain local.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## IPC result\n\n"
        "The bounded exact-build corpus found no confirmed chain from an ordinary app/shell caller "
        "through an accepted permission/identity gate to a User-0 HOME or Fire package-state sink. "
        "Amazon Activity/DevicePolicy/Window/Package services show scoped permissions, callbacks, "
        "metadata or policy effects. The AmazonUserManager KFT setter is child/profile-scoped in the "
        "available evidence. Exported components and signature declarations are not treated as bugs.\n\n"
        "## OTA result\n\n"
        "The saved updater script and native analysis show privileged target/write capabilities and "
        "cache helpers, but caller authentication, complete canonicalization/symlink data flow and "
        "runtime recovery reachability remain `UNKNOWN`. No payload or bypass is produced.\n\n"
        "## Driver result\n\n"
        "GPL source and exact-image metadata close selected read-only Amazon proc nodes, policy "
        "labels and several MediaTek registration surfaces. ION, M4U, MDP, TCPC, input, RPMB, "
        "debugfs and `amzn_drv_test` retain missing shipped/caller/policy/effect edges. No driver "
        "surface reaches PackageManager, ActivityManager, HOME or Fire Launcher in this corpus.\n\n"
        "## Existing-test result\n\n"
        "The reconciliation matrix records 25 historical rows. Priority APK, ordinary set-home, "
        "Fire package/component mutation, child/KFT/private Binder, accessibility replay, driver "
        "ioctl, OTA/recovery and root/partition routes are marked duplicate, closed, refused or "
        "not safe to replay. Historical rollback guards are evidence for those runs only.\n\n"
        "## Current read-only state\n\n"
        "The Phase 6TU redacted summary records PS7331.4463N / KFTRWI / trona, Android 9/API 28, "
        "security patch 2024-08-01, SELinux Enforcing, verified boot green, two users, and HOME "
        "resolver result `com.amazon.firelauncher/.Launcher` with effective priority 50. This is "
        "a current read-only observation, not a new workaround or privilege result.\n\n"
        "## Verdict\n\n"
        "No new safe evidence justifies a Root claim, Fire Launcher disablement, a shell-to-system "
        "confused-deputy claim, an OTA bypass, or a driver exploit. Remaining `UNKNOWN` rows are "
        "research gaps, not proof of absence.\n\n"
        f"Integrated rows: `{len(rows)}`; parse warnings: `{len(warnings)}`.\n\n"
        "Warnings:\n" + warning_text
    )
    evidence = "# Phase 6TV evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Context\n\n" + "\n".join(
        f"- `{path.relative_to(ROOT)}`: `{digest}`" for path, digest in context_hashes
    ) + "\n\n## Labels\n\n"
    evidence += (
        "- `CONFIRMED`: exact static declaration or read-only observation is directly supported.\n"
        "- `STRONG_STATIC`: bounded caller/gate/sink edge, with at least one missing external/runtime edge.\n"
        "- `UNKNOWN`: caller, loader, identity, policy, user scope or downstream effect is missing.\n"
        "- `NOT_A_SINK`/`ABSENT`/`LOCAL_ONLY`: scope classifications, not exploit conclusions.\n"
    )
    graph = """flowchart LR
  I["IPC services"] --> IG["permission / helper gates"]
  IG -. "no ordinary caller→User-0 HOME sink" .-> IX["bounded negative"]
  O["OTA script/native writer"] --> OW["privileged write capability"]
  OW -. "auth/canonicalization/runtime UNKNOWN" .-> OX["no bypass claim"]
  D["GPL/custom drivers"] --> DP["nodes/policy/ELF evidence"]
  DP -. "caller/effect incomplete" .-> DX["no LPE/HOME claim"]
  T["historical tests"] --> R["25-row reconciliation"]
  R -. "duplicates/refused/replay excluded" .-> RX["preserve rollback evidence"]
  S["Phase 6TU read-only state"] --> H["Fire Launcher HOME priority 50"]
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class I,IG,O,OW,D,DP,T,R,S,H bound;
  class IX,OX,DX,RX unknown;
"""
    graph_md = "# Phase 6TV control-surface graph\n\n```mermaid\n" + graph + "```\n"

    for path, content in zip(
        OUTPUTS,
        (
            report,
            evidence,
            matrix.getvalue(),
            "\n".join(manifest) + "\n",
            reconciliation.getvalue(),
            graph,
            graph_md,
        ),
    ):
        write_new(path, content, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(rows)} warnings={len(warnings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
