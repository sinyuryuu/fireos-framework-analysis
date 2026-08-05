#!/usr/bin/env python3
"""Measure Android 9 ShortcutService's cached default-launcher state.

This is a bounded, reversible experiment.  It clears only the shortcut
service's cached launcher value, sends one normal HOME key, and checks whether
the cache is repopulated from the unchanged PackageManager HOME resolver.  It
never changes Fire Launcher package/component state, settings provider data,
permissions, overlays, or partitions.  The explicit serial and output path
are mandatory; existing evidence is never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIRE = "com.amazon.firelauncher/.Launcher"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(argv: list[str], timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)


def save_run(output: Path, name: str, argv: list[str], result: subprocess.CompletedProcess[str]) -> None:
    (output / f"{name}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (output / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    (output / f"{name}.exit_code.txt").write_text(str(result.returncode) + "\n", encoding="utf-8")
    with (output / "commands.txt").open("a", encoding="utf-8") as handle:
        handle.write(f"{shlex.join(argv)}\n")


def capture_state(output: Path, prefix: str, adb: list[str]) -> None:
    commands = {
        "shortcut_dump": adb + ["shell", "dumpsys", "shortcut"],
        # Dump first so the getter cannot repopulate the cached value before
        # the raw cache state is preserved.
        "shortcut_default": adb + ["shell", "cmd", "shortcut", "get-default-launcher", "--user", "0"],
        "home_resolve": adb + [
            "shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME",
        ],
        "preferred": adb + ["shell", "dumpsys", "package", "preferred-activities"],
        "activity": adb + ["shell", "dumpsys", "activity", "activities"],
    }
    for name, argv in commands.items():
        save_run(output, f"{prefix}_{name}", argv, run(argv, timeout=45.0))


def read_stdout(output: Path, name: str) -> str:
    return (output / f"{name}.stdout.txt").read_text(encoding="utf-8", errors="replace")


def contains_fire_launcher(text: str) -> bool:
    return FIRE in text or "com.amazon.firelauncher/com.amazon.firelauncher.Launcher" in text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--test-id", default="PHASE6AU-SHORTCUT-CACHE-PS7331-T01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    output = (ROOT / args.output).resolve()
    if output in (ROOT, Path("/")) or output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    adb = ["adb", "-s", args.serial]
    planned = [
        adb + ["get-state"],
        adb + ["shell", "id"],
        adb + ["shell", "getprop", "ro.build.fingerprint"],
        adb + ["shell", "cmd", "shortcut", "get-default-launcher", "--user", "0"],
        adb + ["shell", "dumpsys", "shortcut"],
        adb + ["shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0",
               "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"],
        adb + ["shell", "cmd", "shortcut", "clear-default-launcher", "--user", "0"],
        adb + ["shell", "input", "keyevent", "3"],
        adb + ["shell", "cmd", "package", "set-home-activity", "--user", "0", FIRE],
    ]
    if args.dry_run:
        print(json.dumps({
            "test_id": args.test_id,
            "output": str(output),
            "mutations": [
                "cmd shortcut clear-default-launcher --user 0",
                "input keyevent 3",
                "conditional restore: cmd package set-home-activity --user 0 " + FIRE,
            ],
            "planned_commands": [shlex.join(argv) for argv in planned],
        }, indent=2))
        return 0

    output.mkdir(parents=True)
    (output / "commands.txt").write_text("", encoding="utf-8")
    metadata = {
        "test_id": args.test_id,
        "serial": args.serial,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "ShortcutService cached default-launcher state only",
        "fire_launcher_mutated": False,
        "fire_launcher_data_cleared": False,
        "settings_provider_written": False,
        "overlay_changed": False,
        "unknown_binder_transaction": False,
        "reboot": False,
        "conditional_restore": False,
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    state = run(adb + ["get-state"])
    save_run(output, "device_state", adb + ["get-state"], state)
    if state.returncode != 0 or state.stdout.strip() != "device":
        raise SystemExit("target is not online in adb device state")
    save_run(output, "device_id", adb + ["shell", "id"], run(adb + ["shell", "id"]))
    save_run(output, "fingerprint", adb + ["shell", "getprop", "ro.build.fingerprint"],
             run(adb + ["shell", "getprop", "ro.build.fingerprint"]))

    capture_state(output, "before", adb)

    clear_argv = adb + ["shell", "cmd", "shortcut", "clear-default-launcher", "--user", "0"]
    save_run(output, "mutation_clear_cache", clear_argv, run(clear_argv))
    capture_state(output, "after_clear", adb)

    home_argv = adb + ["shell", "input", "keyevent", "3"]
    save_run(output, "home_key", home_argv, run(home_argv))
    time.sleep(1.0)
    capture_state(output, "after_home", adb)

    after_home_cache = read_stdout(output, "after_home_shortcut_default").strip()
    after_home_resolve = read_stdout(output, "after_home_home_resolve").strip()
    need_restore = not contains_fire_launcher(after_home_cache) or not contains_fire_launcher(after_home_resolve)
    if need_restore:
        restore_argv = adb + ["shell", "cmd", "package", "set-home-activity", "--user", "0", FIRE]
        save_run(output, "conditional_restore", restore_argv, run(restore_argv))
        metadata["conditional_restore"] = True
        capture_state(output, "after_restore", adb)

    metadata["observed"] = {
        "before_cached_launcher": read_stdout(output, "before_shortcut_default").strip(),
        "after_clear_cached_launcher": read_stdout(output, "after_clear_shortcut_default").strip(),
        "after_home_cached_launcher": after_home_cache,
        "before_resolver": read_stdout(output, "before_home_resolve").strip(),
        "after_clear_resolver": read_stdout(output, "after_clear_home_resolve").strip(),
        "after_home_resolver": after_home_resolve,
        "conditional_restore": metadata["conditional_restore"],
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(metadata["observed"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
