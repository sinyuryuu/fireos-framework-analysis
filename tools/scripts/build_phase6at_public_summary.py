#!/usr/bin/env python3
"""Build a bounded, serial-redacted public summary of a Phase 6AT run.

The source directory is a local ADB capture.  This exporter never contacts a
device, never changes device state, and never copies the raw capture tree into
the public artifact.  It refuses to overwrite an existing output directory.
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
EVENT_RE = re.compile(
    r"am_(?:new_intent|pause_activity|set_resumed_activity|resume_activity|"
    r"stop_activity|activity_launch_time)|"
    r"com\.amazon\.firelauncher/\.Launcher|"
    r"org\.fireosresearch\.phase4\.alias/\.(?:HomeActivity|DirectBootHomeActivity)"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def redact(text: str) -> str:
    return SERIAL_RE.sub("<DEVICE_SERIAL>", text)


def read_required(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing evidence input: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact(content), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="local Phase 6AT capture directory")
    parser.add_argument("--output", required=True, help="new public artifact directory")
    parser.add_argument("--platform", default="PS7331.4463N")
    parser.add_argument("--target", default="org.fireosresearch.phase4.alias/.HomeActivity")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = (ROOT / args.source).resolve()
    output = (ROOT / args.output).resolve()
    if output in (ROOT, Path("/")) or output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    required = {
        "result": source / "result.json",
        "summary": source / "summary.tsv",
        "resolver_before": source / "resolve_before.stdout.txt",
        "resolver_after": source / "resolve_after.stdout.txt",
        "logcat": source / "logcat_after.stdout.txt",
        "metadata": source / "metadata.json",
    }
    contents = {name: read_required(path) for name, path in required.items()}
    result = json.loads(contents["result"])
    rows = list(csv.DictReader(contents["summary"].splitlines(), delimiter="\t"))
    if not rows:
        raise SystemExit("measurement summary has no rows")

    redirect_count = sum(row.get("redirect_sent", "").lower() == "true" for row in rows)
    target_count = sum(row.get("target_observed", "").lower() == "true" for row in rows)
    fire_event_count = sum(row.get("fire_event_seen", "").lower() == "true" for row in rows)
    resolver_before = contents["resolver_before"].strip()
    resolver_after = contents["resolver_after"].strip()
    raw_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in required.values()}

    if args.dry_run:
        print(f"would create {output}")
        print(
            f"iterations={len(rows)} fire_events={fire_event_count} "
            f"redirects={redirect_count} targets={target_count}"
        )
        print(f"resolver_before={resolver_before!r}")
        print(f"resolver_after={resolver_after!r}")
        return 0

    output.mkdir(parents=True)
    write_text(output / "result.json", json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    write_text(output / "summary.tsv", contents["summary"])
    write_text(output / "resolver-before.txt", resolver_before + "\n")
    write_text(output / "resolver-after.txt", resolver_after + "\n")

    relevant = [line for line in contents["logcat"].splitlines() if EVENT_RE.search(line)]
    write_text(output / "logcat-relevant.txt", "\n".join(relevant[:800]) + ("\n" if relevant else ""))

    metadata = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": result.get("test_id") or json.loads(contents["metadata"]).get("test_id"),
        "platform": args.platform,
        "target": args.target,
        "scope": "bounded ADB-connected foreground redirect measurement",
        "iterations": len(rows),
        "fire_foreground_events_observed": fire_event_count,
        "redirects_sent": redirect_count,
        "targets_observed": target_count,
        "resolver_before": resolver_before,
        "resolver_after": resolver_after,
        "classification": "temporary ADB foreground workaround; not a HOME replacement",
        "home_replacement": False,
        "reboot_performed": False,
        "fire_launcher_mutated": False,
        "settings_provider_written": False,
        "package_state_mutation": False,
        "unknown_binder_called": False,
        "raw_capture_published": False,
        "prior_accessibility_state": "unchanged by this monitor; prior manual rollback remains separate",
    }
    write_text(output / "metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    write_text(output / "raw-input-sha256.json", json.dumps(raw_hashes, indent=2, ensure_ascii=False) + "\n")
    write_text(
        output / "reproduction.md",
        f"""# Reproduction boundary

The raw capture remains local under `{args.source}`.  This public artifact was
generated offline and contains only bounded, serial-redacted evidence.

```sh
python3 tools/scripts/run_adb_home_monitor.py \\
  --serial DEVICE_SERIAL \\
  --target {args.target} \\
  --iterations {len(rows)} \\
  --wait-after-home 2.0 \\
  --test-id PHASE6AT-ADB-HOME-MONITOR-PS7331-T02 \\
  --output adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02
```

The monitor uses `input keyevent 3`, observes ActivityManager log events, and
uses `am start -W -n` for the explicitly supplied research Activity.  It does
not disable, hide, suspend, uninstall, force-stop, or clear Fire Launcher; it
does not write Settings, reboot, call unknown Binder transactions, or write a
partition.

Verify the public artifact:

```sh
(cd "$(dirname this-file)" && shasum -a 256 -c sha256sums.txt)
```

This route requires an active ADB connection and is therefore temporary.  The
formal HOME resolver remains the Fire Launcher before and after the run.
""",
    )

    manifest_paths = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = "\n".join(f"{sha256(path)}  {path.relative_to(output)}" for path in manifest_paths) + "\n"
    (output / "sha256sums.txt").write_text(manifest, encoding="utf-8", newline="\n")
    print(f"created {output}; redirects={redirect_count}/{len(rows)}; targets={target_count}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
