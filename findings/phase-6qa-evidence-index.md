# Phase 6QA evidence index

日期：2026-08-10
公開基準：`d34b2909f968d20496a0929822e36586a7e8729b`

| Evidence ID | Source | File | SHA-256 | Observed result | Classification |
|---|---|---|---|---|---|
| `QA-VEND-01` | Vending method follow-up | `work/luna_worker_vending_skipped_methods_followup_20260810.md` | `35782cd1e1703a9926214d78c6ef2c699f70b7f087c5af55c0a6e24653f5a04e` | Recovered `LauncherConfigurationReceiver` and `DseService`; no Fire/HOME/root sink | Strong evidence |
| `QA-VEND-02` | Vending normalized rows | `work/luna_worker_vending_skipped_methods_followup_20260810.csv` | `63edbe2e77c6d203101b8f022c0c389f0505ac23a3ea8a430be20dab0790c4df` | 2 rows, 9-column worker schema | Confirmed artifact |
| `QA-PM-01` | Amazon PM proxy follow-up | `work/luna_worker_amazonpm_proxy_followup_20260810.md` | `182dc6165508b4681a68b4465186d9a5e7154e7bb7e64535574a9621f3c0de79` | tx6/tx7 implementation and identity gates; no production caller found | Strong evidence |
| `QA-PM-02` | Amazon PM normalized rows | `work/luna_worker_amazonpm_proxy_followup_20260810.csv` | `761d7cea8f7ff061053f0d56781844fa287e7a0c3f6a099494b12a27dd32a895` | 2 rows, 9-column worker schema | Confirmed artifact |
| `QA-SET-01` | Settings/Home resource follow-up | `work/luna_worker_settings_home_resource_followup_20260810.md` | `fabb7782657c65eee2f8abecde0582fe603341703eb9a2b9a95372e6fe0caf58` | No new HOME key/resource/route; `default_home` remains dormant/internal | Strong evidence |
| `QA-SET-02` | Settings normalized rows | `work/luna_worker_settings_home_resource_followup_20260810.csv` | `dc4a7c692840ea45cb3391224f91cae0a5bc2c5d37fd6c7dfb224e520a7dac34` | 14 rows, exact-build static comparison | Confirmed artifact |
| `QA-PZ-01` | Phase 6PZ broad closure | `findings/phase-6pz-broad-surface-closure.md` | `c532544e47b83d9f6984472a25d915cbd34fe3701571a4ec46e5ac9d7a657d2c` | Prior 41-row closure; no low-privilege User-0 package/HOME/system/root sink | Strong evidence |
| `QA-MI-01` | Source archive EOF closure | `findings/phase-6mi-source-tar-eof.md` | `0b3d01e8264010320a2b504bceb249f7459bbe96072426e91fe1a42dc56f596f` | Outer source archive reached EOF; no hidden updater/post-install member | Confirmed static |
| `QA-NORM-01` | Phase 6QA normalized matrix | `output/tables/phase6qa-residual-control-closure.csv` | `b441b66b912a63c104efca83b380693867325423afbf2c0b4650dbf23c485d43` | 18 rows: Vending 2 + Amazon PM 2 + Settings 14 | Confirmed artifact |
| `QA-NORM-02` | Phase 6QA normalization manifest | `output/tables/phase6qa-residual-control-closure.csv.manifest.json` | `679369ef937fe7fe788b4b39293e21d04c6c1bf230dd29fa800e4875aa12042a` | Input hashes, row counts, output hash, no-device/no-mutation flags | Confirmed artifact |
| `QA-SCRIPT-01` | Phase 6QA generator | `tools/scripts/build_phase6qa_residual_control_closure.py` | `4c7db5b47059d0772ea49294fbb4f01a8f4747b7303a47236a6d1a52f9743c70` | `py_compile`, dry-run and write-once generation passed | Confirmed artifact |

## Evidence handling

The worker reports and CSVs are raw evidence inputs. They were read only. The
normalizer is host-only and refuses overwrite; it does not contact ADB, Binder,
SettingsProvider, OTA/recovery or any device node.
