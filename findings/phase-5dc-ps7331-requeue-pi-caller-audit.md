# Phase 5DC — PS7331 requeue-PI caller audit

日期：2026-08-04

範圍：官方 PS7331 source extraction、exact build-selected MT8183 kernel tree、
已保存的 Fire libc/Amazon native scan outputs。方法是主機端、只讀文字與
既有 scan artifact 分類；沒有編譯或執行 source/native object，沒有接觸
裝置，也沒有呼叫 futex、ioctl、kernel memory 或 root payload。

## 結論

本輪將先前的大範圍搜尋轉成可重現的「caller role」分類。搜尋到 231 個
matching rows、34 個 source files，但它們全部落在：

- `kernel_implementation`：60 rows；
- `selftest`：135 rows；
- `uapi_or_documentation`：36 rows。

在這兩個 PS7331 source roots 中沒有分類為 Fire framework/app userspace
caller 的 row；在既有 Fire libc 與 Amazon native artifact scan 中也沒有
named requeue-PI row。這是一個 bounded negative observation，不是「Fire
runtime 不可能呼叫」的證明。

最重要的區分是：

```text
PS7331 kernel implementation
  !=  installed userspace caller

PS7331 futex selftest wrapper
  !=  stock Fire runtime execution

ordinary ART compare-requeue marker
  !=  FUTEX_*_REQUEUE_PI proxy execution
```

因此目前仍然是：kernel/source path 已證實；Fire userspace caller、stock
runtime proxy execution、identity mismatch、cleanup residue、後續 consumer、
memory effect 與 privilege transition 尚未取得證據。

## Evidence

完整機器輸出與 hash：

`artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-05/`

主要檔案：

- `source-hits.csv`：231 rows，逐行列出 pattern、source role 與 excerpt；
- `native-scan-hits.csv`：0 rows；
- `summary.json`：scope、分類計數與安全旗標；
- `sha256sums.txt`：輸出 hash。

公開摘要表：
`output/tables/phase5dc-requeue-pi-callers.csv`。

## 1. Exact MT8183 kernel source

build recipe 已在 Phase 5DA 確認選取
`kernel/mediatek/mt8183/4.4` 與 `trona_defconfig`。在這個 exact source
path 中：

- `kernel/futex.c:1926` 記錄 requeue-PI pairing invariant；
- `kernel/futex.c:1959-1965` 在 `futex_requeue()` 呼叫
  `rt_mutex_start_proxy_lock()`，傳入 `this->rt_waiter` 與 `this->task`；
- `kernel/futex.c:3233-3269` 將 `FUTEX_WAIT_REQUEUE_PI`／
  `FUTEX_CMP_REQUEUE_PI` dispatch 到 wait/requeue path；
- `kernel/locking/rtmutex.c:1654-1684` 是 explicit-task proxy API 與
  nonzero-return cleanup branch。

這些是 **Confirmed, source scope**。它們回答「exact kernel source 是否
保留目標路徑」，不回答「哪個 Fire userspace caller 觸發它」。

## 2. Selftest-only direct wrappers

`platform/kernel/mediatek/4.4/tools/testing/selftests/futex/include/futextest.h`
提供：

- lines 189-193：`futex_wait_requeue_pi()` wrapper；
- lines 204-208：`futex_cmp_requeue_pi()` wrapper。

functional selftest files 也有 direct call sites，且 Makefile 列出這些
測試。然而它們位於 kernel selftest tree，不是已 pull 的 Fire app、framework
service 或 system daemon。這些 rows 標示為 **Confirmed, selftest scope**；
本輪沒有 build、push 或 execute selftest。

## 3. Documentation is not a runtime caller

`Documentation/futex-requeue-pi.txt` 有 requeue-PI 的示例文字與 wrapper
名稱，包含 generic `futex()` call 的說明。它解釋 API 的設計用途，但不是
裝置上已安裝的 userspace binary。報告與 CSV 將其單獨標成 documentation，
避免把示例誤當作 Fire caller。

## 4. Native artifact negative observation

