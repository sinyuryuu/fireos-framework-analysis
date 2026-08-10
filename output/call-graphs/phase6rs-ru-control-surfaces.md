# Phase 6RS–RU control-surface graph (text form)

```text
ordinary app / shell
  -> caller permission and user gate
      -> SettingsProvider: SettingsState/XML persistence
      -> PMS setHomeActivity: preferred-activity XML
      -> SystemUI/Amazon callbacks: resolver/window/profile/event sinks
  -> HOME resolver ranking
      -> Fire priority 50 -> com.amazon.firelauncher/.Launcher

Accessibility consent or active ADB monitor
  -> delayed explicit third-party launch
  -> foreground only; no resolver/package-state mutation

Amazon PM metadata mutator
  -> ADD_RM_PKG_METADATA + unresolved production caller/holder
  -> no Fire HOME/package writer shown

Protected OOBE/OTA lifecycle
  -> OOBE/setup writer
  -> not a Fire HOME writer
```

The dashed edges represent bounded negative or unresolved evidence, not a
permission claim. No unknown Binder transaction, broadcast, settings/package
mutation, OTA/recovery replay, driver operation, Root or exploit was used.
