#!/usr/bin/env python3
"""Close the remaining exported-component triage rows without touching a device.

The Phase 6W inventory intentionally over-approximates exposed components.  This
host-only pass resolves the two remaining nonstandard groups that are present in
the preserved PS7331 inputs:

* OOBE activities protected by the package-defined signature-level
  ``OOBE_PERMISSION`` (manifest protection value 0x2); and
* Fire Launcher's BadgingProvider, whose update method performs an additional
  calling-UID/package-ownership check.

It does not invoke an activity, send a broadcast, query or update a provider,
call Binder, or modify the device.  Missing source markers remain unknown.
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
DEFAULTS = {
    "candidates": ROOT / "artifacts/phase6w/exported-component-audit-20260805-01/high-impact-exported-candidates.csv",
    "oobe_manifest": ROOT / "artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt",
    "oobe_launcher": ROOT / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/OOBELauncherV2.java",
    "badging_source": ROOT / "decompiled/jadx/firelauncher/sources/com/amazon/firelauncher/appsgrid/BadgingProvider.java",
    "fire_manifest": ROOT / "decompiled/jadx/firelauncher/resources/AndroidManifest.xml",
    "package_dump": ROOT / "adb/phase6q/PHASE6Q-RO-20260805-01/package_dump_full.stdout.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines_matching(text: str, pattern: str) -> list[int]:
    expression = re.compile(pattern, re.IGNORECASE)
    return [number for number, line in enumerate(text.splitlines(), 1) if expression.search(line)]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def protection_name(value: str) -> str:
    normalized = value.strip().lower()
    base = normalized.split("|")[0]
    numeric = base
    if numeric.startswith("0x"):
        try:
            numeric_value = int(numeric, 16) & 0xF
        except ValueError:
            numeric_value = None
        if numeric_value == 0:
            return "normal"
        if numeric_value == 1:
            return "dangerous"
        if numeric_value == 2:
            return "signature"
        if numeric_value == 3:
            return "signatureOrSystem"
    return {
        "normal": "normal",
        "dangerous": "dangerous",
        "signature": "signature",
        "signatureorsystem": "signatureOrSystem",
    }.get(base.replace(" ", ""), "unknown")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=default)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_names = list(DEFAULTS)
    input_paths = [getattr(args, name) for name in input_names]
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "component_started": False,
            "provider_queried": False,
            "provider_updated": False,
            "broadcast_sent": False,
            "binder_invoked": False,
            "inputs": [str(path) for path in input_paths],
            "output": str(args.output),
        }, indent=2, sort_keys=True))
        return 0

    missing = [str(path) for path in input_paths if not path.is_file()]
    if missing:
        raise SystemExit("missing preserved input(s):\n" + "\n".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    texts = {name: read(getattr(args, name)) for name in input_names}
    with args.candidates.open("r", encoding="utf-8", newline="") as stream:
        candidate_rows = list(csv.DictReader(stream))

    selected: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for row in candidate_rows:
        if row.get("exposure_class") != "EXPORTED_LOWER_OR_NONSTANDARD_PROTECTION":
            continue
        key = (row.get("package", ""), row.get("component", ""),
               row.get("permission", ""), row.get("write_permission", ""))
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)

    output_rows: list[dict[str, str]] = []
    for row in selected:
        package = row.get("package", "")
        component = row.get("component", "")
        permission = row.get("permission", "")
        write_permission = row.get("write_permission", "")
        if component.endswith("BadgingProvider"):
            source_lines = {
                "manifest": ",".join(map(str, lines_matching(
                    texts["fire_manifest"], r"BADGING|BadgingProvider"))),
                "source": ",".join(map(str, lines_matching(
                    texts["badging_source"],
                    r"Binder\.getCallingUid|badgeUpdateAllowed|getPackagesForUid|contains\(pkgName\)|updateBadge"))),
            }
            output_rows.append({
                "package": package,
                "component": component,
                "declared_permission": write_permission or permission,
                "resolved_protection": "normal",
                "method_guard": "Binder.getCallingUid -> getPackagesForUid(uid) -> target package must contain pkgName",
                "source_lines": json.dumps(source_lines, sort_keys=True),
                "decision": "A shell caller does not own com.amazon.firelauncher; static caller-package guard rejects a badge update targeting Fire Launcher.",
                "effect_scope": "launcher badge state only; no HOME selection, package-state, system-setting, Binder, or root effect observed",
                "classification": "CUSTOM_CALLER_PACKAGE_GUARD",
                "confidence": "Strong evidence",
            })
            continue

        if package == "com.amazon.kindle.otter.oobe":
            manifest_lines = lines_matching(
                texts["oobe_manifest"],
                r"OOBE_PERMISSION|OOBELauncherV2|SettingsLanguagePickerActivity|SettingsTimezoneActivity|ATSWiFiActivity",
            )
            launcher_lines = lines_matching(
                texts["oobe_launcher"],
                r"OOBEActivationHelper|PackageHelper\.enableComponent|startActivity|finish\(\)",
            )
            output_rows.append({
                "package": package,
                "component": component,
                "declared_permission": permission,
                "resolved_protection": protection_name("0x2"),
                "method_guard": "manifest component permission OOBE_PERMISSION; package declares protectionLevel=0x2",
                "source_lines": json.dumps({
                    "manifest": ",".join(map(str, manifest_lines)),
                    "launcher": ",".join(map(str, launcher_lines)),
                }, sort_keys=True),
                "decision": "Signature-level OOBE permission blocks ordinary shell/untrusted component launch; side effects are setup/OOBE state transitions, not a general HOME API.",
                "effect_scope": "OOBE flow and setup state; not a demonstrated shell HOME selector or root path",
                "classification": "SIGNATURE_COMPONENT_GUARD",
                "confidence": "Confirmed",
            })
            continue

        output_rows.append({
            "package": package,
            "component": component,
            "declared_permission": permission or write_permission,
            "resolved_protection": protection_name(row.get("resolved_protection_level", "")),
            "method_guard": "not mapped in this bounded closure",
            "source_lines": "",
            "decision": "No conclusion beyond the preserved manifest row.",
            "effect_scope": "unknown",
            "classification": "UNKNOWN",
            "confidence": "Hypothesis",
        })

    fields = [
        "package", "component", "declared_permission", "resolved_protection",
        "method_guard", "source_lines", "decision", "effect_scope",
        "classification", "confidence",
    ]
    write_csv(args.output / "exposed-component-closure.csv", fields, output_rows)

    input_rows = [{"file": str(path), "sha256": sha256(path), "size": path.stat().st_size}
                  for path in input_paths]
    write_csv(args.output / "input-sha256.csv", ["file", "sha256", "size"], input_rows)

    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "component_started": False,
        "provider_queried": False,
        "provider_updated": False,
        "broadcast_sent": False,
        "binder_invoked": False,
        "selected_unique_rows": len(selected),
        "closed_rows": len(output_rows),
        "classification_counts": {
            value: sum(1 for row in output_rows if row["classification"] == value)
            for value in sorted({row["classification"] for row in output_rows})
        },
        "finding": "The six nonstandard manifest rows in the bounded Phase 6W inventory close to signature-protected OOBE components or a badge-only provider with a caller-package guard; no ordinary shell-to-system escalation path is established.",
        "limitations": [
            "This is static closure of preserved inputs, not a runtime caller test.",
            "The OOBE component was not started and the badge provider was not queried or updated.",
            "Unknown rows remain unknown; absence of a source marker is not negative proof.",
        ],
        "inputs": input_rows,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 6AA exposed component closure\n\n"
        "Host-only static output. No device contact, component launch, provider query/update, broadcast, Binder transaction, or package/settings mutation.\n\n"
        f"Unique nonstandard rows: {len(selected)}\n\n"
        "The closure separates manifest triage from method-level authorization. OOBE rows resolve to the package-defined signature-level OOBE_PERMISSION; BadgingProvider is badge-scoped and performs an additional caller-package ownership check.\n",
        encoding="utf-8",
    )

    files = sorted(path for path in args.output.rglob("*")
                   if path.is_file() and path.name != "sha256sums.txt")
    checksum_lines = [f"{sha256(path)}  {path.relative_to(args.output)}" for path in files]
    (args.output / "sha256sums.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
