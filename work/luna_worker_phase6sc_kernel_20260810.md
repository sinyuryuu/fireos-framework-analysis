# Phase 6SC — PS7331 kernel/driver surface join

日期：2026-08-10（Asia/Taipei）  
範圍：host-only 靜態搜尋與既有證據整理。輸入為 PS7331 GPL source、
trona_defconfig／保存的 kernel config、已抽取的 SELinux/config 文字，以及
Phase 6RZ/6FS/6FT/6G/6IS/6NP 證據。沒有接觸真機 device nodes、ioctl、
Binder、reboot、root、diagnostic operation 或 exploit。

## 結果

CSV 將每個 surface 分開記錄 source capability、node/entry、ueventd 或
source mode、SELinux/file-context、userspace caller 與 sensitive effect。
只有 join 真的閉合時才標示 caller；否則明確寫 UNKNOWN。node metadata、
SELinux allow、copy_from_user、proc mode 或 source registration 都沒有被
當成漏洞或成功可達性。

- /dev/mtk_cmdq、/dev/ion、/dev/gsensor 的 source/config 或 label evidence
  已存在；CMDQ 的 Phase 6FT source data-flow 可到 secure metadata/readback
  helper，但沒有安全的 userspace caller 或 framework sink join。
- /proc/perfmgr/perf_ioctl 與 /proc/m4u 是 source-described proc control
  surfaces；exact final policy、caller 與 runtime reachability 均 UNKNOWN。
- ION 的 extracted policy 有 shell -> ion_device allow，且 metadata 曾記錄
  0666 system:graphics；這是 permission/metadata evidence，不是 live open、
  ioctl 成功或 memory-safety finding。Phase 6NP 的 bounded 307 APK/JAR scan
  沒有 direct ION marker；native symbols 不足以閉合 exact caller。
- RPMB/file-context 與 rpmb_svc binary evidence 存在，但 service-to-driver
  caller、exact ueventd ownership/mode、TE join 未閉合。持久化 boot/policy
  effect 只能標示 theoretical。
- Amazon IDME source 移除 write bits，/proc/idme 是 read/seq path；IDME HAL
  binary/context 不等於 /proc/idme writer。Amazon diagnostic test proc source
  有 factory-reset/RTC special-mode labels，但 final config
  # CONFIG_AMZN_DRV_TEST is not set，未證實 shipped module/node。
- /dev/metrics、/dev/vitals logger source/documentation 只有 read/poll；
  /proc/life_cycle_reason source mode 0444 且 userspace write callback 不存在。

## Join interpretation

```
source registration / fops
        -> selected config or image evidence
        -> node name + ueventd/mode + file_context/genfscon/TE
        -> exact userspace open/read/write/ioctl caller
        -> downstream sensitive effect
```

本次多數 rows 在倒數第二步停止。UNKNOWN 是 evidence boundary，不是「沒有
caller」的絕對證明；它表示保存的 host corpus 沒有足夠 exact callsite、policy
與 shipped provenance。

## Provenance anchors

- GPL platform source archive：
  firmware/extracted/PS7331-SOURCE-20250617/platform.tar
  SHA-256 69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd。
- Saved kernel config：
  artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config
  SHA-256 eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04。
- trona_defconfig：
  artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig；
  lines 139–140 select CMDQ, line 463 selects ION, lines 524–527 select Amazon
  lifecycle/metrics; final config line 3584 leaves AMZN_DRV_TEST unset.
- Extracted policy：
  artifacts/phase6c/phase6c-image-policy-extract-20260804-02/system/etc/selinux/plat_sepolicy.cil
  SHA-256 4056ed9140f6c201cb2dd55edf70041667a195e20233bb6a6a2468b40c9a872d。
  The previously cited vendor file-context path was absent at final recheck; the
  CSV preserves it as prior evidence and does not claim a fresh hash.

## Disposition

No sensitive effect is demonstrated for an ordinary app, shell, or framework
caller. The only positive caller boundary retained here is the prior /proc/ged
query-only shell telemetry, which is a reference negative and not one of the
requested sensitive effects. Safe continuation is limited to host-side recovery
of exact final ueventd/file-context/TE and native caller provenance if those
artifacts become available. No node operation is part of this result.

Row-level evidence, hashes and confidence are in
work/luna_worker_phase6sc_kernel_20260810.csv.

