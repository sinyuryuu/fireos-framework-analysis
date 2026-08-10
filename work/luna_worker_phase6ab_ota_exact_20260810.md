# PS7331 OTA exact write-chain audit (host-only)

日期：2026-08-10。範圍只包括工作區保存的官方 PS7331 原始 OTA、解包後的
`META-INF`、`update-binary`、OTA APK/JADX 與既有主機端 disassembly/call-edge
證據。沒有執行 ELF、recovery、updater、sideload、flash、reboot 或設備操作，也
沒有修改設備。本文不把未閉合的部分推定為安全或可利用。

## 結論

PS7331 的已證實寫入能力是 recovery/update-binary context 的高權限 capability：

```text
privileged OTA lifecycle/controller
  -> metadata/sanity/device-state gates
  -> RecoverySystem.verifyPackage (正常驗證分支)
  -> OSUpdatePropertiesValidator
  -> staging / UpdateSystemWrapper.install
  -> UpdateSystem.install
  -> recovery/update-binary
  -> Edify registry
  -> package_extract_file 或 block_image_update
  -> WriteToPartition -> ota_write -> write
```

其中 Java caller、metadata/signature/version/PVT gate、Edify named targets、native
registry、file/partition write capability 都有保存的靜態證據；但 `UpdateSystem.install`
如何進入 recovery、recovery verifier 的完整實作、最終 native/SELinux identity、
canonicalization 結果如何影響 writer，以及 AVB/rollback 的 exact branch，均未在
保存 corpus 中完整閉合，應標為 **UNKNOWN**。

沒有證據將普通 app 或 shell UID 連到這條 partition writer；對普通 app/shell 的
可達性結論為 **NEGATIVE（就已分析 scope）**，不是宣稱所有未保存入口不存在。

## 1. PS7331 package identity 與 package shape

原始包：`firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`

- SHA-256：`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`
- `ota.prop`：`product=trona`、`Fire OS 7.3.3.1 (PS7331.4463N/4463)`、
  `version_number=0031575863172`、`key_type=release-keys`、`sign_type=release`
- `META-INF/com/android/metadata`：`ota-type=BLOCK`、`pre-device=trona`、
  `post-build=Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`、
  `post-security-patch-level=2024-08-01`
- 解包 package members 有 `META-INF/com/android/otacert`、`update-binary`、
  `updater-script`、`system/vendor .new.dat.br`、transfer lists、`boot.img` 與
  多個 boot-chain images。
- 保存的 member inventory 沒有 `payload.bin`，也沒有 A/B `postinstall` executable。
  因此本包的 postinstall 路徑是 **NEGATIVE（package-shape scope）**；不能把
  `otadexopt` 或一般 boot-after-OTA receiver 說成此 OTA 的 partition postinstall。

證據：`firmware/manifests/OTA-20260803-01/README.md`、
`artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`、
`android-metadata.txt`、`ota.prop`；manifest 與原包 hash 亦見該目錄的
`sha256sums.txt`。

## 2. Caller 與 permission/verification gates

### 已閉合的 Java-side caller

1. 正常 OTA validation：`OSUpdateValidator.validateOSUpdate()` 先呼叫
   `mHelper.assertHash()`，再呼叫 `RecoverySystemWrapper.verifyPackage()`，再呼叫
   `OSUpdatePropertiesValidator.assertUpdatePropertiesValid()`。
   證據：`artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/software/ota/tasks/validate/OSUpdateValidator.java:73-78`。
2. Sideload verification：`SideloadVerifier.verifySideloadWithRecoveryCheck()` 順序是
   sanity → metadata → `RecoverySystem.verifyPackage` wrapper → device-state。
   證據：`SideloadVerifier.java:31-58`。
3. Sideload install：`SideloadInstaller.installSideload()` 呼叫
   `verifySideloadWithoutRecoveryCheck()` → `SideloadMover.maybeMoveSideloadFile()`
   → `installOSUpdate()`；後者呼叫 `UpdateSystemWrapper.install()`。
   證據：`SideloadInstaller.java:65-90`。
