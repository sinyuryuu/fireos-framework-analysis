# Phase 6QC — privilege-surface closure beyond HOME

日期：2026-08-10

公開基準：`7065db1cfaf585212aba4337eb1697478cad40e8e`（Phase 6QB）

裝置 comparator：`G001LT0511550CFT` / `KFTRWI` / `trona` /
`PS7331.4463N`。本輪的三條審計線均使用保存的 PS7331 VDEX/JADX/smali、OTA
APK/native artifacts、manifest、fosinit、SELinux 與既有 read-only runtime
證據；沒有重新接觸裝置。

## Executive result

本輪將研究範圍從 Launcher 擴展至任何可能造成權限邊界跨越的候選面：

1. `preWarmApplicationForUser` 的 permission-result 使用方式；
2. tablet-specific `AmazonAspService` permission branch，以及相鄰的
   `AmazonAudioService`；
3. OTA verifier → recovery/native updater → partition-write 的 caller、驗證與
   canonicalization 邊界。

整合後的 26-row matrix 沒有閉合出：

```text
low-privilege caller
  -> accepted authorization gate
  -> system/root identity
  -> package/HOME/credential/SELinux/partition write
```

這是保存 artifacts 範圍內的 bounded conclusion，不是對所有未保存 Amazon
程式碼或所有 kernel 漏洞的不存在性證明。

## 分類結論

### 已證實（Confirmed）

