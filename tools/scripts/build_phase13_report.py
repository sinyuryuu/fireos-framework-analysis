#!/usr/bin/env python3
"""Build the Phase 13 host-only privilege-surface closure.

This builder consumes preserved worker CSV/Markdown files and bounded
disassembly evidence.  It never invokes adb, Binder, a driver, recovery,
update-binary, or any device mutation.  Raw worker outputs are kept intact;
the generated table is a normalized review index whose missing edges remain
explicit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "adb/phase12/PHASE12-BASELINE-20260810-01"
POST_GUARD = ROOT / "adb/phase12/PHASE12-POST-HOST-GUARD-20260810-01"
WORKERS = {
    "kft": ROOT / "work/luna_worker_phase13_kft_tx3_20260810.csv",
    "exported": ROOT / "work/luna_worker_phase13_exported_inventory_20260810.csv",
    "driver": ROOT / "work/luna_worker_phase13_driver_join_20260810.csv",
    "policy-card": ROOT / "work/luna_worker_phase13_policy_card_closure_20260810.csv",
}
WORKER_REPORTS = [p.with_suffix(".md") for p in WORKERS.values()]
DISASSEMBLY = [
    ROOT / "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log",
    ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
]
IDENTITY_EVIDENCE = [
    ROOT / "artifacts/phase6mx-amazon-pm-callers-20260810-01/phase6mx-amazon-pm-callers.md",
    ROOT / "artifacts/phase6mx-amazon-pm-callers-20260810-01/caller-calls.csv",
    ROOT / "artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonusermanager_fosinit.xml",
]
ALLOWED = {"Confirmed", "Strong evidence", "Probable", "Hypothesis", "Disproved", "Unknown"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def csv_shape(path: Path) -> tuple[int, int, int]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        header = next(reader, [])
        rows = list(reader)
    malformed = sum(len(row) != len(header) for row in rows)
    return len(header), len(rows), malformed


def value(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        item = (row.get(key) or "").strip()
        if item:
            return item
    return "UNKNOWN"


def confidence(raw: str) -> str:
    normalized = raw.strip()
    mapping = {
        "HIGH": "Strong evidence",
        "MEDIUM": "Probable",
        "LOW": "Hypothesis",
        "High": "Strong evidence",
        "Medium": "Probable",
        "Low": "Hypothesis",
        "UNKNOWN": "Unknown",
        "Unknown": "Unknown",
        "CONFIRMED_PROXY": "Confirmed",
        "CONFIRMED_DISPATCH_PARTIAL_AUTHZ": "Confirmed",
        "CONFIRMED_SEMANTIC_CALLER_HIGH": "Strong evidence",
    }
    return mapping.get(normalized, normalized if normalized in ALLOWED else "Unknown")


def normalized_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for idx, row in enumerate(csv_rows(WORKERS["kft"]), start=1):
        raw_conf = value(row, "confidence")
        rows.append({
            "id": f"P13-KFT-{idx:03d}",
            "surface": "KFT/IAmazonUserManager",
            "entrypoint_or_source": value(row, "entrypoint"),
            "caller_or_input": value(row, "caller"),
            "gate_or_policy": value(row, "gate"),
            "binder_identity": value(row, "binder_identity"),
            "user_scope_or_target": value(row, "user_scope"),
            "sink_or_effect": value(row, "sink", "observed_effect"),
            "evidence": value(row, "evidence"),
            "confidence": confidence(raw_conf),
            "missing_edge": value(row, "missing_edge"),
        })

    for idx, row in enumerate(csv_rows(WORKERS["exported"]), start=1):
        rows.append({
            "id": f"P13-EXP-{idx:03d}",
            "surface": "exported component inventory",
            "entrypoint_or_source": f"{value(row, 'package')}/{value(row, 'component')} ({value(row, 'type')})",
            "caller_or_input": value(row, "entrypoint"),
            "gate_or_policy": value(row, "gate", "permission"),
            "binder_identity": value(row, "process_or_uid"),
            "user_scope_or_target": value(row, "user_scope"),
            "sink_or_effect": value(row, "sink", "observed_effect"),
            "evidence": value(row, "evidence"),
            "confidence": confidence(value(row, "confidence")),
            "missing_edge": value(row, "missing_edge"),
        })

    for idx, row in enumerate(csv_rows(WORKERS["policy-card"]), start=1):
        rows.append({
            "id": f"P13-PC-{idx:03d}",
            "surface": "policy/card data-flow",
            "entrypoint_or_source": f"{value(row, 'package')}/{value(row, 'entrypoint')}",
            "caller_or_input": value(row, "caller_identity"),
            "gate_or_policy": value(row, "permission"),
            "binder_identity": value(row, "caller_identity"),
            "user_scope_or_target": value(row, "user_scope"),
            "sink_or_effect": value(row, "sink", "observed_effect"),
            "evidence": value(row, "evidence"),
            "confidence": confidence(value(row, "confidence")),
            "missing_edge": value(row, "missing_edge"),
        })

    for idx, row in enumerate(csv_rows(WORKERS["driver"]), start=1):
        rows.append({
            "id": f"P13-DRV-{idx:03d}",
            "surface": value(row, "surface"),
            "entrypoint_or_source": value(row, "source_or_object"),
            "caller_or_input": value(row, "userspace_caller"),
            "gate_or_policy": value(row, "gate", "policy"),
            "binder_identity": value(row, "uid_or_domain"),
            "user_scope_or_target": value(row, "device_node"),
            "sink_or_effect": value(row, "sink", "api_or_ioctl"),
            "evidence": value(row, "evidence"),
            "confidence": "Unknown",
            "missing_edge": value(row, "missing_edge"),
        })

    # This is the key host-only identity handoff closure performed by the main
    # agent.  It is deliberately separate from the worker rows so that the
    # Binder identity inference cannot be confused with a live transaction.
    rows.extend([
        {
            "id": "P13-ID-001",
            "surface": "AmazonPackageManager identity handoff",
            "entrypoint_or_source": "AmazonPackageManagerImpl.<init>(PackageManager, Context)",
            "caller_or_input": "AmazonUserManagerService obtains Context.getPackageManager() and casts to AmazonPackageManager",
            "gate_or_policy": "constructor obtains amazonpackagemanager then standard package Binder",
            "binder_identity": "system_server process for the KFT service implementation; runtime transaction not traced",
            "user_scope_or_target": "not selected by this constructor",
            "sink_or_effect": "mPM is an IPackageManager proxy to the standard package service",
            "evidence": "boot-fosframework/disassembly.log:366047-366081; fosservices/disassembly.log:55072-55076",
            "confidence": "Strong evidence",
            "missing_edge": "runtime attribution and exact process/SELinux domain capture",
        },
        {
            "id": "P13-ID-002",
            "surface": "AmazonPackageManager identity handoff",
            "entrypoint_or_source": "AmazonPackageManagerImpl.setApplicationEnabledSetting(String, int, int, int)",
            "caller_or_input": "KFT BinderService.enableKftLauncher(UserInfo)",
            "gate_or_policy": "delegates to IPackageManager.setApplicationEnabledSetting(..., opPackageName)",
            "binder_identity": "outgoing Binder caller is the process executing the facade; no clearCallingIdentity before this call",
            "user_scope_or_target": "UserInfo.id supplied by KFT method",
            "sink_or_effect": "standard PMS application enabled-state setter; Fire Launcher target is passed by caller",
            "evidence": "boot-fosframework/disassembly.log:368214-368229; fosservices/disassembly.log:54310-54324",
            "confidence": "Strong evidence",
            "missing_edge": "PMS runtime trace, inherited tx3 authorization and actual User-0 invocation",
        },
        {
            "id": "P13-ID-003",
            "surface": "AmazonPackageManager identity handoff",
            "entrypoint_or_source": "AmazonPackageManagerImpl.setComponentEnabledSetting(ComponentName, int, int, int)",
            "caller_or_input": "KFT BinderService.enableKftLauncher(UserInfo)",
            "gate_or_policy": "delegates to IPackageManager.setComponentEnabledSetting(...)",
            "binder_identity": "outgoing Binder caller is the process executing the facade; no clearCallingIdentity before this call",
            "user_scope_or_target": "UserInfo.id supplied by KFT method",
            "sink_or_effect": "standard PMS component enabled-state setter for Tahoe FreeTimeLauncherActivity",
            "evidence": "boot-fosframework/disassembly.log:368254-368263; fosservices/disassembly.log:54300-54309",
            "confidence": "Strong evidence",
            "missing_edge": "PMS runtime trace, inherited tx3 authorization and actual User-0 invocation",
        },
        {
            "id": "P13-ID-004",
            "surface": "KFT writer scope",
            "entrypoint_or_source": "AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)",
            "caller_or_input": "tx3 dispatch or local child-user lifecycle",
            "gate_or_policy": "method-local slice has no visible UID/permission/cross-user check before tryEnableKftLauncherComponent; helper applicability unresolved",
            "binder_identity": "incoming identity is preserved until later DPM clearCallingIdentity, which is after package writers",
            "user_scope_or_target": "all three package/component writes receive UserInfo.id; child lifecycle is the only closed semantic caller",
            "sink_or_effect": "enables Tahoe launcher, disables Fire Launcher and Launcher3 for supplied user; no formal HOME setter",
            "evidence": "fosservices/disassembly.log:54297-54325,54415-54478,54847-54875",
            "confidence": "Strong evidence",
            "missing_edge": "superclass/inherited authorization, service declaration permission, SELinux client allow and PMS downstream gate",
        },
    ])
    return rows


def md(value_text: str) -> str:
    return value_text.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="allow replacing generated Phase 13 files")
    args = parser.parse_args()

    required = [BASELINE / "metadata.json", BASELINE / "sha256sums.txt", POST_GUARD / "metadata.json", POST_GUARD / "sha256sums.txt"]
    required += list(WORKERS.values()) + WORKER_REPORTS + DISASSEMBLY + IDENTITY_EVIDENCE
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))

    out_files = [
        ROOT / "findings/phase-13-report.md",
        ROOT / "findings/phase-13-evidence-index.md",
        ROOT / "output/tables/phase13-control-surface.csv",
        ROOT / "output/call-graphs/phase13-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase13-control-surfaces.md",
        ROOT / "firmware/manifests/PHASE13-HOST-ANALYSIS-20260810/sha256sums.txt",
    ]
    if not args.force:
        existing = [str(path) for path in out_files if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))

    normalized = normalized_rows()
    fields = [
        "id", "surface", "entrypoint_or_source", "caller_or_input", "gate_or_policy",
        "binder_identity", "user_scope_or_target", "sink_or_effect", "evidence",
        "confidence", "missing_edge",
    ]
    table_path = ROOT / "output/tables/phase13-control-surface.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)

    shapes = {name: csv_shape(path) for name, path in WORKERS.items()}
    input_files = list(dict.fromkeys(required))
    manifest_dir = ROOT / "firmware/manifests/PHASE13-HOST-ANALYSIS-20260810"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "sha256sums.txt"
    with manifest_path.open("w", encoding="utf-8") as stream:
        for path in sorted(input_files):
            stream.write(f"{sha256(path)}  {path.relative_to(ROOT)}\n")

    evidence = [
        "# Phase 13 evidence index",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "This is a host-only closure. It does not claim that an external caller",
        "can invoke tx3, construct UserInfo for User 0, bypass PMS, open a driver,",
        "or mutate Fire Launcher state. Unknown edges remain explicitly unknown.",
        "",
        "## Evidence IDs",
        "",
        "| ID | Finding | Source | Confidence | Missing edge |",
        "|---|---|---|---|---|",
    ]
    evidence_descriptions = {
        "P13-KFT-001": ("tx3 Stub enforces descriptor, decodes nullable UserInfo and dispatches", "boot-fosframework/disassembly.log:370674-370777", "Confirmed", "inherited/superclass authorization and full cross-user gate"),
        "P13-KFT-002": ("tx3 Proxy parcels UserInfo and calls transact(3)", "boot-fosframework/disassembly.log:370398-370443", "Confirmed", "external APK/native caller and UID/signature"),
        "P13-KFT-003": ("BinderService tx3 implementation reaches supplied-user KFT path", "fosservices/disassembly.log:54415-54478", "Strong evidence", "authorization and PMS downstream gates"),
        "P13-KFT-004": ("createChildUser is the closed semantic caller and passes returned child UserInfo", "boot-fosframework/disassembly.log:369180-369243", "Strong evidence", "upstream runtime caller and caller authorization"),
        "P13-ID-001": ("AmazonPackageManagerImpl obtains standard package Binder after private service", "boot-fosframework/disassembly.log:366047-366081; fosservices/disassembly.log:55072-55076", "Strong evidence", "runtime attribution/SELinux capture"),
        "P13-ID-002": ("4-argument application-state facade calls IPackageManager with op package", "boot-fosframework/disassembly.log:368214-368229; fosservices/disassembly.log:54310-54324", "Strong evidence", "runtime PMS trace, tx3 auth, User-0 invocation"),
        "P13-ID-003": ("4-argument component-state facade calls IPackageManager", "boot-fosframework/disassembly.log:368254-368263; fosservices/disassembly.log:54300-54309", "Strong evidence", "runtime PMS trace, tx3 auth, User-0 invocation"),
        "P13-ID-004": ("KFT writer uses supplied UserInfo.id for three package/component writers", "fosservices/disassembly.log:54297-54325,54415-54478", "Strong evidence", "inherited auth, service permission, SELinux client allow, PMS gate"),
        "P13-EXP": ("Exported component inventory is not a route without permission, identity, user and sink closure", "work/luna_worker_phase13_exported_inventory_20260810.csv", "Probable", "component-specific caller and sink closure"),
        "P13-PC": ("Parental/card paths close to UI/card/DPM workflows, not arbitrary HOME/package writers", "work/luna_worker_phase13_policy_card_closure_20260810.csv", "Strong evidence", "runtime grants and complete policy call graph"),
        "P13-DRV": ("Seven driver surfaces retain missing caller/policy/identity/validation/effect edges", "work/luna_worker_phase13_driver_join_20260810.csv", "Unknown", "compiled delivery, merged policy, native caller and effect"),
    }
    for evidence_id, (finding, source, conf, gap) in evidence_descriptions.items():
        evidence.append(f"| `{evidence_id}` | {md(finding)} | `{md(source)}` | {conf} | {md(gap)} |")
    evidence += [
        "",
        "## Worker CSV shape and hashes",
        "",
        "| Input | Rows | Columns | Malformed rows | SHA-256 |",
        "|---|---:|---:|---:|---|",
    ]
    for name, path in WORKERS.items():
        cols, rows_count, malformed = shapes[name]
        evidence.append(f"| `{name}` | {rows_count} | {cols} | {malformed} | `{sha256(path)}` |")
    evidence += [
        "",
        "## Baseline and identity inputs",
        "",
        f"- Phase 12 baseline manifest: `{sha256(BASELINE / 'sha256sums.txt')}`",
        f"- Phase 12 post-host guard manifest: `{sha256(POST_GUARD / 'sha256sums.txt')}`",
        f"- Normalized Phase 13 table: `{sha256(table_path)}`",
        "- The manifest under `firmware/manifests/PHASE13-HOST-ANALYSIS-20260810/` records all preserved inputs used by the builder.",
        "",
        "## Confidence semantics",
        "",
        "`Confirmed` is reserved for a directly preserved code/data fact. `Strong evidence` is a bounded static inference whose listed missing edge prevents a reachability or exploit claim. `Unknown` means the corpus did not close the edge. `Disproved` applies only to the specific tested route, never to every possible implementation.",
    ]
    (ROOT / "findings/phase-13-evidence-index.md").write_text("\n".join(evidence) + "\n", encoding="utf-8")

    report = f"""# Phase 13 — KFT, exported components, policy/card and driver closure

