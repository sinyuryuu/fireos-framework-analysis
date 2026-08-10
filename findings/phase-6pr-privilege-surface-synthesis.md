# Phase 6PR — 全域特權面整合摘要

日期：2026-08-10

## 研究範圍

本摘要把目前 PS7331／Fire OS 7 corpus 中與「取得更高權限後可控制
package、component、user、HOME、process、driver 或 boot state」相關的證據
放在同一個判定框架。它不把 Launcher 當成唯一 sink，也不把 source marker、
SELinux allow、service name 或 manifest capability 當成提權證明。

所有結果分為：**已證實、強證據、待驗證、已排除、因風險拒絕測試**。

## Executive summary

### 已證實的低權限→高權限代理

1. **AmazonActivityManager tx1 / `preWarmApplicationForUser()`**
   - 無權限 ordinary APK 已在實機取得 `amazonactivitymanager` Binder。
   - `APP_PREWARM` permission check 的結果在保存的 bytecode path 沒有被消費，
     之後清除 calling identity 並呼叫 `startProcessLocked(..., "prewarm", ...)`。
   - 實機觀察到指定的臨時 target process 出現，完成後移除兩個測試 APK。
   - 這是 **Confirmed process/resource confused deputy**，不是 root、不是 HOME
     writer，也沒有 Fire package state sink。

2. **AmazonUserManager tx4 / `setUserSetupComplete(UserInfo)`**
   - 無權限 ordinary APK 已在實機令 system service 寫入
     `user_setup_complete=1` 和 `tv_user_setup_complete=1`，然後成功還原。
   - 這是 **Confirmed settings-state confused deputy**；固定寫入 `1`，目前沒有
     證據能由此取得 system UID、root、package state 或 HOME 控制。

### 高影響但未形成低權限提權的路徑

- **KFT tx3**：實際能 enable Tahoe、disable Fire/Launcher3，但 User 10／User 0
  ordinary-app 實測分別在 cross-user／component gate 被 PMS 擋下；分類為
  **Strong static deputy review point, not an exploit finding**。
- **DPM persistent preferred／profile owner**：是可信任的 owner/admin writer；
  shell/ordinary relay 沒有被證實。
- **OTA/recovery、OOBE、`/init` policy loader**：具備高權限 capability 或
  lifecycle writer，但 caller、驗證、user scope 或 recovery handoff 尚未形成
  低權限可達鏈；live replay 會跨越高風險邊界，已拒絕。
- **CMDQ／ION／GED／GhostLock**：有 source 或 device surface 候選，但沒有
  runtime memory effect、credential change、system UID transition 或 package/HOME
  sink 證據。

## 特權路徑矩陣

完整機器可讀矩陣：`output/tables/phase6pr-privilege-route-matrix.csv`

| 路徑 | 低權限 caller 實證 | 高權限 sink | 目前判定 | 是否值得重跑 |
|---|---|---|---|---|
| `amazonactivitymanager` tx1 prewarm | ordinary APK UID 10198 | system-identity process start | **Confirmed, bounded deputy** | 否；已有成功與 rollback 證據 |
| `amazonusermanagerservice` tx4 setup state | ordinary APK UID 10223 | secure settings writes | **Confirmed, bounded deputy** | 否；已有成功與 rollback 證據 |
| KFT tx3 `enableKftLauncher` | ordinary APK reached service; PMS rejected | Tahoe/Fire/Launcher3 state setters | **Strong static; runtime mutation disproved** | 否，除非 build/caller precondition 改變 |
| DPM persistent preferred | only owner/admin path | PMS trusted preferred writer | **Trusted path** | 否；不可建立 Device Owner |
| Amazon PackageManager tx1–11 | selected queries/metadata only | no formal HOME/component setter in bounded interface | **Direct route disproved** | 否 |
| OTA/update-binary/recovery | no low-priv caller | partition/block image writer | **Static capability; reachability unknown** | 否；禁止執行 OTA/recovery |
| OOBE/BootAfterSystemOTA | trusted lifecycle only | component/setup-state writer | **Lifecycle candidate; replay rejected** | 否；需合法 OTA lifecycle evidence |
| `/init` rootable policy branch | no writable property/path proven | SELinux policy selection | **Static candidate only** | 否；禁止 property/boot/SELinux mutation |
| GhostLock futex/rtmutex | source path only | no observed memory/credential sink | **Runtime exploitability unproven** | 否；不做 race/DoS/exploit |
| CMDQ secure metadata | source OOB candidate | possible driver/secure path | **Source-only candidate** | 否；不送非零 ioctl/async payload |
| ION | policy/node metadata; no live caller | memory allocator/import path | **Reachability/effect unknown** | 只做 host provenance，不做 ioctl |
| GED `/proc/ged` | shell query telemetry | query/debug surface | **Confirmed telemetry only** | 否；higher-impact ioctl 不测试 |

