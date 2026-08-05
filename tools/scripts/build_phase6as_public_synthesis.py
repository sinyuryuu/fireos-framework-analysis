#!/usr/bin/env python3
"""Build a bounded, public Phase 6AS synthesis from saved evidence.

This script is deliberately host-only.  It reads only reports and public,
serial-redacted artifacts already present in the repository.  It never calls
ADB, starts an Android component, sends a Binder transaction, or writes a
device.  Output directories are never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]

INPUTS = [
    Path("findings/phase-6aq-service-context-closure.md"),
    Path("findings/phase-6ar-home-callback-and-ota-follow-up.md"),
    Path("findings/phase-6af-otadexopt-implementation-closure.md"),
    Path("findings/phase-6ah-update-binary-validation-write-closure.md"),
    Path("findings/phase-6ap-denylist-resource-closure.md"),
    Path("artifacts/phase6aq/public-summary-20260805-05/service-context-key-rows.csv"),
    Path("artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv"),
    Path("artifacts/phase6aq/public-summary-20260805-05/home-and-build-state.txt"),
    Path("artifacts/phase6aq/public-summary-20260805-05/amazon-service-avc.txt"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def rows() -> list[dict[str, str]]:
    return [
        {
            "surface": "HOME key",
            "observed_path": "KeyPolicyManagerCommon.launchHomeFromHotKey -> implicit MAIN + CATEGORY_HOME -> startActivityAsUser",
            "result": "PackageManager HOME resolution remains the final observed selector",
            "confidence": "Confirmed (bounded method)",
            "evidence": "disassembly.log:3744886-3744901; phase-6aq public summary",
            "safe_scope": "No private Binder call; no device mutation",
        },
        {
            "surface": "Amazon private services",
            "observed_path": "fosinit registrations -> service-manager lookup -> SELinux service_manager find policy",
            "result": "Private service handles are not shell-visible under enforcing policy",
            "confidence": "Confirmed for saved runtime capture",
            "evidence": "phase6aq public-summary-20260805-05; service-context-matrix.csv",
            "safe_scope": "No unknown transaction or callback replay",
        },
        {
            "surface": "Package protection",
            "observed_path": "resource package_manager_deny_list -> deny-list seed -> protected-package callback",
            "result": "The PS7331 resource contains Fire Launcher and feeds the protected-package path",
            "confidence": "Confirmed static provenance",
            "evidence": "findings/phase-6ap-denylist-resource-closure.md",
            "safe_scope": "No deny-list mutation; Fire Launcher was not targeted",
        },
        {
            "surface": "OTA updater",
            "observed_path": "updater evaluator -> block-image/direct block-device write wrappers",
            "result": "Official package has a high-impact write boundary; execution is not justified",
            "confidence": "Confirmed static write intent",
            "evidence": "findings/phase-6ah-update-binary-validation-write-closure.md",
            "safe_scope": "No updater, recovery, OTA, or partition write",
        },
        {
            "surface": "BOOT_AFTER_SYSTEM_OTA / OOBE",
            "observed_path": "guarded post-OTA system-server sender -> protected receiver -> OOBE state/component path",
            "result": "High-risk lifecycle surface, not a normal shell HOME setter",
            "confidence": "Strong evidence; lifecycle invocation not replayed",
            "evidence": "findings/phase-6ar-home-callback-and-ota-follow-up.md",
            "safe_scope": "No broadcast replay, OOBE mutation, or provisioning",
        },
        {
            "surface": "otadexopt",
            "observed_path": "standard shell-visible IOtaDexopt publication -> OtaDexoptService",
            "result": "Adjacent dexopt service; no observed HOME or privilege-transition path",
            "confidence": "Confirmed bounded implementation; caller policy remains scoped",
            "evidence": "findings/phase-6af-otadexopt-implementation-closure.md",
            "safe_scope": "Only prior status queries; mutating commands were not called",
        },
    ]


def markdown(input_hashes: dict[str, str], table_rows: Iterable[dict[str, str]]) -> str:
    lines = [
        "# Phase 6AS — PS7331 public boundary synthesis",
        "",
        "## Scope",
        "",
        "This is a host-only synthesis of saved PS7331 evidence. It is intended",
        "for public publication and uses only the serial-redacted Phase 6AQ",
        "summary plus static reports. No ADB command, Binder transaction,",
        "broadcast, OTA/updater/recovery action, package mutation, reboot, or",
        "partition write is performed by this generator.",
        "",
        "## Current conclusions",
        "",
        "- **已證實：** the observed Home-key implementation constructs an implicit",
        "  `MAIN + CATEGORY_HOME` intent and delegates to the normal activity",
        "  start/resolution path in the bounded method scope.",
        "- **已證實：** saved enforcing-policy runtime evidence blocks shell",
        "  discovery of the selected Amazon private services; service inventory",
        "  alone is not a callable Binder API.",
        "- **已證實：** the PS7331 `amazon.fireos` deny-list resource contains",
        "  `com.amazon.firelauncher` and is connected by the saved consumer",
        "  evidence to PackageManager protected-package enforcement.",
        "- **已證實（靜態）：** the official updater script and AArch64",
        "  `update-binary` contain system/vendor and direct block-device write",
        "  intent. This is not an adopted runtime test path.",
        "- **高可信推論：** the remaining ordinary HOME result is best explained",
        "  by the privileged Fire candidate plus the standard implicit resolver,",
        "  while Amazon task-visibility and package-protection callbacks form",
        "  separate boundaries. A direct Fire component injection was not found",
        "  in the bounded callback methods.",
        "- **已排除目前安全範圍：** private-service shell bypass, OOBE replay as",
        "  a normal launcher selector, and OTA/updater execution as a safe test.",
        "- **尚未證明：** every private Binder method's caller policy, the native",
        "  recovery canonicalization details, or any root/privilege transition.",
        "",
        "## Control-surface matrix",
        "",
        "| Surface | Observed path | Result | Confidence |",
        "|---|---|---|---|",
    ]
    for row in table_rows:
        lines.append(
            f"| {row['surface']} | {row['observed_path']} | {row['result']} | {row['confidence']} |"
        )
    lines.extend(
        [
            "",
            "## Reproduction",
            "",
            "```sh",
            "python3 tools/scripts/build_phase6as_public_synthesis.py --dry-run",
            "python3 tools/scripts/build_phase6as_public_synthesis.py \\",
            "  --output artifacts/phase6as/public-synthesis-20260805-01",
            "shasum -a 256 -c artifacts/phase6as/public-synthesis-20260805-01/sha256sums.txt",
            "```",
            "",
            "## Input hashes",
            "",
            "| Input | SHA-256 |",
            "|---|---|",
        ]
    )
    for name, digest in input_hashes.items():
        lines.append(f"| `{name}` | `{digest}` |")
    lines.extend(
        [
            "",
            "The complete raw ADB captures remain local evidence. Public output is",
            "bounded and does not publish device serials or raw restricted files.",
            "",
        ]
    )
    return "\n".join(lines)


def graph() -> str:
    return """flowchart LR
  HK[Home key] --> IMPL[KeyPolicyManagerCommon\nimplicit MAIN + HOME]
  IMPL --> PM[Android activity / PackageManager HOME resolution]
  PM --> FIRE[Fire Launcher candidate\nprivileged / effective priority 50]
  PROT[amazon.fireos deny-list resource] --> GATE[Amazon protected-package callback]
  GATE --> STATE[enabled-state protection]
  SVC[Amazon private service registrations] --> AVC[SELinux service-manager boundary]
  AVC -->|shell lookup denied in saved enforcing capture| SVCSTOP[No shell Binder handle]
  OTA[Official OTA package] --> WRITE[Updater write boundary]
  WRITE -->|not executed| STOP[No partition mutation]
  OTA --> POST[Post-OTA OOBE lifecycle]
  POST -->|protected / guarded| OOBE[OOBE state and setup component path]
  classDef safe fill:#e7f5e9,stroke:#2b7a3d;
  classDef boundary fill:#fff1d6,stroke:#a66b00;
  classDef stopped fill:#fbe4e6,stroke:#a33a46;
  class PM,FIRE,PROT,GATE,STATE safe;
  class AVC,WRITE,POST boundary;
  class SVCSTOP,STOP,OOBE stopped;
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/phase6as/public-synthesis-20260805-01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if output == ROOT or output == Path("/") or output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    missing = [str(ROOT / path) for path in INPUTS if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("missing input files:\n" + "\n".join(missing))
    input_hashes = {str(path): sha256(ROOT / path) for path in INPUTS}
    table_rows = rows()
    if args.dry_run:
        print(f"would create {output}")
        print(f"inputs={len(INPUTS)} rows={len(table_rows)}")
        return 0

    output.mkdir(parents=True)
    write(output / "summary.md", markdown(input_hashes, table_rows))
    write(output / "control-surface.mmd", graph())
    with (output / "control-surface.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table_rows[0]))
        writer.writeheader()
        writer.writerows(table_rows)
    write(output / "input-sha256.json", json.dumps(input_hashes, indent=2, ensure_ascii=False) + "\n")
    metadata = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "host-only public synthesis",
        "input_count": len(INPUTS),
        "row_count": len(table_rows),
        "device_mutation": False,
        "unknown_binder_transactions": False,
        "ota_or_partition_write": False,
    }
    write(output / "metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    files = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = "\n".join(f"{sha256(path)}  {path.relative_to(output)}" for path in files) + "\n"
    write(output / "sha256sums.txt", manifest)
    print(f"created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
