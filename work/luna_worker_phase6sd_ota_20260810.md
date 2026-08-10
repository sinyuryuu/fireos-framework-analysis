# Phase 6SD OTA/install-chain host-only static audit

日期：2026-08-10。範圍限於官方 Fire OS 7.3.3.1 OTA/bin、outer source tar、既有 Phase 6SA/6J/6K/6KT/6KU/6M 產出及保存的 JADX/VDEX/native 反編譯。未執行 OTA、Recovery、sideload、recovery/update-binary、reboot、partition write、symlink payload construction、exploit 或真機命令；只新增本報告與同名 CSV。

## 結論

保存證據支持的是「privileged capability 已確認、低權限 caller-to-sink 未建立」：

- `DeviceSoftwareOTA` 的 controller/service 與 install-like API 受 `com.amazon.dcp.ota.permission.CONTROLLER`（`signature|privileged`）及 package/metadata/recovery/hash/device-state gates 保護。
- Java path 可閉合至 `UpdateSystem.install` handoff；recovery verifier 的實作、native recovery caller identity 與 staging helper 的 canonicalization/flags 仍為 UNKNOWN。
- 官方 `update-binary` 靜態具 extraction、block-image、`open/chown/rename/write` 與固定 named-partition capability；這是 recovery/high-privilege sink，不是 shell 或 ordinary app reachability 證據。
- `BOOT_AFTER_SYSTEM_OTA` 是 system-server `onBootPhase(550)`/`isUpgrade()` lifecycle，受 protected broadcast 與 OOBE/demo/shared-preference predicates；它可 enable `OobeHomeActivity`、寫 OOBE setup state，但沒有證據是普通 HOME selector 或第三方 launcher route。
- Tahoe `MY_PACKAGE_REPLACED` receiver 是 PMS targeted system dispatch；Alexa system-OTA receivers 的 action/setting synchronization 亦未建立 arbitrary caller route。
- outer source tar 已讀到 real EOF：35 members、0 symlink、0 hardlink，沒有 updater/recovery/post-install/partition member；它不是 installable OTA。

精確 ledger（caller／permission／input validation／path-symlink-metadata gate／sink／untrusted reachability／UNKNOWN）見 [CSV](./luna_worker_phase6sd_ota_20260810.csv)。以下只列最小可重現證據。

## Artifact identity

| Artifact | SHA-256 | 靜態判讀 |
|---|---|---|
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | 官方 OTA container；未執行 |
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | AArch64 native updater；未執行 |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | Edify input；fixed targets |
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | official outer source tar；real EOF |

## Chain findings

### OTA controller / updater handoff

保存的 source/JADX chain 是：

```text
OSUpdateValidator / SideloadVerifier
  -> metadata/sanity + hash + RecoverySystem.verifyPackage
  -> OSUpdatePropertiesValidator
  -> SideloadMover / FileHelper
  -> UpdateSystemWrapper.install
  -> UpdateSystem.install
  -> recovery/update-binary
```

`SideloadMover` 使用 input basename 作 staging destination；Java corpus 未見 `canonicalPath` 或 `NOFOLLOW` marker。這只代表 Java-side gate 的觀察界線，不能寫成 traversal/symlink bypass；`FileHelper`、framework/native 與 recovery staging semantics 保留 UNKNOWN。`verifySideloadWithoutRecoveryCheck` 是 install branch 的既有命名，不足以推論 verifier bypass，因為前置 flow 與正常 privileged caller chain 尚未被低權限 caller 取得。

### Recovery / native updater

既有 Phase 6KT/6MD/6MK/6MM 靜態結果確認：

- updater registry 24/24 handler cells；`PackageExtractFileFn -> ota_open -> open` 與 extraction/fsync/close。
- `PerformBlockImageUpdate -> open/chown/rename`；`WriteToPartition -> ota_open -> ota_write -> write`。
- script 固定寫入 system/vendor/boot、preloader/LK/TEE/SPM/SSPM/camera firmware 及 `/cache/recovery/last_blocklist`。
- binary 有 `symlink_realpath`、`readlinkat`、`readlink` markers，但 selected direct graph 沒有 canonicalization-to-extraction/write direct edge；indirect dispatch、unselected CFG、return/error dataflow UNKNOWN。

因此只能說「recovery/update-binary high-privilege capability confirmed」。沒有 shell/app → recovery/update-binary → writer 的證據，也沒有執行或 crafted input 測試。

### OOBE / update receivers

`AmazonPackageManagerService.onBootPhase(550)` 在 `PMS.isUpgrade()` 條件下，以 protected `BOOT_AFTER_SYSTEM_OTA` lifecycle 送往 `BootAfterSystemOTAReceiver`。receiver 另檢查 action、OOBE running、retail demo 與 preference predicates，然後可能 enable `OobeHomeActivity` 並寫 `user_setup_complete`/`isOOBEActive` 等 state。保存 source 已接上 Context-derived user boundary，但 exact post-OTA numeric user 仍 UNKNOWN；未見 Fire Launcher preferred-HOME writer。

同 action 的 Alexa receivers 只見設定同步邏輯；Tahoe receiver 則由 PMS 對 `MY_PACKAGE_REPLACED` 的 replaced package targeting 觸發，並有 child-account gate。兩者的 exported/no component permission metadata 不等於 arbitrary shell/app accepted caller；本輪沒有 broadcast replay。

## Existing test/result整理

只引用已保存的 host-only/read-only結果：

| Scope | Existing result |
|---|---|
| Phase 6J/6KT OTA APK and verifier | controller permission、metadata/sanity、recovery verification、device/product/hash gates；native verifier implementation not recovered |
| Phase 6MD/6MK/6MM/6NE | updater path/registry/block-image/cache direct evidence；canonicalization indirect flow unresolved |
| Phase 6MI | outer tar real EOF，35 members，0 symlink/0 hardlink，無 OTA/recovery/post-install/partition outer member |
| Phase 6MO/6MN/6MG | OOBE Context/user-scope and helper sink shape；numeric delivery user unresolved；no broadcast replay |
| Phase 6CG | Tahoe targeted `MY_PACKAGE_REPLACED` dispatch；no arbitrary caller or persistent HOME writer |
| Saved safety flags | `device_contacted=false` for relevant host-only audits; `updater_executed=false`; `recovery_executed=false`; `partition_written=false` |

## Final disposition

沒有證據把 untrusted app 或 shell 連到 recovery/updater partition writer、OTA install handoff、OOBE setup/HOME side effect 或 update receiver sink。所有「path marker」「exported receiver」「native write capability」「缺少 Java canonicalPath marker」均只作靜態觀察；不能升格成 exploit。未閉合項目（recovery native caller/verifier、staging canonicalization、indirect updater CFG、OOBE numeric user、receiver accepted caller）明確保留 UNKNOWN。

不得以 malformed OTA、symlink/traversal、sideload、recovery/update-binary execution、reboot、partition write、private Binder 或真機命令補足上述缺口。

