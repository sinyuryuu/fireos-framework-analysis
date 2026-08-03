#!/usr/bin/env python3
"""Build a deterministic class inventory from Java/Kotlin/Smali text."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


JAVA_CLASS = re.compile(
    r"\b(?:class|interface|enum)\s+([A-Za-z_$][\w$]*)(?:\s+extends\s+([\w.$<>]+))?(?:\s+implements\s+([^\{]+))?"
)
SMALI_CLASS = re.compile(r"^\.class\s+[^ ]+\s+L([^;]+);$")
SMALI_SUPER = re.compile(r"^\.super\s+L([^;]+);$")
SMALI_INTERFACE = re.compile(r"^\.implements\s+L([^;]+);$")
PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;")


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

    rows: list[tuple[str, str, int, str, str, str, str]] = []
    for path in iter_files(roots):
        package = ""
        current_class = ""
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, start=1):
            package_match = PACKAGE.search(line)
            if package_match:
                package = package_match.group(1)
            smali = SMALI_CLASS.match(line.strip())
            if smali:
                current_class = smali.group(1).replace("/", ".")
                rows.append(("smali", display_path(path), number, package, current_class, "", ""))
                continue
            java = JAVA_CLASS.search(line)
            if java:
                current_class = f"{package}.{java.group(1)}" if package else java.group(1)
                superclass = java.group(2) or ""
                interfaces = [item.strip() for item in (java.group(3) or "").split(",") if item.strip()]
                rows.append((path.suffix[1:], display_path(path), number, package, current_class, superclass, ",".join(interfaces)))
                continue
            super_match = SMALI_SUPER.match(line.strip())
            if super_match and current_class:
                rows.append(("smali-super", display_path(path), number, package, current_class, super_match.group(1).replace("/", "."), ""))
            interface_match = SMALI_INTERFACE.match(line.strip())
            if interface_match and current_class:
                rows.append(("smali-interface", display_path(path), number, package, current_class, "", interface_match.group(1).replace("/", ".")))

    rows.sort()
    config.output.parent.mkdir(parents=True, exist_ok=True)
    with config.output.open("w", encoding="utf-8", newline="") as handle:
        handle.write("language\tfile\tline\tpackage\tclass\tsuperclass\tinterfaces\n")
        for row in rows:
            handle.write("\t".join(str(item) for item in row) + "\n")
    print(f"generated {config.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
