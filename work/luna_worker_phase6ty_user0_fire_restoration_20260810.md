# Phase 6TY：host-only exact-build User-0 Fire Launcher restoration-writer provenance

日期：2026-08-10（Asia/Taipei）。本輪只讀既有 `fosservices`、`services`、`boot-fosframework` disassembly、AmazonUserManager/KFT/ProductPolicy/OOBE/PackageManager call tables，以及 Phase 6TO/6TR evidence。沒有 adb、Binder/service call、broadcast、reboot、setter replay 或任何裝置 mutation。逐列結果見 [CSV](./luna_worker_phase6ty_user0_fire_restoration_20260810.csv)。

## 結論

bounded exact-build search 找到三類 writer，但沒有閉合 `caller → gate → identity/user → User-0 Fire restoration sink`：

1. **child/profile-scoped writer：** `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)` 以 `UserInfo.id` 寫入 Tahoe FreeTime launcher、`com.amazon.firelauncher` 與 `com.android.launcher3`。這是明確的 child/KFT user-scoped package/component writer，不是 User-0 HOME restoration writer；其合法 production tx3 caller/provenance仍未閉合。
2. **fixed OOBE writer：** `AppAdapterHandler.goToRegistration()` 固定 enable `com.amazon.tv.oobe/.RegistrationActivity`；另有受 protected OTA/system-server 與 OOBE predicates 控制的 OOBE activation family。這些不是 Fire Launcher writer，也沒有 normal HOME restoration identity。
3. **fixed ProductPolicy writer：** `EnableDisableComponentAction.enableDisableComponent()` 依 policy target 與 supplied user 做 generic component/application state change。它沒有 Fire literal、preferred HOME selector 或 restoration-specific identity，因此不把 generic setter 當 Fire writer。

## User-0 Fire writer 判定

未找到 exact-build production path 可同時證明：

`named caller → permission/helper/lifecycle gate → accepted caller identity or cleared identity → explicit User-0 scope → Fire-targeted setter or preferred-HOME sink`。

PMS 的 `setHomeActivity(ComponentName,int)` / `replacePreferredActivity(...)` 是 framework generic sink/API boundary；bounded evidence 沒有把它們連到 `com.amazon.firelauncher` restoration caller。保存的 HOME resolver 只顯示 Fire priority 50 的選擇結果，不能反推有 restoration writer。故 User-0 Fire restoration provenance 分類為 **UNKNOWN**（bounded negative for provenance only, not global absence proof）。

## 關鍵定位與雜湊

| family | class/method | location | result |
|---|---|---|---|
| child/KFT | `AmazonUserManagerService$BinderService.enableKftLauncherComponent(UserInfo)` | fosservices codeOff `0x0431e2`; setter offsets `0x04320a`, `0x043228`, `0x043242` | Fire/Tahoe/Launcher3 setters，scope=`UserInfo.id`；**STRONG_STATIC** |
| fixed OOBE | `AppAdapterHandler.goToRegistration()` | fosservices codeOff `0x02aaf6`; setter `0x02ab0c` | fixed OOBE registration component；**NOT_A_SINK** |
| fixed ProductPolicy | `EnableDisableComponentAction.enableDisableComponent(String,boolean)` | fosservices codeOff `0x052642`; setters `0x052688`, `0x052698`, `0x0526e8`, `0x0526f4` | generic policy target/user；**NOT_A_SINK** |
| generic HOME boundary | `PackageManagerService.setHomeActivity(ComponentName,int)` | services codeOff `0x2d5378`; `replacePreferredActivity` invoke `0x2d540c` | generic preferred-HOME sink, no Fire caller join；**UNKNOWN** |

Input SHA-256: `fosservices`=`ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; `services`=`373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`; `boot-fosframework`=`fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`; Phase 6MH writer table=`39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a`; Phase 6KV PMS/HOME table=`dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`。

## Safety boundary

本輪沒有重跑任何 disable/enable、preferred HOME、service/Binder、broadcast、OTA/OOBE delivery 或 reboot。後續若要縮小 UNKNOWN，只能補同一 exact-build 的 production caller、permission owner/grant、Binder UID/identity、`UserHandle`/cross-user gate 與 Fire-target data-flow；不得以 generic setter、resolver observation 或 historical restore/reboot 當作 User-0 Fire writer provenance。
