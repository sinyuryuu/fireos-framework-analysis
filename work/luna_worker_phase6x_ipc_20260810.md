# Phase 6X-IPC — host-only static delta

日期：2026-08-10；基準 HEAD：`687a236c0b81e44060b3ec6a5a53fdce74eabf3e`。

本輪只讀 exact-build `decompiled`、`findings`、`work` 與既有 artifacts；未接觸裝置，未執行 `adb`、`service call`、Binder transaction、未知 transaction、broadcast、package/settings mutation，也未修改 Fire Launcher。

## 新差異

既有 phase-6* IPC 證據未列出 `IAmazonKeyguardService` 這組 interface/Stub/Proxy 與其 caller-to-SystemUI path。本輪確認：

```text
IAmazonKeyguardService Proxy
  -> AmazonKeyguardService$2 Stub implementation
  -> Binder.getCallingUid()
  -> checkKeyguardPermissions(uid, IPackageManager)
       CONTROL_KEYGUARD OR com.amazon.permission.AMAZON_CONTROL_KEYGUARD
  -> getKeyguardPermissionVerifiedDefaultPackageFromUID(uid)
  -> IAmazonKeyguardServiceSystemUI
       dismissWithPendingIntent / setAccessibilityInfo / setForegroundColor
```

`checkKeyguardPermissions` 的兩個 `checkUidPermission` 入口可由 exact-build fosservices disassembly 看到；三個 Stub 方法均讀取 `Binder.getCallingUid()`，把驗證後 UID/package 傳入 SystemUI。沒有觀察到 `clearCallingIdentity()` 或 `restoreCallingIdentity()`，因此本資料不把 system-server 身分誤歸給 Binder caller。

這是 privileged SystemUI/keyguard state surface。它不是 Fire Launcher、HOME resolver、preferred activity、PMS enabled/component state、User/Profile writer 或 Settings sink；靜態 sink 存在不等於低權限可達，也不等於 exploit。transaction integer、service-manager publication policy、SELinux 規則、permission protection level、實際 production caller 與 runtime reachability均為 `UNKNOWN`，除非 CSV 另有明示的靜態 caller/gate。

## 去重與邊界

已去重既有 Phase 6X prewarm、6SB/6UI KFT/tx4、Amazon PM metadata、DPM restriction/profile、Profile service、Input/WMS、OOBE/OTA、PMS HOME/preferred/enabled-state，以及 Phase 6WG 已收錄的 DisplayPower、camera-cover Settings、Alexa mode-switch 三組 surface。本輪只保留上述未在既有索引中找到的 keyguard/SystemUI 三個 mutating methods；read-only `isKeyguardVisible` 與 `isSecureForUserId` 不另列。

CSV 固定欄位為 `evidence_id, surface, source, caller, gate, identity_scope, sink, observed_effect, confidence, evidence_file, evidence_sha256, status`。`status=NEW_DIFFERENCE_STATIC_ONLY` 只表示相對既有 corpus 的新靜態差異，不表示漏洞或 exploit。

## 證據雜湊

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`

詳細逐筆欄位與 UNKNOWN 邊界見同目錄的 `luna_worker_phase6x_ipc_20260810.csv`。
