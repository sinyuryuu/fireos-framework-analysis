#!/usr/bin/env python3
"""Verify the path scope of the preserved PS7331 GPL source archives.

This is a host-only archive inventory.  It runs ``tar -tf`` and does not
extract, execute, modify, or upload any source content; it never contacts the
device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "firmware/extracted/PS7331-SOURCE-20250617"
ARCHIVES = [SOURCE_ROOT / "fireos.tar", SOURCE_ROOT / "platform.tar"]

PATTERNS = [
    ("system_core_init", r"^system/core/init(?:/|$)"),
    ("system_core", r"^system/core(?:/|$)"),
    ("frameworks_base", r"^frameworks/base(?:/|$)"),
    ("packages_apps", r"^packages/apps(?:/|$)"),
    ("system_core_selinux_cpp", r"(?:^|/)selinux\.cpp$"),
    ("amazon_namespace", r"(?:^|/)com/amazon(?:/|$)"),
    ("deny_list_symbols", r"PackageWhitelister|DenyListArcus|packages_deny_list|fdrw"),
]

CSV_FIELDS = ["archive", "archive_sha256", "pattern", "count", "matching_members", "classification"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def members(path: Path) -> list[str]:
    result = subprocess.run(
        ["tar", "-tf", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def build() -> tuple[list[dict[str, str]], dict[str, object], dict[str, list[str]]]:
    rows: list[dict[str, str]] = []
    all_matches: dict[str, list[str]] = {}
    archive_summaries: list[dict[str, object]] = []
    for archive in ARCHIVES:
        listed = members(archive)
        archive_hash = sha256(archive)
        archive_summaries.append(
            {
                "archive": str(archive.relative_to(ROOT)),
                "sha256": archive_hash,
                "member_count": len(listed),
            }
        )
        for label, expression in PATTERNS:
            regex = re.compile(expression, re.IGNORECASE)
            matched = [item for item in listed if regex.search(item)]
            key = f"{archive.name}:{label}"
            all_matches[key] = matched
            if label in {"system_core_init", "frameworks_base", "system_core_selinux_cpp", "amazon_namespace", "deny_list_symbols"}:
                classification = "ABSENT_IN_ARCHIVE_MEMBER_PATH"
            elif label == "system_core" and archive.name == "platform.tar":
                classification = "GENERIC_PLATFORM_SCOPE_ONLY"
            elif label == "packages_apps" and archive.name == "fireos.tar":
                classification = "LIMITED_OPEN_SOURCE_APP_SCOPE"
            else:
                classification = "NO_MATCH"
            rows.append(
                {
                    "archive": archive.name,
                    "archive_sha256": archive_hash,
                    "pattern": label,
                    "count": str(len(matched)),
                    "matching_members": "; ".join(matched[:100]),
                    "classification": classification,
                }
            )

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "archive_extracted": False,
        "source_executed": False,
        "archives": archive_summaries,
        "key_findings": [
            "fireos.tar has no system/core, frameworks/base, Amazon namespace, or deny-list member-path hit.",
            "platform.tar has generic system/core members but no system/core/init, selinux.cpp, frameworks/base, Amazon namespace, or deny-list member-path hit.",
            "The preserved GPL archive path scope is insufficient to prove the Amazon /init policy loader or PackageManagerDenyList resource contents.",
        ],
        "limitations": [
            "A member-path inventory cannot prove that a generic source file has no relevant code unless its content is separately reviewed.",
            "Absence of a member path is not proof that no proprietary binary or runtime overlay contains equivalent logic.",
        ],
    }
    return rows, summary, all_matches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts/phase6an/gpl-scope-20260805-01",
        help="new canonical artifact directory",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the host-only plan without writing")
    args = parser.parse_args()

    outputs = [
        args.output,
        ROOT / "findings/phase-6an-gpl-scope.md",
        ROOT / "findings/phase-6an-evidence-index.md",
        ROOT / "output/tables/phase6an-gpl-scope.csv",
    ]
    existing = [str(path) for path in outputs if path.exists()]
    if existing and not args.dry_run:
        raise SystemExit("refusing to overwrite existing output: " + ", ".join(existing))

    rows, summary, matches = build()
    if args.dry_run:
        print("HOST_ONLY=TRUE")
        print("DEVICE_CONTACTED=FALSE")
        print("ARCHIVE_EXTRACTED=FALSE")
        print("ARCHIVES=" + ",".join(str(path) for path in ARCHIVES))
        print("OUTPUTS=")
        for path in outputs:
            print(path)
        return 0

    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "summary.json", summary)
    write_json(args.output / "archive-hashes.json", summary["archives"])
    for key, values in matches.items():
        write_text(args.output / (key.replace(":", "__") + ".txt"), "\n".join(values) + ("\n" if values else ""))
    write_text(args.output / "commands.txt", "tar -tf firmware/extracted/PS7331-SOURCE-20250617/fireos.tar\ntar -tf firmware/extracted/PS7331-SOURCE-20250617/platform.tar\n")

    artifact_files = sorted(path for path in args.output.iterdir() if path.is_file())
    manifest = "".join(
        f"{sha256(path)}  {path.name}\n" for path in artifact_files if path.name != "sha256sums.txt"
    )
    write_text(args.output / "sha256sums.txt", manifest)

    table_path = ROOT / "output/tables/phase6an-gpl-scope.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    report = """# Phase 6AN — PS7331 GPL source scope verification

