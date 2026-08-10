# Phase 6QB — PS7331 residual caller、writer 與 runtime boundary

日期：2026-08-10
公開基準：`c8ece719f7577b7815c8379265c54efd04dbefb2`（Phase 6QA）
裝置：`G001LT0511550CFT` / `KFTRWI` / `trona` / `PS7331.4463N`

## Executive result

本輪由三個 `luna_worker` 進行 host-only 搜尋，再由主 Agent 交叉驗收；另在
實機上執行一份只讀式 31-command canonical baseline。新增 residual matrix
共 18 rows：

- `IAmazonPackageManager` tx6/tx7 caller inventory：2 rows；
- Play/Vending downstream：9 rows；
- PS7331 Framework/OTA residual writer inventory：7 rows。

**沒有發現新的低權限 caller → accepted gate → system/root identity → User 0
PackageManager、HOME、Fire Launcher 或 partition sink。** 目前結果仍不是
「所有未保存程式碼都不存在問題」的宣稱；每個未取得的 caller、decompiler
branch 或 native handoff 都保留為 `UNKNOWN`。

實機 baseline 顯示：

- build fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`；
- SELinux：`Enforcing`；shell：UID 2000、`u:r:shell:s0`；
- User 0 HOME：`com.amazon.firelauncher/.Launcher`，priority 50；
- HOME candidates：Fire priority 50、Microsoft priority 0、FallbackHome -1000；
- Fire APK：`/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk`；
- private Amazon services 在 `service list` 可列出，但 logcat 保存了 shell
  `service_manager find` denial；
- User 0 與 Fire package/component 沒有被本輪變更。

## Safety boundary

本輪沒有：

- private Binder transaction、service call、broadcast 或偽造 PendingIntent；
- Settings/DeviceConfig/AppOps/Overlay/package/user/profile mutation；
- APK 安裝、Fire Launcher disable/hide/suspend/uninstall/clear/force-stop；
- OTA/recovery/updater、reboot、ioctl、Root、exploit、SELinux 或 partition 操作。

所有 worker 都只讀取既有 host artifacts。實機只使用既有
`capture_phase6q_readonly.py`，該腳本強制指定 serial、拒絕覆寫輸出，且命令
清單只包含 query/dumpsys/logcat read。

## 1. tx6/tx7 caller closure

`IAmazonPackageManager` 的 generated interface/Proxy/Stub、system-server
BinderService 與 ProxyReceiver 實作都已定位，但 exact-build corpus 沒有
production caller，也沒有 system-created PendingIntent provenance。唯一非
generated caller 是 Phase6IP test probe，不能計為量產 caller。

### tx6 — `registerProxyReceiver`

Recovered path：

```text
caller [production NOT_FOUND]
  -> generated Proxy/Stub tx6
  -> BinderService
  -> ProxyReceiver.registerProxyReceiver
  -> creatorPackage -> ApplicationInfo.FLAG_SYSTEM
  -> queryBroadcastReceivers != empty
  -> mOnTheFlyRegisteredIntents
  -> Context.registerReceiver
  -> PendingIntent.send()
