#!/usr/bin/env python3
"""Audit the saved PS7331 IOtaDexopt contract without contacting a device.

This is deliberately a host-only parser.  It never invokes adb, service call,
Binder, dexopt, OTA, or package-management operations.  The input disassembly
and device captures are treated as immutable evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


INTERFACE = "android.content.pm.IOtaDexopt"
SERVICE = "otadexopt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def section(text: str, start: str, end_re: str) -> str:
    start_at = text.find(start)
    if start_at < 0:
        raise ValueError(f"missing section: {start}")
    match = re.search(end_re, text[start_at + len(start) :], re.MULTILINE)
    end_at = start_at + len(start) + (match.start() if match else len(text))
    return text[start_at:end_at]


def parse_proxy_methods(proxy: str) -> list[dict[str, object]]:
    method_re = re.compile(
        r"^\s+virtual_method #[^:]+: ([A-Za-z0-9_]+) \(\)" , re.MULTILINE
    )
    methods: list[dict[str, object]] = []
    matches = list(method_re.finditer(proxy))
    for index, match in enumerate(matches):
        name = match.group(1)
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(proxy)
        body = proxy[match.start() : body_end]
        transact = re.search(
            r"const/4 v3, #int (\d+).*?\n.*?invoke-interface \{v2, v3, v0, v1, v4\}, "
            r"Landroid/os/IBinder;\.transact",
            body,
            re.DOTALL,
        )
        if transact:
            methods.append(
                {
                    "method": name,
                    "transaction": int(transact.group(1)),
                    "proxy_offset": re.search(r"codeOff=([0-9a-f]+)", body).group(1)
                    if re.search(r"codeOff=([0-9a-f]+)", body)
                    else "UNKNOWN",
                    "read_only_by_name": name in {"getProgress", "isDone", "nextDexoptCommand"},
                    "mutation_by_name": name in {"prepare", "dexoptNextPackage", "cleanup"},
                }
            )
    return methods


def parse_stub_dispatch(stub: str) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for match in re.finditer(
        r"invoke-virtual \{v3\}, Landroid/content/pm/IOtaDexopt\$Stub;\."
        r"([A-Za-z0-9_]+):\(\)([^ ]+)",
        stub,
    ):
        name = match.group(1)
        result[name] = {"stub_dispatch": True, "stub_descriptor": match.group(2)}
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disassembly", type=Path, required=True)
    parser.add_argument("--service-list", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = [args.disassembly, args.service_list, args.metadata]
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        print("missing input: " + ", ".join(missing), file=sys.stderr)
        return 2

    plan = {
        "operation": "phase6ae_host_only_otadexopt_contract_audit",
        "inputs": [str(path) for path in inputs],
        "output": str(args.output),
        "device_contacted": False,
        "binder_transaction_sent": False,
        "ota_or_dexopt_operation": False,
        "mutates_input": False,
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0
    if args.output.exists():
        print(f"refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 2

    text = args.disassembly.read_text(errors="replace")
    proxy = section(text, "class #5411: IOtaDexopt.Stub.Proxy", r"^  class #5412:")
    stub = section(text, "class #5412: IOtaDexopt.Stub", r"^  class #5413:")
    methods = parse_proxy_methods(proxy)
    dispatch = parse_stub_dispatch(stub)
    for method in methods:
        method.update(dispatch.get(str(method["method"]), {"stub_dispatch": False}))

    service_lines = [
        line.rstrip("\n") for line in args.service_list.read_text(errors="replace").splitlines()
        if SERVICE in line
    ]
    metadata = json.loads(args.metadata.read_text())
    args.output.mkdir(parents=True)

    input_hashes = {str(path): sha256(path) for path in inputs}
    contract = {
        **plan,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "interface": INTERFACE,
        "service": SERVICE,
        "interface_source": "IOtaDexopt.java",
        "service_list_matches": service_lines,
        "method_count": len(methods),
        "methods": methods,
        "interface_stub_has_local_permission_check": False,
        "implementation_permission_check": "UNKNOWN_NOT_PRESENT_IN_SAVED_VDEX_SCOPE",
        "source_sha256": input_hashes,
        "capture_metadata": {
            "serial": metadata.get("serial"),
            "captured_at_utc": metadata.get("captured_at_utc"),
            "service_check_was_used": any(
                item.get("name") == "service_check_otadexopt"
                for item in metadata.get("commands", [])
            ),
        },
        "safe_runtime_action": "NONE; do not send private Binder transactions",
    }

    (args.output / "contract.json").write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n"
    )
    with (args.output / "methods.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "method",
                "transaction",
                "proxy_offset",
                "stub_dispatch",
                "stub_descriptor",
                "read_only_by_name",
                "mutation_by_name",
            ],
        )
        writer.writeheader()
        writer.writerows(methods)

    graph = """flowchart TD
    S[service list: otadexopt] --> B[IOtaDexopt Binder]
    B --> P[Proxy transaction map]
    P --> T1[1 prepare - mutating]
    P --> T2[2 cleanup - mutating]
    P --> T3[3 isDone - read-like]
    P --> T4[4 getProgress - read-like]
    P --> T5[5 dexoptNextPackage - mutating]
    P --> T6[6 nextDexoptCommand - read-like but sensitive]
    B --> X[Stub enforceInterface only in saved Stub]
    X --> Q[Implementation permission unresolved]
"""
    (args.output / "otadexopt-contract.mmd").write_text(graph)

    result = """# Phase 6AE host-only result

This artifact parses the saved PS7331 `IOtaDexopt` Binder contract. It does not
contact a device, invoke `service call`, send a Binder transaction, run OTA or
dexopt, or modify any input.

## Result

- The saved service list contains `otadexopt` with descriptor
  `android.content.pm.IOtaDexopt`.
- The saved interface exposes six methods and the Proxy maps them to
  transactions 1 through 6.
- The saved Stub performs `enforceInterface()` and dispatches directly to the
  implementation methods. No method-local permission check is visible in the
  Stub. This does **not** prove that the implementation lacks authorization.
- The saved VDEX scope does not recover the concrete publisher/implementation
  class or its permission branch.
- Methods named `prepare`, `dexoptNextPackage`, and `cleanup` are treated as
  potentially state-changing and are not invoked. The read-like methods are
  also not invoked because doing so would require a private Binder transaction
  whose implementation and authorization boundary are unresolved.

## Safety classification

`otadexopt` is a standard dexopt/OTA-adjacent control surface, not evidence of a
HOME selector, Fire Launcher override, privilege transition, or root path.
The next safe step is to recover the implementation statically from an exact
PS7331 services artifact or an authoritative matching Android 9 source tree.
No runtime transaction is justified by this contract-only evidence.
"""
    (args.output / "result.md").write_text(result)

    files = sorted(path for path in args.output.iterdir() if path.name != "sha256sums.txt")
    with (args.output / "sha256sums.txt").open("w") as handle:
        for path in files:
            handle.write(f"{sha256(path)}  {path.name}\n")
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
