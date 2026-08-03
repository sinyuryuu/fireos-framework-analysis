# Phase 4 multi-activity HOME candidate control

This is one small, foreground-only APK used to study candidate composition
and activity-alias matching. It is not a priority matrix and it never changes
the Fire Launcher package. All activities use the default priority of zero.

The manifest contains:

- `HomeActivity`: MAIN + HOME + DEFAULT, normal direct-boot state;
- `HomeAliasDefault`: alias to `HomeActivity`, MAIN + HOME + DEFAULT;
- `HomeAliasHomeOnly`: alias to `HomeActivity`, MAIN + HOME without DEFAULT;
- `DirectBootHomeActivity`: MAIN + HOME + DEFAULT, direct-boot aware;
- `SpecificHomeActivity`: MAIN + HOME + DEFAULT plus a non-matching data
  requirement;
- `SecondaryHomeActivity`: MAIN + `CATEGORY_SECONDARY_HOME` only.

The APK has no network permission, service, receiver, provider, accessibility,
device-admin, or background work. The build uses the raw Android SDK tools in
the same way as `tools/test-launcher`; Gradle and Android Gradle Plugin are not
used. Output is local and ignored by Git. Keep signing keys outside the repo.

## Build

```sh
tools/test-launcher-phase4/build_alias.sh --dry-run
tools/test-launcher-phase4/build_alias.sh \
  --output tools/test-launcher-phase4/dist/BUILD-ID \
  --keystore /private/path/phase4-test.keystore \
  --keystore-password 'supplied-out-of-band'
```

The script refuses to overwrite an existing output directory and records JDK,
SDK, build-tools, source archive, APK and manifest hashes. A local test key is
adequate; no key is committed.

## Read-only device experiment

```sh
tools/scripts/run_phase4_alias_experiment.sh \
  --serial SERIAL \
  --test-id PHASE4-ALIAS-T01 \
  --apk tools/test-launcher-phase4/dist/BUILD-ID/org.fireosresearch.phase4.alias.apk \
  --output adb/phase4/PHASE4-ALIAS-T01
```

The runner installs only this test APK, captures HOME candidates and activity
states, manually starts each declared component, then uninstalls the test APK.
It does not call `set-home-activity`, mutate Fire Launcher, or modify settings.
It requires an explicit approval phrase for the install/remove mutation and
supports `--dry-run`.
