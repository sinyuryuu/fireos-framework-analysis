# IPC/既有測試 evidence reconciliation（Phase 6/10/12/13）

日期：2026-08-10（Asia/Taipei）  
範圍：主機端唯讀整理既有 findings、output/tables、work worker outputs、manifest/source/config 與歷史 ADB 結果。未執行 adb、service call、未知 Binder、root、driver/ioctl、OTA/recovery、package/settings/user/policy mutation；未重做已被否定的 component-disable/priority 矩陣。

## 結論

保存 evidence 沒有閉合出「普通 app 或 shell → accepted gate → Binder identity → User 0 → Fire Launcher/package state 或 formal HOME sink → observed User-0 replacement」的路徑。

最重要的真實 writer 是 KFT `IAmazonUserManager` tx3 / `enableKftLauncher(UserInfo)`：它把 supplied `UserInfo.id` 傳到 AmazonPackageManager，對 child/profile user 啟用 Tahoe、停用 Fire 與 Launcher3；既有 child captures 與 User-0 final guards 支持 scope separation。外部 APK/native caller、tx3 local authorization、service-manager/SELinux client tuple 與 User-0 parcel provenance 仍未閉合，因此不能把 tx3 當成普通 caller 的 User-0 route。

其他合法或可能合法的控制面均被分開核對：

- Amazon PM flags/metadata writers 有 `amazon.permission.ADD_RM_PKG_METADATA` signature|amazon gate，sink 是 file-backed metadata，不是 HOME setter；第一個 production caller/consumer 仍未知。
- DPM restriction 與 persistent-preferred 路線受 `MANAGE_USERS`、active owner/profile-owner、cross-user 及 PMS UID 1000 等 gate 約束；User 0 Profile Owner 確實存在，但保存 source 是固定 parental-control/lock-task policy，沒有任意 Fire/HOME relay。
- Settings `DefaultHomePicker`、Amazon facade 與 PMS `replacePreferredActivity`/`setHomeActivity` 是合法 framework surface，但需要標準 permission/cross-user/resolver gate；saved baseline 仍解析 `com.amazon.firelauncher/.Launcher` priority 50，沒有普通 app/shell 的閉合 replacement。
- Amazon Profile tx41 可以到 `startActivityAsUser` 邊界；metadata map 的 consumer 與 HOME/PMS edge 未閉合。這是仍可做 source/manifest/config join 的缺口，不是已證實 package writer。
- `MigrationService.appsAvailable` 確實把 Fire package 放入每個 running user 的 external-apps broadcast，但它沒有呼叫 package-state/HOME setter；receiver implementation/manifest 與 downstream consumer 是最小可補的 Fire-specific 缺口。
- `LauncherHijackPreventer` 只處理 HOME-task visibility、`READ_LOGS` 與 bookkeeping；Accessibility T01/T02 只觀察到 foreground redirect，formal HOME 仍是 Fire。兩者都不構成 durable HOME replacement。
- OOBE/BOOT_AFTER_SYSTEM_OTA、DCPMS、driver/native 等材料保留為 gated/unknown surfaces；沒有 runtime writer/effect，亦不應用裝置 replay 補洞。

## Reconciliation matrix

完整逐列資料在 [同名 CSV](./luna_worker_cont_ipc_reconciliation_20260810.csv)。CSV 固定欄位為 `id,surface,caller,gate,binder_identity,user_scope,sink,observed_effect,evidence,confidence,missing_edge,next_safe_step`；`confidence` 僅使用 `Confirmed`、`Strong evidence`、`Probable`、`Hypothesis`、`Disproved`、`Unknown`。

| ID | surface | 目前閉合到哪裡 | 未閉合邊 | 判定 |
|---|---|---|---|---|
| IPC-R01/R02 | KFT / child lifecycle | child `UserInfo.id` → Amazon PM setters；local boot path 為 system-server child predicate | external caller、tx3 authorization、PMS cross-user gate、User-0 provenance | Strong evidence / Confirmed（scope） |
| IPC-R03 | Amazon PM metadata | permission gate → flags/metadata persistence | production caller/grant、first consumer、HOME edge | Strong evidence |
| IPC-R04 | Proxy receiver | creator `FLAG_SYSTEM` gate；ordinary probe false | system PendingIntent provenance、receiver/provider inventory | Confirmed boundary |
| IPC-R05/R06 | DPM | restriction owner/admin gates；persistent preferred requires trusted PMS identity | exact owner target/user mapping、resolver outcome | Confirmed / Strong evidence |
| IPC-R07 | Profile tx41 | Binder entry → cross-user startActivityAsUser boundary | production client、map consumers、HOME/PMS edge | Strong evidence |
| IPC-R08 | standard HOME/PMS | saved Fire resolver baseline and standard permission gates | exact runtime caller/permission and User-0 authorization | Confirmed |
| IPC-R09/R10 | ProductPolicy / OOBE | trusted policy/lifecycle writers statically identified | target/user input and natural runtime effect | Strong evidence |
| IPC-R11/R12 | Fire watchdog / hijack prevention | Fire broadcast notification; visibility/permission bookkeeping | receiver handler, native/overlay registration, downstream consumer | Confirmed boundary |
| IPC-R13/R14 | DCPMS / Accessibility | DCPMS read-only; accessibility foreground-only historical result | client identity or persistence outside bounded run | Unknown / Confirmed |

## 最小安全補洞順序

1. 先做 `MigrationService.appsAvailable` 的 Fire Launcher manifest/receiver/handler 靜態 join，確認 broadcast 是否只有 notification consumer。
2. 對 KFT tx3 做離線 APK/native caller、AIDL Stub、privapp、service context/SELinux 與 saved child/User-0 topology join；不得送 tx3。
3. 對 `AmazonApplicationFlags` 與 Profile `launch_info_map_key` 做 consumer-only data-flow，確認是否能抵達 PMS/HOME；不得呼叫 writer。
4. 對 DPM persistent-preferred、Settings default-home 與 PMS protected/resolver checks 做 source/manifest/config/baseline join；不得重放 preferred/set-home/disable。
5. 若上述 joins 仍沒有同時成立的 Fire target + User 0 + accepted gate + HOME/package sink，將候選關閉為 `Disproved` 或 `Unknown`，不升級到裝置操作。

## Evidence limits

`Confirmed` 表示保存檔案中有直接觀察或靜態結構；`Strong evidence` 表示主要邊界已由多份材料支持，但仍有 caller、identity、user scope 或 consumer 缺口；`Unknown` 表示保存 corpus 不足，並非漏洞或成功路徑。Service publication、exported AIDL、interface descriptor、static setter、missing `getCallingUid()` 或 privilege declaration 都不單獨等於 external reachability。

歷史 ADB 只被當作既有結果索引：Phase 10 baseline 保存 User 0 Fire HOME priority 50、User 10 FallbackHome；Phase 11 T01/T02 的 foreground/accessibility 結果均沒有改變 formal HOME。此 worker 沒有重新執行任何裝置命令。
