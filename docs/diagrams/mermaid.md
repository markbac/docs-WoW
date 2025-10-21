# Mermaid examples

```mermaid
flowchart TD
  A[Start] --> B{Choice?}
  B -->|Yes| C[Do the thing]
  B -->|No| D[Abort]
  C --> E[Finish]
  D --> E[Finish]
```
