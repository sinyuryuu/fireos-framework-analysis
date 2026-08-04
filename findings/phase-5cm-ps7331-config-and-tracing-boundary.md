# Phase 5CM：PS7331 kernel config 與 tracing visibility boundary

日期：2026-08-04
Test ID：`PS7331-CONFIG-GATES-20260804-03`

## 已證實

更新後 PS7331 的 `/proc/config.gz` 可被 shell 讀取，並回報：

```text
CONFIG_FUTEX=y
CONFIG_RT_MUTEXES=y
CONFIG_SECCOMP=y
CONFIG_SECCOMP_FILTER=y
CONFIG_SECURITY_SELINUX=y
CONFIG_DEBUG_FS=y
CONFIG_KALLSYMS=y
# CONFIG_KALLSYMS_ALL is not set
```

同一輪只讀檢查顯示 debugfs 與 tracefs 已掛載；路徑 metadata 可 stat，但
目錄 listing 的成功或失敗必須以 `tracing_listing.stdout.txt` 與 stderr
為準。這表示「相關功能編譯存在」與「普通 ADB shell 可以觀察 tracing」
是兩個不同條件。

shell 可以列出部分 trace event categories；目前保存的分類中出現 `sched`、
`block`、`filelock` 等，但沒有名稱為 `futex` 或 `rtmutex` 的專用 category。
這只是 tracepoint inventory，不能用來判定 futex/rtmutex path 是否執行。

## 判定

### 高可信推論

- PS7331 build 的 kernel configuration 與 source-level futex/rtmutex path
  相容；這提高 source-to-runtime feature applicability 的信心。
- 目前普通 shell 沒有取得 task identity event 的已驗證輸出；因此本輪仍無法
  觀察 `waiter->task != current`。若 listing 被拒絕，這是 SELinux visibility
  boundary；若 listing 成功，也不等於已取得 identity event 或 cleanup trace。

### 待驗證

- `CONFIG_HAVE_FUTEX_CMPXCHG` 是否由 arch/Kconfig 以不同形式導出；本輪沒有
  把缺少的輸出當成 unset。
- system service 或 privileged tracing domain 是否能合法取得相同事件；這
  不是 shell 可用性證據，也不是取得 root 的旁路。

### 已排除

- 「CONFIG_FUTEX=y 就代表 GhostLock 可利用」：不成立。
- 「debugfs/tracefs 已掛載就代表 shell 可讀」：不成立；需看 directory
  listing 與 event file 的實際結果。
- 「沒有 futex/rtmutex trace category 就代表 path 不存在」：不成立。
- 「tracefs denied 就代表 futex 沒有執行」：不成立。

## 安全範圍

本輪沒有啟用 tracing、寫入 debugfs、觸發 futex PI、開啟 `/dev/ion`／
`/dev/mtk_cmdq`、執行 ioctl、讀寫 kernel memory 或執行 root payload。

## 證據

| Evidence ID | 原始輸出 | 結論 | Confidence |
|---|---|---|---|
| `P5CM-CONFIG-001` | `adb/phase5/PS7331-CONFIG-GATES-20260804-01/config.stdout.txt` | futex/rtmutex、seccomp、SELinux、debugfs、kallsyms config flags | Confirmed，runtime config |
| `P5CM-TRACE-001` | `.../tracing_paths.stdout.txt`、`tracing_listing.stdout.txt`、`mounts.stdout.txt` | mount、path stat 與 directory listing 分開保存 | Confirmed，visibility scope |
| `P5CM-TRACE-002` | `.../tracing_event_categories.stdout.txt`、`futex_event_search.stdout.txt` | event inventory；無專用 futex/rtmutex category 名稱 | Confirmed，inventory scope |
| `P5CM-SAFETY-001` | `.../result.md`、`sha256sums.txt` | read-only capture；無 device mutation | Confirmed |

## 重現

```sh
bash tools/scripts/capture_phase5cm_config_gates.sh \
  --serial DEVICE_SERIAL \
  --test-id PS7331-CONFIG-GATES-YYYYMMDD-NN \
  --output adb/phase5/PS7331-CONFIG-GATES-YYYYMMDD-NN
```
