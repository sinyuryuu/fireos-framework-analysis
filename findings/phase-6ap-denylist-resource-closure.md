# Phase 6AP — PS7331 PackageManagerDenyList resource closure

Generated: 2026-08-05T01:13:06.488225+00:00

## Safety boundary

This is a host-only read of the preserved PS7331 `system.img` using `debugfs
dump`. The image was not mounted or written. No ADB command, Binder call,
Android process, OTA/updater, recovery, or package-state mutation was used.

## 已證實

1. The preserved PS7331 system image contains
   `/system/framework/fireos-res/fireos-res.apk`; its resource table declares
   package ID `0x7e` with package name `amazon.fireos`.
2. Resource ID `0x7e05000a` resolves exactly to
   `amazon.fireos:raw/package_manager_deny_list`.
3. `res/raw/package_manager_deny_list.json` contains
   `com.amazon.firelauncher` in its `packages_deny_list` array.
4. Resource ID `0x7e060058` resolves exactly to
   `amazon.fireos:string/config_amzpackagemanager_denyListArcusId`.
5. This closes the previously unresolved resource provenance in the static
   chain:

```text
Resources.getSystem().openRawResource(0x7e05000a)
  → amazon.fireos:raw/package_manager_deny_list
  → JSON key packages_deny_list
  → com.amazon.firelauncher membership
  → PackageManagerDenyList seed
  → ControlProtectedPackagesCallback
  → enabled-state rejection before mutation
```

Evidence: `6AP-RSRC-001` through `6AP-RSRC-005`. The minimal static
consumer excerpt is preserved at
`artifacts/phase6ap/consumer-snippet-20260805-01/`; its source metadata
records the original disassembly hash and line interval.

## 高可信推論

The Fire Launcher rejection is now supported by both sides of the chain:
the runtime/static consumer in `fosservices` and the exact PS7331 resource
that seeds the deny-list. This is stronger than inferring membership from the
error message alone. It still does not claim that every protected-package
operation shares identical code or that the resource can be changed by shell.

## 已排除／因風險拒絕

- **已排除：** treating `0x7e05000a` as an unresolved or generic AOSP resource
  for this PS7331 image.
- **因風險拒絕：** modifying the resource, remounting system, changing the
  deny-list, invoking unknown Binder transactions, disabling Fire Launcher,
  executing OTA/recovery, root, or writing any partition.

## Reproduction

```sh
python3 tools/scripts/audit_phase6ap_denylist_resource.py --dry-run
python3 tools/scripts/audit_phase6ap_denylist_resource.py \
  --image firmware/extracted/PS7331/system.img \
  --output artifacts/phase6ap/denylist-resource-closure-20260805-01
```

The local canonical artifact also contains the small extracted APK as a
derived evidence artifact (338,278 bytes); it is included when this evidence
set is published so the recorded resource table and raw resource can be
independently inspected. Its hash is retained in `sha256sums.txt`, and the
same host-only script regenerates it from the preserved image. The raw JSON,
resource-table mapping, input hash, debugfs commands, summary and SHA-256
manifest are public. The consumer excerpt can be regenerated with:

```sh
python3 tools/scripts/export_phase6ap_consumer_snippet.py --dry-run
python3 tools/scripts/export_phase6ap_consumer_snippet.py \\
  --source decompiled/baksmali/vdexExtractor/fosservices/disassembly.log \\
  --output artifacts/phase6ap/consumer-snippet-20260805-01
```
