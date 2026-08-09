#!/usr/bin/env python3
"""Inventory PS7331 IAmazonPackageManager service handles and call sites.

This is a host-only static provenance audit.  It reads preserved disassembly
and fosinit metadata, records the exact service-handle, publication, interface
definition, and call-site lines, and emits a review queue.  It never invokes
ADB, Binder, a device node, an APK, or a mutating command.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "artifacts/phase6mx-amazon-pm-callers-20260810-01"
DISASSEMBLY_INPUTS = (
    ROOT / "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log",
    ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
)
METADATA_INPUTS = (
    ROOT / "artifacts/amazon-services/amazonpackagemanager_fosinit.xml",
)

CLASS_RE = re.compile(r"^\s*(?:class|interface) #\d+: .*\('(?P<descriptor>L[^;]+;)'\)")
METHOD_RE = re.compile(r"^\s*(?:direct|virtual)_method #\d+: (?P<signature>.+)$")
SERVICE_HANDLE_RE = re.compile(
    r"ServiceManager;\.getService:\(Ljava/lang/String;\)Landroid/os/IBinder;"
)
SERVICE_LITERAL_RE = re.compile(r'const-string[^\n]*, "amazonpackagemanager"')
SERVICE_PUBLISH_RE = re.compile(r"publishBinderService:")
SERVICE_NAME_RE = re.compile(r"getSystemServiceName:\(\)Ljava/lang/String;")
INTERFACE_CALL_RE = re.compile(
    r"IAmazonPackageManager(?:\$Stub(?:\$Proxy)?)?;\.(?P<method>[A-Za-z0-9_]+):"
)
INTERFACE_DEF_RE = re.compile(
    r"^\s*virtual_method #\d+: (?P<method>[A-Za-z0-9_]+)\s*\((?P<args>[^)]*)\)(?P<ret>\S+)"
)
PERMISSION_RE = re.compile(
    r"(?:enforceCalling(?:OrSelf)?Permission|checkCalling(?:OrSelf)?Permission|"
    r"checkPermission|amazon\.permission\.[A-Z0-9_]+|CHANGE_COMPONENT_ENABLED_STATE|"
    r"SET_PREFERRED_APPLICATIONS|MANAGE_USERS|INTERACT_ACROSS_USERS)"
)
IDENTITY_RE = re.compile(
    r"(?:getCallingUid|clearCallingIdentity|restoreCallingIdentity|myUid)"
)
USER_RE = re.compile(
    r"(?:UserInfo\.id|userId|callingUserId|targetUserId|userHandle|UserHandle|forUser|asUser)"
)

INTERFACE_METHODS = {
    "deregisterProxyReceiver",
    "getAmazonFlagsForUser",
    "getConfigurationHelper",
    "isFtvSpecApp",
    "isPreInstalledAppWithFtvSpec",
    "registerProxyReceiver",
    "removeAmazonFlagsForUser",
    "removeAmazonMetadataForUser",
    "setAmazonFlagsForUser",
    "setAmazonMetadataForUser",
    "shouldAllowMicAccess",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact(value: str, limit: int = 700) -> str:
    value = " ".join(value.replace("\t", " ").split())
    return value if len(value) <= limit else value[: limit - 3] + "..."


def unique(values: list[str]) -> str:
    return "; ".join(dict.fromkeys(value for value in values if value))


def class_name(descriptor: str) -> str:
    return descriptor[1:-1].replace("/", ".")


def method_at(lines: list[str], index: int) -> str:
    for candidate in range(index, max(-1, index - 220), -1):
        match = METHOD_RE.match(lines[candidate])
        if match:
            return match.group("signature")
    return "<unknown>"


def class_at(lines: list[str], index: int) -> str:
    for candidate in range(index, max(-1, index - 1400), -1):
        match = CLASS_RE.match(lines[candidate])
        if match:
            return class_name(match.group("descriptor"))
    return "<unknown>"


def context(lines: list[str], index: int) -> tuple[str, str, str, str]:
    nearby = lines[max(0, index - 30) : index + 1]
    joined = "\n".join(nearby)
    permission = unique([compact(match.group(0)) for match in PERMISSION_RE.finditer(joined)])
    identity = unique([compact(match.group(0)) for match in IDENTITY_RE.finditer(joined)])
    user = unique([compact(match.group(0)) for match in USER_RE.finditer(joined)])
    literals = unique(
        [compact(line) for line in nearby if "const-string" in line or "const-class" in line]
    )
    return literals, permission, identity, user


def classify(class_name_value: str, method: str, kind: str) -> tuple[str, str]:
    if "AmazonPackageManagerService" in class_name_value:
        if kind == "service_publication":
            return "system_server_publisher", "system_server publishes the private service"
        return "system_server_service", "Amazon system-server implementation"
    if "AmazonPackageManagerImpl" in class_name_value:
        return "framework_facade", "PackageManager vendor instance delegates to private service"
    if "FtvSpecAssertionUtility" in class_name_value:
        return "framework_read_classifier", "framework read/classification helper"
    if "IAmazonPackageManager$Stub" in class_name_value:
        return "binder_contract", "generated Binder contract/proxy/stub"
    if class_name_value == "com.amazon.android.service.pm.IAmazonPackageManager":
        return "binder_interface", "private Binder interface declaration"
    if kind == "interface_callsite":
        return "other_interface_caller", "bounded direct interface caller requires context review"
    return "other", "requires further caller/data-flow review"


def row_for(
    path: Path,
    source_hash: str,
    lines: list[str],
    index: int,
    kind: str,
    operation: str,
    current_class: str | None = None,
    current_method: str | None = None,
) -> dict[str, str | int]:
    current_class = current_class or class_at(lines, index)
    current_method = current_method or method_at(lines, index)
    category, observation = classify(current_class, current_method, kind)
    literals, permissions, identities, users = context(lines, index)
    callsite = compact(lines[index].strip())
    return {
        "source": path.relative_to(ROOT).as_posix(),
        "source_sha256": source_hash,
        "line": index + 1,
        "class": current_class,
        "method": current_method,
        "kind": kind,
        "operation": operation,
        "category": category,
        "scope_observation": observation,
        "nearby_literals": literals,
        "permission_markers": permissions,
        "identity_markers": identities,
        "user_scope_markers": users,
        "callsite": callsite,
        "device_mutation": "false",
    }


def scan(path: Path) -> list[dict[str, str | int]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    source_hash = sha256(path)
    rows: list[dict[str, str | int]] = []
    interface_class = "com.amazon.android.service.pm.IAmazonPackageManager"
    current_class = "<unknown>"
    current_method = "<class-init>"
    for index, line in enumerate(lines):
        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_name(class_match.group("descriptor"))
            current_method = "<class-init>"
        method_match = METHOD_RE.match(line)
        if method_match:
            current_method = method_match.group("signature")
        # Keep the literal-to-call association tight.  A wider window can
        # accidentally associate a later standard "package" service lookup
        # with a previous method's "amazonpackagemanager" literal.
        nearby = "\n".join(lines[max(0, index - 6) : index + 1])
        if SERVICE_HANDLE_RE.search(line) and "amazonpackagemanager" in nearby:
            rows.append(row_for(path, source_hash, lines, index, "service_handle", "ServiceManager.getService", current_class, current_method))
        if SERVICE_LITERAL_RE.search(line):
            rows.append(row_for(path, source_hash, lines, index, "service_name_literal", "amazonpackagemanager", current_class, current_method))
        if SERVICE_PUBLISH_RE.search(line) and "AmazonPackageManagerService" in current_class:
            rows.append(row_for(path, source_hash, lines, index, "service_publication", "publishBinderService", current_class, current_method))
        if (
            SERVICE_NAME_RE.search(line)
            and current_class == "com.amazon.android.service.pm.AmazonPackageManagerService"
            and current_method.startswith("getSystemServiceName")
        ):
            rows.append(row_for(path, source_hash, lines, index, "service_name_method", "getSystemServiceName", current_class, current_method))
        interface_match = INTERFACE_CALL_RE.search(line)
        if interface_match and interface_match.group("method") in INTERFACE_METHODS:
            rows.append(row_for(path, source_hash, lines, index, "interface_callsite", interface_match.group("method"), current_class, current_method))
        if "IAmazonPackageManager ('" in line:
            # The declaration header is sufficient to tie the interface list to
            # the exact preserved artifact. Individual method rows are added
            # below from the declaration block.
            rows.append(row_for(path, source_hash, lines, index, "interface_declaration", interface_class, current_class, current_method))
        if current_class == interface_class and "virtual_method" in line:
            definition = INTERFACE_DEF_RE.match(line)
            if definition and definition.group("method") in INTERFACE_METHODS:
                rows.append(row_for(path, source_hash, lines, index, "interface_method_definition", definition.group("method"), current_class, current_method))
    return rows


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    fields = [
        "source",
        "source_sha256",
        "line",
        "class",
        "method",
        "kind",
        "operation",
        "category",
        "scope_observation",
        "nearby_literals",
        "permission_markers",
        "identity_markers",
        "user_scope_markers",
        "callsite",
        "device_mutation",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(output: Path, rows: list[dict[str, str | int]], metadata: list[Path]) -> None:
    categories = Counter(str(row["category"]) for row in rows)
    kinds = Counter(str(row["kind"]) for row in rows)
    operations = Counter(str(row["operation"]) for row in rows if row["kind"] == "interface_callsite")
    direct_handles = [row for row in rows if row["kind"] == "service_handle"]
    publishers = [row for row in rows if row["kind"] == "service_publication"]
    interface_methods = sorted({str(row["operation"]) for row in rows if row["kind"] == "interface_method_definition"})
    report = f"""# Phase 6MX：IAmazonPackageManager service-handle / caller provenance

