# Phase 5AV：GhostLock upstream fix 與 exact PS7330 邊界

## 目的

本輪只做 host-only、read-only 的 GhostLock/CVE-2026-43499 核對：

1. 固定上游修補 commit 與 follow-up；
2. 將修補前後語意與 Amazon 7.3.3.0 source 比對；
3. 重新整理 exact PS7330 runtime 的可達性與資訊可見性；
4. 決定目前是否有足夠證據執行 live root payload。

沒有執行 futex race、GhostLock reproducer、ION/CMDQ ioctl、native root binary、ADB exploit、fastboot、BROM/DA、bootloader 解鎖或分割區寫入。

## 結論

| 判定 | 結果 |
|---|---|
| PS7330 source 是否含修補前的 remove_waiter 語意 | **已證實，source scope** |
| PS7330 source 是否與 stable v4.4.146 舊 rtmutex.c 相同 | **已證實，normalized byte-identical** |
| exact PS7330 signed kernel 是否確定未私有 backport | **待驗證** |
| CONFIG_FUTEX／CONFIG_RT_MUTEXES 是否開啟 | **已證實，runtime config scope** |
| shell 是否能取得 exact kernel symbol/KASLR/task offset | **已證實不能，current shell scope** |
| 公開 generic Android root PoC 是否可直接套用 | **已排除，target mismatch** |
| 現在是否執行 GhostLock root payload | **因風險拒絕測試** |

## 1. 上游修補鏈

### CVE-2026-43499 初始修補

上游 commit：

- Commit：3bfdc63936dd4773109b7b8c280c0f3b5ae7d349
- Subject：rtmutex: Use waiter::task instead of current in remove_waiter()
- Merged into locking/urgent：2026-04-21
- Stable 7.0 backport：2026-05-04

修補把 remove_waiter() 中的 owner task 從 current 改成 waiter->task，並在該 task 的 pi_lock 下清理 pi_blocked_on，同時把 rt_mutex_adjust_prio_chain() 的最後 task 參數改成 waiter_task。

這正好對應 GhostLock 的錯誤語意：

- proxy-lock rollback 時，waiter->task 不等於 current；
- 舊邏輯清理錯誤 task 的 pi_blocked_on；
- waiter task 會保留指向已釋放 rt_mutex_waiter 的 dangling pointer；
- 後續 PI chain walk 可能觸發 UAF。

來源：

- Linux kernel patch archive：https://www.spinics.net/lists/kernel/msg6163230.html
- Stable 7.0 backport：https://www.spinics.net/lists/stable/msg940408.html
- GhostLock technical record：https://nebusec.ai/buglist/CVE-2026-43499/

### Follow-up CVE-2026-53163

初始修補之後，upstream 又修正一個與未入隊 waiter 及 return code 判斷有關的 follow-up：

- Commit：40a25d59e85b3c8709ac2424d44f65610467871e
- 主要變更：只在 ret < 0 時呼叫 remove_waiter()，並處理 waiter_task 為空的情況。

這個 follow-up 不改變本專案對 PS7330 的核心判定：PS7330 的 exact public source 是 2024 年 v4.4.146 family，與 2026 年修補提交時間相隔很久；但沒有 signed PS7330 binary，仍不能把 source 判定升級成 binary proof。

## 2. Amazon exact source 證據

已保存的 exact Amazon member：

- Member：kernel/mediatek/4.4/kernel/locking/rtmutex.c
- Normalized SHA-256：c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345
- Stable v4.4.146 normalized SHA-256：c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345
- Normalized lines：1754 vs 1754
- Unified diff：0

比較 artifact：

artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json

已保存的 source locations：

- rtmutex.c:1079–1090：remove_waiter() 使用 current->pi_lock、dequeue waiter 並清除 current->pi_blocked_on；
- rtmutex.c:1657–1689：proxy-lock error path 會進入 remove_waiter()；
- futex.c：含 FUTEX_WAIT_REQUEUE_PI、FUTEX_CMP_REQUEUE_PI、rt_mutex_start_proxy_lock() 路徑。

**已證實，source scope：** public Fire source 沒有 3bfdc63936dd 的 waiter_task 修補。

**高可信推論：** 如果 PS7330 signed kernel 由該 source family 建置且沒有未公開 backport，GhostLock root-cause pattern 仍存在。

**待驗證：** Amazon 是否在 2024 source archive 之外對 signed kernel 做過私有 rtmutex patch。

## 3. Exact runtime gate

目前裝置 read-only evidence：

