# Phase 5BM evidence index

| Evidence ID | File | Observation | Confidence |
|---|---|---|---|
| `P5BM-PS7330-RUNTIME` | `device/baseline/BASELINE-20260803-05/device_properties.txt` | Exact runtime identity is PS7330.4104N | Confirmed, runtime scope |
| `P5BM-PS7330-SOURCE` | `artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv` | Exact source-family `rtmutex.c` hash is recorded | Confirmed, source scope |
| `P5BM-PS7330-BOOT-PROBE` | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | Shell pull of installed boot returned Permission denied | Confirmed, access scope |
| `P5BM-PS7330-VMLINUX` | `artifacts/phase5/phase5bm-artifact-ledger-20260804-01/ledger.csv` | No verified exact signed boot/vmlinux in workspace | Confirmed, workspace inventory scope |
| `P5BM-PS7330-BOOTCHAIN` | `artifacts/phase5/phase5bm-artifact-ledger-20260804-01/ledger.csv` | No verified exact preloader/LK/recovery set in workspace | Confirmed, workspace inventory scope |
| `P5BM-PS7331-OTA` | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | Complete adjacent PS7331 OTA; known hash recorded in ledger | Confirmed, version scope |
| `P5BM-PS7331-BOOT` | `firmware/extracted/PS7331/boot.img` | PS7331 boot hash matches preserved manifest; not exact PS7330 | Confirmed, version scope |
| `P5BM-PS7331-RTMUTEX-SOURCE` | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | Adjacent build-selected source hash recorded | Confirmed, adjacent source scope |
| `P5BM-HOST-001` | `artifacts/phase5/phase5bm-artifact-ledger-20260804-01/ledger.json` | Host-only ledger generated without device I/O | Confirmed, analyzer scope |
