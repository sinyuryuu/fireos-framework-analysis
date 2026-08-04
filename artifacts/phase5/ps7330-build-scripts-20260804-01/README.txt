Phase 5BP — PS7330 build-script provenance capture

Scope
-----
These two shell scripts were extracted read-only from the official PS7330
source archive. They are preserved as source evidence only. They have not
been executed, and no toolchain was cloned.

Inputs
------
- Archive: firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2
- Archive SHA-256:
  569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665
- Source path: kernel/mediatek/mt8183/4.4
- Device target: trona

Preserved files
---------------
- build_kernel.sh
- build_kernel_config.sh

Safety boundary
---------------
This artifact is host-side provenance evidence. It is not an instruction to
build, sign, package, flash, boot, or install a kernel. The build script
clones a toolchain, invokes make, and writes generated images; therefore it
was not run in this analysis. No ADB, fastboot, OTA, bootloader, partition,
or device-state operation is performed by this artifact.

Interpretation
--------------
The script selects the exact mt8183/4.4 kernel subtree and trona_defconfig,
uses arm64, and expects a GCC cross-compiler branch plus a separately supplied
Clang 6.0.2-compatible compiler. A static scan found no visible patch,
git-apply, overlay, cherry-pick, or post-build signing step in these two
files. That observation strengthens source/build-path provenance but does not
prove that a signed PS7330 boot image was built directly from the public
source, because build inputs may exist outside these files and signing is an
external release step.
