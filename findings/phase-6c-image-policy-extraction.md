# Phase 6C：PS7331 image policy／zygote 唯讀覆蓋

## 範圍與限制

本輪在主機端對保存的 PS7331 7.3.3.1 `system.img` 與 `vendor.img` 做選定路徑
的 ext4 唯讀抽取。使用 `debugfs 1.47.4` 的 `rdump`／`dump`；沒有掛載 image、
沒有修改 image、沒有執行抽取出的 ELF、沒有連接 ADB，也沒有在設備上呼叫
futex、建立 waiter、競態、panic、kernel memory operation 或 root payload。

這不是整個分割區的完整檔案樹解包；覆蓋範圍是 policy／zygote／SELinux／init／
permissions／sysconfig／bpf 及少量 runtime native files。未抽取的路徑仍是
**待驗證**。

Canonical extraction：

`artifacts/phase6c/phase6c-image-policy-extract-20260804-06/`

Canonical raw-tree marker audit：

`artifacts/phase6c/phase6c-image-policy-marker-audit-20260804-04/`

## 輸入 provenance

| Input | SHA-256 |
|---|---|
| `firmware/extracted/PS7331/system.img` | `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5` |
| `firmware/extracted/PS7331/vendor.img` | `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb` |

`file` 將兩者辨識為 ext2/ext4 family filesystem image；抽取器實際使用的
filesystem reader 是 `debugfs`，而非 mount。

## 抽取結果

| 項目 | 結果 | 證據 |
|---|---:|---|
| raw files recovered | 281 | `extracted-file-manifest.tsv` |
| system image policy／config paths | 已抽取 | `system/` subtree |
| vendor image policy／config paths | 已抽取 | `vendor/` subtree |
| root init／zygote files | 6 | `root/` subtree |
| debugfs command exit codes | 全部 0 | `logs/*.exit_code.txt` |
| image mounted | false | `safety.txt` |
| image written | false | `safety.txt` |
| device contacted | false | `safety.txt` |

修正後的 extractor 排除了 manifest 自身，避免把輸出檔誤列為 recovered input；
本輪也加入 root `/init` binary，以分析 policy loader 的靜態字串。
先前的 `...-04` 與 `...-05` 輸出保留、不覆寫；本報告只引用 `...-06`。

## 1. seccomp policy surface

在抽取出的五份 service-oriented policy 中看到 generic `futex: 1`：

- `system/etc/seccomp_policy/crash_dump.arm.policy`
- `system/etc/seccomp_policy/crash_dump.arm64.policy`
- `system/etc/seccomp_policy/mediacodec.policy`
- `system/etc/seccomp_policy/mediaextractor.policy`
- `vendor/etc/seccomp_policy/configstore@1.1.policy`

抽取檔案雜湊與行號保留於 image artifact；主要 SHA-256 如下：

| Policy | SHA-256 |
|---|---|
| crash_dump.arm | `44c91bd6187354ed039d63a5e536125597ed9e454b206722d9e525d54fb0a482` |
| crash_dump.arm64 | `a40de703c1dc78f24706a62b4e67fcfb0046f744cc7def4de2c294d6274f9278` |
| mediacodec (system) | `ee90974989c392ad6e3e343802bca4769dca4d7ba82ecdf04e0f6ada2806ef7e` |
| mediaextractor (system) | `fcb93275617f3d683826d0c941c6d6787defa12653ee704f2b7e6d802c4972d3` |
| configstore@1.1 | `3525a280a99e6c9f8c191f231cb56709080bcef0bfd35e6c33f368c45f7b3ade` |

原始 profiles 沒有明文 `FUTEX_CMP_REQUEUE_PI`、`FUTEX_WAIT_REQUEUE_PI` 或
`FUTEX_LOCK_PI` rule。這些是 generic syscall policy observations；它們不能
外推到 ordinary app 的 zygote-created filter，也不能證明某個 futex operation
在 runtime 被允許或拒絕。

Raw-tree audit 結果：

| Marker | Count |
|---|---:|
| `FUTEX_CMP_REQUEUE_PI` | 0 |
| `FUTEX_WAIT_REQUEUE_PI` | 0 |
| `FUTEX_LOCK_PI`／`UNLOCK_PI` | 0 |
| generic `futex:` policy lines | 5 |
| `SECCOMP` | 8 |
| `SECCOMP_FILTER` | 0 |

Classification：**已證實（限定於抽取檔案）**。App filter 的真正 blob、BPF
operation argument 判斷，以及 stock runtime 行為仍是**待驗證**；不以 marker
缺失宣稱不存在。

