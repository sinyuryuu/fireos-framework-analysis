# PS7331 / Fire OS 7.3.3.1 kernel driver surface follow-up 2

日期：2026-08-10。這是既有 host-only 結果的增量／正規化版本，不是重新執行裝置測試，也不覆寫既有檔案。

## 範圍與安全界線

本次只重整已保存的 GPL source、boot/config、install/OTA artifact 與 Phase 5/6 reports。未執行 adb、任何 device-node open、ioctl、Binder/service call、Root、exploit/PoC、OTA/recovery/update-binary、reboot 或 partition write；未下載或執行未知程式。

既有同主題結果保留不動：

- `work/luna_worker_kernel_gpl_driver_surface_followup_20260810.md` — SHA-256 `16ccc5ab63b6cd7e902532965a25b24d06d7dcc1b8ccbdf4e8362ee9b3bc5272`
- `work/luna_worker_kernel_gpl_driver_surface_followup_20260810.csv` — SHA-256 `f4b82cc8a9ae50f85866bc2b1b7710587e4d71c644424968a9f60b4c42636aba`

本增量 CSV 使用指定欄位：`surface,source/artifact,user_entry,permission_or_selinux,caller_reachability,sink,existing_evidence,status,next_safe_step`，共 13 筆資料列。

## Provenance

主要輸入與既有雜湊引用如下：

- 官方 source archive `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`: `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`。
- GPL platform archive `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`。
- Preserved boot image `firmware/extracted/PS7331/boot.img`: `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。
- Embedded kernel/config manifest `kernel/source-manifest.json`: source archive SHA-256 `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`、embedded config SHA-256 `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`。
- Official OTA package `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`: `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`。

## 結論

Source capability 不等於 user reachability。`unlocked_ioctl`、`copy_from_user`、`device_create`、source mode、Kconfig 或 SELinux allow 只能證明部分能力或靜態配置；要聲稱可由 user/shell/app 到達，仍需 node 存在、Unix mode、file-context、SELinux domain、實際 caller 與 effect 的獨立證據。

目前唯一有保存 runtime reachability 的 driver route 是 shell UID 2000、`u:r:shell:s0`、SELinux Enforcing 下對 `/proc/ged` 的 read-only query；它是 telemetry，不是 LPE，也沒有通往 HOME、PackageManager、ActivityManager 或 Fire Launcher 的 sink。

CMDQ、ION、RPMB、evdev、USB、Amazon liquid-detection、Amazon test proc、MediaTek debugfs/sysfs 等列為 source-only、unknown 或 bounded negative；沒有把它們提升為 exploitability finding。Amazon 程式碼的 canonical kernel path 是 `drivers/staging/amazon` 與 `platform/device/amazon/kernel/driver`，不是不存在的 `drivers/amazon`；`platform/vendor/mediatek` 是獨立 archive tree，不能僅由目錄存在推定 boot kernel 編入。

## 分類規則

- `confirmed shell telemetry`: 有保存的 shell caller 與 read-only query 結果，但不代表寫入能力。
- `source-capability-only` / `static-only`: source/config 有入口或 sink 形狀，缺 runtime node/caller/effect。
- `unknown`: 關鍵 node、label、SELinux、caller 或 build provenance 未閉合。
- `closed`: 既有證據對指定低權限路徑已有 bounded negative；不宣稱宇宙性不存在。
- `risk-rejected`: 需要危險 ioctl、DMA、debugfs/sysfs write、secure-world 或 storage mutation 的動態驗證被安全界線排除。

## 交付

- [正規化 CSV](./luna_worker_kernel_driver_surface_followup2_20260810.csv)：13 data rows；header 完全符合指定 schema。
- 本檔與 CSV 是本次新增檔案；既有 `...kernel_gpl_driver_surface_followup_20260810.{md,csv}` 未修改。

最小安全後續仍是 host-only join：`registration → fops/attribute → Kconfig → file-context → SELinux policy → preserved caller → sink`。不需要也不應進行 device-node、ioctl、Binder、OTA/recovery 或 partition 操作。
