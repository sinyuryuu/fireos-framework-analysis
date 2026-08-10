# Phase 6PT — Broad privilege-surface closure

日期：2026-08-10  
裝置基線：`G001LT0511550CFT` / Amazon Fire HD 10 KFTRWI / `trona`  
Build：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`  
基準公開提交：`8e37de71b7f2a953b1a8a9e6a0565aff0b31a322`

## 執行範圍

本輪將研究範圍擴展至 Launcher 之外：package/component state、preferred
activity、user/profile、settings、process、DPM、Play Store、KOR、managed
provisioning、OTA、driver 與 kernel 候選。新增分析均以已保存的 PS7331 APK、
JADX、manifest、package dump、privapp XML、Binder disassembly 與既有唯讀
capture 為輸入。

本輪沒有執行 ADB、Binder/service call、ioctl、broadcast、provider write、
package mutation、permission mutation、install/start、reboot、OTA/recovery、
root、exploit 或分割區操作。既有原始 evidence 沒有覆寫。

新增的實機唯讀 capture：
`adb/phase6pt/PHASE6PT-READONLY-20260810-01/`；其中
`sha256sum -c sha256sums.txt` 已通過。設備仍是指定序號、`uid=2000(shell)`、
SELinux `Enforcing`，HOME 仍解析為 Fire Launcher，candidate set 仍是 Fire
50、Microsoft 0、FallbackHome -1000。

## Executive result

**已證實：** Fire OS 有多個高影響 permission holder，包含
`CHANGE_COMPONENT_ENABLED_STATE`、`MANAGE_USERS`、`INSTALL_PACKAGES`、
`DELETE_PACKAGES`、`WRITE_SECURE_SETTINGS` 與 `FORCE_STOP_PACKAGES`；
`com.android.vending` 甚至是 `/data/app`、沒有已擷取的
`PRIVATE_FLAG_PRIVILEGED`，但仍有 package-management grant rows。

**已證實：** KFT 的 system-server code 具備對 child/profile user 設定
Fire/Tahoe/Launcher3 state 的 writer；既有 User 10 與 User 0 實機測試分別
在 cross-user gate 與 protected-component gate 被拒絕。這是 trusted lifecycle
capability，不是普通 caller capability。

**已證實：** 目前能由 ordinary APK 實機閉合的代理只有兩個有限結果：

1. `IAmazonActivityManager` tx1 可讓 system-server `startProcessLocked`
   建立指定 process（prewarm），但沒有 package、HOME 或 UID transition sink。
2. `IAmazonUserManager` tx4 可寫入兩個固定 setup flags，且已回復；沒有
   package、HOME 或 system/root sink。

**高可信推論：** 高權限 permission row 不等於可接受的高權限操作。任何
package/component setter 仍須通過 system-server 的 protected-package、user、
permission 或 policy gate；`clearCallingIdentity()` 也只改變服務在後端執行
系統操作時的身分，不會把未授權 caller 變成 root。

**未發現：** 普通 app／shell 到 system UID 或 root 的可重現 transition；
新的正式 HOME replacement；Play Store、KOR、H2 或 managed provisioning
可由普通 caller 直接改 Fire Launcher 的閉合鏈。

## 高影響 holder inventory

保存的 Phase 6MC table 有 60 rows／59 packages，所需 permission family
計數為：`CHANGE_COMPONENT_ENABLED_STATE` 12、`WRITE_SECURE_SETTINGS` 45、
`MANAGE_USERS` 37、`INSTALL_PACKAGES` 7、`DELETE_PACKAGES` 8、
`FORCE_STOP_PACKAGES` 3。完整逐 package 資料與 UNKNOWN 欄位保留於：

- `work/luna_worker_high_privilege_holder_inventory_20260810.csv`
- `work/luna_worker_high_privilege_holder_inventory_20260810.md`

其中不能將 holder row 解讀為 caller reachability。`STATUS_BAR_SERVICE`、
`INJECT_EVENTS`、`DUMP`、`INTERACT_ACROSS_USERS(_FULL)` 與 Amazon profile
permission 的 holder inventory 沒有在保存表中完整保留，因此本報告標為
UNKNOWN，而不是宣稱沒有 holder。

## 主要路徑判定

### 1. Fire/KFT package-state writer

`AmazonUserManagerService.enableKftLauncherComponent(UserInfo)` 在保存的
system-server disassembly 中寫入：

```text
com.amazon.tahoe/.launcher.FreeTimeLauncherActivity -> ENABLED
com.amazon.firelauncher                         -> DISABLED
com.android.launcher3                           -> DISABLED
```

證據位置：`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`。
但相同 tx3 的既有實機結果是：User 10 被 cross-user gate 擋下，User 0 在
第一個 component setter 被 protected gate 擋下。這條測試前提未變，故本輪
不重播。

判定：**已證實 static capability；ordinary/shell runtime route 已排除（目前
caller/user/build 條件）；受信任 child/profile lifecycle 的完整授權結果
仍不等同於普通 caller。**

### 2. Play Store holder 與 exported launcher receiver

live dump 證實 `com.android.vending` UID 10180、`/data/app`、沒有 captured
privileged private flag，並有 `CHANGE_COMPONENT_ENABLED_STATE` 等 grant rows：
`adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/vending_package.stdout.txt`。
其 grant provenance 仍 UNKNOWN，因為保存的 privapp XML 沒有直接 Vending
block，不能由此推斷 grant 不存在或一定可用。

主機端 recovered code 的 bounded scan 找到 generic package/component writers，
但沒有 Fire Launcher literal、HOME preferred writer 或 direct
`startHomeActivity`。新增的 exported
`com.google.android.finsky.setup.LauncherConfigurationReceiver` 只在收到
`verificationToken` PendingIntent 後驗證 creator 是否為目前 HOME package，
再更新 Play Store 自己的 homescreen restore tracker；未找到直接 PMS
Fire/HOME setter。

精確分析：

- manifest：`artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt:1470-1479`
- recovered receiver：`artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java:43-369`
- HOME package check：同檔 `:68-111`
- tracker update：同檔 `:247-263,312-340`
- Play Store `WEB_SEARCH + DEFAULT` preferred writer：
  `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/defpackage/uez.java:22-63`

判定：**已證實 exported metadata/restore surface；高可信推論它不是 Fire
Launcher controller；bounded code 中的 Fire/HOME writer 已排除；JADX skipped
body、native/resource 行為仍待驗證。** 沒有送出 broadcast、PendingIntent 或
Play Store package setter。

### 3. KOR retail/demo

KOR `ServerMessageReceiver` 需要
`com.amazon.dcp.messaging.permission.INITIATE_HANDLE_DEVICE_MESSAGE`；保存的
shell denial 證據在 `findings/phase-6dl-kor-retail-demo-boundary.md:147-156`。
可信 DCP/cloud envelope 可靜態走到 package deletion，但這是 trusted retail
demo path，不是 ordinary caller。`DemoStateService` 的 component writer 還有
`DemoManager.isDemo()` 與 kiosk state gate。

判定：**ordinary app/shell route 已封閉；trusted demo route 的 package deletion
與 component state capability 已證實；非 Fire HOME sink。**

### 4. H2 household/profile service

`H2ClientService` 雖然 exported，但 binding 需要 signature-level
`com.amazon.alta.h2clientservice.permission.BIND_SERVICE`。其 transaction
鏈是 household/profile user lifecycle，bounded scan 沒有 HOME、preferred 或
Fire package-state writer；`Binder.getCallingUid()` 只被記錄，沒有發現
identity clearing。

證據：`artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.amazon.h2clientservice.xmltree.txt:102-134`、
`artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java:105-127`。

判定：**普通 app/shell bind route 已封閉；authorized H2 client 可做 profile
lifecycle；沒有 HOME/package sink 證據。** 不測試 bind、transaction replay 或
child-user lifecycle。

### 5. ManagedProvisioning、DPM、parent/profile

ManagedProvisioning UID 10091 有 provisioning-related privileged grants，並在
privapp allowlist 中；保存的 resolver output 顯示 device-owner/profile-owner、
managed-user、boot/OTA lifecycle components，但本 corpus 沒有足夠 JADX/VDEX
source 對每個 component 建立精確 caller→sink chain。因此 component gate、
identity clearing、package/HOME sink 均為 **UNKNOWN**，不能把 holder 當成
bypass。

DPM 的 persistent-preferred writer 需要 active admin/profile owner 與 system
server PMS path；DPM tx1/tx2 也有 active-admin/owner gate。parentalcontrols
exported UI/provider 沒有證據能把任意 caller 轉成 package mutator。建立
Device Owner／provisioning 可能需要 reset，列為不執行。

### 6. Driver、OTA、`/init`、kernel

CMDQ/ION/GED、native updater/recovery、BootAfterSystemOTA/OOBE、`/init`
policy loader 與 GhostLock 都只保留 source/lifecycle capability 或未閉合
候選，沒有 ordinary/shell→privileged sink 的證據。任何 write/ioctl、未知
Binder、OTA/recovery、boot property、race/DoS、partition 或 exploit 測試
均列為 **因風險拒絕測試**。

## 決策結論

```text
permission holder
  != caller reachability
