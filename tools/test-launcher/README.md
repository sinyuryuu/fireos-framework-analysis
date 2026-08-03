# Phase 3A test Launcher variants

This directory contains a deliberately small HOME-handler application used by
the Phase 3A resolver experiment. Each variant has a different application ID
and manifest priority. The application has no network permission, services,
receivers, providers, accessibility service, device-admin declaration, or
background work.

The build uses the Android SDK command-line toolchain directly. Android Gradle
Plugin and Gradle are intentionally not used; the build manifest records them
as `NOT_USED`. The build output records the exact JDK, SDK platform, build
tools, compiler, dexer, signer, source digest, and APK digest.

The signing key must remain outside the repository. A test key is sufficient;
these packages are research controls and are never installed as system apps.

## Build

```sh
tools/test-launcher/build_variants.sh --dry-run
tools/test-launcher/build_variants.sh \
  --output tools/test-launcher/dist/BUILD-ID \
  --keystore /private/path/fireos-phase3a-test.keystore \
  --keystore-password 'supplied-out-of-band'
```

The script refuses to overwrite an existing output directory. It requires a
working JDK (`java`, `javac`, and `keytool`) and the Android SDK tools
`aapt2`, `d8`, `zipalign`, and `apksigner`. It does not download tools.

## Variants

The source of truth is `config/variants.tsv`:

```text
org.fireosresearch.home.p0    0
org.fireosresearch.home.p49   49
org.fireosresearch.home.p50   50
org.fireosresearch.home.p51   51
org.fireosresearch.home.p100  100
```

The generated `build-manifest.tsv`, source archive, manifest copies, and
SHA-256 file are the evidence for a build. APKs are built locally and installed
one variant at a time by the Phase 3A runner.
