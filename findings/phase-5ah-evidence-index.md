# Phase 5AH Evidence Index

| Evidence ID | Source | File / URL | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5AH-DEVICE-001 | Current read-only capture + existing baseline | `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/`; `P5AF-DEVICE-001` | `device`, `KFTRWI/trona`, Android 9, PS7330.4104N, kernel 4.4.146+, Enforcing | Exact device boundary unchanged | Confirmed |
| P5AH-SRC-001 | User-provided HackMD | [HackMD](https://hackmd.io/@lokey0905/rk-hQSzibl) | CVE-2025-21479/ABL/MIQSAS content is Qualcomm/Xiaomi-oriented | Platform mismatch for MT8183/Amazon | Confirmed |
| P5AH-SRC-002 | Fixed public repo | [mtk-easy-su](https://github.com/KoCleo/mtk-easy-su/tree/8c6871ac7c15b8e98a47e25c35ab93b87e260475) | Warns post-March-2020 firmware may block; no KFTRWI/trona/MT8183 tested row | No exact target | Confirmed |
| P5AH-RUN-001 | Existing device observation | `adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/` | ordinary preflight observed; no UID 0/permissive/su evidence | Existing payload attempt failed to prove root | Confirmed |
| P5AH-SRC-003 | Existing pinned mtkclient review | `artifacts/phase5/public-mtkclient-followup-20260804-01/` | Generic MTK BROM/DA source; no Amazon exact loader/auth profile | Not safe exact target | Strong evidence |
| P5AH-SRC-004 | Amazon product specification | [Fire HD 10 specifications](https://developer.amazon.com/docs/device-specs/ft-device-specifications-firehd-models.html?v=firehd10_2023) | KFTRWI is 2021 11th gen, Fire OS 7, Android 9/API 28 | Product identity | Confirmed |
| P5AH-SRC-005 | Public exact-model search | Search set recorded in source manifest | No verified exact PS7330 root/bootloader implementation found | Search-bounded negative result | Strong evidence |
| P5AH-SRC-006 | Public near-target search | MT8183 Chromebook/other-device results | Same SoC but different boot/policy/firmware | Not transferable | Strong evidence |
| P5AH-RESULT-001 | Host-only matrix | `output/tables/phase5ah-public-route-matrix.csv` | Every reviewed route has mismatch, missing target evidence, or unsafe boundary | No new live candidate | Confirmed |
| P5AH-SAFETY-001 | Execution disposition | `findings/phase-5ah-public-target-recheck.md` | No unknown payload, BROM/DA, fastboot write, partition write or destructive ADB run | Device preserved | Confirmed |

## Search limitation

This index records public-source review, not proof that no private or undisclosed exploit exists. A future exact signed artifact or independently verified `trona/PS7330` source would supersede the search-bounded result.