| Gate | Observed result |
|---|---|
| Build | Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys |
| Kernel | Linux 4.4.146+, AArch64, PREEMPT |
| Caller | UID 2000, context u:r:shell:s0 |
| SELinux | Enforcing |
| CONFIG_FUTEX | y |
| CONFIG_RT_MUTEXES | y |
| CONFIG_PREEMPT | y |
| CONFIG_RANDOMIZE_BASE | y |
| perf_event_paranoid | 3 |
| /proc/kallsyms | shell denied |
| kptr_restrict | shell denied |
| randomize_va_space | shell denied |
| /proc/kcore | unavailable to shell |
| exact boot/vmlinux | unavailable to shell |

這些結果能確認 source/config family 與安全邊界，但不能取得：

- compiled task_struct.pi_blocked_on offset；
- signed binary 的 actual remove_waiter control flow；
- kernel text base / KASLR slide；
- physmap 或 CPU entry area address；
- compiler-specific gadgets；
- target-specific exploit header。

## 4. 為何不直接執行公開 GhostLock exploit

公開研究頁描述的完整 root chain不只需要觸發 UAF，還依賴 kernel image/physmap information、stack reclaim、fake waiter、controlled write 與 kernel control-flow pivot。這些都是 exact signed image 與 target-specific layout 依賴項。

目前缺少：

1. exact PS7330 signed boot.img 或 vmlinux；
2. exact compiled task_struct layout；
3. exact KASLR/physmap/CPU-entry-area information；
4. exact Android arm64 payload profile；
5. 在 panic 或失敗後不需 factory reset 的 verified recovery path。

因此將其他 MTK、其他 Android、其他 kernel version 的 payload 套到本機，結果只能分類為：

- **不是相容性測試**；
- **不是可解釋的 negative result**；
- **可能是 kernel panic、ADB loss 或 userspace corruption**。

本輪沒有下載、編譯或執行公開 exploit/reproducer，也沒有把其 payload 寫入裝置。

## 5. 對目前假設的判定

### H-GHOST-SOURCE

**已證實，限定 source/config scope：** Amazon 7.3.3.0 public source 顯示 GhostLock 修補前的 rtmutex 語意，並且 runtime config 開啟相關 futex/rtmutex family。

### H-GHOST-BINARY

**待驗證：** exact signed PS7330 binary 是否保留相同 control flow。Source archive 不能取代 signed image。

### H-GHOST-ROOT

**待驗證但目前不可安全實測：** 即使 H-GHOST-BINARY 成立，仍需 exact arm64 layout、KASLR/physmap information 與 Android-specific post-exploitation chain。

### H-GHOST-MTK-SU

**已排除，既有測試條件：** KoCleo/mtk-easy-su fork 使用的 mtk-su payload 與已測 MTK-SU-CMDQ-T03 相同，不能作為新的候選。

### H-GHOST-BOOTCHAIN

**已排除，版本／復原條件不足：** PS7331 boot-chain image、generic MTK DA、fenrir、lkpatcher 不能被當作 PS7330 recovery set。

## 6. 可重現的 host-only 命令

既有 source comparator：

tools/scripts/compare_phase5_exact_rtmutex_source.py

既有 source comparison result：

artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-compare.txt

既有 runtime gate capture：

tools/scripts/capture_phase5p_futex_gates.sh

其用途是確認 source/config/visibility boundary；不會觸發 futex PI、不開啟 device node、不寫 sysctl、不重開機。

## 7. 下一個最高價值資料

若要把 H-GHOST-BINARY 從待驗證提升，最小必要資料是：

1. 可信來源的 exact PS7330.4104N signed kernel/boot artifact；
2. 與 artifact 對應的 hash、build metadata 與分割區來源；
3. host-only disassembly 對 remove_waiter、rt_mutex_start_proxy_lock、futex_requeue 的控制流比對；
4. 只在另有 verified recovery path 時，才重新評估 live test。

在取得這些資料前，執行 root payload 不會增加可判讀的證據品質。

## 8. Safety decision

**因風險拒絕測試：**

- GhostLock race/reproducer；
- 公開 exploit binary；
- ION/CMDQ ioctl；
- BROM/DA/preloader/LK；
- fastboot unlock/flash；
- boot、vbmeta、system、vendor、userdata 寫入；
- 任何以「設備可變磚」為理由的未知 payload。

這不是宣稱 GhostLock 對 PS7330 一定無效，而是把目前最強結論限定在可驗證的 source/config scope。