## 主要證據索引

| Evidence | 檔案 | 結論 |
|---|---|---|
| P4-ER-01 | `findings/phase-6er-amazon-prewarm-confused-deputy.md`；`adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/` | ordinary app → process prewarm deputy，**Confirmed** |
| F-108 | `findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md`；`adb/phase6gv/PHASE6GV-USERMANAGER-TX4-20260807-02/` | ordinary app → setup settings deputy，**Confirmed** |
| KFT-TX3-STATIC | `findings/phase-6pr-kft-tx3-authorization-closure.md`；`artifacts/phase6pr-kft-tx3-authz-20260810-06/` | writer 與缺少 method-local check，**Confirmed static / exploit Unknown** |
| KFT-TX3-FJ | `adb/phase6fj/PHASE6FJ-USER10-TX3-20260807-01/` | cross-user downstream gate，**Confirmed** |
| KFT-TX3-FK | `adb/phase6fk/PHASE6FK-USER0-TX3-20260807-01/` | component-state downstream gate，**Confirmed** |
| IPC-NEGATIVE | `findings/phase-6bj-binder-caller-closure.md`；`findings/phase-6mt-amazon-ipc-candidate-closure.md` | 未找到 User-0 任意 package/HOME writer，**bounded negative** |
| OTA/INIT | `findings/phase-6p-callback-and-ota-audit.md`；`findings/phase-6kt-recovery-verifier-provenance.md` | high-impact static capability，低權限 caller 未閉合 |
| DRIVER/KERNEL | `findings/phase-6np-ion-and-control-surface-closure.md`；`findings/phase-6ha-p5-driver-reaudit-ged-cmdq-boundary.md`；`findings/phase-5cy-ps7331-runtime-observation-boundary.md` | source/runtime candidate，無 LPE 證據 |

## 對「拿到權限就能關閉」的精確回答

概念上，system UID／root／受信任 Device Owner 確實能改變更多 package 或
component state；但目前研究沒有證明任何普通 app 或 shell 能取得那些身份。
已證實的兩個 confused deputy 只分別提供 process prewarm 與 setup settings
寫入，不能把它們升格為 system UID、root 或 Fire Launcher disable capability。

因此目前最準確的總結是：

```text
Confirmed ordinary-app deputies
  ≠ system UID acquisition
  ≠ root
  ≠ arbitrary PackageManager writer
  ≠ formal HOME replacement
```

## 下一個最小安全研究目標

若繼續，優先做主機端而非實機 exploit：

1. 審查 `com.android.vending` 在保存 package dump 中持有
   `CHANGE_COMPONENT_ENABLED_STATE` 的來源、簽章、privileged/app 分區與程式碼
   caller；只做 manifest／code provenance，不 grant/revoke permission，也不呼叫
   package setter。
2. 完成未索引 Amazon Binder interface 的 caller→permission→identity→sink
   表，但維持「不猜 transaction、不送未知 Binder」規則。
3. 對 OTA/OOBE、CMDQ/ION、GhostLock 只補 provenance 或 lab-only model；不在
   stock device 觸發 race、ioctl、recovery 或 partition path。

若這三項仍沒有新的 package/HOME/credential/system-UID sink，研究可合理收斂為：
「目前存在兩個受限的 ordinary-app confused deputies，但沒有已證實的低權限
提權至 root/system；正式 HOME replacement 仍不可行。」
