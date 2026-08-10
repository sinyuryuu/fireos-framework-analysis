# 支線 C：Fire OS 7.3.3.1 OTA/post-install/update static audit

日期：2026-08-10。範圍限唯讀 host-side audit：firmware OTA/bin、extracted metadata、`updater-script`/`update-binary`、fosinit、OOBE/`BootAfterSystemOTAReceiver`、既有 Phase 5/6 OTA artifacts。未修改 OTA，未執行 `update-binary`、recovery、sideload、flash、reboot、partition write，未 replay broadcast。

## 結論

PS7331 是 signed full/block OTA。保存的 script 與 native updater 明確具備 system/vendor、boot-chain、recovery cache、temporary staging、rename/chown/open/write 等 recovery/updater capability；這些是固定高權限更新能力，不是漏洞，也沒有證據顯示 shell 或普通 app 可直接取得該 capability。

Java path 是 metadata/device/product/version/PVT/hash/`RecoverySystem.verifyPackage` → staging → `UpdateSystem.install` 的受 gate handoff。`SideloadMover`/`FileHelper` 可走 basename staging、`renameTo` 或 copy/delete fallback；保存 corpus 沒有完成 canonical/no-follow、race、SELinux label 或 caller UID 閉包，因此不宣稱 symlink/traversal 漏洞。

Native path 已閉合到 handler registry、`WriteToPartition`→`ota_open`/`ota_write`→`open`/`write`，以及 block-image cache cleanup 的 `readlink`/`stat`/`unlink` markers。這只證明 recovery/updater capability；indirect dispatch、完整 path dataflow、平台 recovery verifier、AVB rollback index、slot handoff、authoritative post-install executor 仍有缺口。

`AmazonPackageManagerService.onBootPhase(550)` 在 `PMS.isUpgrade()` 下送出 protected `BOOT_AFTER_SYSTEM_OTA`；receiver 可 enable `OobeHomeActivity` 並寫 OOBE setup state。這是 system-server lifecycle sink，不是普通 HOME replacement，且沒有人工 replay 或 runtime effect。保存的 fosinit 是 derived system-image registration；它不能單獨推導 caller 或 SELinux domain。

## 可達性判定

- `RECOVERY/UPDATER_CAPABILITY`：binary/script 的固定 capability；不等於 caller reachability。
- `SYSTEM_SERVER_LIFECYCLE`：sender 受 boot phase、upgrade predicate 與 protected action boundary 約束。
- `PRIVILEGED_JAVA_HANDOFF`：controller permission 與 Java validation 在既有 path 中可見；implementation UID/native verifier/SELinux 尚未完全閉合。
- `LOW_PRIVILEGE_BOUNDARY_BOUNDED`：在保存 corpus 未找到 ordinary app 或 UID 2000 到 privileged OTA/partition sink 的完整 chain；不是 binary-wide absence。
- `UNKNOWN`：只表示保存證據未閉合，不表示已繞過或已否定。

## 主要輸入 hash

- Original OTA：`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`
- `updater-script`：`4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`
- `update-binary`：`02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`
- `target.system.file_map`：`a535ef97639495175bf4188a1ad1769ba8206bbd69c1b033367b2b5328ecc1ab`
- `target.blocklist`：`f0a3f810d0dab5486a59cc22b9fc9390e9668760ab5a2b1229580a27fb05d83c`

完整 evidence matrix 在 [CSV](./luna_worker_next_ota_postinstall_20260810.csv)；CSV 欄位固定為使用者指定的 11 欄。

## QA / 拒絕測試清單

QA 應確認 CSV header、每列 11 欄、ID 唯一、引用檔案存在或明確標為 missing、輸出只包含本 Markdown/CSV，並以 `sha256sum` 計算兩檔 hash。此 audit 僅做文字/檔案/既有 artifact 的唯讀核對。

明確拒絕：構造或修改 malicious/malformed/downgrade OTA；執行 `update-binary` 或 recovery；sideload、flash、fastboot、reboot；任何 partition write；symlink/traversal/temp-staging race attack；人工 `BOOT_AFTER_SYSTEM_OTA` broadcast replay；private OTA Binder transaction replay；修改 OOBE/settings/component/package state；root/exploit/SELinux bypass；把固定 updater capability、缺失 edge、`priv-app` 位置或 `@Inject` 當成漏洞。

安全下一步僅限 host-side 完成 native indirect/canonicalization dataflow、確認 outer tar member listing 到 EOF、補 recovery/AVB/rollback source provenance；或在自然且已授權 OTA 後只讀收集 build、component、OOBE、HOME resolver 與 log evidence。