caller reachability
  != protected-target acceptance
system-server clearCallingIdentity
  != caller becomes system/root
static capability
  != reproducible privilege escalation
```

因此「只要一拿到權限就一定能關閉」在技術上只適用於已取得受信任 system
UID/root 或通過完整 policy/admin gate 的 actor；目前研究沒有證明如何從
shell/ordinary app 取得該 actor 身分。對 Fire Launcher，已知最短路徑仍是
受保護 PMS package/component state mutation；對更廣泛的權限面，本輪沒有
找到新的低風險入口。

## 不應重複的測試

- KFT tx3 User 10/User 0 component-disable probes。
- KOR shell broadcast/provider/HOME probes。
- H2 bind/service-call、child-user create/switch/reset。
- DPM owner/provisioning 或 tx100 fake-admin probes。
- Play Store exported receiver broadcast、PendingIntent crafting、permission
  grant/revoke 或 generic setter invocation。
- OTA/recovery/updater、driver write/ioctl、`/init` policy mutation、GhostLock
  race/DoS/root。

## 下一個合理研究邊界

若要繼續，最高價值且仍安全的是補齊缺失的 host-only corpus：

1. 取得與保存 ManagedProvisioning 對應的 JADX/VDEX/smali，僅做 component
   gate 與 sink mapping。
2. 對 Play Store skipped receiver 用 smali/DEX decoder 完成控制流，不執行
   receiver。
3. 對 permission grant provenance 做離線 package-settings／privapp／install
   history 交叉索引；不 grant/revoke。

若這三項仍沒有 caller→sink closure，研究結論可正式收斂為：正式 HOME 或
Fire package replacement 需要受信任 system/policy authority；目前沒有安全、
無 Root、普通 app/shell 可重現的權限提升路徑。
