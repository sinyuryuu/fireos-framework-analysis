# Workaround / HOME audit follow-up — 2026-08-10

本報告只整理既有 Phase 3A～6PV 的 launcher、HOME、Accessibility、Settings、child-profile 與 lock-task 測試，以及主機端保存的靜態 evidence。沒有連接裝置、安裝 APK、啟用 Accessibility、停用 Fire Launcher、root、exploit、Binder replay、OTA、reboot 或任何新的 runtime mutation。

## 結論

目前沒有證據支持 User 0 的第三方「真正 HOME replacement」。Fire Launcher 仍是 User 0 的 resolver winner（priority 50）。可逆且已證實的近似方案只有兩類：

- resident Accessibility/event-driven foreground redirect：可在部分測試中把 Microsoft 留在可見 foreground，並有跨 reboot 的 service-setting persistence；但另一次自然 HOME/clean-reboot 量測為 0/3，且 resolver 不變，故只能列為 temporary foreground workaround。
- manifest Lock Task：可在活動已啟動時阻擋 HOME transition，讓第三方 activity 留在 foreground；resolver 仍是 Fire，且 reboot 後 Lock Task 消失，故不是 persistent HOME。

Child profile 的 Tahoe priority 975 是真正的 child-user HOME，但只對 User 12 生效；回到 User 0 後仍是 Fire priority 50。KFT 的 Fire/Tahoe/Launcher3 writer 是 child-scoped trusted path，不是 User-0 replacement。

## 未清楚分類或具矛盾的 evidence

| route | 判定重點 |
|---|---|
| preferred record | `set-home-activity`/preferred record 可成功寫入，但在 unlocked User 0 仍輸出 Fire；應分類為 disproved workaround，而非 resolver bypass。|
| Settings UI | Default-home controller/picker 與 `replacePreferredActivity()` 存在；Phase 3C 只證明 code/data surface，沒有把 UI 選擇結果當成 runtime 成功。|
| SystemUI | `SGObserver` 觀察 Fire foreground 並開 Smart Genie；沒有 inspected direct Fire HOME launch。不要把觀察、foreground redirect 或 copied framework classes 寫成 SystemUI 是 HOME writer。|
| Accessibility | 6CY 的 explicit Fire redirect 與 3/3 HOME retry 是 foreground evidence；6CY reboot/clean sampling 又有 Settings 或 timing-sensitive 結果。應分開記錄，不能合併成真正 HOME replacement。|
| Lock Task | 6CL 的 foreground retention 與 6CM/6CN 的 reboot negatives 互相一致：lock state 是 temporary task policy，不是 PackageManager HOME state。|
| child profile | Tahoe 975 與 User 0 Fire 50 同時為真，因為是 per-user resolver；短暫 FallbackHome 是 switch readiness artifact，不是 replacement。|
| Amazon helper/IPC | `initiateLauncher` 無 launch sink；prewarm/tx4/OOBE/KFT 各自是 process、setup flags、privileged lifecycle、child package-state surface，均不得升格為 HOME replacement。|

## Safety and classification rules

`real HOME?` 僅在 PackageManager/ActivityTaskManager 的 per-user HOME resolver 明確選中該 component 時填 `yes`；可見 foreground、explicit start、redirect、Lock Task 都不算。`persistence` 只描述既有測試觀察到的 state survival，不把 service setting persistence 推論為 HOME persistence。每個 rollback 欄位只引用既有保存的 rollback result；本 follow-up 沒有新增 rollback 操作。

完整逐路徑欄位在 [CSV audit](./luna_worker_workaround_audit_followup_20260810.csv)。主要 provenance 包括：`output/rendered/phase-1-report.phase2-final4.md`、`output/tables/phase-3c-settings-matrix.csv`、`findings/phase-6cy-ms-targeted-accessibility-retry.md`、`findings/phase-6cy-accessibility-reboot-persistence.md`、`findings/phase-6cl-manifest-locktask-boundary.md`、`findings/phase-6cm-manifest-locktask-reboot-boundary.md`、`findings/phase-6cn-boot-completed-locktask-boundary.md`、`findings/phase-6co-child-switch-timing-policy-boundary.md`、`output/tables/phase6cb-gui-child-profile-kft-lifecycle.csv`、`output/tables/phase6pv-broad-route-closure.csv`。

## Next safe steps

只做 host-only：補充 exact-build Settings resource/overlay diff、整理 Accessibility foreground sampling 的時間戳與判定規則、以及追蹤 KFT/Amazon flags 到第一個 persistence/consumer。不要重播 private Binder、child PIN/profile deletion、Accessibility enablement、Lock Task install、OTA/OOBE 或任何 Fire package/HOME state mutation。
