# Phase 5 — `mtk-easy-su` temporary-root review

## Scope

This is an offline/source review of the public `KoCleo/mtk-easy-su` project,
pinned to commit `8c6871ac7c15b8e98a47e25c35ab93b87e260475` and documented in
`artifacts/phase5/mtk-easy-su-audit-20260803/`. No APK, Git LFS executable,
Magisk package, exploit, or payload was downloaded to the device or executed.

## Device baseline

The connected device is `KFTRWI` / `trona`, MT8183, Android 9/API 28,
security patch `2024-02-01`, SELinux `Enforcing`,
`ro.boot.flash.locked=1`, and verified boot `green`. The exact baseline and
hashes are in the existing Phase 5 evidence.

## Findings

### 已證實

1. The app embeds `mtk-su32`, `mtk-su64`, Magisk init binaries, and an LFS
   `magisk-boot.sh`. `ExploitHandler.kt` extracts them under the app's private
   files directory, changes their mode, and executes the script through
   `Runtime.exec`.
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
This is not a proof of impossibility because the opaque LFS payload was not
executed.

### 待驗證

- Exact contents and control flow of the LFS `magisk-boot.sh` and `mtk-su`
  binaries.
- Whether the Fire OS kernel/vendor tree retains any vulnerable behavior
  despite its reported patch level.
- Whether a matching Amazon-specific payload exists outside this repository.

### 因風險拒絕測試

APK installation, Play Protect changes, Magisk installation, exploit
execution, `su` invocation, and boot/system modifications were not performed.
They would constitute a Level 3 operation because they seek privilege
escalation and could leave the locked device without a verified recovery path.

## Decision

`mtk-easy-su` remains a historical compatibility lead, not an executable
workaround for this Fire tablet. The next useful action is offline binary
inspection in an isolated environment or obtaining an exact PS7330-compatible
source/payload; direct device execution is not justified by current evidence.