- PS7331 `AmazonActivityManagerService.BinderService.preWarmApplicationForUser`
  存在 `APP_PREWARM` check、`clearCallingIdentity()`、PMS
  `getApplicationInfo()`，最後到 `startProcessLocked(..., "prewarm", ...)`。
  保存 corpus 中唯一直接 caller 是 Alexa 的
  `ExplicitIntentAction.prewarmApplicationProcess`；這是 process-prewarm sink，
  不是 package state、HOME 或 root writer。[`QC-PW-01`](phase-6qc-evidence-index.md#qc-pw-01)
- exact PS7331 ASP branch 在 tablet configuration 先回傳 `true`，再進入非-tablet
  的 `ASP_PERMISSION` check；這個 branch 是真實的靜態 authorization anomaly
  candidate。[`QC-ASP-01`](phase-6qc-evidence-index.md#qc-asp-01)
- 同一 ASP service 的 sinks 是 `nativeCommand`、capture/injection、IR 與
  audio/HAL-adjacent paths；reviewed body 沒有 PMS、ATMS、preferred HOME、
  package-state、credential/root、APK、OTA 或 reboot writer。[`QC-ASP-02`](phase-6qc-evidence-index.md#qc-asp-02)
- OTA Java verifier 具備 hash、`RecoverySystem.verifyPackage`、certificate、
  product/PVT/build validation；`UpdateSystem.install` 後可達 recovery native
  updater 與固定的 extraction/block-image/write sink。這證明 privileged
  capability，不證明 shell caller。[`QC-OTA-01`](phase-6qc-evidence-index.md#qc-ota-01)
- native `MakeFreeSpaceOnCache` 的 `0x417bf0 -> __readlink_chk 0x4ce4e8`
  marker 已確認；選定 graph 沒有到 extraction、block-image 或 partition write
  sink 的 direct edge。[`QC-OTA-02`](phase-6qc-evidence-index.md#qc-ota-02)

### 高可信推論（Strong evidence / Probable）

- 保存的 enforcing runtime capture 已顯示 shell UID 2000 找不到
  `amazonactivitymanager`／`amazonwindowmanager`，ASP 的既有 probe 回傳
  `-13/EACCES`；因此不能把 static tablet branch 或 prewarm method 直接等同於
  shell 可達。[`QB-RT-05`](phase-6qb-evidence-index.md#qb-rt-05)、
  [`QC-ASP-03`](phase-6qc-evidence-index.md#qc-asp-03)
- `AmazonAudioService` 的 reviewed mutators 受 Android/Amazon
  signature/privileged audio permissions，identity clearing 發生在檢查之後，
  sinks 限於 routing、volume、Dolby、HDMI、HAL-adjacent state；
  `getPackageInFocus` 是 read-only observation。[`QC-ASP-04`](phase-6qc-evidence-index.md#qc-asp-04)
- OTA partition writes 是 recovery/update privileged capability，且保存的
  production updater script 固定選定 targets；沒有 shell/ordinary-app →
  `UpdateSystem.install`／recovery execution 的閉合 caller chain。
  [`QC-OTA-03`](phase-6qc-evidence-index.md#qc-ota-03)

### 待驗證（Hypothesis / bounded unknown）

- prewarm 的完整 `Stub/onTransact`、所有 exact-build caller 與 permission holder
  仍不完整；其他 Amazon APK 不在保存 corpus 的 caller 不能被判定為不存在。
- `setPipVisibility(boolean)` 的完整 `Stub/onTransact`、caller、permission
  contract 尚未閉合；目前只確定它寫入私有 PIP state，沒有確定的敏感 sink。
- ASP/Audio 的 OEM `service_contexts`/`te` 映射與 native library 完整 caller
  universe 尚未完全保存。
- OTA `readlink` return/error branches、`CacheSizeCheck` callers、function-pointer
  dispatch 及 platform `RecoverySystem` native identity 仍可 host-only 深挖；
  不能以未閉合的間接 data-flow 推導 traversal 或 write primitive。

### 已排除（Disproved within reviewed scope）

- 沒有證據顯示 prewarm、ASP 或 Audio service 會修改 User-0 HOME、preferred
  activity、Fire Launcher package/component state，或產生 system/root credential。
- `AmazonAudioService.getPackageInFocus` 不能被稱為 package-management
  writer；它只讀取 focus。
- ASP tablet `true` branch 不能被稱為已取得 shell 音訊控制：既有真機結果是
  `EACCES`，且本輪沒有重播 Binder/native audio call。
- OTA `update-binary` 的 write sink 不能被稱為 shell 可用 primitive；保存的
  chain 需要受驗證的 privileged OTA/recovery lifecycle。

### 因風險拒絕測試（Risk-rejected）

- 不對 `amazonactivitymanager`、`amazonwindowmanager` 或
  `audiosignalprocessor` 猜測 transaction code、構造 parcel 或執行
  `service call`。
- 不重播 protected OTA/OOBE broadcast，不啟動 `UpdateSystem`、recovery、
  `update-binary`，不製作 OTA、symlink/traversal input。
- 不執行 native audio/ASP command、capture、injection 或 IR operation。
- 不執行 root exploit、kernel probe、reboot、settings/package mutation、
  APK 安裝、Fire Launcher disable/hide/suspend/uninstall/clear/force-stop、
  remount、SELinux 或 partition write。

## 1. Prewarm identity path

```text
Alexa system/priv-app caller
  -> IAmazonActivityManager.Stub.Proxy tx=1
  -> AmazonActivityManagerService.BinderService
  -> checkCallingPermission(APP_PREWARM) [result not observed consumed]
  -> clearCallingIdentity()
  -> IPackageManager.getApplicationInfo(user)
  -> PreWarmCacheHelper
  -> ActivityManagerService.startProcessLocked(reason="prewarm")
  -> restoreCallingIdentity()
```

`clearCallingIdentity()` 是需要保留的 code-review anomaly，但它本身只將
process-prewarm body 放在 system identity 下；目前沒有 package/HOME/root sink。
ordinary app/shell caller 尚未從完整 corpus 證明，且 private service lookup 在
保存的 enforcing runtime 被拒絕。因此不執行 transaction。

## 2. ASP / Audio path

```text
AmazonAspService.BinderService
  -> hasCallerGotPermission()
  -> tablet ? true : checkCallingPermission(ASP_PERMISSION)
  -> nativeCommand / capture / injection / IR
```

這條路的 static branch 與既有 runtime denial 必須分開保存。Audio service 的
identity-clearing methods 同樣只到 AudioService/AudioSystem/AudioCapabilities
等音訊 sinks，沒有通往 PackageManager、ATMS、HOME、OTA 或 root 的直接路徑。

## 3. OTA privileged path

```text
privileged OTA controller
  -> hash + RecoverySystem.verifyPackage
  -> certificate/product/PVT/build checks
  -> staging / UpdateSystem.install
  -> recovery/update-binary
  -> package extraction or block_image_update
  -> WriteToPartition -> ota_write -> write
```

`WriteToPartition` 與固定 OTA target 是高風險能力證據，不是低權限可達性證據。
`MakeFreeSpaceOnCache` 的 `readlink` 是待解析的 canonicalization marker；目前
沒有 direct edge 到 write sink，也沒有做任何 traversal execution。

## 4. Current device state

本輪沒有新實機輸出；採用 Phase 6QB 的 canonical read-only baseline：

- fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- SELinux：Enforcing；shell UID 2000
- HOME：`com.amazon.firelauncher/.Launcher`，priority 50
- Fire Launcher：`/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk`
- User 0、Fire package/component、本輪前的設定均未變更

baseline 的 SHA-256 與 command provenance 見 [`QB-RT-01`](phase-6qb-evidence-index.md#qb-rt-01)
至 [`QB-RT-05`](phase-6qb-evidence-index.md#qb-rt-05)。

## 5. Next safe value

若要繼續，最高價值仍是 host-only completeness，而不是在真機嘗試：

1. 完成 prewarm/PIP 的 `Stub/onTransact`、permission holder 與 exact-build caller
   inventory；
2. 保存並比對 ASP/Audio 的 OEM `service_contexts`、`te` 與 native symbol map；
3. 解析 OTA `CacheSizeCheck`、`readlink` return branches、function pointers、
   `RecoverySystem` native identity；
4. 只有在官方自然 OTA lifecycle 發生時，做 read-only before/after comparison。

在出現新的低權限 caller、明確可逆且非核心 sink 前，不應重做 private Binder
replay、protected broadcast、OTA/recovery、native audio 或 kernel probe。

## Reproducibility

```sh
python3 tools/scripts/build_phase6qc_privilege_closure.py --dry-run \
  --prewarm work/luna_worker_prewarm_identity_closure_20260810.csv \
  --asp work/luna_worker_asp_permission_sink_closure_20260810.csv \
  --ota work/luna_worker_ota_canonicalization_provenance_20260810.csv \
  --output output/tables/phase6qc-privilege-closure.csv \
  --manifest output/tables/phase6qc-privilege-closure.csv.manifest.json
```

The generator is write-once and explicitly reports that it contacts no device,
dispatches no Binder, performs no mutation, executes no OTA/recovery, and runs no
root/exploit operation. Raw worker reports and CSVs remain preserved under `work/`.
