# Phase 6NO evidence index

| Evidence ID | Source | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| 6NO-IPC-001 | `work/luna_worker_phase6_private_client_universe_20260810.md` | `3cf080d5304fc65561ed105e7162b29f4386c89ba4270b58f893341eae16898b` | 指定 corpus 的 private service publication、Proxy/Stub、clients、trust domains 與 HOME/package sinks 索引。 | Strong evidence, bounded |
| 6NO-IPC-002 | `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:369203-369243,29462-29832,402917-403398` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | User/Profile/Package client forwarding 與 metadata/KFT sink。 | Confirmed |
| 6NO-IPC-003 | `findings/phase-6j-ipc-deep-review.md`; `adb/phase6cz/`, `adb/phase6ep/` | Hashes in existing manifests | shell private service lookup boundary；下游 PMS/permission gates。 | Confirmed |
| 6NO-OOBE-001 | `work/luna_worker_phase6_oobe_user_scope_20260810.md` | `f6d322aaa157842fd320557d03d6b6a6b00b259c1b402d2dcb718302ec0d2d0c` | OOBE Context/process-user-derived chain；numeric User 0 remains unproven. | Confirmed chain / Unknown numeric user |
| 6NO-OOBE-002 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:96087-96126`; `boot-framework-disassembly.log:452691-452721` | Services `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`; framework `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df` | sendBroadcast user argument is derived from sender Context; PackageManager sink uses Context user. | Confirmed |
| 6NO-OOBE-003 | `findings/phase-6jd-fosinit-registration-audit-closure.md` | `7a56394115235d76812c9c4d273c1eecb896eb268b2bc4ca99a892d4f3e2b238` | 123 `*_fosinit.xml` registration set and read-only runtime callback baseline already closed. | Confirmed |
| 6NO-LAUNCH-001 | `findings/phase-6nk-continuation-synthesis.md` | SHA recorded in Git commit `d9241300d` | Existing priority/preferred/child/Accessibility results separated by scope. | Confirmed |

## Safety fields

- `device_mutation`: false
- `binder_transaction_sent`: false
- `oobe_or_ota_replay`: false
- `input_injection_or_ioctl`: false
- `root_attempt`: false
- `fire_launcher_state_changed`: false
- `credentials_used_or_stored`: false
