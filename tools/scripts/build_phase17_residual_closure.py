#!/usr/bin/env python3
"""Build the Phase 17 residual privilege-surface closure.

Host-only generator. It reads delegated worker inventories and preserved
runtime artifacts, then writes a normalized caller/gate/sink matrix, reports,
graphs, and a SHA-256 manifest. It never connects to ADB or mutates a device.

The IPC worker CSV was written concurrently by two worker completions. The
raw file is preserved; this generator records its duplicate-ID anomaly and
keeps only the first row for each ID in the derived table.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WORKERS = {
    "kft": ROOT / "work/luna_worker_phase17_kft_gate_20260810.csv",
    "ipc": ROOT / "work/luna_worker_phase17_ipc_residual_20260810.csv",
    "driver": ROOT / "work/luna_worker_phase17_driver_policy_20260810.csv",
    "ota": ROOT / "work/luna_worker_phase17_ota_reachability_20260810.csv",
}
WORKER_DOCS = {
    "kft": ROOT / "work/luna_worker_phase17_kft_gate_20260810.md",
    "ipc": ROOT / "work/luna_worker_phase17_ipc_residual_20260810.md",
    "driver": ROOT / "work/luna_worker_phase17_driver_policy_20260810.md",
    "ota": ROOT / "work/luna_worker_phase17_ota_reachability_20260810.md",
}
KEY_INPUTS = [
    ROOT / "adb/phase6fk/PHASE6FK-USER0-TX3-20260807-01/command-output.txt",
    ROOT / "adb/phase6fj/PHASE6FJ-USER10-TX3-20260807-01/command-output.txt",
    ROOT / "adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json",
    ROOT / "findings/phase-6mx-amazon-pm-caller-provenance.md",
    ROOT / "findings/phase-6mu-amazon-application-flags-closure.md",
    ROOT / "findings/phase-6cz-kft-child-gating.md",
    ROOT / "decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java",
    ROOT / "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log",
]

TABLE = ROOT / "output/tables/phase17-residual-privilege-surface.csv"
INDEX = ROOT / "findings/phase-17-evidence-index.md"
REPORT = ROOT / "findings/phase-17-report.md"
GRAPH = ROOT / "output/call-graphs/phase17-kft-pms-identity-flow.mmd"
GRAPH_TEXT = ROOT / "output/call-graphs/phase17-kft-pms-identity-flow.md"
MANIFEST = ROOT / "firmware/manifests/PHASE17-HOST-ANALYSIS-20260810/sha256sums.txt"

FIELDS = [
    "id", "branch", "artifact_or_service", "entrypoint_or_symbol",
    "caller_or_trigger", "permission_or_gate", "binder_identity_or_domain",
    "user_scope", "sink_or_effect", "observed_runtime", "classification",
    "evidence", "missing_edge", "next_safe_step",
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


def val(row: dict[str, str], *names: str) -> str:
    for name in names:
        result = (row.get(name) or "").strip()
        if result:
            return result
    return "UNKNOWN"


def classify(raw: str) -> str:
    aliases = {
        "high": "Strong evidence", "HIGH": "Strong evidence",
        "medium": "Probable", "MEDIUM": "Probable",
        "low": "Hypothesis", "LOW": "Hypothesis",
        "unknown": "Unknown", "UNKNOWN": "Unknown",
    }
    result = aliases.get(raw.strip(), raw.strip())
    if result not in ALLOWED:
        lowered = raw.lower()
        if re.search(r"\blow\b", lowered):
            result = "Hypothesis"
        elif re.search(r"\bmedium\b", lowered) or "reachability not established" in lowered:
            result = "Probable"
        elif re.search(r"\bhigh\b", lowered):
            result = "Strong evidence"
    if result not in ALLOWED:
        raise ValueError(f"invalid confidence/classification: {raw!r}")
    return result


def normalize(branch: str, row: dict[str, str]) -> dict[str, str]:
    if branch == "kft":
        mapping = (
            "Amazon KFT / user-manager", "class_or_service", "method_or_entrypoint",
            "caller_or_client", "permission_or_gate", "binder_identity",
            "user_scope", "sink_or_effect", "observed_runtime",
        )
    elif branch == "ipc":
        mapping = (
            "Amazon Framework / IPC", "service_or_class", "entrypoint",
            "caller_or_client", "permission_or_gate", "binder_identity",
            "user_scope", "sink_or_effect", "observed_runtime",
        )
    elif branch == "driver":
        mapping = (
            "MTK / Amazon driver surface", "path_or_symbol", "device_node_or_surface",
            "caller_or_entry", "permission_or_gate", "owner_mode_or_context",
            "user_scope", "sink_or_effect", "observed_runtime",
        )
    elif branch == "ota":
        mapping = (
            "OTA / OOBE / recovery", "artifact_or_component",
            "entrypoint_or_operation", "caller_or_trigger",
            "permission_or_verification", "binder_identity", "target_scope",
            "sink_or_effect", "observed_runtime",
        )
    else:
        raise ValueError(branch)
    prefixes = {"kft": "KFT", "ipc": "IPC", "driver": "DRV", "ota": "OTA"}
    branch_name, artifact, entry, caller, gate, identity, scope, sink, runtime = mapping
    return {
        "id": f"P17-{prefixes[branch]}-{row['id']}",
        "branch": branch_name,
        "artifact_or_service": val(row, artifact, "path_or_symbol", "service_or_class"),
        "entrypoint_or_symbol": val(row, entry, "operation_or_sink"),
        "caller_or_trigger": val(row, caller, "trigger_or_caller"),
        "permission_or_gate": val(row, gate, "verification_or_gate"),
        "binder_identity_or_domain": val(row, identity, "binder_identity_or_domain"),
        "user_scope": val(row, scope, "user_scope"),
        "sink_or_effect": val(row, sink, "operation_or_sink"),
        "observed_runtime": val(row, runtime),
        "classification": classify(row["confidence"]),
        "evidence": val(row, "evidence"),
        "missing_edge": val(row, "missing_edge"),
        "next_safe_step": val(row, "next_safe_step"),
    }


def supplemental_rows() -> list[dict[str, str]]:
    return [
        {
            "id": "P17-RUN-001",
            "branch": "Existing runtime boundary",
            "artifact_or_service": "amazonusermanagerservice / AmazonUserManagerService.BinderService",
            "entrypoint_or_symbol": "IAmazonUserManager tx3 -> enableKftLauncher(UserInfo)",
            "caller_or_trigger": "ordinary APK UID 10213; structurally valid UserInfo id=0",
            "permission_or_gate": "PMS setComponentEnabledSetting -> protected/caller gate",
            "binder_identity_or_domain": "PMS log preserves pid=27832, uid=10213",
            "user_scope": "User 0",
            "sink_or_effect": "attempted Tahoe enable and Fire/Launcher3 disable; rejected before mutation",
            "observed_runtime": "SecurityException at PMS.setEnabledSetting; result=false; Fire HOME stayed priority 50",
            "classification": "Confirmed",
            "evidence": "adb/phase6fk/PHASE6FK-USER0-TX3-20260807-01/command-output.txt",
            "missing_edge": "trusted external Binder caller is not established; no privilege transition",
            "next_safe_step": "Do not rerun tx3; compare caller references and PMS gate offline",
        },
        {
            "id": "P17-RUN-002",
            "branch": "Existing runtime boundary",
            "artifact_or_service": "amazonusermanagerservice / AmazonUserManagerService.BinderService",
            "entrypoint_or_symbol": "IAmazonUserManager tx3 -> enableKftLauncher(UserInfo)",
            "caller_or_trigger": "ordinary APK UID 10212; supplied UserInfo id=10",
            "permission_or_gate": "PMS cross-user enforcement: INTERACT_ACROSS_USERS",
            "binder_identity_or_domain": "PMS log preserves ordinary caller uid=10212",
            "user_scope": "User 10; User 0 foreground",
            "sink_or_effect": "attempted child launcher state change; rejected before mutation",
            "observed_runtime": "SecurityException: missing INTERACT_ACROSS_USERS; state unchanged",
            "classification": "Confirmed",
            "evidence": "adb/phase6fj/PHASE6FJ-USER10-TX3-20260807-01/command-output.txt",
            "missing_edge": "accepted cross-user trusted caller is not established",
            "next_safe_step": "Do not rerun; retain as user-scope boundary",
        },
        {
            "id": "P17-RUN-003",
            "branch": "Existing runtime boundary",
            "artifact_or_service": "ordinary app -> Amazon private service handle",
            "entrypoint_or_symbol": "preWarmApplicationForUser (tx1, prior bounded test)",
            "caller_or_trigger": "no-permission APK; Phase 6ER saved observation",
            "permission_or_gate": "service handle was available in that bounded app context; no package/HOME writer observed",
            "binder_identity_or_domain": "no UID change; ordinary app remained ordinary",
            "user_scope": "User 0",
            "sink_or_effect": "temporary process/resource effect only",
            "observed_runtime": "target process appeared; Fire HOME and package state unchanged; APK removed",
            "classification": "Confirmed",
            "evidence": "adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json",
            "missing_edge": "no path to package state, HOME, UID 0, or persistent privilege",
            "next_safe_step": "Only passively observe a natural trusted prewarm; do not craft tx1",
        },
        {
            "id": "P17-PM-001",
            "branch": "Amazon Framework / identity preservation",
            "artifact_or_service": "AmazonPackageManagerImpl",
            "entrypoint_or_symbol": "setApplicationEnabledSetting / setComponentEnabledSetting",
            "caller_or_trigger": "Amazon framework facade caller",
            "permission_or_gate": "delegates to standard PackageManager or IPackageManager",
            "binder_identity_or_domain": "no clearCallingIdentity in setter paths; component path calls IPackageManager directly",
            "user_scope": "supplied userId",
            "sink_or_effect": "standard PMS enabled-state setter; not a system-identity relay",
            "observed_runtime": "Phase6FK ordinary uid reached PMS and was rejected before mutation",
            "classification": "Strong evidence",
            "evidence": "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log; AmazonPackageManagerImpl codeOff=76230-76274 and 8fe-92e",
            "missing_edge": "complete facade instantiator/caller inventory",
            "next_safe_step": "Host-only callsite/signature-holder join; no private Binder call",
        },
        {
            "id": "P17-PM-002",
            "branch": "AOSP-shaped PMS gate",
            "artifact_or_service": "PackageManagerService",
            "entrypoint_or_symbol": "replacePreferredActivity; setApplicationEnabledSetting; setComponentEnabledSetting",
            "caller_or_trigger": "Binder caller / PackageManagerShellCommand",
            "permission_or_gate": "SET_PREFERRED_APPLICATIONS, cross-user enforcement, setEnabledSetting protected checks",
            "binder_identity_or_domain": "Binder.getCallingUid used in PMS; shell passes shell package label",
            "user_scope": "requested userId",
            "sink_or_effect": "preferred record or package/component mutation only after PMS checks",
            "observed_runtime": "preferred record accepted but Fire still won HOME; Fire disable rejected",
            "classification": "Confirmed",
            "evidence": "decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java:14910-14930,15654-15675",
            "missing_edge": "no unprivileged caller bypassing these checks",
            "next_safe_step": "No duplicate resolver or disable tests; compare branches offline",
        },
    ]


def collect_rows() -> tuple[list[dict[str, str]], dict[str, dict[str, object]]]:
    rows: list[dict[str, str]] = []
    stats: dict[str, dict[str, object]] = {}
    for branch, path in WORKERS.items():
        source_rows = read_csv(path)
        identifiers = [row.get("id", "") for row in source_rows]
        duplicates = sorted(identifier for identifier, count in Counter(identifiers).items() if count > 1)
        stats[branch] = {
            "rows": len(source_rows),
            "unique_ids": len(set(identifiers)),
            "duplicates": duplicates,
            "malformed": [],
            "sha256": sha256(path),
        }
        seen: set[str] = set()
        for row in source_rows:
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            try:
                rows.append(normalize(branch, row))
            except ValueError:
                stats[branch]["malformed"].append(row.get("id", "UNKNOWN"))
    rows.extend(supplemental_rows())
    identifiers = [row["id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate IDs remain after de-duplication")
    return rows, stats


def resolve_evidence(raw: str) -> Path | None:
    for item in raw.split(";"):
        candidate_text = item.strip().strip(chr(96))
        candidate_text = re.sub(r":\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$", "", candidate_text)
        if candidate_text.startswith("..."):
            continue
        candidate = ROOT / candidate_text
        if candidate.is_file():
            return candidate
    return None


def write_table(rows: list[dict[str, str]]) -> None:
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    with TABLE.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_index(rows: list[dict[str, str]], stats: dict[str, dict[str, object]]) -> None:
    lines = [
        "# Phase 17 evidence index — residual privilege-surface closure",
        "",
        "Generated host-side. No device command, Binder transaction, driver access,",
        "exploit/root action, OTA/recovery execution, reboot, or partition mutation",
        "was performed while building this phase.",
        "",
        "## Input integrity",
        "",
        "Worker files are preserved as received. The IPC worker path was written",
        "by concurrent completions; its CSV and Markdown summaries are not treated",
        "as one atomic artifact. Malformed rows are listed and excluded from the",
        "derived table. These are QA findings, not additional evidence.",
        "",
        "| Branch | Raw rows | Unique IDs | Duplicate IDs | Malformed IDs | SHA-256 |",
        "|---|---:|---:|---|---|---|",
    ]
    for branch, item in stats.items():
        duplicates = ", ".join(item["duplicates"]) if item["duplicates"] else "none"
        malformed = ", ".join(item["malformed"]) if item["malformed"] else "none"
        lines.append(f"| {branch} | {item['rows']} | {item['unique_ids']} | {duplicates} | {malformed} | {item['sha256']} |")
    lines += [
        "",
        "## Evidence rows",
        "",
        "| ID | Branch | Evidence source | Source SHA-256 | Observation / sink | Missing edge | Classification |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        source = resolve_evidence(row["evidence"])
        source_name = str(source.relative_to(ROOT)) if source else row["evidence"]
        source_hash = sha256(source) if source else "UNRESOLVED"
        lines.append(
            f"| {row['id']} | {row['branch']} | {source_name} | {source_hash} | "
            f"{row['sink_or_effect']} | {row['missing_edge']} | {row['classification']} |"
        )
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_graph() -> None:
    graph = """flowchart LR
    A["Ordinary APK / shell"] --> B["ServiceManager / Binder handle"]
    B -->|"shell find denied; handles are service-specific"| C["Amazon private service"]
    C --> D["IAmazonUserManager tx3"]
    D --> E["enableKftLauncher(UserInfo)"]
    E --> F["tryEnableKftLauncherComponent"]
    F --> G["AmazonPackageManagerImpl / IPackageManager"]
    G --> H["PMS.setComponentEnabledSetting"]
    H --> I["caller + cross-user + protected-package checks"]
    I -->|"ordinary uid rejected before mutation"| J["No Fire state change"]
    E --> K["clearCallingIdentity"]
    K --> L["DPM/profile-owner work after package-state attempt"]
    M["Trusted child lifecycle"] --> E
    M --> N["child flag + supplied user id"]
    N --> O["Tahoe on; Fire/Launcher3 off for child scope"]
    P["Driver / OTA capability"] --> Q["object + DTB + policy + native caller gates"]
    Q --> R["No ordinary caller-to-sink closure"]
    S["Prewarm observation"] --> T["process/resource effect"]
    T --> U["No package/HOME/UID0 sink"]
