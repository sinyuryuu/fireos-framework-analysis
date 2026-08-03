# Phase 3C workaround classification

| Class | Result | Status |
|---|---|---|
| A. True HOME replacement | ordinary p0 preferred record does not change resolver | 已排除 |
| B. Persistent system setting workaround | no supported HOME setting reader found | 待驗證 |
| C. Temporary shell workaround | explicit activity start can display a launcher, not HOME | 高可信推論 |
| D. Accessibility/foreground workaround | not implemented; no hidden persistence designed | 待驗證 |
| E. Invalid/unavailable | p0 preferred state ineffective; HOME role/device_config unavailable | 已證實 |
| F. High risk | Fire mutation, core overlay, provisioning, Device Owner | 因風險拒絕測試 |

No persistent no-root HOME replacement was confirmed.
