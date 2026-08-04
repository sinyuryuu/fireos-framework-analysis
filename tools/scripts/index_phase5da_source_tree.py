#!/usr/bin/env python3
"""Build a reproducible, host-only index for the PS7331 source tree.

This script never touches an Android device and never executes source-tree
files.  The extracted source tree is intentionally kept outside Git; this
script records its structure and hashes only the focused files needed for the
PS7331/MT8183 review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path


FOCUS_RE = re.compile(
    r"(?:^|/)(?:trona[^/]*|mt8183[^/]*|[^/]*defconfig|futex(?:_compat)?\.c|"
    r"rtmutex(?:_common\.h)?\.c?|futex-requeue-pi\.txt)$",
    re.IGNORECASE,
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path):
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not Path(current, d).is_symlink())
        for name in sorted(files):
            path = Path(current, name)
            if path.is_symlink() or not path.is_file():
                continue
            yield path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path,
                        help="outer extracted source directory")
    parser.add_argument("--output", required=True, type=Path,
                        help="new metadata output directory")
    parser.add_argument("--archive-sha256", default="",
                        help="SHA-256 of the outer source archive")
    parser.add_argument("--dry-run", action="store_true",
                        help="validate paths and print planned outputs only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if not root.is_dir():
        raise SystemExit(f"source root is not a directory: {root}")
    source_roots = [root / "platform", root / "fireos"]
    missing = [str(path) for path in source_roots if not path.is_dir()]
    if missing:
        raise SystemExit("missing source roots: " + ", ".join(missing))
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    files = []
    focused = []
    for source_root in source_roots:
        for path in iter_files(source_root):
            rel = rel_posix(path, root)
            size = path.stat().st_size
            record = {
                "root": source_root.name,
                "path": rel,
                "bytes": size,
                "extension": path.suffix.lower(),
            }
            files.append(record)
            if FOCUS_RE.search("/" + rel):
                record = dict(record)
                record["sha256"] = sha256_file(path)
                focused.append(record)

    if args.dry_run:
        print(f"root={root}")
        print(f"source_roots={','.join(str(p) for p in source_roots)}")
        print(f"files={len(files)} focused_files={len(focused)}")
        print(f"planned_output={output}")
        return 0

    output.mkdir(parents=True)
    with (output / "file-list.tsv").open("w", encoding="utf-8") as stream:
        stream.write("root\tpath\tbytes\textension\n")
        for record in files:
            stream.write("{root}\t{path}\t{bytes}\t{extension}\n".format(**record))

    with (output / "focus-paths.tsv").open("w", encoding="utf-8") as stream:
        stream.write("root\tpath\tbytes\textension\tsha256\n")
        for record in focused:
            stream.write("{root}\t{path}\t{bytes}\t{extension}\t{sha256}\n".format(**record))

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(root),
        "source_roots": [str(path) for path in source_roots],
        "archive_sha256": args.archive_sha256,
        "file_count": len(files),
        "focused_file_count": len(focused),
        "ctags_path": shutil.which("ctags"),
        "clangd_path": shutil.which("clangd"),
        "script": "tools/scripts/index_phase5da_source_tree.py",
        "offline_only": True,
        "source_executed": False,
        "device_touched": False,
    }
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with (output / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for name in ("file-list.tsv", "focus-paths.tsv", "metadata.json"):
            stream.write(f"{sha256_file(output / name)}  {name}\n")

    print(f"indexed files={len(files)} focused_files={len(focused)} output={output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(1)
