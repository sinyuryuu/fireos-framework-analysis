#!/usr/bin/env python3
"""Build a host-only Android/MediaTek AEE implementation map.

This analyzer consumes already captured exact-device artifacts and local source
excerpts.  It does not access ADB, unpack an image, open a device node, or
download/execute third-party code.  The public MediaTek implementation URLs
are recorded as provenance in the generated report rather than fetched here.
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def first_match(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.I | re.M)
    return match.group(0).strip() if match else ""


def required(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"missing required input: {path}")


def build(args: argparse.Namespace) -> None:
    runtime = ROOT / args.runtime_dir
    exact = ROOT / args.exact_source_dir
    out = ROOT / args.output
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing output: {out}")
    out.mkdir(parents=True)

    inputs = {
        "runtime_nodes": runtime / "aee_nodes.stdout.txt",
        "runtime_access": runtime / "aee_access.stdout.txt",
        "runtime_identity": runtime / "identity.stdout.txt",
        "runtime_home": runtime / "home.stdout.txt",
        "exact_defconfig": ROOT / args.defconfig,
        "exact_path_inventory": exact / "path-matches.txt",
        "phase5y_report": ROOT / "findings/phase-5y-aee-device-node-followup.md",
    }
    for path in inputs.values():
        required(path)

    nodes = read(inputs["runtime_nodes"])
    access = read(inputs["runtime_access"])
    identity = read(inputs["runtime_identity"])
    home = read(inputs["runtime_home"])
    defconfig = read(inputs["exact_defconfig"])
    paths = read(inputs["exact_path_inventory"])

    config_names = [
        line.strip()
        for line in defconfig.splitlines()
        if re.search(r"CONFIG_MTK_(?:AEE|ATF_LOGGER|MRDUMP)", line)
    ]
    access_rows = []
    for line in access.splitlines():
        match = re.match(r"(?P<node>\S+)\s+read=(?P<read>[01])\s+write=(?P<write>[01])", line)
        if match:
            access_rows.append(match.groupdict())

    rows = [
        {
            "layer": "AOSP/Android app",
            "implementation": "No generic AOSP API or APK implementation of MediaTek AEE",
            "exact_device_evidence": "No AEE app/package/service observed in Phase 5X/5Y runtime captures",
            "status": "not observed",
            "confidence": "Strong evidence, runtime-scoped",
        },
        {
            "layer": "Android init/SELinux/userspace",
            "implementation": "Public MTK branches use aee_aed/aee_aed64 or vendor AEE paths with dedicated SELinux domains/socket rules",
            "exact_device_evidence": "No exact PS7330 aee_aed process, package, service or init endpoint observed",
            "status": "analog only; exact binary unavailable",
            "confidence": "Strong evidence, public-reference plus runtime scope",
        },
        {
            "layer": "Linux/MediaTek kernel AEE",
            "implementation": "AED misc driver registers aed0 (external exception) and aed1 (kernel exception), exposes read/write/ioctl and /proc/aed reporting",
            "exact_device_evidence": "Defconfig enables MTK_AEE_FEATURE/AED/IPANIC/MRDUMP; /dev/aed0 and /dev/aed1 exist",
            "status": "present, exact control flow not extracted",
            "confidence": "Confirmed, source/config and node metadata",
        },
        {
            "layer": "SELinux/device boundary",
            "implementation": "Device nodes are labeled aed_device and require a privileged domain in the exact runtime snapshot",
            "exact_device_evidence": "root:root 0600; shell test -r/test -w returned 0/0 for aed0/aed1/atf_log",
            "status": "shell route blocked",
            "confidence": "Confirmed, exact runtime",
        },
        {
            "layer": "Boot/crash persistence",
            "implementation": "IPANIC/MRDUMP/ATF logger may feed crash collection and dump persistence",
            "exact_device_evidence": "Config flags present; no crash, reboot, dump or partition access attempted",
            "status": "configuration scope only",
            "confidence": "Strong evidence, no live trigger",
        },
    ]

    with (out / "android-aee-implementation-map.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    source_urls = [
        "https://android.googlesource.com/kernel/mediatek/+/android-4.4.4_r3/drivers/misc/mediatek/aee/aed/aed-main.c",
        "https://android.googlesource.com/kernel/mediatek/+/android-4.4.4_r3/drivers/misc/mediatek/aee/common/aee-common.c",
        "https://android.googlesource.com/device/mediatek/wembley-sepolicy/+/6f092d159878a6d57c00f2d94c32c28b735761ce%5E%21/",
        "https://nebusec.ai/research/ionstack-part-2/",
        "https://github.com/NebuSec/CyberMeowfia",
    ]
    report = f"""# Phase 5Z：Android AEE implementation review

## Scope

This is a host-only mapping of the Android/MediaTek implementation boundary.
It does not open `/dev/aed0`, `/dev/aed1`, or `/dev/atf_log`, execute an AEE
daemon, trigger a crash/race, build a root payload, or change the device.

## Exact-device inputs

- Runtime identity: `{args.runtime_dir}/identity.stdout.txt`
- AEE node metadata: `{args.runtime_dir}/aee_nodes.stdout.txt`
- Shell access check: `{args.runtime_dir}/aee_access.stdout.txt`
- Exact MT8183 defconfig excerpt: `{args.defconfig}`
- Exact source path inventory: `{args.exact_source_dir}/path-matches.txt`
- Exact source path inventory matches: `{len([line for line in paths.splitlines() if line.strip()])}`
- Analysis timestamp UTC: `{datetime.now(timezone.utc).isoformat()}`

