#!/usr/bin/env python3
"""Build the Phase 14 host-only privilege-surface reconciliation.

The builder consumes preserved worker CSV files and one bounded, read-only
device capture.  It does not invoke adb, Binder, a driver, recovery,
update-binary, or any state-changing command.  The normalized table keeps
caller, gate, Binder identity, user scope, sink, and missing edges separate so
that a capability is not mistaken for a reachable privilege transition.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "adb/phase14/PHASE14-READONLY-SERVICES-20260810-01"
WORKERS = {
    "assets": ROOT / "work/luna_worker_cont_asset_inventory_20260810.csv",
    "ipc": ROOT / "work/luna_worker_cont_ipc_reconciliation_20260810.csv",
    "ota": ROOT / "work/luna_worker_cont_ota_reconciliation_20260810.csv",
    "broad": ROOT / "work/luna_worker_cont_broad_surface_20260810.csv",
}
WORKER_REPORTS = [p.with_suffix(".md") for p in WORKERS.values()]
ALLOWED = {"Confirmed", "Strong evidence", "Probable", "Hypothesis", "Disproved", "Unknown"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def csv_shape(path: Path) -> tuple[int, int, int]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        header = next(reader, [])
        rows = list(reader)
    malformed = sum(len(row) != len(header) for row in rows)
    return len(header), len(rows), malformed


def v(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = (row.get(name) or "").strip()
        if value:
            return value
    return "UNKNOWN"


def confidence(raw: str) -> str:
    normalized = raw.strip()
    aliases = {
        "high": "Strong evidence",
        "HIGH": "Strong evidence",
        "medium": "Probable",
        "MEDIUM": "Probable",
        "low": "Hypothesis",
        "LOW": "Hypothesis",
        "unknown": "Unknown",
        "UNKNOWN": "Unknown",
        "confirmed": "Confirmed",
        "CONFIRMED": "Confirmed",
    }
    return aliases.get(normalized, normalized if normalized in ALLOWED else "Unknown")


def row_for(prefix: str, number: int, source: str, row: dict[str, str]) -> dict[str, str]:
    if source == "ipc":
        return {
            "id": f"P14-IPC-{number:03d}",
            "surface": v(row, "surface"),
            "caller_or_input": v(row, "caller"),
            "gate_or_policy": v(row, "gate"),
            "binder_identity": v(row, "binder_identity"),
            "user_scope_or_target": v(row, "user_scope"),
            "sink_or_effect": v(row, "sink"),
            "observed_effect": v(row, "observed_effect"),
            "evidence": v(row, "evidence"),
            "confidence": confidence(v(row, "confidence")),
            "missing_edge": v(row, "missing_edge"),
            "next_safe_step": v(row, "next_safe_step"),
        }
    if source == "ota":
        return {
            "id": f"P14-OTA-{number:03d}",
            "surface": v(row, "surface"),
            "caller_or_input": v(row, "caller", "entrypoint"),
            "gate_or_policy": v(row, "gate"),
            "binder_identity": v(row, "identity"),
            "user_scope_or_target": v(row, "user_scope"),
            "sink_or_effect": v(row, "sink"),
            "observed_effect": v(row, "observed_effect"),
            "evidence": v(row, "evidence"),
            "confidence": confidence(v(row, "confidence")),
            "missing_edge": v(row, "missing_edge"),
            "next_safe_step": v(row, "next_safe_step"),
        }
    if source == "broad":
        return {
            "id": f"P14-BS-{number:03d}",
            "surface": v(row, "surface"),
            "caller_or_input": v(row, "caller", "entrypoint"),
            "gate_or_policy": v(row, "permission_or_gate"),
            "binder_identity": v(row, "uid_or_domain"),
            "user_scope_or_target": v(row, "user_scope"),
            "sink_or_effect": v(row, "sink"),
            "observed_effect": v(row, "effect"),
            "evidence": v(row, "evidence"),
            "confidence": confidence(v(row, "confidence")),
            "missing_edge": v(row, "missing_edge"),
            "next_safe_step": v(row, "next_safe_step"),
        }
    raise ValueError(f"unknown source: {source}")


def normalized_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in ("ipc", "ota", "broad"):
        for number, item in enumerate(read_csv(WORKERS[source]), start=1):
            rows.append(row_for("P14", number, source, item))

    # These are main-agent evidence joins.  They are deliberately separate
    # from worker rows and never claim that a live transaction was sent.
    rows.extend([
        {
            "id": "P14-LIVE-001",
            "surface": "User 0 formal HOME baseline",
            "caller_or_input": "read-only cmd package resolve-activity",
            "gate_or_policy": "standard HOME resolver; no mutation",
            "binder_identity": "command result only; caller not inferred",
            "user_scope_or_target": "User 0",
            "sink_or_effect": "com.amazon.firelauncher/.Launcher; priority=50; isDefault=true",
            "observed_effect": "resolver and recent START logs select Fire Launcher",
            "evidence": "adb/phase14/PHASE14-READONLY-SERVICES-20260810-01/home_resolution.stdout.txt; recent_logcat.stdout.txt",
            "confidence": "Confirmed",
            "missing_edge": "none for this observed baseline; this is not a privilege proof",
            "next_safe_step": "retain as post-analysis guard",
        },
        {
            "id": "P14-LIVE-002",
            "surface": "ordinary preferred HOME record",
            "caller_or_input": "read-only dumpsys package preferred-xml",
            "gate_or_policy": "record contains MAIN + HOME + DEFAULT",
            "binder_identity": "not applicable to read-only dump",
            "user_scope_or_target": "User 0",
            "sink_or_effect": "com.amazon.firelauncher/.Launcher preferred record",
            "observed_effect": "record and resolver agree on Fire Launcher",
            "evidence": "adb/phase14/PHASE14-READONLY-SERVICES-20260810-01/preferred_xml.stdout.txt",
            "confidence": "Confirmed",
            "missing_edge": "ordinary third-party preferred record was not rewritten in this phase",
            "next_safe_step": "use prior Phase 3C/3A records; do not repeat matrix",
        },
        {
            "id": "P14-LIVE-003",
            "surface": "Amazon private service visibility",
            "caller_or_input": "read-only service list and dumpsys",
            "gate_or_policy": "service names are listed; shell lookup is denied/not found",
            "binder_identity": "shell UID 2000 for read-only command",
            "user_scope_or_target": "device service-manager namespace",
            "sink_or_effect": "amazonactivitymanager, amazonwindowmanager, amazonusermanagerservice, amazonprofileservice not callable by this shell route",
            "observed_effect": "each dumpsys attempt returned Can't find service",
            "evidence": "adb/phase14/PHASE14-READONLY-SERVICES-20260810-01/service_list.stdout.txt; amazon_*_manager.stderr.txt",
            "confidence": "Confirmed",
            "missing_edge": "other authorized callers or exported wrappers remain unproven",
            "next_safe_step": "host-only Stub/manifest/SELinux join; no guessed transaction",
        },
        {
            "id": "P14-IPC-STATIC-001",
            "surface": "AmazonActivityManagerService prewarm authorization candidate",
            "caller_or_input": "IAmazonActivityManager.Proxy.preWarmApplicationForUser(String,int,int)",
            "gate_or_policy": "Context.checkCallingPermission(com.amazon.permission.APP_PREWARM) return is not visibly consumed before clearCallingIdentity",
            "binder_identity": "static method clears identity before package lookup/startProcessLocked; live call not performed",
            "user_scope_or_target": "method accepts target package and profile/user integers; no external input attribution closed",
            "sink_or_effect": "ApplicationInfo lookup then startProcessLocked(..., \"prewarm\", ...)",
            "observed_effect": "static authorization-anomaly candidate only; shell service route denied",
            "evidence": "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40535; findings/phase-6k-ipc-anomaly-candidates.md; output/tables/phase6k-ipc-anomaly-candidates.csv",
            "confidence": "Strong evidence",
            "missing_edge": "exact DEX register semantics, external caller, SELinux service access, input validation, security impact",
            "next_safe_step": "host-only parent Stub/callee and caller/permission/SELinux join",
        },
        {
            "id": "P14-IPC-STATIC-002",
            "surface": "prewarm legitimate caller boundary",
            "caller_or_input": "Amazon Alexa ExplicitIntentAction.prewarmApplicationProcess",
            "gate_or_policy": "privileged Amazon Alexa package; APP_PREWARM signature|amazon; target endpoint registry filters",
            "binder_identity": "privileged Alexa caller in preserved source; no ordinary app caller found",
            "user_scope_or_target": "target package plus foreground profile id",
            "sink_or_effect": "prewarm request only; no HOME/package-state writer in saved path",
            "observed_effect": "supports authorized-caller interpretation, not exploitability",
            "evidence": "artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282; manifest.txt:143-150",
            "confidence": "Strong evidence",
            "missing_edge": "complete universe of callers and runtime Binder/SELinux tuple",
            "next_safe_step": "static caller inventory only",
        },
    ])
    return rows


def write_table(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id", "surface", "caller_or_input", "gate_or_policy", "binder_identity",
        "user_scope_or_target", "sink_or_effect", "observed_effect", "evidence",
        "confidence", "missing_edge", "next_safe_step",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_call_graph(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = """flowchart TD
  A["ordinary app or shell"] --> B["service-manager / Binder lookup"]
  B -->|"Amazon private service lookup denied in saved shell capture"| C["no live private-service call"]
  D["KFT child/profile lifecycle"] --> E["supplied UserInfo.id"]
  E --> F["AmazonPackageManager facade"]
  F --> G["standard IPackageManager Binder"]
  G --> H["PMS package/component state gate"]
  H --> I["child/profile-scoped writer; User 0 route not closed"]
  J["Alexa privileged caller"] --> K["preWarmApplicationForUser"]
  K --> L["static permission-return anomaly candidate"]
  L --> M["clearCallingIdentity"]
  M --> N["getApplicationInfo / startProcessLocked"]
  N -. "no ordinary caller, HOME sink, or privilege transition observed" .-> O["host-only candidate closure"]
  P["OTA/recovery capability"] --> Q["fixed updater targets"]
  Q -. "verifier, caller, SELinux, and execution edges missing" .-> R["no low-privilege partition route established"]
