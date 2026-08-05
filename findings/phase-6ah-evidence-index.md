# Phase 6AH evidence index

Capture time (UTC): `2026-08-04T23:37:00.092164+00:00`

## Evidence IDs

- `SCRIPT-STATIC`: official PS7331 `updater-script` command/target declarations.
- `REG-INSTALL`: saved `main` and `RegisterInstallFunctions` direct edges.
- `REG-BLOCK`: saved `main` edge and bounded block-image registration disassembly.
- `EVAL-DIRECT`: saved `main -> Evaluate` direct edge.
- `BLOCK-WRAPPER`: bounded disassembly of both block-image wrappers.
- `VERIFY-DIRECT`: `LoadSrcTgtVersion3 -> VerifyBlocks` direct edges and bounded VerifyBlocks disassembly.
- `UPDATE-IO`: bounded `PerformBlockImageUpdate` direct I/O edges.
- `WRITE-SYMBOL`: bounded `WriteToPartition` body and its I/O edges.
- `IO-DIRECT`: `ota_open`/`ota_write` to libc `open`/`write` direct edges.

## Evidence files

| File | SHA-256 |
|---|---|
| `binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| `script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| `functions` | `adbf977955846e529d4a9bc44c5b499494a94e529b2e01c60b4731091dc7374d` |
| `edges` | `ede44312f2f667adff552475866de0b17c06b96161854c35a17a3a1c361eaa75` |
| `disassembly` | `0e780e51ced6f7b000bf0a821ffe6cfe81bc0108e6073174b7fa0cb0b94abdcd` |

## Limit

All findings are host-only. No runtime OTA, recovery, OOBE, partition write, or device mutation occurred.
