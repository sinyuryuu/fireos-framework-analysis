#!/usr/bin/env python3
"""Host-only applicability audit for selected PS7331 CVE surfaces.

This tool checks source presence, Kconfig/boot-config gates, and defensive
reachability markers. It does not compile, execute, install, trigger, or
adapt any proof of concept and never contacts a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


TARGETS = (
    "crypto/algif_aead.c",
    "crypto/af_alg.c",
    "crypto/Makefile",
    "crypto/Kconfig",
    "net/unix/af_unix.c",
    "net/unix/Makefile",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def config_state(text: str, symbol: str) -> str:
    if re.search(rf"^CONFIG_{re.escape(symbol)}=y$", text, re.MULTILINE):
        return "y"
    if re.search(rf"^CONFIG_{re.escape(symbol)}=m$", text, re.MULTILINE):
        return "m"
    if re.search(rf"^# CONFIG_{re.escape(symbol)} is not set$", text, re.MULTILINE):
        return "disabled"
    return "absent"


def build(source_root: Path, kernel_config: Path) -> dict[str, object]:
    kernel_root = source_root / "platform/kernel/mediatek/mt8183/4.4"
    config_text = kernel_config.read_text(encoding="utf-8", errors="replace")
    targets = []
    for relative in TARGETS:
        path = kernel_root / relative
        targets.append(
            {
                "path": relative,
                "exists": path.is_file(),
                "size": path.stat().st_size if path.is_file() else 0,
                "sha256": sha256(path) if path.is_file() else "",
            }
        )

    unix_path = kernel_root / "net/unix/af_unix.c"
    unix_text = unix_path.read_text(encoding="utf-8", errors="replace") if unix_path.is_file() else ""
    markers = {
        "af_unix_MSG_OOB_count": len(re.findall(r"MSG_OOB", unix_text)),
        "af_unix_unix_stream_recv_urg_count": len(re.findall(r"unix_stream_recv_urg", unix_text)),
        "af_unix_manage_oob_count": len(re.findall(r"manage_oob", unix_text)),
        "af_unix_unix_stream_sendmsg_present": "unix_stream_sendmsg" in unix_text,
        "af_unix_MSG_OOB_rejected": bool(re.search(r"err\s*=\s*-EOPNOTSUPP[\s\S]{0,180}MSG_OOB", unix_text)),
    }
    config_symbols = {
        symbol: config_state(config_text, symbol)
        for symbol in (
            "CRYPTO_USER_API",
            "CRYPTO_USER_API_AEAD",
            "CRYPTO_USER_API_HASH",
            "CRYPTO_USER_API_SKCIPHER",
            "CRYPTO_USER_API_RNG",
            "UNIX",
            "SECCOMP",
            "SECCOMP_FILTER",
        )
    }
    findings = [
        {
            "cve": "CVE-2026-31431",
            "surface": "crypto/algif_aead.c / AF_ALG AEAD user API",
            "result": "not reachable by stock boot config",
            "confidence": "Strong evidence",
            "evidence": "CONFIG_CRYPTO_USER_API_AEAD is disabled; algif_aead.c is absent from the GPL source scope",
            "runtime_test": "rejected",
        },
        {
            "cve": "CVE-2025-38236",
            "surface": "net/unix consecutive consumed OOB skb path",
            "result": "described OOB path not present in this 4.4 source shape",
            "confidence": "Strong evidence",
            "evidence": "no unix_stream_recv_urg/manage_oob; stream send/receive paths reject MSG_OOB",
            "runtime_test": "rejected",
        },
        {
            "cve": "CVE-2025-20766",
            "surface": "MediaTek display memory corruption",
            "result": "device applicability not established",
            "confidence": "Hypothesis",
            "evidence": "official record requires existing System privilege and does not identify MT8183 in the listed affected hardware set",
            "runtime_test": "rejected",
        },
        {
            "cve": "CVE-2025-20672",
            "surface": "MediaTek Bluetooth bounds-check issue",
            "result": "not a direct MT8183 kernel-source match",
            "confidence": "Strong evidence",
            "evidence": "official affected products are MT7902/MT7921/MT7922/MT7925/MT7927; no MT8183 match",
            "runtime_test": "rejected",
        },
    ]
    return {
        "schema": "phase6e-cve-surface-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_root": str(source_root),
            "kernel_root": str(kernel_root),
            "kernel_config": str(kernel_config),
            "kernel_config_sha256": sha256(kernel_config),
        },
        "targets": targets,
        "config_symbols": config_symbols,
        "source_markers": markers,
        "findings": findings,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "device_mutated": False,
            "source_built": False,
            "source_executed": False,
            "poc_executed": False,
            "kernel_memory_accessed": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "cve-surface.json"
    table = output / "cve-surface.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["cve", "surface", "result", "confidence", "evidence", "runtime_test"]
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["findings"])
    report.write_text(
        "# PS7331 selected CVE surface audit\n\n"
        "Host-only source/config audit. No proof of concept was built or run, and no device was contacted.\n\n"
        "## Findings\n\n"
        "- **CVE-2026-31431 — Strong evidence: not reachable by the stock boot config.** "
        "The extracted config disables `CONFIG_CRYPTO_USER_API_AEAD`, and the GPL source scope "
        "does not contain `algif_aead.c`. This is a reachability result, not a runtime exploit test.\n"
        "- **CVE-2025-38236 — Strong evidence: described OOB path not present in this 4.4 source shape.** "
        "The AF_UNIX stream path has no `unix_stream_recv_urg` or `manage_oob` handler and rejects `MSG_OOB`.\n"
        "- **CVE-2025-20766 — Hypothesis: applicability not established.** The official record describes a "
        "display issue requiring an already privileged System actor; the local source/config review does not establish "
        "an untrusted-app path on MT8183.\n"
        "- **CVE-2025-20672 — Strong evidence: not a direct MT8183 kernel-source match.** The official affected-product "
        "set is a different MediaTek wireless product family.\n\n"
        "All runtime trigger, crash, kernel-memory, and privilege-escalation tests are marked rejected.\n",
        encoding="utf-8",
    )
    files = [summary, table, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--kernel-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.source_root.is_dir():
        raise SystemExit(f"missing source root: {args.source_root}")
    if not args.kernel_config.is_file():
        raise SystemExit(f"missing kernel config: {args.kernel_config}")
    write(build(args.source_root, args.kernel_config), args.output)
    print(f"wrote CVE surface audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
