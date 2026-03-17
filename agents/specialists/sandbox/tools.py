"""
Tools for the Sandbox specialist.

Implements safe multi-language code execution patterns inspired by alibaba/OpenSandbox.
Each function is a pure transformation over its inputs — no persistent side effects.
In a production deployment the actual sandbox backend (container runtime, syscall
filter, resource cgroup) would be injected via configuration rather than hard-coded.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

# ---------------------------------------------------------------------------
# Supported runtimes registry
# ---------------------------------------------------------------------------

_RUNTIMES: list[dict[str, Any]] = [
    {"name": "python", "version": "3.12.3", "available": True},
    {"name": "javascript", "version": "node 22.2.0", "available": True},
    {"name": "typescript", "version": "5.4.5 (via ts-node)", "available": True},
    {"name": "bash", "version": "5.2.21", "available": True},
    {"name": "ruby", "version": "3.3.1", "available": True},
    {"name": "go", "version": "1.22.3", "available": True},
    {"name": "rust", "version": "1.78.0", "available": True},
    {"name": "java", "version": "21.0.3", "available": True},
    {"name": "c", "version": "gcc 13.2.0", "available": True},
    {"name": "cpp", "version": "g++ 13.2.0", "available": True},
    {"name": "php", "version": "8.3.6", "available": False},
    {"name": "perl", "version": "5.38.2", "available": False},
]

# Lightweight static analysis patterns keyed by language.
# Each value is a list of (pattern, message) tuples.
_DANGEROUS_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "python": [
        ("__import__", "Dynamic import via __import__() can bypass sandbox restrictions."),
        ("importlib", "importlib usage may allow restricted module loading."),
        ("subprocess", "subprocess module can spawn arbitrary processes."),
        ("os.system", "os.system() executes shell commands; use safer alternatives."),
        ("eval(", "eval() executes arbitrary code strings."),
        ("exec(", "exec() executes arbitrary code strings."),
        ("open(", "File I/O detected; ensure the path is within the sandbox root."),
        ("socket", "Network socket usage detected."),
    ],
    "javascript": [
        ("require('child_process')", "child_process can spawn shell commands."),
        ("require(\"child_process\")", "child_process can spawn shell commands."),
        ("eval(", "eval() executes arbitrary code strings."),
        ("Function(", "Function constructor executes code strings."),
        ("fs.writeFile", "File write detected outside allowed paths."),
        ("process.exit", "process.exit() terminates the sandbox runner."),
    ],
    "bash": [
        ("curl ", "Network egress via curl detected."),
        ("wget ", "Network egress via wget detected."),
        ("rm -rf", "Recursive deletion is disallowed."),
        ("chmod 777", "Overly permissive mode change detected."),
        ("> /etc/", "Write to system configuration path."),
    ],
}


def execute_code(
    code: str,
    language: str = "python",
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute a code snippet safely inside the sandbox.

    In production this dispatches to the OpenSandbox container runtime,
    which enforces seccomp filters, memory limits, and a read-only filesystem
    overlay.  This implementation simulates the execution contract so the
    specialist pipeline can be exercised end-to-end without a live backend.

    Args:
        code: Source code to execute.  Must be non-empty.
        language: Target runtime identifier (e.g. ``"python"``, ``"javascript"``).
            Case-insensitive.  Defaults to ``"python"``.
        timeout: Maximum wall-clock seconds allowed before the sandbox kills
            the process.  Must be in [1, 300].  Defaults to 30.

    Returns:
        A dict with the following keys:

        - ``stdout`` (str): Captured standard output from the execution.
        - ``stderr`` (str): Captured standard error (compiler messages, tracebacks).
        - ``exit_code`` (int): Process exit code; 0 indicates success.
        - ``execution_time_ms`` (float): Wall-clock duration in milliseconds.
        - ``language`` (str): Normalised language identifier that was used.
        - ``execution_id`` (str): Unique identifier for this execution run.

    Raises:
        ValueError: If ``code`` is empty, ``language`` is unrecognised,
            ``timeout`` is out of range, or the requested runtime is unavailable.
    """
    if not code or not code.strip():
        raise ValueError("code must be a non-empty string")

    lang = language.lower().strip()
    timeout = int(timeout)

    if timeout < 1 or timeout > 300:
        raise ValueError(f"timeout must be in [1, 300], got {timeout}")

    runtime = _find_runtime(lang)
    if runtime is None:
        available = [r["name"] for r in _RUNTIMES]
        raise ValueError(f"Unknown language {lang!r}. Available: {available}")
    if not runtime["available"]:
        raise ValueError(
            f"Runtime {lang!r} is registered but not currently available in this environment."
        )

    t_start = time.perf_counter()
    stdout, stderr, exit_code = _simulate_execution(code, lang, timeout)
    execution_time_ms = round((time.perf_counter() - t_start) * 1000.0, 3)

    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "execution_time_ms": execution_time_ms,
        "language": lang,
        "execution_id": str(uuid.uuid4()),
    }


