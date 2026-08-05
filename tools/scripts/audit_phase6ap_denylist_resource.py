#!/usr/bin/env python3
"""Close the PS7331 PackageManagerDenyList resource provenance, host-only.

The script reads the preserved PS7331 system image with the local ``debugfs``
binary, extracts only the fireos-res APK, and parses its resource table and
deny-list JSON.  It never mounts or writes the image, contacts ADB, executes
Android code, or modifies a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "firmware/extracted/PS7331/system.img"
DEFAULT_DEBUGFS = Path("/opt/homebrew/opt/e2fsprogs/sbin/debugfs")
DEFAULT_OUTPUT = ROOT / "artifacts/phase6ap/denylist-resource-closure-20260805-01"

IMAGE_PATHS = {
    "fireos_res_apk": "/system/framework/fireos-res/fireos-res.apk",
}
TARGET_IDS = (0x7E05000A, 0x7E060058)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def decode_length(data: bytes, offset: int) -> tuple[int, int]:
    value = data[offset]
    offset += 1
    if value & 0x80:
        value = ((value & 0x7F) << 8) | data[offset]
        offset += 1
    return value, offset


def string_pool(data: bytes, base: int) -> list[str]:
    chunk_type = u16(data, base)
    if chunk_type != 0x0001:
        raise ValueError(f"expected string pool at 0x{base:x}, got 0x{chunk_type:x}")
    header_size = u16(data, base + 2)
    count = u32(data, base + 8)
    flags = u32(data, base + 16)
    strings_start = u32(data, base + 20)
    offsets = [u32(data, base + header_size + index * 4) for index in range(count)]
    utf8 = bool(flags & 0x100)
    result: list[str] = []
    for relative in offsets:
        cursor = base + strings_start + relative
        if utf8:
            _, cursor = decode_length(data, cursor)
            byte_length, cursor = decode_length(data, cursor)
            result.append(data[cursor:cursor + byte_length].decode("utf-8", "replace"))
        else:
            character_length = u16(data, cursor)
            result.append(data[cursor + 2:cursor + 2 + character_length * 2].decode("utf-16le", "replace"))
    return result


def resource_entries(data: bytes) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return package metadata and all resource key entries from resources.arsc."""
    if u16(data, 0) != 0x0002:
        raise ValueError("not an Android resource table")
    packages: list[dict[str, object]] = []
    entries: list[dict[str, object]] = []
    table_end = u32(data, 4)
    # The table header is 12 bytes; the first child starts after it.
    cursor = 12
    while cursor + 8 <= table_end:
        chunk_type = u16(data, cursor)
        header_size = u16(data, cursor + 2)
        chunk_size = u32(data, cursor + 4)
        if chunk_size < 8:
            break
        if chunk_type == 0x0200:
            package_id = u32(data, cursor + 8)
            package_name = data[cursor + 12:cursor + 268].decode("utf-16le", "replace").split("\0", 1)[0]
            type_strings_offset = u32(data, cursor + 0x10C)
            key_strings_offset = u32(data, cursor + 0x114)
            type_id_offset = u32(data, cursor + 0x11C)
            types = string_pool(data, cursor + type_strings_offset)
            keys = string_pool(data, cursor + key_strings_offset)
            package = {
                "package_id": package_id,
                "package_name": package_name,
                "offset": cursor,
                "size": chunk_size,
                "type_id_offset": type_id_offset,
            }
            packages.append(package)
            package_end = cursor + chunk_size
            child = cursor + header_size
            while child + 8 <= package_end:
                child_type = u16(data, child)
                child_header = u16(data, child + 2)
                child_size = u32(data, child + 4)
                if child_size < 8:
                    break
                if child_type == 0x0201:
                    type_id = data[child + 8] + type_id_offset
                    entry_count = u32(data, child + 12)
                    entries_start = u32(data, child + 16)
                    type_name = types[type_id - 1 - type_id_offset] if 0 < type_id - type_id_offset <= len(types) else "?"
                    for entry_id in range(entry_count):
                        offset = u32(data, child + child_header + entry_id * 4)
                        if offset == 0xFFFFFFFF:
                            continue
                        entry_offset = child + entries_start + offset
                        if entry_offset + 8 > len(data):
                            continue
                        key_index = u32(data, entry_offset + 4)
                        key_name = keys[key_index] if key_index < len(keys) else "?"
                        resource_id = (package_id << 24) | (type_id << 16) | entry_id
                        entries.append({
                            "resource_id": resource_id,
                            "package_id": package_id,
                            "package_name": package_name,
                            "type_id": type_id,
                            "type_name": type_name,
                            "entry_id": entry_id,
                            "entry_name": key_name,
                        })
                child += child_size
            cursor = package_end
            continue
        cursor += chunk_size
    return packages, entries


