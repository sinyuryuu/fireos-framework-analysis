# Luna worker — PS7331 kernel/source custom-driver surface follow-up

日期：2026-08-10
範圍：bounded host-only；只讀本機 source、既有 findings/artifacts。沒有 ADB、網路、Binder/service call、ioctl、root/exploit、OTA/recovery/fastboot/reboot、安裝或裝置/分割區變更。

## 1. 固定輸入與 scope

`kernel/source-manifest.json` 指定的 build-selected source root 是：

`firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4`

其 metadata 為 Amazon/trona、MT8183、Android 9/API 28、kernel 4.4.146+、PS7331.4463N；canonical tree 有 7,803 個檔案。整個 source archive 的已核對輸入 hash：

| Input | SHA-256 |
|---|---|
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| `kernel/source-manifest.json` | `ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a` |
| `tools/scripts/index_phase6n_kernel_user_surfaces.py`（既有索引工具） | `23334c568ff04f5be162ab9d12860c7f601300f752be2eff65915152d06fcde6` |
| `output/tables/phase6n-kernel-user-surfaces.csv`（既有索引） | `f971b8e1c976ea410ca990c636c9374c826254b0d3f99cde120ae0bff8e44eaf` |
| `artifacts/phase6g/phase6g-cmdq-static-20260804-01/cmdq-static.json` | `021e02c2143901a757cd63eb79fae975b52d01b6efda7fef1c2113fb42d3c638` |

本次查閱的主要路徑：`drivers/misc/mediatek/`、`drivers/staging/amazon/`、`drivers/staging/android/ion/`、`drivers/input/`、`drivers/power/mediatek/`、`drivers/usb/`、`drivers/char/`、`platform/vendor/mediatek/`，以及 `kernel/source-manifest.json`、`findings/phase-6{br,ez,fs,ga,ha,is,n}.md`、`findings/phase-6g-cmdq-static-surface.md`、`artifacts/phase6g/*`。

## 2. 實際路徑盤點

| Requested surface | canonical tree 結果 |
|---|---|
| `drivers/amazon` | 不存在；Amazon kernel driver 實際在 `drivers/staging/amazon/`（例如 `amzn_idme.c`、`amzn_logger.c`、`amzn_sign_of_life.c`、`amzn_ld.c`） |
| `drivers/misc/mediatek` | 存在，1,877 files；含 `cmdq/`、`gpu/ged/`、`mdp/`、`geniezone/`、`ccu/`、`smi/`、`sched/`、`ion` 相關整合等 |
| `mediatek`（source root 直下） | 不存在；MTK kernel surface 位於上述 `drivers/.../mediatek` 與 `arch/.../mediatek` |
| `vendor/mediatek`（canonical kernel root 內） | 不存在；archive 另有 `firmware/extracted/PS7331-SOURCE-20250617/platform/vendor/mediatek/` |
| `drivers/input` | 存在，117 files；含 `keyboard/mediatek`、`touchscreen/mediatek`、Goodix/Himax/Synaptics 等 |
| `drivers/power` | 存在；MTK 子樹為 `drivers/power/mediatek/`，32 files，含 battery/charger/misc |
| `drivers/usb` | 存在，162 files；含 core/gadget/class/host 與 MTK 相關 host/PHY |
| `drivers/char` | 存在，19 files；含 `rpmb/rpmb-mtk.c` 等 |
| ION | 實際為 `drivers/staging/android/ion/`，27 files；不是 `drivers/misc/mediatek/ion` 直下 |

這些 counts 是路徑 inventory，不是漏洞數量，也不表示每個檔案都被 trona_defconfig 編入或由量產 image 使用。

## 3. 分類摘要（固定 canonical tree）

以 source text marker 分類（行數；同一行可屬多類）：

| 類別 | 行數 | 代表路徑/觀察 |
|---|---:|---|
| `unlocked_ioctl` | 305 | CMDQ `cmdq_driver.c`、GED `ged_main.c`、ION、CCU、GZ、SMI、MDP、MTK input/power/char |
| `compat_ioctl` | 170 | CMDQ、GED、ION、CCU、GZ、SMI、scheduler、charger/RPMB 等 |
| procfs (`proc_create`/`proc_mkdir`) | 367 | CMDQ debug/status、GED `/proc/ged`、MTK scheduler、Amazon proc drivers |
| sysfs/device attributes | 1,090 | CMDQ `log_level`/`profile_enable` 等、scheduler、GZ、battery/charger；多數是 mode/建置條件依賴 |
| debugfs create | 198 | GED、CMDQ/MTK debug surfaces；不是 Android framework API |
| `device_create(` | 58 | CMDQ `mtk_cmdq`、MDP、SMI、CCU、scheduler、RPMB、input/power 等 |
| `copy_from_user` | 904 | ioctl、proc/sysfs write、GPU/MDP/CMDQ/ION/CCU/GZ/SMI 等 user-copy |
| `capable`/`ns_capable`/`CAP_SYS_*` | 28 | 主要是一般 kernel/MTK scheduler capability checks；CMDQ/GED 入口本身未見 local UID/CAP gate |
| UID/GID credential markers | 76 | 多為一般 cred plumbing；`mtk_sched.c` 有 `uid_eq`，不是 launcher/package authorization |
| SELinux/security/permission markers | 41 | kernel security hooks/driver security constants；實際 node gate 仍由量產 SELinux label、Unix mode、init/config 決定 |

重點 driver surface：

