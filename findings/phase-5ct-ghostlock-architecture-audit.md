# Phase 5CT：GhostLock Emerald 觸發架構與 PS7331 對照

日期：2026-08-04

範圍：公開 `datfooldive/ghostlock-emerald` source／metadata 的離線架構審計，
以及本機已保存的 Fire PS7331 source、Fire libc、ART 與 config 證據。沒有
clone、編譯、安裝、執行、移植或修改 exploit；沒有接觸裝置狀態。

公開 revision：`ebb355d302629a034d0959e5e579496559e8f84e`。

## 結論

公開 Emerald 專案不是「只換 kernel offset 就能套用」的通用 POC。它的
架構包含四個相互依賴的層：

1. 針對特定 kernel release 的 target selection；
2. 多執行緒 PI-requeue trigger；
3. 針對該 kernel layout 的 post-trigger kernel memory stage；
4. 針對該目標的 privilege/root delivery stage。

本機 PS7331 目前只在 source scope 確認了第 2 層所依賴的 kernel defect
family 路徑；Fire userspace 尚未建立同一個 requeue-PI caller，第 3、4 層
也沒有 Fire-compatible 證據。

因此目前判定：

| 判定 | 狀態 |
|---|---|
| PS7331 source 仍有 GhostLock defect family | **已證實，source scope** |
| Emerald userspace trigger 可直接在 PS7331 使用 | **已排除／不支持** |
| PS7331 runtime 可形成 proxy waiter mismatch | **待驗證** |
| mismatch 後有持久 kernel state violation | **待驗證** |
| PS7331 有可控 memory effect | **未證實** |
| 可取得 temporary root | **未證實，未執行** |

## 1. 公開 Emerald 的分層結構

### Target selection

`src/core/main.c` 會依 kernel release 選取 target profile，並把 profile
資料帶入後續流程。`src/core/target.h` 與 device metadata 保存的是
build-specific kernel mapping／layout 資訊，而不是 Android API 層的可攜式
設定。

README 指向的目標是 Poco M6 Pro／MT6789／Android 16／6.12.30；這和 Fire
PS7331 的 MT8183／Android 9／4.4 系列不一致。[Emerald README](https://github.com/datfooldive/ghostlock-emerald/blob/main/README.md)

### Trigger architecture

`main.c` 將 waiter、owner、consumer 分成不同執行緒角色，建立 PI lock
鏈，再進入 requeue-PI 路徑。這個角色分離可以解釋為什麼 kernel source
中的 explicit waiter task 不必等於執行 requeue 的 `current`。

但「公開 source 有這個架構」不等於「Fire libc／Fire app 已形成同一條
caller」。Phase 5CR 只確認 Fire libc 的 ordinary wait helper 與 PI-lock
helper；沒有建立 Fire libc → requeue-PI caller。

### Post-trigger memory and root stages

Makefile 將 target-specific memory、fops／pipe 類元件與 root delivery 元件
編入同一個 executable；README 也明確描述 locked-bootloader root 目標。
這些部分不是診斷程式，而是會改變 kernel security state 的 exploit stage。
本審計不重現其實作細節、不複製 offsets、不產生 payload。

## 2. 與 PS7331 的逐層對照

### Layer 1：target profile

Emerald 的 profile 對應另一個 kernel generation、SoC、build 與資料結構。
PS7331 雖有 exact source、signed boot evidence 與 embedded config，但目前
沒有一份經驗證的 Fire userspace／memory stage profile。只計算或替換偏移
不足以證明可用性。

**判定：Emerald profile 不可直接套用。**

### Layer 2：userspace requeue-PI trigger

PS7331 source 的 futex dispatch／requeue／proxy-lock 邊界已存在，且
`rt_mutex_start_proxy_lock()` 有 explicit task parameter；這是 source
reachability。另一方面，Fire libc 的已擷取 call edges 只證明：

```text
ordinary condition variable → generic futex wait
PI mutex helper → PI lock syscall boundary
```

沒有證明：

```text
Fire userspace → FUTEX_WAIT_REQUEUE_PI / FUTEX_CMP_REQUEUE_PI
```

**判定：kernel source path 已證實；Fire runtime trigger 待驗證。**

### Layer 3：identity mismatch 與後續 consumer

Phase 5CP 證明 source-level context separation：等待者 task 由 futex queue
保存，requeue caller 另行傳入；但現有 stock capture 沒有觀察到同一次
kernel execution 的 `waiter->task != current`，也沒有觀察到
`remove_waiter()` 錯誤 cleanup 後的殘留或第二次消費。

**判定：dynamic validation 尚未開始。**

### Layer 4：memory effect 與 root

Emerald 的成功路徑依賴 target-specific kernel memory／root stage。Fire
目前沒有經驗證的等價 stage；以 Emerald 的 metadata 或 source 直接改成
PS7331 profile，會把未驗證的 kernel write／root payload 帶到真機，不能當作
安全相容性測試。

**判定：不執行；Fire root 未證實。**

## 3. 為什麼不能直接「自己改 offset」

至少需要同時證明：

- Fire build 的 userspace 確實能呼叫並完成 requeue-PI trigger；
- PS7331 的 runtime identity mismatch 可以重現；
- cleanup 後的 state 可被後續合法路徑消費；
- kernel layout、allocator／stack reuse 與 security policy 仍符合後續
  memory stage；
- root delivery stage 不依賴另一套 kernel／SELinux／KernelSU 假設。

目前只有第一條中的 kernel source 部分成立。其餘不是「偏移還沒算好」的
單一問題，而是尚未建立的 runtime／memory／privilege 證據鏈。

## 4. 安全研究邊界

以下操作因會直接把研究推進到 kernel exploitation／root delivery，本輪不
執行：

- 編譯或改寫 Emerald exploit；
- 在 PS7331 執行 PI-requeue race；
- 使用 kernel memory read/write、fops／pipe corruption 或 credential／
  SELinux 修改路徑；
- 推送並執行 root payload、KernelSU loader 或未知 native binary。

仍可進行的低風險工作是：

1. 讀取更多已可存取的 Fire native／framework artifacts；
2. 做不執行 exploit 的 source／CFG／symbol 對照；
3. 建立 host-only state machine，明確標記 D0–D4 證據門檻；
4. 若取得官方修補 source，做 PS7331 與修補版的語意差異驗證。

## 5. Evidence references

- [Emerald README](https://github.com/datfooldive/ghostlock-emerald/blob/main/README.md)
- [Emerald Makefile](https://github.com/datfooldive/ghostlock-emerald/blob/main/Makefile)
- [Emerald main.c](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/core/main.c)
- [Emerald target.h](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/core/target.h)
- [Emerald offsets metadata](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/devices/emerald/offsets.h)
- `findings/phase-5ce-ghostlock-emerald-compatibility.md`
- `findings/phase-5cp-ps7331-proxy-context-audit.md`
- `findings/phase-5cr-fire-libc-futex-analysis.md`
- `findings/phase-5cs-fire-art-futex-analysis.md`
