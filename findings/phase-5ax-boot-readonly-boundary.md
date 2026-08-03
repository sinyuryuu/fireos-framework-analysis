# Phase 5AX：PS7330 boot／LK／recovery 唯讀可得性邊界

## 目的

本輪嘗試從 Android shell 只讀取得 exact PS7330 的 boot、LK、recovery block
metadata 與 4 KiB header。目標是確認能否取得 GhostLock binary-level analysis
所需的 boot image；不涉及任何寫入。

沒有執行：

- root 或 su；
- futex/GhostLock trigger；
- ION/CMDQ ioctl；
- fastboot、BROM、DA 或 bootloader command；
- remount、分割區寫入或 reboot；
- userdata 讀取。

## 結果摘要

**已證實：**

| 項目 | 結果 |
|---|---|
| boot link | /dev/block/mmcblk0p16 |
| lk link | /dev/block/mmcblk0p5 |
| recovery link | /dev/block/mmcblk0p17 |
| block device SELinux label | u:object_r:block_device:s0 |
| blockdev size query | Permission denied，三者皆同 |
| boot 4 KiB read | Permission denied |
| lk 4 KiB read | Permission denied |
| recovery 4 KiB read | Permission denied |
| exact signed boot image | 未取得 |
| exact signed LK image | 未取得 |
| exact signed recovery image | 未取得 |

這排除了「普通 shell 可以直接讀取 boot block」這個低風險入口，但沒有嘗試
任何權限繞過。

## 1. Exact device context

Capture：

adb/phase5/PHASE5AX-BOOT-READONLY-20260804-03/

| 欄位 | 值 |
|---|---|
| Build fingerprint | Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys |
| Incremental | 0030099376260 |
| Kernel | Linux 4.4.146+ #1 SMP PREEMPT Sat Jul 13 02:13:14 UTC 2024 aarch64 |
| Verified boot | green |
| Flash locked | 1 |
| ADB caller | UID 2000 / u:r:shell:s0 |
| SELinux | Enforcing |

## 2. Commands and observations

### Metadata

命令：

adb -s SERIAL shell readlink -f /dev/block/by-name/boot
adb -s SERIAL shell ls -lZ /dev/block/by-name/boot
adb -s SERIAL shell blockdev --getsize64 /dev/block/by-name/boot

相同命令分別對 lk、recovery 執行。

觀察：

- symlink target 與 block_device label 可列出；
- blockdev 對 boot、lk、recovery 都回傳 Permission denied；
- metadata visibility 不代表 data read permission。

### Header read

修正後命令：

adb -s SERIAL exec-out sh -c 'dd if=/dev/block/by-name/boot bs=4096 count=1'

相同命令分別對 lk、recovery 執行。

三個輸出不是 binary header，而是 shell error text：

- boot：dd: /dev/block/by-name/boot: Permission denied
- lk：dd: /dev/block/by-name/lk: Permission denied
- recovery：dd: /dev/block/by-name/recovery: Permission denied

因此沒有把 error text 當作 boot image，也沒有計算錯誤資料的 image hash。

## 3. Evidence hashes

| File | SHA-256 |
|---|---|
| identity.stdout.txt | c408fdf7daa58d5e511b604354ae479ef04c2160253e3baca9803e8c6c7000f8 |
| path_boot.stdout.txt | 0cd1b159a0b93afd11d1c1f5697509ce74a6bc172db7138a05046af0da5b3d66 |
| head_boot.bin | 1d05472748ba378637edff1e48bf08121309f0ce177fdb7a18b4a3b15b146874 |
| path_lk.stdout.txt | 1283bac6b4d1fe5b5a781803636d03c0ff7967380c03a94b46ff75579372a047 |
| head_lk.bin | 2d90fcef78444ddd64159c07bb504d948414fb3df377ac8f387aa053b953f8d7 |
| path_recovery.stdout.txt | 07c1d51c3654ebec70216d020819789760ce711b2cfd704ef1207c9ffd7d183a |
| head_recovery.bin | b93ab90efea0a008cee9a424891f1a754438f8bff43317eec3663b5ae13a1ebe |
| sha256sums.txt | 49b5ef5a7c9886accc5cb21f0b231ba2325a9fc40b3610aafaf4f16a65bfc773 |
| capture_phase5ax_boot_readonly.sh | 3a73e3abd940c3aad6deecbf4d755b415ec261f1fd348b8751c7addd68f76860 |

完整逐檔雜湊在 capture 目錄的 sha256sums.txt。

## 4. Safety post-check

只讀採集後：

- adb state：device；
- build：PS7330.4104N；
- mResumedActivity：com.amazon.firelauncher/.Launcher；
- realActivity：com.amazon.firelauncher/.Launcher；
- 沒有 package、settings、filesystem、boot 或 partition state mutation。

## 5. 判定

**已證實：** Android shell 能看見 block-device 名稱與 label，但不能讀取
boot、LK 或 recovery 資料。

**已證實：** exact PS7330 signed boot/vmlinux 仍不是目前 ADB 可讀 artifact。

**高可信推論：** 若沒有另行取得官方或研究者合法保存的 exact PS7330 image，
就不能做 compiled remove_waiter、task_struct offset、KASLR 或 target-specific
GhostLock header 的可靠分析。

**已排除：** 以普通 adb pull、blockdev 或 dd 直接取得 boot image。

**因風險拒絕測試：** 不使用 root、SELinux bypass、未知 ioctl、BROM/DA、fastboot
read/write、preloader/LK 操作或任何權限繞過。

## 6. Reproduction

主機腳本：

tools/scripts/capture_phase5ax_boot_readonly.sh

唯讀 dry-run：

tools/scripts/capture_phase5ax_boot_readonly.sh \
  --serial G001LT0511550CFT \
  --output /tmp/phase5ax-dry-run \
  --dry-run

唯讀 capture：

tools/scripts/capture_phase5ax_boot_readonly.sh \
  --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5AX-BOOT-READONLY-20260804-03

--full-boot 只會在 shell 具備讀權限時嘗試讀 boot；本機已先以 4 KiB probe
確認 Permission denied，沒有執行不必要的完整錯誤讀取。
