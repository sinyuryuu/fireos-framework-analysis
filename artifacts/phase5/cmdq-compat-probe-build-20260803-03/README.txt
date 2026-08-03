This is a host-built, never-executed AArch64 probe for
CMDQ-IOCTL-V3-COMPAT-T01. It opens /dev/mtk_cmdq read-only and issues one
ioctl #7 with count=0. It contains no retry, non-zero allocation, address use,
kernel-memory primitive, root setup, or Android package logic.

The binary must not be pushed or run without the exact Level 3 approval named
in findings/phase-5h-cmdq-ioctl-compat-level3-report.md.
