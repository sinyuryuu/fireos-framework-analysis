# Phase 3A HOME priority experiment

## Status

`EXECUTED_AND_RESTORED`

The read-only pre-snapshot was captured, five APK variants were built, and the
approved reversible tests were run. P0 was interrupted during the first
interactive runner attempt after reboot; its raw evidence was preserved and a
separate recovery sequence completed successfully. P49, P50, P51, and P100
completed the full runner sequence.

No Fire Launcher disable, hide, suspend, uninstall, data clear, deny-list
change, system-partition write, Root, or bootloader operation was performed.

## Pre-snapshot

- Test ID: `HOME-PRIORITY-PRE`
- Serial: `G001LT0511550CFT`
- HOME resolver: `com.amazon.firelauncher/.Launcher`, effective priority 50
- HOME candidates: Fire 50, Microsoft 0, Settings FallbackHome -1000
- Snapshot: `adb/mutation-tests/HOME-PRIORITY-PRE/`
- SHA-256 manifest: `adb/mutation-tests/HOME-PRIORITY-PRE/sha256sums.txt`
- Metadata records `read_only=true` and `state_change_executed=false`.

Evidence: `P3A-PRE-001`, `P3A-PRE-002`.

## Build artifacts

The variants were built with the local raw SDK toolchain, OpenJDK 26.0.1,
Android platform 35, and build-tools 35.0.0. AGP and Gradle were not used.
The temporary signing keystore was outside the repository and was not
published.

| Package | Declared manifest priority | APK SHA-256 |
|---|---:|---|
| `org.fireosresearch.home.p0` | 0 | `957f6cc71fd608730582400175f64306aa5ca65eb35ec3e98f4964980df52f70` |
| `org.fireosresearch.home.p49` | 49 | `bad23c71ea344d0106eeed36ceb97c1f144e31a64a7981787b9512cf0b248998` |
| `org.fireosresearch.home.p50` | 50 | `a5cab06fc763dfc99f1b51c2df177f3d79786fa7b4e5a410d74f4e12e3aca007` |
| `org.fireosresearch.home.p51` | 51 | `350d497d9603b479e1453b36685646760bd62a65e8c4a02c1ff9d1665653713c` |
| `org.fireosresearch.home.p100` | 100 | `4fd22ad14b02635a72733d062f3d999f9fb37b758f7434b7addc32db38b20c12` |

Build output and source archive: `tools/test-launcher/dist/20260803-jdk26/`.
The APK manifests were independently inspected with `aapt2 dump xmltree` and
each APK verified with `apksigner` using APK Signature Scheme v3.

Evidence: `P3A-BUILD-001`, `P3A-BUILD-002`.

## Runtime result matrix

The `query-activities` output is the effective PackageManager value, not the
raw manifest declaration.

| Test ID | Declared | Effective candidate priority | After `set-home-activity` | HOME intent / Home key | Immediate post-reboot probe | After post-reboot Home | Final |
|---|---:|---:|---:|---|---|---|---|
| `HOME-PRIORITY-P0` | 0 | 0 | Fire | Fire | PackageManager not ready at interrupted probe | Fire after recovery | `RESTORED_FIRE` |
| `HOME-PRIORITY-P49` | 49 | 0 | Fire | Fire | FallbackHome -1000 transient | Fire | `RESTORED_FIRE` |
| `HOME-PRIORITY-P50` | 50 | 0 | Fire | Fire | FallbackHome -1000 transient | Fire | `RESTORED_FIRE` |
| `HOME-PRIORITY-P51` | 51 | 0 | Fire | Fire | FallbackHome -1000 transient | Fire | `RESTORED_FIRE` |
| `HOME-PRIORITY-P100` | 100 | 0 | Fire | Fire | FallbackHome -1000 transient | Fire | `RESTORED_FIRE` |

For P49/P50/P51/P100, `set-home-activity` returned `Success` and the
post-command preferred dump contained the test package with `mAlways=true`,
but `resolve-activity`, the post-key state, and the final state still selected
Fire. The raw candidate, preferred, activity, window, logcat, reboot, and
restore files are retained under each `adb/mutation-tests/HOME-PRIORITY-P*/`
directory.

Evidence: `P3A-RUN-001`, `P3A-RUN-P49`, `P3A-RUN-P50`, `P3A-RUN-P51`,
`P3A-RUN-P100`, `P3A-P0-RECOVERY`.

## Priority interpretation

`aapt2 dump xmltree` confirms that the requested priorities 49, 50, 51, and
100 are present in the APK manifests. The device nevertheless reports every
sideloaded research package at effective priority 0. The matching Fire VDEX
contains `ActivityIntentResolver.adjustPriority()` with the Android 9 standard
non-privileged priority cap; the AOSP r1/r61 method has the same logic. Fire
Launcher is a privileged system package and retains its manifest priority 50.

Therefore the result is:

- `Confirmed`: normal ADB-installed, non-privileged applications cannot use a
  positive HOME intent-filter priority on this Android 9 PackageManager path.
- `Strong evidence`: Fire's effective priority 50 plus the ordinary preferred
  ranking path explains why the test packages did not replace Fire.
- `Unknown`: whether a privileged/system-signed third-party package with an
  effective priority above 50 would win. Producing that condition would
  require a different trust boundary and is outside this no-Root Phase 3A
  experiment.
- `Disproved`: the simple hypothesis that a normal ADB-installed APK declaring
  priority 51 or 100 can outrank Fire.

This experiment does not prove an Amazon-only resolver priority modification.
It instead confirms the AOSP priority normalization boundary and Fire's
privileged manifest choice.

Evidence: `P3A-STATIC-001`, `P3A-STATIC-002`, `P3A-STATIC-003`,
`P3A-STATIC-004`.

## Preferred activity and command compatibility

The ordinary preferred record can be written by shell, but it does not become
the effective HOME when Fire remains the higher-ranked candidate. This matches
the static `chooseBestActivity()` ordering: ranking fields are compared before
ordinary preferred activity is consulted.

The requested cleanup command was tested and preserved:

```text
cmd package clear-package-preferred-activities PACKAGE
Unknown command: clear-package-preferred-activities
```

This Fire OS build does not expose that command. Recovery used the supported
`cmd package set-home-activity com.amazon.firelauncher/com.amazon.firelauncher.Launcher`
path followed by test-package uninstall; all final resolver checks returned
Fire and all test package paths were absent.

Evidence: `P3A-CLEAN-001`, `P3A-POST-001`.

## Evidence IDs

The detailed evidence records, commands, timestamps, and SHA-256 values are
indexed in `findings/evidence-index-phase2.md`.

## Reproduction and evidence locations

- Source/build: `tools/test-launcher/`
- Runner: `tools/scripts/run_home_priority_experiment.sh`
- Matrix: `output/tables/home-priority-matrix.csv`
- P0 recovery: `adb/mutation-tests/HOME-PRIORITY-P0/recovery-20260803T062741Z/`
- Static resolver analysis: `findings/home-resolver-method-analysis.md`
- AOSP comparison: `diff/reports/home-resolver-aosp-fireos-diff.md`
