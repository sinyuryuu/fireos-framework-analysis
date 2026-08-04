# Phase 5BP result

## Confirmed from the preserved scripts

- `KERNEL_SUBPATH` is `kernel/mediatek/mt8183/4.4` (build_kernel_config.sh:9).
- `DEFCONFIG_NAME` is `trona_defconfig` (build_kernel_config.sh:10).
- `TARGET_ARCH` is `arm64` (build_kernel_config.sh:11).
- The configured toolchain repository is the Android AOSP GCC prebuilt
  repository (build_kernel_config.sh:12).
- The selected toolchain branch is `llvm-r383902b` (build_kernel_config.sh:13).
- The cross-compiler prefix is `aarch64-linux-android-`
  (build_kernel_config.sh:15).
- The script expects `Image`, `Image.gz`, and `Image.gz-dtb`
  (build_kernel_config.sh:18).
- The script recommends a separately supplied Clang 6.0.2/4691093 compiler
  (build_kernel_config.sh:21–24).
- The build invokes `trona_defconfig` and then a parallel `make` in the exact
  kernel subtree (build_kernel.sh:130–150).
- The script copies generated arm64 boot outputs and checks for the expected
  image names (build_kernel.sh:160–185).
- No visible executable patch application, git apply/am/cherry-pick, overlay,
  or signing command occurs in these two files.

## Not established

- A source archive and its build script do not prove the provenance of a
  signed production boot image.
- The scripts do not establish the exact compiler binary digest, complete
  build environment, hidden CI inputs, release patches, image assembly, AVB
  signing inputs, or signing-key lineage.
- No kernel build was performed, so no image comparison or boot test exists.

## Safety result

No device operation and no state mutation occurred. The installed device
remains PS7330.4104N. No exploit, root payload, unknown ioctl, fastboot
operation, OTA installation, boot image write, or partition operation was
executed.
