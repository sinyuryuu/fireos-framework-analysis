# Phase 12 control-surface graph (text form)

```text
ordinary app / shell
  -> Binder or framework entry
  -> caller + permission + identity + user scope?
     -> KFT child path: UserInfo.id -> child/profile state only
     -> PMS path: standard protected-package/preferred/cross-user gates
     -> OTA path: recovery/update-binary capability, not invoked
     -> driver path: node/policy/native caller missing
  -> no closed User-0 Fire/HOME/UID0 path established
```

The graph intentionally stops at unknown edges; it is not an exploit recipe.
