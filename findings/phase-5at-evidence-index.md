# Phase 5AT evidence index

| Evidence ID | Source | File / URL | Observation | Confidence |
|---|---|---|---|---|
| `P5AT-001` | exact device metadata | `findings/phase-5t-ota-metadata-review.md`; `adb/phase5/PHASE5T-OTA-METADATA-20260804-01/` | installed target is PS7330.4104N with recorded PL/LK descriptors | 已證實 |
| `P5AT-002` | Amazon official update index | [Amazon Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE) | 11th-gen entry currently advertises FireOS 7.3.3.1 | 已證實（page scope） |
| `P5AT-003` | Amazon download endpoint | `https://www.amazon.com/update_Fire_HD10_11th_Gen` and redirect metadata in `artifacts/phase5/ps7330-artifact-followup-20260804-01/metadata.md` (`042f9fe92eba9d7cdbf6ee52fd715cd1249f76fe1e4d9f4c7367350cbd35b136`) | endpoint redirects to PS7331.4463N package; no PS7330 package was returned | 已證實（endpoint scope） |
| `P5AT-004` | public firmware history | [FTVDB 11th-gen history](https://ftvdb.com/firetablet/firmware/com.amazon.trona.android.os/) | public page lists PS7331, PS7329 and older records, not PS7330 | 已證實（bounded public page scope） |
| `P5AT-004A` | public raw firmware database | [FTVDB raw trona JSON](https://raw.githubusercontent.com/FTVDB/FTVDB/main/database/firmware/com.amazon.trona.android.os.json) | 5,169-byte snapshot SHA-256 `7d80beaf572ee585449da48121b190b30cee7f92b1a69d3011b61d2668e6632a`; no `PS7330` value | 已證實（bounded public snapshot scope） |
| `P5AT-005` | Amazon source notice provenance | [source-notice archive](https://technicallycompetent.com/pages/amazon-kindle-source-code-notices/) and exact [7.3.3.0 source](https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2) | exact 11th-gen 7.3.3.0 source is listed; no matching signed image is supplied by that listing | 已證實（source-notice scope） |
| `P5AT-006` | descriptor search | exact strings `d1a4a4b-20231011_072631`, `79172a1-20231008_072039`, `trona_fireos_ship_7330`, and `PS7330.4104N` | no independently verifiable public boot/preloader/LK/DA result in bounded search | 待驗證（search-bounded） |
| `P5AT-007` | safety boundary | `findings/phase-5at-ps7330-artifact-followup.md` | no device mutation, low-level loader, firmware write or GhostLock trigger was performed | 因風險拒絕測試 |
