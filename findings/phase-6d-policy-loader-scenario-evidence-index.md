# Phase 6D policy-loader scenario evidence index

## E6D-SC-01 — GPL scope

- **Source:** PS7331 official GPL archive audit
- **File:** `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.json`
- **Observed:** package contains MT8183 4.4 kernel sources but not
  `platform/system/core/init/selinux.cpp`.
- **Interpretation:** no Amazon `/init` source-level diff can be made from this
  archive.
- **Confidence:** 已證實

## E6D-SC-02 — code-level alternate policy references

- **Source:** stripped PS7331 `/init` host audit
- **File:** `artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/policy-loader-audit.json`
- **Observed:** rootable and standard path literals are referenced by ADRP/ADD
  pairs; path-builder candidates call a common helper with `w5=1` and `w5=0`.
- **Interpretation:** rootable path is not merely a strings-only artifact; active
  boot selection remains unresolved.
- **Confidence:** 已證實（code reference）／待驗證（runtime reachability）

## E6D-SC-03 — boot property candidate

- **Source:** stripped `/init` disassembly window
- **File:** `artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/disassembly-windows.txt`
- **Observed:** `0x41bd60` compares `androidboot.selinux` and `permissive`.
- **Interpretation:** boot-time policy/enforcement decision surface candidate;
  exact field and caller are unresolved.
- **Confidence:** 高可信推論

## E6D-SC-04 — AVB/crypto markers

- **Source:** host `strings` inventory of `/init`
- **File:** `artifacts/phase6d/phase6d-policy-scenarios-20260804-01/policy-scenarios.json`
- **Observed:** `FsManagerAvbHandle`, `avb_slot_verify`, `SIGNATURE_MISMATCH`,
  `efuse`, and BoringSSL/AVB source markers occur.
- **Interpretation:** verification code is compiled in; no current evidence ties
  it to rootable policy selection.
- **Confidence:** 已證實（marker presence）／待驗證（control-flow relation）

## E6D-SC-05 — stock read-only boundary

- **Source:** device read-only capture
- **File:** `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/metadata.txt`
- **Observed:** PS7331, locked/green verified boot, SELinux Enforcing, shell UID
  2000; cmdline and live policy blob are not shell-readable.
- **Interpretation:** no evidence of a shell-writable policy selector.
- **Confidence:** 已證實（snapshot）／待驗證（hidden bootloader state）

<!-- End of evidence index -->
