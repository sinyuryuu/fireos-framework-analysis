# Phase 4A H1 verdict

## 判定：已證實（resolver ordering）；高可信推論（本機實際 candidate set 的完整重播）

H1 的核心語句由 AOSP Android 9 原始碼直接證實：
`chooseBestActivity()` 在 ordinary preferred lookup 之前先比較前兩名候選的
`priority`、`preferredOrder`、`isDefault`；任一不同即返回排序後的第一名。

以 Fire priority 50、第三方 priority 0、第三方 `mAlways=true` preferred
record 的輸入重播時，離線模型選 Fire，且標示
`preferred_considered=false`。Phase 3C 的實機結果亦完全相同：p0 record
寫入並跨重啟保存，但 resolver、Home key、explicit HOME 與 foreground 仍是
Fire。

尚缺的直接證據是當時 system_server 內部完整 `ResolveInfo` list 的逐項
序列化 trace；現有 `cmd package query-activities`、resolver 結果、AOSP
方法與事件快照足以把 H1 標為已證實，但不把未取得的內部 trace 假裝存在。

Evidence: `P4A-MODEL-001`, `P3C-PREF-001`, `P3C-REBOOT-001`,
`P3C-LOGCAT-001`.
