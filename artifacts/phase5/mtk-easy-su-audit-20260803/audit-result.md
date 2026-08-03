# Mtk Easy Su audit result

## Device comparison

| Field | Device | Public project evidence | Assessment |
|---|---|---|---|
| SoC | MT8183 | No MT8183/trona entry in README | No exact-device proof |
| Model | KFTRWI / Fire HD 10 11th gen | No KFTRWI or Fire entry | No exact-device proof |
| Android | 9 / API 28 | Project targets old Android/MediaTek devices | Broad match only |
| Security patch | 2024-02-01 | App warns at >= 2020-03-01; README warns post-March-2020 firmware | Strong incompatibility signal |
| SELinux | Enforcing | README success example shows permissive | Runtime security posture differs |
| Boot state | flash.locked=1, verifiedbootstate=green | Project warns about locked-bootloader Magisk updates | No safe boot-image recovery path established |

## Verdict

- **已證實：** this project is an app wrapper around the `mtk-su`/Magisk
  temporary-root path. It extracts executable LFS assets and invokes a shell
  script from app-private storage.
- **已證實：** the public README does not claim support for this Fire tablet,
  KFTRWI, trona, or MT8183; it explicitly warns that post-March-2020 firmware
  can block the method.
- **高可信推論：** the device's 2024-02 patch level is outside the intended
  vulnerability window, so this exact release is unlikely to yield temporary
  root on this build.
- **待驗證：** the opaque `magisk-boot.sh` and `mtk-su32/64` payload behavior
  and whether an Amazon-specific kernel/vendor configuration changes the
  result. Verifying this would require retrieving or executing the exploit
  payload; execution is not performed in this audit.
- **因風險拒絕測試：** APK installation, Play Protect changes, exploit
  execution, Magisk installation, `su` invocation, or any boot/system write.

## No-go decision for direct execution

The repository does not provide an exact-device compatibility proof or a
recovery guarantee. The current device has a locked boot state, green verified
boot, enforcing SELinux, and no exact PS7330 loader/payload pairing in the
reviewed evidence. Therefore no APK, LFS binary, or exploit command is
approved for execution. A future attempt would be a Level 3 operation and
would require a separate exact-command risk report plus explicit approval.

## Safer next step

Compare an exact, researcher-obtained PS7330 kernel/vendor artifact against
the public CVE-2020-0069 fix boundary and inspect the LFS payload offline in a
disposable analysis environment. Do not run it on KFTRWI until exact support
and rollback are established.