"""
    path.write_text(text, encoding="utf-8")
    path.with_suffix(".md").write_text(
        """# Phase 14 control-surface graph (text form)\n\n
- Ordinary app/shell → Amazon private Binder lookup: the saved shell capture cannot find the private services.\n
- KFT child/profile lifecycle → supplied `UserInfo.id` → AmazonPackageManager → standard `IPackageManager` → PMS state gate. The saved chain is child/profile scoped; no User-0 Fire Launcher route is closed.\n
- Alexa privileged caller → `preWarmApplicationForUser()` → static permission-return anomaly candidate → process-prewarm sink. No ordinary caller or HOME/package-state sink is established.\n
- OTA/recovery capability → fixed updater targets. Verifier, caller, SELinux domain and execution edges remain missing.\n\n
Unknown edges are intentionally shown as dotted/negative edges; the graph is not an exploit claim.\n""",
        encoding="utf-8",
    )


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    inputs = list(WORKERS.values()) + WORKER_REPORTS + [
        CAPTURE / "metadata.json",
        CAPTURE / "sha256sums.txt",
        CAPTURE / "home_resolution.stdout.txt",
        CAPTURE / "preferred_xml.stdout.txt",
        CAPTURE / "service_list.stdout.txt",
        CAPTURE / "recent_logcat.stdout.txt",
        ROOT / "findings/phase-6k-ipc-anomaly-candidates.md",
        ROOT / "output/tables/phase6k-ipc-anomaly-candidates.csv",
    ]
    lines = [
        "# Phase 14 host-analysis input hashes",
        f"generated_utc={datetime.now(timezone.utc).isoformat()}",
        "mutation_performed=false",
        "",
    ]
    for item in inputs:
        if item.exists() and item.is_file():
            lines.append(f"{sha256(item)}  {item.relative_to(ROOT)}")
        else:
            lines.append(f"MISSING  {item.relative_to(ROOT)}")
    lines += [
        "",
        f"normalized_rows={len(rows)}",
        "confidence_vocabulary=Confirmed|Strong evidence|Probable|Hypothesis|Disproved|Unknown",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_evidence_index(rows: list[dict[str, str]], output: Path, table_hash: str, manifest_hash: str) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["confidence"]] = counts.get(row["confidence"], 0) + 1
    lines = [
        "# Phase 14 evidence index — host-only privilege-surface reconciliation",
        "",
        "This index is generated from preserved worker reports and the bounded",
        "read-only device capture. It does not imply a live exploit, Binder",
        "transaction, package mutation, root result, or partition write.",
        "",
        "## Inputs",
        "",
        f"- Normalized table SHA-256: `{table_hash}`",
        f"- Input manifest SHA-256: `{manifest_hash}`",
        "- Device capture: `adb/phase14/PHASE14-READONLY-SERVICES-20260810-01/`",
        "- Device capture metadata records `mutation=false`.",
        "- Worker CSVs and Markdown reports are preserved under `work/` and are",
        "  included as source artifacts for this phase.",
        "",
        "## Evidence records",
        "",
        "| Evidence ID | Source / observed fact | Confidence | Missing edge | Next safe step |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['id']}` | {row['surface']}; {row['observed_effect']} "
            f"(`{row['evidence']}`) | {row['confidence']} | "
            f"{row['missing_edge']} | {row['next_safe_step']} |"
        )
    lines += [
        "",
        "## Confidence counts",
        "",
        "| Confidence | Rows |",
        "|---|---:|",
    ]
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")
    lines += [
        "",
        "## Interpretation rule",
        "",
        "`Confirmed` is limited to directly preserved code, manifest, dump, or",
        "hash facts. `Strong evidence` is a bounded inference with an explicit",
        "missing edge. `Unknown` means the corpus did not close the edge; it is",
        "not evidence of a vulnerability. `Disproved` applies only to the exact",
        "tested route and conditions, not to every possible implementation.",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(rows: list[dict[str, str]], table: Path, evidence: Path, manifest: Path) -> None:
    report = f"""# Phase 14 — broad privilege-surface and asset reconciliation