## Executive result

Phase 13 broadened the analysis beyond the Launcher itself. It covered the
KFT `IAmazonUserManager` transaction 3 path, the Amazon package-manager
facade used by that path, exported Amazon components, parental/card policy
flows, and seven previously open driver surfaces. The work was host-only and
read-only. No Binder transaction was sent, no `UserInfo` parcel was forged, no
driver node or ioctl was opened, and no package, HOME, Fire Launcher, OTA,
recovery, partition, SELinux or system state was changed.

**Confirmed:** the saved code contains a real `IAmazonUserManager` tx3
Stub/Proxy pair. The Stub decodes a nullable `UserInfo` and dispatches to
`AmazonUserManagerService$BinderService.enableKftLauncher(UserInfo)`.

**Confirmed:** the only closed semantic caller in the preserved corpus is
`AmazonUserManagerImpl.createChildUser(String)`. It creates a child
user and passes the returned child `UserInfo` through tx3. This is not a
User-0 caller and is not a HOME setter.

**Strong evidence:** the KFT writer passes the supplied `UserInfo.id` to three
package/component state writers: enable Tahoe FreeTime Launcher, disable
`com.amazon.firelauncher`, and disable `com.android.launcher3`. The method has
no visible hard-coded nonzero user check in the bounded slice, but the actual
external tx3 caller, authorization, user scope and PMS downstream decision are
not closed.

