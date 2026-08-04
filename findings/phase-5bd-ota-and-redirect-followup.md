# Phase 5BD：PS7331 OTA 邊界與 PendingIntent redirect follow-up

日期：2026-08-04

本階段延續 GhostLock／PS7331 研究，只做官方 OTA metadata 的主機端檢查、
既有 kernel/source 證據整理，以及一次已由研究者在 Settings 授權的
Accessibility PendingIntent foreground redirect 測量。

## Executive result

### 已證實

1. 本地保存的 PS7331 package 是正式的 `trona`、Fire OS 7.3.3.1、Android
   9/API 28、security patch `2024-08-01` full block OTA，archive SHA-256 為
   `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`。

2. OTA updater script 不只更新 system/vendor/boot，也會寫入
   `preloader`、`lk`、`tee1`、`tee2`、`spmfw`、`sspm_1` 與三個 camera VPU
   分割區。這證明單獨寫入 `boot.img` 不是該 package 的等價升級路徑。

3. 現在裝置仍是 PS7330.4104N、ADB `device`、HOME resolver
   `com.amazon.firelauncher/.Launcher`。本階段沒有 OTA、boot image 或分割區
   寫入。

4. 已授權的 PendingIntent redirect 變體完成 30 次測量：service dispatch
   30/30，但 alias Activity 成為 resumed/focused 為 0/30；Fire Launcher
   仍是正式 HOME 與取樣時的前景。這不是可用的 HOME replacement。

5. Phase 5BC 的 exact PS7331 build-selected `rtmutex.c` source semantics
   與 PS7331 reconstructed signed Image review 都仍呈現 GhostLock 的舊式
   `current->pi_blocked_on` cleanup pattern；因此尚未找到足以支持升級的
   GhostLock remediation 證據。

### 高可信推論

- 7.3.3.1 可以作為「完整官方 OTA 的一般安全更新 A/B 研究候選」，但不應
  把其中的 `boot.img` 單獨寫入 PS7330。該 OTA 同時改動 boot chain 與多個
  vendor/firmware 分割區，且目前沒有在本階段建立可接受的 rollback/recovery
  證據。
- 僅為 GhostLock 升級目前沒有充分理由：相鄰 PS7331 Image 與 source/config
  evidence 沒有顯示 `waiter->task` 修補。這不是「PS7331 沒有任何安全修補」的
  廣泛宣稱，而是針對 GhostLock 的證據判定。
- Accessibility route 目前最多是 foreground redirect attempt；即使 PendingIntent
  呼叫成功，也不改變 PackageManager HOME state，且本機 30/30 未取得穩定前景。

### 待驗證

- exact PS7330 signed kernel Image 的 `remove_waiter()` binary semantics；
  shell 無法讀取已安裝 boot block。
- PS7331 與 PS7330 的所有非 GhostLock 安全修補差異；本階段只分析 OTA
  identity、focus config、rtmutex/source boundary，沒有宣稱完整 security
  audit。
- 若日後要做升級 A/B，需另建完整官方 OTA 的資料備份、供電、驗證、可回復
  路徑與風險核准報告；本報告不構成升級執行授權。

### 已排除／不採用

- 把 OTA 中的 `boot.img` 當成可獨立安全刷入的升級。
- 把 PendingIntent dispatch log 當成第三方已成為 HOME。
- 把短暫 alias window/task presence 當成穩定 foreground handoff。
- 重跑已失敗且 profile 不匹配的 mtk-su payload。

### 因風險拒絕測試

- 完整 OTA sideload／recovery 安裝。
- fastboot／BROM／DA／preloader／LK 操作。
- boot、system、vendor、TEE 或 userdata 寫入。
- futex race、GhostLock reproducer、kernel memory access、root payload、
  未知 ioctl 或 SELinux 修改。

## OTA identity and write scope

| Field | Observation | Classification |
|---|---|---|
| Product | `trona` | 已證實 |
| Target build | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | 已證實 |
| Incremental | `0031575863172` | 已證實 |
| OTA type | `BLOCK`; `binary_type=full` | 已證實 |
| Post security patch | `2024-08-01` | 已證實 |
| Current device | PS7330.4104N / `2024-02-01` | 已證實 |
| Updater write scope | system, vendor, boot, preloader, lk, tee1/tee2, spmfw, sspm_1, cam_vpu1/2/3 | 已證實 |

## Redirect experiment

The exact raw test package is
[`PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01`](../adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/).
The formal resolver and device state were unchanged. The test did not disable
the Accessibility service because it was already user-enabled before the test;
only the visible research toggle was restored to its baseline off state.

## Decision

Do not upgrade to PS7331 solely to pursue GhostLock. Retain the official full
OTA as a host-only adjacent-version artifact. Any future general-security A/B
upgrade must be treated as a separate, high-risk full-OTA operation; do not
write its standalone boot image.
