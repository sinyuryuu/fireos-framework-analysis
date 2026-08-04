# Phase 5DE — non-kernel PS7331 userspace futex source

日期：2026-08-04

本輪對官方 PS7331 source 的非 kernel 部分做文字掃描，專門區分普通
futex direct syscall 與 PI/requeue-PI operation。沒有編譯或執行 source，
沒有接觸裝置、呼叫 syscall、建立 race、讀寫 kernel memory 或產生 payload。

## 結果

排除所有 `kernel/**` 與 `**/kernel/**` 後：

- 只找到 2 個 source files、26 rows；
- 8 rows 是 direct `syscall(__NR_futex, ...)`；
- 只出現 `FUTEX_WAIT`／`FUTEX_WAKE`；
- PI calls：0；
- requeue-PI calls：0。

命中的檔案是：

- `fireos/fireos/external/glib/glib/gbitlock.c`；
- `fireos/fireos/external/glib/glib/gthread-posix.c`。

## 直接觀察

`gbitlock.c:76`、`:93` 使用 `syscall(__NR_futex, ...)`，operation 分別是
普通 `FUTEX_WAIT` 與 `FUTEX_WAKE`。

`gthread-posix.c:1308-1324` 對 mutex 使用普通 WAIT/WAKE；
`:1390-1437` 對 condition variable 使用普通 WAIT/WAKE。這些 operation
不會直接進入 `FUTEX_WAIT_REQUEUE_PI`／`FUTEX_CMP_REQUEUE_PI` dispatch。

`glib/Makefile.am:100-109,214-216` 將 `gbitlock.c` 與 POSIX thread source
列入 GLib build inputs；`gio/inotify/Android.mk` 也引用 Fire GLib include
與 Android integration files。但該 `Android.mk` 參考的
`fireos/external/glib/glib/android.mk`、`gmodule/android.mk` 與
`antiAndroidConfig.h` 在目前擷取的 source roots 中沒有對應檔案，所以這
部分只能標為 **build-intent evidence**，不能直接證明目前 PS7331 system
image 內有 `libglib` 或使用該 caller。

## 判定

- **已證實：** PS7331 source package 中存在 ordinary direct futex userspace
  source；本輪非 kernel 搜尋沒有 PI/requeue-PI call。
- **高可信推論：** Fire source package 的 ordinary GLib synchronization
  path 不能單獨作為 GhostLock proxy-waiter 入口證據。
- **待驗證：**這些 source 是否被編入目前裝置上的哪個 package、Android
  integration include 缺失是否由外部 build layer 補上、未擷取
  native library 的 indirect/numeric syscall、以及 stock runtime 實際操作。
- **已排除／不支持：**把 `syscall(__NR_futex, FUTEX_WAIT/WAKE)` 當成
  requeue-PI caller。
- **因風險拒絕測試：**將 GLib source 編譯、推送到平板或改寫成 PI/requeue-
  PI trigger；這會直接進入 futex runtime exploit path。

## 證據輸出

- 完整 rows：`artifacts/phase5/phase5de-userspace-futex-source-audit-20260804-03/userspace-futex-source-hits.csv`
- Summary：`artifacts/phase5/phase5de-userspace-futex-source-audit-20260804-03/summary.json`
- 公開摘要：`output/tables/phase5de-userspace-futex-summary.csv`
- 重現腳本：`tools/scripts/audit_phase5de_userspace_futex_source.py`

這項結果把 userspace evidence 從「沒有 named caller」進一步縮小為：在
目前可取得的 PS7331 非 kernel source 中，明確看到的是 ordinary WAIT/WAKE，
而非 requeue-PI。
