# Phase 4B — ranking control surface

The only ranking factor a normal sideloaded HOME APK can declare directly is
its intent-filter shape. Positive manifest priority is capped to zero by
`adjustPriority()` unless the package is privileged/system. `preferredOrder` is
not an ordinary application control, and the observed shell preferred API does
not change the top-field gate. `match` and `isDefault` can be explored with
filter composition, but they cannot make a priority-0 candidate cross a
priority-50 candidate when the first two ranking fields differ.

`persistent preferred` is a separate, stronger state source in the code, but a
normal shell user cannot safely create a device-policy persistent preference on
this device without entering provisioning/Device Owner territory. That route is
therefore static-only and marked **因風險拒絕測試**.

`last chosen` is a chooser-history mechanism in AOSP (`setLastChosenActivity()`
and `getLastChosenActivity()`), not a documented HOME replacement mechanism.
The Android 9 HOME chooser's top-field branch returns before ordinary preferred
lookup, so it is not a credible bypass for Fire priority 50.

See `output/tables/phase-4b-ranking-factors.csv` for the complete factor-by-factor
matrix and exact experiment decisions.
