# Phase 5BL result

The exact PS7330 capture remains Android 9 on Linux 4.4.146+, with SELinux
Enforcing and an ordinary shell caller (UID 2000). `/proc/kallsyms` is denied
to shell, and most selected kernel sysctls are denied. ION and CMDQ device-node
metadata was listed but no node was opened and no ioctl was sent.

This result establishes runtime visibility and hardening boundaries only. It
does not establish GhostLock exploitability, a root transition, or a safe live
trigger.
