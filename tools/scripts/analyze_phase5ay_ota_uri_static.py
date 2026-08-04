#!/usr/bin/env python3
"""Summarize the DeviceSoftwareOTA URI/update source flow offline.

This tool invokes JADX against an APK supplied by the caller, searches the
temporary decompilation for OTA endpoint and URI-persistence code, and writes
small, reviewable evidence files. It never connects to a device or network,
and it never executes the APK. Existing output directories are refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


URL_RE = re.compile(r"https?://[^\"' )]+")

RULES = [
    ("remote_config_app", ("createForAppId", "426273902372", "appConfig:a17uvcne"),
     "SettingsManager creates an Arcus remote-configuration client."),
    ("remote_config_attributes", ("Build.SERIAL", "build_version", "ota_group"),
     "The remote configuration request is keyed by device/build attributes."),
    ("remote_config_sync", ("maybeSyncArcusConfig", "mManager.sync", "Twelve"),
     "OTA settings can be refreshed through the remote configuration client."),
    ("update_endpoint_default", ("getUpdatesUrlPathAndMethod", "softwareupdates.amazon.com/software/inventory2"),
     "The APK contains a default authenticated update-query endpoint."),
    ("authenticated_update_post", ("AuthenticatedURLConnectionWrapper", "setRequestMethod(\"POST\")", "Content-Type"),
     "The update query uses the authenticated URL wrapper and JSON POST."),
    ("query_input", ("AuthenticatedDeviceGetUpdatesQueryInput", "setBuildDimensions", "setInventory"),
     "The request carries build dimensions and installed-package inventory."),
    ("server_url_to_remote_uri", ("getUrl()", "mRemoteUri", "URI.create"),
     "The server-provided update URL becomes the PublishedUpdate remote URI."),
    ("remote_uri_database_column", ("RemoteURI", "contentValues.put"),
     "PublishedUpdates persists the remote URI in the OTA database schema."),
    ("download_mapping", ("getOtaDownloadUrl", "IAmazonDownloadManager", "enqueue"),
     "DownloadStarter maps the URI and enqueues it through AmazonDownloadManager."),
    ("local_uri_database_column", ("LocalURI", "setLocalUri"),
     "The local downloaded file is represented separately from the remote URI."),
]

PREFERRED_LINE_ANCHORS = {
    ("remote_uri_database_column", "RemoteURI"): '"RemoteURI"',
    ("remote_uri_database_column", "contentValues.put"): '"RemoteURI"',
    ("local_uri_database_column", "LocalURI"): "setLocalUri",
    ("local_uri_database_column", "setLocalUri"): "setLocalUri",
    ("download_mapping", "IAmazonDownloadManager"): "mIAmazonDownloadManager",
}

RULE_FILE_HINTS = {
    "remote_config_app": "SettingsManager.java",
    "remote_config_attributes": "SettingsManager.java",
    "remote_config_sync": "SettingsManager.java",
    "update_endpoint_default": "OTASettings.java",
    "authenticated_update_post": "GetUpdatesCall.java",
    "query_input": "RequestBuilder.java",
    "server_url_to_remote_uri": "PublishedUpdate.java",
    "remote_uri_database_column": "PublishedUpdate.java",
    "download_mapping": "DownloadStarter.java",
    "local_uri_database_column": "AmazonDownloadManagerHelper.java",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--jadx", default="jadx", help="JADX executable (default: jadx)")
    parser.add_argument("--max-hits", type=int, default=400)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def find_rule_hits(source_root: Path, max_hits: int) -> tuple[list[dict], list[str]]:
    hits: list[dict] = []
    urls: set[str] = set()
    java_files = sorted(source_root.rglob("*.java"))
    for source_file in java_files:
        try:
            lines = source_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        relative = source_file.relative_to(source_root).as_posix()
        for line_number, line in enumerate(lines, 1):
            urls.update(URL_RE.findall(line))
        lower_lines = [line.lower() for line in lines]
        for rule_id, terms, interpretation in RULES:
            file_hint = RULE_FILE_HINTS.get(rule_id)
            if file_hint is not None and not source_file.name.endswith(file_hint):
                continue
            term_matches = []
            for term in terms:
                term_lower = term.lower()
                matching_lines = [
                    (line_number, lines[line_number - 1].strip())
                    for line_number, lower_line in enumerate(lower_lines, 1)
                    if term_lower in lower_line
                ]
                if not matching_lines:
                    term_matches = []
                    break
                anchor = PREFERRED_LINE_ANCHORS.get((rule_id, term))
                if anchor is not None:
                    anchored = [
                        item for item in matching_lines if anchor.lower() in item[1].lower()
                    ]
                    if anchored:
                        matching_lines = anchored
                term_matches.append((term, matching_lines[0]))
            for term, (line_number, text) in term_matches:
                hits.append({
                    "rule": rule_id,
                    "term": term,
                    "file": relative,
                    "line": line_number,
                    "text": text,
                    "interpretation": interpretation,
                })
                if len(hits) >= max_hits:
                    return hits, sorted(urls)
    return hits, sorted(urls)


def write_tsv(path: Path, rows: list[dict]) -> None:
    fields = ["rule", "term", "file", "line", "text", "interpretation"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write("\t".join(fields) + "\n")
        for row in rows:
            handle.write("\t".join(str(row.get(field, "")).replace("\t", " ") for field in fields) + "\n")


def write_excerpts(path: Path, hits: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# DeviceSoftwareOTA URI static excerpts\n\n")
        handle.write("These are JADX-derived line excerpts, not original source. Re-run the script against the hashed APK for regeneration.\n\n")
        for hit in hits:
            handle.write(f"## `{hit['rule']}` / `{hit['term']}` — `{hit['file']}:{hit['line']}`\n\n")
            handle.write(f"- Interpretation: {hit['interpretation']}\n")
            handle.write(f"- Decompiled line: `{hit['text'].replace('`', '\\`')}`\n\n")


def main() -> int:
    args = parse_args()
    apk = args.apk.resolve()
    output = args.output.resolve()
    jadx_path = shutil.which(args.jadx) or args.jadx
    command = [jadx_path, "-d", "<temporary-jadx-output>", "--no-res", "--no-debug-info", str(apk)]

    if args.dry_run:
        print("DRY_RUN")
        print(f"APK={apk}")
        print(f"OUTPUT={output}")
        print("DEVICE_IO=none")
        print("NETWORK_IO=none")
        print("APK_EXECUTION=none")
        print("COMMAND=" + " ".join(command))
        return 0

    if not apk.is_file():
        print(f"error: APK does not exist: {apk}", file=sys.stderr)
        return 2
    if output.exists():
        print(f"error: refusing to overwrite existing output: {output}", file=sys.stderr)
        return 2
    if shutil.which(args.jadx) is None and not Path(args.jadx).is_file():
        print(f"error: JADX executable not found: {args.jadx}", file=sys.stderr)
        return 2

    output.mkdir(parents=True)
    input_hash = sha256(apk)
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="phase5ay-ota-jadx-") as temp_dir:
        temp_root = Path(temp_dir)
        jadx_output = temp_root / "jadx"
        actual_command = [jadx_path, "-d", str(jadx_output), "--no-res", "--no-debug-info", str(apk)]
        completed = subprocess.run(actual_command, text=True, capture_output=True, check=False)
        (output / "jadx.stdout.txt").write_text(completed.stdout, encoding="utf-8")
        (output / "jadx.stderr.txt").write_text(completed.stderr, encoding="utf-8")
        if completed.returncode != 0:
            (output / "commands.txt").write_text(" ".join(actual_command) + "\n", encoding="utf-8")
            print(f"error: JADX failed with exit code {completed.returncode}", file=sys.stderr)
            return completed.returncode or 1
        sources = jadx_output / "sources"
        hits, urls = find_rule_hits(sources, max(1, args.max_hits))
        write_tsv(output / "uri-static-findings.tsv", hits)
        write_excerpts(output / "source-excerpts.md", hits)

    metadata = {
        "analysis": "Phase 5AY DeviceSoftwareOTA URI/update source review",
        "timestamp_utc": started,
        "input_apk": str(args.apk),
        "input_apk_sha256": input_hash,
        "jadx": str(jadx_path),
        "jadx_args": ["--no-res", "--no-debug-info"],
        "device_io": False,
        "network_io": False,
        "apk_execution": False,
        "hit_count": len(hits),
        "url_literals": urls,
        "result_scope": "static decompiler evidence; no live OTA database contents",
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (output / "commands.txt").write_text(
        "jadx -d <temporary-jadx-output> --no-res --no-debug-info " + str(apk) + "\n",
        encoding="utf-8",
    )
    checksum_lines = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        checksum_lines.append(f"{sha256(path)}  {path}")
    (output / "sha256sums.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(f"WROTE={output}")
    print(f"INPUT_SHA256={input_hash}")
    print(f"HITS={len(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
