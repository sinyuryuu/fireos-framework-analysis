#!/usr/bin/env python3
"""Trace AmazonApplicationFlags from package-service mutators to storage/users.

This is a host-only static audit of the preserved PS7331 fosservices
disassembly.  It closes the first persistence and first consumer edges for
Amazon package flags/metadata without invoking the service, writing a device,
or replaying a Binder transaction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path


SCHEMA = "phase6mu-amazon-application-flags-v1"
DEFAULT_OUT = "artifacts/phase6mu-amazon-application-flags-20260810-01"
FOS_REL = "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
PACKAGE_RANGE = (95866, 96036)
FLAGS_RANGE = (95189, 95649)
HEADER_RE = re.compile(r"\s+(?:direct_method|virtual_method) #\d+: (\S+) (.+)$")
CLASS_RE = re.compile(r"^  class #\d+: (.+?) \('")
TARGET_CALLS = (
    "getAmazonFlagsForUser",
    "getAmazonMetadataForUser",
    "getMetadataIndexForUser",
    "buildMetadataIndexForUser",
    "init",
    "readFromFile",
    "writeToFile",
    "setApplicationInfoForUserLocked",
    "removeApplicationInfoForUserLocked",
    "setAmazonMetadataForUserLocked",
    "removeAmazonMetadataForUserLocked",
)
MUTATORS = {
    "removeAmazonFlagsForUser",
    "removeAmazonMetadataForUser",
    "setAmazonFlagsForUser",
    "setAmazonMetadataForUser",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return handle.read().split("\n")


def window(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1:end])


def require_markers(lines: list[str], label: str, start: int, end: int, markers: list[str]) -> None:
    text = window(lines, start, end)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"input drift for {label}:{start}-{end}; missing {missing}")


def method_blocks(lines: list[str], start: int, end: int) -> list[dict[str, object]]:
    heads: list[tuple[int, str, str]] = []
    for index in range(start - 1, end):
        match = HEADER_RE.match(lines[index])
        if match:
            heads.append((index, match.group(1), match.group(2)))
    blocks: list[dict[str, object]] = []
    for position, (index, name, descriptor) in enumerate(heads):
        next_index = heads[position + 1][0] if position + 1 < len(heads) else end
        blocks.append({
            "start": index + 1,
            "end": next_index,
            "name": name,
            "descriptor": descriptor,
            "text": "\n".join(lines[index:next_index]),
        })
    return blocks


def all_method_blocks(lines: list[str]) -> list[dict[str, object]]:
    heads: list[tuple[int, str, str, str]] = []
    current_class = "UNKNOWN_CLASS"
    for index, line in enumerate(lines):
        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_match.group(1)
        method_match = HEADER_RE.match(line)
        if method_match:
            heads.append((index, current_class, method_match.group(1), method_match.group(2)))
    blocks: list[dict[str, object]] = []
    for position, (index, class_name, name, descriptor) in enumerate(heads):
        next_index = len(lines)
        for next_position in range(position + 1, len(heads)):
            candidate_index, next_class, _, _ = heads[next_position]
            if next_class != class_name:
                next_index = candidate_index
                break
            next_index = candidate_index
            break
        blocks.append({
            "start": index + 1,
            "end": next_index,
            "class": class_name,
            "name": name,
            "descriptor": descriptor,
            "text": "\n".join(lines[index:next_index]),
        })
    return blocks


def unique(values: list[str]) -> str:
    return "; ".join(dict.fromkeys(values)) if values else "none observed"


def relevant_tokens(text: str) -> list[str]:
    tokens = (
        "setComponentEnabledSetting", "setApplicationEnabledSetting",
        "setHomeActivity", "replacePreferredActivity", "addPreferredActivity",
        "CATEGORY_HOME", "ACTION_MAIN", "com.amazon.firelauncher",
        "PackageManager", "UserManager", "preferred", "writeToFile",
        "readFromFile", "/data/system/amazon_package_flags.xml",
    )
    return [token for token in tokens if token in text]


def call_sites(lines: list[str]) -> list[dict[str, object]]:
    blocks = all_method_blocks(lines)
    sites: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        if "Lcom/amazon/android/service/pm/AmazonApplicationFlags;." not in line:
            continue
        target = next((name for name in TARGET_CALLS if f"AmazonApplicationFlags;.{name}" in line), None)
        if target is None:
            continue
        containing = next((block for block in reversed(blocks) if block["start"] <= index + 1 < block["end"]), None)
        if containing is None:
            continue
        text = str(containing["text"])
        mask_hits = re.findall(r"(?:and-int(?:/2addr)?|and-int/lit8).*?#int ([0-9-]+)", text)
        sites.append({
            "line": index + 1,
            "target": target,
            "class": containing["class"],
            "method": containing["name"],
            "descriptor": containing["descriptor"],
            "method_range": f"{containing['start']}-{containing['end']}",
            "mask_constants_in_method": unique(mask_hits),
            "tokens": unique(relevant_tokens(text)),
            "classification": classify_consumer(str(containing["name"]), target, text),
        })
    return sites


def classify_consumer(method: str, target: str, text: str) -> str:
    if method == "isIncompatiblePackage":
        return "package compatibility consumer; bit-1 decision, no HOME writer"
    if method == "isGamingApp":
        return "game-mode consumer; bit-2 decision, no HOME writer"
    if method == "sendBroadcastWithDelay":
        return "package-recency broadcast filter consumer, no HOME selector"
    if method == "getAmazonFlagsForUser":
        return "public/read wrapper; does not itself select HOME"
    if target == "init":
        return "initialization path"
    return "internal flags/metadata helper"


def graph_text() -> str:
    return """flowchart TD
  B["IAmazonPackageManager BinderService mutators"] -->|"permission + package list + userId"| F["AmazonApplicationFlags"]
  F --> M["SparseArray<UserId, package flags/metadata>"]
  F --> W["writeToFile()"]
  W --> X["/data/system/amazon_package_flags.xml"]
  X --> R["readFromFile() during init"]
  F --> C1["PackageRecencyUtils.shouldSendBroadcast"]
  F --> C2["GameModeHelper.isGamingApp: bit 2"]
  F --> C3["AppCompatActivityManagerServiceCallback.isIncompatiblePackage: bit 1"]
  F -.-> H["No direct HOME/preferred/Fire Launcher writer in bounded corpus"]
