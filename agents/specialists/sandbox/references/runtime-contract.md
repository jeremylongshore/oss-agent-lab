# Sandbox prototype runtime contract

## Contents

- [Implemented operations](#implemented-operations)
- [Validation rules](#validation-rules)
- [Isolation boundary](#isolation-boundary)

## Implemented operations

`validate_code` applies language-specific substring checks and a 50,000-character ceiling.
`execute_code` validates language and timeout, then calls `_simulate_execution`, which returns fixture
stdout or synthetic errors when marker strings are present. `list_runtimes` returns a static catalogue.

## Validation rules

Code must be non-empty, language must appear in the static runtime list, and timeout must be 1–300.
Warnings cover a small set of strings such as `subprocess`, `os.system`, `eval(`, and network/file APIs.
Absence of a warning does not establish safety. Catalogue `available` fields are static metadata.

## Isolation boundary

No code is parsed for correctness or executed. No interpreter, compiler, subprocess, container,
seccomp filter, cgroup, filesystem overlay, RPC, or OpenSandbox backend is involved. This prototype is
safe only because it does not execute the input; it cannot verify the security of real code.
