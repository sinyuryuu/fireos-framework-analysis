# Phase 6QF — host-only Amazon IPC residual caller/provenance closure

日期：2026-08-10。只讀取目前工作樹保存的 VDEX/JADX/baksmali、manifest、fosinit 與既有 Phase 6 evidence；沒有執行 Binder transaction、service call、broadcast、settings/package/component mutation、OTA/recovery/updater、root、reboot、ioctl 或 partition write。只新增本報告與 companion CSV。

## 結論

本輪把 Phase 6QE 的 residual 收斂為 12 條靜態 caller/provenance rows。每列均按 registration → Stub/onTransact → actual caller/sender → permission/role gate → identity handling → user propagation → first consumer/sink 追蹤；無法由保存 corpus 證明的欄位保留 `UNKNOWN`。

最重要的結果：

- Amazon PM flags/metadata 的四個 mutator 不只存在 generated Binder contract；已找到 framework facade 的四個實際 invoke sites（`AmazonPackageManagerImpl`），但 permission holder、numeric target user、以及第一個把 metadata 轉成 HOME/package-state 的 consumer 仍未完整閉合。保存 consumer 只有 per-user persistence、recency/game-mode/compatibility 類路徑。
- KFT `IAmazonUserManager` tx3 的實際 caller 是 child-user provisioning（`createChildUser` 與 system-server child loop）。sink 使用 caller-supplied `UserInfo.id` 寫 Tahoe/Fire/Launcher3 component state；這是 child/profile state writer，不是 formal preferred-HOME setter。tx3 method-local caller gate 仍 `UNKNOWN`，不能推成漏洞。
- `setUserSetupComplete` tx4 的既有 ordinary APK 證據只到 User 10 settings deputy，且在寫入前 `clearCallingIdentity`；沒有 PM/HOME sink。DPM tx100→PMS tx73 是 active owner/profile-owner 與 system UID downstream gate 的 trusted persistent-preferred path。
- Amazon Profile tx21/tx41、AMS observer/prewarm、WMS PIP/overscan 只閉合到 profile/activity/process/window/status-bar sinks；ordinary reachability、method-local gate 或 exact user 在個別分支仍有 `UNKNOWN`，沒有 recovered User-0 Fire HOME/package sink。
- Vending `LauncherConfigurationReceiver` 的 exported/無 receiver permission metadata 不等於任意 sender。`verificationToken` creator/current-launcher/setup/package qualification 是第一道 gate；first consumer 是 Play restore bookkeeping。DSE service 另有 DSE permission、DeviceSetup、`Binder.getCallingUid()`→package authorization，consumer 是 browser/search/settings/install bookkeeping，不是 Fire HOME。
- `BOOT_AFTER_SYSTEM_OTA` 僅由 system-server phase-550 + `PMS.isUpgrade()` protected lifecycle 發送；OOBE receiver 會啟用 `OobeHomeActivity`、寫 setup/OOBE Secure state，但 exact numeric user 與自然 delivery timeline 未證明，且沒有 preferred HOME/Fire Launcher writer。OTA controller 只有 privileged capability，未證明 ordinary caller。

因此，本輪沒有得到 `ordinary app/shell → accepted gate → system/root identity → User-0 Fire HOME/package sink` 的閉合鏈。`UNKNOWN` 是證據缺口，不是漏洞判定；exported、service publication、normal permission、manifest capability、generated Proxy/Stub 或 static sink 均不單獨證明可達性。

## Evidence anchors

主要 exact-build inputs：

| input | SHA-256 | relevant use |
|---|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | service publication, mutator gates, OOBE sender, DPM/Profile/AMS/WMS methods |
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | Amazon interfaces, Stub/onTransact, PM facade caller sites, child-user caller |
| `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` | `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df` | DPM/PMS downstream transaction evidence |
| `artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java` | `71d17a064272f88d02f4619a2f4fa6fedf0ae91a233c29e0ad6d4110643b6b47` | receiver gate and restore first consumer |
| `BootAfterSystemOTAReceiver.java` | `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90` | protected OOBE receiver guard/sink |
| `OtaService.java` | `d39c799a8e3f9b31eae3677732f75a679433da856b65261f3c71143a75260d09` | OTA controller Binder boundary |

Registration corpus is preserved in `artifacts/phase6jd-fosinit-20260808-01` and `artifacts/amazon-services`; the machine-readable row-level ledger is [luna_worker_phase6qf_ipc_provenance_20260810.csv](luna_worker_phase6qf_ipc_provenance_20260810.csv).

## Residual boundary and safe continuation

Remaining work is strictly host-only: resolve additional exact-build aliases, reflection/generated/native readers, manifest role holders, missing DEX/smali branches, and Context/user API propagation. Do not obtain private service handles, synthesize parcels, replay tx3/tx6/tx7/tx41/tx100, send OTA actions, bind/call DSE, broadcast Vending actions, mutate settings/package/component state, execute OTA/recovery/updater, or write partitions.

