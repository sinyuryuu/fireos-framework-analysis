#!/usr/bin/env python3
"""Integrate Phase 6UE–UG bounded static authorization audits.

This builder is intentionally host-only.  It consumes preserved worker ledgers,
checks their hashes, and writes a new immutable evidence bundle.  It never
invokes adb, Binder, service call, package mutation, reboot, driver or OTA code.
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
    "6UE H2 missing candidates": (
        ROOT / "work/luna_worker_phase6ue_h2_missing_candidates_20260810.md",
        ROOT / "work/luna_worker_phase6ue_h2_missing_candidates_20260810.csv",
    ),
    "6UF KFT tx3 gate": (
        ROOT / "work/luna_worker_phase6uf_kft_gate_20260810.md",
        ROOT / "work/luna_worker_phase6uf_kft_gate_20260810.csv",
    ),
    "6UG permission parser": (
        ROOT / "work/luna_worker_phase6ug_permission_parser_20260810.md",
        ROOT / "work/luna_worker_phase6ug_permission_parser_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6ud-report.md",
    ROOT / "findings/phase-6ud-evidence-index.md",
    ROOT / "output/tables/phase6ud-control-surface.csv",
    ROOT / "findings/phase-6tz-report.md",
    ROOT / "findings/phase-6tv-report.md",
)
OUTPUTS = (
    ROOT / "findings/phase-6uh-report.md",
    ROOT / "findings/phase-6uh-evidence-index.md",
    ROOT / "output/tables/phase6uh-control-surface.csv",
    ROOT / "output/tables/phase6uh-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6uh-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6uh-control-surfaces.md",
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
        manifest.extend(
            [
                f"{report_hash}  {report_path.relative_to(ROOT)}",
                f"{ledger_hash}  {ledger_path.relative_to(ROOT)}",
            ]
        )
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
    report = "# Phase 6UH — bounded permission, KFT and control-surface integration\n\n"
    report += (
        "This host-only bundle integrates the missing H2 candidate search, KFT transaction-3 "
        "authorization review, and exact-build Amazon permission-grant parser review. It broadens "
        "the sink question beyond Launcher: a system-level caller could affect package/component "
        "state, user-scoped policy, or other privileged state, but no accepted ordinary-app or shell "
        "path to such a sink is established here.\n\n"
        f"Generation HEAD: `{head()}`.\n\n"
        "## Safety boundary\n\n"
        "No device operation was performed in this phase: no adb, Binder bind/call, `service call`, "
        "transaction construction, user creation/switch, package or permission mutation, Fire "
        "Launcher mutation, driver operation, OTA, reboot, Root/exploit attempt, or partition write.\n\n"
        "## Inputs\n\n" + "\n".join(input_lines) + "\n\n"
        "Context hashes: "
        + "; ".join(f"`{path.relative_to(ROOT)}` ({digest})" for path, digest in context_hashes)
        + "\n\n"
        "## Findings\n\n"
        "### 1. Amazon permission-grant hook — **已證實 / CONFIRMED**\n\n"
        "The exact-build `fosservices` disassembly contains "
        "`com.android.server.pm.permission.AmazonPermissionsGranter.grantSignaturePermission` "
        "at `codeOff=0xd242a`. Its compiled branches inspect the `BasePermission.protectionLevel` "
        "vendor bit `0x80000000`, return the SELinux grant result for that branch, then inspect "
        "`0x40000000` and consult `FireOsSystemConfig.getAmzRestrictedPermissions(packageName)`. "
        "The neighboring `addAmazonPermissions` path at `codeOff=0xd24ca` checks the SELinux policy "
        "`amazon_policies/grant_amazon_permissions` before adding Amazon cross-user permission "
        "names. This is a confirmed Amazon-specific grant hook, not evidence of a shell bypass.\n\n"
        "### 2. `android.amazon.perm` ownership — **已證實 / CONFIRMED**\n\n"
        "The exact package artifact is a core/system-shared-UID package and owns the custom permission "
        "records. The observed `0x80000002` values are artifact-level evidence consistent with a "
        "signature base plus an Amazon vendor flag. The exact FireOS symbolic parser mapping and "
        "shell/ordinary-app eligibility remain `UNKNOWN`; do not treat the numeric value as a grant.\n\n"
        "### 3. KFT child-state writer — **已證實 / STRONG_STATIC**\n\n"
        "`IAmazonUserManager` transaction 3 is `enableKftLauncher(UserInfo)`. Its recovered Stub "
        "enforces the interface token and unmarshals `UserInfo`, then dispatches the method without a "
        "visible method-local UID, `MANAGE_USERS`, or cross-user check in the bounded slice. The sink "
        "uses `UserInfo.id` to enable Tahoe `FreeTimeLauncherActivity` and set Fire Launcher/Launcher3 "
        "application state to disabled for that same user. Confirmed internal callers are child creation "
        "and an upgrade boot phase guarded by `isUpgrade()` and `isChildUser()`. External caller access, "
        "service-manager policy and downstream PackageManager authorization remain `UNKNOWN`. This is "
        "an authorization review point, not a demonstrated confused deputy or exploit.\n\n"
        "### 4. H2 client candidates — **待驗證 / UNKNOWN**\n\n"
        "Ten candidate grant records remain, but the bounded corpus closes neither a candidate-specific "
        "`bindService` → `ServiceConnection` → `IH2ClientService` path nor a runtime client. Three "
        "preserved XML trees show requested permission names; seven candidate permission fields remain "
        "unavailable. AVOD's separate `PlaybackSdkService` bind and caller check is not H2 evidence.\n\n"
        "## Control-surface interpretation\n\n"
        "The strongest current model is: a privileged Amazon/system-server identity owns the relevant "
        "permission and user/package-state sinks; KFT's recovered writer is user-scoped and can change "
        "more than HOME when reached; the missing evidence is the caller and authorization boundary. "
        "No evidence presently justifies invoking a private Binder transaction, crafting a service "
        "payload, opening a driver, or claiming root. The remaining safe work is artifact-preserving "
        "static closure of candidate manifests/callers and exact runtime read-only correlation.\n\n"
        "## Verdict\n\n"
        "- **已證實:** Amazon permission-grant control flow and owner artifact; KFT child writer sink and "
        "two internal lifecycle callers.\n"
        "- **高可信推論:** the relevant package/user-state effects require an Amazon/system identity or "
        "a caller accepted by additional service/SELinux/PackageManager gates.\n"
        "- **待驗證:** H2 external client, KFT tx3 external authorization, full parser semantics, and "
        "downstream PMS outcome.\n"
        "- **已排除:** no accepted ordinary-app/shell route has been shown in the bounded evidence; this "
        "does not prove universal absence.\n"
        "- **因風險拒絕測試:** private Binder transaction replay, arbitrary `UserInfo` injection, "
        "package-state mutation, driver/ioctl probes, Root and boot/partition operations.\n\n"
        f"Integrated rows: `{len(rows)}`; parse warnings: `{len(warnings)}`.\n\n"
        "Warnings:\n" + warning_text
    )
    evidence = "# Phase 6UH evidence index\n\n" + "\n\n".join(evidence_blocks) + "\n\n"
    evidence += "## Integrated evidence rules\n\n" + (
        "- `CONFIRMED`: exact-build declaration, owner artifact, or bounded compiled branch is shown.\n"
        "- `STRONG_STATIC`: a caller/sink or grant edge is shown but an external/runtime edge is missing.\n"
        "- `UNKNOWN`: the bounded corpus lacks the required caller, service-manager, parser, or downstream edge.\n"
        "- `NEGATIVE_BOUNDED`: no edge was found in preserved artifacts; it is not a universal absence proof.\n"
        "- No row authorizes a live private Binder call, state mutation, driver operation, or exploit.\n"
    )
    graph = """flowchart LR
  O["android.amazon.perm\nUID 1000 owner"] --> P["custom permission\n0x80000002 artifact"]
  P --> G["AmazonPermissionsGranter\ngrantSignaturePermission"]
  G --> S["SELinux / restricted-set\ngate"]
  C["createChildUser"] --> T["IAmazonUserManager tx3\nenableKftLauncher(UserInfo)"]
  B["onBootPhase(500)\nisUpgrade + isChildUser"] --> T
  T --> U["UserInfo.id"]
  U --> W["Tahoe enabled\nFire/Launcher3 disabled\nchild scope"]
  X["external caller / service-manager\npermission boundary"] -. "UNKNOWN" .-> T
  H["H2 candidate packages"] -. "no closed bind/client edge" .-> I["runtime client UNKNOWN"]
  S -. "no shell grant proven" .-> N["no ordinary-app/shell sink proof"]
  W -. "not User-0 proof" .-> N
  classDef bound fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class O,P,G,S,C,T,B,U,W bound;
  class X,H,I,N unknown;
"""
    graph_md = "# Phase 6UH control-surface graph\n\n```mermaid\n" + graph + "```\n"

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
