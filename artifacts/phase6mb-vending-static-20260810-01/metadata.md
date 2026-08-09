# Phase 6MB — `com.android.vending` static audit metadata

Capture date: 2026-08-10 (Asia/Taipei)

## Device-side read-only source

- Serial: `DEVICE_SERIAL_REDACTED` (unredacted value remains only in local ADB command history/raw evidence)
- Fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Model/device: `KFTRWI` / `trona`
- Security patch: `2024-08-01`
- Package paths are recorded in `adb/phase6mb-vending-20260810-01/pm_path_vending.txt`.
- No package state, setting, preferred activity, process, service, or firmware state was changed.

## Pulled APK inputs

| File | SHA-256 | Notes |
|---|---|---|
| `base.apk` | `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916b9b25d5297a50` | `/data/app`; versionCode `84893000`, versionName `48.9.30-23 [0] [PR] 834517506` |
| `split_config.arm64_v8a.apk` | `b59980b4c8764f59c20289c19935fa4da497d799e2a4763ca163c5ef1928f90a` | Pulled from the same package split set |
| `split_config.ja.apk` | `b55b5c31a778187abb394f169e95af79844ac93cfd4b242ea58383e6531df0ed` | Pulled from the same package split set |

The original APKs are under `artifacts/phase6mb-vending-static-20260810-01/`.

## Analysis tools and limitations

- `apkanalyzer manifest print` was used for the manifest projection; the exact output is `manifest-print.txt`.
- JADX was run with `JAVA_HOME=/opt/homebrew/opt/openjdk`, six threads, no debug info/imports. It returned exit code 3 after producing 52,327 Java files and known decompiler warnings. The generated Java is evidence of candidate call sites only; critical claims must be checked against DEX/smali if this route remains in scope.
- A literal search for `com.amazon.firelauncher` in the generated source returned zero matches. This is strong bounded evidence, not proof about code hidden in resources, native code, or failed decompilation regions.
- The reproducible host-only scan is `tools/scripts/audit_vending_state_writers.py`; its output is `output/tables/phase6mb-vending-state-writer-scan.csv` and the scan summary is `static-search-summary.md`.

## Permission/provenance note

The live package dump records `CHANGE_COMPONENT_ENABLED_STATE`, `INSTALL_PACKAGES`, `DELETE_PACKAGES`, `MANAGE_USERS`, `WRITE_SECURE_SETTINGS`, `REBOOT`, and `FORCE_STOP_PACKAGES` as requested/granted for `com.android.vending`. The package is installed from `/data/app` and its private flags do not include `PRIVATE_FLAG_PRIVILEGED`. This is a provenance anomaly worth recording, but it is not evidence that the package can bypass PackageManager's protected-package gate.

The extracted PS7331 `privapp_permissions.xml` and `privapp-permissions-platform.xml` were searched and contain no direct `com.android.vending` grant block. This is a version-scoped correlation only; it does not prove which install-time or persisted state produced the live grants.