Observed device identity excerpt:

```text
{identity.strip()}
```

HOME was captured independently and remains:

```text
{home.strip()}
```

## Android implementation map

```text
MediaTek kernel AEE API / driver
        |
        +--> misc_register(aed0)  [external exception / EE]
        |       \\--> /dev/aed0  --read/write/ioctl--> AEE userspace reader
        |
        +--> misc_register(aed1)  [kernel exception / KE]
        |       \\--> /dev/aed1  --read/write/ioctl--> AEE userspace reader
        |
        +--> /proc/aed/*          [current crash records / reports]
        |
        +--> IPANIC / MRDUMP / ATF logger persistence
        |
        `--> Android init + SELinux domain for aee_aed/aee_aed64 on some MTK branches
```

The public MediaTek Android 4.4 implementation declares two misc devices,
`aed0` and `aed1`, assigns file operations including `read`, `write`, and
`unlocked_ioctl`, and registers them from `aed_init()`. The public code also
creates `/proc/aed` reporting entries. These are kernel/vendor crash-reporting
interfaces, not a normal app permission or Android framework service.

The public SELinux references show the other half of the Android integration:
an `aee_aed`/`aee_aedv` domain, init-daemon treatment, and narrowly granted
access to AEE device/data/socket resources. Those references are analogous
MTK branches, not proof of the exact Fire OS policy or daemon binary.

## Exact Fire OS result

Defconfig AEE entries:

```text
{chr(10).join(config_names)}
```

Exact runtime node metadata contains:

```text
{nodes.strip()}
```

Shell read/write checks contain:

```text
{access.strip()}
```

The node metadata and access checks establish a root-only device boundary. They
do not establish that the AEE daemon is absent from unreadable filesystem
locations, nor do they reveal its patch status. The Phase 5X/5Y process,
package, service, and init captures did not observe an ordinary userspace AEE
endpoint.

The complete streamed archive listing finished successfully, but the
case-insensitive path filter for `aee|aed|mrdump|ipanic|aee_` returned zero
matches. This is an archive-provenance limitation, not proof that AEE code is
absent from the compiled kernel or from renamed/unpublished vendor members.

## GhostLock Android boundary

NebuSec's public article describes GhostLock as a Linux futex/rtmutex issue and
states that its Android-specific exploitation would be covered separately.
The public CyberMeowfia tree has Android/aarch64 build plumbing and target
profiles for other Google builds, but no `KFTRWI`, `trona`, `MT8183`, or
`PS7330.4104N` target in the captured tree. A target-specific header is not
portable across this tablet's kernel build, layout, KASLR, CFI/KPTI, SELinux,
and boot image.

Therefore the repository contains an Android implementation *reference map*,
not an Android root PoC for this device.

## Verdict

- **已證實：** Android-side AEE is a kernel/vendor crash-reporting boundary;
  exact Fire OS exposes root-owned `aed0`/`aed1` nodes and enables AEE-related
  config flags.
- **已證實：** the shell domain cannot read or write those nodes in the
  captured runtime; no node was opened.
- **高可信推論：** a usable Android AEE implementation, where present, would
  require a privileged daemon/domain rather than a normal sideloaded APK.
- **待驗證：** exact PS7330 AEE daemon binary, exact init/SELinux source and
  whether Amazon/MediaTek patched the daemon vulnerability.
- **已排除：** treating public MTK AEE source or another Android target's
  profile as an exact Fire root implementation.
- **因風險拒絕測試：** AEE device-node open/read/write/ioctl, malformed AEE
  message, race/crash trigger, reboot/dump generation, SELinux/property
  changes, root payloads, BROM/DA/fastboot, and partition writes.

## Public references

""" + "\n".join(f"- {url}" for url in source_urls) + "\n"
    (out / "result.md").write_text(report, encoding="utf-8")

    manifest = {
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "runtime_dir": args.runtime_dir,
        "exact_source_dir": args.exact_source_dir,
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in inputs.values()},
        "outputs": {},
        "device_operation": "none",
        "source_execution": "none",
        "web_sources": source_urls,
    }
    for path in sorted(out.iterdir()):
        if path.is_file():
            manifest["outputs"][path.name] = sha256(path)
    (out / "metadata.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with (out / "sha256sums.txt").open("w", encoding="utf-8") as fh:
        for path in sorted(out.iterdir()):
            if path.name != "sha256sums.txt":
                fh.write(f"{sha256(path)}  {path.name}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", default="adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06")
    parser.add_argument("--exact-source-dir", default="artifacts/phase5/exact-source-aee-paths-20260804-01")
    parser.add_argument("--defconfig", default="artifacts/phase5/exact-kernel-source-review-20260804-01/members/mt8183_defconfig.e1495a4e51db.txt")
    parser.add_argument("--output", default="artifacts/phase5/android-aee-implementation-review-20260804-01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print("DRY-RUN: host-only read of captured artifacts; no ADB, device-node, source execution, or network operation")
        return
    build(args)


if __name__ == "__main__":
    main()
