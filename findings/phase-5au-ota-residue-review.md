# Phase 5AU：PS7330 OTA 殘留與更新服務唯讀檢查

## 範圍

本輪只針對目前實機的 Fire OS 7.3.3.0 / PS7330.4104N 做唯讀檢查，目標是確認裝置是否留下可直接辨識的正式 OTA 檔名、Build ID、下載 URI 或待安裝狀態。

沒有執行更新檢查、下載、安裝、sideload、重開機、settings 修改、package 修改、root、bootloader 或分割區操作。OTA debug dashboard 的嘗試只是一個前景 Activity 權限邊界觀察；它被拒絕後以 KEYCODE_HOME 恢復 Fire Launcher。

完整原始輸出保留在本機：

adb/phase5/PHASE5AU-OTA-RESIDUE-20260804-01/

該目錄包含裝置序號、帳號／區域、Wi-Fi 顯示名稱、PlayReady 摘要及完整 dumpsys，因此不提交到公開 repository。公開 repository 僅提交本報告、證據索引、分析腳本及 APK 靜態分析摘要。

## A. 實機版本識別

**已證實：**

| 欄位 | 實際值 |
|---|---|
| Model | KFTRWI |
| Product / device | trona |
| SoC | MT8183 |
| Android | 9 / API 28 |
| Fire OS | 7.3.3.0 |
| Build ID | PS7330.4104N |
| Lab126 build | 4104 |
| Fingerprint | Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys |
| Incremental | 0030099376260 |
| Security patch | 2024-02-01 |
| Kernel | 4.4.146+ |
| Verified boot | 先前基線為 green |
| OTA package path | /system/priv-app/DeviceSoftwareOTA/DeviceSoftwareOTA.apk |

本段直接來自 getprop 與 pm path 的 exact-device capture，見 P5AU-DEV-001、P5AU-PKG-001。

## B. OTA 相關 package 與服務

**已證實：**

pm list packages 的 OTA/update 相關結果為：

- com.amazon.kindle.otter.oobe.forced.ota
- com.amazon.dcp.contracts.library
- com.amazon.dcp
- com.amazon.dcpms.client
- com.amazon.settings.systemupdates
- com.amazon.device.software.ota
- com.amazon.dcp.contracts.framework.library
- com.amazon.device.software.ota.override
- com.amazon.dcpms.fos.service

com.amazon.device.software.ota 的 package dump 顯示：

- codePath：/system/priv-app/DeviceSoftwareOTA
- versionCode：6360610
- versionName：6.0.202217.0_6360610
- userId / shared UID：10017
- privateFlags：PRIVILEGED
- dataDir：/data/user/0/com.amazon.device.software.ota
- 含 OTABootReceiver、OTACheckForUpdatesReceiver、OTADeferredOSInstallReceiver、OTAReplacedReceiver、OtaService 等元件
- OTA controller / monitor / pending-update 相關 permission 為 signature 或 privileged 邊界

這證明 OTA 控制器存在且是 privileged system app；不證明目前有 PS7330 更新包或 pending update。

system_update dump 為空，updatelock 顯示 token count 0。完整 dumpsys 只看到 OTA service 的 receiver／broadcast 註冊，例如 com.amazon.dcp.ota.action.OTA_BROADCAST；這是服務存在的證據，不是待安裝更新的證據。

## C. 可讀路徑與 OTA 檔案搜尋

**已證實，範圍受 shell 權限限制：**

- /cache 與 /cache/recovery：Permission denied
- /data/ota、/data/ota_package、OTA app private data、update_engine 相關 private path：Permission denied 或不可列舉
- /cache/recovery/last_log 與 last_install：因目錄／檔案讀取權限被拒，空輸出不能解讀成「檔案不存在」
- /sdcard/Download：只列出一個 Microsoft Remote Desktop APK，沒有 OTA bin、zip 或 PS7330/PS7331 檔名
- 在 shell 可見範圍內對 /cache、/data、/sdcard 做有界檔名搜尋，沒有回傳 OTA、update、PS7330、PS7331、kindle、bin 或 zip 結果

因此：

**已證實：** 在目前 shell 可見的使用者／共享儲存範圍沒有找到殘留 OTA 檔案。

**無法取得證據：** 不能從本輪 shell 權限證明 /cache、/data/ota_package 或 OTA app 私有資料庫中不存在檔案。

## D. settings 與更新狀態

global settings 中與 OTA／版本相關的值包括：

- ota_disable_automatic_update=1
- database_creation_buildid=PS7324.3016N
- persist.sys.ota.isScreenOffBeforeOTA=false
- restore_blocked_for_ota=0
- persist.sys.DaysFromOTA_V390=8000
- persist.sys.DaysFromOTA_V395=8000
- persist.sys.DaysFromOTA_V400=8000
- persist.sys.DaysFromOTA_V410=8000
- device_provisioned=1

