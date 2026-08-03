# Public CMDQ ioctl reference

The request at `0x2f80` is decoded as `_IOW('x', 7, 8-byte struct)`; the corresponding public MediaTek header names this request `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`. The cleanup request is number 8, `CMDQ_IOCTL_FREE_WRITE_ADDRESS`. These references identify the ioctl encoding only; they do not prove the PS7330 driver is vulnerable.

- https://android.googlesource.com/kernel/mediatek/+/android-mtk-3.18/drivers/misc/mediatek/cmdq/v2/cmdq_driver.h
- https://blog.quarkslab.com/cve-2020-0069-autopsy-of-the-most-stable-mediatek-rootkit.html
