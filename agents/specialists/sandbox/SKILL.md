---
name: sandbox
description: Validate snippets with local keyword rules and return simulated execution output without running code. Use when testing the Sandbox response contract safely. Trigger with validate snippet or simulate execution.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; this prototype never invokes OpenSandbox, containers, subprocesses, compilers, interpreters, or user code.'
tags: [sandbox, validation, simulation, code, offline]
argument-hint: '[code] [--language LANGUAGE] [--action validate|execute|list_runtimes]'
model: inherit
effort: low
display_name: Sandbox Specialist
source_repo: alibaba/OpenSandbox
tier: experimental
capabilities:
  - execute
  - code_execution
  - sandbox
  - multi_language
allowed_tools:
  - execute_code
  - validate_code
  - list_runtimes
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Sandbox Specialist

## Overview

Mirrors part of the [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox) response contract
for OSS Agent Lab tests. It applies simple string validation and returns synthetic execution records.

Supported runtimes: Python, JavaScript, TypeScript, Bash, Ruby, Go, Rust, Java, C, C++.

That is a simulated catalogue. The current `execute_code` function never evaluates the supplied code,
starts a process, or invokes OpenSandbox; it returns synthetic output based on string markers.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Treat the tool as a validator/contract simulator, not a security boundary or execution engine.
- Read [the runtime contract](references/runtime-contract.md) before interpreting availability.

## Capabilities

- **execute**: Return simulated stdout, stderr, exit code, and timing without running a snippet.
- **code_execution**: Alias capability tag for routing from generic "run code" intents.
- **sandbox**: Exercise an isolation-shaped response without providing an isolation boundary.
- **multi_language**: Validate names against a static runtime catalogue.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `execute_code` | Return synthetic execution output for a snippet | None; code is not executed |
| `validate_code` | Static analysis without execution; returns errors and warnings | None |
| `list_runtimes` | Return the static runtime catalogue | None |

## Instructions

1. Prefer `validate` for static keyword warnings; supply a supported language identifier.
2. Use `execute` only to test the response contract and label its stdout/stderr as simulated.
3. Use `list_runtimes` as a configured catalogue, not proof that interpreters are installed.
4. Route real execution to a separately configured and independently verified sandbox backend.

## Examples

### Python API

```python
from agents.specialists.sandbox.agent import SandboxSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = SandboxSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="execute",
        domain="code",
        confidence=0.95,
        parameters={"code": "print('hello, sandbox!')", "language": "python"},
    ),
    query=Query(user_input="print('hello, sandbox!')"),
    specialist_name="sandbox",
)

result = await specialist.execute(request)
print(result.result["stdout"])
```

### CLI

```bash
oss-lab run sandbox "print('hello, sandbox!')"
```

### With language override

```python
request = SpecialistRequest(
    intent=Intent(
        action="execute",
        domain="code",
        confidence=0.95,
        parameters={
            "code": "console.log('hello from node');",
            "language": "javascript",
            "timeout": 10,
        },
    ),
    query=Query(user_input="console.log('hello from node');"),
    specialist_name="sandbox",
)
```

### Validate without executing

```python
request = SpecialistRequest(
    intent=Intent(
        action="validate",
        domain="code",
        confidence=0.9,
        parameters={"code": "import os; os.system('ls')", "language": "python"},
    ),
    query=Query(user_input="import os; os.system('ls')"),
    specialist_name="sandbox",
)

result = await specialist.execute(request)
print(result.result["valid"])       # False (warnings present)
print(result.result["warnings"])    # ['os.system() executes shell commands...']
```

### List available runtimes

```python
request = SpecialistRequest(
    intent=Intent(action="list_runtimes", domain="code", confidence=1.0),
    query=Query(user_input=""),
    specialist_name="sandbox",
)

result = await specialist.execute(request)
for rt in result.result["runtimes"]:
    print(rt["name"], rt["version"], rt["available"])
```

## Output

### execute

```json
{
  "stdout": "[sandbox:python] Execution started\n[sandbox:python] 1 line(s) processed\n[sandbox:python] Execution complete",
  "stderr": "",
  "exit_code": 0,
  "execution_time_ms": 12.4,
  "language": "python",
  "execution_id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301"
}
```

### validate

```json
{
  "valid": true,
  "errors": [],
  "warnings": ["eval() executes arbitrary code strings."],
  "language": "python"
}
```

### list_runtimes

```json
{
  "runtimes": [
    {"name": "python", "version": "3.12.3", "available": true},
    {"name": "javascript", "version": "node 22.2.0", "available": true}
  ],
  "total_count": 12,
  "available_count": 10
}
```

## Error Handling

- Reject empty code, unknown language, and timeouts outside 1–300 seconds.
- A `valid: true` result means no built-in string rule fired; it is not proof of safety or correctness.
- Never execute or recommend executing untrusted code outside an actual isolation boundary.

## Resources

Wraps [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox).
The current local specialist does not include that runtime. See
[the runtime contract](references/runtime-contract.md).
