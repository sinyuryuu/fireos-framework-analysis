# Phase 5CU：PS7331 seccomp 與 futex userspace reachability 邊界

日期：2026-08-04
裝置：Fire HD 10／PS7331／`G001LT0511550CFT`

## Executive result

本輪新增的是 policy boundary，不是 exploit trigger：

1. `system_server`、Microsoft Launcher、SystemUI、OTA service 與本輪測試
   APK 的 `/proc/<pid>/status` 都顯示 `Seccomp: 2`。
2. `adbd` 在同一 snapshot 顯示 `Seccomp: 0`，但 UID 仍是 2000、capability
   為零；這不是 root，也不能推導其他程序可以繞過 policy。
3. 可讀取的 `mediaextractor`、`mediacodec` 與 vendor `configstore` policy
   包含 `futex: 1`。這只代表這些 service policy 對 futex syscall 有允許
   規則，沒有證明普通 app domain 使用 PI requeue。
4. 可見的 policy 目錄沒有提供普通 app 的完整 policy 檔；
   `libandroid_runtime.so` 的 seccomp setup 字串只證明 policy 建立程式存在。

因此，userspace gate 更新為：

```text
kernel futex/rtmutex source path                 confirmed
ordinary app is under seccomp filtering          confirmed
service policy contains generic futex allow      confirmed, service scope
ordinary app futex policy contents                unknown
FUTEX_WAIT_REQUEUE_PI reached on Fire            unobserved
FUTEX_CMP_REQUEUE_PI reached on Fire              unobserved
runtime identity mismatch                         unobserved
root / controlled memory effect                   unproven, not executed
```

## 1. Device and capture boundary

本輪只讀取：

- `getprop` build identity；
- seccomp policy 路徑與檔案 listing；
- selected process `/proc/<pid>/status`；
- `/system/etc/seccomp_policy` 與 `/vendor/etc/seccomp_policy` 中可讀的
  policy files。

沒有呼叫 futex、沒有送出任何 syscall operation probe、沒有修改 seccomp／
SELinux、沒有執行 native code，也沒有重開機。

原始資料：

`adb/phase5/PHASE5CT-SECCOMP-20260804-01/`

## 2. Process-level evidence

| Process | UID | Seccomp | Interpretation |
|---|---:|---:|---|
| `system_server` | 1000 | 2 | filtered system process |
| `com.microsoft.launcher` | 10178 | 2 | filtered ordinary app process |
| `org.fireosresearch.phase4.redirect` | 10189 | 2 | filtered research app process |
| `org.fireosresearch.phase4.alias` | 10190 | 2 | filtered research app process |
| `com.android.systemui` | 10036 | 2 | filtered SystemUI process |
| `com.amazon.device.software.ota` | 10017 | 2 | filtered OTA process |
| `adbd` | 2000 | 0 | separate ADB daemon policy state; no capabilities |

`Seccomp: 2` means the process is in filter mode; this snapshot does not expose
the filter's complete syscall/argument decision table.

## 3. Policy-file evidence

The pulled service policy files include a plain `futex: 1` rule. In the files
captured here, that line does not encode a futex sub-operation selector. The
correct conclusion is narrow: these service profiles permit the futex syscall
at their policy layer. It is not valid to transfer that result to ordinary app
processes, nor to infer successful PI requeue semantics.

The visible policy directory contains service-specific files for media and
crash-dump paths. It does not expose a general ordinary-app policy file. The
runtime strings in `libandroid_runtime.so` refer to seccomp policy setup, but
the actual generated app filter was not recovered.

## 4. GhostLock gate update

### 已證實

- PS7331 normal app processes are under seccomp filtering in the captured
  snapshot.
- Selected service policies explicitly mention futex.
- `adbd` mode/capability state is distinct from app processes.

### 高可信推論

- A direct userspace requeue-PI path must pass an app-domain seccomp boundary;
  the presence of a generic futex rule in a service profile is insufficient.

### 待驗證

- The exact Fire app-domain filter decision for futex PI operations.
- Whether a native app can reach the requeue-PI path under that filter.
- Runtime `waiter->task != current`, cleanup residue and later consumer.

### 已排除或不支持

- `Seccomp: 0` on `adbd` as evidence of root or a general bypass.
- `futex: 1` in media/configstore policy as proof of a Fire GhostLock trigger.

### 因風險拒絕測試

- Sending a futex PI/requeue operation solely to discover the filter result.
- Installing or executing an adapted Emerald/GhostLock binary.
- Changing seccomp, SELinux, tracing, kernel memory or package security state.
