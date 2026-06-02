# Compatibility Adapters

Adapters are narrow public entry points. They do not replace the native APC
path, and they do not promise drop-in compatibility with existing solver APIs.

The current adapter is:

```text
native_binary_milp_dict
```

It lowers through the same pipeline as native inputs:

```text
dictionary
-> ProblemSpec
-> CTIRProblem
-> layout plan
-> operator registry
```

Unsupported solver-oriented features fail loudly before lowering:

```text
branching
callbacks
cutting_planes
lazy_constraints
presolve
solver
```

This keeps compatibility work bounded. Each future adapter should be judged by
whether it preserves the native execution structure rather than by how many
external API details it accepts.
