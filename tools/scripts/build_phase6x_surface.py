#!/usr/bin/env python3
"""Build the Phase 6X cross-surface evidence bundle.

The script is host-only.  It reads preserved reports and a read-only device
snapshot, normalizes evidence into a single ledger, and writes reproducible
Markdown/CSV/Mermaid outputs.  It never contacts a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CONTROL_HEADER = [
    "evidence_id",
    "phase",
    "surface",
    "source",
    "caller",
    "gate",
    "identity_scope",
    "sink",
    "observed_effect",
    "confidence",
    "evidence_file",
    "evidence_sha256",
    "status",
    "scope",
]

TEST_HEADER = [
    "evidence_id",
    "route",
    "test_ids",
    "command_or_method",
    "result",
    "restore_state",
    "duplicate_of",
    "next_minimum_probe",
    "confidence",
    "evidence_file",
    "evidence_sha256",
    "status",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def require(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))


def normalize_prior(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        evidence_id = row.get("id", "") or row.get("evidence_id", "")
        if not evidence_id:
            evidence_id = f"6WL-ROW-{index:03d}"
        normalized.append({
            "evidence_id": evidence_id,
            "phase": "6WL",
            "surface": row.get("surface_family") or row.get("surface") or row.get("sink_class", ""),
            "source": row.get("source_csv", ""),
            "caller": row.get("caller_or_publisher", ""),
            "gate": row.get("permission_selinux_service_manager_gate", ""),
            "identity_scope": row.get("user_scope", "") or row.get("identity_policy_sink", ""),
            "sink": row.get("sink_class", "") or row.get("operation", ""),
            "observed_effect": row.get("observed_effect", "") or row.get("canonical_result", "") or row.get("result", ""),
            "confidence": row.get("confidence", ""),
            "evidence_file": row.get("evidence_location", "") or row.get("evidence_file", ""),
            "evidence_sha256": row.get("evidence_sha256", "") or row.get("provenance_sha256", ""),
            "status": row.get("integrated_status", "") or row.get("status", ""),
            "scope": "previous Phase 6WL integrated corpus",
        })
    return normalized


def normalize_worker(path: Path, phase: str) -> list[dict[str, str]]:
    rows = read_csv(path)
    result: list[dict[str, str]] = []
    for row in rows:
        result.append({
            "evidence_id": row.get("evidence_id", ""),
            "phase": phase,
            "surface": row.get("surface", ""),
            "source": row.get("source", ""),
            "caller": row.get("caller", ""),
            "gate": row.get("gate", ""),
            "identity_scope": row.get("identity_scope", ""),
            "sink": row.get("sink", "") or row.get("node_or_api", ""),
            "observed_effect": row.get("observed_effect", ""),
            "confidence": row.get("confidence", ""),
            "evidence_file": row.get("evidence_file", ""),
            "evidence_sha256": row.get("evidence_sha256", ""),
            "status": row.get("status", ""),
            "scope": "new Phase 6X host-only evidence",
        })
    return result


def normalize_permission(path: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in read_csv(path):
        result.append({
            "evidence_id": row.get("evidence_id", ""),
            "phase": "6Y-PERM",
            "surface": row.get("surface", ""),
            "source": row.get("definition_or_component", ""),
            "caller": row.get("caller", ""),
            "gate": row.get("gate", "") + "; protection=" + row.get("protection_level", ""),
            "identity_scope": row.get("identity_scope", ""),
            "sink": row.get("sink", ""),
            "observed_effect": row.get("observed_effect", ""),
            "confidence": row.get("confidence", ""),
            "evidence_file": row.get("evidence_file", ""),
            "evidence_sha256": row.get("evidence_sha256", ""),
            "status": row.get("status", ""),
            "scope": "new Phase 6Y permission residual",
        })
    return result


def normalize_components(path: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in read_csv(path):
        result.append({
            "evidence_id": row.get("evidence_id", ""),
            "phase": "6Z-COMPONENT",
            "surface": row.get("surface", ""),
            "source": row.get("component_or_key", ""),
            "caller": row.get("caller", ""),
            "gate": row.get("gate", "") + "; action=" + row.get("action", ""),
            "identity_scope": row.get("identity_scope", ""),
            "sink": row.get("sink", ""),
            "observed_effect": row.get("observed_effect", ""),
            "confidence": row.get("confidence", ""),
            "evidence_file": row.get("evidence_file", ""),
            "evidence_sha256": row.get("evidence_sha256", ""),
            "status": row.get("status", ""),
            "scope": "new Phase 6Z exported/OOBE residual",
        })
    return result


def live_rows(snapshot: Path, scope_snapshot: Path) -> list[dict[str, str]]:
    def rel(path: Path) -> str:
        return str(path.relative_to(ROOT))

    def file_hash(name: str, base: Path = snapshot) -> str:
        path = base / name
        return digest(path) if path.exists() else "MISSING"

    rows = [
        {
            "evidence_id": "6X-LIVE-001",
            "phase": "6X-LIVE",
            "surface": "device identity",
            "source": "adb read-only snapshot",
            "caller": "adb shell getprop",
            "gate": "none; observation only",
            "identity_scope": "serial G001LT0511550CFT; User 0 current",
            "sink": "build fingerprint",
            "observed_effect": "PS7331.4463N/0031575863040; incremental 0031575863172; security patch 2024-08-01",
            "confidence": "Confirmed observation",
            "evidence_file": rel(snapshot / "getprop.stdout.txt"),
            "evidence_sha256": file_hash("getprop.stdout.txt"),
            "status": "OBSERVED_READ_ONLY",
            "scope": "exact serial current snapshot",
        },
        {
            "evidence_id": "6X-LIVE-002",
            "phase": "6X-LIVE",
            "surface": "HOME User 0",
            "source": "cmd package resolve-activity",
            "caller": "shell read-only query",
            "gate": "resolver observation",
            "identity_scope": "User 0",
            "sink": "formal HOME resolver",
            "observed_effect": "com.amazon.firelauncher/.Launcher; priority 50",
            "confidence": "Confirmed observation",
            "evidence_file": rel(snapshot / "home_user0.stdout.txt"),
            "evidence_sha256": file_hash("home_user0.stdout.txt", snapshot),
            "status": "OBSERVED_READ_ONLY",
            "scope": "exact serial current snapshot",
        },
        {
            "evidence_id": "6X-LIVE-003",
            "phase": "6X-LIVE",
            "surface": "HOME candidates User 0",
            "source": "cmd package query-activities",
            "caller": "shell read-only query",
            "gate": "resolver observation",
            "identity_scope": "User 0",
            "sink": "candidate set",
            "observed_effect": "Fire 50, Microsoft 0, FallbackHome -1000",
            "confidence": "Confirmed observation",
            "evidence_file": rel(snapshot / "home_candidates_user0.stdout.txt"),
            "evidence_sha256": file_hash("home_candidates_user0.stdout.txt", snapshot),
            "status": "OBSERVED_READ_ONLY",
            "scope": "exact serial current snapshot",
        },
        {
            "evidence_id": "6X-LIVE-004",
            "phase": "6X-LIVE",
            "surface": "HOME candidates User 10",
            "source": "cmd package resolve/query-activities",
            "caller": "shell read-only query",
            "gate": "resolver observation",
            "identity_scope": "User 10 test profile",
            "sink": "candidate set",
            "observed_effect": "FallbackHome only; Fire is user-scoped disabled in saved package dump",
            "confidence": "Confirmed observation",
            "evidence_file": rel(scope_snapshot / "home_user10.stdout.txt"),
            "evidence_sha256": digest(scope_snapshot / "home_user10.stdout.txt"),
            "status": "OBSERVED_READ_ONLY",
            "scope": "exact serial current snapshot; profile scope only",
        },
        {
            "evidence_id": "6X-LIVE-005",
            "phase": "6X-LIVE",
            "surface": "Fire Launcher per-user state",
            "source": "dumpsys package com.amazon.firelauncher",
            "caller": "shell read-only dump",
            "gate": "package-state observation",
            "identity_scope": "User 0 enabled=0; User 10 enabled=2",
            "sink": "package state",
            "observed_effect": "User 0 installed/visible/enabled; User 10 disabled; no cross-user User 0 effect observed",
            "confidence": "Confirmed observation",
            "evidence_file": rel(scope_snapshot / "firelauncher_package.stdout.txt"),
            "evidence_sha256": digest(scope_snapshot / "firelauncher_package.stdout.txt"),
            "status": "OBSERVED_READ_ONLY",
            "scope": "exact serial current snapshot; user scope is material",
        },
        {
            "evidence_id": "6X-LIVE-006",
            "phase": "6X-LIVE",
            "surface": "preferred HOME record",
            "source": "dumpsys package preferred-xml",
            "caller": "shell read-only dump",
            "gate": "preferred state observation",
            "identity_scope": "User 0 record",
            "sink": "ordinary preferred activity",
            "observed_effect": "preferred record names com.amazon.firelauncher/.Launcher with MAIN/HOME/DEFAULT filter",
            "confidence": "Confirmed observation",
            "evidence_file": rel(scope_snapshot / "preferred_activities.stdout.txt"),
            "evidence_sha256": digest(scope_snapshot / "preferred_activities.stdout.txt"),
            "status": "OBSERVED_READ_ONLY",
            "scope": "exact serial current snapshot",
        },
    ]
    return rows


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=header,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    prior_csv = ROOT / "output/tables/phase6wl-control-surface.csv"
    ipc_csv = ROOT / "work/luna_worker_phase6x_ipc_20260810.csv"
    ota_csv = ROOT / "work/luna_worker_phase6x_ota_20260810.csv"
    driver_csv = ROOT / "work/luna_worker_phase6xg_driver_20260810.csv"
    tests_csv = ROOT / "work/luna_worker_phase6x_reconcile_20260810.csv"
    permission_csv = ROOT / "work/luna_worker_phase6y_permission_20260810.csv"
    component_csv = ROOT / "work/luna_worker_phase6z_components_20260810.csv"
    inputs = [
        prior_csv,
        ROOT / "findings/phase-6wl-report.md",
        ipc_csv,
        ROOT / "work/luna_worker_phase6x_ipc_20260810.md",
        ota_csv,
        ROOT / "work/luna_worker_phase6x_ota_20260810.md",
        driver_csv,
        ROOT / "work/luna_worker_phase6xg_driver_20260810.md",
        tests_csv,
        ROOT / "work/luna_worker_phase6x_reconcile_20260810.md",
        permission_csv,
        ROOT / "work/luna_worker_phase6y_permission_20260810.md",
        component_csv,
        ROOT / "work/luna_worker_phase6z_components_20260810.md",
        ROOT / "work/luna_worker_ota_canonicalization_provenance_20260810.md",
        ROOT / "firmware/manifests/OTA-20260803-01/README.md",
        ROOT / "firmware/extracted/PS7331/ota.prop",
        ROOT / "firmware/extracted/PS7331-SOURCE-20250617/platform.tar",
        ROOT / "adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/getprop.stdout.txt",
        ROOT / "adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/sha256sums.txt",
        ROOT / "adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/home_user10.stdout.txt",
        ROOT / "adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/firelauncher_package.stdout.txt",
        ROOT / "adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/preferred_activities.stdout.txt",
        ROOT / "adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/sha256sums.txt",
    ]
    require(inputs)

    output_files = [
        ROOT / "findings/phase-6x-report.md",
        ROOT / "findings/phase-6x-evidence-index.md",
        ROOT / "findings/phase-6x-source-scope.md",
        ROOT / "output/tables/phase6x-control-surface.csv",
        ROOT / "output/tables/phase6x-test-reconciliation.csv",
        ROOT / "output/tables/phase6x-source-scope.csv",
        ROOT / "output/tables/phase6x-input-manifest.sha256",
        ROOT / "output/call-graphs/phase6x-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase6x-control-surfaces.md",
    ]
    if args.dry_run:
        print("host-only dry run; no output written")
        for path in output_files:
            print(path.relative_to(ROOT))
        return 0
    if not args.force and any(path.exists() for path in output_files):
        raise SystemExit("refusing to overwrite output; use --force")

    prior = normalize_prior(read_csv(prior_csv))
    ipc = normalize_worker(ipc_csv, "6X-IPC")
    ota = normalize_worker(ota_csv, "6X-OTA")
    driver = normalize_worker(driver_csv, "6XG-GPL")
    permission = normalize_permission(permission_csv)
    components = normalize_components(component_csv)
    live = live_rows(
        ROOT / "adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01",
        ROOT / "adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01",
    )
    control_rows = prior + ipc + ota + driver + permission + components + live
    tests = read_csv(tests_csv)

    source_root = ROOT / "firmware/extracted/PS7331-SOURCE-20250617"
    source_scope_rows = [
        {
            "evidence_id": "6X-SOURCE-001",
            "path_or_member": "platform/kernel/mediatek/4.4",
            "observed": "present in extracted source tree",
            "interpretation": "MT8183/MediaTek 4.4 kernel source scope is available for host-only audit",
            "confidence": "Confirmed",
            "evidence_file": "firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/4.4",
            "evidence_sha256": digest(ROOT / "firmware/extracted/PS7331-SOURCE-20250617/platform.tar"),
            "status": "SOURCE_SCOPE",
        },
        {
            "evidence_id": "6X-SOURCE-002",
            "path_or_member": "platform/device/amazon/kernel/driver",
            "observed": "present in extracted source tree",
            "interpretation": "Amazon kernel driver source scope is available; source capability is not caller reachability",
            "confidence": "Confirmed",
            "evidence_file": "firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver",
            "evidence_sha256": digest(ROOT / "firmware/extracted/PS7331-SOURCE-20250617/platform.tar"),
            "status": "SOURCE_SCOPE",
        },
        {
            "evidence_id": "6X-SOURCE-003",
            "path_or_member": "platform/system/core",
            "observed": "extracted tree contains libcutils scope; no selinux.cpp/init source found by bounded path search",
            "interpretation": "GPL/source package is not a complete system/core/init provenance source; /init remains binary/AOSP-anchor analysis",
            "confidence": "Strong evidence",
            "evidence_file": "firmware/extracted/PS7331-SOURCE-20250617/platform/system/core",
            "evidence_sha256": digest(ROOT / "firmware/extracted/PS7331-SOURCE-20250617/platform.tar"),
            "status": "BOUNDED_NEGATIVE",
        },
        {
            "evidence_id": "6X-SOURCE-004",
            "path_or_member": "vendor/mediatek in platform.tar",
            "observed": "no archive member path reported by the exact source audit",
            "interpretation": "This is an archive-path provenance negative only; it does not rule out separate vendor artifacts",
            "confidence": "Strong evidence",
            "evidence_file": "firmware/extracted/PS7331-SOURCE-20250617/platform.tar",
            "evidence_sha256": digest(ROOT / "firmware/extracted/PS7331-SOURCE-20250617/platform.tar"),
            "status": "BOUNDED_NEGATIVE",
        },
    ]

    write_csv(ROOT / "output/tables/phase6x-control-surface.csv", CONTROL_HEADER, control_rows)
    write_csv(ROOT / "output/tables/phase6x-test-reconciliation.csv", TEST_HEADER, tests)
    write_csv(
        ROOT / "output/tables/phase6x-source-scope.csv",
        ["evidence_id", "path_or_member", "observed", "interpretation", "confidence", "evidence_file", "evidence_sha256", "status"],
        source_scope_rows,
    )

    status_counts: dict[str, int] = {}
    for row in control_rows:
        status = row["status"] or "UNKNOWN"
        status_counts[status] = status_counts.get(status, 0) + 1
    confidence_counts: dict[str, int] = {}
    for row in control_rows:
        confidence = row["confidence"] or "UNKNOWN"
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1

    report = f"""# Phase 6X — broad privilege/control-surface continuation

