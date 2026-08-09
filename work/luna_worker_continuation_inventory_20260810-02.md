# Luna worker continuation inventory — 2026-08-10-02

## Scope and baseline

This is a host-only, read-only inventory. `git rev-parse HEAD` and
`git rev-parse origin/main` both returned
`17cceb43a29d2b3af7914ecfaa0aca4f4842c668`. No device was contacted. No
existing file was changed; this report is the only file added by this run.

The inventory is evidence bookkeeping, not a vulnerability or privilege-
escalation claim. Phase 3A–6MX results were treated as prior work; no prior
component-disable or 6MV runtime capture was repeated.

## Host-only commands and results

Commands executed in the repository root:

```text
git rev-parse HEAD
git rev-parse origin/main
stat -f '%z %N' <canonical inputs>; sha256sum <canonical inputs>
for d in artifacts/phase6mw-home-state-sinks-20260810-01 \
  artifacts/phase6mx-amazon-pm-callers-20260810-01 \
  artifacts/phase6mi-source-tar-eof-20260810-03; do
  (cd "$d" && sha256sum -c sha256sums.txt)
done
python3 -B tools/scripts/audit_phase6mw_home_state_sinks.py --help
python3 -B tools/scripts/audit_phase6mw_home_state_sinks.py --dry-run
python3 -B tools/scripts/audit_phase6mx_amazon_pm_callers.py --help
python3 -B tools/scripts/audit_phase6mx_amazon_pm_callers.py --dry-run
rg --files firmware artifacts | rg '(fosservices\.jar|framework\.jar|services\.jar|FireLauncher|boot-framework|\.vdex$|\.oat$)'
git status --short -- work/luna_worker_continuation_inventory_20260810-02.md
```

Results: all three artifact manifests returned `OK` for every listed member.
The 6MW dry-run returned `adb:false`, `binder_transaction:false`,
`device_mutation:false`, `host_only:true`, `input_count:21875`,
`java_file_count:21871`, and `disassembly_file_count:4`. The 6MX dry-run
returned `adb:false`, `device_mutation:false`, `host_only:true`,
`input_count:3`, and `inputs_exist:true`. The framework search found only
pull-log records for the named framework files in the `firmware/manifests`
directories, not corresponding local jar/vdex payloads at those paths.

## PS7331 source, OTA, boot and framework-related inputs

The following are present and hashable at reproducible repository paths:

