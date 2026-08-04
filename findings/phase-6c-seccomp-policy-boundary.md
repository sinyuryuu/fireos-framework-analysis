# Phase 6C：PS7331 seccomp policy boundary addendum

## 結論先行

這一輪把先前已保存的實機 seccomp policy 與 process snapshot 接回
GhostLock 證據鏈。結果比單純的 source／binary marker 更有資訊量，但仍不
足以授權在平板上呼叫 `FUTEX_CMP_REQUEUE_PI`。

### 已證實

- PS7331 的已保存 process snapshot 中，`system_server`、SystemUI、Microsoft
  Launcher、研究 APK、Settings 與 OTA process 均為 `Seccomp: 2`；`adbd` 為
  `Seccomp: 0`。這是該次快照的 process 狀態，不是每個 process 的規則內容。
- 五份已保存 service policy 都有 generic `futex: 1`：crash_dump arm／arm64、
  mediacodec、mediaextractor、vendor configstore。
- 這五份 policy 沒有具名 `FUTEX_CMP_REQUEUE_PI`、`FUTEX_WAIT_REQUEUE_PI` 或
  `FUTEX_LOCK_PI` rule。
- 已保存的 policy directory listing 只有 service-oriented profiles；沒有取回
  ordinary app policy 檔。

### 高可信推論

對套用上述五份 profile 的 process，`futex: 1` 是 syscall-name 層級的允許
規則，檔案本身沒有按 futex operation argument 分拆的 deny rule。因此這些
service profile 不能被解讀成「requeue-PI 被 seccomp 擋住」。但這個結論只適用
於對應 service profile，不能外推到 untrusted app。

### 待驗證

- untrusted app／zygote 產生的 app filter 的實際內容；目前只看到 app process
  的 `Seccomp: 2`，沒有 app policy 檔。
- Fire 是否把 app filter 編譯進 Bionic／zygote policy blob、或在未保存的
  image 路徑載入。
- app filter 對 `futex` syscall 是否包含 operation-specific BPF 條件。
- 即使 seccomp 允許 generic futex，是否能在 stock userspace 形成 paired
  `WAIT_REQUEUE_PI` waiter。

### 已排除／不支持

- `Seccomp: 2` 不等於所有 syscall 都允許，也不等於 requeue-PI 可達。
- service policy 的 `futex: 1` 不等於 untrusted app policy。
- generic `futex: 1` 不等於已觀察到 proxy waiter、identity mismatch 或
  GhostLock effect。
- 沒有 app policy 檔不等於 app filter 不存在。

### 因風險拒絕測試

未在 shell 或 untrusted app 執行 `FUTEX_CMP_REQUEUE_PI`。理由不是單純的
permission probing：PS7331 exact source 顯示 requeue-PI 可能先準備 PI state，
並在 paired waiter 條件下進入 `rt_mutex_start_proxy_lock()`／cleanup。單執行緒
與單次呼叫不能把該路徑變成無副作用測試。

## 證據

### Process state

原始檔案：
`adb/phase5/PHASE5CT-SECCOMP-20260804-01/device-status.txt`

SHA-256：
`310c6760f3e241eddca75166875bdaac4ef7d4afb18104fb921e6a3988882a02`

觀察到：

| Process class | Seccomp | Interpretation |
|---|---:|---|
| system_server / system UI / apps / research APK | 2 | filter mode active in snapshot |
| adbd | 0 | no seccomp filter in snapshot |

此表不揭露 BPF filter 的內容。

### Service policy files

| Policy | SHA-256 | 觀察 |
|---|---|---|
| `system-crash_dump.arm.policy` | `44c91bd6187354ed039d63a5e536125597ed9e454b206722d9e525d54fb0a482` | `futex: 1` |
| `system-crash_dump.arm64.policy` | `a40de703c1dc78f24706a62b4e67fcfb0046f744cc7def4de2c294d6274f9278` | `futex: 1` |
| `system-mediacodec.policy` | `ee90974989c392ad6e3e343802bca4769dca4d7ba82ecdf04e0f6ada2806ef7e` | `futex: 1` |
| `system-mediaextractor.policy` | `fcb93275617f3d683826d0c941c6d6787defa12653ee704f2b7e6d802c4972d3` | `futex: 1` |
| `vendor-configstore@1.1.policy` | `3525a280a99e6c9f8c191f231cb56709080bcef0bfd35e6c33f368c45f7b3ade` | `futex: 1` |

Policy listing：
`adb/phase5/PHASE5CT-SECCOMP-20260804-01/policy-list.txt`

SHA-256：
`d37388e86361430684f033b6128c853306fd3c867af0360c9c0d7c7f36648ed3`

### Runtime policy setup surface

`libandroid_runtime.so` 的保存 artifact 含有 seccomp setup markers，包括
`set_app_seccomp_filter`、`set_system_seccomp_filter` 與
`set_global_seccomp_filter`。這證明 runtime policy setup code 存在，但沒有
把 app policy blob 或 operation-specific rule 暴露出來。

## AOSP 對照

AOSP Android 9 的 Bionic common seccomp source 將 `futex` 作為帶有
`futex_op` 參數的 syscall entry；該類 allowlist 是供 zygote-spawned process
使用的 syscall policy 來源。這只能支持「generic futex 是 Android app 基礎
同步能力」的背景，不可替代本機 Fire artifact 的 app policy 證據。

參考：

- [AOSP Android 9.0.0_r61 Bionic tag](https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61)
- [AOSP Bionic common seccomp entry](https://android.googlesource.com/platform/bionic/+/7128923e5/libc/SECCOMP_WHITELIST_COMMON.TXT)

## Canonical host-only inventory

本 addendum 使用的新版 inventory：
`artifacts/phase6c/phase6c-installed-artifact-policy-20260804-05/`

- `installed-artifact-policy.json`：
  `715646e9f19d8382e588f7fe7266f8f29de8f16db2b85c6a961e3a76d510f86a`
- `artifact-inventory.csv`：
  `7c677e8c0a02474d3ff06827572e8277bc5901222e25f74c000097aa19860c5c`
- `marker-hits.csv`：
  `82f91cd2f5b4a28f2c694f3a46ccbc6f3cfada088f90a6c9682243f73865aea3`

本輪掃描 72 個保存檔案、14,075 個 archive members，並額外納入上述
`PHASE5CT-SECCOMP` raw policy／status 檔與 Fire native artifact。輸出中的
`FUTEX_SYSCALL_POLICY` count 為 5；named requeue-PI markers 仍為 0。

## 下一個安全目標

優先順序是建立 `system.img`／`vendor.img` 的唯讀 filesystem inventory，找出
app policy、zygote policy 與未保存的 vendor policy。當前主機沒有 `debugfs`、
`e2fsprogs` 或 EROFS extractor，且 raw image 未掛載；不會為了取得這些檔案而
remount、寫入 image、執行未知工具或改動平板。
