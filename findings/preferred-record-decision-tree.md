# Preferred record exists but does not win

## Decision tree

```text
HOME MAIN+HOME intent for user 0
    |
    +-- Is there a valid persistent preferred record?
    |       |
    |       +-- Yes -> apply it if its filter, user and component are valid
    |       |
    |       +-- Not observed in canonical persistent query -> continue with
    |               ordinary candidate resolution; negative is bounded
    |
    +-- Query enabled HOME candidates
    |       |
    |       +-- Fire Launcher: effective priority 50
    |       +-- Microsoft Launcher: effective priority 0
    |       +-- FallbackHome: effective priority -1000
    |
    +-- chooseBestActivity compares leading priority/order/default state
            |
            +-- Fire wins before ordinary preferred tie branch
            |
            +-- Microsoft mAlways=true record remains stored but is not used
                    as the effective result
```

## Why `mAlways=true` is not enough

`mAlways=true` records express a preferred choice within the ordinary preferred
resolution path. They do not universally override a stronger leading candidate
when `chooseBestActivity()` has already decided on priority. The preserved
Phase 3A Microsoft record is therefore compatible with the resolver returning
Fire.

## Required validity checks

The following checks are captured or bounded as follows:

| Check | Evidence | Status |
|---|---|---|
| intent action/categories | Fire and Microsoft HOME candidate query; preferred XML contains MAIN/HOME/DEFAULT | Confirmed |
| user ID | baseline and Phase 3A tests use User 0 | Confirmed |
| component enabled | Fire package User 0 `enabled=0` (default enabled) and candidate appears | Confirmed |
| ordinary record stored | preferred dump contains Fire selected and Phase 3A Microsoft write | Confirmed |
| distinct persistent HOME record | no separate active record observed; command support is limited | Strong evidence / bounded |
| candidate priority | Fire 50; Microsoft 0; FallbackHome -1000 | Confirmed |
| Amazon resolver callback return | callback API exists; concrete return not observed | Unknown |
| boot-time rewrite | no new reboot in Phase 3B | Unknown |

## Conclusion

The current evidence does not require an Amazon resolver override to explain
the stored-but-unused preferred record. The decisive observed condition is the
effective priority gap.
