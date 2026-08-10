# Phase 6QC privilege-closure graph (text form)

The Mermaid source is `phase6qc-privilege-closure.mmd`. The same graph in plain
text is:

```text
low-privilege caller
  -> [accepted gate not established]
  -> do not invoke private Binder / OTA / native path

Alexa system/priv-app
  -> IAmazonActivityManager tx=1
  -> preWarmApplicationForUser
  -> APP_PREWARM result not observed consumed
  -> clearCallingIdentity
  -> getApplicationInfo
  -> PreWarmCacheHelper
  -> startProcessLocked("prewarm")
  -> process-prewarm only; no HOME/PMS/root sink observed

AmazonAspService
  -> tablet branch returns true before ASP_PERMISSION
  -> nativeCommand / capture / injection / IR
  -> audio/HAL-adjacent sink; saved shell runtime was EACCES

AmazonAudioService
  -> signature/privileged audio permission checks
  -> AudioSystem / routing / Dolby / HDMI / volume
  -> no package/HOME/root writer in reviewed scope

Privileged OTA controller
  -> hash + certificate + product/PVT checks
  -> UpdateSystem.install
  -> recovery/update-binary
  -> extraction or block_image_update
  -> WriteToPartition -> ota_write -> write
  -> recovery capability; shell caller not established

MakeFreeSpaceOnCache
  -> readlink marker
  -> direct edge to write sink not found; indirect data-flow unresolved

All reviewed branches
  -> no closed low-privilege -> system/root -> sensitive sink chain
```