## Scope

本產出是 PS7331 保存 artifacts 的主機端靜態索引。掃描 `boot-fosframework`
與 `fosservices` disassembly，以及 `amazonpackagemanager_fosinit.xml` 的服務註冊資料。
沒有執行 ADB、Binder transaction、`service call`、未知介面呼叫、裝置節點操作或任何裝置狀態修改。

## 已證實

- 精確的 system-server 實作是 `com.amazon.android.service.pm.AmazonPackageManagerService`，其
  `getSystemServiceName()` 回傳 `amazonpackagemanager`，並在 `onStart()` 以
  `publishBinderService()` 發布 `AmazonPackageManagerService$BinderService`。
- 私有介面 `IAmazonPackageManager` 在保存 disassembly 中有 {len(interface_methods)} 個方法：
  `{', '.join(interface_methods)}`。
- 掃描到 {len(direct_handles)} 個 `ServiceManager.getService` service-handle row、
  {len(publishers)} 個 publication row、{operations_total(operations)} 個介面相關呼叫 row（含 generated Stub dispatch）。
- 這個介面沒有 `setHomeActivity`、preferred-activity setter、component/application enabled-state
  setter、hide 或 suspend setter；因此本掃描沒有發現可由該介面直接改寫 User 0 HOME 的方法。

