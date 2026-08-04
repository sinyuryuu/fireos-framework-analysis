# Phase 5CS：Fire ART／Amazon native synchronization inventory

日期：2026-08-04
裝置：Amazon Fire HD 10／`trona`／MT8183
Build：`Amazon/trona/trona:9/PS7331.4463N/0031575863172:user/amz-p,release-keys`
方法：既有唯讀 ADB listing／pull，主機端 ELF inspection
安全狀態：沒有執行 pulled ELF、futex、race、ioctl、device-node、核心記憶體操作或 root payload。

## Executive result

這一輪找到一條新的、但語意上不同於 GhostLock 的 Fire userspace 路徑：

```text
Fire libart.so
  → ThreadList::SuspendAllInternal
  → ART condition-variable synchronization
  → ordinary compare-requeue marker
  → libc syscall boundary
  → kernel futex entry
```

Fire `libart.so` 的字串表包含 `futex cmp requeue failed for`，並保留
`ThreadList::SuspendAllInternal` 符號；針對該方法的主機端 disassembly 看到
它到達 `syscall` PLT 邊界。AOSP ART 的對應 source history 將同一診斷文字
放在 `ConditionVariable::Broadcast` 的 ordinary `FUTEX_CMP_REQUEUE`
路徑中。[AOSP ART reference](https://android.googlesource.com/platform/art/+/e8256e7773a230337c3d137cbf0365f737820405/runtime/base/mutex.cc)

因此本輪最精確的判定是：

- **已證實（binary scope）**：Fire ART 有 compare-requeue 診斷標記、ART
  suspend method 與 syscall boundary。
- **高可信推論（semantic mapping）**：這是 ordinary compare-requeue，並非
  已證明的 `FUTEX_CMP_REQUEUE_PI`。
- **已證實（runtime library scope）**：`libandroid_runtime.so` 有 seccomp
  設定相關符號／字串；這只證明 policy setup code 存在。
- **僅負面觀察**：本輪選取的 Amazon native libraries 沒有建立 named
  requeue-PI caller；stripped、inline、indirect 或未擷取的 library/service
  仍未排除。
- **仍未觀察**：PS7331 stock runtime 的 `waiter->task != current`、錯誤
  cleanup 執行、持久 invariant violation、後續 consumer、記憶體效果或
  privilege transition。

## 1. Capture scope

原始 inventory：

`artifacts/phase5/phase5cs-native-inventory-20260804-01/`

主要 pulled ELF：

`artifacts/phase5/phase5cs-fire-amazon-native-20260804-01/files/`

主機端可重現分析：

```sh
python3 tools/scripts/analyze_phase5cs_native_inventory.py \
  --capture-dir artifacts/phase5/phase5cs-fire-amazon-native-20260804-01 \
  --output artifacts/phase5/phase5cs-native-analysis-20260804-02
```

腳本只讀取既有檔案，拒絕覆寫 output，並提供 `--dry-run`。公開摘要表為
`output/tables/phase5cs-native-inventory.csv`；完整 host-only JSON、命令與
disassembly 保留在本機分析 artifact。

## 2. Fire ART path

### 2.1 Artifact markers

Exact Fire `/system/lib64/libart.so`：

`SHA-256 3a0a7cdc0d8b3634c6b362e0b68d0f05225063eec098fdc7656988139bb9f658`

Host scan records:

- `futex wait failed for`
- `timed futex wait failed for`
- `futex cmp requeue failed for`
- `futex wait failed for SuspendAllInternal()`
- `ThreadList::SuspendAllInternal`
- imported `syscall`

These are direct artifact observations, not a claim that a string alone proves
the operation.

### 2.2 Method boundary

The method-level host disassembly reaches the `syscall` PLT boundary. The
analysis intentionally does not publish or use syscall-number/argument recipes;
it only records the control-flow boundary. The exact method output hash is in
Evidence `P5CS-004`.

### 2.3 AOSP semantic mapping

AOSP ART's `ConditionVariable::Broadcast` reference shows the diagnostic
`futex cmp requeue failed for` around ordinary `FUTEX_CMP_REQUEUE`. This is a
useful semantic map for the Fire marker, but it is not an exact Fire source
dump and does not prove that Fire's binary accepts or reaches a PI requeue
operation.

The distinction matters:

```text
ordinary compare-requeue  ≠  requeue-PI proxy waiter
PI mutex lock helper      ≠  requeue-PI caller
syscall boundary          ≠  successful kernel operation
```

## 3. `libandroid_runtime.so` and policy boundary

Exact Fire `/system/lib64/libandroid_runtime.so`:

`SHA-256 73dd8b974989faeaed65d03d548f3a776fd31e65ddb29cdd583dcaeea623d837`

The bounded string scan contains:

- `set_app_seccomp_filter`, `set_system_seccomp_filter`,
  `set_global_seccomp_filter`;
- `bionic/libc/seccomp/seccomp_policy.cpp`;
- `Could not set seccomp filter of size`;
- pthread condition/mutex symbols.

This confirms the runtime contains policy setup paths. It does **not** reveal
the Fire app-domain allowlist, does not prove that a particular futex operation
is allowed or denied, and does not justify executing a probe.

## 4. Selected Amazon and vendor libraries

The selected Amazon libraries were scanned offline:

- `libAmazon_tat_jni.so`
- `libamazon_remotes.so`
- `libamazonaspservice.so`
- `libamazonmediaanalytica.so`
- `libamazonwifiservice.so`
- `libbinder.so`
- `libcutils.so`
- `libutils.so`

No named `futex`, `requeue` or `rtmutex` caller was established in the Amazon
selection. Two files expose ordinary pthread mutex names. This is a bounded
negative observation only: stripped symbols, inline code, indirect syscall
wrappers, other system libraries, or vendor services remain possible.

The vendor inventory includes FireOS HIDL and MediaTek libraries, but this
round did not execute or bypass-probe them. `/system/bin/amazonfiled` appears in
the read-only inventory and init properties, while pulling the executable was
denied; that path remains `Unknown`.

## 5. GhostLock evidence gates

| Gate | Result | Label |
|---|---|---|
| PS7331 source has proxy task-context separation | Existing Phase 5CP evidence | 已證實，source/dataflow scope |
| Fire ART uses an ordinary compare-requeue-shaped path | Binary marker + method boundary + AOSP semantic reference | 高可信推論 |
| Fire ART reaches PI requeue | No | 待驗證 |
| Selected Amazon native library calls requeue-PI | Not established | 負面觀察，不是排除 |
| Runtime `waiter->task != current` observed | No | 待驗證 |
| `remove_waiter()` wrong-target cleanup observed | No | 待驗證 |
| Persistent state violation or later consumer observed | No | 待驗證 |
| Controlled memory effect / root | No; not attempted | 未證實／因風險拒絕 |

## 6. Why this is not dynamic validation

「抓到一次 identity mismatch」必須來自同一次真實 kernel execution 的
可驗證觀察，而不是：

- source 中兩個不同的 task parameter；
- 離線模型的假設 row；
- ordinary ART compare-requeue 的字串；
- PI mutex helper 的存在；或
- 一次 crash／重啟本身。

本輪沒有建立這個觀察，因此不能把研究進度宣稱已進入 GhostLock dynamic
validation，也不能推導 temporary root。

## 7. Status and next safe target

### 已證實

- Exact PS7331 Fire ART artifact contains the ART compare-requeue marker and
  the identified suspend method reaches a libc syscall boundary.
- Fire runtime contains seccomp setup references.
- Native inventory and hashes are preserved; device state was not changed.

### 高可信推論

- The ART marker maps to ordinary compare-requeue, not a demonstrated PI
  requeue path.

### 待驗證

- Any requeue-PI caller in unpulled/indirect Fire or vendor code.
- Fire app seccomp policy for a native route, without executing a trigger.
- The four GhostLock runtime gates D1–D4.

### 已排除或不支持

- `pthread_cond_wait()` or ART ordinary compare-requeue alone as proof of
  GhostLock.
- The presence of a PI mutex helper as proof of a proxy waiter.

### 因風險拒絕測試

- Running a futex/requeue-PI trigger, race reproducer or native payload on the
  tablet.
- Opening unknown device nodes or invoking ioctl.
- Reading/writing kernel memory, changing tracing/security policy, or writing
  boot/system partitions.
