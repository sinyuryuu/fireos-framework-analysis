#!/usr/bin/env python3
"""Host-only, deterministic audit of Amazon's amzn_drv_test source.

The input is an Amazon GPL source ``platform.tar`` archive.  The script reads
only four source members, extracts no files, executes no source code, and does
not communicate with an Android device.  It emits a compact report, a CSV
evidence table, a Mermaid source graph, and hashes for the selected inputs and
outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import tarfile
from pathlib import Path


MEMBERS = {
    "driver": "device/amazon/kernel/driver/amzn_drv_test.c",
    "kconfig": "device/amazon/kernel/driver/Kconfig",
    "makefile": "device/amazon/kernel/driver/Makefile",
    "defconfig": "kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_members(archive: Path) -> dict[str, bytes]:
    wanted = set(MEMBERS.values())
    found: dict[str, bytes] = {}
    with tarfile.open(archive, mode="r:") as tar:
        for member in tar:
            if member.name not in wanted:
                continue
            handle = tar.extractfile(member)
            if handle is None:
                raise RuntimeError(f"member is not a regular readable file: {member.name}")
            found[member.name] = handle.read()
            if len(found) == len(wanted):
                break
    missing = wanted - set(found)
    if missing:
        raise FileNotFoundError("missing archive members: " + ", ".join(sorted(missing)))
    return found


def lines(text: str, pattern: str) -> list[int]:
    rx = re.compile(pattern)
    return [number for number, value in enumerate(text.splitlines(), 1) if rx.search(value)]


def line_value(text: str, line_number: int) -> str:
    values = text.splitlines()
    return values[line_number - 1].strip() if 0 < line_number <= len(values) else ""


def evidence_rows(texts: dict[str, str]) -> list[dict[str, str]]:
    driver = texts["driver"]
    kconfig = texts["kconfig"]
    makefile = texts["makefile"]
    defconfig = texts["defconfig"]

    rows: list[dict[str, str]] = []

    def add(evidence: str, source: str, pattern: str, interpretation: str) -> None:
        hits = lines(texts[source], pattern)
        rows.append({
            "evidence_id": evidence,
            "source_member": MEMBERS[source],
            "line": ",".join(map(str, hits)) if hits else "NOT_FOUND",
            "matched": " | ".join(line_value(texts[source], hit) for hit in hits[:4]) if hits else "",
            "interpretation": interpretation,
        })

    add("6NB-S01", "kconfig", r"^config AMZN_DRV_TEST$",
        "Kconfig declares the test-driver option.")
    add("6NB-S02", "kconfig", r"^\s*depends on AMZN_METRICS_LOG",
        "The option depends on metrics logging, sign-of-life, and IDME options.")
    add("6NB-S03", "makefile", r"amzn_drv_test\.o",
        "The object is conditionally mapped from CONFIG_AMZN_DRV_TEST.")
    add("6NB-S04", "defconfig", r"CONFIG_AMZN_DRV_TEST",
        "The selected trona_defconfig either selects or omits the test option.")
    add("6NB-S05", "driver", r'AMZN_DRIVERS\s+"amzn_drvs"',
        "The source names the proc root amzn_drvs.")
    add("6NB-S06", "driver", r"proc_mkdir\(AMZN_DRIVERS",
        "Initialization creates the intended /proc/amzn_drvs root when present.")
    add("6NB-S07", "driver", r"proc_create_data",
        "Three child proc entries are wired through the shared file operations.")
    add("6NB-S08", "driver", r"\.write\s*=\s*proc_write",
        "The shared proc file operations expose a write callback.")
    add("6NB-S09", "driver", r'sscanf\(input,\s*"%d"',
        "The source parses one decimal index, subject to the surrounding length and copy checks.")
    add("6NB-S10", "driver", r"sign_of_life_test|idme_test|logger_test",
        "The dispatch and test bodies are present in source; runtime reachability is not implied.")
    add("6NB-S11", "driver", r"S_IRUGO\|S_IWUSR",
        "The source requests owner read/write and group/other read for child entries.")
    return rows


def write_report(output: Path, archive: Path, hashes: dict[str, str], texts: dict[str, str], rows: list[dict[str, str]]) -> Path:
    report = output / "phase6nb-amzn-drv-test-source-closure.md"
    kconfig = texts["kconfig"].splitlines()
    makefile = texts["makefile"].splitlines()
    defconfig = texts["defconfig"].splitlines()
    selected = [line.strip() for line in defconfig if "CONFIG_AMZN" in line and "CONFIG_AMZN_DRV_TEST" not in line]
    drv_lines = len(texts["driver"].splitlines())
    kconfig_hits = ", ".join(str(row["line"]) for row in rows if row["evidence_id"] == "6NB-S01")
    make_hits = ", ".join(str(row["line"]) for row in rows if row["evidence_id"] == "6NB-S03")
    def_hits = ", ".join(str(row["line"]) for row in rows if row["evidence_id"] == "6NB-S04")
    body = f"""# Phase 6NB — `amzn_drv_test.c` host-only source closure

Date: 2026-08-10
Classification: host-only static evidence; no device mutation

## Scope

This report reads four members from the Amazon GPL `platform.tar` stream. It
does not extract the archive, execute source code, access `/proc` on the
tablet, call Binder or ioctl, install an APK, reboot, modify a partition, or
attempt root. A source test label mentioning OTA, factory reset, or reboot is
not treated as proof that the corresponding path exists or is reachable on the
retail build.

