#!/usr/bin/env python3
"""One-shot observation of an already user-enabled Accessibility redirect.

This probe never changes Settings, package state, permissions, or Fire
Launcher. It only opens Settings, sends one HOME key event, captures state,
and explicitly starts Fire Launcher at the end as a foreground guard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIRE = "com.amazon.firelauncher/.Launcher"
REDIRECT = "org.fireosresearch.phase4.redirect"


def run(adb: list[str], *args: str, timeout: float = 60.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run([*adb, *args], text=True, capture_output=True, timeout=timeout, check=False)


def capture(adb: list[str], out: Path, name: str, *args: str) -> str:
    result = run(adb, *args)
    (out / f"{name}.command.txt").write_text(" ".join([*adb, *args]) + "\n", encoding="utf-8")
    (out / f"{name}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (out / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    (out / f"{name}.exit_code.txt").write_text(f"{result.returncode}\n", encoding="utf-8")
    return result.stdout


def foreground(activity: str) -> str:
    for line in activity.splitlines():
        if "mResumedActivity" in line or "mFocusedApp" in line or "topResumedActivity" in line:
            return line.strip()
    return "UNPARSED"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    out = (ROOT / args.output).resolve()
    if out in {ROOT, Path("/")} or out.exists():
        raise SystemExit(f"refusing to overwrite output: {out}")
    out.mkdir(parents=True)
    adb = ["adb", "-s", args.serial]
    metadata = {
        "test_id": "PHASE11-ACCESSIBILITY-LIVE-T01",
        "serial": args.serial,
        "scope": "one-shot observation of an already manually enabled service",
        "read_only_settings": True,
        "package_state_mutation": False,
        "fire_launcher_mutation": False,
        "binder_transaction": False,
        "driver_io": False,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    state = run(adb, "get-state")
    (out / "adb_get_state.stdout.txt").write_text(state.stdout, encoding="utf-8")
    (out / "adb_get_state.stderr.txt").write_text(state.stderr, encoding="utf-8")
    if state.returncode != 0 or state.stdout.strip() != "device":
        raise SystemExit("serial is not in device state")

    commands = {
        "before_resolver": ("shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"),
        "before_accessibility": ("shell", "dumpsys", "accessibility"),
        "before_accessibility_setting": ("shell", "settings", "get", "secure", "enabled_accessibility_services"),
        "before_accessibility_enabled": ("shell", "settings", "get", "secure", "accessibility_enabled"),
        "before_redirect_package": ("shell", "dumpsys", "package", REDIRECT),
        "before_fire_package": ("shell", "dumpsys", "package", "com.amazon.firelauncher"),
        "before_activity": ("shell", "dumpsys", "activity", "activities"),
    }
    before = {name: capture(adb, out, name, *command) for name, command in commands.items()}
    capture(adb, out, "logcat_clear", "shell", "logcat", "-c")
    capture(adb, out, "open_settings", "shell", "am", "start", "-a", "android.settings.SETTINGS")
    time.sleep(0.75)
    rebind_polls = []
    service_bound_before_home = False
    for index in range(1, 17):
        accessibility = capture(adb, out, f"rebind_poll_{index:02d}", "shell", "dumpsys", "accessibility")
        present = "Phase 4 redirect control" in accessibility
        rebind_polls.append({"poll": index, "service_present": present})
        if present:
            service_bound_before_home = True
            break
        time.sleep(0.5)
    capture(adb, out, "home_key", "shell", "input", "keyevent", "3")
    time.sleep(1.5)
    after_activity = capture(adb, out, "after_activity", "shell", "dumpsys", "activity", "activities")
    after_window = capture(adb, out, "after_window", "shell", "dumpsys", "window", "windows")
    after_accessibility = capture(adb, out, "after_accessibility", "shell", "dumpsys", "accessibility")
    after_logcat = capture(adb, out, "after_logcat", "shell", "logcat", "-d", "-b", "all", "-v", "threadtime")
    after_resolver = capture(adb, out, "after_resolver", "shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME")

    # Foreground guard only; no package/settings mutation.
    capture(adb, out, "foreground_restore_fire", "shell", "am", "start", "-W", "-n", FIRE, "--user", "0")
    time.sleep(1.0)
    final_activity = capture(adb, out, "final_activity", "shell", "dumpsys", "activity", "activities")
    result = {
        "before_foreground": foreground(before["before_activity"]),
        "after_foreground": foreground(after_activity),
        "final_foreground": foreground(final_activity),
        "formal_home_before": before["before_resolver"].strip(),
        "formal_home_after": after_resolver.strip(),
        "fire_seen_after_home": FIRE in after_activity,
        "redirect_package_seen_after_home": REDIRECT in after_activity,
        "accessibility_service_still_present": REDIRECT in after_accessibility,
        "service_bound_before_home": service_bound_before_home,
        "rebind_polls": rebind_polls,
        "home_callback_log_markers": [marker for marker in ("home-key", "TYPE_WINDOW_STATE_CHANGED", REDIRECT) if marker in after_logcat],
        "classification": "foreground redirect observation only; formal HOME is not changed",
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    files = sorted(path for path in out.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (out / "sha256sums.txt").write_text("".join(f"{digest(path)}  {path.relative_to(out)}\n" for path in files), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
