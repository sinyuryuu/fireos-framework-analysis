# Phase 5CQ：Android 9 userspace 與 futex requeue-PI 可達性

日期：2026-08-04
目標：補足 GhostLock 從 kernel source/dataflow 到 Android userspace 的證據邊界
方法：主機端、只讀、AOSP reference comparison
安全狀態：沒有編譯或執行 kernel，沒有呼叫 futex syscall，沒有建立 race、地址、payload 或提權流程，也沒有操作裝置。

## Executive result

本輪確認一個重要的 userspace 邊界：AOSP Android 9 的一般 bionic pthread condition-variable 路徑使用一般 futex wait/wake helper；它不是 requeue-PI 的直接呼叫者。AOSP 的 UAPI header 仍公開 PI 與 requeue-PI 常數，因此 kernel 端的 API surface 存在，但不能據此推論普通 Android 應用自然會走到 GhostLock 路徑。

| 判定 | 結果 | 證據 |
|---|---|---|
| Android 9 bionic condition-variable signal/broadcast 使用一般 futex wake helper | 已證實，AOSP r61 reference scope | `P5CQ-001` |
| Android 9 bionic condition-variable wait 使用一般 futex wait helper | 已證實，AOSP r61 reference scope | `P5CQ-002` |
| AOSP userspace UAPI 暴露 PI/requeue-PI 常數 | 已證實，AOSP UAPI reference scope | `P5CQ-003` |
| AOSP r61 有專用 bionic futex syscall stub | 未在該 syscall table 觀察到；僅為 reference negative observation | `P5CQ-004` |
| PS7331 kernel source/config 具備 futex/rtmutex 與 proxy path | 已證實，PS7331 source/config scope | `P5CO-*`, `P5CP-*` |
| 普通 Android pthread condvar 在 Fire PS7331 實際進入 GhostLock path | 尚未取得 Fire libc 的同等 binary/source execution evidence | `P5CQ-006` |
| Fire app 的 seccomp/SELinux 允許任何特定 direct futex route | 尚未證實；不可由 AOSP policy 代替 | `P5CQ-005`, `P5CQ-007` |
| stock runtime 曾觀察到 identity mismatch 或錯誤 cleanup | 尚未觀察 | `P5CP-RUNTIME-001`, `P5CP-RUNTIME-002` |

## 1. 研究問題與結論

### 1.1 「kernel 可達」不等於「普通 Android userspace 可達」

PS7331 source 已有 `futex_requeue()` → `rt_mutex_start_proxy_lock()` 的 proxy dataflow，以及 `remove_waiter()` 使用 implicit `current` 的 pre-fix semantics。這證明 kernel source 具有目標路徑，但尚未證明 Fire OS 上的常用 userspace synchronization primitive 會呼叫該路徑。

AOSP Android 9 r61 的 `libc/bionic/pthread_cond.cpp` 中：

- signal/broadcast 路徑呼叫 `__futex_wake_ex`；
- wait 路徑呼叫 `__futex_wait_ex`；
- 該檔案沒有以 requeue-PI 作為 pthread condition-variable 的一般實作路徑。

因此，以下說法不能成立：

```text
Android app 使用普通 pthread condition variable
→ 必然進入 FUTEX_WAIT_REQUEUE_PI / FUTEX_CMP_REQUEUE_PI
→ 必然觸發 GhostLock
```

### 1.2 UAPI 存在，但不是使用證據

AOSP bionic 的 generated futex UAPI header 列出 PI 與 requeue-PI operation constants。這表示 native userspace 在 API header 層知道這些 kernel operations；它不表示某個普通 Java API、pthread API 或 Fire system service 已經使用它們。

此外，AOSP Android 9 的 `libc/SYSCALLS.TXT` 沒有對應的專用 futex generated stub entry。這是「沒有專用 bionic wrapper entry」的 reference observation，不是「所有 native direct syscall 都不可能」的證明。Fire OS 是否有私有 native caller、不同 bionic 版本、seccomp 例外或 vendor library，仍需另以 Fire-specific artifact 判定。

### 1.3 AOSP seccomp reference 不能替代 Fire runtime policy

AOSP r61 的 app seccomp whitelist/blacklist 檔案說明的是 AOSP reference policy 生成邊界。Fire OS 可能有不同 policy、zygote profile 或 Amazon vendor 規則。現有 PS7331 裝置 capture 只證明 shell 的 visibility/permission boundary，沒有證明任一特定 application domain 對 futex PI 的 allow/deny 結果。

