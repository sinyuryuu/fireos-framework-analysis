# Phase 6AS — PS7331 public boundary synthesis

## Scope

This is a host-only synthesis of saved PS7331 evidence. It is intended
for public publication and uses only the serial-redacted Phase 6AQ
summary plus static reports. No ADB command, Binder transaction,
broadcast, OTA/updater/recovery action, package mutation, reboot, or
partition write is performed by this generator.

## Current conclusions

- **已證實：** the observed Home-key implementation constructs an implicit
  `MAIN + CATEGORY_HOME` intent and delegates to the normal activity
  start/resolution path in the bounded method scope.
- **已證實：** saved enforcing-policy runtime evidence blocks shell
  discovery of the selected Amazon private services; service inventory
  alone is not a callable Binder API.
- **已證實：** the PS7331 `amazon.fireos` deny-list resource contains
  `com.amazon.firelauncher` and is connected by the saved consumer
  evidence to PackageManager protected-package enforcement.
- **已證實（靜態）：** the official updater script and AArch64
  `update-binary` contain system/vendor and direct block-device write
  intent. This is not an adopted runtime test path.
- **高可信推論：** the remaining ordinary HOME result is best explained
  by the privileged Fire candidate plus the standard implicit resolver,
  while Amazon task-visibility and package-protection callbacks form
  separate boundaries. A direct Fire component injection was not found
  in the bounded callback methods.
- **已排除目前安全範圍：** private-service shell bypass, OOBE replay as
  a normal launcher selector, and OTA/updater execution as a safe test.
- **尚未證明：** every private Binder method's caller policy, the native
  recovery canonicalization details, or any root/privilege transition.

## Control-surface matrix

| Surface | Observed path | Result | Confidence |
|---|---|---|---|
| HOME key | KeyPolicyManagerCommon.launchHomeFromHotKey -> implicit MAIN + CATEGORY_HOME -> startActivityAsUser | PackageManager HOME resolution remains the final observed selector | Confirmed (bounded method) |
| Amazon private services | fosinit registrations -> service-manager lookup -> SELinux service_manager find policy | Private service handles are not shell-visible under enforcing policy | Confirmed for saved runtime capture |
| Package protection | resource package_manager_deny_list -> deny-list seed -> protected-package callback | The PS7331 resource contains Fire Launcher and feeds the protected-package path | Confirmed static provenance |
| OTA updater | updater evaluator -> block-image/direct block-device write wrappers | Official package has a high-impact write boundary; execution is not justified | Confirmed static write intent |
| BOOT_AFTER_SYSTEM_OTA / OOBE | guarded post-OTA system-server sender -> protected receiver -> OOBE state/component path | High-risk lifecycle surface, not a normal shell HOME setter | Strong evidence; lifecycle invocation not replayed |
| otadexopt | standard shell-visible IOtaDexopt publication -> OtaDexoptService | Adjacent dexopt service; no observed HOME or privilege-transition path | Confirmed bounded implementation; caller policy remains scoped |

## Reproduction

```sh
python3 tools/scripts/build_phase6as_public_synthesis.py --dry-run
python3 tools/scripts/build_phase6as_public_synthesis.py \
  --output artifacts/phase6as/public-synthesis-20260805-01
shasum -a 256 -c artifacts/phase6as/public-synthesis-20260805-01/sha256sums.txt
```

## Input hashes

| Input | SHA-256 |
|---|---|
| `findings/phase-6aq-service-context-closure.md` | `36eddfc4c80c766e7d8846bc6831a7fa2ca8ddb488125a515f1235d51b5013c4` |
| `findings/phase-6ar-home-callback-and-ota-follow-up.md` | `3e7628d0cf621d6099e79e2c45752301e7e0b8a708ac7256f32dfe54f1168259` |
| `findings/phase-6af-otadexopt-implementation-closure.md` | `77e4cb0b922ce78485c786379e366590af7a55bc1d585e589d9d9eb0f3f6892b` |
| `findings/phase-6ah-update-binary-validation-write-closure.md` | `4b3bb959091c3b41a1c150040f80a1c436b1ec32e3d9915adb1a1ed3a05a9d28` |
| `findings/phase-6ap-denylist-resource-closure.md` | `8b2e71c4e63c15fb249d85e4026896c524b83775157c7fab63a3b524a4de6b02` |
| `artifacts/phase6aq/public-summary-20260805-05/service-context-key-rows.csv` | `5054b51467849496aae838ea3514a700bc12a6652af5d899190eba543653fdba` |
| `artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv` | `44526ce659cea48931be2b5d9b1b981f905a086f30a64acd78576dac27ee6397` |
| `artifacts/phase6aq/public-summary-20260805-05/home-and-build-state.txt` | `01867d17a0084571870ff5cc698d738b109a2d2abcf709d56ed8d6d8ce307563` |
| `artifacts/phase6aq/public-summary-20260805-05/amazon-service-avc.txt` | `d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4` |

The complete raw ADB captures remain local evidence. Public output is
bounded and does not publish device serials or raw restricted files.