Generation HEAD: `{__import__('subprocess').check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}`
Generated UTC: `{datetime.now(timezone.utc).isoformat()}`

## Scope and safety

This phase expands the research beyond Launcher-only behavior. It joins the
existing Phase 6WL corpus with new Framework IPC, 7.3.3.1 OTA, GPL/MediaTek
driver, and prior-test reconciliation evidence. The live observations use the
exact serial `G001LT0511550CFT` and only read-only ADB commands. No unknown
Binder transaction, driver node/ioctl, OTA/recovery execution, exploit payload,
Root attempt, Fire Launcher mutation, reboot, or partition write was executed.

## Current device observation

**已證實：** the device remains PS7331 (`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`), SELinux Enforcing, and User 0 resolves HOME to `com.amazon.firelauncher/.Launcher` at effective priority 50. User 0 candidates include Microsoft Launcher at 0 and FallbackHome at -1000.

**已證實：** an existing User 10 has a different scope: the saved package
dump reports Fire Launcher `enabled=2`, and the User 10 query returns
FallbackHome. Existing Phase 6NC/6FY evidence shows this is a child/profile
boundary involving Tahoe/Profile Owner, not a User 0 package-state writer.

## Cross-surface result

The ledger contains **{len(control_rows)}** control observations: 48 prior
  Phase 6WL rows, 3 new IPC rows, 4 OTA rows, 5 GPL/native rows, 4 permission
  rows, 8 exported/OOBE component rows, and 6 live read-only rows. The separate
  reconciliation matrix contains **{len(tests)}**