## Executive result

Phase 14 widened the review beyond the Launcher to the PS7331 source/boot/OTA
assets, Amazon private IPC, KFT child/profile writers, OOBE/OTA lifecycle,
Settings/DPM surfaces, and preserved native/driver candidates. The work was
host-only plus one bounded read-only device capture. No Binder transaction,
driver/ioctl, root/exploit, updater/recovery execution, package/settings/user
mutation, Fire Launcher mutation, reboot, remount, or partition write was
performed.

**Confirmed:** the exact PS7331 source archive, OTA `.bin`, extracted boot and
selected framework/Amazon artifacts are present with preserved hashes and can
support offline analysis. The asset inventory is in
`work/luna_worker_cont_asset_inventory_20260810.csv`.

**Confirmed:** the read-only device capture still resolves User 0 HOME to
`com.amazon.firelauncher/.Launcher` with `priority=50`, `isDefault=true`, and
the saved ordinary preferred XML points to the same component. Recent Activity
Manager records show HOME starts to that component.

**Confirmed:** the service list contains Amazon private service names, but the
saved shell `dumpsys` attempts for `amazonactivitymanager`,
`amazonwindowmanager`, `amazonusermanagerservice`, and `amazonprofileservice`
all returned `Can't find service`. This closes the saved shell lookup route,
not every possible privileged caller.

