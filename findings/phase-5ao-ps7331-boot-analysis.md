# Phase 5AO：PS7331 boot image 與 GhostLock offset capability review

日期：2026-08-04

## 結論先行

### 已證實

1. PS7331 OTA 的 `boot.img` 可以作為同一 `trona`／MT8183 裝置族的離線
   kernel artifact。Android boot header 指出 page size `2048`、kernel payload
   offset `0x800`、kernel address `0x40080000`；輸入 SHA-256 為
   `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。
2. kernel payload 是 gzip 壓縮的 ARM64 Linux Image。解壓後的 banner 是：

   ```text
   Linux version 4.4.146+ ... #1 SMP PREEMPT Sat May 3 01:24:02 UTC 2025
   ```

   image 內也保留 `mt8183`、Amazon build path 與 kallsyms table marker；這
   證明它是 PS7331 的 kernel payload，不是 generic MTK image。
3. 公開 upstream GhostLock 修補提交是在 2026 年，NVD 將舊 kernel 版本列為
   affected，並把 `rtmutex.c` 列為受影響檔案。[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)
   [Ubuntu advisory](https://ubuntu.com/security/CVE-2026-43499)

### 高可信推論

- PS7331 kernel build date 是 2025-05-03，早於公開 upstream 修補。因此
  「PS7331 沒有直接包含該 upstream 修補」是合理的高可信推論；但 Amazon
  可以自行 backport，單靠 build date 或 CVE 公開日期不能標記為 confirmed。
- `boot.img` 能提供 kernel payload、靜態 symbol table 及 image-level address
  資訊；它不能單獨提供 `struct task_struct` 的完整 C type layout、runtime
  KASLR、physmap、CPU entry area 或 exploit gadget 可用性。
- 目前已知的 `struct rt_mutex_waiter` layout（`task=0x30` 等）來自 PS7330
  source/ABI review，不能直接改名為 PS7331 compiled layout。PS7331 的 exact
  Amazon kernel source 或 DWARF/vmlinux 仍未取得。

## 版本與 artifact 邊界

| 項目 | 目前裝置 | 本地 PS7331 artifact |
|---|---|---|
| Build | `PS7330.4104N/0030099376128` | `PS7331.4463N/0031575863040` |
| Security patch | `2024-02-01` | `2024-08-01` |
| Kernel banner | `4.4.146+`, 2024-07-13 | `4.4.146+`, 2025-05-03 |
| Product / SoC | `trona` / MT8183 | `trona` / MT8183 |
| 用途 | installed-device evidence | adjacent-version offline reference |

同一 product/SoC 不等於同一 signed kernel。PS7331 映像不能作為目前 PS7330
的 boot、recovery、loader、offset 或刷寫輸入。

## 可計算與不可計算的 offset

| 類別 | PS7331 boot image 可否得到 | 結果／限制 |
|---|---|---|
| Android boot header | 可以 | kernel payload offset `0x800`；page `2048` |
| compressed kernel SHA-256 | 可以 | `a608a5f99c155dc8e8b12b308528cbd17175b47199985d017613f9e2fbb1edba` |
| decompressed Image SHA-256 | 可以 | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` |
| exported/global kallsyms | 部分可以 | image 有 kallsyms markers；無需假設有 DWARF type info |
| `struct rt_mutex_waiter` field layout | 不能僅由 image 保證 | 需 exact source、config、compiler ABI 或 debug type data |
| `task_struct.pi_blocked_on` compiled offset | 不能由目前 metadata 保證 | PS7331 exact type layout 尚未取得 |
| runtime KASLR / physmap / CEA | 不能離線確定 | 屬於執行期地址，不是 boot header offset |
| root exploit gadget／credential target | 不能安全推導 | 需 exact target chain；不產生 live payload |

## 方法與可重現命令

輸入來源是本地保存的 PS7331 `boot.img`，未接觸設備：

```sh
python3 tools/scripts/inspect_android_boot_image.py \
  --image firmware/extracted/PS7331/boot.img \
  --output artifacts/phase5/ps7331-boot-image-inspection-20260804-01 \
  --extract-kernel

gzip -dc \
  artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.payload \
  > artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image

file artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image
strings -a artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image
```

`gzip` 顯示 trailing data；其開頭為 device-tree magic `d00dfeed`，所以不能
把整個 boot kernel field 當作單一 gzip stream。parser 保留原始 kernel field
大小與 hash，避免把 appended DTB 誤算成 kernel code。

## 判定

- **已證實：** PS7331 boot image 適合做同一裝置族的 host-only kernel artifact
  分析。
- **高可信推論：** PS7331 可能仍保有未修補的舊 `rtmutex` source family，因為
  build 在 2025 年；這不是 signed-binary patch confirmation。
- **待驗證：** PS7331 是否由 Amazon backport GhostLock 修補；需要 exact
  PS7331 source、可對應的反組譯 basic blocks，或合法取得的 vmlinux/debug
  metadata。
- **已排除：** 只因有 `boot.img` 就能得到所有 exploit 所需 memory offsets；
  只因 CVE 在 2026 年公開就能證明 Amazon image 未修補。
- **因風險拒絕測試：** 不把 PS7331 image 寫入 PS7330，不執行 futex race、
  root/ROP、kernel memory write、BROM/DA、preloader/LK/boot/vbmeta 或
  fastboot 操作。

## 下一個最小且有價值的研究步驟

若研究者日後透過官方更新讓裝置實際運行 PS7331，應先重新封存 fingerprint、
kernel banner、config 與 ADB visibility，然後只做 source/bytecode comparison。
只有取得 exact PS7331 對應的 patch evidence，才能把「很可能未修補」提升為
「已證實」。不應以 PS7331 為理由直接執行其他裝置的 GhostLock payload。
