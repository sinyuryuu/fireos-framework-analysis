# PS7331 `/init` property/cmdline static inventory

Host-only inventory of a preserved stripped AArch64 ELF. `/init` was not executed; no device, boot property, policy selection, fastboot, bootloader, kernel memory, or root payload was touched.

## Input

- Input: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`
- SHA-256: `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`
- Literal marker count: `162`
- ADRP/ADD references mapped to markers: `111`

## Marker classes

| Class | Literal markers | Mapped ADRP/ADD references |
|---|---:|---:|
| `boot_integrity_or_lock_state` | 5 | 1 |
| `boot_or_recovery_control` | 9 | 9 |
| `boot_property` | 36 | 31 |
| `cmdline_source` | 4 | 9 |
| `policy_path_or_variant` | 39 | 41 |
| `security_property` | 2 | 5 |
| `selinux_policy_or_mode` | 67 | 15 |

## Interpretation

**已證實：** the preserved `/init` contains literal surfaces for `/proc/cmdline`, `androidboot.*`/`ro.boot.*`, SELinux mode/policy names, recovery markers, boot-integrity markers, and rootable/standard policy paths. Some literals are reached by statically mapped AArch64 ADRP/ADD pairs.

**高可信推論：** these strings are consistent with a boot-time property and policy-loader decision surface. The existing `0x41bd60` window contains the `androidboot.selinux`/`permissive` comparison candidate, while the `0x41ad00`/`0x41af80` windows contain rootable/standard path-builder call sites.

**待驗證：** which callers execute on the stock boot, the exact property source/data-flow, the meaning of the stripped helper flag, and the active SELinux policy variant. Literal presence is not proof that a shell-writable property can select an alternate policy.

**已排除：** this inventory does not support the claim that the device is rootable, that `androidboot.selinux=permissive` can be set from Android userspace, or that a rootable policy is active.

**因風險拒絕測試：** boot-property mutation, cmdline injection, bootloader/fastboot selection, policy replacement, remount, image write, and any GhostLock trigger/race/panic/memory/root operation.

## Reproduction

```sh
python3 tools/scripts/inventory_phase6d_init_properties.py --dry-run --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init --output artifacts/phase6d/phase6d-init-property-inventory-YYYYMMDD-NN
python3 tools/scripts/inventory_phase6d_init_properties.py --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init --output artifacts/phase6d/phase6d-init-property-inventory-YYYYMMDD-NN
```

Machine-readable marker and reference tables are kept beside this report.
