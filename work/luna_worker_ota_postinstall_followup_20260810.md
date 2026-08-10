# OTA/post-install follow-up — PS7331 / Fire OS 7.3.3.1

Date: 2026-08-10. Scope is host-only static review of the preserved signed
OTA, updater/post-install/recovery/OOBE artifacts, and Phase 6 reports. No OTA
was modified or malformed; no symlink/traversal test, updater/recovery
execution, broadcast replay, partition write, reboot, root, or exploit was
performed.

## Conclusion

No new untrusted caller route to a file/path, symlink, temporary staging,
post-install, package-state, or boot-lifecycle sink was established.

The exact signed OTA has privileged recovery capability: `updater-script:6-24`
uses `block_image_update` for `system`/`vendor`, extracts fixed image members
to fixed `/dev/block/platform/bootdevice/by-name/*` targets, and writes the
fixed blocklist to `/cache/recovery/last_blocklist`. The native updater also
registers 24 handlers, including extraction, `run_program`, mount, staging,
reboot, and block-image handlers. Selected static edges reach `open`, `chown`,
`rename`, and `write`, but this is recovery/update capability, not proof of a
shell or ordinary-app caller route.

Path markers exist at updater virtual addresses `0x1263ac`, `0x1263d9`,
`0x126405` (`symlink_realpath` diagnostics), `0x1312ea` (`readlinkat`), and
`0x1312f5` (`readlink`). Phase 6MK has zero selected direct canonicalization
edges. Phase 6MM finds one `MakeFreeSpaceOnCache` readlink-family call site at
`0x417778-0x417fc4`, without a direct edge to extraction or partition write.
Indirect dispatch, unselected functions, and complete dataflow remain open;
no unsafe path finding is claimed.

The guarded system-server lifecycle sends protected
`BOOT_AFTER_SYSTEM_OTA`; the receiver can enable `OobeHomeActivity` and write
OOBE setup state. Reviewed helper source has no Fire Launcher literal or
ordinary preferred-HOME writer. Exact numeric receiver user is unresolved.

## Hashes and exact evidence

| Input | SHA-256 | Location/offset |
|---|---|---|
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | 27 ZIP entries; Phase 6BP audit |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | lines 1-25; writes/extracts at 6, 10, 13-24 |
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | ELF virtual addresses below |
| `.../target.system.file_map` | `a535ef97639495175bf4188a1ad1769ba8206bbd69c1b033367b2b5328ecc1ab` | 3,779 entries; no duplicate/malformed/traversal result |
| `.../target.blocklist` | `f0a3f810d0dab5486a59cc22b9fc9390e9668760ab5a2b1229580a27fb05d83c` | 13 fixed bootdevice targets |
| `artifacts/phase6bp/ota-path-audit-20260805-02/ota-path-audit.json` | `594ab2dddbb30739261418400913494d97dba1ad24de8422c1c831fc40ac4970` | ZIP/file-map/script boundary |
| `artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json` | `6dec85cee148a60daba1e8c781f30370389c6d95ff787623cb6ac830f058a834` | 16 direct write edges; 14 path markers |
| `artifacts/phase6mk-updater-dispatch-20260810-04/summary.json` | `4cf463ec498b74e6460fb598f7ce5e5756418aaa5c2ac5767009c22e9c29b9fe` | 24 registrations; indirect registry |
| `artifacts/phase6mm-updater-blockimage-20260810-01/summary.json` | `a0186bb7d053d23f002dc663b9ee3f312255410b35ed997a74e864fc8f9229a6` | one selected readlink-family call site |
| `artifacts/phase6ne-updater-cache-flow-20260810-03/summary.json` | `1cb21f3de9403c54e080c27f2d285d8e76a0e3a970063a250cdcc3c222a98b60` | branches `0x409cb8`, `0x409ce0`, `0x417bf4` |
| `artifacts/phase6my-bootafter-ota-package-helper-20260810-01/summary.json` | `0b59425167183deb610188c4ab05d86a994ca040dcf9f1da240d4a8f9a28f43d` | OOBE helper closure |
| `artifacts/phase6ni-system-context-oobe-scope-20260810-01/manifest.json` | `6f0baa99083df47123f53353c3230f1a3835638c33c87f4932bb07ea9c351df5` | 12/12 context checks |

Updater offsets are virtual ELF addresses, not file-byte offsets.

## Key static edges

- `main`: `0x400cac -> RegisterInstallFunctions`; `0x400cb0 ->
  RegisterBlockImageFunctions`.
- `PackageExtractFileFn` `0x401fb8-0x402788`: `0x4021b4 -> ota_open(0x426338)`,
  `0x4022cc -> ExtractToMemory(0x4227a8)`, `0x40238c ->
  ExtractEntryToFile(0x422810)`.
- `PerformBlockImageUpdate` `0x408f08-0x40b8b8`: `0x409340 -> ota_open`,
  `0x409bdc -> chown(0x4c8e90)`, `0x409d48 -> open(0x4cc260)`,
  `0x40a2e0 -> open(0x4cc170)`, `0x40a378 -> rename(0x4cc400)`.
- `WriteToPartition` `0x413c40-0x413f10`: `0x413dcc -> ota_open`,
  `0x413e3c -> ota_write(0x426d58)`; `ota_open` reaches `open` at `0x426354`,
  and `ota_write` reaches `write` at `0x426e44`.
- Handler registration instructions span `0x4069cc-0x407038`; names and
  function-pointer cells are in
  `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`.

OOBE evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96087-96126`
(phase 550/`isUpgrade()`/protected send);
`artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61`
(gates, OOBE enable, settings helper);
`.../PackageHelper.java:11-22`, `.../OOBEActivationHelper.java:53-56`,
`.../SettingsDBUtils.java:51-64`; context propagation at
`decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:449212-449262,449576-449604,452691-452721`.
Phase 6MY found no Fire Launcher, `setHomeActivity`, `addPreferredActivity`,
or `replacePreferredActivity` in the reviewed chain.

## Existing tests and corpus limits

Phase 6BP checked ZIP/file-map/script path safety. Phase 6MD/6MK/6MM/6NE
checked selected updater extraction/write, handler registration,
canonicalization, and cache branches. Phase 6MY/6NI checked OOBE helpers and
system-context scope. Preserved summaries report
`device_contacted=false`, `updater_executed=false`, `recovery_executed=false`,
and `partition_written=false`. No runtime updater/recovery, malformed input,
symlink/traversal, broadcast, OTA Binder, partition, reboot, or staging cleanup
test was done.

Phase 6FE found no top-level post-install/recovery/updater keyword member and
audited 18 known nested `.tar.gz` members negatively for OTA/recovery/
system-server/PMS/HOME helpers. The bounded listing of
`firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` did not reach EOF;
unlisted outer-tail members remain open. Native direct-BL analysis is not a
complete CFG/dataflow proof, and OOBE numeric user scope remains pending.

## Safe/rejected next steps

Safe: hash/re-audit any newly supplied exact signed package; complete the outer
tar.bz2 listing to verified EOF; expand native indirect/canonicalization
dataflow offline; and after a naturally occurring authorized OTA collect only
read-only build, HOME, package/component, OOBE, and log evidence.

Rejected: crafted/modified/malformed/downgrade OTA; symlink/traversal or
temp-staging attack tests; updater/recovery execution; sideload/flash/fastboot,
`dd`, partition write, reboot; `BOOT_AFTER_SYSTEM_OTA` replay; manual OOBE
enablement; private OTA Binder calls; or treating capability/missing local UID
checks/OOBE enablement as a root, launcher, or untrusted-caller exploit.