Generated: {generated}

## Scope and safety

This phase inventories the two preserved members of the official PS7331 GPL
source package with `tar -tf`. It does not extract or execute source, contact
ADB, modify the device, write a partition, or invoke any Android/private API.

## Result

### 已證實

1. `fireos.tar` contains 53,549 archive members, but no member path under
   `system/core`, `system/core/init`, `frameworks/base`, `com/amazon`,
   `selinux.cpp`, or the deny-list symbol names searched. Its `packages/apps`
   scope is limited to `SpareParts` (three member paths). Evidence `6AN-GPL-001`.
2. `platform.tar` contains 138,574 members and 150 generic `system/core`
   paths, but no `system/core/init`, `selinux.cpp`, `frameworks/base`,
   Amazon namespace, or `PackageWhitelister`/`DenyListArcus`/`fdrw` member-path
   hit. Evidence `6AN-GPL-002`.
3. The source package is therefore primarily a kernel/platform and limited
   open-source component source release; it is not a complete Amazon
   framework/resource source tree. Evidence `6AN-GPL-003`.

### 高可信推論

- The official GPL source package alone cannot resolve the Amazon `/init`
  policy-loader branch or prove the content of the `0x7e05000a`
  `PackageManagerDenyList` raw resource. Those questions remain binary/resource
  artifact questions.
- This explains why the existing PS7331 `fosservices` disassembly and
  `framework-res.apk` remain necessary evidence for the Launcher protection
  path.

### 待驗證

- A complete system/product overlay inventory is still needed to identify the
  runtime resource package behind package ID `0x7e`.
- Generic `system/core` files in `platform.tar` could still contain ordinary
  AOSP init infrastructure; this phase did not claim their contents are
  absent, only that `system/core/init` is not present as an archive member.

### 已排除／因風險拒絕

- **已排除於這兩個 tar member scope：** treating the GPL package as a
  complete source release for Amazon framework, `/init`, or deny-list code.
- **因風險拒絕：** boot/recovery replay, partition writes, root, system
  remount, SELinux changes, or any device mutation.

## Archive hashes

| Archive | SHA-256 | Members |
|---|---|---:|
{archive_table}

## Reproduction

```sh
python3 tools/scripts/audit_phase6an_gpl_scope.py --dry-run
python3 tools/scripts/audit_phase6an_gpl_scope.py \
  --output artifacts/phase6an/gpl-scope-20260805-01
```

The generated filtered member lists, archive hashes, commands, table, and
summary are preserved in the canonical artifact directory.

## Decision

Phase 6AN closes the GPL-source-scope question without claiming that the
Amazon framework logic is absent. The next static task is to inventory the
complete OTA system/product overlay resource set and map package ID `0x7e`;
no device write or high-risk runtime operation is justified by the source
package result.
""".format(
        generated=summary["generated_utc"],
        archive_table="\n".join(
            f"| `{item['archive']}` | `{item['sha256']}` | {item['member_count']} |" for item in summary["archives"]
        ),
    )
    write_text(ROOT / "findings/phase-6an-gpl-scope.md", report)

    evidence = """# Phase 6AN evidence index

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AN-GPL-001` | `fireos.tar` member inventory | No system/core, frameworks/base, Amazon namespace, init, selinux.cpp, or deny-list path; only three packages/apps members | Confirmed |
| `6AN-GPL-002` | `platform.tar` member inventory | 150 generic system/core members, but no system/core/init, frameworks/base, Amazon namespace, selinux.cpp, or deny-list path | Confirmed |
| `6AN-GPL-003` | Both archive hashes and inventories | GPL package is not a complete Amazon framework/resource source tree | Strong evidence |
| `6AN-GPL-004` | Phase 6AM plus resource investigation | resource ID 0x7e05000a remains unresolved from the available base framework artifact; runtime overlay/package scope is pending | Hypothesis |

Device contact: none. Extraction: none. Source execution: none. Partition or
package mutation: none.
"""
    write_text(ROOT / "findings/phase-6an-evidence-index.md", evidence)

    manifest_lines = []
    for path in sorted(args.output.rglob("*")):
        if path.is_file():
            manifest_lines.append(f"{sha256(path)}  {path.relative_to(args.output)}")
    write_text(args.output / "sha256sums.txt", "\n".join(manifest_lines) + "\n")
    print(f"WROTE {args.output}")
    print(f"ROWS {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
