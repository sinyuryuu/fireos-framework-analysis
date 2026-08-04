# Step 4 Runtime Harness：安全閘門結果

## 狀態

**因風險拒絕測試。** 本階段沒有在 stock PS7331 上編譯、push 或執行
`FUTEX_CMP_REQUEUE_PI`。

## 原因

該 syscall 是本研究所分析的 proxy-PI 可疑路徑入口。即使限制為單執行緒、
單次呼叫與合法 user-space 位址，也不能從使用者空間保證核心不建立或修改
PI/requeue 狀態；而原始目標明確包含後續 race、memory effect 與暫時 root。
因此「無 race」的測試前提不足以把它視為無害 smoke test。

## 已完成的替代證據

- Phase 6A untrusted app 已驗證普通 private PI lock/unlock syscall path 可由
  untrusted app 執行；該測試沒有 requeue、proxy waiter、thread 或 race。
- Phase 6B 唯讀邊界顯示 shell 無法讀取 `/proc/kallsyms`，`/proc/slabinfo`
  不存在，且 KASLR sysctl 讀取被拒絕。
- 主機端 source/config model 確認 requeue waiter 的 inspected storage 是
  kernel stack，而不是普通 SLUB waiter cache。

## 不會執行的操作

- device-side `FUTEX_CMP_REQUEUE_PI` harness；
- `FUTEX_WAIT_REQUEUE_PI`／`FUTEX_CMP_REQUEUE_PI` 配對 waiter；
- 雙執行緒或競態排程控制；
- heap/ION/pipe shaping 或 spray；
- kernel panic、memory read/write、shellcode、privilege escalation。

## 可繼續的安全工作

1. 在 host-only 環境整理 AArch64 record layouts、SLUB source model 與 exact
   source call graph。
2. 建立不含 requeue/race/memory-corruption 邏輯的 LAB_ONLY kernel build
   說明與工具鏈記錄。
3. 將任何 device-side dynamic trigger 列為需要獨立風險審查的項目，不把
   source reachability 寫成 runtime exploitability。