**Strong evidence:** the KFT path's `AmazonPackageManagerImpl` delegates its
four-argument state calls to the standard `IPackageManager` Binder proxy. The
facade constructor obtains the standard `package` service after the private
`amazonpackagemanager` service. Because the KFT service implementation is in
the system-server service corpus and no `clearCallingIdentity()` precedes
these package calls, the static model is consistent with PMS seeing the
system-server caller for the internal call. This is a serious confused-deputy
candidate, not a proven external vulnerability: no external caller has been
joined, no tx3 authorization has been demonstrated, and no transaction was
sent.

**Unknown:** the exported components and all seven driver surfaces do not
close a new low-privilege route. Their missing caller, permission/SELinux,
user-scope, validation and sink edges remain in the machine-readable table.

## Baseline and safety

The Phase 12 serial-bound baseline remains the current device reference:
[`adb/phase12/PHASE12-BASELINE-20260810-01`](../adb/phase12/PHASE12-BASELINE-20260810-01).
Its post-host guard preserved the same PS7331 fingerprint, User 0 and formal
Fire HOME. Phase 13 performed no device operation, so there is no mutation
rollback to report.

| Item | Result | Status |
|---|---|---|
| Serial | `G001LT0511550CFT` | Confirmed from Phase 12 baseline |
| Fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed from Phase 12 baseline |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed from Phase 12 baseline |
| SELinux | Enforcing | Confirmed from Phase 12 baseline |
| Phase 13 mutation | None | Confirmed |

