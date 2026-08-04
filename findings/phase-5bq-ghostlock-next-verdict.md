# Phase 5BQ：GhostLock 優先研究與 MTK 公開路線更新

日期：2026-08-04
目標：在不改變 Fire HD 10 裝置狀態的前提下，更新 GhostLock、PS7331
與公開 MTK route 的可驗證邊界。

## 結論先行

### 已證實

1. 新的序號限定唯讀 postcheck 顯示設備仍為：

   ```text
   Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
   security_patch=2024-02-01
   HOME=com.amazon.firelauncher/.Launcher
   ADB state=device
   ```

   原始輸出與 SHA-256 位於
   `adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01/`。

2. `KoCleo/mtk-easy-su` 公開 HEAD 為
   `8c6871ac7c15b8e98a47e25c35ab93b87e260475`。其 README 將工具描述為
   Magisk／`mtk-su` 的舊式 bootless-root wrapper，提醒 2020 年 3 月後的
   firmware 可能阻擋方法；公開測試清單沒有 `KFTRWI`、`trona` 或
   `MT8183`。[公開 README](https://raw.githubusercontent.com/KoCleo/mtk-easy-su/master/README.md)

3. `BaronKiko/LauncherHijack` 公開 HEAD 為
   `f79aee3ddd10c053d6d7c55d6f2fc29436001537`。既有 source review 與本機
   controlled run 已將它定位為 Accessibility／foreground redirect 參考，
   不是 formal HOME resolver replacement；本輪沒有安裝未知 APK，也沒有
   重跑已完成的 0/30 route。

4. GhostLock 是 Linux `rtmutex`／futex PI 路徑，修補語意是把
   `remove_waiter()` 的相關 cleanup 與 priority-chain task 從 `current`
   改為 `waiter->task`。NVD 明確描述了 dangling `pi_blocked_on` 與錯誤
   priority-chain task 的問題。[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)

5. Exact PS7330 build-selected `mt8183/4.4` source、PS7331 corresponding
   source，以及已檢查的 PS7331 Image 仍是 pre-fix semantic evidence；這不
   是 exact PS7330 signed binary 的 exploitability proof。

### 高可信推論

- 目前沒有新的、可歸因於 `KFTRWI/trona/MT8183/PS7330` 的 public MTK
  temporary-root implementation。既有 `mtk-su` failure 已封存，且 public
  target list 沒有補足 exact target profile；不重跑同一 payload。
- **不應為 GhostLock 單獨升級 PS7331。** PS7331 可作一般安全更新的獨立
  A/B 候選，但目前 source／inspected Image 沒有證明它包含
  `waiter->task` 修補；完整 OTA 也會更新多個 boot-chain／firmware 成員。
- 「拿 7.3.3.1 `boot.img` 單獨寫入」不是完整 OTA 等價操作，不能作為安全
  或可回復的測試方案。

### 待驗證

- 已安裝 PS7330 signed boot block 的實際 `remove_waiter()` machine code；
  Android shell 讀取被拒絕。
- PS7330 release CI 是否在公開 source/build script 之外套用 backport。
- PS7331 的非 GhostLock 一般安全修補完整差異。

### 已排除／不採用

- 將 `mtk-easy-su` 的通用 MTK 支援說明當成 trona/PS7330 相容證明。
- 將其他 MTK SoC、其他 kernel version 或其他 Android 版本的 PoC 直接套用。
- 將 Android boot header offset、PS7331 offset 或 source layout 當作 runtime
  kernel offset。
- 將 LauncherHijack 的 default-launcher corruption route 當成正式 HOME
  解法；它可能使 user state 無可用 Launcher，且不是本輪所需的 GhostLock
  證據。

### 因風險拒絕測試

即使研究者表示接受變磚，本輪仍不執行會取得未授權 kernel／root 能力或寫入
boot chain 的操作，包括：

- GhostLock futex race、kernel memory read/write、native root payload；
- 未知 ioctl、BROM/DA handshake、preloader/LK patch；
- fastboot unlock/flash、OTA sideload、standalone boot write；
- remount、system/vendor/product/boot/userdata 或其他 partition write；
- LauncherHijack 的破壞 default-launcher 路徑。

這些操作在目前缺少 exact PS7330 signed target 與可靠 recovery set 的情況下，
不能產生可重現、可歸因的科學結果。

## 證據矩陣

| Evidence ID | 來源 | 觀察 | 判定 |
|---|---|---|---|
| `P5BQ-DEVICE-001` | `adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01/` | PS7330 fingerprint、patch、ADB device、HOME Fire Launcher | 已證實，runtime scope |
| `P5BQ-MTK-001` | `artifacts/phase5/phase5bq-public-route-review-20260804-01/source-heads.tsv` | mtk-easy-su HEAD 與 README target scope | 已證實，public-source scope |
| `P5BQ-HIJACK-001` | 同上；既有 `findings/phase-5ab-*` | LauncherHijack pinned source；無新 APK 安裝 | 已證實，source scope |
| `P5BQ-GHOSTLOCK-001` | NVD 與既有 source/image artifacts | fix changes current-task cleanup to waiter-task | 已證實，upstream/inspected scope |
| `P5BQ-PS7330-001` | `artifacts/phase5/ps7330-full-source-members-20260804-01/` | exact mt8183 source remains pre-fix | 已證實，source scope |
| `P5BQ-PS7331-001` | `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/` | inspected PS7331 Image remains pre-fix-consistent | 已證實，inspected-image scope |
| `P5BQ-OTA-001` | `findings/phase-5bd-ota-and-redirect-followup.md` | PS7331 full OTA writes more than boot | 已證實，OTA metadata scope |
| `P5BQ-SAFETY-001` | `artifacts/phase5/phase5bq-public-route-review-20260804-01/commands.txt` | no exploit/bootchain/partition operation | 已證實 |

## 下一個最小且有研究價值的步驟

1. 若能從授權來源取得與已安裝 `PS7330.4104N` 完全匹配的 signed
   `boot.img`／`Image`／`vmlinux`，只做離線 function-semantic comparison，
   不執行 kernel code。
2. 若無法取得，將 GhostLock 判定維持為「source-level applicability
   candidate；live exploitability 未確認」，不要用不匹配的 PS7331 image、
   generic MTK loader 或舊 mtk-su payload 填補證據缺口。

## 重現

```sh
git ls-remote https://github.com/KoCleo/mtk-easy-su.git HEAD
git ls-remote https://github.com/BaronKiko/LauncherHijack.git HEAD

bash tools/scripts/capture_phase5ba_device_postcheck.sh --dry-run \
  --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01

bash tools/scripts/capture_phase5ba_device_postcheck.sh \
  --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01
```

上述 postcheck script 需要明確 serial、拒絕覆寫輸出，且只執行
`get-state`、`getprop`、`cmd package resolve-activity`、`pm path` 與
`dumpsys` 類唯讀命令。
