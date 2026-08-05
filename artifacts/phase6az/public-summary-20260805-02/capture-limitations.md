# Phase 6AZ public-summary redaction

This directory is derived from the explicit-serial read-only capture. Full
raw dumps remain local under `adb/phase6az/PHASE6AZ-RO-20260805-02/` and are not
published here because they may contain user-specific settings, identifiers,
or unrelated application details. The summary retains the build identity,
HOME resolver/candidate evidence, Fire Launcher package state, relevant active
activity lines, private service visibility, security state, and only the
presence (not values) of matching settings keys.

The small `control-state-summary.txt` records only the explicitly queried
launcher-control key and whether the corresponding package was installed; it
contains no user data.

No device mutation, Binder transaction, broadcast, install, reboot, or
partition operation was performed by the summary builder.