## 1. KFT tx3 call path

The bounded static path is:

```text
AmazonUserManagerImpl.createChildUser(String)
  -> createUser(name, 0x8000)
  -> IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)
  -> Parcel(UserInfo) + transact(3)
  -> IAmazonUserManager.Stub.onTransact(3)
  -> BinderService.enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent(UserInfo)
  -> AmazonPackageManagerImpl
  -> IPackageManager Binder proxy
  -> PMS package/component state setters
```

Line/offset evidence:

- Proxy parcel and `transact(3)`: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:370398-370443`.
- Stub descriptor enforcement, nullable parcel decode and tx3 dispatch:
  `.../boot-fosframework/disassembly.log:370674-370777`, tx3 at `370737-370745`.
- Service implementation: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54415-54478`.
- State writer: `.../fosservices/disassembly.log:54297-54325`.
- Closed child semantic caller: `.../boot-fosframework/disassembly.log:369180-369243`.

The method-local slice does not show `Binder.getCallingUid`, a permission
check, or an explicit cross-user check before `tryEnableKftLauncherComponent`.
That observation is **Strong evidence**, not proof of missing authorization:
superclass/inherited checks, service declaration permission, SELinux service
manager rules, and PMS's own checks remain open.

## 2. Package-manager identity handoff

