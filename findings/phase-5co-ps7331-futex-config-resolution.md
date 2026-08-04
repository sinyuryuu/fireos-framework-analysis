# Phase 5CO：PS7331 futex feature-gate source resolution

日期：2026-08-04
裝置：Amazon Fire HD 10／KFTRWI／`trona`／MT8183
韌體：Fire OS 7.3.3.1／`PS7331.4463N`
安全範圍：官方 source archive 與已保存 kernel config 的主機端分析；沒有觸發 futex PI、競速器、未知 ioctl、kernel memory access 或 root payload。

## Executive result

本輪補足 Phase 5CN 尚未取得的 ARM64 futex header 與 Kconfig 片段，解決了
「PS7331 的 PI feature gate 是否只是一段未確認的 source 分支」這個範圍問題。

| 問題 | 判定 | 證據 |
|---|---|---|
| PS7331 source 定義 `HAVE_FUTEX_CMPXCHG` gate | 已證實（source scope） | `P5CO-SRC-001`, `P5CO-SRC-002` |
| MT8183 ARM64 source 有 futex atomic cmpxchg 實作 | 已證實（source scope） | `P5CO-SRC-003` |
| MT8183 ARM64 platform block 直接 `select HAVE_FUTEX_CMPXCHG` | 未找到；不是「final .config 已證實 unset」 | `P5CO-SEARCH-001` |
| PS7331 最終 kernel 啟用 FUTEX／RT_MUTEX | 已證實 | `P5CO-BUILD-001`, `P5CN-RUNTIME-001` |
| PS7331 runtime `futex_cmpxchg_enabled == 1` | 高可信推論，未直接觀察 | `P5CO-SRC-002`, `P5CO-SRC-003`, `P5CO-BUILD-001` |
| `FUTEX_CMP_REQUEUE_PI` 可達 proxy-lock source path | 已證實（source scope）；runtime invocation 未測 | `P5CN-SRC-001`, `P5CN-SRC-002` |
| 實際出現 `waiter->task != current` | 尚未觀察 | `P5CO-D1-001` |
| mismatch 後留下可利用的持久 kernel state | 尚未證明 | `P5CO-D2-001` |

核心結論：本輪只把「feature gate／架構支援」的 source-to-image 對應提高到
高可信；沒有把它誤寫成 GhostLock 已在 PS7331 上動態觸發。真正的分水嶺仍是
同一次受控 kernel execution 中觀察到 `waiter->task != current`。

## 1. 輸入與方法

使用的官方 source archive：

```text
firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2
SHA-256: 02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea
```

`tools/scripts/extract_phase5cn_futex_arch_members.py` 以固定 allow-list 從
nested `platform.tar` 擷取 Kconfig、ARM64 futex header 與 Linux futex header；
`tools/scripts/search_phase5cn_source_literals.py` 以 streaming tar reader 搜尋
`HAVE_FUTEX_CMPXCHG` 與 `CONFIG_HAVE_FUTEX_CMPXCHG`。兩個腳本都是 host-only，
拒絕覆寫既有輸出，不呼叫 ADB／fastboot，也不執行 source。

完整 extraction/search metadata 保留在未納入本次小型 public commit 的 raw evidence
目錄；公開報告只引用檔案 hash、行號與可重跑腳本。

## 2. Source resolution

### 2.1 Gate 的定義

官方 source 的 `init/Kconfig` 定義：

```text
config FUTEX
    default y
    select RT_MUTEXES

config HAVE_FUTEX_CMPXCHG
    bool
    depends on FUTEX
```

位置：`kernel/mediatek/4.4/init/Kconfig:1570-1585`，檔案 SHA-256：
`80b895f9bbad97978823720c357f89e8835d6c0e48336c906c7d8693de3b2957`。

`include/linux/futex.h:61-65` 依據這個 symbol 選擇兩種實作：

```c
#ifdef CONFIG_HAVE_FUTEX_CMPXCHG
#define futex_cmpxchg_enabled 1
#else
extern int futex_cmpxchg_enabled;
#endif
```

