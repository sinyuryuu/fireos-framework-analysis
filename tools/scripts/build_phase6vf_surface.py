#!/usr/bin/env python3
"""Build the Phase 6VF cross-launcher privilege-surface ledger.

This is deliberately host-only.  It normalizes the five completed Phase 6V
worker ledgers and records their hashes; it does not contact a device, invoke
Binder, execute native code, or mutate any project input.
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
    "6VA fosinit residual closure": (
        ROOT / "work/luna_worker_phase6va_fosinit_residual_closure_20260810.md",
        ROOT / "work/luna_worker_phase6va_fosinit_residual_closure_20260810.csv",
    ),
    "6VB OTA post-install closure": (
        ROOT / "work/luna_worker_phase6vb_ota_postinstall_closure_20260810.md",
        ROOT / "work/luna_worker_phase6vb_ota_postinstall_closure_20260810.csv",
    ),
    "6VC native driver caller/policy closure": (
        ROOT / "work/luna_worker_phase6vc_driver_caller_policy_20260810.md",
        ROOT / "work/luna_worker_phase6vc_driver_caller_policy_20260810.csv",
    ),
    "6VD existing-test reconciliation": (
        ROOT / "work/luna_worker_phase6vd_test_reconciliation_20260810.md",
        ROOT / "work/luna_worker_phase6vd_test_reconciliation_20260810.csv",
    ),
    "6VE Framework IPC sink inventory": (
        ROOT / "work/luna_worker_phase6ve_framework_sink_inventory_20260810.md",
        ROOT / "work/luna_worker_phase6ve_framework_sink_inventory_20260810.csv",
    ),
}
CONTEXT = (
    ROOT / "findings/phase-6ur-report.md",
    ROOT / "output/tables/phase6ur-control-surface.csv",
    ROOT / "findings/phase-6ui-readonly-snapshot.md",
    ROOT / "output/tables/phase6ui-readonly-state.csv",
)
OUTPUTS = (
    ROOT / "findings/phase-6vf-report.md",
    ROOT / "findings/phase-6vf-evidence-index.md",
    ROOT / "output/tables/phase6vf-control-surface.csv",
    ROOT / "output/tables/phase6vf-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6vf-cross-surface.mmd",
    ROOT / "output/call-graphs/phase6vf-cross-surface.md",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def read_rows(path: Path, family: str) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream, skipinitialspace=True)
        if not reader.fieldnames:
            return [], [f"{path.relative_to(ROOT)}: missing CSV header"]
        result: list[dict[str, str]] = []
        for line, raw in enumerate(reader, start=2):
            extras = raw.pop(None, None)
            if extras:
                warnings.append(f"{path.relative_to(ROOT)}:{line}: extra_fields={len(extras)}")
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row.update(
                surface_family=family,
                source_csv=str(path.relative_to(ROOT)),
                source_sha256=sha(path),
                source_row=str(line),
            )
            if extras:
                row["csv_parse_warning"] = f"extra_fields={len(extras)}"
            result.append(row)
        return result, warnings


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> None:
    if args.dry_run:
        print("host-only dry run; no output written")
        for family, pair in INPUTS.items():
            print(f"{family}: {pair[0].relative_to(ROOT)}, {pair[1].relative_to(ROOT)}")
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
    manifest: list[str] = []
    source_blocks: list[str] = []
    for family, (report, ledger) in INPUTS.items():
        report_hash, ledger_hash = sha(report), sha(ledger)
        manifest.extend(
            [
                f"{report_hash}  {report.relative_to(ROOT)}",
                f"{ledger_hash}  {ledger.relative_to(ROOT)}",
            ]
        )
        rows, row_warnings = read_rows(ledger, family)
        integrated.extend(rows)
        warnings.extend(row_warnings)
        source_blocks.append(
            f"- **{family}:** `{report.relative_to(ROOT)}` ({report_hash}); "
            f"`{ledger.relative_to(ROOT)}` ({ledger_hash}); {len(rows)} row(s)."
        )
    context_hashes = [(path, sha(path)) for path in CONTEXT]
    manifest.extend(f"{digest}  {path.relative_to(ROOT)}" for path, digest in context_hashes)

    fieldnames: list[str] = []
    for row in integrated:
        for field in row:
            if field not in fieldnames:
                fieldnames.append(field)
    ordered = ["surface_family", "source_csv", "source_sha256", "source_row"]
    fieldnames = ordered + [field for field in fieldnames if field not in ordered]
    matrix = io.StringIO(newline="")
    writer = csv.DictWriter(matrix, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in integrated:
        writer.writerow({field: row.get(field, "") for field in fieldnames})

    report = f"""# Phase 6VF — cross-launcher privilege-surface closure

Generation HEAD: `{git_head()}`.

## Scope and safety

This phase broadens the analysis beyond Fire Launcher to every preserved
high-impact surface that could plausibly change package/component state, HOME,
settings, user/profile state, trust/update state, native memory/IO state, or a
partition. Acceptance remains:

`caller → permission / SELinux / service-manager / lifecycle gate → identity and user scope → exact sink → observed effect`

The five worker ledgers below were produced by host-only analysis. No Binder
transaction, guessed service code, driver node/ioctl, OTA/recovery execution,
malformed input, reboot, package/settings mutation, Fire Launcher mutation,
Root/exploit attempt, or partition write was performed.

## Inputs

""" + "\n".join(source_blocks) + f"""

