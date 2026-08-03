# Phase 5Q evidence index

| Evidence ID | Source | Observed result | Interpretation | Confidence |
|---|---|---|---|---|
| `P5Q-ANDROID-001` | AOSP CTS commit `41603998db75f63a00581e359eca408ff30a3da1` | CVE-2020-0069 is packaged as a native CTS `cc_test` with `poc.c`, not an ordinary APK | Defines the public Android implementation form | 已證實，public-source scope |
| `P5Q-ANDROID-002` | AOSP CTS `poc.c`; NVD CVE-2020-0069 | Historical implementation uses CMDQ device names and v2 request family including #7/#8/#3 | The public PoC has a device/driver-specific ABI contract | 已證實，public-source scope |
| `P5Q-FIRE-001` | `.../v2_driver-excerpt.txt:709–752` | v2 has `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`, `copy_from_user`, allocator call and `copy_to_user` | v2 source exposes the contract expected by old PoCs | 已證實，source scope |
| `P5Q-FIRE-002` | `.../v3_driver-excerpt.txt:663–706` | v3 dispatcher has no #7 case and default returns `-ENOIOCTLCMD` | Exact recovered MT8183 v3 source does not implement the tested v2 request | 已證實，source scope |
| `P5Q-FIRE-003` | `.../v3_make-excerpt.txt`; `mt8183_defconfig-excerpt.txt` | MT8183 build selection and CMDQ configuration select v3 | Connects the source branch to the target platform, within source/config scope | 已證實，source/config scope |
| `P5Q-RUNTIME-001` | `adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/probe.stdout.txt` | One approved read-only open and one zeroed #7 request returned `open_ret=3`, `ioctl_ret=-25` | Runtime corroboration of the v2/v3 mismatch for that request | 已證實，single-test scope |
| `P5Q-ANALYZER-001` | `artifacts/phase5/android-cmdq-implementation-review-20260804-01/` | Host analyzer reports v2 #7 present, v3 #7 absent, runtime `-25` | Reproducible synthesis; no device action | 已證實，derived scope |
| `P5Q-BOUNDARY-001` | `findings/phase-5h-cmdq-ioctl-result.md`; `findings/phase-5p-android-nearby-port-review.md` | No alternate ioctl, exploit, native payload, boot image read, or partition operation was performed | No evidence supports a current-device root claim | 已證實 |
