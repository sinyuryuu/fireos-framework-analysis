# Phase 6D `/init` property/cmdline evidence index

## E6D-IP-01 — exact `/init` input

- Source: preserved PS7331 image extraction
- File: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`
- SHA-256: `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`
- Observed: AArch64 stripped `/init` used as host-only input.
- Interpretation: exact input provenance; not active-policy proof.
- Confidence: **已證實**

## E6D-IP-02 — cmdline/property marker inventory

- Source: `inventory_phase6d_init_properties.py`
- Files: `property-cmdline-inventory.json`, `property-cmdline-markers.csv`
- Artifact: `artifacts/phase6d/phase6d-init-property-inventory-20260804-01/`
- Observed: 162 literal marker occurrences across cmdline, boot property, SELinux,
  recovery, policy and lock-state classes.
- Interpretation: `/init` contains multiple boot-decision surfaces.
- Confidence: **已證實（static scope）**

## E6D-IP-03 — code reference mapping

- Source: AArch64 ADRP/ADD mapping
- File: `property-cmdline-adrp-add-references.csv`
- Artifact: same directory
- Observed: 111 mapped references, including `androidboot.selinux` at `0x41bd90`
  and `permissive` at `0x41bdcc`.
- Interpretation: selected literals are used by code-level address construction;
  this is stronger than a strings-only result but remains static.
- Confidence: **已證實（instruction-pattern scope）**

## E6D-IP-04 — rootable/standard loader boundary

- Source: existing disassembly windows
- File: `artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/disassembly-windows.txt`
- Observed: rootable and standard path-builder regions call `0x41be00` with different
  `w5` values; `0x41be48` branches on `w5`.
- Interpretation: common loader decision boundary; exact branch semantics unresolved.
- Confidence: **高可信推論（control-flow boundary）**

## E6D-IP-05 — stock boot context

- Source: existing read-only runtime snapshot
- File: `findings/phase-6c-runtime-capture-20260804-01.md`
- Observed: SELinux Enforcing, verified boot green and locked-kernel property in that
  snapshot.
- Interpretation: current snapshot context; does not identify which policy blob was
  selected by early init.
- Confidence: **已證實（snapshot scope）／待驗證（active policy identity）**

## E6D-IP-06 — safety boundary

- Source: inventory artifact safety fields
- File: `property-cmdline-inventory.json`
- Observed: host-only, ELF not executed, no device contact, no property change,
  no fastboot, no policy selection, no kernel memory access or payload.
- Interpretation: static inventory only.
- Confidence: **已證實**
