# Phase 6QE privilege-surface graph

```mermaid
flowchart TD
  A["ordinary app / shell UID 2000"] --> B["Amazon IPC or driver node boundary"]
  B --> C["caller / permission / SELinux / user-scope gate"]
  C --> D["system or trusted lifecycle identity"]
  D --> E["PM / HOME / package state / OOBE / OTA sink"]
  B --> F["source capability only"]
  F --> G["exact init mode + file label + shipped client mapping"]
  G --> C
  H["Phase 6QE runtime metadata"] --> I["HOME = Fire Launcher priority 50"]
  H --> J["mtk_cmdq 0644 system:system"]
  H --> K["gsensor 0660 radio:system"]
  H --> L["m4u/lifecycle shell metadata denied"]
  C -. "not closed in reviewed scope" .-> D
  D -. "no ordinary caller evidence" .-> E
```

Text interpretation: source capability is not a caller path. A usable privilege
route would still require the exact node/service publication, accepted caller and
SELinux/permission gate, identity transition, user scope, and a sensitive sink.
