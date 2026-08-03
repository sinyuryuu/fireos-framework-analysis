# Phase 5AI Evidence Index

| Evidence ID | Source | File / URL | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5AI-DEV-001 | Exact read-only capture | `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/` | Runtime is `KFTRWI/trona/PS7330.4104N`, kernel 4.4.146+, green VB, locked, Enforcing | Exact current device identity | Confirmed |
| P5AI-OTA-001 | Local firmware inventory | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | Only complete OTA is PS7331 | Adjacent version only | Confirmed |
| P5AI-OTA-002 | Existing extraction evidence | `firmware/extracted/PS7331/images/`; `findings/phase-5-exact-ota-and-boot-chain-evidence.md` | PS7331 has boot/preloader/LK/TEE and updater targets | Applying it is a boot-chain mutation, not recovery | Confirmed |
| P5AI-WEB-001 | Amazon official update page | [Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE) | 11th-gen row publishes Fire OS 7.3.3.1 and a download link; no PS7330 filename shown | Public page does not provide exact PS7330 artifact in the reviewed view | Confirmed, page-scoped |
| P5AI-WEB-002 | Public exact search | `artifacts/phase5/exact-ps7330-artifact-search-20260804-01/source-manifest.csv` | No verified public PS7330 boot/preloader/DA image found | Search-bounded negative result | Strong evidence |
| P5AI-RESULT-001 | Host-only report | `findings/phase-5ai-exact-ps7330-artifact-search.md` | Exact low-level input remains missing | Do not calculate live offsets or flash adjacent image | Confirmed |
| P5AI-SAFETY-001 | Execution record | Same report and existing Level 3 report | No sideload, flash, BROM/DA, seccfg, rollback or partition operation performed | Device state preserved | Confirmed |
