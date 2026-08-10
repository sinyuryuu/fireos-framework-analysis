#!/usr/bin/env python3
"""Integrate Phase 6TW–TY host-only provenance closures."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6TW H2 owner/grant": (
        ROOT / "work/luna_worker_phase6tw_h2_owner_grant_20260810.md",
        ROOT / "work/luna_worker_phase6tw_h2_owner_grant_20260810.csv",
    ),
    "6TX amzn_drv_test closure": (
        ROOT / "work/luna_worker_phase6tx_amzn_drv_test_closure_20260810.md",
        ROOT / "work/luna_worker_phase6tx_amzn_drv_test_closure_20260810.csv",
    ),
    "6TY User-0 Fire writer": (
        ROOT / "work/luna_worker_phase6ty_user0_fire_restoration_20260810.md",
        ROOT / "work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6tv-report.md",
    ROOT / "findings/phase-6tv-evidence-index.md",
    ROOT / "output/tables/phase6tv-control-surface.csv",
    ROOT / "findings/phase-6tu-readonly-snapshot.md",
)
OUTPUTS = (
    ROOT / "findings/phase-6tz-report.md",
    ROOT / "findings/phase-6tz-evidence-index.md",
    ROOT / "output/tables/phase6tz-control-surface.csv",
    ROOT / "output/tables/phase6tz-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6tz-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6tz-control-surfaces.md",
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

    warning_text = "- None detected.\n" if not warnings else "\n".join(f"- `{w}`" for w in warnings) + "\n"
    report = "# Phase 6TZ host-only permission, writer and driver closure\n\n"
    report += (
        "This bundle integrates the H2 custom-permission owner/grant search, the User-0 Fire "
        "restoration-writer provenance search, and the exact-build `amzn_drv_test` closure. "
        "It preserves the requirement for caller → gate → identity/user scope → exact sink.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No device, adb, Binder bind/call, service call, broadcast, driver open/ioctl, proc/sysfs/"
        "debugfs write, Root/exploit, OTA/recovery/flash, reboot, package/settings mutation, or "
        "partition write was performed.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## H2 owner/grant result\n\n"
        "The exact PackageManager permission record identifies `android.amazon.perm` as the "
        "owner of `com.amazon.alta.h2clientservice.permission.BIND_SERVICE`, UID 1000, with "
        "`signature|amazon` protection. Ten exact custom grant records identify candidate packages, "
        "but their manifest `uses-permission` requests, code-level bind edges and accepted runtime "
        "caller identities remain `UNKNOWN`. This is positive permission provenance, not a confused-"
        "deputy or shell-reachability finding.\n\n"
        "## User-0 Fire writer result\n\n"
        "The child/KFT writer explicitly targets `com.amazon.firelauncher` with `UserInfo.id`, but "
        "the available evidence is child/profile scoped and does not prove User 0. Fixed OOBE and "
        "generic ProductPolicy setters are separate non-Fire/HOME writers. No exact production caller "
        "→ gate → User-0 Fire restoration setter or preferred-HOME write was closed.\n\n"
        "## amzn_drv_test result\n\n"
        "Source Kconfig/Makefile registration is present, but the exact final PS7331 config does not "
        "select `CONFIG_AMZN_DRV_TEST`, unique Image markers are absent, and the audited module/manifest "
        "corpus has no matching payload. Runtime `/proc/amzn_drvs` nodes, labels, init/uevent load and "
        "caller/effect remain `UNKNOWN`; no source registration is promoted to a shipped exploit surface.\n\n"
        "## Overall verdict\n\n"
        "This round improves provenance but still provides no safe basis for invoking private Binder, "
        "writing a driver node, changing Fire Launcher state, or claiming Root. The strongest new "
        "fact is the UID-1000 custom permission owner and its ten explicit grants; the missing request/"
        "bind/sink join is the next host-only evidence target.\n\n"
        f"Integrated rows: `{len(rows)}`; parse warnings: `{len(warnings)}`.\n\n"
        "Warnings:\n" + warning_text
    )
    evidence = "# Phase 6TZ evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Context\n\n" + "\n".join(
        f"- `{path.relative_to(ROOT)}`: `{digest}`" for path, digest in context_hashes
    ) + "\n\n## Labels\n\n"
    evidence += (
        "- `CONFIRMED`: exact owner/config/source/observation is directly supported.\n"
        "- `STRONG_STATIC`: bounded writer or grant edge is joined, with caller/sink scope still open.\n"
        "- `UNKNOWN`: requested permission, bind caller, user scope, shipped object, policy or effect is missing.\n"
        "- `ABSENT`/`LOCAL_ONLY`: bounded corpus classifications, not global absence or vulnerability claims.\n"
    )
    graph = """flowchart LR
  P["BIND_SERVICE permission"] --> O["android.amazon.perm\nUID 1000\nsignature|amazon"]
  O --> G["10 explicit grant candidates"]
  G -. "uses-permission/bind/client UNKNOWN" .-> X["No shell reachability claim"]
  K["KFT child writer"] --> C["UserInfo.id\nchild/profile scope"]
  C -. "User-0 Fire restoration UNKNOWN" .-> Y["No HOME writer proof"]
  S["amzn_drv_test source"] --> F["final config/Image/module audit"]
  F -. "not shipped/runtime nodes UNKNOWN" .-> Z["No driver exploit claim"]
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class P,O,G,K,C,S,F bound;
  class X,Y,Z unknown;
"""
    graph_md = "# Phase 6TZ control-surface graph\n\n```mermaid\n" + graph + "```\n"

    for path, content in zip(
        OUTPUTS,
        (
            report,
            evidence,
            matrix.getvalue(),
            "\n".join(manifest) + "\n",
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
