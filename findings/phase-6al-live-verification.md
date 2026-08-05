# Phase 6AL live verification — read-only PS7331 corroboration

## Scope

This is a read-only capture from the research tablet, serial
`G001LT0511550CFT`, at `2026-08-05T00:45:22Z`.  It used only explicit-serial
`getprop`, `cmd package`, `dumpsys`, `service list`, `service check`, `settings
get`, and metadata `ls` commands.  No activity was started, no private Binder
transaction was sent, no package/settings state was changed, and no reboot was
requested.

Raw captures:

- `adb/phase6al/PHASE6AL-HOME-20260805-01/`
- `adb/phase6al/PHASE6AL-LIVE-20260805-01/`

## Results

### 已證實

- Build fingerprint remains
  `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`.
- The current formal HOME resolver remains:
  `priority=50 ... com.amazon.firelauncher/.Launcher`.
- The current activity snapshot has
  `mResumedActivity ... com.amazon.firelauncher/.Launcher`; the window snapshot
  has `mCurrentFocus` on the Fire Launcher window.
- Standard `service check` found `fosdebug`, `amazonthermalservice`, and
  `otadexopt`.  This capture used only their standard `dumpsys` paths; it did
  not call their private transaction interfaces.

### 高可信推論

- The live state is consistent with the host-only callback closure: the
  preserved resolver callbacks do not need to inject a Fire component to
  explain the observed final PM result.  The result is still consistent with
  the privileged Fire candidate and PackageManager HOME state.

### 待驗證

- A live callback return object was not instrumented.  Doing so would require
  framework instrumentation or a private service call, neither of which is
  appropriate on the stock tablet.

### 已排除／因風險拒絕

- This capture provides no evidence of a shell-writable HOME replacement or a
  root transition.
- Unknown Binder transactions, service fuzzing, OOBE/OTA replay, package-state
  mutation, and root/partition operations were not performed.

## Selected evidence hashes

| File | SHA-256 |
|---|---|
| `adb/phase6al/PHASE6AL-HOME-20260805-01/fingerprint.stdout.txt` | `15efeeb538e9463865e2851c32dc3142d71c8412b8b55447506b1d65db402e4b` |
| `adb/phase6al/PHASE6AL-HOME-20260805-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` |
| `adb/phase6al/PHASE6AL-HOME-20260805-01/activity_state.stdout.txt` | `b5bf3417f9e14e7825412f8508c02dbb3af69fd8feb5f32b77a16d527eaecbf4` |
| `adb/phase6al/PHASE6AL-HOME-20260805-01/window_state.stdout.txt` | `74b4aab1fc38c1138b742066aff20b9649a96e9fc2ec48b73b86340c1edc869b` |
| `adb/phase6al/PHASE6AL-LIVE-20260805-01/metadata.json` | `f2c737dcf040290c576b869e73932f11d354a6ce3236c7030c7a01793bf8e9d3` |

The per-directory `sha256sums.txt` files contain the complete raw-output
manifests.
