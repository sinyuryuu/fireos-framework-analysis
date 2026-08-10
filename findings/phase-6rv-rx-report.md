# Phase 6RV–RX — broad privilege-surface closure

Date: 2026-08-10
Device scope: PS7331.4463N / KFTRWI / trona / Android 9 API 28
Public baseline: `47daff30d` (Phase 6RS–RU)

## Executive result

This follow-up widened the review beyond Launcher to every saved surface that
could plausibly change package state, user/profile state, settings, HOME,
input, OTA/recovery, overlay selection, or native control. Three host-only
ledgers contain 48 rows:

| Surface | Rows |
|---|---:|
| Permission holder/caller and Amazon package metadata | 15 |
| SystemUI, callbacks, overlays, and resource writers | 20 |
| OOBE/OTA/native lifecycle and sensitive-sink gaps | 13 |
| **Total** | **48** |

No new ordinary-app or shell-to-sensitive-sink chain was closed. In
particular, no evidence currently connects a low-privilege caller to a trusted
identity transition and then to the Fire package/component state writer. The
statement “a caller with the required system privilege could disable Fire
Launcher” remains true as an authorization consequence, but this phase did not
find a way for an ordinary app or shell to obtain that privilege.

Data-quality note: the preserved RX worker CSV contains unquoted commas in 12
of 13 data rows. The raw file is not overwritten. The normalized matrix marks
the affected trailing fields `UNKNOWN_DUE_TO_UNQUOTED_RAW_CSV` and points back
to the preserved Markdown ledger; it does not silently shift those fields into
another column. This is a ledger-format limitation, not runtime evidence.

## Findings by confidence

### 已證實 / Confirmed

- `amazon.permission.ADD_RM_PKG_METADATA` is declared as `signature|amazon`.
  Its static mutators preserve an explicit user argument and write
  `AmazonApplicationFlags` XML. The exact package holder and production caller
  are not present in the reviewed exact-build grant corpus, so they remain
  `UNKNOWN` rather than being inferred.
- The SystemUI service arrays are bootstrap lists. The per-user array in the
  saved PS7331 resource slice is empty. The inspected callback bodies do not
  construct `com.amazon.firelauncher/.Launcher` or call a preferred-HOME or
  package/component-state writer.
- `DefaultHomePicker`/PMS can persist an ordinary preferred record, while the
  resolver still evaluates candidate ranking. The saved Fire candidate remains
  priority 50 versus ordinary sideloaded priority 0.
- The KFT package-state writer is scoped by a supplied `UserInfo.id` and is
  associated with child/profile lifecycle. It is not evidence of an ordinary
  User-0 shell writer.
- OOBE/OTA and native updater/recovery code contain privileged writers and
  partition sinks, but no ordinary caller chain to them was closed.

### 高可信推論 / Strong evidence

- The current formal HOME result is best explained by the AOSP-shaped resolver
  candidate ranking plus the protected Fire package state, not by a SystemUI
  hardcoded Fire launch found in this corpus.
- `AmazonApplicationFlags` metadata is not itself a HOME or package-state
  control surface in the visible consumers (recency, game-mode, and
  incompatibility classification).
- The previously measured, user-consented Accessibility delayed foreground
  redirect remains the best practical rootless approximation. It is a
  foreground redirect, not HOME replacement, package mutation, or privilege
  transition.

### 待驗證 / Pending

- Exact package grant and production caller for `ADD_RM_PKG_METADATA`.
- Complete exact-build SystemUI callback/class-loader universe and native
  client/domain mapping.
- Exact user propagation for protected OOBE writers and complete native updater
  caller provenance.
- Remaining unreviewed Amazon metadata consumers and package-policy joins.

### 已排除（限定範圍） / Bounded negative

- No explicit Fire component launch was found in the saved SystemUI/Amazon
  callback corpus.
- No `ADD_RM_PKG_METADATA` → HOME, preferred-activity, enabled-state, or
  package-state join was found in the reviewed corpus.
- Ordinary preferred persistence, SettingsProvider writes, UsageStats,
  PendingIntent, foreground monitoring, and the Settings Home picker do not
  constitute a formal HOME replacement or system-identity relay.

### 因風險拒絕測試 / Risk-rejected

No private/unknown Binder transaction, protected broadcast replay, settings or
package mutation, overlay enablement, input injection, driver/procfs access,
OTA/recovery/updater execution, crafted archive, Root/exploit, remount, SELinux
change, reboot, or partition operation was performed.

## Control-surface model

```text
ordinary app / shell
        |
        +--> SettingsProvider permission + user gates --> SettingsState/XML
        |
        +--> PMS preferred API + candidate validation --> preferred XML
        |                                                   |
        |                                                   v
        |                                      HOME resolver ranking
        |                                                   |
        |                                  Fire priority 50 wins
        |
        +--> Amazon PM metadata gate (holder/caller UNKNOWN)
        |                                      |
        |                                      v
        |                         AmazonApplicationFlags XML only
        |
        +--> OOBE/OTA/input/native services -- protected/unknown boundary

KFT child/profile lifecycle --> UserInfo.id-scoped package-state writer
Accessibility consent       --> delayed explicit foreground redirect only
```

The graph separates capability from reachability. A system-server method that
can write package state is not evidence that shell can invoke it, and a native
partition sink is not evidence of a low-privilege caller.

## Main conclusion

The research question is now broader than “can Fire Launcher be disabled?”
The answer remains:

1. **The effect of sufficient system privilege is confirmed by the existing PMS
   package/component writer and KFT lifecycle code.**
2. **A new ordinary-app/shell route to that privilege was not found in this
   phase.**
3. **No current evidence justifies using `ADD_RM_PKG_METADATA`, SystemUI
   callbacks, overlays, OOBE/OTA, input, or native updater paths as a root or
   Fire-disabling route.**
4. **The only measured no-root usability improvement remains a reversible,
   user-consented Accessibility foreground fallback; it does not alter formal
   HOME selection.**

If the remaining host-only provenance closures do not identify an ordinary
caller and accepted gate, the formal HOME/root route should be treated as
closed for the tested build. Any future root/exploit or unknown Binder work
would require a separate safety review and is not part of this evidence set.

## Artifact index

- `work/luna_worker_phase6rv_20260810.md/.csv`
- `work/luna_worker_phase6rw_20260810.md/.csv`
- `work/luna_worker_phase6rx_20260810.md/.csv`
- `output/tables/phase6rv-rx-privilege-surface.csv`
- `output/tables/phase6rv-rx-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6rv-rx-control-surfaces.mmd`
- `output/call-graphs/phase6rv-rx-control-surfaces.md`
- `tools/scripts/build_phase6rv_rx_surface.py`
