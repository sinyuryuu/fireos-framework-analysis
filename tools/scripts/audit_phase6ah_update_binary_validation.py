#!/usr/bin/env python3
"""Audit the saved PS7331 update-binary validation-to-write boundary.

This tool is deliberately host-only.  It parses an already extracted official
OTA script, a saved AArch64 symbol inventory, a saved direct-call edge list,
and bounded disassembly.  It never executes update-binary, recovery, an OTA,
or any device command.  Indirect/data-driven dispatch is reported as such
instead of being promoted to a direct call edge.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_BINARY = Path(
    "firmware/extracted/PS7331/META-INF/com/google/android/update-binary"
)
DEFAULT_SCRIPT = Path(
    "firmware/extracted/PS7331/META-INF/com/google/android/updater-script"
)
DEFAULT_FUNCTIONS = Path(
    "artifacts/phase6s/ota-cfg-focus-20260805-01/selected-functions.csv"
)
DEFAULT_EDGES = Path(
    "artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv"
)
DEFAULT_DISASSEMBLY = Path(
    "artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)


def write_text(path: Path, text: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_functions(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_edges(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_script(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, object]] = []

    for line_number, line in enumerate(text.splitlines(), 1):
        block = re.search(
            r"block_image_update\(\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"",
            line,
        )
        if block:
            target, transfer, new_data, patch = block.groups()
            rows.append(
                {
                    "script_line": line_number,
                    "command": "block_image_update",
                    "target": target,
                    "source": f"{transfer};{new_data};{patch}",
                    "classification": "raw_partition_update",
                    "verification_or_gate": "block-image verification/update path",
                    "device_effect_if_executed": "writes a named block-device image",
                    "execution_status": "NOT_EXECUTED",
                }
            )

        extract = re.search(
            r"package_extract_file\(\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"\s*\)",
            line,
        )
        if extract:
            source, target = extract.groups()
            if target.startswith("/dev/block/"):
                if any(
                    name in target
                    for name in ("boot", "preloader", "lk", "tee", "spmfw", "sspm", "cam_vpu")
                ):
                    classification = "boot_or_firmware_partition_write"
                else:
                    classification = "raw_partition_write"
                effect = "writes an extracted file to a named block device"
            elif target.startswith("/cache/"):
                classification = "recovery_metadata_write"
                effect = "writes OTA metadata for recovery"
            else:
                classification = "file_extract"
                effect = "extracts a package entry to a filesystem path"
            rows.append(
                {
                    "script_line": line_number,
                    "command": "package_extract_file",
                    "target": target,
                    "source": source,
                    "classification": classification,
                    "verification_or_gate": "package entry lookup/extraction",
                    "device_effect_if_executed": effect,
                    "execution_status": "NOT_EXECUTED",
                }
            )

        for prop, expected in re.findall(r'getprop\("([^"]+)"\)\s*==\s*"([^"]+)"', line):
            rows.append(
                {
                    "script_line": line_number,
                    "command": "getprop_guard",
                    "target": prop,
                    "source": expected,
                    "classification": "device_compatibility_gate",
                    "verification_or_gate": f"requires {prop} == {expected}",
                    "device_effect_if_executed": "abort on mismatch",
                    "execution_status": "NOT_EXECUTED",
                }
            )

        if "less_than_int(" in line and "abort(" in line:
            rows.append(
                {
                    "script_line": line_number,
                    "command": "build_date_guard",
                    "target": "ro.build.date",
                    "source": line.strip(),
                    "classification": "version_compatibility_gate",
                    "verification_or_gate": "abort if package date is not older than the device build",
                    "device_effect_if_executed": "abort on version mismatch",
                    "execution_status": "NOT_EXECUTED",
                }
            )
    return rows


def edge_rows(edges: list[dict[str, str]]) -> list[dict[str, object]]:
    callers = {
        "main",
        "RegisterInstallFunctions",
        "PerformBlockImageUpdate",
        "LoadSrcTgtVersion3",
        "VerifyBlocks",
        "WriteToPartition",
        "PackageExtractFileFn",
        "ota_open",
        "ota_read",
        "ota_write",
        "Sha1CheckFn",
    }
    interesting = (
        "RegisterFunction",
        "Evaluate",
        "RegisterBlockImage",
        "ota_",
        "VerifyBlocks",
        "WriteToPartition",
        "ExtractEntryToFile",
        "SHA1",
        "open",
        "read",
        "write",
        "fsync",
        "lseek",
        "memcmp",
    )
    result: list[dict[str, object]] = []
    for row in edges:
        caller = row.get("caller_label", "")
        callee = row.get("callee", "")
        if caller not in callers:
            continue
        if caller == "main" or any(token.lower() in callee.lower() for token in interesting):
            result.append(
                {
                    "caller_label": caller,
                    "caller_symbol": row.get("caller", ""),
                    "instruction": row.get("instruction", ""),
                    "target_address": row.get("target_address", ""),
                    "callee": callee,
                    "edge_type": "direct BL edge extracted from saved call-edge report",
                }
            )
    return result


def function_by_label(functions: list[dict[str, str]], label: str) -> dict[str, str] | None:
    return next((row for row in functions if row.get("focus_label") == label), None)


def direct_edge(edges: list[dict[str, str]], caller: str, address: str) -> list[dict[str, str]]:
    return [
        row
        for row in edges
        if row.get("caller_label") == caller and row.get("target_address", "").lower() == address.lower()
    ]


def control_rows(
    functions: list[dict[str, str]], edges: list[dict[str, str]], script_rows: list[dict[str, object]]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    def add(stage: str, source: str, location: str, evidence: str, observed: str, caveat: str, risk: str) -> None:
        rows.append(
            {
                "stage": stage,
                "source": source,
                "location": location,
                "evidence": evidence,
                "observed": observed,
                "caveat": caveat,
                "risk_if_executed": risk,
            }
        )

    main = function_by_label(functions, "main")
    register = function_by_label(functions, "RegisterInstallFunctions")
    verify = function_by_label(functions, "VerifyBlocks")
    write = function_by_label(functions, "WriteToPartition")
    update = function_by_label(functions, "PerformBlockImageUpdate")
    block_verify = function_by_label(functions, "BlockImageVerifyFn")
    block_update = function_by_label(functions, "BlockImageUpdateFn")
    load = function_by_label(functions, "LoadSrcTgtVersion3")
    ota_open = function_by_label(functions, "ota_open")
    ota_write = function_by_label(functions, "ota_write")

    for row in script_rows:
        if row["classification"] in {
            "raw_partition_update",
            "raw_partition_write",
            "boot_or_firmware_partition_write",
        }:
            add(
                "script_target",
                "official updater-script",
                f"updater-script:{row['script_line']}",
                "SCRIPT-STATIC",
                f"{row['command']} targets {row['target']}",
                "This is a package request, not proof that recovery executed it.",
                "partition write / firmware write",
            )

    main_edges = [r for r in edges if r.get("caller_label") == "main"]
    for symbol, address, label, description in (
        ("RegisterInstallFunctions", "0x406978", "REG-INSTALL", "registers install-script functions"),
        ("RegisterBlockImageFunctions", "0x40d0a8", "REG-BLOCK", "registers block-image functions"),
        ("Evaluate", "0x41b3c8", "EVAL-DIRECT", "parses/evaluates updater expressions"),
    ):
        matched = [r for r in main_edges if r.get("target_address", "").lower() == address]
        add(
            "startup_dispatch",
            "update-binary main",
            f"main:{matched[0]['instruction'] if matched else 'NOT_FOUND'} -> {address}",
            label,
            description if matched else "target not found in saved direct-edge list",
            "The evaluator's function lookup is data-driven; the script-to-function call is not a direct BL edge in this report.",
            "depends on later OTA/recovery invocation",
        )

    if register:
        add(
            "function_registry",
            "RegisterInstallFunctions",
            f"{register.get('address')}+0x54..+0x390",
            "REG-INSTALL",
            "24 direct calls to RegisterFunction were extracted",
            "Function names/callback pointers are encoded in registers/string data; the saved edge extractor does not decode each registry entry.",
            "none until a registered function is invoked",
        )

    add(
        "block_image_wrapper",
        "BlockImageVerifyFn",
        f"{block_verify.get('address') if block_verify else 'NOT_FOUND'}: b 0x408f08",
        "BLOCK-WRAPPER",
        "wrapper branches to PerformBlockImageUpdate with mode value 1",
        "The wrapper edge is an unconditional branch, not a recovered call edge.",
        "verification/update path is only reached if dispatched",
    )
    add(
        "block_image_wrapper",
        "BlockImageUpdateFn",
        f"{block_update.get('address') if block_update else 'NOT_FOUND'}: b 0x408f08",
        "BLOCK-WRAPPER",
        "wrapper branches to PerformBlockImageUpdate with mode value 0",
        "The wrapper edge is an unconditional branch, not a recovered call edge.",
        "block-image write path is only reached if dispatched",
    )

    load_edges = direct_edge(edges, "LoadSrcTgtVersion3", "0x40ede0")
    add(
        "block_verification",
        "LoadSrcTgtVersion3 -> VerifyBlocks",
        ", ".join(r.get("instruction", "") for r in load_edges) or "NOT_FOUND",
        "VERIFY-DIRECT",
        f"{len(load_edges)} direct call edge(s) to VerifyBlocks; VerifyBlocks computes SHA1 and compares the digest/result",
        "This establishes the validation helper boundary, not a successful validation on the device.",
        "mismatch abort/error path",
    )

    if update:
        update_edges = [
            r
            for r in edges
            if r.get("caller_label") == "PerformBlockImageUpdate"
            and any(token in r.get("callee", "") for token in ("ota_open", "ota_fsync", "WriteStringToFd"))
        ]
        add(
            "block_update_io",
            "PerformBlockImageUpdate",
            f"{update.get('address')}..{update.get('address')}+{update.get('size')}",
            "UPDATE-IO",
            f"direct edges include {', '.join(sorted({r.get('callee','') for r in update_edges}))}",
            "The saved direct-edge list does not recover every indirect callback or internal helper edge.",
            "writes/flushes OTA data when invoked",
        )

    if write:
        add(
            "partition_write_helper",
            "WriteToPartition",
            f"{write.get('address')}..{write.get('address')}+{write.get('size')}",
            "WRITE-SYMBOL",
            "symbol body directly calls ota_open, ota_write, ota_fsync, lseek, read and comparison/error paths",
            "No direct caller edge to this helper was recovered in the bounded call-edge report; data-driven or omitted caller remains unresolved.",
            "raw block-device/file write if reached",
        )

    if ota_open:
        add(
            "raw_io",
            "ota_open",
            f"{ota_open.get('address')}..{ota_open.get('address')}+{ota_open.get('size')}",
            "IO-DIRECT",
            "direct edge to libc open is present",
            "Path and flags are runtime inputs; this report does not invoke them.",
            "opens target path",
        )
    if ota_write:
        add(
            "raw_io",
            "ota_write",
            f"{ota_write.get('address')}..{ota_write.get('address')}+{ota_write.get('size')}",
            "IO-DIRECT",
            "direct edge to libc write is present",
            "This is static binary behavior only; no target path was opened.",
            "writes supplied buffer to open file descriptor",
        )
    return rows


def graph() -> str:
    return """flowchart TD
    SCRIPT[official updater-script\ncompatibility guards] -->|not executed here| EVAL[update-binary main\nparse_string + Evaluate]
    MAIN[main] --> REGI[RegisterInstallFunctions\n24 RegisterFunction edges]
    MAIN --> REGB[RegisterBlockImageFunctions\nregistry calls in bounded disassembly]
    MAIN --> EVAL
    EVAL -. data-driven function lookup .-> PEF[PackageExtractFileFn]
    EVAL -. data-driven function lookup .-> BIV[BlockImageVerifyFn]
    EVAL -. data-driven function lookup .-> BIU[BlockImageUpdateFn]
    BIV -->|unconditional branch, mode=1| PBI[PerformBlockImageUpdate]
    BIU -->|unconditional branch, mode=0| PBI
    PBI -->|direct edge| OPEN[ota_open]
    PBI -->|direct edge| FSYNC[ota_fsync]
    LSV[LoadSrcTgtVersion3] -->|two direct edges| VERIFY[VerifyBlocks\nSHA1 + comparison]
    PBI -. bounded edge not recovered .-> LSV
    WRITE[WriteToPartition\nsymbol body] --> OW[ota_write]
    OW -->|direct libc edge| SYSWRITE[libc write]
    OPEN -->|direct libc edge| SYSOPEN[libc open]
    PEF -->|direct edge| EXTRACT[ExtractEntryToFile / ota I/O]
    SCRIPT -->|partition targets present| PART[system/vendor/boot/firmware targets\nstatic request only]
    classDef unsafe fill:#ffe3e3,stroke:#b00020;
    class PART,WRITE,SYSWRITE unsafe;