def validate_code(
    code: str,
    language: str = "python",
) -> dict[str, Any]:
    """Validate a code snippet without executing it.

    Performs static analysis to surface syntax issues and policy warnings
    before allowing execution.  This is intentionally conservative — it may
    produce false-positive warnings for advanced but safe code patterns.

    Args:
        code: Source code to validate.  Must be non-empty.
        language: Target runtime identifier.  Case-insensitive.
            Defaults to ``"python"``.

    Returns:
        A dict with the following keys:

        - ``valid`` (bool): ``True`` when no errors were found.
        - ``errors`` (list[str]): Fatal issues that would prevent execution.
        - ``warnings`` (list[str]): Non-fatal policy or style advisories.
        - ``language`` (str): Normalised language identifier.

    Raises:
        ValueError: If ``code`` is empty or ``language`` is unrecognised.
    """
    if not code or not code.strip():
        raise ValueError("code must be a non-empty string")

    lang = language.lower().strip()
    runtime = _find_runtime(lang)
    if runtime is None:
        available = [r["name"] for r in _RUNTIMES]
        raise ValueError(f"Unknown language {lang!r}. Available: {available}")

    errors: list[str] = []
    warnings: list[str] = []

    if not runtime["available"]:
        errors.append(f"Runtime {lang!r} is not available in this environment.")

    # Static pattern scan — language-specific and generic.
    patterns = _DANGEROUS_PATTERNS.get(lang, [])
    for pattern, message in patterns:
        if pattern in code:
            warnings.append(message)

    # Generic checks that apply to all languages.
    lines = code.splitlines()
    if len(lines) > 500:
        warnings.append(f"Code is {len(lines)} lines; consider splitting into smaller units.")
    if len(code) > 50_000:
        errors.append("Code exceeds the 50 000 character limit enforced by the sandbox.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "language": lang,
    }


def list_runtimes() -> dict[str, Any]:
    """List all runtimes registered in the sandbox environment.

    Returns:
        A dict with the following keys:

        - ``runtimes`` (list[dict]): Each entry has ``name`` (str),
          ``version`` (str), and ``available`` (bool).
        - ``total_count`` (int): Total number of registered runtimes.
        - ``available_count`` (int): Number of currently available runtimes.
    """
    runtimes = [dict(r) for r in _RUNTIMES]
    available_count = sum(1 for r in runtimes if r["available"])
    return {
        "runtimes": runtimes,
        "total_count": len(runtimes),
        "available_count": available_count,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _find_runtime(lang: str) -> dict[str, Any] | None:
    """Return the runtime descriptor for ``lang``, or ``None`` if not found."""
    for runtime in _RUNTIMES:
        if runtime["name"] == lang:
            return runtime
    return None


def _simulate_execution(
    code: str,
    language: str,
    timeout: int,
) -> tuple[str, str, int]:
    """Produce synthetic execution output for a given code snippet.

    Simulates the behaviour of the OpenSandbox container backend — in
    production this would be replaced by an actual subprocess call or RPC.
    The simulation is deterministic: the same code produces the same output.

    Args:
        code: The source code string.
        language: Normalised runtime identifier.
        timeout: Configured timeout (used only for length-based heuristics).

    Returns:
        A ``(stdout, stderr, exit_code)`` triple.
    """
    lines = code.strip().splitlines()
    line_count = len(lines)

    # Detect obvious error markers in the code to vary the simulated outcome.
    lowered = code.lower()
    has_syntax_error_marker = "syntax_error_marker" in lowered
    has_runtime_error_marker = "runtime_error_marker" in lowered
    is_long = line_count > timeout * 2  # heuristic: very long snippet may time out

    if has_syntax_error_marker:
        return (
            "",
            f"SyntaxError: invalid syntax at line 1 (simulated for {language})",
            1,
        )

    if has_runtime_error_marker:
        return (
            "",
            f"RuntimeError: name 'undefined_variable' is not defined (simulated for {language})",
            1,
        )

    if is_long:
        return (
            "",
            f"TimeoutError: execution exceeded {timeout}s limit",
            124,  # SIGKILL exit code convention
        )

    # Happy-path: produce a plausible stdout.
    stdout_lines = [
        f"[sandbox:{language}] Execution started",
        f"[sandbox:{language}] {line_count} line(s) processed",
        f"[sandbox:{language}] Execution complete",
    ]
    return ("\n".join(stdout_lines), "", 0)
