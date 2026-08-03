#!/usr/bin/env python3
"""Extract approximate caller-to-callee edges from Java/Smali/VDEX text."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


METHOD_DECL = re.compile(r"(?:direct_method|virtual_method|\.method)\s+[^:]*:?\s*([\w$<>.]+)?")
INVOKE = re.compile(r"L([\w/$]+);(?:->|\.)?([\w$<>]+)[:(]")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--keyword", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    config = parse_args()
    roots = [path.resolve() for path in config.root]
    if any(not root.is_dir() for root in roots):
        print("all --root values must be directories", file=sys.stderr)
        return 2
    if config.output.exists():
        print(f"refusing to overwrite existing output: {config.output}", file=sys.stderr)
        return 2
    if config.dry_run:
        print("DRY-RUN: no disassembly will be read and no output will be written.")
        print(f"DRY-RUN: roots={len(roots)} output={config.output}")
        return 0

    keywords = [re.compile(item, re.I) for item in config.keyword]
    edges: set[tuple[str, str, str, int, str]] = set()
    for root in roots:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".java", ".kt", ".smali", ".log", ".txt"}:
                continue
            current = path.stem
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for number, line in enumerate(lines, start=1):
                declaration = METHOD_DECL.search(line)
                if declaration:
                    current = declaration.group(1) or current
                if keywords and not any(pattern.search(line) or pattern.search(current) for pattern in keywords):
                    continue
                for invoke in INVOKE.finditer(line):
                    callee = f"{invoke.group(1).replace('/', '.')}::{invoke.group(2)}"
                    edges.add((display_path(path), current, callee, number, line.strip()))

    config.output.parent.mkdir(parents=True, exist_ok=True)
    with config.output.open("w", encoding="utf-8") as handle:
        handle.write("file\tcaller\tcallee\tline\ttext\n")
        for row in sorted(edges):
            handle.write("\t".join(str(item).replace("\t", " ") for item in row) + "\n")
    print(f"generated {config.output} edges={len(edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