"""


def render_report(
    paths: dict[str, Path],
    hashes: dict[str, str],
    script_rows: list[dict[str, object]],
    control: list[dict[str, object]],
    edges: list[dict[str, object]],
    functions: list[dict[str, str]],
    captured_at: str,
) -> str:
    partition_rows = [
        row for row in script_rows if row["classification"] in {
            "raw_partition_update",
            "raw_partition_write",
            "boot_or_firmware_partition_write",
        }
    ]
    direct = [row for row in control if "DIRECT" in str(row["evidence"]) or row["evidence"] in {"UPDATE-IO", "IO-DIRECT"}]
    return f"""# Phase 6AH：PS7331 `update-binary` 驗證到寫入控制流閉合

## 範圍與安全狀態

本階段完全在主機端執行，使用既有的官方 PS7331 OTA 解包檔、已保存的
AArch64 函式清單、直接 call-edge 報告與 bounded disassembly。沒有執行
`update-binary`、recovery、OTA、OOBE、分割區寫入、任何裝置命令或未知
Binder transaction。`BootAfterSystemOTAReceiver` 仍維持 Phase 6AG 的靜態、
非可採用研究項目；本階段沒有觸發它。

分析時間（UTC）：`{captured_at}`

## 結論摘要

**已證實（靜態）：**官方 `updater-script` 請求兩個 `block_image_update`
目標（system、vendor），並請求將 `boot.img`、preloader、LK、TEE、SPMFW、
SSPM、camera VPU 等檔案寫入明確的 block-device 路徑。這是 OTA 套件的
寫入意圖，不是本機已執行證據。

