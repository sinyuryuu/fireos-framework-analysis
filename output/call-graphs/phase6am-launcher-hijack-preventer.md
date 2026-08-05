# Phase 6AM launcher-hijack callback graph

```mermaid
flowchart TD
  A[HOME / ActivityTaskManager] --> B[Vendor callback fan-in]
  B --> C[ActivityStack callback]
  C --> D[canSeeHomeTask]
  D --> E[SELinux amazon_policies:see_home_task]
  D --> F[platform-signature check]
  D --> G[visibility boolean only]
  B --> H[other HOME pre-resolution callbacks]
  H --> I[PackageManager resolver path]
  J[Permission callback] --> K[blockDevelopmentPermPersist]
  K --> L[record package/user for READ_LOGS revoke]
  M[PackageManager callback] --> N[onShutdown]
  N --> O[revoke READ_LOGS for stored package/user pairs]
  P[PackageWhitelisterCallback] --> Q[updated-system/fdrw package bookkeeping]
  Q --> R[/data/system/fdrw_apks.conf]
  G -. no ResolveInfo/component .-> S[No direct Fire HOME selection]
  L -. permission policy, not HOME .-> S
  O -. shutdown permission cleanup, not HOME .-> S
  R -. package bookkeeping, not HOME .-> S
```

flowchart TD
  A[HOME / ActivityTaskManager] --> B[Vendor callback fan-in]
  B --> C[ActivityStack callback]
  C --> D[canSeeHomeTask]
  D --> E[SELinux amazon_policies:see_home_task]
  D --> F[platform-signature check]
  D --> G[visibility boolean only]
  B --> H[other HOME pre-resolution callbacks]
  H --> I[PackageManager resolver path]
  J[Permission callback] --> K[blockDevelopmentPermPersist]
  K --> L[record package/user for READ_LOGS revoke]
  M[PackageManager callback] --> N[onShutdown]
  N --> O[revoke READ_LOGS for stored package/user pairs]
  P[PackageWhitelisterCallback] --> Q[updated-system/fdrw package bookkeeping]
  Q --> R[/data/system/fdrw_apks.conf]
  G -. no ResolveInfo/component .-> S[No direct Fire HOME selection]
  L -. permission policy, not HOME .-> S
  O -. shutdown permission cleanup, not HOME .-> S
  R -. package bookkeeping, not HOME .-> S
