# PS7331 `/init` selector data-flow audit

This is a host-only audit of a preserved stripped AArch64 ELF. The ELF was not
executed; no device, boot property, SELinux policy, or kernel state was touched.

## Findings

- **已證實：** the full-text scan found `2` direct call(s) to
  `0x41be00`, with nearby `w5` definitions recorded in `summary.json`.
- **已證實：** the full-text scan found `0` direct `bl` call(s)
  to `0x41bd60`. Its instruction shape is consistent with an
  `androidboot.selinux=permissive` enforcing-status parser candidate, not by
  itself evidence of rootable-policy selection.
- **高可信推論：** the rootable path literals and the `w5` branch are real
  instruction/data landmarks, but their stripped high-level semantics remain
  unresolved.
- **待驗證：** indirect/inlined callers, stock-boot reachability, and which
  policy variant is active on the retail device.
- **因風險拒絕測試：** executing `/init`, changing boot properties, loading an
  alternate policy, bypassing AVB, or attempting root.

## Interpretation boundary

A zero direct-call count is not a proof of absence: an indirect call or inlined
implementation could still exist. Conversely, a path reference or branch is not
proof that a retail boot selects that path.
