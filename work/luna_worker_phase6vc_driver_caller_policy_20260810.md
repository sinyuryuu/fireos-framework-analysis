# Phase 6VC — GPL kernel/native-driver exact-device caller/policy closure

日期：2026-08-10（Asia/Taipei）  
裝置：Amazon KFTRWI / trona / MediaTek MT8183 / PS7331，Android 9，kernel 4.4.146+

## 結論

本次是 host-only 靜態 closure。沒有開啟 `/dev` 或 proc 節點、沒有 ioctl、沒有寫 sysfs/proc/debugfs、沒有載入 module、沒有執行 native probe。

依「exact source/config + exact shipped node/DT/init/ueventd/file_contexts/vendor-TE + built-in/module delivery + exact native/APK caller + sink」五段均需相同 path/裝置閉合的規則，沒有任何 row 可標 `POSITIVE`。結果如下：

| Surface | Source/config | DT/init/ueventd/policy | Built-in/module | Exact native/APK caller | Package/HOME/privilege sink | Result |
|---|---|---|---|---|---|---|
| `/dev/mtk_cmdq` / CMDQ-MDP | `cmdq_driver.c:660-743,848-865,894-898`; `kernel.config:1247-1248`; `phase6ft` 已追出 `cmdq_ioctl → CMDQ_IOCTL_ASYNC_EXEC → MDP secure path` | 已保存 node metadata：`0644 system:system`, `mtk_cmdq_device`（`work/luna_worker_phase6sl_driver_callers_20260810.md`）；vendor file-context/TE 行號同報告 `:5228-5229,5754,6087,6199`；完整 exact DT/init/ueventd join 未保存 | `CONFIG_MTK_CMDQ=y`, `CONFIG_MTK_CMDQ_TAB=y`; Image/object/module provenance 未閉合 | phase5cs native inventory 與 TC join 沒有 exact shipped ELF 的 `/dev/mtk_cmdq` open + CMDQ ioctl call-site/relocation tuple | 未找到 AMS/ATMS/PMS/HOME 或 privilege sink；phase6ft 明確記錄無 AMS/ATMS/PMS/HOME data flow | **UNKNOWN** |
| `/dev/ion` / MTK custom ION | `ion.c:1478-1617,1657-1658,1906-1924`; `ion_drv.c:428-492,703-736`; `kernel.config:3532-3534` | 保存 metadata：`0666 system:graphics`, `ion_device`（`phase6un`/`phase6so`）；vendor CIL refs `:3066,4170,4325,4417`；final ueventd/file_contexts/TE source 與 DT/init instance 未完全保存 | `CONFIG_ION=y`, `CONFIG_MTK_ION=y`; final built-in vs module/object manifest unknown | `phase6so` 僅證明 `libion.so` 的 `/dev/ion` strings、`ion_open/alloc/map/share/import/sync` 與 ioctl sites，及 `libion_mtk.so` custom sites；沒有 top-level shipped process/APK consumer、native call chain 或 runtime invocation | allocation/map/share/import/sync 可影響 memory/DMA；沒有 package/HOME/Settings/PMS/privilege effect 的 caller/sink join | **UNKNOWN**（library capability only） |
| Amazon-LD sysfs/module params | `amzn_ld.c:618-738,878-896`; `CONFIG_AMAZON_LD=y`, `CONFIG_AMAZON_LD_SWITCH=y`（`phase6un`） | source-declared 0664 stores/module params；無 ueventd rule 可適用 sysfs；exact trona DT match、file_contexts、vendor-TE allow、init action 未閉合；既有 shell audit 只記錄 denied/無 exposed attrs，未寫入 | exact Image symbol/object/module delivery unknown | phase6tc/phase6so native inventory 沒有 exact sysfs attribute path + shipped ELF write call-site | 未找到 framework/package/HOME/privilege sink；source capability 不等於 caller | **UNKNOWN / bounded closed** |
| `/proc/amzn_drvs/*` Amazon diagnostics | `amzn_drv_test.c` source；`phase6nb`：proc root `amzn_drvs`、children `sign_of_life/idme/logger`、write fops | `phase6nb`/`phase6sl`：`CONFIG_AMZN_DRV_TEST=y/m` 不在 trona defconfig；既有 shipped snapshot 未見 `/proc/amzn_drvs`; final merged config/policy/caller 未閉合 | defconfig negative only；final generated `.config`, Image/module packaging unknown | `com.amazon.connectivitydiag` package 存在不構成 proc caller；native inventories 無 exact open/write caller | diagnostic package/HAL 名稱沒有 package-state、HOME、privilege-transition sink 證據 | **UNKNOWN / conditional source-only** |
| `/proc/idme/*` Amazon IDME | `amzn_idme.c:316-347`; `kernel.config:3583-3584` | 保存 proc metadata、IDME HAL init/CIL refs（`phase6un`：`4471-4473,4741-4749,5135-5137`）；exact file_contexts/TE + init-to-node closure 不完整 | `CONFIG_AMZN_IDME=y`; final object delivery not independently proven | IDME HAL/library presence only；無 exact ELF `/proc/idme` open/read call-site | 無 exact package/HOME/PMS/privilege sink | **UNKNOWN** |
| Amazon metrics/vitals | `amzn_logger.c:696-738`；read/poll/open/release-only misc fops | final node mode/label/ueventd/file_contexts/vendor-TE 未完全保存 | config/object delivery not independently proven | 無 exact shipped ELF open/read/poll caller | read-only source surface；無 higher-level sink | **UNKNOWN** |

