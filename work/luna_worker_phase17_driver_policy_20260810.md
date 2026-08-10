# Phase 17, branch C — PS7331 final-node/policy closure

Date: 2026-08-10 (Asia/Taipei). Host-side only. Six Phase 16 surfaces are covered: CMDQ/MDP, ION/MTK ION, M4U, uinput, AUXADC, and Amazon diagnostic/test proc.

## Result

All six rows remain conservative. Source, Kconfig, Image markers, init/file-contexts, and existing native inventories are joined where available. No row establishes low-privilege reachability: Kconfig, symbols, policy allows, or domain names do not substitute for a shipped ELF caller, boot-selected DTB/DTBO, or merged SELinux decision.

MT8183 DTS records source-level GCE/CQDMA/M4U intent, but a complete bootloader-selected DTB/DTBO manifest is not available for every surface. DT source compatibility is therefore not node-instantiation proof.

No device contact, node open, ioctl, proc/sysfs/debugfs access, module load, Binder call, exploit, root operation, reboot, or partition operation occurred in this phase.

## Closure

- CMDQ has init mode/owner and mtk_cmdq_device context markers; object/module, selected DTB/DTBO, merged TE, and native opener are UNKNOWN.
- ION has saved 0666 system:graphics ion_device metadata and context markers; heap/object/DT, final policy, and exact native client are UNKNOWN.
- M4U has 0440 system:media init metadata; proc genfscon/TE, object/DT delivery, and caller are UNKNOWN.
- uinput has an init owner marker, conflicting context candidates, and negative caller inventory; final node policy and caller are UNKNOWN.
- AUXADC has source/config/Image markers and writable registrations; exact instance, policy, and writer are UNKNOWN.
- Amazon diagnostics are source-conditional with CONFIG_AMZN_DRV_TEST absent/default-n; no production object/module, proc policy, or caller is established.

## Host-only next steps

1. Join exact-build built-in/module manifests and boot-selected DTB/DTBO, with hashes.
2. Extract merged ueventd, file_contexts/genfscon, and compiled allow policy; preserve absent edges as UNKNOWN.
3. Scan exact shipped native ELF imports/relocations for concrete open/ioctl/sysfs/proc callsites and map only those to UID/domain metadata.

No device-side follow-up is proposed. CSV data-row count: 6.
