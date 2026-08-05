#!/usr/bin/env python3
"""Audit the PS7331 OTA/OOBE input and post-OTA state boundaries offline.

This is a host-only evidence generator.  It reads preserved JADX source,
manifest text, and VDEX disassembly.  It never contacts a device, sends an
OTA/OOBE broadcast, invokes Binder, executes an updater/recovery component,
creates a package, follows a symlink, or writes an output file over an
existing artifact directory.

The OTA implementation and contract JADX trees are preserved separately.  The
contract tree supplies ``Sideload`` so the audit can record its parcel/property
shape without pretending that native ZIP, recovery, or update behavior is
reconstructed from Java alone.
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
SOURCE_ROOT = ROOT / "artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources"
CONTRACT_ROOT = ROOT / "artifacts/phase6j/ota-contracts-ps7331-jadx-20260805-01/sources"
DEFAULTS = {
    "oobe_receiver": ROOT / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java",
    "oobe_helper": ROOT / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java",
    "oobe_manifest": ROOT / "artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt",
    "system_server": ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
    "sideload_filename": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadFilenameFilter.java",
    "ota_settings": SOURCE_ROOT / "com/amazon/device/software/ota/util/settings/OTASettings.java",
    "sideload_directory": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadDirectory.java",
    "sideload_observer": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadFileObserver.java",
    "sideload_factory": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadFactory.java",
    "build_properties_factory": SOURCE_ROOT / "com/amazon/dcp/ota/BuildPropertiesFactory.java",
    "zip_helper": SOURCE_ROOT / "com/amazon/device/framework/ZipHelper.java",
    "sideload_metadata": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadMetadataChecker.java",
    "sideload_pvt": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadPVTChecker.java",
    "sideload_verifier": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadVerifier.java",
    "sideload_sanity": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadSanityChecker.java",
    "sideload_installer": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadInstaller.java",
    "os_properties": SOURCE_ROOT / "com/amazon/device/software/ota/tasks/validate/OSUpdatePropertiesValidator.java",
    "device_state": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadDeviceStateChecker.java",
    "sideload_mover": SOURCE_ROOT / "com/amazon/dcp/ota/SideloadMover.java",
    "file_helper": SOURCE_ROOT / "com/amazon/device/framework/FileHelper.java",
    "update_system": SOURCE_ROOT / "com/amazon/device/framework/UpdateSystemWrapper.java",
    # The implementation and contract JADX trees are separate preserved
    # inputs.  Sideload is present in the contract tree.
    "sideload_model": CONTRACT_ROOT / "com/amazon/dcp/ota/Sideload.java",
    "build_properties_model": CONTRACT_ROOT / "com/amazon/dcp/ota/BuildProperties.java",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def line_numbers(text: str, pattern: str) -> list[int]:
    expression = re.compile(pattern, re.IGNORECASE)
    return [number for number, line in enumerate(text.splitlines(), 1) if expression.search(line)]


def line_ref(path: Path, text: str, pattern: str) -> str:
    matches = line_numbers(text, pattern)
    return f"{rel(path)}:{','.join(map(str, matches)) or '?'}"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_row(
    rows: list[dict[str, object]],
    evidence_id: str,
    surface: str,
    class_method: str,
    source: str,
    observed_logic: str,
    security_relevance: str,
    classification: str,
    confidence: str,
    limitation: str,
) -> None:
    rows.append(
        {
            "evidence_id": evidence_id,
            "surface": surface,
            "class_method": class_method,
            "source": source,
            "observed_logic": observed_logic,
            "security_relevance": security_relevance,
            "classification": classification,
            "confidence": confidence,
            "limitation": limitation,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=default)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_paths = {name: getattr(args, name) for name in DEFAULTS}
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "host_only": True,
                    "device_contacted": False,
                    "broadcast_sent": False,
                    "binder_invoked": False,
                    "ota_executed": False,
                    "recovery_invoked": False,
                    "partition_written": False,
                    "output": str(args.output),
                    "inputs": {name: str(path) for name, path in input_paths.items()},
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    missing_required = [
        str(path)
        for name, path in input_paths.items()
        if not path.is_file()
    ]
    if missing_required:
        raise SystemExit("missing preserved input(s):\n" + "\n".join(missing_required))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    texts = {
        name: read_text(path)
        for name, path in input_paths.items()
        if path.is_file()
    }
    rows: list[dict[str, object]] = []

    receiver = input_paths["oobe_receiver"]
    receiver_text = texts["oobe_receiver"]
    add_row(
        rows,
        "6AB-OOBE-001",
        "post-OTA OOBE receiver",
        "BootAfterSystemOTAReceiver.onReceive / enableIncrementalFlow",
        line_ref(receiver, receiver_text, r"BOOT_AFTER_SYSTEM_OTA|enableIncrementalFlow|OOBEActivationHelper"),
        "The action gate checks BOOT_AFTER_SYSTEM_OTA, OOBE-running state, and retail_demo_mode; the qualifying path writes incremental-OOBE preferences, enables OobeHomeActivity, and calls activateOOBEIF.",
        "High-impact setup/HOME lifecycle state transition after a system OTA.",
        "HIGH_RISK_LIFECYCLE_ENTRY",
        "Confirmed",
        "Static source evidence only; no broadcast or OOBE activation was performed.",
    )
    add_row(
        rows,
        "6AB-OOBE-002",
        "post-OTA OOBE receiver",
        "BootAfterSystemOTAReceiver.onReceive error path",
        line_ref(receiver, receiver_text, r"catch \(Throwable|setComponentEnabledSetting"),
        "On an exception the receiver logs a fatal condition and disables its own component.",
        "Failure path mutates component state, but does not create a safe third-party control surface.",
        "ERROR_SELF_DISABLE_SIDE_EFFECT",
        "Confirmed",
        "The exact PackageManager enforcement behavior is not replayed; source only.",
    )

    helper = input_paths["oobe_helper"]
    helper_text = texts["oobe_helper"]
    add_row(
        rows,
        "6AB-OOBE-003",
        "OOBE state helper",
        "OOBEActivationHelper.activateOOBEIF",
        line_ref(helper, helper_text, r"activateOOBEIF|user_setup_complete|isOOBEActive"),
        "The incremental activation method sets user_setup_complete=0 and isOOBEActive=1 through the foreground settings helper.",
        "A qualifying OTA event can reopen setup state; this is not an ordinary HOME preferred-activity mutation.",
        "SETUP_STATE_MUTATION",
        "Confirmed",
        "No setting was changed on the device.",
    )

    manifest = input_paths["oobe_manifest"]
    manifest_text = texts["oobe_manifest"]
    add_row(
        rows,
        "6AB-OOBE-004",
        "OOBE manifest boundary",
        "BootAfterSystemOTAReceiver declaration / OobeHomeActivity",
        line_ref(manifest, manifest_text, r"BootAfterSystemOTAReceiver|OobeHomeActivity|priority=\"100\"|MANAGE_USERS"),
        "The receiver is enabled and directBootAware with an implicit action filter; OobeHomeActivity is a priority-100 MAIN/SETUP_WIZARD/HOME/DEFAULT activity protected by MANAGE_USERS and was observed disabled in the saved User 0 dump.",
        "Manifest exposure is not proof of caller reachability; the receiver is lifecycle-bound and the activity is privileged setup UI.",
        "MANIFEST_SURFACE_NOT_CALLER_PROOF",
        "Confirmed",
        "The action's runtime protected-broadcast classification was not inferred from the absence of a component-local permission.",
    )

    system_server = input_paths["system_server"]
    system_server_text = texts["system_server"]
    add_row(
        rows,
        "6AB-OOBE-005",
        "system-server sender",
        "AmazonPackageManagerService.onBootPhase",
        # The preserved disassembly contains many unrelated sendBroadcast and
        # BOOT_AFTER_SYSTEM_OTA string references.  Keep the known method
        # block as an exact bounded locator instead of emitting a noisy global
        # search result.
        f"{rel(system_server)}:96107-96126",
        "Saved service disassembly shows boot phase 550 plus PackageManagerService.isUpgrade() before constructing and sending the post-OTA action with RECEIVE_BOOT_AFTER_SYSTEM_OTA.",
        "The natural sender is a system-server OTA lifecycle, not an ordinary shell HOME event.",
        "SYSTEM_SERVER_GATED_SENDER",
        "Confirmed",
        "The full runtime caller-permission evaluation was not replayed.",
    )

    filename = input_paths["sideload_filename"]
    filename_text = texts["sideload_filename"]
    settings = input_paths["ota_settings"]
    settings_text = texts["ota_settings"]
    add_row(
        rows,
        "6AB-OTA-001",
        "OTA input discovery",
        "SideloadFilenameFilter / OTASettings.getSideloadFilenameFilter",
        f"{line_ref(filename, filename_text, r"Pattern\.compile|matcher\(str\)\.find")}; {line_ref(settings, settings_text, r"getSideloadFilenameFilter|ota\.sideload\.update_file_pattern")}",
        "The default pattern is update-.*\\.(bin|zip)$, compiled from OTASettings; accept() applies matcher(str).find(), while the setting is runtime-configured.",
        "Filename matching is only an input-discovery boundary. It is not evidence that a discovered file bypasses metadata, signature, recovery, or updater checks.",
        "CONFIGURABLE_FILENAME_DISCOVERY",
        "Strong evidence",
        "The live SettingsManager value was not read; the Sideload model is supplied separately by the preserved contract tree.",
    )
    add_row(
        rows,
        "6AB-OTA-002",
        "OTA input discovery",
        "SideloadDirectory.getSideloads / SideloadFileObserver.findNewestSideloadInArray",
        f"{line_ref(input_paths['sideload_directory'], texts['sideload_directory'], r"listFiles|isFileReadyToBeUsed|mSideloadFactory\.create")}; {line_ref(input_paths['sideload_observer'], texts['sideload_observer'], r"findNewestSideloadInArray|mSideloadMetadataChecker\.check|getBuildVersionNumber")}",
        "Matching files are listed, checked for stable length, converted to Sideload objects, metadata-checked, and the highest build version is selected.",
        "The source shows a selection pipeline before installation; it does not establish that a malformed or replaced file reaches UpdateSystem.",
        "DISCOVERY_THEN_METADATA_GATE",
        "Confirmed",
        "The Sideload contract is supplied by a separate preserved JADX tree; native and implementation details remain separate.",
    )

    factory = input_paths["build_properties_factory"]
    factory_text = texts["build_properties_factory"]
    zip_helper = input_paths["zip_helper"]
    zip_helper_text = texts["zip_helper"]
    model = input_paths["sideload_model"]
    model_text = texts["sideload_model"]
    build_properties_model = input_paths["build_properties_model"]
    build_properties_text = texts["build_properties_model"]
    add_row(
        rows,
        "6AB-OTA-003",
        "OTA metadata parser boundary",
        "BuildPropertiesFactory.parseOsPropertiesFromZipFile / ZipHelper.runWithZipEntry",
        f"{line_ref(factory, factory_text, r"system/build\.prop|Properties\.load")}; {line_ref(zip_helper, zip_helper_text, r"getEntry\(str\)|getInputStream|closeQuietly")}",
        "The preserved code reads the exact system/build.prop ZIP entry and parses it with java.util.Properties; ZipHelper closes the stream and ZipFile on normal/error paths.",
        "Metadata extraction is observable statically; the separate Sideload/BuildProperties contract source closes the Java model coverage without proving native ZIP behavior.",
        "ZIP_METADATA_EXTRACTION",
        "Confirmed",
        "ZipFileFactory/native ZIP behavior and native recovery/update behavior remain outside this Java source scope.",
    )
    add_row(
        rows,
        "6AB-OTA-004",
        "OTA metadata model",
        "Sideload / BuildProperties contract model",
        f"{line_ref(model, model_text, r"class Sideload|VERSION|mFile|mProperties|getVersion|writeToParcel")}; {line_ref(build_properties_model, build_properties_text, r"class BuildProperties|ro\.build\.version|ro\.product\.device|writeToParcel")}",
        "The preserved contract tree defines Sideload as a Parcelable carrying a File and BuildProperties, and maps build/product/signature/version properties including ro.build.version.number and ro.product.device.",
        "This closes the previously documented Java model-source gap; it does not turn the OTA path into a shell-reachable or safe installation interface.",
        "CONTRACT_MODEL_COVERAGE_CLOSED",
        "Confirmed",
        "The contract is a separate JADX output from the implementation tree; native parser, ZIP, recovery, filesystem and UpdateSystem semantics remain unproven here.",
    )

    metadata = input_paths["sideload_metadata"]
    metadata_text = texts["sideload_metadata"]
    pvt = input_paths["sideload_pvt"]
    pvt_text = texts["sideload_pvt"]
    add_row(
        rows,
        "6AB-OTA-005",
        "sideload metadata gates",
        "SideloadMetadataChecker.check / verifySideloadVersion / verifySignatureTransition / verifySideloadProduct",
        f"{line_ref(metadata, metadata_text, r"public void check|verifySideloadVersion|verifySignatureTransition|verifySideloadProduct|allow_.*transition")}",
        "The checker sequences version, signature-transition, product, and PVT build-type checks. Downgrade/product/signature transitions are controlled by OTASettings booleans whose defaults are false.",
        "The ordinary metadata path rejects common cross-product, downgrade, and signature-transition cases before install; configuration provenance remains a separate question.",
        "METADATA_VALIDATION_GATE",
        "Confirmed",
        "This is source-level control-flow evidence, not a validation of an arbitrary package.",
    )
    add_row(
        rows,
        "6AB-OTA-006",
        "PVT build gate",
        "SideloadPVTChecker.checkPVTGetsUserBuild",
        line_ref(pvt, pvt_text, r"isPvt|isPvtUnlocked|build type|InvalidFile"),
        "On PVT devices a non-user build is rejected unless the device is PVT-unlocked; user builds are allowed.",
        "This is a build-type policy gate, not a shell-writable privilege transition.",
        "PVT_BUILD_POLICY_GATE",
        "Confirmed",
        "No PVT state was changed or tested.",
    )

    verifier = input_paths["sideload_verifier"]
    verifier_text = texts["sideload_verifier"]
    add_row(
        rows,
        "6AB-OTA-007",
        "sideload verification",
        "SideloadVerifier.verifySideloadWithRecoveryCheck / verifySideloadPackage",
        line_ref(verifier, verifier_text, r"verifySideloadMetadata|verifyPackage|verifySideloadWithRecoveryCheck|RecoverySystemWrapper"),
        "The full verification path performs sanity checks, metadata checks, RecoverySystemWrapper.verifyPackage, and device-state checks.",
        "A filename match alone is insufficient to reach the privileged package verifier/update sink.",
        "RECOVERY_SIGNATURE_VERIFICATION_BOUNDARY",
        "Confirmed",
        "The recovery/native verifier implementation was not executed or treated as fully reconstructed here.",
    )
    sanity = input_paths["sideload_sanity"]
    sanity_text = texts["sideload_sanity"]
    add_row(
        rows,
        "6AB-OTA-008",
        "sideload sanity",
        "SideloadSanityChecker.check",
        line_ref(sanity, sanity_text, r"verifySideloadExists|verifySideloadContainsMetadata|isPropertiesEmpty"),
        "The sanity checker requires the file to exist and the Sideload properties object not to be empty.",
        "The check is a necessary precondition but not a sufficient authenticity proof.",
        "BASIC_FILE_AND_METADATA_GATE",
        "Confirmed",
        "The Sideload property model is now covered by the preserved contract source; native verification remains separate.",
    )

    installer = input_paths["sideload_installer"]
    installer_text = texts["sideload_installer"]
    update_system = input_paths["update_system"]
    update_text = texts["update_system"]
    add_row(
        rows,
        "6AB-OTA-009",
        "privileged update sink",
        "SideloadInstaller.installSideload / UpdateSystemWrapper.install",
        f"{line_ref(installer, installer_text, r"verifySideloadWithoutRecoveryCheck|maybeMoveSideloadFile|installOSUpdate|mUpdateSystemWrapper\.install")}; {line_ref(update_system, update_text, r"UpdateSystem\.install|replaceFirst")}",
        "installSideload verifies metadata and device state, moves the file if needed, then calls UpdateSystemWrapper.install; the wrapper maps external storage to media storage and invokes UpdateSystem.install.",
        "This is a high-impact update sink. It must not be reached by a research payload or manually invoked during this project.",
        "HIGH_IMPACT_UPDATE_SINK_AFTER_GATES",
        "Confirmed",
        "No installer/updater/recovery code was executed.",
    )

    device_state = input_paths["device_state"]
    device_state_text = texts["device_state"]
    add_row(
        rows,
        "6AB-OTA-010",
        "device-state check",
        "SideloadDeviceStateChecker.check / clearCache",
        line_ref(device_state, device_state_text, r"verifyBatteryLevel|maybeClearCacheSpace|deleteDirectoryContents|verifyDeviceHasSufficientDiskSpace"),
        "The device-state check verifies battery and storage; if cache space is insufficient it deletes download-cache contents while excluding the recovery-cache directory.",
        "This is a potentially destructive local cleanup side effect, not a safe route for runtime experimentation.",
        "CACHE_CLEANUP_SIDE_EFFECT",
        "Confirmed",
        "No cache mutation was performed.",
    )

    mover = input_paths["sideload_mover"]
    mover_text = texts["sideload_mover"]
    file_helper = input_paths["file_helper"]
    file_helper_text = texts["file_helper"]
    add_row(
        rows,
        "6AB-OTA-011",
        "OTA staging move",
        "SideloadMover.maybeMoveSideloadFile / FileHelper.moveFile",
        f"{line_ref(mover, mover_text, r"split\(\"/\"\)|getExternalDataDirectory|moveFile")}; {line_ref(file_helper, file_helper_text, r"renameTo|copyFile|file\.delete\(\)|canonical|readlink|realpath|lstat|NOFOLLOW")}",
        "The Java path builds a destination from the last slash-separated path element and moves by rename, or copy-then-delete; no Java-level canonical/readlink/realpath/lstat/O_NOFOLLOW marker appears in the selected files.",
        "The bounded absence is a review item for native/filesystem provenance, not proof of a symlink or traversal vulnerability.",
        "BOUNDED_PATH_HARDENING_UNKNOWN",
        "Strong evidence",
        "Native File/Zip/UpdateSystem behavior and omitted code paths are not covered; no payload test is allowed.",
    )

    validator = input_paths["os_properties"]
    validator_text = texts["os_properties"]
    add_row(
        rows,
        "6AB-OTA-012",
        "background OTA validation",
        "OSUpdatePropertiesValidator.assertUpdatePropertiesValid",
        line_ref(validator, validator_text, r"assertUpdatePropertiesValid|assertUpdateVersionMatchesPublishedUpdate|assertUpdateSignatureMatchesDeviceSignature|assertPvtGetsUserBuild"),
        "The background-update validation extracts system/build.prop, requires the package version to match the published pending update, matches signature type, and enforces PVT user-build policy.",
        "The same-version OTA path has a separate validator in addition to sideload checks.",
        "BACKGROUND_UPDATE_METADATA_GATE",
        "Confirmed",
        "Only preserved source was analyzed; no pending update was altered.",
    )

    # Record the explicit safety decision as machine-readable evidence rather
    # than implying that a static candidate is an approved experiment.
    add_row(
        rows,
        "6AB-SAFETY-001",
        "research boundary",
        "Phase 6AB execution policy",
        "host-only policy; no device file",
        "No device contact, broadcast, Binder transaction, OTA install, recovery action, malformed package, symlink/traversal payload, partition write, OOBE activation, or component enable was performed.",
        "The receiver remains a high-risk post-OTA/OOBE research item and is not an adopted launcher/root workaround.",
        "RISK_REJECTED_RUNTIME_TRIGGER",
        "Confirmed",
        "Natural-event observation remains the only acceptable future runtime evidence.",
    )

    fields = [
        "evidence_id",
        "surface",
        "class_method",
        "source",
        "observed_logic",
        "security_relevance",
        "classification",
        "confidence",
        "limitation",
    ]
    write_csv(args.output / "ota-input-validation.csv", fields, rows)

    input_rows = []
    for name, path in input_paths.items():
        input_rows.append(
            {
                "input_name": name,
                "file": rel(path),
                "exists": str(path.is_file()).lower(),
                "sha256": sha256(path) if path.is_file() else "MISSING_IN_SELECTED_SOURCE_SCOPE",
                "role": "preserved OTA contract input" if name in {"sideload_model", "build_properties_model"} else "preserved analysis input",
            }
        )
    write_csv(args.output / "input-sha256.csv", ["input_name", "file", "exists", "sha256", "role"], input_rows)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "broadcast_sent": False,
        "binder_invoked": False,
        "ota_executed": False,
        "recovery_invoked": False,
        "partition_written": False,
        "receiver": "BootAfterSystemOTAReceiver",
        "receiver_classification": "HIGH_RISK_LIFECYCLE_ENTRY",
        "receiver_runtime_trigger": "RISK_REJECTED_RUNTIME_TRIGGER",
        "sideload_model_source_present": input_paths["sideload_model"].is_file(),
        "row_count": len(rows),
        "confirmed_rows": sum(row["confidence"] == "Confirmed" for row in rows),
        "strong_evidence_rows": sum(row["confidence"] == "Strong evidence" for row in rows),
        "unknown_or_gap_rows": sum(row["classification"] == "DECOMPILER_COVERAGE_GAP" for row in rows),
        "limitations": [
            "Sideload and BuildProperties are supplied by a separate preserved OTA contract JADX tree; implementation and contract provenance are triangulated, not merged.",
            "Native File/Zip/RecoverySystem/UpdateSystem behavior is not proven by Java source alone.",
            "No runtime OTA/OOBE event was manufactured or replayed.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    flow = """flowchart TD
    A[system_server boot phase 550 + isUpgrade] --> B[BOOT_AFTER_SYSTEM_OTA]
    B --> C[BootAfterSystemOTAReceiver]
    C --> D{OOBE not running and demo mode off?}
    D -- no --> E[disable incremental OOBE flag]
    D -- yes --> F[write incremental OOBE prefs]
    F --> G[enable OobeHomeActivity]
    F --> H[activateOOBEIF: setup state mutation]

    I[external storage filename] --> J[SideloadFilenameFilter regex]
    J --> K[SideloadFactory / BuildPropertiesFactory]
    K --> L[system/build.prop Properties]
    L --> M[SideloadMetadataChecker]
    M --> N[SideloadVerifier + RecoverySystem.verifyPackage]
    N --> O[SideloadDeviceStateChecker]
    O --> P[SideloadMover]
    P --> Q[UpdateSystem.install high-impact sink]

    C -. no manual broadcast .-> R[Phase boundary: natural OTA observation only]
    J -. separate contract source .-> S[Sideload + BuildProperties model]