4. Handoff：`UpdateSystemWrapper.install()` 將 external-storage prefix 替換成
   media-storage prefix、寫入 `persist.sys.ota.isScreenOffBeforeOTA`，再呼叫
   `UpdateSystem.install(context,path,flags,emptyMap)`。
   證據：`UpdateSystemWrapper.java:33-43`。

### Gate

`SideloadMetadataChecker.check()` 的順序是 version、signature transition、product、
PVT user-build；downgrade、product transition、signature transition 在保存 source
中由 OTASettings boolean 控制，預設 false 的 gate 證據已收錄於
`artifacts/phase6ab/ota-input-validation-20260805-03/ota-input-validation.csv`。

`RecoverySystemWrapper` 只是 `RecoverySystem.verifyPackage(file,...)` delegation：
保存 Java source 證明 API call boundary，不包含 platform cryptographic verifier body。
故 package signature gate 是 **CONFIRMED（call boundary）**，完整 certificate
verification implementation 是 **UNKNOWN**。

### Permission / caller identity

保存 manifest/dump 證據顯示 OTA controller surface 使用
`com.amazon.dcp.ota.permission.CONTROLLER`，OOBE OTA package 另有
`PROCESS_UPDATES`；`com.amazon.dcp`、forced OTA 等是 privileged/controller holders。
這只證明受保護的 service/app surface，不能當作普通 APK 可自授予 permission。

`UpdateSystem.install` 的 Java caller 是受控 OTA application/framework path；從
保存 corpus 沒有 shell UID 或 ordinary-app → `UpdateSystem.install` → recovery 的
完整 caller proof。該缺口標 **UNKNOWN**；就已審核 public/controller surface 而言，
普通 app/shell 直達 writer 為 **NEGATIVE**。

## 3. Path canonicalization

- `SideloadMover.java:39-42` 以 `getAbsolutePath()` 拆最後一個 slash-separated
  basename，組合 OTA data destination 後交給 `FileHelper.moveFile`；選取的 Java
  source 沒有 `canonicalPath`、`realpath`、`lstat` 或 `O_NOFOLLOW` marker。
- native `update-binary` 的 `MakeFreeSpaceOnCache + 0x478`（VA `0x417bf0`）直接
  呼叫 `__readlink_chk`（`0x4ce4e8`），同時有 cache/stat/unlink bookkeeping。
- selected direct-call graph 沒有 `MakeFreeSpaceOnCache`/`__readlink_chk` 直接到
  `PackageExtractFileFn`、`PerformBlockImageUpdate`、`BlockImageUpdateFn` 或
  `WriteToPartition` 的 edge；這是 bounded **NEGATIVE**，不是 binary-wide
  traversal/symlink safety proof。
- `CacheSizeCheck` body、全部 callers、readlink return/error branches、function
  pointer dispatch 與其結果到 writer 的 data-flow 未完整選取；因此「canonical path
  是否實際 gate writer」為 **UNKNOWN**。沒有做 symlink/traversal 測試。

證據：`findings/phase-6mm-updater-blockimage-closure.md`、
`artifacts/phase6mm-updater-blockimage-20260810-01/canonicalization-call-sites.csv`、
`artifacts/phase6ab/ota-input-validation-20260805-03/ota-input-validation.csv`。

## 4. Native updater exact write chain

### Edify registry

靜態 disassembly 已閉合：`main (0x400cb0)` → `RegisterBlockImageFunction
(0x40d0a8)` → `RegisterFunction (0x41d528)`；五個 block-image handlers 及 data-cell
均解析到 function symbol，包含 `block_image_update` → `BlockImageUpdateFn
(0x40b8b8)`。另外已保存的 dispatch audit 證明 `package_extract_file` 相關
registration/extraction/open direct edges。

