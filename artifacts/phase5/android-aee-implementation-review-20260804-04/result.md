# Phase 5Z：Android AEE implementation review

## Scope

This is a host-only mapping of the Android/MediaTek implementation boundary.
It does not open `/dev/aed0`, `/dev/aed1`, or `/dev/atf_log`, execute an AEE
daemon, trigger a crash/race, build a root payload, or change the device.

## Exact-device inputs

- Runtime identity: `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/identity.stdout.txt`
- AEE node metadata: `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/aee_nodes.stdout.txt`
- Shell access check: `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/aee_access.stdout.txt`
- Exact MT8183 defconfig excerpt: `artifacts/phase5/exact-kernel-source-review-20260804-01/members/mt8183_defconfig.e1495a4e51db.txt`
- Exact source path inventory: `artifacts/phase5/exact-source-aee-paths-20260804-01/path-matches.txt`
- Exact source path inventory matches: `0`
- Analysis timestamp UTC: `2026-08-03T19:52:51.556367+00:00`

Observed device identity excerpt:

```text
uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc),3011(uhid) context=u:r:shell:s0
```

HOME was captured independently and remains:

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

## Android implementation map

```text
MediaTek kernel AEE API / driver
        |
        +--> misc_register(aed0)  [external exception / EE]
        |       \--> /dev/aed0  --read/write/ioctl--> AEE userspace reader
        |
        +--> misc_register(aed1)  [kernel exception / KE]
        |       \--> /dev/aed1  --read/write/ioctl--> AEE userspace reader
        |
        +--> /proc/aed/*          [current crash records / reports]
        |
        +--> IPANIC / MRDUMP / ATF logger persistence
        |
        `--> Android init + SELinux domain for aee_aed/aee_aed64 on some MTK branches
```

The public MediaTek Android 4.4 implementation declares two misc devices,
`aed0` and `aed1`, assigns file operations including `read`, `write`, and
`unlocked_ioctl`, and registers them from `aed_init()`. The public code also
creates `/proc/aed` reporting entries. These are kernel/vendor crash-reporting
interfaces, not a normal app permission or Android framework service.

The public SELinux references show the other half of the Android integration:
an `aee_aed`/`aee_aedv` domain, init-daemon treatment, and narrowly granted
access to AEE device/data/socket resources. Those references are analogous
MTK branches, not proof of the exact Fire OS policy or daemon binary.

## Exact Fire OS result

Defconfig AEE entries:

```text
1611	CONFIG_MTK_AEE_FEATURE=y
1612	CONFIG_MTK_AEE_AED=y
1613	CONFIG_MTK_AEE_IPANIC=y
1614	# CONFIG_MTK_AEE_POWERKEY_HANG_DETECT is not set
1615	CONFIG_MTK_AEE_MRDUMP=y
1616	# CONFIG_MTK_AEE_UT is not set
1617	CONFIG_MTK_ATF_LOGGER=y
2001	CONFIG_MTK_MRDUMP_KEY=y
```

Exact runtime node metadata contains:

```text
crw------- 1 root root u:object_r:aed_device:s0 10,  60 2026-08-03 18:43 /dev/aed0
crw------- 1 root root u:object_r:aed_device:s0 10,  59 2026-08-03 18:43 /dev/aed1
crw------- 1 root root u:object_r:device:s0     10,  57 2026-08-03 18:43 /dev/atf_log
lrwxrwxrwx 1 root root u:object_r:sysfs:s0            0 2026-08-03 21:00 /sys/class/misc/aed0 -> ../../devices/virtual/misc/aed0
lrwxrwxrwx 1 root root u:object_r:sysfs:s0            0 2026-08-03 21:00 /sys/class/misc/aed1 -> ../../devices/virtual/misc/aed1
```

Shell read/write checks contain:

```text
/dev/aed0 read=0 write=0
/dev/aed1 read=0 write=0
/dev/atf_log read=0 write=0
```

The node metadata and access checks establish a root-only device boundary. They
do not establish that the AEE daemon is absent from unreadable filesystem
locations, nor do they reveal its patch status. The Phase 5X/5Y process,
package, service, and init captures did not observe an ordinary userspace AEE
endpoint.

The complete streamed archive listing finished successfully, but the
case-insensitive path filter for `aee|aed|mrdump|ipanic|aee_` returned zero
matches. This is an archive-provenance limitation, not proof that AEE code is
absent from the compiled kernel or from renamed/unpublished vendor members.

## GhostLock Android boundary

NebuSec's public article describes GhostLock as a Linux futex/rtmutex issue and
states that its Android-specific exploitation would be covered separately.
The public CyberMeowfia tree has Android/aarch64 build plumbing and target
profiles for other Google builds, but no `KFTRWI`, `trona`, `MT8183`, or
`PS7330.4104N` target in the captured tree. A target-specific header is not
portable across this tablet's kernel build, layout, KASLR, CFI/KPTI, SELinux,
and boot image.

Therefore the repository contains an Android implementation *reference map*,
not an Android root PoC for this device.

## Verdict

- **已證實：** Android-side AEE is a kernel/vendor crash-reporting boundary;
  exact Fire OS exposes root-owned `aed0`/`aed1` nodes and enables AEE-related
  config flags.
- **已證實：** the shell domain cannot read or write those nodes in the
  captured runtime; no node was opened.
- **高可信推論：** a usable Android AEE implementation, where present, would
  require a privileged daemon/domain rather than a normal sideloaded APK.
- **待驗證：** exact PS7330 AEE daemon binary, exact init/SELinux source and
  whether Amazon/MediaTek patched the daemon vulnerability.
- **已排除：** treating public MTK AEE source or another Android target's
  profile as an exact Fire root implementation.
- **因風險拒絕測試：** AEE device-node open/read/write/ioctl, malformed AEE
  message, race/crash trigger, reboot/dump generation, SELinux/property
  changes, root payloads, BROM/DA/fastboot, and partition writes.

## Public references

- https://android.googlesource.com/kernel/mediatek/+/android-4.4.4_r3/drivers/misc/mediatek/aee/aed/aed-main.c
- https://android.googlesource.com/kernel/mediatek/+/android-4.4.4_r3/drivers/misc/mediatek/aee/common/aee-common.c
- https://android.googlesource.com/device/mediatek/wembley-sepolicy/+/6f092d159878a6d57c00f2d94c32c28b735761ce%5E%21/
- https://nebusec.ai/research/ionstack-part-2/
- https://github.com/NebuSec/CyberMeowfia
