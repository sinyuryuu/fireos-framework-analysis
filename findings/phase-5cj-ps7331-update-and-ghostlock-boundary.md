# Phase 5CJ：PS7331 官方 OTA 安裝結果與 GhostLock 邊界

日期：2026-08-04
範圍：Fire HD 10 11th Generation／KFTRWI／trona；官方 Amazon PS7331 OTA；GhostLock 公開專案的 target-profile 比對。
裝置操作：只使用 Amazon 原生 System Updates UI；沒有 fastboot、bootloader、root、exploit、未知 ioctl、remount 或手動分割區寫入。

## 結論先行

### 已證實

1. 官方更新器已把裝置從 PS7330 更新至 PS7331。更新後 fingerprint 為：

   ```text
   Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys
   ```

   incremental 為 `0031575863172`，security patch 為 `2024-08-01`。

2. 更新是透過 Amazon 原生 `com.amazon.settings.systemupdates/.SystemUpdatesActivity`
   接受本機完整 OTA；更新前 log 顯示 sideload installer 通過電量、cache 與外部儲存空間檢查，並進入 OTA task staging。

3. 更新後 ADB 已恢復，裝置仍在 Android ADB mode；Verified Boot 為 `green`、
   `ro.boot.flash.locked=1`、SELinux 為 `Enforcing`。沒有進入 fastboot，也沒有手動發出 reboot。

4. 更新後仍使用 privileged Fire Launcher：

   ```text
   /system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
   versionName=1.3.239105.0_89024510
   ```

5. `ota_disable_automatic_update` 已由本研究在更新前從 `1` 改為 `0`，更新後仍為 `0`；這是唯一為了恢復 OTA 檢查而改動的 setting。原始恢復命令仍是將該值寫回 `1`，但本輪暫不恢復，因研究者要求重新開啟 OTA。

6. 更新後本機 OTA 檔已由 updater 移除；這符合已完成安裝的觀察，但不把檔案刪除本身當成安裝成功的唯一證據。

### 高可信推論

- PS7331 已經是裝置實際執行中的 kernel／framework build，因此後續只讀行為觀察可以直接標記為 PS7331 runtime scope，不再只是相鄰版本 source evidence。
- 更新後 resolver 暫時回傳 `com.amazon.kindle.otter.oobe/.OobeHomeActivity`
  （priority 100），而 `user_setup_complete=0` 且螢幕仍在鎖定畫面；這應先視為更新後 OOBE／user-setup 狀態，不是 Fire Launcher 被替換，也不是 GhostLock 或 HOME resolver 的新結論。
- 官方 `ghostlock-emerald` 專案的 README／Makefile 對應的是 Poco M6 Pro、MT6789、Android 16、kernel `6.12.30-android16-5`，而本機 PS7331 是 MT8183、Android API 28、Linux 4.4.146+。兩者沒有足夠 target-profile 相容性，不能直接將其 binary、layout 或 root layer 套用到 Fire。

### 待驗證

- 研究者完成更新後首次解鎖／設定流程後，PS7331 的正常 HOME resolver、preferred state 與 Home key 行為。
- PS7331 實際執行中的 `remove_waiter()` 是否能被非特權 Android userspace 走到 proxy failure，以及是否會留下可觀察的 invariant violation。
- PS7331 是否有 release-CI 或未公開 binary patch，使其與公開 source／已檢查 Image 的 GhostLock marker 不同。

### 已排除／不採用

- 「PS7331 更新完成」等於「GhostLock 可以取得 root」：沒有這種證據。
- 「ghostlock-emerald 可編譯」等於「可在 KFTRWI/trona 執行」：目標 SoC、kernel ABI、Android 版本與 build assumptions 均不同。
- 將官方完整 OTA 視為 standalone `boot.img` 寫入；本次是由 Amazon updater 依官方流程處理完整 OTA，不提供獨立 boot flash 的證明。
- 將更新後 OOBE priority 100 誤判為一般第三方 Launcher 勝過 Fire Launcher；目前 OOBE 是 privileged system component，且 user setup 尚未完成。

### 因風險拒絕測試

本輪未執行 futex race、GhostLock PoC、kernel memory read/write、root payload、
未知 ioctl、BROM/DA、preloader/LK、fastboot unlock/flash、boot image 寫入、
remount、SELinux 修改或任何非官方分割區操作。這些步驟會把 source-level
研究轉成未授權提權或 boot-chain 破壞，且目前沒有可接受的安全回復條件。

## 實際更新證據

