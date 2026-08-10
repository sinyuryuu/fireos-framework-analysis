# Phase 6QD privilege-surface graph (text form)

```text
low-privilege app/shell
  -> caller + accepted gate not proven
  -> do not invoke private API or device node

Amazon IPC candidates
  -> PM flags / DPM / Profile / WMS / Vending
  -> caller, user, first sensitive consumer unresolved

CMDQ / MDP
  -> /dev/mtk_cmdq
  -> async/readback/MDP register operations
  -> final node owner/SELinux/shipped client unresolved
  -> hardware/display sink; no PMS/HOME/root sink shown

M4U
  -> __M4U_USE_PROC_NODE
  -> /proc/m4u (not /dev/m4u in active source branch)
  -> DMA/IOMMU sink; access policy unresolved

Amazon driver test
  -> factory-reset / RTC special modes
  -> CONFIG_AMZN_DRV_TEST absent in trona_defconfig
  -> conditional engineering source; not shipped-confirmed

Privileged OTA controller
  -> certificate + product/PVT + recovery gate
  -> update-binary -> block_image_update -> partition write
  -> high-impact capability; ordinary caller not proven

All reviewed paths
  -> no closed low-privilege -> system/root -> sensitive sink chain
```
