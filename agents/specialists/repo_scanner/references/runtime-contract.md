# Repo Scanner runtime contract

## Contents

- [Read-only operations](#read-only-operations)
- [Scaffold write](#scaffold-write)
- [Safety boundary](#safety-boundary)

## Read-only operations

`scan_repo` and `evaluate_score` validate a literal `owner/repo` string, derive a character-sum seed,
and synthesize structure flags, sub-scores, and one of `auto_scaffold`, `evaluate`, `watch`, or `skip`.
They make no GitHub request and do not inspect a checkout.

## Scaffold write

`scaffold_specialist` accepts a snake_case name, refuses an existing target, and copies
`agents/specialists/_template` to `agents/specialists/<name>` when the template exists. If it is absent,
the function returns `simulated` with an expected file list and writes nothing. A successful copy is a
skeleton, not a working specialist.

## Safety boundary

Require explicit approval of the proposed target before the write. Never reinterpret a synthetic
score as repository quality or existence evidence. Do not overwrite a directory, escape the fixed
specialists parent, or describe simulated structure flags as observations from GitHub.
