#!/usr/bin/env python3
"""Classify the preserved rtmutex source pattern without compiling it.

This is a host-only source inspection utility. It does not calculate addresses,
build code, invoke a device, or produce an exploit payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"source is not a file: {args.source}")
    if args.output.exists() and not args.dry_run:
        parser.error(f"refusing to overwrite: {args.output}")
    if args.dry_run:
        print(f"DRY-RUN: inspect {args.source} and write {args.output}")
        return 0

    text = args.source.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if "remove_waiter(" in line), None)
    end = None
    if start is not None:
        brace_count = 0
        seen_brace = False
        for i in range(start, len(lines)):
            brace_count += lines[i].count("{") - lines[i].count("}")
            seen_brace = seen_brace or "{" in lines[i]
            if seen_brace and brace_count <= 0:
                end = i
                break
    block = "\n".join(lines[start : end + 1]) if start is not None and end is not None else ""
    current_cleanup = bool(re.search(r"current\s*->\s*pi_blocked_on\s*=\s*NULL", block))
    waiter_cleanup = bool(re.search(r"waiter\s*->\s*task", block))
    proxy_start = any("rt_mutex_start_proxy_lock" in line for line in lines)
    proxy_remove = proxy_start and any(
        "remove_waiter(lock, waiter)" in line for line in lines
    )
    if current_cleanup and not waiter_cleanup:
        classification = "PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN"
    elif waiter_cleanup:
        classification = "WAITER_TASK_REFERENCE_PRESENT_REVIEW_REQUIRED"
    else:
        classification = "NO_DIRECT_PATTERN_FOUND"

    result = {
        "source": str(args.source),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "remove_waiter_start_line": start + 1 if start is not None else None,
        "remove_waiter_end_line": end + 1 if end is not None else None,
        "current_pi_blocked_on_cleanup": current_cleanup,
        "waiter_task_reference_in_remove_waiter": waiter_cleanup,
        "proxy_start_present": proxy_start,
        "proxy_error_remove_waiter_call_present": proxy_remove,
        "classification": classification,
        "scope": "source semantics only; no compilation, device I/O, address or payload analysis",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
