Phase 5P nearby Android implementation review

This is a host-only review bundle. It records public repository metadata and
source/header observations; it does not contain exploit source, a compiled
payload, target addresses, or a device command that triggers futex PI.

Pinned public implementation:
- NothingFumo/ghostlock-aresin
- commit 1895a89c52dc7d7355f14babe5009c2932dcdb6a
- POCO F3 GT / Redmi K40 Gaming Edition (aresin)
- MediaTek MT6893 / Dimensity 1200
- Android 13 / MIUI 14
- Linux 4.14.186 arm64

The target is not the Fire HD 10. The public README itself requires device-
specific boot/vmlinux analysis and says the expected failure behavior is a
kernel panic/reboot. Its target profile therefore provides methodology only,
not transferable Fire OS constants.

Source comparison inputs:
- Linux stable v4.4.146 rtmutex_common.h, SHA-256
  ee7fcb3d8edb06312606073f02435da8e6bb1d60b53604733a218c75c48ec51c
- Linux stable v4.14.186 rtmutex_common.h, SHA-256
  884d551fbfa7e4b98037654d645095a7817d9e30a6e8f5f25f41731e2e4f2040

The v4.4.146 waiter has no deadline field after prio. The v4.14.186 waiter
adds deadline after prio. Both pinned headers use rb_node for the first two
tree fields; the public aresin README contains an inconsistent warning that
describes 4.14 as plist_node. The header and target profile, not that warning,
were used for the static comparison.

No Android APK, NDK binary, Shizuku payload, root attempt, reboot trigger,
ioctl, bootloader, partition, or kernel state mutation was performed in this
review.