deduplicated route families.

### 已證實：privileged capability exists, but capability is not reachability

The source and disassembly contain sinks for keyguard/SystemUI state, OTA and
recovery writers, uinput/power-supply/RPMB operations, package/user/settings
state, and child/profile lifecycle. The required proof standard remains:

`caller → permission/identity gate → user scope → exact sink → observed effect`

No new row closes that chain from an ordinary app or shell to User 0 package,
formal HOME, root identity, or partition effect.

### 已證實：new IPC delta is permission-gated SystemUI surface

`IAmazonKeyguardService.dismissWithPendingIntent`, `setAccessibilityInfo`,
and `setForegroundColor` verify `Binder.getCallingUid()` through
`CONTROL_KEYGUARD` or `com.amazon.permission.AMAZON_CONTROL_KEYGUARD` before
forwarding verified caller identity/package to SystemUI. Transaction number,
publication, protection level, SELinux rule, and runtime caller remain
**待驗證**. These methods are not HOME/PMS/package-state sinks.

### 已證實：OTA evidence does not provide a safe or current-build bypass

The retained OTA is preserved 7.3.3.1 evidence and its provenance README
explicitly records the historical PS7330→PS7331 version boundary. The current
live fingerprint is PS7331.4463N, but the package was not executed in this
phase. Native
updater/recovery writers and staging paths remain statically capable, but
caller identity, AVB/rollback handoff, canonicalization/no-follow behavior,
and runtime effect are unresolved. No package was constructed or executed.

