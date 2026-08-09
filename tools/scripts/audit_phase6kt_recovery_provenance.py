#!/usr/bin/env python3
"""Host-only audit of the PS7331 recovery/updater provenance boundary.

This script never executes an updater, recovery binary, APK, OTA package, or
device command. It reads preserved source/decompilation artifacts, hashes the
inputs, records selected source-line markers, and reports fixed partition
targets visible in the preserved updater script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def line_markers(path: Path, patterns: Iterable[str]) -> List[Dict[str, object]]:
    wanted = [(pattern, re.compile(pattern, re.IGNORECASE)) for pattern in patterns]
    results: List[Dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        for pattern, compiled in wanted:
            if compiled.search(line):
                results.append({"line": line_number, "pattern": pattern, "text": line.strip()})
    return results


def binary_markers(path: Path, patterns: Iterable[bytes]) -> List[Dict[str, object]]:
    data = path.read_bytes()
    results: List[Dict[str, object]] = []
    for pattern in patterns:
        offset = data.find(pattern)
        results.append({"pattern": pattern.decode("ascii", "replace"), "offset": offset})
    return results


def resolve(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Directory for audit.json and sha256sums.txt (default: artifacts/phase6kt/...)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "artifacts/phase6kt/recovery-verifier-audit-20260810-01").resolve()
    output.mkdir(parents=True, exist_ok=True)

    inputs = {
        "recovery_wrapper": "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/android/os/RecoverySystemWrapper.java",
        "sideload_verifier": "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadVerifier.java",
        "os_update_validator": "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/software/ota/tasks/validate/OSUpdateValidator.java",
        "sideload_mover": "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java",
        "sideload_installer": "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadInstaller.java",
        "update_system_wrapper": "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/framework/UpdateSystemWrapper.java",
        "update_binary": "firmware/extracted/PS7331/META-INF/com/google/android/update-binary",
        "updater_script": "firmware/extracted/PS7331/META-INF/com/google/android/updater-script",
        "ota_certificate": "artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/otacert.pem",
    }
    paths = {name: resolve(root, relative) for name, relative in inputs.items()}

    source_patterns = {
        "recovery_wrapper": [r"RecoverySystem\.verifyPackage", r"verifyPackage"],
        "sideload_verifier": [r"verifySideloadMetadata", r"verifySideloadPackage", r"verifySideloadWithRecoveryCheck", r"mRecoverySystemWrapper"],
        "os_update_validator": [r"assertRecoverySystemVerifiesPackage", r"verifyPackage", r"assertHash", r"assertUpdatePropertiesValid"],
        "sideload_mover": [r"getAbsolutePath", r"split\(\"/\"\)", r"moveFile", r"getExternalDataDirectory", r"canonical", r"NOFOLLOW"],
        "sideload_installer": [r"verifySideloadWithoutRecoveryCheck", r"maybeMoveSideloadFile", r"mUpdateSystemWrapper\.install"],
        "update_system_wrapper": [r"replaceFirst", r"persist\.sys\.ota\.isScreenOffBeforeOTA", r"UpdateSystem\.install", r"Collections\.emptyMap"],
        "updater_script": [r"block_image_update", r"package_extract_file", r"/dev/block/by-name", r"\.img"],
    }

    record: Dict[str, object] = {
        "classification": "host-only-static-provenance",
        "execution_policy": {
            "adb": False,
            "binder": False,
            "recovery": False,
            "ota_install": False,
            "native_execution": False,
            "partition_write": False,
        },
        "inputs": {},
        "source_markers": {},
        "binary_markers": {},
        "fixed_partition_targets": [],
        "findings": [
            "RecoverySystemWrapper delegates to the Android RecoverySystem verification API.",
            "The Java OTA path performs metadata/sanity and recovery verification before the update handoff.",
            "SideloadMover derives a destination from the basename; no Java canonical-path or NOFOLLOW marker was found by this bounded scan.",
            "The preserved native updater has high-privilege image-write capability, but this audit does not establish an untrusted caller or recovery provenance path.",
        ],
        "confidence": "Strong evidence",
    }

    for name, path in paths.items():
        record["inputs"][name] = {"path": str(path.relative_to(root)), "sha256": sha256(path), "size": path.stat().st_size}

    for name, patterns in source_patterns.items():
        record["source_markers"][name] = line_markers(paths[name], patterns)

    binary_patterns = [b"package_extract_file", b"block_image_verify", b"block_image_update", b"/dev/block/by-name", b"readlink", b"ota_open"]
    record["binary_markers"]["update_binary"] = binary_markers(paths["update_binary"], binary_patterns)

    target_pattern = re.compile(r"/dev/block(?:/[A-Za-z0-9_.-]+)*/by-name/[A-Za-z0-9_.-]+")
    for line_number, line in enumerate(paths["updater_script"].read_text(errors="replace").splitlines(), 1):
        for target in target_pattern.findall(line):
            record["fixed_partition_targets"].append({"line": line_number, "target": target, "text": line.strip()})

    audit_path = output / "audit.json"
    audit_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    manifest_entries = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        manifest_entries.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest_entries) + "\n")
    print(json.dumps({"output": str(audit_path), "sha256": sha256(audit_path), "input_count": len(paths)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
