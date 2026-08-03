# Phase 5 — `mtk-easy-su` temporary-root review

## Scope

This is an offline/source review of the public `KoCleo/mtk-easy-su` project,
pinned to commit `8c6871ac7c15b8e98a47e25c35ab93b87e260475` and documented in
`artifacts/phase5/mtk-easy-su-audit-20260803/`. A later, separately recorded
operation installed and launched the verified APK under an explicit Level 3
scope; its follow-up is in
`findings/phase-5-mtk-easy-su-root-followup.md`. No extracted payload was
executed by the host and no system partition was written.

## Device baseline

The connected device is `KFTRWI` / `trona`, MT8183, Android 9/API 28,
security patch `2024-02-01`, SELinux `Enforcing`,
`ro.boot.flash.locked=1`, and verified boot `green`. The exact baseline and
hashes are in the existing Phase 5 evidence.

## Findings

### 已證實

1. The app embeds `mtk-su32`, `mtk-su64`, Magisk init binaries, and an LFS
   `magisk-boot.sh`. The offline APK follow-up confirms the same assets and
   records their hashes; the app extracts them under private storage, changes
   their mode, and executes the script through `Runtime.exec`.
2. The app's own security-patch warning treats `2020-03-01` and later as a
   blocked/risky boundary. The README likewise warns that firmware after
   March 2020 may block the method.
3. The README's tested-device table has no Fire HD 10, KFTRWI, trona, or
   MT8183 entry; it lists MT6771 as failed.
4. The manifest requests INTERNET and RECEIVE_BOOT_COMPLETED and declares an
   exported boot receiver. The corresponding receiver source was not found
   in the pinned tree listing, so the boot behavior is unresolved.

### 高可信推論

The 2024-02 patch level is far outside the project's stated vulnerability
window. Together with enforcing SELinux and the absence of exact Amazon
device support, this makes a successful temporary root on this build unlikely.
This is not a proof of impossibility because the native return path was not
captured as a controlled device-side result.

### 待驗證

- Exact runtime return path of the native `mtk-su` binaries on PS7330.
- Whether the Fire OS kernel/vendor tree retains any vulnerable behavior
  despite its reported patch level.
- Whether a matching Amazon-specific payload exists outside this repository.

### 因風險拒絕測試

Magisk installation, host-issued `su` invocation, and boot/system
modifications were not performed. The approved app-side Root-control attempt
was separately recorded and did not produce a confirmed UID-0 signal. Any
retry that acknowledges the warning or invokes the native payload remains a
Level 3 operation because it seeks privilege escalation and can leave a
locked device without a verified recovery path.

## Decision

`mtk-easy-su` remains a historical compatibility lead, not a confirmed
workaround for this Fire tablet. The next useful action is exact-device
compatibility analysis or a narrowly scoped, separately approved observation
of the native return path; repeated blind execution is not justified by the
current evidence.