### 已證實：GPL/native driver surfaces do not close a privilege route

The 7.3.3.1 source confirms generic uinput fops, provider-gated power-supply
sysfs writes, and RPMB ioctl-only persistence operations. No exact shipped
caller/package/UID/domain was joined to a package/HOME/root sink. The archive
also has no `vendor/mediatek` path; that is only a provenance negative, not a
claim that every vendor artifact is absent.

### 已證實：permission declarations alone do not form a deputy

The residual permission scan found two `USE_SDK` declarations at `0x0` and one
`PLUGIN` declaration at `0x1`, plus one bounded declaration without a safely
decoded protection level. No requester, granted holder, exported consumer,
method-local caller gate, or sensitive sink was joined to these declarations.
They remain static candidates, not an elevation path.

### 已證實：OOBE/DCPMS surfaces remain lifecycle- or policy-scoped

`BootAfterSystemOTAReceiver` and its activation helper have protected OTA/OOBE
guards and setup-state sinks; DCPMS exported receivers update profile/CDE
policy; ProductPolicy registration is in-process. The bounded source contains
no new Fire Launcher HOME setter. Numeric user, producer permission/identity,
and external caller edges remain **待驗證**.

### Source package scope

The unpacked 7.3.3.1 source contains `platform/kernel/mediatek/4.4`,
`platform/device/amazon/kernel/driver`, and a bounded `platform/system/core`
scope centered on libcutils. The exact source audit did not find
`system/core/init/selinux.cpp` or a complete init policy-loader tree in this
package. Therefore the GPL package supports kernel/driver provenance and
differential analysis, while `/init` policy-loader conclusions still require
the saved binary/AOSP anchor. The absence of a `vendor/mediatek` member is
recorded only as a path-level negative.

