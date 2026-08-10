#!/usr/bin/env python3
"""Build the Phase 16 cross-surface capability-to-sink closure.

This is a host-only report generator.  It reads the four fixed-schema worker
inventories and emits a normalized matrix, evidence index, and call graph.
It never connects to ADB and never mutates device or firmware state.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WORKERS = {
    "kernel": ROOT / "work/luna_worker_next_kernel_surface_20260810.csv",
    "ipc": ROOT / "work/luna_worker_next_ipc_sink_audit_20260810.csv",
    "ota": ROOT / "work/luna_worker_next_ota_postinstall_20260810.csv",
    "reconciliation": ROOT / "work/luna_worker_next_test_reconciliation_20260810.csv",
}
WORKER_DOCS = {
    "kernel": ROOT / "work/luna_worker_next_kernel_surface_20260810.md",
    "ipc": ROOT / "work/luna_worker_next_ipc_sink_audit_20260810.md",
    "ota": ROOT / "work/luna_worker_next_ota_postinstall_20260810.md",
    "reconciliation": ROOT / "work/luna_worker_next_test_reconciliation_20260810.md",
}

TABLE = ROOT / "output/tables/phase16-control-surface.csv"
REPORT = ROOT / "findings/phase-16-report.md"
INDEX = ROOT / "findings/phase-16-evidence-index.md"
GRAPH = ROOT / "output/call-graphs/phase16-capability-to-sink.mmd"
GRAPH_TEXT = ROOT / "output/call-graphs/phase16-capability-to-sink.md"
MANIFEST = ROOT / "firmware/manifests/PHASE16-HOST-ANALYSIS-20260810/sha256sums.txt"

FIELDS = [
    "id",
    "branch",
    "artifact_or_service",
    "entrypoint_or_symbol",
    "caller_or_entry",
    "permission_or_gate",
    "binder_identity_or_domain",
    "user_scope",
    "target_scope",
    "sink_or_effect",
    "observed_runtime",
    "status",
    "confidence",
    "evidence",
    "missing_edge",
    "next_safe_step",
]

ALLOWED = {"Confirmed", "Strong evidence", "Probable", "Hypothesis", "Disproved", "Unknown"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty worker CSV: {path}")
    return rows


def text(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = (row.get(name) or "").strip()
        if value:
            return value
    return "UNKNOWN"


def confidence(value: str) -> str:
    aliases = {
        "high": "Strong evidence",
        "HIGH": "Strong evidence",
        "高": "Strong evidence",
        "medium": "Probable",
        "MEDIUM": "Probable",
        "中": "Probable",
        "low": "Hypothesis",
        "LOW": "Hypothesis",
        "低": "Hypothesis",
        "unknown": "Unknown",
        "UNKNOWN": "Unknown",
        "未知": "Unknown",
    }
    result = aliases.get(value.strip(), value.strip())
    if result not in ALLOWED:
        raise ValueError(f"invalid confidence {value!r}")
    return result


def normalize(branch: str, row: dict[str, str]) -> dict[str, str]:
    if branch == "kernel":
        return {
            "id": row["id"],
            "branch": "kernel/driver static inventory",
            "artifact_or_service": text(row, "path_or_symbol"),
            "entrypoint_or_symbol": text(row, "surface"),
            "caller_or_entry": text(row, "caller_or_entry"),
            "permission_or_gate": text(row, "permission_or_gate"),
            "binder_identity_or_domain": "UNKNOWN",
            "user_scope": "UNKNOWN",
            "target_scope": text(row, "surface"),
            "sink_or_effect": text(row, "sink_or_effect"),
            "observed_runtime": text(row, "existing_runtime_test"),
            "status": "static capability / caller-to-sink closure not established",
            "confidence": confidence(row["confidence"]),
            "evidence": text(row, "evidence"),
            "missing_edge": text(row, "missing_edge"),
            "next_safe_step": text(row, "next_safe_step"),
        }
    if branch == "ipc":
        return {
            "id": row["id"],
            "branch": "Amazon IPC/service static audit",
            "artifact_or_service": text(row, "service_or_class"),
            "entrypoint_or_symbol": text(row, "entrypoint"),
            "caller_or_entry": text(row, "caller_or_client"),
            "permission_or_gate": text(row, "permission_or_gate"),
            "binder_identity_or_domain": text(row, "binder_identity"),
            "user_scope": text(row, "user_scope"),
            "target_scope": "UNKNOWN",
            "sink_or_effect": text(row, "sink_or_effect"),
            "observed_runtime": text(row, "observed_runtime"),
            "status": "static sink / reachability bounded by evidence",
            "confidence": confidence(row["confidence"]),
            "evidence": text(row, "evidence"),
            "missing_edge": text(row, "missing_edge"),
            "next_safe_step": text(row, "next_safe_step"),
        }
    if branch == "ota":
        return {
            "id": row["id"],
            "branch": "OTA/post-install static audit",
            "artifact_or_service": text(row, "artifact_or_component"),
            "entrypoint_or_symbol": text(row, "operation_or_sink"),
            "caller_or_entry": text(row, "trigger_or_caller"),
            "permission_or_gate": text(row, "verification_or_gate"),
            "binder_identity_or_domain": "UNKNOWN",
            "user_scope": "UNKNOWN",
            "target_scope": text(row, "target_scope"),
            "sink_or_effect": text(row, "operation_or_sink"),
            "observed_runtime": text(row, "observed_runtime"),
            "status": "recovery/updater capability; ordinary caller not closed",
            "confidence": confidence(row["confidence"]),
            "evidence": text(row, "evidence"),
            "missing_edge": text(row, "missing_edge"),
            "next_safe_step": text(row, "next_safe_step"),
        }
    if branch == "reconciliation":
        return {
            "id": row["id"],
            "branch": "Phase 1-15 test reconciliation",
            "artifact_or_service": text(row, "phase_or_test"),
            "entrypoint_or_symbol": text(row, "goal"),
            "caller_or_entry": "Historical test / artifact",
            "permission_or_gate": text(row, "precondition"),
            "binder_identity_or_domain": "UNKNOWN",
            "user_scope": "UNKNOWN",
            "target_scope": "UNKNOWN",
            "sink_or_effect": text(row, "result"),
            "observed_runtime": text(row, "status"),
            "status": text(row, "status"),
            "confidence": confidence(row["confidence"]),
            "evidence": text(row, "evidence"),
            "missing_edge": text(row, "repeat_policy"),
            "next_safe_step": text(row, "next_safe_step"),
        }
    raise ValueError(branch)


def all_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for branch, path in WORKERS.items():
        rows.extend(normalize(branch, row) for row in read_csv(path))
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate normalized evidence id")
    return rows


def resolve_evidence(raw: str) -> Path | None:
    # Worker evidence fields frequently contain several paths and optional
    # line ranges.  Hash the first path that exists; retain the full raw field
    # in the matrix and index rather than rewriting source citations.
    for item in raw.split(";"):
        item = item.strip()
        item = re.sub(r":\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$", "", item)
        candidate = ROOT / item
        if candidate.is_file():
            return candidate
    return None


def write_table(rows: list[dict[str, str]]) -> None:
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    with TABLE.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_index(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Phase 16 evidence index — cross-surface capability-to-sink closure",
        "",
        "This index is generated host-side from the four fixed-schema worker CSVs.",
        "Phase 16 performed no device mutation, Binder transaction, driver ioctl,",
        "OTA/recovery execution, root attempt, or partition operation.",
        "",
        "| Evidence ID | Branch | Source file | SHA-256 | Observation | Missing edge / interpretation | Confidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for branch, path in WORKERS.items():
        digest = sha256(path)
        for row in read_csv(path):
            normalized = normalize(branch, row)
            lines.append(
                "| %s | %s | %s | `%s` | %s | %s | %s |"
                % (
                    normalized["id"],
                    normalized["branch"],
                    path.relative_to(ROOT),
                    digest,
                    normalized["sink_or_effect"],
                    normalized["missing_edge"],
                    normalized["confidence"],
                )
            )
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_graph() -> None:
    graph = """flowchart LR
    A["Kernel source / DT / driver capability"] --> A1["caller + UID/domain + SELinux + node gate"]
    A1 -->|"not closed in saved corpus"| AX["No low-privilege kernel sink claim"]
    B["Ordinary APK / shell service reachability"] --> B1["Amazon Binder method gate"]
    B1 --> B2["preWarmApplicationForUser"]
    B2 --> B3["startProcessLocked / resource effect"]
    B3 --> BX["Confirmed process deputy; no HOME/package/root sink"]
    C["KFT child/profile lifecycle"] --> C1["UserInfo.id + lifecycle scope"]
    C1 --> C2["setApplication/ComponentEnabledSetting"]
    C2 --> C3["Tahoe on; Fire/Launcher3 off for child/profile"]
    C3 --> CX["No closed User 0 ordinary relay"]
    D["User 0 package/HOME mutation"] --> D1["PMS protected-package / caller gate"]
    D1 --> DX["Existing shell/component tests rejected; state unchanged"]
    E["Signed OTA / recovery updater"] --> E1["verification + recovery/system context"]
    E1 --> E2["block image / boot-chain partition capability"]
    E2 --> EX["High privilege capability; ordinary caller not closed"]
    F["Phase 1-15 historical tests"] --> F1["reconciled evidence / no duplicate reruns"]
    F1 --> FX["Next safe candidate: passive natural event only"]
