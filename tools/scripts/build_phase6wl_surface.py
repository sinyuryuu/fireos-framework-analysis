#!/usr/bin/env python3
"""Integrate Phase 6WG–WK plus the live ProductPolicy read-only join."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKERS = {
    "6WG Framework IPC residual": (
        ROOT / "work/luna_worker_phase6wg_ipc_residual_20260810.md",
        ROOT / "work/luna_worker_phase6wg_ipc_residual_20260810.csv",
    ),
    "6WH OTA residual": (
        ROOT / "work/luna_worker_phase6wh_ota_residual_20260810.md",
        ROOT / "work/luna_worker_phase6wh_ota_residual_20260810.csv",
    ),
    "6WI native driver caller": (
        ROOT / "work/luna_worker_phase6wi_driver_caller_20260810.md",
        ROOT / "work/luna_worker_phase6wi_driver_caller_20260810.csv",
    ),
    "6WJ test reconciliation": (
        ROOT / "work/luna_worker_phase6wj_test_reconciliation_20260810.md",
        ROOT / "work/luna_worker_phase6wj_test_reconciliation_20260810.csv",
    ),
    "6WK broad surface": (
        ROOT / "work/luna_worker_phase6wk_broad_surface_20260810.md",
        ROOT / "work/luna_worker_phase6wk_broad_surface_20260810.csv",
    ),
}
LIVE_DIR = ROOT / "artifacts/phase6wf-product-policy-readonly-20260810-01"
CONTEXT = (
    ROOT / "findings/phase-6vf-report.md",
    ROOT / "output/tables/phase6vf-control-surface.csv",
    ROOT / "findings/phase-6wf-product-policy-live-readonly.md",
    LIVE_DIR / "sha256sums.txt",
)
OUTPUTS = (
    ROOT / "findings/phase-6wl-report.md",
    ROOT / "findings/phase-6wl-evidence-index.md",
    ROOT / "output/tables/phase6wl-control-surface.csv",
    ROOT / "output/tables/phase6wl-input-manifest.sha256",
    ROOT / "output/call-graphs/phase6wl-control-surfaces.mmd",
    ROOT / "output/call-graphs/phase6wl-control-surfaces.md",
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


def read_csv(path: Path, family: str) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        reader = csv.DictReader(stream, skipinitialspace=True)
        if not reader.fieldnames:
            return [], [f"{path.relative_to(ROOT)}: missing header"]
        rows: list[dict[str, str]] = []
        for line, raw in enumerate(reader, start=2):
            extras = raw.pop(None, None)
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            row.update(surface_family=family, source_csv=str(path.relative_to(ROOT)), source_row=str(line), source_sha256=sha(path))
            if extras:
                warnings.append(f"{path.relative_to(ROOT)}:{line}: extra_fields={len(extras)}")
                row["csv_parse_warning"] = f"extra_fields={len(extras)}"
            rows.append(row)
    return rows, warnings


def live_rows() -> list[dict[str, str]]:
    def evidence(name: str) -> str:
        path = LIVE_DIR / name
        return sha(path) if path.is_file() else "MISSING"

    return [
        {
            "id": "WF-POL-001",
            "surface_family": "6WF live ProductPolicy",
            "category": "global_policy",
            "target_or_literal": "<policy/>; no Fire Launcher",
            "status": "CONFIRMED_NO_ENTRY",
            "evidence_file": str((LIVE_DIR / "global_policy.xml").relative_to(ROOT)),
            "evidence_sha256": evidence("global_policy.xml"),
            "observed_effect": "none; read-only",
            "unknowns": "alternate policy source not excluded",
        },
        {
            "id": "WF-POL-002",
            "surface_family": "6WF live ProductPolicy",
            "category": "common_device_policy",
            "target_or_literal": "child Cloud9 entries; no Fire Launcher",
            "status": "CONFIRMED_NO_ENTRY",
            "evidence_file": str((LIVE_DIR / "common_device_policy.xml").relative_to(ROOT)),
            "evidence_sha256": evidence("common_device_policy.xml"),
            "observed_effect": "none; read-only",
            "unknowns": "policy writer is privileged static capability",
        },
        {
            "id": "WF-POL-003",
            "surface_family": "6WF live ProductPolicy",
            "category": "multimodal_device_policy",
            "target_or_literal": "adult/child Paladin and ECS entries; no Fire Launcher",
            "status": "CONFIRMED_NO_ENTRY",
            "evidence_file": str((LIVE_DIR / "multimodal_device_policy.xml").relative_to(ROOT)),
            "evidence_sha256": evidence("multimodal_device_policy.xml"),
            "observed_effect": "none; read-only",
            "unknowns": "policy writer is privileged static capability",
        },
        {
            "id": "WF-POL-004",
            "surface_family": "6WF live ProductPolicy",
            "category": "receiver_filter_policy",
            "target_or_literal": "Facebook SEND activity filter; no HOME/package writer",
            "status": "CONFIRMED_NOT_HOME_WRITER",
            "evidence_file": str((LIVE_DIR / "receiver_filter_policy.xml").relative_to(ROOT)),
            "evidence_sha256": evidence("receiver_filter_policy.xml"),
            "observed_effect": "none; read-only",
            "unknowns": "full PackageManager filter caller path remains static-only",
        },
        {
            "id": "WF-POL-005",
            "surface_family": "6WF live ProductPolicy",
            "category": "product_policy",
            "target_or_literal": "/system/etc/product_policy.xml absent on live device",
            "status": "UNKNOWN_LAYOUT_MISMATCH",
            "evidence_file": str((LIVE_DIR / "device_policy_paths.txt").relative_to(ROOT)),
            "evidence_sha256": evidence("device_policy_paths.txt"),
            "observed_effect": "none; pull failed with ENOENT",
            "unknowns": "OTA file-map lists path; installed layout or provenance mismatch unresolved",
        },
    ]


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> None:
    if args.dry_run:
        print("host-only dry run; no output written")
        for family, pair in WORKERS.items():
            print(f"{family}: {pair[0].relative_to(ROOT)}, {pair[1].relative_to(ROOT)}")
        print("live:", LIVE_DIR.relative_to(ROOT))
        print("outputs:", ", ".join(str(path.relative_to(ROOT)) for path in OUTPUTS))
        return

    required = [path for pair in WORKERS.values() for path in pair] + list(CONTEXT)
    required += [LIVE_DIR / name for name in ("global_policy.xml", "common_device_policy.xml", "multimodal_device_policy.xml", "receiver_filter_policy.xml", "device_policy_paths.txt")]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))
    existing = [str(path.relative_to(ROOT)) for path in OUTPUTS if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite output(s):\n" + "\n".join(existing))

    rows: list[dict[str, str]] = []
    warnings: list[str] = []
    source_lines: list[str] = []
    manifest: list[str] = []
    for family, (report, ledger) in WORKERS.items():
        report_hash, ledger_hash = sha(report), sha(ledger)
        manifest.extend([f"{report_hash}  {report.relative_to(ROOT)}", f"{ledger_hash}  {ledger.relative_to(ROOT)}"])
        parsed, parse_warnings = read_csv(ledger, family)
        rows.extend(parsed)
        warnings.extend(parse_warnings)
        source_lines.append(f"- **{family}:** `{report.relative_to(ROOT)}` ({report_hash}); `{ledger.relative_to(ROOT)}` ({ledger_hash}); {len(parsed)} row(s).")
    policy = live_rows()
    rows.extend(policy)
    for path in CONTEXT:
        manifest.append(f"{sha(path)}  {path.relative_to(ROOT)}")
    for path in sorted(LIVE_DIR.iterdir()):
        if path.is_file() and path.name != "sha256sums.txt":
            manifest.append(f"{sha(path)}  {path.relative_to(ROOT)}")

    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    preferred = ["surface_family", "source_csv", "source_row", "source_sha256", "id"]
    fields = [key for key in preferred if key in fields] + [key for key in fields if key not in preferred]
    matrix = io.StringIO(newline="")
    writer = csv.DictWriter(matrix, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fields})

    live_dir = str(LIVE_DIR.relative_to(ROOT))
    report = f"""# Phase 6WL — cross-surface residual closure and live policy join

