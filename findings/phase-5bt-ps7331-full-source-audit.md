# Phase 5BT：PS7331 完整官方 source archive／boot image GhostLock audit

日期：2026-08-04
範圍：只分析 Fire OS 7.3.3.1／PS7331 的官方 source archive、其
`platform.tar` kernel members、官方 OTA-derived `boot.img`，以及保存的
address-sanitized static Image evidence。
裝置操作：無。

## Executive verdict

### 已證實

1. 本機保存的 PS7331 source archive 是官方 S3 檔案的完整 byte stream：
   `Content-Length` 與本機大小都是 `2,563,328,975` bytes，S3 ETag 的 MD5
   `88ffafddb97999ebcc441a1caa76ab5da9` 與本機 MD5 相同；本機 SHA-256 是
   `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`。
2. 同一份 archive 的 top-level build scripts 指向：
   `kernel/mediatek/mt8183/4.4`、`trona_defconfig`、`arm64`，並列出
   `Image`、`Image.gz`、`Image.gz-dtb` 作為輸出。這使選取
   `kernel/mediatek/mt8183/4.4` 的 `rtmutex.c` 成為有 build-path 證據的
   PS7331 source，而不是只靠檔名猜測。
3. build-selected `rtmutex.c` 的 SHA-256 是
   `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`。
   `remove_waiter()` 位於第 1079–1129 行，包含以 `current` 鎖定
   `pi_lock`、清除 `current->pi_blocked_on` 的 cleanup；在該 function 中
   沒有以 `waiter->task` 作為 cleanup task。
4. 同一個 source tree 的 `rt_mutex_start_proxy_lock()` error path 在第
   1684 行呼叫 `remove_waiter(lock, waiter)`；`futex.c` 的 PI requeue 路徑
   在第 1958–1965 行將 `this->task` 傳給 proxy-lock API。這證明 source
   wiring 具有 GhostLock 所涉及的 proxy waiter 形狀，但不等於已證明可觸發
   或取得 root。
5. 由官方 PS7331 OTA 擷取的 `boot.img` SHA-256 是
   `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。
   已保存的地址清理後 Image pattern 與 source-to-Image verifier 均通過：
   current-task source、current-task cleanup、proxy error call 三個 marker
   都存在，且 verdict 為 `pre_fix_consistent`。
6. 同一份 source archive 的 path inventory 中，命名為 `.patch`／`.diff`／
   `series` 的檔案只有四個 Mali hrtimer patch path；沒有命名為
   `rtmutex`、`futex` 或 GhostLock 的 patch path。這是 path-name inventory
   結果，不是對未命名 release-CI 變換的否定證明。

### 高可信推論

**PS7331 的 build-selected source 與已檢查的官方 boot Image 都顯示
GhostLock 的 `waiter->task` 修補不在目前分析的 kernel function 中。** 因此
「升級到 PS7331 即可修補 GhostLock」目前沒有證據支持；若目的只是這個
漏洞，PS7331 不應被標示為已確認的 remediation。

### 待驗證

- PS7331 在實際啟動後是否具有足以形成 privilege transition 的完整 runtime
  觸發條件。
- Amazon release-CI 是否在公開 archive 之外套用 backport、編譯器差異或
  binary post-processing。
- 目前保存的 sanitized Image pattern 是否覆蓋 production Image 的所有
  duplicate kernel copies，而不是只覆蓋已檢查的 function reconstruction。

### 已排除／不採用

- 將 boot header 的 `kernel_offset` 或 `kernel_addr` 當成 GhostLock runtime
  exploit offset。
- 將 source-level pre-fix marker 誤稱為 live root。
- 將「source 有 proxy-lock path」誤稱為已完成可用 PoC。
- 將單獨 PS7331 `boot.img` 寫入現有裝置視為完整、可回復的 PS7331 upgrade。

### 因風險拒絕測試

本階段沒有執行 futex race、kernel memory read/write、native root payload、
未知 ioctl、BROM／DA、preloader／LK、fastboot unlock、OTA sideload、boot
image write、remount、SELinux modification 或任何 partition operation。
這些步驟會把 source applicability review 轉成實際提權／boot-chain 操作，
並可能使裝置需要非標準 recovery；本報告不以「研究者接受變磚」作為執行
授權。

## 1. Official source archive validation

| 欄位 | 值 | 證據 |
|---|---|---|
| URL | `https://fireos-tablet-src.s3.amazonaws.com/k2k5jkgocvaww3SgOjJMkJrykI/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `P5BT-ARCHIVE-001` |
| Local size | `2563328975` bytes | `P5BT-ARCHIVE-001` |
| HTTP Content-Length | `2563328975` bytes | `P5BT-ARCHIVE-001` |
| HTTP ETag／local MD5 | `88ff8aaa109325255b9a1caa76ab5da9` | `P5BT-ARCHIVE-001` |
| Local SHA-256 | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | `P5BT-ARCHIVE-001` |
| Last-Modified | `Tue, 17 Jun 2025 23:58:18 GMT` | `P5BT-ARCHIVE-001` |

HTTP headers are preserved in
`artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/source-http-headers.txt`.
The validation record is
`artifacts/phase5/phase5bt-ps7331-source-archive-validation-20260804-01/`.

## 2. Build-selected source mapping

The two top-level scripts were extracted locally from the same archive; their
SHA-256 values are:

- `build_kernel.sh`: `3b7804c62d8533e200c54f076de4e0382bb21c5e924bbc8ac34773ce98653e33`
- `build_kernel_config.sh`: `fbf0f922fad86ac34d94a1c9c1587cb618516191b4e101b990d757e356b97cfa`

Relevant static locations:

