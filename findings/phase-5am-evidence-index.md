# Phase 5AM evidence index — Android Bluetooth implementation boundary

| Evidence ID | Source | File / reference | Test / date | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| `P5AM-001` | Exact target identity | `findings/phase-5v-bluetooth-cve-review.md`; `findings/phase-5j-bluetooth-mtk-android9-triage.md` | `P5J/P5V`, 2026-08-03/04 | KFTRWI/trona/MT8183, Android 9/API 28, PS7330.4104N, patch 2024-02-01 | Scope for interpreting all derived Android artifacts | 已證實，snapshot-scoped |
| `P5AM-002` | Exact Java/VDEX artifact | `adb/phase5/PHASE5J-BLUETOOTH-ARTIFACTS-FOLLOWUP-20260803-01/sha256sums.txt`; `artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/` | `P5J-BT-003/004/005`, 2026-08-03 | Exact Bluetooth APK/ODEX/VDEX were pulled and indexed; derived focus files are line-addressable | Input to host-only boundary parser | 已證實，artifact-scoped |
| `P5AM-003` | AOSP-shaped permission path | `artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_gatt_GattService.txt:433651-439404` | host-only, 2026-08-04 | GATT methods and BLUETOOTH/admin/privileged checks are present | Java/Binder service boundary is real; not a CVE proof | 已證實，slice-scoped |
| `P5AM-004` | Amazon GATT extension | `.../com_android_bluetooth_gatt_FosGattService.txt:507658-509583` | host-only, 2026-08-04 | Extended binder, superclass calls, permission-guarded overrides and Amazon policy adapter references | Amazon Android implementation layer is present | 已證實 |
| `P5AM-005` | Amazon BTPM boundary | `.../com_android_bluetooth_amznbtpolicymgr_AmazonBtPolicyManagerAdapter.txt:160880-161362` | host-only, 2026-08-04 | Private native `btpmLe*` declarations and callbacks into `FosGattService` | Native/vendor bridge exists; no shell caller or privilege transition shown | 已證實，not exploit proof |
| `P5AM-006` | Reproducible method-index correction | `tools/scripts/analyze_phase5am_bluetooth_boundaries.py`; `output/tables/phase5am-bluetooth-boundaries.csv`; artifact manifest | host-only, 2026-08-04 | 62 rows retain DEX index, artifact line, code address and classification; interpretation states method index is not CVE ID | Prevents CVE/method-number conflation | 已證實，script-scoped |
| `P5AM-007` | Public CVE scope | [MediaTek February 2022 bulletin](https://www.mediatek.com/product-security-bulletin/February-2022) | web review, 2026-08-04 | Public bulletin includes MT8183/Android 9 rows for selected Bluetooth CVEs | Historical scope only; not exact PS7330 binary proof | 強證據，external-scope only |
| `P5AM-008` | Public Android patch mapping | [Android February 2022 bulletin](https://source.android.com/docs/security/bulletin/2022-02-01) | web review, 2026-08-04 | 20025–20028 map to MediaTek patch IDs and 2022-02-05+ semantics | Supports likely later remediation, not exact Amazon mapping | 已證實 for bulletin / 高可信推論 for exact binary |
| `P5AM-009` | Android implementation reference | [AOSP Bluetooth GattService](https://android.googlesource.com/platform/packages/apps/Bluetooth/+/refs/heads/oreo-r6-release/src/com/android/bluetooth/gatt/GattService.java) | host/web review, 2026-08-04 | Public AOSP source provides the standard GATT service/permission comparison point | AOSP reference does not expose Amazon/vendor patch status | 已證實，comparison-scoped |
| `P5AM-010` | Safety boundary | `findings/phase-5v-bluetooth-level3-report.md` and this report | 2026-08-04 | No Bluetooth activation, crafted input, unknown Binder, native exploit or device-node operation | Active exploit validation remains unperformed | 因風險拒絕測試 |

## Derived hashes

`artifacts/phase5/phase5am-bluetooth-implementation-20260804-02/sha256sums.txt` records the
derived CSV and analysis manifest. Input artifact hashes remain in the Phase 5J manifest and
are not replaced by this derived index.

The parser SHA-256 is
`b0f263ee032ad87735d42321fb15c3d586df537b5abc1e7a9dac858c1ccb2dee`; the public CSV SHA-256
is `e91a2f22b599c78bf23cba35252aa2b5dbb0b2724078a46098c2e560cda8c4ff`.
