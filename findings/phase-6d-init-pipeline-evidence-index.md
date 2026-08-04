# Phase 6D `/init` pipeline evidence index

## Evidence INIT-PIPE-01

- Source: official AOSP Android 9 anchor fetch
- File: `aosp/android-9/init-source-20260804-01/source-manifest.tsv`
- SHA-256: `007b6ebc575952e2aca6462442fc1523d02e225c7476adc2850727ccd10330f9`
- Observed result: r1/r61 `selinux.cpp`, `selinux.h`, `Android.bp`, `main.cpp` fetched
- Interpretation: reproducible AOSP anchor input is present
- Confidence: **Confirmed**

## Evidence INIT-PIPE-02

- Source: AOSP source function parser
- File: `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/anchor-map.csv`
- SHA-256: `4697d1794f5dc771f9a9e09c6cad66244fc8b286f573566ad87e124fbbc2b4b3`
- Observed result: all seven selected anchors found at identical r1/r61 line ranges
- Interpretation: baseline function anchors are stable for this comparison
- Confidence: **Confirmed**

## Evidence INIT-PIPE-03

- Source: stripped PS7331 `/init` audit joined with AOSP anchors
- File: `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/pipeline.json`
- SHA-256: `a1a98ed3c5ddd2d736f00061f7d4a6cb26e6b0fea64eaec4ab23cb0969e0b563`
- Observed result: standard and rootable path references, common-helper candidate and
  property-parser candidate are recorded; exact mapping is false
- Interpretation: binary decision surface is real, exact Amazon source diff is unavailable
- Confidence: **Strong evidence** for code-level surface; **Hypothesis** for exact identity

## Evidence INIT-PIPE-04

- Source: PS7331 `/init` provenance
- File: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`
- SHA-256: `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`
- Observed result: input binary is the preserved stripped PS7331 `/init`
- Interpretation: pipeline mapping is tied to the preserved artifact, not an unverified binary
- Confidence: **Confirmed**

## Evidence INIT-PIPE-05

- Source: GPL scope audit
- File: `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.json`
- Observed result: `platform/system/core/init` absent
- Interpretation: Amazon source-level `/init` diff cannot be recovered from this GPL package
- Confidence: **Confirmed**