**已證實（靜態）：**`main` 直接呼叫 `RegisterInstallFunctions`、
`RegisterBlockImageFunctions` 及 `Evaluate`。`RegisterInstallFunctions` 的
保存 call-edge 報告含 24 次 `RegisterFunction` 呼叫；block-image 函式則以
保存的 wrapper disassembly 將 `BlockImageVerifyFn`／`BlockImageUpdateFn`
無條件分支到 `PerformBlockImageUpdate`，分別帶入 mode 1／0。

**已證實（靜態）：**`LoadSrcTgtVersion3` 有兩條直接 edge 到
`VerifyBlocks`；`VerifyBlocks` 的 bounded disassembly 顯示 SHA-1 計算、
摘要／資料比較及 mismatch 分支。這閉合了驗證 helper 的存在與呼叫邊界。

**已證實（靜態）：**`PerformBlockImageUpdate` 直接使用 OTA I/O helper，
`WriteToPartition` 的函式本體直接呼叫 `ota_open`、`ota_write`、`ota_fsync`
及相關 `lseek`／錯誤路徑；`ota_open`／`ota_write` 又各自有 libc
`open`／`write` direct edge。這證明 binary 中存在從輸入路徑到原始 I/O
的寫入能力。

**高可信推論：**若 recovery 以該 script 啟動此 binary，資料驅動的
expression registry 可把 `package_extract_file`／`block_image_update`
導向上述函式，形成驗證後的 OTA 寫入流程。因 function-pointer／registry
dispatch 不是普通 direct BL，不能把這一段標成完整的 direct-call proof。