Archive: `{archive}`
Archive SHA-256: `{hashes['archive']}`
Driver source lines: `{drv_lines}`

## Selected member hashes

| Member | SHA-256 |
|---|---|
| `{MEMBERS['driver']}` | `{hashes['driver']}` |
| `{MEMBERS['kconfig']}` | `{hashes['kconfig']}` |
| `{MEMBERS['makefile']}` | `{hashes['makefile']}` |
| `{MEMBERS['defconfig']}` | `{hashes['defconfig']}` |

## Findings

### Confirmed source facts

* `Kconfig` declares `AMZN_DRV_TEST` (line(s) {kconfig_hits}) with dependencies
  on the Amazon metrics, sign-of-life, and IDME options.
* `Makefile` maps `CONFIG_AMZN_DRV_TEST` to `amzn_drv_test.o`
  (line(s) {make_hits}).
* The driver names the proc root `amzn_drvs`, creates the three intended child
  names `sign_of_life`, `idme`, and `logger`, and uses the shared `test_fops`
  with a write callback. The source requests `S_IRUGO|S_IWUSR` for those
  entries.
* The write path bounds the input, copies it, parses a decimal index, and
  dispatches to the corresponding test routine. The exact branch bodies and
  line references are in the evidence CSV.

### Strong negative configuration signal

`trona_defconfig` contains the Amazon parent/dependency selections:

```text
{chr(10).join(selected)}
```

It has no `CONFIG_AMZN_DRV_TEST=y` or `CONFIG_AMZN_DRV_TEST=m` line
({def_hits}). This is evidence about that defconfig only; it does not close
generated `.config` files, product overlays, module packaging, or another
product configuration.

### Not established

The archive-only evidence does not establish Kconfig parent inclusion in the
final build, generated configuration, whether the object is built or loaded,
whether `/proc/amzn_drvs` exists on the device, effective ownership/mode,
SELinux labeling, caller permissions, a userspace caller, vulnerability,
exploitability, or privilege escalation.

## Reproduction

```text
python3 -B tools/scripts/audit_phase6nb_amzn_drv_test_source.py \\
  --archive firmware/extracted/PS7331-SOURCE-20250617/platform.tar \\
  --output artifacts/phase6nb-amzn-drv-test-source-closure-YYYYMMDD-NN
sha256sum -c artifacts/phase6nb-amzn-drv-test-source-closure-YYYYMMDD-NN/sha256sums.txt
```

## Evidence classification

| Evidence | Meaning | Confidence |
|---|---|---|
| 6NB-S01..S11 | Source member content and line-local wiring | Confirmed |
| `trona_defconfig` omission | Negative evidence for this named defconfig | Strong evidence |
| Final image/procfs/SELinux/runtime behavior | Not present in this phase | Unknown |
"""
    report.write_text(body, encoding="utf-8")
    return report


def write_csv(output: Path, rows: list[dict[str, str]]) -> Path:
    path = output / "phase6nb-amzn-drv-test-source.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["evidence_id", "source_member", "line", "matched", "interpretation"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_graph(output: Path) -> Path:
    path = output / "phase6nb-amzn-drv-test-source.mmd"
    path.write_text("""flowchart TD
  K[Kconfig: CONFIG_AMZN_DRV_TEST] --> M[Makefile: amzn_drv_test.o]
  M --> I[driver init]
  I --> R[/proc/amzn_drvs]
  R --> S[/proc/amzn_drvs/sign_of_life]
  R --> D[/proc/amzn_drvs/idme]
  R --> L[/proc/amzn_drvs/logger]
  S --> F[test_fops.write -> proc_write]
  D --> F
  L --> F
  F --> P[parse decimal index]
  P --> T[dispatch to source test routine]
  C[trona_defconfig: dependencies selected; AMZN_DRV_TEST absent] -. negative config evidence .-> K
  X[Final image, procfs, SELinux, caller and runtime] -. unproven .-> R
""", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.archive.is_file():
        parser.error(f"archive not found: {args.archive}")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error(f"refusing to overwrite non-empty output: {args.output}")
    args.output.mkdir(parents=True, exist_ok=True)

    raw = load_members(args.archive)
    texts = {key: raw[path].decode("utf-8", errors="replace") for key, path in MEMBERS.items()}
    hashes = {"archive": sha256_file(args.archive)}
    hashes.update({key: sha256_bytes(raw[path]) for key, path in MEMBERS.items()})
    rows = evidence_rows(texts)
    report = write_report(args.output, args.archive, hashes, texts, rows)
    table = write_csv(args.output, rows)
    graph = write_graph(args.output)

    manifest = args.output / "sha256sums.txt"
    input_manifest = args.output / "input-evidence-sha256sums.txt"
    outputs = [report, table, graph]
    with manifest.open("w", encoding="utf-8") as stream:
        for path in outputs:
            stream.write(f"{sha256_file(path)}  {path.name}\n")
    with input_manifest.open("w", encoding="utf-8") as stream:
        stream.write(f"archive_sha256 {hashes['archive']}  {args.archive.resolve()}\n")
        for key, path in MEMBERS.items():
            stream.write(f"member_{key}_sha256 {hashes[key]}  {path}\n")
    print(f"archive_sha256={hashes['archive']}")
    for path in outputs + [manifest, input_manifest]:
        print(f"wrote={path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