## 2. 證據範圍

### 已證實

1. PS7331 的 kernel source 具備 futex PI dispatch、requeue-PI proxy call 與 pre-fix cleanup semantics（見 Phase 5CO/5CP）。
2. AOSP Android 9 r61 的普通 pthread condition-variable implementation 使用一般 wait/wake helper，而非 requeue-PI。
3. AOSP UAPI header 暴露 PI/requeue-PI operation constants。
4. 目前保存的 PS7331 stock captures 沒有同一次 execution 的 proxy error trace、identity mismatch、wrong cleanup target 或後續 consumer trace。

### 高可信推論

1. 若要從 Android 9 userspace 進入 GhostLock 目標 path，最可能需要 native/private synchronization code 或直接使用 kernel futex interface；普通 bionic pthread condition variable 不足以作為該入口的證據。
2. Fire-specific libc、seccomp 與 private native service 的差異，是目前比重複 ADB 普通命令更有資訊價值的下一個靜態分析目標。

### 待驗證

1. Fire PS7331 實際 `/system/lib64/libc.so` 與 vendor native libraries 是否包含 requeue-PI caller。
2. Fire app/zygote seccomp policy 對 futex PI operations 的實際 allow/deny。
3. 是否有 Amazon private service 或 native daemon 使用 requeue-PI。
4. 即使存在 caller，是否能在 stock runtime 讓 proxy error cleanup 執行並留下可觀察 state。

### 已排除或未支持

1. 「普通 pthread condition variable 必然觸發 GhostLock」未獲 AOSP reference 支持。
2. 「UAPI header 有常數，所以 direct futex route 已可在 Fire shell 使用」未獲證明。
3. 「一次 source-level `waiter->task != current` 就等於 root」不成立；目前 D1-R、D2、D3、D4 仍未完成。

## 3. AOSP reference locations

以下是本輪使用的官方 AOSP reference；它們不是 Fire OS binary 的替代品：

| Evidence | Reference | 觀察 |
|---|---|---|
| `P5CQ-001`, `P5CQ-002` | [`pthread_cond.cpp`, Android 9.0.0_r61](https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/bionic/pthread_cond.cpp) | condition-variable wait/signal 的 futex helper 路徑 |
| `P5CQ-003` | [`futex.h`, AOSP bionic UAPI snapshot](https://android.googlesource.com/platform/bionic/+/3a6c6b3/libc/kernel/uapi/linux/futex.h) | PI/requeue-PI constants exposed to userspace |
| `P5CQ-004` | [`SYSCALLS.TXT`, Android 9.0.0_r61](https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/SYSCALLS.TXT) | no dedicated futex generated-stub entry observed |
| `P5CQ-005` | [`SECCOMP_WHITELIST_APP.TXT`, Android 9.0.0_r61](https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/SECCOMP_WHITELIST_APP.TXT) and [`SECCOMP_BLACKLIST_APP.TXT`](https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/SECCOMP_BLACKLIST_APP.TXT) | AOSP policy reference only |

## 4. 下一個安全且資訊量最高的步驟

只做離線 artifact review：

1. 對已保存的 Fire Launcher、SystemUI、Amazon service native libraries 與可讀取的 Fire libc artifact 做字串/符號/呼叫者索引。
2. 檢查是否有 requeue-PI symbol/reference；若沒有，記錄為 negative observation，不推論不存在。
3. 對 Fire-specific seccomp XML/profile、zygote policy 或已保存 policy artifact 做靜態比對。
4. 將結果與 `P5CP-RUNTIME-*` 分開；在沒有 kernel trace 的情況下，不把 userspace caller evidence 寫成 runtime mismatch。

本專案不在 stock Fire 平板上執行 futex trigger、race、crash、kernel memory access、root payload 或未知 ioctl。若要取得 D1-R/D2，應使用隔離且可觀測的研究 kernel/emulator；這不會把隔離環境結果冒充為 Fire stock runtime 證據。

## Bottom line

本輪把 GhostLock 的「userspace 可達性」縮小為一個可驗證問題：**AOSP Android 9 的普通 pthread condition-variable 路徑不是 requeue-PI 入口；PS7331 kernel path 雖然存在，Fire-specific native caller、policy allowance 與 runtime cleanup observation 仍未證實。**