證據：`findings/phase-6mk-updater-dispatch-closure.md`、
`findings/phase-6mm-updater-blockimage-closure.md`、
`artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv`。

### Extract/write sinks

- `PackageExtractFileFn (0x401fb8–0x402788)` → `ota_open (0x426338)` → libc `open`
  → extraction/fsync/close。
- `BlockImageUpdateFn (0x40b8b8)` → `PerformBlockImageUpdate` → `WriteToPartition
  (0x413c40–0x4142f0)` → `ota_open/ota_write` → `write`。
- `PerformBlockImageUpdate` 有 direct caller edge 到 `CacheSizeCheck`；但
  `CacheSizeCheck` body、return/error propagation 尚未完整解析。

這些是 **CONFIRMED capability**，不是已執行結果。沒有執行 binary，也沒有輸入
人工 package、command、transaction 或 partition data。

### Script target mapping

`updater-script` 的精確 targets：system、vendor、boot、preloader、lk、tee1、tee2、
spmfw、sspm_1、cam_vpu1、cam_vpu2、cam_vpu3；另將 target blocklist 寫到
`/cache/recovery/last_blocklist`。script 也有 device/date assertions：`trona` device
與 build-date comparison。這是 package input 對 named sinks 的靜態 mapping；不是
任意 path writer 證據。

## 5. AVB / signature / rollback

| Check | 判定 | 證據界線 |
|---|---|---|
| OTA ZIP/JAR certificate material | CONFIRMED | `META-INF/com/android/otacert`、`key_type=release-keys`、`RecoverySystem.verifyPackage` call |
| Java metadata/product/version/signature-transition/PVT gates | CONFIRMED | `SideloadMetadataChecker.java` 與 `OSUpdateValidator.java` |
| Native block verification | CONFIRMED capability | `VerifyBlocks`/block-image CFG markers與 `LoadSrcTgtVersion3` call sites |
| AVB verification exact implementation/branch | UNKNOWN | 保存 corpus 只有 boot/recovery/AVB markers，未保存完整 verifier chain |
| rollback index / anti-rollback exact decision | UNKNOWN | package metadata/date/version gates 不等於 bootloader rollback index check；無完整 rollback branch proof |
| signature/AVB/rollback bypass | NEGATIVE for analyzed static chain | 沒有保存 evidence 指向 bypass；未做 crafted OTA 或 runtime test |

不能把 `VerifyBlocks`、`otacert` 或 `ro.expect.recovery_id` 單獨升格成完整 AVB/rollback
證明；同樣不能因 verifier body 缺失而宣稱 bypass。

## 6. PS7330 mismatch（歷史，與目前 PS7331 分開）

`firmware/manifests/OTA-20260803-01/README.md` 明確標示：當時裝置快照是
`PS7330.4104N`，而保存 OTA 是 `PS7331.4463N`，因此該包只可作 adjacent-version
analysis，不能作 exact installed-firmware evidence，也不能 flash。這是歷史
**VERSION_MISMATCH**，不改寫本報告對 PS7331 package contents 的靜態結論。

本報告對 PS7331 的 package identity、解包 members、script targets、update-binary
hash 與 Java OTA source 是 PS7331-scoped；PS7330 的 live identity、舊 snapshot 或
早期 mismatch finding 不得被引用成 PS7331 caller、permission 或 verifier result。

## Final status

**PS7331：** native recovery writer capability = CONFIRMED；Java validation/staging
chain = CONFIRMED；canonicalization-to-write exact data-flow = UNKNOWN；AVB exact
implementation = UNKNOWN；rollback exact check = UNKNOWN；普通 app/shell 到達完整
writer = NEGATIVE（已分析 scope）；postinstall executable = NEGATIVE（package-shape
scope）。

**安全邊界：** 只保留 host-only 靜態證據；沒有執行 bin、sideload、flash、reboot 或
任何設備修改。
