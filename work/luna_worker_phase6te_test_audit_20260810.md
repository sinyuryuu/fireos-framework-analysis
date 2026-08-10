# Phase 6TE — Host-only ADB / Launcher / child-user / permission / workaround test audit

日期：2026-08-10（Asia/Taipei）  
範圍：只讀目前工作樹中的 `findings/`、既有 `adb/` raw outputs、`work/luna_worker_*`、`artifacts/` 與既有報告。此次沒有接觸設備，沒有執行 ADB、Binder、driver、root、OTA、reboot、package/settings mutation，也沒有覆寫既有檔案。

## 結論

現有證據足以閉合目前 exact-build snapshot 的 User 0 HOME 邊界：`com.amazon.firelauncher/.Launcher` 以 priority 50 持續勝出；Microsoft 的 preferred record 可以存在，但 priority 0 仍不會取代 Fire。Fire 的 `disable-user`、`suspend`、`hide`、`uninstall` 等已保存 shell 路徑均被不同的權限或 protected-package gate 擋住，且保存的 before/after/final guard 沒有顯示 Fire、HOME resolver 或 foreground 狀態被改變。

child-user 證據是已完成但 strictly user-scoped 的正面結果：Tahoe 在 child user（歷史 run 使用 User 10/11/12）可成為 priority 975 的 HOME；回到 User 0 後仍是 Fire priority 50。這不能外推為 User 0 replacement，也不能用 KFT/private service 作為 shell workaround。

已知近似 workaround 只有暫時 foreground 效果：ADB monitor、Accessibility redirect、manifest Lock Task。三者都沒有寫入 User 0 formal HOME resolver；Accessibility 的自然 HOME/reboot 結果具有 timing-sensitive 矛盾，應保留為 bounded/temporary，而不是成功的 HOME replacement。

## 狀態與可重複性規則

- **已完成**：既有測試回答了其限定問題，且有報告與 raw output/guard 可交叉核對。
- **已排除**：保存結果否定該路徑在目前 build/user scope 的目標效果；不代表所有更高權限 caller 都不存在。
- **未完成**：仍缺 caller、user scope、exact-build resource/overlay、時間對齊或其他使結論不能升格的證據。
- **重複/guard**：同一 build、user、candidate set 的重複 resolver/package snapshots；只在前提改變時才有新價值。
- **拒絕/未執行**：因安全或 authority boundary 沒有送出的 private Binder、child lifecycle replay、OTA/OOBE、root/exploit 等，不當作負向 runtime 測試。

逐列清單在 [CSV audit](./luna_worker_phase6te_test_audit_20260810.csv)。

## 主要判定

| 主題 | 目前判定 | 可重做性 | 主要缺口 |
|---|---|---|---|
| User 0 HOME resolver | 已完成；Fire priority 50 是 canonical baseline | 僅在 build/user/candidate set 改變時重做 | 未觀察其他 image 或候選集合下的持久性 |
| preferred HOME / `set-home-activity` | 已排除為 User 0 replacement；preferred record 不敵 Fire priority | host-only 可重算 ranking；不需重送 setter | exact caller-to-writer provenance 與 equal-priority branch 的完整 runtime 對照 |
| Fire package state | 已完成 shell gate boundary；disable/suspend/hide/uninstall 均未改變 Fire | 只讀解析 saved exit/state 可重做；不要重送 setter | privileged caller 行為未知，但不屬於本 audit 可測範圍 |
| Settings Default Home | 未完成 runtime selection；static/UI surface 已有 bounded evidence | host-only resource/overlay diff 可重做 | exact-build dashboard omission 與 picker reachability 的完整 artifact join |
| child Tahoe HOME | 已完成 child-only positive result | 不應重做 child creation/switch/unlock；可讀既有 captures | 統一歷史 User 10/11/12 aliases 與 readiness gate |
| KFT/private Amazon service | 已排除 shell reachability；static writer 為 child-scoped | host-only caller/permission/user mapping 可重做 | trusted caller/holder provenance；不得送 tx3 或猜 transaction |
| ADB monitor / Accessibility | 已完成 bounded foreground fallback；正式 HOME 已排除 | host-only 對齊 saved timestamps/rollback 可重做 | 自然 HOME 0/3 與 3/3 差異的時間、trigger、sampling 定義 |
| Lock Task | 已完成 temporary foreground retention；reboot persistence 已排除 | host-only 讀既有 state/manifest 可重做；不要安裝或 lock | 不存在 User 0 HOME writer 的新證據 |

## 證據缺口與安全下一步

1. 只讀 exact-build Settings/framework-res resource、overlay inventory 與既有 UI dump，確認 `default_home`/`config_show_default_home` 是否還有未索引 gate；不點 UI、不 dispatch Binder。
2. 對 KFT、PMS/HOME、prewarm、DPM 與 private service 做 source-to-caller-to-permission-to-user-to-sink join；只用已有 decompiled/source/artifact。
3. 對 Accessibility/ADB monitor 保存檔案做 host-only timestamp、trigger、`resolve-activity`、`ResumedActivity` 對齊；不 reboot、不 enable service、不 replay。
4. 統一 child User 10/11/12 的 capture metadata 與 `RUNNING_UNLOCKED` readiness 條件；不 switch user、不建立/刪除 profile。

本 audit 不宣稱 root，不提出 exploit payload，也不把 static sink、foreground observation 或 child HOME 寫成 User 0 durable HOME replacement。

