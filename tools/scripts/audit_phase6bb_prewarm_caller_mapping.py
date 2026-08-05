#!/usr/bin/env python3
"""Map the PS7331 prewarm Binder method and saved callers without device access."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


METHOD = "preWarmApplicationForUser"
SERVICE_DESCRIPTOR = "com.amazon.android.server.am.IAmazonActivityManager"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> str:
    # Preserve CR and other control bytes in disassembly output. Path.read_text()
    # uses universal-newline translation, which shifts source locations when a
    # VDEX dump contains standalone CR rows.
    return path.read_bytes().decode("utf-8", errors="replace")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def method_blocks(path: Path) -> list[dict[str, object]]:
    # The DEX disassembly contains control characters in some instruction rows.
    # splitlines() treats several of those as line separators and shifts the
    # human-facing locations, so preserve the actual LF layout used by rg/nl.
    lines = read(path).split("\n")
    starts = [
        index
        for index, line in enumerate(lines)
        if "virtual_method" in line and METHOD in line
    ]
    blocks: list[dict[str, object]] = []
    for start in starts:
        end = next(
            (index for index in range(start + 1, len(lines)) if "virtual_method" in lines[index]),
            len(lines),
        )
        block = lines[start:end]
        header = lines[start]
        class_header = next(
            (
                lines[index].strip()
                for index in range(start - 1, -1, -1)
                if re.match(r"\s*class #[0-9]+:", lines[index])
            ),
            "",
        )
        scope = f"{class_header} {header}"
        if "AmazonActivityManagerService.BinderService" in scope or "AmazonActivityManagerService$BinderService" in scope:
            kind = "server_method"
        elif "$Stub$Proxy" in scope:
            kind = "binder_proxy"
        elif "IAmazonActivityManager" in scope and "Stub" not in scope:
            kind = "interface_declaration"
        elif "AmazonActivityManagerImpl" in scope:
            kind = "framework_wrapper"
        else:
            kind = "other_method_scope"
        transaction = None
        for line in block:
            match = re.search(r"const/(?:4|16) v3, #int ([-0-9]+).*", line)
            if match and "#int" in line:
                transaction = int(match.group(1))
            if "IBinder;.transact" in line and transaction is not None:
                break
        check_index = next(
            (index for index, line in enumerate(block) if "checkCallingPermission" in line),
            None,
        )
        clear_index = next(
            (index for index, line in enumerate(block) if "Binder;.clearCallingIdentity" in line),
            None,
        )
        permission_result_consumed = None
        if check_index is not None and clear_index is not None and check_index < clear_index:
            permission_result_consumed = any(
                "move-result" in line for line in block[check_index + 1 : clear_index]
            )
        blocks.append(
            {
                "source": rel(path),
                "line_start": start + 1,
                "line_end": end,
                "kind": kind,
                "class_header": class_header,
                "header": header.strip(),
                "transaction": transaction,
                "has_permission_check": check_index is not None,
                "permission_result_consumed_before_identity_clear": permission_result_consumed,
                "has_clear_calling_identity": clear_index is not None,
                "has_start_process_locked": any("startProcessLocked" in line for line in block),
            }
        )
    return blocks


def caller_occurrences(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".java", ".kt", ".smali"}:
            continue
        for line_number, line in enumerate(read(path).split("\n"), start=1):
            if METHOD not in line:
                continue
            stripped = line.strip()
            if "public abstract" in stripped or "abstract int" in stripped:
                kind = "api_declaration"
            elif "AmazonActivityManager.java" in path.name:
                kind = "api_declaration"
            elif "." in stripped and "(" in stripped:
                kind = "direct_or_wrapper_call"
            else:
                kind = "reference"
            rows.append(
                {
                    "source": rel(path),
                    "line": line_number,
                    "kind": kind,
                    "text": stripped,
                }
            )
    return rows


def run(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    service_blocks = method_blocks(args.fos_vdex)
    framework_blocks = method_blocks(args.framework_vdex)
    ota_blocks = method_blocks(args.ota_vdex)
    occurrences = caller_occurrences(args.caller_root)
    registration = read(args.registration)
    direct_callers = [row for row in occurrences if row["kind"] == "direct_or_wrapper_call"]
    summary = {
        "schema": 1,
        "phase": "6BB",
        "host_only": True,
        "device_contacted": False,
        "binder_invoked": False,
        "mutation_performed": False,
        "root_attempted": False,
        "method": METHOD,
        "descriptor": SERVICE_DESCRIPTOR,
        "service_name": "amazonactivitymanager",
        "service_registered_in_fosinit": "AmazonActivityManagerService" in registration,
        "manager_registered_in_fosinit": "amazon.app.AmazonActivityManagerImpl" in registration,
        "direct_callers_in_saved_source_scope": direct_callers,
        "ordinary_sideloaded_caller_established": False,
        "service_manager_shell_route_tested": False,
        "service_manager_shell_route_from_saved_capture": "denied",
        "source_hashes": {
            rel(path): sha256(path)
            for path in (args.fos_vdex, args.framework_vdex, args.ota_vdex, args.registration)
        },
        "limitations": [
            "The caller search is limited to the supplied saved Alexa JADX source scope.",
            "JADX is an approximation; the VDEX method blocks and transaction proxy are retained as the primary evidence.",
            "No Binder transaction, service call, permission change, process start, or package mutation was attempted.",
        ],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    rows = []
    for block in service_blocks + framework_blocks + ota_blocks:
        rows.append(block)
    return rows, occurrences, summary


def write_outputs(output: Path, blocks: list[dict[str, object]], occurrences: list[dict[str, object]], summary: dict[str, object]) -> None:
    output.mkdir(parents=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    block_fields = [
        "source", "line_start", "line_end", "kind", "class_header", "transaction", "has_permission_check",
        "permission_result_consumed_before_identity_clear", "has_clear_calling_identity",
        "has_start_process_locked", "header",
    ]
    with (output / "prewarm-method-map.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=block_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in block_fields} for row in blocks)
    occurrence_fields = ["source", "line", "kind", "text"]
    with (output / "prewarm-source-occurrences.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=occurrence_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in occurrence_fields} for row in occurrences)
    graph_md = """AmazonActivityManagerImpl
  -> ServiceManager.getService(amazonactivitymanager)
  -> IAmazonActivityManager.Stub.Proxy
  -> preWarmApplicationForUser(...)
  -> Binder.transact(code=1)
  -> AmazonActivityManagerService.BinderService
  -> checkCallingPermission(APP_PREWARM)
  -> clearCallingIdentity
  -> getApplicationInfo / PreWarmCacheHelper
  -> startProcessLocked(..., \"prewarm\", ...)

Saved caller scope:
  Alexa ExplicitIntentAction.prewarmApplicationProcess
  -> preWarmApplicationForUser(targetPackage, 0, foregroundProfileId)

No ordinary sideloaded caller, Binder invocation, or device mutation was established.
"""
    (output / "prewarm-flow.md").write_text(graph_md, encoding="utf-8")
    (output / "prewarm-flow.mmd").write_text(
        """flowchart TD
  A[Alexa ExplicitIntentAction.prewarmApplicationProcess] --> B[AmazonActivityManagerImpl]
  B --> C[ServiceManager.getService amazonactivitymanager]
  C --> D[IAmazonActivityManager Proxy]
  D -->|Binder transaction 1| E[AmazonActivityManagerService BinderService]
  E --> F[checkCallingPermission APP_PREWARM]
  F --> G[clearCallingIdentity]
  G --> H[getApplicationInfo / PreWarmCacheHelper]
  H --> I[startProcessLocked prewarm]
  J[ordinary sideloaded app] -. no saved caller .-> D
  K[shell] -. service-manager find denied in saved capture .-> C
""",
        encoding="utf-8",
    )
    report = [
        "# Phase 6BB — prewarm caller and Binder transaction closure",
        "",
        "This is a host-only mapping of the saved PS7331 VDEX and Alexa JADX scope.",
        "No device, Binder service, permission, process, package, or settings state was changed.",
        "",
        "## Result",
        "",
        "* The saved proxy uses Binder transaction code `1` for `preWarmApplicationForUser(String,int,int)`.",
        "* The exact service name is `amazonactivitymanager`, registered with the Amazon activity-manager implementation.",
        "* The only direct caller found in the supplied Alexa source scope is `ExplicitIntentAction.prewarmApplicationProcess`.",
        "* The server method contains `checkCallingPermission(APP_PREWARM)`, then clears identity before the prewarm process path.",
        "* No ordinary sideloaded caller, shell route, Binder invocation, or privilege transition was established.",
        "",
        "## Disposition",
        "",
        "**Confirmed static:** the method is a real privileged prewarm/process-control surface.",
        "**Strong evidence:** the saved caller is the privileged Alexa path, with target filtering and Amazon permissions documented in Phase 6K.",
        "**Not established:** a permission bypass, root path, or HOME replacement.",
        "**Risk-rejected:** sending transaction 1, using `service call`, fuzzing parameters, or forcing a process start.",
        "",
        "See `prewarm-method-map.csv`, `prewarm-source-occurrences.csv`, and the call graphs for reproducible rows.",
    ]
    (output / "result.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(output)}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fos-vdex", type=Path, default=Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"))
    parser.add_argument("--framework-vdex", type=Path, default=Path("decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log"))
    parser.add_argument("--ota-vdex", type=Path, default=Path("decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log"))
    parser.add_argument("--caller-root", type=Path, default=Path("artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources"))
    parser.add_argument("--registration", type=Path, default=Path("artifacts/amazon-services/amazonactivitymanager_fosinit.xml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_mutation": False, "output": str(args.output)}, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    for path in (args.fos_vdex, args.framework_vdex, args.ota_vdex, args.registration):
        if not path.is_file():
            raise SystemExit(f"missing required input: {path}")
    blocks, occurrences, summary = run(args)
    write_outputs(args.output, blocks, occurrences, summary)
    print(f"wrote {args.output} ({len(blocks)} method blocks, {len(occurrences)} source occurrences)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
