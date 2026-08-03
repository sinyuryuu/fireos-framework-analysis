# Phase 5AF evidence index

All device evidence below is from the explicit serial
`G001LT0511550CFT`, captured 2026-08-03 UTC / 2026-08-04 Asia/Taipei. The capture
script is read-only and records command lines, stdout, stderr, exit codes and a
directory hash manifest.

## Exact-device evidence

### P5AF-DEVICE-001

- Source: exact runtime identity and properties
- File: `adb/phase5/PHASE5AF-ANDROID-CVE-SURFACE-20260804-02/identity.stdout.txt`
  and `props.stdout.txt`
- SHA-256: `7bb4a293663f02c546ed9222fac711bbc22aa451bbfdada564d7019e8e4daff8`; `cf9dd92b26eac1381e1e6a1936b19dc59900705690f136e1ff46b34ab4074f35`
- Test ID: `PHASE5AF-ANDROID-CVE-SURFACE-20260804-02`
- Timestamp: `2026-08-03T20:57:21Z`–`20:57:23Z`
- Command: `adb -s G001LT0511550CFT shell id`; `adb -s G001LT0511550CFT shell getprop`
- Observed result: `KFTRWI` / `trona`, MT8183, Android 9/API 28, PS7330.4104N,
  kernel 4.4.146+, shell UID 2000, SELinux Enforcing
- Interpretation: exact target identity is unchanged
- Confidence: Confirmed
- Related hypothesis: all exact-target CVE applicability hypotheses

### P5AF-DEVICE-002

- Source: kernel security and namespace prerequisite checks
- File: `kernel_security.stdout.txt`; `user_namespace_limits.stdout.txt`
- SHA-256: `1d5251b09f525e43e42d2a9fa07fee1255f656aac2ac87c1d1d3fad40c5df00e`; `93c7084d2ddca5cb1bda4b2b653248d0689636c85eb4c86460b2d194fc1b087e`
- Command: read-only `cat` of kernel security/sysctl paths
- Observed result: `perf_event_paranoid=3`; randomize/kptr values denied to shell;
  user namespace sysctl paths absent
- Interpretation: some public Linux/Android exploit prerequisites are not visible
  or not available to this shell; not a proof that futex PI is patched
- Confidence: Strong evidence, runtime-scoped
- Related hypothesis: GhostLock/DirtyClone public prerequisite equivalence

### P5AF-DEVICE-003