"""
    GRAPH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH.write_text(graph, encoding="utf-8")
    markdown = """# Phase 16 capability-to-sink graph (text form)

```text
Kernel/driver capability
  -> caller + UID/domain + SELinux/node gate [missing in saved corpus]
  -> no low-privilege kernel sink claim

Ordinary APK/service reachability
  -> Amazon Binder method gate
  -> preWarmApplicationForUser
  -> startProcessLocked/resource effect
  -> confirmed process/resource deputy; no HOME/package/root sink

KFT child/profile lifecycle
  -> supplied UserInfo.id and child/profile scope
  -> enabled-state setters
  -> Tahoe enabled; Fire/Launcher3 disabled for child/profile
  -> no closed ordinary User-0 relay

User-0 package/HOME mutation
  -> PMS protected-package/caller gate
  -> existing shell/component tests rejected; state unchanged

Signed OTA/recovery updater
  -> verification and recovery/system context
  -> block-image/boot-chain partition capability
  -> ordinary caller not closed; no execution performed

Historical Phase 1-15 tests
  -> evidence reconciliation and no-repeat policy
  -> next safe candidate is passive natural observation only
```
"""
    GRAPH_TEXT.write_text(markdown, encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["branch"]] = counts.get(row["branch"], 0) + 1
    report = f"""# Phase 16 — broad capability-to-sink reconciliation

