# Android key-event implementation review

This artifact records the safe Phase 5AE source/build boundary. It does not
contain an APK or signing key.

- Source: `tools/phase4-accessibility/`
- Source SHA-256: `37ff8777f38c0a1f2c70adc4a28bc55cfb3cb9b4f07cb9052edb0846ddbc32a0`
- Accessibility XML SHA-256: `3c36360c80e9f20c7812a747e93d28e03bff10f2f1b76182aa463cfcef66a875`
- APK build output (local-only): `tools/phase4-accessibility/dist/20260804-keyevent-pendingintent-jdk17-01/`
- APK SHA-256: `e6a5536d11ff6be5de557d751817af7de69d841f7cd0d03e028d5da2537b013a`
- Build: raw Android SDK platform 35 / Build Tools 35.0.0 / OpenJDK 17
- Signature: v3 verified; key material remains outside the repository
- Device preparation: `adb/phase5/PHASE5AE-KEYEVENT-PENDINGINTENT-T01/`
- Manual consent is intentionally not automated.

The implementation only handles `KEYCODE_HOME` after manual Accessibility
service consent and an explicit in-app toggle. A failed target dispatch returns
false so the normal HOME path remains available.
