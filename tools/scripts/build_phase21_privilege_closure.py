#!/usr/bin/env python3
"""Normalize the Phase 21 host-only privilege-surface ledgers.

This script intentionally has no device-facing code.  It reads the five
worker CSVs produced by the Phase 21 host-only reviews and emits one common
caller -> gate -> identity/user scope -> sink table.  A record is never
promoted to a complete privilege chain merely because a capability or a
registration is present.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


FIELDS = [
    "record_id",
    "record_type",
    "surface",
    "artifact_or_entry",
    "caller",
    "gate",
    "identity_or_user_scope",
    "sink",
    "runtime_or_result",
    "missing_edge",
    "classification",
    "confidence",
    "evidence",
    "next_safe_step",
]

SOURCES = {
    "fosinit": "work/luna_worker_phase21_fosinit_20260810.csv",
    "vending": "work/luna_worker_phase21_vending_20260810.csv",
    "ion": "work/luna_worker_phase21_ion_20260810.csv",
    "denylist": "work/luna_worker_phase21_denylist_20260810.csv",
    "sink_review": "work/luna_worker_phase21_sink_review_20260810.csv",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read_rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header: {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows


def read_sink_review_rows(path: Path) -> list[dict[str, str]]:
    """Read the cross-surface CSV and repair its two unquoted comma fields.

    The worker export contains commas inside two evidence path expressions but
    does not quote those fields.  The raw CSV is preserved unchanged.  This
    parser joins the split evidence fragments only at normalization time and
    fails closed for any other unexpected shape.
    """

    expected = [
        "id",
        "status",
        "surface",
        "caller_gate_identity_sink",
        "exact_ps7331_evidence",
        "classification",
        "duplicate_or_gap",
        "disposition",
    ]
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        header = next(reader, None)
        if header != expected:
            raise ValueError(f"{path}: unexpected header {header!r}")
        rows: list[dict[str, str]] = []
        for line_number, values in enumerate(reader, 2):
            if len(values) < len(expected):
                raise ValueError(
                    f"{path}:{line_number}: too few columns ({len(values)})"
                )
            if len(values) == len(expected):
                repaired = values
            else:
                # The only tolerated extra columns are comma-split fragments
                # in the evidence field at index 4.
                extra = len(values) - len(expected)
                evidence_end = 5 + extra
                repaired = values[:4] + [",".join(values[4:evidence_end])] + values[
                    evidence_end:
                ]
                if len(repaired) != len(expected):
                    raise ValueError(
                        f"{path}:{line_number}: unsupported column shape ({len(values)})"
                    )
            rows.append(dict(zip(expected, repaired)))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows


def confidence(*values: str) -> str:
    """Map worker classifications to the project's five confidence labels."""

    value = " ".join(values).upper()
    if "BOUNDED_NEGATIVE" in value or "NEGATIVE_BOUNDARY" in value:
        return "Disproved"
    if any(
        marker in value
        for marker in (
            "UNKNOWN",
            "UNRESOLVED",
            "OPEN_EDGE",
            "CAPABILITY_ONLY",
            "DRIVER_CAPABILITY_DISCONNECTED",
            "RISK_REJECTED",
        )
    ):
        return "Hypothesis"
    if any(
        marker in value
        for marker in (
            "CONFIRMED",
            "CLOSED_HOST_STATIC",
            "CLOSED_RUNTIME_OBSERVATION",
            "EXACT_",
            "CLOSED_",
        )
    ):
        return "Confirmed"
    if any(
        marker in value
        for marker in (
            "STATIC",
            "PARTIAL",
            "POSITIVE_",
            "HIGH_",
            "BOUNDED_",
            "CAPABILITY",
        )
    ):
        return "Strong evidence"
    return "Probable"


def row(record_id: str, record_type: str, **values: str) -> dict[str, str]:
    result = {field: "" for field in FIELDS}
    result.update(record_id=record_id, record_type=record_type, **values)
    if set(result) != set(FIELDS):
        raise ValueError(f"normalized schema mismatch for {record_id}")
    return result


def normalize_fosinit(item: dict[str, str]) -> dict[str, str]:
    return row(
        item["id"],
        "fosinit",
        surface=item["registration"].split(":", 1)[0],
        artifact_or_entry=(
            f"{item['registration']} -> {item['implementation']} :: {item['entry']}"
        ),
        caller=item["caller"],
        gate=item["gate"],
        identity_or_user_scope=f"{item['identity']} | {item['user_scope']}",
        sink=item["sink"],
        runtime_or_result=item["runtime"],
        missing_edge=item["missing_edge"],
        classification=item["classification"],
        confidence=confidence(item["classification"]),
        evidence=item["evidence"],
        next_safe_step=item["next_safe_step"],
    )


def normalize_vending(item: dict[str, str]) -> dict[str, str]:
    return row(
        item["id"],
        "vending",
        surface=item["surface"],
        artifact_or_entry=item["artifact_or_path"],
        caller=item["caller"],
        gate=item["gate"],
        identity_or_user_scope=(
            "Caller/package/profile/user binding is represented only by the "
            "bounded caller text; no separate accepted identity was closed"
        ),
        sink=item["sink"],
        runtime_or_result="host-only; no broadcast, PendingIntent, Binder or device call",
        missing_edge=item["missing_edge"],
        classification=item["classification"],
        confidence=confidence(item["classification"]),
        evidence=item["evidence"],
        next_safe_step=(
            "Recover the missing caller/creator/user edge offline; do not invoke "
            "the receiver, DSE Binder, PendingIntent or settings writer"
        ),
    )


