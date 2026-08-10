# Phase 12：主機端 OTA / update-binary / post-install 邊界審計

## 範圍與安全界線

- 工作區：`/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire`
- `pwd`：同上；`git HEAD`：`aeb8709519ab4c4cb5b9fc3e835f5cf30a9f5568`
- 只讀主機端分析。未使用 adb，未觸發 recovery/sideload、broadcast、Binder、OTA install、reboot、partition write，未執行 `update-binary` 或任何 post-install helper；未製作 malformed package、symlink/traversal payload、root 或刷機操作。
- 證據是 firmware extracted package、既有 decompiled/JADX/disassembly、既有 artifacts 與 AOSP reference tree 的主機端內容。沒有把靜態字串、manifest exposure 或未知 native handoff 當成 runtime 成功。

## 結論

1. PS7331 package 的 `updater-script` 明確包含 system/vendor block-image 及 boot/preloader/LK/TEE/SPMFW/SSPM/CAM VPU partition sink；這是可確認的高權限 sink contract，不是本次執行結果。
2. Package entry gate 可確認為時間、`ro.product.device == trona`，另有 metadata/`ota.prop` 的產品、版本、release-key/type 資料；Java sideload 路徑另有 filename、sanity、version/product/signature-transition/PVT、battery/storage 與 recovery verification gate。filename match 本身不能到達 installer。
3. `SideloadInstaller` 的 confirmed static chain 是 `verifySideloadWithoutRecoveryCheck` → optional move → `UpdateSystemWrapper.install` → `UpdateSystem.install(context,path,flags,{})`。Recovery/native verifier 與 `UpdateSystem` 實作是 UNKNOWN；沒有執行或重播。
4. Cache 路徑有兩種可確認行為：Java device-state cleanup 會清理 download-cache 並排除 recovery-cache；native `MakeFreeSpaceOnCache` 會列舉 cache、讀 link/stat 並呼叫 `unlink`。對 canonicalization、symlink policy、實際 cache root 與 runtime effect 不作超出證據的推論。
5. post-OTA OOBE sender 是 system-server 的 boot phase 550 + `PackageManagerService.isUpgrade()` 路徑，帶 `com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA` 發送；receiver 再以 action/OOBE-running/retail-demo 條件 gate，成功時 enable `OobeHomeActivity` 並寫 `user_setup_complete=0`、`isOOBEActive=1`。caller context/user 精確 handoff 與 runtime delivery 未重播，標 UNKNOWN。
6. AVB/verity、recovery native signature implementation、SELinux allow rules/actual domain、`postinstall` helper 是否在此 package 之外被調用，均沒有足夠的已保存證據閉合；均標 UNKNOWN，而不宣稱 bypass 或 exploit。

## 證據化 input → gate → sink

| surface | confirmed chain | sink/effect | caller scope | confidence |
|---|---|---|---|---|
| package script | package metadata/date/device → `updater-script` | block write system/vendor；extract image to named partitions | recovery/update-binary execution context only | High |
| update-binary | `main` parses script; `Evaluate` dispatches commands | `PackageExtractFileFn` / `PerformBlockImageUpdate`; native write handoff unresolved | UNKNOWN beyond recovery/updater context | High static / runtime UNKNOWN |
| sideload | filename discovery → Sideload sanity/metadata/PVT/device checks → recovery verify | `UpdateSystem.install` | OtaService task path; external caller not closed | High static |
| cache | cache-size check → `MakeFreeSpaceOnCache` | unlink selected cache entries; Java cleanup side effect | privileged OTA process/native updater context | High static |
| post-OTA OOBE | system-server boot phase + isUpgrade → protected permission → receiver predicates | component enable + setup settings writes | system-server sender; exact user/caller runtime UNKNOWN | High static |

## 逐項證據

