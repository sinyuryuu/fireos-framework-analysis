# Phase 6AJ：Amazon input／Home-key 控制邊界閉合

## 範圍與安全界線

本階段是 host-only、read-only 靜態整合。輸入是 PS7331 的保存 VDEX
disassembly、Amazon input client、Alexa ARIA caller、既有明確序號的 service
list／SELinux AVC capture，以及已完成的 `BootAfterSystemOTAReceiver`
研究報告。

沒有連接 ADB、沒有呼叫 Binder、沒有發送或重播 broadcast、沒有注入 input、
沒有修改 settings/package state、沒有啟動 OTA/OOBE，也沒有寫入裝置或分割區。

Canonical artifact：
`artifacts/phase6aj/input-home-boundary-20260805-05/`

其輸入雜湊、證據 CSV、方法片段與 `sha256sums.txt` 均保存在該目錄。

## Executive result

### 已證實

1. Fire OS system-server 會發布兩個 Amazon 私有 Binder service：
   `amazon_input` 與 `amazon_keyevent`。來源是
   `AmazonInputManagerService.onStart()`，不是 Fire Launcher resolver。
   證據：`6AJ-HOME-001`。
2. 保存的實機 service visibility capture 顯示兩個 service 存在，但 shell UID
   2000 對它們的 `service_manager find` 被 SELinux 拒絕。證據：
   `6AJ-HOME-002`。
3. `registerKeyEventInterceptor()` 不是無條件 callback。它檢查
   `GET_KEYEVENTS`、package whitelist、要求 foreground 時的目前 package、
   key whitelist 與既有 interception collision。證據：
   `6AJ-HOME-003`、`6AJ-HOME-011`。
4. `registerKeyEventListener()` 與 `registerNextKeyEventListener()` 都以
   `GET_KEYEVENTS` 作為 method-local gate；不符合時拋出
   `SecurityException`。證據：`6AJ-HOME-004`、`6AJ-HOME-005`。
5. `setInputFilter()` 的先前未閉合授權已定位：
   `validateInputFilterAccessPermission()` 要求 caller 是 system／updated-system
   app，或具備 `com.amazon.input.permission.FILTER_INPUT_EVENTS`；該權限在
   保存 package dump 中是 `signature|amazon`、source UID 1000。證據：
   `6AJ-HOME-006`。
6. `inject()`／`injectSequence()` 的 checker 會檢查 caller PID／UID、
   `android.permission.INJECT_EVENTS`、`com.amazon.permission.INJECT_EVENTS`
   與 UID 1000 條件；本階段沒有使用 input injection。證據：`6AJ-HOME-007`。
7. `amazon_keyevent` 的 partner／input-locking API 另受
   `SET_PARTNER_APP_INFO`、`INPUT_LOCKING` 或 `GET_KEYEVENTS` 保護；沒有發現
   shell 可寫的 HOME component 設定。證據：`6AJ-HOME-008`。
8. 保存的 Alexa ARIA code 證明一個受信任 Amazon caller 可以取得
   `AmazonInputManager`、註冊特殊按鍵並觀察 keycode 3（HOME）；其功能是在
   partial-screen overlay 中收到 Home 後 dismiss，不是把 HOME resolver 改成
   指定第三方 component。證據：`6AJ-HOME-009`。

### 高可信推論

- `AmazonInputManagerService` 是 privileged input observation／interception
  surface，不是 HOME resolver。其 bounded class scope 沒有出現
  `resolveActivity`、`resolveIntent`、`setPreferredActivity`、
  `replacePreferredActivity`、`startHomeActivity` 或
  `startHomeOnAllDisplays`；這個 negative result 只適用於該 class，不能取代
  對 SystemUI／PhoneWindowManager 的分析。證據：`6AJ-HOME-010`。
- 即使某個合法 Amazon caller 能取得 service handle，callback registration
  仍受 system-app、package whitelist、foreground 與 key map 條件約束；不能
  由此推論普通第三方 APK 有同等能力。證據：`6AJ-HOME-003`、`6AJ-HOME-011`。

### 已排除目前證據支持

- 沒有證據顯示 `amazon_input`／`amazon_keyevent` 直接選擇
  `com.amazon.firelauncher/.Launcher`。
- 沒有證據顯示 `persist.sys.inputdebug` 是 production shell control；保存的
  constructor logic 只在 `Build.IS_DEBUGGABLE` 時讀取該 property，而目前
  PS7331 是 `user/amz-p`、`ro.debuggable=0`。證據：`6AJ-HOME-012`。
- 不能把 Alexa ARIA 的 privileged Home observer 當作第三方 Launcher
  replacement 或 root route。證據：`6AJ-HOME-009`。

### 待驗證

1. 所有 Amazon APK 的 input-service caller 是否已完整盤點；本階段只用保存的
   Alexa ARIA caller 作為一個確定例子。
2. SystemUI／PhoneWindowManager 是否另有獨立的實體 Home key 分支；這不在
   `AmazonInputManagerService` bounded negative result 內。
3. 目前保存 capture 之外，是否有受信任 caller 在自然使用流程中註冊 input
   callback；shell 在現行 SELinux policy 下無法以合法 service lookup 觀察。

## 控制流程

