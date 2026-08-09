#!/usr/bin/env python3
"""Run the Phase 6MX handle-only probe with a reversible test-package scope.

The APK only calls ServiceManager.getService() through reflection.  This
runner never calls `service call`, Binder transact, an ioctl, a private API
method, or a Fire Launcher/package-state mutation.  It installs and removes
only the explicitly supplied test APK on User 0, with before/after evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "org.fireosresearch.phase6mx.lookup"
ACTIVITY = f"{PACKAGE}/.ServiceHandleLookupActivity"
TAG = "Phase6MX"


def run(argv: list[str], timeout: int = 45) -> dict[str, object]:
    started = time.monotonic()
    try:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "argv": argv,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "timeout",
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }


def adb(serial: str, *args: str) -> dict[str, object]:
    return run(["adb", "-s", serial, *args])


def shell(serial: str, *args: str) -> dict[str, object]:
    return adb(serial, "shell", *args)


def out(result: dict[str, object]) -> str:
    value = result.get("stdout", "")
    return value if isinstance(value, str) else str(value)


def write_result(directory: Path, name: str, result: dict[str, object]) -> None:
    (directory / f"{name}.stdout.txt").write_text(out(result), encoding="utf-8")
    (directory / f"{name}.stderr.txt").write_text(str(result.get("stderr", "")), encoding="utf-8")


def capture(serial: str, directory: Path, prefix: str) -> dict[str, dict[str, object]]:
    commands = {
        "adb_devices": ("devices", "-l"),
        "id": ("shell", "id"),
        "getenforce": ("shell", "getenforce"),
        "fingerprint": ("shell", "getprop", "ro.build.fingerprint"),
        "current_user": ("shell", "am", "get-current-user"),
        "home_resolve": (
            "shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME",
        ),
        "fire_package": ("shell", "dumpsys", "package", "com.amazon.firelauncher"),
        "test_path": ("shell", "pm", "path", PACKAGE),
        "test_package": ("shell", "dumpsys", "package", PACKAGE),
        "service_list": ("shell", "service", "list"),
        "activity_top": ("shell", "dumpsys", "activity", "top"),
    }
    results: dict[str, dict[str, object]] = {}
    for name, args in commands.items():
        result = adb(serial, *args)
        results[name] = result
        write_result(directory, f"{prefix}-{name}", result)
    return results


def verify_device(serial: str) -> None:
    result = run(["adb", "devices", "-l"])
    if result.get("returncode") != 0:
        raise SystemExit("adb devices failed")
    rows = [line.split() for line in out(result).splitlines()[1:] if line.strip()]
    matches = [row for row in rows if row and row[0] == serial]
    if len(matches) != 1 or len(matches[0]) < 2 or matches[0][1] != "device":
        raise SystemExit(f"serial {serial!r} is not uniquely connected as device")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    apk = args.apk if args.apk.is_absolute() else ROOT / args.apk
    directory = args.output if args.output.is_absolute() else ROOT / args.output
    if not apk.is_file():
        raise SystemExit(f"APK not found: {apk}")
    if directory.exists():
        raise SystemExit(f"refusing to overwrite existing output: {directory}")
    if args.dry_run:
        print(json.dumps({
            "serial": args.serial,
            "apk": str(apk),
            "output": str(directory),
            "device_contacted": False,
            "binder_transactions": False,
            "private_api_calls": False,
            "fire_launcher_mutation": False,
            "test_package_install_remove_only": True,
        }, indent=2, sort_keys=True))
        return 0

    verify_device(args.serial)
    directory.mkdir(parents=True)
    metadata = {
        "phase": "6MX",
        "serial": args.serial,
        "package": PACKAGE,
        "activity": ACTIVITY,
        "apk": str(apk),
        "apk_sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
        "declared_permissions": [],
        "home_intent_declared": False,
        "service_manager_get_service_only": True,
        "binder_transactions_sent": False,
        "private_api_methods_called": False,
        "fire_launcher_state_mutated": False,
        "reboot": False,
    }
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    before = capture(args.serial, directory, "before")
    install = adb(args.serial, "install", "--user", "0", str(apk))
    write_result(directory, "install", install)
    if install.get("returncode") != 0 or "Success" not in out(install):
        raise SystemExit(f"test APK install failed; evidence retained at {directory}")
    start = shell(args.serial, "am", "start", "-W", "-n", ACTIVITY)
    write_result(directory, "start", start)
    time.sleep(1)
    logcat = shell(args.serial, "logcat", "-d", "-v", "threadtime", "-s", f"{TAG}:*")
    write_result(directory, "probe-logcat", logcat)
    after_start = capture(args.serial, directory, "after-start")
    stop = shell(args.serial, "am", "force-stop", PACKAGE)
    write_result(directory, "test-force-stop", stop)
    uninstall = shell(args.serial, "pm", "uninstall", "--user", "0", PACKAGE)
    write_result(directory, "uninstall", uninstall)
    after = capture(args.serial, directory, "after-rollback")

    log_text = out(logcat)
    handle_lines = [line for line in log_text.splitlines() if "service=" in line and " handle=" in line]
    result = {
        "install_succeeded": install.get("returncode") == 0 and "Success" in out(install),
        "start_returncode": start.get("returncode"),
        "handle_lines": handle_lines,
        "service_handle_true_lines": [line for line in handle_lines if "handle=true" in line],
        "service_handle_false_lines": [line for line in handle_lines if "handle=false" in line],
        "uninstall_succeeded": uninstall.get("returncode") == 0 and "Success" in out(uninstall),
        "test_absent_after_rollback": out(after["test_path"]).strip() == "",
        "home_before": out(before["home_resolve"]).strip(),
        "home_after": out(after["home_resolve"]).strip(),
        "home_unchanged": out(before["home_resolve"]).strip() == out(after["home_resolve"]).strip(),
        "fire_package_before_sha256": hashlib.sha256(out(before["fire_package"]).encode()).hexdigest(),
        "fire_package_after_sha256": hashlib.sha256(out(after["fire_package"]).encode()).hexdigest(),
        "fire_package_state_observed_only": True,
        "classification": "handle lookup only; no Binder transaction or HOME/package-state effect tested",
    }
    (directory / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checks = []
    for path in sorted(directory.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        checks.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (directory / "sha256sums.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(directory), "result": result}, indent=2, sort_keys=True))
    return 0 if result["uninstall_succeeded"] and result["test_absent_after_rollback"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
