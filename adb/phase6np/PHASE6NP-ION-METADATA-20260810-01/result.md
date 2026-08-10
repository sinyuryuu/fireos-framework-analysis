# PHASE6NP-ION-METADATA-20260810-01

This is a read-only device metadata capture.

## Observed

- `/dev/ion` exists with mode `0666`, owner `system:graphics`, and label
  `u:object_r:ion_device:s0`.
- `/dev/mtk_cmdq` exists with mode `0644`, owner `system:system`, and label
  `u:object_r:mtk_cmdq_device:s0`.
- `/proc/ged` exists with mode `0644`, owner `root:root`, and label
  `u:object_r:proc_ged:s0`.
- SELinux is `Enforcing`.
- The executing shell context is `u:r:shell:s0`.

## Interpretation

This closes the existence, Unix-mode and live label portion of the ION
metadata question. It still does not prove a successful ION ioctl, a kernel
memory-safety issue, a privilege transition, or any HOME/PMS effect.

## Safety

No device node was opened. No ioctl, read, write, Binder transaction, package
mutation, reboot or launcher-state operation was performed.

The `stat` command used an unsupported format on this device's tool; its raw
error is preserved in `stat-output.txt`. The authoritative mode/owner/label
observation is the preserved `ls -lZ` output.
