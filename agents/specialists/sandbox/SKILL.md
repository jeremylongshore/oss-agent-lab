---
name: sandbox
display_name: Sandbox Specialist
description: Safe multi-language code execution via alibaba/OpenSandbox
version: 0.1.0
source_repo: alibaba/OpenSandbox
license: Apache-2.0
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

Wraps [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox) to provide
isolated, resource-limited execution of arbitrary code snippets inside OSS Agent Lab.
Each execution runs in a container-backed sandbox with seccomp syscall filters, memory
limits, and configurable timeouts — no persistent side effects leak between runs.

Supported runtimes: Python, JavaScript, TypeScript, Bash, Ruby, Go, Rust, Java, C, C++.

## Capabilities

- **execute**: Run a code snippet and capture stdout, stderr, exit code, and timing.
- **code_execution**: Alias capability tag for routing from generic "run code" intents.
- **sandbox**: Enforce isolation policies (seccomp, cgroup, read-only overlay FS).
- **multi_language**: Dispatch to any of the registered runtime backends.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `execute_code` | Execute a code snippet in the sandbox; returns captured output | Subprocess spawn (sandboxed) |
| `validate_code` | Static analysis without execution; returns errors and warnings | None |
| `list_runtimes` | Enumerate all registered runtimes with version and availability | None |

## Usage

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

## Response Shape

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

## Source

Wraps [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox).
