# Phase 6C：PS7331 唯讀 runtime boundary capture

## 證據範圍

測試 ID：`PHASE6C-RO-CAPTURE-20260804-01`
設備序號：已保留於本機原始輸出，報告不公開重複列出
時間：2026-08-04 14:07:03–14:07:05 UTC
原始資料：`adb/phase6c/PHASE6C-RO-CAPTURE-20260804-01/`

collector 只執行 getprop、id、getenforce、kernel/proc metadata、HOME/package
dump 與 settings read。沒有 package、settings、foreground、reboot、futex、
device-node 或 kernel-memory mutation。

## 觀察

| 項目 | 觀察 | 分類 |
|---|---|---|
| Build fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | 已證實 |
| Model/device | `KFTRWI`／`trona` | 已證實 |
| Kernel | `4.4.146+`, AArch64, `#1 SMP PREEMPT`, 2025-05-03 | 已證實 |
| SELinux | Enforcing | 已證實 |
| Verified boot | `green`; `ro.boot.unlocked_kernel=false` | 已證實 |
| Shell identity | UID 2000, `u:r:shell:s0` | 已證實 |
| `/proc/kallsyms` | shell denied | 已證實（shell boundary） |
| `/proc/slabinfo` | not present | 已證實（shell boundary） |
| `randomize_va_space` | shell denied | 已證實（shell boundary） |
| `user_setup_complete` | `0` | 已證實（snapshot only） |
| `device_provisioned` | `1` | 已證實（snapshot only） |

## HOME 狀態注意事項

本次唯讀 snapshot 的 `resolve-activity` 首項是：

```text
priority=100 ... isDefault=true
com.amazon.kindle.otter.oobe/.OobeHomeActivity
```

候選集中同時可見 Fire Launcher（priority 50）、Microsoft Launcher（effective
priority 0）、Phase 4 alias probe（effective priority 0）與 Settings fallback
（priority -1000）。`mResumedActivity`／`mCurrentFocus` 當時是 Microsoft
Launcher；Activity dump 也保留 Fire Launcher task。這表示 resolver snapshot、
目前 foreground task 與已建立 task 可以不同，不能把其中一項直接當成 GhostLock
或正式 HOME replacement 證據。

`user_setup_complete=0` 是本次 snapshot 的重要條件；它使 OOBE candidate 成為
首項。collector 沒有寫入這個值，也沒有嘗試修正或切換前景，因此不能判斷其
形成時間或將其歸因於本輪工作。

## 原始雜湊

- capture SHA manifest：
  `c2f8469786d2bb8a1acb8f39eb34ae188dd910f03fdc9e3c98f38171d028a2a8`
- protocol JSON：
  `ef716385fd0e7eb00effdb2804bf12e26c194abe1db3f5a25c7941ffdd957206`
- protocol matrix：
  `8f1bf8c40b6cf3c2ea88c2ccdd7d8f30bae51b868908262cbfa6d15e4d11951d`

## 安全結論

本次 capture 沒有提供 `FUTEX_CMP_REQUEUE_PI` runtime return、proxy waiter、
identity mismatch、cleanup residue、panic 或 privilege transition 證據。這些
仍為未知；不應把本次唯讀資料宣稱為 exploit validation。
