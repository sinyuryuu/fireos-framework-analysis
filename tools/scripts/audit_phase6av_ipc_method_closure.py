#!/usr/bin/env python3
"""Close selected PS7331 Amazon IPC method boundaries on the host.

This script is deliberately host-only.  It reads preserved VDEX disassembly,
the existing Binder-method inventory, and serial-redacted service-visibility
evidence.  It never contacts a device, obtains a Binder handle, sends a
transaction, changes package/settings state, or starts a process.

The result is a bounded method review, not a vulnerability scanner.  A missing
method-local authorization marker is recorded as unresolved; it is never
interpreted as an authorization bypass.
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
    "candidate_csv": ROOT / "artifacts/phase6q/binder-service-audit-20260805-03/binder-method-candidates.csv",
    "disassembly": ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
    "service_visibility": ROOT / "artifacts/phase6aq/public-summary-20260805-05/service-check-results.txt",
    "avc": ROOT / "artifacts/phase6aq/public-summary-20260805-05/amazon-service-avc.txt",
    "launcher_service_matrix": ROOT / "artifacts/phase6ak/launcher-user-service-20260805-02/launcher-user-service.csv",
}

FIELDS = [
    "evidence_id",
    "service",
    "binder_class",
    "method",
    "source_lines",
    "authorization_observed",
    "control_flow_observed",
    "state_or_process_effect",
    "shell_boundary",
    "classification",
    "confidence",
    "evidence_source",
]

TARGETS = [
    {
        "evidence_id": "6AV-IPC-001",
        "service": "AmazonInputManagerService",
        "method": "registerKeyEventInterceptor",
        "lines": "19829-19999",
        "authorization": "GET_KEYEVENTS permission; calling UID package lookup; package whitelist; foreground-package check",
        "control": "checkCallingOrSelfPermission -> getCallingUid -> getPackagesForUid -> whitelist containsKey -> foreground equality check",
        "effect": "Registers a key-event interceptor for selected key codes; not a HOME resolver write",
        "boundary": "Amazon input service is not shell-findable under saved enforcing SELinux capture",
        "classification": "CLOSED_FOR_SHELL_HOME_ROUTE",
        "confidence": "Confirmed",
    },
    {
        "evidence_id": "6AV-IPC-002",
        "service": "AmazonInputManagerService",
        "method": "setInputFilter",
        "lines": "20112-20122",
        "authorization": "Method delegates to synthetic access$600 helper; helper body is not present in the bounded disassembly excerpt",
        "control": "access$600 -> InputManagerService.registerSecondaryInputFilter",
        "effect": "Installs a secondary input filter; high impact but no bounded HOME component write",
        "boundary": "Amazon input service is not shell-findable; helper authorization remains unresolved",
        "classification": "STATIC_REVIEW_ONLY",
        "confidence": "Strong evidence",
    },
    {
        "evidence_id": "6AV-IPC-003",
        "service": "AmazonInputManagerService",
        "method": "setInputLockingMode",
        "lines": "20679-20713",
        "authorization": "com.amazon.amazoninputmanager.permission.INPUT_LOCKING",
        "control": "permission helper -> validate mode 0/1 -> update state -> notification",
        "effect": "Changes Amazon input-locking mode; not a formal HOME selection API",
        "boundary": "Amazon input service is not shell-findable under saved enforcing SELinux capture",
        "classification": "CLOSED_FOR_SHELL_HOME_ROUTE",
        "confidence": "Confirmed",
    },
    {
        "evidence_id": "6AV-IPC-004",
        "service": "AmazonProfileService",
        "method": "initiateLauncher",
        "lines": "76246-76256; guard 78949-78966",
        "authorization": "com.amazon.device.permission.PROFILE_INTERACTION via enforceProfileInteractionPermissions",
        "control": "guard checks permission; method invokes internal access$6400, logs, returns SUCCESS",
        "effect": "Profile interaction acknowledgement; no bounded preferred-activity or Fire component write",
        "boundary": "Amazon profile service is not shell-findable under saved enforcing SELinux capture",
        "classification": "NOT_HOME_SELECTOR",
        "confidence": "Confirmed",
    },
    {
        "evidence_id": "6AV-IPC-005",
        "service": "AmazonProfileService",
        "method": "startProfilePicker",
        "lines": "77222-77266",
        "authorization": "Service-manager visibility plus profile-service caller contract; method-local guard not in this excerpt",
        "control": "configuration map -> setClassName(package, activity) -> startActivityAsUser(current user)",
        "effect": "Explicitly starts configured profile-picker activity; not a HOME resolver mutation",
        "boundary": "Amazon profile service is not shell-findable; do not replay transaction",
        "classification": "STATIC_REVIEW_ONLY",
        "confidence": "Strong evidence",
    },
    {
        "evidence_id": "6AV-IPC-006",
        "service": "AmazonUserManagerService",
        "method": "enableKftLauncherComponent",
        "lines": "54297-54325",
        "authorization": "Reached from KFT child-user provisioning path; service-manager visibility remains required",
        "control": "enable com.amazon.tahoe FreeTimeLauncherActivity; set Fire Launcher and Launcher3 application state to disabled",
        "effect": "High-impact profile-specific package/component state mutation; explicitly disables Fire Launcher",
        "boundary": "Service not shell-findable; device test rejected by safety boundary",
        "classification": "STATIC_ONLY_REJECTED_FOR_DEVICE_TEST",
        "confidence": "Confirmed",
    },
    {
        "evidence_id": "6AV-IPC-007",
        "service": "AmazonActivityManagerService",
        "method": "preWarmApplicationForUser",
        "lines": "40453-40534",
        "authorization": "APP_PREWARM checkCallingPermission result not consumed before clearCallingIdentity in saved method block",
        "control": "getApplicationInfo(target) -> PreWarmCacheHelper -> startProcessLocked(..., prewarm, ...)",
        "effect": "Process prewarm for a selected package; no bounded HOME write",
        "boundary": "amazonactivitymanager service_manager find denied for shell UID 2000; known caller is privileged Alexa path",
        "classification": "STATIC_AUTH_ANOMALY_CANDIDATE_NOT_SHELL_REACHABLE",
        "confidence": "Strong evidence",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def line_range(value: str) -> tuple[int, int]:
    match = re.search(r"(\d+)\s*-\s*(\d+)", value)
    if not match:
        number = int(re.search(r"\d+", value).group())
        return number, number
    return int(match.group(1)), int(match.group(2))


def extract_snippet(text: str, ranges: str, limit: int = 120) -> str:
    lines = text.splitlines()
    chunks: list[str] = []
    for part in ranges.split(";"):
        start, end = line_range(part)
        selected = lines[max(0, start - 1):min(len(lines), end)]
        chunks.extend(f"{number}: {line}" for number, line in enumerate(selected, start))
    if len(chunks) > limit:
        chunks = chunks[:limit] + ["[snippet truncated by host-only exporter]"]
    return "\n".join(chunks)


def candidate_map(path: Path) -> dict[str, dict[str, str]]:
    rows = {}
    with path.open(newline="", encoding="utf-8", errors="replace") as stream:
        for row in csv.DictReader(stream):
            rows[row.get("method", "")] = row
    return rows


def write_hash_manifest(output: Path, names: list[str]) -> None:
    manifest = output / "sha256sums.txt"
    with manifest.open("w", encoding="utf-8") as stream:
        for name in names:
            stream.write(f"{sha256(output / name)}  {name}\n")


def public_path(path: Path) -> str:
    """Return a repository-relative path for public evidence metadata."""
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=default)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = {name: getattr(args, name) for name in DEFAULTS}
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "binder_invoked": False,
            "package_state_changed": False,
            "selected_methods": [row["method"] for row in TARGETS],
            "output": str(args.output),
        }, indent=2))
        return 0

    missing = [str(path) for path in inputs.values() if not path.is_file()]
    if missing:
        raise SystemExit("missing preserved input(s):\n" + "\n".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    candidates = candidate_map(inputs["candidate_csv"])
    disassembly = read(inputs["disassembly"])
    visibility_text = read(inputs["service_visibility"]) + "\n" + read(inputs["avc"])
    rows: list[dict[str, str]] = []
    snippets: list[str] = []
    for target in TARGETS:
        inventory = candidates.get(target["method"], {})
        source_line = inventory.get("lines") or target["lines"]
        observed = "inventory row present" if inventory else "inventory row not found"
        if target["method"] == "registerKeyEventInterceptor":
            observed += "; exact bounded block contains permission, UID package lookup, whitelist, and foreground checks"
        elif target["method"] == "preWarmApplicationForUser":
            observed += "; exact bounded block contains checkCallingPermission followed immediately by clearCallingIdentity"
        elif target["method"] == "enableKftLauncherComponent":
            observed += "; exact bounded block contains Fire Launcher state=2 mutation request"
        else:
            observed += "; selected instruction range retained for manual review"
        rows.append({
            "evidence_id": target["evidence_id"],
            "service": target["service"],
            "binder_class": inventory.get("binder_class", "NOT_OBSERVED"),
            "method": target["method"],
            "source_lines": source_line,
            "authorization_observed": target["authorization"],
            "control_flow_observed": target["control"],
            "state_or_process_effect": target["effect"],
            "shell_boundary": target["boundary"],
            "classification": target["classification"],
            "confidence": target["confidence"],
            "evidence_source": "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log + saved service visibility",
        })
        snippets.append(
            f"### {target['evidence_id']} {target['service']}.{target['method']}\n"
            f"source lines: {source_line}\n"
            f"{extract_snippet(disassembly, target['lines'])}\n"
        )

    csv_path = args.output / "ipc-method-closure.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    snippets_path = args.output / "method-snippets.txt"
    snippets_path.write_text("\n".join(snippets), encoding="utf-8")

    input_hashes = {public_path(path): sha256(path) for path in inputs.values()}
    (args.output / "input-sha256.json").write_text(
        json.dumps(input_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    visibility_blocked = bool(re.search(r"not found|find denied|avc", visibility_text, re.IGNORECASE))
    summary = {
        "phase": "6AV",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "binder_invoked": False,
        "package_state_changed": False,
        "process_started": False,
        "service_visibility_blocked_marker_observed": visibility_blocked,
        "method_count": len(rows),
        "classification": "bounded IPC method closure; missing markers are not negative proof",
        "input_sha256": input_hashes,
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    result = [
        "# Phase 6AV — PS7331 Amazon IPC method closure",
        "",
        "This is host-only analysis of preserved PS7331 VDEX and saved service-visibility evidence.",
        "No Binder handle was obtained, no transaction was sent, and no device state was changed.",
        "",
        "## Result",
        "",
        "- **已證實：** `registerKeyEventInterceptor` has a method-local permission, UID-to-package, whitelist, and foreground-package chain.",
        "- **已證實：** the saved enforcing-policy capture prevents shell discovery of the relevant Amazon private services.",
        "- **已證實（靜態）：** KFT launcher provisioning contains an explicit Fire Launcher disabled-state request; it is not an approved test route.",
        "- **Strong evidence：** `preWarmApplicationForUser` shows `checkCallingPermission(APP_PREWARM)` immediately followed by `clearCallingIdentity()` in the bounded method block, then resolves an application and calls `startProcessLocked`.",
        "- **已排除目前安全範圍：** a shell-callable HOME setter, a safe input-filter bypass, or a root path. Service visibility and caller-contract evidence do not provide such a route.",
        "- **待驗證：** helper bodies not present in the bounded disassembly and every private method's complete caller policy.",
        "",
        "## Interpretation",
        "",
        "The input service is the closest HOME-key control surface, but the inspected registration path is protected by Amazon permission and package/foreground checks. The profile and KFT methods are lifecycle/profile controls; they do not establish an ordinary HOME resolver replacement. The prewarm pattern remains a static authorization-review candidate only: no shell handle, Binder invocation, process start, or privilege transition was observed.",
        "",
        "## Reproduction",
        "",
        "```sh",
        "python3 tools/scripts/audit_phase6av_ipc_method_closure.py --dry-run --output /tmp/phase6av-dry-run",
        "python3 tools/scripts/audit_phase6av_ipc_method_closure.py --output artifacts/phase6av/ipc-method-closure-YYYYMMDD-01",
        "shasum -a 256 -c artifacts/phase6av/ipc-method-closure-YYYYMMDD-01/sha256sums.txt",
        "```",
    ]
    result_path = args.output / "result.md"
    result_path.write_text("\n".join(result) + "\n", encoding="utf-8")
    write_hash_manifest(args.output, ["ipc-method-closure.csv", "method-snippets.txt", "input-sha256.json", "summary.json", "result.md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
