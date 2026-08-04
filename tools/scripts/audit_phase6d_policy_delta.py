#!/usr/bin/env python3
"""Host-only comparison of standard and ``rootable_*`` CIL artifacts.

The input files are treated as text sets for evidence triage.  The tool does
not compile, load, install, or apply SELinux policy and never contacts a
device.  A policy delta can show that two preserved files differ; it cannot
show that a retail boot selected the rootable file.

Pairs are supplied as ``--pair NAME=NORMAL:ROOTABLE``.  The output directory
is append-free and is never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


FOCUS_PATTERNS = {
    "typepermissive": re.compile(r"\(typepermissive\b"),
    "allow": re.compile(r"\(allow\b"),
    "neverallow": re.compile(r"\(neverallow\b"),
    "su_token": re.compile(r"\bsu\b"),
    "allow_su": re.compile(r"\(allow[^\n]*\bsu\b"),
    "allow_shell": re.compile(r"\(allow[^\n]*\bshell\b"),
    "allow_untrusted_app": re.compile(r"\(allow[^\n]*\buntrusted_app\b"),
    "setcurrent": re.compile(r"\bsetcurrent\b"),
    "dyntransition": re.compile(r"\bdyntransition\b"),
    "capability": re.compile(r"\(capability\b"),
    "init_domain": re.compile(r"\binit\b"),
    "load_policy": re.compile(r"\bload_policy\b"),
    "setenforce": re.compile(r"\bsetenforce\b"),
    "debug_build_marker": re.compile(r"\b(?:userdebug|eng)\b", re.IGNORECASE),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def focus_counts(lines: list[str]) -> dict[str, int]:
    return {name: sum(1 for line in lines if pattern.search(line)) for name, pattern in FOCUS_PATTERNS.items()}


def focused_additions(added: set[str], cap: int = 200) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in sorted(added):
        matches = [name for name, pattern in FOCUS_PATTERNS.items() if pattern.search(line)]
        if matches:
            rows.append({"categories": ",".join(matches), "line": line})
            if len(rows) >= cap:
                break
    return rows


def analyze_pair(name: str, normal: Path, rootable: Path) -> dict[str, object]:
    normal_lines = read_lines(normal)
    rootable_lines = read_lines(rootable)
    normal_set = set(normal_lines)
    rootable_set = set(rootable_lines)
    added = rootable_set - normal_set
    removed = normal_set - rootable_set
    return {
        "name": name,
        "normal": {"path": str(normal), "sha256": sha256(normal), "lines": len(normal_lines)},
        "rootable": {"path": str(rootable), "sha256": sha256(rootable), "lines": len(rootable_lines)},
        "exact_set": {
            "normal_unique": len(normal_set),
            "rootable_unique": len(rootable_set),
            "added_unique": len(added),
            "removed_unique": len(removed),
        },
        "focus_counts": {
            "normal": focus_counts(normal_lines),
            "rootable": focus_counts(rootable_lines),
            "added": focus_counts(sorted(added)),
        },
        "focused_additions": focused_additions(added),
    }


def parse_pair(value: str) -> tuple[str, Path, Path]:
    if "=" not in value or ":" not in value:
        raise argparse.ArgumentTypeError("pair must be NAME=NORMAL:ROOTABLE")
    name, paths = value.split("=", 1)
    normal_text, rootable_text = paths.split(":", 1)
    if not name or not normal_text or not rootable_text:
        raise argparse.ArgumentTypeError("pair must be NAME=NORMAL:ROOTABLE")
    return name, Path(normal_text), Path(rootable_text)


def write_outputs(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    files: list[Path] = []
    summary = output / "summary.json"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files.append(summary)

    table = output / "policy-delta.csv"
    fields = [
        "pair",
        "normal_sha256",
        "rootable_sha256",
        "normal_lines",
        "rootable_lines",
        "normal_unique",
        "rootable_unique",
        "added_unique",
        "removed_unique",
        "focus",
        "normal_count",
        "rootable_count",
        "added_count",
    ]
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for pair in result["pairs"]:
            for focus in FOCUS_PATTERNS:
                writer.writerow(
                    {
                        "pair": pair["name"],
                        "normal_sha256": pair["normal"]["sha256"],
                        "rootable_sha256": pair["rootable"]["sha256"],
                        "normal_lines": pair["normal"]["lines"],
                        "rootable_lines": pair["rootable"]["lines"],
                        "normal_unique": pair["exact_set"]["normal_unique"],
                        "rootable_unique": pair["exact_set"]["rootable_unique"],
                        "added_unique": pair["exact_set"]["added_unique"],
                        "removed_unique": pair["exact_set"]["removed_unique"],
                        "focus": focus,
                        "normal_count": pair["focus_counts"]["normal"][focus],
                        "rootable_count": pair["focus_counts"]["rootable"][focus],
                        "added_count": pair["focus_counts"]["added"][focus],
                    }
                )
    files.append(table)

    focused = output / "focused-additions.txt"
    with focused.open("w", encoding="utf-8") as stream:
        stream.write("Focused additions only; output is capped at 200 lines per pair.\n")
        for pair in result["pairs"]:
            stream.write(f"\n## {pair['name']}\n")
            for row in pair["focused_additions"]:
                stream.write(f"[{row['categories']}] {row['line']}\n")
    files.append(focused)

    report = output / "result.md"
    report_lines = [
        "# PS7331 SELinux policy variant delta (host-only)",
        "",
        "This comparison reads preserved CIL text as line sets. It does not compile, load,",
        "install, select, or apply a policy, and it does not contact a device.",
        "",
        "## Findings",
        "",
        "- **已證實：** the preserved `rootable_*` files differ materially from their",
        "  standard counterparts; focused counts and hashes are in `policy-delta.csv`.",
        "- **高可信推論：** the rootable variants appear more engineering/debug-oriented",
        "  where the focused additions include `typepermissive`, expanded `su` references,",
        "  and additional transition/capability rules.",
        "- **待驗證：** whether any of these files is selected by the retail PS7331 boot",
        "  path; this host-only delta cannot establish active policy selection.",
        "- **因風險拒絕測試：** policy replacement, boot-property injection, AVB bypass,",
        "  `/init` execution, or any attempt to obtain root.",
        "",
        "## Pair summaries",
        "",
        "| Pair | Added unique lines | Removed unique lines | Rootable `typepermissive` | Rootable `su` matches |",
        "|---|---:|---:|---:|---:|",
    ]
    for pair in result["pairs"]:
        report_lines.append(
            f"| {pair['name']} | {pair['exact_set']['added_unique']} | "
            f"{pair['exact_set']['removed_unique']} | "
            f"{pair['focus_counts']['rootable']['typepermissive']} | "
            f"{pair['focus_counts']['rootable']['su_token']} |"
        )
    report_lines.extend(
        [
            "",
            "The comparison is evidence of file content only. It is not evidence that a",
            "writable property, shell command, or retail boot path can select the rootable",
            "variant.",
        ]
    )
    report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    files.append(report)

    manifest = output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pair",
        action="append",
        type=parse_pair,
        required=True,
        help="NAME=NORMAL:ROOTABLE; may be repeated",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    pairs = []
    for name, normal, rootable in args.pair:
        if not normal.is_file() or not rootable.is_file():
            raise SystemExit(f"missing policy pair input: {name}: {normal} / {rootable}")
        pairs.append(analyze_pair(name, normal, rootable))
    result = {
        "schema": "phase6d-policy-delta-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pairs": pairs,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "policy_compiled": False,
            "policy_loaded": False,
            "device_mutated": False,
            "root_payload": False,
        },
        "limits": [
            "CIL line-set differences do not prove semantic policy validity.",
            "The delta does not prove that the retail boot selected a rootable file.",
            "No policy was compiled, loaded, installed, or applied.",
        ],
    }
    write_outputs(result, args.output)
    print(f"wrote host-only policy delta: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
