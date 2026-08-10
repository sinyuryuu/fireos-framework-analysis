# Phase 6SB–SE control-surface graph

```mermaid
flowchart LR
  A["Preserved PS7331 artifacts"] --> B["6SB IPC / permission audit"]
  A --> C["6SC kernel / driver join"]
  A --> D["6SD OTA / install chain"]
  A --> E["6SE evidence quality catalog"]
  B --> F["metadata XML / KFT writer / PMS gates"]
  C --> G["device nodes / proc surfaces / unknown caller"]
  D --> H["privileged recovery capability / unknown provenance"]
  E --> I["status and evidence normalization"]
  F --> J["No new ordinary-app or shell HOME/package-state bridge"]
  G --> J
  H --> J
  I --> J
  J --> K["Safe next step: host-only completeness; no payload or mutation"]
```

Text form:

```text
preserved PS7331 artifacts
  ├─ 6SB IPC/permission -> metadata/KFT writers -> PMS gates
  ├─ 6SC kernel/driver -> device/proc surfaces -> caller mostly UNKNOWN
  ├─ 6SD OTA/install -> privileged recovery capability -> provenance UNKNOWN
  └─ 6SE catalog -> status/evidence normalization
          └─ no new ordinary-app or shell HOME/package-state bridge
```
