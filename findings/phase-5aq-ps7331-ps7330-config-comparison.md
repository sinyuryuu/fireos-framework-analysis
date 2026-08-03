# Phase 5AQ：PS7331／PS7330 kernel config comparison

日期：2026-08-04

## 結論先行

### 已證實

PS7331 `boot.img` 內嵌的 IKCONFIG 與目前裝置 PS7330 透過
`adb exec-out cat /proc/config.gz` 取得的 config，總共 3,705 個 config key
中只有 3 個不同：

| Key | PS7330 | PS7331 | 關聯 |
|---|---:|---:|---|
| `CONFIG_NETFILTER_NETLINK_ACCT` | not set | y | network accounting |
| `CONFIG_NF_CONNTRACK_TIMESTAMP` | not set | y | conntrack metadata |
| `CONFIG_MTK_WPA3_SUPPORT` | absent | y | Wi‑Fi feature |

GhostLock 相關的所有 focus key 都相同：

```text
CONFIG_ARM64=y
CONFIG_ARM64_4K_PAGES=y
CONFIG_ARM64_VA_BITS=39
CONFIG_THREAD_INFO_IN_TASK=y
CONFIG_FUTEX=y
CONFIG_RT_MUTEXES=y
CONFIG_PREEMPT=y
CONFIG_RANDOMIZE_BASE=y
CONFIG_KALLSYMS=y
# CONFIG_KALLSYMS_ALL is not set
# CONFIG_DEBUG_INFO is not set
CONFIG_IKCONFIG=y
CONFIG_SECURITY_SELINUX=y
CONFIG_SECCOMP=y
```

### 高可信推論

- PS7330 與 PS7331 使用相同的 futex/rtmutex build gate、ARM64 memory model
  與主要 hardening/config family。升級到 PS7331 不會因 config 差異而自動
  消除 GhostLock 的適用性。
- PS7331 build date 早於 2026 upstream 修補，且 config 沒有顯示任何 GhostLock
  專用 gate；因此舊 code path 仍然合理，但這仍不能證明 Amazon 沒有只改
  `rtmutex.c` 而保留相同 config。

### 待驗證

- PS7331 `rtmutex.c` 的 compiled basic blocks 是否使用 `current` 或 waiter task。
- Amazon 是否對 PS7331 做過未公開的 source/binary backport。
- 同 config 是否代表相同 compiler layout；目前 PS7331 kernel banner 顯示
  Clang 6.0.2，但沒有 DWARF/type data。

### 已排除

- 「PS7331 與 PS7330 的 GhostLock 差異來自 FUTEX/RT_MUTEX/ARM64 config」：
  逐鍵比較不支持此說法。
- 「CVE 在 2026 公開，所以 PS7331 一定未修補」：config comparison 不能
  證明 source code 沒有 backport。

### 因風險拒絕測試

- 不以相同 config 為理由執行 futex race、ROP/root payload、kernel memory
  write、BROM/DA、bootloader 或分割區寫入。

## 證據與雜湊

| 來源 | SHA-256 | 範圍 |
|---|---|---|
| PS7330 live config | `9fae0dc507c20842b68f8d0c26b8db8fe7d86c7459acb29cfa5b622e2666cbc9` | exact device |
| PS7331 embedded config | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | adjacent OTA |
| config comparison summary | see `artifacts/phase5/phase5aq-config-comparison-20260804-01/summary.json` | host-derived |

PS7330 raw capture 保留在：
`adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/`。

PS7331 IKCONFIG extraction 保留在：
`artifacts/phase5/ps7331-ikconfig-20260804-01/`。

## Reproduction

```sh
python3 tools/scripts/extract_embedded_kernel_config.py \
  --image artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image \
  --output artifacts/phase5/ps7331-ikconfig-20260804-01

bash tools/scripts/capture_phase5aq_device_config.sh \
  --serial G001LT0511550CFT \
  --test-id PHASE5AQ-DEVICE-CONFIG-20260804-02 \
  --output adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02

python3 tools/scripts/compare_kernel_configs.py \
  --ps7330 adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config \
  --ps7331 artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --output artifacts/phase5/phase5aq-config-comparison-20260804-01
```

三個命令都支援 `--dry-run`；裝置端命令只有讀取 identity 與
`/proc/config.gz`，不改變 package、setting、boot 或 partition。
