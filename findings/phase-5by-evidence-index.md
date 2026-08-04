# Phase 5BY evidence index

| Evidence ID | Source | Location | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| P5BY-001 | PS7331 selected source | `rtmutex.c:973,977,1089,1683-1684` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | Early deadlock return precedes waiter assignment; proxy wrapper conditionally calls `remove_waiter`; cleanup is current-task | Confirmed, source scope |
| P5BY-002 | Host-only fix-chain checker | `artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/fix-chain.json` | `4e15b1302f3b3b3691fe3310298f639207365c3c78c6afece780fdb2791667d9` | `PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW` | Confirmed, host-only |
| P5BY-003 | NVD follow-up record | [CVE-2026-53163](https://nvd.nist.gov/vuln/detail/CVE-2026-53163) | External primary record | Follow-up issue concerns `remove_waiter()` on an un-enqueued waiter after the primary fix | Confirmed, upstream scope |
| P5BY-004 | NVD primary record | [CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499) | External primary record | Primary fix changes current-task operations to waiter-task operations | Confirmed, upstream scope |
| P5BY-005 | Fixed-reference limitation | `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` | Reference is primary-fix semantic only; not claimed as complete follow-up fix | Confirmed |
| P5BY-006 | Safety boundary | `artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/sha256sums.txt` | Manifest verified | No compilation, device I/O, futex trigger, offset, or payload | Confirmed |

The evidence does not authorize live exploit or boot-chain execution.