### 已排除：replaying equivalent known routes is not productive

The 15-row reconciliation matrix marks ordinary preferred/set-home, Fire
package-state gates, KFT child scope, DPM, service visibility, OTA/driver/root,
and Accessibility foreground paths as completed, static-gap, or closed-no-
retest. Repeating denied component-disable, guessing Binder codes, opening
driver nodes, or executing OTA/recovery would not add the missing caller and
identity evidence and would violate the experiment boundary.

## Candidate assessment

| Candidate | Classification | Reason |
|---|---|---|
| User 10 Tahoe/profile HOME | **已證實但非 User 0 replacement** | Child/profile-scoped lifecycle; no cross-user User 0 effect. |
| Keyguard Binder methods | **待驗證 / not a launcher route** | Explicit permission gate; SystemUI presentation sink only. |
| uinput/power/RPMB source surfaces | **高可信推論：capability only** | No shipped low-privileged caller/domain/sink join. |
| OTA staging/recovery | **因風險拒絕測試** | Requires package/recovery/partition execution; current build/provenance gaps remain. |
| Accessibility/foreground redirect | **已排除為正式 HOME** | Historical bounded runs did not establish durable resolver replacement. |

## Remaining minimum host-only work

1. Resolve exact 7.3.3.1 artifact provenance and any missing `product_policy`
   or recovery mapping without executing it.
