# Phase 6MF residual candidates（2026-08-10）

## 範圍與判定

本整理只讀目前工作樹中的 findings、既有 artifacts、scripts 與 tables；沒有
執行 adb、網路、Binder/service call、ioctl、Root/exploit、OTA/recovery/
fastboot/reboot，也沒有修改裝置。Phase 3A–6ME 已完成的實驗不重跑。

判定問題限定為：是否仍有最小、未閉合且與 User-0 HOME/package/component
writer，或 ordinary-app IPC caller-to-sink 有關的候選。

## 最小 residual candidates

| ID | 最小候選 | 目前狀態 | 為何仍未閉合 | 安全邊界／處置 |
|---|---|---|---|---|
| R1 | `PackageHelper.setComponentEnabledSetting()` 的 exact user scope；以及 OOBE `BootAfterSystemOTAReceiver` → `OOBEActivationHelper` 的 User-0 component-state data flow | **待驗證；因風險拒絕 live 驗證** | 6N 明確保留 helper user scope；6Q/6KY 只證實可在合法 OTA/OOBE lifecycle 下啟用 `OobeHomeActivity`，沒有證實普通 User-0 HOME preferred writer 或 Fire package-state restoration | 只可對既有 Fire framework/OOBE source 做 host-only method/data-flow closure。不得人工 broadcast、enable OOBE、寫 setup state 或執行 OTA/recovery。證據：`findings/phase-6n-report.md:55-110`、`findings/phase-6q-binder-service-and-oobe-audit.md:290-356`、`findings/phase-6ky-follow-up-closure.md:55-70` |
| R2 | Amazon `fosinit` runtime-loaded callback／manifest completeness，特別是可能未納入既有 VDEX/XML scope 的 package/HOME callback | **待驗證（host-only completeness gap）** | 6KV/6KW/6KY 已閉合所選 VDEX callback 與 25 個 PMS/package/preferred sink call sites，但仍未證明所有 runtime-loaded `fosinit` callback 都在保存 corpus；若存在未索引 callback，才可能新增 User-0 writer | 只做既有 artifact 的 manifest/hash/class-loader inventory；只有同時找到 concrete package/component 或 preferred-activity sink、User-0 scope、以及合法 caller gate 才能升格為候選。證據：`findings/phase-6kv-pms-home-caller-closure.md:131-159`、`findings/phase-6kw-current-closure.md:39-59`、`findings/phase-6ky-follow-up-closure.md:145-155` |
| R3 | `PackageManagerDenyList` 中 `com.amazon.firelauncher` 的 exact membership | **待驗證；因風險拒絕直接取得內容** | 6V 已閉合 protected-package callback 的 predicate、caller UID 2000 gate 與實機 disable rejection，但保存 shell capture 只有 system-owned file metadata，沒有 entry 內容；membership 仍是 indirect inference | 這是既有 PMS package-state writer gate 的 provenance gap，不是新的 writer 或 bypass。不得讀寫 system-owned deny-list、發送 Arcus action 或嘗試繞過 protected gate。證據：`findings/phase-6v-pms-control-surface-review.md:118-141`、`findings/phase-6v-evidence-index.md:21-25` |

### Residual candidates 的共同結論

R1–R3 都是 host-only 證據完整性問題，沒有一項目前形成可安全執行的
ordinary-app → User-0 HOME/package/component sink。R1 可能是 setup-only
component writer；R2 是未完成的 corpus completeness；R3 是 protection-gate
membership provenance。不能把任一項寫成 HOME replacement、permission bypass
或 root 結果。

## 已閉合／重複項目

| 項目 | 結論與既有證據 |
|---|---|
| ordinary-app `preWarmApplicationForUser()` | **已閉合，勿重跑。** 6KU 已確認 ordinary no-permission APK 可到達 AMS prewarm，sink 是 process/resource use；不呼叫 HOME resolver、preferred-activity、package/component setter 或 Fire restoration。6K/6N 的「permission-check 結果未消費」只保留為 authorization review，不是 HOME writer。證據：`findings/phase-6ku-low-privilege-boundary.md:13-18,89-109`、`findings/phase-6ky-follow-up-closure.md:72-85`。 |
| KFT `enableKftLauncherComponent(UserInfo)` / tx3 | **已閉合為 child/profile-scoped writer，User-0 路徑未成立；勿重跑。** 它寫 Tahoe、Fire、Launcher3 的 supplied-user state；6KQ/6O/6KV/6KU 的既有邊界顯示 User-10 lifecycle 與 PMS caller/protection gate，沒有 User-0 replacement。證據：`findings/phase-6o-control-boundary.md:9-24`、`findings/phase-6kq-kft-tahoe-component-protection-boundary.md:82-89,169-173`。 |
| 標準 PMS HOME setter／DPM preferred HOME | **已閉合／重複。** `setHomeActivity()` 是已知 formal sink；既有 preferred record 仍不能勝過 Fire priority 50，DPM 需合法 admin/Profile Owner，沒有新 Amazon User-0 writer。證據：`findings/phase-6kr-pms-writer-baseline.md:57-75,154-168,252-257`、`findings/phase-6kv-pms-home-caller-closure.md:109-147`。 |
| AppCompat/Eve resolver callbacks | **已閉合。** AppCompat 委派 AOSP resolver，Eve 為 null fallback；沒有 Fire literal 或 preferred/package-state write。證據：`findings/phase-6ky-follow-up-closure.md:38-53`。 |
| private Amazon Binder service 可達性 | **已閉合為 ordinary caller contract／service visibility boundary；勿猜 transaction。** 保存 capture 顯示 shell `service_manager find` 被拒；6KU 已證明的 prewarm 例外 sink 仍僅 process/resource，不是 HOME/package/component writer。證據：`findings/phase-6n-ipc-provenance.md:43-62`、`findings/phase-6q-binder-service-and-oobe-audit.md:29-35,337-341`。 |

## 明確排除或因風險拒絕

- **Native updater / recovery / OTA path：** 6MD/6P/6O 已證實 privileged
  extraction/partition-write capability，但沒有 Fire Launcher、HOME resolver 或
  User-0 preferred sink，也沒有 shell/ordinary-app direct execution route；剩餘
  CFG、canonicalization、recovery verifier 問題不屬本輪目標，且因風險拒絕執行。
  證據：`findings/phase-6md-native-updater-path-audit.md:18-26,104-132`、
  `findings/phase-6p-native-updater-closure.md:48-60`。
- **手動 OOBE/OTA activation、unknown Binder transaction、Fire package
  disable/hide/suspend/uninstall/clear、driver ioctl/DMA/race、Root/partition
  write：** 明確拒絕；不列為可行 residual candidate。
- **ASP tablet branch、CMDQ/GED/sysenv/IDME/kernel surfaces：** 已確認與 HOME、
  package/component writer 無 sink 關聯，分類為重複／範圍外；不列入候選。
  證據：`findings/phase-6ky-follow-up-closure.md:97-127`。

## Phase 6MF stop point

本輪最小清單為 **R1–R3**；其中只有 R1/R2 可能在 host-only source/corpus
completeness review 後改變 User-0 writer 判定，R3 只會補強既有 protected-package
解釋。沒有理由重跑已完成的 Phase 3A–6ME 實驗，亦沒有安全理由將任何 residual
升級成裝置 mutation 或 exploit 假設。