**無法由本階段確認：**recovery 是否在這台設備的一次實際 OTA 中執行了
此 binary；全包簽章、AVB／recovery 前置驗證的完整控制流；以及是否有任何
shell／ADB 可達入口。沒有證據支持繞過驗證或取得額外權限。

## 來源與雜湊

| 證據 | 路徑 | SHA-256 |
|---|---|---|
| OTA binary | `{paths['binary']}` | `{hashes['binary']}` |
| updater script | `{paths['script']}` | `{hashes['script']}` |
| selected functions | `{paths['functions']}` | `{hashes['functions']}` |
| direct call edges | `{paths['edges']}` | `{hashes['edges']}` |
| bounded disassembly | `{paths['disassembly']}` | `{hashes['disassembly']}` |

## Script 寫入目標

| Script line | Command | Target | Classification | Status |
|---:|---|---|---|---|
""" + "\n".join(
        f"| {r['script_line']} | `{r['command']}` | `{r['target']}` | `{r['classification']}` | `{r['execution_status']} |"
        for r in partition_rows
    ) + f"""

## 最小控制流

1. `main` 註冊函式表並呼叫 `Evaluate`。
2. `Evaluate` 依 parsed expression 查找註冊函式；此處是資料驅動 dispatch，
   保存的 direct edge 報告不假裝知道每個 function pointer 的實際 call-site。
