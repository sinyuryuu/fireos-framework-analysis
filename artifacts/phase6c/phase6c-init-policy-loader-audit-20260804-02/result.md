# PS7331 `/init` policy-loader static audit

Host-only disassembly/provenance analysis. The ELF was not executed; no boot property, SELinux policy, device, kernel memory, or exploit path was touched.

## Observed

- Input SHA-256: `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`
- Literal policy markers: `12`
- ADRP/ADD code references mapped to markers: `10`
- Rootable-marker code references: `5`
- Standard-marker code references: `5`

## Evidence interpretation

**已證實：** stripped `/init` contains code-level ADRP/ADD references to both rootable and standard SELinux policy path strings; the references occur in a path-building region which calls a common helper with different flag values. A separate function compares the `androidboot.selinux` key and `permissive` value.

**高可信推論：** the image contains a policy-loader decision surface rather than only inert filenames.

**待驗證：** the active policy variant, exact branch predicate, helper semantics, and whether the current stock boot can select any alternate policy. A stripped binary and static path references cannot answer those runtime questions.

**因風險拒絕測試：** changing boot properties, selecting a rootable policy, remounting, flashing, bootloader operations, or executing any kernel race/panic/root payload.

## Reproduction

```sh
python3 tools/scripts/analyze_phase6c_init_policy_loader.py --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init --output artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02
```

Raw disassembly windows and machine-readable mappings are kept beside this report.