Generation HEAD: `{head()}`.

## Scope and safety

This phase continues the non-Launcher review. It integrates 43 new worker rows
from Framework IPC, OTA, native-driver, test-reconciliation and broad-surface
searches, plus five live ProductPolicy observations from the exact serial.
Acceptance remains:

`caller → gate → identity/user scope → exact sink → observed effect`

All worker work was host-only. The live policy capture used only `adb pull`,
`getprop`, `ls`, and hashing. No Binder transaction, guessed private code,
driver/ioctl, OTA/recovery execution, malformed input, reboot, package/settings
mutation, Fire Launcher mutation, Root/exploit attempt, or partition write was
performed.

## Integrated inputs

""" + "\n".join(source_lines) + f"""

Live policy capture: `{live_dir}` (five observation rows;
the raw files and SHA-256 list are retained).

## Findings

### 已證實：many privileged sinks exist across the system

The new ledgers locate settings writers, user/profile creation and switching
sinks, package hiding/deletion helpers, SettingsProvider operations, OTA native
handler registration and recovery handoff, native driver capabilities, and
Amazon/system-server Binder services. These are capabilities or static sinks;
they do not by themselves establish an external caller or accepted identity.

### 已證實：live ProductPolicy inputs do not name Fire Launcher

`global_policy.xml` is empty. `common_device_policy.xml` contains child-only
Cloud9 browser entries. `multimodal_device_policy.xml` contains adult/child
Paladin/ECS entries. `receiver_filter_policy.xml` contains a Facebook SEND
activity filter. None contains `com.amazon.firelauncher`, a HOME component, or a
User-0 package-state directive.

