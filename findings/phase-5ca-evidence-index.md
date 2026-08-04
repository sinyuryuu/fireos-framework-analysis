# Phase 5CA evidence index

日期：2026-08-04；scope：PS7331 only；host-only。

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| P5CA-001 | Public follow-up patch | [Patchew v1](https://patchew.org/linux/20260507112913.1019537-1-dave%40stgolabs.net/) | web source | Null waiter guard plus negative-only wrapper check | Confirmed, upstream scope |
| P5CA-002 | Exact source | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | Early return before assignment; current-task cleanup; broad wrapper condition | Confirmed |
| P5CA-003 | Exact source | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | PI requeue reaches proxy-lock call | Confirmed |
| P5CA-004 | Host-only mapping | `artifacts/phase5/phase5ca-ps7331-followup-patch-mapping-20260804-01/followup-mapping.json` | generated manifest | Both follow-up source requirements absent in PS7331 source | Confirmed, source scope |
| P5CA-005 | Safety boundary | `findings/phase-5ca-ps7331-followup-patch-mapping.md` | repository commit hash | No device I/O or exploit execution | Confirmed |