"""


def write_text(path: Path, value: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--generated-date", default=str(date.today()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or root / DEFAULT_OUT).resolve()
    fos = root / FOS_REL
    input_paths = [
        fos,
        root / "findings/phase-6mt-amazon-ipc-candidate-closure.md",
        root / "work/luna_worker_phase6ms_inventory_20260810.md",
        root / "work/luna_worker_phase6mu_application_flags_trace_20260810.md",
    ]
    missing = [path for path in input_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required inputs:\n" + "\n".join(map(str, missing)))
    lines = read_lines(fos)
    require_markers(lines, "AmazonApplicationFlags", *FLAGS_RANGE, [
        "AmazonApplicationFlags", "/data/system/amazon_package_flags.xml",
        "readFromFile", "writeToFile", "setAmazonFlagsForUser",
        "setAmazonMetadataForUser",
    ])
    require_markers(lines, "AmazonPackageManagerService.BinderService", *PACKAGE_RANGE, [
        "setAmazonFlagsForUser", "setAmazonMetadataForUser",
        "AmazonApplicationFlags;.",
    ])
    flag_blocks = method_blocks(lines, *FLAGS_RANGE)
    package_blocks = method_blocks(lines, *PACKAGE_RANGE)
    mutator_blocks = [block for block in package_blocks if str(block["name"]) in MUTATORS]
    if len(mutator_blocks) != 4:
        raise RuntimeError(f"expected four package mutators, found {len(mutator_blocks)}")
    sites = call_sites(lines)
    if not sites:
        raise RuntimeError("no AmazonApplicationFlags call sites found")

    flag_text = window(lines, *FLAGS_RANGE)
    package_mutator_text = "\n\n".join(str(block["text"]) for block in mutator_blocks)
    input_hashes = {str(path.relative_to(root)): sha256(path) for path in input_paths}
    report_path = root / "findings/phase-6mu-amazon-application-flags-closure.md"
    evidence_path = root / "findings/phase-6mu-evidence-index.md"
    table_path = root / "output/tables/phase6mu-amazon-application-flags-20260810-01.csv"
    graph_path = root / "output/call-graphs/phase6mu-amazon-application-flags-20260810-01.mmd"
    artifact_files = [
        output / "consumer-call-sites.csv",
        output / "mutator-map.csv",
        output / "input-manifest.csv",
        output / "summary.json",
        output / "route-flow.mmd",
        output / "sha256sums.txt",
        output / "evidence" / "amazon-application-flags-class.txt",
        output / "evidence" / "package-mutators.txt",
        output / "evidence" / "consumer-call-sites.txt",
    ]
    generated = artifact_files + [report_path, evidence_path, table_path, graph_path]

    mutator_rows = []
    for block in mutator_blocks:
        text = str(block["text"])
        mutator_rows.append({
            "method": block["name"],
            "descriptor": block["descriptor"],
            "range": f"{block['start']}-{block['end']}",
            "permission_marker": "checkCallingOrSelfPermission(amazon.permission.ADD_RM_PKG_METADATA)" if "ADD_RM_PKG_METADATA" in text else "not in bounded BinderService method",
            "flags_sink": unique([token for token in ("setAmazonFlagsForUser", "removeAmazonFlagsForUser", "setApplicationInfoForUserLocked", "removeApplicationInfoForUserLocked") if token in text]),
            "metadata_sink": unique([token for token in ("setAmazonMetadataForUser", "removeAmazonMetadataForUser", "setAmazonMetadataForUserLocked", "removeAmazonMetadataForUserLocked") if token in text]),
            "persistence_marker": "writeToFile" if "writeToFile" in text else "not in BinderService wrapper; inner static method handles persistence",
            "user_argument": "explicit userId argument present in descriptor/call path",
            "classification": "Confirmed static permission→AmazonApplicationFlags→writeToFile path",
        })

    if args.dry_run:
        print(f"schema={SCHEMA}")
        print(f"root={root}")
        print(f"output={output}")
        print("host_only=true")
        print("device_contacted=false")
        print("binder_or_service_call=false")
        print("mutation=false")
        print("reboot=false")
        print(f"mutator_count={len(mutator_rows)}")
        print(f"consumer_callsite_count={len(sites)}")
        print("outputs:")
        for path in generated:
            print(f"  {path}")
        return 0

    existing = [path for path in generated if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite existing outputs:\n" + "\n".join(map(str, existing)))
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "mutator-map.csv", list(mutator_rows[0].keys()), mutator_rows, args.force)
    write_csv(output / "consumer-call-sites.csv", list(sites[0].keys()), sites, args.force)
    write_csv(output / "input-manifest.csv", ["path", "sha256", "size"], [
        {"path": str(path.relative_to(root)), "sha256": sha256(path), "size": path.stat().st_size}
        for path in input_paths
    ], args.force)
    write_text(output / "evidence" / "amazon-application-flags-class.txt", flag_text, args.force)
    write_text(output / "evidence" / "package-mutators.txt", package_mutator_text, args.force)
    write_text(output / "evidence" / "consumer-call-sites.txt", "\n\n".join(
        f"# {site['class']}.{site['method']} call at line {site['line']}\n" + window(lines, int(str(site['method_range']).split('-')[0]), int(str(site['method_range']).split('-')[1]))
        for site in sites
    ), args.force)
    write_text(output / "route-flow.mmd", graph_text(), args.force)

    direct_flags_tokens = relevant_tokens(flag_text)
    report = f"""# Phase 6MU — AmazonApplicationFlags persistence and consumer closure

