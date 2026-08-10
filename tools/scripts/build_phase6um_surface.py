#!/usr/bin/env python3
"""Integrate Phase 6UI–UL broad privilege-surface audits.

The builder is host-only. It reads preserved worker ledgers and a redacted
read-only state summary; it never contacts the tablet or constructs a Binder,
driver, OTA, recovery, package-state, or root payload.
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
    "6UI IPC privileged sinks": (
        ROOT / "work/luna_worker_phase6ui_ipc_sinks_20260810.md",
        ROOT / "work/luna_worker_phase6ui_ipc_sinks_20260810.csv",
    ),
    "6UJ OTA post-install": (
        ROOT / "work/luna_worker_phase6uj_ota_postinstall_20260810.md",
        ROOT / "work/luna_worker_phase6uj_ota_postinstall_20260810.csv",
    ),
    "6UK GPL driver surface": (
        ROOT / "work/luna_worker_phase6uk_driver_surface_20260810.md",
        ROOT / "work/luna_worker_phase6uk_driver_surface_20260810.csv",
    ),
    "6UL historical test reconciliation": (
        ROOT / "work/luna_worker_phase6ul_test_reconciliation_20260810.md",
        ROOT / "work/luna_worker_phase6ul_test_reconciliation_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6uh-report.md",
    ROOT / "output/tables/phase6uh-control-surface.csv",
    ROOT / "findings/phase-6py-service-state-exported-closure.md",
    ROOT / "output/tables/phase6py-service-state-exported-closure.csv",
    ROOT / "findings/phase-6nj-followup-synthesis.md",
    ROOT / "findings/phase-6ui-readonly-snapshot.md",
    ROOT / "output/tables/phase6ui-readonly-state.csv",
)
OUTPUTS = (
    ROOT / "findings/phase-6um-report.md",
    ROOT / "findings/phase-6um-evidence-index.md",
    ROOT / "output/tables/phase6um-control-surface.csv",
    ROOT / "output/tables/phase6um-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6um-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6um-control-surfaces.md",
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
    for family, (report_path, ledger_path) in INPUTS.items():
        report_hash, ledger_hash = sha(report_path), sha(ledger_path)
        manifest.extend([
            f"{report_hash}  {report_path.relative_to(ROOT)}",
            f"{ledger_hash}  {ledger_path.relative_to(ROOT)}",
        ])
        family_rows, family_warnings = read_rows(ledger_path, family)
        rows.extend(family_rows)
        warnings.extend(family_warnings)
        input_lines.append(
            f"- **{family}:** `{report_path.relative_to(ROOT)}` ({report_hash}); "
            f"`{ledger_path.relative_to(ROOT)}` ({ledger_hash}); {len(family_rows)} row(s)."
        )
        evidence_blocks.append(
            f"## {family}\n\nReport SHA-256: `{report_hash}`\n\n"
            f"CSV SHA-256: `{ledger_hash}`\n\n"
            f"Sources: `{report_path.relative_to(ROOT)}`, `{ledger_path.relative_to(ROOT)}`"
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

    warning_text = "- None detected.\n" if not warnings else "\n".join(f"- `{w}`" for w in warnings) + "\n"
    report = "# Phase 6UM — broad privilege-surface and reachability closure\n\n"
    report += (
        "This host-only bundle broadens the analysis beyond Launcher to Amazon Framework IPC, "
        "the exact PS7331 OTA/update boundary, GPL/native driver capability, and prior-test "
        "reconciliation. It keeps the required security chain explicit: caller → permission/"
        "service-manager gate → identity/user scope → exact sink → observed effect.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No Binder transaction, service call, driver open/ioctl, malformed OTA, updater/recovery "
        "execution, package/settings mutation, user provisioning, reboot, Root/exploit attempt, "
        "Fire Launcher mutation, or partition write was performed. The device contribution is a "
        "serial-bound read-only snapshot; raw settings/service dumps remain local.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## Current device comparator\n\n"
        "The fresh read-only capture identifies PS7331.4463N / KFTRWI / trona, Android 9/API 28, "
        "security patch 2024-08-01, verified boot `green`, SELinux `Enforcing`, two users, and "
        "HOME still resolving to `com.amazon.firelauncher/.Launcher` at effective priority 50. "
        "This is observation evidence only and does not imply that the visible service or any "
        "static sink is shell-reachable.\n\n"
        "## Findings\n\n"
        "### IPC and state sinks — **已證實 / bounded static**\n\n"
        "The IPC inventory confirms concrete sinks: KFT tx3 can write Tahoe/Fire/Launcher3 state "
        "for supplied `UserInfo.id`; DPM/PMS persistent-preferred paths have active-admin/profile-"
        "owner and system-UID gates; PMS enabled-state and preferred-activity setters are real "
        "state sinks. Amazon activity/window/input/package services expose additional effects, but "
        "private-service handle reachability and method authorization remain separate requirements. "
        "No ordinary-app or shell → accepted identity → User-0 state/root path is closed.\n\n"
        "### OTA and post-install — **已證實 capability / no bypass**\n\n"
        "The exact local package is a signed release full block OTA for `trona`, with product/build "
        "gates, block verification symbols, recovery/update-binary dispatch, and direct partition/cache "
        "writers. `BootAfterSystemOTA` is a system-server phase-550 upgrade lifecycle path that resets "
        "setup/OOBE state; the reviewed chain has no ordinary preferred-HOME or Fire-state writer. "
        "Canonicalization, native recovery verification and AVB rollback details remain partially "
        "UNKNOWN. Static partition-writing capability is not an untrusted caller or safe workaround.\n\n"
        "### GPL/native drivers — **已證實 capability / reachability UNKNOWN**\n\n"
        "The exact source/config evidence contains CMDQ, ION/MTK ION, Amazon LD, debugfs/proc/sysfs "
        "and module capability surfaces. `CONFIG_DEVMEM`/`CONFIG_DEVKMEM` are disabled, while the "
        "selected config enables modules, CMDQ, ION and SELinux. Exact linked module/DTB provenance, "
        "device-node modes/labels, native retail caller, and runtime effect are not closed. No node "
        "was opened and no ioctl was issued.\n\n"
        "### Existing tests — **已排除 within recorded conditions**\n\n"
        "The reconciled ledger marks repeated HOME/priority/set-home tests, package/PMS setters, "
        "raw KFT/private Binder attempts, protected OOBE/OTA replay, driver access, provisioning and "
        "root/boot paths as duplicates, bounded negatives, or risk-rejected. A new filename does not "
        "create a new result when build, user topology and rollback state are unchanged.\n\n"
        "## Broad conclusion\n\n"
        "The project now has high-impact capability evidence across IPC, OTA and kernel-native layers, "
        "but the decisive low-privilege caller/authorization/user-scope/effect chain is still missing. "
        "Therefore no compliant evidence supports claiming root, a confused deputy, a Fire Launcher "
        "disable route, or a formal User-0 HOME replacement. The best remaining safe targets are "
        "artifact-completeness joins (module/DT/policy/client), not guessing Binder codes, crafting "
        "OTA input, or invoking driver interfaces.\n\n"
        "## Verdict labels\n\n"
        "- **已證實:** exact build/static sink or read-only device state within the preserved scope.\n"
        "- **高可信推論:** capability or bounded control-flow interpretation with a named missing edge.\n"
        "- **待驗證:** caller, permission, identity, user scope, loader or downstream effect is missing.\n"
        "- **已排除:** the stated effect did not occur in the recorded test conditions.\n"
        "- **因風險拒絕測試:** operation was not performed because it would cross the safety boundary.\n\n"
        f"Integrated rows: `{len(rows)}`; parse warnings: `{len(warnings)}`.\n\n"
        "Warnings:\n" + warning_text
    )
    evidence = "# Phase 6UM evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Acceptance rules\n\n" + (
        "- A capability row is not a reachability or exploit row without caller, gate, identity/user "
        "scope and effect evidence.\n"
        "- A missing method-local check is not evidence that an external caller can obtain a handle.\n"
        "- A static partition writer, driver ioctl or system-server lifecycle writer is not an ADB "
        "workaround.\n"
        "- `UNKNOWN` is a bounded evidence state, not a universal absence claim.\n"
        "- No row authorizes a live private Binder call, driver operation, OTA/recovery action or exploit.\n"
    )
    graph = """flowchart LR
  A["ordinary app / shell"] --> B["ServiceManager / SELinux / permission gate"]
  B -. "caller or handle not closed" .-> X["No accepted privileged route"]
  K["KFT tx3\nUserInfo.id"] --> K2["Tahoe enabled\nFire/Launcher3 disabled\nchild scope"]
  D["DPM/PMS preferred\nadmin + UID 1000 gates"] --> H["preferred/HOME state sink"]
  O["signed block OTA"] --> O2["recovery/update-binary\npartition/cache writers"]
  O2 -. "signature/product/version/phase gates" .-> X
  G["GPL/config driver capability"] --> G2["CMDQ / ION / Amazon LD"]
  G2 -. "DT/module/node/SELinux/caller missing" .-> X
  R["read-only PS7331 snapshot"] --> R2["Fire HOME priority 50\nSELinux Enforcing\nverified boot green"]
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class K,K2,D,H,O,O2,G,G2,R,R2 bound;
  class A,B,X unknown;
"""
    graph_md = "# Phase 6UM control-surface graph\n\n```mermaid\n" + graph + "```\n"

    for path, content in zip(
        OUTPUTS,
        (report, evidence, matrix.getvalue(), "\n".join(manifest) + "\n", graph, graph_md),
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
