# Phase 20B — PS7331 OTA/recovery boundary closure

日期：2026-08-10。這是以 P19B residual edges 為輸入的 host-only 靜態 closure。檢查 exact PS7331 OTA、extracted system image provenance、Java OTA sources、native `update-binary` disassembly、保存的 PS7331 runtime `update_verifier`/`install-recovery.sh` 與 PHASE19 baseline snapshot。未執行 `update-binary`、recovery、sideload、reboot；未構造 malformed OTA，未做 symlink/race/traversal 或 partition 操作。

## 結論

P20B 將 caller → gate → sink 的保存證據收斂如下：

1. Java caller chain 可閉合到 `OSUpdateValidator`/`SideloadVerifier` 的 hash + `RecoverySystem.verifyPackage`，再到 metadata/PVT/device validation、staging 與 `UpdateSystem.install`。這是 privileged OTA lifecycle 的 static handoff；沒有 ordinary app/shell → install 的 chain。
2. Exact PS7331 system image 中的 `update_verifier` 可靜態確認 first-boot/system-OTA verification capability：讀取 `/data/ota_package/target.blocklist` 或 `/cache/recovery/last_blocklist`，解析 caremap、mount point、length、SHA1/device info，檢查 block ranges，並經 boot-control HAL 對 slot 做 `markBootSuccessful` / `setSlotAsUnbootable` 相關處理；failure path 含 reboot。這是 post-update verifier sink，不是 AVB rollback-index implementation，也不是 caller proof。
3. `install-recovery.sh` 可靜態確認 recovery image repair/install capability：`applypatch` 檢查/重建 recovery，並以 `dd` 將 recovery signature 寫入 fixed by-name recovery device。PS7331 file map 同時列出 `update_verifier.rc`、`install-recovery.sh`、`fireossystemota_fosinit.xml` 與 `init.leakrecoveryd.rc`，但保存 host corpus 沒有把 init action/service stanza、SELinux allow rule、實際 UID/domain transition 接到該 script/verifier。
4. Native updater cache path 不再只是 string marker：selected disassembly 看到 cache entry 經 `stat64`，要求 regular-file mode，再呼叫 `readlink_chk`、長度/`strncmp` 檢查及後續 unlink/space bookkeeping；但沒有證據證明這是所有 staging/write path 的 canonicalization gate，也沒有 open-handle/no-follow/same-object revalidation 或 race guarantee。
5. AVB/rollback 仍為 bounded-unresolved。`update_verifier` 的 boot-control/slot and block verification markers 不等於 AVB key verification 或 rollback-index compare；extracted PS7331 package 沒有 `vbmeta.img`/`META-INF/com/android/avb*`，且沒有 exact native recovery caller/authority chain。PHASE19 baseline 的 `green` verified boot、`Enforcing`、`ro.debuggable=0` 與 shell UID 2000 只描述保存 snapshot，不補出 caller reachability。

## Evidence closure

CSV 只使用唯一 `P20B-*` IDs，逐列列出 caller、gate、sink、missing edge 與 classification。`CONFIRMED_STATIC` 表示保存 source/disassembly/image evidence 已直接觀察到；`BOUNDED_UNKNOWN` 表示仍缺 exact edge；`NEGATIVE_BOUNDARY` 表示在 bounded corpus 未建立低權限路徑，不是 universal absence。

### Exact package and Java handoff

原始 PS7331 package identity 維持 P19B：27-entry SignApk ZIP/JAR、`ota-type=BLOCK`、`pre-device=trona`、PS7331.4463N、release-keys、timestamp gate；`updater-script` 的 fixed system/vendor/boot-chain targets 與 `/cache/recovery/last_blocklist` 是 recovery-side sinks。P20B 不重複把這些 capability 當成 exploit 或 caller。

`OSUpdateValidator.validateOSUpdate` 依序呼叫 `assertHash`、`RecoverySystemWrapper.verifyPackage`、`OSUpdatePropertiesValidator.assertUpdatePropertiesValid`；`SideloadInstaller` 的保存 flow 經 `verifySideloadWithoutRecoveryCheck`、`SideloadMover.maybeMoveSideloadFile` 與 `UpdateSystemWrapper.install`。方法名稱不代表 bypass：平台 verifier implementation、caller UID 與 native recovery executor 仍未由 Java source 關閉。

### Verifier / rollback boundary

`update_verifier` 的 strings 與既有 runtime-binary audit 提供 strong static implementation provenance：`target_blocklist.cpp`、`bootctrl_wrapper.cpp`、`board_verify.cpp`、`rangeset.cpp`、`getService(android.hardware.boot@1.0)`、`ro.boot.slot_suffix`、`markBootSuccessful`、`setSlotAsUnbootable`、`persist.sys.ota.verified`、`amzn_ota_verified` 等。這能把 post-update block/caremap verification 與 slot outcome sink 分開標示，但無法從 strings 單獨證明 call order、AVB key authority、rollback index value/compare 或 actual execution。

`install-recovery.sh` 的 fixed recovery device writes 與 system file map 只證明 image content/repair capability。`update_verifier_nonencrypted=stopped`、`leakrecoveryd=stopped` 是保存 snapshot 的 state，不是 verifier 永不執行的結論，也不是 shell 可啟動它的證據。

### Path / TOCTOU boundary

Java staging 仍是 input absolute path basename → OTA external-data directory destination → `renameTo` 或 buffered copy/delete fallback；source corpus 沒有 `canonicalPath`、`NOFOLLOW`、directory-fd 或 same-object revalidation marker。Native cache helper 已見 `stat64` regular-file test、`readlink_chk`、`strncmp`、`unlink`，但 selected graph 沒有把 result 接到 final extraction/partition write authorization，且 no-follow/race semantics 未證明。不得將此分類為 symlink/TOCTOU vulnerability。

### UID / SELinux / reachability

保存 PHASE19 snapshot：`uid=2000(shell)`, `context=u:r:shell:s0`, `Enforcing`, `ro.debuggable=0`, verified boot state `green`。這支持 shell/recovery separation 的 observed boundary；它沒有提供 update controller UID、recovery UID、`update_verifier` domain、`update-binary` exec transition 或 SELinux allow chain。故 final classification 保持 `NEGATIVE_BOUNDARY`/`BOUNDED_UNKNOWN`，不把 privileged capability 升格為 low-privilege reachability。

## Final disposition

P20B 的 closure result 是：

`Java verification/install handoff: CONFIRMED_STATIC; updater and post-update verifier sinks: CONFIRMED_STATIC capability; cache path guard: PARTIAL_STATIC; AVB rollback authority, native recovery caller, UID/SELinux transition, and TOCTOU revalidation: BOUNDED_UNKNOWN; shell/ordinary-app reachability: not established.`

沒有證據支持 signature bypass、AVB rollback bypass、symlink/race exploit、SELinux bypass、shell/ordinary-app OTA entry、post-install arbitrary code execution 或 partition-write reachability。剩餘工作若要繼續，仍限 host-side exact init/SELinux source recovery、native verifier CFG/call graph、AVB/rollback implementation provenance 與 staging dataflow；不得以 OTA execution、malformed input、recovery/sideload/reboot 或 partition write 補洞。