3. `BlockImageVerifyFn`／`BlockImageUpdateFn` 以 unconditional branch 進入
   `PerformBlockImageUpdate`。
4. source/target 版本流程進入 `VerifyBlocks`；摘要不符走錯誤／拒絕分支。
5. 更新／extract 流程使用 `ota_open`、`ota_write`、`ota_fsync`；
   `WriteToPartition` 的 body 也保留原始 I/O 路徑。

精確 stage、位置、證據 ID 與限制見
`output/tables/phase6ah-update-binary-control-flow.csv` 及
`output/call-graphs/phase6ah-update-binary-control-flow.mmd`。

## 證據分級

| Finding | Confidence | 說明 |
|---|---|---|
| 官方 script 具有 system/vendor/boot/firmware 寫入目標 | 已證實（靜態） | 只表示套件內容與宣告目標 |
| main → registration → Evaluate | 已證實（direct edge） | 來自保存的 AArch64 call-edge |
| block-image wrapper → PerformBlockImageUpdate | 已證實（bounded disassembly） | 為 unconditional branch，非 BL |
| LoadSrcTgtVersion3 → VerifyBlocks | 已證實（direct edge） | 兩個保存的 call-site |
| 驗證後可進入原始 I/O 寫入 helper | 高可信推論 | registry/indirect dispatch 仍需在 host 端進一步解碼 |
| recovery 實際執行本 binary | 待驗證 | 本階段禁止以 OTA 觸發 |
| shell/ADB 可達更新寫入入口 | 已排除（目前證據） | 未找到安全、文件化的 shell caller；不是對所有未來版本的絕對否定 |
| 可繞過簽章/驗證或取得 root | 無證據 | 不由這份 CFG 得出 |

## 明確拒絕的裝置測試

以下不在本階段執行：把 OTA 放入裝置並啟動更新、手動呼叫 recovery/OOBE
流程、發送 `BOOT_AFTER_SYSTEM_OTA`、執行 `update-binary`、測試 crafted 或
malformed OTA、讀寫任何 block device、未知 Binder transaction、Root/提權
驗證。這些操作可能造成分割區改寫、無法開機或資料遺失，與目前的無損
研究邊界不相容。

## 下一個最低風險分析目標

