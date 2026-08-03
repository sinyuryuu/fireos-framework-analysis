#!/usr/bin/env python3
"""Index Android Bluetooth permission and Amazon BTPM boundaries.

This is a host-only parser for the already extracted VDEX text artifacts.  It
does not communicate with a device, invoke a Binder method, load a library,
or execute a proof of concept.  In particular, DEX method numbers are kept as
metadata and are never interpreted as CVE identifiers.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


METHOD_RE = re.compile(
    r"^\s*(?P<line>\d+):\s+(?:\[new\]\s+)?"
    r"(?P<kind>direct_method|virtual_method)\s+#(?P<index>\d+):\s+(?P<signature>.+?)\s*$"
)
CLASS_RE = re.compile(
    r"^\s*\d+:\s+class\s+#\d+:\s+(?P<name>[^ (]+)\s+\('(?P<descriptor>L[^']+;)'\)"
)
OFFSET_RE = re.compile(r"\|(?P<offset>[0-9a-fA-F]+):")
CODE_ADDRESS_RE = re.compile(
    r"^\s*\d+:\s+(?:\[new\]\s+)?(?P<address>[0-9a-fA-F]+):"
)

FOCUS_PATTERNS = {
    "gatt": re.compile(
        r"^(?:clientConnect|clientDisconnect|enforceAdminPermission|"
        r"enforcePrivilegedPermission|permissionCheck|readCharacteristic|"
        r"readDescriptor|registerClient|registerPiAndStartScan|"
        r"registerForNotification|writeCharacteristic|writeDescriptor|"
        r"configureMtu|unregisterClient|unregisterScanner|scan|startScan|"
        r"stopScan|registerServer|unregisterServer)"
    ),
    "fos_gatt": re.compile(
        r"^(?:clientConnect|clientDisconnect|onBtpm|register|unregister|"
        r"scan|startScan|stopScan|read|write|configure|connect|disconnect)"
    ),
    "btpm": re.compile(
        r"^(?:.*Native|btpm.*Callback|classBtpmInit|initializeBtpm|"
        r"cleanup|getInstance)"
    ),
}

PERMISSION_LITERAL_RE = re.compile(
    r"android\.permission\.(?:BLUETOOTH(?:_ADMIN|_PRIVILEGED)?)"
)


@dataclass(frozen=True)
class MethodBlock:
    source: Path
    owner: str
    owner_descriptor: str
    kind: str
    dex_method_index: int
    signature: str
    source_line: int
    lines: tuple[str, ...]

    @property
    def method_name(self) -> str:
        return self.signature.split(" ", 1)[0]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def first_instruction_offset(self) -> str:
        for line in self.lines:
            match = OFFSET_RE.search(line)
            if match:
                return "0x" + match.group("offset").lower()
        return ""

    @property
    def first_code_address(self) -> str:
        for line in self.lines:
            match = CODE_ADDRESS_RE.match(line)
            if match:
                return "0x" + match.group("address").lower()
        return ""


def parse_file(path: Path) -> tuple[str, str, list[MethodBlock]]:
    raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    owner = path.stem
    owner_descriptor = ""
    for line in raw_lines[:200]:
        match = CLASS_RE.match(line)
        if match:
            owner = match.group("name")
            owner_descriptor = match.group("descriptor")
            break

    starts: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(raw_lines):
        match = METHOD_RE.match(line)
        if match:
            starts.append((index, match))

    blocks: list[MethodBlock] = []
    for position, (start, match) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(raw_lines)
        blocks.append(
            MethodBlock(
                source=path,
                owner=owner,
                owner_descriptor=owner_descriptor,
                kind=match.group("kind"),
                dex_method_index=int(match.group("index")),
                signature=match.group("signature"),
                source_line=int(match.group("line")),
                lines=tuple(raw_lines[start:end]),
            )
        )
    return owner, owner_descriptor, blocks


def bool_text(text: str, *needles: str) -> str:
    return "yes" if any(needle in text for needle in needles) else "no"


def classify(block: MethodBlock, label: str) -> str:
    text = block.text
    if label == "btpm":
        return "amazon_btpm_native_or_callback"
    if label == "fos_gatt":
        return "amazon_fos_gatt_callback_or_override"
    if "permissionCheck" in block.method_name or "enforce" in block.method_name:
        return "android_bluetooth_permission_helper"
    if any(
        token in text
        for token in (
            "enforceAdminPermission",
            "enforcePrivilegedPermission",
            "permissionCheck",
            "BLUETOOTH_PRIVILEGED",
            "BLUETOOTH_ADMIN",
        )
    ):
        return "android_bluetooth_permission_boundary"
    return "android_bluetooth_gatt_entrypoint"


def row_for(block: MethodBlock, label: str) -> dict[str, str]:
    text = block.text
    permissions = sorted(set(PERMISSION_LITERAL_RE.findall(text)))
    native_or_callback = any(
        token in text
        for token in (
            "Native",
            "native",
            "BTPM",
            "btpm",
            "FosGattService",
            "AmazonBtPolicyManagerAdapter",
        )
    )
    return {
        "artifact": str(block.source),
        "owner": block.owner,
        "owner_descriptor": block.owner_descriptor,
        "method_kind": block.kind,
        "dex_method_index": str(block.dex_method_index),
        "method_signature": block.signature,
        "artifact_line": str(block.source_line),
        "first_code_address": block.first_code_address,
        "first_instruction_offset": block.first_instruction_offset,
        "bluetooth_permission": bool_text(text, "BLUETOOTH", "Utils.enforceBluetoothPermission"),
        "bluetooth_admin_permission": bool_text(
            text, "BLUETOOTH_ADMIN", "enforceAdminPermission"
        ),
        "bluetooth_privileged_permission": bool_text(
            text, "BLUETOOTH_PRIVILEGED", "enforcePrivilegedPermission"
        ),
        "permission_helper_call": bool_text(text, "permissionCheck", "enforceAdminPermission", "enforcePrivilegedPermission"),
        "amazon_native_or_callback": "yes" if native_or_callback else "no",
        "permission_literals": ";".join(permissions),
        "boundary_classification": classify(block, label),
        "interpretation": (
            "DEX method index; not a CVE identifier. Review smali/control flow."
            if block.dex_method_index >= 20000
            else "DEX method index; not a CVE identifier."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gatt", type=Path, required=True)
    parser.add_argument("--fos-gatt", type=Path, required=True)
    parser.add_argument("--btpm", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = [("gatt", args.gatt), ("fos_gatt", args.fos_gatt), ("btpm", args.btpm)]
    missing = [str(path) for _, path in inputs if not path.is_file()]
    if missing:
        print("missing input(s): " + ", ".join(missing), file=sys.stderr)
        return 2

    if args.dry_run:
        print("read-only dry run")
        for label, path in inputs:
            print(f"{label}\t{path}")
        print(f"output\t{args.output}")
        return 0

    if args.output.exists():
        print(f"refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 3
    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for label, path in inputs:
        _, _, blocks = parse_file(path)
        pattern = FOCUS_PATTERNS[label]
        for block in blocks:
            if pattern.match(block.method_name):
                rows.append(row_for(block, label))

    rows.sort(
        key=lambda row: (
            row["artifact"],
            int(row["artifact_line"]),
            int(row["dex_method_index"]),
        )
    )
    fieldnames = list(rows[0].keys()) if rows else ["artifact"]
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