Date: 2026-08-10
Device context: Amazon Fire HD 10 (KFTRWI / trona), Fire OS 7.3.3.1 / PS7331, Android 9/API 28.
Scope: host-only integration of four disjoint static/test-reconciliation inventories plus previously archived runtime evidence.

## Executive result

**已證實：**本階段沒有新增裝置操作，也沒有找到一條由普通 app 或 shell 到
User 0 Fire Launcher package/component state、正式 HOME、OTA partition、UID 0
的完整 caller→gate→sink 鏈。worker 證據總共整理 {len(rows)} 筆：
kernel/driver {counts.get('kernel/driver static inventory', 0)}、Amazon IPC
{counts.get('Amazon IPC/service static audit', 0)}、OTA/post-install
{counts.get('OTA/post-install static audit', 0)}、Phase 1–15 reconciliation
{counts.get('Phase 1-15 test reconciliation', 0)}。

**已證實：**既有 Phase 6ER/15 runtime 已觀察到 ordinary no-permission APK
透過已保存的 prewarm 路徑造成暫時 process/resource effect；這是 process
confused-deputy finding，不是 root、HOME replacement 或 package-state writer。

**已證實：**KFT 的 package-state writer 可對 supplied `UserInfo.id` 的
child/profile lifecycle 啟用 Tahoe、停用 Fire Launcher/Launcher3；目前保存
證據沒有把普通 caller 或 shell 閉合到 User 0 的該 writer。

