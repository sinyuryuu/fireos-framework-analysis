# Phase 6QF — PS7331 host-only exact image/source policy-client mapping

Date: 2026-08-10. Host-only static inspection. No device node, ioctl, Binder
transaction, exploit, write, reboot, OTA, or partition operation was used.
The companion CSV is the normalized registration → init mode/owner →
file_context → SELinux domain/allow → exact client → sink matrix.

## Inputs and boundary

- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/` (image
  manifest, init rc, vendor file_contexts and vendor CIL).
- `firmware/extracted/PS7331-SOURCE-20250617/` (MT8183 CMDQ/MDP, M4U,
  performance, sensors, and Amazon driver source).
- Existing Phase 6C policy audits, `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-01/`,
  `work/luna_worker_phase6qe_driver_policy_20260810.md`, and
  `work/luna_worker_phase6na_amzn_drv_test_closure_20260810.md`.

`UNKNOWN` is intentional where exact final policy allow, compiled client,
image registration, or runtime reachability is absent. A generic SELinux type
or source registration is not promoted to an effective permission or client.

## Findings

| Surface | Exact host-side closure | Main unresolved gate |
|---|---|---|
| CMDQ/MDP | Source creates CMDQ character/debug proc interfaces; image labels `/dev/mtk_cmdq` and `/dev/mt-mdp`. | Exact domain allow, compiled userspace client, final node mode/owner. |
| M4U | Source registers M4U misc/proc interfaces; image labels `libm4u.so`, with M4U device types in CIL. | Exact runtime node/file_context, allow, and client. |
| perfmgr | Image init declares `system:system` and `0664/0660` on `/proc/perfmgr` paths; source registers perf ioctl, smart, legacy, and EAS controls. | Exact caller and allow; init declaration is not runtime existence. |
| gsensor | Image starts the Mediatek sensors HAL as `system:system`; `/dev/gsensor` maps to `gsensor_device`. | Exact HAL open/client path and `mtk_hal_sensors` allow. |
| IDME | Image starts IDME HAL as `system:system`; executable and boot block labels are exact. | Exact HAL-to-block allow and client path. |
| IDME/lifecycle | Source registers IDME and RTC-backed lifecycle proc semantics. | No exact image child label/allow/client closure. |
| amzn_drv_test | Source/Kconfig/Makefile closure is exact; three `/proc/amzn_drvs/*` entries requested. `trona_defconfig` omits `CONFIG_AMZN_DRV_TEST`. | Generated config/module inclusion, image label, allow, and client. |

The CSV preserves line-local references and a safe next step for each surface.
All next steps remain host-only source/config/policy inspection.

## Safety conclusion

This establishes static registration and policy markers only. It does not
establish node existence, normal-user reachability, or exploitability. No
device-side follow-up is authorized by this report.
