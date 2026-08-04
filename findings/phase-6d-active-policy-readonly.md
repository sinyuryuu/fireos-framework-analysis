# Phase 6D：PS7331 active-policy / boot visibility read-only capture

## 範圍

本輪使用 serial `G001LT0511550CFT`，只執行 `getprop`、`getenforce`、`id`、檔案
可見性、檔案雜湊與 `logcat -d`。沒有改變 boot property、SELinux policy、package、
settings、服務、分割區或裝置重啟狀態。

Canonical raw output：
`adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/`

## 觀察

**已證實（snapshot scope）：**

- Fire OS：`Fire OS 7.3.3.1`
- fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- model：`KFTRWI`
- hardware：`mt8183`
- Android API：28／release 9
- security patch：`2024-08-01`
- kernel：`4.4.146+`
- `getenforce`：`Enforcing`
- shell：UID 2000，context `u:r:shell:s0`
- `ro.boot.verifiedbootstate=green`
- `ro.boot.flash.locked=1`
- `ro.boot.unlocked_kernel=false`
- `ro.debuggable=0`、`ro.secure=1`
- PID 1 context：`u:r:init:s0`

**已證實（可讀檔案）：** 標準 policy 路徑與 rootable variant CIL 同時存在於檔案系統；
標準 `/vendor/etc/selinux/precompiled_sepolicy` 存在。兩個 platform/mapping hash
文字檔內容一致：
`df9c0b3e4264373ba818c420ffb2d144880334c246d74b733dac27c07f0944f8`。

**無法取得證據：** shell 無法讀取 `/sys/fs/selinux/policy`、`/proc/cmdline`、
`/proc/bootconfig`、`/proc/slabinfo` 與 `/proc/kallsyms`，因此本 snapshot 不能直接
計算 live policy blob hash，也不能由 shell 直接觀察 kernel cmdline 或 SLUB 狀態。

**高可信推論：** 可見的 `ro.boot.selinux=enforcing`、green/locked 狀態與標準
precompiled policy 檔案，與 stock enforcing boot 相容；但不能僅憑檔案存在證明
rootable policy 未被選取或標準 precompiled blob 已由 init 載入。

**已排除：** shell 可讀到 `rootable_*` 檔案不等於已取得 root，也不等於能以
`settings`／shell 改寫 init 的 policy 選擇。

## 原始檔與雜湊

| File | SHA-256 |
|---|---|
| `metadata.txt` | `a87d54d7850dce3012068ca35393009abae9ec9fda9bb754c34141cf723ffe73` |
| `getprop.stdout.txt` | `eff54128ec883e000ebc1efc10b90806aa2526bd280557ecffa83051125ab4a2` |
| `policy_hashes.stdout.txt` | `7803bbc21ba9b3862cd04ba8d5491973208d9e6b386a691018b433ccf014284d` |

完整輸出以目錄內 `final_hashes`／`status` 為準；拒絕的讀取會保留 stderr。

## 重現

```sh
bash tools/scripts/capture_phase6d_active_policy_readonly.sh --dry-run \
  --serial G001LT0511550CFT \
  --output adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-YYYYMMDD-NN

bash tools/scripts/capture_phase6d_active_policy_readonly.sh \
  --serial G001LT0511550CFT \
  --output adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-YYYYMMDD-NN
```