"""
    (args.output / "ota-input-validation.mmd").write_text(flow, encoding="utf-8")

    result = f"""# Phase 6AB host-only result

Generated at UTC: `{summary['generated_at_utc']}`

## Scope

This artifact joins the already-registered `BootAfterSystemOTAReceiver` OOBE
lifecycle item with the preserved OTA input-discovery, metadata, verification,
staging, and update-sink source. It does not execute any of those paths.

## Result

- Receiver classification: **HIGH_RISK_LIFECYCLE_ENTRY**.
- Static receiver behavior: **Confirmed** — the qualifying post-OTA path can
  write incremental OOBE state, enable `OobeHomeActivity`, and activate OOBE.
- OTA filename filter: **Strong evidence** — the default pattern is runtime
  configured and applied with `Pattern.matcher(name).find()`; this is discovery,
  not an authenticity bypass.
- Validation order: **Confirmed** — metadata and recovery verification precede
  the `UpdateSystem.install` sink in the preserved Java path.
- `Sideload.java` / `BuildProperties.java`: **Confirmed model coverage** — the
  preserved OTA contract JADX tree defines the Parcelable and property mapping;
  no native parser, filesystem, recovery, or UpdateSystem semantics were
  invented.
- Runtime trigger: **risk rejected** — no broadcast, OOBE activation, updater,
  recovery, payload, or device mutation was performed.

## Evidence

The machine-readable evidence is in `ota-input-validation.csv`; source hashes
are in `input-sha256.csv`; the graph is `ota-input-validation.mmd`.

## Next safe step

Only host-side recovery/native artifact provenance or observation after a normal,
researcher-initiated official OTA may extend this item. Manual broadcast replay,
OOBE component enabling, crafted OTA/symlink tests, updater execution, and
partition operations remain rejected.
"""
    (args.output / "result.md").write_text(result, encoding="utf-8")

    manifest_lines = []
    for path in sorted(args.output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    (args.output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
