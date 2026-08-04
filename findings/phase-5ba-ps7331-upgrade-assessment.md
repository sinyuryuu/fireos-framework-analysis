# Phase 5BA：PS7331 source／boot image 與升級評估

日期：2026-08-04
裝置：Amazon Fire HD 10 2021，`KFTRWI`／`trona`／MT8183
目前安裝版本：Fire OS 7.3.3.0，`PS7330.4104N`

## 結論先行

### 已證實

1. 目前裝置仍運行：

   ```text
   Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
   ```

   最新唯讀 post-check 的 HOME resolver 仍為
   `com.amazon.firelauncher/.Launcher`，priority 50；本輪沒有更新、重開機、
   package、setting 或 partition mutation。

2. 本地保存的官方 PS7331 OTA 是 `trona`／Android 9／API 28 的完整 OTA，
   metadata 為：

   ```text
   post-build=Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys
   post-build-incremental=0031575863172
   post-security-patch-level=2024-08-01
   pre-device=trona
   ```

   它與目前裝置的 `PS7330.4104N` 不同，屬於相鄰版本而不是目前已安裝映像。

3. PS7331 `boot.img` 的 SHA-256 是
   `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`；離線
   解壓出的 ARM64 `Image` SHA-256 是
   `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`。

4. 對 PS7331 signed kernel Image 的離線 kallsyms／反組譯檢查，在
   `remove_waiter` 看到從 `SP_EL0` 取得 current task 並透過該 current-task
   指標清除欄位；同一 Image 的 `rt_mutex_start_proxy_lock` 仍有
   `remove_waiter` proxy error path。這是 GhostLock root-cause 所需的舊
   `current` cleanup pattern，而不是 upstream waiter-task 修補的語意。

5. 7.3.3.1 外層 source bundle 的 build config 明確選擇
   `kernel/mediatek/mt8183/4.4`、`trona_defconfig`、`arm64`，並以 Clang 6.0.2
   作為建置建議。這也解釋了為何外層 tar index 不直接列出
   `kernel/mediatek/.../rtmutex.c`：實際 platform source 是 nested tar input。

### 高可信推論

- 若升級目標是修補 GhostLock／CVE-2026-43499，PS7331 **目前沒有顯示值得升級
  的修補理由**：PS7331 的 signed kernel 已直接呈現舊 pattern，而 PS7330 的
  exact 7.3.3.0 source 也與 v4.4.146 old source normalized-identical。
- PS7331 與 PS7330 的 3,705 個 kernel config key 只有三項不同：
  `CONFIG_NETFILTER_NETLINK_ACCT`、`CONFIG_NF_CONNTRACK_TIMESTAMP`、
  `CONFIG_MTK_WPA3_SUPPORT`。`FUTEX`、`RT_MUTEXES`、`PREEMPT`、ARM64 4K／VA39
  與主要 hardening focus keys 沒有差異。
- 因此，**不建議為了 GhostLock 單獨升級到 PS7331**。它可能提供其他 Fire OS
  修補或功能，但現有證據不支持它消除這條 futex／rtmutex 根因。

### 待驗證

- 7.3.3.1 source archive 的外層 tar index 顯示 source layout 由
  `build_kernel.sh`／`build_kernel_config.sh` 及 nested platform tar packaging
  組成；`rtmutex.c` 與 `futex.c` 的 exact source diff 尚待完成。不能把 bounded
  tail sample 當成完整 archive source。
- 目前裝置 PS7330 的 signed boot block 無法由 shell 讀出，因此沒有 PS7330
  compiled `remove_waiter` 的直接 binary confirmation。
- PS7331 可能有其他非 `remove_waiter` 的 Amazon backport；目前沒有看到能改變
  GhostLock 根因判定的證據。

### 已排除

- 「有 PS7331 `boot.img` 就能直接算出目前 PS7330 的可用 kernel offset」：
  boot header／Image address 不等於 runtime KASLR、physmap、type layout 或
  signed PS7330 binary layout。
- 「CVE 在 2026 年公開，所以 PS7331 必定未修補」：PS7331 現在有 compiled
  old-pattern evidence，但不能用公開日期作為證據；同樣也不能把它推廣成
  PS7330 signed-binary proof。
- 「PS7331 source/config 與 PS7330 相近，所以可以把 PS7331 boot、LK、preloader
  單獨寫入 PS7330」：版本、簽章、rollback 與 boot-chain 相容性均未被證明。

### 因風險拒絕測試

