#!/usr/bin/env python3
"""Extract a host-only extended `/init` policy branch window.

The output records instruction-level branch/call markers around the known
rootable/standard path-builder candidates. It never executes the ELF, changes
boot state, loads policy, or contacts a device.
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(init_binary: Path, start: str, stop: str) -> dict[str, object]:
    completed = subprocess.run(
        ["objdump", "-d", f"--start-address={start}", f"--stop-address={stop}", str(init_binary)],
        check=True,
        capture_output=True,
        text=True,
    )
    text = completed.stdout
    patterns = {
        "rootable_callsite_flag": r"41ae44:.*orr\s+w5,\s*wzr,\s*#0x1",
        "standard_callsite_flag": r"41af78:.*mov\s+w5,\s*wzr",
        "helper_flag_branch": r"41be48:.*tbnz\s+w5,\s*#0x0,\s*0x41c30c",
        "rootable_helper_call": r"41ae5c:.*bl\s+0x41be00",
        "standard_helper_call": r"41af80:.*bl\s+0x41be00",
        "alternate_branch_entry": r"41c30c:\s+.*bl\s+0x4ab980",
        "standard_precompiled_path_entry": r"41be4c:\s+.*adrp\s+x0,\s*0x59c000",
    }
    markers = [
        {
            "id": name,
            "pattern": pattern,
            "present": bool(re.search(pattern, text, re.MULTILINE)),
        }
        for name, pattern in patterns.items()
    ]
    return {
        "schema": "phase6d-init-branch-window-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {"init_binary": str(init_binary), "init_binary_sha256": sha256(init_binary)},
        "range": {"start": start, "stop": stop},
        "markers": markers,
        "observations": [
            "The rootable and standard path-builder call sites pass different w5 values into the same stripped helper candidate.",
            "The helper has an instruction-level conditional branch on w5 to 0x41c30c.",
            "The branch target and the pre-branch block have different call/data-flow shapes; exact high-level policy semantics remain unresolved.",
        ],
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "elf_executed": False,
            "boot_property_changed": False,
            "policy_loaded": False,
            "verification_bypassed": False,
            "kernel_memory_accessed": False,
            "root_payload": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    init_binary = Path(result["input"]["init_binary"])
    disassembly = subprocess.run(
        ["objdump", "-d", f"--start-address={result['range']['start']}", f"--stop-address={result['range']['stop']}", str(init_binary)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    raw = output / "disassembly-extended.txt"
    summary = output / "branch-window.json"
    table = output / "branch-markers.csv"
    report = output / "result.md"
    raw.write_text(disassembly, encoding="utf-8")
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "pattern", "present"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["markers"])
    report.write_text(
        "# PS7331 `/init` extended policy branch window\n\n"
        "Host-only `objdump` extraction; the ELF was not executed.\n\n"
        "## Static observations\n\n"
        "- **已證實：** the rootable candidate call site at `0x41ae44` sets `w5=1`\n"
        "  before calling the common helper candidate at `0x41be00`.\n"
        "- **已證實：** the standard candidate call site at `0x41af80` sets `w5=0`\n"
        "  before calling the same helper candidate.\n"
        "- **已證實：** `0x41be48` branches on `w5` to `0x41c30c`; this upgrades the\n"
        "  result from a string/path observation to an instruction-level split.\n"
        "- **待驗證：** the branch's high-level meaning, whether it selects a\n"
        "  rootable policy, and whether the stock boot reaches that path.\n\n"
        "No boot property, policy, partition, kernel memory, or privilege state was\n"
        "changed.\n",
        encoding="utf-8",
    )
    files = [raw, summary, table, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init-binary", type=Path, required=True)
    parser.add_argument("--start", default="0x41ad00")
    parser.add_argument("--stop", default="0x41d5c0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.init_binary.is_file():
        raise SystemExit(f"missing /init binary: {args.init_binary}")
    write(build(args.init_binary, args.start, args.stop), args.output)
    print(f"wrote extended /init branch audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
