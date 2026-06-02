# State Pool Runtime

`StatePool` is the first public step after the adapter phase toward a native
batched runtime.

It wraps candidate-major states with runtime annotations:

```text
states
scores
uncertainty
alive_mask
metadata
```

The pool is initialized from CTIR batch metadata and remains JSON-summarizable.
It does not replace `StateBatch`; instead, it makes the batch a first-class
runtime object that later phases can feed into branch tensors, reduction gates,
interface projections, and ledgers.

Current API:

```text
initialize_state_pool(problem)
state_pool_with_scores(pool, scores)
mask_state_pool(pool, alive_mask)
state_pool_summary(pool)
```

Acceptance checks:

```text
StatePool can initialize from CTIR.
StatePool records batch score and alive mask.
StatePool exports a JSON-ready summary.
```