| Classification | Path | Bytes | SHA-256 |
|---|---|---:|---|
| Confirmed | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | 2,563,328,975 | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| Confirmed | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | 1,301,005,356 | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` |
| Confirmed | `firmware/extracted/PS7331/boot.img` | 9,885,696 | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |
| Confirmed | `firmware/extracted/PS7331/system.img` | 3,808,428,032 | `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5` |
| Confirmed | `firmware/extracted/PS7331/vendor.img` | 419,430,400 | `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb` |
| Confirmed | `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | 1,749,792 | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| Confirmed | `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | 2,104 | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| Confirmed | `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | 688,250,880 | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` |
| Confirmed | `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | 1,617,756,160 | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` |

Framework pull records (record existence only; not local binary existence)
are:

```text
firmware/manifests/ARTIFACT-20260803-01/pull_path__system_framework_services.jar.log
firmware/manifests/ARTIFACT-20260803-01/pull_path__system_framework_fosframework.jar.log
firmware/manifests/ARTIFACT-20260803-01/pull_path__system_framework_framework.jar.log
firmware/manifests/ARTIFACT-20260803-02/pull_path__system_framework_boot-framework.vdex.log
firmware/manifests/ARTIFACT-20260803-02/pull_path__system_framework_fosservices.jar.log
```

Their log contents record pull sizes of 183, 132801, 183, 20841512, and
200 bytes respectively, but the corresponding jar/vdex payloads were not
found by the bounded `rg --files firmware artifacts` search. Therefore the
payload status is **Pending**, not Confirmed. The source tar, OTA, boot,
system, vendor, updater, and script hashes above are **Confirmed** as local
files; hash alone does not establish execution or a device-side state change.

## Existing findings and residual evidence

### Confirmed / already covered (not repeated)

* `findings/phase-6mw-home-state-sink-closure.md` (SHA-256
  `f7286718ac7a92f11c2d967a01052f2373189f495decb45d9940ddda646b8231`) and
  `artifacts/phase6mw-home-state-sinks-20260810-01/summary.json`
  (`e1320c614c5fc6a6c91d3871fa3be088197c319571bf0b25d2e24711822221bc`)
  record 21,875 preserved Java/disassembly inputs, 175 direct sink/reference
  rows, 59 HOME/preferred or HOME literals, and two direct
  `com.amazon.firelauncher` literals. They explicitly leave native,
  reflective, indirect, and runtime-only consumers pending.
* `findings/phase-6mx-amazon-pm-caller-provenance.md` (SHA-256
  `3df919df5d235fd46a54d9f81fe1f452a1dfe26001d26117edfc45a183801bfa`) and
  `artifacts/phase6mx-amazon-pm-callers-20260810-01/summary.json`
  (`a54d753970247fddee17e5b9952b41eadfdf354f25c1e993307300fc5e82f15f`)
  cover two service-handle lookups, one publication, 30 interface-related
  calls, and 11 methods. No HOME/preferred/enabled-state setter was found.
  Complete `AmazonPackageManagerImpl` instantiation/reflection/generated or
  native caller closure and runtime UID/permission remain pending.
* `findings/phase-6mv-runtime-readonly-report.md` (SHA-256
  `3ea8ff33c75fde654a3208a4c20015a44efe73309720759d259b52b0021eafc8`)
  already contains the read-only HOME observation: User 0 resolves to Fire
  with priority 50, three candidates were recorded, and User 0/User 10 were
  separated. This run did not repeat the capture.
* `findings/phase-6mu-amazon-application-flags-closure.md` (SHA-256
  `e101fe8549ba1aa39b0bc6384d5a1613701f81924002020e1fd5eec4fb0280c6`)
  closes the static flags persistence writer at
  `/data/system/amazon_package_flags.xml` and first consumers, but does not
  establish a HOME/preferred/enabled-state writer.

The prior OTA boundary reports remain the authority for static-only results:
`findings/phase-6i-ota-postinstall.md`,
`findings/phase-6ah-update-binary-validation-write-closure.md` (SHA-256
`4b3bb959091c3b41a1c150040f80a1c436b1ec32e3d9915adb1a1ed3a05a9d28`),
`findings/phase-6md-native-updater-path-audit.md` (SHA-256
`aa8560e22d51c9b141ae063f8a097f28f88304c77d30bee403508f92f6bda1b0`),
`findings/phase-6mk-updater-dispatch-closure.md` (SHA-256
`443c69127293d18903d469f7a670a4b58b208cdbf6402c240ecaeec6e307ecb3`), and
`findings/phase-6mm-updater-blockimage-closure.md` (SHA-256
`f0caa7e810d02f0022180371e0b564f2cef13cd19ed7320fde107a8073d58601`).
They show privileged/static OTA write capability and unresolved interpreter
details, not an ordinary shell caller or an executed OTA route.

The historical ADB launcher workaround is documented in
`findings/phase-6by-adb-task-lock-launcher-workaround.md` (SHA-256
`0fb58712d0caf18e2be7236fcca7e1b8acd98bff6574bb548593c330b6494221`). It is
not a permanent HOME replacement and was not rerun.

### Strong/Probable static leads

* **Strong, bounded static lead:** the residual `BootAfterSystemOTAReceiver`
  to `PackageHelper.setComponentEnabledSetting` user-scope flow in
  `findings/phase-6mf-residual-candidates.md` (SHA-256
  `7610864a21a9bc6696b59dbab9f671a23732241e85f7b6678f46c4c204b90596`). It
  is a possible post-install/package-state writer path, but caller identity,
  exact user argument, and Fire Launcher effect are not closed.
* **Probable but not a conclusion:** KFT launcher enablement is child/profile
  scoped in the existing evidence, while no formal User-0 HOME setter was
  found. This is consistent with the 6MW/6BK static boundary, but does not
  prove absence of indirect/native writers.

### Pending and excluded

Pending: local framework jar/vdex payload recovery or provenance; complete
static closure of the OTA receiver → component-enabled-setting path; generated,
reflection, native, and runtime caller identity portions of 6MX; exact
PackageManagerDenyList membership. The latter was deliberately not read from
the device.

Rejected for this run: ADB, `service call`, Binder transactions, ioctl/device
nodes, reboot, OTA/recovery/flash or updater execution, Root/exploit activity,
and any package/component mutation including disable/hide/suspend/
force-stop/clear of Fire Launcher. These operations are outside the requested
host-only evidence boundary.

## Recommended next minimal non-overlapping task

Perform one bounded host-only static data-flow audit of
`BootAfterSystemOTAReceiver` → `PackageHelper.setComponentEnabledSetting`:
resolve the receiver registration, exact package/component argument, user
scope, permission/caller assumptions, and whether any branch names
`com.amazon.firelauncher` or a HOME/preferred-package state writer. Use only
the preserved JADX/smali/source corpus and emit a small call-edge table with
file/line/hash. Do not execute the receiver, updater, Binder, or any package
operation. This closes the narrow 6MF residual and is non-overlapping with
the completed 6MW sink inventory and 6MX AmazonPackageManager caller matrix.

## Report integrity

This report was created with `apply_patch`; no commit or push was performed.
The final SHA-256 is to be computed after writing and reported by the worker.
