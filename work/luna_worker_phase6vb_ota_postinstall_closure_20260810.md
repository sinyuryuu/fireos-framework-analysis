# Phase 6VB — exact-build OTA/post-install 靜態稽核

日期：2026-08-10。僅做 host-side static audit；沒有構造/修改/執行 OTA，沒有 recovery、sideload、reboot、fastboot、partition write 或 flash。

## 結論

PS7331 是 full/block OTA。`updater-script:1-24` 直接寫 system/vendor、boot 及多個 boot-chain/firmware by-name block device，並將 blocklist 寫到 `/cache/recovery/last_blocklist`。原始 OTA SHA-256：`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`；script SHA-256：`4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`；update-binary SHA-256：`02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`。證據：`firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-24`、`artifacts/phase6md-native-updater-path-audit-20260810-02/updater-script-operations.csv`（SHA `baf9d3598cf35c009afe127401d77b3e2f0a2594c133ba71e6e5bf6b2562b367`）。

Java chain 為：hash/metadata/RecoverySystem verification → basename staging → `renameTo` 或 copy/delete → `UpdateSystem.install`。證據：`SideloadMover.java:39-42`（SHA `59131cf032d8544cd44ea839ad63eb37993d2853b4925bf56d10ede721693f63`）、`FileHelper.java:305-339`（`55a7f44a70735626be7ebde25e96812346f336fddbec2c87de29ac0fb709b980`）、`OSUpdateValidator.java:73-78`（`36fca220ec2332bee5e5af3c9c2317056a425b90507951345d5b729c76c6f256`）、`UpdateSystemWrapper.java:29-47`（`c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`）。這些 Java source 位於既有 `artifacts/phase6j/...` JADX；不是 `decompiled/jadx/ota-PS7331` 的內容。

Canonicalization 結論有界：phase6bp archive/file-map 稽核未見 symlink、traversal 或 duplicate path，但 file-map 有 `//system/...` absolute/empty-segment 形態。native binary 有 `symlink_realpath`/`realpath`/`readlink` markers；6MM 僅閉合 `MakeFreeSpaceOnCache -> __readlink_chk`，6MD/6MM 都未證明 canonicalization helper 直接連至 extraction/partition writer。證據及 hashes：phase6bp JSON `594ab2dddbb30739261418400913494d97dba1ad24de8422c1c831fc40ac4970`；phase6md markers `3fe90198a4de2b30d743191996e8476630603998df20d8f9f91fe942bc244ebb`；phase6mm callsite `8cc6d38c1e464b6b741b29bdee8aa253113e7aea286f368ffe1cf1c0cde5983d`。

Rollback/post-install/AVB 與 permission/identity 沒有完整閉包。可見的是 active/needs-reset state、post-update verification status、build-number success cleanup；AVB rollback index、slot/boot-control handoff、authoritative post-install executor、UID、SELinux domain、Binder `getCallingUid` 均 UNKNOWN。不可由 `@Inject`、priv-app 路徑或單一 manifest permission 推定權限。

## 輸入缺失

- `artifacts/phase6uo` 不存在。
- `decompiled/jadx/ota-PS7331` 存在，但未找到與上述 OTA chain 對應的 Java source；故 exact-build decompiled OTA implementation 為 UNKNOWN。
- 原始 tar hashes：`Fire_HD10-7.3.3.1-20250617.tar.bz2` = `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`；`Fire_HD10-7.3.3.0-20240730.tar.bz2` = `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665`。未重新解包/執行，member-level correspondence UNKNOWN。

## Evidence matrix

逐項檔案、行號/地址、SHA-256 與 UNKNOWN/限制見 [CSV](./luna_worker_phase6vb_ota_postinstall_closure_20260810.csv)。
