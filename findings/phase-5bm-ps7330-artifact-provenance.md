# Phase 5BM：PS7330 signed-artifact provenance ledger

日期：2026-08-04  
範圍：GhostLock exact-target binary evidence 盤點  
方法：host-only ledger；沒有裝置 I/O

## 結論

### 已證實

- 工作區有 exact PS7330 runtime properties、exact source-family metadata、
  kernel config 與 boot-partition read-denied evidence。
- 工作區沒有可驗證的 exact PS7330 signed `boot.img`、`vmlinux`、decompressed
  `Image`，也沒有完整 exact PS7330 preloader/LK/recovery set。
- 工作區唯一完整 OTA 與 `boot.img` 是 PS7331.4463N；兩者均標記為
  `AVAILABLE_VERSION_MISMATCH`。
- PS7330 boot partition 的 shell pull 已保存為 `ACCESS_DENIED`，因此不能把
  block-device 名稱或 symlink 當成 binary input。

### 高可信推論

- 目前不能從現有檔案可靠證明 PS7330 signed binary 的 `remove_waiter()`
  compiled pattern、`task_struct.pi_blocked_on` compiled offset、KASLR 或
  GhostLock target profile。
- PS7331 source／Image 對研究很有價值，但只能作相鄰版本 host-only evidence；
  不能把它改名成 exact PS7330。

### 待驗證

- Amazon 是否曾在未索引的歷史或區域 endpoint 提供 PS7330 full package。
- 是否能由研究者合法取得帶有 `PS7330.4104N` 明確版本證據的 signed boot chain。

### 已排除

- 用 PS7331 `boot.img` 代替 PS7330 signed kernel。
- 用 source-only `rtmutex.c` hash 宣稱 signed binary 已確認。
- 用 `/dev/block/by-name/boot` symlink、`blockdev` metadata 或 denied `adb pull`
  產生 kernel offset。

### 因風險拒絕測試

沒有嘗試權限繞過、Root、SELinux bypass、BROM/DA、fastboot read/write、
preloader/LK、sideload、OTA 或分割區操作。

## Artifact ledger

| ID | Artifact | Version relation | Status | Exact PS7330 binary proof |
|---|---|---|---|---|
| `P5BM-PS7330-RUNTIME` | preserved device properties | exact runtime | available | no |
| `P5BM-PS7330-SOURCE` | Amazon `rtmutex.c` source-member metadata | exact source family | available | no |
| `P5BM-PS7330-BOOT-PROBE` | installed boot read probe | exact device | access denied | no |
| `P5BM-PS7330-VMLINUX` | signed boot/Image/vmlinux | exact device | not present | no |
| `P5BM-PS7330-BOOTCHAIN` | preloader/LK/recovery set | exact device | not present | no |
| `P5BM-PS7331-OTA` | official full OTA | adjacent version | available, mismatch | no |
| `P5BM-PS7331-BOOT` | OTA `boot.img` | adjacent version | available, mismatch | no |
| `P5BM-PS7331-RTMUTEX-SOURCE` | build-selected source | adjacent version | available, mismatch | no |

Machine-readable output：
[`phase5bm-artifact-ledger-20260804-01/`](../artifacts/phase5/phase5bm-artifact-ledger-20260804-01/)

## Relation to GhostLock

公開 CVE 資料把 GhostLock (`CVE-2026-43499`) 的修補語意放在
`remove_waiter()` 的 waiter-task cleanup；Phase 5BJ／5BF 的 source 與 PS7331
inspected Image 仍呈現 pre-fix 方向。[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)

本 ledger 的結果只會把結論限定在：

```text
PS7330 source/config: relevant source-level path
PS7331 source/Image: adjacent-version pre-fix evidence
PS7330 signed binary: not available for direct confirmation
temporary root: not demonstrated
```

## 磁碟空間

盤點時 workspace 所在檔案系統約有 31 GiB 可用空間。沒有刪除任何 source、OTA、
raw capture 或大型 artifact；現階段不需要為了空間清理研究資料。

## Reproduction

```sh
python3 tools/scripts/build_phase5bm_artifact_ledger.py --repo . --output \
  artifacts/phase5/phase5bm-artifact-ledger-YYYYMMDD-NN --dry-run

python3 tools/scripts/build_phase5bm_artifact_ledger.py --repo . --output \
  artifacts/phase5/phase5bm-artifact-ledger-YYYYMMDD-NN
```

腳本只讀 host filesystem，拒絕覆寫既有 output，並不呼叫 ADB 或其他裝置工具。
