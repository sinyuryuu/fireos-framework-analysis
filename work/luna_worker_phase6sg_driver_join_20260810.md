# Phase 6SG — host-only static source-to-client driver join

日期：2026-08-10。範圍限定為 PS7331 / trona 的 host-side static source→config→shipped policy→exact native client join。未啟動真機 node，未執行 ioctl、Binder、root、module load、寫入、reboot 或 diagnostic operation；既有 runtime evidence 僅作 provenance，不重新操作。

## 判定規則

只有同一列同時閉合以下四段才標 `POSITIVE`：

1. GPL source 的 registration/fops/ioctl 與 trona config 選入；
2. 保存的 shipped init/ueventd 或等價 node metadata，能給出 exact owner/group/mode；
3. 保存的 file_contexts/genfscon 與 CIL/TE allow，能指定 exact caller domain；
4. 保存的 native userspace inventory 能把同一 domain 的 exact binary/library/function 與 `open`/`ioctl`（或 proc open/write）連到該 exact node。

其餘一律 `UNKNOWN`；source capability、policy allow、HAL/service 存在、symbol 命中或 adjacent init rule 均不單獨升格 positive。

## 結果

本次沒有 `POSITIVE`。11 個目標面均至少缺少 exact native open/ioctl caller，部分另缺 shipped mode/owner 或 exact allow。`/dev/gsensor`、`/dev/mtk_cmdq`、`/proc/m4u` 的 shipped init ownership/mode 已保存；`/proc/perfmgr/perf_ioctl` 沒有同名 exact init ownership/mode rule，不能以其他 perfmgr children 代替。`/dev/ion` 的 0666 system:graphics 是既有 metadata，不是本次保存 init rule；RPMB node mode/owner 亦未保存。

### 逐列摘要

| Target | 已閉合的部分 | 仍缺的 join | Status |
|---|---|---|---|
| `/dev/mtk_cmdq` | source/config；init `system:system 0644`；`mtk_cmdq_device`；CIL allow 對 appdomain、graphics/media HAL、surfaceflinger、mediaserver 等 | 沒有 exact native binary/function `open` + CMDQ ioctl caller；appdomain allow 不是 caller proof | UNKNOWN |
| `/dev/ion` | source/config；`ion_device`；plat/vendor CIL 多個 domain allow；既有 metadata `system:graphics 0666` | exact shipped init/ueventd ownership/mode provenance 與 exact native `open`/ION ioctl caller 未閉合 | UNKNOWN |
| `/dev/gsensor` | source factory ioctl；init `radio:system 0660`；`gsensor_device`；CIL allow 對 `radio`、`meta_tst`、NVRAM domains | sensors HAL binary 存在不等於 exact `/dev/gsensor` open/ioctl callsite；無 exact caller | UNKNOWN |
| `/proc/perfmgr/perf_ioctl` | source `proc_create` mode 0664；`proc_perfmgr` genfscon；CIL allow 對 appdomain、system/media/power/graphics 等 | exact init owner/group rule 與 native proc open/write/ioctl caller 未閉合；其他 perfmgr child rules 不可替代 | UNKNOWN |
| `/proc/m4u` | source active proc registration mode 0；init `system:media 0440`；M4U type/mediacodec allow | exact final proc label join 與 native M4U proc caller 未閉合；`/dev/M4U_device` branch 被註解 | UNKNOWN |
| RPMB (`/dev/rpmb0`, `/dev/emmcrpmb0`, RPMB block) | source `rpmb-mtk.c`；config `CONFIG_RPMB=y`, `CONFIG_RPMB_INTF_DEV` off；file_contexts labels；`rpmb_svc` init service exists | shipped node owner/mode、service→node exact open/ioctl caller 未閉合；TEE allow 不是 `rpmb_svc` callsite | UNKNOWN |
| IDME (`/proc/idme`, boot1 block) | source proc path strips write bits/restricts ownership；boot1 `idme_block_device` label；IDME HAL init `system:system`；CIL HAL/idme block allow | exact proc read client / HAL-to-block native callsite 與 block owner/mode 未閉合；direct userspace write is source-bounded negative, not a positive join | UNKNOWN |
| Amazon driver-test diagnostic proc | source owner-write test dispatcher；`CONFIG_AMZN_DRV_TEST` absent in trona config；no shipped node proof | module/node delivery、owner/mode、file-context/allow、client all unclosed; not shipped-confirmed | UNKNOWN |
| Amazon metrics/vitals | source read/poll-only logger surface；existing inventory records `/dev/metrics` and `/dev/vitals` | exact shipped mode/owner, labels/allow and native reader not closed | UNKNOWN |
| Amazon lifecycle `/proc/life_cycle_reason` | source read-only proc (`0444`); no proc write callback | exact shipped policy and native reader not closed; kernel setter is not a userspace writer | UNKNOWN |
| Diagnostic Trouble Code HAL | vendor executable/init and `amzn_hal_diagnostictroublecode_default` policy/domain are present | this is a HIDL diagnostic service, not an exact target-node open/ioctl caller; no node client join | UNKNOWN |

## Evidence used

- GPL/source and config: `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/`; exact `arch/arm64/configs/trona_defconfig`; preserved merged config `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`.
- Shipped init/policy extraction: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/init/`, `vendor/etc/selinux/vendor_file_contexts`, `vendor/etc/selinux/vendor_sepolicy.cil`, `system/etc/selinux/plat_sepolicy.cil`.
- Prior reconciliations: `work/luna_worker_phase6sc_kernel_20260810.md/.csv`, `work/luna_worker_phase6qe_driver_policy_20260810.csv`, `work/luna_worker_phase6rz_20260810.md/.csv`, plus the Phase 6SC/6QE/6RZ evidence referenced therein.
- Native inventory boundary: `firmware/extracted/PS7331/selected/extraction-manifest.tsv` and the bounded APK/JAR/native inventories cited by Phase 6RZ/6NP. Marker or symbol presence without an exact open/ioctl callsite remains UNKNOWN.

## Safety and non-claims

No node was opened; no ioctl/proc write/Binder transaction/diagnostic operation was sent. This report does not claim that a policy allow is reachable by an ordinary app, nor that any listed hardware/storage surface changes package, HOME, PMS, ATMS, boot, or identity state.

## Output hashes

SHA-256 values for this report and its companion CSV are reported after file creation in the handoff message and are also reproducible with `shasum -a 256`.
