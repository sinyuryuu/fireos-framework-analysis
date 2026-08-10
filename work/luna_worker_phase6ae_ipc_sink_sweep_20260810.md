# Phase 6AE host-only IPC sink sweep — 2026-08-10

本輪只搜尋保存的 host artifact（JADX、baksmali/vdexExtractor/fosservices disassembly、manifest、fosinit/service-registration、SELinux/registration 索引及既有 Phase 6X/6X2 ledger）。沒有操作真機、沒有執行 adb、沒有呼叫 Binder、沒有 broadcast/OTA/recovery、沒有 exploit/root/partition write。

## 結果

去重後保留 8 條尚未在 Phase 6X/6X2 完整閉合的高權限 sink 或 route。逐條 caller → gate → Binder identity/clearCallingIdentity → user scope → exact sink → observed effect、duplicate_of、行號/offset 與 SHA 均在 [CSV](./luna_worker_phase6ae_ipc_sink_sweep_20260810.csv)。

這些是靜態控制面與證據缺口，不是漏洞結論。尤其 exported、capability、permission declaration 或 service registration 本身不等於可達性；任何未恢復的 caller、permission holder、Binder identity、user scope 或 effect 都明列為 `UNKNOWN`。

## 覆蓋範圍與去重

- `6AE-001/002` 對應 `6X2-ROUTES-001`：post-system-OTA OOBE receiver/helper；確認的是受 lifecycle guard 的 component/setup-state sink，不是普通 caller 或正式 HOME writer。
- `6AE-003/004` 對應 `6X2-ROUTES-002`：DCPMS profile/policy receivers；確認 policy persistence/evaluator sink，producer、permission holder、user scope 未閉合。
- `6AE-005` 對應 `6X2-ROUTES-003`：ProductPolicy fosinit registration；只有 registration，沒有 recovered Binder method/caller/sensitive sink。
- `6AE-006` 對應 `6X2-ROUTES-004`：prewarm；permission check、clear/restore identity 與 process-start sink 可見，但 caller/result branch/cross-user closure 不完整。
- `6AE-007` 對應 `6X2-ROUTES-005`：USE_SDK/PLUGIN declaration；只有 declaration，沒有 exact consumer 或 sink，不能從 protection level 推導漏洞。
- `6AE-008` 對應 `6X2-ROUTES-006`：OTA verifier/canonical staging 到 update hand-off；Java source 有高風險 update sink，但 native flags、SELinux、實際 caller 與 runtime effect 未知。

## 安全判讀

1. OOBE、DCPMS、prewarm、OTA 都只得到 host-side static evidence；沒有把 capability/exported/permission 宣告改寫成 ordinary-app reachability。
2. `UNKNOWN` 是證據狀態，不是 positive finding。特別是 `6AE-003` 的 exported receiver、`6AE-005` 的 service registration、`6AE-007` 的 low-protection declaration 均沒有獨立漏洞結論。
3. Phase 6X/6X2 已覆蓋的 Settings、proxy receiver、H2 exported service、vending、keyguard 及既有 package/user writers 不在本輪重列；相關 duplicate 只以 `duplicate_of` 指向既有 route/ledger。

## Inputs / provenance

主要輸入及 SHA 見 CSV；基準 ledger 為 `output/tables/phase6x2-control-surface.csv`（SHA `ff2066a917625c3fb988a6a7745a44dcf16cf2ed95124aa9a87231739bf42bbf`）。本報告沒有修改任何既有檔案。