def write_text(path: Path, text: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--debugfs", type=Path, default=DEFAULT_DEBUGFS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "image_written": False,
            "debugfs_mode": "read-only dump command only",
            "image": str(args.image),
            "debugfs": str(args.debugfs),
            "output": str(args.output),
            "paths": IMAGE_PATHS,
        }, indent=2))
        return 0

    for path in (args.image, args.debugfs):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    commands: list[dict[str, object]] = []
    extracted: dict[str, Path] = {}
    for label, image_path in IMAGE_PATHS.items():
        destination = args.output / f"{label}.apk"
        command = [str(args.debugfs), "-R", f"dump {image_path} {destination}", str(args.image)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        commands.append({
            "label": label,
            "image_path": image_path,
            "argv": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
        if result.returncode != 0 or not destination.is_file():
            raise SystemExit(f"debugfs dump failed for {image_path}: {result.stderr}")
        extracted[label] = destination

    apk = extracted["fireos_res_apk"]
    with zipfile.ZipFile(apk) as archive:
        resources = archive.read("resources.arsc")
        deny_json = archive.read("res/raw/package_manager_deny_list.json")
        raw_name = "res/raw/package_manager_deny_list.json"
    packages, entries = resource_entries(resources)
    entry_by_id = {int(item["resource_id"]): item for item in entries}
    targets = [entry_by_id.get(resource_id) for resource_id in TARGET_IDS]
    if any(item is None for item in targets):
        missing = [hex(resource_id) for resource_id, item in zip(TARGET_IDS, targets) if item is None]
        raise SystemExit("resource IDs not found: " + ", ".join(missing))

    deny_data = json.loads(deny_json.decode("utf-8"))
    denied_packages = deny_data.get("packages_deny_list", [])
    fire_launcher_present = "com.amazon.firelauncher" in denied_packages
    if not fire_launcher_present:
        raise SystemExit("com.amazon.firelauncher is absent from package_manager_deny_list.json")

    write_text(args.output / raw_name, deny_json.decode("utf-8"))
    write_text(args.output / "debugfs-commands.json", json.dumps(commands, indent=2) + "\n")
    write_text(args.output / "resource-table-targets.json", json.dumps(targets, indent=2, sort_keys=True) + "\n")
    write_text(args.output / "package-table.json", json.dumps(packages, indent=2, sort_keys=True) + "\n")
    write_text(args.output / "input-sha256.json", json.dumps({
        "system_image": {"path": str(args.image), "sha256": sha256(args.image), "size": args.image.stat().st_size},
        "fireos_res_apk": {"path": str(apk), "sha256": sha256(apk), "size": apk.stat().st_size},
    }, indent=2, sort_keys=True) + "\n")

    table_path = ROOT / "output/tables/phase6ap-denylist-resource.csv"
    if table_path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {table_path}")
    table_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in targets:
        rows.append({
            "resource_id": f"0x{int(item['resource_id']):08x}",
            "package_id": f"0x{int(item['package_id']):02x}",
            "package_name": item["package_name"],
            "type_id": item["type_id"],
            "type_name": item["type_name"],
            "entry_id": item["entry_id"],
            "entry_name": item["entry_name"],
            "apk_path": "/system/framework/fireos-res/fireos-res.apk",
            "content_observation": raw_name if item["entry_name"] == "package_manager_deny_list" else "resource-table-name-only",
            "confidence": "Confirmed",
        })
    with table_path.open("x", newline="", encoding="utf-8") as stream:
        fields = list(rows[0].keys())
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "image_mounted": False,
        "image_written": False,
        "debugfs_operation": "read-only dump",
        "system_image_sha256": sha256(args.image),
        "resource_package": targets[0]["package_name"],
        "resource_package_id": "0x%02x" % targets[0]["package_id"],
        "target_resources": targets,
        "deny_json_path": raw_name,
        "deny_package_count": len(denied_packages),
        "fire_launcher_in_deny_list": fire_launcher_present,
        "deny_list_members": denied_packages,
        "verdict": "PS7331 system image maps 0x7e05000a to amazon.fireos:raw/package_manager_deny_list; the raw JSON explicitly contains com.amazon.firelauncher.",
        "limitations": [
            "This closes resource provenance and package membership, not every runtime caller or every possible future resource replacement path.",
            "The image was read through debugfs dump; it was never mounted read-write or modified.",
            "No Android code, Binder transaction, updater, recovery, or device mutation was performed.",
        ],
    }
    write_text(args.output / "summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n")

    artifact_files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    write_text(args.output / "sha256sums.txt", "".join(
        f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in artifact_files
    ))

    report = f"""# Phase 6AP — PS7331 PackageManagerDenyList resource closure

Generated: {summary['generated_at_utc']}

## Safety boundary

This is a host-only read of the preserved PS7331 `system.img` using `debugfs
dump`. The image was not mounted or written. No ADB command, Binder call,
Android process, OTA/updater, recovery, or package-state mutation was used.

## 已證實

1. The preserved PS7331 system image contains
   `/system/framework/fireos-res/fireos-res.apk`; its resource table declares
   package ID `0x7e` with package name `amazon.fireos`.
2. Resource ID `0x7e05000a` resolves exactly to
   `amazon.fireos:raw/package_manager_deny_list`.
3. `res/raw/package_manager_deny_list.json` contains
   `com.amazon.firelauncher` in its `packages_deny_list` array.
4. Resource ID `0x7e060058` resolves exactly to
   `amazon.fireos:string/config_amzpackagemanager_denyListArcusId`.
5. This closes the previously unresolved resource provenance in the static
   chain:

```text
Resources.getSystem().openRawResource(0x7e05000a)
  → amazon.fireos:raw/package_manager_deny_list
  → JSON key packages_deny_list
  → com.amazon.firelauncher membership
  → PackageManagerDenyList seed
  → ControlProtectedPackagesCallback
  → enabled-state rejection before mutation
```

Evidence: `6AP-RSRC-001` through `6AP-RSRC-005`.

## 高可信推論

The Fire Launcher rejection is now supported by both sides of the chain:
the runtime/static consumer in `fosservices` and the exact PS7331 resource
that seeds the deny-list. This is stronger than inferring membership from the
error message alone. It still does not claim that every protected-package
operation shares identical code or that the resource can be changed by shell.

## 已排除／因風險拒絕

- **已排除：** treating `0x7e05000a` as an unresolved or generic AOSP resource
  for this PS7331 image.
- **因風險拒絕：** modifying the resource, remounting system, changing the
  deny-list, invoking unknown Binder transactions, disabling Fire Launcher,
  executing OTA/recovery, root, or writing any partition.

## Reproduction

```sh
python3 tools/scripts/audit_phase6ap_denylist_resource.py --dry-run
python3 tools/scripts/audit_phase6ap_denylist_resource.py \\
  --image firmware/extracted/PS7331/system.img \\
  --output artifacts/phase6ap/denylist-resource-closure-20260805-01
```

The extracted APK, raw JSON, resource-table mapping, input hash, debugfs
commands, summary and SHA-256 manifest are in the canonical artifact.
"""
    write_text(ROOT / "findings/phase-6ap-denylist-resource-closure.md", report)

    evidence = """# Phase 6AP evidence index

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AP-RSRC-001` | PS7331 `system.img` debugfs inventory/dump | `/system/framework/fireos-res/fireos-res.apk` exists in the matched system image | Confirmed |
| `6AP-RSRC-002` | `fireos-res.apk` `resources.arsc` | Package ID `0x7e` is named `amazon.fireos` | Confirmed |
| `6AP-RSRC-003` | `resources.arsc` resource map | `0x7e05000a` is `raw/package_manager_deny_list` | Confirmed |
| `6AP-RSRC-004` | `package_manager_deny_list.json` | `com.amazon.firelauncher` is an explicit deny-list member | Confirmed |
| `6AP-RSRC-005` | `resources.arsc` resource map | `0x7e060058` is `string/config_amzpackagemanager_denyListArcusId` | Confirmed |
| `6AP-RSRC-006` | Existing `fosservices` consumer + new resource closure | Resource seed and protected-package consumer form a closed static chain | Strong evidence |

Device contact: none in this static phase. The separate read-only live capture
is `adb/phase6ao/PHASE6AO-RO-20260805-01/`.
"""
    write_text(ROOT / "findings/phase-6ap-evidence-index.md", evidence)
    print(json.dumps({
        "output": str(args.output),
        "resource_ids": [f"0x{int(item['resource_id']):08x}" for item in targets],
        "fire_launcher_in_deny_list": fire_launcher_present,
        "host_only": True,
        "device_contacted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
