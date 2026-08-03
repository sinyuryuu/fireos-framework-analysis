# Phase 5P：Android 舊核心 GhostLock 實作與 Fire OS runtime gates

## Executive summary

本輪把「公開 kernel source 可以計算什麼」與「公開 Android PoC 可以移植什麼」
分開驗證，並對目前的 Fire HD 10 做只讀 runtime gate 採樣。

- **已證實（裝置／runtime）：** 目前設備是 `KFTRWI / trona / MT8183`，Fire OS
  build fingerprint 為
  `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`，
  kernel 為 `4.4.146+`、AArch64、SELinux enforcing。此輪 shell 身分是 UID
  2000，`CapEff=0`，`/proc/kallsyms` 和多個 kernel sysctl 對 shell 不可讀。
- **已證實（source/config）：** Amazon exact `futex.c` 仍包含 futex PI／proxy
  路徑；與 stable v4.4.146 的可見差異是 MTK FPSGO timer hook，不是
  `remove_waiter()`／proxy rollback 的差異。runtime config 有
  `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`、`CONFIG_PREEMPT=y`，且
  `CONFIG_PANIC_ON_OOPS=y`、`CONFIG_PANIC_ON_OOPS_VALUE=1`。
- **已證實（Android source comparison）：** 最接近的公開 Android port 是
  `NothingFumo/ghostlock-aresin`，目標為 POCO F3 GT／MT6893、Android 13、
  Linux 4.14.186。其 `rt_mutex_waiter` profile 與 Fire 的 4.4 layout 不同，
  並且 README 明確要求裝置專用 boot/vmlinux 分析；不能直接套用到 MT8183。
- **高可信推論：** 公開 Android 實作提供的是「每台裝置重新取得 kernel
  layout、地址與 compiler 結果」的方法，而不是通用 Android binary。只用
  Fire 的公開 source 或另一台 MTK 的 `target.h`，不足以形成可驗證的 Fire
  target。
- **因風險拒絕測試：** 沒有安裝、編譯、推送或執行任何 GhostLock/root PoC，
  沒有觸發 futex PI、kernel panic、reboot、ioctl、bootloader 或分割區操作。

## 1. CVE identity boundary

GhostLock 對應 **CVE-2026-43499**，影響 Linux `rtmutex`／futex PI 路徑。
NVD 的記錄把修正描述為在 `remove_waiter()` 使用 `waiter->task`，而不是把
`current` 當成等待者；這是本專案 Phase 5O 比對的漏洞家族。

**CVE-2026-43503 不是 GhostLock**；其公開記錄是 Linux networking
`skb` shared-frag marker propagation 問題，與本輪的 `rtmutex.c` 不同。使用者
提出的 `CVE-2026-3499` 在本輪檢索中沒有找到可核對的 GhostLock 官方記錄，
因此不把它當作本設備的分析目標。

來源：