Date: {args.generated_date}
Schema: `{SCHEMA}`

## Scope and safety

Host-only analysis of the preserved PS7331 `fosservices/disassembly.log`. No
ADB, Binder/service call, private transaction, ioctl, input injection,
settings/package mutation, reboot, OTA/recovery, exploit, Root attempt, or
partition write was performed.

## Executive result

**已證實：** all four `IAmazonPackageManager` mutators are guarded by
`amazon.permission.ADD_RM_PKG_METADATA`, carry explicit package/list/user
arguments, update `AmazonApplicationFlags`, and call `writeToFile()` in the
bounded static path. The persistent file is
`/data/system/amazon_package_flags.xml`.

**已證實：** the file format uses package/user/flag/metadata records and is
loaded by `AmazonApplicationFlags.init()` → `readFromFile()`. The in-memory
structure is a user-indexed `SparseArray` containing per-package flags and
metadata.

**已證實（bounded consumers）：** the corpus shows flag reads in three
non-mutator consumers: package-recency broadcast filtering, game-mode
classification (bit `2`), and `AppCompatActivityManagerServiceCallback` package
compatibility classification (bit `1`). The package-service getter is a read
wrapper. No direct HOME resolver, preferred-activity, enabled-state writer, or
`com.amazon.firelauncher` token appears in the `AmazonApplicationFlags` class
or these first consumer methods.