本輪重新掃描既有：

- `artifacts/phase5/phase5cr-fire-native-20260804-02/`；
- `artifacts/phase5/phase5cs-fire-amazon-native-20260804-01/`。

結果是 0 個 named `FUTEX_*_REQUEUE_PI`／`futex_*requeue_pi` rows。這和
Phase 5CR 的 libc 結果一致：普通 futex wait helper 與 PI-lock helper
存在，但沒有建立 requeue-PI caller。Phase 5CS 的 ART marker 是 ordinary
compare-requeue 語意映射，不足以改寫這個結論。

限制：ELF 可能 stripped、inline、透過 indirect syscall、由尚未擷取的
library/service 提供，或使用不同字串表示。因此此項只能是 **Negative
observation only**。

## 5. 與 GhostLock 證據門檻的關係

| 門檻 | 本輪結果 | 標籤 |
|---|---|---|
| Exact PS7331 kernel source has PI-requeue proxy path | 由 exact source rows 支持 | 已證實，source scope |
| Source archive contains a direct requeue-PI wrapper | 只在 futex selftests | 已證實，selftest scope |
| Fire framework/app source caller | 0 candidate rows | 尚未建立；bounded negative observation |
| Preserved Fire native named caller | 0 rows | 尚未建立；bounded negative observation |
| Stock runtime entered proxy path | 沒有 same-execution trace | 待驗證 |
| `waiter->task != current` | 未觀察 | 待驗證 |
| Wrong cleanup residue / later consumer | 未觀察 | 待驗證 |
| Memory effect / privilege transition / root | 未證實，未執行 | 因風險拒絕 |

## Phase 6A boundary

下一步可寫成 Phase 6A，但安全的第一個 deliverable 應是觀測設計與隔離
模型，而不是在 stock tablet 上執行 requeue-PI race。要把研究從 static
推到 runtime，至少需要同一次、可歸因的 execution evidence：

1. userspace caller／operation 到 kernel entry 的證據；
2. proxy waiter 的 stored task 與 executing `current` 的 identity observation；
3. return/error branch 的 exact execution record；
4. cleanup 後可讀取、可重現且不涉及 kernel memory write 的 state observation。

目前 Fire shell 沒有可用的 futex tracepoint，`/proc/kallsyms`、`/proc/kcore`
與 `/dev/kmem` 也不可讀；既有 runtime boundary 未看到 futex/rtmutex/requeue
signal。這使 stock-device Phase 6A 不能靠安全的 read-only ADB 完成。

**因風險拒絕測試：**在真機上編譯／執行 futex trigger、race reproducer、
kernel tracing enable、unknown ioctl、kernel memory access、crash 或 root
payload。可繼續的安全路線是隔離 emulator／研究 kernel 的 instrumented
model，且必須把結果標為 lab evidence，不冒充 PS7331 stock runtime evidence。

## Status labels

- **已證實：** exact source path 與 selftest/documentation role 分類；
  native scan 結果與輸出 hash。
- **高可信推論：**目前沒有證據顯示普通 Fire libc/ART 路徑會自然進入
  requeue-PI；這仍需完整 caller coverage 才能更強化。
- **待驗證：** Fire-specific indirect caller、seccomp allow/deny、stock
  runtime identity mismatch 與 cleanup consumer。
- **已排除／不支持：**把 selftest wrapper、documentation example 或
  ordinary compare-requeue string 當作 stock GhostLock execution。
- **因風險拒絕測試：**stock futex race、kernel memory、crash、root stage。

## Reproduction

```sh
python3 tools/scripts/audit_phase5dc_requeue_pi_callers.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/platform \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/fireos \
  --native-scan-dir artifacts/phase5/phase5cr-fire-native-20260804-02 \
  --native-scan-dir artifacts/phase5/phase5cs-fire-amazon-native-20260804-01 \
  --output artifacts/phase5/phase5dc-requeue-pi-caller-audit-NEW
```

The script refuses to overwrite an existing output and supports `--dry-run`.
