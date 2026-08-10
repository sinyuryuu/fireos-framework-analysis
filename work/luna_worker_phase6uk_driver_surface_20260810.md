# Phase 6UK — exact-build Fire OS 7.3.3.1 driver/native surface audit

Scope: host-only static analysis of the preserved PS7331/Fire OS 7.3.3.1 evidence. No device node was opened, no ioctl or probe was issued, no module was loaded, and no root/exploit code was constructed.

## Build and evidence identity

The image-side identity is `firmware/extracted/PS7331/system/build.prop:23,78,183` (`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`; Fire OS 7.3.3.1; MediaTek branch `alps-mp-p0.mp1.tc6sp-of.p12` at line 142). The extracted kernel config is `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`, SHA-256 `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`; its metadata records image SHA-256 `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` (`metadata.json:3-6`). The extracted `boot.img` SHA-256 is `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`. Selected/compiled extraction manifests are respectively `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74` and `7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716`.

The GPL source root is `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/4.4`. `kernel/source-manifest.json` itself is SHA-256 `ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a`. Key source hashes are included in the CSV and were recomputed from this tree. The source package is exact-build-labelled PS7331 GPL evidence, but no preserved reproducible build log proves that every source file below was linked into the installed kernel.

## Executive result

The config confirms `CONFIG_MODULES=y`, `CONFIG_MTK_CMDQ=y`, `CONFIG_ION=y`, `CONFIG_MTK_ION=y`, `CONFIG_AMAZON=y`, `CONFIG_AMAZON_LD=y`, `CONFIG_DEBUG_FS=y`, and SELinux (`kernel.config:250,1247,3532-3535,3555-3564,4133,4319-4327`). `CONFIG_DEVMEM` and `CONFIG_DEVKMEM` are disabled (`2181-2182`). Amazon metrics/sign-of-life options are disabled in this captured config (`3556-3560`); Amazon liquid detection is enabled (`3563-3564`).

Capability is not reachability. Source proves registration and possible effects after a matching DT/config/init path. It does not prove that the installed image contains the object, that a node exists, that a caller can pass SELinux, or that a caller reaches a state-changing operation.

Highest-confidence capabilities:

* CMDQ (`mediatek,gce`) has an ioctl fops path with user copies, register read/write helpers, engine notification, task submission, and secure metadata handling (`cmdq_driver.c:53,225-290,350-524,613-656,663-742`). This is a privileged hardware/control capability if the node is present and policy permits access; no direct framework/launcher caller was found in the preserved source scope.
* ION creates the standard misc device through `ion_device_create()` and exposes generic alloc/share/import/sync/custom ioctl handling (`ion.c:1506-1663,1912-1962`; MTK custom path `ion_drv.c:319-435,612-765`). Capability includes DMA/buffer allocation and MTK physical-address/debug operations subject to heap/driver checks; no source-proven untrusted-app caller or SELinux label was preserved.
* Amazon LD matches `amzn,ld` and creates writable device sysfs attributes (`amzn_ld.c:665-673,758-777`). This can alter liquid-detection controls if the sysfs node is instantiated and writable; the exact DTB, sysfs mode/owner, and SELinux label are missing.

The remaining Amazon surfaces are logging/diagnostic or lifecycle plumbing. `sign_of_life.c:160` creates a proc entry, and `amazon_logger.c:585,665` contains a user-copy read path and conditional misc registration, but the captured config disables the logger/sign-of-life options. CMDQ and ION debugfs/proc/sysfs entries are compiled capabilities, not evidence of mounted debugfs or caller access.

## Surface map and missing joins

The companion CSV is the machine-readable inventory. Each row records exact source path and line offsets (`line=` means the 1-based source line in the hashed file), hash, config, registration/fops, caller references, privilege gates, possible effect, provenance, confidence, and missing edges. Byte offsets were not substituted for line offsets because the source evidence is line-oriented and no generated preprocessor output was preserved.

DT evidence: `arch/arm64/boot/dts/mediatek/mt8183.dts:26` identifies `mediatek,mt8183`; `:293` has Amazon `mdump-reserve-memory`; `:1093-1101` has M4U/DevAPC; `:1181` has MTK CQDMA; `:1374` has `mediatek,gce`. This establishes source-side DT intent only. No compiled DTB/DTBO join was found under the extracted PS7331 image tree, so `mediatek,gce` and `amzn,ld` instantiation remains unproven.

Image/module provenance is incomplete: the config has modules enabled, but no exact-build `/lib/modules` or vendor_dlkm module inventory was found in the preserved image extraction. The source Makefiles show Amazon objects are conditional (`drivers/staging/amazon/Makefile:15-25`) and MTK ION is conditional (`drivers/staging/android/ion/mtk/Makefile:14,27-29`); therefore source presence is not proof of built-in or loadable deployment.

SELinux labels are also a missing edge for these kernel-native nodes. The preserved GPL source and selected image subset contain no authoritative exact-build `file_contexts`, `service_contexts`, `ueventd*.rc`, or `seapp_contexts` mapping for `/dev/ion`, CMDQ, Amazon LD sysfs/proc, or debugfs. `CONFIG_SECURITY_SELINUX=y` is evidence of a kernel enforcement capability, not a label or allow rule. The separately captured device SELinux artifacts are not used to infer untrusted-app access here.

Caller analysis found no direct framework or launcher source caller in the Phase 6ME source-scope scan (`summary.json` reports `direct_framework_or_launcher_files: 0`). This is a bounded negative: native vendor binaries, generated DT, init scripts, vendor policy, and code outside the preserved source scope may still call or authorize the surfaces.

## Interpretation / privilege boundaries

* `CAPABILITY`: kernel code contains an entry point or registration and a possible privileged effect.
* `REACHABLE`: requires all of matching config, linked image/module provenance, DT/init registration, node/label/mode, caller, and SELinux/credential gates. No row is marked proven reachable solely from source.
* `PRIVILEGED EFFECT`: effects include hardware register access, DMA/ION buffer lifecycle, secure metadata/secure-world mediation, power/engine state changes, liquid-detection control, crash/reboot diagnostics, or high-volume kernel information disclosure. These are possible effects, not demonstrated effects.

No exploitability conclusion is made. The audit deliberately stops at static call/control edges and records missing evidence instead of constructing an invocation.