- Source: module and XFRM surface
- File: `module_surface.stdout.txt`; `xfrm_stats.stdout.txt`
- SHA-256: `8ba794e6b9b715a5bf1c2e3c1b412eb2d689e4d1f5398c40838e00c4b63ffa24`; `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Command: read-only `ls` of `/sys/module/*` and `cat /proc/net/xfrm_stat`
- Observed result: `xt_TEE`, `esp4`, `esp6`, `x_tables`, `xfrm_user` paths absent;
  `ipv6` present; `/proc/net/xfrm_stat` absent
- Interpretation: no captured runtime surface for the documented DirtyClone TEE/ESP
  path
- Confidence: Strong evidence, runtime-scoped
- Related hypothesis: DirtyClone exact Android route

### P5AF-DEVICE-004

- Source: device-node metadata and permission checks
- File: `node_metadata.stdout.txt`; `node_access.stdout.txt`
- SHA-256: `d087c220ff9fb586d5a7ef2223b7792634f9a83bb8882a6e5f815402ba61f3`; `64a1d41c462e3acdfbe69fec0b3620ac1cda2bbd2951a9152984ed61fed9ad9c`
- Command: read-only `ls -lZ` and `test -r/-w`; no node open/read/ioctl
- Observed result: `/dev/aed0`, `/dev/aed1`, `/dev/atf_log`, `/dev/sspm` shell
  read/write `0/0`; `/dev/ion` shell access test `1/1`; `/dev/ion` is
  `system:graphics` with mode `0666`
- Interpretation: ION metadata/access is visible but no ioctl capability or exploitability
  follows; AEE/ATF/SPM are blocked at the normal shell boundary
- Confidence: Confirmed, access-check scope
- Related hypothesis: AEE/ION/ATF alternate Android route

### P5AF-DEVICE-005

- Source: HOME resolver sanity check
- File: `home.stdout.txt`
- SHA-256: `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- Command: `adb -s G001LT0511550CFT shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME`
- Observed result: priority 50, `com.amazon.firelauncher/.Launcher`
- Interpretation: HOME behavior remained unchanged after read-only capture
- Confidence: Confirmed
- Related hypothesis: Fire Launcher remains the formal HOME

## Host/source evidence

### P5AF-HOST-001

- Source: existing Phase 5U/5Z exact source/config analysis
- File: `findings/phase-5u-android-cve-applicability.md`; `findings/phase-5z-android-aee-implementation-review.md`
- Observed result: FUTEX/RT_MUTEXES family overlap; AEE node/config boundary; signed
  PS7330 binary and compiled layout unavailable
- Interpretation: GhostLock is source/config applicability only
- Confidence: High-confidence source applicability; not exploitability
- Related hypothesis: H1 GhostLock exact target

### P5AF-HOST-002

- Source: existing exact MT8183 defconfig review
- File: `output/tables/phase5u-cve-surface-matrix.csv`; `findings/phase-5x-android-implementation-and-route-review.md`
- Observed result: principal documented DirtyClone duplicate/TEE symbols are disabled
- Interpretation: documented DirtyClone entry path is not supported by the captured config
- Confidence: Confirmed, config-scoped
- Related hypothesis: H2 DirtyClone exact route

## Public-source evidence

### P5AF-WEB-001

- Source: [NVD CVE-2026-3499](https://nvd.nist.gov/vuln/detail/CVE-2026-3499)
- Observed result: WordPress Product Feed PRO CSRF, not kernel/Android GhostLock
- Interpretation: supplied CVE identifier is unrelated
- Confidence: Confirmed
- Related hypothesis: CVE-2026-3499 = GhostLock

### P5AF-WEB-002

- Source: [NVD CVE-2026-43503](https://nvd.nist.gov/vuln/detail/CVE-2026-43503)
- Observed result: `__pskb_copy_fclone()`/frag-transfer marker propagation in Linux
  net/skbuff and ESP writer context
- Interpretation: DirtyClone is a distinct networking kernel issue
- Confidence: Confirmed
- Related hypothesis: DirtyClone Android implementation

### P5AF-WEB-003

- Source: [JFrog DirtyClone analysis](https://research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503/)
  and [0xBlackash GitHub repository](https://github.com/0xBlackash/CVE-2026-43503)
- Observed result: public implementation is Linux C/research VM oriented and depends
  on TEE/ESP/user-network namespace surfaces
- Interpretation: not an Android APK or exact KFTRWI port
- Confidence: Strong evidence, public-source scope
- Related hypothesis: DirtyClone direct port

### P5AF-WEB-004

- Source: [NebuSec GhostLock](https://nebusec.ai/buglist/CVE-2026-43499/) and
  [Android target index](https://mallory.ai/vulnerabilities/CVE-2026-43499)
- Observed result: GhostLock is futex/rtmutex; public Android projects are target/build
  specific
- Interpretation: target headers and offsets cannot be reused for PS7330 without matching artifacts
- Confidence: Strong evidence
- Related hypothesis: GhostLock Android port

### P5AF-WEB-005

- Source: [rafaeldtinoco/security dirtyclone](https://github.com/rafaeldtinoco/security/tree/main/exploits/dirtyclone)
- Observed result: repository is a Linux VM reproducer with an explicit authorized-use
  warning; no Android target
- Interpretation: useful implementation reference only; not a device payload
- Confidence: Confirmed, public-source scope
- Related hypothesis: DirtyClone Android port

## Hash manifest

The complete capture hash list is:
`adb/phase5/PHASE5AF-ANDROID-CVE-SURFACE-20260804-02/sha256sums.txt`

Its SHA-256 is `9e0557544fc527b27b3d6d280d2ef3efb22a6e9aeeffcfd1dd42ead3674d7d27`.