`AmazonPackageManagerImpl.<init>(PackageManager, Context)` obtains
`amazonpackagemanager`, then obtains `ServiceManager.getService("package")`
and converts it to `IPackageManager`. The four-argument
`setApplicationEnabledSetting` and `setComponentEnabledSetting` methods call
that `mPM` proxy and pass the context op-package name. They do not call
`clearCallingIdentity()` in the bounded method body.

This closes the static *internal* handoff to standard PMS, but not an external
caller-to-tx3 path. The relevant distinction is:

| Question | Status |
|---|---|
| Does the facade use the standard package Binder? | Confirmed |
| Does KFT use the four-argument facade state methods? | Confirmed |
| Would an internal system-server call carry its process Binder identity to PMS? | Strong evidence from Binder call structure |
| Can shell or an ordinary app invoke tx3? | Not established; saved shell lookup route is denied, ordinary app only performed descriptor tests |
| Can an external caller supply `UserInfo.id == 0` and pass all gates? | Unknown |

## 3. What is and is not a Fire Launcher sink

The KFT writer does contain a Fire Launcher package-state target, but its
target is a supplied user and the writer is reached through a child-profile
lifecycle in the only closed caller chain. It does **not** call
`setHomeActivity`, `replacePreferredActivity`, or a formal HOME resolver API.
Therefore it cannot, from this evidence alone, explain User-0 HOME selection.