* **CMDQ**：`cmdq_driver.c:660-743` 有 ioctl/compat dispatcher，`848-865` 有 chrdev/class/device registration，`816-824` 有 debug proc，`894-898` 有 device attributes；`mdp_ioctl_ex.c:1060-1062` 有 ioctl/compat 與大量 user-copy。既有 Phase 6G/6FS/6HA 已記錄 structured request、readback/async/DMA 與 secure-metadata count/length candidate。
* **ION**：`drivers/staging/android/ion/ion.c` 有 `ion_ioctl`/compat、ALLOC/FREE/SHARE/MAP/IMPORT/SYNC/custom surface 與 user-copy；既有 Phase 6N 已將其列為 source surface，但未證 runtime reachability 或 impact。
* **GED**：`ged_main.c` 有 `/proc/ged` mode 0644、unlocked/compat ioctl；既有 query-only evidence 證實 telemetry reachability，沒有 package/Binder/HOME state change。
* **Amazon**：canonical path 不是 `drivers/amazon`，而是 `drivers/staging/amazon`；IDME 會剝除 write bits，logger 是 read/poll/open/release，lifecycle proc read-only；既有 Phase 6BR 已對 runtime SELinux/Unix boundary 做 closure。
* **input/power/usb/char**：存在多個 ioctl、sysfs/proc、user-copy 或 device registration；它們是硬體、充電、輸入、USB、RPMB/診斷 surface，未見 launcher/package sink。

## 4. Launcher / PackageManager / privilege 關聯

在 canonical kernel C/H tree 對 `launcher`、`packagemanager`、`package_manager`、`com.amazon.firelauncher`、`setHomeActivity`、`preferred_home`、`ACTION_MAIN`/`CATEGORY_HOME` 的直接搜尋為 **0 direct hits**。`HOME` 的少量 generic hits 屬 kernel 常數/一般 header 或無關字串，不能解讀為 Android HOME resolver 關聯。

因此目前 evidence chain 是：

```text
ordinary caller -> Unix node mode + SELinux -> Amazon/MTK driver
                                      -> hardware / telemetry / DMA / secure-world
                                      -X-> AMS/ATMS/PMS/HOME/Fire Launcher writer
```

`unlocked_ioctl`、`device_create`、`copy_from_user`、proc/sysfs/debugfs writer 或缺少 local `capable()`，都只證明 source surface；不證明漏洞、低權限 app reachability、root、privilege transition 或 launcher/package mutation。

## 5. 對照既有 findings/artifacts

| 狀態 | 已有證據與本次處理 |
|---|---|
| 已完成／重複 | Phase 6N `4,278 markers / 343 files` 的全索引；本次只補 requested-path 實際位置與 canonical-tree 分類，不重做既有 CSV。 |
| 已完成／重複 | Phase 6BR Amazon proc/sysfs/logger/lifecycle boundary；本次確認 `drivers/amazon` 缺失且實際是 `drivers/staging/amazon`，不把 Amazon driver surface 誤標成 launcher route。 |
| 已完成／重複 | Phase 6EZ/6GA/6IS vendor-driver-to-launcher negative closure；本次 kernel literal search 未找到 Framework/HOME direct edge，與既有結論一致。 |
| 已完成／重複 | Phase 6G/6FS/6HA CMDQ static surface、device registration、compat、user-copy、secure-metadata arithmetic observation；仍維持「candidate / not vulnerability」。 |
| 已完成／重複 | GED query-only exposure：既有 evidence 是 telemetry/query boundary，不外推為 write primitive、LPE 或 HOME control。 |
| bounded unknown | CMDQ `addrMetadataCount` multiplication/downstream `addrMetadataMaxCount` 的完整 arithmetic/dataflow proof，以及 exact shipped binary/source correspondence；禁止以 malformed ioctl 或 DMA/readback payload 驗證。 |
| bounded unknown | ION、MTK connectivity、部分 input/power/USB/char node 的 exact production reachability、Unix mode、SELinux domain/label 與 init registration；host source 不足以替代 runtime provenance。 |
| bounded unknown | source-visible sysfs/proc/debugfs writers 的實際量產 exposure；不得把 source mode 當成 device accessibility。 |

既有 Phase 6N 的「driver-to-HOME/PMS/root claim 已排除」與 Phase 6IS 的「不要重開 SELinux/private-service/vendor-driver route」仍有效。本 follow-up 不提出新 vulnerability finding。

## 6. 下一個最小安全 host-only 分析包

只建議離線、可重現、無裝置接觸的 package：

1. 以 `trona_defconfig`、`source-manifest.json` 與既有 Phase 6N CSV 為固定輸入，將每個候選 node/driver 正規化成 `path → registration → fops → user-copy → local gate → Kconfig`。
2. 對 CMDQ/ION/GED/M4U/CCU/GZ/SMI 各產生一列 `framework_sink = none|unknown`、`runtime_reachability = source-only|existing-readonly|unknown`、`evidence_class`；不發 ioctl、不建 payload。
3. 僅以 source/config/dataflow 做 CMDQ count/length proof（例如 unsigned width、check-before/after-multiply、downstream count 使用），並把 exact binary correspondence 留為 unknown。
4. 對 `platform/vendor/mediatek` 與 `platform/device/amazon` 做 path/config/init/sepolicy cross-reference，仍只讀檔案；若沒有 direct AMS/ATMS/PMS/HOME edge，維持 closure。
5. 輸出應是新的 host-only table/hash manifest；不得加入 runtime mutation、Binder replay、debugfs/sysfs/proc write、non-query ioctl、DMA、module load、reboot、OTA/recovery 或 partition operation。

## 7. 限制

此報告不能證明 canonical source 等於量產 kernel binary，也不能證明每個 built driver/node 被註冊、可由 shell/app domain 開啟，或受何種完整 SELinux policy 約束。既有 PS7330/PS7331 assets 仍不可交叉標成 exact-match。Source surface、ioctl existence、user-copy 或 missing local capability check 均不可單獨升格為漏洞、root、privilege route 或 Launcher/PackageManager route。
