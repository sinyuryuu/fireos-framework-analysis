# Phase 6LZ — live baseline and route closure

## Scope and safety

This addendum records one new read-only baseline and the delegated host-only
reviews of the existing Phase 3–6 evidence. It did not install an APK, change
settings, change package state, call a private Binder transaction, issue a
driver ioctl, run an exploit, reboot, or touch OTA/boot partitions.

The raw baseline is recorded in the repository at:

`adb/phase6lz/PHASE6LZ-BASELINE-20260810-01/`

It was captured with the tracked read-only collector
`tools/scripts/capture_phase6ee_current_baseline.py`. The capture metadata and
every raw output have SHA-256 entries in `sha256sums.txt`; the metadata hash is
`2ebebe79817a91f01ec64638d25bef0527a215542b87944bdb032ca4b8cb8679`.

## Current device observation

The saved fingerprint is:

`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`

The current user was 0 and SELinux was `Enforcing`. A pre-existing user 10 was
present; this capture did not create, switch to, or delete it.

For User 0, the resolver returned:

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

The saved candidate set contained Fire Launcher, Microsoft Launcher at
effective priority 0, and `FallbackHome` at -1000. For User 10 the saved
candidate set contained only `FallbackHome`; this is not evidence of a User-0
replacement.

## Evidence-backed route review

### 已證實

- The formal User-0 HOME remains Fire Launcher with effective priority 50.
- The ordinary preferred record and `set-home-activity` route do not overcome
  the observed candidate selection; the existing Phase 3A–3C experiments were
  not repeated.
- `setComponentEnabledSetting()` protection rejects Fire Launcher before its
  package/component state changes. The new permission-holder inventory finds
  11 package blocks with `CHANGE_COMPONENT_ENABLED_STATE`, but a granted
  permission is not a protected-package bypass.
- The only confirmed Amazon launcher-state writer in the preserved framework
  path is the KFT child/profile lifecycle writer. It enables Tahoe's child
  launcher and disables Fire Launcher for the supplied child/profile user ID;
  no ordinary User-0 shell reachability was found.
- Saved checks and SELinux evidence do not expose the relevant Amazon private
  Binder services to ordinary shell. The inspected HOME callbacks delegate to
  PackageManager or return null and contain no Fire component injection.
- The official PS7331 updater script uses fixed partition targets and has no
  observed dynamic post-install command, archive traversal, or symlink-based
  file writer. The OOBE OTA receiver is a guarded setup-state path, not a
  normal HOME selector.

### 高可信推論

- The remaining formal replacement boundary is privileged/system identity or
  a protected lifecycle event, rather than an untested ordinary settings key.
- The current `com.android.vending` grant is provenance-anomalous because the
  saved package is a `/data/app` package without the `PRIVILEGED` private flag
  and its signature digest differs from the framework `android` package. The
  dump does not establish how the grant was persisted or whether the app can
  invoke a protected-package state change. It must not be treated as a route.
- The PS7331 futex/rtmutex and CMDQ observations remain static or
  unconfirmed kernel candidates. They do not provide a demonstrated HOME
  writer or privilege transition, so no physical-device exploit probe is
  justified by the current evidence.

### 已排除

- Repeating ordinary priority, preferred-activity, component-disable, or
  equivalent shell setter tests without a changed premise.
- Treating a foreground Accessibility/ADB redirect as a formal HOME
  replacement; the existing evidence showed a temporary foreground fallback,
  not a resolver change.
- Using GED/CMDQ/Amazon driver nodes as a launcher-control path; the audited
  source has no driver-to-PMS/AMS/ATMS/HOME edge.
- Treating OTA/OOBE or KFT child-user writers as ordinary User-0 shell APIs.

### 待驗證／無法取得證據

1. The exact current device-protected `PackageManagerDenyList` entry remains
   unreadable to shell. Static source and the observed rejection establish the
   gate, but not the on-device list serialization.
2. Native `fosinit` callback registration outside the preserved VDEX/XML scope
   is not universally closed.
3. The physical hardware Home-button path is not fully reconstructed from the
   available artifacts.
4. The origin of the Play Store permission grant needs an artifact from the
   matching install/provisioning history; invoking or modifying Play Store is
   not an acceptable provenance test.

## Final disposition

No new safe, shell-reachable route was found that formally replaces Fire
Launcher or disables it for User 0. The best demonstrated alternative remains
a user-authorized foreground redirect, with the documented limitations and no
claim of HOME replacement. Further progress should be host-only completeness
analysis or an explicitly bounded, user-visible redirect experiment; it should
not escalate to unknown Binder payloads, malformed driver input, root exploits,
or partition writes.

## Reproduction

```sh
python3 tools/scripts/capture_phase6ee_current_baseline.py \
  --serial G001LT0511550CFT \
  --output adb/phase6lz/PHASE6LZ-BASELINE-20260810-01
```

The output path must be new because the collector refuses to overwrite an
existing directory. The command is read-only apart from saving host-side
evidence.
