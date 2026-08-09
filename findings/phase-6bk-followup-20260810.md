# Phase 6BK follow-up：官方兒童設定檔 UI 與 protected broadcast 聯集掃描

日期：2026-08-10（Asia/Taipei）

裝置：Amazon Fire HD 10 2021／KFTRWI／trona

## 結論摘要

- **已證實：** 對 45 個明確指定、已保存的 APK 進行主機端掃描時，
  `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA` 只在
  `android.amazon.perm.apk` 的 `protected-broadcast` 宣告中出現一次；該 APK
  的 `sharedUserId` 為 `android.uid.system`。這不是完整 runtime APK 集合的全域
  證明，而是明確輸入集合內的確認。
- **已證實：** 透過官方 Tahoe「新增兒童設定檔」畫面提交 `TEST` 與日期後，
  User 0 的 HOME、Fire Launcher package state、build fingerprint 與 ADB 連線
  沒有被改成第三方桌面；本次提交後沒有新增可見的 Android user。
- **高可信推論：** Tahoe 應用層 workflow 確實執行了建立／同步兒童資料的工作鏈，
  因為 logcat 出現 `CreateAndroidUserCommand`、
  `RegisterDelegatedAccountCommand`、`ModifyUserInHouseholdModelCommand`、
  `HOUSEHOLD_UPDATED`，但本地 Android User 建立並未在提交後狀態中出現。
- **待驗證：** 雲端 household 是否已提交成功，以及本地 user 建立失敗是因為已註冊
  account、網路／ADM/DCP 服務不可用，還是後續 rollback。現有證據不足以把它寫成
  完整成功或失敗的 KFT `createChildUser()` 執行。
- **已排除（本次範圍）：** 本次沒有停用 Fire Launcher、清除其資料、發送未知 Binder
  transaction、送出 broadcast、執行 OTA/recovery、寫入分割區或執行 Root。

## 1. 裝置與目前工作目錄

專案根目錄：

`/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire`

裝置識別：

```text
serial: G001LT0511550CFT
fingerprint: Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys
current user: 0
HOME: com.amazon.firelauncher/.Launcher, priority 50
```

提交後的唯讀 capture 顯示 User 0 與既有 stopped User 10 仍在，沒有新的 Android
user；完整輸出見：

- `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/users.stdout.txt`
- `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/current_user.stdout.txt`
- `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/home_user0.stdout.txt`
- `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/firelauncher_package.stdout.txt`

## 2. 官方兒童設定檔 UI 嘗試

### 操作與證據

使用已保存的唯讀／前景切換腳本啟動：

```text
com.amazon.tahoe/.settings.household.HouseholdSettingsAddChildActivity
```

原始資料分為不同 run 保存，沒有覆寫：

- `adb/child-profile-tests/CHILD-TEST-20260810-01/`
- `adb/child-profile-tests/CHILD-TEST-20260810-02/`
- `adb/child-profile-tests/CHILD-TEST-20260810-03-POST/`
- `adb/child-profile-tests/CHILD-TEST-20260810-05-POST-RO/`
- `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/`

後續狀態採集腳本：

- `tools/scripts/capture_phase6bk_child_profile_submission.py`

腳本只執行 `get-state`、`getprop`、`am get-current-user`、`pm list users`、
`dumpsys user/package/activity/window`、HOME resolve 與 logcat dump；支援
`--dry-run`，且拒絕覆寫既有輸出。

### 實際結果

表單曾顯示測試姓名、2000-01-01 與預設頭像，並按下 Add profile。提交後回到 Fire
Launcher，但：

1. `pm list users` 沒有新增 Android user。
2. User 0 HOME 仍為 `com.amazon.firelauncher/.Launcher` priority 50。
3. User 0 Fire Launcher 仍是預設 enabled state；沒有執行停用或清除資料。
4. 沒有出現可證明 Child PIN 已設定的獨立畫面或狀態證據；因此不能宣稱本次設定了
   Child PIN。

### Logcat 中可觀察的應用層 workflow