## 2. zygote 與 native runtime surface

`root/init.zygote64_32.rc` 建立：

```text
service zygote /system/bin/app_process64 -Xzygote /system/bin --zygote --start-system-server --socket-name=zygote
    user root
service zygote_secondary /system/bin/app_process32 -Xzygote /system/bin --zygote --socket-name=zygote_secondary --enable-lazy-preload
    user root
```

`root/init.zygote32.rc` 也保留 32-bit `app_process` 服務。這證明 image 內
標準 Android zygote/app_process 啟動表面存在；它不證明 app 可以建立
requeue-PI paired waiter。

抽取 native files 的 SHA-256：

| File | SHA-256 |
|---|---|
| `system/bin/app_process64` | `c075e6bbef31b2ae03ef6336b8d605c6f430e49bf25444c44aea0563647ec01e` |
| `system/bin/linker64` | `124745b0cac2fa1511cd903a3982108109d8c8f38e77c63df3e97b026e6ee21b` |
| `system/lib64/libc.so` | `0899e7cde39ccae24a3ba7e9f5433922a30f03ed93744af87e053639ce076681` |
| `system/lib64/libandroid_runtime.so` | `73dd8b974989faeaed65d03d548f3a776fd31e65ddb29cdd583dcaeea623d837` |
| `system/lib64/libart.so` | `3a0a7cdc0d8b3634c6b362e0b68d0f05225063eec098fdc7656988139bb9f658` |

Host `strings` 觀察到：

- `libc.so` 有 `__futex_wait_ex` 與 `__futex_pi_lock_ex`。
- `libandroid_runtime.so` 有 `set_app_seccomp_filter`、
  `set_system_seccomp_filter`、`set_global_seccomp_filter`。
- `linker64` 有 `PR_SET_NO_NEW_PRIVS`、`SYS_SECCOMP` 與一般 disallowed
  syscall diagnostic strings。
- `libart.so` 有一般 `futex cmp requeue failed for` diagnostic，但沒有
  命名 `FUTEX_CMP_REQUEUE_PI` marker。

Classification：**已證實（native symbol/string surface）**；這不是 caller、
filter rule 或 runtime proxy evidence。

`root/init` 是 AArch64 stripped static ELF；本輪只在主機上讀取其 bytes 與
`strings`，沒有執行。它含有下列 loader surface：

可公開重現的 marker 摘要保留於
`artifacts/phase6c/phase6c-init-loader-markers-20260804-01.txt`；完整 `/init`
binary 仍只作本機 input，不在報告中當成可執行產物。

- `androidboot.selinux` 與 `permissive`；
- `rootable_plat_sepolicy.cil`、`rootable_plat_pub_versioned.cil`、
  `rootable_vendor_sepolicy.cil`；
- `plat_pub_versioned.cil`、`vendor_sepolicy.cil` 與 `precompiled_sepolicy`；
- `fireos_precompiled_sepolicy.plat_and_mapping.sha256`、
  `fireos_sepolicy.cil` 及 `/fireos`、`/system/fireos`、`/system` policy roots。

這把「rootable file 只是資料檔」提升為「compiled init 支援該類 policy
selection surface」的**高可信靜態線索**；因為只有 strings／順序，沒有 branch
或 runtime property observation，實際選擇條件仍是**待驗證**。任何透過 boot
property、init 或 policy selection 改變設備狀態的驗證都屬於本階段拒絕的
boot/system policy mutation。

既有唯讀設備快照顯示當前 `ro.boot.selinux=enforcing`，檔案為
`device/fireos-config/CONFIG-20260803-02/device_properties.txt`（SHA-256
`dc9ac733476f037073b2046b0c281423010b4e4d7e1b3a74313119d0275d86a6`）。這只
是目前 boot property 的 snapshot；不能把它反推成 init 已選用哪個 policy
variant，也不能替代載入後 policy hash。

## 3. SELinux app／zygote boundary

抽取的 `plat_seapp_contexts` 將 target SDK 28 app 對應到
`untrusted_app`，privileged app 對應到 `priv_app`，並保留 `shell`、
`isolated_app`、`webview_zygote` 等不同 context。`plat_sepolicy.cil` 包含
appdomain 對 zygote socket/process 的標準 Android 互動，以及 vendor policy
對 `appdomain mtk_cmdq_device` 的 ioctl read/open 規則。

這些規則只能回答 label／permission surface；它們不等於某個特定 driver
命令可用，也不構成 ION、CMDQ、kernel memory 或 futex exploit 的授權。

## 4. `rootable_*` policy variant