- 沒有把 `boot.img`、`preloader.img`、`lk.img` 或其他 OTA image 寫入裝置。
- 沒有執行 fastboot flash／unlock、OTA sideload、BROM／DA、分割區寫入、
  futex race、kernel memory write 或 root payload。
- 沒有停用 Fire Launcher、清除其資料或改變目前 HOME 狀態。

## 版本與 artifact 對照

| 項目 | 目前設備 PS7330 | 本地 PS7331 reference |
|---|---|---|
| fingerprint | `PS7330.4104N/0030099376128` | `PS7331.4463N/0031575863040` |
| security patch | 2024-02-01 | 2024-08-01 |
| product／SoC | `trona`／MT8183 | `trona`／MT8183 |
| kernel | 4.4.146+ | 4.4.146+ |
| boot artifact | exact installed boot 不可由 shell pull | `boot.img` SHA recorded |
| source | exact 7.3.3.0 `rtmutex.c` old source | 7.3.3.1 archive URL found; full member comparison pending |

## 為何不能把 boot.img 當作升級操作輸入

`boot.img` 是 signed OTA 的一個分割區 image。即使它來自同一 `trona` 產品，
仍可能受以下條件約束：

- anti-rollback／rollback index；
- AVB／verity／簽章與 OTA transaction；
- boot、vendor、system、preloader、LK 的版本配套；
- userdata migration 與更新後的 package／設定狀態；
- Amazon 更新器對 model、region、build 與 battery 狀態的檢查。

所以若日後真的要升級，唯一合理的方向是使用裝置可接受的官方完整更新流程，
而不是把抽出的 `boot.img` 單獨刷入。那仍可能無法降級，並且需要先保存可讀取的
狀態與接受資料／恢復風險；本報告沒有執行該操作。

## 升級決策

### 建議：暫不升級（針對 GhostLock 研究）

目前證據的最小解釋是：

```text
PS7330 exact source: old rtmutex semantics
        +
PS7331 signed Image: old remove_waiter compiled pattern
        +
PS7330/PS7331 focus config: same
        ↓
PS7331 is not a demonstrated GhostLock remediation
```

維持 PS7330 的研究價值在於保留目前已封存的 exact device baseline，避免把
「版本變更」與「漏洞／權限行為變更」混在一起。若目的改成測試 Amazon 的安全
更新差異，PS7331 可以另立一個版本 A/B 實驗，但應先完成 exact source member
比較，並把更新視為可能不可逆的正式系統變更。

### 若日後要考慮官方升級，必要前置條件

1. 封存現有 PS7330 fingerprint、security state、HOME resolver、package／
   settings、OTA metadata 與所有研究產物。
2. 確認更新包仍是 Amazon release-signed、`pre-device=trona`，且由官方更新
   流程針對本機提供；不要以手上的 `boot.img` 代替完整 OTA。
3. 事先接受「官方更新通常不是可任意 downgrade 的 reversible mutation」；
   沒有 factory reset／官方 recovery 路徑保證時，不把它標記為可完整還原。
4. 更新後只先採集 fingerprint、kernel banner、config、HOME resolver 與
   package state；不要立即執行 root／kernel exploit 測試。
5. 只有在 7.3.3.1 exact source、signed Image 與更新後實機三者對齊後，才把
   PS7331 結論從 reference 提升為 installed-build evidence。

## 可重現 host-only 命令

```sh
python3 tools/scripts/compare_phase5_ps7330_ps7331_kernel.py --dry-run \
  --ps7330-config adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config \
  --ps7331-config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --ps7331-boot firmware/extracted/PS7331/boot.img \
  --output artifacts/phase5/phase5ba-ps7331-upgrade-comparison-20260804-01
```

完整 source archive：
[`Fire_HD10-7.3.3.1-20250617.tar.bz2`](https://fireos-tablet-src.s3.amazonaws.com/k2k5jkgocvaww3SgOjJMkJrykI/Fire_HD10-7.3.3.1-20250617.tar.bz2)

既有 compiled review：[`phase-5ar-ps7331-compiled-rtmutex-review.md`](phase-5ar-ps7331-compiled-rtmutex-review.md)
既有 config comparison：[`phase-5aq-ps7331-ps7330-config-comparison.md`](phase-5aq-ps7331-ps7330-config-comparison.md)
既有 compatibility matrix：[`phase-5az-ghostlock-mtk-compatibility.md`](phase-5az-ghostlock-mtk-compatibility.md)

## 最終狀態

本報告完成時，設備仍是 PS7330，ADB 可連線，HOME 仍解析到 Fire Launcher；
唯讀 post-check 原始輸出保存在
`adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/`，沒有執行升級或其他
裝置狀態變更。
