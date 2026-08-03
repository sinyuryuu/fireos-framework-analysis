#!/usr/bin/env python3
"""Create a deterministic, line-oriented index of launcher-related references.

This intentionally indexes decompiler output rather than trying to infer control
flow.  The resulting TSV is a search aid; conclusions still require review of
the original APK and, for critical branches, smali or bytecode.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("package:firelauncher", re.compile(r"com\.amazon\.firelauncher", re.I)),
    ("intent:ACTION_MAIN", re.compile(r"(?:Intent\.)?ACTION_MAIN|android\.intent\.action\.MAIN", re.I)),
    ("intent:CATEGORY_HOME", re.compile(r"(?:Intent\.)?CATEGORY_HOME|android\.intent\.category\.HOME", re.I)),
    ("key:KEYCODE_HOME", re.compile(r"KEYCODE_HOME", re.I)),
    ("key:HOME_NUMERIC", re.compile(r"(?:getKeyCode\(\)|keyCode)\s*==\s*3|3\s*==\s*(?:getKeyCode\(\)|keyCode)", re.I)),
    ("input:dispatchKeyEvent", re.compile(r"dispatchKeyEvent", re.I)),
    ("home:startHome", re.compile(r"startHome|start_home", re.I)),
    ("home:launchHome", re.compile(r"launchHome|launch_home", re.I)),
    ("home:goHome", re.compile(r"goHome|go_home", re.I)),
    ("home:handleShortPressOnHome", re.compile(r"handleShortPressOnHome", re.I)),
    ("input:interceptKey", re.compile(r"interceptKeyBefore(?:Dispatching|Queueing)", re.I)),
    ("resolver:getHomeActivities", re.compile(r"getHomeActivities", re.I)),
    ("resolver:replacePreferredActivity", re.compile(r"replacePreferredActivity", re.I)),
    ("resolver:resolveHomeActivity", re.compile(r"resolveHomeActivity", re.I)),
    ("package:setEnabledSetting", re.compile(r"setApplicationEnabledSetting|setComponentEnabledSetting|setEnabledSetting", re.I)),
    ("package:disableUser", re.compile(r"disable-user|COMPONENT_ENABLED_STATE_DISABLED_USER|setPackagesSuspended", re.I)),
    ("settings:defaultHome", re.compile(r"DefaultHome|default_home|config_show_default_home|HomeSettings", re.I)),
    ("policy:abortActivityStart", re.compile(r"shouldAbortActivityStart|callShouldAbortActivityStart", re.I)),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        action="append",
        required=True,
        help="Directory to scan; may be repeated.",
    )
    parser.add_argument("--output", required=True, help="New TSV output path.")
    return parser.parse_args()


def workspace_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        # Avoid indexing binary resources and compiled artifacts as text.
        if path.suffix.lower() not in {
            ".java", ".kt", ".smali", ".xml", ".json", ".txt", ".properties", ".mf"
        }:
            continue
        yield path


def main() -> int:
    args = parse_args()
    roots = [Path(item).resolve() for item in args.root]
    output = Path(args.output)
    if output.exists():
        print(f"refusing to overwrite existing output: {output}", file=sys.stderr)
        return 2
    missing = [root for root in roots if not root.is_dir()]
    if missing:
        for root in missing:
            print(f"scan root is not a directory: {root}", file=sys.stderr)
        return 2

    rows: list[tuple[str, str, int, str]] = []
    scanned = 0
    unreadable = 0
    for root in roots:
        for path in iter_text_files(root):
            scanned += 1
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                unreadable += 1
                continue
            for line_number, line in enumerate(content.splitlines(), start=1):
                for label, pattern in PATTERNS:
                    if pattern.search(line):
                        rows.append((label, workspace_path(path), line_number, line.strip()))

    rows.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        handle.write("pattern\tfile\tline\ttext\n")
        for label, path, line_number, line in rows:
            safe_line = line.replace("\t", " ")
            handle.write(f"{label}\t{path}\t{line_number}\t{safe_line}\n")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"generated {output}")
    print(f"scanned_files={scanned} unreadable_files={unreadable} matches={len(rows)}")
    print(f"sha256={digest}")
    print(f"generated_at_utc={dt.datetime.now(dt.timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
