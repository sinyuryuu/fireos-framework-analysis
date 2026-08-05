#!/usr/bin/env python3
"""Inventory preserved DEX-disassembly call sites for selected Amazon IPC APIs.

This is a host-only text audit.  It does not obtain a Binder handle, infer a
transaction payload, call a service, launch a process, or mutate a device.
The output distinguishes declarations from invoke instructions and records the
surrounding class/method so a reviewer can return to the exact smali block.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


TARGETS = {
    "preWarmApplicationForUser": "private activity-manager prewarm",
    "setPipVisibility": "private window-manager PIP state",
    "registerKeyEventInterceptor": "private input interception",
    "enableKftLauncherComponent": "KFT child-user launcher state",
    "tryEnableKftLauncherComponent": "KFT child-user launcher wrapper",
}

CLASS_RE = re.compile(r"^  class #[^:]+: (.+?) \('([^']+)'\)")
METHOD_RE = re.compile(r"^\s+(direct|virtual)_method #[^:]+: ([^\s(]+) \(")
INVOKE_RE = re.compile(r"\binvoke-(?:direct|virtual|interface|static)(?:/range)?\b")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sources(values: list[str]) -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--source must be LABEL=PATH: {value}")
        label, raw_path = value.split("=", 1)
        path = Path(raw_path)
        if not path.is_file():
            raise SystemExit(f"missing source: {path}")
        result.append((label, path))
    return result


def classify(class_name: str, method_name: str) -> str:
    if "$Stub" in class_name:
        return "binder-stub-or-dispatch"
    if ".Proxy" in class_name or class_name.endswith("Proxy"):
        return "binder-proxy"
    if class_name.endswith("Impl") or "Amazon" in class_name and "Manager" in class_name:
        return "framework-or-amazon-wrapper"
    if "Service" in class_name or "BinderService" in class_name:
        return "service-or-binder-implementation"
    return "other-preserved-caller"


def scan(label: str, path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current_class = "UNKNOWN_CLASS"
    current_descriptor = "UNKNOWN_DESCRIPTOR"
    current_method = "UNKNOWN_METHOD"
    current_kind = "UNKNOWN_KIND"
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_match.group(1)
            current_descriptor = class_match.group(2)
            current_method = "<class>"
            current_kind = "class"
            continue
        method_match = METHOD_RE.match(line)
        if method_match:
            current_kind = method_match.group(1)
            current_method = method_match.group(2)
            continue
        if not INVOKE_RE.search(line):
            continue
        for target, description in TARGETS.items():
            if f".{target}:" not in line and f";->{target}:" not in line:
                continue
            rows.append({
                "source_label": label,
                "source": str(path),
                "source_sha256": sha256(path),
                "line": line_number,
                "class": current_class,
                "descriptor": current_descriptor,
                "caller_method": current_method,
                "caller_kind": current_kind,
                "classification": classify(current_class, current_method),
                "target_method": target,
                "target_description": description,
                "instruction": line.strip(),
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", required=True, help="LABEL=DISASSEMBLY")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sources = read_sources(args.source)
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "binder_transaction_sent": False,
            "targets": TARGETS,
            "source_count": len(sources),
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    rows: list[dict[str, object]] = []
    for label, path in sources:
        rows.extend(scan(label, path))
    args.output.mkdir(parents=True)
    fields = [
        "source_label", "source", "source_sha256", "line", "class", "descriptor",
        "caller_method", "caller_kind", "classification", "target_method",
        "target_description", "instruction",
    ]
    with (args.output / "caller-map.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    unique_callers: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        target = str(row["target_method"])
        counts[target] = counts.get(target, 0) + 1
        unique_callers.setdefault(target, set()).add((
            str(row["source_label"]), str(row["class"]), str(row["caller_method"])
        ))
    summary_rows = []
    for target, description in TARGETS.items():
        callers = sorted(unique_callers.get(target, set()))
        summary_rows.append({
            "target_method": target,
            "description": description,
            "invoke_count": counts.get(target, 0),
            "unique_source_class_method_count": len(callers),
            "unique_callers": " | ".join(f"{a}:{b}.{c}" for a, b, c in callers),
        })
    with (args.output / "caller-summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "target_method", "description", "invoke_count",
            "unique_source_class_method_count", "unique_callers",
        ], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    graph = ["flowchart LR"]
    edges: set[tuple[str, str]] = set()
    for row in rows:
        caller = f"{row['source_label']}:{row['class']}.{row['caller_method']}"
        target = str(row["target_method"])
        edges.add((caller, target))
    def node(value: str) -> str:
        return "N" + hashlib.sha1(value.encode()).hexdigest()[:10]
    for value in sorted({v for edge in edges for v in edge}):
        graph.append(f'    {node(value)}["{value.replace(chr(34), chr(39))[:140]}"]')
    for caller, target in sorted(edges):
        graph.append(f"    {node(caller)} --> {node(target)}")
    (args.output / "caller-closure.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")

    summary = {
        "host_only": True,
        "device_contacted": False,
        "binder_transaction_sent": False,
        "process_started": False,
        "device_mutated": False,
        "sources": [{"label": label, "path": str(path), "sha256": sha256(path)} for label, path in sources],
        "target_count": len(TARGETS),
        "invoke_count": len(rows),
        "summary": summary_rows,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Text scan records invoke instructions but does not prove runtime execution.",
            "Reflection, native code, generated Binder code and missing artifacts are outside scope.",
            "No Binder transaction or caller spoofing was attempted.",
        ],
    }
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [args.output / "caller-map.csv", args.output / "caller-summary.csv", args.output / "caller-closure.mmd", summary_path]
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in outputs), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