Context hashes: """ + "; ".join(f"`{p.relative_to(ROOT)}` ({d})" for p, d in context_hashes) + f"""

## Cross-surface findings

### 已證實：privileged sinks exist, but are not low-privilege routes

The Framework inventory contains direct enabled-state and preferred/HOME sinks.
It also contains KFT child/profile-scoped writes, ProductPolicy package/component
writers, DPM/PMS sinks, Amazon user/settings writers, and recovery/update
partition writers. These are concrete code locations, not proof that shell or
an ordinary app can obtain the required handle or accepted identity.

### 高可信推論：User-0 formal HOME and package-state control remain protected

The saved PS7331 read-only snapshot still resolves User 0 HOME to Fire Launcher
at priority 50. The reconciled historical tests show ordinary preferred records,
package/component setters, accessibility/foreground redirects, child/KFT
lifecycle, DPM, settings/overlay, private IPC, OTA, driver and PI-futex routes
did not establish a sustainable User-0 HOME replacement or root transition.
KFT evidence is explicitly child/profile scoped; it must not be generalized to
User 0.

### 待驗證：bounded static gaps remain, but none authorizes live probing

The residual fosinit rows include unresolved caller/authz or receiver-side sink
details for CRL trust/update, tablet broadcast relay, package recency, settings,
factory-reset whitelist, FireOS OTA callback, and related lifecycle services.
The OTA audit still lacks complete recovery-to-updater identity/AVB handoff;
native CMDQ/ION/Amazon-LD joins lack all exact shipped node, policy and caller
edges. These gaps are finite host-side closure targets, not permission to guess
Binder codes, open nodes, execute update paths, or mutate the device.

### 已排除：repeating equivalent tests is not a new control surface

The Phase 6VD reconciliation de-duplicates 19 historical route families. It
records no new durable User-0 writer and specifically preserves the distinction
between a child/profile state change, a foreground redirect, a protected setter
rejection, and a formal HOME resolver change. No same-condition component-disable
or preferred-activity replay is justified.

### 因風險拒絕測試

Recovery/update-binary partition writes, unknown private Binder transactions,
driver/ioctl operations, root/exploit payloads, Fire Launcher mutation, and any
operation requiring a recovery or factory-reset rollback were not performed.

## Highest-value remaining questions

1. Can the residual fosinit rows be closed with exact caller, permission,
   identity and sink joins from preserved artifacts?
2. Can the OTA verifier-to-recovery handoff be proven to require only signed,
   authorized recovery context?
3. Do exact shipped native libraries contain an ordinary-app or system-service
   caller to CMDQ/ION/Amazon-LD with a security-sensitive sink?
4. Is there any exact-build private service whose external handle and caller
   authorization both close to a User-0 package/settings/HOME writer?

Until one of these questions has a complete chain and a safe observation, the
evidence supports protected-control analysis, not a root claim.

## Metrics

- Integrated rows: `{len(integrated)}`
- CSV parse warnings: `{len(warnings)}`
- Worker families: `{len(INPUTS)}`

## Verdict vocabulary

- **已證實:** exact static edge or saved read-only effect within the cited scope.
- **高可信推論:** bounded interpretation with named missing evidence.
- **待驗證:** a caller, gate, identity, user scope, sink, or runtime effect is incomplete.
- **已排除:** the cited route did not achieve its target under recorded conditions.
- **因風險拒絕測試:** deliberately not executed because rollback/safety was insufficient.
"""
    evidence = "# Phase 6VF evidence index\n\n"
    evidence += "## Worker evidence\n\n" + "\n".join(source_blocks) + "\n\n"
    evidence += "## Acceptance rules\n\n"
    evidence += (
        "- Static capability, registration, package visibility, or a missing local check is not external reachability.\n"
        "- `UNKNOWN` is bounded missing evidence, not proof of absence.\n"
        "- A row with a writer must name its identity/user scope before it can support a User-0 conclusion.\n"
        "- No evidence row authorizes live Binder, driver, OTA/recovery, root, or partition execution.\n"
    )
    graph = """flowchart LR
  U["ordinary app / shell"] --> G["caller + permission + SELinux/service gate"]
  G -. "not closed" .-> N["no accepted low-privilege effect"]
  K["KFT / ProductPolicy"] --> P["AmazonPackageManager → PMS enabled-state sink"]
  P --> S["explicit user/profile scope"]
  S -. "User-0 restoration not proven" .-> N
  H["PMS preferred/HOME"] --> R["priority 50 Fire Launcher resolver"]
  R -. "ordinary preferred record did not win" .-> N
  D["DPM / Amazon user-settings"] --> D2["protected system-service sink"]
  D2 -. "caller and owner/admin gate incomplete" .-> N
  O["signed OTA / recovery"] --> W["block-image / partition writer"]
  W -. "recovery identity and AVB handoff unknown" .-> N
  V["CMDQ / ION / Amazon-LD"] --> V2["native capability / node policy"]
  V2 -. "exact shipped caller and security sink unknown" .-> N
  F["fosinit residual services"] --> F2["callbacks / receivers / Binder"]
  F2 -. "authz or final sink unresolved" .-> N
  T["historical tests"] --> T2["no sustainable User-0 replacement"]
  classDef high fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class K,P,S,H,R,D,D2,O,W,V,V2,F,F2,T,T2 high;
  class U,G,N unknown;
"""
    graph_md = "# Phase 6VF cross-surface graph\n\n```mermaid\n" + graph + "```\n"
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