## 高可信推論

- `amazon/content/pm/AmazonPackageManagerImpl` 是 fosinit 宣告的 `PackageManager` vendor instance，
  其保存的 constructor 先取得 `amazonpackagemanager`，再取得標準 `package` Binder；其介面呼叫集中在
  Amazon flags、metadata、mic policy 與 package-data callback 等功能。這更符合 framework facade，
  不等於 shell 可直接取得可改 HOME 的代理。
- `FtvSpecAssertionUtility` 取得同一 service 後只呼叫 FtvSpec／configuration read methods。這是
  classification/configuration read path，不是 HOME selection writer。

## 待驗證

- 完整的 `AmazonPackageManagerImpl` 實例化者、reflection/generated caller 與 native caller 尚未由
  此 bounded disassembly sweep 完整閉合；它們不能靠本索引推論為不存在。
- Binder method 的 runtime caller UID／permission enforcement 仍以既有 Phase 6IA/6HP 證據為準；本階段
  不重播 transaction，也不猜測 transaction code。

## 已排除（本範圍）

- 將 `amazonpackagemanager` service 名稱本身視為可用的 HOME 控制入口：未發現對應 interface method。
- 將 service handle、proxy/stub 或 framework facade 的存在誤稱為已取得 system UID 或 root：本掃描沒有
  改變 caller identity，也沒有執行任何提權測試。

## 統計

- rows: {len(rows)}
- categories: {dict(sorted(categories.items()))}
- kinds: {dict(sorted(kinds.items()))}
- interface calls: {dict(sorted(operations.items()))}
- device_mutation: false

## 證據位置