## Native/APK inventory closure

* Native corpus：`artifacts/phase5/phase5cs-native-analysis-20260804-03` 及 phase6tc/6so caller joins；其中 library presence、strings、symbols 或 relocation marker 只算 capability。對 CMDQ、Amazon-LD、IDME、metrics/vitals 沒有 path-specific exact caller；ION 有 library-level marker，但無 top-level consumer/runtime invocation。
* APK/package corpus：既有 APK/manifest inventory（包括 `com.amazon.connectivitydiag`、Fire Launcher、SettingsProvider、Amazon PM/OTA 與 privileged APK manifests；phase6ad inventory）只提供 package/component/permission evidence。沒有任何 APK/JNI/native inventory 將上述 driver path 與 `open`/`read`/`write`/`ioctl` call site 及 package/HOME sink 同時閉合。
* 因此不能把 `libion.so`、`libion_mtk.so`、HAL 名稱、`com.amazon.connectivitydiag`、SELinux allow、service/init 名稱或 source `device_create` 升級成 exact caller 或 privilege path。

## Inputs and SHA-256

| Input | SHA-256 / status | 行號或 provenance |
|---|---|---|
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | phase6nb input-evidence；members 見 phase6nb report |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` member `amzn_drv_test.c` | `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e` | `phase6nb` source lines/CSV；Kconfig line 65、Makefile line 28、defconfig negative |
| `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | CMDQ `1247-1248`、ION `3532-3534`、IDME `3583-3584` |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | phase6fu；embedded config/symbol strings，不能單獨證明目前 booted image |
| phase6me input manifest | `ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a` | `kernel/source-manifest.json`；phase6me source/control marker closure |
| phase6me `driver-control-closure.csv` | `360168945378dc42c96868339a3ed2a92fa4dfb819e9a9043286a453906218cb` | 1,671 files、7,698 markers、395 source surface files；`summary.json` |
| phase6nb-04 input evidence | `sha256sums` file retained at `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-04/input-evidence-sha256sums.txt` | archive/member/config provenance |

## Unknown boundaries

1. 工作樹沒有 exact named `fireos.tar`；也沒有 `boot_unpacked/Image`。可用 canonical `boot.img`、embedded config、phase6fu Image-string output 與既有 inventories，但不能宣稱已直接檢查缺失檔名。
2. `platform.tar` source capability 不等於 final Android build inclusion；除保存 config 行外，generated merged `.config`、built-in vmlinux/object map、`.ko` packaging/loading、exact DTB instance 尚未全閉合。
3. 部分 policy evidence 是 extracted CIL/file-context 片段或既有 node metadata；缺失的 exact `ueventd*.rc`、init action、file_contexts/type、vendor-TE allow 必須保持 UNKNOWN。
4. native/APK inventory 是 bounded corpus；沒有 caller 不等於全世界不存在 caller，只能表示在保存 corpus 中未找到 exact path-specific call-site。
5. 沒有 runtime open/ioctl/sysfs write/probe，因此不推導有效 UID、capability、實際 module loaded state、driver instance、或任何 package/HOME/privilege effect。

## Safety and verification

本報告與 companion CSV 是本 worker 新增的唯一檔案。只使用 host `rg/find/sed/sha256sum` 與既有 evidence；未執行 ELF/native binary，未接觸裝置節點或 sysfs。CSV row-level evidence references are line-addressable to the cited reports/source locations above。