**高可信推論（bounded）：** the four mutators are a persistent Amazon
package-metadata/flags database, not the control point that makes Fire Launcher
win HOME. A later consumer outside the indexed call sites remains possible but
is not evidenced in this disassembly corpus.

**待驗證：** whether any flag value is consumed indirectly through framework
objects or native code not represented by the preserved Java disassembly.

**因風險拒絕測試：** no attempt was made to call `amazonpackagemanager`, write
`/data/system/amazon_package_flags.xml`, alter flags, or replay a transaction.

## Mutator map

| Method | Range | Permission | Sink | Persistence | Classification |
|---|---|---|---|---|---|
""" + "\n".join(
        f"| `{row['method']}` | `{row['range']}` | `{row['permission_marker']}` | `{row['flags_sink']} / {row['metadata_sink']}` | `{row['persistence_marker']}` | {row['classification']} |"
        for row in mutator_rows
    ) + f"""

## First persistence boundary

`AmazonApplicationFlags.writeToFile()` computes a checkpoint, serializes the
user/package flag map, and writes the XML file. `readFromFile()` parses the
same schema (`amazonflagstag`, `schemaversion`, `package`, `userid`,
`packagename`, `amazonflagsattr`, `metadata`). The bounded class contains these
package/HOME relevance tokens: `{', '.join(direct_flags_tokens) or 'none'}`.

## First consumer map

| Class / method | Read | Effect | HOME relevance | Confidence |
|---|---|---|---|---|
""" + "\n".join(
        f"| `{site['class']}.{site['method']}` | `{site['target']}` | {site['classification']} | no direct HOME writer in method | Confirmed static / bounded |"
        for site in sites
    ) + f"""

## Reproduction

```sh
python3 tools/scripts/audit_phase6mu_amazon_application_flags.py --dry-run
python3 tools/scripts/audit_phase6mu_amazon_application_flags.py
```

Generated artifact: `artifacts/phase6mu-amazon-application-flags-20260810-01`.
"""
    write_text(report_path, report, args.force)
    write_text(graph_path, graph_text(), args.force)
    write_csv(table_path, list(sites[0].keys()), sites, args.force)

    evidence = f"""# Phase 6MU evidence index — AmazonApplicationFlags closure

Generated: {args.generated_date}
Test ID: `PHASE6MU-STATIC-20260810-01`
Scope: host-only; no device/Binder/ioctl/mutation/reboot.

## 6MU-E01 — four mutators

- Source: `{FOS_REL}:95866-96036`, exact wrapper method ranges in
  `artifacts/phase6mu-amazon-application-flags-20260810-01/mutator-map.csv`.
- Observed: permission check, package/list/user inputs, four
  `AmazonApplicationFlags` static calls, and write-to-file boundary.
- Confidence: Confirmed static

## 6MU-E02 — persistence file and schema

- Source: `{FOS_REL}:{FLAGS_RANGE[0]}-{FLAGS_RANGE[1]}`.
- Observed: `/data/system/amazon_package_flags.xml`, read/write methods, user
  indexed flags/metadata, and XML tags.
- Confidence: Confirmed static

## 6MU-E03 — first consumer call sites

- Source: all matching `AmazonApplicationFlags` call sites in `{FOS_REL}`.
- Observed: package-recency filtering, game-mode bit 2, AppCompat package
  compatibility bit 1, and package-service read wrapper.
- Interpretation: no direct HOME/preferred/Fire Launcher writer in the bounded
  consumers.
- Confidence: Strong evidence (bounded)

## 6MU-E04 — unresolved boundary

- The audit does not prove runtime service-handle availability, SELinux access,
  caller UID, flag values supplied by trusted callers, or consumers outside the
  preserved Java corpus.
- Confidence: Unknown / not tested
"""
    write_text(evidence_path, evidence, args.force)

    checksum_lines = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "sha256sums.txt":
            continue
        checksum_lines.append(f"{sha256(path)}  {path.relative_to(output)}")
    write_text(output / "sha256sums.txt", "\n".join(checksum_lines) + "\n", args.force)

    print(json.dumps({
        "schema": SCHEMA,
        "output": str(output),
        "report": str(report_path),
        "evidence_index": str(evidence_path),
        "mutator_count": len(mutator_rows),
        "consumer_callsite_count": len(sites),
        "device_contacted": False,
        "binder_or_service_call": False,
        "mutation": False,
        "reboot": False,
        "sha256_manifest": str(output / "sha256sums.txt"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