image 同時保存：

- `system/etc/selinux/rootable_plat_sepolicy.cil`
- `vendor/etc/selinux/rootable_vendor_sepolicy.cil`
- `vendor/etc/selinux/rootable_plat_pub_versioned.cil`

host-only variant audit 的結果：

| Comparison | Standard bytes/lines | Variant bytes/lines | byte-identical | variant `su`-related lines |
|---|---:|---:|---|---:|
| plat | 1,095,579 / 17,073 | 1,152,902 / 17,599 | no | 332 |
| vendor | 691,263 / 9,749 | 814,078 / 10,803 | no | 7 |

`rootable_plat_sepolicy.cil` 的 diff 顯示它把 `su` 加入若干 domain/type
attribute sets；標準 `plat_sepolicy.cil` 本身也含有 `su`／`su_exec` type
定義，故不能只用「有 `su` 字串」推論系統已 rootable。

對抽取出的 `root/`、`system/`、`vendor/` tree 做 literal filename search，
唯一命中是 root `/init` binary；文本 init/config 中沒有另一個明確的
rootable filename reference。`/init` 的 strings 同時含 rootable 與 standard
policy paths，但無法從 strings 判斷 branch、property 值或實際 kernel-loaded
policy。`precompiled_sepolicy`、未抽取 loader branch、boot/recovery 選擇邏輯
與實際 kernel-loaded policy 仍是**待驗證**。

因此本節結論是：

- **已證實：** image 內存在內容不同的 alternate `rootable_*` policy files。
- **高可信推論：** 它們是 build/configuration variant，且 compiled init 保留
  對應 loader surface；仍不是 active root policy 的證明。
- **待驗證：** 哪個 policy blob 在該 boot path 被載入。
- **已排除：** 「檔名含 rootable」即可當成已取得 root 的結論。

## 5. 與 GhostLock runtime 證據的關係

本輪增加了 installed image 的 policy／zygote coverage，但沒有跨過下列證據
門檻：

- `waiter->task != current` 在 PS7331 runtime 發生；
- proxy error branch 執行；
- cleanup residue 或第二次 consumer；
- memory corruption、kernel panic、可控 read/write；
- privilege transition 或 root。

Phase 6B 已知的 stack-resident `rt_mutex_waiter`、KASLR／SLUB 觀測限制、以及
Phase 6C `NOT_READY` lab audit 仍然有效。任何競態、panic、heap shaping、
ION/pipe 占位、kernel memory access 或提權測試均維持
**因風險拒絕測試／LAB_ONLY** 分類。

## 可重現指令

```sh
tools/scripts/extract_phase6c_image_policy_readonly.sh --dry-run \
  --system-image firmware/extracted/PS7331/system.img \
  --vendor-image firmware/extracted/PS7331/vendor.img \
  --debugfs /opt/homebrew/opt/e2fsprogs/sbin/debugfs \
  --output artifacts/phase6c/phase6c-image-policy-extract-YYYYMMDD-NN

tools/scripts/extract_phase6c_image_policy_readonly.sh \
  --system-image firmware/extracted/PS7331/system.img \
  --vendor-image firmware/extracted/PS7331/vendor.img \
  --debugfs /opt/homebrew/opt/e2fsprogs/sbin/debugfs \
  --output artifacts/phase6c/phase6c-image-policy-extract-YYYYMMDD-NN

python3 tools/scripts/audit_phase6c_installed_artifacts.py \
  --input-root artifacts/phase6c/phase6c-image-policy-extract-YYYYMMDD-NN/root \
  --input-root artifacts/phase6c/phase6c-image-policy-extract-YYYYMMDD-NN/system \
  --input-root artifacts/phase6c/phase6c-image-policy-extract-YYYYMMDD-NN/vendor \
  --output artifacts/phase6c/phase6c-image-policy-marker-audit-YYYYMMDD-NN

python3 tools/scripts/audit_phase6c_selinux_policy_variants.py \
  --standard-plat .../system/etc/selinux/plat_sepolicy.cil \
  --rootable-plat .../system/etc/selinux/rootable_plat_sepolicy.cil \
  --standard-vendor .../vendor/etc/selinux/vendor_sepolicy.cil \
  --rootable-vendor .../vendor/etc/selinux/rootable_vendor_sepolicy.cil \
  --output artifacts/phase6c/phase6c-selinux-variant-audit-YYYYMMDD-NN
```

所有腳本拒絕覆寫既有 output 並支援 `--dry-run`；`...` 僅代表同一 extraction
根目錄的明確路徑，不應直接照抄成未解析的 shell path。
