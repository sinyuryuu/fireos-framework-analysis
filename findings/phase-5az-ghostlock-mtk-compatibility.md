# Phase 5AZ：GhostLock／MTK exact-target compatibility review

日期：2026-08-04
裝置：Amazon Fire HD 10 2021，`KFTRWI` / `trona` / MT8183
Build：`Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`
Kernel：`4.4.146+`，AArch64

## 結論先行

### 已證實

1. Amazon 公開的 Fire HD 10 7.3.3.0 source archive 中，exact
   `kernel/mediatek/4.4/kernel/locking/rtmutex.c` 與 pinned Linux v4.4.146
   reference 的 normalized SHA-256 相同，且比較結果為零差異。
2. Exact runtime/defconfig evidence 顯示 `CONFIG_FUTEX=y`、
   `CONFIG_RT_MUTEXES=y`、`CONFIG_PREEMPT=y` 與 `CONFIG_RANDOMIZE_BASE=y`。
   Exact source 也保留 `FUTEX_WAIT_REQUEUE_PI`、`FUTEX_CMP_REQUEUE_PI` 與
   proxy-lock 呼叫路徑。
3. 這些證據使 GhostLock／`CVE-2026-43499` 成為本機最強的
   **source/config candidate**，但不是 signed PS7330 binary 的漏洞確認。
4. 已測的 KoCleo `mtk-su64` payload 與公開 fork 的 LFS payload 相同；該 payload
   在 exact PS7330 測試中於 critical init step 3 失敗，沒有取得 UID 0。
5. 目前沒有 exact PS7330 signed `boot.img`、kernel `Image`/`vmlinux`、LK、
   preloader、DA/auth bundle。公開 `fenrir`、`lkpatcher` 與 generic mtkclient
   不能因此變成 Amazon `trona` 的可用路徑。

### 高可信推論

- 如果 installed PS7330 kernel 是由保存的 7.3.3.0 source family 建置且沒有
  未公開 backport，GhostLock 的 root-cause control flow 很可能仍在 binary 中。
- CMDQ v2 payload 與 exact source 選出的 v3 interface 不匹配，是既有
  `mtk-su64` step-3 failure 的主要解釋；仍不能由 source 取代 signed binary
  證據。

### 待驗證

- signed PS7330 binary 是否將 `remove_waiter()` 修正、移除或改寫；
- compiled `task_struct.pi_blocked_on`、KASLR／physmap 與 Android privilege
  transition 的實際值；
- exact PS7330 CMDQ compiled driver 是否與公開 source 完全一致；
- 是否存在未公開且可由 shell 達到的 Amazon vendor vulnerability。

### 已排除或不適用

- 將 PS7331 的 compiled pattern 當成 PS7330 binary proof；
- 將 Pixel、Android 12/16/17、Samsung 或其他 MTK device 的 GhostLock profile
  直接套用到本機；
- 把已失敗的 `mtk-su64` fork 當成新的 payload 重跑；
- 把 `CVE-2026-43503` 或 `CVE-2026-3499` 當成 GhostLock；
- 把公開 source 的 `struct rt_mutex_waiter` layout 當成 runtime exploit offset。

### 因風險拒絕測試

本輪沒有執行 futex race、kernel-memory write、ION/CMDQ ioctl、BROM/DA、
preloader/LK patch、seccfg、fastboot unlock/flash、分割區讀寫或未知 root
payload。這些操作缺少 exact target artifact 與可靠復原路徑；設備「可變磚」
不是足以把錯誤版本 payload 變成可驗證實驗的條件。

## Exact evidence

完整矩陣：[`output/tables/phase5az-root-route-matrix.csv`](../output/tables/phase5az-root-route-matrix.csv)
Evidence index：[`findings/phase-5az-evidence-index.md`](phase-5az-evidence-index.md)
可重產腳本：[`tools/scripts/build_phase5az_compatibility_matrix.py`](../tools/scripts/build_phase5az_compatibility_matrix.py)

### GhostLock source/config chain

```text
Fire HD 10 7.3.3.0 public source
        │
        ├─ kernel/locking/rtmutex.c
        │    └─ old remove_waiter() current-task cleanup pattern
        │
        ├─ kernel/futex.c
        │    └─ FUTEX_*_REQUEUE_PI → rt_mutex_start_proxy_lock()
        │
        └─ MT8183 runtime config
             ├─ CONFIG_FUTEX=y
             ├─ CONFIG_RT_MUTEXES=y
             └─ CONFIG_RANDOMIZE_BASE=y
```

這條鏈在 source/config 層成立；signed-image、compiled-layout 與 Android
post-exploitation 階段仍是未知。`CONFIG_FUTEX_PI` literal 沒有出現在 capture
中，不能被解讀為 PI 支援關閉，因為 v4.4 source 的 PI cases 位於 futex/rtmutex
路徑本身。

### Why the current payload is not a new route

`KoCleo/mtk-easy-su` fixed commit 的 `mtk-su64` LFS OID 與先前
`MTK-SU-CMDQ-T03` 執行的 binary 相同。先前結果是：

```text
exit code: 1
stderr: Failed critical init step 3
UID 0: none observed
rollback: successful
```

Exact source follow-up 顯示 payload 使用的 `0x40087807` 屬於舊 CMDQ
write-address allocation contract，而 exact source selection 指向 v3
dispatcher；這是高可信的 interface mismatch hypothesis，但沒有新的 binary
或非破壞性測試可以把它提升為 compiled-driver proof。

## Boot-chain route boundary

現有證據是：

- `ro.boot.flash.locked=1`；
- exact PS7330 boot block 的 shell read 被拒絕；
- 工作區可解析的 boot-chain image 是相鄰 PS7331，且已標記
  `VERSION_MISMATCH`；
- `fenrir` 支援清單沒有 `trona/KFTRWI`；
- `lkpatcher` 需要匹配 LK image；
- generic mtkclient 的 shared MTK profile 不等於 Amazon preloader/auth/rollback
  相容性。

因此 BROM、DA、preloader、LK 與 seccfg 路線目前只能列為「需要 exact artifact
的 Level 3 route」，不能當作可重現的研究結果。沒有執行 handshake、read、erase
或 write。

## Public-source boundary

- [Amazon Fire HD 10 7.3.3.0 source archive](https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2)
- [NebuSec IonStack Part II](https://nebusec.ai/research/ionstack-part-2/)
- [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)
- [KoCleo/mtk-easy-su pinned review](https://github.com/KoCleo/mtk-easy-su/tree/8c6871ac7c15b8e98a47e25c35ab93b87e260475)
- [fenrir](https://github.com/R0rt1z2/fenrir)
- [lkpatcher](https://github.com/R0rt1z2/lkpatcher)

公開來源查找沒有發現 `PS7330.4104N` exact signed boot/vmlinux 或 exact
GhostLock Android target。這是目前記錄範圍內的搜尋結果，不宣稱整個網路絕對不存在。

## Current best next step

最高價值且仍安全的下一步，是取得合法、完整匹配的 PS7330 signed kernel/boot
artifact 或可重現的同版 kernel build input，然後只在主機上：

1. 核對 hash、build ID、compiler 與 config；
2. 比對 `remove_waiter()` 與 `futex.c` control flow；
3. 計算 source/ABI 與 compiled layout 的差異；
4. 再決定是否值得另立、且獨立審查的 live-test 報告。

在此之前，沒有證據支持把錯誤版本的 GhostLock、mtkclient 或 LK payload 推到
裝置上；那只會產生不可歸因的 crash/brick，而不會回答漏洞是否適用。