- `build_kernel_config.sh:9-18` selects the MT8183 kernel subtree,
  `trona_defconfig`, `arm64`, and the expected Image outputs.
- `build_kernel.sh:116-119` extracts the supplied platform tarball.
- `build_kernel.sh:130-150` invokes `make`, first with `trona_defconfig` and
  then with the kernel build arguments.
- `build_kernel.sh:160-185` copies and validates the generated arm64 boot
  outputs.

The read-only analyzer reports zero visible non-comment patch/apply/overlay or
signing command tokens in these two scripts. Signing remains **待驗證** because
the release signing pipeline is outside these captured files.

## 3. GhostLock source semantics

### PS7331 `rtmutex.c`

File:
`artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`

The semantic checker result is:

```text
remove_waiter_start_line=1079
remove_waiter_end_line=1129
current_pi_blocked_on_cleanup=true
waiter_task_reference_in_remove_waiter=false
proxy_start_present=true
proxy_error_remove_waiter_call_present=true
classification=PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN
```

The fixed reference has an explicit `waiter_task = waiter->task` and clears
`waiter_task->pi_blocked_on` under that task's lock at lines 1517–1530 of
`artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c`.
That is the relevant semantic difference; line-number differences between
kernel trees are not themselves a vulnerability claim.

### PS7331 `futex.c`

File:
`artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c`
SHA-256: `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`

The PI requeue section at lines 1958–1965 calls
`rt_mutex_start_proxy_lock()` with `this->rt_waiter` and `this->task`. This is
source reachability evidence only. It does not show a user-space trigger, a
race success, an arbitrary read/write, or a UID transition.

## 4. Boot image semantic cross-check

The boot image is retained under `firmware/extracted/PS7331/boot.img`; its
official-OTA provenance and hash are recorded by `P5BT-IMAGE-001`. The prior
sanitized static review deliberately omitted addresses, branch targets, gadget
data and exploit offsets. Its verifier passed all of the following checks:

```text
boot_hash_matches_ps7331=true
source_is_pre_fix=true
source_has_proxy_remove_waiter=true
image_has_current_task_source=true
image_has_current_task_cleanup=true
image_proxy_calls_remove_waiter=true
comparison_verdict_pre_fix=true
comparison_safety_no_execution=true
```

The correct conclusion is **PS7331 inspected source/Image are pre-fix
consistent**, not **PS7331 live root is proven**.

## 5. Patch and overlay boundary

The local nested archive inventory completed with:

```text
outer_tar=0
nested_tar=0
filter=0
```

The `.patch`/`.diff`/`series` subset is limited to four Mali hrtimer paths. No
GhostLock-named patch was found. The inventory also shows both legacy
`kernel/mediatek/4.4` and build-selected `kernel/mediatek/mt8183/4.4` trees;
only the latter is used by the preserved build config.

This supports a **高可信推論** that no clearly named public source patch hides
the fix in the inspected archive. It does not prove that Amazon's release
system did not apply an unlabelled change, and it does not authorize compiling
or flashing a kernel.

## 6. Answer to “can the PS7331 PoC be made certain?”

Not by the available safe evidence alone.

What is now certain at the static patch-status level is:

> The official PS7331 source archive's build-selected MT8183 `rtmutex.c`, and
> the inspected official PS7331 boot Image, retain the pre-fix
> `current->pi_blocked_on` cleanup pattern.

What is not established is whether a live PS7331 device can be made to execute
the vulnerable proxy-lock failure in a way that yields kernel control or root.
That requires a live trigger and privilege-transition validation, which this
project intentionally does not execute. A source-level candidate is not a
reproducible PoC, and a PoC is not root until the privilege transition is
verified.

## 7. Upgrade decision

**Do not upgrade to PS7331 solely to obtain a GhostLock fix.** The evidence
currently points the other way: the inspected PS7331 kernel function is
pre-fix-consistent. PS7331 may still contain unrelated security fixes, but the
full OTA is a multi-partition block update and the standalone boot image is not
an equivalent upgrade or safe experiment.

## 8. Reproduction (host-only)

```sh
tools/scripts/index_phase5_ps7331_local_nested_build_inputs.sh \
  --archive firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --output artifacts/phase5/ps7331-local-nested-build-index-YYYYMMDD-NN

python3 -B tools/scripts/extract_phase5_ps7331_nested_members.py \
  --archive firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --output artifacts/phase5/ps7331-full-source-members-YYYYMMDD-NN

python3 -B tools/scripts/extract_phase5_ps7331_outer_members.py \
  --archive firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --output artifacts/phase5/ps7331-top-level-build-members-YYYYMMDD-NN

python3 -B tools/scripts/check_phase5_ghostlock_source_semantics.py \
  --source artifacts/phase5/ps7331-full-source-members-YYYYMMDD-NN/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --output artifacts/phase5/phase5bt-source-semantic-YYYYMMDD-NN/result.json
```

All commands above are host-only. They do not invoke ADB, fastboot, a compiler,
an extracted shell script, or a device node.

## Evidence status summary

| Finding | Status |
|---|---|
| Official PS7331 source archive identity | **已證實** |
| Build-selected source path | **已證實** |
| PS7331 source contains the GhostLock fix | **已證實：否** |
| Inspected PS7331 Image matches pre-fix source | **已證實** |
| Public named patch path contains GhostLock fix | **已證實：未找到** |
| Runtime trigger reaches vulnerable path | **待驗證** |
| Runtime exploitability | **待驗證** |
| Root／privilege gain | **待驗證，未證明** |
| PS7331 is a GhostLock remediation | **已排除／不支持** |
| Live PoC execution | **因風險拒絕測試** |
