#!/usr/bin/env python3
"""Compare class, method and string inventories without line-number diffing."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


PACKAGE_RE = re.compile(r"^\s*package\s+([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*;")
CLASS_RE = re.compile(r"\b(?:class|interface|enum|@interface)\s+([A-Za-z_$][\w$]*)")
SMALI_CLASS_RE = re.compile(r"^\.class\s+[^ ]+\s+L([^;]+);")
SMALI_METHOD_RE = re.compile(r"^\.method\s+.*?\s([A-Za-z_$<>][\w$<>]*)\(([^)]*)\)(\S+)")
JAVA_METHOD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|synchronized|abstract|native|strictfp|default|inline|override)\s+)*"
    r"(?:[A-Za-z_$][\w$<>\[\].?, ]*\s+)?([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*(?:throws\s+[^\{;]+)?\s*(?:\{|;|$)"
)
STRING_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fireos-dir", required=True, type=Path)
    parser.add_argument("--aosp-dir", required=True, type=Path)
    parser.add_argument("--class-map", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".java", ".kt", ".smali", ".xml", ".txt", ".properties"}:
            yield path


def qualified(package: str, name: str) -> str:
    return f"{package}.{name}" if package else name


def inventory(
    root: Path,
) -> tuple[set[str], set[str], set[str], list[tuple[str, str]], dict[str, set[str]]]:
    classes: set[str] = set()
    methods: set[str] = set()
    strings: set[str] = set()
    suspicious: list[tuple[str, str]] = []
    class_methods: dict[str, set[str]] = {}
    for path in text_files(root):
        content = path.read_text(encoding="utf-8", errors="replace")
        package = ""
        for line in content.splitlines():
            package_match = PACKAGE_RE.match(line)
            if package_match:
                package = package_match.group(1)
                break
        current = qualified(package, path.stem)
        for line in content.splitlines():
            smali = SMALI_CLASS_RE.match(line.strip())
            java = CLASS_RE.search(line)
            if smali:
                current = smali.group(1).replace("/", ".")
                classes.add(current)
            elif java:
                current = qualified(package, java.group(1))
                classes.add(current)
            smali_method = SMALI_METHOD_RE.match(line.strip())
            java_method = JAVA_METHOD_RE.match(line)
            if smali_method:
                method_value = f"{smali_method.group(1)}({smali_method.group(2)}){smali_method.group(3)}"
                methods.add(f"{current}::{method_value}")
                class_methods.setdefault(current, set()).add(method_value)
            elif java_method:
                method_value = f"{java_method.group(1)}({java_method.group(2).strip()})"
                methods.add(f"{current}::{method_value}")
                class_methods.setdefault(current, set()).add(method_value)
            strings.update(STRING_RE.findall(line))
            if re.search(r"com\.amazon|firelauncher|CATEGORY_HOME|KEYCODE_HOME|protected package|deny.?list", line, re.I):
                suspicious.append((str(path), line.strip()))
    return classes, methods, strings, suspicious, class_methods


def write_set(path: Path, header: str, values: set[str]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write(header + "\n")
        for value in sorted(values):
            handle.write(value.replace("\t", " ") + "\n")


def simple_class(value: str) -> str:
    return value.rsplit(".", 1)[-1].replace("$", ".")


def normalize_class(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", simple_class(value)).lower()


def class_matches(fire_classes: set[str], aosp_classes: set[str]) -> list[tuple[str, str, float, str]]:
    """Return conservative class pairs for review, not proof of equivalence."""
    pairs: list[tuple[str, str, float, str]] = []
    used_fire: set[str] = set()
    used_aosp: set[str] = set()
    for value in sorted(fire_classes & aosp_classes):
        pairs.append((value, value, 1.0, "exact-qualified-name"))
        used_fire.add(value)
        used_aosp.add(value)

    fire_remaining = fire_classes - used_fire
    aosp_remaining = aosp_classes - used_aosp
    by_simple: dict[str, list[str]] = {}
    by_normalized: dict[str, list[str]] = {}
    for value in aosp_remaining:
        by_simple.setdefault(simple_class(value), []).append(value)
        by_normalized.setdefault(normalize_class(value), []).append(value)

    for fire_value in sorted(fire_remaining):
        simple_candidates = by_simple.get(simple_class(fire_value), [])
        if len(simple_candidates) == 1 and simple_candidates[0] not in used_aosp:
            aosp_value = simple_candidates[0]
            pairs.append((fire_value, aosp_value, 0.8, "unique-simple-name"))
            used_fire.add(fire_value)
            used_aosp.add(aosp_value)
            continue
        normalized_candidates = [
            candidate for candidate in by_normalized.get(normalize_class(fire_value), []) if candidate not in used_aosp
        ]
        if len(normalized_candidates) == 1:
            aosp_value = normalized_candidates[0]
            pairs.append((fire_value, aosp_value, 0.7, "unique-normalized-simple-name"))
            used_fire.add(fire_value)
            used_aosp.add(aosp_value)
    return pairs


def write_class_similarity(path: Path, pairs: list[tuple[str, str, float, str]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("fireos_class\taosp_class\tscore\treason\n")
        for fire_value, aosp_value, score, reason in pairs:
            handle.write(f"{fire_value}\t{aosp_value}\t{score:.2f}\t{reason}\n")


def write_method_diff(
    path: Path,
    pairs: list[tuple[str, str, float, str]],
    fire_methods: dict[str, set[str]],
    aosp_methods: dict[str, set[str]],
) -> int:
    differences = 0
    with path.open("w", encoding="utf-8") as handle:
        handle.write("fireos_class\taosp_class\tside\tmethod\tclass_match_score\n")
        for fire_class, aosp_class, score, _ in pairs:
            fire_only = fire_methods.get(fire_class, set()) - aosp_methods.get(aosp_class, set())
            aosp_only = aosp_methods.get(aosp_class, set()) - fire_methods.get(fire_class, set())
            for method in sorted(fire_only):
                handle.write(f"{fire_class}\t{aosp_class}\tfireos-only\t{method}\t{score:.2f}\n")
                differences += 1
            for method in sorted(aosp_only):
                handle.write(f"{fire_class}\t{aosp_class}\taosp-only\t{method}\t{score:.2f}\n")
                differences += 1
    return differences


def main() -> int:
    config = parse_args()
    fireos = config.fireos_dir.resolve()
    aosp = config.aosp_dir.resolve()
    if not fireos.is_dir() or not aosp.is_dir():
        print("both --fireos-dir and --aosp-dir must be directories", file=sys.stderr)
        return 2
    if config.class_map and not config.class_map.is_file():
        print(f"class map is not a file: {config.class_map}", file=sys.stderr)
        return 2
    if config.output.exists():
        print(f"refusing to overwrite existing output: {config.output}", file=sys.stderr)
        return 2
    if config.dry_run:
        print("DRY-RUN: no source tree will be scanned and no output will be written.")
        print(f"DRY-RUN: fireos={fireos} aosp={aosp} output={config.output}")
        return 0

    fire_classes, fire_methods, fire_strings, fire_suspicious, fire_class_methods = inventory(fireos)
    aosp_classes, aosp_methods, aosp_strings, _, aosp_class_methods = inventory(aosp)
    pairs = class_matches(fire_classes, aosp_classes)
    config.output.mkdir(parents=True)
    write_set(config.output / "classes_fireos_only.txt", "class", fire_classes - aosp_classes)
    write_set(config.output / "classes_aosp_only.txt", "class", aosp_classes - fire_classes)
    write_set(config.output / "methods_fireos_only.txt", "method", fire_methods - aosp_methods)
    write_set(config.output / "methods_aosp_only.txt", "method", aosp_methods - fire_methods)
    write_set(config.output / "strings_fireos_only.txt", "string", fire_strings - aosp_strings)
    write_set(config.output / "strings_aosp_only.txt", "string", aosp_strings - fire_strings)
    write_class_similarity(config.output / "class_similarity.csv", pairs)
    method_difference_count = write_method_diff(
        config.output / "method_signature_diff.csv", pairs, fire_class_methods, aosp_class_methods
    )
    with (config.output / "suspicious_package_specific_conditions.tsv").open("w", encoding="utf-8") as handle:
        handle.write("file\ttext\n")
        for path, line in sorted(set(fire_suspicious)):
            handle.write(f"{path}\t{line.replace(chr(9), ' ')}\n")
    with (config.output / "manual_review_queue.tsv").open("w", encoding="utf-8") as handle:
        handle.write("item\treason\n")
        handle.write("all package-specific conditions\tReview smali/control flow before attributing an Amazon patch\n")
        handle.write("all class/method differences\tSeparate AOSP tag drift from OEM changes\n")
        if config.class_map:
            handle.write(f"class map\tSupplied map: {config.class_map}\n")
    summary = config.output / "summary.md"
    exact_matches = sum(1 for _, _, score, _ in pairs if score == 1.0)
    structural_coverage = exact_matches / max(len(aosp_classes), 1)
    with summary.open("w", encoding="utf-8") as handle:
        handle.write("# AOSP / Fire OS structural comparison\n\n")
        handle.write(f"- Fire OS classes: {len(fire_classes)}\n- AOSP classes: {len(aosp_classes)}\n")
        handle.write(f"- Fire OS methods: {len(fire_methods)}\n- AOSP methods: {len(aosp_methods)}\n")
        handle.write(f"- Class pairs for review: {len(pairs)}\n- Exact-qualified class pairs: {exact_matches}\n")
        handle.write(f"- Method signature differences among paired classes: {method_difference_count}\n")
        handle.write(f"- Structural exact-class coverage score: {structural_coverage:.4f}\n")
        handle.write(
            "\nThe score is a structural matching aid, not confidence that a difference is an Amazon patch. "
            "Review smali/control flow and separate AOSP tag drift, decompiler artifacts and OEM changes.\n"
        )
    with (config.output / "confidence_score.txt").open("w", encoding="utf-8") as handle:
        handle.write("metric\tvalue\tinterpretation\n")
        handle.write(f"exact_class_coverage\t{structural_coverage:.4f}\tStructural match aid; not patch confidence\n")
        handle.write(f"paired_classes\t{len(pairs)}\tCandidate class pairs requiring review\n")
        handle.write(f"paired_method_differences\t{method_difference_count}\tSignature differences requiring smali/control-flow review\n")
    manifest = config.output / "sha256sums.txt"
    with manifest.open("w", encoding="utf-8") as handle:
        for path in sorted(config.output.iterdir()):
            if path.name == manifest.name:
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            handle.write(f"{digest}  {path.name}\n")
    print(f"generated {config.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