### 高可信推論：ProductPolicy is not the observed User-0 Fire restoration writer

The exact service has a real enabled-state writer and event dispatch, but the
live policy inputs that were accessible do not supply a Fire Launcher entry.
The `product_policy.xml` path is absent on the live device even though the OTA
file-map lists it; therefore this conclusion is bounded to the captured files.

### 待驗證：remaining artifact and external-caller gaps

The missing product-policy path/layout, OTA recovery/AVB handoff, exact native
ELF caller/policy joins, and private service transaction/caller authorization
remain unresolved. The new IPC rows also show settings sinks guarded by
`DUMP` or Amazon permissions, but exact transaction and SELinux/service-manager
boundaries are not all present. These are host-side closure targets, not a
reason to issue unknown Binder codes or open driver nodes.

### 已排除：new rows do not create a root or formal HOME route

No new row closes an ordinary app or shell caller through authorization and
identity/user scope to User-0 package state, formal HOME, root, or partition
effect. Existing equivalent mutations remain excluded by the 6WJ matrix.

### 因風險拒絕測試

Unknown Binder transactions, native device operations, OTA/recovery execution,
root/exploit payloads, Fire Launcher mutation, and any path whose rollback may
require factory reset were not executed.

## Metrics

- Worker rows: `43`
- Live policy observations: `{len(policy)}`
- Integrated rows: `{len(rows)}`
- CSV parse warnings: `{len(warnings)}`

## Next safe minimum

1. Resolve the live/OTA `product_policy.xml` layout mismatch with exact image
   provenance, without writing or mounting system read-write.
2. Join the residual Binder rows to saved service publication and permission
   artifacts; do not call unknown transactions.
3. Close exact native DT_NEEDED/relocation and policy edges from host artifacts.
4. If all remain incomplete, archive the privileged-control branch as
   unclosed and return to ordinary ADB HOME behavior only through already
   validated reversible paths.
"""
    evidence = "# Phase 6WL evidence index\n\n" + "\n".join(source_lines) + "\n\n"
    evidence += "## Live policy evidence\n\n"
    evidence += "- `artifacts/phase6wf-product-policy-readonly-20260810-01/` — exact serial read-only capture.\n"
    evidence += "- `findings/phase-6wf-product-policy-live-readonly.md` — static-to-live interpretation.\n\n"
    evidence += "## Acceptance rules\n\n"
    evidence += "- Static capability, registration, or a missing local check is not external reachability.\n"
    evidence += "- `UNKNOWN` is bounded missing evidence, not proof of absence.\n"
    evidence += "- No row authorizes live Binder, driver, OTA/recovery, Root, or partition execution.\n"

    graph = """flowchart LR
  L["ordinary app / shell"] --> G["permission + SELinux + service gate"]
  G -. "caller/identity not closed" .-> X["no accepted low-privilege effect"]
  PP["ProductPolicy"] --> PX["live XML inputs"]
  PX -. "no Fire Launcher entry; product_policy absent" .-> X
  PP --> PS["AmazonPackageManager state writer"]
  PS -. "policy/caller/user scope bounded" .-> X
  I["residual IPC"] --> IS["settings/user/profile sinks"]
  IS -. "transaction/SELinux/UID unknown" .-> X
  O["OTA handlers"] --> OW["recovery/partition capability"]
  OW -. "recovery caller/AVB unknown" .-> X
  N["native drivers"] --> NW["node/policy capability"]
  NW -. "exact shipped caller unknown" .-> X
  T["historical tests"] --> T2["no durable User-0 HOME replacement"]
  classDef high fill:#e8f1ff,stroke:#1d4e89,color:#102a43;
  classDef unknown fill:#fff3cd,stroke:#856404,color:#533f3f;
  class PP,PX,PS,I,IS,O,OW,N,NW,T,T2 high;
  class L,G,X unknown;
"""
    graph_md = "# Phase 6WL control-surface graph\n\n```mermaid\n" + graph + "```\n"
    for path, content in zip(OUTPUTS, (report, evidence, matrix.getvalue(), "\n".join(manifest) + "\n", graph, graph_md)):
        write_new(path, content, args.force)
    print(f"wrote {len(OUTPUTS)} outputs; rows={len(rows)} warnings={len(warnings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
