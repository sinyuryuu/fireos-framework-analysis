# Phase 5M ION userspace static inventory

This is host-only disassembly of already-pulled AArch64 shared objects. No file was loaded as code, and no Android device node or ioctl was touched.

The nearby-instruction parser identifies request constants only when the AArch64 `mov`/`movk` pattern is visible. It is a static candidate, not a runtime observation. See `ioctl-call-sites.tsv` and raw `objdump-d` files.
