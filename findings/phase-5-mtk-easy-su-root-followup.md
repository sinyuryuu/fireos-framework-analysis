# Phase 5 — follow-up observation after Root-control test

## Classification

**已證實：** a later observation captured the test APK running its device
preflight commands after the APK had been launched. The recorded signals do
not prove that temporary root was obtained.

**已證實：** the package was absent in the post-observation package query,
SELinux was `Enforcing`, and the device fingerprint was unchanged.

**待驗證：** the exact application-visible failure text and the exit status
returned by the opaque `mtk-su` child process were not captured in this
follow-up directory.

## Observed sequence

The observation directory is:

`adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/`

At `19:24:23` the package was explicitly launched as an ordinary application
from shell UID 2000. At approximately `19:24:54`, `19:24:59`, `19:25:12`, and
`19:25:15`, logcat recorded child processes from the untrusted-app domain
attempting:

- `getprop ro.vendor.product.model`, rejected by the property access policy;
- `cat /proc/version`, rejected by the SELinux `proc_version` policy.

The offline JADX review maps these two commands to the APK's Root-handler
preflight sequence in `W0/c.java`. This is **strong evidence that the Root
control path reached its preflight stage**, but it is not proof that `mtk-su`
obtained UID 0.

There is no recorded `uid=0`, successful `su -c id`, `getenforce=Permissive`,
or successful `/sbin/su` check. The post-observation package query is empty and
the device remained on the original build.

## Result

The practical result is **failed / no confirmed root**. The failure boundary
is narrower than “the APK never ran”: the app reached at least its ordinary
user preflight, while the privilege-transition result was not successful or
not observable. The exact failure branch remains unresolved because the
payload's opaque native process output and the final in-app log text were not
captured in this observation.

## Safety and rollback

- Fire Launcher was not disabled, hidden, suspended, uninstalled, or cleared.
- No system, boot, vendor, product, or userdata partition was written.
- No `su -c id` command was issued by the host.
- The test package is absent from the recorded post-observation state.
- Current read-only checks again show ADB `device`, Fire HOME, green verified
  boot, `ro.boot.flash.locked=1`, and SELinux `Enforcing`.

## Evidence

- `P5-ROOT-003` in `findings/phase-5-evidence-index.md`
- `adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/logcat.txt`
- `adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/package.txt`
- `adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/fingerprint.txt`
- `adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/selinux.txt`

## Next step

The next useful action is offline payload analysis and exact-device
compatibility review. Reinstalling the APK or acknowledging its warning and
retrying the Root control is not repeated automatically; it would require a
new exact Level 3 scope if the researcher wants another device-side attempt.