| Evidence ID | 原始證據 | 觀察 | 信心 |
|---|---|---|---|
| `P5CJ-OTA-001` | `adb/phase5/PS7331-UPDATE-PRE-20260804-01/after_update_button_logcat.txt` | `SideloadInstaller` 開始安裝 PS7331 檔案；battery、cache、external storage checks 通過；OTA task 開始執行 | Confirmed，update-start scope |
| `P5CJ-OTA-002` | `adb/phase5/PS7331-UPDATE-POST-20260804-01/device/fingerprint.stdout.txt` | 實際 fingerprint 為 PS7331.4463N | Confirmed，device runtime |
| `P5CJ-OTA-003` | `adb/phase5/PS7331-UPDATE-POST-20260804-01/device/incremental.stdout.txt`、`security_patch.stdout.txt` | incremental `0031575863172`、patch `2024-08-01` | Confirmed，device runtime |
| `P5CJ-OTA-004` | `adb/phase5/PS7331-UPDATE-POST-20260804-01/boot/verifiedbootstate.stdout.txt`、`flash_locked.stdout.txt`、`device/getenforce.stdout.txt` | green、locked、Enforcing | Confirmed，security-state snapshot |
| `P5CJ-OTA-005` | `adb/phase5/PS7331-UPDATE-POST-20260804-01/device/uname.stdout.txt`、`proc_version.stdout.txt` | Linux 4.4.146+、aarch64、Android clang 6.0.2 build | Confirmed，device runtime |
| `P5CJ-OTA-006` | `adb/phase5/PS7331-UPDATE-POSTCHECK-20260804-01/` | ADB state、fingerprint、Fire Launcher path 與 resolver 的完整原始輸出及 SHA-256 | Confirmed，read-only postcheck |
| `P5CJ-HOME-001` | `adb/phase5/PS7331-UPDATE-POSTCHECK-20260804-01/resolver.stdout.txt`、`activity_top.stdout.txt` | resolver 暫時選 OOBE；activity dump 顯示鎖定狀態與既有測試 task | Confirmed，post-update/OOBE scope |
| `P5CJ-OTA-007` | `adb/phase5/PS7331-UPDATE-PRE-20260804-01/ota_setting_*` 與更新後 `settings get` | OTA automatic-update setting 為 `1 → 0` 並保持 `0` | Confirmed，single-setting mutation |

## GhostLock target-profile 比對

公開專案：<https://github.com/datfooldive/ghostlock-emerald>

該專案公開 README 將 target 描述為 Poco M6 Pro（MT6789），kernel
`6.12.30-android16-5-g6e872b4863d6-ab13847919-4k`；其 Makefile 使用 API 35
的 AArch64 Android NDK compiler，並組合 target-specific source、device config
與 root-related components。這些資料足以確認它是針對另一個 kernel generation
與另一個 SoC 的專案，不足以證明 Fire PS7331 的 ABI 或 exploitability。

本次只讀 pinned provenance：

```text
repository=datfooldive/ghostlock-emerald
HEAD=ebb355d302629a034d0959e5e579496559e8f84e
Makefile_API=35
```

只讀命令為 `git ls-remote ... HEAD` 與對應的 GitHub raw README/Makefile
metadata；沒有 clone、build、install 或 execute。

本專案保存的 PS7331 exact source 仍顯示：

- build-selected `rtmutex.c`：`artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- build-selected `futex.c`：同一 source archive 的 `kernel/mediatek/mt8183/4.4/kernel/futex.c`
- official OTA-derived `boot.img`：`firmware/extracted/PS7331/boot.img`

前述 artifacts 的既有分析仍只能支持「source／inspected Image 與 pre-fix
cleanup pattern 一致」；它不提供 runtime address、KASLR offset、race trigger、
arbitrary read/write 或 UID transition 證據。

## 下一個安全研究步驟

1. 等裝置由研究者完成更新後的首次解鎖／OOBE；只讀重新擷取 HOME resolver、
   `dumpsys activity`、preferred records 與 package state。
2. 將正常 PS7331 runtime identity 與 exact source／boot artifact hash 綁定。
3. 以 host-only model／source review 繼續檢查 ABI、return-path 與 cleanup
   consumer；不在真機觸發 futex race 或執行 root payload。
4. 若研究目標改為正式 HOME 行為，先清理或明確標記仍安裝的研究 Launcher，
   但不得在未建立可逆 snapshot 前變更核心 package state。

## 可重現命令

```sh
bash tools/scripts/capture_phase5_low_level_baseline.sh \
  --serial DEVICE_SERIAL \
  --test-id PS7331-UPDATE-POST-YYYYMMDD-NN \
  --output adb/phase5/PS7331-UPDATE-POST-YYYYMMDD-NN

bash tools/scripts/capture_phase5ba_device_postcheck.sh \
  --serial DEVICE_SERIAL \
  --output adb/phase5/PS7331-UPDATE-POSTCHECK-YYYYMMDD-NN
```

上述腳本只做明確序號限定的 ADB read-only capture；本地 raw evidence 不應在
公開 commit 中包含裝置序號、個人畫面或完整設定資料。