這與 build-selected `kernel/futex.c:176-178` 的 runtime variable 宣告相接。

### 2.2 ARM64 實作

MT8183 ARM64 futex header 提供：

```text
kernel/mediatek/mt8183/4.4/arch/arm64/include/asm/futex.h:92-125
```

檔案 SHA-256：`0aa4289efa3f2f045329969616c74430a4e088b16366f665ec1a0ced09ff3fdc`。

`futex_atomic_cmpxchg_inatomic()` 在 line 99-100 先對 user address 執行
`access_ok()`；無效位址回傳 `-EFAULT`。有效路徑使用 ARM64 `ldxr`／`stlxr`
compare-and-exchange，並在 line 116-119 使用 exception table 處理 fault。

因此，若 final build 沒有把 `CONFIG_HAVE_FUTEX_CMPXCHG` 編成固定常數，
`futex_detect_cmpxchg()` 的 NULL probe 有一條合理的 ARM64 source path 可以
得到 `-EFAULT`。

### 2.3 MT8183 的 Kconfig 選取結果

MT8183 ARM64 platform block 位於：

```text
kernel/mediatek/mt8183/4.4/arch/arm64/Kconfig.platforms:255-294
```

檔案 SHA-256：`89ab399110832ccafe6e5905f02e7df88959f94a2f023406d40f90773cf1a93d`。

在 `config MACH_MT8183` 的選取項目中沒有找到
`select HAVE_FUTEX_CMPXCHG`。literal search 找到的 MediaTek `select` 位於
`kernel/mediatek/4.4/arch/arm/mach-mediatek/Kconfig:244` 的 `MACH_MT8167`
block；它不能被歸因為 MT8183 ARM64 的選取。

這是一項重要的防誤判：

- 「MT8183 header 實作存在」不等於「Kconfig symbol 已固定為 y」；
- 「MT8183 platform block 沒有直接 select」不等於已取得完整 Kconfig 展開後
  的 final `.config` 證明；
- 嵌入式 config 沒有 `CONFIG_HAVE_FUTEX_CMPXCHG` 行，只能作為強證據，不能
  單獨當作所有未輸出 symbol 的負面證據。

## 3. 與 futex／rtmutex source 的連接

build-selected `futex.c`（SHA-256
`ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`）顯示：

1. `futex.c:3310-3327` 只有在未定義 `CONFIG_HAVE_FUTEX_CMPXCHG` 時執行
   NULL probe；回傳 `-EFAULT` 才把 `futex_cmpxchg_enabled` 設為 1。
2. `futex.c:3330-3348` 的 `futex_init()` 呼叫該 detection。
3. `futex.c:3233-3241` 在 PI command dispatch 前檢查 gate，false 時回傳
   `-ENOSYS`。
4. `futex.c:3264-3269` 將 `FUTEX_CMP_REQUEUE_PI` 導向
   `futex_requeue(..., requeue_pi=1)`。

build-selected `rtmutex.c`（SHA-256
`6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`）顯示：

1. `rt_mutex_start_proxy_lock():1656-1671` 接受明確的 `task`。
2. `task_blocks_on_rt_mutex():975-988` 將該 task 寫入 `waiter->task` 與
   `task->pi_blocked_on`。
3. `remove_waiter():1079-1090` 卻鎖定 `current->pi_lock` 並清除
   `current->pi_blocked_on`；`1125-1126` 也將 `current` 傳入 chain adjustment。
4. `rt_mutex_start_proxy_lock():1683-1684` 對 non-zero return 呼叫
   `remove_waiter()`，但 `task_blocks_on_rt_mutex()` 在 `owner == task` 的
   early return（`972-973`）會在設定 `waiter->task` 前離開。

這些是 source-level identity separation 與 cleanup control-flow 證據；它們仍
不等於 runtime mismatch。

## 4. Build config 與 runtime boundary

官方 PS7331 boot image 的 embedded IKCONFIG：

```text
artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config
SHA-256: eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04
```

保存的值包括：