2. Join any remaining Amazon Binder publication to declared permission,
   SELinux/service-manager policy, caller identity, and user-scoped sink.
3. Finish exact native ELF load/caller joins for only those nodes with a
   confirmed policy allow; do not open the nodes.

If those joins remain open, the defensible conclusion is that no safe,
reproducible ADB-only privilege path has been demonstrated; the closest
observed alternate desktop behavior is child/profile-scoped Tahoe, not a
User-0 replacement or Root acquisition.

## Reproduction commands

The device captures were produced with the existing serial-bound read-only
scripts (use a new output directory for every capture):

```sh
tools/scripts/capture_phase6mv_runtime_readonly.sh \
  --serial G001LT0511550CFT \
  --output adb/phase6x/PHASE6X-DEVICE-READONLY-YYYYMMDD-NN

python3 tools/scripts/capture_phase6ee_current_baseline.py \
  --serial G001LT0511550CFT \
  --output adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-YYYYMMDD-NN

python3 tools/scripts/build_phase6x_surface.py --dry-run
python3 tools/scripts/build_phase6x_surface.py --force
```

The first two commands are read-only; the last two are host-only. The scripts
do not call private Binder transactions, open driver nodes, mutate settings or
package state, reboot, or execute OTA/recovery code.
"""
    (ROOT / "findings/phase-6x-report.md").write_text(report, encoding="utf-8")

    evidence = f"""# Phase 6X evidence index

