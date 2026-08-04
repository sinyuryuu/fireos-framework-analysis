# PS7331 SELinux policy variant delta (host-only)

This comparison reads preserved CIL text as line sets. It does not compile, load,
install, select, or apply a policy, and it does not contact a device.

## Findings

- **已證實：** the preserved `rootable_*` files differ materially from their
  standard counterparts; focused counts and hashes are in `policy-delta.csv`.
- **高可信推論：** the rootable variants appear more engineering/debug-oriented
  where the focused additions include `typepermissive`, expanded `su` references,
  and additional transition/capability rules.
- **待驗證：** whether any of these files is selected by the retail PS7331 boot
  path; this host-only delta cannot establish active policy selection.
- **因風險拒絕測試：** policy replacement, boot-property injection, AVB bypass,
  `/init` execution, or any attempt to obtain root.

## Pair summaries

| Pair | Added unique lines | Removed unique lines | Rootable `typepermissive` | Rootable `su` matches |
|---|---:|---:|---:|---:|
| plat | 2295 | 1803 | 1 | 323 |
| plat_pub | 1437 | 1067 | 0 | 1 |
| vendor | 1060 | 6 | 0 | 0 |

The comparison is evidence of file content only. It is not evidence that a
writable property, shell command, or retail boot path can select the rootable
variant.
