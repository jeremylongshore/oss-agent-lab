"""
Tools for the Template specialist.

Each tool is a callable that the specialist can invoke during execution.
Tools should be pure functions where possible — accept inputs, return outputs.
Side effects (network calls, file I/O) must be declared in SKILL.md allowed-tools.
"""


def example_tool(input_data: str) -> dict:
    """Example tool — replace with actual implementation.

    Args:
        input_data: The input to process.

    Returns:
        Dict with tool results.
    """
    raise NotImplementedError("Implement this tool")
