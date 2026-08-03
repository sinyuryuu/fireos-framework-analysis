# Phase 5 — exact-build OTA and boot-chain evidence

## Purpose

This note records a stronger boundary between the installed PS7330 build and
the available adjacent PS7331 OTA. It is an offline artifact review; no OTA
was sideloaded and no partition was written.

## Installed build versus official update page

The device currently reports:

```text
ro.build.mktg.fireos=Fire OS 7.3.3.0
ro.build.lab126.project=trona_fireos_ship_7330
ro.build.fingerprint=Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
```

Amazon's current Fire Tablet Software Updates page lists Fire HD 10 (11th
Generation) as Fire OS 7.3.3.1, and links its manual update endpoint from the
device row. It does not expose a PS7330.4104N package in the page captured for
this review. This is evidence about the currently published page, not proof
that no historical PS7330 package ever existed.

Reference: <https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE>

## PS7331 updater-script writes boot-chain partitions

The adjacent OTA's
`firmware/extracted/PS7331/META-INF/com/google/android/updater-script` contains
the following package extraction targets:

```text
/dev/block/platform/bootdevice/by-name/system
/dev/block/platform/bootdevice/by-name/vendor
/dev/block/platform/bootdevice/by-name/boot
/dev/block/platform/bootdevice/by-name/preloader
/dev/block/platform/bootdevice/by-name/lk
/dev/block/platform/bootdevice/by-name/tee1
/dev/block/platform/bootdevice/by-name/tee2
/dev/block/platform/bootdevice/by-name/spmfw
/dev/block/platform/bootdevice/by-name/sspm_1
/dev/block/platform/bootdevice/by-name/cam_vpu1
/dev/block/platform/bootdevice/by-name/cam_vpu2
/dev/block/platform/bootdevice/by-name/cam_vpu3
```

This demonstrates that an ordinary full OTA package for this product family
can contain critical boot-chain writes. It does **not** make the PS7331 images
safe for PS7330. The package metadata is:

```text
product=trona
version_name=Fire OS 7.3.3.1 (PS7331.4463N/4463)
version_number=0031575863172
description=Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys
key_type=release-keys
sign_type=release
binary_type=full
```

## Preloader static strings

The offline inspection output is reproducible with:

```sh
tools/scripts/inspect_phase5_boot_chain_artifact.sh \
  --input firmware/extracted/PS7331/images/preloader.img \
  --output artifacts/phase5/PS7331-preloader-review
```

The selected strings include indicators for:

- RPMB anti-rollback processing and version checks;
- authenticated LK DA handling (`DA validation`, `LK DA signature`, `LK DA
  pubk`, `DA authenticated`);
- `daa_enabled` and authentication failure paths;
- `preloader_trona.bin` and `MTK_BLOADER_INFO_v36`.

These are strings from the PS7331 preloader and are not a direct readout of the
installed PS7330 preloader. They are useful for risk classification, not for
selecting a payload or bypass.

## Determination

- **已證實：** the currently installed build is PS7330.4104N / Fire OS
  7.3.3.0, while the available complete OTA is PS7331.4463N / Fire OS 7.3.3.1.
- **已證實：** the adjacent OTA writes preloader, LK, boot, TEE and other
  low-level partitions through its updater script.
- **已證實：** the adjacent preloader contains anti-rollback and DA
  authentication paths.
- **高可信推論：** a blind PS7331 preloader/LK write could fail authentication,
  rollback checks, or boot compatibility; it is not a recovery plan for PS7330.
- **待驗證：** exact PS7330 preloader revision, BROM hardware ID, DA policy,
  and a complete signed PS7330 recovery set.
- **因風險拒絕測試：** applying the OTA, extracting or writing a DA to the
  tablet, testing seccfg, or attempting any boot-chain bypass.
