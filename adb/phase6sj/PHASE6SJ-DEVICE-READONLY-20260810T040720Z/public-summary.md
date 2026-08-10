# Redacted public summary — Phase 6SJ device snapshot

Capture time: 2026-08-10T04:07:20Z
Device serial: intentionally redacted from the public artifact.
Collection mode: read-only ADB; all 17 commands returned exit code 0.

## Observed state

- Fire OS build fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Android API: 28
- Kernel: Linux 4.4.146, AArch64
- SELinux: Enforcing
- HOME resolver: `com.amazon.firelauncher/.Launcher`, priority 50
- HOME candidates: Fire Launcher priority 50; Microsoft Launcher priority 0; Settings FallbackHome priority -1000
- Preferred record: Fire Launcher, `mAlways=true`, `mMatch=0x100000`
- Foreground: resumed activity and current window focus are Fire Launcher
- Fire package state: User 0 `enabled=0` (default); User 10 `enabled=2` in the observed snapshot
- `dumpsys role`: no output in this build

## Safety and privacy

The unredacted local snapshot is retained outside the public commit for reproducibility
and audit. The raw secure-settings output contained an Amazon account identifier, so the
raw snapshot, full settings dumps and device serial are intentionally not published.
This summary contains no account identifier, token, password, network credential or
private Binder/driver/OTA result.

The capture script is:
`tools/scripts/capture_phase6sj_readonly.sh`.