```text
CONFIG_FUTEX=y
CONFIG_RT_MUTEXES=y
CONFIG_PREEMPT=y
CONFIG_PREEMPT_COUNT=y
CONFIG_ARM64_4K_PAGES=y
CONFIG_ARM64_VA_BITS=39
CONFIG_RANDOMIZE_BASE=y
CONFIG_KALLSYMS=y
# CONFIG_KALLSYMS_ALL is not set
# CONFIG_DEBUG_RT_MUTEXES is not set
```

裝置端 `PS7331-CONFIG-GATES-20260804-03` 也回報 `CONFIG_FUTEX=y` 與
`CONFIG_RT_MUTEXES=y`，但沒有提供 `futex_cmpxchg_enabled` 的 runtime 值。

**高可信推論：** 結合「MT8183 ARM64 atomic cmpxchg 實作存在」、「MT8183 ARM64
platform block 未直接 select 該 symbol」、「embedded config 未輸出該 symbol」
與 `futex_detect_cmpxchg()` 的 source semantics，PS7331 很可能使用 runtime
detection，並在 init 時把 `futex_cmpxchg_enabled` 設為 1。

**尚未直接證實：** 沒有從 stock device 讀出該 global variable，也沒有執行
任何 PI opcode 作為探針。即使這項推論成立，也只證明 PI path 的 feature gate
可能開放，不會證明 proxy waiter 已形成，更不會證明 identity mismatch 或 root。

## 5. GhostLock 分水嶺判定

### 已證實

- source 中存在 explicit proxy task → `waiter->task` 的路徑；
-同一 source 的 `remove_waiter()` 使用 `current` cleanup；
- ARM64 cmpxchg implementation 與 NULL fault semantics 存在；
- PS7331 image/runtime 啟用 futex／rtmutex 基礎功能。

### 高可信推論

- PS7331 的 `futex_cmpxchg_enabled` 很可能在 futex init 後為 1，因此
  `FUTEX_CMP_REQUEUE_PI` 不會僅因 feature gate 被 `-ENOSYS` 擋住。

### 尚未觀察／尚未證明

- 同一次 execution 中 `waiter->task != current`；
- cleanup 後 `waiter->task->pi_blocked_on` 殘留；
- rtmutex waiter tree、PI chain 或 owner state 出現可持久不一致；
- 後續正常 kernel path 消費該狀態；
- 任意 kernel crash、memory-safety primitive、control flow 或 privilege escalation。

### 安全拒絕

本輪沒有在 stock tablet 上執行 `FUTEX_CMP_REQUEUE_PI`、race trigger、kernel
instrumentation、debug kernel、未知 ioctl、kernel memory read/write 或 exploit。
要取得 D1，下一個合理環境是隔離的 instrumented research kernel／emulator，
而不是在日常裝置上把 race 轉成 crash 或 root。

## 6. Reproduction

主機端唯讀重跑：

```sh
python3 tools/scripts/extract_phase5cn_futex_arch_members.py --dry-run \
  --archive firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --output artifacts/phase5/REPRODUCE-ARCH

python3 tools/scripts/search_phase5cn_source_literals.py --dry-run \
  --archive firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --output artifacts/phase5/REPRODUCE-LITERALS
```

實際 extraction/search 也只應指定新的、尚不存在的 output directory；兩個腳本
會拒絕覆寫既有輸出。不要把任何輸出路徑指向裝置或 source archive 本身。

## 7. Bottom line

本輪解決了 Phase 5CN 的 source completeness gap，但沒有跨過 D1。若研究問題是
「PS7331 是否有足夠的 source/config 條件讓 GhostLock 值得進入動態驗證」，答案是
**高可信支持**；若問題是「GhostLock 是否已在此平板形成可重現 identity mismatch
或 root」，答案仍是**沒有證據**。

一個真正的 `waiter->task != current` observation 會是動態驗證的分水嶺；在取得
該 observation 前，不應把 feature-gate inference、source marker 或重啟結果
升格為 live exploit 結論。
