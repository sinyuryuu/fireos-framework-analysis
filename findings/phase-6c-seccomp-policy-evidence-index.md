# Phase 6C seccomp policy boundary evidence index

## P6C-POLICY-001 — process filter mode

- **Source:** Read-only device snapshot from prior Phase 5 capture
- **File:** `adb/phase5/PHASE5CT-SECCOMP-20260804-01/device-status.txt`
- **SHA-256:** `310c6760f3e241eddca75166875bdaac4ef7d4afb18104fb921e6a3988882a02`
- **Test ID:** `PHASE5CT-SECCOMP-20260804-01`
- **Observed result:** system_server, SystemUI, Settings, Microsoft Launcher, OTA and research APK processes report `Seccomp: 2`; `adbd` reports `Seccomp: 0`.
- **Interpretation:** A filter is active for the listed processes in that snapshot; filter contents are not shown.
- **Confidence:** Confirmed
- **Related hypothesis:** H6C-APP-SECCOMP-SCOPE

## P6C-POLICY-002 — service profiles permit generic futex

- **Source:** Pulled policy files from the same prior read-only capture
- **Files:** `system-crash_dump.arm.policy`, `system-crash_dump.arm64.policy`, `system-mediacodec.policy`, `system-mediaextractor.policy`, `vendor-configstore@1.1.policy`
- **SHA-256:** `44c91bd6187354ed039d63a5e536125597ed9e454b206722d9e525d54fb0a482`, `a40de703c1dc78f24706a62b4e67fcfb0046f744cc7def4de2c294d6274f9278`, `ee90974989c392ad6e3e343802bca4769dca4d7ba82ecdf04e0f6ada2806ef7e`, `fcb93275617f3d683826d0c941c6d6787defa12653ee704f2b7e6d802c4972d3`, `3525a280a99e6c9f8c191f231cb56709080bcef0bfd35e6c33f368c45f7b3ade`
- **Observed result:** each contains a generic `futex: 1` rule; none contains named requeue-PI rules.
- **Interpretation:** These service profiles do not visibly block the generic futex syscall; scope is limited to processes that actually use them.
- **Confidence:** Confirmed, service-policy scope
- **Related hypothesis:** H6C-SECCOMP-GENERIC-FUTEX

## P6C-POLICY-003 — policy directory scope

- **Source:** Prior read-only policy directory inventory
- **File:** `adb/phase5/PHASE5CT-SECCOMP-20260804-01/policy-list.txt`
- **SHA-256:** `d37388e86361430684f033b6128c853306fd3c867af0360c9c0d7c7f36648ed3`
- **Observed result:** visible profiles are crash_dump, media codec/extractor and vendor configstore; no ordinary app profile was recovered.
- **Interpretation:** The app policy source remains a coverage gap, not an absence proof.
- **Confidence:** Confirmed inventory; Unknown app-policy conclusion
- **Related hypothesis:** H6C-APP-POLICY-SOURCE

## P6C-POLICY-004 — installed/native policy surface inventory

- **Source:** Host-only scanner
- **File:** `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-05/installed-artifact-policy.json`
- **SHA-256:** `715646e9f19d8382e588f7fe7266f8f29de8f16db2b85c6a961e3a76d510f86a`
- **Observed result:** 72 files and 14,075 archive members; `FUTEX_SYSCALL_POLICY=5`; named `FUTEX_CMP_REQUEUE_PI=0` and `FUTEX_WAIT_REQUEUE_PI=0`.
- **Interpretation:** No direct named requeue-PI policy/caller marker in the supplied artifacts; service generic futex policy is present.
- **Confidence:** Strong evidence, bounded artifact scope
- **Related hypothesis:** H6C-NAMED-REQUEUE-PI-SURFACE

## P6C-POLICY-005 — runtime policy setup code

- **Source:** Preserved Fire `libandroid_runtime.so` analysis
- **File:** `findings/phase-5cs-fire-art-futex-analysis.md`
- **Observed result:** `set_app_seccomp_filter`, `set_system_seccomp_filter` and `set_global_seccomp_filter` markers are present in the binary scope.
- **Interpretation:** Runtime policy setup exists; the app filter data and futex operation decision are not recovered.
- **Confidence:** Confirmed binary scope; app policy effect Unknown
- **Related hypothesis:** H6C-APP-SECCOMP-SETUP

## P6C-POLICY-006 — safety boundary

- **Source:** Current host-only run
- **File:** `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-05/installed-artifact-policy.json`
- **Observed result:** `device_contacted=false`, `image_mounted=false`, `elf_executed=false`, `futex_triggered=false`, `kernel_memory_accessed=false`.
- **Interpretation:** No device state changed and no kernel trigger was executed.
- **Confidence:** Confirmed
- **Related hypothesis:** Safety boundary

## Evidence limit

These records do not prove a temporary root path. The remaining unverified gates
are app-policy contents, a real requeue-PI caller, runtime identity mismatch,
cleanup residue, later consumer, memory effect and privilege transition.
