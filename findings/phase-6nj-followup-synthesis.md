# Phase 6NJ：主機端 follow-up 證據整合

日期：2026-08-10

## 範圍

本輪把三份 `luna_worker` 只讀盤點、HOME callback completeness、OOBE
system-context closure 與既有 Phase 6 證據整合。沒有執行裝置命令、Binder
transaction、service call、ioctl、root、OTA/updater、recovery、reboot、
package/settings mutation 或 partition write。

## 目前最強結論

### 1. User 0 formal HOME

**已證實／高可信負面（保存 corpus 範圍）：** 尚未找到可由 shell 或普通
APK 觸發、並把第三方 Launcher 寫入 User 0 formal HOME 的 Amazon writer。
Fire Launcher 仍由既有 resolver/priority 路徑選中。這不是「任何未保存元件
都不存在」的全域證明。

### 2. KFT IPC

**已證實：** 保存的唯一 `IAmazonUserManager.enableKftLauncher` caller 是：

```text
AmazonUserManagerImpl.createChildUser(String)
  -> createUser(name, 0x8000)
  -> UserInfo
  -> Binder tx 3 enableKftLauncher(UserInfo)
  -> AmazonUserManagerService.BinderService
  -> writers scoped by UserInfo.id
```

service writer 對 supplied `UserInfo.id` 寫入 Tahoe、Fire Launcher 與
Launcher3 component/application state；沒有 formal preferred-HOME setter，
也沒有硬編碼 User 0。tx3 method-local UID/permission check 在 bounded body
中仍是 **Unknown**；既有 SELinux/service-manager evidence 則支持 shell/private
service boundary，不能把「方法內未見 check」寫成可利用漏洞。

完整 worker 報告：

[`luna_worker_kft_ipc_provenance_20260810.md`](../work/luna_worker_kft_ipc_provenance_20260810.md)

### 3. HOME callback

**已證實：** 已保存的 12 個 `fosinit` XML 中，只有兩個 supervisor resolver
callback registration：

- AppCompat：呼叫 `IPackageManager.resolveIntent()`，只做 uninstalled-app
  filter；不指定 Fire。
- Eve：沒有 concrete `resolveIntent` override，沿用 base null path。

callback chain 全部回 null 後，`ActivityStackSupervisor.resolveIntent()` 回到
`PackageManagerInternal.resolveIntent()`。因此目前沒有證據顯示 callback 直接
回傳或硬編碼 Fire Launcher。

報告與產物：

- [`phase-6nh-home-callback-completeness.md`](phase-6nh-home-callback-completeness.md)
- [`phase6nh-home-callback-completeness-20260810-02`](../artifacts/phase6nh-home-callback-completeness-20260810-02/)

### 4. OOBE/OTA user scope

**已證實：** `BootAfterSystemOTA` sender 使用由 `SystemServer` 建立的
system-server Context；ContextImpl 的 null UserHandle 由
`Process.myUserHandle()` 回填，再傳入受 permission 保護的 broadcast。

**已排除（bounded）：** reviewed OOBE source 沒有 formal HOME/preferred
setter 或 `com.amazon.firelauncher` direct writer。此路徑是 lifecycle/setup/
component/settings path，不是已證實的 Launcher replacement。

報告與產物：

- [`phase-6ni-oobe-system-context-scope.md`](phase-6ni-oobe-system-context-scope.md)
- [`phase6ni-system-context-oobe-scope-20260810-01`](../artifacts/phase6ni-system-context-oobe-scope-20260810-01/)

### 5. PS7331 GPL source / driver scope

**已證實：** 官方 source scope 沒有 Android `system/core/init` 或
`selinux.cpp` userspace policy loader；Amazon/MediaTek driver source 透過
Kconfig/Makefile 接線存在，但 source surface 不等於 shipped module、SELinux
可達性或 ordinary-app caller。

`amzn_drv_test` 在 selected `trona_defconfig` 沒有啟用，官方 Image marker
audit 也缺少 test-specific markers；AUXADC、boot/mem/PMIC factory/debug
surface 仍只標為 source/image correspondence，沒有執行 ioctl 或 driver probe。

完整 worker 報告：

[`luna_worker_source_scope_driver_audit_20260810.md`](../work/luna_worker_source_scope_driver_audit_20260810.md)

### 6. OTA capability boundary

既有 Phase 6NE/6NF 已確認 updater 的 cache/block-image capability 與
`CacheSizeCheck -> MakeFreeSpaceOnCache` 分支；這是 privileged/static
capability，不是 shell/ordinary-app caller 或可安全重現的 HOME/root 路徑。
本輪沒有執行 updater、crafted OTA、symlink、recovery 或 partition write。

## Gap matrix 的驗收

worker gap matrix 把研究目標分為 G1–G6。主 Agent 驗收後：

- G1（穩定無 Root User-0 HOME）仍是核心未閉合目標；目前沒有成功 workaround。
- G2（完整 Amazon IPC universe）仍只能做 bounded static closure，不能重播
  未知 transaction。
- G3（OOBE user scope）已由 Phase 6MO + 6NI 大幅縮小，但 exact numeric
  runtime delivery user 與 artifact completeness 仍待驗證。
- G4（Amazon methods → User-0 HOME sink）目前沒有新 concrete sink。
- G5（OTA handoff/indirect caller）仍是 provenance gap，不應透過執行 OTA 補證。
- G6（flags/metadata indirect consumer）為低優先的 bounded static gap。

gap matrix：

[`luna_worker_evidence_gap_matrix_20260810.md`](../work/luna_worker_evidence_gap_matrix_20260810.md)

## 安全結論

本輪沒有找到足以正當化實機提權、未知 Binder replay、driver ioctl、OTA
執行或 Fire Launcher state mutation 的證據。尤其不能從下列任一項直接推導
root：

- tx3 body 未見 method-local permission check；
- driver source 存在 ioctl/proc/debug code；
- updater 具有 partition write capability；
- OOBE sender 使用 system-server context；
- callback chain 存在 vendor extension。

這些均須同時具備 caller、permission/identity、user scope、sink 與可重現 runtime
證據；目前缺少至少一項。

## 下一個最小安全目標

只做主機端 artifact completeness：追查 runtime `fosinit` loader 的實際來源、
class-loader inventory 與保存 XML 集合是否一致。若仍沒有新的 concrete
User-0 HOME/package-state/preferred sink，應把目前結果封存為：

> 正式 User-0 HOME replacement 尚未找到；KFT 僅證實 child/profile-scoped
> launcher state writer；OOBE/OTA 與 drivers 僅為受保護或未閉合的 lifecycle/
> capability surface。
