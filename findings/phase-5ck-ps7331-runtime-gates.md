# Phase 5CK：PS7331 實機 GhostLock runtime gate snapshot

日期：2026-08-04
裝置範圍：Fire HD 10 11th Generation／KFTRWI／trona／PS7331
Test ID：`PS7331-FUTEX-GATES-20260804-01`

## 結論

### 已證實

1. 更新後的裝置實際回報 PS7331.4463N、incremental `0031575863172`、Linux
   `4.4.146+`、aarch64；採集者是 UID 2000 `shell`，SELinux domain 為
   `u:r:shell:s0`，SELinux 為 `Enforcing`。
2. 普通 shell 的 capability 欄位為零；`perf_event_paranoid` 可讀值為 `3`。
   其他選定 kernel sysctl 多數回傳 `Permission denied`，另有幾個 4.4 路徑
   不存在。原始錯誤均保留，沒有把 denied／missing 當成 enabled 或 disabled
   的證明。
3. `/proc/kallsyms` 對 shell 被拒絕；`/proc/kcore` 與 `/dev/kmem` 不存在或
   不可用。因此這次沒有取得 kernel symbol、KASLR slide、kernel address 或
   source-derived runtime offset。
4. `/dev/ion` 與 `/dev/mtk_cmdq` 只能確認節點 metadata 與 SELinux label；本輪
   沒有 `open()`、allocation、physical-address request 或 ioctl。
5. 本輪完全 read-only：沒有 futex PI／requeue 觸發、沒有 kernel memory access、
   沒有設定修改、沒有 package state mutation、沒有 reboot。

### 高可信推論

- 在 PS7331 的普通 shell domain 下，至少目前的 procfs 與 capability surface
  不提供直接觀察 kernel symbol／address 的必要條件；因此不能可靠地把公開
  GhostLock target 的 layout／offset 套到本機。
- source 中存在 futex PI／rtmutex proxy path，與 runtime gate snapshot 並不矛盾；
  但「系統編譯了該路徑」仍不等於 userspace 已形成 proxy waiter mismatch，
  更不等於存在 root transition。

### 待驗證

- 研究者完成 PS7331 首次解鎖／OOBE 後，正常 Android userspace 是否有任何合法
  application API 可以觀察到 futex PI 行為；本 snapshot 沒有呼叫該 API。
- Amazon release build 是否有 source archive 之外的 binary patch；shell 不能
  讀取 signed kernel block，因此這點不能由本輪 procfs 結果判定。

### 已排除／不採用

- 「`/dev/ion` 或 `/dev/mtk_cmdq` 存在，就代表 shell 可 root」：只有 metadata，
  沒有權限轉換證據。
- 「`/proc/kallsyms` 沒有 symbol，就代表 futex 沒有編譯」：實際是 permission
  boundary，不能作此推論。
- 「PS7331 能跑 Linux 4.4 futex，所以 `ghostlock-emerald` 可直接執行」：公開
  專案 target 是另一個 SoC／kernel generation，不能直接移植。

### 因風險拒絕測試

以下操作未執行：GhostLock PoC、futex race、kernel UAF 觸發、kernel memory
read/write、未知 ioctl、ION/CMDQ request、BROM/DA、preloader/LK、fastboot
unlock/flash、boot image 寫入、remount、SELinux 修改與 partition write。

## 原始證據

| Evidence ID | 檔案 | 觀察 | Confidence |
|---|---|---|---|
| `P5CK-RUNTIME-001` | `adb/phase5/PS7331-FUTEX-GATES-20260804-01/identity.stdout.txt` | shell UID/domain、Enforcing、Linux 4.4.146+、PS7331 fingerprint | Confirmed |
| `P5CK-RUNTIME-002` | `.../process_status.stdout.txt` | 採集程序的 shell UID、零 capability、seccomp 欄位 | Confirmed，process scope |
| `P5CK-RUNTIME-003` | `.../kernel_sysctls.stdout.txt` | sysctl read results 與每個 permission/missing error | Confirmed，visibility scope |
| `P5CK-RUNTIME-004` | `.../proc_visibility.stdout.txt` | kallsyms denied、kcore/kmem unavailable、ION/CMDQ metadata | Confirmed，visibility scope |
| `P5CK-RUNTIME-005` | `.../futex_symbols.stdout.txt` | symbol query 被 kallsyms permission boundary 阻擋 | Confirmed，negative observation only |
| `P5CK-SAFETY-001` | `.../result.md`、`sha256sums.txt` | read-only capture，沒有 device mutation | Confirmed |

## 與 GhostLock source evidence 的關係

PS7331 exact source 的既有分析仍指出 `futex_requeue()` 可以在 source-level
上呼叫 `rt_mutex_start_proxy_lock()`，而 `remove_waiter()` 使用
`current->pi_blocked_on`。這只證明 source wiring 與 advisory 所述形狀相近。
本輪實機資料沒有把 source path 提升成 runtime reachability、持久 invariant
錯誤、可控 memory effect 或 root proof。

公開 target-profile 參考：<https://github.com/datfooldive/ghostlock-emerald>
。該專案 README 標示 Poco M6 Pro／MT6789／Android 16／kernel 6.12.30；本機
是 MT8183／Android API 28／Linux 4.4.146+。所以本輪只採用它作相容性研究
參考，沒有 clone、build、install 或 execute。

## 重現

```sh
bash tools/scripts/capture_phase5p_futex_gates.sh \
  --serial DEVICE_SERIAL \
  --test-id PS7331-FUTEX-GATES-YYYYMMDD-NN \
  --output adb/phase5/PS7331-FUTEX-GATES-YYYYMMDD-NN
```

腳本只讀取 identity、kernel sysctl、`/proc` visibility 與 device-node metadata，
並保存每個命令的 stdout、stderr、exit code 與 SHA-256；它不開啟任何 device
node，也不觸發 futex。
