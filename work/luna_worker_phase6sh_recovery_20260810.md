# Phase 6SH — PS7331 OTA/recovery host-only provenance and path-hardening

日期：2026-08-10。範圍限於保存的 Phase 6KT/6KU/6SD/6J artifacts、`update-binary` mini-debug/disassembly、`updater-script`、DeviceSoftwareOTA JADX/VDEX 與既有 manifest/source reports。未執行 updater/recovery/sideload/reboot/partition write，未構造 malformed OTA 或 symlink/traversal payload；只新增本報告與同名 CSV。

## 結論

- **Recovery verifier caller：已確認 Java-side caller，platform implementation/native recovery caller：UNKNOWN。** `SideloadVerifier.verifySideloadPackage()`（JADX: `SideloadVerifier.java:37-48`）呼叫 `RecoverySystemWrapper.verifyPackage()`；wrapper（`RecoverySystemWrapper.java:21-22`）只 delegation 到 `android.os.RecoverySystem.verifyPackage()`。這證明驗證 API handoff，不證明 recovery verifier 實作或其 caller identity。
- **UpdateSystem.install handoff：已確認。** install branch 是 `SideloadInstaller.installSideload():65-84` → `verifySideloadWithoutRecoveryCheck():65-68` → `SideloadMover.maybeMoveSideloadFile():31-44` → `installOSUpdate():40-47` → `UpdateSystemWrapper.install():33-44` → `UpdateSystem.install(...)`。`withoutRecoveryCheck` 是 branch 名稱；不能解讀成 verifier bypass，因為 `buildSideload()` 先有 `verifySideloadIntegrity()`，且低權限 caller-to-install sink 未建立。
- **Staging canonicalization / NOFOLLOW：UNKNOWN（Java-side bounded observation）。** `SideloadMover` 只以 input absolute-path 的 basename 組 external-data destination（lines 39-42）；保存的 Java corpus 未見 `canonicalPath` 或 `NOFOLLOW`。這不是 traversal/symlink 漏洞證據；`FileHelper`、framework/native、recovery staging、SELinux/context 與 actual flags 未完整保存。
- **rename/copy semantics：已確認 Java implementation shape，但 race/atomicity/security outcome：UNKNOWN。** `FileHelper.moveFile():305-343` 先 `renameTo(destination)`；失敗後 `copyFile()`，其 `FileInputStream`/`FileOutputStream` buffered 8192-byte copy 在 `copyFileInner():56-149`，再 `source.delete()`（lines 314-322）。destination 已存在時先 MD5 比對，匹配則刪 source，否則拒絕（lines 324-343）。未對 symlink/traversal 做動態測試，故不標漏洞。
- **Protected lifecycle caller：已確認 system-server lifecycle provenance，receiver-side exact delivery user/完整 native post-install caller：部分 UNKNOWN。** Phase 6SD 保存的 chain 是 `AmazonPackageManagerService.onBootPhase(550)` → `PMS.isUpgrade()` → protected `BOOT_AFTER_SYSTEM_OTA` → `BootAfterSystemOTAReceiver`；receiver 還有 action/OOBE/retail-demo/preferences predicates，可能 enable `OobeHomeActivity`、寫 OOBE setup state。這不是已確認的 Fire Launcher preferred-HOME writer，也不是 arbitrary broadcast route。DeviceSoftwareOTA manifest 顯示 controller permission 為 `com.amazon.dcp.ota.permission.CONTROLLER`，protection level `0x3`（signature|privileged）；controller receivers/API 因而屬 protected lifecycle surface。
- **Shell / ordinary-app route：未建立（Strong evidence negative boundary）。** `DeviceSoftwareOTA` controller surface 受 signature|privileged controller permission 及 metadata/sanity/hash/recovery/device-state gates；native `update-binary` 僅證明 recovery/high-privilege capability。現有 artifacts 沒有 shell 或 ordinary app → verifier/install → recovery/update-binary → partition writer 的合法 caller chain。不要把 exported metadata、native write capability、缺少 Java canonicalization marker 或 marker string 當漏洞。

## Provenance ledger

| Layer | Static result | Disposition |
|---|---|---|
| Package verification | `SideloadVerifier` metadata/sanity → `RecoverySystemWrapper` → platform `RecoverySystem.verifyPackage` | Confirmed Java caller; verifier implementation/native caller UNKNOWN |
| Install handoff | `SideloadInstaller` → basename staging → `UpdateSystemWrapper` → `UpdateSystem.install` | Confirmed |
| Staging path | basename destination under OTA external-data directory; no observed Java `canonicalPath`/`NOFOLLOW` | UNKNOWN; no vulnerability claim |
| File transfer | `renameTo`, fallback buffered copy, source delete; existing destination uses MD5 comparison | Confirmed shape; atomicity/race/symlink semantics UNKNOWN |
| Native updater | mini-debug/disassembly resolves extraction, block-image registration, `ota_open`/`open`, `ota_write`/`write`, `rename`/`chown`; script has fixed by-name targets | Capability confirmed; reachability not established |
| Protected post-OTA lifecycle | system-server `onBootPhase(550)`/`isUpgrade()` → protected `BOOT_AFTER_SYSTEM_OTA` receiver; OOBE predicates | Caller chain confirmed; exact delivery/native post-install caller partly UNKNOWN |
| Low-privilege route | no shell/ordinary-app caller to privileged handoff in bounded corpus | Strong evidence negative; not universal proof |

## Native/static boundary

Phase 6KT/6SD/6KU/6MD/6MK/6MM/6NE artifacts consistently show capability only: fixed updater-script targets include `/dev/block/platform/bootdevice/by-name/system`, `vendor`, `boot`, `preloader`, `lk`, `tee1`, `tee2`, `spmfw`, `sspm_1`, `cam_vpu1-3`, plus `/cache/recovery/last_blocklist`; block-image registration maps handlers to preserved functions and selected direct edges show `WriteToPartition`/`ota_write`/`write`, `rename`, `chown`, and a cache `__readlink_chk` call site. The selected graph does not close canonicalization to extraction/partition write; indirect dispatch, unselected CFG/dataflow, recovery staging and caller provenance remain UNKNOWN.

## Protected lifecycle / route boundary

`BOOT_AFTER_SYSTEM_OTA` is a system-server upgrade lifecycle, not evidence that an app can send an equivalent accepted broadcast. The saved Phase 6SD interpretation is that it can affect OOBE activity/setup state under predicates, but no Fire Launcher preferred-HOME writer was found. `MY_PACKAGE_REPLACED`/Alexa receiver observations likewise do not establish arbitrary caller acceptance. No private Binder transaction, broadcast replay, sideload, updater/recovery execution, reboot or device mutation was used.

## Input hashes

Principal preserved inputs and generated artifact hashes are recorded in `luna_worker_phase6sh_recovery_20260810.csv`. The repeated `update-binary` and `updater-script` hashes are provenance checks, not newly recovered evidence.

