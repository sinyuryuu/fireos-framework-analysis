#!/usr/bin/env python3
"""Build a bounded, serial-redacted public summary of a Phase 5CQ run.

The source directory is local evidence captured by the existing experiment
runner.  This generator never calls ADB, changes device state, or copies the
raw capture tree into the public artifact.  It refuses to overwrite output.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERIAL_RE = re.compile(r"\bG[A-Z0-9]{8,}\b")
LOG_RE = re.compile(
    r"am_(?:set_resumed_activity|resume_activity|new_intent|pause_activity|"
    r"stop_activity|activity_launch_time)|"
    r"Displayed .*?(?:firelauncher|phase4\.alias)|"
    r"(?:com\.amazon\.firelauncher/\.Launcher|"
    r"org\.fireosresearch\.phase4\.(?:alias|redirect))|"
    r"avc:  denied .*service=amazon(?:activitymanager|accessibilitymanager)"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def redact(text: str) -> str:
    return SERIAL_RE.sub("<DEVICE_SERIAL>", text)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact(content), encoding="utf-8", newline="\n")


def read_required(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing evidence input: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def parse_summary(text: str) -> tuple[int, int, str]:
    rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    if not rows:
        raise SystemExit("measurement summary has no rows")
    alias_count = sum(row.get("alias_observed", "").strip().lower() == "yes" for row in rows)
    last_foreground = rows[-1].get("resumed_or_focus", "").strip()
    return len(rows), alias_count, last_foreground


def resolver_component(text: str) -> str:
    candidates = [line.strip() for line in text.splitlines() if "/" in line]
    return candidates[-1] if candidates else "UNPARSED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="local Phase 5CQ evidence directory")
    parser.add_argument("--output", required=True, help="new public artifact directory")
    parser.add_argument("--redirect-apk")
    parser.add_argument("--alias-apk")
    parser.add_argument("--platform", default="PS7331.4463N")
    parser.add_argument("--test-id", default="PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = (ROOT / args.source).resolve()
    output = (ROOT / args.output).resolve()
    if output in (ROOT, Path("/")) or output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    files = {
        "result": source / "measure/result.md",
        "summary": source / "measure/summary.tsv",
        "resolver_before": source / "resolve_before_measure.stdout.txt",
        "resolver_after": source / "resolve_after_measure.stdout.txt",
        "logcat": source / "logcat_after_measure.stdout.txt",
    }
    contents = {name: read_required(path) for name, path in files.items()}
    iterations, alias_count, last_foreground = parse_summary(contents["summary"])
    before = resolver_component(contents["resolver_before"])
    after = resolver_component(contents["resolver_after"])
    raw_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in files.values()}
    apk_hashes: dict[str, str] = {}
    for label, value in (("redirect_apk", args.redirect_apk), ("alias_apk", args.alias_apk)):
        if value:
            path = (ROOT / value).resolve()
            if not path.is_file():
                raise SystemExit(f"missing APK input: {path}")
            apk_hashes[str(path.relative_to(ROOT))] = sha256(path)

    if args.dry_run:
        print(f"would create {output}")
        print(f"iterations={iterations} alias_observed={alias_count}")
        print(f"resolver_before={before} resolver_after={after}")
        return 0

    output.mkdir(parents=True)
    write_text(output / "result.md", contents["result"])
    write_text(output / "summary.tsv", contents["summary"])
    write_text(output / "resolver-before.txt", contents["resolver_before"])
    write_text(output / "resolver-after.txt", contents["resolver_after"])

    relevant = [line for line in contents["logcat"].splitlines() if LOG_RE.search(line)]
    log_text = "\n".join(relevant[:600]) + ("\n" if relevant else "")
    write_text(output / "logcat-relevant.txt", log_text)

    metadata = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": args.test_id,
        "platform": args.platform,
        "scope": "bounded foreground redirect measurement",
        "iterations": iterations,
        "alias_observed": alias_count,
        "alias_observed_rate": f"{alias_count}/{iterations}",
        "resolver_before": before,
        "resolver_after": after,
        "last_foreground_sample": last_foreground,
        "fire_launcher_mutated": False,
        "settings_provider_written": False,
        "unknown_binder_called": False,
        "reboot_performed": False,
        "manual_accessibility_rollback": "pending; service must be disabled in Android Settings before runner rollback",
        "raw_capture_published": False,
    }
    write_text(output / "metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    write_text(output / "raw-input-sha256.json", json.dumps(raw_hashes, indent=2, ensure_ascii=False) + "\n")
    write_text(output / "apk-input-sha256.json", json.dumps(apk_hashes, indent=2, ensure_ascii=False) + "\n")
    write_text(
        output / "reproduction.md",
        """# Reproduction boundary\n\n"
        "The raw capture is retained locally under the source directory passed to\n"
        "`build_phase5cq_public_summary.py`. The public artifact is generated\n"
        "without contacting the device.\n\n"
        "```sh\n"
        "python3 tools/scripts/build_phase5cq_public_summary.py --dry-run \\\n"
        "  --source adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 \\\n"
        "  --output artifacts/phase5cq/public-summary-20260805-01\n"
        "```\n\n"
        "Verify the generated manifest from its artifact directory:\n\n"
        "```sh\n"
        "(cd artifacts/phase5cq/public-summary-20260805-01 && shasum -a 256 -c sha256sums.txt)\n"
        "```\n\n"
        "The Accessibility service was manually enabled for the measurement.\n"
        "Before package rollback, the device owner must manually disable that\n"
        "service and its visible redirect toggle in Android Settings.\n""",
    )
    manifest_paths = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = "\n".join(f"{sha256(path)}  {path.relative_to(output)}" for path in manifest_paths) + "\n"
    (output / "sha256sums.txt").write_text(manifest, encoding="utf-8", newline="\n")
    print(f"created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