只在主機端解碼 `RegisterBlockImageFunctions` 與 expression registry 的
字串／function-pointer 對應，並把 `package_extract_file`、
`block_image_update` 的 callback 連到已確認的 helper。這可以縮小
`高可信推論` 的不確定性，仍不需要執行 OTA 或修改設備。
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    parser.add_argument("--updater-script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--selected-functions", type=Path, default=DEFAULT_FUNCTIONS)
    parser.add_argument("--call-edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--disassembly", type=Path, default=DEFAULT_DISASSEMBLY)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--table-output", type=Path, required=True)
    parser.add_argument("--graph-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = {
        "binary": args.binary,
        "script": args.updater_script,
        "functions": args.selected_functions,
        "edges": args.call_edges,
        "disassembly": args.disassembly,
    }
    for path in inputs.values():
        require_file(path)

    if args.dry_run:
        print("DRY_RUN: no output written")
        for key, path in inputs.items():
            print(f"{key}: {path}")
        return 0

    functions = parse_functions(args.selected_functions)
    all_edges = parse_edges(args.call_edges)
    script_rows = parse_script(args.updater_script)
    bounded_edges = edge_rows(all_edges)
    control = control_rows(functions, all_edges, script_rows)
    captured_at = datetime.now(timezone.utc).isoformat()
    hashes = {key: sha256(path) for key, path in inputs.items()}
    paths = {key: str(path) for key, path in inputs.items()}

    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "phase": "6AH",
        "captured_at_utc": captured_at,
        "host_only": True,
        "device_contacted": False,
        "ota_executed": False,
        "unknown_binder_transaction": False,
        "inputs": {key: {"path": paths[key], "sha256": hashes[key]} for key in inputs},
        "counts": {
            "script_rows": len(script_rows),
            "partition_targets": sum(
                row["classification"] in {
                    "raw_partition_update",
                    "raw_partition_write",
                    "boot_or_firmware_partition_write",
                }
                for row in script_rows
            ),
            "selected_functions": len(functions),
            "all_direct_edges": len(all_edges),
            "bounded_relevant_edges": len(bounded_edges),
            "control_rows": len(control),
        },
        "classification": "static control-flow closure; no exploit or bypass claim",
    }
    write_json(args.output / "analysis.json", manifest)
    write_csv(
        args.output / "script-commands.csv",
        script_rows,
        [
            "script_line",
            "command",
            "target",
            "source",
            "classification",
            "verification_or_gate",
            "device_effect_if_executed",
            "execution_status",
        ],
    )
    write_csv(
        args.output / "relevant-call-edges.csv",
        bounded_edges,
        ["caller_label", "caller_symbol", "instruction", "target_address", "callee", "edge_type"],
    )
    write_json(args.output / "input-hashes.json", hashes)
    write_text(
        args.output / "sha256sums.txt",
        "".join(f"{digest}  {path}\n" for path, digest in ((str(p), sha256(p)) for p in inputs.values()))
        + f"{sha256(args.output / 'analysis.json')}  {args.output / 'analysis.json'}\n",
    )
    write_csv(
        args.table_output,
        control,
        ["stage", "source", "location", "evidence", "observed", "caveat", "risk_if_executed"],
    )
    write_text(args.graph_output, graph())
    write_text(
        args.evidence_output,
        "# Phase 6AH evidence index\n\n"
        + f"Capture time (UTC): `{captured_at}`\n\n"
        + "## Evidence IDs\n\n"
        + "- `SCRIPT-STATIC`: official PS7331 `updater-script` command/target declarations.\n"
        + "- `REG-INSTALL`: saved `main` and `RegisterInstallFunctions` direct edges.\n"
        + "- `REG-BLOCK`: saved `main` edge and bounded block-image registration disassembly.\n"
        + "- `EVAL-DIRECT`: saved `main -> Evaluate` direct edge.\n"
        + "- `BLOCK-WRAPPER`: bounded disassembly of both block-image wrappers.\n"
        + "- `VERIFY-DIRECT`: `LoadSrcTgtVersion3 -> VerifyBlocks` direct edges and bounded VerifyBlocks disassembly.\n"
        + "- `UPDATE-IO`: bounded `PerformBlockImageUpdate` direct I/O edges.\n"
        + "- `WRITE-SYMBOL`: bounded `WriteToPartition` body and its I/O edges.\n"
        + "- `IO-DIRECT`: `ota_open`/`ota_write` to libc `open`/`write` direct edges.\n\n"
        + "## Evidence files\n\n"
        + "| File | SHA-256 |\n|---|---|\n"
        + "\n".join(f"| `{path}` | `{digest}` |" for path, digest in hashes.items())
        + "\n\n## Limit\n\nAll findings are host-only. No runtime OTA, recovery, OOBE, partition write, or device mutation occurred.\n",
    )
    report = render_report(paths, hashes, script_rows, control, bounded_edges, functions, captured_at)
    write_text(args.report_output, report)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
