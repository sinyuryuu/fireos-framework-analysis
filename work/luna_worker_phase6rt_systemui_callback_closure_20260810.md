# Phase 6RT — SystemUI / callback closure

日期：2026-08-10。這是 host-only static search；只讀保存的 PS7331 JADX、VDEX disassembly、SystemUI resources、Amazon `fosinit` XML、既有 findings/CSV。沒有接觸裝置，沒有 Binder/service call、broadcast、settings/package mutation、OTA/root/exploit，也沒有執行 `boot_unpacked`。

## 結論

在保存 corpus 內，SystemUI resource arrays 是服務註冊/載入清單，不是 Fire HOME 選擇器；`amz_config_systemUIServiceComponents` 列出 Amazon SystemUI service class，`config_systemUIServiceComponentsPerUser` 為空。未找到 `com.amazon.firelauncher/.Launcher` 作為 SystemUI explicit launch target，也未找到 SystemUI callback 直接呼叫 preferred-HOME、`setHomeActivity`、package/component enabled-state writer。

最接近 HOME 的 framework callback 是 AppCompat/Eve 的 pre-resolution hook，以及 LauncherHijackPreventer 的 HOME-task visibility gate。AppCompat 只向 PackageManager 取得 `ResolveInfo`，Eve 在保存 class slice 沒有 resolver override；兩者均不等同 Fire component injection。Amazon Activity/Profile callbacks 主要傳遞 `ComponentName`、作 profile/activity policy decision 或 conditional profile-picker start。OOBE 是真實的 component/setup writer，但其 protected OTA lifecycle sink 指向 OOBE，不是 Fire Launcher。

## registration → caller → gate → identity → sink

| Row | Closure |
|---|---|
| 6RT-001/002 | SystemUI arrays → SystemUIApplication service bootstrap → resource/system context → listed service instances/lifecycle；無 per-user Fire component。 |
| 6RT-004/005/006/007 | Amazon WMS `fosinit` callbacks → PhoneWindowManager/WMS/ViewRoot lifecycle → window-type/permission/framework gates → in-process system_server identity → window flags, visibility, trace, PIP event；不是 package/HOME writer。 |
| 6RT-008/009 | AppCompat/Eve `fosinit` → ActivityStackSupervisor callback dispatcher → first-non-null + PM resolver/fallback → in-process system_server → PM-produced ResolveInfo or null；未見 explicit Fire selector。 |
| 6RT-010 | LauncherHijackPreventer → ActivityStack/AMS callback → Leanback + SELinux `see_home_task` or Android signature → callback context → visibility/permission result；沒有 HOME state write。 |
| 6RT-011/012 | AMS `ComponentName` resume/activity-start callbacks → Amazon ActivityManager/Profile observers → lifecycle/profile state and downstream cross-user gate → in-process service context for local branch → observer notification or conditional profile-picker Activity；沒有 preferred/package writer。 |
| 6RT-013/014 | OTA-protected OOBE receiver or package lifecycle metadata callback → receiver/service handler → protected OTA / system-app target / downstream `INTERACT_ACROSS_USERS` → trusted receiver/service context → OOBE component/setup state or persistent profile metadata；沒有 Fire HOME sink。 |

## AOSP / Fire 對照

- AOSP-shaped path：`ActivityStackSupervisor.resolveIntent()` 先問 vendor callback，callback 回 null 才走 `PackageManagerInternal.resolveIntent()`；這是可插入 resolver 的 callback boundary，但保存的 AppCompat/Eve evidence 沒有 Fire literal 或自行建立 Fire `ComponentName`。
- Fire-specific path：User-0 Fire Launcher 的保存 manifest 是 `MAIN + HOME + DEFAULT`、priority 50；既有 evidence 顯示標準 resolver 仍選 `com.amazon.firelauncher/.Launcher`。這支持「候選/priority/resolver state」解釋，不支持 SystemUI callback explicit launch。
- Fire Profile path：`AmazonProfileService` 的 in-process AMS callback 可觀察 resume、做 profile-picker gate，metadata map 可持久化 configured package/activity；但 ordinary remote tx41 已在 `getCurrentUser()` 的 `INTERACT_ACROSS_USERS` gate 停止，且 path 未見 preferred HOME/package state setter。
- Fire OOBE path：`BOOT_AFTER_SYSTEM_OTA` 是 protected signature|amazon/system-server lifecycle；`PackageHelper`/OOBE helper 可寫 OOBE component/setup settings。這是明確 writer，但不是 Fire Launcher restoration edge。

## 分類與安全下一步

CSV 將每條 route 分成 resource/lifecycle registration、window mutation、resolver callback、visibility gate、activity event、profile metadata 或 OOBE writer。`reachability` 僅表示保存的 static registration/call edge；不把 service publication、permission holder、缺少 method-local check 或 `clearCallingIdentity` 誤當成低權限 caller 可達。

唯一合理的後續仍是主機端：若取得另一份 exact-build resource overlay、完整 callback class slice 或自然官方 OTA 後的既有唯讀 capture，可做 hash/registration/source comparison。不得為補齊未知而 replay callback、tx、broadcast、HOME/profile switch、package/component/settings writer 或 OTA。

## Evidence index

- `decompiled/jadx/ota-PS7331/systemui/resources/res/values/arrays.xml:3-37,344-349`
- `artifacts/amazon-services/amazonwindowmanager_fosinit.xml:12-23`
- `artifacts/amazon-services/appcompatsupport_fosinit.xml:12-20`
- `artifacts/amazon-services/eve_launch_time_fosinit.xml:9-25`
- `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml:9-16`
- `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:12-22`
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:196540-196700,203322-203390,180180-180210`
- `findings/phase-6al-home-resolve-callbacks.md`, `findings/phase-6nh-home-callback-completeness.md`
- `findings/phase-6er-ams-home-callback-boundary.md`, `findings/phase-6er-amazon-profile-metadata-tx41-boundary.md`
- `findings/phase-6ff-oobe-backup-lifecycle-boundary.md`
- `artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv`
- `artifacts/phase6mg-oobe-helper-scope-20260810-01/helper-scope.csv`
