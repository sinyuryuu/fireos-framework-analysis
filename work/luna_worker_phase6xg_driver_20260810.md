# Phase 6X-GPL/native — driver surface audit

日期：2026-08-10（Asia/Taipei）  
範圍：PS7331 / Fire OS 7.3.3.1 / MT8183 GPL source、merged kernel config、boot/native/policy artifacts 的 host-only 靜態 join。未執行 ELF，未 adb push，未開啟 `/dev`，未發送 ioctl、proc/sysfs/debugfs 操作，未做 exploit、offset 或 root。

## 去重後結果

CSV 只保留相對既有 GhostLock/driver reports 的新證據或精確否定，共 5 rows：

- `CONFIG_INPUT_UINPUT=y` 對應的 generic `/dev/uinput` 有完整 `read/write/unlocked_ioctl/compat_ioctl` fops 與 misc registration；source 未見 local `capable()` gate，但沒有 exact shipped native caller、package、UID/domain 或 HOME/PMS sink。
- power-supply sysfs 的 `.store` 並非一律 writable：只有 provider 的 `property_is_writeable()` 回傳正值時才加 `S_IWUSR`，再呼叫 `power_supply_set_property()`；本輪沒有 exact shipped writer。
- RPMB `rpmb_fops` 是精確的 read/write 否定：`.read = NULL`、`.write = NULL`，userspace ABI 只經 `unlocked_ioctl`；`device_create()` 使用 `RPMB_NAME "0"`。既有 `rpmb_svc` process evidence 仍不足以指向 native open/ioctl callsite、package 或 UID。
- GPL platform archive 沒有 `vendor/mediatek` path；這否定該 archive path 的 kernel-driver provenance，不否定其他 exact vendor artifact。
- Exact-build native inventory 與 bounded vendor policy scan 沒有 `/dev/uinput` 的 path-specific ELF caller、uinput file-context 或 allow tuple；這是 caller/policy closure 的精確否定，不是 node absence 或 SELinux denial 證明。

## Identity / sink boundary

本輪沒有任何新證據能把 source surface 映射到實際 package、UID 或 SELinux domain。`uinput` 的理論 sink 是 kernel input graph；power-supply 是 battery/charger property；RPMB 是 authenticated persistent storage。這些都不是已觀測的 PackageManager、ActivityManager、HOME resolver 或 Fire Launcher writer。

既有報告已處理 CMDQ/MDP、ION、GED、M4U、perfmgr、gsensor、Amazon IDME/logger/lifecycle/driver-test、generic evdev/USB 與 RPMB caller gap；本文件不重複其既有 rows，只補本 CSV 所列證據。

## Evidence integrity

- GPL archive：`firmware/extracted/PS7331-SOURCE-20250617/platform.tar`，SHA-256 `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`。
- merged config：`artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`，SHA-256 `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`。
- 每個 source member 的 SHA-256、exact lines、caller/identity/sink/status 見同名 CSV。
- native inventory：`artifacts/phase5/phase5cs-native-analysis-20260804-01/native-inventory.csv`，SHA-256 `9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`。

結論維持 source capability ≠ shipped reachability ≠ low-privileged caller。沒有新的 confirmed low-privilege path、root transition 或 package/HOME effect。
