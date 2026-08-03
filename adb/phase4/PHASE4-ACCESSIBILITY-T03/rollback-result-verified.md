# PHASE4-ACCESSIBILITY-T03 rollback — verified summary

- `settings get secure enabled_accessibility_services` returned an empty value
  before package removal.
- Only `org.fireosresearch.phase4.redirect` and
  `org.fireosresearch.phase4.alias` were removed.
- `pm path` returned no path for either research package after rollback.
- Fire Launcher package state and data were not targeted.
- Final HOME resolver: `com.amazon.firelauncher/.Launcher` with effective
  priority 50.
- Final ADB state: `device`.
- Full before/after snapshots, command outputs, and SHA-256 manifests remain in
  this directory.
