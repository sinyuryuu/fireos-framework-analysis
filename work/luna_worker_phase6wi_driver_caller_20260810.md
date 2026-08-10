# Phase 6WI — PS7331 driver caller closure

Date: 2026-08-10 (Asia/Taipei)  
Scope: host-only static analysis of the exact PS7331 GPL source, preserved boot artifacts, bounded native inventory, and extracted vendor policy. No device node, ioctl, sysfs/proc/debugfs write, ELF execution, root, exploit, or live probing was used.

## Result

No new exact userland/native caller was established. All seven rows are `UNKNOWN`. A positive row would require the same exact driver path in source/config, DT/init/ueventd/file_contexts/vendor-TE, a shipped ELF with path-specific `open/read/write/ioctl` evidence (including DT_NEEDED/relocation where applicable), and an identity-to-sensitive-sink join. Kernel strings, HAL names, policy allows, service names, package presence, or library capability are not caller evidence.

The new boot artifact check is negative for userland callers: `boot_unpacked/Image` is a kernel image and contains Amazon-LD parameter strings and device-label strings, not a userland call site. `boot_unpacked/libmt8183_diag.so` is an ARM64 shared object; its static strings contain ashmem markers but no `amzn_drvs`, `/proc/idme`, `/dev/ion`, `/dev/mtk_cmdq`, sysfs attribute, or ioctl caller marker. It is not treated as shipped diagnostic ownership without a packaging/init/DT_NEEDED join.

## Caller-join matrix

The row-level evidence and hashes are in [the companion CSV](luna_worker_phase6wi_driver_caller_20260810.csv). The matrix deliberately collapses capability-only camera/sensor/thermal library findings into WI-07 and does not repeat prior capability rows as positives.

| ID | Surface | Exact caller result | Primary missing edge |
|---|---|---|---|
| WI-01 | `/dev/mtk_cmdq` | UNKNOWN | shipped ELF open + CMDQ ioctl and exact DT/ueventd/init join |
| WI-02 | `/dev/ion` and ION custom/debugfs | UNKNOWN | top-level consumer plus DT_NEEDED/relocation/call-site and identity sink |
| WI-03 | Amazon-LD sysfs/module parameters | UNKNOWN | exact attribute instance and shipped ELF writer |
| WI-04 | `/proc/idme/*` / IDME HAL | UNKNOWN | exact proc reader ELF and user/sink identity |
| WI-05 | `/proc/amzn_drvs/*` diagnostics | UNKNOWN | final delivery/module state and exact diagnostic process caller |
| WI-06 | RPMB service/block path | UNKNOWN | exact service ELF block open/ioctl and trusted sink |
| WI-07 | thermal/camera/sensor native families | UNKNOWN | path-specific shipped ELF operation and policy identity |

## Policy and boot joins

The extracted `vendor_file_contexts` confirms labels for `/dev/ion` (`ion_device`), `/dev/mtk_cmdq` (`mtk_cmdq_device`), ION debugfs, IDME HAL service executables, and the presence of thermal/sensor init filenames in the vendor-init extraction log. `vendor_sepolicy.cil` contains device/domain type information, including the IDME and diagnostic HAL domains. These are policy/identity context only; no row closes the caller and sensitive sink.

The boot Image strings include `amzn_ld.g_adc1_mv` and `amzn_ld.g_adc2_mv`, plus kernel device-label strings. This corroborates kernel-side delivery markers but cannot establish a userland writer or module load state. `boot.img` and Image hashes are recorded in the CSV; the Image is not assumed to be the currently booted kernel.

## Missing boundaries

1. The bounded native inventory does not retain a complete all-partition ELF corpus with DT_NEEDED, relocation, and function-level call-site tuples for every HAL/service. Absence from it is not global proof of no caller.
2. Exact trona DTB node instances, merged `.config`, built-in/object/module map, final module packaging/loading, and complete ueventd/init joins are not all retained for every surface.
3. Policy labels and privileged domains do not prove that a given process opens the target path, nor that it reaches a package/HOME/settings/privilege sink.
4. `libmt8183_diag.so` is statically inspected only and its deployment/loader edge is not proven. No ELF was executed.
5. Runtime state was intentionally not used to fill these gaps; no device or pseudo-filesystem operation was performed.

## Provenance

Key inputs: exact source/config hashes are row-level in the CSV; `phase6me` manifest hash is `ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a`; native inventory CSV hash is `9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`; `vendor_file_contexts` hash is `db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`; `vendor_sepolicy.cil` hash is `82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`; boot Image hash is `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`; diagnostic library hash is `7147e161de7b3a8097bdf6079d0b414c147067d46e1f446138d041a63dd127d`.

Safety/validation: only host-side `find`, `rg`, `strings`, `file`, `sha256sum`, and CSV parsing were used. No ELF/native binary was run.
