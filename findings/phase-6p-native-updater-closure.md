# Phase 6P — PS7331 native updater closure

Date: 2026-08-10

## Scope

This is a host-only synthesis of the preserved PS7331 `update-binary` ELF,
embedded `.gnu_debugdata`, symbol-guided AArch64 disassembly, and saved direct
call-edge tables. The binary was not executed. No recovery, OTA, ADB, Binder,
partition write, or device mutation was performed.

## Confirmed static capability

- The updater is an ELF64 AArch64 static binary, 1,749,792 bytes,
  SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`.
- The embedded debugdata begins at file offset `0x1a2cf4`, has compressed size
  `0x808c`, and the recovered mini-ELF SHA-256 is
  `a1918c31c48e4ee3a6f06d0bf85a87493d6f28b7b671bb019d8957c06073988d`.
  Symbol recovery found 2,886 symbols; the bounded focus covered 20 functions,
  851 direct `BL` sites, and 246 unique direct edges.
- `main` (`0x400968–0x4015f0`) calls install-function registration and
  expression evaluation. `RegisterInstallFunctions` is at
  `0x406978–0x407078`.
- `PackageExtractFileFn` (`0x401fb8–0x402788`) opens an output with flags
  `0x241` (`O_WRONLY|O_CREAT|O_TRUNC`) and mode `0x180` (`0600`), extracts the
  entry, then fsyncs and closes it.
- `WriteToPartition` (`0x413c40–0x4142f0`) opens a target with `O_RDWR` and
  calls `ota_write`, `ota_fsync`, and close paths.
- `ota_open` (`0x426338–0x426528`) directly calls libc `open` at `0x426354`.
- `VerifyBlocks` (`0x40ede0–0x40f038`) is reached by
  `LoadSrcTgtVersion3` at `0x40d474` and `0x40db4c`; the saved CFG contains
  SHA-1 calculation and comparison branches.

These facts establish high-privilege recovery/update capability conditional on
a valid recovery invocation. They do not establish a shell or ordinary-App
caller.

## Path-handling boundary

The binary contains strings for `package_extract_file`, `block_image_verify`,
`block_image_update`, `/dev/block/by-name`, `readlink`, and `readlinkat`. The
recovered direct `__readlink_chk` edge is from `MakeFreeSpaceOnCache` at
`0x417bf0`, not from `PackageExtractFileFn` or `ota_open`. No direct
`realpath`, `readlink`, or `O_NOFOLLOW` gate was observed in the inspected
extraction/open range. This is bounded negative evidence only; it is not proof
of traversal or symlink bypass.

## Decision

- **已證實：** the native updater contains parser-to-extraction and raw
  partition-write capability.
- **高可信推論：** the capability is reachable only after recovery accepts a
  valid install context and dispatches the registered functions.
- **待驗證：** complete function-pointer registry decoding, recovery-side
  certificate/AVB enforcement, and full input canonicalization.
- **已排除（目前證據範圍）：** a shell/ordinary-App direct execution route,
  a confirmed path-traversal bypass, a signature bypass, or a Root path.
- **因風險拒絕測試：** running the updater/recovery, crafting OTA input,
  testing symlink/traversal payloads, sending private Binder transactions, or
  writing any partition.

## Reproduction inputs

Existing reproducible artifacts:

- [Phase 6BI write-boundary report](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/findings/phase-6bi-ota-write-boundary.md)
- [Phase 6T CFG focus report](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/findings/phase-6t-ota-cfg-focus.md)
- [selected functions](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6s/ota-cfg-focus-20260805-01/selected-functions.csv)
- [control-flow table](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/tables/phase6ah-update-binary-control-flow.csv)
