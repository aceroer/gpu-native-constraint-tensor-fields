# Layout Materialization

Layout planning declares required views. Materialization builds selected host
views and records concrete conversion costs.

Implemented host conversions:

```text
state.candidate_major -> state.variable_major
linear.csr -> linear.csc
violation.dense -> violation.active_compact
```

Each conversion returns a `MaterializedLayout`:

```text
name
data
cost
```

The cost ledger records read/write element counts. For active violation
compaction, `elements_written` is the actual number of active entries, while the
layout planner records an upper bound.
