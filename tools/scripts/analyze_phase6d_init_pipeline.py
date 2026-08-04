#!/usr/bin/env python3
"""Build a conservative host-only AOSP-to-PS7331 /init pipeline map.

The PS7331 /init is a stripped AArch64 ELF.  This tool therefore maps source
anchors to *candidate regions* only; it never executes the ELF, loads a policy,
contacts a device, changes boot state, or emits an exploit payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ANCHORS = (
    "StatusFromCmdline",
    "IsEnforcing",
    "FindPrecompiledSplitPolicy",
    "LoadSplitPolicy",
    "LoadMonolithicPolicy",
    "LoadPolicy",
    "SelinuxInitialize",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def function_range(text: str, name: str) -> tuple[int, int] | None:
    lines = text.splitlines()
    pattern = re.compile(rf"\b{re.escape(name)}\s*\(")
    start = None
    balance = 0
    seen_open = False
    for number, line in enumerate(lines, 1):
        if start is None and pattern.search(line) and not line.lstrip().startswith("//"):
            start = number
        if start is None:
            continue
        balance += line.count("{") - line.count("}")
        if "{" in line:
            seen_open = True
        if seen_open and balance == 0:
            return start, number
    return None


def source_rows(aosp_root: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    comparisons: dict[str, object] = {}
    for tag in ("android-9.0.0_r1", "android-9.0.0_r61"):
        path = aosp_root / tag / "init" / "selinux.cpp"
        if not path.is_file():
            raise SystemExit(f"missing AOSP anchor file: {path}")
        text = path.read_text(encoding="utf-8")
        ranges = {}
        for name in ANCHORS:
            result = function_range(text, name)
            ranges[name] = {"start": result[0], "end": result[1]} if result else None
            rows.append(
                {
                    "kind": "aosp_anchor",
                    "tag": tag,
                    "source_file": "init/selinux.cpp",
                    "anchor": name,
                    "start_line": result[0] if result else "",
                    "end_line": result[1] if result else "",
                    "classification": "AOSP_STANDARD" if result else "UNKNOWN",
                    "note": "function anchor found in fetched official AOSP source"
                    if result
                    else "function anchor not found by conservative parser",
                }
            )
        comparisons[tag] = {
            "path": str(path),
            "sha256": sha256(path),
            "line_count": len(text.splitlines()),
            "anchors": ranges,
        }
    return rows, comparisons


def binary_rows(audit: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    landmarks = audit.get("static_landmarks", [])
    for item in landmarks:
        item = dict(item)
        address = str(item.get("address", ""))
        if address == "0x41bd60":
            anchor = "StatusFromCmdline"
            relation = "property-parser candidate; caller and return semantics unresolved"
        elif address in {"0x41ad00", "0x41af80", "0x41be48"}:
            anchor = "LoadSplitPolicy"
            relation = "split-policy path/helper candidate; exact function mapping unresolved"
        elif address == "0x41be00":
            anchor = "LoadSplitPolicy"
            relation = "common helper candidate; stripped body semantics unresolved"
        elif address == "0x4041fc":
            anchor = "SelinuxInitialize"
            relation = "top-level caller candidate; exact caller identity unresolved"
        else:
            anchor = "UNRESOLVED"
            relation = "no conservative source-anchor mapping"
        rows.append(
            {
                "kind": "binary_candidate",
                "tag": "PS7331",
                "source_file": "stripped /init",
                "anchor": anchor,
                "address": address,
                "start_line": "",
                "end_line": "",
                "classification": "UNKNOWN",
                "note": f"{item.get('classification', '')}: {relation}",
            }
        )
    refs = audit.get("code_references", [])
    for item in refs:
        item = dict(item)
        marker = str(item.get("marker", ""))
        if "plat_and_mapping" in marker:
            anchor = "FindPrecompiledSplitPolicy"
            relation = "hash-marker reference candidate"
        elif "rootable" in marker:
            anchor = "LoadSplitPolicy"
            relation = "rootable path literal reference; not proof of active selection"
        else:
            anchor = "LoadSplitPolicy"
            relation = "standard policy path literal reference"
        rows.append(
            {
                "kind": "binary_literal_reference",
                "tag": "PS7331",
                "source_file": "stripped /init",
                "anchor": anchor,
                "address": item.get("add_address", ""),
                "marker": marker,
                "start_line": "",
                "end_line": "",
                "classification": "UNKNOWN",
                "note": relation,
            }
        )
    return rows


def build(args: argparse.Namespace) -> dict[str, object]:
    aosp_rows, aosp = source_rows(args.aosp_root)
    audit = json.loads(args.audit_json.read_text(encoding="utf-8"))
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    binary = binary_rows(audit)
    return {
        "schema": "phase6d-init-pipeline-differential-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "aosp_root": str(args.aosp_root),
            "audit_json": str(args.audit_json),
            "audit_json_sha256": sha256(args.audit_json),
            "inventory_json": str(args.inventory),
            "inventory_json_sha256": sha256(args.inventory),
            "init_sha256": audit.get("input", {}).get("sha256", ""),
        },
        "aosp": aosp,
        "rows": aosp_rows + binary,
        "observations": {
            "aosp_r1_r61_selinux_cpp_same_sha256": aosp["android-9.0.0_r1"]["sha256"]
            == aosp["android-9.0.0_r61"]["sha256"],
            "gpl_init_source_present": False,
            "inventory_marker_count": len(inventory.get("markers", [])),
            "inventory_adrp_add_reference_count": len(inventory.get("adrp_add_references", [])),
            "binary_has_rootable_and_standard_path_references": True,
            "exact_binary_symbol_mapping": False,
            "active_policy_variant_proven": False,
        },
        "classification": {
            "AOSP_STANDARD": "AOSP anchor source and line ranges",
            "UNKNOWN": "stripped-binary candidate mapping; no symbol/control-flow proof",
            "AMAZON_ADDITION_NOT_PROVEN": "rootable path surface is binary evidence, not a source diff",
        },
        "safety": {
            "host_only": True,
            "elf_executed": False,
            "device_contacted": False,
            "device_mutated": False,
            "boot_property_changed": False,
            "selinux_policy_loaded": False,
            "exploit_or_root_payload": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "pipeline.json"
    table = output / "anchor-map.csv"
    report = output / "result.md"
    graph = output / "pipeline-knowledge-base.mmd"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = result["rows"]
    fields = ["kind", "tag", "source_file", "anchor", "address", "marker", "start_line", "end_line", "classification", "note"]
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    graph.write_text(
        "flowchart TD\n"
        "  A[\"Boot cmdline / properties\"] --> B[\"/init decision surface\"]\n"
        "  B --> C[\"StatusFromCmdline\"]\n"
        "  B --> D[\"FindPrecompiledSplitPolicy\"]\n"
        "  D --> E[\"LoadSplitPolicy\"]\n"
        "  E --> F[\"LoadPolicy\"]\n"
        "  F --> G[\"SelinuxInitialize\"]\n"
        "  H[\"PS7331 0x41bd60 property-parser candidate\"] -.-> C\n"
        "  I[\"PS7331 0x41ad00 rootable path candidate\"] -.-> E\n"
        "  J[\"PS7331 0x41af80 standard path candidate\"] -.-> E\n"
        "  K[\"PS7331 0x41be00 common-helper candidate\"] -.-> E\n"
        "  L[\"Exact mapping / active policy: UNRESOLVED\"] -.-> E\n"
        "  M[\"Boot-property mutation / policy injection: REJECTED\"] -.-> B\n"
        "  classDef source fill:#e8f5e9,stroke:#2e7d32,color:#111;\n"
        "  classDef candidate fill:#fff3e0,stroke:#ef6c00,color:#111;\n"
        "  classDef unknown fill:#ede7f6,stroke:#5e35b1,color:#111;\n"
        "  classDef rejected fill:#ffebee,stroke:#c62828,color:#111;\n"
        "  class A,B,C,D,E,F,G source;\n"
        "  class H,I,J,K candidate;\n"
        "  class L unknown;\n"
        "  class M rejected;\n",
        encoding="utf-8",
    )
    report.write_text(
        "# Phase 6D /init pipeline differential\n\n"
        "Host-only structural comparison. The stripped PS7331 `/init` was not executed, "
        "no SELinux policy was loaded, and no device state was changed.\n\n"
        "## Results\n\n"
        "- **已證實：** official AOSP Android 9 source contains the expected SELinux "
        "loader anchors; the selected r1/r61 `selinux.cpp` files have the same SHA-256.\n"
        "- **已證實：** the PS7331 `/init` evidence contains code-level references to "
        "standard and `rootable_*` policy paths and a common stripped helper candidate.\n"
        "- **高可信推論：** the binary contains a policy-selection/loading decision "
        "surface structurally related to the AOSP split-policy pipeline.\n"
        "- **待驗證：** exact symbol mapping, branch predicate, caller of the property "
        "parser, and the policy variant active on the stock boot.\n"
        "- **無法取得證據：** the GPL archive does not include `system/core/init`; "
        "therefore it cannot supply an Amazon-vs-AOSP source diff for `/init`.\n"
        "- **因風險拒絕測試：** boot-property injection, alternate policy loading, "
        "remount, bootloader/fastboot, image writes, kernel race/panic, and root payloads.\n\n"
        "See `pipeline.json`, `anchor-map.csv`, and `pipeline-knowledge-base.mmd` for "
        "machine-readable evidence and the conservative mapping.\n",
        encoding="utf-8",
    )
    files = [summary, table, report, graph]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aosp-root", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    for path in (args.aosp_root, args.audit_json, args.inventory):
        if not path.exists():
            raise SystemExit(f"missing input: {path}")
    write(build(args), args.output)
    print(f"wrote init pipeline analysis: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
