# Phase 5AY OTA URI static-review artifact

This directory is generated from the preserved DeviceSoftwareOTA APK by
`tools/scripts/analyze_phase5ay_ota_uri_static.py`.

Input:

- `artifacts/phase3b-ota/com.amazon.device.software.ota__0_DeviceSoftwareOTA.apk`
- SHA-256: `4a00b81fda6259e1309d9c6c3021e7d958be8bc6341a49b1278216580824b2a0`

The script runs JADX 1.5.6 in a temporary directory and retains only compact
metadata, line excerpts, logs and a TSV finding index. It does not execute the
APK, connect to a device, make network requests, or read the OTA app's private
data. `sha256sums.txt` covers the generated files except itself.

The report uses this corrected `-04` output. Earlier `-01` through `-03`
directories are retained as local generation history and are not required for
the conclusion.
