# Exact-version source archive tail sample

This is a bounded, host-only sample of the official Fire HD 10 7.3.3.0
source archive. The selected HTTP range is not a complete bzip2 stream; it was
processed with `bzip2recover` to inspect independently recoverable blocks.

## Observed

- Range: bytes `2450000000-2588816415` (138,816,416 bytes).
- Recovered blocks: 900.
- The recovered material contains an MT8183 kernel source tree, including
  `kernel/mediatek/4.4/arch/arm/configs/mt8183_defconfig`,
  `kernel/mediatek/4.4/arch/arm/configs/mt8183_debug_defconfig`, and
  `kernel/mediatek/4.4/arch/arm64/boot/dts/mediatek/mt8183.dts`.
- It also contains many paths under `kernel/mediatek/mt8183/4.4_emc/`.
- The exact kernel-side source-path count in the recovered text was 8,101
  unique strings beginning with `kernel/mediatek/mt8183/`.
- The only exact `kernel/` paths matching `u-boot`/`uboot` in this sample are
  generic AVR32 reference paths, not an MT8183 Amazon boot chain.
- No exact MTK `preloader` or `lk` source path was found in this sampled
  material.

## Limits

This is not a complete archive listing. It cannot establish that no boot-chain
source exists elsewhere in the 2.59 GB archive, and it does not provide a
signed preloader, LK, DA, BROM authentication material, or flashable image.
The source archive remains build context only; it is not an OTA.

No ADB, fastboot, BROM, DA, loader, partition, or device-state operation was
performed. The full recovered blocks and the 138 MB range are intentionally
not committed; the range hash, method, and compact results make the sampling
reproducible.