"""
    GRAPH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH.write_text(graph, encoding="utf-8")
    text = """# Phase 17 KFT to PMS identity flow

Ordinary APK / shell
  -> ServiceManager/Binder handle
  -> Amazon private service
  -> IAmazonUserManager tx3
  -> enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent
  -> AmazonPackageManagerImpl / IPackageManager
  -> PackageManagerService.setComponentEnabledSetting
  -> caller, cross-user, protected-package checks
  -> ordinary UID rejected before state mutation

Trusted child lifecycle
  -> child-flagged UserInfo + supplied user id
  -> Tahoe enabled; Fire/Launcher3 disabled for child scope
  -> clearCallingIdentity only for later DPM/profile-owner work

Driver / OTA capability
  -> shipped object + selected DTB/DTBO + merged policy + native caller
  -> missing low-privilege edge

Ordinary-app prewarm
  -> temporary process/resource effect
  -> no package, HOME, UID0, or persistent privilege effect
"""
    GRAPH_TEXT.write_text(text, encoding="utf-8")


def write_report(rows: list[dict[str, str]], stats: dict[str, dict[str, object]]) -> None:
    counts = Counter(row["classification"] for row in rows)
    branches = Counter(row["branch"] for row in rows)
    raw_summary = ", ".join(
        f"{key}: {item['rows']} raw / {item['unique_ids']} unique / malformed={item['malformed'] or 'none'}"
        for key, item in stats.items()
    )
    lines = [
        "# Phase 17 — residual privilege-surface closure",
        "",
        "Date: 2026-08-10 (Asia/Taipei)",
        "Device corpus: Amazon Fire HD 10 (KFTRWI / trona), Fire OS 7.3.3.1 / PS7331, Android 9/API 28.",
        "Scope: any path that could obtain enough authority to change package state, HOME, user policy, OTA/recovery state, kernel/driver state, or UID.",
        "",
        "## Executive result",
        "",
        "**已證實：**本階段沒有找到普通 APK 或 ADB shell 能取得 UID 0、system identity、User 0 Fire Launcher package-state writer、正式 HOME writer、OTA partition writer 或 driver memory primitive 的完整 caller-to-gate-to-sink 鏈。",
        "",
        "**已證實：**KFT IAmazonUserManager transaction 3 的 implementation 會把 supplied UserInfo.id 傳到 Tahoe/Fire/Launcher3 state writers；既有 PHASE6FK 已以 ordinary APK UID 10213 實機送達 tx3，PMS 在 setComponentEnabledSetting() 前拒絕，Fire state 與 HOME 未變。PHASE6FJ 對 User 10 在跨使用者檢查拒絕。這兩次既有測試不重跑。",
        "",
        "**高可信推論：**KFT tx3 是目前最接近「若取得受信任 system caller 就能改變 Fire state」的靜態控制面，但 Stub 缺少可見 caller check 本身不是漏洞證明；stock SELinux service-manager 邊界、下游 PMS caller gate 與 user-scope gate 尚未被繞過。",
        "",
        "**已證實：**AmazonPackageManager facade 的 enabled-state setter 沒有清除 Binder identity；它委派標準 PackageManager/IPackageManager，不是把 ordinary caller 變成 system UID 的代理。",
        "",
        "**已證實（bounded）：**driver、OTA/recovery、OOBE、Amazon flags、input/profile service 具備不同層級的能力或 sink，但現有 corpus 沒有把 ordinary caller 接到可持久提權、Fire state、HOME、partition 或 kernel memory sink。",
        "",
        "## 1. Scope and no-repeat policy",
        "",
        "本階段擴大到 launcher 以外的權限面：KFT/user management、Amazon IPC、PMS/DPM、driver/device node、OOBE/OTA/recovery、profile/input、Amazon package metadata 與既有 runtime deputy。沒有重跑 Phase 3A–16 已完成的 priority matrix、set-home persistence、Fire disable/component tests、child KFT tx3 probes、private Binder parcel probes、driver ioctl、GhostLock/root、OTA/recovery 或 partition 操作。",
        "",
        f"Worker raw input counts: {raw_summary}。並行 worker 輸出的 CSV/Markdown 不一致或 malformed row 只作 QA 記錄；raw 檔案與 hash 保留，不被當作額外證據。",
        "",
        "## 2. Caller to gate to identity/user scope to sink matrix",
        "",
        f"Derived rows: {len(rows)}. Classification counts: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) + ".",
        "",
        "| Branch | Rows |",
        "|---|---:|",
    ]
    for branch, count in sorted(branches.items()):
        lines.append(f"| {branch} | {count} |")
    lines += [
        "",
        "The machine-readable table is output/tables/phase17-residual-privilege-surface.csv. Static capability, accepted caller, and runtime effect remain separate.",
        "",
        "## 3. KFT and PackageManager identity boundary",
        "",
        "Static path:",
        "",
        "AmazonUserManagerImpl.createChildUser(UserInfo)",
        "  -> IAmazonUserManager.Proxy.transact(3)",
        "  -> IAmazonUserManager.Stub.onTransact()",
        "  -> BinderService.enableKftLauncher(UserInfo)",
        "  -> tryEnableKftLauncherComponent(UserInfo)",
        "  -> enable Tahoe FreeTimeLauncherActivity",
        "  -> set Fire Launcher disabled for UserInfo.id",
        "  -> set Launcher3 disabled for UserInfo.id",
        "  -> clearCallingIdentity() only before later DPM/profile-owner work",
        "",
        "The bounded Stub slice shows interface-descriptor enforcement and optional UserInfo unmarshalling. No getCallingUid, checkCallingPermission, or current-user equality check is visible in tx3. Classification: 待驗證 / high-impact static edge, not a vulnerability, because the accepted external caller set is not closed and the service-manager boundary blocks shell.",
        "",
        "PHASE6FK records service=amazonusermanagerservice handle=true from an ordinary APK, then uid=10213 in PMS and SecurityException: Attempt to change component state at PackageManagerService.setEnabledSetting / setComponentEnabledSetting. Result=false, Tahoe was not enabled, Fire HOME remained priority 50, and the APK was removed.",
        "",
        "PHASE6FJ records the analogous User 10 attempt failing with INTERACT_ACROSS_USERS for ordinary UID 10212. The supplied user ID is not an unrestricted cross-user relay in the observed stock path.",
        "",
        "**結論：Confirmed boundary, not privilege escalation.** The static KFT writer is real, but no ordinary-app or shell route to a User 0 Fire mutation is proven.",
        "",
        "## 4. AmazonPackageManager and other IPC surfaces",
        "",
        "- AmazonPackageManagerImpl — Strong evidence: enabled-state methods delegate to standard PackageManager/IPackageManager and do not call clearCallingIdentity.",
        "- AmazonApplicationFlags — Confirmed, bounded: mutators require amazon.permission.ADD_RM_PKG_METADATA (signature|amazon) and persist /data/system/amazon_package_flags.xml; bounded consumers cover recency, game-mode, and AppCompat, not HOME or Fire state.",
        "- Profile/input services — Strong evidence / Probable: profile picker and input injection are protected or unresolved private surfaces; no direct preferred/HOME/package-state writer is proven.",
        "- Prewarm — Confirmed limited deputy: an ordinary APK previously caused a temporary process/resource effect through a private service; no package, HOME, UID 0, or persistence effect occurred.",
        "",
        "## 5. Driver, OTA, and OOBE surfaces",
        "",
        "CMDQ, ION, M4U, uinput, AUXADC and Amazon diagnostic markers establish source/configuration capability, not a usable caller. Exact shipped object/module, selected DTB/DTBO, merged policy, native opener, UID/domain and input-to-effect path are not jointly closed. No device node, proc/sysfs/debugfs, ioctl, module load or memory operation was performed.",
        "",
        "The OTA controller and deferred/check paths are signature|privileged protected. BootAfterSystemOTAReceiver and its OOBE helper can enable OobeHomeActivity and write setup settings in a trusted post-OTA lifecycle, but no ordinary broadcast replay or shell-to-recovery handoff is proven. The updater has write capability only in recovery/update context behind verification and boot-chain gates.",
        "",
        "**分類：** Strong evidence for capability; low-privilege reachability remains Hypothesis/Unknown.",
        "",
        "## 6. What is required to disable Fire Launcher",
        "",
        "1. A caller accepted by PMS protected-package and user-scope checks, or a trusted internal lifecycle caller that invokes the setter after legitimate elevation.",
        "2. A User 0-scoped package/component state write, not merely a preferred record or foreground redirect.",
        "3. A path not blocked by shell SELinux service discovery, signature permissions, INTERACT_ACROSS_USERS, DevicePolicy/provisioning state, or recovery/AVB verification.",
        "",
        "No current evidence demonstrates all three for a normal app, shell, settings key, AppOp, overlay, profile picker, OTA receiver, or driver node.",
        "",
        "## 7. Classification summary",
        "",
        "- 已證實: PMS rejects the existing ordinary User 0 KFT tx3 route before mutation; cross-user tx3 is rejected; KFT child-scoped writer exists; Amazon facade preserves caller identity; Amazon flags are signature-gated; ordinary prewarm caused only process/resource effect.",
        "- 高可信推論: KFT tx3 authorization and trusted-service caller inventory are the highest-value remaining host-side questions; a successful route would require a materially different trusted caller or changed build/policy boundary.",
        "- 待驗證: complete KFT external caller set; exact Amazon profile/input accepted caller; final driver object/DTB/policy/native joins; OTA native handoff; natural prewarm observation.",
        "- 已排除（bounded scope）: ordinary shell/component disable; ordinary User 0 KFT tx3; User 10 cross-user tx3; preferred record as sufficient HOME replacement; prewarm as package/HOME/root sink; treating source/Kconfig/OTA strings as caller reachability.",
        "- 因風險拒絕測試: guessed Binder transaction/parcel, forged UserInfo, Fire Launcher mutation, driver open/ioctl, Root/GhostLock trigger, OTA/recovery execution, sideload/flash, partition writes, SELinux/service-manager changes and broadcast replay.",
        "",
        "## 8. Recommended next research value",
        "",
        "Only host-only joins remain justified: (a) complete the exact-build trusted caller/reference graph for KFT tx3 and profile/input services; (b) join shipped native ELF, DTB/DTBO, merged policy and node ownership for driver surfaces; and (c) if a natural system prewarm event occurs, passively capture it without manufacturing a private Binder call. A new live mutation is not justified by the present evidence. If the caller/gate/user/sink join remains open, formally close the broad privilege-surface investigation as no ordinary-app/shell privilege path demonstrated.",
        "",
        "## 9. Reproduction",
        "",
        "python3 tools/scripts/build_phase17_residual_closure.py --dry-run",
        "python3 tools/scripts/build_phase17_residual_closure.py --force",
        "python3 -m py_compile tools/scripts/build_phase17_residual_closure.py",
        "sha256sum -c firmware/manifests/PHASE17-HOST-ANALYSIS-20260810/sha256sums.txt",
        "",
        "All commands above are host-only. No rollback is required because this phase performed no device mutation.",
        "",
        "## 10. Outputs",
        "",
        "- findings/phase-17-evidence-index.md",
        "- output/tables/phase17-residual-privilege-surface.csv",
        "- output/call-graphs/phase17-kft-pms-identity-flow.mmd and .md",
        "- firmware/manifests/PHASE17-HOST-ANALYSIS-20260810/sha256sums.txt",
        "- tools/scripts/build_phase17_residual_closure.py",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest() -> None:
    paths = [*WORKERS.values(), *WORKER_DOCS.values(), *KEY_INPUTS, TABLE, INDEX, REPORT, GRAPH, GRAPH_TEXT, Path(__file__).resolve()]
    unique: list[Path] = []
    for path in paths:
        if path not in unique:
            unique.append(path)
    missing = [path for path in unique if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing manifest input/output: " + ", ".join(str(path) for path in missing))
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text("\n".join(f"{sha256(path)}  {path.relative_to(ROOT)}" for path in unique) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    required = [*WORKERS.values(), *WORKER_DOCS.values(), *KEY_INPUTS]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise SystemExit("missing required input: " + ", ".join(str(path) for path in missing))
    rows, stats = collect_rows()
    outputs = [TABLE, INDEX, REPORT, GRAPH, GRAPH_TEXT, MANIFEST]
    if not args.dry_run and not args.force:
        existing = [path for path in outputs if path.exists()]
        if existing:
            raise SystemExit("outputs exist; use --force: " + ", ".join(str(path) for path in existing))
    print("Phase 17 host-only dry-run")
    print(f"derived_rows={len(rows)}")
    for branch, item in stats.items():
        print(f"{branch}: raw_rows={item['rows']} unique_ids={item['unique_ids']} duplicates={item['duplicates'] or 'none'} malformed={item['malformed'] or 'none'} sha256={item['sha256']}")
    for path in outputs:
        print(f"output={path.relative_to(ROOT)}")
    if args.dry_run:
        return 0
    write_table(rows)
    write_index(rows, stats)
    write_graph()
    write_report(rows, stats)
    write_manifest()
    print("generated Phase 17 outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