All rows are reproduced in `output/tables/phase6x-control-surface.csv` and
`output/tables/phase6x-test-reconciliation.csv`. The input manifest records
the exact hashes used to generate them.

## Verdict rules

- **已證實 / Confirmed:** direct saved observation or exact static method.
- **高可信推論:** multiple evidence classes agree, but a caller/effect edge is
  still bounded.
- **待驗證 / UNKNOWN:** missing provenance, publication, identity, user scope,
  or runtime edge; not evidence of a bypass.
- **已排除 / Disproved:** the stated route was tested or statically bounded
  and did not produce the claimed effect.
- **因風險拒絕測試:** execution would require unknown transaction codes,
  driver/OTA/recovery writes, exploit payloads, or irrecoverable device state.

## Counts

- Control rows: `{len(control_rows)}`
- Reconciled route rows: `{len(tests)}`
- Status counts: `{status_counts}`
- Confidence counts: `{confidence_counts}`
"""
    (ROOT / "findings/phase-6x-evidence-index.md").write_text(evidence, encoding="utf-8")
    source_report = """# Phase 6X source package scope\n\nThe 7.3.3.1 source tree was inspected host-only. This report records package\nscope, not a claim of vulnerability or runtime reachability.\n\n| Evidence | Path/member | Observation | Interpretation | Confidence |\n|---|---|---|---|---|\n"""
    for row in source_scope_rows:
        source_report += (
            f"| {row['evidence_id']} | `{row['path_or_member']}` | "
            f"{row['observed']} | {row['interpretation']} | {row['confidence']} |\n"
        )
    source_report += (
        "\nThe source package is not an authorization proof. In particular, a "
        "driver file, Kconfig option, or missing path does not establish a "
        "shipped caller, SELinux allow, UID, or sensitive effect.\n"
    )
    (ROOT / "findings/phase-6x-source-scope.md").write_text(source_report, encoding="utf-8")

    graph = """flowchart TD
  A[ordinary app or shell] --> B{permission / identity gate}
  B -->|not proven accepted| X[no User-0 package/HOME/root effect]
  C[Amazon IPC] --> D[Keyguard/SystemUI guarded sink]
  D --> X
  E[OTA lifecycle] --> F[metadata / AVB / recovery gates]
  F --> G[partition-capable writer, runtime caller unknown]
  G --> X
  H[GPL/native source] --> I[uinput / power / RPMB capability]
  I --> J[shipped caller/domain unknown]
  J --> X
  K[KFT/Tahoe child lifecycle] --> L[User 10 scoped package/HOME state]
  L -. no observed cross-user edge .-> X
  M[User 0 resolver] --> N[Fire Launcher priority 50]
"""
    (ROOT / "output/call-graphs/phase6x-control-surfaces.mmd").write_text(graph, encoding="utf-8")
    (ROOT / "output/call-graphs/phase6x-control-surfaces.md").write_text(
        """# Phase 6X control-surface graph\n\nThe Mermaid source is preserved below. Dashed edges denote an unobserved or\nuser-scoped boundary, not a proven bypass.\n\n```mermaid\n""" + graph + "```\n", encoding="utf-8")

    manifest_lines = []
    for path in sorted(set(inputs)):
        manifest_lines.append(f"{digest(path)}  {path.relative_to(ROOT)}")
    (ROOT / "output/tables/phase6x-input-manifest.sha256").write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(output_files)} outputs; control_rows={len(control_rows)} test_rows={len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
