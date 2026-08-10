# 支線 D：既有測試／POC／結果 reconciliation

日期：2026-08-10。範圍是 workspace 內既有檔案的只讀盤點；本次沒有連接裝置、沒有重跑測試、沒有送 Binder、沒有 APK 安裝/執行、沒有修改 package/settings/user/HOME、沒有 reboot/OTA/driver/kernel/root/exploit 操作。

完整矩陣在 [CSV](luna_worker_next_test_reconciliation_20260810.csv)。固定欄位為：`id,phase_or_test,goal,command_or_artifact,precondition,result,status,evidence,confidence,repeat_policy,next_safe_step`。

## 結論

User 0 的 Fire Launcher gate、priority、set-home、普通 package-state routes、DPM、child/profile/KFT、input、OTA 與 root/kernel 邊界已有足夠的歷史 evidence；沒有證據支持 ordinary app 或 shell 可以持久停用 Fire、替換 formal HOME、取得 UID 0 或寫入 partition。

最小且仍安全的下一個 runtime 候選只有：被動觀察一次「自然發生的 Alexa prewarm」並同步保存 process/activity/package/HOME invariants。它不得注入 tx1、不得猜 parcel、不得 lookup/private-service call、不得安裝 APK 或改變狀態。必要前提是新的明確 live-session 授權、自然事件確實發生，以及 passive capture 能在無 rollback 的情況下完成；若事件不自然發生，或需要人工觸發 private transaction，立即停止。這是 validation candidate，不是 exploit 或 HOME route。

Phase 6ER/15 已證實 ordinary APK 的 tx1 prewarm 曾造成暫時 process/resource effect，但同一 evidence 沒有 HOME/package sink；因此不得把它重述為 root、launcher replacement 或可操作 exploit。

## 狀態總覽

CSV 共有 30 rows，覆蓋 Phase 1–15 以及專門的下一候選/禁止重複彙總。狀態按本次 reconciliation 使用：

- `已測試`：已有 runtime capture，但本身不是表示結果可安全重跑。
- `可重現`：已有固定 artifact/靜態分析或歷史結果可由保存 evidence 重建；不代表要重跑裝置動作。
- `已排除`：在明確 build/user/caller/path 範圍內被否定或已由使用者關閉。
- `未測試`：workspace 沒有該安全 runtime 結果。
- `需要新前提`：只有在新 caller/build/自然事件/安全 lab 條件成立時才可繼續。

| 領域 | 盤點結果 | 下一步分類 |
|---|---|---|
| Fire Launcher disable/component gate | protected package/component state 拒絕 ordinary shell 路徑；state unchanged | 已排除；禁止 duplicate |
| priority/set-home | preferred record 可暫存，但 resolver/reboot 回到 Fire priority 50 | 已排除；禁止 duplicate |
| ordinary-app Amazon handles | handle 可取得；self-owned ProxyReceiver PendingIntent 被 system-flag gate 擋住 | 已排除；除非新 caller/build |
| prewarm tx1 | bounded tx1 有暫時 process/resource effect，無 HOME/package/root effect | 已有結果；只可被動自然事件觀察 |
| KFT child/profile | Tahoe priority 975 僅對 child/profile；回 User 0 為 Fire priority 50 | 已排除 User 0 relay；禁止 child/KFT variants |
| profile/DPM/input | DPM tx100 gate negative；input 走正常 HOME policy；無 Fire writer | 已排除各已測 path |
| OTA/OOBE | static lifecycle/recovery capability，無 ordinary caller/execution/effect | 已排除低權限結論；禁止 replay |
| Root/kernel/driver | source/config/patch/candidate node 不等於 reachability；無 retail root transition | 已排除現有 route；禁止 low-level mutation |

## Phase 1–15 reconciliation

Phase 1–5 建立了 HOME resolver、Fire protection、priority/set-home、Accessibility workaround、package routes、OTA 與低層/Root 的基線；Phase 6 擴展到 KFT/DPM/input/Amazon private services/OTA/native；Phase 7–9 是 control-surface residual review；Phase 10–15 將 caller、gate、Binder identity、user scope、sink 與 evidence schema 做廣泛 reconciliation。

最重要的差異是「能力存在」與「可接受的低權限 caller」分開處理：KFT 確有 Fire/Tahoe/Launcher3 state writer，但 closed semantic caller 是 child/profile lifecycle；prewarm 確有 process sink，但沒有 HOME/package sink；OTA/driver/kernel 只有 static capability 或 missing-edge rows。

## 真正最小的安全 runtime 驗證

候選為 CSV `R-029`：passive natural Alexa prewarm observation。它需要新前提，不是現在即可執行的命令。驗證只應回答：自然 prewarm 是否產生預期暫時 process/resource effect，以及 User 0 Fire HOME、Fire package/component state、current user、settings 與 SELinux invariants 是否保持不變。不得用自製 APK、`service call`、tx1 parcel、UserInfo、DPM admin、child switch、Accessibility、OTA、driver ioctl 或 root 方法來製造事件。

## 禁止重複

禁止重跑的原因不是「尚未找到更好 payload」，而是原 evidence 已足夠關閉該路徑，或重跑本身會新增不必要的狀態/安全風險：

- `pm disable-user`/component disable、priority ranking、`set-home`、reboot persistence：已有 negative/rollback evidence。
- child/KFT/Tahoe/User 10/11、GUI profile switch、child-lock/PIN：已反覆證明 child scope，User 0 回 Fire；closure 明確要求不重複。
- ordinary self-owned Amazon ProxyReceiver tx6/tx7、普通 APK handle variants：已有 physical gate result；只有新 caller provenance 或 build 才可 reopen。
- Accessibility/ADB foreground monitor variants：只能是暫時 foreground fallback，formal resolver 不變，且已明確 closed。
- outer source tar、OTA/OOBE broadcast、updater/recovery、sideload/flash：沒有 ordinary caller，且涉及 execution/partition risk；不得 decompress/replay/flash。
- guessed private Binder parcels、forged `UserInfo`/tx3、crafted tx1 payload：缺少安全新前提，且會把 static candidate 變成未授權 mutation。
- root/GhostLock/preload、kernel/driver node open/ioctl、malformed input：沒有 retail caller-to-sink closure，並超出本支線安全範圍。

## QA

本次 QA 僅針對新建 CSV，執行固定欄位、欄位數、duplicate ID、空值與 confidence vocabulary 檢查；未執行任何 device command 或測試 runner。QA 結果應在交付時為：30 data rows、固定欄位完全相同、ID 無重複、必填欄位無空值、confidence 僅 `高/中/低/未知`。
