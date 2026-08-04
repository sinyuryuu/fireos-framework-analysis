#!/usr/bin/env python3
"""Host-only static comparison for the PS7331 Binder CVE-2023-20938 surface.

The tool extracts function ranges and signature/branch markers from the
preserved PS7331 4.4 Binder source.  It records the public Android common
patch references as provenance metadata, but it does not fetch, build,
execute, install, or adapt an exploit and never contacts a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


FUNCTIONS = (
    "binder_validate_ptr",
    "binder_validate_fixup",
    "binder_transaction_buffer_release",
    "binder_translate_fd_array",
    "binder_transaction",
)

REFERENCES = {
    "osv": "https://osv.dev/vulnerability/ASB-A-257685302",
    "aosp_common_fix_commits": [
        "https://android.googlesource.com/kernel/common/+/baa23246e93f/drivers/android/binder.c",
        "https://android.googlesource.com/kernel/common/+/3d213a626d2d/drivers/android/binder.c",
        "https://android.googlesource.com/kernel/common/+/9d1efccf5ec3/drivers/android/binder.c",
        "https://android.googlesource.com/kernel/common/+/b83173bf86a9/drivers/android/binder.c",
        "https://android.googlesource.com/kernel/common/+/aaf236971732/drivers/android/binder.c",
        "https://android.googlesource.com/kernel/common/+/ecf61e4e1117/drivers/android/binder.c",
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def function_block(text: str, name: str) -> tuple[int, int, str] | None:
    match = re.search(rf"\b{re.escape(name)}\s*\([^;]*\)\s*\{{", text, re.DOTALL)
    if not match:
        return None
    start = match.start()
    brace = text.find("{", match.start(), match.end())
    depth = 0
    end = None
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        end = len(text)
    return text.count("\n", 0, start) + 1, text.count("\n", 0, end) + 1, text[start:end]


def marker_count(block: str, marker: str) -> int:
    return len(re.findall(re.escape(marker), block))


def build(source: Path) -> dict[str, object]:
    text = source.read_text(encoding="utf-8", errors="replace")
    functions: list[dict[str, object]] = []
    for name in FUNCTIONS:
        extracted = function_block(text, name)
        if extracted is None:
            functions.append({"name": name, "present": False})
            continue
        start, end, block = extracted
        functions.append(
            {
                "name": name,
                "present": True,
                "line_start": start,
                "line_end": end,
                "sha256": hashlib.sha256(block.encode()).hexdigest(),
                "markers": {
                    "binder_thread_struct_parameter": bool(re.search(r"struct\s+binder_thread\s*\*", block)),
                    "failed_at_pointer_parameter": bool(re.search(r"failed_at\s*\)", block))
                    or bool(re.search(r"binder_size_t\s*\*\s*failed_at", block)),
                    "failed_at_value_parameter": bool(re.search(r"binder_size_t\s+failed_at", block)),
                    "is_failure_parameter": bool(re.search(r"\bbool\s+is_failure", block)),
                    "off_end_offset_marker": "off_end_offset" in block,
                    "copy_from_binder_alloc_marker": "binder_alloc_copy_from_buffer" in block,
                    "validate_ptr_marker": "binder_validate_ptr" in block,
                    "validate_fixup_marker": "binder_validate_fixup" in block,
                    "object_iteration_marker": "binder_get_object" in block
                    or "binder_validate_object" in block,
                },
            }
        )

    release = next((item for item in functions if item["name"] == "binder_transaction_buffer_release"), {})
    release_markers = release.get("markers", {}) if isinstance(release, dict) else {}
    if release.get("present"):
        if release_markers.get("failed_at_pointer_parameter") and not release_markers.get("is_failure_parameter"):
            classification = "VERSION_DIFFERENCE"
            conclusion = "PS7331 uses the older 4.4 release signature; direct equivalence to the later GKI fix is not established."
        else:
            classification = "UNKNOWN"
            conclusion = "The local shape needs a compiler/image-level comparison before CVE applicability can be classified."
    else:
        classification = "UNKNOWN"
        conclusion = "The target release function was not found in the preserved source."

    return {
        "schema": "phase6f-binder-cve-surface-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(source), "sha256": sha256(source), "size": source.stat().st_size},
        "functions": functions,
        "comparison": {
            "classification": classification,
            "conclusion": conclusion,
            "fixed_reference_signature": "binder_proc, binder_thread, binder_buffer, failed_at value, bool is_failure",
            "local_release_signature_observation": "binder_proc, binder_buffer, failed_at pointer",
            "cve": "CVE-2023-20938",
        },
        "references": REFERENCES,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "device_mutated": False,
            "source_built": False,
            "source_executed": False,
            "binder_transaction_test": False,
            "kernel_memory_accessed": False,
            "exploit_or_payload": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "binder-static.json"
    table = output / "binder-static.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["name", "present", "line_start", "line_end", "sha256"]
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["functions"])
    report.write_text(
        "# PS7331 Binder CVE-2023-20938 static surface\n\n"
        "This is a host-only source-shape comparison. No Binder transaction, ioctl,\n"
        "kernel-memory operation, payload, or device mutation was performed.\n\n"
        "## Finding\n\n"
        "- **已證實：** the preserved PS7331 source contains the Binder validation,\n"
        "  transaction, fd-array, and buffer-release function family where present\n"
        "  in the local function index.\n"
        "- **高可信推論：** `binder_transaction_buffer_release()` has the older 4.4\n"
        "  signature with a `failed_at` pointer and no `binder_thread`/`is_failure`\n"
        "  parameters in the extracted source. The later Android common fix references\n"
        "  a different function shape.\n"
        "- **待驗證：** whether the shipped PS7331 binary is byte-for-byte equivalent\n"
        "  to this source and whether the CVE's affected GKI path maps to this 4.4\n"
        "  vendor implementation. The source shape alone does not prove vulnerable\n"
        "  or exploitable status.\n"
        "- **因風險拒絕測試：** crafted Binder transactions, malformed object arrays,\n"
        "  crash testing, memory effects, and privilege escalation.\n\n"
        "## Classification\n\n"
        f"`{result['comparison']['classification']}` — {result['comparison']['conclusion']}\n\n"
        "## References\n\n"
        "- OSV/Android bulletin record: https://osv.dev/vulnerability/ASB-A-257685302\n"
        "- Android common fix commits are recorded in `binder-static.json`.\n",
        encoding="utf-8",
    )
    files = [summary, table, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binder-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.binder_source.is_file():
        raise SystemExit(f"missing Binder source: {args.binder_source}")
    write(build(args.binder_source), args.output)
    print(f"wrote Binder surface audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
