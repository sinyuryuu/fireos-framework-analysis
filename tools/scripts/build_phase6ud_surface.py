#!/usr/bin/env python3
"""Integrate Phase 6UA–UC H2 client, KFT caller and permission semantics audits."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "6UA H2 grant/client": (
        ROOT / "work/luna_worker_phase6ua_h2_grant_client_20260810.md",
        ROOT / "work/luna_worker_phase6ua_h2_grant_client_20260810.csv",
    ),
    "6UB KFT caller/scope": (
        ROOT / "work/luna_worker_phase6ub_kft_caller_scope_20260810.md",
        ROOT / "work/luna_worker_phase6ub_kft_caller_scope_20260810.csv",
    ),
    "6UC Amazon permission semantics": (
        ROOT / "work/luna_worker_phase6uc_amazon_perm_semantics_20260810.md",
        ROOT / "work/luna_worker_phase6uc_amazon_perm_semantics_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6tz-report.md",
    ROOT / "findings/phase-6tz-evidence-index.md",
    ROOT / "output/tables/phase6tz-control-surface.csv",
    ROOT / "findings/phase-6tv-report.md",
)
OUTPUTS = (
    ROOT / "findings/phase-6ud-report.md",
    ROOT / "findings/phase-6ud-evidence-index.md",
    ROOT / "output/tables/phase6ud-control-surface.csv",
    ROOT / "output/tables/phase6ud-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6ud-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6ud-control-surfaces.md",
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
    report = "# Phase 6UD host-only H2 client, KFT scope and permission semantics\n\n"
    report += (
        "This bundle integrates the exact-build H2 grant-candidate/client search, the KFT child "
        "writer caller/scope search, and the `android.amazon.perm` protection-level comparison.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No device, adb, Binder bind/call, service call, transaction construction, user creation or "
        "switch, package/permission mutation, driver operation, OTA, reboot, Root/exploit or partition "
        "write was performed.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## H2 client result\n\n"
        "Ten exact custom grant records remain grant candidates. Three preserved XML trees show the "
        "requested custom permission for Tahoe, Kindle OOBE and Parental Controls, but no package has a "
        "closed `bindService` → `ServiceConnection` → `IH2ClientService` callsite in the bounded corpus. "
        "The other seven requested-permission fields are not preserved and remain `UNKNOWN`. Grant or "
        "request evidence is not actual runtime binding or a shell path.\n\n"
        "## KFT caller and user scope\n\n"
        "`AmazonUserManagerImpl.createChildUser(String)` creates a child user and passes its `UserInfo` "
        "through transaction 3 to `enableKftLauncher`; an upgrade lifecycle caller also processes only "
        "`isChildUser` entries. The writer uses `UserInfo.id` to enable Tahoe and disable Fire/Launcher3. "
        "The tx3 permission/UID and cross-user/admin gate are not joined in the bounded method slice, "
        "so this is child/profile writer evidence, not a User-0 Fire restoration or arbitrary caller claim.\n\n"
        "## Permission semantics\n\n"
        "`android.amazon.perm` is a system-shared-UID/core framework package and owns the custom records. "
        "`0x80000002` is statically consistent with a signature base plus an Amazon vendor flag, while "
        "the exact FireOS parser semantics and shell/ordinary-app eligibility remain `UNKNOWN`. AOSP's "
        "permission ownership/signature checks do not prove a FireOS bypass.\n\n"
        "## Verdict\n\n"
        "The research now has a stronger permission-owner fact and a confirmed child KFT writer path, "
        "but still no accepted ordinary-app/shell caller leading to User-0 HOME, Fire package state, "
        "root or partition effect. The next safe target is preserving exact candidate manifests and "
        "code-level bind/caller artifacts; no service invocation is justified by this evidence.\n\n"
        f"Integrated rows: `{len(rows)}`; parse warnings: `{len(warnings)}`.\n\n"
        "Warnings:\n" + warning_text
    )
    evidence = "# Phase 6UD evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Context\n\n" + "\n".join(
        f"- `{path.relative_to(ROOT)}`: `{digest}`" for path, digest in context_hashes
    ) + "\n\n## Labels\n\n"
    evidence += (
        "- `CONFIRMED`: exact static declaration, owner record or caller/scope edge is shown.\n"
        "- `STRONG_STATIC`: bounded grant/writer edge is shown, with a missing external/runtime edge.\n"
        "- `UNKNOWN`: bind client, parser semantics, permission eligibility or cross-user gate is missing.\n"
        "- `NEGATIVE_BOUNDED`: no edge in the preserved corpus; not a universal absence proof.\n"
    )
    graph = """flowchart LR
  O["android.amazon.perm\nUID 1000 owner"] --> P["signature|amazon record"]
  P --> G["10 grant candidates"]
  G -. "requested/bind/client incomplete" .-> X["No ordinary reachability"]
  C["createChildUser"] --> T["tx3 enableKftLauncher"]
  T --> U["UserInfo.id"]
  U --> W["Tahoe enabled\nFire/Launcher3 disabled"]
  W -. "child scope; User-0 gate UNKNOWN" .-> Y["No User-0 restoration proof"]
  A["AOSP permission checks"] -. "FireOS parser flag semantics UNKNOWN" .-> F["no bypass claim"]
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class O,P,G,C,T,U,W,A bound;
  class X,Y,F unknown;
"""
    graph_md = "# Phase 6UD control-surface graph\n\n```mermaid\n" + graph + "```\n"

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
