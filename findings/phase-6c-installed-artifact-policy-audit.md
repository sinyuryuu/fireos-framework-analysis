# Phase 6C：PS7331 installed-artifact policy surface audit

## 範圍與安全界線

本輪只讀取工作區已保存的 PS7331 7.3.3.1 artifacts，未連接 ADB、未掛載
image、未執行 ELF、未呼叫 futex、未讀寫 kernel memory，也沒有產生位址、
payload 或競態測試程式。這是對「已保存的安裝檔是否留下可辨識的 userspace
seccomp／zygote／futex policy 線索」的離線盤點，不是 runtime allow/deny 測試。

執行器：`tools/scripts/audit_phase6c_installed_artifacts.py`

結果目錄：
`artifacts/phase6c/phase6c-installed-artifact-policy-20260804-04/`

輸入根目錄：

- `firmware/extracted/PS7331/selected/`
- `firmware/extracted/PS7331/compiled-02/`
- `firmware/extracted/PS7331/compiled/`
- `firmware/extracted/PS7331/system/`
- `artifacts/amazon-services/`
- 已保存的 `app_process64`、`libc`、`linker64` native artifacts

## 原始結果（已證實，限定於輸入範圍）

| 項目 | 結果 |
|---|---:|
| 掃描檔案 | 53 |
| ZIP/APK/JAR/VDEX archive members | 14,075 |
| 路徑名稱含 policy 類標記 | 6 |
| `FUTEX_CMP_REQUEUE_PI` named marker | 0 |
| `FUTEX_WAIT_REQUEUE_PI` named marker | 0 |
| `FUTEX_LOCK_PI`／`UNLOCK_PI` named marker | 0 |
| `SECCOMP` marker | 2 |
| `SECCOMP_FILTER` marker | 0 |
| `zygote` marker | 11 |
| `app_process` marker | 7 |

完整 inventory、marker hit 與 SHA-256 位於結果目錄；原始輸出不得以摘要取代。

## 觀察解讀

### 已證實

1. 在本輪提供的 installed-artifact candidates 中，未發現明文
   `FUTEX_CMP_REQUEUE_PI` 或 `FUTEX_WAIT_REQUEUE_PI` caller marker。
2. `app_process64` 的 hit 是 zygote 啟動參數／類別名稱；它證明保存的檔案是
   zygote 相關 native surface，不證明它建立 requeue-PI waiter。
3. `linker64` 的 `SECCOMP`／`NO_NEW_PRIVS` 字串位於一般 linker/debuggerd
   診斷與 `SYS_SECCOMP` 相關訊息；本輪沒有發現可解析的 Android seccomp
   profile、filter rule 或 futex opcode allowlist。
4. `amazondevicepolicymanager_fosinit.xml`、`keypolicymanager_fosinit.xml`、
   `tabletkeypolicymanager_fosinit.xml` 和 `serendipity_allowlist.xml` 是
   Amazon service/callback／privilege 配置線索；在保存內容中沒有 requeue-PI
   或 seccomp rule。
5. `selected/system/framework/framework.jar` 和 `services.jar` 是極小的
   wrapper／placeholder artifacts；可執行的 framework service code 主要仍需
   由對應 ODEX/VDEX 及其他保存 artifact 解讀。本輪因此只作 marker inventory，
   不把空 wrapper 當成完整 framework source。

### 高可信推論

就目前保存且可掃描的 framework／APK／ODEX／VDEX／zygote/native 集合而言，
沒有直接可辨識的 Fire userspace requeue-PI caller，也沒有可從檔名或明文
marker 還原的 futex-specific seccomp policy。這使「普通 PI futex 能力」與
「GhostLock proxy path 已被 stock userspace 直接使用」之間的差距更明確。

### 待驗證

- `system.img`、`vendor.img`、`boot.img` 內尚未以唯讀 filesystem extractor
  展開的檔案內容。
- stripped／inline／numeric syscall、間接或生成式 caller。
- 實際 zygote／app sandbox 的 seccomp filter 是否允許特定 futex opcode。
- vendor daemon 或未保存的 Amazon process 是否可建立 paired waiter。

### 已排除／不支持

- `CONFIG_SECCOMP=y` 不能單獨推出某個 futex opcode 被允許或拒絕。
- `SECCOMP` 診斷字串不能當作已安裝 filter 規則。
- `zygote`、`app_process` 或普通 `PRCTL` marker 不能當作 proxy waiter 證據。
- 本輪 marker 為零不能推出 installed runtime 絕對不存在間接 caller。

### 因風險拒絕測試

未在實體 PS7331 執行 `FUTEX_CMP_REQUEUE_PI`／`FUTEX_WAIT_REQUEUE_PI`，也未
建立 paired waiter、競態、panic、memory operation 或 root payload。根據已
保存的 PS7331 source，該 syscall 不是無副作用的 capability probe：它可能先
準備 PI state，並在條件成立時進入 proxy／cleanup 路徑。

## 證據與雜湊

- `installed-artifact-policy.json`：
  `8dc5b673da4a12ae3223dd298e1f95ff60b3e87abdaf3a6b9596b45cb24ecc93`
- `artifact-inventory.csv`：
  `28c588e3982674e17b109cbb0f884e812909fe84503ed07058cffe6993c5cc47`
- `marker-hits.csv`：
  `923f59e2e9c48ae5d6ed3bcff21fdc452f01c3744a44100287e8b2d157c3ce89`
- `linker64`：
  `124745b0cac2fa1511cd903a3982108109d8c8f38e77c63df3e97b026e6ee21b`
- `app_process64`：
  `c075e6bbef31b2ae03ef6336b8d605c6f430e49bf25444c44aea0563647ec01e`
- `ota.prop`：
  `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded`

## 可重現指令

```sh
python3 tools/scripts/audit_phase6c_installed_artifacts.py --dry-run \
  --input-root firmware/extracted/PS7331/selected \
  --input-root firmware/extracted/PS7331/compiled-02 \
  --input-root firmware/extracted/PS7331/compiled \
  --input-root firmware/extracted/PS7331/system \
  --input-root artifacts/amazon-services \
  --input-root artifacts/phase5/phase5cq-fire-native-20260804-01/files \
  --input-root artifacts/phase5/phase5cr-fire-native-20260804-02/files \
  --output artifacts/phase6c/phase6c-installed-artifact-policy-YYYYMMDD-NN
```

移除 `--dry-run` 可建立新的結果目錄；程式拒絕覆寫既有輸出。

## 下一個安全研究目標

若要縮小 policy coverage gap，下一步應是取得或建立**唯讀**的 image
filesystem inventory（不 remount、不修改原始 image），再針對
`/system/etc/seccomp`、zygote policy、vendor policy 與 sandbox 配置做同樣
的 marker／hash 盤點。這仍不能替代 runtime 測試，但比在實體裝置觸發
requeue-PI 更能增加證據量且不改變設備狀態。
