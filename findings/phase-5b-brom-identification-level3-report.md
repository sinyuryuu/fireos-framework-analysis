# Phase 5B — MTK BROM identification proposal and Level 3 boundary

## Status

`因風險拒絕測試` — not executed and not approval-ready.

The failed `mtk-easy-su` attempt does not justify sending a generic MTK
payload. Android now exposes useful identity properties, including
`ro.boot.pl_build_desc=d1a4a4b-20231011_072631`, but no matching PS7330
preloader binary, DA, authentication state, or recovery set is available.

## Operation considered

Connect the tablet in MediaTek BROM/Preloader USB mode using a source-audited
MTK client and obtain only hardware/protocol identity information. No read,
write, erase, unlock, `seccfg`, payload, DA upload, preloader patch, or memory
access would be included unless separately reviewed.

## Why ADB is insufficient

Android shell cannot expose the complete BROM hardware ID, exact preloader
binary, or DA/SLA/DAA handshake state. The new baseline only exposes the
preloader/LK descriptors passed into Android properties.

## Exact commands proposed

No device command is proposed at this time. The public MTKClient source does
not provide a guaranteed passive identity path: its preloader initialization
may perform a handshake, authentication, crash, payload, DA, or register
operation before a read-like command. The generic `MT6771/MT8385/MT8183/MT8666`
alias is not an exact Amazon loader match.

Host-only source/help review is safe and separate from a device probe:

```text
python3 mtk.py --help
python3 mtk.py devices --help
```

These commands do not select or send a loader to the tablet. They are not a
substitute for a device-side protocol test.

## Files or images

None selected. In particular, the following are not approved inputs:

- the PS7331 `preloader.img` or `lk.img` artifacts;
- the generic `mt6771_payload.bin`;
- Asus/FiH vendor preloaders from the public MTKClient tree;
- an unreviewed DA, exploit payload, or patched preloader.

## Risk report

- **Soft-brick:** material; a wrong handshake or loader can leave the tablet
  in a non-Android USB mode.
- **Hard-brick:** material if a payload reaches a write-capable path or a
  boot-chain region is touched.
- **Data loss:** material if a tool selects erase, format, userdata metadata,
  or RPMB-related paths.
- **Rollback/anti-rollback:** unknown; the adjacent PS7331 preloader shows
  RPMB/anti-rollback and DA-authentication strings, but it is not the installed
  PS7330 binary.
- **Recovery:** not established. The workspace has no verified, exact PS7330
  preloader/LK/boot recovery set.

## Stop conditions

Any future proposal must stop before execution if:

- a tool requests a loader, DA, payload, authentication file, or patched
  preloader whose exact device match is not proven;
- the command may crash BROM/preloader or upload code;
- the tool presents `seccfg`, unlock, write, erase, format, `da poke`, flash,
  or partition selection;
- normal ADB, fastboot recovery, or a device-specific recovery path is not
  guaranteed;
- any output indicates a write or authentication state mutation.

## Decision

This report does not authorize a BROM probe. A later approval request would
need a specific tool commit, exact command line, selected files and hashes,
USB mode, expected protocol messages, proof that no upload/write occurs, and a
device-specific recovery plan. Until then, continue with offline artifact
matching and non-invasive Android evidence only.
