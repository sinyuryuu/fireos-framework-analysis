#!/usr/bin/env python3
"""Compare two Phase 3C snapshots without changing a device."""

from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path


FOCUS = (
    "com.amazon.firelauncher",
    "org.fireosresearch.home",
    "resolve-activity",
    "priority=",
    "mAlways",
    "Persistent Preferred",
    "Preferred Activities",
    "mResumedActivity",
    "topResumedActivity",
    "mCurrentFocus",
    "mFocusedApp",
    "realActivity",
    "origActivity",
    "HOME",
    "launcher",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def files(root: Path) -> dict[str, Path]:
    return {
        str(p.relative_to(root)): p
        for p in root.rglob("*")
        if p.is_file() and p.name != "sha256sums.txt"
    }


def focused(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    lines = []
    for index, line in enumerate(text.splitlines(), 1):
        if any(token.lower() in line.lower() for token in FOCUS):
            lines.append(f"{index}: {line}")
    return lines[:120]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    before = files(args.before)
    after = files(args.after)
    names = sorted(set(before) | set(after))
    changed = []
    for name in names:
        left = before.get(name)
        right = after.get(name)
        if left is None or right is None:
            changed.append((name, "added" if left is None else "removed"))
        elif digest(left) != digest(right):
            changed.append((name, "changed"))

    out: list[str] = [
        "# Phase 3C snapshot comparison",
        "",
        f"- Before: `{args.before}`",
        f"- After: `{args.after}`",
        f"- Before files: `{len(before)}`",
        f"- After files: `{len(after)}`",
        f"- Changed files: `{len(changed)}`",
        "",
        "## Changed files",
        "",
    ]
    if not changed:
        out.append("No file-level changes.")
    else:
        out.extend(f"- `{name}` — {kind}" for name, kind in changed)

    out.extend(["", "## Focused evidence", ""])
    any_focus = False
    for name, kind in changed:
        if kind != "changed" or name not in after:
            continue
        lines = focused(after[name])
        if not lines:
            continue
        any_focus = True
        out.extend([f"### `{name}`", "", "```text", *lines, "```", ""])
    if not any_focus:
        out.append("No changed file contained a configured HOME/package focus token.")

    out.extend(["", "## Small text diffs", ""])
    diff_count = 0
    for name, kind in changed:
        if kind != "changed" or name not in before or name not in after:
            continue
        try:
            old = before[name].read_text(encoding="utf-8", errors="replace").splitlines()
            new = after[name].read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if len(old) > 2000 or len(new) > 2000:
            continue
        diff = list(difflib.unified_diff(old, new, fromfile=f"before/{name}", tofile=f"after/{name}", n=2))
        if diff:
            diff_count += 1
            out.extend([f"### `{name}`", "", "```diff", *diff[:240], "```", ""])
            if diff_count >= 20:
                break
    if diff_count == 0:
        out.append("No small text diff was emitted; use the preserved raw files and hashes.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
