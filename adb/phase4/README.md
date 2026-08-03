# Phase 4 device experiment archive

All runs use serial `G001LT0511550CFT` and the PS7330.4104N KFTRWI build. The
runner rejects Fire Launcher package state changes and never calls
`set-home-activity`.

- `PHASE4-ALIAS-T01`: harness stopped before installation because the first
  stdin-pipe approval design did not survive the read boundary. No device
  mutation occurred.
- `PHASE4-ALIAS-T02`: the test APK was installed, explicitly sampled, and
  uninstalled. The device returned to Fire, but the first runner stopped when
  `pm path` correctly returned non-zero for the expected absent package before
  writing its final snapshot. It is retained as a harness repair record.
- `PHASE4-ALIAS-T03`: completed the repaired flow and rollback; its generated
  result text was produced before the shell-backtick summary fix. It is
  retained but not the canonical report run.
- `PHASE4-ALIAS-T04`: canonical run after the harness fixes. It contains the
  complete before/installed/after-rollback snapshots, event logcat, explicit
  component starts, candidate query, HOME/Keyevent results, rollback diff, and
  final SHA-256 manifest.

The canonical conclusion is based only on T04 plus its final snapshot. The
earlier runs are not treated as independent causal evidence.

## Accessibility redirect runs

- `PHASE4-ACCESSIBILITY-T01`: preparation installed only the redirect and
  alias research APKs. The first 30-cycle attempt was not causal evidence
  because the visible redirect toggle was not confirmed on.
- `PHASE4-ACCESSIBILITY-T02`: retained as a harness repair record. The alias
  APK did not declare the source-only `ProbeActivity`, so its pre-launch
  command returned `Error type 3`; no success-rate conclusion is taken from
  this run.
- `PHASE4-ACCESSIBILITY-T03`: canonical manual-consent run after changing the
  probe to the manifest-declared `HomeActivity`. It recorded 30 explicit
  redirect attempts and 0/30 resumed/focused handoffs; Fire remained resumed.
  The service was manually disabled, both research APKs were removed, and
  the final resolver/ADB checks passed. Use
  `rollback-result-verified.md` rather than the earlier generated summary,
  which was affected by a shell-backtick formatting bug subsequently fixed in
  the runner.
