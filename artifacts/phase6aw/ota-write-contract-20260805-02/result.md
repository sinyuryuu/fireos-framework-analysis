# Phase 6AW — PS7331 official OTA write contract

This is a host-only provenance and safety analysis. The updater, recovery, OTA package, and device were not executed or modified.

## Gates

- `pre-device`: `trona`
- `post-build`: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- `post-build-incremental`: `0031575863172`
- `post-security-patch-level`: `2024-08-01`
- OTA description: `Fire OS 7.3.3.1 (PS7331.4463N/4463)`

## Static result

- **已證實（靜態）：** the script contains block-image update operations for system and vendor and direct extraction targets for boot-chain/firmware partitions.
- **已證實（靜態）：** the saved update-binary analysis contains registration, expression evaluation, block-image handlers, verification helpers, and raw I/O helper edges.
- **高可信推論：** this package is a full/high-impact update transaction, not a reversible ADB launcher or settings control surface.
- **無法由本階段確認：** complete recovery-side signature/canonicalization behavior and any hypothetical future updater defect.
- **因風險拒絕測試：** OTA install/sideload, recovery execution, malformed or symlink payloads, downgrade attempts, and all partition writes.

## Target list

- `/dev/block/platform/bootdevice/by-name/system` — `system_or_vendor_block_image_write`
- `/dev/block/platform/bootdevice/by-name/vendor` — `system_or_vendor_block_image_write`
- `/dev/block/platform/bootdevice/by-name/boot` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/preloader` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/lk` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/tee1` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/tee2` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/spmfw` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/sspm_1` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/cam_vpu1` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/cam_vpu2` — `boot_or_firmware_partition_write`
- `/dev/block/platform/bootdevice/by-name/cam_vpu3` — `boot_or_firmware_partition_write`
- `/cache/recovery/last_blocklist` — `recovery_metadata_write`

## Consequence

The official package does provide signed boot and source provenance for analysis, but that does not make it a safe runtime experiment. It remains a high-impact lifecycle boundary; no shell/ADB launcher workaround or privilege transition is established by this static contract.

## Reproduction

```sh
python3 tools/scripts/build_phase6aw_ota_write_contract.py --dry-run --output /tmp/phase6aw-dry-run
python3 tools/scripts/build_phase6aw_ota_write_contract.py --output artifacts/phase6aw/ota-write-contract-YYYYMMDD-01
shasum -a 256 -c artifacts/phase6aw/ota-write-contract-YYYYMMDD-01/sha256sums.txt
```