def normalize_ion(item: dict[str, str]) -> dict[str, str]:
    return row(
        item["row_id"],
        "ion",
        surface=item["edge"],
        artifact_or_entry=item["ELF_DT_NEEDED_relocation_dlopen"],
        caller=item["init_vintf_ownership"],
        gate=item["file_context_cil"],
        identity_or_user_scope=item["init_vintf_ownership"],
        sink=item["downstream_graph"],
        runtime_or_result="host-only ELF/policy graph; no /dev node operation",
        missing_edge=item["missing_edge"],
        classification=item["status"],
        confidence=confidence(item["status"], item["confidence"]),
        evidence=item["evidence"],
        next_safe_step=(
            "Join selected object/DTB and loader callsites offline; do not open, "
            "read, write or ioctl any driver node"
        ),
    )


def normalize_denylist(item: dict[str, str]) -> dict[str, str]:
    return row(
        item["reconciliation_id"],
        "denylist",
        surface=item["layer"],
        artifact_or_entry=(
            f"{item['schema_path_hash_comparison']} | {item['saved_evidence']}"
        ),
        caller="resource/persisted/runtime evidence layer; no new caller invoked",
        gate=f"can_close_from_saved_evidence={item['can_close_from_saved_evidence']}",
        identity_or_user_scope="system-owned deny-list; live literal membership is not exposed",
        sink=item["precise_result"],
        runtime_or_result=item["status"],
        missing_edge=item["remaining_boundary"],
        classification=item["status"],
        confidence=confidence(item["status"]),
        evidence=item["saved_evidence"],
        next_safe_step=item["forbidden_action"],
    )


def normalize_sink_review(item: dict[str, str]) -> dict[str, str]:
    classification = item["classification"] or "UNCLASSIFIED"
    return row(
        item["id"],
        "sink_review",
        surface=item["surface"],
        artifact_or_entry=item["exact_ps7331_evidence"],
        caller=item["caller_gate_identity_sink"],
        gate=classification,
        identity_or_user_scope=(
            "See caller_gate_identity_sink; no additional accepted identity/user "
            "edge was closed in this cross-surface review"
        ),
        sink=item["caller_gate_identity_sink"],
        runtime_or_result=(
            f"status={item['status']}; disposition={item['disposition']}"
        ),
        missing_edge=item["duplicate_or_gap"] or "",
        classification=classification,
        confidence=confidence(classification, item["status"]),
        evidence=item["exact_ps7331_evidence"],
        next_safe_step=item["disposition"],
    )


NORMALIZERS = {
    "fosinit": normalize_fosinit,
    "vending": normalize_vending,
    "ion": normalize_ion,
    "denylist": normalize_denylist,
    "sink_review": normalize_sink_review,
}

REQUIRED = {
    "fosinit": {
        "id",
        "registration",
        "implementation",
        "entry",
        "caller",
        "gate",
        "identity",
        "user_scope",
        "sink",
        "runtime",
        "missing_edge",
        "classification",
        "evidence",
        "next_safe_step",
    },
    "vending": {
        "id",
        "surface",
        "artifact_or_path",
        "caller",
        "gate",
        "sink",
        "missing_edge",
        "classification",
        "evidence",
    },
    "ion": {
        "row_id",
        "edge",
        "ELF_DT_NEEDED_relocation_dlopen",
        "init_vintf_ownership",
        "file_context_cil",
        "downstream_graph",
        "status",
        "confidence",
        "missing_edge",
        "evidence",
    },
    "denylist": {
        "reconciliation_id",
        "layer",
        "status",
        "can_close_from_saved_evidence",
        "schema_path_hash_comparison",
        "saved_evidence",
        "precise_result",
        "remaining_boundary",
        "forbidden_action",
    },
    "sink_review": {
        "id",
        "status",
        "surface",
        "caller_gate_identity_sink",
        "exact_ps7331_evidence",
        "classification",
        "duplicate_or_gap",
        "disposition",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/tables/phase21-caller-gate-sink.csv"),
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    normalized: list[dict[str, str]] = []
    manifest: list[tuple[str, str, str, int]] = []
    for kind, relative in SOURCES.items():
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"missing source: {path}")
        if kind == "sink_review":
            source_rows = read_sink_review_rows(path)
        else:
            source_rows = read_rows(path, REQUIRED[kind])
        normalizer = NORMALIZERS[kind]
        normalized.extend(normalizer(item) for item in source_rows)
        manifest.append((kind, relative, digest(path), len(source_rows)))

    ids = [item["record_id"] for item in normalized]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise SystemExit(f"duplicate IDs: {duplicates}")
    for item in normalized:
        if set(item) != set(FIELDS):
            raise SystemExit(f"normalized schema mismatch: {item['record_id']}")
        if item["confidence"] not in {
            "Confirmed",
            "Strong evidence",
            "Probable",
            "Hypothesis",
            "Disproved",
        }:
            raise SystemExit(f"invalid confidence: {item['record_id']}")

    if args.verify_only:
        print(f"verified {len(normalized)} rows from {len(SOURCES)} ledgers")
        for kind, relative, sha, count in manifest:
            print(f"{kind}\t{count}\t{sha}\t{relative}")
        return 0

    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=FIELDS,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(normalized)
    print(f"wrote {len(normalized)} rows to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
