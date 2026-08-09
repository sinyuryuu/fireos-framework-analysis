# Phase 6MI — PS7331 source tar EOF-complete audit

Date: 2026-08-10
Device context: Fire HD 10 / KFTRWI / trona / PS7331.4463N
Scope: host-only inspection of the official `Fire_HD10-7.3.3.1-20250617.tar.bz2`.

## Result

The outer official source archive was read to a real tar EOF. It contains 35
members: 23 regular files and 12 directories. It contains no symlink or
hardlink member. The only launcher-related member names are the expected
`apps/com.amazon.firelauncher` payload directory and its
`javax.annotation-api-1.2.tar.gz` dependency. No outer member name matched an
OTA/recovery/update/post-install command or a partition/image control path.

This closes the outer-stream completeness limitation recorded in Phase 6FE.
It does **not** make the source archive an installable OTA, and it does not
provide a shell, Binder, Root, or HOME-selection entry point.

## Exact evidence

| Field | Value |
|---|---|
| Input | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` |
| Compressed size | `2,563,328,975` bytes |
| SHA-256 | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| Outer member count | `35` |
| EOF reached | `true` |
| Directories / regular files | `12 / 23` |
| Symlinks / hardlinks | `0 / 0` |
| Sensitive-name hits | `2`, both launcher payload names |
| Extraction / execution / device mutation | `false / false / false` |

The outer members include:

```text
README.txt
build_kernel.sh
build_kernel_config.sh
fireos.tar
platform.tar
apps/<Amazon and third-party source payloads>
```

The two sensitive hits are recorded verbatim in
`artifacts/phase6mi-source-tar-eof-20260810-03/sensitive-member-hits.tsv`:

```text
apps/com.amazon.firelauncher
apps/com.amazon.firelauncher/javax.annotation-api-1.2.tar.gz
```

No `META-INF`, `updater-script`, `update-binary`, `postinstall`,
`run_program`, `symlink`, `set_perm`, `set_metadata`, `mount`, `delete`,
`rename`, `otadexopt`, `payload.bin`, `system/`, `vendor/`, `boot/`, or
`recovery/` outer member was observed.

## Source-package interpretation

`fireos.tar` and `platform.tar` are regular nested source payloads, not
post-install executables. Their extracted PS7331 tree is already present under
`firmware/extracted/PS7331-SOURCE-20250617/` and was analyzed in earlier
kernel/source phases. The current source tree contains the MT8183 4.4 futex
and rtmutex implementations under:

```text
platform/kernel/mediatek/mt8183/4.4/kernel/futex.c
platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c
```

The extracted `platform/system/core` scope contains libcutils/logwrapper
content rather than a complete `system/core/init` implementation. This is a
source-package scope fact, not evidence of a boot-policy bypass; `/init`
analysis must continue to use the signed device image and the AOSP baseline.

## Relation to launcher and package protection

This phase does not change the earlier conclusions:

- **已證實：** the PS7331 system-image deny-list resource directly contains
  `com.amazon.firelauncher`; see `findings/phase-6ma-denylist-fosinit-and-kft-closure.md`
  and `artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json`.
- **高可信推論：** the ordinary shell `disable-user` failure is explained by
  the system-server protected-package gate plus the image-seeded deny-list,
  not by a missing OTA source member.
- **已排除：** the outer PS7331 source tar contains a hidden updater or
  post-install launcher writer.
- **待驗證：** whether a runtime Arcus refresh can replace the deny-list is a
  separate protected-service provenance question; it is not a safe shell
  bypass and was not invoked.

The older Phase 6MF R3 wording (“deny-list membership pending”) is superseded
for the static PS7331 image resource by Phase 6MA. Only live runtime refresh
and shell writability remain unproven.

## Reproducibility and safety

Script:

```sh
python3 tools/scripts/audit_phase6mi_source_tar_eof.py \
  --input firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --output artifacts/phase6mi-source-tar-eof-20260810-03
```

Outputs:

- `artifacts/phase6mi-source-tar-eof-20260810-03/summary.json`
- `artifacts/phase6mi-source-tar-eof-20260810-03/source-tar-summary.csv`
- `artifacts/phase6mi-source-tar-eof-20260810-03/sensitive-member-hits.tsv`
- `artifacts/phase6mi-source-tar-eof-20260810-03/source-tar-flow.mmd`
- `artifacts/phase6mi-source-tar-eof-20260810-03/sha256sums.txt`
- `output/tables/phase6mi-source-tar-summary-20260810-03.csv`
- `output/call-graphs/phase6mi-source-tar-flow-20260810-03.mmd`

The script streams tar headers and skips payload contents without extracting
or executing members. No ADB command, OTA install, recovery, reboot, Binder
transaction, package mutation, partition write, or Root operation was used.
