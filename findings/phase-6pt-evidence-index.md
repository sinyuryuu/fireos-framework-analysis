# Phase 6PT evidence index

本輪新增或整合的 evidence 均未改變設備狀態。主機端分析只讀已保存檔案；
Vending live capture 只執行明確列出的 read-only ADB queries。

| Evidence ID | Source | File | SHA-256 | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| PT-HOLDER-01 | preserved Phase 6MC inventory | `output/tables/phase6mc-permission-holders.csv` | `1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18` | 60 holder rows / 59 packages across six requested permission families | High-impact holder metadata exists; caller reachability is separate | Confirmed |
| PT-HOLDER-02 | preserved permission definitions | `adb/phase6mc-permission-holders-20260810-01/package_dump.stdout.txt` | `6f2754f4e9655567524de00c5b044326cbd992d6a9022b87397369fb5b905909` | Requested permissions are signature/privileged or development protected | Ordinary app cannot infer access from package row alone | Confirmed |
| PT-VEND-01 | current device readonly capture | `adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/vending_package.stdout.txt` | `d3075425f6980289611f8163858c9ff637901ccb4648ec482fb844973c50c361` | Vending UID 10180, `/data/app`, package-management grant rows | Holder and placement confirmed; provenance unknown | Confirmed |
| PT-VEND-02 | current device readonly capture | `adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | HOME remains Fire Launcher | No passive holder change observed | Confirmed |
| PT-VEND-03 | host-only receiver audit | `artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java` | `71d17a064272f88d02f4619a2f4fa6fedf0ae91a233c29e0ad6d4110643b6b47` | PendingIntent creator/current HOME checks and Play Store tracker update | Exported restore metadata path; no bounded Fire/HOME setter | Strong evidence |
| PT-LIVE-01 | current device readonly capture | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/fingerprint.stdout.txt` | `15efeeb538e9463865e2851c32dc3142d71c8412b8b55447506b1d65db402e4b` | Serial is `G001LT0511550CFT`; fingerprint is PS7331.4463N; shell is Enforcing | Current target and build match the study baseline | Confirmed |
| PT-LIVE-02 | current device readonly capture | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | HOME resolves to `com.amazon.firelauncher/.Launcher`, priority 50 | No passive HOME change during this phase | Confirmed |
| PT-LIVE-03 | current device readonly capture | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/home_candidates.stdout.txt` | `e868693c97bce5ec4c93c6e5e144225797c2219fafde54d46fdbd3bdf462442c` | Candidates remain Fire 50, Microsoft 0, FallbackHome -1000 | Candidate set unchanged | Confirmed |
| PT-LIVE-04 | current device readonly capture | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/vending_package.stdout.txt` | `d5f14d258467db63110abbae908c3ffb103213f7b361a0f41442e7cacb3446a0` | Current Vending package metadata re-captured without mutation | Provenance remains a static question | Confirmed |
| PT-LIVE-05 | capture metadata | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/metadata.json` | `a42109fa1935f18d7485955bc5d514bc9c2f6f949602b8c748278a6fe631aaf2` | 14 read-only commands; mutation/Binder/reboot/OTA flags false | Evidence capture was non-mutating | Confirmed |
| PT-KFT-01 | saved disassembly and runtime tests | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325` | see `findings/phase-6ps-evidence-index.md` PS-BINDER-01 | KFT code can write Fire/Tahoe/Launcher3 per-user state | Static capability; ordinary replay rejected downstream | Confirmed bounded |
| PT-KOR-01 | host-only + saved shell denial | `findings/phase-6dl-kor-retail-demo-boundary.md:147-180` | `ac6c98e250f82949188ef2cd8eea0e85767bda808c00f9f8dccd384a1adc314e` for manifest source | DCP/demo gates precede deletion/component writers | Ordinary route closed; trusted demo route only | Confirmed |
| PT-H2-01 | host-only H2 audit | `work/luna_worker_high_holder_kor_provisioning_closure_20260810.md` | `ef74f8e644b2f10d1d32594cb7eba77916ecd22750819324169dc5a13864cc83` | Signature BIND_SERVICE gates H2 profile lifecycle; no HOME sink in bounded scan | Ordinary bind route closed | Strong evidence |
| PT-MP-01 | host-only provisioning closure | `work/luna_worker_high_holder_kor_provisioning_closure_20260810.md` | `ef74f8e644b2f10d1d32594cb7eba77916ecd22750819324169dc5a13864cc83` | Privileged provisioning holder exists; exact sink corpus incomplete | Do not infer bypass | Unknown |
| PT-DPM-01 | host-only parent/profile/DPM closure | `work/luna_worker_parent_profile_dpm_sink_closure_20260810.md` | `33a1c241f22b30f2276b4ccc3461b4926e0556e5650d743af4d32e97852d1002` | DPM preferred writer requires admin/owner and system-server path | Trusted policy route only | Strong evidence |
| PT-DEPUTY-01 | existing physical validation | `findings/phase-6er-amazon-prewarm-confused-deputy.md` | existing report evidence | Ordinary APK reaches bounded process prewarm | No package/HOME/root effect | Confirmed bounded |
| PT-DEPUTY-02 | existing physical validation | `findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md` | existing report evidence | Ordinary APK writes fixed setup flags, then rollback | No package/HOME/root effect | Confirmed bounded |
| PT-RISK-01 | host-only kernel/OTA closure | `work/luna_worker_kernel_ota_unclosed_closure_20260810.csv` | `a54a4fe8783263d3f75109c1a9f67bf9991f24cb2e7e242aaf9d251ebd1b64fb` | Driver, updater, init and GhostLock remain capability-only or unclosed | Unsafe runtime testing rejected | Strong evidence |
| PT-OUT-01 | new integrated matrix | `output/tables/phase6pt-privilege-route-closure.csv` | `0fd4528137f240df18439d1daf7c193b417ec1f7a1b2bd0599f6745aa493e186` | Caller, gate, sink and disposition are separated per route | Reproducible integration table | Confirmed |
| PT-OUT-02 | new integrated graph | `output/call-graphs/phase6pt-privilege-route.mmd` | `d8c79ac9a68d1c88773085d7703f845a1e557ba37bab465ce78e7954d7a473d5` | Ordinary caller splits into bounded deputies, trusted gates and rejected capabilities | Visual summary only; unresolved edges stay labelled | Confirmed |
| PT-OUT-03 | new broad report | `findings/phase-6pt-broad-privilege-surface.md` | `9631a4c6b83f8cbde41c981721773254bf3c3a86d2af56882d604671d14c6f0f` | Broad privilege-holder and sink closure | No ordinary-to-system/root transition found | Strong evidence |
| PT-OUT-04 | new Vending receiver report | `findings/phase-6pt-vending-receiver-analysis.md` | `d93f1ab60ef3aca68f148627deb326662b3b01aac407edd53232a1740e58d566` | Exported receiver is bounded restore metadata path | No bounded Fire/HOME setter | Strong evidence |

## Confidence vocabulary

本 index 只使用 `Confirmed`、`Strong evidence`、`Unknown`、`bounded` 与
`risk-rejected` 等明确限定。holder、static capability、trusted lifecycle
不自动升级为 privilege escalation。
