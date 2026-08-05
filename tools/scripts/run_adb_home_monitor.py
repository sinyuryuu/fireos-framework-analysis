#!/usr/bin/env python3
"""Measure a reversible, host-side ADB HOME foreground monitor.

This is deliberately not a launcher replacement.  It watches ActivityManager
events while an ADB connection remains open and starts an explicitly supplied
research activity after Fire Launcher becomes resumed.  It never disables,
hides, suspends, uninstalls, or clears Fire Launcher and never writes Settings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIRE_COMPONENT = "com.amazon.firelauncher/.Launcher"
RESUMED_RE = re.compile(r"am_set_resumed_activity: .*?(?P<component>[^,\]]+)")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(adb: list[str], *args: str, timeout: float = 15.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run([*adb, *args], text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=timeout, check=False)


def write_run(output: Path, name: str, result: subprocess.CompletedProcess[str]) -> None:
    (output / f"{name}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (output / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    (output / f"{name}.exit_code.txt").write_text(str(result.returncode) + "\n", encoding="utf-8")


def foreground_line(dump: str) -> str:
    for line in dump.splitlines():
        if "mResumedActivity" in line or "mFocusedApp" in line:
            return line.strip()
    return "UNPARSED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--target", default="org.fireosresearch.phase4.alias/.HomeActivity")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--wait-after-home", type=float, default=2.0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--test-id", default="PHASE6AT-ADB-HOME-MONITOR-T01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.iterations < 1 or args.iterations > 100:
        raise SystemExit("--iterations must be between 1 and 100")
    if args.wait_after_home <= 0 or args.wait_after_home > 15:
        raise SystemExit("--wait-after-home must be between 0 and 15 seconds")
    if "com.amazon.firelauncher" in args.target:
        raise SystemExit("refusing a Fire Launcher target")
    output = (ROOT / args.output).resolve()
    if output in (ROOT, Path("/")) or output.exists():
        raise SystemExit(f"refusing to overwrite output: {output}")
    adb = ["adb", "-s", args.serial]
    planned = [
        "adb -s SERIAL get-state",
        "adb -s SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0",
        "adb -s SERIAL shell dumpsys activity activities",
        "adb -s SERIAL shell logcat -d -b all -v threadtime",
        "adb -s SERIAL shell logcat -c",
        "adb -s SERIAL shell am start -W -n TARGET",
        "adb -s SERIAL shell input keyevent 3",
        "adb -s SERIAL shell dumpsys activity activities",
        "adb -s SERIAL shell logcat -d -b all -v threadtime",
        "adb -s SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0",
    ]
    if args.dry_run:
        print(f"would create {output}")
        print("planned read-only/foreground commands:")
        for command in planned:
            print(f"  {command}")
        return 0

    output.mkdir(parents=True)
    (output / "commands.txt").write_text("\n".join(planned) + "\n", encoding="utf-8")
    metadata = {
        "test_id": args.test_id,
        "serial": args.serial,
        "target": args.target,
        "iterations": args.iterations,
        "scope": "host-side ADB foreground monitor; not HOME replacement",
        "fire_launcher_mutated": False,
        "settings_written": False,
        "package_state_mutation": False,
        "unknown_binder": False,
        "reboot": False,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    state = run(adb, "get-state")
    write_run(output, "device_state", state)
    if state.returncode != 0 or state.stdout.strip() != "device":
        raise SystemExit("target is not in adb device state")
    before_resolve = run(adb, "shell", "cmd", "package", "resolve-activity", "--brief",
                         "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME", "--user", "0")
    write_run(output, "resolve_before", before_resolve)
    before_activity = run(adb, "shell", "dumpsys", "activity", "activities")
    write_run(output, "activity_before", before_activity)
    before_log = run(adb, "shell", "logcat", "-d", "-b", "all", "-v", "threadtime", timeout=30)
    write_run(output, "logcat_before", before_log)
    cleared = run(adb, "shell", "logcat", "-c")
    write_run(output, "logcat_clear", cleared)

    stream = subprocess.Popen([*adb, "shell", "logcat", "-b", "all", "-v", "threadtime"],
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              bufsize=1)
    events: deque[str] = deque(maxlen=4000)
    stop = threading.Event()

    def read_stream() -> None:
        assert stream.stdout is not None
        for line in stream.stdout:
            if stop.is_set():
                break
            if "am_set_resumed_activity" in line or FIRE_COMPONENT in line or args.target in line:
                events.append(line.rstrip("\n"))

    reader = threading.Thread(target=read_stream, daemon=True)
    reader.start()
    rows: list[dict[str, object]] = []
    try:
        for iteration in range(1, args.iterations + 1):
            launch = run(adb, "shell", "am", "start", "-W", "-n", args.target)
            write_run(output, f"iteration_{iteration:02d}_probe", launch)
            time.sleep(0.35)
            start_index = len(events)
            key = run(adb, "shell", "input", "keyevent", "3")
            write_run(output, f"iteration_{iteration:02d}_home", key)
            deadline = time.monotonic() + args.wait_after_home
            event_seen = False
            redirect = None
            while time.monotonic() < deadline:
                recent = list(events)[start_index:]
                if any(FIRE_COMPONENT in line for line in recent):
                    event_seen = True
                    redirect = run(adb, "shell", "am", "start", "-W", "-n", args.target)
                    write_run(output, f"iteration_{iteration:02d}_redirect", redirect)
                    break
                time.sleep(0.05)
            dump = run(adb, "shell", "dumpsys", "activity", "activities")
            write_run(output, f"iteration_{iteration:02d}_foreground", dump)
            line = foreground_line(dump.stdout)
            rows.append({
                "iteration": iteration,
                "fire_event_seen": event_seen,
                "redirect_sent": redirect is not None and redirect.returncode == 0,
                "target_observed": args.target in line,
                "foreground": line,
            })
    finally:
        stop.set()
        stream.terminate()
        try:
            stream.wait(timeout=3)
        except subprocess.TimeoutExpired:
            stream.kill()
        reader.join(timeout=3)

    after_log = run(adb, "shell", "logcat", "-d", "-b", "all", "-v", "threadtime", timeout=30)
    write_run(output, "logcat_after", after_log)
    after_resolve = run(adb, "shell", "cmd", "package", "resolve-activity", "--brief",
                        "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME", "--user", "0")
    write_run(output, "resolve_after", after_resolve)
    after_activity = run(adb, "shell", "dumpsys", "activity", "activities")
    write_run(output, "activity_after", after_activity)
    successful_redirects = sum(bool(row["redirect_sent"]) for row in rows)
    observed_targets = sum(bool(row["target_observed"]) for row in rows)
    summary = ["iteration\tfire_event_seen\tredirect_sent\ttarget_observed\tforeground"]
    summary.extend(
        f"{row['iteration']}\t{str(row['fire_event_seen']).lower()}\t"
        f"{str(row['redirect_sent']).lower()}\t{str(row['target_observed']).lower()}\t{row['foreground']}"
        for row in rows
    )
    (output / "summary.tsv").write_text("\n".join(summary) + "\n", encoding="utf-8")
    result = {
        "iterations": args.iterations,
        "redirects_sent": successful_redirects,
        "targets_observed": observed_targets,
        "resolver_before": before_resolve.stdout.strip(),
        "resolver_after": after_resolve.stdout.strip(),
        "classification": "ADB-connected temporary foreground workaround" if observed_targets else "ineffective under this run",
        "home_replacement": False,
        "reboot_persistence": False,
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output / "result.md").write_text(
        f"# {args.test_id}\n\n"
        f"- Iterations: {args.iterations}\n"
        f"- Redirects sent after Fire foreground event: {successful_redirects}/{args.iterations}\n"
        f"- Target observed in final foreground dump: {observed_targets}/{args.iterations}\n"
        "- This is an ADB-connected foreground monitor, not a HOME resolver replacement.\n"
        "- Fire Launcher was not mutated; no Settings/package-state write, reboot, or Binder transaction was used.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = "\n".join(f"{digest(path)}  {path.relative_to(output)}" for path in files) + "\n"
    (output / "sha256sums.txt").write_text(manifest, encoding="utf-8")
    print(f"created {output}; redirects={successful_redirects}/{args.iterations}; targets={observed_targets}/{args.iterations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
