# MTK Easy SU follow-up observation

- Test ID: `MTK-EASY-SU-ROOT-T02-OBS`
- Scope: read-only capture after a device-side test
- Package query: absent at capture time
- SELinux: `Enforcing`
- Build fingerprint: unchanged PS7330.4104N fingerprint
- Root result: not confirmed

Logcat contains repeated ordinary-app preflight attempts for
`getprop ro.vendor.product.model` and `cat /proc/version`; both are denied by
the device policy. The static mapping and interpretation are in
`findings/phase-5-mtk-easy-su-root-followup.md`.
