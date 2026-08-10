# Phase 6AJ user-scope closure (host-only static)

基準：`ba42ba5f6` / Phase6X3 rows `6AE-001`, `6AE-002`, `6AE-006`；對照 Phase6X2 rows `6X2-ROUTES-001`, `6X2-ROUTES-004`。

本 closure 僅讀取保存的 JADX/source、baksmali/VDEX/disassembly、CSV/既有 finding。未執行 broadcast、service call、Binder transaction、process launch、reboot 或任何真機 mutation。未將任何缺失證據推導成 HOME、root 或特定 user。

## 結論

`6AE-001`/`6AE-002` 是同一條受 OTA lifecycle guard 的 OOBE 路徑：`AmazonPackageManagerService.onBootPhase(550)` 在 `isUpgrade` 條件下送出受保護的 `BOOT_AFTER_SYSTEM_OTA`，receiver 以傳入 `Context` 操作 PackageManager/ContentResolver。保存的 Java/source 及 disassembly 沒有 numeric user argument、`createContextAsUser`、`UserHandle` 或 profile 選擇；因此不能標為 User 0、User 10 或 profile。`OOBEActivationHelper` 的 `ContentResolver` 從 receiver context 繼承，`Settings.Secure` 的實際 user 仍為 `UNKNOWN`。

`6AE-006`/`6X2-ROUTES-004` 的 prewarm Binder contract 明確帶入 `(String target, int arg1, int user)`；disassembly 將該 user int 傳到 `IPackageManager.getApplicationInfo(target, 1024, user)`，之後進入 `PreWarmCacheHelper` 與 `ActivityManagerService.startProcessLocked(..., "prewarm", ...)`。保存 slice 未證明 caller 對該 user 的 cross-user validation，也未證明該 int 是 0、10 或 profile parent/child。

## Identity / permission 分界

* OOBE receiver：保存證據顯示 system-server OTA lifecycle producer 到 receiver；不是 ordinary Binder caller。receiver/helper slice 沒有 `clearCallingIdentity` / `restoreCallingIdentity` 呼叫，因此這兩者在此路徑為 `UNKNOWN/NOT APPLICABLE`，不可把 lifecycle context 誤寫成 shell 或 root identity。
* OOBE context handles：`context.getPackageManager()` 對應 component enable sink；`context.getContentResolver()` 對應 `SettingsDBUtils.setSettingSecurePutIntFG`。未恢復出 context 的 numeric user 或 profile handle。`PackageHelper` 的 PMS-side user routing 亦未在保存 corpus 中閉合。
* prewarm caller permission：BinderService 先呼叫 `Context.checkCallingPermission("com.amazon.permission.APP_PREWARM")`；在 bounded disassembly 中該 return value 未見被消費，隨後即 `Binder.clearCallingIdentity()`。這是靜態 authorization-anomaly candidate，不是 caller bypass 的證明。
* prewarm identity：`clearCallingIdentity` 後才做 `AppGlobals.getPackageManager().getApplicationInfo(..., user)`、cache lookup 及 AM `startProcessLocked`；正常返回路徑有 `Binder.restoreCallingIdentity`，保存 slice 對所有 exceptional cleanup 與 caller UID 轉換不足，故仍標 `UNKNOWN`。

## User 0 / User 10 / profile

Phase6X3 的保存 read-only snapshot 只證明當時 User 0 resolver 選到 Fire Launcher，並分別列有 User 0 與 User 10 package state；它沒有把 snapshot 的 user state join 到 OOBE receiver context 或 prewarm 的 explicit user int。故：

* User 0：未由上述五個 route 的 source/bytecode 證明為 route target；`UNKNOWN`。
* User 10：有獨立保存狀態，但沒有 route invocation 或 handle propagation join；`UNKNOWN`。
* profile：保存 slice 沒有 `UserHandle`/profile-parent mapping 或 profile-specific prewarm/OOBE dispatch；`UNKNOWN`。

這些路徑的 confirmed sinks 是 OOBE component/setup settings，或 prewarm process/cache；沒有由本 closure 證明 HOME preferred-activity mutation、Fire Launcher replacement、root 或 privilege escalation。

## Evidence anchors

* `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61`
* `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
* `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`（prewarm permission, clear/restore identity, PMS/AM calls）
* `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394739`（prewarm proxy：package + two ints）
* `findings/phase-6x3-evidence-index.md:1445-1495,1517-1590`
* `findings/phase-6x3-readonly-check.md`（User 0/User 10 read-only snapshot；不與上述 route 做 user join）

Status：`STATIC_CLOSURE_WITH_USER_SCOPE_UNKNOWN`；未知資料保留，未作 runtime 或真機驗證。
