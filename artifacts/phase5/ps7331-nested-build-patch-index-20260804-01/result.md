# PS7331 nested build patch/overlay path inventory

- URL: https://fireos-tablet-src.s3.amazonaws.com/k2k5jkgocvaww3SgOjJMkJrykI/Fire_HD10-7.3.3.1-20250617.tar.bz2
- Outer member: platform.tar
- The nested archive was listed through a streaming pipeline; no source file
  was extracted, executed, or built.
- matching-paths.txt contains path names matching patch, overlay, build,
  kernel configuration, rtmutex/futex, or GhostLock-related terms.
- patch-diff-series-paths.txt is the exact .patch/.diff/patch/series subset
  used for the focused conclusion.
- An empty match file means no matching path name was observed in this
  inventory; it does not prove that an unlabelled generated transformation is
  absent from the build environment.
- No ADB, fastboot, BROM, DA, loader, device-node, or partition operation ran.
