# Phase 5AL evidence index

| Evidence ID | Source | File | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5AL-DEVICE-001 | read-only capture | `adb/phase5/PHASE5AL-MTK-CVE-SURFACE-20260804-02/fingerprint.stdout.txt`, `kernel.stdout.txt`, `patch.stdout.txt` | `trona` / Android 9 / Linux 4.4.146+ / SPL 2024-02-01 | Exact device identity for candidate triage | 已證實 |
| P5AL-ACCESS-001 | read-only capture | `id.stdout.txt`, `device_nodes.stdout.txt` | shell UID 2000; candidate nodes are system/root/camera/media-owned | MDP/VPU route has no demonstrated shell access | Strong evidence |
| P5AL-IMS-001 | read-only capture | `packages_filtered.stdout.txt`, `services_filtered.stdout.txt` | no IMS package/service; `imms` is `IMms`, plus `telephony.registry` | Public IMS candidates lack an observed exact entry surface | Strong evidence |
| P5AL-IMS-002 | read-only capture | `telephony_registry.stdout.txt`, `phone_dump.stdout.txt`, `radio_dump.stdout.txt` | Phone 0 is out of service; phone/radio dumps do not expose an IMS implementation | No active modem/IMS path was observed | Strong evidence |
| P5AL-IMS-003 | read-only capture | `device_nodes.stdout.txt`, `binary_names.stdout.txt` | no `/dev/ccci*`/AT/modem node and no matching binary names | No documented AT/CCCI route was observed | Strong evidence |
| P5AL-MDP-001 | official bulletin + runtime mode | MediaTek April 2022 bulletin; `device_nodes.stdout.txt` | `20067` is MT8183/Android 9 but requires system privilege; `/dev/mdp_freq` root-only | Not a shell-start route | Strong evidence |
| P5AL-PRELOADER-001 | official bulletin + artifact review | MediaTek March/April 2022 bulletins; `findings/phase-5ai-exact-ps7330-artifact-search.md` | preloader candidates are Android 10-12 and exact PS7330 loader is absent | Do not use generic DA/preloader | 已證實 |
| P5AL-WIFI-001 | official bulletin + runtime | MediaTek October 2021 bulletin; `proc_modules.stdout.txt` | Wi-Fi rows are DoS/info-disclosure, not root EoP; Wi-Fi module exists | Not a root candidate | 已證實 |
| P5AL-COLLECTOR-001 | host script validation | `tools/scripts/capture_phase5al_mtk_cve_surface.sh` | `bash -n` and `--dry-run` passed; second capture uses corrected remote shell argument form | Reproducible read-only collection | 已證實 |
| P5AL-INVALID-001 | discarded first capture | `adb/phase5/PHASE5AL-MTK-CVE-SURFACE-20260804-01/` | filtered commands produced `pm help` due argument handling | Not used as device evidence; preserved without overwrite | 已證實 |
