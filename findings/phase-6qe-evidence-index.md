# Phase 6QE evidence index

日期：2026-08-10
公開基準：`52c8b3f6bd376d87635ab76681f1290b29dac415`

## QE-IPC-01 — Amazon IPC caller→sink inventory

- Files: `work/luna_worker_phase6qe_ipc_caller_closure_20260810.md/.csv`
- SHA-256: MD `2abf89488e780fef9a6fd7226e197837740a9736d6ffbe280ab33ad2392401e2`;
  CSV `45c43c50f479e4b2362011e30604c62984ee629a80f45406926a0104a2f866a8`
- Rows: 15
- Observation: no ordinary app/shell → accepted gate → User-0 HOME/package/root/OTA
  sink was closed; UNKNOWN caller or first consumer remains explicitly marked.
- Confidence: Strong evidence for bounded static inventory; not a global absence proof.

## QE-DRV-01 — 7.3.3.1 GPL driver and policy inventory

- Files: `work/luna_worker_phase6qe_driver_policy_20260810.md/.csv`
- SHA-256: MD `812767a9e740c225e608513daf20dbb051a264de72a0efe9f15b532acb8675d9`;
  CSV `a6948b87852491dd5af9dc7d231db1cbb724de1eec9a66e7bdd8a29a5e087dca`
- Rows: 8
- Observation: exact image node modes/labels and SELinux policy are separated from
  source capability; no low-privilege write or package/HOME sink was proven.
- Confidence: Confirmed source/policy observations; indirect/native client scope remains
  bounded Unknown.

## QE-TEST-01 — existing test reconciliation

- Files: `work/luna_worker_phase6qe_existing_tests_20260810.md/.csv`
- SHA-256: MD `1403f5ede56e8f4ae9c7931d315c62db721756abe03934cd01a6417ed511c7e9`;
  CSV `e971ddc55f8cdaa172f15099ac42c6d4e98a807d49dc11581af035fe9114a611`
- Rows: 14
- Observation: prior package gate, KFT, DPM/Profile, Accessibility, OOBE/OTA and
  service-visibility results are preserved; excluded tests are not repeated.
- Confidence: Confirmed where raw evidence/hash is cited; remaining caller provenance
  is Unknown.

## QE-RT-01 — exact-device metadata-only snapshot

- Directory: `adb/phase6qe/PHASE6QE-DEVICE-READONLY-20260810-02/`
- Script SHA-256: `240f6a858769132523f2f550c3988fa434f611411e4da8a692e245d0056b6838`
- Metadata SHA-256: `5afaf05e9d2bec715d9142250f053441b31383ffe9624cb3d80f03cff6e16a0d`
- Manifest SHA-256: `355dd168ad1061f5f017fb24f0d5b6e102d0d17e58cf38710d777cd39c5facee`
- Timestamp: `2026-08-10T02:42:40Z`
- Serial: `G001LT0511550CFT`
- Commands: 12; metadata says no node open, driver read, Binder transaction,
  settings/package mutation, reboot, OTA/recovery or root/exploit.
- Confidence: Confirmed read-only capture.

## QE-RT-02 — node metadata and HOME result

- `node_metadata.stdout.txt` SHA-256:
  `fd8a1b871b5e65e948b44a9d121a0e4368e0c702c07accc756c6bbff9eb28e82`
- `home_resolve.stdout.txt` SHA-256:
  `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- `selinux.stdout.txt` SHA-256:
  `4fefafd0dcddf54b31a0fef448083e7b77576d86a9ec97c14bfd92479c404290`
- Observed: HOME remained `com.amazon.firelauncher/.Launcher` at priority 50;
  mtk_cmdq and gsensor labels/modes matched the bounded policy reading; shell could
  not metadata-read `/proc/m4u` or `/proc/life_cycle_reason`.
- Confidence: Confirmed direct runtime metadata; does not prove behavior of unopened
  drivers or unknown native clients.

## QE-MATRIX-01 — normalized inventory

- File: `output/tables/phase6qe-privilege-surface.csv`
- SHA-256: `fc62a5e463f85169d6854c564f233bec392d23c6f1ec904982f3855ac6d6690a`
- Manifest SHA-256: `cbbe95a47ccb591b8ba92440fb48b342fbd14a5322946fc5dfd4e7b31a5be788`
- Rows: 37 = 15 IPC + 8 driver/policy + 14 existing tests.
- Generator: `tools/scripts/build_phase6qe_privilege_surface.py`; device contact is
  hard-coded false and the dry-run manifest was verified.

## Confidence vocabulary

- **Confirmed**: directly observed or hash-verified source/image/runtime fact.
- **Strong evidence**: multiple artifacts agree, but a caller or runtime edge remains.
- **Probable**: bounded inference with an explicit missing edge.
- **Hypothesis**: requires a future safe test or host analysis.
- **Disproved**: contradicted within the stated build/test scope.
- **Risk-rejected**: intentionally not executed because rollback or safety is not
  sufficiently guaranteed.
