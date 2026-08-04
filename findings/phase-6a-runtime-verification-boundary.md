# Phase 6A — runtime verification boundary

本文件只定義安全的觀測問題，不執行 stock-device futex trigger、race、
crash、kernel memory operation 或 root payload。

## 目前可開始的部分

### A. Userspace caller attribution

先要取得「哪個已安裝 native component 呼叫 requeue-PI」的可歸因證據。Phase
5DC 在 source tree 與既有 native scan 中尚未建立這個 caller；selftest source
不能代替 installed runtime。

### B. Lab-only identity model

可在不接觸平板的 host-only model 中表示：

```text
stored waiter task  ───────────────┐
                                   ├─ proxy API task argument
requeue execution context/current ─┘
```

模型只驗證 source dataflow 與 observation schema，不產生 syscall arguments、
kernel addresses、race schedule 或 exploit payload。

### C. Runtime evidence schema

若在隔離且可觀測的 research kernel／emulator 中取得資料，至少要保存：

- source/build identity；
- caller component與操作名稱；
- waiter task identity與執行 context identity（以 lab instrumentation 定義）；
- proxy return domain；
- cleanup branch execution；
- cleanup 前後的非敏感 state summary；
- 是否有 later consumer；
- 完整 safety/rollback metadata。

結果必須標為 `LAB_ONLY`，不能直接宣稱 PS7331 stock runtime 已驗證。

## 明確不執行

- 在平板上呼叫 `FUTEX_WAIT_REQUEUE_PI` 或 `FUTEX_CMP_REQUEUE_PI`；
- 建立 race、故意觸發 kernel crash 或製造 deadlock；
- 開啟未授權 kernel tracing、讀取 kernel memory 或推導可利用地址；
- 編譯、推送或執行 root/exploit payload；
- 變更 boot、system、vendor、SELinux 或 partition state。

## Phase 6A gate

| Gate | Current status |
|---|---|
| Exact PS7331 source/Image provenance | 已證實 |
| Requeue-PI source path | 已證實 |
| Installed Fire userspace caller | 待驗證；Phase 5DC bounded negative observation |
| Same-execution proxy identity mismatch | 未觀察 |
| Cleanup residue/later consumer | 未觀察 |
| Memory effect/privilege transition | 未證實；因風險拒絕 |

目前最有資訊量且不擴大風險的下一步，是擴充離線 Fire native inventory與
policy/source mapping，而不是直接在 stock tablet 上追 race。
