# Phase 5CF：目前實機版本邊界與 PS7331 runtime 證據隔離

日期：2026-08-04

## 基線

本輪使用既有唯讀腳本，明確指定 serial
`G001LT0511550CFT`，Test ID `PHASE5CF-READONLY-20260804-01`。

原始輸出位於：
`adb/phase5/PHASE5CF-READONLY-20260804-01/`。

腳本保存 154 個命令輸出／狀態檔案及 SHA-256 manifest；所有命令均為
ADB read-only 或 host fastboot enumeration，沒有 reboot、bootloader transition、
package/setting mutation、exploit 或 partition write。

另以獨立 Test ID `PHASE5CF-OTA-METADATA-20260804-01` 執行 OTA metadata
只讀採集，原始輸出位於：
`adb/phase5/PHASE5CF-OTA-METADATA-20260804-01/`。該採集只讀取
`getprop`、可讀目錄列舉、OTA 相關 package path 與 HOME resolver，沒有啟動更新、
下載、安裝或重開機。

| Field | Observed value | Evidence |
|---|---|---|
| Model | `KFTRWI` | `device/model.stdout.txt` |
| Product/device | `trona` | `device/product.stdout.txt` |
| Build fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` | `device/fingerprint.stdout.txt` |
| Incremental | `0030099376260` | `device/incremental.stdout.txt` |
| Fire OS property | `7.0` | `device/fireos.stdout.txt` |
| Android base | API level inferred from fingerprint Android `9`; no new API mutation | fingerprint |
| Security patch | `2024-02-01` | `device/security_patch.stdout.txt` |
| Board/boot hardware | `mt8183` | `device/board_platform.stdout.txt`, `device/boot_hardware.stdout.txt` |
| Verified boot | `green` | `boot/verifiedbootstate.stdout.txt` |
| Flash locked | `1` | `boot/flash_locked.stdout.txt` |
| SELinux | `Enforcing` | `device/getenforce.stdout.txt` |
| Boot mode | `normal` | `boot/mode.stdout.txt` |
| Fire Launcher path | `/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk` | `device/firelauncher_path.stdout.txt` |

## 版本結論

### OTA metadata 邊界

| Observation | Evidence | Interpretation |
|---|---|---|
| `ro.build.mktg.fireos` | `PHASE5CF-OTA-METADATA-20260804-01/ota_props.stdout.txt` | `Fire OS 7.3.3.0` |
| `ro.build.version.name` | 同上 | `Fire OS 7.3.3.0 (PS7330/4104)` |
| OTA-related packages | `ota_package_paths.stdout.txt` | OTA packages are installed, but this does not prove a pending update |
| `/data/ota`, `/data/ota_package` | `readable_ota_paths.stdout.txt` | shell received `Permission denied`; contents are not inferred |
| HOME resolver | `home_result.stdout.txt` | resolver still reports Fire Launcher with priority 50 |

這些 metadata 只能確認目前版本與 OTA 元件存在；沒有從 shell 可讀範圍取得
PS7331 檔名、下載 URL 或待安裝 payload。這不是「不存在」的證明。

### 已證實

目前連線的實機仍執行 `PS7330.4104N`，不是 PS7331。先前保存的 PS7331
`boot.img`、IKCONFIG、source members 與 Image markers 是離線韌體／source
證據，不是目前這台平板的 runtime evidence。

因此不能把 PS7331 的 GhostLock source applicability 直接寫成「目前實機
可觸發」，也不能用目前裝置執行結果反推 PS7331。

Fire Launcher 目前是 system/privileged package；本輪只讀取其 package state，
沒有停用、hide、suspend、uninstall 或 clear data。

### 高可信推論

若要取得 PS7331 runtime 證據，首先必須讓裝置實際進入與官方 PS7331 artifact
一致的 build，並重新保存完整基線。這涉及更新／刷入路徑，不應以未知 POC、
bootloader 寫入或分割區操作取代版本確認。

### 已排除

本輪沒有執行任何 GhostLock POC，因此沒有「PS7331 POC 在 PS7330 失敗」或
「PS7331 POC 在 PS7330 成功」的結論；這兩種說法目前都沒有證據。

## 讀取失敗項目

下列命令 exit code 為 1，原始 stdout/stderr 與 exit code 已保存；不能把
失敗解讀成檔案不存在或安全功能關閉：

- `/proc/bootconfig`
- `/proc/cmdline`
- `/proc/partitions`
- `/system/etc/fosinit`
- `/vendor/etc/fosinit`

## 安全狀態

本輪沒有執行：root exploit、futex trigger、unknown ioctl、fastboot command、
bootloader unlock、sideload、remount、image/partition write 或刻意 crash。