The exact protected-package gate observed in earlier phases remains relevant
when PMS receives a direct state mutation. A system-server internal caller may
be authorized for a child-user operation; that does not establish that an
ordinary caller can turn the same code into a User-0 Fire disable.

## 4. Exported component inventory

The inventory contains Fire Launcher activities/receivers/providers,
Parental Controls, Settings and SystemUI entries. Exported status or a named
permission is not treated as an exploit. The current bounded findings are:

- Fire Launcher `Launcher` is an exported HOME activity; no new state writer
  was recovered from that entry.
- `StartEditModeReceiver` is permission-gated and starts edit mode; its source
  does not close to PackageManager or HOME default mutation.
- Card provider/agent routes close to card database, blacklist and card-read
  state. They do not close to package enabled state or HOME selection.
- Parental restriction provider/service routes close to auth/dialog flow.
  Fixed policy-map entries can reach DPM hidden/restriction APIs, but the
  supplied provider package name is not connected to that map in the saved
  corpus.
- SystemUI keyguard and Settings entries have unresolved method-level gates;
  no new Fire Launcher writer was proven.

## 5. Driver and native surface join

CMDQ/MDP, ION, M4U, uinput, perfmgr, Amazon driver-test and RPMB remain
`Unknown`. Source handlers, Kconfig, init node metadata, file contexts or
library symbols are capabilities, not reachability. Each row is missing at
least one of final object/DT delivery, merged SELinux allow, native caller and
UID/domain, input validation, or effect closure. No `/dev` node was opened and
no ioctl was attempted.

## 6. Overall decision

**No new reproducible low-privilege route to disable User-0 Fire Launcher or
replace formal HOME was established.** The highest-value remaining static
question is the authorization boundary around tx3: service declaration
permission, inherited Stub/service checks, SELinux service-manager access for
candidate domains, and the exact upstream caller. That work must remain
host-only unless a natural, user-driven child-profile lifecycle supplies an
observable call. Forging tx3, guessing a `service call` parcel, or trying a
User-0 `UserInfo` is not justified and is not part of this phase.

## Status vocabulary

- **已證實 / Confirmed:** directly preserved code, manifest, baseline or
  transaction structure.
- **高可信推論 / Strong evidence:** bounded static inference with explicit
  missing edges.
