# Phase 8D — host-side final driver join

日期：2026-08-10（Asia/Taipei）  
範圍：只讀、host-side static join；基線為 Phase 7C CSV、PS7331 GPL source、`trona_defconfig`、boot Image/DTB provenance、ueventd/file_contexts/vendor/plat policy artifacts、native inventory/JADX。未執行 kernel/QEMU、open/ioctl、ADB、root、exploit，未設計 payload。

## 結果

輸出 6 條高價值 surface：CMDQ/MDP、ION core、ION MediaTek custom、M4U、uinput、AUXADC。每列依序檢查 `source → final_artifact → node → mode/owner/policy → shipped native caller UID/domain → gate → sink/effect`。只要鏈中任一段沒有直接證據，`status` 即保持 `UNKNOWN`；因此本輪沒有把 source mode、Kconfig、Image string、library marker、policy allow 或 package 名稱推論成實際 caller/reachability。

可閉合的 partial edges：

- CMDQ 有 `/dev/mtk_cmdq` 的 init owner/mode 與 `mtk_cmdq_device` policy reference；仍缺完整 compiled DTB/object/native caller join。
- ION 有保存的 `/dev/ion` metadata、`ion_device` policy reference；`libion`/`libion_mtk` 只證明 library capability，不是 process caller。
- M4U 有 `init.mt8183.rc` 的 `system:media 0440` 與 `M4U_device_device`/mediacodec policy evidence；active misc char branch 在 source `#if 0`，proc label/caller 未閉合。
- uinput 的 source capability 與 `CONFIG_INPUT_UINPUT=y` 確認，但 native/SELinux caller join 是 bounded negative，不等於 node 不存在或一定 deny。
- AUXADC source 明確建立 calibration cdev、`mt-auxadc/dump_auxadc_status` proc 與 writable calibration sysfs；final DT/object/labels/allow/caller 未證實。

## Conservative boundary

`caller` 欄只接受 exact shipped ELF/native function plus UID/domain evidence；JNI、Java package、HAL/library symbol、service name、policy allow 都不足以填入 caller。`sink`/`effect` 僅描述 source-visible sensitive path，不宣稱低權限可達，也不宣稱已造成 package/HOME/PMS/AMS/privilege effect。`missing_edge` 列出縮小 UNKNOWN 所需的下一個靜態證據。

## Evidence anchors

- Phase 7C baseline：`work/luna_worker_phase7c_kernel_driver_closure_20260810.csv`（SHA-256 `a74360ff8b202ae2086eaa8c1e680078acdac2309168e9b9b8ace5e083ff3cf8`）。
- Final node/policy/caller cross-check：`work/luna_worker_phase6sg_driver_join_20260810.csv`（`6cb000e68c9391a2b954966944a41facb31d9c6fed8372c07b8fb4ce07441111`）、`work/luna_worker_phase6vc_driver_caller_policy_20260810.csv`（`8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0`）。
- Native/uinput and source-control cross-check：`work/luna_worker_phase6xg_driver_20260810.csv`（`20a47a755613dcfd967624d9821060534e9cda38286a7bb2f8ee777ed9e9a225`）、`artifacts/phase6me-driver-control-edges-20260810-01/driver-control-markers.csv`（`077a7cff0d60ae2329986382ef91118819045c3540ec76d0d9eeffb2c67230e3`）。
- Per-row source hashes and evidence paths are recorded in the companion CSV.

## Deliverables

- [CSV](luna_worker_phase8d_driver_final_join_20260810.csv)
- [MD](luna_worker_phase8d_driver_final_join_20260810.md)