**已證實：** ota_disable_automatic_update=1 是目前可讀到的 OTA 自動更新控制值。

**待驗證：** database_creation_buildid=PS7324.3016N 的語意與寫入來源；它不是目前 firmware fingerprint，也不是 pending OTA URI。

本輪沒有修改任何 settings。特別沒有嘗試清除或改寫 ota_disable_automatic_update，因為那會改變裝置更新策略而不是單純觀察。

## E. OTA debug UI 權限邊界

嘗試啟動：

am start -W -n com.amazon.device.software.ota/.dx.OtaDashboardActivity

結果：

Permission Denial：shell UID 2000 缺少 com.amazon.dcp.permission.DISPLAY_DEBUG_UI。

ActivityManager stack 顯示拒絕點為：

- ActivityStackSupervisor.checkStartAnyActivityPermission
- ActivityStarter.startActivity
- ActivityManagerShellCommand.runStartActivity

**已證實：** OTA debug dashboard 不是 shell 可直接使用的公開控制入口。

**因風險／權限拒絕測試：** 沒有嘗試授予該 privileged permission、呼叫私有 Binder、猜 transaction code 或繞過 Activity 權限。拒絕後裝置已回到 com.amazon.firelauncher/.Launcher。

## F. OTA APK 離線靜態分析

repository 內既有 OTA APK：

- artifacts/phase3b-ota/com.amazon.device.software.ota__0_DeviceSoftwareOTA.apk
- SHA-256：4a00b81fda6259e1309d9c6c3021e7d958be8bc6341a49b1278216580824b2a0
- artifacts/phase3b-ota/com.amazon.device.software.ota.override__0_DeviceSoftwareOTAIdleOverride.apk
- SHA-256：b0d78110e5f1b58efc7c741936fcc2233c05a06ea5bd65f4cf2237c3e3c1118b

JADX 1.5.6 的離線分析找到：

- DBHelper 建立 updates.db
- PublishedUpdates 表含 RemoteURI 欄位
- PendingUpdates 表含 LocalURI 欄位
- OTADataDirectory 優先使用 /data/ota_package/；若不可用，改用 app external files directory
- SideloadDirectory 會掃描 external storage
- OTABootReceiver 在開機路徑安排 OTA check
- UpdateSystemWrapper.install() 最終使用 UpdateSystem.install()

**高可信推論：** OTA framework 確實具備保存 remote URI、pending local URI 與 sideload 路徑的資料模型。

**無法取得證據：** shell 無法讀取 OTA app private data，因此本輪不能把 updates.db 的實際內容、RemoteURI、LocalURI 或 pending record 取出。

**安全界線：** 沒有執行 UpdateSystem.install()，沒有觸發 check/download/install，也沒有對 app private data 做權限繞過。

## G. 結論

1. **已證實：** 裝置目前仍是 exact PS7330.4104N / Fire OS 7.3.3.0。
2. **已證實：** privileged OTA package 與完整 OTA receiver/service 存在。
3. **已證實：** shell 可見的 Download 與 bounded path search 沒有殘留 PS7330 OTA bin/zip。
4. **已證實：** system_update 沒有提供 pending state；updatelock token count 為 0。
5. **已證實：** OTA debug dashboard 需要 Amazon 私有 privileged permission，shell 不能直接開啟。
6. **高可信推論：** 目前沒有可由普通 ADB shell 直接取出的正式 PS7330 下載 URI 或更新包。
7. **無法取得證據：** OTA app private database、/cache recovery log 與 /data/ota_package 的真實內容。
8. **待驗證：** Amazon 是否曾在該 private database 保存過已完成、已刪除或尚未同步的歷史 RemoteURI。
9. **已排除本輪方向：** 不需要為了尋找殘留包而更新到 PS7331；也沒有理由把 database_creation_buildid 當成目前可用的 PS7330 OTA 檔名或 S3 URL。

## H. 下一個低風險研究點

若仍要追查歷史 OTA URI，下一步應只做：

- 取得官方／授權的 exact PS7330 OTA 備份或合法 app-data export；
- 只讀分析 OTA APK 的公開／可讀設定與 manifest；
- 比對本機 OTA package hash、版本與 Phase 3B 已保存 artifact；
- 維持 ota_disable_automatic_update=1，不觸發更新流程。

不應做：

- 授予 DISPLAY_DEBUG_UI；
- 猜測私有 Binder transaction；
- 讀取或修改受限 app data；
- 執行 OTA install；
- 將 PS7331 當成 PS7330 recovery 或 root input。
