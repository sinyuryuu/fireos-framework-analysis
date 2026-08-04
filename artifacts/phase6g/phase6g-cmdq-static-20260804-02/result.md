# PS7331 MTK CMDQ static surface

Host-only source/config inventory. No device node was opened and no ioctl,
kernel-memory, crash, or privilege-escalation test was performed.

## Findings

- **已證實：** the preserved MT8183 source enables `CONFIG_MTK_CMDQ=y` and
  `CONFIG_MTK_CMDQ_TAB=y`, registers a device named `mtk_cmdq`, and wires a
  v3 `unlocked_ioctl` dispatcher with a compat path.
- **高可信推論：** the driver is a sensitive userspace-to-kernel control
  surface because it accepts structured requests, performs user copies, and
  reaches CMDQ/readback helpers. Bounds checks visible in this source are
  evidence about this tree, not a complete vulnerability proof.
- **待驗證：** whether the shipped binary exactly matches the source and how
  SELinux/device-node permissions constrain each caller.
- **Unknown：** CVE-2020-0069 applicability. No exact patch mapping or runtime
  ioctl test is included.
- **因風險拒絕測試：** any standalone ioctl, non-zero request, address
  readback, DMA interaction, race, crash, or root payload.
