# PS7331 trona_defconfig extraction

The exact member named by the PS7331 build configuration was found in the
official Amazon source archive and extracted without building or executing the
source. The member is a Kconfig build input, not a signed kernel Image.

- Member: `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig`
- Size: 14,743 bytes
- SHA-256: `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`
- Source URL: `https://fireos-tablet-src.s3.amazonaws.com/k2k5jkgocvaww3SgOjJMkJrykI/Fire_HD10-7.3.3.1-20250617.tar.bz2`

The file explicitly selects `CONFIG_PREEMPT`, `CONFIG_RANDOMIZE_BASE`,
`CONFIG_MTK_CMDQ`, `CONFIG_ION`, `CONFIG_MTK_ION`, and `CONFIG_PANIC_ON_OOPS`.
The final PS7331 boot Image's embedded config separately records the focus
`CONFIG_FUTEX`, `CONFIG_RT_MUTEXES`, ARM64, SELinux, seccomp, ION and CMDQ
values. An absent symbol in this partial defconfig is therefore not treated as
`n` and is not evidence of a final-image difference.
