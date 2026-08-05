# Phase 6AN — PS7331 GPL source scope verification

Generated: 2026-08-05T01:02:22.215537+00:00

## Scope and safety

This phase inventories the two preserved members of the official PS7331 GPL
source package with `tar -tf`. It does not extract or execute source, contact
ADB, modify the device, write a partition, or invoke any Android/private API.

## Result

### 已證實

1. `fireos.tar` contains 53,549 archive members, but no member path under
   `system/core`, `system/core/init`, `frameworks/base`, `com/amazon`,
   `selinux.cpp`, or the deny-list symbol names searched. Its `packages/apps`
   scope is limited to `SpareParts` (three member paths). Evidence `6AN-GPL-001`.
2. `platform.tar` contains 138,574 members and 150 generic `system/core`
   paths, but no `system/core/init`, `selinux.cpp`, `frameworks/base`,
   Amazon namespace, or `PackageWhitelister`/`DenyListArcus`/`fdrw` member-path
   hit. Evidence `6AN-GPL-002`.
3. The source package is therefore primarily a kernel/platform and limited
   open-source component source release; it is not a complete Amazon
   framework/resource source tree. Evidence `6AN-GPL-003`.

### 高可信推論

- The official GPL source package alone cannot resolve the Amazon `/init`
  policy-loader branch or prove the content of the `0x7e05000a`
  `PackageManagerDenyList` raw resource. Those questions remain binary/resource
  artifact questions.
- This explains why the existing PS7331 `fosservices` disassembly and
  `framework-res.apk` remain necessary evidence for the Launcher protection
  path.

### 待驗證

- A complete system/product overlay inventory is still needed to identify the
  runtime resource package behind package ID `0x7e`.
- Generic `system/core` files in `platform.tar` could still contain ordinary
  AOSP init infrastructure; this phase did not claim their contents are
  absent, only that `system/core/init` is not present as an archive member.

### 已排除／因風險拒絕

- **已排除於這兩個 tar member scope：** treating the GPL package as a
  complete source release for Amazon framework, `/init`, or deny-list code.
- **因風險拒絕：** boot/recovery replay, partition writes, root, system
  remount, SELinux changes, or any device mutation.

## Archive hashes

| Archive | SHA-256 | Members |
|---|---|---:|
| `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` | 53549 |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | 138574 |

## Reproduction

```sh
python3 tools/scripts/audit_phase6an_gpl_scope.py --dry-run
python3 tools/scripts/audit_phase6an_gpl_scope.py   --output artifacts/phase6an/gpl-scope-20260805-01
```

The generated filtered member lists, archive hashes, commands, table, and
summary are preserved in the canonical artifact directory.

## Decision

Phase 6AN closes the GPL-source-scope question without claiming that the
Amazon framework logic is absent. The next static task is to inventory the
complete OTA system/product overlay resource set and map package ID `0x7e`;
no device write or high-risk runtime operation is justified by the source
package result.
