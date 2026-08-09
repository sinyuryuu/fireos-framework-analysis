# Phase 6NE evidence index

| Evidence ID | Source file | SHA-256 | Observed result | Confidence |
|---|---|---|---|---|
| `6NE-CACHE-001` | `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv` | 見 artifact `sha256sums.txt` | `PerformBlockImageUpdate` 在 `0x409cb4`、`0x409cdc` 呼叫 `CacheSizeCheck`；`CacheSizeCheck` 在 `0x414730` 呼叫 `MakeFreeSpaceOnCache` | Confirmed |
| `6NE-CACHE-002` | `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv` | 見 artifact `sha256sums.txt` | cache helper 的 sign-bit error branch 與兩個 caller 的 `cbz w0` 分支已保存 | Confirmed |
| `6NE-CACHE-003` | `artifacts/phase6ne-updater-cache-flow-20260810-03/summary.json` | 見 artifact `sha256sums.txt` | host-only、未接觸設備、未執行 updater、未寫入分割區 | Confirmed |
| `6NE-CACHE-004` | `findings/phase-6mm-updater-blockimage-closure.md` | `f0caa7e810d02f0022180371e0b564f2cef13cd19ed7320fde107a8073d58601` | `MakeFreeSpaceOnCache → __readlink_chk` 已有 bounded static evidence | Strong evidence |
| `6NE-SAFETY-001` | `tools/scripts/audit_phase6ne_updater_cache_flow.py` | 由公開 artifact manifest 驗證 | 只讀輸入；支援 `--dry-run`；拒絕覆寫輸出 | Confirmed |

本索引不把 updater 的高權限 capability 誤標為 shell/ordinary-app reachability。
