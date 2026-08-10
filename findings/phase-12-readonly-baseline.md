# Phase 12 — current read-only baseline

## Scope

This capture is a serial-bound, read-only baseline for the next control-surface
review. It did not perform a Binder transaction, private service lookup,
package/settings mutation, user switch, reboot, OTA/recovery operation, driver
I/O, or kernel operation.

## Device

- Serial: `G001LT0511550CFT`
- Product/model: `trona` / `KFTRWI`
- Fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Current user: `0`
- SELinux: `Enforcing`
- Capture directory: [`adb/phase12/PHASE12-BASELINE-20260810-01`](../adb/phase12/PHASE12-BASELINE-20260810-01)
- Capture script: [`capture_phase6ee_current_baseline.py`](../tools/scripts/capture_phase6ee_current_baseline.py)

## Observed state

| Scope | Observation | Confidence |
|---|---|---|
| ADB | `device` | Confirmed |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority `50`, `isDefault=true` | Confirmed |
| User 10 HOME | `com.android.settings/.FallbackHome`, priority `-1000` | Confirmed |
| SELinux | `Enforcing` | Confirmed |
| Device state changes | None requested by the capture | Confirmed |

The complete raw stdout/stderr set, metadata, command list, and SHA-256
manifest are retained in the capture directory. The manifest was verified with
`shasum -a 256 -c sha256sums.txt`.

## Reproduction

```sh
python3 tools/scripts/capture_phase6ee_current_baseline.py \
  --serial G001LT0511550CFT \
  --output adb/phase12/PHASE12-BASELINE-20260810-01
(cd adb/phase12/PHASE12-BASELINE-20260810-01 && shasum -a 256 -c sha256sums.txt)
```

This baseline is evidence of the state at capture time only; it does not by
itself identify the writer or protection gate responsible for the HOME result.
