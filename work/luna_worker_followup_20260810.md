# luna_worker follow-up：Phase 6BK+ 主機端檔案盤點

日期：2026-08-10
公開 HEAD 參考：`2f096656158a30ddb834c3bab69c8b6b4b984514`
範圍：只讀取工作區既有 `findings/`、`adb/`、`artifacts/`、`decompiled/` 與公開索引；本輪沒有 ADB、Binder transaction、root、ioctl、OTA/fastboot/reboot、broadcast、package/component/settings/HOME 狀態修改，也沒有重做 `com.android.vending` 掃描。

## 執行邊界與工作樹狀態

工作樹在本輪開始前已有多個 tracked 修改與大量 untracked Phase 6BK+ 證據。本檔是本輪唯一新增檔案；其他既有修改未觸碰。報告中的「目前內容」指工作區檔案，不表示它們都已進入公開 HEAD。

## 盤點結論

| 路線 | 目前判定 | 主要證據與去重結論 |
|---|---|---|
| Amazon IPC / private Binder | 已證實存在；低權限不可達尚未改變 | `findings/phase-6l-binder-contract-audit.md` 已對齊 `IAmazonActivityManager`、`IAmazonWindowManager`、`IAmazonPackageManager` 的 interface→Proxy/Stub→system-server implementation；6BK 靜態閉包又整理 `preWarmApplicationForUser`、KFT、profile/OTA 方法。`adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/` 顯示 `amazonpackagemanager`、`amazonusermanagerservice` 等 `service check` 為 not found，而 `fosdebug` found。這是既有可達性邊界的唯讀重確認，不是新 transaction 路線。 |
| package-state / Fire protection | 已證實，重複於既有公開 finding | `findings/phase-6ma-denylist-fosinit-and-kft-closure.md`：PS7331 deny-list 含 `com.amazon.firelauncher`；PackageManager protected gate 在 state mutation 前拒絕。`findings/evidence-index.md` F-057/F-058/F-060 已記錄 package/component/suspend/hide 邊界。6BK state capture 只重現現況，不應再設計 disable/hide/suspend 測試。 |
| KFT / child-user | 靜態 writer 已證實；User-0 路線未證實且已被邊界排除 | `findings/phase-6kq-kft-tahoe-component-protection-boundary.md`、`phase-6ma...` 與 6BK IPC closure 都指向 `AmazonUserManagerService` 的 child/profile-scoped writer：對指定 child user enable Tahoe、disable Fire/Launcher3。`adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/` 僅是唯讀 preflight；User 0 Fire HOME、既有 User 10、shell UID 2000 狀態均未提供 tx3 可達性。`PHASE6BK-KFT-RUNTIME-20260810-01/` 的 user switching/rollback 是既有 runtime 證據，非新研究入口。 |
| BootAfterSystemOTAReceiver | 高影響 lifecycle 已證實；安全上不可人工觸發 | `findings/phase-6q-bootafter-system-ota.md`、`phase-6r-bootafter-system-ota-authorization.md` 已證實 phase 550 + `isUpgrade()` sender、protected-broadcast source、receiver 啟用 OOBE HOME 的副作用。`artifacts/phase6bk/protected-broadcast-expanded-20260810-01/result.md` 在 34 個輸入中未命中；`protected-broadcast-union-20260810-02/result.md` 在 45 個輸入中命中 1 個。這修正掃描範圍，不證明完整 runtime set，也不授權手動 broadcast。 |
| fosinit / callback registration | 全集已完成；負向 closure | `findings/phase-6jd-fosinit-registration-audit-closure.md` 已覆蓋 PS7331 123 個 `*_fosinit.xml`，並核對 Activity/Package/Permission/User/Profile callbacks。結論：沒有新的 User-0 HOME、preferred-activity 或 package-enabled writer；唯一直接 Fire/Tahoe/Launcher3 writer 是既有 child/KFT 路徑。再掃同一全集屬重複。 |
| HOME 控制候選 | Fire HOME 現況已證實；新 Amazon HOME setter 未找到 | `adb/phase6bk/PHASE6BK-STATE-RO-20260810-01/home_candidates.stdout.txt` 顯示 Fire priority 50、Microsoft priority 0；`home_resolve.stdout.txt` 為 `com.amazon.firelauncher/.Launcher`。`findings/evidence-index.md` F-014/F-016/F-031/F-033/F-044–F-048 已覆蓋 key policy、ActivityStack visibility、Settings UI 與 resolver；Amazon callback 可觀察/過濾，但不是已證實 shell-writable HOME setter。 |
| OTA/updater/recovery | 能力已證實；低權限 launcher/root 路線未建立 | 6BK IPC/OTA closure 與 `findings/phase-6kt-evidence-index.md` 已記錄 updater partition-write capability、OtaDexopt read-only preconditions、無 shell/app→recovery 完整鏈。OTA、recovery、malformed input、partition write 均列為不可動態測試。 |

## 證據雜湊

下列為已存在的原始檔或報告 SHA-256；未重新覆蓋或改寫來源。