- [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)
- [NVD CVE-2026-43503](https://nvd.nist.gov/vuln/detail/CVE-2026-43503)

## 2. Device and read-only evidence

| Evidence ID | 原始檔 | 觀察 | 信心 |
|---|---|---|---|
| `P5P-DEVICE-001` | `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/identity.stdout.txt` | UID 2000 shell、SELinux enforcing、AArch64 4.4.146、PS7330 fingerprint | 已證實 |
| `P5P-DEVICE-002` | `.../process_status.stdout.txt` | `Uid/Gid=2000`、`CapEff=0`、`Seccomp=0`；此輸出由 shell 執行的 `/proc/self/status` 取得 | 已證實 |
| `P5P-DEVICE-003` | `.../kernel_sysctls.stdout.txt` | `perf_event_paranoid=3`；panic/KASLR/kptr 等多數 sysctl 對 shell 回傳 Permission denied | 已證實（可見性 scope） |
| `P5P-DEVICE-004` | `.../proc_visibility.stdout.txt` | `/proc/kallsyms` denied、`/proc/kcore`／`/dev/kmem` 不存在；`/dev/ion` 與 `/dev/mtk_cmdq` 的 mode/SELinux label 已保存 | 已證實（可見性 scope） |
| `P5P-DEVICE-005` | `adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/kernel_config.stdout.txt` | `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_PREEMPT=y`, `CONFIG_RANDOMIZE_BASE=y`, `CONFIG_PANIC_ON_OOPS=y` | 已證實（captured config scope） |

這些採樣是 read-only。個別 `/proc` 或 sysctl 的 Permission denied 只表示
目前 caller 看不到該資料，不代表對應 kernel feature 開啟或關閉。

## 3. Exact Fire source and Android implementation comparison

### 3.1 Fire exact source

Phase 5O 已將 Amazon exact `kernel/mediatek/4.4/kernel/futex.c` 與 stable
v4.4.146 正規化比較：3341 對 3337 行，27 行 diff、3 個 hunks。差異只有：

1. `mt-plat/fpsgo_common.h` include；
2. timer 建立後的 FPSGO timer hook；
3. cleanup 路徑的 FPSGO timer hook。

目前沒有 source evidence 顯示 Fire 對 `remove_waiter()`、
`rt_mutex_start_proxy_lock()` 或 futex requeue PI 做了 Amazon-specific 修正。
這是 source scope 結論，不能外推成 signed kernel binary 一定未修補。

Exact vendor `sched.h` 則不是 upstream v4.4.146 的 byte-identical copy：
`struct task_struct` 從 source line 1685 開始，`pi_blocked_on` 出現在 line 1945，
前方有 `CONFIG_THREAD_INFO_IN_TASK`、WALT 及其他 vendor/config 條件欄位。
因此 upstream `sched.h` 不能直接推出 Fire 編譯後的 task offset。

來源：

- `findings/phase-5o-exact-futex-sched-review.md`
- `artifacts/phase5/exact-futex-sched-review-20260804-04/futex-comparison.json`
- `artifacts/phase5/exact-futex-sched-review-20260804-04/sched-comparison.json`
- `artifacts/phase5/exact-futex-sched-review-20260804-04/futex-diff.txt`

### 3.2 Public Android port

固定審查的 `ghostlock-aresin` commit 是
`1895a89c52dc7d7355f14babe5009c2932dcdb6a`。該專案的公開文件把目標限定為：

- POCO F3 GT／Redmi K40 Gaming Edition，codename `aresin`；
- MediaTek MT6893／Dimensity 1200；
- Android 13／MIUI 14；
- Linux `4.14.186` arm64。

它要求從目標裝置的 boot/vmlinux 或 Ghidra/pahole 重新取得結構與地址，並在
README 中把錯誤適配的預期結果寫成 kernel panic/reboot。這正好說明它不是
可跨裝置複製的 Android APK 或 root binary。

來源：

- [ghostlock-aresin pinned repository](https://github.com/NothingFumo/ghostlock-aresin/commit/1895a89c52dc7d7355f14babe5009c2932dcdb6a)
- `artifacts/phase5/android-nearby-port-review-20260804-01/repo-metadata.tsv`

### 3.3 `rt_mutex_waiter` layout

本輪對 pinned Linux headers 做了 host-only comparison：

| 欄位 | v4.4.146 | v4.14.186 / aresin | 結論 |
|---|---:|---:|---|
| `tree_entry` | `rb_node` @ `0x00` | `rb_node` @ `0x00` | 共同 prefix，不足以證明可移植 |
| `pi_tree_entry` | `rb_node` @ `0x18` | `rb_node` @ `0x18` | 共同 prefix |
| `task` | @ `0x30` | @ `0x30` | 共同 prefix；不代表 `task_struct` 相同 |
| `lock` | @ `0x38` | @ `0x38` | 共同 prefix |
| `prio` | @ `0x40` | @ `0x40` | 共同 prefix |
| `deadline` | 不存在 | `u64` @ `0x48` | 版本差異 |
| non-debug size | `0x48` | `0x50` | 不能複製 aresin waiter profile |

值得特別記錄：aresin README 的 warning 文字說 4.14 使用 `plist_node`，但其
同一 commit 的 `target.h` 與 pinned v4.14.186 header 顯示前兩個欄位是
`rb_node`。本專案採用 header／target profile 的可驗證內容，將 README warning
標記為文件內部不一致，不把它當作 Fire 4.4 的證據。

來源與 hash：

- v4.4.146 header：
  `ee7fcb3d8edb06312606073f02435da8e6bb1d60b53604733a218c75c48ec51c`
- v4.14.186 header：
  `884d551fbfa7e4b98037654d645095a7817d9e30a6e8f5f25f41731e2e4f2040`
- `artifacts/phase5/android-nearby-port-review-20260804-01/source-comparison.tsv`

## 4. Applicability matrix

| 條件 | Fire HD 10 | aresin public port | 判定 |
|---|---|---|---|
| AArch64 | 是 | 是 | 必要但不充分 |
| MediaTek | MT8183 | MT6893 | 不同 SoC |
| kernel line | 4.4.146 | 4.14.186 | 不同 ABI/回溯基線 |
| `CONFIG_FUTEX` | runtime `y` | README claims enabled | 支持 source family |
| `CONFIG_RT_MUTEXES` | runtime `y` | README claims enabled | 支持 source family |
| `CONFIG_PREEMPT` | runtime `y` | README claims enabled | 支持 source family |
| `rt_mutex_waiter` | v4.4 無 deadline | v4.14 有 deadline | target profile 不可複製 |
| `task_struct` | vendor layout，compiled offset 未取得 | MT6893-specific offsets | 未知且不相容 |
| kernel addresses/KASLR | shell 不可直接讀取 | aresin own profile | 不可移植 |
| SELinux/caller reachability | shell domain 的完整 trigger 未驗證 | aresin uses shell/Shizuku | 未知 |
| public exact `trona` target | 未找到 | 不適用 | 搜尋範圍內未發現 |

## 5. Answer to “公開 source 能不能算出來？”

可以算出三種有限結果：

1. 某個 source tree 的控制流是否仍包含 PI/proxy 路徑；
2. 在明確 Kconfig 與 debug 條件下，source-level struct 的欄位 layout；
3. vendor source 與 upstream 的差異，從而列出需要重新驗證的欄位。

公開 source 不能單獨算出：

- signed PS7330 kernel 是否包含私有 backport；
- 編譯器實際產生的 `task_struct` offset、stack placement 與 register layout；
- runtime kernel address、KASLR slide、physmap、symbol visibility；
- Android SELinux 對特定 syscall／memory primitive 的完整可達性；
- 一個可安全執行且能取得 root 的裝置專用 payload。

所以「先提取 boot.img、再計算 offset」在研究方法上是合理方向，但在本設備
上仍屬高風險 Level 3 工作；而且即使有 boot image，還需要確認 signed kernel
與 source/build 完全匹配，不能把 aresin 的常數改名後使用。

## 6. Safety decision

### 本輪未執行

- 不下載或編譯 public exploit source；
- 不安裝 APK、NDK binary、Shizuku payload；
- 不 `adb push` 或執行 native trigger；
- 不讀取 block device、不提取 boot partition；
- 不開啟 `/dev/ion` 或 `/dev/mtk_cmdq`；
- 不執行 futex PI stress、panic trigger 或 root check；
- 不 reboot、fastboot、remount、刷寫或修改分割區。

### 原因

目前 runtime 已保存 `CONFIG_PANIC_ON_OOPS=y`，而 shell 又不能直接取得
`/proc/kallsyms`、KASLR 或 compiled task offsets。錯誤的 aresin profile 在這台
4.4.146/MT8183 上最保守的預期不是「無效而返回」，而是 crash/reboot 或資料
遺失風險。這不符合本輪只讀、可恢復的研究邊界。

若要進行 live trigger，必須另提交「針對 KFTRWI／PS7330／MT8183 的 Level 3
operation-specific report」，包括 payload hash、精確寫入位置、預期 panic/
reboot、資料損失與 recovery plan；本報告不構成該核准，也沒有執行該操作。

## 7. Findings classification

### 已證實

- 本設備身份、kernel、SELinux、shell caller 與 runtime gate 的原始輸出。
- exact Fire source/config 的 futex／rtmutex 相關條件。
- aresin 是另一台 MTK/Android/kernel 的公開 device-specific port。
- v4.4 與 v4.14 waiter layout 的欄位差異。

### 高可信推論

- aresin 可作 Android port 方法參考，但不能作 Fire target profile。
- 下一個關鍵技術問題是取得匹配 signed kernel 的唯讀結構證據，而不是重跑
  同一個 public payload。

### 待驗證

- signed PS7330 kernel 是否已有 `remove_waiter()` 修補 backport；
- Fire 編譯後 `task_struct.pi_blocked_on` 的實際 offset；
- shell domain 是否能達到完整 futex PI 觸發條件；
- 是否存在未公開的 exact `trona/MT8183` Android port。

### 已排除／不採用

- 把 CVE-2026-43503 當成 GhostLock；
- 把 aresin 的地址、task offsets、waiter profile 直接套到 Fire；
- 把 source 中存在 PI 路徑寫成「已證明可 root」；
- 把公開 Android crash/reboot 行為寫成 Fire 上的成功結果。

### 因風險拒絕測試

- 任何會觸發 futex PI、kernel panic、root escalation 或預期 reboot 的 payload
  執行；
- 提取或讀取 boot/block partition；
- 任何需要 root、remount、fastboot 或寫入分割區的適配步驟。

## 8. Reproduction

Host-only public review and the device read-only gate capture can be reproduced
from:

- `artifacts/phase5/android-nearby-port-review-20260804-01/commands.txt`
- `tools/scripts/capture_phase5p_futex_gates.sh --dry-run`
- `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/`
- `adb/phase5/PHASE5P-RUNTIME-20260804-01/`

The gate script requires an explicit serial and refuses an existing output
directory. It never opens a device node, writes a sysctl, triggers futex PI or
changes Android state.
