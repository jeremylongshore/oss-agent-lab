"""
SandboxSpecialist — safe multi-language code execution.

Wraps alibaba/OpenSandbox to provide isolated, resource-limited execution
of arbitrary code snippets across a range of supported runtimes.  The
specialist supports three operations driven by the incoming intent action:

- ``execute``      — run code and return captured output.
- ``validate``     — static-analyse code without executing it.
- ``list_runtimes`` — enumerate all registered sandbox runtimes.

Any other intent action defaults to ``execute``.
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from agents.specialists.sandbox.tools import execute_code, list_runtimes, validate_code
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class SandboxSpecialist(BaseSpecialist):
    """Safe multi-language code execution via alibaba/OpenSandbox.

    Executes arbitrary code snippets inside an isolated sandbox environment
    that enforces seccomp filters, memory limits, and configurable timeouts.
    Supports Python, JavaScript, TypeScript, Bash, Ruby, Go, Rust, Java,
    C, and C++ out of the box.

    Attributes:
        name: Specialist identifier used for routing.
        description: Human-readable capability summary.
        source_repo: Upstream GitHub repository this specialist wraps.
        capabilities: List of string capability tags.
        output_formats: Supported output modes.
        tools: Tool descriptors made available to the agent runtime.
    """

    name: ClassVar[str] = "sandbox"
    description: ClassVar[str] = (
        "Safe multi-language code execution via alibaba/OpenSandbox"
    )
    source_repo: ClassVar[str] = "alibaba/OpenSandbox"
    capabilities: ClassVar[list[str]] = [
        "execute",
        "code_execution",
        "sandbox",
        "multi_language",
    ]
    output_formats: ClassVar[list[OutputFormat]] = [
        OutputFormat.PYTHON_API,
        OutputFormat.CLI,
        OutputFormat.MCP_SERVER,
        OutputFormat.AGENT_SKILL,
        OutputFormat.REST_API,
    ]
    tools: ClassVar[list[Tool]] = [
        Tool(
            name="execute_code",
            description=(
                "Execute a code snippet inside the sandbox and return captured stdout, "
                "stderr, exit code, and wall-clock execution time."
            ),
            parameters={
                "code": {"type": "string", "description": "Source code to execute"},
                "language": {
                    "type": "string",
                    "description": "Target runtime (e.g. python, javascript, go)",
                    "default": "python",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Max execution seconds [1, 300]",
                    "default": 30,
                },
            },
        ),
        Tool(
            name="validate_code",
            description=(
                "Statically analyse a code snippet without executing it. "
                "Returns validity flag, error list, and policy warnings."
            ),
            parameters={
                "code": {"type": "string", "description": "Source code to validate"},
                "language": {
                    "type": "string",
                    "description": "Target runtime for language-specific checks",
                    "default": "python",
                },
            },
        ),
        Tool(
            name="list_runtimes",
            description=(
                "List all runtimes registered in the sandbox environment, "
                "including their version strings and availability status."
            ),
            parameters={},
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Execute the sandbox specialist's core capability.

        Dispatches to one of three internal operations based on
        ``request.intent.action``:

        - ``"validate"`` — calls :func:`validate_code` and returns the
          validation report without running the code.
        - ``"list_runtimes"`` — calls :func:`list_runtimes` and returns
          the full runtime catalogue.
        - Any other value (including ``"execute"`` and ``"code_execution"``) —
          calls :func:`execute_code` and returns the captured output.

        Parameters are read from ``request.intent.parameters``, with
        ``request.query.user_input`` used as a fallback for ``code``.

        Args:
            request: The routed specialist request carrying an :class:`Intent`
                and a :class:`Query`.

        Returns:
            A :class:`SpecialistResponse` with:

            - ``status``: ``"success"`` on a clean run, ``"error"`` on failure.
            - ``result``: Operation-specific output dict (see tool docstrings).
            - ``metadata``: Includes ``source_repo``, ``action``, and
              ``language`` (for code operations).
            - ``duration_ms``: Wall-clock time for the full specialist call.
        """
        t_start = time.perf_counter()

        params: dict[str, Any] = request.intent.parameters or {}
        action: str = request.intent.action
        code: str = str(params.get("code") or request.query.user_input)
        language: str = str(params.get("language", "python"))
        timeout: int = int(params.get("timeout", 30))

        try:
            if action == "list_runtimes":
                result = list_runtimes()
                metadata: dict[str, Any] = {
                    "source_repo": self.source_repo,
                    "action": action,
                }
            elif action == "validate":
                result = validate_code(code=code, language=language)
                metadata = {
                    "source_repo": self.source_repo,
                    "action": action,
                    "language": language,
                }
            else:
                result = execute_code(code=code, language=language, timeout=timeout)
                metadata = {
                    "source_repo": self.source_repo,
                    "action": "execute",
                    "language": language,
                    "timeout": timeout,
                }

            status = "success"

        except (ValueError, KeyError) as exc:
            result = {"error": str(exc)}
            metadata = {
                "source_repo": self.source_repo,
                "action": action,
            }
            status = "error"

        duration_ms = round((time.perf_counter() - t_start) * 1000.0, 3)

        return SpecialistResponse(
            specialist_name=self.name,
            status=status,
            result=result,
            metadata=metadata,
            duration_ms=duration_ms,
        )