```text
AmazonInputManagerService.onStart()
  -> publishBinderService("amazon_input")
  -> publishBinderService("amazon_keyevent")
  -> shell service_manager find denied
  -> authorized Amazon caller
      -> GET_KEYEVENTS / package whitelist / foreground / key whitelist
      -> input callback registry
      -> optional ARIA overlay Home observation

setInputFilter()
  -> validateInputFilterAccessPermission()
  -> system/updated-system app OR FILTER_INPUT_EVENTS(signature|amazon)
  -> InputManagerService.registerSecondaryInputFilter()

bounded input service
  - no HOME resolver API observed
  - no Fire Launcher component selection observed
```

## `BootAfterSystemOTAReceiver` 關聯項目

此入口已在 Phase 6AG／6R 正式納入研究，這一輪只把它連到 evidence index，
沒有重新觸發或修改 OOBE 狀態。

### 已證實

`BootAfterSystemOTAReceiver` 是受 system-server OTA lifecycle 控制的高影響
OOBE surface：phase 550／`isUpgrade()` sender、protected broadcast、
`OobeHomeActivity` enable side effect 與 setup-state mutation 均已有保存證據。
證據：`6AJ-OTA-001`，詳細來源為 `findings/phase-6ag-boot-after-system-ota-research-item.md`
與 `findings/phase-6r-bootafter-system-ota-authorization.md`。

### 因風險拒絕測試

不執行 `am broadcast`／`cmd activity broadcast` replay、不 enable
`OobeHomeActivity`、不寫入 `user_setup_complete`／`isOOBEActive`、不執行
OTA/updater/recovery、不呼叫未知 Binder transaction。原因是這些操作會改變
setup state 或觸及受保護更新流程，不能作為普通 HOME 實驗。

## 實機驗證判定

本階段沒有新的實機命令，因為既有 read-only capture 已足以閉合兩個關鍵邊界：
service-manager visibility 與 method-local authorization。重新發送未知 Binder
transaction、嘗試 `service call`、注入 Home 或重播 OTA broadcast 都不會增加安全
證據，且可能改變輸入／OOBE 狀態，因此不採用。

## 證據表

| Evidence ID | Finding | Source / method | Confidence |
|---|---|---|---|
| `6AJ-HOME-001` | 兩個 Amazon input service 的發布 | `fosservices/disassembly.log`，`AmazonInputManagerService.onStart()` | 已證實 |
| `6AJ-HOME-002` | shell service lookup 被 SELinux 拒絕 | Phase 6J service list／AVC capture | 已證實 |
| `6AJ-HOME-003` | interceptor 的 permission／whitelist／foreground gate | `registerKeyEventInterceptor()`，line 19829；smali `0x024c3e` | 已證實 |
| `6AJ-HOME-004` | listener 的 `GET_KEYEVENTS` gate | `registerKeyEventListener()`，line 20048；smali `0x025710` | 已證實 |
| `6AJ-HOME-005` | next-listener 的 `GET_KEYEVENTS` gate | `registerNextKeyEventListener()`，line 20077；smali `0x025780` | 已證實 |
| `6AJ-HOME-006` | input-filter 的 system-app／signature permission gate | `validateInputFilterAccessPermission()`，line 22437；smali `0x027b6e` | 已證實 |
| `6AJ-HOME-007` | injection 的 PID／UID／permission gate | `checkInjectEventsPermission()`，smali `0x02667a` | 已證實 |
| `6AJ-HOME-009` | Alexa ARIA 可觀察 Home 以 dismiss overlay | `AriaPartialScreen.java:56,77,174-180,323-335` | 高可信推論 |
| `6AJ-HOME-010` | bounded input service 沒有 resolver API | AmazonInputManagerService class scope | 高可信推論 |
| `6AJ-HOME-012` | production 不以 `persist.sys.inputdebug` 控制 | constructor/static init，smali `0x026c0e-0x026c30` | 已證實 |
| `6AJ-OTA-001` | OOBE/OTA receiver 仍是 static-only 高風險項目 | Phase 6AG／6R reports | 已證實 |

## 可重現命令

```sh
python3 -m py_compile tools/scripts/audit_phase6aj_input_home_boundary.py
python3 tools/scripts/audit_phase6aj_input_home_boundary.py --dry-run
python3 tools/scripts/audit_phase6aj_input_home_boundary.py \
  --output artifacts/phase6aj/input-home-boundary-20260805-05
(cd artifacts/phase6aj/input-home-boundary-20260805-05 && \
  sha256sum -c sha256sums.txt)
```

腳本是 host-only；它不包含 ADB、`service call`、input injection、broadcast
replay、package mutation 或 OTA operation。

## 最終結論

**已證實：** Amazon 的 input/Home-key 私有服務有明確的 privileged caller 與
SELinux／permission 邊界；`setInputFilter` 的授權鏈也已閉合。

**高可信推論：** 這條路徑可讓受信任 Amazon overlay 觀察或消費 Home，但目前
證據不支持它負責正式 HOME resolver selection。

**目前沒有可採用 workaround：** 普通 shell／第三方 APK 沒有合法 service
handle、私有 permission、system-app 身分或 whitelist；因此本階段不產生 PoC，
也不把 privileged ARIA 行為誤稱為 Launcher replacement。
