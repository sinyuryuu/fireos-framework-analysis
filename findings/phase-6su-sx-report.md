# Phase 6SU–SX broad privilege-surface continuation

This bundle integrates four host-only static/evidence audits. It does not treat exported status, a missing local permission check, a kernel symbol, or a privileged capability as proof of low-privilege reachability. A route must show caller → gate → identity/user scope → exact sink.

Generation HEAD: `3504a28728a9daff43897bd4a11137787bac3168`.

## Safety boundary

No ADB, Binder transaction, broadcast, driver open/ioctl, OTA/recovery execution, Root/exploit, reboot, package/settings mutation, or partition write was performed. Raw worker files are retained and output files are generated without overwriting previous evidence.

## Inputs

- **6SU IPC residual:** `work/luna_worker_phase6su_ipc_residual_20260810.md` (5dff1c6d2a6c4ab3d49d9010199201a3a85ebc05d9315942c81a5b9465934a95); `work/luna_worker_phase6su_ipc_residual_20260810.csv` (9fb343157e94c92ce78e482e01f6d70f9791a855dd96ca52baad1e1b8761bd2a); 8 data row(s).
- **6SV exported/protected surface:** `work/luna_worker_phase6sv_exported_surface_20260810.md` (0464606bf29246439cc462751b86b1377b7fd15a9d6b709007c8f42284e301ec); `work/luna_worker_phase6sv_exported_surface_20260810.csv` (b07ce35207afe09da343d573fe9969f1487fd7b0cf00463be73cb42a1394c27d); 4 data row(s).
- **6SW kernel surface:** `work/luna_worker_phase6sw_kernel_surface_20260810.md` (1be76f8f51c368d71853af558d6d6b049fa4f1e661c6cf22c0cccebf402cb13b); `work/luna_worker_phase6sw_kernel_surface_20260810.csv` (4255a2d668488c08ceb1393222eb6c77155b61edb91109f65c1475511a679010); 18 data row(s).
- **6SX evidence audit:** `work/luna_worker_phase6sx_evidence_audit_20260810.md` (734f61046322dc88817be88e97dae6ff4d47966139483a7693cb6fbbb63c097c); `work/luna_worker_phase6sx_evidence_audit_20260810.csv` (c745f206218d34fc9b5f831be7c06686e9fd5adaf6b64acc564843b2eff4a695); 20 data row(s).

## Interpretation

- IPC rows separate declaration, publication, caller, permission, identity and sink. `UNKNOWN` means the saved corpus does not close that edge.
- Exported components and protected broadcasts are inventory evidence only; sender permission, UID, lifecycle predicate and downstream target are required.
- Kernel rows distinguish source/config presence, shipped node/policy, and exact native caller. Source-only ioctl/proc/debugfs code is not a runtime route.
- Evidence-audit rows are a completeness catalog, not new runtime observations.

## Safe continuation

The next justified work is exact-build corpus completeness and naturally obtained read-only state. Unknown Binder transactions, crafted OTA input, driver ioctl/proc writes, Root/exploit payloads and Fire Launcher mutation are not safe validation steps and remain excluded.
