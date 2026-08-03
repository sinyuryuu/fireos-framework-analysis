# OTA provenance — PS7331 adjacent sample

Status: `VERSION_MISMATCH` — retained for adjacent-version analysis only.

## Device build being analysed

| Field | Value |
|---|---|
| Model | `KFTRWI` |
| Product/device | `trona` |
| Installed Fire OS | `7.3.3.0` |
| Installed build | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Installed incremental | `0030099376260` |
| Installed security patch | `2024-02-01` |

Source: `device/baseline/BASELINE-20260803-03/properties/`.

## Downloaded OTA

| Field | Value |
|---|---|
| File | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` |
| Product | `com.amazon.trona.android.os` |
| Version | `Fire OS 7.3.3.1 (PS7331.4463N/4463)` |
| Post-build | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` |
| Post-incremental | `0031575863172` |
| Post-security patch | `2024-08-01` |
| Size | `1,301,005,356` bytes |
| SHA-256 | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` |
| Package format | SignApk-signed ZIP/JAR; contains `system.new.dat.br` and `vendor.new.dat.br` |

The embedded values were read without installing the package:

- `META-INF/com/android/metadata`
- `ota.prop`
- `META-INF/com/amazon/android/target.system.devicepath`
- `META-INF/com/amazon/android/target.blocklist`

## Source and verification

- Official Amazon support page: <https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE?theme=light>
- Official redirect endpoint: <https://www.amazon.com/update_Fire_HD10_11th_Gen>
- Final S3 URL from the Amazon redirect: <https://fireos-tablet-src.s3.us-west-2.amazonaws.com/3omHNOvwW4KDYd5xDz75MnJ9npabcf/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin>
- Independent history/catalog reference: <https://ftvdb.com/firetablet/firmware/com.amazon.trona.android.os/>

The official support page currently labels this device family as Fire OS 7.3.3.1. Its embedded OTA metadata confirms `PS7331.4463N`, not the installed `PS7330.4104N`. Therefore this file must not be used as evidence of the exact installed firmware, and must not be flashed to the device.

The original OTA is preserved separately from all extracted or normalized output. No device state was changed while acquiring or inspecting it.

## Derived read-only analysis outputs

The ZIP was extracted to `firmware/extracted/PS7331/`. The `system.new.dat.br` and `vendor.new.dat.br` payloads were decompressed and converted with `tools/scripts/convert_dat_to_img.py` into read-only analysis images; the original OTA and `.new.dat` inputs were not modified.

| Derived artifact | SHA-256 | Notes |
|---|---|---|
| `firmware/extracted/PS7331/system.img` | `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5` | Reconstructed from `system.transfer.list` and `system.new.dat` |
| `firmware/extracted/PS7331/vendor.img` | `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb` | Reconstructed from `vendor.transfer.list` and `vendor.new.dat` |
| `firmware/extracted/PS7331/selected/` | See `extraction-manifest.tsv` | Selected framework/APK paths extracted read-only with `debugfs` |
| `firmware/extracted/PS7331/compiled-02/` | See `extraction-manifest.tsv` | Selected VDEX/ODEX paths extracted read-only with `debugfs` |

The selected APK/JAR and compiled-artifact hashes are recorded in the two extraction manifests. The adjacent OTA's decompiled outputs are under `decompiled/jadx/ota-PS7331/` and `decompiled/baksmali/ota-PS7331/`; they are reference material only and must not be cited as exact PS7330.4104N evidence.
