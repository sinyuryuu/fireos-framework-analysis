# Phase 5AR/5AS evidence index

日期：2026-08-04

本索引只收錄本輪新增的 PS7331 靜態編譯證據，以及使用者提供的
Amazon source-notice 備份頁審核。原始 boot/Image、重建 ELF 與大型 source
archive 不在本次 commit 中重複保存；其 SHA-256 及來源記錄在下列 metadata
與既有 Phase 5 evidence index。

| Evidence ID | Source | File | SHA-256 | Test ID / time | Command or method | Observed result | Interpretation | Confidence | Related hypothesis |
|---|---|---|---|---|---|---|---|---|---|
| `P5AR-001` | PS7331 parser provenance | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/parser-metadata.md` | recorded input hashes in file | `PHASE5AR-STATIC-20260804-01` / 2026-08-04 | host-only `vmlinux-to-elf` reconstruction followed by `nm`/`objdump` inspection | PS7331 Image, boot image and reconstructed ELF hashes are recorded; no ELF execution or device I/O | establishes reproducible provenance for the compiled review | 已證實 | PS7331 compiled evidence is target-specific |
| `P5AR-002` | symbol extraction | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/symbol-presence.csv` | `c82b1881cd62d4519563727968e25bb946615c344de3c3293a013b3cd2788ea0` | `PHASE5AR-STATIC-20260804-01` / 2026-08-04 | host `nm -n` over reconstructed ELF | `remove_waiter`, `rt_mutex_start_proxy_lock`, `rt_mutex_finish_proxy_lock` and `futex_requeue` are present | PS7331 reconstructed Image contains the relevant symbol family | 已證實 | GhostLock code-path presence |
| `P5AR-003` | instruction-pattern extraction | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d` | `PHASE5AR-STATIC-20260804-01` / 2026-08-04 | host `objdump` over `remove_waiter` | `remove_waiter` reads `SP_EL0` and clears a field through the same current-task register | compiled pattern maps to old `current->pi_blocked_on = NULL` behavior | 已證實（inspected function scope） | upstream fix status in PS7331 |
| `P5AR-004` | proxy path extraction | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d` | `PHASE5AR-STATIC-20260804-01` / 2026-08-04 | host `objdump` over `rt_mutex_start_proxy_lock` | proxy error path contains a call to `remove_waiter` | compiled proxy relationship required by the root-cause review is present | 已證實（inspected function scope） | GhostLock root-cause pattern |
| `P5AR-005` | analyzer summary | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | `eede2b264a6a3a9934cc09b374ae9162e4196d2bdf68a07d6cd5fe2156148f2b2` | `PHASE5AR-STATIC-20260804-01` / 2026-08-04 | `analyze_phase5ar_ps7331_rtmutex_binary.py` | summary records requested/present symbols, sanitized patterns, source hashes and `device_execution=false` | independently records the scope and safety boundary of the analyzer | 已證實 | evidence reproducibility |
| `P5AR-006` | exact current-device source review | `findings/phase-5n-exact-source-ghostlock-review.md` | tracked file hash at commit `f83a3b5` | `PHASE5N` / prior capture | exact Amazon 7.3.3.0 source extraction and normalized source comparison | source `rtmutex.c` has the old current-based pattern and futex/rtmutex config is enabled | PS7330 source/config remains a strong candidate, not signed-binary proof | 高可信推論 | PS7330 applicability |
| `P5AR-007` | live symbol access boundary | `findings/phase-5ap-evidence-index.md` (`P5AP-002`, `P5AP-003`) | see referenced capture manifest | `PHASE5AP` / prior capture | read-only ADB procfs capture | shell cannot read `/proc/kallsyms` or `kptr_restrict` | exact installed PS7330 compiled function cannot be confirmed through that shell path | 已證實 | PS7330 binary boundary |
| `P5AS-001` | source-notice archive metadata | `artifacts/phase5/technically-competent-source-notice-review-20260804-01/metadata.md` | retrieved HTML `fa0e0c8639549d61ab4b59a6fb34b99da5a3ce690af668c59d026fe1d97c9e0d` | `PHASE5AS-SOURCE-NOTICE-20260804-01` / 2026-08-04 | retrieve and inspect supplied backup page | page snapshot marked `scraped 2025-02-26` lists the exact 11th-gen `7.3.3.0` archive and no 11th-gen `7.3.3.1` entry | useful historical provenance; absence is not proof that a later archive never existed | 已證實（page scope） | 7.3.3.1 source availability |
| `P5AS-002` | source-notice review | `findings/phase-5as-source-notice-archive-review.md` | recorded with commit | `PHASE5AS-SOURCE-NOTICE-20260804-01` / 2026-08-04 | compare archive listing with device generation and official software-version information | 7.3.3.0 is the exact public source link for the current PS7330 family; 7.3.3.1 software listing and source-notice listing are separate facts | do not treat the backup page as 7.3.3.1 kernel-source evidence | 已證實（page scope） | source provenance |
| `P5AR-008` | safety boundary | `findings/phase-5ar-ps7331-compiled-rtmutex-review.md` | recorded with commit | `PHASE5AR-STATIC-20260804-01` / 2026-08-04 | host-only analysis review | no futex race, payload, ioctl, kernel memory access, bootloader or partition operation was performed | result is patch-status evidence only, not a root result | 因風險拒絕測試 | safety |

## Reproduction notes

The analyzer is [`tools/scripts/analyze_phase5ar_ps7331_rtmutex_binary.py`](../tools/scripts/analyze_phase5ar_ps7331_rtmutex_binary.py).
It requires a reconstructed analysis ELF, refuses to overwrite an existing output,
supports `--dry-run`, invokes only host `nm`/`objdump`, and deliberately omits
absolute addresses, branch targets, gadget data and exploit offsets.