**高可信推論：**若目標是「取得任意足以停用官方 Launcher 的權限」，目前最接近
的研究面仍是受保護的 system-service caller/identity boundary，而不是再做
priority、`set-home-activity`、猜測 Binder parcel、driver ioctl 或 OTA replay。
本輪沒有證據足以把任何一個候選升級成可利用權限提升。

## 1. Capability versus accepted caller

Evidence discipline: the normalized table preserves each worker row's raw
evidence citation. The Phase 16 manifest hashes the worker files and every
generated output. Legacy shorthand citations that are not standalone paths are
not silently resolved or promoted; they remain part of the row's missing-edge
review.

| Surface | Static capability / sink | Accepted low-privilege caller | Current verdict |
|---|---|---|---|
| Kernel / MTK drivers | CMDQ, ION, M4U, uinput, AUXADC, power/USB/debug surfaces | Exact native caller, node mode, merged SELinux allow and shipped object are not all joined | **待驗證**；不得由 symbol/config 推論可利用 |
| Amazon private IPC | User/KFT, profile, input, PMS-facing metadata, OOBE/OTA contracts | Service visibility and method-specific gates vary; no closed ordinary User-0 package/HOME caller | **已證實能力存在；低權限 sink 未閉合** |
| Prewarm | `preWarmApplicationForUser` → `startProcessLocked` | Prior bounded ordinary-app observation exists | **已證實 process/resource effect；不等於 root/HOME** |
| KFT child/profile | enabled-state calls using supplied `UserInfo.id` | Child/profile lifecycle scope is shown; ordinary User-0 relay is missing | **已證實 child-scoped writer；User 0 路徑未證實** |
| OTA/recovery | signed block/full OTA, updater write handlers, boot-chain targets | Recovery/update verification and system context required; ordinary caller not closed | **高權限能力；非低權限入口** |
| User-0 Fire package/HOME | PMS protected gate; ordinary disable/component tests | Existing shell tests were rejected before state mutation | **已排除既有 shell route** |

## 2. Amazon IPC and package-state sinks

The strongest static package-state sink is:

```text
AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)
  -> enableKftLauncherComponent(UserInfo)
  -> enabled-state setters for supplied UserInfo.id
  -> Tahoe enabled; Fire Launcher and Launcher3 disabled
```

Evidence rows `LUNA-B-002`–`LUNA-B-005` and the prior KFT closure support the
sink and its child/profile scope. The precise external caller authorization for
`enableKftLauncher` remains an **待驗證** edge; the method's existence is not
permission to invoke it, and no transaction was sent in Phase 16.

The bounded Amazon profile/input/OOBE/OTA review found no proven direct
`setHomeActivity`, `addPreferredActivity`, or `replacePreferredActivity` writer.
`BootAfterSystemOTAReceiver` remains a protected lifecycle sink, not a broadcast
that may be replayed by shell. Treat these as bounded negatives, not a claim that
every Amazon class has been exhaustively decompiled.

## 3. Kernel and driver surface

The PS7331 source and saved boot/image artifacts contain capability markers for
CMDQ/GCE, ION, M4U, uinput, AUXADC, perf/power, USB PHY/TCPC and Amazon
diagnostic surfaces. The worker correctly separates:

1. registration/Kconfig/DT capability;
2. final shipped object/DTB and node ownership;
3. caller UID/domain, merged SELinux allow and ioctl/proc/sysfs dataflow; and
4. observable security effect.

The saved corpus does not close all four layers for a low-privilege caller.
`CONFIG_AMZN_DRV_TEST` is not enabled in the cited trona configuration, so its
factory/engineering dispatcher is not a shipped runtime claim. No open/ioctl,
memory read/write, exploit, or root test was performed in this phase.

## 4. OTA and post-install surface

The PS7331 package is a signed full/block OTA. The script/native updater artifacts
show fixed high-privilege capabilities including system/vendor and boot-chain
targets, but the relevant caller is recovery/updater context behind package,
version, signature, AVB/rollback and boot-control gates. The missing edges listed
in `C-001`–`C-018` prevent a low-privilege conclusion.

