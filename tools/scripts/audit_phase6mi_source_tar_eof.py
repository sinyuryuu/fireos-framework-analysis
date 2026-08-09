#!/usr/bin/env python3
"""Read-only, EOF-complete member-name audit for the PS7331 source tarball.

The archive is streamed through bzip2 and tar. Members are never extracted or
executed. Only aggregate counts, a bounded sensitive-name hit list, and a
small prefix summary are written.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import re
import tarfile
from pathlib import Path


PATTERNS = [
    ("archive_control", re.compile(r"(?:META-INF|updater-script|update-binary|payload\\.bin)", re.I)),
    ("post_install", re.compile(r"(?:postinstall|run_program|otadexopt)", re.I)),
    ("file_mutation", re.compile(r"(?:set_perm|set_metadata|symlink|mount|delete|rename)", re.I)),
    ("partition_or_image", re.compile(r"(?:^|/)(?:system|system_ext|vendor|product|boot|recovery|super)(?:/|$)|(?:^|/)payload\\.bin$", re.I)),
    ("launcher_or_home", re.compile(r"(?:firelauncher|launcher|home)", re.I)),
    ("framework_or_service", re.compile(r"(?:system_server|framework|priv-app|services\\.(?:jar|odex|vdex))", re.I)),
]


def classify(name: str) -> list[str]:
    return [label for label, pattern in PATTERNS if pattern.search(name)]


def bounded_name(name: str, limit: int = 4096) -> str:
    return name if len(name) <= limit else name[:limit] + "...[truncated]"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-hits", type=int, default=20000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.max_hits < 1:
        parser.error("--max-hits must be positive")
    if not args.input.is_file():
        raise SystemExit(f"input does not exist: {args.input}")
    if args.dry_run:
        print(json.dumps({
            "input": str(args.input),
            "input_size": args.input.stat().st_size,
            "output": str(args.output),
            "would_extract": False,
            "would_execute": False,
            "would_mutate_device": False,
        }, ensure_ascii=False))
        return 0

    args.output.mkdir(parents=True, exist_ok=True)
    hit_path = args.output / "sensitive-member-hits.tsv"
    input_stat = args.input.stat()
    raw_sha = hashlib.sha256()
    member_count = 0
    type_counts: collections.Counter[str] = collections.Counter()
    class_counts: collections.Counter[str] = collections.Counter()
    prefix_counts: collections.Counter[str] = collections.Counter()
    hit_count = 0
    hit_truncated = False
    first_names: list[str] = []
    last_names: collections.deque[str] = collections.deque(maxlen=20)
    symlink_names: list[str] = []
    errors: list[str] = []
    reached_eof = False

    # Hash the original compressed bytes and stream the decompressed tar in a
    # separate pass. This avoids retaining archive contents or member names.
    with args.input.open("rb") as raw:
        while True:
            block = raw.read(1024 * 1024)
            if not block:
                break
            raw_sha.update(block)

    with hit_path.open("w", encoding="utf-8") as hits:
        hits.write("index\tmember\ttype\tsize\tclasses\n")
        try:
            with tarfile.open(args.input, mode="r|bz2", errorlevel=2) as archive:
                for member in archive:
                    member_count += 1
                    name = member.name
                    if len(first_names) < 20:
                        first_names.append(name)
                    last_names.append(name)
                    prefix_counts[name.split("/", 1)[0] if name else ""] += 1

                    if member.isdir():
                        type_counts["directory"] += 1
                    elif member.isreg():
                        type_counts["regular"] += 1
                    elif member.issym():
                        type_counts["symlink"] += 1
                        if len(symlink_names) < 100:
                            symlink_names.append(bounded_name(name))
                    elif member.islnk():
                        type_counts["hardlink"] += 1
                    else:
                        type_counts["other"] += 1

                    classes = classify(name)
                    for label in classes:
                        class_counts[label] += 1
                    if classes:
                        hit_count += 1
                        if hit_count <= args.max_hits:
                            hits.write(
                                f"{member_count}\t{bounded_name(name)}\t"
                                f"{member.type!r}\t{member.size}\t{','.join(classes)}\n"
                            )
                        else:
                            hit_truncated = True
                reached_eof = True
        except (EOFError, OSError, tarfile.TarError, ValueError) as exc:
            errors.append(f"{type(exc).__name__}: {exc}")

    summary = {
        "schema": "phase6mi-source-tar-eof-v1",
        "input": str(args.input),
        "input_size": input_stat.st_size,
        "input_sha256": raw_sha.hexdigest(),
        "member_count": member_count,
        "reached_eof": reached_eof,
        "type_counts": dict(sorted(type_counts.items())),
        "sensitive_hit_count": hit_count,
        "sensitive_hit_truncated": hit_truncated,
        "sensitive_class_counts": dict(sorted(class_counts.items())),
        "symlink_names_sample": symlink_names,
        "first_member_names": first_names,
        "last_member_names": list(last_names),
        "top_level_prefix_counts": dict(prefix_counts.most_common(100)),
        "errors": errors,
        "extracted": False,
        "executed": False,
        "device_mutation": False,
    }
    with (args.output / "source-tar-summary.csv").open("w", newline="", encoding="utf-8") as table:
        writer = csv.DictWriter(table, fieldnames=[
            "input", "input_size", "input_sha256", "member_count", "reached_eof",
            "regular_count", "directory_count", "symlink_count", "hardlink_count",
            "sensitive_hit_count", "post_install_or_update_hits", "launcher_or_home_hits",
            "extracted", "executed", "device_mutation",
        ], lineterminator="\n")
        writer.writeheader()
        writer.writerow({
            "input": args.input.as_posix(),
            "input_size": input_stat.st_size,
            "input_sha256": raw_sha.hexdigest(),
            "member_count": member_count,
            "reached_eof": reached_eof,
            "regular_count": type_counts.get("regular", 0),
            "directory_count": type_counts.get("directory", 0),
            "symlink_count": type_counts.get("symlink", 0),
            "hardlink_count": type_counts.get("hardlink", 0),
            "sensitive_hit_count": hit_count,
            "post_install_or_update_hits": class_counts.get("archive_control", 0) + class_counts.get("post_install", 0) + class_counts.get("file_mutation", 0),
            "launcher_or_home_hits": class_counts.get("launcher_or_home", 0),
            "extracted": False,
            "executed": False,
            "device_mutation": False,
        })
    (args.output / "source-tar-flow.mmd").write_text(
        """flowchart LR
  A[Fire_HD10-7.3.3.1.tar.bz2] --> B[bzip2 stream]
  B --> C[tar member headers]
  C --> D[35 outer members; EOF reached]
  D --> E[apps payloads]
  D --> F[fireos.tar]
  D --> G[platform.tar]
  E -. no recovery/update/post-install member .-> X[No OTA writer in outer archive]
  F -. source payload only .-> Y[Offline source analysis]
  G -. source payload only .-> Y
  C -. no extraction or execution .-> Z[Host-only evidence]
""",
        encoding="utf-8",
    )
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in (
        "input_size", "input_sha256", "member_count", "reached_eof",
        "sensitive_hit_count", "sensitive_hit_truncated", "errors",
    )}, ensure_ascii=False))
    return 0 if reached_eof and not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