```

在目前 method slice 沒有 `clearCallingIdentity()`、preferred activity writer、
enabled-state writer、HOME component 或 Fire Launcher sink。普通 app 的
Phase6IP self-created PendingIntent 已有 negative result（`tx6=false`，
`receiver_hits=0`），但不能反推 system token 的來源。

### tx7 — `deregisterProxyReceiver`

tx7 只在 stored PendingIntent creator UID 等於目前
`Binder.getCallingUid()` 時移除 entry；空 map 才 unregister receiver。沒有
package/HOME/root sink，也沒有 cross-UID cleanup 證據。

判定：**已證實 implementation/gate；production caller 與 system-token
provenance 待驗證；沒有足夠依據進行裝置 Binder 測試。**

## 2. Vending downstream closure

### LauncherConfigurationReceiver

`verificationToken`、current-launcher creator check、setup state 與 package/
launcher qualification 之後，receiver 消費 hotseat/widget/workspace/folder
metadata，進入 `aoba.k`、`aofc.y` restore/install bookkeeping。

沒有 recovered：

- `com.amazon.firelauncher` literal；
- `replacePreferredActivity`；
- `setComponentEnabledSetting`；
- direct `MAIN + HOME` start；
- system/root identity relay。

它是 **launcher metadata restore surface**，不是 Fire Launcher selection
writer。sender provenance 與 downstream account/user binding 仍是 UNKNOWN。

### DseService

已確認的 gates：exported service permission、DeviceSetup feature、
`Binder.getCallingUid()` → package authorization helper。已確認 sinks：

| Sink | Classification |
|---|---|
| `setDefaultBrowserPackageNameAsUser` | browser default，非 HOME |
| search-selector Activity | Setup Wizard UI，非 Fire/HOME writer |
| secure-settings eligibility | Settings sink；key/user/profile dependency UNKNOWN |
| DSE/browser install bookkeeping | install path；無 Fire/HOME/root evidence |

`g()` 的 JADX duplicated-block warning、injected writer、完整 account/user/
profile binding 未被補出，故保留 UNKNOWN；不能把 normal DSE permission 或
browser sink 誇張成提權。

## 3. PS7331 residual writer inventory

七個 residual 均是 bounded static/lifecycle item：

| ID | Current disposition |
|---|---|
| RWI-01 | system-server phase-550 + `isUpgrade()` sender；numeric user unknown |
| RWI-02 | post-OTA OOBE component writer；不是 Fire/third-party HOME setter |
| RWI-03 | post-OTA OOBE secure-settings writer；exact user unknown |
| RWI-04 | Alexa SystemOTA settings/access-control consumers；無 bounded Fire/HOME sink |
| RWI-05 | fosinit/runtime loader completeness；reviewed callbacks無 HOME/package writer |
| RWI-06 | verifier → recovery/native updater privileged capability；caller provenance unknown |
| RWI-07 | updater canonicalization markers；direct canonicalization→write edge unknown |

RWI-01～04 需要自然、合法的 OTA lifecycle 才能取得 runtime timeline；不應以
protected broadcast replay 或手動 enable 取代。RWI-06～07 涉及 recovery/partition
capability，不能因為存在高權限 sink 就推導 shell 可達。

## 4. Runtime baseline

Canonical raw output：
`adb/phase6qb/PHASE6QB-READONLY-20260810-01/`。

重要檔案與 SHA-256：

| File | SHA-256 |
|---|---|
| `metadata.json` | `9c8db228ac716492ee230e5e93e59eb5cb8ef082b15a0077b66acba1523c2f79` |
| `home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` |
| `home_candidates_cmd.stdout.txt` | `e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6` |
| `firelauncher_package_dump.stdout.txt` | `73cf239df6f218c345fad253d707e852ba50cdbacdefe5a93a91a99456734db5` |
| `service_list.stdout.txt` | `137d57c64fc2e05345fc219f661ca39b4f10f756d83e755d8a5d50f12ca6c4b0` |
| `logcat_all_dump.stdout.txt` | `dcef2a733776de2832c99dfe2239f25a619ab222a0bfbc44f60b17b354ddf451` |
| `sha256sums.txt` | `04f4b4b3cdca711e9a345dffab9e32303243931746ebb0a89cabf5fc0cbd0c5f` |

這份 baseline 是觀察證據，不是新的 workaround。它確認目前仍沒有合理的
低風險 runtime route 可以進入 tx6/tx7、DSE、KFT 或 OTA writer。

## 5. Decision and next safe value

本輪沒有達成正式 User-0 HOME replacement，也沒有取得 root；但完成了三個
較容易被誤判為「可利用」的面向之 caller/gate/sink 分層。下一個合理步驟
仍只能是 host-only：

1. 若取得新的 exact-build artifact，補 tx6/7 system-token caller provenance；
2. 補 DSE `g()` 與 injected writer 的 smali/data-flow；
3. 補 OTA verifier→recovery 的 certificate/AVB/registry provenance；
4. 只在自然官方 OTA 後做 read-only state comparison。

在沒有新 caller 或新 artifact 前，不應重做已排除的 `set-home-activity`、
priority、Fire component disable、private Binder replay、protected broadcast、
OTA/recovery 或 kernel probe。

## Evidence IDs

詳見 `findings/phase-6qb-evidence-index.md` 與 normalized matrix。
