# Phase 6AB：OTA 輸入驗證與 BootAfterSystemOTAReceiver 研究項目

## 研究定位

本階段把 `BootAfterSystemOTAReceiver` 與同版本 PS7331 OTA 檔案發現、metadata
解析、驗證、staging 及 `UpdateSystem.install` 邊界放在同一條證據鏈中分析。
重點不是嘗試觸發，而是確認這個 OOBE 入口的實際副作用與 OTA 驗證順序。

所有分析均使用已保存的 JADX/VDEX/manifest 輸入，在主機端完成。沒有接觸
設備、送出 broadcast、呼叫 Binder、啟動 OOBE、執行 updater/recovery、建立
OTA payload 或寫入任何分割區。

## 結論摘要

### 已證實

1. `AmazonPackageManagerService.onBootPhase()` 在 boot phase `550` 且
   `PackageManagerService.isUpgrade()` 成立時，建立
   `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA`，並以
   `com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA` 發送。
   保存的 system-server disassembly 範圍是
   `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`。
2. `BootAfterSystemOTAReceiver.onReceive()` 只有在 action 相符、OOBE 尚未有效
   運行且 `retail_demo_mode` 關閉時，才會進入 incremental flow；該 flow 會
   寫入 OOBE preferences、enable `OobeHomeActivity`，並呼叫
   `OOBEActivationHelper.activateOOBEIF()`。
3. `activateOOBEIF()` 將 `user_setup_complete` 設為 `0`、
   `isOOBEActive` 設為 `1`。這是 setup-state mutation，不是普通
   `set-home-activity` 或 HOME resolver mutation。
4. `OobeHomeActivity` 是 `MAIN + SETUP_WIZARD + HOME + DEFAULT`、priority
   `100` 的 setup activity，且宣告 `android.permission.MANAGE_USERS`；保存的
   User 0 package dump 將它記為 disabled。
5. OTA sideload 的保存 Java path 先做 metadata/sanity、RecoverySystem
   package verification 與 device-state checks，之後才經由 `SideloadMover`
   到 `UpdateSystemWrapper.install()`／`UpdateSystem.install()`。
6. 背景 OTA 的 `OSUpdatePropertiesValidator` 另外檢查 `system/build.prop` 的
   version、signature type 與 PVT build type。

### 高可信推論

- 這是高風險的 system-OTA/OOBE lifecycle entry，可能在合法 OTA 後暫時讓
  setup Home flow 成為前景；它不是一般 shell 可寫的 HOME selector，也沒有
  證據顯示它能把第三方 Launcher 變成正式 HOME。
- `SideloadFilenameFilter` 的預設規則為
  `update-.*\\.(bin|zip)$`，而 `accept()` 使用 `Pattern.matcher(name).find()`。
  這只代表檔案發現規則可由 OTASettings 供應；不能推論可跳過 metadata、
  package signature 或 recovery verification。
- Java source 範圍沒有觀察到 `canonical`/`realpath`/`readlink`/`lstat`/
  `O_NOFOLLOW` marker，但 native File/Zip/RecoverySystem/UpdateSystem 與
  缺失的 `Sideload` 類別尚未閉合，因此這不是 symlink/traversal 漏洞結論。

### 待驗證

- 完整 matching build 的 protected-broadcast/runtime caller authorization。
- `Sideload.java` / `BuildProperties.java` 的 native parser、path semantics 與
  implementation/contract 完整 provenance；目前已由分開保存的 OTA contract
  JADX tree 補上 Java model，但 native 行為仍未閉合。
- native `RecoverySystem`、`UpdateSystem`、ZipFile 與 filesystem mount policy
  對 staging path 的實際處理。
- 研究者日後正常完成官方 OTA 時，receiver、OOBE component、ActivityTaskManager
  與 HOME resolver 的自然時間順序。

### 已排除目前證據支持

- `BootAfterSystemOTAReceiver` 是普通 shell HOME replacement。
- manifest receiver 沒有 component-local `android:permission`，就代表 shell
  可以安全送達或能安全重放該 action。
- filename filter 本身能繞過 OTA 的 metadata、簽章或 recovery 檢查。
- 這條鏈提供了已證實的 root、SELinux bypass 或 Fire Launcher 停用入口。

### 因風險拒絕測試

拒絕手動 `am broadcast`、啟用 `OobeHomeActivity`、修改
`user_setup_complete`/`isOOBEActive`、清除 OOBE data、執行 OTA/updater/recovery、
crafted OTA、symlink/traversal payload、未知 Binder transaction、reboot 以製造
事件，以及任何 partition/system write。這些操作可能重新開啟 OOBE、破壞正常
設定流程或需要 factory reset 才能恢復。

## 主要控制鏈

```text
system_server boot phase 550 + isUpgrade()
  → BOOT_AFTER_SYSTEM_OTA
  → BootAfterSystemOTAReceiver.onReceive()
  → OOBE predicates
  → incremental preferences + enable OobeHomeActivity
  → OOBEActivationHelper.activateOOBEIF()
  → setup-state / OOBE flow
```

平行的 OTA 檔案鏈為：

```text
external-storage filename
  → SideloadFilenameFilter
  → SideloadFactory / BuildPropertiesFactory
  → system/build.prop Properties
  → SideloadMetadataChecker
  → RecoverySystemWrapper.verifyPackage
  → SideloadDeviceStateChecker
  → SideloadMover
  → UpdateSystemWrapper.install
  → UpdateSystem.install
```

這兩條鏈相鄰但不是同一個 HOME resolver API；不能把 OOBE Home 的 priority 100
誤寫成普通 Launcher replacement。

## 可重現產物

主機端生成器：

```sh
python3 tools/scripts/audit_phase6ab_ota_input_validation.py \
  --output artifacts/phase6ab/ota-input-validation-20260805-03 --dry-run

python3 tools/scripts/audit_phase6ab_ota_input_validation.py \
  --output artifacts/phase6ab/ota-input-validation-20260805-03

cd artifacts/phase6ab/ota-input-validation-20260805-03
sha256sum -c sha256sums.txt
```

產物包含：

- `ota-input-validation.csv`
- `input-sha256.csv`
- `summary.json`
- `result.md`
- `ota-input-validation.mmd`
- `sha256sums.txt`

輸入與產物 hash、每個 evidence ID 及限制均保留在 artifact 內。新的 artifact
納入 `ota-contracts-ps7331-jadx-20260805-01` 中的 `Sideload.java` 與
`BuildProperties.java`；implementation tree 與 contract tree 仍分開標示，沒有
把不同來源當成同一個反編譯輸出。

## Source-scope correction

既有 `...-02` artifact 保持不可變，作為當時 selected-source scope 的歷史記錄。
`...-03` 以 alternate contract tree 補上 Java model coverage：`Sideload` 是
Parcelable，攜帶 `File` 與 `BuildProperties`；`BuildProperties` 映射
`ro.build.version.number`、`ro.product.device`、signature/build/product 欄位。
這只修正 decompiler coverage，不改變 OOBE/OTA runtime 的風險判定，也沒有送出
broadcast、Binder、OTA 或修改設備。

## 下一個安全研究項目

1. 只做 host-only 的 matching framework/native artifact provenance，補齊
   protected broadcast、`Sideload` model 與 `UpdateSystem` 呼叫邊界。
2. 若研究者日後正常完成官方 OTA，事後使用 read-only ADB 保存 package、settings、
   task、resolver 與 logcat 時序；不為了研究重播 action。
3. 若上述證據仍不能建立新的合法控制面，將此入口正式結案為「高風險
   OTA/OOBE lifecycle surface，非可採用 workaround」。
