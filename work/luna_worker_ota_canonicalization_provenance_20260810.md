# Phase 6QC-C — PS7331 7.3.3.1 OTA canonicalization/provenance closure

日期：2026-08-10。範圍是保存的 PS7331 7.3.3.1 firmware、OTA APK/JADX、VDEX、native
`update-binary`、manifest/package dump、SELinux/init snapshot 的 host-only 靜態分析。
本輪沒有接觸裝置，沒有執行 OTA、Recovery、`update-binary`、updater、sideload、
symlink/traversal、reboot、partition write、Root 或未知 Binder transaction；沒有回退
工作區其他變更。

## 結論

在保存 corpus 內，合法 production path 可閉合為：

```text
privileged OTA controller/app
  -> metadata/sanity/device-state + hash
  -> RecoverySystem.verifyPackage (certificate/signature boundary)
  -> product/build/PVT-style OSUpdatePropertiesValidator
  -> SideloadMover staging
  -> UpdateSystemWrapper.install
  -> UpdateSystem.install(Context,path,flags,options)
  -> recovery/update-binary
  -> Edify registry
  -> package extraction 或 block_image_update
  -> WriteToPartition -> ota_open/ota_write -> write
```

這是一條「高權限 capability 已確認、shell/ordinary-app reachability 未建立」的
bounded result。`OSUpdateValidator` 的 verifier、certificate 與 product/PVT checks
位於 Java/native handoff 前；`RecoverySystemWrapper` 只是 platform API wrapper，保存的
Java corpus 沒有 cryptographic verifier 的實作。AVB/SELinux 只有 boot/init/recovery
邊界 markers 與 enforcing snapshot，不能升格成 AVB bypass 或 policy bypass。

`MakeFreeSpaceOnCache + 0x478` 在 `0x417bf0` 直接呼叫 `__readlink_chk 0x4ce4e8`，
但 selected graph 沒有它到 extraction、block-image 或 write sink 的 direct edge。這是
bounded negative；`CacheSizeCheck` body、全部 callers、function-pointer dispatch、
readlink return/error branches 仍未完全解析。沒有做 symlink/traversal 測試，故不作漏洞
結論。

## Caller、gate、identity、sink 摘要

| 範圍 | 靜態閉合結果 | 權限/身份與可達性 |
|---|---|---|
| Java verifier | `OSUpdateValidator.java:73-78`：hash → `RecoverySystem.verifyPackage` → `OSUpdatePropertiesValidator.assertUpdatePropertiesValid` | `/system/priv-app/com.amazon.kindle.otter.oobe` snapshot userId 10023；PROCESS_UPDATES/CONTROLLER 等 privileged/signature surface；非普通 app/shell caller |
| Sideload install | `SideloadInstaller.java:65-74`：metadata/sanity/device-state branch 後 `maybeMoveSideloadFile` → install；integrity method 另有 recovery check | 內部 privileged controller path；`verifySideloadWithoutRecoveryCheck` 是 install branch 的既有設計，不是 verifier bypass 證據；外部 caller chain 未完整保存 |
| Staging | `SideloadMover.java:31-44` basename destination + `FileHelper.moveFile` | Java source 無 canonicalPath/NOFOLLOW marker；canonicalization 行為可能在 helper/framework/native，未測 traversal |
| Handoff | `UpdateSystemWrapper.java:33-44` remap path、設定 screen-state，再呼叫 `UpdateSystem.install` | privileged Context / framework boundary；native/recovery caller identity 未由保存 Java 完全閉合 |
| Registry | main `0x400cb0` → `RegisterInstallFunctions 0x406978` / `RegisterBlockImageFunction 0x40d0a8` → `RegisterFunction 0x41d528`; cells `0x5af670-0x5af690` resolved | recovery/update-binary identity；registry registration closed，runtime dispatch 未執行 |
| Extraction sink | `PackageExtractFileFn 0x401fb8-0x402788` → `ota_open 0x426338` → extraction/fsync/close | privileged recovery updater capability；非 shell/ordinary-app route |
| Partition write sink | `BlockImageUpdateFn 0x40b8b8` → `PerformBlockImageUpdate` → `WriteToPartition 0x413c40-0x4142f0` → `ota_write 0x426d58` → `write 0x4d4a10` | named PS7331 targets fixed by script；write capability confirmed, execution/write explicitly false |
| Canonicalization | `MakeFreeSpaceOnCache 0x417778-0x417fc4` → `__readlink_chk` at `0x417bf0` | helper caller/input provenance and return-to-write data-flow unresolved；no traversal test |
| Boot/AVB/SELinux | `ro.boot.selinux=enforcing`, recovery-id/expect markers, `fireossystemota_fosinit.xml` path; no exact updater domain allow chain | boot/recovery privileged boundary only; no AVB/SELinux bypass or shell reachability |

完整逐列 evidence、exact VA/source path、hash 與 next-safe-step 見同目錄的
[`luna_worker_ota_canonicalization_provenance_20260810.csv`](luna_worker_ota_canonicalization_provenance_20260810.csv)。

## Production caller 與低權限結論

保存的合法 caller 是 OTA privileged/controller lifecycle：`DeviceSoftwareOTA` 相關
priv-app/component（例如 `com.amazon.kindle.otter.oobe` userId 10023）以及其 framework
`UpdateSystem` handoff；`com.amazon.dcp` 等保存 package dump 也具有
`com.amazon.dcp.ota.permission.CONTROLLER`，但這只證明 privileged capability，不等同
普通 APK 可取得該權限。

沒有證據把 shell UID 或 ordinary app 連到 `UpdateSystem.install`、recovery execution、
update-binary registry 或 partition write sink。`otadexopt` 的 shell-visible surface
是另一條 dexopt/precondition 路徑，不能當 OTA updater authority。故本輪應明確標示：
**bounded privileged capability；不是 shell/ordinary-app 漏洞。**

## Remaining safe closure

只剩 host-only 的有限缺口：解析 `CacheSizeCheck` 全部 CFG/return branches、
`MakeFreeSpaceOnCache` 所有 callers、function-pointer targets，以及從 readlink 結果
到 cache-size/write guard 的 data-flow；同時恢復 platform `RecoverySystem`/recovery
verifier 與 updater exec 的 exact native/SELinux identity。不得用 OTA execution、crafted
package、symlink/traversal、recovery、reboot 或 partition write 補足缺口。

## Evidence hashes

| Evidence | SHA-256 |
|---|---|
| `update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| `updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| `otacert.pem` | `5d52405362dcc9e755a4d972074ac7f886a5450e18fb6a6c2c2dad2b55730fe1` |
| `audit.json` | `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9` |
| `phase6mm summary.json` | `a0186bb7d053d23f002dc663b9ee3f312255410b35ed997a74e864fc8f9229a6` |
| `phase6md summary.json` | `6dec85cee148a60daba1e8c781f30370389c6d95ff787623cb6ac830f058a834` |
| `UpdateSystemWrapper.java` | `c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9` |
| `OSUpdateValidator.java` | `36fca220ec2332bee5e5af3c9c2317056a425b90507951345d5b729c76c6f256` |