在 `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/logcat_all.stdout.txt`：

- line 1930：`CreateAndroidUserCommand`
- lines 1959–1964：`RegisterDelegatedAccountCommand`，包含 already registered
  account 與 allow-child-profile 訊息
- line 1979：`ModifyUserInHouseholdModelCommand`
- lines 2125–2150：`TimeSpentAddChildApiCall` 與 `AddChildCount=1`
- lines 2231、2360、2527：household loaded，children=1
- lines 2274–2280：`HOUSEHOLD_UPDATED` unicast／receiver 成功
- lines 2667–2684：DCP/ADM `NoNetworkException` 與
  `Unable to register package 'com.amazon.tahoe'`

這些行支持「Tahoe 應用層 workflow 被執行」；但因同一 capture 的本地 user 清單沒有
新增 user，不能把它等同於 system-server 的 `createChildUser()` 已完成。

## 3. Protected broadcast 聯集掃描

主機端輸出：

`artifacts/phase6bk/protected-broadcast-union-20260810-02/`

該輸出包含：

- `summary.json`
- `protected-broadcast-inventory.csv`
- `input-sha256.csv`
- `sha256sums.txt`
- `result.md`
- `protected-broadcast-inventory.mmd`

掃描摘要：

```text
input_apk_count: 45
aapt_failure_count: 0
target_action: amazon.intent.action.BOOT_AFTER_SYSTEM_OTA
target declarations: 1
device_contacted: false
binder_transaction_sent: false
broadcast_sent: false
ota_executed: false
partition_written: false
```

唯一命中來源為：

```text
apk: artifacts/phase6ac/android-amazon-perm-device-20260805-01/android.amazon.perm.apk
package: android.amazon.perm
sharedUserId: android.uid.system
apk SHA-256: 5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058
protected-broadcast count: 158
```

`sha256sum -c sha256sums.txt` 已在該輸出目錄內通過。這裡的判定是
`CONFIRMED_IN_SCANNED_SOURCES`；摘要同時明確保留限制：輸入是明確指定的保存 APK，
不是裝置 runtime PackageManager 的完整全域 inventory。

## 4. 與既有 Phase 6BK 的關係

本次 follow-up 沒有改寫既有 Phase 6BK 結論：

- KFT 內部存在 per-user launcher-state writer 是 **Confirmed（static）**。
- 普通 shell 不能因 `service list` 看見名稱就取得 Amazon 私有 Binder handle。
- User 0 的 Fire Launcher 與正式 HOME 沒有被這次兒童設定檔 UI 提交改變。
- OTA `BOOT_AFTER_SYSTEM_OTA` 是受保護 lifecycle，不能由這次 UI 觀察推導出 shell
  可達的 OTA／root 路徑。

既有整合報告：`findings/phase-6bk-report.md`；既有證據索引：
`findings/phase-6bk-evidence-index.md`。

## 5. Safety / rollback status

本次狀態：

- ADB：`device`
- current user：0
- User 10：保留且停止
- User 0 HOME：Fire Launcher
- Fire Launcher：未停用、未隱藏、未 suspend、未 uninstall、未清除資料
- system/vendor/product/boot/分割區：未寫入
- Root／exploit／未知 Binder transaction／OTA／recovery：未執行

解鎖密碼只作現場 UI 解鎖用途，未寫入 repository、metadata、log 或 Git。

## 6. Remaining questions

1. Tahoe household 的雲端資料是否在 network/ADM failure 前已提交；需要官方服務端或
   下一次正常網路條件下的最小、明確授權 UI 觀察，不能由現有本地 user 清單推論。
2. `CreateAndroidUserCommand` 的 local-user commit／rollback 邏輯要在 host-only
   Tahoe 反編譯中繼續追蹤；不可直接呼叫私有 Binder。
3. 若要確認 Android user 建立，下一個最低風險證據是再次唯讀採集
   `pm list users`、`dumpsys user`、Tahoe household state 與 package state；不需要
   停用 Fire Launcher 或執行 OTA。
