# Phase 6C.5 GPL source scope evidence index

## Evidence GPL-6C5-01

- Source: PS7331 GPL source scope audit
- File: `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.json`
- SHA-256: `8ab20dd811f93b30163f0f5b5f8dadb75bb3e73cc8199571a0f62f9709963221`
- Command: `python3 tools/scripts/audit_phase6c5_gpl_source_scope.py ...`
- Observed result: `system_core_init_present=false`; kernel futex／rtmutex targets present
- Interpretation: source package has kernel scope but no Android init source
- Confidence: **Confirmed**
- Related hypothesis: GPL archive can provide `/init/selinux.cpp` source diff — **Disproved**

## Evidence GPL-6C5-02

- Source: named-file scan
- File: `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.json`
- Command: same audit; `selinux_named_matches`
- Observed result: four `selinux.h` matches are kernel headers or external dbus header;
  no `rootable_*`／`sepolicy` init source match
- Interpretation: filename hits do not provide policy-loader implementation
- Confidence: **Confirmed**
- Related hypothesis: a named SELinux file in the GPL package is the Amazon init patch — **Disproved**

## Evidence GPL-6C5-03

- Source: exact kernel file hashes
- File: `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.json`
- Observed result: `kernel/futex.c` SHA-256 `ca9140...ca7a96`; `rtmutex.c` SHA-256
  `6cb544...75dde`
- Interpretation: the package remains valid for the separate kernel provenance audit
- Confidence: **Confirmed**
- Related hypothesis: the GPL package is useless for all Fire OS analysis — **Disproved**
