# Phase 6G：MTK CMDQ 靜態攻擊面分析

## 結論

PS7331 GPL source 與 extracted config **已證實**包含 MT8183 CMDQ v3 driver：

- `CONFIG_MTK_CMDQ=y`
- `CONFIG_MTK_CMDQ_TAB=y`
- device name `mtk_cmdq`
- `alloc_chrdev_region`、`class_create`、`device_create`
- `file_operations` 的 `unlocked_ioctl = cmdq_ioctl`
- 32-bit compat dispatcher

`cmdq_driver.c` 的 user-copy 與 request count bounds 也可在 source 中定位；這代表
一個敏感 userspace-to-kernel control surface，但**不等於 CVE-2020-0069 已確認**。

## Source anchors

| Anchor | Line |
|---|---:|
| `cmdq_open` | 120 |
| `cmdq_release` | 145 |
| `cmdq_driver_create_reg_address_buffer` | 181 |
| `cmdq_driver_process_read_address_request` | 248 |
| `cmdq_ioctl` | 660 |
| `cmdqOP` | 735 |
| `alloc_chrdev_region` | 848 |
| `device_create` | 865 |

Source hashes：

- `cmdq_driver.c`: `b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899`
- `cmdq_def.h`: `2dcdb4b2abc76b0100d4448796e2f4d223dbd28027fa63cc7ba8517911450fc1`
- kernel config: `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`

## 分類

- **已證實：** source/config driver surface and v3 dispatch exist。
- **高可信推論：** requests reach structured user-copy/readback helpers subject to
  the visible bounds checks。
- **待驗證：** shipped binary/source equivalence and per-domain SELinux access for
  each operation。
- **未知：** CVE-2020-0069 applicability。
- **因風險拒絕測試：** any new `open`/`ioctl` beyond already archived historical
  evidence, non-zero request, address/readback operation, DMA interaction, crash,
  kernel memory operation or root payload。

Canonical artifact：
`artifacts/phase6g/phase6g-cmdq-static-20260804-02/`。
