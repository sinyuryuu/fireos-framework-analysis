# Phase 4 alias APK build record

The APK was built locally with the raw Android SDK toolchain. Signing keys are
not committed. The APK used by canonical device run `PHASE4-ALIAS-T04` was
build `20260803-openjdk17-02`; build `-03` is a post-script-fix rebuild of the
same source and is recorded to make the corrected build reproducible.

| Field | Value |
|---|---|
| Package | `org.fireosresearch.phase4.alias` |
| Test APK SHA-256 (`-02`) | `1d1e90f05334434b18cab3b0d31e5b5344beb4d149e7da02e8b9db62a2ada99c` |
| Rebuild APK SHA-256 (`-03`) | `ac87bf9fde1ea1d501ef2ff5ce4ebe5e062952432f990384a64cbe49f77aa68a` |
| Manifest SHA-256 | `03fb7819dff8557d2e91841dcc153cffa2d3329378c1a3b86293e4adeea93c7f` |
| Source archive SHA-256 | `5b26a8b1fa76d5f6e91600a9b100dcb6a9205ce55d37327a38a0f2211f23aa34` |
| JDK | OpenJDK 17.0.20 (Homebrew) |
| SDK platform | Android API 35 (`android.jar`) |
| Build tools | 35.0.0 |
| `aapt2` | 2.19-11948202 |
| `d8` | 8.6.2-dev, build `abaab469b5ebd4dd2bb91ba0ed6f45277faae4ca` |
| `apksigner` | 0.9; v3 verified |
| Android Gradle Plugin / Gradle | `NOT_USED` |
| APK min/target SDK | 28 / 28 |

The complete local build manifests, tool outputs, source hashes and APKs are
under the ignored `tools/test-launcher-phase4/dist/` directory. The committed
source and `build_alias.sh` are the source of truth; hashes above bind the
canonical run to its exact local APK without publishing signing material.
