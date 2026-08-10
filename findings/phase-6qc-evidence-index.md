# Phase 6QC evidence index

日期：2026-08-10
公開基準：`7065db1cfaf585212aba4337eb1697478cad40e8e`

本索引只引用保存的 host artifacts 與既有 read-only device evidence。`UNKNOWN`
或 `NOT_FOUND` 表示目前保存 corpus 沒有建立該鏈，並非對所有未取得程式碼的
不存在性證明。

## Worker artifacts

<a id="qc-pw-01"></a>
### QC-PW-01

- Source: prewarm/identity closure worker
- Files: `work/luna_worker_prewarm_identity_closure_20260810.md`；CSV
- SHA-256: `511d58c70767736ff8ecea4a11a7f9e6b4c712aacf06c42d822041c6ca436386`；`7973988c4fa609de8f9f22f8e1e0654cf118a418d43cd742953239d8ee44f0ad`
- Observed: PS7331 prewarm method、transaction 1、Alexa caller、identity clear/restore、PMS lookup 與 `startProcessLocked("prewarm")` 已定位。
- Interpretation: process-prewarm path confirmed; no package/HOME/root sink in bounded body.
- Confidence: Confirmed static / Strong evidence for bounded closure.

<a id="qc-asp-01"></a>
### QC-ASP-01

- Source: ASP/Audio permission-to-sink worker
- Files: `work/luna_worker_asp_permission_sink_closure_20260810.md`；CSV
- SHA-256: `65068874e74ec8fd3e38b28aca55577d70a3f8dacdde0f81592e0460e3e7d0a5`；`e4212271e783a7ab522d9da922a8013dcaf5dbc0129df79294ad4e51edc17778`
- Observed: tablet branch of `hasCallerGotPermission()` returns true before named `ASP_PERMISSION` branch.
- Interpretation: static authorization anomaly candidate; not runtime exploit proof.
- Confidence: Confirmed static; Hypothesis for security impact.

<a id="qc-asp-02"></a>
### QC-ASP-02

- Source: same ASP/Audio worker
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`, hash `ecbe62fe8eb8bd575da8b2a73a1551651c`
- Observed: ASP callers reach native command/capture/injection/IR/audio paths; no reviewed PMS, ATMS, HOME, package-state, credential/root, APK, OTA or reboot writer.
- Interpretation: sink is audio/HAL-adjacent, not a privilege-to-package pivot.
- Confidence: Strong evidence, bounded to reviewed class/callers.

<a id="qc-asp-03"></a>
### QC-ASP-03

- Source: prior real-device ASP read-only evidence
- Files: `adb/phase6bv/PHASE6BV-ASP-RO-20260805-01/`; manifest hash `5127e7a16039556ce825165d97c787f9f7a2512e7a33a2834ddf618c54c97673`
- Observed: shell UID 2000, SELinux Enforcing, `audiosignalprocessor` visible, probe result `-13/EACCES`, denial log preserved.
- Interpretation: tablet static branch does not establish shell reachability on the captured device; no new probe was run in Phase 6QC.
- Confidence: Confirmed runtime observation.

<a id="qc-asp-04"></a>
### QC-ASP-04

- Source: same ASP/Audio worker
- File: `work/luna_worker_asp_permission_sink_closure_20260810.csv`
- Observed: AudioService mutators use explicit audio/signature permissions; identity clearing follows checks; `getPackageInFocus` is read-only.
- Interpretation: audio control surface is not a HOME/package/root writer in bounded scope.
- Confidence: Strong evidence.

<a id="qc-ota-01"></a>
### QC-OTA-01

- Source: OTA canonicalization/provenance worker
- Files: `work/luna_worker_ota_canonicalization_provenance_20260810.md`；CSV
- SHA-256: `4d6bc6518f8f45773ac517225d33e9f990ed1de5c590c2b68bf827482e057e64`；`374d5bdb1eb0d3658d9bce25abd48cb75b30795d369f94e8650efde6f962ac18`
- Observed: hash/certificate/product-PVT validation, `UpdateSystem.install`, recovery/update-binary registry, extraction/block-image and write sink mapped.
- Interpretation: privileged OTA/recovery capability confirmed; shell/ordinary-app caller not established.
- Confidence: Confirmed capability; Strong evidence for no bounded low-privilege chain.

<a id="qc-ota-02"></a>
### QC-OTA-02

- Source: same OTA worker
- File: native `update-binary`/summary artifacts cited by worker; `update-binary` hash `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`
- Observed: `MakeFreeSpaceOnCache 0x417bf0 -> __readlink_chk 0x4ce4e8`; no selected direct edge to extraction/block-image/write sink.
- Interpretation: canonicalization marker is confirmed; indirect data-flow remains unresolved and no traversal claim is made.
- Confidence: Strong evidence for the bounded direct-edge result; Hypothesis for indirect behavior.

<a id="qc-ota-03"></a>
### QC-OTA-03

- Source: same OTA worker
- Files: `UpdateSystemWrapper.java` hash `c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`；`OSUpdateValidator.java` hash `36fca220ec2332bee5e5af3c9c2317056a425b90507951345d5b729c76c6f256`
- Observed: privileged/controller identity and certificate/product/PVT checks precede recovery/native write capability; no crafted OTA or updater execution.
- Interpretation: high-impact capability is not a shell primitive in the preserved chain.
- Confidence: Strong evidence.

<a id="qb-rt-01"></a>
### QB-RT-01

- Source: Phase 6QB canonical read-only baseline
- File: `adb/phase6qb/PHASE6QB-READONLY-20260810-01/metadata.json`
- SHA-256: `9c8db228ac716492ee230e5e93e59eb5cb8ef082b15a0077b66acba1523c2f79`
- Observed: 31 read-only commands; no mutation, Binder transaction, OTA/recovery or reboot.
- Confidence: Confirmed runtime capture.

<a id="qb-rt-05"></a>
### QB-RT-05

- Source: Phase 6QB canonical read-only baseline
- File: `adb/phase6qb/PHASE6QB-READONLY-20260810-01/logcat_all_dump.stdout.txt`
- SHA-256: `dcef2a733776de2832c99dfe2239f25a619ab222a0bfbc44f60b17b354ddf451`
- Observed: shell UID 2000 service-manager lookup denials for Amazon private services.
- Interpretation: service listing is not proof of shell Binder reachability.
- Confidence: Confirmed runtime boundary.

## Normalized artifact

- File: `output/tables/phase6qc-privilege-closure.csv`
- SHA-256: `c22a7cd25e43204351967c77fa4d2f7ffcc410540efb92b00d81aa2de137151c`
- Manifest: `output/tables/phase6qc-privilege-closure.csv.manifest.json`
- Manifest SHA-256: `25ee8838d16c9c339b127a0ca07f2e663b3d647c3336dde5dc7a27806aa513f2`
- Rows: 26 = 7 prewarm/identity + 8 ASP/Audio + 11 OTA/canonicalization.
- Generator: `tools/scripts/build_phase6qc_privilege_closure.py`.
- Generator behavior: host-only; write-once; no ADB/Binder/settings/package/OTA/recovery/root/exploit operation.
