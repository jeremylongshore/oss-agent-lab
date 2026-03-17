"""CLI entry point for OSS Agent Lab."""
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """OSS Agent Lab - Turn trending repos into instant capabilities."""
    pass


@main.command()
@click.argument("query")
def run(query: str) -> None:
    """Run a natural language query through the agent pipeline."""
    console.print("[bold]OSS Agent Lab[/bold] v0.1.0")
    console.print(f"Query: {query}")
    console.print("[yellow]Conductor → Router → Specialist pipeline not yet implemented.[/yellow]")
    console.print("See: agents/conductor/agent.py (Epic 2)")


@main.command()
@click.argument("repo")
def score(repo: str) -> None:
    """Score a GitHub repo using the Capability Scoring Engine."""
    console.print(f"[bold]Scoring:[/bold] {repo}")
    console.print("[yellow]Scoring engine not yet implemented.[/yellow]")
    console.print("See: scoring/scorer.py (Epic 5)")


@main.command()
def specialists() -> None:
    """List registered specialists."""
    console.print("[bold]Registered Specialists:[/bold]")
    console.print("[yellow]Registry not yet implemented.[/yellow]")
    console.print("See: agents/router/registry.py (Epic 2)")


if __name__ == "__main__":
    main()
