# OSS Agent Lab - CLAUDE.md

Turn trending repos into instant capabilities for any AI framework.

Capability factory that auto-discovers trending GitHub repos and wraps them as Python/CLI/MCP/Skills/REST capabilities. Framework-agnostic. Built on Claude Agent SDK (Python).

## Architecture

4-layer system:

1. **Temporal Capability Index** - Auto-discovery from 6+ sources (`scoring/sources/`), composite scoring 0-100
2. **Conductor** (Tier 1) - NL interface + task decomposition (`agents/conductor/`)
3. **Router** (Tier 2) - Capability matching + dispatch (`agents/router/`)
4. **Specialists** (Tier 3) - Plug-and-play repo wrappers (`agents/specialists/`)

Supporting layers: contracts (`agents/contracts/`), memory (`agents/memory/`), scoring (`scoring/`)

## Beads Workflow

Run `/beads` at session start.

`bd update <id> --status in_progress` -> work -> `bd close <id> --reason "evidence"` -> `bd sync`

Never code without a task. Never finish without closing.

## Key Conventions

- Specialists follow `agents/specialists/_template/` pattern: `agent.py`, `tools.py`, `SKILL.md`, `README.md`
- All inter-agent data uses Pydantic schemas from `agents/contracts/schemas.py`
- 80%+ test coverage required per specialist
- Each specialist generates 5 output formats: Python API, CLI, MCP server, Agent Skill, REST API
- Memory layer uses cognee patterns in `agents/memory/`
- Scoring engine in `scoring/` with composite 0-100 Capability Score
- MIT license required for all specialists

## Dev Commands

```bash
pip install -e .              # Install
python -m pytest tests/       # Test
python -m oss_agent_lab       # Run
python scoring/scorer.py --repo <owner/name>  # Score a repo
```

## Standards

- Semantic Versioning (semver.org)
- Keep a Changelog (keepachangelog.com)
- doc-filing v4.3 (NNN-CC-ABCD) in `000-docs/`
- MIT license on all specialists

## Agent HQ

Full ecosystem context: `/home/jeremy/000-projects/000-ecosystem/CLAUDE.md`


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:b9766037 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
