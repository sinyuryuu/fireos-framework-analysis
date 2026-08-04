#!/usr/bin/env python3
"""Build a host-only GhostLock/MTK compatibility matrix.

This script reads only preserved repository evidence. It does not access ADB,
the network, device nodes, boot images, or exploit payloads. Derived files may
be regenerated; raw captures are never modified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


ROWS = [
    {"route":"CVE-2026-43499 GhostLock","layer":"Linux futex PI / rtmutex","target":"KFTRWI/trona/MT8183/PS7330.4104N","required_input":"Matching signed PS7330 Image/vmlinux, compiled layout, Android post-exploitation chain","observed":"Exact public rtmutex source matches old v4.4.146 semantics; runtime config has FUTEX and RT_MUTEXES; signed binary and runtime layout unavailable","live_action":"No futex race, kernel trigger, payload, or root stage","classification":"STRONG_EVIDENCE_SOURCE_CONFIG_ONLY","next_safe_step":"Obtain an authorized exact signed artifact and compare offline","evidence":"P5AZ-001;P5AZ-002;P5AZ-003;P5AZ-004"},
    {"route":"PS7331 compiled rtmutex reference","layer":"Adjacent Fire OS kernel image","target":"PS7331.4463N (not installed target)","required_input":"Exact-version identity before applying any inference","observed":"Old current-task pattern observed in compiled PS7331 image; version mismatch prevents PS7330 binary conclusion","live_action":"Host-only inspection; not pushed or flashed","classification":"STRONG_EVIDENCE_VERSION_MISMATCH","next_safe_step":"Use only as compiler/build-family context","evidence":"P5AZ-005"},
    {"route":"Public GhostLock Android ports","layer":"Native Android exploit implementations","target":"Pixel/modern GKI/other vendor targets","required_input":"Device-specific kernel profile, offsets, symbols, and privilege chain","observed":"Reviewed profiles do not contain KFTRWI, trona, MT8183, or 4.4.146","live_action":"Not compiled, installed, or executed","classification":"DISPROVED_AS_DIRECT_PORT","next_safe_step":"Reference only; do not reuse target headers or offsets","evidence":"P5AZ-006"},
    {"route":"KoCleo/mtk-easy-su mtk-su64","layer":"Legacy MTK bootless root wrapper","target":"Generic legacy MTK; no exact trona profile","required_input":"A payload compatible with the running CMDQ/kernel interface","observed":"Payload SHA matches the already executed MTK-SU-CMDQ-T03; direct run failed at critical init step 3 with no UID 0","live_action":"One prior exact-device run; no duplicate run","classification":"DISPROVED_FOR_THIS_PAYLOAD_BUILD","next_safe_step":"Do not rerun; require a materially different exact-target implementation","evidence":"P5AZ-007;P5AZ-008"},
    {"route":"CVE-2020-0069 / CMDQ v2 payload family","layer":"MediaTek CMDQ driver","target":"Historical v2 interface versus exact MT8183 source selecting v3","required_input":"Matching compiled driver and a separately reviewed non-destructive test plan","observed":"Existing payload uses ioctl 0x40087807; source review indicates v2/v3 interface mismatch; running binary status remains unproven","live_action":"No new ioctl, DMA, or kernel-memory operation","classification":"STRONG_EVIDENCE_PAYLOAD_MISMATCH;BINARY_STATUS_UNKNOWN","next_safe_step":"Obtain matching signed driver artifact; static compare only","evidence":"P5AZ-009"},
    {"route":"Generic mtkclient BROM/DA","layer":"Preloader/BROM/DA boot chain","target":"Amazon trona requires exact preloader, DA/auth, rollback, and recovery set","required_input":"Exact PS7330 boot-chain bundle and verified recovery path","observed":"Flash locked; exact PS7330 preloader/LK/DA/auth unavailable; only adjacent PS7331 artifacts exist","live_action":"No handshake, read, erase, unlock, or write","classification":"RISK_REJECTED_EXACT_INPUT_MISSING","next_safe_step":"Host-side documentation only until exact artifacts exist","evidence":"P5AZ-011"},
    {"route":"fenrir / LK patcher","layer":"Device-specific secure boot/LK modification","target":"Supported phones/firmware listed by each project; no trona profile","required_input":"Matching device codename image, seccfg state, rollback/auth conditions","observed":"Public support lists do not include KFTRWI/trona; PS7331 LK is VERSION_MISMATCH","live_action":"No patch, flash, seccfg, or bootloader command","classification":"DISPROVED_AS_DIRECT_ROUTE;RISK_REJECTED","next_safe_step":"Do not apply to Amazon images without exact target support","evidence":"P5AZ-012"},
    {"route":"MTK Android CVE candidates (IMS/AT/MDP/preloader)","layer":"Vendor services and boot chain","target":"Some historical bulletins mention MT8183/Android 9, but exact surface is required","required_input":"Observed service/device node plus exact vulnerable binary and permission boundary","observed":"No shell-to-IMS/AT surface; MDP/system-privilege boundary; preloader candidates version/path mismatch","live_action":"Read-only enumeration only; no Binder fuzz, AT, ioctl, or preloader test","classification":"NO_VERIFIED_SHELL_ROUTE","next_safe_step":"Acquire exact vendor binary/source mapping before further review","evidence":"P5AZ-010;P5AZ-013"},
    {"route":"CVE-2026-43503 DirtyClone","layer":"Linux skb/XFRM/ESP networking","target":"Not GhostLock; exact captured config lacks key packet-duplication/TEE path","required_input":"Exact vulnerable code path and non-destructive reachability proof","observed":"Config review does not support the documented primary path; no packet/kernel trigger","live_action":"No network exploit or kernel test","classification":"DISPROVED_AS_GHOSTLOCK_ROUTE","next_safe_step":"Keep separate from GhostLock; no live test","evidence":"P5AZ-014"},
]

EVIDENCE = [
    ("P5AZ-001", "Exact device identity", "findings/phase-5an-ghostlock-exact-target-review.md", "PS7330.4104N, KFTRWI/trona, kernel 4.4.146+, SELinux/verified-boot boundary", "Confirmed", "GhostLock target scope"),
    ("P5AZ-002", "Exact Amazon rtmutex source comparison", "artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json", "Normalized Amazon source and stable v4.4.146 hashes identical; zero diff", "Confirmed, source scope", "CVE-2026-43499 source candidate"),
    ("P5AZ-003", "Exact config and futex/rtmutex reachability", "artifacts/phase5/exact-futex-sched-review-20260804-04/kconfig-observations.tsv", "CONFIG_FUTEX=y, CONFIG_RT_MUTEXES=y, CONFIG_RANDOMIZE_BASE=y; no literal FUTEX_PI line observed", "Confirmed, runtime/config scope", "GhostLock source/config compatibility"),
    ("P5AZ-004", "Exact PS7330 boot read boundary", "adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt", "ADB shell cannot read installed boot block", "Confirmed", "Signed binary/layout missing"),
    ("P5AZ-005", "Adjacent PS7331 compiled rtmutex inspection", "findings/phase-5ar-ps7331-compiled-rtmutex-review.md", "Old current-task pattern observed, but image is PS7331 and version-mismatched", "Confirmed, version mismatch", "Context only; not PS7330 proof"),
    ("P5AZ-006", "Public GhostLock target review", "findings/phase-5o-exact-futex-sched-review.md", "Reviewed public profiles are other kernel/device generations; no trona/MT8183/4.4.146 profile", "Confirmed in bounded review", "No direct port"),
    ("P5AZ-007", "KoCleo payload identity", "artifacts/phase5/mtk-easy-su-current-review-20260804-01/repo-metadata.tsv", "mtk-su64 LFS OID matches previously executed local payload", "Confirmed", "Duplicate payload"),
    ("P5AZ-008", "Previous mtk-su result", "findings/phase-5e-mtk-su-t03-result.md", "Failed critical init step 3; exit 1; no root; rollback succeeded", "Confirmed", "Payload/build route disproved"),
    ("P5AZ-009", "CMDQ source follow-up", "findings/phase-5f-exact-cmdq-source-followup.md", "Payload ioctl #7 is associated with v2, while exact source selects v3; running binary still unknown", "Strong evidence, source scope", "Do not repeat payload"),
    ("P5AZ-010", "MTK low-level source surface", "findings/phase-5al-mtk-cve-surface-review.md", "No verified shell-to-IMS/AT route; system privilege and version boundaries remain", "Confirmed/strong evidence", "No safe public CVE route"),
    ("P5AZ-011", "BROM/boot-chain artifact boundary", "findings/phase-5ac-mtkclient-and-android-route-review.md", "No exact PS7330 preloader/LK/DA/auth bundle; flash locked", "Confirmed", "Boot-chain route not executable as evidence"),
    ("P5AZ-012", "fenrir/lkpatcher target boundary", "findings/phase-5r-mtk-root-route-review.md", "No trona support; exact LK unavailable; no patch/write", "Confirmed", "No direct route"),
    ("P5AZ-013", "Historical MTK Android CVE triage", "findings/phase-5al-mtk-cve-surface-review.md", "Candidate bulletins do not form an observed shell-to-root path", "Strong evidence", "No live trigger"),
    ("P5AZ-014", "DirtyClone identity/config boundary", "findings/phase-5u-android-cve-applicability.md", "CVE-2026-43503 is separate from GhostLock; key captured config path is not established", "Confirmed identity; applicability unproven", "No live test"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--evidence-index", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    table_path = (args.output_dir or root / "output/tables") / "phase5az-root-route-matrix.csv"
    evidence_path = args.evidence_index or root / "findings/phase-5az-evidence-index.md"

    if args.dry_run:
        print(f"would write {table_path}")
        print(f"would write {evidence_path}")
        print(f"rows={len(ROWS)} evidence={len(EVIDENCE)}")
        return 0

    table_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ROWS[0])
    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ROWS)

    lines = [
        "# Phase 5AZ evidence index — GhostLock and MTK compatibility",
        "",
        "This index is generated by `tools/scripts/build_phase5az_compatibility_matrix.py`.",
        "The generator is host-only and does not access ADB, the network, device nodes, boot images, or payloads.",
        "",
        "| Evidence ID | Source | File | SHA-256 | Observed result | Confidence | Related question |",
        "|---|---|---|---|---|---|---|",
    ]
    for evidence_id, source, relpath, result, confidence, question in EVIDENCE:
        path = root / relpath
        file_hash = sha256(path) if path.is_file() else "NOT_A_SINGLE_FILE"
        lines.append(f"| {evidence_id} | {source} | `{relpath}` | `{file_hash}` | {result} | {confidence} | {question} |")
    lines.extend([
        "",
        "## Classification vocabulary",
        "",
        "- `Confirmed`: directly shown by the cited artifact within its stated scope.",
        "- `Strong evidence`: repeatable source/config or prior exact-device observation, not binary exploit proof.",
        "- `Unknown`: exact signed artifact or runtime behavior is unavailable.",
        "- `Disproved`: the specific payload/route is ruled out by the cited target or prior result.",
        "- `Risk rejected`: no live boot-chain or kernel-trigger operation was performed.",
    ])
    evidence_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {table_path}")
    print(f"wrote {evidence_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
