# Phase 6O — KFT per-user and OTA fixed-target boundary

Date: 2026-08-10

## Result

This phase closes two remaining, high-impact hypotheses using preserved PS7331
artifacts and a previously rolled-back child-profile observation. It does not
contact the tablet and does not execute an OTA or private Binder transaction.

The evidence supports a per-user KFT launcher state writer, not a User-0
launcher replacement path. It also supports a fixed-target, privileged OTA
control plane, not an ordinary-app or shell post-install writer.

## Findings

- **已證實：** `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)` is a private helper that enables Tahoe's `FreeTimeLauncherActivity` and requests state `2` for `com.amazon.firelauncher` and `com.android.launcher3` for the supplied user. Source/disassembly evidence is at lines 54297–54325 of the preserved method index and selected snippets.
- **已證實：** the prior reversible profile-switch capture is user-scoped: User 10 resolved Tahoe at priority 975; after returning to User 0, HOME resolved to `com.amazon.firelauncher/.Launcher` at priority 50; rollback succeeded.
- **已證實：** the PS7331 updater script uses fixed system/vendor block-image targets and fixed boot/firmware partition targets. The preserved audit reports no archive traversal/symlink path, duplicate file-map path, or post-install executor.
- **已證實：** OTA control receivers and `OtaService` are gated by `signature|privileged` controller permission and single-user policy. OTA lifecycle broadcasts are sourced from the system permission package and are protected.
- **已排除（目前證據範圍）：** no ordinary shell/App caller to the KFT writer or OTA writer was established, and neither path is evidence of a User-0 HOME replacement.
- **待驗證：** a complete CFG/data-flow review of the native `update-binary` parser and a byte-complete audit of the outer source archive remain host-only gaps. They do not justify device execution.

## Evidence bundle

The reproducible host-only builder and generated bundle are:

- [build_phase6o_control_boundary.py](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/tools/scripts/build_phase6o_control_boundary.py)
- [generated result](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6o/control-boundary-20260810-01/result.md)
- [evidence CSV](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6o/control-boundary-20260810-01/evidence.csv)
- [input hashes](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6o/control-boundary-20260810-01/input-sha256.json)
- [bundle hashes](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6o/control-boundary-20260810-01/sha256sums.txt)

Evidence IDs in the bundle: `6O-KFT-001`, `6O-KFT-002`, `6O-USER-001`,
`6O-OTA-001` through `6O-OTA-004`.

## Safety boundary

No root attempt, unknown Binder transaction, malformed ioctl, synthetic
protected broadcast, recovery/sideload, partition write, Fire Launcher
disable/hide/suspend/uninstall/clear, or factory reset was performed. The
child-user result records a prior successful rollback; this phase performed no
new profile mutation.

## Next direction

The remaining safe work is host-only native updater CFG review and broader
artifact inventory. If those do not identify a legitimate unprivileged writer,
the project should return to measuring a reversible foreground launcher
fallback rather than retrying protected package-state routes.
