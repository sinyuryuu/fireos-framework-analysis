# Phase 5C — exact-version source and loader search

## Scope

This phase follows the failed MTK-EASY-SU root-control test and Phase 5B.
It searches for an exact PS7330 source or recovery input without touching the
device boot chain. It does not repeat the APK root test and does not invoke a
BROM client, DA, payload, fastboot unlock, erase, or flash command.

Device under test:

| Field | Value |
|---|---|
| Serial | G001LT0511550CFT |
| Model | KFTRWI |
| Product | trona |
| SoC | MT8183 |
| Installed build | Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys |
| Fire OS | 7.3.3.0 |
| Android | 9 / API 28 |
| Security patch | 2024-02-01 |
| Preloader descriptor | d1a4a4b-20231011_072631 |
| LK descriptor | 79172a1-20231008_072039 |

The post-test device state remains the Phase 5B baseline: ADB is in normal
device mode, verified boot is green, flash.locked is 1, SELinux is enforcing,
Fire Launcher is the HOME result, and the test APK is absent. Evidence:
P5-BASE-007.

## Search inputs

### Official current update page

Amazon's current Fire Tablet Software Updates page lists Fire HD 10
(11th Generation) at Fire OS 7.3.3.1. The page does not expose the installed
PS7330.4104N package in the captured current row. This is page-scoped evidence,
not proof that an older PS7330 package never existed.

Source:

- https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE

### Archived update redirects

The update endpoint was checked against retained Wayback snapshots. The
redirect targets in the evidence artifact are:

| Snapshot | Target version |
|---|---|
| 2021-08-15 | PS7319 |
| 2022-03-15 | PS7322 |
| 2022-06-20 | PS7323 |
| 2023-01-21 | PS7326 |
| 2023-10-20 | PS7328 |
| 2025-08-21 | PS7331 |

No PS7330 URL was recovered from this snapshot set. The result is a search
boundary only. It is not evidence that Amazon never published PS7330.

### Public firmware metadata index

The retained version excerpt from the public FTVDB metadata index contains
PS7319, PS7321 through PS7324, PS7326 through PS7329, and PS7331. It contains
no PS7330 record. FTVDB is an independent metadata index, not an official
Amazon image source, so this is supporting evidence only.

### Exact marketing-version source archive

An Amazon S3 source archive was found:

    https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2

HTTP metadata:

| Header | Value |
|---|---|
| Content-Type | application/x-bzip2 |
| Content-Length | 2,588,816,416 bytes |
| Last-Modified | Tue, 30 Jul 2024 02:09:09 GMT |
| ETag | c14e143433d91648afe4634c30a35320 |

The archive is a source/build-material package, not a full OTA. Its README
describes kernel, BusyBox, U-Boot, and Android library build workflows and
references AOSP android-9.0.0_r1. The bounded prefix also contains an
application source directory named apps/com.amazon.firelauncher/.

The full 2.59 GB archive was not retained or committed. A 16 MiB HTTP range
was inspected and its truncation diagnostics were preserved. The bounded
prefix cannot establish what later archive members contain; in particular it
does not establish a signed preloader, LK, DA, or recovery set.

Reproduction:

    tools/scripts/inspect_phase5_exact_source_metadata.sh \
      --url https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2 \
      --output /tmp/phase5-exact-source-metadata

The script has a dry-run mode and only uses host-side HTTP, bzip2, and tar.

### Bounded tail sample

To reduce the remaining uncertainty without retaining the full archive, a
138,816,416-byte range from the archive tail was sampled with
`bzip2recover`. The recovered blocks contain the MT8183 kernel build tree,
including the MT8183 defconfigs and the `mt8183.dts` device tree. They also
contain thousands of paths under `kernel/mediatek/mt8183/4.4_emc/`.

The exact `kernel/` paths matching `u-boot`/`uboot` in this sample are generic
AVR32 reference paths. No exact MTK `preloader` or `lk` source path was found
in the sampled material. This is a partial-range observation, not a complete
archive inventory and not a signed boot-chain artifact.

The sample range SHA-256 is
`706f8e7284cc70b30cf0dc62e8d97a8d4b5bbc49062af157f659b06f59d865e7`.
The method and compact results are under
`artifacts/phase5/exact-source-search-20260803/tail-sample-*`; the reusable
collector is `tools/scripts/inspect_phase5_exact_source_tail.sh`.

## Relationship to the available OTA

The complete local OTA remains PS7331.4463N, not the installed
PS7330.4104N. Its preloader and LK hashes are retained under the existing
PS7331 artifact directory. The adjacent OTA updater script writes boot-chain
partitions, and its preloader contains anti-rollback and DA-authentication
strings. Those facts classify risk; they do not make PS7331 compatible with
PS7330 and do not authorize applying it.

## Determination

- **已證實：** the installed device identity and PL/LK descriptors are those
  recorded in the Phase 5B baseline.
- **已證實：** a public Amazon S3 source archive matching the Fire OS 7.3.3.0
  marketing version exists and can be inspected through a bounded range.
- **已證實：** the complete OTA available in the workspace is PS7331 and is
  a version mismatch for the installed PS7330 build.
- **高可信推論：** the source archive is useful for build-context and kernel
  comparison, but it does not provide the signed boot-chain inputs needed for
  a safe BROM or bootloader operation.
- **已證實（範圍限定）：** the sampled tail contains an MT8183 kernel tree,
  two MT8183 defconfig paths, and the MT8183 device-tree path.
- **待驗證：** whether other, unsampled archive ranges contain a buildable
  U-Boot source or any boot-chain source relevant to the PL/LK descriptors.
- **待驗證：** exact PS7330 preloader binary, BROM hardware ID, DA/SLA/DAA
  policy, and a complete signed recovery set.
- **因風險拒絕測試：** PS7331 image use, generic MTK payloads, DA upload,
  preloader/LK writes, seccfg, fastboot unlock/flash/erase, and any BROM
  connection without an exact protocol and recovery plan.

## Evidence

- P5-SRC-001 through P5-SRC-005
- P5-BASE-007
- P5-OTA-001 through P5-OTA-003

Raw and derived files are under:

- artifacts/phase5/exact-source-search-20260803/
- adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-02/
