# Phase 6QE — PS7331 7.3.3.1 GPL custom driver / node policy / shipped client

日期：2026-08-10（Asia/Taipei）  
範圍：只讀 `firmware/extracted/PS7331-SOURCE-20250617`、PS7331 image/extracted policy artifacts 與既有報告。沒有開啟任何真機 device node，沒有 ioctl/proc write/debugfs、Root、exploit、Binder、OTA 或分割區操作。

## 結論

Source capability 與 shipped reachability 必須分開。source 中 CMDQ/MDP、M4U、performance ioctl、gsensor factory、IDME/lifecycle 與 `amzn_drv_test` 都能看到不同程度的 registration、user-copy 或 fops；但 exact-image evidence 顯示實際 node policy 主要由 init mode/owner、SELinux type/allow、build/config 與 client domain 共同決定。未發現任何 evidence 可把缺少 `capable()` 宣稱成一般低權限可利用。

- CMDQ/MDP：source 有 `/dev/mtk_cmdq` ioctl 與 MDP register/job path；exact image 為 `0644 system:system`，label `mtk_cmdq_device`。policy 有 `appdomain` read/ioctl allow，但沒有由此推導任意 app、caller 或可利用性；已知具體 privileged/mediaserver/surfaceflinger/graphics domains 的 allow 也只證明 policy route。
- M4U：source active path 是 `/proc/m4u`，`/dev/m4u` misc branch 不活躍；exact init 設為 `0440 system:media`，並有 `M4U_device_device` label。`mediacodec` 對 M4U char device 有 allow；未建立普通 app caller 或實際 proc access。
- performance：source `/proc/perfmgr/perf_ioctl` mode `0664`，exact policy type 為 `proc_perfmgr`；allow 分散於 system/mediaserver/graphics/MTK power 等 domains，沒有 ordinary-app write allow 證據。mode 的 owner/group write 不等於 world write。
- gsensor：source factory ioctl 無 local `capable()` gate；exact init normal path 為 `0660 radio:system`，factory init 另有 `0666`，label `gsensor_device`。policy allow 見 `radio` read/ioctl、`meta_tst`/NVRAM domains；factory stanza 是 image policy evidence，不是 retail runtime 選路或低權限 reachability 證明。
- IDME/lifecycle：source IDME 與 `/proc/life_cycle_reason` 是 read-only/bounded negative；exact policy 有 IDME HAL/client reads 與 `system_server` lifecycle read。這些不是 userspace write sink。
- `amzn_drv_test`：source 定義 owner-writable `/proc/amzn_drvs/{sign_of_life,idme,logger}` test dispatcher，但 `trona_defconfig` 沒有 `CONFIG_AMZN_DRV_TEST=y/m`，且 official boot Image 未觀察到專屬 `amzn_drvs`/test-function markers。這是 bounded negative/conditional build evidence，不是 runtime 絕對不存在證明；不把 index 21/23 的 test labels 當成 shipped factory-reset/RTC reachability。

## Exact-image policy evidence

主要 input 是既有 Phase 6C policy extract：

`artifacts/phase6c/phase6c-image-policy-extract-20260804-06/`

關鍵檔案與 SHA-256：

| Artifact | SHA-256 |
|---|---|
| `vendor/etc/selinux/vendor_file_contexts` | `db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e` |
| `vendor/etc/selinux/vendor_sepolicy.cil` | `82430dbe87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035` |
| `vendor/etc/init/hw/init.mt8183.rc` | `bbd2d5a1d891735718272f1d8a9f8b1248ba4aa034e8915951a076759d3cfcac` |
| `vendor/etc/init/hw/init.sensor_1_0.rc` | `03ced918cd07f8354667ea6205a5281fc22161cc22aa3f2e0a0255bc870a9be3` |
| `vendor/etc/init/hw/factory_init.rc` | `7f22a66cbe9188e83f329fc1db83c8ebf3c083fb81275c068405ebe835925e73` |

Policy joins：`vendor_file_contexts:304` → `/dev/gsensor` → `gsensor_device`；`:326` → `/dev/mtk_cmdq` → `mtk_cmdq_device`；`:376` → `/dev/M4U_device` → `M4U_device_device`。`init.mt8183.rc:293-303` sets `/dev/m4u` 0444, `/proc/m4u` 0440 `system media`, and `/dev/mtk_cmdq` 0644 `system system`; `init.sensor_1_0.rc:8,31` sets gsensor 0660 `radio system`; factory init has a separate 0666/system setup. `vendor_sepolicy.cil` includes `appdomain → mtk_cmdq_device` read/ioctl, `mediacodec → M4U_device_device` read/write/ioctl, `radio → gsensor_device` read/ioctl, and `system_server → proc_life_cycle_reason` read; it also contains privileged perfmgr routes. An allow rule is policy capability evidence, not proof of a live caller or effect.

## Client mapping

The selected exact-image client set is limited to framework jars and Fire OS privileged APKs listed in `firmware/extracted/PS7331/selected/extraction-manifest.tsv`, with compiled artifacts in `compiled-02`. Host-only string scans found no direct `/dev/mtk_cmdq`, `/dev/gsensor`, `/proc/m4u`, `/proc/perfmgr/perf_ioctl`, or `/proc/amzn_drvs` literal in the selected framework jars/APKs. `TabletSystemUI.apk` contains the generic string `mCmdQueue`; Fire Launcher contains `M4U` strings, but these are not sufficient to establish a driver client, ioctl ABI, node open, or sink. Therefore shipped-client mapping is `not established` for the selected app/framework subset. Policy-domain mappings remain the stronger static evidence: graphics/media/MTK HAL/system domains, not an identified untrusted app.

## Guardrails and residuals

No source permission mode, `device_create`, `proc_create`, `copy_from_user`, SELinux allow, or absent `capable()` check is treated as a confirmed low-privilege route. Remaining uncertainty is limited to generated config/module inclusion, exact runtime init branch, compiled/loaded module set, indirect/native clients outside the selected artifacts, and policy/runtime state not preserved in the scoped files. Further work, if authorized, should remain offline: normalize `registration → node → init mode/owner → file_context → domain allow → exact client → sink`, with `source-only`, `policy-capability`, `client-not-established`, and `shipped-reachability` kept as separate classifications.

## Evidence references

- `work/luna_worker_gpl_driver_surface_inventory_20260810.md/.csv`
- `work/luna_worker_kernel_gpl_driver_surface_followup_20260810.md/.csv`
- `work/luna_worker_phase6na_amzn_drv_test_closure_20260810.md`
- `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-02/phase6nb-amzn-drv-test-source-closure.md`
- `artifacts/phase6nd-amzn-drv-test-image-marker-20260810-01/phase6nd-image-marker-audit.md/.csv`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/`

