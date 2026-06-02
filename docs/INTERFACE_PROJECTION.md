# Interface Projection

`InterfaceProjection` marks the boundary between native runtime objects and
public outputs.

The runtime can contain rich internal objects:

```text
StatePool
BranchTensor
ReductionGateResult
AdapterResult
```

Public outputs should not expose those objects directly as the API shape. They
are projected into JSON-ready payloads with explicit projection metadata:

```text
projection.kind
projection.reason
payload
```

Current API:

```text
InterfaceProjection
project_public_summary(kind, payload, reason=...)
project_adapter_summary(payload)
project_runtime_summary(payload, reason=...)
interface_projection_to_dict(projection)
```

Acceptance checks:

```text
Runtime state is not treated as the public API shape.
Each public output includes a projection reason.
Adapters and summaries use projection helpers.
```
