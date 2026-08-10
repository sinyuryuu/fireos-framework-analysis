#!/usr/bin/env python3
"""Build the Phase 12 host-only control-surface report.

The script consumes small worker CSV/Markdown outputs and the serial-bound
read-only baseline.  It never invokes adb, Binder, an OTA binary, a driver, or
any device mutation.  Raw captures and worker outputs are inputs; generated
reports are written to separate findings/output/manifest paths.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "adb/phase12/PHASE12-BASELINE-20260810-01"
POST_GUARD = ROOT / "adb/phase12/PHASE12-POST-HOST-GUARD-20260810-01"
WORKER_FILES = {
    "existing-evidence": ROOT / "work/luna_worker_phase12_existing_evidence_20260810.csv",
    "binder-package": ROOT / "work/luna_worker_phase12_binder_package_20260810.csv",
    "ota": ROOT / "work/luna_worker_phase12_ota_20260810.csv",
    "driver": ROOT / "work/luna_worker_phase12d_driver_20260810.csv",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def csv_shape(path: Path) -> tuple[int, int, int]:
    """Return header count, row count, and malformed-row count."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = list(reader)
    return len(header), len(rows), sum(len(row) != len(header) for row in rows)


def pick(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = (row.get(name) or "").strip()
        if value:
            return value
    return "UNKNOWN"


def normalize_confidence(value: str) -> str:
    """Map worker shorthand to the project's allowed confidence vocabulary."""
    mapping = {
        "High": "Strong evidence",
        "Medium": "Probable",
        "Low": "Hypothesis",
        "UNKNOWN": "Unknown",
        "Unknown": "Unknown",
    }
    return mapping.get(value, value)


def normalize(kind: str, row: dict[str, str]) -> dict[str, str]:
    if kind == "existing-evidence":
        return {
            "phase": pick(row, "phase"),
            "source_id": pick(row, "test_or_evidence_id"),
            "surface": "existing-evidence",
            "entrypoint_or_source": pick(row, "command_or_method"),
            "caller_or_input": "UNKNOWN",
            "gate_or_policy": "UNKNOWN",
            "user_scope_or_target": "UNKNOWN",
            "sink_or_effect": pick(row, "observed_result"),
            "evidence": pick(row, "source_file"),
            "confidence": normalize_confidence(pick(row, "confidence")),
            "open_gap": pick(row, "open_gap"),
        }
    if kind == "binder-package":
        return {
            "phase": "12",
            "source_id": pick(row, "surface", "entrypoint"),
            "surface": pick(row, "surface"),
            "entrypoint_or_source": pick(row, "entrypoint"),
            "caller_or_input": pick(row, "caller"),
            "gate_or_policy": pick(row, "permission_or_gate"),
            "user_scope_or_target": pick(row, "user_scope"),
            "sink_or_effect": pick(row, "sink", "observed_effect"),
            "evidence": pick(row, "evidence"),
            "confidence": normalize_confidence(pick(row, "confidence")),
            "open_gap": pick(row, "missing_edge"),
        }
    if kind == "ota":
        return {
            "phase": "12",
            "source_id": pick(row, "surface", "entrypoint"),
            "surface": pick(row, "surface"),
            "entrypoint_or_source": pick(row, "entrypoint"),
            "caller_or_input": pick(row, "caller_scope", "input"),
            "gate_or_policy": pick(row, "gate"),
            "user_scope_or_target": pick(row, "write_target"),
            "sink_or_effect": pick(row, "sink", "observed_effect"),
            "evidence": pick(row, "evidence"),
            "confidence": normalize_confidence(pick(row, "confidence")),
            "open_gap": pick(row, "open_gap"),
        }
    # The raw driver worker file has a 14-column header but 13-field data
    # rows. Preserve it as evidence, but do not treat shifted fields as a
    # security conclusion in the normalized table.
    return {
        "phase": "12D",
        "source_id": pick(row, "id"),
        "surface": pick(row, "surface"),
        "entrypoint_or_source": pick(row, "source_entry"),
        "caller_or_input": pick(row, "shipped_userspace_caller"),
        "gate_or_policy": pick(row, "node_policy"),
        "user_scope_or_target": pick(row, "node_policy"),
        "sink_or_effect": pick(row, "sensitive_sink") if pick(row, "sensitive_sink") != "UNKNOWN" else pick(row, "ioctl_or_api"),
        "evidence": "worker report; raw CSV schema requires manual review",
        "confidence": "Unknown",
        "open_gap": pick(row, "missing_edge", "status") if pick(row, "missing_edge", "status") != "UNKNOWN" else "driver caller/policy/sink closure and raw CSV schema review",
    }


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    required = list(WORKER_FILES.values()) + [
        BASELINE / "metadata.json",
        BASELINE / "sha256sums.txt",
        POST_GUARD / "metadata.json",
        POST_GUARD / "sha256sums.txt",
        ROOT / "findings/phase-12-readonly-baseline.md",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("missing input(s):\n" + "\n".join(missing))

    out_files = [
        ROOT / "findings/phase-12-report.md",
        ROOT / "findings/phase-12-evidence-index.md",
        ROOT / "output/tables/phase12-control-surface.csv",
        ROOT / "output/call-graphs/phase12-control-surfaces.mmd",
        ROOT / "output/call-graphs/phase12-control-surfaces.md",
        ROOT / "firmware/manifests/PHASE12-HOST-ANALYSIS-20260810/sha256sums.txt",
    ]
    if not args.force:
        existing = [str(p) for p in out_files if p.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force:\n" + "\n".join(existing))

    rows: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    shapes: dict[str, tuple[int, int, int]] = {}
    for kind, path in WORKER_FILES.items():
        source_rows = read_csv(path)
        counts[kind] = len(source_rows)
        shapes[kind] = csv_shape(path)
        rows.extend(normalize(kind, row) for row in source_rows)

    table_path = ROOT / "output/tables/phase12-control-surface.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "phase", "source_id", "surface", "entrypoint_or_source",
        "caller_or_input", "gate_or_policy", "user_scope_or_target",
        "sink_or_effect", "evidence", "confidence", "open_gap",
    ]
    with table_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    manifest_inputs = required + list(WORKER_FILES.values())
    manifest_inputs = list(dict.fromkeys(manifest_inputs))
    manifest_dir = ROOT / "firmware/manifests/PHASE12-HOST-ANALYSIS-20260810"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "sha256sums.txt"
    with manifest_path.open("w", encoding="utf-8") as f:
        for path in sorted(manifest_inputs):
            f.write(f"{digest(path)}  {path.relative_to(ROOT)}\n")

    generated = datetime.now(timezone.utc).isoformat()
    evidence_lines = [
        "# Phase 12 evidence index",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "This index is host-only. It does not claim that a static caller, Binder",
        "handle, update-binary sink, driver node, or source capability was reached",
        "on the device. Every missing caller, identity, user scope, policy or sink",
        "edge remains `UNKNOWN`.",
        "",
        "## Worker row counts",
        "",
        "| Input | Rows | CSV shape QA | SHA-256 manifest |",
        "|---|---:|---|---|",
    ]
    for kind, path in WORKER_FILES.items():
        header_count, row_count, malformed_count = shapes[kind]
        shape_note = f"{header_count} cols; malformed rows: {malformed_count}"
        evidence_lines.append(f"| `{kind}` | {counts[kind]} | {shape_note} | `{digest(path)}` |")
    evidence_lines.extend([
        "",
        "## Baseline and generated inputs",
        "",
        f"- Baseline manifest: `{digest(BASELINE / 'sha256sums.txt')}`",
        f"- Baseline metadata: `{digest(BASELINE / 'metadata.json')}`",
        f"- Baseline report: `{digest(ROOT / 'findings/phase-12-readonly-baseline.md')}`",
        f"- Post-host guard manifest: `{digest(POST_GUARD / 'sha256sums.txt')}`",
        f"- Normalized table: `{digest(table_path)}`",
        "",
        "## Confidence rule",
        "",
        "`Confirmed` is reserved for a directly observed or directly preserved",
        "fact. `Strong evidence` still requires any explicitly listed missing edge",
        "to be resolved before it becomes a reachability claim. `Unknown` means the",
        "bounded corpus did not close the edge. `Disproved` applies only to the",
        "specific tested route, not to every possible implementation.",
    ])
    (ROOT / "findings/phase-12-evidence-index.md").write_text(
        "\n".join(evidence_lines) + "\n", encoding="utf-8"
    )

    report = f"""# Phase 12 — broad privilege-surface closure

## Executive result

This phase broadened the review beyond Launcher-only logic across four
independent surfaces: existing test evidence, Amazon Binder/package-state
writers, OTA/post-install paths, and MTK/Amazon driver callers. The review was
host-only except for one new serial-bound read-only baseline. No root exploit,
unknown Binder transaction, driver open/ioctl, OTA/recovery execution, reboot,
partition write, Fire Launcher state mutation, or Fire Launcher data deletion
was performed.

**Confirmed:** the current device remains User 0 with SELinux Enforcing and
formal HOME `com.amazon.firelauncher/.Launcher` at priority 50.

**Strong evidence:** the bounded Framework/Binder corpus does not close an
ordinary-app or shell path to User-0 Fire package/component state, HOME state,
UID 0, or a protected partition.

**Confirmed static capability, not runtime access:** the signed OTA script
contains recovery-time partition sinks; its caller, verifier, AVB/SELinux
handoff and runtime execution were not established.

**Unknown:** all twelve driver surfaces remain missing at least one of the
shipped caller, node policy, identity/domain, validation, or effect edges.

## Current baseline

The serial-bound capture is
[`adb/phase12/PHASE12-BASELINE-20260810-01`](../adb/phase12/PHASE12-BASELINE-20260810-01)
and its summary is
[`findings/phase-12-readonly-baseline.md`](phase-12-readonly-baseline.md).

| Field | Observation | Status |
|---|---|---|
| Serial | `G001LT0511550CFT` | Confirmed |
| Fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed |
| Current user | `0` | Confirmed |
| SELinux | `Enforcing` | Confirmed |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority `50` | Confirmed |
| User 10 HOME | `com.android.settings/.FallbackHome`, priority `-1000` | Confirmed |

The post-host guard
[`adb/phase12/PHASE12-POST-HOST-GUARD-20260810-01`](../adb/phase12/PHASE12-POST-HOST-GUARD-20260810-01)
repeated only `get-state`, fingerprint, current-user, User-0 HOME resolution,
and the Fire package dump. It matched the baseline: User 0, the same PS7331
fingerprint, and Fire Launcher HOME priority 50. Its SHA-256 manifest passed.

## Control-surface findings

### Amazon Binder and package state

The worker closure identifies the known KFT writer as child/profile-scoped:
the sink consumes a supplied `UserInfo.id`, and the observed effect is on the
child user. It does not prove a User-0 route. AmazonPackageManager metadata
writers retain the `ADD_RM_PKG_METADATA` gate and the private interface has no
formal HOME or enabled-state setter. Its facade delegates enabled-state and
preferred operations to ordinary PMS checks.

`IAmazonUserManager` service-handle reachability is not method authorization.
The exact tx3 authorization and arbitrary `UserInfo` construction edge remain
`UNKNOWN`; no unknown transaction was sent. DPM generic restrictions still
flow through active-admin/owner checks. ProxyReceiver requires a system-app
PendingIntent creator; the saved ordinary-app result was negative.

### OTA and post-install

The PS7331 `updater-script` statically names system/vendor/boot and several
boot-chain partition sinks. This is a recovery/update-binary capability
contract, not evidence that an app or shell can invoke it. Sideload validation,
release metadata, device/version checks, signature/PVT checks, and recovery
handoff remain gates. The post-OTA OOBE sender uses the protected
`RECEIVE_BOOT_AFTER_SYSTEM_OTA` path; delivery, user handoff, and native
verifier behavior were not replayed.

No malformed package, symlink/traversal input, update-binary invocation,
recovery/sideload, or partition operation was performed. These remain
**因風險拒絕測試**.

### MTK/Amazon drivers

The driver review covers CMDQ, ION, M4U, uinput, AUXADC, performance,
Amazon liquid detection, Amazon driver-test, thermal/PMIC, USB, RPMB, and the
MediaTek SoC directory. All remain `UNKNOWN`: source/Kconfig, init mode, a
file-context label, or an ioctl handler alone does not establish a retail
caller, SELinux allow, UID/domain, validation, or a package/HOME/credential
effect. No device node was opened. The raw driver CSV has a 14-column header
but 13-field data rows; the normalized table therefore forces all driver
confidence values to `UNKNOWN` and treats the worker narrative as the
authoritative summary until the raw CSV is repaired.

### Existing runtime evidence

The prior child-profile, DPM, package-state, HOME, OTA and Accessibility
captures were indexed without replay. The Phase 11 Accessibility T01/T02
results remain foreground-observation-only: formal HOME stayed Fire and the
current APK did not produce a reliable redirect. This does not prove that every
future Accessibility implementation is ineffective, but it is not a stable
replacement result.

## Overall decision

**No new reproducible low-privilege route was established.** The formal HOME
replacement and Fire Launcher disable objectives remain unachieved without
Root/system privilege or an as-yet unproven control-surface flaw. The present
evidence supports closing the broad static sweep as a bounded negative result,
not declaring that every private API or driver is mathematically impossible.

The safest next research targets are host-only completion of the remaining
exact tx3 Stub/caller and compiled policy/DT joins, followed by a natural,
non-mutating lifecycle observation if a concrete caller is identified. Sending
unknown Binder parcels, invoking update-binary/recovery, opening driver nodes,
or mutating Fire Launcher state is not justified by the current evidence.

## Reproduction

```sh
python3 tools/scripts/capture_phase6ee_current_baseline.py \\
  --serial G001LT0511550CFT \\
  --output adb/phase12/PHASE12-BASELINE-20260810-01
python3 tools/scripts/build_phase12_report.py --force
```

The normalized matrix is
[`output/tables/phase12-control-surface.csv`](../output/tables/phase12-control-surface.csv),
the evidence index is
[`findings/phase-12-evidence-index.md`](phase-12-evidence-index.md),
and the call graph is
[`output/call-graphs/phase12-control-surfaces.mmd`](../output/call-graphs/phase12-control-surfaces.mmd).
"""
    (ROOT / "findings/phase-12-report.md").write_text(report, encoding="utf-8")

    graph = """flowchart TD
    A["ordinary app / shell"] --> B["Binder or framework entry"]
    B --> C{"caller + permission + identity + user scope closed?"}
    C -->|No| U["UNKNOWN / stop; no payload"]
    C -->|KFT child only| K["UserInfo.id child/profile lifecycle"]
    C -->|PMS standard gate| P["protected package / preferred / cross-user checks"]
    C -->|OTA protected| O["recovery/update-binary capability; not invoked"]
    C -->|driver edges missing| D["node/policy/native caller UNKNOWN"]
    K --> K2["observed child state only; no User-0 HOME effect"]
    P --> P2["no ordinary User-0 Fire/HOME writer observed"]
    O --> O2["partition sinks static only; AVB/SELinux/runtime UNKNOWN"]
    D --> D2["no device node opened; no HOME/PMS sink"]
    U --> Z["No UID 0 or formal HOME replacement established"]
    K2 --> Z
    P2 --> Z
    O2 --> Z
    D2 --> Z
"""
    graph_md = """# Phase 12 control-surface graph (text form)

```text
ordinary app / shell
  -> Binder or framework entry
  -> caller + permission + identity + user scope?
     -> KFT child path: UserInfo.id -> child/profile state only
     -> PMS path: standard protected-package/preferred/cross-user gates
     -> OTA path: recovery/update-binary capability, not invoked
     -> driver path: node/policy/native caller missing
  -> no closed User-0 Fire/HOME/UID0 path established
```

The graph intentionally stops at unknown edges; it is not an exploit recipe.
"""
    (ROOT / "output/call-graphs/phase12-control-surfaces.mmd").write_text(graph, encoding="utf-8")
    (ROOT / "output/call-graphs/phase12-control-surfaces.md").write_text(graph_md, encoding="utf-8")
    print({"rows": len(rows), "counts": counts, "table": str(table_path)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
