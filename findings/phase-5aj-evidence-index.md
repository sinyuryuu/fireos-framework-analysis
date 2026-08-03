# Phase 5AJ evidence index — MT8183／Android 9 CVE 與公開 Android 實作

## Scope

本階段只做 host-side source／artifact／official bulletin 對照，並引用既有
exact PS7330 read-only capture；沒有新增裝置狀態變更。Confidence 僅表示目前
證據範圍，不表示漏洞可利用性。

| Evidence ID | Source | File / URL | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5AJ-DEVICE-001 | Exact runtime capture | `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/` | `trona` / MT8183 / PS7330.4104N / Android 9 / patch 2024-02-01 / SELinux Enforcing / verified boot green | Exact target context | 已證實 |
| P5AJ-DEVICE-002 | Bluetooth package capture | `adb/phase5/PHASE5J-BLUETOOTH-ARTIFACTS-FOLLOWUP-20260803-01/sha256sums.txt` | Bluetooth APK/ODEX/VDEX are present; preserved state was Bluetooth off/disconnected | Android Bluetooth layer exists; active vendor path not proven reachable | 已證實 |
| P5AJ-ANDROID-001 | AOSP Android implementation | [AOSP GattService.java](https://android.googlesource.com/platform/packages/apps/Bluetooth/+/refs/heads/oreo-r6-release/src/com/android/bluetooth/gatt/GattService.java) | `BluetoothGattBinder`, permission checks, `classInitNative`, `initializeNative` define the Java/Binder/native boundary | Android app layer is not the MediaTek proprietary vulnerable implementation | 已證實 |
| P5AJ-AMAZON-001 | Exact Fire VDEX | `artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_gatt_FosGattService.txt` | `FosGattService` extends the GATT service shape, creates `FosBluetoothGattBinder`, enforces `BLUETOOTH`, and calls native-backed adapter paths | Amazon adds a Bluetooth extension; no root decision shown in reviewed slice | 已證實，slice-scoped |
| P5AJ-AMAZON-002 | Exact Fire VDEX | `artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_amznbtpolicymgr_AmazonBtPolicyManagerAdapter.txt` | Adapter declares BTPM native methods and forwards callbacks to `FosGattService` | Proprietary native boundary is below ordinary AOSP Java service | 已證實，slice-scoped |
| P5AJ-MTK-001 | Android/MediaTek February bulletin | [Android February 2022 bulletin](https://source.android.com/docs/security/bulletin/2022-02-01); [MediaTek February 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/February-2022) | 20025-20028 are MediaTek Bluetooth issues; Android bulletin lists patch IDs; published scope includes MT8183/Android 9 in vendor records | Historical applicability scope only; not proof PS7330 is vulnerable | 強證據，external-scope |
| P5AJ-ASB-001 | Android bulletin | [Android February 2022 bulletin](https://source.android.com/docs/security/bulletin/2022-02-01) | Patch levels `2022-02-05` or later address the bulletin's applicable issues | PS7330 date is later, so patched status is plausible, but Amazon binary mapping is absent | 高可信推論 |
| P5AJ-NVD-001 | NVD | [CVE-2022-20027](https://nvd.nist.gov/vuln/detail/CVE-2022-20027) | Bluetooth OOB write, patch `ALPS06126826`, CPE includes Android 9 and MT8183 | Confirms issue class/scope, not exact binary state | 強證據，external-scope |
| P5AJ-MTK-002 | MediaTek July bulletin | [MediaTek July 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/July-2022) | 21767/21768 are Bluetooth heap OOB issues; bulletin lists MT8183 and Android 8.1-12 | Historical applicability scope only | 強證據，external-scope |
| P5AJ-NVD-002 | NVD | [CVE-2022-21767](https://nvd.nist.gov/vuln/detail/CVE-2022-21767) | Bluetooth OOB write, patch `ALPS06784430`, Android 9/MT8183 CPE scope | Confirms issue class/scope, not exact binary state | 強證據，external-scope |
| P5AJ-NVD-003 | NVD | [CVE-2022-21768](https://nvd.nist.gov/vuln/detail/CVE-2022-21768) | Bluetooth OOB write, patch `ALPS06784351`, Android 9/MT8183 CPE scope | Confirms issue class/scope, not exact binary state | 強證據，external-scope |
| P5AJ-WEB-001 | NVD | [CVE-2026-3499](https://nvd.nist.gov/vuln/detail/CVE-2026-3499) | WordPress Product Feed PRO CSRF, not Android/Linux kernel | User-supplied identifier is mismatched for this device research | 已證實，已排除 |
| P5AJ-WEB-002 | NVD | [CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499) | Linux `rtmutex`/futex `remove_waiter()` issue; fix uses `waiter->task` instead of `current` | Confirms GhostLock's kernel layer; does not provide exact Android payload | 已證實，external-scope |
| P5AJ-WEB-003 | NVD | [CVE-2026-43503](https://nvd.nist.gov/vuln/detail/CVE-2026-43503) | Linux `skb` shared-frag marker/XFRM/ESP path | Confirms DirtyClone is distinct from GhostLock and not an Android Framework issue | 已證實，external-scope |
| P5AJ-KERNEL-001 | Prior exact source review | `findings/phase-5u-android-cve-applicability.md`; `artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json` | Fire 4.4 source family has GhostLock-relevant source overlap; signed PS7330 kernel is unavailable | Source overlap is not exploitability or root evidence | 已證實，source-scoped |
| P5AJ-KERNEL-002 | Prior defconfig review | `findings/phase-5af-android-cve-and-poc-review.md` | Main documented DirtyClone packet-duplication/TEE symbols are absent from captured config | No exact documented entry path justified; not a proof of all kernel safety | 強證據，config-scoped |
| P5AJ-POC-001 | Bounded public-source search | `artifacts/phase5/android-implementation-public-review-20260804-01/`; `artifacts/phase5/bluetooth-cve-screen-20260804-01/github-repository-search.tsv` | No exact `KFTRWI/trona/MT8183/PS7330` Android root implementation found | Search absence is bounded, not global nonexistence | 高可信推論，bounded-search |
| P5AJ-SAFETY-001 | Test boundary | `artifacts/phase5/phase5aj-mtk-android9-cve-poc-review-20260804-01/metadata.tsv` | No exploit download/compile/run; no Bluetooth activation, trigger, node open, boot or partition operation | Live exploitation was intentionally not performed | 已證實 |

## Status vocabulary

- **已證實**：直接由 preserved artifact/source/official record 支持。
- **高可信推論**：由多個來源支持，但缺少 exact signed binary 或 live proof。
- **待驗證**：需要 exact vendor binary/source mapping；不應在設備上猜測觸發。
- **已排除**：識別碼或必要 entry condition 與本機不符。
- **因風險拒絕測試**：需要記憶體破壞、kernel race、外部 crafted input 或未知高權限介面。
