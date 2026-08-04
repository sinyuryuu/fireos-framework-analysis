# Phase 6C `/init` policy-loader evidence index

## E6C-IL-01 — input identity

- Source: preserved PS7331 image extraction
- File: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`
- SHA-256: `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`
- Command: `shasum -a 256 .../root/init`
- Observed: AArch64 stripped `/init` input preserved from PS7331 image.
- Interpretation: exact input provenance; not proof of active policy selection.
- Confidence: **已證實**

## E6C-IL-02 — rootable path code references

- Source: host-only ADRP/ADD mapping
- Files: `artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/policy-path-references.csv`, `disassembly-windows.txt`
- SHA-256: `e70c9fc26bf1f688579f8643d2a88bf79408dd7ff98cbb99b60948fe4bdd7d60`; `3a8baaa32fefc4b3fa73ed32a7e470d580b500497d5e37bfbf62d88bf3e319bd`
- Command: `python3 tools/scripts/analyze_phase6c_init_policy_loader.py ...`
- Observed: five rootable path references are reached by AArch64 ADRP/ADD pairs in the `0x41ad00` region, followed by a call to `0x41be00` with `w5=1`.
- Interpretation: code-level loader/path-builder surface exists.
- Confidence: **已證實（static scope）**

## E6C-IL-03 — standard path code references

- Source: same host-only mapping
- Files: same artifact directory
- Observed: five standard policy/hash path references are reached by ADRP/ADD pairs in the `0x41aea8–0x41bf08` regions; the standard path call at `0x41af80` passes `w5=0`.
- Interpretation: standard and alternate path construction share a stripped helper boundary.
- Confidence: **已證實（static scope）**

## E6C-IL-04 — boot property comparison candidate

- Source: AArch64 disassembly window
- File: `disassembly-windows.txt`, section `selinux_property_compare_41bd60`
- Observed: 19-byte comparison against `androidboot.selinux`, then 10-byte comparison against `permissive`, followed by a zero store through a structure field on success.
- Interpretation: property parsing/decision candidate; exact field semantics unresolved.
- Confidence: **已證實（instruction pattern）／高可信推論（policy role）**

## E6C-IL-05 — current stock boot context

- Source: read-only device snapshot
- File: `findings/phase-6c-runtime-capture-20260804-01.md`
- Observed: PS7331 fingerprint, SELinux Enforcing, verified boot green, locked kernel property.
- Interpretation: snapshot-scoped runtime context; does not identify active policy blob.
- Confidence: **已證實（snapshot scope）／待驗證（active policy identity）**

## E6C-IL-06 — safety boundary

- Source: tool metadata and artifact safety fields
- Files: `policy-loader-audit.json`, `result.md`
- Observed: host-only; ELF not executed; no device contact; no policy load; no boot-property change; no kernel memory or payload.
- Interpretation: provenance analysis only.
- Confidence: **已證實**

## E6C-IL-07 — GhostLock runtime gap remains

- Source: Phase 6A/6B/6C reports
- Files: `findings/phase-6a-untrusted-app-pi-smoke-test.md`, `findings/phase-6b-host-layout-model.md`, `findings/phase-6c-requeue-precondition-model.md`
- Observed: ordinary PI lock/unlock reached from untrusted app; proxy identity mismatch, cleanup residue, memory effect and privilege transition were not observed.
- Interpretation: static loader evidence does not close the runtime exploitability gap.
- Confidence: **已證實（what was tested）／待驗證（unobserved runtime states）**

## Safety exclusions

因風險拒絕：在 stock device 上觸發 requeue-PI、建立 paired waiter、安排 race、
測試 kernel panic、heap shaping、ION/pipe 佔位、KASLR live-slide extraction、
kernel memory read/write、policy selection mutation 或 privilege payload。
