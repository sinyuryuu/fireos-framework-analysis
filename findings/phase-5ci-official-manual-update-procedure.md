# Phase 5CI：PS7331 官方手動更新流程與本地包核對

日期：2026-08-04

範圍：官方文件、主機端 OTA metadata 與封存的 PS7331 檔案；未啟動更新。

## 官方說明

Amazon 的官方裝置頁把 Fire HD 10（11th Generation）列為 Fire OS 7.3.3.1，
並提供 Software Update 下載入口：

- [Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE)
- [Install Your Fire Tablet Software Update Manually](https://digprjsurvey.amazon.co.uk/csad/help/node/GVKSH9UN8NKKU4PL)

官方手動流程是：

1. 在桌面電腦下載與裝置型號相符的更新檔。
2. 用 USB 連接 Fire tablet；在平板下拉 USB charging notification，選擇
   **Transfer files**。
3. 在電腦開啟 Fire 裝置磁碟，將整個更新檔放入 **Internal storage**。
4. 完成傳輸後拔除 USB。
5. 平板開啟 **Settings → Device Options → System Updates → Update**。
6. 系統會重啟，畫面顯示 **Installing system update**。

這是 Amazon 文件描述的裝置端 OTA 安裝流程；文件沒有要求使用 fastboot、
bootloader unlock、單獨寫入 `boot.img` 或手動選擇分割區。

## 本地檔案核對

| Field | Value | Evidence |
|---|---|---|
| Local OTA | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | local file |
| Size | `1,301,005,356` bytes | `artifacts/phase5/ps7331-official-update-source-20260804-01/source-map.tsv` |
| SHA-256 | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | `shasum -a 256` and source map |
| Official source | Amazon update page → Amazon S3 | `source-map.tsv` |
| OTA type | `BLOCK` | `META-INF/com/android/metadata` |
| Target device | `trona` | `pre-device=trona`, `ota.prop` |
| Target build | `PS7331.4463N/0031575863040` | OTA metadata |
| Security patch | `2024-08-01` | `post-security-patch-level` |
| Package type | `full` | `ota.prop` |
| Archive integrity | ZIP test passed | `unzip -t` |
| OTA certificate | subject/issuer `Amazon-1`, `CN=Amazon` | `META-INF/com/android/otacert` |

The local file therefore matches the official PS7331 update metadata and the
published Fire HD 10 (11th Generation) target. This confirms provenance and
format, not that the update has been installed on the connected tablet.

## Important scope and risk

The package contains `system`, `vendor`, `boot`, `preloader`, `lk`, TEE, SPMFW,
SSPM and camera VPU members in its updater inputs. It is a full system update,
not a reversible boot-image experiment. The connected tablet remains:

```text
PS7330.4104N
Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
```

No file was pushed to the tablet, no Settings update was started, no reboot was
requested, and no partition was written. The official procedure may still be
non-reversible from a research perspective because rollback and recovery
behavior are not guaranteed by the public instructions.

## Post-update verification plan

If the researcher elects to apply the official update manually, the first
post-boot action should be read-only identity capture, before any kernel or
package experiment:

```sh
adb shell getprop ro.build.fingerprint
adb shell getprop ro.build.version.name
adb shell getprop ro.build.version.incremental
adb shell getprop ro.build.version.security_patch
adb shell getprop ro.boot.verifiedbootstate
adb shell getenforce
```

Expected PS7331 identity is `PS7331.4463N/0031575863040` with security patch
`2024-08-01`. A mismatch must be recorded as `VERSION_MISMATCH`; it must not be
used as evidence for PS7331 runtime behavior.

## Classification

- **已證實：** Amazon publishes Fire OS 7.3.3.1 for this model/generation and
  documents MTP copy followed by Settings → System Updates → Update.
- **已證實：** the local `.bin` is a valid, integrity-checked, Amazon-signed
  metadata-compatible PS7331 full OTA artifact.
- **高可信推論：** this is the correct official update path for the target
  model, subject to the device accepting the package.
- **待驗證：** whether the connected PS7330 device accepts the package and the
  exact post-update runtime behavior.
- **因風險拒絕測試：** no sideload, Settings update, fastboot flash, boot image
  write, preloader/LK write or bootloader operation was performed in this
  phase.