**Strong evidence:** the KFT path is a real package/component-state writer,
but its closed semantic caller is child/profile lifecycle and the supplied
`UserInfo.id` remains the target. The corpus does not close an ordinary
app/shell → accepted tx3 → system-server identity → User 0 → Fire Launcher
state/HOME sink chain.

**Strong evidence, not a vulnerability finding:**
`preWarmApplicationForUser()` contains a static pattern in which
`checkCallingPermission(com.amazon.permission.APP_PREWARM)` is not visibly
consumed before `clearCallingIdentity()`, followed by ApplicationInfo lookup
and `startProcessLocked`. The saved legitimate caller is privileged Amazon
Alexa; the private service is not reachable through the saved shell route, and
no HOME/package-state sink or privilege transition was observed.

**Not established:** a low-privilege path that disables User 0 Fire Launcher,
changes formal HOME, or reaches an OTA/partition sink. The current highest-value
next step is host-only completion of caller, Stub, permission, SELinux service
context, input validation, and downstream-consumer joins for the prewarm and
remaining private services. Guessing Binder transactions or replaying OOBE/OTA
actions is not justified by this evidence.

## Device and asset guard

| Item | Observation | Status |
|---|---|---|
| Build | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| Preferred XML | Fire Launcher MAIN + HOME + DEFAULT record | Confirmed |
| Private-service shell lookup | Four selected `dumpsys` calls: `Can't find service` | Confirmed |
| Device mutation in this phase | `false` in capture metadata | Confirmed |
| PS7331 source tar | 2,563,328,975 bytes; SHA-256 recorded in worker inventory | Confirmed |
| PS7331 OTA `.bin` | 1,301,005,356 bytes; SHA-256 recorded in worker inventory | Confirmed |
| Boot image | Present in extracted PS7331 tree; hash recorded in worker inventory | Confirmed |

