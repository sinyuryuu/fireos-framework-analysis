#!/usr/bin/env python3
"""Export the minimal PS7331 deny-list consumer disassembly, host-only.

This creates a small, reviewable excerpt from the preserved local services
VDEX disassembly. It never contacts ADB, executes Android code, or modifies a
device or image. Existing output is never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
DEFAULT_OUTPUT = ROOT / "artifacts/phase6ap/consumer-snippet-20260805-01"
CLASS_MARKER = "  class #663: DenyListArcusHelper "


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "source": str(args.source),
            "output": str(args.output),
            "class_marker": CLASS_MARKER,
        }, indent=2))
        return 0

    if not args.source.is_file():
        raise SystemExit(f"missing source: {args.source}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    lines = args.source.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    try:
        start = next(index for index, line in enumerate(lines) if line.startswith(CLASS_MARKER))
    except StopIteration as exc:
        raise SystemExit(f"class marker not found: {CLASS_MARKER!r}") from exc
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("  class #")),
        len(lines),
    )
    snippet = "".join(lines[start:end])
    args.output.mkdir(parents=True)
    snippet_path = args.output / "fosservices-denylist-consumer.snippet.txt"
    metadata_path = args.output / "source-metadata.json"
    snippet_path.write_text(snippet, encoding="utf-8")
    metadata_path.write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "source_path": str(args.source),
        "source_sha256": sha256(args.source),
        "source_size": args.source.stat().st_size,
        "source_line_start": start + 1,
        "source_line_end_exclusive": end + 1,
        "class": "com.amazon.android.service.pm.DenyListArcusHelper",
        "methods_of_interest": [
            "extractListFromResorces()",
            "processJSON()",
            "initialize()",
        ],
        "limitations": [
            "The excerpt is a static consumer slice, not proof of runtime execution at boot.",
            "The surrounding VDEX and decompiler metadata are not copied into this small artifact.",
        ],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.iterdir() if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output),
        "class": "com.amazon.android.service.pm.DenyListArcusHelper",
        "source_line_start": start + 1,
        "source_line_end_exclusive": end + 1,
        "host_only": True,
        "device_contacted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
