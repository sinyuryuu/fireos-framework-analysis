# Phase 4B final workaround verdict

## 正式 HOME replacement

**未找到新的可證實方案。** The ordinary preferred record remains below the
priority-50 privileged candidate, and the multi-activity/alias control did not
change candidate ranking or Home key behavior. No Fire state mutation was used.

## Closest safe approximation

The tested Accessibility redirect is **not viable on this build**: it made
30 explicit attempts but achieved 0 foreground handoffs. A different
user-consented design might use a foreground-visible interaction or a
notification/Quick Settings action, but that would be an explicit shortcut,
not an automatic HOME replacement. UsageStats observation remains a weaker,
unmeasured candidate and should not be advertised as a solution.

Measured latency and flash rate were not claimed because the target never
became resumed. Reboot persistence was not tested after the failed handoff.

## Paths not worth repeating

Priority APK matrix, ordinary `set-home-activity` persistence, HOME role/
device_config availability, random settings/overlay writes, and Fire Launcher
state mutation are respectively **已排除**, **已排除**, **已確認不可用**,
**已拒絕**, and **因風險拒絕測試** under the unchanged build/caller conditions.
