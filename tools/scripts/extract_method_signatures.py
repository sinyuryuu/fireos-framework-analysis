#!/usr/bin/env python3
"""Extract approximate Java/Kotlin and exact Smali method signatures."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


JAVA_CLASS = re.compile(r"\b(?:class|interface|enum)\s+([A-Za-z_$][\w$]*)")
JAVA_METHOD = re.compile(
    r"^\s*(?:(?:public|protected|private|static|final|synchronized|native|abstract|default|strictfp)\s+)*"
    r"(?:[\w.$<>\[\], ?]+\s+)?([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*(?:throws\s+([^\{]+))?"
)
SMALI_CLASS = re.compile(r"^\.class\s+[^ ]+\s+L([^;]+);")
SMALI_METHOD = re.compile(r"^\.method\s+(.+?)\s+([\w$<>]+)\((.*?)\)(\S+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def iter_files(roots: list[Path]):
    for root in roots:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".java", ".kt", ".smali"}:
                yield path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def main() -> int:
    config = parse_args()
    roots = [path.resolve() for path in config.root]
    missing = [path for path in roots if not path.is_dir()]
    if missing:
        for path in missing:
            print(f"root is not a directory: {path}", file=sys.stderr)
        return 2
    if config.output.exists():
        print(f"refusing to overwrite existing output: {config.output}", file=sys.stderr)
        return 2
    if config.dry_run:
        print("DRY-RUN: no decompiled file will be read and no output will be written.")
        print(f"DRY-RUN: roots={len(roots)} output={config.output}")
        return 0

    rows: list[tuple[str, str, int, str, str, str]] = []
    for path in iter_files(roots):
        current_class = path.stem
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, start=1):
            class_match = SMALI_CLASS.match(line.strip()) or JAVA_CLASS.search(line)
            if class_match:
                current_class = class_match.group(1).replace("/", ".")
            smali = SMALI_METHOD.match(line.strip())
            if smali:
                _modifiers, name, params, result = smali.groups()
                rows.append(("smali", display_path(path), number, current_class, name, f"({params}){result}"))
                continue
            if path.suffix.lower() in {".java", ".kt"}:
                java = JAVA_METHOD.match(line)
                if java and java.group(1) not in {"if", "for", "while", "switch", "catch", "return", "new"}:
                    name, params, throws = java.groups()
                    descriptor = f"({params})" + (f" throws {throws.strip()}" if throws else "")
                    rows.append((path.suffix[1:], display_path(path), number, current_class, name, descriptor))

    rows.sort()
    config.output.parent.mkdir(parents=True, exist_ok=True)
    with config.output.open("w", encoding="utf-8", newline="") as handle:
        handle.write("language\tfile\tline\tclass\tmethod\tdescriptor\n")
        for row in rows:
            handle.write("\t".join(str(item).replace("\t", " ") for item in row) + "\n")
    print(f"generated {config.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