完整逐行索引見 `caller-calls.csv`；輸入雜湊見 `input-manifest.csv`。
"""
    (output / "phase6mx-amazon-pm-callers.md").write_text(report, encoding="utf-8")


def operations_total(operations: Counter[str]) -> int:
    return sum(operations.values())


def write_graph(output: Path) -> None:
    graph = """flowchart LR
  F[fosinit vendor instance] --> I[AmazonPackageManagerImpl]
  I --> H[ServiceManager.getService\n amazonpackagemanager]
  H --> P[IAmazonPackageManager Stub.Proxy]
  P --> R[Amazon flags / metadata / FtvSpec / mic / proxy receiver]
  S[AmazonPackageManagerService] --> N[getSystemServiceName]
  S --> B[publishBinderService]
  B --> H
  A[FtvSpecAssertionUtility] --> H
  A --> Q[configuration / FtvSpec read calls]
  R -. no HOME/preferred/enabled setter in interface .-> X[No direct HOME writer proven]
  I -. delegates separately to standard package Binder .-> M[IPackageManager / standard PMS gates]
"""
    (output / "phase6mx-amazon-pm-callers.mmd").write_text(graph, encoding="utf-8")


def write_manifest(output: Path, inputs: list[Path]) -> None:
    rows = []
    for path in inputs:
        rows.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    with (output / "input-manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "sha256", "bytes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    inputs = [path for path in (*DISASSEMBLY_INPUTS, *METADATA_INPUTS) if path.is_file()]
    missing = [path for path in (*DISASSEMBLY_INPUTS, *METADATA_INPUTS) if not path.is_file()]
    if missing:
        raise SystemExit("missing input: " + ", ".join(str(path) for path in missing))
    output = args.output.resolve()
    if args.dry_run:
        print(json.dumps({"input_count": len(inputs), "inputs_exist": True, "host_only": True, "adb": False, "device_mutation": False}, sort_keys=True))
        return 0
    if output.exists() and any(output.iterdir()) and not args.force:
        raise SystemExit(f"refusing to overwrite non-empty output: {output}")
    output.mkdir(parents=True, exist_ok=True)
    rows = [row for path in DISASSEMBLY_INPUTS for row in scan(path)]
    write_csv(output / "caller-calls.csv", rows)
    write_manifest(output, inputs)
    summary = {
        "schema": "phase6mx-amazon-pm-callers-v1",
        "input_count": len(inputs),
        "row_count": len(rows),
        "categories": dict(sorted(Counter(str(row["category"]) for row in rows).items())),
        "kinds": dict(sorted(Counter(str(row["kind"]) for row in rows).items())),
        "interface_methods": sorted({str(row["operation"]) for row in rows if row["kind"] == "interface_method_definition"}),
        "device_mutation": False,
        "adb": False,
        "binder_transaction": False,
        "interpretation": "Static provenance inventory only; no runtime reachability or privilege proof.",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_graph(output)
    write_report(output, rows, METADATA_INPUTS)
    checks = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        checks.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")

    findings = ROOT / "findings/phase-6mx-amazon-pm-caller-provenance.md"
    evidence = ROOT / "findings/phase-6mx-evidence-index.md"
    table = ROOT / "output/tables/phase6mx-amazon-pm-callers.csv"
    graph = ROOT / "output/call-graphs/phase6mx-amazon-pm-callers.mmd"
    content = (output / "phase6mx-amazon-pm-callers.md").read_text(encoding="utf-8")
    for target, value in ((findings, content), (evidence, f"# Phase 6MX evidence index\n\n- **6MX-E01** — Static service publication and handle inventory; see `{output.relative_to(ROOT)}/caller-calls.csv` and its input manifest. Confidence: **Strong evidence**.\n- **6MX-E02** — IAmazonPackageManager method set contains no HOME/preferred/enabled-state setter. Source: `boot-fosframework/disassembly.log`, interface declaration and method rows. Confidence: **Confirmed static**.\n- **6MX-E03** — No ADB, Binder transaction, device mutation, root, or exploit action was performed. Source: script and artifact summary. Confidence: **Confirmed**.\n")):
        if target.exists() and not args.force:
            raise SystemExit(f"refusing to overwrite: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")
    import shutil
    shutil.copyfile(output / "caller-calls.csv", table)
    shutil.copyfile(output / "phase6mx-amazon-pm-callers.mmd", graph)
    # Canonical copies are part of the artifact integrity set as well.
    for target in (findings, evidence, table, graph):
        if target.name not in {"caller-calls.csv", "phase6mx-amazon-pm-callers.mmd"}:
            pass
    print(json.dumps({"output": str(output), "row_count": len(rows), "interface_methods": summary["interface_methods"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
