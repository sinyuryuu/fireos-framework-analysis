#!/usr/bin/env python3
"""Build a privacy-reduced, reproducible public summary of a Phase 6AZ capture.

The full explicit-serial capture remains local. This script publishes only
launcher, resolver, security, service-visibility, build and relevant-setting
evidence; it does not modify the device or the input capture.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "adb/phase6az/PHASE6AZ-RO-20260805-02"
DEFAULT_OUTPUT = ROOT / "artifacts/phase6az/public-summary-20260805-01"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text(input_dir: Path, name: str) -> str:
    path = input_dir / name
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def select_lines(value: str, patterns: list[str]) -> str:
    regex = re.compile("|".join(patterns), re.I)
    return "".join(line for line in value.splitlines(keepends=True) if regex.search(line))


def setting_presence(value: str) -> str:
    terms = re.compile(r"home|launcher|default|resolver|preferred|role|kiosk|desktop|fire|amazon", re.I)
    rows: list[str] = []
    for line in value.splitlines():
        if "=" not in line:
            continue
        key = line.split("=", 1)[0]
        if terms.search(key):
            rows.append(f"{key}=PRESENT\n")
    return "".join(sorted(set(rows)))


def write_new(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    path.write_text(value, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    input_dir = args.input if args.input.is_absolute() else ROOT / args.input
    output_dir = args.output if args.output.is_absolute() else ROOT / args.output
    required = [
        "getprop.stdout.txt", "security_state.stdout.txt", "home_resolve.stdout.txt",
        "home_candidates.stdout.txt", "firelauncher_package.stdout.txt",
        "preferred_activities.stdout.txt", "activity_activities.stdout.txt",
        "services.stdout.txt", "settings_system.stdout.txt",
        "settings_secure.stdout.txt", "settings_global.stdout.txt",
    ]
    if args.dry_run:
        print({"host_only": True, "device_mutation": False, "input": str(input_dir), "output": str(output_dir)})
        return 0
    if not input_dir.is_dir():
        raise SystemExit(f"missing input directory: {input_dir}")
    if output_dir.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output_dir}")
    missing = [name for name in required if not (input_dir / name).is_file()]
    if missing:
        raise SystemExit("missing capture files: " + ", ".join(missing))
    output_dir.mkdir(parents=True)

    getprop = text(input_dir, "getprop.stdout.txt")
    package = text(input_dir, "firelauncher_package.stdout.txt")
    preferred = text(input_dir, "preferred_activities.stdout.txt")
    activities = text(input_dir, "activity_activities.stdout.txt")
    services = text(input_dir, "services.stdout.txt")

    write_new(output_dir / "build-properties.txt", select_lines(getprop, [
        r"^\[(ro\.product\.model|ro\.product\.device|ro\.build\.fingerprint|"
        r"ro\.build\.version\.incremental|ro\.build\.version\.security_patch|"
        r"ro\.build\.version\.release|ro\.build\.version\.sdk|ro\.build\.type|"
        r"ro\.debuggable|ro\.boot\.verifiedbootstate)\]:",
    ]))
    write_new(output_dir / "security-state.txt", text(input_dir, "security_state.stdout.txt"))
    write_new(output_dir / "home-resolver.txt", text(input_dir, "home_resolve.stdout.txt") + text(input_dir, "home_candidates.stdout.txt"))
    write_new(output_dir / "firelauncher-package-summary.txt", select_lines(package, [
        r"Package \[com\.amazon\.firelauncher\]", r"^\s+(userId|codePath|resourcePath|"
        r"legacyNativeLibraryDir|versionCode|versionName|flags|privateFlags|pkgFlags|"
        r"signatures|path:|User 0:)",
    ]))
    write_new(output_dir / "preferred-summary.txt", select_lines(preferred, [
        r"Preferred Activities", r"Persistent Preferred", r"mAlways", r"com\.amazon\.firelauncher",
        r"com\.microsoft\.launcher", r"org\.fireosresearch",
    ]))
    write_new(output_dir / "activity-summary.txt", select_lines(activities, [
        r"mResumedActivity", r"mCurrentFocus", r"realActivity=", r"Intent .*HOME",
        r"baseDir=", r"launchedFromPackage=",
    ]))
    write_new(output_dir / "service-visibility-summary.txt", select_lines(services, [
        r"amazonpackagemanager", r"amazonusermanagerservice", r"amazonactivitymanager",
        r"amazonwindowmanager", r"amazon_input", r"fosdebug", r"otadexopt",
    ]))
    write_new(output_dir / "settings-key-presence.txt", "[system]\n" + setting_presence(text(input_dir, "settings_system.stdout.txt"))
             + "[secure]\n" + setting_presence(text(input_dir, "settings_secure.stdout.txt"))
             + "[global]\n" + setting_presence(text(input_dir, "settings_global.stdout.txt")))
    tb_value = text(input_dir, "tb_custom_launcher_value.stdout.txt").strip()
    tesla_state = text(input_dir, "teslacoilsw_package.stdout.txt")
    accessibility = text(input_dir, "enabled_accessibility_services_value.stdout.txt").strip()
    write_new(output_dir / "control-state-summary.txt", "".join([
        "tb_custom_launcher=" + (tb_value if tb_value else "NOT_PRESENT") + "\n",
        "com.teslacoilsw.launcher=" + ("NOT_INSTALLED\n" if "Unable to find package" in tesla_state else "PRESENT\n"),
        "enabled_accessibility_services=" + ("PRESENT_REDACTED\n" if accessibility else "NOT_PRESENT\n"),
    ]))
    write_new(output_dir / "capture-limitations.md", """# Phase 6AZ public-summary redaction

This directory is derived from the explicit-serial read-only capture. Full
raw dumps remain local under `adb/phase6az/PHASE6AZ-RO-20260805-02/` and are not
published here because they may contain user-specific settings, identifiers,
or unrelated application details. The summary retains the build identity,
HOME resolver/candidate evidence, Fire Launcher package state, relevant active
activity lines, private service visibility, security state, and only the
presence (not values) of matching settings keys.

The small `control-state-summary.txt` records only the explicitly queried
launcher-control key and whether the corresponding package was installed; it
contains no user data.

No device mutation, Binder transaction, broadcast, install, reboot, or
partition operation was performed by the summary builder.
""")

    input_manifest = input_dir / "sha256sums.txt"
    write_new(output_dir / "input-capture-sha256.txt", digest(input_manifest) + "  source-capture-sha256sums.txt\n")
    files = sorted(path for path in output_dir.iterdir() if path.is_file())
    write_new(output_dir / "sha256sums.txt", "".join(f"{digest(path)}  {path.name}\n" for path in files))
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