`BootAfterSystemOTAReceiver` and OOBE helpers can participate in protected
post-upgrade lifecycle and settings/setup changes. No broadcast replay, updater
execution, sideload, recovery, reboot, partition write or malformed OTA test was
performed. Capability is not reachability.

## 5. Historical runtime reconciliation and no-repeat policy

The reconciliation confirms that priority APK matrices, ordinary
`set-home-activity`, Fire package/component disable, child/KFT variants, DPM,
Accessibility foreground redirect, guessed private Binder parcels, root/GhostLock
probes, and OTA/driver mutation paths already have negative, bounded, or
risk-rejected results. They are not repeated merely because a static sink exists.

The only new runtime candidate identified by the reconciliation is a **passive
observation of a naturally occurring Alexa prewarm event**, with no APK, no
Binder transaction, no guessed parcel, no child/user mutation and no state write.
It is a validation candidate, not an exploit path. If no natural event occurs,
the correct result is `未觀察到`, not synthetic injection.

## 6. Verdict classification

- **已證實:** process/resource prewarm deputy; KFT child/profile package-state
  writer; Amazon/OTA/kernel capabilities exist at their respective static layers;
  existing User-0 Fire disable/component routes are protected/rejected.
- **高可信推論:** a new privilege path, if one exists, must close a protected
  caller/identity/user-scope edge; broad capability inventory alone is insufficient.
- **待驗證:** exact external authorization and accepted `UserInfo` validation
  for KFT; final shipped driver node/policy/caller joins; OTA native indirect
  handoff; a naturally occurring prewarm observation.
- **已排除（bounded scope）:** prewarm as HOME/package/root writer; existing
  ordinary shell HOME/disable route; child-scoped KFT evidence as a User-0 relay;
  treating OTA/driver symbols as an ordinary-app exploit.
- **因風險拒絕測試:** guessed private Binder transactions, forged user records,
  Fire Launcher mutation, driver open/ioctl, Root/GhostLock attempts, OTA/recovery
  execution, sideload/flash, partition writes, malformed OTA and broadcast replay.

## 7. Safe next action

No new state-changing device action is justified by the current matrix. The next
minimal step, if a new live-session observation is explicitly desired, is a
read-only passive capture around a naturally occurring Alexa prewarm event while
checking HOME, Fire package/component state, current user, settings and SELinux
invariants. Do not manufacture the event through private Binder calls. Otherwise
continue host-only joins of exact shipped driver objects/DTB/policy and the KFT
caller authorization path.

## 8. Reproduction and generated outputs

```sh
python3 tools/scripts/build_phase16_control_surface.py --dry-run
python3 tools/scripts/build_phase16_control_surface.py --force
python3 -m py_compile tools/scripts/build_phase16_control_surface.py
```

The normalized matrix, evidence index, Mermaid/text graph and input/output hashes
are generated without touching the device. Worker source files are retained under
`work/` and are hashed by the Phase 16 manifest.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")


def write_manifest() -> None:
    paths = [
        *WORKERS.values(),
        *WORKER_DOCS.values(),
        TABLE,
        REPORT,
        INDEX,
        GRAPH,
        GRAPH_TEXT,
    ]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8") as stream:
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(path)
            stream.write(f"{sha256(path)}  {path.relative_to(ROOT)}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="validate inputs without writing outputs")
    parser.add_argument("--force", action="store_true", help="allow regeneration of Phase 16 outputs")
    args = parser.parse_args()
    missing = [str(path) for path in [*WORKERS.values(), *WORKER_DOCS.values()] if not path.is_file()]
    if missing:
        parser.error("missing input(s): " + ", ".join(missing))
    rows = all_rows()
    if args.dry_run:
        print(f"validated {len(rows)} normalized rows from {len(WORKERS)} worker CSVs")
        return 0
    if not args.force and any(path.exists() for path in [TABLE, REPORT, INDEX, GRAPH, GRAPH_TEXT, MANIFEST]):
        parser.error("Phase 16 output exists; pass --force to regenerate")
    write_table(rows)
    write_index(rows)
    write_graph()
    write_report(rows)
    write_manifest()
    print(f"wrote {len(rows)} normalized rows and Phase 16 report outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