| 檔案 | SHA-256 |
|---|---|
| `artifacts/phase6bk/ipc-ota-closure-20260810-01/result.md` | `4052ad1c008f891584e83a9ebc2ac5655f47f616a92f30512885c6557dcfa4c4` |
| `artifacts/phase6bk/ipc-ota-closure-20260810-02/result.md` | `4052ad1c008f891584e83a9ebc2ac5655f47f616a92f30512885c6557dcfa4c4`（內容重複） |
| `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/result.md` | `5b2a96f1fcca8688bbbd39dd34a5633dc73381e9018e339aa69ba07cb34035f3` |
| `artifacts/phase6bk/protected-broadcast-union-20260810-02/result.md` | `84544b8246b9bcc5c9371d0f0e148b99393b2a574e6cdecb8803b1b0cfe06f06` |
| `findings/phase-6jd-fosinit-registration-audit-closure.md` | `7a56394115235d76812c9c4d273c1eecb896eb2682b2bc4ca99a892d4f3e2b238` |
| `findings/phase-6q-bootafter-system-ota.md` | `41c0a9378402d7df555c0ad00a6b5016b41bbc367bee7766fd74924cd2cd1957` |
| `findings/phase-6r-bootafter-system-ota-authorization.md` | `4c2edb6e43b39bfbe615fd8779f49026f3694cad884ebab50103f0cfbd701fbc` |
| `findings/phase-6kq-kft-tahoe-component-protection-boundary.md` | `e77ec612dbe1cbb5f8631aec3e0bd8cbc0218a8f2b4996a4d6cf6ee3e72f90ab` |
| `findings/phase-6ma-denylist-fosinit-and-kft-closure.md` | `8dc5549de5451ccddd9010e98e0aae32e66c6dcc34e3eccec1d51001b2e19b83` |
| `artifacts/phase6jd-fosinit-20260808-01/manifest.sha256` | 已存在；報告記錄 extraction manifest SHA-256 `0797a670880672e424326aa206ab422ca849e2996d2f0985aa2d4b2ca61ea993` |
| `adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/sha256sums.txt` | 已存在；代表性 `service_list.stdout.txt`=`137d57c64fc2e05345fc219f661ca39b4f10f756d83e755d8a5d50f12ca6c4b0`、`dumpsys_fosdebug.stdout.txt`=`c0cd9cd0eac9895469ac67f0b6c85e71c024db65d1fec19db9e7c909daf12b24` |
| `adb/phase6bk/PHASE6BK-STATE-RO-20260810-01/sha256sums.txt` | 已存在；`home_candidates.stdout.txt`=`e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6` |

## 待審核與安全不可動態測試

待審核僅保留以下最小問題：

- `preWarmApplicationForUser` 的完整 privileged caller graph，確認是否只有 Alexa/privileged caller；不可呼叫 transaction。
- `IAmazonUserManager.enableKftLauncher` tx3 的 exported contract、permission 與 trusted child lifecycle caller；不可以 shell 或未知 `service call` 嘗試。
- `BOOT_AFTER_SYSTEM_OTA` 完整 runtime `mProtectedBroadcasts` provenance；只能做 host-only manifest/source inventory，不能人工送 broadcast。
- protected-broadcast union 中唯一命中的來源與 Phase 6Q/6R 的 source-package mapping；這是 provenance 對齊，不是動態送達測試。

下列路線明確標記為不可動態測試：未知 Binder/service-call 或 ioctl；root exploit；OTA/fastboot/recovery/reboot；partition/updater execution；手動 `BOOT_AFTER_SYSTEM_OTA` broadcast；任何 Fire Launcher/KFT/child-user/package/component/preferred-HOME/Settings state mutation；以及任何用 payload 驗證 writer 的操作。

## 下一個最小可驗證研究包（host-only 優先）

**Package：`LUNA-20260810-AMAZON-CALLER-PROVENANCE-RO`**

1. 以既有 PS7331 VDEX/JADX/disassembly 與 123-file fosinit manifest 為輸入，建立一份新的 host-only caller matrix：`preWarmApplicationForUser`、`enableKftLauncher`、`createChildUser`、`BOOT_AFTER_SYSTEM_OTA` sender。欄位固定為 caller class、registration、permission marker、identity clear、sink、user scope、已有 evidence path。
2. 對 `artifacts/phase6bk/ipc-ota-closure-20260810-01/02/`、`findings/phase-6l*`、`phase-6jd*`、`phase-6q/6r` 與 `protected-broadcast-*` 做 input-manifest/sha256 去重；只產生新 output directory，不覆蓋現有 artifacts。
3. 對每條路線輸出三值判定：`static_sink_confirmed`、`low_privilege_caller_found`、`dynamic_test_allowed`。預期分別多為 `true/false/false`；不得把 service name visibility 或 AIDL transaction mapping 當成 reachability。
4. 可選的唯讀 ADB 僅限重新收集 `getprop ro.build.fingerprint`、`cmd user list`、`service list`、`service check`、`resolve-activity --brief HOME`、`dumpsys package/user`；不得新增 user、切換 user、啟動 OOBE、發送 broadcast、寫入 package/HOME state。若現有相同 build capture 足夠，優先不接觸設備。

成功標準：新增 matrix 能指出每個候選的唯一 source/sink、與公開 finding 的重複關係、完整 hash provenance，且沒有任何 exploit payload 或裝置狀態變更。最大不確定性仍是未取得的 private Binder authorization semantics 與自然 OTA/child lifecycle 事件；這些不能用量產機人工模擬補洞。
