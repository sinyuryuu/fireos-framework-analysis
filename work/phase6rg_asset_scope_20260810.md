# Phase 6RG asset-scope note

日期：2026-08-10。這是主 Agent 對目前工作樹資產做的 host-only provenance
核對；沒有執行解包寫入、裝置操作或任何 exploit/root 程式。

## Exact PS7331 package artifacts

`firmware/extracted/PS7331/` contains the extracted PS7331 package/image set,
including `boot.img`, `system.img`, `vendor.img`, `ota.prop`, transfer/patch
files, and the `compiled-02/extraction-manifest.tsv` index.

Hash anchors:

```text
7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716  compiled-02/extraction-manifest.tsv
b6ac2a6e51d11e9591cae72c81332f55b6169406b599d55fa9240d1b7d033a24  compiled-02/manifest.sha256
f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded  ota.prop
cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b  boot.img
```

`ota.prop` identifies product `trona`, package `com.amazon.trona.android.os`,
Fire OS 7.3.3.1 / PS7331.4463N, version `0031575863172`, and release keys.

## GPL source scope

`firmware/extracted/PS7331-SOURCE-20250617/` contains the MT8183 4.4 kernel,
Amazon device/kernel drivers, selected FireOS/apps material, and a limited
`platform/system/core` tree. A targeted file inventory found `libcutils` and
`logwrapper` under that system/core tree, but no `system/core/init` or
`system/core/init/selinux.cpp` source in the searched path. Therefore the GPL
source is strong evidence for kernel/driver/config provenance, not a complete
source release for the installed `/init` or Amazon framework services.

## Separating local research files from official artifacts

`firmware/extracted/PS7331/boot_unpacked/README.md` states that its target
headers were copied from the local `exploit/` directory and describes a safe
diagnostic build mode. The presence of `boot_unpacked/src/exploit_main.c` or
`root.c` is therefore **not** evidence that those files came from the official
OTA or GPL tarball. They were not executed, built for the device, or treated as
official firmware evidence. Their hashes are retained only for provenance:

```text
68bac1bf27ed3a62dea2730d3738454ebd2e381d380f6d036c8f2546f2283573  boot_unpacked/src/exploit_main.c
b3291f38957eab0e5a21c011703e97ee7ea7a58dceb2810edaad1ff3e7f8fa79  boot_unpacked/src/root.c
8e14d3892ea21d85a540a299aea9c874d165c6a185637764adecf87c925ea52e  boot_unpacked/README.md
```

Conclusion: future reports must distinguish official image/source artifacts,
decompiled output, and local research code. No local exploit file may be used
to claim a PS7331 vulnerability or be copied to the device.
