# Phase 5BN：GhostLock 最新證據與升級判定

日期：2026-08-04
範圍：CVE-2026-43499、Fire HD 10 KFTRWI/trona、PS7330 與 PS7331 的 source／binary provenance

## 結論

### 已證實

1. 上游修補的語意是將 `remove_waiter()` 的 cleanup 與 priority-chain task
   從 `current` 改為 `waiter->task`。上游 patch 明確指出該路徑與
   `rt_mutex_start_proxy_lock()`、`futex_requeue()` 的 proxy-lock rollback
   有關。[Linux stable patch](https://www.spinics.net/lists/stable/msg940814.html)
2. 獨立重跑的 host-only checker 結果仍為：PS7330 source family 與 PS7331
   build-selected source 都是 `PRE_FIX_CURRENT_TASK_CLEANUP`；固定參考是
   `FIXED_WAITER_TASK_CLEANUP`。
3. PS7330 source member hash 為
   `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345`；
   PS7331 build-selected member hash 為
   `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`；
   fixed reference hash 為
   `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`。
4. 官方 PS7330／PS7331 source URL 均可取得，且 HTTP metadata 與既有
   provenance 一致；這不等於 signed kernel binary。
5. 現有 PS7331 inspected Image 亦保存了 old-pattern observations，但它仍是
   相鄰版本，不是目前已安裝的 PS7330 signed Image。

### 高可信推論

- 以 source 與已檢查的 PS7331 Image pattern 而言，PS7331 沒有顯示已套用
  GhostLock 的 `waiter->task` 修補；因此不應為了 GhostLock 單獨升級。
- PS7330 的 source/config evidence 使它成為有力的 source-level candidate，
  但不能提升為 exact signed-binary vulnerability proof，也不能推出可用
  kernel offset、KASLR slide 或 root payload。
- PS7331 仍可能包含其他一般安全更新；該問題與 GhostLock remediation 必須
  分開判定。PS7331 完整 OTA 不是 standalone `boot.img` 的等價替換。

### 待驗證

- PS7330 signed boot block 是否有未公開 backport；目前 shell 讀取被拒絕。
- PS7330 compiled `remove_waiter()`、`task_struct` 編譯後欄位、KASLR 與
  Android SELinux／post-exploitation 行為。
- PS7331 其他 vendor/framework 修補的完整 security delta。

### 已排除

- 以 PS7331 `boot.img` 取代 PS7330 作為 GhostLock target。
- 以 source-derived layout 或 Android boot header 推導可用 runtime offset。
- 以「2026 年公開 CVE」推論 PS7331 必定未修補或 PS7330 必定可利用。
- 將 `CVE-2026-43503` 或 `CVE-2026-3499` 當作 GhostLock 路徑。

### 因風險拒絕測試

本輪沒有執行 futex race、kernel memory 操作、root payload、未知 ioctl、
MTK BROM/DA、preloader/LK、fastboot、OTA、boot image 或分割區寫入。也沒有
升級裝置；目前設備仍維持 PS7330。

## 證據

| Evidence ID | 檔案 | 觀察 | 判定 |
|---|---|---|---|
| `P5BN-MARKER-001` | `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/summary.json` | 三個 source input 的 marker classification | Confirmed，host-only |
| `P5BN-MARKER-002` | `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/comparison.csv` | PS7330／PS7331 均為 pre-fix；fixed reference 為 waiter-task | Confirmed，source scope |
| `P5BN-SOURCE-001` | `artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv` | PS7330 exact source member provenance | Confirmed，source scope |
| `P5BN-BINARY-001` | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | PS7331 inspected Image 的 current-task／proxy observations | Confirmed，inspected Image scope |
| `P5BN-URL-001` | `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/source-http-headers.txt` | 官方 source URL HTTP 200、長度與 ETag | Confirmed，availability scope |
| `P5BN-BOOT-001` | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | PS7330 boot pull denied | Confirmed，access scope |

## 升級決策

| 目的 | 判定 |
|---|---|
| GhostLock remediation | 不支持；現有 PS7331 source／Image evidence 仍是 pre-fix 方向 |
| 一般 Fire OS security update | 可作獨立 host-only研究候選；未執行安裝 |
| standalone PS7331 boot 寫入 | 拒絕；不是完整 OTA，也未證明 boot-chain 相容 |
| 目前 GhostLock live root test | 不可責任地執行；缺少 exact PS7330 signed target 與可靠 recovery |

## 可重現方式

```sh
python3 tools/scripts/compare_phase5bj_ghostlock_fix.py \\
  --ps7330 artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/4.4/kernel/locking/rtmutex.c \\
  --ps7331 artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \\
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \\
  --output artifacts/phase5/phase5bn-ghostlock-marker-recheck-YYYYMMDD-NN
```

Checker 是 host-only，拒絕覆寫既有 output，不連接裝置，不輸出 address、offset
或 payload。

