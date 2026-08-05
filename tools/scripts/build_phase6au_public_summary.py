#!/usr/bin/env python3
"""Export bounded, serial-redacted evidence for the Phase 6AU cache test.

This exporter is host-only.  It never contacts ADB, never changes device state,
and never copies the raw ShortcutService dumps into the public artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERIAL_RE = re.compile(r"\bG[A-Z0-9]{8,}\b")
MARKER_RE = re.compile(
    r"Cached launcher:.*|Last known launcher:.*|Launcher: com\.amazon\.firelauncher.*|"
    r"mResumedActivity:.*|realActivity=com\.amazon\.firelauncher/\.Launcher.*"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_required(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing evidence input: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def redact(text: str) -> str:
    return SERIAL_RE.sub("<DEVICE_SERIAL>", text)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact(content), encoding="utf-8", newline="\n")


def markers(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if MARKER_RE.search(line)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--platform", default="PS7331.4463N")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = (ROOT / args.source).resolve()
    output = (ROOT / args.output).resolve()
    if output in (ROOT, Path("/")) or output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    names = {
        "metadata": "metadata.json",
        "before_dump": "before_shortcut_dump.stdout.txt",
        "after_clear_dump": "after_clear_shortcut_dump.stdout.txt",
        "after_home_dump": "after_home_shortcut_dump.stdout.txt",
        "before_resolver": "before_home_resolve.stdout.txt",
        "after_clear_resolver": "after_clear_home_resolve.stdout.txt",
        "after_home_resolver": "after_home_home_resolve.stdout.txt",
        "before_activity": "before_activity.stdout.txt",
        "after_clear_activity": "after_clear_activity.stdout.txt",
        "after_home_activity": "after_home_activity.stdout.txt",
    }
    contents = {key: read_required(source / filename) for key, filename in names.items()}
    metadata = json.loads(contents["metadata"])
    if args.dry_run:
        print(f"would create {output}")
        print(f"test_id={metadata.get('test_id')}")
        print(f"source={source}")
        return 0

    output.mkdir(parents=True)
    public_metadata = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": metadata.get("test_id"),
        "platform": args.platform,
        "scope": "ShortcutService cached default-launcher state only",
        "mutation": "cmd shortcut clear-default-launcher --user 0",
        "home_key_sent": True,
        "conditional_restore": metadata.get("conditional_restore", False),
        "fire_launcher_mutated": False,
        "settings_provider_written": False,
        "unknown_binder_transaction": False,
        "reboot": False,
        "formal_home_resolver_changed": False,
        "classification": "shell-writable cache, not a HOME selection control",
    }
    write_text(output / "metadata.json", json.dumps(public_metadata, indent=2, ensure_ascii=False) + "\n")

    for key in ("before_dump", "after_clear_dump", "after_home_dump"):
        write_text(output / f"{key.replace('_dump', '')}-markers.txt", "\n".join(markers(contents[key])) + "\n")
    for key in ("before_resolver", "after_clear_resolver", "after_home_resolver"):
        write_text(output / f"{key}.txt", contents[key])
    for key in ("before_activity", "after_clear_activity", "after_home_activity"):
        write_text(output / f"{key}-markers.txt", "\n".join(markers(contents[key])) + "\n")

    raw_hashes = {str((source / filename).relative_to(ROOT)): sha256(source / filename)
                  for filename in names.values()}
    write_text(output / "raw-input-sha256.json", json.dumps(raw_hashes, indent=2) + "\n")
    write_text(
        output / "reproduction.md",
        """# Reproduction boundary

The raw capture remains local.  This public artifact was generated offline and
contains only selected markers and resolver output.

```sh
python3 tools/scripts/run_phase6au_shortcut_cache_test.py \\
  --serial DEVICE_SERIAL \\
  --output adb/phase6au/PHASE6AU-SHORTCUT-CACHE-PS7331-T02 \\
  --test-id PHASE6AU-SHORTCUT-CACHE-PS7331-T02
```

The experiment clears only ShortcutService's cached launcher value, sends one
normal Home key, and conditionally restores the Fire HOME record only if the
post-Home resolver is not already the baseline.  It does not disable, hide,
suspend, uninstall, force-stop, or clear Fire Launcher.
""",
    )

    files = sorted(path for path in output.rglob("*") if path.is_file())
    (output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(output)}\n" for path in files),
        encoding="utf-8",
    )
    print(f"created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
