# Phase 6RS–RU evidence index

日期：2026-08-10
公開基準：`224e126eb2cea75a7817bff34c2afbe63e35f1b1`

## RS-01 — SettingsProvider/PMS/Amazon PM closure

- Files: `work/luna_worker_phase6rs_settings_pm_closure_20260810.md/.csv`
- SHA-256: MD `6d5e43ac80febad594ef8b8ee2bab7faceca2b17925a7cfe7032725d44601383`;
  CSV `452d4a7bafa1316991211a3428280cddc539810d75b49dfba1aaca4fbf7449eb`
- Rows: 10
- Observation: SettingsProvider caller/user/permission gates and PMS preferred sink
  are statically closed; Amazon PM metadata production caller/holder remains UNKNOWN。
- Confidence: Confirmed static implementation; Strong evidence for bounded negative relay。

## RT-01 — SystemUI/Amazon callback closure

- Files: `work/luna_worker_phase6rt_systemui_callback_closure_20260810.md/.csv`
- SHA-256: MD `7674d467753028df80b9f76435ab4d024629415541c45157b7abdb6958cf673e`;
  CSV `9b3f9bdd9d85f11e298999f07514e0906d535384b30b46b3893dade544afc97d`
- Rows: 14
- Observation: no explicit Fire component in preserved SystemUI/callback corpus; OOBE/setup
  and profile metadata are writers with different sinks。
- Confidence: Strong evidence, bounded by saved class/resource corpus。

## RU-01 — rootless fallback review

- Files: `work/luna_worker_phase6ru_rootless_fallback_review_20260810.md/.csv`
- SHA-256: MD `e3192cd74a10c7aa13403bf297d831335f6d66a85613380f67ddf908ec740bf7`;
  CSV `5ceaf50ecc9d69e8b017d99f194e5250287ea768d4489c9321b53fd230191057`
- Rows: 11
- Observation: Accessibility delayed redirect is the best measured approximation; no formal
  HOME replacement. UsageStats/PendingIntent/ADB monitor are weaker or temporary。
- Confidence: Confirmed for cited historical tests; no new device test this round。

## RS-RU-MATRIX-01 — normalized matrix

- File: `output/tables/phase6rs-ru-privilege-surface.csv`
- SHA-256: `8ad7c9006432a61fa7d57b2a20f090815c1d6c410194c0c03710f21e7b664f7d`
- Manifest: `output/tables/phase6rs-ru-privilege-surface.csv.manifest.json`
  SHA-256 `007e9e987a57e25f4b73868339cabecbd7138122e3f372acb9fe126d2b697dd2`
- Rows: 35 (10 + 14 + 11)
- Generator: `tools/scripts/build_phase6rs_ru_surface.py`
- Device contact by generator: false

## RS-RU-SAFETY-01 — not executed

No unknown Binder/service call, settings/package mutation, AppOps/overlay change,
Accessibility/UsageStats enablement, OTA/recovery, driver operation, Root/exploit,
reboot or partition write was performed. These are **因風險拒絕測試** rather than runtime
negative findings。

## Confidence vocabulary

- **已證實 / Confirmed**：direct source or saved runtime fact。
- **高可信推論 / Strong evidence**：multiple artifacts agree with a bounded gap。
- **Probable**：bounded inference, not a permission claim。
- **Hypothesis**：requires a future safe analysis/test。
- **Disproved**：contradicted in the stated build/test scope。
- **因風險拒絕測試 / Risk-rejected**：not executed for safety/rollback reasons。