- Package identity: `firmware/extracted/PS7331/META-INF/com/android/metadata` says `ota-type=BLOCK`, `pre-device=trona`, `post-timestamp=1746234888`, `ota-required-cache=0`; `ota.prop` says product `trona`, version `0031575863172`, `key_type=release-keys`, `sign_type=release`, `binary_type=full`.
- Script guards and sinks: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-24`; identical extracted rows are in `artifacts/phase6mk-updater-dispatch-20260810-01/updater-script-entrypoints.csv` and write contract in `artifacts/phase6aw/ota-write-contract-20260805-01/ota-write-contract.csv`.
- `update-binary` host artifact hash is `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`. Disassembly identifies `main`, `Evaluate`, `PackageExtractFileFn`, `PerformBlockImageUpdate`, `ota_open`, `ExtractEntryToFile`, `ota_fsync`; it does not establish that an arbitrary caller can start it or that any write happened. See `artifacts/phase6ne-updater-cache-flow-20260810-02/focus-disassembly.txt` and `direct-call-edges.csv`.
- Cache native evidence: `CacheSizeCheck` calls `MakeFreeSpaceOnCache`; `MakeFreeSpaceOnCache` calls `opendir`, `readdir64`, `__readlink_chk`, `stat64`, `unlink`, and `FreeSpaceForFile`. The artifact records the function boundary, not a runtime deletion. See `artifacts/phase6ne-updater-cache-flow-20260810-02/{selected-functions.csv,direct-call-edges.csv,return-branches.csv}`.
- Java service: `OtaService.onStartCommand` enqueues task resolution and schedules periodic work (`.../OtaService.java:118-125`). `OTABootReceiver` schedules boot tasks/immediate check (`.../OTABootReceiver.java:32-45`); `OTADeferredOSInstallReceiver` schedules deferred install (`.../OTADeferredOSInstallReceiver.java:20-29`). Manifest caller permissions/exported state for these exact entries is not fully closed in the selected source, so external caller scope remains UNKNOWN.
- Sideload verifier/install: `SideloadInstaller.java:40-48,65-94`; `UpdateSystemWrapper.java:29-44`. The wrapper remaps external storage to media storage, writes `persist.sys.ota.isScreenOffBeforeOTA`, then calls `UpdateSystem.install`; no runtime invocation was done.
- Sideload task/data state: `SideloadVerificationTask.java:36-77` rejects unreadable, in-progress, multiple, or non-newer sideloads and can remove all sideload files; existing validation matrix records metadata, PVT, recovery verification and device-state gates in `artifacts/phase6ab/ota-input-validation-20260805-03/ota-input-validation.csv`.
- Post-OTA OOBE: `artifacts/phase6u/bootafter-ota-scope-20260805-01/bootafter-ota-scope.csv` records action, receiver predicates, component mutation, settings mutation, system-server phase/isUpgrade sender, and permission metadata. `OOBEActivationHelper` source is the settings-write evidence; exact runtime receiver delivery is not claimed.
- Permission boundary: the saved union/source audit identifies `com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA` as the sender permission and signature/Amazon-level definition; see `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/` and `artifacts/phase6bk/protected-broadcast-union-20260810-02/`. The receiver declaration’s lack of a local `android:permission` does not prove ordinary caller reachability.
- SELinux/AVB: searched extracted firmware and saved policy/reference artifacts for OTA, recovery, AVB, verity, block-device and post-install labels. No complete allow-rule/domain-to-sink chain or AVB native verifier implementation was present in the bounded evidence. Classification is UNKNOWN, not a negative security finding.
- AOSP references: `aosp/android-9` and `aosp/references` were treated as semantic comparison sources only; no AOSP file in the bounded tree closes Amazon’s recovery, AVB, SELinux, or `UpdateSystem` handoff.

## Open gaps

- UNKNOWN: who can invoke `OtaService`/its receivers in the installed runtime, exact manifest exported/permission values for every OTA receiver, and Binder/JobScheduler caller identity.
- UNKNOWN: recovery signature/AVB/verity verifier implementation, certificate chain and exact handoff from package verification to updater execution.
- UNKNOWN: `update-binary` process UID/domain, SELinux allow rules for each named block device, and whether `postinstall` exists in an unexamined image/helper path.
- UNKNOWN: native path canonicalization and symlink handling for package extraction, cache cleanup and staging; no exploit payload was used.
- UNKNOWN: runtime effect, selected user, ordering and failure semantics of post-OTA OOBE delivery; no broadcast or settings/component mutation was performed.

## Reproduction boundary

Only host-side reads, hashing and static extraction/reporting were used. The existence of an explicit partition sink is a risk boundary requiring the natural verified OTA/recovery lifecycle for future observation; it is not authorization to invoke it.
