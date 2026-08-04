# PS7331 OTA post-install surface (host-only)

- OTA: `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`
- SHA-256: `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`
- ZIP members: **27**
- Captured findings: **46** (all-match counts are in `summary.json`)

## Evidence

The preserved updater metadata contains explicit `block_image_update` and `package_extract_file` operations targeting system/vendor and boot-chain block devices. This is a high-risk update boundary, not a safe userspace control surface.

The scan found no reason to execute the updater, alter a ZIP, or test a symlink/path traversal hypothesis on a device. `run_program`, symlink handling and temp-path hits, if any, require manual binary/recovery review.

## Classification

- **已證實：** the package is a full/block OTA with inventory entries for update-binary, updater-script, boot and system/vendor payloads; the preserved script names concrete partition targets.
- **高可信推論：** this package is not an ADB-level reversible launcher workaround and must be treated as a full update transaction.
- **待驗證：** implementation-level staging, signature and path handling inside recovery/update-binary; no dynamic test was justified.
- **因風險拒絕測試：** OTA install/sideload, malformed package, symlink replacement, bootloader or partition writes.

## Reproduction

```text
python3 tools/scripts/audit_phase6i_ota_postinstall_surface.py \
  --ota firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin \
  --metadata-root artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01 \
  --extracted-root firmware/extracted/PS7331 \
  --output artifacts/phase6i/phase6i-ota-postinstall-YYYYMMDD-01
```

All operations above are host-only; the script refuses an existing output directory and never invokes update-binary.