- **待驗證 / Unknown:** a required edge is not present in the corpus.
- **已排除 / Disproved:** only a specifically tested route, such as the saved
  shell service lookup, not every possible implementation.
- **因風險拒絕測試:** unknown Binder parcels, driver opens/ioctls, OTA or
  recovery execution, root, partition writes and Fire Launcher mutations.

## Reproduction

```sh
python3 tools/scripts/build_phase13_report.py --force
python3 - <<'PY'
import csv
from pathlib import Path
p = Path('output/tables/phase13-control-surface.csv')
rows = list(csv.DictReader(p.open()))
allowed = {{'Confirmed','Strong evidence','Probable','Hypothesis','Disproved','Unknown'}}
assert rows and all(r['confidence'] in allowed for r in rows)
print(f'rows={{len(rows)}} confidence={{sorted(set(r["confidence"] for r in rows))}}')
PY
sha256sum firmware/manifests/PHASE13-HOST-ANALYSIS-20260810/sha256sums.txt
```

The normalized evidence table is
[`output/tables/phase13-control-surface.csv`](../output/tables/phase13-control-surface.csv),
and the detailed index is
[`findings/phase-13-evidence-index.md`](phase-13-evidence-index.md).
"""
    (ROOT / "findings/phase-13-report.md").write_text(report, encoding="utf-8")

    mmd = """flowchart TD
  A["Unknown external caller"] -. "caller/UID/package unknown" .-> B["amazonusermanagerservice tx3"]
  C["AmazonUserManagerImpl.createChildUser"] --> D["IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)"]
  D --> E["Parcel UserInfo + transact(3)"]
  E --> F["IAmazonUserManager.Stub.onTransact(3)"]
  F --> G["BinderService.enableKftLauncher(UserInfo)"]
  G -. "authorization edge unresolved" .-> H["tryEnableKftLauncherComponent"]
  G --> I["AmazonPackageManagerImpl facade"]
  I --> J["ServiceManager package -> IPackageManager proxy"]
  J --> K["PackageManagerService setters"]
  K --> L["Tahoe FreeTimeLauncherActivity enabled"]
  K --> M["Fire Launcher disabled for supplied user"]
  K --> N["Launcher3 disabled for supplied user"]
  H -. "DPM/child lifecycle scope" .-> O["empowerKftUser(UserInfo)"]
  P["ordinary app: descriptor-only historical test"] -. "no tx3" .-> B
  Q["shell UID: saved service-manager lookup denied"] -. "no handle" .-> B
  R["driver/static surfaces"] -. "caller/policy/identity/sink unknown" .-> S["No closed low-privilege route"]
  M -. "not formal HOME setter" .-> S
"""
    (ROOT / "output/call-graphs/phase13-control-surfaces.mmd").write_text(mmd, encoding="utf-8")
    (ROOT / "output/call-graphs/phase13-control-surfaces.md").write_text(
        "# Phase 13 call graph (plain text)\n\n" +
        "```text\n" +
        "Unknown external caller [UNCONFIRMED]\n"
        "  -> amazonusermanagerservice tx3 [caller/UID/package UNCONFIRMED]\n"
        "AmazonUserManagerImpl.createChildUser\n"
        "  -> IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)\n"
        "  -> Parcel(UserInfo) + transact(3)\n"
        "  -> IAmazonUserManager.Stub.onTransact(3)\n"
        "  -> BinderService.enableKftLauncher(UserInfo)\n"
        "  -> tryEnableKftLauncherComponent(UserInfo) [authz UNCONFIRMED]\n"
        "  -> AmazonPackageManagerImpl\n"
        "  -> standard package Binder / IPackageManager\n"
        "  -> PMS setters\n"
        "     -> Tahoe FreeTimeLauncher enabled for supplied user\n"
        "     -> Fire Launcher disabled for supplied user\n"
        "     -> Launcher3 disabled for supplied user\n"
        "No formal HOME setter; User-0 external reachability UNCONFIRMED.\n"
        "```\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