The full input hash list is
`firmware/manifests/PHASE14-HOST-ANALYSIS-20260810/sha256sums.txt`.

## 1. Broad control-surface result

The normalized machine-readable table is
`{table.relative_to(ROOT)}`. Each row separates caller, gate, Binder
identity, user scope, sink/effect, and the missing edge. The important
distinction is:

```text
capability or static writer
        ≠ accepted low-privilege caller
        ≠ identity handoff
        ≠ User 0 target
        ≠ observed HOME/package-state effect
```

### KFT and package-state writers

The KFT writer remains the closest Fire-specific state sink: it can enable
the Tahoe FreeTime launcher and disable Fire Launcher/Launcher3 for a supplied
child/profile `UserInfo.id`. The preserved closed caller is child creation or
child lifecycle. The missing external caller, service-manager/SELinux client
tuple, tx3 authorization, and User 0 parcel provenance prevent an exploit or
User-0 relay claim. This phase did not replay tx3 and did not construct a
forged `UserInfo`.

### Private ActivityManager prewarm candidate

The exact saved disassembly is
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40535`.
It contains the following bounded sequence:

```text
checkCallingPermission(APP_PREWARM)
clearCallingIdentity()
getApplicationInfo(package, 1024, user)
PreWarmCacheHelper...
startProcessLocked(..., "prewarm", ...)
```

This is a static authorization-review candidate. The saved Alexa source calls
it only after endpoint/package filtering and the package holds the Amazon
signature permission. The service lookup barrier and missing input/consumer
edges mean the correct status is **Strong evidence / Unknown**, not “root
primitive”.

### OTA and post-install

The updater script and native `update-binary` show fixed-target write
capabilities in recovery/updater context. The evidence does not close a
low-privilege caller, accepted-package verifier chain, AVB/rollback decision,
SELinux domain, or actual execution. No update or recovery path was run.

### OOBE, DPM, SettingsProvider, native and driver surfaces

These remain bounded static writers/capabilities with missing publication,
caller/UID/domain, user attribution, validation, or final HOME/package sink
edges. `BootAfterSystemOTAReceiver` is an OTA-gated OOBE lifecycle writer, not
a generic third-party HOME API. DCPMS and SettingsProvider evidence does not
close to Fire Launcher state. Driver nodes and native symbols are not treated
as reachable merely because an init rule, config, or symbol exists.

## 2. Evidence categories

See `{evidence.relative_to(ROOT)}` for the complete row-level index.

- **已證實 / Confirmed:** asset hashes, package/HOME dumps, service-list and
  read-only shell errors, preserved method/manifest structure.
- **高可信推論 / Strong evidence:** KFT child-scoped state-writer semantics;
  prewarm permission-return anomaly candidate; privileged caller boundary;
  OTA capability with missing reachability edges.
- **待驗證 / Unknown:** external private-service caller universe, SELinux
  client tuple, exact DEX register semantics of the prewarm check, arbitrary
  input validation, downstream HOME/package consumer, and driver/native
  reachability.
- **已排除 / Disproved:** the saved shell route directly finding the four
  selected private services; a closed ordinary app/shell → User 0 Fire state
  writer in the preserved corpus; any claim that OTA capability alone is an
  exploit.
- **因風險拒絕測試:** unknown `service call`, Binder parcel forgery, driver
  open/ioctl, root/exploit, OOBE/OTA broadcast replay, updater/recovery,
  sideload/flash, remount, SELinux or Fire Launcher state mutation.

## 3. Next minimal safe research target

1. Build a host-only parent Stub/callee map for `IAmazonActivityManager` and
   the four private services.
2. Join the service registration/init context, manifest declarations,
   permission definitions, `service_contexts`, and saved SELinux allow rules.
3. Enumerate all preserved callers of `preWarmApplicationForUser()` and
   prove target package/profile input validation and consumer scope.
4. Scan the exact PS7331 corpus for an exported wrapper or documented read-only
   API that reaches a package/HOME writer; if no closed edge appears, close the
   candidate as inaccessible rather than replaying it.
5. Keep the existing Fire Launcher baseline as a guard; do not repeat the
   disproved component-disable or priority matrices.

## Reproduction and QA

```sh
python3 tools/scripts/build_phase14_report.py --force
python3 - <<'PY'
import csv
from pathlib import Path
p = Path('output/tables/phase14-control-surface.csv')
rows = list(csv.DictReader(p.open()))
allowed = {{'Confirmed','Strong evidence','Probable','Hypothesis','Disproved','Unknown'}}
assert rows and all(r['confidence'] in allowed for r in rows)
assert all(len(r) == len(rows[0]) for r in csv.reader(p.open()))
print('rows=', len(rows), 'confidence=', sorted({{r['confidence'] for r in rows}}))
PY
git diff --check
```

Input manifest SHA-256 is generated by the builder; the report and graph are
derived outputs and can be regenerated without a device connection.
"""
    (ROOT / "findings/phase-14-report.md").write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite generated outputs")
    args = parser.parse_args()
    del args

    for path in list(WORKERS.values()) + WORKER_REPORTS:
        if not path.exists():
            raise SystemExit(f"missing input: {path}")
    if not CAPTURE.exists():
        raise SystemExit(f"missing capture: {CAPTURE}")

    rows = normalized_rows()
    if any(row["confidence"] not in ALLOWED for row in rows):
        raise SystemExit("invalid confidence vocabulary")

    table = ROOT / "output/tables/phase14-control-surface.csv"
    graph = ROOT / "output/call-graphs/phase14-control-surfaces.mmd"
    manifest = ROOT / "firmware/manifests/PHASE14-HOST-ANALYSIS-20260810/sha256sums.txt"
    evidence = ROOT / "findings/phase-14-evidence-index.md"
    report = ROOT / "findings/phase-14-report.md"

    write_table(rows, table)
    write_call_graph(graph)
    write_manifest(manifest, rows)
    write_evidence_index(rows, evidence, sha256(table), sha256(manifest))
    write_report(rows, table, evidence, manifest)

    print(json.dumps({
        "rows": len(rows),
        "table": str(table.relative_to(ROOT)),
        "table_sha256": sha256(table),
        "manifest": str(manifest.relative_to(ROOT)),
        "manifest_sha256": sha256(manifest),
        "capture": str(CAPTURE.relative_to(ROOT)),
        "worker_shapes": {key: csv_shape(path) for key, path in WORKERS.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
